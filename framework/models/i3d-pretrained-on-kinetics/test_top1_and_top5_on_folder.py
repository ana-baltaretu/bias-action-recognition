import os
import numpy as np
import mxnet as mx
from mxnet import nd
from gluoncv.data.transforms import video
from gluoncv.model_zoo import get_model
from gluoncv.utils.filesystem import try_import_decord

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# Load video reader
decord = try_import_decord()

# Load pre-trained model
model_name = 'i3d_inceptionv1_kinetics400'
net = get_model(model_name, nclass=400, pretrained=True)
print('%s model is successfully loaded.' % model_name)

# Transform for evaluation
transform_fn = video.VideoGroupValTransform(
    size=224,
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225]
)

# Folder name → Kinetics labels mapping
matching_dict = {
    "cartwheel": ["cartwheeling"],
    "walking": ["walking the dog", "walking with cane", "walking on treadmill"],
    "jumping": ["jumping jacks", "jumping into pool", "jumping on trampoline"],
    "running": ["running on treadmill", "sprinting", "jogging"],
    # Add more as needed
}

# Metrics
total_videos = 0
top1_correct = 0
top5_correct = 0
true_labels = []
pred_labels = []
per_class_counts = {}
per_class_correct = {}

def classify_video(video_path, expected_label_options):
    global total_videos, top1_correct, top5_correct

    vr = decord.VideoReader(video_path)
    frame_id_list = range(0, 64, 2)
    video_data = vr.get_batch(frame_id_list).asnumpy()
    clip_input = [video_data[vid] for vid in range(len(frame_id_list))]

    # Preprocessing
    clip_input = transform_fn(clip_input)
    clip_input = np.stack(clip_input, axis=0)
    clip_input = clip_input.reshape((-1,) + (32, 3, 224, 224))
    clip_input = np.transpose(clip_input, (0, 2, 1, 3, 4))

    # Inference
    pred = net(nd.array(clip_input))
    classes = net.classes
    topK = 5
    ind = nd.topk(pred, k=topK)[0].astype('int')
    top5_labels = [classes[int(ind[i].asscalar())] for i in range(topK)]
    top1_label = top5_labels[0]

    # Output only video name and top-1 prediction
    print(f"{os.path.basename(video_path)}: {top1_label}")

    # Update metrics
    true_label = expected_label_options[0]  # use canonical label for confusion matrix
    total_videos += 1
    true_labels.append(true_label)
    pred_labels.append(top1_label)

    per_class_counts[true_label] = per_class_counts.get(true_label, 0) + 1
    if top1_label in expected_label_options:
        top1_correct += 1
        per_class_correct[true_label] = per_class_correct.get(true_label, 0) + 1
    if any(label in expected_label_options for label in top5_labels):
        top5_correct += 1

def process_all_folders(parent_folder):
    for action_folder in sorted(os.listdir(parent_folder)):
        if "__" in action_folder:
            continue

        action_path = os.path.join(parent_folder, action_folder)
        if not os.path.isdir(action_path):
            continue

        expected_labels = matching_dict.get(action_folder.lower(), [])
        if not expected_labels:
            print(f"⚠️  Skipping '{action_folder}': no matching label found in dictionary.")
            continue

        for file_name in os.listdir(action_path):
            if file_name.endswith(".mp4"):
                video_path = os.path.join(action_path, file_name)
                classify_video(video_path, expected_labels)

    # Final results
    print("\n==================== RESULTS ====================")
    print(f"Total videos processed: {total_videos}")
    print(f"Top-1 Accuracy: {top1_correct / total_videos:.2%} ({top1_correct}/{total_videos})")
    print(f"Top-5 Accuracy: {top5_correct / total_videos:.2%} ({top5_correct}/{total_videos})")

    print("\nPer-action Top-1 Accuracy:")
    for label in sorted(per_class_counts):
        correct = per_class_correct.get(label, 0)
        total = per_class_counts[label]
        print(f"{label}: {correct / total:.2%} ({correct}/{total})")

    # Confusion matrix
    print("\nSaving confusion matrix...")
    if true_labels and pred_labels:
        labels_to_show = sorted(set(true_labels + pred_labels))
        cm = confusion_matrix(true_labels, pred_labels, labels=labels_to_show)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels_to_show)
        disp.plot(include_values=True, xticks_rotation=45, cmap='Blues')
        plt.title("Top-1 Prediction Confusion Matrix")
        plt.tight_layout()
        plt.savefig("confusion_matrix.pdf")
        print("✅ Confusion matrix saved as 'confusion_matrix.pdf'")

# Run the processing
parent_folder = "C:/Users/anaba/OneDrive/Desktop/Master Thesis/bias-action-recognition/bedlam/my_videos/attempt2/quick_test/"
process_all_folders(parent_folder)