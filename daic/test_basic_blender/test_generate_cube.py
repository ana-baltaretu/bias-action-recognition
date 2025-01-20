import bpy
import mathutils
import os
import math
import datetime
import shutil
import sys

# Get the script arguments
args = sys.argv[4:]  # Skip the first 4 arguments, which is: --background --python script_name and "--"

if len(args) < 4:
    print("Not enough arguments provided. Expected: job_id, red, green, blue")
    sys.exit(1)
else:
    job_id, red, green, blue = args[:4]
    print(f"Red: {red}, Green: {green}, Blue: {blue}")


# Record start time
start_time = datetime.datetime.now()
print(f"Script started at: {start_time}")

# Parameters
cube_size = 1
cube_x, cube_y = 1, 1  # Cube position in X, Y
cube_z = cube_size / 2  # Cube position in Z
camera_x, camera_y, camera_z = 10, 10, 10  # Camera position

# FILE PATH == VERY IMPORTANT TO PUT IT IN TMP!!!!!!!!!!!!!
output_filename = f"render_output{job_id}.mp4"  # Output path for the video
temp_path = os.path.join(os.path.abspath("/tmp"), output_filename)
result_path = os.path.join(os.path.abspath("."), output_filename)


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

prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'CUDA'  # Or 'OPTIX' for newer NVIDIA GPUs
prefs.get_devices()
for device in prefs.devices:
    device.use = True
    print(f"Device: {device.name}, Type: {device.type}")
bpy.context.scene.cycles.device = 'GPU'

setup_scene()
# Delete all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=cube_size, location=(cube_x, cube_y, cube_z))
cube = bpy.context.object

# Setup & assign material
if "CubeMaterial" not in bpy.data.materials:
    cube_material = bpy.data.materials.new(name="CubeMaterial")
    cube_material.diffuse_color = (float(red), float(green), float(blue), 1)
else:
    cube_material = bpy.data.materials["CubeMaterial"]
cube.data.materials.append(cube_material)

# Create a camera
bpy.ops.object.camera_add(location=(camera_x, camera_y, camera_z))
camera = bpy.context.object
camera_look_at_origin(camera, camera_x, camera_y, camera_z)
bpy.context.scene.camera = camera # Set camera as the active camera

# Set render settings
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
print("Saving at:", temp_path)
bpy.context.scene.render.filepath = temp_path
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'

# Set animation length
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120  # 60 frames for the video

# Render animation
bpy.ops.render.render(animation=True)

# Record end time
end_time = datetime.datetime.now()
print(f"Script ended at: {end_time}")

# Calculate and display duration
duration = end_time - start_time
print(f"Total duration: {duration}")

# Copy file from temp to actual output location
shutil.copy(temp_path, result_path)
print("Moved to:", result_path)

