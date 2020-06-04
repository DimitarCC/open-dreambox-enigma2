from Components.config import config
from enigma import eServiceReference, eServiceCenter
import re

class PiconResolver(object):
	@staticmethod
	def getPngName(reference, nameCache, findPicon):
		ref = eServiceReference(reference)
		info = eServiceCenter.getInstance().info(ref)
		sRef = info and info.getName(ref)
		if sRef is not None:
			sRef = sRef.replace('\xc2\x86', '').replace('\xc2\x87', '')	
			sRef = re.sub('[^0-9a-zA-Z]+', '', sRef)
			sRef = sRef.lower()
			pngname = findPicon(sRef)
		else:
			pngname = ""
		x = reference.split(':')
		if len(x) < 11: # skip invalid service references
			return ""
		del x[x[10] and 11 or 10:] # remove name and empty path
		x[1]='0' #replace flags field
		name = '_'.join(x).strip('_')
		pngname2 = nameCache.get(name, "")
		if pngname2 == "":
			pngname2 = findPicon(name)
			if pngname2 == "":
				# lookup without path
				pngname2 = findPicon('_'.join(x[:10]))
				if pngname2 == "":
					if x[0] in ('4097', '8193'): 
						# lookup 1_* instead of 4097_*
						pngname2 = findPicon('1_'+'_'.join(x[1:10]))
					# DVB-T(2)
					elif int(x[0]) == 1 and (int(x[6], 16) & 0xFFFF0000) == 0xEEEE0000:
						x[6] = '{:02X}'.format(0xEEEE0000)
						pngname2 = findPicon('1_'+'_'.join(x[1:10]))
					#if pngname2 == "": # no picon for service found
					#	pngname2 = nameCache.get("default", "")
					#	if pngname2 == "": # no default yet in cache..
					#		pngname2 = findPicon("picon_default")
					#		if pngname2 != "":
					#			nameCache["default"] = pngname2
		if pngname2 != "":
			nameCache[name] = pngname2
			pngname = pngname2
		return pngname
