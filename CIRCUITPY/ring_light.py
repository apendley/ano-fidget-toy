import board
import neopixel
from fidget_helper import gamma8, color_unpack, color_blend, clamp

class RingLight:
	def __init__(self, pin, led_count, brightness=1.0):
		self._led_buffer = [(0, 0, 0)] * led_count		
		self._leds = neopixel.NeoPixel(pin, led_count, brightness=brightness, auto_write=False)

		self._animation = None

		self.crossfade(0)

	def __len__(self):
		return len(self._leds)

	def __getitem__(self, index: int):
		return self._led_buffer[index]

	def __setitem__(self, index: int, new_color):
		# Always store tuple
		if type(new_color) is int:
			self._led_buffer[index] = color_unpack(new_color)
		else:
			self._led_buffer[index] = new_color

	@property
	def brightness(self):
		return self._leds.brightness

	@brightness.setter
	def brightness(self, b):
		self._leds.brightness = b

	def fill(self, c):
		for i in range(len(self._leds)):
			self[i] = c

	# Instead of taking an instantiated animation object, we take the class and 
	# parameters and create the object internally with the appropriate
	# dependencies (specifically, the neopixel strip object, which  I would like to
	# remain "private"). The contents of self._led_buffer will not be drawn while an
	# animation is active. To stop an animation and return to normal rendering, 
	# use set_animation(None)
	def set_animation(self, anim_class, **kwargs):
		if anim_class is None:
			self._animation = None
		else:
			self._animation = anim_class(self._leds, **kwargs)

			# cancel any fades in progress
			self.crossfade(0)

	# Takes a snapshot of the current led buffer and fades to whatever
	# is in the current led buffer over 'duration' milliseconds.
	# To stop a crossfade, use crossfade(0)
	def crossfade(self, duration=200):
		duration = max(0, duration)
		self._fade_timer = 0
		self._fade_duration = duration

		if duration == 0:
			self._snapshot = None
		elif self._animation is not None:
			self._snapshot = []

			# Copy straight from the led object's pixel buffer
			for i in range(len(self._leds)):
				self._snapshot.append(self._leds[i])
		else:
			self._snapshot = self._led_buffer.copy()

	# Blend 'with_buffer' at specified weight (0.0-1.0)
	# with whatever is currently in the led buffer
	def blend(self, with_buffer, weight):
		weight = clamp(weight, 0.0, 1.0)

		for i in range(len(self._leds)):
			c1 = self._led_buffer[i]
			c2 = with_buffer[i]
			self._led_buffer[i] = color_blend(c1, c2, weight)

	# Update any logic and draw the current LED buffer or animation
	def update(self, elapsed_ms):
		if self._animation is not None:
			self._animation.animate()
			return

		if self._fade_duration > 0:
			self._fade_timer += elapsed_ms

			if self._fade_timer <= self._fade_duration:
				for i in range(len(self._leds)):
					from_color = self._snapshot[i]
					to_color = self._led_buffer[i]
					t = self._fade_timer / self._fade_duration
					c = color_blend(from_color, to_color, t)
					self._leds[i] = gamma8(c)
			else:
				self.crossfade(0)
		else:
			for i in range(len(self._leds)):
				self._leds[i] = gamma8(self._led_buffer[i])

		self._leds.show()

	# Helpful method wrap LED indices
	def wrap_index(self, index):
		return int(index % len(self._leds))
