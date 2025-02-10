#!/bin/sh
# --- General DAIC setup ---
#SBATCH --partition=prb,insy,general
#SBATCH --qos=short
#SBATCH --output=logs/latest_run-%x-%j.out
#SBATCH --error=logs/latest_run-%x-%j.err

# --- Setup specific for task ---
#SBATCH --job-name=train_ConvLSTM_model
#SBATCH --time=0:10:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
#SBATCH --gpu-bind=closest
#SBATCH --mem=16GB

# --- Email me when job finishes ---
#SBATCH --mail-type=ALL
#SBATCH --mail-user=a.baltaretu@student.tudelft.nl

# Load necessary modules
module use /opt/insy/modulefiles
module load cuda/12.4
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-12.4/lib64

# Set Apptainer variables
export APPTAINER_HOME="/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/ConvLSTM_model_training/"
export APPTAINER_NAME="model_training.sif"

# Start measuring execution time
start_time=$(date +%s)

# TODO: Change "dataset_path" and "split_path" as needed!!!!
# Run script
srun \
    apptainer exec --nv $APPTAINER_HOME/$APPTAINER_NAME \
    python3 ./action-recognition-by-eriklindernoren/train.py \
    --dataset_path "$APPTAINER_HOME/training_data/train-validation-frames" \
    --split_path "$APPTAINER_HOME/action-recognition-by-eriklindernoren/labels/" \
    --num_epochs 100 \
    --sequence_length 40 \
    --img_dim 112 \
    --latent_dim 512 \
    --batch_size 8

# End measuring execution time
end_time=$(date +%s)

elapsed_time=$((end_time - start_time))
echo "Elapsed time: $elapsed_time seconds"