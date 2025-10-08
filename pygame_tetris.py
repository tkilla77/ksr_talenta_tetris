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
    """A sprite for a Tetris piece."""
    def __init__(self, cell_size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([4*cell_size, 4*cell_size]).convert_alpha()
        self.rect = self.image.get_rect()
        self.cell_size = cell_size
        self.layer = 1

    def cell2rect(self, row, col):
        return (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)
    
    def update(self, piece):
        if piece:
            self.image.fill((0, 0, 0, 0))  # fill with transparency
            for r, c in piece.coords:
                color = to_pg_color(piece.color)
                pygame.draw.rect(self.image, color, self.cell2rect(r, c))

class TetrisGameArea(pygame.sprite.Group):
    """A custom sprite group for the grid and current tetromino."""
    def __init__(self, tetris, cell_size):
        pygame.sprite.Group.__init__(self)
        self.cell_size = cell_size
        self.grid = TetrisGrid(tetris.rows, tetris.cols, cell_size)
        self.tetromino = Tetromino(cell_size)
        self.destination = None
        self.add(self.grid)
        self.add(self.tetromino)
    
    def rect(self):
        return self.grid.rect
    
    def update(self, tetris):
        self.grid.update(tetris)
        self.tetromino.update(tetris.current)
        if tetris.current:
            self.destination = (tetris.current_pos[1]*self.cell_size, tetris.current_pos[0]*self.cell_size)
        else:
            self.destination = None

    def draw(self, surface: pygame.Surface, bgd=None, special_flags=0):
        surface.blit(self.grid.image)
        if self.destination:
            surface.blit(self.tetromino.image, dest=self.destination)

class NextPieceSprite(pygame.sprite.Sprite):
    def __init__(self, cell_size):
        super().__init__()
        self.cell_size = cell_size
        self.font = pygame.font.SysFont("", 70)
        self.caption = self.font.render('Next', True, pygame.Color("yellow"))
        self.caption_rect = self.caption.get_rect()
        # Create a Tetromino sprite for the preview
        self.tetromino_sprite = Tetromino(cell_size)
        # Set up the image size to fit caption and tetromino
        height = self.caption_rect.height + 4 * cell_size
        self.image = pygame.Surface([4 * cell_size, height], pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self, next_piece):
        self.image.fill((0, 0, 0, 0))
        self.image.blit(self.caption, (0, 0))
        if next_piece:
            # Update the Tetromino sprite with the next piece
            self.tetromino_sprite.update(next_piece)
            # Draw the Tetromino sprite below the caption
            self.image.blit(
                self.tetromino_sprite.image,
                (0, self.caption_rect.height)
            )

class ScoreSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.font_caption = pygame.font.SysFont("", 70)
        self.font_score = pygame.font.SysFont("", 100)
        self.image = pygame.Surface((220, 140), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.score = 0

    def update(self, score):
        self.score = score
        self.image.fill((0, 0, 0, 0))
        caption = self.font_caption.render('Score', True, pygame.Color("yellow"))
        score_surface = self.font_score.render(f'{round(score)}', True, pygame.Color("yellow"))
        self.image.blit(caption, (0, 0))
        self.image.blit(score_surface, (0, caption.get_height()))

class SpeedSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.font_caption = pygame.font.SysFont("", 70)
        self.font_speed = pygame.font.SysFont("", 100)
        self.image = pygame.Surface((220, 140), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.speed = 1.0

    def update(self, speed):
        self.speed = speed
        self.image.fill((0, 0, 0, 0))
        caption = self.font_caption.render('Speed', True, pygame.Color("yellow"))
        speed_surface = self.font_speed.render(f'{speed:.1f}', True, pygame.Color("yellow"))
        self.image.blit(caption, (0, 0))
        self.image.blit(speed_surface, (0, caption.get_height()))

class InfoPanel(pygame.sprite.Group):
    """Sprite group for next piece, score, and speed."""
    def __init__(self, cell_size):
        super().__init__()
        self.next_piece_sprite = NextPieceSprite(cell_size)
        self.score_sprite = ScoreSprite()
        self.speed_sprite = SpeedSprite()
        self.add(self.next_piece_sprite, self.score_sprite, self.speed_sprite)

    def update(self, tetris):
        self.next_piece_sprite.update(tetris.next)
        self.score_sprite.update(tetris.score)
        self.speed_sprite.update(tetris.speed)

    def draw(self, surface, topleft):
        # Stack sprites vertically
        y = topleft[1]
        for sprite in self.sprites():
            sprite.rect.topleft = (topleft[0], y)
            surface.blit(sprite.image, sprite.rect)
            y += sprite.rect.height + 10

class TetrisSounds():
    def __init__(self, tetris):
        pygame.mixer.init()
        self.sound_shift = pygame.mixer.Sound('sounds/rotate.wav')
        self.sound_drop = pygame.mixer.Sound('sounds/drop.wav')
        self.sound_cleared = pygame.mixer.Sound('sounds/cleared.wav')
        self.sound_ended = pygame.mixer.Sound('sounds/ended.wav')
        self.sound_step = pygame.mixer.Sound('sounds/step.wav')
        self.sound_rotate = pygame.mixer.Sound('sounds/shift.wav')
        self.sound_shift_blocked = pygame.mixer.Sound('sounds/shift_blocked.wav')

        tetris.add_listener(self)

    def rotated(self):
        self.sound_rotate.play()
    def rotate_blocked(self):
        self.sound_shift_blocked.play()
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
    
class TetrisPygame:
    """A pygame based renderer for a tetris game."""
    def __init__(self, tetris, cell_size=30):
        pygame.init()
        self.tetris = tetris
        screen_sizes = pygame.display.get_desktop_sizes()
        initial_size = screen_sizes[0] if screen_sizes else (1024, 768)
        self.screen = pygame.display.set_mode(initial_size, flags=pygame.RESIZABLE)
        pygame.display.set_caption("Tetris")

        self.game_area = TetrisGameArea(tetris, cell_size)
        self.info_panel = InfoPanel(cell_size)
        self.sounds = TetrisSounds(tetris)
        self.clock = pygame.time.Clock()
   
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.tetris.left()
                elif event.key == pygame.K_RIGHT:
                    self.tetris.right()
                elif event.key == pygame.K_DOWN:
                    self.tetris.down()
                elif event.key == pygame.K_UP:
                    self.tetris.rotate()
                elif event.key == pygame.K_f:
                    pygame.display.toggle_fullscreen()
        return True

    def run(self):
        running = True
        step_time = 0
        while running:
            step_time += self.clock.tick(40)
            if step_time > 1000 / self.tetris.speed:
                self.tetris.step()
                step_time = 0
            
            running = self.handle_events()

            self.game_area.update(self.tetris)
            self.info_panel.update(self.tetris)

            self.screen.fill((0, 0, 0))
            screen_rect = self.screen.get_rect()
            game_rect = self.game_area.rect().copy()
            game_rect.center = screen_rect.center
            game_surface = self.screen.subsurface(game_rect)
            self.game_area.draw(game_surface)

            # Draw info panel to the right of the game area
            info_x = game_rect.right + 50
            info_y = game_rect.top
            self.info_panel.draw(self.screen, (info_x, info_y))

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    tetris = Tetris(22, 10)
    game = TetrisPygame(tetris)
    game.run()
