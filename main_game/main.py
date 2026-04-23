# snake_game/main.py
import sys
import time
import os
import pygame
from snake_game.config import WINDOW_W, WINDOW_H, FPS, SOUND_ENABLED
from snake_game.sprites import build_sprites
from snake_game.renderer import Renderer
from snake_game.game import Game


def load_font(size: int) -> pygame.font.Font:
    font_path = os.path.join(os.path.dirname(__file__), 'assets', 'fonts', 'pixel.ttf')
    if os.path.exists(font_path):
        return pygame.font.Font(font_path, size)
    for name in ('meiryo', 'msgothic', 'mspgothic', 'yugothic', 'msmincho'):
        f = pygame.font.SysFont(name, size)
        if f is not None:
            return f
    return pygame.font.Font(None, size)


def load_sounds() -> dict:
    if not SOUND_ENABLED:
        return {}
    sounds = {}
    sound_dir = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')
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
        try:
            pygame.mixer.init()
        except Exception:
            pass

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
