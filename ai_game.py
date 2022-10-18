from sprites import *

import numpy
import json
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame

WIDTH = 800
HEIGHT = 600
FPS = 60

class AICar:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Car AI")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        
        self.reset()

    def reset(self):
        self.spritesGroup = pygame.sprite.Group()

        car = Car(self.screen, pygame.image.load(r"sprites\aicar.png"))
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
            "car": car,
            #"goal": Goal()
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
        self.lastDistance = pygame.math.Vector2(*car.position).distance_to(self.goals[self.nextGoalIndex].rect.center)
        self.checkForwardGoalIndex = 0
        self.score = 0
    
    def render(self, action) -> bool:
        car = self.sprites["car"]

        for event in pygame.event.get():
            if event.type == pygame.QUIT: os._exit(0)
            """elif event.type == pygame.MOUSEBUTTONDOWN:
                self.goals.append({
                    "direction": round(self.sprites["goal"].direction.angle_to((1, 0))),
                    "rect_attributes": {
                        "x": self.sprites["goal"].rect.x,
                        "y": self.sprites["goal"].rect.y
                    }
                })
                with open("goals.json", "w") as f: json.dump(self.goals, f, indent=4)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: self.sprites["goal"].direction.rotate_ip(-2)
        if keys[pygame.K_d]: self.sprites["goal"].direction.rotate_ip(2)"""
        
        self.spritesGroup.update()
        for index, goal in enumerate(self.goals):
            offset = (goal.rect.x - car.rect.x, goal.rect.y - car.rect.y)
            if car.mask.overlap(goal.mask, offset):
                self.checkForwardGoalIndex = index + 1
                if self.checkForwardGoalIndex >= len(self.goals): self.checkForwardGoalIndex = 0
                break
        result = self._move(action)

        self.screen.fill((0, 0, 0))
        self.spritesGroup.draw(self.screen)
        #for rotation in [95, 45, 0, -45, -95]: pygame.draw.line(self.screen, (0, 255, 0), car.position, car.position + car.direction.rotate(rotation) * 50)
        pygame.display.flip()

        self.clock.tick(FPS)
        return result
    
    def _move(self, action) -> tuple:
        car = self.sprites["car"]
        background = self.sprites["background"]
        reward = 0
        gameOver = False

        if numpy.array_equal(action, [1, 0, 0]): car.direction.rotate_ip(-3.5)
        elif numpy.array_equal(action, [0, 1, 0]): car.direction.rotate_ip(3.5)

        offsetIn = (background.rect.x - car.rect.x, background.rect.y - car.rect.y)
        if car.mask.overlap(background.mask, offsetIn):
            reward = -10
            gameOver = True
            return reward, gameOver, self.score

        if car.rect.colliderect(self.goals[self.nextGoalIndex]):
            reward = 1
            self.nextGoalIndex += 1
            if self.nextGoalIndex >= len(self.goals): self.nextGoalIndex = 0
            self.score += 1
        else:
            rays = []
            angles = [45, 0, -45]
            for rotation in angles:
                rays.append(self._raycast_collision([self.goals[self.checkForwardGoalIndex]], rotation, 50))

            if sum(rays) < 50 * len(angles): reward = 1
            else:
                print("-1 points")
                reward = -1
        return reward, gameOver, self.score

    def get_state(self):
        background = self.sprites["background"]

        state = []
        for rotation in [90, 45, 0, -45, -90]: state.append(self._raycast_collision([background], rotation, 50))
        return state
    
    def _raycast_collision(self, sprites, rotation, until) -> int:
        car = self.sprites["car"]

        direction = car.direction.rotate(rotation)
        for offset in range(until):
            line = pygame.draw.line(self.screen, (0, 255, 0), car.position + direction * offset, car.position + direction * (offset + 1))
            lineMask = pygame.mask.Mask(line.size, True)

            for sprite in sprites:
                spriteOffset = (sprite.rect.x - line.x, sprite.rect.y - line.y)
                if lineMask.overlap(sprite.mask, spriteOffset): return offset
        return until

"""game = AICar()
while True:
    keys = pygame.key.get_pressed()
    action = [0, 0, 0]
    if keys[pygame.K_a]: action = [1, 0, 0]
    if keys[pygame.K_d]: action = [0, 1, 0]
    game.render(action)
    print(game.get_state())"""