#!/bin/bash
#SBATCH --job-name=v4_grpo_tmpl
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=30:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:2
#SBATCH --output=/home/zhendong_li/FrameWorkers/training/director/logs/v4_grpo_tmpl_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/training/director/logs/v4_grpo_tmpl_%j.error
#SBATCH --qos=neurips-2026
#SBATCH --partition=non-reserved
#SBATCH --constraint=zone-sof1

# v4_500 GRPO — templated variant (4 epoch).
# DEPENDS ON: train_sft_v4_templated_2gpu.sbatch finishing first
#             (reads SFT adapter at adapters_v4_500/templated/sft).

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
SFT_ADAPTER="training/director/adapters_v4_500/templated/sft"
GRPO_OUT="training/director/adapters_v4_500/templated/grpo"
GRPO_DATA="training/director/samples_grpo_v1.templated.v4_500.jsonl"
EPOCHS=4

if [ ! -d "${SFT_ADAPTER}" ]; then
    echo "FATAL: SFT adapter not found at ${SFT_ADAPTER}. Run train_sft_v4_templated_2gpu.sbatch first." >&2
    exit 1
fi

echo "=== v4_500 GRPO (templated, 2-GPU, ${EPOCHS}ep) ==="
echo "  SFT base:    ${SFT_ADAPTER}"
echo "  GRPO out:    ${GRPO_OUT}"
echo "  GRPO data:   ${GRPO_DATA}"
echo "  run stamp:   ${RUN_STAMP}"

RESUME_FROM="${RESUME_FROM:-}"
[ -n "${RESUME_FROM}" ] && echo "  resume from: ${RESUME_FROM}"

export PYTHONUNBUFFERED=1

MASTER_PORT=$((20000 + SLURM_JOB_ID % 10000))
echo "  master_port: ${MASTER_PORT}"

RESUME_ARG=()
[ -n "${RESUME_FROM}" ] && RESUME_ARG=(--resume-from "${RESUME_FROM}")

PYTHONPATH=. torchrun --nproc_per_node=2 --master_port="${MASTER_PORT}" \
    training/director/train_grpo.py \
        --adapter-in  "${SFT_ADAPTER}" \
        --adapter-out "${GRPO_OUT}" \
        --sft-path    "${GRPO_DATA}" \
        "${RESUME_ARG[@]}" \
        --num-generations 4 \
        --epochs "${EPOCHS}" \
        --max-new-tokens 1024 \
        --learning-rate 1e-6 \
        --beta 0.04 \
        --logging-steps 5 \
        --save-steps 200

echo "=== eval on v4_500 (522 cases, with_rationale schema) ==="
PYTHONPATH=. python evals/director_routing/eval_lora.py \
    --adapter "${GRPO_OUT}" \
    --cases evals/director_routing/eval_cases_v4_500.json \
    --schema-variant with_rationale \
    --name "v4500_grpo_templated_${RUN_STAMP}" || true

echo "=== DONE — adapter ${GRPO_OUT}, eval logged in Runtime/eval_routing/ ==="
