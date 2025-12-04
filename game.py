import pygame
import math
import random
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
TILE_SIZE = 40
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
DARK_GREEN = (34, 139, 34)
DARK_BLUE = (0, 0, 139)
LIGHT_BLUE = (173, 216, 230)
GOLD = (255, 215, 0)
PINK = (255, 192, 203)

class SoundManager:
    """Procedural sound generation"""
    def __init__(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.enabled = True
        except:
            self.enabled = False
    
    def play_jump(self):
        if self.enabled:
            self._play_tone(440, 0.1)
    
    def play_coin(self):
        if self.enabled:
            self._play_tone(880, 0.15)
    
    def play_hit(self):
        if self.enabled:
            self._play_tone(220, 0.2)
    
    def play_win(self):
        if self.enabled:
            for freq in [523, 659, 784]:
                self._play_tone(freq, 0.2)
    
    def _play_tone(self, frequency, duration):
        try:
            import numpy as np
            sample_rate = 22050
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2), dtype=np.int16)
            for i in range(frames):
                wave = int(2000 * math.sin(2 * math.pi * frequency * i / sample_rate))
                arr[i] = [wave, wave]
            sound = pygame.sndarray.make_sound(arr)
            sound.play()
        except:
            pass

class Particle:
    """Individual particle for effects"""
    def __init__(self, x, y, vx, vy, color, life, size=3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
    
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 300 * dt  # Gravity
        self.life -= dt
    
    def draw(self, screen, camera):
        if self.life > 0:
            alpha = self.life / self.max_life
            size = max(1, int(self.size * alpha))
            x = int(self.x - camera.x)
            y = int(self.y - camera.y)
            if 0 <= x <= SCREEN_WIDTH and 0 <= y <= SCREEN_HEIGHT:
                pygame.draw.circle(screen, self.color, (x, y), size)

class ParticleSystem:
    """Manages all particle effects"""
    def __init__(self):
        self.particles = []
    
    def add_jump_dust(self, x, y):
        for _ in range(5):
            vx = random.uniform(-50, 50)
            vy = random.uniform(-100, -20)
            self.particles.append(Particle(x, y, vx, vy, GRAY, 0.5, 2))
    
    def add_coin_sparkle(self, x, y):
        for _ in range(8):
            vx = random.uniform(-80, 80)
            vy = random.uniform(-120, -40)
            color = random.choice([GOLD, YELLOW, WHITE])
            self.particles.append(Particle(x, y, vx, vy, color, 0.8, 3))
    
    def add_enemy_burst(self, x, y):
        for _ in range(12):
            vx = random.uniform(-120, 120)
            vy = random.uniform(-150, -50)
            self.particles.append(Particle(x, y, vx, vy, RED, 1.0, 4))
    
    def update(self, dt):
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update(dt)
    
    def draw(self, screen, camera):
        for particle in self.particles:
            particle.draw(screen, camera)

class Camera:
    """Smooth following camera with bounds"""
    def __init__(self, world_width):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.world_width = world_width
    
    def update(self, target_x, target_y, dt):
        self.target_x = target_x - SCREEN_WIDTH // 2
        self.target_x = max(0, min(self.target_x, self.world_width - SCREEN_WIDTH))
        
        # Smooth following
        self.x += (self.target_x - self.x) * 8 * dt
        
        # Vertical camera (slight following)
        target_y = target_y - SCREEN_HEIGHT * 0.6
        self.y += (target_y - self.y) * 3 * dt
        self.y = max(-200, min(self.y, 200))

class Player:
    """Animated player character with realistic appearance"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width = 24
        self.height = 32
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.on_ground = False
        self.facing_right = True
        self.animation_time = 0
        self.jump_time = 0
        self.invulnerable = False
        self.invuln_time = 0
        self.walk_cycle = 0
    
    def update(self, dt, keys, level, particles, sound):
        # Input handling
        move_speed = 180
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            move_speed = 280
        
        # Smooth horizontal movement with delta-time
        target_vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target_vx = -move_speed
            self.facing_right = False
            self.walk_cycle += dt * 8
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target_vx = move_speed
            self.facing_right = True
            self.walk_cycle += dt * 8
        else:
            self.walk_cycle = 0
        
        # Smooth acceleration/deceleration
        accel_rate = 1200 * dt  # Acceleration rate
        if target_vx != 0:
            if abs(target_vx - self.vx) < accel_rate:
                self.vx = target_vx
            else:
                self.vx += accel_rate if target_vx > self.vx else -accel_rate
        else:
            # Friction when no input
            friction = 800 * dt
            if abs(self.vx) < friction:
                self.vx = 0
            else:
                self.vx -= friction if self.vx > 0 else -friction
        
        # Realistic jumping physics
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = -480  # Initial jump velocity
            self.jump_time = 0.15  # Short boost window
            sound.play_jump()
            particles.add_jump_dust(self.x + self.width//2, self.y + self.height)
        
        # Brief jump boost for variable height
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.jump_time > 0 and self.vy < 0:  # Only boost while going up
                self.vy -= 400 * dt  # Moderate boost
                self.jump_time -= dt
        else:
            self.jump_time = 0  # Stop boost immediately when key released
        
        # Consistent gravity - always pulls down
        self.vy += 1200 * dt  # Strong, consistent gravity
        
        # Move and check collisions
        self._move_and_collide(dt, level)
        
        # Check hazards and enemies
        result = self._check_interactions(level, particles, sound)
        
        # Update invulnerability
        if self.invulnerable:
            self.invuln_time -= dt
            if self.invuln_time <= 0:
                self.invulnerable = False
        
        self.animation_time += dt
        return result
    
    def _move_and_collide(self, dt, level):
        # Horizontal movement
        self.x += self.vx * dt
        self.rect.x = self.x
        
        for tile in level.tiles:
            if tile.solid and self.rect.colliderect(tile.rect):
                if self.vx > 0:
                    self.rect.right = tile.rect.left
                else:
                    self.rect.left = tile.rect.right
                self.x = self.rect.x
                self.vx = 0
        
        # Vertical movement
        self.y += self.vy * dt
        self.rect.y = self.y
        self.on_ground = False
        
        for tile in level.tiles:
            if tile.solid and self.rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.rect.bottom = tile.rect.top
                    self.y = self.rect.y
                    self.vy = 0
                    self.on_ground = True
                else:
                    self.rect.top = tile.rect.bottom
                    self.y = self.rect.y
                    self.vy = 0
        
        # Moving platforms
        for platform in level.moving_platforms:
            if self.rect.colliderect(platform.rect) and self.vy >= 0:
                if self.rect.bottom <= platform.rect.top + 15:
                    self.rect.bottom = platform.rect.top
                    self.y = self.rect.y
                    self.vy = 0
                    self.on_ground = True
    
    def _check_interactions(self, level, particles, sound):
        # Check hazards and falling off world
        for tile in level.tiles:
            if tile.type in ['water', 'lava'] and self.rect.colliderect(tile.rect):
                return 'death'
        
        # Check if player fell off the world
        if self.y > 900:
            return 'death'
        
        # Check enemies
        if not self.invulnerable:
            for enemy in level.enemies:
                if enemy.alive and self.rect.colliderect(enemy.rect):
                    if self.vy > 0 and self.rect.bottom <= enemy.rect.centery:
                        # Stomp enemy
                        enemy.alive = False
                        self.vy = -200
                        particles.add_enemy_burst(enemy.x + enemy.width//2, enemy.y + enemy.height//2)
                        sound.play_hit()
                    else:
                        # Take damage
                        self.invulnerable = True
                        self.invuln_time = 1.5
                        self.vx = -150 if self.x < enemy.x else 150
                        self.vy = -200
                        sound.play_hit()
                        return 'hit'
        
        # Check collectibles
        for collectible in level.collectibles:
            if not collectible.collected and self.rect.colliderect(collectible.rect):
                collectible.collected = True
                particles.add_coin_sparkle(collectible.x + collectible.width//2, 
                                         collectible.y + collectible.height//2)
                sound.play_coin()
                # Hearts increase lives
                if collectible.type == 'gem':
                    return 'heart_collected'
        
        return 'normal'
    
    def draw(self, screen, camera):
        if self.invulnerable and int(self.invuln_time * 15) % 2:
            return
        
        x = int(self.x - camera.x)
        y = int(self.y - camera.y)
        
        # Shadow
        pygame.draw.ellipse(screen, (0, 0, 0, 50), (x + 2, y + self.height + 2, 20, 8))
        
        # Body animation offsets
        walk_offset = math.sin(self.walk_cycle) * 2 if abs(self.vx) > 10 else 0
        jump_stretch = -4 if not self.on_ground else 0
        
        # Enhanced body with overalls
        body_color = BLUE
        pygame.draw.ellipse(screen, body_color, (x + 5, y + 12 + walk_offset, 14, 18 + jump_stretch))
        # Overalls straps
        pygame.draw.rect(screen, BLUE, (x + 8, y + 12, 3, 8))
        pygame.draw.rect(screen, BLUE, (x + 13, y + 12, 3, 8))
        # Overalls buttons
        pygame.draw.circle(screen, YELLOW, (x + 9, y + 14), 1)
        pygame.draw.circle(screen, YELLOW, (x + 15, y + 14), 1)
        
        # Head with better proportions
        head_color = (255, 220, 177)  # Skin tone
        pygame.draw.circle(screen, head_color, (x + 12, y + 8), 9)
        # Face outline
        pygame.draw.circle(screen, (240, 200, 160), (x + 12, y + 8), 9, 2)
        
        # Mustache (Mario style)
        mustache_color = BROWN
        pygame.draw.ellipse(screen, mustache_color, (x + 8, y + 10, 8, 3))
        
        # Hat (draw before eyes so eyes are visible)
        pygame.draw.circle(screen, RED, (x + 12, y + 3), 10)
        pygame.draw.rect(screen, RED, (x + 7, y, 10, 6))
        # Hat brim with shadow
        pygame.draw.ellipse(screen, RED, (x + 3, y + 8, 18, 7))
        pygame.draw.ellipse(screen, (180, 0, 0), (x + 3, y + 9, 18, 5))
        # Hat emblem
        pygame.draw.circle(screen, WHITE, (x + 12, y + 4), 3)
        pygame.draw.rect(screen, RED, (x + 11, y + 2, 2, 4))
        
        # Eyes (larger and more expressive)
        eye_offset = 1 if self.facing_right else -1
        pygame.draw.circle(screen, WHITE, (x + 8 + eye_offset, y + 7), 4)
        pygame.draw.circle(screen, WHITE, (x + 16 + eye_offset, y + 7), 4)
        pygame.draw.circle(screen, BLACK, (x + 9 + eye_offset, y + 7), 3)
        pygame.draw.circle(screen, BLACK, (x + 17 + eye_offset, y + 7), 3)
        # Eye shine
        pygame.draw.circle(screen, WHITE, (x + 10 + eye_offset, y + 6), 1)
        pygame.draw.circle(screen, WHITE, (x + 18 + eye_offset, y + 6), 1)
        
        # Nose
        pygame.draw.circle(screen, (255, 200, 160), (x + 12, y + 9), 2)
        
        # Arms with gloves
        arm_swing = math.sin(self.walk_cycle + math.pi) * 4 if abs(self.vx) > 10 else 0
        if self.facing_right:
            # Right arm
            pygame.draw.circle(screen, head_color, (x + 22, y + 16 - arm_swing), 4)
            pygame.draw.circle(screen, WHITE, (x + 22, y + 16 - arm_swing), 4, 2)  # Glove
            # Left arm
            pygame.draw.circle(screen, head_color, (x + 2, y + 16 + arm_swing), 4)
            pygame.draw.circle(screen, WHITE, (x + 2, y + 16 + arm_swing), 4, 2)  # Glove
        else:
            # Left arm
            pygame.draw.circle(screen, head_color, (x + 2, y + 16 - arm_swing), 4)
            pygame.draw.circle(screen, WHITE, (x + 2, y + 16 - arm_swing), 4, 2)  # Glove
            # Right arm
            pygame.draw.circle(screen, head_color, (x + 22, y + 16 + arm_swing), 4)
            pygame.draw.circle(screen, WHITE, (x + 22, y + 16 + arm_swing), 4, 2)  # Glove
        
        # Legs with better animation
        leg_offset = math.sin(self.walk_cycle) * 5 if abs(self.vx) > 10 else 0
        # Left leg
        pygame.draw.rect(screen, BROWN, (x + 7 + leg_offset, y + 26, 4, 6))
        pygame.draw.rect(screen, BLACK, (x + 6 + leg_offset, y + 30, 6, 3))  # Shoe
        # Right leg
        pygame.draw.rect(screen, BROWN, (x + 13 - leg_offset, y + 26, 4, 6))
        pygame.draw.rect(screen, BLACK, (x + 12 - leg_offset, y + 30, 6, 3))  # Shoe

class Enemy:
    """Goomba-like enemy with simple AI"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vx = -60
        self.vy = 0
        self.alive = True
        self.animation_time = 0
        self.on_ground = False
    
    def update(self, dt, level):
        if not self.alive:
            return
        
        self.animation_time += dt
        
        # Physics
        self.vy += 800 * dt
        
        # Move horizontally
        self.x += self.vx * dt
        self.rect.x = self.x
        
        # Check horizontal collisions
        for tile in level.tiles:
            if tile.solid and self.rect.colliderect(tile.rect):
                self.vx = -self.vx
                if self.vx > 0:
                    self.rect.left = tile.rect.right
                else:
                    self.rect.right = tile.rect.left
                self.x = self.rect.x
        
        # Move vertically
        self.y += self.vy * dt
        self.rect.y = self.y
        self.on_ground = False
        
        # Check vertical collisions
        for tile in level.tiles:
            if tile.solid and self.rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.rect.bottom = tile.rect.top
                    self.y = self.rect.y
                    self.vy = 0
                    self.on_ground = True
        
        # Edge detection
        if self.on_ground:
            check_x = self.x + (25 if self.vx > 0 else -25)
            check_y = self.y + 25
            ground_ahead = False
            
            for tile in level.tiles:
                if tile.solid and tile.rect.collidepoint(check_x, check_y):
                    ground_ahead = True
                    break
            
            if not ground_ahead:
                self.vx = -self.vx
    
    def draw(self, screen, camera):
        if not self.alive:
            return
        
        x = int(self.x - camera.x)
        y = int(self.y - camera.y)
        
        # Body (brown mushroom-like)
        body_bob = math.sin(self.animation_time * 4) * 1
        pygame.draw.ellipse(screen, BROWN, (x, y + body_bob, self.width, self.height))
        
        # Spots
        pygame.draw.circle(screen, (101, 67, 33), (x + 5, y + 6 + body_bob), 2)
        pygame.draw.circle(screen, (101, 67, 33), (x + 13, y + 8 + body_bob), 2)
        
        # Eyes
        pygame.draw.circle(screen, WHITE, (x + 6, y + 10 + body_bob), 2)
        pygame.draw.circle(screen, WHITE, (x + 14, y + 10 + body_bob), 2)
        pygame.draw.circle(screen, BLACK, (x + 6, y + 10 + body_bob), 1)
        pygame.draw.circle(screen, BLACK, (x + 14, y + 10 + body_bob), 1)
        
        # Feet
        pygame.draw.ellipse(screen, (101, 67, 33), (x - 2, y + 16, 6, 4))
        pygame.draw.ellipse(screen, (101, 67, 33), (x + 16, y + 16, 6, 4))

class Collectible:
    """Animated coins and power-ups"""
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.rect = pygame.Rect(x + 4, y + 4, 8, 8)
        self.type = item_type
        self.collected = False
        self.animation_time = 0
        self.bob_offset = 0
    
    def update(self, dt):
        self.animation_time += dt
        self.bob_offset = math.sin(self.animation_time * 3) * 3
    
    def draw(self, screen, camera):
        if self.collected:
            return
        
        x = int(self.x - camera.x)
        y = int(self.y - camera.y + self.bob_offset)
        
        if self.type == 'coin':
            # Spinning coin effect
            spin = math.sin(self.animation_time * 6)
            width = max(2, int(12 * abs(spin)))
            
            # Outer glow
            pygame.draw.ellipse(screen, YELLOW, (x - 2, y - 2, 20, 20))
            # Main coin
            pygame.draw.ellipse(screen, GOLD, (x + 8 - width//2, y + 4, width, 12))
            # Highlight
            pygame.draw.ellipse(screen, WHITE, (x + 8 - width//4, y + 6, width//2, 3))
        
        elif self.type == 'gem':
            # Heart shape
            # Left circle of heart
            pygame.draw.circle(screen, RED, (x + 6, y + 6), 4)
            # Right circle of heart
            pygame.draw.circle(screen, RED, (x + 10, y + 6), 4)
            # Bottom triangle of heart
            heart_points = [(x + 2, y + 8), (x + 14, y + 8), (x + 8, y + 14)]
            pygame.draw.polygon(screen, RED, heart_points)
            # Highlight
            pygame.draw.circle(screen, PINK, (x + 5, y + 5), 2)
            pygame.draw.circle(screen, PINK, (x + 9, y + 5), 2)

class Tile:
    """Environment tiles with visual styling"""
    def __init__(self, x, y, tile_type):
        self.x = x
        self.y = y
        self.type = tile_type
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.solid = tile_type in ['grass', 'stone', 'wood']
    
    def draw(self, screen, camera):
        x = int(self.x - camera.x)
        y = int(self.y - camera.y)
        
        if self.type == 'grass':
            # Grass block with texture
            pygame.draw.rect(screen, DARK_GREEN, (x, y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, GREEN, (x, y, TILE_SIZE, 8))
            # Grass blades
            for i in range(0, TILE_SIZE, 4):
                pygame.draw.line(screen, GREEN, (x + i, y), (x + i, y + 6), 2)
            # Border
            pygame.draw.rect(screen, (0, 100, 0), (x, y, TILE_SIZE, TILE_SIZE), 2)
        
        elif self.type == 'stone':
            # Stone block
            pygame.draw.rect(screen, GRAY, (x, y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, WHITE, (x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4))
            pygame.draw.rect(screen, (64, 64, 64), (x, y, TILE_SIZE, TILE_SIZE), 2)
        
        elif self.type == 'wood':
            # Wooden plank
            pygame.draw.rect(screen, BROWN, (x, y, TILE_SIZE, TILE_SIZE))
            # Wood grain
            for i in range(0, TILE_SIZE, 8):
                pygame.draw.line(screen, (101, 67, 33), (x, y + i), (x + TILE_SIZE, y + i))
            pygame.draw.rect(screen, (101, 67, 33), (x, y, TILE_SIZE, TILE_SIZE), 2)
        
        elif self.type == 'water':
            # Animated water
            wave = math.sin(time.time() * 3 + x * 0.1) * 2
            pygame.draw.rect(screen, BLUE, (x, y + wave, TILE_SIZE, TILE_SIZE - wave))
            pygame.draw.rect(screen, LIGHT_BLUE, (x, y + wave, TILE_SIZE, 4))
        
        elif self.type == 'lava':
            # Animated lava
            bubble = math.sin(time.time() * 4 + x * 0.15) * 3
            pygame.draw.rect(screen, RED, (x, y + bubble, TILE_SIZE, TILE_SIZE - bubble))
            pygame.draw.rect(screen, ORANGE, (x, y + bubble, TILE_SIZE, 6))

class MovingPlatform:
    """Animated moving platforms"""
    def __init__(self, x, y, width, direction, distance, speed):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.width = width
        self.height = 16
        self.rect = pygame.Rect(x, y, width, self.height)
        self.direction = direction
        self.distance = distance
        self.speed = speed
        self.progress = 0
    
    def update(self, dt):
        self.progress += self.speed * dt
        
        if self.direction == 'horizontal':
            self.x = self.start_x + math.sin(self.progress) * self.distance
        else:
            self.y = self.start_y + math.sin(self.progress) * self.distance
        
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, screen, camera):
        x = int(self.x - camera.x)
        y = int(self.y - camera.y)
        
        # Platform with metallic look
        pygame.draw.rect(screen, GRAY, (x, y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (x + 2, y + 2, self.width - 4, 4))
        pygame.draw.rect(screen, (64, 64, 64), (x, y, self.width, self.height), 2)
        
        # Rivets
        for i in range(8, self.width - 8, 16):
            pygame.draw.circle(screen, (32, 32, 32), (x + i, y + 8), 2)

class Level:
    """Game level with all objects"""
    def __init__(self, level_data):
        self.tiles = []
        self.moving_platforms = []
        self.enemies = []
        self.collectibles = []
        self.goal_x = level_data.get('goal_x', 3000)
        self.goal_y = level_data.get('goal_y', 400)
        self.width = 0
        
        # Create tiles from map
        tile_map = level_data['map']
        for y, row in enumerate(tile_map):
            for x, tile_char in enumerate(row):
                if tile_char != ' ':
                    tile_x = x * TILE_SIZE
                    tile_y = y * TILE_SIZE
                    self.width = max(self.width, tile_x + TILE_SIZE)
                    
                    tile_types = {
                        '#': 'grass', 'S': 'stone', 'W': 'wood',
                        '~': 'water', 'L': 'lava'
                    }
                    if tile_char in tile_types:
                        self.tiles.append(Tile(tile_x, tile_y, tile_types[tile_char]))
        
        # Add moving platforms
        for platform_data in level_data.get('platforms', []):
            self.moving_platforms.append(MovingPlatform(**platform_data))
        
        # Add enemies
        for enemy_data in level_data.get('enemies', []):
            self.enemies.append(Enemy(enemy_data['x'], enemy_data['y']))
        
        # Add collectibles
        for collectible_data in level_data.get('collectibles', []):
            self.collectibles.append(Collectible(**collectible_data))
    
    def update(self, dt):
        for platform in self.moving_platforms:
            platform.update(dt)
        for enemy in self.enemies:
            enemy.update(dt, self)
        for collectible in self.collectibles:
            collectible.update(dt)
    
    def draw_background(self, screen, camera):
        # Sky gradient
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(135 + (255 - 135) * color_ratio)
            g = int(206 + (165 - 206) * color_ratio)
            b = int(235 + (0 - 235) * color_ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Sun with rays
        sun_x = 200 - camera.x * 0.05
        sun_y = 80
        
        # Sun rays
        ray_time = time.time() * 2
        for i in range(8):
            angle = (i * 45 + ray_time * 10) * math.pi / 180
            ray_end_x = sun_x + math.cos(angle) * 80
            ray_end_y = sun_y + math.sin(angle) * 80
            pygame.draw.line(screen, YELLOW, (int(sun_x), int(sun_y)), 
                           (int(ray_end_x), int(ray_end_y)), 3)
        
        # Sun glow (multiple layers)
        for radius in range(50, 20, -5):
            alpha = 255 - (50 - radius) * 6
            color = (255, 255, min(255, 150 + alpha//2))
            pygame.draw.circle(screen, color, (int(sun_x), int(sun_y)), radius)
        
        # Sun core
        pygame.draw.circle(screen, YELLOW, (int(sun_x), int(sun_y)), 25)
        pygame.draw.circle(screen, WHITE, (int(sun_x - 8), int(sun_y - 8)), 8)
        
        # Clouds
        cloud_positions = [(300, 120), (800, 80), (1200, 140), (1600, 100)]
        for cloud_x, cloud_y in cloud_positions:
            x = cloud_x - camera.x * 0.3
            if -100 < x < SCREEN_WIDTH + 100:
                # Cloud made of circles
                pygame.draw.circle(screen, WHITE, (int(x), int(cloud_y)), 25)
                pygame.draw.circle(screen, WHITE, (int(x + 20), int(cloud_y)), 30)
                pygame.draw.circle(screen, WHITE, (int(x + 40), int(cloud_y)), 25)
                pygame.draw.circle(screen, WHITE, (int(x + 15), int(cloud_y - 15)), 20)
        
        # Mountains (far background) - more realistic with multiple layers
        # Back mountains
        back_mountain_points = [
            (0, SCREEN_HEIGHT), (150, 250), (300, 280), (450, 220), 
            (600, 260), (750, 200), (900, 240), (1050, 180), 
            (1200, 220), (1350, 160), (1500, 200), (SCREEN_WIDTH + 200, SCREEN_HEIGHT)
        ]
        adjusted_back_points = []
        for px, py in back_mountain_points:
            x = px - camera.x * 0.1
            adjusted_back_points.append((x, py))
        pygame.draw.polygon(screen, (80, 80, 100), adjusted_back_points)
        
        # Front mountains
        front_mountain_points = [
            (0, SCREEN_HEIGHT), (250, 320), (500, 280), (750, 340), 
            (1000, 300), (1250, 360), (1500, 320), (SCREEN_WIDTH + 200, SCREEN_HEIGHT)
        ]
        adjusted_front_points = []
        for px, py in front_mountain_points:
            x = px - camera.x * 0.15
            adjusted_front_points.append((x, py))
        pygame.draw.polygon(screen, (120, 120, 140), adjusted_front_points)
        
        # Enhanced trees with outlines and shadows
        tree_positions = [200, 450, 750, 1100, 1450, 1800, 2200, 2600, 3000, 3400]
        for i, tree_x in enumerate(tree_positions):
            x = tree_x - camera.x * 0.5
            if -80 < x < SCREEN_WIDTH + 80:
                tree_height = 60 + (i % 3) * 20
                trunk_width = 12 + (i % 2) * 4
                
                # Tree shadow
                shadow_offset = 8
                pygame.draw.rect(screen, (0, 0, 0, 50), 
                               (int(x - trunk_width//2 + shadow_offset), 
                                int(SCREEN_HEIGHT - 150 - tree_height + shadow_offset), 
                                trunk_width, tree_height))
                
                # Tree trunk with outline
                trunk_rect = (int(x - trunk_width//2), int(SCREEN_HEIGHT - 150 - tree_height), trunk_width, tree_height)
                pygame.draw.rect(screen, BROWN, trunk_rect)
                pygame.draw.rect(screen, (80, 40, 20), trunk_rect, 2)
                
                # Bark texture
                for bark_y in range(0, tree_height, 8):
                    pygame.draw.line(screen, (101, 67, 33), 
                                   (int(x - trunk_width//2), int(SCREEN_HEIGHT - 150 - bark_y)), 
                                   (int(x + trunk_width//2), int(SCREEN_HEIGHT - 150 - bark_y)))
                
                # Tree leaves with shadows and outlines
                leaf_y = SCREEN_HEIGHT - 160 - tree_height
                # Leaf shadows
                pygame.draw.circle(screen, (0, 50, 0, 80), (int(x + 5), int(leaf_y + 5)), 35)
                pygame.draw.circle(screen, (0, 50, 0, 80), (int(x - 10), int(leaf_y - 5)), 25)
                pygame.draw.circle(screen, (0, 50, 0, 80), (int(x + 20), int(leaf_y)), 28)
                
                # Main leaves
                pygame.draw.circle(screen, DARK_GREEN, (int(x), int(leaf_y)), 35)
                pygame.draw.circle(screen, GREEN, (int(x - 15), int(leaf_y - 10)), 25)
                pygame.draw.circle(screen, GREEN, (int(x + 15), int(leaf_y - 5)), 28)
                pygame.draw.circle(screen, (0, 200, 0), (int(x), int(leaf_y - 15)), 20)
                
                # Leaf outlines
                pygame.draw.circle(screen, (0, 100, 0), (int(x), int(leaf_y)), 35, 2)
                pygame.draw.circle(screen, (0, 120, 0), (int(x - 15), int(leaf_y - 10)), 25, 2)
                pygame.draw.circle(screen, (0, 120, 0), (int(x + 15), int(leaf_y - 5)), 28, 2)
    
    def draw(self, screen, camera):
        # Draw tiles with shadows
        for tile in self.tiles:
            if tile.x - camera.x > -TILE_SIZE and tile.x - camera.x < SCREEN_WIDTH + TILE_SIZE:
                # Platform shadow
                shadow_x = int(tile.x - camera.x + 3)
                shadow_y = int(tile.y - camera.y + 3)
                shadow_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
                shadow_surface.set_alpha(60)
                shadow_surface.fill((0, 0, 0))
                screen.blit(shadow_surface, (shadow_x, shadow_y))
                
                tile.draw(screen, camera)
        
        # Draw moving platforms with shadows
        for platform in self.moving_platforms:
            # Platform shadow
            shadow_x = int(platform.x - camera.x + 4)
            shadow_y = int(platform.y - camera.y + 4)
            shadow_surface = pygame.Surface((platform.width, platform.height))
            shadow_surface.set_alpha(80)
            shadow_surface.fill((0, 0, 0))
            screen.blit(shadow_surface, (shadow_x, shadow_y))
            
            platform.draw(screen, camera)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen, camera)
        
        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw(screen, camera)
        
        # Draw winning flag on ground when player reaches 95% progress
        player_progress = (camera.x + SCREEN_WIDTH//2) / self.goal_x
        if player_progress >= 0.95:  # Show flag when close to end
            flag_x = int(self.goal_x - camera.x)
            flag_y = int(self.goal_y - camera.y)
            if -50 < flag_x < SCREEN_WIDTH + 50:
                # Victory flag pole on ground (shorter)
                pole_height = 80
                pygame.draw.rect(screen, BROWN, (flag_x, flag_y - pole_height, 8, pole_height))
                # Pole segments
                for segment in range(0, pole_height, 15):
                    pygame.draw.line(screen, (101, 67, 33), 
                                   (flag_x, flag_y - pole_height + segment), 
                                   (flag_x + 8, flag_y - pole_height + segment), 2)
                
                # Victory flag with animation
                flag_wave = math.sin(time.time() * 4) * 4
                flag_points = [
                    (flag_x + 8, flag_y - pole_height + 10),
                    (flag_x + 50 + flag_wave, flag_y - pole_height + 15),
                    (flag_x + 45 + flag_wave, flag_y - pole_height + 35),
                    (flag_x + 8, flag_y - pole_height + 30)
                ]
                pygame.draw.polygon(screen, GREEN, flag_points)
                pygame.draw.polygon(screen, DARK_GREEN, flag_points, 2)
                
                # Victory symbol on flag
                pygame.draw.circle(screen, GOLD, (flag_x + 25, flag_y - pole_height + 22), 6)
                pygame.draw.rect(screen, WHITE, (flag_x + 22, flag_y - pole_height + 19, 6, 6))
                
                # Enhanced sparkle effect for victory
                sparkle_time = time.time() * 8
                for i in range(6):
                    angle = (i * 60 + sparkle_time * 40) * math.pi / 180
                    sparkle_x = flag_x + 30 + math.cos(angle) * 20
                    sparkle_y = flag_y - pole_height + 22 + math.sin(angle) * 15
                    pygame.draw.circle(screen, GOLD, (int(sparkle_x), int(sparkle_y)), 3)
                
                # "FINISH" text above flag
                finish_font = pygame.font.Font(None, 36)
                finish_text = finish_font.render("FINISH!", True, GOLD)
                screen.blit(finish_text, (flag_x - 20, flag_y - pole_height - 30))

class HUD:
    """Heads-up display with polished UI"""
    def __init__(self):
        self.font_large = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
    
    def draw(self, screen, score, coins, lives, time_left, progress):
        # Modern gradient top bar
        for y in range(90):
            alpha = 200 - (y * 2)
            color = (20, 20, 40, alpha)
            bar_surface = pygame.Surface((SCREEN_WIDTH, 1))
            bar_surface.set_alpha(alpha)
            bar_surface.fill((20, 20, 40))
            screen.blit(bar_surface, (0, y))
        
        # Rounded rectangle background
        hud_rect = pygame.Rect(10, 10, SCREEN_WIDTH - 20, 70)
        pygame.draw.rect(screen, (0, 0, 0, 100), hud_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255, 50), hud_rect, 2, border_radius=15)
        
        # Score with shadow
        shadow_text = self.font_large.render(f"Score: {score:06d}", True, (0, 0, 0))
        screen.blit(shadow_text, (22, 17))
        score_text = self.font_large.render(f"Score: {score:06d}", True, WHITE)
        screen.blit(score_text, (20, 15))
        
        # Animated glowing coin
        glow_time = time.time() * 4
        glow_size = 15 + math.sin(glow_time) * 3
        pygame.draw.circle(screen, (255, 215, 0, 100), (220, 30), int(glow_size))
        pygame.draw.circle(screen, GOLD, (220, 30), 12)
        pygame.draw.circle(screen, YELLOW, (220, 30), 8)
        pygame.draw.circle(screen, WHITE, (218, 28), 3)
        
        coins_shadow = self.font_large.render(f"x {coins}", True, (0, 0, 0))
        screen.blit(coins_shadow, (242, 17))
        coins_text = self.font_large.render(f"x {coins}", True, WHITE)
        screen.blit(coins_text, (240, 15))
        
        # Modern heart icons
        for i in range(lives):
            heart_x = 350 + i * 35
            heart_y = 25
            # Heart shadow
            pygame.draw.circle(screen, (100, 0, 0), (heart_x + 1, heart_y + 1), 8)
            pygame.draw.circle(screen, (100, 0, 0), (heart_x + 11, heart_y + 1), 8)
            pygame.draw.polygon(screen, (100, 0, 0), [
                (heart_x - 7, heart_y + 4), (heart_x + 19, heart_y + 4), (heart_x + 6, heart_y + 16)
            ])
            # Heart main
            pygame.draw.circle(screen, RED, (heart_x, heart_y), 8)
            pygame.draw.circle(screen, RED, (heart_x + 10, heart_y), 8)
            pygame.draw.polygon(screen, RED, [
                (heart_x - 8, heart_y + 3), (heart_x + 18, heart_y + 3), (heart_x + 5, heart_y + 15)
            ])
            # Heart highlight
            pygame.draw.circle(screen, PINK, (heart_x - 2, heart_y - 2), 3)
        
        # Timer with shadow
        timer_shadow = self.font_large.render(f"Time: {int(time_left)}", True, (0, 0, 0))
        screen.blit(timer_shadow, (SCREEN_WIDTH - 198, 17))
        timer_text = self.font_large.render(f"Time: {int(time_left)}", True, WHITE)
        screen.blit(timer_text, (SCREEN_WIDTH - 200, 15))
        
        # Modern progress bar
        bar_width = 200
        bar_height = 16
        bar_x = SCREEN_WIDTH - bar_width - 20
        bar_y = 52
        
        # Progress bar shadow
        shadow_rect = pygame.Rect(bar_x + 2, bar_y + 2, bar_width, bar_height)
        pygame.draw.rect(screen, (0, 0, 0, 80), shadow_rect, border_radius=8)
        
        # Progress bar background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect, border_radius=8)
        
        # Progress fill with gradient
        progress_width = int(bar_width * min(1.0, progress))
        if progress_width > 0:
            if progress < 0.3:
                color1, color2 = (255, 100, 100), (200, 50, 50)
            elif progress < 0.6:
                color1, color2 = (255, 200, 100), (255, 150, 50)
            elif progress < 0.9:
                color1, color2 = (255, 255, 100), (255, 200, 50)
            else:
                color1, color2 = (100, 255, 100), (50, 200, 50)
            
            for i in range(bar_height):
                ratio = i / bar_height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                pygame.draw.rect(screen, (r, g, b), (bar_x, bar_y + i, progress_width, 1))
        
        # Progress bar border
        pygame.draw.rect(screen, WHITE, bg_rect, 2, border_radius=8)
        
        # Progress text with shadow
        progress_shadow = self.font_small.render(f"Progress: {int(progress*100)}%", True, (0, 0, 0))
        screen.blit(progress_shadow, (bar_x + 1, bar_y - 19))
        progress_text = self.font_small.render(f"Progress: {int(progress*100)}%", True, WHITE)
        screen.blit(progress_text, (bar_x, bar_y - 20))

class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Escape Rush - Platformer Adventure")
        self.clock = pygame.time.Clock()
        
        # Game systems
        self.sound = SoundManager()
        self.particles = ParticleSystem()
        self.hud = HUD()
        
        # Game state
        self.state = 'menu'  # menu, playing, paused, game_over, win
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.level_time = 300
        self.start_time = 0
        
        # Create level
        self.level_data = self._create_level_data()
        self.level = Level(self.level_data)
        self.camera = Camera(self.level.width)
        self.player = None
        
        # Menu animation
        self.menu_time = 0
        self.title_bounce = 0
    
    def _create_level_data(self):
        """Create the game level"""
        # Level map with varied terrain - up and down movement
        level_map = [
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "                                                                                                                                                    ",
            "########  #  ##  ###  ####  ###  ##  ###  ####  #####  ####  ###  ####  #####  ######  #####  ####  ###  ##  #  ########",
        ]
        
        return {
            'map': level_map,
            'platforms': [
                {'x': 1300, 'y': 650, 'width': 80, 'direction': 'horizontal', 'distance': 40, 'speed': 1},
                {'x': 1600, 'y': 600, 'width': 80, 'direction': 'vertical', 'distance': 30, 'speed': 1.2},
            ],
            'enemies': [
                {'x': 700, 'y': 740},   # Mid-level challenge
                {'x': 1300, 'y': 740},  # Near end area
            ],
            'collectibles': [
                {'x': 250, 'y': 740, 'item_type': 'coin'},   # Start area
                {'x': 400, 'y': 740, 'item_type': 'coin'},   # Ground level
                {'x': 550, 'y': 700, 'item_type': 'coin'},   # Small platform
                {'x': 650, 'y': 680, 'item_type': 'gem'},    # Heart - jump height
                {'x': 800, 'y': 740, 'item_type': 'coin'},   # Ground level
                {'x': 900, 'y': 700, 'item_type': 'coin'},   # Small platform
                {'x': 1050, 'y': 740, 'item_type': 'coin'},  # Ground level
                {'x': 1200, 'y': 680, 'item_type': 'gem'},   # Heart - jump height
                {'x': 1350, 'y': 740, 'item_type': 'coin'},  # Ground level
                {'x': 1500, 'y': 700, 'item_type': 'coin'},  # Small platform
                {'x': 1650, 'y': 740, 'item_type': 'coin'},  # Ground level
                {'x': 1800, 'y': 680, 'item_type': 'gem'},   # Final heart
            ],
            'goal_x': 2000,
            'goal_y': 720
        }
    
    def start_game(self):
        """Initialize a new game"""
        self.player = Player(100, 600)
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.level_time = 300
        self.start_time = time.time()
        self.camera.x = 0
        self.camera.y = 0
        
        # Reset level
        self.level = Level(self.level_data)
        self.state = 'playing'
    
    def update_playing(self, dt, keys):
        """Update game during play"""
        # Update game objects
        self.level.update(dt)
        result = self.player.update(dt, keys, self.level, self.particles, self.sound)
        
        # Handle player state
        if result == 'death' or result == 'hit':
            self.lives -= 1
            if self.lives <= 0:
                self.state = 'game_over'
            else:
                self.player = Player(100, 600)
                self.camera.x = 0
            return  # Don't update timer when player dies
        elif result == 'heart_collected':
            self.lives += 1  # Increase life when heart collected
        
        # Update timer only when player is alive and playing
        self.level_time -= dt
        if self.level_time <= 0:
            self.lives -= 1
            if self.lives <= 0:
                self.state = 'game_over'
            else:
                self.start_game()
            return
        
        # Update camera
        self.camera.update(self.player.x, self.player.y, dt)
        
        # Update particles
        self.particles.update(dt)
        
        # Count collected items
        collected_coins = sum(1 for c in self.level.collectibles if c.collected and c.type == 'coin')
        collected_gems = sum(1 for c in self.level.collectibles if c.collected and c.type == 'gem')
        self.coins = collected_coins
        self.score = collected_coins * 100 + collected_gems * 500
        
        # Check win condition - game ends at 100% progress
        progress = min(1.0, self.player.x / self.level.goal_x)
        if progress >= 1.0:
            self.sound.play_win()
            # Add celebration particles
            for _ in range(30):
                self.particles.add_coin_sparkle(self.player.x + random.randint(-20, 20), 
                                              self.player.y + random.randint(-20, 20))
            self.state = 'win'
    
    def draw_menu(self):
        """Draw modern main menu"""
        # Animated background
        self.level.draw_background(self.screen, self.camera)
        
        # Floating title animation
        self.title_bounce += 0.03
        title_y = 180 + math.sin(self.title_bounce) * 12
        title_scale = 1.0 + math.sin(self.title_bounce * 2) * 0.05
        
        # Title glow effect
        for glow_size in range(8, 0, -2):
            glow_alpha = 50 - (glow_size * 6)
            glow_font = pygame.font.Font(None, int(84 * title_scale) + glow_size)
            glow_text = glow_font.render("ESCAPE RUSH", True, (255, 215, 0, glow_alpha))
            glow_rect = glow_text.get_rect(center=(SCREEN_WIDTH//2, title_y))
            self.screen.blit(glow_text, glow_rect)
        
        # Title shadow
        shadow_font = pygame.font.Font(None, int(84 * title_scale))
        title_shadow = shadow_font.render("ESCAPE RUSH", True, (0, 0, 0, 150))
        title_shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH//2 + 4, title_y + 4))
        self.screen.blit(title_shadow, title_shadow_rect)
        
        # Main title
        title_font = pygame.font.Font(None, int(84 * title_scale))
        title = title_font.render("ESCAPE RUSH", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, title_y))
        self.screen.blit(title, title_rect)
        
        # Fade-in menu options
        fade_alpha = min(255, int(self.menu_time * 200))
        
        # Modern button backgrounds
        button_font = pygame.font.Font(None, 48)
        mouse_pos = pygame.mouse.get_pos()
        
        # Play button with rounded background
        play_hover = 400 < mouse_pos[1] < 450
        play_bg_color = (100, 150, 255, 100) if play_hover else (50, 50, 100, 80)
        play_bg = pygame.Surface((300, 50))
        play_bg.set_alpha(fade_alpha)
        play_bg.fill(play_bg_color[:3])
        self.screen.blit(play_bg, (SCREEN_WIDTH//2 - 150, 400))
        
        play_color = WHITE if play_hover else (200, 200, 200)
        play_text = button_font.render("PLAY (Space)", True, (*play_color, fade_alpha))
        play_rect = play_text.get_rect(center=(SCREEN_WIDTH//2, 425))
        self.screen.blit(play_text, play_rect)
        
        # Instructions with fade
        inst_alpha = min(255, int((self.menu_time - 0.5) * 200))
        if inst_alpha > 0:
            inst_text = pygame.font.Font(None, 32).render("Arrow Keys/WASD: Move  |  Space: Jump  |  Shift: Run", True, (*WHITE, inst_alpha))
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, 500))
            self.screen.blit(inst_text, inst_rect)
        
        # Quit button
        quit_hover = 550 < mouse_pos[1] < 600
        quit_bg_color = (255, 100, 100, 100) if quit_hover else (100, 50, 50, 80)
        quit_bg = pygame.Surface((300, 50))
        quit_bg.set_alpha(fade_alpha)
        quit_bg.fill(quit_bg_color[:3])
        self.screen.blit(quit_bg, (SCREEN_WIDTH//2 - 150, 550))
        
        quit_color = WHITE if quit_hover else (200, 200, 200)
        quit_text = button_font.render("QUIT (Escape)", True, (*quit_color, fade_alpha))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH//2, 575))
        self.screen.blit(quit_text, quit_rect)
    
    def draw_playing(self):
        """Draw game during play"""
        # Draw background
        self.level.draw_background(self.screen, self.camera)
        
        # Draw level
        self.level.draw(self.screen, self.camera)
        
        # Draw player
        self.player.draw(self.screen, self.camera)
        
        # Draw particles
        self.particles.draw(self.screen, self.camera)
        
        # Draw HUD
        progress = min(1.0, self.player.x / self.level.goal_x)
        self.hud.draw(self.screen, self.score, self.coins, self.lives, self.level_time, progress)
    
    def draw_paused(self):
        """Draw pause screen"""
        self.draw_playing()
        
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause menu
        font = pygame.font.Font(None, 72)
        pause_text = font.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        button_font = pygame.font.Font(None, 36)
        resume_text = button_font.render("P - Resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        self.screen.blit(resume_text, resume_rect)
        
        menu_text = button_font.render("M - Main Menu", True, WHITE)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        self.screen.blit(menu_text, menu_rect)
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill(BLACK)
        
        font = pygame.font.Font(None, 84)
        game_over_text = font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        self.screen.blit(score_text, score_rect)
        
        button_font = pygame.font.Font(None, 36)
        restart_text = button_font.render("R - Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(restart_text, restart_rect)
        
        menu_text = button_font.render("M - Main Menu", True, WHITE)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        self.screen.blit(menu_text, menu_rect)
    
    def draw_win(self):
        """Draw win screen with celebration"""
        # Animated celebration background
        self.screen.fill((50, 0, 100))
        
        # Fireworks effect
        for _ in range(30):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT//2)
            color = random.choice([GOLD, YELLOW, CYAN, GREEN, RED, PINK])
            size = random.randint(3, 12)
            pygame.draw.circle(self.screen, color, (x, y), size)
            # Sparkle trails
            for trail in range(3):
                trail_x = x + random.randint(-20, 20)
                trail_y = y + random.randint(10, 30)
                pygame.draw.circle(self.screen, color, (trail_x, trail_y), size//3)
        
        # Clear background for text
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 60))
        self.screen.blit(overlay, (0, 0))
        
        # Animated "YOU WON!" text with proper spacing
        bounce = math.sin(time.time() * 3) * 8
        
        # Main title shadow
        font = pygame.font.Font(None, 84)
        shadow_text = font.render("YOU WON!", True, BLACK)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH//2 + 3, SCREEN_HEIGHT//2 - 150 + bounce))
        self.screen.blit(shadow_text, shadow_rect)
        
        # Main title
        win_text = font.render("YOU WON!", True, GOLD)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 150 + bounce))
        self.screen.blit(win_text, win_rect)
        
        # 100% Complete message
        complete_font = pygame.font.Font(None, 42)
        complete_text = complete_font.render("100% COMPLETE!", True, GREEN)
        complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        self.screen.blit(complete_text, complete_rect)
        
        # Game completion message
        game_font = pygame.font.Font(None, 36)
        game_text = game_font.render("Escape Rush Complete!", True, WHITE)
        game_rect = game_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        self.screen.blit(game_text, game_rect)
        
        # Final score
        score_font = pygame.font.Font(None, 40)
        score_text = score_font.render(f"Final Score: {self.score:06d}", True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
        self.screen.blit(score_text, score_rect)
        
        # Coins collected
        coins_text = score_font.render(f"Coins Collected: {self.coins}", True, GOLD)
        coins_rect = coins_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(coins_text, coins_rect)
        
        # Congratulations message
        congrats_font = pygame.font.Font(None, 32)
        congrats_text = congrats_font.render("Congratulations, Champion!", True, CYAN)
        congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 90))
        self.screen.blit(congrats_text, congrats_rect)
        
        # Menu option
        button_font = pygame.font.Font(None, 28)
        menu_text = button_font.render("Press M - Return to Main Menu", True, WHITE)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 140))
        self.screen.blit(menu_text, menu_rect)
        
        # Draw celebration particles
        self.particles.draw(self.screen, self.camera)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            keys = pygame.key.get_pressed()
            self.menu_time += dt
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if self.state == 'menu':
                        if event.key == pygame.K_SPACE:
                            self.start_game()
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    
                    elif self.state == 'playing':
                        if event.key == pygame.K_p:
                            self.state = 'paused'
                    
                    elif self.state == 'paused':
                        if event.key == pygame.K_p:
                            self.state = 'playing'
                        elif event.key == pygame.K_m:
                            self.state = 'menu'
                    
                    elif self.state == 'game_over':
                        if event.key == pygame.K_r:
                            self.start_game()
                        elif event.key == pygame.K_m:
                            self.state = 'menu'
                    
                    elif self.state == 'win':
                        if event.key == pygame.K_m:
                            self.state = 'menu'
            
            # Update game state
            if self.state == 'playing':
                self.update_playing(dt, keys)
            elif self.state == 'menu':
                # Animate menu background
                self.camera.x += 20 * dt
                if self.camera.x > 1000:
                    self.camera.x = 0
            
            # Draw everything
            if self.state == 'menu':
                self.draw_menu()
            elif self.state == 'playing':
                self.draw_playing()
            elif self.state == 'paused':
                self.draw_paused()
            elif self.state == 'game_over':
                self.draw_game_over()
            elif self.state == 'win':
                self.draw_win()
            
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()