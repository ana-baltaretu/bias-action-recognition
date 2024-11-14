import bpy
import math
import mathutils
import time
import random
import os
#from joblib import Parallel, delayed


def clean_all():
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def setup_scene():
    # Add a ground plane
    bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
    plane = bpy.context.object
    plane.name = "GroundPlane"

    # Set ground plane color/material (optional)
    ground_mat = bpy.data.materials.new(name="GroundMaterial")
    ground_mat.diffuse_color = (0.8, 0.8, 0.8, 1)  # Light gray color
    plane.data.materials.append(ground_mat)

    # Add a light source for shadows
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    light = bpy.context.object
    light.name = "SunLight"
    light.data.energy = 5  # Adjust brightness as needed
    light.rotation_euler = (math.radians(-30), 0, math.radians(30))  # 30 degrees tilt

    # Enable shadow rendering in the light settings
    light.data.shadow_soft_size = 0.5  # Adjust shadow softness


def camera_look_at_origin(camera, x, y, z):
    # Set the camera location
    camera.location = (x, y, z)

    # Compute direction vector from the camera to the origin
    direction = mathutils.Vector((0, 0, 0)) - camera.location

    # Create rotation matrix that points the camera towards the direction vector
    rot_quat = direction.to_track_quat('-Z', 'Y')  # Track Z-axis to point at origin, Y-axis as up

    # Convert quaternion to Euler angles and set camera rotation
    camera.rotation_euler = rot_quat.to_euler()


def setup_camera(x, y, z):
    # Delete existing cameras (optional)
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            bpy.data.objects.remove(obj, do_unlink=True)

    # Create a new camera
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    bpy.context.scene.camera = camera

    # Set camera position and rotation
    camera_look_at_origin(camera, x, y, z)


def setup_rendering_animation():
    # Set render resolution
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080

    # Set file format and output path for the animation
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'

    # Set FFMPEG codec and encoding options (optional)
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'

    # Render the animation and save it to the specified path
    bpy.ops.render.render(animation=True)


def generate_hemispherical_coordinates(radius, num_points, min_distance=8):
    coordinates = []

    counter = 0

    while len(coordinates) < num_points:
        # Generate a random angle theta between 0 and π/2 (latitude) to keep points above y=0
        theta = math.acos(random.random())  # θ in [0, π/2]
        # Generate a random angle phi between 0 and 2π (longitude)
        phi = 2 * math.pi * random.random()

        # Convert spherical coordinates (radius, theta, phi) to Cartesian coordinates (x, y, z)
        x = radius * math.sin(theta) * math.cos(phi)
        y = radius * math.sin(theta) * math.sin(phi)
        z = radius * math.cos(theta)

        too_close = any(
            math.sqrt((x - px) ** 2 + (y - py) ** 2 + (z - pz) ** 2) < min_distance
            for px, py, pz in coordinates
        )

        # If no points are too close, add this point to the list
        if not too_close:
            coordinates.append((x, y, z))
        else:
            counter += 1

        if counter == 100:
            break

    return coordinates


def create_base_folder(file_path):
    # Take everything in the path except the last segment
    base_folder = "/".join(file_path.split("/")[:-1])

    # Create the directories up to the last specified directory if they don't exist
    if not os.path.exists(base_folder):
        os.makedirs(base_folder, exist_ok=True)
        print(f"Folder created up to: {base_folder}")


def get_absolute_path(relative_path):
    absolute_path = os.path.abspath(relative_path)
    return absolute_path


def parallelized_part(save_file, i, x, y, z):
    start_time = time.time()

    create_base_folder(save_file)
    setup_camera(x, y, z)
    bpy.context.scene.render.filepath = get_absolute_path(save_file) + f"{i}.mp4"  # Set your output path
    setup_rendering_animation()

    print(f"Rendered {i}")
    end_time = time.time()
    print(f"Time taken (so far, for video {i}): {end_time - start_time:.2f} seconds")


def create_hemispherical_distribution(args, radius=5, num_points=10):
    # Generate coordinates and place spheres at those points
    coords = generate_hemispherical_coordinates(radius=radius, num_points=num_points)
    #Parallel(n_jobs=-1)(delayed(parallelized_part)(args.save, i, x, y, z) for i, (x, y, z) in enumerate(coords))

    for i, (x, y, z) in enumerate(coords):
        parallelized_part(args.save, i, x, y, z)
