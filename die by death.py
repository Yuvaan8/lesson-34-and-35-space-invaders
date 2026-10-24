import pygame
import math
pygame.init()
pygame.font.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TARGET_FPS = 60
ICE_LEVELS = {7, 16, 19, 20}
GRAVITY_LEVELS = {11, 17, 18}
BLACK = (18, 18, 18)
WHITE = (255, 255, 255)
BLUE = (0, 116, 217)
RED = (255, 65, 54)
GROUND_COLOR = (45, 45, 45)
YELLOW = (255, 220, 0)
CYAN = (0, 192, 255)
PURPLE = (155, 89, 182)
GREEN = (46, 204, 113)
class Player:
    def __init__(self):
        self.size = 32
        self.x = 100.0
        self.y = 500.0
        self.rect = pygame.Rect(int(self.x), int(self.y), self.size, self.size)
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 400.0
        self.acceleration = 14.0
        self.friction = 12.0
        self.gravity = 1800.0
        self.jump_force = -760.0
        self.min_jump_force = -320.0
        self.is_grounded = False
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0

    def reset(self, start_x=100.0, start_y=500.0):
        self.x = start_x
        self.y = start_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0

    def handle_input(self, dt, level):
        keys = pygame.key.get_pressed()
        target_vx = 0.0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target_vx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target_vx = self.speed

        accel_rate = 3.5 if level in ICE_LEVELS else self.acceleration
        fric_rate = 2.5 if level in ICE_LEVELS else self.friction

        smoothing = 1.0 - math.exp(-accel_rate * dt)
        slowing = 1.0 - math.exp(-fric_rate * dt)
        if target_vx != 0.0:
            self.vx += (target_vx - self.vx) * smoothing
        else:
            self.vx += (0.0 - self.vx) * slowing

        if keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]:
            self.jump_buffer_timer = 0.18

        if self.is_grounded:
            self.coyote_timer = 0.13

        if level not in GRAVITY_LEVELS:
            if self.vy < self.min_jump_force and not (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]):
                self.vy = self.min_jump_force
        elif level in GRAVITY_LEVELS:
            if self.vy > -self.min_jump_force and not (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]):
                self.vy = -self.min_jump_force

    def update(self, dt, platforms, hazards, level, reset_x, reset_y, pushable_blocks=None):
        pushable_blocks = pushable_blocks or []
        self.coyote_timer -= dt
        self.jump_buffer_timer -= dt

        grav_modifier = -1.0 if level in GRAVITY_LEVELS else 1.0
        self.vy += self.gravity * dt * grav_modifier

        if abs(self.vy) > 1200.0:
            self.vy = 1200.0 * (1.0 if self.vy > 0 else -1.0)

        actual_jump_force = -self.jump_force if level in GRAVITY_LEVELS else self.jump_force
        if self.jump_buffer_timer > 0.0 and self.coyote_timer > 0.0:
            self.vy = actual_jump_force
            self.jump_buffer_timer = 0.0
            self.coyote_timer = 0.0
            self.is_grounded = False
        previous_x = self.rect.x
        self.x += self.vx * dt
        self.rect.x = int(self.x)
        horizontal_movement = self.rect.x - previous_x
        if horizontal_movement != 0:
            for block in pushable_blocks:
                if self.rect.colliderect(block):
                    next_block_position = block.move(horizontal_movement, 0)
                    other_blocks = [other for other in pushable_blocks if other is not block]
                    if (
                        next_block_position.left >= 0
                        and next_block_position.right <= SCREEN_WIDTH
                        and not any(next_block_position.colliderect(plat) for plat in platforms)
                        and not any(next_block_position.colliderect(other) for other in other_blocks)
                    ):
                        block.x = next_block_position.x

        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vx > 0:
                    self.rect.right = plat.left
                    self.x = float(self.rect.x)
                    self.vx = 0
                elif self.vx < 0:
                    self.rect.left = plat.right
                    self.x = float(self.rect.x)
                    self.vx = 0
        for block in pushable_blocks:
            if self.rect.colliderect(block):
                if self.vx > 0:
                    self.rect.right = block.left
                    self.x = float(self.rect.x)
                    self.vx = 0
                elif self.vx < 0:
                    self.rect.left = block.right
                    self.x = float(self.rect.x)
                    self.vx = 0

        self.y += self.vy * dt
        self.rect.y = int(self.y)
        self.is_grounded = False
        collision_platforms = platforms + pushable_blocks
        for plat in collision_platforms:
            if self.rect.colliderect(plat):
                if level not in GRAVITY_LEVELS:
                    if self.vy > 0:
                        self.rect.bottom = plat.top
                        self.y = float(self.rect.y)
                        self.vy = 0
                        self.is_grounded = True
                    elif self.vy < 0:
                        self.rect.top = plat.bottom
                        self.y = float(self.rect.y)
                        self.vy = 0
                else:
                    if self.vy < 0:
                        self.rect.top = plat.bottom
                        self.y = float(self.rect.y)
                        self.vy = 0
                        self.is_grounded = True
                    elif self.vy > 0:
                        self.rect.bottom = plat.top
                        self.y = float(self.rect.y)
                        self.vy = 0

        if self.rect.left < 0:
            self.rect.left = 0
            self.x = float(self.rect.x)
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.x = float(self.rect.x)

       
        if (
            (level not in GRAVITY_LEVELS and self.rect.top > SCREEN_HEIGHT)
            or (level in GRAVITY_LEVELS and self.rect.bottom < 0)
        ):
            self.reset(reset_x, reset_y)
            return True

        
        for hazard in hazards:
            if self.rect.colliderect(hazard):
                self.reset(reset_x, reset_y)
                return True
                
        return False

def generate_level(level_num):
    
    layouts = {
        1: (
            [(100, 450, 160, 20), (320, 360, 160, 20), (540, 270, 160, 20),
             (350, 160, 130, 20)],
            [], (400, 110),
        ),
        2: (
            [(70, 470, 130, 20), (240, 390, 130, 20), (430, 310, 130, 20),
             (600, 230, 120, 20), (390, 150, 150, 20)],
            [(390, 430, 35, 20)], (450, 100),
        ),
        3: (
            [(90, 470, 100, 20), (220, 395, 100, 20), (350, 320, 100, 20),
             (480, 245, 100, 20), (600, 170, 100, 20)],
            [(320, 455, 35, 20), (450, 380, 35, 20)], (635, 115),
        ),
        4: (
            [(150, 470, 150, 20), (360, 400, 150, 20), (540, 460, 150, 20),
             (600, 350, 130, 20), (420, 270, 140, 20), (210, 195, 140, 20),
             (350, 120, 150, 20)],
            [], (405, 65),
        ),
        5: (
            [(60, 475, 100, 20), (250, 400, 100, 20), (470, 325, 100, 20),
             (250, 250, 100, 20), (470, 175, 100, 20)],
            [(175, 430, 35, 20), (390, 355, 35, 20), (355, 205, 35, 20)],
            (505, 120),
        ),
        6: (
            [(80, 480, 200, 20), (300, 410, 200, 20), (520, 340, 200, 20),
             (300, 270, 200, 20), (80, 200, 220, 20), (300, 130, 220, 20)],
            [], (390, 80),
        ),
        7: (
            [(50, 460, 120, 20), (250, 380, 100, 20), (500, 300, 100, 20),
             (280, 210, 120, 20)],
            [], (325, 140),
        ),
        8: (
            [(70, 465, 160, 20), (300, 410, 160, 20), (530, 350, 160, 20),
             (350, 285, 160, 20), (100, 220, 160, 20), (330, 155, 160, 20)],
            [(240, 445, 35, 20), (470, 385, 35, 20), (275, 260, 35, 20)],
            (395, 100),
        ),
        9: (
            [(100, 470, 120, 20), (430, 430, 120, 20), (220, 350, 120, 20),
             (540, 300, 120, 20), (330, 220, 120, 20), (100, 145, 120, 20)],
            [], (145, 90),
        ),
        10: (
            [(80, 475, 160, 20), (300, 440, 160, 20), (520, 380, 160, 20),
             (400, 310, 160, 20), (180, 250, 160, 20), (330, 185, 160, 20),
             (540, 120, 160, 20)],
            [(250, 410, 35, 20), (500, 350, 35, 20)], (600, 65),
        ),
        11: (
            [(150, 150, 140, 20), (350, 260, 140, 20), (550, 370, 140, 20),
             (380, 450, 80, 20)],
            [(300, 335, 35, 20)], (405, 500),
        ),
        12: (
            [(60, 470, 180, 20), (300, 420, 180, 20), (540, 360, 180, 20),
             (330, 300, 180, 20), (70, 240, 180, 20), (300, 180, 180, 20),
             (540, 120, 180, 20)],
            [(250, 445, 30, 20), (500, 390, 30, 20), (250, 270, 30, 20)],
            (610, 65),
        ),
        13: (
            [(110, 470, 130, 20), (300, 405, 200, 20), (550, 340, 130, 20),
             (370, 275, 130, 20), (130, 210, 130, 20), (330, 145, 200, 20)],
            [(250, 445, 30, 20), (510, 315, 30, 20)], (415, 90),
        ),
        14: (
            [(100, 480, 150, 20), (320, 400, 160, 20), (540, 320, 160, 20)],
            [], (600, 270),
        ),
        15: (
            [(80, 470, 155, 20), (300, 410, 155, 20), (520, 350, 155, 20),
             (360, 285, 155, 20), (120, 220, 155, 20), (350, 155, 155, 20),
             (590, 100, 155, 20)],
            [(250, 440, 35, 20), (460, 320, 35, 20), (270, 190, 35, 20)],
            (640, 45),
        ),
        16: (
            [(70, 475, 150, 20), (265, 405, 150, 20), (475, 335, 150, 20),
             (260, 265, 150, 20), (480, 195, 150, 20), (315, 125, 170, 20)],
            [(440, 375, 35, 20)], (385, 75),
        ),
        17: (
            [(150, 115, 170, 20), (390, 195, 170, 20), (570, 285, 150, 20),
             (350, 365, 170, 20), (110, 435, 170, 20)],
            [(310, 320, 35, 20)], (175, 475),
        ),
        18: (
            [(80, 120, 170, 20), (300, 205, 170, 20), (535, 290, 170, 20),
             (310, 375, 170, 20), (500, 455, 170, 20)],
            [(260, 170, 35, 20), (490, 340, 35, 20)], (560, 510),
        ),
        19: (
            [(55, 475, 170, 20), (290, 410, 170, 20), (535, 345, 170, 20),
             (330, 280, 170, 20), (85, 215, 170, 20), (335, 150, 170, 20)],
            [(465, 375, 35, 20)], (405, 100),
        ),
        20: (
            [(70, 475, 120, 20), (270, 415, 90, 20), (480, 350, 90, 20),
             (625, 280, 90, 20), (420, 220, 95, 20), (190, 165, 100, 20)],
            [(405, 382, 24, 14), (310, 192, 24, 14)], (150, 130),
        ),
    }

    route, hazard_rects, goal_position = layouts[level_num]
    if level_num in GRAVITY_LEVELS:
        platforms = [pygame.Rect(0, 0, SCREEN_WIDTH, 40)]
        start_x, start_y = 60.0, 60.0
    else:
        platforms = [pygame.Rect(0, 560, SCREEN_WIDTH, 40)]
        start_x, start_y = 60.0, 500.0

    platforms.extend(
        pygame.Rect(x, y, min(width + 24, SCREEN_WIDTH - x), height)
        for x, y, width, height in route
    )
    hazards = [pygame.Rect(*hazard) for hazard in hazard_rects]
    goal_spike = pygame.Rect(*goal_position, 30, 30)
    pushable_blocks = []
    block_targets = []
    spike_box = []
    if level_num == 14:
        pushable_blocks = [pygame.Rect(360, 368, 32, 32)]
        block_targets = [pygame.Rect(445, 394, 32, 6)]
        spike_box = [
            pygame.Rect(590, 240, 90, 10),
            pygame.Rect(590, 240, 10, 80),
            pygame.Rect(670, 240, 10, 80),
        ]
        goal_spike.topleft = (620, 290)
    elif level_num == 20:
        pushable_blocks = [pygame.Rect(78, 443, 32, 32)]
        block_targets = [pygame.Rect(150, 469, 32, 6)]
        spike_box = [
            pygame.Rect(125, 100, 80, 10),
            pygame.Rect(125, 100, 10, 75),
            pygame.Rect(195, 100, 10, 75),
            pygame.Rect(125, 165, 80, 10),
        ]

    return start_x, start_y, platforms, hazards, goal_spike, pushable_blocks, block_targets, spike_box

def draw_spike(surface, color, rect, inverted=False):
    
    if not inverted:
        p1 = (rect.left, rect.bottom)
        p2 = (rect.right, rect.bottom)
        p3 = (rect.centerx, rect.top)
    else:
        p1 = (rect.left, rect.top)
        p2 = (rect.right, rect.top)
        p3 = (rect.centerx, rect.bottom)
    pygame.draw.polygon(surface, color, [p1, p2, p3])

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Die by death by once more ME!")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 22)

    player = Player()
    current_level = 1
    max_levels = 20
    skip_button = pygame.Rect(SCREEN_WIDTH - 120, 16, 100, 38)

    start_x, start_y, platforms, hazards, goal_spike, pushable_blocks, block_targets, spike_box = generate_level(current_level)
    player.reset(start_x, start_y)
    spike_box_open = False

    running = True
    while running:
        dt = clock.tick(TARGET_FPS) / 1000.0
        if dt > 0.1: 
            dt = 0.1 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: 
                    player.reset(start_x, start_y)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if skip_button.collidepoint(event.pos):
                    current_level = current_level % max_levels + 1
                    start_x, start_y, platforms, hazards, goal_spike, pushable_blocks, block_targets, spike_box = generate_level(current_level)
                    player.reset(start_x, start_y)
                    spike_box_open = False

        # Updates
        player.handle_input(dt, current_level)
        all_blocks_on_targets = bool(pushable_blocks) and all(
            block.colliderect(target)
            for block, target in zip(pushable_blocks, block_targets)
        )
        if current_level == 14:
            spike_box_open = spike_box_open or all_blocks_on_targets
        else:
            spike_box_open = all_blocks_on_targets
        block_puzzle_solved = not pushable_blocks or spike_box_open
        collision_platforms = platforms + (spike_box if not block_puzzle_solved else [])
        player.update(dt, collision_platforms, hazards, current_level, start_x, start_y, pushable_blocks)

        # Reaching the Spike Goal moves player forward to the next map!
        if block_puzzle_solved and player.rect.colliderect(goal_spike):
            current_level += 1
            if current_level > max_levels:
                current_level = 1 
            start_x, start_y, platforms, hazards, goal_spike, pushable_blocks, block_targets, spike_box = generate_level(current_level)
            player.reset(start_x, start_y)
            spike_box_open = False
        screen.fill(BLACK)
        for plat in platforms:
            pygame.draw.rect(screen, GROUND_COLOR, plat)

        for haz in hazards:
            pygame.draw.rect(screen, RED, haz)

        
        for block, target in zip(pushable_blocks, block_targets):
            target_color = GREEN if block.colliderect(target) else YELLOW
            pygame.draw.rect(screen, target_color, target, border_radius=2)
            pygame.draw.rect(screen, target_color, target, 3, border_radius=4)
            pygame.draw.rect(screen, (160, 160, 160), block, border_radius=3)
        if pushable_blocks and not block_puzzle_solved:
            for box_piece in spike_box:
                pygame.draw.rect(screen, (120, 120, 120), box_piece)
        if block_puzzle_solved:
            draw_spike(screen, RED, goal_spike, inverted=(current_level in GRAVITY_LEVELS))
        player_color = CYAN if current_level in GRAVITY_LEVELS else (PURPLE if current_level in ICE_LEVELS else BLUE)
        pygame.draw.rect(screen, player_color, player.rect)

      
        lvl_text = font.render(f"Level: {current_level} / {max_levels}", True, WHITE)
        screen.blit(lvl_text, (20, 20))
        gimmick_str = "Parkour Target: Die by death!"
        if current_level in ICE_LEVELS:
            gimmick_str = "Ice traction: Die by Ice!"
        elif current_level in GRAVITY_LEVELS:
            gimmick_str = "Gravity inverted: Die by Physics!!"
        elif current_level in {14, 20}:
            gimmick_str = "Die by Weight!"
        elif current_level >= 11:
            gimmick_str = "Die by Death again!"
        gimmick_text = font.render(gimmick_str, True, YELLOW)
        screen.blit(gimmick_text, (20, 50))

        button_color = (70, 130, 180) if skip_button.collidepoint(pygame.mouse.get_pos()) else BLUE
        pygame.draw.rect(screen, button_color, skip_button, border_radius=6)
        skip_text = font.render("Skip Level", True, WHITE)
        screen.blit(skip_text, skip_text.get_rect(center=skip_button.center))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()