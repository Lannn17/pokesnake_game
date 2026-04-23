# Snake Game Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Pokémon-themed Snake game in Python + pygame with 8 Kanto gym levels, pixel art GB style, badge/lives system, and Hakuryu→Dragonite ending animation.

**Architecture:** Modular pygame game with a central state machine in `game.py` orchestrating independent modules for snake logic, level/wall data, ball timers, rendering, and JSON save. All sprites are generated programmatically via `sprites.py` using `pygame.draw` — no external image files required. All tunable constants live in `config.py`.

**Tech Stack:** Python 3.10+, pygame 2.x, pytest (testing), json (stdlib)

---

## File Map

| File | Role |
|------|------|
| `snake_game/config.py` | All constants: grid, colors, speeds, timers, scores |
| `snake_game/snake.py` | Pure logic: position list, direction, move, grow, collision |
| `snake_game/level.py` | Gym dataclasses, initial wall layouts, dynamic wall spawn/expire |
| `snake_game/ball.py` | Ball state, モンスターボール/スーパーボール/マスターボール timers |
| `snake_game/save.py` | JSON read/write for `save/save.json` |
| `snake_game/sprites.py` | Generates all pygame.Surface sprites with pygame.draw |
| `snake_game/renderer.py` | All blit/draw calls: game area, HUD, menus, animations |
| `snake_game/game.py` | State machine + per-frame update orchestration |
| `snake_game/main.py` | pygame init, clock, top-level loop |
| `tests/test_snake.py` | Unit tests for snake.py |
| `tests/test_level.py` | Unit tests for level.py dynamic wall logic |
| `tests/test_ball.py` | Unit tests for ball.py timer logic |
| `tests/test_save.py` | Unit tests for save.py |

---

## Task 1: Project Setup

**Files:**
- Create: `snake_game/` directory and all subdirectories
- Create: `snake_game/config.py`
- Create: `tests/__init__.py`
- Create: `requirements.txt`

- [ ] **Step 1: Create directory structure**

```bash
cd "C:/Users/mcc/Desktop/AI研修2026"
mkdir -p snake_game/save
mkdir -p tests
touch tests/__init__.py
```

- [ ] **Step 2: Create requirements.txt**

```
pygame>=2.1.0
pytest>=7.0.0
```

- [ ] **Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: pygame and pytest installed successfully.

- [ ] **Step 4: Create `snake_game/config.py`**

```python
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

# Gym background accent colors (subtle tint, drawn behind grid)
GYM_BG_ACCENTS = [
    (28, 62, 44),  # ニビ
    (24, 58, 52),  # ハナダ
    (32, 60, 36),  # クチバ
    (26, 62, 38),  # タマムシ
    (32, 52, 44),  # セキチク
    (32, 52, 48),  # ヤマブキ
    (36, 52, 36),  # グレン
    (28, 48, 52),  # トキワ
]

# --- Difficulty ---
# difficulty keys: 'easy', 'normal', 'hard'
DIFFICULTY_NAMES = {
    'easy': 'かんたん',
    'normal': 'ふつう',
    'hard': 'むずかしい',
}
BASE_SPEED = {'easy': 8, 'normal': 12, 'hard': 16}   # steps/sec
SPEED_CAP  = {'easy': 14, 'normal': 18, 'hard': 22}
SPEED_PER_10PTS = 1   # +1 step/s per 10 per-gym points
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
GYM_TARGETS = [10, 15, 22, 30, 40, 50, 62, 75]

# --- GYM_CLEAR display duration ---
GYM_CLEAR_DURATION = 0.5  # seconds

# --- Ending animation timing ---
ENDING_CONGRATULATIONS_DURATION = 3.0  # seconds

# --- Sound ---
SOUND_ENABLED = True  # set False on environments without audio; all sound calls check this flag

# --- Save path ---
import os
SAVE_PATH = os.path.join(os.path.dirname(__file__), '..', 'snake_game', 'save', 'save.json')
```

- [ ] **Step 5: Commit**

```bash
git add snake_game/config.py requirements.txt tests/__init__.py
git commit -m "feat: project setup and config constants"
```

---

## Task 2: Snake Logic

**Files:**
- Create: `snake_game/snake.py`
- Create: `tests/test_snake.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_snake.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from snake_game.snake import Snake

def test_initial_state():
    s = Snake(start=(5, 10), direction=(1, 0), length=3)
    assert len(s.body) == 3
    assert s.body[0] == (5, 10)
    assert s.direction == (1, 0)

def test_move_right():
    s = Snake(start=(5, 10), direction=(1, 0), length=3)
    s.move()
    assert s.body[0] == (6, 10)
    assert len(s.body) == 3  # no growth

def test_grow():
    s = Snake(start=(5, 10), direction=(1, 0), length=3)
    s.grow()
    s.move()
    assert len(s.body) == 4

def test_self_collision_false_when_short():
    s = Snake(start=(5, 10), direction=(1, 0), length=3)
    assert s.check_self_collision() is False

def test_self_collision_true():
    s = Snake(start=(5, 10), direction=(1, 0), length=3)
    # Manually craft a collision: head at same position as body segment
    s.body = [(5, 10), (4, 10), (5, 10)]
    assert s.check_self_collision() is True

def test_set_direction_ignores_reverse():
    s = Snake(start=(5, 10), direction=(1, 0), length=3)
    s.set_direction((-1, 0))  # reverse — should be ignored
    assert s.direction == (1, 0)

def test_set_direction_accepts_perpendicular():
    s = Snake(start=(5, 10), direction=(1, 0), length=3)
    s.set_direction((0, -1))
    assert s.direction == (0, -1)

def test_occupies():
    s = Snake(start=(5, 10), direction=(1, 0), length=3)
    assert s.occupies(5, 10) is True
    assert s.occupies(4, 10) is True
    assert s.occupies(99, 99) is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd "C:/Users/mcc/Desktop/AI研修2026"
pytest tests/test_snake.py -v
```

Expected: ImportError or NameError (snake.py does not exist).

- [ ] **Step 3: Implement `snake_game/snake.py`**

```python
# snake_game/snake.py

class Snake:
    """Pure logic snake — no pygame dependency."""

    def __init__(self, start: tuple[int,int], direction: tuple[int,int], length: int = 3):
        x, y = start
        dx, dy = direction
        # body[0] = head; body[-1] = tail
        self.body = [(x - dx * i, y - dy * i) for i in range(length)]
        self.direction = direction
        self._pending_growth = 0

    def set_direction(self, new_dir: tuple[int,int]):
        """Ignore reversal direction."""
        if (new_dir[0] + self.direction[0], new_dir[1] + self.direction[1]) != (0, 0):
            self.direction = new_dir

    def grow(self):
        """Queue one extra segment for next move."""
        self._pending_growth += 1

    def move(self):
        """Advance the snake one cell in current direction."""
        hx, hy = self.body[0]
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)
        self.body.insert(0, new_head)
        if self._pending_growth > 0:
            self._pending_growth -= 1
        else:
            self.body.pop()

    def check_self_collision(self) -> bool:
        return self.body[0] in self.body[1:]

    def occupies(self, x: int, y: int) -> bool:
        return (x, y) in self.body

    @property
    def head(self) -> tuple[int,int]:
        return self.body[0]

    @property
    def cells(self) -> list[tuple[int,int]]:
        return self.body
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_snake.py -v
```

Expected: 8 PASSED.

- [ ] **Step 5: Commit**

```bash
git add snake_game/snake.py tests/test_snake.py
git commit -m "feat: snake pure logic with TDD"
```

---

## Task 3: Level System

**Files:**
- Create: `snake_game/level.py`
- Create: `tests/test_level.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_level.py
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from snake_game.level import Level, DynamicWall
from snake_game.config import GYM_TARGETS

def test_level_has_8_gyms():
    from snake_game.level import GYMS
    assert len(GYMS) == 8

def test_gym_target_scores():
    from snake_game.level import GYMS
    for i, gym in enumerate(GYMS):
        assert gym.target_score == GYM_TARGETS[i]

def test_level_loads_gym():
    level = Level(gym_index=0, difficulty='normal')
    assert len(level.fixed_walls) > 0
    assert level.target_score == GYM_TARGETS[0]

def test_dynamic_wall_expiry():
    wall = DynamicWall(x=5, y=5, lifespan=2.0, spawn_time=0.0)
    assert wall.is_expired(current_time=1.0) is False
    assert wall.is_expired(current_time=2.5) is True

def test_dynamic_wall_alpha():
    wall = DynamicWall(x=5, y=5, lifespan=3.0, spawn_time=0.0)
    # at t=0 (full life), alpha should be 255
    assert wall.alpha(current_time=0.0) == 255
    # at t=1.5 (half life remaining within fade zone), alpha < 255
    assert wall.alpha(current_time=1.5) < 255

def test_spawn_wall_respects_cap():
    level = Level(gym_index=7, difficulty='normal')  # cap=12
    occupied = set()
    for _ in range(20):
        level.try_spawn_wall(current_time=1000.0, occupied_cells=occupied)
    assert len(level.dynamic_walls) <= 12

def test_spawn_wall_avoids_occupied():
    level = Level(gym_index=0, difficulty='normal')
    occupied = {(x, y) for x in range(25) for y in range(20) if (x, y) not in [(12, 10)]}
    # Only (12,10) is free
    level.try_spawn_wall(current_time=1000.0, occupied_cells=occupied)
    # Either spawns at (12,10) or doesn't spawn (if interval not met)
    for w in level.dynamic_walls:
        assert (w.x, w.y) not in occupied
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_level.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `snake_game/level.py`**

```python
# snake_game/level.py
import random
import time
from dataclasses import dataclass, field
from typing import Optional
from snake_game.config import (
    GYM_TARGETS, GYM_WALL_PARAMS, GYM_WALL_COLORS, GYM_BG_ACCENTS,
    WALL_INTERVAL_MULT, GRID_W, GRID_H
)


@dataclass
class GymDef:
    """Static gym definition."""
    name: str          # Japanese city name
    leader: str        # Japanese leader name
    type_name: str     # Japanese type name
    wall_color: tuple
    bg_accent: tuple
    target_score: int
    wall_params: tuple  # (lifespan, cap, interval_normal)
    fixed_walls: list   # list of (x, y)


@dataclass
class DynamicWall:
    x: int
    y: int
    lifespan: float
    spawn_time: float

    def is_expired(self, current_time: float) -> bool:
        return (current_time - self.spawn_time) >= self.lifespan

    def age(self, current_time: float) -> float:
        return current_time - self.spawn_time

    def remaining(self, current_time: float) -> float:
        return max(0.0, self.lifespan - self.age(current_time))

    def alpha(self, current_time: float) -> int:
        """255 until final 3s, then linear fade. Floors at 60."""
        rem = self.remaining(current_time)
        if rem >= 3.0:
            return 255
        return max(60, int(255 * (rem / 3.0)))

    def is_flashing(self, current_time: float) -> bool:
        """True in final 1s (used to drive flash render)."""
        return self.remaining(current_time) <= 1.0


def _build_gym(i: int, name: str, leader: str, type_name: str, walls: list) -> GymDef:
    lifespan, cap, interval = GYM_WALL_PARAMS[i]
    return GymDef(
        name=name, leader=leader, type_name=type_name,
        wall_color=GYM_WALL_COLORS[i],
        bg_accent=GYM_BG_ACCENTS[i],
        target_score=GYM_TARGETS[i],
        wall_params=(lifespan, cap, interval),
        fixed_walls=walls,
    )


# --- Fixed wall layouts ---
def _nibi_walls():
    """Sparse corner stones."""
    return [
        (1,1),(2,1),(1,2),
        (23,1),(22,1),(23,2),
        (1,18),(2,18),(1,17),
        (23,18),(22,18),(23,17),
    ]

def _hanada_walls():
    """Central vertical channels."""
    walls = []
    for y in range(5, 16):
        walls.append((8, y))
        walls.append((16, y))
    return walls

def _kuchiba_walls():
    """Lightning zigzag."""
    walls = []
    pts = [(3,3),(4,3),(5,3),(5,4),(5,5),(6,5),(7,5),(7,6),(7,7),
           (17,12),(18,12),(19,12),(19,13),(19,14),(20,14),(21,14),(21,15),(21,16)]
    return pts

def _tamamushi_walls():
    """Scattered tree clusters (4 clusters)."""
    clusters = [(5,4),(6,4),(5,5),(17,4),(18,4),(17,5),(5,15),(6,15),(5,16),(17,15),(18,15),(17,16)]
    center = [(11,8),(12,8),(13,8),(12,7),(11,12),(12,12),(13,12),(12,13)]
    return clusters + center

def _sekichiku_walls():
    """Grid mesh pattern."""
    walls = []
    for x in range(4, 22, 4):
        for y in range(4, 17, 4):
            walls.append((x, y))
            walls.append((x+1, y))
    return walls

def _yamabuki_walls():
    """Symmetric cross walls."""
    walls = []
    # horizontal bars
    for x in range(6, 11):
        walls.append((x, 9))
        walls.append((x, 11))
        walls.append((25-x-1, 9))
        walls.append((25-x-1, 11))
    # vertical bars
    for y in range(6, 11):
        walls.append((12, y))
        walls.append((12, 20-y-1))
    return list(set(walls))

def _guren_walls():
    """Volcanic rock corridors."""
    walls = []
    for x in range(3, 10):
        walls.append((x, 7))
    for x in range(15, 22):
        walls.append((x, 13))
    for y in range(3, 8):
        walls.append((9, y))
    for y in range(13, 18):
        walls.append((15, y))
    return list(set(walls))

def _tokiwa_walls():
    """Spiral inner maze."""
    walls = []
    # outer spiral ring
    for x in range(4, 21):
        walls.append((x, 4))
        walls.append((x, 16))
    for y in range(4, 17):
        walls.append((4, y))
        walls.append((20, y))
    # inner ring (partial)
    for x in range(7, 18):
        walls.append((x, 7))
    for y in range(7, 14):
        walls.append((17, y))
    for x in range(7, 17):
        walls.append((x, 13))
    for y in range(10, 14):
        walls.append((7, y))
    # remove duplicate and opening
    walls = list(set(walls))
    # openings so it isn't fully closed
    openings = [(12,4),(20,10),(12,7),(17,10),(10,13),(7,10)]
    return [w for w in walls if w not in openings]


GYMS = [
    _build_gym(0, 'ニビシティ', 'タケシ', 'いわ', _nibi_walls()),
    _build_gym(1, 'ハナダシティ', 'カスミ', 'みず', _hanada_walls()),
    _build_gym(2, 'クチバシティ', 'マチス', 'でんき', _kuchiba_walls()),
    _build_gym(3, 'タマムシシティ', 'エリカ', 'くさ', _tamamushi_walls()),
    _build_gym(4, 'セキチクシティ', 'キョウ', 'どく', _sekichiku_walls()),
    _build_gym(5, 'ヤマブキシティ', 'ナツメ', 'エスパー', _yamabuki_walls()),
    _build_gym(6, 'グレンタウン', 'カツラ', 'ほのお', _guren_walls()),
    _build_gym(7, 'トキワシティ', 'サカキ', 'ドラゴン', _tokiwa_walls()),
]


class Level:
    """Runtime level state: loads a gym and manages dynamic walls."""

    def __init__(self, gym_index: int, difficulty: str):
        self.gym_index = gym_index
        self.difficulty = difficulty
        gym = GYMS[gym_index]
        self.fixed_walls: set[tuple[int,int]] = set(map(tuple, gym.fixed_walls))
        self.target_score = gym.target_score
        self.wall_color = gym.wall_color
        self.bg_accent = gym.bg_accent
        lifespan, cap, interval_normal = gym.wall_params
        self.wall_lifespan = lifespan
        self.wall_cap = cap
        self.wall_interval = interval_normal * WALL_INTERVAL_MULT[difficulty]
        self.dynamic_walls: list[DynamicWall] = []
        self._next_spawn_time: float = self.wall_interval  # seconds from level start
        self._level_start_time: Optional[float] = None

    def start(self, now: float):
        """Call when PLAYING begins for this gym."""
        self._level_start_time = now
        self._next_spawn_time = now + self.wall_interval
        self.dynamic_walls = []

    def _elapsed(self, now: float) -> float:
        return now - (self._level_start_time or now)

    def all_wall_cells(self) -> set[tuple[int,int]]:
        return self.fixed_walls | {(w.x, w.y) for w in self.dynamic_walls}

    def try_spawn_wall(self, current_time: float, occupied_cells: set[tuple[int,int]]):
        """Attempt to spawn a dynamic wall if interval elapsed."""
        if current_time < self._next_spawn_time:
            return
        self._next_spawn_time = current_time + self.wall_interval

        # Remove expired walls first
        self.dynamic_walls = [w for w in self.dynamic_walls
                               if not w.is_expired(current_time)]

        # Enforce cap: remove oldest if at cap
        if len(self.dynamic_walls) >= self.wall_cap:
            self.dynamic_walls.pop(0)

        # Find a valid cell
        all_occupied = occupied_cells | self.all_wall_cells()
        candidates = [
            (x, y)
            for x in range(1, GRID_W - 1)
            for y in range(1, GRID_H - 1)
            if (x, y) not in all_occupied
        ]
        if not candidates:
            return
        x, y = random.choice(candidates)
        self.dynamic_walls.append(DynamicWall(x=x, y=y,
                                               lifespan=self.wall_lifespan,
                                               spawn_time=current_time))

    def remove_expired(self, current_time: float):
        self.dynamic_walls = [w for w in self.dynamic_walls
                               if not w.is_expired(current_time)]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_level.py -v
```

Expected: all PASSED.

- [ ] **Step 5: Commit**

```bash
git add snake_game/level.py tests/test_level.py
git commit -m "feat: level system with gym definitions and dynamic walls"
```

---

## Task 4: Ball System

**Files:**
- Create: `snake_game/ball.py`
- Create: `tests/test_ball.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_ball.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from snake_game.ball import BallManager

def make_manager():
    occupied = set()  # no walls
    return BallManager(wall_cells=occupied, grid_w=25, grid_h=20)

def test_initial_has_two_balls():
    bm = make_manager()
    bm.reset(now=0.0)
    balls = bm.get_all_balls()
    assert len(balls) == 2
    assert all(b['type'] == 'normal' for b in balls)

def test_eat_normal_ball_respawns():
    bm = make_manager()
    bm.reset(now=0.0)
    pos = bm.get_all_balls()[0]['pos']
    score = bm.try_eat(pos, now=0.0, snake_cells=set())
    assert score == 1
    # Still 2 balls
    assert len(bm.get_all_balls()) == 2

def test_super_ball_appears_after_interval():
    bm = make_manager()
    bm.reset(now=0.0)
    # Force super ball spawn by advancing time past max interval
    bm.update(now=36.0, snake_cells=set(), head_adjacent=set())
    balls = bm.get_all_balls()
    types = [b['type'] for b in balls]
    assert 'super' in types

def test_master_ball_score():
    bm = make_manager()
    bm.reset(now=0.0)
    # Inject master ball directly for test
    bm._master_ball = {'pos': (10, 10), 'type': 'master', 'expire_time': 100.0}
    score = bm.try_eat((10, 10), now=1.0, snake_cells=set())
    assert score == 5

def test_no_spawn_on_wall():
    bm = BallManager(wall_cells={(x, y) for x in range(25) for y in range(20)
                                  if (x, y) != (12, 10)},
                     grid_w=25, grid_h=20)
    bm.reset(now=0.0)
    for b in bm.get_all_balls():
        assert b['pos'] == (12, 10)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_ball.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `snake_game/ball.py`**

```python
# snake_game/ball.py
import random
from typing import Optional
from snake_game.config import (
    BALL_SCORES,
    SUPER_BALL_INTERVAL_MIN, SUPER_BALL_INTERVAL_MAX, SUPER_BALL_LIFESPAN,
    MASTER_BALL_TIMER_MIN, MASTER_BALL_TIMER_MAX,
    MASTER_BALL_SPAWN_CHANCE, MASTER_BALL_LIFESPAN,
    GRID_W, GRID_H,
)


class BallManager:
    """Manages all Poké Balls on the map."""

    def __init__(self, wall_cells: set, grid_w: int = GRID_W, grid_h: int = GRID_H):
        self._walls = wall_cells
        self._gw = grid_w
        self._gh = grid_h
        self._balls: list[dict] = []          # list of {'pos', 'type', 'expire_time'|None}
        self._master_ball: Optional[dict] = None
        self._super_next: float = 0.0
        self._master_next: float = 0.0

    def reset(self, now: float):
        self._balls = []
        self._master_ball = None
        self._spawn_normal(now)
        self._spawn_normal(now)
        self._super_next = now + random.uniform(SUPER_BALL_INTERVAL_MIN, SUPER_BALL_INTERVAL_MAX)
        self._master_next = now + random.uniform(MASTER_BALL_TIMER_MIN, MASTER_BALL_TIMER_MAX)

    def update(self, now: float, snake_cells: set, head_adjacent: set):
        """Call each game tick. Handles expiry and new spawns."""
        # Revert expired super balls to normal (same cell), then filter truly expired normals
        for b in self._balls:
            if b['type'] == 'super' and b['expire_time'] and now >= b['expire_time']:
                b['type'] = 'normal'
                b['expire_time'] = None
                self._super_next = now + random.uniform(SUPER_BALL_INTERVAL_MIN,
                                                         SUPER_BALL_INTERVAL_MAX)

        # Ensure at least 1 normal ball
        normals = [b for b in self._balls if b['type'] == 'normal']
        if not normals:
            self._spawn_normal(now, snake_cells)

        # Super ball spawn
        if now >= self._super_next:
            self._super_next = now + random.uniform(SUPER_BALL_INTERVAL_MIN, SUPER_BALL_INTERVAL_MAX)
            normals = [b for b in self._balls if b['type'] == 'normal']
            if normals:
                target = random.choice(normals)
                target['type'] = 'super'
                target['expire_time'] = now + SUPER_BALL_LIFESPAN

        # Master ball timer
        if self._master_ball is None and now >= self._master_next:
            self._master_next = now + random.uniform(MASTER_BALL_TIMER_MIN, MASTER_BALL_TIMER_MAX)
            if random.random() < MASTER_BALL_SPAWN_CHANCE:
                pos = self._free_cell(snake_cells)
                if pos:
                    self._master_ball = {
                        'pos': pos, 'type': 'master',
                        'expire_time': now + MASTER_BALL_LIFESPAN,
                    }

        # Expire master ball
        if self._master_ball and now >= self._master_ball['expire_time']:
            self._master_ball = None
            self._master_next = now + random.uniform(MASTER_BALL_TIMER_MIN, MASTER_BALL_TIMER_MAX)

    def try_eat(self, pos: tuple, now: float, snake_cells: set) -> int:
        """Returns score if pos matches a ball, else 0."""
        for b in self._balls:
            if b['pos'] == pos:
                score = BALL_SCORES[b['type']]
                self._balls.remove(b)
                self._spawn_normal(now, snake_cells)
                if b['type'] == 'super':
                    self._super_next = now + random.uniform(SUPER_BALL_INTERVAL_MIN,
                                                             SUPER_BALL_INTERVAL_MAX)
                return score
        if self._master_ball and self._master_ball['pos'] == pos:
            score = BALL_SCORES['master']
            self._master_ball = None
            self._master_next = now + random.uniform(MASTER_BALL_TIMER_MIN, MASTER_BALL_TIMER_MAX)
            return score
        return 0

    def get_all_balls(self) -> list[dict]:
        result = list(self._balls)
        if self._master_ball:
            result.append(self._master_ball)
        return result

    def master_ball_remaining(self, now: float) -> float:
        if self._master_ball:
            return max(0.0, self._master_ball['expire_time'] - now)
        return 0.0

    def master_ball_active(self) -> bool:
        return self._master_ball is not None

    def all_ball_cells(self) -> set:
        cells = {b['pos'] for b in self._balls}
        if self._master_ball:
            cells.add(self._master_ball['pos'])
        return cells

    def _free_cell(self, snake_cells: set = None) -> Optional[tuple]:
        occupied = self._walls | self.all_ball_cells() | (snake_cells or set())
        candidates = [
            (x, y) for x in range(self._gw) for y in range(self._gh)
            if (x, y) not in occupied
        ]
        return random.choice(candidates) if candidates else None

    def _spawn_normal(self, now: float, snake_cells: set = None):
        pos = self._free_cell(snake_cells)
        if pos:
            self._balls.append({'pos': pos, 'type': 'normal', 'expire_time': None})
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_ball.py -v
```

Expected: all PASSED.

- [ ] **Step 5: Commit**

```bash
git add snake_game/ball.py tests/test_ball.py
git commit -m "feat: ball system with timer logic"
```

---

## Task 5: Save System

**Files:**
- Create: `snake_game/save.py`
- Create: `tests/test_save.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_save.py
import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import snake_game.save as save_module

def make_tmp_path(tmp_dir):
    return os.path.join(tmp_dir, 'save.json')

def test_no_save_returns_none(tmp_path):
    path = str(tmp_path / 'save.json')
    assert save_module.load(path) is None

def test_save_and_load(tmp_path):
    path = str(tmp_path / 'save.json')
    data = save_module.new_save('normal')
    save_module.write(data, path)
    loaded = save_module.load(path)
    assert loaded['difficulty'] == 'normal'
    assert loaded['lives'] == 1
    assert loaded['current_gym'] == 0

def test_delete_save(tmp_path):
    path = str(tmp_path / 'save.json')
    data = save_module.new_save('easy')
    save_module.write(data, path)
    save_module.delete(path)
    assert save_module.load(path) is None

def test_new_save_structure(tmp_path):
    data = save_module.new_save('hard')
    assert len(data['badges']) == 8
    assert len(data['best_scores']) == 8
    assert data['completed'] is False
    assert data['total_clear_time'] == 0.0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_save.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `snake_game/save.py`**

```python
# snake_game/save.py
import json
import os
from snake_game.config import STARTING_LIVES


def new_save(difficulty: str) -> dict:
    return {
        'current_gym': 0,
        'lives': STARTING_LIVES,
        'badges': [False] * 8,
        'total_score': 0,
        'best_scores': [0] * 8,
        'total_clear_time': 0.0,
        'difficulty': difficulty,
        'completed': False,
    }


def load(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def write(data: dict, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def delete(path: str):
    if os.path.exists(path):
        os.remove(path)
```

- [ ] **Step 4: Run all tests**

```bash
pytest tests/ -v
```

Expected: all PASSED (snake, level, ball, save).

- [ ] **Step 5: Commit**

```bash
git add snake_game/save.py tests/test_save.py
git commit -m "feat: save system with JSON read/write"
```

---

## Task 6: Sprite Generation

**Files:**
- Create: `snake_game/sprites.py`

No unit tests — visual output; verify by running the game in Task 8.

- [ ] **Step 1: Implement `snake_game/sprites.py`**

```python
# snake_game/sprites.py
"""
Generates all game sprites programmatically using pygame.draw.
Call build_sprites() after pygame.display.set_mode() is called.
"""
import pygame
from snake_game.config import CELL_SIZE, COLOR_WHITE, COLOR_BLACK

C = CELL_SIZE
HALF = C // 2


def _surf(w=C, h=C, alpha=True) -> pygame.Surface:
    fmt = pygame.SRCALPHA if alpha else 0
    s = pygame.Surface((w, h), fmt)
    s.fill((0, 0, 0, 0) if alpha else (0, 0, 0))
    return s


def _head(color=(80, 100, 200), eye_color=(255,255,255), facing='right') -> pygame.Surface:
    s = _surf()
    pygame.draw.ellipse(s, color, (2, 2, C-4, C-4))
    # eyes
    ex, ey = {
        'right': (C-7, 5),
        'left':  (4,   5),
        'up':    (5,   4),
        'down':  (5,   C-8),
    }[facing]
    ex2 = ex + (4 if facing in ('right','left') else 0)
    ey2 = ey + (4 if facing in ('up','down') else 0)
    pygame.draw.circle(s, eye_color, (ex, ey), 2)
    pygame.draw.circle(s, eye_color, (ex2, ey2), 2)
    return s


def _head_open(color=(80, 100, 200), facing='right') -> pygame.Surface:
    s = _head(color=color, facing=facing)
    # open mouth
    mx, my = {
        'right': (C-5, HALF-2),
        'left':  (2,   HALF-2),
        'up':    (HALF-2, 2),
        'down':  (HALF-2, C-5),
    }[facing]
    pygame.draw.ellipse(s, (255, 60, 60), (mx, my, 5, 4))
    return s


def _body(color=(80, 100, 200), orb_color=(220,220,255)) -> pygame.Surface:
    s = _surf()
    pygame.draw.ellipse(s, color, (2, 2, C-4, C-4))
    pygame.draw.circle(s, orb_color, (HALF, HALF), 4)
    return s


def _tail(color=(80, 100, 200)) -> pygame.Surface:
    s = _surf()
    pts = [(2, HALF), (C-4, 4), (C-4, C-4)]
    pygame.draw.polygon(s, color, pts)
    return s


def _pokeball(inner=(220,50,50), label=None) -> pygame.Surface:
    s = _surf()
    pygame.draw.circle(s, (220,220,220), (HALF, HALF), HALF-2)
    pygame.draw.rect(s, inner, (2, 2, C-4, HALF-2), border_radius=8)
    pygame.draw.line(s, (30,30,30), (2, HALF), (C-2, HALF), 2)
    pygame.draw.circle(s, (80,80,80), (HALF, HALF), 4)
    pygame.draw.circle(s, (200,200,200), (HALF, HALF), 3)
    return s


def _badge(color=(200,200,50)) -> pygame.Surface:
    s = _surf(w=16, h=16)
    pygame.draw.polygon(s, color, [(8,1),(15,6),(12,15),(4,15),(1,6)])
    return s


def _heart() -> pygame.Surface:
    s = _surf(w=14, h=14)
    pygame.draw.circle(s, (220,50,50), (4,5), 4)
    pygame.draw.circle(s, (220,50,50), (10,5), 4)
    pygame.draw.polygon(s, (220,50,50), [(0,6),(7,14),(14,6)])
    return s


def build_sprites() -> dict:
    """Returns dict of all game sprites as pygame.Surface objects."""
    SNAKE_COLOR = (80, 100, 200)
    sprites = {}

    # Snake head — 4 directions, normal + mouth open
    for facing in ('right', 'left', 'up', 'down'):
        sprites[f'head_{facing}'] = _head(color=SNAKE_COLOR, facing=facing)
        sprites[f'head_{facing}_open'] = _head_open(color=SNAKE_COLOR, facing=facing)

    sprites['body'] = _body(color=SNAKE_COLOR)
    sprites['tail'] = _tail(color=SNAKE_COLOR)

    # Balls
    sprites['ball_normal'] = _pokeball(inner=(220,50,50))          # red top = Poké Ball
    sprites['ball_super']  = _pokeball(inner=(50,80,220))          # blue top = Great Ball
    sprites['ball_master'] = _pokeball(inner=(160,0,200))          # purple top = Master Ball

    # Badges (8 colors)
    badge_colors = [
        (180,160,120),  # ニビ - stone
        (80,160,220),   # ハナダ - water
        (240,220,40),   # クチバ - electric
        (80,200,80),    # タマムシ - grass
        (180,80,200),   # セキチク - poison
        (220,120,200),  # ヤマブキ - psychic
        (240,120,40),   # グレン - fire
        (120,60,220),   # トキワ - dragon
    ]
    for i, c in enumerate(badge_colors):
        sprites[f'badge_{i}'] = _badge(color=c)

    sprites['heart'] = _heart()

    return sprites
```

- [ ] **Step 2: Commit**

```bash
git add snake_game/sprites.py
git commit -m "feat: programmatic pixel art sprite generation"
```

---

## Task 7: Renderer

**Files:**
- Create: `snake_game/renderer.py`

- [ ] **Step 1: Implement `snake_game/renderer.py`**

```python
# snake_game/renderer.py
import pygame
import math
from snake_game.config import (
    CELL_SIZE, GRID_W, GRID_H, GAME_W, GAME_H, HUD_H, WINDOW_W, WINDOW_H,
    COLOR_BG, COLOR_GRID, COLOR_WALL_FIXED, COLOR_HUD_BG, COLOR_WHITE, COLOR_BLACK,
)


class Renderer:
    def __init__(self, screen: pygame.Surface, sprites: dict, font_small, font_large):
        self.screen = screen
        self.sprites = sprites
        self.font_s = font_small
        self.font_l = font_large
        self._flash_on = True
        self._flash_timer = 0.0
        self._border_flash = False

    def _cell_rect(self, x, y) -> pygame.Rect:
        return pygame.Rect(x * CELL_SIZE, HUD_H + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

    # ---- Background & grid ----
    def draw_bg(self, bg_accent):
        self.screen.fill(bg_accent)
        for x in range(GRID_W):
            for y in range(GRID_H):
                pygame.draw.rect(self.screen, COLOR_GRID,
                                 self._cell_rect(x, y), 1)

    # ---- Walls ----
    def draw_walls(self, fixed_walls, dynamic_walls, now: float, flash_frame: bool):
        for (wx, wy) in fixed_walls:
            pygame.draw.rect(self.screen, COLOR_WALL_FIXED,
                             self._cell_rect(wx, wy))
        for dw in dynamic_walls:
            alpha = dw.alpha(now)
            flashing = dw.is_flashing(now)
            color = dw.color if hasattr(dw, 'color') else (160, 160, 160)
            if flashing and flash_frame:
                color = COLOR_WHITE
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            surf.fill((*color, alpha))
            self.screen.blit(surf, self._cell_rect(dw.x, dw.y))

    def draw_walls_ex(self, fixed_walls, dynamic_walls, wall_color, now: float, flash_frame: bool):
        """draw_walls with per-level dynamic wall color."""
        for (wx, wy) in fixed_walls:
            pygame.draw.rect(self.screen, COLOR_WALL_FIXED,
                             self._cell_rect(wx, wy))
        for dw in dynamic_walls:
            alpha = dw.alpha(now)
            color = wall_color
            if dw.is_flashing(now) and flash_frame:
                color = COLOR_WHITE
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            surf.fill((*color, alpha))
            self.screen.blit(surf, self._cell_rect(dw.x, dw.y))

    # ---- Snake ----
    def draw_snake(self, snake, eating: bool):
        dx, dy = snake.direction
        facing_map = {(1,0):'right',(-1,0):'left',(0,-1):'up',(0,1):'down'}
        facing = facing_map.get((dx, dy), 'right')
        key = f'head_{facing}_open' if eating else f'head_{facing}'
        for i, (bx, by) in enumerate(snake.body):
            if i == 0:
                self.screen.blit(self.sprites[key], self._cell_rect(bx, by))
            elif i == len(snake.body) - 1:
                self.screen.blit(self.sprites['tail'], self._cell_rect(bx, by))
            else:
                self.screen.blit(self.sprites['body'], self._cell_rect(bx, by))

    # ---- Balls ----
    def draw_balls(self, balls: list):
        for b in balls:
            bx, by = b['pos']
            key = {'normal': 'ball_normal', 'super': 'ball_super',
                   'master': 'ball_master'}.get(b['type'], 'ball_normal')
            self.screen.blit(self.sprites[key], self._cell_rect(bx, by))

    # ---- Master Ball border flash ----
    def draw_master_border(self, active: bool, flash_frame: bool):
        if active and flash_frame:
            pygame.draw.rect(self.screen, (200, 0, 255),
                             pygame.Rect(0, HUD_H, GAME_W, GAME_H), 3)

    # ---- HUD ----
    def draw_hud(self, score: int, lives: int, badges: list,
                 master_remaining: float, gym_name: str):
        pygame.draw.rect(self.screen, COLOR_HUD_BG,
                         pygame.Rect(0, 0, WINDOW_W, HUD_H))
        # Score
        txt = self.font_s.render(f'SCORE {score:04d}', True, COLOR_WHITE)
        self.screen.blit(txt, (8, 8))
        # Gym name
        gym_txt = self.font_s.render(gym_name, True, COLOR_WHITE)
        self.screen.blit(gym_txt, (8, 30))
        # Lives (hearts)
        for i in range(lives):
            self.screen.blit(self.sprites['heart'], (180 + i * 18, 8))
        # Badges
        for i, earned in enumerate(badges):
            if earned:
                self.screen.blit(self.sprites[f'badge_{i}'], (180 + i * 18, 30))
        # Master Ball countdown
        if master_remaining > 0:
            m_txt = self.font_s.render(f'★ {master_remaining:.1f}s', True, (200, 0, 255))
            self.screen.blit(m_txt, (400, 8))

    # ---- Menus ----
    def draw_main_menu(self, has_save: bool, selected: int):
        self.screen.fill(COLOR_BLACK)
        title = self.font_l.render('ポケモン へびゲーム', True, COLOR_WHITE)
        self.screen.blit(title, title.get_rect(center=(WINDOW_W//2, 160)))
        options = ['つづきから', 'はじめから'] if has_save else ['はじめから']
        for i, opt in enumerate(options):
            color = (255, 220, 0) if i == selected else COLOR_WHITE
            txt = self.font_s.render(opt, True, color)
            self.screen.blit(txt, txt.get_rect(center=(WINDOW_W//2, 260 + i * 40)))

    def draw_difficulty_select(self, selected: int):
        self.screen.fill(COLOR_BLACK)
        title = self.font_l.render('むずかしさ', True, COLOR_WHITE)
        self.screen.blit(title, title.get_rect(center=(WINDOW_W//2, 150)))
        opts = [('かんたん', 'easy'), ('ふつう', 'normal'), ('むずかしい', 'hard')]
        for i, (label, _) in enumerate(opts):
            color = (255, 220, 0) if i == selected else COLOR_WHITE
            txt = self.font_s.render(label, True, color)
            self.screen.blit(txt, txt.get_rect(center=(WINDOW_W//2, 240 + i * 44)))

    def draw_pause_menu(self, selected: int):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        title = self.font_l.render('ポーズ', True, COLOR_WHITE)
        self.screen.blit(title, title.get_rect(center=(WINDOW_W//2, 160)))
        opts = ['つづける', 'タイトルへ']
        for i, opt in enumerate(opts):
            color = (255, 220, 0) if i == selected else COLOR_WHITE
            txt = self.font_s.render(opt, True, color)
            self.screen.blit(txt, txt.get_rect(center=(WINDOW_W//2, 240 + i * 44)))

    def draw_game_over(self, lives: int):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        msg = 'ゲームオーバー'
        txt = self.font_l.render(msg, True, (220, 50, 50))
        self.screen.blit(txt, txt.get_rect(center=(WINDOW_W//2, 200)))
        if lives > 0:
            sub = self.font_s.render('なんでもおして つづける', True, COLOR_WHITE)
        else:
            sub = self.font_s.render('なんでもおして タイトルへ', True, COLOR_WHITE)
        self.screen.blit(sub, sub.get_rect(center=(WINDOW_W//2, 270)))

    def draw_gym_clear(self, gym_name: str):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        txt = self.font_l.render(f'{gym_name} クリア！', True, (255, 220, 0))
        self.screen.blit(txt, txt.get_rect(center=(WINDOW_W//2, 220)))

    def draw_confirm_new_game(self, selected: int):
        self.screen.fill(COLOR_BLACK)
        q = self.font_s.render('ほんとうによいですか？', True, COLOR_WHITE)
        self.screen.blit(q, q.get_rect(center=(WINDOW_W//2, 200)))
        for i, opt in enumerate(['はい', 'いいえ']):
            color = (255, 220, 0) if i == selected else COLOR_WHITE
            txt = self.font_s.render(opt, True, color)
            self.screen.blit(txt, txt.get_rect(center=(WINDOW_W//2, 270 + i * 44)))

    # ---- Ending animation ----
    def draw_ending(self, phase: str, progress: float,
                    hakuryu_sprite, dragonite_sprite,
                    total_score: int, total_time: float, best_scores: list, badges: list):
        """
        phase: 'congratulations' | 'hakuryu' | 'flash' | 'dragonite' | 'stats'
        progress: 0.0..1.0 within phase
        """
        self.screen.fill(COLOR_BLACK)
        if phase == 'congratulations':
            alpha = min(255, int(255 * progress * 3))
            txt = self.font_l.render('Congratulations!', True, COLOR_WHITE)
            txt.set_alpha(alpha)
            self.screen.blit(txt, txt.get_rect(center=(WINDOW_W//2, WINDOW_H//2)))
        elif phase == 'hakuryu':
            self.screen.blit(hakuryu_sprite,
                             hakuryu_sprite.get_rect(center=(WINDOW_W//2, WINDOW_H//2 - 20)))
            # particle dots
            for i in range(12):
                angle = (i / 12) * 2 * math.pi + progress * 4
                r = 40 + 20 * math.sin(progress * math.pi * 2)
                px = int(WINDOW_W//2 + r * math.cos(angle))
                py = int(WINDOW_H//2 - 20 + r * math.sin(angle))
                pygame.draw.circle(self.screen, COLOR_WHITE, (px, py), 3)
        elif phase == 'flash':
            alpha = int(255 * progress)
            flash = pygame.Surface((WINDOW_W, WINDOW_H))
            flash.fill(COLOR_WHITE)
            flash.set_alpha(alpha)
            self.screen.blit(flash, (0, 0))
        elif phase == 'dragonite':
            alpha = int(255 * progress)
            dragonite_sprite.set_alpha(alpha)
            self.screen.blit(dragonite_sprite,
                             dragonite_sprite.get_rect(center=(WINDOW_W//2, WINDOW_H//2 - 20)))
        elif phase == 'stats':
            title = self.font_l.render('Congratulations!', True, (255, 220, 0))
            self.screen.blit(title, title.get_rect(center=(WINDOW_W//2, 60)))
            score_txt = self.font_s.render(f'トータルスコア: {total_score}', True, COLOR_WHITE)
            self.screen.blit(score_txt, (60, 120))
            mins = int(total_time) // 60
            secs = int(total_time) % 60
            time_txt = self.font_s.render(f'クリアタイム: {mins:02d}:{secs:02d}', True, COLOR_WHITE)
            self.screen.blit(time_txt, (60, 150))
            for i, s in enumerate(best_scores):
                gym_score_txt = self.font_s.render(f'Gym{i+1}: {s}pt', True, COLOR_WHITE)
                self.screen.blit(gym_score_txt, (60 + (i % 4) * 110, 190 + (i // 4) * 28))
            for i, earned in enumerate(badges):
                if earned:
                    self.screen.blit(self.sprites[f'badge_{i}'], (60 + i * 40, 270))
            any_key = self.font_s.render('なんでもおして タイトルへ', True, (180, 180, 180))
            self.screen.blit(any_key, any_key.get_rect(center=(WINDOW_W//2, 370)))
```

- [ ] **Step 2: Commit**

```bash
git add snake_game/renderer.py
git commit -m "feat: renderer with all draw methods"
```

---

## Task 8: Game State Machine

**Files:**
- Create: `snake_game/game.py`

- [ ] **Step 1: Implement `snake_game/game.py`**

```python
# snake_game/game.py
import pygame
import time
import random
from enum import Enum, auto
from snake_game.snake import Snake
from snake_game.level import Level, GYMS
from snake_game.ball import BallManager
from snake_game import save as save_module
from snake_game.config import (
    GRID_W, GRID_H, HUD_H, CELL_SIZE,
    BASE_SPEED, SPEED_CAP, SPEED_PER_10PTS,
    STARTING_LIVES, GYM_CLEAR_DURATION,
    ENDING_CONGRATULATIONS_DURATION,
    SOUND_ENABLED, SAVE_PATH,
)


class State(Enum):
    MAIN_MENU = auto()
    CONFIRM_NEW = auto()
    DIFFICULTY_SELECT = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    GYM_CLEAR = auto()
    GAME_COMPLETE = auto()


_START_POS = (GRID_W // 2, GRID_H // 2)
_START_DIR = (1, 0)


class Game:
    def __init__(self, renderer, sprites, sounds: dict = None):
        self.renderer = renderer
        self.sprites = sprites
        self.sounds = sounds or {}
        self.state = State.MAIN_MENU

        # Persistent session data
        self.save_data: dict = None
        self.difficulty: str = 'normal'

        # Menu cursors
        self.menu_cursor = 0
        self.diff_cursor = 1  # default ふつう

        # Runtime game state
        self.snake: Snake = None
        self.level: Level = None
        self.balls: BallManager = None
        self.gym_index: int = 0
        self.lives: int = STARTING_LIVES
        self.per_gym_score: int = 0
        self.total_score: int = 0
        self.best_scores: list = [0] * 8
        self.badges: list = [False] * 8
        self.total_clear_time: float = 0.0
        self.current_speed: float = BASE_SPEED['normal']

        # Timing
        self._step_timer: float = 0.0
        self._gym_clear_timer: float = 0.0
        self._gym_attempt_start: float = 0.0
        self._pause_start: float = 0.0   # monotonic time when PAUSED entered
        self._pause_total: float = 0.0   # cumulative pause seconds for this attempt
        self._now: float = 0.0

        # Flash state
        self._flash_frame: bool = False
        self._flash_accum: float = 0.0

        # Eating animation
        self._eating: bool = False

        # Ending animation
        self._ending_phase: str = 'congratulations'
        self._ending_phase_start: float = 0.0
        self._ending_phase_durations = {
            'congratulations': 3.0,
            'hakuryu': 2.5,
            'flash': 1.0,
            'dragonite': 2.5,
            'stats': float('inf'),
        }

    # ------------------------------------------------------------------ #
    #  Input                                                               #
    # ------------------------------------------------------------------ #
    def handle_event(self, event: pygame.event.Event):
        if event.type != pygame.KEYDOWN:
            return
        key = event.key

        if self.state == State.MAIN_MENU:
            self._menu_nav(key, ['つづきから', 'はじめから'] if self.save_data else ['はじめから'])
            if key == pygame.K_RETURN or key == pygame.K_z:
                self._main_menu_confirm()

        elif self.state == State.CONFIRM_NEW:
            self._menu_nav(key, ['はい', 'いいえ'])
            if key == pygame.K_RETURN or key == pygame.K_z:
                if self.menu_cursor == 0:  # はい
                    save_module.delete(SAVE_PATH)
                    self.save_data = None
                    self.state = State.DIFFICULTY_SELECT
                    self.menu_cursor = 1
                else:
                    self.state = State.MAIN_MENU
                    self.menu_cursor = 0

        elif self.state == State.DIFFICULTY_SELECT:
            self._menu_nav(key, ['', '', ''])
            if key == pygame.K_RETURN or key == pygame.K_z:
                self.difficulty = ['easy', 'normal', 'hard'][self.diff_cursor]
                self._start_new_run()

        elif self.state == State.PLAYING:
            dir_map = {
                pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1),
                pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0),
            }
            if key in dir_map:
                self.snake.set_direction(dir_map[key])
            elif key == pygame.K_SPACE:
                self.state = State.PAUSED
                self._pause_start = time.monotonic()
                self.menu_cursor = 0

        elif self.state == State.PAUSED:
            self._menu_nav(key, ['つづける', 'タイトルへ'])
            if key == pygame.K_RETURN or key == pygame.K_z or key == pygame.K_SPACE:
                if self.menu_cursor == 0 or key == pygame.K_SPACE:
                    self._pause_total += time.monotonic() - self._pause_start
                    self.state = State.PLAYING
                else:
                    self._save_and_go_menu()

        elif self.state == State.GAME_OVER:
            self.state = State.MAIN_MENU if self.lives <= 0 else State.PLAYING
            if self.lives <= 0:
                save_module.delete(SAVE_PATH)
                self.save_data = None
            else:
                self._restart_gym()

        elif self.state == State.GAME_COMPLETE:
            # stats phase: any key → menu
            self.state = State.MAIN_MENU
            self.menu_cursor = 0
            self.save_data = save_module.load(SAVE_PATH)

    def _menu_nav(self, key, options: list):
        n = len(options)
        if key in (pygame.K_UP, pygame.K_DOWN):
            delta = -1 if key == pygame.K_UP else 1
            if self.state == State.DIFFICULTY_SELECT:
                self.diff_cursor = (self.diff_cursor + delta) % 3
            else:
                self.menu_cursor = (self.menu_cursor + delta) % n

    def _main_menu_confirm(self):
        has_save = self.save_data is not None
        options = ['つづきから', 'はじめから'] if has_save else ['はじめから']
        chosen = options[self.menu_cursor]
        if chosen == 'つづきから':
            self._load_and_continue()
        else:
            if has_save:
                self.state = State.CONFIRM_NEW
                self.menu_cursor = 0
            else:
                self.state = State.DIFFICULTY_SELECT
                self.menu_cursor = 1

    # ------------------------------------------------------------------ #
    #  Update                                                              #
    # ------------------------------------------------------------------ #
    def update(self, dt: float, now: float):
        self._now = now
        self._flash_accum += dt
        if self._flash_accum >= 0.5:
            self._flash_accum = 0.0
            self._flash_frame = not self._flash_frame

        if self.state == State.MAIN_MENU:
            self.save_data = save_module.load(SAVE_PATH)

        elif self.state == State.PLAYING:
            self._update_playing(dt, now)

        elif self.state == State.GYM_CLEAR:
            self._gym_clear_timer -= dt
            if self._gym_clear_timer <= 0:
                self._advance_gym()

        elif self.state == State.GAME_COMPLETE:
            self._update_ending(dt, now)

    def _update_playing(self, dt: float, now: float):
        step_interval = 1.0 / self.current_speed
        self._step_timer += dt
        stepped = False
        if self._step_timer >= step_interval:
            self._step_timer -= step_interval
            self.snake.move()
            stepped = True

        if not stepped:
            return

        head = self.snake.head
        hx, hy = head

        # Wall & bounds collision
        all_walls = self.level.all_wall_cells()
        if (hx < 0 or hx >= GRID_W or hy < 0 or hy >= GRID_H
                or head in all_walls or self.snake.check_self_collision()):
            self._play_sound('death')
            self.lives -= 1
            self.state = State.GAME_OVER
            return

        # Ball collection
        occupied_for_balls = set(self.snake.cells)
        score = self.balls.try_eat(head, now, snake_cells=occupied_for_balls)
        if score > 0:
            self.snake.grow()
            self.per_gym_score += score
            self.total_score += score
            self._eating = True
            self._play_sound('eat')
            # Speed ramp
            new_speed = BASE_SPEED[self.difficulty] + (self.per_gym_score // 10) * SPEED_PER_10PTS
            self.current_speed = min(new_speed, SPEED_CAP[self.difficulty])
        else:
            self._eating = False

        # Ball updates
        head_adj = {(hx+dx, hy+dy) for dx,dy in ((1,0),(-1,0),(0,1),(0,-1))}
        self.balls.update(now, snake_cells=set(self.snake.cells), head_adjacent=head_adj)

        # Dynamic walls
        snake_set = set(self.snake.cells) | self.balls.all_ball_cells() | head_adj
        self.level.try_spawn_wall(now, occupied_cells=snake_set)
        self.level.remove_expired(now)

        # Gym clear check
        if self.per_gym_score >= self.level.target_score:
            self._on_gym_clear(now)

    def _on_gym_clear(self, now: float):
        # Exclude pause time from clear time (spec: only PLAYING state counts)
        elapsed = (now - self._gym_attempt_start) - self._pause_total
        self.total_clear_time += max(0.0, elapsed)
        self.best_scores[self.gym_index] = self.per_gym_score
        self.badges[self.gym_index] = True
        self.lives += 1
        self._play_sound('clear')
        self.state = State.GYM_CLEAR
        self._gym_clear_timer = GYM_CLEAR_DURATION
        # Save progress
        self._write_save()

    def _advance_gym(self):
        if self.gym_index >= 7:
            # All 8 gyms complete
            sd = save_module.load(SAVE_PATH) or {}
            sd['completed'] = True
            save_module.write(sd, SAVE_PATH)
            self._start_ending()
        else:
            self.gym_index += 1
            self._enter_gym(self._now)

    def _enter_gym(self, now: float):
        self.per_gym_score = 0
        self.current_speed = BASE_SPEED[self.difficulty]
        self._step_timer = 0.0
        self.snake = Snake(start=_START_POS, direction=_START_DIR, length=3)
        self.level = Level(gym_index=self.gym_index, difficulty=self.difficulty)
        self.level.start(now)
        all_walls = self.level.all_wall_cells()
        self.balls = BallManager(wall_cells=all_walls, grid_w=GRID_W, grid_h=GRID_H)
        self.balls.reset(now)
        self._gym_attempt_start = now
        self._pause_total = 0.0
        self.state = State.PLAYING

    def _restart_gym(self):
        now = time.monotonic()
        self.per_gym_score = 0
        self.current_speed = BASE_SPEED[self.difficulty]
        self._step_timer = 0.0
        self.snake = Snake(start=_START_POS, direction=_START_DIR, length=3)
        self.level = Level(gym_index=self.gym_index, difficulty=self.difficulty)
        self.level.start(now)
        all_walls = self.level.all_wall_cells()
        self.balls = BallManager(wall_cells=all_walls, grid_w=GRID_W, grid_h=GRID_H)
        self.balls.reset(now)
        self._gym_attempt_start = now
        self._pause_total = 0.0
        self.state = State.PLAYING

    # ------------------------------------------------------------------ #
    #  Run init                                                            #
    # ------------------------------------------------------------------ #
    def _start_new_run(self):
        self.gym_index = 0
        self.lives = STARTING_LIVES
        self.total_score = 0
        self.best_scores = [0] * 8
        self.badges = [False] * 8
        self.total_clear_time = 0.0
        self._enter_gym(time.monotonic())

    def _load_and_continue(self):
        sd = self.save_data
        self.difficulty = sd.get('difficulty', 'normal')
        self.gym_index = sd.get('current_gym', 0)
        self.lives = sd.get('lives', STARTING_LIVES)
        self.total_score = sd.get('total_score', 0)
        self.best_scores = sd.get('best_scores', [0]*8)
        self.badges = sd.get('badges', [False]*8)
        self.total_clear_time = sd.get('total_clear_time', 0.0)
        self._enter_gym(time.monotonic())

    def _save_and_go_menu(self):
        self._write_save()
        self.state = State.MAIN_MENU
        self.menu_cursor = 0

    def _write_save(self):
        data = {
            'current_gym': self.gym_index,
            'lives': self.lives,
            'badges': self.badges,
            'total_score': self.total_score,
            'best_scores': self.best_scores,
            'total_clear_time': self.total_clear_time,
            'difficulty': self.difficulty,
            'completed': all(self.badges),
        }
        save_module.write(data, SAVE_PATH)
        self.save_data = data

    # ------------------------------------------------------------------ #
    #  Ending                                                              #
    # ------------------------------------------------------------------ #
    def _start_ending(self):
        self.state = State.GAME_COMPLETE
        self._ending_phase = 'congratulations'
        self._ending_phase_start = self._now

    def _update_ending(self, dt: float, now: float):
        phase_dur = self._ending_phase_durations.get(self._ending_phase, 3.0)
        if self._ending_phase == 'stats':
            return  # wait for key press
        elapsed = now - self._ending_phase_start
        if elapsed >= phase_dur:
            phases = ['congratulations', 'hakuryu', 'flash', 'dragonite', 'stats']
            idx = phases.index(self._ending_phase)
            if idx + 1 < len(phases):
                self._ending_phase = phases[idx + 1]
                self._ending_phase_start = now

    @property
    def ending_progress(self) -> float:
        phase_dur = self._ending_phase_durations.get(self._ending_phase, 3.0)
        if phase_dur == float('inf'):
            return 1.0
        elapsed = self._now - self._ending_phase_start
        return min(1.0, elapsed / phase_dur)

    # ------------------------------------------------------------------ #
    #  Draw                                                                #
    # ------------------------------------------------------------------ #
    def draw(self):
        r = self.renderer
        now = self._now

        if self.state == State.MAIN_MENU:
            r.draw_main_menu(has_save=self.save_data is not None,
                             selected=self.menu_cursor)

        elif self.state == State.CONFIRM_NEW:
            r.draw_confirm_new_game(selected=self.menu_cursor)

        elif self.state == State.DIFFICULTY_SELECT:
            r.draw_difficulty_select(selected=self.diff_cursor)

        elif self.state in (State.PLAYING, State.PAUSED, State.GAME_OVER, State.GYM_CLEAR):
            gym = GYMS[self.gym_index]
            r.draw_bg(self.level.bg_accent)
            r.draw_walls_ex(self.level.fixed_walls, self.level.dynamic_walls,
                            self.level.wall_color, now, self._flash_frame)
            r.draw_balls(self.balls.get_all_balls())
            r.draw_snake(self.snake, eating=self._eating)
            r.draw_master_border(self.balls.master_ball_active(), self._flash_frame)
            r.draw_hud(score=self.per_gym_score, lives=self.lives,
                       badges=self.badges,
                       master_remaining=self.balls.master_ball_remaining(now),
                       gym_name=gym.name)
            if self.state == State.PAUSED:
                r.draw_pause_menu(selected=self.menu_cursor)
            elif self.state == State.GAME_OVER:
                r.draw_game_over(lives=self.lives)
            elif self.state == State.GYM_CLEAR:
                r.draw_gym_clear(gym_name=gym.name)

        elif self.state == State.GAME_COMPLETE:
            hakuryu = self._make_hakuryu_big()
            dragonite = self._make_dragonite_big()
            r.draw_ending(
                phase=self._ending_phase,
                progress=self.ending_progress,
                hakuryu_sprite=hakuryu,
                dragonite_sprite=dragonite,
                total_score=self.total_score,
                total_time=self.total_clear_time,
                best_scores=self.best_scores,
                badges=self.badges,
            )

    def _make_hakuryu_big(self) -> pygame.Surface:
        """Scale up head sprite for ending."""
        s = self.sprites.get('head_right', pygame.Surface((20, 20)))
        return pygame.transform.scale(s, (120, 120))

    def _make_dragonite_big(self) -> pygame.Surface:
        """Simple Dragonite placeholder: orange circle with wings."""
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(s, (240, 160, 40), (60, 70), 40)    # body
        pygame.draw.ellipse(s, (240, 200, 80), (5, 20, 45, 25)) # left wing
        pygame.draw.ellipse(s, (240, 200, 80), (70, 20, 45, 25)) # right wing
        pygame.draw.circle(s, (255,255,200), (52, 62), 6)        # eye L
        pygame.draw.circle(s, (255,255,200), (68, 62), 6)        # eye R
        return s

    # ------------------------------------------------------------------ #
    #  Sound                                                               #
    # ------------------------------------------------------------------ #
    def _play_sound(self, name: str):
        if not SOUND_ENABLED:
            return
        snd = self.sounds.get(name)
        if snd:
            snd.play()
```

- [ ] **Step 2: Commit**

```bash
git add snake_game/game.py
git commit -m "feat: game state machine with full playing logic"
```

---

## Task 9: Main Entry Point

**Files:**
- Create: `snake_game/main.py`
- Create: `snake_game/__init__.py`

- [ ] **Step 1: Create `snake_game/__init__.py`** (empty)

```bash
touch snake_game/__init__.py
```

- [ ] **Step 2: Implement `snake_game/main.py`**

```python
# snake_game/main.py
import sys
import time
import pygame
from snake_game.config import (
    WINDOW_W, WINDOW_H, FPS, SOUND_ENABLED,
    COLOR_BLACK,
)
from snake_game.sprites import build_sprites
from snake_game.renderer import Renderer
from snake_game.game import Game


def load_font(size: int) -> pygame.font.Font:
    """Try to load a pixel font; fall back to default."""
    import os
    font_path = os.path.join(os.path.dirname(__file__), '..', 'snake_game',
                              'assets', 'fonts', 'pixel.ttf')
    if os.path.exists(font_path):
        return pygame.font.Font(font_path, size)
    return pygame.font.SysFont('Arial', size)


def load_sounds() -> dict:
    if not SOUND_ENABLED:
        return {}
    sounds = {}
    import os
    sound_dir = os.path.join(os.path.dirname(__file__), '..', 'snake_game', 'assets', 'sounds')
    for name, filename in [('eat', 'eat.wav'), ('clear', 'clear.wav'), ('death', 'death.wav')]:
        path = os.path.join(sound_dir, filename)
        if os.path.exists(path):
            try:
                sounds[name] = pygame.mixer.Sound(path)
            except Exception:
                pass
    return sounds


def main():
    pygame.init()
    if SOUND_ENABLED:
        pygame.mixer.init()

    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption('ポケモン へびゲーム')

    sprites = build_sprites()
    font_s = load_font(16)
    font_l = load_font(24)
    sounds = load_sounds()

    renderer = Renderer(screen, sprites, font_s, font_l)
    game = Game(renderer, sprites, sounds)

    clock = pygame.time.Clock()
    prev_time = time.monotonic()

    while True:
        now = time.monotonic()
        dt = now - prev_time
        prev_time = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)

        game.update(dt, now)
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
```

- [ ] **Step 3: Run the game**

```bash
cd "C:/Users/mcc/Desktop/AI研修2026"
python -m snake_game.main
```

Expected: Game window opens at 500×460px showing main menu in Japanese. Arrow keys navigate, Enter/Z selects. Game is fully playable through all 8 gyms.

- [ ] **Step 4: Run all tests once more to confirm nothing broken**

```bash
pytest tests/ -v
```

Expected: all PASSED.

- [ ] **Step 5: Commit**

```bash
git add snake_game/__init__.py snake_game/main.py
git commit -m "feat: main entry point, game is playable end-to-end"
```

---

## Task 10: Fix config.py SAVE_PATH

The `SAVE_PATH` in config.py uses a relative path built at import time which may be fragile. Fix it to be relative to the project root.

- [ ] **Step 1: Update SAVE_PATH in config.py**

Replace the SAVE_PATH line at the bottom of `snake_game/config.py`:

```python
# Replace:
import os
SAVE_PATH = os.path.join(os.path.dirname(__file__), '..', 'snake_game', 'save', 'save.json')

# With:
import os
SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'save', 'save.json')
```

- [ ] **Step 2: Re-run all tests**

```bash
pytest tests/ -v
```

Expected: all PASSED.

- [ ] **Step 3: Run game and test save**

```bash
python -m snake_game.main
```

Verify: save file created at `snake_game/save/save.json` after clearing gym 1.

- [ ] **Step 4: Commit**

```bash
git add snake_game/config.py
git commit -m "fix: resolve SAVE_PATH to absolute path relative to module"
```

---

## Balancing & Playtesting Notes

After the game runs end-to-end, tune these values in `config.py` based on play feel:

- `GYM_TARGETS` — adjust if gyms clear too fast or too slow
- `GYM_WALL_PARAMS` — adjust lifespan/cap/interval per gym
- `BASE_SPEED` / `SPEED_CAP` — adjust if game feels too fast or slow
- `MASTER_BALL_SPAWN_CHANCE` — increase if Master Ball rarely appears
- `SUPER_BALL_INTERVAL_MIN/MAX` — adjust Great Ball frequency

All these are in one place in `config.py` — no hunting through code.

---

## Asset Upgrade Path (Optional)

To replace programmatic sprites with actual pixel art PNG files:

1. Add PNG files to `snake_game/assets/sprites/snake/`, `balls/`, etc.
2. In `sprites.py`, replace `_head()`, `_body()`, etc. with `pygame.image.load()` calls
3. No other files need to change — renderer and game.py use the same sprite dict keys
