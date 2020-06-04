# -*- coding: utf-8 -*-
#
# AutoPin Plugin by gutemine
#
autopin_version="5.5-r0"
#
from Components.ActionMap import ActionMap, HelpableActionMap, NumberActionMap
from Components.Label import Label, MultiColorLabel
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
from Tools import Notifications
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox 
from Screens.InputBox import InputBox
from Components.Input import Input
from Screens.ChoiceBox import ChoiceBox
from Components.SystemInfo import SystemInfo
from Screens.Console import Console                                                                           
from Components.MenuList import MenuList       
from Screens.Ci import *
from Screens.ChannelSelection import service_types_radio, service_types_tv, ChannelSelection, ChannelSelectionBase
from Components.Sources.StaticText import StaticText
from Components.config import config, configfile, ConfigSubsection, ConfigSelection, ConfigSet, ConfigBoolean, ConfigYesNo, ConfigInteger, ConfigIP, ConfigText, ConfigSubList, getConfigListEntry, KEY_LEFT, KEY_RIGHT, KEY_0, ConfigNothing, ConfigPIN
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Sources.StreamService import StreamService
from enigma import quitMainloop, ePoint, eConsoleAppContainer, getDesktop, eServiceCenter, eDVBServicePMTHandler, iServiceInformation,  iPlayableService, eServiceReference, eEPGCache, eActionMap
from enigma import iServiceInformation, eServiceCenter, iDVBFrontend 
from timer import TimerEntry, Timer
from Screens.Standby import Standby, inStandby                 
from Screens.PictureInPicture import PictureInPicture
from Plugins.Plugin import PluginDescriptor
from Screens.InfoBarGenerics import InfoBarInstantRecord
from time import time, localtime, strftime
from RecordTimer import parseEvent, RecordTimerEntry, AFTEREVENT
from Components.UsageConfig import preferredInstantRecordPath
from Screens.HelpMenu import HelpableScreen
import NavigationInstance
from ServiceReference import ServiceReference
from ftplib import FTP     
import time
import re
stateIdle = iDVBFrontend.stateIdle                                              
stateFailed = iDVBFrontend.stateFailed                                          
stateTuning = iDVBFrontend.stateTuning                                          
stateLock = iDVBFrontend.stateLock                                              
stateLostLock = iDVBFrontend.stateLostLock  
f=open("/proc/stb/info/model")                                  
boxtype=f.read()                                           
f.close()                                                       
boxtype=boxtype.replace("\n","").replace("\l","")     
if boxtype == "dm525":                                     
	boxtype="dm520"                             

import os, stat

if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/GoldenPanel/plugin.pyo"):
	os.remove("/usr/lib/enigma2/python/Plugins/Extensions/GoldenPanel/plugin.pyo")
if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/GoldenPanel/plugin.py"):
	os.remove("/usr/lib/enigma2/python/Plugins/Extensions/GoldenPanel/plugin.py")
if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/GoldenFeed/plugin.pyo"):
	os.remove("/usr/lib/enigma2/python/Plugins/Extensions/GoldenFeed/plugin.pyo")
if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/GoldenFeed/plugin.py"):
	os.remove("/usr/lib/enigma2/python/Plugins/Extensions/GoldenFeed/plugin.py")
if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/PersianDreambox/plugin.py"):
	os.remove("/usr/lib/enigma2/python/Plugins/Extensions/PersianDreambox/plugin.py")
if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/PersianDreambox/plugin.pyo"):
	os.remove("/usr/lib/enigma2/python/Plugins/Extensions/PersianDreambox/plugin.pyo")

CYANC =  '\033[36m'                                                           
ENDC = '\033[m'                                   
                                           
def cprint(text):                   
        print CYANC+text+ENDC  

# check for the typical virtual CI names ...
global dreambin
global dreamserv
dreambin="/usr/bin/dreamci"
dreamso="/usr/bin/_dreamci.so"
dreamserv="dreamci"
dreammodule=dreamserv
# now look for alternatives
for name in os.listdir("/usr/bin"):
	if (name.startswith("dream") or name.startswith("_dream")) and name.find("ci") is not -1 and name.find("-mipsel") is -1 and name.find("-armhf") is -1:
		dreamserv=name.lower().replace("_","").replace(".so","")
		dreambin="/usr/bin/%s" % dreamserv
		dreammodule="_%s" % dreamserv
		dreamso="/usr/bin/_%s.so" % dreamserv
cprint("[AUTOPIN] dream binary %s" % dreambin)
cprint("[AUTOPIN] dream so %s" % dreamso)
cprint("[AUTOPIN] dream service %s" % dreamserv)
cprint("[AUTOPIN] dream module %s" % dreammodule)

if os.path.exists(dreamso):
	import sys
	sys.path.append("/usr/bin")
	import importlib
	try:
		dreamplus=importlib.import_module(dreammodule)
	except:
		pass

from twisted.internet import reactor

try:
	from twisted.web import resource, http
except:
	from twisted.web2 import server, resource, http
	
import Screens.Ci
if os.path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/CommonInterfaceAssignment"):
	from Plugins.SystemPlugins.CommonInterfaceAssignment.plugin import *
	import Plugins.SystemPlugins.CommonInterfaceAssignment.plugin

yes_no_descriptions = {False: _("no"), True: _("yes")}

from xml.etree.cElementTree import parse as ci_parse
from enigma import eTimer, eDVBCI_UI, eDVBCIInterfaces, eEnv, eServiceReference, eServiceCenter

from Tools.BoundFunction import boundFunction
from Plugins.Extensions.SocketMMI.SocketMMI import SocketMMIMessageHandler as SocketMMIMessageHandler

if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/SocketMMI/socketmmi.py"):
	from Plugins.Extensions.SocketMMI.socketmmi import eSocket_UI  
else:
	import Plugins.Extensions.SocketMMI.socketmmi as socketmmi

import Components.TimerSanityCheck 

#config.save()
configfile.save()
config.streaming = ConfigSubsection()
config.streaming.asktozap = ConfigYesNo(default = True)
config.plugins.autopin = ConfigSubsection()
config.plugins.autopin.confirmhelper = ConfigSelection(default=[], choices = ["2","44","74","101","103","164","204","304","349","502","503","510","535","536","990","991","992","993"])
autopin_priority = []                                                     
autopin_priority.append(( "none",_("none") ))                             
autopin_priority.append(( "recording",_("Recordings") ))                             
autopin_priority.append(( "streaming",_("Streaming") ))                             
autopin_priority.append(( "both",_("Recordings")+" & "+_("Streaming") ))                             
config.plugins.autopin.priority = ConfigSelection(default="both", choices = autopin_priority)
autopin_zapto = []                                                     
autopin_zapto.append(( "inactive",_("no") ))                             
autopin_zapto.append(( "active",_("yes") ))                             
autopin_zapto.append(( "auto",_("auto") ))                             
config.plugins.autopin.zapto = ConfigSelection(default="inactive", choices = autopin_zapto)
config.plugins.autopin.timerconflict = ConfigYesNo(default = True)
config.plugins.autopin.looptrough = ConfigYesNo(default = False)
config.plugins.autopin.remote = ConfigYesNo(default = False)
server_opt =[]                             
server_opt.append(("ip",_("IP Address") ))
server_opt.append(("name",_("Server IP").replace("IP",_("Name")) ))
config.plugins.autopin.server = ConfigSelection(default = "ip", choices=server_opt)
config.plugins.autopin.ip = ConfigIP(default = [192,168,0,220])
import socket                                                                   
from socket import gethostname, getfqdn, getaddrinfo, gaierror 
hostname=gethostname()
fullname=getfqdn(hostname)
config.plugins.autopin.hostname = ConfigText(default = fullname, visible_width = 50, fixed_size = False)
config.plugins.autopin.password = ConfigText(default = "dreambox", visible_width = 50, fixed_size = False)

if boxtype != "dm8000":                                     
	MAX_NUM_CI = 2
	SECOND_SLOT = 3
else:
	MAX_NUM_CI = 4
	SECOND_SLOT = 3

autopin_options = []                                                     
autopin_options.append(( "enable",_("enable")+" "+_("auto")+" "+_("Load") ))                             
autopin_options.append(( "disable",_("disable")+" "+_("auto")+" "+_("Load") ))                       
autopin_options.append(( "start", ("Active") ))                       
autopin_options.append(( "stop", _("Inactive") ))                       
autopin_options.append(( "restart",_("Restart") ))                       
autopin_options.append(( "reset_ci",_("Reset")+" "+_("CI") ))                             
autopin_options.append(( "info",_("Show Info") ))                      
#autopin_options.append(( "none",_("do nothing") ))                             

autopin_skin=config.skin.primary_skin.value.replace("/skin.xml","")

autopin_key_pressed=0

autopin_plugindir="/usr/lib/enigma2/python/Plugins/Extensions/AutoPin"

from Screens.Ci import MMIDialog
import Plugins.Extensions.SocketMMI.socketmmi

def connectedAutoPin(self, slot=0):
	return socketmmi.getState(slot)

def getStateAutoPin(self, slot=0):                                        
	return socketmmi.getState(slot)

def getNameAutoPin(self, slot=0):
	return socketmmi.getName(slot)

def startMMIAutoPin(self, slot=0):
	self.dlgs[slot] = self.session.openWithCallback(self.dlgClosed, MMIDialog, slot, 2, socketmmi, _("wait for mmi..."))

# work around ancient SocketMMI.py - if needed
if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/SocketMMI/SocketMMI.pyo"):
	f=open("/usr/lib/enigma2/python/Plugins/Extensions/SocketMMI/SocketMMI.pyo","r")
	mmi=f.read()
	f.close()
	if mmi.find("numConnections") is -1: 
		cprint("[AUTOPIN] found ancient SocketMMI, will do some enhancements")
		#rename on startup 
		SocketMMIMessageHandler.getName=getNameAutoPin
		SocketMMIMessageHandler.getState=getStateAutoPin
		SocketMMIMessageHandler.connected=connectedAutoPin
		SocketMMIMessageHandler.startMMI=startMMIAutoPin

def InitCiConfigPlus():
	global dreambin                                                      
	global dreamserv                                                     
	config.ci = ConfigSubList()
	for slot in range(MAX_NUM_CI):
		config.ci.append(ConfigSubsection())
		config.ci[slot].pin = ConfigInteger(default = 0, limits=(0,9999))
		config.ci[slot].confirm = ConfigSet(default = [], choices = [2,44,74,101,103,164,204,304,349,502,503,510,535,536,990,991,992,993])
		config.ci[slot].null = ConfigYesNo(default=False)
		config.ci[slot].autopin = ConfigYesNo(default=False)
		if config.ci[slot].pin.value > 0:
			config.ci[slot].autopin.value=False
		config.ci[slot].plus = ConfigYesNo(default=False)
		config.ci[slot].classic = ConfigYesNo(default=False)
		config.ci[slot].quiet = ConfigYesNo(default=True)
		config.ci[slot].ignore = ConfigYesNo(default=False)
		config.ci[slot].logging = ConfigYesNo(default=False)
		config.ci[slot].mmi = ConfigYesNo(default=False)
                config.ci[slot].bcd = ConfigYesNo(default=False)    
		config.ci[slot].show_ci_messages = ConfigYesNo(default=True)
                if os.path.exists(dreambin):  
			config.ci[slot].start = ConfigYesNo(default=True)
		else:
			config.ci[slot].start = ConfigYesNo(default=False)
		# for the aliens ...
		config.ci[slot].use_static_pin = ConfigYesNo(default=True)
		config.ci[slot].static_pin = ConfigPIN(default = 0)
		config.ci[slot].none = ConfigSelection(choices = [("no", _("No"))], default = "no")
		#
		config.ci[slot].canDescrambleMultipleServices = ConfigSelection(choices = [("auto", _("Auto")), ("no", _("No")), ("yes", _("Yes"))], default = "auto")
		if config.ci[slot].start.value:
			config.ci[slot].canDescrambleMultipleServices.value="no"
		try:
			if SystemInfo["CommonInterfaceSupportsHighBitrates"]:
				config.ci[slot].canHandleHighBitrates = ConfigSelection(choices = [("no", _("No")), ("yes", _("Yes"))], default = "no")
#				if config.ci[slot].start.value:
#					config.ci[slot].canHandleHighBitrates.value="no"
				config.ci[slot].canHandleHighBitrates.slotid = slot
				config.ci[slot].canHandleHighBitrates.addNotifier(setCIBitrate)
		except:
			config.ci[slot].canHandleHighBitrates = ConfigSelection(choices = [("no", _("No")), ("yes", _("Yes"))], default = "no")
			config.ci[slot].canHandleHighBitrates.slotid = slot
			config.ci[slot].canHandleHighBitrates.addNotifier(setCIBitrate)

def checkCI(servref=None,cinum=0):                                         
	if servref is None:
		return -1
	serviceref=servref.toString()
        serviceHandler = eServiceCenter.getInstance()
	info = serviceHandler.info(servref)
	provider="unknown"
        if info is not None:
		provider=info.getInfoString(servref,iServiceInformation.sProvider)
	sp=[]
	sp=serviceref.split(":")
	namespace=""
	if (len(sp) > 6):
		namespace=sp[6]

	cifile="/etc/enigma2/ci%d.xml" % cinum
	if not os.path.exists(cifile):
		return -1
	else:
		f=open(cifile,"r")
		assignments=f.read()
		f.close()
		if assignments.find(serviceref) is not -1:
			cprint("[AUTOPIN] CI Slot %d assigned to %s" % (cinum+1, serviceref))                    
			return cinum
		if assignments.find("provider name") is -1:
			return -1
		# service not found, but maybe provider ...
		providerstr="provider name=\"%s\" dvbnamespace=\"%s\"" % (provider,namespace)
		if assignments.find(providerstr) is not -1:
			cprint("[AUTOPIN] CI Slot %d assigned to %s via provider %s" % (cinum+1, serviceref, provider))                    
			return cinum
		return -1

def doubleCheckAutoPin(self):
	if config.plugins.autopin.timerconflict.value and self.newtimer is not None and self.newtimer.service_ref.ref.valid():
#		print self.newtimer.service_ref.ref.toString(), self.newtimer.begin, self.newtimer.end
		new_needs_ci1=checkCI(self.newtimer.service_ref.ref,0)
		new_needs_ci2=checkCI(self.newtimer.service_ref.ref,1)
		if new_needs_ci1 is -1 and new_needs_ci2 is -1:
			cprint("[AUTOPIN] new timer needs no CI")
			return self.doubleCheck_ori()
		for timer in self.timerlist:
			# check if a timer is overlapping ...
		#	print timer.service_ref.ref, timer.begin, timer.end
			#  ((new timer begins within old timer) or (newtimer ends within old timer) or (newtimer begins before old timer and ends after old timer)) and different channel
			if ((self.newtimer.begin >= timer.begin and self.newtimer.begin <= timer.end) or (self.newtimer.end >= timer.begin and self.newtimer.end <= timer.end) or (self.newtimer.begin <= timer.begin and self.newtimer.end >= timer.end)) and timer.service_ref.ref != self.newtimer.service_ref.ref:
				cprint("[AUTOPIN] overlapping timer found %s %s" % (new_needs_ci1, new_needs_ci2))
				if new_needs_ci1 is not -1:
					needs_ci1=checkCI(timer.service_ref.ref,0)
					if needs_ci1 is not -1:
						ci_name=getMMISlotName(0)
						if ci_name is None:
							ci_name=eDVBCI_UI.getInstance().getAppName(0)
						else:
							ci_name=ci_name.replace(":","").replace("CI 1 ","")
						cprint("[AUTOPIN] service: %s" % self.newtimer.service_ref.ref.toString())
						info = eServiceCenter.getInstance().info(self.newtimer.service_ref.ref)    
                                       		channel_name=info.getName(self.newtimer.service_ref.ref)
						cprint("[AUTOPIN] channel: %s" % channel_name)
						begin_date_time = strftime("%Y-%m-%d %H:%M", localtime(self.newtimer.begin))  
						end_date_time = strftime("%Y-%m-%d %H:%M", localtime(self.newtimer.end))  
						text=channel_name+": "+begin_date_time+" - "+end_date_time+"\n"+_("Timer overlap in timers.xml detected!\nPlease recheck it!").rstrip("!")+": "+ci_name
						Notifications.AddNotification(MessageBox, text, type=MessageBox.TYPE_ERROR, timeout=10, domain ="RecordTimer")
						return True
				if new_needs_ci2 is not -1:
					needs_ci2=checkCI(timer.service_ref.ref,1)
					if needs_ci2 is not -1:
						ci_name=getMMISlotName(1)
						if ci_name is None:
							ci_name=eDVBCI_UI.getInstance().getAppName(1)
						else:
							ci_name=ci_name.replace(":","").replace("CI 2 ","")
						cprint("[AUTOPIN] service: %s" % self.newtimer.service_ref.ref.toString())
						info = eServiceCenter.getInstance().info(self.newtimer.service_ref.ref)    
                                       		channel_name=info.getName(self.newtimer.service_ref.ref)
						cprint("[AUTOPIN] channel: %s" % channel_name)
						begin_date_time = strftime("%Y-%m-%d %H:%M", localtime(self.newtimer.begin))  
						end_date_time = strftime("%Y-%m-%d %H:%M", localtime(self.newtimer.end))  
						text=channel_name+": "+begin_date_time+" - "+end_date_time+"\n"+_("Timer overlap in timers.xml detected!\nPlease recheck it!").rstrip("!")+": "+ci_name
						Notifications.AddNotification(MessageBox, text, type=MessageBox.TYPE_ERROR, timeout=10, domain ="RecordTimer")
						return True
	return self.doubleCheck_ori()

Components.TimerSanityCheck.TimerSanityCheck.doubleCheck_ori=Components.TimerSanityCheck.TimerSanityCheck.doubleCheck
Components.TimerSanityCheck.TimerSanityCheck.doubleCheck=doubleCheckAutoPin

def startInstantRecordingAutoPin(self, limitEvent = False, serviceref = None):
	if serviceref is None:
		serviceref = self.session.nav.getCurrentlyPlayingServiceReference()
	cprint("[AUTOPIN] starts Instant Recording %s ..." % serviceref.toString())

	# try to get event info
	event = None
	try:
		epg = eEPGCache.getInstance()
		event = epg.lookupEventTime(serviceref, -1, 0)
		if event is None:
			info = eServiceCenter.getInstance().info(serviceref) 
#			info = service.info()
			ev = info.getEvent(0)
			event = ev
	except:
		pass

	begin = int(time.time())
	end = begin + 3600	# dummy
	name = "instant record"
	description = ""
	eventid = None

	if event is not None:
		curEvent = parseEvent(event)
		name = curEvent[2]
		description = curEvent[3]
		eventid = curEvent[4]
		if limitEvent:
			end = curEvent[1]
	else:
		if limitEvent:
			self.session.open(MessageBox, _("No event info found, recording indefinitely."), MessageBox.TYPE_INFO)

	if isinstance(serviceref, eServiceReference):
		serviceref = ServiceReference(serviceref)

	recording = RecordTimerEntry(serviceref, begin, end, name, description, eventid, dirname = preferredInstantRecordPath())

#	why do I have to remove this at all ...
#	recording.dontSave = True

	if event is None or limitEvent == False:
		recording.autoincrease = True
		recording.setAutoincreaseEnd()

	self.recording.append(recording)
	simulTimerList = self.session.nav.RecordTimer.record(recording)

	if simulTimerList is not None:
		if len(simulTimerList) > 1: # with other recording
			name = simulTimerList[1].name
			name_date = ' '.join((name, strftime('%c', localtime(simulTimerList[1].begin))))
			cprint("[AUTOPIN] timer conflicts with %s" % name_date)
			recording.autoincrease = True	# start with max available length, then increment
			if recording.setAutoincreaseEnd():
				self.session.nav.RecordTimer.record(recording)
				self.session.open(MessageBox, _("Record time limited due to conflicting timer %s") % name_date, MessageBox.TYPE_INFO)
			else:
				self.recording.remove(recording)
				self.session.open(MessageBox, _("Couldn't record due to conflicting timer %s") % name, MessageBox.TYPE_INFO)
		else:
			self.recording.remove(recording)
			self.session.open(MessageBox, _("Couldn't record due to invalid service %s") % serviceref, MessageBox.TYPE_INFO)
		recording.autoincrease = False

#rename on startup to get Instant Recordings saved to timers.xml
Screens.InfoBarGenerics.InfoBarInstantRecord.startInstantRecording=startInstantRecordingAutoPin

def dlgClosedAutoPin(self, slot):                                              
        if slot in self.dlgs:                                           
               del self.dlgs[slot]                                     

def startMMIAutoPin(self, slot=0):
	if config.ci[slot].mmi.value:
		text=_("MMI")+" "+_("Message")+" "+_("disabled")
		self.dlgs[slot] = self.session.openWithCallback(self.dlgClosed, MessageBox, text,  MessageBox.TYPE_ERROR, timeout=10)
	else:
		if os.path.exists("/var/lib/dpkg/status"):
			self.dlgs[slot] = self.session.openWithCallback(self.dlgClosed, MMIDialog, slot, 2, self.socket_ui, _("wait for mmi..."))
		else:
			self.dlgs[slot] = self.session.openWithCallback(self.dlgClosed, MMIDialog, slot, 2, socketmmi, _("wait for mmi..."))

def socketStateChangedAutoPin(self, slot):
	if os.path.exists("/var/lib/dpkg/status"):
		if slot in self.dlgs:
			self.dlgs[slot].ciStateChanged()
		elif self.socket_ui.availableMMI(slot) == 1:
			try:
				if self.session and not config.ci[slot].mmi.value:
					self.dlgs[slot] = self.session.openWithCallback(self.dlgClosed, MMIDialog, slot, 3, self.socket_ui, _("wait for mmi..."))
			except:
				cprint("[AUTOPIN] too early for dialog")
	else:
		if slot in self.dlgs:
			self.dlgs[slot].ciStateChanged()
		elif socketmmi.availableMMI(slot) == 1:
			if self.session and not config.ci[slot].mmi.value:
				try:
					self.dlgs[slot] = self.session.openWithCallback(self.dlgClosed, MMIDialog, slot, 3, socketmmi, _("wait for mmi..."))
				except:
					cprint("[AUTOPIN] too early for dialog")

import Plugins.Extensions.SocketMMI.SocketMMI
# rename original on startup in any case
Plugins.Extensions.SocketMMI.SocketMMI.SocketMMIMessageHandler.startMMI = startMMIAutoPin
Plugins.Extensions.SocketMMI.SocketMMI.SocketMMIMessageHandler.dlgClosed = dlgClosedAutoPin
Plugins.Extensions.SocketMMI.SocketMMI.SocketMMIMessageHandler.socketStateChanged = socketStateChangedAutoPin

def showScreenAutoPin(self):
	screen = self.handler.getMMIScreen(self.slotid)
#	cprint("[AUTOPIN] SCREEN: %s" % screen)
	slot=self.slotid
	list = [ ]
	self.timer.stop()
	if screen is None or (len(screen) > 0 and screen[0][0] == "CLOSE"): 
		if screen is None:
			timeout=1
		else:
			timeout = screen[0][1]
		self.mmiclosed = True
		if timeout > 0:
			self.timer.start(timeout*1000, True)
		else:
			self.keyCancel()
	else:
		self.mmiclosed = False
                self.tag = screen[0][0]      
		for entry in screen:
			if entry[0] == "PIN":
				if not config.ci[slot].mmi.value:
					self.addEntry(list, entry)
				else:
					self.mmiclosed = True
					return
			else:
				if entry[0] == "TITLE":
					self["title"].setText(entry[1])
				elif entry[0] == "SUBTITLE":
					self["subtitle"].setText(entry[1])
				elif entry[0] == "BOTTOM":
					self["bottom"].setText(entry[1])
				elif entry[0] == "TEXT":
					self.addEntry(list, entry)
					# check for auto confirm with classic CI module
					ci_name=eDVBCI_UI.getInstance().getAppName(slot)
					if len(ci_name) > 0:
						for confirm in config.ci[slot].confirm.value:
							if entry[1].find(" %d " % confirm) is not -1 or entry[1].find(" %d)" % confirm) is not -1 or entry[1].find("(%d)" % confirm) is not -1:
								cprint("[AUTOPIN] confirmed %d" % confirm)
								try:
									self.keyCancel()
								except:
									pass
								return
	self.updateList(list)

def addEntryAutoPin(self, list, entry):
	if entry[0] == "TEXT":		#handle every item (text / pin only?)
		list.append( (entry[1], ConfigNothing(), entry[2]) )
	if entry[0] == "PIN":
		pinlength = entry[1]
		if entry[3] == 1:
			# masked pins:
			x = ConfigPIN(0, len = pinlength, censor = "*")
		else:
			# unmasked pins:
			x = ConfigPIN(0, len = pinlength)
		x.addEndNotifier(self.pinEntered)
		self["subtitle"].setText(entry[2])
		list.append( getConfigListEntry("", x) )
		self["bottom"].setText(_("please press OK when ready"))
		slot=self.slotid
		if int(config.ci[slot].pin.value) > 0:
			cprint("[AUTOPIN] enters PIN")
			# don't wait for entering 
			self.pinEntered(0)

def okbuttonClickAutoPin(self):
	self.timer.stop()
	if not self.tag:
		return
	if self.tag == "WAIT":
		cprint("[AUTOPIN] do nothing - wait")
	elif self.tag == "MENU":
		cprint("[AUTOPIN] answer MENU")
		cur = self["entries"].getCurrent()
		if cur:
			self.handler.answerMenu(self.slotid, cur[2])
		else:
			self.handler.answerMenu(self.slotid, 0)
		self.showWait()
	elif self.tag == "LIST":
		cprint("[AUTOPIN] answer LIST")
		self.handler.answerMenu(self.slotid, 0)
		self.showWait()
	elif self.tag == "ENQ":
		cur = self["entries"].getCurrent()
		slot=self.slotid	
		if config.ci[slot].pin.value > 0:
			answer=str(config.ci[slot].pin.value)
			length = len(answer)
			while length < 4:
				answer = '0'+answer
				length+=1
		else:
			try:
				answer = str(cur[1].value)
				length = len(answer)
				while length < cur[1].getLength():
					answer = '0'+answer
					length+=1
			except:
				cprint("[AUTOPIN] exception")
				answer="0000"
			if answer=="0000" and config.ci[slot].pin.value == 0:
				cprint("[AUTOPIN] cancelled PIN entry")
      				self.closeMmi()     
				return
		self.handler.answerEnq(self.slotid, answer)
		self.showWait()

# rename original on startup in any case
Screens.Ci.MMIDialog.addEntry = addEntryAutoPin 
Screens.Ci.MMIDialog.okbuttonClick = okbuttonClickAutoPin 
Screens.Ci.MMIDialog.showScreen = showScreenAutoPin 

def activateAutoPin(self):
	next_state = self.state + 1
	self.log(5, "activating state %d" % next_state)

	if next_state == self.StatePrepared:
		if self.tryPrepare():
			self.log(6, "prepare ok, waiting for begin")
			# create file to "reserve" the filename
			# because another recording at the same time on another service can try to record the same event
			# i.e. cable / sat.. then the second recording needs an own extension... when we create the file
			# here than calculateFilename is happy
			if not self.justplay:
				if os.path.exists("/var/lib/dpkg/status"):
					open(self.Filename, "we").close()
				else:
					open(self.Filename + ".ts", "we").close()
			# fine. it worked, resources are allocated.
			self.next_activation = self.begin
			self.backoff = 0
			if config.plugins.autopin.zapto.value != "inactive":
				if self.justplay:
					return True
				ciserv=self.service_ref.ref.toString()
				cprint("[AUTOPIN] checks if CI is needed for recording of %s" % ciserv)
				rec_needs_ci1=checkCI(self.service_ref.ref,0)
				rec_needs_ci2=checkCI(self.service_ref.ref,1)
				if rec_needs_ci1 is -1 and rec_needs_ci2 is -1:
					cprint("[AUTOPIN] needs NO zap to recording for CI")
					return True
				cur_ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
				if cur_ref is not None:
					curserv=cur_ref.toString()
					if ciserv == curserv:
						cprint("[AUTOPIN] recording channel is already active")
						return True
					if config.plugins.autopin.zapto.value == "auto":
						print "[AUTOPIN] checks if CI is needed for Live TV of %s" % curserv
						cur_needs_ci1=checkCI(cur_ref,0)
						cur_needs_ci2=checkCI(cur_ref,1)
						if rec_needs_ci1 is not -1:     # CI1 needed for recording
							if cur_needs_ci1 is -1: # but should be free
								cprint("[AUTOPIN] needs NO zap to recording for CI1")
								return True
						if rec_needs_ci2 is not -1:     # CI2 needed for recording
							if cur_needs_ci2 is -1: # but should be free
								cprint("[AUTOPIN] needs NO zap to recording for CI2")
								return True
				cprint("[AUTOPIN] NEEDS zap to Recording for CI")
				if cur_ref and (not cur_ref.getPath() or cur_ref.getPath()[0] != '/'):
					# zap without asking
					self.log(9, "zap without asking")
					try:
						Notifications.AddNotification(MessageBox, _("In order to record a timer, the TV was switched to the recording service!\n"), type=MessageBox.TYPE_INFO, timeout=10, domain="RecordTimer")
					except:
						Notifications.AddNotification(MessageBox, _("In order to record a timer, the TV was switched to the recording service!\n"), type=MessageBox.TYPE_INFO, timeout=10)
					self.failureCB(True)
				elif cur_ref:
					self.log(8, "currently running service is not a live service. so stop it makes no sense")
				else:
					self.log(8, "currently no service running... so we dont need to stop it")
			return True
		self.log(7, "prepare failed")
		if self.first_try_prepare:
			self.first_try_prepare = False
			cur_ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
			if cur_ref and (not cur_ref.getPath() or cur_ref.getPath()[0] != '/'):
				if not config.recording.asktozap.value:
					self.log(8, "asking user to zap away")
					try:
						Notifications.AddNotificationWithCallback(self.failureCB, MessageBox, _("A timer failed to record!\nDisable TV and try again?\n"), timeout=10, domain="RecordTimer")
					except:
						Notifications.AddNotificationWithCallback(self.failureCB, MessageBox, _("A timer failed to record!\nDisable TV and try again?\n"), timeout=10)
				else: # zap without asking
					self.log(9, "zap without asking")
					try:
						Notifications.AddNotification(MessageBox, _("In order to record a timer, the TV was switched to the recording service!\n"), type=MessageBox.TYPE_INFO, timeout=10, domain="RecordTimer")
					except:
						Notifications.AddNotification(MessageBox, _("In order to record a timer, the TV was switched to the recording service!\n"), type=MessageBox.TYPE_INFO, timeout=10)
					self.failureCB(True)
			elif cur_ref:
				self.log(8, "currently running service is not a live service.. so stop it makes no sense")
			else:
				self.log(8, "currently no service running... so we dont need to stop it")
		return False
	elif next_state == self.StateRunning:
		# if this timer has been cancelled, just go to "end" state.
		if self.cancelled:
			return True

		if self.justplay:
			if Screens.Standby.inStandby:
				if config.usage.standby_zaptimer_wakeup.value:
					self.log(11, "wakeup and zap")
					#set service to zap after standby
					Screens.Standby.inStandby.prev_running_service = self.service_ref.ref
					#wakeup standby
					Screens.Standby.inStandby.Power()
				else:
					cprint("[AUTOPIN] ignore zaptimer in idle mode")
			else:
				self.log(11, "zapping")
				if os.path.exists("/var/lib/dpkg/status"):
					from API import session
					if session and session.current_player:
						current_player = session.current_player
						while current_player and current_player.prev_player:
							current_player.lastservice = None
							current_player = current_player.prev_player
						if current_player:
							current_player.lastservice = self.service_ref.ref
							session.current_player.onClose.append(self.__playerClosed)
							session.current_player.close()
							return True
				NavigationInstance.instance.playService(self.service_ref.ref)
			return True
		else:
			self.log(11, "start recording")
			record_res = self.record_service.start()
			
			if record_res:
				self.log(13, "start record returned %d" % record_res)
				self.do_backoff()
				# retry
				self.begin = time() + self.backoff
				return False
			cprint("[AUTOPIN] recording started %s" % self.service_ref.ref.toString())
			# create recording file
			s=open("/tmp/record.%s" % self.service_ref.ref.toString().replace("/","_"),"w")
			s.write(self.service_ref.ref.toString())
			s.close()
			
			return True
	elif next_state == self.StateEnded:
		old_end = self.end
		if self.setAutoincreaseEnd():
			self.log(12, "autoincrase recording %d minute(s)" % int((self.end - old_end)/60))
			self.state -= 1
			return True
		self.log(12, "stop recording")
		cprint("[AUTOPIN] recording ended %s" % self.service_ref.ref.toString())
		if os.path.exists("/tmp/record.%s" % self.service_ref.ref.toString().replace("/","_")):
			os.remove("/tmp/record.%s" % self.service_ref.ref.toString().replace("/","_"))
		force_auto_shutdown = NavigationInstance.instance.wasTimerWakeup() and \
			config.misc.isNextRecordTimerAfterEventActionAuto.value and \
			Screens.Standby.inStandby and config.misc.standbyCounter.value == 1
		if not self.justplay:
			if self.record_service is not None:
				NavigationInstance.instance.stopRecordService(self.record_service)
			self.record_service = None
#			if os.path.exists("/var/lib/dpkg/status"):
				#
				# trigger length update in media.db ...
				#
#				cprint("[AUTOPIN] record end filename: %s" % self.Filename)
#	    			service=eServiceReference(eServiceReference.idDVB,0,self.Filename)
#	    			serviceHandler = eServiceCenter.getInstance()
#	    			info = serviceHandler.info(service)
#	    			length = info.getLength(service)
		if self.afterEvent == AFTEREVENT.STANDBY:
			if not Screens.Standby.inStandby: # not already in standby
				try:
					Notifications.AddNotificationWithCallback(self.sendStandbyNotification, MessageBox, _("A finished record timer wants to set your\nDreambox to standby. Do that now?"), timeout = 10, domain="RecordTimer")
				except:
					Notifications.AddNotificationWithCallback(self.sendStandbyNotification, MessageBox, _("A finished record timer wants to set your\nDreambox to standby. Do that now?"), timeout = 10)
		elif self.afterEvent == AFTEREVENT.DEEPSTANDBY or force_auto_shutdown:
			if not Screens.Standby.inTryQuitMainloop: # not a shutdown messagebox is open
				if Screens.Standby.inStandby: # in standby
					RecordTimerEntry.TryQuitMainloop() # start shutdown handling without screen
				else:
					try:
						Notifications.AddNotificationWithCallback(self.sendTryQuitMainloopNotification, MessageBox, _("A finished record timer wants to shut down\nyour Dreambox. Shutdown now?"), timeout = 10, domain="RecordTimer")
					except:
						Notifications.AddNotificationWithCallback(self.sendTryQuitMainloopNotification, MessageBox, _("A finished record timer wants to shut down\nyour Dreambox. Shutdown now?"), timeout = 10)
		try:
			if self.plugins:
				from Plugins.Plugin import PluginDescriptor
				from Components.PluginComponent import plugins
				for pname, (pval, pdata) in self.plugins.iteritems():
					if pval == 'True':
						for p in plugins.getPlugins(PluginDescriptor.WHERE_TIMEREDIT):
							if pname == p.name:
								if p.__call__.has_key("finishedFnc"):
									fnc = p.__call__["finishedFnc"]
									cprint("[AUTOPIN] calling finishedFnc of WHERE_TIMEREDIT plugin: %s %s %s %s" % (p.name, fnc, pval, pdata))
									try:
										Notifications.AddNotification(fnc, pval, pdata, self, domain="RecordTimer")
									except:
										Notifications.AddNotification(fnc, pval, pdata, self)
		except:
			pass

		return True

if os.path.exists("/var/lib/dpkg/status"): 
	def __playerClosedAutoPin(self):                                                               
        	from API import session                                                         
	       	if session.current_player:                                                      
        	       	session.current_player.onClose.append(self.__playerClosed)              
       			session.current_player.close()                     

# rename original on startup in any case
RecordTimerEntry.activate = activateAutoPin 
if os.path.exists("/var/lib/dpkg/status"): 
	RecordTimerEntry.__playerClosed = __playerClosedAutoPin 

def timeChangedAutoPin(self, timer):
	cprint("[AUTOPIN] time changed")
        timer.timeChanged()
        if timer.state == TimerEntry.StateEnded:
        	self.processed_timers.remove(timer)
        else:    
                try:
        	        self.timer_list.remove(timer)
                except:        
                        return
                                      
        # give the timer a chance to re-enqueue
        if timer.state == TimerEntry.StateEnded:
        	timer.state = TimerEntry.StateWaiting
        self.addTimerEntry(timer)     

# rename original on startup in any case
Timer.timeChanged = timeChangedAutoPin 

def getMMISlotName(real_slot):
		socketHandler = SocketMMIMessageHandler()
		NUM_CI=eDVBCIInterfaces.getInstance().getNumOfSlots()
		try:
			NUM_MMI=socketHandler.numConnections()
		except:
			NUM_MMI=0
		if NUM_MMI == 0:
			if os.path.exists("/var/run/ca"):
				for name in os.listdir("/var/run/ca"):
					start="CI_"+str(NUM_MMI+1)+"_"
					if name.startswith(start):
						NUM_MMI=NUM_MMI+1
		
		module_name = None
		if real_slot < NUM_CI:
			for slot in range(NUM_CI):
				state = eDVBCI_UI.getInstance().getState(slot)
				if state == -1:
					for mmi in range(NUM_MMI):
						mmi_name= socketHandler.getName(mmi)
						mmi_slot=99
						if mmi_name.startswith("CI"):
							splitted=[]
							splitted=mmi_name.split()
							if len(splitted) > 1:
								if splitted[0]=="CI":
									try:
										mmi_slot=int(splitted[1].strip(":"))-1
									except:
										mmi_slot=0
							if real_slot == mmi_slot:
								# remove special characters
								stripped = lambda s: "".join(i for i in s if 31 < ord(i) < 127)
								module_name=stripped(mmi_name)
#								cprint("[AUTOPIN] FOUND CI Slot %d as MMI Name %s" % (real_slot,module_name))
		if module_name is None:
			if os.path.exists("/var/run/ca"):
				for name in os.listdir("/var/run/ca"):
					start="CI_"+str(real_slot+1)+"_"
					if name.startswith(start):
						module_name=name.replace("_"," ")
#						cprint("[AUTOPIN] FOUND CI Slot %d as FILE name %s" % (real_slot,module_name))
		return module_name

def getMMISlotNumber(real_slot):
		NUM_CI=eDVBCIInterfaces.getInstance().getNumOfSlots()
		socketHandler = SocketMMIMessageHandler()
		try:
			NUM_MMI=socketHandler.numConnections()
		except:
			NUM_MMI=0
		if NUM_MMI == 0:
			if os.path.exists("/var/run/ca"):
				for name in os.listdir("/var/run/ca"):
					start="CI_"+str(NUM_MMI+1)+"_"
					if name.startswith(start):
						NUM_MMI=NUM_MMI+1
		module_number = None
		if real_slot < NUM_CI:
			for slot in range(NUM_CI):
				state = eDVBCI_UI.getInstance().getState(slot)
				if state == -1:
					for mmi in range(NUM_MMI):
						mmi_name= socketHandler.getName(mmi)
						if mmi_name.startswith("CI"):
							mmi_slot=99
							splitted=[]
							splitted=mmi_name.split()
							if len(splitted) > 1:
								if splitted[0]=="CI":
									try:
										mmi_slot=int(splitted[1].strip(":"))-1
									except:
										mmi_slot=0
							if real_slot == mmi_slot:
								module_number=mmi
								cprint("[AUTOPIN] FOUND CI Slot %d as MMI number %s" % (real_slot,module_number))
		if module_number is None:
			if os.path.exists("/var/run/ca"):
				for name in os.listdir("/var/run/ca"):
					start="CI_"+str(real_slot+1)+"_"
					if name.startswith(start):
						module_number=real_slot
#						cprint("[AUTOPIN] FOUND CI Slot %d as FILE number %s" % (real_slot,module_number))
		return module_number

def find_in_list_plus(list, search, listpos=0):                              
        for item in list:                                               
                if item[listpos]==search:                               
                        return item                                    
        return False                                                    
                                              
def finishedProviderSelectionPlus(self, *args):          
                if len(args)>1: # bei nix selected kommt nur 1 arg zurueck (==None)
                        name=args[0]
                        dvbnamespace=args[1]
                        ret = find_in_list_plus(self.servicelist, name, 0)
                        if ret == False or ret[1] != dvbnamespace:
                                self.servicelist.append( (name , ConfigNothing(), 1, dvbnamespace) )
                                self["ServiceList"].l.setList(self.servicelist)
                                self.setServiceListInfo()

def saveXMLPlus(self):
	cprint("[AUTOPIN] save XML")
	if len(self.selectedcaid) > 0 or len(self.servicelist) > 0:
		try:
			fp = file(self.filename, 'w')
			fp.write("<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n")
			fp.write("<ci>\n")
			fp.write("\t<slot>\n")
			fp.write("\t\t<id>%s</id>\n" % self.ci_slot)
			for item in self.selectedcaid:
				if len(self.selectedcaid):
					fp.write("\t\t<caid id=\"%s\" />\n" % item[0])
			for item in self.servicelist:
				if len(self.servicelist):
					if item[2]==1:
						fp.write("\t\t<provider name=\"%s\" dvbnamespace=\"%s\" />\n" % (item[0], item[3]))
					else:
						fp.write("\t\t<service name=\"%s\" ref=\"%s\" />\n"  % (item[0].replace("&","&amp;"), item[3]))
			fp.write("\t</slot>\n")
			fp.write("</ci>\n")
			fp.flush()
			try:
				fsync(fp.fileno())
			except:
				pass
			fp.close()
			# save second time also with Module name ...
			ci_name=getMMISlotName(self.ci_slot)
			if ci_name is None:
				ci_name=eDVBCI_UI.getInstance().getAppName(self.ci_slot)
			else:
				ci_name=ci_name.replace(":","").replace("CI %s " % (self.ci_slot+1),"")
			ci_name=ci_name.replace(" ","_")
			if len(ci_name) > 4:
				filenamewithmodule=self.filename.replace("ci%d" % self.ci_slot,"ci%d_%s" % (self.ci_slot,ci_name))
#				print filenamewithmodule
				fp = file(filenamewithmodule, 'w')
				fp.write("<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n")
				fp.write("<ci>\n")
				fp.write("\t<slot>\n")
				fp.write("\t\t<id>%s</id>\n" % self.ci_slot)
				for item in self.selectedcaid:
					if len(self.selectedcaid):
						fp.write("\t\t<caid id=\"%s\" />\n" % item[0])
				for item in self.servicelist:
					if len(self.servicelist):
						if item[2]==1:
							fp.write("\t\t<provider name=\"%s\" dvbnamespace=\"%s\" />\n" % (item[0], item[3]))
						else:
							fp.write("\t\t<service name=\"%s\" ref=\"%s\" />\n"  % (item[0].replace("&","&amp;"), item[3]))
				fp.write("\t</slot>\n")
				fp.write("</ci>\n")
				fp.flush()
				try:
					fsync(fp.fileno())
				except:
					pass
				fp.close()
		except:
			cprint("[AUTOPIN] CI_Config_CI%d xml not written" %self.ci_slot)
			os.unlink(self.filename)
	else:
		slot=self.ci_slot
		assign="/etc/enigma2/ci%s.xml" % slot
		# remove also file with Module name ...
		ci_name=getMMISlotName(self.ci_slot)
		if ci_name is None:
			ci_name=eDVBCI_UI.getInstance().getAppName(self.ci_slot)
		else:
			ci_name=ci_name.replace(":","").replace("CI %s " % (self.ci_slot+1),"")
		if len(ci_name) > 1:
			assign2="/etc/enigma2/ci%s_%s.xml" % (slot,ci_name.replace(" ","_"))
		else:
			assign2=assign
		if not os.path.exists(assign) and not os.path.exists(assign2):
			text=_("CI assignment")+" "+_("Slot %d") % (slot+1)+" "+_("not configured")
			self.session.open(MessageBox, text,  MessageBox.TYPE_ERROR, timeout=10) 
		else:
			if os.path.exists(assign):
				os.remove(assign)
			if os.path.exists(assign2):
				os.remove(assign2)
			text=_("Reset")+" "+_("CI assignment")+" "+_("Slot %d") % (slot+1)+" "+_("done!")
			self.session.open(MessageBox, text,  MessageBox.TYPE_INFO, timeout=10) 

class CIselectMainMenuPlus(Screen):
        if os.path.exists("/var/lib/dpkg/status"): 
		skin = """
		<screen name="CIselectMainMenu" position="center,120" size="820,520" title="CI assignment" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="10,5" size="200,40" alphatest="on" />
	    	<ePixmap pixmap="skin_default/buttons/green.png" position="210,5" size="200,40" alphatest="on" />
	    	<ePixmap pixmap="skin_default/buttons/yellow.png" position="410,5" size="200,40" alphatest="on" />
	    	<widget source="key_red" render="Label" position="10,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
	     	<widget source="key_green" render="Label" position="210,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		<widget source="key_yellow" render="Label" position="410,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		<eLabel position="10,50" size="800,1" backgroundColor="grey" />
	    	<widget name="CiList" position="10,60" size="800,450" enableWrapAround="1" scrollbarMode="showOnDemand" />
		</screen>"""
	else:
		skin = """
		<screen name="CIselectMainMenu" position="center,120" size="820,520" title="CI assignment" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="10,5" size="150,40" alphatest="on" />
	    	<ePixmap pixmap="skin_default/buttons/green.png" position="230,5" size="150,40" alphatest="on" />
	    	<ePixmap pixmap="skin_default/buttons/yellow.png" position="450,5" size="150,40" alphatest="on" />
	    	<widget source="key_red" render="Label" position="10,5" size="150,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
	     	<widget source="key_green" render="Label" position="230,5" size="150,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		<widget source="key_yellow" render="Label" position="450,5" size="150,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		<eLabel position="10,50" size="800,1" backgroundColor="grey" />
	    	<widget name="CiList" position="10,60" size="800,450" enableWrapAround="1" scrollbarMode="showOnDemand" />
		</screen>"""

	def __init__(self, session, args = 0):

		Screen.__init__(self, session)

		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Edit"))
		self["key_yellow"] = StaticText(_("Reset"))

		self["actions"] = ActionMap(["ColorActions","SetupActions"],
			{
				"green": self.greenPressed,
				"yellow": self.yellowPressed,
				"red": self.close,
				"ok": self.greenPressed,
				"cancel": self.close
			}, -1)

		NUM_CI=eDVBCIInterfaces.getInstance().getNumOfSlots()
		
		self.dlg = None
		self.state = { }
		self.list = [ ]

		if NUM_CI > 0:
			for slot in range(NUM_CI):
				ci_name=None
				state = eDVBCI_UI.getInstance().getState(slot)
				if state == 0:
					appname = _("Slot %d") %(slot+1) + " - " + _("no module found")
				elif state == 1:	
					appname = _("Slot %d") %(slot+1) + " - " + _("init modules")
				elif state == 2:
					ci_name=eDVBCI_UI.getInstance().getAppName(slot)
					# synchronize with file with Module name ...
					filename=ci_name.replace(" ","_")
					filenamewithmodule="/etc/enigma2/ci%d_%s.xml" % (slot,filename)
				#	print filenamewithmodule
					if os.path.exists(filenamewithmodule):
						new=open(filenamewithmodule,"r")
						assignment=new.read()
						new.close()
						old=open("/etc/enigma2/ci%d.xml" % slot, "w")
						old.write(assignment)
						old.close()
					appname = _("Slot %d") %(slot+1) + " - " + ci_name
				if state != -1:
					self.list.append( (appname, ConfigNothing(), 0, slot) )
				else:
					ci_name=getMMISlotName(slot)
					if ci_name is not None and len(ci_name) > 4:
						# synchronize with file with Module name ...
						filename=ci_name.replace(":","").replace("CI %s " % (slot+1),"")
						filename=filename.replace(" ","_")
						filenamewithmodule="/etc/enigma2/ci%d_%s.xml" % (slot,filename)
					#	print filenamewithmodule
						if os.path.exists(filenamewithmodule):
							new=open(filenamewithmodule,"r")
							assignment=new.read()
							new.close()
							old=open("/etc/enigma2/ci%d.xml" % slot, "w")
							old.write(assignment)
							old.close()
						appname = _("Slot %d") %(slot+1) + " - " + ci_name.replace(":","").replace("CI %s " % (slot+1),"")
						self.list.append( (appname, ConfigNothing(), 0, slot) )
		else:
			if config.plugins.autopin.remote.value:
				for name in os.listdir("/etc/enigma2"):
					for slot in range(2):
						if name.startswith("ci%d" % slot):
							ci_name=name.replace("ci%d" % slot,"").replace(".xml","").replace("_"," ")
	#						print ">>>>>", slot, ci_name, len(ci_name)
							if len(ci_name) > 0:
								appname = _("Slot %d") %(slot+1) + " - " + ci_name
								self.list.append( (appname, ConfigNothing(), 0, slot) )
		if not self.list:
			self.list.append( (_("no CI slots found") , ConfigNothing(), 1, -1) )

		menuList = ConfigList(self.list)
		menuList.list = self.list
		menuList.l.setList(self.list)
		self["CiList"] = menuList
		self.onShown.append(self.setWindowTitle)

	def setWindowTitle(self):
		self.setTitle(_("CI assignment")+" + "+_("Auto Pin V%s") % autopin_version )

	def greenPressed(self):
		cur = self["CiList"].getCurrent()
		if cur and len(cur) > 2:
			name = cur[0]
			action = cur[2]
			slot = cur[3]
			if slot < 0:
				cprint("[AUTOPIN] CI_Wizzard there is no used CI Slot in your receiver")
				return
			sp=[]
			sp=name.split()
			helped=False
			if config.ci[slot].start.value:
				helped=True
			if action == 1:
				cprint("[AUTOPIN] CI_Wizzard there is no used CI Slot in your receiver")
			else:
				cprint("[AUTOPIN] CI_Wizzard selected CI Slot : %d" % slot)
				if config.usage.setup_level.index > 1 and not helped: 
					self.session.open(CIconfigMenu, slot)
				else:
					self.session.open(easyCIconfigMenu, slot)

	def yellowPressed(self): 
		cur = self["CiList"].getCurrent()
		if cur and len(cur) > 2:
			slot = cur[3]
			if slot < 0:
				cprint("[AUTOPIN] CI_Wizzard there is no used CI Slot in your receiver")
				return
		self.session.openWithCallback(self.yellow_confirmed,MessageBox,_("Reset")+" "+_("CI assignment")+"?", MessageBox.TYPE_YESNO)

	def yellow_confirmed(self,answer):
		if answer is True:
			cur = self["CiList"].getCurrent()
			if cur and len(cur) > 2:
			#	print cur
				name=cur[0]
				slot=int(cur[3])
				assign="/etc/enigma2/ci%s.xml" % slot
				# remove also file with Module name ...
				module_name=name.replace(_("Slot %d") % (slot+1)+" - ","").replace(":","").replace("CI %s " % (slot+1),"")
				assign2="/etc/enigma2/ci%s%s.xml" % (slot,module_name.replace(" ","_"))
				if not os.path.exists(assign) and not os.path.exists(assign2):
					text=_("CI assignment")+" "+_("Slot %d") % (slot+1)+" "+_("not configured")
					self.session.open(MessageBox, text,  MessageBox.TYPE_ERROR, timeout=10) 
				else:
					if os.path.exists(assign):
						os.remove(assign)
					if os.path.exists(assign2):
						os.remove(assign2)
					text=_("Reset")+" "+_("CI assignment")+" "+_("Slot %d") % (slot+1)+" "+_("done!")
					self.session.open(MessageBox, text,  MessageBox.TYPE_INFO, timeout=10) 
		else:
			self.session.open(MessageBox, _("Reset")+" "+_("CI assignment")+" "+_("unconfirmed").lower() , MessageBox.TYPE_ERROR)
		
# rename original on startup
if os.path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/CommonInterfaceAssignment"):
	Plugins.SystemPlugins.CommonInterfaceAssignment.plugin.CIselectMainMenu = CIselectMainMenuPlus
	Plugins.SystemPlugins.CommonInterfaceAssignment.plugin.CIconfigMenu.saveXML = saveXMLPlus
	# Patch from Ghost for same provider with different dvbspace
	Plugins.SystemPlugins.CommonInterfaceAssignment.plugin.CIconfigMenu.finishedProviderSelection = finishedProviderSelectionPlus

class CiSelectionPlus(Screen):
	skin = """
		<screen name="CiSelection" position="center,120" size="820,520" title="Common Interface">
		<widget name="text" position="10,10" size="800,25" font="Regular;23" />
		<eLabel position="10,50" size="800,1" backgroundColor="grey" />
		<widget name="entries" position="10,60" size="800,450" enableWrapAround="1" scrollbarMode="showOnDemand" />
    	</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
#		self["actions"] = ActionMap(["OkCancelActions", "CiSelectionActions" ],
	        self["setupActions"] = ActionMap(["SetupActions"],
			{
				"left": self.keyLeft,
				"right": self.keyLeft,
				"ok": self.okbuttonClick,
				"cancel": self.cancel,
				"1": self.onePressed,
				"2": self.twoPressed
			},-2)

		self.dlg = None
		self.state = { }
		self.list = [ ]

		for slot in range(MAX_NUM_CI):
			state = eDVBCI_UI.getInstance().getState(slot)
			if state != -1:
				self.appendEntries(slot, state)
				CiHandler.registerCIMessageHandler(slot, self.ciStateChanged)
			else:
				if getMMISlotName(slot) is not None:
					state=3
					self.appendEntries(slot, state)
					CiHandler.registerCIMessageHandler(slot, self.ciStateChanged)

		menuList = ConfigList(self.list)
		menuList.list = self.list
		menuList.l.setList(self.list)
		self["entries"] = menuList
		self["entries"].onSelectionChanged.append(self.selectionChanged)
		self["text"] = Label(_("Slot %d")%(1))
		self.onShown.append(self.setWindowTitle)

	def setWindowTitle(self):
		self.setTitle(_("Common Interface")+" + "+_("Auto Pin V%s") % autopin_version )

	def onePressed(self):
		cprint("[AUTOPIN] selecting CI slot 1")
		self["entries"].setCurrentIndex(2)

	def twoPressed(self):
		cprint("[AUTOPIN] selecting CI slot 2")
		self["entries"].setCurrentIndex(7)
		
	def selectionChanged(self):
		cur_idx = self["entries"].getCurrentIndex()
		self["text"].setText(_("Slot %d")%((cur_idx / 5)+1))

	def keyConfigEntry(self, key):
		try:
			self["entries"].handleKey(key)
			self["entries"].getCurrent()[1].save()
		except:
			pass

	def keyLeft(self):
		self.keyConfigEntry(KEY_LEFT)

	def keyRight(self):
		self.keyConfigEntry(KEY_RIGHT)

	def appendEntries(self, slot, state):
		self.state[slot] = state
		self.list.append( (_("Reset"), ConfigNothing(), 0, slot) )
		self.list.append( (_("Init"), ConfigNothing(), 1, slot) )
		if self.state[slot] == 0:			#no module
			self.list.append( (_("no module found"), ConfigNothing(), 2, slot) )
		elif self.state[slot] == 1:		#module in init
			self.list.append( (_("init module"), ConfigNothing(), 2, slot) )
		elif self.state[slot] == 2:		#module ready
			#get appname
			appname = eDVBCI_UI.getInstance().getAppName(slot)
			self.list.append( (appname, ConfigNothing(), 2, slot) )
		elif self.state[slot] == 3:		#virtual module
       			mmi_name=getMMISlotName(slot)                      
			if mmi_name is not None:
		#		cprint("[AUTOPIN] CI %d %s" % (slot,mmi_name))
				self.list.append( (mmi_name.replace(":","").replace("CI %s " % (slot+1),""), ConfigNothing(), 2, slot) )
		ci_e2_fifo=False
		if os.path.exists("/dev/ci%d" % slot):
			if stat.S_ISFIFO(os.stat("/dev/ci%d" % slot).st_mode):
				ci_e2_fifo=True
		if self.state[slot] < 3 and not ci_e2_fifo:	
			self.list.append(getConfigListEntry(_("Multiple service support"), config.ci[slot].canDescrambleMultipleServices))
			try:
				if SystemInfo["CommonInterfaceSupportsHighBitrates"]:
					self.list.append(getConfigListEntry(_("High bitrate support"), config.ci[slot].canHandleHighBitrates))
			except:
				self.list.append(getConfigListEntry(_("High bitrate support"), config.ci[slot].canHandleHighBitrates))
		else:                                   # virtual module
			if config.ci[slot].start.value:
				self.list.append(getConfigListEntry(_("Multiple service support"), config.ci[slot].none))
			else:
				self.list.append(getConfigListEntry(_("Multiple service support"), config.ci[slot].canDescrambleMultipleServices))
			try:
				if SystemInfo["CommonInterfaceSupportsHighBitrates"]:
					self.list.append(getConfigListEntry(_("High bitrate support"), config.ci[slot].canHandleHighBitrates))
#				if config.ci[slot].start.value:
#					self.list.append(getConfigListEntry(_("High bitrate support"), config.ci[slot].none))
#				else:
#					self.list.append(getConfigListEntry(_("High bitrate support"), config.ci[slot].canHandleHighBitrates))
			except:
				self.list.append(getConfigListEntry(_("High bitrate support"), config.ci[slot].canHandleHighBitrates))

	def updateState(self, slot):
		state = eDVBCI_UI.getInstance().getState(slot)
		self.state[slot] = state

		slotidx=0
		while len(self.list[slotidx]) < 3 or self.list[slotidx][3] != slot:
			slotidx += 1

		slotidx += 1 # do not change Reset
		slotidx += 1 # do not change Init

		if state == 0:			#no module
			self.list[slotidx] = (_("no module found"), ConfigNothing(), 2, slot)
		elif state == 1:		#module in init
			self.list[slotidx] = (_("init module"), ConfigNothing(), 2, slot)
		elif state == 2: 		#module ready
			#get appname
			appname = eDVBCI_UI.getInstance().getAppName(slot)
			self.list[slotidx] = (appname, ConfigNothing(), 2, slot)
		elif state == 3:		#virtual module
       			mmi_name= socketHandler.getName(mmi)                       
			if mmi_name is not None:
				self.list[slotidx] = (mmi_name, ConfigNothing(), 2, slot)
		lst = self["entries"]
		lst.list = self.list
		lst.l.setList(self.list)

	def ciStateChanged(self, slot):
		if self.dlg:
			self.dlg.ciStateChanged()
		else:
			state = eDVBCI_UI.getInstance().getState(slot)
			if self.state[slot] != state:
			# 	cprint("[AUTOPIN] something happens")
				self.state[slot] = state
				self.updateState(slot)

	def dlgClosed(self, slot):
		self.dlg = None

	def okbuttonClick(self):
		cur = self["entries"].getCurrent()
		global dreambin
		global dreamserv
		if cur and len(cur) > 2:
			action = cur[2]
			slot = cur[3]
			state=self.state[slot]
			cprint("[AUTOPIN] CI ACTION slot %d action %d state %d" % (slot,action,state))
		        self.realinstance = eDVBCI_UI.getInstance()
			self.container = eConsoleAppContainer()
			if os.path.exists("/var/lib/dpkg/status"):
				self.container_appClosed_conn = self.container.appClosed.connect(self.runFinished)
			else:
				self.container.appClosed.append(self.runFinished)
			ci_e2_fifo=False
			if os.path.exists("/dev/ci%d" % slot):
				if stat.S_ISFIFO(os.stat("/dev/ci%d" % slot).st_mode):
					ci_e2_fifo=True
					state=3
			if action == 0:		#reset
				if state < 3:
			                self.realinstance.setReset(slot) 
				else:
					if config.ci[slot].mmi.value or ci_e2_fifo:
#						text=_("MMI")+" "+_("Message")+" "+_("disabled")
#						self.session.open(MessageBox, text,  MessageBox.TYPE_ERROR, timeout=10)
						if os.path.exists(dreamso) and config.ci[slot].plus.value:
							cprint("[AUTOPIN] CI reset %d" % slot)
							dreamplus.setReset(slot)
						else:
							cmd="%s erase %d" % (dreambin, slot)
							cprint("[AUTOPIN] CI command %s" % cmd)
							self.container.execute(cmd)
					else:
						if os.path.exists("/var/lib/dpkg/status"):   
                                    			self.realinstance = eSocket_UI.getInstance()
                            			else:                                             
                                    			self.realinstance = socketmmi   
						mmi_number=getMMISlotNumber(slot)
						if mmi_number is not None:
							cprint("[AUTOPIN] CI MMI reset slot %d" % mmi_number)
							self.realinstance.answerEnq(mmi_number,"CA_RESET")
			elif action == 1:	#init
				if state < 3:
			                self.realinstance.setInit(slot) 
				else:
					if config.ci[slot].mmi.value or ci_e2_fifo:
#						text=_("MMI")+" "+_("Message")+" "+_("disabled")
#						self.session.open(MessageBox, text,  MessageBox.TYPE_ERROR, timeout=10)
						if os.path.exists(dreamso) and config.ci[slot].plus.value:
							cprint("[AUTOPIN] CI restart %d" % slot)
							dreamplus.restart(slot)
						else:
							cmd="%s restart %d" % (dreambin, slot)
							cprint("[AUTOPIN] CI command %s" % cmd)
							self.container.execute(cmd)
					else:
						if os.path.exists("/var/lib/dpkg/status"):   
                                    			self.realinstance = eSocket_UI.getInstance()
                            			else:                                             
                                    			self.realinstance = socketmmi   
						mmi_number=getMMISlotNumber(slot)
						if mmi_number is not None:
							cprint("[AUTOPIN] CI MMI init slot %d" % mmi_number)
							self.realinstance.answerEnq(mmi_number,"CA_INIT")
			elif state == 2: 	#dialog
				self.dlg = self.session.openWithCallback(self.dlgClosed, MMIDialog, slot, action)
			elif state == 3: 	#mmi dialog
				mmi_number=getMMISlotNumber(slot)
				if mmi_number is not None:
					cprint("[AUTOPIN] MMI number %d" % mmi_number)
					ci_name=getMMISlotName(slot)
					cprint("[AUTOPIN] CI Name %s" % ci_name)
					if os.path.exists("/var/lib/dpkg/status"):
						self.realinstance = eSocket_UI.getInstance()
					else:
						self.realinstance = socketmmi
					if config.ci[slot].mmi.value:
						text=_("MMI")+" "+_("Message")+" "+_("disabled")
						self.dlg = self.session.openWithCallback(self.dlgClosed, MessageBox, text,  MessageBox.TYPE_ERROR, timeout=10)
					else:
						self.dlg = self.session.openWithCallback(self.dlgClosed, MMIDialog, mmi_number, 2, self.realinstance, _("wait for mmi..."))

	def cancel(self):
		for slot in range(MAX_NUM_CI):
			state = eDVBCI_UI.getInstance().getState(slot)
			if state != -1:
				CiHandler.unregisterCIMessageHandler(slot)
		self.close()

	def runFinished(self, retval):    
		pass

	def dummyPressed(self):                                                  
		pass
		
# rename original on startup in any case
Screens.Ci.CiSelection = CiSelectionPlus

from Components.Sources.Source import Source
from Components.Element import cached

class StreamServiceAutoPin(Source):
	def __init__(self, navcore):
		Source.__init__(self)
		self.ref = None
		self.__service = None
		self.navcore = navcore

	def serviceEvent(self, event):
		pass

	@cached
	def getService(self):
		return self.__service

	service = property(getService)

	def handleCommand(self, cmd):
		cprint("[AUTOPIN] StreamService handle command %s" % cmd)
		self.ref = eServiceReference(cmd)

	def recordEvent(self, service, event):
		if service is self.__service:
			return
		cprint("[AUTOPIN] RECORD event for us: %s" % service)
		self.changed((self.CHANGED_ALL, ))

	def execBegin(self):
		if self.ref is None:
#			cprint("[AUTOPIN] StreamService has no service ref")
			return
		if not config.streaming.asktozap.value: # CI streaming has NO priority
			ciserv=self.ref.toString()
			cprint("[AUTOPIN] checks if CI is needed for streaming of %s" % ciserv)
			rec_needs_ci1=checkCI(self.ref,0)
			rec_needs_ci2=checkCI(self.ref,1)
			cur_ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
			curserv="unknown"
			if cur_ref is not None:
				curserv=cur_ref.toString()
			if ciserv == curserv:
				cprint("[AUTOPIN] streaming channel is Live TV")
			else:
				cprint("[AUTOPIN] checks if CI is busy")
				if rec_needs_ci1 is not -1 and os.path.exists("/var/run/ca/ci0.service"):
					cprint("[AUTOPIN] CI1 is busy, no streaming")
					return
				if rec_needs_ci2 is not -1 and os.path.exists("/var/run/ca/ci1.service"):
					cprint("[AUTOPIN] CI2 is busy, no streaming")
					return

	        cprint("[AUTOPIN] StreamService execBegin %s" % self.ref.toString())
		self.__service = self.navcore.recordService(self.ref)
		self.navcore.record_event.append(self.recordEvent)
		if self.__service is None:
			cprint("[AUTOPIN] failed streaming")
		else:
			self.__service.prepareStreaming()
			self.__service.start()
			cprint("[AUTOPIN] started streaming")
			# create streaming file
			s=open("/tmp/stream.%s" % self.ref.toString().replace("/","_"),"w")
			s.write(self.ref.toString())
			s.close()
			if config.streaming.asktozap.value: # CI streaming needs special priority
				ciserv=self.ref.toString()
				cprint("[AUTOPIN] checks if CI is needed for streaming of %s" % ciserv)
				rec_needs_ci1=checkCI(self.ref,0)
				rec_needs_ci2=checkCI(self.ref,1)
				cur_ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
				if (Screens.Standby.inStandby) or (config.plugins.autopin.zapto.value == "inactive") or (cur_ref is None) or ((rec_needs_ci1 is -1) and (rec_needs_ci2 is -1)):
					cprint("[AUTOPIN] CI needs NO zap to streaming")
					return
				curserv=cur_ref.toString()
				if ciserv == curserv:
					cprint("[AUTOPIN] streaming channel is Live TV")
					return
				cprint("[AUTOPIN] checks if CI is needed for Live TV of %s" % curserv)
				cur_needs_ci1=checkCI(cur_ref,0)
				cur_needs_ci2=checkCI(cur_ref,1)
				ci1_needed=True
				ci2_needed=True
				if rec_needs_ci1 is not -1:     # CI1 needed for streaming
					if cur_needs_ci1 is -1: # but should be free
						cprint("[AUTOPIN] needs NO zap to streaming for CI1")
						ci1_needed=False
										
				if rec_needs_ci2 is not -1:     # CI2 needed for streaming
					if cur_needs_ci2 is -1: # but should be free
						cprint("[AUTOPIN] needs NO zap to streaming for CI2")
						ci2_needed=False

				if config.plugins.autopin.zapto.value == "active": 
					cprint("[AUTOPIN] needs ALWAYS zap to streaming for CI")
					self.navcore.playService(self.ref)
					return
				if ci1_needed or ci2_needed:
					cprint("[AUTOPIN] needs restart of Live TV")
					self.navcore.stopService()
					self.navcore.playService(cur_ref)

	def execEnd(self):
		if self.ref is None:
#			cprint("[AUTOPIN] StreamService has no service ref")
			return
	        cprint("[AUTOPIN] StreamService execEnd %s" % self.ref.toString())
		try:
			self.navcore.record_event.remove(self.recordEvent)
		except:
			pass
		ciserv=self.ref.toString()
		cprint("[AUTOPIN] checks if CI was needed for streaming of %s" % ciserv)
		rec_needs_ci1=checkCI(self.ref,0)
		rec_needs_ci2=checkCI(self.ref,1)
		if self.__service is not None:
			self.navcore.stopRecordService(self.__service)
			self.__service = None
		# remove streaming file
		if os.path.exists("/tmp/stream.%s" % self.ref.toString().replace("/","_")):
			os.remove("/tmp/stream.%s" % self.ref.toString().replace("/","_"))
		if config.streaming.asktozap.value: # CI streaming needs special priority
			if rec_needs_ci1 is -1 and rec_needs_ci2 is -1:
				cprint("[AUTOPIN] needed NO CI for streaming")
				return
			cur_ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
			if (Screens.Standby.inStandby) or (config.plugins.autopin.zapto.value == "inactive") or (cur_ref is None) or ((rec_needs_ci1 is -1) and (rec_needs_ci2 is -1)):
				cprint("[AUTOPIN] CI no need to zap")
				return
			curserv=cur_ref.toString()
			if ciserv == curserv:
				cprint("[AUTOPIN] streaming channel is Live TV")
				return
			cprint("[AUTOPIN] checks if CI is is needed for Live TV of %s" % curserv)
			cur_needs_ci1=checkCI(cur_ref,0)
			cur_needs_ci2=checkCI(cur_ref,1)
			ci1_needed=True
			ci2_needed=True
			if rec_needs_ci1 is not -1:     # CI1 was needed for streaming
				if cur_needs_ci1 is -1: # but should be free
					cprint("[AUTOPIN] needs NO restart for CI1")
					ci1_needed=False
							
			if rec_needs_ci2 is not -1:     # CI2 was needed for streaming
				if cur_needs_ci2 is -1: # but should be free
					cprint("[AUTOPIN] needs NO zap to streaming for CI2")
					ci2_needed=False

			if config.plugins.autopin.zapto.value == "active": 
				cprint("[AUTOPIN] needs ALWAYS zap to streaming for CI")
				self.navcore.playService(self.ref)
				return
			if ci1_needed or ci2_needed:
				cprint("[AUTOPIN] needs restart of Live TV")
				self.navcore.stopService()
				self.navcore.playService(cur_ref)

# rename original on startup in any case
Components.Sources.StreamService.StreamService = StreamServiceAutoPin

autopin_title=_("Auto Pin by gutemine")+" V%s " % autopin_version
autopin_support=_("Kit & Support:\n\nwww.oozoon-board.de")
autopin_help=_("Message")+" "+_("confirmed")+":\n"+_("insert card: 44, 103, 503, 993\nno subscription: 2, 204, 304, 502, 510, 990, 991\nreading card: 74, 536")

size_w = getDesktop(0).size().width()
size_h = getDesktop(0).size().height()

class AutoPin(Screen, HelpableScreen, ConfigListScreen):
# Full HD skin
	if size_w > 1280: 
		skin = """
		<screen position="center,center" size="1010,780" title="Auto Pin" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="10,10" size="240,40" alphatest="on" />
	     	<ePixmap pixmap="skin_default/buttons/green.png" position="260,10" size="240,40" alphatest="on" />
	    	<ePixmap pixmap="skin_default/buttons/yellow.png" position="510,10" size="240,40" alphatest="on" />
     		<ePixmap pixmap="skin_default/buttons/blue.png" position="760,10" size="240,40" alphatest="on" />
	    	<widget name="buttonred" position="10,10" size="240,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
	    	<widget name="buttongreen" position="260,10" size="240,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
	    	<widget name="buttonyellow" position="510,10" size="240,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
	    	<widget name="buttonblue" position="760,10" size="240,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		<eLabel position="10,65" size="1000,1" backgroundColor="grey" />
		<widget name="config" position="10,80" size="990,500" scrollbarMode="showOnDemand" />

		<widget name="info"  position="870,640" size="60,30" alphatest="on" />
		<widget name="menu"  position="800,640" size="60,30" alphatest="on" />
		<widget name="pvr"   position="940,640" size="60,30" alphatest="on" />
		<widget name="help"  position="940,680" size="60,30" alphatest="on" />
		<widget name="text"  position="940,720" size="60,30" alphatest="on" />

		<widget name="rewind"  position="60,635" size="16,16" alphatest="on" />
		<widget name="play"    position="124,635" size="16,16" alphatest="on" />
		<widget name="pause"   position="140,635" size="16,16" alphatest="on" />
		<widget name="stop"    position="200,635" size="16,16" alphatest="on" />
		<widget name="forward" position="260,635" size="16,16" alphatest="on" />
		<widget name="record"  position="320,636" size="14,14" alphatest="on" />

		<widget name="ci0_auth1" position="16,680" size="28,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;32"/>
		<widget name="ci0_auth2" position="18,682" size="24,26" backgroundColors="black,white,red,green,yellow,blue" valign="center" halign="center" zPosition="3"  foregroundColors="white,black,white,white,black,white" font="Regular;32"/>
		<widget name="ci1_auth1" position="16,720" size="28,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;32"/>
		<widget name="ci1_auth2" position="18,722" size="24,26" backgroundColors="black,white,red,green,yellow,blue" valign="center" halign="center" zPosition="3"  foregroundColors="white,black,white,white,black,white" font="Regular;32"/>

		<widget name="ci0_module_back1" position="50,680" size="250,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>
		<widget name="ci0_module_back2" position="52,682" size="246,26" backgroundColor="black" valign="center" halign="center" zPosition="3"  foregroundColor="black" font="Regular;18"/>
		<widget name="ci0_module" position="62,691" size="226,8" backgroundColor="white" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18"/>

		<widget name="ci1_module_back1" position="50,720" size="250,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>
		<widget name="ci1_module_back2" position="52,722" size="246,26" backgroundColor="black" valign="center" halign="center" zPosition="3"  foregroundColor="black" font="Regular;18"/>
		<widget name="ci1_module" position="62,731" size="226,8" backgroundColor="white" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18"/>

		<widget name="ci0_back" position="310,680" size="30,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>
		<widget name="ci0" position="312,682" size="26,26" backgroundColors="black,white,red,green,yellow,blue" valign="center" halign="center" zPosition="3"  foregroundColors="white,black,white,white,black,white" font="Regular;16"/>

		<widget name="ci1_back" position="310,720" size="30,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>
		<widget name="ci1" position="312,722" size="26,26" backgroundColors="black,white,red,green,yellow,blue" valign="center" halign="center" zPosition="3"  foregroundColors="white,black,white,white,black,white" font="Regular;16"/>

		<widget name="ci0_text_rect" position="350,680" size="580,30" backgroundColor="yellow" valign="center" halign="center" zPosition="3"  foregroundColor="yellow" font="Regular;16"/>
		<widget name="ci1_text_rect" position="350,720" size="580,30" backgroundColor="yellow" valign="center" halign="center" zPosition="3"  foregroundColor="yellow" font="Regular;16"/>
		<widget name="ci0_text" position="351,681" size="578,28" backgroundColor="black" valign="center" halign="left" zPosition="4"  foregroundColor="yellow" font="Regular;20"/>
		<widget name="ci1_text" position="351,721" size="578,28" backgroundColor="black" valign="center" halign="left" zPosition="4"  foregroundColor="yellow" font="Regular;20"/>
		</screen>"""
	else:
# other skin
                # only DreamOS scales Buttons :-(                                     
                if os.path.exists("/var/lib/dpkg/status"): 
			skin = """
			<screen position="center,120" size="820,520" title="Auto Pin" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="10,5" size="200,40" alphatest="on" />
		     	<ePixmap pixmap="skin_default/buttons/green.png" position="210,5" size="200,40" alphatest="on" />
		    	<ePixmap pixmap="skin_default/buttons/yellow.png" position="410,5" size="200,40" alphatest="on" />
	     		<ePixmap pixmap="skin_default/buttons/blue.png" position="610,5" size="200,40" alphatest="on" />
		    	<widget name="buttonred" position="10,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		    	<widget name="buttongreen" position="210,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		    	<widget name="buttonyellow" position="410,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		    	<widget name="buttonblue" position="610,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
			<eLabel position="10,50" size="800,1" backgroundColor="grey" />
		    	<widget name="config" position="10,60" size="800,330" enableWrapAround="1" scrollbarMode="showOnDemand" />

			<widget name="info"  position="680,402" size="60,30" alphatest="on" />
			<widget name="menu"  position="610,402" size="60,30" alphatest="on" />
			<widget name="pvr"   position="750,402" size="60,30" alphatest="on" />
			<widget name="help"  position="750,442" size="60,30" alphatest="on" />
			<widget name="text"  position="750,482" size="60,30" alphatest="on" />

			<widget name="rewind"  position="60,415" size="16,16" alphatest="on" />
			<widget name="play"    position="124,415" size="16,16" alphatest="on" />
			<widget name="pause"   position="140,415" size="16,16" alphatest="on" />
			<widget name="stop"    position="200,415" size="16,16" alphatest="on" />
			<widget name="forward" position="260,415" size="16,16" alphatest="on" />
			<widget name="record"  position="320,416" size="14,14" alphatest="on" />

			<widget name="ci0_auth1" position="16,440" size="28,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;32"/>
			<widget name="ci0_auth2" position="18,442" size="24,26" backgroundColors="black,white,red,green,yellow,blue" valign="center" halign="center" zPosition="3"  foregroundColors="white,black,white,white,black,white" font="Regular;32"/>
			<widget name="ci1_auth1" position="16,480" size="28,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;32"/>
			<widget name="ci1_auth2" position="18,482" size="24,26" backgroundColors="black,white,red,green,yellow,blue" valign="center" halign="center" zPosition="3"  foregroundColors="white,black,white,white,black,white" font="Regular;32"/>

			<widget name="ci0_module_back1" position="50,440" size="250,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>
			<widget name="ci0_module_back2" position="52,442" size="246,26" backgroundColor="black" valign="center" halign="center" zPosition="3"  foregroundColor="black" font="Regular;18"/>
			<widget name="ci0_module" position="62,451" size="226,8" backgroundColor="white" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18"/>

			<widget name="ci1_module_back1" position="50,480" size="250,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>
			<widget name="ci1_module_back2" position="52,482" size="246,26" backgroundColor="black" valign="center" halign="center" zPosition="3"  foregroundColor="black" font="Regular;18"/>
			<widget name="ci1_module" position="62,491" size="226,8" backgroundColor="white" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18"/>

			<widget name="ci0_back" position="310,440" size="30,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>
			<widget name="ci0" position="312,442" size="26,26" backgroundColors="black,white,red,green,yellow,blue" valign="center" halign="center" zPosition="3"  foregroundColors="white,black,white,white,black,white" font="Regular;16"/>

			<widget name="ci1_back" position="310,480" size="30,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>
			<widget name="ci1" position="312,482" size="26,26" backgroundColors="black,white,red,green,yellow,blue" valign="center" halign="center" zPosition="3"  foregroundColors="white,black,white,white,black,white" font="Regular;16"/>

			<widget name="ci0_text_rect" position="350,440" size="390,30" backgroundColor="yellow" valign="center" halign="center" zPosition="3"  foregroundColor="yellow" font="Regular;16"/>
			<widget name="ci1_text_rect" position="350,480" size="390,30" backgroundColor="yellow" valign="center" halign="center" zPosition="3"  foregroundColor="yellow" font="Regular;16"/>
			<widget name="ci0_text" position="351,441" size="388,28" backgroundColor="black" valign="center" halign="left" zPosition="4"  foregroundColor="yellow" font="Regular;16"/>
			<widget name="ci1_text" position="351,481" size="388,28" backgroundColor="black" valign="center" halign="left" zPosition="4"  foregroundColor="yellow" font="Regular;16"/>
			</screen>"""
		else:
			skin = """
			<screen position="center,120" size="820,520" title="Auto Pin" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="10,5" size="150,40" alphatest="on" />
		     	<ePixmap pixmap="skin_default/buttons/green.png" position="230,5" size="150,40" alphatest="on" />
		    	<ePixmap pixmap="skin_default/buttons/yellow.png" position="450,5" size="150,40" alphatest="on" />
	     		<ePixmap pixmap="skin_default/buttons/blue.png" position="670,5" size="150,40" alphatest="on" />
		    	<widget name="buttonred" position="10,5" size="150,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		    	<widget name="buttongreen" position="230,5" size="150,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		    	<widget name="buttonyellow" position="450,5" size="150,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		    	<widget name="buttonblue" position="670,5" size="150,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
			<eLabel position="10,50" size="800,1" backgroundColor="grey" />
		    	<widget name="config" position="10,60" size="800,330" enableWrapAround="1" scrollbarMode="showOnDemand" />

			<widget name="info"  position="680,402" size="60,30" alphatest="on" />
			<widget name="menu"  position="610,402" size="60,30" alphatest="on" />
			<widget name="pvr"   position="750,402" size="60,30" alphatest="on" />
			<widget name="help"  position="750,442" size="60,30" alphatest="on" />
			<widget name="text"  position="750,482" size="60,30" alphatest="on" />

			<widget name="rewind"  position="60,415" size="16,16" alphatest="on" />
			<widget name="play"    position="124,415" size="16,16" alphatest="on" />
			<widget name="pause"   position="140,415" size="16,16" alphatest="on" />
			<widget name="stop"    position="200,415" size="16,16" alphatest="on" />
			<widget name="forward" position="260,415" size="16,16" alphatest="on" />
			<widget name="record"  position="320,416" size="14,14" alphatest="on" />

			<widget name="ci0_auth1" position="16,440" size="28,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;32"/>
			<widget name="ci0_auth2" position="18,442" size="24,26" backgroundColors="black,white,red,green,yellow,blue" valign="center" halign="center" zPosition="3"  foregroundColors="white,black,white,white,black,white" font="Regular;32"/>
			<widget name="ci1_auth1" position="16,480" size="28,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;32"/>
			<widget name="ci1_auth2" position="18,482" size="24,26" backgroundColors="black,white,red,green,yellow,blue" valign="center" halign="center" zPosition="3"  foregroundColors="white,black,white,white,black,white" font="Regular;32"/>

			<widget name="ci0_module_back1" position="50,440" size="250,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>
			<widget name="ci0_module_back2" position="52,442" size="246,26" backgroundColor="black" valign="center" halign="center" zPosition="3"  foregroundColor="black" font="Regular;18"/>
			<widget name="ci0_module" position="62,451" size="226,8" backgroundColor="white" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18"/>

			<widget name="ci1_module_back1" position="50,480" size="250,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>
			<widget name="ci1_module_back2" position="52,482" size="246,26" backgroundColor="black" valign="center" halign="center" zPosition="3"  foregroundColor="black" font="Regular;18"/>
			<widget name="ci1_module" position="62,491" size="226,8" backgroundColor="white" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18"/>

			<widget name="ci0_back" position="310,440" size="30,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>
			<widget name="ci0" position="312,442" size="26,26" backgroundColors="black,white,red,green,yellow,blue" valign="center" halign="center" zPosition="3"  foregroundColors="white,black,white,white,black,white" font="Regular;16"/>

			<widget name="ci1_back" position="310,480" size="30,30" backgroundColor="white" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>
			<widget name="ci1" position="312,482" size="26,26" backgroundColors="black,white,red,green,yellow,blue" valign="center" halign="center" zPosition="3"  foregroundColors="white,black,white,white,black,white" font="Regular;16"/>

			<widget name="ci0_text_rect" position="350,440" size="390,30" backgroundColor="yellow" valign="center" halign="center" zPosition="3"  foregroundColor="yellow" font="Regular;16"/>
			<widget name="ci1_text_rect" position="350,480" size="390,30" backgroundColor="yellow" valign="center" halign="center" zPosition="3"  foregroundColor="yellow" font="Regular;16"/>
			<widget name="ci0_text" position="351,441" size="388,28" backgroundColor="black" valign="center" halign="left" zPosition="4"  foregroundColor="yellow" font="Regular;16"/>
			<widget name="ci1_text" position="351,481" size="388,28" backgroundColor="black" valign="center" halign="left" zPosition="4"  foregroundColor="yellow" font="Regular;16"/>
			</screen>"""

	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
     		self.skin = AutoPin.skin 

		self.list = []                                                  
		ConfigListScreen.__init__(self, self.list, session = self.session)
		self.createSetup()       
		self.addedKeys=False
                self.onShown.append(self.setWindowTitle)
                self.onLayoutFinish.append(self.refreshLayout)
		global dreambin
		global dreamserv
		self.remote_ci0=False
		self.remote_ci1=False
		if config.plugins.autopin.remote.value:
			for name in os.listdir("/etc/enigma2"):
				if name.startswith("ci0"):
					self.remote_ci0=True
				if name.startswith("ci1"):
					self.remote_ci1=True
		self["buttonred"] = Label(_("Exit"))
		self["buttongreen"] = Label(_("Save"))
		if self.remote_ci0 or self.remote_ci1:
			self["buttonyellow"] = Label(_("FTP")+" "+_("Download"))
		else:
                	if os.path.exists("/var/lib/dpkg/status"): 
				self["buttonyellow"] = Label(_("Common Interface"))
			else:
				self["buttonyellow"] = Label(_("CI")+" "+_("Menu"))
		if os.path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/CommonInterfaceAssignment"):
			self["buttonblue"] = Label(_("CI assignment"))
		else:
			self["buttonblue"] = Label(_("About"))
      		self["help"] = Pixmap() 
      		self["menu"] = Pixmap() 
      		self["pvr"] = Pixmap() 
      		self["text"] = Pixmap() 
      		self["info"] = Pixmap() 
      		self["rewind"] = Pixmap() 
      		self["forward"] = Pixmap() 
      		self["stop"] = Pixmap() 
      		self["play"] = Pixmap() 
      		self["pause"] = Pixmap() 
      		self["record"] = Pixmap() 
		self["ci0_auth1"] = Label("")
		self["ci0_auth2"] = MultiColorLabel("+")
		self["ci1_auth1"] = Label("")
		self["ci1_auth2"] = MultiColorLabel("+")
		self["ci0_module"] = Label("")
		self["ci0_module_back1"] = Label("")
		self["ci0_module_back2"] = Label("")
		self["ci1_module"] = Label("")
		self["ci1_module_back1"] = Label("")
		self["ci1_module_back2"] = Label("")
		self["ci0"] = MultiColorLabel("1")
		self["ci0_back"] = Label("")
		self["ci1"] = MultiColorLabel("2")
		self["ci1_back"] = Label("")
		self["ci0_text_rect"] = Label("")
		self["ci1_text_rect"] = Label("")
		self["ci0_text"] = Label("")
		self["ci1_text"] = Label("")
		# hide until checked
		self["ci0_auth1"].hide()
		self["ci0_auth2"].hide()
		self["ci1_auth1"].hide()
		self["ci1_auth2"].hide()
		if not os.path.exists("/dev/ci1") and not self.remote_ci1:
			self["ci1"].hide()
			self["ci1_back"].hide()
			self["ci1_module"].hide()
			self["ci1_module_back1"].hide()
			self["ci1_module_back2"].hide()
		self.AutoPinRefreshTimer.start(200, True)
		global autopin_key_pressed
		autopin_key_pressed=0
		if os.path.exists(dreambin):
			self["EPGSelectActions"] = HelpableActionMap(self,"EPGSelectActions",
			{
				"info":			(self.info,_("Show Info")+" "+dreamserv),
			}, -3)

			self["MediaPlayerSeekActions"] = HelpableActionMap(self,"MediaPlayerSeekActions",
			{
				"seekBack": 		(self.previousPressed,_("disable")+" "+_("auto")+" "+_("Load")+" "+dreamserv),
				"seekFwd": 		(self.nextPressed,_("enable")+" "+_("auto")+" "+_("Load")+" "+ dreamserv),
#				"seekBack": 		(self.dummyPressed,_("disable")+" "+_("auto")+" "+_("Load")+" "+dreamserv),
#				"seekFwd": 		(self.dummyPressed,_("enable")+" "+_("auto")+" "+_("Load")+" "+dreamserv),
			}, -3)

			self["InfobarInstantRecord"] = HelpableActionMap(self,"InfobarInstantRecord",
			{
				"instantRecord": 	(self.logging,_("Log")),
				"delete": 		(self.logging,_("Log")),
			}, -6)	
		
			self["MediaPlayerActions"] = HelpableActionMap(self,"MediaPlayerActions",
			{
				"pause": 		(self.playPressed,_("Start")+" "+dreamserv),
				"stop": 		(self.stopPressed,_("Stop")+" "+dreamserv),
#				"pause": 		(self.dummyPressed,_("Start")+" "+dreamserv),
#				"stop": 		(self.dummyPressed,_("Stop")+" "+dreamserv),
				"menu":			(self.menu,_("Extended Setup...").replace("...","").replace("-"," ")),
				"delete":		(self.pvrPressed,_("enable")+"/"+_("disable")+" "+_("CI")+" "+_("Message").replace("...","").replace("-"," ")),
#				"subtitles": 		(self.about,_("About")),
				"subtitles": 		(self.logging,_("Log")),
			}, -3)

		if not os.path.exists("/dev/ci0") and not os.path.exists("/dev/ci1"):
			self["SetupActions"] = HelpableActionMap(self,"SetupActions",
				{
					"save": 		(self.save,_("Save")+" "+_("Settings")),
					"cancel":		(self.cancel,_("Exit")),
					"ok": 			(self.okPressed, _("Show Info")+" "+dreamserv),
				}, -6)
		else:
			self["SetupActions"] = HelpableActionMap(self,"SetupActions",
				{
					"1": 			(self.onePressed,_("Slot %d") % 1),
					"2": 			(self.twoPressed,_("Slot %d") % 2),
					"save": 		(self.save,_("Save")+" "+_("Settings")),
					"cancel":		(self.cancel,_("Exit")),
					"ok": 			(self.okPressed, _("Show Info")+" "+dreamserv),
				}, -6)

		if os.path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/CommonInterfaceAssignment"):
			self["ColorActions"] = HelpableActionMap(self,"ColorActions",
			{
				"green":		(self.save, _("Save")+" "+_("Settings")),
				"red":			(self.cancel,_("Exit")),
				"yellow":		(self.interface,_("Common Interface")+" "+_("Open plugin menu")),
				"blue":			(self.assign,_("CI-Assignment")+" "+_("Open plugin menu")),
			}, -4)
		else:
			self["ColorActions"] = HelpableActionMap(self,"ColorActions",
			{
				"green":		(self.save, _("Save")+" "+_("Settings")),
				"red":			(self.cancel,_("Exit")),
				"yellow":		(self.interface,_("Common Interface")+" "+_("Open plugin menu")),
				"blue":			(self.assign,_("About")),
			}, -4)

		self["TvRadioActions"] = HelpableActionMap(self,"TvRadioActions",
		{
			"keyTV":		(self.cancel,_("Exit")),
#			"keyRadio": 		(self.dummyPressed, _("Auto PIN")),
		}, -3)

	def checkPid(self,slot):                                         
		global dreambin
		global dreamserv
		pf="/var/run/ca/%s%d.pid" % (dreamserv,slot)
		try:
			if os.path.exists(pf):
				f=open(pf,"r")
				pid=f.read().rstrip("\n")
				f.close()
				if os.path.exists("/proc/%s" % pid):
					return True
				else:
					os.remove(pf)
		except:
			pass
		return False

	def dummyPressed(self):                                                  
		pass

	def createSetup(self):                                                  
		# init only on first run
		self.refreshLayout(True)

	def updateList(self, configElement):
		defval = []
		if configElement.value and len(config.plugins.autopin.confirmhelper.value) >0:
			val = int(config.plugins.autopin.confirmhelper.value)
			if not val in configElement.value:
				tmp = configElement.value[:]
				tmp.reverse()
				for x in tmp:
					if x < val:
						defval = str(x)
						break
		config.plugins.autopin.confirmhelper.setChoices(map(str, configElement.value), defval)

	def playPressed(self):
		try:
			cur_idx = self["config"].getCurrentIndex()
		except:
			cprint("[AUTOPIN] EXCEPT")
			cur_idx = 99
		if cur_idx == 0:
			self.okPressed("start")
		if cur_idx == SECOND_SLOT and os.path.exists("/dev/ci1"):
			self.okPressed("start")

	def stopPressed(self):
		try:
			cur_idx = self["config"].getCurrentIndex()
		except:
			cprint("[AUTOPIN] EXCEPT")
			cur_idx = 99
		if cur_idx == 0:
			self.okPressed("stop")
		if cur_idx == SECOND_SLOT and os.path.exists("/dev/ci1"):
			self.okPressed("stop")

	def onePressed(self):
		if self.remote_ci0 or self.remote_ci1:
			return
		cur = self["config"].getCurrent()
		if cur and isinstance(cur[1], ConfigInteger) and cur[0].startswith("PIN"):
			self["config"].handleKey(13)
		else:
			cprint("[AUTOPIN] selecting CI slot 1")
			self["config"].setCurrentIndex(0)

	def twoPressed(self):
		if self.remote_ci0 or self.remote_ci1:
			return
		cur = self["config"].getCurrent()
		if cur and isinstance(cur[1], ConfigInteger) and cur[0].startswith("PIN"):
			self["config"].handleKey(14)
		else:	
			if os.path.exists("/dev/ci1"):
				cprint("[AUTOPIN] selecting CI slot 2")
				self["config"].setCurrentIndex(SECOND_SLOT)
		
	def previousPressed(self):
		try:
			cur_idx = self["config"].getCurrentIndex()
		except:
			cprint("[AUTOPIN] EXCEPT")
			cur_idx = 99
		if cur_idx == 0:
			slot=0
			self.okPressed("disable")
		if cur_idx == SECOND_SLOT and os.path.exists("/dev/ci1"):
			slot=1
			self.okPressed("disable")

	def nextPressed(self):
		try:
			cur_idx = self["config"].getCurrentIndex()
		except:
			cprint("[AUTOPIN] EXCEPT")
			cur_idx = 99
		if cur_idx == 0:
			slot=0
			self.okPressed("enable")
		if cur_idx == SECOND_SLOT and os.path.exists("/dev/ci1"):
			slot=1
			self.okPressed("enable")

	def okPressed(self, action=None):
		binversion=""
		global dreambin
		global dreamserv
		if os.path.exists(dreambin):
			cur = self["config"].getCurrent()
			if cur and len(cur) > 2:
				restart=False
				done=True
		#		print cur
				self.name = cur[0]
				if action is None and len(self.name) > 0:
#					action = cur[1].value
					action = "info"
				slot = cur[2]
				cprint("[AUTOPIN] CI %s slot %d action %s" % (self.name,slot,action))

				pid=os.getpid()
				cprint("[AUTOPIN] enigma2 pid %i" % pid)
				ci_e2_fifo=False
				ci_e2_locked=False
				if os.path.exists("/dev/ci%d" % slot):
					if stat.S_ISFIFO(os.stat("/dev/ci%d" % slot).st_mode):
						ci_e2_fifo=True
				else:
					for of in os.listdir("/proc/%i/fd" % pid):
						if os.path.exists("/proc/%i/fd/%s" % (pid,of)) and os.path.islink("/proc/%i/fd/%s" % (pid,of)):
							result=os.readlink("/proc/%i/fd/%s" % (pid,of))
							if result.startswith("/dev/ci%d" % slot):
								cprint("[AUTOPIN] enigma2 has locked /dev/ci%d" % slot)
								ci_e2_locked=True
				self.container = eConsoleAppContainer()
				if os.path.exists("/var/lib/dpkg/status"):
					self.container_appClosed_conn = self.container.appClosed.connect(self.runFinished)
				else:
					self.container.appClosed.append(self.runFinished)
				if action == "none":
					return
				elif action == "start":
					if os.path.exists("/var/run/ca/%s%d.pid" % (dreamserv,slot)):
						# already running, hence do restart
						text=_("Restart").lower()
						if not ci_e2_locked or ci_e2_fifo:
							if config.ci[slot].mmi.value or ci_e2_fifo:
								if os.path.exists(dreamso) and config.ci[slot].plus.value:
									cprint("[AUTOPIN] CI restart %d" % slot)
									dreamplus.restart(slot)
								else:
									cmd="%s restart %d" % (dreambin, slot)
									cprint("[AUTOPIN] CI command %s" % cmd)
									self.container.execute(cmd)
							else:
								if os.path.exists("/var/lib/dpkg/status"):   
        		                            			self.realinstance = eSocket_UI.getInstance()
                		            			else:                                             
                        		            			self.realinstance = socketmmi   
								mmi_number=getMMISlotNumber(slot)
								if mmi_number is not None:
									cprint("[AUTOPIN] CI MMI restart slot %d" % mmi_number)
									self.realinstance.answerEnq(mmi_number,"CA_RESTART")
						else:
							done=False
							restart=True
							text="enigma2"+" "+_("disabled")+" "+_("Slot %d") %(slot+1)+"\n\n"+_("better")+" "+_("enable")+" "+_("auto")+" "+_("Load")+_(" & ")
					else:
						text=_("enable")
						if not ci_e2_locked:
							if os.path.exists(dreamso) and config.ci[slot].plus.value:
								cprint("[AUTOPIN] CI start %d" % slot)
								dreamplus.start(slot)
							else:
								cmd="%s start %d" % (dreambin, slot)
								cprint("[AUTOPIN] CI command %s" % cmd)
								self.container.execute(cmd)
						else:
							done=False
							restart=True
							text="enigma2"+" "+_("disabled")+" "+_("Slot %d") %(slot+1)+"\n\n"+_("better")+" "+_("enable")+" "+_("auto")+" "+_("Load")+_(" & ")
				elif action == "stop":
					text=_("disable")
					if not ci_e2_locked or ci_e2_fifo:
						if config.ci[slot].mmi.value or ci_e2_fifo:
							if os.path.exists(dreamso) and config.ci[slot].plus.value:
								cprint("[AUTOPIN] CI stop %d" % slot)
								dreamplus.stop(slot)
							else:
								cmd="%s stop %d" % (dreambin, slot)
								cprint("[AUTOPIN] CI command %s" % cmd)
								self.container.execute(cmd)
						else:
							if os.path.exists("/var/lib/dpkg/status"):   
       		                            			self.realinstance = eSocket_UI.getInstance()
               		            			else:                                             
                       		            			self.realinstance = socketmmi   
							mmi_number=getMMISlotNumber(slot)
							if mmi_number is not None:
								cprint("[AUTOPIN] CI MMI stop slot %d" % mmi_number)
								self.realinstance.answerEnq(mmi_number,"CA_KILL")
					else:
						done=False
						restart=True
						text="enigma2"+" "+_("disabled")+" "+_("Slot %d") %(slot+1)+"\n\n"+_("better")+" "+_("enable")+" "+_("auto")+" "+_("Load")+_(" & ")
				elif action == "restart":
					text=_("Restart").lower()+" "+_("done!") 
					if not ci_e2_locked or ci_e2_fifo:
						if config.ci[slot].mmi.value or ci_e2_fifo:
							if os.path.exists(dreamso) and config.ci[slot].plus.value:
								cprint("[AUTOPIN] CI restart %d" % slot)
								dreamplus.restart(slot)
							else:
								cmd="%s restart %d" % (dreambin, slot)
								cprint("[AUTOPIN] CI command %s" % cmd)
								self.container.execute(cmd)
						else:
							if os.path.exists("/var/lib/dpkg/status"):   
       		                            			self.realinstance = eSocket_UI.getInstance()
               		            			else:                                             
                       		            			self.realinstance = socketmmi   
							mmi_number=getMMISlotNumber(slot)
							if mmi_number is not None:
								cprint("[AUTOPIN] CI MMI restart slot %d" % mmi_number)
								self.realinstance.answerEnq(mmi_number,"CA_RESTART")
					else:
						done=False
						restart=True
						text="enigma2"+" "+_("disabled")+" "+_("Slot %d") %(slot+1)+"\n\n"+_("better")+" "+_("enable")+" "+_("auto")+" "+_("Load")+_(" & ")
				elif action == "enable":
					restart=True
					config.ci[slot].start.value=True
					config.ci[slot].start.save()
					# make sure it is in settings file
					configfile.save()
					text=_("auto")+" "+_("enable")
				elif action == "disable":
					restart=True
					config.ci[slot].start.value=False
					config.ci[slot].start.save()
					# make sure it is in settings file
					configfile.save()
					text=_("auto")+" "+_("disable").lower()
				elif action == "info":
					done=False
					if os.path.exists(dreambin):
						# get version ...
						kitname=""
						version=""
						kitname=dreambin.replace("/usr/bin/","").replace("_","-").replace(".so","")
						kitname=kitname.lstrip("-")
						cprint("[AUTOPIN] KIT: %s" % kitname)
						if os.path.exists("/var/lib/dpkg/status"):
							p=open("/var/lib/dpkg/status")
						else:
							p=open("/var/lib/opkg/status")
						line=p.readline()
						found=False
						while line and not found:
							line=p.readline()
							if line.startswith("Package: %s" % kitname):
								found=True
								if os.path.exists("/var/lib/dpkg/status"):
									found=False
									while line and not found:
										line=p.readline()
										if line.startswith("Architecture:"):
											found=True
								version=p.readline()
								binversion=kitname+" "+version
						p.close()
					header=_("Show WLAN Status").replace("WLAN","CI")
					enabled=_("enabled")+" "+_("auto")+" "+_("Load")
					running=_("Inactive")
					# check for enabled
					if config.ci[slot].start.value:
						enabled=_("enabled")+" "+_("auto")+" "+_("Load")
					else:
						enabled=_("disabled")+" "+_("auto")+" "+_("Load")
					# check for running via pidfile
					if os.path.exists("/var/run/ca/%s%d.pid" % (dreamserv,slot)):
						running=_("Active")
					text=header+":\n\n"+enabled+" & "+running
					if ci_e2_locked:
						restart=True
						text=text+"\n\n"+"enigma2"+" "+_("disabled")+" "+_("Slot %d") %(slot+1)+" "+_("better")
				else:
#					done=False
#					text=_("do nothing")
					cprint("[AUTOPIN] CI unsupported command %s" % self.name)
					return
				cimsg= self.name+"\n\n"+text
				if done:
					cimsg= cimsg+" "+ _("done!")
				cimsg=cimsg+"\n\n"+binversion
				if restart:
					cimsg=cimsg+"\n\n"+_("Please Reboot")
					self.session.openWithCallback(self.refreshLayout(False), MessageBox, cimsg,  MessageBox.TYPE_WARNING, timeout=10) 
				else:
					self.session.openWithCallback(self.refreshLayout(False), MessageBox, cimsg,  MessageBox.TYPE_INFO, timeout=10) 
		
	def getPiconPath(self,name):
		if os.path.exists("/usr/share/enigma2/%s/skin_default/icons/%s.svg" % (autopin_skin,name)):
			return "/usr/share/enigma2/%s/skin_default/icons/%s.svg" % (autopin_skin,name)
		elif os.path.exists("/usr/share/enigma2/%s/skin_default/icons/%s.png" % (autopin_skin,name)):
			return "/usr/share/enigma2/%s/skin_default/icons/%s.png" % (autopin_skin,name)
		elif os.path.exists("/usr/share/enigma2/skin_default/icons/%s.svg" % (name)):
			return "/usr/share/enigma2/skin_default/icons/%s.svg" % (name)
		else:
			return "/usr/share/enigma2/skin_default/icons/%s.png" % (name)

	def setWindowTitle(self):
		self.setTitle(autopin_title)

		# if skin has no svg or png use default skin ones
		self["help"].instance.setPixmapFromFile(self.getPiconPath("help"))
		self["menu"].instance.setPixmapFromFile(self.getPiconPath("menu"))
		self["pvr"].instance.setPixmapFromFile(self.getPiconPath("pvr"))
		self["text"].instance.setPixmapFromFile(self.getPiconPath("text"))
		self["info"].instance.setPixmapFromFile(self.getPiconPath("info"))
		self["rewind"].instance.setPixmapFromFile(self.getPiconPath("ico_mp_rewind"))
		self["forward"].instance.setPixmapFromFile(self.getPiconPath("ico_mp_forward"))
		self["stop"].instance.setPixmapFromFile(self.getPiconPath("ico_mp_stop"))
		self["play"].instance.setPixmapFromFile(self.getPiconPath("ico_mp_play"))
		self["pause"].instance.setPixmapFromFile(self.getPiconPath("ico_mp_pause"))
		self["record"].instance.setPixmapFromFile(self.getPiconPath("record"))
		global dreambin
		global dreamserv
		if not os.path.exists(dreambin):
			self["menu"].hide()
			self["pvr"].hide()
			self["text"].hide()
			self["info"].hide()
			self["rewind"].hide()
			self["forward"].hide()
			self["stop"].hide()
			self["play"].hide()
			self["pause"].hide()
			self["record"].hide()
			self["text"].hide()
		self.addKeys(True)

        def rcKeyPressed(self, key, flag):                                            
                if (key != 207) and (key != 128) and (key != 159) and (key != 163) and (key != 168) and (key != 165):                           
			# ignore unhandled keys
			return 0
		global autopin_key_pressed
	       	if flag == 1:
			autopin_key_pressed=0
        	else:
			autopin_key_pressed=autopin_key_pressed+1
        	if autopin_key_pressed != 1: # single shot ...
        		return 0
                if (key == 207):                           
                 	cprint("[AUTOPIN] PLAY key %i flag %i" % (key,flag))
			self.playPressed()
                if (key == 128):                           
	                cprint("[AUTOPIN] STOP key %i flag %i" % (key,flag))
			self.stopPressed()
                if (key == 159) or (key == 163):                           
                	cprint("[AUTOPIN] FORWARD key %i flag %i" % (key,flag))
			self.nextPressed()
                if (key == 168) or (key == 165):                           
                   	cprint("[AUTOPIN] BACKWARD key %i flag %i" % (key,flag))
			self.previousPressed()
                return 0                                                 

	def connectHighPrioAction(self):                                              
                self.highPrioActionSlot = eActionMap.getInstance().bindAction('', -0x7FFFFFFF, self.rcKeyPressed)
                                                                                      
	def disconnectHighPrioAction(self):                                           
                self.highPrioAction = None           

	def addKeys(self,status):                                                       
		# thanks Dr. Best !                              
        	if not self.addedKeys:              
              		self.addedKeys=True            
                	self.onShow.append(self.connectHighPrioAction)
                	self.onHide.append(self.disconnectHighPrioAction)       

	def runFinished(self, retval):    
		pass

	def checkUnicable(self):
		global dreambin
		global dreamserv
		if os.path.exists(dreambin):
			if os.path.exists("/etc/enigma2/settings"):
				s=open("/etc/enigma2/settings","r")
				line=s.readline()
				while line:
					line=s.readline()
					if line.find("configMode=advanced") is not -1:
						line=s.readline()
						while ((line.find("unicableLnb") is not -1) or (line.find("advanced.sat") is not -1) or (line.find("unicableconnected") is not -1)):
							line=s.readline()
						if line.find("lof=unicable") is not -1:
							cprint("[AUTOPIN] found Unicable")
							s.close()
							return True
				s.close()
		return False

	def refreshLayout(self,first=False):
#		cprint("[AUTOPIN] updating status")
		if not first:
			if config.plugins.autopin.remote.value:
				for name in os.listdir("/etc/enigma2"):
					if name.startswith("ci0"):
						self.remote_ci0=True
					if name.startswith("ci1"):
						self.remote_ci1=True
			else:
				self.remote_ci0=False
				self.remote_ci1=False
			if self.remote_ci0 or self.remote_ci1:
				self["buttonyellow"].setText(_("FTP")+" "+_("Download"))
			else:
                		if os.path.exists("/var/lib/dpkg/status"): 
					self["buttonyellow"].setText(_("Common Interface"))
				else:
					self["buttonyellow"].setText(_("CI")+" "+_("Menu"))
		# redo the list to reflect modules inserted/ejected ...
		self.list = []
		NUM_CI=eDVBCIInterfaces.getInstance().getNumOfSlots()
		socketHandler = SocketMMIMessageHandler()
		try:
			NUM_MMI=socketHandler.numConnections()
		except:
			NUM_MMI=0
		if NUM_MMI == 0:
			if os.path.exists("/var/run/ca"):
				for name in os.listdir("/var/run/ca"):
					start="CI_"+str(NUM_MMI+1)+"_"
					if name.startswith(start):
						NUM_MMI=NUM_MMI+1
		
		cur_idx = self["config"].getCurrentIndex()
		if NUM_CI > 0:
			for slot in range(NUM_CI):
				self.checkPid(slot)
				appname = _("Slot %d") %(slot+1) + " - " + _("no module found")
				state = eDVBCI_UI.getInstance().getState(slot)
				if state == 0:
					appname = _("Slot %d") %(slot+1) + " - " + _("no module found")
				elif state == 1:	
					appname = _("Slot %d") %(slot+1) + " - " + _("init modules")
				elif state == 2:
					appname = _("Slot %d") %(slot+1) + " - " + eDVBCI_UI.getInstance().getAppName(slot)
				elif state == -1:
					mmi_name=getMMISlotName(slot)
					if mmi_name is not None:
						appname = _("Slot %d") %(slot+1) + " - " + mmi_name.replace(":","").replace("CI %s" % (slot+1),"")
				global dreambin
				global dreamserv
				self.list.append((appname, ConfigNothing(), slot, "info"))
				if config.ci[slot].autopin.value:
					self.list.append(("1 x "+_("Enter pin code")+" "+_("enabled")+" ["+_("PVR")+" "+_("disable")+"]", ConfigNothing(), 0))
				else:
					self.list.append(getConfigListEntry(_("PIN")+" [0000 = "+ _("none")+"]", config.ci[slot].pin))
				if not os.path.exists(dreambin) or not config.ci[slot].start.value:
					self.list.append(("", ConfigNothing(), 0))
				else:
					if config.ci[slot].mmi.value:
						self.list.append((_("disconnected").lower()+" "+_("MMI"), ConfigNothing(), 0))
					else:
						if config.ci[slot].ignore.value:
							self.list.append((_("Yes to all").lower()+" "+_("CI")+" "+_("Message"), ConfigNothing(), 0))
						else:
							self.list.append(getConfigListEntry(_("OK"), config.ci[slot].confirm ))
			self.list.append(("", ConfigNothing(), 0))
			self.list.append(getConfigListEntry(_("CI")+" "+_("Priority"), config.plugins.autopin.priority))
			if config.plugins.autopin.priority.value != "none":
				self.list.append(getConfigListEntry(_("CI")+" "+_("Priority")+" "+_("zap"), config.plugins.autopin.zapto))
			self.list.append(getConfigListEntry(_("CI")+" "+_("Recordings")+" "+_("Check")+ " "+_("Conflicting timer"), config.plugins.autopin.timerconflict))
			if os.path.exists(dreambin):
				if boxtype == "dm7020" or boxtype == "dm7080":
					self.list.append(getConfigListEntry(_("CI")+" "+_("Slot")+" 2 "+_("Connected to")+" "+("CI")+" "+_("Slot")+" 1 ", config.plugins.autopin.looptrough))
		else:
			self.list.append(getConfigListEntry(_("remote CI streaming"), config.plugins.autopin.remote))
			if config.plugins.autopin.remote.value:
				self.list.append(getConfigListEntry(_("Streaming")+" "+_("Server IP").replace("IP",""), config.plugins.autopin.server))
				if config.plugins.autopin.server.value=="ip":
					self.list.append(getConfigListEntry(_("IP Address"), config.plugins.autopin.ip))
				else:
					self.list.append(getConfigListEntry(_("Server IP").replace("IP",_("Name")), config.plugins.autopin.hostname))
				self.list.append(getConfigListEntry(_("Password"), config.plugins.autopin.password))
			if cur_idx > 1:
				self.AutoPinRefreshTimer.start(200, True)
				return
		if first:
			self.menuList = ConfigList(self.list)                           
                	self.menuList.list = self.list                                  
                	self.menuList.l.setList(self.list)                              
                	self["config"] = self.menuList        
			self.AutoPinRefreshTimer = eTimer()
			if os.path.exists("/var/lib/dpkg/status"):
	 			self.AutoPinRefreshTimer_conn = self.AutoPinRefreshTimer.timeout.connect(self.refreshLayout)
			else:
				self.AutoPinRefreshTimer.callback.append(self.refreshLayout)
			self.AutoPinRefreshTimer.start(200, True)
		else:
			self["help"].show()
#			if os.path.exists(dreambin):
#				self["text"].show()
			# better don't refresh while editing confirm messages ...
			if cur_idx != 2 and cur_idx != (SECOND_SLOT+2):
				self.menuList.l.setList(self.list)
			if cur_idx == 0 or cur_idx == 1:
				slot=0
				if not config.ci[slot].mmi.value:
					self["pvr"].show()
				else:
					self["pvr"].hide()
				if cur_idx == 0 or self.remote_ci0 or self.remote_ci1:
					self["text"].show()
				else:
					self["text"].hide()
			elif (cur_idx == SECOND_SLOT or cur_idx == SECOND_SLOT+1) and os.path.exists("/dev/ci1"):
				slot=1
				if not config.ci[slot].mmi.value:
					self["pvr"].show()
				else:
					self["pvr"].hide()
				if cur_idx == SECOND_SLOT or self.remote_ci0 or self.remote_ci1:
					self["text"].show()
				else:
					self["text"].hide()
			else:
				self["pvr"].hide()
				self["text"].hide()
			if cur_idx != 0 and cur_idx != SECOND_SLOT:
				self["info"].hide()
				self["menu"].hide()
				self["rewind"].hide()
				self["forward"].hide()
				self["stop"].hide()
				self["play"].hide()
				self["pause"].hide()
				self["record"].hide()
			else:
				if cur_idx == SECOND_SLOT and not os.path.exists("/dev/ci1"):
					self["info"].hide()
					self["menu"].hide()
					self["rewind"].hide()
					self["forward"].hide()
					self["stop"].hide()
					self["play"].hide()
					self["pause"].hide()
					self["record"].hide()
				else:
					if os.path.exists(dreambin):
						self["info"].show()
						self["menu"].show()
						self["rewind"].show()
						self["forward"].show()
						self["stop"].show()
						self["play"].show()
						self["record"].show()
						if cur_idx == 0:
							slot=0
						elif cur_idx == SECOND_SLOT:
							slot=1
						else:
							slot=99
						if os.path.exists("/var/run/ca/%s%d.pid" % (dreamserv,slot)):
							self["pause"].show()
						else:
							self["pause"].hide()
			if not os.path.exists(dreambin):
				self["ci0_text"].hide()
				self["ci1_text"].hide()
				self["ci0_text_rect"].hide()
				self["ci1_text_rect"].hide()
				
			for slot in range(2):
				if os.path.exists("/dev/ci%d" % slot) and (config.ci[slot].start.value or os.path.exists("/var/run/ca/%s%d.pid" % (dreamserv,slot))):
					self["ci%d_text" % slot].show()
					self["ci%d_text_rect" % slot].show()
				else:
					self["ci%d_text" % slot].hide()
					self["ci%d_text_rect" % slot].hide()
				state = eDVBCI_UI.getInstance().getState(slot)
				self["ci%s_module" % slot].hide()
				ci_e2_fifo=False
				if os.path.exists("/dev/ci%d" % slot):
					if stat.S_ISFIFO(os.stat("/dev/ci%d" % slot).st_mode):
						ci_e2_fifo=True
				if state > 0 and not ci_e2_fifo:
					self["ci%s_module" % slot].show()
				else:
					name=getMMISlotName(slot)
					if name is not None:
						length=len(name)
						if name.startswith("CI ") and length > 4:
							self["ci%s_module" % slot].show()
							module_name=name.replace(":","").replace("CI %s " % (slot+1),"")
							self["ci%s_auth1" % slot].hide()
							self["ci%s_auth2" % slot].hide()
							if os.path.exists(dreambin) and os.path.exists("/var/run/ca/%s%d.pid" % (dreamserv,slot)):
								if slot==0 or (slot==1 and os.path.exists("/dev/ci1")):
									if config.ci[slot].plus.value:
										self["ci%s_auth2" % slot].setText("+")
									else:
										self["ci%s_auth2" % slot].setText("#")
									auth="/etc/enigma2/ci_auth_%s.bin" % (slot)
									if os.path.exists(auth):
										self["ci%s_auth1" % slot].show()
										self["ci%s_auth2" % slot].show()
									auth="/etc/enigma2/ci_auth_slot_%s.bin" % (slot)
									if os.path.exists(auth):
										self["ci%s_auth1" % slot].show()
										self["ci%s_auth2" % slot].show()
									auth="/etc/enigma2/ci_auth_%s.bin" % (module_name.replace(" ","_"))
									if os.path.exists(auth):
										self["ci%s_auth1" % slot].show()
										self["ci%s_auth2" % slot].show()
									auth="/etc/enigma2/ci_auth_%s_%s.bin" % (module_name.replace(" ","_"),slot)
									if os.path.exists(auth):
										self["ci%s_auth1" % slot].show()
										self["ci%s_auth2" % slot].show()
									auth="/var/run/ca/ci_auth_slot_%s.bin" % (slot)
									if os.path.exists(auth):
										self["ci%s_auth1" % slot].show()
										self["ci%s_auth2" % slot].show()
				
				if os.path.exists(dreambin):
					enabled=config.ci[slot].start.value
					running=False
					# check for running via pidfile
					if os.path.exists("/var/run/ca/%s%d.pid" % (dreamserv,slot)):
						running=True
					self["ci%s" % slot].hide()
					if os.path.exists(dreambin):
						if enabled:							
							if running:							
#								cprint("[AUTOPIN] slot %d running and enabled!" % slot)
								self["ci%s" % slot].setBackgroundColorNum(3) # green
								self["ci%s" % slot].setForegroundColorNum(3)
							else:
#								cprint("[AUTOPIN] slot %d NOT running but enabled!" % slot)
								self["ci%s" % slot].setBackgroundColorNum(4) # yellow
								self["ci%s" % slot].setForegroundColorNum(4)
						else: # 
							if running:							
#								cprint("[AUTOPIN] slot %d NOT enabled but running!" % slot)
								self["ci%s" % slot].setBackgroundColorNum(5) # blue
								self["ci%s" % slot].setForegroundColorNum(5)
							else:
#								cprint("[AUTOPIN] slot %d NOT enabled and NOT running!" % slot)
								self["ci%s" % slot].setBackgroundColorNum(2) # red
								self["ci%s" % slot].setForegroundColorNum(2)
						servfile="/var/run/ca/ci%d.service" % (slot)
						channelref=""
						channel=""
						if os.path.exists(servfile):
							f=open(servfile,"r")
							channelref=f.readline()
							channel=f.readline()
							f.close()
						channelref=channelref.rstrip("\n")
						fullchannelref=channelref
						channel=channel.rstrip("\n")
						if channelref.startswith("1:0:"):
							if len(channelref) < 25:
								fullchannelref=channelref+"0:0:0:"
     							channel = ServiceReference(fullchannelref).getServiceName()
						if config.ci[slot].plus.value:
							self["ci%s_auth2" % slot].setText("+")
						else:
							self["ci%s_auth2" % slot].setText("#")
						if len(fullchannelref) > 20:
							streamservicefile="/tmp/stream.%s" % fullchannelref.replace("/","_")
							recordservicefile="/tmp/record.%s" % fullchannelref.replace("/","_")
							if os.path.exists(streamservicefile):
								cprint("[AUTOPIN] found stream %s" % streamservicefile)
								self["ci%s_auth2" % slot].setBackgroundColorNum(5) # blue
								self["ci%s_auth2" % slot].setForegroundColorNum(5)
							else:
								if os.path.exists(recordservicefile):
									self["ci%s_auth2" % slot].setBackgroundColorNum(2) # red
									self["ci%s_auth2" % slot].setForegroundColorNum(2)
								else:	
									self["ci%s_auth2" % slot].setBackgroundColorNum(3) # green
									self["ci%s_auth2" % slot].setForegroundColorNum(3)
						else:
							self["ci%s_auth2" % slot].setBackgroundColorNum(3) # green
							self["ci%s_auth2" % slot].setForegroundColorNum(3)
						if len(channel) < 1:
							channel=fullchannelref
						# Fake Check ...
						x=[]
						x=fullchannelref.split(":")
						if len(x) > 5:
							if int(x[0]) == 1 and (int(x[6], 16) & 0xF) == 0x1:
								fake=int(x[6], 16)
								faked=hex(fake-1).lstrip('0x').upper()
								fake_service=fullchannelref.replace(":"+x[6]+":",":"+faked+":")
								f_service=eServiceReference(fake_service)   
		     						info = eServiceCenter.getInstance().info(f_service)    
	     							channel=info.getName(f_service)                   
								cprint("[AUTOPIN] FAKES %s" % (channel))
#						cprint("[AUTOPIN] found channel %s from channelref %s" % (channel,fullchannelref))
						self["ci%s_text" % slot].setText("  %s" % channel)
					else:
#						cprint("[AUTOPIN] no binary")
						self["ci%s" % slot].setBackgroundColorNum(0) # black
						self["ci%s" % slot].setForegroundColorNum(0)
					self["ci%s" % slot].show()
					self["ci%s_back" % slot].show()
			if not os.path.exists("/dev/ci1") and not self.remote_ci1:
				self["ci1"].hide()
				self["ci1_back"].hide()
				self["ci1_module"].hide()
				self["ci1_module_back1"].hide()
				self["ci1_module_back2"].hide()
		self.AutoPinRefreshTimer.start(200, True)

	def save(self):
		self.AutoPinRefreshTimer.stop()
		for slot in range(MAX_NUM_CI):                                                  
			if config.ci[slot].start.value:
				config.ci[slot].canDescrambleMultipleServices.value="no"
#			if SystemInfo["CommonInterfaceSupportsHighBitrates"]:
#				if config.ci[slot].start.value:
#					config.ci[slot].canHandleHighBitrates.value="no"
			if config.plugins.autopin.priority.value == "recording" or config.plugins.autopin.priority.value == "both":
				config.recording.asktozap.value=True
			else:
				config.recording.asktozap.value=False
			if config.plugins.autopin.priority.value == "streaming" or config.plugins.autopin.priority.value == "both":
				config.streaming.asktozap.value=True
			else:
				config.streaming.asktozap.value=False
		config.recording.asktozap.save()
		config.streaming.asktozap.save()
		config.ci.save()

		for x in self["config"].list:
			x[1].save()

		# make sure it is in settings file
		configfile.save()
		self.close(True)

	def cancel(self):
		self.AutoPinRefreshTimer.stop()
		for x in self["config"].list:
			x[1].cancel()
		closing=True
		self.close(False)

	def pvrPressed(self):
		cprint("[AUTOPIN] PVR pressed")
		cur_idx = self["config"].getCurrentIndex()
		if cur_idx == 0:
			slot=0
			slot_string=_("Slot %d") % (slot+1)
			if config.ci[slot].mmi.value:
				text=slot_string+" "+_("MMI")+" "+_("Message")+" "+_("disabled")
				self.session.open(MessageBox, text,  MessageBox.TYPE_WARNING, timeout=10) 
				return
			if config.ci[slot].ignore.value:
				text=slot_string+" "+_("Yes to all").lower()+" "+_("CI")+" "+_("Message")
				self.session.open(MessageBox, text,  MessageBox.TYPE_WARNING, timeout=10) 
				return
			if len(config.ci[slot].confirm.value) == 0:
				# surpress all messages
				config.ci[slot].confirm.value=[2, 44, 74, 101, 103, 164, 204, 304, 349, 502, 503, 510, 535, 536, 990, 991, 992, 993]
			else:
				# allow all messages
				config.ci[slot].confirm.value=[]
		elif cur_idx == 1:
			slot=0
			slot_string=_("Slot %d") % (slot+1)
			if config.ci[slot].mmi.value:
				text=slot_string+" "+_("MMI")+" "+_("Message")+" "+_("disabled")
				self.session.open(MessageBox, text,  MessageBox.TYPE_WARNING, timeout=10) 
				return
			if config.ci[slot].ignore.value:
				text=slot_string+" "+_("Yes to all").lower()+" "+_("CI")+" "+_("Message")
				self.session.open(MessageBox, text,  MessageBox.TYPE_WARNING, timeout=10) 
				return
			if not config.ci[slot].autopin.value:
				config.ci[slot].autopin.value=True
				config.ci[slot].pin.value="0000"
				cprint("[AUTOPIN] slot %d PIN enabled ..." % slot)
			else:
				config.ci[slot].autopin.value=False
				cprint("[AUTOPIN] slot %d PIN disabled ..." % slot)
				# reset stored PIN
				pf="/var/run/ca/%s%d.pin" % (dreamserv,slot)
				if os.path.exists(pf):
					os.remove(pf)
		elif cur_idx == SECOND_SLOT and os.path.exists("/dev/ci1"):
			slot=1
			slot_string=_("Slot %d") % (slot+1)
			if config.ci[slot].mmi.value:
				text=slot_string+" "+_("MMI")+" "+_("Message")+" "+_("disabled")
				self.session.open(MessageBox, text,  MessageBox.TYPE_WARNING, timeout=10) 
				return
			if config.ci[slot].ignore.value:
				text=slot_string+" "+_("Yes to all").lower()+" "+_("CI")+" "+_("Message")
				self.session.open(MessageBox, text,  MessageBox.TYPE_WARNING, timeout=10) 
				return
			if len(config.ci[slot].confirm.value) == 0:
				# surpress all messages
				config.ci[slot].confirm.value=[2, 44, 74, 101, 103, 164, 204, 304, 349, 502, 503, 510, 535, 536, 990, 991, 992, 993]
			else:
				# allow all messages
				config.ci[slot].confirm.value=[]
		elif cur_idx == SECOND_SLOT+1 and os.path.exists("/dev/ci1"):
			slot=1
			slot_string=_("Slot %d") % (slot+1)
			if config.ci[slot].mmi.value:
				text=slot_string+" "+_("MMI")+" "+_("Message")+" "+_("disabled")
				self.session.open(MessageBox, text,  MessageBox.TYPE_WARNING, timeout=10) 
				return
			if config.ci[slot].ignore.value:
				text=slot_string+" "+_("Yes to all").lower()+" "+_("CI")+" "+_("Message")
				self.session.open(MessageBox, text,  MessageBox.TYPE_WARNING, timeout=10) 
				return
			if not config.ci[slot].autopin.value:
				config.ci[slot].autopin.value=True
				config.ci[slot].pin.value="0000"
				cprint("[AUTOPIN] slot %d PIN enabled ..." % slot)
			else:
				config.ci[slot].autopin.value=False
				cprint("[AUTOPIN] slot %d PIN disabled ..." % slot)
				# reset stored PIN
				pf="/var/run/ca/%s%d.pin" % (dreamserv,slot)
				if os.path.exists(pf):
					os.remove(pf)
		else:
			pass

	def menu(self):
		global dreambin
		global dreamserv
		if os.path.exists(dreambin):
			cur_idx = self["config"].getCurrentIndex()
			global menu_slot
			if cur_idx == 0:
				menu_slot=0
				self.session.open(AutoPinConfigurePlus)
			elif cur_idx == SECOND_SLOT and os.path.exists("/dev/ci1"):
				menu_slot=1
				self.session.open(AutoPinConfigurePlus)

	def info(self):
		cur_idx = self["config"].getCurrentIndex()
	#       print cur_idx
		if cur_idx == 0:
			self.okPressed("info")
		if cur_idx == SECOND_SLOT and os.path.exists("/dev/ci1"):
			self.okPressed("info")

	def logging(self):
		cur_idx = self["config"].getCurrentIndex()
		if cur_idx == 0 or (cur_idx == SECOND_SLOT and os.path.exists("/dev/ci1")):
			if cur_idx == 0:
				slot=0
			if cur_idx == SECOND_SLOT:
				slot=1
        		if config.ci[slot].logging.value:                  
				cprint("[AUTOPIN] logging ...")
        			config.ci[slot].logging.value=False                  
	                	config.ci[slot].logging.save()                    
				# make sure it is in settings file
	  			configfile.save()
				self.session.open(MessageBox, _("Log")+" "+_("disabled")+"\n"+_("Restart")+" "+_("CI") , MessageBox.TYPE_INFO)
			else:
        			config.ci[slot].logging.value=True                 
	                	config.ci[slot].logging.save()                    
				# make sure it is in settings file
				configfile.save()
				self.session.open(MessageBox, _("Log")+" "+_("enabled")+"\n"+_("Restart")+" "+_("CI")  , MessageBox.TYPE_INFO)

	def about(self):
		self.session.open(MessageBox, autopin_title+"\n\n"+autopin_support , MessageBox.TYPE_INFO)

	def interface(self):
		if self.remote_ci1 or self.remote_ci0:
			self.loadFTP()
		else:
			try:
				self.session.open(CiSelectionPlus)
			except:
				CiSelectionPlus(self.session)
				cprint("[AUTOPIN] no CI Menu")
				self.close()

	def loadFTP(self):
		cprint("[AUTOPIN] FTP Download ci*.xml")
		for name in os.listdir("/etc/enigma2"):
			if name.startswith("ci") and name.endswith(".xml"):
				if os.path.exists("/etc/enigma2/%s" % name):
					os.remove("/etc/enigma2/%s" % name)
		if config.plugins.autopin.server.value=="ip":
	               	host = "%d.%d.%d.%d" % tuple(config.plugins.autopin.ip.value)
		else:
			host = config.plugins.autopin.hostname.value
		port=21
		self.tmpname="/tmp/ci.xml"
		try:
			ftp=FTP()
			ftp.connect(host,port) 
	                password = str(config.plugins.autopin.password.value)
	                username = "root"
			if len(password) == 0:
				ftp.login(username)
			else:
				ftp.login(username,password)
			remote_path="/etc/enigma2"
			ftp.cwd(remote_path)
			data = []
			ftp.dir(data.append)
			file=[]
			for line in data:
				file=line.split()
				length=len(file)
				filename=file[length-1]
				type=file[0]
				link=file[length-3]
#				print ">>>>>>>>>>", filename, link, type
				if filename.startswith("/etc/enigma2/ci") and filename.endswith(".xml") and type.startswith("l"): # symlink
					if not os.path.exists(filename):
						ftp.retrbinary('RETR %s' % filename, open(filename, 'wb').write)
					if os.path.exists("/etc/enigma2/%s" % link):
						os.remove("/etc/enigma2/%s" % link)
					os.symlink(filename ,"/etc/enigma2/%s" % link)
				else:
					if filename.startswith("ci") and filename.endswith(".xml"):
						if not os.path.exists("/etc/enigma2/%s" % filename):
							ftp.retrbinary('RETR %s' % filename, open("/etc/enigma2/%s" % filename, 'wb').write)
			ftp.quit()
			text=_("FTP")+" "+_("Download")+" ci*.xml "+_("done")
			cprint("[AUTOPIN] %s" % text)
			self.session.open(MessageBox, text, MessageBox.TYPE_INFO)
		except:
			text=_("FTP")+" "+_("Download")+" ci*.xml "+_("failed")
			cprint("[AUTOPIN] %s" % text)
			self.session.open(MessageBox, text, MessageBox.TYPE_ERROR)

	def assign(self):
		if os.path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/CommonInterfaceAssignment"):
			try:
				self.session.open(CIselectMainMenuPlus)
			except:
				self.about()
		else:
			self.about()

class AutoPinConfigurePlus(Screen, ConfigListScreen):
# Full HD skin
	if size_w > 1280: 
		skin = """
		<screen position="center,center" size="1010,780" title="Auto Pin" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="10,10" size="240,40" alphatest="on" />
	     	<ePixmap pixmap="skin_default/buttons/green.png" position="260,10" size="240,40" alphatest="on" />
	    	<ePixmap pixmap="skin_default/buttons/yellow.png" position="510,10" size="240,40" alphatest="on" />
     		<ePixmap pixmap="skin_default/buttons/blue.png" position="760,10" size="240,40" alphatest="on" />
	    	<widget name="buttonred" position="10,10" size="240,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
	    	<widget name="buttongreen" position="260,10" size="240,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
	    	<widget name="buttonyellow" position="510,10" size="240,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
	    	<widget name="buttonblue" position="760,10" size="240,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		<eLabel position="10,65" size="1000,1" backgroundColor="grey" />
		<widget name="config" position="10,80" size="990,500" scrollbarMode="showOnDemand" />
		</screen>"""
	else:
# other skin
                # only DreamOS scales Buttons :-(                                     
                if os.path.exists("/var/lib/dpkg/status"): 
			skin = """
			<screen position="center,120" size="820,520" title="Auto Pin" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="10,5" size="200,40" alphatest="on" />
		     	<ePixmap pixmap="skin_default/buttons/green.png" position="210,5" size="200,40" alphatest="on" />
		    	<ePixmap pixmap="skin_default/buttons/yellow.png" position="410,5" size="200,40" alphatest="on" />
	     		<ePixmap pixmap="skin_default/buttons/blue.png" position="610,5" size="200,40" alphatest="on" />
		    	<widget name="buttonred" position="10,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		    	<widget name="buttongreen" position="210,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		    	<widget name="buttonyellow" position="410,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		    	<widget name="buttonblue" position="610,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
			<eLabel position="10,50" size="800,1" backgroundColor="grey" />
		    	<widget name="config" position="10,60" size="800,330" enableWrapAround="1" scrollbarMode="showOnDemand" />
			</screen>"""
		else:
			skin = """
			<screen position="center,120" size="820,520" title="Auto Pin" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="10,5" size="150,40" alphatest="on" />
		     	<ePixmap pixmap="skin_default/buttons/green.png" position="230,5" size="150,40" alphatest="on" />
		    	<ePixmap pixmap="skin_default/buttons/yellow.png" position="450,5" size="150,40" alphatest="on" />
	     		<ePixmap pixmap="skin_default/buttons/blue.png" position="670,5" size="150,40" alphatest="on" />
		    	<widget name="buttonred" position="10,5" size="150,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		    	<widget name="buttongreen" position="230,5" size="150,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		    	<widget name="buttonyellow" position="450,5" size="150,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
		    	<widget name="buttonblue" position="670,5" size="150,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
			<eLabel position="10,50" size="800,1" backgroundColor="grey" />
		    	<widget name="config" position="10,60" size="800,330" enableWrapAround="1" scrollbarMode="showOnDemand" />
			</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
     		self.skin = AutoPinConfigurePlus.skin 
		global menu_slot
		self.list = []                                                  

		ConfigListScreen.__init__(self, self.list, session = self.session)
		# remember old values
 	        self.mmi=config.ci[menu_slot].mmi.value
 	        self.classic=config.ci[menu_slot].classic.value
 	        self.plus=config.ci[menu_slot].plus.value
 	        self.quiet=config.ci[menu_slot].quiet.value

		self.createSetup()       
	        self.onShown.append(self.setWindowTitle)                                                            
                self.onLayoutFinish.append(self.refreshLayout)
		global dreambin
		global dreamserv
        	# explizit check on every entry                                                                     
        	self.onChangedEntry = []                                                                            
		self["buttonred"] = Label(_("Exit"))
		self["buttongreen"] = Label(_("Save"))
		self["buttonyellow"] = Label(_("Message"))
		self["buttonblue"] = Label(_("About"))
		self["actions"] = ActionMap(["WizardActions", "ColorActions", "MenuActions"], {"red": self.cancel, "green": self.leave, "blue": self.about, "yellow": self.messages, "back": self.cancel, "menu": self.cancel  }, -1) 

	def setWindowTitle(self):                                                                               
		global menu_slot
        	self.setTitle(_("Auto Pin")+" "+_("Extended Setup...").replace("...","").replace("-"," ")+": "+_("Slot %d") % (menu_slot+1))

	def createSetup(self):                                                  
		# init only on first run
		self.refreshLayout(True)

	def refreshLayout(self,first=False):
		global menu_slot
                self.list = []
                self.list.append(getConfigListEntry(_("enable")+" "+"1 x "+_("Enter pin code"), config.ci[menu_slot].autopin))
		self.list.append(getConfigListEntry(_("Yes to all").lower()+" "+_("CI")+" "+_("Message"), config.ci[menu_slot].ignore))
		if os.path.exists(dreambin) and config.ci[menu_slot].start.value:
			self.list.append(getConfigListEntry(_("disconnected").lower()+" "+_("MMI"), config.ci[menu_slot].mmi))
	 	        self.list.append(getConfigListEntry(_("enable")+" "+_("better")+ " "+_("CI")+" "+_("Devices"), config.ci[menu_slot].plus))
	 	        self.list.append(getConfigListEntry(_("enable")+" "+_("CI")+" "+_("init module")+" "+_("Classic").lower(), config.ci[menu_slot].classic)) 	        
	 	        self.list.append(getConfigListEntry(_("disable")+" "+_("CI")+" "+_("init module").replace("...","").replace("-"," ")+" "+_("Save").lower()+ " /etc/enigma2", config.ci[menu_slot].quiet))
		else:
			self.list.append(getConfigListEntry(_("remote CI streaming"), config.plugins.autopin.remote))
			if config.plugins.autopin.remote.value:
				self.list.append(getConfigListEntry(_("Streaming")+" "+_("Server IP").replace("IP",""), config.plugins.autopin.server))
				if config.plugins.autopin.server.value=="ip":
					self.list.append(getConfigListEntry(_("IP Address"), config.plugins.autopin.ip))
				else:
					self.list.append(getConfigListEntry(_("Server IP").replace("IP",_("Name")), config.plugins.autopin.hostname))
				self.list.append(getConfigListEntry(_("Password"), config.plugins.autopin.password))
			cur_idx = self["config"].getCurrentIndex()
			if cur_idx > 1:
				self.AutoPinConfigRefreshTimer.start(200, True)
				return
		if first:
			self.menuList = ConfigList(self.list)                           
	               	self.menuList.list = self.list                                  
	               	self.menuList.l.setList(self.list)                              
	               	self["config"] = self.menuList        
			self.AutoPinConfigRefreshTimer = eTimer()
			if os.path.exists("/var/lib/dpkg/status"):
	 			self.AutoPinConfigRefreshTimer_conn = self.AutoPinConfigRefreshTimer.timeout.connect(self.refreshLayout)
			else:
				self.AutoPinConfigRefreshTimer.callback.append(self.refreshLayout)
			self.AutoPinConfigRefreshTimer.start(200, True)
		else:
			self.menuList.l.setList(self.list)
			self.AutoPinConfigRefreshTimer.start(200, True)

        def leave(self):
		global menu_slot
		if config.ci[menu_slot].autopin.value and config.ci[menu_slot].mmi.value:
                        error=_("enable")+" "+"1 x "+_("Enter pin code")+" & "+_("disable")+" "+_("CI")+" "+_("Message")+" - "+_("not configured")
			self.session.open(MessageBox, error , MessageBox.TYPE_ERROR)
			return
		if config.ci[menu_slot].autopin.value:
			config.ci[menu_slot].pin.value="0000"
			cprint("[AUTOPIN] slot %d PIN enabled ..." % menu_slot)
		else:
			cprint("[AUTOPIN] slot %d PIN disabled ..." % menu_slot)
			# reset stored PIN
			pf="/var/run/ca/%s%d.pin" % (dreamserv,menu_slot)
			if os.path.exists(pf):
				os.remove(pf)
		config.ci[menu_slot].autopin.save()
		config.ci[menu_slot].pin.save()
		# check if expert settings need reboot
		reboot=False
 	        if self.mmi != config.ci[menu_slot].mmi.value:
			reboot=True
 	        if self.classic != config.ci[menu_slot].classic.value:
			reboot=True
 	        if self.plus != config.ci[menu_slot].plus.value:
			reboot=True
 	        if self.quiet != config.ci[menu_slot].quiet.value:
			reboot=True
		if reboot:
			question=_("Do you want to reboot your Dreambox?")
	                self.session.openWithCallback(self.reboot_confirmed,MessageBox,question, MessageBox.TYPE_YESNO)
		else:
			config.ci[menu_slot].mmi.save()
			config.ci[menu_slot].quiet.save()
			config.ci[menu_slot].ignore.save()
			config.ci[menu_slot].plus.save()
			config.ci[menu_slot].classic.save()
			# make sure it is in settings file
			configfile.save()
			self.close(True)

        def reboot_confirmed(self,answer):
		global menu_slot
                if answer is True:
			config.ci[menu_slot].mmi.save()
			config.ci[menu_slot].quiet.save()
			config.ci[menu_slot].ignore.save()
			config.ci[menu_slot].plus.save()
			config.ci[menu_slot].classic.save()
			# make sure it is in settings file
			configfile.save()
                        quitMainloop(2) 
		else:
			config.ci[menu_slot].mmi.cancel()
			config.ci[menu_slot].quiet.cancel()
			config.ci[menu_slot].ignore.cancel()
			config.ci[menu_slot].plus.cancel()
			config.ci[menu_slot].classic.cancel()
			# make sure it is in settings file
			configfile.save()
                        question=("Reboot")+" "+_("unconfirmed").lower()
			self.session.open(MessageBox, question , MessageBox.TYPE_WARNING)

    	def cancel(self):                                                                                                         
		global menu_slot
		config.ci[menu_slot].quiet.cancel()
		config.ci[menu_slot].ignore.cancel()
		config.ci[menu_slot].plus.cancel()
		config.ci[menu_slot].classic.cancel()
		config.ci[menu_slot].autopin.cancel()
        	self.close(False)       

        def about(self):
		self.session.open(MessageBox, autopin_title+"\n\n"+autopin_support , MessageBox.TYPE_INFO)

        def messages(self):
		self.session.open(MessageBox, autopin_help, MessageBox.TYPE_WARNING)

def startAutoPin(session, **kwargs):
	session.open(AutoPin)    

def autostart(reason,**kwargs):
	if kwargs.has_key("session") and reason == 0:           
		session = kwargs["session"]                       
		cprint("[AUTOPIN] autostart")
		config.misc.standbyCounter.addNotifier(AutoPinOnStandby, initial_call = False)
		if not os.path.exists("/var/run/ca"):
			os.mkdir("/var/run/ca")
		if not os.path.exists("/var/run/ca"):
			os.mkdir("/var/run/ca")
		# adding PIN to settings
		InitCiConfigPlus()

		for slot in range(MAX_NUM_CI):                                                  
			# disable features that AutoPin doesn't need ...
                	config.ci[slot].null = ConfigYesNo(default=False)
                        config.ci[slot].null.value=False               
                	config.ci[slot].null.save()                    
		for name in os.listdir("/tmp"):
			# clean stream service files ...
			if name.startswith("stream.1:0"):
				os.remove("/tmp/%s" % name)
			# clean record service files ...
			if name.startswith("record.1:0"):
				os.remove("/tmp/%s" % name)

		if not os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data"):
			cprint("[AUTOPIN] finds NO suitable web interface")
			session.open(AutoPinCheck)
			return
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/pin.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/pin.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/pin.png")
			if os.path.exists("%s/pin.png" % autopin_plugindir):
				os.symlink("%s/pin.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/pin.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/green_box1.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/green_box1.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/green_box1.png")
			if os.path.exists("%s/green_box1.png" % autopin_plugindir):
				os.symlink("%s/green_box1.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/green_box1.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/green_box2.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/green_box2.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/green_box2.png")
			if os.path.exists("%s/green_box2.png" % autopin_plugindir):
				os.symlink("%s/green_box2.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/green_box2.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow_box1.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow_box1.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow_box1.png")
			if os.path.exists("%s/yellow_box1.png" % autopin_plugindir):
				os.symlink("%s/yellow_box1.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow_box1.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow_box2.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow_box2.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow_box2.png")
			if os.path.exists("%s/yellow_box2.png" % autopin_plugindir):
				os.symlink("%s/yellow_box2.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow_box2.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/red_box1.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/red_box1.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/red_box1.png")
			if os.path.exists("%s/red_box1.png" % autopin_plugindir):
				os.symlink("%s/red_box1.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/red_box1.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/red_box2.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/red_box2.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/red_box2.png")
			if os.path.exists("%s/red_box2.png" % autopin_plugindir):
				os.symlink("%s/red_box2.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/red_box2.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/blue_box1.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/blue_box1.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/blue_box1.png")
			if os.path.exists("%s/blue_box1.png" % autopin_plugindir):
				os.symlink("%s/blue_box1.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/blue_box1.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/blue_box2.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/blue_box2.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/blue_box2.png")
			if os.path.exists("%s/blue_box2.png" % autopin_plugindir):
				os.symlink("%s/blue_box2.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/blue_box2.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/black_box1.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/black_box1.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/black_box1.png")
			if os.path.exists("%s/black_box1.png" % autopin_plugindir):
				os.symlink("%s/black_box1.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/black_box1.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/black_box2.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/black_box2.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/black_box2.png")
			if os.path.exists("%s/black_box2.png" % autopin_plugindir):
				os.symlink("%s/black_box2.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/black_box2.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/white_outline.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/white_outline.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/white_outline.png")
			if os.path.exists("%s/white_outline.png" % autopin_plugindir):
				os.symlink("%s/white_outline.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/white_outline.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow_outline.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow_outline.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow_outline.png")
			if os.path.exists("%s/yellow_outline.png" % autopin_plugindir):
				os.symlink("%s/yellow_outline.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow_outline.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/white_bar.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/white_bar.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/white_bar.png")
			if os.path.exists("%s/white_bar.png" % autopin_plugindir):
				os.symlink("%s/white_bar.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/white_bar.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_red.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_red.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_red.png")
			if os.path.exists("%s/plus_icon_red.png" % autopin_plugindir):
				os.symlink("%s/plus_icon_red.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_red.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_green.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_green.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_green.png")
			if os.path.exists("%s/plus_icon_green.png" % autopin_plugindir):
				os.symlink("%s/plus_icon_green.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_green.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_yellow.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_yellow.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_yellow.png")
			if os.path.exists("%s/plus_icon_yellow.png" % autopin_plugindir):
				os.symlink("%s/plus_icon_yellow.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_yellow.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_blue.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_blue.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_blue.png")
			if os.path.exists("%s/plus_icon_blue.png" % autopin_plugindir):
				os.symlink("%s/plus_icon_blue.png" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/plus_icon_blue.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/css") is False:
			os.mkdir("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/css")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/css/auto_pin.css") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/css/auto_pin.css") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/css/auto_pin.css")
			if os.path.exists("%s/auto_pin.css" % autopin_plugindir):
				os.symlink("%s/auto_pin.css" % autopin_plugindir,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/css/auto_pin.css")

		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_rewind.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_rewind.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_rewind.png")
			if os.path.exists("/usr/share/enigma2/%s/skin_default/icons/ico_mp_rewind.png" % autopin_skin):
				os.symlink("/usr/share/enigma2/%s/skin_default/icons/ico_mp_rewind.png" % autopin_skin,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_rewind.png")
			else:
				os.symlink("/usr/share/enigma2/skin_default/icons/ico_mp_rewind.png","/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_rewind.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_forward.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_forward.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_forward.png")
			if os.path.exists("/usr/share/enigma2/%s/skin_default/icons/ico_mp_forward.png" % autopin_skin):
				os.symlink("/usr/share/enigma2/%s/skin_default/icons/ico_mp_forward.png" % autopin_skin,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_forward.png")
			else:
				os.symlink("/usr/share/enigma2/skin_default/icons/ico_mp_forward.png","/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_forward.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_play.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_play.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_play.png")
			if os.path.exists("/usr/share/enigma2/%s/skin_default/icons/ico_mp_play.png" % autopin_skin):
				os.symlink("/usr/share/enigma2/%s/skin_default/icons/ico_mp_play.png" % autopin_skin,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_play.png")
			else:
				os.symlink("/usr/share/enigma2/skin_default/icons/ico_mp_play.png","/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_play.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_pause.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_pause.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_pause.png")
			if os.path.exists("/usr/share/enigma2/%s/skin_default/icons/ico_mp_pause.png" % autopin_skin):
				os.symlink("/usr/share/enigma2/%s/skin_default/icons/ico_mp_pause.png" % autopin_skin,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_pause.png")
			else:
				os.symlink("/usr/share/enigma2/skin_default/icons/ico_mp_pause.png","/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_pause.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_stop.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_stop.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_stop.png")
			if os.path.exists("/usr/share/enigma2/%s/skin_default/icons/ico_mp_stop.png" % autopin_skin):
				os.symlink("/usr/share/enigma2/%s/skin_default/icons/ico_mp_stop.png" % autopin_skin,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_stop.png")
			else:
				os.symlink("/usr/share/enigma2/skin_default/icons/ico_mp_stop.png","/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/ico_mp_stop.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/record.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/record.png") is True:
				os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/record.png")
			if os.path.exists("/usr/share/enigma2/%s/skin_default/icons/record.png" % autopin_skin):
				os.symlink("/usr/share/enigma2/%s/skin_default/icons/record.png" % autopin_skin,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/record.png")
			else:
				os.symlink("/usr/share/enigma2/skin_default/icons/record.png","/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/record.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/red.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/red.png") is True:
			    os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/red.png")
			if os.path.exists("/usr/share/enigma2/%s/skin_default/buttons/red.png" % autopin_skin):
				os.symlink("/usr/share/enigma2/%s/skin_default/buttons/red.png" % autopin_skin,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/red.png")
			else:
				os.symlink("/usr/share/enigma2/skin_default/buttons/red.png","/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/red.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/green.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/green.png") is True:
			    os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/green.png")
			if os.path.exists("/usr/share/enigma2/%s/skin_default/buttons/green.png" % autopin_skin):
				os.symlink("/usr/share/enigma2/%s/skin_default/buttons/green.png" % autopin_skin,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/green.png")
			else:
				os.symlink("/usr/share/enigma2/skin_default/buttons/green.png","/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/green.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/blue.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/blue.png") is True:
			    os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/blue.png")
			if os.path.exists("/usr/share/enigma2/%s/skin_default/buttons/blue.png" % autopin_skin):
				os.symlink("/usr/share/enigma2/%s/skin_default/buttons/blue.png" % autopin_skin,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/blue.png")
			else:
				os.symlink("/usr/share/enigma2/skin_default/buttons/blue.png","/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/blue.png")
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow.png") is False:
			if os.path.lexists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow.png") is True:
			    os.remove("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow.png")
			if os.path.exists("/usr/share/enigma2/%s/skin_default/buttons/yellow.png" % autopin_skin):
				os.symlink("/usr/share/enigma2/%s/skin_default/buttons/yellow.png" % autopin_skin,"/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow.png")
			else:
				os.symlink("/usr/share/enigma2/skin_default/buttons/yellow.png","/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/web-data/img/yellow.png")
		session.open(AutoPinCheck)

def AutoPinOnStandby(reason):
	cprint("[AUTOPIN] entering Standby/Idle")
	from Screens.Standby import inStandby                           
        inStandby.onClose.append(AutoPinPowerOn)                   
	if config.plugins.autopin.remote.value:
		cprint("[AUTOPIN] CHECKING REMOTE CI")
		from API import session
		serviceref = session.nav.getCurrentlyPlayingServiceReference()
		if serviceref is None:
			cprint("[AUTOPIN] ALREADY STOPPED STREAM")
			return
		ref=serviceref.toString()
		if ref.find("//") is -1: # no stream
			return
		needs_ci1=checkCI(serviceref,0)
		if needs_ci1 is not -1:
			cprint("[AUTOPIN] STOPS REMOTE CI0")
			session.nav.stopService()
		needs_ci2=checkCI(serviceref,1)
		if needs_ci2 is not -1:
			cprint("[AUTOPIN] STOPS REMOTE CI1")
			session.nav.stopService()

def AutoPinPowerOn():                                              
        cprint("[AUTOPIN] booting or leaving Standby/Idle")


class AutoPinCheck(Screen):
    def __init__(self,session):
	self.session = session
        self.altshift = []
	Screen.__init__(self,session)
       	self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
      		{                                 
      		iPlayableService.evSeekableStatusChanged: self.EventSeekable,
       		iPlayableService.evStart: self.EventStart,
      		iPlayableService.evEnd: self.EventEnd,
      		iPlayableService.evEOF: self.EventEOF,
      		iPlayableService.evSOF: self.EventSOF,
      		iPlayableService.evCuesheetChanged: self.EventCue,
      		iPlayableService.evBuffering: self.EventBuffer,
       		iPlayableService.evStopped: self.EventStopped,
      		iPlayableService.evUpdatedInfo: self.EventInfo,
      		})                                                      

    def EventEOF(self):                                         
	cprint("[AUTOPIN] EOF")
    def EventInfo(self):                                         
	cprint("[AUTOPIN] Info")
	if config.plugins.autopin.looptrough.value:
		cprint("[AUTOPIN] checking CI0")
		serviceref = self.session.nav.getCurrentlyPlayingServiceReference()
		needs_ci1=checkCI(serviceref,0)
		if needs_ci1 is not -1:
			cprint("[AUTOPIN] needs CI0")
			f=open("/proc/stb/tsmux/ci0_input","r")
			tuner=f.read()
			f.close()
			cprint("[AUTOPIN] CI0 uses tuner %s" % tuner)
			if not tuner.startswith("CI"):
				cprint("[AUTOPIN] CI1 switched to tuner %s" % tuner)
				f=open("/proc/stb/tsmux/ci1_input","w")
				f.write(tuner)
				f.close()
				cprint("[AUTOPIN] CI0 switched to CI1")
				f=open("/proc/stb/tsmux/ci0_input","w")
				f.write("CI1")
				f.close()

	if config.plugins.autopin.remote.value:
		cprint("[AUTOPIN] CHECKING CI")
		serviceref = self.session.nav.getCurrentlyPlayingServiceReference()
		if serviceref is None:
			return
		ref=serviceref.toString()
		if ref.find("//") is not -1: # prevent circular call
			return
		needs_ci1=checkCI(serviceref,0)
		if needs_ci1 is not -1:
			cprint("[AUTOPIN] NEEDS REMOTE CI0")
		needs_ci2=checkCI(serviceref,1)
		if needs_ci2 is not -1:
			cprint("[AUTOPIN] NEEDS REMOTE CI1")
		if needs_ci1 is -1 and needs_ci2 is -1:
			return
		if config.plugins.autopin.server.value=="ip":
                	host = "%d.%d.%d.%d" % tuple(config.plugins.autopin.ip.value)
		else:
			host = config.plugins.autopin.hostname.value
		rhost,resolv=self.checkHost(host)
                if resolv is None: 
			cprint("[AUTOPIN] HOST NOT REACHABLE")
			return
               	password = str(config.plugins.autopin.password.value)
		port = "8001"
               	username = "root"
		if len(password) == 0:
                	http = "http://%s:%s/" % (host,port)       
		else:
                	http = "http://%s:%s@%s:%s/" % (username,password,host,port)       
		http=http.replace(":","%3a")
		sp=[]
		sp=ref.split(":")
		ll=len(sp)
		href="%3a".join(map(str,sp[:ll]))
		sp[1]=256 # change stream service reference for retry ...
		nref=":".join(map(str,sp[:ll]))
		teservice=nref+http+href
		cprint("[AUTOPIN] PLAYS REMOTE %s" % teservice)
		teref = eServiceReference(teservice)    
		self.session.nav.playService(teref)

    def checkHost(self,host):                             
        resolv=None                                     
        try:                                                   
                resolv=getaddrinfo(host,None)                           
        except gaierror:                                                
                cprint("[AUTOPIN] HOST ERROR %s" % host)               
        return host, resolv      

    def EventSOF(self):                                         
	cprint("[AUTOPIN] SOF")
    def EventCue(self):                                         
	cprint("[AUTOPIN] Cue")
    def EventBuffer(self):                                         
	cprint("[AUTOPIN] Buffer")
    def EventEnd(self):                                         
	cprint("[AUTOPIN] END")
    def EventStart(self):                                         
	cprint("[AUTOPIN] START")
    def EventStopped(self):                                         
	cprint("[AUTOPIN] STOPPED")
    def EventSeekable(self):                                         
	cprint("[AUTOPIN] SEEKABLE changed")
     	service = self.session.nav.getCurrentService()

def startTunerState(session):
        fe_data = { }                                                           
        self.frontend.getFrontendStatus(fe_data)                                
        stop = False                                                            
        state = fe_data["tuner_state"]                                          
        cprint("[AUTOPIN] status: %s" % state)                                              

###############################################################################
# Auto Pin Webinterface by gutemine and coded by GreatGreyWolfSif
###############################################################################
autopin_webif_title = _("Auto Pin Webinterface by gutemine Version %s") % autopin_version 

class AutoPinChild(resource.Resource):
	def __init__(self,session):
		self.session = session
		self.putChild('autopin',AutoPinWebif())

class AutoPinWebif(resource.Resource):

	def checkPid(self,slot):                                         
		global dreambin
		global dreamserv
		pf="/var/run/ca/%s%d.pid" % (dreamserv,slot)
		if os.path.exists(pf):
			f=open(pf,"r")
			pid=f.read().rstrip("\n")
			f.close()
			if os.path.exists("/proc/%s" % pid):
				return True
			else:
				os.remove(pf)
		return False

	def escape_html(self, text):
	    	"""escape strings for display in HTML"""
		text2 = re.sub('[^a-zA-Z0-9 \n\.\-\&\+\!]', '', text)
	    	text3 = text2.replace("&","&amp;")
	    	text4 = text3.replace("-","&middot;") # 45 failed ?
	    	text5 = text4.replace("+","&#43;")
	    	text6 = text5.replace("!","&#33;")
	    	result= text6.replace(" ","&nbsp;")
#	    	print ">>>>>>", text, result
		return result

	def render(self, req):
		global dreambin
		global dreamserv
		self.checkPid(0)
		self.checkPid(1)
		self.container = eConsoleAppContainer()
#		if os.path.exists("/var/lib/dpkg/status"):
#			self.container_appClosed_conn = self.container.appClosed.connect(self.runFinished)
#		else:
#			self.container.appClosed.append(self.runFinished)
		enabled0=config.ci[0].start.value
		running0=False
		# check for running via pidfile
		if os.path.exists("/var/run/ca/%s0.pid" % (dreamserv)):
			running0=True
		running1=False
		enabled1=config.ci[1].start.value
		if os.path.exists("/var/run/ca/%s1.pid" % (dreamserv)):
			running1=True
			
		# check for module names
		module_name=["",""]
		start0="CI_1_"
		start1="CI_2_"
		for name in os.listdir("/var/run/ca"):
			if name.startswith(start0):
				module_name[0]=name.replace("_"," ").replace(start0,"")
			if name.startswith(start1):
				module_name[1]=name.replace("_"," ").replace(start1,"")

		binversion=""
		restart=False
		done=True
		if os.path.exists(dreambin):
			pid=os.getpid()
#			cprint("[AUTOPIN] enigma2 pid %i" % pid)
			ci_e2_locked=[False,False]
			for of in os.listdir("/proc/%i/fd" % pid):
				if os.path.exists("/proc/%i/fd/%s" % (pid,of)) and os.path.islink("/proc/%i/fd/%s" % (pid,of)):
					result=os.readlink("/proc/%i/fd/%s" % (pid,of))
					if result.startswith("/dev/ci0"):
#						cprint("[AUTOPIN] enigma2 has locked /dev/ci0")
						ci_e2_locked[0]=True
					if result.startswith("/dev/ci1"):
#						cprint("[AUTOPIN] enigma2 has locked /dev/ci1")
						ci_e2_locked[1]=True

		req.setHeader('Content-type', 'text/html')
		req.setHeader('charset', 'UTF-8')

		""" rendering server response """
		command = req.args.get("cmd",None)
		if command is not None:
			cprint("[AUTOPIN] >>>>>>>>> %s" % command[0])
			
		coded_string=_("coded by")+" "+"GreatGreyWolfSif"
		slot_string=_("Slot %d")
		mainmenu_string=_("Auto Pin Main Menu")
		refresh_string=_("Refresh")
		save_string=_("Save")
		done_string=_("done!")
		assign_string_full=_("CI assignment")+" + "+_("Auto Pin V%s") % autopin_version
		assign_string=_("CI assignment")
		about_string=_("About")
		ci_string_full=_("Common Interface")+" + "+_("Auto Pin V%s") % autopin_version
		ci_string=_("Common Interface")
		return_string=_("Back")
		ok_string=_("OK")
		
		reset_string=_("Reset")
		
		none_string=_("none")
		recording_string=_("Recordings")
		streaming_string=_("Streaming")
		both_string=_("Recordings")+" & "+_("Streaming")
		
		no_string=_("no")
		yes_string=_("yes")
		auto_string=_("auto")
		
		inactive_string=_("no")
		active_string=_("yes")
		disable_string=_("disable")
		enable_string=_("enable")  
		
		header_string=autopin_webif_title
		priority_string=_("CI")+" "+_("Priority")
		priority_zap_string=_("CI")+" "+_("Priority")+" "+_("zap")
		pin_string=_("PIN")+" [0000 = "+ _("none")+"]"
		mmi_string=_("MMI")+" "+_("Message")+" "+_("OK")
		message_string=_("OK")
		high_bitrate_string=_("High bitrate support")
		multiple_string=_("Multiple service support")
		
		slot1_string=_("Slot %d") % (1)
		slot2_string=_("Slot %d") % (2)
		reset_ci_string=_("Reset")
		init_ci_string=_("Init")
		
		xml_error_str=_("Error")+" "+_("XML")
		
		mmi_disabled=_("MMI")+" "+_("Message")+" "+_("disabled")
		
		choice_message = ["2","44","74","101","103","164","204","304","349","502","503","510","535","536","990","991","992","993"]
		choice_len = len(choice_message)
		
		channelname0 = ""
		servfile="/var/run/ca/ci0.service"
		channelref=""
		channel=""
		
		streaming0=False
		recording0=False
		if os.path.exists(servfile):
			f=open(servfile,"r")
			channelref=f.readline()
			channel=f.readline()
			f.close()
			channelref=channelref.rstrip("\n")
			fullchannelref=channelref
			channel=channel.rstrip("\n")
			if channelref.startswith("1:0:"):
				if len(channelref) < 25:
					fullchannelref=channelref+"0:0:0:"
     				channel = ServiceReference(fullchannelref).getServiceName()
				if len(channel) < 1:
					channelname0=fullchannelref
				else:
					channelname0=channel
			if len(fullchannelref) > 20:
				streamservicefile="/tmp/stream.%s" % fullchannelref.replace("/","_")
				recordservicefile="/tmp/record.%s" % fullchannelref.replace("/","_")
				if os.path.exists(streamservicefile):
					streaming0=True
				if os.path.exists(recordservicefile):
					recording0=True

		channelname1 = ""
		servfile="/var/run/ca/ci1.service"
		channelref=""
		channel=""
		streaming1=False
		recording1=False
		if os.path.exists(servfile):
			f=open(servfile,"r")
			channelref=f.readline()
			channel=f.readline()
			f.close()
			channelref=channelref.rstrip("\n")
			fullchannelref=channelref
			channel=channel.rstrip("\n")
			if channelref.startswith("1:0:"):
				if len(channelref) < 25:
					fullchannelref=channelref+"0:0:0:"
     				channel = ServiceReference(fullchannelref).getServiceName()
				if len(channel) < 1:
					channelname1=fullchannelref
				else:
					channelname1=channel
			if len(fullchannelref) > 20:
				streamservicefile="/tmp/stream.%s" % fullchannelref.replace("/","_")
				recordservicefile="/tmp/record.%s" % fullchannelref.replace("/","_")
				if os.path.exists(streamservicefile):
					streaming1=True
				if os.path.exists(recordservicefile):
					recording1=True


		if command is None or command[0] == "return" or command[0] == return_string:
			html  = "<html>\n"
			html += "<head>\n"
			html += "<link rel= \"stylesheet\" href=\"/web-data/css/auto_pin.css\">\n"
			html += "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n"
			html += "<title>%s</title>\n"	% autopin_webif_title
			html += "<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n"
			html += "<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n"
			
			html += "<meta http-equiv=\"Cache-Control\" content=\"no-cache, no-store, must-revalidate\" />\n"
			html += "<meta http-equiv=\"Pragma\" content=\"no-cache\" />\n"
			html += "<meta http-equiv=\"Expires\" content=\"0\" />\n"
			html += "<meta charset=\"UTF-8\">\n" 
			
			html += "<script type=\"text/javascript\">\n"
			
			html += "var help\n"
			
			html += "var messages= [\"2\",\"44\",\"74\",\"101\",\"103\",\"164\",\"204\",\"304\",\"349\",\"502\",\"503\",\"510\",\"535\",\"536\",\"990\",\"991\",\"992\",\"993\"]\n"
			
			html += "var denied1= [\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\"]\n"
			
			html += "var denied2= [\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\",\"false\"]\n"
			
			slot=0
			for i in range(choice_len):
				len2 = len(config.ci[slot].confirm.value)
				for msg in range(len2):
					if int(choice_message[i])==config.ci[slot].confirm.value[msg]:
						html += "denied1[%d]=\"true\"\n"	%i
			slot=1
			for i in range(choice_len):
				len2 = len(config.ci[slot].confirm.value)
				for msg in range(len2):
					if int(choice_message[i])==config.ci[slot].confirm.value[msg]:
						html += "denied2[%d]=\"true\"\n"	%i
			
			html += "function autopin_refresh(){\n"
			html += "if(document.getElementById(\"ar\").checked){\n"
			html += "var date = new Date()\n"
	#		html += "var Auszeit = new Date(jetzt.getTime() + 2000)\n"
			html += "date.setTime(date.getTime()+2000)\n"
			html += "document.cookie = \"if_refresh=hallo; expires=date.toGMTString();\"   \n"
			html += "location.reload()\n"
			html += "}\n"
			html += "}\n"
			
			html += "function check_auto_refresh(){\n"
			html += "if(document.cookie){\n"
			html += "document.getElementById(\"ar\").checked= true\n"
			html += "} else {\n"
			html += "document.getElementById(\"ar\").checked= false\n"
			html += "}\n"
			html += "}\n"
			
			
			
			html += "function man_refresh(){\n"
			html += "location.reload()\n"
			html += "}\n"
			
			
			html += "function write_save(){\n"
			html += "var pin1 = document.getElementById(\"pin1\").value\n"
			html += "var pin2 = document.getElementById(\"pin2\").value\n"
			html += "var mmi = document.getElementById(\"mmi\").value\n"
			html += "var ci_prioritaet = document.getElementById(\"ci_prioritaet\").value\n"
			html += "var ci_prioritaet_umschalten = document.getElementById(\"ci_prioritaet_umschalten\").value\n"
			
			html += "var message_box_top1 = document.getElementById(\"message_box_top0\").checked\n"
			html += "var message_box_top2 = document.getElementById(\"message_box_top1\").checked\n"
			html += "var message_box_top3 = document.getElementById(\"message_box_top2\").checked\n"
			html += "var message_box_top4 = document.getElementById(\"message_box_top3\").checked\n"
			html += "var message_box_top5 = document.getElementById(\"message_box_top4\").checked\n"
			html += "var message_box_top6 = document.getElementById(\"message_box_top5\").checked\n"
			html += "var message_box_top7 = document.getElementById(\"message_box_top6\").checked\n"
			html += "var message_box_top8 = document.getElementById(\"message_box_top7\").checked\n"
			html += "var message_box_top9 = document.getElementById(\"message_box_top8\").checked\n"
			html += "var message_box_top10 = document.getElementById(\"message_box_top9\").checked\n"
			html += "var message_box_top11 = document.getElementById(\"message_box_top10\").checked\n"
			html += "var message_box_top12 = document.getElementById(\"message_box_top11\").checked\n"
			html += "var message_box_top13 = document.getElementById(\"message_box_top12\").checked\n"
			html += "var message_box_top14 = document.getElementById(\"message_box_top13\").checked\n"
			html += "var message_box_top15 = document.getElementById(\"message_box_top14\").checked\n"
			html += "var message_box_top16 = document.getElementById(\"message_box_top15\").checked\n"
			
			
			html += "var message_box_bottom1 = document.getElementById(\"message_box_bottom0\").checked\n"
			html += "var message_box_bottom2 = document.getElementById(\"message_box_bottom1\").checked\n"
			html += "var message_box_bottom3 = document.getElementById(\"message_box_bottom2\").checked\n"
			html += "var message_box_bottom4 = document.getElementById(\"message_box_bottom3\").checked\n"
			html += "var message_box_bottom5 = document.getElementById(\"message_box_bottom4\").checked\n"
			html += "var message_box_bottom6 = document.getElementById(\"message_box_bottom5\").checked\n"
			html += "var message_box_bottom7 = document.getElementById(\"message_box_bottom6\").checked\n"
			html += "var message_box_bottom8 = document.getElementById(\"message_box_bottom7\").checked\n"
			html += "var message_box_bottom9 = document.getElementById(\"message_box_bottom8\").checked\n"
			html += "var message_box_bottom10 = document.getElementById(\"message_box_bottom9\").checked\n"
			html += "var message_box_bottom11 = document.getElementById(\"message_box_bottom10\").checked\n"
			html += "var message_box_bottom12 = document.getElementById(\"message_box_bottom11\").checked\n"
			html += "var message_box_bottom13 = document.getElementById(\"message_box_bottom12\").checked\n"
			html += "var message_box_bottom14 = document.getElementById(\"message_box_bottom13\").checked\n"
			html += "var message_box_bottom15 = document.getElementById(\"message_box_bottom14\").checked\n"
			html += "var message_box_bottom16 = document.getElementById(\"message_box_bottom15\").checked\n"
			
			html += "document.getElementById(\"save_href\").href = \"?cmd=save&pin1=\"+pin1+\"&pin2=\"+pin2+\"&mmi=\"+mmi+\"&ci_prioritaet=\"+ci_prioritaet+\"&ci_prioritaet_umschalten=\"+ci_prioritaet_umschalten+\"&message_box_top1=\"+message_box_top1+\"&message_box_top2=\"+message_box_top2+\"&message_box_top3=\"+message_box_top3+\"&message_box_top4=\"+message_box_top4+\"&message_box_top5=\"+message_box_top5+\"&message_box_top6=\"+message_box_top6+\"&message_box_top7=\"+message_box_top7+\"&message_box_top8=\"+message_box_top8+\"&message_box_top9=\"+message_box_top9+\"&message_box_top10=\"+message_box_top10+\"&message_box_top11=\"+message_box_top11+\"&message_box_top12=\"+message_box_top12+\"&message_box_top13=\"+message_box_top13+\"&message_box_top14=\"+message_box_top14+\"&message_box_top15=\"+message_box_top15+\"&message_box_top16=\"+message_box_top16+\"&message_box_bottom1=\"+message_box_bottom1+\"&message_box_bottom2=\"+message_box_bottom2+\"&message_box_bottom3=\"+message_box_bottom3+\"&message_box_bottom4=\"+message_box_bottom4+\"&message_box_bottom5=\"+message_box_bottom5+\"&message_box_bottom6=\"+message_box_bottom6+\"&message_box_bottom7=\"+message_box_bottom7+\"&message_box_bottom8=\"+message_box_bottom8+\"&message_box_bottom9=\"+message_box_bottom9+\"&message_box_bottom10=\"+message_box_bottom10+\"&message_box_bottom11=\"+message_box_bottom11+\"&message_box_bottom12=\"+message_box_bottom12+\"&message_box_bottom13=\"+message_box_bottom13+\"&message_box_bottom14=\"+message_box_bottom14+\"&message_box_bottom15=\"+message_box_bottom15+\"&message_box_bottom16=\"+message_box_bottom16+\"\"\n"
			html += "document.getElementById(\"save_label_href\").href = \"?cmd=save&pin1=\"+pin1+\"&pin2=\"+pin2+\"&mmi=\"+mmi+\"&ci_prioritaet=\"+ci_prioritaet+\"&ci_prioritaet_umschalten=\"+ci_prioritaet_umschalten+\"&message_box_top1=\"+message_box_top1+\"&message_box_top2=\"+message_box_top2+\"&message_box_top3=\"+message_box_top3+\"&message_box_top4=\"+message_box_top4+\"&message_box_top5=\"+message_box_top5+\"&message_box_top6=\"+message_box_top6+\"&message_box_top7=\"+message_box_top7+\"&message_box_top8=\"+message_box_top8+\"&message_box_top9=\"+message_box_top9+\"&message_box_top10=\"+message_box_top10+\"&message_box_top11=\"+message_box_top11+\"&message_box_top12=\"+message_box_top12+\"&message_box_top13=\"+message_box_top13+\"&message_box_top14=\"+message_box_top14+\"&message_box_top15=\"+message_box_top15+\"&message_box_top16=\"+message_box_top16+\"&message_box_bottom1=\"+message_box_bottom1+\"&message_box_bottom2=\"+message_box_bottom2+\"&message_box_bottom3=\"+message_box_bottom3+\"&message_box_bottom4=\"+message_box_bottom4+\"&message_box_bottom5=\"+message_box_bottom5+\"&message_box_bottom6=\"+message_box_bottom6+\"&message_box_bottom7=\"+message_box_bottom7+\"&message_box_bottom8=\"+message_box_bottom8+\"&message_box_bottom9=\"+message_box_bottom9+\"&message_box_bottom10=\"+message_box_bottom10+\"&message_box_bottom11=\"+message_box_bottom11+\"&message_box_bottom12=\"+message_box_bottom12+\"&message_box_bottom13=\"+message_box_bottom13+\"&message_box_bottom14=\"+message_box_bottom14+\"&message_box_bottom15=\"+message_box_bottom15+\"&message_box_bottom16=\"+message_box_bottom16+\"\"\n"
			html += "}\n"

			
			
			html += "function write_message(){\n"
			html += "var temp=\"\"\n"
			html += "var x=0\n"
			html += "for(var i=0;i<16;i++){\n"
			html += "temp +=\"<label id='message_top\"+i+\"' style='position: absolute; top: 0px; left: \"+x+\"' for='message_box_top\"+i+\"'>\"+messages[i]+\"</label>\"\n"
			html += "if(denied1[i]==\"true\"){\n"
			html += "temp +=\"<input type='checkbox' id='message_box_top\"+i+\"' style='position: absolute; top: 50px; left: \"+x+\"' checked>\"\n"
			html += "} else {\n"
			html += "temp +=\"<input type='checkbox' id='message_box_top\"+i+\"' style='position: absolute; top: 50px; left: \"+x+\"'>\"\n"
			html += "}\n"
			html += "x +=60\n"
			html += "}\n"
			html += "document.getElementById(\"message_1\").innerHTML = temp\n"
			
			html += "temp =\"\"\n"
			html += "var x=0\n"
			html += "var temp=\"\"\n"
			html += "for(var i=0;i<16;i++){\n"
			html += "temp +=\"<label id='message_bottom\"+i+\"' style='position: absolute; top: 0px; left: \"+x+\"' for='message_box_bottom\"+i+\"'>\"+messages[i]+\"</label>\"\n"
			html += "if(denied2[i]==\"true\"){\n"
			html += "temp +=\"<input type='checkbox' id='message_box_bottom\"+i+\"' style='position: absolute; top: 50px; left: \"+x+\"' checked>\"\n"
			html += "} else {\n"
			html += "temp +=\"<input type='checkbox' id='message_box_bottom\"+i+\"' style='position: absolute; top: 50px; left: \"+x+\"'>\"\n"
			html += "}\n"
			html += "x +=60\n"
			html += "}\n"
			html += "document.getElementById(\"message_2\").innerHTML =temp\n"
			html += "}\n"
			
			html += "setInterval(autopin_refresh,5000)\n"
			html += "setInterval(write_save,1000)\n"
			html += "</script>\n"
			
			html += "</head>\n"
			
			if not config.ci[0].mmi.value and not config.ci[1].mmi.value:
				html += "<body bgcolor=\"black\" link=\"#FFFFFF\" vlink=\"#FFFFFF\" alink=\"#FFFFFF\" onload=\"check_auto_refresh(), write_message()\">\n"
			else:
				html += "<body bgcolor=\"black\" link=\"#FFFFFF\" vlink=\"#FFFFFF\" alink=\"#FFFFFF\" onload=\"check_auto_refresh()\">\n"
				
			html += "<font face=\"Tahoma, Arial, Helvetica\" color=\"white\" size=\"6\">\n"
			html += "<hr>\n"
			html += "%s</br>\n" % (self.escape_html(autopin_webif_title+" "+coded_string))
			html += "<hr>\n"
			html += "<a href=\"#\" onclick=\"man_refresh()\"><img src=\"/web-data/img/pin.png\" alt=\"Auto Pin ...\"/></a>\n"
			
			html += "<form name=\"refresh_box\" action=\"\" method=\"GET\">\n"
			html += "<label id=\"refresh_label\" for=\"ar\">Auto Refresh</label>\n"
			html += "<input type=\"checkbox\" id=\"ar\" name=\"auto_refresh_yn\">\n"
			html += "</form>\n"
			
			
			html += "<div id=\"top\">\n"
			html += "<a href=\"?cmd=about\"><img src=\"/web-data/img/red.png\" id=\"about\" width=\"300\" height=\"50\" name=\"red_button\"></a>\n"
			html += "<a href=\"?cmd=about\"><label id=\"about_label\" for=\"about\">%s</label></a>\n" % about_string
			
			html += "<a href=\"?cmd=save\" id=\"save_href\"><img src=\"/web-data/img/green.png\" id=\"save\" width=\"300\" height=\"50\" name=\"green_button\"></a>\n"
			html += "<a href=\"?cmd=save\" id=\"save_label_href\"><label id=\"save_label\" for=\"save\">%s</label></a>\n" % save_string
			
			html += "<a href=\"?cmd=ci\"><img src=\"/web-data/img/yellow.png\" id=\"ci\" width=\"300\" height=\"50\" name=\"yellow_button\"></a>\n"
			html += "<a href=\"?cmd=ci\"><label id=\"ci_label\" for=\"ci\">%s</label></a>\n"  % self.escape_html(ci_string)
			html += "<a href=\"?cmd=assign\"><img src=\"/web-data/img/blue.png\" id=\"assign\" width=\"300\" height=\"50\" name=\"blue_button\"></a>\n"
			html += "<a href=\"?cmd=assign\"><label id=\"assign_label\" for=\"assign\">%s</label></a>\n"  % self.escape_html(assign_string)
			html += "</div>\n"
			
			
			html += "<div id=\"info\">\n"
			
			html += "%s %s<br>\n"	%(slot1_string, module_name[0])
			html += "%s<br>\n" % pin_string
			html += "%s<br>\n"	% message_string
			html += "%s %s<br>\n"	%(slot2_string, module_name[1])
			html += "%s<br>\n"	% pin_string
			html += "%s<br>\n"	% message_string
			html += "<br>\n"
			html += "%s<br>\n"	% mmi_string
			html += "%s<br>\n" % priority_string
			html += "%s<br>\n" % priority_zap_string
			
			html += "</div>\n"
			
			html += "<div id=\"info2\">\n"
			
			html += "<form method=\"GET\">\n"
			html += "<input type=\"number\" id=\"pin1\" value=\"%s\" style=\"width: 55px;\" min=\"1\" max=\"9999\">\n"	% config.ci[0].pin.value
			
			
			html += "<div id=\"message_1\">\n"
#			html += "<form method=\"GET\">\n"
			
			
#			html += "</form>\n"
			html += "</div>\n"
			
			html += "<input type=\"number\" id=\"pin2\" value=\"%s\" style=\"width: 55px;\" min=\"1\" max=\"9999\">\n"	% config.ci[1].pin.value
			
			html += "<div id=\"message_2\">\n"
#			html += "<form method=\"GET\">\n"
			
			
#			html += "</form>\n"
			html += "</div>\n"
			
			html += "<select id=\"mmi\" size=\"1\">\n"
			if not config.ci[0].mmi.value and not config.ci[1].mmi.value:
				html += "<option value=\"active\" selected>%s</option>\n"		% active_string
			else:
				html += "<option value=\"active\">%s</option>\n"		% active_string
			if not config.ci[0].mmi.value and not config.ci[1].mmi.value:
				html += "<option value=\"inactive\" selected>%s</option>\n"		% inactive_string
			else:
				html += "<option value=\"inactive\">%s</option>\n"		% inactive_string
			html += "</select>\n"
			html += "<br>\n"
			
			html += "<select id=\"ci_prioritaet\" size=\"1\">\n"
			if config.plugins.autopin.priority.value == "none":
				html += "<option value=\"none\" selected>%s</option>\n"	% none_string
			else:
				html += "<option value=\"none\">%s</option>\n"	% none_string
			if config.plugins.autopin.priority.value == "recording":
				html += "<option value=\"recording\" selected>%s</option>\n"		% recording_string
			else:
				html += "<option value=\"recording\">%s</option>\n"		% recording_string
			if config.plugins.autopin.priority.value == "streaming":
				html += "<option value=\"streaming\" selected>%s</option>\n"		% streaming_string
			else:
				html += "<option value=\"streaming\">%s</option>\n"		% streaming_string
			if config.plugins.autopin.priority.value == "both":
				html += "<option value=\"both\" selected>%s</option>\n"		% both_string
			else:
				html += "<option value=\"both\">%s</option>\n"		%  both_string
			html += "</select>\n"
			
			html += "<br>\n"
			
			html += "<select id=\"ci_prioritaet_umschalten\" size=\"1\">\n"
			if  config.plugins.autopin.zapto.value == "active":
				html += "<option value=\"active\" selected>%s</option>\n"	% yes_string
			else:
				html += "<option value=\"active\">%s</option>\n"	% yes_string
			if config.plugins.autopin.zapto.value == "inactive":
				html += "<option selected value=\"inactive\">%s</option>\n"		%	no_string
			else:
				html += "<option value=\"inactive\">%s</option>\n"		%	no_string
			if config.plugins.autopin.zapto.value == "auto":
				html += "<option value=\"auto\" selected>%s</option>\n"		%	auto_string
			else:
				html += "<option value=\"auto\">%s</option>\n"		%	auto_string
			html += "</select>\n"
			html += "<br>\n"
			
			html += "</form>\n"
			
			html += "</div>\n"

			html += "<div id=\"images\">\n"
			if os.path.exists("/var/run/ca/%s0.pid" % dreamserv):
				if streaming0:
					html += "<img src=\"/web-data/img/plus_icon_blue.png\" id=\"plus1\" width=\"50\" height=\"50\" name=\"plus1\">\n"
				else:
					if recording0:
						html += "<img src=\"/web-data/img/plus_icon_red.png\" id=\"plus1\" width=\"50\" height=\"50\" name=\"plus1\">\n"
					else:
						html += "<img src=\"/web-data/img/plus_icon_green.png\" id=\"plus1\" width=\"50\" height=\"50\" name=\"plus1\">\n"
			if os.path.exists("/var/run/ca/%s1.pid" % dreamserv):
				if streaming0:
					html += "<img src=\"/web-data/img/plus_icon_blue.png\" id=\"plus2\" width=\"50\" height=\"50\" name=\"plus2\">\n"
				else:
					if recording0:
						html += "<img src=\"/web-data/img/plus_icon_red.png\" id=\"plus2\" width=\"50\" height=\"50\" name=\"plus2\">\n"
					else:
						html += "<img src=\"/web-data/img/plus_icon_green.png\" id=\"plus2\" width=\"50\" height=\"50\" name=\"plus2\">\n"
			html += "<img src=\"/web-data/img/white_outline.png\" id=\"woutline1\" width=\"300\" height=\"50\" name=\"woutline1\">\n"
			html += "<img src=\"/web-data/img/white_outline.png\" id=\"woutline2\" width=\"300\" height=\"50\" name=\"woutline2\">\n"
			if os.path.exists(dreambin):
				html += "<img src=\"/web-data/img/yellow_outline.png\" id=\"youtline1\" width=\"400\" height=\"50\" name=\"youtline1\">\n"
				html += "<img src=\"/web-data/img/yellow_outline.png\" id=\"youtline2\" width=\"400\" height=\"50\" name=\"youtline2\">\n"
			if os.path.exists("/var/run/ca/%s0.pid" % dreamserv):
				html += "<img src=\"/web-data/img/white_bar.png\" id=\"wbar1\" width=\"280\" height=\"30\" name=\"wbar1\">\n"
			if os.path.exists("/var/run/ca/%s1.pid" % dreamserv):
				html += "<img src=\"/web-data/img/white_bar.png\" id=\"wbar2\" width=\"280\" height=\"30\" name=\"wbar2\">\n"
			if os.path.exists(dreambin):
				if enabled0:							
					if running0:							
						html += "<img src=\"/web-data/img/green_box1.png\" id=\"pbox1\" width=\"50\" height=\"50\" name=\"pbox1\">\n"
					else:
						html += "<img src=\"/web-data/img/yellow_box1.png\" id=\"pbox1\" width=\"50\" height=\"50\" name=\"pbox1\">\n"
				else: # 
					if running0:							
						html += "<img src=\"/web-data/img/blue_box1.png\" id=\"pbox1\" width=\"50\" height=\"50\" name=\"pbox1\">\n"
					else:
						html += "<img src=\"/web-data/img/red_box1.png\" id=\"pbox1\" width=\"50\" height=\"50\" name=\"pbox1\">\n"
				if enabled1:							
					if running1:							
						html += "<img src=\"/web-data/img/green_box2.png\" id=\"pbox2\" width=\"50\" height=\"50\" name=\"pbox2\">\n"
					else:
						html += "<img src=\"/web-data/img/yellow_box2.png\" id=\"pbox2\" width=\"50\" height=\"50\" name=\"pbox2\">\n"
				else: # 
					if running1:							
						html += "<img src=\"/web-data/img/blue_box2.png\" id=\"pbox2\" width=\"50\" height=\"50\" name=\"pbox2\">\n"
					else:
						html += "<img src=\"/web-data/img/red_box2.png\" id=\"pbox2\" width=\"50\" height=\"50\" name=\"pbox2\">\n"
				# slot 0
				html += "<a href=\"?cmd=disable&slot=0\" onClick=\"rst_output()\"><img src=\"./web-data/img/ico_mp_rewind.png\" id=\"rst1\" width=\"30\" height=\"30\" name=\"zurueckspultaste1\"></a>\n"
				html += "<a href=\"?cmd=start&slot=0\" onClick=\"play_output()\"><img src=\"./web-data/img/ico_mp_play.png\" id=\"play1\" width=\"30\" height=\"30\" name=\"play1\"></a>\n"
				if os.path.exists("/var/run/ca/%s0.pid" % dreamserv):
					html += "<a href=\"?cmd=start&slot=0\" onClick=\"play_output()\"><img src=\"./web-data/img/ico_mp_pause.png\" id=\"pause1\" width=\"30\" height=\"30\" name=\"pausetaste1\"></a>\n"
				html += "<a href=\"?cmd=stop&slot=0\" onClick=\"stop_output()\"><img src=\"./web-data/img/ico_mp_stop.png\" id=\"stop1\" width=\"30\" height=\"30\" name=\"stop1\"></a>\n"
				html += "<a href=\"?cmd=enable&slot=0\" onClick=\"vst_output()\"><img src=\"./web-data/img/ico_mp_forward.png\" id=\"vst1\" width=\"30\" height=\"30\" name=\"vorspultaste1\" value=\"xxx\"></a>\n"
				html += "<a href=\"?cmd=record&slot=0\" onClick=\"rec_output()\"><img src=\"./web-data/img/record.png\" id=\"rec1\" width=\"30\" height=\"30\" name=\"recordtaste1\"></a>\n"
				# slot 1
				html += "<a href=\"?cmd=disable&slot=1\" onClick=\"rst_output()\"><img src=\"./web-data/img/ico_mp_rewind.png\" id=\"rst2\" width=\"30\" height=\"30\" name=\"zurueckspultaste2\"></a>\n"
				html += "<a href=\"?cmd=start&slot=1\" onClick=\"play_output()\"><img src=\"./web-data/img/ico_mp_play.png\" id=\"play2\" width=\"30\" height=\"30\" name=\"play2\"></a>\n"
				if os.path.exists("/var/run/ca/%s1.pid" % dreamserv):
					html += "<a href=\"?cmd=start&slot=1\" onClick=\"play_output()\"><img src=\"./web-data/img/ico_mp_pause.png\" id=\"pause2\" width=\"30\" height=\"30\" name=\"pausetaste2\"></a>\n"
				html += "<a href=\"?cmd=stop&slot=1\" onClick=\"stop_output()\"><img src=\"./web-data/img/ico_mp_stop.png\" id=\"stop2\" width=\"30\" height=\"30\" name=\"stop2\"></a>\n"
				html += "<a href=\"?cmd=enable&slot=1\" onClick=\"vst_output()\"><img src=\"./web-data/img/ico_mp_forward.png\" id=\"vst2\" width=\"30\" height=\"30\" name=\"vorspultaste2\"></a>\n"
				html += "<a href=\"?cmd=record&slot=1\" onClick=\"rec_output()\"><img src=\"./web-data/img/record.png\" id=\"rec2\" width=\"30\" height=\"30\" name=\"recordtaste2\"></a>\n"

				html += "<div id=\"co1\">"
				html += "<font color=\"yellow\" size=\"6px\">%s</font>\n" % self.escape_html(channelname0)
				html += "</div>"
				html += "<div id=\"co2\">\n"
				html += "<font color=\"yellow\" size=\"6px\">%s</font>\n" % self.escape_html(channelname1)
				html += "</div>\n"
			else:
				html += "<img src=\"/web-data/img/black_box1.png\" id=\"pbox1\" width=\"50\" height=\"50\" name=\"pbox1\">\n"
				html += "<img src=\"/web-data/img/black_box1.png\" id=\"pbox2\" width=\"50\" height=\"50\" name=\"pbox2\">\n"
				html += "</div>\n"
			html += "<hr>\n"
			html += "</font>\n"
			html += "</body>\n"
			html += "</html>\n"
			
		elif command[0] == "save":
#		    pin1 = int(req.args.get("pin1","0")[0].rstrip().replace(" ","").replace("|","").replace(">\n","").replace("<",""))
			
			pin=[0,0]
			pin1=req.args.get("pin1",None)
			if pin1 is None:
				pin[0] = config.ci[0].pin.value
			else:
				pin[0] = int(pin1[0])
				
			pin2=req.args.get("pin2",None)	
			if pin2 is None:
				pin[1] = config.ci[0].pin.value
			else:
				pin[1] = int(pin2[0]) 

			mmi=req.args.get("mmi",None)

			ci_prioritaet=req.args.get("ci_prioritaet",None)
			
			ci_prioritaet_umschalten=req.args.get("ci_prioritaet_umschalten",None)
			
			slot1_Descramble=req.args.get("descramble1",None)
			slot1_bitrate=req.args.get("bitrate1",None)
			
			slot2_Descramble=req.args.get("descramble2",None)
			slot2_bitrate=req.args.get("bitrate2",None)
			
			slot=0
			if slot1_Descramble is not None:
				if slot1_Descramble[0] == "true":
					config.ci[slot].canDescrambleMultipleServices.value = true
				else:
					config.ci[slot].canDescrambleMultipleServices.value = false
				config.ci[slot].canDescrambleMultipleServices.save
			
			slot=1
			if slot2_Descramble is not None:
				if slot2_Descramble[0] == "true":
					config.ci[slot].canDescrambleMultipleServices.value = true
				else:
					config.ci[slot].canDescrambleMultipleServices.value = false
				config.ci[slot].canDescrambleMultipleServices.save
					
			slot=0
			if slot1_bitrate is not None:
				if slot1_bitrate[0] == "true":
					config.ci[slot].canHandleHighBitrates.value = true
				else:
					config.ci[slot].canHandleHighBitrates.value = false
				config.ci[slot].canHandleHighBitrates.save
#			
			slot=1
			if slot2_bitrate is not None:
				if slot2_bitrate[0] == "true":
					config.ci[slot].canHandleHighBitrates.value = true
				else:
					config.ci[slot].canHandleHighBitrates.value = false
				config.ci[slot].canHandleHighBitrates.save
			
			
			slot=0
			top = []
			for i in range(choice_len):
				ticked = req.args.get("message_box_top%d" %(i+1))	
				if ticked is not None:
					if ticked[0]== "true":
						top.append(int(choice_message[i]))
			config.ci[slot].confirm.value = top
			config.ci[slot].confirm.save()
			slot=1
			bottom = []
			for i in range(choice_len):
				ticked = req.args.get("message_box_bottom%d" %(i+1))
				if ticked is not None:
					if ticked[0]== "true":
						bottom.append(int(choice_message[i]))
			config.ci[slot].confirm.value = bottom
			config.ci[slot].confirm.save()
			
			config.plugins.autopin.priority.value=ci_prioritaet
			config.plugins.autopin.priority.save()
			
			config.plugins.autopin.zapto.value=ci_prioritaet_umschalten
			config.plugins.autopin.zapto.save()
	 
			for slot in range(MAX_NUM_CI): 			
				config.ci[slot].pin.value=pin[slot]
				config.ci[slot].pin.save()
#				if config.ci[slot].start.value is True:
#					config.ci[slot].canDescrambleMultipleServices.value="no"
#				if SystemInfo["CommonInterfaceSupportsHighBitrates"]:
#					if config.ci[slot].start.value is True:
#						config.ci[slot].canHandleHighBitrates.value="no"
			if config.plugins.autopin.priority.value == "recording" or config.plugins.autopin.priority.value == "both":
				config.recording.asktozap.value=True
			else:
				config.recording.asktozap.value=False
			if config.plugins.autopin.priority.value == "streaming" or config.plugins.autopin.priority.value == "both":
				config.streaming.asktozap.value=True
			else:
				config.streaming.asktozap.value=False
			config.recording.asktozap.save()
			config.streaming.asktozap.save()
			config.ci.save()

			#for x in self["config"].list:
			#	x[1].save()

			# make sure it is in settings file
			configfile.save()

		
			html  = "<html>\n<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n<head>\n<title>%s</title>\n<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n</head>\n<body bgcolor=\"black\">\n" % autopin_webif_title
			html += "<font face=\"Tahoma, Arial, Helvetica\" font size=\"6\" color=\"white\">\n"
			html += "<hr>\n"
			html += "%s" % (save_string+" "+done_string)
			html += "<hr>\n"
			html += "<br><form method=\"GET\">"                                  
			html += "<input name=\"cmd\" type=\"submit\" size=\"100px\" title=\"%s\" value=\"%s\">" % (return_string,return_string)      
			html += "</form>"
			html += "</font>\n"
			html += "</body>\n"
			html += "</html>\n"
			
		elif command[0] == "ci":
			html  = "<html>\n<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n"
			html += "<head>\n<title>%s</title>\n"	% autopin_webif_title
			html += "<link rel= \"stylesheet\" href=\"/web-data/css/auto_pin.css\">\n"
			html += "<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n"
			html += "<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n"
			html += "<meta charset=\"UTF-8\">\n" 
			
			html += "<script type=\"text/javascript\">\n"
			
			html += "function write_save(){\n"
			html += "var slot1_Descramble = document.getElementById(\"slot1_Descramble\").value\n"
			html += "var slot2_Descramble = document.getElementById(\"slot2_Descramble\").value\n"
			html += "var slot1_bitrate = document.getElementById(\"slot1_bitrate\").value\n"
			html += "var slot2_bitrate = document.getElementById(\"slot2_bitrate\").value\n"
			html += "document.getElementById(\"save_ci_href\").href = \"?cmd=save&descramble1\"+slot1_Descramble+\"&descramble2\"+slot2_Descramble+\"&bitrate1\"+slot1_bitrate+\"&bitrate2\"+slot2_bitrate+\"\n"
			html += "document.getElementById(\"save_label_ci_href\").href = \"?cmd=save&descramble1\"+slot1_Descramble+\"&descramble2\"+slot2_Descramble+\"&bitrate1\"+slot1_bitrate+\"&bitrate2\"+slot2_bitrate+\"\"\n"
			html += "}\n"
			
			html += "var help\n"
			
			html += "setInterval(write_save,1000)\n"
			
			html += "</script>\n"
			
			
			html += "</head>\n"
			html += "<body bgcolor=\"black\" link=\"#FFFFFF\" vlink=\"#FFFFFF\" alink=\"#FFFFFF\">\n" 
			html += "<font face=\"Tahoma, Arial, Helvetica\" font size=\"6\" color=\"white\">\n"
			html += "<hr>\n"
			html += "%s" % (ci_string_full)
			html += "<hr>\n"
			
			html += "<div id=\"ci_info\">\n"
			html += "%s<br>\n"	% slot1_string
			html += "<hr>\n"
			html += "<a href=\"?cmd=reset&slot=0\">%s</a><br>\n"	% reset_ci_string
			html += "<a href=\"?cmd=init&slot=0\">%s</a><br>\n"	% init_ci_string
			html += "%s<br>\n"	% module_name[0]
			html += "%s<br>\n"	% multiple_string
			if boxtype != "dm520" and boxtype != "dm900":
				html += "%s<br>\n"	% high_bitrate_string
			else:
				html += "<br>\n"
			html += "<hr>\n"
			html += "%s<br>\n" % slot2_string
			html += "<hr>\n"
			html += "<a href=\"?cmd=reset&slot=1\">%s</a><br>\n"	% reset_ci_string
			html += "<a href=\"?cmd=init&slot=1\">%s</a><br>\n"	% init_ci_string
			html += "%s<br>\n"	% module_name[1]
			html += "%s<br>\n"	% multiple_string
			if boxtype != "dm520" and boxtype != "dm900":
				html += "%s<br>\n"	% high_bitrate_string
			else:
				html += "<br>\n"
			html += "</div>\n"
			
			html += "<div id=\"ci_info2\">\n"
			
			html += "<form method=\"GET\">\n"
			
			html += "<select id=\"slot1_Descramble\" size=\"1\">\n"
			if  config.ci[0].canDescrambleMultipleServices.value == "yes":
				html += "<option selected>%s</option>\n"	% yes_string
			else:
				html += "<option>%s</option>\n"	% yes_string
			if config.ci[0].canDescrambleMultipleServices.value == "no":
				html += "<option selected>%s</option>\n"		%	no_string
			else:
				html += "<option>%s</option>\n"		%	no_string
			html += "</select>\n"
				
			html += "<br>\n"
			
			if boxtype != "dm520" and boxtype != "dm900":
				html += "<select id=\"slot1_bitrate\" size=\"1\">\n"
				if  config.ci[0].canHandleHighBitrates.value == "yes":
					html += "<option selected>%s</option>\n"	% yes_string
				else:
					html += "<option>%s</option>\n"	% yes_string
				if config.ci[0].canHandleHighBitrates.value == "no":
					html += "<option selected>%s</option>\n"		%	no_string
				else:
					html += "<option>%s</option>\n"		%	no_string
				html += "</select>\n"
			
			
			html += "<select id=\"slot2_Descramble\" size=\"1\">\n"
			if  config.ci[1].canDescrambleMultipleServices.value == "yes":
				html += "<option selected>%s</option>\n"	% yes_string
			else:
				html += "<option>%s</option>\n"	% yes_string
			if config.ci[1].canDescrambleMultipleServices.value == "no":
				html += "<option selected>%s</option>\n"		%	no_string
			else:
				html += "<option>%s</option>\n"		%	no_string
			html += "</select>\n"
			
			html += "<br>\n"
			
			if boxtype != "dm520" and boxtype != "dm900":
				html += "<select id=\"slot2_bitrate\" size=\"1\">\n"
				if  config.ci[1].canHandleHighBitrates.value == "yes":
					html += "<option selected>%s</option>\n"	% yes_string
				else:
					html += "<option>%s</option>\n"	% yes_string
				if config.ci[1].canHandleHighBitrates.value == "no":
					html += "<option selected>%s</option>\n"		%	no_string
				else:
					html += "<option>%s</option>\n"		%	no_string
				html += "</select>\n"
				
			html += "</form>\n"
			html += "</div>\n"
			
			html += "<hr>\n"
			html += "<a href=\"?cmd=%s\"><img src=\"/web-data/img/red.png\" id=\"return_ci\" width=\"300\" height=\"50\" name=\"red_button\"></a>\n" % return_string
			html += "<a href=\"?cmd=%s\"><label id=\"return_label_ci\" for=\"return_ci\">%s</label></a>\n" % (return_string, return_string)
			html += "<a href=\"?cmd=save\" id=\"save_ci_href\" ><img src=\"/web-data/img/green.png\" id=\"save_ci\" width=\"300\" height=\"50\" name=\"green_button\"></a>\n"
			html += "<a href=\"?cmd=save\" id=\"save_label_ci_href\" ><label id=\"save_label_ci\" for=\"save\">%s</label></a>\n" % save_string
			html += "</font>\n"
			html += "</body>\n</html>\n"
		
		elif command[0] == "reset":
			slot = int(req.args.get("slot"," ")[0].rstrip().replace(" ","").replace("|","").replace(">\n","").replace("<",""))
			ci_e2_fifo=False
			if os.path.exists("/dev/ci%d" % slot):
				if stat.S_ISFIFO(os.stat("/dev/ci%d" % slot).st_mode):
					ci_e2_fifo=True
			html  = "<html>\n<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n<head>\n<title>%s</title>\n<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n</head>\n<body bgcolor=\"black\">\n" % autopin_webif_title
			html += "<font face=\"Tahoma, Arial, Helvetica\" font size=\"3 \" color=\"white\">\n"
			html += "<hr>\n"
			text= slot_string	% (slot+1)
			html += "%s %s" % (reset_ci_string,text)
			if not config.ci[slot].mmi.value and not ci_e2_fifo:
				if os.path.exists("/var/lib/dpkg/status"):   
					self.realinstance = eSocket_UI.getInstance()
				else:                                             
					self.realinstance = socketmmi   
				mmi_number=getMMISlotNumber(slot)
				if mmi_number is not None:
					cprint("[AUTOPIN] CI MMI reset slot %d" % mmi_number)
					self.realinstance.answerEnq(mmi_number,"CA_RESET")
			else:
				if os.path.exists(dreamso) and config.ci[slot].plus.value:
					cprint("[AUTOPIN] CI reset %d" % slot)
					dreamplus.setReset(slot)
				else:
					cmd="%s erase %d" % (dreambin, slot)
					cprint("[AUTOPIN] CI command %s" % cmd)
					self.container.execute(cmd)
				
			html += "<hr>\n"
			html += "<br><form method=\"GET\">"                                  
			html += "<input name=\"cmd\" type=\"submit\" size=\"100px\" title=\"%s\" value=\"%s\">" % (return_string,return_string)      
			html += "</form>"
			html += "</font>\n"
			html += "</body>\n</html>\n"
				
		elif command[0] == "init":
			slot = int(req.args.get("slot"," ")[0].rstrip().replace(" ","").replace("|","").replace(">\n","").replace("<",""))
			ci_e2_fifo=False
			if os.path.exists("/dev/ci%d" % slot):
				if stat.S_ISFIFO(os.stat("/dev/ci%d" % slot).st_mode):
					ci_e2_fifo=True
			html  = "<html>\n<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n<head>\n<title>%s</title>\n<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n</head>\n<body bgcolor=\"black\">\n" % autopin_webif_title
			html += "<font face=\"Tahoma, Arial, Helvetica\" font size=\"3 \" color=\"white\">\n"
			html += "<hr>\n"
			text= slot_string	% (slot+1)
			html += "%s %s" % (init_ci_string,text)
			if not config.ci[slot].mmi.value and not ci_e2_fifo:
				if os.path.exists("/var/lib/dpkg/status"):   
					self.realinstance = eSocket_UI.getInstance()
				else:                                             
					self.realinstance = socketmmi   
				mmi_number=getMMISlotNumber(slot)
				if mmi_number is not None:
					cprint("[AUTOPIN] CI MMI reset slot %d" % mmi_number)
					self.realinstance.answerEnq(mmi_number,"CA_INIT")
			else:
				if os.path.exists(dreamso) and config.ci[slot].plus.value:
					cprint("[AUTOPIN] CI restart %d" % slot)
					dreamplus.restart(slot)
				else:
					cmd="%s restart %d" % (dreambin, slot)
					cprint("[AUTOPIN] CI command %s" % cmd)
					self.container.execute(cmd)
			html += "<hr>\n"
			html += "<br><form method=\"GET\">"                                  
			html += "<input name=\"cmd\" type=\"submit\" size=\"100px\" title=\"%s\" value=\"%s\">" % (return_string,return_string)      
			html += "</form>"
			html += "</font>\n"
			html += "</body>\n</html>\n"
			
			
		elif command[0] == "assign":
			html  = "<html>\n<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n"
			html += "<head>\n"
			html += "<link rel= \"stylesheet\" href=\"/web-data/css/auto_pin.css\">\n"
			html += "<title>%s</title>\n"	% autopin_webif_title
			html += "<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n"
			html += "<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n"
			html += "</head>\n"
			html += "<body bgcolor=\"black\" link=\"#FFFFFF\" vlink=\"#FFFFFF\" alink=\"#FFFFFF\">\n" 
			html += "<font face=\"Tahoma, Arial, Helvetica\" font size=\"6\" color=\"white\">\n"
			html += "<hr>\n"
			html += "%s \n" % (assign_string_full)
			html += "<hr>\n"
			html += "<a href=\"?cmd=configure&slot=0\">%s %s</a><br>\n"	%(slot1_string, module_name[0])
			html += "<a href=\"?cmd=configure&slot=1\">%s %s</a><br>\n"	%(slot2_string, module_name[1])
			
			html += "<a href=\"?cmd=%s\"><img src=\"/web-data/img/red.png\" id=\"return_assign\" width=\"300\" height=\"50\" name=\"red_button\"></a>\n" % return_string
			html += "<a href=\"?cmd=%s\"><label id=\"return_label_assign\" for=\"return_assign\">%s</label></a>\n" % (return_string, return_string)
			
			html += "</font>\n"
			html += "</body>\n</html>\n"
					
		elif command[0] == "configure":
			slot = int(req.args.get("slot"," ")[0].rstrip().replace(" ","").replace("|","").replace(">\n","").replace("<",""))
			self.filename = eEnv.resolve("${sysconfdir}/enigma2/ci") + str(slot) + ".xml"
			
			html  = "<html>\n<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n"
			html += "<head>\n"
			html += "<title>%s</title>\n" % autopin_webif_title
			html += "<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n"
			html += "<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n"
			html += "<link rel= \"stylesheet\" href=\"/web-data/css/auto_pin.css\">\n"
			html += "</head>\n"
			html += "<body bgcolor=\"black\" link=\"#FFFFFF\" vlink=\"#FFFFFF\" alink=\"#FFFFFF\">\n" 
			html += "<font face=\"Tahoma, Arial, Helvetica\" font size=\"6\" color=\"white\">\n"
			html += "<hr>\n"
			text= slot_string	% (slot+1)
			html += "%s %s" % (assign_string,text)
			html += "<hr>\n"
			html += "Provider:<br>\n"
			if os_path.exists(self.filename):
				try:
					tree = ci_parse(self.filename).getroot()
					self.read_services=[]
					self.read_providers=[]
					self.usingcaid=[]
					self.ci_config=[]
					for slot2 in tree.findall("slot"):
						read_slot = getValue(slot2.findall("id"), False).encode("UTF-8")
						cprint("[AUTOPIN] CI: %s" % read_slot)
						self.read_providers=[]
						
						for provider in  slot2.findall("provider"):
							read_provider_name = xml_unescape( provider.get("name").encode("UTF-8") )
							read_provider_dvbname = xml_unescape( provider.get("dvbnamespace").encode("UTF-8") )
							cprint("[AUTOPIN] PROVIDER: %s" % (read_provider_name))
							html +="%s</br>\n"	% self.escape_html(read_provider_name)

				except:
					html +="%s</br>\n"	% xml_error_str

	#			html +="%s</br>\n"	% self.escape_html()
			html +="<hr>\n"
			html += "Services:<br>\n"
			
			if os_path.exists(self.filename):
				try:
					tree = ci_parse(self.filename).getroot()
					self.read_services=[]
					self.read_providers=[]
					self.usingcaid=[]
					self.ci_config=[]
					for slot2 in tree.findall("slot"):
						read_slot = getValue(slot2.findall("id"), False).encode("UTF-8")
				#		cprint("[AUTOPIN] CI: %s" % read_slot)
						self.read_providers=[]
						
						
						for service in  slot2.findall("service"):
							read_service_ref = xml_unescape( service.get("ref").encode("UTF-8") )
							channel = ServiceReference(read_service_ref).getServiceName()
					#		cprint("[AUTOPIN] CHANNEL: %s" % (channel))
							html +="%s</br>\n"	% self.escape_html(channel)

						

				except:
					html +="%s</br>\n"	% xml_error_str

			html += "<hr>\n"
			html += "<a href=\"?cmd=assign\"><img src=\"/web-data/img/red.png\" id=\"return_configure\" width=\"300\" height=\"50\" name=\"red_button\"></a>\n" 
			html += "<a href=\"?cmd=assign\"><label id=\"return_label_configure\" for=\"return_configure\">%s</label></a>\n" % (return_string)
			html += "<a href=\"?cmd=reset_configure&slot=%s\"><img src=\"/web-data/img/yellow.png\" id=\"reset_configure\" width=\"300\" height=\"50\" name=\"yellow_button\"></a>\n" % (slot)
			html += "<a href=\"?cmd=reset_configure&slot=%s\"><label id=\"reset_label_configure\" for=\"reset_configure\">%s</label></a>\n" % (slot, reset_string)
			html += "</font>\n"
			html += "</body>\n</html>\n"

		elif command[0] == "reset_configure":
			slot = int(req.args.get("slot"," ")[0].rstrip().replace(" ","").replace("|","").replace(">\n","").replace("<",""))
			name = module_name[slot]
			html = "<html>\n<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n"
			html += "<head>\n"
			html += "<title>%s</title>\n" % autopin_webif_title
			html += "<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n"
			html += "<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n"
			html += "<link rel= \"stylesheet\" href=\"/web-data/css/auto_pin.css\">\n"
			html += "</head>\n"
			html += "<body bgcolor=\"black\" link=\"#FFFFFF\" vlink=\"#FFFFFF\" alink=\"#FFFFFF\">\n" 
			html += "<font face=\"Tahoma, Arial, Helvetica\" font size=\"6\" color=\"white\">\n"
			html += "<hr>\n"
			
		#		name=cur[0]
	#			slot=int(cur[3])
			assign="/etc/enigma2/ci%s.xml" % slot
			# remove also file with Module name ...
			module_name=name.replace(_("Slot %d") % (slot+1)+" - ","").replace(":","").replace("CI %s " % (slot+1),"")
			assign2="/etc/enigma2/ci%s%s.xml" % (slot,module_name.replace(" ","_"))
			if not os.path.exists(assign) and not os.path.exists(assign2):
				text=_("CI assignment")+" "+_("Slot %d") % (slot+1)+" "+_("not configured")
			else:
				if os.path.exists(assign):
					os.remove(assign)
				if os.path.exists(assign2):
					os.remove(assign2)
				text=_("Reset")+" "+_("CI assignment")+" "+_("Slot %d") % (slot+1)+" "+_("done!")
			html += "%s\n" % text
			html += "<hr>\n"
			html += "<a href=\"?cmd=assign\"><img src=\"/web-data/img/red.png\" id=\"return_configure\" width=\"300\" height=\"50\" name=\"red_button\"></a>\n" 
			html += "<a href=\"?cmd=assign\"><label id=\"return_label_configure\" for=\"return_configure\">%s</label></a>\n" % (return_string)
			html += "</font>\n"
			html += "</body>\n</html>\n"

		elif command[0] == "disable":
			restart=True
			slot = int(req.args.get("slot"," ")[0].rstrip().replace(" ","").replace("|","").replace(">\n","").replace("<",""))
			config.ci[slot].start.value=False
			config.ci[slot].start.save()
			text=_("auto")+" "+_("disable").lower()+" "+_("done!")
			cimsg= (("Slot %d") % (slot+1)) +" - "+module_name[slot]+"<hr>"+text
			cimsg=cimsg+"<hr>"+_("Please Reboot")
			html  = "<html>\n<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n<head>\n<title>%s</title>\n<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n</head>\n<body bgcolor=\"black\">\n" % autopin_webif_title
			html += "<font face=\"Tahoma, Arial, Helvetica\" color=\"white\">\n"
			html += "<font size=\"3 \" color=\"white\">\n"
			html += "<hr>\n"
			html += "%s" % (cimsg)
			html += "<hr>\n"
			html += "<br><form method=\"GET\">\n"                                  
			html += "<input name=\"cmd\" type=\"submit\" size=\"100px\" title=\"%s\" value=\"%s\">\n" % (return_string,return_string)      
			html += "</form>\n"       
			html += "</body>\n</html>\n"
			
		elif command[0] == "enable":
			restart=True
			slot = int(req.args.get("slot"," ")[0].rstrip().replace(" ","").replace("|","").replace(">\n","").replace("<",""))
			config.ci[slot].start.value=True
			config.ci[slot].start.save()
			text=_("auto")+" "+_("enable")+" "+_("done!") 			
			cimsg= (("Slot %d") % (slot+1)) +" - "+module_name[slot]+"<hr>"+text
			cimsg=cimsg+"<hr>"+_("Please Reboot")
			html  = "<html>\n<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n<head>\n<title>%s</title>\n<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n</head>\n<body bgcolor=\"black\">\n" % autopin_webif_title
			html += "<font face=\"Tahoma, Arial, Helvetica\" color=\"white\">\n"
			html += "<font size=\"3 \" color=\"white\">\n"
			html += "<hr>\n"
			html += "%s" % (cimsg)
			html += "<hr>\n"
			html += "<br><form method=\"GET\">"                                  
			html += "<input name=\"cmd\" type=\"submit\" size=\"100px\" title=\"%s\" value=\"%s\">" % (return_string,return_string)      
			html += "</form>"       
			html += "</body>\n</html>\n"
			
		elif command[0] ==  "start":
			slot = int(req.args.get("slot"," ")[0].rstrip().replace(" ","").replace("|","").replace(">\n","").replace("<",""))
			ci_e2_fifo=False
			if os.path.exists("/dev/ci%d" % slot):
				if stat.S_ISFIFO(os.stat("/dev/ci%d" % slot).st_mode):
					ci_e2_fifo=True
			if os.path.exists("/var/run/ca/%s%d.pid" % (dreamserv,slot)):
				# already running, hence do restart
				text=_("Restart").lower()+" "+_("done!") 
				if not ci_e2_locked[slot] or ci_e2_fifo:
					if config.ci[slot].mmi.value or ci_e2_fifo:
						if os.path.exists(dreamso) and config.ci[slot].plus.value:
							cprint("[AUTOPIN] CI restart %d" % slot)
							dreamplus.restart(slot)
						else:
							cmd="%s restart %d" % (dreambin, slot)
							cprint("[AUTOPIN] CI command %s" % cmd)
							self.container.execute(cmd)
					else:
						if os.path.exists("/var/lib/dpkg/status"):   
        		               			self.realinstance = eSocket_UI.getInstance()
                	       			else:                                             
                                    			self.realinstance = socketmmi   
						mmi_number=getMMISlotNumber(slot)
						if mmi_number is not None:
							cprint("[AUTOPIN] CI MMI restart slot %d" % mmi_number)
							self.realinstance.answerEnq(mmi_number,"CA_RESTART")
				else:
					done=False
					restart=True
					text=self.escape_html("enigma2"+" "+_("disabled")+" "+_("Slot %d") %(slot+1)+"\n\n"+_("better")+" "+_("enable")+" "+_("auto")+" "+_("Load")+_(" & ")+" "+_("Reboot"))
			else:
				text=_("enable")
				if not ci_e2_locked[slot] or ci_e2_fifo:
					if os.path.exists(dreamso) and config.ci[slot].plus.value:
						cprint("[AUTOPIN] CI start %d" % slot)
						dreamplus.start(slot)
					else:
						cmd="%s start %d" % (dreambin, slot)
						cprint("[AUTOPIN] CI command %s" % cmd)
						self.container.execute(cmd)
				else:
					done=False
					restart=True
					text=self.escape_html("enigma2"+" "+_("disabled")+" "+_("Slot %d") %(slot+1)+"\n\n"+_("better")+" "+_("enable")+" "+_("auto")+" "+_("Load")+_(" & ")+" "+_("Reboot"))
			cimsg= (("Slot %d") % (slot+1)) +" - "+module_name[slot]+"<hr>"+text
			html  = "<html>\n<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n<head>\n<title>%s</title>\n<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n</head>\n<body bgcolor=\"black\">\n" % autopin_webif_title
			html += "<font face=\"Tahoma, Arial, Helvetica\" color=\"white\">\n"
			html += "<font size=\"3 \" color=\"white\">\n"
			html += "<hr>\n"
			html += "%s" % cimsg
			html += "<hr>\n"
			html += "<br><form method=\"GET\">"                                  
			html += "<input name=\"cmd\" type=\"submit\" size=\"100px\" title=\"%s\" value=\"%s\">" % (return_string,return_string)      
			html += "</form>"       
			html += "</body>\n</html>\n"
			
		elif command[0] == "stop":
			slot = int(req.args.get("slot"," ")[0].rstrip().replace(" ","").replace("|","").replace(">\n","").replace("<",""))
			ci_e2_fifo=False
			if os.path.exists("/dev/ci%d" % slot):
				if stat.S_ISFIFO(os.stat("/dev/ci%d" % slot).st_mode):
					ci_e2_fifo=True
			text=_("disable")+" "+_("done!") 
			if not ci_e2_locked[slot] or ci_e2_fifo:
				if config.ci[slot].mmi.value or ci_e2_fifo:
					if os.path.exists(dreamso) and config.ci[slot].plus.value:
						cprint("[AUTOPIN] CI stop %d" % slot)
						dreamplus.stop(slot)
					else:
						cmd="%s stop %d" % (dreambin, slot)
						cprint("[AUTOPIN] CI command %s" % cmd)
						self.container.execute(cmd)
				else:
					if os.path.exists("/var/lib/dpkg/status"):   
       		                		self.realinstance = eSocket_UI.getInstance()
               		        	else:                                             
                       				self.realinstance = socketmmi   
					mmi_number=getMMISlotNumber(slot)
					if mmi_number is not None:
						cprint("[AUTOPIN] CI MMI stop slot %d" % mmi_number)
						self.realinstance.answerEnq(mmi_number,"CA_KILL")
			else:
				done=False
				restart=True
				text="enigma2"+" "+_("disabled")+" "+_("Slot %d") %(slot+1)+"\n\n"+_("better")+" "+_("enable")+" "+_("auto")+" "+_("Load")+_(" & ")
			cimsg= (("Slot %d") % (slot+1)) +" - "+module_name[slot]+"<hr>"+text
			html  = "<html>\n<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n<head>\n<title>%s</title>\n<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n</head>\n<body bgcolor=\"black\">\n" % autopin_webif_title
			html += "<font face=\"Tahoma, Arial, Helvetica\" color=\"white\">\n"
			html += "<font size=\"3 \" color=\"white\">\n"
			html += "<hr>\n"
			html += "%s" % cimsg
			html += "<hr>\n"
			html += "<br><form method=\"GET\">"                                  
			html += "<input name=\"cmd\" type=\"submit\" size=\"100px\" title=\"%s\" value=\"%s\">" % (return_string,return_string)      
			html += "</form>"       
			html += "</body>\n</html>\n"
			
		elif command[0] == "record":
			slot = int(req.args.get("slot"," ")[0].rstrip().replace(" ","").replace("|","").replace(">\n","").replace("<",""))
        		if config.ci[slot].logging.value:                  
        			config.ci[slot].logging.value=False                  
	                	config.ci[slot].logging.save()                    
				# make sure it is in settings file
	  			configfile.save()
				cimsg=_("Log")+" "+_("disabled")+"<hr>"+_("Restart")+" "+_("CI")
			else:
        			config.ci[slot].logging.value=True                 
	                	config.ci[slot].logging.save()                    
				# make sure it is in settings file
				configfile.save()
				cimsg=_("Log")+" "+_("enabled")+"<hr>"+_("Restart")+" "+_("CI")
			html  = "<html>\n<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n<head>\n<title>%s</title>\n<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n</head>\n<body bgcolor=\"black\">\n" % autopin_webif_title
			html += "<font face=\"Tahoma, Arial, Helvetica\" color=\"white\">\n"
			html += "<font size=\"3 \" color=\"white\">\n"
			html += "<hr>\n"
			html += "%s" % cimsg
			html += "<hr>\n"
			html += "<br><form method=\"GET\">"                                  
			html += "<input name=\"cmd\" type=\"submit\" size=\"100px\" title=\"%s\" value=\"%s\">" % (return_string,return_string)      
			html += "</form>"       
			html += "</body>\n</html>\n"
			
		elif command[0] ==  "about":
			html  = "<html>\n<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n<head>\n<title>about %s</title>\n<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n</head>\n<body bgcolor=\"black\">\n" % autopin_webif_title
			html += "<font face=\"Tahoma, Arial, Helvetica\" color=\"white\">\n"
			html += "<font size=\"6 \" color=\"white\">\n"
			html += "<hr>\n"
			html += "%s" % self.escape_html(autopin_webif_title+" "+coded_string)
			html += "<hr>\n"
			html += "%s" % autopin_help
			html += "<hr>\n"
			html += "<br><form method=\"GET\">"                                  
			html += "<input name=\"cmd\" type=\"submit\" size=\"100px\" title=\"%s\" value=\"%s\">" % (return_string,return_string)      
			html += "</form>"       
			html += "</body>\n"
			html += "</html>\n"
		else:
			slot = req.args.get("slot"," ")[0].rstrip().replace(" ","").replace("|","").replace(">\n","").replace("<","")
			html  = "<html>\n<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n		\"http://www.w3.org/TR/html4/loose.dtd\">\n<head>\n<title>%s</title>\n<link rel=\"shortcut icon\" type=\"/web-data/image/x-icon\" href=\"/web-data/img/favicon.ico\">\n<meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">\n</head>\n<body bgcolor=\"red\">\n" % autopin_webif_title
			html += "<font face=\"Tahoma, Arial, Helvetica\" color=\"yellow\">\n"
			html += "<font size=\"3 \" color=\"yellow\">\n"
			html += "<hr>\n"
			html += "%s" % command
			html += "<hr>\n"
			html += "%s" % slot
			html += "<hr>\n"
			html += "</body>\n</html>\n"
		req.setHeader('Content-type', 'text/html')
		return html
		
def getValue(definitions, default):
	ret = ""
	Len = len(definitions)
	return Len > 0 and definitions[Len-1].text or default
	
def sessionstart(reason, **kwargs):                                               
	if reason == 0 and "session" in kwargs:                                                        
	 	cprint("[AUTOPIN] sessionstart")
	        from Plugins.Extensions.WebInterface.WebChilds.Toplevel import addExternalChild
	 	addExternalChild( ("autopin", AutoPinWebif(), "Auto Pin", "1", True) )     

def Plugins(**kwargs):
	return [PluginDescriptor(name=_("Auto Pin"), description=_("Enter pin code")+" & "+_("CI assignment"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="pin.png", fnc=startAutoPin),
		PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc = autostart), PluginDescriptor(name=_("Auto Pin"), description=_("Enter pin code")+" & "+_("CI assignment"), where=PluginDescriptor.WHERE_MENU, fnc=mainconf), PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=sessionstart, needsRestart=False)]

def mainconf(menuid):
	if menuid != "devices":                                                  
		return [ ]                                                     
	return [(_("Auto Pin"), startAutoPin, "autopin", None)]  
