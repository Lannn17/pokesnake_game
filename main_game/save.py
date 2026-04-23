# snake_game/save.py
import json
import os
from snake_game.config import STARTING_LIVES


def new_save(difficulty: str) -> dict:
    return {
        'current_gym': 0,
        'lives': STARTING_LIVES,
        'badges': [False] * 8,
        'total_score': 0,
        'best_scores': [0] * 8,
        'total_clear_time': 0.0,
        'difficulty': difficulty,
        'completed': False,
    }


def load(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def write(data: dict, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def delete(path: str):
    if os.path.exists(path):
        os.remove(path)
