
from gluon import current

import os
import json
import datetime
import time
import random
from datetime import timedelta

from string import Template

from applications.my_pms2.modules import common
from applications.my_pms2.modules import mail
from applications.my_pms2.modules import tasks
from applications.my_pms2.modules import status
from applications.my_pms2.modules import cycle
from applications.my_pms2.modules import logger

datefmt = "%d/%m/%Y"
datetimefmt = "%d/%m/%Y %H:%M:%S"

def serializedatetime(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()    
   

class Appointment:
    
    
    
    def __init__(self,db,providerid):
        self.db = db
        self.providerid = providerid
        return     
    
    def appointmentstatus(self):
        
        st = status.APPTSTATUS
        return  json.dumps(st)        
    
    def appointmentduration(self):
        dur = cycle.DURATION
        return json.dumps(dur)
        
        
        
    def isBlocked(self, startdt, enddt,doctorid,clinicid=0):
        
        db = self.db
        
        retval = False
        str1 = datetime.datetime.strftime(startdt, "%Y-%m-%d %H:%M:%S")
        str2 = datetime.datetime.strftime(enddt,  "%Y-%m-%d %H:%M:%S")
    
        if(clinicid == 0):
            appts = db((db.t_appointment.doctor == doctorid)&( str1 >= db.t_appointment.f_start_time)& (str1 <= db.t_appointment.f_end_time) & (db.t_appointment.blockappt == True) & (db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
        else:
            appts = db((db.t_appointment.clinicid==clinicid)&(db.t_appointment.doctor == doctorid)&( str1 >= db.t_appointment.f_start_time)& (str1 <= db.t_appointment.f_end_time) & (db.t_appointment.blockappt == True) & (db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)    
            
        if(len(appts)>0):
            return True
        
        if(clinicid == 0):
            appts = db((db.t_appointment.doctor == doctorid)&( str1 >= db.t_appointment.f_end_time)&(db.t_appointment.blockappt == True)&(db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
        else:
            appts = db((db.t_appointment.clinicid==clinicid)&(db.t_appointment.doctor == doctorid)&( str1 >= db.t_appointment.f_end_time)&(db.t_appointment.blockappt == True)&(db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
            
        
        if(len(appts)>0):
            return False
        
        if(clinicid == 0):
            appts = db((db.t_appointment.doctor == doctorid)&( str1 <= db.t_appointment.f_start_time)&(str2 <= db.t_appointment.f_start_time)&(db.t_appointment.blockappt == True)&(db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
        else:
            appts = db((db.t_appointment.clinicid==clinicid)&(db.t_appointment.doctor == doctorid)&( str1 <= db.t_appointment.f_start_time)&(str2 <= db.t_appointment.f_start_time)&(db.t_appointment.blockappt == True)&(db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)            
            
        if(len(appts)>0):
            return False
        
        
        return retval    
   
    def sms_confirmation(self,appPath,appointmentid,action='create'):
            
            fname = ""
    
            retVal1 = False
            retVal2 = False
            retVal3 = False
            
            db = self.db
            
            appts = db(db.t_appointment.id == appointmentid).select(db.t_appointment.provider,db.t_appointment.doctor,\
                                                                    db.t_appointment.patient,db.t_appointment.f_location,\
                                                                    db.t_appointment.f_patientname,db.t_appointment.cell,\
                                                                    db.t_appointment.f_start_time,db.t_appointment.patientmember)
            
            if(len(appts)==0):
                    return retVal1
            
            
            providerid = int(common.getid(appts[0].provider))
            doctorid = int(common.getid(appts[0].doctor))
            patientid = int(common.getid(appts[0].patient))
            memberid = int(common.getid(appts[0].patientmember))
            location = common.getstring(appts[0].f_location)
            
            pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & ((db.vw_memberpatientlist.patientid == patientid))).select()
            fname = common.getstring(appts[0].f_patientname)        
            patcell = common.modify_cell(common.getstring(appts[0].cell))
            patemail = ""
            if(len(pats)>0):
                    patemail = pats[0].email
                    if(patcell == ""):
                            patcell = common.modify_cell(common.getstring(pats[0].cell))        
    
            provs = db(db.provider.id == providerid).select(db.provider.cell,db.provider.providername,db.provider.telephone,db.provider.email)        
            provcell = common.modify_cell(common.getstring(provs[0].cell)) if(len(provs) > 0 ) else "910000000000"
            provname = common.getstring(provs[0].providername) if(len(provs) > 0 ) else ""
            provtel = common.getstring(provs[0].telephone) if(len(provs) > 0 ) else "910000000000"
            provemail = common.getstring(provs[0].email) if(len(provs) > 0 ) else "x@x.com"
            
            docs = db(db.doctor.id == doctorid).select(db.doctor.cell,db.doctor.name,db.doctor.email,db.doctor.docsms,db.doctor.docemail)
            doccell = common.modify_cell(common.getstring(docs[0].cell)) if(len(docs) > 0 ) else "910000000000"
            docname  = common.getstring(docs[0].name) if(len(docs) > 0 ) else ""
            docemail = common.getstring(docs[0].email) if(len(docs) > 0 ) else "x@x.com"
            docsms =   common.getboolean(docs[0].docsms) if(len(docs) > 0 ) else False
            docemailflag = common.getboolean(docs[0].docemail) if(len(docs) > 0 ) else False
            
            
            apptdate = (appts[0].f_start_time).strftime('%d/%m/%Y %I:%M %p')
                
            #SMS to Patient
            if(action == 'create'):
                    smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptConfirm.txt') 
            elif(action == 'update'):
                    smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptReschedule.txt')
            else:
                    smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptCancel.txt')
        
                    
            f = open(smsfile,'rb')
            temp = Template(f.read())
            f.close()  
            patmessage = temp.template
            patmessage = patmessage.replace("$fname", fname)
            patmessage = patmessage.replace("$docname", docname)
            patmessage = patmessage.replace("$appointmentdate", apptdate)
            patmessage = patmessage.replace("$provplace", location)
            patmessage = patmessage.replace("$doccell", "+" + doccell)
            if(provtel != ""):
                    patmessage = patmessage.replace("$clinicno", provtel)
            else:
                    patmessage = patmessage.replace("$clinicno", doccell)
                               
                    
                    
            #SMS to Attending doctor
            if(action == 'create'):
                    smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptConfirmDoc.txt') 
            elif(action == 'update'):
                    smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptRescheduleDoc.txt')
            else:
                    smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptCancelDoc.txt')
            
            f = open(smsfile,'rb')
            temp = Template(f.read())
            f.close()  
            docmessage = temp.template
            docmessage = docmessage.replace("$fname", fname)
            docmessage = docmessage.replace("$docname", docname)
            docmessage = docmessage.replace("$appointmentdate", apptdate)
            docmessage = docmessage.replace("$patcell", "+" + patcell)
        
            #SMS to Provider
            smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptCancelProv.txt')            
            f = open(smsfile,'rb')
            temp = Template(f.read())
            f.close()  
            provmessage = temp.template
            provmessage = provmessage.replace("$providername",provname )
            provmessage = provmessage.replace("$fname", fname + "(+" + patcell  +")")
            provmessage = provmessage.replace("$appointmentdate", apptdate)      
    
            props = db(db.urlproperties.id>0).select()
            ccs = common.getstring(props[0].mailcc) if(len(props[0].mailcc)>0) else ""
         
            
            if(patcell != ""):   # send SMS and email to patient
                    retVal1 = mail.sendSMS2Email(db,patcell,patmessage)
            if(patemail != ""):
                    mail.groupEmail(db, patemail, ccs, "Appointment: " + apptdate, patmessage)  # send email to patient
                
            if(doccell != ""): # send SMS to 
                    retVal2 = mail.sendSMS2Email(db,doccell,docmessage)
            
             
            if(docemail != ""):  #send email to doc
                    mail.groupEmail(db, docemail, ccs, "Appointment: " + apptdate, docmessage)  # send email to patient
        
    
            if(provcell != ""): # send SMS to 
                    retVal2 = mail.sendSMS2Email(db,provcell,provmessage)
             
            if((provemail != "")):  #send email to provider
                    mail.groupEmail(db, provemail, ccs, "Appointment: " + apptdate, provmessage)  # send email to patient
    
    
    
    
            return retVal1   
        

    
    
    #this method gets a list of all apointments for this patient for a particular month and year
    #month = 1..12
    #year = YYYY  e.g. 2018
    #return - list of appointments
    #apptid, doctorid, patientname, apptdatetime, color
    def getappointmentsbypatient(self,month,year,memberid,patientid):
        
        db = self.db
        providerid = self.providerid
        
        start = str(year) + "-" + str(month).zfill(2) + "-01 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-31 23:59:00"  #no need to take 30 or 31 days - just default to 31 days
    
        
        appts = db((db.vw_appointments.provider == providerid) & (db.vw_appointments.patientmember == memberid) & (db.vw_appointments.patient == patientid) & \
                   (db.vw_appointments.f_start_time >= start)  & (db.vw_appointments.f_start_time <= end) &\
                   (db.vw_appointments.is_active == True)).\
            select(db.vw_appointments.f_uniqueid,db.vw_appointments.f_start_time,db.vw_appointments.f_patientname,\
                   db.vw_appointments.doctor,db.vw_appointments.docname,db.vw_appointments.color,db.vw_appointments.cell, orderby=db.vw_appointments.f_start_time)
        
        apptlist = []
        
        for appt in appts:
             
            apptobj = {
                "appointmentid" : int(common.getid(appt.f_uniqueid)),
                "apptdatetime":(appt.f_start_time).strftime("%d/%m/%Y %I:%M %p"),
                "patientname" : common.getstring(appt.f_patientname),
                "patcell": common.modify_cell(appt.cell),
                "docname":common.getstring(appt.docname),
                "doctorid": common.getstring(appt.doctor),
                "color":common.getstring(appt.color)
            }
            apptlist.append(apptobj)        
        
        return json.dumps({"apptcount":len(appts), "apptlist":apptlist})
    

    #this method gets a list of all apointments for this provider and patient for a particular month and year
    #month = 1..12
    #year = YYYY  e.g. 2018
    #return - list of appointments
    #apptid, doctorid, doctorname, patientname, apptdatetime, color
    def appointments(self,month,year):
        
        db = self.db
        providerid = self.providerid
             
        
        start = str(year) + "-" + str(month).zfill(2) + "-01 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-31 23:59:00"  #no need to take 30 or 31 days - just default to 31 days
    
        
        appts = db((db.vw_appointments.provider == providerid) & (db.vw_appointments.f_start_time >= start)  & \
                   (db.vw_appointments.f_start_time <= end) & (db.vw_appointments.is_active == True)).\
            select(db.vw_appointments.f_uniqueid,db.vw_appointments.f_start_time,db.vw_appointments.f_patientname,\
                   db.vw_appointments.doctor,db.vw_appointments.docname,db.vw_appointments.color,db.vw_appointments.cell, orderby=db.vw_appointments.f_start_time)
        
        apptlist = []
        
        for appt in appts:
             
            apptobj = {
                "appointmentid" : int(common.getid(appt.f_uniqueid)),
                "apptdatetime":(appt.f_start_time).strftime("%d/%m/%Y %I:%M %p"),
                "patientname" : common.getstring(appt.f_patientname),
                "patcell": common.modify_cell(appt.cell),
                "docname":common.getstring(appt.docname),
                "doctorid": common.getstring(appt.doctor),
                "color":common.getstring(appt.color)
            }
            apptlist.append(apptobj)        
        
        return json.dumps({"apptcount":len(appts), "apptlist":apptlist})
    
    
    #this method gets a list of all apointments for this provider and patient in a particular month and year
    #month = 1..12
    #year = YYYY  e.g. 2018
    #return - list of appointments
    #apptid, doctorid, doctorname, patientname, apptdatetime, color
    def getappointmentsbymonth(self,month,year):
        
    
        db = self.db
        providerid = self.providerid
        
        start = str(year) + "-" + str(month).zfill(2) + "-01 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-31 23:59:00"  #no need to take 30 or 31 days - just default to 31 days
        
        
        appts = db((db.vw_appointments.provider == providerid) & (db.vw_appointments.f_start_time >= start)  & \
                   (db.vw_appointments.f_start_time <= end) & (db.vw_appointments.is_active == True)).\
            select(db.vw_appointments.f_uniqueid,db.vw_appointments.f_start_time,db.vw_appointments.f_patientname,\
                   db.vw_appointments.doctor,db.vw_appointments.docname,db.vw_appointments.color, db.vw_appointments.cell,orderby=db.vw_appointments.f_start_time)
        
        apptlist = []
        
        for appt in appts:
             
            apptobj = {
                "appointmentid" : int(common.getid(appt.f_uniqueid)),
                "apptdate":(appt.f_start_time).strftime("%d/%m/%Y"),
                "appttime"  : (appt.f_start_time).strftime("%I:%M %p"),
                "patientname" : appt.f_patientname,
                "patcell": common.modify_cell(appt.cell),
                "docname":appt.docname,
            }
            apptlist.append(apptobj)        
        
        return json.dumps({"apptcount":len(appts), "apptlist":apptlist})    


    #this method gets a list of all apointments for this provider and patient for a particular day, month and year
    #day = 1..31 or 1..30
    #month = 1..12
    #year = YYYY  e.g. 2018
    #return - list of appointments
    #apptid, doctorid, doctorname, patientname, apptdatetime, color
    def getpatappointmentsbyday(self,day,month,year,memberid,patientid):
        
    
        db = self.db
        providerid = self.providerid
        
        start = str(year) + "-" + str(month).zfill(2) + "-" + str(day).zfill(2) + " 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-" + str(day).zfill(2) + " 23:59:59"
        
        
        appts = db((db.vw_appointments.provider == providerid) & (db.vw_appointments.patientmember == memberid) & (db.vw_appointments.patient == patientid) & \
                   (db.vw_appointments.f_start_time >= start)  & \
                   (db.vw_appointments.f_start_time <= end) & (db.vw_appointments.is_active == True)).\
            select(db.vw_appointments.f_uniqueid,db.vw_appointments.f_start_time,db.vw_appointments.f_patientname,\
                   db.vw_appointments.doctor,db.vw_appointments.docname,db.vw_appointments.color,db.vw_appointments.cell)
        
        apptlist = []
        
        for appt in appts:
             
            apptobj = {
                "appointmentid" : int(common.getid(appt.f_uniqueid)),
                "apptdate":(appt.f_start_time).strftime("%d/%m/%Y"),
                "appttime"  : (appt.f_start_time).strftime("%I:%M %p"),
                "patientname" : appt.f_patientname,
                "docname":appt.docname,
                "patcell":common.modify_cell(appt.cell)
            }
            apptlist.append(apptobj)        
        
        return json.dumps({"apptcount":len(appts), "apptlist":apptlist})    

    
    #this method gets a list of all apointments for this provider for a particular day, month and year
    #day = 1..31 or 1..30
    #month = 1..12
    #year = YYYY  e.g. 2018
    #return - list of appointments
    #apptid, doctorid, doctorname, patientname, apptdatetime, color
    def getappointmentsbyday(self,day,month,year):
        
    
        db = self.db
        providerid = self.providerid
        
        start = str(year) + "-" + str(month).zfill(2) + "-" + str(day).zfill(2) + " 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-" + str(day).zfill(2) + " 23:59:59"
        
        
        appts = db((db.vw_appointments.provider == providerid) & (db.vw_appointments.f_start_time >= start)  & \
                   (db.vw_appointments.f_start_time <= end) & (db.vw_appointments.is_active == True)).\
            select(db.vw_appointments.f_uniqueid,db.vw_appointments.f_start_time,db.vw_appointments.f_patientname,\
                   db.vw_appointments.doctor,db.vw_appointments.docname,db.vw_appointments.color,db.vw_appointments.cell)
        
        apptlist = []
        
        for appt in appts:
             
            apptobj = {
                "appointmentid" : int(common.getid(appt.f_uniqueid)),
                "apptdate":(appt.f_start_time).strftime("%d/%m/%Y"),
                "appttime"  : (appt.f_start_time).strftime("%I:%M %p"),
                "patientname" : appt.f_patientname,
                "docname":appt.docname,
                "patcell":common.modify_cell(appt.cell)
            }
            apptlist.append(apptobj)        
        
        return json.dumps({"apptcount":len(appts), "apptlist":apptlist})    

    #this method returns number of appointments/day for all the days in a month
    def getappointmentcountbymonth(self,month,year):

        db = self.db
        providerid = self.providerid
        
        start = str(year) + "-" + str(month).zfill(2) + "-01 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-31 23:59:00"  #no need to take 30 or 31 days - just default to 31 days
        
        strsql = "select DATE(f_start_time) as apptdate, count(*) as apptcount from vw_appointments where provider = " + str(providerid)
        strsql = strsql + " and f_start_time >= '"  + start +  "'"
        strsql = strsql + " and f_start_time <= '"  + end +  "'"
        strsql = strsql + " and is_active = 'T' "
        strsql = strsql + " group by DATE(f_start_time)"
        
        ds = db.executesql(strsql)
        apptobj = {}
        apptlist = []
        
        
        for i in xrange(0,len(ds)):
            apptobj = {
                "apptdate": ds[i][0].strftime("%d/%m/%Y"),
                "count": int(common.getid(ds[i][1]))
            }
            apptlist.append(apptobj)
            
        
        return json.dumps({"apptlist":apptlist})            

    #this method returns number of appointments/day for all the days in a month
    def getpatappointmentcountbymonth(self,month,year,memberid,patientid):

        db = self.db
        providerid = self.providerid
        
        start = str(year) + "-" + str(month).zfill(2) + "-01 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-31 23:59:00"  #no need to take 30 or 31 days - just default to 31 days
        
        strsql = "select DATE(f_start_time) as apptdate, count(*) as apptcount from vw_appointments where provider = " + str(providerid)
        strsql = strsql + " and patientmember = "  + str(memberid) +  ""
        strsql = strsql + " and patient = "  + str(patientid) +  ""
        strsql = strsql + " and f_start_time >= '"  + start +  "'"
        strsql = strsql + " and f_start_time <= '"  + end +  "'"
        strsql = strsql + " and is_active = 'T' "
        strsql = strsql + " group by DATE(f_start_time)"
        
        ds = db.executesql(strsql)
        apptobj = {}
        apptlist = []
        
        
        for i in xrange(0,len(ds)):
            apptobj = {
                "apptdate": ds[i][0].strftime("%d/%m/%Y"),
                "count": int(common.getid(ds[i][1]))
            }
            apptlist.append(apptobj)
            
        
        return json.dumps({"apptlist":apptlist})            
    
    #this method returns number of appointments/doc in a month
    def getdocappointmentcountbymonth(self,month,year):
 
        db = self.db
        providerid = self.providerid
        
        start = str(year) + "-" + str(month).zfill(2) + "-01 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-31 23:59:00"  #no need to take 30 or 31 days - just default to 31 days
        
        
        strsql = "select doctorid, doctorname, doccolor,count(*),doccell as apptcount from vw_appointment_monthly where providerid = " + str(providerid)
        strsql = strsql + " and f_start_time >= '"  + start +  "'"
        strsql = strsql + " and f_start_time <= '"  + end +  "'"
        strsql = strsql + " and is_active = 'T' "
        strsql = strsql + " group by doctorid"
        
        ds = db.executesql(strsql)
        apptobj = {}
        apptlist = []
        
        
        for i in xrange(0,len(ds)):
            
            apptobj = {
                
                "doctor":common.getstring(ds[i][1]),
                'doccell':common.modify_cell(ds[i][4]),
                "count": int(common.getstring(ds[i][3])),
                "color": common.getstring(ds[i][2])
            
            }
            
            apptlist.append(apptobj)
            
        
        return json.dumps({"doclist":apptlist})              
  
    #this method return the appointment detail for the specific appointment
    #
    def appointment(self,apptid):
        
        db = self.db
        providerid = self.providerid
        prov = db(db.provider.id == providerid).select(db.provider.pa_locationurl)
        locationurl = prov[0].pa_locationurl if len(prov) == 1 else ""
        apptobj = {}
        
        try:
            #appt = db((db.vw_appointments.f_uniqueid == apptid) & (db.vw_appointments.provider == providerid)  & (db.vw_appointments.is_active == True)).select()
            appt = db((db.vw_appointments.id == apptid)   & (db.vw_appointments.is_active == True)).select()
            if(len(appt) == 1):
                apptobj= {
                    "appointmentid":apptid,
                    "apptdatetime" : (appt[0].f_start_time).strftime("%d/%m/%Y %I:%M %p"),
                    "duration": 30 if(common.getstring(appt[0].f_duration) == "") else int(appt[0].f_duration),
                    "complaint":common.getstring(appt[0].f_title),
                    "notes":common.getstring(appt[0].description),
                    "location":common.getstring(appt[0].f_location),
                    "locationurl":locationurl,
                    "status":common.getstring(appt[0].f_status) if(common.getstring(appt[0].f_status) != "") else "Open",
                    "memberid":int(common.getid(appt[0].patientmember)),
                    "patientid":int(common.getid(appt[0].patient)),
                    "patientname" : common.getstring(appt[0].f_patientname),
                    "patcell":common.modify_cell(appt[0].cell),
                    "doctorid":int(common.getid(appt[0].doctor)),
                    "docname":common.getstring(appt[0].docname),
                    "doccell":common.modify_cell(appt[0].doccell),
                    "color": appt[0].color if(common.getstring(appt[0].color) != "") else "#ff0000",
                    "provcell":common.modify_cell(appt[0].provcell),
                    "result":"success",
                    "error_message":""
                      
                    }
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Appointment API Exception Error - " + str(e)
            return json.dumps(excpobj)       
            
    
        return json.dumps(apptobj)
    
    
    
    #This method creates a new appointment with the following inputs
    #Input:
    #{ 
    # providerid
    # memberid
    # patientid
    # doctorid
    # complaint
    # start date and time   'dd/mm/yyyy hh:mm'
    # duration
    # provider notes
    # app status
    #}
    def xnewappointment(self,memberid,patientid,doctorid,complaint,startdt,duration,providernotes,cell,appPath,appointment_ref = None):
        logger.loggerpms2.info("Enter newappointment in mdpappointment" + str(memberid) + " " + startdt)
        db = self.db
        providerid = self.providerid
        auth = current.auth
        
        newapptobj = {}
        
        
        try:
            #location of the Provider's practice
            location = ""
            provs = db(db.provider.id == providerid).select()
            if(len(provs) == 1):
                location = provs[0].pa_practicename + ", " + provs[0].pa_practiceaddress
            
            # find out day of the appt.
            startapptdt    = common.getdt(datetime.datetime.strptime(startdt,"%d/%m/%Y %H:%M"))
            endapptdt = startapptdt + timedelta(minutes=duration)
            
            
    
            
            pat = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).\
                select(db.vw_memberpatientlist.fullname)
            
            #check for block
            if((self.isBlocked(startapptdt,endapptdt,doctorid)==False)):
                logger.loggerpms2.info("Not Blocked")
                apptid  = db.t_appointment.insert(f_start_time=startapptdt, f_end_time = endapptdt, f_duration = duration, f_status = "Open", 
                                                  cell = cell,f_title = complaint,f_treatmentid = 0,
                                                  f_patientname = common.getstring(pat[0].fullname),
                                                  description = providernotes,f_location = location, sendsms = True, smsaction = 'create',sendrem = True,
                                                  doctor = doctorid, provider=providerid, patient=patientid,patientmember=memberid, is_active=True,
                                                  created_on=common.getISTFormatCurrentLocatTime(),modified_on=common.getISTFormatCurrentLocatTime(),
                                                  created_by = 1,
                                                  modified_by= 1) 
                
                
                db.commit()
                logger.loggerpms2.info("New Appointment " + str(apptid))
                appointment_ref = apptid if(appointment_ref == None) else appointment_ref
                
                db(db.t_appointment.id == apptid).update(f_uniqueid = appointment_ref)
                
                #save in case report
                common.logapptnotes(db,complaint,providernotes,apptid)
                
                # Send Confirmation SMS
                #self.sms_confirmation(appPath,apptid,"create")
                
                newapptobj= {"result":"success","error_message":"","appointment_ref":appointment_ref,"appointmentid":apptid,"message":"success"}
             
            else:
                logger.loggerpms2.info("Blocked")
                newapptobj = {"result":"success","error_message":"","appointment_ref":appointment_ref, "appointmentid":0,"message":"Invalid Appointment Date and Time"}
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "New Appointment API Exception Error - " + str(e)
            return json.dumps(excpobj)       
            

        
        return json.dumps(newapptobj)
    def newappointment(self,memberid,patientid,doctorid,complaint,startdt,duration,providernotes,cell,appPath,appointment_ref = None):
            logger.loggerpms2.info("Enter newappointment in mdpappointment" + str(memberid) + " " + startdt)
            db = self.db
            providerid = self.providerid
            auth = current.auth
            
            newapptobj = {}
            
            
            try:
                #location of the Provider's practice
                location = ""
                provs = db(db.provider.id == providerid).select()
                if(len(provs) == 1):
                    location = provs[0].pa_practicename + ", " + provs[0].pa_practiceaddress
                
                # find out day of the appt.
                startapptdt    = common.getdt(datetime.datetime.strptime(startdt,"%d/%m/%Y %H:%M"))
                endapptdt = startapptdt + timedelta(minutes=duration)
                
                
        
                
                pat = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).\
                    select(db.vw_memberpatientlist.fullname)
                
                #check for block
                if((self.isBlocked(startapptdt,endapptdt,doctorid)==False)):
                    logger.loggerpms2.info("Not Blocked")
                    
                    #strSQL = ""
                    #strstart = common.getstringfromdate(startapptdt, "%Y-%m-%d %H:%M")
                    #strend = common.getstringfromdate(endapptdt, "%Y-%m-%d %H:%M")
                    
                    #uniqueid = random.randint(9999,999999)
                    #y = db(db.t_appointment.f_uniqueid == uniqueid).count()
                    #if(y > 0):
                        #uniqueid = random.randint(9999,999999)
                    
                    
                    
                    #strSQL = strSQL + "INSERT INTO t_appointment( "
                    #strSQL = strSQL + "f_uniqueid , f_title, f_patientname, f_start_time, f_end_time, f_duration,f_location,f_treatmentid,f_status, description,provider,doctor,"
                    #strSQL = strSQL + "patientmember,patient,cell,sendsms,sendrem,smsaction) VALUES ("
                    #strSQL = strSQL + str(uniqueid) + ","
                    #strSQL = strSQL + "'" + complaint + "',"
                    #strSQL = strSQL + "'" + pat[0].fullname + "',"
                    #strSQL = strSQL + "'" + strstart + "',"
                    #strSQL = strSQL + "'" + strend + "',"
                    #strSQL = strSQL + str(duration) + ","
                    #strSQL = strSQL + "'" + location + "',"
                    #strSQL = strSQL + "0" + ","
                    #strSQL = strSQL + "'Open'" + ","
                    #strSQL = strSQL + "'" + providernotes + "',"
                    #strSQL = strSQL +  str(providerid) + ","
                    #strSQL = strSQL +  str(doctorid) + ","
                    #strSQL = strSQL +  str(memberid) + ","
                    #strSQL = strSQL + str(patientid) + ","
                    #strSQL = strSQL + "'" + cell + "',"
                    #strSQL = strSQL + "'T'" + ","
                    #strSQL = strSQL + "'T'" + ","
                    #strSQL = strSQL + "'create'"  + ")"           
                    ##strSQL = strSQL + "'T'" + ")"
                    ##strSQL = strSQL + "1",
                    ##strSQL = strSQL + "'" + common.getstringfromdate(datetime.datetime.today(),"%Y-%m-%d %H:%M") +"',"
                    ##strSQL = strSQL + "1",
                    ##strSQL = strSQL + "'" + common.getstringfromdate(datetime.datetime.today(),"%Y-%m-%d %H:%M") + "')"
                    
                    
                    #logger.loggerpms2.info("Insert Appointment SQL ",strSQL)
                   
                    
                    apptid  = db.t_appointment.insert(f_start_time=startapptdt, f_end_time = endapptdt, f_duration = duration, f_status = "Open", 
                                                      cell = cell,f_title = complaint,f_treatmentid = 0,
                                                      f_patientname = common.getstring(pat[0].fullname),
                                                      description = providernotes,f_location = location, sendsms = True, smsaction = 'create',sendrem = True,
                                                      doctor = doctorid, provider=providerid, patient=patientid,patientmember=memberid, is_active=True,
                                                      created_on=common.getISTFormatCurrentLocatTime(),modified_on=common.getISTFormatCurrentLocatTime(),
                                                      created_by = 1,
                                                      modified_by= 1) 
                    
                    #db.executesql(strSQL)
                    #db.commit()
                    #ds = db(db.t_appointment.f_uniqueid == uniqueid).select(db.t_appointment.id)
                    #apptid = int(common.getid(ds[0].id) if (len(ds) == 1) else "0")
                    
                    logger.loggerpms2.info("New Appointment " + str(apptid))
                    appointment_ref = apptid if(appointment_ref == None) else appointment_ref
                    
                    db(db.t_appointment.id == apptid).update(f_uniqueid = appointment_ref)
                    
                    #save in case report
                    common.logapptnotes(db,complaint,providernotes,apptid)
                    
                    # Send Confirmation SMS
                    #self.sms_confirmation(appPath,apptid,"create")
                    
                    newapptobj= {"result":"success","error_message":"","appointment_ref":appointment_ref,"appointmentid":apptid,"message":"success"}
                 
                else:
                    logger.loggerpms2.info("Blocked")
                    newapptobj = {"result":"success","error_message":"","appointment_ref":appointment_ref, "appointmentid":0,"message":"Invalid Appointment Date and Time"}
            except Exception as e:
                excpobj = {}
                excpobj["result"] = "fail"
                excpobj["error_message"] = "New Appointment API Exception Error - " + str(e)
                return json.dumps(excpobj)       
                
    
            
            return json.dumps(newapptobj)    
    def cancelappointment(self,appointmentid,providernotes,appPath):
        db = self.db
        providerid = self.providerid
        auth = current.auth
        apptobj = {}
        try:
            appt = db(db.t_appointment.id == appointmentid).select()  
            
            currnotes = common.getstring(appt[0].description)
            complaint = appt[0].f_title,
            apptobj = {}
            
            db(db.t_appointment.id == appointmentid).update(f_status = "Cancelled", sendsms = False, sendrem=False, smsaction='cancelled', \
                                                            description = providernotes if(providernotes != "") else currnotes, is_active = False,
                                                            modified_on = common.getISTFormatCurrentLocatTime(),
                                                            modified_by = 1 if(auth.user == None) else auth.user.id                                                        
                                                            )
        
            if(providernotes != ""):
                if(currnotes.strip().upper() != providernotes.strip().upper()):
                    common.logapptnotes(db,complaint,providernotes,appointmentid)
                            
            # Send Confirmation SMS
            retval = self.sms_confirmation(appPath,appointmentid,"delete")
            logger.loggerpms2.info("SMS Confirmation Ret value = >>" + str(retval))
            
            if(retval == True):
                apptobj= {"result":True, "appointmentid":appointmentid,"message":"Appointment deleted successfully"}
            else:
                apptobj= {"result":False, "appointmentid":appointmentid,"message":"Error sending delete appointment SMS message"}  
                
        except Exception as e:
            excpobj = {}
            excpobj["result"] = False
            excpobj["error_message"] = "Cancel Appointment API Exception Error - " + str(e)
            
            logger.loggerpms2.info("Cancel Appointment API Exception Error - " + str(e))
            return json.dumps(excpobj)       

        return json.dumps(apptobj)
                                                        
    def checkinappointment(self,apptid):
        
        db = self.db
        auth = current.auth
        retval = {}
        
        try:
            db((db.t_appointment.id == apptid) & (db.t_appointment.is_active == True)).update(\
                f_status = status.APPTSTATUS[2],   #Checked-In
                modified_on = common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id
            )  
            retval = {"result":"success","error_message":""}
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Check-in Appointment API Exception Error - " + str(e)
            return json.dumps(excpobj)       

        
        return json.dumps(retval)
    
    
    def updateappointment(self,appointmentid,doctorid,complaint,startdt,duration,providernotes,cell,status,treatmentid,appPath):
        
        db = self.db
        providerid = self.providerid
        auth = current.auth
        
        appt = db(db.t_appointment.id == appointmentid).select()  
        curraptdt = appt[0].f_start_time
        currenddt = appt[0].f_end_time
        currnotes = common.getstring(appt[0].description)
        
        
        apptobj = {}
        
        
        try:
            newapptdt    = common.getdt(datetime.datetime.strptime(startdt,"%d/%m/%Y %H:%M"))
            newendapptdt = newapptdt + timedelta(minutes=duration)       
            
            if(self.isBlocked(newapptdt,newendapptdt,doctorid if(doctorid != 0) else appt[0].doctor)==False):
                db(db.t_appointment.id == appointmentid).update(\
                   
                    f_title = complaint if(complaint !="") else appt[0].f_title,
                    f_start_time = newapptdt if(startdt !="") else currapptdt,
                    f_end_time = newendapptdt if(startdt !="") else currenddt,
                    f_duration = duration if(duration != 0) else appt[0].f_duration,
                    
                    f_treatmentid = treatmentid if(treatmentid != 0) else appt[0].f_treatmentid,
                    f_status = status if(status != "") else appt[0].f_status,
                    sendsms = True  if(curraptdt !=newapptdt ) else common.getboolean(appt[0].sendsms),
                    sendrem = True  if(curraptdt !=newapptdt ) else common.getboolean(appt[0].sendrem),
                    smsaction = 'update'  if(curraptdt !=newapptdt ) else common.getboolean(appt[0].smsaction),
                    description = providernotes if(providernotes != "") else currnotes,
                    doctor = doctorid if(doctorid != 0) else appt[0].doctor,
                    cell = cell if(common.getstring(cell) != "") else appt[0].cell,
                    modified_on = common.getISTFormatCurrentLocatTime(),
                    modified_by= 1 if(auth.user == None) else auth.user.id
                    )
                
                if(providernotes != ""):
                    if(currnotes.strip().upper() != providernotes.strip().upper()):
                        common.logapptnotes(db,complaint,providernotes,appointmentid)
                     
                # Send Confirmation SMS
                #retval=True
                #if(curraptdt !=newapptdt ):
                    #retval = self.sms_confirmation(appPath,appointmentid,"update")
                
                apptobj= {"result":True, "appointmentid":appointmentid,"message":"Appointment updated successfully"}
            else:
                apptobj = {"result":False, "appointmentid":appointmentid,"message":"Invalid Appointment Date and Time"}
                
        except Exception as e:
            excpobj = {}
            excpobj["result"] = False
            excpobj["error_message"] = "Check-in Appointment API Exception Error - " + str(e)
            return json.dumps(excpobj)       
        
               
        return json.dumps(apptobj)
        
     
    def groupsms(self,appPath):
        
        
        logger.loggerpms2.info("Enter groupsms")
        db = self.db
        
        try:
            r = tasks.sendGroupSMS(db,appPath)     #sendNewAptGrpSMS(db,appPath)
            r["result"] = "success"
            r["error_message"] = ""
            
            #if(r != None):
                #strsmsdate = r["smsdate"]
                #smsdate = datetime.datetime.strptime(strsmsdate, "%d/%m/%Y")
                
                #if(int(r["provsmscount"])>0):
                    #r1 = db(db.groupsmscount.smsdate == smsdate).select()
                    #if(len(r1) == 0):
                            #db.groupsmscount.insert(smscount=int(r["provsmscount"]),smsdate=smsdate)
                    #else:
                        #sql = "UPDATE groupsmscount SET smscount = smscount + " + str(int(r["provsmscount"])) + " WHERE smsdate = '" + strsmsdate + "'"
                        #db.executesql(sql)
                        #db.commit()
                    
        
        except Exception as e:
            r = {
            
                "result":"fail",
                "error_message":"Appointment groupsms Exception Error - " + e.message
            }
            
            
        
        return json.dumps(r)
       

    
    
     
    def new_appointment(self,avars):
        logger.loggerpms2.info("Enter New_Appointment API ==>")
        auth = current.auth
        db = self.db
        try:
            
            blockappt = common.getboolean(common.getkeyvalue(avars,"block","False"))
            providerid = int(common.getkeyvalue(avars,"providerid","0"))
            clinicid = int(common.getkeyvalue(avars,"clinicid","0"))
            doctorid = int(common.getkeyvalue(avars,"doctorid","0"))
            memberid = int(common.getkeyvalue(avars,"memberid","0"))
            patientid = int(common.getkeyvalue(avars,"patientid","0"))
            cell = common.getkeyvalue(avars,"cell","1111111111")
                            
            complaint = common.getkeyvalue(avars,"complaint","")
            
            
            duration = common.getkeyvalue(avars,"duration","30")
            defdtstr = common.getstringfromdate(datetime.datetime.today(), "%d/%m/%Y %H:%M")
            startdtstr = common.getkeyvalue(avars,"appointment_start",defdtstr)
            startapptdt = common.getdatefromstring(startdtstr, "%d/%m/%Y %H:%M")
            endapptdt = startapptdt + timedelta(minutes=duration)
            
            
            notes = common.getkeyvalue(avars,"notes","")
            appointment_ref = common.getkeyvalue(avars,"appointment_ref","")
            
            #location of the Clinic Address (by default it is Provider's primary clinic)
            location = ""
            if(clinicid == 0):
                provs = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.pa_practicename,db.pa_practiceaddress)
                location =  provs[0].pa_practicename + ", " + provs[0].pa_practiceaddress   if(len(provs) == 1) else  ""
            else:
                r = db((db.clinic.id == clinicid) & (db.clinic.is_active == True)).select()
                
                location = r[0].address1 + " " + r[0].address2 + " " + r[0].address3 + " " + r[0].city + " " + r[0].st + " " + r[0].pin if(len(r) == 1) else ""
                location = location.strip()
        
            pat = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).\
                            select(db.vw_memberpatientlist.fullname)        
            #check for block
            if((self.isBlocked(startapptdt,endapptdt,doctorid,clinicid)==False)):
                apptid  = db.t_appointment.insert(f_start_time=startapptdt, f_end_time = endapptdt, f_duration = duration, f_status = "Blocked", \
                                                  cell = cell,f_title = complaint,f_treatmentid = 0,blockappt = blockappt,\
                                                  f_patientname = common.getstring("" if (len(pat) == 0) else pat[0].fullname),
                                                  description = notes,f_location = location, sendsms = True, smsaction = 'create',sendrem = True,
                                                  doctor = doctorid, provider=providerid, patient=patientid,patientmember=memberid, clinicid=clinicid, is_active=True,
                                                  created_on=common.getISTFormatCurrentLocatTime(),modified_on=common.getISTFormatCurrentLocatTime(),
                                                  created_by = 1 if(auth.user == None) else auth.user.id,
                                                  modified_by = 1 if(auth.user == None) else auth.user.id
                                                  )  
                
                appointment_ref = apptid if(appointment_ref == "") else appointment_ref
                db(db.t_appointment.id == apptid).update(f_uniqueid = appointment_ref)
                
                #save in case report
                common.logapptnotes(db,complaint,notes,apptid)

                newapptobj= {"result":"success","error_message":"","appointment_ref":appointment_ref,"appointmentid":apptid,"message":"success"}    
            else:
                newapptobj = {"result":"blocked","error_message":"","appointment_ref":appointment_ref, "appointmentid":0,"message":"The appointment date and time is blocked"}

        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "New_Appointment API Exception Error - " + str(e)
            excpobj["error_code"] = ""
            return json.dumps(excpobj)
        
        return json.dumps(newapptobj)

    def update_appointment(self,avars):
        logger.loggerpms2.info("Enter Update_Appointment API ==>")
        db = self.db
        auth = current.auth
        
        
        apptobj = {}
        
        
        try:
            appointmentid = int(common.getkeyvalue(avars,"appointmentid","0"))
            ds = db((db.t_appointment.id == appointmentid) & (db.t_appointment.is_active == True)).select()  
            if(len(ds) == 1):
                
                def_start_time_str = common.getstringfromdate(ds[0].f_start_time,"%d/%m/%Y %H:%M")
                def_end_time_str  = common.getstringfromdate(ds[0].f_end_time,"%d/%m/%Y %H:%M")
                db(db.t_appointment.id == appointmentid).update(\
                    
                    f_uniqueid = int(common.getkeyvalue(avars,"f_uniqueid","0" if(ds[0].f_uniqueid == None) else str(ds[0].f_uniqueid))),
                    f_title = common.getkeyvalue(avars,"f_title",ds[0].f_title),
                   
                    f_patientname = common.getkeyvalue(avars,"f_patientname",ds[0].f_patientname),
                    f_location = common.getkeyvalue(avars,"f_location",ds[0].f_location),
                    f_status = common.getkeyvalue(avars,"f_status",ds[0].f_status),
                    description = common.getkeyvalue(avars,"description",ds[0].description),
                    newpatient = common.getkeyvalue(avars,"newpatient",ds[0].newpatient),
                   
                    cell = common.getkeyvalue(avars,"cell",ds[0].cell),
                    smsaction = common.getkeyvalue(avars,"smsaction",ds[0].smsaction),
                    
                    f_start_time = common.getdatefromstring(common.getkeyvalue(avars,"f_start_time",def_start_time_str),"%d/%m/%Y %H:%M"),
                    f_end_time = common.getdatefromstring(common.getkeyvalue(avars,"f_end_time",def_end_time_str),"%d/%m/%Y %H:%M"),
                    f_duration = int(common.getkeyvalue(avars,"f_duration","0" if(ds[0].f_duration == None) else str(ds[0].f_duration))),

                    f_treatmentid = int(common.getkeyvalue(avars,"f_treatmentid","0" if(ds[0].f_treatmentid == None) else str(ds[0].f_treatmentid))),
                    provider = int(common.getkeyvalue(avars,"provider","0" if(ds[0].provider == None) else str(ds[0].provider))),
                    doctor = int(common.getkeyvalue(avars,"doctor", "0" if(ds[0].doctor == None) else str(ds[0].doctor))),
                    clinicid = int(common.getkeyvalue(avars,"clinicid","0" if(ds[0].clinicid == None) else str(ds[0].clinicid))),
                    patientmember = int(common.getkeyvalue(avars,"memberid","0" if(ds[0].patientmember == None) else str(ds[0].patientmember))),
                    patient = int(common.getkeyvalue(avars,"patientid","0" if(ds[0].patient == None) else str(ds[0].patient))),
                    
                    blockappt = common.getboolean(common.getkeyvalue(avars,"blockappt","False")),
                    sendsms = common.getboolean(common.getkeyvalue(avars,"sendsms","False")),
                    sendrem = common.getboolean(common.getkeyvalue(avars,"sendrem","False")),
                    
                    modified_on=common.getISTFormatCurrentLocatTime(),
                    modified_by= 1 if(auth.user == None) else auth.user.id
                    
                    )
                
                apptobj= {"result":"success", "appointmentid":appointmentid,"error_message":"","message":"Appointment updated successfully"}
                
            else:
                apptobj = {"result":"fail", "appointmentid":appointmentid,"error_message":"Error Updating Appointment","error_code":""}
                
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Update Appointment API Exception Error - " + str(e)
            return json.dumps(excpobj)       
        
               
        return json.dumps(apptobj)
        
    def cancel_appointment(self,avars):
        logger.loggerpms2.info("Enter Cancel_Appointment API ==>")
        db = self.db
        auth = current.auth
        
        
        apptobj = {}
        
        
        try:
            
            appointmentid = int(common.getkeyvalue(avars,"appointmentid","0"))
            appt = db((db.t_appointment.id == appointmentid) & (db.t_appointment.is_active == True)).select(db.t_appointment.description)
            desc = "" if len(appt) != 1 else appt[0].description
            notes = common.getkeyvalue(avars,"notes",desc)
            
            db((db.t_appointment.id == appointmentid)).update(\
                description = notes,
                f_status = "Cancelled"  ,  
                is_active = False,
                    
                modified_on=common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id
                
            )
            
            apptobj= {"result":"success", "appointmentid":appointmentid,"error_message":"", "error_code":"", "message":"Appointment Cancelled successfully"}
            
                
        except Exception as e:
            excpobj = {}
            excpobj["result"] = False
            excpobj["error_message"] = "Cancel Appointment API Exception Error - " + str(e)
            return json.dumps(excpobj)       
        
                 
        return json.dumps(apptobj)
                  
    
    def get_appointment(self,avars):
        logger.loggerpms2.info("Enter Get_Appointment API ==>")
        auth = current.auth
        db = self.db
        try:
            blockappt = common.getboolean(common.getkeyvalue(avars,"block","False"))
            appointmentid = int(common.getkeyvalue(avars,"appointmentid","0"))
            appt = db((db.vw_appointments.id == appointmentid) &  (db.vw_appointments.blockappt == blockappt) &  (db.vw_appointments.is_active == True)).select()
            providerid = appt[0].provider if(len(appt) == 1) else 0
            
            prov = db(db.provider.id == providerid).select(db.provider.pa_locationurl)
            locationurl = prov[0].pa_locationurl if len(prov) == 1 else ""
            apptobj = {}


                              
            if(len(appt) == 1):
                x=str(providerid),
                x=str(appointmentid),
                x= (appt[0].f_start_time).strftime("%d/%m/%Y %I:%M %p"),
                x= "30" if(common.getstring(appt[0].f_duration) == "") else int(appt[0].f_duration),
                x=common.getstring(appt[0].f_title),
                x=common.getstring(appt[0].description),
                x=common.getstring(appt[0].f_location),
                x=locationurl,
                x=common.getstring(appt[0].f_status) if(common.getstring(appt[0].f_status) != "") else "Open",
                x=common.getid(appt[0].patientmember),
                x=common.getid(appt[0].patient),
                x=common.getstring(appt[0].f_patientname),
                x=common.modify_cell(appt[0].cell),
                x=common.getid(appt[0].clinicid),
                x=common.getid(appt[0].doctor),
                x=common.getstring(appt[0].docname),
                x=common.modify_cell(appt[0].doccell),
                x=common.getstring(appt[0].color) if(common.getstring(appt[0].color) != "") else "#ff0000",
                x=common.modify_cell(appt[0].provcell),
                x=common.getstring(appt[0].clinic_ref),
                x=common.getstring(appt[0].clinic_name),
                x=common.getboolean(appt[0].blockappt),
                
                apptobj= {
                    "providerid":str(providerid),
                    "appointmentid":str(appointmentid),
                    "apptdatetime" : (appt[0].f_start_time).strftime("%d/%m/%Y %I:%M %p"),
                    "duration": "30" if(common.getstring(appt[0].f_duration) == "") else int(appt[0].f_duration),
                    "complaint":common.getstring(appt[0].f_title),
                    "notes":common.getstring(appt[0].description),
                    "location":common.getstring(appt[0].f_location),
                    "locationurl":locationurl,
                    "status":common.getstring(appt[0].f_status) if(common.getstring(appt[0].f_status) != "") else "Open",
                    "memberid":common.getid(appt[0].patientmember),
                    "patientid":common.getid(appt[0].patient),
                    "patientname" : common.getstring(appt[0].f_patientname),
                    "patcell":common.modify_cell(appt[0].cell),
                    "clinicid":common.getid(appt[0].clinicid),
                    "doctorid":common.getid(appt[0].doctor),
                    "docname":common.getstring(appt[0].docname),
                    "doccell":common.modify_cell(appt[0].doccell),
                    "color": common.getstring(appt[0].color) if(common.getstring(appt[0].color) != "") else "#ff0000",
                    "provcell":common.modify_cell(appt[0].provcell),
                    "clinic_ref":common.getstring(appt[0].clinic_ref),
                    "clinic_name":common.getstring(appt[0].clinic_name),
                    "block":common.getboolean(appt[0].blockappt),
                    "result":"success",
                    "error_message":""
                      
                    }              
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Get_Appointment API Exception Error - " + str(e)
            excpobj["error_code"] = ""
            return json.dumps(excpobj)
        
        return json.dumps(apptobj)
    
    
    def list_appointment(self,avars):
        logger.loggerpms2.info("Enter List Appointments")
        db = self.db
        auth = current.auth
        
        try:
            providerid = int(common.getkeyvalue(avars,"providerid","0"))
            clinicid = int(common.getkeyvalue(avars,"clinicid","0"))
            doctorid = int(common.getkeyvalue(avars,"doctorid","0"))
            memberid = int(common.getkeyvalue(avars,"memberid","0"))
            patientid = int(common.getkeyvalue(avars,"patientid","0"))
            blockappt = common.getboolean(common.getkeyvalue(avars,"block","False"))
            
            
            query = ((db.t_appointment.blockappt == blockappt)&(db.t_appointment.is_active == True))
            
            if(providerid != 0):
                query = query & (db.t_appointment.provider == providerid)

            if(doctorid != 0):
                query = query & (db.t_appointment.doctor == doctorid)

            if(clinicid != 0):
                query = query & (db.t_appointment.clinicid == clinicid)
                
            if(memberid != 0):
                query = query & (db.t_appointment.patientmember == memberid)
                    
            if(patientid != 0):
                query = query & (db.t_appointment.patient == patientid)
            
            fromdtstr = common.getkeyvalue(avars,"from_date",None)
            fromapptdt = None
            if(fromdtstr != None):
                fromapptdt = common.getdatefromstring(fromdtstr, "%d/%m/%Y %H:%M") 

            todtstr = common.getkeyvalue(avars,"to_date",None)
            toapptdt = None
            if(todtstr != None):
                toapptdt = common.getdatefromstring(todtstr, "%d/%m/%Y %H:%M")
            

            if(fromapptdt != None):
                query = query & (db.t_appointment.f_start_time >= fromapptdt)
            if(toapptdt != None):
                query = query & (db.t_appointment.f_start_time <= toapptdt)
        
            appts = db((query)).select()
            
            apptlist = []
                   
            for appt in appts:
                apptobj = json.loads(self.get_appointment({"appointmentid":appt.id,"block":blockappt}))
                apptlist.append(apptobj)             
            
            apptobj = {"result":"success", "error_message":"", "error_code":"", "apptcount":str(len(appts)), "apptlist":apptlist}
        
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "List_Appointment API Exception Error - " + str(e)
            excpobj["error_code"] = ""
            return json.dumps(excpobj)    
        
        return json.dumps(apptobj)

    
    def add_block_datetime(self,avars):
        avars["block"] = True
       
        block_start_str = common.getkeyvalue(avars,"block_start",None)
        if((block_start_str == None) | (block_start_str == "") ):
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Start Block Date Time not specified"
            excpobj["error_code"] = ""
            return json.dumps(excpobj)            

        block_start_date = common.getdatefromstring(block_start_str, "%d/%m/%Y %H:%M")
        
        
        block_end_str = common.getkeyvalue(avars,"block_end",None)
        if((block_end_str == None) | (block_end_str == "") ):
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "End Block Date Time not specified"
            excpobj["error_code"] = ""
            return json.dumps(excpobj)            

        block_end_date   = common.getdatefromstring(block_end_str, "%d/%m/%Y %H:%M")
        
        duration = ((block_end_date - block_start_date).total_seconds())/60
        avars["duration"] = duration
        avars["appointment_start"] = common.getstringfromdate(block_start_date,"%d/%m/%Y %H:%M")
        rsp = json.loads(self.new_appointment(avars))
        return json.dumps(rsp)
    
    def remove_block_datetime(self,avars):
  
        logger.loggerpms2.info("Enter Remove_Block API ==>")
        db = self.db
        auth = current.auth
        
        
        apptobj = {}
        
        
        try:
            block_start_str = common.getkeyvalue(avars,"block_start",None)
            if((block_start_str == None) | (block_start_str == "") ):
                excpobj = {}
                excpobj["result"] = "fail"
                excpobj["error_message"] = "Start Block Date Time not specified"
                excpobj["error_code"] = ""
                return json.dumps(excpobj)            
    
            block_start_date = common.getdatefromstring(block_start_str, "%d/%m/%Y %H:%M")
            
            
            block_end_str = common.getkeyvalue(avars,"block_end",None)
            if((block_end_str == None) | (block_end_str == "") ):
                excpobj = {}
                excpobj["result"] = "fail"
                excpobj["error_message"] = "End Block Date Time not specified"
                excpobj["error_code"] = ""
                return json.dumps(excpobj)            
    
            block_end_date   = common.getdatefromstring(block_end_str, "%d/%m/%Y %H:%M")            
     
            
            blockid = int(common.getkeyvalue(avars,"blockid","0"))
            db((db.t_appointment.f_uniqueid == blockid)).update(\
                blockappt = False,   
                is_active = False,
                    
                modified_on=common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id
                
            )
            
            
            r = db((db.t_appointment.blockappt == True) & () & ()).select()
            apptobj= {"result":"success", "error_message":"", "error_code":"","blockid":blockid,"message":"Blocked remvoed successfully"}
            
                
        except Exception as e:
            excpobj = {}
            excpobj["result"] = False
            excpobj["error_message"] = "Remove Block API Exception Error - " + str(e)
            return json.dumps(excpobj)       
        
                 
        return json.dumps(apptobj) 
    
    
    def remove_block_datetime_byID(self,avars):
      
            logger.loggerpms2.info("Enter Remove_Block API ==>")
            db = self.db
            auth = current.auth
            
            
            apptobj = {}
            
            
            try:
                
                
                blockid = int(common.getkeyvalue(avars,"blockid","0"))
                db((db.t_appointment.f_uniqueid == blockid)).update(\
                    blockappt = False,   
                    is_active = False,
                        
                    modified_on=common.getISTFormatCurrentLocatTime(),
                    modified_by= 1 if(auth.user == None) else auth.user.id
                    
                )
                
                apptobj= {"result":"success", "error_message":"", "error_code":"","blockid":blockid,"message":"Blocked remvoed successfully"}
                
                    
            except Exception as e:
                excpobj = {}
                excpobj["result"] = False
                excpobj["error_message"] = "Remove Block API Exception Error - " + str(e)
                return json.dumps(excpobj)       
            
                     
            return json.dumps(apptobj) 

    
    def list_block_datetime(self,avars):
        avars["block"]  = True
        avars["from_date"] = avars["block_start"]
        avars["to_date"] = avars["block_end"]
        rsp = json.loads(self.list_appointment(avars))
        return json.dumps(rsp)
    
    def get_block_datetime(self,avars):
        avars["block"] = True
        avars["appointmentid"] = avars["blockid"]
        rsp = json.loads(self.get_appointment(avars))
        return json.dumps(rsp)

    def checkIn(self,avars):
        avars["f_status"] = "Checked-In" 
        rsp =  json.loads(self.update_appointment(avars))
        return json.dumps(rsp)

    def checkOut(self,avars):
        avars["f_status"] = "Checked-Out" 
        rsp= json.loads(self.update_appointment(avars))
        return json.dumps(rsp)

    def confirm(self,avars):
        avars["f_status"] = "Confirmed" 
        rsp = json.loads(self.update_appointment(avars))
        return json.dumps(rsp)
    
    
    
    def reSchedule(self,avars):
        duration = common.getkeyvalue(avars,"duration","30")
        defdtstr = common.getstringfromdate(datetime.datetime.today(), "%d/%m/%Y %H:%M")
        startdtstr = common.getkeyvalue(avars,"appointment_start",defdtstr)
        startapptdt = common.getdatefromstring(startdtstr, "%d/%m/%Y %H:%M")
        endapptdt = startapptdt + timedelta(minutes=duration)
        
        avars["f_duration"] = str(duration)
        avars["f_start_time"] = common.getstringfromdate(startapptdt,"%d/%m/%Y %H:%M")
        avars["f_end_time"] = common.getstringfromdate(endapptdt,"%d/%m/%Y %H:%M")
        
        
        rsp = json.loads(self.update_appointment(avars))
        return json.dumps(rsp)
    
    
    #this method returns number of appointments/day for all the days in a month
    #filtered by provider and clinic
    def list_day_appointment_count(self,avars):

        db = self.db
        try:
            providerid = 0 if(common.getkeyvalue(avars,"providerid","0") == "") else int(common.getkeyvalue(avars,"providerid","0"))
            clinicid = 0 if(common.getkeyvalue(avars,"clinicid","0") == "") else int(common.getkeyvalue(avars,"clinicid","0"))
            doctorid = 0 if(common.getkeyvalue(avars,"doctorid","0") == "") else int(common.getkeyvalue(avars,"doctorid","0")) 
            blockappt = common.getboolean(common.getkeyvalue(avars,"block","False"))
            blockappt = 'T' if(blockappt == True) else 'F'
            month = int(common.getkeyvalue(avars,"month",(datetime.date.today()).strftime("%m")))
            year = int(common.getkeyvalue(avars,"year",(datetime.date.today()).strftime("%Y")))
    
            start = str(year) + "-" + str(month).zfill(2) + "-01 00:00:00"
            end   = str(year) + "-" + str(month).zfill(2) + "-31 23:59:00"  #no need to take 30 or 31 days - just default to 31 days
            
            strsql = "select DATE(f_start_time) as apptdate, count(*) as apptcount from vw_appointments where (1=1) "
            if(providerid !=0):
                strsql = strsql + "AND provider = " + str(providerid)
            if(clinicid !=0):
                strsql = strsql + " AND clinicid = " + str(clinicid)
            if(doctorid !=0):
                strsql = strsql + " AND doctor = " + str(doctorid)
            strsql = strsql + " and f_start_time >= '"  + start +  "'"
            strsql = strsql + " and f_start_time <= '"  + end +  "'"
            strsql = strsql + " and blockappt = '" + blockappt +"'"
            strsql = strsql + " and is_active = 'T' "
            strsql = strsql + " group by DATE(f_start_time)"
            
            ds = db.executesql(strsql)
            apptobj = {}
            apptlist = []
            #apptobj = {
                #"apptday":ds[0][0].strftime("%d"),
                #"apptmonth":ds[0][0].strftime("%m"),
                #"apptyear":ds[0][0].strftime("%Y"),
                #"apptdate": ds[0][0].strftime("%d/%m/%Y"),
                #"count": int(common.getid(ds[0][1]))
            
            #}
            
            for d in ds:
                apptobj={
                    "apptday":d[0].strftime("%d"),
                    "apptmonth":d[0].strftime("%m"),
                    "apptyear":d[0].strftime("%Y"),
                    "apptdate": d[0].strftime("%d/%m/%Y"),
                    "count": int(common.getid(d[1]))
                }
                apptlist.append(apptobj)
                
            rspObj = {
                "result":"success",
                "error_message":"",
                "error_code":"",
                
                "apptlist":apptlist,
            
            }
            
        except Exception as e:
                excpobj = {}
                excpobj["result"] = "fail"
                excpobj["error_message"] = "list_day_appointment_count API Exception Error - " + str(e)
                excpobj["error_code"] = ""
                return json.dumps(excpobj)               

        
        return json.dumps(rspObj)
    
    
    #this API gets a list of appointment for a Provider/Clinic/Doctor a day/month/year
    def list_appointments_byday(self,avars):
        
        logger.loggerpms2.info("Enter Get Appointments by Day/Month/Year for a particular provider, clinic, doctor")
        db = self.db
        auth = current.auth
        
        try:
          
            
            day = int(common.getkeyvalue(avars,"day",(datetime.date.today()).strftime("%d")))
            month = int(common.getkeyvalue(avars,"month",(datetime.date.today()).strftime("%m")))
            year = int(common.getkeyvalue(avars,"year",(datetime.date.today()).strftime("%Y")))
            
            from_date = str(day).zfill(2) + "/" + str(month).zfill(2) + "/" + str(year).zfill(2) + " 00:00"
            to_date = str(day).zfill(2) + "/" + str(month).zfill(2) + "/" + str(year).zfill(2) + " 23:59"
            
            avars["from_date"] = from_date
            avars["to_date"] = to_date

            obj = json.loads(self.list_appointment(avars))
            
            
            
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Get Appointments by Day API Exception Error - " + str(e)
            excpobj["error_code"] = ""
            return json.dumps(excpobj)         
        
        return json.dumps(obj)
    
    
