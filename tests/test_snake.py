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
    assert len(s.body) == 3

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
    s.body = [(5, 10), (4, 10), (5, 10)]
    assert s.check_self_collision() is True

def test_set_direction_ignores_reverse():
    s = Snake(start=(5, 10), direction=(1, 0), length=3)
    s.set_direction((-1, 0))
    assert s.direction == (1, 0)

def test_set_direction_accepts_perpendicular():
    s = Snake(start=(5, 10), direction=(1, 0), length=3)
    s.set_direction((0, -1))
    s.move()  # direction is buffered and applied on move()
    assert s.direction == (0, -1)

def test_occupies():
    s = Snake(start=(5, 10), direction=(1, 0), length=3)
    assert s.occupies(5, 10) is True
    assert s.occupies(4, 10) is True
    assert s.occupies(99, 99) is False
