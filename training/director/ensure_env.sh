#!/usr/bin/env bash
# Ensure the cephfs-resident director-train conda env exists and is usable.
# MUST run on a node where /scratch/.../miniconda3 is visible (typically the
# login node), because the source env is cloned from /scratch which is
# node-local on this cluster and not visible to GPU compute nodes.
#
# Idempotent: no-ops if the env already imports torch/transformers/trl cleanly.
# Exit codes:
#   0 — env is ready to use
#   1 — source conda not available on this node → run on login node
#   2 — source frameworkers env missing → rebuild it first
#   3 — clone/install failed (see stderr)
set -euo pipefail

TARGET_ENV="/home/zhendong_li/.conda-envs/director-train"
SRC_CONDA="/scratch/zhendong_li/tools/miniconda3/bin/conda"
SRC_ENV="/scratch/zhendong_li/tools/miniconda3/envs/frameworkers"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REQ_FILE="$REPO_ROOT/training/director/requirements-training.txt"

# ---------------------------------------------------------------------------
# Fast path: env already imports required training deps
# ---------------------------------------------------------------------------
if [ -x "$TARGET_ENV/bin/python" ]; then
    if "$TARGET_ENV/bin/python" -c "import torch, transformers, trl, peft, datasets, accelerate" 2>/dev/null; then
        echo "[ensure_env] ✓ $TARGET_ENV already has all deps — nothing to do"
        exit 0
    fi
    echo "[ensure_env] env dir exists but training deps missing — pip-installing..."
    "$TARGET_ENV/bin/pip" install -r "$REQ_FILE" || exit 3
    echo "[ensure_env] ✓ deps installed into existing env"
    exit 0
fi

# ---------------------------------------------------------------------------
# Need to create env — require source conda + source frameworkers env
# ---------------------------------------------------------------------------
echo "[ensure_env] $TARGET_ENV missing — need to clone"

if [ ! -x "$SRC_CONDA" ]; then
    echo "[ensure_env] FATAL: $SRC_CONDA not found on this node." >&2
    echo "[ensure_env] /scratch is node-local. Run this on the login node where the scratch miniconda exists." >&2
    exit 1
fi

if [ ! -d "$SRC_ENV" ]; then
    echo "[ensure_env] FATAL: source env $SRC_ENV missing." >&2
    echo "[ensure_env] Create the frameworkers env first (see install_requirements.py)." >&2
    exit 2
fi

mkdir -p "$(dirname "$TARGET_ENV")"

echo "[ensure_env] cloning $SRC_ENV → $TARGET_ENV (--copy, self-contained for GPU nodes)..."
"$SRC_CONDA" create --yes --copy --prefix "$TARGET_ENV" --clone "$SRC_ENV" || exit 3

# Ensure training-specific pip deps are present (SFTTrainer / DPOTrainer etc)
if ! "$TARGET_ENV/bin/python" -c "import torch, transformers, trl, peft, datasets, accelerate" 2>/dev/null; then
    echo "[ensure_env] installing training requirements..."
    "$TARGET_ENV/bin/pip" install -r "$REQ_FILE" || exit 3
fi

echo "[ensure_env] ✓ $TARGET_ENV ready"
