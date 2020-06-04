#!/usr/bin/python
# -*- coding: utf-8 -*-

from Screens.ChannelSelection import BouquetSelector, SilentBouquetSelector
from ServiceReference import ServiceReference
from skin import parseColor
from Components.config import config, ConfigClock, ConfigInteger
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.HTMLComponent import HTMLComponent
from Components.GUIComponent import GUIComponent
from Components.EpgList import Rect
from Components.Sources.Event import Event
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.TimerList import TimerList
from Components.TimerSanityCheck import TimerSanityCheck
from Components.ServiceList import PiconLoader

from Screens.Screen import Screen
from Screens.EventView import EventViewSimple, EventViewEPGSelect
from Screens.TimeDateInput import TimeDateInput
from Screens.TimerEntry import TimerEntry
from Screens.EpgSelection import EPGSelection
from Screens.TimerEdit import TimerSanityConflict
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.HelpMenu import HelpableScreen
from Screens.InfoBar import InfoBar

from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
from RecordTimer import RecordTimerEntry, parseEvent, AFTEREVENT
from ServiceReference import ServiceReference
#for more-key
from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins

from enigma import eEPGCache, eListbox, gFont, eListboxPythonMultiContent, eServiceCenter, eServiceReference, RT_HALIGN_LEFT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, RT_WRAP, eRect, eTimer, getDesktop, iPlayableService, gPixmapPtr, eSize, eDVBVolumecontrol, SCALE_ASPECT, SCALE_HEIGHT, loadPNG, ePoint, eVideoWidget
from time import localtime, time, strftime, mktime
from datetime import datetime
#from pprint import pprint
import os

import MultiEPGSetup

# Movie preview
#from Components.VideoWindow import VideoWindow

Session = None
Servicelist = None
bouquetSel = None
epg_bouquet = None
bouquet_name = None
activeEventID = None
goNext = False

current_service_name = ""

sz_w = getDesktop(0).size().width()
sz_h = getDesktop(0).size().height()

########################################################################################

class EPGList(HTMLComponent, GUIComponent):   # 6. Schritt ==========
	def __init__(self, session, selChangedCB=None, timer = None, time_epoch = 180, overjump_empty=False):
		#print " ============= EPGList ==============="
		self.cur_event = None
		self.cur_service = None
		self.offs = 0
		self.session = session
		self.timer = timer
		self.onSelChanged = [ ]
		self.setActiveEvent = False
		self.old_event_isLive = True
		self.last_time=0
		if selChangedCB is not None:
			self.onSelChanged.append(selChangedCB)
		GUIComponent.__init__(self)
		self.l = eListboxPythonMultiContent()
		if sz_w == 1920:
			self.l.setItemHeight(55)
			self.itemheightorg = 55
		else:
			self.l.setItemHeight(36)
			self.itemheightorg = 36
		self.l.setBuildFunc(self.buildEntry)
		if overjump_empty:
			self.l.setSelectableFunc(self.isSelectable)
		self.epgcache = eEPGCache.getInstance()
		
		self.clock_pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/epgclock.png'))
		self.clock_add_pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/epgclock_add.png'))
		self.clock_pre_pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/epgclock_pre.png'))
		self.clock_post_pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/epgclock_post.png'))
		self.clock_prepost_pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/epgclock_prepost.png'))
		
		self.time_base = None
		self.time_epoch = time_epoch
		self.list = None
		self.event_rect = None
		self.foreColor = None
		self.foreColorSelected = 0x00fcc000
		self.borderColor = 0x00555556
		self.backColor = 0x10303030
		self.backColorSelected = 0x104c0000
		self.foreColorService = None
		self.foreColorActiveService = None
		self.backColorActiveService = 0x10ededed
		self.backColorService = 0x10323c4d
		self.backColorServiceSelected = 0x105c0000
		self.nowBackColor = 0x10001e4b
		self.nowTimerBackColor = 0x108a2be2 # violett for now Timer
		self.PrimetimeBackColor = 0x000579d4
		#self.GoodiesBackColor = 0x10004c00
		self.TimerBackColor = 0x105c0000 # rot fuer timer hintergrund
		self.halfTimerBackColor = 0x105c3030 # blasseres rot for half Timer events
		self.TimerBackColorSelected = 0x10ffa07a # Light Salmon for selected Timer
		self.offTimerBackColor = 0x10999999 #gray for inactive timer
		self.errorTimerBackColor = 0x10ffff00 #yellow for inactive timer
		
		fontsizeoffset = int(config.plugins.multiepgmv.fontsizeoffset.value)
		if sz_w == 1920:
			Testfont = gFont("Regular", 25 + fontsizeoffset)
		else:
			Testfont = gFont("Regular", 19 + fontsizeoffset)
		self.Alphasize = Testfont.pointSize


	def applySkin(self, desktop, screen):   # 7. Schritt - Nach EPGList
		#print " ============= applaySkin ==============="
		if self.skinAttributes is not None:
			attribs = [ ]
			for (attrib, value) in self.skinAttributes:
				if attrib == "EntryForegroundColor":
					self.foreColor = parseColor(value).argb()
				elif attrib == "EntryForegroundColorSelected":
					self.foreColorSelected = parseColor(value).argb()
				elif attrib == "EntryBorderColor":
					self.borderColor = parseColor(value).argb()
				elif attrib == "EntryBackgroundColor":
					self.backColor = parseColor(value).argb()
				elif attrib == "EntryBackgroundColorSelected":
					self.backColorSelected = parseColor(value).argb()
				elif attrib == "ServiceNameForegroundColor":
					self.foreColorService = parseColor(value).argb()
				elif attrib == "ActiveServiceNameForegroundColor":
					self.foreColorActiveService = parseColor(value).argb()
				elif attrib == "ActiveServiceNameBackgroundColor":
					self.backColorActiveService = parseColor(value).argb()
				elif attrib == "ServiceNameBackgroundColor":
					self.backColorService = parseColor(value).argb()
				elif attrib == "NowBackgroundColor":
					self.nowBackColor = parseColor(value).argb()
				elif attrib == "PrimetimeBackgroundColor":
					self.PrimetimeBackColor = parseColor(value).argb()
				elif attrib == "TimerBackgroundColor":
					self.TimerBackColor = parseColor(value).argb()
				elif attrib == "TimerBackColorSelected":
					self.TimerBackColorSelected = parseColor(value).argb()
				elif attrib == "halfTimerBackgroundColor":
					self.halfTimerBackColor = parseColor(value).argb()
				elif attrib == "offTimerBackgroundColor":
					self.offTimerBackColor = parseColor(value).argb()
				elif attrib == "errorTimerBackgroundColor":
					self.errorTimerBackColor = parseColor(value).argb()
				elif attrib == "nowTimerBackgroundColor":
					self.nowTimerBackColor = parseColor(value).argb()
				else:
					attribs.append((attrib,value))
			self.skinAttributes = attribs
		return GUIComponent.applySkin(self, desktop, screen)

	def fillMultiEPG(self, services, stime=-1):  # 9. Schritt nach onCreate() aus Screen
		currentservice = self.session.nav.getCurrentService()
		currentinfo = currentservice.info()
		global current_service_name
		current_service_name = currentinfo.getName().replace('\xc2\x86', '').replace('\xc2\x87', '')
		#print " === MEPGMV fillMultiEPG current_service_name:", str(current_service_name)
		if services is None:
			time_base = self.time_base+self.offs*self.time_epoch*60
			if stime > 0:
				time_base = int(stime)
				self.time_base = time_base
			test = [ (service[0], 0, time_base, self.time_epoch) for service in self.list ]
		else:
			self.cur_event = None
			self.cur_service = None
			self.time_base = int(stime)
			test = [ (service.ref.toString(), 0, self.time_base, self.time_epoch) for service in services ]
		test.insert(0, 'XRnITBD') # N = ServiceName, n = short ServiceName
		#R = ServiceRef, n = ShortServiceName (N= ServiceName), I=id, T=Titel, B=Begin, D=Duration
		
		#List of all epgcache-Parameters
		#I = Event Id, B = Event Begin Time, D = Event Duration, T = Event Title
		#S = Event Short Description, E = Event Extended Description,  C = Current Time
		#R = Service Reference String, N = Service Name, n = Short Service Name
		#X = Return a minimum of one tuple per service in the result list... even when no event was found.
		
		epg_data = self.queryEPG(test)
		self.list = [ ]
		tmp_list = None
		service = ""
		sname = ""
		for x in epg_data:
			if service != x[0]:
				if tmp_list is not None:
					self.list.append((service, sname, tmp_list[0][0] is not None and tmp_list or None))
				service = x[0]
				sname = ServiceReference(service).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
				#sname = x[1] #only short serviceName
				#print "=== MEPGMV service, sname:", service, sname, x
				tmp_list = [ ]
			tmp_list.append((x[2], x[3], x[4], x[5]))
		if tmp_list and len(tmp_list):
			self.list.append((service, sname, tmp_list[0][0] is not None and tmp_list or None))
		
		#print " === MEPGMV fillMultiEPG setList"
		self.l.setList(self.list)
		#self.findBestEvent()

	def findBestEvent(self): # 10. Schritt nach fillMultiEPG
		#print "============= findbestevent ==============="
		old_service = self.cur_service  #(service, service_name, events)
		cur_service = self.cur_service = self.l.getCurrentSelection()
		old_sender = None
		old_event = None
		current_event_live = None
		if old_service:
			old_sender = old_service[1]
		#print "========== findbestevent - cur_service, oldservice: ", cur_service[1], old_sender
		time_base = self.getTimeBase()
		if old_service and self.cur_event is not None:
			#print "============= findbestevent - if oldservice ====="
			old_events = old_service[2]
			old_event = old_events[self.cur_event] #(event_id, event_title, begin_time, duration)
			self.last_time = old_event[2]
			if self.last_time < time_base:
				self.last_time = time_base
		if cur_service:
			#print "============= findbestevent - if cur_service ====="
			self.cur_event = 0
			events = cur_service[2]
			#print "findbestevent - cur_service, current_service_name: ", cur_service[1], current_service_name
			if events and len(events):
				if self.last_time or self.old_event_isLive:
					best_diff = 0
					best = len(events) #set invalid
					idx = 0
					#current_event_live = None
					for event in events: #iterate all events
						now = int(time())
						#== Setzen des ActiveEvents (ID) ===
						if self.setActiveEvent == False and cur_service[1] == current_service_name:
							if event[2] <= now and (event[2] + event[3]) > now:
								#print "========== SetActiveEvent ============================"
								global activeEventID
								activeEventID=event[0]
								self.setActiveEvent=True
						ev_time = event[2]
						if ev_time < time_base:
							ev_time = time_base
						diff = abs(ev_time-self.last_time)
						if (best == len(events)) or (diff < best_diff):
							best = idx
							best_diff = diff
						#== zwischenseichern, welches Event gerade laeuft ====
						if (event[2] <= now and (event[2] + event[3]) > now): 
							#print "========== Bestevent current live =====", event[1]
							current_event_live = idx
						idx += 1
					if best != len(events):
						self.cur_event = best
					#falls bei Auswahlwechsel die alte Sendung aktuell war und die neue bereits alt ist====
					self.setOldEventIsLive(old_event, now)
					#print "= Bestevent best vorschlag:   ", events[best], best
					if (events[best][2] <= now and (events[best][2] + events[best][3]) < now) or (events[best][2] > now): 
						#print "========== Bestevent best vorschlag ist unpassend =====", events[best][1]
						self.setIfCurrentEventLive(current_event_live, events)
			else:
				#print "========== findbestevent - self.cur_event = None ====="
				self.cur_event = None
				self.setIfCurrentEventLive(current_event_live, events)
		else:
			#print "========== findbestevent - kein Old_service ====="
			self.setOldEventIsLive(old_event, now)
			self.setIfCurrentEventLive(current_event_live)
		self.setIfCurrentEventLive(current_event_live, events)
		self.selEntry(0)

#== anhand des old-events ziwschenspeichern, ob das old-event eine aktuelle Sendung (live-event) war
	def setOldEventIsLive(self, old_event, now):
		if old_event and (old_event[2] <= now and (old_event[2] + old_event[3]) > now):
			#print "========== old is Live =====", old_event[1]
			self.old_event_isLive = True
		else:
			if old_event:
				#print "========== old is NOT live =====", old_event[1]
				pass
			else:
				#print "========== old is None ====="
				pass
			self.old_event_isLive = False
		return

#== falls ein aktuelles Live-event gefunden und das old-Event auch live war, dann aktuelle Sendung (live-event) setzen
	def setIfCurrentEventLive(self, current_event_live, events):
		if current_event_live != None and self.old_event_isLive:
			self.cur_event = current_event_live
			#print "========== Bestevent live:   ", events[current_event_live]
		return


	def selEntry(self, dir, visible=True):   # 11. Schritt
		#print " ============= selEntry ==============="
		cur_service = self.cur_service #(service, service_name, events)
		#print "MEPGMV - cur_service: ", cur_service
		#pprint (cur_service)
		self.recalcEntrySize()
		valid_event = self.cur_event is not None
		if cur_service:
			#print "MEPGMV - after if cur_service - valid_event: ", valid_event
			#pprint (valid_event)
			update = True
			entries = cur_service[2]
			#pprint(entries)
			if dir == 0: #current
				update = False
			elif dir == +1: #next
				if valid_event and self.cur_event+1 < len(entries):
					self.cur_event+=1
				else:
					self.offs += 1
					self.fillMultiEPG(None) # refill
					return True
			elif dir == -1: #prev
				if valid_event and self.cur_event-1 >= 0:
					self.cur_event-= 1
				elif valid_event and self.cur_event-1 <0 and self.offs<1:
					self.resetOffset()
					self.cur_event = 0
					self.fillMultiEPG(None, self.time_base - 3600)
					return True
				elif self.offs > 0:
					self.offs -= 1
					self.fillMultiEPG(None) # refill
					return True
		if cur_service and valid_event:
			#print "MEPGMV: after if cur_service and valid_event"
			entry = entries[self.cur_event] #(event_id, event_title, begin_time, duration)
			#print "MEPGMV: after if cur_service and valid_event - entry", entry
			time_base = self.time_base+self.offs*self.time_epoch*60
			xpos, width = self.calcEntryPosAndWidth(self.event_rect, time_base, self.time_epoch, entry[2], entry[3])
			self.l.setSelectionClip(eRect(xpos, 0, width, self.event_rect.height()), visible and update)
		else:
			#print "MEPGMV: after if not cur_service and valid_event (else)"
			self.l.setSelectionClip(eRect(self.event_rect.left(), self.event_rect.top(), self.event_rect.width(), self.event_rect.height()), False)
		self.selectionChanged()
		#print "============ end selENtry =========================="
		return False

	def connectSelectionChanged(func):
		if not self.onSelChanged.count(func):
			self.onSelChanged.append(func)

	def isSelectable(self, service, sname, event_list):
		return (event_list and len(event_list) and True) or False

	def setEpoch(self, epoch):
#		if self.cur_event is not None and self.cur_service is not None:
		self.offs = 0
		self.time_epoch = epoch
		self.fillMultiEPG(None) # refill

	def getEventFromId(self, service, eventid):
		event = None
		if self.epgcache is not None and eventid is not None:
			event = self.epgcache.lookupEventId(service.ref, eventid)
		return event

	def moveToEventId(self, eventId):
		#print "movetoEventId Start: ", eventId
		return
		if not eventId:
			return
		index = 0
		for x in self.list:
			#pprint (x)
			events = x[2]
			#pprint (events)
			for event in events:
				if event[0] == eventId:
					self.instance.moveSelectionTo(index)
					#print "movetoEventId Treffer: ", eventId, index
					break
				index += 1

	def moveToService(self,serviceref):
		#print "=== MEPGMV moveToService", serviceref.toString()
		if serviceref is not None:
			for x in range(len(self.list)):
				#print "=== MEPGMV moveToService List-Values", self.list[x][0]
				if self.list[x][0] == serviceref.toString():
					self.instance.moveSelectionTo(x)
					break
	
	def getIndexFromService(self, serviceref):
		if serviceref is not None:
			for x in range(len(self.list)):
				if self.list[x][0] == serviceref.toString():
					return x
	
	#== zur angegebenen Zeile (Sender) wechseln
	def setCurrentIndex(self, index):
		if self.instance is not None:
			self.instance.moveSelectionTo(index)
	
	def getCurrent(self):
		if self.cur_service is None:
			return ( None, None )
		old_service = self.cur_service  #(service, service_name, events)
		events = self.cur_service[2]
		refstr = self.cur_service[0]
		if self.cur_event is None or not events or not len(events):
			return ( None, ServiceReference(refstr) )
		event = events[self.cur_event] #(event_id, event_title, begin_time, duration)
		eventid = event[0]
		service = ServiceReference(refstr)
		event = self.getEventFromId(service, eventid)
		return ( event, service )

	def disconnectSelectionChanged(func):
		self.onSelChanged.remove(func)

	def serviceChanged(self):
		cur_sel = self.l.getCurrentSelection()
		if cur_sel:
			self.findBestEvent()
			pass

	def selectionChanged(self):
		for x in self.onSelChanged:
			if x is not None:
				x()
#				try:
#					x()
#				except: # FIXME!!!
#					print "FIXME in EPGList.selectionChanged"
#					pass

	GUI_WIDGET = eListbox

	def postWidgetCreate(self, instance):
		instance.setWrapAround(True)
		instance.selectionChanged_conn = instance.selectionChanged.connect(self.serviceChanged)
		instance.setContent(self.l)
		fontsizeoffset = int(config.plugins.multiepgmv.fontsizeoffset.value)
		if sz_w == 1920:
			self.l.setFont(0, gFont("Regular", 26 + fontsizeoffset))
			self.l.setFont(1, gFont("Regular", 26 + fontsizeoffset))
		else:
			self.l.setFont(0, gFont("Regular", 20 + fontsizeoffset))
			self.l.setFont(1, gFont("Regular", 20 + fontsizeoffset))
		self.l.setSelectionClip(eRect(0,0,0,0), False)

	def preWidgetRemove(self, instance):
		instance.selectionChanged_conn = None
		instance.setContent(None)

	def recalcEntrySize(self): #calculate the width for service-column and events-column
		esize = self.l.getItemSize()
		width = esize.width()
		height = esize.height()
		#print "=== height", height
		xpos = 0;
		#w = int(width/10*1.7);
		#w = int(width/10*1.4); #fuer Sendername als Text
		if sz_w == 1920:
			w = 130
		else:
			w = 85; #fuer Senderlogo
		if not config.plugins.multiepgmv.showpicons.value:
			w = w*2 #double width for service-column if use servicename as text (no picon)
		self.service_rect = Rect(xpos, 0, w-10, height) # service column
		xpos += w;
		#w = int(width/10*9.3);
		#w = int(width/10*8.6);
		#self.event_rect = Rect(xpos, 0, w, height)
		if not config.plugins.multiepgmv.showpicons.value:
			w2 = width - w/2
		else:
			w2 = width
		self.event_rect = Rect(xpos, 0, w2, height) # events column
		#print "=== recalc event_rect_width",w, width, w2

	def calcEntryPosAndWidthHelper(self, stime, duration, start, end, width):
		xpos = (stime - start) * width / (end - start)
		ewidth = (stime + duration - start) * width / (end - start)
		ewidth -= xpos;
		if xpos < 0:
			ewidth += xpos;
			xpos = 0;
		if (xpos+ewidth) > width:
			ewidth = width - xpos
		return xpos, ewidth

	def calcEntryPosAndWidth(self, event_rect, time_base, time_epoch, ev_start, ev_duration):
		xpos, width = self.calcEntryPosAndWidthHelper(ev_start, ev_duration, time_base, time_base + time_epoch * 60, event_rect.width())
		return xpos+event_rect.left(), width

	def buildEntry(self, service, service_name, events):
		#print " ============= buildEntry ================"
		r1=self.service_rect
		r2=self.event_rect
		#print "=== event_rect", r2.width()
		self.fColorService = self.foreColorService
		self.bColorService = self.backColorService
		isActiveService=False
		#print " === MEPGMV buildEntry cur_serv_name, serv_name, sname1: '%s', '%s'" % (current_service_name, service_name)
		if current_service_name == service_name:
			self.fColorService = self.foreColorActiveService
			isActiveService=True
		png_pixmap = None
		if config.plugins.multiepgmv.showpicons.value:
			#png_pixmap = self.getServicePixmap(service)
			try:
				png_pixmap = PiconLoader().getPicon(service)
				pass
			except:
				import traceback
				traceback.print_exc()
		service_name_txt = ""
		if png_pixmap == None:
			service_name_txt = service_name
		#else:
		if current_service_name == service_name:
			self.bColorService = self.backColorActiveService

		service_height = self.l.getItemSize().height()
		
		if sz_w == 1920:
			picon_width = 80 #90
		else:
			picon_width = 50 #60
			
		picon_left = (r1.width() - picon_width) / 2
		
		res = [ None, MultiContentEntryText(
						pos = (r1.left(),r1.top()),
						size = (r1.width(), r1.height()),
						font = 0, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER,
						text = " " + service_name_txt, #+ service_name,
						color = self.fColorService,
						backcolor_sel = self.backColorServiceSelected,
						backcolor = self.bColorService) ]
		res.append(MultiContentEntryPixmapAlphaTest(
						pos=(r1.left()+picon_left,r1.top()+1),
						size=(picon_width, service_height - 2),
						png=png_pixmap,
						backcolor=self.bColorService, #self.backColorService,
						backcolor_sel=self.backColorServiceSelected,
						scale_flags=SCALE_ASPECT))
		
		#== Darstellung der Timer =====================================================
		show_banner = config.plugins.multiepgmv.timerdisplay.value
		if show_banner == "True": show_banner = True
		if show_banner == "False": show_banner = False
		#== Darstellung der Timer als Farbe + Symbole für Vor-/Nachlaufzeit ===========
		if show_banner in ("org", "own", "owntxt"):
			show_symbol = show_banner
			show_banner = False
		else:
			show_symbol = False

		if events:
			start = self.time_base+self.offs*self.time_epoch*60
			end = start + self.time_epoch * 60
			left = r2.left()
			top = r2.top()
			width = r2.width()
			height = r2.height()
			foreColor = self.foreColor
			backColor = self.backColor
			borderColor = self.borderColor
			now = int(time())
			myPT = float(str(config.plugins.multiepgmv.prime_time.value[0])+"."+str("%0.2d" % config.plugins.multiepgmv.prime_time.value[1]))
			Primerime1 = myPT - 0.05
			Primerime2 = myPT + 0.05
			for ev in events:  #(event_id, event_title, begin_time, duration)
				backColor = self.backColor
				backColorSelected = self.backColorSelected
				foreColorSelected = self.foreColorSelected
				pt_t = localtime(ev[2])
				evCHT = float(str(pt_t[3])+"."+str("%0.2d" % pt_t[4]))
				
				bannerWidth_faktor=1
				banner_pos=0
				banner_width = 0
				banner_typ=0
				banner_pos_left=0
				#== check event ist Timer with set width of banner and banner_typ ==========
				bannerWidth_faktor, banner_width, banner_pos, banner_typ, banner_pos_left, banner_width2 = self.getBannerWidth(service, ev[2], ev[3], ev[0], ev[1], start, end, width)
				
				rec = banner_typ
				isRecordEvent = (banner_typ==1)
				
				xpos, ewidth = self.calcEntryPosAndWidthHelper(ev[2], ev[3], start, end, width)
				# calclate addtxt on show_symbol
				typ, png = self.getClockPixmap(service, ev[2], ev[3], ev[0])
				symboltxt = ""
				if typ in (3, 4) and show_symbol and show_symbol != "org": symboltxt = "  "
				
				TxtLen = int((ewidth/self.Alphasize)*1.4)
				if TxtLen<3:
					ShowTxt = " "
				elif len(ev[1])>TxtLen:
					#ShowTxt = " " + ev[1][:TxtLen] + ".."
					if typ in (1, 4): 
						TxtLen = TxtLen - 1
					ShowTxt = " " + str(unicode(ev[1].encode("utf-8"),"utf-8")[:TxtLen]) + ".."
				else:
					ShowTxt = " " + ev[1]
				if ev[2] <= now and (ev[2] + ev[3]) > now:
					backColor = self.nowBackColor
					if rec and show_banner == False:
						#== aktuelle Sendung mit Aufnahme nicht blau sondern rot wie alle anderen Timer
						if banner_typ == 1 or banner_typ == 5 or ((banner_typ == 2 or banner_typ == 6) and not show_symbol):
							backColor = self.TimerBackColor
							backColorSelected = self.TimerBackColorSelected
							if not isRecordEvent:
								backColor = self.halfTimerBackColor
								backColorSelected = self.backColorSelected
				elif (evCHT >= Primerime1) and (evCHT <= Primerime2):
					backColor = self.PrimetimeBackColor
					if rec and show_banner == False:
						if banner_typ == 1 or banner_typ == 5 or ((banner_typ == 2 or banner_typ == 6) and not show_symbol):
							#== Sendung mit Aufnahme nicht gruen sondern rot wie alle anderen Timer
							backColor = self.TimerBackColor
							backColorSelected = self.TimerBackColorSelected
							#== falls Sendung selbst nicht aufgenommen wird, aber der Timer reinragt
							if not isRecordEvent:
								backColor = self.halfTimerBackColor
								backColorSelected = self.backColorSelected
				#elif "live" in ev[1].lower():
					#backColor = self.GoodiesBackColor
				elif rec and show_banner == False:
					if banner_typ == 1 or banner_typ == 5 or ((banner_typ == 2 or banner_typ == 6) and not show_symbol):
						backColor = self.TimerBackColor
						backColorSelected = self.TimerBackColorSelected
						if not isRecordEvent:
							backColor = self.halfTimerBackColor
							backColorSelected = self.backColorSelected
				else:
					backColor = self.backColor
				
				res.append(MultiContentEntryText(
					pos = (left+xpos, top), size = (ewidth, height),
					font = 1, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER,
					text = symboltxt + ShowTxt, color = foreColor, color_sel = foreColorSelected,
					backcolor = backColor, backcolor_sel = backColorSelected, border_width = 1, border_color = borderColor))

				#show org e2 symbols 
				if show_symbol == "org" and rec and ewidth > 23:
					res.append(MultiContentEntryPixmapAlphaTest(
						pos = (left+xpos+ewidth-22, top+height/2-11), size = (21, 21),
						png = png,
						backcolor = backColor,
						backcolor_sel = backColorSelected))
				
				#show own symbols 
				if show_symbol == "own" and rec and ewidth > 23 and (banner_typ == 2 or banner_typ == 6):
					if typ ==3:
						leftpos = left +xpos
					else:
						leftpos = left+xpos+ewidth-22
					res.append(MultiContentEntryPixmapAlphaTest(
						pos = (leftpos, top+height/2-11), size = (21, 21),
						png = png,
						backcolor = backColor,
						backcolor_sel = backColorSelected))
				
				#show own text 
				if show_symbol == "owntxt" and rec and (banner_typ == 2 or banner_typ == 6):
					if sz_w == 1920: 
						owntxt_width=20 
					else: 
						owntxt_width=15
					if typ == 4:
						leftpos = left +xpos+3
						ShowTxt = ">"
						res.append(MultiContentEntryText(
							pos = (leftpos, top+1), size = (owntxt_width, height-2),
							font = 1, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER,
							text = ShowTxt, color = foreColor, color_sel = foreColorSelected,
							backcolor = backColor, backcolor_sel = backColorSelected, border_width = 0))
						leftpos = left+xpos+ewidth-owntxt_width
						ShowTxt = "<"
						res.append(MultiContentEntryText(
							pos = (leftpos, top+1), size = (owntxt_width, height-2),
							font = 1, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER,
							text = ShowTxt, color = foreColor, color_sel = foreColorSelected,
							backcolor = backColor, backcolor_sel = backColorSelected, border_width = 0))
					else:
						if typ == 3:
							leftpos = left +xpos+3
							ShowTxt = ">"
						else:
							leftpos = left+xpos+ewidth-owntxt_width
							ShowTxt = "<"
						res.append(MultiContentEntryText(
							pos = (leftpos, top+1), size = (owntxt_width, height-2),
							font = 1, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER,
							text = ShowTxt, color = foreColor, color_sel = foreColorSelected,
							backcolor = backColor, backcolor_sel = backColorSelected, border_width = 0))
				
				#== Darstellung der Timer als schmale Banner oder voll ===========
				if show_banner:
					#banner_typ=0   #0=kein Timer, 1=Timer, 2=PreAfterTimer, 3=errTimer, 4=offTimer
					if banner_typ:
							if banner_typ == 1 or banner_typ == 5:
								bannerColor=self.TimerBackColor
							elif banner_typ == 2 or banner_typ == 6:
								bannerColor = self.halfTimerBackColor
							elif banner_typ == 3 or banner_typ == 7:
								bannerColor = self.errorTimerBackColor
							elif banner_typ == 4:
								#print "=== banner_typ", banner_typ, ShowTxt
								bannerColor = self.offTimerBackColor
							backColor = bannerColor
							backColorSelected = bannerColor
							entry_width = ewidth-2
							entry_pos = left+xpos+1
							bannerheight = height / 6 + int(config.plugins.multiepgmv.bannerheightoffset.value)
							if bannerheight > height / 3: bannerheight = height / 3
							if bannerheight < 1: bannerheight = 1
							if banner_typ:  #not isRecordEvent:
								#print "== banner_pos: ", banner_pos, ev[1]
								#if bannerWidth_faktor != 1:
									#banner_ewidth = ewidth*bannerWidth_faktor
								if banner_width != 0 and banner_typ != 1 and banner_typ != 5:
									if banner_width > entry_width:
										banner_width = entry_width
									entry_width = banner_width
								if banner_width2 and (banner_typ==2 or banner_typ==6):  #links und rechts
									res.append(MultiContentEntryText(
										pos = (entry_pos, top+height-bannerheight-1), size = (banner_width2, bannerheight),
										font = 1, flags = RT_HALIGN_CENTER | RT_VALIGN_CENTER | RT_WRAP,
										text = "", color = foreColor, color_sel = foreColorSelected,
										backcolor = backColor, backcolor_sel = backColorSelected, border_width = 0, border_color = borderColor))
								if banner_pos == 1:  #rechts im Eintrag ausgerichtet
									entry_pos = entry_pos + ewidth - entry_width - 1
								if banner_pos == 2:  #in der mitte des Eintrages
									#banner_width = float(endTimer - begTimer) / (end - start) * width
									#entry_pos = left+xpos+1 + banner_pos_left
									entry_pos = left+xpos+1 + float(ewidth*bannerWidth_faktor)
							
							res.append(MultiContentEntryText(
								pos = (entry_pos, top+height-bannerheight-1), size = (entry_width, bannerheight),
								font = 1, flags = RT_HALIGN_CENTER | RT_VALIGN_CENTER | RT_WRAP,
								text = "", color = foreColor, color_sel = foreColorSelected,
								backcolor = backColor, backcolor_sel = backColorSelected, border_width = 0, border_color = borderColor))
				
				
		return res


	#== ermittelt die Bannerbreite, Position und Typ des Events  ====
	def getBannerWidth(self, refstr, beginTime, duration, eventId, eventName, start, end, width):
		
		duration_org = duration
		beginTime_org = beginTime
		endTime_org = beginTime + duration
		endTime = beginTime + duration
		
		#Zeiten auf volle Minuten abrunden =====
		endTime = endTime - (endTime % 60) 
		#eventDauer auf/abrunden auf volle Minute =====
		duration = duration - (duration % 60)
		#eventBeginTime auf/abrunden auf volle Minute =====
		beginTime = beginTime - (beginTime % 60) 

		#print "== check Timer: ", eventId, eventName
		width_faktor=1
		banner_width = float(duration) / (end - start) * width
		pos=0   # 0=links, 1=rechts ausgerichtet, 2=mitte, 3=links und rechts
		typ=0   #0=kein Timer, 1=Timer, 2=PreAfterTimer, 3=errTimer, 4=offTimer
		pos_left=0 #Abstand von links
		banner_width2=0
		
		#== wenn kein Timer, dann check inactive Timer =====================
		#print "=== len offtimer", len(self.timer.processed_timers)
		for timerOff in self.timer.processed_timers:
			#self.timer.processed_timers.remove(timerOff)
			#print "== offTimer: ", timerOff.eit, eventName
			if timerOff.eit == eventId:
				#print "== offTimer: ", timerOff.eit, eventName
				typ = 4
				return width_faktor, banner_width, pos, typ, pos_left, banner_width2
		
		for x in self.timer.timer_list:
			#print "== getBanner EvStart, EvEnde, TimerStart, TimerEnde:"
			if x.service_ref.ref.toString() == refstr:
				begTimer = x.begin
				endTimer = x.end
				
				#== wenn eventId in Timerliste gefunden =====
				if x.eit == eventId:
					#print "== Timer gefunden: ", x.eit, x.name
					if begTimer <= beginTime and endTimer >= endTime:
						#print "== echter Timer: ", x.eit, eventName
						pos=0
						if not x.justplay:
							typ=1
						else:
							typ=5
						banner_width = float(duration) / (end - start) * width
						return width_faktor, banner_width, pos, typ, pos_left, banner_width2
					if begTimer > beginTime or endTimer < endTime:
						pos=0
						if begTimer > beginTime:
							pos=1 #rechts ausgerichtet
						if begTimer > beginTime and endTimer < endTime:
							pos=2 #zentriert
							pos_left = float(begTimer - beginTime) / (end - start) * width
							width_faktor = (begTimer - beginTime) / float(duration)
						if not x.justplay:
							typ=3
						else:
							type=7
						banner_width = float(endTimer - begTimer) / (end - start) * width
						return width_faktor, banner_width, pos, typ, pos_left, banner_width2
				
				#== wenn event zeitlich innerhalb eines Timers liegt ===
				rec=0
				rec=beginTime and self.timer.isInTimer(eventId, beginTime, duration, refstr)
				if not rec:
					typ=0
					#return width_faktor, banner_width, pos, typ
				
				if begTimer <= beginTime and endTimer >= endTime:
					pos=0
					if not x.justplay:
						typ=2
					else:
						typ=6
					#return width_faktor, banner_width, pos, typ
				
				if beginTime > begTimer and beginTime < endTimer and endTime > endTimer:
					pos=0
					if not x.justplay:
						typ=2
					else:
						typ=6
					width_faktor = (endTimer - beginTime) / float(duration)
					banner_width = (endTimer - beginTime) / float(end - start) * width
					#=== width_faktor = Faktor als Anteil, pos = 0 (links) oder 1 (rechts)
					#if (endTimer - beginTime) !=300:
					#print "== getBanner Ergebnis-links: ", banner_width, pos, eventName, (endTimer - beginTime), endTimer, beginTime, duration
					#return width_faktor, banner_width, pos, typ
				elif beginTime < begTimer and endTime > begTimer and endTime < endTimer:
					#== falls event vorher schon als PreTimer gefunden, dann auch als PostTimer
					if typ ==2 or typ==6 and pos==0:
						banner_width2 = banner_width
						#print "== getBanner Ergebnis2-links: ", banner_width, pos, eventName
					pos=1
					if not x.justplay:
						typ=2
					else:
						typ=6
					width_faktor = (endTime - begTimer) / float(duration)
					# pos = 3
					banner_width = (endTime - begTimer) / float(end - start) * width
		
		return width_faktor, banner_width, pos, typ, pos_left, banner_width2
		

	def queryEPG(self, list, buildFunc=None):
		if self.epgcache is not None:
			if buildFunc is not None:
				return self.epgcache.lookupEvent(list, buildFunc)
			else:
				return self.epgcache.lookupEvent(list)
		return [ ]

	def getEventRect(self):
		rc = self.event_rect
		return Rect( rc.left() + (self.instance and self.instance.position().x() or 0), rc.top(), rc.width(), rc.height() )

	def getTimeEpoch(self):
		return self.time_epoch

	def getTimeBase(self):
		return self.time_base + (self.offs * self.time_epoch * 60)

	def resetOffset(self):
		self.offs = 0
	
	def getClockPixmap(self, refstr, beginTime, duration, eventId):
		pre_clock = 1
		post_clock = 2
		clock_type = 0
		endTime = beginTime + duration
		for x in self.timer.timer_list:
			if x.service_ref.ref.toString() == refstr:
				if x.eit == eventId:
					return 2, self.clock_pixmap
				beg = x.begin
				end = x.end
				#print "=== timer", x.name
				if beginTime > beg and beginTime < end and endTime > end:
					clock_type |= pre_clock
				elif beginTime < beg and endTime > beg and endTime < end:
					clock_type |= post_clock
		#print "=== clocktype", clock_type
		if clock_type == 0:
			return 0, self.clock_add_pixmap
		elif clock_type == pre_clock:
			return 3, self.clock_pre_pixmap
		elif clock_type == post_clock:
			return 1, self.clock_post_pixmap
		else:
			return 4, self.clock_prepost_pixmap
			
			

	# def getServicePixmap(self, service):
			# serviceref = ServiceReference(service)
			# refstr = serviceref.ref.toString()
			# refstr_txt="_".join(refstr.split(":",10)[:10])
			# if refstr_txt[:4]=="4097": #bei IP-TV den TV-Ref verwenden
				# refstr_txt = "1" + refstr_txt[4:]
			# #print "MEPG_VM: " + refstr
			# #print "MEPG_VM: " + refstr_txt
			# #pic_path = "/data/picon_miniorg/" + refstr_txt + ".png"
			# pic_path = config.plugins.multiepgmv.picon_path.value + "/" + refstr_txt + ".png"
			# #return pic_path
			# self.service_pixmap = LoadPixmap(cached=True, path=pic_path)
			# #self.service_pixmap = loadPNG(pic_path)
			# return self.service_pixmap


########################################################################################

class TimelineText(HTMLComponent, GUIComponent):
	def __init__(self):
		GUIComponent.__init__(self)
		self.l = eListboxPythonMultiContent()
		self.l.setSelectionClip(eRect(0,0,0,0))
		if sz_w == 1920:
			self.itemHeight =40
			self.l.setFont(0, gFont("Regular", 26))
		else:
			self.itemHeight =25
			self.l.setFont(0, gFont("Regular", 20))
		self.l.setItemHeight(self.itemHeight);

	GUI_WIDGET = eListbox

	def postWidgetCreate(self, instance):
		instance.setContent(self.l)

	def setEntries(self, entries):
		res = [ None ] # no private data needed
		for x in entries:
			tm = x[0]
			xpos = x[1]
			str = strftime("%H:%M", localtime(tm))
			#print "== Zeit: ", str, xpos
			res.append((eListboxPythonMultiContent.TYPE_TEXT, xpos-20, 0, 70, self.itemHeight, 0, RT_HALIGN_CENTER|RT_VALIGN_CENTER, str))
		self.l.setList([res])


########################################################################################

class MultiEPG_MV(Screen, HelpableScreen):
	EMPTY = 0
	ADD_TIMER = 1
	REMOVE_TIMER = 2
	ENABLE_TIMER = 3
	ZAP = 1
	
	if sz_w == 1920:
		skin = """
		<screen name="MultiEPG_MV_New" position="center,center" size="1920,1080" title="MultiEPG Vali-Mod" flags="wfNoBorder" >
			<widget name="channel_txt" position="10,15" size="1900,40" font="Regular;32" foregroundColor="#fcc000" transparent="1" />		
			<widget name="bouquet_txt" position="10,15" size="1900,40" font="Regular;32" halign="center" transparent="1" />					
			<widget source="global.CurrentTime" render="Label" position="10,15" size="1900,40" font="Regular;32" halign="right" transparent="1" >
				<convert type="ClockToText">Format:%A %e. %B  %-H:%M</convert>
			</widget>
			<ePixmap pixmap="skin_default/buttons/red.png" position="10,1005" size="295,70" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="305,1005" size="295,70" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="600,1005" size="295,70" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="895,1005" size="295,70" alphatest="on" />
			<widget name="key_red" position="10,1005" size="295,70" font="Regular;30" halign="center" valign="center" backgroundColor="#9f1313" shadowColor="#000000" shadowOffset="-3,-3" zPosition="1" transparent="1" />
			<widget name="key_green" position="305,1005" size="295,70" font="Regular;30" halign="center" valign="center" backgroundColor="#1f771f" shadowColor="#000000" shadowOffset="-3,-3" zPosition="1" transparent="1" />
			<widget name="key_yellow" position="600,1005" size="295,70" font="Regular;30" halign="center" valign="center" backgroundColor="#a08500" shadowColor="#000000" shadowOffset="-3,-3" zPosition="1" transparent="1" />
			<widget name="key_blue" position="895,1005" size="295,70" font="Regular;30" halign="center" valign="center" backgroundColor="#18188b" shadowColor="#000000" shadowOffset="-3,-3" zPosition="1" transparent="1" />
			<ePixmap pixmap="skin_default/buttons/key_info.png" position="1260,1015" size="100,50" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/key_menu.png" position="1370,1015" size="100,50" alphatest="on" />
			<widget name="timeline_text" position="-10,55" size="1896,45" transparent="1" />
			<widget name="list" position="10,103" size="1900,715" ServiceNameBackgroundColor="#10323c4d" ActiveServiceNameBackgroundColor="#00fcc000" NowBackgroundColor="#1039BA77" PrimetimeBackgroundColor="#000579d4" TimerBackgroundColor="#10c63131" nowTimerBackgroundColor="#10c63131" halfTimerBackgroundColor="#10e26f6f" EntryBackgroundColor="#10515151" EntryForegroundColorSelected="#040404" EntryBackgroundColorSelected="#10f0f0f0" EntryBorderColor="#00555556" scrollbarMode="showNever" />
			<widget name="timeline0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiEPG_MV/timeline.png" position="90,98" size="5,725" zPosition="-2" />
			<widget name="timeline1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiEPG_MV/timeline.png" position="90,98" size="5,725" zPosition="-2" />
			<widget name="timeline2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiEPG_MV/timeline.png" position="90,98" size="5,725" zPosition="-2" />
			<widget name="timeline3" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiEPG_MV/timeline.png" position="90,98" size="5,725" zPosition="-2" />
			<widget name="timeline4" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiEPG_MV/timeline.png" position="90,98" size="5,725" zPosition="-2" />
			<widget name="timeline5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiEPG_MV/timeline.png" position="90,98" size="5,725" zPosition="-2" />
			<widget alphatest="on" name="timeline_now" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiEPG_MV/timeline-now.png" position="90,95" size="30,730" zPosition="2" />
			<eLabel backgroundColor="#00555556" position="8,830" size="1910,2" zPosition="1" />
			<widget source="Event" render="Label" position="10,835" size="1090,35" font="Regular;28" noWrap="1" valign="top" foregroundColor="#fcc000" transparent="1" >
				<convert type="EventName">Name</convert>
			</widget>
			<widget source="Event" position="1120,835" size="350,35" render="Label" font="Regular;28" halign="right" valign="top" foregroundColor="#00fcc000" transparent="1" >
				<convert type="EventTime">StartTime</convert>
				<convert type="ClockToText">Format:%A %d. %b.</convert>
			</widget>			
			<widget source="Event" render="Label" position="10,870" size="1090,35" font="Regular;28" noWrap="1" valign="top" transparent="1">
				<convert type="EventName">Description</convert>
			</widget>
			<widget source="Event" render="Label" position="1120,870" size="90,35" font="Regular;28" halign="right" valign="top" foregroundColor="#00fcc000" transparent="1" >
				<convert type="EventTime">StartTime</convert>
				<convert type="ClockToText" />
			</widget>
			<widget source="Event" render="Label" position="1210,870" size="120,35" font="Regular;28" foregroundColor="#00fcc000" transparent="1" >
				<convert type="EventTime">EndTime</convert>
				<convert type="ClockToText">Format: - %H:%M</convert>
			</widget>						
			<widget source="Event" render="Label" position="1120,870" size="350,35" font="Regular;28" halign="right" valign="top" foregroundColor="#00fcc000" transparent="1"  >
				<convert type="EventTime">Remaining</convert>
				<convert type="RemainingToText">InMinutes</convert>
			</widget>			
			<widget source="Event" render="Label" font="Regular;28" position="10,905" size="1470,100" valign="top" transparent="1">
				<convert type="EventName">ExtendedDescription</convert>
			</widget>		
			<eLabel backgroundColor="#ff000000" position="1485,835" size="440,250" zPosition="1" />
			<widget source="session.VideoPicture" render="Pig" position="1502,845" size="403,225" zPosition="3" backgroundColor="#ff000000" />
		</screen>"""
	else:
		skin = """
		<screen name="MultiEPG_MV_New" position="center,center" size="1280,720" title="MultiEPG Vali-Mod" flags="wfNoBorder">
			<widget name="channel_txt" position="5,10" size="1270,30" font="Regular;22" foregroundColor="#fcc000" backgroundColor="background" transparent="1" />		
			<widget name="bouquet_txt" position="5,10" size="1270,30" font="Regular;22" halign="center" backgroundColor="background" transparent="1" />							
			<widget source="global.CurrentTime" position="5,10" size="1270,30" render="Label" font="Regular;22" halign="right" backgroundColor="background" transparent="1" >
				<convert type="ClockToText">Format:%A %e. %B  %-H:%M</convert>
			</widget>
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,680" size="200,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="200,680" size="200,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="400,680" size="200,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="600,680" size="200,40" alphatest="on" />
			<widget name="key_red" position="0,680" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowColor="#000000" shadowOffset="-2,-2" zPosition="1" transparent="1" />
			<widget name="key_green" position="200,680" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowColor="#000000" shadowOffset="-2,-2" zPosition="1" transparent="1" />
			<widget name="key_yellow" position="400,680" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowColor="#000000" shadowOffset="-2,-2" zPosition="1" transparent="1" />
			<widget name="key_blue" position="600,680" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowColor="#000000" shadowOffset="-2,-2" zPosition="1" transparent="1" />
			<ePixmap pixmap="skin_default/buttons/key_info.png" position="845,685" size="60,30" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/key_menu.png" position="915,685" size="60,30" alphatest="on" />
			<widget name="timeline_text" position="-15,40" size="1250,30" transparent="1" />
			<widget name="list" position="5,72" size="1270,468" ServiceNameBackgroundColor="#10323c4d" ActiveServiceNameBackgroundColor="#00fcc000" NowBackgroundColor="#1039BA77" PrimetimeBackgroundColor="#000579d4" TimerBackgroundColor="#10c63131" nowTimerBackgroundColor="#10c63131" halfTimerBackgroundColor="#10e26f6f" EntryBackgroundColor="#10515151" EntryForegroundColorSelected="#040404" EntryBackgroundColorSelected="#10f0f0f0" EntryBorderColor="#00555556" scrollbarMode="showNever" />
			<widget name="timeline0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiEPG_MV/timeline.png" position="60,67" size="2,478" zPosition="-2" />
			<widget name="timeline1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiEPG_MV/timeline.png" position="60,67" size="2,478" zPosition="-2" />
			<widget name="timeline2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiEPG_MV/timeline.png" position="60,67" size="2,478" zPosition="-2" />
			<widget name="timeline3" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiEPG_MV/timeline.png" position="60,67" size="2,478" zPosition="-2" />
			<widget name="timeline4" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiEPG_MV/timeline.png" position="60,67" size="2,478" zPosition="-2" />
			<widget name="timeline5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiEPG_MV/timeline.png" position="60,67" size="2,478" zPosition="-2" />
			<widget name="timeline_now" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiEPG_MV/timeline-now.png" position="60,65" size="19,484" zPosition="2" alphatest="on" />
			<eLabel backgroundColor="#00555556" position="5,550" size="1275,1" zPosition="1" />
			<widget source="Event" render="Label" position="5,555" size="720,25" font="Regular;19" noWrap="1" valign="top" foregroundColor="#fcc000" transparent="1" >
				<convert type="EventName">Name</convert>
			</widget>
			<widget source="Event" position="735,555" size="240,25" render="Label" font="Regular;19" halign="right" valign="top" foregroundColor="#00fcc000" transparent="1" >
				<convert type="EventTime">StartTime</convert>
				<convert type="ClockToText">Format:%A %d. %b.</convert>
			</widget>
			<widget source="Event" render="Label" position="5,583" size="720,25" font="Regular;19" noWrap="1" valign="top" backgroundColor="background" transparent="1" >
				<convert type="EventName">Description</convert>
			</widget>
			<widget source="Event" render="Label" position="735,583" size="65,25" font="Regular;19" halign="right" valign="top" foregroundColor="#00fcc000" transparent="1" >
				<convert type="EventTime">StartTime</convert>
				<convert type="ClockToText" />
			</widget>
			<widget source="Event" render="Label" position="800,583" size="100,25" font="Regular;19" foregroundColor="#00fcc000" transparent="1" >
				<convert type="EventTime">EndTime</convert>
				<convert type="ClockToText">Format: - %H:%M</convert>
			</widget>			
			<widget source="Event" render="Label" position="735,583" size="240,25" font="Regular;19" halign="right" valign="top" foregroundColor="#00fcc000" transparent="1"  >
				<convert type="EventTime">Remaining</convert>
				<convert type="RemainingToText">InMinutes</convert>
			</widget>			
			<widget source="Event" render="Label" font="Regular;19" position="5,610" size="970,68" valign="top" transparent="1">
				<convert type="EventName">ExtendedDescription</convert>
			</widget>			
			<eLabel backgroundColor="#ff000000" position="981,551" size="299,169" zPosition="1" />
			<widget source="session.VideoPicture" render="Pig" position="993,557" size="277,156" zPosition="3" backgroundColor="#ff000000" />
		</screen>"""

	def __init__(self, session, services, zapFunc=None, bouquetChangeCB=None, serviceChangeCB=None):  #5. Schritt
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		#== Aufruf des Screens von openBouquetEPG() ====
		#print " ============= init MultiEPG_MV (screen) ==============="
		self.bouquetChangeCB = bouquetChangeCB
		self.serviceChangeCB = serviceChangeCB 
		self.skin = MultiEPG_MV.skin
		self.skinName = "MultiEPG_MV_New"
		now = time()
		tmp = now % 900
		#== entweder <widget name="Video".../> im Skin oder <widget source="session.VideoPicture" render="Pig" /> ===
		#desktopSize = getDesktop(0).size()
		#self["Video"] = VideoWindow(decoder = 0, fb_width=desktopSize.width(), fb_height=desktopSize.height())
		self.ask_time = now - tmp
		self.closeRecursive = False
		self["channel_txt"] = Label("")
		self["bouquet_txt"] = Label("")
		self["key_red"] = Label("")
		self["key_green"] = Label("")
		self["key_yellow"] = Label("")
		self["key_blue"] = Label(_("PrimeTime"))
		self.key_green_choice = self.EMPTY
		self.key_red_choice = self.EMPTY
		self.key_yellow_choice = self.EMPTY
		self.key_blue_choice = self.goPrimeTime
		self.PrimeTime=0
		self["timeline_text"] = TimelineText()
		self["Event"] = Event()
		self.time_lines = [ ]
		for x in (0,1,2,3,4,5):
			pm = Pixmap()
			self.time_lines.append(pm)
			self["timeline%d"%(x)] = pm
		self["timeline_now"] = Pixmap()
		self.services = services
		self.zapFunc = zapFunc
		self.listheightorg = None
		self.moved=None

		#== 6. Schritt ====
		#print " === MEPGMV set EPGList ==============="
		self["list"] = EPGList(self.session, selChangedCB = self.onSelectionChanged, timer = self.session.nav.RecordTimer, time_epoch = int(config.plugins.multiepgmv.time_period.value) )

		self["actions0"] = HelpableActionMap(self, "OkCancelActions",
			{
				"cancel": (self.closeScreen, _("Exit plugin")), 
				"ok":     (self.eventSelected, _("Zap and Exit plugin")),
			}, -1)

		self["actions1"] = HelpableActionMap(self, "WizardActions",
			{
				"up":     (self.ChannelUp,_("Next Channel")),
				"down":   (self.ChannelDown,_("Previous Channel")),
				"left":   (self.leftPressed, _("Previous entry")),
				"right":  (self.rightPressed, _("Next entry")),
			}, -1)

		self["actions2"] = HelpableActionMap(self, "QuickButtonActions",
			{
				"green":         (self.timerAdd, _("Add/Remove/Enable timer")),
				"yellow":        (self.timerEdit, _("Edit Timer")),
				"red":           (self.zapTo, _("Zap")),
				"blue":          (self.goPrimeTime, _("PrimeTime")),
				"green_long":    (self.addAutoTimer, _("Add Autotimer")),
				"text":          (self.openSPInfoScreen, _("Open SeriesPlugin InfoScreen")),
				"pvr":           (self.searchEPG, _("Search EPG") + _(" - jump to next event")),
				"radio":         (self.openTimerList, _("Open Timerlist")),
				"instantRecord": (self.instantRecord, _("Add timer") + " / " + _("Remove timer")),
				"info":          (self.infoKeyPressed, _("EventView")),
				"menu":          (self.openSetup, _("Open Setup")),
			}, -1)

		self["actions7"] = HelpableActionMap(self, "InfobarAudioSelectionActions",
			{
				"audioSelection":  (self.searchEPGmsg, _("Search EPG")),
			}, -1)

		self["actions6"] = HelpableActionMap(self, "MediaPlayerActions",
			{
				"stop":  (self.timerEnableDisable, _("Enable timer") + " / " + _("Disable timer")),
				"pause": (self.playPressed, _("enable move mode")), 
			}, -1)

		self["actions3"] = HelpableActionMap(self, "EPGSelectActions",
			{
				"nextBouquet": (self.nextBouquet, _("Next bouquet")),
				"prevBouquet": (self.prevBouquet, _("Previous bouquet")),
				"nextService": (self.goPageRight, _("Next Day")),
				"prevService": (self.goPageLeft, _("Previous Day")),
			}, -1)

		self["actions4"] = HelpableActionMap(self, "InfobarActions",
			{
				'showTv':      (self.showTrailer, _("Open Youtube Trailer")),
			}, -1)

		#self["actions5"] = HelpableActionMap(self, "InfobarInstantRecord",
		#	{
		#		'instantRecord': (self.instantRecord, _("Add timer") + " / " + _("Remove timer")),
		#	}, -1)

		self["input_actions"] = HelpableActionMap(self, "InputActions",
			{
				"1":      (self.key1, _("Show less entries")),
				"2":      (self.key2, _("Show normal entries")),
				"3":      (self.key3, _("Show more entries")),
				"4":      (self.key4, _("Show most more entries")),
				"5":      (self.key5, _("Show mostest more entries")),
				'8':      (self.goPageUp, _("Page up")),
				'0':      (self.goPageDown, _("Page down")),
				'7':      (self.key7, _("Previous Page")),
				'9':      (self.key9, _("Next Page")),
			},-1)

		self.updateTimelineTimer = eTimer()
		self.updateTimelineTimer_conn = self.updateTimelineTimer.timeout.connect(self.moveTimeLines)
		self.updateTimelineTimer.start(60*1000, True)
		self.onLayoutFinish.append(self.onCreate)
		
		try:
			self.volctrl = eDVBVolumecontrol.getInstance() # volume control # dirty
		except:
			#print "eDVBVolumecontrol.getInstance() failed"
			self.volctrl = None
		self.preMute_muteState = None
		
		#set redkey to multiple action from WHERE_..._RED/BLUE-Key
		if config.plugins.multiepgmv.useMoreKey.value and hasattr(PluginDescriptor, "WHERE_CHANNEL_SELECTION_RED"):
			actions = self["actions2"].actions
			del actions['red'] #delete redKeyFunction
			self._pluginList = []
			self._checkPlugins()
			self["redKeyActions"] = HelpableActionMap(self, "QuickButtonActions",
			{
				"red":        (self._openPlugins, _("More ...")),
			}, -1)

	def _checkPlugins(self):
		self._pluginList.append((_("Zap"), self.zapTo, True))
		for p in plugins.getPlugins(where = [PluginDescriptor.WHERE_CHANNEL_SELECTION_RED,PluginDescriptor.WHERE_EVENTVIEW, PluginDescriptor.WHERE_EPG_SELECTION_SINGLE_RED, PluginDescriptor.WHERE_EPG_SELECTION_SINGLE_BLUE]):
			if (p.name, p, False) not in self._pluginList and "/MultiEPG_MV" not in p.path:
				self._pluginList.append((p.name, p, False))
		if self._pluginList:
			if len(self._pluginList) > 1:
				self["key_red"].setText(_("More ..."))
			else:
				self["key_red"].setText(self._pluginList[0][0])
		else:
			self["key_red"].setText("")

	def _openPlugins(self):
		if self._pluginList:
			if len(self._pluginList) > 1:
				self.session.openWithCallback(self._onPluginSelected, ChoiceBox, list=self._pluginList, windowTitle=_("More ..."))
			else:
				self._onPluginSelected(self._pluginList[0])

	def _onPluginSelected(self, p=None):
		noargs = p and p[2]
		fnc = p and p[1]
		if not fnc:
			return
		if noargs: #noarg for multiepgcallback backwards compat
			fnc()
			return
		
		serviceref = self["list"].cur_service[0]
		event = self["Event"].event
		service = ServiceReference(serviceref)
		
		if not event:
			self.session.toastManager.showToast(_("This feature requires valid EPG!"))
			return
		fnc(self.session, event, service)

	def openSetup(self):
		reload(MultiEPGSetup)
		from MultiEPGSetup import MultiEPGSetup as MEPGSetup
		self.session.openWithCallback(self.onCloseSetup, MEPGSetup)

	def onCloseSetup(self):
		self["list"].setEpoch(int(config.plugins.multiepgmv.time_period.value))
		
		fontsizeoffset = int(config.plugins.multiepgmv.fontsizeoffset.value)
		if sz_w == 1920:
			self["list"].l.setFont(0, gFont("Regular", 26 + fontsizeoffset))
			self["list"].l.setFont(1, gFont("Regular", 26 + fontsizeoffset))
			Testfont = gFont("Regular", 25 + fontsizeoffset)
		else:
			self["list"].l.setFont(0, gFont("Regular", 20 + fontsizeoffset))
			self["list"].l.setFont(1, gFont("Regular", 20 + fontsizeoffset))
			Testfont = gFont("Regular", 19 + fontsizeoffset)
		self["list"].Alphasize = Testfont.pointSize
		
		# cur = self["list"].getCurrent()
		# eventId = None
		# if cur[0]:
			# cur_event = cur[0]
			# eventId = cur_event.getEventId()
			# print "=== eventId", eventId, self["list"].instance.getCurrentIndex()
			
		self.onCreate()
		# if eventId: 
			# self["list"].moveToEventId(eventId)
		# self["list"].setCurrentIndex(200)
		#self.updateList()
		#self["list"].fillMultiEPG(self.services, self.ask_time)
		#self.moveTimeLines()

	def playPressed(self):
		print "MOVING ..."
	        ch = self.instance.csize().height()
	        cw = self.instance.csize().width()
		if self.moved is None:
		    	# get current skin position, width and height  ...
		        x = self.instance.position().x()
		        y = self.instance.position().y()
		        pw = self.instance.size().width()
		        ph = self.instance.size().height()
		    	# get video skin position, width and height  ...
#			from Components.VideoWindow import VideoWindow
#			self["Video"] = VideoWindow(decoder = 0, fb_width=sz_w, fb_height=sz_h)
#	        	vh = self["Video"].csize().height()   
#	       		vw = self["Video"].csize().width()                              
#	        	vx = self["Video"].csize().x()                              
#	        	vy = self["Video"].csize().y()                              
#			print "VIDEO", vx,vy,vw,vh
			decw=pw-cw
			dech=ph-ch
			self.y=y+dech/2
			if sz_w == 1920:
				self.x=100
			else:
				self.x=70
			if cw==pw:
				self.x=x+decw/2
			self.moved=False
		if self.moved:
			nx=self.x
			ny=self.y
			self.moved=False
		else:
			ny=self.y
			nx=int(config.plugins.multiepgmv.hidePosition.value)
			print "FULL SCREEN"                 
			if os.path.exists("/proc/stb/vmpeg/0"):       
				l=open("/proc/stb/vmpeg/0/dst_left","w")       
				l.write("%x" % 0)                              
				l.close()                                 
				t=open("/proc/stb/vmpeg/0/dst_top","w")       
				t.write("%x" % 0)                              
				t.close()                                 
				h=open("/proc/stb/vmpeg/0/dst_height","w")
				h.write("%x" % 576)                       
				h.close()                                 
				w=open("/proc/stb/vmpeg/0/dst_width","w") 
				w.write("%x" % 720)                       
				w.close()                 
			self.moved=True
		print "MOVING TO %i,%i" % (nx,ny)
		self.instance.move(ePoint(nx,ny))

	#EPG-Suche in EPGSearch oder eigener EPG-Trefferliste oeffnen
	def searchEPGmsg(self):
		#alter Aufruf fuer die Messagebox mit Treffern
		#self.searchEPG(True)
		#return
		
		#Aufruf der EPG-Suche im EPGSearch (falls installiert)
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/EPGSearch"):
			from Plugins.Extensions.EPGSearch.EPGSearch import EPGSearch
			cur = self["list"].getCurrent()
			eventname = cur[0].getEventName()
			self.session.open(EPGSearch, eventname)
			return
		
		#alternativer Aufruf der EPG-Suche in eigener EPG-Trefferliste (falls EPGSearch nicht installiert ist)
		cur = self["list"].getCurrent()
		cur_event = cur[0]
		eventname = cur_event.getEventName()
		
		epgcache = eEPGCache.getInstance()
		ret = epgcache.search(('RIBDT',	500, eEPGCache.PARTIAL_TITLE_SEARCH, eventname, eEPGCache.NO_CASE_CHECK)) or []
		ret.sort(key=lambda x: x[2])
		
		cur_service = cur[1]
		event1 = parseEvent(cur_event)
		found_events = []
		services = getServiceList('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.hd__tv_.tv" ORDER BY bouquet')
		
		for event in ret:
			#print "== event", event
			if str(event[0]) in services and int(event[2])>= int(event1[0]):
				#print "==== Kanal gefunden", str(event[0])
				
				msgtxt_event = ""
				channel_txt = ""
				epgEvent = epgcache.lookupEventId(eServiceReference(event[0]), int(event[1]))
				if epgEvent:
					msgtxt_event += str(epgEvent.getShortDescription())
					if len(msgtxt_event)>64:
						msgtxt_event = msgtxt_event[:61] + "..."
					if str(event[0]) != str(cur_service):
						channel_txt = ServiceReference(event[0]).getServiceName() + ": "
					if len(msgtxt_event):
						event_lst = list(event)
						event_lst[4] = channel_txt + event_lst[4] + "  |  " + msgtxt_event
						event = tuple(event_lst)
				
				found_events.append(event)
		
		if len(found_events)>1:
			self.session.open(MultiEPGmvEPGSelection, cur_service.ref, None, cur_event, found_events)
		else:
			self.session.open(MessageBox,"Keine weitere Sendung zu '" + eventname + "' gefunden!", MessageBox.TYPE_INFO,3)

	#EPG-Suche als Messagebox anzeigen oder im MultiEPG zum naechsten Treffer springen
	def searchEPG(self, msg=False):
		
		cur = self["list"].getCurrent()
		cur_event = cur[0]
		if cur_event == None:
			return
		
		eventname = cur_event.getEventName()
		cur_service = cur[1]

		event1 = parseEvent(cur_event)
		eventname = cur_event.getEventName()
		
		found_events = set()
		events = self["list"].cur_service[2]
		event1 = events[self["list"].cur_event]
		
		#print "Service: ",cur_service
		#print "event: ", eventname
		#print "eventid: ", int(event1[0])
		#pprint (event1)
		
		epgcache = eEPGCache.getInstance()
		ret = epgcache.search(('RIBDT',
					500,
					eEPGCache.PARTIAL_TITLE_SEARCH,
					eventname,
					eEPGCache.NO_CASE_CHECK)) or []
		ret.sort(key=lambda x: x[2])
		
		for event in ret:
			#print "ref: ", event[1], datetime.fromtimestamp(int(event[2])).strftime('%d.%m.%y %H:%M:%S'), int(event[2]), int(event1[2])
			if str(event[0]) == str(cur_service) and int(event[1]) != int(event1[0]) and int(event[2])> int(event1[2]):
				#print "ref1: ", event[1], datetime.fromtimestamp(int(event[2])).strftime('%d.%m.%y %H:%M:%S'), int(event[2]), int(event1[2]), event[1]
				found_events.add(event)
		
		#Ausgabe aller Treffer als Messagebox
		if msg:
			msgtxt = "Es gibt " + str(len(found_events)) + " EPG-Treffer zu '" + eventname + "':\n"
			#msgtxt = "Es wurden Folgende EPG-Entries wurden gefunden:\n"
			for event in sorted(found_events, key=lambda x: x[2]):
				msgtxt_event = "\n" + datetime.fromtimestamp(int(event[2])).strftime('%a %d.%m. %H:%M') + "  " + event[4]
				epgEvent = epgcache.lookupEventId(eServiceReference(event[0]), int(event[1]))
				if epgEvent:
					msgtxt_event += "  (" + str(epgEvent.getShortDescription()) + ")"
				
				if len(msgtxt_event)>64:
					msgtxt_event = msgtxt_event[:61] + "...)"
				
				msgtxt += msgtxt_event
				
			if len(found_events):
				self.session.open(MessageBox,msgtxt, MessageBox.TYPE_INFO)
		
		#Springe zum naechsten Treffer im MultiEPG
		else:
			#pprint (found_events)
			for event in sorted(found_events, key=lambda x: x[2]):
				#print "Treffer: ", event[2], event[4], datetime.fromtimestamp(int(event[2])).strftime('%d.%m.%y %H:%M:%S'), event[1]
				#print "EventTime: ", event1[2], datetime.fromtimestamp(int(event1[2])).strftime('%d.%m.%y %H:%M:%S')

				self.ask_time = int(event[2])
				self.PrimeTime=1
				self["key_blue"].setText(_("Now"))
				l = self["list"]
				l.resetOffset()
				l.cur_event = 0
				l.fillMultiEPG(self.services, self.ask_time)
				self.moveTimeLines(True)
				
				return
		
		if len(found_events) == 0:
			self.session.open(MessageBox,"Keine Sendung zu '" + eventname + "' gefunden!", MessageBox.TYPE_INFO)
		#pprint (ret)
		return

	def onCreate(self):   # 8.Schritt
		#print "=== MEPGMV onCreate  =========================", self.session.nav.getCurrentlyPlayingServiceReference()
		#print "=== MEPGMV onCreate  ========================="
		self.opentime_multiepg = time()
		self.recalcItemHeight() #recalc itemheigt to use rowoffset from setup
		self["list"].fillMultiEPG(self.services, self.ask_time) #ask_time = startzeit
		self["list"].moveToService(self.session.nav.getCurrentlyPlayingServiceReference())
		self.moveTimeLines()

	def recalcItemHeight(self):
		#recalc itemheigt to use rowoffset from setup
		restheight = 0
		if not self.listheightorg:
			self.listheightorg = self["list"].instance.size().height()
		listheight = self.listheightorg
		itemheight = self["list"].itemheightorg
		rowsorg = listheight / itemheight
		rows = listheight / itemheight + int(config.plugins.multiepgmv.rowoffset.value)
		newitemheight = listheight / rows
		restheight = listheight % newitemheight
		self["list"].l.setItemHeight(newitemheight)
		self["list"].instance.resize(eSize(*(self["list"].instance.size().width(),self.listheightorg - restheight)))

	def updateList(self):
		self['list'].l.invalidate()

	def initPig(self):
		#print "MEPG_VM: InitPig"
		self["Video"].show()
		self.miniTV_resume(True)
		self["bouquet_txt"].setText(bouquet_name)

	def volumeMute(self):
		if self.volctrl is not None:
			self.volctrl.volumeMute()

	def volumeUnMute(self):
		if self.volctrl is not None:
			self.volctrl.volumeUnMute()

	def miniTV_unmute(self):
		if self.preMute_muteState is not None:
			if not self.preMute_muteState:
				self.volumeUnMute()
			self.preMute_muteState = None

	def miniTV_resume(self,calledFromInitPig):
		if self.lastservice and not self.hide_miniTV:
			self.session.nav.playService(self.lastservice)
			if calledFromInitPig:
				self.lastservice = None
			else:
				self["Video"].show()
			self.miniTV_unmute()

	def goPageUp(self):
			self['list'].instance.moveSelection(self['list'].instance.pageUp)

	def goPageDown(self):
			self['list'].instance.moveSelection(self['list'].instance.pageDown)

	def goPageRight(self):
		#self.ask_time = self.ask_time + (60*60*24)
		l = self['list']
		time_base = l.getTimeBase()
		self.ask_time = time_base + (60*60*24)
		l.resetOffset()
		l.fillMultiEPG(self.services, self.ask_time)
		self.moveTimeLines(True)

	def goPageLeft(self):
		l = self['list']
		time_base = l.getTimeBase()
		#self.ask_time = self.ask_time - (60*60*24)
		self.ask_time = time_base - (60*60*24)
		if self.ask_time < time():
			self.go2now()
		else:	
			l.resetOffset()
			l.fillMultiEPG(self.services, self.ask_time)
			self.moveTimeLines(True)

	def leftPressed(self):
		if self.moved:
			ny=self.y
			nx=int(config.plugins.multiepgmv.hidePosition.value)-5
			if nx < 0:
				nx=0
			config.plugins.multiepgmv.hidePosition.value=nx
			config.plugins.multiepgmv.hidePosition.save()
			print "MOVING TO %i,%i" % (nx,ny)
			self.instance.move(ePoint(nx,ny))
		else:
			self.prevEvent()

	def rightPressed(self):
		if self.moved:
			ny=self.y
			nx=int(config.plugins.multiepgmv.hidePosition.value)+5
			if nx > sz_w:
				nx=sz_w
			config.plugins.multiepgmv.hidePosition.value=nx
			config.plugins.multiepgmv.hidePosition.save()
			print "MOVING TO %i,%i" % (nx,ny)
			self.instance.move(ePoint(nx,ny))
		else:
			self.nextEvent()

	def nextEvent(self, visible=True):
		ret = self["list"].selEntry(+1, visible)
		if ret:
			self.moveTimeLines(True)

	def prevEvent(self, visible=True):
		ret = self["list"].selEntry(-1, visible)
		if ret:
			self.moveTimeLines(True)

	def key1(self):
		self["list"].setEpoch(60)
		config.plugins.multiepgmv.time_period.value = 60
		self.moveTimeLines()

	def key2(self):
		self["list"].setEpoch(120)
		config.plugins.multiepgmv.time_period.value = 120
		self.moveTimeLines()

	def key3(self):
		self["list"].setEpoch(180)
		config.plugins.multiepgmv.time_period.value = 180
		self.moveTimeLines()

	def key4(self):
		self["list"].setEpoch(240)
		config.plugins.multiepgmv.time_period.value = 240
		self.moveTimeLines()

	def key5(self):
		self["list"].setEpoch(300)
		config.plugins.multiepgmv.time_period.value = 300
		self.moveTimeLines()

	def key7(self):
		l = self["list"]
		jump = l.getTimeBase() - (l.getTimeEpoch()*60)
		if self.ask_time > jump:
			now = time()
			tmp = now % 900
			self.ask_time = now - tmp
			jump = self.ask_time
		l.resetOffset()
		l.fillMultiEPG(self.services, jump)
		self.moveTimeLines(True)

	def key9(self):
		l = self["list"]
		jump = l.getTimeBase() + (l.getTimeEpoch()*60)
		l.resetOffset()
		l.fillMultiEPG(self.services, jump)
		self.moveTimeLines(True)

	def ChannelDown(self):
		#print "== Channeldown"
		self["list"].instance.moveSelection(self["list"].instance.moveDown)
		self.moveTimeLines()
		if self.moved:
			self.zapTo()

	def ChannelUp(self):
		#print "== Channelup"
		self["list"].instance.moveSelection(self["list"].instance.moveUp)
		self.moveTimeLines()
		if self.moved:
			self.zapTo()

	def nextBouquet(self):
		if self.bouquetChangeCB:
			self.ask_time = self["list"].getTimeBase()
			self.bouquetChangeCB(1, self)
			self["list"].resetOffset()
			self["list"].fillMultiEPG(self.services, self.ask_time)
			self.moveTimeLines(True)

	def prevBouquet(self):
		if self.bouquetChangeCB:
			self.ask_time = self["list"].getTimeBase()
			self.bouquetChangeCB(-1, self)
			self["list"].resetOffset()
			self["list"].fillMultiEPG(self.services, self.ask_time)
			self.moveTimeLines(True)

	def openTimerList(self):
		from Screens.TimerEdit import TimerEditList
		self.session.open(TimerEditList)

	def openSPInfoScreen(self):
		
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/SeriesPlugin"):
			#== Aufruf fuer SeriesPlugin-InfoScreen bei Menu-Taste==
			serviceref = self["list"].cur_service[0]
			event = self["Event"].event
			service = ServiceReference(serviceref)
			
			from Plugins.Extensions.SeriesPlugin.SeriesPluginInfoScreen import SeriesPluginInfoScreen
			self.session.open(SeriesPluginInfoScreen, service, event)
		else:
			self.session.open(MessageBox,"Kann die Sendungsinfo nicht abrufen.\nSeriesPlugin ist nicht installiert!", MessageBox.TYPE_INFO)

#	def enterDateTime(self):
#		
#		#== Org-Aufruf fuer enterDateTime bei Menu-Taste==
#		self.session.openWithCallback(self.onDateTimeInputClosed, TimeDateInput, config.mepg_mv_prev_time )

	def goPrimeTime(self):
		#== Umschalten auf PrimeTime 20:15 ===============
		l = self["list"]
		if self.PrimeTime == 0:
			now_time = localtime()
			jahr, monat, tag = now_time[0:3]
			primetime =  [y for y in config.plugins.multiepgmv.prime_time.value]
			primetime_val = jahr, monat, tag, primetime[0], primetime[1], 0, 0, 0, -1
			self.ask_time = mktime(primetime_val)
			self.PrimeTime=1
			self["key_blue"].setText(_("Now"))
			l.resetOffset()
			l.cur_event = None
			l.fillMultiEPG(self.services, self.ask_time)
			self.moveTimeLines(True)
		
		#== zurueck auf aktuelle Zeit==============
		elif self.PrimeTime == 1:
			now_time = time() - (time() % 900) + 60
			self.PrimeTime=0
			self["key_blue"].setText(_("PrimeTime"))
			self.ask_time = now_time
			l.resetOffset()
			l.cur_event = 0
			l.fillMultiEPG(self.services, self.ask_time)
			self.moveTimeLines(True)

			#== aktuelle Sendung auswaehlen ===
			#events = l.cur_service[2]
			#event = events[0]
			#pprint (events)
			#pprint (event)
			#print "eventId: ", int(event[0])
			#l.setCurrentIndex(5)
			
			#serviceref = self["list"].cur_service[0]
			#service = ServiceReference(serviceref)
			#l.moveToService(service)
			#l.moveToEventId( int(event[0]) )

	def onDateTimeInputClosed(self, ret):
		if len(ret) > 1:
			if ret[0]:
				self.ask_time=ret[1]
				l = self["list"]
				l.resetOffset()
				l.fillMultiEPG(self.services, ret[1])
				self.moveTimeLines(True)

	def closeScreen(self, timercheck=True, zap=False):
		#print "== CloseScreen", config.plugins.multiepgmv.timercheck.value
		if config.plugins.multiepgmv.timercheck.value == True and timercheck:
			self.check_Timerlist(zap)
		else:
			self.close(self.closeRecursive, zap)

	def infoKeyPressed(self):
		cur = self["list"].getCurrent()
		event = cur[0]
		service = cur[1]
		if event is not None:
			self.opentime_EventView = time()
			self.session.openWithCallback(self.infoKeyPressedClosed, EventViewEPGSelect, event, service, self.eventViewCallback, self.openSingleServiceEPG, InfoBar.instance.openMultiServiceEPG, self.openSimilarList)
	
	def infoKeyPressedClosed(self, ret=False):
		#print "=== MultiEPG_MV infoKeyPressedClosed"
		#print "=== open MultiEPG_MV", self.opentime_multiepg
		#print "=== open EventView", self.opentime_EventView
		#print "=== open Diff", self.opentime_EventView - self.opentime_multiepg
		if self.opentime_EventView - self.opentime_multiepg < 0.2:
			#close Plugin without timercheck after show eventview bei doublecklick
			self.closeScreen(False)

	def changeServiceCB(self, direction, epg):
		l = self["list"]
		if l.getCurrent():
			if direction > 0:
				self.ChannelDown()
			else:
				self.ChannelUp()
			l = self["list"]
			cur = l.getCurrent()
			epg.setService(cur[1])

	def openSimilarList(self, eventid, refstr):
		self.session.open(EPGSelection, refstr, None, eventid)
		
	def openSingleServiceEPG(self):
		l = self["list"]
		cur = l.getCurrent()
		self.savedService = cur[1].ref
		self.session.openWithCallback(self.SingleServiceEPGClosed, EPGSelection, cur[1].ref, serviceChangeCB=self.changeServiceCB)

	def SingleServiceEPGClosed(self, ret=False):
		#print "== EPG Closed", self.savedService
		l = self['list']
		l.moveToService(self.savedService)

	def setServices(self, services):
		self.services = services
		self.onCreate()

	def eventViewCallback(self, setEvent, setService, val):
		l = self["list"]
		old = l.getCurrent()
		if val == -1:
			self.prevEvent(False)
		elif val == +1:
			self.nextEvent(False)
		cur = l.getCurrent()
		if cur[0] is None and cur[1].ref != old[1].ref:
			self.eventViewCallback(setEvent, setService, val)
		else:
			setService(cur[1])
			setEvent(cur[0])

	def zapTo(self):
		if self.zapFunc and self.key_red_choice == self.ZAP:
			self.closeRecursive = True
			ref = self["list"].getCurrent()[1]
			if ref:
				self.zapFunc(ref.ref)
				self['list'].l.invalidate()
				global current_service_name
				current_service_name = self["list"].cur_service[1]
				#print "============ zapto1: ", current_service_name

	def eventSelected(self):
		#self.infoKeyPressed()
		self.zapTo()
		print "=== OK"
		self.closeScreen(True,True)

	def removeTimer(self, result):
		
		result = result and result[1]
		#print "== removeTimer result: ", result
		timer = self.delete_timer
		
		if result == "exit":
			return
		#nur Timer loeschen =====================
		if result == "delete":
			timer.afterEvent = AFTEREVENT.NONE
			self.session.nav.RecordTimer.removeEntry(timer)
		
		#Timer und Aufnahme loeschen =====================
		elif result == "deleteRecFile":
			timer.afterEvent = AFTEREVENT.NONE
			self.session.nav.RecordTimer.removeEntry(timer)

			#print "== also delete recfile ==="
			from Tools.Directories import SCOPE_HDD
			from enigma import eBackgroundFileEraser
			hdd_path = resolveFilename(SCOPE_HDD)
			servicename = str(timer.service_ref.getServiceName())
			replacestring = '/.\\:*?<>|"'
			filename = ''
			for s in servicename:
				if s in replacestring:
					s = '_'
				filename += s

			timestr = strftime('%Y%m%d %H%M', localtime(timer.begin))
			filename = filename.replace('\xc2\x86', '').replace('\xc2\x87', '')
			filename = timestr + ' - ' + filename
			files = os.listdir(hdd_path)
			for xfile in files:
				if xfile.startswith(filename):
					eBackgroundFileEraser.getInstance().erase(os.path.realpath(hdd_path + xfile))
		#==========================================================================================
		
		self['list'].l.invalidate()
		self["key_green"].setText(_("Add timer"))
		self.key_green_choice = self.ADD_TIMER
		self["key_yellow"].setText(" ")
		self.key_yellow_choice = self.EMPTY
		#self["list"].rebuild() #aus aktuellem org-Plugin

	def timerEdit(self):
		cur = self["list"].getCurrent()
		event = cur[0]
		serviceref = cur[1]
		if event is None:
			return
		eventid = event.getEventId()
		refstr = serviceref.ref.toString()
		for timer in self.session.nav.RecordTimer.timer_list:
			if timer.eit == eventid and timer.service_ref.ref.toString() == refstr:
				self.session.openWithCallback(self.finishedAdd, TimerEntry, timer)
				#self.session.open(TimerEntry, timer)
				break

	def instantRecord(self):
		self.timerAdd()

	def timerAdd(self):
		print "=== MultiEPG_MV org timerAdd"
		cur = self["list"].getCurrent()
		event = cur[0]
		serviceref = cur[1]
		if event is None:
			return
			
		if self.key_green_choice == self.ENABLE_TIMER:
			self.timerEnableDisable()
			return
		
		eventid = event.getEventId()
		refstr = serviceref.ref.toString()
		for timer in self.session.nav.RecordTimer.timer_list:
			if timer.eit == eventid and timer.service_ref.ref.toString() == refstr:
				if timer.begin < time():
					self.delete_timer = timer
					self.session.openWithCallback(self.removeTimer, ChoiceBox, title=_('Remove timer') + (':\n\n%s') % event.getEventName() + " (" + serviceref.getServiceName() + ")", list=[(_('yes') + ', ' + _('Remove timer') + ' + ' + _('Recording'), 'deleteRecFile'), (_('yes') + ', ' + _("Remove timer"), 'delete'), (_('Abort'), 'exit'), ])
				else:
					self.delete_timer = timer
					cb_func = lambda ret : not ret or self.removeTimer(('Remove Timer','delete'))
					self.session.openWithCallback(cb_func, MessageBox, _("Do you really want to delete %s?") % event.getEventName())
				
				break
		else:
			newEntry = RecordTimerEntry(serviceref, checkOldTimers = True, *parseEvent(event))
			self.session.openWithCallback(self.finishedAdd, TimerEntry, newEntry)

	def finishedAdd(self, answer):
		#print "finished add"
		if answer[0]:
			entry = answer[1]
			simulTimerList = self.session.nav.RecordTimer.record(entry)
			if simulTimerList is not None:
				for x in simulTimerList:
					if x.setAutoincreaseEnd(entry):
						self.session.nav.RecordTimer.timeChanged(x)
				simulTimerList = self.session.nav.RecordTimer.record(entry)
				if simulTimerList is not None:
					self.session.openWithCallback(self.finishSanityCorrection, TimerSanityConflict, simulTimerList)
			self["key_green"].setText(_("Remove timer"))
			self.key_green_choice = self.REMOVE_TIMER
			self["key_yellow"].setText(_("Edit Timer"))
			self.key_yellow_choice = self.timerEdit
		else:
			if self.key_yellow_choice != self.timerEdit:
				self["key_green"].setText(_("Add timer"))
				self.key_green_choice = self.ADD_TIMER
			#print "Timeredit aborted"
	
	def finishSanityCorrection(self, answer):
		self.finishedAdd(answer)

	def instantToggleTimerState(self):
		self.timerEnableDisable(True)

	def timerEnableDisable(self, instant_toggle = False):
		cur = self["list"].getCurrent()
		event = cur[0]
		serviceref = cur[1]
		if event is None:
			return
		eventid = event.getEventId()
		refstr = serviceref.ref.toString()
		for timer in self.session.nav.RecordTimer.timer_list:
			if timer.eit == eventid and timer.service_ref.ref.toString() == refstr:
				if instant_toggle:
					self.toggleTimerState(timer, True)
				else:
					cb_func = lambda ret : not ret or self.toggleTimerState(timer, True)
					self.session.openWithCallback(cb_func, MessageBox, _("Do you really want to disable timer:") + "\n" + event.getEventName() + " ?")
				return
		for timer in self.session.nav.RecordTimer.processed_timers:
			if timer.eit == eventid and timer.service_ref.ref.toString() == refstr and timer.disabled == True:
				if instant_toggle:
					self.toggleTimerState(timer, False)
				else:
					cb_func = lambda ret : not ret or self.toggleTimerState(timer, False)
					self.session.openWithCallback(cb_func, MessageBox, _("Do you really want to enable timer:") + "\n" + event.getEventName() + " ?")
				return

	def toggleTimerState(self, timer, disableTimer):
		if disableTimer:
			timer.disable()
			self.session.nav.RecordTimer.timeChanged(timer)
			self["key_green"].setText(_("Enable timer"))
			self.key_green_choice = self.ENABLE_TIMER
			self["key_yellow"].setText("")
			self.key_yellow_choice = self.EMPTY
		else:
			timer.enable()
			self["key_green"].setText(_("Remove timer"))
			self.key_green_choice = self.REMOVE_TIMER
			self["key_yellow"].setText(_("Edit Timer"))
			self.key_yellow_choice = self.timerEdit
			timersanitycheck = TimerSanityCheck(self.session.nav.RecordTimer.timer_list, timer)
			#print "==toggleTimerState timer.enable: ", timersanitycheck.check()
			if not timersanitycheck.check():
				#print "==toggleTimerState not timersanitycheck.check()"
				timer.disable()
				self["key_green"].setText("")
				self.key_green_choice = self.EMPTY
				simulTimerList = timersanitycheck.getSimulTimerList()
				if simulTimerList is not None:
					self.session.openWithCallback(self.finishedEdit, TimerSanityConflict, simulTimerList)
			else:
				#print "==toggleTimerState timersanitycheck.check()"
				if timersanitycheck.doubleCheck():
					#print "==toggleTimerState timersanitycheck.doublecheck()"
					timer.disable()
					self["key_green"].setText(_("Remove timer"))
					self.key_green_choice = self.REMOVE_TIMER
			self.session.nav.RecordTimer.timeChanged(timer)
		self.updateList()

	def finishedEdit(self, answer):
		if answer[0]:
			entry = answer[1]
			timersanitycheck = TimerSanityCheck(self.session.nav.RecordTimer.timer_list, entry)
			success = False
			if not timersanitycheck.check():
				simulTimerList = timersanitycheck.getSimulTimerList()
				if simulTimerList is not None:
					for x in simulTimerList:
						if x.setAutoincreaseEnd(entry):
							self.session.nav.RecordTimer.timeChanged(x)
					if not timersanitycheck.check():
						simulTimerList = timersanitycheck.getSimulTimerList()
						if simulTimerList is not None:
							self.session.openWithCallback(self.finishedEdit, TimerSanityConflict, timersanitycheck.getSimulTimerList())
					else:
						success = True
			else:
				success = True
			if success:
				self.session.nav.RecordTimer.timeChanged(entry)
			self.updateList()

#=== Beginn Integration von addAutoTimer ==============================================================
	def addAutoTimer(self):
		cur = self["list"].getCurrent()
		if not cur:
			return
		try:
			from Plugins.Extensions.AutoTimer.AutoTimerEditor import addAutotimerFromEvent
			addAutotimerFromEvent(self.session, evt = cur[0], service = cur[1], importer_Callback = self.own_importerCallback)
		except:
			self.session.open(MessageBox, _('No AutoTimer seems to be installed. Please install it for this functionality.'), MessageBox.TYPE_ERROR)

	def own_importerCallback(self, ret):
		if ret:
			ret, session = ret
			from Plugins.Extensions.AutoTimer.AutoTimerEditor import AutoTimerEditor

			self.session.openWithCallback(
				self.finishedaddAutoTimer,
				AutoTimerEditor,
				ret
			)

	def finishedaddAutoTimer(self, result):
		#print "== result AT: ", result
		if result:
			from Plugins.Extensions.AutoTimer.plugin import autotimer
			autotimer.add(result)

			# Save modified xml
			if config.plugins.autotimer.always_write_config.value:
				autotimer.writeXml()
				
			self.session.openWithCallback(self.openAutotimerPlugin, ChoiceBox, title=_('   Open Autotimer-Plugin ?'), list=[(_('Yes'), 'Yes'), (_('No'), 'No')])

	def openAutotimerPlugin(self, result):
		result = result and result[1]
		if result == 'Yes':
			try:
				from Plugins.Extensions.AutoTimer.plugin import main as AutoTimerPlugin
				AutoTimerPlugin(self.session)
			except:
				self.session.open(MessageBox, _('No AutoTimer seems to be installed. Please install it for this functionality.'), MessageBox.TYPE_ERROR)
#=== Ende Integration von addAutoTimer ==============================================================


	def onSelectionChanged(self):
		#print "=========== onSelectionChanged ==========================="
		cur = self["list"].getCurrent()
		#print "MEPGMV onSelectionChanged - cur: ", cur
		#self["list"].cur_service = self["list"].l.getCurrentSelection()
		#print "MEPGMV onSelectionChanged - cur_service: ", self["list"].cur_service
		global bouquet_name
		from plugin import bouquet_name
		if bouquet_name is None:
			from plugin import epg_bouquet
			serviceHandler = eServiceCenter.getInstance()
			info = serviceHandler.info(epg_bouquet)
			#global bouquet_name
			bouquet_name = info.getName(epg_bouquet)
		
		self["bouquet_txt"].setText(bouquet_name)
		if cur is None:
			#print "=========== onSelectionChanged cur is none==========================="
			if self.key_green_choice != self.EMPTY:
				self["key_green"].setText(" ")
				self.key_green_choice = self.EMPTY
			if self.key_yellow_choice != self.EMPTY:
				self["key_yellow"].setText(" ")
				self.key_yellow_choice = self.EMPTY
			if self.key_red_choice != self.EMPTY:
				self["key_red"].setText(" ")
				self.key_red_choice = self.EMPTY
			return
		
		event = cur[0]
		self["Event"].newEvent(event)
		
		if cur[1] is None or cur[1].getServiceName() == "":
			#print "=========== onSelectionChanged cur1 is none or cur1.getservicename="" ==================="
			if self.key_green_choice != self.EMPTY:
				self["key_green"].setText(" ")
				self.key_green_choice = self.EMPTY
			if self.key_red_choice != self.EMPTY:
				self["key_red"].setText(" ")
				self.key_red_choice = self.EMPTY
			if self.key_yellow_choice != self.EMPTY:
				self["key_yellow"].setText(" ")
				self.key_yellow_choice = self.EMPTY
			return
		elif self.key_red_choice != self.ZAP:
				if config.plugins.multiepgmv.useMoreKey.value and self._pluginList:
					if len(self._pluginList) > 1:
						self["key_red"].setText(_("More ..."))
					else:
						self["key_red"].setText(self._pluginList[0][0])
				else:
					self["key_red"].setText(_("Zap"))
				self.key_red_choice = self.ZAP
			
		if not event:
			#print "=========== onSelectionChanged not event ==========================="
			if self.key_green_choice != self.EMPTY:
				self["key_green"].setText(" ")
				self.key_green_choice = self.EMPTY
			if self.key_yellow_choice != self.EMPTY:
				self["key_yellow"].setText(" ")
				self.key_yellow_choice = self.EMPTY
			return

		#== beim Sendungswechsel den Sendernamen aktualisieren ====
		if cur[1] is None or cur[1].getServiceName() == "":
			self["channel_txt"].setText(" ")
		else:
			self["channel_txt"].setText(cur[1].getServiceName())
		
		serviceref = cur[1]
		eventid = event.getEventId()
		refstr = serviceref.ref.toString()
		isRecordEvent = False
		isDisabled = False
		for timer in self.session.nav.RecordTimer.timer_list:
			if timer.eit == eventid and timer.service_ref.ref.toString() == refstr:
				isRecordEvent = True
				break
		if not isRecordEvent:
			for timer in self.session.nav.RecordTimer.processed_timers:
				if timer.eit == eventid and timer.service_ref.ref.toString() == refstr and timer.disabled == True:
					isDisabled = True
					break
		if isDisabled:
			self["key_green"].setText(_("Enable timer"))
			self.key_green_choice = self.ENABLE_TIMER
		elif isRecordEvent:
			if self.key_green_choice != self.REMOVE_TIMER:
				#print "=========== onSelectionChanged addRemoveTimer-Text  ====================="
				self["key_yellow"].setText(_("Edit Timer"))
				self.key_yellow_choice = self.timerEdit
				self.key_green_choice = self.REMOVE_TIMER
				self["key_green"].setText(_("Remove timer"))
		elif not isRecordEvent:
			if self.key_green_choice != self.ADD_TIMER:
				#print "=========== onSelectionChanged addTimer-Text==========================="
				self["key_yellow"].setText(" ")
				self.key_yellow_choice = self.EMPTY
				self.key_green_choice = self.ADD_TIMER
				self["key_green"].setText(_("Add timer"))


	def moveTimeLines(self, force=False):
		#print " "
		#print "============= moveTimeLines()  ========================="
		#print " "
		self.updateTimelineTimer.start((60-(int(time())%60))*1000)	#keep syncronised
		#print "============= next Timer in: ", (60-(int(time())%60))*1000
		l = self["list"]
		event_rect = l.getEventRect()
		time_epoch = l.getTimeEpoch()
		time_base = l.getTimeBase()
		if event_rect is None or time_epoch is None or time_base is None:
			return
		time_steps = time_epoch > 180 and 60 or 30
		
		num_lines = time_epoch/time_steps
		incWidth=event_rect.width()/num_lines
		pos=event_rect.left()
		timeline_entries = [ ]
		x = 0
		changecount = 0
		for line in self.time_lines:
			old_pos = line.position
			new_pos = (x == num_lines and event_rect.left()+event_rect.width() or pos, old_pos[1])
			if not x or x >= num_lines:
			#== 1. Linie auch anzeigen ==
			#if x >= num_lines:
				line.visible = False
			else:
				if old_pos != new_pos:
					line.setPosition(new_pos[0], new_pos[1])
					changecount += 1
				line.visible = True
			if not x or line.visible:
				timeline_entries.append((time_base + x * time_steps * 60, new_pos[0]))
			x += 1
			pos += incWidth

		if changecount or force:
			self["timeline_text"].setEntries(timeline_entries)

		now=time()
		timeline_now = self["timeline_now"]
		if now >= time_base and now < (time_base + time_epoch * 60):
			xpos = int((((now - time_base) * event_rect.width()) / (time_epoch * 60))-(timeline_now.instance.size().width()/2))
			old_pos = timeline_now.position
			new_pos = (xpos+event_rect.left(), old_pos[1])
			if old_pos != new_pos:
				timeline_now.setPosition(new_pos[0], new_pos[1])
			timeline_now.visible = True
		else:
			timeline_now.visible = False

	def go2now(self):
		now_time = time() - (time() % 900) + 60
		self.ask_time = now_time
		l = self['list']
		l.resetOffset()
		l.fillMultiEPG(self.services, self.ask_time)
		self.moveTimeLines(True)


	def showTrailer(self):
		
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/YTTrailer"):
			l = self["list"]
			events = l.cur_service[2]
			event = events[l.cur_event] #(event_id, event_title, begin_time, duration)
			eventname = event[1]
			#print "== MEPG_MV TV eventname", eventname
			from Plugins.Extensions.YTTrailer.plugin import YTTrailer
			ytTrailer = YTTrailer(self.session)
			ytTrailer.showTrailer(eventname)
		else:
			self.session.open(MessageBox,"Kann keinen Trailer abrufen.\nYTTrailer ist nicht installiert!", MessageBox.TYPE_INFO)


	def check_Timerlist(self, zap=False):
		
		#print "== MultiEPG check_Timerlist"
		self.epgcache = eEPGCache.getInstance()
		self.hide()
		TimerInfo = set()
		zeit = time()
		TimerName = False
		
		#== in Timerliste suchen ==============================
		for x in self.session.nav.RecordTimer.timer_list:
				TimerBegin = x.begin
				TimerBegin = TimerBegin - (TimerBegin % 60)
				TimerEnd   = x.end
				TimerEnd   = TimerEnd - (TimerEnd % 60)
				TimerPart  = TimerBegin + (TimerEnd -TimerBegin) / 4
				try:
					epgEvent = self.epgcache.lookupEventId(x.service_ref.ref, x.eit)
				except:
					epgEvent = self.epgcache.lookupEventTime(x.service_ref.ref, TimerPart)

				#print "== CheckTimer VPS: ", x.vpsplugin_enabled, x.name
				if epgEvent:
					epgBegin = epgEvent.getBeginTime()
					epgEnd = epgBegin + epgEvent.getDuration()
					epgBegin = epgBegin - (epgBegin % 60)
					epgEnd = epgEnd - (epgEnd % 60)
					
					recording_margin_before = config.recording.margin_before.value * 60
					recording_margin_after  = config.recording.margin_after.value * 60
					
					#selected timerdiff in minutes from setup
					timerdiff_time = (int(config.plugins.multiepgmv.timerdiff.value) * 60) - int(60)
					#print "=== MultiEPG_MV timerdiff", timerdiff_time
					
					#== keine Vor-/Nachlaufzeit bei VPS verrechnen ====
					if hasattr(x, "vpsplugin_enabled") and x.vpsplugin_enabled:
						recording_margin_before=0
						recording_margin_after =0
					#meldung bei abweichung ab x min 
					#...
					if epgBegin - (recording_margin_before) + timerdiff_time < TimerBegin or (epgEnd + recording_margin_after - timerdiff_time) > TimerEnd:
						#print "== ", epgEvent.getEventName(), datetime.fromtimestamp(epgBegin).strftime('%H:%M:%S'), datetime.fromtimestamp(epgEnd).strftime('%H:%M:%S'), datetime.fromtimestamp(TimerBegin).strftime('%H:%M:%S'), datetime.fromtimestamp(TimerEnd).strftime('%H:%M:%S'), (epgEvent.getDuration()/60)

						if epgEvent.getDuration() > 300 and TimerBegin > zeit:
							x.epgBegin = epgBegin
							x.epgEnd   = epgEnd
							x.recording_margin_before = recording_margin_before
							x.recording_margin_after = recording_margin_after
							TimerInfo.add(x)

		#== in inaktiven Timern suchen ==============================
		#for x in self.session.nav.RecordTimer.processed_timers:
		#		#== nur, wenn Timer noch nicht abgelaufen ===
		#		if zeit < x.end:
		#			TimerInfo.add(x)

		message_str = _('\n == MultiEPG Timer-Info == \n\n')
		for x in TimerInfo:

			TimerName = str(x.name)
			TimerZeit = "Timerzeit:  " + str(strftime('%d.%m.%Y, %H:%M', localtime(x.begin)))
			TimerZeit += str(strftime(' - %H:%M', localtime(x.end))) 
			SendeZeit = "Sendezeit: " + str(strftime('%d.%m.%Y, %H:%M', localtime(x.epgBegin - x.recording_margin_before)))
			SendeZeit += str(strftime(' - %H:%M', localtime(x.epgEnd + x.recording_margin_after)))
			if hasattr(x, "vpsplugin_enabled") and x.vpsplugin_enabled == False:
				SendeZeit + "  (inkl. Vor-/Nachlauf)"
			SenderName = str(x.service_ref.getServiceName())
			TimerProblem = _('Timer ist deaktiviert:') if x.disabled else _('-- Sende-Zeiten haben sich evtl. geaendert --')
			#message_str += TimerZeit + ' - ' + SenderName + '\n' + TimerName + ' ' + TimerProblem + '\n\n'
			message_str += TimerProblem + '\n' + TimerName + ' (' + SenderName + ')\n' + SendeZeit + "\n" + TimerZeit + '\n\n'

		message_str += _('-- Bitte die Timer ueberpruefen --')
		if TimerName:
			self.session.open(MessageBox, message_str, MessageBox.TYPE_INFO)
		
		#== EPG-Screen schliessen ===
		self.close(self.closeRecursive, zap)
		

class MultiEPGmvEPGSelection(EPGSelection):
	def __init__(self, *args):
		EPGSelection.__init__(self, *args)
		self.args = args
		self.skinName = "EPGSelection"

	def onCreate(self):
		l = self["list"]
		l.recalcEntrySize()
		service = self.currentService
		self["Service"].newService(service.ref)
		if self.saved_title is None:
			self.saved_title = self.instance.getTitle()
		#title = self.saved_title + ' - ' + service.getServiceName() + " (" + _("Search") + ": " + self.args[3].getEventName() + ")"
		title = self.saved_title + " - " + _("Search") + ": " + self.args[3].getEventName()
		#self["Title"].invalidate()
		try:
			self.setTitle(title)
			#self["Title"].text = title
		except:
			print "== Error Title.text"
		
		found_events = self.args[4]
		if len(found_events)>1:
			l.list = found_events
			l.l.setList(found_events)


def getServiceList(bouquet1 = None):
			
			bouquet = None
			infoBarInstance = InfoBar.instance
			if infoBarInstance is not None:
				servicelist = infoBarInstance.servicelist
				currentBouquet = servicelist.getRoot()
				bouquet = currentBouquet.toString()
			#print "== bouquet", bouquet
			
			services = []
			
			if bouquet is not None:
				serviceHandler = eServiceCenter.getInstance()
				myref = eServiceReference(str(bouquet))
				mylist = serviceHandler.list(myref)
				if mylist is not None:
					while 1:
						s = mylist.getNext()
						# TODO: I wonder if its sane to assume we get services here (and not just new lists)
						# We can ignore markers & directorys here because they won't match any event's service :-)
						if s.valid():
							# strip all after last :
							value = s.toString()
							#print "== service", value, ServiceReference(s).getServiceName()
							services.append(value)
						else:
							break 
			
			return services

