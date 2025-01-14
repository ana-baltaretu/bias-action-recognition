import sys
import os

script_dir = os.path.dirname(__file__)
sys.path.append(script_dir)

from library import *
from config import frame_start, frame_end, cube_size


# Scene and animation setup
initial_height = 2.5
damping_factor = 0.6
fps = bpy.context.scene.render.fps  # Frames per second
min_distance = 2  # Minimum distance between cubes to avoid overlap
area_for_cubes_pos = 3
min_bounces, max_bounces = 3, 7

# Set up animation frames
bpy.context.scene.frame_start = frame_start
bpy.context.scene.frame_end = frame_end


def generate_cubes_bouncing_animation(total_cubes, red_cubes_count, green_cubes_count):
    check_cubes_count(total_cubes, red_cubes_count, green_cubes_count)
    initialize_RGB_materials()

    # Generate random positions ensuring non-overlapping placement
    positions = []
    counter = 0
    for _ in range(total_cubes):
        while True:
            x, y = random.uniform(-area_for_cubes_pos, area_for_cubes_pos), \
                   random.uniform(-area_for_cubes_pos, area_for_cubes_pos)
            if all(math.sqrt((x - px) ** 2 + (y - py) ** 2) >= min_distance for px, py in positions):
                positions.append((x, y))
                break
            else:
                counter += 1
            if counter > 100:
                break

    # Generate cubes with random bounce timings and start frames
    for i, (x, y) in enumerate(positions):
        bpy.ops.mesh.primitive_cube_add(size=cube_size, location=(x, y, cube_size/2))
        cube = bpy.context.object
        cube.name = f"Cube_{i + 1}"
        cube.data.materials.append(get_material_to_assign(i, red_cubes_count, green_cubes_count))

        # Random start frame for this cube
        start_frame = random.randint(frame_start, frame_end - 100)  # Ensure enough time for animation
        current_frame = start_frame
        height = initial_height
        num_bounces = random.randint(min_bounces, max_bounces)  # Randomize the number of bounces for each cube

        for bounce in range(num_bounces):
            t_up = math.sqrt(2 * height / 9.8)  # Calculate time to peak
            frames_up = int(t_up * fps)

            # Start on the ground
            cube.location.z = 0.35
            cube.scale = (cube_size, cube_size, cube_size * 0.7)  # Flatten on impact
            cube.keyframe_insert(data_path="location", frame=current_frame)
            cube.keyframe_insert(data_path="scale", frame=current_frame)

            # Peak of the bounce
            current_frame += frames_up
            cube.location.z = height + 0.5
            cube.scale = (cube_size * 0.7, cube_size * 0.7, cube_size * 1.3)  # Stretch at peak
            cube.keyframe_insert(data_path="location", frame=current_frame)
            cube.keyframe_insert(data_path="scale", frame=current_frame)

            # Return to the ground
            current_frame += frames_up
            cube.location.z = 0.3
            cube.scale = (cube_size * 1.3, cube_size * 1.3, cube_size * 0.6)  # Flatten on impact
            cube.keyframe_insert(data_path="location", frame=current_frame)
            cube.keyframe_insert(data_path="scale", frame=current_frame)

            # Reset scale shortly after impact
            cube.scale = (cube_size, cube_size, cube_size)
            cube.keyframe_insert(data_path="scale", frame=current_frame + 3)

            # Reduce height for next bounce
            height *= damping_factor

        # Adjust interpolation for smoother motion
        for fcurve in cube.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'BEZIER'


args = get_args()
clean_all()
setup_scene()
print("Bouncing animation setup complete.")

generate_cubes_bouncing_animation(total_cubes=args.number, red_cubes_count=args.red, green_cubes_count=args.green)
create_hemispherical_distribution(args, radius=20, num_points=args.animations)
