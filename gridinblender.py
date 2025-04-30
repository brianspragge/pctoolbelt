import bpy
import math

# Parameters
grid_size = 19
x_space_mm = 22
y_space_mm = 23.7
line_width_mm = 1
# star_width_mm = 4

# Conversion to Blender units (1mm = 0.001 Blender units)
x_space_bu = x_space_mm / 1000
y_space_bu = y_space_mm / 1000
line_width_bu = line_width_mm / 1000
# star_width_bu = star_width_mm / 1000

def create_grid_draft(grid_size, x_space, y_space):
    """Creates a grid of vertices, then creates a mesh object from them."""
    vertices = []
    edges = []

    for y in range(grid_size):
        for x in range(grid_size):
            vertices.append((x * x_space, y * y_space, 0))

            # Create edges between consecutive vertices in a row
            if x < grid_size - 1:
                edges.append((y * grid_size + x, y * grid_size + (x + 1)))  # Edge to the right

            # Create edges between consecutive vertices in a column
            if y < grid_size - 1:
                edges.append((y * grid_size + x, (y + 1) * grid_size + x))  # Edge downwards

    # Create the mesh
    mesh = bpy.data.meshes.new(name="GridMesh")
    obj = bpy.data.objects.new(f"{grid_size}x{grid_size}_Grid", mesh)

    # Link the object to the current collection
    bpy.context.collection.objects.link(obj)

    # Make the new object the active object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Create the mesh from vertices and edges
    mesh.from_pydata(vertices, edges, [])
    mesh.update()

    # Switch to Object Mode to make sure it is properly displayed
    if bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

# Call the function to create the grid object mesh
create_grid_draft(grid_size, x_space_bu, y_space_bu)
