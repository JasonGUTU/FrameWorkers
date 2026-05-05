#!/bin/bash
#SBATCH --job-name=director_eval_lora
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

# Eval a trained director-routing LoRA against the 100 held-out cases.
# Required env var: ADAPTER. NAME is optional tag.
#
# Example:
#   sbatch --export=ALL,ADAPTER=training/director/adapters_full/dpo,NAME=full_dpo \
#          training/director/eval_full.sbatch

set -euo pipefail

ADAPTER="${ADAPTER:-}"  # empty = base-model-only eval (no LoRA)
if [ -n "$ADAPTER" ]; then
    NAME="${NAME:-$(basename $(dirname $ADAPTER))_$(basename $ADAPTER)}"
else
    : "${NAME:?NAME env var required when running base-only eval (no ADAPTER)}"
fi
# Optional overrides — leave empty to use eval_lora.py defaults
CASES="${CASES:-}"
SCHEMA_VARIANT="${SCHEMA_VARIANT:-}"
BASE_MODEL="${BASE_MODEL:-}"

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
nvidia-smi | head -20

CMD=(python evals/director_routing/eval_lora.py --name "$NAME")
[ -n "$ADAPTER" ] && CMD+=(--adapter "$ADAPTER")
[ -n "$BASE_MODEL" ] && CMD+=(--base-model "$BASE_MODEL")
[ -n "$CASES" ] && CMD+=(--cases "$CASES")
[ -n "$SCHEMA_VARIANT" ] && CMD+=(--schema-variant "$SCHEMA_VARIANT")
echo "Running: ${CMD[*]}"
PYTHONPATH=. "${CMD[@]}"

echo "=== DONE ==="
