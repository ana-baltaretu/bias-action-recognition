### **Just Apptainer**

**Build the Image**
```bash
apptainer build test_sine_wave.sif test_sine_wave.def
```

**Test the Image**
Make sure the image works by generating the file:
```bash
apptainer run test_sine_wave.sif test_sine_wave.py
```

---

### **With SLURM**

**Run the Job**
Submit the SLURM job using the image:
```bash
sbatch test_slurm_sine_wave.sbatch
```

---

### **Getting Files from the Cluster**

**Get the Image File**
```bash
scp daic:/home/nfs/abaltaretu/bias-action-recognition/daic/test_sine_wave/test_sine_wave.sif \
    /mnt/c/Users/anaba/OneDrive/Desktop/cluster/
```

**Get the Generated `sine_wave.png`**
```bash
scp daic:/home/nfs/abaltaretu/bias-action-recognition/daic/test_sine_wave/sine_wave.png \
    /mnt/c/Users/anaba/OneDrive/Desktop/cluster/
```

---

**Notes**
- Ensure that you have Apptainer and SLURM set up properly on your system.
- Use the appropriate paths when retrieving files from the cluster.

