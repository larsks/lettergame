class Subject (object):

  def __init__ (self):
    self.listeners = []

  def attach(self, listener):
    if not listener in self.listeners:
      self.listeners.append(listener)

  def detach(self, listener):
    if listener in self.listeners:
      self.listeners.remove(listener)

  def notify_listeners(self):
    for listener in self.listeners:
      listener.notify(self)

class Observer (object):

  def notify (self, event):
    pass

