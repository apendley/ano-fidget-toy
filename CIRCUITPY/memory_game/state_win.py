from memory_game.memory_game_state import MemoryGameState
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle

class StateWin(MemoryGameState):
	def enter(self):
		ring_light = self.device.ring_light
		sparkle_count = int(len(ring_light)/6)
		ring_light.set_animation(RainbowSparkle, speed=0.1, num_sparkles=sparkle_count)
		
	def exit(self):
		self.device.ring_light.set_animation(None)

	def update(self, elapsed_ms):
		game = self.game

		if self.device.any_button_long_pressed:
			game.set_next_state(game.STATE_SCORE, score=game.high_score)
			self.device.ring_light.crossfade()
