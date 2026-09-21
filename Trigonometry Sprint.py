import pygame
import random
import sys
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)
RED = (255, 80, 80)
GREEN = (46, 204, 113)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Trigonometry Sprint")
clock = pygame.time.Clock()
class Player:
    def __init__(self):
        self.size = 40
        self.x = 100
        self.y = SCREEN_HEIGHT - self.size - 50
        self.vel_y = 0
        self.gravity = 0.8
        self.jump_power = -16
        self.is_grounded = True
    def jump(self):
        if self.is_grounded:
            self.vel_y = self.jump_power
            self.is_grounded = False
    def update(self, platforms):
        self.vel_y += self.gravity
        self.y += self.vel_y
        player_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.is_grounded = False
        floor_y = SCREEN_HEIGHT - 50
        if self.y + self.size >= floor_y:
            self.y = floor_y - self.size
            self.vel_y = 0
            self.is_grounded = True
        for plat in platforms:
            plat_rect = pygame.Rect(plat.x, plat.y, plat.width, plat.height)
            if player_rect.colliderect(plat_rect):
                if self.vel_y > 0 and (self.y + self.size - self.vel_y) <= plat.y + 10:
                    self.y = plat.y - self.size
                    self.vel_y = 0
                    self.is_grounded = True
    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.size, self.size))
class Obstacle:
    def __init__(self, x, type="spike"):
        self.type = type 
        self.x = x
        self.speed = 6
        if self.type == "spike":
            self.width = 30
            self.height = 40
            self.y = SCREEN_HEIGHT - 50 - self.height
        elif self.type == "block":
            self.width = 80
            self.height = 30
            self.y = SCREEN_HEIGHT - 50 - 120 
    def update(self):
        self.x -= self.speed
    def draw(self):
        if self.type == "spike":
            points = [
                (self.x, self.y + self.height), 
                (self.x + self.width, self.y + self.height),  
                (self.x + self.width // 2, self.y)  
            ]
            pygame.draw.polygon(screen, RED, points)
        elif self.type == "block":
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
def main():
    player = Player()
    obstacles = []
    spawn_timer = 0
    score = 0
    font = pygame.font.SysFont("Arial", 30)
    running = True
    while running:
        clock.tick(FPS)
        screen.fill(WHITE)
        pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    player.jump()
        spawn_timer += 1
        if spawn_timer > random.randint(70, 120):
            obs_type = random.choice(["spike", "block"])
            obstacles.append(Obstacle(SCREEN_WIDTH, type=obs_type))
            spawn_timer = 0
        platforms = [obs for obs in obstacles if obs.type == "block"]
        player.update(platforms)
        for obs in obstacles[:]:
            obs.update()
            obs.draw()
            if player.update: 
                player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
                if obs.type == "spike" and player_rect.colliderect(obs.get_rect()):
                    running = False 
                elif obs.type == "block" and player_rect.colliderect(obs.get_rect()):
                    if player.x + player.size - 6 > obs.x and player.y + player.size > obs.y + 5:
                        running = False
            if obs.x + obs.width < 0:
                obstacles.remove(obs)
                score += 1
        player.draw()
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (20, 20))
        pygame.display.flip()
    screen.fill(BLACK)
    game_over_text = font.render(f"GAME OVER! Score: {score}", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 20))
    pygame.display.flip()
    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()