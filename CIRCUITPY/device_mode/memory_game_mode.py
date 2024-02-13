# Memory game mode
# 
# Long press the green button to begin a game
# Long press the red button to see the recent score (if there is one)
# Long press the blue button to see the high score (if there is one)

from device_mode.device_mode import DeviceMode
from memory_game.state_fidget import StateFidget
from memory_game import game

class MemoryGameMode(DeviceMode):
	def __init__(self, device):
		super().__init__(device)

		self._game = None
		self._current_state = None

	def enter(self):
		self._game = game.Game()
		first_state = StateFidget(self._game, self.device)
		self._set_state(first_state)

	def exit(self):
		if self._current_state is not None:
			self._current_state.exit()

	def update(self, elapsed_ms):
		if self._current_state is not None:
			self._current_state.update(elapsed_ms)

		next_state = self._game.make_next_state(self.device)

		if next_state is not None:
			self._set_state(next_state)

	def _set_state(self, next_state):
		if self._current_state is not None:
			self._current_state.exit()

		self._current_state = next_state

		if self._current_state is not None:
			self._current_state.enter()
