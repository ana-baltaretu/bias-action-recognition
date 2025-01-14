#!/bin/sh
#SBATCH --job-name=plot-sine
#SBATCH --partition=general
#SBATCH --qos=short
#SBATCH --time=0:03:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:1
#SBATCH --mem=2GB
#SBATCH --output=slurm-%x-%j.out
#SBATCH --error=slurm-%x-%j.err

# Load necessary modules
module use /opt/insy/modulefiles
module load cuda/12.1

# Set Apptainer variables
export APPTAINER_HOME="/home/nfs/abaltaretu/bias-action-recognition/daic/test_sine_wave/"
export APPTAINER_NAME="test_sine_wave.sif"

# Run the container with Apptainer
srun apptainer exec --nv $APPTAINER_HOME/$APPTAINER_NAME python test_sine_wave.py
