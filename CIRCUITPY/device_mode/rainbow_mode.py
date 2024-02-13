# Rainbow mode
# 
# Spin the rotary encoder spin the rainbow
# Press a DPAD button to spawn a particle on the opposite side of the ring and "attract" it
# Press SELECT to create a particle "explosion" from a random point on the ring

from device_mode.device_mode import DeviceMode
from rainbowio import colorwheel
from fidget_helper import color_scale, random_sign
import random

class Particle:
	def __init__(self, ring_light):
		self.ring_light = ring_light
		self.is_active = False
		self.position = 0
		self.color = (0, 0, 0)
		self.speed = 1.0
		self.duration = 1000

	def activate(self, position, color, speed, duration):
		self.is_active = True
		self.position = position
		self.color = color
		self.speed = speed
		self.duration = duration

	def deactivate(self):
		self.is_active = False

	def update(self, elapsed_ms):
		if not self.is_active:
			return

		self.duration -= elapsed_ms

		if self.duration <= 0:
			self.duration = 0
			self.is_active = False
			return

		self.position += self.speed * elapsed_ms / 1000
		p = self.ring_light.wrap_index(self.position)
		self.ring_light[p] = self.color


class RainbowMode(DeviceMode):
	def __init__(self, device):
		super().__init__(device)
		self._position = 0
		self._particle_count = 16
		self._particles = []

		for p in range(self._particle_count):
			self._particles.append(Particle(device.ring_light))

	def enter(self):
		self._position = 0
		
		for p in self._particles:
			p.is_active = False

	def update(self, elapsed_ms):
		device = self.device
		ring_light = device.ring_light
		led_count = len(ring_light)

		# "Attract" a particle from the opposite side of the ring to the pressed button
		if device.pressed(device.BUTTON_UP):
			p = int(led_count / 2)
			self._new_particle(p)			

		if device.pressed(device.BUTTON_LEFT):
			p = int(led_count / 4)
			self._new_particle(p)

		if device.pressed(device.BUTTON_DOWN):
			self._new_particle(0)

		if device.pressed(device.BUTTON_RIGHT):
			p = -int(led_count / 4)
			self._new_particle(p)

		# Particle explosion from random point
		if device.pressed(device.BUTTON_SELECT):
			n = random.randrange(3, 5)
			p = random.randrange(0, led_count)

			for i in range(n):
				b = random.randrange(128, 256)
				self._new_particle(position=p, 
								   speed=random.uniform(0.5, 2.5), 
								   duration=random.randrange(500, 1250), 
								   color=(b, b, b))

		# Spin the rainbow
		if device.rotary_encoder_delta != 0:
			self._position += device.rotary_encoder_delta
			self._position = ring_light.wrap_index(self._position)

		for i in range(led_count):
			n = ring_light.wrap_index(self._position - i)
			hue = n * 256 / led_count;
			c = colorwheel(hue)
			c = color_scale(c, 160)
			ring_light[i] = c

		# Draw the particles over the rainbow
		for particle in self._particles:
			if particle.is_active:
				particle.update(elapsed_ms)

	def _new_particle(self, 
					  position, 
					  direction=0, 
					  speed=2.5, 
					  duration=220, 
					  color=(255, 255, 255)):
		# Look for an inactive particle
		try:
			particle = next(particle for particle in self._particles if not particle.is_active)
		except StopIteration:
			return

		ring_light = self.device.ring_light

		if direction == 0:
			direction = random_sign()

		# This way it appears to emit from the same pixel in both directions
		if direction == -1:
			position += 1

		led_count = len(ring_light)
		position = ring_light.wrap_index(position)

		particle.activate(position=position,
						  color=color,
						  speed=led_count * direction * speed,
						  duration=duration)
