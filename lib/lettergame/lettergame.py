#!/usr/bin/python

import os, sys, optparse, time, random
import pygame
from spritequeue import SpriteQueue

DEFAULT_MAX_SPRITES   = 10
DEFAULT_TICK          = 60

DYNAMIC_LAYER         = 0
FIXED_LAYER           = 1

def randomColor():
  '''Returns a random (r,g,b) tuple.'''

  return (random.randint(0,255),
      random.randint(0,255),
      random.randint(0,255))

def randomNotZeroSpeed():
  '''Returns a random number in the range -3 <= x <= 3, excluding 0.'''

  return random.choice(list(set(range(-3,4)) - set([0])))

class bouncingImage(pygame.sprite.Sprite):
  '''An image that bounces around the screen.'''

  def __init__ (self, imgPath, container, colorkey = None, holdTime = 5):
    '''Initialize a new bouncingImage instance.

    - imgPath -- path to an image file
    - container -- a Rect that defines the borders in which the image moves
    - colorKey -- set this to make a color transparent
    - holdTime -- how long to pause if we receive a click() event.
    '''

    super(bouncingImage, self).__init__()
    self.image = pygame.image.load(imgPath).convert()
    self.container = container
    self.speed = (randomNotZeroSpeed(), randomNotZeroSpeed())
    self.state = 0
    self.holdTime = holdTime

    if colorkey:
      self.image.set_colorkey(colorkey)
    self.rect = self.image.get_rect()

    self.rect.centerx = random.randint(self.rect.width,container.width - self.rect.width)
    self.rect.centery = random.randint(self.rect.height,container.height - self.rect.height)

  def update(self):
    '''Move image around the screen.  If we hit the side of the screen, reverse 
    direction.'''

    if self.state == 0:
      self.rect = self.rect.move(self.speed)

      if not self.container.contains(self.rect):
        # Found out where we hit the edge.
        tl = not self.container.collidepoint(self.rect.topleft)
        tr = not self.container.collidepoint(self.rect.topright)
        bl = not self.container.collidepoint(self.rect.bottomleft)
        br = not self.container.collidepoint(self.rect.bottomright)

        if (tl and tr) or (bl and br):
          self.speed = (self.speed[0], -self.speed[1])
        elif (tl and bl) or (tr and br):
          self.speed = (-self.speed[0], self.speed[1])
    elif self.state == 1:
      # We've been clicked; wait for self.holdTime seconds.
      if time.time() > self.startHold + self.holdTime:
        self.state = 0

  def clicked(self):
    '''Someone clicked on us!  Stop moving for a while.'''

    self.state = 1
    self.startHold = time.time()

class simpleRipple(pygame.sprite.Sprite):
  '''Circles that expand from a given point.'''

  def __init__ (self, center, initialSize = 10, maxSize = 500,
      step = 5, speed = 0, color = None):
    '''Initialize a new simpleRipple sprite.  The circle will grow
    `step` increments every `speed` ticks.  If `speed` is 0, pick a random 
    1 <= x <= 4.'''

    super(simpleRipple, self).__init__()

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

class animatedLetter(pygame.sprite.Sprite):
  '''Letters that grow.'''

  def __init__(self, origin, letter, fontName = None, 
      color = None,
      initialSize = 36, 
      maxSize = 1000,
      factor = 1.1, 
      holdTime = 1):
    super(animatedLetter, self).__init__()

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

class LetterGame (object):

  def __init__ (self, size = (0, 0),
      fullscreen = False,
      maxSprites = None,
      tick = None):

    self.size = size
    self.tick = tick and tick or DEFAULT_TICK
    self.quit = False
    self.flags = 0
    self.sounds = {}
    self.sprites = {}
    self.layers = [
        SpriteQueue(maxSprites and maxSprites or DEFAULT_MAX_SPRITES),
        pygame.sprite.Group()
        ]

    self.soundDirectory = os.path.join(os.path.dirname(__file__), 'sounds')
    self.imageDirectory = os.path.join(os.path.dirname(__file__), 'images')

    self.clock = pygame.time.Clock()

    if fullscreen:
      self.flags = pygame.FULLSCREEN

  def run(self):
    pygame.init()

    self.screen = pygame.display.set_mode(self.size, self.flags)

    self.loadSprites()
    self.loadSounds()

    # Letters start in the center of the screen (but this can be
    # changed by mouse clicks).
    self.letterOrigin = self.screen.get_rect().center

    self.background = pygame.Surface(self.screen.get_size()).convert()
    self.background.fill((0, 0, 0))

    self.loop()

  def loadSprites(self):
    self.sprites['cat'] = bouncingImage(os.path.join(
      self.imageDirectory, 'cat-small.png'), self.screen.get_rect(), colorkey=(0,255,0))
    self.layers[FIXED_LAYER].add(self.sprites['cat'])

  def loadSounds(self):
    if self.soundDirectory is None: return

    self.sounds = {}

    for which in ['keydown', 'mousedown', 'meow']:
      thisDir = os.path.join(self.soundDirectory, which)
      if not os.path.isdir(thisDir):
        continue

      soundFiles = [x for x in os.listdir(thisDir)
          if x.endswith('.wav')]

      for x in soundFiles:
        path = os.path.join(thisDir, x)
        sound = pygame.mixer.Sound(path)

        try:
          self.sounds[which].append(sound)
        except KeyError:
          self.sounds[which] = [sound]

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
    if event.type == pygame.QUIT:
      sys.exit()
    elif event.type == pygame.KEYDOWN:
      if event.key == 27:
        self.quit = True
      elif event.mod == 256 and event.key == 102:
        self.toggleFullScreen()
      elif event.unicode.isalnum():
        self.newLetter(event)
        self.playSound('keydown')
    elif event.type == pygame.MOUSEBUTTONDOWN:
      self.letterOrigin = event.pos

      if self.sprites['cat'].rect.collidepoint(event.pos):
        self.sprites['cat'].clicked()
        self.playSound('meow')
      else:
        self.newRipple(event)
        self.playSound('mousedown')

  def playSound(self, which):
    if not self.sounds.has_key(which) or not self.sounds[which]:
      return

    sound = random.choice(self.sounds[which])
    sound.play()

  def newLetter(self, event):
    letter = animatedLetter(self.letterOrigin, event.unicode.upper())
    self.layers[DYNAMIC_LAYER].add(letter)

  def newRipple(self, event):
    ripple = simpleRipple(event.pos)
    self.layers[DYNAMIC_LAYER].add(ripple)

  def toggleFullScreen(self):
    if self.flags & pygame.FULLSCREEN:
      self.flags = self.flags & ~pygame.FULLSCREEN
    else:
      self.flags = self.flags | pygame.FULLSCREEN

    self.screen = pygame.display.set_mode(self.size, self.flags)


