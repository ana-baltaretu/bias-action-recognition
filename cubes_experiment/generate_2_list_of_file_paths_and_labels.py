import os


def generate_file_paths_with_labels(folder_path="animation_output/actual_output", # TODO: Update this with your actual folder path
                                    labels_file="labels/classInd.txt",
                                    output_file="labels/file_paths_with_labels.txt"):
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


generate_file_paths_with_labels()
