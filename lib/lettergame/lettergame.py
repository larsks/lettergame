#!/usr/bin/python

import os, sys, optparse, time, random
import pygame
import observer
from spritequeue import SpriteQueue
from bouncer import Bouncer
from cursor import Cursor

DEFAULT_MAX_SPRITES   = 10
DEFAULT_TICK          = 60

DYNAMIC_LAYER         = 0
FIXED_LAYER           = 1

soundDirectory = os.path.join(os.path.dirname(__file__), 'sounds')
imageDirectory = os.path.join(os.path.dirname(__file__), 'images')

def randomColor():
  '''Returns a random (r,g,b) tuple.'''

  return (random.randint(0,255),
      random.randint(0,255),
      random.randint(0,255))

class Cat(Bouncer):
  '''An image that bounces around the screen.'''

  def __init__ (self, path, container, colorkey = None, holdTime = 5):
    image = pygame.image.load(path).convert()
    if colorkey:
      image.set_colorkey(colorkey)

    super(Cat, self).__init__(image, container)

    self.clicked = False
    self.holdTime = holdTime
    self.sounds = []

    meowDir = os.path.join(soundDirectory, 'meow')
    if os.path.isdir(meowDir):
      for soundFile in [x for x in os.listdir(meowDir)
          if x.endswith('.wav')]:
        path = os.path.join(meowDir, soundFile)
        self.sounds.append(pygame.mixer.Sound(path))

  def update(self):
    if self.clicked:
      # We've been clicked; wait for self.holdTime seconds.
      if time.time() > self.startHold + self.holdTime:
        self.clicked = False
    else:
      super(Cat, self).update()

  def notify(self, event):
    '''Someone clicked on us!  Stop moving for a while.'''

    if not self.clicked:
      random.choice(self.sounds).play()
      self.clicked = True
      self.startHold = time.time()
      return True

class Arrow(Cursor):

  def __init__ (self, path, colorkey = None):
    image = pygame.image.load(path).convert()
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

class GameWidget (object):

  category = None

  def __init__ (self, game):
    self.game = game
    self.sounds = []

    if self.category is not None:
      self.loadSounds()

  def loadSounds(self):
    mySoundDir = os.path.join(soundDirectory, self.category)
    if os.path.isdir(mySoundDir):
      for soundFile in [os.path.join(mySoundDir, x)
          for x in os.listdir(mySoundDir)
          if x.endswith('.wav')]:
        self.sounds.append(pygame.mixer.Sound(soundFile))

  def play(self):
    if self.sounds:
      random.choice(self.sounds).play()

class RippleFactory (GameWidget):

  category = 'ripple'

  def notify(self, event):
    self.play()
    self.game.layers[DYNAMIC_LAYER].add(Ripple(event.pos))

class LetterPosition (GameWidget):

  def notify(self, event):
    self.game.letterOrigin = event.pos

class LetterFactory (GameWidget):

  category = 'letter'

  def notify(self, event):
    self.play()
    self.game.layers[DYNAMIC_LAYER].add(Letter(self.game.letterOrigin,
        event.unicode.upper()))

class HotKeyDispatcher (GameWidget):

  def notify(self, event):
    res = False

    if event.mod == 256:
      if event.key == 102:
        self.game.toggleFullScreen()
        res = True
    elif event.key == 27:
      self.game.quit = True
      res = True

    return res

class LetterGame (object):

  def __init__ (self, size = (0, 0),
      fullscreen = False,
      maxSprites = None,
      tick = None):

    self.size = size
    self.tick = tick or DEFAULT_TICK
    print 'TICK:', self.tick
    self.quit = False
    self.flags = 0
    self.sprites = {}

    self.layers = [
        SpriteQueue(maxSprites or DEFAULT_MAX_SPRITES),
        pygame.sprite.OrderedUpdates()
    ]

    self.events = {
      pygame.MOUSEBUTTONDOWN  : observer.Subject(),
      pygame.KEYDOWN          : observer.Subject(),
      pygame.MOUSEMOTION      : observer.Subject(),
    }

    self.clock = pygame.time.Clock()

    if fullscreen:
      self.flags = pygame.FULLSCREEN

  def run(self):
    pygame.init()
    pygame.mouse.set_visible(False)

    self.screen = pygame.display.set_mode(self.size, self.flags)

    self.loadSprites()

    self.events[pygame.MOUSEBUTTONDOWN].attach(RippleFactory(self))
    self.events[pygame.MOUSEBUTTONDOWN].attach(LetterPosition(self))
    self.events[pygame.KEYDOWN].attach(HotKeyDispatcher(self))
    self.events[pygame.KEYDOWN].attach(LetterFactory(self),
        lambda self, event: event.unicode.isalnum() and event.mod == 0)

    # Letters start in the center of the screen (but this can be
    # changed by mouse clicks).
    self.letterOrigin = self.screen.get_rect().center

    self.background = pygame.Surface(self.screen.get_size()).convert()
    self.background.fill((0, 0, 0))

    self.loop()

  def loadSprites(self):
    cat = Cat(os.path.join(imageDirectory, 'cat-small.png'),
      self.screen.get_rect(),
      colorkey=(0,255,0))
    self.layers[FIXED_LAYER].add(cat)
    self.events[pygame.MOUSEBUTTONDOWN].attach(cat,
        lambda self, event: self.rect.collidepoint(event.pos))

    arrow = Arrow(os.path.join(imageDirectory, 'arrow.png'),
        colorkey=(0,255,0))
    self.layers[FIXED_LAYER].add(arrow)
    self.events[pygame.MOUSEMOTION].attach(arrow)

  def loop(self):
    spritelayer = pygame.Surface(self.screen.get_size()).convert()

    while 1:
      self.clock.tick(self.tick)

      for event in pygame.event.get():
        self.handleEvent(event)

      if self.quit:
        break

      spritelayer.fill((0,0,0))

      for layer in self.layers:
        layer.update()
        layer.draw(spritelayer)

      self.screen.blit(spritelayer, (0,0))
      pygame.display.flip()

  def handleEvent(self, event):
    if self.events.has_key(event.type):
      self.events[event.type].notify_listeners(event)

    if event.type == pygame.QUIT:
      sys.exit()

  def toggleFullScreen(self):
    if self.flags & pygame.FULLSCREEN:
      self.flags = self.flags & ~pygame.FULLSCREEN
    else:
      self.flags = self.flags | pygame.FULLSCREEN

    self.screen = pygame.display.set_mode(self.size, self.flags)


