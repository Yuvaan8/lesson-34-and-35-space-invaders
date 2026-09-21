import math
import random
import pygame
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 800
PLAYER_START_X = 220    
PLAYER_START_Y = 700  
ENEMY_START_Y_MIN = 50
ENEMY_START_Y_MAX = 150
ENEMY_SPEED_X = 4
ENEMY_SPEED_Y = 40
BULLET_SPEED = 10
COLLISION_DISTANCE = 27
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Space Invaders')
background = pygame.image.load('bg.png')
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)
playerimage = pygame.image.load('player.png')
playerX = PLAYER_START_X
playerY = PLAYER_START_Y
playerX_change = 0
enemyimage = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_enemies = 6
for i in range(num_enemies):
    enemyimage.append(pygame.image.load('enemy.png'))
    enemyX.append(random.randint(0, SCREEN_WIDTH - 64))
    enemyY.append(random.randint(ENEMY_START_Y_MIN, ENEMY_START_Y_MAX))
    enemyX_change.append(ENEMY_SPEED_X)
    enemyY_change.append(ENEMY_SPEED_Y)
bulletimage = pygame.image.load('bullet.png')
bulletX = 0
bulletY = PLAYER_START_Y
bulletX_change = 0
bulletY_change = BULLET_SPEED
bullet_state = 'ready'
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
    screen.blit(over_text, (75, 350))
def player(x, y):
    screen.blit(playerimage, (x, y))
def enemy(x, y, i):
    screen.blit(enemyimage[i], (x, y))
def fire_bullet(x, y):
    global bullet_state
    bullet_state = 'fire'
    screen.blit(bulletimage, (x + 16, y + 10))
def IsCollison(enX, enY, bulX, bulY):
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
                playerX_change = -5
            if event.key == pygame.K_RIGHT:
                playerX_change = 5
            if event.key == pygame.K_SPACE and bullet_state == 'ready':
                bulletX = playerX
                fire_bullet(bulletX, bulletY)          
        if event.type == pygame.KEYUP and event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
            playerX_change = 0
    if not is_game_over:
        playerX += playerX_change
        playerX = max(0, min(playerX, SCREEN_WIDTH - 64))
        for i in range(num_enemies):
            if enemyY[i] > (playerY - 40):
                for j in range(num_enemies):
                    enemyY[j] = 2000  
                is_game_over = True
                break
            enemyX[i] += enemyX_change[i]
            if enemyX[i] <= 0:
                enemyX_change[i] = ENEMY_SPEED_X
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= SCREEN_WIDTH - 64:
                enemyX_change[i] = -ENEMY_SPEED_X
                enemyY[i] += enemyY_change[i]
            if IsCollison(enemyX[i], enemyY[i], bulletX, bulletY) and bullet_state == 'fire':
                bulletY = playerY
                bullet_state = 'ready'
                score_value += 1 
                enemyX[i] = random.randint(0, SCREEN_WIDTH - 64)
                enemyY[i] = random.randint(ENEMY_START_Y_MIN, ENEMY_START_Y_MAX)           
            enemy(enemyX[i], enemyY[i], i)
        if bullet_state == 'fire':
            fire_bullet(bulletX, bulletY)
            bulletY -= bulletY_change
        if bulletY <= 0:
            bulletY = playerY
            bullet_state = 'ready'
        player(playerX, playerY)
    else :
        game_over_text()
    show_score(fontX, fontY)
    pygame.display.update()
    clock.tick(60)
pygame.quit()