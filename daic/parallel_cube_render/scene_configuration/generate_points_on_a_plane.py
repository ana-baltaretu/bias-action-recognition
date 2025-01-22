import bpy
import math
from mathutils import Vector
import numpy as np
import mathutils

import sys
import os

script_dir = os.path.dirname(__file__)
sys.path.append(script_dir)

from point_on_plane_sampling import PlanePointGenerator


# Parameters
plane_position = (8, 7, 6)  # Position of the plane
plane_size = 5  # Size of the plane


def clean_all():
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


clean_all()


# Function to create a plane at a given position
def create_plane_at_position(location, size=1):
    # Add a plane
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    # Get reference to the newly created plane
    plane = bpy.context.object
    return plane


# Function to rotate an object to face a target
def rotate_to_face_origin(obj, origin=(0, 0, 0)):
    # Compute the direction vector from the object to the origin
    direction = Vector(origin) - obj.location
    # Calculate the rotation to align the local Z-axis with the direction
    rot_quat = direction.to_track_quat('Z', 'Y')  # Align Z-axis towards direction, Y-axis as secondary
    # Apply rotation
    obj.rotation_euler = rot_quat.to_euler()
    return obj.rotation_euler


# Function to get the normal of the plane
def get_plane_normal(plane, origin=(0, 0, 0)):
    # Calculate the direction from the plane to the origin
    direction = Vector(origin) - plane.location
    # Normalize to get the unit normal vector
    normal = direction.normalized()
    return normal


# Function to visualize the normal as a line
def visualize_normal(plane, normal, length=2):
    # Start point is the plane's location
    start = plane.location
    # End point is along the normal direction
    end = start + normal * length

    # Create a curve to visualize the line
    curve_data = bpy.data.curves.new('Normal_Line', type='CURVE')
    curve_data.dimensions = '3D'

    # Create a polyline for the curve
    polyline = curve_data.splines.new('POLY')
    polyline.points.add(1)  # Add two points
    polyline.points[0].co = (start.x, start.y, start.z, 1)  # Start point
    polyline.points[1].co = (end.x, end.y, end.z, 1)  # End point

    # Create an object for the curve and link it to the scene
    curve_object = bpy.data.objects.new('Normal_Visualizer', curve_data)
    bpy.context.collection.objects.link(curve_object)


# Create the plane
plane = create_plane_at_position(plane_position, plane_size)
rotate_to_face_origin(plane)

# Rotate the plane to face the origin
plane_normal = get_plane_normal(plane)

visualize_normal(plane, plane_normal, length=2)


def place_spheres_from_points(points, radius=0.2):
    """
    Place spheres at given points.

    :param points: List of tuples [(x, y, z), ...] specifying the sphere locations.
    :param radius: Radius of the spheres.
    """
    for point in points:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=point)
        bpy.context.object.data.materials.append(yellow_material)


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

    triangle_object.data.materials.append(pink_material)

    return triangle_object


# Example usage
center = np.array(plane_position)  # Plane center in 3D
normal = np.array(plane_normal)  # Plane normal in 3D (e.g., rotated at 45°)
width, height = plane_size-1, plane_size-1  # Plane dimensions
num_points = 10  # Number of points to generate

# Create a new material for yellow spheres
yellow_material = bpy.data.materials.new(name="YellowMaterial")
yellow_material.diffuse_color = (1.0, 1.0, 0.0, 1.0)  # RGBA for yellow

# Create and assign pink material
pink_material = bpy.data.materials.new(name="PinkMaterial")
pink_material.diffuse_color = (1.0, 0.4, 0.7, 1.0)  # RGBA for pink

generator = PlanePointGenerator(center, normal, width, height, num_points)
strategy = "poisson"  # Choose a strategy: 'random', 'grid', or 'poisson'
points = generator.generate_points(strategy)

# Write points to file
output_file = "camera_positions"
with open(output_file, "w") as file:
    print("All Points:\n", points)
    place_spheres_from_points(points)
    file.write(f"X\t\tY\t\tZ\n")
    for (x, y, z) in points:
        create_triangle_pointing_to_origin(x, y, z, size=-1)
        file.write(f"{x:.3f}\t{y:.3f}\t{z:.3f}\n")

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
