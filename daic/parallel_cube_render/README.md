

`cd /tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/parallel_cube_render`

`apptainer build render_cubes.sif render_cubes.def`

`sbatch render_cubes.sbatch`

`scp daic:/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/parallel_cube_render/bouncing_3.mp4 /mnt/c/Users/anaba/OneDrive/Desktop/cluster/`

`scp daic:/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/parallel_cube_render/*.mp4 /mnt/c/Users/anaba/OneDrive/Desktop/cluster/`

### Checking jobs
```
squeue --me

scontrol show job <job_ID> | grep RunTime
```


### TODOs

- [x] Generate camera positions (plane, input: random seed, input: plane distance, plane angle)
- [ ] Generate combinations of amount of cubes (all possible, min 1 cube)
- [ ] Generate the scene_info.config file (list of rendering job info + extra file with each cube position)