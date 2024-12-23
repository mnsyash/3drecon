import bpy
import os
from cutout import Cutout
from utils.utils import replace_placeholders

class DoorWindow:
    def __init__(self, name, location, scale,rotation,collection ,wall_obj, blend_file, object_name):
        self.name = name
        self.location = location
        self.scale = scale
        self.rotation = rotation
        self.collection = collection
        self.wall_obj = wall_obj
        self.blend_file = blend_file
        self.object_name = object_name
        self.import_object()

    def import_object(self):
        blend_file_path = replace_placeholders(self.blend_file)
        
        if not os.path.exists(blend_file_path):
            raise FileNotFoundError(f"The blend file '{blend_file_path}' does not exist.")

        with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
            if self.object_name in data_from.objects:
                data_to.objects = [self.object_name]
            else:
                raise ValueError(f"Object '{self.object_name}' not found in '{blend_file_path}'.")

        if data_to.objects:
            imported_object = data_to.objects[0]
            if imported_object is not None:
            
            
                self.collection.objects.link(imported_object)
            
                imported_object.location = self.location
                imported_object.scale = self.scale
                imported_object.name = self.name
                imported_object.rotation_euler = tuple(self.rotation)
                
                imported_object.hide_set(False)
                imported_object.hide_viewport = False
                imported_object.hide_render = False
                        
                    
                
                  
            else:
                raise ValueError(f"Failed to import object '{self.object_name}' from '{blend_file_path}'.")
        else:
            raise ValueError(f"No objects were imported from '{blend_file_path}'.")
