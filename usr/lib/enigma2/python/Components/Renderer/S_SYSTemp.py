from Components.VariableText import VariableText
from enigma import eLabel
from Renderer import Renderer
from os import path, popen

class S_SYSTemp(Renderer, VariableText):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		
	GUI_WIDGET = eLabel

	def changed(self, what):
		if not self.suspended:
			systemp = "-- "
			try:
				if path.exists('/proc/stb/sensors/temp0/value'):
					out_line = popen("cat /proc/stb/sensors/temp0/value").readline()
					systemp = out_line.replace('\n', '')
				elif path.exists('/proc/stb/fp/temp_sensor'):
					out_line = popen("cat /proc/stb/fp/temp_sensor").readline()
					systemp = out_line.replace('\n', '')
				elif path.exists('/sys/devices/virtual/thermal/thermal_zone0/temp'):
					systemp = popen("cat /sys/devices/virtual/thermal/thermal_zone0/temp").read().strip()
					#f = open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r')
					#tempinfo = f.read()
					#systemp = tempinfo[:-4]
					#f.close()
				if not systemp == "-- " and len(systemp) > 2:
					systemp = systemp[:2]
			except:
				pass
			self.text = systemp + str('\xc2\xb0') + "C"
			
	def onShow(self):
		self.suspended = False
		self.changed(None)

	def onHide(self):
		self.suspended = True

