#######################################################################
#
#    Second InfoBar for Enigma-2
#    Vesion 2.7
#    Coded by Vali (c)2010
#    Support: www.dreambox-tools.info
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#######################################################################




from Screens.Screen import Screen
from Screens.InfoBarGenerics import InfoBarPlugins
from Screens.InfoBar import InfoBar
from Screens.MessageBox import MessageBox
from Screens.EpgSelection import EPGSelection
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigText, ConfigSelection
from Components.ConfigList import ConfigListScreen
from Tools.Directories import fileExists, SCOPE_LANGUAGE, SCOPE_PLUGINS, resolveFilename
from Components.Language import language
from os import environ
import gettext
from enigma import eTimer, ePoint, getDesktop

try:
	from Components.Sources.HbbtvApplication import HbbtvApplication
	haveHbbtvApplication = True
except:
	haveHbbtvApplication = False

sz_w = getDesktop(0).size().width()

def localeInit():
	lang = language.getLanguage()
	environ["LANGUAGE"] = lang[:2]
	gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
	gettext.textdomain("enigma2")
	gettext.bindtextdomain("2IB", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/2IB/locale/"))

def _(txt):
	t = gettext.dgettext("2IB", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)


SIBbase__init__ = None
SIB_StartOnlyOneTime = False
VZ_MODE = "-1"


CoolTVGuideAvailable = False
if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/CoolTVGuide/plugin.pyo"):
	from Plugins.Extensions.CoolTVGuide.plugin import main as ctvmain
	CoolTVGuideAvailable = True	

modechoices = [
				("nothing", _("Not enabled")),
				("sib", _("Show Second-InfoBar")),
				("subsrv", _("Show Subservices")),
				("epglist", _("Show standard single EPG"))
			]


if CoolTVGuideAvailable:
	modechoices.append(("cooltv", _("Show CoolTVGuide")))

config.plugins.SecondInfoBar  = ConfigSubsection()
config.plugins.SecondInfoBar.TimeOut = ConfigInteger(default = 10, limits = (0, 60))
config.plugins.SecondInfoBar.Mode = ConfigSelection(default="sib", choices = modechoices)
config.plugins.SecondInfoBar.HideNormalIB = ConfigYesNo(default = False)

def Plugins(**kwargs):
	return [PluginDescriptor(name="SecondInfoBar", description=_("SecondInfoBar 2 Setup"), where=PluginDescriptor.WHERE_MENU, fnc=SIBsetup),
			PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc = SIBautostart)]



def SIBsetup(menuid):
	if menuid != "osd_video_audio":
		return [ ]
	return [(_("Second InfoBar"), openSIBsetup, "sibsetup", None)]
def openSIBsetup(session, **kwargs):
	session.open(SIBsetupScreen)



class SIBsetupScreen(ConfigListScreen, Screen):
	if sz_w == 1920:
		skin = """
	    <screen name="SIBsetupScreen" position="center,170" size="1200,820" title=" ">
        <ePixmap pixmap="Default-FHD/skin_default/buttons/red.svg" position="10,5" size="300,70" />
        <ePixmap pixmap="Default-FHD/skin_default/buttons/green.svg" position="310,5" size="300,70" />
        <eLabel backgroundColor="#9f1313" font="Regular;30" halign="center" position="10,5" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="300,70" text="Cancel" transparent="1" valign="center" zPosition="1" />
        <eLabel backgroundColor="#1f771f" font="Regular;30" halign="center" position="310,5" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="300,70" text="Save" transparent="1" valign="center" zPosition="1" />
        <widget font="Regular;34" halign="right" position="1050,25" render="Label" size="120,40" source="global.CurrentTime">
            <convert type="ClockToText">Default</convert>
        </widget>
        <widget font="Regular;34" halign="right" position="640,25" render="Label" size="400,40" source="global.CurrentTime">
            <convert type="ClockToText">Date</convert>
        </widget>
        <eLabel backgroundColor="grey" position="10,80" size="1180,1" />
        <widget enableWrapAround="1" name="config" position="10,90" scrollbarMode="showOnDemand" size="1180,630" />
        <eLabel backgroundColor="grey" position="10,730" size="1180,1" />
        <eLabel font="Regular;32" halign="center" position="10,740" size="1180,70" text="coded:2010 by Vali" valign="center" />
		</screen>"""
	else:
		skin = """
	    <screen name="SIBsetupScreen" position="center,120" size="820,520" title=" ">
		<ePixmap pixmap="skin_default/buttons/red.png" position="10,5" size="200,40" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="210,5" size="200,40" />
		<eLabel text="Cancel" position="10,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" />
		<eLabel text="Save" position="210,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" />
		<eLabel position="10,50" size="800,1" backgroundColor="grey" />
		<widget name="config" position="10,55" size="800,420" enableWrapAround="1" scrollbarMode="showOnDemand" />
		<eLabel position="10,480" size="800,1" backgroundColor="grey" />
		<eLabel  text="coded: 2010 by Vali" position="10,488" size="800,25" font="Regular;22" halign="center" />
		</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.setTitle(_("Second-InfoBar setup"))
		self.MustRestart = (config.plugins.SecondInfoBar.HideNormalIB.value)
		list = []
		list.append(getConfigListEntry(_("Second-InfoBar working mode"), config.plugins.SecondInfoBar.Mode))
		list.append(getConfigListEntry(_("Second-InfoBar Timeout (in Sec. , 0 = wait for OK)"), config.plugins.SecondInfoBar.TimeOut))
		list.append(getConfigListEntry(_("Hide Infobar if Second-InfoBar shown"), config.plugins.SecondInfoBar.HideNormalIB))
		ConfigListScreen.__init__(self, list)
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], 
									{
									"red": self.exit, 
									"green": self.save,
									"cancel": self.exit
									}, -1)

	def exit(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()

	def save(self):
		for x in self["config"].list:
			x[1].save()
		if (self.MustRestart ^ (config.plugins.SecondInfoBar.HideNormalIB.value)):
			self.session.open(MessageBox, _("GUI needs a restart to apply the new settings !!!"), MessageBox.TYPE_INFO)	
		self.close()



def SIBautostart(reason, **kwargs):
	global SIBbase__init__
	if "session" in kwargs:
		if SIBbase__init__ is None:
			SIBbase__init__ = InfoBarPlugins.__init__
		InfoBarPlugins.__init__ = InfoBarPlugins__init__
		InfoBarPlugins.switch = switch
		InfoBarPlugins.swOff = swOff



def InfoBarPlugins__init__(self):
	global SIB_StartOnlyOneTime
	global VZ_MODE
	if not SIB_StartOnlyOneTime: 
		SIB_StartOnlyOneTime = True
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/VirtualZap/plugin.pyo"):
			try:
				VZ_MODE = config.plugins.virtualzap.mode.value
			except:
				VZ_MODE = "-1"
		else:
			VZ_MODE = "-1"
		if VZ_MODE == "1":
			self["SIBActions"] = ActionMap(["SIBwithVZActions"],{"ok_but": self.switch,"exit_but": self.swOff}, -1)
		else:
			self["SIBActions"] = ActionMap(["SIBActions"],{"ok_but": self.switch,"exit_but": self.swOff}, -1)
		self.SIBtimer = eTimer()
		self.SIBtimer_Connection = self.SIBtimer.timeout.connect(self.swOff)
		self.SIBdialog = self.session.instantiateDialog(SecondInfoBar)
		self.SIBdialog.shown = False
		def CheckSIBtimer():
			if self.SIBtimer.isActive():
				self.SIBtimer.stop()
		self.SIBdialog.onHide.append(CheckSIBtimer)
	else:
		InfoBarPlugins.__init__ = InfoBarPlugins.__init__
		InfoBarPlugins.switch = None
		InfoBarPlugins.swOff = None
	SIBbase__init__(self)



def switch(self):
	if isinstance(self,InfoBar):
		if config.plugins.SecondInfoBar.Mode.value == "sib":
			if not self.shown and not self.SIBdialog.shown:
				self.toggleShow()
			elif self.shown and not self.SIBdialog.shown:
				if config.plugins.SecondInfoBar.HideNormalIB.value:
					self.hide()
				self.SIBdialog.show()
				SIBidx = config.plugins.SecondInfoBar.TimeOut.value
				if (SIBidx > 0):
					self.SIBtimer.start(SIBidx*1000, True)
			elif not self.shown and self.SIBdialog.shown:
				self.SIBdialog.hide()
			elif self.shown and self.SIBdialog.shown:
				self.hide()
				self.SIBdialog.hide()
			else:
				self.toggleShow()	
		elif config.plugins.SecondInfoBar.Mode.value == "epglist":
			if self.shown:
				self.session.open(EPGSelection, self.session.nav.getCurrentlyPlayingServiceReference())
			else:
				self.toggleShow()		
		elif config.plugins.SecondInfoBar.Mode.value == "cooltv":
			if self.shown:
				if CoolTVGuideAvailable:
					ctvmain(self.session)
			else:
				self.toggleShow()		
		elif config.plugins.SecondInfoBar.Mode.value == "subsrv":
			if self.shown:
				service = self.session.nav.getCurrentService()
				subservices = service and service.subServices()
				if subservices.getNumberOfSubservices()>0:
					self.subserviceSelection()
				else:
					self.toggleShow()
			else:
				self.toggleShow()
		else:
			self.toggleShow()



def swOff(self):
	if isinstance(self,InfoBar):
		if not(self.shown or self.SIBdialog.shown) and (VZ_MODE == "2"):
			self.newHide()
		else:
			self.hide()
			self.SIBdialog.hide()



class SecondInfoBar(Screen):
	if sz_w == 1920:
		skin = """
		<screen backgroundColor="transparent" flags="wfNoBorder" name="SecondInfoBar" position="0,0" size="1920,810">
        <eLabel backgroundColor="background" position="10,100" size="940,80" zPosition="-1" />
        <eLabel backgroundColor="background" position="970,100" size="940,80" zPosition="-1" />
        <eLabel backgroundColor="background" position="10,190" size="940,625" zPosition="-1" />
        <eLabel backgroundColor="background" position="970,190" size="940,625" zPosition="-1" />
        <eLabel font="Regular;32" position="30,102" size="150,40" text="NOW" />
        <widget font="Regular;32" halign="right" position="190,103" render="Label" size="100,35" source="session.Event_Now">
            <convert type="EventTime">StartTime</convert>
            <convert type="ClockToText">Default</convert>
        </widget>
        <widget font="Regular;32" halign="left" position="300,103" render="Label" size="110,35" source="session.Event_Now">
            <convert type="EventTime">EndTime</convert>
            <convert type="ClockToText">Format:- %H:%M</convert>
        </widget>
        <widget font="Regular;32" halign="right" position="730,103" render="Label" size="200,35" source="session.Event_Now">
            <convert type="EventTime">Remaining</convert>
            <convert type="RemainingToText">InMinutes</convert>
        </widget>
        <widget font="Regular;32" position="30,140" render="Label" size="910,38" source="session.Event_Now">
            <convert type="EventName">Name</convert>
        </widget>
        <widget font="Regular;30" position="40,200" render="Label" size="900,600" source="session.Event_Now">
            <convert type="EventName">FullDescription</convert>
        </widget>
        <eLabel font="Regular;32" position="990,102" size="160,40" text="NEXT" />
        <widget font="Regular;32" halign="right" position="1160,103" render="Label" size="100,35" source="session.Event_Next">
            <convert type="EventTime">StartTime</convert>
            <convert type="ClockToText">Default</convert>
        </widget>
        <widget font="Regular;32" halign="left" position="1270,103" render="Label" size="110,35" source="session.Event_Next">
            <convert type="EventTime">EndTime</convert>
            <convert type="ClockToText">Format:- %H:%M</convert>
        </widget>
        <widget font="Regular;32" halign="right" position="1720,103" render="Label" size="170,35" source="session.Event_Next">
            <convert type="EventTime">Remaining</convert>
            <convert type="RemainingToText">InMinutes</convert>
        </widget>
        <widget font="Regular;32" position="990,140" render="Label" size="910,38" source="session.Event_Next">
            <convert type="EventName">Name</convert>
        </widget>
        <widget font="Regular;30" position="1000,200" render="Label" size="880,600" source="session.Event_Next">
            <convert type="EventName">FullDescription</convert>
        </widget>
		</screen>"""
	else:
		skin = """
		<screen name="SecondInfoBar" position="center,70" size="1200,455" title="SecondInfoBar" flags="wfNoBorder">	
			<widget source="session.Event_Now" render="Label" position="10,5" size="60,26" font="Regular;22" halign="right" >
				<convert type="EventTime">StartTime</convert>
				<convert type="ClockToText">Default</convert>
			</widget>
			<eLabel text="-" position="70,5" size="15,30" font="Regular;22" halign="center" />
			<widget source="session.Event_Now" render="Label" position="85,5" size="75,26" font="Regular;22" >
				<convert type="EventTime">EndTime</convert>
				<convert type="ClockToText">Default</convert>
			</widget>
			<widget source="session.Event_Now" render="Label" position="170,5" size="420,26" font="Regular;22" >
				<convert type="EventName">Name</convert>
			</widget>		
			<widget source="session.Event_Now" render="Label" position="10,50" size="580,390" font="Regular;20">
				<convert type="EventName">FullDescription</convert>
			</widget>
			<eLabel position="595,0" size="5,455" backgroundColor="transparent" />
            <eLabel position="0,38" size="1200,6" backgroundColor="transparent" />
			<widget source="session.Event_Next" render="Label" position="610,5" size="60,26" font="Regular;22" halign="right" >
				<convert type="EventTime">StartTime</convert>
				<convert type="ClockToText">Default</convert>
			</widget>
			<eLabel text="-" position="670,5" size="15,30" font="Regular;22" halign="center" />
			<widget source="session.Event_Next" render="Label" position="685,5" size="75,26" font="Regular;22" >
				<convert type="EventTime">EndTime</convert>
				<convert type="ClockToText">Default</convert>
			</widget>
			<widget source="session.Event_Next" render="Label" position="760,5" size="415,26" font="Regular;22" >
				<convert type="EventName">Name</convert>
			</widget>
			<widget source="session.Event_Next" render="Label" position="610,50" size="575,390" font="Regular;20">
				<convert type="EventName">FullDescription</convert>
			</widget>	
		</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skin = SecondInfoBar.skin
		self["HbbtvApplication"] = HbbtvApplication()







