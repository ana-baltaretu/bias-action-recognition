import os
import sys
import numpy as np
import re

import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from torchvision.models import resnet152
import torchvision.transforms as transforms

from PIL import Image

import av
import time
import tqdm
import random
import datetime
import argparse
import glob

import itertools
import wandb

print("Imports successful!")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)
print("Cuda is available (using GPU?):", torch.cuda.is_available())

