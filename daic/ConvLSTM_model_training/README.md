## Training the model on the Cluster
Access the folder inside the cluster:  
`cd /tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/ConvLSTM_model_training`

### Setup
Build the apptainer image (only once OR when you change the .def file):  
```
sinteractive --ntasks=1 --mem=4G --time=00:25:00 --partition=prb,insy,general
apptainer build model_training.sif model_training.def
```

Run interactive shell to test imports (only for testing setup):
`apptainer shell --nv model_training.sif`

Run python file:
`apptainer exec --nv model_training.sif python3 test_imports.py`

### General run
Running a job:  
`sbatch model_training.sbatch`

Copy files from cluster to a local folder (run from WSL):
```
scp -r daic:/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/ConvLSTM_model_training/results /mnt/c/Users/anaba/OneDrive/Desktop/cluster/
```

