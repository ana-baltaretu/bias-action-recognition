import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os


def read_results(path):
    # Dictionary to store video paths and corresponding arrays
    results_data = {}

    if not os.path.exists(path):
        raise IOError(f"File not found at {path}")

    # Read and process the file
    with open(path, "r") as file:
        current_path = None
        array_str = ""

        for line in file:
            line = line.strip()

            # If the line has the name of the file
            if "data/" in line:
                if current_path and array_str:      # Save the previous path and array
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


if __name__ == '__main__':
    file_path = "../models/action-recognition-by-eriklindernoren/output/test_folder/orbiting"
    dict_of_results = read_results(file_path)
    green_results_per_frame = []
    non_green_results_per_frame = []
    green_results_per_video = []
    non_green_results_per_video = []
    for key, val in dict_of_results.items():
        avg_accuracy = sum(val) / len(val) * 100  # Compute average accuracy
        correctly_classified = avg_accuracy > 50

        if "_green" in key:
            green_results_per_frame.append(avg_accuracy)
            green_results_per_video.append(correctly_classified)
        else:
            non_green_results_per_frame.append(avg_accuracy)
            non_green_results_per_video.append(correctly_classified)

    print("----------- RESULTS PER FRAME -----------")

    # Per frame accuracy per video (capped to 2 decimal places)
    print("Green results:", [round(res, 2) for res in green_results_per_frame])
    print("Non-Green results:", [round(res, 2) for res in non_green_results_per_frame])

    # Per frame accuracy averages (capped to 2 decimal places)
    print("Green averages:", round(np.average(green_results_per_frame), 2))
    print("Non-Green averages:", round(np.average(non_green_results_per_frame), 2))

    print("----------- RESULTS PER VIDEO -----------")
    print("Green VIDEO averages:", round(np.average(green_results_per_video), 2))
    print("Non-Green VIDEO averages:", round(np.average(non_green_results_per_video), 2))