# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']

#from gluon.tools import Crud
#crud = Crud(db)

#crud.settings.formstyle='table3cols'
#

import datetime
import time
import calendar
from datetime import timedelta

from decimal import Decimal
from string import Template
import os;



#import sys
#sys.path.append('/my_pms2/modules')
from applications.my_pms2.modules import common
from applications.my_pms2.modules import mail
from applications.my_pms2.modules import cycle
from applications.my_pms2.modules import logger

#from gluon.contrib import common
#from gluon.contrib import mail





#### required - do no delete
#def xuser(): return dict(form=auth())
#def xdownload(): return response.download(request,db)
#def xcall():
    #session.forget()
    #return service()
#### end requires
#def xindex():
    #return dict()

#def xerror():
    #return dict()

#@auth.requires_login()
#def xmymap():
    #rows=db(db.t_appointment.created_by==auth.user.id)(db.t_appointment.f_start_time>=request.now).select()
    #return dict(rows=rows)


def saveNewAppt(userid,form2,providerid):
        
        # find out appointment start and end datetime
        provdict = common.getprovider(auth,db)
        duration = int(common.getid(form2.vars.duration))
        apptdt = common.getnulldt(form2.vars.start_date)
        endapptdt = apptdt + timedelta(minutes=duration)
        
        memberid = 0
        patientid = 0
        appt  = 0
        planid = 0
        treatmentid = 0
        clinicid = session.clinicid
        clinicname = session.clinicname
        
        doctorid = int(common.getid(form2.vars.doctor))
        
        #patient = <fname lanme>:<memberid>
        #xpatientmember = <fname lanme>:<memberid>
        rows = db(db.vw_memberpatientlist.patient == form2.vars.xpatientmember).select(db.vw_memberpatientlist.primarypatientid, 
                                                                                       db.vw_memberpatientlist.patientid,
                                                                                       db.vw_memberpatientlist.patientmember
                                                                                       )
        
        if(len(rows) > 0):
                memberid = int(common.getid(rows[0].primarypatientid))
                patientid = int(common.getid(rows[0].patientid))
                patientmember = common.getstring(rows[0].patientmember) #patientmember/member ID
        else:
                r = db((db.hmoplan.hmoplancode == 'PREMWALKIN') & (db.hmoplan.is_active == True)).select(db.hmoplan.id)
                hmoplanid = int(common.getid(r[0].id)) if(len(r) == 1) else 1
        
                #default to MyDP
                r = db((db.company.company == ' ') & (db.company.is_active == False)).select(db.company.id)
                companyid = int(common.getid(r[0].id)) if(len(r) == 1) else 4
                  
                
                fname = ""
                lname = ""
                strarr = form2.vars.xpatientmember.split()
                if(len(strarr) >0):
                        fname = strarr[0].strip()
                for i in xrange(1,len(strarr)):
                        lname = lname + " " + strarr[i].strip()
                        
                provcount = db(db.patientmember.provider == providerid).count()
                patientmember = provdict["provider"] + str(provcount).zfill(4) 
         
        apptid = 0
        retval = False
        if((isBlocked(apptdt,endapptdt,doctorid)==False)):
                
                if(memberid == 0):
                        # create a new patient with assumption the name is entered as [<title>] [<fname>] [<lname>]
                        db.patientmember.dob.requires = ""
                        db.patientmember.address1.requires = ""
                        db.patientmember.city.requires = ""
                        db.patientmember.st.requires = ""
                        db.patientmember.pin.requires = ""
                        db.patientmember.cell.requires = ""
                        db.patientmember.status.requires = ""
                       
                       
                        patientid = db.patientmember.insert(
                           patientmember = patientmember,
                           title = " ",
                           fname = fname,
                           lname = lname,
                           cell = form2.vars.cell,
                           company = companyid,
                           hmoplan = hmoplanid,
                           groupregion = 1,
                           provider  = providerid,
                           clinicid = session.clinicid,
                           hmopatientmember = False,
                           
                           newmember = True,
                           freetreatment = True,
                           is_active = True,
                           created_on = common.getISTFormatCurrentLocatTime(),
                           created_by = userid,
                           modified_on =common.getISTFormatCurrentLocatTime(),
                           modified_by = userid
                       
                        )
                                
                       
                        #22/07/22 : As per new appointment confirmation process, the original status is Open instead o Confirmed
                        apptid  = db.t_appointment.insert(f_start_time=apptdt, f_end_time = endapptdt, f_duration= duration, cell = common.getstring(form2.vars.cell),
                                                        f_title = common.getstring(form2.vars.title),f_status='Open',
                                                        f_patientname = common.getstring(form2.vars.patientmember),
                                                        f_location = form2.vars.location,
                                                        f_treatmentid = treatmentid,
                                                        description = form2.vars.description,
                                                        doctor = doctorid,
                                                        patient=patientid,
                                                        patientmember=patientid,
                                                        clinicid = clinicid,
                                                        sendsms = True,
                                                        sendrem = True,
                                                        smsaction = "create",
                                                      provider=providerid,  is_active=True,
                                                      created_on=common.getISTFormatCurrentLocatTime(),modified_on=common.getISTFormatCurrentLocatTime(),
                                              created_by = userid, modified_by=userid)
                else:
                       
                        apptid  = db.t_appointment.insert(f_start_time=apptdt, f_end_time = endapptdt, f_duration = duration, cell = common.getstring(form2.vars.cell),
                                                        f_title = common.getstring(form2.vars.title),f_status='Open',
                                                        f_treatmentid = treatmentid,
                                                        f_patientname = common.getstring(form2.vars.patientmember),
                                                        clinicid = clinicid,
                                                        description = form2.vars.description,f_location = form2.vars.location, sendsms = True, sendrem=True,smsaction="create",
                                                        doctor = doctorid, provider=providerid, patient=patientid,patientmember=memberid, is_active=True,
                                                        created_on=common.getISTFormatCurrentLocatTime(),modified_on=common.getISTFormatCurrentLocatTime(),
                                                        created_by = userid, modified_by=userid)  
                        
                db(db.t_appointment.id == apptid).update(f_uniqueid = apptid)

                # Send Confirmation SMS  - these will be sent via Tasks-Group Messages module from superadmin activity tracker
                retval = True

                #save in case report
                common.logapptnotes(db,common.getstring(form2.vars.title),common.getstring(form2.vars.description),apptid)
        
            
        return retval
        



def prevnextappt():
    provdict = common.getprovider(auth,db)
    providerid = int(provdict["providerid"])
    if(providerid  < 0):
        raise HTTP(400,"PMS-Error: There is no valid logged-in Provider: providerhome()")    
   
    prov = db(db.provider.id == providerid).select(db.provider.pa_practicename,db.provider.pa_practiceaddress)

    clinicid = session.clinicid
    
    x = (datetime.datetime.today()).strftime("%d/%m/%Y %H:%M")
    xdt = datetime.datetime.strptime(x, "%d/%m/%Y %H:%M")
    
    if(request.vars.moment != None):
        y = (request.vars.moment).split("T")
        if(y[1] == "00:00:00 00:00"):
            currdate = datetime.datetime.strptime(request.vars.moment, "%Y-%m-%dT%H:%M:%S 00:00")            
        else:
            currdate = datetime.datetime.strptime(request.vars.moment, "%Y-%m-%dT%H:%M:%S")            
    else:
        currdate = xdt

    if(request.vars.defdate == None):
            defdate = (currdate).strftime('%Y-%m-%d %H:%M')
    else:
            if(secondsFormat(request.vars.defdate)):
                currdate = datetime.datetime.strptime(request.vars.defdate, "%Y-%m-%d %H:%M:%S")        
            else:
                currdate = datetime.datetime.strptime(request.vars.defdate, "%Y-%m-%d %H:%M")
                
            defdate = (currdate).strftime('%Y-%m-%d %H:%M')    
            
    defyear =(currdate).strftime('%Y')  #YYYY
    defmonth = (currdate).strftime('%m')  #mm
    
    defstart = datetime.datetime.strptime("01/" + str(defmonth)+"/"+str(defyear) + " 00:00:00", '%d/%m/%Y %H:%M:%S')   #start of def month
    defend   = datetime.date(defstart.year, defstart.month, calendar.monthrange(defstart.year, defstart.month)[-1])
    defend   = datetime.datetime.strptime( defend.strftime("%d") + "/" + str(defmonth)+"/"+str(defyear) + " 23:59:59", '%d/%m/%Y %H:%M:%S')   #end of def month (assuming 31 for all months)    
 
   
    start = "2100-01-01 00:00"
    end   = "2100-01-01 00:00"  
 
    #get all appointments for this provider & Clinicid and default month
    rows=db((db.t_appointment.provider==providerid) & (db.t_appointment.clinicid==clinicid) & (db.t_appointment.f_start_time>=defstart) &(db.t_appointment.f_start_time<=defend) &(db.t_appointment.is_active==True) ).\
            select(db.t_appointment.id,db.t_appointment.f_title,db.t_appointment.f_start_time,db.t_appointment.f_end_time,db.t_appointment.f_patientname,db.t_appointment.is_active, \
                   db.doctor.color, left=db.doctor.on(db.doctor.id == db.t_appointment.doctor))  
    
    dailyappts  = db((db.vw_appointment_today.providerid == providerid) & (db.vw_appointment_today.clinicid==clinicid) & (db.vw_appointment_today.is_active == True)).select(orderby=db.vw_appointment_today.f_start_time)
    weeklyappts = db((db.vw_appointment_weekly.providerid == providerid) & (db.vw_appointment_weekly.clinicid==clinicid) & (db.vw_appointment_weekly.is_active == True)).select(orderby=db.vw_appointment_weekly.f_start_time)
    monthlyappts = db((db.vw_appointment_monthly.providerid == providerid) & (db.vw_appointment_monthly.clinicid==clinicid) & (db.vw_appointment_monthly.is_active == True)).select(orderby=db.vw_appointment_monthly.f_start_time)
    
   
    
    common.dashboard(db,session,providerid)
    memberid = 0
    patientid = 0   
    
    
    
    sqlquery = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True))
    
    form = SQLFORM.factory(
           Field('patientmember1', 'string',    label='Patient ID',requires=IS_NOT_EMPTY()),
           Field('xpatientmember1', 'string',   label='Member ID', default = ""),
           Field('xaction','string', label='', default='X')
                       
    )
       
    xpatientmember = form.element('#no_table_patientmember1')
    #xpatientmember['_class'] = 'w3-input w3-border'
    xpatientmember['_class'] = 'form-control'
    xpatientmember['_placeholder'] = 'Enter Patient Information (first, Last, Cell, Email)' 
    xpatientmember['_autocomplete'] = 'off' 
    
    xpatientmember1 = form.element('#no_table_xpatientmember1')
    #xpatientmember['_class'] = 'w3-input w3-border'
    xpatientmember1['_class'] = 'form-control'
   
    xpatientmember1['_autocomplete'] = 'off' 
    
    
    doctorid = int(common.getdefaultdoctor(db, providerid))
    returnurl = URL('admin', 'providerhome')
    r = db(db.urlproperties.id >0).select()
    exturl = None
    if(len(r)>0):
        exturl = common.getstring(r[0].externalurl)
      
       
                
   
       
    if form.process().accepted:  
        xaction = form.vars.xaction
        xphrase1 = form.vars.xpatientmember1.strip()
            
        if(xaction == "searchPatient"):
            processPatientLookup(providerid, xphrase1)
        elif(xaction == "newPatient"):
            redirect(URL('member','new_nonmember',vars=dict(page=0,providerid=providerid,returnurl=URL('admin','providerhome'))))
        elif(xaction == "newTreatment"):
            processNewTreatment(providerid, xphrase1)
        elif(xaction == "newPayment"):
            processNewPayment(providerid, xphrase1)
        elif(xaction == "newImage"):
            processNewImage(providerid,xphrase1)
        elif(xaction == "newReport"):
            processNewReport(providerid, xphrase1)
            
    elif form.errors:
        #xpatientmember1 is empty
        xaction = form.vars.xaction
        if(xaction == "newPatient"):
            redirect(URL('member','new_nonmember',vars=dict(page=0,providerid=providerid,returnurl=URL('admin','providerhome'))))        
       
       

    
    sql = "select doctor.name, doctor.color, IFNULL(appts.appointments,0) AS appointments,doctor.providerid,doctor.id as docid  from doctor left join "
    sql = sql + "(select vw_appointment_count.doctorid, vw_appointment_count.name, color, sum(appointments) as appointments, starttime from " 
    sql = sql + "vw_appointment_count where is_active = 'T' and providerid =" +  str(providerid)  + " and starttime >= '" + defstart.strftime('%Y-%m-%d') + "'  and starttime <= '" + defend.strftime('%Y-%m-%d') + "' group by name ) appts "
    sql = sql + " on doctor.id = appts.doctorid where doctor.stafftype <> 'Staff' and doctor.is_active = 'T' and doctor.providerid = " + str(providerid) + " ORDER BY appointments DESC" 
    
    docs = db.executesql(sql)   
   
   
    return dict(form=form,docs=docs,defdate=defdate,start=start,end=end,rows=rows,memberpage=1,page=1,\
                dailyappts=dailyappts,monthlyappts=monthlyappts,weeklyappts=weeklyappts,providerid=providerid, providername= provdict["providername"] + " " + provdict["provider"],returnurl=returnurl,source='home',externalurl=exturl)



def xisBlocked(apptid):
        retval = True
        appt = db(db.t_appointment.id == apptid).select(db.t_appointment.f_start_time, db.t_appointment.f_end_time)
        str1 = datetime.datetime.strftime(appt[0].f_start_time, "%d/%m/%Y %H:%M")
        str2 = datetime.datetime.strftime(appt[0].f_end_time, "%d/%m/%Y %H:%M")
        
        blockappts = db(( str1 >= db.t_appointment.f_start_time)& (str1 <= db.t_appointment.f_end_time) & (db.t_appointment.blockappt == True) & (db.t_appointment.is_active == True)).\
                select(db.t_appointment.blockappt)   
        
        if(len(blockappts)>0):
                return True
        
        blockappts = db(( str1 >= db.t_appointment.f_end_time)&(db.t_appointment.blockappt == True)&(db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
        
        if(len(blockappts)>0):
                return False
        
        blockappts = db(( str1 <= db.t_appointment.f_start_time)&(str2 <= db.t_appointment.f_start_time)&(db.t_appointment.blockappt == True)&(db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
        if(len(blockappts)>0):
                return False
        
        
        return retval

def isBlocked(startdt, enddt,doctorid):
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
    
    
def smsmessage():
    
  
       
    smstemplate = None
    if(request.vars.smstemplate == None):
        smstemplate = "SMS_Empty.txt"
    else:
        smstemplate = request.vars.smstemplate     
        
    appPath = request.folder
    smsfile = os.path.join(appPath,'templates/appointments/sms',smstemplate)
    f = open(smsfile,'rb')
    message = Template(f.read())
    f.close()    
    
    return dict(message=message.template)

def emailmessage():
    

    emailtemplate = None
    if(request.vars.emailtemplate == None):
        emailtemplate = "Email_Empty.txt"
    else:
        emailtemplate = request.vars.emailtemplate    
    appPath = request.folder
    emailfile = os.path.join(appPath,'templates/appointments/email',emailtemplate)
    f = open(emailfile,'rb')
    message = Template(f.read())
    f.close()    
    
    return dict(message=message.template)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def sms_reminders():
    ids = request.vars.ids
    page = common.getgridpage(request.vars)
    providerid = int(common.getid(request.vars.providerid))
    start = request.vars.start
    end=request.vars.end
    notification = request.vars.notification
    
    redirect(URL('appointment', 'sms_reminder', vars=dict(page=page, providerid=providerid, mode='multiple',ids=ids,start=start,end=end,notification=notification)))
    return dict()

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def email_reminders():
    ids = request.vars.ids
    page = common.getgridpage(request.vars)
    providerid = int(common.getid(request.vars.providerid))
    start = request.vars.start
    end=request.vars.end
    notification = request.vars.notification
    
    redirect(URL('appointment', 'email_reminder', vars=dict(page=page, providerid=providerid, mode='multiple',ids=ids,start=start,end=end,notification=notification)))
    return dict()



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def sms_reminder():

    username   = auth.user.first_name + ' ' + auth.user.last_name
    
    
    providerid = request.vars.providerid
    provdict = common.getproviderfromid(db, request.vars.providerid)
    start = request.vars.start
    end=request.vars.end    
    notification = request.vars.notification
    page=common.getgridpage(request.vars)
    ids = common.getstring(request.vars.ids)
    if(ids == 'None'):
        ids = None
        
    cellnos = ""
    formheader = "Appointment Reminder SMS Text - From:" + start + " To:" + end
    appts = ''
    locs = ""
    docs = ""
    mode = common.getstring(request.vars.mode)
    
    if((ids != None) & (ids != "")):
        if(mode == 'single'):
            uid = int(common.getid(request.vars.ids))
            pat = db((db.t_appointment.id == uid) & (db.t_appointment.is_active == True)).select(db.patientmember.cell, db.doctor.id, db.t_appointment.f_start_time,db.t_appointment.f_location,\
                                                                                                 left=[db.patientmember.on(db.patientmember.id==db.t_appointment.patient), \
                                                                                                       db.doctor.on(db.doctor.id == db.t_appointment.doctor)])
        
            if(len(pat)>0):
                appt = (pat[0].t_appointment.f_start_time).strftime('%d/%m/%Y %H:%M')
                cellno = common.getstring(pat[0].patientmember.cell)
                loc = common.getstring(pat[0].t_appointment.f_location)
                doc = str(pat[0].doctor.id)
            else:
                appt = ""
                cellno = ""
                loc = ""
                doc  = ""
                
            
            if(cellno != ""):
                if(cellno.startswith("91") == True):
                    cellnos = cellnos + cellno
                else:
                    cellnos = cellnos + "91" + cellno
            if(appt != ""):
                appts = appts + appt
            else:
                appts = appts + " " 
            if(loc != ""):
                locs = locs + loc
            else:
                locs = locs + " " 
            if(docs != ""):
                docs = docs + doc
            else:
                docs = doc + " " 
                    
                
        else:
            for uid in ids:
                pat = db((db.t_appointment.id == uid) & (db.t_appointment.is_active == True)).\
                    select(db.patientmember.cell, db.doctor.id, db.t_appointment.f_start_time,db.t_appointment.f_location,\
                           left=[db.patientmember.on(db.patientmember.id==db.t_appointment.patient), db.doctor.on(db.doctor.id == db.t_appointment.doctor)])
                
                if(len(pat)>0):
                    appt = (pat[0].t_appointment.f_start_time).strftime('%d/%m/%Y %H:%M')
                    cellno = common.getstring(pat[0].patientmember.cell)
                    loc = common.getstring(pat[0].t_appointment.f_location)
                    doc = str(pat[0].doctor.id)
                else:
                    appt = ""
                    cellno = ""
                    loc = ""
                    doc  = ""
                    
                
                if(cellno != ""):
                    if(cellno.startswith("91") == True):
                        cellnos = cellnos + cellno + ","
                    else:
                        cellnos = cellnos + "91" + cellno + ","            
                if(appt != ""):
                    appts = appts + appt + ","
                else:
                    appts = appts + " " +","
                if(loc != ""):
                    locs = locs + loc +","
                else:
                    locs = locs + " " +","
                if(docs != ""):
                    docs = docs + doc + ","
                else:
                    docs = doc + " "  + ","
    
    if(cellnos != None)&(cellnos != ""):
        cellnos = cellnos.rstrip(',')
        
    appts = appts.rstrip(',')
    locs = locs.rstrip(',')   
    docs = docs.rstrip(',')   
    
    files = os.listdir(os.path.join(request.folder, 'templates/appointments/sms'))
    options=[smsfile for smsfile in files] 
    
    formA = SQLFORM.factory(Field('smstemplate','list:string',label='SMS Template',requires=IS_IN_SET(options)),
                            Field('to','string',label='To:',default=cellnos),
                            Field('appton', 'string', label='Appts. On:', default=appts),
                            Field('loc', 'string', label='Location:', default=locs),
                            Field('doc', 'string', default=docs)
                            )
    
    
    xsmstemplate = formA.element('#no_table_smstemplate')
    xsmstemplate['_class'] = 'form-control'
    xto = formA.element('#no_table_to')
    xto['_class'] = 'form-control'    
  
    retVal = None
    if formA.accepts(request,session,keepvalues=True):
        #ids = request.vars.ids
        page = common.getgridpage(request.vars)
        providerid = int(common.getid(request.vars.providerid))        
        provdict = common.getproviderfromid(db, request.vars.providerid)
        start = request.vars.start
        end=request.vars.end        
        notification = request.vars.notification
        cellarr = (request.vars.to).split(",")
        apptarr = (request.vars.appton).split(",")
        locarr = (request.vars.loc).split(",")
        docarr = (request.vars.doc).split(",")
        messsage = request.vars.message
       
        for i in xrange(len(cellarr)):
            
            cellstr = ""
            if len(cellarr[i])>2 :
                cellstr = cellarr[i].replace("91","",1)
            
            pat = db(db.patientmember.cell == cellstr).select(\
                db.patientmember.fname, db.patientmember.lname, db.provider.providername, db.provider.cell, db.provider.email,\
                left=db.provider.on(db.provider.id==db.patientmember.provider))
            
            doc = db(db.doctor.id == common.getid(docarr[i])).select()
            
            if(len(pat) >= 1):
                message = request.vars.message
                message = message.replace("$fname", pat[0]["patientmember.fname"])
                message = message.replace("$lname", pat[0]["patientmember.lname"])
                message = message.replace("$providername", doc[0].name)
                message = message.replace("$cell", doc[0].cell)
                message = message.replace("$email", "")
                message = message.replace("$appointmentdate", apptarr[i] )
                message = message.replace("$place","" )
                retVal = mail.sendSMS2Email(db,cellarr[i],message)
     


    returnurl = URL('utility','list_appointment_reminders',vars=dict(providerid=providerid, providername=provdict["providername"],\
                                                                             page=page,start=start,end=end,\
                                                                             notification=request.vars.notification))
    
    message = ""
    
    return dict(username=username, returnurl=returnurl, formA=formA,formheader=formheader,page=page, retVal = retVal,providername = provdict["providername"], providerid=provdict["providerid"],smsfiles=files,message=message)
        




def sms_confirmation(appointmentid,action="create"):
        
        fname = ""

        retVal1 = False
        retVal2 = False
        retVal3 = False
        
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
        
        appPath = request.folder
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
        
    
@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def email_reminder():

    username   = auth.user.first_name + ' ' + auth.user.last_name
    
    
    providerid = request.vars.providerid
    provdict = common.getproviderfromid(db, request.vars.providerid)
    start = request.vars.start
    end=request.vars.end    
    notification = request.vars.notification
    page=common.getgridpage(request.vars)
    ids = common.getstring(request.vars.ids)
    if(ids == 'None'):
        ids = None
    
    emails = ""
    locs = ""
    appts = ""
    docs = ""
    email = ""
    formheader = "Appointment Reminder Email - From:" + start + " To:" + end
    mode = common.getstring(request.vars.mode)
    
    if((ids != None) & (ids != "")):
        if(mode == 'single'):
            uid = int(common.getid(request.vars.ids))
            pat = db((db.t_appointment.id == uid) & (db.t_appointment.is_active == True)).select(db.patientmember.email, db.doctor.id,db.t_appointment.f_start_time,db.t_appointment.f_location,\
                                                                                                 left=[db.patientmember.on(db.patientmember.id==db.t_appointment.patient), \
                                                                                                       db.doctor.on(db.doctor.id == db.t_appointment.doctor)])
            if(len(pat)>0):
                appt = (pat[0].t_appointment.f_start_time).strftime('%d/%m/%Y %H:%M')
                email = common.getstring(pat[0].patientmember.email)
                loc = common.getstring(pat[0].t_appointment.f_location)
                doc = str(pat[0].doctor.id)
            else:
                appt = ""
                email = ""
                loc = ""
                doc  = ""
                
            
            if(email != ""):
                emails = emails + email
            else:
                emails = emails + " "
                    
            if(appt != ""):
                appts = appts + appt
            else:
                appts = appts + " " 
            if(loc != ""):
                locs = locs + loc
            else:
                locs = locs + " " 
            if(docs != ""):
                docs = docs + doc
            else:
                docs = doc + " " 
        else:
            for uid in ids:
                pat = db((db.t_appointment.id == uid) & (db.t_appointment.is_active == True)).select(db.patientmember.email, db.doctor.id,db.t_appointment.f_start_time,db.t_appointment.f_location,\
                                                                                                     left=[db.patientmember.on(db.patientmember.id==db.t_appointment.patient), \
                                                                                                           db.doctor.on(db.doctor.id == db.t_appointment.doctor)])
                
                
                if(len(pat)>0):
                    appt = (pat[0].t_appointment.f_start_time).strftime('%d/%m/%Y %H:%M')
                    email = common.getstring(pat[0].patientmember.email)
                    loc = common.getstring(pat[0].t_appointment.f_location)
                    doc = str(pat[0].doctor.id)
                else:
                    appt = ""
                    email = ""
                    loc = ""
                    doc  = ""
                    
                
                if(email != ""):
                    emails = emails + email + ";"
                else:
                    emails = emails + " " + ";"            
                        
                if(appt != ""):
                    appts = appts + appt + ";"
                else:
                    appts = appts + " " +";"
                if(loc != ""):
                    locs = locs + loc +";"
                else:
                    locs = locs + " " +";"
                if(docs != ""):
                    docs = docs + doc + ";"
                else:
                    docs = doc + " "  + ";"
   
   
   
    if((emails != None) & (emails != "")):
        emails = emails.rstrip(';')
        
    if((docs != None) & (docs != "")):
        docs = docs.rstrip(';')
    
    if((locs != None) & (locs != "")):
        locs = locs.rstrip(';')

    if((appts != None) & (appts != "")):
        appts = appts.rstrip(';')

    files = os.listdir(os.path.join(request.folder, 'templates/appointments/email'))
    options=[emailfile for emailfile in files] 
    
    formA = SQLFORM.factory(Field('emailtemplate','list:string',label='Email Template',requires=IS_IN_SET(options)),
                            Field('to','string',label='To:',default=emails),
                            Field('doc', 'string', default=docs),
                            Field('loc', 'string', default=locs),
                            Field('appt', 'string', default=appts),
                            )
           
    
    xemailtemplate = formA.element('#no_table_emailtemplate')
    xemailtemplate['_class'] = 'form-control'
    xto = formA.element('#no_table_to')
    xto['_class'] = 'form-control'    
     
  
    retVal = None
    if formA.accepts(request,session,keepvalues=True):
        #ids = request.vars.ids
        page = common.getgridpage(request.vars)
        providerid = int(common.getid(request.vars.providerid))        
        provdict = common.getproviderfromid(db, request.vars.providerid)
        start = request.vars.start
        end=request.vars.end        
        notification = request.vars.notification
        emailarr = (request.vars.to).split(";")
        docarr = (request.vars.doc).split(";")
        locarr = (request.vars.loc).split(";")
        apptarr = (request.vars.appt).split(";")
        
        messsage = request.vars.message
        for i in xrange(len(emailarr)):
            
            emailstr = emailarr[i]
            
            pat = db(db.patientmember.email == emailstr).select(\
                db.patientmember.fname, db.patientmember.lname, db.provider.providername, db.provider.cell, db.provider.email,\
                db.provider.address1, db.provider.address2, db.provider.address3, db.provider.city, db.provider.st, db.provider.pin, \
                left=db.provider.on(db.provider.id==db.patientmember.provider))
                
            doc = db(db.doctor.id == common.getid(docarr[i])).select()
            loc = locarr[i]
            appt = apptarr[i]
            
            if(len(pat) >= 1):
                message = request.vars.message
                message = message.replace("$fname", pat[0]["patientmember.fname"])
                message = message.replace("$lname", pat[0]["patientmember.lname"])
                message = message.replace("$appointmentdate", appt)
                message = message.replace("$place", loc)
                message = message.replace("$providername", doc[0].name)
                message = message.replace("$cell", doc[0].cell)
                message = message.replace("$email", doc[0].email)
                
                retVal = mail.groupEmail(db,emailstr,doc[0].email, "Appointment Reminder",message)


    returnurl = URL('utility','list_appointment_reminders',vars=dict(providerid=providerid, providername=provdict["providername"],\
                                                                             page=page,start=start,end=end,\
                                                                             notification=request.vars.notification))
    
    message = ""
    
    return dict(username=username, returnurl=returnurl, formA=formA,formheader=formheader,page=page, retVal = retVal,providername = provdict["providername"], providerid=provdict["providerid"],emailfiles=files,message=message)


#@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
#@auth.requires_login()
#def xappointments():
    #page = 0
    #providerid = int(common.getnegid(request.vars.providerid))
    #providerdict = common.getproviderfromid(db,providerid)
    #returnurl = URL('admin','providerhome')    
    #return dict(page=page,providerid=providerid,providername=providerdict["providername"],returnurl=returnurl)

#@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
#@auth.requires_login()
#def xcalendar():
    #defdate = (datetime.date.today()).strftime('%Y-%m-%d')
    
    #page = 0
    #memberpage = 0
    #membername = ""
    #patientname = ""
    
    #providerid = int(common.getnegid(request.vars.providerid))
    #memberid   = int(common.getid(request.vars.memberid))
    #patientid  = int(common.getid(request.vars.patientid))
    #memberpage = int(common.getpage(request.vars.memberpage))
    #providerdict = common.getproviderfromid(db,providerid)
    
    
    #pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid) &  (db.vw_memberpatientlist.providerid == providerid) &  (db.vw_memberpatientlist.is_active == True)).select()
    #if(len(pats)>0):
        #patientname = pats[0].fullname
        #membername  = pats[0].patient

    #if(patientid > 0):
        #rows=db((db.t_appointment.provider==providerid) & (db.t_appointment.patient==patientid) & (db.t_appointment.is_active==True)).select()
    #else:
        #rows=db((db.t_appointment.provider==providerid)& (db.t_appointment.is_active==True) ).select()
    
    
    #start = "2100-01-01 00:00:00"
    #end = "2100-01-01 00:00:00"
    


    #form = SQLFORM.factory(Field('start','datetime',requires=IS_EMPTY_OR(IS_DATETIME(format=T('%d/%m/%Y %H:%M:%S')))),
                           #Field('end','datetime', requires=IS_EMPTY_OR(IS_DATETIME(format=T('%d/%m/%Y %H:%M:%S'))))
                           #)
    
    
    
    

    #xstart = form.element('input',_id='no_table_start')
    #xstart['_class'] =  'input-group form-control form-control-inline date-picker'
    
    #xend = form.element('input',_id='no_table_end')
    #xend['_class'] =  'input-group form-control form-control-inline date-picker'
    
    #if form.accepts(request,session,keepvalues=True):
        #if((form.vars.start != None) & (form.vars.start != "")):
            #start = (form.vars.start).strftime('%Y-%m-%d %H:%M:%S')
        
        #if((form.vars.end != None) & (form.vars.end != None)):
            #end = (form.vars.end).strftime('%Y-%m-%d %H:%M:%S')
        
   

    #returnurl = URL('admin','providerhome')
    #return dict(form=form, rows=rows,providerid=providerid, memberid=memberid, patientid=patientid, providername=providerdict["providername"],\
                #returnurl=returnurl,page=page,memberpage=memberpage,start=start,end=end,defdate=defdate,membername=membername)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def appointment():
    defdate = (datetime.date.today()).strftime('%Y-%m-%d %H:%M:%S')
    
    source = common.getstring(request.vars.source)
    page = 0
    memberpage = 0
    membername = ""
    patientname = ""
    memberid = 0
    patientid = 0
    provloc = ""
    provcode = ""
    clinicid = session.clinicid
    
    page       = common.getgridpage(request.vars)
    memberpage = int(common.getpage(request.vars.memberpage))
    providerid = int(common.getnegid(request.vars.providerid))
    providerdict = common.getproviderfromid(db,providerid)
    providername = providerdict['providername']
    prov = db(db.provider.id == providerid).select()
    if(len(prov)>0):
        provloc = provloc + prov[0].address1 + ", " + prov[0].address2 + ", " + prov[0].address3 + ", " + prov[0].city + ", " + prov[0].st + " - " + prov[0].pin
        provcode = prov[0].provider
    
    pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid) &  (db.vw_memberpatientlist.providerid == providerid) &  (db.vw_memberpatientlist.is_active == True)).select()
    if(len(pats)>0):
        patientname = pats[0].fullname   # fname Lname (Neeta Hebbar)
        membername  = pats[0].patient    # fname, lname, memberid (Neeta Hebbad : BLR100823)
        
        

    if(patientid > 0):
        if(clinicid == 0):
                rows=db((db.t_appointment.provider==providerid) & (db.t_appointment.patientmember == memberid) & (db.t_appointment.patient==patientid) & (db.t_appointment.is_active==True)).\
                    select(db.t_appointment.ALL, db.doctor.ALL, left=db.doctor.on(db.doctor.id == db.t_appointment.doctor))
        else:
                rows=db((db.t_appointment.provider==providerid) & (db.t_appointment.clinicid==clinicid) & (db.t_appointment.patientmember == memberid) & (db.t_appointment.patient==patientid) & (db.t_appointment.is_active==True)).\
                        select(db.t_appointment.ALL, db.doctor.ALL, left=db.doctor.on(db.doctor.id == db.t_appointment.doctor))
                
    else:
        if(clinicid == 0):
                rows=db((db.t_appointment.provider==providerid)& (db.t_appointment.is_active==True) ).\
                    select(db.t_appointment.ALL, db.doctor.ALL, left=db.doctor.on(db.doctor.id == db.t_appointment.doctor))
        else:
                rows=db((db.t_appointment.provider==providerid)& (db.t_appointment.clinicid==clinicid)& (db.t_appointment.is_active==True) ).\
                        select(db.t_appointment.ALL, db.doctor.ALL, left=db.doctor.on(db.doctor.id == db.t_appointment.doctor))
        
    
    start = "2100-01-01 00:00:00"
    end   = "2100-01-01 00:00:00"
    
    lowerlimit = (datetime.date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    sql = "select doctor.name, doctor.color, IFNULL(appts.appointments,0) AS appointments,doctor.providerid  from doctor left join "
    sql = sql + "(select vw_appointment_count.doctorid, vw_appointment_count.name, color, count(appointments) as appointments, starttime from " 
    sql = sql + "vw_appointment_count where is_active = 'T' and providerid =" +  str(providerid)  + " and starttime >= '" + lowerlimit + "' group by name ) appts "
    sql = sql + " on doctor.id = appts.doctorid where doctor.stafftype <> 'Staff' and doctor.is_active = 'T' and doctor.providerid = " + str(providerid) + " ORDER BY appointments DESC" 
    
    docs = db.executesql(sql)
    
    
 
    form = SQLFORM.factory(Field('start','datetime', requires=IS_EMPTY_OR(IS_DATETIME(format=T('%d %B %Y - %H:%M')))),
                           Field('end','datetime',  requires=IS_EMPTY_OR(IS_DATETIME(format=T('%d %B %Y - %H:%M'))))
                           )
        

        
        
    xstart = form.element('input',_id='no_table_start')
    xstart['_class'] =  'form-control'
   
    xend = form.element('input',_id='no_table_end')
    xend['_class'] =  'form-control'
    
    
    #default attending doctor to owner doctor
    #r = db((db.doctor.providerid == providerid) & (db.doctor.practice_owner == True)).select()
    #doctorid = 0
    #if(len(r) > 0):
        #doctorid = common.getid(r[0].id)    
        
    doctorid = int(common.getdefaultdoctor(db, providerid))
    
    form2 = SQLFORM.factory(
              Field('patientmember', 'string',  label='Patient',default=patientname,requires=[IS_NOT_EMPTY()]),
              Field('cell', 'string',  label='Cell',default=""),
              Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
              Field('title', 'string',  label='Patient',default=""),
              Field('location', 'string',  label='Clinic Location',default=provloc),
              Field('xpatientmember', 'string',  label='Patient',default=membername),
              Field('xfullname', 'string',  label='Patient', default=patientname),
              Field('xmemberid', 'string',  label='Patient',default=memberid),
              Field('start_date', 'datetime',label='Start Date & Time',requires=[IS_NOT_EMPTY(), IS_DATETIME(format=T('%d %B %Y - %H:%M'))]),
              Field('duration', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default='15', label='Doctor',requires=IS_IN_SET(['15','30','45','60'])),
              Field('end_date', 'datetime',label='End Date & Time',default=request.now,requires=[IS_NOT_EMPTY(), IS_DATETIME(format=T('%d %B %Y - %H:%M'))]),
              Field('description','text', label='Description', default='')
              
              )
    
    form2.element('textarea[name=description]')['_class'] = 'form-control'
    form2.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    form2.element('textarea[name=description]')['_rows'] = 5

    title = form2.element('#no_table_title')
    title['_class'] = 'form-control'
    title['_style'] = 'width:100%'
    title['_placeholder'] = 'Enter Complaint'   
    title['_autocomplete'] = 'off'   

    
    xcell = form2.element('#no_table_cell')
    xcell['_class'] = 'form-control'
    xcell['_style'] = 'width:100%'
    xcell['_placeholder'] = 'Enter Cell Number'   
    xcell['_autocomplete'] = 'off'   

    loc = form2.element('#no_table_location')
    loc['_class'] = 'form-control'
    loc['_style'] = 'width:100%'
    loc['_placeholder'] = 'Enter office location'   
    loc['_autocomplete'] = 'off'   

    patientmember = form2.element('#no_table_patientmember')
    patientmember['_class'] = 'form-control'
    patientmember['_style'] = 'width:100%'
    patientmember['_placeholder'] = 'Enter Patient Name or New Patient'   
    patientmember['_autocomplete'] = 'off'   

    doc = form2.element('#no_table_doctor')
    doc['_class'] = 'form-control'
    doc['_style'] = 'width:100%'

    dur = form2.element('#no_table_duration')
    dur['_class'] = 'form-control'
    dur['_style'] = 'width:100%'

    xnew_start = form2.element('input',_id='no_table_start_date')
    xnew_start['_class'] =  'input-group date form_datetime form_datetime bs-datetime'

    xnew_end = form2.element('input',_id='no_table_end_date')
    xnew_end['_class'] =  'input-group date form_datetime form_datetime bs-datetime'
    
    if(source == "home") :
        #returnurl = URL('admin', 'providerhome', vars=dict(page=1, memberpage=0, providerid=providerid,source=source))
        returnurl = URL('appointment', 'appointment', vars=dict(page=page, memberpage=0, providerid=providerid,source=source))
        
    else:     
        returnurl = URL('appointment','appointment',vars=dict(providerid=providerid,page=page,memberpage=memberpage,memberid=memberid,patientid=patientid,source=source))
     
    #dailyappts  = db((db.vw_appointment_today.providerid == providerid) & (db.vw_appointment_today.is_active == True)).select()
    #weeklyappts = db((db.vw_appointment_weekly.providerid == providerid) & (db.vw_appointment_weekly.is_active == True)).select()
    #monthlyappts = db((db.vw_appointment_monthly.providerid == providerid) & (db.vw_appointment_monthly.is_active == True)).select()
     
    
    
    
    if form2.process(formname='form_two').accepted:
        
      
       
        memberid = 0
        patientid = 0
        appt  = 0
        planid = 0
        
        doctorid = int(common.getid(form2.vars.doctor))
        
            
        #patient = <fname lanme>:<memberid>
        #xpatientmember = <fname lanme>:<memberid>
        rows = db(db.vw_memberpatientlist.patient == form2.vars.xpatientmember).select()
        if(len(rows) > 0):
            memberid = int(common.getid(rows[0].primarypatientid))
            patientid = int(common.getid(rows[0].patientid))
            patientmember = common.getstring(rows[0].patientmember) #patientmember/member ID
            fullname = common.getstring(rows[0].fullname)  # fname + lname
            patient = common.getstring(rows[0].patient)  # fname + lname + : + patientmember
        else:
            hmoplanid = 1
            r = db(db.hmoplan.hmoplancode == 'PREMWALKIN').select()
            if(len(r)>0):
                hmoplanid = common.getid(r[0].id)
            
            companyid = 4 #default to MyDP
            r = db((db.company.company == ' ') & (db.company.is_active == False)).select()
            if(len(r) > 0):
                companyid = common.getid(r[0].id)            
            
            fname = ""
            lname = ""
            strarr = form2.vars.xpatientmember.split()
            if(len(strarr) >0):
                fname = strarr[0].strip()
            for i in xrange(1,len(strarr)):
                lname = lname + " " + strarr[i].strip()
            provcount = db(db.patientmember.provider == providerid).count()
            patientmember = provcode + str(provcount).zfill(4) 

          
        
        #Treatment
        if((request.vars.chiefcomplaint == None) | (request.vars.chiefcomplaint == "")):
            treatmentid = 0
        else:
            treatmentid = int(common.getid(request.vars.chiefcomplaint))
        
        # find out day of the appt.
        duration = int(common.getid(form2.vars.duration))
        apptdt = common.getnulldt(form2.vars.start_date)
        endapptdt = apptdt + timedelta(minutes=duration)

        # title, cell, patientname
        apptid = 0
        #if((isBlocked(apptdt,endapptdt)==False) & (common.validappointment(db,doctorid, apptdt) == True)):
        if((isBlocked(apptdt,endapptdt)==False)):            
            if(memberid == 0):
                # create a new patient with assumption the name is entered as [<title>] [<fname>] [<lname>]
                db.patientmember.dob.requires = ""
                db.patientmember.address1.requires = ""
                db.patientmember.city.requires = ""
                db.patientmember.st.requires = ""
                db.patientmember.pin.requires = ""
                db.patientmember.cell.requires = ""
                db.patientmember.status.requires = ""
               
               
                patientid = db.patientmember.insert(
                   patientmember = patientmember,
                   title = " ",
                   fname = fname,
                   lname = lname,
                   cell = form2.vars.cell,
                   company = companyid,
                   hmoplan = hmoplanid,
                   groupregion = 1,
                   provider  = providerid,
                   hmopatientmember = False,
                   
                   newmember = True,
                   freetreatment = True,
                   is_active = True,
                   created_on = common.getISTFormatCurrentLocatTime(),
                   created_by = providerid,
                   modified_on =common.getISTFormatCurrentLocatTime(),
                   modified_by = providerid
               
                )
                        
                
                apptid  = db.t_appointment.insert(f_start_time=apptdt, f_end_time = endapptdt, f_duration= duration, cell = common.getstring(form2.vars.cell),
                                                f_title = common.getstring(form2.vars.title),
                                                f_patientname = "NP: " + common.getstring(form2.vars.patientmember),
                                                f_location = form2.vars.location,
                                                f_treatmentid = treatmentid,
                                                description = form2.vars.description,
                                                doctor = doctorid,
                                              provider=providerid,  is_active=True,
                                              created_on=common.getISTFormatCurrentLocatTime(),modified_on=common.getISTFormatCurrentLocatTime(),
                                              created_by = auth.user_id, modified_by=auth.user_id)
            else:
                apptid  = db.t_appointment.insert(f_start_time=apptdt, f_end_time = endapptdt, f_duration = duration, cell = common.getstring(form2.vars.cell),
                                                f_title = common.getstring(form2.vars.title),
                                                f_treatmentid = treatmentid,
                                                f_patientname = common.getstring(form2.vars.patientmember),
                                                description = form2.vars.description,f_location = form2.vars.location,
                                                doctor = doctorid, provider=providerid, patient=patientid,patientmember=memberid, is_active=True,
                                                created_on=common.getISTFormatCurrentLocatTime(),modified_on=common.getISTFormatCurrentLocatTime(),
                                                created_by = auth.user_id, modified_by=auth.user_id)  
                
            
            db(db.t_appointment.id == apptid).update(f_uniqueid = apptid)
            
            #save in case report
            csrdate = (form2.vars.start_date).strftime('%d/%m/%Y %H:%M:%S')
            csr = "Appointment CR:"  + csrdate + "\r\n" + form2.vars.description
            csrid = db.casereport.insert(patientid = patientid, providerid=providerid, doctorid=doctorid, casereport = csr, is_active=True,\
                                             created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid)
            # Send Confirmation SMS
            retval = sms_confirmation(apptid)
            
            if(retval == True):
                session.flash = "Appointment created! SMS confirmation sent to the patient!"
            else:
                session.flash = "Appointment created!"
                
            redirect(returnurl)
        else:
            session.flash = "Invalid Appointment Times"
            redirect(returnurl)
            
    elif form2.errors:
     
        response.flash = "Form has errors " + str(form2.errors)
            
    
    if form.process(formname='form_one').accepted:
        
        if((form.vars.start != None) & (form.vars.start != "")):
            start = (form.vars.start).strftime('%Y-%m-%d %H:%M:%S')
        
        if((form.vars.end != None) & (form.vars.end != None)):
            end = (form.vars.end).strftime('%Y-%m-%d %H:%M:%S')
        
          

        if(patientid > 0):
            rows=db((db.t_appointment.provider==providerid) & (db.t_appointment.patientmember == memberid) & (db.t_appointment.patient==patientid) & (db.t_appointment.is_active==True) & \
                    (db.t_appointment.f_start_time >= start) & (db.t_appointment.f_end_time <= end)).select(db.t_appointment.ALL, db.doctor.ALL, left=db.doctor.on(db.doctor.id == db.t_appointment.doctor))
        else:
            rows=db((db.t_appointment.provider==providerid) & (db.t_appointment.is_active==True) & \
                    (db.t_appointment.f_start_time >= start) & (db.t_appointment.f_end_time <= end)).select(db.t_appointment.ALL, db.doctor.ALL, left=db.doctor.on(db.doctor.id == db.t_appointment.doctor))

   
    return dict(form=form, form2=form2,  rows=rows,docs=docs,providerid=providerid, memberid=memberid, patientid=patientid, providername=providername,\
                returnurl=returnurl,page=page,memberpage=memberpage,start=start,end=end,defdate=defdate,membername=membername,patientname=patientname,source=source)

#return dict(form=form, form2=form2,  rows=rows,docs=docs,dailyappts=dailyappts, weeklyappts=weeklyappts,monthlyappts=monthlyappts,providerid=providerid, memberid=memberid, patientid=patientid, providername=providername,\
            #returnurl=returnurl,page=page,memberpage=memberpage,start=start,end=end,defdate=defdate,membername=membername,patientname=patientname,source=source)

def getmembers(db,providerid, member,fname,lname,cell,email,limitby,is_active):
    
    members = None
    
    if(is_active == None):
        activequery = True
    else:
        activequery = ((db.vw_imagememberlist.is_active == is_active))
        
    if(providerid > 0):
        query = ((db.vw_imagememberlist.providerid == providerid) & (activequery))
    else:
        query = ((activequery))
    
    
    if(member != ""):
        query = query & (db.vw_imagememberlist.patientmember.contains(member))
    if(fname != ""):
        query = query & (db.vw_imagememberlist.fname.contains(fname))
    if(lname != ""):
        query = query & (db.vw_imagememberlist.lname.contains(lname))
    if(cell != ""):
        query = query & (db.vw_imagememberlist.cell.contains(cell))
    if(email != ""):
        query = query & (db.vw_imagememberlist.email.contains(email))
    
  
    
    dsmembers = db(query).select(db.vw_imagememberlist.id,db.vw_imagememberlist.patientid,db.vw_imagememberlist.primarypatientid, db.vw_imagememberlist.patientmember, \
                                 db.vw_imagememberlist.fname, db.vw_imagememberlist.lname,db.vw_imagememberlist.patienttype,\
                                 db.vw_imagememberlist.cell,db.vw_imagememberlist.email,db.vw_imagememberlist.providerid,
                                 limitby=limitby, orderby = db.vw_imagememberlist.patientmember | ~db.vw_imagememberlist.patienttype
                                 
                                 )
    
        
    return dsmembers


#@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
#@auth.requires_login()
#def xappointment_create():

    
    #session.nonmemberscount=False
    #provdict = common.getprovider(auth, db)
    #providerid = provdict["providerid"]
    #providername = provdict["providername"]
    #page=common.getgridpage(request.vars)    
    
    
    #memberid = int(common.getid(request.vars.memberid))
    #memberref  = common.getstring(request.vars.memberref)
    
    #if(memberid > 0):
        #r = db(db.patientmember.id == memberid).select()
        #memberref= common.getstring(r[0].patientmember)


    #returnurl =  URL('appointment','calendar', vars=dict(page=page,providerid=providerid,memberid=memberid))

    #if(memberid > 9):
        #query = ((db.vw_imagememberlist.providerid == providerid) & (db.vw_imagememberlist.primarypatientid == memberid) &  (db.vw_imagememberlist.is_active == True))
    #else:
        #query = ((db.vw_imagememberlist.providerid == providerid) & (db.vw_imagememberlist.is_active == True))

    
    ##dsmembers = db(query).select(db.vw_imagememberlist.id,db.vw_imagememberlist.patientid,db.vw_imagememberlist.primarypatientid, db.vw_imagememberlist.patientmember, \
                                 ##db.vw_imagememberlist.fname, db.vw_imagememberlist.lname,db.vw_imagememberlist.patienttype,\
                                 ##db.vw_imagememberlist.cell,db.vw_imagememberlist.email,db.vw_imagememberlist.providerid,
                                 ##limitby=limitby, orderby = db.vw_imagememberlist.patientmember | ~db.vw_imagememberlist.patienttype
                                 
                                 ##)


    
    #fields=(db.vw_imagememberlist.patientid,db.vw_imagememberlist.primarypatientid, db.vw_imagememberlist.patientmember,db.vw_imagememberlist.fname,\
            #db.vw_imagememberlist.lname,db.vw_imagememberlist.patienttype,db.vw_imagememberlist.cell,db.vw_imagememberlist.email)    
    
  
    #headers={
            #'vw_imagememberlist.patientmember':'Member ID',
            #'vw_imagememberlist.patienttype':'P/D',
            #'vw_imagememberlist.fname':'First Name',
            #'vw_imagememberlist.lname':'Last Name',
            #'vw_imagememberlist.cell':'Cell',
            #'vw_imagememberlist.email':'Email'
            #}
 
    
    #exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
    #db.vw_imagememberlist.patientid.readable = False
    #db.vw_imagememberlist.providerid.readable = False
    #db.vw_imagememberlist.is_active.readable = False
    #db.vw_imagememberlist.primarypatientid.readable = False 
        
    #exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
    
    #links = [
             #dict(header='New Aptmt.',body=lambda row: A(IMG(_src="../static/assets/global/img/png/011-calendar.png",_width=30, _height=30),\
                                    #_href=URL('appointment','appointment_new',vars=dict(page=page,providerid=providerid,memberid=row.primarypatientid,patientid=row.patientid))))
             #]
    #orderby = (db.vw_imagememberlist.patientmember|~db.vw_imagememberlist.patienttype)

    #form = SQLFORM.grid(query=query,
                            #headers=headers,
                            #fields=fields,
                            #links=links,
                            #paginate=10,
                            #orderby = orderby,
                            #exportclasses=exportlist,
                            #links_in_grid=True,
                            #searchable=True,
                            #create=False,
                            #deletable=False,
                            #editable=False,
                            #details=False,
                            #user_signature=True
                           #)
    
    
 
    
    #return dict(form = form, returnurl=returnurl,page=page,providerid=providerid,providername=providername)
    
   



#@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
#@auth.requires_login()
#def xappointment_create():
    
    #i=0
    #provdict = common.getproviderfromid(db, request.vars.providerid)
    
    #providerid = int(common.getid(request.vars.providerid))
    #memberid = int(common.getid(request.vars.memberid))
    #memberref  = common.getstring(request.vars.memberref)
    
    #if(memberid > 0):
        #r = db(db.patientmember.id == memberid).select()
        #memberref= common.getstring(r[0].patientmember)
    
    #page       = common.getgridpage(request.vars)    
    
    
    #fname    = common.getstring(request.vars.fname)
    #lname    = common.getstring(request.vars.lname)
    #cell     = common.getstring(request.vars.cell)
    #email    = common.getstring(request.vars.email)
    
    ##display treatment plan filtering criteria
    #items_per_page = 5
    #limitby = (page*items_per_page,(page+1)*items_per_page+1) 
    
    ##display list of treatment plans
    #form = SQLFORM.factory(
            #Field('memberref','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border w3-small'),label='Member', default=memberref),
            #Field('fname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border w3-small'),label='First Name', default=fname),
            #Field('lname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border w3-small'),label='Last Name', default=lname),
            #Field('cell', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border w3-small'),label='Cell Phone',  default=cell ),
            #Field('email', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border w3-small'),label='Email',  default=email )
            #)
    
    #submit = form.element('input',_type='submit')
    #submit['_value'] = 'Search'    
    
    #dsmembers = getmembers(db,providerid,memberref,fname,lname,cell,email,limitby,True)
    
    
    
    #if form.accepts(request,session,keepvalues=True):
        
        
        #memberref     = common.getstring(form.vars.memberref)
        #fname      = common.getstring(form.vars.fname)
        #lname      = common.getstring(form.vars.lname)
        #cell       = common.getstring(form.vars.cell)
        #email       = common.getstring(form.vars.email)
        
        #dsmembers = getmembers(db,providerid,memberref, fname,lname,cell,email,limitby,True)
        
    #elif form.errors:
        #response.flash = 'form has errors'         
    
    #returnurl =  URL('appointment','calendar', vars=dict(page=page,providerid=providerid,memberid=memberid))
    
    #return dict(dsmembers=dsmembers,providername=provdict["providername"],form=form,providerid=provdict["providerid"],\
                #memberref=memberref,memberid=memberid,fname=fname,lname=lname,cell=cell,email=email,page=page,items_per_page=items_per_page,\
                #returnurl=returnurl)     

#def xappointment_hide():
    
    #return ''

def getcell():
    
    provdict = common.getprovider(auth, db)
    providerid = provdict["providerid"]
    
    xpatientmember = common.getstring(request.vars.xpatientmember)  #WLK03_FN WLK03_LN :P0014_0090
    rows = db(db.vw_memberpatientlist.patient == xpatientmember).select(db.vw_memberpatientlist.patientid,db.vw_memberpatientlist.cell)
    patientid = int(common.getid(rows[0].patientid))  if(len(rows)>0) else 0
    cell = common.getstring(rows[0].cell) if(len(rows)>0) else ""
    
    form2 = SQLFORM.factory(
                  Field('cell', 'string',  label='Cell',default=cell)
                  
                  #Field('chiefcomplaint', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), label='Treatment',\
                        #requires=IS_IN_DB(db((db.vw_treatmentlist.providerid==providerid)&(db.vw_treatmentlist.patientid == patientid)&(db.vw_treatmentlist.is_active==True)), \
                                          #'vw_treatmentlist.id', '%(chiefcomplaint)s : %(startdate)s')),
                  
                  )
    

    
    xcell = form2.element('#no_table_cell')
    xcell['_class'] = 'form-control'
    xcell['_style'] = 'width:100%'
    xcell['_placeholder'] = 'Enter Cell Number'   
    xcell['_autocomplete'] = 'off'   
     
    #trt = form2.element('#no_table_chiefcomplaint')
    #trt['_class'] = 'form-control'
    #trt['_style'] = 'width:100%'
     
    return dict(form2 = form2)    
 

 
 
    

def appointpatient_selector():
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])    

    if not request.vars.patientmember:
        return ''

    xmemberid = int(common.getid(request.vars.xmemberid))
    
    #if(memberid == 0):
        #sqlquery = db((db.vw_appointmentmemberlist.providerid == providerid) & (db.vw_appointmentmemberlist.is_active == True))
    #if(memberid > 0 ):
        #sqlquery = db((db.vw_appointmentmemberlist.providerid == providerid) & (db.vw_appointmentmemberlist.primarypatientid == memberid) & (db.vw_appointmentmemberlist.is_active == True))
    
    if(request.vars.patientmember == ""):
        pattern = '%'
    else:
        pattern = request.vars.patientmember.capitalize() + '%'
        
    if(xmemberid == 0):
        selected = [row.patient for row in db(((db.vw_appointmentmemberlist.is_active == True)  & \
                                               ((db.vw_appointmentmemberlist.providerid == providerid) | ((db.vw_appointmentmemberlist.providerid == 1)&\
                                                                                                          (db.vw_appointmentmemberlist.hmopatientmember == False))))&\
                                              (db.vw_appointmentmemberlist.patient.like(pattern))).select()]
    else:
        selected = [row.patient for row in db(((db.vw_appointmentmemberlist.is_active == True)  & (db.vw_appointmentmemberlist.primarypatientid == xmemberid)  & \
                                               ((db.vw_appointmentmemberlist.providerid == providerid) | ((db.vw_appointmentmemberlist.providerid == 1)&\
                                                                                                          (db.vw_appointmentmemberlist.hmopatientmember == False))))&\
                                              (db.vw_appointmentmemberlist.patient.like(pattern))).select()]
        
        
    return ''.join([DIV(k,
                 _onclick="jQuery('#no_table_patientmember').text('%s')" % k,
                 _onmouseover="this.style.backgroundColor='cyan'",
                 _onmouseout="this.style.backgroundColor='white'",
                 _style="z-index:500000;width:100%;font-family:verdana;font-size:12px;color:black;font-weight:normal"                 
                 ).xml() for k in selected])




@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def new_appointment():
    
    
    clinicid = session.clinicid
    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getproviderfromid(db,providerid)
    prov = db(db.provider.id == providerid).select(db.provider.pa_practicename,db.provider.pa_practiceaddress)
    doctorid = int(common.getdefaultdoctor(db, providerid))

    if(request.vars.defdate == None):
            defdate = common.getISTFormatCurrentLocatTime()
            defdt1 = defdate.strftime('%d %B %Y - %I:%M %p')
    else:
            defdate = datetime.datetime.strptime(request.vars.defdate, "%Y-%m-%d %H:%M")
            defdt1 = defdate.strftime('%d %B %Y - %I:%M %p')
            
    
    returnurl=(URL('admin','providerhome', vars=dict(defdate=defdate)))
    
    
    form2 = SQLFORM.factory(
        Field('patientmember', 'string',  \
              widget=lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form-control',_style='width:100%',_placeholder='Enter Patient Name',_autocomplete='off'), \
              label='Patient',default='',requires=[IS_NOT_EMPTY()]),
        
        Field('cell', 'string',\
              widget=lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form-control',_style='width:100%',_placeholder='Enter Cell',_autocomplete='off'), \
              label='Cell',default=""),
        
        Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form-control',_style='width:100%'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
        
        Field('title', 'text',\
              widget=lambda field, value:SQLFORM.widgets.text.widget(field, value, _class='form-control',_style='height:100px;line-height:1.0;',_rows='5'), \
              label='Patient',default=""),
        
        Field('location', 'string',\
              widget=lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form-control',_style='width:100%',_placeholder='Enter Office Location',_autocomplete='off'), \
              label='Clinic Location',default=common.getstring(prov[0].pa_practicename) + ", " + common.getstring(prov[0].pa_practiceaddress)),
        
        Field('xpatientmember', 'string',  label='Patient',default=''),
        Field('xfullname', 'string',  label='Patient', default=''),
        Field('xmemberid', 'string',  label='Patient',default=''),
        
        Field('start_date', 'datetime',\
              widget=lambda field, value:SQLFORM.widgets.datetime.widget(field, value, _class='input-group date form_datetime form_datetime bs-datetime'), \
              label='Start Date & Time',default=defdate, requires=[IS_NOT_EMPTY(), IS_DATETIME(format=T('%d %B %Y - %H:%M'))]),
        
        Field('duration', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,  _class='form-control',_style='width:100%'), default='30', label='Doctor',requires=IS_IN_SET(['30','45','60'])),
        Field('end_date', 'datetime',\
              widget=lambda field, value:SQLFORM.widgets.datetime.widget(field, value, _class='input-group date form_datetime form_datetime bs-datetime'), \
              label='End Date & Time',default=request.now,requires=[IS_NOT_EMPTY(), IS_DATETIME(format=T('%d %B %Y - %H:%M'))]),
        Field('description','text',\
              widget=lambda field, value:SQLFORM.widgets.text.widget(field, value, _class='form-control',_style='height:100px;line-height:1.0;',_rows='5'), \
              label='Description', default='')
        )
      
   
    
    
    if(form2.accepts(request,session,keepvalues=True)):
        
        retval = saveNewAppt(auth.user_id, form2,providerid)
       
        
        if(retval == True):
                session.flash = "Appointment created! SMS & Email confirmation will be sent to the patient and the doctor!"
        else:
                session.flash = "Appointment not created - Invalid Appointment Times"
                
        redirect(returnurl)         
        
    elif form2.errors:
        response.flash = "Error creating Appointment!" + str(form2.errors)
    
    #if form2.accepts(request,session,keepvalues=True):
        #memberid = 0
        #patientid = 0
        #appt  = 0
        #planid = 0
        
        
        
        #ucttime = common.getUCTCurrentLocalTime()
        #isttime = common.getISTFromUCT(ucttime)
        
        
        #doctorid = int(common.getid(form2.vars.doctor))
        
            
        ##patient = <fname lanme>:<memberid>
        ##xpatientmember = <fname lanme>:<memberid>
        #rows = db(db.vw_memberpatientlist.patient == form2.vars.xpatientmember).select()
        #if(len(rows) > 0):
            #memberid = int(common.getid(rows[0].primarypatientid))
            #patientid = int(common.getid(rows[0].patientid))
            #patientmember = common.getstring(rows[0].patientmember) #patientmember/member ID
            #fullname = common.getstring(rows[0].fullname)  # fname + lname
            #patient = common.getstring(rows[0].patient)  # fname + lname + : + patientmember
        #else:
            #hmoplanid = 1
            #r = db(db.hmoplan.hmoplancode == 'PREMWALKIN').select()
            #if(len(r)>0):
                #hmoplanid = common.getid(r[0].id)
            
            #companyid = 4 #default to MyDP
            #r = db((db.company.company == ' ') & (db.company.is_active == False)).select()
            #if(len(r) > 0):
                #companyid = common.getid(r[0].id)            
            
            #fname = ""
            #lname = ""
            #strarr = form2.vars.xpatientmember.split()
            #if(len(strarr) >0):
                #fname = strarr[0].strip()
            #for i in xrange(1,len(strarr)):
                #lname = lname + " " + strarr[i].strip()
            #provcount = db(db.patientmember.provider == providerid).count()
            #patientmember = provdict["provider"] + str(provcount).zfill(4) 
             
          
        
        ##Treatment
        #treatmentid = 0
        
        ## find out day of the appt.
        #duration = int(common.getid(form2.vars.duration))
        
        
        
        #apptdt = common.getnulldt(form2.vars.start_date)
        #endapptdt = apptdt + timedelta(minutes=duration)
         
        #apptid = 0
        ##if((isBlocked(apptdt,endapptdt)==False) & (common.validappointment(db,doctorid, apptdt) == True)):
        #if((isBlocked(apptdt,endapptdt)==False)):            
            #if(memberid == 0):
                ## create a new patient with assumption the name is entered as [<title>] [<fname>] [<lname>]
                #db.patientmember.dob.requires = ""
                #db.patientmember.address1.requires = ""
                #db.patientmember.city.requires = ""
                #db.patientmember.st.requires = ""
                #db.patientmember.pin.requires = ""
                #db.patientmember.cell.requires = ""
                #db.patientmember.status.requires = ""
               
               
                #patientid = db.patientmember.insert(
                   #patientmember = patientmember,
                   #title = " ",
                   #fname = fname,
                   #lname = lname,
                   #cell = form2.vars.cell,
                   #company = companyid,
                   #hmoplan = hmoplanid,
                   #groupregion = 1,
                   #provider  = providerid,
                   #hmopatientmember = False,
                   
                   #newmember = True,
                   #freetreatment = True,
                   #is_active = True,
                   #created_on = datetime.datetime.today(),
                   #created_by = providerid,
                   #modified_on =datetime.datetime.today(),
                   #modified_by = providerid
               
                #)
                        
               
                
                #apptid  = db.t_appointment.insert(f_start_time=apptdt, f_end_time = endapptdt, f_duration= duration, cell = common.getstring(form2.vars.cell),
                                                #f_title = common.getstring(form2.vars.title),f_status='Open',
                                                #f_patientname = common.getstring(form2.vars.patientmember),
                                                #f_location = form2.vars.location,
                                                #f_treatmentid = treatmentid,
                                                #description = form2.vars.description,
                                                #doctor = doctorid,
                                                #patient=patientid,
                                                #patientmember=patientid,
                                                #sendsms = True,
                                              #provider=providerid,  is_active=True,
                                              #created_on=common.datetime.datetime.today(),modified_on=datetime.datetime.today(),
                                              #created_by = auth.user_id, modified_by=auth.user_id)
            #else:
                #apptid  = db.t_appointment.insert(f_start_time=apptdt, f_end_time = endapptdt, f_duration = duration, cell = common.getstring(form2.vars.cell),
                                                #f_title = common.getstring(form2.vars.title),f_status='Open',
                                                #f_treatmentid = treatmentid,
                                                #f_patientname = common.getstring(form2.vars.patientmember),
                                                #description = form2.vars.description,f_location = form2.vars.location, sendsms = True,
                                                #doctor = doctorid, provider=providerid, patient=patientid,patientmember=memberid, is_active=True,
                                                #created_on=datetime.datetime.today(),modified_on=datetime.datetime.today(),
                                                #created_by = auth.user_id, modified_by=auth.user_id)  
            
            #db(db.t_appointment.id == apptid).update(f_uniqueid = apptid)
            
            ##save in case report
            #common.logapptnotes(db,common.getstring(form2.vars.title),common.getstring(form2.vars.description),apptid)
            
            ## Send Confirmation SMS
            #retval = sms_confirmation(apptid,"create")
            
            
            #if(retval == True):
                #session.flash = "Appointment created! SMS & Email confirmation sent to the patient and the doctor!"
            #else:
                #session.flash = "Appointment created! No SMS confirmation was sent to the patient!"
            #redirect(returnurl)              
        #else:
            #session.flash = "Invalid Appointment Times"
            #redirect(returnurl)
         
    #elif form2.errors:
        #response.flash = "Error creating Appointment!" + str(form2.errors)
      

    return dict(form2=form2, returnurl=returnurl, providerid=providerid, apptid=173, providername=provdict["providername"],
                source='xhome')

#@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
#@auth.requires_login()
#def xappointment_new():

    #membername = ""
    #memberref = ""
    #patientname = ""
    
    #providerid = int(common.getnegid(request.vars.providerid))
    #provdict   = common.getproviderfromid(db, providerid)
    #memberid   = int(common.getid(request.vars.memberid))
    #patientid  = int(common.getid(request.vars.patientid))
    
    
    #page = common.getgridpage(request.vars)
    
    #rows = db((db.vw_imagememberlist.providerid == providerid) & (db.vw_imagememberlist.primarypatientid == memberid)  & (db.vw_imagememberlist.patientid == memberid)).select()
    #if(len(rows) > 0):
        #membername = rows[0].fname + " "  + rows[0].lname
        #memberref = rows[0].patientmember

    
        
    #rows = db((db.vw_imagememberlist.providerid == providerid) & (db.vw_imagememberlist.primarypatientid == memberid)  & (db.vw_imagememberlist.patientid == patientid)).select()
    #if(len(rows) > 0):
        #patientname = rows[0].fname + " "  + rows[0].lname
        
   
    #returnurl = URL('appointment', 'appointment_create', vars=dict(page=page,providerid=providerid,memberid=memberid,memberref=memberref))
    
    #form = SQLFORM.factory(
           #Field('title','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border'),label='Title', default=''),
           #Field('location','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border'),label='Location', default=''),
           #Field('start', 'datetime',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border datetime'),label='Start Date & Time',requires=[IS_NOT_EMPTY(), IS_DATETIME(format=T('%d/%m/%Y %H:%M:%S')), IS_NOT_IN_DB(db, db.t_appointment.f_start_time)]),
           #Field('end', 'datetime',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border datetime'),label='End Date & Time',requires=[IS_NOT_EMPTY(), IS_DATETIME(format=T('%d/%m/%Y %H:%M:%S'))])
           #)
    
        
    #if form.accepts(request,session,keepvalues=True):
        #appt  = db.t_appointment.insert(f_title = form.vars.title, f_start_time=form.vars.start, f_end_time = form.vars.end, f_location = form.vars.location,
                                      #provider=providerid, patient=patientid,patientmember=memberid, is_active=True,
                                      #created_on=request.now,modified_on=request.now,
                                      #created_by = auth.user_id, modified_by=auth.user_id)
        
        #common.dashboard(db, session, providerid)
        #redirect(URL('appointment','calendar',vars=dict(providerid=providerid,page=0,memberid=memberid)))
        
        
    #else:
        #response.flash = 'Form has errors'

    
    #return dict(form=form, page=page,returnurl=returnurl, providerid=providerid, providername=provdict["providername"],membername=membername,patientname=patientname,memberid=memberid,memberref=memberref)


#@auth.requires_login()
#def xappointment_read():
    #record = db.t_appointment(request.args(0)) or redirect(URL('error'))
    #form=crud.read(db.t_appointment,record)
    #return dict(form=form)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def appointment_update():
    
    
    apptid = int(common.getid(request.vars.apptid))
    appt = db(db.t_appointment.id == apptid).select()    

    
    
    source = common.getstring(request.vars.source)
    page = common.getpage(request.vars.page)   
    memberpage = common.getpage(request.vars.memberpage)
    
    provdict = common.getprovider(auth, db)
    providername = provdict["providername"]
    providerid = provdict["providerid"]

    
    flag = common.getboolean(appt[0].blockappt)
    if(flag == True):
        redirect(URL('appointment', 'appointment_blockupdate', vars=dict(apptid=apptid,providerid=providerid,source=source)))
    
    
    title = common.getstring(appt[0].f_title)
    location = common.getstring(appt[0].f_location)
    cell = common.getstring(appt[0].cell)
    patientname = common.getstring(appt[0].f_patientname) 
    duration = int(common.getid(appt[0].f_duration))
    description = common.getstring(appt[0].description)
    
    patientid = int(common.getid(appt[0].patient))
    memberid  = int(common.getid(appt[0].patientmember))
    doctorid = int(common.getid(appt[0].doctor))
    treatmentid = int(common.getid(appt[0].f_treatmentid))
    
    
    #patient = <fname lanme>:<memberref>
    #xpatientmember = <fname lanme>:<memberref>
    patientmember = ""
    patient=""
    membername = ""
    fullname = ""
    status = ""
    
    rows = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select()
    if(len(rows) > 0):
        patientmember = common.getstring(rows[0].patientmember) #Patient/Member ID
        patient = common.getstring(rows[0].patient)  # fname + lname + : + patientmember
    else:
        fullname = patientname
        
        

    curraptdt = appt[0].f_start_time
    str2 = curraptdt.strftime('%d %B %Y - %H:%M')
    str3 = appt[0].f_end_time
    str4 = str3.strftime('%d %B %Y - %H:%M') 
    
    status = appt[0].f_status

   
    if(patientid > 0):
        
        form2 = SQLFORM.factory(
            Field('patientmember', 'string',  label='Patient',default=patientname,requires=[IS_NOT_EMPTY()],writable=False),
            Field('cell', 'string',  label='Cell',default=cell),
            Field('treatment', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=treatmentid,label='Treatment List',\
                   requires=IS_EMPTY_OR(IS_IN_DB(db((db.vw_treatmentlist.providerid==providerid)&(db.vw_treatmentlist.patientid == patientid)&(db.vw_treatmentlist.is_active==True)), \
                                    'vw_treatmentlist.id', '%(treatment)s : %(startdate)s'))),
            Field('chiefcomplaint', 'text', default=title),
            Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active==True)&(db.doctor.stafftype=='Doctor')), 'doctor.id', '%(name)s')),
            Field('title', 'text',  label='Patient',default=title),
            Field('location', 'string',  label='Clinic Location',default=location),
            Field('status', 'string',  label='Status',default=status,requires = IS_IN_SET(APPTSTATUS)),            
            Field('xpatientmember', 'string',  label='Patient',default=patient),
            Field('xfullname', 'string',  label='Patient', default=fullname),
            Field('xmemberid', 'string',  label='Patient',default=memberid),
            Field('start_date', 'datetime',label='Start Date & Time',default=str2,requires=[IS_NOT_EMPTY()]),
            Field('duration', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=duration, label='Doctor',requires=IS_IN_SET(['30','45','60'])),
            Field('end_date', 'datetime',label='End Date & Time', default=str4,requires=[IS_NOT_EMPTY()]),
            Field('description','text', label='Description', default=description)
    
            )
    else:
        form2 = SQLFORM.factory(
            Field('patientmember', 'string',  label='Patient',default=patientname,requires=[IS_NOT_EMPTY()],writable=False),
            Field('cell', 'string',  label='Cell',default=cell),
            Field('treatment', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=treatmentid,label='Treatment List',\
                              requires=IS_EMPTY_OR(IS_IN_DB(db((db.vw_treatmentlist.providerid==providerid)&(db.vw_treatmentlist.patientid == patientid)&(db.vw_treatmentlist.is_active==True)), \
                                               'vw_treatmentlist.id', '%(treatment)s : %(startdate)s'))),            Field('chiefcomplaint', 'text', default=title),
            Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
            Field('title', 'text',  label='Patient',default=title),
            Field('location', 'string',  label='Clinic Location',default=location),
            Field('status', 'string',  label='Status',default=status,requires = IS_IN_SET(APPTSTATUS)),
            Field('xpatientmember', 'string',  label='Patient',default=patient),
            Field('xfullname', 'string',  label='Patient', default=fullname),
            Field('xmemberid', 'string',  label='Patient',default=memberid),
            Field('start_date', 'datetime',label='Start Date & Time',default=str2,requires=[IS_NOT_EMPTY()]),
            Field('duration', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=duration, label='Doctor',requires=IS_IN_SET(['15','30','45','60'])),
            Field('end_date', 'datetime',label='End Date & Time', default=str4,requires=[IS_NOT_EMPTY()]),
            Field('description','text', label='Description', default=description)
    
            )
        
      
    form2.element('textarea[name=description]')['_class'] = 'form-control'
    form2.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    form2.element('textarea[name=description]')['_rows'] = 5
    
    form2.element('textarea[name=title]')['_class'] = 'form-control'
    form2.element('textarea[name=title]')['_style'] = 'height:100px;line-height:1.0;'
    form2.element('textarea[name=title]')['_rows'] = 5    
    form2.element('textarea[name=title]')['_placeholder'] = "Enter Title"
    
    form2.element('textarea[name=chiefcomplaint]')['_class'] = 'form-control'
    form2.element('textarea[name=chiefcomplaint]')['_style'] = 'height:100px;line-height:1.0;'
    form2.element('textarea[name=chiefcomplaint]')['_rows'] = 5    
    form2.element('textarea[name=chiefcomplaint]')['_placeholder'] = "Enter Complaint"
    
    #patientmember = form2.element('#no_table_patientmember')
    #patientmember['_class'] = 'form-control'
    #patientmember['_style'] = 'width:100%'
    #patientmember['_placeholder'] = 'Enter Patient Name or New Patient'   
    #patientmember['_autocomplete'] = 'off'   
    xcell = form2.element('#no_table_cell')
    xcell['_class'] = 'form-control'
    xcell['_style'] = 'width:100%'
    xcell['_placeholder'] = 'Enter Cell Number'   
    xcell['_autocomplete'] = 'off'   

    trmnt = form2.element('#no_table_treatment')
    trmnt['_class'] = 'form-control'
    trmnt['_style'] = 'width:100%'  
    

    loc = form2.element('#no_table_location')
    loc['_class'] = 'form-control'
    loc['_style'] = 'width:100%'
    loc['_placeholder'] = 'Enter clinic'   
    loc['_autocomplete'] = 'off'   

    dur = form2.element('#no_table_duration')
    dur['_class'] = 'form-control'
    dur['_style'] = 'width:100%'


    doc = form2.element('#no_table_doctor')
    doc['_class'] = 'form-control'
    doc['_style'] = 'width:100%'
    
    sts = form2.element('#no_table_status')
    sts['_class'] = 'form-control'
    sts['_style'] = 'width:100%'    
    
  
  
    xnew_start = form2.element('input',_id='no_table_start_date')
    xnew_start['_class'] =  'form-control form_datetime bs-datetime'


    xnew_end = form2.element('input',_id='no_table_end_date')
    xnew_end['_class'] =  'form-control form_datetime bs-datetime'
    
    
    
    if(source == "home") :
        returnurl = URL('admin','providerhome',vars=dict(apptid = apptid,page=page,memberpage=memberpage,providerid=providerid,source=source))
    else:     
        returnurl = URL('appointment','appointment',vars=dict(providerid=providerid,page=page,memberpage=memberpage,memberid=memberid,patientid=patientid,source=source))
      
      
      
    if form2.process(formname='form_two',keepvalues=True).accepted:
            
        
        page = common.getpage(request.vars.page)
        memberpage = common.getpage(request.vars.memberpage)
        
        apptid = int(common.getid(request.vars.apptid))
        
        newdescription = common.getstring(request.vars.description)
        cell = common.getstring(request.vars.cell)
        treatmentid = int(common.getid(request.vars.treatment))
        chiefcomplaint = common.getstring(request.vars.chiefcomplaint)  # this is stored in f_title field
        
        
        duration = int(common.getid(request.vars.duration))
        start_date = common.getnulldt(request.vars.start_date)
        apptdt = datetime.datetime.strptime(start_date, '%d %B %Y - %H:%M')
        endapptdt = apptdt + timedelta(minutes=duration)

        
        providerid = int(common.getid(request.vars.providerid))
        memberid = int(common.getid(request.vars.xmemberid))
        doctorid = int(common.getid(request.vars.doctor))
        
        #patient = <fname lanme>:<membercode>
        #xpatientmember = <fname lanme>:<membercode>
        rows = db(db.vw_memberpatientlist.patient == form2.vars.xpatientmember).select()
        
        if(len(rows) > 0):
            memberid = int(common.getid(rows[0].primarypatientid))
            patientid = int(common.getid(rows[0].patientid))
        else:
            memberid = 0
            patientid = 0
       
         

        
        db(db.t_appointment.id == apptid).update(f_title = chiefcomplaint, f_start_time = apptdt, f_end_time =  endapptdt, f_duration=duration,\
                                                 f_status=common.getstring(form2.vars.status),\
                                                 description = newdescription, cell = cell,  doctor=doctorid,f_treatmentid=treatmentid,\
                                                 modified_by = auth.user_id, modified_on=common.getISTFormatCurrentLocatTime())
        
        
        #save in case report
        
        if((patientid > 0) & ((title.strip().upper() != chiefcomplaint.strip().upper()) | (description.strip().upper() != newdescription.strip().upper() ))):
            
            common.logapptnotes(db,chiefcomplaint,newdescription,apptid)
            #csrdate = (request.now).strftime('%d/%m/%Y %H:%M:%S')
            #csr = "Appointment CR:"  + csrdate + "\r\n" + form2.vars.title + "\r\n" + form2.vars.description 
            #csrid = db.casereport.insert(appointmentid=apptid,memberid=memberid,patientid = patientid, providerid=providerid, doctorid=doctorid, casereport = csr, is_active=True,\
                                     #created_on = request.now, created_by = providerid, modified_on = request.now, modified_by = providerid)        
        
        # Send Confirmation SMS only when appt start date is changed
        # The confirmation sms will be sent from Superadmin Activity Tracker Group Message module
        # At this point we will send 
        retval=False
        if(apptdt != curraptdt):
                db(db.t_appointment.id == apptid).update(sendsms = True, sendrem = True,smsaction="update")
                session.flash = "Appointment updated! SMS confirmation will be sent to the patient and the doctor!"
    
        #return HTML(BODY(SCRIPT('window.close()'))).xml()        
        redirect(returnurl)

    elif form2.errors:
        session.flash = "Error updating appointment "  + str(form2.errors)
        redirect(returnurl)
        #return HTML(BODY(SCRIPT('window.close()'))).xml()        
   
    return dict(form2=form2,apptid = apptid, providerid=providerid, memberid=memberid, patientid=patientid, providername=providername,\
                    returnurl=returnurl,page=page,memberpage=memberpage,membername=patient,patientname=fullname,source=source)
    
@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def appointment_block():

    provdict = common.getprovider(auth, db)
    providername = provdict["providername"]
    providerid = provdict["providerid"]
    clinicid = session.clinicid
    
    doctorid = int(common.getdefaultdoctor(db, providerid))    
    
    form2 = SQLFORM.factory(
        Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid,  label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active==True)&(db.doctor.stafftype=='Doctor')), 'doctor.id', '%(name)s')),
        Field('title', 'string',  label='Patient'),
        Field('start_date', 'datetime',label='Start Date & Time',requires=[IS_NOT_EMPTY(), IS_DATETIME(format=T('%d %B %Y - %H:%M'))]),
        Field('duration', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), label='Doctor',default="Full Day", requires=IS_IN_SET(['Pre-Lunch','Post-Lunch','Full Day'])),
        Field('end_date', 'datetime',label='Start Date & Time',requires=[IS_NOT_EMPTY(), IS_DATETIME(format=T('%d %B %Y - %H:%M'))]),
        Field('description','text', label='Description')

        )
  
    form2.element('textarea[name=description]')['_class'] = 'form-control'
    form2.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    form2.element('textarea[name=description]')['_rows'] = 5
    
    
    title = form2.element('#no_table_title')
    title['_class'] = 'form-control'
    title['_style'] = 'width:100%'
    title['_placeholder'] = 'Enter Blocking Appointment Name'   
    title['_autocomplete'] = 'off'   


    dur = form2.element('#no_table_duration')
    dur['_class'] = 'form-control'
    dur['_style'] = 'width:100%'


    doc = form2.element('#no_table_doctor')
    doc['_class'] = 'form-control'
    doc['_style'] = 'width:100%'
    
   
  
    xnew_start = form2.element('input',_id='no_table_start_date')
    xnew_start['_class'] =  'form-control form_datetime bs-datetime'
    xnew_start['_autocomplete'] = 'off' 
  
    xnew_end = form2.element('input',_id='no_table_end_date')
    xnew_end['_class'] =  'form-control form_datetime bs-datetime'
    xnew_end['_autocomplete'] = 'off'
  
    returnurl = URL('admin', 'providerhome', vars=dict(page=1, providerid=providerid))
     
    if form2.process(formname='form_two',keepvalues=True).accepted:
    
       
        startdate = datetime.datetime.strptime(request.vars.start_date, "%d %B %Y - %H:%M")
        enddate = datetime.datetime.strptime(request.vars.end_date, "%d %B %Y - %H:%M")
        
        intduration = 0       
      
    
        apptid  = db.t_appointment.insert(f_start_time=startdate, f_end_time = enddate, f_duration= intduration, cell = "",
                                        f_title = common.getstring(form2.vars.title),
                                        f_patientname = "",
                                        f_location = "",
                                        f_treatmentid = "",
                                        description = form2.vars.description,
                                        doctor = doctorid,
                                      provider=providerid, 
                                      clinicid = clinicid,
                                      is_active=True,
                                      newpatient = False,
                                      blockappt = True,
                                      created_on=common.getISTFormatCurrentLocatTime(),modified_on=common.getISTFormatCurrentLocatTime(),
                                      created_by = auth.user_id, modified_by=auth.user_id)

    
        redirect(returnurl)
        
    elif form2.errors:
        response.flash = "Error in the form " + str(form2.errors)
          
      
    return dict(form2=form2, providerid=providerid, providername=providername,\
                    returnurl=returnurl,page=1,source="")

    

#@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
#@auth.requires_login()
def appointment_blockupdate():


   
   
    providername = ""
    
    apptid = int(common.getid(request.vars.apptid))
    providerid = int(common.getid(request.vars.providerid))
    
    appt = db(db.t_appointment.id == apptid).select(db.t_appointment.f_start_time, db.t_appointment.f_end_time, db.t_appointment.provider, db.t_appointment.doctor, \
                                                    db.t_appointment.f_duration, db.t_appointment.f_title,db.t_appointment.description)
   
    start_date = (appt[0].f_start_time).strftime('%d %B %Y - %H:%M')
    end_date = (appt[0].f_end_time).strftime('%d %B %Y - %H:%M') 
    

    doctorid  = int(common.getid(appt[0].doctor))    
    
   

    duration = "Full Day"
    form2 = SQLFORM.factory(
        Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid,  label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active==True)&(db.doctor.stafftype=='Doctor')), 'doctor.id', '%(name)s')),
        Field('title', 'string',  label='Patient', default = common.getstring(appt[0].f_title)),
        Field('start_date', 'datetime',label='Start Date & Time',default=start_date, requires=[IS_NOT_EMPTY()]),
        Field('duration',  widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'),  default=duration,label='Duration', requires=IS_IN_SET(['Pre-Lunch','Post-Lunch','Full Day'])),
        Field('end_date', 'datetime',label='End Date & Time',default=end_date, requires=[IS_NOT_EMPTY()]),
        Field('description','text', label='Description',default=appt[0].description)

        )
  
    form2.element('textarea[name=description]')['_class'] = 'form-control'
    form2.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    form2.element('textarea[name=description]')['_rows'] = 5
    
    
    title = form2.element('#no_table_title')
    title['_class'] = 'form-control'
    title['_style'] = 'width:100%'
    title['_placeholder'] = 'Enter Blocking Appointment Name'   
    title['_autocomplete'] = 'off'   



    doc = form2.element('#no_table_doctor')
    doc['_class'] = 'form-control'
    doc['_style'] = 'width:100%'
    
   
  
    xnew_start = form2.element('input',_id='no_table_start_date')
    xnew_start['_class'] =  'form-control form_datetime bs-datetime'
    xnew_start['_autocomplete'] = 'off'   
  
    xnew_end = form2.element('input',_id='no_table_end_date')
    xnew_end['_class'] =  'form-control form_datetime bs-datetime'
    xnew_end['_autocomplete'] = 'off'   
    
   
    returnurl = URL('admin', 'providerhome', vars=dict(page=1, providerid=providerid))
    
    if form2.process(formname='form_two',keepvalues=True).accepted:

        doctorid = int(common.getid(request.vars.doctor))
        startdate = datetime.datetime.strptime(request.vars.start_date, "%d %B %Y - %H:%M")
        enddate = datetime.datetime.strptime(request.vars.end_date, "%d %B %Y - %H:%M")            
      
        
        intduration = 720
        title = common.getstring(form2.vars.title)
        description = common.getstring(form2.vars.description)
        
        db(db.t_appointment.id == apptid).update(f_title = title, f_start_time = startdate, f_end_time =  enddate, f_duration=intduration,\
                                                 description = description,  doctor=doctorid,smsaction="update",\
                                                 modified_by = providerid, modified_on=common.getISTFormatCurrentLocatTime())
        
        session.flash = "Successfully Updated Block Appointment"
        redirect(returnurl)
        
    elif form2.errors:
        response.flash = "Error in the form " + str(form2.errors)
          
      
    return dict(form2=form2, apptid=apptid, providerid=providerid, providername=providername,\
                    returnurl=returnurl,page=1,source="home")

    
    




@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def delete_appointment():
    
    source = common.getstring(request.vars.source)
    apptid = int(common.getid(request.vars.apptid))
    appt = db(db.t_appointment.id == apptid).select()
    memberid = int(common.getid(appt[0].patientmember))
    patientid = int(common.getid(appt[0].patient))
    providerid = int(common.getid(appt[0].provider))
    providerdict = common.getproviderfromid(db,providerid)
    providername = providerdict["providername"]
    
    startdate = (appt[0].f_start_time).strftime('%d %B %Y - %H:%M')
    header = common.getstring(appt[0].f_patientname)
     
    page = common.getpage(request.vars.page)          
    memberpage = common.getpage(request.vars.memberpage)          
    returnurl = URL('admin', 'providerhome', vars=dict(page=1, memberpage=0, providerid=providerid,source=source))
    
    form = FORM.confirm('Yes?',{'No':returnurl})

    if form.accepted:
        db((db.t_appointment.id == apptid)).update(is_active=False,f_status='Cancelled', smsaction="cancel",modified_by = auth.user_id, modified_on=common.getISTFormatCurrentLocatTime())
        
        # Send Confirmation SMS
        #retval=False
        #retval = sms_confirmation(apptid,'delete')
        
        
        session.flash = "Appointment has been cancelled! SMS confirmation will be sent to the patient and the doctor"
        
        redirect(returnurl)

    return dict(form=form,returnurl=returnurl,providerid=providerid,providername=providername,page=page,memberpage=memberpage,header=header,startdate=startdate,source=source)




@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def delete_block():
    apptid = int(common.getid(request.vars.apptid))
    appt = db(db.t_appointment.id == apptid).select(db.t_appointment.f_start_time, db.t_appointment.f_end_time, db.t_appointment.provider, db.t_appointment.doctor, \
                                                    db.t_appointment.f_duration, db.t_appointment.f_title,db.t_appointment.description)
    
    
    providerid = 0 if(len(appt) == 0) else int(common.getid(appt[0].provider))
    title = "" if(len(appt) == 0) else common.getstring(appt[0].f_title)
    startdate = "01 January 1990 - 00:00:00" if(len(appt) == 0) else  (appt[0].f_start_time).strftime('%d %B %Y - %H:%M')
    enddate = "01 January 1990 - 00:00:00" if(len(appt) == 0) else  (appt[0].f_end_time).strftime('%d %B %Y - %H:%M')
  
    
    returnurl = URL('admin', 'providerhome', vars=dict(page=1, providerid=providerid))
    
    form = FORM.confirm('Yes?',{'No':returnurl})

    if form.accepted:
        db((db.t_appointment.id == apptid)).update(is_active=False,smsaction="cancelled",modified_by = auth.user_id, modified_on=common.getISTFormatCurrentLocatTime())
        redirect(returnurl)

    return dict(form=form,returnurl=returnurl,providerid=providerid,page=1, source="home",title=title,startdate=startdate,enddate=enddate)


def customer_appointment_update():


        apptid = int(common.getid(request.vars.apptid))
        appt = db(db.t_appointment.id == apptid).select()    

        

        source = common.getstring(request.vars.source)
        page = common.getpage(request.vars.page)   
        memberpage = common.getpage(request.vars.memberpage)

        providerid = int(request.vars.providerid)
        
        provdict = common.getproviderfromid(db, providerid)
        providername = provdict["providername"]
       


        flag = common.getboolean(appt[0].blockappt)
        if(flag == True):
                redirect(URL('appointment', 'appointment_blockupdate', vars=dict(apptid=apptid,providerid=providerid,source=source)))


        title = common.getstring(appt[0].f_title)
        location = common.getstring(appt[0].f_location)
        cell = common.getstring(appt[0].cell)
        patientname = common.getstring(appt[0].f_patientname) 
        duration = int(common.getid(appt[0].f_duration))
        description = common.getstring(appt[0].description)

        patientid = int(common.getid(appt[0].patient))
        memberid  = int(common.getid(appt[0].patientmember))
        doctorid = int(common.getid(appt[0].doctor))
        treatmentid = int(common.getid(appt[0].f_treatmentid))


        #patient = <fname lanme>:<memberref>
        #xpatientmember = <fname lanme>:<memberref>
        patientmember = ""
        patient=""
        membername = ""
        fullname = ""
        status = ""

        rows = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select()
        if(len(rows) > 0):
                patientmember = common.getstring(rows[0].patientmember) #Patient/Member ID
                patient = common.getstring(rows[0].patient)  # fname + lname + : + patientmember
        else:
                fullname = patientname



        curraptdt = appt[0].f_start_time
        str2 = curraptdt.strftime('%d %B %Y - %H:%M')
        str3 = appt[0].f_end_time
        str4 = str3.strftime('%d %B %Y - %H:%M') 

        status = appt[0].f_status


        if(patientid > 0):

                form2 = SQLFORM.factory(
                        Field('patientmember', 'string',  label='Patient',default=patientname,requires=[IS_NOT_EMPTY()],writable=False),
                        Field('cell', 'string',  label='Cell',default=cell),
                        Field('treatment', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=treatmentid,label='Treatment List',\
                              requires=IS_EMPTY_OR(IS_IN_DB(db((db.vw_treatmentlist.providerid==providerid)&(db.vw_treatmentlist.patientid == patientid)&(db.vw_treatmentlist.is_active==True)), \
                                                            'vw_treatmentlist.id', '%(treatment)s : %(startdate)s'))),
                        Field('chiefcomplaint', 'text', default=title),
                        Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active==True)&(db.doctor.stafftype=='Doctor')), 'doctor.id', '%(name)s')),
                        Field('title', 'text',  label='Patient',default=title),
                        Field('location', 'string',  label='Clinic Location',default=location),
                        Field('status', 'string',  label='Status',default=status,requires = IS_IN_SET(APPTSTATUS)),            
                        Field('xpatientmember', 'string',  label='Patient',default=patient),
                        Field('xfullname', 'string',  label='Patient', default=fullname),
                        Field('xmemberid', 'string',  label='Patient',default=memberid),
                        Field('start_date', 'datetime',label='Start Date & Time',default=str2,requires=[IS_NOT_EMPTY()]),
                        Field('duration', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=duration, label='Doctor',requires=IS_IN_SET(['30','45','60'])),
                        Field('end_date', 'datetime',label='End Date & Time', default=str4,requires=[IS_NOT_EMPTY()]),
                        Field('description','text', label='Description', default=description)

                )
        else:
                form2 = SQLFORM.factory(
                        Field('patientmember', 'string',  label='Patient',default=patientname,requires=[IS_NOT_EMPTY()],writable=False),
                        Field('cell', 'string',  label='Cell',default=cell),
                        Field('treatment', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=treatmentid,label='Treatment List',\
                              requires=IS_EMPTY_OR(IS_IN_DB(db((db.vw_treatmentlist.providerid==providerid)&(db.vw_treatmentlist.patientid == patientid)&(db.vw_treatmentlist.is_active==True)), \
                                                            'vw_treatmentlist.id', '%(treatment)s : %(startdate)s'))),            Field('chiefcomplaint', 'text', default=title),
                        Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
                        Field('title', 'text',  label='Patient',default=title),
                        Field('location', 'string',  label='Clinic Location',default=location),
                        Field('status', 'string',  label='Status',default=status,requires = IS_IN_SET(APPTSTATUS)),
                        Field('xpatientmember', 'string',  label='Patient',default=patient),
                        Field('xfullname', 'string',  label='Patient', default=fullname),
                        Field('xmemberid', 'string',  label='Patient',default=memberid),
                        Field('start_date', 'datetime',label='Start Date & Time',default=str2,requires=[IS_NOT_EMPTY()]),
                        Field('duration', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=duration, label='Doctor',requires=IS_IN_SET(['15','30','45','60'])),
                        Field('end_date', 'datetime',label='End Date & Time', default=str4,requires=[IS_NOT_EMPTY()]),
                        Field('description','text', label='Description', default=description)

                )


        form2.element('textarea[name=description]')['_class'] = 'form-control'
        form2.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
        form2.element('textarea[name=description]')['_rows'] = 5

        form2.element('textarea[name=title]')['_class'] = 'form-control'
        form2.element('textarea[name=title]')['_style'] = 'height:100px;line-height:1.0;'
        form2.element('textarea[name=title]')['_rows'] = 5    
        form2.element('textarea[name=title]')['_placeholder'] = "Enter Title"

        form2.element('textarea[name=chiefcomplaint]')['_class'] = 'form-control'
        form2.element('textarea[name=chiefcomplaint]')['_style'] = 'height:100px;line-height:1.0;'
        form2.element('textarea[name=chiefcomplaint]')['_rows'] = 5    
        form2.element('textarea[name=chiefcomplaint]')['_placeholder'] = "Enter Complaint"

        #patientmember = form2.element('#no_table_patientmember')
        #patientmember['_class'] = 'form-control'
        #patientmember['_style'] = 'width:100%'
        #patientmember['_placeholder'] = 'Enter Patient Name or New Patient'   
        #patientmember['_autocomplete'] = 'off'   
        xcell = form2.element('#no_table_cell')
        xcell['_class'] = 'form-control'
        xcell['_style'] = 'width:100%'
        xcell['_placeholder'] = 'Enter Cell Number'   
        xcell['_autocomplete'] = 'off'   

        trmnt = form2.element('#no_table_treatment')
        trmnt['_class'] = 'form-control'
        trmnt['_style'] = 'width:100%'  


        loc = form2.element('#no_table_location')
        loc['_class'] = 'form-control'
        loc['_style'] = 'width:100%'
        loc['_placeholder'] = 'Enter clinic'   
        loc['_autocomplete'] = 'off'   

        dur = form2.element('#no_table_duration')
        dur['_class'] = 'form-control'
        dur['_style'] = 'width:100%'


        doc = form2.element('#no_table_doctor')
        doc['_class'] = 'form-control'
        doc['_style'] = 'width:100%'

        sts = form2.element('#no_table_status')
        sts['_class'] = 'form-control'
        sts['_style'] = 'width:100%'    



        xnew_start = form2.element('input',_id='no_table_start_date')
        xnew_start['_class'] =  'form-control form_datetime bs-datetime'


        xnew_end = form2.element('input',_id='no_table_end_date')
        xnew_end['_class'] =  'form-control form_datetime bs-datetime'


        returnurl = URL('appointment','customer_appointment',vars=dict(providerid=providerid,page=page))



        if form2.process(formname='form_two',keepvalues=True).accepted:


                page = common.getpage(request.vars.page)
                memberpage = common.getpage(request.vars.memberpage)

                apptid = int(common.getid(request.vars.apptid))

                newdescription = common.getstring(request.vars.description)
                cell = common.getstring(request.vars.cell)
                treatmentid = int(common.getid(request.vars.treatment))
                chiefcomplaint = common.getstring(request.vars.chiefcomplaint)  # this is stored in f_title field


                duration = int(common.getid(request.vars.duration))
                start_date = common.getnulldt(request.vars.start_date)
                apptdt = datetime.datetime.strptime(start_date, '%d %B %Y - %H:%M')
                endapptdt = apptdt + timedelta(minutes=duration)


                providerid = int(common.getid(request.vars.providerid))
                memberid = int(common.getid(request.vars.xmemberid))
                doctorid = int(common.getid(request.vars.doctor))

                #patient = <fname lanme>:<membercode>
                #xpatientmember = <fname lanme>:<membercode>
                rows = db(db.vw_memberpatientlist.patient == form2.vars.xpatientmember).select()

                if(len(rows) > 0):
                        memberid = int(common.getid(rows[0].primarypatientid))
                        patientid = int(common.getid(rows[0].patientid))
                else:
                        memberid = 0
                        patientid = 0




                db(db.t_appointment.id == apptid).update(f_title = chiefcomplaint, f_start_time = apptdt, f_end_time =  endapptdt, f_duration=duration,\
                                                         f_status=common.getstring(form2.vars.status),\
                                                         description = newdescription, cell = cell,  doctor=doctorid,f_treatmentid=treatmentid,\
                                                         modified_by = auth.user_id, modified_on=common.getISTFormatCurrentLocatTime())


                #save in case report

                if((patientid > 0) & ((title.strip().upper() != chiefcomplaint.strip().upper()) | (description.strip().upper() != newdescription.strip().upper() ))):

                        common.logapptnotes(db,chiefcomplaint,newdescription,apptid)
                        #csrdate = (request.now).strftime('%d/%m/%Y %H:%M:%S')
                        #csr = "Appointment CR:"  + csrdate + "\r\n" + form2.vars.title + "\r\n" + form2.vars.description 
                        #csrid = db.casereport.insert(appointmentid=apptid,memberid=memberid,patientid = patientid, providerid=providerid, doctorid=doctorid, casereport = csr, is_active=True,\
                                                                                #created_on = request.now, created_by = providerid, modified_on = request.now, modified_by = providerid)        

                # Send Confirmation SMS only when appt start date is changed
                # The confirmation sms will be sent from Superadmin Activity Tracker Group Message module
                # At this point we will send 
                retval=False
                if(apptdt != curraptdt):
                        db(db.t_appointment.id == apptid).update(sendsms = True, sendrem = True,smsaction="update")
                        session.flash = "Appointment updated! SMS confirmation will be sent to the patient and the doctor!"

                #return HTML(BODY(SCRIPT('window.close()'))).xml()        
                redirect(returnurl)

        elif form2.errors:
                session.flash = "Error updating appointment "  + str(form2.errors)
                redirect(returnurl)
                #return HTML(BODY(SCRIPT('window.close()'))).xml()        

        return dict(form2=form2,apptid = apptid, providerid=providerid, memberid=memberid, patientid=patientid, providername=providername,\
                    returnurl=returnurl,page=page,memberpage=memberpage,membername=patient,patientname=fullname,source=source)


def customer_prevnextappt():

        providerid = int(request.vars.providerid)
        provdict = common.getproviderfromid(db,providerid)
        prov = db(db.provider.id == providerid).select(db.provider.pa_practicename,db.provider.pa_practiceaddress)

        x = (datetime.datetime.today()).strftime("%d/%m/%Y %H:%M")
        xdt = datetime.datetime.strptime(x, "%d/%m/%Y %H:%M")

        if(request.vars.moment != None):
                y = (request.vars.moment).split("T")
                if(y[1] == "00:00:00 00:00"):
                        currdate = datetime.datetime.strptime(request.vars.moment, "%Y-%m-%dT%H:%M:%S 00:00")            
                else:
                        currdate = datetime.datetime.strptime(request.vars.moment, "%Y-%m-%dT%H:%M:%S")            
        else:
                currdate = xdt

        if(request.vars.defdate == None):
                defdate = (currdate).strftime('%Y-%m-%d %H:%M')
        else:
                if(secondsFormat(request.vars.defdate)):
                        currdate = datetime.datetime.strptime(request.vars.defdate, "%Y-%m-%d %H:%M:%S")        
                else:
                        currdate = datetime.datetime.strptime(request.vars.defdate, "%Y-%m-%d %H:%M")

                defdate = (currdate).strftime('%Y-%m-%d %H:%M')    

        defyear =(currdate).strftime('%Y')  #YYYY
        defmonth = (currdate).strftime('%m')  #mm

        defstart = datetime.datetime.strptime("01/" + str(defmonth)+"/"+str(defyear) + " 00:00:00", '%d/%m/%Y %H:%M:%S')   #start of def month
        defend   = datetime.date(defstart.year, defstart.month, calendar.monthrange(defstart.year, defstart.month)[-1])
        defend   = datetime.datetime.strptime( defend.strftime("%d") + "/" + str(defmonth)+"/"+str(defyear) + " 23:59:59", '%d/%m/%Y %H:%M:%S')   #end of def month (assuming 31 for all months)    


        start = "2100-01-01 00:00"
        end   = "2100-01-01 00:00"  

        #get all appointments for this provider and default month
        rows=db((db.t_appointment.provider==providerid) & (db.t_appointment.f_start_time>=defstart) &(db.t_appointment.f_start_time<=defend) &(db.t_appointment.is_active==True) ).\
                select(db.t_appointment.id,db.t_appointment.f_title,db.t_appointment.f_start_time,db.t_appointment.f_end_time,db.t_appointment.f_patientname,db.t_appointment.is_active, \
                       db.doctor.color, left=db.doctor.on(db.doctor.id == db.t_appointment.doctor))  

        dailyappts  = db((db.vw_appointment_today.providerid == providerid) & (db.vw_appointment_today.is_active == True)).select(orderby=db.vw_appointment_today.f_start_time)
        weeklyappts = db((db.vw_appointment_weekly.providerid == providerid) & (db.vw_appointment_weekly.is_active == True)).select(orderby=db.vw_appointment_weekly.f_start_time)
        monthlyappts = db((db.vw_appointment_monthly.providerid == providerid) & (db.vw_appointment_monthly.is_active == True)).select(orderby=db.vw_appointment_monthly.f_start_time)



        common.dashboard(db,session,providerid)
        memberid = 0
        patientid = 0   



        sqlquery = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True))

        form = SQLFORM.factory(
                Field('patientmember1', 'string',    label='Patient ID',requires=IS_NOT_EMPTY()),
                Field('xpatientmember1', 'string',   label='Member ID', default = ""),
                Field('xaction','string', label='', default='X')

        )

        xpatientmember = form.element('#no_table_patientmember1')
        #xpatientmember['_class'] = 'w3-input w3-border'
        xpatientmember['_class'] = 'form-control'
        xpatientmember['_placeholder'] = 'Enter Patient Information (first, Last, Cell, Email)' 
        xpatientmember['_autocomplete'] = 'off' 

        xpatientmember1 = form.element('#no_table_xpatientmember1')
        #xpatientmember['_class'] = 'w3-input w3-border'
        xpatientmember1['_class'] = 'form-control'

        xpatientmember1['_autocomplete'] = 'off' 


        doctorid = int(common.getdefaultdoctor(db, providerid))
        returnurl = URL('admin', 'providerhome')
        r = db(db.urlproperties.id >0).select()
        exturl = None
        if(len(r)>0):
                exturl = common.getstring(r[0].externalurl)





        if form.process().accepted:  
                xaction = form.vars.xaction
                xphrase1 = form.vars.xpatientmember1.strip()

                if(xaction == "searchPatient"):
                        processPatientLookup(providerid, xphrase1)
                elif(xaction == "newPatient"):
                        redirect(URL('member','new_nonmember',vars=dict(page=0,providerid=providerid,returnurl=URL('admin','providerhome'))))
                elif(xaction == "newTreatment"):
                        processNewTreatment(providerid, xphrase1)
                elif(xaction == "newPayment"):
                        processNewPayment(providerid, xphrase1)
                elif(xaction == "newImage"):
                        processNewImage(providerid,xphrase1)
                elif(xaction == "newReport"):
                        processNewReport(providerid, xphrase1)

        elif form.errors:
                #xpatientmember1 is empty
                xaction = form.vars.xaction
                if(xaction == "newPatient"):
                        redirect(URL('member','new_nonmember',vars=dict(page=0,providerid=providerid,returnurl=URL('admin','providerhome'))))        




        sql = "select doctor.name, doctor.color, IFNULL(appts.appointments,0) AS appointments,doctor.providerid,doctor.id as docid  from doctor left join "
        sql = sql + "(select vw_appointment_count.doctorid, vw_appointment_count.name, color, sum(appointments) as appointments, starttime from " 
        sql = sql + "vw_appointment_count where is_active = 'T' and providerid =" +  str(providerid)  + " and starttime >= '" + defstart.strftime('%Y-%m-%d') + "'  and starttime <= '" + defend.strftime('%Y-%m-%d') + "' group by name ) appts "
        sql = sql + " on doctor.id = appts.doctorid where doctor.stafftype <> 'Staff' and doctor.is_active = 'T' and doctor.providerid = " + str(providerid) + " ORDER BY appointments DESC" 

        docs = db.executesql(sql)   


        return dict(form=form,docs=docs,defdate=defdate,start=start,end=end,rows=rows,memberpage=1,page=1,\
                    dailyappts=dailyappts,monthlyappts=monthlyappts,weeklyappts=weeklyappts,providerid=providerid, providername= provdict["providername"] + " " + provdict["provider"],returnurl=returnurl,source='home',externalurl=exturl)


def customer_appointment():



        providerid = int(request.vars.providerid)
        provdict = common.getproviderfromid(db,providerid)
        if(providerid  < 0):
                raise HTTP(400,"PMS-Error: There is no valid logged-in Provider: providerhome()")    

        prov = db(db.provider.id == providerid).select(db.provider.pa_practicename,db.provider.pa_practiceaddress)

        

        if(request.vars.moment != None):
                y = (request.vars.moment).split("T")
                if(y[1] == "00:00:00 00:00"):
                        currdate = datetime.datetime.strptime(request.vars.moment, "%Y-%m-%dT%H:%M:%S 00:00")            
                else:
                        currdate = datetime.datetime.strptime(request.vars.moment, "%Y-%m-%dT%H:%M:%S")            
        else:
                currdate = datetime.datetime.strptime((datetime.datetime.today()).strftime("%d/%m/%Y %H:%M"), "%d/%m/%Y %H:%M")   


        if(request.vars.defdate == None):
                defdate = (currdate).strftime('%Y-%m-%d %H:%M')
        else:
                if(secondsFormat(request.vars.defdate)):
                        currdate = datetime.datetime.strptime(request.vars.defdate, "%Y-%m-%d %H:%M:%S")        
                else:
                        currdate = datetime.datetime.strptime(request.vars.defdate, "%Y-%m-%d %H:%M")        
                defdate = (currdate).strftime('%Y-%m-%d %H:%M')

        defyear =(currdate).strftime('%Y')  #YYYY
        defmonth = (currdate).strftime('%m')  #mm

        defstart = datetime.datetime.strptime("01/" + str(defmonth)+"/"+str(defyear) + " 00:00:00", '%d/%m/%Y %H:%M:%S')   #start of def month
        defend   = datetime.date(defstart.year, defstart.month, calendar.monthrange(defstart.year, defstart.month)[-1])
        defend   = datetime.datetime.strptime( defend.strftime("%d") + "/" + str(defmonth)+"/"+str(defyear) + " 23:59:59", '%d/%m/%Y %H:%M:%S')   #end of def month (assuming 31 for all months)    



        start = "2100-01-01 00:00"
        end   = "2100-01-01 00:00"  

        #get all appointments for this provider and default month
        rows=db((db.t_appointment.provider==providerid) & (db.t_appointment.f_start_time>=defstart) &(db.t_appointment.f_start_time<=defend) &(db.t_appointment.is_active==True) ).\
                select(db.t_appointment.id,db.t_appointment.f_title,db.t_appointment.f_start_time,db.t_appointment.f_end_time,db.t_appointment.f_patientname,db.t_appointment.blockappt,db.t_appointment.is_active, \
                       db.doctor.color, left=db.doctor.on(db.doctor.id == db.t_appointment.doctor))  



        dailyappts  = db((db.vw_appointment_today.providerid == providerid)  &(db.vw_appointment_today.is_active == True)).select(orderby=db.vw_appointment_today.f_start_time)
        weeklyappts = db((db.vw_appointment_weekly.providerid == providerid)  &(db.vw_appointment_weekly.is_active == True)).select(orderby=db.vw_appointment_weekly.f_start_time)
        monthlyappts = db((db.vw_appointment_monthly.providerid == providerid)  &(db.vw_appointment_monthly.is_active == True)).select(orderby=db.vw_appointment_monthly.f_start_time)



        common.dashboard(db,session,providerid)
        memberid = 0
        patientid = 0   



        sqlquery = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True))


        form = SQLFORM.factory(
                Field('patientmember1', 'string',    label='Patient ID',requires=IS_NOT_EMPTY()),
                Field('xpatientmember1', 'string',   label='Member ID', default = ""),
                Field('xaction','string', label='', default='X')

        )

        xpatientmember = form.element('#no_table_patientmember1')
        #xpatientmember['_class'] = 'w3-input w3-border'
        xpatientmember['_class'] = 'form-control'
        xpatientmember['_placeholder'] = 'Enter Patient Information (memberid, first, Last, Cell, Email)' 
        xpatientmember['_autocomplete'] = 'off' 

        xpatientmember1 = form.element('#no_table_xpatientmember1')
        #xpatientmember['_class'] = 'w3-input w3-border'
        xpatientmember1['_class'] = 'form-control'

        xpatientmember1['_autocomplete'] = 'off' 


        doctorid = int(common.getdefaultdoctor(db, providerid))




        returnurl = URL('admin', 'customer_appointment')


        r = db(db.urlproperties.id >0).select()
        exturl = None
        if(len(r)>0):
                exturl = common.getstring(r[0].externalurl)







        if form.process().accepted:  
                xaction = form.vars.xaction
                xphrase1 = form.vars.xpatientmember1.strip()

                if(xaction == "searchPatient"):
                        processPatientLookup(providerid, xphrase1)
                elif(xaction == "newPatient"):
                        redirect(URL('member','new_nonmember',vars=dict(page=0,providerid=providerid,returnurl=URL('admin','cutomer_appointment'))))
                elif(xaction == "newTreatment"):
                        processNewTreatment(providerid, xphrase1)
                elif(xaction == "newPayment"):
                        processNewPayment(providerid, xphrase1)
                elif(xaction == "newImage"):
                        processNewImage(providerid,xphrase1)
                elif(xaction == "newMedia"):
                        processNewMedia(providerid,xphrase1)
                elif(xaction == "newReport"):
                        processNewReport(providerid, xphrase1)

        elif form.errors:
                #xpatientmember1 is empty
                xaction = form.vars.xaction
                if(xaction == "newPatient"):
                        redirect(URL('member','new_nonmember',vars=dict(page=0,providerid=providerid,returnurl=URL('admin','providerhome'))))        




        start1 = defstart.strftime('%Y-%m-%d')
        end1 = defend.strftime('%Y-%m-%d')

        sql = "select doctor.name, doctor.color, IFNULL(appts.appointments,0) AS appointments,doctor.providerid,doctor.id as docid  from doctor left join "
        sql = sql + "(select vw_appointment_count.doctorid, vw_appointment_count.name, color, sum(appointments) as appointments, starttime from " 
        sql = sql + "vw_appointment_count where is_active = 'T' and providerid =" +  str(providerid)  + " and starttime >= '" + start1 + "'  and starttime <= '" + end1 + "' group by name ) appts "
        sql = sql + " on doctor.id = appts.doctorid where doctor.stafftype <> 'Staff' and doctor.is_active = 'T' and doctor.providerid = " + str(providerid) + " ORDER BY appointments DESC" 

        docs = db.executesql(sql)


        return dict(form=form,docs=docs,defdate=defdate,start=start,end=end,rows=rows,memberpage=1,page=1,\
                    dailyappts=dailyappts,monthlyappts=monthlyappts,weeklyappts=weeklyappts,providerid=provdict["providerid"], providername= provdict["providername"] + " " + provdict["provider"],returnurl=returnurl,source='home',externalurl=exturl)
