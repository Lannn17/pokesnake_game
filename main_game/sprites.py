# snake_game/sprites.py
import pygame
from snake_game.config import CELL_SIZE, COLOR_WHITE

C = CELL_SIZE
HALF = C // 2


def _surf(w=C, h=C, alpha=True) -> pygame.Surface:
    fmt = pygame.SRCALPHA if alpha else 0
    s = pygame.Surface((w, h), fmt)
    s.fill((0, 0, 0, 0) if alpha else (0, 0, 0))
    return s


def _head(color=(80, 100, 200), facing='right') -> pygame.Surface:
    s = _surf()
    pygame.draw.ellipse(s, color, (2, 2, C-4, C-4))
    ex, ey = {'right': (C-7,5), 'left': (4,5), 'up': (5,4), 'down': (5,C-8)}[facing]
    ex2 = ex + (4 if facing in ('right','left') else 0)
    ey2 = ey + (4 if facing in ('up','down') else 0)
    pygame.draw.circle(s, COLOR_WHITE, (ex, ey), 2)
    pygame.draw.circle(s, COLOR_WHITE, (ex2, ey2), 2)
    return s


def _head_open(color=(80, 100, 200), facing='right') -> pygame.Surface:
    s = _head(color=color, facing=facing)
    mx, my = {'right': (C-5,HALF-2), 'left': (2,HALF-2),
               'up': (HALF-2,2), 'down': (HALF-2,C-5)}[facing]
    pygame.draw.ellipse(s, (255, 60, 60), (mx, my, 5, 4))
    return s


def _body(color=(80, 100, 200)) -> pygame.Surface:
    s = _surf()
    pygame.draw.ellipse(s, color, (2, 2, C-4, C-4))
    pygame.draw.circle(s, (220, 220, 255), (HALF, HALF), 4)
    return s


def _tail(color=(80, 100, 200)) -> pygame.Surface:
    s = _surf()
    pygame.draw.polygon(s, color, [(2, HALF), (C-4, 4), (C-4, C-4)])
    return s


def _pokeball(inner=(220, 50, 50)) -> pygame.Surface:
    s = _surf()
    pygame.draw.circle(s, (220, 220, 220), (HALF, HALF), HALF-2)
    pygame.draw.rect(s, inner, (2, 2, C-4, HALF-2), border_radius=8)
    pygame.draw.line(s, (30, 30, 30), (2, HALF), (C-2, HALF), 2)
    pygame.draw.circle(s, (80, 80, 80), (HALF, HALF), 4)
    pygame.draw.circle(s, (200, 200, 200), (HALF, HALF), 3)
    return s


def _badge(color=(200, 200, 50)) -> pygame.Surface:
    s = _surf(w=16, h=16)
    pygame.draw.polygon(s, color, [(8,1),(15,6),(12,15),(4,15),(1,6)])
    return s


def _heart() -> pygame.Surface:
    s = _surf(w=14, h=14)
    pygame.draw.circle(s, (220, 50, 50), (4, 5), 4)
    pygame.draw.circle(s, (220, 50, 50), (10, 5), 4)
    pygame.draw.polygon(s, (220, 50, 50), [(0,6),(7,14),(14,6)])
    return s


def build_sprites() -> dict:
    SNAKE_COLOR = (80, 100, 200)
    sprites = {}
    for facing in ('right', 'left', 'up', 'down'):
        sprites[f'head_{facing}'] = _head(color=SNAKE_COLOR, facing=facing)
        sprites[f'head_{facing}_open'] = _head_open(color=SNAKE_COLOR, facing=facing)
    sprites['body'] = _body(color=SNAKE_COLOR)
    sprites['tail'] = _tail(color=SNAKE_COLOR)
    sprites['ball_normal'] = _pokeball(inner=(220, 50, 50))
    sprites['ball_super']  = _pokeball(inner=(50, 80, 220))
    sprites['ball_master'] = _pokeball(inner=(160, 0, 200))
    badge_colors = [
        (180,160,120),(80,160,220),(240,220,40),(80,200,80),
        (180,80,200),(220,120,200),(240,120,40),(120,60,220),
    ]
    for i, c in enumerate(badge_colors):
        sprites[f'badge_{i}'] = _badge(color=c)
    sprites['heart'] = _heart()
    return sprites
