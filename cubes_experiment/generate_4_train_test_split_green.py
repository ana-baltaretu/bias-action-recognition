import random
from collections import defaultdict


def adjust_test_split(test_file="labels/testlist01.txt",
                      output_file="test_green.txt",
                      green_percentage=20):
    """
    Adjusts the test split to include a specified percentage of green videos.

    Args:
        test_file (str): Path to the test split file.
        output_file (str): Path to save the adjusted test split.
        green_percentage (float): Percentage of green videos to include in the test split.
    """
    try:
        # Read test file paths and group by green/non-green categories
        green_videos = []
        non_green_videos = []

        with open(test_file, "r") as file:
            for line in file:
                file_path, label = line.strip().rsplit(" ", 1)
                # Check if the folder name contains "green"
                if "_green" in file_path:
                    green_videos.append((file_path, label))
                else:
                    non_green_videos.append((file_path, label))

        # Calculate desired number of green videos in the test split
        total_test_size = len(green_videos) + len(non_green_videos)
        desired_green_count = int((green_percentage / 100) * total_test_size)
        current_green_count = len(green_videos)

        if current_green_count > desired_green_count:
            # Too many green videos: remove excess from green_videos
            random.shuffle(green_videos)
            excess_count = current_green_count - desired_green_count
            non_green_videos.extend(green_videos[-excess_count:])
            green_videos = green_videos[:-excess_count]
        elif current_green_count < desired_green_count:
            # Too few green videos: add more from non-green if possible
            available_to_add = len(non_green_videos)
            additional_needed = min(desired_green_count - current_green_count, available_to_add)
            if additional_needed > 0:
                additional_videos = random.sample(non_green_videos, additional_needed)
                green_videos.extend(additional_videos)
                non_green_videos = [v for v in non_green_videos if v not in additional_videos]

        # Combine adjusted green and non-green videos
        adjusted_test_split = sorted(green_videos + non_green_videos, key=lambda x: x[0])

        # Write the adjusted test split to the output file
        with open(output_file, "w") as out_file:
            for file_path, label in adjusted_test_split:
                out_file.write(f"{file_path} {label}\n")

        print(f"Test split adjusted successfully. Saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")


adjust_test_split()
