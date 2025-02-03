import os
import shutil

# Define the source directory containing multiple categories
folder_with_videos = "../data/RGB_cubes/90_scenes"  # Update with the actual folder path

test_dir = "test"
train_val_dir = "train-validation"

# Create test and train-validation directories
os.makedirs(test_dir, exist_ok=True)
os.makedirs(train_val_dir, exist_ok=True)

# Identify all matching category pairs (e.g., bouncing and bouncing_green)
categories = {}
for entry in os.listdir(folder_with_videos):
    full_path = os.path.join(folder_with_videos, entry)
    if os.path.isdir(full_path):
        base_name = entry.replace("_green", "")
        categories.setdefault(base_name, []).append(entry)

# Process each category pair
for base_name, subfolders in categories.items():
    if len(subfolders) == 2 and f"{base_name}_green" in subfolders and base_name in subfolders:
        dir_main = os.path.join(folder_with_videos, base_name)
        dir_green = os.path.join(folder_with_videos, f"{base_name}_green")
        test_main = os.path.join(test_dir, base_name)
        test_green = os.path.join(test_dir, f"{base_name}_green")
        train_val_main = os.path.join(train_val_dir, base_name)

        os.makedirs(test_main, exist_ok=True)
        os.makedirs(test_green, exist_ok=True)
        os.makedirs(train_val_main, exist_ok=True)

        processed_files = set()

        for filename in os.listdir(dir_green):
            file_green = os.path.join(dir_green, filename)
            file_main = os.path.join(dir_main, filename)

            if os.path.isfile(file_green):
                if os.path.isfile(file_main):
                    shutil.move(file_green, os.path.join(test_green, filename))
                    shutil.move(file_main, os.path.join(test_main, filename))
                    processed_files.add(filename)
                    print(f"Moved matching pair '{filename}' to test.")
                else:
                    raise FileNotFoundError(f"Error: Matching file '{filename}' not found in '{dir_main}'.")

        for filename in os.listdir(dir_main):
            if filename not in processed_files:
                file_main = os.path.join(dir_main, filename)
                if os.path.isfile(file_main):
                    shutil.move(file_main, os.path.join(train_val_main, filename))
                    print(f"Moved '{filename}' from {base_name} to train-validation.")

# Remove the parent folder once processing is complete
shutil.rmtree(folder_with_videos)
print(f"Removed source folder: {folder_with_videos}")