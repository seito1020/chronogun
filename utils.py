import pygame
import math
import random
import os
import heapq
from config import *

IMAGES = {}

def load_and_scale(filename, width, height):
    path = os.path.join("images", filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (int(width), int(height)))
    except FileNotFoundError:
        print(f"Error: Image not found at {path}")
        surf = pygame.Surface((int(width), int(height)))
        surf.fill((255, 0, 255)) 
        return surf

def load_all_images():
    IMAGES['player'] = load_and_scale('player.png', PLAYER_VISUAL_SIZE, PLAYER_VISUAL_SIZE)
    IMAGES['exit'] = load_and_scale('exit.png', EXIT_W, EXIT_H)
    IMAGES['hp'] = load_and_scale('hp.png', HP_ICON_SIZE, HP_ICON_SIZE)
    IMAGES['alert'] = load_and_scale('bikkuri.png', 20, 20)

    enemies_specs = GAME_SPECS["enemies"]
    IMAGES['enemy_normal'] = load_and_scale('enemy_nomal.png', enemies_specs["normal"]["w"], enemies_specs["normal"]["h"])
    IMAGES['enemy_sniper'] = load_and_scale('enemy_sniper.png', enemies_specs["sniper"]["w"], enemies_specs["sniper"]["h"])
    IMAGES['enemy_fighter'] = load_and_scale('enemy_fighter.png', enemies_specs["fighter"]["w"], enemies_specs["fighter"]["h"])
    IMAGES['enemy_assassin'] = load_and_scale('enemy_assassin.png', enemies_specs["assassin"]["w"], enemies_specs["assassin"]["h"])
    IMAGES['enemy_rapid'] = load_and_scale('enemy_rensya.png', enemies_specs["rapid"]["w"], enemies_specs["rapid"]["h"])
    IMAGES['enemy_bomber'] = load_and_scale('enemy_bomber.png', enemies_specs["bomber"]["w"], enemies_specs["bomber"]["h"])
    IMAGES['enemy_shielder'] = load_and_scale('enemy_shielder.png', enemies_specs["shielder"]["w"], enemies_specs["shielder"]["h"])
    IMAGES['enemy_ghost'] = load_and_scale('enemy_ghost.png', enemies_specs["ghost"]["w"], enemies_specs["ghost"]["h"])
    IMAGES['enemy_summoner'] = load_and_scale('enemy_summoner.png', enemies_specs["summoner"]["w"], enemies_specs["summoner"]["h"])
    IMAGES['enemy_turret'] = load_and_scale('enemy_turret.png', enemies_specs["turret"]["w"], enemies_specs["turret"]["h"])
    
    # ボス画像の読み込み
    if "boss" in enemies_specs:
        IMAGES['enemy_boss'] = load_and_scale('enemy_lasboss.png', enemies_specs["boss"]["w"], enemies_specs["boss"]["h"])
    else:
        IMAGES['enemy_boss'] = load_and_scale('enemy_lasboss.png', 120, 120)

    IMAGES['gun_pistol'] = load_and_scale('gun_pistol.png', WEAPON_ICON_SIZE, WEAPON_ICON_SIZE)
    IMAGES['gun_shotgun'] = load_and_scale('gun_sg.png', WEAPON_ICON_SIZE, WEAPON_ICON_SIZE)
    IMAGES['gun_rifle'] = load_and_scale('gun_sr.png', WEAPON_ICON_SIZE, WEAPON_ICON_SIZE)
    IMAGES['gun_smg'] = load_and_scale('gun_smg.png', WEAPON_ICON_SIZE, WEAPON_ICON_SIZE)
    IMAGES['gun_rpg'] = load_and_scale('gun_rpg.png', WEAPON_ICON_SIZE, WEAPON_ICON_SIZE)
    IMAGES['gun_blade'] = load_and_scale('gun_blade.png', WEAPON_ICON_SIZE, WEAPON_ICON_SIZE)
    IMAGES['gun_railgun'] = load_and_scale('gun_railgun.png', WEAPON_ICON_SIZE, WEAPON_ICON_SIZE)
    IMAGES['gun_ricochet'] = load_and_scale('gun_ricochet.png', WEAPON_ICON_SIZE, WEAPON_ICON_SIZE)
    IMAGES['gun_mine'] = load_and_scale('gun_mine.png', WEAPON_ICON_SIZE, WEAPON_ICON_SIZE)

    IMAGES['item_pistol'] = load_and_scale('gun_pistol.png', ITEM_IMAGE_SIZE, ITEM_IMAGE_SIZE)
    IMAGES['item_shotgun'] = load_and_scale('gun_sg.png', ITEM_IMAGE_SIZE, ITEM_IMAGE_SIZE)
    IMAGES['item_rifle'] = load_and_scale('gun_sr.png', ITEM_IMAGE_SIZE, ITEM_IMAGE_SIZE)
    IMAGES['item_smg'] = load_and_scale('gun_smg.png', ITEM_IMAGE_SIZE, ITEM_IMAGE_SIZE)
    IMAGES['item_rpg'] = load_and_scale('gun_rpg.png', ITEM_IMAGE_SIZE, ITEM_IMAGE_SIZE)
    IMAGES['item_blade'] = load_and_scale('gun_blade.png', ITEM_IMAGE_SIZE, ITEM_IMAGE_SIZE)
    IMAGES['item_railgun'] = load_and_scale('gun_railgun.png', ITEM_IMAGE_SIZE, ITEM_IMAGE_SIZE)
    IMAGES['item_ricochet'] = load_and_scale('gun_ricochet.png', ITEM_IMAGE_SIZE, ITEM_IMAGE_SIZE)
    IMAGES['item_mine'] = load_and_scale('gun_mine.png', ITEM_IMAGE_SIZE, ITEM_IMAGE_SIZE)
    IMAGES['hp_item'] = load_and_scale('hp.png', ITEM_IMAGE_SIZE, ITEM_IMAGE_SIZE)

    IMAGES['bullet_pistol'] = load_and_scale('bullet_pistol.png', BULLET_W, BULLET_H)
    IMAGES['bullet_sg'] = load_and_scale('bullet_sg.png', BULLET_W, BULLET_H)
    IMAGES['bullet_sr'] = load_and_scale('bullet_sr.png', BULLET_W * 1.5, BULLET_H)
    IMAGES['bullet_smg'] = load_and_scale('bullet_smg.png', BULLET_W, BULLET_H)
    IMAGES['bullet_rpg'] = load_and_scale('bullet_rocket.png', int(BULLET_W * 1.2), int(BULLET_H * 1.5))
    IMAGES['bullet_ricochet'] = load_and_scale('bullet_pistol.png', BULLET_W, BULLET_H)
    IMAGES['bullet_mine'] = load_and_scale('bullet_mine.png', 40, 40)

def is_collision(rect, obstacles):
    for obs in obstacles:
        if rect.colliderect(obs): return True
    return False

def get_distance(rect1, rect2):
    dx = rect1.centerx - rect2.centerx
    dy = rect1.centery - rect2.centery
    return math.sqrt(dx**2 + dy**2)

def raycast(start_pos, angle, max_dist, obstacles):
    step = 10
    x, y = start_pos
    dx = math.cos(angle) * step
    dy = math.sin(angle) * step
    
    current_dist = 0
    while current_dist < max_dist:
        x += dx
        y += dy
        current_dist += step
        point_rect = pygame.Rect(x-1, y-1, 2, 2)
        if is_collision(point_rect, obstacles):
            return (x, y)
    return (x, y)

def line_intersects_rect(p1, p2, rect):
    try:
        clipped_line = rect.clipline(p1, p2)
        if clipped_line:
            return True
    except ValueError:
        pass
    return False

def angle_difference(a1, a2):
    return (a1 - a2 + math.pi) % (2 * math.pi) - math.pi

def get_random_free_pos(width, height, obstacles, map_w, map_h, padding=20):
    margin = 20 
    attempts = 0
    max_attempts = 2000

    while attempts < max_attempts:
        attempts += 1
        x = random.randint(padding, map_w - width - padding)
        y = random.randint(padding, map_h - height - padding)
        check_rect = pygame.Rect(x - margin, y - margin, width + margin * 2, height + margin * 2)
        if not is_collision(check_rect, obstacles):
            return x, y
            
    print("Warning: Could not find free spawn position!")
    return map_w // 2, map_h // 2

def find_path(start_pos, target_pos, obstacles):
    grid_size = NAV_GRID_SIZE 
    
    start_gx = int(start_pos[0] // grid_size)
    start_gy = int(start_pos[1] // grid_size)
    target_gx = int(target_pos[0] // grid_size)
    target_gy = int(target_pos[1] // grid_size)

    start_node = (start_gx, start_gy)
    target_node = (target_gx, target_gy)

    if start_node == target_node:
        return target_pos

    frontier = []
    heapq.heappush(frontier, (0, start_node))
    came_from = {}
    cost_so_far = {}
    came_from[start_node] = None
    cost_so_far[start_node] = 0

    found = False
    max_steps = 300 
    steps = 0
    
    closest_node = start_node
    min_dist_to_target = float('inf')

    while frontier and steps < max_steps:
        steps += 1
        _, current = heapq.heappop(frontier)

        if current == target_node:
            found = True
            closest_node = current
            break
            
        dist = abs(current[0] - target_node[0]) + abs(current[1] - target_node[1])
        if dist < min_dist_to_target:
            min_dist_to_target = dist
            closest_node = current

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_node = (current[0] + dx, current[1] + dy)
            
            if not (0 <= next_node[0] < MAP_WIDTH // grid_size and 
                    0 <= next_node[1] < MAP_HEIGHT // grid_size):
                continue
            
            check_rect = pygame.Rect(next_node[0] * grid_size, 
                                     next_node[1] * grid_size, 
                                     grid_size, grid_size)
            if is_collision(check_rect, obstacles):
                continue

            new_cost = cost_so_far[current] + 1
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + abs(target_node[0] - next_node[0]) + abs(target_node[1] - next_node[1])
                heapq.heappush(frontier, (priority, next_node))
                came_from[next_node] = current

    curr = closest_node
    path = []
    while curr != start_node and curr is not None:
        path.append(curr)
        curr = came_from.get(curr) 
    path.reverse()
    
    if len(path) > 0:
        next_grid = path[0]
        return (next_grid[0] * grid_size + grid_size // 2,
                next_grid[1] * grid_size + grid_size // 2)
    
    return target_pos

def is_path_exists(start_pos, target_pos, obstacles, map_w, map_h):
    start_gx = int(start_pos[0] // PATH_GRID_SIZE)
    start_gy = int(start_pos[1] // PATH_GRID_SIZE)
    target_gx = int(target_pos[0] // PATH_GRID_SIZE)
    target_gy = int(target_pos[1] // PATH_GRID_SIZE)
    
    start_node = (start_gx, start_gy)
    target_node = (target_gx, target_gy)
    
    queue = [start_node]
    visited = {start_node}
    cols = map_w // PATH_GRID_SIZE
    rows = map_h // PATH_GRID_SIZE
    
    while queue:
        current = queue.pop(0)
        if current == target_node: return True
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_node = (current[0] + dx, current[1] + dy)
            if not (0 <= next_node[0] < cols and 0 <= next_node[1] < rows):
                continue
            if next_node in visited:
                continue
            check_rect = pygame.Rect(next_node[0] * PATH_GRID_SIZE, 
                                     next_node[1] * PATH_GRID_SIZE, 
                                     PATH_GRID_SIZE, PATH_GRID_SIZE)
            if is_collision(check_rect, obstacles):
                continue
            visited.add(next_node)
            queue.append(next_node)
    return False