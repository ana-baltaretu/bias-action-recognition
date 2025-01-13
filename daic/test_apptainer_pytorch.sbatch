#!/bin/sh
#SBATCH --job-name=test-pytorch
#SBATCH --account=ewi-insy-reit
#SBATCH --reservation=reit-course-containerization
#SBATCH --qos=reservation
#SBATCH --time=0:03:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:1
#SBATCH --mem=2GB
#SBATCH --output=slurm-%x-%j.out
#SBATCH --error=slurm-%x-%j.err

module use /opt/insy/modulefiles
module load cuda/12.1

export APPTAINER_HOME="/usr/bin/apptainer"
export APPTAINER_NAME="pytorch2.2.1-cuda12.1.sif"

srun apptainer exec --nv $APPTAINER_HOME/$APPTAINER_NAME python -c "import torch; print(torch.__version__)"