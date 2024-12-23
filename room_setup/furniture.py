import bpy
import os
from utils.utils import replace_placeholders

# def replace_placeholders(path):
#     return path.replace("{base_path}", base_path)

# base_path = "D:/try4/assets/"
class Furniture:
    def __init__(self, name, model_path,collection,location, scale, rotation,material_config=None, geometry_nodes_params=None):
        self.name = name
        self.collection = collection
        self.model_path = replace_placeholders(model_path)
        self.location = location
        self.scale = scale
        self.rotation = rotation
        self.material_config = material_config
        self.geo_nodes_params = geometry_nodes_params
        self.object = self.import_furniture()
        self.apply_geometry_nodes_params()
        if self.geo_nodes_params:
            self.apply_geometry_nodes_params()
         
    
    def import_furniture(self):
        if self.model_path.lower().endswith('.blend'):
            return self.import_blender_furniture()
        
        else:
            raise ValueError(f"Unsupported file format: {self.model_path}")

    def import_blender_furniture(self):
        # Check if the file exists before attempting to load
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Blend file '{self.model_path}' does not exist. Check the path and ensure the file is present.")

        try:
            # Attempt to load the Blender file
            with bpy.data.libraries.load(self.model_path, link=False) as (data_from, data_to):
                print(f"Available objects in the blend file: {data_from.objects}")  # Debugging
                data_to.objects = [name for name in data_from.objects]  # Load all objects
        except Exception as e:
            raise RuntimeError(f"Failed to load the blend file '{self.model_path}': {e}")
        
        imported_object = None
        for obj in data_to.objects:
            if obj is not None:
                self.collection.objects.link(obj)
                #bpy.context.collection.objects.link(obj)
                obj.location = self.location
                obj.scale = self.scale
                obj.rotation_euler = self.rotation
                obj.name = self.name
                imported_object = obj
                
                
                  # Save the imported object reference
        
        if not imported_object:
            raise RuntimeError(f"No objects were imported from '{self.model_path}'. Please check the blend file contents.")
        
        return imported_object

    def update_geo_node_param(self, modifier, geometry_nodes_params, value):
        if modifier.node_group and geometry_nodes_params in modifier.node_group.inputs:
            input_socket = modifier.node_group.inputs[geometry_nodes_params]
            input_socket.default_value = value

             
    
    def update_geo_node_param(self, modifier, geometry_nodes_params, value):
        if modifier.node_group and geometry_nodes_params in modifier.node_group.inputs:
            input_socket = modifier.node_group.inputs[geometry_nodes_params]
            input_socket.default_value = value

    def apply_geometry_nodes_params(self):
        if self.object and self.geo_nodes_params:
            for modifier in self.object.modifiers:
                if modifier.type == 'NODES':
                    for input_name, input_value in self.geo_nodes_params.items():
                        try:
                            if isinstance(input_value, list):
                                modifier[input_name][:] = input_value
                            else:
                                modifier[input_name] = input_value
                        except KeyError:
                            print(f"Modifier does not have input: {input_name}") 