import torch
from torch import nn

class SiameseNet(nn.Module):
    def __init__(self):
        super(SiameseNet, self).__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(1, 64, 10), # 64@96*96
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2), #64@48*48
            nn.Conv2d(64, 128, 7),
            nn.ReLU(inplace=True), #128@42*52
            nn.MaxPool2d(2), #128@18*18
            nn.Conv2d(128,128,4),
            nn.ReLU(inplace=True), #128@18*18
            nn.MaxPool2d(2), #128@9*9
            nn.Conv2d(128,256,4),
            nn.ReLU(inplace=True), #256@6*6
        )
        self.liner = nn.Sequential(nn.Linear(9216, 4096), nn.Sigmoid)
        self.out = nn.Linear(4096, 1)
        
    def sub_forward(self, x):
        x = self.conv(x)
        x = x.view(x.size()[0], -1)
        x = self.liner(x)
        return x
    
    def forward(self, x1, x2):
        h1 = self.sub_forward(x1)
        h2 = self.sub_forward(x2)
        
        diff = torch.abs(h1-h2)
        
        scores = self.out(diff)
        return scores
    