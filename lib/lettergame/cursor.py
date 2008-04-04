import pygame

class Cursor(pygame.sprite.Sprite):
  '''Follows mouse position around the screen.'''

  def __init__ (self, image):
    super(Cursor, self).__init__()
    self.image = image
    self.rect = image.get_rect()

  def notify(self, event):
    self.rect.topleft = event.pos

