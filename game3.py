import pygame
import math
import random
import time
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
GRID_SIZE = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_CYAN = (0, 255, 255)
NEON_PURPLE = (255, 0, 255)
NEON_GREEN = (0, 255, 100)
NEON_ORANGE = (255, 150, 0)
DARK_BLUE = (10, 20, 40)
GLASS_BLUE = (50, 100, 200, 120)
QUANTUM_GOLD = (255, 215, 0)

class Particle:
    """Individual particle for visual effects"""
    def __init__(self, x: float, y: float, vx: float, vy: float, color: Tuple[int, int, int], life: float, size: float = 3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        
    def update(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        
    def draw(self, screen: pygame.Surface):
        if self.life > 0:
            alpha = self.life / self.max_life
            size = max(1, int(self.size * alpha))
            color = tuple(int(c * alpha) for c in self.color)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)

class ParticleSystem:
    """Manages all particle effects"""
    def __init__(self):
        self.particles: List[Particle] = []
        
    def add_burst(self, x: float, y: float, color: Tuple[int, int, int] = NEON_CYAN, count: int = 15):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, vx, vy, color, random.uniform(0.5, 1.5), random.uniform(2, 6)))
            
    def add_trail(self, x: float, y: float, color: Tuple[int, int, int] = NEON_PURPLE):
        for _ in range(3):
            vx = random.uniform(-30, 30)
            vy = random.uniform(-30, 30)
            self.particles.append(Particle(x, y, vx, vy, color, 0.8, 4))
            
    def add_ambient(self, x: float, y: float):
        vx = random.uniform(-20, 20)
        vy = random.uniform(-20, 20)
        color = random.choice([NEON_CYAN, NEON_PURPLE, NEON_GREEN])
        self.particles.append(Particle(x, y, vx, vy, color, 2.0, 2))
        
    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update(dt)
            
    def draw(self, screen: pygame.Surface):
        for particle in self.particles:
            particle.draw(screen)

class QuantumOrb:
    """Futuristic collectible orb"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.pulse_time = 0
        self.spin_angle = 0
        self.collected = False
        
    def update(self, dt: float):
        self.pulse_time += dt * 4
        self.spin_angle += dt * 3
        
    def draw(self, screen: pygame.Surface):
        if self.collected:
            return
            
        pulse = 1.0 + math.sin(self.pulse_time) * 0.3
        
        # Outer glow
        glow_size = int(25 * pulse)
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*QUANTUM_GOLD, 30), (glow_size, glow_size), glow_size)
        screen.blit(glow_surface, (self.x - glow_size, self.y - glow_size))
        
        # Main orb layers
        for i in range(3):
            size = int((15 - i * 3) * pulse)
            alpha = 255 - i * 60
            color = (*QUANTUM_GOLD, alpha) if i == 0 else (*NEON_ORANGE, alpha)
            orb_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(orb_surface, color, (size, size), size)
            screen.blit(orb_surface, (self.x - size, self.y - size))
            
        # Spinning core
        core_x = self.x + math.cos(self.spin_angle) * 3
        core_y = self.y + math.sin(self.spin_angle) * 3
        pygame.draw.circle(screen, WHITE, (int(core_x), int(core_y)), 3)

class PowerUp:
    """Special power-up items"""
    def __init__(self, x: float, y: float, power_type: str):
        self.x = x
        self.y = y
        self.type = power_type
        self.time = 0
        self.collected = False
        
        self.colors = {
            'speed': NEON_GREEN,
            'slow': NEON_PURPLE,
            'shield': NEON_CYAN,
            'multi': NEON_ORANGE
        }
        
    def update(self, dt: float):
        self.time += dt * 2
        
    def draw(self, screen: pygame.Surface):
        if self.collected:
            return
            
        color = self.colors.get(self.type, WHITE)
        pulse = 1.0 + math.sin(self.time) * 0.4
        
        # Aura
        aura_size = int(20 * pulse)
        aura_surface = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surface, (*color, 50), (aura_size, aura_size), aura_size)
        screen.blit(aura_surface, (self.x - aura_size, self.y - aura_size))
        
        # Main shape
        size = int(12 * pulse)
        if self.type == 'speed':
            # Triangle
            points = [(self.x + size, self.y), (self.x - size//2, self.y - size), (self.x - size//2, self.y + size)]
            pygame.draw.polygon(screen, color, points)
        elif self.type == 'slow':
            # Diamond
            points = [(self.x, self.y - size), (self.x + size, self.y), (self.x, self.y + size), (self.x - size, self.y)]
            pygame.draw.polygon(screen, color, points)
        elif self.type == 'shield':
            # Hexagon
            points = []
            for i in range(6):
                angle = i * math.pi / 3
                px = self.x + math.cos(angle) * size
                py = self.y + math.sin(angle) * size
                points.append((px, py))
            pygame.draw.polygon(screen, color, points)
        else:  # multi
            # Star
            points = []
            for i in range(10):
                angle = i * math.pi / 5
                radius = size if i % 2 == 0 else size // 2
                px = self.x + math.cos(angle) * radius
                py = self.y + math.sin(angle) * radius
                points.append((px, py))
            pygame.draw.polygon(screen, color, points)

class SnakeSegment:
    """Individual snake segment with smooth positioning"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        
    def update(self, dt: float, target_x: float, target_y: float):
        self.target_x = target_x
        self.target_y = target_y
        
        # Smooth interpolation
        lerp_speed = 15.0
        self.x += (self.target_x - self.x) * lerp_speed * dt
        self.y += (self.target_y - self.y) * lerp_speed * dt

class QuantumSerpent:
    """The main snake with smooth, flowing movement"""
    def __init__(self, x: float, y: float):
        self.segments = [SnakeSegment(x, y)]
        self.direction = pygame.Vector2(1, 0)
        self.speed = 200
        self.base_speed = 200
        self.trail_positions = []
        self.last_turn_time = 0
        
        # Power-up effects
        self.speed_boost_time = 0
        self.slow_time = 0
        self.shield_time = 0
        self.multi_orb_time = 0
        
    def update(self, dt: float, keys: pygame.key.ScancodeWrapper, particles: ParticleSystem):
        # Handle input with smooth turning
        new_direction = self.direction.copy()
        
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.direction.x == 0:
            new_direction = pygame.Vector2(-1, 0)
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.direction.x == 0:
            new_direction = pygame.Vector2(1, 0)
        elif (keys[pygame.K_UP] or keys[pygame.K_w]) and self.direction.y == 0:
            new_direction = pygame.Vector2(0, -1)
        elif (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.direction.y == 0:
            new_direction = pygame.Vector2(0, 1)
            
        if new_direction != self.direction:
            self.direction = new_direction
            self.last_turn_time = time.time()
            particles.add_burst(self.segments[0].x, self.segments[0].y, NEON_CYAN, 8)
            
        # Update power-up effects
        self.speed_boost_time = max(0, self.speed_boost_time - dt)
        self.slow_time = max(0, self.slow_time - dt)
        self.shield_time = max(0, self.shield_time - dt)
        self.multi_orb_time = max(0, self.multi_orb_time - dt)
        
        # Calculate current speed
        current_speed = self.base_speed
        if self.speed_boost_time > 0:
            current_speed *= 1.8
        elif self.slow_time > 0:
            current_speed *= 0.5
            
        # Move head
        head = self.segments[0]
        head.x += self.direction.x * current_speed * dt
        head.y += self.direction.y * current_speed * dt
        
        # Update trail
        self.trail_positions.append((head.x, head.y, time.time()))
        self.trail_positions = [(x, y, t) for x, y, t in self.trail_positions if time.time() - t < 0.5]
        
        # Update segments to follow smoothly
        for i in range(1, len(self.segments)):
            prev_segment = self.segments[i - 1]
            segment = self.segments[i]
            
            # Calculate target position
            dx = prev_segment.x - segment.x
            dy = prev_segment.y - segment.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > GRID_SIZE:
                target_x = prev_segment.x - (dx / distance) * GRID_SIZE
                target_y = prev_segment.y - (dy / distance) * GRID_SIZE
                segment.update(dt, target_x, target_y)
            
        # Add trail particles
        if random.random() < 0.3:
            particles.add_trail(head.x, head.y)
            
    def grow(self):
        """Add a new segment to the snake"""
        if len(self.segments) > 0:
            tail = self.segments[-1]
            new_segment = SnakeSegment(tail.x, tail.y)
            self.segments.append(new_segment)
            
    def check_collision(self) -> bool:
        """Check if snake collides with itself or walls"""
        head = self.segments[0]
        
        # Wall collision
        if (head.x < 0 or head.x >= SCREEN_WIDTH or 
            head.y < 0 or head.y >= SCREEN_HEIGHT):
            return True
            
        # Self collision (skip if shield is active)
        if self.shield_time <= 0:
            for segment in self.segments[4:]:  # Skip first few segments
                dx = head.x - segment.x
                dy = head.y - segment.y
                if math.sqrt(dx * dx + dy * dy) < GRID_SIZE * 0.8:
                    return True
                    
        return False
        
    def get_head_pos(self) -> Tuple[int, int]:
        """Get head position in grid coordinates"""
        head = self.segments[0]
        return (int(head.x // GRID_SIZE), int(head.y // GRID_SIZE))
        
    def draw(self, screen: pygame.Surface):
        # Draw trail
        current_time = time.time()
        for i, (x, y, t) in enumerate(self.trail_positions):
            alpha = max(0, 1.0 - (current_time - t) * 2)
            if alpha > 0:
                size = int(5 * alpha)
                trail_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (*NEON_PURPLE, int(100 * alpha)), (size, size), size)
                screen.blit(trail_surface, (x - size, y - size))
                
        # Draw segments with smooth curves
        for i, segment in enumerate(self.segments):
            is_head = i == 0
            
            # Segment size decreases towards tail - increased base size
            size_factor = 1.0 - (i * 0.03)
            size = max(12, int(GRID_SIZE * 0.6 * size_factor))
            
            # Color gradient from head to tail
            if is_head:
                color = NEON_CYAN
                glow_color = (*NEON_CYAN, 100)
            else:
                blend = min(1.0, i / len(self.segments))
                r = int(NEON_CYAN[0] * (1 - blend) + NEON_PURPLE[0] * blend)
                g = int(NEON_CYAN[1] * (1 - blend) + NEON_PURPLE[1] * blend)
                b = int(NEON_CYAN[2] * (1 - blend) + NEON_PURPLE[2] * blend)
                color = (r, g, b)
                glow_color = (*color, 80)
                
            # Glow effect
            glow_size = size + 8
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (glow_size, glow_size), glow_size)
            screen.blit(glow_surface, (segment.x - glow_size, segment.y - glow_size))
            
            # Main segment
            pygame.draw.circle(screen, color, (int(segment.x), int(segment.y)), size)
            
            # Inner highlight
            highlight_size = max(2, size // 3)
            pygame.draw.circle(screen, WHITE, (int(segment.x), int(segment.y)), highlight_size)
            
            # Snake eyes on head
            if is_head:
                # Eye positions based on direction
                eye_offset = 6
                if self.direction.x != 0:  # Moving horizontally
                    eye1_x = segment.x - 3
                    eye1_y = segment.y - eye_offset
                    eye2_x = segment.x - 3
                    eye2_y = segment.y + eye_offset
                else:  # Moving vertically
                    eye1_x = segment.x - eye_offset
                    eye1_y = segment.y - 3
                    eye2_x = segment.x + eye_offset
                    eye2_y = segment.y - 3
                
                # Eye glow
                for eye_x, eye_y in [(eye1_x, eye1_y), (eye2_x, eye2_y)]:
                    eye_glow_surface = pygame.Surface((12, 12), pygame.SRCALPHA)
                    pygame.draw.circle(eye_glow_surface, (*WHITE, 100), (6, 6), 6)
                    screen.blit(eye_glow_surface, (eye_x - 6, eye_y - 6))
                    
                    # Eye base
                    pygame.draw.circle(screen, WHITE, (int(eye_x), int(eye_y)), 4)
                    # Pupil
                    pygame.draw.circle(screen, NEON_CYAN, (int(eye_x), int(eye_y)), 2)
                    # Eye shine
                    pygame.draw.circle(screen, WHITE, (int(eye_x - 1), int(eye_y - 1)), 1)
            
        # Draw power-up effects
        if self.shield_time > 0:
            head = self.segments[0]
            shield_pulse = 1.0 + math.sin(time.time() * 10) * 0.3
            shield_size = int(30 * shield_pulse)
            shield_surface = pygame.Surface((shield_size * 2, shield_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (*NEON_CYAN, 60), (shield_size, shield_size), shield_size, 3)
            screen.blit(shield_surface, (head.x - shield_size, head.y - shield_size))

class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Quantum Serpent")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = "menu"  # menu, target_select, playing, game_over, victory
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.target_score = 5000
        self.target_options = [2000, 5000, 10000, 15000]
        self.selected_target = 1  # Index of selected target
        
        # Game objects
        self.snake = QuantumSerpent(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.orbs: List[QuantumOrb] = []
        self.powerups: List[PowerUp] = []
        self.particles = ParticleSystem()
        
        # Timers
        self.orb_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.background_time = 0
        
        # Fonts
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        # Animation
        self.menu_pulse = 0
        self.transition_alpha = 0
        self.victory_time = 0
        self.celebration_particles = []
        
        # Spawn initial orbs
        for _ in range(3):
            self.spawn_orb()
        
    def spawn_orb(self):
        """Spawn a new quantum orb"""
        while True:
            x = random.randint(2, SCREEN_WIDTH // GRID_SIZE - 2) * GRID_SIZE + GRID_SIZE // 2
            y = random.randint(2, SCREEN_HEIGHT // GRID_SIZE - 2) * GRID_SIZE + GRID_SIZE // 2
            
            # Check if position is clear
            clear = True
            for segment in self.snake.segments:
                if abs(segment.x - x) < GRID_SIZE and abs(segment.y - y) < GRID_SIZE:
                    clear = False
                    break
                    
            if clear:
                self.orbs.append(QuantumOrb(x, y))
                break
                
    def spawn_powerup(self):
        """Spawn a random power-up"""
        power_types = ['speed', 'slow', 'shield', 'multi']
        power_type = random.choice(power_types)
        
        while True:
            x = random.randint(2, SCREEN_WIDTH // GRID_SIZE - 2) * GRID_SIZE + GRID_SIZE // 2
            y = random.randint(2, SCREEN_HEIGHT // GRID_SIZE - 2) * GRID_SIZE + GRID_SIZE // 2
            
            # Check if position is clear
            clear = True
            for segment in self.snake.segments:
                if abs(segment.x - x) < GRID_SIZE and abs(segment.y - y) < GRID_SIZE:
                    clear = False
                    break
                    
            if clear:
                self.powerups.append(PowerUp(x, y, power_type))
                break
                
    def draw_background(self):
        """Draw animated holographic background"""
        self.background_time += 1/60
        
        # Subtle gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            # Much more subtle wave effect
            wave = math.sin(self.background_time * 0.2 + ratio * 2) * 0.05
            r = int(8 + wave * 12)
            g = int(12 + wave * 18)
            b = int(35 + wave * 25)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Square grid with subtle glow
        grid_alpha = 25 + int(math.sin(self.background_time * 0.5) * 8)
        
        # Vertical lines
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, (*NEON_CYAN, grid_alpha), (x, 0), (x, SCREEN_HEIGHT))
            
        # Horizontal lines  
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, (*NEON_CYAN, grid_alpha), (0, y), (SCREEN_WIDTH, y))
        
        # Subtle corner accents (only in menu)
        if self.state == "menu":
            # Corner glow effects
            corner_glow = int(40 + math.sin(self.background_time) * 20)
            corners = [(0, 0), (SCREEN_WIDTH, 0), (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT)]
            
            for corner_x, corner_y in corners:
                glow_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*NEON_PURPLE, corner_glow), (50, 50), 50)
                self.screen.blit(glow_surface, (corner_x - 50, corner_y - 50))
        
        # Very minimal ambient particles (only during menu)
        if self.state == "menu" and random.random() < 0.05:
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            self.particles.add_ambient(x, y)
            
    def draw_hud(self):
        """Draw the heads-up display"""
        # Glass panel background
        panel_surface = pygame.Surface((SCREEN_WIDTH, 80), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, GLASS_BLUE, (0, 0, SCREEN_WIDTH, 80))
        pygame.draw.rect(panel_surface, (*WHITE, 50), (0, 0, SCREEN_WIDTH, 80), 2)
        self.screen.blit(panel_surface, (0, 0))
        
        # Score with glow
        score_text = f"SCORE: {self.score:06d}"
        text_surface = self.font_medium.render(score_text, True, WHITE)
        
        # Glow effect
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_surface = self.font_medium.render(score_text, True, NEON_CYAN)
            glow_surface.set_alpha(100)
            self.screen.blit(glow_surface, (20 + offset[0], 20 + offset[1]))
            
        self.screen.blit(text_surface, (20, 20))
        
        # Level
        level_text = f"LEVEL {self.level}"
        level_surface = self.font_small.render(level_text, True, NEON_GREEN)
        self.screen.blit(level_surface, (20, 50))
        
        # Length
        length_text = f"LENGTH: {len(self.snake.segments)}"
        length_surface = self.font_small.render(length_text, True, NEON_PURPLE)
        self.screen.blit(length_surface, (SCREEN_WIDTH - 200, 20))
        
        # Power-up indicators
        y_offset = 50
        if self.snake.speed_boost_time > 0:
            boost_text = f"SPEED BOOST: {self.snake.speed_boost_time:.1f}s"
            boost_surface = self.font_small.render(boost_text, True, NEON_GREEN)
            self.screen.blit(boost_surface, (SCREEN_WIDTH - 300, y_offset))
            y_offset += 25
            
        if self.snake.shield_time > 0:
            shield_text = f"SHIELD: {self.snake.shield_time:.1f}s"
            shield_surface = self.font_small.render(shield_text, True, NEON_CYAN)
            self.screen.blit(shield_surface, (SCREEN_WIDTH - 300, y_offset))
            
    def draw_menu(self):
        """Draw main menu with animations"""
        self.menu_pulse += 0.05
        
        # Title with advanced animations
        title_y = SCREEN_HEIGHT // 3 + math.sin(self.menu_pulse) * 15
        
        # 3D Shadow layers
        for depth in range(8, 0, -1):
            shadow_alpha = 30 - depth * 3
            shadow_font = pygame.font.Font(None, 84)
            shadow_text = shadow_font.render("QUANTUM SERPENT", True, (0, 0, 0, shadow_alpha))
            shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + depth, title_y + depth))
            self.screen.blit(shadow_text, shadow_rect)
        
        # Rainbow gradient title - each letter different color
        title_text = "QUANTUM SERPENT"
        rainbow_colors = [
            (255, 0, 100),   # Pink
            (255, 100, 0),   # Orange  
            (255, 255, 0),   # Yellow
            (100, 255, 0),   # Lime
            (0, 255, 100),   # Cyan-green
            (0, 100, 255),   # Blue
            (100, 0, 255),   # Purple
            (255, 0, 255),   # Magenta
        ]
        
        # Outer glow for each letter
        letter_x = SCREEN_WIDTH // 2 - 200
        for i, letter in enumerate(title_text):
            if letter == ' ':
                letter_x += 20
                continue
                
            color_index = (i + int(self.menu_pulse * 3)) % len(rainbow_colors)
            color = rainbow_colors[color_index]
            
            # Pulsing glow
            pulse = 1.0 + math.sin(self.menu_pulse * 4 + i * 0.5) * 0.4
            
            # Multiple glow layers
            for glow in range(6, 0, -1):
                glow_alpha = int(40 - glow * 5)
                glow_font = pygame.font.Font(None, int(84 + glow * 2 * pulse))
                glow_surface = glow_font.render(letter, True, (*color, glow_alpha))
                glow_rect = glow_surface.get_rect(center=(letter_x, title_y))
                self.screen.blit(glow_surface, glow_rect)
            
            # Main letter with pulse
            main_font = pygame.font.Font(None, int(84 * pulse))
            letter_surface = main_font.render(letter, True, WHITE)
            letter_rect = letter_surface.get_rect(center=(letter_x, title_y))
            self.screen.blit(letter_surface, letter_rect)
            
            letter_x += letter_surface.get_width() + 5
        
        # Subtitle
        subtitle_surface = self.font_small.render("Next-Gen Snake Experience", True, NEON_PURPLE)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, title_y + 60))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Instructions
        instructions = [
            "WASD or Arrow Keys - Control Serpent",
            "Collect Quantum Orbs to grow",
            "Avoid walls and your own tail",
            "Grab power-ups for special abilities",
            "",
            "Press SPACE to select target score"
        ]
        
        start_y = SCREEN_HEIGHT // 2 + 50
        for i, instruction in enumerate(instructions):
            if instruction:
                color = NEON_GREEN if "SPACE" in instruction else WHITE
                text_surface = self.font_small.render(instruction, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 30))
                self.screen.blit(text_surface, text_rect)
                
        # High score
        if self.high_score > 0:
            high_score_text = f"HIGH SCORE: {self.high_score:06d}"
            high_score_surface = self.font_medium.render(high_score_text, True, QUANTUM_GOLD)
            high_score_rect = high_score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            self.screen.blit(high_score_surface, high_score_rect)
            
    def draw_target_select(self):
        """Draw target score selection screen"""
        # Title
        title_surface = self.font_large.render("SELECT TARGET SCORE", True, NEON_CYAN)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_surface, title_rect)
        
        # Target options
        for i, target in enumerate(self.target_options):
            y_pos = 350 + i * 80
            is_selected = i == self.selected_target
            
            # Button background
            button_width, button_height = 300, 60
            button_x = SCREEN_WIDTH // 2 - button_width // 2
            button_rect = pygame.Rect(button_x, y_pos - 30, button_width, button_height)
            
            if is_selected:
                # Selected button glow
                glow_surface = pygame.Surface((button_width + 20, button_height + 20), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*QUANTUM_GOLD, 100), (0, 0, button_width + 20, button_height + 20), border_radius=15)
                self.screen.blit(glow_surface, (button_x - 10, y_pos - 40))
                
                button_color = (*QUANTUM_GOLD, 150)
                text_color = WHITE
            else:
                button_color = (*NEON_CYAN, 80)
                text_color = NEON_CYAN
                
            # Button
            button_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
            pygame.draw.rect(button_surface, button_color, (0, 0, button_width, button_height), border_radius=10)
            pygame.draw.rect(button_surface, text_color, (0, 0, button_width, button_height), 3, border_radius=10)
            self.screen.blit(button_surface, (button_x, y_pos - 30))
            
            # Button text
            target_text = f"{target:,} POINTS"
            text_surface = self.font_medium.render(target_text, True, text_color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            self.screen.blit(text_surface, text_rect)
            
        # Instructions
        instructions = [
            "Use UP/DOWN arrows to select",
            "Press SPACE to start game",
            "Press ESC to return to menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = self.font_small.render(instruction, True, WHITE)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 650 + i * 25))
            self.screen.blit(text_surface, text_rect)
            
    def draw_victory(self):
        """Draw victory celebration screen"""
        self.victory_time += 1/60
        
        # Celebration fireworks
        if random.random() < 0.3:
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 200)
            colors = [QUANTUM_GOLD, NEON_CYAN, NEON_PURPLE, NEON_GREEN, NEON_ORANGE]
            self.particles.add_burst(x, y, random.choice(colors), 25)
            
        # Victory panel with animation
        panel_scale = 1.0 + math.sin(self.victory_time * 2) * 0.05
        panel_width = int(700 * panel_scale)
        panel_height = int(500 * panel_scale)
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        # Panel glow
        glow_surface = pygame.Surface((panel_width + 40, panel_height + 40), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*QUANTUM_GOLD, 60), (0, 0, panel_width + 40, panel_height + 40), border_radius=30)
        self.screen.blit(glow_surface, (panel_x - 20, panel_y - 20))
        
        # Main panel
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*DARK_BLUE, 200), (0, 0, panel_width, panel_height), border_radius=25)
        pygame.draw.rect(panel_surface, QUANTUM_GOLD, (0, 0, panel_width, panel_height), 4, border_radius=25)
        self.screen.blit(panel_surface, (panel_x, panel_y))
        
        # Animated victory text
        victory_pulse = 1.0 + math.sin(self.victory_time * 4) * 0.2
        victory_font_size = int(80 * victory_pulse)
        victory_font = pygame.font.Font(None, victory_font_size)
        
        # Victory text with rainbow effect
        victory_colors = [QUANTUM_GOLD, NEON_ORANGE, NEON_GREEN, NEON_CYAN, NEON_PURPLE]
        color_index = int(self.victory_time * 3) % len(victory_colors)
        victory_color = victory_colors[color_index]
        
        victory_surface = victory_font.render("VICTORY!", True, victory_color)
        victory_rect = victory_surface.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 100))
        self.screen.blit(victory_surface, victory_rect)
        
        # Target achieved text
        target_text = f"Target of {self.target_score:,} points achieved!"
        target_surface = self.font_medium.render(target_text, True, WHITE)
        target_rect = target_surface.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 180))
        self.screen.blit(target_surface, target_rect)
        
        # Final stats
        stats = [
            f"Final Score: {self.score:,}",
            f"Snake Length: {len(self.snake.segments)}",
            f"Level Reached: {self.level}"
        ]
        
        for i, stat in enumerate(stats):
            stat_surface = self.font_small.render(stat, True, NEON_CYAN)
            stat_rect = stat_surface.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 240 + i * 30))
            self.screen.blit(stat_surface, stat_rect)
            
        # Celebration message
        celebration_messages = [
            "🎉 QUANTUM MASTERY ACHIEVED! 🎉",
            "You are the ultimate Serpent Commander!",
            "The quantum realm bows to your skill!"
        ]
        
        for i, message in enumerate(celebration_messages):
            color = QUANTUM_GOLD if i == 0 else WHITE
            font = self.font_medium if i == 0 else self.font_small
            message_surface = font.render(message, True, color)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 350 + i * 30))
            self.screen.blit(message_surface, message_rect)
            
        # Instructions
        restart_surface = self.font_small.render("Press SPACE to play again or ESC for menu", True, NEON_GREEN)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 450))
        self.screen.blit(restart_surface, restart_rect)
            
    def draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*BLACK, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Game over panel
        panel_width, panel_height = 600, 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, GLASS_BLUE, (0, 0, panel_width, panel_height), border_radius=20)
        pygame.draw.rect(panel_surface, (*NEON_CYAN, 150), (0, 0, panel_width, panel_height), 3, border_radius=20)
        self.screen.blit(panel_surface, (panel_x, panel_y))
        
        # Game over text
        game_over_surface = self.font_large.render("QUANTUM COLLAPSE", True, NEON_CYAN)
        game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 80))
        self.screen.blit(game_over_surface, game_over_rect)
        
        # Stats
        stats = [
            f"Final Score: {self.score:06d}",
            f"Final Length: {len(self.snake.segments)}",
            f"Level Reached: {self.level}"
        ]
        
        for i, stat in enumerate(stats):
            stat_surface = self.font_medium.render(stat, True, WHITE)
            stat_rect = stat_surface.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 150 + i * 40))
            self.screen.blit(stat_surface, stat_rect)
            
        # New high score
        if self.score > self.high_score:
            new_high_surface = self.font_medium.render("NEW HIGH SCORE!", True, QUANTUM_GOLD)
            new_high_rect = new_high_surface.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 280))
            self.screen.blit(new_high_surface, new_high_rect)
            
        # Instructions
        restart_surface = self.font_small.render("Press SPACE to play again or ESC for menu", True, NEON_GREEN)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 350))
        self.screen.blit(restart_surface, restart_rect)
        
    def check_collisions(self):
        """Check all game collisions"""
        head_x, head_y = self.snake.segments[0].x, self.snake.segments[0].y
        
        # Orb collection
        for orb in self.orbs[:]:
            dx = head_x - orb.x
            dy = head_y - orb.y
            if math.sqrt(dx * dx + dy * dy) < GRID_SIZE:
                orb.collected = True
                self.orbs.remove(orb)
                self.snake.grow()
                self.score += 100 * self.level
                self.particles.add_burst(orb.x, orb.y, QUANTUM_GOLD, 20)
                
                # Always spawn multiple orbs, more if multi-orb is active
                orb_count = 5 if self.snake.multi_orb_time > 0 else 2
                for _ in range(orb_count):
                    self.spawn_orb()
                    
        # Power-up collection
        for powerup in self.powerups[:]:
            dx = head_x - powerup.x
            dy = head_y - powerup.y
            if math.sqrt(dx * dx + dy * dy) < GRID_SIZE:
                powerup.collected = True
                self.powerups.remove(powerup)
                self.particles.add_burst(powerup.x, powerup.y, powerup.colors[powerup.type], 15)
                
                # Apply power-up effect
                if powerup.type == 'speed':
                    self.snake.speed_boost_time = 5.0
                elif powerup.type == 'slow':
                    self.snake.slow_time = 8.0
                elif powerup.type == 'shield':
                    self.snake.shield_time = 10.0
                elif powerup.type == 'multi':
                    self.snake.multi_orb_time = 15.0
                    
                self.score += 50
                
    def update_difficulty(self):
        """Update game difficulty based on score"""
        new_level = (self.score // 1000) + 1
        if new_level > self.level:
            self.level = new_level
            self.snake.base_speed += 20
            self.particles.add_burst(SCREEN_WIDTH // 2, 100, NEON_GREEN, 30)
            
    def reset_game(self):
        """Reset game state"""
        self.snake = QuantumSerpent(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.orbs = []
        self.powerups = []
        self.particles = ParticleSystem()
        self.score = 0
        self.level = 1
        self.orb_spawn_timer = 0
        self.powerup_spawn_timer = 0
        # Spawn multiple initial orbs
        for _ in range(3):
            self.spawn_orb()
        
    def handle_events(self, event):
        """Handle pygame events"""
        if event.type == pygame.QUIT:
            return False
            
        elif event.type == pygame.KEYDOWN:
            if self.state == "menu":
                if event.key == pygame.K_SPACE:
                    self.state = "target_select"
                elif event.key == pygame.K_ESCAPE:
                    return False
                    
            elif self.state == "target_select":
                if event.key == pygame.K_UP:
                    self.selected_target = (self.selected_target - 1) % len(self.target_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_target = (self.selected_target + 1) % len(self.target_options)
                elif event.key == pygame.K_SPACE:
                    self.target_score = self.target_options[self.selected_target]
                    self.state = "playing"
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                    
            elif self.state == "playing":
                if event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                    
            elif self.state == "game_over":
                if event.key == pygame.K_SPACE:
                    self.state = "target_select"
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                    
            elif self.state == "victory":
                if event.key == pygame.K_SPACE:
                    self.state = "target_select"
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                    
        return True
        
    def update(self, dt: float):
        """Update game logic"""
        if self.state == "playing":
            keys = pygame.key.get_pressed()
            
            # Update snake
            self.snake.update(dt, keys, self.particles)
            
            # Update orbs
            for orb in self.orbs:
                orb.update(dt)
                
            # Update power-ups
            for powerup in self.powerups:
                powerup.update(dt)
                
            # Spawn power-ups occasionally
            self.powerup_spawn_timer += dt
            if self.powerup_spawn_timer > random.uniform(15, 25):
                self.powerup_spawn_timer = 0
                if len(self.powerups) < 2:
                    self.spawn_powerup()
                    
            # Check collisions
            self.check_collisions()
            
            # Update difficulty
            self.update_difficulty()
            
            # Check victory condition
            if self.score >= self.target_score:
                self.state = "victory"
                if self.score > self.high_score:
                    self.high_score = self.score
                self.victory_time = 0
                # Victory celebration particles
                for _ in range(50):
                    x = random.randint(0, SCREEN_WIDTH)
                    y = random.randint(0, SCREEN_HEIGHT)
                    colors = [QUANTUM_GOLD, NEON_CYAN, NEON_PURPLE, NEON_GREEN]
                    self.particles.add_burst(x, y, random.choice(colors), 15)
                    
            # Check game over
            elif self.snake.check_collision():
                self.state = "game_over"
                if self.score > self.high_score:
                    self.high_score = self.score
                    
        # Update particles
        self.particles.update(dt)
        
    def draw(self):
        """Draw everything"""
        # Background
        self.draw_background()
        
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "target_select":
            self.draw_target_select()
        elif self.state == "playing":
            # Game objects
            for orb in self.orbs:
                orb.draw(self.screen)
                
            for powerup in self.powerups:
                powerup.draw(self.screen)
                
            self.snake.draw(self.screen)
            
            # Effects
            self.particles.draw(self.screen)
            
            # UI
            self.draw_hud()
            
        elif self.state == "game_over":
            # Still draw game objects faded
            for orb in self.orbs:
                orb.draw(self.screen)
            for powerup in self.powerups:
                powerup.draw(self.screen)
            self.snake.draw(self.screen)
            self.particles.draw(self.screen)
            
            self.draw_game_over()
            
        elif self.state == "victory":
            # Still draw game objects faded
            for orb in self.orbs:
                orb.draw(self.screen)
            for powerup in self.powerups:
                powerup.draw(self.screen)
            self.snake.draw(self.screen)
            self.particles.draw(self.screen)
            
            self.draw_victory()
            
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if not self.handle_events(event):
                    running = False
                    
            # Update
            self.update(dt)
            
            # Draw
            self.draw()
            
            # Display
            pygame.display.flip()
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()