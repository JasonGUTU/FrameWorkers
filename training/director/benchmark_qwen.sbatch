#!/bin/bash
#SBATCH --job-name=qwen_benchmark
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=0:30:00
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=h200:1
#SBATCH --output=/home/zhendong_li/FrameWorkers/training/director/logs/benchmark_%j.log
#SBATCH --error=/home/zhendong_li/FrameWorkers/training/director/logs/benchmark_%j.error
#SBATCH --qos=neurips-2026
#SBATCH --partition=non-reserved
#SBATCH --constraint=zone-sof1

set -euo pipefail

REPO_ROOT="/home/zhendong_li/FrameWorkers"
cd "$REPO_ROOT"

ENV_DIR="/home/zhendong_li/.conda-envs/director-train"
set +u
source ~/.bashrc
conda activate "$ENV_DIR" 2>/dev/null || conda activate frameworkers
set -u

export PYTHONUNBUFFERED=1

PYTHONPATH=. python -u training/director/benchmark_qwen.py

echo "=== DONE ==="
