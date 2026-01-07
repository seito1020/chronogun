import pygame
import math
import random
from config import *
from utils import IMAGES

class Particle:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, 4, 4)
        self.color = color
        self.life = 40
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

    def update(self):
        self.rect.move_ip(self.dx, self.dy)
        self.life -= 1

    def draw(self, surface, camera_offset):
        if self.life > 0:
            draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
            pygame.draw.rect(surface, self.color, draw_rect)

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 40 
        self.max_radius = EXPLOSION_RADIUS

    def update(self):
        self.life -= 1

    def draw(self, surface, camera_offset):
        if self.life > 0:
            progress = 1.0 - (self.life / 40.0)
            current_radius = int(self.max_radius * progress)
            alpha = int(255 * (self.life / 40.0))
            
            center = (int(self.x - camera_offset[0]), int(self.y - camera_offset[1]))
            surf = pygame.Surface((current_radius*2, current_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*ORANGE, alpha), (current_radius, current_radius), current_radius)
            surface.blit(surf, (center[0] - current_radius, center[1] - current_radius))

class Item:
    def __init__(self, x, y, item_type, data=None):
        self.rect = pygame.Rect(x, y, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        self.type = item_type 
        self.data = data      
        self.float_offset = 0
        
        if self.type == "hp":
            self.image = IMAGES['hp_item']
        elif self.type == "weapon":
            img_map = {
                "Pistol": "item_pistol", "Shotgun": "item_shotgun",
                "Rifle": "item_rifle", "SMG": "item_smg",
                "RPG": "item_rpg", "Blade": "item_blade", 
                "Railgun": "item_railgun"
            }
            self.image = IMAGES.get(img_map.get(data, "item_pistol"), IMAGES["item_pistol"])

    def draw(self, surface, camera_offset):
        # 浮遊アニメーション
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.005) * 5
        
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1] + self.float_offset
        
        if self.type == "hp":
            pygame.draw.rect(surface, CYAN, (draw_x, draw_y, ITEM_BOX_SIZE, ITEM_BOX_SIZE), 1)
        
        center_x = draw_x + ITEM_BOX_SIZE // 2
        center_y = draw_y + ITEM_BOX_SIZE // 2
        
        image_rect = self.image.get_rect(center=(center_x, center_y))
        surface.blit(self.image, image_rect)