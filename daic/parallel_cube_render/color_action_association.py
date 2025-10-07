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

cubes_red, cubes_blue = int(cubes_red), int(cubes_blue)
cubes_green = cubes_red + cubes_blue

# Red/Blue cubes only orbiting
animation = OrbitingCubesAnimation(
    job_id=job_id,
    camera_x=camera_x,
    camera_y=camera_y,
    camera_z=camera_z,
    cubes_red=cubes_red,
    cubes_blue=cubes_blue,
    cubes_random_position_seed=cubes_random_position_seed,
    cubes_green=0,
)
animation.execute()

# Green cubes only bouncing
animation = BouncingCubesAnimation(
    job_id=job_id,
    camera_x=camera_x,
    camera_y=camera_y,
    camera_z=camera_z,
    cubes_red=0,
    cubes_blue=0,
    cubes_random_position_seed=cubes_random_position_seed,
    cubes_green=cubes_green,
)
animation.execute()


