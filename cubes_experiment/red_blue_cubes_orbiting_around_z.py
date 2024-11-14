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
    parser.add_argument('--number', help="Number of cubes")
    parser.add_argument('--save', help="Output folder (path)")

    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


args = get_args()


def generate_cubes_animation():
    # Set up scene parameters
    frame_count = 120  # Total frames for the animation
    radius = 3  # Distance of cubes from the origin
    orbit_speed = 2  # Speed of the orbit (adjust as needed)
    cube_size = 1

    # Create two cubes
    bpy.ops.mesh.primitive_cube_add(size=1, location=(radius, 0, 0))
    cube1 = bpy.context.object
    cube1.name = "Cube1"
    cube1.location = (radius, 0, cube_size)

    bpy.ops.mesh.primitive_cube_add(size=1, location=(-radius, 0, 0))
    cube2 = bpy.context.object
    cube2.name = "Cube2"
    cube2.location = (-radius, 0, cube_size)

    # Set colors for the cubes
    cube1.data.materials.append(bpy.data.materials.new(name="RedMaterial"))
    cube1.data.materials[0].diffuse_color = (1, 0, 0, 1)  # Red color
    cube2.data.materials.append(bpy.data.materials.new(name="BlueMaterial"))
    cube2.data.materials[0].diffuse_color = (0, 0, 1, 1)  # Blue color

    # Set up animation frames
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frame_count

    # Animate both cubes to orbit around the Z-axis
    for frame in range(1, frame_count + 1):
        bpy.context.scene.frame_set(frame)

        # Calculate the angle for this frame (in radians)
        angle = (2 * math.pi * orbit_speed * frame) / frame_count

        # Update Cube1 position (Orbiting clockwise)
        cube1.location.x = radius * math.cos(angle)
        cube1.location.y = radius * math.sin(angle)
        cube1.keyframe_insert(data_path="location", index=-1)

        # Update Cube2 position (Orbiting clockwise, shifted by 180 degrees)
        cube2.location.x = radius * math.cos(angle + math.pi)
        cube2.location.y = radius * math.sin(angle + math.pi)
        cube2.keyframe_insert(data_path="location", index=-1)

    print("Animation setup complete. Play the animation in Blender to see the cubes orbit!")

clean_all()
setup_scene()
generate_cubes_animation()
create_hemispherical_distribution(args, radius=20, num_points=1)
