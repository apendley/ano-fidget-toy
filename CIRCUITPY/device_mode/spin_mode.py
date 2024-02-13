# Spin (the bottle) Mode
# 
# Spin the rotary encoder to apply accelration to the pointer
# Press DPAD up/down to change the pointer color
# Press DPAD left/right to change the background color
# Press SELECT to apply random acceleration to pointer

from device_mode.device_mode import DeviceMode
from rainbowio import colorwheel
from fidget_helper import color_blend, color_by_index, random_sign, sign
import random

class SpinMode(DeviceMode):
	ACCELERATION = 0.05
	MAX_SPEED = 2.5
	FRICTION = 0.0003
	SPEED_EPSILON = 0.00001

	# For color_by_index. 32 hues + black + white
	PALETTE_SIZE = 34

	def __init__(self, device):
		super().__init__(device)
		led_count = len(device.ring_light)

		self._position = 0.0
		self._last_position = 0.0
		self._velocity = 0.0
		self._max_speed = self.MAX_SPEED * led_count
		self._friction = self.FRICTION * led_count
		self._acceleration = self.ACCELERATION * led_count
		self._pointer_color_index = 1
		self._bg_color_index = 0

		# Draw into separate buffer so we can blend with previous frame
		self._draw_buffer = [(0, 0, 0)] * led_count

	def update(self, elapsed_ms):
		device = self.device
		ring_light = device.ring_light
		led_count = len(ring_light)

		# Update the pointer position based on velocity
		movement_direction = sign(self._velocity)
		speed = abs(self._velocity)

		if speed > self._max_speed:
			speed = self._max_speed
			self._velocity = movement_direction * self._max_speed

		if speed > self.SPEED_EPSILON:
			friction = -movement_direction * elapsed_ms * self._friction
			self._velocity += friction
		else:
			self._velocity = 0		

		# Change pointer color
		if device.pressed(device.BUTTON_UP):
			self._pointer_color_index += 1
			self._pointer_color_index %= self.PALETTE_SIZE

		if device.pressed(device.BUTTON_DOWN):
			self._pointer_color_index -= 1
			self._pointer_color_index %= self.PALETTE_SIZE

		# Change background color
		if device.pressed(device.BUTTON_LEFT):
			self._bg_color_index -= 1
			self._bg_color_index %= self.PALETTE_SIZE			

		if device.pressed(device.BUTTON_RIGHT):
			self._bg_color_index += 1
			self._bg_color_index %= self.PALETTE_SIZE

		# Give the pointer a spin by applying a random velocity
		if device.pressed(device.BUTTON_SELECT):
			# If we're already moving, reverse direction
			d = -movement_direction

			if speed < self.SPEED_EPSILON:
				# Otherwise pick a random direction
				d = random_sign()
			
			self._velocity = d * random.uniform(self._max_speed * 0.25, self._max_speed)

		# Accelerate in the direction of the rotary encoder spin
		if device.rotary_encoder_delta != 0:
			# TODO: Need to incorporate elapsed_ms otherwise framerate is too high
			self._velocity += device.rotary_encoder_delta * self._acceleration

		# Apply velocity to the position
		self._last_position = self._position
		self._position += self._velocity * elapsed_ms / 1000
		# self._position %= led_count

		# Draw the background
		bg_color = color_by_index(self._bg_color_index, self.PALETTE_SIZE, 80)
		for i in range(led_count):
			self._draw_buffer[i] = bg_color

		# Blend with previous frame
		ring_light.blend(self._draw_buffer, 0.15)

		# Draw the pointer after the blend, so it's always at full brightness
		pointer_color = color_by_index(self._pointer_color_index, self.PALETTE_SIZE)

		# To prevent gaps in the trail in case the framerate dips, track the last pointer index.
		pointer_index = int(self._position)		
		last_pointer_index = int(self._last_position)

		# Draw the pixel at the current pointer location
		ring_light[ring_light.wrap_index(pointer_index)] = pointer_color

		# Draw the pixels in between the last position and the current position
		if pointer_index > last_pointer_index:
			pointer_index, last_pointer_index = last_pointer_index, pointer_index

		for i in range(pointer_index, last_pointer_index):
			n = ring_light.wrap_index(i)
			ring_light[n] = pointer_color
