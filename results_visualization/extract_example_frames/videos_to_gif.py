import cv2
import os
import numpy as np
import imageio
import glob
from collections import defaultdict

# === Settings ===
base_folder = r"C:\Users\Ana\Desktop\bias-action-recognition\framework\models\i3d-torch\data\run_results\top_20_kinetics_actions"
action = "cartwheel"
backgrounds = ["autumn_hockey", "konzerthaus", "stadium_01"]
cameras = ["camera_near", "camera_far"]
crop_top_left = (400, 150)  # x, y
crop_size = (450, 450)  # width, height
output_gif_path = r"C:\Users\Ana\Desktop\bias-action-recognition\results_visualization\extract_example_frames\video_grid.gif"
num_timepoints = 70
scale_factor = 0.15  # 0.5 or 0.25 for stronger compression

# === Find all skin colors ===
video_dict = defaultdict(list)  # skin_color -> list of (camera, background, path)

for cam in cameras:
    for bg in backgrounds:
        folder = os.path.join(base_folder, cam, bg, "__generated_synthetic_videos", action)
        pattern = os.path.join(folder, f"{action}_0_*.mp4")
        for video_path in glob.glob(pattern):
            filename = os.path.basename(video_path)
            if "modified_" in filename:
                skin_color = filename.replace(f"{action}_0_modified_", "").replace(".mp4", "")
            elif "initial" in filename:
                skin_color = "initial"
            else:
                continue
            video_dict[skin_color].append((cam, bg, video_path))

# Ensure all skin colors have full video sets
valid_skin_colors = [sc for sc, vids in video_dict.items() if len(vids) == 6]
print("✅ Found valid skin color rows:", valid_skin_colors)

# === Load Videos ===
video_caps_by_skin = {}
min_total_frames = float("inf")

for skin_color in valid_skin_colors:
    caps = []
    sorted_vids = []
    for cam in cameras:
        for bg in backgrounds:
            for c, b, path in video_dict[skin_color]:
                if c == cam and b == bg:
                    sorted_vids.append(path)
    for video_path in sorted_vids:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open {video_path}")
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        min_total_frames = min(min_total_frames, total_frames)
        caps.append(cap)
    video_caps_by_skin[skin_color] = caps

# === Sample frame indices ===
frame_indices = np.linspace(0, min_total_frames - 1, num=num_timepoints, dtype=int)

# === Generate GIF frames ===
gif_frames = []

for frame_idx in frame_indices:
    print(frame_idx)
    grid_rows = []
    for skin_color in valid_skin_colors:
        row_frames = []
        for cap in video_caps_by_skin[skin_color]:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                raise RuntimeError(f"Failed to read frame {frame_idx} from video ({skin_color})")
            x, y = crop_top_left
            w, h = crop_size
            cropped = frame[y:y+h, x:x+w]
            if cropped.shape[0] != h or cropped.shape[1] != w:
                raise ValueError(f"Cropped region out of bounds in {skin_color}")
            row_frames.append(cropped)
        row = np.hstack(row_frames)
        grid_rows.append(row)
    full_grid = np.vstack(grid_rows)

    # After creating full_grid (before adding to gif_frames)
    resized = cv2.resize(full_grid, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
    gif_frames.append(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))

    # gif_frames.append(cv2.cvtColor(full_grid, cv2.COLOR_BGR2RGB))  # convert to RGB for GIF

# === Save to GIF ===
# imageio.mimsave(output_gif_path, gif_frames, fps=24)
# print(f"✅ Saved GIF to {output_gif_path}")

from PIL import Image

frames = [Image.fromarray(f) for f in gif_frames]
frames[0].save(output_gif_path, save_all=True, append_images=frames[1:], duration=50, loop=0, optimize=True)


# === Release video handles ===
for caps in video_caps_by_skin.values():
    for cap in caps:
        cap.release()
