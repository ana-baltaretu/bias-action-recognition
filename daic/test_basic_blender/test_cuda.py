import bpy


# Enable CUDA or OptiX
bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'

# Ensure all GPUs are enabled
for device in bpy.context.preferences.addons['cycles'].preferences.get_devices():
    if device.type == 'CUDA' or device.type == 'OPTIX':
        device.use = True

# Set Cycles to use GPU rendering
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.feature_set = 'SUPPORTED'  # Use supported features for faster rendering
