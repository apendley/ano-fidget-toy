from memory_game.memory_game_state import MemoryGameState

class StateEnterSequence(MemoryGameState):
	INPUT_TIMEOUT = 5000

	def enter(self):
		self._input_timer = self.INPUT_TIMEOUT
		self._user_sequence_index = 0		
		self._pressed_quadrant = None		
		self._expected_quadrant = self.game.sequence[self._user_sequence_index]		

	def update(self, elapsed_ms):
		device = self.device
		game = self.game

		# We'll use this to tell when the player presses/releases a quadrant button
		previous_quadrant = self._pressed_quadrant

		# Since it's easy to accidentally press multiple directions simultaneously 
		# on the ANO dpad, we listen for the first press and ignore all further
		# button presses until all buttons are once again up.
		if self._pressed_quadrant is None:
			for q in range(game.QUADRANT_COUNT):
				button_index = self._button_index_for_quadrant[q]

				if device.pressed(button_index):
					self._pressed_quadrant = q
					break
		elif device.all_buttons_up:
			self._pressed_quadrant = None

		# Draw the quadrants
		for q in range(game.QUADRANT_COUNT):
			b = game.IDLE_BRIGHTNESS

			if q == self._pressed_quadrant:
				b = game.ACTIVE_BRIGHTNESS	
			
			self._draw_quadrant(q, b)

		if self._pressed_quadrant is None:
			# Did the player just release the quadrant button?
			if previous_quadrant is not None:
				# Yep, was it the right quadrant?
				if self._expected_quadrant == previous_quadrant:
					# It was! Move on to the next "note"
					self._user_sequence_index += 1

					# Are we caught up to the current "note"?
					if self._user_sequence_index >= game.sequence_index + 1:
						game.sequence_index += 1

						# Are we at the end of the sequence?!
						if game.sequence_index == game.MAX_SEQUENCE_LENGTH:
							# Amazing!
							game.last_score = game.sequence_index

							if game.last_score > game.high_score:
								game.high_score = game.last_score

							game.set_next_state(game.STATE_WIN)
						else:
							# You wish, buddy
							game.set_next_state(game.STATE_WAIT, 
												duration=1250, 
												action=lambda: game.set_next_state(game.STATE_SHOW_SEQUENCE))
					else:
						# Not caught up to current note, keep going.
						self._expected_quadrant = game.sequence[self._user_sequence_index]
				else:
					# Incorrect quadrant pressed, so sad.
					self._game_over()
			else:
				# Game over if user takes too long to press a button
				self._input_timer -= elapsed_ms

				if self._input_timer <= 0:
					self._game_over()
		else:
			# One of the buttons is down, reset the input timer
			self._input_timer = self.INPUT_TIMEOUT

	def _game_over(self):
		game = self.game

		game.last_score = game.sequence_index

		if game.last_score > game.high_score:
			game.high_score = game.last_score

		game.set_next_state(game.STATE_GAMEOVER, expected_quadrant=self._expected_quadrant)