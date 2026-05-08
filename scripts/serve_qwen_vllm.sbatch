#!/bin/bash
#SBATCH --job-name=qwen_vllm_serve
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=3-00:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:1
#SBATCH --output=/home/zhendong_li/FrameWorkers/scripts/logs/qwen_vllm_serve_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/scripts/logs/qwen_vllm_serve_%j.error
#SBATCH --qos=neurips-2026
#SBATCH --partition=non-reserved
#SBATCH --constraint=zone-sof1

# Persistent vLLM serve for Qwen2.5-VL-7B-Instruct. Runs on one H200 for the
# duration of the SLURM allocation (default 3 days). Other jobs / login-node
# Python clients hit it via the OpenAI-compat /v1 endpoint.
#
# Endpoint discovery: writes Runtime/vllm_endpoints/qwen2.5-vl-7b.json with
# {host, port, base_url, served_name, slurm_job_id, started_at}. Callers
# read that file to learn where to point AsyncOpenAI.
#
# Stop early: scancel <jobid>. Auto-resubmit on expiry: not built in —
# resubmit manually when --time runs out.

set -euo pipefail

REPO_ROOT="/home/zhendong_li/FrameWorkers"
cd "$REPO_ROOT"

# --- Env (same convention as run_assistant_eval_qwen_local.sbatch:
#     /home-based director-train env is visible on compute nodes;
#     /scratch-based frameworkers env is not). ---
ENV_DIR="/home/zhendong_li/.conda-envs/director-train"
set +u
source ~/.bashrc
conda activate "$ENV_DIR"
set -u

if [ -z "${CONDA_PREFIX:-}" ] || [ ! -x "$CONDA_PREFIX/bin/python" ]; then
    echo "FATAL: conda activate $ENV_DIR failed." >&2
    exit 1
fi

echo "compute node: $(hostname)"
echo "python: $(which python) — $(python --version)"
echo "CONDA_PREFIX=$CONDA_PREFIX"
nvidia-smi -L || true

# director-train env has torch/transformers/peft from training; top up vllm.
# Pin to 0.20.1: it correctly parses Qwen2.5-VL-7B's mixed mrope+rope_type
# config (0.10 rejects); but its kernel_warmup unconditionally calls a
# DeepGEMM FP8 path that raises when deep_gemm package is missing, even
# on bf16 models that never use FP8. So we *patch* the broken function
# in-place (next step) — the patch is NFS-persistent.
DESIRED_VLLM="0.20.1"
INSTALLED_VLLM=$(python -c "import vllm; print(vllm.__version__)" 2>/dev/null || echo "none")
if [ "$INSTALLED_VLLM" != "$DESIRED_VLLM" ]; then
    pip install "vllm==${DESIRED_VLLM}"
fi
python -c "import vllm; print('vllm', vllm.__version__)"

# In-place patch: make _fp8_linear_may_use_deep_gemm() return False unconditionally
# so kernel_warmup's FP8 iteration count is 0 and deep_gemm_warmup is a no-op.
# Idempotent (skips if marker already present); hard-fails if target def moved.
python <<'PYEOF'
import vllm.model_executor.warmup.deep_gemm_warmup as dgw
path = dgw.__file__
content = open(path).read()
marker = "# PATCHED: skip FP8 warmup (deep_gemm not installed)"
if marker in content:
    print(f"[patch] already applied: {path}")
else:
    target = "def _fp8_linear_may_use_deep_gemm(m):\n"
    if target not in content:
        raise SystemExit(f"[patch] target def not found in {path} — vllm internals changed")
    new = target + f"    return False  {marker}\n"
    open(path, "w").write(content.replace(target, new, 1))
    print(f"[patch] applied: {path}")
PYEOF

export PYTHONUNBUFFERED=1
export PYTHONPATH=.
# SLURM --gpus=h200:1 sets CUDA_VISIBLE_DEVICES to the GPU's UUID (e.g.
# "GPU-a385a88d-..."). vLLM 0.20.x's device_id_to_physical_device_id does
# `int(...)` on this and crashes. Override to integer index — cgroup
# isolation guarantees the allocated GPU is index 0 inside the job's view.
export CUDA_VISIBLE_DEVICES=0

# --- Run config ---
VLLM_PORT=8000
HF_MODEL="Qwen/Qwen2.5-VL-7B-Instruct"
SERVED_NAME="qwen2.5-vl-7b"
ENDPOINT_DIR="${REPO_ROOT}/Runtime/vllm_endpoints"
ENDPOINT_FILE="${ENDPOINT_DIR}/${SERVED_NAME}.json"
RUN_LOG_DIR="${REPO_ROOT}/scripts/logs/qwen_vllm_serve_${SLURM_JOB_ID}"
mkdir -p "$ENDPOINT_DIR" "$RUN_LOG_DIR"

# --- Start vLLM serve (background) ---
# --host 0.0.0.0: bind all interfaces so the login node can reach
#   $(hostname):8000 (default newer-vLLM bind is already 0.0.0.0; explicit
#   for safety + visibility).
# --max-model-len 32768: native ctx for Qwen2.5-VL-7B. Clients MUST cap
#   FW_MAX_TOKENS<=32768 (run_eval_via_persistent_vllm.sh sets it).
echo "=== launching vllm serve ${HF_MODEL} on $(hostname):${VLLM_PORT} ==="
vllm serve "$HF_MODEL" \
    --host 0.0.0.0 \
    --port "$VLLM_PORT" \
    --served-model-name "$SERVED_NAME" \
    --max-model-len 32768 \
    --gpu-memory-utilization 0.85 \
    --limit-mm-per-prompt '{"image": 4, "video": 1}' \
    --enforce-eager \
    > "${RUN_LOG_DIR}/vllm.log" 2>&1 &
VLLM_PID=$!
echo "vllm PID: $VLLM_PID, log: ${RUN_LOG_DIR}/vllm.log"

cleanup() {
    rc=$?
    echo "=== teardown (exit $rc) ==="
    kill "$VLLM_PID" 2>/dev/null || true
    wait 2>/dev/null || true
    rm -f "$ENDPOINT_FILE"
    exit $rc
}
trap cleanup EXIT

# --- Wait for /v1/models to be ready (cold start ~17 GB HF download on
#     first run; allow 20 min). ---
echo "waiting for vllm at :${VLLM_PORT} ..."
READY=0
for i in $(seq 1 240); do
    if curl -sf "http://localhost:${VLLM_PORT}/v1/models" >/dev/null 2>&1; then
        READY=1
        echo "vllm ready after ${i}*5s = $((i*5))s"
        break
    fi
    sleep 5
done
if [ "$READY" -ne 1 ]; then
    echo "FATAL: vllm did not become ready within 1200s." >&2
    tail -50 "${RUN_LOG_DIR}/vllm.log" >&2 || true
    exit 1
fi
curl -s "http://localhost:${VLLM_PORT}/v1/models" | head -c 500 ; echo

# --- Publish endpoint for callers (login node reads this file) ---
NODE_HOST=$(hostname -f 2>/dev/null || hostname)
cat > "$ENDPOINT_FILE" <<EOF
{
  "served_name": "${SERVED_NAME}",
  "host": "${NODE_HOST}",
  "port": ${VLLM_PORT},
  "base_url": "http://${NODE_HOST}:${VLLM_PORT}/v1",
  "max_model_len": 32768,
  "slurm_job_id": "${SLURM_JOB_ID}",
  "started_at": "$(date -Iseconds)"
}
EOF
echo "=== endpoint published to ${ENDPOINT_FILE} ==="
cat "$ENDPOINT_FILE"

# --- Hold until SLURM kills the job. wait $VLLM_PID exits if vLLM dies on
#     its own; trap 'cleanup' tears down + removes endpoint file. ---
echo "=== serving on http://${NODE_HOST}:${VLLM_PORT}/v1 — waiting until SLURM expires ==="
wait $VLLM_PID
