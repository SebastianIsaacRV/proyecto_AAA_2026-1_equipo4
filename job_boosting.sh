#!/bin/bash
#SBATCH --job-name=boosting_delitos
#SBATCH --output=logs/boosting_%j.out
#SBATCH --error=logs/boosting_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=02:00:00

source /apps/miniconda3/etc/profile.d/conda.sh
conda activate mlflow

export MLFLOW_TRACKING_URI="https://dagshub.com/SebastianIsaacRV/proyecto_AAA_2026-1_equipo4.mlflow"
export MLFLOW_TRACKING_USERNAME="SebastianIsaacRV"
export MLFLOW_TRACKING_PASSWORD="fee2eff0dc1f07f5a5358e83ffeb5aa125543ac6"

cd /lustre/home/estudiante_58/proyecto_AAA_2026-1_equipo4
python notebooks/modelado_boosting.py
