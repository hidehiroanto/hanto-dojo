#!/usr/bin/exec-suid -- /usr/bin/python3 -I

from math import sqrt
import os
import time
import torch
from torch import nn
from torch.optim import Adam as AdamDoupe
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.utils import make_grid
from warnings import filterwarnings

MODELS_DIR = '/challenge/models'
DATA_DIR = '/challenge/data'
IMAGES_DIR = '/challenge/images'
DEFAULT_MODEL = 'convolutional_autoencoder'
BATCH_SIZE = 0x64
NUM_EPOCHS = 0x10
NOISE_FACTOR = 0.125

device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')
train_dataset = datasets.MNIST(DATA_DIR, True, transforms.ToTensor())
test_dataset = datasets.MNIST(DATA_DIR, False, transforms.ToTensor())
train_loader = DataLoader(train_dataset, BATCH_SIZE, True)
test_loader = DataLoader(test_dataset, BATCH_SIZE, False)
loss_function = nn.MSELoss()
optimizer_class = AdamDoupe

class LinearAutoencoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.relu = nn.ReLU()
        self.encoder = nn.Sequential(
            nn.Linear(0x310, 0x100),
            self.relu,
            nn.Linear(0x100, 0x40),
            self.relu,
            nn.Linear(0x40, 0x10),
            self.relu
        )
        self.decoder = nn.Sequential(
            nn.Linear(0x10, 0x40),
            self.relu,
            nn.Linear(0x40, 0x100),
            self.relu,
            nn.Linear(0x100, 0x310),
            nn.Sigmoid()
        )

    def forward(self, img: torch.Tensor):
        return self.decoder(self.encoder(img))

class ConvolutionalAutoencoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.relu = nn.ReLU()
        self.encoder = nn.Sequential(
            nn.Conv2d(1, 0x10, 3, 2, 1),
            self.relu,
            nn.Conv2d(0x10, 0x20, 3, 2, 1),
            self.relu,
            nn.Conv2d(0x20, 0x40, 7)
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(0x40, 0x20, 7),
            self.relu,
            nn.ConvTranspose2d(0x20, 0x10, 3, 2, 1, 1),
            self.relu,
            nn.ConvTranspose2d(0x10, 1, 3, 2, 1, 1),
            nn.Sigmoid()
        )

    def forward(self, img: torch.Tensor):
        img = self.decoder(self.encoder(img.view(-1, 1, 0x1c, 0x1c)))
        return img.view(img.size(0), -1)

available_models = {
    'linear_autoencoder': LinearAutoencoder,
    'convolutional_autoencoder': ConvolutionalAutoencoder
}

def load_model(model_name: str) -> nn.Module:
    model_path = os.path.join(MODELS_DIR, model_name + '.pt')
    if not os.path.isfile(model_path):
        raise FileNotFoundError(f'Model {model_name} not found in {MODELS_DIR}')
    load_data = torch.load(model_path)
    if isinstance(load_data, nn.Module):
        model = load_data
    else:
        raise TypeError(f'{model_name} is not a valid model: {load_data}')
    print(f'Model {model_name} loaded from {model_path}')
    return model.to(device)

def save_model(model: nn.Module, model_name: str):
    model_path = os.path.join(MODELS_DIR, model_name + '.pt')
    torch.save(model, model_path)
    print(f'Model {model_name} saved to {model_path}')

def add_noise(img: torch.Tensor) -> torch.Tensor:
    return torch.clamp(img + NOISE_FACTOR * torch.randn(img.size()).to(device), 0, 1)

def make_grids(images: torch.Tensor) -> list:
    make_pillow = transforms.ToPILImage()
    row_size = round(sqrt(BATCH_SIZE))
    resized_images = [img.view(-1, 1, 0x1c, 0x1c) for img in images]
    return [make_pillow(make_grid(img, row_size)) for img in resized_images]

def train_model(model_name: str):
    if model_name not in available_models:
        raise ValueError(f'Model {model_name} not available. Available models: {list(available_models.keys())}')
    model = available_models[model_name]().to(device)
    optimizer = optimizer_class(model.parameters())
    for epoch in range(NUM_EPOCHS):
        print(f'Epoch {epoch + 1}/{NUM_EPOCHS}')
        for batch_data, _ in train_loader:
            original_img = batch_data.view(batch_data.size(0), -1).to(device)
            noisy_img = add_noise(original_img)
            denoised_img = model(noisy_img)
            train_loss = loss_function(original_img, denoised_img)
            optimizer.zero_grad()
            train_loss.backward()
            optimizer.step()
        print(f'Training loss: {train_loss.item()}')

        validation_loss = 0
        with torch.no_grad():
            for batch_data, _ in test_loader:
                original_img = batch_data.view(batch_data.size(0), -1).to(device)
                noisy_img = add_noise(original_img)
                denoised_img = model(noisy_img)
                validation_loss += loss_function(original_img, denoised_img).item()
        validation_loss /= len(test_loader)
        print(f'Validation loss: {validation_loss}')
    save_model(model, model_name)

def test_model(model_name: str):
    model = load_model(model_name)
    images_subdir = os.path.join(IMAGES_DIR, model_name, str(int(time.time())))
    os.makedirs(images_subdir, exist_ok=True)
    model.eval()
    test_loss = 0
    with torch.no_grad():
        for batch_index, (batch_data, _) in enumerate(test_loader):
            original_img = batch_data.view(batch_data.size(0), -1).to(device)
            noisy_img = add_noise(original_img)
            denoised_img = model(noisy_img)
            test_loss += loss_function(original_img, denoised_img).item()

            grid_images = make_grids([original_img, noisy_img, denoised_img])
            grid_images[0].save(os.path.join(images_subdir, f'{batch_index:02d}_original.png'))
            grid_images[1].save(os.path.join(images_subdir, f'{batch_index:02d}_with_noise.png'))
            grid_images[2].save(os.path.join(images_subdir, f'{batch_index:02d}_without_noise.png'))
        test_loss /= len(test_loader)
        print(f'Testing loss: {test_loss}')
        print(f'Images saved to {images_subdir}')

if __name__ == '__main__':
    filterwarnings('ignore', category=FutureWarning)
    filterwarnings('ignore', category=UserWarning)
    print(f'Using device: {device}')
    model_name = input('Enter the model name (press Enter for default): ')
    if not model_name:
        model_name = DEFAULT_MODEL
    train_choice = input('Do you want to train the model? (y/N): ')
    if train_choice.strip().lower().startswith('y'):
        train_model(model_name)
    test_choice = input('Do you want to test the model? (y/N): ')
    if test_choice.strip().lower().startswith('y'):
        test_model(model_name)
