# snake_game/config.py

# --- Grid ---
CELL_SIZE = 20
GRID_W = 25
GRID_H = 20
GAME_W = CELL_SIZE * GRID_W   # 500
GAME_H = CELL_SIZE * GRID_H   # 400
HUD_H = 60
WINDOW_W = GAME_W              # 500
WINDOW_H = GAME_H + HUD_H     # 460
FPS = 60

# --- Colors ---
COLOR_BG = (26, 58, 42)
COLOR_GRID = (30, 64, 47)
COLOR_WALL_FIXED = (200, 184, 154)
COLOR_HUD_BG = (10, 10, 10)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_HEART = (220, 50, 50)

# Gym dynamic wall colors (by gym index 0-7)
GYM_WALL_COLORS = [
    (160, 160, 150),   # 0 ニビ - stone gray
    (60, 120, 220),    # 1 ハナダ - water blue
    (240, 220, 40),    # 2 クチバ - electric yellow
    (60, 180, 80),     # 3 タマムシ - grass green
    (160, 60, 200),    # 4 セキチク - poison purple
    (220, 100, 200),   # 5 ヤマブキ - psychic pink
    (240, 100, 40),    # 6 グレン - fire orange
    (100, 40, 200),    # 7 トキワ - dragon purple
]

# Gym background accent colors (distinctive per type)
GYM_BG_ACCENTS = [
    (40, 36, 30),  # 0 ニビ - dark stone cave
    (16, 34, 60),  # 1 ハナダ - deep ocean
    (26, 26, 16),  # 2 クチバ - stormy gray-yellow
    (16, 44, 16),  # 3 タマムシ - deep forest
    (32, 16, 46),  # 4 セキチク - dark toxic purple
    (36, 16, 40),  # 5 ヤマブキ - deep psychic indigo
    (50, 16, 10),  # 6 グレン - volcanic dark red
    (10, 10, 30),  # 7 トキワ - deep dragon navy
]

# Gym grid line colors (themed per gym type)
GYM_GRID_COLORS = [
    (55, 50, 42),   # 0 ニビ - stone
    (22, 46, 80),   # 1 ハナダ - water
    (42, 42, 22),   # 2 クチバ - electric
    (22, 60, 22),   # 3 タマムシ - grass
    (46, 22, 62),   # 4 セキチク - poison
    (52, 22, 56),   # 5 ヤマブキ - psychic
    (65, 26, 12),   # 6 グレン - fire
    (15, 15, 46),   # 7 トキワ - dragon
]

# --- Difficulty ---
DIFFICULTY_NAMES = {
    'easy': 'かんたん',
    'normal': 'ふつう',
    'hard': 'むずかしい',
}
BASE_SPEED = {'easy': 4, 'normal': 6, 'hard': 8}   # steps/sec
SPEED_CAP  = {'easy': 10, 'normal': 12, 'hard': 14}
SPEED_PER_10PTS = 1
WALL_INTERVAL_MULT = {'easy': 1.4, 'normal': 1.0, 'hard': 0.7}

# --- Lives ---
STARTING_LIVES = 1

# --- Ball timers (seconds) ---
SUPER_BALL_INTERVAL_MIN = 25
SUPER_BALL_INTERVAL_MAX = 35
SUPER_BALL_LIFESPAN = 30

MASTER_BALL_TIMER_MIN = 20
MASTER_BALL_TIMER_MAX = 40
MASTER_BALL_SPAWN_CHANCE = 0.30
MASTER_BALL_LIFESPAN = 8

# Ball scores
BALL_SCORES = {
    'normal': 1,
    'super': 2,
    'master': 5,
}

# --- Dynamic wall strip length ---
DYNAMIC_WALL_LEN_MIN = 2
DYNAMIC_WALL_LEN_MAX = 5

# --- Gym wall dynamic parameters (index = gym 0..7) ---
# (lifespan_sec, cap, interval_normal_sec)
GYM_WALL_PARAMS = [
    (40, 3, 45),   # 0 ニビ
    (30, 4, 38),   # 1 ハナダ
    (25, 5, 32),   # 2 クチバ
    (30, 6, 27),   # 3 タマムシ
    (20, 7, 22),   # 4 セキチク
    (22, 8, 18),   # 5 ヤマブキ
    (25, 9, 13),   # 6 グレン
    (50, 12, 8),   # 7 トキワ
]

# --- Gym target scores ---
GYM_TARGETS = [5, 7, 10, 13, 16, 20, 25, 30]

# --- GYM_CLEAR display duration ---
GYM_CLEAR_DURATION = 0.5  # seconds

# --- Ending animation timing ---
ENDING_CONGRATULATIONS_DURATION = 3.0  # seconds

# --- Sound ---
SOUND_ENABLED = True  # set False on environments without audio

# --- Save path ---
import os
SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'save', 'save.json')
