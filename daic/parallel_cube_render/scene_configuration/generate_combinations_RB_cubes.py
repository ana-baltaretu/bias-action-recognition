max_cubes=3

# Write points to file
output_file = "amount_of_Red_Blue_cubes"
with open(output_file, "w") as file:
    file.write(f"Red\tBlue\n")
    for cubes in range(1, max_cubes+1):
        for red in range(cubes+1):
            blue = cubes - red
            file.write(f"{red}\t{blue}\n")

