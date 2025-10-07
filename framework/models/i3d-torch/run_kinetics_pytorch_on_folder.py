import csv
import os
import json
import torch
import urllib.request
import numpy as np
from numpy.f2py.auxfuncs import throw_error
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from torchvision.transforms import Compose, Lambda
from torchvision.transforms._transforms_video import CenterCropVideo, NormalizeVideo
from pytorchvideo.data.encoded_video import EncodedVideo
from pytorchvideo.transforms import ApplyTransformToKey, ShortSideScale, UniformTemporalSubsample
import torch.nn.functional as F
import warnings
import pandas as pd
import seaborn as sns
from transformers.models.hiera.convert_hiera_to_hf import get_labels_for_classifier

warnings.filterwarnings("ignore", category=UserWarning)

# TODO: Update these for different experiment results
model_name = "x3d_xs" # slowfast_r50, slow_r50, x3d_xs, x3d_s, mvit_base_16x4, c2d_r50
ROOT_FOLDER = r"C:\Users\Ana\Desktop\bias-action-recognition\framework\models\i3d-torch\data\run_results\top_20_kinetics_actions"
CAMERA_DISTANCES = ["camera_far", "camera_near"]
BACKGROUNDS = ["autumn_hockey", "konzerthaus", "stadium_01"]
MODELS = ["slowfast_r50", "slow_r50", "x3d_xs", "mvit_base_16x4"] #"x3d_s", "c2d_r50"
LABEL_URL = "https://dl.fbaipublicfiles.com/pyslowfast/dataset/class_names/kinetics_classnames.json"
LABEL_FILE = "kinetics_classnames.json"

BEDLAM_TO_DATASET_MATCHING_LABELS_FILE_PATH = r"D:\BEDLAM_videos_render\more_animations\config\label_matches.csv"


def get_labels_matching_dict(df):
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # Create the MATCHING_DICT
    matching_dict = {}

    for _, row in df.iterrows():
        bedlam_label = row.matched_bedlam_label.strip()
        real_label = row.real_dataset_label.strip()

        if bedlam_label not in matching_dict:
            matching_dict[bedlam_label] = []
        matching_dict[bedlam_label].append(real_label)

    return matching_dict


def load_classnames():
    if not os.path.exists(LABEL_FILE):
        urllib.request.urlretrieve(LABEL_URL, LABEL_FILE)
    with open(LABEL_FILE, "r") as f:
        return {v: k.replace('"', "") for k, v in json.load(f).items()}


def get_kinetics_to_custom():
    return {k: custom for custom, values in MATCHING_DICT.items() for k in values}


def get_transform(model_name):
    side_size, crop_size = 256, 256
    num_frames = 32
    alpha = 4

    if model_name == "slowfast_r50":
        class PackPathway(torch.nn.Module):
            def forward(self, frames: torch.Tensor):
                fast = frames
                slow = torch.index_select(
                    frames, 1,
                    torch.linspace(0, frames.shape[1] - 1, frames.shape[1] // alpha).long(),
                )
                return [slow, fast]

        return ApplyTransformToKey(
            key="video",
            transform=Compose([
                UniformTemporalSubsample(num_frames),
                Lambda(lambda x: x / 255.0),
                NormalizeVideo([0.45]*3, [0.225]*3),
                ShortSideScale(size=side_size),
                CenterCropVideo(crop_size),
                PackPathway()
            ])
        )

    if model_name == "mvit_base_16x4":
        def resize(frames, size=(224, 224)):
            frames = frames.permute(1, 0, 2, 3)
            frames = F.interpolate(frames, size=size, mode='bilinear', align_corners=False)
            return frames.permute(1, 0, 2, 3)

        return ApplyTransformToKey(
            key="video",
            transform=Compose([
                UniformTemporalSubsample(16),
                Lambda(lambda x: x / 255.0),
                Lambda(resize),
                NormalizeVideo([0.45]*3, [0.225]*3)
            ])
        )

    if model_name in ["slow_r50", "x3d_xs"]:
        return ApplyTransformToKey(
            key="video",
            transform=Compose([
                UniformTemporalSubsample(num_frames),
                Lambda(lambda x: x / 255.0),
                NormalizeVideo([0.45]*3, [0.225]*3),
                ShortSideScale(size=side_size),
                CenterCropVideo(crop_size),
            ])
        )

    raise ValueError(f"Unsupported model name '{model_name}'. Please add a transform pipeline for it.")


# Predict one video
def classify_video(model, transform, video_path, model_name, device, classnames, label_map, folder_label):
    try:
        video = EncodedVideo.from_path(video_path)
        video_data = transform(video.get_clip(0, 2.13))  # ~2.13s = 32f @ 15fps
        inputs = ([i.to(device)[None, ...] for i in video_data["video"]]
                  if model_name == "slowfast_r50" else video_data["video"].to(device)[None, ...])

        with torch.no_grad():
            probs = torch.nn.functional.softmax(model(inputs), dim=1)
            indices = torch.topk(probs, k=5).indices[0].cpu().numpy()
            top5_raw = [classnames[int(i)] for i in indices]
            top5_mapped = [label_map.get(lbl, "other") for lbl in top5_raw]
            mapped_top1 = top5_mapped[0]
            is_correct = mapped_top1 == folder_label
            return {
                "video": os.path.basename(video_path),
                "true_label": folder_label,
                "raw_prediction": top5_raw[0],
                "mapped_prediction": mapped_top1,
                "result": "correct" if is_correct else "incorrect",
                "top5": top5_mapped
            }

    except Exception as e:
        print(f"⚠️ Skipped {video_path}: {e}")
        return None


def evaluate_model(model_name):
    print(f"\n🔍 Evaluating model: {model_name}")
    output_path = os.path.join(MODEL_FOLDER, model_name)
    os.makedirs(output_path, exist_ok=True)

    classnames = load_classnames()
    label_map = get_kinetics_to_custom()
    transform = get_transform(model_name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Device:", device)
    model = torch.hub.load("facebookresearch/pytorchvideo", model=model_name, pretrained=True).to(device).eval()

    results = []
    stats = {"top1": 0, "top5": 0, "total": 0}
    class_counts = {}
    class_correct = {}

    for folder in sorted(os.listdir(VIDEO_FOLDER)):
        folder_path = os.path.join(VIDEO_FOLDER, folder)
        if not os.path.isdir(folder_path):
            continue
        if folder.lower() not in MATCHING_DICT:
            print(f"⚠️ No mapping for {folder}, skipping...")
            continue

        for file in os.listdir(folder_path):
            if not file.endswith(".mp4"):
                continue
            res = classify_video(
                model, transform,
                os.path.join(folder_path, file),
                model_name, device,
                classnames, label_map,
                folder.lower()
            )
            if not res:
                continue
            # print(res)
            print(file, res["mapped_prediction"])
            results.append(res)
            stats["total"] += 1
            class_counts[res["true_label"]] = class_counts.get(res["true_label"], 0) + 1
            if res["mapped_prediction"] == res["true_label"]:
                stats["top1"] += 1
                class_correct[res["true_label"]] = class_correct.get(res["true_label"], 0) + 1
            if res["true_label"] in res["top5"]:
                stats["top5"] += 1

            # print(stats)

    # Save CSV
    csv_path = os.path.join(output_path, "video_results.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["video", "true_label", "raw_prediction", "mapped_prediction", "result", "top5"])
        writer.writeheader()
        writer.writerows(results)
    print(f"📄 Saved video results: {csv_path}")

    # print(stats)

    # Save summary
    summary_path = os.path.join(output_path, "summary_metrics.txt")
    with open(summary_path, "w") as f:
        f.write("==================== RESULTS ====================\n")
        f.write(f"Total videos processed: {stats['total']}\n")
        f.write(f"Top-1 Accuracy: {stats['top1'] / stats['total']:.2%}\n")
        f.write(f"Top-5 Accuracy: {stats['top5'] / stats['total']:.2%}\n\n")
        f.write("Per-class Accuracy:\n")
        for label in sorted(class_counts):
            correct = class_correct.get(label, 0)
            total = class_counts[label]
            f.write(f"{label}: {correct / total:.2%} ({correct}/{total})\n")
    print(f"📄 Saved summary: {summary_path}")

    # Confusion matrix
    if results:
        y_true = [r["true_label"] for r in results]
        y_pred = [r["mapped_prediction"] for r in results]
        labels = list(MATCHING_DICT.keys()) + ["other"]
        # Compute confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=labels)

        # Plot heatmap-style confusion matrix
        plt.figure(figsize=(18, 18))
        ax = sns.heatmap(
            cm,
            xticklabels=labels,
            yticklabels=labels,
            cmap='viridis',  # or 'plasma', 'inferno', 'magma' for similar styles
            cbar=True,
            square=True,
            linewidths=0,
            linecolor='none'
        )

        # Ticks
        plt.xticks(rotation=90, fontsize=6)
        plt.yticks(rotation=0, fontsize=6)

        # Title and layout
        plt.title(f"Confusion Matrix - {model_name}", fontsize=14)
        plt.xlabel("Predicted Labels", fontsize=12)
        plt.ylabel("True Labels", fontsize=12)
        plt.tight_layout()

        # Save
        plt.savefig(os.path.join(output_path, "confusion_matrix.pdf"), bbox_inches='tight')
        plt.close()

        print(f"📊 Saved confusion matrix for {model_name}")



# Run all models
if __name__ == "__main__":
    MATCHING_DICT = get_labels_matching_dict(pd.read_csv(BEDLAM_TO_DATASET_MATCHING_LABELS_FILE_PATH))
    print(MATCHING_DICT)

    for camera_distance in CAMERA_DISTANCES:
        for background in BACKGROUNDS:
            MODEL_FOLDER = rf"{ROOT_FOLDER}\{camera_distance}\{background}"
            VIDEO_FOLDER = os.path.join(MODEL_FOLDER, "__generated_synthetic_videos")
            for model in MODELS:
                evaluate_model(model)