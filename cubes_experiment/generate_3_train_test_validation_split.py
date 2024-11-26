import os
import random
from collections import defaultdict


def write_to_file(output_path, list_to_write):
    """
    Writes a list of file paths and labels at the specified output path.
    :param output_path: Where to write it (e.g. "labels/train.txt").
    :param list_to_write: List of pairs of file paths and labels of the videos [(file_path, label), ..]
    """
    with open(output_path, "w") as train_file:
        for file_path, label in list_to_write:
            train_file.write(f"{file_path} {label}\n")


def split_videos(input_file="labels/file_paths_with_labels.txt",
                 train_output="labels/trainlist01.txt",
                 test_output="labels/testlist01.txt",
                 val_output="labels/validationlist01.txt",
                 train_percentage=60,
                 val_percentage=10):
    """
    Splits videos into train, validation, and test files with equal representation from each category.

    Args:
        input_file (str): Path to the file containing video paths and labels.
        train_output (str): Path to save the train split file.
        test_output (str): Path to save the test split file.
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
        test_split = []

        # Process each category
        for category, videos in categories.items():
            total_videos = len(videos)
            train_count = max(1, int((train_percentage / 100) * total_videos))  # At least 1 for train
            val_count = max(1, int((val_percentage / 100) * total_videos))  # At least 1 for validation
            test_count = total_videos - train_count - val_count

            # Ensure test_count is at least 0
            if test_count < 0:
                val_count += test_count
                test_count = 0

            # Randomly shuffle and split videos
            random.shuffle(videos)
            train_split.extend(videos[:train_count])
            val_split.extend(videos[train_count:train_count + val_count])
            test_split.extend(videos[train_count + val_count:])

        # Sort splits before writing to file
        train_split = sorted(train_split, key=lambda x: x[0])  # Sort by file path
        val_split = sorted(val_split, key=lambda x: x[0])  # Sort by file path
        test_split = sorted(test_split, key=lambda x: x[0])  # Sort by file path

        write_to_file(train_output, train_split)
        write_to_file(val_output, val_split)
        write_to_file(test_output, test_split)

        print(f"Train, validation, and test splits created successfully:")
        print(f"Train split: {train_output}")
        print(f"Validation split: {val_output}")
        print(f"Test split: {test_output}")

    except Exception as e:
        print(f"An error occurred: {e}")


split_videos()
