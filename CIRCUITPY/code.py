import board
import gc
from adafruit_ticks import ticks_ms, ticks_diff

# Use this import if you are using the regular breakout PCB (https://www.adafruit.com/product/5221)
from device.device_gpio import DeviceGPIO as FidgetDevice

# Use this import if you are using the Stemma QT PCB (https://www.adafruit.com/product/5740)
# from device.device_seesaw import DeviceSeesaw as FidgetDevice

# The device object is the main interface to the hardware features.
# Change the pin and LED count if necessary.
device = FidgetDevice(neopixel_pin=board.D5, led_count=16)

# Set the long press duration for each button, in milliseconds.
device.set_long_press_duration(device.BUTTON_SELECT, 1000)
device.set_long_press_duration(device.BUTTON_UP, 500)
device.set_long_press_duration(device.BUTTON_LEFT, 500)
device.set_long_press_duration(device.BUTTON_DOWN, 500)
device.set_long_press_duration(device.BUTTON_RIGHT, 500)

# All of the device modes. Long-press the select button to cycle through them.
from device_mode.spin_mode import SpinMode
from device_mode.rainbow_mode import RainbowMode
from device_mode.meter_mode import MeterMode
from device_mode.memory_game_mode import MemoryGameMode

device_mode_classes = [
	SpinMode,
	RainbowMode,
	MeterMode,
	MemoryGameMode,
]

# The index of the current mode
current_mode_index = 0

# Create the current mode
current_mode = device_mode_classes[current_mode_index](device)

# Enter the current mode
current_mode.enter()

# Fade in
device.ring_light.crossfade()

# Show memory before we kick things off
gc.collect()
print("free memory:", gc.mem_free())

# Loop/frame timing
last_ticks = ticks_ms()

# Main loop
while True:
	# Track how much time has passed since the last "frame"
	now = ticks_ms()
	elapsed_ms = ticks_diff(now, last_ticks)
	last_ticks = now
	# print("elapsed_ms:", elapsed_ms)

	# Update the device hardware
	device.update(elapsed_ms)

	if device.long_pressed(device.BUTTON_SELECT):
		device.ring_light.crossfade()
		current_mode.exit()

		current_mode_index = (current_mode_index + 1) % len(device_mode_classes)
		current_mode = device_mode_classes[current_mode_index](device)

		current_mode.enter()

		# Show memory after state transition
		gc.collect()
		print("free memory:", gc.mem_free())		
	else:
		current_mode.update(elapsed_ms)
		device.ring_light.update(elapsed_ms)
