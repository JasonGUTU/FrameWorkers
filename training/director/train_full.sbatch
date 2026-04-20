#!/bin/bash
#SBATCH --job-name=director_lora_full
#SBATCH --nodelist=sof1-h200-[0,1,2,3,4,6,7]
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=8:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:1
#SBATCH --output=/home/zhendong_li/FrameWorkers/training/director/logs/train_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/training/director/logs/train_%j.error
#SBATCH --qos=eccv-2026
#SBATCH --partition=batch

set -euo pipefail

REPO_ROOT="/home/zhendong_li/FrameWorkers"
cd "$REPO_ROOT"

# ---------------------------------------------------------------------------
# Env: source ~/.bashrc to bring in conda init, then activate director-train
# by full cephfs path. The env lives on cephfs (shared across nodes); the
# source miniconda in ~/.bashrc points at /scratch/…/miniconda3 which must be
# resolvable on this GPU node for `conda activate` to work.
# If /scratch is node-local and not visible here, activation fails loudly
# below — in that case, fall back to PATH-prepend:
#   export PATH="$ENV_DIR/bin:$PATH" ; export CONDA_PREFIX="$ENV_DIR"
# ---------------------------------------------------------------------------
ENV_DIR="/home/zhendong_li/.conda-envs/director-train"
set +u                             # ~/.bashrc may touch unset vars
source ~/.bashrc
conda activate "$ENV_DIR"
set -u

if [ -z "${CONDA_PREFIX:-}" ] || [ ! -x "$CONDA_PREFIX/bin/python" ]; then
    echo "FATAL: conda activate failed." >&2
    echo "       ~/.bashrc conda init points at /scratch/…/miniconda3 which may not be visible on this GPU node." >&2
    echo "       Either (a) bootstrap a cephfs miniconda and rerun 'conda init' from it, or" >&2
    echo "       (b) revert this sbatch to the PATH-prepend activation pattern (see comment above)." >&2
    exit 1
fi
echo "python: $(which python) — $(python --version)"
echo "CONDA_PREFIX=$CONDA_PREFIX"
nvidia-smi | head -20

# ---------------------------------------------------------------------------
# Ensure training deps — pip into the cephfs env if something's missing
# (cephfs is writable from GPU node so this works even when scratch isn't).
# ---------------------------------------------------------------------------
python -c "import torch, transformers, trl, peft, datasets, accelerate" 2>/dev/null \
    || pip install -r training/director/requirements-training.txt

# ---------------------------------------------------------------------------
# Validate full-size samples before touching GPU
# ---------------------------------------------------------------------------
echo "=== validate samples_sft_full / samples_dpo_full ==="
PYTHONPATH=. python training/director/validate.py \
    --sft samples_sft_full.jsonl \
    --dpo samples_dpo_full.jsonl \
    --seq-len 4096

# ---------------------------------------------------------------------------
# Train: SFT (3 epochs) → DPO (1 epoch) on full datasets.
#   1110 SFT × 3 epochs / (batch 1 × grad-accum 8) ≈ 416 steps
#   500  DPO × 1 epoch  / (batch 1 × grad-accum 8) ≈  62 steps
# Output adapters: training/director/adapters_full/{sft,dpo}/
# ---------------------------------------------------------------------------
echo "=== train SFT → DPO on full datasets ==="
PYTHONPATH=. python training/director/train_lora.py \
    --stage both \
    --sft-path training/director/samples_sft_full.jsonl \
    --dpo-path training/director/samples_dpo_full.jsonl \
    --adapter-dir training/director/adapters_full \
    --sft-epochs 3 \
    --dpo-epochs 1 \
    --per-device-batch 1 \
    --grad-accum 8

# ---------------------------------------------------------------------------
# Inference smoke on the trained DPO adapter
# ---------------------------------------------------------------------------
echo "=== infer smoke (adapter=adapters_full/dpo) ==="
PYTHONPATH=. python training/director/infer.py \
    --adapter training/director/adapters_full/dpo || true

echo "=== DONE ==="
