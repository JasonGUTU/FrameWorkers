#!/bin/bash
#SBATCH --job-name=director_sft_overfit_templated
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=50:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:1
#SBATCH --output=/home/zhendong_li/FrameWorkers/training/director/logs/train_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/training/director/logs/train_%j.error
#SBATCH --qos=neurips-2026
#SBATCH --partition=non-reserved
#SBATCH --constraint=zone-sof1

# Overfit experiment — SFT 50 epochs on TEMPLATED data
# (samples_sft_full.templated.jsonl: chain-free rationale + 3-variant intent
# per agent, 126 rationale skeletons, 1406 unique signatures).
# Output adapter: training/director/adapters_overfit_templated/sft/
# Comparison vs adapters_overfit/sft (same 50-epoch overfit on original
# hand-tailored data) tells us how rationale/intent format style affects
# overfitting dynamics — train_loss → 0 in both, but generalization on
# held-out eval may differ.

set -euo pipefail

REPO_ROOT="/home/zhendong_li/FrameWorkers"
cd "$REPO_ROOT"

ENV_DIR="/home/zhendong_li/.conda-envs/director-train"
set +u
source ~/.bashrc
conda activate "$ENV_DIR"
set -u

if [ -z "${CONDA_PREFIX:-}" ] || [ ! -x "$CONDA_PREFIX/bin/python" ]; then
    echo "FATAL: conda activate failed." >&2
    exit 1
fi
echo "python: $(which python) — $(python --version)"
echo "CONDA_PREFIX=$CONDA_PREFIX"
nvidia-smi | head -20

python -c "import torch, transformers, trl, peft, datasets, accelerate" 2>/dev/null \
    || pip install -r training/director/requirements-training.txt

echo "=== validate samples_sft_full.templated ==="
PYTHONPATH=. python training/director/validate.py \
    --sft samples_sft_full.templated.jsonl \
    --seq-len 8192

echo "=== SFT 50 epochs — OVERFIT (templated data) ==="
PYTHONPATH=. python training/director/train_sft.py \
    --sft-path training/director/samples_sft_full.templated.jsonl \
    --adapter-dir training/director/adapters_overfit_templated \
    --sft-epochs 50 \
    --per-device-batch 1 \
    --grad-accum 8

echo "=== infer smoke (adapter=adapters_overfit_templated/sft) ==="
PYTHONPATH=. python training/director/infer.py \
    --adapter training/director/adapters_overfit_templated/sft || true

echo "=== DONE ==="
