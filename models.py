import torch
import torch.nn as nn
import torch_geometric.nn as gnn

class HabitatGAN(nn.Module):
    def __init__(self):
        super(HabitatGAN, self).__init__()
        self.generator = nn.Sequential(
            nn.Linear(100, 512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, 1024),
            nn.LeakyReLU(0.2),
            nn.Linear(1024, 2048),
            nn.Tanh()
        )
        
        self.discriminator = nn.Sequential(
            nn.Linear(2048, 1024),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(1024, 512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, 1),
            nn.Sigmoid()
        )

class PINN(nn.Module):
    def __init__(self):
        super(PINN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(4, 128),
            nn.Tanh(),
            nn.Linear(128, 128),
            nn.Tanh(),
            nn.Linear(128, 1)
        )

class HabitatGNN(torch.nn.Module):
    def __init__(self):
        super(HabitatGNN, self).__init__()
        self.conv1 = gnn.GCNConv(in_channels=128, out_channels=64)
        self.conv2 = gnn.GCNConv(in_channels=64, out_channels=32)
        self.classifier = nn.Linear(32, 1)