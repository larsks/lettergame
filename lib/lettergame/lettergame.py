#!/usr/bin/python

import os, sys, optparse, time, random
import pygame
import observer

import sprites
from spritequeue import SpriteQueue
from gamewidget import GameWidget

DEFAULT_MAX_SPRITES   = 10
DEFAULT_TICK          = 60

soundDirectory = os.path.join(os.path.dirname(__file__), 'sounds')
imageDirectory = os.path.join(os.path.dirname(__file__), 'images')

class RippleFactory (GameWidget):
  '''Creates a new Ripple sprite when notified.'''

  category = 'ripple'

  def notify(self, event):
    self.play()
    self.game.addDynamicSprite(sprites.Ripple(event.pos))

class LetterPosition (GameWidget):
  '''Resets origin of letters when notified.'''

  def notify(self, event):
    self.game.recenter(event.pos)

class LetterFactory (GameWidget):
  '''Creates a new Letter sprite when notified.'''

  category = 'letter'

  def notify(self, event):
    if not event.unicode.isalnum() or not event.mod == 0: return

    self.play()
    self.game.addDynamicSprite(sprites.Letter(self.game.letterOrigin,
        event.unicode.upper()))

class HotKeyDispatcher (GameWidget):
  '''Notified on KEYDOWN events.  Dispatches appropriate function
  based on key press.'''

  def notify(self, event):
    res = False

    if event.mod & (pygame.KMOD_ALT | pygame.KMOD_LALT | pygame.KMOD_RALT):
      if event.key == pygame.K_f:
        self.game.toggleFullScreen()
        res = True
      elif event.key == pygame.K_q:
        self.game.quit = True
        res = True
      elif event.key == pygame.K_r:
        self.game.recenter()
        res = True
    elif event.key == pygame.K_SPACE:
      self.game.clearDynamicSprites()

    return res

class LetterGame (object):

  soundDirectory = soundDirectory
  imageDirectory = imageDirectory

  def __init__ (self, size = (0, 0),
      fullscreen = False,
      maxSprites = None,
      tick = None):

    self.size = size
    self.tick = tick or DEFAULT_TICK
    self.quit = False
    self.flags = 0
    self.sprites = {}

    self.layers = {
        'dynamic' : SpriteQueue(maxSprites or DEFAULT_MAX_SPRITES),
        'fixed'   : pygame.sprite.OrderedUpdates()
    }
    self.layering = [ 'dynamic', 'fixed' ]

    self.events = {
      pygame.MOUSEBUTTONDOWN  : observer.Subject(),
      pygame.KEYDOWN          : observer.Subject(),
      pygame.MOUSEMOTION      : observer.Subject(),
    }

    self.clock = pygame.time.Clock()

    if fullscreen:
      self.flags = pygame.FULLSCREEN

  def run(self):
    '''Initialize pygame and run the game.'''

    pygame.init()
    pygame.mouse.set_visible(False)

    self.initScreen()
    self.loadSprites()
    self.setupEventHandlers()

    self.recenter()
    self.loop()

  def initScreen(self):
    '''Initialize display environment.'''

    self.screen = pygame.display.set_mode(self.size, self.flags)
    self.background = pygame.Surface(self.screen.get_size()).convert()
    self.background.fill((0, 0, 0))

  def setupEventHandlers(self):
    '''Attach sprites and widgets to event notification machinery.'''

    self.events[pygame.MOUSEBUTTONDOWN].attach(RippleFactory(self))
    self.events[pygame.MOUSEBUTTONDOWN].attach(LetterPosition(self))
    self.events[pygame.KEYDOWN].attach(HotKeyDispatcher(self))
    self.events[pygame.KEYDOWN].attach(LetterFactory(self))

  def recenter(self, center = None):
    if center is None:
      center = self.screen.get_rect().center

    self.letterOrigin = center

  def loadSprites(self):
    '''Load our fixed sprites.  These stay around for the duration of
    the game.'''

    cat = sprites.Cat(self, self.screen.get_rect(), colorkey=(0,255,0))
    self.addFixedSprite(cat, events = [pygame.MOUSEBUTTONDOWN])

    arrow = sprites.Arrow(self, colorkey=(0,255,0))
    self.addFixedSprite(arrow, events = [pygame.MOUSEMOTION])

  def loop(self):
    '''This is the main application event loop.'''

    while 1:
      self.clock.tick(self.tick)

      for event in pygame.event.get():
        self.handleEvent(event)

      if self.quit:
        break

      self.screen.blit(self.background, (0,0))

      for layer in self.layering:
#        self.layers[layer].clear(self.screen, self.background)
        self.layers[layer].update()
        self.layers[layer].draw(self.screen)

      pygame.display.update()

  def handleEvent(self, event):
    '''Notify event listeners.'''

    if event.type == pygame.QUIT:
      sys.exit()

    if self.events.has_key(event.type):
      self.events[event.type].notify_listeners(event)

  def toggleFullScreen(self):
    '''Turn full screen mode on and off.'''

    if self.flags & pygame.FULLSCREEN:
      self.flags = self.flags & ~pygame.FULLSCREEN
    else:
      self.flags = self.flags | pygame.FULLSCREEN

    self.screen = pygame.display.set_mode(self.size, self.flags)

  def addDynamicSprite(self, sprite, events = []):
    '''Added a "dynamic" sprite -- e.g., a sprite with a limited lifetime.
    The number of dynamic sprites active at any point in time is limited
    by self.maxSprites.  Attach sprite to the notification 
    machinery for event types listed in `events`.'''

    self.layers['dynamic'].add(sprite)

    for event in events:
      if not self.events.has_key(event):
        self.events[event] = Subject()

      self.events[event].attach(sprite)

  def addFixedSprite(self, sprite, events = []):
    '''Added a "fixed" sprite -- e.g., a sprite that will stay around
    for the duration of the game.  Attach it to the notification 
    machinery for event types listed in `events`.'''

    self.layers['fixed'].add(sprite)

    for event in events:
      if not self.events.has_key(event):
        self.events[event] = Subject()

      self.events[event].attach(sprite)

  def clearDynamicSprites(self):
    '''Remove all active "dynamic" sprites.'''

    self.layers['dynamic'].empty()

