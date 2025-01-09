
import sys
import os

script_dir = os.path.dirname(__file__)
sys.path.append(script_dir)

from library import *
from config import frame_start, frame_end, cube_size


# Set up scene parameters
radius = 3  # Distance of cubes from the origin
orbit_speed = 2  # Speed of the orbit (adjust as needed)

# Set up animation frames
bpy.context.scene.frame_start = frame_start
bpy.context.scene.frame_end = frame_end


def generate_cubes_orbiting_animation(total_cubes, red_cubes_count, green_cubes_count):
    check_cubes_count(total_cubes, red_cubes_count, green_cubes_count)
    initialize_RGB_materials()

    # Generate cubes and assign them colors
    for i in range(total_cubes):
        angle_offset = i * (2 * math.pi / total_cubes)  # Evenly space cubes around the orbit
        bpy.ops.mesh.primitive_cube_add(size=cube_size, location=(
        radius * math.cos(angle_offset), radius * math.sin(angle_offset), cube_size))

        cube = bpy.context.object
        cube.name = f"Cube{i + 1}"
        cube.data.materials.append(get_material_to_assign(i, red_cubes_count, green_cubes_count))

        # Animate the cube to orbit around the Z-axis
        for frame in range(frame_start, frame_end + 1):
            bpy.context.scene.frame_set(frame)

            # Calculate the angle for this frame and this cube
            angle = (2 * math.pi * orbit_speed * frame / frame_end) + angle_offset

            # Update cube position
            cube.location.x = radius * math.cos(angle)
            cube.location.y = radius * math.sin(angle)
            cube.keyframe_insert(data_path="location", index=-1)

    print("Animation setup complete. Play the animation in Blender to see the cubes orbit!")


args = get_args()
clean_all()
setup_scene()
generate_cubes_orbiting_animation(total_cubes=args.number, red_cubes_count=args.red, green_cubes_count=args.green)
create_hemispherical_distribution(args, radius=20, num_points=int(args.animations))
