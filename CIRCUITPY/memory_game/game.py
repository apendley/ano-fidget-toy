import microcontroller
import random

from memory_game.state_fidget import StateFidget
from memory_game.state_wait import StateWait
from memory_game.state_show_sequence import StateShowSequence
from memory_game.state_enter_sequence import StateEnterSequence
from memory_game.state_game_over import StateGameOver
from memory_game.state_score import StateScore
from memory_game.state_win import StateWin

class Game:
	# Sequence length to win the game
	MAX_SEQUENCE_LENGTH = 50

	# Quadarant data
	QUADRANT_RED = 0
	QUADRANT_BLUE = 1
	QUADRANT_YELLOW = 2		
	QUADRANT_GREEN = 3
	QUADRANT_COUNT = 4

	QUADRANT_COLORS = [
		(255, 0, 0),
		(0, 0, 255),
		(255, 255, 0),
		(0, 255, 0),
	]

	# State machine classes
	# Defined here for 2 reasons:
	# 	1) To prevent circular dependencies between state classes
	# 	2) To provide current state object easy access to the canonical list of states, 
	# 	   since each state object gets a reference to the game object at creation time.
	STATE_FIDGET = StateFidget
	STATE_WAIT = StateWait
	STATE_SHOW_SEQUENCE = StateShowSequence
	STATE_ENTER_SEQUENCE = StateEnterSequence
	STATE_GAMEOVER = StateGameOver
	STATE_SCORE = StateScore
	STATE_WIN = StateWin

	# Brightness constants
	IDLE_BRIGHTNESS = 50
	ACTIVE_BRIGHTNESS = 255

	# High score save data signature
	HIGH_SCORE_SAVE_SIG = b"MGHS"
	HIGH_SCORE_SAVE_SIG_SIZE = len(HIGH_SCORE_SAVE_SIG)

	def __init__(self):
		self._high_score = self._load_high_score()

		self._next_state = None
		self.last_score = 0

		self.sequence_index = 0
		self.sequence = [0] * self.MAX_SEQUENCE_LENGTH

	def start(self):
		self._next_state = None
		self.last_score = 0		

		self.sequence_index = 0		

		for i in range(self.MAX_SEQUENCE_LENGTH):
			self.sequence[i] = random.randrange(0, 4)

	@property
	def high_score(self):
		return self._high_score

	@high_score.setter
	def high_score(self, s):
		self._high_score = s
		self._save_high_score()

	def _load_high_score(self):
		save_sig = microcontroller.nvm[0:self.HIGH_SCORE_SAVE_SIG_SIZE]

		if save_sig == self.HIGH_SCORE_SAVE_SIG:
			# return the byte right after the signature
			high_score_byte = microcontroller.nvm[self.HIGH_SCORE_SAVE_SIG_SIZE]
			return microcontroller.nvm[self.HIGH_SCORE_SAVE_SIG_SIZE]

		return 0

	def _save_high_score(self):
		microcontroller.nvm[0:self.HIGH_SCORE_SAVE_SIG_SIZE] = self.HIGH_SCORE_SAVE_SIG
		microcontroller.nvm[self.HIGH_SCORE_SAVE_SIG_SIZE] = self._high_score

	# Instead of taking an instantiated state object, we take the class and 
	# parameters and create the state object internally so we can inject
	# the device object and game object dependencies at creation time. 
	# This also helps reduce a bit of boilerplate code when performing 
	# state transitions.
	def set_next_state(self, state_class, **kwargs):
		self._next_state = (state_class, kwargs)

	def make_next_state(self, device):
		next_state_token = self._next_state

		if next_state_token is None:
			return None

		self._next_state = None

		next_state_class = next_state_token[0]
		next_state_params = next_state_token[1]
		return next_state_class(self, device, **next_state_params)
