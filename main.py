import pygame
import sys
import random
import math

from config import *
from utils import *
from items import *
from weapons import *
from entities import *

#初期設定
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chronosphere v9.3")
pygame.key.stop_text_input() #これで日本語入力無効化するらしい

clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)

load_all_images()

#ゲーム管理変数
WALLS = []
enemies = []
bullets = []
items = [] 
particles = []
explosions = [] 
EXIT_RECT = pygame.Rect(0, 0, 0, 0)
current_stage = 0
player = Player(0, 0)
game_state = "PLAY"

camera_x = 0
camera_y = 0
last_move_time = 0
current_map_width = MAP_WIDTH
current_map_height = MAP_HEIGHT

# 隠しコマンド入力用バッファ
cheat_input_buffer = ""

def generate_random_map(stage_num):
    global WALLS, enemies, items, EXIT_RECT, player, bullets, explosions
    global current_map_width, current_map_height
    
    #ステージ8生成ルール
    if stage_num == 8:
        current_map_width = 2000
        current_map_height = 2000
        
        WALLS.clear(); enemies.clear(); items.clear(); bullets.clear(); explosions.clear()
        
        WALLS.append(pygame.Rect(0, 0, current_map_width, 20))
        WALLS.append(pygame.Rect(0, current_map_height - 20, current_map_width, 20))
        WALLS.append(pygame.Rect(0, 0, 20, current_map_height))
        WALLS.append(pygame.Rect(current_map_width - 20, 0, 20, current_map_height))
        
        pillar_size = 100
        WALLS.append(pygame.Rect(500, 500, pillar_size, pillar_size))
        WALLS.append(pygame.Rect(1500, 500, pillar_size, pillar_size))
        WALLS.append(pygame.Rect(500, 1500, pillar_size, pillar_size))
        WALLS.append(pygame.Rect(1500, 1500, pillar_size, pillar_size))

        player.rect.center = (1000, 1800)
        player.pos_x, player.pos_y = 1000, 1800
        player.aim((0,0))

        enemies.append(Enemy(1000, 200, "boss", "enemy_boss")) 

        EXIT_RECT = pygame.Rect(1000 - EXIT_W//2, 50, EXIT_W, EXIT_H)
        
        weapon_pool = ["RPG", "Blade", "Rifle"]
        for _ in range(3):
            wx, wy = get_random_free_pos(ITEM_BOX_SIZE, ITEM_BOX_SIZE, WALLS, current_map_width, current_map_height)
            items.append(Item(wx, wy, "weapon", random.choice(weapon_pool)))
            
        return

    ratio = min(1.0, (stage_num - 1) / 6.0)
    min_w, min_h = int(SCREEN_WIDTH * 1.2), int(SCREEN_HEIGHT * 1.2)
    max_w, max_h = MAP_WIDTH, MAP_HEIGHT
    
    current_map_width = int(min_w + (max_w - min_w) * ratio)
    current_map_height = int(min_h + (max_h - min_h) * ratio)
    current_map_width = (current_map_width // PATH_GRID_SIZE) * PATH_GRID_SIZE
    current_map_height = (current_map_height // PATH_GRID_SIZE) * PATH_GRID_SIZE

    while True:
        WALLS.clear(); enemies.clear(); items.clear(); bullets.clear(); explosions.clear()
        
        WALLS.append(pygame.Rect(0, 0, current_map_width, 20))
        WALLS.append(pygame.Rect(0, current_map_height - 20, current_map_width, 20))
        WALLS.append(pygame.Rect(0, 0, 20, current_map_height))
        WALLS.append(pygame.Rect(current_map_width - 20, 0, 20, current_map_height))

        cols = current_map_width // PATH_GRID_SIZE
        rows = current_map_height // PATH_GRID_SIZE
        grid_count = cols * rows
        num_walls = int(grid_count * 0.25)
        
        for _ in range(num_walls):
            gx = random.randint(1, cols - 2)
            gy = random.randint(1, rows - 2)
            x = gx * PATH_GRID_SIZE
            y = gy * PATH_GRID_SIZE
            thickness = 20 
            
            if random.random() > 0.5:
                h = PATH_GRID_SIZE * random.randint(1, 3) + thickness
                w = thickness
            else:
                w = PATH_GRID_SIZE * random.randint(1, 3) + thickness
                h = thickness
            WALLS.append(pygame.Rect(x, y, w, h))

        px, py = get_random_free_pos(PLAYER_HITBOX_SIZE, PLAYER_HITBOX_SIZE, WALLS, current_map_width, current_map_height, padding=50)
        player.rect.center = (px, py)
        player.pos_x, player.pos_y = px, py
        player.aim((0,0)) 

        while True:
            ex, ey = get_random_free_pos(EXIT_W, EXIT_H, WALLS, current_map_width, current_map_height, padding=50)
            min_exit_dist = min(1500, min(current_map_width, current_map_height) * 0.7)
            if math.hypot(ex - px, ey - py) > min_exit_dist:
                EXIT_RECT = pygame.Rect(ex, ey, EXIT_W, EXIT_H)
                break
        
        if is_path_exists(player.rect.center, EXIT_RECT.center, WALLS, current_map_width, current_map_height):
            break 
        else:
            pass

    enemy_types = ["normal", "normal", "fighter"]
    if stage_num > 2: enemy_types += ["sniper", "shielder", "turret"]
    if stage_num > 3: enemy_types += ["bomber", "summoner"]
    if stage_num > 4: enemy_types += ["assassin", "rapid", "ghost"]
    
    num_enemies = 3 + int(27 * ratio)
    
    for _ in range(num_enemies):
        etype = random.choice(enemy_types)
        stats = GAME_SPECS["enemies"][etype]
        ex, ey = get_random_free_pos(stats['hitbox'], stats['hitbox'], WALLS, current_map_width, current_map_height, padding=40)
        img_key = f"enemy_{etype}"
        enemies.append(Enemy(ex, ey, etype, img_key))

    hx, hy = get_random_free_pos(ITEM_BOX_SIZE, ITEM_BOX_SIZE, WALLS, current_map_width, current_map_height)
    items.append(Item(hx, hy, "hp"))
    
    weapon_pool = ["Pistol", "Shotgun", "Rifle", "SMG"]
    if stage_num > 2: weapon_pool += ["Blade", "RPG", "Ricochet"]
    
    if stage_num > 4: weapon_pool += ["Mine"]

    for _ in range(random.randint(1, 2)):
        wx, wy = get_random_free_pos(ITEM_BOX_SIZE, ITEM_BOX_SIZE, WALLS, current_map_width, current_map_height)
        items.append(Item(wx, wy, "weapon", random.choice(weapon_pool)))

def load_stage(stage_num):
    global current_stage
    current_stage = stage_num
    if stage_num > 8: return False 
    generate_random_map(stage_num)
    return True

def update_camera():
    global camera_x, camera_y
    target_x = player.rect.centerx - SCREEN_WIDTH // 2
    target_y = player.rect.centery - SCREEN_HEIGHT // 2
    camera_x = max(0, min(target_x, current_map_width - SCREEN_WIDTH))
    camera_y = max(0, min(target_y, current_map_height - SCREEN_HEIGHT))

def explode(x, y):
    explosions.append(Explosion(x, y))
    
    dist_p = math.hypot(player.rect.centerx - x, player.rect.centery - y)
    if dist_p < EXPLOSION_RADIUS:
        player.hp -= EXPLOSION_DAMAGE
        for _ in range(10): particles.append(Particle(player.rect.centerx, player.rect.centery, ORANGE))

    for e in enemies[:]:
        dist_e = math.hypot(e.rect.centerx - x, e.rect.centery - y)
        if dist_e < EXPLOSION_RADIUS:
            e.hp -= EXPLOSION_DAMAGE
            for _ in range(10): particles.append(Particle(e.rect.centerx, e.rect.centery, ORANGE))
            
            if e.hp <= 0 and e in enemies:
                enemies.remove(e)
                if e.type == 'bomber':
                    explode(e.rect.centerx, e.rect.centery)
                if e.type == 'summoner':
                    for child in e.children:
                        if child in enemies: child.hp = 0

def draw_scene():
    screen.fill(BG_COLOR)
    camera_offset = (camera_x, camera_y)

    screen_rect = screen.get_rect()
    for wall in WALLS:
        draw_rect = wall.move(-camera_x, -camera_y)
        if screen_rect.colliderect(draw_rect):
            pygame.draw.rect(screen, WALL_COLOR, draw_rect, 3)
    
    draw_exit = EXIT_RECT.move(-camera_x, -camera_y)
    screen.blit(IMAGES['exit'], draw_exit)
    
    for item in items: item.draw(screen, camera_offset)
    for b in bullets: b.draw(screen, camera_offset)
    for e in enemies: e.draw(screen, player.rect, WALLS, camera_offset)
    player.draw(screen, obstacles=WALLS, camera_offset=camera_offset)
    
    for p in particles: p.draw(screen, camera_offset)
    for exp in explosions: exp.draw(screen, camera_offset)
    
    surface = screen
    stage_text = f"STAGE {current_stage}/8" if current_stage < 8 else "FINAL STAGE"
    surface.blit(font.render(stage_text, True, WHITE), (20, 20))
    
    hp_y = SCREEN_HEIGHT - HP_ICON_SIZE - 20 
    surface.blit(IMAGES['hp'], (20, hp_y))
    hp_col = GREEN if player.hp > 3 else RED
    surface.blit(font.render(f"{player.hp:.0f}", True, hp_col), (20 + HP_ICON_SIZE + 10, hp_y + 25)) 
    
    w = player.current_weapon
    icon_x = SCREEN_WIDTH - WEAPON_ICON_SIZE - 30
    icon_y = SCREEN_HEIGHT - WEAPON_ICON_SIZE - 30
    surface.blit(IMAGES[w.icon_key], (icon_x, icon_y))
    
    w_name_surf = pygame.font.Font(None, 30).render(w.name, True, WHITE)
    surface.blit(w_name_surf, (icon_x, icon_y - 25))

def draw_game_over(is_clear):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    msg, color = ("MISSION COMPLETED", GREEN) if is_clear else ("GAME OVER", RED)
    text_surf = font.render(msg, True, color)
    screen.blit(text_surf, text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
    retry_surf = font.render("Press [R] to Retry", True, WHITE)
    screen.blit(retry_surf, retry_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)))

#メインループ
player = Player(0, 0)
running = load_stage(1)

while running:
    update_camera()
    camera_offset = (camera_x, camera_y)
    current_time = pygame.time.get_ticks()

    for p in particles[:]:
        p.update()
        if p.life <= 0: particles.remove(p)
    
    for exp in explosions[:]:
        exp.update()
        if exp.life <= 0: explosions.remove(exp)

    action_taken = False
    player_move_vec = (0, 0)
    enemy_move_vecs = []
    bullet_move_vecs = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if game_state == "PLAY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    player.shoot(bullets, enemies, particles)
                    action_taken = True 
                    last_move_time = current_time

            if event.type == pygame.KEYDOWN:
                # 隠しコマンド処理 (Railgunアンロックのみ残存)
                cheat_input_buffer += event.unicode
                if len(cheat_input_buffer) > 20: 
                    cheat_input_buffer = cheat_input_buffer[-20:]
                
                if "railgun" in cheat_input_buffer:
                    print(">>> Cheat Activated: Railgun Equipped")
                    player.weapons["Railgun"].amo = 1
                    player.current_weapon = player.weapons["Railgun"]
                    cheat_input_buffer = "" 
                    for _ in range(20): particles.append(Particle(player.rect.centerx, player.rect.centery, CYAN))
                

        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                player.hp = GAME_SPECS["player"]["hp"]
                player.current_weapon = player.weapons["Pistol"]
                player.railgun_charged = False
                
                load_stage(1)
                particles.clear()
                explosions.clear()
                game_state = "PLAY"

    if game_state == "PLAY" and not action_taken:
        mouse_pressed = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()
        
        if mouse_pressed[0] and not keys[pygame.K_SPACE]:
            if current_time - last_move_time > MOVE_COOLDOWN:
                mouse_pos = pygame.mouse.get_pos()
                vx, vy = player.calculate_move(mouse_pos, WALLS, camera_offset)
                
                if vx != 0 or vy != 0:
                    player_move_vec = (vx, vy)
                    action_taken = True
                    last_move_time = current_time

    if action_taken:
        #召喚用的リスト
        new_enemies_to_add = []

        for e in enemies:
            if e.try_attack(player, bullets, WALLS, particles):
                enemy_move_vecs.append((0, 0))
                
                if e.type == 'summoner':
                    new_minion = e.summon_minion(WALLS)
                    if new_minion:
                        new_enemies_to_add.append(new_minion)
                
                if e.type == 'boss' and e.pending_minions:
                    for m_type in e.pending_minions:
                        bx = e.rect.centerx + random.randint(-100, 100)
                        by = e.rect.centery + random.randint(100, 200)
                        spawn_rect = pygame.Rect(bx, by, 60, 60)
                        if not is_collision(spawn_rect, WALLS):
                            img_key = f"enemy_{m_type}"
                            new_enemies_to_add.append(Enemy(bx, by, m_type, img_key))
                    e.pending_minions = []

            else:
                ex, ey = e.calculate_move(player.rect, WALLS)
                enemy_move_vecs.append((ex, ey))
        
        enemies.extend(new_enemies_to_add)

        for b in bullets:
            bdx, bdy = b.get_step_move()
            bullet_move_vecs.append((bdx, bdy))

        hit_by_enemy_this_turn = []

        for step in range(ANIMATION_STEPS):
            step_vx = player_move_vec[0] / ANIMATION_STEPS
            step_vy = player_move_vec[1] / ANIMATION_STEPS
            player.update_step_pos(step_vx, step_vy)
            
            if is_collision(player.rect, WALLS):
                player.update_step_pos(-step_vx, -step_vy)
            
            update_camera()
            camera_offset = (camera_x, camera_y)
            
            for i, e in enumerate(enemies):
                if i < len(enemy_move_vecs):
                    e.update_step_pos(enemy_move_vecs[i][0]/ANIMATION_STEPS, enemy_move_vecs[i][1]/ANIMATION_STEPS)
            
            for i, b in enumerate(bullets[:]):
                if i < len(bullet_move_vecs):
                    bdx, bdy = bullet_move_vecs[i]
                else:
                    bdx, bdy = b.get_step_move()
                
                b.update_step(bdx, bdy, WALLS)
                
                if b.is_player_bullet:
                    for e in enemies[:]:
                        if e in b.hit_list: continue
                        if b.hitbox.colliderect(e.rect):
                            damage = b.atk
                            if e.type == 'shielder':
                                bullet_angle = math.atan2(b.dy, b.dx)
                                angle_diff = abs(math.degrees(bullet_angle - e.angle)) % 360
                                if angle_diff > 180: angle_diff = 360 - angle_diff
                                if angle_diff > 90: damage = 0 

                            if damage > 0:
                                e.hp -= damage
                                b.hit_list.append(e)
                                for _ in range(5): particles.append(Particle(e.rect.centerx, e.rect.centery, RED))

                            if getattr(b, 'explosive', False):
                                explode(b.hitbox.centerx, b.hitbox.centery)
                                if b in bullets: bullets.remove(b)
                                break

                            if not b.penetration:
                                if b in bullets: bullets.remove(b)
                            
                            if e.hp <= 0 and e in enemies:
                                enemies.remove(e)
                                if e.type == 'bomber': explode(e.rect.centerx, e.rect.centery)
                                if e.type == 'summoner':
                                    for child in e.children:
                                        if child in enemies: child.hp = 0
                            
                            if not b.penetration and damage > 0: break
                
                else:
                    if b.hitbox.colliderect(player.rect):
                        player.hp -= b.atk 
                        for _ in range(5): particles.append(Particle(player.rect.centerx, player.rect.centery, GREEN))
                        if b in bullets: bullets.remove(b)
                
                if b.brg <= 0:
                    if getattr(b, 'explosive', False):
                         explode(b.hitbox.centerx, b.hitbox.centery)
                    if b in bullets: bullets.remove(b)

            for e in enemies[:]:
                if player.rect.colliderect(e.rect):
                    if e not in hit_by_enemy_this_turn:
                        player.hp -= e.atk
                        hit_by_enemy_this_turn.append(e)
                        
                        if e.type == 'bomber':
                            explode(e.rect.centerx, e.rect.centery)
                            if e in enemies: enemies.remove(e)

            for item in items[:]:
                if player.rect.colliderect(item.rect):
                    if item.type == "hp":
                        player.hp += 3
                        items.remove(item)
                    elif item.type == "weapon":
                        player.current_weapon = player.weapons[item.data]
                        items.remove(item)

            draw_scene()
            pygame.display.flip()
            clock.tick(60) 
        
        #終了処理
        for e in enemies[:]:
            if e.hp <= 0:
                if e in enemies: enemies.remove(e)
                if e.type == 'bomber': explode(e.rect.centerx, e.rect.centery)
                if e.type == 'summoner':
                    for child in e.children:
                        if child in enemies: child.hp = 0

    if player.hp <= 0:
        game_state = "GAMEOVER"

    player.aim(camera_offset)
    if game_state == "PLAY":
        if (not enemies) or player.rect.colliderect(EXIT_RECT):
            particles.clear()
            if not load_stage(current_stage + 1): game_state = "CLEAR"

    draw_scene()
    if game_state != "PLAY": draw_game_over(game_state == "CLEAR")

    pygame.display.flip()
    clock.tick(60) 

pygame.quit()
sys.exit()