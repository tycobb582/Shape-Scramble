import random
import pygame
import vector as v
import matrix as m
import math


class Basic:
    """
    Basic functions for creating any object with collision (inherited by circular objects)
    """
    def __init__(self, start_pos, radius):
        """
        Creates a basic object with a bounding box
        :param start_pos: The center point of the shape
        :param radius
        """
        self.center = start_pos
        self.radius = radius
        self.aabb = self.create_aabb()

    def create_aabb(self):
        """
        Creates an Axially Aligned Bounding Box for the object
        :return: The AABB
        """
        point_x = self.center.x - self.radius
        point_y = self.center.y - self.radius
        size = self.radius * 2
        bounding_box = pygame.Rect(point_x, point_y, size, size)
        return bounding_box


class Polygon(Basic):
    """
    Basic functions for creating any object whose shape is a regular polygon
    """
    def __init__(self, center, num_points, radius):
        """
        Creates a regular polygonal shape
        :param center:
        :param num_points: The number of vertices the shape has
        :param radius: Distance from the center of the shape to a vertex
        """
        self.radius = radius
        self.color = (255, 255, 255)
        self.area = None
        self.num_points = num_points
        self.point_matrix = self.create_point_matrix()
        super().__init__(center, radius)

    def get_relative_point(self, radians):
        """
        Finds a point vector relative to the center of the shape.
        :param radians: Angle of the line between the initial point and second point
        :return:
        """
        x_y_distance = v.polar_to_Vector2(self.radius, math.degrees(radians))
        new_point = self.center + x_y_distance
        return new_point

    def create_point_matrix(self):
        """
        Creates a matrix containing the point data of the shape
        :return: The matrix that contains the point vectors of the shape
        """
        point_list = []
        for point_index in range(self.num_points):
            angle_poly = math.radians((360 / self.num_points) * point_index)
            next_point = self.get_relative_point(angle_poly)
            point_list.append(next_point)
        point_matrix = m.Matrix(*point_list)
        if self.num_points == 4:
            # I wanted normal looking squares so I rotated them
            r_point = point_matrix.get_row(1)
            point_matrix = m.hg(point_matrix)
            T = m.translate(3, -r_point.x, -r_point.y)
            R = m.Matrix(v.Vector(*m.rotate(45).get_row(0), 0), v.Vector(*m.rotate(45).get_row(1), 0), v.Vector(0, 0, 1))
            point_matrix *= T * R * m.inverse(T) * m.project(2)
            # Rotation throws the center point off
            half_side_length = ((self.radius * 2) / (2 ** 0.5)) / 2
            self.radius = int(half_side_length)
            self.center = point_matrix.get_row(1) + v.Vector(half_side_length, half_side_length)
        return point_matrix

    def create_aabb(self):
        """
        Creates an Axially Aligned Bounding Box that fits tightly around the shape
        :return: Returns the bounding box
        """
        if self.num_points != 4:
            bounding_box = super().create_aabb()
        else:
            point_x = self.point_matrix.get_row(1).x
            point_y = self.point_matrix.get_row(1).y
            size = int(self.point_matrix.get_row(0).x) - int(point_x)
            bounding_box = pygame.Rect(point_x, point_y, size, size)
        return bounding_box

    def draw(self, surf, width=0):
        """
        Draws the polygon to a surface
        :param surf: Surface to draw to
        :param width: Width of the shape fill
        """
        point_coords = []
        for point in self.point_matrix.rows:
            point_coords.append(point.i)
        pygame.draw.polygon(surf, self.color, point_coords, width)
        #pygame.draw.rect(surf, (255, 255, 0), self.aabb, 1)    # Bounding Box
        #pygame.draw.circle(surf, (0, 0, 255), self.center.i, 1)    # Center point


class Player(Basic):
    def __init__(self, start_pos, surf, image):
        """
        Creates a player object that can fire projectiles
        :param start_pos: Center point of player shape
        :param surf: Surface to draw to
        :param image: Player image
        """
        self.image = image
        self.center = start_pos
        self.speed = 150
        self.movement = v.Vector2(0, 0)
        self.radius = 10
        self.score = 5
        self.color = (0, 255, 0)
        self.shot_timer = 0.1
        self.shot_list = []
        self.surf = surf
        super().__init__(start_pos, self.radius)

    def update(self, dt, buffer, window):
        """
        Updates the player's position and keeps them within game boundaries
        :param dt: Change in time
        :param buffer: Space reserved for UI
        :param window: Window dimensions
        """
        self.shot_timer -= dt
        self.center += self.movement * self.speed * dt
        self.aabb = self.create_aabb()
        if self.center.x - self.radius < 0:
            self.center.x = self.radius
        elif self.center.x + self.radius > window[0]:
            self.center.x = window[0] - self.radius
        if self.center.y - self.radius < buffer // 2:
            self.center.y = buffer // 2 + self.radius
        elif self.center.y + self.radius > window[1]:
            self.center.y = window[1] - self.radius

    def handle_input(self, mp, shot_image, shot_effect):
        """
        Handles input that moves the player and fires projectiles
        :param mp: Mouse position
        :param shot_image: The image for projectiles
        :param shot_effect: The sound effect to play when firing a projectile
        """
        keys = pygame.key.get_pressed()
        mouse_button = pygame.mouse.get_pressed(3)
        mouse_pos = mp
        # Movement controls with WASD or Arrow Keys
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.movement.x = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.movement.x = 1
        else:
            self.movement.x = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.movement.y = -1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.movement.y = 1
        else:
            self.movement.y = 0
        if mouse_button[0] and self.shot_timer <= 0:
            # Left click or holding left click
            target_pos = v.Vector2(*mouse_pos)
            diff = target_pos - self.center
            shot_angle = math.atan2(-diff.y, diff.x)
            shot_pos = self.center + v.polar_to_Vector2(self.radius + 1, math.degrees(shot_angle))
            new_shot = Shot(shot_pos, shot_angle, self.surf, shot_image)
            self.shot_list.append(new_shot)
            self.shot_timer = 0.25
            shot_effect.play()

    def draw(self):
        """
        Draws the object to the screen
        """
        for s in self.shot_list:
            s.draw()
        blit_pos = self.center - v.Vector(self.radius, self.radius)
        self.surf.blit(self.image, (blit_pos.i))
        #pygame.draw.circle(self.surf, self.color, self.center.i, self.radius, 1)   #Collision circle


class Shot(Basic):
    def __init__(self, start_pos, angle, surf, image):
        """
        Creates a projectile object with constant velocity
        :param start_pos: Start position for center of the shape
        :param angle: Angle to move in
        :param surf: Surface to draw to
        :param image: Object image
        """
        self.center = start_pos
        self.speed = 200
        self.movement = v.polar_to_Vector2(self.speed, math.degrees(angle))
        self.color = (188, 80, 8)
        self.radius = 5
        self.surf = surf
        super().__init__(start_pos, self.radius)
        self.image = image

    def update(self, dt):
        """
        Moves the projectile and updates it's bounding box
        :param dt: Change in time
        """
        self.center += self.movement * dt
        self.aabb = self.create_aabb()

    def draw(self):
        """
        Draws the shape to its assigned surface
        """
        blit_pos = self.center - v.Vector(self.radius, self.radius)
        self.surf.blit(self.image, (blit_pos.i))
        #pygame.draw.circle(self.surf, self.color, self.center.i, self.radius, 1)   # Collision circle


class Enemy(Polygon):
    def __init__(self, center):
        """
        Creates a random enemy shape that tracks the player
        :param center: Center point of the shape
        """
        self.center = center
        self.speed = 70
        self.movement = v.Vector2(0, 0)
        self.accel_timer = 10
        self.seek_timer = 0
        self.accel = 25
        self.radius = random.randint(15, 30)
        self.shape = random.randint(0, 8)
        if self.shape == 0:
            self.shape = "Circle"
            self.area = None    # Needs to have area attribute to change into polygon later
        else:
            self.shape = "Polygon"
            self.num_points = random.randint(3, 10)
            super().__init__(center, self.num_points, self.radius)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

    def update(self, dt, buffer, window, player_pos):
        """
        Increases the shape's speed every 10 seconds. Target's player's position every second. Moves the shape and
        bounces the shape if it collides with the game boundaries.
        :param dt: Change in time
        :param buffer: Space reserved for UI
        :param window: Window dimensions
        :param player_pos: The position of the player
        """
        self.accel_timer -= dt
        self.seek_timer -= dt
        if self.accel_timer <= 0:
            self.speed += self.accel
            self.accel_timer = 10
        if self.seek_timer <= 0:
            # Adjusts targeting to the current player position every second,
            self.seek_target(player_pos)
            self.seek_timer = 1
        self.center += self.movement * dt
        if self.shape != "Circle":
            self.poly_movement(dt)
            self.aabb = self.create_aabb()
        if self.center.x - self.radius < 0:
            self.center.x = self.radius
            self.movement = self.movement.perpendicular
        elif self.center.x + self.radius > window[0]:
            self.center.x = window[0] - self.radius
            self.movement = self.movement.perpendicular
        if self.center.y - self.radius < buffer // 2:
            self.center.y = buffer // 2 + self.radius
            self.movement = self.movement.perpendicular
        elif self.center.y + self.radius > window[1]:
            self.center.y = window[1] - self.radius
            self.movement = self.movement.perpendicular

    def poly_movement(self, dt):
        """
        Moves a polygonal shape
        :param dt: Change in time
        """
        self.point_matrix = m.hg(self.point_matrix)
        frame_movement = self.movement * dt
        translation = m.translate(3, *frame_movement)
        self.point_matrix *= translation * m.project(2)

    def seek_target(self, target):
        """
        Adjusts an object's movement towards a target
        :param target: An object to move towards
        """
        diff = target - self.center
        angle = math.atan2(-diff.y, diff.x)
        self.movement = v.polar_to_Vector2(self.speed, math.degrees(angle))

    def draw(self, surf, width=0):
        """
        Draws the object to a surface
        :param surf: The surface to draw to
        :param width: Width of the collision shape fill
        """
        if self.shape == "Circle":
            pygame.draw.circle(surf, self.color, self.center.i, self.radius)
        else:
            super().draw(surf)


class Pickup(Polygon):
    def __init__(self, center, image_set):
        """
        Creates a stationary triangle
        :param center: Center point of the triangle
        :param image_set: The set of images that the triangle can change to
        """
        self.center = center
        self.images = image_set
        self.image = image_set[0]
        self.radius = 15
        self.shape = "Polygon"
        self.num_points = 3
        super().__init__(self.center, self.num_points, self.radius)
        self.color = (86, 190, 30)
        self.score = 0.5
        self.score_at_collection = None
        self.decay_timer = 5
        self.collected = False

    def update(self, dt):
        """
        Counts down it's internal timer. When the timer reaches 0, state changes accordingly.
        :param dt: Delta time
        :return: True if the triangle is to disappear
        """
        self.decay_timer -= dt
        if self.decay_timer <= 0 and self.score == 0.5:
            self.decay_timer = 5
            self.color = (255, 191, 0)
            self.score = 0.25
            self.image = self.images[1]
        if self.decay_timer <= 0 and self.score == 0.25:
            self.decay_timer = 2
            self.score = 0
            self.image = self.images[2]
        if self.decay_timer <= 0 and self.score == 0:
            return True

    def draw(self, surf, width=1):
        """
        Draws the object to a surface
        :param surf: Surface to draw to
        :param width: Width of collision shape fill
        :return:
        """
        blit_pos = self.center - v.Vector(self.radius, self.radius)
        surf.blit(self.image, (blit_pos.i))
        #super().draw(surf, width)  # Collision Triangle

