#!/bin/bash
#SBATCH --job-name=v4_sft_rich_q4b
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=10:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:2
#SBATCH --output=/home/zhendong_li/FrameWorkers/training/director/logs/v4_sft_rich_q4b_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/training/director/logs/v4_sft_rich_q4b_%j.error
#SBATCH --qos=neurips-2026
#SBATCH --partition=non-reserved
#SBATCH --constraint=zone-sof1

# v4_500 SFT — rich variant, Qwen3-4B base (parallel to Qwen3-8B run).
# Output adapter is at adapters_v4_500_qwen4b/rich/sft (does NOT touch
# adapters_v4_500/rich/sft which is the 8B run).

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
nvidia-smi -L

RUN_STAMP=$(date +%Y%m%d_%H%M%S)
BASE_MODEL="Qwen/Qwen3-4B"
SFT_DATA="training/director/samples_sft_full.v4_500.jsonl"
ADAPTER_DIR="training/director/adapters_v4_500_qwen4b/rich"
EPOCHS=8

echo "=== v4_500 SFT (rich, Qwen3-4B, 2-GPU, ${EPOCHS}ep) ==="
echo "  base model:  ${BASE_MODEL}"
echo "  data:        ${SFT_DATA}"
echo "  output:      ${ADAPTER_DIR}/sft"
echo "  run stamp:   ${RUN_STAMP}"

export PYTHONUNBUFFERED=1

MASTER_PORT=$((20000 + SLURM_JOB_ID % 10000))
echo "  master_port: ${MASTER_PORT}"

PYTHONPATH=. torchrun --nproc_per_node=2 --master_port="${MASTER_PORT}" \
    training/director/train_sft.py \
        --base-model "${BASE_MODEL}" \
        --sft-path "${SFT_DATA}" \
        --adapter-dir "${ADAPTER_DIR}" \
        --sft-epochs "${EPOCHS}" \
        --per-device-batch 1 \
        --grad-accum 4

echo "=== eval on v4_500 (522 cases, with_rationale schema) ==="
PYTHONPATH=. python evals/director_routing/eval_lora.py \
    --base-model "${BASE_MODEL}" \
    --adapter "${ADAPTER_DIR}/sft" \
    --cases evals/director_routing/eval_cases_v4_500.json \
    --schema-variant with_rationale \
    --name "v4500_q4b_sft_rich_${RUN_STAMP}" || true

echo "=== DONE — adapter ${ADAPTER_DIR}/sft, eval logged in Runtime/eval_routing/ ==="
