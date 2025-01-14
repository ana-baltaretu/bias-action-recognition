import bpy
import mathutils
import os
import math
import datetime

# Record start time
start_time = datetime.datetime.now()
print(f"Script started at: {start_time}")

# Parameters
cube_size = 1
cube_x, cube_y = 1, 1  # Cube position in X, Y
cube_z = cube_size / 2  # Cube position in Z
camera_x, camera_y, camera_z = 10, 10, 10  # Camera position
output_filename = "render_output.mp4"  # Output path for the video


def camera_look_at_origin(camera, x, y, z):
    # Set the camera location
    camera.location = (x, y, z)

    # Compute direction vector from the camera to the origin
    direction = mathutils.Vector((0, 0, 0)) - camera.location

    # Create rotation matrix that points the camera towards the direction vector
    rot_quat = direction.to_track_quat('-Z', 'Y')  # Track Z-axis to point at origin, Y-axis as up

    # Convert quaternion to Euler angles and set camera rotation
    camera.rotation_euler = rot_quat.to_euler()


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


setup_scene()
# Delete all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=cube_size, location=(cube_x, cube_y, cube_z))
cube = bpy.context.object

# Setup & assign material
if "RedMaterial" not in bpy.data.materials:
    red_material = bpy.data.materials.new(name="RedMaterial")
    red_material.diffuse_color = (1, 0, 0, 1)
else:
    red_material = bpy.data.materials["RedMaterial"]
cube.data.materials.append(red_material)

# Create a camera
bpy.ops.object.camera_add(location=(camera_x, camera_y, camera_z))
camera = bpy.context.object
camera_look_at_origin(camera, camera_x, camera_y, camera_z)
bpy.context.scene.camera = camera # Set camera as the active camera

# Set render settings
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
path_to_save = os.path.join(os.path.abspath("."), output_filename)
print("Path to save: ", path_to_save)
bpy.context.scene.render.filepath = path_to_save
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'

# Set animation length
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120  # 120 frames for the video

# Render animation
bpy.ops.render.render(animation=True)

# Record end time
end_time = datetime.datetime.now()
print(f"Script ended at: {end_time}")

# Calculate and display duration
duration = end_time - start_time
print(f"Total duration: {duration}")


