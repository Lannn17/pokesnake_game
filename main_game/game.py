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
    GRID_W, GRID_H, BASE_SPEED, SPEED_CAP, SPEED_PER_10PTS,
    STARTING_LIVES, GYM_CLEAR_DURATION, SOUND_ENABLED, SAVE_PATH,
    GYM_WALL_COLORS,
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
    def __init__(self, renderer, sprites: dict, sounds: dict = None):
        self.renderer = renderer
        self.sprites = sprites
        self.sounds = sounds or {}
        self.state = State.MAIN_MENU
        self.save_data: dict = None
        self.difficulty: str = 'normal'
        self.menu_cursor = 0
        self.diff_cursor = 1

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

        self._step_timer: float = 0.0
        self._gym_clear_timer: float = 0.0
        self._gym_attempt_start: float = 0.0
        self._pause_start: float = 0.0
        self._pause_total: float = 0.0
        self._now: float = 0.0
        self._flash_frame: bool = False
        self._flash_accum: float = 0.0
        self._eating: bool = False

        self._ending_phase: str = 'congratulations'
        self._ending_phase_start: float = 0.0
        self._ending_phase_durations = {
            'congratulations': 3.0,
            'hakuryu': 2.5,
            'flash': 1.0,
            'dragonite': 2.5,
            'stats': float('inf'),
        }

    # --- Input ---
    def handle_event(self, event: pygame.event.Event):
        if event.type != pygame.KEYDOWN:
            return
        key = event.key

        if self.state == State.MAIN_MENU:
            options = ['つづきから', 'はじめから'] if self.save_data else ['はじめから']
            self._nav(key, len(options))
            if key in (pygame.K_RETURN, pygame.K_z):
                self._main_menu_confirm(options)

        elif self.state == State.CONFIRM_NEW:
            self._nav(key, 2)
            if key in (pygame.K_RETURN, pygame.K_z):
                if self.menu_cursor == 0:
                    save_module.delete(SAVE_PATH)
                    self.save_data = None
                    self.state = State.DIFFICULTY_SELECT
                    self.menu_cursor = 1
                else:
                    self.state = State.MAIN_MENU
                    self.menu_cursor = 0

        elif self.state == State.DIFFICULTY_SELECT:
            if key == pygame.K_UP:
                self.diff_cursor = (self.diff_cursor - 1) % 3
            elif key == pygame.K_DOWN:
                self.diff_cursor = (self.diff_cursor + 1) % 3
            elif key in (pygame.K_RETURN, pygame.K_z):
                self.difficulty = ['easy', 'normal', 'hard'][self.diff_cursor]
                self._start_new_run()

        elif self.state == State.PLAYING:
            dir_map = {
                pygame.K_UP: (0,-1), pygame.K_DOWN: (0,1),
                pygame.K_LEFT: (-1,0), pygame.K_RIGHT: (1,0),
            }
            if key in dir_map:
                self.snake.set_direction(dir_map[key])
            elif key == pygame.K_SPACE:
                self.state = State.PAUSED
                self._pause_start = time.monotonic()
                self.menu_cursor = 0

        elif self.state == State.PAUSED:
            self._nav(key, 2)
            if key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                if self.menu_cursor == 0 or key == pygame.K_SPACE:
                    self._pause_total += time.monotonic() - self._pause_start
                    self.state = State.PLAYING
                else:
                    self._save_and_go_menu()

        elif self.state == State.GYM_CLEAR:
            if self._gym_clear_timer <= 0:
                self._advance_gym()

        elif self.state == State.GAME_OVER:
            if self.lives <= 0:
                save_module.delete(SAVE_PATH)
                self.save_data = None
                self.state = State.MAIN_MENU
                self.menu_cursor = 0
            else:
                self._restart_gym()

        elif self.state == State.GAME_COMPLETE:
            if self._ending_phase == 'stats':
                self.state = State.MAIN_MENU
                self.menu_cursor = 0
                self.save_data = save_module.load(SAVE_PATH)

    def _nav(self, key, n: int):
        if key == pygame.K_UP:
            self.menu_cursor = (self.menu_cursor - 1) % n
        elif key == pygame.K_DOWN:
            self.menu_cursor = (self.menu_cursor + 1) % n

    def _main_menu_confirm(self, options):
        chosen = options[self.menu_cursor]
        if chosen == 'つづきから':
            self._load_and_continue()
        elif self.save_data:
            self.state = State.CONFIRM_NEW
            self.menu_cursor = 0
        else:
            self.state = State.DIFFICULTY_SELECT
            self.menu_cursor = 1

    # --- Update ---
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
            if self._gym_clear_timer > 0:
                self._gym_clear_timer -= dt
        elif self.state == State.GAME_COMPLETE:
            self._update_ending(now)

    def _update_playing(self, dt: float, now: float):
        self._step_timer += dt
        if self._step_timer < 1.0 / self.current_speed:
            return
        self._step_timer -= 1.0 / self.current_speed

        self.snake.move()
        hx, hy = self.snake.head

        if (hx < 0 or hx >= GRID_W or hy < 0 or hy >= GRID_H
                or self.snake.head in self.level.all_wall_cells()
                or self.snake.check_self_collision()):
            self._play_sound('death')
            self.lives -= 1
            self.state = State.GAME_OVER
            return

        snake_cells = set(self.snake.cells)
        score = self.balls.try_eat(self.snake.head, now, snake_cells)
        if score > 0:
            self.snake.grow()
            self.per_gym_score += score
            self.total_score += score
            self._eating = True
            self._play_sound('eat')
            new_speed = BASE_SPEED[self.difficulty] + (self.per_gym_score // 10) * SPEED_PER_10PTS
            self.current_speed = min(new_speed, SPEED_CAP[self.difficulty])
        else:
            self._eating = False

        head_adj = {(hx+dx, hy+dy) for dx,dy in ((1,0),(-1,0),(0,1),(0,-1))}
        self.balls.update(now, snake_cells=snake_cells, head_adjacent=head_adj)

        wall_occupied = snake_cells | self.balls.all_ball_cells() | head_adj
        self.level.try_spawn_wall(now, occupied_cells=wall_occupied)
        self.level.remove_expired(now)

        if self.per_gym_score >= self.level.target_score:
            self._on_gym_clear(now)

    def _on_gym_clear(self, now: float):
        elapsed = (now - self._gym_attempt_start) - self._pause_total
        self.total_clear_time += max(0.0, elapsed)
        self.best_scores[self.gym_index] = self.per_gym_score
        self.badges[self.gym_index] = True
        self.lives += 1
        self._play_sound('clear')
        self.state = State.GYM_CLEAR
        self._gym_clear_timer = GYM_CLEAR_DURATION
        self._write_save()

    def _advance_gym(self):
        if self.gym_index >= 7:
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
        self._pause_total = 0.0
        self.snake = Snake(start=_START_POS, direction=_START_DIR, length=3)
        self.level = Level(gym_index=self.gym_index, difficulty=self.difficulty)
        self.level.start(now)
        self.balls = BallManager(wall_cells=self.level.all_wall_cells())
        self.balls.reset(now)
        self._gym_attempt_start = now
        self.state = State.PLAYING

    def _restart_gym(self):
        now = time.monotonic()
        self.per_gym_score = 0
        self.current_speed = BASE_SPEED[self.difficulty]
        self._step_timer = 0.0
        self._pause_total = 0.0
        self.snake = Snake(start=_START_POS, direction=_START_DIR, length=3)
        self.level = Level(gym_index=self.gym_index, difficulty=self.difficulty)
        self.level.start(now)
        self.balls = BallManager(wall_cells=self.level.all_wall_cells())
        self.balls.reset(now)
        self._gym_attempt_start = now
        self.state = State.PLAYING

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

    # --- Ending ---
    def _start_ending(self):
        self.state = State.GAME_COMPLETE
        self._ending_phase = 'congratulations'
        self._ending_phase_start = self._now

    def _update_ending(self, now: float):
        dur = self._ending_phase_durations.get(self._ending_phase, 3.0)
        if dur == float('inf'):
            return
        if now - self._ending_phase_start >= dur:
            phases = ['congratulations', 'hakuryu', 'flash', 'dragonite', 'stats']
            idx = phases.index(self._ending_phase)
            if idx + 1 < len(phases):
                self._ending_phase = phases[idx + 1]
                self._ending_phase_start = now

    @property
    def ending_progress(self) -> float:
        dur = self._ending_phase_durations.get(self._ending_phase, 3.0)
        if dur == float('inf'):
            return 1.0
        return min(1.0, (self._now - self._ending_phase_start) / dur)

    # --- Draw ---
    def draw(self):
        r = self.renderer
        now = self._now

        if self.state == State.MAIN_MENU:
            r.draw_main_menu(has_save=self.save_data is not None, selected=self.menu_cursor)
        elif self.state == State.CONFIRM_NEW:
            r.draw_confirm_new_game(selected=self.menu_cursor)
        elif self.state == State.DIFFICULTY_SELECT:
            r.draw_difficulty_select(selected=self.diff_cursor)
        elif self.state in (State.PLAYING, State.PAUSED, State.GAME_OVER, State.GYM_CLEAR):
            gym = GYMS[self.gym_index]
            r.draw_bg(self.level.bg_accent, self.gym_index)
            r.draw_gym_ambient(self.gym_index, now)
            r.draw_walls_ex(self.level.fixed_walls, self.level.dynamic_walls,
                            self.level.wall_color, now, self._flash_frame)
            r.draw_balls(self.balls.get_all_balls())
            r.draw_snake(self.snake, eating=self._eating)
            r.draw_master_border(self.balls.master_ball_active(), self._flash_frame)
            r.draw_hud(score=self.per_gym_score, lives=self.lives, badges=self.badges,
                       master_remaining=self.balls.master_ball_remaining(now),
                       gym_name=gym.name, gym_type=gym.type_name,
                       type_color=GYM_WALL_COLORS[self.gym_index])
            if self.state == State.PAUSED:
                r.draw_pause_menu(selected=self.menu_cursor)
            elif self.state == State.GAME_OVER:
                r.draw_game_over(lives=self.lives)
            elif self.state == State.GYM_CLEAR:
                r.draw_gym_clear(gym_name=gym.name, ready=self._gym_clear_timer <= 0)
        elif self.state == State.GAME_COMPLETE:
            r.draw_ending(
                phase=self._ending_phase,
                progress=self.ending_progress,
                hakuryu_sprite=self._big_hakuryu(),
                dragonite_sprite=self._big_dragonite(),
                total_score=self.total_score,
                total_time=self.total_clear_time,
                best_scores=self.best_scores,
                badges=self.badges,
            )

    def _big_hakuryu(self) -> pygame.Surface:
        s = self.sprites.get('head_right', pygame.Surface((20, 20)))
        return pygame.transform.scale(s, (120, 120))

    def _big_dragonite(self) -> pygame.Surface:
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(s, (240, 160, 40), (60, 70), 40)
        pygame.draw.ellipse(s, (240, 200, 80), (5, 20, 45, 25))
        pygame.draw.ellipse(s, (240, 200, 80), (70, 20, 45, 25))
        pygame.draw.circle(s, (255, 255, 200), (52, 62), 6)
        pygame.draw.circle(s, (255, 255, 200), (68, 62), 6)
        return s

    def _play_sound(self, name: str):
        if not SOUND_ENABLED:
            return
        snd = self.sounds.get(name)
        if snd:
            snd.play()
