import bpy
import math
import mathutils
import time
import random
import os


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


def create_triangle_pointing_to_origin(x, y, z, size=-3):
    # Create a new mesh and object for the triangle
    mesh = bpy.data.meshes.new("Triangle")
    triangle_object = bpy.data.objects.new("Triangle", mesh)

    # Link the object to the scene
    bpy.context.collection.objects.link(triangle_object)

    # Calculate direction vector towards the origin
    direction = mathutils.Vector((0, 0, 0)) - mathutils.Vector((x, y, z))
    direction.normalize()

    # Define vertices for the triangle
    # Vertex 1: Center of the sphere
    vertex1 = (x, y, z)
    # Vertex 2: Offset towards the origin
    vertex2 = (x - direction.x * size, y - direction.y * size, z - direction.z * size)
    # Vertex 3: Offset towards the origin at an angle
    vertex3 = (x - direction.x * size * 0.8,
               y - direction.y * size * 0.8 + size * 0.5,
               z - direction.z * size * 0.8)

    # Combine vertices into a list
    vertices = [vertex1, vertex2, vertex3]

    # Define a single face for the triangle
    faces = [(0, 1, 2)]

    # Create the mesh
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    # Create and assign pink material
    pink_material = bpy.data.materials.get("PinkMaterial")
    if pink_material is None:
        pink_material = bpy.data.materials.new(name="PinkMaterial")
        pink_material.diffuse_color = (1.0, 0.4, 0.7, 1.0)  # RGBA for pink
    triangle_object.data.materials.append(pink_material)

    return triangle_object


def generate_cubes_bouncing_animation(total_cubes, red_cubes_count, green_cubes_count):
    # Ensure valid counts
    blue_cubes_count = total_cubes - red_cubes_count
    if blue_cubes_count < 0:
        raise ValueError("The number of red cubes cannot exceed the total number of cubes.")

    # Scene and animation setup
    frame_start = 1
    frame_end = 120
    initial_height = 2.5
    damping_factor = 0.6
    fps = bpy.context.scene.render.fps  # Frames per second
    min_distance = 2  # Minimum distance between cubes to avoid overlap

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
            x, y = random.uniform(-3, 3), random.uniform(-3, 3)
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


clean_all()
setup_scene()
coordinates = generate_hemispherical_coordinates(radius=20, num_points=10)

# Create a new material for yellow spheres
yellow_material = bpy.data.materials.new(name="YellowMaterial")
yellow_material.diffuse_color = (1.0, 1.0, 0.0, 1.0)  # RGBA for yellow

# Create spheres in Blender at the generated coordinates
for coord in coordinates:
    x, y, z = coord
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(x, y, z))
    bpy.context.object.data.materials.append(yellow_material)
    create_triangle_pointing_to_origin(x, y, z)

generate_cubes_bouncing_animation(9, 3, 1)