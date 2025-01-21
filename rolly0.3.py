import pygame
import sys
from pygame.locals import QUIT, KEYDOWN, K_RETURN
import time
import math

# Initialize Pygame
pygame.init()

# Screen dimensions and colors
WIDTH, HEIGHT = 800, 800
BACKGROUND_COLOR = (0, 0, 100)  # Dark blue background
FPS = 60

# Colors
RED = (255, 0, 0)
DARK_RED = (200, 0, 0)
DARKER_RED = (150, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 200)
DARKER_BLUE = (0, 0, 150)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

# Ball properties
BALL_RADIUS = 20
BALL_SPEED = 1
FRICTION = 0.98

# Platform position
PLATFORM_SIZE = 600
PLATFORM_X = (WIDTH - PLATFORM_SIZE) // 2
PLATFORM_Y = (HEIGHT - PLATFORM_SIZE) // 2

# Initialize screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rolly V0.3")
clock = pygame.time.Clock()

# Fonts
pygame.font.init()
title_font = pygame.font.Font(None, 150)  # Large font for the title
subtitle_font = pygame.font.Font(None, 50)  # Smaller font for the subtitle
score_font = pygame.font.Font(None, 40)  # Font for score-keeping

# Sounds (optional, placeholder if you have files)
pygame.mixer.init()
collision_sound = pygame.mixer.Sound("collision.wav")
rolling_sound = pygame.mixer.Sound("rolling.wav")
rolling_sound.set_volume(0)
rolling_channel = pygame.mixer.Channel(0)

# Ball setup
red_ball = {'x': PLATFORM_X + 150, 'y': PLATFORM_Y + 150, 'vx': 0, 'vy': 0, 'colors': [DARKER_RED, DARK_RED, RED]}
blue_ball = {'x': PLATFORM_X + 450, 'y': PLATFORM_Y + 450, 'vx': 0, 'vy': 0, 'colors': [DARKER_BLUE, DARK_BLUE, BLUE]}

# Score
score = {'red': 0, 'blue': 0}

def draw_text_with_outline(text, font, x, y, text_color, outline_color, center=False):
    """Draw text with a black outline."""
    text_surface = font.render(text, True, text_color)
    outline_surface = font.render(text, True, outline_color)

    text_rect = text_surface.get_rect()
    outline_rect = outline_surface.get_rect()
    if center:
        text_rect.center = (x, y)
        outline_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
        outline_rect.topleft = (x, y)

    screen.blit(outline_surface, (outline_rect.x - 2, outline_rect.y - 2))
    screen.blit(outline_surface, (outline_rect.x + 2, outline_rect.y - 2))
    screen.blit(outline_surface, (outline_rect.x - 2, outline_rect.y + 2))
    screen.blit(outline_surface, (outline_rect.x + 2, outline_rect.y + 2))
    screen.blit(text_surface, text_rect)

def draw_platform():
    """Draw the platform."""
    pygame.draw.rect(screen, GRAY, (PLATFORM_X, PLATFORM_Y, PLATFORM_SIZE, PLATFORM_SIZE))

def draw_ball(ball):
    """Draw a ball with a glossy reflective look."""
    x, y = int(ball['x']), int(ball['y'])
    pygame.draw.circle(screen, BLACK, (x, y), BALL_RADIUS + 3)  # Shadow
    for i, color in enumerate(ball['colors']):
        pygame.draw.circle(screen, color, (x, y), BALL_RADIUS - i * 5)
    pygame.draw.circle(screen, WHITE, (x - BALL_RADIUS // 3, y - BALL_RADIUS // 3), BALL_RADIUS // 4)  # Highlight

def draw_scores():
    """Draw the scores with a black outline."""
    draw_text_with_outline(f"Red: {score['red']}", score_font, 10, 10, RED, BLACK, center=False)
    draw_text_with_outline(f"Blue: {score['blue']}", score_font, WIDTH - 150, 10, BLUE, BLACK, center=False)

def move_ball(ball, keys, up, down, left, right):
    if keys[up]: ball['vy'] -= BALL_SPEED
    if keys[down]: ball['vy'] += BALL_SPEED
    if keys[left]: ball['vx'] -= BALL_SPEED
    if keys[right]: ball['vx'] += BALL_SPEED

def apply_physics(ball):
    ball['vx'] *= FRICTION
    ball['vy'] *= FRICTION
    ball['x'] += ball['vx']
    ball['y'] += ball['vy']

def handle_collision(ball1, ball2):
    dx = ball1['x'] - ball2['x']
    dy = ball1['y'] - ball2['y']
    dist = (dx**2 + dy**2)**0.5
    if dist < 2 * BALL_RADIUS:
        overlap = 2 * BALL_RADIUS - dist
        ball1['vx'] += dx * overlap * 0.05
        ball1['vy'] += dy * overlap * 0.05
        ball2['vx'] -= dx * overlap * 0.05
        ball2['vy'] -= dy * overlap * 0.05
        collision_sound.play()

def is_off_platform(ball):
    return (ball['x'] - BALL_RADIUS > PLATFORM_X + PLATFORM_SIZE or
            ball['x'] + BALL_RADIUS < PLATFORM_X or
            ball['y'] - BALL_RADIUS > PLATFORM_Y + PLATFORM_SIZE or
            ball['y'] + BALL_RADIUS < PLATFORM_Y)

def reset_balls():
    red_ball['x'], red_ball['y'] = PLATFORM_X + 150, PLATFORM_Y + 150
    red_ball['vx'], red_ball['vy'] = 0, 0
    blue_ball['x'], blue_ball['y'] = PLATFORM_X + 450, PLATFORM_Y + 450
    blue_ball['vx'], blue_ball['vy'] = 0, 0

def title_screen():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_RETURN:
                return

        screen.fill(BACKGROUND_COLOR)
        draw_text_with_outline("ROLLY", title_font, WIDTH // 2, HEIGHT // 3, RED, BLACK, center=True)
        draw_text_with_outline("Press Start to Play", subtitle_font, WIDTH // 2, HEIGHT // 2, BLUE, BLACK, center=True)
        pygame.display.flip()
        clock.tick(FPS)

def show_start_message():
    screen.fill(BACKGROUND_COLOR)
    draw_text_with_outline("Start!", title_font, WIDTH // 2, HEIGHT // 2, WHITE, BLACK, center=True)
    pygame.display.flip()
    time.sleep(1)

def main_game():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        move_ball(red_ball, keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)
        move_ball(blue_ball, keys, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)

        apply_physics(red_ball)
        apply_physics(blue_ball)
        handle_collision(red_ball, blue_ball)

        if is_off_platform(red_ball):
            score['blue'] += 1
            reset_balls()
        elif is_off_platform(blue_ball):
            score['red'] += 1
            reset_balls()

        screen.fill(BACKGROUND_COLOR)
        draw_platform()
        draw_ball(red_ball)
        draw_ball(blue_ball)
        draw_scores()
        pygame.display.flip()
        clock.tick(FPS)

# Run the game
title_screen()
show_start_message()
main_game()