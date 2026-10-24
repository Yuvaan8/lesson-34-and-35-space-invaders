import pygame
import random
import sys
pygame.init()
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 20
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Anacondas by me again")
clock = pygame.time.Clock()
def game_loop():
    snake_body = [[SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]]
    dir_x, dir_y = GRID_SIZE, 0
    food_x = random.randint(0, (SCREEN_WIDTH - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
    food_y = random.randint(0, (SCREEN_HEIGHT - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
    score = 0
    game_over = False
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and dir_y == 0:
                    dir_x, dir_y = 0, -GRID_SIZE
                elif event.key == pygame.K_DOWN and dir_y == 0:
                    dir_x, dir_y = 0, GRID_SIZE
                elif event.key == pygame.K_LEFT and dir_x == 0:
                    dir_x, dir_y = -GRID_SIZE, 0
                elif event.key == pygame.K_RIGHT and dir_x == 0:
                    dir_x, dir_y = GRID_SIZE, 0
        new_head = [snake_body[0][0] + dir_x, snake_body[0][1] + dir_y]
        snake_body.insert(0, new_head)
        if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or
            new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT or
            new_head in snake_body[1:]):
            game_over = True
            continue
        if new_head[0] == food_x and new_head[1] == food_y:
            score += 1
            food_x = random.randint(0, (SCREEN_WIDTH - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
            food_y = random.randint(0, (SCREEN_HEIGHT - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
        else:
            snake_body.pop()
        screen.fill(COLOR_BLACK)
        for segment in snake_body:
            pygame.draw.rect(screen, COLOR_GREEN, pygame.Rect(segment[0], segment[1], GRID_SIZE - 2, GRID_SIZE - 2))
        pygame.draw.rect(screen, COLOR_RED, pygame.Rect(food_x, food_y, GRID_SIZE - 2, GRID_SIZE - 2))   
        font = pygame.font.SysFont(None, 35)
        score_surface = font.render(f"Score: {score}", True, COLOR_WHITE)
        screen.blit(score_surface, (10, 10))
        pygame.display.update()
        clock.tick(10)
    screen.fill(COLOR_BLACK)
    font = pygame.font.SysFont(None, 50)
    game_over_surface = font.render(f"Game Over! Final Score: {score}", True, COLOR_RED)
    screen.blit(game_over_surface, (SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2.5))
    pygame.display.update()
    pygame.time.wait(2000)
while True:
    game_loop()
