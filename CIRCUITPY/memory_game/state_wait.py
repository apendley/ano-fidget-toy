from memory_game.memory_game_state import MemoryGameState

class StateWait(MemoryGameState):
	def __init__(self, game, device, duration, action):
		super().__init__(game, device)
		self._duration = duration
		self._timer = 0
		self._action = action

	def enter(self):
		self._timer = 0

	def update(self, elapsed_ms):
		game = self.game

		self.device.ring_light.fill(0)

		for q in range(game.QUADRANT_COUNT):
			self._draw_quadrant(q, game.IDLE_BRIGHTNESS)

		if self._action is None:
			return

		self._timer += elapsed_ms

		if self._timer >= self._duration:
			self._action()
			self._action = None