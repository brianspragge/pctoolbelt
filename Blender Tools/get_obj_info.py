# \===== HOW TO USE =====/
# select object in blender, go to script tab, paste this code and hit play button

import bpy

# Function to extract vertex and edge data of the active object
def get_edge_and_vertex_data(obj):
    if obj.type == 'MESH':
        # Ensure we're in Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Get the mesh data of the object
        mesh = obj.data

        # Extract vertices (coordinates)
        vertices = [(v.co.x, v.co.y, v.co.z) for v in mesh.vertices]

        # Extract edges (vertex indices)
        edges = [(e.vertices[0], e.vertices[1]) for e in mesh.edges]

        return vertices, edges
    else:
        print(f"Object {obj.name} is not a mesh.")
        return None, None

# Function to create a new text object with the edge and vertex data
def create_text_object_from_data(vertices, edges, name="Edge_Vert_Data"):
    # Create a new text object in Blender's Text Editor
    text_data = bpy.data.texts.new(name)

    # Prepare the text content
    text_content = "Vertices:\n"
    for vertex in vertices:
        text_content += f"  {vertex}\n"

    text_content += "\nEdges:\n"
    for edge in edges:
        text_content += f"  {edge}\n"

    # Write the content to the text object
    text_data.from_string(text_content)

    # Set the text object as active in the Text Editor
    bpy.context.space_data.text = text_data

# Get the active object (you can replace this with any object in the scene)
active_obj = bpy.context.view_layer.objects.active

# Call the function to get vertex and edge data
vertices, edges = get_edge_and_vertex_data(active_obj)

# Create a text object with the data if it exists
if vertices is not None and edges is not None:
    create_text_object_from_data(vertices, edges, name=f"{active_obj.name}_Edge_Vert_Data")
else:
    print("No mesh data available.")
