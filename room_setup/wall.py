import bpy
import os
from utils.utils import replace_placeholders
class Wall:
    def __init__(self, name, location, scale, color, texture, texture_transform):
        self.name = name
        self.location = location
        self.scale = scale
        self.color = color
        self.texture = texture
        self.texture_transform = texture_transform
        self.object = self.create_wall()

    def create_wall(self):
        bpy.ops.mesh.primitive_cube_add(size=2, location=self.location)
        wall = bpy.context.object
        wall.name = self.name
        wall.scale = self.scale
        self.apply_material(wall)
        return wall

    def apply_material(self, wall):
        # Create a new material and enable nodes
        mat = bpy.data.materials.new(name=self.name + "_Material")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")

        # Nodes: Texture Coordinate and Mapping
        tex_coord = mat.node_tree.nodes.new('ShaderNodeTexCoord')
        mapping = mat.node_tree.nodes.new('ShaderNodeMapping')
        mat.node_tree.links.new(mapping.inputs['Vector'], tex_coord.outputs['UV'])

        if isinstance(self.texture, str):
            print(f"Error: Texture data should be a dictionary but is a string: {self.texture}")
            self.texture = {}

    # Ensure texture_transform is a dictionary
        if isinstance(self.texture_transform, str):
            print(f"Error: Texture transform data should be a dictionary but is a string: {self.texture_transform}")
            self.texture_transform = {}

        # Retrieve texture paths from JSON or other sources
        base_color_path = replace_placeholders(self.texture.get('base_color', ''))
        roughness_path = replace_placeholders(self.texture.get('roughness', ''))
        normal_path = replace_placeholders(self.texture.get('normal', ''))
        displacement_path = replace_placeholders(self.texture.get('displacement', ''))

        # Scale, displacement, and rotation values from JSON
        scale = self.texture_transform.get('scale', [1, 1, 1])
        location = self.texture_transform.get('location', [0, 0, 0])
        rotation = self.texture_transform.get('rotation', [0, 0, 0])

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

        # Load textures and connect them
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

            # Assign material to the wall object
        if wall.data.materials:
            wall.data.materials[0] = mat
        else:
            wall.data.materials.append(mat)
        print(f"Material applied with textures for wall: {self.name}")