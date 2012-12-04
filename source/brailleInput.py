#brailleInput.py
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2012 NV Access Limited
#Copyright (C) 2012 Rui Batista

import os.path
import louis
import braille
import config
from logHandler import log
import winUser
import inputCore

handler = None

def initialize():
	global handler
	handler = BrailleInputHandler()
	log.info("Braille input initialized")

def terminate():
	global handler
	handler = None

class BrailleInputHandler(object):

	def input(self, dots):
		log.info(str(dots))
		char = unichr(dots & 0xff)
		text = louis.backTranslate(
			[os.path.join(braille.TABLES_DIR, config.conf["braille"]["translationTable"]),
			"braille-patterns.cti"],
			char, mode=louis.dotsIO)
		chars = text[0]
		if len(chars) > 0:
			self.sendChars(chars)

	def sendChars(self, chars):
		inputs = []
		for ch in chars:
			input = winUser.Input()
			input.type = winUser.INPUT_KEYBOARD
			input.ii.ki = winUser.KeyBdInput()
			input.ii.ki.wScan = ord(ch)
			input.ii.ki.dwFlags = winUser.KEYEVENTF_UNICODE
			inputs.append(input)
		winUser.SendInput(inputs)

class BrailleInputGesture(inputCore.InputGesture):
	"""Input from a braille keyboard.
	This could either be as part of a braille display or a stand-alone unit.
	L{dots} and L{space} should be set appropriately.
	"""

	#: Bitmask of pressed dots.
	#: @type: int
	dots = 0

	#: Whether the space bar is pressed.
	#: @type: bool
	space = False

	def _get_identifiers(self):
		if self.space and self.dots:
			dotsString = "+".join("dot%d" % (i+1) for i in xrange(8) if self.dots & (1 << i))
			return ("bk:space+%s" % dotsString,
				"bk:space+dots")
		elif self.dots:
			return ("bk:dots",)
		elif self.space:
			return ("bk:space",)
		else:
			return ()

	def _get_displayName(self):
		# Translators: Reported before braille input in input help mode.
		out = [_("braille")]
		if self.space and self.dots:
			# Translators: Reported when braille space is pressed with dots in input help mode.
			out.append(_("space with dot"))
		elif self.dots:
			# Translators: Reported when braille dots are pressed in input help mode.
			out.append(_("dot"))
		elif self.space:
			# Translators: Reported when braille space is pressed in input help mode.
			out.append(_("space"))
		if self.dots:
			for dot in xrange(8):
				if self.dots & (1 << dot):
					out.append(str(dot + 1))
		return " ".join(out)
