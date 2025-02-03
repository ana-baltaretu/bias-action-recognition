import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib
matplotlib.use('TkAgg')  # Use this for interactive plotting


results_path = "../output/out_labels_from_validation/200-epochs/bouncing"
#out_path = "../output/out_labels_from_validation/200-epochs/orbiting_plots/"

dataset_split_paths = {
    "train": "../data/cubesTrainTestlist/trainlist01.txt",
    "test": "../data/cubesTrainTestlist/testlist01.txt",
    "validation": "../data/cubesTrainTestlist/validationlist01.txt",
    "green": "../data/cubesTrainTestlist/greenlist01.txt"
}


def read_results(path):
    # Dictionary to store video paths and corresponding arrays
    results_data = {}

    # Read and process the file
    with open(path, "r") as file:
        current_path = None
        array_str = ""

        for line in file:
            line = line.strip()

            # If the line starts with a file path
            if line.startswith("data/"):
                if current_path and array_str:  # Save the previous path and array
                    results_data[current_path] = np.array(eval(array_str))

                # Extract the file name
                current_path = os.path.splitext(os.path.basename(line.split(" ")[0]))[0]
                array_str = line.split(" ", 1)[1] if " " in line else ""
            else:
                # Continue building the array string
                array_str += line

            # Add the last entry
        if current_path and array_str:
            results_data[current_path] = np.array(eval(array_str))

    return results_data


def calculate_accuracy_per_split(name_of_split, file_path):
    print("Calculating results for:", name_of_split)

    averages = np.array([])
    item_counter = 0
    with open(file_path, "r") as file:
        # Parse the data line by line
        for line in file:
            file_path, label_type = line.strip().rsplit(" ", 1)
            label_type = int(label_type)  # Convert label to integer
            file_path = os.path.splitext(os.path.basename(line.split(" ")[0]))[0]
            if label_type == 1:     ### Bouncing
                #print(f"File Path: {file_path}, Label Type: {label_type}")
                #print(output_data[file_path])
                averages = np.append(averages, np.array(output_data[file_path]))
                item_counter += 1

    mean = np.mean(averages)
    print(f"Averages for {name_of_split}: {averages}")
    print(f"Mean for {name_of_split}: {mean}")

    return item_counter, mean


if __name__ == '__main__':

    output_data = read_results(results_path)

    average_accuracies = {}
    for key, path in dataset_split_paths.items():
        item_counter, mean = calculate_accuracy_per_split(key, path)
        average_accuracies[key + "-" + str(item_counter) + " samples"] = mean

    plt.figure(figsize=(8, 5))
    bars = plt.bar(average_accuracies.keys(), average_accuracies.values())

    # Add numerical values on top of the bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.2f}', ha='center', va='bottom')

    plt.title('Average Accuracy by Dataset Split for \"Bouncing\" action')
    plt.ylabel('Average Accuracy')
    plt.ylim(0, 1.2)  # To better emphasize the range of accuracy (0 to 1)
    plt.xlabel('Dataset Split')
    plt.show()

    # # Example: Print the first video path and its corresponding array
    # for video_path, array in output_data.items():
    #     print(f"Video Path: {video_path}")
    #     print(f"Array: {array}")
    #     print("-" * 40)
    #     out_file = os.path.splitext(os.path.basename(video_path))[0]
    #     # plot_array_labels(array, out_file)