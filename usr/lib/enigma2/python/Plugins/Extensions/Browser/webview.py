# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.8
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _webview.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_webview', [dirname(__file__)])
        except ImportError:
            import _webview
            return _webview
        if fp is not None:
            try:
                _mod = imp.load_module('_webview', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _webview = swig_import_helper()
    del swig_import_helper
else:
    import _webview
del version_info
try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.


def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        object.__setattr__(self, name, value)
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr_nondynamic(self, class_type, name, static=1):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    if (not static):
        return object.__getattr__(self, name)
    else:
        raise AttributeError(name)

def _swig_getattr(self, class_type, name):
    return _swig_getattr_nondynamic(self, class_type, name, 0)


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object:
        pass
    _newclass = 0



def _swig_setattr_nondynamic_method(set):
    def set_attr(self, name, value):
        if (name == "thisown"):
            return self.this.own(value)
        if hasattr(self, name) or (name == "this"):
            set(self, name, value)
        else:
            raise AttributeError("You cannot add attributes to %s" % self)
    return set_attr


try:
    import weakref
    weakref_proxy = weakref.proxy
except Exception:
    weakref_proxy = lambda x: x


import enigma
class eWebView(enigma.eWidget):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    navOpenLink = _webview.eWebView_navOpenLink
    navLeft = _webview.eWebView_navLeft
    navRight = _webview.eWebView_navRight
    navUp = _webview.eWebView_navUp
    navDown = _webview.eWebView_navDown
    navPageUp = _webview.eWebView_navPageUp
    navPageDown = _webview.eWebView_navPageDown
    navTab = _webview.eWebView_navTab
    navBackspace = _webview.eWebView_navBackspace
    navBacktab = _webview.eWebView_navBacktab
    navDelete = _webview.eWebView_navDelete
    navRed = _webview.eWebView_navRed
    navGreen = _webview.eWebView_navGreen
    navYellow = _webview.eWebView_navYellow
    navBlue = _webview.eWebView_navBlue
    navMediaPlay = _webview.eWebView_navMediaPlay
    navMediaPause = _webview.eWebView_navMediaPause
    navMediaStop = _webview.eWebView_navMediaStop
    navMediaPlayPause = _webview.eWebView_navMediaPlayPause
    navMediaRewind = _webview.eWebView_navMediaRewind
    navMediaFastForward = _webview.eWebView_navMediaFastForward
    nav0 = _webview.eWebView_nav0
    nav1 = _webview.eWebView_nav1
    nav2 = _webview.eWebView_nav2
    nav3 = _webview.eWebView_nav3
    nav4 = _webview.eWebView_nav4
    nav5 = _webview.eWebView_nav5
    nav6 = _webview.eWebView_nav6
    nav7 = _webview.eWebView_nav7
    nav8 = _webview.eWebView_nav8
    nav9 = _webview.eWebView_nav9
    navBack = _webview.eWebView_navBack
    navBackExplicit = _webview.eWebView_navBackExplicit
    navForward = _webview.eWebView_navForward
    navForwardExplicit = _webview.eWebView_navForwardExplicit
    navStop = _webview.eWebView_navStop
    navReload = _webview.eWebView_navReload

    def __init__(self, parent):
        _webview.eWebView_swiginit(self, _webview.new_eWebView(parent))
    __swig_destroy__ = _webview.delete_eWebView
    contentsSizeChanged = _swig_property(_webview.eWebView_contentsSizeChanged_get, _webview.eWebView_contentsSizeChanged_set)
    iconChanged = _swig_property(_webview.eWebView_iconChanged_get, _webview.eWebView_iconChanged_set)
    initialLayoutCompleted = _swig_property(_webview.eWebView_initialLayoutCompleted_get, _webview.eWebView_initialLayoutCompleted_set)
    javaScriptWindowObjectCleared = _swig_property(_webview.eWebView_javaScriptWindowObjectCleared_get, _webview.eWebView_javaScriptWindowObjectCleared_set)
    pageChanged = _swig_property(_webview.eWebView_pageChanged_get, _webview.eWebView_pageChanged_set)
    titleChanged = _swig_property(_webview.eWebView_titleChanged_get, _webview.eWebView_titleChanged_set)
    urlChanged = _swig_property(_webview.eWebView_urlChanged_get, _webview.eWebView_urlChanged_set)
    contentsChanged = _swig_property(_webview.eWebView_contentsChanged_get, _webview.eWebView_contentsChanged_set)
    downloadRequested = _swig_property(_webview.eWebView_downloadRequested_get, _webview.eWebView_downloadRequested_set)
    geometryChangeRequested = _swig_property(_webview.eWebView_geometryChangeRequested_get, _webview.eWebView_geometryChangeRequested_set)
    linkClicked = _swig_property(_webview.eWebView_linkClicked_get, _webview.eWebView_linkClicked_set)
    linkHovered = _swig_property(_webview.eWebView_linkHovered_get, _webview.eWebView_linkHovered_set)
    loadFinished = _swig_property(_webview.eWebView_loadFinished_get, _webview.eWebView_loadFinished_set)
    loadProgress = _swig_property(_webview.eWebView_loadProgress_get, _webview.eWebView_loadProgress_set)
    loadStarted = _swig_property(_webview.eWebView_loadStarted_get, _webview.eWebView_loadStarted_set)
    menuBarVisibilityChangeRequested = _swig_property(_webview.eWebView_menuBarVisibilityChangeRequested_get, _webview.eWebView_menuBarVisibilityChangeRequested_set)
    microFocusChanged = _swig_property(_webview.eWebView_microFocusChanged_get, _webview.eWebView_microFocusChanged_set)
    selectionChanged = _swig_property(_webview.eWebView_selectionChanged_get, _webview.eWebView_selectionChanged_set)
    statusBarMessage = _swig_property(_webview.eWebView_statusBarMessage_get, _webview.eWebView_statusBarMessage_set)
    statusBarVisibilityChangeRequested = _swig_property(_webview.eWebView_statusBarVisibilityChangeRequested_get, _webview.eWebView_statusBarVisibilityChangeRequested_set)
    toolBarVisibilityChangeRequested = _swig_property(_webview.eWebView_toolBarVisibilityChangeRequested_get, _webview.eWebView_toolBarVisibilityChangeRequested_set)
    unsupportedContent = _swig_property(_webview.eWebView_unsupportedContent_get, _webview.eWebView_unsupportedContent_set)
    windowCloseRequested = _swig_property(_webview.eWebView_windowCloseRequested_get, _webview.eWebView_windowCloseRequested_set)
    javaScriptAlert = _swig_property(_webview.eWebView_javaScriptAlert_get, _webview.eWebView_javaScriptAlert_set)
    windowRequested = _swig_property(_webview.eWebView_windowRequested_get, _webview.eWebView_windowRequested_set)
    authenticationRequired = _swig_property(_webview.eWebView_authenticationRequired_get, _webview.eWebView_authenticationRequired_set)
    proxyAuthenticationRequired = _swig_property(_webview.eWebView_proxyAuthenticationRequired_get, _webview.eWebView_proxyAuthenticationRequired_set)
    sslErrors = _swig_property(_webview.eWebView_sslErrors_get, _webview.eWebView_sslErrors_set)
eWebView.navigate = new_instancemethod(_webview.eWebView_navigate, None, eWebView)
eWebView.asciiInput = new_instancemethod(_webview.eWebView_asciiInput, None, eWebView)
eWebView.load = new_instancemethod(_webview.eWebView_load, None, eWebView)
eWebView.scroll = new_instancemethod(_webview.eWebView_scroll, None, eWebView)
eWebView.getHtml = new_instancemethod(_webview.eWebView_getHtml, None, eWebView)
eWebView.setHtml = new_instancemethod(_webview.eWebView_setHtml, None, eWebView)
eWebView.setZoomFactor = new_instancemethod(_webview.eWebView_setZoomFactor, None, eWebView)
eWebView.getZoomFactor = new_instancemethod(_webview.eWebView_getZoomFactor, None, eWebView)
eWebView.setDict = new_instancemethod(_webview.eWebView_setDict, None, eWebView)
eWebView.enablePersistentStorage = new_instancemethod(_webview.eWebView_enablePersistentStorage, None, eWebView)
eWebView.getRawCookies = new_instancemethod(_webview.eWebView_getRawCookies, None, eWebView)
eWebView.setRawCookies = new_instancemethod(_webview.eWebView_setRawCookies, None, eWebView)
eWebView.setHbbtv = new_instancemethod(_webview.eWebView_setHbbtv, None, eWebView)
eWebView.setBackgroundTransparent = new_instancemethod(_webview.eWebView_setBackgroundTransparent, None, eWebView)
eWebView.setAcceptLanguage = new_instancemethod(_webview.eWebView_setAcceptLanguage, None, eWebView)
eWebView.leftClick = new_instancemethod(_webview.eWebView_leftClick, None, eWebView)
eWebView.scale = new_instancemethod(_webview.eWebView_scale, None, eWebView)
eWebView.show = new_instancemethod(_webview.eWebView_show, None, eWebView)
eWebView.hide = new_instancemethod(_webview.eWebView_hide, None, eWebView)
eWebView.getUserAgent = new_instancemethod(_webview.eWebView_getUserAgent, None, eWebView)
eWebView.setUserAgent = new_instancemethod(_webview.eWebView_setUserAgent, None, eWebView)
eWebView.resetUserAgent = new_instancemethod(_webview.eWebView_resetUserAgent, None, eWebView)
eWebView_swigregister = _webview.eWebView_swigregister
eWebView_swigregister(eWebView)
cvar = _webview.cvar

class StdStringList(object):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __iter__(self):
        return self.iterator()

    def __init__(self, *args):
        _webview.StdStringList_swiginit(self, _webview.new_StdStringList(*args))
    __swig_destroy__ = _webview.delete_StdStringList
StdStringList.iterator = new_instancemethod(_webview.StdStringList_iterator, None, StdStringList)
StdStringList.__nonzero__ = new_instancemethod(_webview.StdStringList___nonzero__, None, StdStringList)
StdStringList.__bool__ = new_instancemethod(_webview.StdStringList___bool__, None, StdStringList)
StdStringList.__len__ = new_instancemethod(_webview.StdStringList___len__, None, StdStringList)
StdStringList.__getslice__ = new_instancemethod(_webview.StdStringList___getslice__, None, StdStringList)
StdStringList.__setslice__ = new_instancemethod(_webview.StdStringList___setslice__, None, StdStringList)
StdStringList.__delslice__ = new_instancemethod(_webview.StdStringList___delslice__, None, StdStringList)
StdStringList.__delitem__ = new_instancemethod(_webview.StdStringList___delitem__, None, StdStringList)
StdStringList.__getitem__ = new_instancemethod(_webview.StdStringList___getitem__, None, StdStringList)
StdStringList.__setitem__ = new_instancemethod(_webview.StdStringList___setitem__, None, StdStringList)
StdStringList.pop = new_instancemethod(_webview.StdStringList_pop, None, StdStringList)
StdStringList.append = new_instancemethod(_webview.StdStringList_append, None, StdStringList)
StdStringList.empty = new_instancemethod(_webview.StdStringList_empty, None, StdStringList)
StdStringList.size = new_instancemethod(_webview.StdStringList_size, None, StdStringList)
StdStringList.swap = new_instancemethod(_webview.StdStringList_swap, None, StdStringList)
StdStringList.begin = new_instancemethod(_webview.StdStringList_begin, None, StdStringList)
StdStringList.end = new_instancemethod(_webview.StdStringList_end, None, StdStringList)
StdStringList.rbegin = new_instancemethod(_webview.StdStringList_rbegin, None, StdStringList)
StdStringList.rend = new_instancemethod(_webview.StdStringList_rend, None, StdStringList)
StdStringList.clear = new_instancemethod(_webview.StdStringList_clear, None, StdStringList)
StdStringList.get_allocator = new_instancemethod(_webview.StdStringList_get_allocator, None, StdStringList)
StdStringList.pop_back = new_instancemethod(_webview.StdStringList_pop_back, None, StdStringList)
StdStringList.erase = new_instancemethod(_webview.StdStringList_erase, None, StdStringList)
StdStringList.push_back = new_instancemethod(_webview.StdStringList_push_back, None, StdStringList)
StdStringList.front = new_instancemethod(_webview.StdStringList_front, None, StdStringList)
StdStringList.back = new_instancemethod(_webview.StdStringList_back, None, StdStringList)
StdStringList.assign = new_instancemethod(_webview.StdStringList_assign, None, StdStringList)
StdStringList.resize = new_instancemethod(_webview.StdStringList_resize, None, StdStringList)
StdStringList.insert = new_instancemethod(_webview.StdStringList_insert, None, StdStringList)
StdStringList.pop_front = new_instancemethod(_webview.StdStringList_pop_front, None, StdStringList)
StdStringList.push_front = new_instancemethod(_webview.StdStringList_push_front, None, StdStringList)
StdStringList.reverse = new_instancemethod(_webview.StdStringList_reverse, None, StdStringList)
StdStringList_swigregister = _webview.StdStringList_swigregister
StdStringList_swigregister(StdStringList)

class ByteVector(object):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __iter__(self):
        return self.iterator()

    def __init__(self, *args):
        _webview.ByteVector_swiginit(self, _webview.new_ByteVector(*args))
    __swig_destroy__ = _webview.delete_ByteVector
ByteVector.iterator = new_instancemethod(_webview.ByteVector_iterator, None, ByteVector)
ByteVector.__nonzero__ = new_instancemethod(_webview.ByteVector___nonzero__, None, ByteVector)
ByteVector.__bool__ = new_instancemethod(_webview.ByteVector___bool__, None, ByteVector)
ByteVector.__len__ = new_instancemethod(_webview.ByteVector___len__, None, ByteVector)
ByteVector.__getslice__ = new_instancemethod(_webview.ByteVector___getslice__, None, ByteVector)
ByteVector.__setslice__ = new_instancemethod(_webview.ByteVector___setslice__, None, ByteVector)
ByteVector.__delslice__ = new_instancemethod(_webview.ByteVector___delslice__, None, ByteVector)
ByteVector.__delitem__ = new_instancemethod(_webview.ByteVector___delitem__, None, ByteVector)
ByteVector.__getitem__ = new_instancemethod(_webview.ByteVector___getitem__, None, ByteVector)
ByteVector.__setitem__ = new_instancemethod(_webview.ByteVector___setitem__, None, ByteVector)
ByteVector.pop = new_instancemethod(_webview.ByteVector_pop, None, ByteVector)
ByteVector.append = new_instancemethod(_webview.ByteVector_append, None, ByteVector)
ByteVector.empty = new_instancemethod(_webview.ByteVector_empty, None, ByteVector)
ByteVector.size = new_instancemethod(_webview.ByteVector_size, None, ByteVector)
ByteVector.swap = new_instancemethod(_webview.ByteVector_swap, None, ByteVector)
ByteVector.begin = new_instancemethod(_webview.ByteVector_begin, None, ByteVector)
ByteVector.end = new_instancemethod(_webview.ByteVector_end, None, ByteVector)
ByteVector.rbegin = new_instancemethod(_webview.ByteVector_rbegin, None, ByteVector)
ByteVector.rend = new_instancemethod(_webview.ByteVector_rend, None, ByteVector)
ByteVector.clear = new_instancemethod(_webview.ByteVector_clear, None, ByteVector)
ByteVector.get_allocator = new_instancemethod(_webview.ByteVector_get_allocator, None, ByteVector)
ByteVector.pop_back = new_instancemethod(_webview.ByteVector_pop_back, None, ByteVector)
ByteVector.erase = new_instancemethod(_webview.ByteVector_erase, None, ByteVector)
ByteVector.push_back = new_instancemethod(_webview.ByteVector_push_back, None, ByteVector)
ByteVector.front = new_instancemethod(_webview.ByteVector_front, None, ByteVector)
ByteVector.back = new_instancemethod(_webview.ByteVector_back, None, ByteVector)
ByteVector.assign = new_instancemethod(_webview.ByteVector_assign, None, ByteVector)
ByteVector.resize = new_instancemethod(_webview.ByteVector_resize, None, ByteVector)
ByteVector.insert = new_instancemethod(_webview.ByteVector_insert, None, ByteVector)
ByteVector.reserve = new_instancemethod(_webview.ByteVector_reserve, None, ByteVector)
ByteVector.capacity = new_instancemethod(_webview.ByteVector_capacity, None, ByteVector)
ByteVector_swigregister = _webview.ByteVector_swigregister
ByteVector_swigregister(ByteVector)

class ByteVectorList(object):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __iter__(self):
        return self.iterator()

    def __init__(self, *args):
        _webview.ByteVectorList_swiginit(self, _webview.new_ByteVectorList(*args))
    __swig_destroy__ = _webview.delete_ByteVectorList
ByteVectorList.iterator = new_instancemethod(_webview.ByteVectorList_iterator, None, ByteVectorList)
ByteVectorList.__nonzero__ = new_instancemethod(_webview.ByteVectorList___nonzero__, None, ByteVectorList)
ByteVectorList.__bool__ = new_instancemethod(_webview.ByteVectorList___bool__, None, ByteVectorList)
ByteVectorList.__len__ = new_instancemethod(_webview.ByteVectorList___len__, None, ByteVectorList)
ByteVectorList.__getslice__ = new_instancemethod(_webview.ByteVectorList___getslice__, None, ByteVectorList)
ByteVectorList.__setslice__ = new_instancemethod(_webview.ByteVectorList___setslice__, None, ByteVectorList)
ByteVectorList.__delslice__ = new_instancemethod(_webview.ByteVectorList___delslice__, None, ByteVectorList)
ByteVectorList.__delitem__ = new_instancemethod(_webview.ByteVectorList___delitem__, None, ByteVectorList)
ByteVectorList.__getitem__ = new_instancemethod(_webview.ByteVectorList___getitem__, None, ByteVectorList)
ByteVectorList.__setitem__ = new_instancemethod(_webview.ByteVectorList___setitem__, None, ByteVectorList)
ByteVectorList.pop = new_instancemethod(_webview.ByteVectorList_pop, None, ByteVectorList)
ByteVectorList.append = new_instancemethod(_webview.ByteVectorList_append, None, ByteVectorList)
ByteVectorList.empty = new_instancemethod(_webview.ByteVectorList_empty, None, ByteVectorList)
ByteVectorList.size = new_instancemethod(_webview.ByteVectorList_size, None, ByteVectorList)
ByteVectorList.swap = new_instancemethod(_webview.ByteVectorList_swap, None, ByteVectorList)
ByteVectorList.begin = new_instancemethod(_webview.ByteVectorList_begin, None, ByteVectorList)
ByteVectorList.end = new_instancemethod(_webview.ByteVectorList_end, None, ByteVectorList)
ByteVectorList.rbegin = new_instancemethod(_webview.ByteVectorList_rbegin, None, ByteVectorList)
ByteVectorList.rend = new_instancemethod(_webview.ByteVectorList_rend, None, ByteVectorList)
ByteVectorList.clear = new_instancemethod(_webview.ByteVectorList_clear, None, ByteVectorList)
ByteVectorList.get_allocator = new_instancemethod(_webview.ByteVectorList_get_allocator, None, ByteVectorList)
ByteVectorList.pop_back = new_instancemethod(_webview.ByteVectorList_pop_back, None, ByteVectorList)
ByteVectorList.erase = new_instancemethod(_webview.ByteVectorList_erase, None, ByteVectorList)
ByteVectorList.push_back = new_instancemethod(_webview.ByteVectorList_push_back, None, ByteVectorList)
ByteVectorList.front = new_instancemethod(_webview.ByteVectorList_front, None, ByteVectorList)
ByteVectorList.back = new_instancemethod(_webview.ByteVectorList_back, None, ByteVectorList)
ByteVectorList.assign = new_instancemethod(_webview.ByteVectorList_assign, None, ByteVectorList)
ByteVectorList.resize = new_instancemethod(_webview.ByteVectorList_resize, None, ByteVectorList)
ByteVectorList.insert = new_instancemethod(_webview.ByteVectorList_insert, None, ByteVectorList)
ByteVectorList.pop_front = new_instancemethod(_webview.ByteVectorList_pop_front, None, ByteVectorList)
ByteVectorList.push_front = new_instancemethod(_webview.ByteVectorList_push_front, None, ByteVectorList)
ByteVectorList.reverse = new_instancemethod(_webview.ByteVectorList_reverse, None, ByteVectorList)
ByteVectorList_swigregister = _webview.ByteVectorList_swigregister
ByteVectorList_swigregister(ByteVectorList)

from enigma import WeakMethodReference

class eSlot2CStrCstr(enigma.eSlot):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self):
        if self.__class__ == eSlot2CStrCstr:
            _self = None
        else:
            _self = self
        _webview.eSlot2CStrCstr_swiginit(self, _webview.new_eSlot2CStrCstr(_self, ))
    __swig_destroy__ = _webview.delete_eSlot2CStrCstr
    def __disown__(self):
        self.this.disown()
        _webview.disown_eSlot2CStrCstr(self)
        return weakref_proxy(self)
eSlot2CStrCstr.cb_func = new_instancemethod(_webview.eSlot2CStrCstr_cb_func, None, eSlot2CStrCstr)
eSlot2CStrCstr_swigregister = _webview.eSlot2CStrCstr_swigregister
eSlot2CStrCstr_swigregister(eSlot2CStrCstr)

class eSignal2CStrCstr(object):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def connect(self, func):
        class ePythonSlot2CStrCstr(eSlot2CStrCstr):
            def __init__(self, func):
                eSlot2CStrCstr.__init__(self)
                self.cb_func=func
        slot = ePythonSlot2CStrCstr(WeakMethodReference(func))
        self.connect2(slot)
        return slot

    def __init__(self):
        _webview.eSignal2CStrCstr_swiginit(self, _webview.new_eSignal2CStrCstr())
    __swig_destroy__ = _webview.delete_eSignal2CStrCstr
eSignal2CStrCstr.connect2 = new_instancemethod(_webview.eSignal2CStrCstr_connect2, None, eSignal2CStrCstr)
eSignal2CStrCstr_swigregister = _webview.eSignal2CStrCstr_swigregister
eSignal2CStrCstr_swigregister(eSignal2CStrCstr)

class eSlot3CStrCStrCStr(enigma.eSlot):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self):
        if self.__class__ == eSlot3CStrCStrCStr:
            _self = None
        else:
            _self = self
        _webview.eSlot3CStrCStrCStr_swiginit(self, _webview.new_eSlot3CStrCStrCStr(_self, ))
    __swig_destroy__ = _webview.delete_eSlot3CStrCStrCStr
    def __disown__(self):
        self.this.disown()
        _webview.disown_eSlot3CStrCStrCStr(self)
        return weakref_proxy(self)
eSlot3CStrCStrCStr.cb_func = new_instancemethod(_webview.eSlot3CStrCStrCStr_cb_func, None, eSlot3CStrCStrCStr)
eSlot3CStrCStrCStr_swigregister = _webview.eSlot3CStrCStrCStr_swigregister
eSlot3CStrCStrCStr_swigregister(eSlot3CStrCStrCStr)

class eSignal3CStrCStrCStr(object):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def connect(self, func):
        class ePythonSlot3CStrCStrCStr(eSlot3CStrCStrCStr):
            def __init__(self, func):
                eSlot3CStrCStrCStr.__init__(self)
                self.cb_func=func
        slot = ePythonSlot3CStrCStrCStr(WeakMethodReference(func))
        self.connect2(slot)
        return slot

    def __init__(self):
        _webview.eSignal3CStrCStrCStr_swiginit(self, _webview.new_eSignal3CStrCStrCStr())
    __swig_destroy__ = _webview.delete_eSignal3CStrCStrCStr
eSignal3CStrCStrCStr.connect2 = new_instancemethod(_webview.eSignal3CStrCStrCStr_connect2, None, eSignal3CStrCStrCStr)
eSignal3CStrCStrCStr_swigregister = _webview.eSignal3CStrCStrCStr_swigregister
eSignal3CStrCStrCStr_swigregister(eSignal3CStrCStrCStr)

class eSlot3LongStrListByteVectorList(enigma.eSlot):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self):
        if self.__class__ == eSlot3LongStrListByteVectorList:
            _self = None
        else:
            _self = self
        _webview.eSlot3LongStrListByteVectorList_swiginit(self, _webview.new_eSlot3LongStrListByteVectorList(_self, ))
    __swig_destroy__ = _webview.delete_eSlot3LongStrListByteVectorList
    def __disown__(self):
        self.this.disown()
        _webview.disown_eSlot3LongStrListByteVectorList(self)
        return weakref_proxy(self)
eSlot3LongStrListByteVectorList.cb_func = new_instancemethod(_webview.eSlot3LongStrListByteVectorList_cb_func, None, eSlot3LongStrListByteVectorList)
eSlot3LongStrListByteVectorList_swigregister = _webview.eSlot3LongStrListByteVectorList_swigregister
eSlot3LongStrListByteVectorList_swigregister(eSlot3LongStrListByteVectorList)

class eSignal3LongStrListByteVectorList(object):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def connect(self, func):
        class ePythonSlot3LongStrListByteVectorList(eSlot3LongStrListByteVectorList):
            def __init__(self, func):
                eSlot3LongStrListByteVectorList.__init__(self)
                self.cb_func=func
        slot = ePythonSlot3LongStrListByteVectorList(WeakMethodReference(func))
        self.connect2(slot)
        return slot

    def __init__(self):
        _webview.eSignal3LongStrListByteVectorList_swiginit(self, _webview.new_eSignal3LongStrListByteVectorList())
    __swig_destroy__ = _webview.delete_eSignal3LongStrListByteVectorList
eSignal3LongStrListByteVectorList.connect2 = new_instancemethod(_webview.eSignal3LongStrListByteVectorList_connect2, None, eSignal3LongStrListByteVectorList)
eSignal3LongStrListByteVectorList_swigregister = _webview.eSignal3LongStrListByteVectorList_swigregister
eSignal3LongStrListByteVectorList_swigregister(eSignal3LongStrListByteVectorList)

class eSlot4IntIntIntInt(enigma.eSlot):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self):
        if self.__class__ == eSlot4IntIntIntInt:
            _self = None
        else:
            _self = self
        _webview.eSlot4IntIntIntInt_swiginit(self, _webview.new_eSlot4IntIntIntInt(_self, ))
    __swig_destroy__ = _webview.delete_eSlot4IntIntIntInt
    def __disown__(self):
        self.this.disown()
        _webview.disown_eSlot4IntIntIntInt(self)
        return weakref_proxy(self)
eSlot4IntIntIntInt.cb_func = new_instancemethod(_webview.eSlot4IntIntIntInt_cb_func, None, eSlot4IntIntIntInt)
eSlot4IntIntIntInt_swigregister = _webview.eSlot4IntIntIntInt_swigregister
eSlot4IntIntIntInt_swigregister(eSlot4IntIntIntInt)

class eSignal4IntIntIntInt(object):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def connect(self, func):
        class ePythonSlot4IntIntIntInt(eSlot4IntIntIntInt):
            def __init__(self, func):
                eSlot4IntIntIntInt.__init__(self)
                self.cb_func=func
        slot = ePythonSlot4IntIntIntInt(WeakMethodReference(func))
        self.connect2(slot)
        return slot

    def __init__(self):
        _webview.eSignal4IntIntIntInt_swiginit(self, _webview.new_eSignal4IntIntIntInt())
    __swig_destroy__ = _webview.delete_eSignal4IntIntIntInt
eSignal4IntIntIntInt.connect2 = new_instancemethod(_webview.eSignal4IntIntIntInt_connect2, None, eSignal4IntIntIntInt)
eSignal4IntIntIntInt_swigregister = _webview.eSignal4IntIntIntInt_swigregister
eSignal4IntIntIntInt_swigregister(eSignal4IntIntIntInt)

class eSlot4LongCStrCStrCStr(enigma.eSlot):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self):
        if self.__class__ == eSlot4LongCStrCStrCStr:
            _self = None
        else:
            _self = self
        _webview.eSlot4LongCStrCStrCStr_swiginit(self, _webview.new_eSlot4LongCStrCStrCStr(_self, ))
    __swig_destroy__ = _webview.delete_eSlot4LongCStrCStrCStr
    def __disown__(self):
        self.this.disown()
        _webview.disown_eSlot4LongCStrCStrCStr(self)
        return weakref_proxy(self)
eSlot4LongCStrCStrCStr.cb_func = new_instancemethod(_webview.eSlot4LongCStrCStrCStr_cb_func, None, eSlot4LongCStrCStrCStr)
eSlot4LongCStrCStrCStr_swigregister = _webview.eSlot4LongCStrCStrCStr_swigregister
eSlot4LongCStrCStrCStr_swigregister(eSlot4LongCStrCStrCStr)

class eSignal4LongCStrCStrCStr(object):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def connect(self, func):
        class ePythonSlot4LongCStrCStrCStr(eSlot4LongCStrCStrCStr):
            def __init__(self, func):
                eSlot4LongCStrCStrCStr.__init__(self)
                self.cb_func=func
        slot = ePythonSlot4LongCStrCStrCStr(WeakMethodReference(func))
        self.connect2(slot)
        return slot

    def __init__(self):
        _webview.eSignal4LongCStrCStrCStr_swiginit(self, _webview.new_eSignal4LongCStrCStrCStr())
    __swig_destroy__ = _webview.delete_eSignal4LongCStrCStrCStr
eSignal4LongCStrCStrCStr.connect2 = new_instancemethod(_webview.eSignal4LongCStrCStrCStr_connect2, None, eSignal4LongCStrCStrCStr)
eSignal4LongCStrCStrCStr_swigregister = _webview.eSignal4LongCStrCStrCStr_swigregister
eSignal4LongCStrCStrCStr_swigregister(eSignal4LongCStrCStrCStr)

class eSlot5IntIntIntIntBool(enigma.eSlot):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self):
        if self.__class__ == eSlot5IntIntIntIntBool:
            _self = None
        else:
            _self = self
        _webview.eSlot5IntIntIntIntBool_swiginit(self, _webview.new_eSlot5IntIntIntIntBool(_self, ))
    __swig_destroy__ = _webview.delete_eSlot5IntIntIntIntBool
    def __disown__(self):
        self.this.disown()
        _webview.disown_eSlot5IntIntIntIntBool(self)
        return weakref_proxy(self)
eSlot5IntIntIntIntBool.cb_func = new_instancemethod(_webview.eSlot5IntIntIntIntBool_cb_func, None, eSlot5IntIntIntIntBool)
eSlot5IntIntIntIntBool_swigregister = _webview.eSlot5IntIntIntIntBool_swigregister
eSlot5IntIntIntIntBool_swigregister(eSlot5IntIntIntIntBool)

class eSignal5IntIntIntIntBool(object):
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def connect(self, func):
        class ePythonSlot5IntIntIntIntBool(eSlot5IntIntIntIntBool):
            def __init__(self, func):
                eSlot5IntIntIntIntBool.__init__(self)
                self.cb_func=func
        slot = ePythonSlot5IntIntIntIntBool(WeakMethodReference(func))
        self.connect2(slot)
        return slot

    def __init__(self):
        _webview.eSignal5IntIntIntIntBool_swiginit(self, _webview.new_eSignal5IntIntIntIntBool())
    __swig_destroy__ = _webview.delete_eSignal5IntIntIntIntBool
eSignal5IntIntIntIntBool.connect2 = new_instancemethod(_webview.eSignal5IntIntIntIntBool_connect2, None, eSignal5IntIntIntIntBool)
eSignal5IntIntIntIntBool_swigregister = _webview.eSignal5IntIntIntIntBool_swigregister
eSignal5IntIntIntIntBool_swigregister(eSignal5IntIntIntIntBool)



