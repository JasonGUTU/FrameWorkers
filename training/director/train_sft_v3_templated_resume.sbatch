#!/bin/bash
#SBATCH --job-name=qwen3_sft_resume_e4
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

# Resume SFT from checkpoint-712 (epoch 4, loss=0.017) → continue toward 50 epochs.
# Original Job 541556 was preempted by SLURM at step 825 / 8900 (non-reserved partition).
# Now restarting from checkpoint-712 (the last save before preemption).
#
# IMPORTANT: checkpoint-712 has been backed up to
#   training/director/adapters_grpo_base/qwen3_v3tmpl_e4_step712/
# so even if save_total_limit=1 deletes it during continuation, the GRPO
# base is preserved. Do NOT touch adapters_grpo_base/.
#
# Continuation runs in the SAME adapter dir as original (qwen3_20260427_005706)
# so trainer can find checkpoint-712 and resume from it.

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

ADAPTER_DIR="training/director/adapters_overfit_templated/qwen3_20260427_005706"
RESUME_CKPT="${ADAPTER_DIR}/sft/checkpoint-890"

echo "=== Resume target: ${RESUME_CKPT} ==="
ls -la "${RESUME_CKPT}/" || { echo "FATAL: resume checkpoint not found" >&2; exit 1; }

echo "=== validate samples_sft_full.templated.jsonl ==="
PYTHONPATH=. python training/director/validate.py \
    --sft samples_sft_full.templated.jsonl \
    --seq-len 8192

echo "=== SFT resume: 50 epochs total, picking up from step 712 (epoch 4) ==="
PYTHONPATH=. python training/director/train_sft.py \
    --sft-path training/director/samples_sft_full.templated.jsonl \
    --adapter-dir "${ADAPTER_DIR}" \
    --sft-epochs 50 \
    --per-device-batch 1 \
    --grad-accum 8 \
    --resume-from-checkpoint "${RESUME_CKPT}"

echo "=== infer smoke (adapter=${ADAPTER_DIR}/sft) ==="
PYTHONPATH=. python training/director/infer.py \
    --adapter "${ADAPTER_DIR}/sft" || true

# Full 130-case eval on v3 GT — auto-runs only if SFT completed successfully.
# If preempted mid-training, this won't fire; eval the latest checkpoint manually.
RUN_STAMP_END=$(date +%Y%m%d_%H%M%S)
echo "=== 130-case eval on v3 GT ==="
PYTHONPATH=. python evals/director_routing/eval_lora.py \
    --adapter "${ADAPTER_DIR}/sft" \
    --name "qwen3_sft_v3tmpl_full_${RUN_STAMP_END}" || true

echo "=== DONE — adapter at ${ADAPTER_DIR}/sft, eval logged in Runtime/eval_routing/ ==="
