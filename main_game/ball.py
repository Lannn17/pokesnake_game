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
    def __init__(self, wall_cells: set, grid_w: int = GRID_W, grid_h: int = GRID_H):
        self._walls = wall_cells
        self._gw = grid_w
        self._gh = grid_h
        self._balls: list = []
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
        # Revert expired super balls to normal (same cell)
        for b in self._balls:
            if b['type'] == 'super' and b['expire_time'] and now >= b['expire_time']:
                b['type'] = 'normal'
                b['expire_time'] = None
                self._super_next = now + random.uniform(SUPER_BALL_INTERVAL_MIN,
                                                         SUPER_BALL_INTERVAL_MAX)

        # Ensure at least 1 normal ball
        if not any(b['type'] == 'normal' for b in self._balls):
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
        for b in self._balls:
            if b['pos'] == pos:
                score = BALL_SCORES[b['type']]
                was_super = b['type'] == 'super'
                self._balls.remove(b)
                self._spawn_normal(now, snake_cells)
                if was_super:
                    self._super_next = now + random.uniform(SUPER_BALL_INTERVAL_MIN,
                                                             SUPER_BALL_INTERVAL_MAX)
                return score
        if self._master_ball and self._master_ball['pos'] == pos:
            score = BALL_SCORES['master']
            self._master_ball = None
            self._master_next = now + random.uniform(MASTER_BALL_TIMER_MIN, MASTER_BALL_TIMER_MAX)
            return score
        return 0

    def get_all_balls(self) -> list:
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
