import json
import os
from utils.utils import change_here

def update_dict(base, updates):
    for key, value in updates.items():
        if isinstance(base.get(key), dict) and isinstance(value, dict):
            update_dict(base[key], value)
        else:
            base[key] = value

def merge_lists(base_list, updates_list, key=None):
    if key:
        updates_dict = {item[key]: item for item in updates_list if key in item}
        base_dict = {item[key]: item for item in base_list if key in item}
    else:
        updates_dict = {index: item for index, item in enumerate(updates_list)}
        base_dict = {index: item for index, item in enumerate(base_list)}

    merged_list = []

    for item_key in base_dict:
        if item_key in updates_dict:
            if isinstance(base_dict[item_key], dict):
                update_dict(base_dict[item_key], updates_dict[item_key])
            else:
                base_dict[item_key] = updates_dict[item_key]
        merged_list.append(base_dict[item_key])

    for item_key in updates_dict:
        if item_key not in base_dict:
            merged_list.append(updates_dict[item_key])

    return merged_list

def merge_jsons(json1, json2):
    for key, value in json2.items():
        if isinstance(value, dict):
            if key in json1 and isinstance(json1[key], dict):
                update_dict(json1[key], value)
            else:
                json1[key] = value
        elif isinstance(value, list) and all(isinstance(i, dict) for i in value):
            if key in json1:
                json1[key] = merge_lists(json1[key], value, 'name')
            else:
                json1[key] = value
        else:
            json1[key] = value
    return json1

def get_base_name(file_name):
    # Split the file name before the first underscore or before .json
    return file_name.split('_')[0]

def merge_all_jsons(folder1, folder2, output_folder):
    # Ensure that the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through each JSON in the first folder
    for base_file in os.listdir(folder1):
        if base_file.endswith(".json"):
            base_file_path = os.path.join(folder1, base_file)
            base_name = get_base_name(base_file)
            
            # Find matching replacement files in folder2 based on base_name
            matched = False
            for replacement_file in os.listdir(folder2):
                if replacement_file.endswith(".json") and get_base_name(replacement_file) == base_name:
                    replacement_file_path = os.path.join(folder2, replacement_file)

                    with open(base_file_path, 'r') as f_base, open(replacement_file_path, 'r') as f_replacement:
                        base_json = json.load(f_base)
                        replacement_json = json.load(f_replacement)

                    # Merge the base and replacement JSONs
                    final_json = merge_jsons(base_json, replacement_json)

                    # Save the merged JSON in the output folder
                    output_path = os.path.join(output_folder, base_file)
                    with open(output_path, 'w') as f_output:
                        json.dump(final_json, f_output, indent=4)
                    
                    print(f"Merged {base_file} with {replacement_file} and saved to {output_path}")
                    matched = True
                    break

            if not matched:
                print(f"No replacement JSON found for {base_file}, skipping...")

# Example usage:
folder1 = change_here("{change_path}/json_folder1")  # Folder with base JSON files
folder2 = change_here("{change_path}/json_folder2")  # Folder with replacement JSON files
output_folder = change_here("{change_path}/final_json")  # Folder to save the merged JSON files
merge_all_jsons(folder1, folder2, output_folder)
