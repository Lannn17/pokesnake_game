# snake_game/renderer.py
import pygame
import math
from snake_game.config import (
    CELL_SIZE, GRID_W, GRID_H, GAME_W, GAME_H, HUD_H, WINDOW_W, WINDOW_H,
    COLOR_BG, COLOR_GRID, COLOR_HUD_BG, COLOR_WHITE, COLOR_BLACK,
    GYM_GRID_COLORS,
)


class Renderer:
    def __init__(self, screen: pygame.Surface, sprites: dict, font_small, font_large):
        self.screen = screen
        self.sprites = sprites
        self.font_s = font_small
        self.font_l = font_large

    def _cell_rect(self, x, y) -> pygame.Rect:
        return pygame.Rect(x * CELL_SIZE, HUD_H + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

    def draw_bg(self, bg_accent, gym_index: int = 0):
        self.screen.fill(bg_accent)
        grid_color = GYM_GRID_COLORS[gym_index] if 0 <= gym_index < len(GYM_GRID_COLORS) else COLOR_GRID
        for x in range(GRID_W):
            for y in range(GRID_H):
                pygame.draw.rect(self.screen, grid_color, self._cell_rect(x, y), 1)

    def draw_gym_ambient(self, gym_index: int, now: float):
        """Draw gym-specific ambient decorative effects."""
        GAME_TOP = HUD_H
        GAME_BOTTOM = HUD_H + GAME_H
        MID_X = GAME_W // 2
        MID_Y = GAME_TOP + GAME_H // 2

        if gym_index == 0:  # ニビ - Rock: stone blocks in corners
            for cx, cy in [(4, GAME_TOP+4), (GAME_W-36, GAME_TOP+4),
                           (4, GAME_BOTTOM-36), (GAME_W-36, GAME_BOTTOM-36)]:
                for i in range(2):
                    for j in range(2):
                        s = pygame.Surface((14, 14), pygame.SRCALPHA)
                        s.fill((105, 92, 78, 50))
                        self.screen.blit(s, (cx + i * 16, cy + j * 16))

        elif gym_index == 1:  # ハナダ - Water: animated waves at bottom
            wave_surf = pygame.Surface((GAME_W, 26), pygame.SRCALPHA)
            for row in range(3):
                y = 20 - row * 7
                phase = now * 2.2 + row * 0.9
                pts = [(x, y + int(math.sin(phase + x * 0.045) * 4))
                       for x in range(0, GAME_W + 1, 5)]
                if len(pts) >= 2:
                    pygame.draw.lines(wave_surf, (65, 145, 230, 80 - row * 18), False, pts, 2)
            self.screen.blit(wave_surf, (0, GAME_BOTTOM - 26))

        elif gym_index == 2:  # クチバ - Electric: spark bolts at corners
            t = now * 4.5
            corners = [
                (12, GAME_TOP+12, 1, 1), (GAME_W-12, GAME_TOP+12, -1, 1),
                (12, GAME_BOTTOM-12, 1, -1), (GAME_W-12, GAME_BOTTOM-12, -1, -1),
            ]
            for i, (ex, ey, dx, dy) in enumerate(corners):
                if math.sin(t + i * 2.1) > 0.15:
                    pts = [(ex, ey)]
                    for k in range(1, 5):
                        jx = int(math.sin(t * 3.1 + k * 1.8) * 6) * dy
                        jy = int(math.sin(t * 2.7 + k * 1.3) * 6) * dx
                        pts.append((ex + dx * k * 8 + jx, ey + dy * k * 6 + jy))
                    pygame.draw.lines(self.screen, (255, 245, 70), False, pts, 2)

        elif gym_index == 3:  # タマムシ - Grass: falling leaf particles
            for i in range(12):
                phase = (now * 0.55 + i * (1.0/12)) % 1.0
                lx = (i * 43 + 8) % GAME_W
                ly = GAME_TOP + int(phase * GAME_H)
                swing = int(math.sin(now * 1.4 + i * 0.7) * 11)
                s = pygame.Surface((10, 10), pygame.SRCALPHA)
                pygame.draw.polygon(s, (72, 196, 58, 105), [(5, 0), (9, 5), (5, 9), (1, 5)])
                self.screen.blit(s, (lx + swing, ly))

        elif gym_index == 4:  # セキチク - Poison: rising bubble particles
            for i in range(9):
                phase = (now * 0.38 + i * (1.0/9)) % 1.0
                bx = (i * 57 + 18) % GAME_W
                by = GAME_BOTTOM - int(phase * GAME_H)
                r = 3 + (i % 3) * 2
                s = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
                pygame.draw.circle(s, (195, 72, 215, 65), (r+2, r+2), r)
                pygame.draw.circle(s, (220, 135, 255, 95), (r+2, r+2), r, 1)
                self.screen.blit(s, (bx - r - 2, by - r - 2))

        elif gym_index == 5:  # ヤマブキ - Psychic: orbiting star particles
            for ring_rx, ring_ry, n, speed, color in [
                (95, 48, 6, 1.15, (225, 78, 225, 85)),
                (145, 72, 8, -0.72, (180, 78, 255, 58)),
            ]:
                for i in range(n):
                    angle = (i / n) * 2 * math.pi + now * speed
                    px = int(MID_X + ring_rx * math.cos(angle))
                    py = int(MID_Y + ring_ry * math.sin(angle))
                    s = pygame.Surface((8, 8), pygame.SRCALPHA)
                    pygame.draw.circle(s, color, (4, 4), 3)
                    self.screen.blit(s, (px - 4, py - 4))

        elif gym_index == 6:  # グレン - Fire: flame tips along bottom edge
            t = now * 3.8
            for fx in range(0, GAME_W, 20):
                flicker = math.sin(t + fx * 0.38) * 0.38 + 0.62
                h = max(2, int(18 * flicker))
                s = pygame.Surface((18, h), pygame.SRCALPHA)
                pygame.draw.polygon(s, (238, 68, 12, 155), [(1, h-1), (9, 0), (17, h-1)])
                if h > 5:
                    pygame.draw.polygon(s, (255, 195, 30, 145), [(5, h-1), (9, 3), (13, h-1)])
                self.screen.blit(s, (fx + 1, GAME_BOTTOM - h))

        elif gym_index == 7:  # トキワ - Dragon: glowing orbs orbiting perimeter
            for i in range(14):
                angle = (i / 14) * 2 * math.pi + now * 0.52
                rx = GAME_W // 2 - 22
                ry = GAME_H // 2 - 22
                px = int(MID_X + rx * math.cos(angle))
                py = int(MID_Y + ry * 0.62 * math.sin(angle))
                glow = 4 + int(2 * math.sin(now * 2.6 + i * 0.45))
                s = pygame.Surface((glow*4, glow*4), pygame.SRCALPHA)
                pygame.draw.circle(s, (68, 32, 195, 48), (glow*2, glow*2), glow*2)
                pygame.draw.circle(s, (148, 88, 255, 88), (glow*2, glow*2), glow)
                self.screen.blit(s, (px - glow*2, py - glow*2))

    def draw_walls_ex(self, fixed_walls, dynamic_walls, wall_color, now: float, flash_frame: bool):
        fixed_color = tuple(min(255, c + 55) for c in wall_color)
        for (wx, wy) in fixed_walls:
            pygame.draw.rect(self.screen, fixed_color, self._cell_rect(wx, wy))
            # inner highlight line for depth
            r = self._cell_rect(wx, wy)
            pygame.draw.rect(self.screen, tuple(min(255, c + 90) for c in wall_color),
                             pygame.Rect(r.x+1, r.y+1, r.w-2, 2))
        for dw in dynamic_walls:
            alpha = dw.alpha(now)
            color = COLOR_WHITE if (dw.is_flashing(now) and flash_frame) else wall_color
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            surf.fill((*color, alpha))
            for (cx, cy) in dw.cells:
                self.screen.blit(surf, self._cell_rect(cx, cy))

    def draw_snake(self, snake, eating: bool):
        facing_map = {(1,0):'right',(-1,0):'left',(0,-1):'up',(0,1):'down'}
        facing = facing_map.get(snake.direction, 'right')
        key = f'head_{facing}_open' if eating else f'head_{facing}'
        for i, (bx, by) in enumerate(snake.body):
            if i == 0:
                self.screen.blit(self.sprites[key], self._cell_rect(bx, by))
            elif i == len(snake.body) - 1:
                self.screen.blit(self.sprites['tail'], self._cell_rect(bx, by))
            else:
                self.screen.blit(self.sprites['body'], self._cell_rect(bx, by))

    def draw_balls(self, balls: list):
        key_map = {'normal': 'ball_normal', 'super': 'ball_super', 'master': 'ball_master'}
        for b in balls:
            bx, by = b['pos']
            self.screen.blit(self.sprites[key_map.get(b['type'], 'ball_normal')],
                             self._cell_rect(bx, by))

    def draw_master_border(self, active: bool, flash_frame: bool):
        if active and flash_frame:
            pygame.draw.rect(self.screen, (200, 0, 255),
                             pygame.Rect(0, HUD_H, GAME_W, GAME_H), 3)

    def draw_hud(self, score: int, lives: int, badges: list,
                 master_remaining: float, gym_name: str,
                 gym_type: str = '', type_color: tuple = COLOR_WHITE):
        pygame.draw.rect(self.screen, COLOR_HUD_BG, pygame.Rect(0, 0, WINDOW_W, HUD_H))
        self.screen.blit(self.font_s.render(f'SCORE {score:04d}', True, COLOR_WHITE), (8, 8))
        name_surf = self.font_s.render(gym_name, True, COLOR_WHITE)
        self.screen.blit(name_surf, (8, 32))
        if gym_type:
            type_surf = self.font_s.render(f' [{gym_type}]', True, type_color)
            self.screen.blit(type_surf, (8 + name_surf.get_width(), 32))
        for i in range(lives):
            self.screen.blit(self.sprites['heart'], (180 + i * 18, 10))
        for i, earned in enumerate(badges):
            if earned:
                self.screen.blit(self.sprites[f'badge_{i}'], (180 + i * 18, 32))
        if master_remaining > 0:
            m = self.font_s.render(f'★ {master_remaining:.1f}s', True, (200, 0, 255))
            self.screen.blit(m, (400, 8))

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
        title = self.font_l.render('むずかしさをえらんでください', True, COLOR_WHITE)
        self.screen.blit(title, title.get_rect(center=(WINDOW_W//2, 140)))
        opts = ['かんたん', 'ふつう', 'むずかしい']
        for i, label in enumerate(opts):
            color = (255, 220, 0) if i == selected else COLOR_WHITE
            txt = self.font_s.render(label, True, color)
            self.screen.blit(txt, txt.get_rect(center=(WINDOW_W//2, 230 + i * 44)))

    def draw_pause_menu(self, selected: int):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        title = self.font_l.render('ポーズ', True, COLOR_WHITE)
        self.screen.blit(title, title.get_rect(center=(WINDOW_W//2, 160)))
        for i, opt in enumerate(['つづける', 'タイトルへ']):
            color = (255, 220, 0) if i == selected else COLOR_WHITE
            txt = self.font_s.render(opt, True, color)
            self.screen.blit(txt, txt.get_rect(center=(WINDOW_W//2, 240 + i * 44)))

    def draw_game_over(self, lives: int):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        txt = self.font_l.render('ゲームオーバー', True, (220, 50, 50))
        self.screen.blit(txt, txt.get_rect(center=(WINDOW_W//2, 200)))
        sub_text = 'なんでもおして つづける' if lives > 0 else 'なんでもおして タイトルへ'
        sub = self.font_s.render(sub_text, True, COLOR_WHITE)
        self.screen.blit(sub, sub.get_rect(center=(WINDOW_W//2, 270)))

    def draw_gym_clear(self, gym_name: str, ready: bool = False):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        txt = self.font_l.render(f'{gym_name} クリア！', True, (255, 220, 0))
        self.screen.blit(txt, txt.get_rect(center=(WINDOW_W//2, 200)))
        if ready:
            sub = self.font_s.render('なんでもおして つぎへ', True, COLOR_WHITE)
            self.screen.blit(sub, sub.get_rect(center=(WINDOW_W//2, 270)))

    def draw_confirm_new_game(self, selected: int):
        self.screen.fill(COLOR_BLACK)
        q = self.font_s.render('ほんとうによいですか？', True, COLOR_WHITE)
        self.screen.blit(q, q.get_rect(center=(WINDOW_W//2, 200)))
        for i, opt in enumerate(['はい', 'いいえ']):
            color = (255, 220, 0) if i == selected else COLOR_WHITE
            txt = self.font_s.render(opt, True, color)
            self.screen.blit(txt, txt.get_rect(center=(WINDOW_W//2, 270 + i * 44)))

    def draw_ending(self, phase: str, progress: float,
                    hakuryu_sprite, dragonite_sprite,
                    total_score: int, total_time: float,
                    best_scores: list, badges: list):
        self.screen.fill(COLOR_BLACK)
        cx, cy = WINDOW_W // 2, WINDOW_H // 2

        if phase == 'congratulations':
            alpha = min(255, int(255 * progress * 3))
            txt = self.font_l.render('Congratulations!', True, COLOR_WHITE)
            txt.set_alpha(alpha)
            self.screen.blit(txt, txt.get_rect(center=(cx, cy)))

        elif phase == 'hakuryu':
            self.screen.blit(hakuryu_sprite, hakuryu_sprite.get_rect(center=(cx, cy - 20)))
            for i in range(12):
                angle = (i / 12) * 2 * math.pi + progress * 4
                r = 40 + 20 * math.sin(progress * math.pi * 2)
                px = int(cx + r * math.cos(angle))
                py = int(cy - 20 + r * math.sin(angle))
                pygame.draw.circle(self.screen, COLOR_WHITE, (px, py), 3)

        elif phase == 'flash':
            flash = pygame.Surface((WINDOW_W, WINDOW_H))
            flash.fill(COLOR_WHITE)
            flash.set_alpha(int(255 * progress))
            self.screen.blit(flash, (0, 0))

        elif phase == 'dragonite':
            dragonite_sprite.set_alpha(int(255 * progress))
            self.screen.blit(dragonite_sprite, dragonite_sprite.get_rect(center=(cx, cy - 20)))

        elif phase == 'stats':
            title = self.font_l.render('Congratulations!', True, (255, 220, 0))
            self.screen.blit(title, title.get_rect(center=(cx, 55)))
            self.screen.blit(self.font_s.render(f'トータルスコア: {total_score}', True, COLOR_WHITE), (60, 110))
            mins, secs = int(total_time) // 60, int(total_time) % 60
            self.screen.blit(self.font_s.render(f'クリアタイム: {mins:02d}:{secs:02d}', True, COLOR_WHITE), (60, 138))
            for i, s in enumerate(best_scores):
                t = self.font_s.render(f'Gym{i+1}: {s}pt', True, COLOR_WHITE)
                self.screen.blit(t, (60 + (i % 4) * 110, 175 + (i // 4) * 26))
            for i, earned in enumerate(badges):
                if earned:
                    self.screen.blit(self.sprites[f'badge_{i}'], (60 + i * 40, 250))
            any_key = self.font_s.render('なんでもおして タイトルへ', True, (180, 180, 180))
            self.screen.blit(any_key, any_key.get_rect(center=(cx, 360)))
