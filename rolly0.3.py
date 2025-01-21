import pygame
import sys
from pygame.locals import QUIT, KEYDOWN, K_RETURN
import time
import math
import random

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

# Player 3 and 4 colors
ORANGE = (255, 165, 0)
DARK_ORANGE = (200, 130, 0)
DARKER_ORANGE = (150, 100, 0)
PLAYER_PURPLE = (180, 0, 255)  # Different from powerup purple
DARK_PLAYER_PURPLE = (140, 0, 200)
DARKER_PLAYER_PURPLE = (100, 0, 150)

# Powerup colors with light variants
YELLOW = (255, 255, 0)
LIGHT_YELLOW = (255, 255, 128)
DARKER_YELLOW = (200, 200, 0)
GREEN = (0, 255, 0)
LIGHT_GREEN = (128, 255, 128)
DARKER_GREEN = (0, 200, 0)
PURPLE = (255, 0, 255)
LIGHT_PURPLE = (255, 128, 255)
DARKER_PURPLE = (200, 0, 200)

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
subtitle_font = pygame.font.Font(None, 40)  # Smaller font for menu options (changed from 50)
score_font = pygame.font.Font(None, 40)  # Font for score-keeping

# Sounds (optional, placeholder if you have files)
pygame.mixer.init()
collision_sound = pygame.mixer.Sound("collision.wav")
rolling_sound = pygame.mixer.Sound("rolling.wav")
rolling_sound.set_volume(0)
rolling_channel = pygame.mixer.Channel(0)

# Ball setup
red_ball = {
    'x': PLATFORM_X + 150, 
    'y': PLATFORM_Y + 150, 
    'vx': 0, 
    'vy': 0, 
    'colors': [DARKER_RED, DARK_RED, RED],
    'radius': BALL_RADIUS,
    'powerup': None,
    'powerup_end': 0,
    'last_hit_by': None
}
blue_ball = {
    'x': PLATFORM_X + 450, 
    'y': PLATFORM_Y + 150, 
    'vx': 0, 
    'vy': 0, 
    'colors': [DARKER_BLUE, DARK_BLUE, BLUE],
    'radius': BALL_RADIUS,
    'powerup': None,
    'powerup_end': 0,
    'last_hit_by': None
}
orange_ball = {
    'x': PLATFORM_X + 150, 
    'y': PLATFORM_Y + 450, 
    'vx': 0, 
    'vy': 0, 
    'colors': [DARKER_ORANGE, DARK_ORANGE, ORANGE],
    'radius': BALL_RADIUS,
    'powerup': None,
    'powerup_end': 0,
    'last_hit_by': None
}
purple_ball = {
    'x': PLATFORM_X + 450, 
    'y': PLATFORM_Y + 450, 
    'vx': 0, 
    'vy': 0, 
    'colors': [DARKER_PLAYER_PURPLE, DARK_PLAYER_PURPLE, PLAYER_PURPLE],
    'radius': BALL_RADIUS,
    'powerup': None,
    'powerup_end': 0,
    'last_hit_by': None
}

# Score
score = {'red': 0, 'blue': 0, 'orange': 0, 'purple': 0}

# Powerup properties
POWERUP_SIZE = 20
POWERUP_SPAWN_INTERVAL = 15000  # Increased from 5000 to 15000 (15 seconds)
GROW_MULTIPLIER = 1.5
SHRINK_MULTIPLIER = 0.7

# Powerups
powerups = []
last_powerup_spawn = 0

# Add after other global variables
WIN_SCORES = [25, 50, 100]
selected_win_score = WIN_SCORES[0]  # Default to first option

# Add after WIN_SCORES
PLAYER_COUNTS = [2, 3, 4]
selected_player_count = PLAYER_COUNTS[0]  # Default to 2 players

# Add after PLAYER_COUNTS
PLATFORM_SIZES = [400, 600, 700]  # Small, Medium, Large (700 instead of 800)
selected_platform_size = PLATFORM_SIZES[1]  # Default to medium (600)

# Add after PLATFORM_SIZES
POWERUP_INTERVALS = [30000, 15000, 7500]  # Slow, Normal, Fast (in milliseconds)
selected_powerup_interval = POWERUP_INTERVALS[1]  # Default to normal speed

# Add after other powerup constants
POWERUP_DURATIONS = {
    'grow': 10000,    # 10 seconds
    'shrink': 7000,   # 7 seconds
    'shield': 5000    # 5 seconds
}

# Modify the platform position to be dynamic
def update_platform_position():
    """Update platform position and ball positions based on selected size"""
    global PLATFORM_X, PLATFORM_Y, PLATFORM_SIZE
    
    # Update platform position and size
    PLATFORM_SIZE = selected_platform_size
    PLATFORM_X = (WIDTH - PLATFORM_SIZE) // 2
    PLATFORM_Y = (HEIGHT - PLATFORM_SIZE) // 2
    
    # Update ball positions to match new platform size
    spawn_pos = get_spawn_positions()
    red_ball['x'], red_ball['y'] = spawn_pos['red']
    blue_ball['x'], blue_ball['y'] = spawn_pos['blue']
    orange_ball['x'], orange_ball['y'] = spawn_pos['orange']
    purple_ball['x'], purple_ball['y'] = spawn_pos['purple']

def get_spawn_positions():
    """Get spawn positions for balls based on platform size and player count"""
    margin = 80  # Distance from corner
    
    if selected_player_count == 2:
        # Diagonal corners for 2 players (top-left and bottom-right)
        return {
            'red': (PLATFORM_X + margin, PLATFORM_Y + margin),  # Top-left
            'blue': (PLATFORM_X + selected_platform_size - margin, PLATFORM_Y + selected_platform_size - margin),  # Bottom-right
            'orange': (PLATFORM_X + margin, PLATFORM_Y + selected_platform_size - margin),  # Bottom-left (unused)
            'purple': (PLATFORM_X + selected_platform_size - margin, PLATFORM_Y + margin)  # Top-right (unused)
        }
    else:
        # All corners for 3-4 players
        return {
            'red': (PLATFORM_X + margin, PLATFORM_Y + margin),  # Top-left
            'blue': (PLATFORM_X + selected_platform_size - margin, PLATFORM_Y + margin),  # Top-right
            'orange': (PLATFORM_X + margin, PLATFORM_Y + selected_platform_size - margin),  # Bottom-left
            'purple': (PLATFORM_X + selected_platform_size - margin, PLATFORM_Y + selected_platform_size - margin)  # Bottom-right
        }

def reset_balls(fallen_ball=None):
    """Reset ball positions and clear powerups. If fallen_ball is specified, only reset that ball."""
    spawn_pos = get_spawn_positions()
    
    if fallen_ball:
        # Only reset the fallen ball
        # Find which ball it is
        for color, ball in get_active_balls().items():
            if ball == fallen_ball:
                # Reset just this ball's position
                ball['x'], ball['y'] = spawn_pos[color]
                # Reset its velocity and powerup effects
                ball['vx'], ball['vy'] = 0, 0
                
                # If this ball had a shrink powerup, restore other balls to normal size
                if ball['powerup'] == 'shrink':
                    for other_ball in get_active_balls().values():
                        if other_ball != ball:
                            other_ball['radius'] = BALL_RADIUS
                
                # Reset this ball's powerup and radius
                ball['powerup'] = None
                ball['radius'] = BALL_RADIUS
                break
        # Don't clear powerups on the stage in 3-4 player mode
    else:
        # Reset all balls (used at game start)
        red_ball['x'], red_ball['y'] = spawn_pos['red']
        blue_ball['x'], blue_ball['y'] = spawn_pos['blue']
        orange_ball['x'], orange_ball['y'] = spawn_pos['orange']
        purple_ball['x'], purple_ball['y'] = spawn_pos['purple']
        
        # Reset velocities and other properties for all balls
        for ball in [red_ball, blue_ball, orange_ball, purple_ball]:
            ball['vx'], ball['vy'] = 0, 0
            ball['powerup'] = None
            ball['radius'] = BALL_RADIUS
            ball['last_hit_by'] = None
        
        # Only clear powerups on stage when resetting all balls
        global powerups
        powerups = []

def title_screen():
    global selected_win_score, selected_player_count, selected_platform_size, selected_powerup_interval
    selected_score_index = 0
    selected_player_index = 0
    selected_platform_index = 1  # Start with medium platform
    selected_powerup_index = 1   # Start with normal speed
    selected_option = 0  # 0: players, 1: score, 2: platform, 3: powerup speed
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    update_platform_position()
                    return
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % 4  # Now 4 options
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % 4  # Now 4 options
                elif event.key == pygame.K_LEFT:
                    if selected_option == 0:  # Players
                        selected_player_index = (selected_player_index - 1) % len(PLAYER_COUNTS)
                        selected_player_count = PLAYER_COUNTS[selected_player_index]
                    elif selected_option == 1:  # Score
                        selected_score_index = (selected_score_index - 1) % len(WIN_SCORES)
                        selected_win_score = WIN_SCORES[selected_score_index]
                    elif selected_option == 2:  # Platform
                        selected_platform_index = (selected_platform_index - 1) % len(PLATFORM_SIZES)
                        selected_platform_size = PLATFORM_SIZES[selected_platform_index]
                    else:  # Powerup speed
                        selected_powerup_index = (selected_powerup_index - 1) % len(POWERUP_INTERVALS)
                        selected_powerup_interval = POWERUP_INTERVALS[selected_powerup_index]
                elif event.key == pygame.K_RIGHT:
                    if selected_option == 0:  # Players
                        selected_player_index = (selected_player_index + 1) % len(PLAYER_COUNTS)
                        selected_player_count = PLAYER_COUNTS[selected_player_index]
                    elif selected_option == 1:  # Score
                        selected_score_index = (selected_score_index + 1) % len(WIN_SCORES)
                        selected_win_score = WIN_SCORES[selected_score_index]
                    elif selected_option == 2:  # Platform
                        selected_platform_index = (selected_platform_index + 1) % len(PLATFORM_SIZES)
                        selected_platform_size = PLATFORM_SIZES[selected_platform_index]
                    else:  # Powerup speed
                        selected_powerup_index = (selected_powerup_index + 1) % len(POWERUP_INTERVALS)
                        selected_powerup_interval = POWERUP_INTERVALS[selected_powerup_index]

        screen.fill(BACKGROUND_COLOR)
        
        # Draw title
        draw_text_with_outline("ROLLY", title_font, WIDTH // 2, HEIGHT // 4, RED, BLACK, center=True)
        
        # Draw options
        y_start = HEIGHT // 2 - 75  # Adjusted to accommodate new option
        spacing = 50
        
        # Player count (option 0)
        color = WHITE if selected_option == 0 else GRAY
        player_text = f"{selected_player_count} Players"
        draw_text_with_outline(player_text, subtitle_font, WIDTH // 2, y_start, color, BLACK, center=True)
        
        # Win score (option 1)
        color = WHITE if selected_option == 1 else GRAY
        score_text = f"First to {selected_win_score} points"
        draw_text_with_outline(score_text, subtitle_font, WIDTH // 2, y_start + spacing, color, BLACK, center=True)
        
        # Platform size (option 2)
        color = WHITE if selected_option == 2 else GRAY
        size_names = {400: "Small", 600: "Medium", 700: "Large"}
        platform_text = f"Platform: {size_names[selected_platform_size]}"
        draw_text_with_outline(platform_text, subtitle_font, WIDTH // 2, y_start + spacing * 2, color, BLACK, center=True)
        
        # Powerup speed (option 3)
        color = WHITE if selected_option == 3 else GRAY
        speed_names = {30000: "Slow", 15000: "Normal", 7500: "Fast"}
        powerup_text = f"Powerup Speed: {speed_names[selected_powerup_interval]}"
        draw_text_with_outline(powerup_text, subtitle_font, WIDTH // 2, y_start + spacing * 3, color, BLACK, center=True)
        
        # Draw controls hint
        controls_text = "UP DOWN to select | LEFT RIGHT to change | Enter to start"
        draw_text_with_outline(controls_text, subtitle_font, WIDTH // 2, HEIGHT * 3 // 4, GRAY, BLACK, center=True)
        
        pygame.display.flip()
        clock.tick(FPS)

def show_start_message():
    screen.fill(BACKGROUND_COLOR)
    draw_text_with_outline("Start!", title_font, WIDTH // 2, HEIGHT // 2, WHITE, BLACK, center=True)
    pygame.display.flip()
    time.sleep(1)

def main_game():
    global powerups, last_powerup_spawn
    active_balls = get_active_balls()
    
    while True:
        current_time = pygame.time.get_ticks()
        
        # Check for win condition
        for color in active_balls:
            if score[color] >= selected_win_score:
                show_winner(color.capitalize())
                return
        
        # Spawn powerups periodically using selected interval
        if current_time - last_powerup_spawn > selected_powerup_interval:
            if len(powerups) < 3:  # Limit maximum powerups
                powerups.append(spawn_powerup())
                last_powerup_spawn = current_time
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        # Only move active balls
        if 'red' in active_balls:
            move_ball(red_ball, keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)
        if 'blue' in active_balls:
            move_ball(blue_ball, keys, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)
        if 'orange' in active_balls:
            move_ball(orange_ball, keys, pygame.K_i, pygame.K_k, pygame.K_j, pygame.K_l)
        if 'purple' in active_balls:
            move_ball(purple_ball, keys, pygame.K_KP8, pygame.K_KP5, pygame.K_KP4, pygame.K_KP6)

        # Apply physics and check collisions for active balls
        for ball in active_balls.values():
            apply_physics(ball)
            check_powerup_collision(ball)
        
        # Generate collision pairs for active balls
        ball_pairs = []
        ball_list = list(active_balls.values())
        for i in range(len(ball_list)):
            for j in range(i + 1, len(ball_list)):
                ball_pairs.append((ball_list[i], ball_list[j]))
        
        # Handle collisions
        for ball1, ball2 in ball_pairs:
            handle_collision(ball1, ball2)

        # Check if any active ball is off platform
        for color, ball in active_balls.items():
            if is_off_platform(ball):
                if ball['last_hit_by'] is not None:
                    # Give point to the player who knocked this ball off
                    for other_color, other_ball in active_balls.items():
                        if other_ball == ball['last_hit_by']:
                            score[other_color] += 1
                            break
                else:
                    # Ball fell off by itself - give point to the last player to touch it
                    # or if no one touched it, give points to all other players
                    other_players = [c for c in active_balls.keys() if c != color]
                    for other_color in other_players:
                        score[other_color] += 1

                # Only reset the fallen ball in 3-4 player mode
                if selected_player_count >= 3:
                    reset_balls(ball)
                else:
                    reset_balls()  # Reset all balls in 2 player mode
                break

        # Check powerup expiry for all active balls
        for ball in active_balls.values():
            check_powerup_expiry(ball)

        screen.fill(BACKGROUND_COLOR)
        draw_platform()
        draw_powerups()
        for ball in active_balls.values():
            draw_ball(ball)
        draw_scores()
        pygame.display.flip()
        clock.tick(FPS)

def show_winner(winner):
    """Show the winner screen"""
    waiting = True
    start_time = pygame.time.get_ticks()
    winner_colors = {
        'Red': RED,
        'Blue': BLUE,
        'Orange': ORANGE,
        'Purple': PLAYER_PURPLE
    }
    active_balls = get_active_balls()
    
    while waiting:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_RETURN:
                if current_time - start_time > 1000:
                    waiting = False
        
        screen.fill(BACKGROUND_COLOR)
        winner_color = winner_colors[winner]
        draw_text_with_outline(f"{winner} Wins!", title_font, WIDTH // 2, HEIGHT // 3, winner_color, BLACK, center=True)
        
        # Show scores for active players only
        y_pos = HEIGHT // 2
        for color in active_balls:
            color_name = color.capitalize()
            draw_text_with_outline(f"{color_name}: {score[color]}", 
                                 subtitle_font, WIDTH // 2, y_pos, winner_colors[color_name], BLACK, center=True)
            y_pos += 40
            
        draw_text_with_outline("Press Enter to Play Again", 
                             subtitle_font, WIDTH // 2, HEIGHT * 4 // 5, WHITE, BLACK, center=True)
        pygame.display.flip()
        clock.tick(FPS)

def handle_collision(ball1, ball2):
    """Handle collision between two balls"""
    dx = ball1['x'] - ball2['x']
    dy = ball1['y'] - ball2['y']
    dist = (dx**2 + dy**2)**0.5
    if dist < ball1['radius'] + ball2['radius']:
        overlap = (ball1['radius'] + ball2['radius']) - dist
        
        # Calculate knockback multiplier based on powerups
        knockback1 = 0.05  # knockback applied to ball1
        knockback2 = 0.05  # knockback applied to ball2
        
        # Modify knockback based on powerups
        if ball1['powerup'] == 'grow':
            knockback2 *= 2  # ball1 applies more knockback to ball2
        if ball2['powerup'] == 'grow':
            knockback1 *= 2  # ball2 applies more knockback to ball1
            
        # Shield makes the ball immune to knockback
        if ball1['powerup'] == 'shield':
            knockback1 = 0  # ball1 receives no knockback
        if ball2['powerup'] == 'shield':
            knockback2 = 0  # ball2 receives no knockback
            
        # Apply knockback to both balls
        ball1['vx'] += dx * overlap * knockback1
        ball1['vy'] += dy * overlap * knockback1
        ball2['vx'] -= dx * overlap * knockback2
        ball2['vy'] -= dy * overlap * knockback2
        
        # Track who hit whom
        if knockback2 > 0:  # If ball1 can affect ball2
            ball2['last_hit_by'] = ball1
        if knockback1 > 0:  # If ball2 can affect ball1
            ball1['last_hit_by'] = ball2
        
        collision_sound.play()

def is_off_platform(ball):
    """Check if a ball is off the platform"""
    return (ball['x'] - ball['radius'] > PLATFORM_X + PLATFORM_SIZE or
            ball['x'] + ball['radius'] < PLATFORM_X or
            ball['y'] - ball['radius'] > PLATFORM_Y + PLATFORM_SIZE or
            ball['y'] + ball['radius'] < PLATFORM_Y)

def draw_platform():
    """Draw the platform."""
    pygame.draw.rect(screen, GRAY, (PLATFORM_X, PLATFORM_Y, PLATFORM_SIZE, PLATFORM_SIZE))

def draw_ball(ball):
    """Draw a ball with a glossy reflective look."""
    x, y = int(ball['x']), int(ball['y'])
    radius = int(ball['radius'])
    
    # Draw shield effect
    if ball['powerup'] == 'shield':
        pygame.draw.circle(screen, PURPLE, (x, y), radius + 5, 2)
    
    pygame.draw.circle(screen, BLACK, (x, y), radius + 3)  # Shadow
    for i, color in enumerate(ball['colors']):
        pygame.draw.circle(screen, color, (x, y), radius - i * 5)
    pygame.draw.circle(screen, WHITE, (x - radius // 3, y - radius // 3), radius // 4)  # Highlight

def draw_scores():
    """Draw the scores with a black outline."""
    active_balls = get_active_balls()
    if 'red' in active_balls:
        draw_text_with_outline(f"Red: {score['red']}", score_font, 10, 10, RED, BLACK, center=False)
    if 'blue' in active_balls:
        draw_text_with_outline(f"Blue: {score['blue']}", score_font, WIDTH - 150, 10, BLUE, BLACK, center=False)
    if 'orange' in active_balls:
        draw_text_with_outline(f"Orange: {score['orange']}", score_font, 10, HEIGHT - 30, ORANGE, BLACK, center=False)
    if 'purple' in active_balls:
        draw_text_with_outline(f"Purple: {score['purple']}", score_font, WIDTH - 150, HEIGHT - 30, PLAYER_PURPLE, BLACK, center=False)

def get_active_balls():
    """Return dictionary of active balls based on player count"""
    balls = {'red': red_ball, 'blue': blue_ball}
    if selected_player_count >= 3:
        balls['orange'] = orange_ball
    if selected_player_count >= 4:
        balls['purple'] = purple_ball
    return balls

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

def spawn_powerup():
    """Spawn a random powerup on the platform"""
    powerup_types = ['grow', 'shrink', 'shield']
    powerup_colors = {
        'grow': [DARKER_YELLOW, YELLOW, LIGHT_YELLOW],
        'shrink': [DARKER_GREEN, GREEN, LIGHT_GREEN],
        'shield': [DARKER_PURPLE, PURPLE, LIGHT_PURPLE]
    }
    
    type = random.choice(powerup_types)
    x = random.randint(PLATFORM_X + POWERUP_SIZE, PLATFORM_X + PLATFORM_SIZE - POWERUP_SIZE)
    y = random.randint(PLATFORM_Y + POWERUP_SIZE, PLATFORM_Y + PLATFORM_SIZE - POWERUP_SIZE)
    
    return {
        'type': type,
        'x': x,
        'y': y,
        'colors': powerup_colors[type]
    }

def draw_powerups():
    """Draw all active powerups with a glossy effect"""
    for powerup in powerups:
        x, y = powerup['x'], powerup['y']
        
        # Draw shadow
        pygame.draw.circle(screen, BLACK, (x, y), POWERUP_SIZE + 2)
        
        # Draw main circles with gradient effect
        for i, color in enumerate(powerup['colors']):
            pygame.draw.circle(screen, color, (x, y), POWERUP_SIZE - i * 5)
        
        # Draw highlight
        highlight_size = POWERUP_SIZE // 4
        pygame.draw.circle(screen, WHITE, (x - highlight_size, y - highlight_size), highlight_size)

def check_powerup_collision(ball):
    """Check if ball collides with any powerup"""
    global powerups
    for powerup in powerups[:]:
        dx = ball['x'] - powerup['x']
        dy = ball['y'] - powerup['y']
        dist = (dx**2 + dy**2)**0.5
        
        if dist < ball['radius'] + POWERUP_SIZE:
            apply_powerup(ball, powerup['type'])
            powerups.remove(powerup)

def apply_powerup(ball, powerup_type):
    """Apply powerup effect to ball with time limit"""
    current_time = pygame.time.get_ticks()
    ball['powerup'] = powerup_type
    ball['powerup_end'] = current_time + POWERUP_DURATIONS[powerup_type]
    
    if powerup_type == 'grow':
        ball['radius'] = BALL_RADIUS * GROW_MULTIPLIER
    elif powerup_type == 'shrink':
        # Shrink all other active balls
        active_balls = get_active_balls()
        for other_ball in active_balls.values():
            if other_ball != ball:
                other_ball['radius'] = BALL_RADIUS * SHRINK_MULTIPLIER

def check_powerup_expiry(ball):
    """Check if ball's powerup has expired"""
    current_time = pygame.time.get_ticks()
    if ball['powerup'] and current_time >= ball['powerup_end']:
        if ball['powerup'] == 'shrink':
            # Restore other balls to normal size
            active_balls = get_active_balls()
            for other_ball in active_balls.values():
                if other_ball != ball:
                    other_ball['radius'] = BALL_RADIUS
        # Reset ball's powerup
        ball['powerup'] = None
        ball['radius'] = BALL_RADIUS

# Modify the game loop to allow replaying
def game_loop():
    global score
    while True:
        score = {'red': 0, 'blue': 0, 'orange': 0, 'purple': 0}  # Reset scores
        title_screen()
        show_start_message()
        main_game()

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

    # Draw outline
    screen.blit(outline_surface, (outline_rect.x - 2, outline_rect.y - 2))
    screen.blit(outline_surface, (outline_rect.x + 2, outline_rect.y - 2))
    screen.blit(outline_surface, (outline_rect.x - 2, outline_rect.y + 2))
    screen.blit(outline_surface, (outline_rect.x + 2, outline_rect.y + 2))
    
    # Draw main text
    screen.blit(text_surface, text_rect)

# Replace the final lines with:
game_loop()
