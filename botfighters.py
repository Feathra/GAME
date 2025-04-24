import random
import pygame
import math
import time

# ------------------------
# SpaceObject Class (Physics)
# ------------------------

class SpaceObject:
    
    def __init__(self, x, y, angle=0, velocity_x=0, velocity_y=0, hp=100):
        self.x = x
        self.y = y
        self.angle = angle
        self.vx = velocity_x
        self.vy = velocity_y
        self.hp = hp  # Health points

    def thrust(self, amount):
        rad = math.radians(self.angle)
        self.vx += math.cos(rad) * amount
        self.vy += math.sin(rad) * amount

    def rotate(self, degrees):
        self.angle = (self.angle + degrees) % 360

    def update_position(self):
        self.x += self.vx
        self.y += self.vy

    def get_state(self):
        return {
            "x": self.x,
            "y": self.y,
            "vx": self.vx,
            "vy": self.vy,
            "angle": self.angle,
        }


# ------------------------
# Bullet Class
# ------------------------        
class Bullet:
    def __init__(self, x, y, angle, owner, speed=5):
        self.x = x
        self.y = y
        self.angle = angle
        self.owner = owner
        rad = math.radians(angle)
        self.vx = math.cos(rad) * speed
        self.vy = math.sin(rad) * speed

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def is_offscreen(self, world_width, world_height):
        return not (0 <= self.x <= world_width and 0 <= self.y <= world_height)


# ------------------------
# GameEngine Class
# ------------------------

class GameEngine:
    def __init__(self):
        self.ships = [
            SpaceObject(x=100, y=100),
            SpaceObject(x=300, y=300)
        ]
        self.bullets = [] 
        self.score = [0, 0]
        self.time = 0

    def update(self):
        for ship in self.ships:
            ship.update_position()

        for bullet in self.bullets:
            bullet.update()

        new_bullets = []
        for bullet in self.bullets:
            hit = False
            for i, ship in enumerate(self.ships):
                if i != bullet.owner and self._collides(bullet, ship):  # 🟪 avoid friendly fire
                    ship.hp -= 10  # 🟪 damage dealt
                    hit = True
                    print(f"Ship {i} hit! HP: {ship.hp}")
            if not hit:
                new_bullets.append(bullet)

        self.bullets = [b for b in new_bullets if not b.is_offscreen(WORLD_WIDTH, WORLD_HEIGHT)]
            
    def shoot(self, ship_index):
        ship = self.ships[ship_index]
        bullet = Bullet(ship.x, ship.y, ship.angle, owner=ship_index)
        self.bullets.append(bullet)
    
    def draw_bullets(self, screen, camera_x, camera_y):
        for bullet in self.bullets:
            screen_x, screen_y = world_to_screen(bullet.x, bullet.y, camera_x, camera_y)
            pygame.draw.circle(screen, (0, 0, 0), (screen_x, screen_y), 3)


    def rotate_ship(self, index, degrees):
        self.ships[index].rotate(degrees)

    def thrust_ship(self, index, amount):
        self.ships[index].thrust(amount)

    def get_game_state(self):
        return {
            "ships": [ship.get_state() for ship in self.ships],
            "score": self.score,
            "time": self.time
        }
    def _collides(self, bullet, ship):
        dist = math.hypot(bullet.x - ship.x, bullet.y - ship.y)
        return dist < 15  # 🟪 simple collision radius
    

# ------------------------
# Main Game Loop with Pygame
# ------------------------

# 🟪 Set world size larger than screen
WORLD_WIDTH, WORLD_HEIGHT = 2000, 2000
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
RED = (255, 50, 50)

background_image = pygame.image.load("galaxie.jpg")  # 🟪 load background image
background_image = pygame.transform.scale(background_image, (WORLD_WIDTH, WORLD_HEIGHT))  # 🟪 match world size


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

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("BotFighters Arena")
    clock = pygame.time.Clock()
    engine = GameEngine()

    running = True
    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player controls (reduced thrust)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            engine.rotate_ship(0, -3)
        if keys[pygame.K_RIGHT]:
            engine.rotate_ship(0, 3)
        if keys[pygame.K_UP]:
            engine.thrust_ship(0, 0.1)  # 🟪 reduced thrust
        if keys[pygame.K_SPACE]:        # 🟪 SHOOT!
            engine.shoot(0)

        # Dummy agent movement
        engine.rotate_ship(1, 1)
        engine.thrust_ship(1, 0.05)
        
        if random.random() < 0.02:  # 🟪 2% chance each frame to shoot
            engine.shoot(1)

        # Update game state
        engine.update()

        # 🟪 Camera follows player ship
        player = engine.ships[0]
        camera_x = player.x
        camera_y = player.y
        screen.blit(background_image, (-camera_x + SCREEN_WIDTH // 2, -camera_y + SCREEN_HEIGHT // 2))  # 🟪 draw background


        # 🟪 Draw ships relative to camera
        for i, ship in enumerate(engine.ships):
            draw_ship(screen, ship, BLUE if i == 0 else RED, camera_x, camera_y)
        
        # 🟪 Display HP
        font = pygame.font.SysFont(None, 24)
        p1_hp = engine.ships[0].hp
        p2_hp = engine.ships[1].hp
        hp_text = font.render(f"Player HP: {p1_hp}    Enemy HP: {p2_hp}", True, (0, 0, 0))
        screen.blit(hp_text, (10, 10))


        engine.draw_bullets(screen, camera_x, camera_y)


        pygame.display.flip()
        clock.tick(60)


    pygame.quit()

if __name__ == "__main__":
    main()
