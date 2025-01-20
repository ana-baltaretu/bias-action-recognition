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
#SBATCH --array=1-3

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

config=jobarray.config          # Path to config file

# Obtain parameters from config file:
red=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $2}' $config)
green=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $3}' $config)
blue=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $4}' $config)

# Run the container with Apptainer
echo "Array task: ${SLURM_ARRAY_TASK_ID},  R: ${red}, G: ${green}, B: ${blue}" >> output.txt
srun apptainer exec --nv $APPTAINER_HOME/$APPTAINER_NAME blender --background --python test_generate_cube.py -- "${SLURM_ARRAY_TASK_ID}" "${red}" "${green}" "${blue}"
