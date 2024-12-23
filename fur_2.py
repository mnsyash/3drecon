import json

# Data from Space Dimensions
with open("D:/Blender_Folder/dec13/scripts/extraction/paths/BPTP/dimensions_ready_Master Bedroom_88.json") as f:
    master_bedroom_data = json.load(f)

# Details from extracted file
with open("D:/Blender_Folder/dec13/scripts/extraction/paths/BPTP/Extracted_Master Bedroom_88.json") as f:
    master_bedroom_details = json.load(f)

room_width = master_bedroom_data['room']['width']
room_length = master_bedroom_data['room']['length']

wall_mapping = {
    1: "Wall_1",
    2: "Wall_2",
    3: "Wall_3",
    4: "Wall_4"
}

bed_dimension = [2.0, 1.5]  
side_stool_1_dimension = [0.5, 0.5]
side_stool_2_dimension = [0.5, 0.5]


def categorize_wall(wall_no, door_details, window_details):
    openings_count = sum(door["WallNo"] == wall_no for door in door_details) + sum(window["WallNo"] == wall_no for window in window_details)
    if openings_count == 0:
        return "plain_wall"
    elif openings_count >= 1:
        return "wall_with_one_opening"


furniture = []
for wall in master_bedroom_details["WallDetails"]:
    wall_name = wall_mapping.get(wall["WallNo"])
    subspace_key = wall["SubspaceProductCKey"]
    door_details = master_bedroom_details.get("DoorDetails", [])
    window_details = master_bedroom_details.get("WindowDetails", [])
    wall_type = categorize_wall(wall["WallNo"], door_details, window_details)

    startpoint = next((float(int(door["StartPoint"]) / 1000) for door in door_details if door["WallNo"] == wall["WallNo"]), None)
    door_width = next((float(int(door["DoorWidth"])/1000) for door in door_details if door["WallNo"] == wall["WallNo"]), None)

    if "ENT" in subspace_key:
        furniture.append({
            "type": "ENT",
            "name": "Entertainment unit",
            "model_path": f"{master_bedroom_data['path']['base_path']}/Assets Guest Bedroom (1)/BR1 TV Unit .blend",
            "location": [0, (room_width / 2), 0],
            "rotation": [0, 0, 1.5708],
            "scale": [1, 1, 1],
            "material_config": {},
            "geometry_nodes_params": {}
        })

    for key in ["ST1", "KSB", "ST2"]:
        if key in subspace_key:
            furniture.append({
                "type": key,
                "name": key.replace("ST1", "Side Stool 1")
                             .replace("KSB", "King Size Bed")
                             .replace("ST2", "Side Stool 2"),
                "model_path": f"{master_bedroom_data['path']['base_path']}Rest/{'MBR Side table.blend' if 'ST' in key else 'MBR BED.blend'}",
                "location": [0, (room_width / 2), 0],
                "rotation": [0, 0, 1.5708],
                "scale": [1, 1, 1],
                "material_config": {},
                "geometry_nodes_params": {}
            })

# Replace Door Configuration
door_config = next((door for door in master_bedroom_details.get("DoorDetails", []) if door["WallNo"] == 1), None)
if door_config:
    furniture.append({
        "name": "Door",
        "location": [-0.1, 0.45, 1.2],
        "scale": [1, 1, 1],
        "rotation": [0, 0, 1.5708],
        "wall_name": "Wall_1",
        "blend_file": f"{master_bedroom_data['path']['base_path']}Rest/Door 750 MM.blend",
        "object_name": "MBR 2 Door Toilet D1_750"
    })

# Replace Window Configuration
window_config = next((window for window in master_bedroom_details.get("WindowDetails", []) if window["WallNo"] == 2), None)
if window_config:
    furniture.append({
        "name": "Window",
        "location": [2.25, 4.47, 1.7],
        "scale": [1, 1, 1],
        "rotation": [0, 0, 0],
        "wall_name": "Wall_2",
        "blend_file": f"{master_bedroom_data['path']['base_path']}Rest/MBR Sliding Window Glass.blend",
        "object_name": "MBR Sliding Window Glass"
    })

master_bedroom_data["furniture"] = furniture

updated_file_path = 'D:/Blender_Folder/dec13/scripts/extraction/paths/BPTP/BPTP_Final_Master_Bedroom_88.json'
with open(updated_file_path, 'w') as f:
    json.dump(master_bedroom_data, f, indent=4)

print(f"Updated JSON saved to {updated_file_path}")
