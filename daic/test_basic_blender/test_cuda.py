import bpy


# Enable CUDA or OptiX
bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'


gpus = bpy.context.preferences.addons['cycles'].preferences.get_devices()
print(gpus)

print(gpus[0])

# Set Cycles to use GPU rendering
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.feature_set = 'SUPPORTED'  # Use supported features for faster rendering
