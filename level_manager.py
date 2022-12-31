import math
import random
import pygame
import classes
import vector as v
import matrix as m


class level_manager:
    def __init__(self, win, ui_space):
        """
        Creates an object that holds all game variables and controls everything that happens in game.
        :param win: The window that the game is to be played in
        :param ui_space: Amount of space reserved for UI
        """
        self.win = win
        self.win_dim = (win.get_width(), win.get_height())
        self.buffer = ui_space
        self.enemies = [classes.Enemy(v.Vector2(500, 200))]
        self.enemy_spawn_timer = 30
        self.pickup_spawn_timer = random.uniform(0.5, 2)
        self.triangle_points_collected = 0
        self.pickups = []
        self.state = "Title"
        self.ttc = 0    # Total Triangles Collected
        self.tes = 0    # Total Enemies Shot
        self.tts = 0    # Total Time Survived
        self.images = {"Player": pygame.image.load("Images\\player.png"),
                       "Title Player": pygame.image.load("Images\\title_player.png"),
                       "Shot" : pygame.image.load("Images\\shot image.png"),
                       "Triangles": [pygame.image.load("Images\\green tri.png"),
                                     pygame.image.load("Images\\yellow tri.png"),
                                     pygame.image.load("Images\\red tri.png")]}
        self.sfx = {"Shot": pygame.mixer.Sound("Sounds\\Shot.ogg"),
                    "Damage": pygame.mixer.Sound("Sounds\\Hurt.ogg"),
                    "Enemy Hit": pygame.mixer.Sound("Sounds\\Pop.ogg"),
                    "Game Over": pygame.mixer.Sound("Sounds\\GameOver.ogg"),
                    "Title": pygame.mixer.Sound("Sounds\\Title.ogg"),
                    "Good Triangle": pygame.mixer.Sound("Sounds\\Good Triangle.ogg"),
                    "Bad Triangle": pygame.mixer.Sound("Sounds\\Bad Triangle.ogg"),
                    "Enemy Spawn": pygame.mixer.Sound("Sounds\\Enemy Spawn.ogg")}
        self.sfx["Good Triangle"].set_volume(0.4)
        self.sfx["Title"].play()
        starting_position = v.Vector(self.win_dim[0] // 2, self.win_dim[1] // 2)
        self.player = classes.Player(starting_position, win, self.images["Player"])

        # Text
        self.normal = pygame.font.SysFont("Arial", 21)
        self.header = pygame.font.SysFont("Arial", 24)
        self.title = pygame.font.SysFont("Arial", 28)

        # Title Screen
        self.start_rect = None
        self.start_hover = False
        self.quit_rect = None
        self.quit_hover = False

    def reset(self):
        """
        Resets all game variables to play again.
        """
        starting_position = v.Vector(self.win_dim[0] // 2, self.win_dim[1] // 2)
        self.enemies = [classes.Enemy(v.Vector2(500, 200))]
        self.enemy_spawn_timer = 30
        self.pickup_spawn_timer = random.uniform(0.5, 2)
        self.triangle_points_collected = 0
        self.pickups = []
        self.player = classes.Player(starting_position, self.win, self.images["Player"])
        self.ttc = 0
        self.tes = 0
        self.tts = 0
        self.sfx["Title"].play()

    def circle_collision(self, v1, v2, r1, r2):
        """
        Detects collision between two circles
        :param v1: Center coordinate of the first circle as a Vector
        :param v2: Center coordinate of the second circle as a Vector
        :param r1: Radius of the first circle
        :param r2: Radius of the second circle
        :return: True if collision, False otherwise
        """
        if (v1 - v2).mag <= r1 + r2:
            return True
        else:
            return False

    def triangle_area(self, p1, p2, p3, circle=None):
        """
        Returns the area of a triangle given three points
        :param p1: The first point in the triangle
        :param p2: The second point in the triangle
        :param p3: The third point in the triangle (pass circle center here for circle collision)
        :param circle: If a circle object is passed, check for sector area
        :return: The area of the triangle
        """
        # Get the distance between each point for the side lengths, then apply Heron's Formula
        vec1 = p1 - p2
        vec2 = p2 - p3
        vec3 = p1 - p3
        a = vec1.mag
        b = vec2.mag
        c = vec3.mag
        s = (a + b + c) / 2
        area = (s * (s - a) * (s - b) * (s - c)) ** 0.5
        if circle:
            # p3 is circle center. Find the angle between p1-p3 and p2-p3 to calculate the area of the circle sector
            angle = self.angle_between_vectors(vec2, vec3)
            sector_area = (angle / 360) * math.pi * (circle.radius ** 2)
            return area, sector_area
        return area

    def angle_between_vectors(self, v1, v2):
        """
        Returns the angle between two vectors
        :param v1: First vector
        :param v2: Second vector
        :return: The angle between them (in degrees)
        """
        dot = v.dot(v1, v2)
        c_angle = dot / (v1.mag * v2.mag)
        angle = math.acos(c_angle)
        return math.degrees(angle)

    def circle_poly_collision(self, circle, shape, og_area):
        """
        Detects collision between a circle and a polygon
        :param circle: The circle object being checked
        :param shape: A Matrix containing the points of the polygon
        :param og_area: Area of the polygon
        :return: True if a collision occurs, False otherwise
        """
        # Splits the shape into triangles focused on the vector point and calculates the combined area of each
        test_area = 0
        sector_area = 0
        for point_index in range(shape.num_rows):
            second_point = point_index + 1
            if second_point > shape.num_rows - 1:
                second_point = 0
            area_add, sector_add = self.triangle_area(shape.get_row(point_index), shape.get_row(second_point),
                                                 circle.center, circle)
            test_area += area_add
            sector_area += sector_add
        # Now that we have the combined area of each triangle and the full circle sector between the triangles, we
        # can subtract the sector area from the test area. That way, we're checking the area between the shape and edge
        # of the circle rather than the shape and the center of the circle.
        test_area -= sector_area
        # Area calculations seem to have a very small inaccuracy, so the function will return true if the combined area
        # is between a range of values extremely close to the original area, rather than exactly equal to the original.
        float_check = 0.00000001
        if test_area - float_check <= og_area + float_check:
            return True
        else:
            # This area test doesn't work if the circle is colliding with a point in the shape,
            # so next the function checks collision with each point
            for point_index in range(shape.num_rows):
                result = self.circle_collision(circle.center, shape.get_row(point_index), circle.radius, 0)
                if result:
                    return True
        # If we get here, neither test has passed and the function returns False
        return False

    def aabb_test(self, subject, other):
        """
        Checks collision between the bounding boxes of shapes
        :param subject: The object you want to check collision for
        :param other: The object you're checking collision against
        :return: True if the boxes overlap, false otherwise
        """
        collision = False
        if subject.aabb.colliderect(other.aabb):
            if other.num_points == 3:
                if other.area is None:  # Only calculate the shape's area once then store it to the shape
                    other.area = self.triangle_area(*other.point_matrix.rows)
                collision = self.circle_poly_collision(subject, other.point_matrix, other.area)
            elif other.num_points == 4:
                collision = True
            else:
                if other.area is None:
                    sample_tri = m.Matrix(other.center, other.point_matrix.get_row(0), other.point_matrix.get_row(1))
                    other.area = self.triangle_area(*sample_tri.rows) * other.num_points
                collision = self.circle_poly_collision(subject, other.point_matrix, other.area)
        return collision

    def choose_new_position(self, obj):
        """
        Selects a spawn position
        :param obj: Object to move
        :return: The new position
        """
        pos_found = False
        new_pos = None
        # The function will keep searching for a position until it is more than x pixels away from the player.
        while not pos_found:
            new_pos = v.Vector2(random.randint(obj.radius, self.win_dim[0] - obj.radius),
                                random.randint(self.buffer + obj.radius, self.win_dim[1] - obj.radius))
            # Check collision with player
            if obj.__class__.__name__ == "Enemy":
                if self.circle_collision(new_pos, self.player.center, obj.radius, self.player.radius + 100):
                    new_pos = v.Vector2(random.randint(obj.radius, self.win_dim[0] - obj.radius),
                                        random.randint(self.buffer + obj.radius, self.win_dim[1] - obj.radius))
                else:
                    pos_found = True
            else:
                # Other objects like pickups can spawn closer
                if self.circle_collision(new_pos, self.player.center, obj.radius, self.player.radius + 10):
                    new_pos = v.Vector2(random.randint(obj.radius, self.win_dim[0] - obj.radius),
                                        random.randint(self.buffer + obj.radius, self.win_dim[1] - obj.radius))
                else:
                    pos_found = True
        return new_pos

    def spawn_new_object(self, kind, object_list):
        """
        Spawns a new object on screen
        :param kind: The kind of object to spawn
        :param object_list: The list of objects to add this one to
        :return: The updated list
        """
        if kind == "Enemy":
            obj = classes.Enemy(v.Vector2(0, 0))
        else:
            obj = classes.Pickup(v.Vector2(0, 0), self.images["Triangles"])
        obj.center = self.choose_new_position(obj)
        if obj.shape == "Polygon":
            obj.point_matrix = obj.create_point_matrix()
        object_list.append(obj)
        return object_list

    def clear_collected_triangles(self):
        """
        Clears all triangles that are currently collected
        """
        for pickup in range(len(self.pickups) - 1, -1, -1):
            if self.pickups[pickup].collected:
                self.triangle_points_collected = 0
                self.pickups.remove(self.pickups[pickup])

    def player_hit(self, enemy):
        """
        Effects from player colliding with enemy
        :param enemy: The enemy collided with
        """
        self.player.score -= 1
        self.sfx["Damage"].play()
        # Change shape size, shape, color, and position
        enemy.center = self.choose_new_position(enemy)
        enemy.radius = random.randint(15, 30)
        if enemy.shape == "Polygon" or random.randint(1, 3) == 1:
            # Set a new polygonal shape or change a circle into one
            enemy.shape = "Polygon"
            enemy.num_points = random.randint(3, 10)
            enemy.point_matrix = enemy.create_point_matrix()
            enemy.aabb = enemy.create_aabb()
        enemy.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

    def enemy_hit(self, shot, enemy):
        """
        Effects from shot hitting enemy
        :param shot: The projectile that hit
        :param enemy: The enemy that was hit
        """
        self.sfx["Enemy Hit"].play()
        self.player.shot_list.remove(shot)
        self.enemies.remove(enemy)
        self.player.score += 1
        self.tes += 1
        self.enemies = self.spawn_new_object("Enemy", self.enemies)

    def update(self, dt):
        """
        Updates all variables that need updates
        :param dt: Change in time
        """
        # Updates pause in other states
        if self.state == "Game":
            # Timers
            self.enemy_spawn_timer -= dt
            self.pickup_spawn_timer -= dt
            self.tts += dt
            if self.enemy_spawn_timer <= 0:
                self.enemies = self.spawn_new_object("Enemy", self.enemies)
                self.sfx["Enemy Spawn"].play()
                self.enemy_spawn_timer = 30
            if self.pickup_spawn_timer <= 0:
                self.pickups = self.spawn_new_object("Pickup", self.pickups)
                # Its AABB doesn't update every frame, its position will just be set once here
                self.pickups[len(self.pickups) - 1].aabb = self.pickups[len(self.pickups) - 1].create_aabb()
                self.pickup_spawn_timer = random.uniform(0.5, 2)
            self.player.update(dt, self.buffer, self.win_dim)
            # Projectile Updates
            for s in self.player.shot_list:
                s.update(dt)
                for e in self.enemies:
                    if e.shape == "Circle" and self.circle_collision(s.center, e.center, s.radius, e.radius):
                        self.enemy_hit(s, e)
                        break
                    elif e.shape == "Polygon" and self.aabb_test(s, e):
                        self.enemy_hit(s, e)
                        break
                if s.radius < s.center.x < self.win_dim[0] - s.radius and self.buffer // 2 + s.radius < s.center.y < \
                        self.win_dim[1] - s.radius:
                    # Shot is in bounds
                    pass
                else:
                    # Add a new enemy where the bullet exited the screen
                    e = classes.Enemy(s.center)
                    self.sfx["Enemy Spawn"].play()
                    # Adjust the spawn position depending on the side that is hit
                    if s.center.x < s.radius:
                        e.center.x += e.radius
                    elif s.center.x > self.win_dim[0] - s.radius:
                        e.center.x -= e.radius
                    if s.center.y < self.buffer + s.radius:
                        e.center.y += e.radius
                    else:
                        e.center.y -= e.radius
                    if e.shape == "Polygon":
                        e.point_matrix = e.create_point_matrix()
                    self.enemies.append(e)
                    self.player.score -= 1
                    # This shot will be deleted if it passes outside the window
                    self.player.shot_list.remove(s)
            # Enemy Updates
            for e in self.enemies:
                e.update(dt, self.buffer, self.win_dim, self.player.center)
                if e.shape == "Circle":
                    if self.circle_collision(e.center, self.player.center, e.radius, self.player.radius):
                        self.player_hit(e)
                else:
                    if self.aabb_test(self.player, e):
                        self.player_hit(e)
            # Triangle Pickup Updates
            for p in self.pickups:
                result = p.update(dt)
                if result:
                    if p.collected:
                        self.triangle_points_collected -= p.score_at_collection
                    self.pickups.remove(p)
                elif not p.collected and self.aabb_test(self.player, p):
                    if p.score == 0:
                        self.sfx["Bad Triangle"].play()
                        p.collected = True
                        self.clear_collected_triangles()
                    else:
                        self.sfx["Good Triangle"].play()
                        self.ttc += 1
                        self.triangle_points_collected += p.score
                        p.score_at_collection = p.score
                        p.collected = True
            if self.triangle_points_collected >= 1:
                self.player.score += 1
                self.clear_collected_triangles()

            if self.player.score <= 0:
                self.state = "Game Over"
                self.sfx["Game Over"].play()

    def input(self):
        """
        Handles all input
        :return: True if the game should be shut down
        """
        event = pygame.event.poll()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state != "Game":
                    return True
                else:
                    self.state = "Resume"
                    self.player.shot_timer = 0.1
        elif event.type == pygame.QUIT:
            return True

        # Mouse Position Updates
        mouse_pos = pygame.mouse.get_pos()
        if self.state != "Game":
            if self.start_rect:
                if self.start_rect[0] - 5 < mouse_pos[0] < self.start_rect[0] + self.start_rect[2] + 5 and \
                        self.start_rect[1] - 5 < mouse_pos[1] < self.start_rect[1] + self.start_rect[3] + 5:
                    self.start_hover = True
                else:
                    self.start_hover = False
            if self.quit_rect:
                if self.quit_rect[0] - 5 < mouse_pos[0] < self.quit_rect[0] + self.quit_rect[2] + 5 and \
                        self.quit_rect[1] - 5 < mouse_pos[1] < self.quit_rect[1] + self.quit_rect[3] + 5:
                    self.quit_hover = True
                else:
                    self.quit_hover = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state != "Game":
                    if event.button == 1 and self.start_hover:
                        if self.state == "Game Over":
                            self.reset()
                        self.state = "Game"
                    elif event.button == 1 and self.quit_hover:
                        return True
        else:
            self.player.handle_input(mouse_pos, self.images["Shot"], self.sfx["Shot"])

    def draw(self):
        """
        Tells what to draw to the screen and when. Holds all Game state draw code.
        """
        if self.state == "Game":
            self.win.fill((50, 50, 50))
            pygame.draw.rect(self.win, (0, 0, 0), (0, 0, self.win_dim[0], self.buffer // 2))
            for p in self.pickups:
                if p.collected:
                    pygame.draw.line(self.win, p.color, p.center.i, self.player.center.i)
                p.draw(self.win)
            self.player.draw()
            for e in self.enemies:
                e.draw(self.win)
            temp = self.normal.render("Score: " + str(self.player.score), False, (255, 255, 0))
            self.win.blit(temp, (self.win_dim[0] // 2 - temp.get_width() // 2, 10))
            temp = self.normal.render("Triangle Points Stashed: " + str(self.triangle_points_collected), False, (255, 255, 0))
            self.win.blit(temp, (self.win_dim[0] * 0.69, 10))
            if self.enemy_spawn_timer > 10:
                temp = self.normal.render("Next Enemy in: " + str(int(self.enemy_spawn_timer)), False, (255, 255, 0))
            else:
                # Decimals on a timer create a sense of urgency
                temp = self.normal.render("Next Enemy in: " + str(round(self.enemy_spawn_timer, 2)), False, (255, 255, 0))
            self.win.blit(temp, (self.win_dim[0] * 0.05, 10))
        elif self.state == "Title" or self.state == "Resume" or self.state == "Game Over":
            self.draw_title_screen()

    def draw_title_screen(self):
        """
        Code for drawing Title screen. Elements are adjusted for Pause Screen and Game Over Screen.
        """
        bg_color = (20, 134, 9)
        title_color = (30, 91, 147)
        highlight_color = (41, 196, 147)
        game_over_color = (200, 22, 13)
        self.win.fill(bg_color)
        self.win.blit(self.images["Title Player"], (self.win_dim[0] // 2 - self.images["Title Player"].get_width() // 2, 50))
        temp = ""
        if self.state == "Title" or self.state == "Resume":
            temp = self.title.render("Shape Scramble!", False, title_color, bg_color)
            self.win.blit(temp, (self.win_dim[0] // 2 - temp.get_width() // 2, self.win_dim[1] // 3 - temp.get_height() // 2))
            temp = self.header.render("By Tyler Cobb", False, (0, 0, 0), bg_color)
            self.win.blit(temp, (self.win_dim[0] // 2 - temp.get_width() // 2, self.win_dim[1] * 0.37))
        elif self.state == "Game Over":
            temp = self.header.render("G A M E  O V E R", False, game_over_color, bg_color)
            self.win.blit(temp, (self.win_dim[0] // 2 - temp.get_width() // 2, self.win_dim[1] * 0.37))
            temp = self.normal.render("Triangles Collected: " + str(self.ttc), False, game_over_color, bg_color)
            stats_align = self.win_dim[1] * 0.45
            self.win.blit(temp, (self.win_dim[0] * 0.12, stats_align))
            temp = self.normal.render("Enemies Shot: " + str(self.tes), False, game_over_color, bg_color)
            self.win.blit(temp, (self.win_dim[0] * 0.422, stats_align))
            temp = self.normal.render("Time Survived: " + str(int(self.tts)) + " seconds", False, game_over_color, bg_color)
            self.win.blit(temp, (self.win_dim[0] * 0.65, stats_align))
        if not self.start_hover:
            if self.state == "Title":
                temp = self.header.render("Start Game", False, title_color, bg_color)
            elif self.state == "Resume":
                temp = self.header.render("Resume Game", False, title_color, bg_color)
            elif self.state == "Game Over":
                temp = self.header.render("Try Again", False, title_color, bg_color)
        else:
            if self.state == "Title":
                temp = self.header.render("Start Game", False, highlight_color, bg_color)
            elif self.state == "Resume":
                temp = self.header.render("Resume Game", False, highlight_color, bg_color)
            elif self.state == "Game Over":
                temp = self.header.render("Try Again", False, highlight_color, bg_color)
        self.start_rect = temp.get_rect()
        self.start_rect[0] = self.win_dim[0] // 2 - temp.get_width() // 2
        self.start_rect[1] = int(self.win_dim[1] * 0.55)
        self.win.blit(temp, (self.win_dim[0] // 2 - temp.get_width() // 2, int(self.win_dim[1] * 0.55)))
        if self.state == "Resume":
            temp = self.title.render("Score: " + str(self.player.score), False, title_color, bg_color)
            self.win.blit(temp, (self.win_dim[0] // 2 - temp.get_width() // 2, self.win_dim[1] * 0.66))
        if not self.quit_hover:
            temp = self.header.render("Quit Game", False, title_color, bg_color)
        else:
            temp = self.header.render("Quit Game", False, highlight_color, bg_color)
        self.quit_rect = temp.get_rect()
        self.quit_rect[0] = self.win_dim[0] // 2 - temp.get_width() // 2
        if self.state == "Resume":
            self.quit_rect[1] = int(self.win_dim[1] * 0.8)
        else:
            self.quit_rect[1] = int(self.win_dim[1] * 0.61)
        self.win.blit(temp, (self.quit_rect[0], self.quit_rect[1]))

