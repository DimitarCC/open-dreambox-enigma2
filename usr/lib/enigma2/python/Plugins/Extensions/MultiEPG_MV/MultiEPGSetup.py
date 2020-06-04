#!/usr/bin/python
# -*- coding: utf-8 -*-

# GUI (System)
from enigma import getDesktop

# GUI (Screens)
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.ConfigList import ConfigListScreen
from Screens.MessageBox import MessageBox

# GUI (Summary)
from Screens.Setup import SetupSummary
from Screens.LocationBox import LocationBox

# GUI (Components)
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.Label import Label

# Configuration
from Components.config import * 

from Plugins.Plugin import PluginDescriptor
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS

PluginVersion = "1.1"

sz_w = getDesktop(0).size().width()

class MultiEPGSetup(Screen, ConfigListScreen):
	
	if sz_w == 1920:
		skin = """
		<screen name="MultiEPGSetup" position="center,center" size="1200,790">
			<ePixmap pixmap="skin_default/buttons/red.png" position="10,5" size="295,70" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="305,5" size="295,70" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="600,5" size="295,70" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="895,5" size="295,70" alphatest="on" />
			<widget source="key_red" render="Label" position="10,5" size="295,70" font="Regular;30" halign="center" valign="center" backgroundColor="#9f1313" shadowColor="#000000" shadowOffset="-3,-3" zPosition="1" transparent="1" />
			<widget source="key_green" render="Label" position="310,5" size="300,70" font="Regular;30" halign="center" valign="center" backgroundColor="#1f771f" shadowColor="#000000" shadowOffset="-3,-3" zPosition="1" transparent="1" />
			<widget source="key_yellow" render="Label" position="610,5" size="300,70" font="Regular;30" halign="center" valign="center" backgroundColor="#a08500" shadowColor="#000000" shadowOffset="-3,-3" zPosition="1" transparent="1" />
			<widget source="key_blue" render="Label" position="910,5" size="300,70" font="Regular;30" halign="center" valign="center" backgroundColor="#18188b" shadowColor="#000000" shadowOffset="-3,-3" zPosition="1" transparent="1" />
			<widget name="config" position="10,90" size="1180,550" enableWrapAround="1" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="skin_default/div-h.png" position="10,650" zPosition="2" size="1180,2" />
			<widget name="help" position="10,650" size="1180,120" font="Regular;32" />
		</screen>"""
	else:
		skin = """
		<screen name="MultiEPGSetup" position="center,center" size="800,570">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="200,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="200,0" size="200,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="400,0" size="200,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="600,0" size="200,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowColor="#000000" shadowOffset="-2,-2" zPosition="1" transparent="1" />
			<widget source="key_green" render="Label" position="200,0" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowColor="#000000" shadowOffset="-2,-2" zPosition="1" transparent="1" />
			<widget source="key_yellow" render="Label" position="400,0" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowColor="#000000" shadowOffset="-2,-2" zPosition="1" transparent="1" />
			<widget source="key_blue" render="Label" position="600,0" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowColor="#000000" shadowOffset="-2,-2" zPosition="1" transparent="1" />
			<widget name="config" position="5,50" size="790,400" enableWrapAround="1" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="skin_default/div-h.png" position="0,460" zPosition="2" size="800,2" />
			<widget name="help" position="5,470" size="790,90" font="Regular;22" />
		</screen>"""


	def __init__(self, session):
		Screen.__init__(self, session)

		# Summary
		self.skinName = "MultiEPGSetup"
		self.setup_title = _("MultiEPG Vali Mod ") + _("Setup") + " - Version " + str(PluginVersion)
		self.onChangedEntry = []
		
		self.list = []
		self.buildConfig()
		ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changed)
		
		def selectionChanged():
			if self["config"].current:
				self["config"].current[1].onDeselect(self.session)
			self["config"].current = self["config"].getCurrent()
			if self["config"].current:
				self["config"].current[1].onSelect(self.session)
			for x in self["config"].onSelectionChanged:
				x()
		self["config"].selectionChanged = selectionChanged
		self["config"].onSelectionChanged.append(self.updateHelp)

		# Initialize widgets
		self["key_green"] = StaticText(_("OK"))
		self["key_red"] = StaticText(_("Cancel"))
		self["key_yellow"] = StaticText("")
		self["key_blue"] = StaticText(_("About"))
		self["help"] = Label("")
		
		# Define Actions
		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": 	self.keyCancel,
				"save": 		self.keySave,
				"ok": 			self.ok,
				"blue": 		self.about,
			},-2)

		# Trigger change
		self.changed()

		self.onLayoutFinish.append(self.layoutFinished)

	def buildConfig(self):
		
		
		self.list.append( getConfigListEntry(_("Show Picons"), config.plugins.multiepgmv.showpicons, _("Displays the logo for each service entry.")) )
		#if config.plugins.multiepgmv.showpicons.value:
		#	self.list.append( getConfigListEntry(_("Picons path"), config.plugins.multiepgmv.picon_path, _("Wähle den Pfad der picons aus.")) )

		self.list.append( getConfigListEntry(_("Prime Time"), config.plugins.multiepgmv.prime_time, _("Primetime (default='20:15').")) )

		self.list.append( getConfigListEntry(_("Time range (in Minutes)"), config.plugins.multiepgmv.time_period, _("Enter the time range to be displayed in the MultiEPG (in minutes).")) )

		self.list.append( getConfigListEntry(_("Display the timer"), config.plugins.multiepgmv.timerdisplay, _("Choose the display type for the timer banner = flat line (default = banner).")) )
		if config.plugins.multiepgmv.timerdisplay.value == "True":
			self.list.append( getConfigListEntry(_("   Adjustment of the banner height"), config.plugins.multiepgmv.bannerheightoffset, _("To adjust the height of the banner line for timers(-5 to +5, default = 0).")) )

		self.list.append( getConfigListEntry(_("Check timers when closing the MultiEPG"), config.plugins.multiepgmv.timercheck, _("Checks the existing timer times with the EPG times when closing the MultiEPG and show a message if there is a difference.")) )
		if config.plugins.multiepgmv.timercheck.value:
			self.list.append( getConfigListEntry(_("   Notice for differences of x minutes"), config.plugins.multiepgmv.timerdiff, _("Outputs only a hint from a deviation of x minutes (default=1).")) )
		
		self.list.append( getConfigListEntry(_("Show plugin in PluginBrowser"), config.plugins.multiepgmv.pluginbrowsermenu, _("Wähle, ob das Plugin im PluginBrowser angezeigt werden soll (GUI-Neustart erforderlich).")) )
		
		self.list.append( getConfigListEntry(_("Show plugin in the extension menu"), config.plugins.multiepgmv.extensionsmenu, _("Wähle, ob das Plugin im Erweiterungsmenü (blaue Taste) angezeigt werden soll (GUI-Neustart erforderlich).")) )
		
		if not fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/EasyInfo/plugin.py")):
			self.list.append( getConfigListEntry(_("Start the plugin with the info button"), config.plugins.multiepgmv.openOnInfokey, _("Wähle, ob das Plugin mit der Info-Taste geöffnet werden soll.\nDas EventView-Fenster kann man dann mit einen Doppelklick auf die Info-Taste direkt öffnen.")) )
		
		if hasattr(PluginDescriptor, "WHERE_CHANNEL_SELECTION_RED"):
			self.list.append( getConfigListEntry(_("Use the More ... function for the red button"), config.plugins.multiepgmv.useMoreKey, _("Listet alle Plugin-Befehle für Events im Mehr-Menü der roten Taste auf.")) )
		
		self.list.append( getConfigListEntry(_("Adjust EPG font size"), config.plugins.multiepgmv.fontsizeoffset, _("Zur Anpassung der Schriftgröße im EPG-Raster (-5 bis +10, default = 0).")) )
		self.list.append( getConfigListEntry(_("Adjustment of the EPG line number"), config.plugins.multiepgmv.rowoffset, _("Zur Anpassung der Zeilenanzahl (Sender) im EPG-Raster (-10 bis +10, default = 0).")) )

	def layoutFinished(self):
		self.setTitle(self.setup_title)

	def ok(self):
		#if self["config"].getCurrent()[1] == config:
		#	...
		pass

	def setCustomTitle(self):
		self.setTitle(self.setup_title)

	def updateHelp(self):
		cur = self["config"].getCurrent()
		if cur:
			self["help"].text = cur[2]

	def changeConfig(self):
		self.list = []
		self.buildConfig()
		self["config"].setList(self.list)

	def changed(self):
		for x in self.onChangedEntry:
			x()
		current = self["config"].getCurrent()[1]
		if current in (config.plugins.multiepgmv.showpicons, config.plugins.multiepgmv.timercheck, config.plugins.multiepgmv.timerdisplay):
			self.changeConfig()
			return

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def createSummary(self):
		return SetupSummary

	def about(self):
		self.session.open(MessageBox, _("MultiEPG Vali Mod")+" "+_("Version")+" " + PluginVersion + "\n\n"+_("(c) Vali & Dreamy"),  MessageBox.TYPE_INFO)
		