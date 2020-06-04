#
# Extended NumberZap Plugin for Enigma2
# Coded by vlamo (c) 2011,2012
#

from . import _
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigInteger, ConfigDirectory
from Screens.Screen import Screen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ActionMap import NumberActionMap
from enigma import eServiceReference, eServiceCenter, eTimer, getDesktop
from Screens.ChannelSelection import ChannelSelectionBase, BouquetSelector
from Tools.BoundFunction import boundFunction
from Tools.Directories import fileExists, pathExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Tools.PiconResolver import PiconResolver

sz_w = getDesktop(0).size().width()

base_keyNumberGlobal = None
base_getBouquetNumOffset = None
base_ChannelSelectionBase__init__ = None
config.plugins.NumberZapExt = ConfigSubsection()
config.plugins.NumberZapExt.enable = ConfigYesNo(default=False)
config.plugins.NumberZapExt.kdelay = ConfigInteger(default=3000, limits=(0, 9999))
config.plugins.NumberZapExt.acount = ConfigYesNo(default=False)
config.plugins.NumberZapExt.hotkey = ConfigYesNo(default=False)
config.plugins.NumberZapExt.picons = ConfigYesNo(default=False)
config.plugins.NumberZapExt.picondir = ConfigDirectory()
config.plugins.NumberZapExt.action = ConfigSubsection()

class NumberZapExt(Screen):
    if sz_w == 1920:
        skin = """
            <screen name="NumberZapExt" position="center,center" size="940,170" title="Extended NumberZap">
            <widget name="chPicon" position="700,20" scale="1" size="220,132" />
            <widget name="number"  position="5,15"   size="160,38" halign="right" font="Regular;35" />
            <widget name="chNum"   position="200,15" size="240,38" font="Regular;35" />
            <widget name="channel" position="5,70"   size="160,38" halign="right" font="Regular;35" />
            <widget name="chName"  position="200,70" size="480,36" font="Regular;33" noWrap="1" />
            <widget name="bouquet" position="5,120"   size="160,38" halign="right" font="Regular;35" />
            <widget name="chBouq"  position="200,120" size="480,36" font="Regular;33" noWrap="1" />
           </screen>"""
    else:
        skin = """
            <screen name="NumberZapExt" position="center,center" size="600,100" title="Extended NumberZap">
            <widget name="chPicon" position="490,15" size="100,60" />
            <widget name="number"  position="5,5"   size="150,30" halign="right" font="Regular;24" />
            <widget name="chNum"   position="170,5" size="240,30" halign="left"  font="Regular;24" />
            <widget name="channel" position="5,35"   size="150,30" halign="right" font="Regular;24" />
            <widget name="chName"  position="170,36" size="310,30" halign="left"  font="Regular;22" noWrap="1" />
            <widget name="bouquet" position="5,65"   size="150,30" halign="right" font="Regular;24" />
            <widget name="chBouq"  position="170,66" size="310,30" halign="left"  font="Regular;22" noWrap="1" />
           </screen>"""      

    def __init__(self, session, number, servicelist = None):
        Screen.__init__(self, session)
        self.digits = 4
        self.field = str(number)
        self.servicelist = servicelist
        self.kdelay = config.plugins.NumberZapExt.kdelay.value
        self.bouqSelDlg = None
        self.bouquet = None
        self.action = ''
        self.action_prio = 'low'
        self.defpicon = None
        for scope, path in {SCOPE_SKIN_IMAGE: 'skin_default/picon_default.png',
         SCOPE_CURRENT_SKIN: 'picon_default.png'}.items():
            tmp = resolveFilename(scope, path)
            if pathExists(tmp):
                self.defpicon = tmp
                break

        self.picons = config.plugins.NumberZapExt.picons.value
        self['number'] = Label(_('Number:'))
        self['channel'] = Label(_('Channel:'))
        self['bouquet'] = Label(_('Bouquet:'))
        self['chNum'] = Label()
        self['chName'] = Label()
        self['chBouq'] = Label()
        self['chPicon'] = Pixmap()
        self['actions'] = NumberActionMap(['SetupActions'],
         {
         'cancel': self.quit,
         'ok': self.keyOK,
         '1': self.keyNumberGlobal,
         '2': self.keyNumberGlobal,
         '3': self.keyNumberGlobal,
         '4': self.keyNumberGlobal,
         '5': self.keyNumberGlobal,
         '6': self.keyNumberGlobal,
         '7': self.keyNumberGlobal,
         '8': self.keyNumberGlobal,
         '9': self.keyNumberGlobal,
         '0': self.keyNumberGlobal
         })
        self.nameCache = { }
        self.Timer = eTimer()
        self.timer_conn = self.Timer.timeout.connect(self.keyOK)
        self.onFirstExecBegin.append(self.__onStart)
        return

    def __onStart(self):
        if self.servicelist and self.servicelist.getMutableList() is None and config.plugins.NumberZapExt.acount.value:
            bouquets = self.servicelist.getBouquetList()
            if not bouquets:
                self.quit()
            if len(bouquets) == 1:
                self.bouquetSelected(bouquet[0][1])
            else:
                self.bouqSelDlg = self.session.openWithCallback(self.bouquetSelectorClosed, BouquetSelector, bouquets, self.bouquetSelected, enableWrapAround=True)
        else:
            self.printLabels()
            self.startTimer()
        return

    def bouquetSelectorClosed(self, retval):
        if retval is False:
            self.quit()
        else:
            self.bouqSelDlg = None
        return

    def bouquetSelected(self, bouquet):
        if self.bouqSelDlg:
            self.bouqSelDlg.close(True)
        self.bouquet = bouquet
        self.printLabels()
        self.startTimer()

    def startTimer(self):
        if self.kdelay:
            self.Timer.start(self.kdelay, True)

    def printLabels(self):
        if self.action_prio != 'low':
            self.action = self.getHotkeyAction(int(self.field))
            if self.action:
                name = self.action.replace('_', ' ').title()
                channel = _('Action:')
                bouquet = bqname = ''
            else:
                channel = _('Channel:')
                bouquet = _('Bouquet:')
                service, name, bqname = self.getNameFromNumber(int(self.field))
                if name == 'N/A':
                    name = _('invalid channel number')
        else:
            channel = _('Channel:')
            bouquet = _('Bouquet:')
            self.action = ''
            service, name, bqname = self.getNameFromNumber(int(self.field))
            if name == 'N/A':
                if service is not None:
                    name = _('service not found')
                else:
                    name = _('invalid channel number')
                    self.action = self.getHotkeyAction(int(self.field))
                    if self.action:
                        name = self.action.replace('_', ' ').title()
                        channel = _('Action:')
                        bouquet = bqname = ''
        self['chNum'].setText(self.field)
        self['channel'].setText(channel)
        self['bouquet'].setText(bouquet)
        self['chName'].setText(name)
        self['chBouq'].setText(bqname)
        if self.picons:
            pngname = self.defpicon
            if service:
                sname = service.toString()
                pngname = PiconResolver.getPngName(sname, self.nameCache, self.findPicon)
                #pos = sname.rfind(':')
                #if pos != -1:
                #    sname = sname[:pos].rstrip(':').replace(':', '_')
                #    sname = config.plugins.NumberZapExt.picondir.value + sname + '.png'
                #    if pathExists(sname):
                #        pngname = sname
            self['chPicon'].instance.setPixmapFromFile(pngname)
        return

    def quit(self):
        self.Timer.stop()
        self.close(0, None)
        return

    def keyOK(self):
        self.Timer.stop()
        self.close(int(self['chNum'].getText()), self.action or self.bouquet)

    def keyNumberGlobal(self, number):
        self.startTimer()
        l = len(self.field)
        if l < self.digits:
            l += 1
            self.field = self.field + str(number)
            self.printLabels()
        if l >= self.digits and self.kdelay:
            self.keyOK()

    def getNameFromNumber(self, number):
        name = 'N/A'
        bqname = 'N/A'
        service, bouquet = getServiceFromNumber(self, number, config.plugins.NumberZapExt.acount.value, self.bouquet)
        if service is not None:
            serviceHandler = eServiceCenter.getInstance()
            info = serviceHandler.info(service)
            name = info and info.getName(service) or 'N/A'
            if bouquet and bouquet.valid():
                info = serviceHandler.info(bouquet)
                bqname = info and info.getName(bouquet)
        return (service, name, bqname)

    def getHotkeyAction(self, number):
        if config.plugins.NumberZapExt.hotkey.value:
            for key, val in config.plugins.NumberZapExt.action.content.items.items():
                if val.value == number:
                    return key

        return ''
    def findPicon(self, serviceName):
         pngname = config.plugins.NumberZapExt.picondir.value + serviceName + ".png"
         if fileExists(pngname):
            return pngname
         return ""


def getServiceFromNumber(self, number, acount = True, bouquet = None):

    def searchHelper(serviceHandler, num, bouquet):
        servicelist = serviceHandler.list(bouquet)
        if servicelist is not None:
            while num:
                s = servicelist.getNext()
                if not s.valid():
                    break
                if not s.flags & (eServiceReference.isMarker | eServiceReference.isDirectory):
                    num -= 1

            if not num:
                return (s, num)
        return (None, num)

    if self.servicelist is None:
        return
    else:
        service = None
        serviceHandler = eServiceCenter.getInstance()
        if not config.usage.multibouquet.value:
            bouquet = self.servicelist.bouquet_root
            service, number = searchHelper(serviceHandler, number, bouquet)
        elif acount and self.servicelist.getMutableList() is not None:
            bouquet = self.servicelist.getRoot()
            service, number = searchHelper(serviceHandler, number, bouquet)
        elif acount and bouquet is not None:
            service, number = searchHelper(serviceHandler, number, bouquet)
        else:
            bouquet = self.servicelist.bouquet_root
            bouquetlist = serviceHandler.list(bouquet)
            if bouquetlist is not None:
                while number:
                    bouquet = bouquetlist.getNext()
                    if not bouquet.valid():
                        break
                    if bouquet.flags & eServiceReference.isDirectory:
                        service, number = searchHelper(serviceHandler, number, bouquet)
                        if acount:
                            break

        return (service, bouquet)


def zapToNumber(self, number, bouquet):
    service, bouquet = getServiceFromNumber(self, number, config.plugins.NumberZapExt.acount.value, bouquet)
    if service is not None:
        if self.servicelist.getRoot() != bouquet:
            self.servicelist.clearPath()
            if self.servicelist.bouquet_root != bouquet:
                self.servicelist.enterPath(self.servicelist.bouquet_root)
            self.servicelist.enterPath(bouquet)
        self.servicelist.setCurrentSelection(service)
        self.servicelist.zap()
    return


def numberEntered(self, retval, bouquet = None):
    if retval > 0:
        if isinstance(bouquet, str):
            if config.plugins.NumberZapExt.action.confirm.value:
                from Screens.MessageBox import MessageBox
                self.session.openWithCallback(boundFunction(self, bouquet), MessageBox, _('Really run %s now?') % bouquet.replace('_', ' ').title(), type=MessageBox.TYPE_YESNO, timeout=10, default=True)
        else:
            zapToNumber(self, retval, bouquet)


def new_keyNumberGlobal(self, number):
    global base_keyNumberGlobal
    if not config.plugins.NumberZapExt.enable.value or number == 0:
        base_keyNumberGlobal(self, number)
    else:
        try:
            pts_enabled = config.plugins.pts.enabled.value
        except:
            pts_enabled = False

        if self.has_key('TimeshiftActions') and not self.timeshift_enabled or pts_enabled:
            self.session.openWithCallback(boundFunction(numberEntered, self), NumberZapExt, number, self.servicelist)


def new_getBouquetNumOffset(self, bouquet):
    global base_getBouquetNumOffset
    if config.plugins.NumberZapExt.acount.value:
        return 0
    else:
        return base_getBouquetNumOffset(self, bouquet)


def new_AltCountChanged(self, configElement):
    service = self.getCurrentSelection()
    self.setRoot(self.getRoot())
    self.setCurrentSelection(service)


def new_ChannelSelectionBase__init__(self, session):
    global base_ChannelSelectionBase__init__
    config.plugins.NumberZapExt.acount.addNotifier(self.AltCountChanged, False)
    base_ChannelSelectionBase__init__(self, session)


def StartMainSession(session, **kwargs):
    global base_keyNumberGlobal
    global base_getBouquetNumOffset
    global base_ChannelSelectionBase__init__
    from Screens.InfoBar import InfoBar
    if base_getBouquetNumOffset is None:
        base_getBouquetNumOffset = ChannelSelectionBase.getBouquetNumOffset
        ChannelSelectionBase.getBouquetNumOffset = new_getBouquetNumOffset
    if base_ChannelSelectionBase__init__ is None:
        base_ChannelSelectionBase__init__ = ChannelSelectionBase.__init__
        ChannelSelectionBase.__init__ = new_ChannelSelectionBase__init__
        ChannelSelectionBase.AltCountChanged = new_AltCountChanged
    if base_keyNumberGlobal is None:
        base_keyNumberGlobal = InfoBar.keyNumberGlobal
        InfoBar.keyNumberGlobal = new_keyNumberGlobal
    return


def OpenSetup(session, **kwargs):
    import NumberZapExtSetup
    session.open(NumberZapExtSetup.NumberZapExtSetupScreen)


def StartSetup(menuid, **kwargs):
    if menuid == "services_recordings":
        return [(_('Extended NumberZap'),
          OpenSetup,
          'numzapext_setup',
          None)]
    else:
        return []
        return None


def Plugins(**kwargs):
    return [PluginDescriptor(name=_('Extended NumberZap'), description=_('Extended NumberZap addon'), where=PluginDescriptor.WHERE_SESSIONSTART, fnc=StartMainSession), PluginDescriptor(name=_('Extended NumberZap'), description=_('Extended NumberZap addon'), where=PluginDescriptor.WHERE_MENU, fnc=StartSetup)]