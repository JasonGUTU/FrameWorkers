#!/bin/bash
#SBATCH --job-name=qwen3_grpo_expanded
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=50:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:1
#SBATCH --output=/home/zhendong_li/FrameWorkers/training/director/logs/grpo_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/training/director/logs/grpo_%j.error
#SBATCH --qos=neurips-2026
#SBATCH --partition=non-reserved
#SBATCH --constraint=zone-sof1

# GRPO training on expanded set: 1396 templated + ≤420 hard failures from
# LoRA(checkpoint-712) inference on SFT training data.
#
# Pipeline:
#   1. infer_on_training.sbatch (542238) → infer_on_training_failed.jsonl
#   2. build_expanded_grpo_data.py → samples_grpo_v1.expanded.jsonl (≤1816 samples)
#   3. THIS sbatch: GRPO from checkpoint-712 → adapter_grpo_v3_expanded/
#
# Submit AFTER inference completes:
#   sbatch --dependency=afterok:542238 train_grpo_v3_expanded.sbatch

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

# Step 1: build expanded training set (idempotent — can rerun)
echo "=== build expanded GRPO data ==="
PYTHONPATH=. python training/director/build_expanded_grpo_data.py \
    --base training/director/samples_grpo_v1.templated.jsonl \
    --failed training/director/infer_on_training_failed.jsonl \
    --cap 420 \
    --out training/director/samples_grpo_v1.expanded.jsonl

# Step 2: GRPO training
RUN_STAMP=$(date +%Y%m%d_%H%M%S)
SFT_ADAPTER="training/director/adapters_grpo_base/qwen3_v3tmpl_e4_step712"
GRPO_OUT="training/director/adapters_grpo_v3_expanded/qwen3_${RUN_STAMP}/grpo"
GRPO_DATA="training/director/samples_grpo_v1.expanded.jsonl"
EPOCHS=3

echo "=== GRPO training ==="
echo "Run timestamp: ${RUN_STAMP}"
echo "SFT base:      ${SFT_ADAPTER}"
echo "GRPO out:      ${GRPO_OUT}"
echo "GRPO data:     ${GRPO_DATA}"
echo "Epochs:        ${EPOCHS}"

PYTHONPATH=. python training/director/train_grpo.py \
    --adapter-in  "${SFT_ADAPTER}" \
    --adapter-out "${GRPO_OUT}" \
    --sft-path    "${GRPO_DATA}" \
    --num-generations 4 \
    --epochs "${EPOCHS}" \
    --max-new-tokens 1024 \
    --learning-rate 1e-6 \
    --beta 0.04 \
    --logging-steps 5 \
    --save-steps 200

echo "=== infer smoke (adapter=${GRPO_OUT}) ==="
PYTHONPATH=. python training/director/infer.py --adapter "${GRPO_OUT#training/director/}" || true

echo "=== 130-case eval on v3 GT ==="
PYTHONPATH=. python evals/director_routing/eval_lora.py \
    --adapter "${GRPO_OUT}" \
    --name "qwen3_grpo_v3_expanded_${RUN_STAMP}" || true

echo "=== DONE — adapter at ${GRPO_OUT}, eval logged in Runtime/eval_routing/ ==="
