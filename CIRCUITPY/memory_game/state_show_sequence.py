from memory_game.memory_game_state import MemoryGameState

class StateShowSequence(MemoryGameState):
	SHOW_TIME = 400
	HIDE_TIME = 200

	STATE_SHOW = 1
	STATE_HIDE = 2

	def __init__(self, game, device):
		super().__init__(game, device)

	def enter(self):
		self._preview_index = 0
		self._state = self.STATE_SHOW
		self._state_timer = self.SHOW_TIME

	def update(self, elapsed_ms):
		game = self.game

		self.device.ring_light.fill(0)
		self._state_timer -= elapsed_ms		
		
		# Show the next quadrant in the sequence
		if self._state == self.STATE_SHOW:
			for i in range(game.QUADRANT_COUNT):
				if i == game.sequence[self._preview_index]:
					self._draw_quadrant(i, game.ACTIVE_BRIGHTNESS)
				else:
					self._draw_quadrant(i, game.IDLE_BRIGHTNESS)

			if self._state_timer <= 0:
				if self._preview_index == game.sequence_index:
					# That was the last note, it's the player's turn
					game.set_next_state(game.STATE_ENTER_SEQUENCE)
				else:
					# Keep going
					self._state = self.STATE_HIDE
					self._state_timer = self.HIDE_TIME

		# Hide all quadrants to perceptibly break up each "note" in the sequence
		elif self._state == self.STATE_HIDE:
			for i in range(game.QUADRANT_COUNT):
				self._draw_quadrant(i, game.IDLE_BRIGHTNESS)

				if self._state_timer <= 0:
					self._preview_index += 1
					self._state = self.STATE_SHOW
					self._state_timer = self.SHOW_TIME
