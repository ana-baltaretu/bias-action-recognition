# Output file name
output_file = "../scene_info.config"

# Import necessary libraries
import numpy as np

# File paths for input data
camera_positions_file = "camera_positions"
red_blue_file = "amount_of_Red_Blue_cubes"

# Read data from the provided file paths
def read_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    return [list(map(float, line.strip().split())) for line in lines[1:]]

camera_positions = read_file(camera_positions_file)
red_blue = read_file(red_blue_file)

# Generate random seeds for each red-blue combination
rng = np.random.default_rng()
seeds = rng.integers(0, 10000, size=len(red_blue))

# Combine the data
combined_data = []
index = 1
for seed, (red, blue) in zip(seeds, red_blue):
    for camera_x, camera_y, camera_z in camera_positions:
        combined_data.append(
            f"{index}\t\t{camera_x}\t\t{camera_y}\t\t{camera_z}\t\t{int(red)}\t\t\t{int(blue)}\t\t\t{seed}\n"
        )
        index += 1

# Write the combined data to a new file
with open(output_file, "w") as file:
    file.write(
        "i\t\tcamera_x\tcamera_y\tcamera_z\tcubes_red\tcubes_blue\tcubes_random_position_seed\n"
    )
    file.writelines(combined_data)

print(f"Combined data written to {output_file}")
