FOLDER_PATH="/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/ConvLSTM_model_training/input_data" # TODO: Update with the actual folder path

python move_green_videos.py "$FOLDER_PATH"

MODEL_PATH="/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/ConvLSTM_model_training/action-recognition-by-eriklindernoren"
TRAIN_PERCENTAGE=80

python generate_labels_for_training.py "$FOLDER_PATH" "$MODEL_PATH" "$TRAIN_PERCENTAGE"

python extract_frames.py --dataset_path "{$FOLDER_PATH}/train-validation" # TODO: Get this working
python extract_frames.py --dataset_path "{$FOLDER_PATH}/test" # TODO: Get this working