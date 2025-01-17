#!/bin/sh
#SBATCH --job-name=cubes
#SBATCH --partition=prb,insy,general
#SBATCH --qos=short
#SBATCH --time=2:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
#SBATCH --gpu-bind=closest
#SBATCH --mem=8GB
#SBATCH --output=slurm-%x-%j.out
#SBATCH --error=slurm-%x-%j.err

# --- Email me when job finishes ---
#SBATCH --mail-type=ALL
#SBATCH --mail-user=a.baltaretu@student.tudelft.nl

# Load necessary modules
module use /opt/insy/modulefiles
module load cuda/12.1
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-12.1/lib64

# Set Apptainer variables
export APPTAINER_HOME="/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/test_basic_blender/"
export APPTAINER_NAME="test_generate_cube.sif"

# Run the container with Apptainer
srun apptainer exec --nv $APPTAINER_HOME/$APPTAINER_NAME blender --background --python test_generate_cube.py
