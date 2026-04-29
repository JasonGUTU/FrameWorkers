#!/bin/bash
#SBATCH --job-name=grpo
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=50:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:4
#SBATCH --output=/home/zhendong_li/FrameWorkers/training/director/logs/grpo_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/training/director/logs/grpo_%j.error
#SBATCH --qos=neurips-2026
#SBATCH --partition=non-reserved
#SBATCH --constraint=zone-sof1

set -euo pipefail

REPO_ROOT="/home/zhendong_li/FrameWorkers"
cd "$REPO_ROOT"

ENV_DIR="/home/zhendong_li/.conda-envs/director-train"
set +u
source ~/.bashrc
conda activate "$ENV_DIR" 2>/dev/null || conda activate frameworkers
set -u

if [ -z "${CONDA_PREFIX:-}" ] || [ ! -x "$CONDA_PREFIX/bin/python" ]; then
    echo "FATAL: conda activate failed on this GPU node." >&2
    exit 1
fi
echo "python: $(which python) — $(python --version)"
echo "CONDA_PREFIX=$CONDA_PREFIX"
nvidia-smi -L

# Parametric — override via sbatch --export=ALL,VAR=...
SFT_ADAPTER="${SFT_ADAPTER:-training/director/adapters_full/sft}"
GRPO_OUT="${GRPO_OUT:-training/director/adapters_full/grpo}"
GRPO_DATA="${GRPO_DATA:-training/director/samples_sft_full.jsonl}"
EPOCHS="${EPOCHS:-3}"
SUBSAMPLE="${SUBSAMPLE:-}"        # e.g. SUBSAMPLE=20 for smoke test
MAX_STEPS="${MAX_STEPS:-}"        # e.g. MAX_STEPS=10 for smoke test

if [ ! -d "$SFT_ADAPTER" ]; then
    echo "FATAL: $SFT_ADAPTER missing — train SFT first" >&2
    exit 2
fi

# Smoke-test mode: tiny budget to verify pipeline runs end-to-end without crashes.
# Submit:  sbatch --export=ALL,SUBSAMPLE=20,MAX_STEPS=10 train_grpo.sbatch
# Default: full 3-epoch run on all 1406 prompts.
EXTRA_ARGS=""
[ -n "$SUBSAMPLE" ] && EXTRA_ARGS="$EXTRA_ARGS --subsample $SUBSAMPLE"
[ -n "$MAX_STEPS" ] && EXTRA_ARGS="$EXTRA_ARGS --max-steps $MAX_STEPS"

export PYTHONUNBUFFERED=1

echo "=== GRPO from $SFT_ADAPTER → $GRPO_OUT (epochs=$EPOCHS) ==="
echo "EXTRA_ARGS: $EXTRA_ARGS"

PYTHONPATH=. torchrun --nproc_per_node=${NPROC:-4} --master_port=29501 \
    training/director/train_grpo.py \
    --adapter-in  "$SFT_ADAPTER" \
    --adapter-out "$GRPO_OUT" \
    --sft-path    "$GRPO_DATA" \
    --num-generations 4 \
    --epochs "$EPOCHS" \
    --max-new-tokens 1024 \
    --learning-rate 1e-6 \
    --beta 0.04 \
    --logging-steps 5 \
    --save-steps 200 \
    $EXTRA_ARGS

echo "=== infer smoke (adapter=$GRPO_OUT) ==="
# infer.py treats --adapter as relative to training/director/, so strip the
# leading "training/director/" if present (no-op for absolute paths).
PYTHONPATH=. python training/director/infer.py --adapter "${GRPO_OUT#training/director/}" || true

echo "=== DONE ==="
