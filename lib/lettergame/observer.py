class Subject (object):

  def __init__ (self):
    self.listeners = []

  def attach(self, listener):
    if not listener in self.listeners:
      self.listeners.append(listener)

  def detach(self, listener):
    if listener in self.listeners:
      self.listeners.remove(listener)

  def clear(self):
    self.listeners = []

  def notify_listeners(self, event):
    for listener in self.listeners:
      if listener.notify(event): break

class _observer:

  def __init__(self, name):
    self.name = name

  def notify(self, event):
    print self.name, 'notified with:', event

if __name__ == '__main__':

  s = Subject()
  o1 = _observer('o1')
  o2 = _observer('o2')

  print 'attaching o1'
  s.attach(o1)
  print 'attaching o2'
  s.attach(o2)
  s.notify_listeners('foo')

  print 'detaching o1'
  s.detach(o1)
  s.notify_listeners('bar')

