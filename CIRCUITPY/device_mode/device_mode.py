
class DeviceMode:
	def __init__(self, device):
		self._device = device

	@property
	def device(self):
		return self._device

	def enter(self):
		pass

	def update(self, elapsed_ms):
		pass

	def exit(self):
		pass