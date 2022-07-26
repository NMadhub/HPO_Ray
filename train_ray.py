import os
from ray_lightning import RayPlugin
import torch
from torch.nn import functional as F
from torch.utils.data import DataLoader
from torchvision.datasets import MNIST
from torchvision import transforms
import pytorch_lightning as pl

class MNISTModel(pl.LightningModule):

    def __init__(self):
        super(MNISTModel, self).__init__()
        self.l1 = torch.nn.Linear(28 * 28, 10)

    def forward(self, x):
        return torch.relu(self.l1(x.view(x.size(0), -1)))

    def training_step(self, batch, batch_nb):
        x, y = batch
        loss = F.cross_entropy(self(x), y)
        tensorboard_logs = {'train_loss': loss}
        return {'loss': loss, 'log': tensorboard_logs}

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=0.02)

    def train_dataloader(self):
        train_loader = DataLoader(MNIST(os.getcwd(), train=True, download=True, transform=transforms.ToTensor()), batch_size=32)
        return train_loader

# variables for Ray around parallelism and hardware

# Initialize ray
#ray.init()

mnist_model = MNISTModel()

# Create Trainer and start training
plugin = RayPlugin(num_workers=4, num_cpus_per_worker=1, use_gpu=True)
trainer = pl.Trainer(gpus=1, progress_bar_refresh_rate=20, plugins=[plugin])
trainer.fit(mnist_model)
#trainer = pl.Trainer(gpus=1, progress_bar_refresh_rate=20)    
#trainer.fit(mnist_model, train_loader)  

