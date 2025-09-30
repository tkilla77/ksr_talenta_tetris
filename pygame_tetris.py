import pygame
from tetris import *

class TetrisPygame:
    def __init__(self, rows=20, cols=10, cell_size=30):
        pygame.init()
        self.cell_size = cell_size
        self.width = cols * cell_size
        self.height = rows * cell_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.tetris = Tetris(rows, cols)
    
    def color(self, cell):
        return pygame.Color(cell.name.lower()) if cell != Color.EMPTY else pygame.Color('black')

    def draw_grid(self):
        for r in range(self.tetris.rows):
            for c in range(self.tetris.cols):
                cell = self.tetris.grid[r][c]
                color = self.color(cell)
                pygame.draw.rect(
                    self.screen,
                    color,
                    (c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size),
                    0
                )
                pygame.draw.rect(
                    self.screen,
                    pygame.Color('grey'),
                    (c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size),
                    1
                )

    def draw_piece(self):
        if self.tetris.current:
            for r, c in self.tetris.current_coords():
                color = self.color(self.tetris.current.color)
                pygame.draw.rect(
                    self.screen,
                    color,
                    (c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size),
                    0
                )

    def run(self):
        running = True
        while running:
            self.clock.tick(3)
            self.tetris.step()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.tetris.left()
                    elif event.key == pygame.K_RIGHT:
                        self.tetris.right()
                    elif event.key == pygame.K_DOWN:
                        self.tetris.down()
                    elif event.key == pygame.K_UP:
                        self.tetris.rotate()
            self.screen.fill((0, 0, 0))
            self.draw_grid()
            self.draw_piece()
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    game = TetrisPygame()
    game.run()




