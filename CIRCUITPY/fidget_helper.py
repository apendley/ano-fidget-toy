import math
import random
from rainbowio import colorwheel

# ---------------------------
# gamma8
# ---------------------------
_gamma = 1.6
_gamma_table = []

for i in range(256):
	value = math.pow(i / 255.0, _gamma) * 255.0 + 0.5
	_gamma_table.append(int(value))

def gamma8(c):
	global _gamma_table

	if type(c) is int:
		c = color_unpack(c)

	return (
		_gamma_table[c[0]], 
		_gamma_table[c[1]], 
		_gamma_table[c[2]]
	)

# ---------------------------
# sin8
# ---------------------------
_sin_table = []

for i in range(256):
	value = int((math.sin(i / 128.0 * math.pi) + 1.0) * 127.5 + 0.5)
	_sin_table.append(value)

def sin8(x):
	global _sin_table
	return _sin_table[x % 256]

# ---------------------------
# Clamp
# ---------------------------	

def clamp(val, lower, upper):
	return max(lower, min(val, upper))

# ---------------------------
# Color helpers
# ---------------------------
def color_unpack(packed_rgb):
	r = (packed_rgb >> 16) & 0xFF
	g = (packed_rgb >> 8) & 0xFF
	b = packed_rgb & 0xFF
	return (r, g, b)

def color_scale(c, brightness):
	inv = brightness / 255

	if type(c) is int:
		c = color_unpack(c)

	return (
		int(c[0] * inv), 
		int(c[1] * inv), 
		int(c[2] * inv)
	)

def color_blend(from_color, to_color, t):
	if type(from_color) is int:
		from_color = color_unpack(from_color)
	
	if type(to_color) is int:
		to_color = color_unpack(to_color)

	t = clamp(t, 0.0, 1.0)
	t_from = 1.0 - t

	return (
		int(from_color[0] * t_from + to_color[0] * t),
		int(from_color[1] * t_from + to_color[1] * t),
		int(from_color[2] * t_from + to_color[2] * t),
	)

# Splits rainbow into (palette_size - 2) indices, 
# and assigns black to index 0, and white to index 1.
def color_by_index(index, palette_size, brightness=255):
	# 0 is black
	if index == 0:
		return (0, 0, 0)
	# 1 is white
	elif index == 1:
		return (brightness, brightness, brightness)
	# Everything else is part of the rainbow
	else:
		hue = int((index - 2) * (255 / (palette_size - 2)))
		rgb = colorwheel(hue)
		return color_scale(rgb, brightness)

# ---------------------------
# Sign/direction helpers
# ---------------------------
def random_sign():
	if random.randrange(0, 2) == 0:
		return 1

	return -1

def sign(x):
	if x < 0:
		return -1

	return 1