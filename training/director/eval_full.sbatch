#!/bin/bash
#SBATCH --job-name=director_eval_lora
#SBATCH --nodelist=sof1-h200-[0,1,2,3,4,6,7]
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=2:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:1
#SBATCH --output=/home/zhendong_li/FrameWorkers/training/director/logs/eval_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/training/director/logs/eval_%j.error
#SBATCH --qos=eccv-2026
#SBATCH --partition=non-reserved

# Eval a trained director-routing LoRA against the 100 held-out cases.
# Required env var: ADAPTER and PROMPT (full|bare). NAME is optional tag.
#
# Example:
#   sbatch --export=ALL,ADAPTER=training/director/adapters_full/dpo,PROMPT=full,NAME=full_dpo \
#          training/director/eval_full.sbatch

set -euo pipefail

: "${ADAPTER:?ADAPTER env var required — e.g. training/director/adapters_full/dpo}"
: "${PROMPT:?PROMPT env var required — full | bare}"
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
echo "prompt:  $PROMPT"
echo "name:    $NAME"
nvidia-smi | head -20

PYTHONPATH=. python evals/director_routing/eval_lora.py \
    --adapter "$ADAPTER" \
    --prompt "$PROMPT" \
    --name "$NAME"

echo "=== DONE ==="
