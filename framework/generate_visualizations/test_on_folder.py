from models import *
from dataset import *
from data.extract_frames import extract_frames
import argparse
import os
import glob
import tqdm
from torchvision.utils import make_grid
from PIL import Image, ImageDraw, ImageFont
import skvideo.io


def evaluate_video(video_path, ground_truth_label):
    print(f"Processing \"{video_path}\"!")
    frames = extract_frames(video_path)
    predictions = np.zeros(120)  ### TODO: Change this if different length of videos

    # Extract predictions
    for i, frame in enumerate(tqdm.tqdm(frames, desc="Processing frames")):
        image_tensor = Variable(transform(frame)).to(device)
        image_tensor = image_tensor.view(1, 1, *image_tensor.shape)

        # Get label prediction for frame
        with torch.no_grad():
            prediction = model(image_tensor)
            predicted_label = labels[prediction.argmax(1).item()]

        predictions[i] = predicted_label == ground_truth_label

    return predictions


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_folder_path", type=str, default="../data/cubes/bouncing", help="Path to folder of videos")
    parser.add_argument("--ground_truth_label", type=str, default="bouncing", help="Label of TRUTH!")
    parser.add_argument("--dataset_path", type=str, default="../data/cubes-frames", help="Path to cubes dataset")
    parser.add_argument("--image_dim", type=int, default=112, help="Height / width dimension")
    parser.add_argument("--channels", type=int, default=3, help="Number of image channels")
    parser.add_argument("--latent_dim", type=int, default=512, help="Dimensionality of the latent representation")
    parser.add_argument("--checkpoint_model", type=str, default="../model_checkpoints/ConvLSTM_95.pth", help="Optional path to checkpoint model")
    parser.add_argument("--output_file", type=str, default="output", help="File path to output.")
    opt = parser.parse_args()
    print(opt)

    assert opt.checkpoint_model, "Specify path to checkpoint model using arg. '--checkpoint_model'"

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_shape = (opt.channels, opt.image_dim, opt.image_dim)

    transform = transforms.Compose(
        [
            transforms.Resize(input_shape[-2:], Image.BICUBIC),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )

    labels = sorted(list(set(os.listdir(opt.dataset_path))))

    # Define model and load model checkpoint
    model = ConvLSTM(num_classes=len(labels), latent_dim=opt.latent_dim)
    model.to(device)
    model.load_state_dict(torch.load(opt.checkpoint_model), strict=False)
    model.eval()

    # Write the line to the output file
    with open(opt.output_file, 'w') as f:
        for filename in os.listdir(opt.video_folder_path):
            if filename.endswith(".mp4"):
                path = os.path.join(opt.video_folder_path, filename)
                predictions = evaluate_video(path, opt.ground_truth_label)

                # Format the numpy array as a string
                array_str = np.array2string(predictions, separator=',', precision=2, suppress_small=True)
                line = f"{path} {array_str}\n"
                f.write(line)

