from gluon.tools import Mail
import datetime
import time
import os
from string import Template
import json
import requests


import urllib
import base64
import hashlib
import uuid




from applications.my_pms2.modules import common

from applications.my_pms2.modules import logger


#def sms_confirmation(db,request,appointmentid):
    
    #provcell = ""
    #provname = ""
    #doccell = ""
    #docname = ""
    #fname = ""
    #lname = ""
    #patcell = ""
    #docemail = ""
    
    #retVal1 = False
    #retVal2 = False
    #retVal3 = False
    #status = "Open"
    #appts = db(db.t_appointment.id == appointmentid).select()
    
    #if(len(appts)>0):
        
        #providerid = int(common.getid(appts[0].provider))
        #doctorid = int(common.getid(appts[0].doctor))
        #patientid = int(common.getid(appts[0].patient))
        
        #location = common.getstring(appts[0].f_location)
        #status = common.getstring(appts[0].f_status)
        #provs = db(db.provider.id == providerid).select()
        #if(len(provs)>0):
            #provcell = common.modify_cell(common.getstring(provs[0].cell))
            #provname = common.getstring(provs[0].providername)
            
        #docs = db(db.doctor.id == doctorid).select()
        #if(len(docs)>0):
            #doccell = common.modify_cell(common.getstring(docs[0].cell))
            #docname  = common.getstring(docs[0].name)
            #docemail = common.getstring(docs[0].email)
            
        #fname = common.getstring(appts[0].f_patientname)        
        #patcell = common.getstring(appts[0].cell)
        #if(patcell == ""):
            #pats = db(db.patientmember.id == patientid).select()
            #if(len(pats)>0):
                #patcell = common.modify_cell(common.getstring(pats[0].cell))
            #else:
                #patcell = common.modify_cell(common.getstring(appts[0].cell))
                
        #appPath = request.folder
        
        
        #smsfile = os.path.join(appPath,'templates/reminders/sms','SMS_ApptConfirm.txt')
        #if(status == 'Cancelled'):
            #smsfile = os.path.join(appPath,'templates/reminders/sms','SMS_ApptCancel.txt')
            
        #f = open(smsfile,'rb')
        #temp = Template(f.read())
        #f.close()  
        #message = temp.template
        
        #apptdate = (appts[0].f_start_time).strftime('%d/%m/%Y %H:%M')
        
               
        #message = message.replace("$fname", fname)
        #message = message.replace("$providername",docname)
        ##message = message.replace("$cell", doccell)
        ##message = message.replace("$email", docemail)
        #message = message.replace("$appointmentdate", apptdate )
        ##message = message.replace("$place",location )
        
        ##SMS sent to Doctor
        #docsmsfile = os.path.join(appPath,'templates/reminders/sms','SMS_ApptConfirmProv.txt')
        #if(status == 'Cancelled'):
            #docsmsfile = os.path.join(appPath,'templates/reminders/sms','SMS_ApptCancelProv.txt')
        
        #f = open(docsmsfile,'rb')
        #temp = Template(f.read())
        #f.close()  
        #docmessage = temp.template
        
       
        
               
        #docmessage = docmessage.replace("$fname", fname)
        #docmessage = docmessage.replace("$providername",provname)
        ##docmessage = docmessage.replace("$cell", doccell)
        ##docmessage = docmessage.replace("$email", docemail)
        #docmessage = docmessage.replace("$appointmentdate", apptdate )
        ##docmessage = docmessage.replace("$place",location )        
        
        #if(patcell != ""):
            #retVal1 = sendSMS2Email(db,patcell,message)
        #if(provcell != ""):
            #retVal2 = sendSMS2Email(db,provcell,docmessage)
       
    
    
    #return retVal1


#ccs = email1,email2..
#cc1 = ['email1','email2']
def createMailCC(ccs):
    cc1 = []
    if((ccs == "") | (ccs==None)):
        return cc1
    
    arr = ccs.split(',')
    for i in xrange(0,len(arr)):
        cc1.append(arr[i])
    
    return cc1
    
    
def emailAssignedMembers(db,request,providercode, provideremail, pdffile):

    props = db(db.urlproperties.id>0).select()
    server = None
    sender = None
    login = None
    tls = True
    mailcc = None
    
    if(len(props)>0):
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
        mailcc= props[0].mailcc
    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")

   
    mail = Mail()
    mail.settings.server = server
    mail.settings.sender = sender
    mail.settings.login =  login
    mail.settings.tls = tls

    to      =  provideremail
    subject = "Assigned Members Report"


    appPath = request.folder
    htmlfile = os.path.join(appPath, 'templates','assignedmembers.html')

    f = open(htmlfile,'rb')
    html = Template(f.read())
    f.close()

    result  = html.safe_substitute(dateandtime='xxx')  # dummy replacement

    attachments = []
    attachments += [Mail.Attachment(pdffile)]


    if(len(attachments) == 0):
        retVal = mail.send(to,subject,result,encoding='utf-8')
    else:
        retVal = mail.send(to,subject,result, attachments = attachments,encoding='utf-8')

    return retVal

def emailProviderLoginDetails(db,request,sitekey,email):

    retVal = True
    loginlink = None


    # get mail details
    tls = True
    props = db(db.urlproperties.id>0).select()

    if(len(props)>0):
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

        loginlink = "http://"  + props[0].mydp_ipaddress + ":" + props[0].mydp_port + "/my_pms2/default/provider_login"

        mail = Mail()
        mail.settings.server = server
        mail.settings.sender = sender
        mail.settings.login =  login
        mail.settings.tls = tls

        to      =  email
        subject = "MyDentalPlan Login Details"

        appPath = request.folder
        htmlfile = os.path.join(appPath, 'templates','Registration_Successful.html')

        f = open(htmlfile,'rb')
        html = Template(f.read())
        f.close()
        result  = html.safe_substitute(loginlink=loginlink)
        retVal = mail.send(to,subject,result,encoding='utf-8')

    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")



    return retVal


def emailRegistrationLink(db,request,key,email):

    retVal = True
    loginlink = None


    # get mail details
    tls = True
    props = db(db.urlproperties.id>0).select()

    if(len(props)>0):
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

        registrationlink = props[0].mydp_ipaddress + "/my_pms2/admin/register?key=" + key

        mail = Mail()
        mail.settings.server = server
        mail.settings.sender = sender
        mail.settings.login =  login
        mail.settings.tls = tls

        to      =  email
        subject = "Practice Management Software - Registration Details"

        appPath = request.folder
        htmlfile = os.path.join(appPath, 'templates','registrationemail.html')

        f = open(htmlfile,'rb')
        html = Template(f.read())
        f.close()
        result  = html.safe_substitute(registrationlink=registrationlink)
        retVal = mail.send(to,subject,result,encoding='utf-8')

    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")

    
    
    return retVal


def emailPALink(db,request,key,providerid,email):

    retVal = True
    loginlink = None


    # get mail details
    tls = True
    props = db(db.urlproperties.id>0).select()

    if(len(props)>0):
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

        palink = props[0].mydp_ipaddress + "/my_dentalplan/provider/provideragreement?key=" + key + "&providerid=" + str(providerid)

        mail = Mail()
        mail.settings.server = server
        mail.settings.sender = sender
        mail.settings.login =  login
        mail.settings.tls = tls

        to      =  email
        subject = "Provider Agreement"

        appPath = request.folder
        htmlfile = os.path.join(appPath, 'templates','provideragreementemail.html')

        f = open(htmlfile,'rb')
        html = Template(f.read())
        f.close()
        result  = html.safe_substitute(palink=palink)
        retVal = mail.send(to,subject,result,encoding='utf-8')

    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")

    
    
    return retVal


def emailProspectAgreementink(db,request,key,prospectid,email):

    retVal = True
    loginlink = None


    # get mail details
    tls = True
    props = db(db.urlproperties.id>0).select()

    if(len(props)>0):
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

        palink = props[0].mydp_ipaddress + "/my_dentalplan/prospect/prospectagreement?key=" + key + "&prospectid=" + str(prospectid)

        mail = Mail()
        mail.settings.server = server
        mail.settings.sender = sender
        mail.settings.login =  login
        mail.settings.tls = tls

        to      =  email
        subject = "Provider Agreement"

        appPath = request.folder
        htmlfile = os.path.join(appPath, 'templates','provideragreementemail.html')

        f = open(htmlfile,'rb')
        html = Template(f.read())
        f.close()
        result  = html.safe_substitute(palink=palink)
        retVal = mail.send(to,subject,result,encoding='utf-8')

    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")

    
    
    return retVal


def emailResetPasswordLink(db,request,username,reset_password_key):

    mssg = ""
    email = ""
    resetpassword = ""
    siteurl = ""
    retVal = False
    
    ds = db(db.auth_user.username == username).select()
    length = len(ds)
    
    
    if(length == 0):
        mssg = "Error: Username not in the system. Please enter correct Username!"
    elif (length > 1):
        mssg = "Error: More than one user has the same Username!"
    else:
        mssg  = "Valid request for reset password"    
        email = common.getstring(ds[0].email)
        userid = common.getid(ds[0].id)
        db(db.auth_user.id == userid).update(reset_password_key = reset_password_key)
        tls = True
        props = db(db.urlproperties.id>0).select()
    
        if(len(props)>0):
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
    
         
            mail = Mail()
            mail.settings.server = server
            mail.settings.sender = sender
            mail.settings.login =  login
            mail.settings.tls = tls
    
            to      =  email
            subject = "My Dental Plan Practice Management Software Reset Password Link"
            resetpassword ='Please click this link ' + siteurl+ '/admin/reset_password'+ '?key='+  reset_password_key + ' to reset your password' 
    
            appPath = request.folder
            htmlfile = os.path.join(appPath, 'templates','emailresetpassword.html')
    
            f = open(htmlfile,'rb')
            html = Template(f.read())
            f.close()
            result  = html.safe_substitute(resetpassword=resetpassword)
            retVal = mail.send(to,subject,result,encoding='utf-8')
    
        else:
            retVal = False
            raise HTTP(400,"Mail attributes not found")
    
    return dict(mssg=mssg,retVal=retVal)


def emailUsername(db,request,email):
    
    mssg = ""
    username = ""
    retVal = False
    
    ds = db(db.auth_user.email == email).select()
    
    length = len(ds);
    
    if(length == 0):
        mssg = "Error: User email not in the system. Please enter correct email!"
    elif (length > 1):
        mssg = "Error: More than one user has the same email!"
    else:
        mssg = "Valid username"
        username = common.getstring(ds[0].username)
        # get mail details
        tls = True
        props = db(db.urlproperties.id>0).select()
    
        if(len(props)>0):
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
    
         
            mail = Mail()
            mail.settings.server = server
            mail.settings.sender = sender
            mail.settings.login =  login
            mail.settings.tls = tls
    
            to      =  email
            subject = "My Dental Plan Practice Management Software Username"
    
            appPath = request.folder
            htmlfile = os.path.join(appPath, 'templates','emailusername.html')
    
            f = open(htmlfile,'rb')
            html = Template(f.read())
            f.close()
            result  = html.safe_substitute(myusername=username)
            retVal = mail.send(to,subject,result,encoding='utf-8')
    
        else:
            retVal = False
            raise HTTP(400,"Mail attributes not found")
    
    return dict(mssg=mssg,retVal=retVal)


def emailProviderLoginDetails(db,request,sitekey,email,username,password):

    retVal = False
    loginlink = ""
    emailreceipt = ""
    

    # get mail details
    tls = True
    props = db(db.urlproperties.id>0).select()

    if(len(props)>0):
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

        emailreceipt = props[0].emailreceipt
            
        loginlink = props[0].mydp_ipaddress + "/my_pms2/admin/login"
        

        mmail = Mail()
        mmail.settings.server = server
        mmail.settings.sender = sender
        mmail.settings.login =  login
        mmail.settings.tls = tls

        to      =  email
        subject = "My Dental Plan - Practice Management Software Login Details"

        appPath = request.folder
        htmlfile = os.path.join(appPath, 'templates','MDP Provider Login.html')

        f = open(htmlfile,'rb')
        html = Template(f.read())
        f.close()
        result  = html.safe_substitute(loginlink=loginlink,username=username,password=password)

        if(emailreceipt == ""):
            retVal = mmail.send(to,subject,result,encoding='utf-8')
        else:
            retVal = mmail.send(to,subject,result,encoding='utf-8',headers={'Disposition-Notification-To': emailreceipt})  
        
        

    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")


    return retVal


def emailLoginDetails(db,request,sitekey,email):

    retVal = True
    loginlink = None


    # get mail details
    tls = True
    props = db(db.urlproperties.id>0).select()

    if(len(props)>0):
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

        loginlink = props[0].mydp_ipaddress + "/my_dentalplan/default/member_login"
        #loginlink = "https://"  + props[0].mydp_ipaddress + ":" + props[0].mydp_port + "/my_dentalplan/default/member_login"

        mail = Mail()
        mail.settings.server = server
        mail.settings.sender = sender
        mail.settings.login =  login
        mail.settings.tls = tls

        to      =  email
        subject = "MyDentalPlan Login Details"

        appPath = request.folder
        htmlfile = os.path.join(appPath, 'templates','Registration_Successful.html')

        f = open(htmlfile,'rb')
        html = Template(f.read())
        f.close()
        result  = html.safe_substitute(loginlink=loginlink)
        retVal = mail.send(to,subject,result,encoding='utf-8')

    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")


    return retVal

def emailPaymentReceipt(db,request,memberid,paymentid,
                        transactionid,
                        merchantrefno,
                        billingname,
                        billingaddress,
                        txamount,
                        servicetax,
                        swipecharge,
                        amount,
                        datecreated,
                        responsecode,
                        responsemessage,
                        txdate):

    tls = True
    server = None
    sender = None
    login = None
 
    mailcc = ""
   

    props = db(db.urlproperties.id>0).select()

    if(len(props)>0):
        server = props[0].mailserver + ":"  + props[0].mailserverport
        sender = props[0].mailsender
        mailcc = props[0].mailcc
        login  = props[0].mailusername + ":" + props[0].mailpassword
        port = int(props[0].mailserverport)
        if((port != 25) & (port != 26)):
            tls = True
        else:
            tls = False

        if((props[0].mailusername == 'None')):
            login = None

    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")

    
    #server =  'smtp.live.com:587'
    #sender =  'imtiazbengali@hotmail.com'
    #login  =  'imtiazbengali@hotmail.com:sahil27@'

    #server =  '68.178.232.62:25'
    #sender =  'imtiazbengali@hotmail.com'
    #login  =  None



    name = ''
    fname = ''
    lname = ''
    address1 = ''
    address2 = ''
    address3 = ''
    city = ''
    st = ''
    pin = ''
    cell = ''
    email = ''
    retVal = True
    membercode= ''
    member = db(db.webmember.id == memberid).select()
    
    if(len(member)>0):
        membercode = member[0].webmember
        fname = member[0].fname
        lname = member[0].lname
        name = fname + ' '  + lname
        address1 = member[0].address1
        address2 = member[0].address2
        address3 = member[0].address3
        if(address3 == None):
            address3 = ''

        city = member[0].city
        st = member[0].st
        pin = member[0].pin
        cell = member[0].cell
        effectivedate = member[0].webenrollcompletedate
        email = member[0].email
        if(email == ''):
            retVal = False
            raise HTTP(403,"Member email not provided")
    else:
        retVal = False
        raise HTTP(403,"Member not found")

    mail = Mail()
    mail.settings.server = server
    mail.settings.sender = sender
    mail.settings.login =  login
    mail.settings.tls = tls

    to      =  email
    #to      = "imtiazbengali@hotmail.com"  #TEST

    subject = "Payment Receipt"




    appPath = request.folder
    #htmlfile = os.path.join(appPath, 'templates','paymentreceipt.html')
    #htmlfile = os.path.join(appPath, 'templates','Transaction_Successful.html')
    htmlfile = os.path.join(appPath, 'templates','MDP_Payment_Page.html')

    f = open(htmlfile,'rb')
    html = Template(f.read())
    f.close()
    result  = html.safe_substitute(toName=name, paymentid=paymentid,
                                   transactionid=transactionid,
                                   merchantrefno=merchantrefno,
                                   billingname=billingname,
                                   billingaddress=billingaddress,
                                   txamount=txamount,
                                   servicetax=servicetax,
                                   swipecharge=swipecharge,
                                   amount=amount,
                                   datecreated=datecreated,
                                   responsecode=responsecode,
                                   responsemessage=responsemessage,
                                   membercode=membercode,
                                   txdate=txdate)

    if((mailcc==None)|(mailcc=='')):
        retVal = mail.send(to,subject,result)
    else:
        retVal = mail.send(to,subject,result,cc=createMailCC(mailcc))

    return retVal


def emailWelcomeKit(db,request,memberid,providerid):

    #logger.loggerpms2.info("Enter mail emailWelcomeKit " + str(memberid) + " " + str(providerid))
    props = db(db.urlproperties.id>0).select()
    server = None
    sender = None
    login = None
    tls = True
    emailreceipt = None
    planfile = None
    welcomeletter = None
    mailcc = None
    name = ''
    fname = ''
    lname = ''
    address1 = ''
    address2 = ''
    address3 = ''
    city = ''
    st = ''
    pin = ''
    cell = ''
    email = ''
    pname = ''
    paddress1 = ''
    paddress2 = ''
    paddress3 = ''
    pcity = ''
    pst = ''
    ppin = ''
    pcell = ''
    pemail = ''
    paddr = ''
    retVal = False
    groupid = ''
    pcode = ''
    hmoplancode = ''
    membercode = ''
    region = ''
    regionid = 0
  
    
    
    #member = db(db.webmember.id == memberid).select()
    try:
        member = db(db.patientmember.id == memberid).select()
        if(len(member)>0):
            membercode = member[0].patientmember
            fname = member[0].fname
            lname = member[0].lname
            name = fname + ' '  + lname
            address1 = member[0].address1
            address2 = member[0].address2
            address3 = member[0].address3
            if(address3 == None):
                address3 = ''
    
            city = member[0].city
            st = member[0].st
            pin = member[0].pin
            cell = member[0].cell
            effectivedate = member[0].enrollmentdate
            email = member[0].email
            if(email == ''):
                retVal = False
                raise HTTP(403,"Member email not provided")
            group = db(db.company.id == int(member[0].company)).select()
            groupid = group[0].company
    
            if(member[0].groupregion != None):
                regionid = int(member[0].groupregion)
            else:
                regionid = 0
                    
            #hmoplanid = int(group[0].hmoplan)
            if(member[0].hmoplan != None):
                hmoplanid = int(member[0].hmoplan)
            else:
                hmoplanid = 0
    
            hmoplan = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.groupregion == regionid) & (db.hmoplan.is_active == True)).select()
            if(len(hmoplan)>0):
                hmoplancode = hmoplan[0].hmoplancode
                planfile = hmoplan[0].planfile
                welcomeletter = hmoplan[0].welcomeletter
                #logger.loggerpms2.info("Planfile and Welcomeletter " + planfile + " " + welcomeletter)
            else:
                hmoplancode = ''
                planfile = ''
                welcomeletter = ''
                
           
    
            regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select()
            if(len(regions)>0):
                region = regions[0].groupregion
            else:
                region = ''
    
        else:
            retVal = False
            raise HTTP(403,"Member not found")
    
    
        pats = db(db.vw_memberpatientlist.primarypatientid == memberid).select()
        
        provider = db(db.provider.id == providerid).select()
        if(len(provider)>0):
            pname = provider[0].providername
            paddress1 = provider[0].address1
            paddress2 = provider[0].address2
            if(paddress2 == None):
                paddress2 = ''
            paddress3 = provider[0].address3
            if(paddress3 == None):
                paddress3 = ''
            pcity = provider[0].city
            pst = provider[0].address1
            ppin = provider[0].pin
            pcell = provider[0].cell
            pemail = provider[0].email
            paddr = paddress1 + ' '  + paddress2 + ' '  + paddress3 + ' ' + pcity + ' ' + pst + ' ' + ppin
            pcode = provider[0].provider
    
        if(len(props)>0):
            server = props[0].mailserver + ":"  + props[0].mailserverport
            sender = props[0].mailsender
            login  = props[0].mailusername + ":" + props[0].mailpassword
            mailcc = props[0].mailcc
            
            emailreceipt = props[0].emailreceipt
            
            port = int(props[0].mailserverport)
            if((port != 25) & (port != 26)):
                tls = True
            else:
                tls = False
    
            if((props[0].mailusername == 'None')):
                login = None
            
        else:
            retVal = False
            raise HTTP(400,"Mail attributes not found")

        #tls=False   
        mmail = Mail()
        
        
        #mailserver = p3plcpnl0607.prod.phx3.secureserver.net
        #mailserverport = 587
        #mailusername = enrollment@mydentalplan.in
        #mailpassword= enr0!!ment
        #mailsender = enrollment@mydentalplan.in
        
        #server = 'smtp.gmail.com:587'
        #login = 'mydentalplan.in@gmail.com:MNgrak@7526#'
        #sender = 'mydentalplan.in@gmail.com'
        #tls = True        

        mmail.settings.server = server
        mmail.settings.sender = sender
        mmail.settings.login =  login
        mmail.settings.tls = tls
        
        
        to      =  email
        subject = "MyDentalPlan Member Welcome Letter"
        
        patientrow = db(db.patientmember.patientmember == membercode).select()
        patientid = 0
        if(len(patientrow)>0):
            patientid = patientrow[0].id
        else:
            raise HTTP(403,"Error in mapping Webmember and enrolled patientmember")
    
        normaltime = time.asctime(time.localtime(time.time())).encode('base64','strict')
        str1 = normaltime +'_'+ membercode
        encodedarg = str1.encode('base64','strict')    
    
        normaltime = time.asctime(time.localtime(time.time())).encode('base64','strict')
        returnurl = props[0].mydp_ipaddress  + "/my_dentalplan/member/list_member/"
        page = 0
        
        links = []
        names = []
        styles = []
        
        for i in xrange(0,14):
            styles.insert(i,"display:none")
        
        
        for i in xrange(0, len(pats)):
            
            args = normaltime + "_" + str(common.getid(pats[i].primarypatientid)) + "_" + str(common.getid(pats[i].patientid)) + "_" + common.getstring(pats[i].patienttype)
            encodedarg = args.encode('base64','strict')
            link = props[0].mydp_ipaddress  + "/my_dentalplan/member/member_card_welcomekit/" + encodedarg
            links.insert(i,link)
            
            names.insert(i, common.getstring(pats[i].fullname))
        
            styles[i] = "display:block"
        
        
        helpfultiplink = props[0].mydp_ipaddress + "/my_dentalplan/templates/images/HelpfulTips.jpg"
        dateandtime = time.asctime(time.localtime(time.time()))
    
        appPath = request.folder
        if((welcomeletter == None) | (welcomeletter == '')):
            if(groupid != ""):
                htmlfile = os.path.join(appPath, 'templates', groupid + '_WelcomeLetter.html')
                if(os.path.isfile(htmlfile) == False):
                    htmlfile = os.path.join(appPath, 'templates','MyDentalPlanMemberWelcomeLetter.html')
            else:
                htmlfile = os.path.join(appPath, 'templates','MyDentalPlanMemberWelcomeLetter.html')
        else:
            htmlfile = os.path.join(appPath, 'templates', welcomeletter)
    
        #htmlfile = os.path.join(appPath, 'templates','MyDentalPlanMemberWelcomeLetter.html')
        #logger.loggerpms2.info("HTML File - " + htmlfile)
        f = open(htmlfile,'rb')
        html = Template(f.read())
        f.close()
        
        
       
        
        subsdict = dict()
        
        for i in xrange(0,len(links)):
            key = "linkdep" + str(i)
            val = links[i]
            subsdict[key] = val
        
        for i in xrange(0,len(names)):
            key = "dep" + str(i)
            val = names[i]
            subsdict[key] = val
        
        for i in xrange(0,len(styles)):
            key = "displaydep" + str(i)
            val =  styles[i]
            subsdict[key] = val
            
        subsdict["helpfultiplink"]  = helpfultiplink
        subsdict["dateandtime"]  = dateandtime
        
        result = html.safe_substitute(subsdict)
        
        
        
        
        
        providerpdf = None
        providerpdf = os.path.join(appPath, 'templates','providers',pcode + '.pdf')
        #logger.loggerpms2.info("Provider file " + providerpdf)
        if(os.path.isfile(providerpdf) == False):
            providerpdf = None
    
        planpdf = None
        planstr = ""
    
        if((planfile == None) | (planfile == "")):
            if(hmoplancode.find("PRE")>-1):
                planstr = "_MyDentalPlan_Premium_TreatmentCosting"
            elif(hmoplancode.find("EXE")>-1):
                planstr = "_MyDentalPlan_Executive_TreatmentCosting"
            elif(hmoplancode.find("JUN")>-1):
                planstr = "_MyDentalPlan_Junior_TreatmentCosting"
            elif(hmoplancode.find("BAS")>-1):
                planstr = "_MyDentalPlan_Basic_TreatmentCosting"
            elif(hmoplancode.find("PLAN")>-1):
                planstr = "_MyDentalPlan_Plan_TreatmentCosting"
    
            #BLR test is for backward compatibility
            if((hmoplancode.startswith(region))|(hmoplancode.startswith("BLR"))):
                planpdf = os.path.join(appPath, 'templates','plans',hmoplancode + planstr + '.pdf')
            else:
                planpdf = os.path.join(appPath, 'templates','plans',region + hmoplancode + planstr + '.pdf')
    
        else:
            planpdf = os.path.join(appPath, 'templates','plans', planfile)
    
        #logger.loggerpms2.info("Plan PDF = " + planpdf)
        if(os.path.isfile(planpdf) == False):
            planpdf = None
        helpfulpdf = None
        helpfulpdf = os.path.join(appPath, 'templates','images','HelpfulTips_MyDentalPlan.pdf')
        if(os.path.isfile(helpfulpdf) == False):
            helpfulpdf = None
    
        #logger.loggerpms2.info("Help PDF = " + helpfulpdf)
        attachments = []
        
        #PDF attachments will be turned on once all Provider PDF are under 1MB 06 Sep 2018
        providerpdf = None
        #planpdf = None
        #helpfulpdf = None
        
        if(providerpdf != None):
            attachments += [Mail.Attachment(providerpdf)]
    
        if(planpdf != None):
            attachments += [Mail.Attachment(planpdf)]
    
        if(helpfulpdf != None):
            attachments += [Mail.Attachment(helpfulpdf)]
    
        
        if(len(attachments) == 0):
            #logger.loggerpms2.info("Before mail send 0 attachments")
            retVal = mmail.send(to,subject,result,encoding='utf-8',headers={'Disposition-Notification-To': emailreceipt})       
        else:
            #logger.loggerpms2.info("Before mail send attachments " + str(len(attachments)))            
            retVal = mmail.send(to,subject,result,attachments = attachments,encoding='utf-8',headers={'Disposition-Notification-To': emailreceipt})       
            
        #logger.loggerpms2.info("After  mail send " + str(retVal))    

    except Exception as e:
        logger.loggerpms2.info(">>Email Welcom Kit\n")
        logger.loggerpms2.info(str(e))
        
    return retVal

def emailWelcomeKit_current(db,request,memberid,providerid):

    props = db(db.urlproperties.id>0).select()
    server = None
    sender = None
    login = None
    tls = True
    emailreceipt = None
    planfile = None
    welcomeletter = None
    mailcc = None
    name = ''
    fname = ''
    lname = ''
    address1 = ''
    address2 = ''
    address3 = ''
    city = ''
    st = ''
    pin = ''
    cell = ''
    email = ''
    pname = ''
    paddress1 = ''
    paddress2 = ''
    paddress3 = ''
    pcity = ''
    pst = ''
    ppin = ''
    pcell = ''
    pemail = ''
    paddr = ''
    retVal = False
    groupid = ''
    pcode = ''
    hmoplancode = ''
    membercode = ''
    region = ''
    regionid = 0

    #member = db(db.webmember.id == memberid).select()
    member = db(db.patientmember.id == memberid).select()
    if(len(member)>0):
        membercode = member[0].patientmember
        fname = member[0].fname
        lname = member[0].lname
        name = fname + ' '  + lname
        address1 = member[0].address1
        address2 = member[0].address2
        address3 = member[0].address3
        if(address3 == None):
            address3 = ''

        city = member[0].city
        st = member[0].st
        pin = member[0].pin
        cell = member[0].cell
        effectivedate = member[0].enrollmentdate
        email = member[0].email
        if(email == ''):
            retVal = False
            raise HTTP(403,"Member email not provided")
        group = db(db.company.id == int(member[0].company)).select()
        groupid = group[0].company

        if(member[0].groupregion != None):
            regionid = int(member[0].groupregion)
        else:
            regionid = 0
                
        #hmoplanid = int(group[0].hmoplan)
        if(member[0].hmoplan != None):
            hmoplanid = int(member[0].hmoplan)
        else:
            hmoplanid = 0

        hmoplan = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.groupregion == regionid) & (db.hmoplan.is_active == True)).select()
        if(len(hmoplan)>0):
            hmoplancode = hmoplan[0].hmoplancode
            planfile = hmoplan[0].planfile
            welcomeletter = hmoplan[0].welcomeletter
        else:
            hmoplancode = ''
            planfile = ''
            welcomeletter = ''
            
       

        regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select()
        if(len(regions)>0):
            region = regions[0].groupregion
        else:
            region = ''

    else:
        retVal = False
        raise HTTP(403,"Member not found")

    provider = db(db.provider.id == providerid).select()
    if(len(provider)>0):
        pname = provider[0].providername
        paddress1 = provider[0].address1
        paddress2 = provider[0].address2
        if(paddress2 == None):
            paddress2 = ''
        paddress3 = provider[0].address3
        if(paddress3 == None):
            paddress3 = ''
        pcity = provider[0].city
        pst = provider[0].address1
        ppin = provider[0].pin
        pcell = provider[0].cell
        pemail = provider[0].email
        paddr = paddress1 + ' '  + paddress2 + ' '  + paddress3 + ' ' + pcity + ' ' + pst + ' ' + ppin
        pcode = provider[0].provider

    if(len(props)>0):
        server = props[0].mailserver + ":"  + props[0].mailserverport
        sender = props[0].mailsender
        login  = props[0].mailusername + ":" + props[0].mailpassword
        mailcc = props[0].mailcc
        
        emailreceipt = props[0].emailreceipt
        
        port = int(props[0].mailserverport)
        if((port != 25) & (port != 26)):
            tls = True
        else:
            tls = False

        if((props[0].mailusername == 'None')):
            login = None
        
    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")

    mail = Mail()
    mail.settings.server = server
    mail.settings.sender = sender
    mail.settings.login =  login
    mail.settings.tls = tls
    
    

    to      =  email
    subject = "MyDentalPlan Member Welcome Letter"
    patientrow = db(db.patientmember.patientmember == membercode).select()
    patientid = 0
    if(len(patientrow)>0):
        patientid = patientrow[0].id
    else:
        raise HTTP(403,"Error in mapping Webmember and enrolled patientmember")

    normaltime = time.asctime(time.localtime(time.time())).encode('base64','strict')
    str1 = normaltime +'_'+ membercode
    encodedarg = str1.encode('base64','strict')

    membercardlink = props[0].mydp_ipaddress  + "/my_dentalplan/member/member_card_welcomekit/" + encodedarg
    helpfultiplink = props[0].mydp_ipaddress + "/my_dentalplan/templates/images/HelpfulTips.jpg"
    #membercardlink = "https://"  + props[0].mydp_ipaddress + ":" + props[0].mydp_port + "/my_dentalplan/member/member_card_welcomekit/" + encodedarg
    #helpfultiplink = "https://"  + props[0].mydp_ipaddress + ":" + props[0].mydp_port + "/my_dentalplan/templates/images/HelpfulTips.jpg"
    dateandtime = time.asctime(time.localtime(time.time()))

    appPath = request.folder
    if((welcomeletter == None) | (welcomeletter == '')):
        if(groupid != ""):
            htmlfile = os.path.join(appPath, 'templates', groupid + '_WelcomeLetter.html')
            if(os.path.isfile(htmlfile) == False):
                htmlfile = os.path.join(appPath, 'templates','MyDentalPlanMemberWelcomeLetter.html')
        else:
            htmlfile = os.path.join(appPath, 'templates','MyDentalPlanMemberWelcomeLetter.html')
    else:
        htmlfile = os.path.join(appPath, 'templates','welcomeletter', welcomeletter)


    f = open(htmlfile,'rb')
    html = Template(f.read())
    f.close()
    #result  = html.safe_substitute(membername = name, membercode=membercode,effectivedate=effectivedate,groupid=groupid,providername=pname,provideraddress=paddr, providerphone=pcell,membercardlink=membercardlink,helpfultiplink=helpfultiplink)
    result  = html.safe_substitute(membercardlink=membercardlink,helpfultiplink=helpfultiplink,dateandtime=dateandtime)

    #pcode = 'provider'   #test
    #hmoplancode = 'plan' #test

    providerpdf = None
    providerpdf = os.path.join(appPath, 'templates','providers',pcode + '.pdf')
    if(os.path.isfile(providerpdf) == False):
        providerpdf = None

    planpdf = None
    planstr = ""

    if((planfile == None) | (planfile == "")):
        if(hmoplancode.find("PRE")>-1):
            planstr = "_MyDentalPlan_Premium_TreatmentCosting"
        elif(hmoplancode.find("EXE")>-1):
            planstr = "_MyDentalPlan_Executive_TreatmentCosting"
        elif(hmoplancode.find("JUN")>-1):
            planstr = "_MyDentalPlan_Junior_TreatmentCosting"
        elif(hmoplancode.find("BAS")>-1):
            planstr = "_MyDentalPlan_Basic_TreatmentCosting"
        elif(hmoplancode.find("PLAN")>-1):
            planstr = "_MyDentalPlan_Plan_TreatmentCosting"

        #BLR test is for backward compatibility
        if((hmoplancode.startswith(region))|(hmoplancode.startswith("BLR"))):
            planpdf = os.path.join(appPath, 'templates','plans',hmoplancode + planstr + '.pdf')
        else:
            planpdf = os.path.join(appPath, 'templates','plans',region + hmoplancode + planstr + '.pdf')

    else:
        planpdf = os.path.join(appPath, 'templates','plans', planfile)

    if(os.path.isfile(planpdf) == False):
        planpdf = None
    helpfulpdf = None
    helpfulpdf = os.path.join(appPath, 'templates','images','HelpfulTips_MyDentalPlan.pdf')
    if(os.path.isfile(helpfulpdf) == False):
        helpfulpdf = None

    attachments = []
    if(providerpdf != None):
        attachments += [Mail.Attachment(providerpdf)]

    if(planpdf != None):
        attachments += [Mail.Attachment(planpdf)]

    if(helpfulpdf != None):
        attachments += [Mail.Attachment(helpfulpdf)]

    if(len(attachments) == 0):
        retVal = mail.send(to,subject,result,encoding='utf-8',headers={'Disposition-Notification-To': emailreceipt})       
    else:
        retVal = mail.send(to,subject,result,attachments = attachments,encoding='utf-8',headers={'Disposition-Notification-To': emailreceipt})       
        
        


    return retVal

def emailProviderWelcomeKit(db,request,providercode, provideremail, pdffile):

    props = db(db.urlproperties.id>0).select()
    server = None
    sender = None
    login = None
    tls = True

    if(len(props)>0):
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
    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")

    mail = Mail()
    
  
    
    mail.settings.server = server
    mail.settings.sender = sender
    mail.settings.login =  login
    mail.settings.tls = tls

    to      =  provideremail
    subject = "Provider Welcome Letter"


    appPath = request.folder
    htmlfile = os.path.join(appPath, 'templates','ProviderWelcomeLetter.html')

    f = open(htmlfile,'rb')
    html = Template(f.read())
    f.close()

    result  = html.safe_substitute(dateandtime='xxx')

    providerpdf = None
    providerpdf = os.path.join(appPath, 'templates','providers',providercode + '.pdf')
    if(os.path.isfile(providerpdf) == False):
        providerpdf = None

    planpdf = None
    planstr = ""

    #hmoplancode = "BLRPRE101"
    #if(hmoplancode.startswith("BLRPRE")):
        #planstr = "_MyDentalPlan_Premium_TreatmentCosting"

    #planpdf = os.path.join(appPath, 'templates','plans',hmoplancode + planstr + '.pdf')
    #if(os.path.isfile(planpdf) == False):
        #planpdf = None

    helpfulpdf = None
    helpfulpdf = os.path.join(appPath, 'templates','images','MDP_Provider_HelpfulTips.pdf')
    if(os.path.isfile(helpfulpdf) == False):
        helpfulpdf = None




    attachments = []
    #attachments += [Mail.Attachment(pdffile)]


    if(providerpdf != None):
        attachments += [Mail.Attachment(providerpdf)]

    if(planpdf != None):
        attachments += [Mail.Attachment(planpdf)]

    if(helpfulpdf != None):
        attachments += [Mail.Attachment(helpfulpdf)]


    if(len(attachments) == 0):
        retVal = mail.send(to,subject,result,encoding='utf-8')
    else:
        retVal = mail.send(to,subject,result, attachments = attachments,encoding='utf-8')

    return retVal



def sendEmail(db,subject,htmltext, memberid,providerid,providerpdf, planpdf, memberpdf):

    props = db(db.urlproperties.id>0).select()
    server = None
    sender = None
    login = None

    name = ''
    fname = ''
    lname = ''
    address1 = ''
    address2 = ''
    address3 = ''
    city = ''
    st = ''
    pin = ''
    cell = ''
    email = ''
    pname = ''
    paddress1 = ''
    paddress2 = ''
    paddress3 = ''
    pcity = ''
    pst = ''
    ppin = ''
    pcell = ''
    pemail = ''
    paddr = ''
    retVal = False
    groupid = ''
    tls = True
    
    member = db(db.webmember.id == memberid).select()
    if(len(member)>0):
        membercode = member[0].webmember
        fname = member[0].fname
        lname = member[0].lname
        address1 = member[0].address1
        address2 = member[0].address2
        address3 = member[0].address3
        city = member[0].city
        st = member[0].address1
        pin = member[0].pin
        cell = member[0].cell
        effectivedate = member[0].webenrollcompletedate
        email = member[0].email
        if(email == ''):
            retVal = False
            raise HTTP(403,"Member email not provided")
        group = db(db.company.id == int(member[0].company)).select()
        groupid = group[0].company
        name = fname + ' '  + lname

    else:
        retVal = False
        raise HTTP(403,"Member not found")

    provider = db(db.provider.id == providerid).select()
    if(len(provider)>0):
        pname = provider[0].providername
        paddress1 = provider[0].address1
        paddress2 = provider[0].address2
        paddress3 = provider[0].address3
        pcity = provider[0].city
        pst = provider[0].address1
        ppin = provider[0].pin
        pcell = provider[0].cell
        pemail = provider[0].email
        paddr = paddress1 + ' '  + paddress2 + ' '  + paddress3 + ' ' + pcity + ' ' + ps + ' ' + ppin

    if(len(props)>0):
        server = props[0].mailserver + ":"  + props[0].mailserverport
        sender = props[0].mailsender
        login  = props[0].mailusername + ":" + props[0].mailpassword
        port = int(props[0].mailserverport)
        tls = True if((port != 25) & (port != 26)) else False
    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")

    mail = Mail()
    mail.settings.server = server
    mail.settings.sender = sender
    mail.settings.login =  login
    mail.settings.tls = tls

    to      =  email
    subject = "MyDentalPlan Member Welcome Letter"

    f = open(htmlfile,'rb')
    html = Template(f.read())
    f.close()
    result  = html.safe_substitute(membername = name, membercode=membercode,effectivedate=effectivedate,groupid=groupid,providername=pname,provideraddress=paddr, providerphone=pcell)

    attachments = []
    if(providerpdf != ''):
        attachments += [Mail.Attachment(providerpdf)]

    if(planpdf != ''):
        attachments += [Mail.Attachment(planpdf)]

    if(memberpdf != ''):
        attachments += [Mail.Attachment(memberpdf)]

    if(len(attachments) == 0):
        retVal = mail.send(to,subject,result)
    else:
        retVal = mail.send(to,subject,htmltext, attachments = attachments)

    return retVal



#{
  #"sender": "SOCKET",
  #"route": "4",
  #"country": "91",
  #"sms": [
    #{
      #"message": "Message1",
      #"to": [
        #"98260XXXXX",
        #"98261XXXXX"
      #]
    #},
    #{
      #"message": "Message2",
      #"to": [
        #"98260XXXXX",
        #"98261XXXXX"
      #]
    #}
  #]
#}

#sending SMS through MSG91
def sendSMS_MSG91(db, cellnos, message):
    
    resp = None
    tls = True
    props = db(db.urlproperties.id == 1).select()
    msg91key = props[0].msg91key if(len(props)>0) else ""
    url = props[0].msg91url if(len(props)>0) else "https://www.mydentalpractice.in/my_pms2/admin/login"
    
    tolist = []
    smslist = []
    smsobj = {}
    tos = cellnos.split(",")
    for i in xrange(0, len(tos)):
        tolist.append(tos[i])
     
    smsobj = {"message":message,
              "to":tolist}
    
    smslist.append(smsobj)
    
    jsonreqdata = {
        "sender": "MyDentalPlan",
        "route": "4",
        "country": "91",
        "sms":smslist
      }

    headers = {'Content-Type':'application/json', 'authkey':msg91key}
    resp = requests.post(url,json=jsonreqdata,headers=headers)
    
    if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
        respstr =   resp.text    
        
    
    return json.dumps(resp)


def encoderequestdata(self,jsondata):
    jsonstr = json.dumps(jsondata)
    jsonstrencrypt = self.encrypts(jsonstr)
    
    #jsonstrencoded = base64.b64encode(jsonstrencrypt)
    #jsonstrdecrypt = self.decrypts(jsonstrencrypt)
    reqobj = {"req_data":jsonstrencrypt}

    return reqobj  


#import urllib,urllib.request,urllib.parse
#class SendSms:
#def __init__(self,mobilenumber,message):
#url = "http://www.smscountry.com/smscwebservice_bulk.aspx"
#values = {'user' : 'XXXX',
#'passwd' : 'XXXX',
#'message' : message,
#'mobilenumber':mobilenumber,
#'mtype':'N',
#'DR':'Y'
#}
#data = urllib.parse.urlencode(values)
#data = data.encode('utf-8')
#request = urllib.request.Request(url,data)
#response = urllib.request.urlopen(request)
#print (response.read().decode('utf-8'))
#http://api.smscountry.com/SMSCwebservice_bulk.aspx?User=xxxxxx&passwd=xxxxxxxxxxx 
#x&mobilenumber=xxxxxxxxxx&message=xxxxxxxxx&sid =xxxxxxxx&mtype=N&DR=Y


def sendAPI_SMS2Email(db, cellnos, message):
    
    logger.loggerpms2.info("Enter API SendSMS2Email " + cellnos )
    
    retVal = False
    server = None
    sender = None
    login = None
    smsusername = None
    smsemail = None
    subject = "Email2SMS"
    tls = True
    
    #get email details from urlPropertieslect()
    jsonresp={}
    respstr = ""
    
    try:    
        props = db(db.urlproperties.id == 1).select()
        if(len(props)>0):
            url = props[0].mydp_getrsa_url
            server = props[0].mailserver + ":"  + props[0].mailserverport
            sender = props[0].mailsender
            login  = props[0].mailusername + ":" + props[0].mailpassword
            mailcc = props[0].mailcc
            smsusername = props[0].smsusername
            port = int(props[0].mailserverport)
            tls = True if((port !=25) & (port != 26)) else False
        else:
            retVal = False
            raise HTTP(400,"Mail attributes not found")

        #SMS URL
     
        requestObj = {
            'user' : smsusername,
            'passwd' : '71328781',
            'message' : message,
            'mobilenumber':cellnos,
            'mtype':'N',
            'DR':'Y'
        }
        
        resp = requests.post(url,data=requestObj)
        jsonresp = {}
        
        if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respstr =   resp.text
            logger.loggerpms2.info("Send SMS API Response Successs=> " + respstr)
            retVal = True
        else:
            retVal = False
            logger.loggerpms2.info("Send SMS API - Response Error " + resp.status_code)
    
    except Exception as e:
        error_message = "sendAPI_SMS2Email API Exception " + str(e)
        logger.loggerpms2.info(error_message)
        retVal = False

    return retVal


#using Format 1
def sendSMS2Email(db, cellnos, message):
    
    logger.loggerpms2.info("Enter SendSMS2Email " + cellnos)
    retVal = False
    server = None
    sender = None
    login = None
    smsusername = None
    smsemail = None
    subject = "Email2SMS"
    tls = True
    
    #get email details from urlProperties
    props = db(db.urlproperties.id == 1).select()
    

    if(len(props)>0):
        
        server = props[0].mailserver + ":"  + props[0].mailserverport
        sender = props[0].mailsender
        login  = props[0].mailusername + ":" + props[0].mailpassword
        mailcc = props[0].mailcc
        smsusername = props[0].smsusername
        port = int(props[0].mailserverport)
        tls = True if((port !=25) & (port != 26)) else False
        
    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")
    

    subject = smsusername
    tos = cellnos.split(",")
    to= ""
    
    for i in xrange(0, len(tos)):
        to = to + tos[i] + "." + smsusername + "@smscountry.net" + ","
        
    
    smsemail =  to.rstrip(',')
    #body = "User:" + smsusername + "\n"
    #body = body + "To:" + cellnos + "\n"
    #message = message.replace("\n", "\nText:")
    body = message
    
    
    try:
        email = Mail()
        email.settings.server = server
        email.settings.sender = sender
        email.settings.login =  login
        email.settings.tls = tls
        
        #retval  = True
        #logger.loggerpms2.info("SendSMS2Email:Before Send Email " + body)
        retVal = email.send(smsemail,subject,body)
        #logger.loggerpms2.info("SendSMS2Email:After Send Email " + str(retVal))
        
        
        #if((mailcc==None)|(mailcc=='')):
            #retVal = email.send(smsemail,subject,body)
        #else:
            #retVal = email.send(smsemail,subject,body,cc=[mailcc])
    except Exception as e:
        logger.loggerpms2.info("SendSMS2Email:Exception Error " + str(e))
        raise
    
    return retVal

def sendSMS2Email_format2(db, cellnos, message):
    retVal = False
    server = None
    sender = None
    login = None
    smsusername = None
    smsemail = None
    subject = "Email2SMS"
    tls = True
    
    #get email details from urlProperties
    props = db(db.urlproperties.id == 1).select()
    
    mailcc = ""
    if(len(props)>0):
        
        server = props[0].mailserver + ":"  + props[0].mailserverport
        sender = props[0].mailsender
        login  = props[0].mailusername + ":" + props[0].mailpassword
        mailcc = props[0].mailcc
        port = int(props[0].mailserverport)
        tls = True if((port !=25) & (port != 26)) else False        
        smsusername = props[0].smsusername
        smsemail = props[0].smsemail
        
    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")
    

    body = "User:" + smsusername + "\n"
    body = body + "To:" + cellnos + "\n"
    message = message.replace("\n", "\nText:")
    body = body + "Text:" + message
    
    
    email = Mail()
    email.settings.server = server
    email.settings.sender = sender
    email.settings.login =  login
    email.settings.tls = tls
    
    if((mailcc==None)|(mailcc=='')):
        retVal = email.send(smsemail,subject,body)
    else:
        retVal = email.send(smsemail,subject,body,cc=createMailCC(mailcc))
    
    return retVal


def groupEmail(db,emails,ccs, subject,message):
    
    retVal = True
    
    # get mail details
    tls = True
    props = db(db.urlproperties.id>0).select()

    if(len(props)>0):
        server = props[0].mailserver + ":"  + props[0].mailserverport
        sender = props[0].mailsender
        login  = props[0].mailusername + ":" + props[0].mailpassword
        port = int(props[0].mailserverport)
        if((port != 25) & (port != 26)):
            tls = True
        else:
            tls = False

        mail = Mail()
        mail.settings.server = server
        mail.settings.sender = sender
        mail.settings.login =  login
        mail.settings.tls = tls

        to      =  emails
        subject =  subject
        message = message
        
        #logger.loggerpms2.info("GropuEmail:Before Send Email " + message)
        retVal = mail.send(to,subject,message,cc=createMailCC(ccs))
        #logger.loggerpms2.info("GropuEmail:After Send Email " + message)
        

    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")
    
    return retVal

def _groupEmail(db,mail,emails,ccs, subject,message):
    
    retVal = True
    
    # get mail details
    tls = True
    props = db(db.urlproperties.id>0).select()

  
        
    if(len(props)>0):
        server = props[0].mailserver + ":"  + props[0].mailserverport
        sender = props[0].mailsender
        login  = props[0].mailusername + ":" + props[0].mailpassword
        port = int(props[0].mailserverport)
        if((port != 25) & (port != 26)):
            tls = True
        else:
            tls = False

        #mail = Mail()
        mail.settings.server = server
        mail.settings.sender = sender
        mail.settings.login =  login
        mail.settings.tls = tls

        to      =  emails
        subject =  subject
        message = message
        
        #logger.loggerpms2.info("GropuEmail:Before Send Email " + message)
        retVal = mail.send(to,subject,message,cc=createMailCC(ccs))
        #logger.loggerpms2.info("GropuEmail:After Send Email " + message)
        

    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")
    
    return retVal

def emailDentalCaseSheet(db,request,preregid,email):

    retVal = True
    dentalcaselink = None


    # get mail details
    tls = True
    props = db(db.urlproperties.id>0).select()

    if(len(props)>0):
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

        dentalcasesheetlink = props[0].mydp_ipaddress + "/my_dentalplan/default/dentalcasesheet?preregid=" + str(preregid)
        

        mail = Mail()
        mail.settings.server = server
        mail.settings.sender = sender
        mail.settings.login =  login
        mail.settings.tls = tls

        to      =  email
        subject = "Dental Casesheet"

        appPath = request.folder
        htmlfile = os.path.join(appPath, 'templates','dentalcasesheetletter.html')

        f = open(htmlfile,'rb')
        html = Template(f.read())
        f.close()
        result  = html.safe_substitute(dentalcasesheetlink=dentalcasesheetlink)
        retVal = mail.send(to,subject,result,encoding='utf-8')

    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")


    return retVal


def emailPreAuthorization(db,appPath,treatmentid):
    
    
    tr = db(db.treatment.id == treatmentid).select()
    
    tplanid = int(common.getid(tr[0].treatmentplan)) 
    tp = db(db.treatmentplan.id == tplanid).select()
    providerid = int(common.getid(tp[0].provider))
    patientid = int(common.getid(tp[0].patient))
    memberid = int(common.getid(tp[0].primarypatient))
    
    pats = db((db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid == memberid )).select()
    patient = ""  #first &lastname:patientmember
    patemail = ""
    patientmember = ""
    patcell = ""
    
    docname = ""
    doccell = ""
    docid = common.getid(tr[0].doctor)
    doc = db(db.doctor.id == docid).select()
    if(len(doc)>0):
        docname = common.getstring(doc[0].name)
        doccell = common.modify_cell(common.getstring(doc[0].cell))
    
    if(len(pats)>0):
        patient = common.getstring(pats[0].patient)
        patemail = common.getstring(pats[0].email)
        patientmember = common.getstring(pats[0].patientmember)
        patcell = common.modify_cell(common.getstring(pats[0].cell))
        
    provs= db((db.provider.id == providerid)&(db.provider.is_active == True)).select()
    providername = ""
    provemail = ""
    provcell = ""
    
    if(len(provs)>0):
        providername = common.getstring(provs[0].providername) + ":" + common.getstring(provs[0].provider)
        provemail = common.getstring(provs[0].email)
        provcell = common.modify_cell(provs[0].cell)
  
    #email body
    str1 = "<p>" + "Patient:" + "\t" + patient + "</p>\r\n"
    str1 = str1 + "<p>" + "Provider:" + "\t" + providername + "</p>\r\n"
    
    #treatment
    trmnts = db(db.vw_patienttreatment_detail_rpt.id == tplanid).select()
    
    
    for trtmnt in trmnts:
        str1 = str1 + "<p>Treatment Plan: " + trtmnt.treatment + "\t" + common.getdt(trtmnt.startdate).strftime("%d/%m/%Y") + "</p>\r\n"
        
    str1 = str1 + "</p>\r\n<p>Procedures</p>\r\n"
    
    #procedures
    procs = db((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True)).select()
    str1 = str1 + "<table border=\"1\">"
    for proc in procs:
        str1 = str1 + "<tr border=\"1\">"
        str1 = str1 + "<td>"  + common.getdt(proc.treatmentdate).strftime("%d/%m/%Y") + "</td>"
        str1 = str1 + "<td>"  + common.getstring(proc.altshortdescription) + "</td>"
        str1 = str1 + "<td>"  + "Rs. " + str(common.getvalue(proc.procedurefee)) + "</td>"
        str1 = str1 + "</tr>"
        
    str1 = str1 + "</table>"

    #URL properties
    props = db(db.urlproperties.id>0).select()
    server = None
    sender = None
    login = None
    medi_email = ""
    medi_mydp_email = ""
    medi_mydp_cell = ""
    mailcc = ""
    tls = True
    
      
    if(len(props)>0):
        server = props[0].mailserver + ":"  + props[0].mailserverport
        sender = props[0].mailsender
        login  = props[0].mailusername + ":" + props[0].mailpassword
        
        medi_email = props[0].medi_email
        medi_mydp_email = props[0].medi_mydp_email
        mailcc = props[0].mailcc
        medi_mydp_cell = common.modify_cell(props[0].medi_mydp_cell)
        port = int(props[0].mailserverport)
        if((port != 25) & (port != 26)):
            tls = True
        else:
            tls = False

        if((props[0].mailusername == 'None')):
                    login = None
        
    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")

    mail = Mail()
    mail.settings.server = server
    mail.settings.sender = sender
    mail.settings.login =  login
    mail.settings.tls = tls
   
    to      =  medi_mydp_email 
    subject = "Pre-Authorization for " + patient
    
    cc = ""
    if(provemail == ""):
        if(mailcc == ""):
            cc = ""
        else:
            cc = mailcc
    else:
        if(mailcc == ""):
            cc = provemail
        else:
            cc = provemail + "," + mailcc
        
    
  
    
    htmlfile = os.path.join(appPath, 'templates','preauthorizationemail.html')

    f = open(htmlfile,'rb')
    html = Template(f.read())
    f.close()
    result  = html.safe_substitute(medi_mydp_email=medi_mydp_email,emailbody=str1)    

    #pre-auth sms to be sent to patient
    #smsfile = os.path.join(appPath,'templates/reminders/sms','SMS_PreAuthorization.txt')
    #f = open(smsfile,'rb')
    #temp = Template(f.read())
    #f.close()  
    #patmessage = temp.template
    #patmessage = patmessage.replace("$fname", patient)
    #patmessage = patmessage.replace("$docname", docname)
    #patmessage = patmessage.replace("$doccell", doccell)   
    
    
    #if(patcell != ""):
        #retVal1 = sendSMS2Email(db,patcell,patmessage)    

  
    
    #sending preauthorization email to provider, medi assist contact, mydp contact
    retVal = mail.send(to,subject,result,cc=createMailCC(cc)) 

    return retVal

def emailAuthorizedTreatment(db,appPath,treatmentid):
    
   
    tr = db(db.treatment.id == treatmentid).select()
    tplanid = int(common.getid(tr[0].treatmentplan))    
    tp = db(db.treatmentplan.id == tplanid).select()
    providerid = int(common.getid(tp[0].provider))
    patientid = int(common.getid(tp[0].patient))
    memberid = int(common.getid(tp[0].primarypatient))
    pats = db((db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid == memberid )).select()
    patient = ""  #first &lastname:patientmember
    patemail = ""
    patcell = ""
    
    docname = ""
    doccell = ""
    docid = common.getid(tr[0].doctor)
    doc = db(db.doctor.id == docid).select()
    if(len(doc)>0):
        docname = common.getstring(doc[0].name)
        doccell = common.modify_cell(common.getstring(doc[0].cell))    

    if(len(pats)>0):
        patient = common.getstring(pats[0].patient)
        patemail = common.getstring(pats[0].email)
        patcell = common.getstring(pats[0].cell)
        
    provs= db((db.provider.id == providerid)&(db.provider.is_active == True)).select()
    providername = ""
    provemail = ""
    if(len(provs)>0):
        providername = common.getstring(provs[0].providername) + ":" + common.getstring(provs[0].provider)
        provemail = common.getstring(provs[0].email)
  
    #email body
    str1 = "<p>" + "Patient:" + "\t" + patient + "</p>\r\n"
    str1 = str1 + "<p>" + "Provider:" + "\t" + providername + "</p>\r\n"
    
    #treatment
    trmnts = db(db.vw_patienttreatment_detail_rpt.id == tplanid).select()
    str1 = "<p>Treatment Plan</p>"
    str1 = str1 + "\r\n"
    str1 = str1 + "<p>"
    
    for trtmnt in trmnts:
        str1 = str1 + trtmnt.treatment + "\t" + common.getdt(trtmnt.startdate).strftime("%d/%m/%Y")
        
    str1 = str1 + "</p>\r\n<p>Procedures</p>\r\n"
    
    #procedures
    procs = db((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True)).select()
    str1 = str1 + "<table border=\"1\">"
    for proc in procs:
        str1 = str1 + "<tr border=\"1\">"
        str1 = str1 + "<td span=\"2\">"  + common.getdt(proc.treatmentdate).strftime("%d/%m/%Y") + "</td>"
        str1 = str1 + "<td span=\"2\">"  + common.getstring(proc.altshortdescription) + "</td>"
        str1 = str1 + "<td> Procedure Fee </td<td>"  + "Rs. " + str(common.getvalue(proc.procedurefee)) + "</td>"
        str1 = str1 + "<td> Authorized Amount </td<td>"  + "Rs. " + str(common.getvalue(proc.inspays)) + "</td>"
        str1 = str1 + "<td> Co-Pay </td<td>"  + "Rs. " + str(common.getvalue(proc.copay)) + "</td>"
        str1 = str1 + "</tr>"
        
    str1 = str1 + "</table>"    
 
    #URL properties
    props = db(db.urlproperties.id>0).select()
    server = None
    sender = None
    login = None
    medi_email = ""
    medi_mydp_email = ""
    mailcc = ""
    tls = True
    
      
    if(len(props)>0):
        server = props[0].mailserver + ":"  + props[0].mailserverport
        sender = props[0].mailsender
        login  = props[0].mailusername + ":" + props[0].mailpassword
        
        medi_email = props[0].medi_email
        medi_mydp_email = props[0].medi_mydp_email
        mailcc = props[0].mailcc
        
        port = int(props[0].mailserverport)
        if((port != 25) & (port != 26)):
            tls = True
        else:
            tls = False

        if((props[0].mailusername == 'None')):
                    login = None
        
    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")

    mail = Mail()
    mail.settings.server = server
    mail.settings.sender = sender
    mail.settings.login =  login
    mail.settings.tls = tls

    to      =  medi_mydp_email
    subject = "Authorized Treatment for " + patient   
    
    cc = ""
    if(provemail == ""):
        if(mailcc == ""):
            cc = ""
        else:
            cc = mailcc
    else:
        if(mailcc == ""):
            cc = provemail
        else:
            cc = provemail + "," + mailcc
                
       
  
    htmlfile = os.path.join(appPath, 'templates','authorizedemail.html')

    f = open(htmlfile,'rb')
    html = Template(f.read())
    f.close()
    result  = html.safe_substitute(medi_mydp_email=medi_mydp_email,emailbody=str1)    

    #Auth sms to be sent to patient
    #smsfile = os.path.join(appPath,'templates/reminders/sms','SMS_Authorization.txt')
    #f = open(smsfile,'rb')
    #temp = Template(f.read())
    #f.close()  
    #patmessage = temp.template
    #patmessage = patmessage.replace("$fname", patient)
    #patmessage = patmessage.replace("$docname", docname)
    #patmessage = patmessage.replace("$doccell", doccell)    
    #if(patcell != ""):
        #retVal1 = sendSMS2Email(db,patcell,patmessage)  


    retVal = mail.send(to,subject,result,cc=createMailCC(cc))       

    return retVal
    
    