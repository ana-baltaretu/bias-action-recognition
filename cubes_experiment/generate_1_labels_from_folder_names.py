import os


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
        with open(output_file, "w") as file:
            for index, folder_name in enumerate(subfolders, start=1):
                file.write(f"{index} {folder_name}\n")

        print(f"Labels file created successfully at: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


folder_path = "animation_output/actual_output"  # TODO: Update this with your actual folder path
output_file = "labels/classInd.txt"

generate_labels(folder_path, output_file)
