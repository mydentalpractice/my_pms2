

import datetime 
from datetime import timedelta



import time

import random

import pytz
from pytz import timezone

getdt    = lambda dt:dt if(dt != None) else datetime.date.today()
getnulldt = lambda dt:dt if(dt != None) else ""
getid    = lambda xid :xid if((xid != None)&(xid != "")&(xid != "None")) else 0
getnegid = lambda xid :xid if((xid != None)&(xid != "")&(xid != "None")) else -1
getpage  = lambda page:page if((page != None)&(page != "")&(page != "0")) else 0
getpage1  = lambda page:page if((page != None)&(page != "")&(page != "0")) else 1
getvalue = lambda amount: amount if((amount != None)&(amount != "")&(amount != "None")) else 0
getstring = lambda text: text if((text != None)&(text != "")&(text != "None")) else ""
getbool =   lambda text: text if((text != None)&(text != "")&(text != "None")) else False
getboolean =   lambda text: True if((text != None)&(text != "")&(text != "None")&((text == "True")|(text == "true")|(text==True)|(text=="1")|(text=="on")|(text=="On"))) else False


getyesno = lambda text: "yes" if((text == "True")) else ("no" if(text=="False") else "yes")
gettruefalse = lambda text: "True" if((text == "yes")) else ("False" if(text=="no") else "True")

#getmode    = lambda mode:mode if(mode != None) else 'None'

fmt = "%Y-%m-%d %H:%M:%S"



def getregioncodefromcity(db,city):
        rgn = db((db.groupregion.region == city) & (db.groupregion.is_active == True)).select()
        return rgn[0].groupregion if(len(rgn) != 0) else "JAI"

def getregionidfromcity(db,city):
        rgn = db((db.groupregion.region == city) & (db.groupregion.is_active == True)).select()
        return rgn[0].id if(len(rgn) != 0) else 0

#this will convert %d/%m/%Y %I:%M %p  into %d/%m/%Y %H:%M

def convert12to24clock(timestr):
        d = getdatefromstring(timestr, "%d/%m/%Y %I:%M %p")
        e = getstringfromdate(d,"%d/%m/%Y %H:%M")
        return e

def convert24to12clock(timestr):
        
        if((timestr.upper().find("AM") == -1)|(timestr.upper().find("PM") == -1)):
                return timestr
        
        d = datetime.datetime.strptime(timestr,"%H:%M")

        e = d.strftime("%I:%M %p")
        return e

        
def getkeyvalue(jobj, key1, defval):
        

        keys = jobj.keys()

        for key in keys:
                if(key.lower() == key1.lower()):
                        return jobj.get(key,defval)


        return defval


def setcookies(response):
        response.cookies[response.session_id_name] =response.session_id
        response.cookies[response.session_id_name]["Secure"] =  True
        response.cookies[response.session_id_name]["HttpOnly"] =  True        
            
        
        return True

def getstringfromdate(dateobj,fmt):
        if(dateobj == None):
                return ""
        dtstr = dateobj.strftime(fmt)
        
        return dtstr

def getdatefromstring(strdate,fmt):
        if(strdate == ""):
                return datetime.date.today()
        
        dt = datetime.datetime.strptime(strdate,fmt)
        return dt
        
def gettimefromstring(strtime,fmt):
        if(strtime == ""):
                return None
        
        t = time.strptime(strtime, fmt)
        return t

def getstringfromtime(timeobj, fmt):
        if(timeobj == None):
                return ""
        strtime = timeobj.strftime(fmt)
        
       
        return strtime


#this returns local current (IST) date  as datetime object
def getISTFormatCurrentLocatDate():
        loctime = getISTCurrentLocatTime()
        dttodaydate =   datetime.datetime.strptime(loctime.strftime("%d") + "/" + loctime.strftime("%m") + "/" + loctime.strftime("%Y"),\
                                                   "%d/%m/%Y")
        str1 = getstringfromdate(dttodaydate,"%d/%m/%Y")
        dt1 = getdatefromstring(str1,"%d/%m/%Y")
        
        return dt1


#this returns local current (IST) date and time as datetime object
def getISTFormatCurrentLocatTime():
        loctime = getISTCurrentLocatTime()
        dttodaydate =   datetime.datetime.strptime(loctime.strftime("%d") + "/" + loctime.strftime("%m") + "/" + loctime.strftime("%Y") + \
                                                   " " + loctime.strftime("%H")+ ":" + loctime.strftime("%M") + ":" + loctime.strftime("%S"),\
                                                   "%d/%m/%Y %H:%M:%S")
        return dttodaydate

def getISTFromUCT(uctdate):
        istdate = uctdate.astimezone(timezone('Asia/Kolkata'))
        return istdate

def getUCTFromIST(istdate):
        uctdate = istdate.astimezone(timezone('UCT'))
        return uctdate

def getISTFromUCTCurrentLocatTime():
        nowUCT = datetime.datetime.now(timezone('UTC'))  # this will give UTC current time
        nowISTfromUCT = nowUCT.astimezone(timezone('Asia/Kolkata'))  # this onverts UTC time to IST
        #nowISTfromUCTstr = nowISTfromUCT.strftime(fmt) 
        return nowISTfromUCT
        
def getZoneCurrentLocalTime(zone):
        nowZone = datetime.datetime.now(timezone(zone)) 
        return nowZone

def getUCTCurrentLocalTime():
        nowUCT = datetime.datetime.now(timezone('UTC'))  # this will give UTC current time
        #nowUCTstr = nowUCT.strftime(fmt)
        return nowUCT
        
def getISTCurrentLocatTime():
        nowIST = datetime.datetime.now(timezone('Asia/Kolkata'))  # this will give India Local Time
        #nowiststr = nowist.strftime(fmt)
        return nowIST
    


def changeinnotes(currnotes, newnotes):
        retVal = True
        if(getstring(currnotes).strip().upper() == getstring(newnotes).strip().upper()):
                retVal = False
        return retVal




def logapptnotes(db,chiefcomplaint,notes,apptid):
    
        treatment = ""
        doctorname = ""
        providerid = 0
        doctorid = 0
        patientid = 0
        memberid = 0
        apptdate = getISTCurrentLocatTime()
        
        appts = db(db.vw_appointments.id == apptid).select(db.vw_appointments.provider,db.vw_appointments.patient,db.vw_appointments.patientmember,db.vw_appointments.doctor,db.vw_appointments.docname,db.vw_appointments.f_start_time)
        if(len(appts)>0):
                providerid = int(getid(appts[0].provider))
                patientid  = int(getid(appts[0].patient))
                memberid = int(getid(appts[0].patientmember))
                doctorid = int(int(getid(appts[0].doctor)))
                doctorname = getstring(appts[0].docname)
                apptdate   = appts[0].f_start_time
                
        if((notes != None) & (notes != "")):
                csr = getISTCurrentLocatTime().strftime('%d/%m/%Y %I:%M %p') + "\r\n" + "Appointment:" + apptdate.strftime('%d/%m/%Y %I:%M %p') + "\r\n" + chiefcomplaint + "\r\n" + notes
                csrid = db.casereport.insert(patientid = patientid, memberid = memberid,providerid=providerid, doctorid=doctorid,appointmentid=apptid, \
                                             casereport = csr, is_active=True,\
                                             created_on = getISTFormatCurrentLocatTime(), created_by = providerid, \
                                             modified_on = getISTFormatCurrentLocatTime(), modified_by = providerid)
            
        return
    
def lognotes(db,notes,treatmentid,providerid=0,patientid=0,memberid=0,doctorid=0):

        treatment = ""
        doctorname = ""

        ts = db(db.vw_treatmentlist.id == treatmentid).select(db.vw_treatmentlist.treatment,db.vw_treatmentlist.providerid,db.vw_treatmentlist.doctorid,\
                                                              db.vw_treatmentlist.patientid,db.vw_treatmentlist.memberid,db.vw_treatmentlist.doctorname)
     
        if(len(ts)>0):
                treatment= getstring(ts[0].treatment)
                providerid = int(getid(ts[0].providerid))
                doctorid = int(getid(ts[0].doctorid))
                patientid = int(getid(ts[0].patientid))
                memberid = int(getid(ts[0].memberid))
                doctorname = getstring(ts[0].doctorname)
   
        if((notes != None) & (notes != "")):
                csrdate = getISTCurrentLocatTime().strftime('%d/%m/%Y %I:%M %p')
                csr = csrdate + "\r\n" + ("" if(len(treatment)==0) else ("Treatment Number:"  + treatment + "\r\n"))
                csr = csr + ("" if(len(doctorname) == 0) else ("Doctor:" + doctorname + "\r\n"))
                csr = csr + notes
                csrid = db.casereport.insert(patientid = patientid, memberid=memberid,providerid=providerid, doctorid=doctorid, casereport = csr, is_active=True,\
                                              created_on =  getISTFormatCurrentLocatTime(), created_by = providerid,treatmentid=treatmentid,\
                                              modified_on =  getISTFormatCurrentLocatTime(), modified_by = providerid)        
        
        
        return

def getdefaultdoctor(db,providerid):

    doctorid = 0
    
    #default attending doctor to owner doctor
    r = db((db.doctor.providerid == providerid) & (db.doctor.practice_owner == True) & (db.doctor.is_active == True)).select()
    if(len(r) > 0):
        doctorid = r[0].id
    return doctorid

def getgridpage(requestvars):
    
    page = 1
    if(len(requestvars)==0):
        page = 1
    elif(requestvars == None):
        page = 1
    elif(requestvars.page == None):
        page = 1
    else:
        page = int(requestvars.page)
        
    return page


def getLoggedProvider(db,auth):
    
    id = auth.user_id
    sitekey = auth.user.sitekey    
    rows = db(db.provider.sitekey == sitekey).select()
    
    if(len(rows) > 0):
        providerid = rows[0].id
    else:
        providerid = 0    
        
    return providerid

def showerror(header,mssg,returnurl):
    redirect(URL('default','showerror',args=[header,mssg,returnurl]))
    return

def getrenewals(db,fromrp,torp):
    
    renewals = 0
    fromdt = datetime.date.today() + timedelta(days=fromrp)
    todt   = datetime.date.today() + timedelta(days=torp) 
    renewals = db((db.patientmember.is_active == True)  & (db.patientmember.hmopatientmember == True) & (db.patientmember.duedate >= fromdt) & (db.patientmember.duedate < todt)).count()
    
    return renewals

def gettotalmembers(db):
    webmembers = db(db.webmember.is_active == True).count()
    return webmembers

def getregisteredmembers(db,fromdays, todays):
    
    webmembers = 0
    if(todays == None):
        fromdt = datetime.date.today() - timedelta(days=fromdays)
        todt = None
        webmembers = db((db.webmember.is_active == True) & \
                        ((db.webmember.status == 'No_Attempt') | (db.webmember.status == 'Attempting')) & \
                        (db.webmember.created_on <= fromdt)).count()
    else:
        fromdt = datetime.date.today() - timedelta(days=fromdays)
        todt   = datetime.date.today() + timedelta(days=todays) 
        webmembers = db((db.webmember.is_active == True) & \
                        ((db.webmember.status == 'No_Attempt') | (db.webmember.status == 'Attempting')) & \
                        (db.webmember.created_on > fromdt) & (db.webmember.created_on <= todt)).count()
    
    return webmembers

def getcompletedmembers(db):
    completed = 0
    completed   =  db((db.webmember.status == 'Completed') & (db.webmember.is_active == True)).count()
    return completed

def getenrolledmembers(db):
    enrolled    =  db((db.patientmember.status == 'Enrolled') & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).count()    
    return enrolled

def getcompanies(db):
    companies = db((db.company.is_active == True)).count()
    return companies

def getproviders(db):
    providers = db(db.provider.is_active == True).count()   
    return providers

def getplans(db):
     plans = db(db.hmoplan.is_active == True).count()     
     return plans

#if this is a webadming, then this is a super provider
#providerid > 0, valid provider
#providerid = 0, super provider webadmin
#providerid < 0, invalid user
#@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
#@auth.requires_login()
def getprovider(auth,db):
        
    providerid = -1
    
    #determine if logged in user is a provider or webadmin
    #return valid provider or webadmin or -1
    provider = ""
    providername = ""
    registration = ""
    practicename = ""
    practiceaddress = ""
    email = ""
    cell = ""
    rlgrpolicynumber = ""
    rlgprovider = False
    regionid = 0
    planid = 0
    latitude = ""
    longitude = ""
    locationurl = ""
    
    
    if(auth.has_membership('provider')):
        rows = db((db.provider.sitekey == auth.user.sitekey) & (db.provider.is_active == True)).select()
        if(len(rows)==1):
            providerid = int(getid(rows[0].id))
            if(providerid == 0):
                providerid = -1
            else:
                rlgprov = db(db.rlgprovider.providerid == providerid).select()   
                urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.relgrpolicynumber)
                rlgrpolicynumber =  "9999" if(len(urlprops) == 0) else getstring(urlprops[0].relgrpolicynumber)
                rlgprovider = False if(len(rlgprov) == 0) else getboolean(rlgprov[0].is_active)
                regionid =  0 if(len(rlgprov) == 0) else int(rlgprov[0].regionid)
                planid = 0 if(len(rlgprov) == 0) else int(rlgprov[0].planid)
                provider = getstring(rows[0]["provider"])
                providername = getstring(rows[0]["providername"])  
                registration = getstring(rows[0]["registration"])
                practicename =  getstring(rows[0]["pa_practicename"])
                practiceaddress =  getstring(rows[0]["pa_practiceaddress"])
                email =  getstring(rows[0]["email"])
                cell =  getstring(rows[0]["cell"])
                longitude = getstring(rows[0]["pa_longitude"])
                latitude = getstring(rows[0]["pa_latitude"])
                locationurl = getstring(rows[0]["pa_locationurl"])
                
                
        else:
            providerid = -1
            
    if(auth.has_membership('webadmin')):
        providerid = 0
        provider = ''
        providername = getstring(auth.user.first_name)  + " " + getstring(auth.user.last_name)
    
    
    return dict(providerid=providerid,provider=provider,providername=providername,registration=registration,
        practicename=practicename,practiceaddress=practiceaddress,email=email,cell=cell,rlgrpolicynumber=rlgrpolicynumber,
        rlgprovider=rlgprovider,regionid=regionid,planid=planid)

def getproviderfromid(db,aproviderid):
    
    providerid = int(getid(aproviderid))
    
    

    provider = ""
    providername  = ""
    registration = ""
    practicename =  ""
    practiceaddress =  ""
    email =  ""
    cell =  ""

    rlgrpolicynumber =  ""
    rlgprovider = False
    regionid =  0 
    planid = 0   
    
    latitude = ""
    longitude = ""
    locationurl = ""
    
    city = ""
    st = ""
    pin = ""


    if(providerid > 0):
        rows = db((db.provider.id == providerid) & (db.provider.is_active == True)).select()
        if(len(rows)==1):
                
                provider = getstring(rows[0]["provider"])
                providername = getstring(rows[0]["providername"])  
                registration = getstring(rows[0]["registration"])
              
                urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.relgrpolicynumber)
                rlgrpolicynumber =  "9999" if(len(urlprops) == 0) else getstring(urlprops[0].relgrpolicynumber)

                rlgprov = db(db.rlgprovider.providerid == providerid).select() 
                rlgprovider = False if(len(rlgprov) == 0) else True
                regionid =  0 if(len(rlgprov) == 0) else int(rlgprov[0].regionid)
                planid = 0 if(len(rlgprov) == 0) else int(rlgprov[0].planid)
                
                provider = getstring(rows[0]["provider"])
                providername = getstring(rows[0]["providername"])  
                practicename =  getstring(rows[0]["pa_practicename"])
                practiceaddress =  getstring(rows[0]["pa_practiceaddress"])
                city = getstring(rows[0]["city"])
                st = getstring(rows[0]["st"])
                pin = getstring(rows[0]["pin"])
                email =  getstring(rows[0]["email"])
                cell =  getstring(rows[0]["cell"])
                longitude = getstring(rows[0]["pa_longitude"])
                latitude = getstring(rows[0]["pa_latitude"])
                locationurl = getstring(rows[0]["pa_locationurl"])
            
            
    return dict(providerid=providerid,provider=provider,providername=providername,registration=registration,
                practicename=practicename,practiceaddress=practiceaddress,city=city,st=st,pin=pin,email=email,cell=cell,rlgrpolicynumber=rlgrpolicynumber,
                rlgprovider=rlgprovider,regionid=regionid,planid=planid,longitude=longitude,latitude=latitude,locationurl=locationurl)
                
   
   
   
def dashboard(db,session,providerid):
    
    oneday = datetime.timedelta(days=1)
    today = datetime.date.today()
    tomorrow = today + oneday
    
    
    members = db(((db.vw_memberpatientlist.providerid == providerid)&\
                    (db.vw_memberpatientlist.hmopatientmember == True)&\
                    (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt)&\
                    (db.vw_memberpatientlist.is_active == True))).count()
      
    exmembers = db(((db.vw_memberpatientlist.providerid == providerid)&\
                    (db.vw_memberpatientlist.hmopatientmember == True)&\
                    (datetime.date.today().strftime('%Y-%m-%d') > db.vw_memberpatientlist.premenddt)&\
                    (db.vw_memberpatientlist.is_active == True))).count()
  
    nonmembers = db((db.vw_memberpatientlist.providerid == providerid) & \
                   (db.vw_memberpatientlist.is_active == True) & \
                   (db.vw_memberpatientlist.hmopatientmember == False)).count()

    newmembers = db(((db.vw_memberpatientlist.providerid == providerid)&\
                        (db.vw_memberpatientlist.hmopatientmember == True)&\
                        (db.vw_memberpatientlist.newmember == True) & \
                        (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt)&\
                        (db.vw_memberpatientlist.is_active == True))).count()
        

      
    images = db((db.dentalimage.provider == providerid) & (db.dentalimage.is_active == True)).count()
    treatmentplans = db((db.treatmentplan.provider == providerid) & (db.treatmentplan.is_active == True)).count()
    treatments = db((db.treatment.provider == providerid) & (db.treatment.is_active == True)).count()
    appointments = db((db.t_appointment.provider == providerid) & (db.t_appointment.is_active == True)).count()
    
 

    #ds= db((db.t_appointment.provider == providerid) &  (db.t_appointment.is_active == True)).select()
    
    todayappts = db((db.t_appointment.provider == providerid) & ((db.t_appointment.f_start_time.day() == today.day) & (db.t_appointment.f_start_time.month() == today.month) & (db.t_appointment.f_start_time.year() == today.year)) & \
                                                                 (db.t_appointment.is_active == True)).count()
    tomorrowappts = db((db.t_appointment.provider == providerid) & ((db.t_appointment.f_start_time.day() == tomorrow.day) & (db.t_appointment.f_start_time.month() == tomorrow.month) & (db.t_appointment.f_start_time.year() == tomorrow.year)) & \
                                                                 (db.t_appointment.is_active == True)).count()

    session.members = members
    session.exmembers = exmembers
    session.nonmembers = nonmembers
    session.newmembers = newmembers
    session.images = images
    session.treatmentplans = treatments
    session.appointments = appointments
    session.todayappts = todayappts
    session.tomorrowappts = tomorrowappts
    
      
    
    
    return dict()



def getdocdatetime(apptdt, doctime):
    
    dtobj = None
    
    if(getstring(doctime) != ""):
        str1 = str(apptdt.year) + "-" + str(apptdt.month) + "-" + str(apptdt.day) + " " + doctime
        dtobj = datetime.datetime.strptime(str1, "%Y-%m-%d %I:%M %p")
    
    return dtobj


def validappointment(db,doctorid, startappt):
    retval  = False
    
    day_chk = False
    del_chk = False
    
    starttime1 = "01:01 AM"
    endtime1 = "01:01 AM"
    starttime2 = "01:01 AM"
    endtime2 = "01:01 AM"
    
    docstarttime1 = None
    docendtime1 = None
    docstarttime1 = None
    docendtime1 = None
    
    #doctor timings
    dt = db((db.doctortiming.doctor == doctorid) & (db.doctortiming.is_active == True)).select()
    
    if(len(dt)>0):
        apptday = startappt.weekday()
        
        
        if(apptday == 0):    # Mon
            day_chk = getboolean(dt[0].mon_day_chk)
            del_chk = getboolean(dt[0].mon_del_chk)
            if((day_chk == True) & (del_chk == False)):
                starttime1 = getstring(dt[0].mon_starttime_1)
                endtime1 = getstring(dt[0].mon_endtime_1)
                starttime2 = getstring(dt[0].mon_starttime_2)
                endtime2 = getstring(dt[0].mon_endtime_2)
                
            
        elif(apptday == 1):  # Tue
            day_chk = getboolean(dt[0].tue_day_chk)
            del_chk = getboolean(dt[0].tue_del_chk)
            if((day_chk == True) & (del_chk == False)):
                starttime1 = getstring(dt[0].tue_starttime_1)
                endtime1 = getstring(dt[0].tue_endtime_1)
                starttime2 = getstring(dt[0].tue_starttime_2)
                endtime2 = getstring(dt[0].tue_endtime_2)
                
        
        elif(apptday == 2):  # Wed
            day_chk = getboolean(dt[0].wed_day_chk)
            del_chk = getboolean(dt[0].wed_del_chk)
            if((day_chk == True) & (del_chk == False)):
                starttime1 = getstring(dt[0].wed_starttime_1)
                endtime1 = getstring(dt[0].wed_endtime_1)
                starttime2 = getstring(dt[0].wed_starttime_2)
                endtime2 = getstring(dt[0].wed_endtime_2)
                
            
            
        elif(apptday == 3):  # Thu
            day_chk = getboolean(dt[0].thu_day_chk)
            del_chk = getboolean(dt[0].thu_del_chk)
            if((day_chk == True) & (del_chk == False)):
                starttime1 = getstring(dt[0].thu_starttime_1)
                endtime1 = getstring(dt[0].thu_endtime_1)
                starttime2 = getstring(dt[0].thu_starttime_2)
                endtime2 = getstring(dt[0].thu_endtime_2)
    
        elif(apptday == 4):  # Fri
            day_chk = getboolean(dt[0].fri_day_chk)
            del_chk = getboolean(dt[0].fri_del_chk)
            if((day_chk == True) & (del_chk == False)):
                starttime1 = getstring(dt[0].fri_starttime_1)
                endtime1 = getstring(dt[0].fri_endtime_1)
                starttime2 = getstring(dt[0].fri_starttime_2)
                endtime2 = getstring(dt[0].fri_endtime_2)
        
        elif(apptday == 5):  # Sat
            day_chk = getboolean(dt[0].sat_day_chk)
            del_chk = getboolean(dt[0].sat_del_chk)
            if((day_chk == True) & (del_chk == False)):
                starttime1 = getstring(dt[0].sat_starttime_1)
                endtime1 = getstring(dt[0].sat_endtime_1)
                starttime2 = getstring(dt[0].sat_starttime_2)
                endtime2 = getstring(dt[0].sat_endtime_2)
            
        elif(apptday == 6):  # Sun
            day_chk = getboolean(dt[0].sun_day_chk)
            del_chk = getboolean(dt[0].sun_del_chk)
            if((day_chk == True) & (del_chk == False)):
                starttime1 = getstring(dt[0].sun_starttime_1)
                endtime1 = getstring(dt[0].sun_endtime_1)
                starttime2 = getstring(dt[0].sun_starttime_2)
                endtime2 = getstring(dt[0].sun_endtime_2)
            
        else:
            docstarttime1 = None
            docendtime1 = None
            docstarttime1 = None
            docendtime1 = None
    
        
        docstarttime1 = getdocdatetime(startappt, "01:01 AM" if ((starttime1 == "")|(starttime1 == None)) else starttime1)
        docendtime1 = getdocdatetime(startappt, "01:01 AM" if ((endtime1 == "")|(endtime1 == None)) else endtime1)
        docstarttime2 = getdocdatetime(startappt, "01:01 AM" if ((starttime2 == "")|(starttime2 == None)) else starttime2)
        docendtime2 = getdocdatetime(startappt, "01:01 AM" if ((endtime2 == "")|(endtime2 == None)) else endtime2)
    
        retval = False
        if((retval == False) & (docstarttime1 != None) & (startappt >= docstarttime1 ) & (docendtime1 != None) & (startappt <= docendtime1 )):
            retval = True
             
        if((retval == False) & (docstarttime2 != None) & (startappt >= docstarttime2 ) & (docendtime2 != None) & (startappt <= docendtime2 )):
            retval = True
            
    else:
        retval = True
        
    return  retval
    




#treatment can be "" or treatment or treatment phrase
#this function will return a grid fulfilling the query
def gettreatmentgrid(db,page, imagepage, providerid, providername, treatment,memberid=0,patientid=0):
    
    query = (db.vw_treatmentlist.memberid == memberid) if(memberid > 0) else (1==1)
    
    query = query & (db.vw_treatmentlist.patientid == patientid) if(memberid > 0) else query

    query =  (query )
     
    if((treatment == "") | (treatment == None)):
        query = query & ((db.vw_treatmentlist.providerid == providerid) & (db.vw_treatmentlist.is_active == True))
    else:
        query=  query & ((db.vw_treatmentlist.providerid == providerid) & (db.vw_treatmentlist.pattern.like('%' + treatment + '%')) & (db.vw_treatmentlist.is_active == True))


    fields=(db.vw_treatmentlist.patientname,db.vw_treatmentlist.treatment,db.vw_treatmentlist.chiefcomplaint,db.vw_treatmentlist.startdate,db.vw_treatmentlist.dentalprocedure, db.vw_treatmentlist.shortdescription, db.vw_treatmentlist.memberid,
            db.vw_treatmentlist.treatmentplan,db.vw_treatmentlist.status,db.vw_treatmentlist.treatmentcost,db.vw_treatmentlist.memberid,db.vw_treatmentlist.patientid,db.vw_treatmentlist.tplanid)

    headers={
        'vw_treatmentlist.treatment':'Treatment No.',
        'vw_treatmentlist.chiefcomplaint':'Complaint',
        'vw_treatmentlist.patientname':'Patient',
        'vw_treatmentlist.startdate':'Treatment Date',
        'vw_treatmentlist.treatmentcost':'Cost',
                }

    db.vw_treatmentlist.status.readable = False
    db.vw_treatmentlist.treatmentplan.readable = False
    
    db.vw_treatmentlist.memberid.readable = False
    db.vw_treatmentlist.patientid.readable = False
    db.vw_treatmentlist.providerid.readable = False
    db.vw_treatmentlist.is_active.readable = False
    db.vw_treatmentlist.providerid.readable = False

    db.vw_treatmentlist.treatmentcost.readable = False
    db.vw_treatmentlist.tplanid.readable = False
    db.vw_treatmentlist.memberid.readable = False
    
    db.vw_treatmentlist.dentalprocedure.readable = False
    db.vw_treatmentlist.shortdescription.readable = False
    
    
    links = [\
           dict(header=CENTER("Open"), body=lambda row: CENTER(A(IMG(_src="../static/assets/global/img/edit.png",_width=25, _height=25),_href=URL("treatment","update_treatment",vars=dict(page=page,imagepage=imagepage,treatmentid=row.id, providerid=providerid))))),
           #dict(header=CENTER('New'), body=lambda row: CENTER(A(IMG(_src="../static/assets/global/img/png/014-dentist.png",_width=30, _height=30),_href=URL("treatment","new_treatment",vars=dict(page=page,treatmentid=row.id, memberid=row.memberid,patientid=row.patientid, providerid=providerid))))),\
           dict(header=CENTER('Payment'), body=lambda row: CENTER(A(IMG(_src="../static/assets/global/img/payments.png",_width=30, _height=30),_href=URL("payment","create_payment",vars=dict(page=page,tplanid=row.tplanid,providerid=providerid,providername=providername,memberid=row.memberid,patientid=row.patientid))))),\
           dict(header=CENTER('Auth.Rpt.'), body=lambda row: CENTER(A(IMG(_src="../static/assets/global/img/reports.png",_width=30, _height=30),_href=URL("reports","treatmentreport",vars=dict(page=page,treatmentid=row.id,providerid=providerid))))),
           dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="../static/assets/global/img/delete.png",_width=30, _height=30),_href=URL("treatment","delete_treatment",vars=dict(page=page,treatmentid=row.id,  memberid=row.memberid,patientid=row.patientid, providerid=providerid,providername=providername)))))
    ]

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
    returnurl =  URL('treatment', 'list_treatments', vars=dict(page=page,providerid=providerid))
     
    orderby = ~db.vw_treatmentlist.id
    
    maxtextlengths = {'vw_treatmentlist.treatment':50}
       
    form = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        paginate=10,
                        orderby=orderby,
                        maxtextlengths=maxtextlengths,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )
    
    
    
    return form







def modify_cell(cell):
        if((cell == None)|(cell == "")):
                return "0000000000"
        
        cellno = cell.lstrip('0')  # remove leading zero  in case cell  = 078901234544
        if(len(cellno) == 10):     # pure number with no Country code
                cellno = "+91" + cellno 
        elif(not cellno.startswith("91")):
                cellno = "+91" + cellno
        elif(cellno.startswith("91")):
                cellno = "+" + cellno

        return cellno

def addyears(dt,yrs):
        newdt = dt + datetime.timedelta(365*yrs)
        return newdt
        


def isfloat(value):
        try:
                x = float(value)
                return True
        except Exception as e:
                return False
        
def generateackid(base,digits):
        ackid = base
        random.seed(int(time.time()))
        for j in range(0,(digits-len(base))):
                ackid += str(random.randint(0,9))  
        return ackid

def getmessage(db,message_code):
        
        mssgs = db((db.mdpmessages.message_code == message_code)).select()
        
        return "" if(len(mssgs) != 1) else mssgs[0].mdpmessage
        
