from __future__ import division
from Screens.Screen import Screen
from Components.ActionMap import NumberActionMap
from Components.Input import Input
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.config import config, ConfigInteger
from Components.SystemInfo import SystemInfo
from enigma import eEPGCache
from time import time

import math

config.SleepTimer.defaulttime = ConfigInteger(default = 30, limits=(0,9999))

class SleepTimerEdit(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["red"] = Pixmap()
		self["green"] = Pixmap()
		self["yellow"] = Pixmap()
		self["blue"] = Pixmap()
		self["red_text"] = Label()
		self["green_text"] = Label()
		self["yellow_text"] = Label()
		self["blue_text"] = Label()
		self["current_status"] = Label()
		self.is_active = self.session.nav.SleepTimer.isActive()
		if self.is_active:
			self["current_status"].setText(_("Timer status:") + " " + _("Enabled"))
		else:
			self["current_status"].setText(_("Timer status:") + " " + _("Disabled"))
		
		if self.is_active:
			self.time = self.session.nav.SleepTimer.getCurrentSleepTime()
		else:
			self.time = config.SleepTimer.defaulttime.value
		self["input"] = Input(text = str(self.time), maxSize = False, type = Input.NUMBER)
		
		self.status = True
		self.updateColors()
		
		self["pretext"] = Label(_("Shutdown Dreambox after"))
		self["aftertext"] = Label(_("minutes"))
		
		self["actions"] = NumberActionMap(["SleepTimerEditorActions", "TextEntryActions", "KeyboardInputActions"], 
		{
			"exit": self.cancel,
			"select": self.select,
			"1": self.keyNumberGlobal,
			"2": self.keyNumberGlobal,
			"3": self.keyNumberGlobal,
			"4": self.keyNumberGlobal,
			"5": self.keyNumberGlobal,
			"6": self.keyNumberGlobal,
			"7": self.keyNumberGlobal,
			"8": self.keyNumberGlobal,
			"9": self.keyNumberGlobal,
			"0": self.keyNumberGlobal,
			"selectLeft": self.selectLeft,
			"selectRight": self.selectRight,
			"left": self.selectLeft,
			"right": self.selectRight,
			"home": self.selectHome,
			"end": self.selectEnd,
			"deleteForward": self.deleteForward,
			"deleteBackward": self.deleteBackward,
			"disableTimer": self.disableTimer,
			"toggleAction": self.toggleAction,
			"toggleAsk": self.toggleAsk,
			"useServiceTime": self.useServiceTime,
			"up": self.incrementTime,
			"down": self.decrementTime,
		}, -1)

	def updateColors(self):
		if self.status:
			self["red_text"].setText(_("Action:") + " " + _("Enable timer"))
		else:
			self["red_text"].setText(_("Action:") + " " + _("Disable timer"))
		
		if config.SleepTimer.action.value == "shutdown":
			if SystemInfo["DeepstandbySupport"]:
				shutdownString = _("Standby")
			else:
				shutdownString = _("Shutdown")
			self["green_text"].setText(_("Sleep timer action:") + " " + shutdownString)
		elif config.SleepTimer.action.value == "standby":
			self["green_text"].setText(_("Sleep timer action:") + " " + _("Idle Mode"))
		
		if config.SleepTimer.ask.value:
			self["yellow_text"].setText(_("Ask before shutdown:") + " " + _("yes"))
		else:
			self["yellow_text"].setText(_("Ask before shutdown:") + " " + _("no"))
		self["blue_text"].setText(_("Use time of currently running service"))

	def cancel(self):
		config.SleepTimer.ask.cancel()
		config.SleepTimer.action.cancel()
		self.close()

	def select(self):
		time = self._intValue()
		if self.status and time:
			config.SleepTimer.defaulttime.setValue(time)
			config.SleepTimer.defaulttime.save()
			config.SleepTimer.action.save()
			config.SleepTimer.ask.save()
			self.session.nav.SleepTimer.setSleepTime(time)
			self.session.toastManager.showToast(_("The sleep timer has been activated.") + "\n%s minutes" %(self["input"].getText(),))
		else:
			self.status = False
			self.session.nav.SleepTimer.clear()
			self.session.toastManager.showToast(_("The sleep timer has been disabled."))
		self.close(True)

	def keyNumberGlobal(self, number):
		self["input"].number(number)

	def _intValue(self):
		return int(self["input"].getText() or self._min())

	def _min(self):
		return config.SleepTimer.defaulttime.limits[0][0]

	def _max(self):
		return config.SleepTimer.defaulttime.limits[0][1]

	def incrementTime(self):
		val = self._intValue()
		value = int(math.ceil(val / 10.0)) * 10 #round up
		if val >= 10 or val == 0:
			time = str(min(value + 10, self._max()))
		else:
			time = str(value)
		self.setTime(time)

	def decrementTime(self):
		value = self._intValue()
		decrement = 10 if value > 10 else 1
		if value >= 10:
			value = int(math.floor(value / 10.0)) * 10
		time = str(max(value - decrement, self._min()))
		self.setTime(time)

	def setTime(self, time):
		self["input"].allmarked=True
		self["input"].setText(time)

	def selectLeft(self):
		self["input"].left()

	def selectRight(self):
		self["input"].right()

	def selectHome(self):
		self["input"].home()

	def selectEnd(self):
		self["input"].end()

	def deleteForward(self):
		self["input"].delete()

	def deleteBackward(self):
		self["input"].deleteBackward()

	def disableTimer(self):
		self.status = not self.status
		self.updateColors()

	def toggleAction(self):
		if config.SleepTimer.action.value == "shutdown":
			config.SleepTimer.action.value = "standby"
		elif config.SleepTimer.action.value == "standby":
			config.SleepTimer.action.value = "shutdown"
		self.updateColors()

	def toggleAsk(self):
		config.SleepTimer.ask.value = not config.SleepTimer.ask.value
		self.updateColors()
		
	def useServiceTime(self):
		remaining = None
		ref = self.session.nav.getCurrentlyPlayingServiceReference()
		if ref:
			path = ref.getPath()
			if path and path[0] == '/': # Movie
				service = self.session.nav.getCurrentService()
				seek = service and service.seek()
				if seek:
					length = seek.getLength()
					position = seek.getPlayPosition()
					if length and position:
						remaining = length[1] - position[1]
						if remaining > 0:
							remaining = remaining // 90000
			else: # DVB
				epg = eEPGCache.getInstance()
				event = epg.lookupEventTime(ref, -1, 0)
				if event:
					now = int(time())
					start = event.getBeginTime()
					duration = event.getDuration()
					end = start + duration
					remaining = end - now
		if remaining:
			config.SleepTimer.defaulttime.value = (remaining // 60) + 2
			self["input"].setText(str((remaining // 60) + 2))
