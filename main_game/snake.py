# snake_game/snake.py

class Snake:
    """Pure logic snake — no pygame dependency."""

    def __init__(self, start: tuple, direction: tuple, length: int = 3):
        x, y = start
        dx, dy = direction
        self.body = [(x - dx * i, y - dy * i) for i in range(length)]
        self.direction = direction
        self._pending_growth = 0
        self._buffered_dir = None  # 缓冲下一步方向

    def set_direction(self, new_dir: tuple):
        """Buffer next direction; ignore reversal."""
        # 以当前实际移动方向（而非缓冲方向）来判断是否反向
        ref = self._buffered_dir if self._buffered_dir else self.direction
        if (new_dir[0] + ref[0], new_dir[1] + ref[1]) != (0, 0):
            self._buffered_dir = new_dir

    def grow(self):
        """Queue one extra segment for next move."""
        self._pending_growth += 1

    def move(self):
        """Advance the snake one cell in current direction."""
        # 每次移动时才从缓冲取出方向
        if self._buffered_dir is not None:
            self.direction = self._buffered_dir
            self._buffered_dir = None
        hx, hy = self.body[0]
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)
        self.body.insert(0, new_head)
        if self._pending_growth > 0:
            self._pending_growth -= 1
        else:
            self.body.pop()

    def check_self_collision(self) -> bool:
        return self.body[0] in self.body[1:]

    def occupies(self, x: int, y: int) -> bool:
        return (x, y) in self.body

    @property
    def head(self) -> tuple:
        return self.body[0]

    @property
    def cells(self) -> list:
        return self.body
