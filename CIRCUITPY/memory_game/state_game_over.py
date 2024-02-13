from memory_game.memory_game_state import MemoryGameState

class StateGameOver(MemoryGameState):
	def __init__(self, game, device, expected_quadrant):
		super().__init__(game, device)
		self._expected_quadrant = expected_quadrant
		self._delay = 3000

	def update(self, elapsed_ms):
		game = self.game
		device = self.device
		ring_light = device.ring_light

		# Draw the color of the quadrant the player missed
		c = game.QUADRANT_COLORS[self._expected_quadrant]
		ring_light.fill(c)

		self._delay -= elapsed_ms

		if self._delay <= 0:
			if game.last_score > 0:
				game.set_next_state(game.STATE_SCORE, score=game.last_score)
			else:
				game.set_next_state(game.STATE_FIDGET)

			ring_light.crossfade()