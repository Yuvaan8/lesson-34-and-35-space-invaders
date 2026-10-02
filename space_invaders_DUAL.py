import math
import random
import pygame
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 800
ENEMY_START_Y_MIN = 50
ENEMY_START_Y_MAX = 150
ENEMY_SPEED_X = 4
ENEMY_SPEED_Y = 40
BULLET_SPEED = 10
COLLISION_DISTANCE = 27
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Space Invaders - 2 Player Edition')
background = pygame.image.load('bg.png')
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)
player1_img = pygame.image.load('player.png')
player1_X = 220
player1_Y = 700
player1_X_change = 0
bullet1_img = pygame.image.load('bullet.png')
bullet1_X = 0
bullet1_Y = 700
bullet1_state = 'ready'
player2_img = pygame.image.load('player2.png')
player2_X = 520
player2_Y = 700
player2_X_change = 0
bullet2_img = pygame.image.load('bullet2.png')
bullet2_X = 0
bullet2_Y = 700
bullet2_state = 'ready'
num_enemies = 7
enemyimage = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
for i in range(num_enemies):
    enemyimage.append(pygame.image.load('enemy.png'))
    enemyX.append(random.randint(0, SCREEN_WIDTH - 64))
    enemyY.append(random.randint(ENEMY_START_Y_MIN, ENEMY_START_Y_MAX))
    enemyX_change.append(ENEMY_SPEED_X)
    enemyY_change.append(ENEMY_SPEED_Y)
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
fontX = 10
fontY = 10
over_font = pygame.font.Font('freesansbold.ttf', 64)
is_game_over = False
def show_score(x, y):
    score = font.render('Score: ' + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))
def game_over_text():
    over_text = over_font.render('GAME OVER', True, (255, 255, 255))
    screen.blit(over_text, (200, 350))
def draw_player(img, x, y):
    screen.blit(img, (x, y))
def draw_enemy(x, y, i):
    screen.blit(enemyimage[i], (x, y))
def fire_bullet1(x, y):
    global bullet1_state
    bullet1_state = 'fire'
    screen.blit(bullet1_img, (x + 16, y + 10))
def fire_bullet2(x, y):
    global bullet2_state
    bullet2_state = 'fire'
    screen.blit(bullet2_img, (x + 16, y + 10))
def IsCollision(enX, enY, bulX, bulY):
    distance = math.sqrt((enX - bulX) ** 2 + (enY - bulY) ** 2)
    return distance < COLLISION_DISTANCE
clock = pygame.time.Clock()
running = True
while running:
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player1_X_change = -5
            if event.key == pygame.K_RIGHT:
                player1_X_change = 5
            if event.key == pygame.K_SPACE and bullet1_state == 'ready':
                bullet1_X = player1_X
                fire_bullet1(bullet1_X, bullet1_Y)
            if event.key == pygame.K_a:
                player2_X_change = -5
            if event.key == pygame.K_d:
                player2_X_change = 5
            if event.key == pygame.K_w and bullet2_state == 'ready':
                bullet2_X = player2_X
                fire_bullet2(bullet2_X, bullet2_Y)
        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                player1_X_change = 0
            if event.key in [pygame.K_a, pygame.K_d]:
                player2_X_change = 0
    if not is_game_over:
        player1_X += player1_X_change
        player1_X = max(0, min(player1_X, SCREEN_WIDTH - 64))
        player2_X += player2_X_change
        player2_X = max(0, min(player2_X, SCREEN_WIDTH - 64))
        for i in range(num_enemies):
            if enemyY[i] > 640:
                is_game_over = True
                break
            enemyX[i] += enemyX_change[i]
            if enemyX[i] <= 0:
                enemyX_change[i] = ENEMY_SPEED_X
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= SCREEN_WIDTH - 64:
                enemyX_change[i] = -ENEMY_SPEED_X
                enemyY[i] += enemyY_change[i]
            if bullet1_state == 'fire' and IsCollision(enemyX[i], enemyY[i], bullet1_X, bullet1_Y):
                bullet1_Y = 700
                bullet1_state = 'ready'
                score_value += 1
                enemyX[i] = random.randint(0, SCREEN_WIDTH - 64)
                enemyY[i] = random.randint(ENEMY_START_Y_MIN, ENEMY_START_Y_MAX)
            if bullet2_state == 'fire' and IsCollision(enemyX[i], enemyY[i], bullet2_X, bullet2_Y):
                bullet2_Y = 700
                bullet2_state = 'ready'
                score_value += 1
                enemyX[i] = random.randint(0, SCREEN_WIDTH - 64)
                enemyY[i] = random.randint(ENEMY_START_Y_MIN, ENEMY_START_Y_MAX)
            draw_enemy(enemyX[i], enemyY[i], i)
        if bullet1_state == 'fire':
            fire_bullet1(bullet1_X, bullet1_Y)
            bullet1_Y -= BULLET_SPEED
        if bullet1_Y <= 0:
            bullet1_Y = 700
            bullet1_state = 'ready'
        if bullet2_state == 'fire':
            fire_bullet2(bullet2_X, bullet2_Y)
            bullet2_Y -= BULLET_SPEED
        if bullet2_Y <= 0:
            bullet2_Y = 700
            bullet2_state = 'ready'
        draw_player(player1_img, player1_X, player1_Y)
        draw_player(player2_img, player2_X, player2_Y)
        show_score(fontX, fontY)
    else:
        game_over_text()
    pygame.display.update()
    clock.tick(60)
pygame.quit()