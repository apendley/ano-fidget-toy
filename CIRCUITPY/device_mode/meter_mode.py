# Meter simulator mode
# 
# Spin the rotary encoder hide either the low part or the high part of the meter
# Press DPAD up to cycle through the brightness settings
# Press DPAD left to cycle through the colors for the "low" part of the meter
# Press DPAD down to cycle through the colors for the "medium" part of the meter
# Press DPAD right to cycle through the colors for the "high" part of the meter

from device_mode.device_mode import DeviceMode
from fidget_helper import color_blend, color_by_index, color_scale, sign
from rainbowio import colorwheel

class MeterMode(DeviceMode):
	BRIGHTNESS_VALUES = [100, 150, 200, 255]

	# For color_by_index. 32 hues + black + white
	PALETTE_SIZE = 34	

	def __init__(self, device):
		super().__init__(device)

		self._position = 0

		# The +2s below are to skip over black and white
		# Red
		self._low_color_index = 0 + 2
		# Yellow
		self._medium_color_index = 5 + 2
		# Green
		self._high_color_index = 10 + 2

		# Next-to-lowest setting
		self._brightness_index = 1

	def enter(self):
		self._position = 0

	def update(self, elapsed_ms):
		device = self.device
		ring_light = device.ring_light

		led_count = len(ring_light)
		half_led_count = int(led_count / 2)

		# Change brightness
		if device.pressed(device.BUTTON_UP):
			self._brightness_index += 1
			self._brightness_index %= len(self.BRIGHTNESS_VALUES)

		# Change meter colors
		if device.pressed(device.BUTTON_DOWN):
			self._medium_color_index += 1
			self._medium_color_index %= self.PALETTE_SIZE

		if device.pressed(device.BUTTON_LEFT):
			self._low_color_index += 1
			self._low_color_index %= self.PALETTE_SIZE

		if device.pressed(device.BUTTON_RIGHT):
			self._high_color_index += 1
			self._high_color_index %= self.PALETTE_SIZE

		# Move the meter position. We'll calculate the start/end positions 
		# for the meter based on the position later.
		if device.rotary_encoder_delta != 0:
			self._position += device.rotary_encoder_delta

			# Move from (-16 to 15) space to (0 to 31) space
			p = self._position + led_count
			# Wrap it
			p %= led_count * 2
			# And move it back into (-16 to 15) space
			p -= led_count

			# At position = -16, no pixels would be drawn, so skip over it.
			# I'm sure there's a more mathy way to do this.
			if p == -led_count:
				spin_direction = sign(device.rotary_encoder_delta)				
				if spin_direction == 1:
					p = 1 - led_count
				else:
					p = led_count - 1

			self._position = p

		# Clear the buffer
		ring_light.fill(0)

		# Figure out start/end positions for the meter
		if self._position >= 0:
			start_position = self._position
			end_position = led_count - 1
		else:
			start_position = 0
			end_position = self._position + led_count - 1

		# Finally, draw the meter
		for i in range(start_position, end_position + 1):
			if i < half_led_count:
				# Interpolate between the high and medium colors
				t = i / half_led_count
				from_color = color_by_index(self._high_color_index, self.PALETTE_SIZE)
				to_color = color_by_index(self._medium_color_index, self.PALETTE_SIZE)
			else:
				# Interpolate between the medium and low colors
				t = (i - half_led_count) / half_led_count
				from_color = color_by_index(self._medium_color_index, self.PALETTE_SIZE)
				to_color = color_by_index(self._low_color_index, self.PALETTE_SIZE)

			c = color_blend(from_color, to_color, t)
			b = self.BRIGHTNESS_VALUES[self._brightness_index]
			ring_light[i] = color_scale(c, b)
