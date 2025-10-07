import cv2
import numpy as np
import os

# === Input Settings ===
# camera = "camera_far" # camera_near, camera_far
background = "stadium_01" # autumn_hockey, konzerthaus, stadium_01
base_folder = r"C:\Users\Ana\Desktop\bias-action-recognition\framework\models\i3d-torch\data\run_results\top_20_kinetics_actions"
action = "cartwheel"
skin_color = "south_east_asian" # asian, african, hispanic, indian, middle_eastern
video_name = f"{action}_0_modified_{skin_color}" #
video1_path = rf"{base_folder}\camera_near\{background}\__generated_synthetic_videos\{action}\{video_name}.mp4"
video2_path = rf"{base_folder}\camera_far\{background}\__generated_synthetic_videos\{action}\{video_name}.mp4"
frame_number = 110


output_dir = r"C:\Users\Ana\Desktop\bias-action-recognition\results_visualization\extract_example_frames\extracted_frames"
os.makedirs(output_dir, exist_ok=True)

crop_size = (450, 450)  # width, height
crop_top_left = (400, 150)  # (x, y)

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_thickness = 2
label_height = 35

def save_frame(video_path, frame_number, output_filename):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Could not open video {video_path}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_number >= total_frames or frame_number < 0:
        print(f"Frame number {frame_number} is out of bounds. Total frames: {total_frames}")
        cap.release()
        return

    current_frame = 0
    success = True

    while current_frame < frame_number and success:
        success, _ = cap.read()
        current_frame += 1

    success, frame = cap.read()
    cap.release()

    if success:
        x, y = crop_top_left
        w, h = crop_size
        cropped_frame = frame[y:y+h, x:x+w]

        if cropped_frame.shape[0] != h or cropped_frame.shape[1] != w:
            print("⚠️ Cropped area is outside the frame boundaries.")
            return

        cv2.imwrite(output_filename, cropped_frame)
        print(f"✅ Saved cropped frame {frame_number} to {output_filename}")
    else:
        print(f"⚠️ Could not read frame {frame_number} from {video_path}")

# Generate output filenames
name1 = os.path.splitext(os.path.basename(video1_path))[0]
name2 = os.path.splitext(os.path.basename(video2_path))[0]

save_frame(video1_path, frame_number, os.path.join(output_dir, f"{name1}_frame{frame_number}_{background}_near.png"))
save_frame(video2_path, frame_number, os.path.join(output_dir, f"{name2}_frame{frame_number}_{background}_far.png"))
