class LimitedQueue (list):

	def __init__ (self, limit, onDequeue = None):
		super(list, self).__init__()
		self.limit = limit
		self.onDequeue = onDequeue

	def enqueue(self, thing):
		if len(self) == self.limit:
			oldthing = self.dequeue()
			if self.onDequeue is not None:
				self.onDequeue(oldthing)

		self.append(thing)

	def dequeue(self):
		oldthing = self.pop(0)
		return oldthing
