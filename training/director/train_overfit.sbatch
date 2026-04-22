#!/bin/bash
#SBATCH --job-name=director_lora_overfit
#SBATCH --nodelist=sof1-h200-[0,1,2,3,4,6,7]
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=10:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:1
#SBATCH --output=/home/zhendong_li/FrameWorkers/training/director/logs/train_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/training/director/logs/train_%j.error
#SBATCH --qos=eccv-2026
#SBATCH --partition=non-reserved

# Overfit experiment — SFT 50 epochs + DPO 1 epoch on same canonical data.
# Output adapters: training/director/adapters_overfit/{sft,dpo}/
# Expected: train_loss → 0, generalization likely regresses on held-out eval.
# That regression IS the signal (measures how much SFT capacity the 3-epoch
# default leaves on the table vs. how much drives overfit).

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

echo "=== validate samples_sft_full / samples_dpo_full ==="
PYTHONPATH=. python training/director/validate.py \
    --sft samples_sft_full.jsonl \
    --dpo samples_dpo_full.jsonl \
    --seq-len 4096

echo "=== train SFT (50 epochs) → DPO (1 epoch) — OVERFIT ==="
PYTHONPATH=. python training/director/train_lora.py \
    --stage both \
    --sft-path training/director/samples_sft_full.jsonl \
    --dpo-path training/director/samples_dpo_full.jsonl \
    --adapter-dir training/director/adapters_overfit \
    --sft-epochs 50 \
    --dpo-epochs 1 \
    --per-device-batch 1 \
    --grad-accum 8

echo "=== infer smoke (adapter=adapters_overfit/dpo) ==="
PYTHONPATH=. python training/director/infer.py \
    --adapter training/director/adapters_overfit/dpo || true

echo "=== DONE ==="
