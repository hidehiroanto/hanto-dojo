#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import os
import time
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.utils import make_grid
import warnings

MODELS_DIR = '/challenge/models'
DATA_DIR = '/challenge/data'
IMAGES_DIR = '/challenge/images'
DEFAULT_MODEL = 'denoiser'
BATCH_SIZE = 0x40

device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
test_dataset = datasets.MNIST(root=DATA_DIR, train=False, transform=transform)
testloader = DataLoader(dataset=test_dataset, batch_size=BATCH_SIZE, shuffle=False)
criterion = nn.SmoothL1Loss()

def load_model(model_name):
    model_path = os.path.join(MODELS_DIR, model_name + '.pt')
    if not os.path.isfile(model_path):
        raise FileNotFoundError(f'Model {model_name} not found in {MODELS_DIR}')
    return torch.load(model_path)

def add_noise(img):
    noise = torch.randn(img.size()).to(device) * 0.2
    noisy_img = img + noise
    return noisy_img

def testing_loop(model_name: str, model: nn.Module):
    images_subdir = os.path.join(IMAGES_DIR, model_name, str(int(time.time())))
    os.makedirs(images_subdir, exist_ok=True)

    model = model.to(device)
    model.eval()
    test_loss = 0
    with torch.no_grad():
        for batch_index, (batch_data, _) in enumerate(testloader):
            original_img = batch_data.view(batch_data.size(0), -1).to(device)
            noisy_img = add_noise(original_img)
            denoised_img = model(noisy_img)
            test_loss += criterion(original_img, denoised_img).item()

            images = [original_img, noisy_img, denoised_img]
            grid_images = [transforms.ToPILImage()(make_grid(img.view(img.shape[0], 1, 28, 28))) for img in images]
            grid_images[0].save(os.path.join(images_subdir, f'batch_{batch_index}_original.png'))
            grid_images[1].save(os.path.join(images_subdir, f'batch_{batch_index}_noisy.png'))
            grid_images[2].save(os.path.join(images_subdir, f'batch_{batch_index}_denoised.png'))

        test_loss /= len(testloader)
        print(f'{model_name} test loss: {test_loss:.4f}')

if __name__ == '__main__':
    warnings.filterwarnings('ignore', category=FutureWarning)
    model_name = input('Enter the model name (press Enter for default): ')
    if not model_name:
        model_name = DEFAULT_MODEL
    model = load_model(model_name)
    if isinstance(model, nn.Module):
        print(f'Model {model_name} loaded successfully.')
        testing_loop(model_name, model)
    else:
        print(f'{model_name} is not a valid PyTorch model: {model}')
