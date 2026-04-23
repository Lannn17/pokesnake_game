import sys, os
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
    wall = DynamicWall(cells=[(5, 5)], lifespan=2.0, spawn_time=0.0)
    assert wall.is_expired(current_time=1.0) is False
    assert wall.is_expired(current_time=2.5) is True

def test_dynamic_wall_alpha():
    wall = DynamicWall(cells=[(5, 5)], lifespan=3.0, spawn_time=0.0)
    assert wall.alpha(current_time=0.0) == 255
    assert wall.alpha(current_time=1.5) < 255

def test_spawn_wall_respects_cap():
    level = Level(gym_index=7, difficulty='normal')  # cap=12
    level.start(now=0.0)
    occupied = set()
    for _ in range(20):
        level.try_spawn_wall(current_time=1000.0, occupied_cells=occupied)
    assert len(level.dynamic_walls) <= 12

def test_spawn_wall_avoids_occupied():
    level = Level(gym_index=0, difficulty='normal')
    level.start(now=0.0)
    occupied = {(x, y) for x in range(25) for y in range(20) if (x, y) not in [(12, 10)]}
    level.try_spawn_wall(current_time=1000.0, occupied_cells=occupied)
    for w in level.dynamic_walls:
        for cell in w.cells:
            assert cell not in occupied
