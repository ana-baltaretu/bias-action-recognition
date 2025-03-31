import csv
import os
import json
import torch
import urllib.request
import numpy as np
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from torchvision.transforms import Compose, Lambda
from torchvision.transforms._transforms_video import CenterCropVideo, NormalizeVideo
from pytorchvideo.data.encoded_video import EncodedVideo
from pytorchvideo.transforms import ApplyTransformToKey, ShortSideScale, UniformTemporalSubsample
import torch.nn.functional as F
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# TODO: Update these for different experiment results
folder_name = "initial" # initial OR modified
background_name = "wide_street_01" # autumn_park, konzerthaus, wide_street_01
model_name = "slow_r50" # slowfast_r50, slow_r50, x3d_xs, x3d_s, mvit_base_16x4, c2d_r50

# Folder name → Kinetics labels mapping
matching_dict = {
    "cartwheel": ["cartwheeling"],
    "walk": ["walking the dog", "walking with cane", "walking on treadmill"],
    "jump": ["jumping jacks", "jumping into pool", "jumping on trampoline", "jumpstyle dancing"],
    "run": ["running on treadmill", "sprinting", "jogging"],
    # TODO: Add more as needed
}

selected_background_and_distribution = rf"attempt2\{background_name}"
root_to_data = r"C:\Users\Ana\Desktop\bias-action-recognition\framework\models\i3d-torch\results_on_kinetics"
parent_folder = rf"{root_to_data}\{selected_background_and_distribution}\__generated_synthetic_videos\{folder_name}"

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load model
model = torch.hub.load("facebookresearch/pytorchvideo", model=model_name, pretrained=True)
model = model.to(device).eval()

# Download class names
label_url = "https://dl.fbaipublicfiles.com/pyslowfast/dataset/class_names/kinetics_classnames.json"
label_file = "kinetics_classnames.json"
if not os.path.exists(label_file):
    urllib.request.urlretrieve(label_url, label_file)
with open(label_file, "r") as f:
    kinetics_classnames = json.load(f)
id_to_classname = {v: k.replace('"', "") for k, v in kinetics_classnames.items()}

# Reverse mapping: Kinetics label → custom label
kinetics_to_custom = {}
for custom_label, kinetics_labels in matching_dict.items():
    for k in kinetics_labels:
        kinetics_to_custom[k] = custom_label

# Transform
side_size = 256
crop_size = 256
num_frames = 32
sampling_rate = 2
fps = 30
alpha = 4
clip_duration = (num_frames * sampling_rate) / fps

if model_name=="slowfast_r50":
    class PackPathway(torch.nn.Module):
        def forward(self, frames: torch.Tensor):
            fast = frames
            slow = torch.index_select(
                frames,
                1,
                torch.linspace(0, frames.shape[1] - 1, frames.shape[1] // alpha).long(),
            )
            return [slow, fast]

    transform = ApplyTransformToKey(
        key="video",
        transform=Compose([
            UniformTemporalSubsample(num_frames),
            Lambda(lambda x: x / 255.0),
            NormalizeVideo([0.45, 0.45, 0.45], [0.225, 0.225, 0.225]),
            ShortSideScale(size=side_size),
            CenterCropVideo(crop_size),
            PackPathway()
        ])
    )

elif model_name=="mvit_base_16x4":
    def resize_video(frames, size=(224, 224)):
        # frames: (C, T, H, W) → need to reshape to (1, C, T, H, W), then permute to (1, T, C, H, W)
        frames = frames.permute(1, 0, 2, 3)  # (T, C, H, W)
        frames = F.interpolate(frames, size=size, mode='bilinear', align_corners=False)
        frames = frames.permute(1, 0, 2, 3)  # back to (C, T, H, W)
        return frames

    transform = ApplyTransformToKey(
        key="video",
        transform=Compose([
            UniformTemporalSubsample(16),  # 16 frames for MViT
            Lambda(lambda x: x / 255.0),
            Lambda(resize_video),          # Resize to 224x224
            NormalizeVideo([0.45, 0.45, 0.45], [0.225, 0.225, 0.225]),
        ])
    )

else:  # slow_r50, x3d_xs
    transform = ApplyTransformToKey(
        key="video",
        transform=Compose([
            UniformTemporalSubsample(num_frames),
            Lambda(lambda x: x / 255.0),
            NormalizeVideo([0.45, 0.45, 0.45], [0.225, 0.225, 0.225]),
            ShortSideScale(size=side_size),
            CenterCropVideo(crop_size),
        ])
    )

# Metrics
top1_correct = 0
top5_correct = 0
total_videos = 0
true_labels = []
pred_labels = []
per_class_counts = {}
per_class_correct = {}

video_results = []

# Predict one video
def classify_video(video_path, folder_label, expected_label_options):
    global top1_correct, top5_correct, total_videos

    try:
        video = EncodedVideo.from_path(video_path)
        video_data = video.get_clip(start_sec=0, end_sec=clip_duration)
        video_data = transform(video_data)
        #

        if model_name=="slowfast_r50":
            inputs = [i.to(device)[None, ...] for i in video_data["video"]]
        else:
            inputs = video_data["video"].to(device)[None, ...]  # Remove list wrapping for all other models

        with torch.no_grad():
            preds = model(inputs)
            probs = torch.nn.functional.softmax(preds, dim=1)
            top5 = torch.topk(probs, k=5)
            indices = top5.indices[0].cpu().numpy()
            top5_names = [id_to_classname[int(i)] for i in indices]
            top1_name_raw = top5_names[0]

            # Map predicted label to your custom label space
            top1_name = kinetics_to_custom.get(top1_name_raw, "other")
            top5_mapped = [kinetics_to_custom.get(name, "other") for name in top5_names]

            filename = os.path.basename(video_path)
            is_correct = "correct" if top1_name == folder_label else "incorrect"
            print(f"{filename} → {top1_name_raw} mapped to {top1_name} → {is_correct}")

            video_results.append({
                "video": filename,
                "true_label": folder_label,
                "raw_prediction": top1_name_raw,
                "mapped_prediction": top1_name,
                "result": is_correct
            })

            # Track for confusion matrix
            true_labels.append(folder_label)
            pred_labels.append(top1_name)

            total_videos += 1
            per_class_counts[folder_label] = per_class_counts.get(folder_label, 0) + 1

            if top1_name == folder_label:
                top1_correct += 1
                per_class_correct[folder_label] = per_class_correct.get(folder_label, 0) + 1
            if folder_label in top5_mapped:
                top5_correct += 1

    except Exception as e:
        print(f"⚠️ Skipped {video_path} due to error: {e}")


# Process folder
def process_all_folders(parent_folder):
    for action_folder in sorted(os.listdir(parent_folder)):
        action_path = os.path.join(parent_folder, action_folder)
        if not os.path.isdir(action_path):
            continue

        expected_labels = matching_dict.get(action_folder.lower(), [])
        if not expected_labels:
            print(f"⚠️ Skipping '{action_folder}': no mapping found.")
            continue

        for file in os.listdir(action_path):
            if file.endswith(".mp4"):
                video_path = os.path.join(action_path, file)
                classify_video(video_path, action_folder.lower(), expected_labels)

    # Save summary metrics to file
    summary_path = f"{folder_name}_summary_metrics.txt"
    with open(summary_path, "w") as f:
        f.write("==================== RESULTS ====================\n")
        f.write(f"Total videos processed: {total_videos}\n")
        f.write(f"Top-1 Accuracy: {top1_correct / total_videos:.2%} ({top1_correct}/{total_videos})\n")
        f.write(f"Top-5 Accuracy: {top5_correct / total_videos:.2%} ({top5_correct}/{total_videos})\n\n")

        f.write("Per-class Top-1 Accuracy:\n")
        for label in sorted(per_class_counts):
            correct = per_class_correct.get(label, 0)
            total = per_class_counts[label]
            f.write(f"{label}: {correct / total:.2%} ({correct}/{total})\n")

    print(f"📝 Saved summary metrics to '{summary_path}'")

    # Confusion matrix
    print("\nSaving confusion matrix...")
    if true_labels and pred_labels:
        custom_labels = list(matching_dict.keys()) + ["other"]
        cm = confusion_matrix(true_labels, pred_labels, labels=custom_labels)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=custom_labels)
        disp.plot(include_values=True, xticks_rotation=45, cmap='Blues')
        plt.title("Top-1 Prediction Confusion Matrix")
        plt.tight_layout()
        plt.savefig(f"confusion_matrix_{folder_name}.pdf")
        print(f"✅ Confusion matrix saved as 'confusion_matrix_{folder_name}.pdf'")


    with open(f"{folder_name}_video_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["video", "true_label", "raw_prediction", "mapped_prediction", "result"])
        writer.writeheader()
        writer.writerows(video_results)

    print(f"📝 Saved per-video results to '{folder_name}_video_results.csv'")

# Run it!
process_all_folders(parent_folder)
