### Training the model on the Cluster
Access the folder inside the cluster:  
`cd /tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/bias-action-recognition/daic/ConvLSTM_model_training`

Build the apptainer image (only once OR when you change the .def file):  
```
sinteractive --ntasks=1 --mem=2G --time=00:05:00 --partition=prb,insy,general
apptainer build model_training.sif model_training.def
```

Run interactive shell to test imports (only for testing setup):
`apptainer shell --nv model_training.sif`