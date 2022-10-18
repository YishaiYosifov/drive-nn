from torch.nn import functional
from torch import nn, optim

import torch
import os

class Linear_QNET(nn.Module):
    def __init__(self, inputSize, hiddenSize, outputSize):
        super().__init__()

        self.linear1 = nn.Linear(inputSize, hiddenSize)
        self.linear2 = nn.Linear(hiddenSize, outputSize)
    
    def forward(self, x):
        x = functional.relu(self.linear1(x))
        x = self.linear2(x)
        return x
    
    def save(self, fileName = "model.pth"):
        modelFolder = "./model"
        if not os.path.exists(modelFolder): os.makedirs(modelFolder)

        fileName = os.path.join(modelFolder, fileName)
        torch.save(self, fileName)

class QTrainer:
    def __init__(self, model, learningRate, gamma):
        self.model = model
        self.learningRate = learningRate
        self.gamma = gamma
        
        self.optimizer = optim.Adam(model.parameters(), lr=learningRate)
        self.loss = nn.MSELoss()
    
    def train_step(self, state, action, reward, nextState, gameOver):
        state = torch.tensor(state, dtype=torch.float)
        nextState = torch.tensor(nextState, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            nextState = torch.unsqueeze(nextState, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            gameOver = (gameOver,)
        
        prediction = self.model(state)

        target = prediction.clone()
        for index in range(len(gameOver)):
            QNew = reward[index]
            if not gameOver[index]: QNew = reward[index] + self.gamma * torch.max(self.model(nextState[index]))

            target[index][torch.argmax(action).item()] = QNew
        
        self.optimizer.zero_grad()
        loss = self.loss(target, prediction)
        loss.backward()

        self.optimizer.step()