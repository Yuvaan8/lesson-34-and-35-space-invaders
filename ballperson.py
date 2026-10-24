import pygame
import sys
import random
pygame.init()
TILE_SIZE = 24
FPS = 10
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
LEVEL_MAP = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.#  #.#   #.##.#   #.#  #.#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##    ##    ##.#     ",
    "######.## ######## ##.######",
    "..........   ##   ..........",
    "######.## ######## ##.######",
    "     #.##    ##    ##.#     ",
    "     #.##### ## #####.#     ",
    "######.##### ## #####.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#...##................##...#",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################"
]
MAP_WIDTH = len(LEVEL_MAP[0])
MAP_HEIGHT = len(LEVEL_MAP)
SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE
SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pacman by this guy again")
clock = pygame.time.Clock()
font = pygame.font.SysFont("freesansbold.ttf", 30)
class Game:
    def __init__(self):
        self.grid = [list(row) for row in LEVEL_MAP]
        self.score = 0
        self.game_over = False
        self.game_won = False
        self.pacman_x, self.pacman_y = 1, 1
        self.pacman_dx, self.pacman_dy = 0, 0       
        self.ghost_x, self.ghost_y = 13, 11
        self.ghost_dx, self.ghost_dy = 0, -1       
        self.total_pellets = sum(row.count('.') for row in LEVEL_MAP)
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()               
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.pacman_dx, self.pacman_dy = -1, 0
        elif keys[pygame.K_RIGHT]:
            self.pacman_dx, self.pacman_dy = 1, 0
        elif keys[pygame.K_UP]:
            self.pacman_dx, self.pacman_dy = 0, -1
        elif keys[pygame.K_DOWN]:
            self.pacman_dx, self.pacman_dy = 0, 1
    def update(self):
        if self.game_over or self.game_won:
            return
        next_px = self.pacman_x + self.pacman_dx
        next_py = self.pacman_y + self.pacman_dy       
        if 0 <= next_px < MAP_WIDTH and 0 <= next_py < MAP_HEIGHT:
            if self.grid[next_py][next_px] != '#':
                self.pacman_x = next_px
                self.pacman_y = next_py
        if self.grid[self.pacman_y][self.pacman_x] == '.':
            self.grid[self.pacman_y][self.pacman_x] = ' '
            self.score += 10
            self.total_pellets -= 1
            if self.total_pellets == 0:
                self.game_won = True
        possible_dirs = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            gx = self.ghost_x + dx
            gy = self.ghost_y + dy
            if 0 <= gx < MAP_WIDTH and 0 <= gy < MAP_HEIGHT:
                if self.grid[gy][gx] != '#':
                    if (dx, dy) != (-self.ghost_dx, -self.ghost_dy) or len(possible_dirs) == 0:
                        possible_dirs.append((dx, dy))             
        if possible_dirs:
            self.ghost_dx, self.ghost_dy = random.choice(possible_dirs)            
        self.ghost_x += self.ghost_dx
        self.ghost_y += self.ghost_dy
        if self.pacman_x == self.ghost_x and self.pacman_y == self.ghost_y:
            self.game_over = True
    def draw(self):
        screen.fill(BLACK)  
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE       
                if tile == '#':
                    pygame.draw.rect(screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
                elif tile == '.':
                    pygame.draw.circle(screen, WHITE, (x + TILE_SIZE//2, y + TILE_SIZE//2), 4)                
        px = self.pacman_x * TILE_SIZE + TILE_SIZE//2
        py = self.pacman_y * TILE_SIZE + TILE_SIZE//2
        pygame.draw.circle(screen, YELLOW, (px, py), TILE_SIZE//2 - 2)    
        gx = self.ghost_x * TILE_SIZE + TILE_SIZE//2
        gy = self.ghost_y * TILE_SIZE + TILE_SIZE//2
        pygame.draw.circle(screen, RED, (gx, gy), TILE_SIZE//2 - 2)   
        score_text = font.render(f"SCORE: {self.score}", True, WHITE)
        screen.blit(score_text, (15, 10))     
        if self.game_over:
            end_text = font.render("GAME OVER! Press Esc", True, RED)
            screen.blit(end_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        elif self.game_won:
            end_text = font.render("YOU WIN! Press Esc", True, YELLOW)
            screen.blit(end_text, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2))         
        pygame.display.flip()
def main():
    game = Game()
    while True:
        game.handle_input()      
        if game.game_over or game.game_won:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                game = Game()
        else:
            game.update() 
        game.draw()
        clock.tick(FPS)
if __name__ == "__main__":
    main()
