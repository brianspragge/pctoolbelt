import bpy
import bmesh

# Define variables
grid_size = 9
x_space_mm = 22
y_space_mm = 23.7
line_width_mm = 1
line_height_mm = 5

# Convert dimensions to Blender Units
x_space_bu = x_space_mm / 1000
y_space_bu = y_space_mm / 1000
line_width_bu = line_width_mm / 1000
line_height_bu = line_height_mm / 1000

# Create a new collection
collection_name = "ThickGrid"
if collection_name not in bpy.data.collections:
    thickgrid_collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(thickgrid_collection)
else:
    thickgrid_collection = bpy.data.collections[collection_name]

# Function to create planes
def create_grid_plane(location, width, height, name, collection):
    """
    Creates a single plane, removes its face, and moves its corners inward.
    """
    # Add a plane
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=location)
    plane = bpy.context.object
    plane.name = name

    # Scale the plane to the correct size
    plane.scale = (width, height, 1)

    # Apply scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Switch to edit mode
    bpy.context.view_layer.objects.active = plane
    bpy.ops.object.mode_set(mode='EDIT')

    # Modify the geometry
    bm = bmesh.from_edit_mesh(plane.data)

    # Move corners inward
    for vert in bm.verts:
        vert.co.x += -(line_width_bu / 2) if vert.co.x > 0 else (line_width_bu / 2)
        vert.co.y += -(line_width_bu / 2) if vert.co.y > 0 else (line_width_bu / 2)

    # Update the mesh
    bmesh.update_edit_mesh(plane.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add to collection
    collection.objects.link(plane)
    bpy.context.scene.collection.objects.unlink(plane)

    return plane

# Create grid planes
for row in range(grid_size - 1):
    for col in range(grid_size - 1):
        x_loc = col * x_space_bu
        y_loc = row * y_space_bu
        create_grid_plane(location=(x_loc, y_loc, 0), width=x_space_bu, height=y_space_bu, name=f"Plane_{row}_{col}", collection=thickgrid_collection)

# Join all planes into a single object
bpy.ops.object.select_all(action='DESELECT')
for obj in thickgrid_collection.objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = thickgrid_collection.objects[0]
bpy.ops.object.join()

# Reset origin to the center of the object
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

# Add outer rectangle
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(bpy.context.object.data)

# Find the 4 corners of the grid
verts = [v for v in bm.verts]
x_coords = [v.co.x for v in verts]
y_coords = [v.co.y for v in verts]
min_x, max_x = min(x_coords), max(x_coords)
min_y, max_y = min(y_coords), max(y_coords)

# Duplicate the 4 corners
corners = [
    [min_x, min_y, 0],
    [max_x, min_y, 0],
    [max_x, max_y, 0],
    [min_x, max_y, 0],
]
new_verts = []
for corner in corners:
    v = bm.verts.new(corner)
    new_verts.append(v)

# Connect new corners into a rectangle
bm.edges.new([new_verts[0], new_verts[1]])
bm.edges.new([new_verts[1], new_verts[2]])
bm.edges.new([new_verts[2], new_verts[3]])
bm.edges.new([new_verts[3], new_verts[0]])

# Move new verts outward
for v in new_verts:
    if v.co.x > 0:
        v.co.x += line_width_bu
    else:
        v.co.x -= line_width_bu

    if v.co.y > 0:
        v.co.y += line_width_bu
    else:
        v.co.y -= line_width_bu

outer_rect = bm.faces.new(new_verts)
bmesh.update_edit_mesh(bpy.context.object.data)

# Separate the planes from the unselected geometry(outer_rect)
bpy.ops.mesh.separate(type='SELECTED')

# Extrude along Z-axis
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={
    "value": (0, 0, -line_height_bu)
})

bpy.ops.object.mode_set(mode='OBJECT')


# Width: 13.1
# Height: 12.9

# 177 + 26.2 = 203.2
# 191 + 25.8 = 216.8
