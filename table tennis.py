import pygame
import sys
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Table Tennis by this guy for the other time")
clock = pygame.time.Clock()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 15
paddle_a = pygame.Rect(50, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle_b = pygame.Rect(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
paddle_speed = 6
ball_speed_x = 5
ball_speed_y = 5
score_a = 0
score_b = 0
font = pygame.font.SysFont("Courier", 36)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and paddle_a.top > 0:
        paddle_a.y -= paddle_speed
    if keys[pygame.K_s] and paddle_a.bottom < SCREEN_HEIGHT:
        paddle_a.y += paddle_speed
    if keys[pygame.K_UP] and paddle_b.top > 0:
        paddle_b.y -= paddle_speed
    if keys[pygame.K_DOWN] and paddle_b.bottom < SCREEN_HEIGHT:
        paddle_b.y += paddle_speed
    ball.x += ball_speed_x
    ball.y += ball_speed_y
    if ball.top <= 0:
        ball.top = 0
        ball_speed_y *= -1
    if ball.bottom >= SCREEN_HEIGHT:
        ball.bottom = SCREEN_HEIGHT
        ball_speed_y *= -1
    if ball.colliderect(paddle_a) and ball_speed_x < 0:
        ball.left = paddle_a.right
        ball_speed_x *= -1
    if ball.colliderect(paddle_b) and ball_speed_x > 0:
        ball.right = paddle_b.left
        ball_speed_x *= -1
    if ball.left <= 0:
        score_b += 1
        ball.x = SCREEN_WIDTH // 2 - BALL_SIZE // 2
        ball.y = SCREEN_HEIGHT // 2 - BALL_SIZE // 2
        ball_speed_x *= -1
    if ball.right >= SCREEN_WIDTH:
        score_a += 1
        ball.x = SCREEN_WIDTH // 2 - BALL_SIZE // 2
        ball.y = SCREEN_HEIGHT // 2 - BALL_SIZE // 2
        ball_speed_x *= -1
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, paddle_a)
    pygame.draw.rect(screen, WHITE, paddle_b)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
    score_text = font.render(f"{score_a}   {score_b}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 20))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()
