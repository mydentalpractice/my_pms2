# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from gluon import current
from gluon import current
from gluon.tools import Crud
crud = Crud(db)

#import sys
#sys.path.append('/my_pms2/modules')

from applications.my_pms2.modules import common
from applications.my_pms2.modules import mail
from applications.my_pms2.modules import cycle
from applications.my_pms2.modules import logger

from applications.my_pms2.modules import mdpuser

#from gluon.contrib import common
#from gluon.contrib import mail
from gluon.tools import Mail


import datetime
import time
import calendar
import socket


from datetime import timedelta


import pytz
from pytz import timezone

from decimal import Decimal
from string import Template

import os;
import uuid
from uuid import uuid4


getvar = lambda text: text if((text != None)&(text != "")) else "Unknown"
getvarurl = lambda text: text if((text != None)&(text != "")) else URL('admin','providerhome')



fmt = "%Y-%m-%d %H:%M:%S"



def download():
    return response.download(request, db)

def readme():
    
    
    return dict()

def isBlocked(startdt, enddt):
    
    retval = True
    str1 = datetime.datetime.strftime(startdt, "%Y-%m-%d %H:%M")
    str2 = datetime.datetime.strftime(enddt, "%Y-%m-%d %H:%M")
    
    
    
    appts = db(( str1 >= db.t_appointment.f_start_time)& (str1 <= db.t_appointment.f_end_time) & (db.t_appointment.blockappt == True) & (db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
    if(len(appts)>0):
        return True
    
    appts = db(( str1 >= db.t_appointment.f_end_time)&(db.t_appointment.blockappt == True)&(db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
    if(len(appts)>0):
        return False
    
    appts = db(( str1 <= db.t_appointment.f_start_time)&(str2 <= db.t_appointment.f_start_time)&(db.t_appointment.blockappt == True)&(db.t_appointment.is_active == True)).select(db.t_appointment.blockappt)
    if(len(appts)>0):
        return False
    
    
    return retval
    
    
def modify_cell(cell):

    cellno = cell
    if(cell.startswith("91") == False):
        cellno = "91" + cell
        
    return cellno

def sms_confirmation(appointmentid,action='create'):
    
    
    provcell = ""
    provname = ""
    doccell = ""
    docname = ""
    fname = ""
    lname = ""
    patcell = ""
    docemail = ""
    patemail = ""
    provemail = ""
    
    retVal1 = False
    retVal2 = False
    retVal3 = False
    
    appts = db(db.t_appointment.id == appointmentid).select()
    
    if(len(appts)>0):
        
        providerid = int(common.getid(appts[0].provider))
        doctorid = int(common.getid(appts[0].doctor))
        patientid = int(common.getid(appts[0].patient))
        memberid = int(common.getid(appts[0].patientmember))
        
        location = common.getstring(appts[0].f_location)
        
        provs = db(db.provider.id == providerid).select()
        if(len(provs)>0):
            provcell = common.modify_cell(common.getstring(provs[0].cell))
            provname = common.getstring(provs[0].providername)
            provtel = common.getstring(provs[0].telephone)
            provemail = common.getstring(provs[0].email)
                                         
        docs = db(db.doctor.id == doctorid).select()
        if(len(docs)>0):
            doccell = common.modify_cell(common.getstring(docs[0].cell))
            docname  = common.getstring(docs[0].name)
            docemail = common.getstring(docs[0].email)
            docsms = common.getboolean(docs[0].docsms)
            docemailflag = common.getboolean(docs[0].docemail)
        
        pats = db((db.vw_memberpatientlist.primarypatitentid == memberid) & ((db.vw_memberpatientlist.patitentid == patientid))).select()
        fname = common.getstring(appts[0].f_patientname)        
        patcell = common.modify_cell(common.getstring(appts[0].cell))
        patemail = ""
        if(len(pats)>0):
            patemail = pats[0].email
            if(patcell == ""):
                patcell = common.modify_cell(common.getstring(pats[0].cell))
                
        appPath = request.folder
        
        
            
        #f = open(smsfile,'rb')
        #temp = Template(f.read())
        #f.close()  
        #message = temp.template
        
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
        if(provtel != ""):
            patmessage = patmessage.replace("$clinicno", provtel)
        else:
            patmessage = patmessage.replace("$clinicno", "+" + doccell)
            
        
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
            
        if((doccell != "") & (docsms == True)): # send SMS to 
            retVal2 = mail.sendSMS2Email(db,doccell,docmessage)
         
        if((docemail != "") & (docemailflag == True)):  #send email to doc
            mail.groupEmail(db, docemail, ccs, "Appointment: " + apptdate, docmessage)  # send email to patient
        
        if(provcell != ""): # send SMS to 
            retVal2 = mail.sendSMS2Email(db,provcell,provmessage)
         
        if((provemail != "")):  #send email to provider
            mail.groupEmail(db, provemail, ccs, "Appointment: " + apptdate, provmessage)  # send email to patient

    return retVal1

def smsmessage():
    smstemplate = None
    if(request.vars.smstemplate == None):
        smstemplate = "SMS_Empty.txt"
    else:
        smstemplate = request.vars.smstemplate     
        
    appPath = request.folder
    smsfile = os.path.join(appPath,'templates/reminders/sms',smstemplate)
    f = open(smsfile,'rb')
    message = Template(f.read())
    f.close()    
    
    return dict(message=message.template)

def dashboard():
    
    provdict = common.getprovider(auth,db)

    
    return dict(providername= provdict["providername"] + " " + provdict["provider"])

def dashboard_new():
    
    provdict = common.getprovider(auth,db)

    
    return dict(providername= "ABC")


def dashboard_top():
    
    provdict = common.getprovider(auth,db)

    
    return dict(providername= "TOP")


def showerror():
    

    if(len(request.args)>0):
        errorheader = request.args[0]
        errormssg   = request.args[1]
        returnURL   = URL(request.args[3],request.args[4],request.args[5])
    else:
        errorheader = getvar(request.vars.errorheader)
        errormssg = getvar(request.vars.errormssg)
        returnURL = getvarurl(request.vars.returnURL)
        
    
    return dict(errorheader=errorheader,errormssg=errormssg,returnURL=returnURL,buttontext='Return')


def new_user(first_name, last_name, email, username, passw,key,registration_id): 
    
    providers = db((db.provider.sitekey==key)&(db.provider.email==email)).select()
    if(len(providers) >0):
        users = db((db.auth_user.email==email) & (db.auth_user.sitekey == key)).select()
        if users:
            my_crypt = CRYPT(key=auth.settings.hmac_key)
            crypt_pass = my_crypt(passw)[0]  
            db(db.auth_user.id == users[0].id).update(first_name=first_name,last_name=last_name,
                                                      username=username,password=crypt_pass)
            return dict(new=False, userid = users[0].id)
        else:
            my_crypt = CRYPT(key=auth.settings.hmac_key)
            crypt_pass = my_crypt(passw)[0]        
            id_user= db.auth_user.insert(
                                       first_name=first_name,
                                       last_name=last_name,
                                       email = email,
                                       sitekey = key,
                                       registration_id = registration_id,
                                       username = username,
                                       password = crypt_pass 
                                       )
            db.commit()
            return dict(new = True, userid = id_user)
    else:
        return 0
    
def register():
    
   
    
    key = ''
    
    key = common.getstring(request.vars.key)
    db.auth_user.sitekey.defaul = key
    if(len(key) > 0):
        xwritable = False
    else:
        xwritable = True
    
    
    
    prov = db(db.provider.sitekey == key).select()
    email = ""
    fname = ""
    lname = ""
    cell  = ""
    registration = ""
    if(len(prov) == 1):
        email = common.getstring(prov[0].email)
        cell = common.getstring(prov[0].cell)
        registration = common.getstring(prov[0].registration)
        fname = common.getstring(prov[0].providername)
        
                                        
    else:
        session.flash = "Registration Error. Invalid Key!. Please contact MyDentalPlan"
        redirect(URL('admin', 'register'))
       
    
    formregister = SQLFORM.factory(
            Field('email', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),label='Email',default=email,requires=[IS_EMAIL()]),
            Field('cell', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),default=cell,label='Cell',requires=""),
            Field('registration_id', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),label='Registration',default=registration,requires=[IS_NOT_EMPTY()]),
            Field('key', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),default=key, writable=xwritable, label='Key',requires=IS_NOT_EMPTY()),
            Field('fname', 'string',  widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),label='First Name',default=fname,requires=IS_NOT_EMPTY()),
            Field('lname', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'), label='Last Name',default=lname),
            Field('username', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'), label='User Name',requires=[IS_NOT_EMPTY(),IS_NOT_IN_DB(db,db.auth_user.username)]),
            Field('password', 'password',widget = lambda field, value:SQLFORM.widgets.password.widget(field, value,_class='form-control'),  label='Password',requires=[IS_NOT_EMPTY(),CRYPT(key=auth.settings.hmac_key)]),
            Field('confirm', 'password', widget = lambda field, value:SQLFORM.widgets.password.widget(field, value,_class='form-control'), label='Confirm', requires=IS_EXPR('value==%s' % repr(request.vars.get('password', None)),
             error_message='passwords do not match')),             
        )    
    

        
    submit = formregister.element('input',_type='submit')
    submit['_style'] = 'display:none;'    
    
    xpassword = formregister.element('input',_id='no_table_password')
    xpassword['_type'] = 'password'
    xpassword['_class'] = 'form-control'
    xpassword['_style'] = 'width:100%'
    xpassword['_placeholder'] = 'Create your password'
    xpassword['_autocomplete'] = 'off'
    
    xconfirm = formregister.element('input',_id='no_table_confirm')
    xconfirm['_type'] = 'password'
    xconfirm['_class'] = 'form-control'
    xconfirm['_style'] = 'width:100%'
    xconfirm['_placeholder'] = 'Confirm your password'
    xconfirm['_autocomplete'] = 'off'
  
    xemail = formregister.element('input',_id='no_table_email')
    xemail['_class'] = 'form-control'
    xemail['_style'] = 'width:100%'
    xemail['_placeholder'] = 'Enter your email'
    xemail['_autocomplete'] = 'off'
    
    xcell = formregister.element('input',_id='no_table_cell')
    xcell['_class'] = 'form-control'
    xcell['_style'] = 'width:100%'
    xcell['_placeholder'] = 'Enter your Cell or Telephone number'
    xcell['_autocomplete'] = 'off'
    
    
    xreg = formregister.element('input',_id='no_table_registration_id')
    xreg['_class'] = 'form-control'
    xreg['_style'] = 'width:100%'
    xreg['_placeholder'] = 'Enter your Registration Number'
    xreg['_autocomplete'] = 'off'

    xkey = formregister.element('input',_id='no_table_key')
    if(xkey != None):
        xkey['_class'] = 'form-control'
        xkey['_style'] = 'width:100%'
        xkey['_placeholder'] = 'Enter Provider Key'
        xkey['_autocomplete'] = 'off'

    xfname = formregister.element('input',_id='no_table_fname')
    xfname['_class'] = 'form-control'
    xfname['_style'] = 'width:100%'
    xfname['_placeholder'] = 'Enter your First Name'
    xfname['_autocomplete'] = 'off'

    xlname = formregister.element('input',_id='no_table_lname')
    xlname['_class'] = 'form-control'
    xlname['_style'] = 'width:100%'
    xlname['_placeholder'] = 'Enter your Last Name'
    xlname['_autocomplete'] = 'off'

    xuname = formregister.element('input',_id='no_table_username')
    xuname['_class'] = 'form-control'
    xuname['_style'] = 'width:100%'
    xuname['_placeholder'] = 'Enter your Username'
    xuname['_autocomplete'] = 'off'


    if formregister.process().accepted:
        userdict = new_user(request.vars.fname,request.vars.lname,request.vars.email,request.vars.username,request.vars.password,request.vars.key,request.vars.registration_id)
        user_id = common.getid(userdict["userid"])
        new = common.getboolean(userdict["new"])
        
        if(user_id <= 0):
            response.flash = "Registration Error! You may have entered a different email than the email that My Dental Plan has in their system. Please enter the correct email or call MyDentalPlan for help!"
            session.flash = "Registration Error! You may have entered a different email than the email that My Dental Plan has in their system. Please enter the correct email or call MyDentalPlan for help!"
            redirect(URL('admin', 'register'))
            
        
        # Setting Group Membership
        group_id = auth.id_group(role="provider")

        if(group_id == 0):
            group_id = auth.add_group('provider', 'Provider User')
        elif(group_id > 0):
            auth.add_membership(group_id, user_id)
        elif(group_id < 0):
            response.flash = "Registration Error! You may have entered a different email than the email that My Dental Plan has in their system. Please enter the correct email or call MyDentalPlan for help!"
            session.flash = "Registration Error! You may have entered a different email than the email that My Dental Plan has in their system. Please enter the correct email or call MyDentalPlan for help!"
            redirect(URL('admin', 'register'))
        
        #db.person.update_or_insert(db.person.name=='John',
        #2 name='John',birthplace='Chicago')  
        db.commit()
        rows = db((db.provider.sitekey ==request.vars.key) & (db.provider.is_active == True)).select()
        if(len(rows)==1):
            providerid = int(common.getid(rows[0].id))
        else:
            providerid = 0
        
        #update provider's Registration
        db(db.provider.id == providerid).update(registration = request.vars.registration_id, email=request.vars.email,registered=True)
        
        if(new == True):
            #copy default Roles, Speciality and Medicines for this provider
            sql = "insert into role(role,providerid, is_active, created_by, created_on, modified_by, modified_on)"
            sql = sql + " select role," +  str(providerid) + ", 'T'," +  str(providerid) + ", NOW()," +  str(providerid) + ", NOW() from role_default"
            db.executesql(sql)    
            db.commit()
             
            sql = "insert into speciality(speciality,providerid, is_active, created_by, created_on, modified_by, modified_on)"
            sql = sql + " select speciality," +  str(providerid) + ", 'T'," +  str(providerid) + ", NOW()," +  str(providerid) + ", NOW() from speciality_default"
            db.executesql(sql)    
            db.commit()
            
            sql = "insert into medicine(providerid,medicine,medicinetype, strength,strengthuom, instructions,   is_active, created_by, created_on, modified_by, modified_on)"
            sql = sql + " select " + str(providerid) + ", medicine , meditype , strength , strngthuom ,instructions, 'T'," +  str(providerid) + ", NOW()," + str(providerid) + ", NOW() from medicine_default"
            db.executesql(sql)    
            db.commit()
            
        
        
            #Add role = 'Doctor_Owner' and 'General Dentist' in Speciality
            roles = db((db.role.providerid == providerid) & (db.role.role == "Chief Consultant")).select()
            if(len(roles)==0):
                roleid = db.role.insert(role='Chief Dentist', providerid = providerid, is_active = True, \
                                        created_by = providerid, modified_by = providerid, created_on = request.now,modified_on = request.now)
            else:
                roleid = int(common.getid(roles[0].id))
                
            spcs = db((db.speciality.providerid == providerid) & (db.speciality.speciality == "General Dentist")).select()
            if(len(spcs)==0):
                specialityid = db.speciality.insert(speciality='General Dentist', providerid = providerid, is_active = True, \
                                        created_by = providerid, modified_by = providerid, created_on = request.now,modified_on = request.now)
            else:
                specialityid = int(common.getid(spcs[0].id))
                
            
            
        
            name = common.getstring(request.vars.fname) + " " + common.getstring(request.vars.lname)
            email = common.getstring(request.vars.email)
            cell = common.getstring(request.vars.cell)
            registration = common.getstring(request.vars.registration_id)
          
            db.doctor.insert(name = name, providerid = providerid, speciality=specialityid, role = roleid, email=email,cell=cell,registration=registration,stafftype='Doctor',\
                             color="#ff0000",practice_owner=True,is_active = True, created_on = request.now, created_by = providerid, modified_on=request.now, modified_by = providerid)      
        
        response.flash = "You have been registered successfully! After login, please visit your profile to change default settings!"
        redirect(URL('admin','login'))
        
    elif formregister.errors:
        response.flash = 'Error in registration. ' + str(formregister.errors)
    
    return dict(formregister=formregister)


def loginblock(login, username):
    
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    
    loctime = common.getISTFormatCurrentLocatTime()
    
    r = db((db.loginblock.username == username) |(db.loginblock.ip_address == ip_address)).select()
    
    if(len(r) == 0):
        attempts = 0
        lastlogin = loctime
    elif (len(r) == 1):
        attempts = int(r[0].attempts)
        lastlogin = r[0].lastlogin
    else:
        attempts = 5
        lastlogin = loctime
    
    time15 = lastlogin + timedelta(minutes=15)
    
    if(login == True):
        if(attempts < 5):
            #delete the attempt record from DB
            db(db.loginblock.username == username).delete()
            return dict(login=True, error_mssg = "")
        else:
            if(loctime > time15):
                db(db.loginblock.username == username).delete()
                return dict(login=True, error_mssg = "")
            else:    
                return dict(login = False, error_mssg = "You have reached login attempts limit. Please contact MDP Support or try after 15 minutes")
           
    else:
        if(attempts >= 5):
            return dict(login = False, error_mssg = "You have reached login attempts limit. Please contact MDP Support")

        
        db.loginblock.update_or_insert(((db.loginblock.username==username) | (db.loginblock.ip_address==ip_address)),
                                      ip_address=ip_address, username = username,attempts = attempts + 1, lastlogin = loctime)
        
        return dict(login = True, error_mssg = "Number of attempts = " + str(attempts+1) + " out of 5")

    return dict(login = True, error_mssg = "")



    
    

def login():
    
    session.religare = False
    form = SQLFORM.factory(
                Field('username', 'string',  label='User Name',requires=[IS_NOT_EMPTY(), IS_IN_DB(db,'auth_user.username','%(registration_id)s')]),
                Field('password', 'password',  label='Password',requires=[IS_NOT_EMPTY(),CRYPT(key=auth.settings.hmac_key)])
        )
    
    xusername = form.element('input',_id='no_table_username')
    xusername['_class'] =  'form-control'
    xusername['_placeholder'] =  'Username'
    xusername['_autocomplete'] =  'off'
    xusername['_pattern'] = "[a-zA-Z0-9-_.]+"
    
    xpassword = form.element('input',_id='no_table_password')
    xpassword['_class'] =  'form-control'
    xpassword['_placeholder'] =  'Password'
    xpassword['_autocomplete'] =  'off'
    xpassword['_pattern'] = "[a-zA-Z0-9-_.!@#$%^&*]+"


    
    if form.process().accepted:
        logger.loggerpms2.info("MyDentalPlan Login ==>>" + common.getstring(form.vars.username) + " " + common.getstring(form.vars.password.password))
        
           

        user = auth.login_bare(form.vars.username, form.vars.password.password)
        
        #logger.loggerpms2.info("Auth User Username + Sitekey = " + common.getstring(auth.user.username) + " " + common.getstring(auth.user.sitekey))
        
        if(user==False):
            session.flash = "Login Error! Please try again!"
            ologinblock = loginblock(False, form.vars.username)
            if(ologinblock["login"] == False):
                error_mssg = ologinblock["error_mssg"]
            else:
                error_mssg = "There was a login error. Please try again!\n" + ologinblock["error_mssg"]
            redirect(URL('admin','showerror', vars=dict(errorheader="Login Error", errormssg=error_mssg, returnURL=URL('admin','login'))))
        else:
                         
            ologinblock = loginblock(True,form.vars.username)
            
            if(common.getboolean(ologinblock["login"]) == False):
                redirect(URL('admin','showerror', vars=dict(errorheader="Login Error", errormssg=ologinblock["error_mssg"], returnURL=URL('admin','login'))))
                
            
            auth.user.impersonated = False
            auth.user.impersonatorid = 0        
            
            auth.settings.login_url = URL('admin','login')
            logmssg = ""
            provdict = common.getprovider(auth, db)
            session.religare = common.getboolean(provdict["rlgprovider"])
            if(int(provdict["providerid"]) == 0):
                logmssg = 'Login Success - SuperAdmin Access'
                db.loghistory.insert(username = form.vars.username, logerror = logmssg, logstatus = True,\
                                                        created_on=common.getISTFormatCurrentLocatTime(), created_by=1,modified_on=common.getISTFormatCurrentLocatTime(),modified_by=1
                                                        )                   
                redirect(URL('superadmin','superadmin'))
         
            else:
                logmssg = 'Login Success'
                db.loghistory.insert(username = form.vars.username, logerror = logmssg, logstatus = True,\
                                                        created_on=common.getISTFormatCurrentLocatTime(), created_by=1,modified_on=common.getISTFormatCurrentLocatTime(),modified_by=1
                                                        )                   
                
                redirect(URL('admin','providerhome'))
                #redirect(URL('admin','select_clinic'))
    elif form.errors:
        logmssg = "Login Error " + str(form.errors)
        db.loghistory.insert(username = "", logerror = logmssg, logstatus = False,\
                                         created_on=common.getISTFormatCurrentLocatTime(), created_by=1,modified_on=common.getISTFormatCurrentLocatTime(),modified_by=1
                                         )        
        response.flash = "Login Error " + str(form.errors)
         
        
            
    return dict(form = form)




def reset_password():
    user = db.auth_user
    if request.vars.key:
        key = request.vars.key
        users = db(user.reset_password_key == key).select()
        if not users:
            session.flash='Invalid password reset'
            redirect(URL('admin','login')) 

            
        form = SQLFORM.factory(
                    #Field('password', 'password',  label='Enter New Password',requires=[IS_NOT_EMPTY()])
                    Field('password', 'password',  label='Enter New Password',requires=[IS_NOT_EMPTY(),CRYPT(key=auth.settings.hmac_key)])
            )
        
        xpassword = form.element('input',_id='no_table_password')
        xpassword['_class'] =  'form-control placeholder-no-fix'
        xpassword['_placeholder'] =  'Enter new password'
        xpassword['_autocomplete'] =  'off'
        xpassword['_pattern'] = "[a-zA-Z0-9-_.!@#$%^&*]+"
        
   

        if form.accepts(request,session):
            key= request.vars.key if request.vars.key else _error()
            password= request.vars.password if request.vars.password else _error()
            users = db(user.reset_password_key == key).select()
            if not users:
                session.flash='Invalid password reset'
                redirect(URL('admin','login'))  
            users[0].update_record(password=CRYPT(key=auth.settings.hmac_key)(str(password))[0],reset_password_key='')
            session.flash='Password Reset Successful'
            redirect(URL('admin','login')) 

    return dict(form=form)
    


def select_clinic():

    formheader = "New Agent"
    username = ""
    returnurl = URL('admin','login')

    provdict = common.getprovider(auth,db)
    providerid = int(provdict["providerid"])
    if(providerid  < 0):
        raise HTTP(400,"PMS-Error: There is no valid logged-in Provider: providerhome()")    


    #primary clinicid of this provider
    c = db((db.vw_clinic.is_active == True) & (db.vw_clinic.ref_code == 'PRV') & (db.vw_clinic.ref_id == providerid) & (db.vw_clinic.primary_clinic == True)).select()
    clinicid = int(common.getid(c[0].id)) if(len(c) == 1) else 0
    clinics = db((db.vw_clinic.ref_code == 'PRV') & (db.vw_clinic.ref_id == providerid) & (db.vw_clinic.is_active == True ))
    
    form = SQLFORM.factory(
        Field('clinic', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='form-control'),
              label='Please Select your clinic',default=clinicid, requires=IS_IN_DB(clinics, 'vw_clinic.id',"%(name)s"))
        

    )

    #xclinic = form.element('input',_id='no_table_clinic')
    #xclinic['_class'] =  'form-control'
    #xclinic['_placeholder'] =  'Select Clinic'
    #xclinic['_autocomplete'] =  'off'

    clinic = None
    if form.process().accepted:
        clinicid = form.vars.clinic
        d=db((db.clinic.id == clinicid)&(db.clinic.is_active == True)).select()
        clinicname= common.getstring(d[0].name) if (len(d)==1) else ""
        session.clinicid = clinicid
        session.clinicname = clinicname
        redirect(URL('admin','providerhome', vars=dict(clinicid=clinicid,clinicname=clinicname))) 

    return dict(form=form,returnurl = returnurl,clinic=clinic) 

def request_username():
    email = request.vars.usernameemail
    ret = mail.emailUsername(db, request, email)
    mssg = ret['mssg']
    retVal = ret['retVal']
    returnurl = URL('admin', 'login')
    return dict(mssg = mssg, retVal = retVal, returnurl = returnurl,email=email)

def request_resetpassword():
    
    username = request.vars.username
    reset_password_key=str(int(time.time()))+'-'+str(uuid.uuid4())
    
    ret = mail.emailResetPasswordLink(db, request, username,reset_password_key)
    mssg = ret['mssg']
    retVal = ret['retVal']
    returnurl = URL('admin', 'login')
    return dict(mssg = mssg, retVal = retVal, returnurl = returnurl,username=username)  



def xrequest_resetpassword():
    props = db(db.urlproperties.id>0).select()
    siteurl = props[0].pms_ipaddress + ":" + props[0].pms_port + "/" + props[0].pms_application
    server = props[0].mailserver + ":"  + props[0].mailserverport
    sender = props[0].mailsender
    login  = props[0].mailusername + ":" + props[0].mailpassword
    port = int(props[0].mailserverport)
    if((port != 25) & (port != 26)):
        tls = True
    else:
        tls = False

    if((props[0].mailusername == 'None')):
        login = None

    mail = auth.settings.mailer
    mail.settings.server = server
    mail.settings.sender = sender
    mail.settings.login =  login
    mail.settings.tls = tls

    auth.settings.reset_password_next = URL( 'login')
    auth.settings.request_reset_password_next = URL('login')
    auth.messages.reset_password ='Please click this link ' + siteurl+ '/admin/reset_password'+ '?key='+'%(key)s to reset your password' 
    
    form = auth.request_reset_password()
    
    username = ""
    xusername = form.element('input',_id='auth_user_username')
    xusername['_class'] =  'form-control placeholder-no-fix'
    xusername['_placeholder'] =  'Username'
    xusername['_autocomplete'] =  'off'
    xusername['_value'] =  username
     
    
    return dict(form=form)

@auth.requires_login()
def logout():
    """ Logout handler """
    
    auth.settings.logout_next = URL('admin','login')
   
    auth.logout()
    return dict()

@auth.requires_login()    
def memberlookup():
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    formheader = "Member Lookup"    
    #form = SQLFORM.factory(
           #Field('patientmember', 'string',  label='Member ID',requires=[IS_NOT_EMPTY(),IS_IN_DB(db, 'patientmember.patientmember')])
    #)
    
    sqlquery = db(((db.patientmember.provider == providerid)&\
                  (db.patientmember.hmopatientmember == True)&\
                  (datetime.date.today().strftime('%Y-%m-%d') <= db.patientmember.premenddt)&\
                  (db.patientmember.is_active == True)) | \
                  ((db.patientmember.provider == providerid) & \
                  (db.patientmember.hmopatientmember == False) & \
                  (db.patientmember.is_active  == True)))
                  
    form = SQLFORM.factory(
           Field('patientmember', 'string',  label='Member ID',requires=[IS_NOT_EMPTY(),IS_IN_DB(sqlquery,'patientmember.patientmember')])
    )
       
    patientmember = form.element('#no_table_patientmember')
    patientmember['_class'] = 'form-control'
    patientmember['_placeholder'] = 'Enter Member ID'

    if form.process().accepted:  
        redirect(URL('member','list_members',vars=dict(page=0, providerid = providerid, member=request.vars.patientmember)))
    elif form.errors:
        member = db((db.patientmember.patientmember == form.vars.patientmember) & \
                    (db.patientmember.provider==providerid)).select()
        
        if(len(member) == 0):
            form.errors.patientmember = T('Member not present')
        elif (member[0]["is_active"] == False):
            form.errors.patientmember = T('Member is inactive')
        elif ((member[0]["hmopatientmember"]==True)&(datetime.date.today() > member[0]["premenddt"])):
            form.errors.patientmember = T("Member's insurance policy has expired")
        else:
            form.errors.patientmember = T("Invalid Member")
            
        
    returnurl = URL('admin','providerhome')
    return dict(form=form,ormheader=formheader,returnurl=returnurl)    
    
def patient_hide():
    return ''


def provider_selector():
    
    if(request.vars.xprovider == ""):
        pattern = '%'
    else:
        pattern = request.vars.xprovider.capitalize() + '%'
        
    selected = [row.provider for row in db((db.vw_provider.id >0) & (db.vw_provider.is_active == True) & (db.vw_provider.provider.like(pattern))).select()]
    return ''.join([DIV(k,
                 _onclick="jQuery('#no_table_provider').val('%s')" % k,
                 _onmouseover="this.style.backgroundColor='cyan'",
                 _onmouseout="this.style.backgroundColor='white'",
                 _style="z-index:500000;width:100%;font-family:verdana;font-size:12px;color:black;font-weight:normal"                 
                 
                 ).xml() for k in selected])

def member_selector():
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])    
 
    if(request.vars.xpatientmember1 == ""):
        pattern = '%'
    else:
        if(request.vars.xpatientmember1.isdigit()):
            pattern = request.vars.xpatientmember1.capitalize() + '%'
        else:
            pattern = '%' + request.vars.xpatientmember1.capitalize() + '%'
    
    selected = ""
    if(request.vars.xpatientmember1.isdigit()):
        selected = [row.patient for row in db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.hmopatientmember == True) & (db.vw_memberpatientlist.is_active == True) & (db.vw_memberpatientlist.cell.like(pattern))).select()]
    else:
        selected = [row.patient for row in db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.hmopatientmember == True) & (db.vw_memberpatientlist.is_active == True) & (db.vw_memberpatientlist.pattern.like(pattern))).select()]
    
    
    
    return ''.join([DIV(k,
                 _onclick="jQuery('#no_table_patientmember1').val('%s')" % k,
                 _onmouseover="this.style.backgroundColor='cyan'",
                 _onmouseout="this.style.backgroundColor='white'",
                 _style="z-index:500000;width:100%;font-family:verdana;font-size:12px;color:black;font-weight:normal"                 
                 
                 ).xml() for k in selected])

def nonmember_selector():
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])    
    
    
    if(request.vars.xpatientmember1 == ""):
        pattern = '%'
    else:
        if(request.vars.xpatientmember1.isdigit()):
            pattern = request.vars.xpatientmember1.capitalize() + '%'
        else:
            pattern = '%' + request.vars.xpatientmember1.capitalize() + '%'
    
    selected = ""
    if(request.vars.xpatientmember1.isdigit()):
        selected = [row.patient for row in db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.hmopatientmember == False) & (db.vw_memberpatientlist.is_active == True) & (db.vw_memberpatientlist.cell.like(pattern))).select()]
    else:
        selected = [row.patient for row in db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.hmopatientmember == False) & (db.vw_memberpatientlist.is_active == True) & (db.vw_memberpatientlist.pattern.like(pattern))).select()]
        

    return ''.join([DIV(k,
                 _onclick="jQuery('#no_table_patientmember1').val('%s')" % k,
                 _onmouseover="this.style.backgroundColor='cyan'",
                 _onmouseout="this.style.backgroundColor='white'",
                 _style="z-index:500000;width:100%;font-family:verdana;font-size:12px;color:black;font-weight:normal"                 
                 
                 ).xml() for k in selected])


def patient_selector():
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])    
    
    
    if(request.vars.xpatientmember1 == ""):
        pattern = '%'
    else:
        if(request.vars.xpatientmember1.isdigit()):
            pattern = request.vars.xpatientmember1.capitalize() + '%'
        else:
            pattern = '%' + request.vars.xpatientmember1.capitalize() + '%'
    
    selected = ""
    if(request.vars.xpatientmember1.isdigit()):
        selected = [row.patient for row in db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True) & (db.vw_memberpatientlist.cell.like(pattern))).select()]
    else:
        selected = [row.patient for row in db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True) & (db.vw_memberpatientlist.pattern.like(pattern))).select()]
    
           
        
        
    return ''.join([DIV(k,
                 _onclick="jQuery('#no_table_patientmember1').val('%s')" % k,
                 _onmouseover="this.style.backgroundColor='cyan'",
                 _onmouseout="this.style.backgroundColor='white'",
                 _style="z-index:500000;width:100%;font-family:verdana;font-size:12px;color:black;font-weight:normal"                 
                 
                 ).xml() for k in selected])


def treatment_selector():
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])    
    
    
    if(request.vars.xpattreatment1 == ""):
        pattern = '%'
    else:
        pattern = '%' + request.vars.xpattreatment1.capitalize() + '%'
    
    selected = ""
    selected = [row.pattreatment for row in db((db.vw_treatmentlist.providerid == providerid) & (db.vw_treatmentlist.is_active == True) & (db.vw_treatmentlist.pattern.like(pattern))).select()]
    
        
        
    return ''.join([DIV(k,
                 _onclick="jQuery('#no_table_pattreatment1').val('%s')" % k,
                 _onmouseover="this.style.backgroundColor='cyan'",
                 _onmouseout="this.style.backgroundColor='white'",
                 _style="z-index:500000;width:100%;font-family:verdana;font-size:12px;color:black;font-weight:normal"                 
                 
                 ).xml() for k in selected])




def newpatient_selector():
    
    if not request.vars.patientmember:
            return ''    

    providerid = int(common.getid(request.vars.providerid))
    xmemberid = int(common.getid(request.vars.xmemberid))
    
   
    if(request.vars.patientmember == ""):
        pattern = '%'
    else:
        pattern = request.vars.patientmember.capitalize() + '%'
        
    if(xmemberid == 0):
        selected = [row.patient for row in db(((db.vw_appointmentmemberlist.is_active == True)  & \
                                               ((db.vw_appointmentmemberlist.providerid == providerid) | ((db.vw_appointmentmemberlist.providerid == 1)&\
                                                                                                          (db.vw_appointmentmemberlist.hmopatientmember == False))))&\
                                              (db.vw_appointmentmemberlist.patient.like(pattern))).select(db.vw_appointmentmemberlist.patient)]
    else:
        selected = [row.patient for row in db(((db.vw_appointmentmemberlist.is_active == True)  & (db.vw_appointmentmemberlist.primarypatientid == xmemberid)  & \
                                               ((db.vw_appointmentmemberlist.providerid == providerid) | ((db.vw_appointmentmemberlist.providerid == 1)&\
                                                                                                          (db.vw_appointmentmemberlist.hmopatientmember == False))))&\
                                              (db.vw_appointmentmemberlist.patient.like(pattern))).select(db.vw_appointmentmemberlist.patient)]
        
    return ''.join([DIV(k,
                 _onclick="jQuery('#no_table_patientmember').text('%s')" % k,
                 _onmouseover="this.style.backgroundColor='cyan'",
                 _onmouseout="this.style.backgroundColor='white'",
                 _style="z-index:500000;width:100%;font-family:verdana;font-size:12px;color:black;font-weight:normal"                 
                 ).xml() for k in selected])

def vwdentalprocedurecode_selector():
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])    
   
    freetreatment = common.getboolean(request.vars.freetreatment)
    newmember = common.getboolean(request.vars.newmember)
    
    patientid = int(common.getid(request.vars.patientid))
    memberid  = int(common.getid(request.vars.memberid))
    
    rows = db((db.vw_memberpatientlist.patientid == patientid)&(db.vw_memberpatientlist.primarypatientid == memberid)).select()
    procedurepriceplancode = 'PREM103'
    if(len(rows)>0):
        procedurepriceplancode = rows[0].hmoplan.procedurepriceplancode
    if(request.vars.vwdentalprocedurecode == ""):
        pattern = '%'
    else:
        pattern = request.vars.vwdentalprocedurecode.capitalize() + '%'
    
    if((freetreatment == True) | (newmember == False)):
        selected = [row.longprocedurecode for row in db((db.vw_procedurepriceplan.is_active == True)  &  \
                                                       (db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode) & \
                                                       (db.vw_procedurepriceplan.longprocedurecode.like(pattern))).select()]
    else:
        selected = [row.longprocedurecode for row in db((db.vw_procedurepriceplan_x999.is_active == True)  &  \
                                                       (db.vw_procedurepriceplan_x999.procedurepriceplancode == procedurepriceplancode) & \
                                                       (db.vw_procedurepriceplan_x999.longprocedurecode.like(pattern))).select()]
        
        
    return ''.join([DIV(k,
                 _onclick="jQuery('#no_table_vwdentalprocedurecode').val('%s')" % k,
                 _onmouseover="this.style.backgroundColor='cyan'",
                 _onmouseout="this.style.backgroundColor='white'",
                 _style="z-index:500000;width:100%;font-family:verdana;font-size:12px;color:black;font-weight:normal"                 
                 ).xml() for k in selected])



def vwdentalprocedure_selector():
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])    
    
    freetreatment = common.getboolean(request.vars.freetreatment)
    newmember = common.getboolean(request.vars.newmember)
    
    patientid = int(common.getid(request.vars.patientid))
    memberid  = int(common.getid(request.vars.memberid))
    
    rows = db((db.vw_memberpatientlist.patientid == patientid)&(db.vw_memberpatientlist.primarypatientid == memberid)).select()
    procedurepriceplancode = 'PREM103'
    if(len(rows)>0):
        procedurepriceplancode = rows[0].hmoplan.procedurepriceplancode
    if(request.vars.vwdentalprocedure == ""):
        pattern = '%'
    else:
        pattern = '%' + request.vars.vwdentalprocedure.capitalize() + '%'
    
    
    
    
    if((freetreatment == True) | (newmember == False)):
        selected = [row.shortdescription for row in db((db.vw_procedurepriceplan.is_active == True)  &  \
                                                       (db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode) & \
                                                       (db.vw_procedurepriceplan.shortdescription.like(pattern))).select(db.vw_procedurepriceplan.shortdescription)]
    else:
        selected = [row.shortdescription for row in db((db.vw_procedurepriceplan_x999.is_active == True)  &  \
                                                       (db.vw_procedurepriceplan_x999.procedurepriceplancode == procedurepriceplancode) & \
                                                       (db.vw_procedurepriceplan_x999.shortdescription.like(pattern))).select(db.vw_procedurepriceplan_x999.shortdescription)]
        
    return ''.join([DIV(k,
                 _onclick="jQuery('#no_table_vwdentalprocedure').val('%s')" % k,
                 _onmouseover="this.style.backgroundColor='cyan'",
                 _onmouseout="this.style.backgroundColor='white'",
                _style="z-index:500000;width:100%;font-family:verdana;font-size:12px;color:black;font-weight:normal"
                 ).xml() for k in selected])

    



def dentalprocedure_selector():
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])    
    if not request.vars.dentalprocedure:
        return ''
    if(len(request.vars.dentalprocedure) < 3):
        return ''
    
    pattern = '%' + request.vars.dentalprocedure.capitalize() + '%'
    selected = [row.shortdescription for row in db((db.dentalprocedure.is_active == True) & (db.dentalprocedure.shortdescription.like(pattern))).select()]
    return ''.join([DIV(k,
                 _onclick="jQuery('#no_table_dentalprocedure').val('%s')" % k,
                 _onmouseover="this.style.backgroundColor='cyan'",
                 _onmouseout="this.style.backgroundColor='white'",
                 _style="z-index:500000;width:100%;font-family:verdana;font-size:12px;color:black;font-weight:normal"                 
                 ).xml() for k in selected])



    
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
    title = common.getstring(appt[0].f_title)
    startdate = (appt[0].f_start_time).strftime('%d %B %Y - %H:%M')
    header = common.getstring(appt[0].f_patientname)
     
    page = common.getpage(request.vars.page)          
    memberpage = common.getpage(request.vars.memberpage)          
    returnurl = URL('admin', 'providerhome', vars=dict(page=1, memberpage=0, providerid=providerid,source=source))
    
    form = FORM.confirm('Yes?',{'No':returnurl})

    if form.accepted:
        db((db.t_appointment.id == apptid)).update(is_active=False,f_status='Cancelled', modified_by = auth.user_id, modified_on=request.now)
        
        # Send Confirmation SMS
        retval=False
        retval = sms_confirmation(apptid,'delete')
        
        if(retval == True):
            session.flash = "Appointment Deletion! SMS confirmation sent to the patient!"
        else:
            session.flash = "Appointment Deleted! No SMS confirmation sent to the patient!"

        
        redirect(returnurl)

    return dict(form=form,returnurl=returnurl,providerid=providerid,providername=providername,page=page,memberpage=memberpage,header=header,startdate=startdate,source=source)



def appointment_drop():
    
    uniqueid = int(common.getid(request.vars.xuniqueid))
    title = request.vars.xtitle
    start = request.vars.xstart
    end = request.vars.xend
    duration = 0
    appts = db(db.t_appointment.id == uniqueid).select()
    
    if(len(appts)>0):
        apptid = int(common.getid(appts[0].id))
        if(common.getstring(appts[0].f_duration) == ""):
            duration = (appts[0].f_end_time-appts[0].f_start_time).seconds/60
           
        
        start = datetime.datetime(*time.strptime(start, "%Y-%m-%dT%H:%M:%S")[:6])
        if(end != ""):
            end = datetime.datetime(*time.strptime(end, "%Y-%m-%dT%H:%M:%S")[:6])
            duration = (end-start).seconds/60
        else:
            end = start + timedelta(minutes=duration) 
        
        if(isBlocked(start,end) == False):
            db(db.t_appointment.id == apptid).update(f_start_time = start, f_end_time=end,f_duration=duration,modified_on=datetime.datetime.today())
            retval =sms_confirmation(apptid,"update")
            if(retval==True):
                response.flash = "Appointment SMS & Email confirmation sent successfully!"
            else:
                response.flash = "Error in sending Appointment SMS confirmation!"
        else:
            response.flash = "New Appointment date and time is blocked!"
            
        returnurl = URL("admin","providerhome")
        redirect(returnurl)
    
    else:
        session.flash = "Error updating dropped appointment" 
        
    return dict()

def appointment_update():
   
    
    apptid = int(common.getid(request.vars.apptid1))
    appt = db(db.t_appointment.id == apptid).select()  
    curraptdt = appt[0].f_start_time
    currnotes = common.getstring(appt[0].description)
    currcomplaint = common.getstring(appt[0].f_title)
    
    status = common.getstring(request.vars.status1)
    title = common.getstring(request.vars.title1)
    description = common.getstring(request.vars.description1)
    cell = common.getstring(request.vars.cell1)
    treatmentid = int(common.getid(request.vars.treatments1))
    
    
    duration = int(common.getid(request.vars.duration1))
    newapptdt = common.getnulldt(request.vars.start_date1)
    apptdt = datetime.datetime.strptime(newapptdt, '%d %B %Y - %H:%M')
    endapptdt = apptdt + timedelta(minutes=duration)

    
    providerid = int(common.getid(request.vars.providerid1))
    memberid = int(common.getid(request.vars.memberid1))
    patientid = int(common.getid(request.vars.patientid1))
    doctorid = int(common.getid(request.vars.doctors1))
    
    
    
   
   
    
    db(db.t_appointment.id == apptid).update(f_title = title, f_start_time = apptdt, f_end_time =  endapptdt, f_duration=duration,f_status=status,\
                                             description = description, cell = cell,  doctor=doctorid,f_treatmentid=treatmentid,sendsms = True,\
                                             modified_by = auth.user_id, modified_on=request.now)
    
    
    
  
    if((currnotes.strip().upper() != description.strip().upper()) | (currcomplaint.strip().upper() != currcomplaint.strip().upper())):
        common.logapptnotes(db,title, description,apptid)
     
    # Send Confirmation SMS
    retval=False
    if(curraptdt !=apptdt ):
        retval = sms_confirmation(apptid,"update")
    
    if(retval == True):
        session.flash = "Appointment updated! SMS confirmation sent to the patient!"
    else:
        session.flash = "Appointment updated!"

    returnurl = URL("admin","providerhome")
    redirect(returnurl)


#treatment can be "" or treatment or treatment phrase
#this function will return a grid fulfilling the query
def getpatientgrid(page,providerid, providername, phrase):
    
    query = (db.vw_treatmentlist.memberid == memberid) if(memberid > 0) else (1==1)
    
    query = query & (db.vw_treatmentlist.patientid == patientid) if(memberid > 0) else (1==1)

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


# this is called when 'Patient Lookup is called from the dashboard
# xphrase = ""
#xphrase  = <fn lan>:<memberid>
#xphrase   = <fn ln>
#xphrase  = <phrase>

def processPatientLookup(providerid, xphrase):
    xphrase1 = xphrase.strip()  #remove all leading trailing blanks
    patientid = 0
    memberid = 0
    hmopatientmember = True
    patientmember = ""
    
    r = db((db.vw_memberpatientlist.patient.like("%" + xphrase1 + "%")) & \
           (db.vw_memberpatientlist.providerid == providerid) & \
           (db.vw_memberpatientlist.is_active == True)).select()
    
    if(len(r)==1):  #exact patietn match
        member = common.getstring(r[0].patientmember)  #BLR...
        memberid = int(common.getid(r[0].primarypatientid))
        patientid = int(common.getid(r[0].patientid))
        hmopatientmember = common.getboolean(r[0].hmopatientmember)
        if(hmopatientmember == True):
            redirect(URL('member','list_patients',vars=dict(page=1, providerid = providerid, member=member,memberid=memberid,patientid=patientid)))
        else:
            redirect(URL('member','list_nonmembers',vars=dict(page=1, providerid = providerid, member=member,memberid=memberid,patientid=patientid)))
    else: # no exact match = Prompt Error
        #redirect(URL('member','list_allpatients',vars=dict(page=1, providerid = providerid, member=member,memberid=memberid,patientid=patientid,phrase=xphrase1)))
        response.flash = "Please select the patient from the drop down list of suggested patients"
    return
    
def processNewTreatment(providerid, xphrase):
    xphrase1 = xphrase.strip()  #remove all leading trailing blanks
    patientid = 0
    memberid = 0
    
    r = db((db.vw_memberpatientlist.patient.like("%" + xphrase1 + "%")) & \
           (db.vw_memberpatientlist.providerid == providerid) & \
           (db.vw_memberpatientlist.is_active == True)).select()
    
    if(len(r)==1):  #exact patietn match
        memberid = int(common.getid(r[0].primarypatientid))
        patientid = int(common.getid(r[0].patientid))
        
        redirect(URL('treatment','new_treatment',vars=dict(page=1,providerid=providerid,memberid=memberid,patientid=patientid,treatmentid=0,tplanid=0)))
        
    else: # no exact match = Prompt Error
        response.flash = "Error: Invalid Patient"
        
    return

def processNewAppointment(providerid):
    redirect(URL('appointment','new_appointment',vars=dict(proivderid=providerid)))
    return dict()
    
    
def processNewPayment(providerid, xphrase):
    xphrase1 = xphrase.strip()  #remove all leading trailing blanks
    patientid = 0
    memberid = 0
    fullname = ""
    
    r = db((db.vw_memberpatientlist.patient.like("%" + xphrase1 + "%")) & \
           (db.vw_memberpatientlist.providerid == providerid) & \
           (db.vw_memberpatientlist.is_active == True)).select()
    
    if(len(r)==1):  #exact patietn match
        memberid = int(common.getid(r[0].primarypatientid))
        patientid = int(common.getid(r[0].patientid))
        fullname = common.getstring(r[0].fullname)
        
        
        
        redirect(URL('payment','list_payment',vars=dict(page=1,fullname=fullname)))
        
    else: # no exact match = Prompt Error
       
        response.flash = "Error: Invalid Patient"
    return
   
def processNewImage(providerid, xphrase):
    xphrase1 = xphrase.strip()  #remove all leading trailing blanks
    patientid = 0
    memberid = 0
    
    patientmember = ""
    patient = ""
    
    r = db((db.vw_memberpatientlist.patient.like("%" + xphrase1 + "%")) & \
           (db.vw_memberpatientlist.providerid == providerid) & \
           (db.vw_memberpatientlist.is_active == True)).select()
    
    if(len(r)==1):  #exact patietn match
        memberid = int(common.getid(r[0].primarypatientid))
        patientid = int(common.getid(r[0].patientid))
        fullname = common.getstring(r[0].fullname)
        patientmember = common.getstring(r[0].patientmember)
        patient = common.getstring(r[0].patient)
        
        
        redirect(URL('dentalimage','dentalimage_new',vars=dict(memberpage=1,imagepage=1,page=1,memberref=patientmember,patientid=patientid,\
                                                               patient=patient,memberid=memberid,providerid=providerid)))

 
def processNewMedia(providerid, xphrase):
    xphrase1 = xphrase.strip()  #remove all leading trailing blanks
    patientid = 0
    memberid = 0
    
    patientmember = ""
    patient = ""
    
    r = db((db.vw_memberpatientlist.patient.like("%" + xphrase1 + "%")) & \
           (db.vw_memberpatientlist.providerid == providerid) & \
           (db.vw_memberpatientlist.is_active == True)).select()
    
    if(len(r)==1):  #exact patietn match
        memberid = int(common.getid(r[0].primarypatientid))
        patientid = int(common.getid(r[0].patientid))
        fullname = common.getstring(r[0].fullname)
        patientmember = common.getstring(r[0].patientmember)
        patient = common.getstring(r[0].patient)
        
        
        redirect(URL('media','list_media',vars=dict(page=1,patientid=patientid,\
                                                               memberid=memberid,providerid=providerid)))
        
    else: # no exact match = Prompt Error
       
        response.flash = "Error: Invalid Patient"
    return
   
def processNewReport(providerid, xphrase):
    xphrase1 = xphrase.strip()  #remove all leading trailing blanks
    patientid = 0
    memberid = 0
    
    patientmember = ""
    patient = ""
    
    provdict = common.getproviderfromid(db, providerid)

    
    r = db((db.vw_memberpatientlist.patient.like("%" + xphrase1 + "%")) & \
           (db.vw_memberpatientlist.providerid == providerid) & \
           (db.vw_memberpatientlist.is_active == True)).select()
    
    if(len(r)==1):  #exact patietn match
        memberid = int(common.getid(r[0].primarypatientid))
        patientid = int(common.getid(r[0].patientid))
        fullname = common.getstring(r[0].fullname)
        patientmember = common.getstring(r[0].patientmember)
        patient = common.getstring(r[0].patient)
        
        redirect(URL('reports','membertreatmentplansreport',vars=dict(memberid=memberid,patientid=patientid,\
                                                                      providerid=providerid,providername=provdict["providername"],page=1)))
        
    else: # no exact match = Prompt Error
       
        response.flash = "Error: Invalid Patient"
    return

def secondsFormat(datestr):
    
    

    #assuming format is in %Y-%m-%d  %H:%M:%S   or %d/%m/%Y %H:%M:%S
    r = datestr.split(':')
    retval = True if(len(r)>2) else False
        
    return retval

@auth.requires_login()    
def providerhome():
  
    provdict = common.getprovider(auth,db)
    providerid = int(provdict["providerid"])
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
    xpatientmember['_placeholder'] = 'Enter Patient Information (memberid, first, Last, Cell, Email)' 
    xpatientmember['_autocomplete'] = 'off' 
    
    xpatientmember1 = form.element('#no_table_xpatientmember1')
    #xpatientmember['_class'] = 'w3-input w3-border'
    xpatientmember1['_class'] = 'form-control'
   
    xpatientmember1['_autocomplete'] = 'off' 
    
    
    doctorid = int(common.getdefaultdoctor(db, providerid))
    
    
    #form2 = SQLFORM.factory(
                #Field('patientmember', 'string',  label='Patient',default='',requires=[IS_NOT_EMPTY()]),
                #Field('cell', 'string',  label='Cell',default=""),
                #Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
                #Field('title', 'text',  label='Patient',default=""),
                #Field('location', 'string',  label='Clinic Location',default=common.getstring(prov[0].pa_practicename) + ", " + common.getstring(prov[0].pa_practiceaddress)),
                #Field('xpatientmember', 'string',  label='Patient',default=''),
                #Field('xfullname', 'string',  label='Patient', default=''),
                #Field('xmemberid', 'string',  label='Patient',default=''),
                #Field('day', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=curday, label='Day',requires=IS_IN_SET(cycle.DAY)),
                #Field('month', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=curmnth, label='Month',requires=IS_IN_SET(cycle.MONTH)),
                #Field('year', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=curyr, label='Monht',requires=IS_IN_SET(cycle.YEAR)),
                #Field('hour', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=curhr, label='Hour',requires=IS_IN_SET(cycle.HOUR)),
                #Field('mins', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default='00', label='Min',requires=IS_IN_SET(cycle.MINS)),
                #Field('ampm', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=curampm, label='AM/PM',requires=IS_IN_SET(cycle.AMPM)),
                ##Field('start_date', 'datetime',label='Start Date & Time',requires=[IS_NOT_EMPTY(), IS_DATETIME(format=T('%d %B %Y - %H:%M'))]),
                #Field('start_date', 'datetime',label='Start Date & Time'),
                #Field('duration', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default='30', label='Doctor',requires=IS_IN_SET(['30','45','60'])),
                #Field('end_date', 'datetime',label='End Date & Time',default=request.now,requires=[IS_NOT_EMPTY(), IS_DATETIME(format=T('%d %B %Y - %H:%M'))]),
                #Field('description','text', label='Description', default='')
                
                
                #)
      
    #form2.element('textarea[name=description]')['_class'] = 'form-control'
    #form2.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    #form2.element('textarea[name=description]')['_rows'] = 5
    
    #form2.element('textarea[name=title]')['_class'] = 'form-control'
    #form2.element('textarea[name=title]')['_style'] = 'height:100px;line-height:1.0;'
    #form2.element('textarea[name=title]')['_rows'] = 5    

    
    ##title = form2.element('#no_table_title')
    ##title['_class'] = 'form-control'
    ##title['_style'] = 'width:100%'
    ##title['_placeholder'] = 'Enter Complaint'   
    ##title['_autocomplete'] = 'off'   
    
    
    #xcell = form2.element('#no_table_cell')
    #xcell['_class'] = 'form-control'
    #xcell['_style'] = 'width:100%'
    #xcell['_placeholder'] = 'Enter Cell Number'   
    #xcell['_autocomplete'] = 'off'   
    
    #loc = form2.element('#no_table_location')
    #loc['_class'] = 'form-control'
    #loc['_style'] = 'width:100%'
    #loc['_placeholder'] = 'Enter office location'   
    #loc['_autocomplete'] = 'off'   
    
    #patientmember = form2.element('#no_table_patientmember')
    #patientmember['_class'] = 'form-control'
    #patientmember['_style'] = 'width:100%'
    #patientmember['_placeholder'] = 'Enter Patient Name or New Patient'   
    #patientmember['_autocomplete'] = 'off'   
    
    #doc = form2.element('#no_table_doctor')
    #doc['_class'] = 'form-control'
    #doc['_style'] = 'width:100%'


    #day = form2.element('#no_table_day')
    #day['_class'] = 'form-control'
    #day['_style'] = 'width:100%'

    #mnth = form2.element('#no_table_month')
    #mnth['_class'] = 'form-control'
    #mnth['_style'] = 'width:100%'

    #yr = form2.element('#no_table_year')
    #yr['_class'] = 'form-control'
    #yr['_style'] = 'width:100%'

    #hr = form2.element('#no_table_hour')
    #hr['_class'] = 'form-control'
    #hr['_style'] = 'width:100%'

    #mn = form2.element('#no_table_mins')
    #mn['_class'] = 'form-control'
    #mn['_style'] = 'width:100%'

    #ampm = form2.element('#no_table_ampm')
    #ampm['_class'] = 'form-control'
    #ampm['_style'] = 'width:100%'
    
    #dur = form2.element('#no_table_duration')
    #dur['_class'] = 'form-control'
    #dur['_style'] = 'width:100%'
    
    #xnew_start = form2.element('input',_id='no_table_start_date')
    #xnew_start['_class'] =  'input-group date form_datetime form_datetime bs-datetime'
    
    #xnew_end = form2.element('input',_id='no_table_end_date')
    #xnew_end['_class'] =  'input-group date form_datetime form_datetime bs-datetime'
    
    
    returnurl = URL('admin', 'providerhome')
     

    r = db(db.urlproperties.id >0).select()
    exturl = None
    if(len(r)>0):
        exturl = common.getstring(r[0].externalurl)
     
     
      



    #if form2.process(formname='form_two').accepted:
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
        #if((request.vars.chiefcomplaint == None) | (request.vars.chiefcomplaint == "")):
            #treatmentid = 0
        #else:
            #treatmentid = int(common.getid(request.vars.chiefcomplaint))
        
        ## find out day of the appt.
        #duration = int(common.getid(form2.vars.duration))
        
        #day = common.getstring(form2.vars.day)
        #mnth = common.getstring(form2.vars.month)
        #yr = common.getstring(form2.vars.year)
        #hr = common.getstring(form2.vars.hour)
        #mins = common.getstring(form2.vars.mins)
        #ampm = common.getstring(form2.vars.ampm)
        #apptdt = datetime.datetime.strptime(day + "/" + mnth + '/' + yr + " " + hr + ":" + mins + " "+ ampm, "%d/%B/%Y %I:%M %p")
        ##apptdt = common.getnulldt(form2.vars.start_date)
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
            ##retval = True
            
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
   
    #trtmnts = db((db.vw_treatmentlist.providerid==providerid)&(db.vw_treatmentlist.is_active==True)).select()
    #returnurl = URL('admin','providerhome')
    return dict(form=form,docs=docs,defdate=defdate,start=start,end=end,rows=rows,memberpage=1,page=1,\
                dailyappts=dailyappts,monthlyappts=monthlyappts,weeklyappts=weeklyappts,providerid=provdict["providerid"], providername= provdict["providername"] + " " + provdict["provider"],returnurl=returnurl,source='home',externalurl=exturl)




def customer_appointment():
  
    provdict = common.getprovider(auth,db)
    providerid = int(provdict["providerid"])
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