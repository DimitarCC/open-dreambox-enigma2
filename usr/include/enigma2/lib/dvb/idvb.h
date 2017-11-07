#ifndef __dvb_idvb_h
#define __dvb_idvb_h

#ifndef SWIG

#include <linux/dvb/dmx.h>
#include <linux/dvb/video.h>
#include <lib/dvb/frontendparms.h>
#include <lib/base/object.h>
#include <lib/base/ebase.h>
#include <lib/base/elock.h>
#include <lib/base/itssource.h>
#include <lib/service/service.h>
#include <lib/base/sigc.h>
#include <lib/base/connection.h>

#include <list>
typedef std::list<uint16_t> CAID_LIST;

#include <boost/any.hpp>

struct dvb_frontend_parameters;

struct eDVBSectionFilterMask
{
	int pid;
		/* mode is 0 for positive, 1 for negative filtering */
	__u8 data[DMX_FILTER_SIZE], mask[DMX_FILTER_SIZE], mode[DMX_FILTER_SIZE];
	enum {
		rfCRC=1,
		rfNoAbort=2
	};
	int flags;
};

struct eDVBTableSpec
{
	int pid, tid, tidext, tid_mask, tidext_mask;
	int version;
	int timeout;        /* timeout in ms */
	enum
	{
		tfInOrder=1,
		/*
			tfAnyVersion      filter ANY version
			0                 filter all EXCEPT given version (negative filtering)
			tfThisVersion     filter only THIS version
		*/
		tfAnyVersion=2,
		tfThisVersion=4,
		tfHaveTID=8,
		tfHaveTIDExt=16,
		tfCheckCRC=32,
		tfHaveTimeout=64,
		tfHaveTIDMask=128,
		tfHaveTIDExtMask=256
	};
	int flags;
};

struct eBouquet
{
	std::string m_bouquet_name;
	std::string m_filename;  // without path.. just name
	typedef std::list<eServiceReference> list;
	list m_services;
// the following five methods are implemented in db.cpp
	RESULT flushChanges();
	RESULT addService(const eServiceReference &, eServiceReference before=eServiceReference());
	RESULT removeService(const eServiceReference &);
	RESULT moveService(const eServiceReference &, unsigned int);
	RESULT setListName(const std::string &name);
};

		/* these structures have by intention no operator int() defined.
		   the reason of these structures is to avoid mixing for example
		   a onid and a tsid (as there's no general order for them).
		   
		   defining an operator int() would implicitely convert values
		   between them over the constructor with the int argument.
		   
		   'explicit' doesn't here - eTransportStreamID(eOriginalNetworkID(n)) 
		   would still work. */

struct eTransportStreamID
{
private:
	int v;
public:
	int get() const { return v; }
	eTransportStreamID(int i): v(i) { }
	eTransportStreamID(): v(-1) { }
	bool operator == (const eTransportStreamID &c) const { return v == c.v; }
	bool operator != (const eTransportStreamID &c) const { return v != c.v; }
	bool operator < (const eTransportStreamID &c) const { return v < c.v; }
	bool operator > (const eTransportStreamID &c) const { return v > c.v; }
};

struct eServiceID
{
private:
	int v;
public:
	int get() const { return v; }
	eServiceID(int i): v(i) { }
	eServiceID(): v(-1) { }
	bool operator == (const eServiceID &c) const { return v == c.v; }
	bool operator != (const eServiceID &c) const { return v != c.v; }
	bool operator < (const eServiceID &c) const { return v < c.v; }
	bool operator > (const eServiceID &c) const { return v > c.v; }
};

struct eOriginalNetworkID
{
private:
	int v;
public:
	int get() const { return v; }
	eOriginalNetworkID(int i): v(i) { }
	eOriginalNetworkID(): v(-1) { }
	bool operator == (const eOriginalNetworkID &c) const { return v == c.v; }
	bool operator != (const eOriginalNetworkID &c) const { return v != c.v; }
	bool operator < (const eOriginalNetworkID &c) const { return v < c.v; }
	bool operator > (const eOriginalNetworkID &c) const { return v > c.v; }
};

struct eDVBNamespace
{
private:
	int v;
public:
	int get() const { return v; }
	eDVBNamespace(int i): v(i) { }
	eDVBNamespace(): v(-1) { }
	bool operator == (const eDVBNamespace &c) const { return v == c.v; }
	bool operator != (const eDVBNamespace &c) const { return v != c.v; }
	bool operator < (const eDVBNamespace &c) const { return (unsigned int)v < (unsigned int)c.v; }
	bool operator > (const eDVBNamespace &c) const { return (unsigned int)v > (unsigned int)c.v; }
};

struct eDVBChannelID
{
	eDVBNamespace dvbnamespace;
	eTransportStreamID transport_stream_id;
	eOriginalNetworkID original_network_id;
	std::string pvr_source;
	
	bool operator==(const eDVBChannelID &c) const
	{
		return dvbnamespace == c.dvbnamespace &&
			transport_stream_id == c.transport_stream_id &&
			original_network_id == c.original_network_id &&
			pvr_source == c.pvr_source;
	}
	
	bool operator<(const eDVBChannelID &c) const
	{
		if (dvbnamespace < c.dvbnamespace)
			return 1;
		else if (dvbnamespace == c.dvbnamespace)
		{
			if (original_network_id < c.original_network_id)
				return 1;
			else if (original_network_id == c.original_network_id)
			{
				if (transport_stream_id < c.transport_stream_id)
					return 1;
				else if (transport_stream_id == c.transport_stream_id)
				{
					if (pvr_source < c.pvr_source)
						return 1;
				}
			}
		}
		return 0;
	}
	eDVBChannelID(eDVBNamespace dvbnamespace, eTransportStreamID tsid, eOriginalNetworkID onid, const std::string &pvr_source = std::string()):
			dvbnamespace(dvbnamespace), transport_stream_id(tsid), original_network_id(onid), pvr_source(pvr_source)
	{
	}
	eDVBChannelID():
			dvbnamespace(-1), transport_stream_id(-1), original_network_id(-1)
	{
	}
	operator bool() const
	{
		return (dvbnamespace != -1) && (transport_stream_id != -1) && (original_network_id != -1);
	}
};

struct eServiceReferenceDVB: public eServiceReference
{
	int getServiceType() const { return data[0]; }
	void setServiceType(int service_type) { data[0]=service_type; }

	eServiceID getServiceID() const { return eServiceID(data[1]); }
	void setServiceID(eServiceID service_id) { data[1]=service_id.get(); }

	eTransportStreamID getTransportStreamID() const { return eTransportStreamID(data[2]); }
	void setTransportStreamID(eTransportStreamID transport_stream_id) { data[2]=transport_stream_id.get(); }

	eOriginalNetworkID getOriginalNetworkID() const { return eOriginalNetworkID(data[3]); }
	void setOriginalNetworkID(eOriginalNetworkID original_network_id) { data[3]=original_network_id.get(); }

	eDVBNamespace getDVBNamespace() const { return eDVBNamespace(data[4]); }
	void setDVBNamespace(eDVBNamespace dvbnamespace) { data[4]=dvbnamespace.get(); }

	eServiceID getParentServiceID() const { return eServiceID(data[5]); }
	void setParentServiceID( eServiceID sid ) { data[5]=sid.get(); }

	eTransportStreamID getParentTransportStreamID() const { return eTransportStreamID(data[6]); }
	void setParentTransportStreamID( eTransportStreamID tsid ) { data[6]=tsid.get(); }

	eServiceReferenceDVB getParentServiceReference() const
	{
		eServiceReferenceDVB tmp(*this);
		if (data[5] && data[6])
		{
			tmp.data[1] = data[5];
			tmp.data[2] = data[6];
			tmp.data[5] = tmp.data[6] = 0;
		}
		else
			tmp.type = idInvalid;
		return tmp;
	}

	eServiceReferenceDVB(eDVBNamespace dvbnamespace, eTransportStreamID transport_stream_id, eOriginalNetworkID original_network_id, eServiceID service_id, int service_type)
		:eServiceReference(eServiceReference::idDVB, 0)
	{
		setTransportStreamID(transport_stream_id);
		setOriginalNetworkID(original_network_id);
		setDVBNamespace(dvbnamespace);
		setServiceID(service_id);
		setServiceType(service_type);
	}
	
	void set(const eDVBChannelID &chid)
	{
		setDVBNamespace(chid.dvbnamespace);
		setOriginalNetworkID(chid.original_network_id);
		setTransportStreamID(chid.transport_stream_id);
	}
	
	void getChannelID(eDVBChannelID &chid) const
	{
		chid = eDVBChannelID(getDVBNamespace(), getTransportStreamID(), getOriginalNetworkID(), path);
	}

	eServiceReferenceDVB()
		:eServiceReference(eServiceReference::idDVB, 0)
	{
	}

	eServiceReferenceDVB(const std::string &string)
		:eServiceReference(string)
	{
	}

	bool compareDVB(const eServiceReferenceDVB& r) const
	{
		if ((unsigned int)data[4] < (unsigned int)r.data[4])
			return true;
		if (data[4] == r.data[4])
		{
			if (data[3] < r.data[3])
				return true;
			if (data[3] == r.data[3])
			{
				if (data[2] < r.data[2])
					return true;
				if (data[2] == r.data[2])
					return data[1] < r.data[1];
			}
		}
		return false;
	}
};


////////////////// TODO: we need an interface here, but what exactly?

#include <set>
// btw, still implemented in db.cpp. FIX THIS, TOO.

class eDVBChannelQuery;

class eDVBService: public iStaticServiceInformation
{
	DECLARE_REF(eDVBService);
	int *m_cache;
	void initCache();
	void copyCache(const eDVBService &source);

	std::string m_service_name, m_service_name_sort;
	std::string m_provider_name;
	int m_flags;
	CAID_LIST m_ca;
	int m_running_state; // only valid for services on onid 0x85 yet...

public:
	enum cacheID
	{
		cVPID, cMPEGAPID, cTPID, cPCRPID, cAC3PID,
		cVTYPE, cACHANNEL, cAC3DELAY, cPCMDELAY,
		cSUBTITLE, cATYPE, cAPID, cacheMax
	};

	int getCacheEntry(cacheID) const;
	void setCacheEntry(cacheID, int);

	bool cacheEmpty() const;

	const std::string &getServiceName() const;
	void setServiceName(const std::string &name);
	void setServiceName(const char *name);

	const std::string &getServiceNameSort() const;
	void setServiceNameSort(const std::string &name);
	void setServiceNameSort(const char *name);

	const std::string &getProviderName() const;
	void setProviderName(const std::string &name);
	void setProviderName(const char *name);

	int getFlags() const;
	void setFlags(int);

	const CAID_LIST &getCaIds() const;
	void setCaIds(const CAID_LIST &ca);

	int getRunningState() const;
	void setRunningState(int);

	eDVBService();
		/* m_service_name_sort is uppercase, with special chars removed, to increase sort performance. */

	void genSortName();

	enum
	{
		dxNoSDT=1,    // don't get SDT
		dxDontshow=2,
		dxNoDVB=4,  // dont use PMT for this service ( use cached pids )
		dxHoldName=8,
		dxNewFound=64,
	};

	bool usePMT() const { return !(m_flags & dxNoDVB); }
	bool isHidden() const { return m_flags & dxDontshow; }

	virtual ~eDVBService();

	eDVBService &operator=(const eDVBService &);

	// iStaticServiceInformation
	RESULT getName(const eServiceReference &ref, std::string &name);
	RESULT getEvent(const eServiceReference &ref, ePtr<eServiceEvent> &ptr, time_t start_time);
	int isPlayable(const eServiceReference &ref, const eServiceReference &ignore, bool simulate=false);

	int getInfo(const eServiceReference &ref, int);  // implemented in lib/service/servicedvb.cpp
	std::string getInfoString(const eServiceReference &ref, int);  // implemented in lib/service/servicedvb.cpp
	boost::any getInfoObject(const eServiceReference &ref, int);  // implemented in lib/service/servicedvb.cpp

		/* for filtering: */
	int checkFilter(const eServiceReferenceDVB &ref, const eDVBChannelQuery &query);


};

//////////////////

class iDVBChannel;
class iDVBDemux;
class iDVBFrontendParameters;

class iDVBChannelListQuery: public iObject
{
public:
	virtual RESULT getNextResult(eServiceReferenceDVB &ref)=0;
	virtual int compareLessEqual(const eServiceReferenceDVB &a, const eServiceReferenceDVB &b)=0;
};

class eDVBChannelQuery: public iObject
{
	DECLARE_REF(eDVBChannelQuery);
public:
	enum
	{
		tName,
		tProvider,
		tType,
		tBouquet,
		tSatellitePosition,
		tChannelID,
		tAND,
		tOR,
		tAny,
		tNumCAIDs,
		tFlags
	};
	
	int m_type;
	int m_inverse;
	
	std::string m_string;
	int m_int;
	eDVBChannelID m_channelid;
	
		/* sort is only valid in root, and must be from the enum above. */
	int m_sort;
	std::string m_bouquet_name;
	
	static RESULT compile(ePtr<eDVBChannelQuery> &res, const std::string &query);
	
	ePtr<eDVBChannelQuery> m_p1, m_p2;
};

class iDVBChannelList: public iObject
{
public:
	virtual RESULT removeService(const eServiceReference &service)=0;
	virtual RESULT removeServices(eDVBChannelID chid=eDVBChannelID(), unsigned int orb_pos=0xFFFFFFFF)=0;
	virtual RESULT removeServices(int dvb_namespace=-1, int tsid=-1, int onid=-1, unsigned int orb_pos=0xFFFFFFFF)=0;
	virtual RESULT removeServices(iDVBFrontendParameters *feparm)=0;
	virtual RESULT addFlag(const eServiceReference &service, unsigned int flagmask=0xFFFFFFFF)=0;
	virtual RESULT removeFlag(const eServiceReference &service, unsigned int flagmask=0xFFFFFFFF)=0;
	virtual RESULT removeFlags(unsigned int flagmask, eDVBChannelID chid=eDVBChannelID(), unsigned int orb_pos=0xFFFFFFFF)=0;
	virtual RESULT removeFlags(unsigned int flagmask, int dvb_namespace=-1, int tsid=-1, int onid=-1, unsigned int orb_pos=0xFFFFFFFF)=0;
	virtual RESULT addChannelToList(const eDVBChannelID &id, iDVBFrontendParameters *feparm)=0;
	virtual RESULT removeChannel(const eDVBChannelID &id)=0;
	
	virtual RESULT getChannelFrontendData(const eDVBChannelID &id, ePtr<iDVBFrontendParameters> &parm)=0;
	
	virtual RESULT addService(const eServiceReferenceDVB &reference, eDVBService *service)=0;
	virtual RESULT getService(const eServiceReferenceDVB &reference, ePtr<eDVBService> &service)=0;
	virtual RESULT flush()=0;

	virtual RESULT getBouquet(const eServiceReference &ref,  eBouquet* &bouquet)=0;

	virtual RESULT startQuery(ePtr<iDVBChannelListQuery> &query, eDVBChannelQuery *q, const eServiceReference &source)=0;
};

#endif  // SWIG

class iDVBFrontendParameters: public iObject
{
#ifdef SWIG
	iDVBFrontendParameters();
	~iDVBFrontendParameters();
#endif
public:
	enum { flagOnlyFree = 1 };
	virtual SWIG_VOID(RESULT) getSystem(int &SWIG_OUTPUT) const = 0;
	virtual SWIG_VOID(RESULT) getDVBS(eDVBFrontendParametersSatellite &SWIG_OUTPUT) const = 0;
	virtual SWIG_VOID(RESULT) getDVBC(eDVBFrontendParametersCable &SWIG_OUTPUT) const = 0;
	virtual SWIG_VOID(RESULT) getDVBT(eDVBFrontendParametersTerrestrial &SWIG_OUTPUT) const = 0;
	virtual SWIG_VOID(RESULT) getFlags(unsigned int &SWIG_OUTPUT) const = 0;
#ifndef SWIG
	virtual SWIG_VOID(RESULT) calculateDifference(const iDVBFrontendParameters *parm, int &, bool exact) const = 0;
	virtual SWIG_VOID(RESULT) getHash(unsigned long &) const = 0;
	virtual SWIG_VOID(RESULT) calcLockTimeout(unsigned int &) const = 0;
#endif
};
SWIG_TEMPLATE_TYPEDEF(ePtr<iDVBFrontendParameters>, iDVBFrontendParametersPtr);

#define MAX_DISEQC_LENGTH  16

class eDVBDiseqcCommand
{
#ifndef SWIG
public:
#endif
	int len;
	__u8 data[MAX_DISEQC_LENGTH];
#ifdef SWIG
public:
#endif
	void setCommandString(const char *str);
};

class iDVBSatelliteEquipmentControl;
class eSecCommandList;

class iDVBFrontend_ENUMS
{
#ifdef SWIG
	iDVBFrontend_ENUMS();
	~iDVBFrontend_ENUMS();
#endif
public:
	enum { feSatellite=1, feCable=2, feTerrestrial=4, feSatellite2=8, feTerrestrial2=16 };
	enum { stateIdle, stateTuning, stateFailed, stateLock, stateLostLock, statePreClose, statePendingClose, stateClosed };
	enum { toneOff, toneOn, toneUnknown };
	enum { voltageOff, voltage13, voltage18, voltage13_5, voltage18_5 };
	enum { bitErrorRate, signalPower, signalQuality, locked, synced, frontendNumber, signalQualitydB };
	enum { canDVBS2Multistream = 1 };
};

typedef std::map<std::string, int> FrontendDataMap;

SWIG_IGNORE_ENUMS(iDVBFrontend);
class iDVBFrontend: public iDVBFrontend_ENUMS, public iObject
{
public:
	virtual RESULT getFrontendType(int &SWIG_OUTPUT)=0;
	virtual RESULT getTunedType(int &SWIG_OUTPUT)=0;
	virtual RESULT tune(const iDVBFrontendParameters &where)=0;
	virtual int closeFrontend(bool force = false, bool no_delayed = false)=0;
	virtual void reopenFrontend()=0;
#ifndef SWIG
	virtual RESULT connectStateChange(const sigc::slot1<void,iDVBFrontend*> &stateChange, ePtr<eConnection> &connection)=0;
#endif
	virtual RESULT getState(int &SWIG_OUTPUT)=0;
	virtual RESULT setTone(int tone)=0;
	virtual RESULT setVoltage(int voltage, iDVBFrontend *child_fe=NULL)=0;
	virtual RESULT sendDiseqc(const eDVBDiseqcCommand &diseqc)=0;
	virtual RESULT sendToneburst(int burst)=0;
#ifndef SWIG
	virtual RESULT setSEC(iDVBSatelliteEquipmentControl *sec)=0;
	virtual RESULT setSecSequence(eSecCommandList &list)=0;
#endif
	virtual int readFrontendData(int type)=0;
	virtual RESULT getFrontendStatus(FrontendDataMap &INOUT)=0;
	virtual RESULT getTransponderData(FrontendDataMap &INOUT, bool original)=0;
	virtual RESULT getFrontendData(FrontendDataMap &INOUT)=0;
	virtual eSignal1<void,iDVBFrontend*> &getStateChangeSignal()=0;
#ifndef SWIG
	virtual RESULT getData(int num, long &data)=0;
	virtual RESULT setData(int num, long val)=0;
		/* 0 means: not compatible. other values are a priority. */
	virtual int isCompatibleWith(ePtr<iDVBFrontendParameters> &feparm)=0;
#endif
	virtual int getCapabilities() const = 0;
};
SWIG_TEMPLATE_TYPEDEF(ePtr<iDVBFrontend>, iDVBFrontendPtr);

#ifndef SWIG
class iDVBSatelliteEquipmentControl: public iObject
{
public:
	virtual RESULT prepare(iDVBFrontend &frontend, dvb_frontend_parameters &parm, const eDVBFrontendParametersSatellite &sat, int frontend_id, unsigned int timeout)=0;
	virtual void prepareClose(iDVBFrontend &frontend, bool typeChanged=false)=0;
	virtual int canTune(const eDVBFrontendParametersSatellite &feparm, iDVBFrontend *fe, int frontend_id, int *highest_score_lnb=0)=0;
	virtual void setRotorMoving(int slotid, bool)=0;
};
#endif // SWIG

SWIG_IGNORE(iDVBChannel);
class iDVBChannel: public iObject
{
public:
		/* direct frontend access for raw channels and/or status inquiries. */
	virtual SWIG_VOID(RESULT) getFrontend(ePtr<iDVBFrontend> &SWIG_OUTPUT)=0;
	virtual RESULT requestTsidOnid(eSlot1<void, int> &callback) { E_UNUSED(callback); return -1; }
	virtual int reserveDemux() { return -1; }
#ifndef SWIG
	enum
	{
		state_idle,        /* not yet tuned */
		state_tuning,      /* currently tuning (first time) */
		state_failed,      /* tuning failed. */
		state_unavailable, /* currently unavailable, will be back without further interaction */
		state_ok,          /* ok */
		state_last_instance, /* just one reference to this channel is left */
		state_release      /* channel is being shut down. */
	};
	virtual RESULT getState(int &)=0;

	virtual RESULT getCurrentFrontendParameters(ePtr<iDVBFrontendParameters> &)=0;
	enum 
	{
		evtPreStart, evtEOF, evtSOF, evtFailed
	};
	virtual RESULT connectStateChange(const sigc::slot1<void,iDVBChannel*> &stateChange, ePtr<eConnection> &connection)=0;
	virtual RESULT connectEvent(const sigc::slot2<void,iDVBChannel*,int> &eventChange, ePtr<eConnection> &connection)=0;
	virtual RESULT connectSourceEvent(const sigc::slot2<void,int,std::string> &sourceEventChange, ePtr<eConnection> &connection){return -1;};

		/* demux capabilities */
	enum
	{
		capDecode = 1,
		/* capCI = 2 */
		capNoDescrambler = 4
	};
	virtual RESULT getDemux(ePtr<iDVBDemux> &demux, int cap=0)=0;
	
		/* use count handling */
	virtual void AddUse() = 0;
	virtual void ReleaseUse() = 0;
#endif
};
SWIG_TEMPLATE_TYPEDEF(eUsePtr<iDVBChannel>, iDVBChannelPtr);

#ifndef SWIG
	/* signed, so we can express deltas. */
	
typedef long long pts_t;

class iFilePushScatterGather;
class iTSMPEGDecoder;

	/* note that a cue sheet describes the logical positions. thus 
	   everything is specified in pts and not file positions */

	/* implemented in dvb.cpp */
class eCueSheet: public iObject, public sigc::trackable
{
	DECLARE_REF(eCueSheet);
public:
	eCueSheet();
	
			/* frontend */
	void seekTo(int relative, const pts_t &pts);
	
	void clear();
	void addSourceSpan(const pts_t &begin, const pts_t &end);
	void commitSpans();
	
	void setSkipmode(const pts_t &ratio); /* 90000 is 1:1 */
	void setDecodingDemux(iDVBDemux *demux, iTSMPEGDecoder *decoder);
	
			/* frontend and backend */
	eRdWrLock m_lock;
	
			/* backend */
	enum { evtSeek, evtSkipmode, evtSpanChanged };
	RESULT connectEvent(const sigc::slot1<void, int> &event, ePtr<eConnection> &connection);

	std::list<std::pair<pts_t,pts_t> > m_spans;	/* begin, end */
	std::list<std::pair<int, pts_t> > m_seek_requests; /* relative, delta */
	pts_t m_skipmode_ratio;
	sigc::signal1<void,int> m_event;
	ePtr<iDVBDemux> m_decoding_demux;
	ePtr<iTSMPEGDecoder> m_decoder;
};

class iDVBPVRChannel: public iDVBChannel
{
public:
	enum
	{
		state_eof = state_release + 1  /* end-of-file reached. */
	};
	
		/* FIXME: there are some very ugly buffer-end and ... related problems */
		/* so this is VERY UGLY. 
		
		   ok, it's going to get better. but still...*/
	virtual RESULT playFile(const char *file) = 0;
	virtual void stopFile() = 0;
	
	/* new interface */
	virtual RESULT playSource(ePtr<iTsSource> &source, const char *priv=NULL) = 0;
	virtual void stopSource() = 0;
	
	virtual void setCueSheet(eCueSheet *cuesheet) = 0;
	
	virtual RESULT getLength(pts_t &pts) = 0;
	
		/* we explicitely ask for the decoding demux here because a channel
		   can be shared between multiple decoders.
		*/
	virtual RESULT getCurrentPosition(iDVBDemux *decoding_demux, pts_t &pos, int mode) = 0;
		/* skipping must be done with a cue sheet */
};

class iDVBSectionReader;
class iDVBPESReader;
class iDVBTSRecorder;
class iTSMPEGDecoder;

class iDVBDemux: public iObject
{
public:
	virtual RESULT createSectionReader(eMainloop *context, ePtr<iDVBSectionReader> &reader)=0;
	virtual RESULT createPESReader(eMainloop *context, ePtr<iDVBPESReader> &reader)=0;
	virtual RESULT createTSRecorder(ePtr<iDVBTSRecorder> &recorder)=0;
	virtual RESULT getMPEGDecoder(ePtr<iTSMPEGDecoder> &reader, int decoder_id=0)=0;
	virtual RESULT getSTC(pts_t &pts, int num=0)=0;
	virtual RESULT getCADemuxID(uint8_t &id)=0;
	virtual RESULT flush()=0;
	virtual int openDVR(int flags)=0;
};

class iTSMPEGDecoder: public iObject
{
public:
	enum { pidDisabled = -1 };
		/** Set Displayed Video PID and type */
	virtual RESULT setVideoPID(int vpid, int type)=0;

	enum { af_MPEG, af_AC3, af_DTS, af_AAC, af_DTSHD };
		/** Set Displayed Audio PID and type */
	virtual RESULT setAudioPID(int apid, int type)=0;

	enum { ac_left, ac_stereo, ac_right };
		/** Set Displayed Audio Channel */
	virtual RESULT setAudioChannel(int channel)=0;
	virtual int getAudioChannel()=0;

	virtual RESULT setPCMDelay(int delay)=0;
	virtual int getPCMDelay()=0;
	virtual RESULT setAC3Delay(int delay)=0;
	virtual int getAC3Delay()=0;

		/** Set Displayed Videotext PID */
	virtual RESULT setTextPID(int vpid)=0;

		/** Set Sync mode to PCR */
	virtual RESULT setSyncPCR(int pcrpid)=0;
	enum { sm_Audio, sm_Video };

		/** Apply settings but don't change state */
	virtual RESULT set()=0;
		/* all those apply settings, then transition to the given state */

		/** play */
	virtual RESULT play()=0;
		/** Freeze frame. */
	virtual RESULT pause()=0;

		/** fast forward by skipping frames. 0 is disabled, 2 is twice-the-speed, ... */
	virtual RESULT setFastForward(int skip=0)=0;

		/** Slow Motion by repeating pictures */
	virtual RESULT setSlowMotion(int repeat)=0;

		/** Display any complete data as fast as possible */
	virtual RESULT setTrickmode()=0;
	
	virtual RESULT getPTS(int what, pts_t &pts) = 0;

	virtual RESULT showSinglePic(const char *filename) = 0;

	virtual RESULT setRadioPic(const std::string &filename) = 0;

	struct videoEvent
	{
		enum { eventUnknown = 0,
			eventSizeChanged = VIDEO_EVENT_SIZE_CHANGED,
			eventFrameRateChanged = VIDEO_EVENT_FRAME_RATE_CHANGED,
			eventProgressiveChanged = 16
		} type;
		unsigned char aspect;
		unsigned short height;
		unsigned short width;
		bool progressive;
		unsigned short framerate;
	};

	virtual RESULT connectVideoEvent(const sigc::slot1<void, struct videoEvent> &event, ePtr<eConnection> &connection) = 0;
	virtual RESULT connectStateEvent(const sigc::slot1<void, int> &event, ePtr<eConnection> &connection) = 0;

	virtual int getVideoWidth() = 0;
	virtual int getVideoHeight() = 0;
	virtual int getVideoProgressive() = 0;
	virtual int getVideoFrameRate() = 0;
	virtual int getVideoAspect() = 0;
	virtual int getState() = 0;
	virtual const char *getEotf() = 0;
};

#endif //SWIG
#endif
