## Relevant cluster commands
Access the folder inside the cluster:  
`cd /tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/parallel_cube_render`

Build the apptainer image (only once OR when you change the .def file):  
`apptainer build render_cubes.sif render_cubes.def`

Running a job:  
`sbatch render_cubes.sbatch`

Copy files from cluster to a local folder (run from WSL):
```
scp -r daic:/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/parallel_cube_render/results /mnt/c/Users/anaba/OneDrive/Desktop/cluster/
```

Checking jobs:
- See jobs that I am running `squeue --me`
- See more details on a currently running job `scontrol show job <job_ID> | grep RunTime` (specifically runtime here)
