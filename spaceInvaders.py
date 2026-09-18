import math
import random
import pygame

# Constants
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 800
PLAYER_START_X = 220  # Adjusted so player starts in the center of a 500px wide screen
PLAYER_START_Y = 700  # Adjusted so player starts at the bottom of an 800px high screen
ENEMY_START_Y_MIN = 50
ENEMY_START_Y_MAX = 150
ENEMY_SPEED_X = 4
ENEMY_SPEED_Y = 40
BULLET_SPEED = 10
COLLISION_DISTANCE = 27

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Space Invaders')

# --- Assets ---
# Note: Ensure these images exist in your project folder, or use placeholders
try:
    background = pygame.image.load('bg.png')
    icon = pygame.image.load('ufo.png')
    pygame.display.set_icon(icon)
    playerimage = pygame.image.load('player.png')
    bulletimage = pygame.image.load('bullet.png')
    enemy_img_asset = pygame.image.load('enemy.png')
except pygame.error:
    # Fallback to colored surfaces if images are missing so the code still runs
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    playerimage = pygame.Surface((64, 64)); playerimage.fill((0, 255, 0))
    bulletimage = pygame.Surface((16, 16)); bulletimage.fill((255, 255, 0))
    enemy_img_asset = pygame.Surface((64, 64)); enemy_img_asset.fill((255, 0, 0))

# Player Setup
playerX = PLAYER_START_X
playerY = PLAYER_START_Y
playerX_change = 0

# Enemy Setup
enemyimage = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_enemies = 6

for i in range(num_enemies):
    enemyimage.append(enemy_img_asset)
    enemyX.append(random.randint(0, SCREEN_WIDTH - 64))
    enemyY.append(random.randint(ENEMY_START_Y_MIN, ENEMY_START_Y_MAX))
    enemyX_change.append(ENEMY_SPEED_X)
    enemyY_change.append(ENEMY_SPEED_Y)

# Bullet Setup
bulletX = 0
bulletY = PLAYER_START_Y
bullet_state = 'ready'

# Score & Text Setup
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
fontX = 10
fontY = 10
over_font = pygame.font.Font('freesansbold.ttf', 64)
game_over = False

def show_score(x, y):
    score = font.render('Score: ' + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))

def game_over_text():
    over_text = over_font.render('GAME OVER', True, (255, 255, 255))
    # Centers the text on our 500px wide screen
    screen.blit(over_text, (65, 350))

def player(x, y):
    screen.blit(playerimage, (x, y))

def enemy(img, x, y):
    screen.blit(img, (x, y))

def fire_bullet(x, y):
    global bullet_state
    bullet_state = 'fire'
    screen.blit(bulletimage, (x + 16, y + 10))

def is_collision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt((enemyX - bulletX) ** 2 + (enemyY - bulletY) ** 2)
    return distance < COLLISION_DISTANCE

# Clock to control frame rate
clock = pygame.time.Clock()

# --- Game Loop ---
running = True
while running:
    # Frame rate lock (60 FPS)
    clock.tick(60)
    
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -5
            if event.key == pygame.K_RIGHT:
                playerX_change = 5
            if event.key == pygame.K_SPACE:
                if bullet_state == 'ready' and not game_over:
                    bulletX = playerX
                    fire_bullet(bulletX, bulletY)
                    
        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                playerX_change = 0

    if not game_over:
        # Player Movement & Boundaries
        playerX += playerX_change
        if playerX <= 0:
            playerX = 0
        elif playerX >= SCREEN_WIDTH - 64:
            playerX = SCREEN_WIDTH - 64

        # Enemy Movement & Logic
        for i in range(num_enemies):
            # Game Over Condition (Enemy reaches player depth)
            if enemyY[i] > 640:
                for j in range(num_enemies):
                    enemyY[j] = 2000  # Move all enemies off-screen
                game_over = True
                break

            enemyX[i] += enemyX_change[i]
            
            # Enemy boundary bouncing
            if enemyX[i] <= 0:
                enemyX_change[i] = ENEMY_SPEED_X
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= SCREEN_WIDTH - 64:
                enemyX_change[i] = -ENEMY_SPEED_X
                enemyY[i] += enemyY_change[i]

            # Collision Check
            if is_collision(enemyX[i], enemyY[i], bulletX, bulletY) and bullet_state == 'fire':
                bulletY = PLAYER_START_Y
                bullet_state = 'ready'
                score_value += 1
                enemyX[i] = random.randint(0, SCREEN_WIDTH - 64)
                enemyY[i] = random.randint(ENEMY_START_Y_MIN, ENEMY_START_Y_MAX)

            enemy(enemyimage[i], enemyX[i], enemyY[i])

        # Bullet Movement
        if bullet_state == 'fire':
            fire_bullet(bulletX, bulletY)
            bulletY -= BULLET_SPEED
            
        if bulletY <= 0:
            bulletY = PLAYER_START_Y
            bullet_state = 'ready'

        player(playerX, playerY)
    else:
        game_over_text()

    show_score(fontX, fontY)
    pygame.display.update()

pygame.quit()