#!/usr/bin/env bash
# End-to-end smoke: validate → SFT → DPO → inference.
# Run on a GPU node (one-shot). Activates frameworkers conda env via
# /scratch (mounted on both login + GPU nodes; no PATH dependency).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

# ---------------------------------------------------------------------------
# Environment setup: source the cephfs-resident director-train env.
# /scratch is node-local on this cluster, so the frameworkers conda env at
# /scratch/zhendong_li/tools/miniconda3/envs/frameworkers is invisible to
# GPU nodes. director-train is a `conda create --copy --clone` of that env
# placed on cephfs (/home, shared across all nodes), and its activate
# script is self-contained — no `conda` binary needed on the GPU node.
# ---------------------------------------------------------------------------
echo "=== [0/5] env setup ==="

ENV_DIR="/home/zhendong_li/.conda-envs/director-train"

if [ ! -x "$ENV_DIR/bin/python" ]; then
    echo "FATAL: $ENV_DIR/bin/python not found — clone env first via:" >&2
    echo "  conda create --copy --prefix $ENV_DIR --clone /scratch/zhendong_li/tools/miniconda3/envs/frameworkers" >&2
    exit 1
fi

# Conda envs created with --copy don't ship a venv-style `activate` script,
# but they're fully self-contained: prepending bin/ to PATH is equivalent.
export PATH="$ENV_DIR/bin:$PATH"
export CONDA_PREFIX="$ENV_DIR"

echo "python: $(which python) — $(python --version)"

# ---------------------------------------------------------------------------
# 1. Install training deps if missing (idempotent)
# ---------------------------------------------------------------------------
echo "=== [1/5] ensure training deps ==="
python -c "import torch, transformers, trl, peft, datasets, accelerate" 2>/dev/null \
    || pip install -r training/director/requirements-training.txt

# ---------------------------------------------------------------------------
# 2. Validate samples (should pass all 5 checks now that transformers is installed)
# ---------------------------------------------------------------------------
echo "=== [2/5] validate samples ==="
PYTHONPATH=. python training/director/validate.py --seq-len 4096

# ---------------------------------------------------------------------------
# 3. Train: SFT → DPO on 5+5 samples
# ---------------------------------------------------------------------------
echo "=== [3/5] train LoRA (SFT → DPO) ==="
PYTHONPATH=. python training/director/train_lora.py --stage both

# ---------------------------------------------------------------------------
# 4. Inference smoke
# ---------------------------------------------------------------------------
echo "=== [4/5] inference smoke ==="
PYTHONPATH=. python training/director/infer.py --adapter adapters/dpo

# ---------------------------------------------------------------------------
# 5. Report
# ---------------------------------------------------------------------------
echo "=== [5/5] summary ==="
echo "adapters saved in: $REPO_ROOT/training/director/adapters/"
echo "=== smoke OK ==="
