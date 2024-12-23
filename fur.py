import json

#Data from Space Dimensions
with open("D:/Blender_Folder/dec13/scripts/extraction/paths/BPTP/dimensions_ready_Master Bedroom_88.json") as f:
    master_bedroom_data = json.load(f)

#Details from extracted file
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
    # elif openings_count == 2:
    #     return "wall_with_two_openings"
    # else:
    #     return "complex_wall"


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
        ent_config = {
            "plain_wall": {
                "Wall_1": ([0, (room_width / 2), 0], 1.5708),
                "Wall_2": ([(room_length / 2), room_width, 0], 0),
                "Wall_3": ([room_length, (room_width / 2), 0], 4.71239),
                "Wall_4": ([(room_length / 2), 0, 0], 3.14159),
            },
            "wall_with_one_opening": {
                "startpoint < 1000": {
                    "Wall_1": ([0, ((room_width / 2) + (startpoint or 0) / 2 + (door_width or 0) / 2), 0], 1.5708),
                    "Wall_2": ([(room_length / 2) + (startpoint or 0) / 2 + (door_width or 0) / 2, room_width, 0], 0),
                    "Wall_3": ([room_length, ((room_width / 2) + (startpoint or 0) / 2 + (door_width or 0) / 2), 0], 4.71239),
                    "Wall_4": ([(room_length / 2) + (startpoint or 0) / 2 + (door_width or 0) / 2, 0, 0], 3.14159),
                },
                "startpoint > 1000": {
                    "Wall_1": ([0, ((startpoint or 0) / 2), 0], 1.5708),
                    "Wall_2": ([(startpoint or 0) / 2, room_width, 0], 0),
                    "Wall_3": ([room_length, ((startpoint or 0) / 2), 0], 4.71239),
                    "Wall_4": ([(startpoint or 0) / 2, 0, 0], 3.14159),
                }
            }
        }
        selected_config = ent_config[wall_type]
        if wall_type == "wall_with_one_opening":
            if startpoint < 1000:
                selected_config = selected_config["startpoint < 1000"]
            elif startpoint > 1000:
                selected_config = selected_config["startpoint > 1000"]
        if wall_name in selected_config:
            location, z_rotation = selected_config[wall_name]
            furniture.append({
                "type": "ENT",
                "name": "Entertainment unit",
                "model_path": f"{master_bedroom_data['path']['base_path']}Rest/ENT.blend",
                "location": location,
                "rotation": [0, 0, z_rotation],
                "scale": [1, 1, 1],
                "material_config": {},
                "geometry_nodes_params": {}
            })

    
    if any(key in subspace_key for key in ["ST1", "KSB", "ST2"]):
        st_config = {
            "plain_wall": {
                "ST1": {
                    "Wall_1": ([0, (room_width / 2) - (bed_dimension[1] / 2) - (side_stool_1_dimension[1] / 2), 0], 1.5708),
                    "Wall_2": ([(room_length / 2) - (bed_dimension[0] / 2) - (side_stool_1_dimension[0] / 2), room_width, 0], 0),
                    "Wall_3": ([room_length, (room_width / 2) + (bed_dimension[1] / 2) + (side_stool_1_dimension[1] / 2), 0], 4.71239),
                    "Wall_4": ([(room_length / 2) - (bed_dimension[0] / 2) - (side_stool_1_dimension[0] / 2), 0, 0], 3.14159)},  
                "KSB": {
                    "Wall_1": ([0, room_width / 2, 0], 1.5708),
                    "Wall_2": ([room_length / 2, room_width, 0], 0),
                    "Wall_3": ([room_length, room_width / 2, 0], 4.71239),
                    "Wall_4": ([room_length / 2, 0, 0], 3.14159)},  
                "ST2": {
                    "Wall_1": ([0, (room_width / 2) + (bed_dimension[1] / 2) + (side_stool_2_dimension[1] / 2), 0], 1.5708),
                    "Wall_2": ([(room_length / 2) + (bed_dimension[0] / 2) + (side_stool_2_dimension[0] / 2), room_width, 0], 0),
                    "Wall_3": ([room_length, (room_width / 2) - (bed_dimension[1] / 2) - (side_stool_2_dimension[1] / 2), 0], 4.71239),
                    "Wall_4": ([(room_length / 2) - (bed_dimension[0] / 2) - (side_stool_2_dimension[0] / 2), 0, 0], 3.14159)},  
            },
            "wall_with_one_opening": {
                "startpoint < 1000": {
                    "ST1": {
                        "Wall_1": ([0, ((room_width / 2) + ((startpoint or 0) / 2) + ((door_width or 0) / 2) - (bed_dimension[1] / 2) - 0.1 - (side_stool_1_dimension[1] / 2)), 0], 1.5708),
                        "Wall_2": ([(room_length / 2) + ((startpoint or 0) / 2) + ((door_width or 0) / 2) - (bed_dimension[1] / 2) - 0.1 - (side_stool_1_dimension[1] / 2), room_width, 0], 0),
                        "Wall_3": ([room_length, ((room_width / 2) + ((startpoint or 0) / 2) + ((door_width or 0) / 2) + (bed_dimension[1] / 2) + 0.1 + (side_stool_1_dimension[1] / 2)), 0], 4.71239),
                        "Wall_4": ([(room_length / 2) + ((startpoint or 0) / 2) + ((door_width or 0) / 2) + 0.1 + (side_stool_1_dimension[1] / 2), 0, 0], 3.14159)},  
                    "KSB": { 
                        "Wall_1": ([0, ((room_width / 2) + ((startpoint or 0) / 2) + ((door_width or 0) / 2)), 0], 1.5708),
                        "Wall_2": ([(room_length / 2) + ((startpoint or 0) / 2) + ((door_width or 0) / 2), room_width, 0], 0),
                        "Wall_3": ([room_length, ((room_width / 2) + ((startpoint or 0) / 2) + ((door_width or 0) / 2)), 0], 4.71239),
                        "Wall_4": ([(room_length / 2) + ((startpoint or 0) / 2) + ((door_width or 0) / 2), 0, 0], 3.14159)},  
                    "ST2": {
                        "Wall_1": ([0, ((room_width / 2) + ((startpoint or 0) / 2) + ((door_width or 0) / 2) + (bed_dimension[1] / 2) + 0.1 + (side_stool_2_dimension[1] / 2)), 0], 1.5708),
                        "Wall_2": ([(room_length / 2) + ((startpoint or 0) / 2) + ((door_width or 0) / 2) + (bed_dimension[1] / 2) + 0.1 + (side_stool_2_dimension[1] / 2), room_width, 0], 0),
                        "Wall_3": ([room_length, ((room_width / 2) + ((startpoint or 0) / 2) + ((door_width or 0) / 2) - (bed_dimension[1] / 2) - 0.1 - (side_stool_2_dimension[1] / 2)), 0], 4.71239),
                        "Wall_4": ([(room_length / 2) + ((startpoint or 0) / 2) + ((door_width or 0) / 2) - 0.1 - (side_stool_2_dimension[1] / 2), 0, 0], 3.14159)},  
                },
                "startpoint > 1000": {
                    "ST1": {
                        "Wall_1": ([0, (((startpoint or 0) / 2) - (bed_dimension[1] / 2) - 0.1 - (side_stool_1_dimension[1] / 2)), 0], 1.5708),
                        "Wall_2": ([((startpoint or 0) / 2) - (bed_dimension[1] / 2) - 0.1 - (side_stool_1_dimension[1] / 2), room_width, 0], 0),
                        "Wall_3": ([room_length, (((startpoint or 0) / 2) + (bed_dimension[1] / 2) + 0.1 + (side_stool_1_dimension[1] / 2)), 0], 4.71239),
                        "Wall_4": ([((startpoint or 0) / 2) + (bed_dimension[1] / 2) + 0.1 + (side_stool_1_dimension[1] / 2), 0, 0], 3.14159)},  
                    "KSB": {
                        "Wall_1": ([0, ((startpoint or 0) / 2), 0], 1.5708),
                        "Wall_2": ([((startpoint or 0) / 2), room_width, 0], 0),
                        "Wall_3": ([room_length, ((startpoint or 0) / 2), 0], 4.71239),
                        "Wall_4": ([((startpoint or 0) / 2), 0, 0], 3.14159)},  
                    "ST2": {
                        "Wall_1": ([0, (((startpoint or 0) / 2) + (bed_dimension[1] / 2) + 0.1 + (side_stool_2_dimension[1] / 2)), 0], 1.5708),
                        "Wall_2": ([((startpoint or 0) / 2) + (bed_dimension[1] / 2) + 0.1 + (side_stool_2_dimension[1] / 2), room_width, 0], 0),
                        "Wall_3": ([room_length, (((startpoint or 0) / 2) - (bed_dimension[1] / 2) - 0.1 - (side_stool_2_dimension[1] / 2)), 0], 4.71239),
                        "Wall_4": ([((startpoint or 0) / 2) - (bed_dimension[1] / 2) - 0.1 - (side_stool_2_dimension[1] / 2), 0, 0], 3.14159)},  
                }
            }
        }
        selected_config = st_config[wall_type]
        if wall_type == "wall_with_one_opening":
            if startpoint and startpoint < 1000:
                selected_config = selected_config["startpoint < 1000"]
            elif startpoint and startpoint > 1000:
                selected_config = selected_config["startpoint > 1000"]
        for key in ["ST1", "KSB", "ST2"]:
            if key in subspace_key and key in selected_config:
                location, z_rotation = selected_config[key][wall_name]
                furniture.append({
                    "type": key,
                    "name": key.replace("ST1", "Side Stool 1")
                                 .replace("KSB", "King Size Bed")
                                 .replace("ST2", "Side Stool 2"),
                    "model_path": f"{master_bedroom_data['path']['base_path']}Rest/{key}.blend",
                    "location": location,
                    "rotation": [0, 0, z_rotation],
                    "scale": [1, 1, 1],
                    "material_config": {},
                    "geometry_nodes_params": {}
                })


master_bedroom_data["furniture"] = furniture


updated_file_path = 'D:/Blender_Folder/dec13/scripts/extraction/paths/BPTP/BPTP_FInal_Master Bedroom_88.json'
with open(updated_file_path, 'w') as f:
    json.dump(master_bedroom_data, f, indent=4)

print(f"Updated JSON saved to {updated_file_path}")