#!/bin/sh
#SBATCH --job-name=cubes
#SBATCH --partition=general
#SBATCH --qos=short
#SBATCH --time=0:10:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:1
#SBATCH --gpu-bind=closest
#SBATCH --mem=2GB
#SBATCH --output=slurm-%x-%j.out
#SBATCH --error=slurm-%x-%j.err

# Load necessary modules
module use /opt/insy/modulefiles
module load cuda/12.1

# Set Apptainer variables
export LIBGL_ALWAYS_SOFTWARE=1 # This forces Blender to use CPU-based OpenGL rendering, avoid libEGL
export APPTAINER_HOME="/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/test_basic_blender/"
export APPTAINER_NAME="test_generate_cube.sif"

# Run the container with Apptainer
srun apptainer exec --nv $APPTAINER_HOME/$APPTAINER_NAME blender --background --python test_generate_cube.py
