import torch
print(torch.cuda.is_available())       # Should be True
print(torch.version.cuda)              # Should be '12.1'
print(torch.cuda.get_device_name(0))   # Your GPU's name


import pytorchvideo.models

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)