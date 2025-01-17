import bpy


prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'CUDA'  # Or 'OPTIX' for newer NVIDIA GPUs
prefs.get_devices()
for device in prefs.devices:
    device.use = True
    print(f"Device: {device.name}, Type: {device.type}")
bpy.context.scene.cycles.device = 'GPU'