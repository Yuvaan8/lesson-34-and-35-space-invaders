import math
import random
import pygame
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 500
PLAYER_START_X = 370
PLAYER_START_Y = 380
ENEMY_START_Y_MIN = 50
ENEMY_START_Y_MAX = 150
ENEMY_SPEED_X = 4
ENEMY_SPEED_Y = 40
BULLET_SPEED = 10
COLLISION_DISTANCE = 27
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background = pygame.image.load('bg.png')
pygame.display.set_caption('Space Invaders')
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
num_enemies = 8
for i in range(num_enemies):
    enemyimage.append(pygame.image.load('enemey.png'))
    enemyX.append(random.randint(0 - SCREEN_WIDTH - 64))
    enemyY.append(random.randint(ENEMY_START_Y_MAX, ENEMY_START_Y_MIN))
    enemyX.change.append(ENEMY_SPEED_X)
    enemyY.change.append(ENEMY_SPEED_Y)
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
def show_score(x, y):
    score = font.render('Score:' + str(score_value), True (255, 255, 255))
    screen.blit(score,(x, y))
def player(x, y):
    screen.blit(playerimage,(x, y))
def enemy(x, y):
    screen.blit(player.image(x, y))
def fire_bullet(x, y):
    global bullet_state
    bullet_state = 'fire'
    screen.blit(bulletimage(x + 16, y + 10))
def IsCollison(enemyX, enemyY,bulletX, bulletY):
    distance = math.sqrt((enemyX - bulletX) ** 2 + (enemyY - bulletY) ** 2)
    return distance < COLLISION_DISTANCE
