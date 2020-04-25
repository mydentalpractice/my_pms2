# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from gluon import current
db = current.globalenv['db']

from decimal import Decimal
from gluon.tools import Mail
from string import Template

import urllib
import os
import mail
import datetime 
import re

import pytz
from gluon import current
from datetime import datetime
from pytz import timezone


def sitehasmoved():
 return dict()


# utc : datetime
def utc2local(utc):
 return utc+current.session.timeshift
 
# utc : datetime
def local2utc(local):
 return local-current.session.timeshift


def getLocalTime():
 timezonevalue = request.vars.timezonevalue
 tz = timezone(timezonevalue)
 dt = datetime.now(tz)
 
 return dict(dt=dt)
 
def time_calculator():

 timezonevalue = request.vars.timezonevalue
 tz = timezone(timezonevalue)
 dt = datetime.now(tz)
 
 return dict(dt=dt)


def select_datewidget(f,v):
    import datetime
    now = datetime.date.today()
    dtval = v if v else now.isoformat()
    y,m,d= str(dtval).split("-") 
    dt = SQLFORM.widgets.string.widget(f,v)
    dayid = dt['_id']+'_day'
    monthid = dt['_id']+'_month'
    yearid = dt['_id']+'_year'
    wrapper = DIV(_id=dt['_id']+"_wrapper")
    day = SELECT([OPTION(str(i).zfill(2)) for i in range(1,32)],
                 value=d,_id=dayid)
    month = SELECT([OPTION(datetime.date(2008,i,1).strftime('%B')
                           ,_value=str(i).zfill(2)) for i in range(1,13)],
                 value=m,_id=monthid)
    year = SELECT([OPTION(i) for i in range(now.year-50,now.year+50)],
                 value=y,_id=yearid)
    setval = "var curval = jQuery('#%s').val();if(curval){var pcs = curval.split('-');"\
             "var dd = pcs[2];var mm = pcs[1];var yy = pcs[0];"\
             "jQuery('#%s').val(dd);jQuery('#%s').val(mm);jQuery('#%s').val(yy);}" % \
                              (dt['_id'],dayid,monthid,yearid)
    combined = "jQuery('#%s').val()+'-'+jQuery('#%s').val()+'-'+jQuery('#%s').val()" % \
                                      (yearid,monthid,dayid)
    combine = "jQuery('#%s').val(%s);" % (dt['_id'],combined)
    onchange = "jQuery('#%s select').change(function(e){%s});" % \
                                         (wrapper['_id'],combine)
    jqscr = SCRIPT("jQuery('#%s').hide();%s%s" % (dt['_id'],setval,onchange))
    wrapper.components.extend([month,day,year,dt,jqscr])
    return wrapper

def testdate():
 
 dt = datetime.now()
 
 tz = timezone('Asia/Kolkata')
 ist = datetime.now(tz)
 fmtz = "%Y-%m-%d %H:%M:%S %Z%z"
 fmt = "%Y-%m-%d %H:%M:%S"
 s1 = ist.strftime(fmtz)
 s2 = ist.strftime(fmt)
 
 
 
 return dict(dt = ist, fmt=fmt)
    #request.localnow = request.now # creation of variable localnow
    #if not session.timeshift:
        #session.timeshift = request.localnow - request.utcnow 
    
    #loc = datetime.datetime.now()
    #locutc = local2utc(loc)
    #utclog = utc2local(locutc)
    

    #form = SQLFORM.factory(Field('posted','date',default=request.now,widget=select_datewidget))
    #if form.accepts(request.vars,session):
     #response.flash = "New record added"     
     #return dict(form=form)
   

def dentalproc():
    
    
    
    #formA = SQLFORM.factory(Field('shortdescription'),widget=SQLFORM.widgets.autocomplete(request,db.dentalprocedure.shortdescription,limitby=(0,10), min_length=2))
    #db.dentalprocedure.shortdescription.widget =SQLFORM.widgets.autocomplete(request, db.dentalprocedure.shortdescription, limitby=(0,10), min_length=2,id_field=db.dentalprocedure.id)
    #formA = SQLFORM.factory(Field('shortdescription'),widget=SQLFORM.widgets.autocomplete(request, db.dentalprocedure.shortdescription, limitby=(0,10), min_length=2,id_field=db.dentalprocedure.id))
    
    
    #db.dentalprocedure.shortdescription.widget = SQLFORM.widgets.autocomplete(request, db.dentalprocedure.shortdescription, limitby=(0,10), min_length=2)    
    db.testdentalproc.dproc.widget = SQLFORM.widgets.autocomplete(request, db.vw_dentalprocedure.shortdescription, id_field=db.vw_dentalprocedure.id)    

    formA = SQLFORM(db.testdentalproc)
    if formA.accepts(request.vars,session):
        response.flash = "New record added"      
    else:
        i = 0
        
    return dict(formA=formA)

                            

def month_input():
    
    
    return dict()


def elementnode_autocomplete():
    rows=db((db.node.computedSubClass==SC_ORGANIZATION)&(db.node.computedName.like(request.vars.term+'%')))\
    .select(db.node.computedName,distinct=True,orderby=db.node.computedName).as_list()
    result=[r['computedName']for r in rows]
    return response.json(result)

def patient_selector():

    if not request.vars.month:
        return ''
    pattern = request.vars.month.capitalize() + '%'
    selected = [row.patient for row in db((db.vw_patientmember.providerid == 112) & (db.vw_patientmember.patient.like(pattern))).select()]
    return response.json(selected)

def month_hide():
    return ''
    #selected = []
    #return DIV(*[DIV(k,
                     #_onclick="jQuery('#month').val('%s')" % k,
                     #_onmouseover="this.style.backgroundColor='yellow'",
                     #_onmouseout="this.style.backgroundColor='white'"
                     #) for k in selected])



def month_selector():
    if not request.vars.month: return ''
    months = ['January', 'February', 'March', 'April', 'May',
              'June', 'July', 'August', 'September' ,'October',
              'November', 'December']
    month_start = request.vars.month.capitalize()
    selected = [m for m in months if m.startswith(month_start)]
    return DIV(*[DIV(k,
                     _onclick="jQuery('#month').val('%s')" % k,
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'"
                     ) for k in selected])


def ymonth_selector():
    if not request.vars.month:
        return ''
    pattern = request.vars.month.capitalize() + '%'
    selected = [row.patient for row in db((db.vw_patientmember.providerid == 112) & (db.vw_patientmember.patient.like(pattern))).select()]
    return ''.join([DIV(k,
                 _onclick="jQuery('#month').val('%s')" % k,
                 _onmouseover="this.style.backgroundColor='yellow'",
                 _onmouseout="this.style.backgroundColor='white'"
                 ).xml() for k in selected])

def showerror():

    if(len(request.vars)>0):
        errorheader = request.vars.errorheader
        errormssg   = request.vars.errormssg
        returnurl   = request.vars.returnurl
    else:
        errorheader = "Unknown"
        errormssg   = "Unknown"
        returnurl   = URL('admin','providerhome')
    
    return dict(page=0, providerid=0, providername="",errorheader=errorheader,errormssg=errormssg,returnurl=returnurl,buttontext='Return')

def register():
    return dict()

def login():
    return dict(form=auth.login())

def change_password():
    return dict(form=auth.change_password())

def member_resetpassword():
    return dict()

@auth.requires_membership('webadmin')
@auth.requires_login()
def main():
    return dict()

def admin_resetpassword():
    props = db(db.urlproperties.id>0).select()
   
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
    auth.settings.reset_password_next = URL('default', 'index')
    auth.settings.request_reset_password_next = URL('default', 'index')
    form = auth.request_reset_password()
    xusername =form.element('input',_id='auth_user_username')
    xusername['_value'] =  username
    xusername['_class'] = 'w3-input w3-border  w3-small'

    
    return dict(form=form)    
    
    
def index():
    sitekey = None
    
    if(auth.user == None):
        sitekey = None
    else:
        if(auth.user.sitekey == ''):
            sitekey = None
        elif(auth.user.sitekey == None):
            sitekey = None
        else:
            sitekey = auth.user.sitekey

    if(auth.is_logged_in() & (sitekey == None)):
        redirect(URL('default','main'))
    elif (auth.is_logged_in() & (sitekey != None)):
        redirect(URL('default','user', args=['logout'], vars=dict(_next=URL('default','index'))))
    else:
        #redirect(URL('my_dentalplan','default','user'))
        formlogin = auth.login()
        return dict(formlogin=formlogin)
    
    #auth.settings.login_onaccept.append(redirect_after_adminlogin)
    #auth.settings.login_onfail.append(login_adminerror)
    #formlogin = auth.login()
    #return dict(formlogin=formlogin)

def login_error(form):
    redirect(URL('my_dentalplan','default','member_login_error'))

def member_login_error():
    return dict()

def login_adminerror(form):
    return()

def redirect_after_adminlogin(form):
    ret = auth.is_logged_in()
    
    if(ret == True):
        webmemberid = auth.user_id
        rows = db((db.webmember.webkey == auth.user.sitekey) & (db.webmember.email == auth.user.email)).select()
        if((len(rows)>0) | (auth.user.sitekey != None)):
            redirect(URL('my_dentalplan','default', 'user'))
            
        else:
            redirect(URL('my_dentalplan','default', 'main'))

def redirect_after_login(form):
    ret = auth.is_logged_in()
    if(ret == True):
        webmemberid = auth.user_id
        rows = db((db.webmember.webkey == auth.user.sitekey) & (db.webmember.email == auth.user.email)).select()
        if(len(rows)>0):
            webmemberid = rows[0].id
            db((db.webmember.id == webmemberid) & (db.webmember.status == 'No_Attempt') & (db.webmember.is_active==True)).update(status = 'Attempting')
            redirect(URL('my_dentalplan','member', 'update_webmember_0', args=[webmemberid]))
        else:
            raise HTTP(403,"Error in Login Redirection")

def member_login():

    session.logmode = 'login'
    sitekey = None
    if(len(request.args)>0):
        sitekey = request.args[0]

    auth.settings.login_next = URL('my_dentalplan','default','member_register')
    #if request.env.http_referer:
        #redirect(URL('my_dentalplan','default','member_register'))
    auth.settings.login_onaccept.append(redirect_after_login)

    auth.settings.login_onfail.append(login_error)

    formlogin = auth.login()
    submit = formlogin.element('input',_type='submit')
    submit['_style'] = 'display:none;'
    return dict(formlogin=formlogin)


def verifymember(form):
    sitekey = form.vars.sitekey
    email   = form.vars.email

    #check whether company exists
    rows = db((db.company.groupkey == sitekey) & (db.company.is_active == True)).select()
    if(len(rows) == 0):
        redirect(URL('my_dentalplan','default','member_register_error', args=['companynotregistered']))
    else:
        #check whether company-hmoplan rate defiend
        rows1 = db((db.companyhmoplanrate.company == int(rows[0].id)) & (db.companyhmoplanrate.is_active == True)).select()
        if(len(rows1) == 0):
            redirect(URL('my_dentalplan','default','member_register_error', args=['planrateerror']))

def member_register_error():
    if(len(request.args)>0):
        return dict(error = request.args[0])
    else:
        return dict(error = "registrationerror")

def member_register_success():
    ret = True
    if(request.args[0] == "True"):
        ret = True
    else:
        ret = False

    email = request.args[1]

    return dict(ret=ret, email=email)

def member_register():

    session.logmode = 'register'
    sitekey = None
    if(len(request.vars)>0):
        sitekey = request.vars["promocode"]
        db.auth_user.sitekey.default = sitekey
        
    db.auth_user.sitekey.writable = True
    db.auth_user.sitekey.readable = True
    db.auth_user.sitekey.label = "Promotion Code"
   
    db.auth_user.last_name.writable = False
    db.auth_user.last_name.readable = False
    db.auth_user.first_name.writable = False
    db.auth_user.first_name.readable = False
    db.auth_user.username.writable = True
    db.auth_user.username.readable = True
    db.auth_user.sitekey.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
    


    auth.settings.logged_url = None #URL('user', args='profile')

    form = auth.register()
    submit = form.element('input',_type='submit')
    submit['_style'] = 'display:none;'


    if form.process(onvalidation=verifymember).accepted:
        sitekey = form.vars.sitekey
        email   = form.vars.email
        
        x = re.match(regexp,email)
        db((db.auth_user.sitekey==sitekey) & (db.auth_user.email == email)).update(registration_key = '')


        # create new member
        rows = db(db.company.groupkey == sitekey).select()
        companyid = rows[0].id
        companycode = rows[0].company
        webid = db.webmember.insert(email=email,webkey=sitekey,status='No_Attempt',webenrolldate = datetime.date.today(), company=companyid,provider=1,groupregion=1, hmoplan=1, imported=True)
        db(db.webmember.id == webid).update(webmember = companycode + str(webid))



        ret = mail.emailLoginDetails(db,request,sitekey,email)

        redirect(URL('my_dentalplan','default','member_register_success', args=[ret,email]))



    return dict(form=form)



def HDFC_Callback():
    requestvars = request.vars
    webmemberid = 0

    responseheader = ''
    txamount = 0.00
    servicetax = 0.00
    swipecharge = 0.00
    total = 0.00
    fname = ''
    lname = ''
    MerchantRefNo =  request.vars.MerchantRefNo

    #MerchantRefNo = '4627_20160325_200023'  #TEST

    rows = db(db.paymenttxlog.txno == MerchantRefNo).select()
    if(len(rows)>0):
        webmemberid = int(rows[0].webmember)

    else:
        raise HTTP(403,"Error in Payment Callback " + MerchantRefNo)

    txamount = round(Decimal(rows[0].txamount,2))
    servicetax = round(Decimal(rows[0].servicetax),2)
    swipecharge = round(Decimal(rows[0].swipecharge),2)
    total = round(Decimal(rows[0].total),2)

    if(request.vars.ResponseCode == None):
        responsecode = '999'
    else:
        responsecode = request.vars.ResponseCode



    responsemssg = request.vars.ResponseMessage
    paymentid = request.vars.PaymentID
    paymentdate = request.vars.DateCreated
    if(request.vars.Amount == None):
        paymentamount = 0.00
    else:
        paymentamount = round(Decimal(request.vars.Amount),2)
    paymenttxid = request.vars.TransactionID
    accountid = request.vars.TransactionIDAccountID


    BillingName = request.vars.BillingName
    BillingAddress = request.vars.BillingAddress

    ##TEST
    #total = 124.56
    #responsecode = "0"
    #responsemssg = "Success"
    #paymentid ="Payment_ID"
    #paymentdate = "20015-06-20"
    #paymentamount = 124.56
    #paymenttxid = "Payment_TXID"
    #BillingName = "Billing_Name"
    #BillingAddress= "Billing_Addr"

    ##& (total == paymentamount)
    if((responsecode == '0') & (total == paymentamount)):
        #TEST - comment the update when testing
        db(db.webmember.id == webmemberid).update(status = 'Completed',webenrollcompletedate = datetime.date.today(),paid=True)
        db(db.webmemberdependants.webmember == webmemberid).update(paid=True)
       
        
        
        responseheader = "Thank you for your Payment!"
        #TEST - comment the update when testing
        db(db.paymenttxlog.txno == MerchantRefNo).update(responsecode=responsecode,
                                                         responsemssg=responsemssg,
                                                         paymentid=paymentid,
                                                         paymentdate=paymentdate,
                                                         paymentamount = paymentamount,
                                                         paymenttxid=paymenttxid,
                                                         accountid = accountid)

    else:
        responseheader = "Payment Failure!"
        paymentamount = 'Error'

        if((responsemssg != '') & (responsemssg != None)):
            responsemssg = "Transaction Failure - " + responsemssg
        else:
            responsemssg = "Transaction Failure"

        if((responsecode != '') & (responsecode != None)):
            responsecode =  responsecode
        else:
            responsecode = "999"

        db(db.paymenttxlog.txno == MerchantRefNo).update(responsecode=responsecode,
                                                         responsemssg=responsemssg,
                                                         paymentid=paymentid,
                                                         paymentdate=paymentdate,
                                                         paymenttxid=paymenttxid,
                                                         accountid = accountid)
        #retrieve raw post data
        #xml = request.body.read()  # retrieve the raw POST data
        #if(len(xml)>0):
            #appPath = request.folder
            #rawdatafile = paymenttxid + "_" + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S") + ".log"
            #rawdatafile = os.path.join(appPath, 'private',rawdatafile)
            #flog = open(rawdatafile, 'w')
            #flog.write(xml)
            #flog.close()

    return dict(PaymentID=paymentid, TransactionID=paymenttxid, MerchantRefNo=MerchantRefNo, BillingName=BillingName,BillingAddress=BillingAddress,Amount=paymentamount,txamount=txamount,servicetax=servicetax,swipecharge=swipecharge,ResponseMessage=responsemssg,DateCreated=paymentdate,ResponseCode=responsecode,ResponseHeader=responseheader)





def emailpaymentreceipt():

    ret = False
    if(len(request.args)>0):

        paymentid = request.args[0]
        paymenttxid= request.args[1]
        MerchantRefNo= request.args[2]
        BillingName= request.args[3]
        BillingAddress= request.args[4]
        txamount= request.args[5]
        servicetax= request.args[6]
        swipecharge= request.args[7]
        paymentamount= request.args[8]
        paymentdate= request.args[9]
        responsecode= request.args[10]
        responsemssg = request.args[11]

        rows = db(db.paymenttxlog.txno == MerchantRefNo).select()
        if(len(rows) > 0):
            webmemberid = int(rows[0].webmember)
        else:
            raise HTTP(403,"Error in sending payment receipt by email: Member Not Found")

        ret = mail.emailPaymentReceipt(db,request,webmemberid,
                                        paymentid,
                                        paymenttxid,
                                        MerchantRefNo,
                                        BillingName,
                                        BillingAddress,
                                        txamount,
                                        servicetax,
                                        swipecharge,
                                        paymentamount,
                                        paymentdate,
                                        responsecode,
                                        responsemssg
                                        )
    else:
        raise HTTP(403,"Error in sending payment receipt by email: Error in payment receipt data")

    return dict(ret=ret,logmode="login")

def emailwelcomekit():
    membername = ""
    memberid = 0
    ret = False
    if(len(request.args)>0):

        memberid = int(request.args[0])
        rows = db(db.patientmember.id == memberid).select()
        if(len(rows)>0):
            membername = rows[0].fname + " " + rows[0].lname
            providerid = int(rows[0].provider)
        else:
            raise HTTP(403,"Error in sending Welcome Kit by email: Invalid Patient Name")
        ret = mail.emailWelcomeKit(db,request,memberid,providerid)
        if(ret == False):
            raise HTTP(403,"Error in sending Welcome Kit by email: Error in sending email")
    else:
        raise HTTP(403,"Error in sending Welcome Kit by email: Invalid arguments")

    return dict(ret=ret, member = membername)

def xemailwelcomekit():
    webmembername = ""
    ret = False
    if(len(request.args)>0):

        webmemberid = int(request.args[0])
        providerid = request.args[1]
        ret = mail.emailWelcomeKit(db,request,webmemberid,providerid)

        if(ret == False):
            raise HTTP(403,"Error in sending Welcome Kit by email: Error in sending email")
        rows = db(db.webmember.id == webmemberid).select()
        if(len(rows)>0):
            webmembername = rows[0].fname + " " + rows[0].lname
    else:
        raise HTTP(403,"Error in sending Welcome Kit by email: Error in sending email")

    return dict(ret=ret, member = webmembername)

def emailwelcomekit_0():
    memberid = 0
    providerid = 0
    membername = ""

    ret = False
    if(len(request.args)>0):
        memberid = int(request.args[0])
        rows = db(db.patientmember.id == memberid).select()
        if(len(rows)>0):
            patientmember = rows[0].patientmember
            providerid = int(rows[0].provider)
            membername = rows[0].fname + " " + rows[0].lname
            ret = mail.emailWelcomeKit(db,request,memberid,providerid)
            if(ret == False):
                raise HTTP(403,"Error in sending Welcome Kit by email")

        else:
            raise HTTP(403,"Error in sending Welcome Kit by email: Invalid Patient Member")
    else:
        raise HTTP(403,"Error in sending Welcome Kit by email: No Patient Member")

    return dict(ret=ret, member = membername)

def xemailwelcomekit_0():
    memberid = 0
    providerid = 0
    webmembername = ""
    webmemberid = 0

    ret = False
    if(len(request.args)>0):
        memberid = int(request.args[0])
        rows = db(db.patientmember.id == memberid).select()
        if(len(rows)>0):
            patientmember = rows[0].patientmember
            rows1 = db(db.webmember.webmember == patientmember).select()
            if(len(rows1)>0):
                webmemberid = int(rows1[0].id)
                providerid  = int(rows1[0].provider)
                ret = mail.emailWelcomeKit(db,request,webmemberid,providerid)
                if(ret == False):
                    raise HTTP(403,"Error in sending Welcome Kit by email")
                rows2= db(db.webmember.id == webmemberid).select()
                if(len(rows2)>0):
                    webmembername = rows2[0].fname + " " + rows2[0].lname
                else:
                    raise HTTP(403,"Error in sending Welcome Kit by email")

            else:
                raise HTTP(403,"Error in sending Welcome Kit by email: Invalid Web Patient Member")

        else:
            raise HTTP(403,"Error in sending Welcome Kit by email: Invalid Patient Member")

    else:
        raise HTTP(403,"Error in sending Welcome Kit by email: No Patient Member")

    return dict(ret=ret, member = webmembername)



def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    user = db.auth_user
    key = None
    if(len(request.args) > 0):
        if(request.args[0] == 'login'):
            redirect(URL('admin','login'))
        else:
         key = request.args[1]
         users = db(user.reset_password_key == key).select()
         
         if not users:
          session.flash = 'Invalid password reset'
          redirect(URL('admin','login'))

         auth.settings.prevent_password_reset_attacks = True
         form = auth()   
         xnew =form.element('input',_id='no_table_new_password')
         xnew['_class'] = 'w3-input w3-border  w3-small'    
         xver =form.element('input',_id='no_table_new_password2')
         xver['_class'] = 'w3-input w3-border  w3-small'    
         submit = form.element('input',_type='submit')
         submit['_value'] = 'Reset Password'    
     
         if form.accepts(request,session):
             key= request.vars.key if request.vars.key else _error()
             password= request.vars.password if request.vars.password else _error()
             users = db(user.reset_password_key == key).select()
             if not users:
               session.flash='Invalid password reset'
               redirect(URL('admin','login'))
             users[0].update_record(password=CRYPT(key=auth.settings.hmac_key)(password)[0],reset_password_key='')
             session.flash='Password was reset'
             redirect(URL('admin','login'))

  
    
        
    #if(auth.user == None):
        #sitekey = None
    #elif(auth.user.sitekey == ''):
        #sitekey = None
    #else:
        #sitekey = auth.user.sitekey    
        
    #if(sitekey == None):
        #auth.settings.reset_password_next = URL('admin', 'login')
    #else:
        #auth.settings.reset_password_next = URL('admin', 'login')
        
    #auth.settings.login_onaccept.append(redirect_after_adminlogin)
    #auth.settings.login_onfail.append(login_adminerror)
    #auth.settings.reset_password_next = auth.settings.request_reset_password_next
 
    return dict(form=form)


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    filename = request.args[0]
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login()
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)


def test():
    return dict()

def urlproperties():

    crud.settings.keepvalues = True
    crud.settings.showid = True

    crud.settings.update_next = URL('default','index')
    crud.messages.submit_button = 'Submit'
    rows = db(db.urlproperties.id > 0).select()
    propid = int(rows[0].id)
    formA = crud.update(db.urlproperties, propid,cast=int, message='Properties Information Updated!')

    return dict(formA=formA)

def ibm():

    return dict()

def dps():

    return dict()

def termsandconditions():

    return dict()

def accepttest1(form):
    
    x = form.request_vars.source
    session.source = x
    if(form.request_vars.source == 'Test2'):
        redirect(URL('default','create_test2',args=[form.vars.id]))
    
    return dict()

def onvalidation2(form):
    
    x = 0
    form.attributes['hidden']['_next'] = 'update_test2/[id]'
    session.field1 = request.vars['field1']
    session.field2 = request.vars['field2']
    return dict()

def create_test1():
    
    formheader="Add Test1"
    crud.settings.formstyle='table2cols'
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.create_onvalidation = onvalidation2
    crud.settings.create_onaccept = accepttest1
    
    db.test1.field1.requires = [IS_NOT_EMPTY()]
    db.test1.field2.requires = [IS_NOT_EMPTY(),IS_EMAIL()]
    formA = crud.create(db.test1, next='create_test2/[id]')  
   
    
    return dict(formA=formA, formvars=request.vars)


def update_test1():
    
   
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.detect_record_change = False
    crud.settings.update_next = URL('default','index',args='')

    formA = crud.update(db.test1, request.args[0],cast=int)
    

    
    return dict(formA=formA)

def create_test2():
    
    formheader="Add Test2"
    crud.settings.formstyle='table2cols'
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.create_next = URL('default','update_test1',args=request.args[0])
    formA = crud.create(db.test2)  
    
    
    return dict(formA=formA)


def update_test2():
    
   
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.detect_record_change = False
    crud.settings.update_next = URL('default','index',args='')
   
   


    formA = crud.update(db.test2, request.args[0],cast=int)
    
    return dict()



def test2():
    
    return dict()

def testemail1():
    props = db(db.urlproperties.id>0).select()
    
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
    
    
    to      =  'imtiazbengali@gmail.com'
    subject = "Test Email"
    result = "Test Email"
    retVal = mail.send(to,subject,result)

    return dict()

def welcome():
    
    view = "member_register"
    
    if(len(request.args)>0):
        
        redirect("http://www.huffingtonpost.com")
        
    else:
        redirect("http://www.politico.com")
    
    return dict()

@auth.requires_login()
def logout():
    """ Logout handler """
    auth.settings.logout_next = URL('default','login')
    auth.logout()
    return dict()
