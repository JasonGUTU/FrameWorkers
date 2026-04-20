#!/bin/bash
#SBATCH --job-name=director_lora_full
#SBATCH --nodelist=sof1-h200-[0,1,2,3,4,6,7]
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=8:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:1
#SBATCH --output=/home/zhendong_li/FrameWorkers/training/director/logs/train_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/training/director/logs/train_%j.error
#SBATCH --qos=eccv-2026
#SBATCH --partition=non-reserved

set -euo pipefail

REPO_ROOT="/home/zhendong_li/FrameWorkers"
cd "$REPO_ROOT"

# ---------------------------------------------------------------------------
# Env: activate self-contained director-train (copy-clone of frameworkers env
# at a cephfs path visible to GPU nodes). See run_smoke.sh for full rationale.
# ---------------------------------------------------------------------------
ENV_DIR="/home/zhendong_li/.conda-envs/director-train"
if [ ! -x "$ENV_DIR/bin/python" ]; then
    echo "FATAL: $ENV_DIR/bin/python missing on GPU node." >&2
    echo "       /scratch is node-local so we cannot clone the source env from here." >&2
    echo "       Run 'bash training/director/ensure_env.sh' on the LOGIN node before sbatch." >&2
    echo "       Or use the wrapper: 'bash training/director/submit_training.sh'." >&2
    exit 1
fi
export PATH="$ENV_DIR/bin:$PATH"
export CONDA_PREFIX="$ENV_DIR"
echo "python: $(which python) — $(python --version)"
nvidia-smi | head -20

# ---------------------------------------------------------------------------
# Ensure training deps — pip into the cephfs env if something's missing
# (cephfs is writable from GPU node so this works even when scratch isn't).
# ---------------------------------------------------------------------------
python -c "import torch, transformers, trl, peft, datasets, accelerate" 2>/dev/null \
    || pip install -r training/director/requirements-training.txt

# ---------------------------------------------------------------------------
# Validate full-size samples before touching GPU
# ---------------------------------------------------------------------------
echo "=== validate samples_sft_full / samples_dpo_full ==="
PYTHONPATH=. python training/director/validate.py \
    --sft samples_sft_full.jsonl \
    --dpo samples_dpo_full.jsonl \
    --seq-len 4096

# ---------------------------------------------------------------------------
# Train: SFT (3 epochs) → DPO (1 epoch) on full datasets.
#   1110 SFT × 3 epochs / (batch 1 × grad-accum 8) ≈ 416 steps
#   500  DPO × 1 epoch  / (batch 1 × grad-accum 8) ≈  62 steps
# Output adapters: training/director/adapters_full/{sft,dpo}/
# ---------------------------------------------------------------------------
echo "=== train SFT → DPO on full datasets ==="
PYTHONPATH=. python training/director/train_lora.py \
    --stage both \
    --sft-path training/director/samples_sft_full.jsonl \
    --dpo-path training/director/samples_dpo_full.jsonl \
    --adapter-dir training/director/adapters_full \
    --sft-epochs 3 \
    --dpo-epochs 1 \
    --per-device-batch 1 \
    --grad-accum 8

# ---------------------------------------------------------------------------
# Inference smoke on the trained DPO adapter
# ---------------------------------------------------------------------------
echo "=== infer smoke (adapter=adapters_full/dpo) ==="
PYTHONPATH=. python training/director/infer.py \
    --adapter training/director/adapters_full/dpo || true

echo "=== DONE ==="
