#!/usr/bin/env bash
# Entry point: ensure conda env + submit training sbatch.
# Run from any node where /scratch is visible (typically login).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

# 1. Ensure the cephfs env is ready (idempotent)
bash "$HERE/ensure_env.sh"

# 2. Submit the actual training job
sbatch "$HERE/train_full.sbatch"
