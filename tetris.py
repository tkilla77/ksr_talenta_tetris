from enum import Enum
import random

class Cell(Enum):
    EMPTY = 1
    RED = 2
    BLUE = 3
    GREEN = 4

class Piece:
    def __init__(self, coords, color):
        self.coords = coords
        self.color = color

    def width(self):
        result = 0
        for c in self.coords:
            result = max(result, c[1] + 1)
        return result

    def height(self):
        result = 0
        for c in self.coords:
            result = max(result, c[0] + 1)
        return result

    def rotate(self):
        """Rotate CCW and ensure 0,0 is the upper left corner."""
        # Rotation matrix is [[0, -1], [1, 0]]
        minx, miny = 0, 0
        for c in self.coords:
            c[0], c[1] = -c[1], c[0]
            minx = min(minx, c[0])
            miny = min(miny, c[1])
        for c in self.coords:
            c[0] -= minx
            c[1] -= miny


class Tetris:
    def __init__(self, rows=20, cols=10):
        self.rows = rows
        self.cols = cols
        self.grid = [[Cell.EMPTY] * cols for _ in range(rows)]
        self.level = 1
        self.speed = 1.0
        self.current = None
        self.current_pos = None
    
    def rotate(self):
        """Rotate the current piece in CCW direction."""
        if self.current:
            self.current.rotate()
            # Ensure piece stays within grid
            shift = self.cols - (self.current_pos[1] + self.current.width())
            if shift < 0:
                self.current_pos[1] += shift
    
    def left(self):
        if self.current_pos:
            self.current_pos[1] = max(0, self.current_pos[1] - 1)

    def right(self):
        if self.current:
            self.current_pos[1] = min(self.cols - self.current.width(), self.current_pos[1] + 1)

    def down(self):
        if self.current:
            while not self.is_blocked():
                self.current_pos[0] += 1
    
    def current_coords(self):
        result = []
        if not self.current:
            return result
        for coords in self.current.coords:
            r = coords[0] + self.current_pos[0]
            c = coords[1] + self.current_pos[1]
            result.append([r, c])
        return result

    
    def step(self):
        if not self.current:
            # Create new piece
            # TODO random shape
            self.current = Piece([[0, 0], [1, 0], [1, 1], [2, 0]], random.choice([Cell.RED, Cell.BLUE, Cell.GREEN]))
            self.current_pos = [0, (self.cols - self.current.width()) // 2]
        elif self.is_blocked():
            self.anchor_piece()
            self.clear_full_rows()
        else:
            self.current_pos[0] += 1
    
    def anchor_piece(self):
        for r, c in self.current_coords():
            self.grid[r][c] = self.current.color
        self.current = None
        self.current_pos = None

    def is_blocked(self):
        if self.current:
            for r, c in self.current_coords():
                if r+1 == self.rows:
                    return True
                if self.grid[r+1][c] != Cell.EMPTY:
                    return True
        return False
        
    def is_full_row(self, row):
        for cell in row:
            if cell == Cell.EMPTY:
                return False
        return True

    def clear_full_row(self):
        for index, row in enumerate(self.grid):
            if self.is_full_row(row):
                self.grid.pop(index)
                self.grid.insert(0, [Cell.EMPTY] * self.cols)
                return True
        return False
    
    def clear_full_rows(self):
        while self.clear_full_row():
            pass
