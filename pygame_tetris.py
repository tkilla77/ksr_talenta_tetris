import pygame
from tetris import *

def to_pg_color(cell):
    return pygame.Color(cell.name.lower()) if cell != Color.EMPTY else pygame.Color('black')


class TetrisGrid(pygame.sprite.Sprite):
    """A sprite for the main grid."""
    def __init__(self, rows, cols, cell_size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([cols*cell_size, rows*cell_size])
        self.rect = self.image.get_rect()
        self.cell_size = cell_size
        self.layer = 0
    
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

class Tetromino(pygame.sprite.Sprite):
    """A sprite for the currently active piece."""
    def __init__(self, cell_size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([4*cell_size, 4*cell_size]).convert_alpha()
        self.rect = self.image.get_rect()
        self.cell_size = cell_size
        self.layer = 1

    def cell2rect(self, row, col):
        return (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)

    def update(self, tetris):
        if tetris.current:
            self.image.fill((0, 0, 0, 0))
            for r, c in tetris.current.coords:
                color = to_pg_color(tetris.current.color)
                pygame.draw.rect(self.image, color, self.cell2rect(r, c))

class TetrisGameArea(pygame.sprite.Group):
    """A custom sprite group for the grid and current tetromino."""
    def __init__(self, tetris, cell_size):
        pygame.sprite.Group.__init__(self)
        self.grid = TetrisGrid(tetris.rows, tetris.cols, cell_size)
        self.tetris = tetris
        self.cell_size = cell_size
        self.tetromino = Tetromino(cell_size)
        self.add(self.grid)
        self.add(self.tetromino)

    def draw(self, surface: pygame.Surface, bgd=None, special_flags=0):
        surface.blit(self.grid.image)
        if self.tetris.current:                
            dest = (self.tetris.current_pos[1]*self.cell_size, self.tetris.current_pos[0]*self.cell_size)
            surface.blit(self.tetromino.image, dest=dest)
    
class TetrisPygame:
    """A pygame based renderer for a tetris game."""
    def __init__(self, tetris, cell_size=30):
        pygame.init()
        self.tetris = tetris
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tetris")

        self.sprites = TetrisGameArea(tetris, cell_size)

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

            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    tetris = Tetris(20, 10)
    game = TetrisPygame(tetris)
    game.run()
