### Training the model on the Cluster

Build the apptainer image (only once OR when you change the .def file):  
`apptainer build model_training.sif model_training.def`

Run interactive shell to test imports (only for testing setup):
`apptainer shell --nv model_training.sif`