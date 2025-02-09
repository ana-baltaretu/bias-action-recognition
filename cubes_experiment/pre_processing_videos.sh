#!/bin/bash

# Define paths
FOLDER_PATH="../daic/ConvLSTM_model_training/input_data"
MODEL_PATH="../daic/ConvLSTM_model_training/action-recognition-by-eriklindernoren"
TRAIN_PERCENTAGE=80

TEMP_FOLDER_PATH="/tmp/data_ConvLSTM"
TEMP_MODEL_PATH="/tmp/model_ConvLSTM"

# Copy to tmp folder cause apptainer can't see normal folder for some reason???
cp -r "$FOLDER_PATH" "$TEMP_FOLDER_PATH"
cp -r "$MODEL_PATH" "$TEMP_MODEL_PATH"

# Define Apptainer image
CONTAINER="pre_processing.sif"

# Run processing steps inside the Apptainer container
apptainer exec $CONTAINER python3 move_green_videos.py "$TEMP_FOLDER_PATH"
echo "Separated train-validation and test videos!"
apptainer exec $CONTAINER python3 generate_labels_for_training.py "$TEMP_FOLDER_PATH" "$TEMP_MODEL_PATH" "$TRAIN_PERCENTAGE"
apptainer exec $CONTAINER python3 extract_frames.py --dataset_path "$TEMP_FOLDER_PATH/train-validation"
apptainer exec $CONTAINER python3 extract_frames.py --dataset_path "$TEMP_FOLDER_PATH/test"

# Move back to normal folder
cp -r "$TEMP_FOLDER_PATH" "$FOLDER_PATH"
cp -r "$TEMP_MODEL_PATH" "$MODEL_PATH"