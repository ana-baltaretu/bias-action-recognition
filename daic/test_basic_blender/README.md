``https://download.blender.org/release/Blender4.2/blender-4.2.2-linux-x64.tar.xz``

``cd /tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu``, Note: the default folder doesn't have enough space for Blender image

```bash
apptainer build test_generate_cube.sif test_generate_cube.def
```

```bash
apptainer run test_generate_cube.sif test_generate_cube.py
```

```bash
sbatch test_generate_cube.sbatch
```

```
squeue --me
```
