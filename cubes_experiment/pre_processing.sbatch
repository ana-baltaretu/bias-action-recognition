#!/bin/sh
# --- General DAIC setup ---
#SBATCH --partition=prb,insy,general
#SBATCH --qos=short
#SBATCH --output=logs/latest_run-%x-%j.out
#SBATCH --error=logs/latest_run-%x-%j.err

# --- Setup specific for task ---
#SBATCH --job-name=pre_process_frames
#SBATCH --time=0:15:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
#SBATCH --gpu-bind=closest
#SBATCH --mem=1GB

# --- Email me when job finishes ---
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=a.baltaretu@student.tudelft.nl

# Load necessary modules
module use /opt/insy/modulefiles
module load cuda/12.4
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-12.4/lib64

# Set Apptainer variables
export APPTAINER_HOME="/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/cubes_experiment/"
export APPTAINER_NAME="pre_processing.sif"

# Start measuring execution time
start_time=$(date +%s)

# Run script
srun sh pre_processing_videos.sbatch # TODO: CHECK IF THIS ACTUALLY WORKS!!!!!!!!!!!!!!!

# End measuring execution time
end_time=$(date +%s)

elapsed_time=$((end_time - start_time))
echo "Elapsed time: $elapsed_time seconds"