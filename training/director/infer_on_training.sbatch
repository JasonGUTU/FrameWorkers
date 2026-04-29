#!/bin/bash
#SBATCH --job-name=infer_train_e4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=6:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:1
#SBATCH --output=/home/zhendong_li/FrameWorkers/training/director/logs/infer_train_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/training/director/logs/infer_train_%j.error
#SBATCH --qos=neurips-2026
#SBATCH --partition=non-reserved
#SBATCH --constraint=zone-sof1

# Run LoRA(checkpoint-712) inference on SFT training data → mine failed cases
# for GRPO hard-example training.
#
# Output:
#   - infer_on_training_all.jsonl   (all 1417 records + chain_correct verdict)
#   - infer_on_training_failed.jsonl (failed records only, ~30% of 1417 ≈ 420)
#
# Estimated runtime: 1417 samples × ~1.3 s/sample = ~30 min on H200.

set -euo pipefail

REPO_ROOT="/home/zhendong_li/FrameWorkers"
cd "$REPO_ROOT"

ENV_DIR="/home/zhendong_li/.conda-envs/director-train"
set +u
source ~/.bashrc
conda activate "$ENV_DIR" 2>/dev/null || conda activate frameworkers
set -u

if [ -z "${CONDA_PREFIX:-}" ] || [ ! -x "$CONDA_PREFIX/bin/python" ]; then
    echo "FATAL: conda activate failed." >&2
    exit 1
fi
echo "python: $(which python) — $(python --version)"
nvidia-smi | head -20

ADAPTER="${ADAPTER:-training/director/adapters_grpo_base/qwen3_v3tmpl_e4_step712}"
SFT_JSONL="${SFT_JSONL:-training/director/samples_sft_full.templated.jsonl}"
OUT_ALL="${OUT_ALL:-training/director/infer_on_training_all.jsonl}"
OUT_FAIL="${OUT_FAIL:-training/director/infer_on_training_failed.jsonl}"

echo "adapter:  $ADAPTER"
echo "sft:      $SFT_JSONL"
echo "out-all:  $OUT_ALL"
echo "out-fail: $OUT_FAIL"

PYTHONPATH=. python training/director/infer_on_training.py \
    --adapter "$ADAPTER" \
    --sft-jsonl "$SFT_JSONL" \
    --out-all "$OUT_ALL" \
    --out-fail "$OUT_FAIL" \
    --max-new-tokens 512

echo "=== DONE ==="
