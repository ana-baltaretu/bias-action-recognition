import cv2
import numpy as np
import os

# === Settings ===
prefix = "data/cartwheel_11_modified"
video_paths = [
    f"{prefix}_hispanic.mp4",
    f"{prefix}_african.mp4",
    f"{prefix}_asian.mp4",
    f"{prefix}_middle_eastern.mp4",
    f"{prefix}_white.mp4",
    f"{prefix}_indian.mp4",
    f"{prefix}_south_east_asian.mp4"
]
# frame_number = 32
# output_path = "combined_frame_female.png"

frame_number = 26
output_path = "combined_frame_male.png"

crop_size = (450, 450)  # width, height
crop_top_left = (400, 150)  # (x, y) coordinates

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_thickness = 2
label_height = 35

# === Helper to extract skin color from filename ===
def extract_skin_label(filename):
    base = os.path.basename(filename).replace(".mp4", "")
    parts = base.split("_modified_")
    if len(parts) > 1:
        return parts[1].replace("_", " ").title()
    else:
        return "Original"

# === Process each video ===
frames_with_labels = []

for path in video_paths:
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    success, frame = cap.read()
    if not success:
        print(f"⚠️ Could not read frame {frame_number} from {path}")
        cropped = np.zeros((*crop_size[::-1], 3), dtype=np.uint8)
    else:
        x, y = crop_top_left
        w, h = crop_size
        cropped = frame[y:y+h, x:x+w]
        if cropped.shape[0] != h or cropped.shape[1] != w:
            print(f"⚠️ Cropped frame from {path} has incorrect size. Using blank fallback.")
            cropped = np.zeros((*crop_size[::-1], 3), dtype=np.uint8)

    # Create label image
    label_text = extract_skin_label(path)
    label_img = np.ones((label_height, cropped.shape[1], 3), dtype=np.uint8) * 255
    text_size = cv2.getTextSize(label_text, font, font_scale, font_thickness)[0]
    text_x = (label_img.shape[1] - text_size[0]) // 2
    text_y = (label_img.shape[0] + text_size[1]) // 2
    cv2.putText(label_img, label_text, (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness)

    # Stack frame and label
    combined = np.vstack((cropped, label_img))
    frames_with_labels.append(combined)
    cap.release()

# === Combine side by side and save ===
final_image = np.hstack(frames_with_labels)
cv2.imwrite(output_path, final_image)
print(f"✅ Combined labeled cropped frame saved to: {output_path}")
