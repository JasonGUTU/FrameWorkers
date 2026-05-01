#!/bin/bash
#SBATCH --job-name=director_eval_lora_norat
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=2:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:1
#SBATCH --output=/home/zhendong_li/FrameWorkers/training/director/logs/eval_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/training/director/logs/eval_%j.error
#SBATCH --qos=neurips-2026
#SBATCH --partition=non-reserved
#SBATCH --constraint=zone-sof1

# Eval a no-rationale LoRA adapter against eval_cases.json with the
# canonical no-rationale system prompt (--schema-variant no_rationale).
# Sister of eval_full.sbatch.
#
# Required env: ADAPTER. Optional: NAME (defaults to <basename>_<dirname>).
#
# Example:
#   sbatch --export=ALL,ADAPTER=training/director/adapters_grpo_base/qwen3_no_rationale_e4/sft,NAME=sft_qwen3_no_rationale_e4_209 \
#          training/director/eval_full_no_rationale.sbatch

set -euo pipefail

: "${ADAPTER:?ADAPTER env var required}"
NAME="${NAME:-$(basename $(dirname $ADAPTER))_$(basename $ADAPTER)}"

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
echo "python: $(which python)"
echo "adapter: $ADAPTER"
echo "name:    $NAME"
echo "schema_variant: no_rationale"
nvidia-smi | head -20

PYTHONPATH=. python evals/director_routing/eval_lora.py \
    --adapter "$ADAPTER" \
    --name "$NAME" \
    --schema-variant no_rationale

echo "=== DONE ==="
