import pygame
import math
import argparse
import random

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Polar System Simulation Game")
    parser.add_argument('--width', type=int, default=1200, help='Width of the game window')
    parser.add_argument('--height', type=int, default=760, help='Height of the game window')
    parser.add_argument('--fps', type=int, default=60, help='Frame rate of the game')
    args = parser.parse_args()

    # Initialize Pygame
    pygame.init()

    # Set up display
    width, height = args.width, args.height
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Polar System Simulation Game")

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREY = (169, 169, 169)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    CYAN = (0, 255, 255)
    DARK_BLUE = (0, 0, 139)

    # Set the center of the polar system
    center_x = width // 2
    center_y = height // 2

    # Create a surface for static elements
    static_surface = pygame.Surface((width, height))
    static_surface.fill(BLACK)

    # Draw stars in the background to simulate space
    def draw_starry_background(surface, num_stars=30):
        for _ in range(num_stars):
            star_x = random.randint(0, width - 1)
            star_y = random.randint(0, height - 1)
            star_color = random.choice([WHITE, GREY])
            if random.random() > 0.8:  # Only some stars will flicker
                pygame.draw.circle(surface, star_color, (star_x, star_y), 1)

    # Draw the sun with a shimmering effect
    def draw_sun(surface, x, y):
        sun_radius = 20 + random.randint(-1, 1)  # Reduce shimmering effect
        pygame.draw.circle(surface, YELLOW, (x, y), sun_radius)
        for _ in range(5):  # Reduce number of flame effects
            angle = random.uniform(0, 2 * math.pi)
            length = random.randint(22, 28)
            end_x = x + int(length * math.cos(angle))
            end_y = y + int(length * math.sin(angle))
            pygame.draw.circle(surface, ORANGE, (end_x, end_y), 2)

    # Object parameters (elliptical coordinates)
    objects = [
        {'a': 70, 'b': 50, 'theta': 0, 'angular_velocity': 0.02, 'color': RED, 'name': 'Mercury', 'size': 4, 'weight': '3.3e23 kg', 'volume': '6.083e10 km³', 'rotation_period': '58.6 days', 'orbital_period': '88 days', 'discovery_year': 'Before 3000 BC'},
        {'a': 100, 'b': 80, 'theta': math.pi / 6, 'angular_velocity': 0.015, 'color': GREEN, 'name': 'Venus', 'size': 6, 'weight': '4.87e24 kg', 'volume': '9.284e11 km³', 'rotation_period': '243 days', 'orbital_period': '225 days', 'discovery_year': 'Before 17th century'},
        {'a': 150, 'b': 120, 'theta': math.pi / 4, 'angular_velocity': 0.01, 'color': BLUE, 'name': 'Earth', 'size': 6, 'weight': '5.97e24 kg', 'volume': '1.08321e12 km³', 'rotation_period': '24 hours', 'orbital_period': '365.25 days'},
        {'a': 200, 'b': 160, 'theta': math.pi / 3, 'angular_velocity': 0.008, 'color': YELLOW, 'name': 'Mars', 'size': 4, 'weight': '6.39e23 kg', 'volume': '1.6318e11 km³', 'rotation_period': '24.6 hours', 'orbital_period': '687 days', 'discovery_year': 'Before 17th century'},
        {'a': 250, 'b': 200, 'theta': math.pi / 2, 'angular_velocity': 0.005, 'color': ORANGE, 'name': 'Jupiter', 'size': 12, 'weight': '1.898e27 kg', 'volume': '1.43128e15 km³', 'rotation_period': '9.9 hours', 'orbital_period': '11.9 years', 'discovery_year': '1610 by Galileo Galilei'},
        {'a': 300, 'b': 240, 'theta': math.pi / 1.5, 'angular_velocity': 0.004, 'color': PURPLE, 'name': 'Saturn', 'size': 10, 'weight': '5.68e26 kg', 'volume': '8.2713e14 km³', 'rotation_period': '10.7 hours', 'orbital_period': '29.5 years', 'discovery_year': '1610 by Galileo Galilei'},
        {'a': 350, 'b': 280, 'theta': math.pi / 1.8, 'angular_velocity': 0.003, 'color': CYAN, 'name': 'Uranus', 'size': 8, 'weight': '8.68e25 kg', 'volume': '6.833e13 km³', 'rotation_period': '17.2 hours', 'orbital_period': '84 years', 'discovery_year': '1781 by William Herschel'},
        {'a': 400, 'b': 320, 'theta': math.pi / 2.2, 'angular_velocity': 0.002, 'color': DARK_BLUE, 'name': 'Neptune', 'size': 8, 'weight': '1.02e26 kg', 'volume': '6.254e13 km³', 'rotation_period': '16.1 hours', 'orbital_period': '165 years', 'discovery_year': '1846 by Johann Galle'},
    ]

    # Add the Moon
    moon = {
        'a': 20, 'b': 15, 'theta': 0, 'angular_velocity': 0.05, 'color': GREY, 'name': 'Moon', 'size': 2
    }

    # Game loop control
    running = True
    clock = pygame.time.Clock()

    # Function to convert elliptical to Cartesian
    def elliptical_to_cartesian(a, b, cos_theta, sin_theta, offset_x=0, offset_y=0):
        x = a * cos_theta + offset_x
        y = b * sin_theta + offset_y
        return int(x), int(y)

    # Hover effect
    hovered_object = None
    all_paused = False

    while running:
        # Blit the static elements surface
        static_surface.fill(BLACK)
        #draw_starry_background(static_surface)
        draw_sun(static_surface, center_x, center_y)
        window.blit(static_surface, (0, 0))

        # Event handling
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Check if any object is hovered
        any_hovered = False
        for obj in objects:
            cos_theta = math.cos(obj['theta'])
            sin_theta = math.sin(obj['theta'])
            x, y = elliptical_to_cartesian(obj['a'], obj['b'], cos_theta, sin_theta, center_x, center_y)
            distance = math.sqrt((mouse_pos[0] - x) ** 2 + (mouse_pos[1] - y) ** 2)

            if distance <= obj['size'] + 5:
                hovered_object = obj
                any_hovered = True
                break

        if any_hovered:
            all_paused = True
        else:
            all_paused = False
            hovered_object = None

        # Update and draw each object
        for obj in objects:
            # Update the angle (movement simulation)
            if not all_paused:
                obj['theta'] = (obj['theta'] + obj['angular_velocity']) % (2 * math.pi)

            # Draw the elliptical path
            rect = pygame.Rect(center_x - obj['a'], center_y - obj['b'], 2 * obj['a'], 2 * obj['b'])
            pygame.draw.ellipse(window, WHITE, rect, 1)

            # Draw the object
            cos_theta = math.cos(obj['theta'])
            sin_theta = math.sin(obj['theta'])
            x, y = elliptical_to_cartesian(obj['a'], obj['b'], cos_theta, sin_theta, center_x, center_y)
            pygame.draw.circle(window, obj['color'], (x, y), obj['size'])

            # Draw the name of the object with a transparent background next to the planet
            font = pygame.font.Font(None, 24)
            text = font.render(obj['name'], True, WHITE)
            text_rect = text.get_rect()
            text_rect.midleft = (x + obj['size'] + 5, y)
            window.blit(text, text_rect)

            # Draw Jupiter's satellite belt
            if obj['name'] == 'Jupiter':
                for _ in range(20):
                    angle = random.uniform(0, 2 * math.pi)
                    length = obj['size'] + 10 + random.randint(3, 5)  # Reduce the distance of the satellite belt
                    satellite_x = x + int(length * math.cos(angle))
                    satellite_y = y + int(length * math.sin(angle))
                    pygame.draw.circle(window, GREY, (satellite_x, satellite_y), 1)

            # Update Moon's position if the object is Earth
            if obj['name'] == 'Earth':
                if not all_paused:
                    moon['theta'] = (moon['theta'] + moon['angular_velocity']) % (2 * math.pi)
                moon_cos_theta = math.cos(moon['theta'])
                moon_sin_theta = math.sin(moon['theta'])
                moon_x, moon_y = elliptical_to_cartesian(moon['a'], moon['b'], moon_cos_theta, moon_sin_theta, x, y)
                pygame.draw.circle(window, moon['color'], (moon_x, moon_y), moon['size'])
                moon_text = font.render(moon['name'], True, WHITE)
                moon_text_rect = moon_text.get_rect()
                moon_text_rect.midleft = (moon_x + moon['size'] + 5, moon_y)
                window.blit(moon_text, moon_text_rect)

        # Display information about the hovered object
        if hovered_object:
            info_font = pygame.font.Font(None, 36)
            info_text_lines = [
                f"Name: {hovered_object['name']}",
                f"Weight: {hovered_object['weight']}",
                f"Volume: {hovered_object['volume']}",
                f"Rotation Period: {hovered_object['rotation_period']}",
                f"Orbital Period: {hovered_object['orbital_period']}",
                f"Discovery Year: {hovered_object.get('discovery_year', 'Unknown')}"
            ]
            for i, line in enumerate(info_text_lines):
                info_text = info_font.render(line, True, WHITE)
                info_x, info_y = mouse_pos
                window.blit(info_text, (info_x + 15, info_y + i * 30))

        # Update the display
        pygame.display.update()

        # Cap the frame rate
        clock.tick(args.fps)

    # Quit Pygame
    pygame.quit()

if __name__ == "__main__":
    main()