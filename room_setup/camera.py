import bpy

'''
Camera Parameters(Bottle Camera Paramter)
    1) Resolution : "1440/1200"
    2) Aspect ratio : 4:3
    3) Focal Length : 18
    4) Clip Start : 0.1
    5) Clip End : logic(10, 20)
    6) Placement : As per wall 
    7) Samples : 256
    8) Render Engine : Cycles
    9) Exposure : 1
    10) De-Noise : True
'''

class Camera:
    def __init__(self, config, name="Camera"):
        self.config = config
        self.name = name
        self.camera = self.create_camera()

    def create_camera(self):
        bpy.ops.object.camera_add(location=self.config['location'], rotation=self.config['rotation'])
        camera = bpy.context.object
        camera.name = self.name
        camera.data.lens = self.config['focal_length']
        camera.data.clip_start = self.config['clip_start']
        camera.data.clip_end = self.config['clip_end']
        bpy.context.scene.camera = camera
        return camera

    def set_render_settings(self):
        bpy.context.scene.render.engine = self.config['render_engine']
        bpy.context.scene.cycles.samples = self.config['samples']
        bpy.context.scene.cycles.use_denoising = self.config['noise']
        bpy.context.scene.view_settings.exposure = self.config['exposure']

        bpy.context.scene.cycles.device = 'GPU'  # Use GPU for Cycles

        # Set device preferences to use the GPU
        prefs = bpy.context.preferences
        cycles_prefs = prefs.addons['cycles'].preferences
        cycles_prefs.compute_device_type = 'CUDA'  
        prefs.addons['cycles'].preferences.get_devices()
        
        
        for device in cycles_prefs.devices:
            device.use = True  

    def set_camera_view(self):
        bpy.context.scene.camera = self.camera
        bpy.context.view_layer.objects.active = self.camera

    def render(self, filepath):
        bpy.context.scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)

    def set_render_resolution(self, resolution_x=1440, resolution_y=1200, resolution_percentage=100):
        bpy.context.scene.render.resolution_x = resolution_x
        bpy.context.scene.render.resolution_y = resolution_y
        bpy.context.scene.render.resolution_percentage = resolution_percentage

    @staticmethod
    def switch_to_view(view):
        if view == 'TOP':
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.region_3d.view_perspective = 'ORTHO'
                            space.region_3d.view_rotation = (1.0, 0.0, 0.0, 0.0)
        elif view == 'FRONT':
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.region_3d.view_perspective = 'ORTHO'
                            space.region_3d.view_rotation = (1.0, 0.0, 0.0, 0.0)
