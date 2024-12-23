import os

def replace_placeholders(path):
    base_path = "D:/Blender_Folder/dec13/scripts/assets/"
    return path.replace("{base_path}", base_path)



def change_here(path):
    change_path = "D:/Blender_Folder/dec13/scripts/"
    # Replace placeholder in the path with the actual base path or other dynamic values
    return path.replace("{change_path}", change_path)


# Define the base path once
