import pygame

class SpriteQueue(pygame.sprite.Group):

  def __init__ (self, limit, *sprites):
    super(SpriteQueue,self).__init__(*sprites)

    if limit <= 0:
      raise ValueError('Limit must be >= 0.', limit)

    self.limit = limit
    self.queue = []

  def add_internal(self, sprite):
    self.queue.append(sprite)
    super(SpriteQueue, self).add_internal(sprite)

    if len(self.queue) > self.limit:
      print 'DEQUEUE'
      oldsprite = self.queue.pop(0)
      super(SpriteQueue, self).remove_internal(oldsprite)

  def remove_internal(self, sprite):
    try:
      self.queue.remove(sprite)
    except ValueError:
      pass

    super(SpriteQueue, self).remove_internal(sprite)

