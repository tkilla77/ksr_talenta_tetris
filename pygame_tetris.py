import pygame
from tetris import *

def to_pg_color(cell):
    return pygame.Color(cell.name.lower()) if cell != Color.EMPTY else pygame.Color('black')


class TetrisGrid(pygame.sprite.Sprite):
    def __init__(self, rows, cols, cell_size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([cols*cell_size, rows*cell_size])
        self.rect = self.image.get_rect()
        self.cell_size = cell_size
    
    def cell2rect(self, row, col):
        return (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)

    def update(self, tetris):
        for r in range(tetris.rows):
            for c in range(tetris.cols):
                cell = tetris.grid[r][c]
                color = to_pg_color(cell)
                # Draw cell and grey frame
                pygame.draw.rect(self.image, color, self.cell2rect(r, c))
                pygame.draw.rect(self.image, pygame.Color('grey'), self.cell2rect(r, c), 1)




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

        self.grid = TetrisGrid(tetris.rows, tetris.cols, cell_size)
        self.sprites = pygame.sprite.Group()
        self.sprites.add(self.grid)

        self.clock = pygame.time.Clock()

        pygame.mixer.init()
        self.sound_shift = pygame.mixer.Sound('sounds/rotate.wav')
        self.sound_drop = pygame.mixer.Sound('sounds/drop.wav')
        self.sound_cleared = pygame.mixer.Sound('sounds/cleared.wav')
        self.sound_ended = pygame.mixer.Sound('sounds/ended.wav')
        self.sound_step = pygame.mixer.Sound('sounds/step.wav')
        self.sound_rotate = pygame.mixer.Sound('sounds/shift.wav')
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
    
    def cell2rect(self, row, col):
        return (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)

    def draw_grid(self):
        for r in range(self.tetris.rows):
            for c in range(self.tetris.cols):
                cell = self.tetris.grid[r][c]
                color = self.color(cell)
                # Draw cell and grey frame
                pygame.draw.rect(self.screen, color, self.cell2rect(r, c))
                pygame.draw.rect(self.screen, pygame.Color('grey'), self.cell2rect(r, c), 1)

    def draw_piece(self):
        if self.tetris.current:
            for r, c in self.tetris.current_coords():
                color = to_pg_color(self.tetris.current.color)
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
            
            self.sprites.update(self.tetris)

            self.screen.fill((0, 0, 0))
            self.sprites.draw(self.screen)

            self.draw_piece()
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    tetris = Tetris(20, 10)
    game = TetrisPygame(tetris)
    game.run()
