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

    def accelerate(self, speed: int, speed_factor: float):
        self.velocity += speed * speed_factor

        if self.velocity > 5 * speed_factor:
            self.velocity = 5 * speed_factor
        if self.velocity < -5 * speed_factor:
            self.velocity = -5 * speed_factor

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

    def rotate(self, angle):
        self.angle += angle

    def move(self, screen_size):
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



def draw_all(surface, ship: 'Ship', lasers: list['Laser']):

    surface.fill('black')

    # Handle ship processes -- Return the Rect that the draw command creates and feed it in as hitbox
    if ship.alive:
        hitbox = ship.draw(surface, lasers)
        ship.move(surface.get_size())


        for laser in lasers:
            laser.draw(surface)
            laser.move(surface.get_size())

            if laser.collide(hitbox):
                ship.alive = False

    pygame.display.update()

def create_lasers(num: int, scalar: float, screen_size: tuple[int, int]) -> list['Laser']:

    # Googled: 'python random float'
    lasers_side = random.choices(range(4), k = num)

    lasers = []
    for i in range(num):
        side = lasers_side[i]

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

        laser = Laser(x, y, angle, velocity * scalar, (255, 255, 255))
        lasers.append(laser)

    return lasers

# def cubic_scaling(x: float) -> float:
#


def main():

    pygame.init()
    surface = pygame.display.set_mode((640, 400))
    surface.fill(pygame.Color(0, 0, 0))
    lasers = []
    ship = Ship(10, 320, 200, 0, 0)

    # Framerate
    clock = pygame.Clock

    # Scaling factor; I want fast, instant inputs with no delay. This means that having some delay (say 50 ms) to
    # every frame is really not conducive to gameplay. So I add a scalar that affects ALL velocities so to slow the game
    # down. Arbitrarily chosen and tuned
    speed_factor: float = 0.005

    running = True
    while running:
        draw_all(surface, ship, lasers)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:

                # if event.key == K_a:
                #     ship.rotate(-0.1 * math.pi)
                # elif event.key == K_d:
                #     ship.rotate(0.1 * math.pi)
                # elif event.key == K_w:
                #     ship.velocity += 1 * speed_factor
                # elif event.key == K_s:
                #     ship.velocity -= 1 * speed_factor
                if event.key == K_t:
                    new_lasers = create_lasers(5, speed_factor, surface.get_size())
                    for new_laser in new_lasers:
                        lasers.append(new_laser)
                elif event.key == K_y:
                    new_lasers = create_lasers(50, speed_factor, surface.get_size())
                    for new_laser in new_lasers:
                        lasers.append(new_laser)

        keys = pygame.key.get_pressed()
        if keys[K_a]:
            ship.rotate(-0.05 * math.pi * speed_factor)
        if keys[K_d]:
            ship.rotate(0.05 * math.pi * speed_factor)
        if keys[K_w]:
            ship.accelerate(1, speed_factor)
        if keys[K_s]:
            ship.accelerate(-1, speed_factor)



        # Remove distant, out of sight lasers
        remove_lasers = []
        for laser in lasers:
            destroy = laser.should_destroy(1, surface.get_size())
            if destroy:
                remove_lasers.append(laser)

        for laser in remove_lasers:
            lasers.remove(laser)

        # print(clock.get_fps())

    pygame.quit()


main()