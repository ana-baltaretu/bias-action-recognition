### Setup conda

```
conda create -n blender_cubes python=3.11 -y
conda activate blender_cubes
conda install joblib -y
```


### Possible errors

<details>
  <summary>ModuleNotFoundError: No module named 'joblib'</summary>

```
"C:\Program Files\Blender Foundation\Blender 4.2\4.2\python\bin\python.exe" -m ensurepip
"C:\Program Files\Blender Foundation\Blender 4.2\4.2\python\bin\python.exe" -m pip install joblib
```

or

directly in Blender
```
import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "pip", "install", "joblib"])
```

or force Blender to get joblib from another place, add this to start of your file

```
import site
site.addsitedir(r"C:\Users\<your_user>\AppData\Roaming\Python\Python311\site-packages")
import joblib
```

</details>


C:\Program Files\Blender Foundation\Blender 4.2\4.2\python\bin\python.exe -m pip install --upgrade pip

"C:\Program Files\Blender Foundation\Blender 4.2\4.2\python\bin\python.exe" -m pip install --upgrade pip


### Running the code

```
blender --background --python red_blue_cubes_orbiting_around_z.py -- --save "./animation_output/test_parallel/orbiting"
```

Or you can run the `run_orbiting.sh` from GitBash
Run also `sh run_bouncing.sh`