##
## ServiceType renderer by DimitarCC
##
from Renderer import Renderer
from enigma import ePixmap, eEnv, iServiceInformation, iPlayableService
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Tools.Transponder import ConvertToHumanReadable

class ServiceType(Renderer):

	def __init__(self):
		Renderer.__init__(self)
		self.pngname = ""

	def applySkin(self, desktop, parent):
		#attribs = [ ]
		#for (attrib, value) in self.skinAttributes:
		#	if attrib == "path":
		#		self.path = value
		#	else:
		#		attribs.append((attrib,value))
		#self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def postWidgetCreate(self, instance):
		instance.setScale(1)
		instance.setDefaultAnimationEnabled(self.source.isAnimated)

	def changed(self, what):
		if self.instance:
			if what[0] == self.CHANGED_ANIMATED:
				self.instance.setDefaultAnimationEnabled(self.source.isAnimated)
				return
			pngname = ""
			service = self.source.service
			info = service and service.info()
			tp_data = info and info.getInfoObject(iServiceInformation.sTransponderData)
			fedata = tp_data and ConvertToHumanReadable(tp_data)
			tunersystem = fedata and fedata.get("system") or ""
			icon = "icons/dvb_s_w.png"
			if "%3a//" in info.getInfoString(iServiceInformation.sServiceref).lower():
				icon = "icons/stream_w.png"
			elif tunersystem == "DVB-T" or tunersystem == "DVB-T2":
				icon = "icons/dvb_t_w.png"
			elif tunersystem == "DVB-C":
				icon = "icons/dvb_c_w.png"
			tmp = resolveFilename(SCOPE_CURRENT_SKIN, icon)
			if fileExists(tmp):
				pngname = tmp
			if self.pngname != pngname:
				self.instance.setPixmapFromFile(pngname)
				self.pngname = pngname
