# Just Apptainer
Build the image:
```apptainer build test_sine_wave.sif test_sine_wave.def```

Test image works to generate file:
```apptainer run test_sine_wave.sif```

# With SLURM
Run job with image:
```sbatch test_slurm_sine_wave.slurm```