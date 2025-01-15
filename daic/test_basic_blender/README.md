``https://download.blender.org/release/Blender4.2/blender-4.2.2-linux-x64.tar.xz``

``cd /tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/test_basic_blender``
Note: the default folder doesn't have enough space for Blender image

```bash
apptainer build test_generate_cube.sif test_generate_cube.def
OR
Log:
apptainer build --force test_generate_cube.sif test_generate_cube.def > debugging_logs/container_build_log 2>&1
```

```bash
apptainer run test_generate_cube.sif test_generate_cube.py
OR
apptainer run --nv test_generate_cube.sif test_generate_cube.py
OR
apptainer run --nv --bind /dev/dri:/dev/dri test_generate_cube.sif test_generate_cube.py
OR
blender --background --python test_generate_cube.py
```

```bash
sbatch test_generate_cube.sbatch
```

```
squeue --me
```

test apptainer local "/mnt/c/Users/anaba/OneDrive/Desktop/Master Thesis/bias-action-recognition/daic/test_basic_blender"

python3 -c "import torch; print(torch.cuda.get_device_name(0))"

## Interactive session
```
sinteractive
sinteractive --ntasks=2 --mem=2G --time=00:05:00
```


## Commands I ran in Interactive session

1. `sinteractive --ntasks=2 --mem=2G --time=00:10:00`
2. `module use /opt/insy/modulefiles`
3. Command: `apptainer exec --nv test_generate_cube.sif python3 -c "import torch; print(torch.cuda.get_device_name(0))"`

   Output:
   ```
      WARNING: Could not find any nv files on this host!
       Traceback (most recent call last):
         File "<string>", line 1, in <module>
         File "/usr/local/lib/python3.10/dist-packages/torch/cuda/__init__.py", line 493, in get_device_name
           return get_device_properties(device).name
         File "/usr/local/lib/python3.10/dist-packages/torch/cuda/__init__.py", line 523, in get_device_properties
           _lazy_init()  # will define _get_device_properties
         File "/usr/local/lib/python3.10/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
           torch._C._cuda_init()
       RuntimeError: Found no NVIDIA driver on your system. Please check that you have an NVIDIA GPU and installed a driver from http://www.nvidia.com/Download/index.aspx
   ```
4. Command: `apptainer exec --nv test_generate_cube.sif python3 -c "import torch; print(torch.cuda.is_available())"`

   Output: 
   ```
   False
   ```
5. `apptainer exec --nv test_generate_cube.sif python3 -c "import ctypes; ctypes.CDLL('libcudart.so')"`
   ```
   ```
6. `apptainer exec --nv test_generate_cube.sif ls /dev/nvidia*`
   ```
   ```
7. `apptainer exec --nv test_generate_cube.sif env | grep -E "CUDA|NVIDIA"`
   ```
   ```
8. `apptainer exec --nv test_generate_cube.sif nvidia-smi`
   ```
   ```
9. ``
   ```
   ```
10. ``
    ```
    ```
11. ``
    ```
    ```
12. ``
    ```
    ```
   

### NOTE
I also tried running this command just normally in the login node and it worked (no interactive session)???
Command: `apptainer exec --nv test_generate_cube.sif python3 -c "import torch; print(torch.cuda.get_device_name(0))"`  

Output:
```
Quadro K2200
```
