from device.device import Device
import board
import digitalio
import rotaryio

class DeviceGPIO(Device):
	# Edit pins as necessary
	BUTTON_PINS = [
		# Select
		board.D25,

		# Up
		board.A3,

		# Left
		board.A2,

		# Down
		board.A1,

		# Right
		board.D24
	]

	ENCODER_PIN_A = board.MOSI
	ENCODER_PIN_B = board.SCK

	def __init__(self, neopixel_pin, led_count):
		super().__init__(neopixel_pin, led_count)

		self._encoder = rotaryio.IncrementalEncoder(self.ENCODER_PIN_A,
													self.ENCODER_PIN_B, 
													divisor=2)

		self._buttons = []

		for i in range(self.BUTTON_COUNT):
			pin = self.BUTTON_PINS[i]
			button = digitalio.DigitalInOut(pin)
			button.direction = digitalio.Direction.INPUT
			button.pull = digitalio.Pull.UP
			self._buttons.append(button)

	def _update_input(self):
		# Update self._rotary_encoder_delta
		encoder_position = self._encoder.position

		if encoder_position == 0:
			self._rotary_encoder_delta = 0
		else:
			self._rotary_encoder_delta = encoder_position
			self._encoder.position = 0

		# Update self._buttons_state
		self._buttons_state = 0

		for i in range(self.BUTTON_COUNT):
			if self._buttons[i].value == False:
				self._buttons_state |= 1 << i
