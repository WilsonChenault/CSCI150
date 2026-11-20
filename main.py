import pygame
from pygame.locals import *
from dataclasses import dataclass
import math
import random


@dataclass
class Ship:

    radius: int # Pixels, making this variable to easily change ship size during development
    x: int # Pixels
    y: int # Pixels
    angle: float # Radians
    velocity: float # Pixels/frame
    color: tuple[int, int, int] = (255, 255, 255) # Will default be white but setting as a variable just in case
    alive: bool = True
    dash_timer: int = 0
    field_timer: int = 0
    used_dash: bool = False
    used_field: bool = False

    def draw(self, surface, lasers: list):

        # Some weird stuff to create an arrowhead shape based on angle
        # Our position gives the circumcenter of the triangle. We can use the angle to determine the location
        # of the other points. The position of the triangle has to be placed into each vertex, according to PyGame
        # documentation?
        # Googled: 'pygame give position to a draw.polygon command' and
        # looked at https://www.pygame.org/docs/ref/draw.html#pygame.draw.polygon
        # The other two points are just + 2/3 pi to offset the angle, fourth point is stylistic!
        front_vertice = (self.radius * math.cos(self.angle) + self.x,
                         self.radius * math.sin(self.angle) + self.y)
        left_vertice = (self.radius * math.cos(self.angle + 2/3 * math.pi) + self.x,
                      self.radius * math.sin(self.angle + 2/3 * math.pi) + self.y)
        right_vertice = (self.radius * math.cos(self.angle - 2/3 * math.pi) + self.x,
                       self.radius * math.sin(self.angle - 2/3 * math.pi) + self.y)
        bottom_vertice = (0.02 * self.radius * math.cos(self.angle) + self.x,
                          0.02 * self.radius * math.sin(self.angle) + self.y)

        vertices = [front_vertice, left_vertice, bottom_vertice, right_vertice]
        ship = pygame.draw.polygon(surface, self.color, vertices)

        return ship

    def rotate(self, angle):
        self.angle += angle

    def accelerate(self, speed: float, speed_factor: float):
        self.velocity += speed * speed_factor

        if self.velocity > 10 * speed_factor:
            self.velocity = 10 * speed_factor
        if self.velocity < -10 * speed_factor:
            self.velocity = -10 * speed_factor

    def move(self, screen_size: tuple[int, int]):

        self.x += self.velocity * math.cos(self.angle)
        self.y += self.velocity * math.sin(self.angle)

        if self.x >= screen_size[0]:
            self.x = 0
        elif self.x <= 0:
            self.x = screen_size[0]
        if self.y >= screen_size[1]:
            self.y = 0
        elif self.y <= 0:
            self.y = screen_size[1]

    def dash(self, surface):

        if not self.used_dash:
            # Check if velocity is 0 to avoid ZeroDivisionError
            if self.velocity == 0:
                self.velocity = 0.01

            # Create unit vectors to jump the ship by
            x_hat = self.velocity * math.cos(self.angle) / self.velocity
            y_hat = self.velocity * math.sin(self.angle) / self.velocity

            self.dash_animation(surface, x_hat, y_hat)

            self.x += x_hat * 150
            self.y += y_hat * 150

            # Start the used_dash cooldown
            self.used_dash = True


    # Animation methods!
    def dash_animation(self, surface, x_hat: float, y_hat: float):

        # Recalculating vertices for the polygon -- repeated code but used rarely enough I think it is fine
        front_vertice = (self.radius * math.cos(self.angle) + self.x,
                         self.radius * math.sin(self.angle) + self.y)
        left_vertice = (self.radius * math.cos(self.angle + 2 / 3 * math.pi) + self.x,
                        self.radius * math.sin(self.angle + 2 / 3 * math.pi) + self.y)
        right_vertice = (self.radius * math.cos(self.angle - 2 / 3 * math.pi) + self.x,
                         self.radius * math.sin(self.angle - 2 / 3 * math.pi) + self.y)
        bottom_vertice = (0.02 * self.radius * math.cos(self.angle) + self.x,
                          0.02 * self.radius * math.sin(self.angle) + self.y)

        # Create four new lists to draw the ship "jumping" forward
        vertices = [front_vertice, left_vertice, bottom_vertice, right_vertice]

        first = []
        second = []
        third = []
        for vertice in vertices:
            first.append((vertice[0] + 25 * x_hat, vertice[1] + 25 * y_hat))
            second.append((vertice[0] + 75 * x_hat, vertice[1] + 75 * y_hat))
            third.append((vertice[0] + 125 * x_hat, vertice[1] + 125 * y_hat))

        pygame.draw.polygon(surface, (50, 50, 50), first)
        pygame.draw.polygon(surface, (100, 100, 100), second)
        pygame.draw.polygon(surface, (150, 150, 150), third)

        pygame.display.update()

    def explode(self, surface):

        frames = 6
        # Run a loop for this!
        for i in range(frames):
            surface.fill('black')

            for j in range(frames // 2):
                pygame.draw.circle(surface, 'red', (self.x, self.y), self.radius + 10 * i)
                pygame.draw.circle(surface, 'black', (self.x, self.y), self.radius + 10 * (i - 1) + 3)

            pygame.draw.circle(surface, 'white', (self.x + i * 35 + 10, self.y), 2)
            pygame.draw.circle(surface, 'white', (self.x - i * 35 - 10, self.y), 2)
            pygame.draw.circle(surface, 'white', (self.x, self.y + i * 35 + 10), 2)
            pygame.draw.circle(surface, 'white', (self.x, self.y - i * 35 - 10), 2)

            pygame.display.update()
            pygame.time.wait(250)

@dataclass
class Laser:

    x: int # Pixels
    y: int # Pixels
    angle: float # Radians
    velocity: float # Pixels/frame
    color: tuple[int, int, int]
    size: int = 10 # Static but leaving as something that I can easily adjust -- length of long side of rectangle

    def draw(self, surface):

        # Find the endpoints of the laser line using its angle and size
        cosine = self.size * math.cos(-self.angle)
        sine = self.size * math.sin(-self.angle)

        # Define points
        right_vertice = (self.x + cosine, self.y - sine)
        left_vertice = (self.x - cosine, self.y + sine)

        pygame.draw.line(surface, 'white', right_vertice, left_vertice, 1)

    def move(self, screen_size: tuple[int, int]):
        self.x += self.velocity * math.cos(self.angle)
        self.y += self.velocity * math.sin(self.angle)

    def should_destroy(self, force_field, screen_size: tuple[int, int]) -> bool:

        if self.x >= screen_size[0] + 50:
            return True
        elif self.x <= -50:
            return True
        if self.y >= screen_size[1] + 50:
            return True
        elif self.y <= -50:
            return True

        return False

    def collide(self, hitbox: 'pygame.Rect') -> bool:

        cosine = self.size * math.cos(-self.angle)
        sine = self.size * math.sin(-self.angle)

        # Our defined pivot points for each triangle
        right_vertice = (self.x + cosine, self.y - sine)
        left_vertice = (self.x - cosine, self.y + sine)

        if hitbox.collidepoint(right_vertice) or hitbox.collidepoint(left_vertice):
            return True

        return False

@dataclass
class Bouncer:

    x: int # Pixels
    y: int # Pixels
    angle: float # Radians
    velocity: float # Pixels/frame
    color: tuple[int, int, int]
    bounce_count: int = random.randint(1, 5)
    size: int = 10 # Static but leaving as something that I can easily adjust -- length of long side of rectangle

    def draw(self, surface):

        # Find the endpoints of the laser line using its angle and size
        cosine = self.size * math.cos(-self.angle)
        sine = self.size * math.sin(-self.angle)

        # Define points
        right_vertice = (self.x + cosine, self.y - sine)
        left_vertice = (self.x - cosine, self.y + sine)

        pygame.draw.line(surface, self.color, right_vertice, left_vertice, 1)

    def bounce(self, angle):
        self.angle += angle

    def move(self, screen_size: tuple[int, int]):

        self.x += self.velocity * math.cos(self.angle)
        self.y += self.velocity * math.sin(self.angle)

        if self.x >= screen_size[0]:
            self.bounce(math.pi/2)
        elif self.x <= 0:
            self.bounce(math.pi/2)
        elif self.y >= screen_size[1]:
            self.bounce(math.pi/2)
        elif self.y <= 0:
            self.bounce(math.pi/2)

    def should_destroy(self, force_field, screen_size: tuple[int, int]) -> bool:

        if self.x >= screen_size[0] + 50:
            return True
        elif self.x <= -50:
            return True
        if self.y >= screen_size[1] + 50:
            return True
        elif self.y <= -50:
            return True

        return False

    def collide(self, hitbox: 'pygame.Rect') -> bool:

        cosine = self.size * math.cos(-self.angle)
        sine = self.size * math.sin(-self.angle)

        # Our defined pivot points for each triangle
        right_vertice = (self.x + cosine, self.y - sine)
        left_vertice = (self.x - cosine, self.y + sine)

        if hitbox.collidepoint(right_vertice) or hitbox.collidepoint(left_vertice):
            return True

        return False

@dataclass
class Bomber:

    x: int # Pixels
    y: int # Pixels
    angle: float # Radians
    velocity: float # Pixels/frame
    color: tuple[int, int, int]
    clock: 'pygame.Clock'
    timer: int
    time: int = 0
    size: int = 10 # Static but leaving as something that I can easily adjust -- length of long side of rectangle
    ready: bool = False
    exploded: bool = False

    def draw(self, surface):

        # Find the endpoints of the laser line using its angle and size
        cosine = self.size * math.cos(-self.angle)
        sine = self.size * math.sin(-self.angle)

        # Define points
        right_vertice = (self.x + cosine, self.y - sine)
        left_vertice = (self.x - cosine, self.y + sine)

        pygame.draw.line(surface, self.color, right_vertice, left_vertice, 1)

    def update(self):

        if self.color[1] > 60:
            # Update color of bomb
            self.color = (self.color[0], self.color[1] - 60, self.color[2] - 60)
        else:
            self.color = (255, 0, 0)
            self.ready = True

    def move(self, screen_size: tuple[int, int]):

        self.x += self.velocity * math.cos(self.angle)
        self.y += self.velocity * math.sin(self.angle)

    def should_destroy(self, force_field, screen_size: tuple[int, int]) -> bool:

        if self.x >= screen_size[0] + 50:
            return True
        elif self.x <= -50:
            return True
        if self.y >= screen_size[1] + 50:
            return True
        elif self.y <= -50:
            return True

        if self.exploded:
            return True

        return False

    def collide(self, hitbox: 'pygame.Rect') -> bool:

        cosine = self.size * math.cos(-self.angle)
        sine = self.size * math.sin(-self.angle)

        # Our defined pivot points for each triangle
        right_vertice = (self.x + cosine, self.y - sine)
        left_vertice = (self.x - cosine, self.y + sine)

        if hitbox.collidepoint(right_vertice) or hitbox.collidepoint(left_vertice):
            return True

        return False

    def explode(self, bomb: 'pygame.Rect', hitbox: 'pygame.Rect') -> bool:

        if hitbox.colliderect(bomb):
            return True

        return False

    # Animation methods!
    def explosion(self, surface) -> 'pygame.Rect':
        bomb = pygame.draw.circle(surface, 'red', (self.x, self.y), 75)

        return bomb

# Ship functions
def check_dash_cooldown(time: float, on_cooldown: bool, clock: 'pygame.Clock') -> tuple[float, bool]:

    # Keeps track of dash cooldown
    return_cooldown = False
    if on_cooldown:
        time += clock.tick()

        if time > 5000:
            time = 0
            return_cooldown = False
        else:
            return_cooldown = True

    return time, return_cooldown

# Laser functions
def generate_lasers(num: int, scalar: float, weights: list[float], screen_size: tuple[int, int]) -> list:

    # Googled: 'python random float'
    lasers_side = random.choices(range(4), k = num)

    lasers = []
    for i in range(num):
        side = lasers_side[i]
        roll = random.random() # Float 0 to 1

        x, y, angle = 0, 0, 0
        velocity = random.randint(5, 15)
        if side == 0:
            x = 0
            y = random.randint(0, screen_size[1])
            angle = random.uniform(-math.pi/2, math.pi/2)
        elif side == 1:
            x = random.randint(0, screen_size[0])
            y = 0
            angle = -random.uniform(-math.pi, 0)
        elif side == 2:
            x = screen_size[0]
            y = random.randint(0, screen_size[1])
            angle = random.uniform(math.pi / 2, 3 * math.pi / 2)
        elif side == 3:
            x = random.randint(0, screen_size[0])
            y = screen_size[1]
            angle = -random.uniform(0, math.pi)

        # Decide what type of laser -- list of specific indices, improve later?
        if roll <= weights[0]:
            laser = Laser(x, y, angle, velocity * scalar, (255, 255, 255))
        elif roll <= weights[1]:
            laser = Bouncer(x, y, angle, velocity * scalar, (255, 0, 255))
        elif roll <= weights[2]:
            laser = Bomber(x, y, angle, velocity * scalar, (255, 255, 255), pygame.Clock(), random.randint(400, 1600))
        else:
            laser = Laser(x, y, angle, velocity * scalar, (255, 255, 255))

        lasers.append(laser)

    return lasers

def generate_burst(ship_point: tuple[int, int], laser_point: tuple[int, int]) -> list['Laser']:

    ihat, jhat = compute_normals(laser_point, ship_point)


def laser_weights(difficulty: int) -> list[float]:

    # Produce weights for laser generation chance based on difficulty
    basic, bounce, bomb, burst = 1, 0, 0, 0
    if difficulty > 10:
        basic = 0.25
        bounce = 0.50
        bomb = 0.75
        burst = 1
    else:
        basic = 1 - 0.15 * difficulty
        bounce = basic + 0.05 * difficulty
        bomb = bounce + 0.075 * difficulty
        burst = burst + 0.025 * difficulty

    return [basic, bounce, bomb, burst]

def create_lasers(num: int, index: int, scalar: float, screen_size: tuple[int, int]) -> list:

    # Debug function to create desired laser
    # Googled: 'python random float'
    lasers_side = random.choices(range(4), k=num)

    lasers = []
    for i in range(num):
        side = lasers_side[i]

        x, y, angle = 0, 0, 0
        velocity = random.randint(5, 15)
        if side == 0:
            x = 0
            y = random.randint(0, screen_size[1])
            angle = random.uniform(-math.pi / 2, math.pi / 2)
        elif side == 1:
            x = random.randint(0, screen_size[0])
            y = 0
            angle = -random.uniform(-math.pi, 0)
        elif side == 2:
            x = screen_size[0]
            y = random.randint(0, screen_size[1])
            angle = random.uniform(math.pi / 2, 3 * math.pi / 2)
        elif side == 3:
            x = random.randint(0, screen_size[0])
            y = screen_size[1]
            angle = -random.uniform(0, math.pi)

        if index == 0:
            laser = Laser(x, y, angle, velocity * scalar, (255, 255, 255))
            lasers.append(laser)
        elif index == 1:
            laser = Bouncer(x, y, angle, velocity * scalar, (255, 0, 255))
            lasers.append(laser)
        elif index == 2:
            laser = Bomber(x, y, angle, velocity * scalar, (255, 255, 255), pygame.Clock(), random.randint(500, 1500))
            lasers.append(laser)
        elif index == 3:
            x = 1 # to do
        else:
            laser = Laser(x, y, angle, velocity * scalar, (255, 255, 255))
            lasers.append(laser)

    return lasers

# Mathematical functions
def sign(value: int | float) -> int:

    # Return -1 if negative, 1 if positive
    if value < 0:
        return -1

    return 1

def compute_normals(start_point: tuple[int, int], end_point: tuple[int, int]) -> tuple[float, float]:

    # Returns a tuple of î and ĵ normal vectors that point towards the endpoint from startpoint
    x = end_point[0] - start_point[0]
    y = end_point[1] - start_point[1]

    return x, y

def compute_angle(vector: tuple[float, float]) -> float:

    # Googled: "python.math inverse tangent"
    # Takes a vector and computes the angle between the vector and the axis (within the triangle),
    # so we need to adjust our output depending on direction
    ihat, jhat = vector # Unpack vector
    angle = math.atan(jhat/ihat) # tan^-1(y/x), radians

    # Find offset
    offset = 0
    if sign(ihat) == 1 and sign(jhat) == 1:
        offset = -math.pi/2
    elif sign(ihat) == -1 and sign(jhat) == 1:
        offset = math.pi/2
    elif sign(ihat) == -1 and sign(jhat) == -1:
        offset = -1

    angle += offset

    return angle

# Draw functions
def set_text(string, coord_x, coord_y, font_size): # Function to set text

    # Taken from notes from class, the early pygame stuff (rewritten so I understand it a little better)
    font = pygame.font.Font('freesansbold.ttf', font_size)
    text = font.render(string, True, (0,0,0))
    text_rect = text.get_rect()
    text_rect.center = (coord_x, coord_y)

    return text, text_rect

def draw_all(surface, ship: 'Ship', lasers: list, clocks: tuple['pygame.Clock', 'pygame.Clock'],
             prolong_render: list['Bomber']):

    surface.fill('black')
    resolution = surface.get_size()

    # Handle ship processes -- Return the Rect that the draw command creates and feed it in as hitbox
    if ship.alive:

        hitbox = ship.draw(surface, lasers)
        ship.move(resolution)

        # Keep track of dash cooldown
        ship.dash_timer, ship.used_dash = check_dash_cooldown(ship.dash_timer, ship.used_dash, clocks[0])

        for laser in lasers:
            laser.draw(surface)
            laser.move(resolution)

            if laser.collide(hitbox):

                ship.alive = False
                ship.explode(surface)

            if type(laser) is Bomber:

                if laser.time > laser.timer:
                    laser.time = 0

                    laser.update()

                elif laser.ready:
                    explode = random.random()

                    if explode > 0.95:
                        bomb = laser.explosion(surface)

                        if laser.explode(bomb, hitbox):
                            ship.alive = False
                            ship.explode(surface)

                        laser.time = 0
                        laser.exploded = True

                else:
                    laser.time += laser.clock.tick()

    for bomber in prolong_render:
        bomber.explosion(surface)

    pygame.display.update()

# Googled: "python how to denote a function has two return values of different types" to make code cleaner
def initialize_pygame(resolution: tuple[int, int]) -> tuple['pygame.Surface', 'pygame.Clock']:

    pygame.init()
    surface = pygame.display.set_mode(resolution)
    surface.fill(pygame.Color(0, 0, 0))

    # Clock to help handle gameplay, especially with getting more difficult over time.
    # All code was built from documentation at https://www.pygame.org/docs/ref/time.html
    clock = pygame.time.Clock()

    return surface, clock

def main():

    resolution: tuple[int, int] = (1280, 800)
    surface, clock = initialize_pygame(resolution)

    # Initialize game parameters
    lasers = []
    weights = [1, 0, 0, 0] # Debug initialization
    ship = Ship(10, int(resolution[0] * 0.5), int(resolution[1] * 0.5), 0, 0)
    difficulty, time, timer = 1, 0, 500 # Timing and difficulty to make get harder over time
    score = 0 # Initialize score
    prolong_render = [] # For prolong_explosion()

    # Initialize cooldown timers and clocks
    clocks = (pygame.Clock(), pygame.Clock())

    # Scaling factor; I want fast, instant inputs with no delay. This means that having some delay (say 50 ms) to
    # every frame is really not conducive to gameplay. So I add a scalar that affects ALL velocities so to slow the game
    # down. Arbitrarily chosen and tuned
    speed_factor: float = 0.075

    running = True
    while running:
        draw_all(surface, ship, lasers, clocks, prolong_render)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:

                point = pygame.mouse.get_pos()
                x, y = random.randint(0, 1280), 800
                normals = compute_normals((x, y), point)
                laser = Laser(x, y, compute_angle(normals), 20 * speed_factor, (255, 255, 255))
                lasers.append(laser)
            elif event.type == KEYDOWN:

                # Debug keys!
                if event.key == K_t:
                    new_lasers = create_lasers(5, 0, speed_factor, surface.get_size())
                    for new_laser in new_lasers:
                        lasers.append(new_laser)
                elif event.key == K_y:
                    new_lasers = create_lasers(50, 0, speed_factor, surface.get_size())
                    for new_laser in new_lasers:
                        lasers.append(new_laser)
                elif event.key == K_r:
                    new_lasers = create_lasers(5, 1, speed_factor, surface.get_size())
                    for new_laser in new_lasers:
                        lasers.append(new_laser)
                elif event.key == K_u:
                    new_lasers = create_lasers(5, 2, speed_factor, surface.get_size())
                    for new_laser in new_lasers:
                        lasers.append(new_laser)

                # Game keys!
                elif event.key == K_SPACE:
                    ship.dash(surface)


        keys = pygame.key.get_pressed()
        if keys[K_a]:
            ship.rotate(-0.05 * math.pi * speed_factor)
        if keys[K_d]:
            ship.rotate(0.05 * math.pi * speed_factor)
        if keys[K_w]:
            ship.accelerate(0.1, speed_factor)
        if keys[K_s]:
            ship.accelerate(-0.1, speed_factor)

        # Remove distant, out of sight lasers
        remove_lasers = []
        for laser in lasers:
            destroy = laser.should_destroy(1, surface.get_size())
            if destroy:
                remove_lasers.append(laser)

        for laser in remove_lasers:
            lasers.remove(laser)

            # Increase score for every survived laser, more for different types
            # Googled: python how to check type of object
            if type(laser) is Laser:
                score += 1
            elif type(laser) is Bouncer:
                score += 5
            elif type(laser) is Bomber:
                score += 3

                if laser.exploded:
                    prolong_render.append(laser)

        # Prolong explosion render
        remove_render = []
        for bomber in prolong_render:
            if bomber.time > 400:
                remove_render.append(bomber)

            else:
                bomber.time += bomber.clock.tick()

        for bomber in remove_render:
            prolong_render.remove(bomber)


        # Create lasers
        if time > timer:
            time = 0

            # Rate at which lasers are created is based on the difficulty value
            timer = 600 / difficulty * 2
            weights = laser_weights(difficulty)

            new_lasers = generate_lasers(1, speed_factor, weights, surface.get_size())
            for new_laser in new_lasers:
                lasers.append(new_laser)


        # As time goes on, game gets harder
        time_lived = pygame.time.get_ticks()
        difficulty = time_lived // 8000 + 1 # Game gets harder every 10 seconds

        # Limit framerate to 250 fps
        pygame.time.delay(4)
        time += clock.tick() # Tick the clock so it slowly adds up to 3000 ms and then resets in the if statement above

    print(score)
    pygame.quit()

main()