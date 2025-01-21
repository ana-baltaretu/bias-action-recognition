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
6. `apptainer exec --nv test_generate_cube.sif ls /dev/nvidia*`
7. `apptainer exec --nv test_generate_cube.sif env | grep -E "CUDA|NVIDIA"`
8. `apptainer exec --nv test_generate_cube.sif nvidia-smi`

   

### NOTE
I also tried running this command just normally in the login node and it worked (no interactive session)???
Command: `apptainer exec --nv test_generate_cube.sif python3 -c "import torch; print(torch.cuda.get_device_name(0))"`  

Output:
```
Quadro K2200
```

1. `nvidia-smi`
```
Wed Jan 15 17:45:43 2025
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.90.07              Driver Version: 550.90.07      CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  Quadro K2200                   On  |   00000000:08:00.0 Off |                  N/A |
| 43%   32C    P8              1W /   39W |       2MiB /   4096MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
```


### OTHERS
```
apptainer run --fakeroot --nv --bind /dev/dri:/dev/dri test_generate_cube.sif test_generate_cube.py

Even after making sandbox
apptainer build --sandbox test_generate_cube_sandbox test_generate_cube.sif
```


```
apptainer run --nv test_generate_cube.sif nvidia-smi

Blender 4.2.2 LTS (hash c03d7d98a413 built 2024-09-24 00:09:56)
could not get a list of mounted file-systems
OSError: Python file "/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/test_basic_blender/nvidia-smi" could not be opened: No such file or directory
Blender quit
```


```
apptainer run --nv --bind /dev/dri:/dev/dri test_generate_cube.sif nvidia-smi

Blender 4.2.2 LTS (hash c03d7d98a413 built 2024-09-24 00:09:56)
could not get a list of mounted file-systems
OSError: Python file "/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/test_basic_blender/nvidia-smi" could not be opened: No such file or directory
Blender quit
```

```
ls -l /dev/dri/

total 0
crw-rw----. 1 root video 226,   0 Sep 16 08:29 card0
crw-rw----. 1 root video 226,   1 Sep 16 08:29 card1
crw-rw----. 1 root video 226, 128 Sep 16 08:29 renderD128
```

```
groups

domain users ewi-insy ewi-insy-prb ewi-insy-students daic
```

```
blender --background --python-expr "import bpy; print(bpy.context.preferences.addons['cycles'].preferences.compute_device_type)"

AL lib: (WW) alc_initconfig: Failed to initialize backend "pulse"
ALSA lib confmisc.c:767:(parse_card) cannot find card '0'
ALSA lib conf.c:4568:(_snd_config_evaluate) function snd_func_card_driver returned error: Permission denied
ALSA lib confmisc.c:392:(snd_func_concat) error evaluating strings
ALSA lib conf.c:4568:(_snd_config_evaluate) function snd_func_concat returned error: Permission denied
ALSA lib confmisc.c:1246:(snd_func_refer) error evaluating name
ALSA lib conf.c:4568:(_snd_config_evaluate) function snd_func_refer returned error: Permission denied
ALSA lib conf.c:5047:(snd_config_expand) Evaluate error: Permission denied
ALSA lib pcm.c:2565:(snd_pcm_open_noupdate) Unknown PCM default
AL lib: (EE) ALCplaybackAlsa_open: Could not open playback device 'default': Permission denied
unknown argument, loading as file: --python-expr
read blend: /tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/test_basic_blender/--python-expr
Warning: Unable to open '/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/test_basic_blender/--python-expr': No such file or directory
Blender quit
```


### Cool stuff

```
-bash-4.2$ squeue --me
JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
11311299_[1-3] prb,insy,    cubes abaltare PD       0:00      1 (Resources)
```