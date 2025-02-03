## Dataset format

For each experiment you should have the data in the following folder structure
```
experiment_name/
├── sub_experiment/             # Different variations of the same experiment
│   ├── bouncing/               # Example label for an action
│   │   ├── bouncing_1.mp4      # Video with no problems (e.g. only Red-Blue) -> can be used for train/test
│   │   ├── bouncing_2.mp4          # Video with matching problem counterpart -> used for validation
│   │   └── ...                 
│   ├── bouncing_green/         # Example label for an action with problems (in this case "_green")
│   │   ├── bouncing_2.mp4      # Same as bouncing_2, but also has green cubes
│   │   ├── bouncing_17.mp4         # Only a subset of "bouncing" match with the "bouncing_green"
│   │   └── ...                 
│   └── ... 
└── ... 
```

