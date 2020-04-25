# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']




import datetime
import time
import calendar
from datetime import timedelta
from decimal import Decimal
from string import Template
import os;

#import sys
#sys.path.append('modules')
from applications.my_pms2.modules import common
from applications.my_pms2.modules import mail
from applications.my_pms2.modules import tasks

from applications.my_pms2.modules import logger

#from gluon.contrib import common
#from gluon.contrib import mail
#from gluon.contrib import tasks


def testmsg91():
    
    cellnos = "9137908350,9916314080"
    mssg = "Test MSG91 SMS"
    
    r = mail.sendSMS_MSG91(db,cellnos,mssg)
    
    return r
def groupsmsmessage():
    
    logger.loggerpms2.info("Enter GroupSMSMessage")
    
    tasks.sendNewAptGrpSMS();
    
    return True


def smsmessage():
    
    smstemplate = request.vars.smstemplate
    
    smstemplate = None
    if(request.vars.smstemplate == None):
        smstemplate = "SMS_Empty.txt"
    else:
        smstemplate = request.vars.smstemplate    
    
    appPath = request.folder
    smsfile = os.path.join(appPath, 'templates/birthdays/sms',smstemplate)
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
    emailfile = os.path.join(appPath, 'templates/birthdays/email',emailtemplate)
    f = open(emailfile,'rb')
    message = Template(f.read())
    f.close()    
    
    return dict(message=message.template)

def fromDOB(currentdate, dobperiod):
    newDate = currentdate - timedelta(days=dobperiod)
   
    
    return newDate
    
def toDOB(currentdate, dobperiod):
    
    newDate = currentdate + timedelta(days=dobperiod)
    return newDate

def isDOBInRange(dob, currentdate):
    
    retVal = False
    
    myFromDOB = fromDOB(currentdate, 30)
    myToDOB    = toDOB(currentdate, 60)
    
    currDOB = datetime.date(currentdate.year,dob.month,dob.day)
    
    if((currDOB >= myFromDOB) & (currDOB <= myToDOB)):
        retVal = True
    
    
    return retVal
    
@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def email_multiple():
    ids = request.vars.ids
    page = common.getgridpage(request.vars)
    providerid = int(common.getid(request.vars.providerid))    
    
    redirect(URL('utility', 'send_email', vars=dict(page=page, providerid=providerid, mode='multiple',ids=ids)))
    return dict()

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def send_email():
    emails = ""
    
    formheader = "Email Message"
    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getproviderfromid(db, request.vars.providerid)
    
    page=common.getgridpage(request.vars)
    

    ids = common.getstring(request.vars.ids)
    if(ids == 'None'):
        ids = None
    
    mode=common.getstring(request.vars.mode)
    if((ids != None) & (ids != "")):
        if(mode=='single'):
            uid = int(common.getid(request.vars.ids))
            pat = db((db.patientmember.id == uid) & (db.patientmember.is_active == True)).select(db.patientmember.email)
            if(len(pat)>0):
                email = common.getstring(pat[0].email)    
            else:
                email = ""
                
            if(email != ""):
                emails = emails + email + ";"
        else:    
            for uid in ids:
                pat = db((db.patientmember.id == uid) & (db.patientmember.is_active == True)).select(db.patientmember.email)
                if(len(pat)>0):
                    email = common.getstring(pat[0].email)    
                else:
                    email = ""
                if(email != ""):
                    emails = emails + email + ";"

    if((emails != None) & (emails != "")):
        emails = emails.rstrip(';')
    
    formA = SQLFORM.factory(Field('to','string',label='To:',default=emails),
                            Field('cc','string',label='Cc:'),    
                            Field('subject','string',label='Subject'),
                            Field('message','text', label='Message'))
    
    formA.element('textarea[name=message]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=message]')['_rows'] = 5
    formA.element('textarea[name=message]')['_cols'] = 70
    formA.element('textarea[name=message]')['_class'] = 'form-control'
   
    xto = formA.element('input',_id='no_table_to')
    xto['_class'] =  'form-control'
    xto['_autocomplete'] = 'off'  
    
    xcc = formA.element('input',_id='no_table_cc')
    xcc['_class'] =  'form-control'
    xcc['_autocomplete'] = 'off'  

    xsbj = formA.element('input',_id='no_table_subject')
    xsbj['_class'] =  'form-control'
    xsbj['_autocomplete'] = 'off'  
    
    retVal = None
    
    if formA.accepts(request,session,keepvalues=True):
        retVal = mail.groupEmail(db,formA.vars.to,formA.vars.cc, formA.vars.subject,formA.vars.message)
    
    returnurl = URL('utility','list_memberpatient', vars=dict(page=page,providerid=providerid,notification="Email"))
    return dict(returnurl=returnurl, formA=formA,formheader=formheader,page=page, retVal = retVal,providername = provdict["providername"], providerid=providerid)





@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def birthday_email_multiple():
    ids = request.vars.ids
    page = common.getgridpage(request.vars)
    providerid = int(common.getid(request.vars.providerid))
    start = request.vars.start
    end=request.vars.end
    notification = request.vars.notification
    
    
    redirect(URL('utility', 'send_birthday_email', vars=dict(page=page, providerid=providerid, mode='multiple',ids=ids,start=start,end=end,notification=notification)))
    return dict()

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def birthday_sms_multiple():
    ids = request.vars.ids
    page = common.getgridpage(request.vars)
    providerid = int(common.getid(request.vars.providerid))
    start = request.vars.start
    end=request.vars.end
    notification = request.vars.notification    

    
    redirect(URL('utility', 'send_birthday_sms', vars=dict(page=page, providerid=providerid, mode='multiple',ids=ids,start=start,end=end,notification=notification)))
    return dict()


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def send_birthday_email():

   
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
    formheader = "Birthday Reminder Email Text - From:" + start + " To:" + end
    mode = common.getstring(request.vars.mode)
    
    if((ids != None) & (ids != "")):
        if(mode=='single'):
            uid = int(common.getid(request.vars.ids))
            
            pat = db((db.patientmember.id == uid) & (db.patientmember.is_active == True)).select(db.patientmember.email)
            if(len(pat)>0):
                email = common.getstring(pat[0].email)    
            else:
                email = ""
                
            if(email != ""):
                emails = emails + email + ";"
        else:    
            for uid in ids:
                pat = db((db.patientmember.id == uid) & (db.patientmember.is_active == True)).select(db.patientmember.email)
                if(len(pat)>0):
                    email = common.getstring(pat[0].email)    
                else:
                    email = ""
                if(email != ""):
                    emails = emails + email + ";"

    if((emails != None) & (emails != "")):
        emails = emails.rstrip(';')
    
    files = os.listdir(os.path.join(request.folder, 'templates/birthdays/email'))
    options=[emailfile for emailfile in files] 
    
    formA = SQLFORM.factory(Field('emailtemplate','list:string',label='Email Template',requires=IS_IN_SET(options)),
                            Field('to','string',label='To:',default=emails)
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
        messsage = request.vars.message
        for i in xrange(len(emailarr)):
            
            emailstr = emailarr[i]
            if((emailstr == "") | (emailstr == None)):
                continue;
            
            pat = db(db.patientmember.email == emailstr).select(\
                db.patientmember.fname, db.patientmember.lname, db.provider.providername, db.provider.cell, db.provider.email,\
                left=db.provider.on(db.provider.id==db.patientmember.provider))
                
            ccs=""
            subject = "Happy Birthday"
            if(len(pat) >= 1):
                message = request.vars.message
                message = message.replace("$fname", pat[0]["patientmember.fname"])
                message = message.replace("$lname", pat[0]["patientmember.lname"])
                message = message.replace("$providername", pat[0]["provider.providername"])
                message = message.replace("$cell", pat[0]["provider.cell"])
                message = message.replace("$email", pat[0]["provider.email"])
                retVal = mail.groupEmail(db, emailstr, ccs, subject, message)

        
        
    
    returnurl = URL('utility','list_birthday_reminders',vars=dict(providerid=providerid, providername=provdict["providername"],\
                                                                                             page=page,start=start,end=end,\
                                                                                             notification=request.vars.notification))
    message = ""
    return dict(returnurl=returnurl, formA=formA,formheader=formheader,page=page, retVal = retVal,providername = provdict["providername"], providerid=provdict["providerid"],emailfiles=files,message=message)
    
@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def send_birthday_sms():

    
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
    formheader = "Birthday Reminder SMS Text - From:" + start + " To:" + end
    mode = common.getstring(request.vars.mode)
    
    if((ids != None)&(ids != "")):
        if(mode == 'single'):
            uid = int(common.getid(request.vars.ids))
            pat = db((db.patientmember.id == uid) & (db.patientmember.is_active == True)).select(db.patientmember.cell)
            if(len(pat)>0):
                cellno = common.getstring(pat[0].cell) 
            else:
                cellno = ""
                
            if(cellno != ""):
                if(cellno.startswith("91") == True):
                    cellnos = cellnos + cellno
                else:
                    cellnos = cellnos + "91" + cellno
        else:
            for uid in ids:
                pat = db((db.patientmember.id == uid) & (db.patientmember.is_active == True)).select(db.patientmember.cell)
                if(len(pat)>0):
                    cellno = common.getstring(pat[0].cell)
                else:
                    cellno = ""
                    
                if(cellno != ""):
                    if(cellno.startswith("91") == True):
                        cellnos = cellnos + cellno + ","
                    else:
                        cellnos = cellnos + "91" + cellno + ","            

    if((cellnos != None)&(cellnos != "")):
        cellnos = cellnos.rstrip(',')

    username = auth.user.first_name + ' ' + auth.user.last_name
       
    files = os.listdir(os.path.join(request.folder, 'templates/birthdays/sms'))
    options=[smsfile for smsfile in files] 
    
    formA = SQLFORM.factory(Field('smstemplate','list:string',label='SMS Template',requires=IS_IN_SET(options)),
                            Field('to','string',label='To:',default=cellnos)
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
        messsage = request.vars.message
        for i in xrange(len(cellarr)):
            
            cellstr = ""
            if len(cellarr[i])>2 :
                cellstr = cellarr[i].replace("91","",1)
            if((cellstr=="")|(cellstr==None)):
                continue;
            pat = db(db.vw_memberpatientlist.cell == cellstr).select(\
                db.vw_memberpatientlist.fname, db.vw_memberpatientlist.lname, db.provider.providername, db.provider.cell, db.provider.email,\
                left=db.provider.on(db.provider.id==db.vw_memberpatientlist.providerid))
                
                
            if(len(pat) >= 1):
                message = request.vars.message
                message = message.replace("$fname", pat[0]["vw_memberpatientlist.fname"])
                message = message.replace("$lname", pat[0]["vw_memberpatientlist.lname"])
                message = message.replace("$providername", pat[0]["provider.providername"])
                message = message.replace("$cell", pat[0]["provider.cell"])
                message = message.replace("$email", pat[0]["provider.email"])
                retVal = mail.sendSMS2Email(db,cellarr[i],message)
                
        
        
    returnurl = URL('utility','list_birthday_reminders',vars=dict(providerid=providerid, providername=provdict["providername"],\
                                                                                             page=page,start=start,end=end,\
                                                                                             notification=request.vars.notification))
    

    message = ""
    return dict(returnurl=returnurl, formA=formA,formheader=formheader,page=page, retVal = retVal,providername = provdict["providername"], providerid=provdict["providerid"],smsfiles=files,message=message)
    



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def sms_multiple():
    ids = request.vars.ids
    page = common.getgridpage(request.vars)
    providerid = int(common.getid(request.vars.providerid))
    
    redirect(URL('utility', 'send_sms', vars=dict(page=page, providerid=providerid, mode='multiple',ids=ids)))
    return dict()



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def send_sms():

   
    formheader = "SMS Text"
    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getproviderfromid(db, providerid)
    
    page=common.getgridpage(request.vars)
    ids = common.getstring(request.vars.ids)
    if(ids == 'None'):
        ids = None
    cellnos = ""
    
    mode = common.getstring(request.vars.mode)
    if((ids != None) & (ids != "")):
        if(mode == 'single'):
            uid = int(common.getid(request.vars.ids))
            pat = db((db.patientmember.id == uid) & (db.patientmember.is_active == True)).select(db.patientmember.cell)
            if(len(pat)>0):
                cellno = common.getstring(pat[0].cell)    
            else:
                cellno = ""
                
            if(cellno != ""):
                if(cellno.startswith("91") == True):
                    cellnos = cellnos + cellno
                else:
                    cellnos = cellnos + "91" + cellno
        else:
            for uid in ids:
                pat = db((db.patientmember.id == uid) & (db.patientmember.is_active == True)).select(db.patientmember.cell)
                if(len(pat)>0):
                    cellno = common.getstring(pat[0].cell)    
                else:
                    cellno = ""
                if(cellno != ""):
                    if(cellno.startswith("91") == True):
                        cellnos = cellnos + cellno + ","
                    else:
                        cellnos = cellnos + "91" + cellno + ","            
   
    if((cellnos != None) & (cellnos != "")):
        cellnos = cellnos.rstrip(',')
    
    formA = SQLFORM.factory(Field('to','string',label='To:',default=cellnos),
                            Field('description','text', label='Message'))
    
    formA.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=description]')['_rows'] = 5
    formA.element('textarea[name=description]')['_cols'] = 70
    formA.element('textarea[name=description]')['_class'] = 'form-control'   
   
    xto = formA.element('input',_id='no_table_to')
    xto['_class'] =  'form-control'
    xto['_autocomplete'] = 'off' 
    
  
    retVal = None
    if formA.accepts(request,session,keepvalues=True):
        retVal = mail.sendSMS2Email(db,formA.vars.to,formA.vars.description)
    
    returnurl = URL('utility','list_memberpatient', vars=dict(page=page,providerid=providerid,notification="SMS"))
    return dict( returnurl=returnurl, formA=formA,formheader=formheader,page=page, retVal = retVal,providername = provdict["providername"], providerid=provdict["providerid"])
    




@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_memberpatient():


    formheader = "Member/Patient  List"
   
    page = common.getpage(request.vars.page)
    
    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getproviderfromid(db, request.vars.providerid)
  
    fields=(db.patientmember.fname,db.patientmember.lname,db.patientmember.patientmember, db.patientmember.cell,db.patientmember.email,db.company.company,db.patientmember.hmopatientmember)
    
    headers={
        'patientmember.patientmember':'Member ID',
        'patientmember.fname':'First Name',
        'patientmember.lname':'Last Name',
        'patientmember.email':'Email',
        'patientmember.cell':'Cell',
        'company.company':'Company',
        'patientmember.hmopatientmember':'Member'
            }


    if(request.vars.notification == "SMS"):
        selectable = lambda ids : redirect(URL('utility', 'sms_multiple', vars=dict(ids=ids,page=page,providerid=providerid)))  
    else:
        selectable = lambda ids : redirect(URL('utility', 'email_multiple', vars=dict(ids=ids,page=page,providerid=providerid)))  
        

    if(request.vars.notification == "SMS"):
        links = [lambda row: A('SMS',_href=URL("utility","send_sms",vars=dict(page=page, mode='single', ids=row.patientmember.id,providerid=providerid)))]
    else:
        links = [lambda row: A('Email',_href=URL("utility","send_email",vars=dict(page=page, mode='single', ids=row.patientmember.id,providerid=providerid)))]
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
    query = ((db.patientmember.is_active==True) & (db.patientmember.provider == providerid))

    left =    [db.company.on(db.company.id==db.patientmember.company)]
    
    
    orderby = ~(db.patientmember.id)
    
    form = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        left=left,
                        orderby=orderby,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        selectable = selectable,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )
    

    
    returnurl = URL('admin','providerhome')
    
    return dict(form=form,returnurl=returnurl,providername=provdict["providername"],providerid=providerid,page=page)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_birthday_reminders():

    
    
    page = common.getpage(request.vars.page)
    
    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]

    keywords = common.getstring(request.vars.keywords)

    start = request.vars.start
    end = request.vars.end
    
    notification=request.vars.notification
    returnurl = URL('utility','birthday_reminders',vars=dict(providerid=providerid))    
 
    fields=(db.vw_patientmemberbirthday.patientmember,db.vw_patientmemberbirthday.patientid, db.vw_patientmemberbirthday.memberid,db.vw_patientmemberbirthday.fname,db.vw_patientmemberbirthday.lname,\
                db.vw_patientmemberbirthday.birthday,db.vw_patientmemberbirthday.dob,\
                db.vw_patientmemberbirthday.cell)
        
    headers={
        'vw_patientmemberbirthday.patientmember':'Member ID',
        'vw_patientmemberbirthday.fname':'First Name',
        'vw_appointmentreminders.lname':'Last Name',
        'vw_appointmentreminders.birthday':'Birthday',
        'vw_appointmentreminders.dob':'DOB',
        'vw_patientmemberbirthday.cell':'Mobile'
            }    
 
     
    db.vw_patientmemberbirthday.email.readable = False
    db.vw_patientmemberbirthday.patientid.readable = False
    db.vw_patientmemberbirthday.memberid.readable = False
    db.vw_patientmemberbirthday.providerid.readable = False 
    db.vw_patientmemberbirthday.is_active.readable = False 
    db.vw_patientmemberbirthday.hmopatientmember.readable = False  
    db.vw_patientmemberbirthday.providername.readable = False 
    db.vw_patientmemberbirthday.lastreminder.readable = False
      

    

    if(request.vars.notification == "SMS"):
        selectable = lambda ids : redirect(URL('utility', 'birthday_sms_multiple', vars=dict(ids=ids,page=page,providerid=providerid,start=start,end=end,notification=notification)))  
    else:
        selectable = lambda ids : redirect(URL('utility', 'birthday_email_multiple', vars=dict(ids=ids,page=page,providerid=providerid,start=start,end=end,notification=notification)))  
        
            

    if(request.vars.notification == "SMS"):
        links = [lambda row: A('SMS',_href=URL("utility","send_birthday_sms",vars=dict(page=page, mode='single', providerid=providerid, ids=row.id,patientid=row.patientid,memberid=row.memberid,start=start,end=end,notification=notification)))]
    else:
        links = [lambda row: A('Email',_href=URL("utility","send_birthday_email",vars=dict(page=page, mode='single', providerid=providerid, ids=row.id,patientid=row.patientid,memberid=row.memberid,start=start,end=end,notification=notification)))]

    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
    query = ""
    if((keywords != None )& (keywords != "")):
        if((start != None) & (start != "")):
            
            query = ((db.vw_patientmemberbirthday.is_active==True) & \
                     (db.vw_patientmemberbirthday.providerid ==providerid )&\
                     ((db.vw_patientmemberbirthday.birthday)>=start) & \
                     ((db.vw_patientmemberbirthday.birthday)<=end) & \
                     (keywords)\
                     )   
        else:
            query = ((db.vw_patientmemberbirthday.is_active==True) & \
                     (db.vw_patientmemberbirthday.providerid ==providerid ) &\
                     (keywords)
                     )   
    else:
        if((start != None) & (start != "")):
            
            query = ((db.vw_patientmemberbirthday.is_active==True) & \
                     (db.vw_patientmemberbirthday.providerid ==providerid )&\
                     ((db.vw_patientmemberbirthday.birthday)>=start) & \
                     ((db.vw_patientmemberbirthday.birthday)<=end)
                     )   
        else:
            query = ((db.vw_patientmemberbirthday.is_active==True) & \
                     (db.vw_patientmemberbirthday.providerid ==providerid )
                     )   
    
  


    left =  None
    
    
    orderby = ~(db.vw_patientmemberbirthday.birthday)
    
    formA = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        left=left,
                        links=links,
                        selectable=selectable,
                        orderby=orderby,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )
    
    
    submit = formA.element('.web2py_table input[type=submit]')
    if(submit != None):
        if(request.vars.notification == 'SMS'):
            submit['_value'] = T('Send Group SMS')
        else:
            submit['_value'] = T('Send Group Email')
            
        submit['_class'] = 'form_details_button'
    
   
    
    return dict(formA=formA,providerid=providerid, providername=providerdict["providername"],returnurl=returnurl,page=page,start=start,end=end)




@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_appointment_reminders():
    page = common.getpage(request.vars.page)

    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]

    keywords = common.getstring(request.vars.keywords)

    
    start = request.vars.start
    end = request.vars.end

    notification=request.vars.notification
   
    
    returnurl = URL('utility','appointment_reminders',vars=dict(providerid=providerid))
    
    fields=(db.vw_appointmentreminders.patientmember, db.vw_appointmentreminders.fname,db.vw_appointmentreminders.lname,db.vw_appointmentreminders.cell,\
            db.vw_appointmentreminders.starttime,db.vw_appointmentreminders.endtime)
    

    headers={
        'vw_appointmentreminders.patientmember':'Member ID',
        'vw_appointmentreminders.fname':'First Name',
        'vw_appointmentreminders.lname':'Last Name',
        'vw_appointmentreminders.cell':'Mobile',
        'vw_appointmentreminders.starttime':'Start',
        'vw_appointmentreminders.enddtime':'End'
            }
    
    
    db.vw_appointmentreminders.title.readable=False 
    db.vw_appointmentreminders.place.readable=False 
    db.vw_appointmentreminders.activeappt.readable=False 
    db.vw_appointmentreminders.email.readable=False 
    db.vw_appointmentreminders.gender.readable=False 
    db.vw_appointmentreminders.hmopatientmember.readable=False  
    db.vw_appointmentreminders.patient.readable=False 
    db.vw_appointmentreminders.provider.readable=False 
    db.vw_appointmentreminders.lastreminder.readable=False 
    
    if(request.vars.notification == "SMS"):
        selectable = lambda ids : redirect(URL('appointment', 'sms_reminders', vars=dict(ids=ids,page=page,providerid=providerid,start=start,end=end,notification=notification)))  
    else:
        selectable = lambda ids : redirect(URL('appointment', 'email_reminders', vars=dict(ids=ids,page=page,providerid=providerid,start=start,end=end,notification=notification)))  
            
    if(request.vars.notification == "SMS"):
        links = [lambda row: A('SMS',_href=URL("appointment","sms_reminder",vars=dict(page=page, mode='single', providerid=providerid, ids=row.id,start=start,end=end,notification=notification)))]
    else:
        links = [lambda row: A('Email',_href=URL("appointment","email_reminder",vars=dict(page=page, mode='single', providerid=providerid, ids=row.id,start=start,end=end,notification=notification)))]

    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
    query = ""
    if((keywords != None )& (keywords != "")):
        if((start != None) & (start != "")):
            
            query = ((db.vw_appointmentreminders.activeappt==True) & \
                     (db.vw_appointmentreminders.provider ==providerid )&\
                     ((db.vw_appointmentreminders.startdate)>=start) & \
                     ((db.vw_appointmentreminders.startdate)<=end) & \
                     (keywords)\
                     )   
        else:
            query = ((db.vw_appointmentreminders.activeappt==True) & \
                     (db.vw_appointmentreminders.provider ==providerid ) &\
                     (keywords)
                     )   
    else:
        if((start != None) & (start != "")):
            
            query = ((db.vw_appointmentreminders.activeappt==True) & \
                     (db.vw_appointmentreminders.provider ==providerid )&\
                     ((db.vw_appointmentreminders.startdate)>=start) & \
                     ((db.vw_appointmentreminders.startdate)<=end)
                     )   
        else:
            query = ((db.vw_appointmentreminders.activeappt==True) & \
                     (db.vw_appointmentreminders.provider ==providerid )
                     )   
        
        
    left = None
    orderby = None
 
    formA = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            left=left,
                            links=links,
                            selectable=selectable,
                            orderby=orderby,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            formargs={'notification':notification},
                            searchable=False ,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            user_signature=True
                           )    

    
    
    
    submit = formA.element('.web2py_table input[type=submit]')
    if(submit != None):
        if(request.vars.notification == 'SMS'):
            submit['_value'] = T('SMS Group Appointment Reminders')
        else:
            submit['_value'] = T('Email Group Apointment Reminders')
            
        submit['_class'] = 'form_details_button'
    
 
    
    return dict(formA=formA,providerid=providerid, providername=providerdict["providername"],returnurl=returnurl,page=1,start=start,end=end,notification=notification)



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def appointment_reminders():
    page = 1
    providerid = int(common.getnegid(request.vars.providerid))
    providerdict = common.getproviderfromid(db,providerid)
    returnurl = URL('admin','providerhome')
   
    start = datetime.datetime.today()
    end   = datetime.datetime.today()
    
    

    
    form = SQLFORM.factory(Field('start','date',default=start,requires=IS_DATE(format=('%d/%m/%Y'))),
                           Field('end','date',end,default=end,requires=IS_DATE(format=('%d/%m/%Y')))
                           )
    
 
    xstartdate = form.element('input',_id='no_table_start')
    xstartdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xstartdate['_data-date-format'] = 'dd/mm/yyyy'
    xstartdate['_autocomplete'] = 'off' 

    xenddate = form.element('input',_id='no_table_end')
    xenddate['_class'] =  'input-group form-control form-control-inline date-picker'
    xenddate['_data-date-format'] = 'dd/mm/yyyy'
    xenddate['_autocomplete'] = 'off' 


    if form.accepts(request,session,keepvalues=True):
        start = (form.vars.start)
        end   = (form.vars.end)
        notification = request.vars.remindertype
        
        redirect(URL('utility','list_appointment_reminders',vars=dict(providerid=providerid, providername=providerdict["providername"],\
                                                              returnurl=returnurl,page=page,start=start,end=end,\
                                                              notification=notification)))
        
    
    return dict(form=form, providerid=providerid, providername=providerdict["providername"],returnurl=returnurl,page=page)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def birthday_reminders():
    page = 1
    providerid = int(common.getnegid(request.vars.providerid))
    providerdict = common.getproviderfromid(db,providerid)
    returnurl = URL('admin','providerhome')
   
    start = datetime.datetime.today()
    end   = datetime.datetime.today()
    
    form = SQLFORM.factory(Field('start','date',default=start,requires=IS_DATE(format=('%d/%m/%Y'))),
                           Field('end','date',end,default=end,requires=IS_DATE(format=('%d/%m/%Y')))
                           )
    
 
    xstartdate = form.element('input',_id='no_table_start')
    xstartdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xstartdate['_data-date-format'] = 'dd/mm/yyyy'
    xstartdate['_autocomplete'] = 'off' 

    xenddate = form.element('input',_id='no_table_end')
    xenddate['_class'] =  'input-group form-control form-control-inline date-picker'
    xenddate['_data-date-format'] = 'dd/mm/yyyy'
    xenddate['_autocomplete'] = 'off' 


    if form.accepts(request,session,keepvalues=True):
        start = (form.vars.start)
        end   = (form.vars.end)
        notification = request.vars.remindertype
        
        redirect(URL('utility','list_birthday_reminders',vars=dict(providerid=providerid, providername=providerdict["providername"],\
                                                              returnurl=returnurl,page=page,start=start,end=end,\
                                                              notification=notification)))
        
    
    return dict(form=form, providerid=providerid, providername=providerdict["providername"],returnurl=returnurl,page=page)

