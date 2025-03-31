Cuda 12.1-12.6

```
conda create -n random_env38 python=3.8 -y
conda activate random_env38
pip install torch==2.1.0+cu121 torchvision==0.16.0+cu121 torchaudio==2.1.0+cu121 --index-url https://download.pytorch.org/whl/cu121

```