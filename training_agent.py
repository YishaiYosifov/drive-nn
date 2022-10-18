from collections import deque
from ai_game import AICar
from util import plot
from model import *

import random
import torch
import numpy
import os

MAX_MEMORY = 100000
BATCH_SIZE = 1000
LEARNING_RATE = 0.001

class Agent:
    def __init__(self):
        self.numberOfGames = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)

        if os.path.exists(r"model\model.pth"):
            self.model = torch.load(r"model\model.pth")
            self.model.eval()
        else: self.model = Linear_QNET(5, 256, 3)

        self.trainer = QTrainer(self.model, LEARNING_RATE, self.gamma)

    def get_state(self, game):
        state = game.get_state()

        return numpy.array(state, dtype=numpy.int32)

    def remember(self, state, action, reward, nextState, gameOver): self.memory.append((state, action, reward, nextState, gameOver))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE: sample = random.sample(self.memory, BATCH_SIZE)
        else: sample = self.memory

        states, actions, rewards, nextStates, gameOvers = zip(*sample)
        self.trainer.train_step(states, actions, rewards, nextStates, gameOvers)

    def train_short_memory(self, state, action, reward, nextState, gameOver): self.trainer.train_step(state, action, reward, nextState, gameOver)

    def get_action(self, state):
        self.epsilon = 0 - self.numberOfGames
        finalMove = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            finalMove[move] = 1
        else:
            state = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state)
            move = torch.argmax(prediction).item()
            finalMove[move] = 1
        return finalMove

def train():
    plotScores = []
    plotMeanScore = []
    totalScore = 0
    record = 0

    agent = Agent()
    game = AICar()

    while True:
        oldState = agent.get_state(game)
        finalMove = agent.get_action(oldState)

        reward, gameOver, score = game.render(finalMove)
        newState = agent.get_state(game)

        agent.train_short_memory(oldState, finalMove, reward, newState, gameOver)
        agent.remember(oldState, finalMove, reward, newState, gameOver)

        if gameOver:
            game.reset()
            agent.numberOfGames += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print(f"Game: {agent.numberOfGames}\nScore: {score}\nRecord: {record}")

            plotScores.append(score)
            totalScore += score
            meanScore = totalScore / agent.numberOfGames
            plotMeanScore.append(meanScore)
            plot(plotScores, plotMeanScore)


if __name__ == "__main__": train()