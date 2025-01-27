#!/bin/sh
# --- General DAIC setup ---
#SBATCH --partition=prb,insy,general
#SBATCH --qos=short
#SBATCH --output=run_10_90scenes/render_cubes-%x-%j.out
#SBATCH --error=run_10_90scenes/render_cubes-%x-%j.err

# --- Setup specific for task ---
#SBATCH --job-name=run_10_90scenes
#SBATCH --time=0:10:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
#SBATCH --gpu-bind=closest
#SBATCH --mem=2GB
#SBATCH --array=1-90

# --- Email me when job finishes ---
#SBATCH --mail-type=ALL
#SBATCH --mail-user=a.baltaretu@student.tudelft.nl

# Load necessary modules
module use /opt/insy/modulefiles
module load cuda/12.1
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-12.1/lib64

config=scene_info.config          # Path to config file

# Obtain parameters from config file:
camera_x=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $2}' $config)
camera_y=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $3}' $config)
camera_z=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $4}' $config)
cubes_red=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $5}' $config)
cubes_blue=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $6}' $config)
cubes_random_position_seed=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $7}' $config)

# Set Apptainer variables
export APPTAINER_HOME="/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/parallel_cube_render/"
export APPTAINER_NAME="render_cubes.sif"

srun \
    apptainer exec --nv $APPTAINER_HOME/$APPTAINER_NAME \
    blender --background --python main.py -- \
    "${SLURM_ARRAY_TASK_ID}" \
    "${camera_x}" "${camera_y}" "${camera_z}" \
    "${cubes_red}" "${cubes_blue}" \
    "${cubes_random_position_seed}"