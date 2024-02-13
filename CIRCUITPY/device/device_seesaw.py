from device.device import Device
import board
import busio
from adafruit_seesaw import seesaw

class DeviceSeesaw(Device):
	# Edit pins as necessary
	BUTTON_PINS = [
		# Select
		1,

		# Up
		2,

		# Left
		3,

		# Down
		4,

		# Right
		5
	]

	SS_BUTTON_BITS = Device.BUTTON_BITS << 1
	ROTARY_BITS = 0x18000

	def __init__(self, neopixel_pin, led_count):
		super().__init__(neopixel_pin, led_count)

		# Boost the I2C clock frequency. Seems to buy us 1-2 ms on the Feather RP2040.
		i2c = busio.I2C(board.SCL, board.SDA, frequency=1_000_000)
		ss = seesaw.Seesaw(i2c, addr=0x49)
		self._seesaw = ss

		# Set up buttons
		for pin in self.BUTTON_PINS:
			ss.pin_mode(pin, ss.INPUT_PULLUP)

		# Enable interrupt for encoder and buttons
		ss.enable_encoder_interrupt()
		ss.set_GPIO_interrupts(self.BUTTON_BITS << 1, True)

		# Flush interrupt
		ss.get_GPIO_interrupt_flag()

	def _update_input(self):
		interrupt_flags = self._seesaw.get_GPIO_interrupt_flag()

		# Read buttons and update self._buttons_state			
		if (interrupt_flags & self.SS_BUTTON_BITS) != 0:
			self._buttons_state = ~self._seesaw.digital_read_bulk(self.SS_BUTTON_BITS)
			self._buttons_state &= self.SS_BUTTON_BITS
			self._buttons_state >>= 1
	
		# Update self._rotary_encoder_delta
		if (interrupt_flags & self.ROTARY_BITS) == 0:
			self._rotary_encoder_delta = 0
		else:
			self._rotary_encoder_delta = self._seesaw.encoder_delta()