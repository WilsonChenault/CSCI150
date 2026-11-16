import pygame
from pygame.locals import *
from dataclasses import dataclass
import math


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

    def draw(self, surface):

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
        pygame.draw.polygon(surface, self.color, vertices)

    def rotate(self, angle):
        self.angle += angle

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
    size: int = 20 # Static but leaving as something that I can easily adjust -- length of long side of rectangle

    def draw(self, surface):

        # Because I want to draw rectangles at an angle, I can't use draw.rect -- need to draw as two triangles
        # to make collision detection easier later
        # I am also going to create a "draw" location -- I prefer to keep (x, y) as its center, but for drawing it's
        # way easier to do one of the corners, also! while here do cos(x) and sin(x) to make more efficient (barely)

        length, width = self.size, self.size * 0.25
        cosine = math.cos(self.angle)
        sine = math.sin(self.angle)

        # Our defined pivot points for each triangle
        top_left = (self.x - 0.5 * width, self.y - 0.5 * length)
        bottom_right = (self.x + 0.5 * width, self.y + 0.5 * length)

        top_vertice = (self.size * math.cos(self.angle) + self.x,
                         self.size * math.sin(self.angle) + self.y)
        left_vertice = (self.size * math.cos(self.angle + 2 / 3 * math.pi) + self.x,
                        1.5 * self.size * math.sin(self.angle + 2 / 3 * math.pi) + self.y)
        right_vertice = (self.size * math.cos(self.angle - 2 / 3 * math.pi) + self.x,
                         self.size * math.sin(self.angle - 2 / 3 * math.pi) + self.y)
        bottom_vertice = (self.size * math.cos(self.angle) - self.x,
                          self.size * math.sin(self.angle) - self.y)


        # Defining triangles
        vertices_right = [
            top_vertice, left_vertice, right_vertice
        ]

        vertices_left = [
            bottom_vertice, left_vertice, right_vertice
        ]

        pygame.draw.polygon(surface, (0, 255, 0), vertices_right)
        pygame.draw.polygon(surface, (255, 0, 0), vertices_left)

    def rotate(self, angle):
        self.angle += angle

    def move(self, screen_size):
        self.x += self.velocity * math.cos(self.angle)
        self.y += self.velocity * math.sin(self.angle)







def draw_all(surface, objects: list):
    surface.fill('black')

    for item in objects:
        item.draw(surface)
        item.move(surface.get_size())

    pygame.display.update()


def main():
    pygame.init()
    surface = pygame.display.set_mode((640, 400))
    surface.fill(pygame.Color(0, 0, 0))

    ship = Ship(10, 320, 200, 0, 0)
    laser = Laser(400, 300, 0, 0, (255, 255, 255))
    objects = [ship, laser]

    running = True
    while running:
        draw_all(surface, objects)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_a:
                    ship.rotate(-0.1 * math.pi)
                elif event.key == K_d:
                    ship.rotate(0.1 * math.pi)
                elif event.key == K_w:
                    ship.velocity += 1
                elif event.key == K_s:
                    ship.velocity -= 1
                elif event.key == K_i:
                    laser.velocity += 1
                elif event.key == K_k:
                    laser.velocity -= 1
                elif event.key == K_j:
                    laser.rotate(-0.1 * math.pi)
                elif event.key == K_l:
                    laser.rotate(0.1 * math.pi)

        pygame.time.delay(50)
    pygame.quit()


main()