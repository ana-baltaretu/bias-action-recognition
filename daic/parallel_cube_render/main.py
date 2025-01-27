import sys
import os
import random

script_dir = os.path.dirname(__file__)
sys.path.append(script_dir)

from library import BouncingCubesAnimation, OrbitingCubesAnimation

# Get the script arguments
args = sys.argv[5:]  # Skip the first 5 arguments, which is: blender --background --python script_name and "--"

if len(args) < 7:
    print("Not enough arguments provided. Expected 7: "
          "job_id, camera_x, camera_y, camera_z, cubes_red, cubes_blue, cubes_random_position_seed")
    sys.exit(1)
else:
    job_id, camera_x, camera_y, camera_z, cubes_red, cubes_blue, cubes_random_position_seed = args[:7]

# TODO: Decide do I put the entire camera angle in the "validation dataset"
#       OR can I have bouncing in training/testing for example, and rotation in validation

train_percentage = 60
val_percentage = 10
test_percentage = 100-train_percentage-val_percentage
green_percentage = 10

should_we_put_green = random.randint(0, 100)

cubes_red, cubes_blue = int(cubes_red), int(cubes_blue)
cubes_green = 0
if should_we_put_green < green_percentage:
    cubes_green = random.randint(1, cubes_red + cubes_blue)
    print(f"Making scene with {cubes_green} green cubes!")

if cubes_green > 0: # IF GREEN WE MAKE 2X SAME VIDEO (just diff colors)
    # TODO: I THINK I MIGHT BE COLORING CUBES DIFFERENTLY
    animation = OrbitingCubesAnimation(
        job_id=job_id,
        camera_x=camera_x,
        camera_y=camera_y,
        camera_z=camera_z,
        cubes_red=cubes_red,
        cubes_blue=cubes_blue,
        cubes_random_position_seed=cubes_random_position_seed,
        cubes_green=cubes_green,
    )
    animation.execute()

    animation = BouncingCubesAnimation(
        job_id=job_id,
        camera_x=camera_x,
        camera_y=camera_y,
        camera_z=camera_z,
        cubes_red=cubes_red,
        cubes_blue=cubes_blue,
        cubes_random_position_seed=cubes_random_position_seed,
        cubes_green=cubes_green,
    )
    animation.execute()

animation = OrbitingCubesAnimation(
    job_id=job_id,
    camera_x=camera_x,
    camera_y=camera_y,
    camera_z=camera_z,
    cubes_red=cubes_red,
    cubes_blue=cubes_blue,
    cubes_random_position_seed=cubes_random_position_seed,
    cubes_green=cubes_green,
)
animation.execute()

animation = BouncingCubesAnimation(
    job_id=job_id,
    camera_x=camera_x,
    camera_y=camera_y,
    camera_z=camera_z,
    cubes_red=cubes_red,
    cubes_blue=cubes_blue,
    cubes_random_position_seed=cubes_random_position_seed,
    cubes_green=cubes_green,
)
animation.execute()

