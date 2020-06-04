# -*- coding: utf-8 -*-
from Components.Converter.Converter import Converter
from enigma import eServiceCenter, eServiceReference, iServiceInformation, iPlayableService, iPlayableServicePtr, iDVBFrontend as FE
from Components.Element import cached
from Components.config import config
from Screens.InfoBar import InfoBar

class ServiceName(Converter, object):
	NAME = 0
	PROVIDER = 1
	REFERENCE = 2
	NUMBER_NAME_PROVIDER = 3

	def __init__(self, type):
		Converter.__init__(self, type)
		self.channelSelectionServicelist = InfoBar.instance and InfoBar.instance.servicelist
		if type == "Provider":
			self.type = self.PROVIDER
		elif type == "Reference":
			self.type = self.REFERENCE
		elif type == "ServiceNumberAndName":
			self.type = self.NUMBER_NAME_PROVIDER
			self.list = []
		else:
			self.type = self.NAME

	def getServiceInfoValue(self, info, what, ref=None):
		v = ref and info.getInfo(ref, what) or info.getInfo(what)
		if v != iServiceInformation.resIsString:
			ret = "N/A" if not ref or self.type != self.REFERENCE else ref.toString()
		elif ref:
			ret = info.getInfoString(ref, what) or self.type == self.REFERENCE and ref.toString()
		else:
			ret = info.getInfoString(what)
		return ret

	@cached
	def getText(self):
		service = self.source.service
		if isinstance(service, iPlayableServicePtr):
			info = service and service.info()
			ref = None
		else: # reference
			info = service and self.source.info
			ref = service
		if info is None:
			return ""
		name = ref and info.getName(ref)
		if name is None:
			name = info.getName()
		nametext = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
		provider = self.getServiceInfoValue(info, iServiceInformation.sProvider, ref)
		
		if self.type == self.NAME:
			return nametext
		elif self.type == self.PROVIDER:
			return provider
		elif self.type == self.REFERENCE:
			return self.getServiceInfoValue(info, iServiceInformation.sServiceref, ref)
		elif self.type == self.NUMBER_NAME_PROVIDER:
			channelnum = ''
			orbitalpos = ''
			ref = ref or eServiceReference(info.getInfoString(iServiceInformation.sServiceref))
			if self.channelSelectionServicelist.inBouquet():
				isalternatenum = False
				try:
					isalternatenum = config.plugins.NumberZapExt.acount.value
				except:
					isalternatenum = False
				markeroffset = 0
				bouquetoffset = 0
				serviceHandler = eServiceCenter.getInstance()
				services = serviceHandler.list(eServiceReference('1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195) FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
				bouquets = services and services.getContent("SN", True)
				myRoot = self.channelSelectionServicelist.getRoot()
				mySSS = serviceHandler.list(myRoot)
				for bouquet in bouquets:
					if not isalternatenum or eServiceReference(bouquet[0]) == myRoot:
						services = serviceHandler.list(eServiceReference(bouquet[0]))
						channels = services and services.getContent("SN", True)
						for idx in range(1, len(channels)):
							if not channels[idx-1][0].startswith("1:64:"):
								if ref.toString() == channels[idx-1][0]:
									if isalternatenum:
										channelnum = str(idx - markeroffset)
									else:
										channelnum = str(idx - markeroffset + bouquetoffset)
									break
							else:
								markeroffset = markeroffset + 1
						bouquetoffset = bouquetoffset + len(channels)
			if channelnum != '':
				resulttext = "%s. %s" % (channelnum, nametext)
			else:
				resulttext = nametext
			tp_data = info.getInfoObject(iServiceInformation.sTransponderData)
			if tp_data is not None:
				position = tp_data["orbital_position"]
				if position > 1800: # west
					orbitalpos = "%.1f " %(float(3600 - position)/10) + _("W")
				else:
					orbitalpos = "%.1f " %(float(position)/10) + _("E")
			if orbitalpos != "":
				resulttext = "%s  •  %s" % (resulttext, orbitalpos) 
			if provider != "":
				resulttext = "%s  •  %s" % (resulttext, provider) 
			return resulttext

	text = property(getText)

	def changed(self, what):
		if what[0] != self.CHANGED_SPECIFIC or what[1] in (iPlayableService.evStart,):
			Converter.changed(self, what)