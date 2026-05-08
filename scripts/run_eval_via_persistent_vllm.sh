#!/bin/bash
# Run assistant_pipeline eval against a *persistent* vLLM serve instance
# launched by scripts/serve_qwen_vllm.sbatch. Run this from the login node
# (or any host that can reach the serve job's compute node on port 8000).
#
# Usage:
#   bash scripts/run_eval_via_persistent_vllm.sh [WORKERS] [CASES_FILE]
# Defaults:
#   WORKERS=4
#   CASES_FILE=assistant_test/assistant_test_chain_shape_sampled.json
#
# Prerequisites:
#   1. scripts/serve_qwen_vllm.sbatch is running and has published
#      Runtime/vllm_endpoints/qwen2.5-vl-7b.json.
#   2. login node can reach the compute node on port 8000 (we curl-probe
#      first; if blocked, set up `ssh -L 8000:<node>:8000` and override
#      LOCAL_VL_BASE_URL=http://localhost:8000/v1 manually).

set -euo pipefail

REPO_ROOT="/home/zhendong_li/FrameWorkers"
cd "$REPO_ROOT"

WORKERS="${1:-4}"
CASES_FILE="${2:-assistant_test/assistant_test_chain_shape_sampled.json}"

# --- Env ---
set +u
source ~/.bashrc
conda activate frameworkers
set -u

# --- Read endpoint published by serve sbatch ---
SERVED_NAME="qwen2.5-vl-7b"
ENDPOINT_FILE="${REPO_ROOT}/Runtime/vllm_endpoints/${SERVED_NAME}.json"
if [ ! -f "$ENDPOINT_FILE" ]; then
    echo "FATAL: no endpoint file at $ENDPOINT_FILE — start scripts/serve_qwen_vllm.sbatch first and wait for it to publish." >&2
    exit 1
fi
BASE_URL=$(python3 -c "import json; print(json.load(open('$ENDPOINT_FILE'))['base_url'])")
echo "endpoint: $BASE_URL"

# Reachability probe — 99% of cluster issues happen here.
if ! curl -sf "${BASE_URL}/models" >/dev/null; then
    echo "FATAL: cannot reach ${BASE_URL}/models from $(hostname)." >&2
    echo "       check: scancel/squeue on the serve job; firewall login->compute :8000;" >&2
    echo "       fallback: ssh -L 8000:<compute_host>:8000 + override LOCAL_VL_BASE_URL." >&2
    exit 1
fi

# --- LLMClient routing → local_vl provider via FW env vars
#     (inference_runtime.yaml line 28/44 already maps qwen2.5-vl-7b →
#     local_vl → openai_sdk; LOCAL_VL_{BASE_URL,API_KEY} are picked up by
#     default_client.py's f"{provider.upper()}_*" fallback). ---
export INFERENCE_DEFAULT_MODEL="$SERVED_NAME"
export LOCAL_VL_BASE_URL="$BASE_URL"
export LOCAL_VL_API_KEY=dummy
export FW_MAX_TOKENS=32768
unset FW_USE_REAL_MEDIA_GEN || true

RUN_NAME="${SERVED_NAME//[\/.]/_}_persistent_$(date +%Y%m%d_%H%M%S)"
echo "=== launching eval_pipeline ==="
echo "  cases:    $CASES_FILE"
echo "  workers:  $WORKERS"
echo "  model:    $SERVED_NAME @ $BASE_URL"
echo "  max_tok:  $FW_MAX_TOKENS"
echo "  run name: $RUN_NAME"

python evals/assistant_pipeline/eval_pipeline.py \
    --cases "$CASES_FILE" \
    --workers "$WORKERS" \
    --name "$RUN_NAME" \
    --timeout 1800
