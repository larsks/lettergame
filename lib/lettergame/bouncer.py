import random
import pygame

def randomNotZero(min, max):
  '''Returns a random number in the range min <= x <= max, excluding 0.'''

  return random.choice(list(set(range(min,max+1)) - set([0])))

class Bouncer(pygame.sprite.Sprite):
  '''An image that bounces around the screen.'''

  def __init__ (self, image = None, container = None, *args, **kwargs):
    '''Initialize a new Bouncer instance.

    - image -- Pygame Image instance
    - container -- a Rect that defines the borders in which the image moves
    '''

    super(Bouncer, self).__init__(*args, **kwargs)
    self.image = image
    self.container = container
    self.speed = (randomNotZero(-3,3), randomNotZero(-3,3))

    self.rect = self.image.get_rect()

    self.rect.centerx = random.randint(self.rect.width,
        container.width - self.rect.width)
    self.rect.centery = random.randint(self.rect.height,
        container.height - self.rect.height)

  def update(self):
    '''Move image around the screen.  If we hit the side of the
    screen, reverse direction.'''

    self.rect = self.rect.move(self.speed)

    if not self.container.contains(self.rect):
      # Find out where we hit the edge.
      tl = not self.container.collidepoint(self.rect.topleft)
      tr = not self.container.collidepoint(self.rect.topright)
      bl = not self.container.collidepoint(self.rect.bottomleft)
      br = not self.container.collidepoint(self.rect.bottomright)

      if (tl and tr) or (bl and br):
        self.speed = (self.speed[0], -self.speed[1])

      if (tl and bl) or (tr and br):
        self.speed = (-self.speed[0], self.speed[1])

