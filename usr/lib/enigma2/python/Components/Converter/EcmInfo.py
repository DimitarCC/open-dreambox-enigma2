# Coded by Dream Elite Team
from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import iServiceInformation, iPlayableService
from Poll import Poll
from DE.DELibrary import Tool
t=Tool()
refresh = 6000

class EcmInfo(Poll, Converter, object):

	CA_ID = 0
	PID = 1
	HOPS = 2
	CRYPT = 3
	ECM_TIME = 4
	READER_SOURCE = 5
	READER_ADDRESS = 6
	EMU_NAME = 7

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)

		self.poll_interval = refresh
		self.poll_enabled = True

		self.ecm_info = {}
		self.systemCaids = 	{	"01" : "Seca",
								"05" : "Viaccess",
								"06" : "Irdeto",
								"09" : "NDS",
								"0B" : "Conax",
								"0D" : "CryptoWorks",
								"17" : "BetaCrypt",
								"18" : "Nagravision",
								"26" : "BiSS",
							}
		self.type = {	"CaId": 			self.CA_ID,
						"Pid":				self.PID,
						"Hops":				self.HOPS,
						"Crypt":			self.CRYPT,
						"EcmTime":			self.ECM_TIME,
						"Reader":			self.READER_SOURCE,
						"ReaderAddress":	self.READER_ADDRESS,
						"EmuActive":		self.EMU_NAME,
					}[type]

	@cached
	def getText(self):
		textvalue = ""
		service = self.source.service
		if service:
			info = service and service.info()
			if info:
				ecm_info = self.ecm_info
				# CaId
				if self.type == self.CA_ID:
					caid = ecm_info.get("caid", "")
					if caid:
						caid = caid.lstrip("0x")
						caid = caid.upper()
						caid = caid.zfill(4)
						return "CaID: %s" % caid
					if info.getInfoObject(iServiceInformation.sCAIDs):
						return "Crypted"
					else:
						return "FTA"
				# Pid
				elif self.type == self.PID:
					pid = ecm_info.get("pid", "")
					if pid:
						pid = pid.lstrip("0x")
						pid = pid.upper()
						pid = pid.zfill(4)
						return "Pid: %s" % pid
					return textvalue
				# Hops
				elif self.type == self.HOPS:
					hops = ecm_info.get("hops", "")
					if hops:
						return hops
					return textvalue
				# Crypt
				elif self.type == self.CRYPT:
					caids = info.getInfoObject(iServiceInformation.sCAIDs)
					if caids:
						emu_caid = ecm_info.get("caid", "")
						if emu_caid:
							c = emu_caid.lstrip("0x")
							if len(c) == 3:
								c = "0%s" % c
							c = c[:2].upper()
							return self.systemCaids.get(c, "Unknown")
						return "Crypted"
					return "FTA"
				# EcmTime
				elif self.type == self.ECM_TIME:
					ecmtext = "0.000 s"
					ecm_time = ecm_info.get("ecm time", "")
					if ecm_time:
						if "msec" in ecm_time:
							return "%s" % ecm_time
						elif ecm_time != "nan":
							return "%s s" % ecm_time
						else:
							return ecmtext 
					return ecmtext
				# Reader (Unused, empty)
				elif self.type == self.READER_SOURCE:
					return textvalue
				# ReaderAddress
				elif self.type == self.READER_ADDRESS:
					addresstext = ""
					protocol = ecm_info.get("protocol", "")	# emu oscam
					using = ecm_info.get("using", "")		# emu cccam
					if protocol:
						if protocol == "internal":
							addresstext = "Internal Slot"
						elif protocol in ("smartreader","mouse","serial","pcsc","sc8in1","smargo",):
							addresstext = "USB Reader"
						else:
							addresstext = ecm_info.get("from", "")
					elif using:
						if using == "emu":
							addresstext = "EMU"
						else:
							address = ecm_info.get("address", "")
							if address:
								if address == "/dev/sci0":
									addresstext = "Slot #1"
								elif address == "/dev/sci1":
									addresstext = "Slot #2"
								elif address.find("/dev/ttyUSB") >= 0:
									addresstext = "USB Reader" 
								else:
									addresstext = address 
					return addresstext
				# EmuActive
				elif self.type == self.EMU_NAME:
					return t.readEmuName(t.readEmuActive()).strip()
		return textvalue

	text = property(getText)

	def ecmfile(self):
		ecm = None
		info = {}
		service = self.source.service
		if service:
			frontendInfo = service.frontendInfo()
			if frontendInfo:
				try:
					ecm = open("/tmp/ecm.info", "rb").readlines()
				except:
					pass
			if ecm:
				for line in ecm:
					x = line.lower().find("msec")
					if x != -1:
						info["ecm time"] = line[0:x+4]
					elif line.lower().find("response:") != -1:
						y = line.lower().find("response:")
						if y != -1:
							info["ecm time"] = line[y+9:].strip("\n\r")
					else:
						item = line.split(":", 1)
						if len(item) > 1:
							info[item[0].strip().lower()] = item[1].strip()
						else:
							if not info.has_key("caid"):
								x = line.lower().find("caid")
								if x != -1:
									y = line.find(",")
									if y != -1:
										info["caid"] = line[x+5:y]
		return info 

	def changed(self, what):
		if what[0] == self.CHANGED_SPECIFIC or what[0] == self.CHANGED_POLL:
			self.ecm_info = self.ecmfile()
			Converter.changed(self, what)
	