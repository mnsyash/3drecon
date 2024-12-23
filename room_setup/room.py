import bpy
import os
from utils.utils import replace_placeholders
from .wall import Wall
from .door_window import DoorWindow
from .cutout import Cutout
from .furniture import Furniture




class Room:
    def __init__(self, config, collection_name=None):
        self.config = config
        room_name = config['room'].get('name', 'RoomCollection')
        collection_name = collection_name or room_name
        self.collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(self.collection)
        self.location = config['room']['location']
        self.length = config['room']['length']
        self.width = config['room']['width']
        self.height = config['room']['height']
        self.create_floor(config.get('floor', {})) 
        self.create_ceiling(config.get('ceiling', {}))
        self.walls = self.create_walls(config.get('walls', []))
        self.create_wall_objects(config.get('wall_objects', []))
        self.create_cutouts(config.get('cutouts', []))
        self.create_openings(config.get('openings', []))
        self.create_doors_windows(config.get('doors_windows', []))
        self.add_furniture(config['furniture'])
        self.create_skirtings(config.get('skirtings', []))
        self.import_false_ceiling(config.get('false_ceiling', []))
        self.create_add_ons(config.get('add_on', []))
        

    

    def link_to_collection(self, obj, collection=None):
       target_collection = collection or self.collection
       if target_collection not in obj.users_collection:
            target_collection.objects.link(obj)
       if bpy.context.collection in obj.users_collection:
            bpy.context.collection.objects.unlink(obj)

    def create_floor(self, floor_config):
        if not floor_config:
            print("No floor configuration provided.")
            return
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=floor_config.get('location', [0, 0, 0]))
        floor = bpy.context.object
        floor.name = floor_config.get('name', 'Floor')
        dimensions = floor_config.get('dimensions', [4, 4, 0.005])
        floor.scale = (dimensions[0], dimensions[1], dimensions[2])
        texture = floor_config.get('texture', {
            'base_color': '{base_path}wallpaper/texture/2-1.png',
            'roughness': '{base_path}wallpaper/texture/2-1.png',
            'normal': '{base_path}wallpaper/texture/2-1.png',
            'displacement': '{base_path}wallpaper/texture/2-1.png'
        })
        texture_transform = floor_config.get('texture_transform', {
            'scale': [1, 1, 1],
            'location': [0, 0, 0],
            'rotation': [0, 0, 0]
        })

        self.apply_material(floor, texture, texture_transform)
        self.link_to_collection(floor)

    def apply_material(self, obj, texture, texture_transform):
            # Create a new material and enable nodes
            mat = bpy.data.materials.new(name=obj.name + "_Material")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get("Principled BSDF")

            # Nodes: Texture Coordinate and Mapping
            tex_coord = mat.node_tree.nodes.new('ShaderNodeTexCoord')
            mapping = mat.node_tree.nodes.new('ShaderNodeMapping')
            mat.node_tree.links.new(mapping.inputs['Vector'], tex_coord.outputs['UV'])

            # Retrieve texture paths
            base_color_path = replace_placeholders(texture.get('base_color', ''))
            roughness_path = replace_placeholders(texture.get('roughness', ''))
            normal_path = replace_placeholders(texture.get('normal', ''))
            displacement_path = replace_placeholders(texture.get('displacement', ''))

            # Scale, location, and rotation values from JSON
            scale = texture_transform.get('scale', [1, 1, 1])
            location = texture_transform.get('location', [0, 0, 0])
            rotation = texture_transform.get('rotation', [0, 0, 0])

            # Set the mapping node values
            mapping.inputs['Scale'].default_value = scale
            mapping.inputs['Location'].default_value = location
            mapping.inputs['Rotation'].default_value = rotation

            # Function to load texture nodes
            def load_texture_node(image_path, label):
                if os.path.exists(image_path):
                    texture_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                    try:
                        texture_node.image = bpy.data.images.load(image_path)
                        texture_node.label = label
                        mat.node_tree.links.new(texture_node.inputs['Vector'], mapping.outputs['Vector'])
                        print(f"Loaded texture: {image_path}")
                        return texture_node
                    except Exception as e:
                        print(f"Failed to load texture {image_path}: {e}")
                        return None
                else:
                    print(f"Texture file not found: {image_path}")
                    return None

            # Load and connect textures
            base_color_node = load_texture_node(base_color_path, "Base Color")
            roughness_node = load_texture_node(roughness_path, "Roughness")
            normal_node = load_texture_node(normal_path, "Normal")
            displacement_node = load_texture_node(displacement_path, "Displacement")

            # Connect Base Color to BSDF
            if base_color_node:
                mat.node_tree.links.new(bsdf.inputs['Base Color'], base_color_node.outputs['Color'])

            # Connect Roughness to BSDF
            if roughness_node:
                roughness_node.image.colorspace_settings.name = 'Non-Color'
                mat.node_tree.links.new(bsdf.inputs['Roughness'], roughness_node.outputs['Color'])

            # Connect Normal Map
            if normal_node:
                normal_map_node = mat.node_tree.nodes.new('ShaderNodeNormalMap')
                normal_node.image.colorspace_settings.name = 'Non-Color'
                mat.node_tree.links.new(normal_map_node.inputs['Color'], normal_node.outputs['Color'])
                mat.node_tree.links.new(bsdf.inputs['Normal'], normal_map_node.outputs['Normal'])

            # Connect Displacement
            if displacement_node:
                displacement_node.image.colorspace_settings.name = 'Non-Color'
                disp_node = mat.node_tree.nodes.new('ShaderNodeDisplacement')
                mat.node_tree.links.new(disp_node.inputs['Height'], displacement_node.outputs['Color'])
                disp_node.inputs['Midlevel'].default_value = 0.5
                disp_node.inputs['Scale'].default_value = 1.0
                mat.node_tree.links.new(mat.node_tree.nodes['Material Output'].inputs['Displacement'], disp_node.outputs['Displacement'])

            # Assign material to the object
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)
            print(f"Material applied with textures for object: {obj.name}")

    def create_skirtings(self, skirtings_config):
        for skirting in skirtings_config:
            skirting_name = skirting.get('name', 'Skirting')
            skirting_location = skirting.get('location', [0, 0, 0])
            skirting_scale = skirting.get('scale', [0.1, 2, 0.1])  # Skirting height is small
            skirting_texture = skirting.get('texture', {})
            skirting_texture_transform = skirting.get('texture_transform', {})
            skirting_wall_name = skirting.get('wall_name')
            
            if skirting_wall_name in self.walls:
                skirting_obj = Wall(skirting_name, skirting_location, skirting_scale, [1, 1, 1], skirting_texture, skirting_texture_transform).object
                self.apply_material(skirting_obj, skirting_texture, skirting_texture_transform)
                self.link_to_collection(skirting_obj)

                # Handle cutouts for skirting using the wall cutouts configuration
                skirting_cutouts = skirting.get('cutouts', [])
                for cutout in skirting_cutouts:
                    if skirting_wall_name in self.walls:
                        Cutout(cutout['name'], cutout['location'], cutout['scale'], skirting_obj)
                    else:
                        print(f"Skirting '{skirting_name}' does not match any wall for cutout '{cutout['name']}'.")

    def create_ceiling(self, ceiling_config=None):
        if ceiling_config is None:
            ceiling_config = {}

        # Get the location and scale from the JSON config
        location_with_height = ceiling_config.get('location', (self.location[0], self.location[1], self.height))
        scale = ceiling_config.get('scale', [self.length, self.width, 1])  # Default to room's length and width

        # Add the ceiling mesh at the specified location
        bpy.ops.mesh.primitive_cube_add(size=1, location=location_with_height)
        ceiling = bpy.context.object
        ceiling.name = ceiling_config.get('name', "Ceiling")
        
        # Set the scale directly from the JSON
        ceiling.scale[0] = scale[0]  # Length of ceiling
        ceiling.scale[1] = scale[1]  # Width of ceiling
        ceiling.scale[2] = scale[2]  # Optional: Thickness or height (usually not used in a plane, but just in case)

        # Link ceiling to the collection
        self.ceiling = ceiling
        self.link_to_collection(ceiling)

        print(f"Ceiling created with scale: {scale} at location: {location_with_height}")

    def import_false_ceiling_with_lights(self, file_path, object_name, location, scale):
        if not os.path.exists(file_path):
            print(f"Blend file '{file_path}' does not exist.")
            return

        with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
            # Import the specific ceiling object and its collection (lights included)
            if object_name in data_from.objects:
                data_to.objects.append(object_name)
            else:
                print(f"Object '{object_name}' not found in '{file_path}'.")

            # If lights are part of a collection or hierarchy, import all linked data
            collections_to_import = [coll for coll in data_from.collections]
            data_to.collections.extend(collections_to_import)

        imported_ceiling = None
        imported_collection = None

        # Link the imported objects and collections to the current collection
        for imported_object in data_to.objects:
            if imported_object is not None:
                self.collection.objects.link(imported_object)
                if imported_object.type == 'MESH' and imported_object.name == object_name:
                    imported_ceiling = imported_object
                    imported_ceiling.location = location
                    imported_ceiling.scale = scale
                    imported_ceiling.name = "FalseCeiling"
                    print(f"Imported false ceiling '{object_name}' from '{file_path}' at location {location} with scale {scale}.")
        
        # Handle imported collections (for lights and other linked objects)
        for imported_collection in data_to.collections:
            if imported_collection is not None:
                bpy.context.scene.collection.children.link(imported_collection)
                print(f"Imported collection '{imported_collection.name}' from '{file_path}'.")

        # Ensure lights are parented properly
        if imported_ceiling:
            for obj in bpy.context.scene.objects:
                if obj.type == 'LIGHT' and obj.name.startswith(object_name):
                    obj.parent = imported_ceiling
                    obj.matrix_parent_inverse = imported_ceiling.matrix_world.inverted()
                    print(f"Parented light '{obj.name}' to ceiling '{imported_ceiling.name}'.")

    def import_false_ceiling(self, false_ceiling_config):
        for fc in false_ceiling_config:
            blend_file_path = replace_placeholders(fc.get('blend_file', ''))
            object_name = fc.get('object_name', 'FalseCeiling')
            location = fc.get('location', [0, 0, 0])
            scale = fc.get('scale', [1, 1, 1])

            self.import_false_ceiling_with_lights(blend_file_path, object_name, location, scale)

    
    def create_walls(self, walls_config):
        self.walls = {}
        for wall in walls_config:
            color = wall.get('color', [1, 1, 1])
            texture = wall.get('texture')
            texture_transform = wall.get('texture_transform', {})
            new_wall = Wall(wall['name'], wall['location'], wall['scale'],color, texture, texture_transform)
            self.walls[wall['name']] = new_wall.object
            self.link_to_collection(new_wall.object)            
        return self.walls
    
    def create_wall_objects(self, wall_objects_config):
        for obj in wall_objects_config:
            wall_name = obj['wall_name']
            if wall_name in self.walls:
                DoorWindow(obj['name'], obj['location'], obj['scale'], obj['rotation'], self.collection, self.walls[wall_name], obj['blend_file'], obj['object_name'])
            else:
                print(f"Wall '{wall_name}' not found for wall object '{obj['name']}'.")   

    def create_cutouts(self, cutouts_config):
        for cutout in cutouts_config:
            wall_name = cutout['wall_name']
            if wall_name in self.walls:
                Cutout(cutout['name'], cutout['location'], cutout['scale'], self.walls[wall_name])
            else:
                print(f"Wall '{wall_name}' not found for cutout '{cutout['name']}'.")        

    def create_doors_windows(self, doors_windows_config):
        for dw in doors_windows_config:
            wall_name = dw['wall_name']
            if wall_name in self.walls:
                DoorWindow(dw['name'], dw['location'], dw['scale'], dw['rotation'],self.collection, self.walls[wall_name], dw['blend_file'], dw['object_name'])

            else:
                print(f"Wall '{wall_name}' not found for door/window '{dw['name']}'.")
            
    def create_openings(self, openings_config):
        # Create openings in walls based on the JSON configuration
        for opening in openings_config:
            wall_name = opening['wall_name']
            if wall_name in self.walls:
                Cutout(opening['name'], opening['location'], opening['scale'], self.walls[wall_name])
            else:
                print(f"Wall '{wall_name}' not found for opening '{opening['name']}'.")        

    def create_door(self, door_config):
        door = DoorWindow(self.walls[door_config['wall']], door_config['name'], door_config['location'], door_config['scale'], self.door_material)

    def create_window(self, window_config):
        window = DoorWindow(self.walls[window_config['wall']], window_config['name'], window_config['location'], window_config['scale'], self.door_material)

    def add_furniture(self, furniture_config):
        for furn in furniture_config:
            Furniture(furn['name'], furn['model_path'] ,self.collection,furn['location'], furn['scale'], furn['rotation'],furn['material_config'],furn['geometry_nodes_params'])
            

    def move_collection(self,collection, new_location):
        # This method moves the entire collection to the new location
        for obj in collection.objects:
            obj.location.x += new_location[0] 
            obj.location.y += new_location[1] 
            obj.location.z += new_location[2]         
        print(f"Moved collection '{collection.name}' to new location: {new_location}")
    
    def create_add_ons(self, add_ons_config):
        # Recursively create add-ons as separate rooms
        for add_on in add_ons_config:
            add_on_name = add_on.get('room', {}).get('name', 'Add-On')
            add_on_room = Room(add_on, collection_name=f"Add-On_{add_on_name}")

            # Get new location from add_on configuration
            new_location = add_on.get('room_collection', {}).get('location', [0, 0, 0])

            # Move the add-on collection to the new location
            self.move_collection(add_on_room.collection, new_location)
            print(f"Add-On room '{add_on_name}' created and moved to {new_location}")
