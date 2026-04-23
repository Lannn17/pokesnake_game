import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import snake_game.save as save_module

def test_no_save_returns_none(tmp_path):
    path = str(tmp_path / 'save.json')
    assert save_module.load(path) is None

def test_save_and_load(tmp_path):
    path = str(tmp_path / 'save.json')
    data = save_module.new_save('normal')
    save_module.write(data, path)
    loaded = save_module.load(path)
    assert loaded['difficulty'] == 'normal'
    assert loaded['lives'] == 1
    assert loaded['current_gym'] == 0

def test_delete_save(tmp_path):
    path = str(tmp_path / 'save.json')
    data = save_module.new_save('easy')
    save_module.write(data, path)
    save_module.delete(path)
    assert save_module.load(path) is None

def test_new_save_structure():
    data = save_module.new_save('hard')
    assert len(data['badges']) == 8
    assert len(data['best_scores']) == 8
    assert data['completed'] is False
    assert data['total_clear_time'] == 0.0
