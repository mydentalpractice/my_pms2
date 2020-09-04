import os
import datetime
import time
from datetime import timedelta
from string import Template

#import sys
#sys.path.app('modules')

from applications.my_pms2.modules import common
from applications.my_pms2.modules import mail
from applications.my_pms2.modules import logger

datefmt = "%d/%m/%Y"
datetimefmt = "%d/%m/%Y %H:%M:%S"

def senddoctornewaptgroupsms(db,appPath,ccs,doctorid,smsdate,providerid=0):
    
    
    logger.loggerpms2.info("Enter senddoctornewaptgroupsms")
    
    docname = ""
    doccell = ""
    docemail = ""
    docmessage = ""
    
    provcell = ""
    
    fname = ""
    patcell = ""

    retval = False 

    #get all new appointments for this doctor and provider
    appts = db((db.vw_appointments.sendsms == True) & (db.vw_appointments.doctor == doctorid) &\
               ((db.vw_appointments.is_active == True) | ((db.vw_appointments.is_active == False)&(db.vw_appointments.f_status == 'Cancelled')))).select() \
            if(providerid == 0) else \
            db((db.vw_appointments.sendsms == True) & (db.vw_appointments.doctor == doctorid) & (db.vw_appointments.provider == providerid) & \
               ((db.vw_appointments.is_active == True) | ((db.vw_appointments.is_active == False)&(db.vw_appointments.f_status == 'Cancelled')))).select()    
    
     
        
    apptcount = common.getid(len(appts))
    
    
    if(apptcount > 0):
        grpdocmessage = ("$docname,\nYou have $count appointments as of  $smsdate\n").replace("$count", str(apptcount)).replace("$smsdate", smsdate.strftime("%d/%m/%Y"))
        
        if(len(appts) > 0):   # the doctor information is goign to be same for this group of appointments
            doccell = common.modify_cell(common.getstring(appts[0].doccell))
            docname  = common.getstring(appts[0].docname)
            docemail = common.getstring(appts[0].docemail) 
            grpdocmessage = grpdocmessage.replace("$docname", docname)
            
            docsms = common.getboolean(appts[0].docsms)
            docemailflag = common.getboolean(appts[0].docemailflag)
            groupsms = common.getboolean(appts[0].groupsms)
            groupemail = common.getboolean(appts[0].groupemail)
            
        for appt in appts:
            patientid = int(common.getid(appt.patient))
            fname   = common.getstring(appt.f_patientname)  if((appt.f_patientname != "") & (appt.f_patientname != None))  else "Patient"
            patcell = common.modify_cell(common.getstring(appt.cell))
            appttime = (appt.f_start_time).strftime('%d/%m/%Y %I:%M %p')
            location = common.getstring(appt.f_location)
            provcell = common.modify_cell(common.getstring(appt.provcell))
            provtel = common.getstring(appt.provtel)
           
            pats = db(db.patientmember.id == patientid).select(db.patientmember.cell, db.patientmember.email)
            if(patcell == ""):
                patcell = common.modify_cell(common.getstring(pats[0].cell)) if(len(pats) > 0 ) else "910000000000"
            patemail = common.getstring(pats[0].email) if(len(pats) > 0 ) else "x@x.com"


            #grpdocmessage = grpdocmessage + "\n" + fname + " (+" + patcell  + "): " + appttime
           
            #send SMS & email to patient
            smsfile = ""
            if(appt.smsaction == "create"):
                #new appointment message
                smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptConfirm.txt') 
            elif(appt.smsaction == "update"):
                #reschedule  appointment message
                smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptReschedule.txt') 
            elif(appt.smsaction == "cancel"):
                smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptCancel.txt') 
            else:
                smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptConfirm.txt') 
                
            f = open(smsfile,'rb')
            temp = Template(f.read())
            f.close()  
            patmessage = temp.template
            patmessage = patmessage.replace("$fname", fname)
            patmessage = patmessage.replace("$docname", docname)
            patmessage = patmessage.replace("$appointmentdate", appttime)
            patmessage = patmessage.replace("$provplace", location)
            patmessage = patmessage.replace("$doccell", "+" + doccell)
            patmessage = patmessage.replace("$clinicno", provtel) if(provtel != "" ) else patmessage.replace("$clinicno", "+" + doccell)  
            if(patcell != ""):
                mail.sendSMS2Email(db,patcell,patmessage)
            if(patemail != ""):
                mail.groupEmail(db, patemail, ccs, "Appointment: " + appttime, patmessage)  # send email to patient
            
            #send SMS to doctor 
            if(appt.smsaction == "create"):
                #new appointment message
                smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptConfirmDoc.txt') 
            elif(appt.smsaction == "update"):
                #reschedule  appointment message
                smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptRescheduleDoc.txt') 
            elif(appt.smsaction == "cancel"):
                smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptCancel.txt') 
            else:
                smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptCancelDoc.txt')             
        
            f = open(smsfile,'rb')
            temp = Template(f.read())
            f.close()  
            docmessage = temp.template
            docmessage = docmessage.replace("$fname", fname)
            docmessage = docmessage.replace("$docname", docname)
            docmessage = docmessage.replace("$appointmentdate", appttime)
            docmessage = docmessage.replace("$patcell", "+" + patcell) 

            grpdocmessage = grpdocmessage + docmessage.replace(docname+",","" )
            
            if((doccell != "") & (docsms == True)):
                db(db.t_appointment.id == appt.id).update(sendsms = False)
                db.commit()
                retval = mail.sendSMS2Email(db,doccell,docmessage)
                
            if((docemail != "") & (docemailflag == True)):
                mail.groupEmail(db, docemail, ccs, "Appointment: " + appttime, docmessage)  # send email to patient
            
        
        try:
            if(groupsms == True):
                for appt in appts:
                    db(db.t_appointment.id == appt.id).update(sendsms = False)
                    db.commit()
                if(doccell == provcell):  # do not send sms if the doctor is same as provider  but keep thw docmessage
                    retval = True
                else:
                    retval = mail.sendSMS2Email(db, doccell, grpdocmessage) 
                #send email irrespective whether SMS sent or no.
                if(docemail != ""):
                    retval1 = mail.groupEmail(db, docemail, ccs, "Appointments:" + appttime, grpdocmessage) 
            else:
                grpdocmessage = ""
                apptcount = 0
                retval = False       
        except Exception,e:
            logger.loggerpms2.info("Senddoctornewapptgroupseme Exception " + str(e))
        
    return dict(retval = retval, docmessage = grpdocmessage, docsmscount = apptcount)





def senddoctorremaptgroupsms(db,appPath,ccs,doctorid,smsdate,smsdateUSFormat,providerid=0):
    
    docname = ""
    doccell = ""
    docemail = ""
    
    provcell = ""
    
    fname = ""
    patcell = ""
    
    docmessage = ""
      
    retval = False 


    #get all new appointments for this doctor 
    appts = db((db.vw_appointments.sendsms == False)  & (db.vw_appointments.sendrem == True) & (db.vw_appointments.doctor == doctorid) \
                  & ((db.vw_appointments.f_start_time).strftime("%Y-%m-%d") == smsdateUSFormat) \
                  & (db.vw_appointments.is_active == True)).select()
            
    apptcount = common.getid(len(appts))
    
    
    if(apptcount > 0):
    
        grpdocmessage = ("$docname,\nReminder for $count appointments as of  $smsdate\n").replace("$count", str(apptcount)).replace("$smsdate", smsdate.strftime("%d/%m/%Y"))
        
        # the doctor information is goign to be same for this group of appointments
        doccell = common.modify_cell(common.getstring(appts[0].doccell))
        docname  = common.getstring(appts[0].docname)
        docemail = common.getstring(appts[0].docemail) 
        grpdocmessage = grpdocmessage.replace("$docname", docname)
        
        #flags for this doc
        docsms = common.getboolean(appts[0].docsms)
        docemailflag = common.getboolean(appts[0].docemailflag)
        groupsms = common.getboolean(appts[0].groupsms)
        groupemail = common.getboolean(appts[0].groupemail)
        
        #group all messages for this doctor
        for appt in appts:
            patientid = int(common.getid(appt.patient))
            fname   = common.getstring(appt.f_patientname)  if((appt.f_patientname != "") & (appt.f_patientname != None))  else "Patient"
            patcell = common.modify_cell(common.getstring(appt.cell))
            appttime = (appt.f_start_time).strftime('%d/%m/%Y %I:%M %p')
            location = common.getstring(appt.f_location)
            provcell = common.modify_cell(common.getstring(appt.provcell))
            provtel = common.getstring(appt.provtel)
           
            pats = db(db.patientmember.id == patientid).select(db.patientmember.cell, db.patientmember.email)
            if(patcell == ""):
                patcell = common.modify_cell(common.getstring(pats[0].cell)) if(len(pats) > 0 ) else "910000000000"
            patemail = common.getstring(pats[0].email) if(len(pats) > 0 ) else "x@x.com"


            grpdocmessage = grpdocmessage + "\n" + fname + " (+" + patcell  + "): " + appttime
            
            #send SMS & email to patient
            smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptReminder.txt') 
                
            f = open(smsfile,'rb')
            temp = Template(f.read())
            f.close()  
            patmessage = temp.template
            patmessage = patmessage.replace("$fname", fname)
            patmessage = patmessage.replace("$docname", docname)
            patmessage = patmessage.replace("$appointmentdate", appttime)
            patmessage = patmessage.replace("$provplace", location)
            patmessage = patmessage.replace("$doccell", "+" + doccell)
            patmessage = patmessage.replace("$clinicno", provtel) if(provtel != "" ) else patmessage.replace("$clinicno", doccell)  
            if(patcell != ""):
                mail.sendSMS2Email(db,patcell,patmessage)
            if(patemail != ""):
                mail.groupEmail(db, patemail, ccs, "Appointment: " + appttime, patmessage)  # send email to patient
            
            #send SMS to doctor 
            if(docsms == True):
                smsfile  = os.path.join(appPath,'templates/reminders/sms','SMS_ApptReminderDoc.txt') 
                
                
                f = open(smsfile,'rb')
                temp = Template(f.read())
                f.close()  
                docmessage = temp.template
                docmessage = docmessage.replace("$fname", fname)
                docmessage = docmessage.replace("$docname", docname)
                docmessage = docmessage.replace("$appointmentdate", appttime)
                docmessage = docmessage.replace("$patcell", " +" + patcell)               
                if(doccell != ""):
                    db(db.t_appointment.id == appt.id).update(sendsms = False)
                    db.commit()
                    retval = mail.sendSMS2Email(db,doccell,docmessage)
                if((docemail != "") & (docemailflag == True)):
                    mail.groupEmail(db, docemail, ccs, "Appointment: " + appttime, docmessage)  # send email to patient
            
        
        if(groupsms == True):
            for appt in appts:
                db(db.t_appointment.id == appt.id).update(sendsms = False)
                db.commit()
            
            if(doccell == provcell):  # do not send sms if the doctor is same as provider  but keep thw docmessage
                retval = True
            else:
                retval = mail.sendSMS2Email(db, doccell, grpdocmessage) 
         
            #send email irrespective whether SMS sent or no.
            if(docemail != ""):
                retval1 = mail.groupEmail(db, docemail, ccs, "Appointments:" + appttime, grpdocmessage) 
        else:
            grpdocmessage = ""
            apptcount = 0
            retval = False

    return dict(retval = retval, docmessage = grpdocmessage, docsmscount = apptcount)


def sendAptReminders(db,appPath):
    
    loccurrdate = common.getISTCurrentLocatTime()
    smsdate  = datetime.datetime.strptime(loccurrdate.strftime("%d") + "/" + loccurrdate.strftime("%m") + "/" + loccurrdate.strftime("%Y"), "%d/%m/%Y")
    smsdateUSFormat = loccurrdate.strftime("%Y") + "-" + loccurrdate.strftime("%m") + "-" + loccurrdate.strftime("%d")
    #logger.loggerpms2.info(smsdate + ": Enter sendAptReminders")
    
    
    ####select all provs from t_appt table of new appointments
    props = db(db.urlproperties.id>0).select()
    ccs = props[0].mailcc if(len(props)>0) else ""
    
    
    retval = False
    provsmscount = 0
    docs = None
    providerid = 0
    
    provs = db((db.vw_appointments.sendsms == False)  & (db.vw_appointments.sendrem == True)  \
               & ((db.vw_appointments.f_start_time).strftime("%Y-%m-%d") == smsdateUSFormat) \
               & (db.vw_appointments.is_active == True)).\
        select(db.vw_appointments.provider,db.vw_appointments.provname,db.vw_appointments.provcell, db.vw_appointments.provemail,distinct=True)
    
    for prov in provs:
        provsmscount = 0
        
        providerid = prov.provider
        provname = prov.provname
        provcell = common.modify_cell(prov.provcell)
        provemail = prov.provemail        

        provsms = "Dear $provider,\r\n Reminder for $count appointments for " + smsdate.strftime("%d/%m/%Y") + "\r\n " 
        provsms = provsms.replace('$provider',provname)
        
        
        docs = db((db.vw_appointments.sendsms == False)  & (db.vw_appointments.sendrem == True) & (db.vw_appointments.provider == prov.provider) \
                      & ((db.vw_appointments.f_start_time).strftime("%Y-%m-%d") == smsdateUSFormat) \
                      & (db.vw_appointments.is_active == True)).select(db.vw_appointments.doctor,distinct=True)   

        for doc in docs:
            docret = senddoctorremaptgroupsms(db,appPath, ccs,doc.doctor,smsdate,prov.provider)
            if(docret["retval"] == True):
                provsms = provsms + docret["docmessage"] + "\n\n"
                provsmscount = provsmscount+ int(docret["docsmscount"])
        
        provsms = provsms.replace('$count', str(provsmscount))
        retval = False
        
        if(prov.groupsms == True):
            retval = mail.sendSMS2Email(db, provcell, provsms) 
            appts = db((db.vw_appointments.sendsms == False)  & (db.vw_appointments.sendrem == True) & (db.vw_appointments.provider == providerid) \
                          & ((db.vw_appointments.f_start_time).strftime("%Y-%m-%d") == smsdateUSFormat) \
                          & (db.vw_appointments.is_active == True)).select(db.vw_appointments.doctor,distinct=True)         
            for appt in appts:
                db(db.t_appointment.id == appt.id).update(sendrem = False)        
                db.commit()
        
        if((provemail != "")&(prov.groupemail == True)):
            retval1 = mail.groupEmail(db, provemail, ccs, "Appointments:" + smsdate.strftime("%d/%m/%Y"), provsms) 
            
   
    
    return dict(smsok = retval, provsmscount = provsmscount, smsdate=smsdate)
    
    




#this function groups new appointments by provider and doctor
#and sends a single sms for this group of new appointments
#the sms are scanned and sent every hour. No smses are sent
#if no new appointments are created
def sendNewAptGrpSMS(db,appPath):
    
    
    
    loccurrdate = common.getISTCurrentLocatTime()
    smsdate  = datetime.datetime.strptime(loccurrdate.strftime("%d") + "/" + loccurrdate.strftime("%m") + "/" + loccurrdate.strftime("%Y"), "%d/%m/%Y")

    message = "Enter sendNewAptGrpSMS" + " " + (common.getISTFormatCurrentLocatTime()).strftime(datetimefmt)
    logger.loggerpms2.info(message)    
    
    
    
    
    
    #####select all provs from t_appt table of new appointments
    props = db(db.urlproperties.id>0).select()
    ccs = props[0].mailcc if(len(props)>0) else ""
    
    
    retval = False
    provsmscount = 0
    docs = None
    providerid = 0
    
    
    try:
        provs = db((db.vw_appointments.sendsms == True) & \
                   ((db.vw_appointments.is_active == True))).\
            select(db.vw_appointments.provider,db.vw_appointments.provname,db.vw_appointments.provcell, db.vw_appointments.provemail,\
                   db.vw_appointments.groupsms, db.vw_appointments.groupemail,distinct=True)
        #provs = db((db.vw_appointments.sendsms == True) & \
                   #((db.vw_appointments.is_active == True) | ((db.vw_appointments.is_active == False)&(db.vw_appointments.f_status == 'Cancelled')))).\
            #select(db.vw_appointments.provider,db.vw_appointments.provname,db.vw_appointments.provcell, db.vw_appointments.provemail,\
                   #db.vw_appointments.groupsms, db.vw_appointments.groupemail,distinct=True)
        
        for prov in provs:
            provsmscount = 0
            
            providerid = prov.provider
            provname = prov.provname
            provcell = common.modify_cell(prov.provcell)
            provemail = prov.provemail        
    
            provsms = "Dear $provider,\r\n There are $count of appointments\r\n" 
            provsms = provsms.replace('$provider',provname)
            
            docs = db((db.vw_appointments.sendsms == True) & (db.vw_appointments.provider == prov.provider) & (db.vw_appointments.is_active == True)).select(db.vw_appointments.doctor,\
                                                                                                                                                             distinct=True)
            for doc in docs:
            
                docret = senddoctornewaptgroupsms(db,appPath, ccs,doc.doctor,smsdate,prov.provider)
                if(docret["retval"] == True):
                    provsms = provsms + docret["docmessage"] + "\n\n"
                    provsmscount = provsmscount+ int(docret["docsmscount"])
            
            provsms = provsms.replace('$count', str(provsmscount))
            retval = False
            if((prov.groupsms == True) & (provsmscount > 0)):
                appts = db((db.vw_appointments.sendsms == True) & (db.vw_appointments.provider == providerid) & (db.vw_appointments.is_active == True)).select(db.vw_appointments.id,db.vw_appointments.sendsms)
                for appt in appts:
                    db(db.t_appointment.id == appt.id).update(sendsms = False)
                    db.commit()
    
                retval = mail.sendSMS2Email(db, provcell, provsms)
          
            if((provemail != "") & (prov.groupemail == True) & (provsmscount > 0)):
                logger.loggerpms2("sendNewAptGrpSMS:send group email")
                retval1 = mail.groupEmail(db, provemail, ccs, "Appointments:" + smsdate.strftime("%d/%m/%Y"), provsms) 
                
    except Exception as e:
        raise
        
    return dict(smsok = retval, provsmscount = provsmscount, smsdate=smsdate.strftime("%d/%m/%Y"))
  




#THis function is called fiveminutes past hour, 24x7 from a task that runs 24x7 in the background
#The group SMS will not be sent between 00:00:00 to 06:59:59  each day.
def sendGroupSMS(db,appPath):
    message = "Enter SendGroupSMS" + " " + (common.getISTFormatCurrentLocatTime()).strftime(datetimefmt)
    logger.loggerpms2.info(message)    
    
    
    try:
        loccurrdate = common.getISTCurrentLocatTime()
        
        
        currdate  = datetime.datetime.strptime(loccurrdate.strftime("%d") + "/" + loccurrdate.strftime("%m") + "/" + loccurrdate.strftime("%Y") + \
                                               " " + loccurrdate.strftime("%H") + ":" + loccurrdate.strftime("%M") + ":" + loccurrdate.strftime("%S"), "%d/%m/%Y %H:%M:%S")
        
        zerohour  = datetime.datetime.strptime(currdate.strftime("%d/%m/%Y") + " 00:00:00", "%d/%m/%Y %H:%M:%S")
        sevenhour = datetime.datetime.strptime(currdate.strftime("%d/%m/%Y") + " 06:59:59", "%d/%m/%Y %H:%M:%S")
        
    
       
        retval = None
        if( not ((currdate >= zerohour) & (currdate <= sevenhour))):
            retval = sendNewAptGrpSMS(db,appPath)
        else:
            retval = dict(smsok = None, provsmscount = 0, smsdate=currdate.strftime("%d/%m/%Y"))            
    except Exception as e:
        logger.loggerpms2.info('sendGroupSMS:Exception ' + str(e))
        raise
    
    return retval