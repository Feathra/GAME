import random
import math
import time
import pygame

class DummyAgent:
    def __init__(self, ship_index):
        self.ship_index = ship_index  # The index of the ship controlled by the agent
        self.last_direction_change = time.time()  # Track the last time the direction was changed
        self.current_rotation = 0  # Current rotation direction

    def decide(self, game_state, walls):
        """
        Returns a dictionary with possible actions:
        {
            "rotate": -3,     # Rotate left
            "thrust": 1,      # Move forward
            "shoot": True     # Shoot
        }
        """
        # Get the agent's ship and the target ship
        my_ship = game_state["ships"][self.ship_index]
        target_ship = game_state["ships"][1 - self.ship_index]  # The other ship is the target

        # Extract positions and angles
        my_x, my_y, my_angle = my_ship["x"], my_ship["y"], my_ship["angle"]
        target_x, target_y = target_ship["x"], target_ship["y"]

        # Scan for enemies with the laser
        enemy_detected = self._scan_with_laser(my_x, my_y, my_angle, target_x, target_y, walls)

        if enemy_detected:
            # Calculate the angle to the enemy
            dx = target_x - my_x
            dy = target_y - my_y
            angle_to_enemy = math.degrees(math.atan2(dy, dx))

            # Calculate the shortest rotation direction
            angle_difference = (angle_to_enemy - my_angle + 360) % 360
            if angle_difference > 180:
                angle_difference -= 360  # Rotate left if shorter

            # Limit the rotation speed
            max_rotation_speed = 10  # Maximum rotation speed per frame
            rotation = max(-max_rotation_speed, min(angle_difference, max_rotation_speed))

            # Rotate towards the enemy and shoot
            print(f"Enemy detected! Rotating by {rotation:.2f} degrees and shooting.")
            return {"rotate": rotation, "thrust": 0, "shoot": True}

        # Check if there is a wall directly in front of the agent
        if self._is_wall_ahead(my_x, my_y, my_angle, walls):
            # Rotate randomly to avoid the wall
            self.current_rotation = random.choice([-1, 1]) * random.randint(90, 180)  # Random angle between 90 and 180 degrees
            print(f"Wall ahead! Rotating by {self.current_rotation} degrees.")
            return {"rotate": self.current_rotation, "thrust": 0, "shoot": False}

        # Add slow self-rotation
        slow_rotation = 1  # Very slow rotation (1 degree per frame)
        return {"rotate": slow_rotation, "thrust": 1, "shoot": False}

    def _scan_with_laser(self, x, y, angle, target_x, target_y, walls):
        """
        Simulates a laser scan in the direction of the ship's angle.
        Returns True if the laser detects the enemy, otherwise False.
        """
        laser_length = 1000  # Maximum laser range
        rad = math.radians(angle)
        laser_end_x = x + math.cos(rad) * laser_length
        laser_end_y = y + math.sin(rad) * laser_length

        # Check for wall collisions
        for wall in walls:
            wall_rect = {"x": wall.x, "y": wall.y, "width": wall.width, "height": wall.height} if hasattr(wall, 'x') else wall
            if self._line_intersects_rect(x, y, laser_end_x, laser_end_y, wall_rect):
                # Shorten the laser to the wall
                laser_end_x, laser_end_y = DummyAgent._get_intersection_point(
                    x, y, laser_end_x, laser_end_y, {
                        "x": getattr(wall, 'x', 0), "y": getattr(wall, 'y', 0), 
                        "width": getattr(wall, 'width', 0), "height": getattr(wall, 'height', 0)
                    }
                )
                break

        # Check if the laser hits the enemy
        enemy_rect = {"x": target_x - 10, "y": target_y - 10, "width": 20, "height": 20}  # Size of the enemy
        if self._line_intersects_rect(x, y, laser_end_x, laser_end_y, enemy_rect):
            return True

        return False

    @staticmethod
    def _line_intersects_rect(x1, y1, x2, y2, rect):
        # Checks if a line intersects a rectangle
        rect_lines = [
            ((rect["x"], rect["y"]), (rect["x"] + rect["width"], rect["y"])),
            ((rect["x"] + rect["width"], rect["y"]), (rect["x"] + rect["width"], rect["y"] + rect["height"])),
            ((rect["x"] + rect["width"], rect["y"] + rect["height"]), (rect["x"], rect["y"] + rect["height"])),
            ((rect["x"], rect["y"] + rect["height"]), (rect["x"], rect["y"]))
        ]
        for (rx1, ry1), (rx2, ry2) in rect_lines:
            if DummyAgent._line_intersects_line(x1, y1, x2, y2, rx1, ry1, rx2, ry2):
                return True
        return False

    @staticmethod
    def _line_intersects_line(x1, y1, x2, y2, x3, y3, x4, y4):
        # Checks if two lines intersect
        def ccw(a, b, c):
            return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

        return ccw((x1, y1), (x3, y3), (x4, y4)) != ccw((x2, y2), (x3, y3), (x4, y4)) and ccw((x1, y1), (x2, y2), (x3, y3)) != ccw((x1, y1), (x2, y2), (x4, y4))

    @staticmethod
    def _get_intersection_point(x1, y1, x2, y2, rect):
        # Convert pygame.Rect to dictionary if necessary
        if isinstance(rect, pygame.Rect):
            rect = {"x": rect.x, "y": rect.y, "width": rect.width, "height": rect.height}

        # Calculates the intersection point of a line with a rectangle
        rect_lines = [
            ((rect["x"], rect["y"]), (rect["x"] + rect["width"], rect["y"])),
            ((rect["x"] + rect["width"], rect["y"]), (rect["x"] + rect["width"], rect["y"] + rect["height"])),
            ((rect["x"] + rect["width"], rect["y"] + rect["height"]), (rect["x"], rect["y"] + rect["height"])),
            ((rect["x"], rect["y"] + rect["height"]), (rect["x"], rect["y"]))
        ]
        for (rx1, ry1), (rx2, ry2) in rect_lines:
            denom = (x1 - x2) * (ry1 - ry2) - (y1 - y2) * (rx1 - rx2)
            if denom == 0:
                continue
            t = ((x1 - rx1) * (ry1 - ry2) - (y1 - ry1) * (rx1 - rx2)) / denom
            u = -((x1 - x2) * (y1 - ry1) - (y1 - y2) * (x1 - rx1)) / denom
            if 0 <= t <= 1 and 0 <= u <= 1:
                return x1 + t * (x2 - x1), y1 + t * (y2 - y1)
        return x2, y2  # Default to the end of the line if no intersection is found

    def _is_wall_ahead(self, x, y, angle, walls):
        """
        Checks if there is a wall directly in front of the agent.
        """
        laser_length = 50  # Short range to check for walls ahead
        rad = math.radians(angle)
        laser_end_x = x + math.cos(rad) * laser_length
        laser_end_y = y + math.sin(rad) * laser_length

        # Check for wall collisions
        for wall in walls:
            if self._line_intersects_rect(x, y, laser_end_x, laser_end_y, {
                "x": getattr(wall, 'x', 0), "y": getattr(wall, 'y', 0), 
                "width": getattr(wall, 'width', 0), "height": getattr(wall, 'height', 0)
            }):
                return True

        return False
