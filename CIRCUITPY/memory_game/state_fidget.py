from memory_game.memory_game_state import MemoryGameState
from fidget_helper import sin8, color_scale

class StateFidget(MemoryGameState):
	def enter(self):
		ring_light = self.device.ring_light

		p = -len(ring_light) / 8
		self._spoke_position = ring_light.wrap_index(int(p))
		self._pulse_elapsed = 0

		# We're gonna wait for all buttons to be up before
		# we start processing any button input.
		self._ignore_buttons = not self.device.all_buttons_up

	def update(self, elapsed_ms):
		device = self.device
		ring_light = device.ring_light
		game = self.game

		ring_light.fill(0)

		period = 3000
		self._pulse_elapsed += elapsed_ms
		self._pulse_elapsed %= period

		n = int(self._pulse_elapsed * 255 / period)
		s = sin8(192 + n)

		pulse_min = 32
		pulse_max = 128
		pulse_range = pulse_max - pulse_min
		b = pulse_min + int(s * pulse_range / 255)

		# Draw the quadrants
		for q in range(game.QUADRANT_COUNT):
			button_index = self._button_index_for_quadrant[q]
			# button = device.buttons[button_index]

			# if button.value or self._ignore_buttons:
			if device.is_down(button_index) == False or self._ignore_buttons:
				self._draw_quadrant(q, b)
			else:
				self._draw_quadrant(q, 200)

		# Move the spokes with the rotary encoder
		if device.rotary_encoder_delta != 0:
			self._spoke_position += device.rotary_encoder_delta
			self._spoke_position = ring_light.wrap_index(self._spoke_position)

		# Draw the "spokes"
		led_count = len(ring_light)
		spoke_brightness = 160

		if device.is_down(device.BUTTON_SELECT):
			spoke_brightness = 255

		for i in range(0, 4):
			index = ring_light.wrap_index(self._spoke_position + i * led_count / 4)
			ring_light[index] = (spoke_brightness, spoke_brightness, spoke_brightness)				

		# Ignore new button input until all buttons are up
		if self._ignore_buttons:
			if device.all_buttons_up:
				self._ignore_buttons = False
			else:
				return

		# Left button = green quadrant = start game
		if device.long_pressed(device.BUTTON_LEFT):
			# The game officially starts now
			game.start()

			game.set_next_state(game.STATE_WAIT, 
								duration=2500, 
								action=lambda: game.set_next_state(game.STATE_SHOW_SEQUENCE))

			ring_light.crossfade()
			return

		# Up button = red quadrant = see last score (if there is one)
		if device.long_pressed(device.BUTTON_UP):
			if game.last_score > 0:
				game.set_next_state(game.STATE_SCORE, score=game.last_score)
				ring_light.crossfade()

		# Right button = blue quadrant = see high score (if there is one)
		if device.long_pressed(device.BUTTON_RIGHT):
			if game.high_score > 0:
				game.set_next_state(game.STATE_SCORE, score=game.high_score)
				ring_light.crossfade()
