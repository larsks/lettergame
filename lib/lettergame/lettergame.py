#!/usr/bin/python

import os, sys, optparse, time, random
import pygame
import observer

from spritequeue import SpriteQueue
from gamewidget import GameWidget
from sprites import Cat, Arrow, Letter, Ripple

DEFAULT_MAX_SPRITES   = 10
DEFAULT_TICK          = 60

soundDirectory = os.path.join(os.path.dirname(__file__), 'sounds')
imageDirectory = os.path.join(os.path.dirname(__file__), 'images')

class RippleFactory (GameWidget):

  category = 'ripple'

  def notify(self, event):
    self.play()
    self.game.addDynamicSprite(Ripple(event.pos))

class LetterPosition (GameWidget):

  def notify(self, event):
    self.game.letterOrigin = event.pos

class LetterFactory (GameWidget):

  category = 'letter'

  def notify(self, event):
    self.play()
    self.game.addDynamicSprite(Letter(self.game.letterOrigin,
        event.unicode.upper()))

class HotKeyDispatcher (GameWidget):

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
    pygame.init()
    pygame.mouse.set_visible(False)

    self.screen = pygame.display.set_mode(self.size, self.flags)

    self.loadSprites()

    self.events[pygame.MOUSEBUTTONDOWN].attach(RippleFactory(self))
    self.events[pygame.MOUSEBUTTONDOWN].attach(LetterPosition(self))
    self.events[pygame.KEYDOWN].attach(HotKeyDispatcher(self))
    self.events[pygame.KEYDOWN].attach(LetterFactory(self),
        lambda self, event: event.unicode.isalnum() and event.mod == 0)

    self.background = pygame.Surface(self.screen.get_size()).convert()
    self.background.fill((0, 0, 0))
    self.spritelayer = pygame.Surface(self.screen.get_size()).convert()

    self.recenter()
    self.loop()

  def recenter(self):
    self.letterOrigin = self.screen.get_rect().center

  def loadSprites(self):
    cat = Cat(self, self.screen.get_rect(), colorkey=(0,255,0))
    self.addFixedSprite(cat, events = [pygame.MOUSEBUTTONDOWN])

    arrow = Arrow(self, colorkey=(0,255,0))
    self.addFixedSprite(arrow, events = [pygame.MOUSEMOTION])

  def loop(self):
    while 1:
#     self.clock.tick(self.tick)

      for event in pygame.event.get():
        self.handleEvent(event)

      if self.quit:
        break

#      self.spritelayer.fill((0,0,0))

      for layer in self.layering:
        #self.layers[layer].clear(self.spritelayer, self.background)
        self.layers[layer].update()
        self.layers[layer].draw(self.spritelayer)

      self.screen.blit(self.spritelayer, (0,0))
      pygame.display.update()

  def handleEvent(self, event):
    if event.type == pygame.QUIT:
      sys.exit()

    if self.events.has_key(event.type):
      self.events[event.type].notify_listeners(event)

  def toggleFullScreen(self):
    if self.flags & pygame.FULLSCREEN:
      self.flags = self.flags & ~pygame.FULLSCREEN
    else:
      self.flags = self.flags | pygame.FULLSCREEN

    self.screen = pygame.display.set_mode(self.size, self.flags)

  def addDynamicSprite(self, sprite, events = []):
    self.layers['dynamic'].add(sprite)

    for event in events:
      if not self.events.has_key(event):
        self.events[event] = Subject()

      self.events[event].attach(sprite)

  def addFixedSprite(self, sprite, events = []):
    self.layers['fixed'].add(sprite)

    for event in events:
      if not self.events.has_key(event):
        self.events[event] = Subject()

      self.events[event].attach(sprite)

  def clearDynamicSprites(self):
    self.layers['dynamic'].empty()

