class Subject (object):

  def __init__ (self):
    self.listeners = []

  def attach(self, listener, filter = None):
    if not listener in self.listeners:
      self.listeners.append((listener, filter))

  def detach(self, listener):
    target = None

    for i in range(0, len(self.listeners)):
      if listener is self.listeners[i][0]:
        target = i
        break

    if target is not None:
      del self.listeners[target]

  def notify_listeners(self, event):
    for listener, filter in self.listeners:
      if callable(filter) and not filter(listener, event): continue
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

  s.attach(o1)
  s.attach(o2)
  s.notify_listeners('foo')

  s.detach(o1)
  s.notify_listeners('bar')

