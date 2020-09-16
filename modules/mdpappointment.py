
from gluon import current

import os
import json
import datetime
import time
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
        
        
        
    def isBlocked(self, startdt, enddt,doctorid):
        
        db = self.db
        
        retval = False
        str1 = datetime.datetime.strftime(startdt, "%Y-%m-%d %H:%M:%S")
        str2 = datetime.datetime.strftime(enddt,  "%Y-%m-%d %H:%M:%S")
    
        
        appts = db((db.t_appointment.doctor == doctorid)&( str1 >= db.t_appointment.f_start_time)& (str1 <= db.t_appointment.f_end_time) & (db.t_appointment.blockappt == True) & (db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
        if(len(appts)>0):
            return True
        
        appts = db((db.t_appointment.doctor == doctorid)&( str1 >= db.t_appointment.f_end_time)&(db.t_appointment.blockappt == True)&(db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
        if(len(appts)>0):
            return False
        
        appts = db((db.t_appointment.doctor == doctorid)&( str1 <= db.t_appointment.f_start_time)&(str2 <= db.t_appointment.f_start_time)&(db.t_appointment.blockappt == True)&(db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
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
        

    
    def xgetappointmentsbypatient(self,month,year,memberid,patientid):
            
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
        apptobj = {}
        
        try:
            appt = db((db.vw_appointments.f_uniqueid == apptid) & (db.vw_appointments.provider == providerid)  & (db.vw_appointments.is_active == True)).select()
            
            if(len(appt) == 1):
                apptobj= {
                    "appointmentid":apptid,
                    "apptdatetime" : (appt[0].f_start_time).strftime("%d/%m/%Y %I:%M %p"),
                    "duration": 30 if(common.getstring(appt[0].f_duration) == "") else int(appt[0].f_duration),
                    "complaint":common.getstring(appt[0].f_title),
                    "notes":common.getstring(appt[0].description),
                    "location":common.getstring(appt[0].f_location),
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
    def newappointment(self,memberid,patientid,doctorid,complaint,startdt,duration,providernotes,cell,appPath):
        
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
                
                apptid  = db.t_appointment.insert(f_start_time=startapptdt, f_end_time = endapptdt, f_duration = duration, f_status = "Open", \
                                                  cell = cell,f_title = complaint,f_treatmentid = 0,\
                                                  f_patientname = common.getstring(pat[0].fullname),
                                                  description = providernotes,f_location = location, sendsms = True, smsaction = 'create',sendrem = True,
                                                  doctor = doctorid, provider=providerid, patient=patientid,patientmember=memberid, is_active=True,
                                                  created_on=common.getISTFormatCurrentLocatTime(),modified_on=common.getISTFormatCurrentLocatTime(),
                                                  created_by = 1 if(auth.user == None) else auth.user.id, \
                                                  modified_by= 1 if(auth.user == None) else auth.user.id)  
                
                db(db.t_appointment.id == apptid).update(f_uniqueid = apptid)
                
                #save in case report
                common.logapptnotes(db,complaint,providernotes,apptid)
                
                # Send Confirmation SMS
                #self.sms_confirmation(appPath,apptid,"create")
                
                newapptobj= {"result":"success","error_message":"","appointmentid":apptid,"message":"success"}
             
            else:
                newapptobj = {"result":"success","error_message":"","appointmentid":0,"message":"Invalid Appointment Date and Time"}
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
       
       