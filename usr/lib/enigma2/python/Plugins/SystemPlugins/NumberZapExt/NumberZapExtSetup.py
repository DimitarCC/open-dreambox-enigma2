#
# Extended NumberZap Plugin for Enigma2
# Coded by vlamo (c) 2011,2012
#

from . import _
from Screens.Screen import Screen
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigSubsection
from Components.FileList import FileList
from enigma import getDesktop

sz_w = getDesktop(0).size().width()

class DirectoryBrowser(Screen):
    if sz_w == 1920:
        skin = """
            <screen name="DirectoryBrowser" position="center,170" size="1200,820" title="Directory browser" >
            <ePixmap pixmap="Default-FHD/skin_default/buttons/red.svg" position="10,5" size="300,70" />
            <ePixmap pixmap="Default-FHD/skin_default/buttons/green.svg" position="310,5" size="300,70" />
            <widget backgroundColor="#9f1313" font="Regular;30" halign="center" position="10,5" render="Label" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="300,70" source="key_red" transparent="1" valign="center" zPosition="1" />
            <widget backgroundColor="#1f771f" font="Regular;30" halign="center" position="310,5" render="Label" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="300,70" source="key_green" transparent="1" valign="center" zPosition="1" />
            <widget font="Regular;34" halign="right" position="1050,25" render="Label" size="120,40" source="global.CurrentTime">
                <convert type="ClockToText">Default</convert>
            </widget>
            <widget font="Regular;34" halign="right" position="640,25" render="Label" size="400,40" source="global.CurrentTime">
                <convert type="ClockToText">Date</convert>
            </widget>
            <eLabel backgroundColor="grey" position="10,80" size="1180,1" />
            <widget enableWrapAround="1" name="filelist" position="10,90" scrollbarMode="showOnDemand" size="1180,630" />
            <eLabel backgroundColor="grey" position="10,730" size="1180,1" />
            <widget font="Regular;32" halign="center" source="curdir" render="Label" position="10,735" size="1180,75" valign="center" />
        	</screen>"""
    else:
        skin = """
            <screen name="DirectoryBrowser" position="center,120" size="820,520" title="Directory browser" >
            <ePixmap pixmap="skin_default/buttons/red.png" position="10,5" size="200,40" />
	    	<ePixmap pixmap="skin_default/buttons/green.png" position="210,5" size="200,40" />
    		<widget source="key_red" render="Label" position="10,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" />
	    	<widget source="key_green" render="Label" position="210,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" />
	    	<eLabel position="10,50" size="800,1" backgroundColor="grey" />
	    	<widget source="curdir" render="Label" position="10,60" size="800,25" font="Regular;20" noWrap="1" />
	    	<widget name="filelist" position="10,90" size="800,420" enableWrapAround="1" scrollbarMode="showOnDemand" />
        	</screen>"""

    def __init__(self, session, curdir, matchingPattern = None):
        Screen.__init__(self, session)
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Save'))
        self['curdir'] = StaticText('current:  %s' % (curdir or ''))
        self.filelist = FileList(curdir, matchingPattern=matchingPattern, enableWrapAround=True)
        self.filelist.onSelectionChanged.append(self.__selChanged)
        self['filelist'] = self.filelist
        self['FilelistActions'] = ActionMap(['SetupActions', 'ColorActions'],
         {
         'green': self.keyGreen,
         'red': self.keyRed,
         'ok': self.keyOk,
         'cancel': self.keyRed
         })
        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        pass

    def getCurrentSelected(self):
        dirname = self.filelist.getCurrentDirectory()
        filename = self.filelist.getFilename()
        if not filename and not dirname:
            cur = ''
        elif not filename:
            cur = dirname
        elif not dirname:
            cur = filename
        elif not self.filelist.canDescent() or len(filename) <= len(dirname):
            cur = dirname
        else:
            cur = filename
        return cur or ''

    def __selChanged(self):
        self['curdir'].setText('current:  %s' % self.getCurrentSelected())

    def keyOk(self):
        if self.filelist.canDescent():
            self.filelist.descent()

    def keyGreen(self):
        self.close(self.getCurrentSelected())

    def keyRed(self):
        self.close(False)


class NumberZapExtSetupScreen(Screen, ConfigListScreen):

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self.skinName = ['NumberZapExtSetup', 'Setup']
        self.setup_title = _('Extended NumberZap Setup')
        self['key_green'] = StaticText(_('Save'))
        self['key_red'] = StaticText(_('Cancel'))
        self['actions'] = NumberActionMap(['SetupActions'],
         {
         'cancel': self.keyRed,
         'ok': self.keyOk,
         'save': self.keyGreen
         }, -1)
         
        ConfigListScreen.__init__(self, [])
        self.initConfig()
        self.createSetup()
        self.onClose.append(self.__closed)
        self.onLayoutFinish.append(self.__layoutFinished)

    def __closed(self):
        pass

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def initConfig(self):

        def getPrevValues(section):
            res = {}
            for key, val in section.content.items.items():
                if isinstance(val, ConfigSubsection):
                    res[key] = getPrevValues(val)
                else:
                    res[key] = val.value

            return res

        self.NZE = config.plugins.NumberZapExt
        self.prev_values = getPrevValues(self.NZE)
        self.cfg_enable = getConfigListEntry(_('enable extended number zap'), self.NZE.enable)
        self.cfg_kdelay = getConfigListEntry(_('time to wait next keypress (millisecond)'), self.NZE.kdelay)
        self.cfg_acount = getConfigListEntry(_('alternative service counter in bouquets'), self.NZE.acount)
        self.cfg_picons = getConfigListEntry(_('enable picons'), self.NZE.picons)
        self.cfg_picondir = getConfigListEntry(_('picons directory:'), self.NZE.picondir)

    def createSetup(self):
        list = [self.cfg_enable]
        if self.NZE.enable.value:
            list.append(self.cfg_kdelay)
            list.append(self.cfg_acount)
            list.append(self.cfg_picons)
            if self.NZE.picons.value:
                list.append(self.cfg_picondir)
        self['config'].list = list
        self['config'].l.setList(list)

    def newConfig(self):
        cur = self['config'].getCurrent()
        if cur in (self.cfg_enable, self.cfg_picons):
            self.createSetup()
        elif cur == self.cfg_picondir:
            self.keyOk()

    def keyOk(self):
        cur = self['config'].getCurrent()
        if cur == self.cfg_picondir:
            self.session.openWithCallback(self.directoryBrowserClosed, DirectoryBrowser, self.NZE.picondir.value, '^.*\\.png')

    def directoryBrowserClosed(self, path):
        if path != False:
            self.NZE.picondir.setValue(path)

    def keyRed(self):

        def setPrevValues(section, values):
            for key, val in section.content.items.items():
                value = values.get(key, None)
                if value is not None:
                    if isinstance(val, ConfigSubsection):
                        setPrevValues(val, value)
                    else:
                        val.value = value

            return

        setPrevValues(self.NZE, self.prev_values)
        self.keyGreen()

    def keyGreen(self):
        if not self.NZE.enable.value:
            self.NZE.acount.value = False
        self.NZE.save()
        self.close()

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.newConfig()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.newConfig()