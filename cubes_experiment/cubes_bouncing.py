import sys
import os

script_dir = os.path.dirname(__file__)
sys.path.append(script_dir)

from library import *


def generate_cubes_bouncing_animation(total_cubes, red_cubes_count, green_cubes_count):
    # Ensure valid counts
    blue_cubes_count = total_cubes - red_cubes_count - green_cubes_count
    if blue_cubes_count < 0:
        raise ValueError("The number of red/green cubes cannot exceed the total number of cubes.")

    # Scene and animation setup
    frame_start = 1
    frame_end = 120
    initial_height = 2.5
    damping_factor = 0.6
    fps = bpy.context.scene.render.fps  # Frames per second
    min_distance = 2  # Minimum distance between cubes to avoid overlap
    area_for_cubes_pos = 3

    # Set up animation frames
    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end = frame_end

    # Create materials for red and blue cubes
    if "RedMaterial" not in bpy.data.materials:
        red_material = bpy.data.materials.new(name="RedMaterial")
        red_material.diffuse_color = (1, 0, 0, 1)
    else:
        red_material = bpy.data.materials["RedMaterial"]

    if "BlueMaterial" not in bpy.data.materials:
        blue_material = bpy.data.materials.new(name="BlueMaterial")
        blue_material.diffuse_color = (0, 0, 1, 1)
    else:
        blue_material = bpy.data.materials["BlueMaterial"]

    if "GreenMaterial" not in bpy.data.materials:
        green_material = bpy.data.materials.new(name="GreenMaterial")
        green_material.diffuse_color = (0, 1, 0, 1)
    else:
        green_material = bpy.data.materials["GreenMaterial"]

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
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.5))
        cube = bpy.context.object
        cube.name = f"Cube_{i + 1}"

        # Assign material
        if i < green_cubes_count:
            cube.data.materials.append(green_material)
        elif i < green_cubes_count + red_cubes_count:
            cube.data.materials.append(red_material)
        else:
            cube.data.materials.append(blue_material)

        # Random start frame for this cube
        start_frame = random.randint(frame_start, frame_end - 100)  # Ensure enough time for animation
        current_frame = start_frame
        height = initial_height
        num_bounces = random.randint(3, 7)  # Randomize the number of bounces for each cube

        for bounce in range(num_bounces):
            t_up = math.sqrt(2 * height / 9.8)  # Calculate time to peak
            frames_up = int(t_up * fps)
            frames_total = frames_up * 2

            # Start on the ground
            cube.location.z = 0.35
            cube.scale = (1, 1, 0.7)  # Flatten on impact
            cube.keyframe_insert(data_path="location", frame=current_frame)
            cube.keyframe_insert(data_path="scale", frame=current_frame)

            # Peak of the bounce
            current_frame += frames_up
            cube.location.z = height + 0.5
            cube.scale = (0.7, 0.7, 1.3)  # Stretch at peak
            cube.keyframe_insert(data_path="location", frame=current_frame)
            cube.keyframe_insert(data_path="scale", frame=current_frame)

            # Return to the ground
            current_frame += frames_up
            cube.location.z = 0.3
            cube.scale = (1.3, 1.3, 0.6)  # Flatten on impact
            cube.keyframe_insert(data_path="location", frame=current_frame)
            cube.keyframe_insert(data_path="scale", frame=current_frame)

            # Reset scale shortly after impact
            cube.scale = (1, 1, 1)
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

generate_cubes_bouncing_animation(total_cubes=args.number, red_cubes_count=args.red)
create_hemispherical_distribution(args, radius=20, num_points=args.animations)

