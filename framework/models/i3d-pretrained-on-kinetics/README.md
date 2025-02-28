
- USING Conda environment `random_env37`

### Installation
Assuming CUDA 12.5 is installed, check CUDA version with `nvidia-smi`
Using Python 3.7

```
conda create --name random_env37 python=3.7
conda activate random_env37
pip install --upgrade mxnet
pip install --upgrade pip setuptools wheel
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu102
pip install --upgrade gluoncv
pip install decord
```

### Run
- `demo_gluon.py` to test Gluon installation
- `demo_I3D_action_recognition.py` to see how it performs on action recognition model
- `test_I3D_on_folder.py` to run on a folder of videos (I have it set to be the same action, but you can do whatever)

