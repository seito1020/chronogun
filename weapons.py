import pygame
import math
import random
from config import *
from utils import IMAGES, is_collision

class Bullet:
    def __init__(self, x, y, angle, bsp, atk, brg, penetration, image_key, is_player_bullet, 
                 explosive=False, wall_pen=False, bounce=0, is_mine=False):
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        self.hitbox = pygame.Rect(0, 0, BULLET_HITBOX_SIZE, BULLET_HITBOX_SIZE)
        if is_mine:
            self.hitbox = pygame.Rect(0, 0, 40, 40)
        self.hitbox.center = (int(x), int(y))
        
        self.atk = atk
        self.bsp = bsp
        self.brg = brg
        self.penetration = penetration
        self.is_player_bullet = is_player_bullet
        self.hit_list = [] 
        
        self.explosive = explosive
        self.wall_pen = wall_pen
        self.bounce = bounce
        self.is_mine = is_mine
        
        self.dx = math.cos(angle) * self.bsp
        self.dy = math.sin(angle) * self.bsp
        
        self.original_img = None
        if image_key and image_key in IMAGES:
            self.original_img = IMAGES[image_key]
            self.update_rotation()
        else:
            self.image = None
            self.rect = self.hitbox.copy()
        
        if not is_player_bullet:
             self.color = RED
             self.image = None

    def update_rotation(self):
        if self.original_img:
            angle = math.atan2(self.dy, self.dx)
            degrees = math.degrees(-angle)
            self.image = pygame.transform.rotate(self.original_img, degrees)
            self.rect = self.image.get_rect(center=self.hitbox.center)

    def get_step_move(self):
        if self.is_mine: return 0, 0
        return self.dx / ANIMATION_STEPS, self.dy / ANIMATION_STEPS

    def update_step(self, step_dx, step_dy, obstacles):
        if not self.is_mine and self.brg != "inf":
            step_dist = math.hypot(step_dx, step_dy)
            self.brg -= step_dist

        bounced_this_step = False

        # X軸移動処理
        self.pos_x += step_dx
        self.hitbox.centerx = int(self.pos_x)
        
        if not self.wall_pen and is_collision(self.hitbox, obstacles):
            if self.bounce > 0:
                self.pos_x -= step_dx 
                self.hitbox.centerx = int(self.pos_x)
                self.dx *= -1 
                self.update_rotation()
                
                if not bounced_this_step:
                    self.bounce -= 1
                    bounced_this_step = True
            else:
                self.brg = 0 

        # Y軸移動処理
        self.pos_y += step_dy
        self.hitbox.centery = int(self.pos_y)
        
        if not self.wall_pen and is_collision(self.hitbox, obstacles):
            if self.brg != 0:
                if self.bounce > 0:
                    self.pos_y -= step_dy 
                    self.hitbox.centery = int(self.pos_y)
                    self.dy *= -1 
                    self.update_rotation()
                    
                    if not bounced_this_step:
                        self.bounce -= 1
                        bounced_this_step = True
                else:
                    self.brg = 0

        if self.image: 
            self.rect.center = self.hitbox.center

    def draw(self, surface, camera_offset):
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        
        if self.image:
            surface.blit(self.image, draw_rect)
        else:
            draw_center_x = int(self.pos_x - camera_offset[0])
            draw_center_y = int(self.pos_y - camera_offset[1])
            radius = max(3, BULLET_HITBOX_SIZE // 2) 
            pygame.draw.circle(surface, getattr(self, 'color', WHITE), (draw_center_x, draw_center_y), radius)

class MeleeSlash(Bullet):
    def __init__(self, x, y, angle, atk, is_player_bullet):
        super().__init__(x, y, angle, 0, atk, 999, True, None, is_player_bullet)
        self.base_angle = angle
        self.life_max = ANIMATION_STEPS 
        self.life = self.life_max
        self.reach = 100 
        self.hitbox = pygame.Rect(0, 0, 120, 120)
        offset_x = math.cos(angle) * 40
        offset_y = math.sin(angle) * 40
        self.hitbox.center = (int(x + offset_x), int(y + offset_y))
        self.rect = self.hitbox.copy()

    def get_step_move(self):
        return 0, 0

    def update_step(self, step_dx, step_dy, obstacles):
        self.life -= 1
        self.brg = self.life

    def draw(self, surface, camera_offset):
        if self.life <= 0: return
        progress = 1.0 - (self.life / self.life_max)
        start_swing = self.base_angle - math.pi / 2
        end_swing = self.base_angle + math.pi / 2
        current_angle = start_swing + (end_swing - start_swing) * progress
        start_pos = (self.pos_x - camera_offset[0], self.pos_y - camera_offset[1])
        end_x = start_pos[0] + math.cos(current_angle) * self.reach
        end_y = start_pos[1] + math.sin(current_angle) * self.reach
        pygame.draw.line(surface, CYAN, start_pos, (end_x, end_y), 5)

class RailgunVisual(Bullet):
    def __init__(self, x, y, end_x, end_y):
        super().__init__(x, y, 0, 0, 0, 999, True, None, True)
        self.start_pos = (x, y)
        self.end_pos = (end_x, end_y)
        self.life = 15
    
    def get_step_move(self): return 0, 0
    def update_step(self, step_dx, step_dy, obstacles):
        self.life -= 1
        if self.life <= 0: self.brg = 0

    def draw(self, surface, camera_offset):
        if self.life <= 0: return
        width = max(1, int(10 * (self.life / 15)))
        
        sx = int(self.start_pos[0] - camera_offset[0])
        sy = int(self.start_pos[1] - camera_offset[1])
        ex = int(self.end_pos[0] - camera_offset[0])
        ey = int(self.end_pos[1] - camera_offset[1])
        
        sp = (sx, sy)
        ep = (ex, ey)
        
        pygame.draw.line(surface, RAILGUN_COLOR, sp, ep, width)
        pygame.draw.line(surface, WHITE, sp, ep, max(1, width // 2))

class TurretLaserVisual(RailgunVisual):
    def draw(self, surface, camera_offset):
        if self.life <= 0: return
        width = max(1, int(8 * (self.life / 15)))
        
        sx = int(self.start_pos[0] - camera_offset[0])
        sy = int(self.start_pos[1] - camera_offset[1])
        ex = int(self.end_pos[0] - camera_offset[0])
        ey = int(self.end_pos[1] - camera_offset[1])
        
        sp = (sx, sy)
        ep = (ex, ey)
        
        pygame.draw.line(surface, TURRET_LASER_COLOR, sp, ep, width)
        pygame.draw.line(surface, WHITE, sp, ep, max(1, width // 2))

class Weapon:
    def __init__(self, name):
        self.name = name
        stats = GAME_SPECS["weapons"][name]
        self.atk = stats["atk"]
        self.amo = stats["amo"]
        self.bsp = stats["bsp"] * 10
        self.brg = stats["brg"]
        self.pen = stats["pen"]
        self.icon_key = stats["img"]
        
        if self.brg == "inf":
            self.brg_val = 99999
        else:
            self.brg_val = self.brg * 100

    def create_bullets(self, x, y, angle):
        bullets = []
        
        img_key = None
        if "pistol" in self.name.lower(): img_key = "bullet_pistol"
        elif "shotgun" in self.name.lower(): img_key = "bullet_sg"
        elif "rifle" in self.name.lower(): img_key = "bullet_sr"
        elif "smg" in self.name.lower(): img_key = "bullet_smg"
        elif "rpg" in self.name.lower(): img_key = "bullet_rpg"
        elif "ricochet" in self.name.lower(): img_key = "bullet_ricochet"
        elif "mine" in self.name.lower(): img_key = "bullet_mine"

        if self.name == "Shotgun":
            spread = math.radians(15)
            for i in range(self.amo):
                base_angle = angle - spread
                step_angle = (spread * 2) / (self.amo - 1)
                shot_angle = base_angle + (step_angle * i)
                bullets.append(Bullet(x, y, shot_angle, self.bsp, self.atk, self.brg_val, self.pen, img_key, True))
        
        elif self.name in ["SMG", "Rapid"]:
            spacing = 15
            for i in range(self.amo):
                jitter = random.uniform(-0.02, 0.02) 
                shot_angle = angle + jitter
                offset_x = math.cos(angle) * (i * spacing)
                offset_y = math.sin(angle) * (i * spacing)
                bullets.append(Bullet(x + offset_x, y + offset_y, shot_angle, self.bsp, self.atk, self.brg_val, self.pen, img_key, True))

        elif self.name == "RPG":
            bullets.append(Bullet(x, y, angle, self.bsp, self.atk, self.brg_val, self.pen, img_key, True, explosive=True))

        elif self.name == "Blade":
            bullets.append(MeleeSlash(x, y, angle, self.atk, True))

        elif self.name == "Railgun":
            pass

        elif self.name == "Ricochet":
            bullets.append(Bullet(x, y, angle, self.bsp, self.atk, self.brg_val, self.pen, img_key, True, bounce=3))

        elif self.name == "Mine":
            bullets.append(Bullet(x, y, 0, 0, self.atk, self.brg_val, False, img_key, True, is_mine=True))

        else:
            bullets.append(Bullet(x, y, angle, self.bsp, self.atk, self.brg_val, self.pen, img_key, True))
            
        return bullets