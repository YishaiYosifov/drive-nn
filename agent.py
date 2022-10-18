from ai_game import AICar

import torch

if __name__ == "__main__":

    model = torch.load(r"carmodel\model.pth")
    model.eval()

    game = AICar()
    gameOver = False
    while not gameOver:
        finalMove = [0, 0, 0]
        state = torch.tensor(game.get_state(), dtype=torch.float)
        prediction = model(state)
        move = torch.argmax(prediction).item()
        finalMove[move] = 1

        reward, gameOver, score = game.render(finalMove)
    print(score)