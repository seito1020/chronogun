import pygame
import math
import random
from config import *
from utils import IMAGES, is_collision, get_distance, raycast, find_path, line_intersects_rect, angle_difference
from weapons import Weapon, Bullet, RailgunVisual, MeleeSlash, TurretLaserVisual
from items import Particle

class Enemy:
    def __init__(self, x, y, enemy_type, image_key):
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.stats = GAME_SPECS["enemies"][enemy_type]
        self.width = self.stats['w']
        self.height = self.stats['h']
        self.hitbox_size = self.stats['hitbox']
        self.rect = pygame.Rect(x, y, self.hitbox_size, self.hitbox_size)
        self.image = IMAGES[image_key]
        self.type = enemy_type
        
        self.hp = self.stats["hp"]
        self.max_hp = self.stats["hp"]
        self.atk = self.stats["atk"]
        self.spd = self.stats["spd"] * 10
        self.rng = self.stats["rng"] * 40
        self.amo = self.stats["amo"]
        self.bsp = self.stats["bsp"] * 10
        
        self.patrol_angle = random.uniform(0, math.pi * 2)
        self.patrol_timer = 0
        self.alerted = False
        self.angle = 0
        
        self.children = []
        self.summon_cooldown = 0
        self.charge_time = 0
        
        # ボス用変数
        self.boss_action_cycle = 0
        self.pending_minions = []
        self.has_summoned_reinforcements = False

    def calculate_move(self, player_rect, obstacles):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        target_angle = math.atan2(dy, dx)
        
        if self.type == 'turret':
            diff = angle_difference(target_angle, self.angle)
            rot_step = math.radians(TURRET_ROT_SPEED)
            if abs(diff) < rot_step:
                self.angle = target_angle
            elif diff > 0:
                self.angle += rot_step
            else:
                self.angle -= rot_step
        else:
            self.angle = target_angle

        if self.spd == 0: return 0, 0 

        can_see_player = False
        if distance > 0:
            hit_pos = raycast(self.rect.center, target_angle, distance, obstacles)
            dist_hit = math.hypot(hit_pos[0] - player_rect.centerx, hit_pos[1] - player_rect.centery)
            if dist_hit < 30:
                can_see_player = True
                self.alerted = True

        if self.type == 'ghost':
            move_dx = (dx / distance) * self.spd if distance > 0 else 0
            move_dy = (dy / distance) * self.spd if distance > 0 else 0
            return move_dx, move_dy

        move_dx, move_dy = 0, 0
        use_pathfinding = False

        if self.type == 'summoner':
            if can_see_player or self.alerted:
                escape_angle = target_angle + math.pi
                t_dx = math.cos(escape_angle) * self.spd
                t_dy = math.sin(escape_angle) * self.spd
                
                if is_collision(self.rect.move(t_dx, t_dy), obstacles):
                    escape_angle += random.uniform(-1.0, 1.0)
                    t_dx = math.cos(escape_angle) * self.spd
                    t_dy = math.sin(escape_angle) * self.spd
                
                if not is_collision(self.rect.move(t_dx, t_dy), obstacles):
                    return t_dx, t_dy
                elif not is_collision(self.rect.move(t_dx, 0), obstacles):
                    return t_dx, 0
                elif not is_collision(self.rect.move(0, t_dy), obstacles):
                    return 0, t_dy
            pass

        can_move_directly = False
        if can_see_player:
            stop_dist = self.width if self.type != 'bomber' else 0
            if distance > stop_dist:
                t_dx = (dx / distance) * self.spd
                t_dy = (dy / distance) * self.spd
                if not is_collision(self.rect.move(t_dx, t_dy), obstacles):
                    move_dx, move_dy = t_dx, t_dy
                    can_move_directly = True
            
        if (not can_move_directly) and self.alerted:
            use_pathfinding = True
            next_pos = find_path(self.rect.center, player_rect.center, obstacles)
            p_dx = next_pos[0] - self.rect.centerx
            p_dy = next_pos[1] - self.rect.centery
            p_dist = math.hypot(p_dx, p_dy)
            
            if p_dist > 0:
                move_dx = (p_dx / p_dist) * self.spd
                move_dy = (p_dy / p_dist) * self.spd

        if not is_collision(self.rect.move(move_dx, move_dy), obstacles):
            return move_dx, move_dy
        
        can_move_x = not is_collision(self.rect.move(move_dx, 0), obstacles)
        can_move_y = not is_collision(self.rect.move(0, move_dy), obstacles)

        if can_move_x and can_move_y:
            if abs(move_dx) > abs(move_dy): return move_dx, 0
            else: return 0, move_dy
        elif can_move_x: return move_dx, 0
        elif can_move_y: return 0, move_dy

        if move_dx == 0 and move_dy == 0 and self.type != 'turret' and not use_pathfinding:
            self.patrol_timer -= 1
            if self.patrol_timer <= 0:
                self.patrol_angle = random.uniform(0, math.pi * 2)
                self.patrol_timer = random.randint(20, 60)
            
            patrol_spd = self.spd * 0.5
            p_dx = math.cos(self.patrol_angle) * patrol_spd
            p_dy = math.sin(self.patrol_angle) * patrol_spd
            
            if not is_collision(self.rect.move(p_dx, p_dy), obstacles):
                return p_dx, p_dy
            else:
                self.patrol_angle += math.pi

        return 0, 0

    def try_attack(self, player, bullets, obstacles, particles):
        if self.rng == 0: return False

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx)
        
        hit_pos = raycast(self.rect.center, angle, dist, obstacles)
        can_see = (math.hypot(hit_pos[0]-player.rect.centerx, hit_pos[1]-player.rect.centery) < 30)

        if can_see: self.alerted = True 

        if self.type == 'summoner':
            if not self.alerted: return False
            if self.summon_cooldown > 0:
                self.summon_cooldown -= 1
                return False 
            return True 

        if self.type == 'turret':
            angle_diff = abs(angle_difference(self.angle, angle))
            if can_see and dist < self.rng and angle_diff < 0.2:
                if self.charge_time < 3:
                    self.charge_time += 1
                    return True
                else:
                    self.charge_time = 0
                    start_pos = self.rect.center
                    end_pos = raycast(start_pos, self.angle, self.rng, obstacles)
                    if line_intersects_rect(start_pos, end_pos, player.rect):
                        player.hp -= self.atk 
                        for _ in range(10): particles.append(Particle(player.rect.centerx, player.rect.centery, GREEN))
                    bullets.append(TurretLaserVisual(start_pos[0], start_pos[1], end_pos[0], end_pos[1]))
                    return True
            else:
                self.charge_time = 0
                return False

        if self.type == 'boss':
            if not can_see: return False
            if dist < self.rng:
                phase = self.boss_action_cycle % 5
                if phase == 2 and not self.has_summoned_reinforcements:
                    self.pending_minions.append("shielder")
                    self.pending_minions.append("bomber")
                    self.has_summoned_reinforcements = True
                    self.boss_action_cycle += 1
                    return True

                if phase < 3:
                    spread_angle = math.radians(20)
                    offsets = [-spread_angle, spread_angle]
                    for offset in offsets:
                        fire_angle = angle + offset
                        spacing = 20
                        for i in range(5): 
                            bx = self.rect.centerx + math.cos(fire_angle) * (i * spacing)
                            by = self.rect.centery + math.sin(fire_angle) * (i * spacing)
                            speed_jitter = random.uniform(0.9, 1.1)
                            b = Bullet(bx, by, fire_angle, self.bsp * speed_jitter, self.atk, 
                                       99999, False, "bullet_pistol", False)
                            b.color = PURPLE
                            bullets.append(b)
                    self.boss_action_cycle += 1
                    return True 
                else:
                    self.boss_action_cycle += 1
                    return False

            return False

        if self.rng > 0 and dist < self.rng and can_see:
            if self.type == 'rapid':
                spacing = 15
                for i in range(self.amo):
                    jitter = random.uniform(-0.05, 0.05)
                    offset_x = math.cos(angle) * (i * spacing)
                    offset_y = math.sin(angle) * (i * spacing)
                    b = Bullet(self.rect.centerx + offset_x, self.rect.centery + offset_y, 
                               angle + jitter, self.bsp, self.atk, 99999, False, None, False)
                    b.color = RED
                    bullets.append(b)
            else:
                b = Bullet(self.rect.centerx, self.rect.centery, angle, self.bsp, self.atk, 99999, False, None, False)
                b.color = RED
                bullets.append(b)
            return True
        return False

    def summon_minion(self, obstacles):
        if self.type != 'summoner': return None
        self.summon_cooldown = 10 
        for _ in range(10):
            rx = self.rect.x + random.randint(-150, 150)
            ry = self.rect.y + random.randint(-150, 150)
            spawn_rect = pygame.Rect(rx, ry, 60, 60)
            if not is_collision(spawn_rect, obstacles):
                etype = random.choice(['normal', 'rapid'])
                img_key = f"enemy_{etype if etype != 'rapid' else 'rapid'}"
                if etype == 'normal': img_key = 'enemy_normal'
                minion = Enemy(rx, ry, etype, img_key)
                self.children.append(minion)
                return minion
        return None

    def update_step_pos(self, step_dx, step_dy):
        self.pos_x += step_dx
        self.pos_y += step_dy
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

    def draw(self, surface, player_rect, obstacles, camera_offset):
        degrees = math.degrees(-self.angle) - 90
        rotated_img = pygame.transform.rotate(self.image, degrees)
        visual_rect = rotated_img.get_rect(center=self.rect.center)
        draw_rect = visual_rect.move(-camera_offset[0], -camera_offset[1])
        
        surface.blit(rotated_img, draw_rect)
        
        if self.hp < self.max_hp:
            ratio = self.hp / self.max_hp
            ratio = max(0.0, ratio)
            bar_w = self.width
            bar_x = draw_rect.centerx - bar_w // 2
            bar_y = draw_rect.top - 10
            pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_w, 4))
            pygame.draw.rect(surface, GREEN, (bar_x, bar_y, bar_w * ratio, 4))
        
        if (self.type != 'ghost'):
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            angle = math.atan2(dy, dx)
            hit_pos = raycast(self.rect.center, angle, dist, obstacles)
            can_see = (math.hypot(hit_pos[0]-player_rect.centerx, hit_pos[1]-player_rect.centery) < 30)
            
            if can_see or self.alerted:
                alert_x = draw_rect.right - 5
                alert_y = draw_rect.top - 10
                surface.blit(IMAGES['alert'], (alert_x, alert_y))
        
        if self.type == 'turret' and self.charge_time > 0:
             end_pos = (self.rect.centerx + math.cos(self.angle)*1000, self.rect.centery + math.sin(self.angle)*1000)
             sp = (self.rect.centerx - camera_offset[0], self.rect.centery - camera_offset[1])
             ep = (end_pos[0] - camera_offset[0], end_pos[1] - camera_offset[1])
             width = self.charge_time * 2 
             pygame.draw.line(surface, RED, sp, ep, width)

class Player:
    def __init__(self, x, y):
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.rect = pygame.Rect(x, y, PLAYER_HITBOX_SIZE, PLAYER_HITBOX_SIZE)
        
        stats = GAME_SPECS["player"]
        self.hp = stats["hp"]
        self.max_hp = stats["max_hp"]
        self.spd = stats["spd"] * 10
        self.angle = 0
        self.original_image = IMAGES['player']
        self.image = self.original_image
        
        self.weapons = {
            "Pistol":  Weapon("Pistol"),
            "Shotgun": Weapon("Shotgun"),
            "Rifle":   Weapon("Rifle"),
            "SMG":     Weapon("SMG"),
            "RPG":     Weapon("RPG"),
            "Blade":   Weapon("Blade"),
            "Railgun": Weapon("Railgun"),
            "Ricochet":Weapon("Ricochet"),
            "Mine":    Weapon("Mine"),
        }
        self.current_weapon = self.weapons["Pistol"]
        self.railgun_charged = False

    def aim(self, camera_offset):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_mouse_x = mouse_x + camera_offset[0]
        world_mouse_y = mouse_y + camera_offset[1]
        
        dx = world_mouse_x - self.rect.centerx
        dy = world_mouse_y - self.rect.centery
        self.angle = math.atan2(dy, dx)
        degrees = math.degrees(-self.angle) - 90
        self.image = pygame.transform.rotate(self.original_image, degrees)
        self.visual_rect = self.image.get_rect(center=self.rect.center)

    def calculate_move(self, target_pos, obstacles, camera_offset):
        world_target_x = target_pos[0] + camera_offset[0]
        world_target_y = target_pos[1] + camera_offset[1]
        
        dx = world_target_x - self.rect.centerx
        dy = world_target_y - self.rect.centery
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist == 0: return 0, 0
        
        move_dist = min(dist, self.spd)
        norm_x = (dx / dist)
        norm_y = (dy / dist)
        
        test_x = norm_x * move_dist
        test_y = norm_y * move_dist
        
        if not is_collision(self.rect.move(test_x, test_y), obstacles):
            return test_x, test_y
        
        valid_x, valid_y = 0, 0
        for i in range(10, 0, -1):
            ratio = i / 10.0
            tx = test_x * ratio
            ty = test_y * ratio
            if not is_collision(self.rect.move(tx, ty), obstacles):
                valid_x, valid_y = tx, ty
                break
                
        return valid_x, valid_y

    def update_step_pos(self, step_dx, step_dy):
        self.pos_x += step_dx
        self.pos_y += step_dy
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        self.visual_rect = self.image.get_rect(center=self.rect.center)

    def shoot(self, bullets, enemies, particles):
        if self.current_weapon.name == "Railgun":
            if not self.railgun_charged:
                self.railgun_charged = True
                return
            else:
                self.railgun_charged = False 
                
                start_pos = self.rect.center
                end_x = start_pos[0] + math.cos(self.angle) * 3000 
                end_y = start_pos[1] + math.sin(self.angle) * 3000
                end_pos = (end_x, end_y)
                
                for e in enemies[:]:
                    if line_intersects_rect(start_pos, end_pos, e.rect):
                        e.hp -= 999 
                        for _ in range(10):
                            particles.append(Particle(e.rect.centerx, e.rect.centery, CYAN))
                
                bullets.append(RailgunVisual(start_pos[0], start_pos[1], end_x, end_y))
                return

        self.railgun_charged = False 
        
        new_bullets = self.current_weapon.create_bullets(
            self.rect.centerx, self.rect.centery, self.angle
        )
        bullets.extend(new_bullets)

    def draw(self, surface, obstacles, camera_offset):
        max_aim_dist = 600
        if self.current_weapon.brg != "inf":
            max_aim_dist = self.current_weapon.brg_val
        
        end_pos_world = raycast(self.rect.center, self.angle, max_aim_dist, obstacles)
        
        start_pos_screen = (self.rect.centerx - camera_offset[0], self.rect.centery - camera_offset[1])
        end_pos_screen = (end_pos_world[0] - camera_offset[0], end_pos_world[1] - camera_offset[1])
        
        aim_color = AIM_LINE_COLOR
        # レールガンチャージ時のエフェクト
        if self.current_weapon.name == "Railgun" and self.railgun_charged:
            aim_color = CHARGE_COLOR 
            end_x = self.rect.centerx + math.cos(self.angle) * 3000
            end_y = self.rect.centery + math.sin(self.angle) * 3000
            end_pos_screen = (end_x - camera_offset[0], end_y - camera_offset[1])
        
        pygame.draw.line(surface, aim_color, start_pos_screen, end_pos_screen, 2)
        pygame.draw.circle(surface, aim_color, (int(end_pos_screen[0]), int(end_pos_screen[1])), 4)
        
        if hasattr(self, 'visual_rect'):
            draw_rect = self.visual_rect.move(-camera_offset[0], -camera_offset[1])
            surface.blit(self.image, draw_rect)
        else:
            rect = self.image.get_rect(center=self.rect.center)
            draw_rect = rect.move(-camera_offset[0], -camera_offset[1])
            surface.blit(self.image, draw_rect)