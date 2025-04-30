import pygame
import math
import random

# ------------------------
# SpaceObject Class (Physics)
# ------------------------

# This class represents the ships and their physics in the game.
# It handles the position, velocity, rotation, and collision with walls.
# The ships can move, rotate, and apply thrust. The class also manages the health points (HP) of the ships.
class SpaceObject:
    
    def __init__(self, x, y, angle=0, velocity_x=0, velocity_y=0, hp=100, WORLD_WIDTH=2000, WORLD_HEIGHT=2000):
        self.WORLD_WIDTH = WORLD_WIDTH
        self.WORLD_HEIGHT = WORLD_HEIGHT
        self.x = x
        self.y = y
        self.angle = angle
        self.vx = velocity_x  # Initial velocity
        self.vy = velocity_y
        self.hp = hp  # Health points
    
    # Update the position of the ship based on its velocity and angle.
    # The ship's velocity is affected by friction, and it is clamped to a maximum speed.    
    def update_position(self, is_enemy=False):
        max_speed = 10 if not is_enemy else 5  # Player: 10, Enemy: 5
        friction = 0.98  # Friction effect
        self.vx *= friction
        self.vy *= friction
        self.vx = max(-max_speed, min(self.vx, max_speed))
        self.vy = max(-max_speed, min(self.vy, max_speed))
        self.x += self.vx
        self.y += self.vy
        self.x = max(0, min(self.x, self.WORLD_WIDTH))
        self.y = max(0, min(self.y, self.WORLD_HEIGHT))

    # Apply thrust in the direction of the ship's angle.
    # The thrust amount is added to the ship's velocity in the x and y directions.
    def thrust(self, amount):
        rad = math.radians(self.angle)
        self.vx += math.cos(rad) * amount
        self.vy += math.sin(rad) * amount

    ## Rotate the ship by a specified number of degrees.
    # The angle is clamped to the range [0, 360) degrees.
    def rotate(self, degrees):
        self.angle = (self.angle + degrees) % 360

    # Get the current state of the ship, including position, velocity, and angle.
    # This is useful for saving or sending the state of the ship.
    # The state is returned as a dictionary.
    def get_state(self):
        return {
            "x": self.x,
            "y": self.y,
            "vx": self.vx,
            "vy": self.vy,
            "angle": self.angle,
        }
        
    # Check for collision with walls.
    # If a collision is detected, the ship's position and velocity are adjusted accordingly.
    # The ship is moved back to the edge of the wall, and its velocity is set to zero.

    def check_wall_collision(self, walls):
        ship_rect = pygame.Rect(self.x - 10, self.y - 10, 20, 20)  # Size of the ship
        for wall in walls:
            if ship_rect.colliderect(wall):
                # Bounce back based on direction
                if self.x < wall.x:  # Left of the wall
                    self.x = wall.x - 10
                    self.vx = 0
                elif self.x > wall.x + wall.width:  # Right of the wall
                    self.x = wall.x + wall.width + 10
                    self.vx = 0
                if self.y < wall.y:  # Above the wall
                    self.y = wall.y - 10
                    self.vy = 0
                elif self.y > wall.y + wall.height:  # Below the wall
                    self.y = wall.y + wall.height + 10
                    self.vy = 0


# ------------------------
# Bullet Class
# ------------------------   

# This class represents the bullets fired by the ships.
# Each bullet has a position, angle, owner (ship index), and speed.     
class Bullet:
    def __init__(self, x, y, angle, owner, speed=15):  # Bullets are faster
        self.x = x
        self.y = y
        self.angle = angle
        self.owner = owner
        rad = math.radians(angle)
        self.vx = math.cos(rad) * speed
        self.vy = math.sin(rad) * speed
        
    # Update the position of the bullet based on its velocity.
    # The bullet moves in the direction of its angle.
    # The position is updated by adding the velocity to the current position.
    def update(self):
        self.x += self.vx
        self.y += self.vy

    # Check if the bullet is offscreen.
    # The bullet is considered offscreen if it is outside the world boundaries.
    def is_offscreen(self, world_width, world_height):
        return not (0 <= self.x <= world_width and 0 <= self.y <= world_height)


# ------------------------
# GameEngine Class
# ------------------------

# This class manages the game state, including the ships, bullets, score, and time.
# It handles the game logic, including updating the positions of the ships and bullets,
class GameEngine:
    def __init__(self, walls):
        self.ships = [
            SpaceObject(*generate_valid_position(walls, WORLD_WIDTH, WORLD_HEIGHT)),
            SpaceObject(*generate_valid_position(walls, WORLD_WIDTH, WORLD_HEIGHT))
        ]
        self.bullets = [] 
        self.score = [0, 0]
        self.time = 0

    # Update the game state.
    # This includes updating the positions of the ships and bullets, checking for collisions,
    def update(self, walls):
        new_ships = []
        for i, ship in enumerate(self.ships[:]):
            is_enemy = (i == 1)  # The enemy is the second ship
            ship.update_position(is_enemy=is_enemy)
            ship.check_wall_collision(walls)  # Wall collision check
            if ship.hp <= 0:  # Remove the ship if HP is 0
                self.ships.remove(ship)
                if is_enemy:  # If an enemy dies, double the number of enemies
                    for _ in range(2):  # Add two new enemies
                        x, y = generate_valid_position(walls, WORLD_WIDTH, WORLD_HEIGHT)
                        new_ships.append(SpaceObject(x, y, angle=random.randint(0, 360), hp=100))
        self.ships.extend(new_ships)

        
        for bullet in self.bullets:
            bullet.update()
        new_bullets = []
        for bullet in self.bullets:
            hit = False
            for i, ship in enumerate(self.ships):
                if i != bullet.owner and self._collides(bullet, ship):  # Avoid friendly fire
                    ship.hp -= 10  # Damage dealt
                    hit = True
                    if ship.hp <= 0 and i == 1:  # Points for killing an enemy
                        self.score[0] += 10  # Player earns 10 points
                    print(f"Ship {i} hit! HP: {ship.hp}")
            if not hit:
                new_bullets.append(bullet)

        self.bullets = [b for b in new_bullets if not b.is_offscreen(self.ships[0].WORLD_WIDTH, self.ships[0].WORLD_HEIGHT)]
    
    # Shoot a bullet from the specified ship.
    # The bullet is spawned slightly in front of the ship, and its speed is set.
    # The bullet is added to the list of bullets in the game.       
    def shoot(self, ship_index):
        ship = self.ships[ship_index]
        # Spawn bullet slightly in front of the ship
        rad = math.radians(ship.angle)
        bullet_x = ship.x + math.cos(rad) * 15  # Offset by 15 units in the direction of the ship
        bullet_y = ship.y + math.sin(rad) * 15
        bullet = Bullet(bullet_x, bullet_y, ship.angle, owner=ship_index, speed=15)  # Fast bullets
        self.bullets.append(bullet)

    # Draw the bullets on the screen.
    def draw_bullets(self, screen, camera_x, camera_y):
        for bullet in self.bullets:
            screen_x, screen_y = world_to_screen(bullet.x, bullet.y, camera_x, camera_y)
            pygame.draw.circle(screen, (0, 0, 0), (screen_x, screen_y), 3)

    # Rotate the ship by a specified number of degrees.
    def rotate_ship(self, index, degrees):
        self.ships[index].rotate(degrees)
    
    # Apply thrust to the ship in the direction of its angle.
    def thrust_ship(self, index, amount):
        self.ships[index].thrust(amount)

    # Get the current state of the game.
    # This includes the state of the ships, score, and time.
    # The state is returned as a dictionary. (This is useful for saving or sending the state of the game)

    def get_game_state(self):
        return {
            "ships": [ship.get_state() for ship in self.ships],
            "score": self.score,
            "time": self.time
        }
    def _collides(self, bullet, ship):
        dist = math.hypot(bullet.x - ship.x, bullet.y - ship.y)
        return dist < 15  # Simple collision radius


# ------------------------
# Main Game Loop with Pygame
# ------------------------

# Set world size larger than screen
WORLD_WIDTH, WORLD_HEIGHT = 2000, 2000
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
RED = (255, 50, 50)

background_image = pygame.image.load("galaxie.jpg")  # Load background image
background_image = pygame.transform.scale(background_image, (WORLD_WIDTH, WORLD_HEIGHT))

# Create a semi-transparent surface
transparent_surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT), pygame.SRCALPHA)
transparent_surface.blit(background_image, (0, 0))  # Draw the background onto the surface
transparent_surface.set_alpha(128)  # Set transparency to 50% (128 out of 255)

def world_to_screen(x, y, camera_x, camera_y):
    return int(x - camera_x + SCREEN_WIDTH // 2), int(y - camera_y + SCREEN_HEIGHT // 2)


def draw_ship(screen, ship, color, camera_x, camera_y):
    screen_x, screen_y = world_to_screen(ship.x, ship.y, camera_x, camera_y)
    angle = ship.angle
    length = 20
    rad = math.radians(angle)
    end_x = screen_x + math.cos(rad) * length
    end_y = screen_y + math.sin(rad) * length
    pygame.draw.circle(screen, color, (screen_x, screen_y), 10)
    pygame.draw.line(screen, color, (screen_x, screen_y), (int(end_x), int(end_y)), 2)


def create_labyrinth():
    # A larger labyrinth with multiple paths and dead ends
    walls = [
        # Outer walls
        pygame.Rect(50, 50, 1900, 20),  # Top wall
        pygame.Rect(50, 50, 20, 1900),  # Left wall
        pygame.Rect(50, 1930, 1900, 20),  # Bottom wall
        pygame.Rect(1930, 50, 20, 1900),  # Right wall

        # Inner structures
        pygame.Rect(200, 200, 20, 400),  # Vertical wall top left
        pygame.Rect(200, 600, 400, 20),  # Horizontal wall top left
        pygame.Rect(600, 200, 20, 400),  # Vertical wall top center
        pygame.Rect(600, 600, 400, 20),  # Horizontal wall top center
        pygame.Rect(1000, 200, 20, 800),  # Vertical wall top right
        pygame.Rect(200, 1000, 800, 20),  # Horizontal wall center
        pygame.Rect(1200, 200, 20, 800),  # Vertical wall center right
        pygame.Rect(1200, 1000, 400, 20),  # Horizontal wall center right
        pygame.Rect(1600, 200, 20, 800),  # Vertical wall top far right
        pygame.Rect(200, 1400, 400, 20),  # Horizontal wall bottom left
        pygame.Rect(600, 1400, 20, 400),  # Vertical wall bottom center
        pygame.Rect(600, 1800, 400, 20),  # Horizontal wall bottom center
        pygame.Rect(1000, 1400, 20, 400),  # Vertical wall bottom right
        pygame.Rect(1200, 1400, 400, 20),  # Horizontal wall bottom right
        pygame.Rect(1600, 1400, 20, 400),  # Vertical wall bottom far right

        # Dead ends
        pygame.Rect(300, 300, 100, 20),  # Horizontal dead end top left
        pygame.Rect(1500, 1500, 100, 20),  # Horizontal dead end bottom right
        pygame.Rect(800, 800, 20, 100),  # Vertical dead end center
    ]
    return walls

# Generate a random position for the ship within the labyrinth
# The position is generated by checking if it is valid (not colliding with walls).
# The function returns the x and y coordinates of the valid position.

def is_position_valid(x, y, walls):
    ship_rect = pygame.Rect(x - 10, y - 10, 20, 20)  # Size of the ship
    for wall in walls:
        if ship_rect.colliderect(wall):
            return False
    return True


# Generate a random position for the ship within the labyrinth
# The position is generated by checking if it is valid (not colliding with walls).
def generate_valid_position(walls, world_width, world_height):
    while True:
        x = random.randint(100, world_width - 100)  # Avoid outer walls
        y = random.randint(100, world_height - 100)
        if is_position_valid(x, y, walls):
            return x, y

# Generate coins in random positions within the labyrinth
# The coins are represented as small rectangles.
def generate_coins(num_coins, walls):
    coins = []
    for _ in range(num_coins):
        x, y = generate_valid_position(walls, WORLD_WIDTH, WORLD_HEIGHT)
        coins.append(pygame.Rect(x - 5, y - 5, 10, 10))  # Coin as a small rectangle
    return coins

# Move the enemy randomly with a chance to rotate or thrust
# The enemy will rotate left or right randomly and apply light thrust.
def move_enemy_randomly(enemy):
    # Random rotation
    if random.random() < 0.1:  # 10% chance per frame
        enemy.rotate(random.choice([-5, 5]))  # Rotate left or right

    # Random thrust
    if random.random() < 0.2:  # 20% chance per frame
        enemy.thrust(0.5)  # Light thrust

# Avoid walls
# The enemy will check for collisions with walls and rotate away from them.
def avoid_walls(enemy, walls):
    ship_rect = pygame.Rect(enemy.x - 10, enemy.y - 10, 20, 20)
    for wall in walls:
        if ship_rect.colliderect(wall):
            # Rotate the enemy if it hits a wall
            enemy.rotate(180)  # Rotate 180 degrees
            enemy.thrust(-1)  # Reverse movement


# Chase the player
# The enemy will chase the player by calculating the angle to the player and rotating towards them.
def chase_player(enemy, player):
    # Calculate the angle to the player
    dx = player.x - enemy.x
    dy = player.y - enemy.y
    angle_to_player = math.degrees(math.atan2(dy, dx))

    # Rotate the enemy towards the player
    if abs(angle_to_player - enemy.angle) > 5:  # Only rotate if the angle is significant
        if (angle_to_player - enemy.angle) % 360 < 180:
            enemy.rotate(3)  # Rotate right
        else:
            enemy.rotate(-3)  # Rotate left

    # Thrust towards the player
    enemy.thrust(0.4)  # Thrust towards the player


def can_see_player(enemy, player, walls):
    # Calculate the line between the enemy and the player
    dx = player.x - enemy.x
    dy = player.y - enemy.y
    distance = math.hypot(dx, dy)
    steps = int(distance / 10)  # Divide the line into steps

    for step in range(steps):
        check_x = enemy.x + dx * (step / steps)
        check_y = enemy.y + dy * (step / steps)
        check_rect = pygame.Rect(check_x - 5, check_y - 5, 10, 10)  # Small area to check
        for wall in walls:
            if check_rect.colliderect(wall):
                return False  # Wall blocks the view
    return True


def chase_and_shoot(enemy, player, walls, engine):
    if can_see_player(enemy, player, walls):
        # Chase the player
        chase_player(enemy, player)

        # Shoot at the player
        if random.random() < 0.02:  # 5% chance per frame
            engine.shoot(1)  # Enemy shoots (Index 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("BotFighters Arena")

    walls = create_labyrinth()
    coins = generate_coins(20, walls)  # 20 coins on the field

    clock = pygame.time.Clock()
    engine = GameEngine(walls)  # Pass walls to the GameEngine

    running = True
    while running:
        screen.fill(WHITE)
        player = engine.ships[0]
        enemy = engine.ships[1] if len(engine.ships) > 1 else None  # Check if the enemy exists
        
        camera_x = player.x
        camera_y = player.y

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw the semi-transparent background relative to the camera
        screen.blit(transparent_surface, (-camera_x + SCREEN_WIDTH // 2, -camera_y + SCREEN_HEIGHT // 2))

        # Draw walls (relative to camera)
        for wall in walls:
            wall_screen = pygame.Rect(
                wall.x - camera_x + SCREEN_WIDTH // 2,
                wall.y - camera_y + SCREEN_HEIGHT // 2,
                wall.width,
                wall.height
            )
            pygame.draw.rect(screen, (80, 80, 80), wall_screen)
        
        # Draw coins
        for coin in coins[:]:
            coin_screen = pygame.Rect(
                coin.x - camera_x + SCREEN_WIDTH // 2,
                coin.y - camera_y + SCREEN_HEIGHT // 2,
                coin.width,
                coin.height
            )
            pygame.draw.rect(screen, (255, 215, 0), coin_screen)  # Yellow coins

            # Check if the player collects a coin
            player_rect = pygame.Rect(player.x - 10, player.y - 10, 20, 20)
            if player_rect.colliderect(coin):
                coins.remove(coin)  # Remove coin
                engine.score[0] += 1  # Player earns 1 point

        # Player controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            engine.rotate_ship(0, -3)
        if keys[pygame.K_RIGHT]:
            engine.rotate_ship(0, 3)
        if keys[pygame.K_UP]:
            engine.thrust_ship(0, 1)
        if keys[pygame.K_SPACE]:
            engine.shoot(0)

        # Enemy movement and behavior
        if enemy:
            chase_and_shoot(enemy, player, walls, engine)
            move_enemy_randomly(enemy)  # Random movement if the player is not visible
            avoid_walls(enemy, walls)  # Avoid obstacles

        # Update game state
        try:
            engine.update(walls)
        except Exception as e:
            print(f"Error: {e}")

        # Draw ships relative to camera
        for i, ship in enumerate(engine.ships):
            draw_ship(screen, ship, BLUE if i == 0 else RED, camera_x, camera_y)

        # Display HP and Score
        font = pygame.font.SysFont(None, 24)
        p1_hp = engine.ships[0].hp
        p2_hp = engine.ships[1].hp if len(engine.ships) > 1 else 0
        hp_text = font.render(f"Player HP: {p1_hp}    Enemy HP: {p2_hp}", True, (0, 0, 0))
        score_text = font.render(f"Score: {engine.score[0]}", True, (0, 0, 0))
        screen.blit(hp_text, (10, 10))
        screen.blit(score_text, (10, 40))

        engine.draw_bullets(screen, camera_x, camera_y)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()