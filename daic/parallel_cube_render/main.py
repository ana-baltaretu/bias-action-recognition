import sys
import os

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


animation = BouncingCubesAnimation(
    job_id=job_id,
    camera_x=camera_x,
    camera_y=camera_y,
    camera_z=camera_z,
    cubes_red=cubes_red,
    cubes_blue=cubes_blue,
    cubes_random_position_seed=cubes_random_position_seed
)
animation.execute()

animation = OrbitingCubesAnimation(
    job_id=job_id,
    camera_x=camera_x,
    camera_y=camera_y,
    camera_z=camera_z,
    cubes_red=cubes_red,
    cubes_blue=cubes_blue,
    cubes_random_position_seed=cubes_random_position_seed
)
animation.execute()