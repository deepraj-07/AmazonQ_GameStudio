import pygame
import math
import random
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
DARK_BLUE = (20, 30, 60)
GOLD = (255, 215, 0)

class Particle:
    """Individual particle for visual effects"""
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
        self.life -= dt
        
    def draw(self, screen):
        if self.life > 0:
            alpha = self.life / self.max_life
            size = max(1, int(self.size * alpha))
            color = tuple(int(c * alpha) for c in self.color)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)

class ParticleSystem:
    """Manages all particle effects"""
    def __init__(self):
        self.particles = []
        
    def add_explosion(self, x, y, color=ORANGE, count=15):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, vx, vy, color, 1.0, random.randint(2, 6)))
            
    def add_trail(self, x, y, color=CYAN, count=3):
        for _ in range(count):
            vx = random.uniform(-20, 20)
            vy = random.uniform(20, 60)
            self.particles.append(Particle(x, y, vx, vy, color, 0.5, 2))
            
    def add_pickup(self, x, y):
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 80)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = random.choice([GOLD, YELLOW, WHITE])
            self.particles.append(Particle(x, y, vx, vy, color, 0.8, 3))
            
    def add_muzzle_flash(self, x, y):
        for _ in range(5):
            vx = random.uniform(-30, 30)
            vy = random.uniform(-50, -20)
            color = random.choice([WHITE, YELLOW, ORANGE])
            self.particles.append(Particle(x, y, vx, vy, color, 0.2, random.randint(3, 6)))
            
    def add_hit_blast(self, x, y):
        """Add blast animation when bullet hits target"""
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = random.choice([RED, ORANGE, YELLOW, WHITE])
            self.particles.append(Particle(x, y, vx, vy, color, 0.8, random.randint(4, 8)))
            
    def update(self, dt):
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update(dt)
            
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

class Player:
    """Player spaceship with smooth movement and animations"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width = 30
        self.height = 40
        self.rect = pygame.Rect(x - self.width//2, y - self.height//2, self.width, self.height)
        self.health = 100
        self.max_health = 100
        self.shoot_cooldown = 0
        self.trail_timer = 0
        self.invulnerable = False
        self.invuln_time = 0
        
    def update(self, dt, keys, particles):
        # Ultra-fast robot movement
        accel = 2000
        friction = 0.95
        max_speed = 800
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx -= accel * 2.0 * dt  # Ultra-fast horizontal movement
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx += accel * 2.0 * dt  # Ultra-fast horizontal movement
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy -= accel * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy += accel * dt
            
        # Apply friction and speed limit
        self.vx *= friction
        self.vy *= friction
        self.vx = max(-max_speed, min(max_speed, self.vx))
        self.vy = max(-max_speed, min(max_speed, self.vy))
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Keep on screen
        self.x = max(self.width//2, min(SCREEN_WIDTH - self.width//2, self.x))
        self.y = max(self.height//2, min(SCREEN_HEIGHT - self.height//2, self.y))
        
        # Update rect
        self.rect.center = (self.x, self.y)
        
        # Shooting
        self.shoot_cooldown -= dt
        
        # Trail effect
        self.trail_timer += dt
        if self.trail_timer > 0.05:
            particles.add_trail(self.x, self.y + 15, BLUE, 2)
            self.trail_timer = 0
            
        # Invulnerability
        if self.invulnerable:
            self.invuln_time -= dt
            if self.invuln_time <= 0:
                self.invulnerable = False
                
    def shoot(self, particles):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = 0.1  # Faster shooting
            # Muzzle flash effect
            particles.add_muzzle_flash(self.x, self.y - 20)
            return Bullet(self.x, self.y - 20, 0, -700, CYAN, True)
        return None
        
    def take_damage(self, damage):
        if not self.invulnerable:
            self.health -= damage
            self.invulnerable = True
            self.invuln_time = 1.0
            return True
        return False
        
    def draw(self, screen):
        # Flash when invulnerable
        if self.invulnerable and int(self.invuln_time * 15) % 2:
            return
            
        # Ship body with gradient effect
        points = [
            (self.x, self.y - 20),
            (self.x - 12, self.y + 15),
            (self.x - 6, self.y + 10),
            (self.x + 6, self.y + 10),
            (self.x + 12, self.y + 15)
        ]
        
        # Shadow
        shadow_points = [(p[0] + 2, p[1] + 2) for p in points]
        pygame.draw.polygon(screen, (0, 0, 0, 100), shadow_points)
        
        # Main ship
        pygame.draw.polygon(screen, BLUE, points)
        pygame.draw.polygon(screen, CYAN, points, 2)
        
        # Cockpit
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y - 5)), 4)
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y - 5)), 4, 2)

class Enemy:
    """Enemy with AI behavior"""
    def __init__(self, x, y, enemy_type="basic"):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.width = 25
        self.height = 25
        self.rect = pygame.Rect(x - self.width//2, y - self.height//2, self.width, self.height)
        self.health = 1  # One bullet kill for all enemies
        self.speed = 150 if enemy_type == "basic" else 100
        self.shoot_cooldown = 0
        self.angle = 0
        self.alive = True
        
    def update(self, dt, player, bullets, particles):
        if not self.alive:
            return
            
        # AI behavior
        if self.type == "basic":
            self.y += self.speed * dt
        else:  # "advanced"
            # Move toward player
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                self.x += (dx / dist) * self.speed * dt
                self.y += (dy / dist) * self.speed * dt
                
        self.angle += dt * 2
        self.rect.center = (self.x, self.y)
        
        # Shooting
        self.shoot_cooldown -= dt
        if self.shoot_cooldown <= 0 and self.y > 0:
            self.shoot_cooldown = random.uniform(1.0, 2.5)
            if self.type == "basic":
                bullets.append(Bullet(self.x, self.y + 15, 0, 200, RED, False))
            else:
                # Shoot toward player
                dx = player.x - self.x
                dy = player.y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    speed = 250
                    vx = (dx / dist) * speed
                    vy = (dy / dist) * speed
                    bullets.append(Bullet(self.x, self.y, vx, vy, ORANGE, False))
                    
        # Remove if off screen
        if self.y > SCREEN_HEIGHT + 50:
            self.alive = False
            
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return True
        return False
        
    def draw(self, screen):
        if not self.alive:
            return
            
        # Shadow
        pygame.draw.circle(screen, (0, 0, 0, 80), (int(self.x + 2), int(self.y + 2)), self.width//2)
        
        if self.type == "basic":
            # Basic enemy - red triangle
            points = [
                (self.x, self.y + 12),
                (self.x - 10, self.y - 12),
                (self.x + 10, self.y - 12)
            ]
            pygame.draw.polygon(screen, RED, points)
            pygame.draw.polygon(screen, ORANGE, points, 2)
        else:
            # Advanced enemy - rotating diamond
            size = 12
            cos_a = math.cos(self.angle)
            sin_a = math.sin(self.angle)
            points = [
                (self.x + cos_a * size, self.y + sin_a * size),
                (self.x - sin_a * size, self.y + cos_a * size),
                (self.x - cos_a * size, self.y - sin_a * size),
                (self.x + sin_a * size, self.y - cos_a * size)
            ]
            pygame.draw.polygon(screen, PURPLE, points)
            pygame.draw.polygon(screen, WHITE, points, 2)

class Bullet:
    """Bullet projectile"""
    def __init__(self, x, y, vx, vy, color, friendly):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.friendly = friendly
        self.width = 4
        self.height = 8
        self.rect = pygame.Rect(x - 2, y - 4, self.width, self.height)
        self.alive = True
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.center = (self.x, self.y)
        
        # Remove if off screen
        if (self.x < -10 or self.x > SCREEN_WIDTH + 10 or 
            self.y < -10 or self.y > SCREEN_HEIGHT + 10):
            self.alive = False
            
    def draw(self, screen):
        if self.alive:
            # Fire bullet appearance
            flame_time = time.time() * 30
            
            if self.friendly:
                # Player fire bullet - blue flame
                # Outer flame
                flame_size = 10 + math.sin(flame_time) * 3
                pygame.draw.circle(screen, (0, 100, 255), (int(self.x), int(self.y)), int(flame_size))
                # Middle flame
                pygame.draw.circle(screen, (100, 200, 255), (int(self.x), int(self.y)), 6)
                # Inner flame
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 3)
                # Fire trail
                for i in range(3):
                    trail_y = self.y + (i + 1) * 8
                    trail_size = 4 - i
                    pygame.draw.circle(screen, (0, 50 + i * 50, 255), (int(self.x), int(trail_y)), trail_size)
            else:
                # Enemy fire bullet - red flame
                flame_size = 8 + math.sin(flame_time) * 2
                pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), int(flame_size))
                pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), 5)
                pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 2)

class PowerUp:
    """Collectible power-up"""
    def __init__(self, x, y, power_type="health"):
        self.x = x
        self.y = y
        self.type = power_type
        self.width = 20
        self.height = 20
        self.rect = pygame.Rect(x - 10, y - 10, self.width, self.height)
        self.alive = True
        self.bob_time = 0
        self.glow_time = 0
        # Health boost amount (25-30%)
        self.health_boost = random.randint(25, 30) if power_type == "health" else 0
        
    def update(self, dt):
        self.y += 100 * dt  # Slow fall
        self.bob_time += dt * 4
        self.glow_time += dt * 6
        self.rect.center = (self.x, self.y + math.sin(self.bob_time) * 3)
        
        if self.y > SCREEN_HEIGHT + 50:
            self.alive = False
            
    def draw(self, screen):
        if not self.alive:
            return
            
        y_offset = math.sin(self.bob_time) * 3
        glow_size = 15 + math.sin(self.glow_time) * 5
        
        # Glow effect
        color = GREEN if self.type == "health" else GOLD
        pygame.draw.circle(screen, (*color, 100), (int(self.x), int(self.y + y_offset)), int(glow_size))
        
        # Main item
        if self.type == "health":
            # Big health cross with pulsing effect
            pulse = 1.0 + math.sin(self.glow_time * 2) * 0.2
            size = int(8 * pulse)
            pygame.draw.rect(screen, GREEN, (self.x - size, self.y + y_offset - 2, size * 2, 4))
            pygame.draw.rect(screen, GREEN, (self.x - 2, self.y + y_offset - size, 4, size * 2))
            pygame.draw.rect(screen, WHITE, (self.x - size, self.y + y_offset - 2, size * 2, 4), 1)
            pygame.draw.rect(screen, WHITE, (self.x - 2, self.y + y_offset - size, 4, size * 2), 1)
        else:
            # Score gem
            points = [
                (self.x, self.y + y_offset - 8),
                (self.x + 6, self.y + y_offset - 2),
                (self.x, self.y + y_offset + 8),
                (self.x - 6, self.y + y_offset - 2)
            ]
            pygame.draw.polygon(screen, GOLD, points)
            pygame.draw.polygon(screen, WHITE, points, 2)

class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Stellar Defender - Space Shooter")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = "menu"  # menu, playing, game_over, victory
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.difficulty = 1.0
        self.victory_level = 4  # Win at level 4
        
        # Game objects
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.enemies = []
        self.bullets = []
        self.powerups = []
        self.particles = ParticleSystem()
        
        # Timers
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.background_stars = self._generate_stars()
        
        # UI
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        # Menu animation
        self.menu_time = 0
        self.title_glow = 0
        
    def _generate_stars(self):
        """Generate shiny background stars"""
        stars = []
        for _ in range(150):  # More stars
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(1, 4)
            speed = random.uniform(20, 120)
            brightness = random.uniform(0.3, 1.0)
            twinkle_speed = random.uniform(2, 8)
            stars.append([x, y, size, speed, brightness, twinkle_speed, 0])
        return stars
        
    def _update_stars(self, dt):
        """Update scrolling shiny star field"""
        for star in self.background_stars:
            star[1] += star[3] * dt  # Move down
            star[6] += star[5] * dt  # Update twinkle timer
            if star[1] > SCREEN_HEIGHT:
                star[1] = -5
                star[0] = random.randint(0, SCREEN_WIDTH)
                
    def _draw_stars(self):
        """Draw shiny background stars"""
        for star in self.background_stars:
            # Twinkling effect
            twinkle = math.sin(star[6]) * 0.3 + 0.7
            brightness = int(255 * star[4] * twinkle)
            
            # Star colors - some are white, some are colored
            if star[2] >= 3:  # Larger stars get colors
                colors = [(brightness, brightness, 255), (255, brightness, brightness), 
                         (brightness, 255, brightness), (255, 255, brightness)]
                color = random.choice(colors)
            else:
                color = (brightness, brightness, brightness)
            
            # Draw star with glow
            if star[2] >= 2:
                # Glow effect for bigger stars
                glow_size = star[2] + 2
                glow_color = tuple(int(c * 0.3) for c in color)
                pygame.draw.circle(self.screen, glow_color, (int(star[0]), int(star[1])), glow_size)
            
            pygame.draw.circle(self.screen, color, (int(star[0]), int(star[1])), star[2])
            
    def _draw_gradient_bg(self):
        """Draw gradient background"""
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(10 * (1 - ratio) + 5 * ratio)
            g = int(15 * (1 - ratio) + 10 * ratio)
            b = int(40 * (1 - ratio) + 60 * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
    def _spawn_enemy(self):
        """Spawn new enemy"""
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = -30
        enemy_type = "advanced" if random.random() < 0.3 * self.difficulty else "basic"
        self.enemies.append(Enemy(x, y, enemy_type))
        
    def _spawn_powerup(self):
        """Spawn power-up"""
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = -30
        power_type = "health" if random.random() < 0.7 else "score"
        self.powerups.append(PowerUp(x, y, power_type))
        
    def _update_difficulty(self):
        """Increase difficulty based on score"""
        self.level = (self.score // 1000) + 1
        self.difficulty = 1.0 + (self.level - 1) * 0.3
        
    def _check_collisions(self):
        """Handle all collision detection"""
        # Player bullets vs enemy bullets
        for player_bullet in self.bullets[:]:
            if not player_bullet.friendly or not player_bullet.alive:
                continue
            for enemy_bullet in self.bullets[:]:
                if enemy_bullet.friendly or not enemy_bullet.alive:
                    continue
                if player_bullet.rect.colliderect(enemy_bullet.rect):
                    player_bullet.alive = False
                    enemy_bullet.alive = False
                    # Bullet collision explosion
                    self.particles.add_hit_blast((player_bullet.x + enemy_bullet.x) / 2, 
                                                (player_bullet.y + enemy_bullet.y) / 2)
                    self.score += 25  # Bonus for bullet deflection
                    break
        
        # Player bullets vs enemies
        for bullet in self.bullets[:]:
            if not bullet.friendly or not bullet.alive:
                continue
            for enemy in self.enemies[:]:
                if enemy.alive and bullet.rect.colliderect(enemy.rect):
                    bullet.alive = False
                    # Add hit blast animation
                    self.particles.add_hit_blast(enemy.x, enemy.y)
                    if enemy.take_damage(1):  # One bullet kill
                        self.particles.add_explosion(enemy.x, enemy.y, RED)
                        self.score += 100 if enemy.type == "basic" else 250
                        
        # Enemy bullets vs player
        for bullet in self.bullets[:]:
            if bullet.friendly or not bullet.alive:
                continue
            if bullet.rect.colliderect(self.player.rect):
                bullet.alive = False
                # Add hit blast animation
                self.particles.add_hit_blast(self.player.x, self.player.y)
                if self.player.take_damage(20):
                    self.particles.add_explosion(self.player.x, self.player.y, ORANGE)
                    
        # Player vs enemies
        for enemy in self.enemies[:]:
            if enemy.alive and enemy.rect.colliderect(self.player.rect):
                if self.player.take_damage(30):
                    self.particles.add_explosion(self.player.x, self.player.y, RED)
                enemy.take_damage(50)
                
        # Player vs power-ups
        for powerup in self.powerups[:]:
            if powerup.alive and powerup.rect.colliderect(self.player.rect):
                powerup.alive = False
                self.particles.add_pickup(powerup.x, powerup.y)
                if powerup.type == "health":
                    # Big health boost (25-30% of max health)
                    health_restore = powerup.health_boost
                    self.player.health = min(self.player.max_health, self.player.health + health_restore)
                else:
                    self.score += 500
                    
    def _draw_hud(self):
        """Draw heads-up display"""
        # Semi-transparent HUD background
        hud_surface = pygame.Surface((SCREEN_WIDTH, 80))
        hud_surface.set_alpha(150)
        hud_surface.fill(DARK_BLUE)
        self.screen.blit(hud_surface, (0, 0))
        
        # Score
        score_text = self.font_medium.render(f"Score: {self.score:06d}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        # Level
        level_text = self.font_small.render(f"Level: {self.level}", True, CYAN)
        self.screen.blit(level_text, (20, 50))
        
        # Health bar
        bar_width = 200
        bar_height = 20
        bar_x = SCREEN_WIDTH - bar_width - 20
        bar_y = 20
        
        # Health bar background
        pygame.draw.rect(self.screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Health bar fill
        health_ratio = self.player.health / self.player.max_health
        fill_width = int(bar_width * health_ratio)
        color = GREEN if health_ratio > 0.6 else ORANGE if health_ratio > 0.3 else RED
        pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_width, bar_height))
        
        # Health bar border
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Health text
        health_text = self.font_small.render("Health", True, WHITE)
        self.screen.blit(health_text, (bar_x, bar_y - 25))
        
    def _draw_menu(self):
        """Draw main menu"""
        self.menu_time += 1/60
        self.title_glow += 0.1
        
        # Animated title
        glow_size = 5 + math.sin(self.title_glow) * 3
        title_y = 150 + math.sin(self.menu_time) * 10
        
        # Title glow
        for i in range(int(glow_size)):
            alpha = 50 - i * 8
            glow_font = pygame.font.Font(None, 84 + i * 2)
            glow_text = glow_font.render("STELLAR DEFENDER", True, (*CYAN, alpha))
            glow_rect = glow_text.get_rect(center=(SCREEN_WIDTH//2, title_y))
            self.screen.blit(glow_text, glow_rect)
            
        # Main title
        title_text = self.font_large.render("STELLAR DEFENDER", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, title_y))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font_small.render("Space Shooter Adventure", True, CYAN)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, title_y + 60))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Menu buttons
        mouse_pos = pygame.mouse.get_pos()
        
        buttons = [
            ("PLAY", 350),
            ("INSTRUCTIONS", 420),
            ("QUIT", 490)
        ]
        
        for text, y in buttons:
            # Button background
            button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, y - 20, 200, 50)
            hover = button_rect.collidepoint(mouse_pos)
            
            color = (100, 150, 255) if hover else (50, 50, 100)
            pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2, border_radius=10)
            
            # Button text
            text_color = YELLOW if hover else WHITE
            button_text = self.font_medium.render(text, True, text_color)
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)
            
        # High score
        if self.high_score > 0:
            high_score_text = self.font_small.render(f"High Score: {self.high_score:06d}", True, GOLD)
            high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH//2, 580))
            self.screen.blit(high_score_text, high_score_rect)
            
    def _draw_instructions(self):
        """Draw instructions overlay"""
        # Semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Instructions panel
        panel_rect = pygame.Rect(150, 100, SCREEN_WIDTH - 300, SCREEN_HEIGHT - 200)
        pygame.draw.rect(self.screen, DARK_BLUE, panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 3, border_radius=20)
        
        # Title
        title_text = self.font_large.render("HOW TO PLAY", True, CYAN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        instructions = [
            "WASD or Arrow Keys - Move your ship",
            "SPACE - Shoot lasers",
            "Avoid enemy ships and projectiles",
            "Collect green crosses to restore health",
            "Collect gold gems for bonus points",
            "Survive as long as possible!",
            "",
            "Press ESC or ENTER to return to menu"
        ]
        
        y_start = 220
        for i, instruction in enumerate(instructions):
            color = WHITE if instruction else CYAN
            text = self.font_small.render(instruction, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_start + i * 35))
            self.screen.blit(text, text_rect)
            
    def _draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over panel
        panel_rect = pygame.Rect(200, 150, SCREEN_WIDTH - 400, SCREEN_HEIGHT - 300)
        pygame.draw.rect(self.screen, DARK_BLUE, panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, RED, panel_rect, 3, border_radius=20)
        
        # Game over text
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, 220))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        score_text = self.font_medium.render(f"Final Score: {self.score:06d}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 300))
        self.screen.blit(score_text, score_rect)
        
        # Level reached
        level_text = self.font_small.render(f"Level Reached: {self.level}", True, CYAN)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, 340))
        self.screen.blit(level_text, level_rect)
        
        # New high score
        if self.score > self.high_score:
            new_high_text = self.font_medium.render("NEW HIGH SCORE!", True, GOLD)
            new_high_rect = new_high_text.get_rect(center=(SCREEN_WIDTH//2, 380))
            self.screen.blit(new_high_text, new_high_rect)
            
        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        
        buttons = [
            ("PLAY AGAIN", 450),
            ("MAIN MENU", 500)
        ]
        
        for text, y in buttons:
            button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, y - 20, 200, 40)
            hover = button_rect.collidepoint(mouse_pos)
            
            color = (100, 150, 255) if hover else (50, 50, 100)
            pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2, border_radius=10)
            
            text_color = YELLOW if hover else WHITE
            button_text = self.font_small.render(text, True, text_color)
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)
            
    def _reset_game(self):
        """Reset game state for new game"""
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.enemies = []
        self.bullets = []
        self.powerups = []
        self.particles = ParticleSystem()
        self.score = 0
        self.level = 1
        self.difficulty = 1.0
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
        
    def handle_events(self, event):
        """Handle pygame events"""
        if event.type == pygame.QUIT:
            return False
            
        elif event.type == pygame.KEYDOWN:
            if self.state == "menu":
                if event.key == pygame.K_RETURN:
                    self.state = "playing"
                    self._reset_game()
                elif event.key == pygame.K_i:
                    self.state = "instructions"
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return False
                    
            elif self.state == "instructions":
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    self.state = "menu"
                    
            elif self.state == "playing":
                if event.key == pygame.K_SPACE:
                    bullet = self.player.shoot(self.particles)
                    if bullet:
                        self.bullets.append(bullet)
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                    
            elif self.state == "victory":
                if event.key == pygame.K_r:
                    self.state = "playing"
                    self._reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                    
            elif self.state == "game_over":
                if event.key == pygame.K_r:
                    self.state = "playing"
                    self._reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                    
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.state == "menu":
                # Check button clicks
                if 330 <= mouse_pos[1] <= 370:  # Play
                    self.state = "playing"
                    self._reset_game()
                elif 400 <= mouse_pos[1] <= 440:  # Instructions
                    self.state = "instructions"
                elif 470 <= mouse_pos[1] <= 510:  # Quit
                    return False
                    
            elif self.state == "game_over":
                if 430 <= mouse_pos[1] <= 470:  # Play Again
                    self.state = "playing"
                    self._reset_game()
                elif 480 <= mouse_pos[1] <= 520:  # Main Menu
                    self.state = "menu"
                    
        return True
        
    def update(self, dt):
        """Update game logic"""
        if self.state == "playing":
            keys = pygame.key.get_pressed()
            
            # Update player
            self.player.update(dt, keys, self.particles)
            
            # Update enemies
            for enemy in self.enemies[:]:
                enemy.update(dt, self.player, self.bullets, self.particles)
                if not enemy.alive:
                    self.enemies.remove(enemy)
                    
            # Update bullets
            for bullet in self.bullets[:]:
                bullet.update(dt)
                if not bullet.alive:
                    self.bullets.remove(bullet)
                    
            # Update power-ups
            for powerup in self.powerups[:]:
                powerup.update(dt)
                if not powerup.alive:
                    self.powerups.remove(powerup)
                    
            # Update particles
            self.particles.update(dt)
            
            # Spawn enemies
            self.enemy_spawn_timer += dt
            spawn_rate = max(0.5, 2.0 - self.difficulty * 0.3)
            if self.enemy_spawn_timer > spawn_rate:
                self.enemy_spawn_timer = 0
                self._spawn_enemy()
                
            # Spawn power-ups more frequently
            self.powerup_spawn_timer += dt
            if self.powerup_spawn_timer > random.uniform(3, 6):  # Much more frequent
                self.powerup_spawn_timer = 0
                self._spawn_powerup()
                
            # Update difficulty
            self._update_difficulty()
            
            # Check collisions
            self._check_collisions()
            
            # Check game over
            if self.player.health <= 0:
                self.state = "game_over"
                if self.score > self.high_score:
                    self.high_score = self.score
                    
            # Check victory condition - win at level 4
            if self.level >= self.victory_level:
                self.state = "victory"
                if self.score > self.high_score:
                    self.high_score = self.score
                    
        # Update background
        self._update_stars(dt)
        
    def draw(self):
        """Draw everything"""
        # Background
        self._draw_gradient_bg()
        self._draw_stars()
        
        if self.state == "menu":
            self._draw_menu()
        elif self.state == "instructions":
            self._draw_instructions()
        elif self.state == "playing":
            # Game objects
            self.player.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
                
            for bullet in self.bullets:
                bullet.draw(self.screen)
                
            for powerup in self.powerups:
                powerup.draw(self.screen)
                
            # Effects
            self.particles.draw(self.screen)
            
            # UI
            self._draw_hud()
            
        elif self.state == "game_over":
            # Still draw game objects faded
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for bullet in self.bullets:
                bullet.draw(self.screen)
            self.particles.draw(self.screen)
            
            self._draw_game_over()
            
        elif self.state == "victory":
            # Draw victory screen
            self._draw_victory()
            
    def _draw_victory(self):
        """Draw victory screen"""
        # Celebration background with particles
        for _ in range(20):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            color = random.choice([GOLD, YELLOW, CYAN, GREEN])
            size = random.randint(2, 8)
            pygame.draw.circle(self.screen, color, (x, y), size)
            
        # Victory panel
        panel_rect = pygame.Rect(150, 100, SCREEN_WIDTH - 300, SCREEN_HEIGHT - 200)
        pygame.draw.rect(self.screen, DARK_BLUE, panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 3, border_radius=20)
        
        # Main victory text
        victory_text = self.font_large.render("VICTORY!", True, YELLOW)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, 180))
        self.screen.blit(victory_text, victory_rect)
        
        # Mission accomplished
        mission_text = self.font_medium.render("Mission Accomplished!", True, WHITE)
        mission_rect = mission_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(mission_text, mission_rect)
        
        # Final score
        score_text = self.font_medium.render(f"Final Score: {self.score:06d}", True, CYAN)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 320))
        self.screen.blit(score_text, score_rect)
        
        # Congratulations
        congrats_text = self.font_small.render("You are the ultimate space defender!", True, GREEN)
        congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH//2, 380))
        self.screen.blit(congrats_text, congrats_rect)
        
        # Instructions
        restart_text = self.font_small.render("Press R to Play Again or ESC for Menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, 450))
        self.screen.blit(restart_text, restart_rect)
    
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