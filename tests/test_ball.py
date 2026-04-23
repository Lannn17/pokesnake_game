import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from snake_game.ball import BallManager

def make_manager():
    return BallManager(wall_cells=set(), grid_w=25, grid_h=20)

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
    assert len(bm.get_all_balls()) == 2

def test_super_ball_appears_after_interval():
    bm = make_manager()
    bm.reset(now=0.0)
    bm.update(now=36.0, snake_cells=set(), head_adjacent=set())
    types = [b['type'] for b in bm.get_all_balls()]
    assert 'super' in types

def test_master_ball_score():
    bm = make_manager()
    bm.reset(now=0.0)
    bm._master_ball = {'pos': (10, 10), 'type': 'master', 'expire_time': 100.0}
    score = bm.try_eat((10, 10), now=1.0, snake_cells=set())
    assert score == 5

def test_no_spawn_on_wall():
    walls = {(x, y) for x in range(25) for y in range(20) if (x, y) != (12, 10)}
    bm = BallManager(wall_cells=walls, grid_w=25, grid_h=20)
    bm.reset(now=0.0)
    for b in bm.get_all_balls():
        assert b['pos'] == (12, 10)
