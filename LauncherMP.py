import subprocess
import multiprocessing
import os
from utils.utils import change_here

# Define the paths
blender_path = "C:/Program Files/Blender Foundation/Blender 4.1/blender.exe"
comparison_script = change_here("{change_path}/compare_master.py")
main_blender_script = change_here("{change_path}/__main__.py")
json_folder = change_here("{change_path}/json_folder1")
replacement_json_folder = change_here("{change_path}/json_folder2")
final_json_folder = change_here("{change_path}/final_json")
output_base_folder = change_here("{change_path}/render_output")
first_camera_output_folder = change_here("{change_path}/render_output/first_camera_renders")

# Function to run a subprocess and check the result
def run_process(command):
    try:
        subprocess.run(command, check=True)
        print(f"Command {' '.join(command)} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Command {' '.join(command)} failed with error: {e}")

# Function to run the Blender script with a specific JSON configuration
def run_blender_for_json(json_file, output_folder,first_camera_output_folder):
    # Construct the Blender command
    command = [
        blender_path,
               # Run in background without GUI
        "--python", main_blender_script,  # Main Blender script
        "--",  # Arguments passed to the Python script
        json_file,  # JSON file to be passed
        output_folder,
        first_camera_output_folder  # Output folder for rendering
    ]
     
    # Print the command to check if it's correct
    
    print(f"Running Blender with command: {' '.join(command)}")
    
    # Run the command
    run_process(command)


# Function to run the JSON comparison script and generate final JSONs
def generate_final_jsons():
    for json_file in os.listdir(json_folder):
        if json_file.endswith(".json"):
            base_json = os.path.join(json_folder, json_file)
            replacement_json = os.path.join(replacement_json_folder, json_file)  # Match by file name
            final_json = os.path.join(json_folder, f"final_{json_file}")
            
            if os.path.exists(replacement_json):
                # Command to run the JSON comparison script
                command = [
                    "python", comparison_script, base_json, replacement_json, final_json
                ]
                run_process(command)
            else:
                final_json = os.path.join(final_json_folder, json_file)
                print(f"No replacement JSON found for {json_file}, using base JSON.")
                with open(base_json, 'r') as f_base, open(final_json, 'w') as f_final:
                    f_final.write(f_base.read())

# Main launcher logic
if __name__ == "__main__":
    # Step 1: Generate final JSONs for each room
    generate_final_jsons()

    # Step 2: Launch Blender for each final JSON
    processes = []
    for json_file in os.listdir(final_json_folder):
        if json_file.endswith(".json"):
            final_json = os.path.join(final_json_folder, json_file)
            output_folder = os.path.join(output_base_folder, os.path.splitext(json_file)[0])

            # Ensure the output folder exists
            os.makedirs(output_folder, exist_ok=True)

            # Start Blender process for this JSON
            p = multiprocessing.Process(target=run_blender_for_json, args=(final_json, output_folder,first_camera_output_folder))
            p.start()
            processes.append(p)

    # Wait for all Blender instances to finish
    for p in processes:
        p.join()

    print("All Blender scripts have finished execution.")
