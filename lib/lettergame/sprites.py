import os
import time
import random
import pygame

from bouncer import Bouncer
from cursor import Cursor
from gamewidget import GameWidget

def randomColor():
  '''Returns a random (r,g,b) tuple.'''

  return (random.randint(0,255),
      random.randint(0,255),
      random.randint(0,255))

class Cat(Bouncer, GameWidget):
  '''An image that bounces around the screen.'''

  category = 'meow'

  def __init__ (self, game, container, colorkey = None, holdTime = 5):
    image = pygame.image.load(os.path.join(game.imageDirectory,
      'cat.png')).convert()
    if colorkey:
      image.set_colorkey(colorkey)

    Bouncer.__init__(self, image, container)
    GameWidget.__init__(self, game)

    self.clicked = False
    self.holdTime = holdTime

  def update(self):
    if self.clicked:
      # We've been clicked; wait for self.holdTime seconds.
      if time.time() > self.startHold + self.holdTime:
        self.clicked = False
    else:
      super(Cat, self).update()

  def notify(self, event):
    '''Someone clicked on us!  Stop moving for a while.'''

    if not self.rect.collidepoint(event.pos): return

    self.play()

    if not self.clicked:
      self.clicked = True
      self.startHold = time.time()

    return True

class Arrow(Cursor):

  def __init__ (self, game, colorkey = None):
    image = pygame.image.load(os.path.join(game.imageDirectory,
      'arrow.png')).convert()
    if colorkey:
      image.set_colorkey(colorkey)

    super(Arrow, self).__init__(image)

class Ripple(pygame.sprite.Sprite):
  '''Circles that expand from a given point.'''

  def __init__ (self, center, initialSize = 10, maxSize = 500,
      step = 5, speed = 0, color = None):
    '''Initialize a new Ripple sprite.  The circle will grow
    `step` increments every `speed` ticks.  If `speed` is 0, pick a random 
    1 <= x <= 4.'''

    super(Ripple, self).__init__()

    if color is None:
      color = randomColor()

    self.center = center
    self.size = initialSize
    self.maxSize = maxSize
    self.color = color
    self.step = step
    self.speed = speed == 0 and random.randint(1,4) or speed
    self.counter = self.speed

    self.draw()

  def draw(self):
    self.image = pygame.Surface((self.size*2, self.size*2))
    self.image.set_colorkey((0,0,0))
    self.rect = self.image.get_rect()

    self.rect.center = self.center
    pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size, 8)

  def update(self):
    # Only update every self.speed ticks.
    self.counter -= 1
    if self.counter: return
    self.counter = self.speed

    self.draw()

    self.size += self.step
    if self.size > self.maxSize:
      self.kill()

class Letter(pygame.sprite.Sprite):
  '''Letters that grow.'''

  def __init__(self, origin, letter, fontName = None, 
      color = None,
      initialSize = 36, 
      maxSize = 1000,
      factor = 1.1, 
      holdTime = 1):
    super(Letter, self).__init__()

    if color is None:
      color = randomColor()

    self.origin = origin
    self.size = initialSize
    self.maxSize = maxSize
    self.letter = letter
    self.color = color
    self.fontName = fontName
    self.factor = factor
    self.state = 0
    self.holdTime = holdTime

  def draw(self):
      font = pygame.font.Font(self.fontName, self.size)
      self.image = font.render(self.letter, 1, self.color)
      self.rect = self.image.get_rect()
      self.rect.center = self.origin
  
  def update(self):
    if self.state == 0:
      self.size = int(self.size * self.factor)

      if self.size > self.maxSize:
        self.finalUpdate = time.time()
        self.state = 1

      self.draw()

    elif self.state == 1:
      # After reaching maximum size, pause on screen for self.holdTime
      # seconds before disappearing.
      if time.time() > self.finalUpdate + self.holdTime:
        self.kill()


