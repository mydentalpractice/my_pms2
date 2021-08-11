
from gluon import current
from gluon.tools import Mail
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
from applications.my_pms2.modules import mdptimings

datefmt = "%d/%m/%Y"
datetimefmt = "%d/%m/%Y %H:%M:%S"

def serializedatetime(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()    
   
def calculateAge(dob):
    
    today = datetime.date.today()
    ty = today.year
    doby = dob.year
    age = ty-doby
    return age

class Appointment:
    
    
    
    def __init__(self,db,providerid):
        self.db = db
        self.providerid = providerid
       
        
        #setting the primary clinic as default clinic id for backward compatibility
        #all appointments from Practice App 1.0 will have clinicid = primary clinic
        
        clns = db((db.clinic_ref.ref_code == 'PRV') & (db.clinic_ref.ref_id == providerid) & (db.clinic.primary_clinic == True) &(db.clinic.is_active == True)).\
            select(db.clinic_ref.clinic_id, left=db.clinic.on(db.clinic.id==db.clinic_ref.clinic_id))
        self.clinicid = 0 if(len(clns) == 0) else clns[0].clinic_id
        
        return     
    
    def appointmentstatus(self):
        
        st = status.APPTSTATUS
        return  json.dumps(st)        
    
    def appointmentduration(self):
        dur = cycle.DURATION
        return json.dumps(dur)
    
    def isAppointmentSlot(self, startdt, enddt,doctorid,clinicid=0):
            
            db = self.db
            
           
                
            retval = False
            str1 = datetime.datetime.strftime(startdt, "%Y-%m-%d %H:%M:%S")
            str2 = datetime.datetime.strftime(enddt,  "%Y-%m-%d %H:%M:%S")
        
            if(clinicid == 0):
                if(doctorid == 0):
                    appts = db(( str1 >= db.t_appointment.f_start_time)& (str1 < db.t_appointment.f_end_time) & (db.t_appointment.blockappt == False) & (db.t_appointment.is_active == True)).select(db.t_appointment.id)
                else:
                    appts = db((db.t_appointment.doctor == doctorid)&( str1 >= db.t_appointment.f_start_time)& (str1 < db.t_appointment.f_end_time) & (db.t_appointment.blockappt == False) & (db.t_appointment.is_active == True)).select(db.t_appointment.id)                    
            else:
                if(doctorid == 0):
                    appts = db((db.t_appointment.clinicid==clinicid)&( str1 >= db.t_appointment.f_start_time)& (str1 < db.t_appointment.f_end_time) & (db.t_appointment.blockappt == False) & (db.t_appointment.is_active == True)).select(db.t_appointment.id)    
                else:
                    appts = db((db.t_appointment.clinicid==clinicid)&(db.t_appointment.doctor == doctorid)&( str1 >= db.t_appointment.f_start_time)& (str1 < db.t_appointment.f_end_time) & (db.t_appointment.blockappt == False) & (db.t_appointment.is_active == True)).select(db.t_appointment.id)                        
                
            if(len(appts)>0):
                return True
            
     
 
            
            return retval        
        
    def isBlocked(self, startdt, enddt,doctorid,clinicid=0):
        
        db = self.db
       
        
        retval = False
        str1 = datetime.datetime.strftime(startdt, "%Y-%m-%d %H:%M:%S")
        str2 = datetime.datetime.strftime(enddt,  "%Y-%m-%d %H:%M:%S")
    
        if(clinicid == 0):
            if(doctorid == 0):
                appts = db(( str1 >= db.t_appointment.f_start_time)& (str1 < db.t_appointment.f_end_time) & (db.t_appointment.blockappt == True) & (db.t_appointment.is_active == True)).select()
            else:
                appts = db((db.t_appointment.doctor == doctorid)&( str1 >= db.t_appointment.f_start_time)& (str1 < db.t_appointment.f_end_time) & (db.t_appointment.blockappt == True) & (db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)                
        else:
            if(doctorid == 0):
                appts = db((db.t_appointment.clinicid==clinicid)&( str1 >= db.t_appointment.f_start_time)& (str1 < db.t_appointment.f_end_time) & (db.t_appointment.blockappt == True) & (db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)    
            else:
                appts = db((db.t_appointment.clinicid==clinicid)&( str1 >= db.t_appointment.f_start_time)& (str1 < db.t_appointment.f_end_time) & (db.t_appointment.blockappt == True) & (db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)                    
            
        if(len(appts)>0):
            return True
        
        #if(clinicid == 0):
            #appts = db((db.t_appointment.doctor == doctorid)&( str1 >= db.t_appointment.f_start_time)&(db.t_appointment.blockappt == True)&(db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
        #else:
            #appts = db((db.t_appointment.clinicid==clinicid)&(db.t_appointment.doctor == doctorid)&( str1 >= db.t_appointment.f_end_time)&(db.t_appointment.blockappt == True)&(db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
            
        
        #if(len(appts)>0):
            #return False
        
        #if(clinicid == 0):
            #appts = db((db.t_appointment.doctor == doctorid)&( str1 <= db.t_appointment.f_start_time)&(str2 <= db.t_appointment.f_start_time)&(db.t_appointment.blockappt == True)&(db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
        #else:
            #appts = db((db.t_appointment.clinicid==clinicid)&(db.t_appointment.doctor == doctorid)&( str1 <= db.t_appointment.f_start_time)&(str2 <= db.t_appointment.f_start_time)&(db.t_appointment.blockappt == True)&(db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)            
            
        #if(len(appts)>0):
            #return False
        
        
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
        

    def list_open_slots(self,avars):
        db = self.db
        logger.loggerpms2.info("Enter list_open_slots " + json.dumps(avars))
        try:
            todaystr = common.getstringfromdate(datetime.date.today(),"%d/%m/%Y")
            appt_dt_str = common.getkeyvalue(avars,"appointment_date", todaystr)
            from_appt_dt = common.getdatefromstring(appt_dt_str + " 00:00:00", "%d/%m/%Y 00:00:00")

            appt_dt_str1= common.getstringfromdate(from_appt_dt,"%d/%m/%Y")
            appt_dt_str= common.getstringfromdate(from_appt_dt,"%Y-%m-%d 00:00:00")
            from_appt_dt = common.getdatefromstring(appt_dt_str, "%Y-%m-%d 00:00:00")
            
            appt_dt_str = common.getkeyvalue(avars,"appointment_date", todaystr)
            to_appt_dt = common.getdatefromstring(appt_dt_str + " 23:59:59", "%d/%m/%Y %H:%M:%S")

            appt_dt_str1= common.getstringfromdate(to_appt_dt,"%d/%m/%Y")
            appt_dt_str= common.getstringfromdate(to_appt_dt,"%Y-%m-%d 23:59:59")
            to_appt_dt = common.getdatefromstring(appt_dt_str, "%Y-%m-%d %H:%M:%S")
            
            providerid = int(common.getid(common.getkeyvalue(avars,"providerid","0")))
            clinicid = int(common.getid(common.getkeyvalue(avars,"clinicid","0")))
            doctorid = int(common.getid(common.getkeyvalue(avars,"doctorid","0")))
            
               
           
            apptobj={}
            apptobj["action"] = "list_appointment"
            apptobj["providerid"] = str(providerid)
            apptobj["clinicid"] =  str(clinicid)
            apptobj["doctorid"] = str(doctorid)
            
            apptobj["from_date"] = common.getstringfromdate(from_appt_dt,"%d/%m/%Y %H:%M")
            apptobj["to_date"] =  common.getstringfromdate(to_appt_dt,"%d/%m/%Y %H:%M")
            apptobj["block"] =  False
            
            list_appointments = self.list_appointment(apptobj)
            
            
            apptobj = {}
            apptobj["action"] = "list_block"
            apptobj["providerid"] = str(providerid)
            apptobj["clinicid"] =  str(clinicid)
            apptobj["doctorid"] = str(doctorid)
            apptobj["block_start"] = common.getstringfromdate(from_appt_dt,"%d/%m/%Y %H:%M")
            apptobj["block_end"] =  common.getstringfromdate(to_appt_dt,"%d/%m/%Y %H:%M")

            list_blocks = self.list_block_datetime(apptobj)
            
            timingReq = {
                "action":"list_ops_timing",
                "ref_code":"CLN",
                "ref_id":clinicid,
                "from_date":common.getstringfromdate(from_appt_dt,"%d/%m/%Y"),
                "to_date":common.getstringfromdate(to_appt_dt,"%d/%m/%Y")
            }
        
            timingObj  = mdptimings.OPS_Timing(db)
            clinic_timings = json.loads(timingObj.list_ops_timing(timingReq))
            ops_timing_list = clinic_timings["ops_timing_list"]                    
       
            
          
            
            list_open_slots = []
         
            if((ops_timing_list == None)|(len(ops_timing_list)==0)):
                logger.loggerpms2.info("Empty Clinic Timings")
                
                list_open_slots1=[
                    "7:00 AM","7:30 AM","8:00 AM","8:30 AM","9:00 AM","9:30 AM","10:00 AM","10:30 AM","11:00 AM","11:30 AM",
                    "12:00 PM","12:30 PM","01:00 PM","01:30 PM","02:00 PM","02:30 PM","03:00 PM","03:30 PM","04:00 PM","04:30 PM",
                    "05:00 PM","05:30 PM","06:00 PM","06:30 PM","07:00 PM","07:30 PM","08:00 PM","08:30 PM","09:00 PM","09:30 PM","10:00 PM","10:30 PM"]            
                
                todaystr = common.getstringfromdate(datetime.date.today(),"%d/%m/%Y")
                appt_dt_str = common.getkeyvalue(avars,"appointment_date", todaystr)                

                for i in xrange(0,len(list_open_slots1)):
                    open_time_str = appt_dt_str + " " + list_open_slots1[i]
                    open_dt = common.getdatefromstring(open_time_str, "%d/%m/%Y %I:%M %p")
                    close_dt = open_dt + datetime.timedelta(minutes=30)
                    
                    #check if t is appointment
                    if(self.isAppointmentSlot(open_dt,close_dt,doctorid,clinicid) == True):
                        
                        continue
                    
                    #check if t is blocked
                    if(self.isBlocked(open_dt, close_dt, doctorid,clinicid) == True):
                       
                        continue
                    
                
                    #add t time in open_slot list
                    open_slot = common.getstringfromtime(open_dt,"%I:%M %p")
                    if not (open_slot in list_open_slots) :
                        list_open_slots.append(open_slot)                    
            
            else:
                logger.loggerpms2.info("Not Empty Clinic Timings")
                for t in ops_timing_list:
                    i  =0
                    today_dt_str = common.getstringfromdate(datetime.date.today(),"%d/%m/%Y")
                    calendar_date_str = common.getkeyvalue(t,"calendar_date",today_dt_str)
                    
                    open_time_str = common.getkeyvalue(t,"open_time","07:00 AM")
                    open_time = common.gettimefromstring(open_time_str,"%I:%M %p")
                    open_dt_str = calendar_date_str + " " + open_time_str
                    open_dt = common.getdatefromstring(open_dt_str,"%d/%m/%Y %I:%M %p")
                    
    
                    close_time_str = common.getkeyvalue(t,"close_time","10:30 PM")
                    close_time = common.gettimefromstring(close_time_str,"%I:%M %p")
                    close_dt_str = calendar_date_str + " " + close_time_str
                    close_dt = common.getdatefromstring(close_dt_str,"%d/%m/%Y %I:%M %p")
                    
                    
                    is_holiday = common.getboolean(common.getkeyvalue(t,"is_holiday","false"))
                    is_saturday = common.getboolean(common.getkeyvalue(t,"is_saturday","false"))
                    is_sunday = common.getboolean(common.getkeyvalue(t,"is_sunday","false"))
                    is_lunch = common.getboolean(common.getkeyvalue(t,"is_lunch","false"))
                    if((is_holiday == True)|(is_saturday == True)|(is_sunday == True)|(is_lunch == True)):
                        continue
                    
                    t=open_dt
                    while(t < close_dt):
                        
                        #check if t is appointment
                        if((self.isAppointmentSlot(t,close_dt,doctorid,clinicid) == True) | ((self.isBlocked(t,close_dt,doctorid,clinicid) == True))):
                            t=t+datetime.timedelta(minutes=30)
                            continue
                        
                        
                    
                        #add t time in open_slot list
                        open_slot = common.getstringfromtime(t,"%I:%M %p")
                        
                        if not (open_slot in list_open_slots) :
                            list_open_slots.append(open_slot)
                        
                        t=t+datetime.timedelta(minutes=30)
                   
                
                
            
            rspobj = {
                "result":"success",
                "error_message":"",
                "error_code":"",
                "appointment_date":appt_dt_str1,
                "list_open_slots":list_open_slots
            
            }
            
          
          
            
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Get Open Slots API Exception Error - " + str(e)
            return json.dumps(excpobj)  
        
        logger.loggerpms2.info("Exit Open_Slots - " + json.dumps(rspobj))
        return json.dumps(rspobj)
    
    
    #this method gets a list of all apointments for this patient for a particular month and year
    #month = 1..12
    #year = YYYY  e.g. 2018
    #return - list of appointments
    #apptid, doctorid, patientname, apptdatetime, color
    def getappointmentsbypatient(self,month,year,memberid,patientid,clinicid=0):
        logger.loggerpms2.info("Enter API getappointmentsbypatient " + str(month) + " " + str(year) + " " + str(memberid) + " " + str(patientid) + " " + str(clinicid))
        
        db = self.db
        providerid = self.providerid
        clinicid = self.clinicid
        
        start = str(year) + "-" + str(month).zfill(2) + "-01 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-31 23:59:00"  #no need to take 30 or 31 days - just default to 31 days
    
        
        appts = db((db.vw_appointments.provider == providerid) & (db.vw_appointments.patientmember == memberid) & (db.vw_appointments.patient == patientid) & \
                   (db.vw_appointments.f_start_time >= start)  & (db.vw_appointments.f_start_time <= end) &\
                   (db.vw_appointments.is_active == True)).\
            select(db.vw_appointments.f_uniqueid,db.vw_appointments.f_start_time,db.vw_appointments.f_patientname,db.vw_appointments.blockappt,\
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
                "color":common.getstring(appt.color),
                "blockappt":common.getboolean(appt.blockappt)
            }
            apptlist.append(apptobj)        
        
        return json.dumps({"apptcount":len(appts), "apptlist":apptlist})
    

    #this method gets a list of all apointments for this provider and patient for a particular month and year
    #month = 1..12
    #year = YYYY  e.g. 2018
    #return - list of appointments
    #apptid, doctorid, doctorname, patientname, apptdatetime, color
    def appointments(self,month,year,clinicid=0):
        logger.loggerpms2.info("Enter API appointments " + str(month) + " " + str(year))
        
        db = self.db
        providerid = self.providerid
             
        
        start = str(year) + "-" + str(month).zfill(2) + "-01 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-31 23:59:00"  #no need to take 30 or 31 days - just default to 31 days
    
        appts = None
        if(clinicid == 0):
            appts = db((db.vw_appointments.provider == providerid) & (db.vw_appointments.f_start_time >= start) & \
                       (db.vw_appointments.f_start_time <= end) & (db.vw_appointments.is_active == True)).\
                select(db.vw_appointments.f_uniqueid,db.vw_appointments.f_start_time,db.vw_appointments.f_patientname,db.vw_appointments.blockappt,db.vw_appointments.clinicid,\
                       db.vw_appointments.doctor,db.vw_appointments.docname,db.vw_appointments.color,db.vw_appointments.cell, orderby=~db.vw_appointments.f_start_time)
        else:
            appts = db((db.vw_appointments.provider == providerid) & (db.vw_appointments.f_start_time >= start) & (db.vw_appointments.clinicid == clinicid)   & \
                       (db.vw_appointments.f_start_time <= end) & (db.vw_appointments.is_active == True)).\
                select(db.vw_appointments.f_uniqueid,db.vw_appointments.f_start_time,db.vw_appointments.f_patientname,db.vw_appointments.blockappt,db.vw_appointments.clinicid,\
                       db.vw_appointments.doctor,db.vw_appointments.docname,db.vw_appointments.color,db.vw_appointments.cell, orderby=~db.vw_appointments.f_start_time)
        
        apptlist = []
        
        for appt in appts:
             
            apptobj = {
                "appointmentid" : int(common.getid(appt.f_uniqueid)),
                "apptdatetime":(appt.f_start_time).strftime("%d/%m/%Y %I:%M %p"),
                "patientname" : common.getstring(appt.f_patientname),
                "patcell": common.modify_cell(appt.cell),
                "docname":common.getstring(appt.docname),
                "doctorid": int(common.getid(appt.doctor)),
                "clinicid": int(common.getid(appt.clinicid)),
                "color":common.getstring(appt.color),
                "blockappt":common.getboolean(appt.blockappt)
            }
            apptlist.append(apptobj)        
        
        return json.dumps({"apptcount":len(appts), "apptlist":apptlist})
    
    
    #this method gets a list of all apointments for this provider and patient in a particular month and year
    #month = 1..12
    #year = YYYY  e.g. 2018
    #return - list of appointments
    #apptid, doctorid, doctorname, patientname, apptdatetime, color
    def getappointmentsbymonth(self,month,year,clinicid=0):
        logger.loggerpms2.info("Enter API getappointmentsbymonth "+ str(month) + " " + str(year) + " " + str(clinicid))
        
    
        db = self.db
        providerid = self.providerid
        #clinicid = self.clinicid
        
        start = str(year) + "-" + str(month).zfill(2) + "-01 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-31 23:59:00"  #no need to take 30 or 31 days - just default to 31 days
        
        if(clinicid == 0):
            appts = db((db.vw_appointments.provider == providerid) & (db.vw_appointments.f_start_time >= start)  & \
                       (db.vw_appointments.f_start_time <= end) & (db.vw_appointments.is_active == True)).\
                select(db.vw_appointments.f_uniqueid,db.vw_appointments.f_start_time,db.vw_appointments.f_patientname,db.vw_appointments.blockappt,db.vw_appointments.clinicid,\
                       db.vw_appointments.doctor,db.vw_appointments.docname,db.vw_appointments.color, db.vw_appointments.cell,orderby=db.vw_appointments.f_start_time)
        else:
            appts = db((db.vw_appointments.provider == providerid) & (db.vw_appointments.f_start_time >= start) & (db.vw_appointments.clinicid == clinicid)  & \
                       (db.vw_appointments.f_start_time <= end) & (db.vw_appointments.is_active == True)).\
                select(db.vw_appointments.f_uniqueid,db.vw_appointments.f_start_time,db.vw_appointments.f_patientname,db.vw_appointments.blockappt,db.vw_appointments.clinicid,\
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
                "clinicid" : int(common.getid(appt.clinicid)),
                
                "blockappt":common.getboolean(appt.blockappt)
            }
            apptlist.append(apptobj)        
        
        return json.dumps({"apptcount":len(appts), "apptlist":apptlist})    


    #this method gets a list of all apointments for this provider and patient for a particular day, month and year
    #day = 1..31 or 1..30
    #month = 1..12
    #year = YYYY  e.g. 2018
    #return - list of appointments
    #apptid, doctorid, doctorname, patientname, apptdatetime, color
    def getpatappointmentsbyday(self,day,month,year,memberid,patientid,clinicid=0):
        logger.loggerpms2.info("Enter API getpatappointmentsbyday "+ str(day) + " " + str(month) + " " + str(year) + " " + str(clinicid) )
        
    
        db = self.db
        providerid = self.providerid
        
        start = str(year) + "-" + str(month).zfill(2) + "-" + str(day).zfill(2) + " 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-" + str(day).zfill(2) + " 23:59:59"
        
        if(clinicid == 0):
            appts = db((db.vw_appointments.provider == providerid) & (db.vw_appointments.patientmember == memberid) & (db.vw_appointments.patient == patientid) & \
                       (db.vw_appointments.f_start_time >= start)  & \
                       (db.vw_appointments.f_start_time <= end) & (db.vw_appointments.is_active == True)).\
                select(db.vw_appointments.f_uniqueid,db.vw_appointments.f_start_time,db.vw_appointments.f_patientname,db.vw_appointments.clinicid,\
                       db.vw_appointments.doctor,db.vw_appointments.docname,db.vw_appointments.color,db.vw_appointments.cell,db.vw_appointments.blockappt)
        else:
            appts = db((db.vw_appointments.provider == providerid) & (db.vw_appointments.patientmember == memberid) & (db.vw_appointments.patient == patientid) & (db.vw_appointments.clinicid == clinicid) & \
                       (db.vw_appointments.f_start_time >= start)  & \
                       (db.vw_appointments.f_start_time <= end) & (db.vw_appointments.is_active == True)).\
                select(db.vw_appointments.f_uniqueid,db.vw_appointments.f_start_time,db.vw_appointments.f_patientname,db.vw_appointments.clinicid,\
                       db.vw_appointments.doctor,db.vw_appointments.docname,db.vw_appointments.color,db.vw_appointments.cell,db.vw_appointments.blockappt)
            
        apptlist = []
        
        for appt in appts:
             
            apptobj = {
                "appointmentid" : int(common.getid(appt.f_uniqueid)),
                "apptdate":(appt.f_start_time).strftime("%d/%m/%Y"),
                "appttime"  : (appt.f_start_time).strftime("%I:%M %p"),
                "patientname" : appt.f_patientname,
                "docname":appt.docname,
                "patcell":common.modify_cell(appt.cell),
                "clinicid" : int(common.getid(appt.clinicid)),
                "blockappt":common.getboolean(appt.blockappt)
            }
            apptlist.append(apptobj)        
        
        return json.dumps({"apptcount":len(appts), "apptlist":apptlist})    

    
    #this method gets a list of all apointments for this provider for a particular day, month and year
    #day = 1..31 or 1..30
    #month = 1..12
    #year = YYYY  e.g. 2018
    #return - list of appointments
    #apptid, doctorid, doctorname, patientname, apptdatetime, color
    def getappointmentsbyday(self,day,month,year,clinicid=0):
        logger.loggerpms2.info("Enter API getappointmentsbyday "+ str(day) + " " + str(month) + " " + str(year) + " " + str(clinicid) )
    
        db = self.db
        providerid = self.providerid
        
        start = str(year) + "-" + str(month).zfill(2) + "-" + str(day).zfill(2) + " 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-" + str(day).zfill(2) + " 23:59:59"
        
        if(clinicid==0):
            appts = db((db.vw_appointments.provider == providerid) & (db.vw_appointments.f_start_time >= start) & \
                       (db.vw_appointments.f_start_time <= end) & (db.vw_appointments.is_active == True)).\
                select(db.vw_appointments.f_uniqueid,db.vw_appointments.f_start_time,db.vw_appointments.f_patientname,db.vw_appointments.clinicid,\
                       db.vw_appointments.doctor,db.vw_appointments.docname,db.vw_appointments.color,db.vw_appointments.cell,db.vw_appointments.blockappt)
        else:
            appts = db((db.vw_appointments.provider == providerid) & (db.vw_appointments.f_start_time >= start) & (db.vw_appointments.clinicid == clinicid)  & \
                       (db.vw_appointments.f_start_time <= end) & (db.vw_appointments.is_active == True)).\
                select(db.vw_appointments.f_uniqueid,db.vw_appointments.f_start_time,db.vw_appointments.f_patientname,db.vw_appointments.clinicid,\
                       db.vw_appointments.doctor,db.vw_appointments.docname,db.vw_appointments.color,db.vw_appointments.cell,db.vw_appointments.blockappt)
            
        apptlist = []
        
        for appt in appts:
             
            apptobj = {
                "appointmentid" : int(common.getid(appt.f_uniqueid)),
                "apptdate":(appt.f_start_time).strftime("%d/%m/%Y"),
                "appttime"  : (appt.f_start_time).strftime("%I:%M %p"),
                "patientname" : appt.f_patientname,
                "docname":appt.docname,
                "patcell":common.modify_cell(appt.cell),
                "clinicid" : int(common.getid(appt.clinicid)),
                "blockappt":common.getboolean(appt.blockappt)
            }
            apptlist.append(apptobj)        
        
        return json.dumps({"apptcount":len(appts), "apptlist":apptlist})    

    #this method returns number of appointments/day for all the days in a month
    def getappointmentcountbymonth(self,month,year,clinicid = 0):

        logger.loggerpms2.info("Enter API getappointmentcountbymonth "+  str(month) + " " + str(year)  + " " +str(clinicid) )
        db = self.db
        providerid = self.providerid
        #clinicid = self.clinicid
        
        start = str(year) + "-" + str(month).zfill(2) + "-01 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-31 23:59:00"  #no need to take 30 or 31 days - just default to 31 days
        
        #All unblocked & uncancelled appointments
        if(clinicid == 0):
            strsql = "select DATE(f_start_time) as apptdate, count(*) as apptcount from vw_appointments where provider = " + str(providerid) 
            strsql = strsql + " and f_start_time >= '"  + start +  "'"
            strsql = strsql + " and f_start_time <= '"  + end +  "'"
            strsql = strsql + " and is_active = 'T' "
            strsql = strsql + " group by DATE(f_start_time)"
        else:
            strsql = "select DATE(f_start_time) as apptdate, count(*) as apptcount from vw_appointments where provider = " + str(providerid) + " and clinicid = " + str(clinicid)
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
            
       
        logger.loggerpms2.info("Exit API getappointmentcountbymonth" )
        return json.dumps({"apptlist":apptlist})            

    #this method returns number of appointments/day for all the days in a month
    def getpatappointmentcountbymonth(self,month,year,memberid,patientid,clinicid=0):
        logger.loggerpms2.info("Enter API getpatappointmentcountbymonth " + str(month) + " " + str(year) + " " + str(memberid)  + " " + str(patientid) + " " +str(clinicid) )
        db = self.db
        providerid = self.providerid
       
        
        start = str(year) + "-" + str(month).zfill(2) + "-01 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-31 23:59:00"  #no need to take 30 or 31 days - just default to 31 days
        
        if(clinicid == 0):
            strsql = "select DATE(f_start_time) as apptdate, count(*) as apptcount from vw_appointments where provider = " + str(providerid)
            strsql = strsql + " and patientmember = "  + str(memberid) +  ""
            strsql = strsql + " and patient = "  + str(patientid) +  ""
            strsql = strsql + " and f_start_time >= '"  + start +  "'"
            strsql = strsql + " and f_start_time <= '"  + end +  "'"
            strsql = strsql + " and is_active = 'T' "
            strsql = strsql + " group by DATE(f_start_time)"
        else:
            strsql = "select DATE(f_start_time) as apptdate, count(*) as apptcount from vw_appointments where provider = " + str(providerid) + " and clinicid = " + str(clinicid)
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
            
        logger.loggerpms2.info("Exit API getpatappointmentcountbymonth" )
        
        return json.dumps({"apptlist":apptlist})            
    
    #this method returns number of appointments/doc in a month
    def getdocappointmentcountbymonth(self,month,year,clinicid=0):
        logger.loggerpms2.info("Enter API getdocappointmentcountbymonth " + str(month) + " " + str(year) + " " + str(clinicid))   
        db = self.db
        providerid = self.providerid
        #clinicid = self.clinicid
        
        start = str(year) + "-" + str(month).zfill(2) + "-01 00:00:00"
        end   = str(year) + "-" + str(month).zfill(2) + "-31 23:59:00"  #no need to take 30 or 31 days - just default to 31 days
        
        if(clinicid == 0):
            strsql = "select doctorid, doctorname, doccolor,count(*),doccell as apptcount from vw_appointment_monthly where providerid = " + str(providerid)
            strsql = strsql + " and f_start_time >= '"  + start +  "'"
            strsql = strsql + " and f_start_time <= '"  + end +  "'"
            strsql = strsql + " and is_active = 'T' "
            strsql = strsql + " group by doctorid"
        else:
            strsql = "select doctorid, doctorname, doccolor,count(*),doccell as apptcount from vw_appointment_monthly where providerid = " + str(providerid) + " and clinicid = " + str(clinicid)
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
        logger.loggerpms2.info("Enter API appointment " + str(apptid))
        db = self.db
        providerid = self.providerid
        prov = db(db.provider.id == providerid).select(db.provider.pa_locationurl)
        locationurl = prov[0].pa_locationurl if len(prov) == 1 else ""
        apptobj = {}
        
        try:
            #appt = db((db.vw_appointments.f_uniqueid == apptid) & (db.vw_appointments.provider == providerid)  & (db.vw_appointments.is_active == True)).select()
            appt = db((db.vw_appointments.id == apptid) &  (db.vw_appointments.blockappt == False) &  (db.vw_appointments.is_active == True)).select()
            if(len(appt) == 1):
                apptobj= {
                    "appointmentid":apptid,
                    "clinicid":int(common.getid(appt[0].clinicid)),
                    "apptdatetime" : (appt[0].f_start_time).strftime("%d/%m/%Y %I:%M %p"),
                    "duration": 30 if(common.getstring(appt[0].f_duration) == "") else int(appt[0].f_duration),
                    "complaint":common.getstring(appt[0].f_title),
                    "notes":common.getstring(appt[0].description),
                    "location":common.getstring(appt[0].f_location),
                    "locationurl":locationurl,
                    "status":common.getstring(appt[0].f_status) if(common.getstring(appt[0].f_status) != "") else "Confirmed",
                    "memberid":int(common.getid(appt[0].patientmember)),
                    "patientid":int(common.getid(appt[0].patient)),
                    "patientname" : common.getstring(appt[0].f_patientname),
                    "patcell":common.modify_cell(appt[0].cell),
                    "doctorid":int(common.getid(appt[0].doctor)),
                    "docname":common.getstring(appt[0].docname),
                    "doccell":common.modify_cell(appt[0].doccell),
                    "color": appt[0].color if(common.getstring(appt[0].color) != "") else "#ff0000",
                    "provcell":common.modify_cell(appt[0].provcell),
                    "gender":common.getstring(appt[0].gender),
                    "dob":common.getstringfromdate(appt[0].dob,"%d/%M/%Y"),  
                    "age":calculateAge(appt[0].dob) if(appt[0].dob != None) else 0,
                    "blockappt":common.getboolean(appt[0].blockappt),
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
   
        
     
    #def newappointment(self,memberid,patientid,doctorid,complaint,startdt,duration,providernotes,cell,appPath,appointment_ref = None):
    def newappointment(self,avars):        
            logger.loggerpms2.info("Enter NewAppointment API ==>" + json.dumps(avars))
            memberid = int(common.getid(common.getkeyvalue(avars,"memberid","0")))
            patientid = int(common.getid(common.getkeyvalue(avars,"patientid","0")))
            doctorid = int(common.getid(common.getkeyvalue(avars,"doctorid","0")))
            clinicid = int(common.getid(common.getkeyvalue(avars,"clinicid","0")))
            
            complaint = common.getkeyvalue(avars,"complaint","")
            
            startdt = common.getkeyvalue(avars,"startdt",common.getstringfromdate(common.getISTFormatCurrentLocatTime(),"%d/%m/%Y"))
            duration = int(common.getid(common.getkeyvalue(avars,"duration","30")))

            providernotes = common.getkeyvalue(avars,"providernotes","")
            cell = common.getkeyvalue(avars,"cell","")
            appPath = common.getkeyvalue(avars,"appPath","")
            appointment_ref = common.getkeyvalue(avars,"appointment_ref","")
            

            
            logger.loggerpms2.info("Enter newappointment in mdpappointment" + str(memberid) + " " + startdt + " " + str(self.clinicid))
            
            db = self.db
            providerid = self.providerid
            
            clinicid = self.clinicid if(clinicid == 0) else clinicid

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
                    select(db.vw_memberpatientlist.fullname,db.vw_memberpatientlist.dob)
                
                #check for block
                if((self.isBlocked(startapptdt,endapptdt,doctorid,clinicid)==False)):
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
                   
                    
                    apptid  = db.t_appointment.insert(f_start_time=startapptdt, f_end_time = endapptdt, f_duration = duration, f_status = "Confirmed", 
                                                      cell = cell,f_title = complaint,f_treatmentid = 0,
                                                      f_patientname = common.getstring(pat[0].fullname),
                                                      description = providernotes,f_location = location, sendsms = True, smsaction = 'create',sendrem = True,
                                                      doctor = doctorid, provider=providerid, clinicid=clinicid,\
                                                      patient=patientid,patientmember=memberid, is_active=True,
                                                      created_on=common.getISTFormatCurrentLocatTime(),modified_on=common.getISTFormatCurrentLocatTime(),
                                                      created_by = 1,
                                                      modified_by= 1) 
                    
                    #db.executesql(strSQL)
                    #db.commit()
                    #ds = db(db.t_appointment.f_uniqueid == uniqueid).select(db.t_appointment.id)
                    #apptid = int(common.getid(ds[0].id) if (len(ds) == 1) else "0")
                    
                    logger.loggerpms2.info("New Appointment " + str(apptid))
                    
                    appointment_ref = common.getkeyvalue(avars,"appointment_ref", str(apptid))
                    appointment_ref = str(apptid) if(common.getstring(appointment_ref) == "") else appointment_ref
                    
                    db(db.t_appointment.id == apptid).update(f_uniqueid = appointment_ref)
                    
                    #save in case report
                    common.logapptnotes(db,complaint,providernotes,apptid)
                    
                    # Send Confirmation SMS
                    #self.sms_confirmation(appPath,apptid,"create")
                    
                    newapptobj= {"result":"success","error_message":"","appointment_ref":appointment_ref,"appointmentid":apptid,"clinicid":clinicid,"message":"success"}
                 
                else:
                    logger.loggerpms2.info("Blocked")
                    newapptobj = {"result":"success","error_message":"","appointment_ref":appointment_ref,"clinicid":clinicid, "appointmentid":0,"message":"Invalid Appointment Date and Time"}
                    
            except Exception as e:
                excpobj = {}
                excpobj["result"] = "fail"
                excpobj["error_message"] = "New Appointment API Exception Error - " + str(e)
                return json.dumps(excpobj)       
                
    
            
            return json.dumps(newapptobj)    
    def cancelappointment(self,appointmentid,providernotes,appPath):
        logger.loggerpms2.info("Enter Cancel Appointment APi")
        db = self.db
        providerid = self.providerid
        auth = current.auth
        apptobj = {}
        try:
            appt = db(db.t_appointment.id == appointmentid).select()  
            
            currnotes = "" if(len(appt) == 0) else common.getstring(appt[0].description)
            complaint = "" if(len(appt) == 0) else appt[0].f_title,
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
        logger.loggerpms2.info("Enter Checkin Appointment APi")
        
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
    
    
    #def updateappointment(self,appointmentid,doctorid,complaint,startdt,duration,providernotes,cell,status,treatmentid,appPath):
    def updateappointment(self,avars):
        
        treatmentid = int(common.getid(common.getkeyvalue(avars,"treatmentid","0")))
        appointmentid = int(common.getid(common.getkeyvalue(avars,"appointmentid","0")))
        doctorid = int(common.getid(common.getkeyvalue(avars,"doctorid","0")))
        clinicid = int(common.getid(common.getkeyvalue(avars,"clinicid","0")))
        
        complaint = common.getkeyvalue(avars,"complaint","")
        
        startdt = common.getkeyvalue(avars,"startdt",common.getstringfromdate(common.getISTFormatCurrentLocatTime(),"%d/%m/%Y"))
        duration = int(common.getid(common.getkeyvalue(avars,"duration","30")))

        providernotes = common.getkeyvalue(avars,"providernotes","")
        cell = common.getkeyvalue(avars,"cell","")
        status = common.getkeyvalue(avars,"status","Confirmed")
        
        appPath = common.getkeyvalue(avars,"appPath","")
        
        
        
        
        
        logger.loggerpms2.info("Enter API updateappointment " + str(appointmentid))
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
                    clinicid = clinicid if(clinicid != 0) else int(common.getid(appt[0].clinicid)),
                    
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
       
    def sendPatSMSEmail(self,avars):
        logger.loggerpms2.info("Enter Send PAT SMS Email " + json.dumps(avars))
        db = self.db
        rspobj = {}
        rspmail = {}
        patobj = {}
        
        try:

            ccs = common.getkeyvalue(avars,"ccs","")
            appPath = common.getkeyvalue(avars,"appPath","")
            apptid = int(common.getid(common.getkeyvalue(avars,"appointmentid","0")))
            _mail = Mail()
            appts = db((db.vw_appointments.sendsms == True) & (db.vw_appointments.id == apptid) & \
                       ((db.vw_appointments.is_active == True) | ((db.vw_appointments.is_active == False)&(db.vw_appointments.f_status == 'Cancelled')))).\
                select(db.vw_appointments.ALL, db.clinic.ALL,left=db.clinic.on(db.clinic.id==db.vw_appointments.clinicid))
            
            sendsms = common.getboolean(common.getkeyvalue(avars,"sendsms","True"))
            sendemail = common.getboolean(common.getkeyvalue(avars,"sendemail","True"))
            retVal = True
            retVal1 = True
            
            for appt in appts:
                memberid = int(common.getid(appt.vw_appointments.patientmember))
                patientid = int(common.getid(appt.vw_appointments.patient))
                providerid = int(common.getid(appt.vw_appointments.provider))
                clinicid = int(common.getid(appt.vw_appointments.clinicid))
                doctorid = int(common.getid(appt.vw_appointments.doctor))
                appttime = (appt.vw_appointments.f_start_time).strftime('%d/%m/%Y %I:%M %p')
            
                #clinicname. clinicaddress, clinicno, cliniclocation
                clinicname = common.getstring(appt.clinic.name)
                clinicaddress1 = common.getstring(appt.clinic.address1) + " " + common.getstring(appt.clinic.address2) + " " + common.getstring(appt.clinic.address3) + " "
                clinicaddress2 = common.getstring(appt.clinic.city) + " " + common.getstring(appt.clinic.st) +" " + common.getstring(appt.clinic.pin)
                cliniclocation = common.getstring(appt.clinic.gps_location)
                cliniccell = common.modify_cell(common.getstring(appt.clinic.cell))
                clinictel  = common.getstring(appt.clinic.telephone)
                clinicno = clinictel if(clinictel != "" ) else cliniccell            
            
                fname   = common.getstring(appt.vw_appointments.f_patientname)  if((appt.vw_appointments.f_patientname != "") & (appt.vw_appointments.f_patientname != None))  else "Patient"
                
                docname = common.getstring(appt.vw_appointments.docname)

                pats = db((db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid==memberid) & (db.vw_memberpatientlist.is_active==True)).\
                    select(db.vw_memberpatientlist.cell, db.vw_memberpatientlist.email)
                
                patcell = common.modify_cell(common.getstring(pats[0].cell)) if(len(pats) > 0 ) else "910000000000"
                patemail = common.getstring(pats[0].email) if(len(pats) > 0 ) else "x@x.com"                
    
                #send SMS & email to patient
                smsfile = ""
                emailfile = ""
                if(appt.vw_appointments.smsaction == "create"):
                    #new appointment message
                    smsfile  = os.path.join(appPath,'templates/sms','SMS_ApptConfirm.txt') 
                    emailfile  = os.path.join(appPath,'templates/sms','Email_ApptConfirm.txt') 
                    
                elif(appt.vw_appointments.smsaction == "update"):
                    #reschedule  appointment message
                    smsfile  = os.path.join(appPath,'templates/sms','SMS_ApptReschedule.txt') 
                elif(appt.vw_appointments.smsaction == "cancel"):
                    smsfile  = os.path.join(appPath,'templates/sms','SMS_ApptCancel.txt') 
                else:
                    smsfile  = os.path.join(appPath,'templates/sms','SMS_ApptConfirm.txt') 
        
                f = open(smsfile,'rb')
                temp = Template(f.read())
                f.close()  
                patmessage = temp.template
                patmessage = patmessage.replace("$fname", fname)
                patmessage = patmessage.replace("$docname", docname)
                patmessage = patmessage.replace("$appointmentdate", appttime)
                patmessage = patmessage.replace("$clinicname", clinicname)             
                #patmessage = patmessage.replace("$clinicaddress1", "")             
                #patmessage = patmessage.replace("$clinicaddress2", "")             
                patmessage = patmessage.replace("$cliniclocation", cliniclocation)             
                patmessage = patmessage.replace("$clinicno", clinicno)
                
                f = open(emailfile,'rb')
                temp1 = Template(f.read())
                f.close()  
                patemailmssg = temp1.template
                patemailmssg = patemailmssg.replace("$fname", fname)
                patemailmssg = patemailmssg.replace("$docname", docname)
                patemailmssg = patemailmssg.replace("$appointmentdate", appttime)
                patemailmssg = patemailmssg.replace("$clinicname", clinicname)             
                patemailmssg = patemailmssg.replace("$clinicaddress1", clinicaddress1)             
                patemailmssg = patemailmssg.replace("$clinicaddress2", clinicaddress2)             
                patemailmssg = patemailmssg.replace("$cliniclocation", cliniclocation)             
                patemailmssg = patemailmssg.replace("$clinicno", clinicno)
                
        
                retVal = True
               
                if((patcell != "") & (sendsms)):
                    retVal = mail.sendAPI_SMS2Email(db,patcell,patmessage)
                    
                if((patemail != "")&(sendemail)):
                    #retVal1= mail.groupEmail(db, patemail, ccs, "Appointment: " + appttime, patemailmssg)  # send email to patient        
                    retVal1= mail._groupEmail(db, _mail, patemail, ccs, "Appointment: " + appttime, patemailmssg)  # send email to patient        
                
                rspobj = {}
                if(retVal == True):
                    mssg = "sendPatSMSEmail: Patient SMS sent successfully to this patient " + fname + "(" + patcell + ")"
                    rspobj["appointmentid"] = str(apptid)
                    rspobj["result"] = "success"
                    rspobj["error_message"] = ""
                    rspobj["message"] = mssg
                else:
                    rspobj["appointmentid"] = str(apptid)
                    mssg = "sendPatSMSEmail:  Error sending Patient SMS to this patient " + fname + "(" + patcell + ")"
                    rspobj["result"] = "fail"
                    rspobj["error_message"] = mssg
                    
               
                
                rspmail={}
                if(retVal1 == True):
                    mssg = "sendPatSMSEmail: Patient Email sent successfully to this patient " + fname + "(" + patemail + ")"
                    rspmail["result"] = "success"
                    rspmail["error_message"] = ""
                    rspmail["message"] = mssg
                    rspmail["appointmentid"] = str(apptid)
                else:
                    mssg = "sendPatSMSEmail:  Error sending Patient Email Sent  to this patient " + fname + "(" + patemail + ")"
                    rspmail["result"] = "fail"
                    rspmail["error_message"] = mssg
                    rspmail["appointmentid"] = str(apptid)

                
               
                    
                
            
            patobj["result"] = "success"
            patobj["error_message"] = ""            
                    
        except Exception as e:
            mssg = "sendPatSMSEmail API Exception Error ==>>" + str(e)
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = mssg
            excpobj["error_code"] = ""
            return json.dumps(excpobj)    
            
        logger.loggerpms2.info("Exit sedPatSMSEmail PAT + EMAIL SMS " + json.dumps(rspobj) + " " + json.dumps(rspmail) + " " + json.dumps(patobj))
        return json.dumps(patobj)        


    def sendDocSMSEmail(self,avars):
        logger.loggerpms2.info("Enter Send DOC SMS Email " + json.dumps(avars))
        db = self.db
        rspobj = {}
        rspmail = {}
        docobj = {}
          

        try:
            _mail = Mail()
            ccs = common.getkeyvalue(avars,"ccs","")
            appPath = common.getkeyvalue(avars,"appPath","")
            apptid = int(common.getid(common.getkeyvalue(avars,"appointmentid","0")))
            appts = db((db.vw_appointments.sendsms == True) & (db.vw_appointments.id == apptid) & \
                       ((db.vw_appointments.is_active == True) | ((db.vw_appointments.is_active == False)&(db.vw_appointments.f_status == 'Cancelled')))).\
                select(db.vw_appointments.ALL, db.clinic.ALL,left=db.clinic.on(db.clinic.id==db.vw_appointments.clinicid))
            
            sendsms = common.getboolean(common.getkeyvalue(avars,"sendsms","True"))
            sendemail = common.getboolean(common.getkeyvalue(avars,"sendemail","True"))
            retVal = True
            retVal1 = True
            
            for appt in appts:
                memberid = int(common.getid(appt.vw_appointments.patientmember))
                patientid = int(common.getid(appt.vw_appointments.patient))
                providerid = int(common.getid(appt.vw_appointments.provider))
                clinicid = int(common.getid(appt.vw_appointments.clinicid))
                doctorid = int(common.getid(appt.vw_appointments.doctor))
                appttime = (appt.vw_appointments.f_start_time).strftime('%d/%m/%Y %I:%M %p')
            
                fname   = common.getstring(appt.vw_appointments.f_patientname)  if((appt.vw_appointments.f_patientname != "") & (appt.vw_appointments.f_patientname != None))  else "Patient"
                
                docname = common.getstring(appt.vw_appointments.docname)
                doccell = common.modify_cell(common.getstring(appt.vw_appointments.doccell))
                docemail = common.getstring(appt.vw_appointments.docemail)
                
                pats = db((db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid==memberid) & (db.vw_memberpatientlist.is_active==True)).\
                    select(db.vw_memberpatientlist.cell, db.vw_memberpatientlist.email)
                
                patcell = common.modify_cell(common.getstring(pats[0].cell)) if(len(pats) > 0 ) else "910000000000"
                             
                #send SMS & email to patient
                smsfile = ""
                if(appt.vw_appointments.smsaction == "create"):
                    #new appointment message
                    smsfile  = os.path.join(appPath,'templates/sms','SMS_ApptConfirmDoc.txt') 
                elif(appt.vw_appointments.smsaction == "update"):
                    #reschedule  appointment message
                    smsfile  = os.path.join(appPath,'templates/sms','SMS_ApptRescheduleDoc.txt') 
                elif(appt.vw_appointments.smsaction == "cancel"):
                    smsfile  = os.path.join(appPath,'templates/sms','SMS_ApptCancel.txt') 
                else:
                    smsfile  = os.path.join(appPath,'templates/sms','SMS_ApptCancelDoc.txt')             
        
                f = open(smsfile,'rb')
                temp = Template(f.read())
                f.close()  
                docmessage = temp.template
                docmessage = docmessage.replace("$fname", fname)
                docmessage = docmessage.replace("$docname", docname)
                docmessage = docmessage.replace("$appointmentdate", appttime)
                docmessage = docmessage.replace("$patcell", patcell)
        
                retVal = True
                retVal1 = True
                if((doccell != "") & (sendsms)):
                    #retVal = mail.sendSMS2Email(db,doccell,docmessage)
                    retVal = mail.sendAPI_SMS2Email(db,doccell,docmessage)
                    
                if((docemail != "")&(sendemail)):
                    #retVal1 = mail.groupEmail(db, docemail, ccs, "Appointment: " + appttime, docmessage)  # send email to patient        
                    retVal1 = mail._groupEmail(db, _mail, docemail, ccs, "Appointment: " + appttime, docmessage)  # send email to patient        
                
                
                
                rspobj = {}
                if(retVal == True):
                    mssg = "sendDocSMSEmail: Doctor SMS sent successfully to this doctor " + docname + "(" + doccell + ")"
                    rspobj["appointmentid"] = str(apptid)
                    rspobj["result"] = "success"
                    rspobj["error_message"] = ""
                    rspobj["message"] = mssg
                else:
                    mssg = "sendDocSMSEmail:  Error sending SMS  to this doctor " + docname + "(" + doccell + ")"
                    rspobj["appointmentid"] = str(apptid)
                    rspobj["result"] = "fail"
                    rspobj["error_message"] = mssg
                
               
                
                rspmail={}
                if(retVal1 == True):
                    mssg = "sendDocSMSEmail: Doctor Email sent successfully to this doctor " + docname + "(" + docemail + ")"
                    rspmail["result"] = "success"
                    rspmail["error_message"] = ""
                    rspmail["message"] = mssg
                else:
                    mssg = "sendDocSMSEmail:  Error sending Email to this doctor " + docname + "(" + docemail + ")"
                    rspmail["result"] = "fail"
                    rspmail["error_message"] = mssg
                
              
                
        
          
            docobj["result"] = "success"
            docobj["error_message"] = ""            
        
        
        
        except Exception as e:
            mssg = "sendDocSMSEmail API Exception Error ==>>" + str(e)
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = mssg
            excpobj["error_code"] = ""
            return json.dumps(excpobj)    
            
        logger.loggerpms2.info("Exit sedDocSMSEmail DOC + EMAIL SMS " + json.dumps(rspobj) + " " + json.dumps(rspmail) + " " + json.dumps(docobj))
        
        return json.dumps(docobj)        
    
   
    
    def sendAllAppointmentsSMSEmail(self,avars):
        logger.loggerpms2.info("Enter sendAllAppointmentsSMSEmail " + json.dumps(avars))
         
        db = self.db
        rspObj = {}
        try:
            appPath = common.getkeyvalue(avars,"appPath","")
            props = db(db.urlproperties.id>0).select()
            ccs = props[0].mailcc if(len(props)>0) else ""
            
            #get all appointments for which SMS has not been sent & appointment date > from Date & < to Date
            appts = db((db.vw_appointments.sendsms == True) &\
                       ((db.vw_appointments.is_active == True) | ((db.vw_appointments.is_active == False)&(db.vw_appointments.f_status == 'Cancelled')))).\
                select(db.vw_appointments.id,limitby=(0, 1),orderby_on_limitby = False)
            
            
         
            
            for appt in appts:
                #send SMS to Patient
                avars["appointmentid"]  = str(appt.id)
                avars["ccs"]  = ccs
          
                patrspObj = json.loads(self.sendPatSMSEmail(avars))
                
                            
                #send SMS to Doctor
                avars["appointmentid"]  = str(appt.id)
                avars["ccs"]  = ccs
                docrspObj = json.loads(self.sendDocSMSEmail(avars))
              
                
                #send SMS to Provider
                
                db(db.t_appointment.id == appt.id).update(sendsms = False,sendrem=False) 
                db.commit()
                
       
            rspObj["result"] = "success"
            rspObj["error_message"] = ""
           
            
        
        except Exception as e:
            mssg = "sendSMS API Exception Error ==>>" + str(e)
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = mssg
            excpobj["error_code"] = ""
            return json.dumps(excpobj)    
            
       
        return json.dumps(rspObj)
    
    
     
    def new_appointment(self,avars):
        logger.loggerpms2.info("Enter New_Appointment API ==>" + json.dumps(avars))
        auth = current.auth
        db = self.db
        try:
            
            
            blockappt = common.getboolean(common.getkeyvalue(avars,"block","False"))
            providerid = int(common.getkeyvalue(avars,"providerid","0"))
            clinicid = int(common.getkeyvalue(avars,"clinicid","0"))
            
            memberid = int(common.getkeyvalue(avars,"memberid","0"))
            patientid = int(common.getkeyvalue(avars,"patientid",common.getstring(memberid)))
            cell = common.getkeyvalue(avars,"cell","1111111111")
           
            complaint = common.getkeyvalue(avars,"complaint","")
            
            #if doctorid == 0, then practice owner becomes the defautl doctor
            d = db((db.doctor.providerid == providerid) & (db.doctor.practice_owner == True)&(db.doctor.is_active == True)).select()
            defdoctorid = d[0].id if(len(d) != 0) else 0
            doctorid = int(common.getkeyvalue(avars,"doctorid",common.getstring(defdoctorid)))
            
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
                provs = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.pa_practicename,db.provider.pa_practiceaddress)
                location =  provs[0].pa_practicename + ", " + provs[0].pa_practiceaddress   if(len(provs) == 1) else  ""
            else:
                r = db((db.clinic.id == clinicid) & (db.clinic.is_active == True)).select()
                
                location = r[0].address1 + " " + r[0].address2 + " " + r[0].address3 + " " + r[0].city + " " + r[0].st + " " + r[0].pin if(len(r) == 1) else ""
                location = location.strip()
        
            pat = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).\
                            select(db.vw_memberpatientlist.fullname,db.vw_memberpatientlist.dob,db.vw_memberpatientlist.email,db.vw_memberpatientlist.cell)        
            #check for block
            if((self.isBlocked(startapptdt,endapptdt,doctorid,clinicid)==False)):
                sts = "Blocked" if(blockappt == True) else "Confirmed"
                apptid  = db.t_appointment.insert(f_start_time=startapptdt, f_end_time = endapptdt, f_duration = duration, f_status = sts, \
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

                                          
                
                dobstr = "" if(len(pat) == 0) else common.getstringfromdate(pat[0].dob,"%d/%m/%Y")
                email = "" if(len(pat) == 0) else common.getstring(pat[0].email)
                cell = "" if(len(pat) == 0) else common.getstring(pat[0].cell)
                
                newapptobj= {"result":"success","error_message":"","appointment_ref":appointment_ref,"appointmentid":apptid,"appointment_start":startdtstr,"message":"success","dob":dobstr,"email":email,"cell":cell}    
            else:
                dobstr = "" if(len(pat) == 0) else common.getstringfromdate(pat[0].dob,"%d/%m/%Y")
                email = "" if(len(pat) == 0) else common.getstring(pat[0].email)
                cell = "" if(len(pat) == 0) else common.getstring(pat[0].cell)
                newapptobj = {"result":"blocked","error_message":"","appointment_ref":appointment_ref, "appointmentid":0,"dob":dobstr,"email":email,"cell":cell,"message":"The appointment date and time is blocked"}

        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "New_Appointment API Exception Error - " + str(e)
            excpobj["error_code"] = ""
            return json.dumps(excpobj)
        
        return json.dumps(newapptobj)

    def update_appointment(self,avars):
        logger.loggerpms2.info("Enter Update_Appointment API ==>" + json.dumps(avars))
        db = self.db
        auth = current.auth
        
        
        apptobj = {}
        
        
        try:
            blockappt = common.getboolean(common.getkeyvalue(avars,"block","False"))
            
            appointmentid = int(common.getkeyvalue(avars,"appointmentid","0"))
            ds = db((db.t_appointment.id == appointmentid) & (db.t_appointment.is_active == True)).select()  
            if(len(ds) == 1):
                
                def_start_time_str = common.getstringfromdate(ds[0].f_start_time,"%d/%m/%Y %H:%M")
                def_end_time_str  = common.getstringfromdate(ds[0].f_end_time,"%d/%m/%Y %H:%M")
                notes = common.getkeyvalue(avars,"notes",ds[0].description)
                cc = common.getkeyvalue(avars,"complaint",ds[0].f_title)
                
                memberid = int(common.getkeyvalue(avars,"memberid","0" if(ds[0].patientmember == None) else str(ds[0].patientmember)))
                patientid = int(common.getkeyvalue(avars,"patientid","0" if(ds[0].patient == None) else str(ds[0].patient)))              
                pat = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).\
                                           select(db.vw_memberpatientlist.fullname,db.vw_memberpatientlist.dob,db.vw_memberpatientlist.email,db.vw_memberpatientlist.cell)     
                
                sts = "Blocked" if (blockappt == True) else common.getkeyvalue(avars,"f_status",ds[0].f_status)
                db(db.t_appointment.id == appointmentid).update(\
                    
                    f_uniqueid = int(common.getkeyvalue(avars,"f_uniqueid","0" if(ds[0].f_uniqueid == None) else str(ds[0].f_uniqueid))),
                    f_title = cc,
                   
                    f_patientname = common.getkeyvalue(avars,"f_patientname",ds[0].f_patientname),
                    f_location = common.getkeyvalue(avars,"f_location",ds[0].f_location),
                    f_status = sts,
                    description = notes,
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
                    
                    blockappt = blockappt,
                    sendsms = common.getboolean(common.getkeyvalue(avars,"sendsms","False")),
                    sendrem = common.getboolean(common.getkeyvalue(avars,"sendrem","False")),
                    
                    modified_on=common.getISTFormatCurrentLocatTime(),
                    modified_by= 1 if(auth.user == None) else auth.user.id
                    
                    )
                
                common.logapptnotes(db, cc, notes, appointmentid)
                dobstr = "" if(len(pat) == 0) else common.getstringfromdate(pat[0].dob,"%d/%m/%Y")
                email = "" if(len(pat) == 0) else common.getstring(pat[0].email)
                cell = "" if(len(pat) == 0) else common.getstring(pat[0].cell)
                
                apptobj= {"result":"success", "appointmentid":appointmentid,"dob":dobstr,"email":email,"cell":cell,"error_message":"","message":"Appointment updated successfully"}
                
            else:
                apptobj = {"result":"fail", "appointmentid":appointmentid,"error_message":"Error Updating Appointment","error_code":""}
                
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Update Appointment API Exception Error - " + str(e)
            return json.dumps(excpobj)       
        
               
        return json.dumps(apptobj)
        
    def cancel_appointment(self,avars):
        logger.loggerpms2.info("Enter Cancel_Appointment API ==>"  + json.dumps(avars))
        db = self.db
        auth = current.auth
        
        
        apptobj = {}
        
        
        try:
            
            appointmentid = int(common.getkeyvalue(avars,"appointmentid","0"))
            appt = db((db.t_appointment.id == appointmentid) & (db.t_appointment.is_active == True)).select(db.t_appointment.description,db.t_appointment.f_title)
            desc = "" if len(appt) != 1 else appt[0].description
            notes = common.getkeyvalue(avars,"notes",desc)
            cc = "" if len(appt) != 1 else appt[0].f_title
            
            db((db.t_appointment.id == appointmentid)).update(\
                description = notes,
                f_status = "Cancelled"  ,  
                is_active = False,
                    
                modified_on=common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id
                
            )
            common.logapptnotes(db,cc,notes,appointmentid)
            apptobj= {"result":"success", "appointmentid":appointmentid,"error_message":"", "error_code":"", "message":"Appointment Cancelled successfully"}
            
                
        except Exception as e:
            excpobj = {}
            excpobj["result"] = False
            excpobj["error_message"] = "Cancel Appointment API Exception Error - " + str(e)
            return json.dumps(excpobj)       
        
                 
        return json.dumps(apptobj)
                  
    
    def get_appointment(self,avars):
        logger.loggerpms2.info("Enter Get_Appointment API ==> " +str(avars))
        auth = current.auth
        db = self.db
        appointmentid= 0
        try:
            blockappt = common.getboolean(common.getkeyvalue(avars,"block","False"))
            appointmentid = int(common.getkeyvalue(avars,"appointmentid","0"))
            appt = db((db.vw_appointments.id == appointmentid) &  (db.vw_appointments.blockappt == blockappt) &  (db.vw_appointments.is_active == True)).select()
            providerid = appt[0].provider if(len(appt) == 1) else 0
            memberid = int(common.getid(appt[0].patientmember)) if(len(appt) == 1) else 0
            patientid = int(common.getid(appt[0].patient)) if(len(appt) == 1) else 0

            pat = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).\
                select(db.vw_memberpatientlist.fullname,db.vw_memberpatientlist.patientmember,db.vw_memberpatientlist.dob,db.vw_memberpatientlist.email,db.vw_memberpatientlist.cell)     
            
            
            dobstr = "" if(len(pat) == 0) else common.getstringfromdate(pat[0].dob,"%d/%m/%Y")
            email = "" if(len(pat) == 0) else common.getstring(pat[0].email)
            cell = "" if(len(pat) == 0) else common.getstring(pat[0].cell)
            patientmember = "" if(len(pat) == 0) else common.getstring(pat[0].patientmember)
            
            prov = db(db.provider.id == providerid).select(db.provider.pa_locationurl)
            locationurl = prov[0].pa_locationurl if len(prov) == 1 else ""
            apptobj = {}
            
            


                              
            if(len(appt) == 1):
                x=str(providerid)
                x=str(appointmentid)
                x= (appt[0].f_start_time).strftime("%d/%m/%Y %I:%M %p")
                x= "30" if(common.getstring(appt[0].f_duration) == "") else int(appt[0].f_duration)
                x=common.getstring(appt[0].f_title)
                x=common.getstring(appt[0].description)
                x=common.getstring(appt[0].f_location)
                x=locationurl
                x=common.getstring(appt[0].f_status) if(common.getstring(appt[0].f_status) != "") else "Confirmed"
                x=common.getid(appt[0].patientmember)
                x=common.getid(appt[0].patient)
                x=common.getstring(appt[0].f_patientname)
                x=common.modify_cell(appt[0].cell)
                x=common.getid(appt[0].clinicid)
                x=common.getid(appt[0].doctor)
                x=common.getstring(appt[0].docname)
                x=common.modify_cell(appt[0].doccell)
                x=common.getstring(appt[0].color) if(common.getstring(appt[0].color) != "") else "#ff0000"
                x=common.modify_cell(appt[0].provcell)
                x=common.getstring(appt[0].clinic_ref)
                x=common.getstring(appt[0].clinic_name)
                x=common.getboolean(appt[0].blockappt)
                dobstr = common.getstringfromdate(appt[0].dob,"%d/%m/%Y")
                apptobj= {
                    "providerid":str(providerid),
                    "appointmentid":str(appointmentid),
                    "apptdatetime" : (appt[0].f_start_time).strftime("%d/%m/%Y %I:%M %p"),
                    "apptenddatetime" : (appt[0].f_end_time).strftime("%d/%m/%Y %I:%M %p"),
                    "duration": "30" if(common.getstring(appt[0].f_duration) == "") else str(int(appt[0].f_duration)),
                    "days":"0" if(common.getstring(appt[0].f_duration) == "") else str(int(round((appt[0].f_duration)/1440))),
                    "complaint":common.getstring(appt[0].f_title),
                    "notes":common.getstring(appt[0].description),
                    "location":common.getstring(appt[0].f_location),
                    "locationurl":locationurl,
                    "status":common.getstring(appt[0].f_status) if(common.getstring(appt[0].f_status) != "") else "Confirmed",
                    "memberid":common.getid(appt[0].patientmember),
                    "patientid":common.getid(appt[0].patient),
                    "patientname" : common.getstring(appt[0].f_patientname),
                    "patientmember" : patientmember,
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
                    "gender":common.getstring(appt[0].gender),
                    "dob":dobstr,
                    "age":calculateAge(appt[0].dob) if(appt[0].dob != None) else 0,
                    "email":email,
                    "cell":cell,
                    "result":"success",
                    "error_message":""
                      
                    }              
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Get_Appointment API Exception Error - " + str(e) + "apptid = " +str(appointmentid)
            excpobj["error_code"] = ""
            return json.dumps(excpobj)
        
        return json.dumps(apptobj)
    
    def get_appointment_limited(self,avars):
            logger.loggerpms2.info("Enter Get_Appointment_Limited API ==> " +str(avars))
            auth = current.auth
            db = self.db
            appointmentid= 0
            try:
                blockappt = common.getboolean(common.getkeyvalue(avars,"block","False"))
                appointmentid = int(common.getkeyvalue(avars,"appointmentid","0"))
                appt = db((db.vw_appointments.id == appointmentid) &\
                          (db.vw_appointments.is_active == True)).select()
                
                    
                
                providerid = appt[0].provider if(len(appt) == 1) else 0
                memberid = int(common.getid(appt[0].patientmember)) if(len(appt) == 1) else 0
                patientid = int(common.getid(appt[0].patient)) if(len(appt) == 1) else 0
    
                pat = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).\
                    select(db.vw_memberpatientlist.fullname,db.vw_memberpatientlist.dob,db.vw_memberpatientlist.email,db.vw_memberpatientlist.cell)     
                
                
                dobstr = "" if(len(pat) == 0) else common.getstringfromdate(pat[0].dob,"%d/%m/%Y")
                email = "" if(len(pat) == 0) else common.getstring(pat[0].email)
                cell = "" if(len(pat) == 0) else common.getstring(pat[0].cell)
    
                
                prov = db(db.provider.id == providerid).select(db.provider.pa_locationurl)
                locationurl = prov[0].pa_locationurl if len(prov) == 1 else ""
                apptobj = {}
                
                
    
    
                                  
                if(len(appt) == 1):
                    #x=str(providerid)
                    #x=str(appointmentid)
                    #x= (appt[0].f_start_time).strftime("%d/%m/%Y %I:%M %p")
                    #x= "30" if(common.getstring(appt[0].f_duration) == "") else int(appt[0].f_duration)
                    #x=common.getstring(appt[0].f_title)
                    #x=common.getstring(appt[0].description)
                    #x=common.getstring(appt[0].f_location)
                    #x=locationurl
                    #x=common.getstring(appt[0].f_status) if(common.getstring(appt[0].f_status) != "") else "Open"
                    #x=common.getid(appt[0].patientmember)
                    #x=common.getid(appt[0].patient)
                    #x=common.getstring(appt[0].f_patientname)
                    #x=common.modify_cell(appt[0].cell)
                    #x=common.getid(appt[0].clinicid)
                    #x=common.getid(appt[0].doctor)
                    #x=common.getstring(appt[0].docname)
                    #x=common.modify_cell(appt[0].doccell)
                    #x=common.getstring(appt[0].color) if(common.getstring(appt[0].color) != "") else "#ff0000"
                    #x=common.modify_cell(appt[0].provcell)
                    #x=common.getstring(appt[0].clinic_ref)
                    #x=common.getstring(appt[0].clinic_name)
                    #x=common.getboolean(appt[0].blockappt)
                    dobstr = common.getstringfromdate(appt[0].dob,"%d/%M/%Y")
                    apptobj= {
                        #"providerid":str(providerid),
                        "appointmentid":str(appointmentid),
                        "apptdatetime" : (appt[0].f_start_time).strftime("%d/%m/%Y %I:%M %p"),
                        #"apptenddatetime" : (appt[0].f_end_time).strftime("%d/%m/%Y %I:%M %p"),
                        "duration": "30" if(common.getstring(appt[0].f_duration) == "") else str(int(appt[0].f_duration)),
                        #"days":"0" if(common.getstring(appt[0].f_duration) == "") else str(int(round((appt[0].f_duration)/1440))),
                        #"complaint":common.getstring(appt[0].f_title),
                        #"notes":common.getstring(appt[0].description),
                        #"location":common.getstring(appt[0].f_location),
                        #"locationurl":locationurl,
                        "status":common.getstring(appt[0].f_status) if(common.getstring(appt[0].f_status) != "") else "Confirmed",
                        #"memberid":common.getid(appt[0].patientmember),
                        #"patientid":common.getid(appt[0].patient),
                        "patientname" : common.getstring(appt[0].f_patientname),
                        "patientcode" : common.getstring(appt[0].membercode),
                        #"patcell":common.modify_cell(appt[0].cell),
                        #"clinicid":common.getid(appt[0].clinicid),
                        #"doctorid":common.getid(appt[0].doctor),
                        "docname":common.getstring(appt[0].docname),
                        #"doccell":common.modify_cell(appt[0].doccell),
                        #"color": common.getstring(appt[0].color) if(common.getstring(appt[0].color) != "") else "#ff0000",
                        #"provcell":common.modify_cell(appt[0].provcell),
                        #"clinic_ref":common.getstring(appt[0].clinic_ref),
                        #"clinic_name":common.getstring(appt[0].clinic_name),
                        #"block":common.getboolean(appt[0].blockappt),
                        #"gender":common.getstring(appt[0].gender),
                        #"dob":dobstr,
                        #"age":calculateAge(appt[0].dob) if(appt[0].dob != None) else 0,
                        #"email":email,
                        "cell":cell,
                        "hmopatientmember":common.getboolean(appt[0].hmopatientmember)  if(appt[0].hmopatientmember != "") else False
                       
                          
                        } 
                    
                    
            except Exception as e:
                excpobj = {}
                excpobj["result"] = "fail"
                excpobj["error_message"] = "Get_Appointment API Exception Error - " + str(e) + "apptid = " +str(appointmentid)
                excpobj["error_code"] = ""
                return json.dumps(excpobj)
            
            return json.dumps(apptobj)
    
    
    def list_appointment_limited(self,avars):
        logger.loggerpms2.info("Enter List Appointments Limited  " + json.dumps(avars))
        db = self.db
        auth = current.auth
        
        try:
            providerid = int(common.getkeyvalue(avars,"providerid","0"))
            clinicid = int(common.getkeyvalue(avars,"clinicid","0"))
            doctorid = int(common.getkeyvalue(avars,"doctorid","0"))
            memberid = int(common.getkeyvalue(avars,"memberid","0"))
            patientid = int(common.getkeyvalue(avars,"patientid","0"))
            blockappt = common.getboolean(common.getkeyvalue(avars,"block","False"))
            status = common.getkeyvalue(avars,"status","")
            
            page = common.getkeyvalue(avars,"page","0")
            page = 0 if((page==None)|(page == "")) else int(common.getid(page))
        
            maxcount = common.getkeyvalue(avars,"maxcount","0")
            maxcount = 0 if((maxcount==None)|(maxcount == "")) else int(common.getid(maxcount))
            
            
            
                   
            page = page -1
            urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
            items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
            limitby = None if page < 0 else ((page)*items_per_page,(page+1)*items_per_page)             
            
            query = (1==1)
            if(blockappt == False):
                if(status == ""):
                    query = query & (db.t_appointment.blockappt == blockappt)& (db.t_appointment.is_active == True)
                else:
                    query = query & (db.t_appointment.blockappt == blockappt) &  (db.t_appointment.f_status == status)& (db.t_appointment.is_active == True)
                
                
                #query = ((db.t_appointment.blockappt == blockappt) & (db.t_appointment.f_status != "Blocked") & (db.t_appointment.is_active == True))
            else:
                query = (((db.t_appointment.blockappt == blockappt) | (db.t_appointment.f_status == "Blocked")) & (db.t_appointment.is_active == True))
                
            
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
            
                
                
            currdate = common.getISTFormatCurrentLocatTime()
          

            
            fromdtstr = common.getkeyvalue(avars,"from_date",common.getstringfromdate(currdate,"%d/%m/%Y %H:%M"))
            fromapptdt = None
            fromapptdt90 = None
            if(fromdtstr != None):
                fromapptdt = common.getdatefromstring(fromdtstr, "%d/%m/%Y %H:%M")
                fromapptdt90 = fromapptdt + timedelta(days=90)

            todtstr = common.getkeyvalue(avars,"to_date",common.getstringfromdate(fromapptdt90,"%d/%m/%Y %H:%M"))
            toapptdt = None
            if(todtstr != None):
                toapptdt = common.getdatefromstring(todtstr, "%d/%m/%Y %H:%M")
            

            if(fromapptdt != None):
                query = query & (db.t_appointment.f_start_time >= fromapptdt)
                
            if(toapptdt != None):
                query = query & (db.t_appointment.f_start_time <= toapptdt)
        
            appts = db((query)).select(db.t_appointment.ALL,orderby=db.t_appointment.f_start_time,limitby=limitby)
            
            apptlist = []
                   
            for appt in appts:
                apptobj = json.loads(self.get_appointment_limited({"appointmentid":appt.id,"block":blockappt}))
                apptlist.append(apptobj)             
            
            apptobj = {"result":"success", "error_message":"", "error_code":"", "page":str(page+1),"apptcount":str(len(appts)), "apptlist":apptlist}
        
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "List_Appointment_limited  API Exception Error - " + str(e)
            excpobj["error_code"] = ""
            return json.dumps(excpobj)    
        
        return json.dumps(apptobj)

    
    def list_appointment(self,avars):
        logger.loggerpms2.info("Enter List Appointments " + json.dumps(avars))
        db = self.db
        auth = current.auth
        
        try:
            
            page = common.getkeyvalue(avars,"page","0")
            page = 0 if((page==None)|(page == "")) else int(common.getid(page))
    
            maxcount = common.getkeyvalue(avars,"maxcount","0")
            maxcount = 0 if((maxcount==None)|(maxcount == "")) else int(common.getid(maxcount))

            
            providerid = int(common.getkeyvalue(avars,"providerid","0"))
            clinicid = int(common.getkeyvalue(avars,"clinicid","0"))
            doctorid = int(common.getkeyvalue(avars,"doctorid","0"))
            memberid = int(common.getkeyvalue(avars,"memberid","0"))
            patientid = int(common.getkeyvalue(avars,"patientid","0"))
            blockappt = common.getboolean(common.getkeyvalue(avars,"block","False"))
            status = common.getkeyvalue(avars,"status","")
            
            urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
        
            page = page -1
            urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
            items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
            limitby = None if page < 0 else ((page)*items_per_page,(page+1)*items_per_page)      
            
            query = (1==1)
            if(blockappt == False):
                if(status == ""):
                    query = query & (db.t_appointment.blockappt == blockappt)& (db.t_appointment.is_active == True)
                else:
                    query = query & (db.t_appointment.blockappt == blockappt) &  (db.t_appointment.f_status == status)& (db.t_appointment.is_active == True)
                
                
                #query = ((db.t_appointment.blockappt == blockappt) & (db.t_appointment.f_status != "Blocked") & (db.t_appointment.is_active == True))
            else:
                query = (((db.t_appointment.blockappt == blockappt) | (db.t_appointment.f_status == "Blocked")) & (db.t_appointment.is_active == True))
            
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


           
                

            currdate = common.getISTFormatCurrentLocatTime()

            fromdtstr = common.getkeyvalue(avars,"from_date",common.getstringfromdate(currdate,"%d/%m/%Y %H:%M"))
            fromapptdt = None
            fromapptdt90 = None
            if(fromdtstr != None):
                fromapptdt = common.getdatefromstring(fromdtstr, "%d/%m/%Y %H:%M")
                fromapptdt90 = fromapptdt + timedelta(days=90)

            todtstr = common.getkeyvalue(avars,"to_date",common.getstringfromdate(fromapptdt90,"%d/%m/%Y %H:%M"))
            toapptdt = None
            if(todtstr != None):
                toapptdt = common.getdatefromstring(todtstr, "%d/%m/%Y %H:%M")
            
            if(fromapptdt != None):
                query = query & (db.t_appointment.f_start_time >= fromapptdt)
                
            if(toapptdt != None):
                query = query & (db.t_appointment.f_start_time <= toapptdt)
        
            appts = db((query)).select(db.t_appointment.ALL,orderby=db.t_appointment.f_start_time,limitby=limitby)
            
            apptlist = []
                   
            for appt in appts:
                apptobj = json.loads(self.get_appointment({"appointmentid":appt.id,"block":blockappt}))
                apptlist.append(apptobj)             
            
            apptobj = {"result":"success", "error_message":"", "error_code":"", "apptcount":str(len(appts)), "page":str(page+1),"apptlist":apptlist}
        
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "List_Appointment API Exception Error - " + str(e)
            excpobj["error_code"] = ""
            return json.dumps(excpobj)    
        
        return json.dumps(apptobj)

    
    def add_block_datetime(self,avars):
        
        logger.loggerpms2.info("Enter Add Block Datetime API")
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
        avars["appointment_end"] = common.getstringfromdate(block_end_date,"%d/%m/%Y %H:%M")
        avars["days"] = int(duration)/1440
        rsp = json.loads(self.new_appointment(avars))
        rsp["appointment_end"] = common.getstringfromdate(block_end_date,"%d/%m/%Y %H:%M")
        rsp["days"] = str(int(round(duration/1440)))
        
        return json.dumps(rsp)
    
    def remove_block_datetime(self,avars):
  
        logger.loggerpms2.info("Enter Remove_Block API ==>" + str(avars))
        db = self.db
        auth = current.auth
        
        
        apptobj = {}
        
        
        try:
            #block_start_str = common.getkeyvalue(avars,"block_start",None)
            #if((block_start_str == None) | (block_start_str == "") ):
                #excpobj = {}
                #excpobj["result"] = "fail"
                #excpobj["error_message"] = "Start Block Date Time not specified"
                #excpobj["error_code"] = ""
                #return json.dumps(excpobj)            
    
            #block_start_date = common.getdatefromstring(block_start_str, "%d/%m/%Y %H:%M")
            
            
            #block_end_str = common.getkeyvalue(avars,"block_end",None)
            #if((block_end_str == None) | (block_end_str == "") ):
                #excpobj = {}
                #excpobj["result"] = "fail"
                #excpobj["error_message"] = "End Block Date Time not specified"
                #excpobj["error_code"] = ""
                #return json.dumps(excpobj)            
    
            #block_end_date   = common.getdatefromstring(block_end_str, "%d/%m/%Y %H:%M")            
     
            
            blockid = int(common.getkeyvalue(avars,"blockid","0"))
            db((db.t_appointment.f_uniqueid == blockid)).update(\
                blockappt = False,   
                is_active = True,
                f_status = 'Open',
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
    
    
    def remove_block_datetime_byID(self,avars):
      
            logger.loggerpms2.info("Enter Remove_Block_byID API ==>"+ str(avars))
            db = self.db
            auth = current.auth
            
            
            apptobj = {}
            
            
            try:
                
                
                blockid = int(common.getkeyvalue(avars,"blockid","0"))
                db((db.t_appointment.f_uniqueid == blockid)).update(\
                    blockappt = False,   
                    is_active = True,
                    f_status = 'Open',
                        
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
        logger.loggerpms2.info("Enter API reSchedule  " + json.dumps(avars))
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
        logger.loggerpms2.info("Enter API list_day_appointment_count  " + json.dumps(avars))

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
        
        logger.loggerpms2.info("Enter list_appointments_byday  " + json.dumps(avars))
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
    
    
    #this method returns number of appointments/day for all the days in a month
    def list_appointment_count_bymonth(self,avars):
        logger.loggerpms2.info("Enter list_appointment_count_bymonth  " + json.dumps(avars))

        db = self.db
        try:
           
            
            providerid = 0 if(common.getkeyvalue(avars,"providerid","0") == "") else int(common.getkeyvalue(avars,"providerid","0"))
            clinicid = 0 if(common.getkeyvalue(avars,"clinicid","0") == "") else int(common.getkeyvalue(avars,"clinicid","0"))
            doctorid = 0 if(common.getkeyvalue(avars,"doctorid","0") == "") else int(common.getkeyvalue(avars,"doctorid","0")) 
            blockappt = common.getboolean(common.getkeyvalue(avars,"block","False"))
            blockappt = 'T' if(blockappt == True) else 'F'
            month = int(common.getkeyvalue(avars,"month",(datetime.date.today()).strftime("%m")))
            year = int(common.getkeyvalue(avars,"year",(datetime.date.today()).strftime("%Y")))            
            
            
            #count of active / unblocked appointment counts
            start = str(year) + "-" + str(month).zfill(2) + "-01 00:00:00"
            end   = str(year) + "-" + str(month).zfill(2) + "-31 23:59:00"  #no need to take 30 or 31 days - just default to 31 days
            
            strsql = "select DATE(f_start_time) as apptdate, count(*) as apptcount,f_duration from vw_appointments where (1=1) "

            if(providerid != 0):
                strsql = strsql + " AND provider = " + str(providerid)

            if(clinicid != 0):
                strsql = strsql + " AND clinicid = " + str(clinicid)
                
            if(doctorid != 0):
                strsql = strsql + " AND doctor = " + str(doctorid)
            
            strsql = strsql + " and f_start_time >= '"  + start +  "'"
            strsql = strsql + " and f_start_time <= '"  + end +  "'"
            strsql = strsql + " and blockappt = '" + blockappt +"'"            
            strsql = strsql + " and is_active = 'T' "
            
           
            
            strsql = strsql + " group by DATE(f_start_time)"
          
            
            ds = db.executesql(strsql)
            apptobj = {}
            apptlist = []
            blocklist = []
        
            
            for i in xrange(0,len(ds)):
                x = {
                   
                    "apptdate": ds[i][0].strftime("%d/%m/%Y"),
                    "count": int(common.getid(ds[i][1])),
                    "days":str(round(common.getvalue(ds[i][2])/1439))
                }
                apptlist.append(x)
            
            apptobj["result"] = "success"
            apptobj["error_message"] = ""
            apptobj["error_code"]=""
            apptobj["apptlist"] = apptlist
          
            
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Get Appointments Count by Month  API Exception Error - " + str(e)
            excpobj["error_code"] = ""
            return json.dumps(excpobj)
        logger.loggerpms2.info("Exit list_appointment_count_bymonth  " + json.dumps(apptobj))
        return json.dumps(apptobj)       