import os
import matplotlib.pyplot as plt
import numpy as np
import mxnet as mx
from mxnet import gluon, nd, image
from mxnet.gluon.data.vision import transforms
from gluoncv.data.transforms import video
from gluoncv import utils
from gluoncv.model_zoo import get_model
from gluoncv.utils.filesystem import try_import_decord

decord = try_import_decord()

model_name = 'i3d_inceptionv1_kinetics400'
net = get_model(model_name, nclass=400, pretrained=True)
print('%s model is successfully loaded.' % model_name)

transform_fn = video.VideoGroupValTransform(size=224, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

# Mapping from folder names to Kinetics classes
matching_dict = {
    "cartwheel": ["cartwheeling"],
    "walking": ["walking the dog", "walking with cane", "walking on treadmill"],
    "jumping": ["jumping jacks", "jumping into pool", "jumping on trampoline"],
    "running": ["running on treadmill", "sprinting", "jogging"],
    # TODO: Add more mappings if needed
}

total_videos = 0
top1_correct = 0
top5_correct = 0


def classify_video(video_path, expected_label_options):
    """Classify a video and update top-1 and top-5 accuracy metrics."""
    global top1_correct, top5_correct, total_videos

    vr = decord.VideoReader(video_path)
    frame_id_list = range(0, 64, 2)
    video_data = vr.get_batch(frame_id_list).asnumpy()
    clip_input = [video_data[vid, :, :, :] for vid, _ in enumerate(frame_id_list)]

    clip_input = transform_fn(clip_input)
    clip_input = np.stack(clip_input, axis=0)
    clip_input = clip_input.reshape((-1,) + (32, 3, 224, 224))
    clip_input = np.transpose(clip_input, (0, 2, 1, 3, 4))

    pred = net(nd.array(clip_input))
    classes = net.classes
    topK = 5
    ind = nd.topk(pred, k=topK)[0].astype('int')

    top5_labels = [classes[ind[i].asscalar()] for i in range(topK)]
    top1_label = top5_labels[0]

    print(f"{os.path.basename(video_path)}: {top1_label}")

    total_videos += 1
    if top1_label in expected_label_options:
        top1_correct += 1
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

    # Final metrics
    print("\n==================== RESULTS ====================")
    print(f"Total videos processed: {total_videos}")
    print(f"Top-1 Accuracy: {top1_correct / total_videos:.2%} ({top1_correct}/{total_videos})")
    print(f"Top-5 Accuracy: {top5_correct / total_videos:.2%} ({top5_correct}/{total_videos})")



# Set your input path here
parent_folder = "C:/Users/anaba/OneDrive/Desktop/Master Thesis/bias-action-recognition/bedlam/my_videos/attempt2/initial/"
process_all_folders(parent_folder)
