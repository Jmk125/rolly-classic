import pygame
import sys
from pygame.locals import QUIT, KEYDOWN, K_RETURN
import time
import math
import random

# Initialize Pygame
pygame.init()

# Initialize controllers
pygame.joystick.init()
controllers = []


def init_controllers():
    """Initialize all connected controllers"""
    global controllers
    controllers = []
    for i in range(pygame.joystick.get_count()):
        controller = pygame.joystick.Joystick(i)
        controller.init()
        controllers.append(controller)
        print(f"Controller {i + 1} connected: {controller.get_name()}")
    return len(controllers)


def check_for_new_controllers():
    """Check if controllers have been connected/disconnected"""
    current_count = pygame.joystick.get_count()
    if current_count != len(controllers):
        return init_controllers()
    return len(controllers)


def get_controller_input(controller_index):
    """Get analog stick input from a controller"""
    if controller_index >= len(controllers):
        return 0, 0

    try:
        controller = controllers[controller_index]
        x_axis = controller.get_axis(0)  # Left stick X axis
        y_axis = controller.get_axis(1)  # Left stick Y axis

        # Apply deadzone
        deadzone = 0.15
        if abs(x_axis) < deadzone:
            x_axis = 0
        if abs(y_axis) < deadzone:
            y_axis = 0

        return x_axis, y_axis
    except BaseException:
        return 0, 0


def handle_controller_menu_input():
    """Process controller input for menu navigation"""
    for controller in controllers:
        try:
            # D-pad/analog for navigation
            y_axis = controller.get_axis(1)
            x_axis = controller.get_axis(0)

            # Get D-pad input if available
            hat_y = 0
            hat_x = 0
            if controller.get_numhats() > 0:
                hat_x, hat_y = controller.get_hat(0)

            if y_axis < -0.5 or hat_y > 0:
                return "UP"
            elif y_axis > 0.5 or hat_y < 0:
                return "DOWN"
            elif x_axis < -0.5 or hat_x < 0:
                return "LEFT"
            elif x_axis > 0.5 or hat_x > 0:
                return "RIGHT"

            # A button (0) or Start button (7) to confirm
            if controller.get_button(0) or controller.get_button(7):
                return "SELECT"
        except BaseException:
            continue

    return None


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
pygame.display.set_caption("Rolly V0.51 with Controller Support & Co-op")
clock = pygame.time.Clock()

# Fonts
pygame.font.init()
title_font = pygame.font.Font(None, 150)  # Large font for the title
# Smaller font for menu options (changed from 50)
subtitle_font = pygame.font.Font(None, 40)
score_font = pygame.font.Font(None, 40)  # Font for score-keeping
# Small font for controller indicators
controller_font = pygame.font.Font(None, 24)

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
# Slow, Normal, Fast (in milliseconds)
POWERUP_INTERVALS = [30000, 15000, 7500]
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

# Add after other constants - UPDATE: Added Co-op mode
GAME_MODES = ["Normal", "Last Standing", "Co-op"]
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

# --- Co-op mode variables ---
coop_level = 1
coop_ai_balls = []  # List to store multiple AI balls in co-op mode
eliminated_players = set()  # Keep track of eliminated players in current level
MAX_AI_BALLS = 10  # Maximum number of AI balls (maximum level)

# AI ball colors with variations for higher levels
AI_COLORS = [
    [AI_DARKER_GRAY, AI_DARK_GRAY, AI_GRAY],  # Level 1
    [AI_DARKER_GRAY, AI_DARK_GRAY, (100, 100, 100)],  # Level 2
    [AI_DARKER_GRAY, (70, 70, 70), (120, 120, 120)],  # Level 3
    [(20, 20, 20), (80, 80, 80), (140, 140, 140)],  # Level 4
    [(30, 30, 30), (90, 90, 90), (150, 150, 150)],  # Level 5
    [(40, 40, 40), (100, 100, 100), (160, 160, 160)],  # Level 6
    [(25, 25, 25), (85, 85, 85), (145, 145, 145)],  # Level 7
    [(35, 35, 35), (95, 95, 95), (155, 155, 155)],  # Level 8
    [(45, 45, 45), (105, 105, 105), (165, 165, 165)],  # Level 9
    [(50, 50, 50), (110, 110, 110), (170, 170, 170)],  # Level 10
]

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
            # Player in top-left
            'red': (PLATFORM_X + margin, PLATFORM_Y + margin),
            'ai': (PLATFORM_X + selected_platform_size - margin,
                   PLATFORM_Y + selected_platform_size - margin)  # AI in bottom-right
        }
    elif selected_player_count == 2:
        # Diagonal corners for 2 players (top-left and bottom-right)
        return {
            'red': (PLATFORM_X + margin, PLATFORM_Y + margin),  # Top-left
            'blue': (PLATFORM_X + selected_platform_size - margin,
                     PLATFORM_Y + selected_platform_size - margin),  # Bottom-right
            # Bottom-left (unused)
            'orange': (PLATFORM_X + margin, PLATFORM_Y + selected_platform_size - margin),
            # Top-right (unused)
            'purple': (PLATFORM_X + selected_platform_size - margin, PLATFORM_Y + margin)
        }
    else:
        # All corners for 3-4 players
        return {
            'red': (PLATFORM_X + margin, PLATFORM_Y + margin),  # Top-left
            # Top-right
            'blue': (PLATFORM_X + selected_platform_size - margin, PLATFORM_Y + margin),
            # Bottom-left
            'orange': (PLATFORM_X + margin, PLATFORM_Y + selected_platform_size - margin),
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
                ball['spawn_immunity_end'] = current_time + \
                    SPAWN_IMMUNITY_DURATION
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

        # Skip the ready screen for Co-op mode
        if (selected_player_count <= 2 or selected_game_mode ==
                "Last Standing") and selected_game_mode != "Co-op":
            # Draw current state
            screen.fill(BACKGROUND_COLOR)
            draw_platform()
            for ball in get_active_balls().values():
                draw_ball(ball)
            draw_scores()
            draw_text_with_outline(
                "Ready...",
                subtitle_font,
                WIDTH // 2,
                HEIGHT // 2,
                WHITE,
                BLACK,
                center=True)
            pygame.display.flip()
            pygame.time.wait(1000)  # 1 second pause

        # Add brief pause in 1-player, 2-player mode or Last Standing mode
        if selected_player_count <= 2 or selected_game_mode == "Last Standing":
            # Draw current state
            screen.fill(BACKGROUND_COLOR)
            draw_platform()
            for ball in get_active_balls().values():
                draw_ball(ball)
            draw_scores()
            draw_text_with_outline(
                "Ready...",
                subtitle_font,
                WIDTH // 2,
                HEIGHT // 2,
                WHITE,
                BLACK,
                center=True)
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
        if ball['pos']['x'] - BALL_RADIUS <= 0 or ball['pos']['x'] + \
                BALL_RADIUS >= WIDTH:
            ball['vel']['x'] *= -1
        if ball['pos']['y'] - BALL_RADIUS <= 0 or ball['pos']['y'] + \
                BALL_RADIUS >= HEIGHT:
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

    # Initialize controllers
    init_controllers()
    last_controller_input = pygame.time.get_ticks()
    controller_repeat_delay = 200  # ms between controller input repeats

    # Initialize bouncing balls with different starting positions and
    # velocities
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
            # Orange/Yellow ball
            'colors': [DARKER_ORANGE, DARK_ORANGE, ORANGE],
            'elapsed': 0
        },
        {
            'pos': {'x': WIDTH * 3 // 4, 'y': HEIGHT * 3 // 4},
            'vel': {'x': -0.3, 'y': -0.2},
            # Purple ball
            'colors': [DARKER_PLAYER_PURPLE, DARK_PLAYER_PURPLE, PLAYER_PURPLE],
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
            # Red, Blue, and Orange/Yellow
            return [balls[0], balls[1], balls[2]]
        else:
            # Red, Blue, Orange/Yellow, and Purple
            return [balls[0], balls[1], balls[2], balls[3]]

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
                    selected_option = (
                        selected_option - 1) % 5  # Now 5 options
                elif event.key == pygame.K_DOWN:
                    selected_option = (
                        selected_option + 1) % 5  # Now 5 options
                elif event.key == pygame.K_LEFT:
                    if selected_option == 0:  # Players
                        selected_player_index = (
                            selected_player_index - 1) % len(PLAYER_COUNTS)
                        selected_player_count = PLAYER_COUNTS[selected_player_index]
                        if selected_player_count == 2:
                            selected_game_mode = "Normal"  # Force normal mode for 2 players
                    elif selected_option == 1:  # Game Mode
                        if selected_player_count > 1:  # Allow mode change for 2+ players, including Co-op
                            selected_mode_index = (
                                selected_mode_index - 1) % len(GAME_MODES)
                            selected_game_mode = GAME_MODES[selected_mode_index]
                            # Force normal mode if Last Standing with only 2
                            # players
                            if selected_player_count == 2 and selected_game_mode == "Last Standing":
                                selected_game_mode = "Normal"
                    elif selected_option == 2:  # Score
                        if selected_game_mode != "Co-op":  # Only allow changing score in non-Co-op modes
                            selected_score_index = (
                                selected_score_index - 1) % len(WIN_SCORES)
                            selected_win_score = WIN_SCORES[selected_score_index]
                    elif selected_option == 3:  # Platform
                        selected_platform_index = (
                            selected_platform_index - 1) % len(PLATFORM_SIZES)
                        selected_platform_size = PLATFORM_SIZES[selected_platform_index]
                    else:  # Powerup speed
                        selected_powerup_index = (
                            selected_powerup_index - 1) % len(POWERUP_INTERVALS)
                        selected_powerup_interval = POWERUP_INTERVALS[selected_powerup_index]
                elif event.key == pygame.K_RIGHT:
                    if selected_option == 0:  # Players
                        selected_player_index = (
                            selected_player_index + 1) % len(PLAYER_COUNTS)
                        selected_player_count = PLAYER_COUNTS[selected_player_index]
                        if selected_player_count == 2:
                            selected_game_mode = "Normal"  # Force normal mode for 2 players
                    elif selected_option == 1:  # Game Mode
                        if selected_player_count > 1:  # Allow mode change for 2+ players, including Co-op
                            selected_mode_index = (
                                selected_mode_index + 1) % len(GAME_MODES)
                            selected_game_mode = GAME_MODES[selected_mode_index]
                            # Force normal mode if Last Standing with only 2
                            # players
                            if selected_player_count == 2 and selected_game_mode == "Last Standing":
                                selected_game_mode = "Normal"
                    elif selected_option == 2:  # Score
                        if selected_game_mode != "Co-op":  # Only allow changing score in non-Co-op modes
                            selected_score_index = (
                                selected_score_index + 1) % len(WIN_SCORES)
                            selected_win_score = WIN_SCORES[selected_score_index]
                    elif selected_option == 3:  # Platform
                        selected_platform_index = (
                            selected_platform_index + 1) % len(PLATFORM_SIZES)
                        selected_platform_size = PLATFORM_SIZES[selected_platform_index]
                    else:  # Powerup speed
                        selected_powerup_index = (
                            selected_powerup_index + 1) % len(POWERUP_INTERVALS)
                        selected_powerup_interval = POWERUP_INTERVALS[selected_powerup_index]

        # Handle controller input with repeat delay
        if current_time - last_controller_input > controller_repeat_delay:
            controller_action = handle_controller_menu_input()
            if controller_action:
                last_controller_input = current_time

                if controller_action == "UP":
                    selected_option = (selected_option - 1) % 5
                elif controller_action == "DOWN":
                    selected_option = (selected_option + 1) % 5
                elif controller_action == "LEFT":
                    if selected_option == 0:  # Players
                        selected_player_index = (
                            selected_player_index - 1) % len(PLAYER_COUNTS)
                        selected_player_count = PLAYER_COUNTS[selected_player_index]
                        if selected_player_count == 2:
                            selected_game_mode = "Normal"  # Force normal mode for 2 players
                    elif selected_option == 1:  # Game Mode
                        if selected_player_count > 1:  # Allow mode change for 2+ players, including Co-op
                            selected_mode_index = (
                                selected_mode_index - 1) % len(GAME_MODES)
                            selected_game_mode = GAME_MODES[selected_mode_index]
                            # Force normal mode if Last Standing with only 2
                            # players
                            if selected_player_count == 2 and selected_game_mode == "Last Standing":
                                selected_game_mode = "Normal"
                    elif selected_option == 2:  # Score
                        selected_score_index = (
                            selected_score_index - 1) % len(WIN_SCORES)
                        selected_win_score = WIN_SCORES[selected_score_index]
                    elif selected_option == 3:  # Platform
                        selected_platform_index = (
                            selected_platform_index - 1) % len(PLATFORM_SIZES)
                        selected_platform_size = PLATFORM_SIZES[selected_platform_index]
                    else:  # Powerup speed
                        selected_powerup_index = (
                            selected_powerup_index - 1) % len(POWERUP_INTERVALS)
                        selected_powerup_interval = POWERUP_INTERVALS[selected_powerup_index]
                elif controller_action == "RIGHT":
                    if selected_option == 0:  # Players
                        selected_player_index = (
                            selected_player_index + 1) % len(PLAYER_COUNTS)
                        selected_player_count = PLAYER_COUNTS[selected_player_index]
                        if selected_player_count == 2:
                            selected_game_mode = "Normal"  # Force normal mode for 2 players
                    elif selected_option == 1:  # Game Mode
                        if selected_player_count > 1:  # Allow mode change for 2+ players, including Co-op
                            selected_mode_index = (
                                selected_mode_index + 1) % len(GAME_MODES)
                            selected_game_mode = GAME_MODES[selected_mode_index]
                            # Force normal mode if Last Standing with only 2
                            # players
                            if selected_player_count == 2 and selected_game_mode == "Last Standing":
                                selected_game_mode = "Normal"
                    elif selected_option == 2:  # Score
                        selected_score_index = (
                            selected_score_index + 1) % len(WIN_SCORES)
                        selected_win_score = WIN_SCORES[selected_score_index]
                    elif selected_option == 3:  # Platform
                        selected_platform_index = (
                            selected_platform_index + 1) % len(PLATFORM_SIZES)
                        selected_platform_size = PLATFORM_SIZES[selected_platform_index]
                    else:  # Powerup speed
                        selected_powerup_index = (
                            selected_powerup_index + 1) % len(POWERUP_INTERVALS)
                        selected_powerup_interval = POWERUP_INTERVALS[selected_powerup_index]
                elif controller_action == "SELECT":
                    if selected_player_count == 2 and selected_game_mode == "Last Standing":
                        selected_game_mode = "Normal"
                    update_platform_position()
                    return

        screen.fill(BACKGROUND_COLOR)

        # Animate the bouncing balls with current player count
        animate_title_balls(get_active_title_balls(selected_player_count),
                            len(get_active_title_balls(selected_player_count)))

        # Draw title
        draw_text_with_outline(
            "ROLLY",
            title_font,
            WIDTH // 2,
            HEIGHT // 4,
            RED,
            BLACK,
            center=True)

        # Draw options
        y_start = HEIGHT // 2 - 100  # Adjusted to accommodate new option
        spacing = 50

        # Player count (option 0)
        color = WHITE if selected_option == 0 else GRAY
        player_text = f"{selected_player_count} Players"
        draw_text_with_outline(
            player_text,
            subtitle_font,
            WIDTH // 2,
            y_start,
            color,
            BLACK,
            center=True)

        # Game Mode (option 1)
        color = WHITE if selected_option == 1 else GRAY
        # Only grey out Last Standing for 2 players, Co-op is always available
        # for 2+ players
        mode_color = GRAY if (
            selected_player_count == 2 and selected_game_mode == "Last Standing") else color
        mode_text = f"Mode: {selected_game_mode}"
        draw_text_with_outline(
            mode_text,
            subtitle_font,
            WIDTH // 2,
            y_start + spacing,
            mode_color,
            BLACK,
            center=True)

        # Win score (option 2)
        color = WHITE if selected_option == 2 and selected_game_mode != "Co-op" else GRAY
        score_text = f"First to {selected_win_score} points"
        if selected_game_mode == "Co-op":
            score_text = "Co-op Mode: Survive As Long As Possible"
        draw_text_with_outline(
            score_text,
            subtitle_font,
            WIDTH // 2,
            y_start + spacing * 2,
            color,
            BLACK,
            center=True)

        # Platform size (option 3)
        color = WHITE if selected_option == 3 else GRAY
        size_names = {400: "Small", 600: "Medium", 700: "Large"}
        platform_text = f"Platform: {size_names[selected_platform_size]}"
        draw_text_with_outline(
            platform_text,
            subtitle_font,
            WIDTH // 2,
            y_start + spacing * 3,
            color,
            BLACK,
            center=True)

        # Powerup speed (option 4)
        color = WHITE if selected_option == 4 else GRAY
        speed_names = {30000: "Slow", 15000: "Normal", 7500: "Fast"}
        powerup_text = f"Powerup Speed: {
            speed_names[selected_powerup_interval]}"
        draw_text_with_outline(
            powerup_text,
            subtitle_font,
            WIDTH // 2,
            y_start + spacing * 4,
            color,
            BLACK,
            center=True)

        # Draw controls hint
        controls_text = "UP DOWN to select | LEFT RIGHT to change | Enter to start"
        draw_text_with_outline(
            controls_text,
            subtitle_font,
            WIDTH // 2,
            HEIGHT * 3 // 4,
            GRAY,
            BLACK,
            center=True)

        # Draw controller status
        if len(controllers) > 0:
            controller_text = f"{len(controllers)} Controller(s) connected"
            draw_text_with_outline(
                controller_text,
                subtitle_font,
                WIDTH // 2,
                HEIGHT * 4 // 5,
                WHITE,
                BLACK,
                center=True)

        pygame.display.flip()
        clock.tick(FPS)


def show_start_message():
    screen.fill(BACKGROUND_COLOR)
    draw_text_with_outline(
        "Start!",
        title_font,
        WIDTH // 2,
        HEIGHT // 2,
        WHITE,
        BLACK,
        center=True)
    pygame.display.flip()
    time.sleep(1)


def move_ball(ball, keys, up, down, left, right, controller_index=-1):
    """Move ball using keyboard or controller input"""
    if ball.get('frozen', False):
        return  # Don't move if frozen

    # Keyboard input
    if keys[up]:
        ball['vy'] -= BALL_SPEED
    if keys[down]:
        ball['vy'] += BALL_SPEED
    if keys[left]:
        ball['vx'] -= BALL_SPEED
    if keys[right]:
        ball['vx'] += BALL_SPEED

    # Controller input
    if controller_index >= 0 and controller_index < len(controllers):
        x_axis, y_axis = get_controller_input(controller_index)
        # Slightly higher sensitivity for controller
        ball['vx'] += x_axis * BALL_SPEED * 1.5
        ball['vy'] += y_axis * BALL_SPEED * 1.5


def draw_controller_indicators():
    """Show which controller is assigned to which player"""
    active_balls = get_active_balls()

    if len(controllers) > 0 and 'red' in active_balls:
        controller_text = "🎮1"
        draw_text_with_outline(controller_text, controller_font,
                               55, 15, RED, BLACK, center=True)

    if len(controllers) > 1 and 'blue' in active_balls:
        controller_text = "🎮2"
        draw_text_with_outline(controller_text, controller_font,
                               WIDTH - 60, 15, BLUE, BLACK, center=True)

    if len(controllers) > 2 and 'orange' in active_balls:
        controller_text = "🎮3"
        draw_text_with_outline(controller_text, controller_font,
                               55, HEIGHT - 15, ORANGE, BLACK, center=True)

    if len(controllers) > 3 and 'purple' in active_balls:
        controller_text = "🎮4"
        draw_text_with_outline(
            controller_text,
            controller_font,
            WIDTH - 60,
            HEIGHT - 15,
            PLAYER_PURPLE,
            BLACK,
            center=True)


def main_game():
    global powerups, last_powerup_spawn

    # Special handling for Co-op mode
    if selected_game_mode == "Co-op":
        coop_game()
        return

    # Reset game state
    reset_balls()
    powerups = []
    last_powerup_spawn = pygame.time.get_ticks()
    active_balls = get_active_balls()

    # Check for controllers periodically
    controller_check_time = pygame.time.get_ticks()

    while True:
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        # Check for controller changes every few seconds
        if current_time - controller_check_time > 3000:
            check_for_new_controllers()
            controller_check_time = current_time

        # Handle player movements based on active balls
        if 'red' in active_balls:
            move_ball(
                red_ball,
                keys,
                pygame.K_w,
                pygame.K_s,
                pygame.K_a,
                pygame.K_d,
                0)  # Controller 0 for Red

        if 'blue' in active_balls:
            move_ball(
                blue_ball,
                keys,
                pygame.K_UP,
                pygame.K_DOWN,
                pygame.K_LEFT,
                pygame.K_RIGHT,
                1 if len(controllers) > 1 else -
                1)  # Controller 1 for Blue if available

        if 'orange' in active_balls:
            move_ball(
                orange_ball,
                keys,
                pygame.K_i,
                pygame.K_k,
                pygame.K_j,
                pygame.K_l,
                2 if len(controllers) > 2 else -
                1)  # Controller 2 for Orange if available

        if 'purple' in active_balls:
            move_ball(
                purple_ball,
                keys,
                pygame.K_KP8,
                pygame.K_KP5,
                pygame.K_KP4,
                pygame.K_KP6,
                3 if len(controllers) > 3 else -
                1)  # Controller 3 for Purple if available

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
                        # Ball fell off by itself - give point to all other
                        # players
                        other_players = [
                            c for c in active_balls.keys() if c != color]
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
            if ball.get(
                    'frozen',
                    False) and current_time >= ball.get(
                    'frozen_end',
                    0):
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

        # Draw controller indicators if controllers are connected
        if len(controllers) > 0:
            draw_controller_indicators()

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

        # Also allow controller buttons to skip the winner screen
        if current_time - start_time > 1000:  # Prevent immediate skip
            for i in range(len(controllers)):
                if controllers[i].get_button(
                        0) or controllers[i].get_button(7):  # A or Start button
                    waiting = False
                    break

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
            draw_text_with_outline(
                f"{winner} Wins!",
                title_font,
                WIDTH // 2,
                HEIGHT // 3,
                winner_color,
                BLACK,
                center=True)

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
                draw_text_with_outline(
                    "Press Enter or Controller Button to Play Again",
                    subtitle_font,
                    WIDTH // 2,
                    HEIGHT * 4 // 5,
                    WHITE,
                    BLACK,
                    center=True)

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
        if knockback2 > 0 or ball1.get(
                'heavy_hit', False):  # If ball1 affected ball2
            ball2['last_hit_by'] = ball1
        if knockback1 > 0 or ball2.get(
                'heavy_hit', False):  # If ball2 affected ball1
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
    pygame.draw.rect(
        screen,
        GRAY,
        (PLATFORM_X,
         PLATFORM_Y,
         PLATFORM_SIZE,
         PLATFORM_SIZE))


def draw_ball(ball):
    """Draw a ball with a glossy reflective look and trail effect if shielded."""
    x, y = int(ball['x']), int(ball['y'])
    radius = int(ball['radius'])
    current_time = pygame.time.get_ticks()

    # Initialize trail if it doesn't exist
    if 'trail' not in ball:
        ball['trail'] = []

    # Draw trail if ball has shield powerup or was recently hit
    if ball['powerup'] == 'shield' or ball.get(
            'hit_flash_start', 0) > current_time - 1000:
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
        for ghost in ball['trail'][:-
                                   1]:  # Don't draw ghost at current position
            # Calculate how long this ghost has existed
            age = (current_time - ghost['time']) / 1000.0  # Convert to seconds

            # Calculate alpha based on age
            alpha = int(ghost['initial_alpha'] * (TRAIL_FADE ** (age * 5)))

            if alpha > 0:
                # Create a surface for this trail segment
                trail_surface = pygame.Surface(
                    (radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)

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
        flash = (math.sin(current_time * 0.02) + 1) / \
            2  # Faster pulse than powerup
        outline_color = interpolate_color(BLACK, WHITE, flash)
        pygame.draw.circle(screen, outline_color, (x, y), radius + 3)
    else:
        pygame.draw.circle(screen, BLACK, (x, y), radius + 3)

    # Draw the main ball
    for i, color in enumerate(ball['colors']):
        pygame.draw.circle(screen, color, (x, y), radius - i * 5)
    pygame.draw.circle(
        screen,
        WHITE,
        (x - radius // 3,
         y - radius // 3),
        radius // 4)  # Highlight

    # Draw tron trail if active
    if ball['powerup'] == 'tron' and ball['tron_trail']:
        for segment in ball['tron_trail']:
            pygame.draw.line(
                screen, segment['color'], segment['start'], segment['end'], int(
                    ball['radius']))  # Changed to radius instead of diameter


def draw_scores():
    """Draw the scores with a black outline."""
    active_balls = get_active_balls()
    if 'red' in active_balls:
        draw_text_with_outline(
            f"Red: {
                score['red']}",
            score_font,
            10,
            10,
            RED,
            BLACK,
            center=False)
    if 'ai' in active_balls:
        draw_text_with_outline(
            f"Black: {
                score['ai']}",
            score_font,
            WIDTH - 150,
            10,
            AI_GRAY,
            BLACK,
            center=False)
    elif 'blue' in active_balls:
        draw_text_with_outline(
            f"Blue: {
                score['blue']}",
            score_font,
            WIDTH - 150,
            10,
            BLUE,
            BLACK,
            center=False)
    if 'orange' in active_balls:
        draw_text_with_outline(
            f"Orange: {
                score['orange']}",
            score_font,
            10,
            HEIGHT - 30,
            ORANGE,
            BLACK,
            center=False)
    if 'purple' in active_balls:
        draw_text_with_outline(
            f"Purple: {
                score['purple']}",
            score_font,
            WIDTH - 150,
            HEIGHT - 30,
            PLAYER_PURPLE,
            BLACK,
            center=False)


def get_active_balls():
    """Return dictionary of active balls based on player count and game mode"""
    if selected_game_mode == "Co-op":
        # In Co-op mode, only return human players that aren't eliminated
        balls = {}
        if 'red' not in eliminated_players:
            balls['red'] = red_ball
        if selected_player_count >= 2 and 'blue' not in eliminated_players:
            balls['blue'] = blue_ball
        if selected_player_count >= 3 and 'orange' not in eliminated_players:
            balls['orange'] = orange_ball
        if selected_player_count >= 4 and 'purple' not in eliminated_players:
            balls['purple'] = purple_ball
        return balls
    elif selected_player_count == 1:
        return {'red': red_ball, 'ai': ai_ball}
    balls = {'red': red_ball, 'blue': blue_ball}
    if selected_player_count >= 3:
        balls['orange'] = orange_ball
    if selected_player_count >= 4:
        balls['purple'] = purple_ball
    return balls


def move_ai_ball(ai_ball, player_ball, current_time):
    """Control AI ball movement"""
    if ai_ball.get('frozen', False):
        return

    dx = player_ball['x'] - ai_ball['x']
    dy = player_ball['y'] - ai_ball['y']
    dist_to_player = math.sqrt(dx * dx + dy * dy)

    # Initialize movement vector
    move_x = 0
    move_y = 0

    # Platform edge awareness
    dist_to_left = ai_ball['x'] - PLATFORM_X
    dist_to_right = PLATFORM_X + PLATFORM_SIZE - ai_ball['x']
    dist_to_top = ai_ball['y'] - PLATFORM_Y
    dist_to_bottom = PLATFORM_Y + PLATFORM_SIZE - ai_ball['y']

    # Strong edge avoidance - increased margin and force when player has
    # powerup
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
            edge_proximity = min(1.0,
                                 (platform_margin * 2) / min(dist_to_left,
                                                             dist_to_right,
                                                             dist_to_top,
                                                             dist_to_bottom))
            center_weight = 0.7 * edge_proximity  # Increase center-seeking when near edges

            move_x = (escape_x * (1 - center_weight) + to_center_x *
                      center_weight) * BALL_SPEED * AI_SPEED * 2
            move_y = (escape_y * (1 - center_weight) + to_center_y *
                      center_weight) * BALL_SPEED * AI_SPEED * 2

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
            powerup_dist = math.sqrt(px * px + py * py)

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


def move_ai_ball_coop(ai_ball, player_ball, current_time):
    """AI movement logic specifically for Co-op mode, modified from move_ai_ball"""
    if ai_ball.get('frozen', False):
        return

    # Get speed multiplier based on level
    speed_mult = ai_ball.get('speed_multiplier', 1.0)

    dx = player_ball['x'] - ai_ball['x']
    dy = player_ball['y'] - ai_ball['y']
    dist_to_player = math.sqrt(dx * dx + dy * dy)

    # Initialize movement vector
    move_x = 0
    move_y = 0

    # Platform edge awareness
    dist_to_left = ai_ball['x'] - PLATFORM_X
    dist_to_right = PLATFORM_X + PLATFORM_SIZE - ai_ball['x']
    dist_to_top = ai_ball['y'] - PLATFORM_Y
    dist_to_bottom = PLATFORM_Y + PLATFORM_SIZE - ai_ball['y']

    # Edge avoidance
    platform_margin = AI_PLATFORM_MARGIN
    edge_force = 3.0

    if dist_to_left < platform_margin:
        move_x += BALL_SPEED * AI_SPEED * edge_force
    if dist_to_right < platform_margin:
        move_x -= BALL_SPEED * AI_SPEED * edge_force
    if dist_to_top < platform_margin:
        move_y += BALL_SPEED * AI_SPEED * edge_force
    if dist_to_bottom < platform_margin:
        move_y -= BALL_SPEED * AI_SPEED * edge_force

    # Player has powerup - be more cautious
    player_has_powerup = player_ball['powerup'] is not None

    if player_has_powerup and dist_to_player < 300:
        # Be more cautious around powered-up players
        if player_ball['powerup'] in ['heavy', 'grow', 'tron']:
            # These are dangerous - run away
            if dist_to_player > 0:
                move_x -= (dx / dist_to_player) * BALL_SPEED * \
                    AI_SPEED * 1.5 * speed_mult
                move_y -= (dy / dist_to_player) * BALL_SPEED * \
                    AI_SPEED * 1.5 * speed_mult
        else:
            # For other powerups, go for a powerup yourself
            closest_powerup = None
            closest_powerup_dist = float('inf')

            for powerup in powerups:
                px = powerup['x'] - ai_ball['x']
                py = powerup['y'] - ai_ball['y']
                powerup_dist = math.sqrt(px * px + py * py)

                if powerup_dist < closest_powerup_dist:
                    closest_powerup_dist = powerup_dist
                    closest_powerup = powerup

            if closest_powerup:
                # Go for closest powerup
                if closest_powerup['x'] > ai_ball['x']:
                    move_x += BALL_SPEED * AI_SPEED * speed_mult
                if closest_powerup['x'] < ai_ball['x']:
                    move_x -= BALL_SPEED * AI_SPEED * speed_mult
                if closest_powerup['y'] > ai_ball['y']:
                    move_y += BALL_SPEED * AI_SPEED * speed_mult
                if closest_powerup['y'] < ai_ball['y']:
                    move_y -= BALL_SPEED * AI_SPEED * speed_mult
            else:
                # No powerups, circle the player
                # 90 degrees offset for circling
                angle = math.atan2(dy, dx) + math.pi / 2
                circle_x = math.cos(angle)
                circle_y = math.sin(angle)
                move_x += circle_x * BALL_SPEED * AI_SPEED * speed_mult
                move_y += circle_y * BALL_SPEED * AI_SPEED * speed_mult
    else:
        # Normal pursuit behavior
        # Check for powerups occasionally
        if random.random() < 0.1:  # 10% chance to look for powerups
            closest_powerup = None
            closest_powerup_dist = float('inf')

            for powerup in powerups:
                px = powerup['x'] - ai_ball['x']
                py = powerup['y'] - ai_ball['y']
                powerup_dist = math.sqrt(px * px + py * py)

                if powerup_dist < closest_powerup_dist:
                    closest_powerup_dist = powerup_dist
                    closest_powerup = powerup

            if closest_powerup and closest_powerup_dist < 200:  # Only go for nearby powerups
                # Go for powerup
                if closest_powerup['x'] > ai_ball['x']:
                    move_x += BALL_SPEED * AI_SPEED * speed_mult
                if closest_powerup['x'] < ai_ball['x']:
                    move_x -= BALL_SPEED * AI_SPEED * speed_mult
                if closest_powerup['y'] > ai_ball['y']:
                    move_y += BALL_SPEED * AI_SPEED * speed_mult
                if closest_powerup['y'] < ai_ball['y']:
                    move_y -= BALL_SPEED * AI_SPEED * speed_mult
            else:
                # Chase player directly with some prediction
                predicted_x = player_ball['x'] + player_ball['vx'] * 5
                predicted_y = player_ball['y'] + player_ball['vy'] * 5
                dx_pred = predicted_x - ai_ball['x']
                dy_pred = predicted_y - ai_ball['y']

                if dx_pred > 0:
                    move_x += BALL_SPEED * AI_SPEED * speed_mult
                if dx_pred < 0:
                    move_x -= BALL_SPEED * AI_SPEED * speed_mult
                if dy_pred > 0:
                    move_y += BALL_SPEED * AI_SPEED * speed_mult
                if dy_pred < 0:
                    move_y -= BALL_SPEED * AI_SPEED * speed_mult
        else:
            # Chase player directly with some prediction
            predicted_x = player_ball['x'] + player_ball['vx'] * 5
            predicted_y = player_ball['y'] + player_ball['vy'] * 5
            dx_pred = predicted_x - ai_ball['x']
            dy_pred = predicted_y - ai_ball['y']

            if dx_pred > 0:
                move_x += BALL_SPEED * AI_SPEED * speed_mult
            if dx_pred < 0:
                move_x -= BALL_SPEED * AI_SPEED * speed_mult
            if dy_pred > 0:
                move_y += BALL_SPEED * AI_SPEED * speed_mult
            if dy_pred < 0:
                move_y -= BALL_SPEED * AI_SPEED * speed_mult

    # Apply movement
    ai_ball['vx'] += move_x * AI_ACCELERATION * speed_mult
    ai_ball['vy'] += move_y * AI_ACCELERATION * speed_mult


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
            if math.sqrt(dx * dx + dy * dy) > 20:  # Minimum segment length
                ball['tron_trail'].append({
                    'start': (ball['x'], ball['y']),
                    'end': (ball['x'], ball['y']),
                    # Use the brightest color of the ball
                    'color': ball['colors'][2]
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
    x = random.randint(
        PLATFORM_X +
        POWERUP_SIZE,
        PLATFORM_X +
        PLATFORM_SIZE -
        POWERUP_SIZE)
    y = random.randint(
        PLATFORM_Y +
        POWERUP_SIZE,
        PLATFORM_Y +
        PLATFORM_SIZE -
        POWERUP_SIZE)

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
        pygame.draw.circle(
            screen,
            WHITE,
            (x - highlight_size,
             y - highlight_size),
            highlight_size)


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
    global coop_ai_balls # Move global declaration to the beginning   

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

        # Also shrink AI balls in Co-op mode
        if selected_game_mode == "Co-op":
            for ai_ball in coop_ai_balls:
                ai_ball['radius'] = BALL_RADIUS * SHRINK_MULTIPLIER
    elif powerup_type == 'freeze':
        # Freeze all other active balls
        active_balls = get_active_balls()
        for other_ball in active_balls.values():
            if other_ball != ball:
                other_ball['frozen'] = True
                other_ball['frozen_end'] = current_time + \
                    POWERUP_DURATIONS['freeze']

        # Also freeze AI balls in Co-op mode
        if selected_game_mode == "Co-op":
            for ai_ball in coop_ai_balls:
                ai_ball['frozen'] = True
                ai_ball['frozen_end'] = current_time + \
                    POWERUP_DURATIONS['freeze']


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


def check_tron_trail_collision(ball):
    """Check if ball has hit any tron trails"""
    active_balls = get_active_balls()
    for other_ball in active_balls.values():
        # Skip if it's the same ball or if the other ball has no trail
        # Also skip if this ball is the one with the tron powerup
        if (other_ball == ball or not other_ball.get('tron_trail')
                or ball['powerup'] == 'tron'):  # Changed this line to check if the checking ball has tron
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
            unit_line = (line_vec[0] / line_length, line_vec[1] / line_length)

            # Project ball vector onto line vector
            proj_length = ball_vec[0] * unit_line[0] + \
                ball_vec[1] * unit_line[1]

            # Get closest point on line segment
            if proj_length < 0:
                closest = (x1, y1)
            elif proj_length > line_length:
                closest = (x2, y2)
            else:
                closest = (x1 + unit_line[0] * proj_length,
                           y1 + unit_line[1] * proj_length)

            # Check distance from ball to closest point
            dx = ball['x'] - closest[0]
            dy = ball['y'] - closest[1]
            distance = math.sqrt(dx**2 + dy**2)

            if distance < ball['radius']:
                # Collision detected - bounce the ball
                normal = (dx / distance, dy / distance)
                ball['vx'] = normal[0] * abs(ball['vx'] + ball['vy'])
                ball['vy'] = normal[1] * abs(ball['vx'] + ball['vy'])
                collision_sound.play()
                return


def init_coop_mode():
    """Initialize Co-op mode for a new game"""
    global coop_level, coop_ai_balls, eliminated_players
    coop_level = 1
    eliminated_players = set()

    # Clear and create initial AI ball(s)
    coop_ai_balls = []
    spawn_coop_ai_balls()

    # Reset all player balls
    reset_balls()


def spawn_coop_ai_balls():
    """Spawn AI balls for the current co-op level"""
    global coop_level, coop_ai_balls
    coop_ai_balls = []

    # Place AI balls in positions around the platform
    platform_center_x = PLATFORM_X + PLATFORM_SIZE / 2
    platform_center_y = PLATFORM_Y + PLATFORM_SIZE / 2
    radius = PLATFORM_SIZE * 0.35  # Distance from center

    for i in range(coop_level):
        # Calculate position in a circle around center
        angle = (2 * math.pi * i) / coop_level
        x = platform_center_x + radius * math.cos(angle)
        y = platform_center_y + radius * math.sin(angle)

        # Ensure within platform bounds
        x = max(PLATFORM_X + BALL_RADIUS,
                min(x, PLATFORM_X + PLATFORM_SIZE - BALL_RADIUS))
        y = max(PLATFORM_Y + BALL_RADIUS,
                min(y, PLATFORM_Y + PLATFORM_SIZE - BALL_RADIUS))

        # Create an AI ball with color based on level
        color_index = min(i, len(AI_COLORS) - 1)  # Prevent index out of range
        ai_ball = {
            'x': x,
            'y': y,
            'vx': 0,
            'vy': 0,
            'colors': AI_COLORS[color_index],
            'radius': BALL_RADIUS,
            'powerup': None,
            'powerup_end': 0,
            'last_hit_by': None,
            'trail': [],
            'frozen': False,
            'frozen_end': 0,
            'heavy_hit': False,
            'hit_flash_start': 0,
            'tron_trail': [],
            'is_ai': True,
            # Speed increases with level, caps at +50%
            'speed_multiplier': 1.0 + (0.1 * min(coop_level - 1, 5))
        }

        coop_ai_balls.append(ai_ball)


def show_level_message():
    """Show level transition message"""
    global coop_level
    screen.fill(BACKGROUND_COLOR)
    draw_text_with_outline(
        f"Level {coop_level}",
        title_font,
        WIDTH // 2,
        HEIGHT // 3,
        WHITE,
        BLACK,
        center=True)

    # Show currently active players
    y_pos = HEIGHT // 2
    player_colors = {
        'red': RED,
        'blue': BLUE,
        'orange': ORANGE,
        'purple': PLAYER_PURPLE
    }

    # List active players
    active_players = [color for color in ['red', 'blue', 'orange', 'purple']
                      if color not in eliminated_players and (
        color == 'red' or
        (color == 'blue' and selected_player_count >= 2) or
        (color == 'orange' and selected_player_count >= 3) or
        (color == 'purple' and selected_player_count >= 4)
    )]

    if active_players:
        draw_text_with_outline(
            "Active Players:",
            subtitle_font,
            WIDTH // 2,
            y_pos,
            WHITE,
            BLACK,
            center=True)
        y_pos += 40

        for color in active_players:
            draw_text_with_outline(
                color.capitalize(),
                subtitle_font,
                WIDTH // 2,
                y_pos,
                player_colors[color],
                BLACK,
                center=True)
            y_pos += 30

    # Show enemy count
    draw_text_with_outline(
        f"{coop_level} AI Opponent{
            '' if coop_level == 1 else 's'}",
        subtitle_font,
        WIDTH // 2,
        HEIGHT * 3 // 4 - 30,
        AI_GRAY,
        BLACK,
        center=True)

    # Ready text
    draw_text_with_outline(
        "Get Ready!",
        subtitle_font,
        WIDTH // 2,
        HEIGHT * 3 // 4 + 30,
        WHITE,
        BLACK,
        center=True)

    pygame.display.flip()
    time.sleep(2)  # Show message for 2 seconds


def show_game_over_screen():
    """Show game over screen for Co-op mode"""
    global coop_level
    waiting = True
    start_time = pygame.time.get_ticks()
    last_time = start_time

    # Create bouncing balls for animation
    balls = []

    # Add player balls that were in the game
    if selected_player_count >= 1:
        balls.append({
            'pos': {'x': WIDTH // 4, 'y': HEIGHT // 4},
            'vel': {'x': 0.3, 'y': 0.2},
            'colors': [DARKER_RED, DARK_RED, RED],
            'elapsed': 0,
            'active': True
        })

    if selected_player_count >= 2:
        balls.append({
            'pos': {'x': WIDTH * 3 // 4, 'y': HEIGHT // 4},
            'vel': {'x': -0.25, 'y': 0.3},
            'colors': [DARKER_BLUE, DARK_BLUE, BLUE],
            'elapsed': 0,
            'active': True
        })

    if selected_player_count >= 3:
        balls.append({
            'pos': {'x': WIDTH // 4, 'y': HEIGHT * 3 // 4},
            'vel': {'x': 0.2, 'y': -0.25},
            'colors': [DARKER_ORANGE, DARK_ORANGE, ORANGE],
            'elapsed': 0,
            'active': True
        })

    if selected_player_count >= 4:
        balls.append({
            'pos': {'x': WIDTH * 3 // 4, 'y': HEIGHT * 3 // 4},
            'vel': {'x': -0.3, 'y': -0.2},
            'colors': [DARKER_PLAYER_PURPLE, DARK_PLAYER_PURPLE, PLAYER_PURPLE],
            'elapsed': 0,
            'active': True
        })

    # Add an AI ball
    balls.append({
        'pos': {'x': WIDTH // 2, 'y': HEIGHT // 2},
        'vel': {'x': -0.2, 'y': 0.2},
        'colors': AI_COLORS[0],
        'elapsed': 0,
        'active': True
    })

    while waiting:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - last_time
        last_time = current_time

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_RETURN:
                if current_time - start_time > 1000:  # Prevent immediate skip
                    waiting = False

        # Also allow controller buttons to skip
        if current_time - start_time > 1000:
            for i in range(len(controllers)):
                if controllers[i].get_button(
                        0) or controllers[i].get_button(7):
                    waiting = False
                    break

        screen.fill(BACKGROUND_COLOR)

        # Update and draw bouncing balls
        for ball in balls:
            ball['elapsed'] = elapsed_time

            # Update position
            ball['pos']['x'] += ball['vel']['x'] * ball['elapsed']
            ball['pos']['y'] += ball['vel']['y'] * ball['elapsed']

            # Bounce off edges
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

            # Draw ball
            draw_ball({
                'x': ball['pos']['x'],
                'y': ball['pos']['y'],
                'radius': BALL_RADIUS,
                'colors': ball['colors'],
                'powerup': None
            })

        # Draw game over text
        draw_text_with_outline(
            "Game Over!",
            title_font,
            WIDTH // 2,
            HEIGHT // 4,
            WHITE,
            BLACK,
            center=True)

        # Draw level reached
        level_text = f"Your team reached Level {coop_level}"
        draw_text_with_outline(
            level_text,
            subtitle_font,
            WIDTH // 2,
            HEIGHT // 2 - 30,
            WHITE,
            BLACK,
            center=True)

        # Draw AI defeated count
        ai_count = coop_level - 1  # Players defeated all AI in previous levels
        ai_text = f"AI Defeated: {ai_count}"
        draw_text_with_outline(
            ai_text,
            subtitle_font,
            WIDTH // 2,
            HEIGHT // 2 + 30,
            AI_GRAY,
            BLACK,
            center=True)

        # Show continue prompt
        if current_time - start_time > 1000:
            draw_text_with_outline(
                "Press Enter or Controller Button to Continue",
                subtitle_font,
                WIDTH // 2,
                HEIGHT * 3 // 4,
                WHITE,
                BLACK,
                center=True)

        pygame.display.flip()
        clock.tick(FPS)


def show_victory_screen():
    """Show victory screen when players beat all levels in Co-op mode"""
    global coop_level, MAX_AI_BALLS
    waiting = True
    start_time = pygame.time.get_ticks()
    last_time = start_time

    # Create bouncing balls for animation (one for each player)
    balls = []

    # Add player balls that were in the game
    if selected_player_count >= 1:
        balls.append({
            'pos': {'x': WIDTH // 4, 'y': HEIGHT // 4},
            'vel': {'x': 0.3, 'y': 0.2},
            'colors': [DARKER_RED, DARK_RED, RED],
            'elapsed': 0,
            'active': True
        })

    if selected_player_count >= 2:
        balls.append({
            'pos': {'x': WIDTH * 3 // 4, 'y': HEIGHT // 4},
            'vel': {'x': -0.25, 'y': 0.3},
            'colors': [DARKER_BLUE, DARK_BLUE, BLUE],
            'elapsed': 0,
            'active': True
        })

    if selected_player_count >= 3:
        balls.append({
            'pos': {'x': WIDTH // 4, 'y': HEIGHT * 3 // 4},
            'vel': {'x': 0.2, 'y': -0.25},
            'colors': [DARKER_ORANGE, DARK_ORANGE, ORANGE],
            'elapsed': 0,
            'active': True
        })

    if selected_player_count >= 4:
        balls.append({
            'pos': {'x': WIDTH * 3 // 4, 'y': HEIGHT * 3 // 4},
            'vel': {'x': -0.3, 'y': -0.2},
            'colors': [DARKER_PLAYER_PURPLE, DARK_PLAYER_PURPLE, PLAYER_PURPLE],
            'elapsed': 0,
            'active': True
        })

    while waiting:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - last_time
        last_time = current_time

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_RETURN:
                if current_time - start_time > 1000:  # Prevent immediate skip
                    waiting = False

        # Also allow controller buttons to skip
        if current_time - start_time > 1000:
            for i in range(len(controllers)):
                if controllers[i].get_button(
                        0) or controllers[i].get_button(7):
                    waiting = False
                    break

        screen.fill(BACKGROUND_COLOR)

        # Update and draw bouncing balls
        for ball in balls:
            ball['elapsed'] = elapsed_time

            # Update position
            ball['pos']['x'] += ball['vel']['x'] * ball['elapsed']
            ball['pos']['y'] += ball['vel']['y'] * ball['elapsed']

            # Bounce off edges
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

            # Draw ball
            draw_ball({
                'x': ball['pos']['x'],
                'y': ball['pos']['y'],
                'radius': BALL_RADIUS,
                'colors': ball['colors'],
                'powerup': None
            })

        # Draw victory text
        draw_text_with_outline(
            "VICTORY!",
            title_font,
            WIDTH // 2,
            HEIGHT // 3,
            WHITE,
            BLACK,
            center=True)

        # Draw congratulatory text
        victory_text = f"You beat all {MAX_AI_BALLS} levels!"
        draw_text_with_outline(
            victory_text,
            subtitle_font,
            WIDTH // 2,
            HEIGHT // 2,
            WHITE,
            BLACK,
            center=True)

        # Show continue prompt
        if current_time - start_time > 1000:
            draw_text_with_outline(
                "Press Enter or Controller Button to Continue",
                subtitle_font,
                WIDTH // 2,
                HEIGHT * 3 // 4,
                WHITE,
                BLACK,
                center=True)

        pygame.display.flip()
        clock.tick(FPS)


def coop_game():
    """Main game loop for Co-op mode"""
    global powerups, last_powerup_spawn, eliminated_players, coop_level

    # Initialize Co-op mode
    init_coop_mode()
    show_level_message()

    # Reset game state
    powerups = []
    last_powerup_spawn = pygame.time.get_ticks()
    active_players = get_active_balls()  # Only human players

    # Check for controllers periodically
    controller_check_time = pygame.time.get_ticks()

    while True:
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        # Check for controller changes every few seconds
        if current_time - controller_check_time > 3000:
            check_for_new_controllers()
            controller_check_time = current_time

        # Handle player movements
        if 'red' in active_players:
            move_ball(
                red_ball,
                keys,
                pygame.K_w,
                pygame.K_s,
                pygame.K_a,
                pygame.K_d,
                0)

        if 'blue' in active_players:
            move_ball(
                blue_ball,
                keys,
                pygame.K_UP,
                pygame.K_DOWN,
                pygame.K_LEFT,
                pygame.K_RIGHT,
                1 if len(controllers) > 1 else -1)

        if 'orange' in active_players:
            move_ball(
                orange_ball,
                keys,
                pygame.K_i,
                pygame.K_k,
                pygame.K_j,
                pygame.K_l,
                2 if len(controllers) > 2 else -1)

        if 'purple' in active_players:
            move_ball(
                purple_ball,
                keys,
                pygame.K_KP8,
                pygame.K_KP5,
                pygame.K_KP4,
                pygame.K_KP6,
                3 if len(controllers) > 3 else -1)

        # Handle AI movements
        for ai_ball in coop_ai_balls:
            # Find closest human player to target
            closest_player = None
            closest_dist = float('inf')

            for player_ball in active_players.values():
                dx = player_ball['x'] - ai_ball['x']
                dy = player_ball['y'] - ai_ball['y']
                dist = math.sqrt(dx * dx + dy * dy)

                if dist < closest_dist:
                    closest_dist = dist
                    closest_player = player_ball

            if closest_player:
                # Use the existing AI movement code with the closest player
                move_ai_ball_coop(ai_ball, closest_player, current_time)

        # Spawn powerups
        if current_time - last_powerup_spawn > selected_powerup_interval:
            if len(powerups) < 3:
                powerups.append(spawn_powerup())
                last_powerup_spawn = current_time

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # Apply physics to all balls and check powerup collisions
        for ball in active_players.values():
            apply_physics(ball)
            check_powerup_collision(ball)

        for ai_ball in coop_ai_balls:
            apply_physics(ai_ball)
            check_powerup_collision(ai_ball)

        # Handle collisions between players
        ball_list = list(active_players.values())
        for i in range(len(ball_list)):
            for j in range(i + 1, len(ball_list)):
                handle_collision(ball_list[i], ball_list[j])

        # Handle collisions between players and AI
        for player_ball in active_players.values():
            for ai_ball in coop_ai_balls:
                handle_collision(player_ball, ai_ball)

        # Handle collisions between AI balls
        for i in range(len(coop_ai_balls)):
            for j in range(i + 1, len(coop_ai_balls)):
                handle_collision(coop_ai_balls[i], coop_ai_balls[j])

        # Check for fallen players
        fallen_players = []
        for color, player_ball in active_players.items():
            if is_off_platform(player_ball):
                fallen_players.append((color, player_ball))

        # Handle fallen players in Co-op mode
        for color, player_ball in fallen_players:
            # Mark player as eliminated
            eliminated_players.add(color)
            # Remove from active players
            del active_players[color]

        # Check for fallen AI balls
        fallen_ai = []
        for i, ai_ball in enumerate(coop_ai_balls):
            if is_off_platform(ai_ball):
                fallen_ai.append(i)

        # Remove fallen AI (in reverse order to avoid index issues)
        for i in sorted(fallen_ai, reverse=True):
            coop_ai_balls.pop(i)

        # Check end conditions
        if not active_players:
            # All players eliminated - game over
            show_game_over_screen()
            return

        if not coop_ai_balls:
            # All AI eliminated - advance to next level
            coop_level += 1
            if coop_level > MAX_AI_BALLS:
                # Player beat the maximum level - victory!
                show_victory_screen()
                return

            # Reset eliminated players for next level - everyone comes back
            eliminated_players = set()

            # Reset all ball positions to proper spawn positions
            spawn_pos = get_spawn_positions()
            red_ball['x'], red_ball['y'] = spawn_pos['red']
            red_ball['vx'], red_ball['vy'] = 0, 0
            if selected_player_count >= 2:
                blue_ball['x'], blue_ball['y'] = spawn_pos['blue']
                blue_ball['vx'], blue_ball['vy'] = 0, 0
            if selected_player_count >= 3:
                orange_ball['x'], orange_ball['y'] = spawn_pos['orange']
                orange_ball['vx'], orange_ball['vy'] = 0, 0
            if selected_player_count >= 4:
                purple_ball['x'], purple_ball['y'] = spawn_pos['purple']
                purple_ball['vx'], purple_ball['vy'] = 0, 0

            # Clear powerups for all players
            red_ball['powerup'] = None
            red_ball['radius'] = BALL_RADIUS
            if selected_player_count >= 2:
                blue_ball['powerup'] = None
                blue_ball['radius'] = BALL_RADIUS
            if selected_player_count >= 3:
                orange_ball['powerup'] = None
                orange_ball['radius'] = BALL_RADIUS
            if selected_player_count >= 4:
                purple_ball['powerup'] = None
                purple_ball['radius'] = BALL_RADIUS

            # Clear all powerups on the field
            powerups = []

            # Update active players
            active_players = get_active_balls()

            # Spawn new AI balls for next level
            spawn_coop_ai_balls()

            # Show level message
            show_level_message()

            # Start next level
            eliminated_players = set()  # Respawn all players
            active_players = get_active_balls()
            spawn_coop_ai_balls()
            show_level_message()

        # Apply physics effects after collisions
        for ball in active_players.values():
            # Check powerup expiry
            check_powerup_expiry(ball)
            # Check frozen state
            if ball.get(
                    'frozen',
                    False) and current_time >= ball.get(
                    'frozen_end',
                    0):
                ball['frozen'] = False
                ball['frozen_end'] = 0
            # Check tron trail collisions
            check_tron_trail_collision(ball)

        for ai_ball in coop_ai_balls:
            # Check powerup expiry
            check_powerup_expiry(ai_ball)
            # Check frozen state
            if ai_ball.get(
                    'frozen',
                    False) and current_time >= ai_ball.get(
                    'frozen_end',
                    0):
                ai_ball['frozen'] = False
                ai_ball['frozen_end'] = 0
            # Check tron trail collisions
            check_tron_trail_collision(ai_ball)

        # Render everything
        screen.fill(BACKGROUND_COLOR)
        draw_platform()
        draw_powerups()

        # Draw level indicator for Co-op mode
        draw_text_with_outline(
            f"Level {coop_level}",
            subtitle_font,
            WIDTH // 2,
            20,
            WHITE,
            BLACK,
            center=True)

        # Draw all active players
        for ball in active_players.values():
            draw_ball(ball)

        # Draw all AI balls
        for ai_ball in coop_ai_balls:
            draw_ball(ai_ball)

        # Draw scores (for Co-op, just show active/dead status)
        draw_coop_status()

        # Draw controller indicators
        if len(controllers) > 0:
            draw_controller_indicators()

        pygame.display.flip()
        clock.tick(FPS)


def draw_coop_status():
    """Draw player status for Co-op mode"""
    # Display which players are still active and which are eliminated
    potential_players = {
        'red': (RED, 10, 10),
        'blue': (BLUE, WIDTH - 150, 10),
        'orange': (ORANGE, 10, HEIGHT - 30),
        'purple': (PLAYER_PURPLE, WIDTH - 150, HEIGHT - 30)
    }

    # Only show status for players that should be in the game based on player
    # count
    active_colors = ['red']
    if selected_player_count >= 2:
        active_colors.append('blue')
    if selected_player_count >= 3:
        active_colors.append('orange')
    if selected_player_count >= 4:
        active_colors.append('purple')

    for color in active_colors:
        display_color, x, y = potential_players[color]
        status = "Active" if color not in eliminated_players else "Eliminated"
        text_color = display_color if status == "Active" else GRAY
        draw_text_with_outline(f"{color.capitalize()}: {status}",
                               score_font, x, y, text_color, BLACK, center=False)


def game_loop():
    global score

    # Initialize controllers at game start
    init_controllers()

    while True:
        score = {
            'red': 0,
            'blue': 0,
            'orange': 0,
            'purple': 0,
            'ai': 0}  # Added 'ai' score
        title_screen()
        show_start_message()
        main_game()


def draw_text_with_outline(
        text,
        font,
        x,
        y,
        text_color,
        outline_color,
        center=False):
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
    return tuple(int(c1 + (c2 - c1) * factor)
                 for c1, c2 in zip(color1, color2))


# Start the game loop
game_loop()
