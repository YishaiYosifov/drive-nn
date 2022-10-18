from sprites import *

import numpy
import torch
import time
import json
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame

WIDTH = 800
HEIGHT = 600
FPS = 60

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Car AI")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.model = torch.load(r"carmodel\model.pth")
        self.model.eval()
        
        self.reset()

    def reset(self):
        self.spritesGroup = pygame.sprite.Group()

        self.sprites = {
            "background": BasicSprite(
                0,
                {"center": (WIDTH / 2, HEIGHT / 2)},
                pygame.image.load(r"sprites\background.png").convert()
            ),
            "track": BasicSprite(
                0,
                {"center": (WIDTH / 2, HEIGHT / 2)},
                pygame.image.load(r"sprites\track.png").convert()
            ),
            "car-ai": Car(self.screen, pygame.image.load(r"sprites\aicar.png")),
            "car": Car(self.screen, pygame.image.load(r"sprites\car.png"))
        }
        for sprite in self.sprites.values(): self.spritesGroup.add(sprite)

        with open("goals.json", "r") as f: goalSettings = json.load(f)
        goalSurface = pygame.Surface((80, 10))
        goalSurface.fill((0, 255, 0))
        self.goals = []
        for goal in goalSettings:
            goal = BasicSprite(goal["direction"], goal["rect_attributes"], goalSurface)
            self.goals.append(goal)

        self.fps = FPS
        self.nextGoalIndex = 0
        self.lastDistance = pygame.math.Vector2(*self.sprites["car-ai"].position).distance_to(self.goals[self.nextGoalIndex].rect.center)
        self.checkForwardGoalIndex = 0
    
    def render(self) -> bool:
        background = self.sprites["background"]
        car = self.sprites["car"]
        aiCar = self.sprites["car-ai"]

        for event in pygame.event.get():
            if event.type == pygame.QUIT: os._exit(0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: car.direction.rotate_ip(-3.5)
        if keys[pygame.K_RIGHT]: car.direction.rotate_ip(3.5)
        
        self.spritesGroup.update()
        for index, goal in enumerate(self.goals):
            offset = (goal.rect.x - car.rect.x, goal.rect.y - car.rect.y)
            if car.mask.overlap(goal.mask, offset):
                self.checkForwardGoalIndex = index + 1
                if self.checkForwardGoalIndex >= len(self.goals): self.checkForwardGoalIndex = 0
                break
        aiOver = self._ai_move()

        self.screen.fill((0, 0, 0))
        self.spritesGroup.draw(self.screen)
        goal = pygame.draw.line(self.screen, (0, 255, 0), (576, 443), (576, 532))
        pygame.display.flip()
        
        if car.rect.colliderect(goal) or aiOver:
            time.sleep(0.3)
            print("User Won")
            os._exit(0)

        offset = (background.rect.x - car.rect.x, background.rect.y - car.rect.y)
        if aiCar.rect.colliderect(goal) or car.mask.overlap(background.mask, offset):
            time.sleep(0.3)
            print("AI Won")
            os._exit(0)

        self.clock.tick(FPS)
    
    def _ai_move(self) -> tuple:
        car = self.sprites["car-ai"]
        background = self.sprites["background"]
        gameOver = False

        action = [0, 0, 0]
        state = torch.tensor(self.get_state(), dtype=torch.float)
        prediction = self.model(state)
        move = torch.argmax(prediction).item()
        action[move] = 1

        if numpy.array_equal(action, [1, 0, 0]): car.direction.rotate_ip(-3.5)
        elif numpy.array_equal(action, [0, 1, 0]): car.direction.rotate_ip(3.5)

        offset = (background.rect.x - car.rect.x, background.rect.y - car.rect.y)
        if car.mask.overlap(background.mask, offset):
            gameOver = True
            return gameOver

        if car.rect.colliderect(self.goals[self.nextGoalIndex]):
            self.nextGoalIndex += 1
            if self.nextGoalIndex >= len(self.goals): self.nextGoalIndex = 0
        
        return gameOver

    def get_state(self):
        background = self.sprites["background"]
        car = self.sprites["car-ai"]

        state = []
        for rotation in [90, 45, 0, -45, -90]: state.append(self._raycast_collision(car, [background], rotation, 50))
        return state
    
    def _raycast_collision(self, start, sprites, rotation, until) -> int:
        direction = start.direction.rotate(rotation)
        for offset in range(until):
            line = pygame.draw.line(self.screen, (0, 255, 0), start.position + direction * offset, start.position + direction * (offset + 1))
            lineMask = pygame.mask.Mask(line.size, True)

            for sprite in sprites:
                spriteOffset = (sprite.rect.x - line.x, sprite.rect.y - line.y)
                if lineMask.overlap(sprite.mask, spriteOffset): return offset
        return until

game = Game()
while True: game.render()