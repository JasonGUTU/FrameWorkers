#!/bin/bash
#SBATCH --job-name=qwen3_sft_v3tmpl_overfit
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=50:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:4
#SBATCH --output=/home/zhendong_li/FrameWorkers/training/director/logs/train_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/training/director/logs/train_%j.error
#SBATCH --qos=neurips-2026
#SBATCH --partition=non-reserved
#SBATCH --constraint=zone-sof1

# SFT 50 epochs on v3-aligned TEMPLATED data — Qwen3-8B base.
# Input:  training/director/samples_sft_full.templated.jsonl  (1417 samples)
# Output: training/director/adapters_overfit_templated/qwen3_<TIMESTAMP>/sft/
#         (qwen3_ prefix isolates Qwen3-8B runs from old Qwen2.5-7B adapters;
#          timestamp subdirectory so successive runs do not overwrite)
# Data lineage:
#   - Path B aligned with v3 eval (Round 1 opt-in audio + Round 2 dep-aware)
#   - 7 audio-baked shapes rewritten (drop M+A+AM from chain + user_goal)
#   - 1 new shape: extend_ambience (covers extend_05's audio underspec fix)
#   - Templated rationale + intents (chain-free, programmatic per chain)
# Model: Qwen/Qwen3-8B (thinking mode OFF for inference/eval)

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
nvidia-smi -L

python -c "import torch, transformers, trl, peft, datasets, accelerate" 2>/dev/null \
    || pip install -r training/director/requirements-training.txt

RUN_STAMP=$(date +%Y%m%d_%H%M%S)
ADAPTER_DIR="training/director/adapters_overfit_templated/qwen3_${RUN_STAMP}"
echo "Run timestamp: ${RUN_STAMP}"
echo "Adapter dir:   ${ADAPTER_DIR}"

echo "=== validate samples_sft_full.templated.jsonl ==="
PYTHONPATH=. python training/director/validate.py \
    --sft samples_sft_full.templated.jsonl \
    --seq-len 8192

echo "=== SFT 50 epochs on v3 TEMPLATED data (4-GPU DDP) ==="
PYTHONPATH=. torchrun --nproc_per_node=4 --master_port=29500 \
    training/director/train_sft.py \
    --sft-path training/director/samples_sft_full.templated.jsonl \
    --adapter-dir "${ADAPTER_DIR}" \
    --sft-epochs 50 \
    --per-device-batch 4 \
    --grad-accum 2

echo "=== infer smoke (adapter=${ADAPTER_DIR}/sft) ==="
PYTHONPATH=. python training/director/infer.py \
    --adapter "${ADAPTER_DIR}/sft" || true

echo "=== DONE — adapter at ${ADAPTER_DIR}/sft ==="
