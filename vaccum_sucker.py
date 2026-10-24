import random
import sys
import pygame
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 10
MINES_COUNT = 10
TILE_SIZE = WIDTH // GRID_SIZE
BG_COLOR = (192, 192, 192)
LINE_COLOR = (128, 128, 128)
COVERED_COLOR = (160, 160, 160)
UNCOVERED_COLOR = (220, 220, 220)
TEXT_COLORS = {
    1: (0, 0, 255),
    2: (0, 128, 0),
    3: (255, 0, 0),
    4: (0, 0, 128),
    5: (128, 0, 0),
    6: (0, 128, 128),
    7: (0, 0, 0),
    8: (128, 128, 128),
}
class Cell:
  def __init__(self, row, col):
    self.row = row
    self.col = col
    self.is_mine = False
    self.is_covered = True
    self.is_flagged = False
    self.neighbor_mines = 0
class MinesweeperGame:
  def __init__(self):
    pygame.init()
    self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("vaccum sucker by me")
    self.clock = pygame.time.Clock()
    self.font = pygame.font.SysFont("Arial", 28, bold=True)
    self.game_over = False
    self.win = False
    self.reset_game()
  def reset_game(self):
    self.grid = [
        [Cell(r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)
    ]
    self.game_over = False
    self.win = False
    self.place_mines()
    self.calculate_neighbors()
  def place_mines(self):
    placed = 0
    while placed < MINES_COUNT:
      r = random.randint(0, GRID_SIZE - 1)
      c = random.randint(0, GRID_SIZE - 1)
      if not self.grid[r][c].is_mine:
        self.grid[r][c].is_mine = True
        placed += 1
  def calculate_neighbors(self):
    for r in range(GRID_SIZE):
      for c in range(GRID_SIZE):
        if self.grid[r][c].is_mine:
          continue
        count = 0
        for dr in [-1, 0, 1]:
          for dc in [-1, 0, 1]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
              if self.grid[nr][nc].is_mine:
                count += 1
        self.grid[r][c].neighbor_mines = count
  def reveal_cell(self, r, c):
    cell = self.grid[r][c]
    if not cell.is_covered or cell.is_flagged:
      return
    cell.is_covered = False
    if cell.is_mine:
      self.game_over = True
      return
    if cell.neighbor_mines == 0:
      for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
          nr, nc = r + dr, c + dc
          if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
            if self.grid[nr][nc].is_covered:
              self.reveal_cell(nr, nc)
  def check_win(self):
    for r in range(GRID_SIZE):
      for c in range(GRID_SIZE):
        cell = self.grid[r][c]
        if not cell.is_mine and cell.is_covered:
          return False
    return True
  def draw(self):
    self.screen.fill(BG_COLOR)

    for r in range(GRID_SIZE):
      for c in range(GRID_SIZE):
        cell = self.grid[r][c]
        rect = pygame.Rect(
            c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE - 1, TILE_SIZE - 1
        )
        if cell.is_covered:
          pygame.draw.rect(self.screen, COVERED_COLOR, rect)
          if cell.is_flagged:
            pygame.draw.circle(
                self.screen,
                (255, 0, 0),
                rect.center,
                TILE_SIZE // 4,
            )
        else:
          pygame.draw.rect(self.screen, UNCOVERED_COLOR, rect)
          if cell.is_mine:
            pygame.draw.circle(
                self.screen, (0, 0, 0), rect.center, TILE_SIZE // 3
            )
          elif cell.neighbor_mines > 0:
            text_surf = self.font.render(
                str(cell.neighbor_mines),
                True,
                TEXT_COLORS.get(cell.neighbor_mines, (0, 0, 0)),
            )
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)
        pygame.draw.rect(self.screen, LINE_COLOR, rect, 1)
    pygame.display.flip()
  def run(self):
    running = True
    while running:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
          mx, my = pygame.mouse.get_pos()
          c = mx // TILE_SIZE
          r = my // TILE_SIZE
          if event.button == 1: 
            self.reveal_cell(r, c)
            if self.check_win():
              self.win = True
              self.game_over = True
          elif event.button == 3:  
            cell = self.grid[r][c]
            if cell.is_covered:
              cell.is_flagged = not cell.is_flagged
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_r:  
            self.reset_game()
      self.draw()
      self.clock.tick(30)
    pygame.quit()
    sys.exit()
if __name__ == "__main__":
  game = MinesweeperGame()
  game.run()