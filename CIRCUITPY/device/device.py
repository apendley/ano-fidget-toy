import ring_light

class Device:
	BUTTON_SELECT = 0
	BUTTON_UP = 1
	BUTTON_LEFT = 2
	BUTTON_DOWN = 3
	BUTTON_RIGHT = 4	
	BUTTON_COUNT = 5

	BUTTON_BIT_SELECT = 1 << BUTTON_SELECT
	BUTTON_BIT_UP	  = 1 << BUTTON_UP
	BUTTON_BIT_LEFT   = 1 << BUTTON_LEFT
	BUTTON_BIT_DOWN   = 1 << BUTTON_DOWN
	BUTTON_BIT_RIGHT  = 1 << BUTTON_RIGHT
	BUTTON_BITS 	  = BUTTON_BIT_SELECT | BUTTON_BIT_UP | BUTTON_BIT_LEFT | BUTTON_BIT_DOWN | BUTTON_BIT_RIGHT

	DEFAULT_LONG_PRESS_DURATION = 1000

	LONG_PRESS_INACTIVE = 0
	LONG_PRESS_TRIGGERED = 1
	LONG_PRESS_ACTIVE = 2

	def __init__(self, neopixel_pin, led_count):
		self._ring_light = ring_light.RingLight(neopixel_pin, led_count)

		self._rotary_encoder_delta = 0
		self._buttons_state = 0
		self._last_buttons_state = 0

		self._button_long_press_duration = [self.DEFAULT_LONG_PRESS_DURATION] * self.BUTTON_COUNT
		self._button_long_press_timer = [0] * self.BUTTON_COUNT
		self._button_long_press_flag = [self.LONG_PRESS_INACTIVE] * self.BUTTON_COUNT

	def set_long_press_duration(self, button_index, duration):
		self._button_long_press_duration[button_index] = duration

	@property
	def rotary_encoder_delta(self):
		return self._rotary_encoder_delta

	@property
	def ring_light(self):
		return self._ring_light

	def pressed(self, button_index):
		bit = 1 << button_index
		return bit & (self._buttons_state & ~self._last_buttons_state);

	@property
	def any_button_pressed(self):
		return self.BUTTON_BITS & (self._buttons_state & ~self._last_buttons_state);

	def is_down(self, button_index):
		bit = 1 << button_index
		return (self._buttons_state & bit) != 0

	@property
	def any_button_down(self):
		return self._buttons_state != 0

	def released(self, button_index):
		bit = 1 << button_index
		return bit & (~self._buttons_state & self._last_buttons_state)

	@property
	def any_button_released(self):
		return self.BUTTON_BITS & (~self._buttons_state & self._last_buttons_state)		

	def long_pressed(self, button_index):
		return self._button_long_press_flag[button_index] == 1

	@property
	def any_button_long_pressed(self):
		for i in range(self.BUTTON_COUNT):
			if self._button_long_press_flag[i] == self.LONG_PRESS_TRIGGERED:
				return True

		return False

	@property
	def all_buttons_up(self):
		return self._buttons_state == 0

	def update(self, elapsed_ms):
		self._last_buttons_state = self._buttons_state

		self._update_input()
		
		for i in range(self.BUTTON_COUNT):
			if self._is_held(i):
				self._button_long_press_timer[i] += elapsed_ms

				if self._button_long_press_timer[i] < self._button_long_press_duration[i]:
					self._button_long_press_flag[i] = self.LONG_PRESS_INACTIVE
				else:
					if self._button_long_press_flag[i] == self.LONG_PRESS_INACTIVE:
						self._button_long_press_flag[i] = self.LONG_PRESS_TRIGGERED
					elif self._button_long_press_flag[i] == self.LONG_PRESS_TRIGGERED:
						self._button_long_press_flag[i] = self.LONG_PRESS_ACTIVE
			else:
				self._button_long_press_timer[i] = 0 
				self._button_long_press_flag[i] = False

	def _update_input(self):
		# Subclass should implement this, and update:
		# 	self._buttons_state
		# 	self._rotary_encoder_delta
		pass

	def _is_held(self, button_index):
		bit = 1 << button_index
		return bit & (self._buttons_state & self._last_buttons_state);