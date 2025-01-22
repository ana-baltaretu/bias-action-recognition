import bpy
import math
import mathutils
import time
import random
import os
import shutil
from abc import ABC, abstractmethod


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


def check_cubes_count(total_cubes, red_cubes_count, green_cubes_count):
    # Ensure valid counts
    blue_cubes_count = total_cubes - red_cubes_count - green_cubes_count
    if blue_cubes_count < 0:
        raise ValueError("The number of red cubes cannot exceed the total number of cubes.")


red_material, green_material, blue_material = None, None, None


def initialize_RGB_materials():
    global red_material, green_material, blue_material
    if "RedMaterial" not in bpy.data.materials:
        red_material = bpy.data.materials.new(name="RedMaterial")
        red_material.diffuse_color = (1, 0, 0, 1)
    else:
        red_material = bpy.data.materials["RedMaterial"]

    if "GreenMaterial" not in bpy.data.materials:
        green_material = bpy.data.materials.new(name="GreenMaterial")
        green_material.diffuse_color = (0, 1, 0, 1)
    else:
        green_material = bpy.data.materials["GreenMaterial"]

    if "BlueMaterial" not in bpy.data.materials:
        blue_material = bpy.data.materials.new(name="BlueMaterial")
        blue_material.diffuse_color = (0, 0, 1, 1)
    else:
        blue_material = bpy.data.materials["BlueMaterial"]


def get_material_to_assign(i, green_cubes_count, red_cubes_count):
    global red_material, green_material, blue_material
    if i < green_cubes_count:
        return green_material
    if i < green_cubes_count + red_cubes_count:
        return red_material
    return blue_material


def camera_look_at_origin(camera, x, y, z):
    camera.location = (x, y, z)
    direction = mathutils.Vector((0, 0, 0)) - camera.location   # Direction vector from camera to  origin

    # Create rotation matrix that points the camera towards the direction vector
    rot_quat = direction.to_track_quat('-Z', 'Y')

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


def setup_rendering_animation(output_path):
    # Set render resolution
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080

    # Set file format and output path for the animation
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'

    # Set FFMPEG codec and encoding options (optional)
    bpy.context.scene.render.filepath = output_path     # When running on CLUSTER should be inside the /tmp folder
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'

    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'  # Or 'OPTIX' for newer NVIDIA GPUs
    prefs.get_devices()
    for device in prefs.devices:
        device.use = True
        print(f"Device: {device.name}, Type: {device.type}")
    bpy.context.scene.cycles.device = 'GPU'

    # Set animation length
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120

    # Set Cycles as the renderer
    bpy.context.scene.render.engine = 'CYCLES'

    # Render the animation and save it to the specified path
    bpy.ops.render.render(animation=True)


class CubeAnimation(ABC):
    animation_type = "unknown"  # Default value, SHOULD be overridden by subclasses

    def __init__(self, job_id, camera_x, camera_y, camera_z, cubes_red, cubes_blue, cubes_random_position_seed):
        self.frame_start = 1
        self.frame_end = 120
        self.job_id = int(job_id)
        self.camera_x = float(camera_x)
        self.camera_y = float(camera_y)
        self.camera_z = float(camera_z)
        self.total_cubes = int(cubes_red) + int(cubes_blue)
        self.cubes_red = int(cubes_red)
        self.cubes_blue = int(cubes_blue)
        self.random_seed = int(cubes_random_position_seed)

    def setup(self):
        """Shared setup logic."""
        clean_all()
        setup_scene()
        setup_camera(self.camera_x, self.camera_y, self.camera_z)
        random.seed(self.random_seed)

    @abstractmethod
    def generate_animation(self):
        """Animation-specific logic to be implemented by subclasses."""
        pass

    def render(self):
        """Shared rendering logic."""
        output_filename = f"{self.animation_type}_{self.job_id}.mp4"
        temp_path = os.path.join("/tmp", output_filename)
        setup_rendering_animation(temp_path)

        print("Rendered? ", os.path.exists(temp_path))
        result_path = os.path.join(os.path.abspath("."), output_filename)
        print("Moving: ", temp_path)
        print("To: ", result_path)
        shutil.copy(temp_path, result_path)
        print("Moved to:", result_path)

    def execute(self):
        """Template method defining the overall workflow."""
        self.setup()
        self.generate_animation()
        self.render()


class BouncingCubesAnimation(CubeAnimation):
    animation_type = "bouncing"

    def generate_animation(self):
        print("Generating bouncing cubes animation.")
        initialize_RGB_materials()

        # Animation-specific logic
        positions = []
        for _ in range(self.total_cubes):
            while True:
                x, y = random.uniform(-3, 3), random.uniform(-3, 3)  # Example bounds
                if all(math.sqrt((x - px) ** 2 + (y - py) ** 2) >= 2 for px, py in positions):
                    positions.append((x, y))
                    break

        for i, (x, y) in enumerate(positions):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 1))  # Example cube size
            cube = bpy.context.object
            cube.data.materials.append(get_material_to_assign(i, self.cubes_red, self.cubes_blue))
            # TODO: Add bouncing animation logic here
        print("Bouncing cubes animation complete.")


class OrbitingCubesAnimation(CubeAnimation):
    animation_type = "orbiting"

    def generate_animation(self):
        # Set up scene parameters
        radius = 3  # Distance of cubes from the origin
        orbit_speed = 2  # Speed of the orbit (adjust as needed)

        print("Generating orbiting cubes animation.")
        initialize_RGB_materials()

        random_offset = random.uniform(0, math.pi / 4)
        # TODO: Check orbiting animation logic
        for i in range(self.total_cubes):
            angle_offset = i * (2 * math.pi / self.total_cubes) + random_offset

            bpy.ops.mesh.primitive_cube_add(size=1, location=(3 * math.cos(angle_offset), 3 * math.sin(angle_offset), 1))
            cube = bpy.context.object
            cube.data.materials.append(get_material_to_assign(i, self.cubes_red, self.cubes_blue))

            # Animate the cube to orbit around the Z-axis
            for frame in range(self.frame_start, self.frame_end + 1):
                bpy.context.scene.frame_set(frame)

                # Calculate the angle for this frame and this cube
                angle = (2 * math.pi * orbit_speed * frame / self.frame_end) + angle_offset

                # Update cube position
                cube.location.x = radius * math.cos(angle)
                cube.location.y = radius * math.sin(angle)
                cube.keyframe_insert(data_path="location", index=-1)
        print("Orbiting cubes animation complete.")
