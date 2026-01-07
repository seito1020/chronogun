import pygame

#画面設定
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

#マップ設定
MAP_WIDTH = 3000
MAP_HEIGHT = 2000

#色の定義
BG_COLOR = (20, 10, 40)
WALL_COLOR = (255, 100, 50)
AIM_LINE_COLOR = (100, 255, 100)
ENEMY_AIM_COLOR = (255, 0, 0, 128)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (200, 0, 255)
PINK = (255, 105, 180)

#レールガン・タレット用カラー
RAILGUN_COLOR = (0, 255, 255)
TURRET_LASER_COLOR = (255, 50, 50)
CHARGE_COLOR = (255, 0, 255)

#サイズ設定
PLAYER_VISUAL_SIZE = 60
PLAYER_HITBOX_SIZE = 40

ENEMY_SIZE = 60
ENEMY_HITBOX_SIZE = 40

WEAPON_ICON_SIZE = 80
HP_ICON_SIZE = 80

ITEM_BOX_SIZE = 70
ITEM_IMAGE_SIZE = 60

BULLET_W, BULLET_H = 32, 16
BULLET_HITBOX_SIZE = 8

EXIT_W, EXIT_H = 100, 100

# --- ゲームバランス設定 ---
MOVE_COOLDOWN = 300
PATH_GRID_SIZE = 100
NAV_GRID_SIZE = 40
ANIMATION_STEPS = 6

# 爆発設定
EXPLOSION_RADIUS = 150
EXPLOSION_DAMAGE = 5

# タレット旋回速度
TURRET_ROT_SPEED = 3.0

# --- ステータス設定 ---
GAME_SPECS = {
    "player": {
        "hp": 10,
        "max_hp": 10,
        "spd": 5.0,
    },
    "weapons": {
        "Pistol":  {"atk": 1,   "amo": 1, "bsp": 6.0, "brg": "inf", "pen": False, "img": "gun_pistol"},
        "Shotgun": {"atk": 2,   "amo": 5, "bsp": 7.0, "brg": 3.5,   "pen": False, "img": "gun_shotgun"},
        "Rifle":   {"atk": 3,   "amo": 1, "bsp": 12.0,"brg": "inf", "pen": True,  "img": "gun_rifle"},
        "SMG":     {"atk": 0.5, "amo": 5, "bsp": 6.0, "brg": "inf", "pen": False, "img": "gun_smg"},
        "RPG":     {"atk": 10,  "amo": 1, "bsp": 4.0, "brg": "inf", "pen": False, "img": "gun_rpg"},
        "Blade":   {"atk": 10,  "amo": 1, "bsp": 0,   "brg": 0,     "pen": True,  "img": "gun_blade"},
        "Railgun": {"atk": 50,  "amo": 1, "bsp": 0,   "brg": "inf", "pen": True,  "img": "gun_railgun"},
        "Ricochet": {"atk": 2,  "amo": 1, "bsp": 5.0, "brg": "inf", "pen": False, "img": "gun_ricochet"},
        "Mine":     {"atk": 10, "amo": 1, "bsp": 0,   "brg": "inf", "pen": False, "img": "gun_mine"},
    },
    "enemies": {
        "normal":   {"hp": 1, "atk": 1, "spd": 2.0, "rng": 6.0,  "amo": 1, "bsp": 3.0, "w": 60, "h": 60, "hitbox": 40},
        "sniper":   {"hp": 1, "atk": 5, "spd": 1.5, "rng": 18.0, "amo": 1, "bsp": 8.0, "w": 60, "h": 60, "hitbox": 40},
        "fighter":  {"hp": 3, "atk": 4, "spd": 4.5, "rng": 0,    "amo": 0, "bsp": 0,   "w": 60, "h": 60, "hitbox": 40},
        "assassin": {"hp": 1, "atk": 5, "spd": 8.0, "rng": 0,    "amo": 0, "bsp": 0,   "w": 50, "h": 50, "hitbox": 30},
        "rapid":    {"hp": 1, "atk": 0.5,"spd": 2.0,"rng": 8.0,  "amo": 5, "bsp": 4.0, "w": 60, "h": 60, "hitbox": 40},
        "bomber":   {"hp": 2, "atk": 8,"spd": 5.0, "rng": 0,    "amo": 0, "bsp": 0,   "w": 80, "h": 80, "hitbox": 60},
        "shielder": {"hp": 5, "atk": 2, "spd": 1.5, "rng": 4.0,  "amo": 1, "bsp": 2.5, "w": 70, "h": 70, "hitbox": 50},
        "ghost":    {"hp": 2, "atk": 3, "spd": 2.5, "rng": 0,    "amo": 0, "bsp": 0,   "w": 60, "h": 60, "hitbox": 40},
        "summoner": {"hp": 3, "atk": 0, "spd": 3.0, "rng": 10.0, "amo": 0, "bsp": 0,   "w": 60, "h": 60, "hitbox": 40},
        "turret":   {"hp": 10,"atk": 8, "spd": 0.0, "rng": 15.0, "amo": 1, "bsp": 0,   "w": 70, "h": 70, "hitbox": 50},
        "boss":     {"hp": 50,"atk": 2, "spd": 2.5, "rng": 25.0, "amo": 1, "bsp": 5.0, "w": 120, "h": 120, "hitbox": 80}
    }
}