"""
Used to store training memory.
"""

# Standard
from collections import deque

# Local
import config


class Memory:
	def __init__(self, Memory_size):
		self.MEMORY_SIZE = Memory_size
		self.ltmemory = deque(maxlen=Memory_size)
		self.stmemory = deque(maxlen=Memory_size)

	def commit_stmemory(self, identities, state, actionValues):
		for r in identities(state, actionValues):
			self.stmemory.append({'board': r[0].board,
				'state': r[0],
				'id': r[0].id,
				'AV': r[1],
				'playerTurn': r[0].playerTurn
				})

	def commit_ltmemory(self):
		for i in self.stmemory:
			self.ltmemory.append(i)
		self.clear_stmemory()

	def clear_stmemory(self):
		self.stmemory = deque(maxlen=config.MEMORY_SIZE)
