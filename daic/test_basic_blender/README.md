``https://download.blender.org/release/Blender4.2/blender-4.2.2-linux-x64.tar.xz``

``cd /tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/test_basic_blender``, Note: the default folder doesn't have enough space for Blender image

```bash
apptainer build test_generate_cube.sif test_generate_cube.def
```

```bash
apptainer run test_generate_cube.sif test_generate_cube.py
apptainer run --nv test_generate_cube.sif test_generate_cube.py

```

```bash
sbatch test_generate_cube.sbatch
```

```
squeue --me
```

test apptainer local "/mnt/c/Users/anaba/OneDrive/Desktop/Master Thesis/bias-action-recognition/daic/test_basic_blender"

python3 -c "import torch; print(torch.cuda.get_device_name(0))"


### Commands for debugging (most give error, Apptainer image doesn't find NVIDIA driver)

```
apptainer exec test_generate_cube.sif python3 -c "import torch; print(torch.cuda.get_device_name(0))"
apptainer exec --nv test_generate_cube.sif python3 -c "import torch; print(torch.cuda.get_device_name(0))"

apptainer exec test_generate_cube.sif python3 -c "import torch; print(torch.cuda.is_available())"
apptainer exec --nv test_generate_cube.sif python3 -c "import torch; print(torch.cuda.is_available())"

apptainer exec --nv test_generate_cube.sif python3 -c "import torch; print(torch.version.cuda)"

apptainer exec --nv test_generate_cube.sif nvidia-smi

apptainer config dump | grep nvidia

apptainer exec --nv test_generate_cube.sif python3 -c "import ctypes; ctypes.CDLL('libcudart.so')"
apptainer exec --nv test_generate_cube.sif ls /dev/nvidia*
apptainer exec --nv test_generate_cube.sif env | grep -E "CUDA|NVIDIA"

apptainer exec --nv --bind /dev/nvidia0:/dev/nvidia0 --bind /dev/nvidiactl:/dev/nvidiactl --bind /dev/nvidia-uvm:/dev/nvidia-uvm test_generate_cube.sif python3 -c "import torch; print(torch.cuda.is_available())"

apptainer exec --nv test_generate_cube.sif python3 -c "import ctypes; ctypes.CDLL('libcudart.so').cudaGetDeviceCount"

# Create Driver nodes
sudo apt install nvidia-modprobe
sudo apt install nvidia-container-toolkit
sudo nvidia-modprobe -u -c=0 
```