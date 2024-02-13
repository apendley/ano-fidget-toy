from memory_game.memory_game_state import MemoryGameState

# Score display:
#    White pixels = 10 points
#    Green pixels = 5 points
#    Blue pixels = 1 point

class StateScore(MemoryGameState):
	DIVISORS = [10, 5, 1]

	DIVISOR_COLORS = [
		(255, 255, 255),
		(0, 255, 0),
		(0, 0, 255),
	]

	def __init__(self, game, device, score):
		super().__init__(game, device)

		self._pips = []

		for i in range(len(self.DIVISORS)):
			d = self.DIVISORS[i]
			n = int(score / d)
			score = score % d

			for p in range(n):
				self._pips.append(self.DIVISOR_COLORS[i])

	def update(self, elapsed_ms):
		ring_light = self.device.ring_light
		game = self.game

		ring_light.fill(0)

		for i in range(len(self._pips)):
			p = int(ring_light.wrap_index(i - len(ring_light) / 8))
			ring_light[p] = self._pips[i]

		if self.device.any_button_long_pressed:
			game.set_next_state(game.STATE_FIDGET)
			ring_light.crossfade()
