import argparse
import sys
import os

script_dir = os.path.dirname(__file__)
sys.path.append(script_dir)

from library import *


def get_args():
    parser = argparse.ArgumentParser()

    # Get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1:]

    # Add parser rules
    parser.add_argument('--number', type=int, help="Number of cubes")
    parser.add_argument('--red', type=int,  help="Number of cubes")
    parser.add_argument('--save', type=str, help="Output folder (path)")

    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


args = get_args()


def generate_cubes_animation(total_cubes, red_cubes_count):
    # Ensure valid counts
    blue_cubes_count = total_cubes - red_cubes_count
    if blue_cubes_count < 0:
        raise ValueError("The number of red cubes cannot exceed the total number of cubes.")

    # Set up scene parameters
    frame_count = 120  # Total frames for the animation
    radius = 3  # Distance of cubes from the origin
    orbit_speed = 2  # Speed of the orbit (adjust as needed)
    cube_size = 1

    # Create materials for red and blue colors if they don't exist
    if "RedMaterial" not in bpy.data.materials:
        red_material = bpy.data.materials.new(name="RedMaterial")
        red_material.diffuse_color = (1, 0, 0, 1)  # Red color
    else:
        red_material = bpy.data.materials["RedMaterial"]

    if "BlueMaterial" not in bpy.data.materials:
        blue_material = bpy.data.materials.new(name="BlueMaterial")
        blue_material.diffuse_color = (0, 0, 1, 1)  # Blue color
    else:
        blue_material = bpy.data.materials["BlueMaterial"]

    # Set up animation frames
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frame_count

    # Generate cubes and assign them colors
    for i in range(total_cubes):
        angle_offset = i * (2 * math.pi / total_cubes)  # Evenly space cubes around the orbit
        bpy.ops.mesh.primitive_cube_add(size=cube_size, location=(
        radius * math.cos(angle_offset), radius * math.sin(angle_offset), cube_size))

        cube = bpy.context.object
        cube.name = f"Cube{i + 1}"

        # Assign color based on the cube count
        if i < red_cubes_count:
            cube.data.materials.append(red_material)
        else:
            cube.data.materials.append(blue_material)

        # Animate the cube to orbit around the Z-axis
        for frame in range(1, frame_count + 1):
            bpy.context.scene.frame_set(frame)

            # Calculate the angle for this frame and this cube
            angle = (2 * math.pi * orbit_speed * frame / frame_count) + angle_offset

            # Update cube position
            cube.location.x = radius * math.cos(angle)
            cube.location.y = radius * math.sin(angle)
            cube.keyframe_insert(data_path="location", index=-1)

    print("Animation setup complete. Play the animation in Blender to see the cubes orbit!")


clean_all()
setup_scene()
generate_cubes_animation(total_cubes=args.number, red_cubes_count=args.red)
create_hemispherical_distribution(args, radius=20, num_points=1)
