import bpy


class Cutout:
    def __init__(self, name, location, scale, wall_obj):
        self.name = name
        self.location = location
        self.scale = scale
        self.wall_obj = wall_obj
        self.create_cutout()

    def create_cutout(self):
        # Create a cube to serve as the cutout shape
        bpy.ops.mesh.primitive_cube_add(size=2, location=self.location)
        cutout = bpy.context.object
        cutout.name = self.name
        cutout.scale = self.scale
        
        # Apply the boolean modifier to the wall
        mod_bool = self.wall_obj.modifiers.new(name=f"{self.name}_bool", type='BOOLEAN')
        mod_bool.operation = 'DIFFERENCE'
        mod_bool.object = cutout
        
        # Apply the modifier and remove the cutout object
        bpy.context.view_layer.objects.active = self.wall_obj
        bpy.ops.object.modifier_apply(modifier=mod_bool.name)
        bpy.data.objects.remove(cutout)