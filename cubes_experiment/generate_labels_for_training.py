import os
import random
from collections import defaultdict
import argparse

# Argument parsing
parser = argparse.ArgumentParser(description="Process video categories into test and train-validation directories.")
parser.add_argument("folder_with_videos", type=str, help="Path to the folder containing video categories.")
parser.add_argument("model_path", type=str, help="Path to the folder model you want to train.")
parser.add_argument("train_percentage", type=int, default=80, help="Percentage of videos in the train folder " +
                                                                   "(rest 100-train will be in validation).")

args = parser.parse_args()

folder_with_videos = args.folder_with_videos  # Get the folder path from command-line argument
model_path = args.model_path
train_percentage = args.train_percentage     # Rest 100-train_percentage will be validation

folder_path = os.path.join(folder_with_videos, "train-validation")  # Input data for training
labels_folder = os.path.join(model_path, "labels_v2")   # TODO: Change this only if you want to combine multiple datasets or smth
labels_file = os.path.join(labels_folder, "classInd.txt")
file_paths_with_labels = os.path.join(labels_folder, "file_paths_with_labels.txt")

train_output_filepaths = os.path.join(labels_folder, "trainlist01.txt")
validation_output_filepaths = os.path.join(labels_folder, "validationlist01.txt")


def generate_labels(folder_path, output_file):
    """
    Generates a text file with numbered labels based on subfolder names,
    ignoring subfolders that contain '_green'.

    Args:
        folder_path (str): Path to the main folder containing subfolders.
        output_file (str): Path to save the labels text file.
    """
    try:
        # Get all subfolder names in the main folder, excluding those with '_green'
        subfolders = sorted(
            [name for name in os.listdir(folder_path)
             if os.path.isdir(os.path.join(folder_path, name)) and "_green" not in name]
        )

        # Create a labels file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as file:
            for index, folder_name in enumerate(subfolders, start=1):
                file.write(f"{index} {folder_name}\n")

        print(f"Labels file created successfully at: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


def generate_file_paths_with_labels(folder_path, labels_file, output_file):
    """
    Generates a text file with file paths (using forward slashes) and their corresponding labels
    based on a labels.txt file.

    Args:
        folder_path (str): Path to the main folder containing subfolders.
        labels_file (str): Path to the labels.txt file.
        output_file (str): Path to save the file paths with labels.
    """
    try:
        # Read labels from the labels file
        labels = {}
        with open(labels_file, "r") as file:
            for line in file:
                label, folder_name = line.strip().split(" ", 1)
                labels[folder_name] = int(label)

        # Create the output file
        with open(output_file, "w") as out_file:
            for folder_name, label in labels.items():
                folder_path_full = os.path.join(folder_path, folder_name)
                if os.path.isdir(folder_path_full):
                    # List all video files in the folder
                    for file_name in os.listdir(folder_path_full):
                        # Create file path with forward slashes
                        file_path = os.path.join(folder_name, file_name).replace("\\", "/")
                        # file_path_without_extension = os.path.splitext(file_path)[0]    # Removes the .mp4
                        out_file.write(f"{file_path} {label}\n")

        print(f"File paths with labels saved successfully at: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


def write_to_file(output_path, list_to_write):
    """
    Writes a list of file paths and labels at the specified output path.
    :param output_path: Where to write it (e.g. "labels/train.txt").
    :param list_to_write: List of pairs of file paths and labels of the videos [(file_path, label), ..]
    """
    with open(output_path, "w") as train_file:
        for file_path, label in list_to_write:
            train_file.write(f"{file_path} {label}\n")


def split_videos(input_file, train_output, val_output, train_percentage):
    """
    Splits videos into train and validation files with equal representation from each category.

    Args:
        input_file (str): Path to the file containing video paths and labels.
        train_output (str): Path to save the train split file.
        val_output (str): Path to save the validation split file.
        train_percentage (float): Percentage of videos to use for training.
        val_percentage (float): Percentage of videos to use for validation.
    """
    try:
        # Read video file paths and group them by category
        categories = defaultdict(list)
        with open(input_file, "r") as file:
            for line in file:
                file_path, label = line.strip().rsplit(" ", 1)
                # Extract category from file path (e.g., 2C1R1B)
                category = file_path.split("_")[1]
                categories[category].append((file_path, label))

        # Initialize train, validation, and test splits
        train_split = []
        val_split = []

        # Process each category
        for category, videos in categories.items():
            total_videos = len(videos)
            train_count = max(1, int((train_percentage / 100) * total_videos))  # At least 1 for train
            val_count = total_videos - train_count

            # Randomly shuffle and split videos
            random.shuffle(videos)
            train_split.extend(videos[:train_count])
            val_split.extend(videos[train_count:train_count + val_count])

        # Sort splits before writing to file
        train_split = sorted(train_split, key=lambda x: x[0])  # Sort by file path
        val_split = sorted(val_split, key=lambda x: x[0])  # Sort by file path

        write_to_file(train_output, train_split)
        write_to_file(val_output, val_split)

        print(f"Train, validation, and test splits created successfully:")
        print(f"Train split: {train_output}")
        print(f"Validation split: {val_output}")

    except Exception as e:
        print(f"An error occurred: {e}")


generate_labels(folder_path, labels_file) # Makes classInd.txt file
generate_file_paths_with_labels(folder_path, labels_file, file_paths_with_labels) # Makes file_paths_with_labels.txt file
split_videos(file_paths_with_labels, train_output_filepaths, validation_output_filepaths, train_percentage)


