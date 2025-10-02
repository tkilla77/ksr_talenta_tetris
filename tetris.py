from enum import Enum
import random

class Color(Enum):
    EMPTY = 1
    RED = 2
    BLUE = 3
    GREEN = 4
    MAGENTA = 5
    YELLOW = 6
    CYAN = 7
    PINK = 8

class Piece:
    """A tetris piece with shape and color."""
    def __init__(self, coords, color):
        self.coords = coords
        self.color = color

    def width(self):
        """Returns the width of the piece in cells."""
        result = 0
        for c in self.coords:
            result = max(result, c[1] + 1)
        return result

    def height(self):
        """Returns the height of the piece in cells."""
        result = 0
        for c in self.coords:
            result = max(result, c[0] + 1)
        return result

    def rotate(self, turns=1):
        """Rotate CCW and ensure 0,0 is the upper left corner."""
        # Rotation matrix is [[0, -1], [1, 0]]
        for _ in range(turns):
            minx, miny = 0, 0
            for c in self.coords:
                c[0], c[1] = -c[1], c[0]
                minx = min(minx, c[0])
                miny = min(miny, c[1])
            for c in self.coords:
                c[0] -= minx
                c[1] -= miny

pieces = [
    Piece([[0, 0], [1, 0], [1, 1], [2, 0]], Color.GREEN),  # T
    Piece([[0, 0], [0, 1], [0, 2], [0, 3]], Color.RED),    # I
    Piece([[0, 0], [0, 1], [0, 2], [1, 2]], Color.BLUE),   # L
    Piece([[0, 0], [0, 1], [0, 2], [1, 0]], Color.YELLOW), # inversed L
    Piece([[0, 0], [0, 1], [1, 1], [1, 2]], Color.CYAN),  # S
    Piece([[1, 0], [1, 1], [0, 1], [0, 2]], Color.PINK),  # 2
    Piece([[0, 0], [0, 1], [1, 0], [1, 1]], Color.MAGENTA),# square
]
def random_piece():
    """Returns a random piece."""
    import copy
    return copy.deepcopy(random.choice(pieces))
    # return copy.deepcopy(pieces[1])  # for testing
    
class Tetris:
    """An abstract game of Tetris."""
    def __init__(self, rows=20, cols=10, speed=1.5, speedup=1.1):
        self.rows = rows
        self.cols = cols
        self.grid = [[Color.EMPTY] * cols for _ in range(rows)]
        self.speed = speed  # Game steps per second
        self.speedup = speedup
        self.score = 0
        """The currently active piece being dropped."""
        self.current = None
        """The upper-left coordinate [row, col] of the current piece being dropped."""
        self.current_pos = None
    
    def rotate(self):
        """Rotate the current piece in CCW direction."""
        if self.current:
            self.current.rotate()
            # Ensure piece stays within grid
            shift = self.cols - (self.current_pos[1] + self.current.width())
            if shift < 0:
                self.current_pos[1] += shift
            # TODO: undo block rotation if the result is illegal
    
    def left(self):
        """Shift the current piece to the left, if possible."""
        if self.current_pos:
            self.current_pos[1] = max(0, self.current_pos[1] - 1)
            if self.is_impossible():
                self.current_pos[1] += 1

    def right(self):
        """Shift the current piece to the right, if possible."""
        if self.current:
            self.current_pos[1] = min(self.cols - self.current.width(), self.current_pos[1] + 1)
            if self.is_impossible():
                self.current_pos[1] -= 1

    def down(self):
        """Shift the current piece down as far as possible."""
        if self.current:
            while not self.is_blocked():
                self.current_pos[0] += 1
    
    def current_coords(self):
        """Returns the coordinates [row, col] of all cells occupied by the current piece."""
        result = []
        if not self.current:
            return result
        for coords in self.current.coords:
            r = coords[0] + self.current_pos[0]
            c = coords[1] + self.current_pos[1]
            result.append([r, c])
        return result

    def step(self):
        """Modifies the state of the tetris game by dropping the current piece by one, or 
           spawning a fresh piece."""
        if not self.current:
            # Spawn a new piece
            self.current = random_piece()
            self.current_pos = [0, (self.cols - self.current.width()) // 2]
            if self.is_impossible():
                raise Exception(f"ended with highscore {self.score}")
        elif self.is_blocked():
            # Anchor the current piece and clear rows.
            self.anchor_piece()
            self.clear_full_rows()
        else:
            # Lower current piece by one.
            self.current_pos[0] += 1
    
    def anchor_piece(self):
        """Anchors the current piece in place by fixing the cells, and clears the current piece."""
        for r, c in self.current_coords():
            self.grid[r][c] = self.current.color
        self.current = None
        self.current_pos = None

    def is_impossible(self):
        """Returns True if the current piece position is illegal."""
        if self.current:
            for r, c in self.current_coords():
                if self.grid[r][c] != Color.EMPTY:
                    return True  # piece overlaps with an existing block.
        return False

    def is_blocked(self):
        """Returns True if the current piece cannot move downwards."""
        if self.current:
            for r, c in self.current_coords():
                if r+1 >= self.rows:
                    return True  # piece has reached bottom
                if self.grid[r][c] != Color.EMPTY:
                    return True  # piece overlaps with an existing block.
                if self.grid[r+1][c] != Color.EMPTY:
                    return True  # piece stands on a non-empty block.
        return False
        
    def is_full_row(self, row):
        """Returns True if a row is full, False otherwise."""
        for cell in row:
            if cell == Color.EMPTY:
                return False
        return True

    def is_cleared(self):
        """Returns True if a row is full, False otherwise."""
        for cell in self.grid[-1]:
            if cell != Color.EMPTY:
                return False
        return True

    def clear_full_row(self):
        """Clear a single full row or return False if no rows can be cleared."""
        for index, row in enumerate(self.grid):
            if self.is_full_row(row):
                self.grid.pop(index)
                self.grid.insert(0, [Color.EMPTY] * self.cols)
                self.speed *= self.speedup
                return True
        return False
    
    def clear_full_rows(self):
        """Clear all complete rows."""
        row_score = 0
        while self.clear_full_row():
            # Clearing multiple rows increases the jackpot...
            row_score = row_score * 2 + self.cols
        if row_score:
            if self.is_cleared():
                row_score += 100
            self.score += row_score
            print(f'+{row_score} => {self.score}')
