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

# Import decord for video reading
decord = try_import_decord()

# Define the model once
model_name = 'i3d_inceptionv1_kinetics400'
net = get_model(model_name, nclass=400, pretrained=True)
print('%s model is successfully loaded.' % model_name)

# Transformation function
transform_fn = video.VideoGroupValTransform(size=224, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])


def classify_video(video_path):
    """Process and classify a single video."""
    vr = decord.VideoReader(video_path)
    frame_id_list = range(0, 64, 2)
    video_data = vr.get_batch(frame_id_list).asnumpy()
    clip_input = [video_data[vid, :, :, :] for vid, _ in enumerate(frame_id_list)]

    # Apply transformations
    clip_input = transform_fn(clip_input)
    clip_input = np.stack(clip_input, axis=0)
    clip_input = clip_input.reshape((-1,) + (32, 3, 224, 224))
    clip_input = np.transpose(clip_input, (0, 2, 1, 3, 4))

    # Run inference
    pred = net(nd.array(clip_input))
    classes = net.classes
    topK = 5
    ind = nd.topk(pred, k=topK)[0].astype('int')

    # Extract relative path
    last_part = "/".join(video_path.split("/")[-1:])
    print(f'The input ``{last_part}`` video clip is classified to be')
    print("```")
    for i in range(topK):
        print('[%s], with probability %.3f.' %
              (classes[ind[i].asscalar()], nd.softmax(pred)[0][ind[i]].asscalar()))
    print("```")


def process_all_folders(parent_folder):
    """Iterate through all action folders inside the parent folder and classify videos."""
    for action_folder in sorted(os.listdir(parent_folder)):  # Sort to process consistently
        if "__" not in action_folder:
            action_path = os.path.join(parent_folder, action_folder)

            # Ensure it's a directory (not a file)
            if os.path.isdir(action_path):
                print(f"\n<details> <summary>{action_folder}</summary>\n")  # Print action name

                # Process videos inside the action folder
                for i, file_name in enumerate(os.listdir(action_path)):
                    if file_name.endswith(".mp4"):  # Process only mp4 files
                        video_path = os.path.join(action_path, file_name)
                        #print(f"{i + 1}. Processing {file_name}...")
                        classify_video(video_path)

                print("</details>\n")
        else:
            print(f"Not processing {action_folder} folder\n\n")


# Define the parent folder containing all action subfolders
parent_folder = "../../../bedlam/be_imagedata_download/categorized/" \
                "20221011_1_250_batch01hand_closeup_suburb_d_mp4"

# Process all folders inside the parent folder
process_all_folders(parent_folder)
