from enum import Enum

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame

class Direction(Enum):
    UP = 0
    LEFT = -90
    RIGHT = 90

class Car(pygame.sprite.Sprite):
    def __init__(self, screen, sprite):
        super().__init__()

        self.originalImage = sprite.convert()
        self.originalImage.set_colorkey((0, 0, 0))
        self.originalImage = pygame.transform.scale(self.originalImage, (24, 14))

        self.image = self.originalImage

        self.direction = pygame.Vector2(-2, 0.8)
        self.position = pygame.Vector2((561, 509))
        self.screen = screen

        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def update(self):
        self.position += self.direction * 1.5
        #self.position = pygame.mouse.get_pos()

        degrees = self.direction.angle_to((1, 0))
        self.image = pygame.transform.rotate(self.originalImage, degrees)
        self.rect.center = self.position

class BasicSprite(pygame.sprite.Sprite):
    def __init__(self, direction, rectAttributes, image) -> None:
        super().__init__()
        
        self.originalImage = image
        self.originalImage.set_colorkey((0, 0, 0))

        self.image = pygame.transform.rotate(self.originalImage, direction)
        
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        for attribute, value in rectAttributes.items(): setattr(self.rect, attribute, value)

class DetectBorders(pygame.sprite.Sprite):
    def __init__(self, car, direction, offset) -> None:
        super().__init__()

        self.originalImage = pygame.Surface((10, 40), pygame.SRCALPHA)
        self.originalImage.fill((0, 255, 0))
        self.image = self.originalImage
        
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.car = car

        self.offset = offset
        self.direction = direction.value
    
    def update(self):
        degrees = self.car.direction.angle_to((1, 0))
        self.image = pygame.transform.rotate(self.originalImage, degrees)
        
        self.rect.center = self.car.position + self.car.direction.rotate(self.direction) * self.offset

class Goal(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()

        self.originalImage = pygame.Surface((80, 10), pygame.SRCALPHA)
        self.originalImage.fill((0, 255, 0))
        self.image = self.originalImage

        self.direction = pygame.Vector2(2, 0)
        self.rect = self.image.get_rect()
    
    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        self.image = pygame.transform.rotate(self.originalImage, self.direction.angle_to((1, 0)))