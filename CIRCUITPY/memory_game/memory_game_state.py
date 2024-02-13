from fidget_helper import color_scale

class MemoryGameState():
	def __init__(self, game, device):
		self.game = game
		self.device = device

		self._button_index_for_quadrant = [
			device.BUTTON_UP,
			device.BUTTON_RIGHT,
			device.BUTTON_DOWN,
			device.BUTTON_LEFT,
		]				

	def enter(self):
		pass

	def update(self, elapsed_ms):
		pass

	def exit(self):
		pass

	# Helpers for drawing the four colored quadrants
	def _get_quadrant_center_led(self, quadrant_index):
		led_count = len(self.device.ring_light)
		return int(quadrant_index * (led_count / 4))

	def _get_quadrant_leds(self, quadrant_index):
		led_count = len(self.device.ring_light)
		quadrant_led_count = int(led_count / 4 - 1)
		first_led_offset = int(quadrant_led_count / 2)
		center_led = int(quadrant_index * (led_count / 4))
		first_led = center_led - first_led_offset		

		leds = []

		for i in range(first_led, first_led + quadrant_led_count):
			leds.append(self.device.ring_light.wrap_index(i))
		
		return leds

	def _draw_quadrant(self, quadrant_index, brightness):
		c = self.game.QUADRANT_COLORS[quadrant_index]
		c = color_scale(c, brightness)

		for i in self._get_quadrant_leds(quadrant_index):
			self.device.ring_light[i] = c
