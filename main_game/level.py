# snake_game/level.py
import random
from dataclasses import dataclass
from typing import Optional
from snake_game.config import (
    GYM_TARGETS, GYM_WALL_PARAMS, GYM_WALL_COLORS, GYM_BG_ACCENTS,
    WALL_INTERVAL_MULT, GRID_W, GRID_H,
    DYNAMIC_WALL_LEN_MIN, DYNAMIC_WALL_LEN_MAX,
)


@dataclass
class GymDef:
    name: str
    leader: str
    type_name: str
    wall_color: tuple
    bg_accent: tuple
    target_score: int
    wall_params: tuple  # (lifespan, cap, interval_normal)
    fixed_walls: list


@dataclass
class DynamicWall:
    cells: list  # list of (x, y) tuples forming the strip
    lifespan: float
    spawn_time: float

    def is_expired(self, current_time: float) -> bool:
        return (current_time - self.spawn_time) >= self.lifespan

    def remaining(self, current_time: float) -> float:
        return max(0.0, self.lifespan - (current_time - self.spawn_time))

    def alpha(self, current_time: float) -> int:
        rem = self.remaining(current_time)
        if rem >= 3.0:
            return 255
        return max(60, int(255 * (rem / 3.0)))

    def is_flashing(self, current_time: float) -> bool:
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


def _nibi_walls():
    return [
        (1,1),(2,1),(1,2),(23,1),(22,1),(23,2),
        (1,18),(2,18),(1,17),(23,18),(22,18),(23,17),
    ]

def _hanada_walls():
    walls = []
    for y in range(5, 16):
        walls += [(8, y), (16, y)]
    return walls

def _kuchiba_walls():
    return [
        (3,3),(4,3),(5,3),(5,4),(5,5),(6,5),(7,5),(7,6),(7,7),
        (17,12),(18,12),(19,12),(19,13),(19,14),(20,14),(21,14),(21,15),(21,16),
    ]

def _tamamushi_walls():
    clusters = [(5,4),(6,4),(5,5),(17,4),(18,4),(17,5),(5,15),(6,15),(5,16),(17,15),(18,15),(17,16)]
    center = [(11,8),(12,8),(13,8),(12,7),(11,12),(12,12),(13,12),(12,13)]
    return clusters + center

def _sekichiku_walls():
    walls = []
    for x in range(4, 22, 4):
        for y in range(4, 17, 4):
            walls += [(x, y), (x+1, y)]
    return walls

def _yamabuki_walls():
    walls = []
    for x in range(6, 11):
        walls += [(x,9),(x,11),(24-x,9),(24-x,11)]
    for y in range(6, 11):
        walls += [(12,y),(12,19-y)]
    return list(set(walls))

def _guren_walls():
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
    walls = []
    for x in range(4, 21):
        walls += [(x,4),(x,16)]
    for y in range(4, 17):
        walls += [(4,y),(20,y)]
    for x in range(7, 18):
        walls.append((x,7))
    for y in range(7, 14):
        walls.append((17,y))
    for x in range(7, 17):
        walls.append((x,13))
    for y in range(10, 14):
        walls.append((7,y))
    walls = list(set(walls))
    openings = [(12,4),(20,10),(12,7),(17,10),(10,13),(7,10)]
    return [w for w in walls if w not in openings]


GYMS = [
    _build_gym(0, 'ニビシティ',    'タケシ', 'いわ',     _nibi_walls()),
    _build_gym(1, 'ハナダシティ',  'カスミ', 'みず',     _hanada_walls()),
    _build_gym(2, 'クチバシティ',  'マチス', 'でんき',   _kuchiba_walls()),
    _build_gym(3, 'タマムシシティ','エリカ', 'くさ',     _tamamushi_walls()),
    _build_gym(4, 'セキチクシティ','キョウ', 'どく',     _sekichiku_walls()),
    _build_gym(5, 'ヤマブキシティ','ナツメ', 'エスパー', _yamabuki_walls()),
    _build_gym(6, 'グレンタウン',  'カツラ', 'ほのお',   _guren_walls()),
    _build_gym(7, 'トキワシティ',  'サカキ', 'ドラゴン', _tokiwa_walls()),
]


class Level:
    def __init__(self, gym_index: int, difficulty: str):
        self.gym_index = gym_index
        self.difficulty = difficulty
        gym = GYMS[gym_index]
        self.fixed_walls: set = set(map(tuple, gym.fixed_walls))
        self.target_score = gym.target_score
        self.wall_color = gym.wall_color
        self.bg_accent = gym.bg_accent
        lifespan, cap, interval_normal = gym.wall_params
        self.wall_lifespan = lifespan
        self.wall_cap = cap
        self.wall_interval = interval_normal * WALL_INTERVAL_MULT[difficulty]
        self.dynamic_walls: list = []
        self._next_spawn_time: float = 0.0

    def start(self, now: float):
        self._next_spawn_time = now + self.wall_interval
        self.dynamic_walls = []

    def all_wall_cells(self) -> set:
        cells = set(self.fixed_walls)
        for w in self.dynamic_walls:
            cells.update(w.cells)
        return cells

    def try_spawn_wall(self, current_time: float, occupied_cells: set):
        if current_time < self._next_spawn_time:
            return
        self._next_spawn_time = current_time + self.wall_interval

        self.dynamic_walls = [w for w in self.dynamic_walls
                               if not w.is_expired(current_time)]

        if len(self.dynamic_walls) >= self.wall_cap:
            self.dynamic_walls.pop(0)

        all_occupied = occupied_cells | self.all_wall_cells()
        candidates = [
            (x, y)
            for x in range(1, GRID_W - 1)
            for y in range(1, GRID_H - 1)
            if (x, y) not in all_occupied
        ]
        if not candidates:
            return

        if self.difficulty == 'hard':
            cells = self._pick_strip(all_occupied, candidates)
        else:
            cells = [random.choice(candidates)]

        self.dynamic_walls.append(DynamicWall(cells=cells,
                                               lifespan=self.wall_lifespan,
                                               spawn_time=current_time))

    def _pick_strip(self, all_occupied: set, candidates: list) -> list:
        random.shuffle(candidates)
        length = random.randint(DYNAMIC_WALL_LEN_MIN, DYNAMIC_WALL_LEN_MAX)
        dx, dy = random.choice([(1, 0), (0, 1)])
        for ax, ay in candidates:
            strip = [(ax + dx * i, ay + dy * i) for i in range(length)]
            if all(
                1 <= cx < GRID_W - 1 and 1 <= cy < GRID_H - 1 and (cx, cy) not in all_occupied
                for cx, cy in strip
            ):
                return strip
        # fallback to single cell if no valid strip found
        return [candidates[0]]

    def remove_expired(self, current_time: float):
        self.dynamic_walls = [w for w in self.dynamic_walls
                               if not w.is_expired(current_time)]
