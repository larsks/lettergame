import os
import random
import pygame

class GameWidget (object):

  category = None

  def __init__ (self, game):
    self.game = game
    self.sounds = []

    if self.category is not None:
      self.loadSounds()

  def loadSounds(self):
    mySoundDir = os.path.join(self.game.soundDirectory, self.category)
    if os.path.isdir(mySoundDir):
      for soundFile in [os.path.join(mySoundDir, x)
          for x in os.listdir(mySoundDir)
          if x.endswith('.wav')]:
        self.sounds.append(pygame.mixer.Sound(soundFile))

  def play(self):
    if self.sounds:
      random.choice(self.sounds).play()


