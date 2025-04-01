import pygame
import sys
from pygame.locals import QUIT, KEYDOWN, K_RETURN
import time
import math
import random

# Initialize Pygamess
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

# Add to the colors section at the top
LIGHT_BLUE = (135, 206, 235)
DARKER_LIGHT_BLUE = (100, 150, 180)
DARKEST_LIGHT_BLUE = (80, 120, 150)

# Add to the colors section at the top
DARK_GRAY = (50, 50, 50)

# Add to the colors section at the top
TEAL = (0, 128, 128)
DARK_TEAL = (0, 100, 100)
DARKER_TEAL = (0, 80, 80)

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
pygame.display.set_caption("Rolly V0.5")
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
    'last_hit_by': None,
    'trail': [],
    'frozen': False,
    'frozen_end': 0,
    'heavy_hit': False,
    'hit_flash_start': 0,
    'tron_trail': []  # List to store trail segments
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
    'last_hit_by': None,
    'trail': [],
    'frozen': False,
    'frozen_end': 0,
    'heavy_hit': False,
    'hit_flash_start': 0,
    'tron_trail': []  # List to store trail segments
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
    'last_hit_by': None,
    'trail': [],
    'frozen': False,
    'frozen_end': 0,
    'heavy_hit': False,
    'hit_flash_start': 0,
    'tron_trail': []  # List to store trail segments
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
    'last_hit_by': None,
    'trail': [],
    'frozen': False,
    'frozen_end': 0,
    'heavy_hit': False,
    'hit_flash_start': 0,
    'tron_trail': []  # List to store trail segments
}

# Score
score = {'red': 0, 'blue': 0, 'orange': 0, 'purple': 0, 'ai': 0}

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

# Modify PLAYER_COUNTS to create the desired cycling order
PLAYER_COUNTS = [2, 3, 4, 1]  # Changed order so 2 is first, then 3, 4, and 1
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
    'shield': 7000,   # 7 seconds
    'freeze': 2000,   # 2 seconds
    'heavy': 5000,    # 5 seconds to use the heavy hit
    'tron': 5000      # 5 seconds of trail
}

# Add after other constants
GAME_MODES = ["Normal", "Last Standing"]
selected_game_mode = GAME_MODES[0]  # Default to normal mode

# Add after other global constants
TRAIL_LENGTH = 4  # Number of ghost images in trail
TRAIL_FADE = 0.1  # How quickly the trail fades (0-1)
TRAIL_SPACING = 20  # Minimum pixels between trail images

# Add AI ball colors
AI_GRAY = (70, 70, 70)
AI_DARK_GRAY = (50, 50, 50)
AI_DARKER_GRAY = (30, 30, 30)

# Add AI ball setup
ai_ball = {
    'x': PLATFORM_X + 450, 
    'y': PLATFORM_Y + 150, 
    'vx': 0, 
    'vy': 0, 
    'colors': [AI_DARKER_GRAY, AI_DARK_GRAY, AI_GRAY],
    'radius': BALL_RADIUS,
    'powerup': None,
    'powerup_end': 0,
    'last_hit_by': None,
    'trail': [],
    'frozen': False,
    'frozen_end': 0,
    'heavy_hit': False,
    'hit_flash_start': 0,
    'tron_trail': [],  # List to store trail segments
    'is_ai': True  # Flag to identify AI-controlled ball
}

# Add these constants for AI behavior
AI_CHASE_DISTANCE = 300  # Distance at which AI starts chasing player
AI_POWERUP_INTEREST = 150  # Distance at which AI gets interested in powerups
AI_PLATFORM_MARGIN = 50  # How far from edge AI tries to stay
AI_SPEED = 2.0  # Increased from 1.5 for more aggressive movement
AI_ACCELERATION = 0.2  # Increased from 0.15 for faster response
AI_POWERUP_PRIORITY = 0.9  # Increased chance to go for powerups

# Add to the constants section
SPAWN_IMMUNITY_DURATION = 1500  # 1.5 seconds of immunity after spawn

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
    active_balls = get_active_balls()
    
    # Only update positions of active balls
    for color, ball in active_balls.items():
        ball['x'], ball['y'] = spawn_pos[color]

def get_spawn_positions():
    """Get spawn positions for balls based on platform size and player count"""
    margin = 80  # Distance from corner
    
    if selected_player_count == 1:
        return {
            'red': (PLATFORM_X + margin, PLATFORM_Y + margin),  # Player in top-left
            'ai': (PLATFORM_X + selected_platform_size - margin, 
                  PLATFORM_Y + selected_platform_size - margin)  # AI in bottom-right
        }
    elif selected_player_count == 2:
        # Diagonal corners for 2 players (top-left and bottom-right)
        return {
            'red': (PLATFORM_X + margin, PLATFORM_Y + margin),  # Top-left
            'blue': (PLATFORM_X + selected_platform_size - margin, 
                    PLATFORM_Y + selected_platform_size - margin),  # Bottom-right
            'orange': (PLATFORM_X + margin, PLATFORM_Y + selected_platform_size - margin),  # Bottom-left (unused)
            'purple': (PLATFORM_X + selected_platform_size - margin, PLATFORM_Y + margin)  # Top-right (unused)
        }
    else:
        # All corners for 3-4 players
        return {
            'red': (PLATFORM_X + margin, PLATFORM_Y + margin),  # Top-left
            'blue': (PLATFORM_X + selected_platform_size - margin, PLATFORM_Y + margin),  # Top-right
            'orange': (PLATFORM_X + margin, PLATFORM_Y + selected_platform_size - margin),  # Bottom-left
            'purple': (PLATFORM_X + selected_platform_size - margin, 
                      PLATFORM_Y + selected_platform_size - margin)  # Bottom-right
        }

def reset_balls(fallen_ball=None):
    """Reset ball positions and clear powerups."""
    spawn_pos = get_spawn_positions()
    current_time = pygame.time.get_ticks()
    
    if fallen_ball:
        # Only reset the fallen ball
        for color, ball in get_active_balls().items():
            if ball == fallen_ball:
                ball['x'], ball['y'] = spawn_pos[color]
                ball['vx'], ball['vy'] = 0, 0
                ball['powerup'] = None
                ball['radius'] = BALL_RADIUS
                ball['trail'] = []
                ball['frozen'] = False
                ball['frozen_end'] = 0
                ball['heavy_hit'] = False
                ball['hit_flash_start'] = 0
                ball['tron_trail'] = []
                ball['spawn_immunity_end'] = current_time + SPAWN_IMMUNITY_DURATION
                break
    else:
        # Reset all balls
        active_balls = get_active_balls()
        for color, ball in active_balls.items():
            ball['x'], ball['y'] = spawn_pos[color]
            ball['vx'], ball['vy'] = 0, 0
            ball['powerup'] = None
            ball['radius'] = BALL_RADIUS
            ball['last_hit_by'] = None
            ball['trail'] = []
            ball['frozen'] = False
            ball['frozen_end'] = 0
            ball['heavy_hit'] = False
            ball['hit_flash_start'] = 0
            ball['tron_trail'] = []
            ball['spawn_immunity_end'] = current_time + SPAWN_IMMUNITY_DURATION
        
        # Only clear powerups on stage when resetting all balls
        global powerups
        powerups = []
        
        # Add brief pause in 1-player, 2-player mode or Last Standing mode
        if selected_player_count <= 2 or selected_game_mode == "Last Standing":
            # Draw current state
            screen.fill(BACKGROUND_COLOR)
            draw_platform()
            for ball in get_active_balls().values():
                draw_ball(ball)
            draw_scores()
            draw_text_with_outline("Ready...", subtitle_font, WIDTH // 2, HEIGHT // 2, WHITE, BLACK, center=True)
            pygame.display.flip()
            pygame.time.wait(1000)  # 1 second pause

def handle_title_ball_collision(ball1, ball2):
    """Handle collision between two balls in the title screen"""
    dx = ball1['pos']['x'] - ball2['pos']['x']
    dy = ball1['pos']['y'] - ball2['pos']['y']
    dist = (dx**2 + dy**2)**0.5
    
    if dist < BALL_RADIUS * 2:  # Using diameter as collision distance
        # Calculate collision response
        # Normalize the collision vector
        if dist != 0:
            nx = dx / dist
            ny = dy / dist
        else:
            nx, ny = 1, 0
            
        # Calculate relative velocity
        dvx = ball1['vel']['x'] - ball2['vel']['x']
        dvy = ball1['vel']['y'] - ball2['vel']['y']
        
        # Calculate impulse
        impulse = nx * dvx + ny * dvy
        
        # Apply impulse to both balls
        ball1['vel']['x'] -= nx * impulse
        ball1['vel']['y'] -= ny * impulse
        ball2['vel']['x'] += nx * impulse
        ball2['vel']['y'] += ny * impulse

def animate_title_balls(balls, active_count):
    """Animate multiple balls bouncing around the screen like DVD logos"""
    # Only process the active number of balls
    active_balls = balls[:active_count]
    
    # Update positions and handle wall collisions
    for ball in active_balls:
        # Update position
        ball['pos']['x'] += ball['vel']['x'] * ball['elapsed']
        ball['pos']['y'] += ball['vel']['y'] * ball['elapsed']
        
        # Bounce off screen edges
        if ball['pos']['x'] - BALL_RADIUS <= 0 or ball['pos']['x'] + BALL_RADIUS >= WIDTH:
            ball['vel']['x'] *= -1
        if ball['pos']['y'] - BALL_RADIUS <= 0 or ball['pos']['y'] + BALL_RADIUS >= HEIGHT:
            ball['vel']['y'] *= -1
    
    # Handle ball-to-ball collisions
    for i in range(len(active_balls)):
        for j in range(i + 1, len(active_balls)):
            handle_title_ball_collision(active_balls[i], active_balls[j])
    
    # Draw all active balls
    for ball in active_balls:
        draw_ball({
            'x': ball['pos']['x'],
            'y': ball['pos']['y'],
            'radius': BALL_RADIUS,
            'colors': ball['colors'],
            'powerup': None
        })

def title_screen():
    global selected_win_score, selected_player_count, selected_platform_size, selected_powerup_interval, selected_game_mode
    selected_score_index = 0
    selected_player_index = 0
    selected_platform_index = 1
    selected_powerup_index = 1
    selected_mode_index = 0
    selected_option = 0
    
    # Initialize bouncing balls with different starting positions and velocities
    balls = [
        {
            'pos': {'x': WIDTH // 4, 'y': HEIGHT // 4},
            'vel': {'x': 0.3, 'y': 0.2},
            'colors': [DARKER_RED, DARK_RED, RED],  # Red ball
            'elapsed': 0
        },
        {
            'pos': {'x': WIDTH * 3 // 4, 'y': HEIGHT // 4},
            'vel': {'x': -0.25, 'y': 0.3},
            'colors': [DARKER_BLUE, DARK_BLUE, BLUE],  # Blue ball
            'elapsed': 0
        },
        {
            'pos': {'x': WIDTH // 4, 'y': HEIGHT * 3 // 4},
            'vel': {'x': 0.2, 'y': -0.25},
            'colors': [DARKER_ORANGE, DARK_ORANGE, ORANGE],  # Orange/Yellow ball
            'elapsed': 0
        },
        {
            'pos': {'x': WIDTH * 3 // 4, 'y': HEIGHT * 3 // 4},
            'vel': {'x': -0.3, 'y': -0.2},
            'colors': [DARKER_PLAYER_PURPLE, DARK_PLAYER_PURPLE, PLAYER_PURPLE],  # Purple ball
            'elapsed': 0
        },
        {
            'pos': {'x': WIDTH * 3 // 4, 'y': HEIGHT // 4},
            'vel': {'x': -0.25, 'y': 0.3},
            'colors': [AI_DARKER_GRAY, AI_DARK_GRAY, AI_GRAY],  # Black ball
            'elapsed': 0
        }
    ]
    
    # Modify the ball list based on player count
    def get_active_title_balls(player_count):
        if player_count == 1:
            return [balls[0], balls[4]]  # Red and Black
        elif player_count == 2:
            return [balls[0], balls[1]]  # Red and Blue
        elif player_count == 3:
            return [balls[0], balls[1], balls[2]]  # Red, Blue, and Orange/Yellow
        else:
            return [balls[0], balls[1], balls[2], balls[3]]  # Red, Blue, Orange/Yellow, and Purple

    last_time = pygame.time.get_ticks()
    
    while True:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - last_time
        last_time = current_time
        
        # Update elapsed time for each ball
        for ball in balls:
            ball['elapsed'] = elapsed_time
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if selected_player_count == 2 and selected_game_mode == "Last Standing":
                        # Force normal mode for 2 players
                        selected_game_mode = "Normal"
                    update_platform_position()
                    return
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % 5  # Now 5 options
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % 5  # Now 5 options
                elif event.key == pygame.K_LEFT:
                    if selected_option == 0:  # Players
                        selected_player_index = (selected_player_index - 1) % len(PLAYER_COUNTS)
                        selected_player_count = PLAYER_COUNTS[selected_player_index]
                        if selected_player_count == 2:
                            selected_game_mode = "Normal"  # Force normal mode for 2 players
                    elif selected_option == 1:  # Game Mode
                        if selected_player_count > 2:  # Only allow mode change for 3+ players
                            selected_mode_index = (selected_mode_index - 1) % len(GAME_MODES)
                            selected_game_mode = GAME_MODES[selected_mode_index]
                    elif selected_option == 2:  # Score
                        selected_score_index = (selected_score_index - 1) % len(WIN_SCORES)
                        selected_win_score = WIN_SCORES[selected_score_index]
                    elif selected_option == 3:  # Platform
                        selected_platform_index = (selected_platform_index - 1) % len(PLATFORM_SIZES)
                        selected_platform_size = PLATFORM_SIZES[selected_platform_index]
                    else:  # Powerup speed
                        selected_powerup_index = (selected_powerup_index - 1) % len(POWERUP_INTERVALS)
                        selected_powerup_interval = POWERUP_INTERVALS[selected_powerup_index]
                elif event.key == pygame.K_RIGHT:
                    if selected_option == 0:  # Players
                        selected_player_index = (selected_player_index + 1) % len(PLAYER_COUNTS)
                        selected_player_count = PLAYER_COUNTS[selected_player_index]
                        if selected_player_count == 2:
                            selected_game_mode = "Normal"  # Force normal mode for 2 players
                    elif selected_option == 1:  # Game Mode
                        if selected_player_count > 2:  # Only allow mode change for 3+ players
                            selected_mode_index = (selected_mode_index + 1) % len(GAME_MODES)
                            selected_game_mode = GAME_MODES[selected_mode_index]
                    elif selected_option == 2:  # Score
                        selected_score_index = (selected_score_index + 1) % len(WIN_SCORES)
                        selected_win_score = WIN_SCORES[selected_score_index]
                    elif selected_option == 3:  # Platform
                        selected_platform_index = (selected_platform_index + 1) % len(PLATFORM_SIZES)
                        selected_platform_size = PLATFORM_SIZES[selected_platform_index]
                    else:  # Powerup speed
                        selected_powerup_index = (selected_powerup_index + 1) % len(POWERUP_INTERVALS)
                        selected_powerup_interval = POWERUP_INTERVALS[selected_powerup_index]

        screen.fill(BACKGROUND_COLOR)
        
        # Animate the bouncing balls with current player count
        animate_title_balls(get_active_title_balls(selected_player_count), 
                          len(get_active_title_balls(selected_player_count)))
        
        # Draw title
        draw_text_with_outline("ROLLY", title_font, WIDTH // 2, HEIGHT // 4, RED, BLACK, center=True)
        
        # Draw options
        y_start = HEIGHT // 2 - 100  # Adjusted to accommodate new option
        spacing = 50
        
        # Player count (option 0)
        color = WHITE if selected_option == 0 else GRAY
        player_text = f"{selected_player_count} Players"
        draw_text_with_outline(player_text, subtitle_font, WIDTH // 2, y_start, color, BLACK, center=True)
        
        # Game Mode (option 1)
        color = WHITE if selected_option == 1 else GRAY
        mode_color = color if selected_player_count > 2 else GRAY
        mode_text = f"Mode: {selected_game_mode}"
        draw_text_with_outline(mode_text, subtitle_font, WIDTH // 2, y_start + spacing, mode_color, BLACK, center=True)
        
        # Win score (option 2)
        color = WHITE if selected_option == 2 else GRAY
        score_text = f"First to {selected_win_score} points"
        draw_text_with_outline(score_text, subtitle_font, WIDTH // 2, y_start + spacing * 2, color, BLACK, center=True)
        
        # Platform size (option 3)
        color = WHITE if selected_option == 3 else GRAY
        size_names = {400: "Small", 600: "Medium", 700: "Large"}
        platform_text = f"Platform: {size_names[selected_platform_size]}"
        draw_text_with_outline(platform_text, subtitle_font, WIDTH // 2, y_start + spacing * 3, color, BLACK, center=True)
        
        # Powerup speed (option 4)
        color = WHITE if selected_option == 4 else GRAY
        speed_names = {30000: "Slow", 15000: "Normal", 7500: "Fast"}
        powerup_text = f"Powerup Speed: {speed_names[selected_powerup_interval]}"
        draw_text_with_outline(powerup_text, subtitle_font, WIDTH // 2, y_start + spacing * 4, color, BLACK, center=True)
        
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
    
    # Reset game state
    reset_balls()
    powerups = []
    last_powerup_spawn = pygame.time.get_ticks()
    active_balls = get_active_balls()
    
    while True:
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        
        # Handle player movements based on active balls
        if 'red' in active_balls:
            move_ball(red_ball, keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)  # WASD
            
        if 'blue' in active_balls:
            move_ball(blue_ball, keys, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)  # Arrow keys
            
        if 'orange' in active_balls:
            move_ball(orange_ball, keys, pygame.K_i, pygame.K_k, pygame.K_j, pygame.K_l)  # IJKL
            
        if 'purple' in active_balls:
            move_ball(purple_ball, keys, pygame.K_KP8, pygame.K_KP5, pygame.K_KP4, pygame.K_KP6)  # Numpad
        
        # Handle AI movement in 1-player mode
        if selected_player_count == 1 and 'ai' in active_balls:
            move_ai_ball(ai_ball, red_ball, current_time)
        
        # Check for win condition
        for color in active_balls:
            if score[color] >= selected_win_score:
                # Convert color name for winner display
                if color == 'ai':
                    winner_name = 'Black'
                else:
                    winner_name = color.capitalize()
                show_winner(winner_name)
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
        fallen_balls = []
        for color, ball in active_balls.items():
            if is_off_platform(ball):
                fallen_balls.append((color, ball))
        
        if fallen_balls:
            if selected_game_mode == "Last Standing" and selected_player_count > 2:
                # Remove fallen balls and check if only one remains
                for color, ball in fallen_balls:
                    del active_balls[color]
                
                if len(active_balls) == 1:
                    # Last player standing gets the point
                    last_color = list(active_balls.keys())[0]
                    score[last_color] += 1
                    active_balls = get_active_balls()  # Reset active balls dictionary
                    reset_balls()  # Reset all balls for next round
                elif len(active_balls) == 0:
                    # Everyone fell off, reset all balls with no points awarded
                    active_balls = get_active_balls()  # Reset active balls dictionary
                    reset_balls()
            else:
                # Normal mode scoring
                for color, ball in fallen_balls:
                    if ball['last_hit_by'] is not None:
                        # Give point to the player who knocked this ball off
                        for other_color, other_ball in active_balls.items():
                            if other_ball == ball['last_hit_by']:
                                score[other_color] += 1
                                break
                    else:
                        # Ball fell off by itself - give point to all other players
                        other_players = [c for c in active_balls.keys() if c != color]
                        for other_color in other_players:
                            score[other_color] += 1

                # Reset balls according to mode and player count
                if selected_player_count >= 3 and selected_game_mode == "Normal":
                    for _, ball in fallen_balls:
                        reset_balls(ball)
                else:
                    reset_balls()  # Reset all balls

        # Check powerup expiry for all active balls
        for ball in active_balls.values():
            check_powerup_expiry(ball)

        # Inside the main loop, after applying physics:
        for ball in active_balls.values():
            # Check if frozen state should end
            if ball.get('frozen', False) and current_time >= ball.get('frozen_end', 0):
                ball['frozen'] = False
                ball['frozen_end'] = 0

        # After applying physics to all balls
        for ball in active_balls.values():
            check_tron_trail_collision(ball)

        screen.fill(BACKGROUND_COLOR)
        draw_platform()
        draw_powerups()
        for ball in active_balls.values():
            draw_ball(ball)
        draw_scores()
        pygame.display.flip()
        clock.tick(FPS)

def create_win_ball(x, y, vx, vy, colors):
    """Create a ball for the win animation"""
    return {
        'pos': {'x': x, 'y': y},
        'vel': {'x': vx, 'y': vy},
        'colors': colors,
        'elapsed': 0
    }

def show_winner(winner):
    """Show the winner screen with multiplying DVD-style bouncing balls"""
    waiting = True
    start_time = pygame.time.get_ticks()
    last_time = start_time
    
    # Set up winning ball colors
    winner_colors = {
        'Red': [DARKER_RED, DARK_RED, RED],
        'Blue': [DARKER_BLUE, DARK_BLUE, BLUE],
        'Orange': [DARKER_ORANGE, DARK_ORANGE, ORANGE],
        'Purple': [DARKER_PLAYER_PURPLE, DARK_PLAYER_PURPLE, PLAYER_PURPLE],
        'Black': [AI_DARKER_GRAY, AI_DARK_GRAY, AI_GRAY]
    }
    
    # Initialize with a single ball in the middle
    balls = [{
        'pos': {'x': WIDTH // 2, 'y': HEIGHT // 2},
        'vel': {'x': 0.3, 'y': 0.2},
        'colors': winner_colors[winner],
        'elapsed': 0,
        'active': True
    }]
    
    # Configuration
    max_balls = 120  # Maximum number of balls
    spawn_interval = 1  # Frames between spawns
    frame_count = 0
    bounce_speed = 0.4  # Speed of balls
    
    while waiting:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - last_time
        last_time = current_time
        frame_count += 1
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_RETURN:
                if current_time - start_time > 1000:  # Prevent immediate skip
                    waiting = False
        
        screen.fill(BACKGROUND_COLOR)
        
        # Spawn new ball every spawn_interval frames
        if frame_count % spawn_interval == 0 and len(balls) < max_balls:
            # Pick random active ball to split from
            active_balls = [b for b in balls if b['active']]
            if active_balls:
                parent = random.choice(active_balls)
                # Create new ball with slightly varied velocity
                angle = random.uniform(0, 2 * math.pi)
                new_ball = {
                    'pos': {'x': parent['pos']['x'], 'y': parent['pos']['y']},
                    'vel': {
                        'x': bounce_speed * math.cos(angle),
                        'y': bounce_speed * math.sin(angle)
                    },
                    'colors': winner_colors[winner],
                    'elapsed': 0,
                    'active': True
                }
                balls.append(new_ball)
        
        # Update and draw all balls
        for ball in balls:
            ball['elapsed'] = elapsed_time
            
            # Update position
            ball['pos']['x'] += ball['vel']['x'] * ball['elapsed']
            ball['pos']['y'] += ball['vel']['y'] * ball['elapsed']
            
            # DVD-style bounce off edges
            if ball['pos']['x'] - BALL_RADIUS <= 0:
                ball['pos']['x'] = BALL_RADIUS
                ball['vel']['x'] = abs(ball['vel']['x'])
            elif ball['pos']['x'] + BALL_RADIUS >= WIDTH:
                ball['pos']['x'] = WIDTH - BALL_RADIUS
                ball['vel']['x'] = -abs(ball['vel']['x'])
            
            if ball['pos']['y'] - BALL_RADIUS <= 0:
                ball['pos']['y'] = BALL_RADIUS
                ball['vel']['y'] = abs(ball['vel']['y'])
            elif ball['pos']['y'] + BALL_RADIUS >= HEIGHT:
                ball['pos']['y'] = HEIGHT - BALL_RADIUS
                ball['vel']['y'] = -abs(ball['vel']['y'])
            
            # Draw the ball
            draw_ball({
                'x': ball['pos']['x'],
                'y': ball['pos']['y'],
                'radius': BALL_RADIUS,
                'colors': ball['colors'],
                'powerup': None
            })
        
        # Draw winner text
        if current_time - start_time > 500:  # Slight delay before showing text
            winner_color = winner_colors[winner][2]
            draw_text_with_outline(f"{winner} Wins!", title_font, WIDTH // 2, HEIGHT // 3, 
                                 winner_color, BLACK, center=True)
            
            # Show scores for active players
            active_balls = get_active_balls()
            y_pos = HEIGHT // 2
            for color in active_balls:
                # Convert color name properly for display
                if color == 'ai':
                    display_name = 'Black'
                    color_value = winner_colors['Black'][2]
                else:
                    display_name = color.capitalize()
                    color_value = winner_colors[display_name][2]
                
                draw_text_with_outline(f"{display_name}: {score[color]}", 
                                     subtitle_font, WIDTH // 2, y_pos, 
                                     color_value, BLACK, center=True)
                y_pos += 40
            
            # Show continue prompt
            if current_time - start_time > 1000:
                draw_text_with_outline("Press Enter to Play Again", 
                                     subtitle_font, WIDTH // 2, HEIGHT * 4 // 5, 
                                     WHITE, BLACK, center=True)
        
        pygame.display.flip()
        clock.tick(FPS)

def handle_collision(ball1, ball2):
    """Handle collision between two balls"""
    current_time = pygame.time.get_ticks()
    
    # Skip collision if either ball has spawn immunity
    if (ball1.get('spawn_immunity_end', 0) > current_time or 
        ball2.get('spawn_immunity_end', 0) > current_time):
        return
        
    dx = ball1['x'] - ball2['x']
    dy = ball1['y'] - ball2['y']
    dist = (dx**2 + dy**2)**0.5
    
    if dist < ball1['radius'] + ball2['radius']:
        overlap = (ball1['radius'] + ball2['radius']) - dist
        
        # Calculate knockback multiplier based on powerups
        knockback1 = 0.05  # knockback applied to ball1
        knockback2 = 0.05  # knockback applied to ball2
        
        # Check for heavy hit
        if ball1.get('heavy_hit', False):
            knockback1 = 0  # Make ball1 immune (like shield)
            knockback2 *= 5  # Reduced from 7 to 5 for more balanced force
            ball2['hit_flash_start'] = pygame.time.get_ticks()
            ball1['heavy_hit'] = False  # Consume the heavy hit
            ball1['powerup'] = None  # Remove powerup
        elif ball2.get('heavy_hit', False):
            knockback2 = 0  # Make ball2 immune (like shield)
            knockback1 *= 5  # Reduced from 7 to 5 for more balanced force
            ball1['hit_flash_start'] = pygame.time.get_ticks()
            ball2['heavy_hit'] = False  # Consume the heavy hit
            ball2['powerup'] = None  # Remove powerup
        
        # Modify knockback based on powerups
        if ball1['powerup'] == 'grow':
            knockback2 *= 2
        if ball2['powerup'] == 'grow':
            knockback1 *= 2
            
        # Shield makes the ball immune to knockback
        if ball1['powerup'] == 'shield':
            knockback1 = 0
        if ball2['powerup'] == 'shield':
            knockback2 = 0
            
        # Apply knockback to both balls
        ball1['vx'] += dx * overlap * knockback1
        ball1['vy'] += dy * overlap * knockback1
        ball2['vx'] -= dx * overlap * knockback2
        ball2['vy'] -= dy * overlap * knockback2
        
        # Track who hit whom
        if knockback2 > 0 or ball1.get('heavy_hit', False):  # If ball1 affected ball2
            ball2['last_hit_by'] = ball1
        if knockback1 > 0 or ball2.get('heavy_hit', False):  # If ball2 affected ball1
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
    """Draw a ball with a glossy reflective look and trail effect if shielded."""
    x, y = int(ball['x']), int(ball['y'])
    radius = int(ball['radius'])
    current_time = pygame.time.get_ticks()
    
    # Initialize trail if it doesn't exist
    if 'trail' not in ball:
        ball['trail'] = []
    
    # Draw trail if ball has shield powerup or was recently hit
    if ball['powerup'] == 'shield' or ball.get('hit_flash_start', 0) > current_time - 1000:
        if not ball['trail'] or math.sqrt(
            (x - ball['trail'][-1]['x'])**2 + 
            (y - ball['trail'][-1]['y'])**2) > TRAIL_SPACING:
            
            ball['trail'].append({
                'x': x,
                'y': y,
                'time': current_time,
                'initial_alpha': 255
            })
            
            # Remove old trail positions
            while len(ball['trail']) > TRAIL_LENGTH:
                ball['trail'].pop(0)
        
        # Draw and update each ghost in the trail
        for ghost in ball['trail'][:-1]:  # Don't draw ghost at current position
            # Calculate how long this ghost has existed
            age = (current_time - ghost['time']) / 1000.0  # Convert to seconds
            
            # Calculate alpha based on age
            alpha = int(ghost['initial_alpha'] * (TRAIL_FADE ** (age * 5)))
            
            if alpha > 0:
                # Create a surface for this trail segment
                trail_surface = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
                
                # Draw the trail segment with transparency
                for j, color in enumerate(ball['colors']):
                    # Convert color to include alpha
                    color_with_alpha = (*color, alpha)
                    pygame.draw.circle(trail_surface, color_with_alpha, 
                                     (radius + 3, radius + 3), 
                                     radius - j * 5)
                
                # Draw the trail surface
                screen.blit(trail_surface, 
                           (ghost['x'] - radius - 3, ghost['y'] - radius - 3))
    else:
        # Clear trail when not shielded
        ball['trail'] = []
    
    # Draw shield effect
    if ball['powerup'] == 'shield':
        pygame.draw.circle(screen, PURPLE, (x, y), radius + 5, 2)
    
    # Draw outline
    if ball.get('frozen', False):
        pygame.draw.circle(screen, LIGHT_BLUE, (x, y), radius + 3)
    elif ball.get('heavy_hit', False):
        # Flash outline between black and white
        flash = (math.sin(current_time * 0.02) + 1) / 2  # Faster pulse than powerup
        outline_color = interpolate_color(BLACK, WHITE, flash)
        pygame.draw.circle(screen, outline_color, (x, y), radius + 3)
    else:
        pygame.draw.circle(screen, BLACK, (x, y), radius + 3)
    
    # Draw the main ball
    for i, color in enumerate(ball['colors']):
        pygame.draw.circle(screen, color, (x, y), radius - i * 5)
    pygame.draw.circle(screen, WHITE, (x - radius // 3, y - radius // 3), radius // 4)  # Highlight

    # Draw tron trail if active
    if ball['powerup'] == 'tron' and ball['tron_trail']:
        for segment in ball['tron_trail']:
            pygame.draw.line(screen, segment['color'], segment['start'], 
                           segment['end'], int(ball['radius']))  # Changed to radius instead of diameter

def draw_scores():
    """Draw the scores with a black outline."""
    active_balls = get_active_balls()
    if 'red' in active_balls:
        draw_text_with_outline(f"Red: {score['red']}", score_font, 10, 10, RED, BLACK, center=False)
    if 'ai' in active_balls:
        draw_text_with_outline(f"Black: {score['ai']}", score_font, WIDTH - 150, 10, AI_GRAY, BLACK, center=False)
    elif 'blue' in active_balls:
        draw_text_with_outline(f"Blue: {score['blue']}", score_font, WIDTH - 150, 10, BLUE, BLACK, center=False)
    if 'orange' in active_balls:
        draw_text_with_outline(f"Orange: {score['orange']}", score_font, 10, HEIGHT - 30, ORANGE, BLACK, center=False)
    if 'purple' in active_balls:
        draw_text_with_outline(f"Purple: {score['purple']}", score_font, WIDTH - 150, HEIGHT - 30, PLAYER_PURPLE, BLACK, center=False)

def get_active_balls():
    """Return dictionary of active balls based on player count"""
    if selected_player_count == 1:
        return {'red': red_ball, 'ai': ai_ball}
    balls = {'red': red_ball, 'blue': blue_ball}
    if selected_player_count >= 3:
        balls['orange'] = orange_ball
    if selected_player_count >= 4:
        balls['purple'] = purple_ball
    return balls

def move_ball(ball, keys, up, down, left, right):
    if not ball.get('frozen', False):  # Only move if not frozen
        if keys[up]: ball['vy'] -= BALL_SPEED
        if keys[down]: ball['vy'] += BALL_SPEED
        if keys[left]: ball['vx'] -= BALL_SPEED
        if keys[right]: ball['vx'] += BALL_SPEED

def move_ai_ball(ai_ball, player_ball, current_time):
    """Control AI ball movement"""
    if ai_ball.get('frozen', False):
        return
        
    dx = player_ball['x'] - ai_ball['x']
    dy = player_ball['y'] - ai_ball['y']
    dist_to_player = math.sqrt(dx*dx + dy*dy)
    
    # Initialize movement vector
    move_x = 0
    move_y = 0
    
    # Platform edge awareness
    dist_to_left = ai_ball['x'] - PLATFORM_X
    dist_to_right = PLATFORM_X + PLATFORM_SIZE - ai_ball['x']
    dist_to_top = ai_ball['y'] - PLATFORM_Y
    dist_to_bottom = PLATFORM_Y + PLATFORM_SIZE - ai_ball['y']
    
    # Strong edge avoidance - increased margin and force when player has powerup
    platform_margin = AI_PLATFORM_MARGIN * (2 if player_ball['powerup'] else 1)
    edge_force = 4.0 if player_ball['powerup'] else 3.0
    
    if dist_to_left < platform_margin:
        move_x += BALL_SPEED * AI_SPEED * edge_force
    if dist_to_right < platform_margin:
        move_x -= BALL_SPEED * AI_SPEED * edge_force
    if dist_to_top < platform_margin:
        move_y += BALL_SPEED * AI_SPEED * edge_force
    if dist_to_bottom < platform_margin:
        move_y -= BALL_SPEED * AI_SPEED * edge_force
    
    # Check if player has powerup
    player_has_powerup = player_ball['powerup'] is not None
    
    if player_has_powerup and dist_to_player < 350:  # Increased detection range
        # Calculate center of platform
        platform_center_x = PLATFORM_X + PLATFORM_SIZE / 2
        platform_center_y = PLATFORM_Y + PLATFORM_SIZE / 2
        
        # Vector from AI to platform center
        to_center_x = platform_center_x - ai_ball['x']
        to_center_y = platform_center_y - ai_ball['y']
        to_center_length = math.sqrt(to_center_x**2 + to_center_y**2)
        
        if to_center_length > 0:
            # Normalize vector to center
            to_center_x /= to_center_length
            to_center_y /= to_center_length
            
            # Calculate escape direction that keeps AI more central
            escape_x = -dx / dist_to_player
            escape_y = -dy / dist_to_player
            
            # Blend escape vector with center-seeking vector
            edge_proximity = min(1.0, (platform_margin * 2) / min(dist_to_left, dist_to_right, dist_to_top, dist_to_bottom))
            center_weight = 0.7 * edge_proximity  # Increase center-seeking when near edges
            
            move_x = (escape_x * (1 - center_weight) + to_center_x * center_weight) * BALL_SPEED * AI_SPEED * 2
            move_y = (escape_y * (1 - center_weight) + to_center_y * center_weight) * BALL_SPEED * AI_SPEED * 2
            
            # Extra evasion for dangerous powerups
            if player_ball['powerup'] in ['heavy', 'grow', 'tron']:
                move_x *= 1.8
                move_y *= 1.8
    else:
        # Normal behavior when player doesn't have powerup
        # Check for powerups - now always interested regardless of distance
        closest_powerup = None
        closest_powerup_dist = float('inf')
        
        for powerup in powerups:
            px = powerup['x'] - ai_ball['x']
            py = powerup['y'] - ai_ball['y']
            powerup_dist = math.sqrt(px*px + py*py)
            
            if powerup_dist < closest_powerup_dist:
                closest_powerup_dist = powerup_dist
                closest_powerup = powerup
        
        # Decide whether to chase powerup or player
        if closest_powerup and random.random() < AI_POWERUP_PRIORITY:
            # Go for powerup with speed based on distance
            speed_multiplier = min(1.5, 0.5 + (closest_powerup_dist / 400))
            
            if closest_powerup['x'] > ai_ball['x']:
                move_x += BALL_SPEED * AI_SPEED * speed_multiplier
            if closest_powerup['x'] < ai_ball['x']:
                move_x -= BALL_SPEED * AI_SPEED * speed_multiplier
            if closest_powerup['y'] > ai_ball['y']:
                move_y += BALL_SPEED * AI_SPEED * speed_multiplier
            if closest_powerup['y'] < ai_ball['y']:
                move_y -= BALL_SPEED * AI_SPEED * speed_multiplier
        else:
            # Chase player aggressively
            predicted_x = player_ball['x'] + player_ball['vx'] * 5
            predicted_y = player_ball['y'] + player_ball['vy'] * 5
            dx_pred = predicted_x - ai_ball['x']
            dy_pred = predicted_y - ai_ball['y']
            
            if dx_pred > 0:
                move_x += BALL_SPEED * AI_SPEED
            if dx_pred < 0:
                move_x -= BALL_SPEED * AI_SPEED
            if dy_pred > 0:
                move_y += BALL_SPEED * AI_SPEED
            if dy_pred < 0:
                move_y -= BALL_SPEED * AI_SPEED
    
    # Apply movement with increased acceleration
    ai_ball['vx'] += move_x * AI_ACCELERATION
    ai_ball['vy'] += move_y * AI_ACCELERATION

def apply_physics(ball):
    old_x, old_y = ball['x'], ball['y']
    
    if ball.get('frozen', False):
        ball['vx'] *= FRICTION * 0.95
        ball['vy'] *= FRICTION * 0.95
    else:
        ball['vx'] *= FRICTION
        ball['vy'] *= FRICTION
    
    ball['x'] += ball['vx']
    ball['y'] += ball['vy']
    
    # Update tron trail if active
    if ball['powerup'] == 'tron':
        # Get last trail segment
        if ball['tron_trail']:
            last_segment = ball['tron_trail'][-1]
            # Update end point of last segment
            last_segment['end'] = (ball['x'], ball['y'])
            
            # If we've moved far enough, start a new segment
            dx = ball['x'] - last_segment['start'][0]
            dy = ball['y'] - last_segment['start'][1]
            if math.sqrt(dx*dx + dy*dy) > 20:  # Minimum segment length
                ball['tron_trail'].append({
                    'start': (ball['x'], ball['y']),
                    'end': (ball['x'], ball['y']),
                    'color': ball['colors'][2]  # Use the brightest color of the ball
                })

def spawn_powerup():
    """Spawn a random powerup on the platform"""
    powerup_types = ['grow', 'shrink', 'shield', 'freeze', 'heavy', 'tron']
    powerup_colors = {
        'grow': [DARKER_YELLOW, YELLOW, LIGHT_YELLOW],
        'shrink': [DARKER_GREEN, GREEN, LIGHT_GREEN],
        'shield': [DARKER_PURPLE, PURPLE, LIGHT_PURPLE],
        'freeze': [DARKEST_LIGHT_BLUE, DARKER_LIGHT_BLUE, LIGHT_BLUE],
        'heavy': [DARK_GRAY, GRAY, WHITE],
        'tron': [DARKER_TEAL, DARK_TEAL, TEAL]
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
    current_time = pygame.time.get_ticks()
    
    for powerup in powerups:
        x, y = powerup['x'], powerup['y']
        
        if powerup['type'] == 'heavy':
            # Pulse between black and white
            pulse = (math.sin(current_time * 0.01) + 1) / 2
            color1 = interpolate_color(BLACK, WHITE, pulse)
            color2 = interpolate_color(DARK_GRAY, WHITE, pulse)
            color3 = interpolate_color(GRAY, WHITE, pulse)
            colors = [color1, color2, color3]
        else:
            colors = powerup['colors']
        
        # Draw shadow
        pygame.draw.circle(screen, BLACK, (x, y), POWERUP_SIZE + 2)
        
        # Draw main circles with gradient effect
        for i, color in enumerate(colors):
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
    
    if powerup_type == 'tron':
        ball['tron_trail'] = []  # Initialize empty trail
        # Add first trail point with ball's color
        ball['tron_trail'].append({
            'start': (ball['x'], ball['y']),
            'end': (ball['x'], ball['y']),
            'color': ball['colors'][2]  # Use the brightest color of the ball
        })
    elif powerup_type == 'heavy':
        ball['heavy_hit'] = True
    elif powerup_type == 'grow':
        ball['radius'] = BALL_RADIUS * GROW_MULTIPLIER
    elif powerup_type == 'shrink':
        # Shrink all other active balls
        active_balls = get_active_balls()
        for other_ball in active_balls.values():
            if other_ball != ball:
                other_ball['radius'] = BALL_RADIUS * SHRINK_MULTIPLIER
    elif powerup_type == 'freeze':
        # Freeze all other active balls
        active_balls = get_active_balls()
        for other_ball in active_balls.values():
            if other_ball != ball:
                other_ball['frozen'] = True
                other_ball['frozen_end'] = current_time + POWERUP_DURATIONS['freeze']

def check_powerup_expiry(ball):
    """Check if ball's powerup has expired"""
    current_time = pygame.time.get_ticks()
    if ball['powerup'] and current_time >= ball['powerup_end']:
        if ball['powerup'] == 'tron':
            ball['tron_trail'] = []  # Clear trail
        if ball['powerup'] == 'heavy':
            ball['heavy_hit'] = False
        if ball['powerup'] == 'shrink':
            # Restore other balls to normal size
            active_balls = get_active_balls()
            for other_ball in active_balls.values():
                if other_ball != ball:
                    other_ball['radius'] = BALL_RADIUS
        elif ball['powerup'] == 'freeze':
            # Restore other balls from frozen state
            active_balls = get_active_balls()
            for other_ball in active_balls.values():
                if other_ball != ball:
                    other_ball['frozen'] = False
                    other_ball['frozen_end'] = 0
        # Reset ball's powerup
        ball['powerup'] = None
        ball['radius'] = BALL_RADIUS

# Modify check_tron_trail_collision function to fix collision logic
def check_tron_trail_collision(ball):
    """Check if ball has hit any tron trails"""
    active_balls = get_active_balls()
    for other_ball in active_balls.values():
        # Skip if it's the same ball or if the other ball has no trail
        # Also skip if this ball is the one with the tron powerup
        if (other_ball == ball or 
            not other_ball.get('tron_trail') or 
            ball['powerup'] == 'tron'):  # Changed this line to check if the checking ball has tron
            continue
            
        # Check collision with each trail segment
        for segment in other_ball['tron_trail']:
            # Calculate distance from point (ball center) to line segment
            x1, y1 = segment['start']
            x2, y2 = segment['end']
            
            # Vector from line start to end
            line_vec = (x2 - x1, y2 - y1)
            # Vector from line start to ball
            ball_vec = (ball['x'] - x1, ball['y'] - y1)
            line_length = math.sqrt(line_vec[0]**2 + line_vec[1]**2)
            
            if line_length == 0:
                continue
                
            # Normalize line vector
            unit_line = (line_vec[0]/line_length, line_vec[1]/line_length)
            
            # Project ball vector onto line vector
            proj_length = ball_vec[0]*unit_line[0] + ball_vec[1]*unit_line[1]
            
            # Get closest point on line segment
            if proj_length < 0:
                closest = (x1, y1)
            elif proj_length > line_length:
                closest = (x2, y2)
            else:
                closest = (x1 + unit_line[0]*proj_length, 
                         y1 + unit_line[1]*proj_length)
            
            # Check distance from ball to closest point
            dx = ball['x'] - closest[0]
            dy = ball['y'] - closest[1]
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < ball['radius']:
                # Collision detected - bounce the ball
                normal = (dx/distance, dy/distance)
                ball['vx'] = normal[0] * abs(ball['vx'] + ball['vy'])
                ball['vy'] = normal[1] * abs(ball['vx'] + ball['vy'])
                collision_sound.play()
                return

# Modify the game loop to allow replaying
def game_loop():
    global score
    while True:
        score = {'red': 0, 'blue': 0, 'orange': 0, 'purple': 0, 'ai': 0}  # Added 'ai' score
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

# Add helper function for color interpolation
def interpolate_color(color1, color2, factor):
    """Interpolate between two colors"""
    return tuple(int(c1 + (c2 - c1) * factor) for c1, c2 in zip(color1, color2))

# Replace the final lines with:
game_loop()