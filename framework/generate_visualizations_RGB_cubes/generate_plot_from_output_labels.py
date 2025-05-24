import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib
matplotlib.use('TkAgg')  # Use this for interactive plotting


file_path = "../output/out_labels_from_validation/200-epochs/bouncing"
out_path = "../output/out_labels_from_validation/200-epochs/bouncing_plots/"


def plot_array_labels(data, output_file):
    accuracy = np.mean(data) * 100  # Percentage of 1's in the array

    # Generate the plot
    fig, ax = plt.subplots(figsize=(12, 1))

    # Define colors
    colors = ['red', 'green']  # Red for 0 (bad), Green for 1 (good)
    color_map = [colors[int(val)] for val in data]

    # Create bar plot
    ax.bar(range(len(data)), np.full_like(data, 0.5), color=color_map, edgecolor='none', width=2.0)

    # Customize the plot
    ax.set_yticks([])  # Remove y-axis ticks
    ax.set_xticks([])  # Remove x-axis ticks
    ax.set_xlim(0, len(data))  # Set x-axis limit
    ax.set_title(output_file, fontsize=14)

    # Add accuracy annotation on the right side of the plot
    ax.text(len(data) + 2, 0.5, f"Accuracy: \n {accuracy:.2f}%", fontsize=20,
            color='black', ha='left', va='center', transform=ax.transData)

    # Adjust layout to avoid cutting off the text
    plt.tight_layout(rect=(0, 0, 0.97, 1))  # Leave space for the text on the right

    plt.savefig(out_path + output_file + ".png")
    plt.close()

    #plt.show()


if __name__ == '__main__':

    # Dictionary to store video paths and corresponding arrays
    video_data = {}

    # Read and process the file
    with open(file_path, "r") as file:
        current_path = None
        array_str = ""

        for line in file:
            line = line.strip()
            # If the line starts with a file path
            if line.startswith("../data/"):
                if current_path and array_str:  # Save the previous path and array
                    video_data[current_path] = np.array(eval(array_str))

                # Extract the file name
                current_path = os.path.splitext(os.path.basename(line.split(" ")[0]))[0]
                array_str = line.split(" ", 1)[1] if " " in line else ""
            else:
                # Continue building the array string
                array_str += line

            # Add the last entry
        if current_path and array_str:
            video_data[current_path] = np.array(eval(array_str))

    # Example: Print the first video path and its corresponding array
    for video_path, array in video_data.items():
        print(f"Video Path: {video_path}")
        print(f"Array: {array}")
        print("-" * 40)
        out_file = os.path.splitext(os.path.basename(video_path))[0]
        plot_array_labels(array, out_file)