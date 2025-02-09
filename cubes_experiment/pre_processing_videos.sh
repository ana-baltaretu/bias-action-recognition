#!/bin/bash

# Define paths
FOLDER_PATH="../daic/ConvLSTM_model_training/input_data/"
MODEL_PATH="../daic/ConvLSTM_model_training/action-recognition-by-eriklindernoren"
TRAIN_PERCENTAGE=80

# Define Apptainer image
CONTAINER="pre_processing.sif"

# Run processing steps inside the Apptainer container
apptainer exec $CONTAINER python3 move_green_videos.py "$FOLDER_PATH"
apptainer exec $CONTAINER python3 generate_labels_for_training.py "$FOLDER_PATH" "$MODEL_PATH" "$TRAIN_PERCENTAGE"
apptainer exec $CONTAINER python3 extract_frames.py --dataset_path "$FOLDER_PATH/train-validation"
apptainer exec $CONTAINER python3 extract_frames.py --dataset_path "$FOLDER_PATH/test"
