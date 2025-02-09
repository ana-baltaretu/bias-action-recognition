#!/bin/bash

# Define paths
FOLDER_PATH="../daic/ConvLSTM_model_training/input_data/"
MODEL_PATH="../daic/ConvLSTM_model_training/action-recognition-by-eriklindernoren"
TRAIN_PERCENTAGE=80

# Define Apptainer image
CONTAINER="pre_processing.sif"

# Bind FOLDER_PATH so the container can access it
BIND="--bind $FOLDER_PATH:$FOLDER_PATH"

# Run processing steps inside the Apptainer container
apptainer exec "$BIND" $CONTAINER python3 move_green_videos.py "$FOLDER_PATH"
apptainer exec "$BIND" $CONTAINER python3 generate_labels_for_training.py "$FOLDER_PATH" "$MODEL_PATH" "$TRAIN_PERCENTAGE"
apptainer exec "$BIND" $CONTAINER python3 extract_frames.py --dataset_path "$FOLDER_PATH/train-validation"
apptainer exec "$BIND" $CONTAINER python3 extract_frames.py --dataset_path "$FOLDER_PATH/test"
