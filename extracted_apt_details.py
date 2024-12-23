import json
import os
# File paths
space_details_file = "D:/Blender_Folder/dec13/scripts/extraction/paths/10_BPTP Terra_2bhk_1.json"
space_master_file = "D:/Blender_Folder/dec13/scripts/extraction/SpaceMasterData.txt"
output_path_for_pp2 = "D:/Blender_Folder/dec13/scripts/extraction/paths/BPTP"

# Load JSON data from files
with open(space_details_file, "r") as file:
    space_details_data = json.load(file)

with open(space_master_file, "r") as file:
    space_master_data = json.load(file)

# Extract relevant sections
dpa_space_details = space_details_data["Data"]["DPASpaceDetails"]
dpa_space_wall_details = space_details_data["Data"]["DPASpaceWallDetails"]
dpa_space_door_details = space_details_data["Data"]["DPASpaceDoorDetails"]
dpa_space_window_details = space_details_data["Data"]["DPASpaceWindowDetails"]
dpa_space_opening_details=space_details_data["Data"]["DPASpaceOpeningDetails"]
dpa_door_masters = space_master_data["Data"]["DPADoorMasters"]
dpa_window_masters = space_master_data["Data"]["DPAWindowsMasters"]

# Function to filter data by space
def filter_by_space_id(data, space_id):
    return [item for item in data if item.get("DPASpaceId") == space_id]

# Example space details (Master Bedroom)
master_bedrooms = [space for space in dpa_space_details if space["Name"] == "Master Bedroom"]

# Ensure output directory exists
os.makedirs(output_path_for_pp2, exist_ok=True)

# Process each master bedroom
for master_bedroom in master_bedrooms:
    target_space_id = master_bedroom["DPASpaceId"]

# Filter details for the target space
space_details = next(item for item in dpa_space_details if item["DPASpaceId"] == target_space_id)
wall_details = filter_by_space_id(dpa_space_wall_details, target_space_id)
door_details = filter_by_space_id(dpa_space_door_details, target_space_id)
window_details = filter_by_space_id(dpa_space_window_details, target_space_id)
opening_details=filter_by_space_id(dpa_space_opening_details,target_space_id)

# Enrich door and window details with master data
for door in door_details:
    master = next((item for item in dpa_door_masters if item["DoorKey"] == door["DoorKey"]), {})
    door.update(master)

for window in window_details:
    master = next((item for item in dpa_window_masters if item["WindowKey"] == window["WindowKey"]), {})
    window.update(master)

  

# Compile all data
output_data = {
    "SpaceDetails": space_details,
    "WallDetails": wall_details,
    "DoorDetails": door_details,
    "WindowDetails": window_details,
    "OpeningDetails":opening_details
}

output_path_for_pp2 = os.path.join(output_path_for_pp2, f"Extracted_{dpa_space_details[0]["Name"]}_{target_space_id}.json")
# Save to output JSON
with open(output_path_for_pp2, "w") as file:
    json.dump(output_data, file, indent=4)

print(f"Extracted details saved to {output_path_for_pp2}")
