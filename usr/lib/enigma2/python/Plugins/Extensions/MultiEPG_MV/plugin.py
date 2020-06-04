#!/usr/bin/python
# encoding: utf-8

from Components.config import config
from Plugins.Plugin import PluginDescriptor
from Screens.ChannelSelection import BouquetSelector, SilentBouquetSelector
from ServiceReference import ServiceReference
from enigma import eServiceCenter, eServiceReference, eEnv, getDesktop

from Screens.InfoBar import InfoBar
from time import time, mktime

#for ChannelContextMenu
from Screens.ChannelSelection import ChannelContextMenu
from Tools.BoundFunction import boundFunction
from Components.ChoiceList import ChoiceEntryComponent

from Components.config import config, ConfigInteger, ConfigSubsection, ConfigOnOff, ConfigClock, ConfigDirectory, ConfigNumber, ConfigSelection, ConfigYesNo, ConfigText, ConfigSelectionNumber

import MultiEPG
import MultiEPGSetup

CS_dialog = None
Session = None
Servicelist = None
bouquetSel = None
epg_bouquet = None
bouquet_name = None
activeEventID = None
goNext = False
dlg_stack = [ ]


# Initialize Configuration
config.plugins.multiepgmv = ConfigSubsection()
primetime = 0, 0, 0, 20, 15, 0, 0, 0, -1
primetime_default = mktime(primetime)
config.plugins.multiepgmv.prime_time=ConfigClock(default = primetime_default)
config.plugins.multiepgmv.time_period=ConfigSelectionNumber(60, 300, 60, default = 180)

config.plugins.multiepgmv.timercheck 		= ConfigYesNo(default = False)
config.plugins.multiepgmv.timerdiff			= ConfigSelectionNumber(1, 10, 1, default = 1)
config.plugins.multiepgmv.showpicons 		= ConfigYesNo(default = True)
#config.plugins.multiepgmv.picon_path = ConfigSelection(default = eEnv.resolve('${datadir}/enigma2/picon_50x30/'), choices = [
#				(eEnv.resolve('${datadir}/enigma2/picon_50x30/'), eEnv.resolve('${datadir}/enigma2/picon_50x30')),
#				(eEnv.resolve('${datadir}/enigma2/picon/'), eEnv.resolve('${datadir}/enigma2/picon')),
#				(eEnv.resolve('/data/picon_50x30/'), eEnv.resolve('/data/picon_50x30')),
#				(eEnv.resolve('/data/picon/'), eEnv.resolve('/data/picon')),
#				])
#config.plugins.multiepgmv.timerbanner 		= ConfigYesNo(default = True)
config.plugins.multiepgmv.timerdisplay 		= ConfigSelection(choices=[("False",_("farbig")), ("True",_("als Banner")), ("org",_("e2 Symbole")), ("own",_("eigene Symbole")), ("owntxt",_("<|> Zeichen"))], default = "True")
config.plugins.multiepgmv.useMoreKey 		= ConfigYesNo(default = True)
config.plugins.multiepgmv.extensionsmenu 	= ConfigYesNo(default = True)
config.plugins.multiepgmv.openOnInfokey		= ConfigYesNo(default = False)
config.plugins.multiepgmv.pluginbrowsermenu = ConfigYesNo(default = True)
config.plugins.multiepgmv.fontsizeoffset	= ConfigSelectionNumber(-5, 10, 1, default = 0)
config.plugins.multiepgmv.rowoffset			= ConfigSelectionNumber(-10, 10, 1, default = 0)
config.plugins.multiepgmv.bannerheightoffset = ConfigSelectionNumber(-5, 5, 1, default = 0)

sz_w = getDesktop(0).size().width()
sz_h = getDesktop(0).size().height()
if sz_w == 1920:
	defhide=1320
else:
	defhide=880
config.plugins.multiepgmv.hidePosition = ConfigInteger(default = defhide, limits=(0,-sz_h))

valismultiepg_setup=_("Vali's MultiEPG")+" "+_("Setup")

from Screens.InfoBarGenerics import InfoBarEPG as InfoBarEPG
MultiEPG_MV_openEventViewOri=InfoBarEPG.openEventView

def MultiEPG_MV_openEventView(self):  
	print "[MultiEPG_MV] openEventView ..."
	if config.plugins.multiepgmv.openOnInfokey.value:
		from API import session
		main(session)
	else:
		MultiEPG_MV_openEventViewOri(self)

# rename on startup
InfoBarEPG.openEventView=MultiEPG_MV_openEventView

def zapToService(service):
	if not service is None:
		if Servicelist.getRoot() != epg_bouquet: #already in correct bouquet?
			Servicelist.clearPath()
			if Servicelist.bouquet_root != epg_bouquet:
				Servicelist.enterPath(Servicelist.bouquet_root)
			Servicelist.enterPath(epg_bouquet)
		Servicelist.setCurrentSelection(service) #select the service in Servicelist
		Servicelist.zap()

def openAskBouquet(Session, bouquets, cnt):
	#print " ============= openaksbouquet ==============="
	if cnt > 1: # show bouquet list
		global bouquetSel
		bouquetSel = Session.openWithCallback(closed, BouquetSelector, bouquets, openBouquetEPG, enableWrapAround=True)
		dlg_stack.append(bouquetSel)
	elif cnt == 1:
		if not openBouquetEPG(bouquets[0][1]):
			cleanup()

def cleanup():
	global Session
	Session = None
	global Servicelist
	Servicelist = None
	global bouquet_name
	bouquet_name = None

def closed(ret=False, zap=False):
	closedScreen = dlg_stack.pop()
	global bouquetSel
	if bouquetSel and closedScreen == bouquetSel:
		bouquetSel = None
	dlgs=len(dlg_stack)
	if ret and dlgs > 0: # recursive close wished
		dlg_stack[dlgs-1].close(dlgs > 1)
	if dlgs <= 0:
		cleanup()

	#to close ChannelSelection-Screen (ChannelContextMenu) after close MultiEPG_MV
	from Screens.ChannelSelection import ChannelSelection, ChannelContextMenu
	from Screens.PluginBrowser import PluginBrowser
	global CS_dialog
	if zap and CS_dialog is not None and isinstance(CS_dialog,ChannelSelection):
		CS_dialog.cancel() #close ChannelSelection
	elif zap and CS_dialog is not None and isinstance(CS_dialog,PluginBrowser):
		CS_dialog.close() #close PluginBrowser
	elif CS_dialog is not None and isinstance(CS_dialog,ChannelContextMenu):
		if zap:
			CS_dialog.close(True) #close ChannelContextMenu and ChannelSelection
		else:
			CS_dialog.close() #close only ChannelContextMenu
	CS_dialog = None

def changeBouquetCB(direction, epg):
	#print " ============= changedBouquetCB ==============="
	if bouquetSel:
		if direction > 0:
			bouquetSel.down()
		else:
			bouquetSel.up()
		bouquet = bouquetSel.getCurrent()
		serviceHandler = eServiceCenter.getInstance()
		info = serviceHandler.info(bouquet)
		global bouquet_name
		bouquet_name = info.getName(bouquet)
		services = getBouquetServices(bouquet)
		if len(services):
			global epg_bouquet
			epg_bouquet = bouquet
			epg.setServices(services)

def getBouquetServices(bouquet):  # 4. Schritt - openBouquetEPG <-> init MultiEPG_MV (Screen)
	#print " ============= getBouquetService ==============="
	services = [ ]
	Servicelist = eServiceCenter.getInstance().list(bouquet)
	if not Servicelist is None:
		while True:
			service = Servicelist.getNext()
			if not service.valid(): #check if end of list
				break
			if service.flags & (eServiceReference.isDirectory | eServiceReference.isMarker): #ignore non playable services
				continue
			services.append(ServiceReference(service))
	return services

def openBouquetEPG(bouquet):    # 3. Schritt
	#print " ============= openBouquetEPG ==============="
	services = getBouquetServices(bouquet)
	if len(services):
		global epg_bouquet
		epg_bouquet = bouquet
		#reload(MultiEPG)
		from MultiEPG import MultiEPG_MV
		dlg_stack.append(Session.openWithCallback(closed, MultiEPG_MV, services, zapToService, changeBouquetCB))
		return True
	return False

def openSilent(Servicelist, bouquets, cnt):   # 2. Schritt
	#print " ============= opensilent ==============="
	root = Servicelist.getRoot()
	if cnt > 1: # create bouquet list
		global bouquetSel
		current = 0
		rootstr = root.toCompareString()
		for bouquet in bouquets:
			if bouquet[1].toCompareString() == rootstr:
				break
			current += 1
		if current >= cnt:
			current = 0
		bouquetSel = SilentBouquetSelector(bouquets, True, current)
	if cnt >= 1: # open current bouquet
		if not openBouquetEPG(root):
			cleanup()

def main(session, **kwargs):    # 1. Schritt
	global CS_dialog
	CS_dialog = session.current_dialog
	
	#print " ============= main ==============="
	servicelist = kwargs.get('servicelist', None)
	if servicelist is None:
		if InfoBar is not None:
			InfoBarInstance = InfoBar.instance
			if InfoBarInstance is not None:
				servicelist = InfoBarInstance.servicelist
	global Session
	Session = session
	global Servicelist
	bouquets = None
	Servicelist = servicelist
	if Servicelist is not None:
		bouquets = Servicelist.getBouquetList()
	if bouquets is None:
		cnt = 0
	else:
		cnt = len(bouquets)
	if config.usage.multiepg_ask_bouquet.value:
		openAskBouquet(session, bouquets, cnt)
	else:
		openSilent(servicelist, bouquets, cnt)

#for open from ChannelContextMenu
def openMultiEPGMV_ChannelContextMenu(session, service=None, **kwargs):
	main(session)

#for open from red_key in ChannelSelection
def openMultiEPGMV(session, event, service):
	main(session)

def menu(menuid):
	if menuid == "osd_video_audio":
		return [(valismultiepg_setup, VEPGhandle, "valismultiepg", None)]
	return [ ]

def VEPGhandle(session, **kwargs):
	reload(MultiEPGSetup)
	from MultiEPGSetup import MultiEPGSetup as MEPGSetup
	session.open(MEPGSetup)

def Plugins(**kwargs):
	
	name  = _("MultiEPG Vali Mod")
	descr = _("A graphical EPG")
	
	descriptors = []
	
	if config.plugins.multiepgmv.extensionsmenu.value:
		descriptors.append(PluginDescriptor(name=name, description = descr, where=[PluginDescriptor.WHERE_EXTENSIONSMENU], icon = "plugin.png", fnc = main, needsRestart = False) )
	
	if config.plugins.multiepgmv.pluginbrowsermenu.value:
		descriptors.append(PluginDescriptor(name=name, description = descr, where=[PluginDescriptor.WHERE_PLUGINMENU], icon = "plugin.png", fnc = main, needsRestart = False) )
	
	descriptors.append(PluginDescriptor(name=name, description = descr, where=[PluginDescriptor.WHERE_EVENTINFO], icon = "plugin.png", fnc = main, needsRestart = False) )
	
	#add to ChannelContextMenu
	descriptors.append(PluginDescriptor(name=name, description = name, where=[ PluginDescriptor.WHERE_CHANNEL_CONTEXT_MENU ], fnc = openMultiEPGMV_ChannelContextMenu))
	
	#add to red_key in ChannelSelection
	if hasattr(PluginDescriptor, "WHERE_CHANNEL_SELECTION_RED"):
		descriptors.append(PluginDescriptor(name=name, where = [PluginDescriptor.WHERE_CHANNEL_SELECTION_RED], fnc = openMultiEPGMV) )
	
	return descriptors

