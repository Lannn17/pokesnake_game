# Snake Game Design Spec — ポケモン貪食蛇
Date: 2026-04-22
Version: 1.3

## Overview

A local Snake game built with Python + pygame, featuring a Pokémon GB-era pixel art theme. The player controls Hakuryu (Dragonair) through 8 gym-themed levels, collecting Poké Balls to score points and earning gym badges. Completing all 8 gyms triggers a Hakuryu→Dragonite evolution ending animation.

**System Language**: Japanese (UI, menus, system prompts)
**Ending Animation Text**: English ("Congratulations!")
**Tech Stack**: Python + pygame, modular file structure

---

## Directory Structure

```
snake_game/
├── main.py              # Entry point, pygame init, main loop
├── game.py              # Game state machine
├── snake.py             # Snake movement, collision, growth logic
├── level.py             # 8 gym level definitions
├── ball.py              # Poké Ball spawning and timer logic
├── renderer.py          # All drawing logic (pixel art style)
├── save.py              # Save/load (JSON)
├── config.py            # Constants (grid size, colors, speed, scores)
└── assets/
    ├── sprites/
    │   ├── snake/       # Hakuryu head (4 directions), body, tail sprites
    │   ├── balls/       # Poké Ball, Great Ball, Master Ball sprites
    │   ├── walls/       # Wall tile sprites per gym theme
    │   ├── badges/      # 8 gym badge sprites
    │   └── ending/      # Evolution animation frames
    ├── fonts/           # GB-style pixel font
    └── sounds/          # Eat, clear, game over SFX (optional)
```

---

## Game State Machine

```
MAIN_MENU → DIFFICULTY_SELECT → PLAYING ⇄ PAUSED
                                    ↓
                               GAME_OVER → PLAYING (retry, lives > 0)
                                    ↓
                               GAME_OVER → MAIN_MENU (lives = 0, save cleared)
                                    ↓
                              GYM_CLEAR → PLAYING (next gym)
                                    ↓
                            GAME_COMPLETE (ending animation)
```

### PAUSED State Transitions
- **Enter PAUSED**: press Space during PLAYING
- **Resume**: press Space again → return to PLAYING
- **Return to menu from PAUSED**: dedicated menu option → triggers save write → MAIN_MENU
- On mid-gym return to menu: `current_gym` is saved, in-progress gym score is discarded, only cleared gym scores are in `best_scores`

### GAME_OVER State Transitions
- **Enter GAME_OVER**: on collision (wall / self) during PLAYING
- GAME_OVER screen displays a Japanese prompt
- If lives > 0: press any key → deduct 1 life, reset per-gym score and speed to base, re-enter PLAYING (same gym)
- If lives = 0: press any key → delete save, return to MAIN_MENU
- GYM_CLEAR is a 0.5s non-interactive state (all input ignored); transitions automatically to PLAYING (next gym) on completion

### Main Loop (per frame)
1. Handle input (arrow keys, Space to pause)
2. Advance snake by one grid step on timer tick
3. Check collisions (wall / obstacle / self)
4. Check Poké Ball collection → score, grow, trigger Master Ball timer
5. Check dynamic wall add/remove conditions
6. Check gym clear condition (per-gym score ≥ gym target)
7. Call renderer

---

## Score System

**Scores are tracked per-gym.** Each gym starts with a score counter at 0. The gym clear condition compares this per-gym counter against the gym's target score. Upon clearing a gym, the per-gym score is written to `best_scores[gym_index]` and added to `total_score`. The per-gym counter resets to 0 at the start of each gym.

---

## Difficulty System

| Difficulty | Base Speed | Speed Cap | Wall Interval Multiplier |
|------------|-----------|-----------|------------------------|
| かんたん   | 8 steps/s | 14 steps/s | ×1.4 |
| ふつう     | 12 steps/s| 18 steps/s | ×1.0 |
| むずかしい | 16 steps/s| 22 steps/s | ×0.7 |

Speed increases by 1 step/s for every 10 **per-gym** points scored. Speed resets to base at the start of each new gym and also on retry of the same gym.

---

## Lives & Death System

- Start with 1 life
- Earn +1 life on each gym clear (awarded before entering next gym)
- On death:
  - If lives > 0 → deduct 1 life, retry current gym from start (per-gym score resets to 0)
  - If lives = 0 → game over, save file deleted, return to MAIN_MENU

**Note**: Starting with 1 life means dying twice in Gym 1 (without clearing it) results in game over on the second death. This is intentional.

---

## 8 Gym Levels

Each gym defined in `level.py` as a data class: initial wall coordinate list, dynamic wall parameters per difficulty, background color accent, target score.

| # | 都市名 | リーダー | タイプ | Initial Wall Style | Target Score | Expected Clear Time |
|---|--------|---------|------|--------------------|-------------|---------------------|
| 1 | ニビシティ | タケシ | いわ | Sparse corner stones | 10 | ~1.5 min |
| 2 | ハナダシティ | カスミ | みず | Central channel shape | 15 | ~2 min |
| 3 | クチバシティ | マチス | でんき | Lightning zigzag | 22 | ~2.5 min |
| 4 | タマムシシティ | エリカ | くさ | Scattered tree clusters | 30 | ~3 min |
| 5 | セキチクシティ | キョウ | どく | Grid mesh pattern | 40 | ~3.5 min |
| 6 | ヤマブキシティ | ナツメ | エスパー | Symmetric cross walls | 50 | ~4 min |
| 7 | グレンタウン | カツラ | ほのお | Volcanic rock corridor | 62 | ~4.5 min |
| 8 | トキワシティ | サカキ | ドラゴン* | Spiral inner maze | 75 | ~5 min |

*Gym 8 uses Dragon theme intentionally (not Giovanni's canonical Ground) to create a climactic final level and connect thematically to the Hakuryu→Dragonite ending.

---

## Dynamic Wall System

Each dynamic wall block has:
- A **lifespan**: counts down from spawn; removed on expiry
- A **spawn interval**: how often a new dynamic wall is added (per difficulty)
- A **cap**: maximum simultaneous dynamic walls; when cap is reached, the oldest dynamic wall is forcibly removed before spawning a new one

**Spawn safety rule**: A dynamic wall may not spawn on any cell occupied by the snake body, in any of the 4 directly adjacent cells of the snake head, or on any cell occupied by an existing ball.

Dynamic wall expiry animation: alpha decreases linearly over the final 3 seconds; in the final 1 second, the wall flashes to give a clear warning. Dynamic walls use gym-attribute colors to distinguish from fixed walls.

| # | 都市名 | Wall Lifespan | Cap | ふつう Interval | Wall Color Theme |
|---|--------|--------------|-----|----------------|-----------------|
| 1 | ニビ | 40s | 3 | 45s | Stone gray |
| 2 | ハナダ | 30s | 4 | 38s | Water blue (fades fast, like tide) |
| 3 | クチバ | 25s | 5 | 32s | Electric yellow |
| 4 | タマムシ | 30s | 6 | 27s | Grass green |
| 5 | セキチク | 20s | 7 | 22s | Poison purple |
| 6 | ヤマブキ | 22s | 8 | 18s | Psychic pink |
| 7 | グレン | 25s | 9 | 13s | Fire orange-red |
| 8 | トキワ | 50s | 12 | 8s | Dragon purple (long-lasting, most chaotic) |

かんたん interval = ふつう × 1.4 / むずかしい interval = ふつう × 0.7

---

## Poké Ball System

Map always holds **2 active regular/great ball slots** plus an optional **Master Ball slot** (separate).

### モンスターボール (1pt)
- Always present: at least 1 on map at all times
- On eaten: immediately respawns at a random empty cell

### スーパーボール (2pt)
- Spawn: every 25–35s (random), one モンスターボール chosen at random is replaced by a スーパーボール
- Despawn: eaten (モンスターボール respawns in its place), or 30s elapses (reverts to モンスターボール in same cell)
- Timer restart: after a revert or eat event, a new 25–35s countdown begins immediately

### マスターボール (5pt)
- Trigger: a 20–40s timer (random) runs continuously; on expiry, 30% chance of spawning
  - Success (30%): Master Ball appears, 8s visibility window begins; next attempt timer starts after ball is collected or expires
  - Failure (70%): no spawn; new 20–40s timer begins immediately
- Only 1 Master Ball at a time; trigger attempts skipped while one is active
- On appearance: screen border flashes; HUD shows 8s countdown

All spawn positions must avoid: wall cells, snake body cells, and existing ball cells. Head-adjacency exclusion is intentionally not applied to balls — a ball spawning one step ahead of the snake is a valid reward opportunity, not a hazard.

**Gym transition**: On GYM_CLEAR, all active balls are removed and all ball timers reset. The new gym starts with a fresh モンスターボール spawn and fresh スーパーボール and マスターボール timer countdowns.

---

## Visual Style

**Window**: 500×460px total
**Game area**: 500×400px (25×20 grid, 20px per cell)
**HUD**: 60px top bar — per-gym score, lives (heart icons), badges (small sprites), Master Ball countdown

**Color Palette** (GBC Pokémon-inspired):

| Element | Color |
|---------|-------|
| Background | `#1a3a2a` |
| Grid lines | `#1e402f` |
| Fixed walls | `#c8b89a` (stone) |
| Dynamic walls | Gym-attribute color, alpha fades with remaining lifespan |
| HUD | `#0a0a0a` with white pixel text |

**Hakuryu Sprite Set**:
- Head: 4 directional sprites (up/down/left/right); mouth-open variant used for 1 game-tick eating animation
- Body: Blue-purple rounded segment with white orb detail
- Tail: Tapered tail segment

**Animations**:
- Eating: head switches to mouth-open sprite for 1 game tick
- Master Ball alert: border flashes every 0.5s while ball is on map
- Gym clear: pixel star burst animation (0.5s)
- Dynamic wall expiry: alpha decreases linearly over final 3s, flashes in final 1s (consistent with Dynamic Wall System section)
- Ending: Hakuryu → Dragonite evolution sequence

---

## Ending Animation (GAME_COMPLETE)

Triggered after all 8 badges collected:

1. Fade to black
2. "Congratulations!" in pixel font, center screen (3s)
3. Hakuryu sprite appears center, surrounded by gathering white particles
4. White flash covers full screen
5. Dragonite silhouette emerges from white, resolves to full sprite
6. Stats screen: total score, total clear time, per-gym best scores, all 8 badge icons
7. Press any key → MAIN_MENU (save `completed = true`)

Animation frames stored in `assets/sprites/ending/`. `renderer.py` handles via `draw_ending_animation()`.

---

## Save System

File: `save/save.json`

```json
{
  "current_gym": 3,
  "lives": 3,
  "badges": [true, true, false, false, false, false, false, false],
  "total_score": 25,
  "best_scores": [10, 15, 0, 0, 0, 0, 0, 0],
  "total_clear_time": 210.5,
  "difficulty": "normal",
  "completed": false
}
```

`total_clear_time` is cumulative seconds, accumulated only while in the PLAYING state (pause time excluded). Each gym attempt has its own timer that starts when PLAYING is entered for that gym and resets on retry. Only the successful clear attempt's elapsed time is added to `total_clear_time`. Written on each gym clear, displayed on the ending stats screen.

**Write triggers**:
- Gym cleared → write (badges, lives +1, best_scores, total_score updated)
- Return to main menu from PAUSED → write (current_gym saved, in-progress gym score discarded)

**Delete trigger**:
- Lives = 0 game over → delete save file

**Main menu logic**:
- Save exists → show `つづきから` / `はじめから`
- No save → go directly to difficulty select
- `はじめから` → Japanese confirmation prompt ("ほんとうによいですか？ はい / いいえ"); `はい` overwrites save and goes to DIFFICULTY_SELECT; `いいえ` returns to MAIN_MENU

---

## Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `main.py` | pygame init, clock, top-level loop |
| `game.py` | State machine, per-frame update orchestration |
| `snake.py` | Grid position list, direction, move, grow, self-collision detection |
| `level.py` | Gym data classes, fixed wall coordinates, dynamic wall spawn/expire logic |
| `ball.py` | Ball state, spawn timers, Master Ball trigger logic |
| `renderer.py` | All `pygame.draw`/`blit` calls, animation state |
| `save.py` | JSON read/write, save existence check |
| `config.py` | All constants (speeds, intervals, colors, scores, timers) |

`game.py` orchestrates but does not draw or calculate physics. Each module is independently understandable without reading others' internals.

---

## Key Design Principles

- All tunable numbers live in `config.py` — easy to adjust after playtesting; includes `SOUND_ENABLED = True` flag; all sound calls guarded by this flag so the game runs silently on environments without audio
- `best_scores[i]` always overwrites on gym clear (each gym is played at most once per run, so there is no cross-session best to protect)
- Per-gym score is the source of truth for clear conditions and speed ramp; total_score is a display/save aggregate only
- Dynamic wall spawn never targets cells adjacent to the snake head (4-directional)
- Ball spawn never overlaps walls, snake body, or other balls
- Speed resets to base at each gym start for consistent early-gym feel
