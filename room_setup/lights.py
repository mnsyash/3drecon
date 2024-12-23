import bpy
from utils.utils import  *

class Light:
    def __init__(self, config):
        self.config = config
        if "type" in self.config and self.config['type'] in ['POINT', 'SUN', 'SPOT', 'AREA']:
            self.light = self.create_light()
        else:
            print("No valid light type specified. Skipping light creation.")
        
        # If environment_image is provided, create the world environment
        if "environment_image" in self.config:
            self.create_world_environment()

    def create_light(self):
        bpy.ops.object.light_add(type=self.config['type'], location=self.config['location'])
        light = bpy.context.object
        light.name = self.config['name']
        light.scale = self.config['scale']
        light.data.color = self.config['color']
        light.data.energy = self.config['power']
        light.data.diffuse_factor = self.config['diffuse']
        light.data.specular_factor = self.config['specular']
        light.data.volume_factor = self.config['volume']
        light.data.shadow_soft_size = self.config['radius']
        if self.config['type'] == 'SPOT':
            light.data.spot_size = self.config['spot_size']
            light.data.spot_blend = self.config['spot_blend']
        return light

    def create_world_environment(self):
            try:
                image_path=replace_placeholders(self.config['environment_image'])
                print(f"Creating world environment texture with image: {image_path}")
                
                # Ensure we're editing the world nodes
                world = bpy.context.scene.world
                if not world.use_nodes:
                    world.use_nodes = True
                node_tree = world.node_tree
                nodes = node_tree.nodes
                
                # Clear existing nodes
                for node in nodes:
                    nodes.remove(node)
                print("Existing world nodes cleared.")

                # Add the necessary nodes
                texture_coord_node = nodes.new(type='ShaderNodeTexCoord')
                mapping_node = nodes.new(type='ShaderNodeMapping')
                env_texture_node = nodes.new(type='ShaderNodeTexEnvironment')
                background_node_1 = nodes.new(type='ShaderNodeBackground')
                background_node_2 = nodes.new(type='ShaderNodeBackground')
                mix_shader_node = nodes.new(type='ShaderNodeMixShader')
                light_path_node = nodes.new(type='ShaderNodeLightPath')
                world_output_node = nodes.new(type='ShaderNodeOutputWorld')
                # Set up the environment texture with the image from the JSON
                env_texture_node.image = bpy.data.images.load(image_path)

                # Position nodes (optional but useful for organization)
                texture_coord_node.location = (-1000, 0)
                mapping_node.location = (-800, 0)
                env_texture_node.location = (-600, 0)
                background_node_1.location = (-400, 200)
                background_node_2.location = (-400, -200)
                mix_shader_node.location = (-200, 0)
                light_path_node.location = (-600, 400)
                world_output_node.location = (0, 0)
                

                # Connect the nodes
                node_tree.links.new(texture_coord_node.outputs['Generated'], mapping_node.inputs['Vector'])
                node_tree.links.new(mapping_node.outputs['Vector'], env_texture_node.inputs['Vector'])
                node_tree.links.new(env_texture_node.outputs['Color'], background_node_2.inputs['Color'])
                node_tree.links.new(background_node_2.outputs['Background'], mix_shader_node.inputs[2])  # Input for Shader 2
                node_tree.links.new(background_node_1.outputs['Background'], mix_shader_node.inputs[1])  # Input for Shader 1
                node_tree.links.new(mix_shader_node.outputs['Shader'], world_output_node.inputs['Surface'])
                node_tree.links.new(light_path_node.outputs['Is Camera Ray'], background_node_1.inputs['Color'])  # Mix factor
                # Optional: Set additional node properties like background strength from config
                if 'background_strength' in self.config:
                    background_node_1.inputs['Strength'].default_value = self.config['background_strength']

                if 'environment_strength' in self.config:
                    background_node_2.inputs['Strength'].default_value = self.config.get('environment_strength')


                if 'hdri_rotation' in self.config:
                    # The rotation should be in radians for Blender, so converting degrees to radians if necessary
                    from math import radians
                    rotation = self.config['hdri_rotation']
                    rotation_radians = [radians(rotation.get('x', 0)), radians(rotation.get('y', 0)), radians(rotation.get('z', 0))]
                    mapping_node.inputs['Rotation'].default_value = rotation_radians
                    print(f"HDRI rotation applied: {rotation_radians}")    
                
                print("World environment node setup complete.")
            except Exception as e:
                print(f"Failed to create world environment: {e}")
#new light script below 
# import bpy
# from utils import *

# '''
# Properties for Lights(Cycles) :
#     1) Internsity(Power) : 420
#     2) Radius : 2meter
#     3) Max Bounce : 256
#     4) Spot Size : 60 Degree(
#         Shadow Casting: ON
#         Soft Fall off: )
# Properties for HDRI:
#     1) Rotation : x = -5.4 , y = 0, z = 200(Degrees)
#     2) Strength : 0.5
#     3) HDRI Image : Meadow_1
# '''

# class Light:
#     def __init__(self, config):
#         self.config = config
#         if "type" in self.config and self.config['type'] in ['POINT', 'SUN', 'SPOT', 'AREA']:
#             self.light = self.create_light()
#         else:
#             print("No valid light type specified. Skipping light creation.")
        
#         # If environment_image is provided, create the world environment
#         if "environment_image" in self.config:
#             self.create_world_environment()

#     def create_light(self):
#         bpy.ops.object.light_add(type=self.config['type'], location=self.config['location'])
#         light = bpy.context.object
#         light.name = self.config['name']
#         light.scale = self.config['scale']
#         light.data.color = self.config['color']
#         light.data.energy = self.config['power']
#         light.data.diffuse_factor = self.config['diffuse']
#         light.data.specular_factor = self.config['specular']
#         light.data.volume_factor = self.config['volume']
#         light.data.shadow_soft_size = self.config['radius']
#         if self.config['type'] == 'SPOT':
#             light.data.spot_size = self.config['spot_size']
#             light.data.spot_blend = self.config['spot_blend']
#         return light

#     def create_world_environment(self):
#             try:
#                 image_path=replace_placeholders(self.config['environment_image'])
#                 print(f"Creating world environment texture with image: {image_path}")
                
#                 # Ensure we're editing the world nodes
#                 world = bpy.context.scene.world
#                 if not world.use_nodes:
#                     world.use_nodes = True
#                 node_tree = world.node_tree
#                 nodes = node_tree.nodes
                
#                 # Clear existing nodes
#                 for node in nodes:
#                     nodes.remove(node)
#                 print("Existing world nodes cleared.")

#                 # Add the necessary nodes
#                 texture_coord_node = nodes.new(type='ShaderNodeTexCoord')
#                 mapping_node = nodes.new(type='ShaderNodeMapping')
#                 env_texture_node = nodes.new(type='ShaderNodeTexEnvironment')
#                 background_node_1 = nodes.new(type='ShaderNodeBackground')
#                 background_node_2 = nodes.new(type='ShaderNodeBackground')
#                 mix_shader_node = nodes.new(type='ShaderNodeMixShader')
#                 light_path_node = nodes.new(type='ShaderNodeLightPath')
#                 world_output_node = nodes.new(type='ShaderNodeOutputWorld')
#                 # Set up the environment texture with the image from the JSON
#                 env_texture_node.image = bpy.data.images.load(image_path)

#                 # Position nodes (optional but useful for organization)
#                 texture_coord_node.location = (-1000, 0)
#                 mapping_node.location = (-800, 0)
#                 env_texture_node.location = (-600, 0)
#                 background_node_1.location = (-400, 200)
#                 background_node_2.location = (-400, -200)
#                 mix_shader_node.location = (-200, 0)
#                 light_path_node.location = (-600, 400)
#                 world_output_node.location = (0, 0)
                

#                 # Connect the nodes
#                 node_tree.links.new(texture_coord_node.outputs['Generated'], mapping_node.inputs['Vector'])
#                 node_tree.links.new(mapping_node.outputs['Vector'], env_texture_node.inputs['Vector'])
#                 node_tree.links.new(env_texture_node.outputs['Color'], background_node_2.inputs['Color'])
#                 node_tree.links.new(background_node_2.outputs['Background'], mix_shader_node.inputs[2])  # Input for Shader 2
#                 node_tree.links.new(background_node_1.outputs['Background'], mix_shader_node.inputs[1])  # Input for Shader 1
#                 node_tree.links.new(mix_shader_node.outputs['Shader'], world_output_node.inputs['Surface'])
#                 node_tree.links.new(light_path_node.outputs['Is Camera Ray'], mix_shader_node.inputs['Fac'])  # Mix factor
#                 # Optional: Set additional node properties like background strength from config
#                 if 'background_strength' in self.config:
#                     background_node_1.inputs['Strength'].default_value = self.config['background_strength']

#                 if 'environment_strength' in self.config:
#                     background_node_2.inputs['Strength'].default_value = self.config.get('environment_strength')


#                 if 'hdri_rotation' in self.config:
#                     # The rotation should be in radians for Blender, so converting degrees to radians if necessary
#                     from math import radians
#                     rotation = self.config['hdri_rotation']
#                     rotation_radians = [radians(rotation.get('x', 0)), radians(rotation.get('y', 0)), radians(rotation.get('z', 0))]
#                     mapping_node.inputs['Rotation'].default_value = rotation_radians
#                     print(f"HDRI rotation applied: {rotation_radians}")    
                
#                 print("World environment node setup complete.")
#             except Exception as e:
#                 print(f"Failed to create world environment: {e}")
