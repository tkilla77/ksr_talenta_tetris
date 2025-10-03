import pygame
from tetris import *


class TetrisPygame:
    """A pygame based renderer for a tetris game."""
    def __init__(self, tetris, cell_size=30):
        pygame.init()
        self.cell_size = cell_size
        self.tetris = tetris
        self.width = tetris.cols * cell_size
        self.height = tetris.rows * cell_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()

        pygame.mixer.init()
        self.sound_rotate = pygame.mixer.Sound('sounds/rotate.wav')
        self.sound_drop = pygame.mixer.Sound('sounds/drop.wav')
        self.sound_cleared = pygame.mixer.Sound('sounds/cleared.wav')
        self.sound_ended = pygame.mixer.Sound('sounds/ended.wav')
        self.sound_step = pygame.mixer.Sound('sounds/step.wav')
        self.sound_shift = pygame.mixer.Sound('sounds/shift.wav')
        self.sound_shift_blocked = pygame.mixer.Sound('sounds/shift_blocked.wav')


        tetris.add_listener(self)

    # Tetris Event listeners
    def rotated(self):
        self.sound_rotate.play()
    def shifted(self):
        self.sound_shift.play()
    def shift_blocked(self):
        self.sound_shift_blocked.play()
    def lowered(self):
        self.sound_drop.play()
    def ended(self, score):
        self.sound_ended.play()
    def spawned(self):
        self.sound_step.play()
    def anchored(self):
        pass
    def cleared(self, rows):
        self.sound_cleared.play()
    def stepped(self):
        self.sound_step.play()
    
    def color(self, cell):
        return pygame.Color(cell.name.lower()) if cell != Color.EMPTY else pygame.Color('black')
    
    def cell2rect(self, row, col):
        return (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)

    def draw_grid(self):
        for r in range(self.tetris.rows):
            for c in range(self.tetris.cols):
                cell = self.tetris.grid[r][c]
                color = self.color(cell)
                pygame.draw.rect(self.screen, color, self.cell2rect(r, c))
                pygame.draw.rect(self.screen, pygame.Color('grey'), self.cell2rect(r, c), 1)

    def draw_piece(self):
        if self.tetris.current:
            for r, c in self.tetris.current_coords():
                color = self.color(self.tetris.current.color)
                pygame.draw.rect(self.screen, color, self.cell2rect(r, c))

    def run(self):
        running = True
        step_time = 0
        while running:
            step_time += self.clock.tick(40)
            if step_time > 1000 / self.tetris.speed:
                self.tetris.step()
                step_time = 0

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
    tetris = Tetris(20, 10)
    game = TetrisPygame(tetris)
    game.run()
