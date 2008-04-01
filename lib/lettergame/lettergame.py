#!/usr/bin/python

import os, sys, optparse, time, random
import pygame

def randomColor():
  return (random.randint(0,255),
      random.randint(0,255),
      random.randint(0,255))

def randomNotZeroSpeed():
  return random.choice((-2,-1,1,2))

class bouncingImage(pygame.sprite.Sprite):

  def __init__ (self, imgPath, container, colorkey = None, holdTime = 5):
    super(bouncingImage, self).__init__()
    self.image = pygame.image.load(imgPath).convert()
    self.container = container
    self.speed = (randomNotZeroSpeed(), randomNotZeroSpeed())
    self.state = 0
    self.holdTime = holdTime

    if colorkey:
      self.image.set_colorkey(colorkey)
    self.rect = self.image.get_rect()

    self.rect.centerx = random.randint(self.rect.width,container.get_rect().width - self.rect.width)
    self.rect.centery = random.randint(self.rect.height,container.get_rect().height - self.rect.height)

  def update(self):
    if self.state == 0:
      self.rect = self.rect.move(self.speed)
      container = self.container.get_rect()
      if not container.contains(self.rect):
        tl = not container.collidepoint(self.rect.topleft)
        tr = not container.collidepoint(self.rect.topright)
        bl = not container.collidepoint(self.rect.bottomleft)
        br = not container.collidepoint(self.rect.bottomright)

        if (tl and tr) or (bl and br):
          self.speed = (self.speed[0], -self.speed[1])
        elif (tl and bl) or (tr and br):
          self.speed = (-self.speed[0], self.speed[1])
    elif self.state == 1:
      if time.time() > self.startHold + self.holdTime:
        self.state = 0

  def clicked(self):
    self.state = 1
    self.startHold = time.time()

class simpleRipple(pygame.sprite.Sprite):

  def __init__ (self, center,
      initialSize = 10,
      maxSize = 500,
      step = 5,
      speed = 0,
      color = None):
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

    self.rect.centerx = self.center[0]
    self.rect.centery = self.center[1]
    pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size, 8)

  def update(self):
    self.counter -= 1
    if self.counter: return
    self.counter = self.speed

    self.draw()

    self.size += self.step
    if self.size > self.maxSize:
      self.kill()

class animatedLetter(pygame.sprite.Sprite):

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
      self.rect.centerx = self.origin[0]
      self.rect.centery = self.origin[1]
  
  def update(self):
    if self.state == 0:
      self.size = int(self.size * self.factor)

      if self.size > self.maxSize:
        self.finalUpdate = time.time()
        self.state = 1

      self.draw()

    elif self.state == 1:
      if time.time() > self.finalUpdate + self.holdTime:
        self.kill()

class LetterGame (object):

  def __init__ (self, size = (0, 0),
      fullscreen = False,
      useHardware = False, 
      soundDirectory = None,
      imageDirectory = None,
      tick = 60):

    self.size = size
    self.tick = tick
    self.quit = False
    self.flags = 0
    self.isFullScreen = False
    self.sounds = {}

    if soundDirectory is not None:
      self.soundDirectory = soundDirectory
    else:
      self.soundDirectory = os.path.join(os.path.dirname(__file__), 'sounds')

    if imageDirectory is not None:
      self.imageDirectory = imageDirectory
    else:
      self.imageDirectory = os.path.join(os.path.dirname(__file__), 'images')

    if fullscreen:
      self.isFullScreen = True
      self.flags = pygame.FULLSCREEN

    if useHardware:
      self.isFullScreen = True
      self.flags = pygame.FULLSCREEN | pygame.HWSURFACE \
          | pygame.DOUBLEBUF

    pygame.init()
    self.loadSounds()

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

  def run(self):
    self.screen = pygame.display.set_mode(self.size, self.flags)
    self.letterOrigin = self.screen.get_rect().center

    self.cat = bouncingImage(os.path.join(self.imageDirectory, 'cat-small.png'),
        self.screen, colorkey=(0,255,0))
    self.sprites = pygame.sprite.Group(self.cat)
    self.clock = pygame.time.Clock()

    background = pygame.Surface(self.screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))

    self.background = background
    self.screen.blit(background, (0, 0))

    self.loop()

  def loop(self):
    background = self.background

    while 1:
      self.clock.tick(self.tick)

      for event in pygame.event.get():
        self.handleEvent(event)

      if self.quit:
        break

      background.fill((0, 0, 0))
      self.sprites.update()
      self.sprites.draw(background)
      self.screen.blit(background, (0,0))
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

      if self.cat.rect.collidepoint(event.pos):
        self.cat.clicked()
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
    self.sprites.add(animatedLetter(self.letterOrigin, event.unicode.upper()))

  def newRipple(self, event):
    self.sprites.add(simpleRipple(event.pos))

  def toggleFullScreen(self):
    if self.isFullScreen:
      self.screen = pygame.display.set_mode(self.size, self.flags & ~pygame.FULLSCREEN)
      self.isFullScreen = False
    else:
      self.screen = pygame.display.set_mode(self.size, self.flags | pygame.FULLSCREEN)
      self.isFullScreen = True

if __name__ == '__main__': main()
