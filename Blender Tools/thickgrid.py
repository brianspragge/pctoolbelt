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

def create_grid_draft(grid_size, x_space, y_space, line_width_bu):
    """Creates a grid of vertices, then creates a mesh object from them."""
    vertices = []
    edges = []
    horizontal_edges = []
    vertical_edges = []
    half_line_width = line_width_bu / 2

    # Enable auto-merge
    bpy.context.tool_settings.use_mesh_automerge = True
    bpy.context.tool_settings.double_threshold = 0.00001

    # Create vertices and initial edges
    for y in range(grid_size):
        for x in range(grid_size):
            vertices.append((x * x_space, y * y_space, 0))

            # Horizontal edges (within the same row)
            if x < grid_size - 1:
                horizontal_edges.append((y * grid_size + x, y * grid_size + (x + 1)))  # Edge to the right

            # Vertical edges (within the same column)
            if y < grid_size - 1:
                vertical_edges.append((y * grid_size + x, (y + 1) * grid_size + x))  # Edge downwards

    # For horizontal edges, duplicate upwards and downwards
    for edge in horizontal_edges:
        # Get the indices of the original vertices in the edge
        v1, v2 = edge
        # Get the coordinates of the original vertices
        v1_coords = vertices[v1]
        v2_coords = vertices[v2]

        # Apply the line width shift in the Y direction for horizontal edges
        # Duplicate the vertices by shifting them vertically
        top_v1 = (v1_coords[0], v1_coords[1] - half_line_width, v1_coords[2])  # Shift up by half of line width
        top_v2 = (v2_coords[0], v2_coords[1] - half_line_width, v2_coords[2])  # Shift up by half of line width
        bottom_v1 = (v1_coords[0], v1_coords[1] + half_line_width, v1_coords[2])  # Shift down by half of line width
        bottom_v2 = (v2_coords[0], v2_coords[1] + half_line_width, v2_coords[2])  # Shift down by half of line width

        # Add the new shifted vertices
        vertices.append(top_v1)
        vertices.append(top_v2)
        vertices.append(bottom_v1)
        vertices.append(bottom_v2)

        # Add new edges between the shifted vertices
        edges.append((len(vertices) - 4, len(vertices) - 3))  # Top edge
        edges.append((len(vertices) - 2, len(vertices) - 1))  # Bottom edge

    # For vertical edges, duplicate left and right
    for edge in vertical_edges:
        # Get the indices of the original vertices in the edge
        v1, v2 = edge
        # Get the coordinates of the original vertices
        v1_coords = vertices[v1]
        v2_coords = vertices[v2]

        # Apply the line width shift in the X direction for vertical edges
        # Duplicate the vertices by shifting them horizontally
        left_v1 = (v1_coords[0] - half_line_width, v1_coords[1], v1_coords[2])  # Shift left by half of line width
        left_v2 = (v2_coords[0] - half_line_width, v2_coords[1], v2_coords[2])  # Shift left by half of line width
        right_v1 = (v1_coords[0] + half_line_width, v1_coords[1], v1_coords[2])  # Shift right by half of line width
        right_v2 = (v2_coords[0] + half_line_width, v2_coords[1], v2_coords[2])  # Shift right by half of line width

        # Add the new shifted vertices
        vertices.append(left_v1)
        vertices.append(left_v2)
        vertices.append(right_v1)
        vertices.append(right_v2)

        # Add new edges between the shifted vertices
        edges.append((len(vertices) - 4, len(vertices) - 3))  # Left edge
        edges.append((len(vertices) - 2, len(vertices) - 1))  # Right edge

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

    # Disable auto-merge
    bpy.context.tool_settings.use_mesh_automerge = False

# Call the function to create the grid object mesh
create_grid_draft(grid_size, x_space_bu, y_space_bu, line_width_bu)





# Parameters
grid_size = 19
x_space_mm = 22
y_space_mm = 23.7
line_width_mm = 1

# Conversion to Blender units (1mm = 0.001 Blender units)
x_space_bu = x_space_mm / 1000
y_space_bu = y_space_mm / 1000
line_width_bu = line_width_mm / 1000


for row in range(grid_size)
    for col in range(grid_size)
        def create_plane(default size is 2m so make it = xy / 2)
            # (DEFAULT?)set origin to center mass (ops.object.origin_set)
            name planes f"Row:{row} Col:{col} plane"
