import pygame
import math
import random

# ------------------------
# SpaceObject Class (Physics)
# ------------------------

class SpaceObject:
    
    def __init__(self, x, y, angle=0, velocity_x=0, velocity_y=0, hp=100, WORLD_WIDTH=2000, WORLD_HEIGHT=2000):
        self.WORLD_WIDTH = WORLD_WIDTH
        self.WORLD_HEIGHT = WORLD_HEIGHT
        self.x = x
        self.y = y
        self.angle = angle
        self.vx = velocity_x  # Anfangsgeschwindigkeit
        self.vy = velocity_y
        self.hp = hp  # Health points
        
    def update_position(self, is_enemy=False):
        max_speed = 10 if not is_enemy else 5  # Spieler: 10, Feind: 5
        friction = 0.98  # Reibungseffekt
        self.vx *= friction
        self.vy *= friction
        self.vx = max(-max_speed, min(self.vx, max_speed))
        self.vy = max(-max_speed, min(self.vy, max_speed))
        self.x += self.vx
        self.y += self.vy
        self.x = max(0, min(self.x, self.WORLD_WIDTH))
        self.y = max(0, min(self.y, self.WORLD_HEIGHT))


    def thrust(self, amount):
        rad = math.radians(self.angle)
        self.vx += math.cos(rad) * amount
        self.vy += math.sin(rad) * amount

    def rotate(self, degrees):
        self.angle = (self.angle + degrees) % 360


    def get_state(self):
        return {
            "x": self.x,
            "y": self.y,
            "vx": self.vx,
            "vy": self.vy,
            "angle": self.angle,
        }

    def check_wall_collision(self, walls):
        ship_rect = pygame.Rect(self.x - 10, self.y - 10, 20, 20)  # Größe des Schiffs
        for wall in walls:
            if ship_rect.colliderect(wall):
                # Rückstoß basierend auf der Richtung
                if self.x < wall.x:  # Links der Wand
                    self.x = wall.x - 10
                    self.vx = 0
                elif self.x > wall.x + wall.width:  # Rechts der Wand
                    self.x = wall.x + wall.width + 10
                    self.vx = 0
                if self.y < wall.y:  # Über der Wand
                    self.y = wall.y - 10
                    self.vy = 0
                elif self.y > wall.y + wall.height:  # Unter der Wand
                    self.y = wall.y + wall.height + 10
                    self.vy = 0


# ------------------------
# Bullet Class
# ------------------------        
class Bullet:
    def __init__(self, x, y, angle, owner, speed=15):  # Kugeln sind schneller
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
    def __init__(self, walls):
        self.ships = [
            SpaceObject(*generate_valid_position(walls, WORLD_WIDTH, WORLD_HEIGHT)),
            SpaceObject(*generate_valid_position(walls, WORLD_WIDTH, WORLD_HEIGHT))
        ]
        self.bullets = [] 
        self.score = [0, 0]
        self.time = 0

    def update(self, walls):
        for i, ship in enumerate(self.ships[:]):
            is_enemy = (i == 1)  # Der Feind ist das zweite Schiff
            ship.update_position(is_enemy=is_enemy)
            ship.check_wall_collision(walls)  # Wall collision check
            if ship.hp <= 0:  # Entferne das Schiff, wenn HP 0 sind
                self.ships.remove(ship)

        for bullet in self.bullets:
            bullet.update()
        new_bullets = []
        for bullet in self.bullets:
            hit = False
            for i, ship in enumerate(self.ships):
                if i != bullet.owner and self._collides(bullet, ship):  # Avoid friendly fire
                    ship.hp -= 10  # Damage dealt
                    hit = True
                    print(f"Ship {i} hit! HP: {ship.hp}")
            if not hit:
                new_bullets.append(bullet)

        self.bullets = [b for b in new_bullets if not b.is_offscreen(self.ships[0].WORLD_WIDTH, self.ships[0].WORLD_HEIGHT)]
            
    def shoot(self, ship_index):
        ship = self.ships[ship_index]
        # Spawn bullet slightly in front of the ship
        rad = math.radians(ship.angle)
        bullet_x = ship.x + math.cos(rad) * 15  # Offset by 15 units in the direction of the ship
        bullet_y = ship.y + math.sin(rad) * 15
        bullet = Bullet(bullet_x, bullet_y, ship.angle, owner=ship_index, speed=15)  # Schnelle Kugeln
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

#background_image = pygame.image.load("galaxie.jpg")  # Load background image
#background_image = pygame.transform.scale(background_image, (WORLD_WIDTH, WORLD_HEIGHT))


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
    # Ein größeres Labyrinth mit mehreren Wegen und Sackgassen
    walls = [
        # Außenwände
        pygame.Rect(50, 50, 1900, 20),  # Obere Wand
        pygame.Rect(50, 50, 20, 1900),  # Linke Wand
        pygame.Rect(50, 1930, 1900, 20),  # Untere Wand
        pygame.Rect(1930, 50, 20, 1900),  # Rechte Wand

        # Innere Strukturen
        pygame.Rect(200, 200, 20, 400),  # Vertikale Wand links oben
        pygame.Rect(200, 600, 400, 20),  # Horizontale Wand links oben
        pygame.Rect(600, 200, 20, 400),  # Vertikale Wand Mitte oben
        pygame.Rect(600, 600, 400, 20),  # Horizontale Wand Mitte oben
        pygame.Rect(1000, 200, 20, 800),  # Vertikale Wand rechts oben
        pygame.Rect(200, 1000, 800, 20),  # Horizontale Wand Mitte
        pygame.Rect(1200, 200, 20, 800),  # Vertikale Wand rechts Mitte
        pygame.Rect(1200, 1000, 400, 20),  # Horizontale Wand rechts Mitte
        pygame.Rect(1600, 200, 20, 800),  # Vertikale Wand rechts oben
        pygame.Rect(200, 1400, 400, 20),  # Horizontale Wand links unten
        pygame.Rect(600, 1400, 20, 400),  # Vertikale Wand Mitte unten
        pygame.Rect(600, 1800, 400, 20),  # Horizontale Wand Mitte unten
        pygame.Rect(1000, 1400, 20, 400),  # Vertikale Wand rechts unten
        pygame.Rect(1200, 1400, 400, 20),  # Horizontale Wand rechts unten
        pygame.Rect(1600, 1400, 20, 400),  # Vertikale Wand rechts unten

        # Sackgassen
        pygame.Rect(300, 300, 100, 20),  # Horizontale Sackgasse links oben
        pygame.Rect(1500, 1500, 100, 20),  # Horizontale Sackgasse rechts unten
        pygame.Rect(800, 800, 20, 100),  # Vertikale Sackgasse Mitte
    ]
    return walls


def is_position_valid(x, y, walls):
    ship_rect = pygame.Rect(x - 10, y - 10, 20, 20)  # Größe des Schiffs
    for wall in walls:
        if ship_rect.colliderect(wall):
            return False
    return True


def generate_valid_position(walls, world_width, world_height):
    while True:
        x = random.randint(100, world_width - 100)  # Vermeide die Außenwände
        y = random.randint(100, world_height - 100)
        if is_position_valid(x, y, walls):
            return x, y


def move_enemy_randomly(enemy):
    # Zufällige Rotation
    if random.random() < 0.1:  # 10% Wahrscheinlichkeit pro Frame
        enemy.rotate(random.choice([-5, 5]))  # Drehe nach links oder rechts

    # Zufälliger Schub
    if random.random() < 0.2:  # 20% Wahrscheinlichkeit pro Frame
        enemy.thrust(0.5)  # Leichter Schub


def avoid_walls(enemy, walls):
    ship_rect = pygame.Rect(enemy.x - 10, enemy.y - 10, 20, 20)
    for wall in walls:
        if ship_rect.colliderect(wall):
            # Drehe den Feind, wenn er eine Wand berührt
            enemy.rotate(180)  # Drehe um 180 Grad
            enemy.thrust(-1)  # Rückwärtsbewegung


def chase_player(enemy, player):
    # Berechne den Winkel zum Spieler
    dx = player.x - enemy.x
    dy = player.y - enemy.y
    angle_to_player = math.degrees(math.atan2(dy, dx))

    # Drehe den Feind in Richtung des Spielers
    if abs(angle_to_player - enemy.angle) > 5:  # Nur drehen, wenn der Winkel signifikant ist
        if (angle_to_player - enemy.angle) % 360 < 180:
            enemy.rotate(3)  # Drehe nach rechts
        else:
            enemy.rotate(-3)  # Drehe nach links

    # Schub in Richtung des Spielers
    enemy.thrust(0.5)


def can_see_player(enemy, player, walls):
    # Berechne die Linie zwischen Feind und Spieler
    dx = player.x - enemy.x
    dy = player.y - enemy.y
    distance = math.hypot(dx, dy)
    steps = int(distance / 10)  # Teile die Linie in Schritte auf

    for step in range(steps):
        check_x = enemy.x + dx * (step / steps)
        check_y = enemy.y + dy * (step / steps)
        check_rect = pygame.Rect(check_x - 5, check_y - 5, 10, 10)  # Kleiner Bereich zum Prüfen
        for wall in walls:
            if check_rect.colliderect(wall):
                return False  # Wand blockiert die Sicht
    return True


def chase_and_shoot(enemy, player, walls, engine):
    if can_see_player(enemy, player, walls):
        # Verfolge den Spieler
        chase_player(enemy, player)

        # Schieße auf den Spieler
        if random.random() < 0.05:  # 5% Wahrscheinlichkeit pro Frame
            engine.shoot(1)  # Feind schießt (Index 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("BotFighters Arena")

    walls = create_labyrinth()

    clock = pygame.time.Clock()
    engine = GameEngine(walls)  # Wände an die GameEngine übergeben

    running = True
    while running:
        screen.fill(WHITE)
        player = engine.ships[0]
        enemy = engine.ships[1] if len(engine.ships) > 1 else None  # Prüfe, ob der Feind existiert
        
        camera_x = player.x
        camera_y = player.y

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw walls (relative to camera)
        for wall in walls:
            wall_screen = pygame.Rect(
                wall.x - camera_x + SCREEN_WIDTH // 2,
                wall.y - camera_y + SCREEN_HEIGHT // 2,
                wall.width,
                wall.height
            )
            pygame.draw.rect(screen, (80, 80, 80), wall_screen)
        
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

        # Feindbewegung und Verhalten
        if enemy:
            chase_and_shoot(enemy, player, walls, engine)
            move_enemy_randomly(enemy)  # Zufällige Bewegung, wenn der Spieler nicht sichtbar ist
            avoid_walls(enemy, walls)  # Hindernisse vermeiden

        # Update game state
        try:
            engine.update(walls)
        except Exception as e:
            print(f"Error: {e}")

        # Draw ships relative to camera
        for i, ship in enumerate(engine.ships):
            draw_ship(screen, ship, BLUE if i == 0 else RED, camera_x, camera_y)

        # Display HP
        font = pygame.font.SysFont(None, 24)
        p1_hp = engine.ships[0].hp
        p2_hp = engine.ships[1].hp if len(engine.ships) > 1 else 0
        hp_text = font.render(f"Player HP: {p1_hp}    Enemy HP: {p2_hp}", True, (0, 0, 0))
        screen.blit(hp_text, (10, 10))

        engine.draw_bullets(screen, camera_x, camera_y)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
