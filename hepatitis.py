import pygame
import random
pygame.init()
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700
GRID_SIZE = 30
COLUMNS = 10
ROWS = 15
BOARD_WIDTH = COLUMNS * GRID_SIZE
BOARD_HEIGHT = ROWS * GRID_SIZE
SIDEBAR_WIDTH = SCREEN_WIDTH - BOARD_WIDTH
BLACK = (21, 21, 21)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (180, 180, 180)
SHAPE_COLORS = [
    (0, 255, 255),
    (255, 255, 0),
    (128, 0, 128),
    (0, 255, 0),
    (255, 0, 0),
    (0, 0, 255),
    (255, 165, 0)
]
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]]
]
class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0
class Tetris:
    def __init__(self):
        self.grid = [[(0,0,0) for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_speed = 500
        self.game_over = False
        self.current_piece = self.new_piece()
    def new_piece(self):
        return Piece(COLUMNS // 2 - 1, 0, random.choice(SHAPES))
    def rotate_shape(self, shape):
        return [list(x) for x in zip(*shape[::-1])]
    def valid_space(self, piece, adj_x=0, adj_y=0, new_shape=None):
        shape = new_shape if new_shape else piece.shape
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    next_x = piece.x + c + adj_x
                    next_y = piece.y + r + adj_y                   
                    if next_x < 0 or next_x >= COLUMNS or next_y >= ROWS:
                        return False
                    if next_y >= 0 and self.grid[next_y][next_x] != (0,0,0):
                        return False
        return True
    def lock_piece(self):
        for r, row in enumerate(self.current_piece.shape):
            for c, val in enumerate(row):
                if val:
                    self.grid[self.current_piece.y + r][self.current_piece.x + c] = self.current_piece.color      
        self.clear_lines()
        self.current_piece = self.new_piece()    
        if not self.valid_space(self.current_piece):
            self.game_over = True
    def clear_lines(self):
        lines_to_clear = []
        for r in range(ROWS):
            if (0,0,0) not in self.grid[r]:
                lines_to_clear.append(r)              
        for r in lines_to_clear:
            del self.grid[r]
            self.grid.insert(0, [(0,0,0) for _ in range(COLUMNS)])            
        if len(lines_to_clear) > 0:
            self.lines_cleared += len(lines_to_clear)
            points = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += points.get(len(lines_to_clear), 800) * self.level           
            new_level = (self.lines_cleared // 5) + 1
            if new_level > self.level:
                self.level = new_level
                self.fall_speed = max(50, int(500 * (0.85 ** (self.level - 1))))
    def draw(self, surface):
        for r in range(ROWS):
            for c in range(COLUMNS):
                pygame.draw.rect(surface, self.grid[r][c], (c * GRID_SIZE, r * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
                pygame.draw.rect(surface, GRAY, (c * GRID_SIZE, r * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
        if self.current_piece:
            for r, row in enumerate(self.current_piece.shape):
                for c, val in enumerate(row):
                    if val:
                        pygame.draw.rect(surface, self.current_piece.color, ((self.current_piece.x + c) * GRID_SIZE, (self.current_piece.y + r) * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
        pygame.draw.line(surface, WHITE, (BOARD_WIDTH, 0), (BOARD_WIDTH, BOARD_HEIGHT), 2)
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("hepatitis by this guy for idk smth straight?")
    clock = pygame.time.Clock()
    game = Tetris()  
    font = pygame.font.SysFont("Arial", 22)
    large_font = pygame.font.SysFont("Arial", 40) 
    last_fall_time = pygame.time.get_ticks()
    running = True
    while running:
        current_time = pygame.time.get_ticks()     
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
               running = False              
            if event.type == pygame.KEYDOWN and not game.game_over:
                if event.key == pygame.K_LEFT:
                    if game.valid_space(game.current_piece, adj_x=-1):
                        game.current_piece.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if game.valid_space(game.current_piece, adj_x=1):
                        game.current_piece.x += 1
                elif event.key == pygame.K_DOWN:
                    if game.valid_space(game.current_piece, adj_y=1):
                        game.current_piece.y += 1
                elif event.key == pygame.K_UP:
                    rotated = game.rotate_shape(game.current_piece.shape)
                    if game.valid_space(game.current_piece, new_shape=rotated):
                        game.current_piece.shape = rotated
                elif event.key == pygame.K_SPACE:
                    while game.valid_space(game.current_piece, adj_y=1):
                        game.current_piece.y += 1
                    game.lock_piece()           
            if event.type == pygame.KEYDOWN and game.game_over:
                if event.key == pygame.K_r:
                    game = Tetris()
                    last_fall_time = pygame.time.get_ticks()
        if not game.game_over:
            if current_time - last_fall_time > game.fall_speed:
                if game.valid_space(game.current_piece, adj_y=1):
                    game.current_piece.y += 1
                else:
                    game.lock_piece()
                last_fall_time = current_time
        screen.fill(BLACK)
        game.draw(screen)  
        sidebar_x = BOARD_WIDTH + 15     
        score_lbl = font.render("Score:", True, LIGHT_GRAY)
        score_val = font.render(f"{game.score}", True, WHITE)
        level_lbl = font.render("Level:", True, LIGHT_GRAY)
        level_val = font.render(f"{game.level}", True, WHITE)
        lines_lbl = font.render("Lines:", True, LIGHT_GRAY)
        lines_val = font.render(f"{game.lines_cleared}", True, WHITE)   
        screen.blit(score_lbl, (sidebar_x, 30))
        screen.blit(score_val, (sidebar_x, 55))
        screen.blit(level_lbl, (sidebar_x, 110))
        screen.blit(level_val, (sidebar_x, 135))
        screen.blit(lines_lbl, (sidebar_x, 190))
        screen.blit(lines_val, (sidebar_x, 215))       
        if game.game_over:
            go_text = large_font.render("GAME OVER", True, (255, 50, 50))
            restart_text = font.render("Press 'R' to Restart", True, WHITE) 
            screen.blit(go_text, (BOARD_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(restart_text, (BOARD_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        pygame.display.update()
        clock.tick(60)
    pygame.quit()
if __name__ == "__main__":
    main()
