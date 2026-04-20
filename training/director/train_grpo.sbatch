#!/bin/bash
#SBATCH --job-name=director_grpo
#SBATCH --nodelist=sof1-h200-[0,1,2,3,4,6,7]
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:1
#SBATCH --output=/home/zhendong_li/FrameWorkers/training/director/logs/grpo_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/training/director/logs/grpo_%j.error
#SBATCH --qos=eccv-2026
#SBATCH --partition=non-reserved

set -euo pipefail

REPO_ROOT="/home/zhendong_li/FrameWorkers"
cd "$REPO_ROOT"

# ---------------------------------------------------------------------------
# Env: self-contained cephfs env (same pattern as train_full.sbatch)
# ---------------------------------------------------------------------------
ENV_DIR="/home/zhendong_li/.conda-envs/director-train"
if [ ! -x "$ENV_DIR/bin/python" ]; then
    echo "FATAL: $ENV_DIR/bin/python missing." >&2
    echo "       Run 'bash training/director/ensure_env.sh' on the LOGIN node before sbatch." >&2
    exit 1
fi
export PATH="$ENV_DIR/bin:$PATH"
export CONDA_PREFIX="$ENV_DIR"
echo "python: $(which python) — $(python --version)"
nvidia-smi | head -20

# Training deps (TRL GRPOTrainer requires trl>=0.14; verify)
python -c "import torch, transformers, trl, peft, datasets, accelerate; \
           assert trl.__version__ >= '1.0.0', f'trl too old: {trl.__version__}'" 2>/dev/null \
    || pip install -r training/director/requirements-training.txt

# ---------------------------------------------------------------------------
# Prerequisite: SFT+DPO adapter must exist
# ---------------------------------------------------------------------------
DPO_ADAPTER="training/director/adapters_full/dpo"
if [ ! -d "$DPO_ADAPTER" ]; then
    echo "FATAL: $DPO_ADAPTER missing — run train_full.sbatch first" >&2
    exit 2
fi

# ---------------------------------------------------------------------------
# GRPO on SFT goals (1110 prompts × 4 rollouts = 4440 generations / epoch).
# Starts from the DPO adapter as the initial policy.
# ---------------------------------------------------------------------------
echo "=== GRPO from DPO adapter → adapters_full/grpo/ ==="
PYTHONPATH=. python training/director/train_grpo.py \
    --adapter-in  "$DPO_ADAPTER" \
    --adapter-out training/director/adapters_full/grpo \
    --sft-path    training/director/samples_sft_full.jsonl \
    --num-generations 4 \
    --epochs 1 \
    --per-device-batch 1 \
    --grad-accum 8

# ---------------------------------------------------------------------------
# Post-train smoke
# ---------------------------------------------------------------------------
echo "=== infer smoke (adapter=adapters_full/grpo) ==="
PYTHONPATH=. python training/director/infer.py \
    --adapter training/director/adapters_full/grpo || true

echo "=== DONE ==="
