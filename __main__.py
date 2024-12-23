
import json
import os
import bpy
import sys
 

# Select all objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Get the JSON file and output folder from command-line arguments
argv = sys.argv
argv = argv[argv.index("--") + 1:]

# The first argument should be the JSON file, second is the output folder
json_file = argv[0]
output_folder = argv[1]
first_camera_output_folder = argv[2]

# Load the JSON configuration
with open(json_file, 'r') as f:
    config = json.load(f)

# Ensure output folder exists

# Ensure the "first camera renders" folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

 # Replace with your desired absolute path

if not os.path.exists(first_camera_output_folder):
    os.makedirs(first_camera_output_folder)


script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Add the classes directory to the system path
classes_dir = os.path.join(script_dir, 'room_setup')
if classes_dir not in sys.path:
    sys.path.append(classes_dir)

from room_setup import Room, Camera, Light

room = Room(config)

# Switch to Material Preview mode
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'

# Create and configure lights
for light_config in config['lights']:
    Light(light_config)

# Create and configure cameras, render each view
for i, camera_config in enumerate(config['cameras']):
    camera_name = f"Camera no _{i+1}"
    camera = Camera(camera_config, name=camera_name)
    camera.set_render_settings()
    camera.set_render_resolution()
   
    camera.set_camera_view()

    room_name = config['room'].get('name', 'default_room')

    if i == 0:
        # Save the first camera render in a separate folder
        output_image = os.path.join(first_camera_output_folder, f"rendered_image_{room_name}_camera_1.png")
    else:
        # Save other camera renders in the default output folder
        output_image = os.path.join(output_folder, f"rendered_image_camera_{i+1}.png")
    
    # Render the image and save it
    camera.render(output_image)

    print(f"Render and save complete for Camera {i+1}.")

# Define a unique file path for each camera render
    # output_image = os.path.join(output_folder, f"rendered_image_camera_{i+1}.png")
    
    # # Render the image and save it
    # camera.render(output_image)

    # print(f"Render and save complete for Camera {i+1}.")
