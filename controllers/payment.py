from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)



import os
import requests
import json

import base64
import hashlib
import sha
#import rsa

import hmac

import urllib




#from Crypto.PublicKey import RSA 
#from Crypto.Signature import SHA512
#from Crypto.Hash import SHA512 
#from Crypto import b64decode 

from OpenSSL import SSL
from OpenSSL import crypto

import datetime
from decimal  import Decimal

#import sys
#sys.path.append('modules')
from applications.my_pms2.modules import common
from applications.my_pms2.modules import account
from applications.my_pms2.modules import datasecurity
from applications.my_pms2.modules import mdputils
from applications.my_pms2.modules import mdpbenefits
from applications.my_pms2.modules import mdppayment
from applications.my_pms2.modules import mdpshopse
from applications.my_pms2.modules import mdppinelabs
from applications.my_pms2.modules import mdprules
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import logger

#from gluon.contrib import common
#from gluon.contrib import account

def getproceduregrid(treatmentid, providerid):
    
    query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.providerid  == providerid) & (db.vw_treatmentprocedure.is_active == True))
    
    fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription, db.vw_treatmentprocedure.relgrprocdesc,\
            db.vw_treatmentprocedure.tooth,db.vw_treatmentprocedure.quadrant,\
            db.vw_treatmentprocedure.procedurefee,db.vw_treatmentprocedure.copay,db.vw_treatmentprocedure.inspays,db.vw_treatmentprocedure.status,\
            db.vw_treatmentprocedure.treatmentdate)
            
    
    headers={
        'vw_treatmentprocedure.procedurecode':'Code',
        'vw_treatmentprocedure.altshortdescription':'Description',
        'vw_treatmentprocedure.relgrprocdesc':'Religare Procedure'  if(session.religare == True) else '',
        'vw_treatmentprocedure.tooth':'Tooth',
        'vw_treatmentprocedure.quadrant':'Quadrant',
        'vw_treatmentprocedure.procedurefee':'Procedure Cost',
        'vw_treatmentprocedure.copay':'Co-Pay',
        'vw_treatmentprocedure.inspays':'Authorized',
        'vw_treatmentprocedure.status':'Status',
        'vw_treatmentprocedure.treatmentdate':'Treatment Date'
    }
        
    links = None

    maxtextlengths = {'vw_treatmentprocedure.altshortdescription':100,'vw_treatmentprocedure.status':100}
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
      
    db.vw_treatmentprocedure.relgrprocdesc.represent=lambda v, r: '' if v is None else v
    
    form = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        paginate=10,
                        maxtextlengths=maxtextlengths,
                        orderby=None,
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


def getpatientinformation(patientid, memberid):
    
    patientname = ''
    patientmember = ''
    mediassistid  = ''
    patientemail = ''
    patientcell  = ''
    patientgender = ''
    patientage = 0
    patientaddress = ""
    groupref = ""   
    
    companyname  = ""
    planname = ""
    hmopatientmember = False
    
    patient = db(db.vw_memberpatientlist.patientid == patientid).select()
    if(len(patient)>0):
        patientname = common.getstring(patient[0].fullname)   # fname, last name
        patientmember = common.getstring(patient[0].patientmember)  #BLR0001
        patientemail = common.getstring(patient[0].email)
        patientcell  = common.getstring(patient[0].cell)
        patientgender = common.getstring(patient[0].gender)
        patientage = int(common.getvalue(patient[0].age))
        groupref = common.getstring(patient[0].groupref)  #company ID
        companyid = int(common.getvalue(patient[0].company))
        planid = int(common.getvalue(patient[0].hmoplan))
        hmopatientmember = patient[0].hmopatientmember
        
        r = db(db.company.id == companyid).select()
        if(len(r)>0):
            companyname = r[0].name
        
        r = db(db.hmoplan.id == planid).select()
        if(len(r)>0):
            planname = r[0].name
        
        r = db(db.patientmember.id == memberid).select()
        if(len(r) > 0):
            str1 = common.getstring(r[0].address1)
            patientaddress = patientaddress + ("" if(str1 == "") else (str1 + ","))
            str1 = common.getstring(r[0].address2)
            patientaddress = patientaddress + ("" if(str1 == "") else (str1 + ","))
            str1 = common.getstring(r[0].address3)
            patientaddress = patientaddress + ("" if(str1 == "") else (str1 + ","))
            str1 = common.getstring(r[0].city)
            patientaddress = patientaddress + ("" if(str1 == "") else (str1 + ","))
            str1 = common.getstring(r[0].st)
            patientaddress = patientaddress + ("" if(str1 == "") else (str1 + ","))
            str1 = common.getstring(r[0].pin)
            patientaddress = patientaddress + ("" if(str1 == "") else (str1 + ","))            
            patientaddress = patientaddress.rstrip(',')
            
    
    return dict(patientname=patientname,patientmember=patientmember,groupref=groupref,patientemail=patientemail,patientcell=patientcell,patientgender=patientgender,\
                patientage=patientage,patientaddress=patientaddress,companyname=companyname, planname=planname,hmopatientmember=hmopatientmember)


def getproviderinformation(providerid):
    
    provtitle = ""
    providername = ""
    providerregno = ""
    
    pracname = ""
    pracaddress1 = ""
    pracaddress2 = ""
    
    pracphone = ""
    pracemail = ""
    

    r = db(db.provider.id == providerid).select()
    if(len(r)>0):
        provtitle = r[0].title
        providername = r[0].providername
        providerregno = r[0].registration
        
        pracname = r[0].practicename
        str1 = common.getstring(r[0].address1)
        pracaddress1 = pracaddress1 + ("" if(str1 == "") else (str1 + ","))
        str1 = common.getstring(r[0].address2)
        pracaddress1 = pracaddress1 + ("" if(str1 == "") else (str1 + ","))
        str1 = common.getstring(r[0].address3)
        pracaddress1 = pracaddress1 + ("" if(str1 == "") else (str1 + ","))
        pracaddress1 = pracaddress1.rstrip(',')
        
        str1 = common.getstring(r[0].city)
        pracaddress2 = pracaddress2 + ("" if(str1 == "") else (str1 + ","))
        str1 = common.getstring(r[0].st)
        pracaddress2 = pracaddress2 + ("" if(str1 == "") else (str1 + ","))
        str1 = common.getstring(r[0].pin)
        pracaddress2 = pracaddress2 + ("" if(str1 == "") else (str1 + ","))
        pracaddress2 = pracaddress2.rstrip(',')
        
        pracemail = common.getstring(r[0].email)
        pracphone = common.getstring(r[0].telephone)
        
    return dict(providername=providername,providertitle=provtitle,providerregno = providerregno, practicename=pracname, practiceaddress1 = pracaddress1, practiceaddress2=pracaddress2,\
                practicephone = pracphone, practiceemail = pracemail)


def cashpayment_success():
    
    providerid = 0
    treatmentid = 0
    tplanid = 0
    
    bankname = ""
    chequeno = ""
    accountname = ""
    accountno = ""    

    
    dttodaydate = datetime.date.today()
    todaydate = dttodaydate.strftime("%d/%m/%Y")
    returnurl = common.getstring(request.vars.returnurl)

    providerid = int(common.getstring(request.vars.providerid))
    paymentid = int(common.getstring(request.vars.paymentid))
    pays = db(db.payment.id == paymentid).select()

    paymentref = pays[0].paymentmode
    paymentdate = todaydate
    paymenttype = pays[0].paymenttype
    paymentmode = pays[0].paymentmode
    chequeno = pays[0].chequeno
    bankname = pays[0].bankname
    accountno = pays[0].accountno
    accountname = pays[0].accountname
    
    otherinfo = ""
    
    paymentdetail = ""
    cardtype = ""
    merchantid = ""
    merchantdisplay = ""
    
    invoice = ""
    invoiceamt = float(common.getstring(pays[0].amount))
    amount = invoiceamt
    fee = ""
    status = "Success"
    
    error = ""
    errormsg = ""
    doctortitle = ''
    doctorname = ''
    treatment = ''
    chiefcomplaint = ''
    description = ''
    memberid = 0
    r = db(db.vw_fonepaise.paymentid == paymentid).select()
    if(len(r)>0):
        memberid = int(common.getid(r[0].memberid))
        treatmentid = int(common.getid(r[0].treatmentid))
        tplanid = int(common.getid(r[0].tplanid))
        providerid = int(common.getid(r[0].providerid))
        providerinfo  = getproviderinformation(providerid)
        patientinfo = getpatientinformation(int(common.getid(r[0].patientid)),int(common.getid(r[0].memberid)))

        doctortitle = common.getstring(r[0].doctortitle)
        doctorname  = common.getstring(r[0].doctorname)


        treatment = common.getstring(r[0].treatment)
        description = common.getstring(r[0].description)
        chiefcomplaint = common.getstring(r[0].chiefcomplaint)
        otherinfo = chiefcomplaint
        
        invoice = treatment + "_" + str(paymentid)
        
        
        
        db(db.payment.id == paymentid).update(\
        
            fp_paymentref = paymentref,
            fp_paymentdate = todaydate,
            fp_paymenttype = paymentmode,
            paymentmode = paymentmode,
            fp_paymentdetail = paymentdetail,
            fp_cardtype = "",
            fp_merchantid = "",
            fp_merchantdisplay = "",
            fp_invoice = invoice,
            fp_invoiceamt = invoiceamt,
            fp_amount = invoiceamt,
            amount = invoiceamt,
            fp_fee = "",
            fp_status = "Success",
            fp_error = "",
            fp_errormsg = "",
            fp_otherinfo = otherinfo,
            paymentcommit = True
        
        )
        
        #Procedure Grid
        query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True))
    
    
        fields=(db.vw_treatmentprocedure.altshortdescription, \
                   db.vw_treatmentprocedure.procedurefee,\
                   db.vw_treatmentprocedure.treatmentdate)
    
    
        headers={
            'vw_treatmentprocedure.altshortdescription':'Description',
            'vw_treatmentprocedure.procedurefee':'Procedure Cost',
            'vw_treatmentprocedure.treatmentdate':'Treatment Date'
        }
    
        links = None
        maxtextlengths = {'vw_treatmentprocedure.altshortdescription':100}
        
        exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
           
        formProcedure = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            maxtextlengths=maxtextlengths,
                            orderby=None,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            searchable=False,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            user_signature=True
                           )  
        
        
        totpaid = 0
        tottreatmentcost  = 0
        totinspays = 0    
        totaldue = 0
        
        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()                
    
        #Call Voucder success
        vcobj = mdpbenefits.Benefit(db)
        reqobj = {"paymentid" : paymentid}
        rspobj = json.loads(vcobj.voucher_success(reqobj))                 
    
        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()
    
        trtmnt = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
        discount_amount = trtmnt[0].companypay if(len(trtmnt) > 0) else 0
    
        pmnt = db((db.payment.id == paymentid) & (db.payment.is_active == True)).select()
        policy = pmnt[0].policy if(len(pmnt) > 0) else ""
        obj={
            "paymentid":str(paymentid),
            "plan":policy,
            "discount_amount":str(discount_amount),
            "memberid":str(memberid),
            "treatmentid":str(treatmentid)
        }
        bnftobj = mdpbenefits.Benefit(db)
        rspObj = json.loads(bnftobj.benefit_success(obj))
        if(rspObj['result'] == "success"):
            #update totalcompanypays (we are saving discount_amount as companypays )
            db(db.treatment.id == treatmentid).update(companypay = discount_amount)    
            #update treatmentplan assuming there is one treatment per tplan
            db(db.treatmentplan.id==tplanid).update(totalcompanypays = discount_amount) 
            db.commit()                      
    
        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()
    
        paytm = json.loads(account._calculatepayments(db, tplanid))
        tottreatmentcost= paytm["totaltreatmentcost"]
        totinspays= paytm["totalinspays"]
        totpaid=paytm["totalpaid"] 
        totaldue = paytm["totaldue"]  
        
        return dict(formProcedure=formProcedure,\
                       todaydate = todaydate,\
                       providerid = providerid,
                       practicename = providerinfo["practicename"],\
                       providername  = providerinfo["providername"],\
                       provideregnon = providerinfo["providerregno"],\
                       practiceaddress1 = providerinfo["practiceaddress1"],\
                       practiceaddress2 = providerinfo["practiceaddress2"],\
                       practicephone = providerinfo["practicephone"],\
                       practiceemail =providerinfo["practiceemail"],\
                       patientname = patientinfo["patientname"],\
                       patientmember = patientinfo["patientmember"],\
                       patientemail = patientinfo["patientemail"],\
                       patientcell = patientinfo["patientcell"],\
                       patientgender=  patientinfo["patientgender"],\
                       patientage =patientinfo["patientage"],\
                       patientaddress =patientinfo["patientaddress"],\
                       groupref = patientinfo["groupref"],\
                       companyname = patientinfo["companyname"],\
                       planname  = patientinfo["planname"],\
                       paymentref =paymentref,\
                       paymentdate = paymentdate,\
                       paymenttype = paymenttype,\
                       paymentmode = paymentmode,\
                       paymentdetail = paymentdetail,\
                       cardtype = cardtype,\
                       merchantid = merchantid,\
                       merchantdisplay = merchantdisplay,\
                       invoice = invoice,\
                       invoiceamt = invoiceamt,\
                       amount = amount,\
                       fee = fee,\
                       totaldue=totaldue,\
                       status = status,\
                       doctorname  = doctorname,\
                       treatment = treatment,\
                       description =description,\
                       chiefcomplaint = chiefcomplaint,\
                       otherinfo=otherinfo,\
                       chequeno = chequeno,\
                       bankname= bankname,\
                       accountname = accountname,\
                       accountno = accountno,\
                       error = error,\
                       errormsg=errormsg,\
                       returnurl=returnurl
                       )
        
        
            
# dict(header=CENTER("View/Print"), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("payment","payment_success",vars=dict(paymentid=row.id, page=page,tplanid=tplanid,treatmentid=treatmentid,patient=patient,fullname=fullname,patientid=patientid, memberid=memberid,providerid=providerid,providername=providername,returnurl=returnurl,mode="update"))))),
            

def print_payment_receipt():
    
    dttodaydate = common.getISTFormatCurrentLocatTime()
    todaydate = dttodaydate.strftime("%d/%m/%Y")

    paymentid  = int(common.getid(request.vars.paymentid))
    
      
    doctortitle = ''
    doctorname = ''
    treatment = ''
    chiefcomplaint = ''
    description = ''
    otherinfo = ''

    providerid = 0
    treatmentid = 0
    tplanid = 0
    patientinfo = None
    hmopatientmember = False
    
    r = db(db.vw_fonepaise.paymentid == paymentid).select()
    if(len(r)>0):
        
        treatmentid = int(common.getid(r[0].treatmentid))
        tplanid = int(common.getid(r[0].tplanid))
        providerid = int(common.getid(r[0].providerid))
        providerinfo  = getproviderinformation(providerid)
        patientinfo = getpatientinformation(int(common.getid(r[0].patientid)),int(common.getid(r[0].memberid)))
        hmopatientmember = patientinfo["hmopatientmember"]
        
        doctortitle = common.getstring(r[0].doctortitle)
        doctorname  = common.getstring(r[0].doctorname)


        treatment = common.getstring(r[0].treatment)
        description = common.getstring(r[0].description)
        chiefcomplaint = common.getstring(r[0].chiefcomplaint)
        otherinfo = chiefcomplaint


    paymentref = ""
    paymentdate = dttodaydate
    paymenttype = ""
    paymentdetail = ""
    paymentmode = ""
    cardtype = ""
    merchantid = ""
    merchantdisplay = ""
    invoice = ""
    invoiceamt = 0.00
    amount = 0.00
    fee = 0.00
    status = "S"
    chequeno = ""
    bankname= ""
    accountname = ""
    accountno = ""
    error = ""
    errormssg = ""
    
    p = db(db.payment.id == paymentid).select()

    
    if(len(p)>0):
        paymentref = p[0].fp_paymentref
        paymentdate = (p[0].fp_paymentdate).strftime("%d/%m/%Y") if((p[0].fp_paymentdate != None)) else todaydate
        paymenttype = p[0].fp_paymenttype
        paymentdetail = p[0].fp_paymentdetail
        paymentmode = p[0].paymentmode
        cardtype = p[0].fp_cardtype
        merchantid = p[0].fp_merchantid
        merchantdisplay = p[0].fp_merchantdisplay
        invoice = p[0].fp_invoice
        invoiceamt = float(common.getvalue(p[0].fp_invoiceamt))
        amount = float(common.getvalue(p[0].fp_amount))
        fee = float(common.getvalue(p[0].fp_fee))
        status = p[0].fp_status
        chequeno = common.getstring(p[0].chequeno)
        bankname= common.getstring(p[0].bankname)
        accountname = common.getstring(p[0].accountname)
        accountno = common.getstring(p[0].accountno)
        if(status == 'S'):
            error = ""
            errormsg = ""
        else:
            error  = common.getstring(p[0].fp_error)
            errormsg = common.getstring(p[0].fp_errormsg)
        
    #Procedure Grid
    query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True))


    fields=(db.vw_treatmentprocedure.altshortdescription, \
               db.vw_treatmentprocedure.procedurefee,\
               db.vw_treatmentprocedure.treatmentdate)
 
 
    headers={
        'vw_treatmentprocedure.altshortdescription':'Description',
        'vw_treatmentprocedure.procedurefee':'Procedure Cost',
        'vw_treatmentprocedure.treatmentdate':'Treatment Date'
    }
 
    links = None
    maxtextlengths = {'vw_treatmentprocedure.altshortdescription':200}
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
       
    formProcedure = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        paginate=10,
                        maxtextlengths=maxtextlengths,
                        orderby=None,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )  
    
             
    totpaid = 0
    tottreatmentcost  = 0
    totinspays = 0    
    totaldue = 0
    
    
    if(status == 'S'):
               
      
        paytm = calculatepayments(tplanid,providerid)
        tottreatmentcost= paytm["totaltreatmentcost"]
        totinspays= paytm["totalinspays"]
        totpaid=paytm["totalpaid"] 
        totaldue = paytm["totaldue"]        
    
   
    
    
    returnurl = request.vars.returnurl

    return dict(formProcedure=formProcedure,\
                todaydate = todaydate,\
                providerid = providerid,
                practicename = providerinfo["practicename"],\
                providername  = providerinfo["providername"],\
                provideregnon = providerinfo["providerregno"],\
                practiceaddress1 = providerinfo["practiceaddress1"],\
                practiceaddress2 = providerinfo["practiceaddress2"],\
                practicephone = providerinfo["practicephone"],\
                practiceemail =providerinfo["practiceemail"],\
                patientname = patientinfo["patientname"],\
                patientmember = patientinfo["patientmember"],\
                patientemail = patientinfo["patientemail"],\
                patientcell = patientinfo["patientcell"],\
                patientgender=  patientinfo["patientgender"],\
                patientage =patientinfo["patientage"],\
                patientaddress =patientinfo["patientaddress"],\
                groupref = patientinfo["groupref"],\
                companyname = patientinfo["companyname"],\
                planname  = patientinfo["planname"],\
                paymentref =paymentref,\
                paymentdate = paymentdate,\
                paymenttype = paymenttype,\
                paymentdetail = paymentdetail,\
                paymentmode = paymentmode,\
                cardtype = cardtype,\
                merchantid = merchantid,\
                merchantdisplay = merchantdisplay,\
                invoice = invoice,\
                invoiceamt = invoiceamt,\
                amount = amount,\
                fee = fee,\
                totaldue=totaldue,\
                status = status,\
                doctorname  = doctorname,\
                treatment = treatment,\
                description =description,\
                chiefcomplaint = chiefcomplaint,\
                otherinfo=otherinfo,\
                chequeno = chequeno,\
                bankname= bankname,\
                accountname = accountname,\
                accountno = accountno,\
                error = error,\
                errormsg=errormsg,\
                returnurl=returnurl
                )



def payment_success():
    
    dttodaydate = common.getISTFormatCurrentLocatTime()
    todaydate = dttodaydate.strftime("%d/%m/%Y")
    
    
    jsonData = json.dumps(request.post_vars)
    jsonConfirmPayment = json.loads(jsonData)
    
    paymentref = common.getstring(jsonConfirmPayment['payment_reference']) if('payment_reference' in jsonConfirmPayment) else "Error"
    paymentdate = common.getstring(jsonConfirmPayment['payment_date']) if('payment_date' in jsonConfirmPayment) else "01/01/1900"
    paymenttype = common.getstring(jsonConfirmPayment['payment_type']) if('payment_type' in jsonConfirmPayment) else "Error"
    paymentdetail = common.getstring(jsonConfirmPayment['payment_detail']) if('payment_detail' in jsonConfirmPayment) else "Error"
    cardtype = common.getstring(jsonConfirmPayment['card_type']) if('card_type' in jsonConfirmPayment) else "Error"
    merchantid = common.getstring(jsonConfirmPayment['merchant_id']) if('merchant_id' in jsonConfirmPayment) else "Error"
    merchantdisplay = common.getstring(jsonConfirmPayment['merchant_display']) if('merchant_display' in jsonConfirmPayment) else "Error"
    
    status = common.getstring(jsonConfirmPayment['status']) 
    
    invoice = common.getstring(jsonConfirmPayment['invoice']) if('invoice' in jsonConfirmPayment) else "Error"
    invoiceamt = common.getstring(jsonConfirmPayment['invoice_amt']) if('invoice_amt' in jsonConfirmPayment) else "0"
    amount = 0 if(status != 'S') else (common.getstring(jsonConfirmPayment['amount']) if('amount' in jsonConfirmPayment) else 0)
    fee = 0 if(status != 'S') else (common.getstring(jsonConfirmPayment['fee']) if('fee' in jsonConfirmPayment) else 0)
    
   
     
    jsonObj = json.loads(common.getstring(jsonConfirmPayment['addnl_detail']))
    
    logger.loggerpms2.info(json.dumps(jsonObj))
    paymentid = int(common.getstring(jsonObj["paymentid"]))
    
    
    
    returnurl = common.getstring(jsonObj["returnurl"])
    if((returnurl == None) |(returnurl == "")):
        returnurl = URL("admin","logout")    
    
    if(status == 'S'):
        error = ""
        errormsg = ""
    else:
        error  = common.getstring(jsonConfirmPayment['error'])
        errormsg = common.getstring(jsonConfirmPayment['error_msg'])
    
    
    
    
    
    doctortitle = ''
    doctorname = ''
    treatment = ''
    chiefcomplaint = ''
    description = ''
    otherinfo = ''

    providerid = 0
    treatmentid = 0
    tplanid = 0
    patientinfo = None
    hmopatientmember = False
    memberid = 0
    
    providerinfo = getproviderinformation(0)
    patientinfo = getpatientinformation(0,0)
   
    r = db(db.vw_fonepaise.paymentid == paymentid).select()
    if(len(r)>0):
        memberid = int(common.getid(r[0].memberid))
        treatmentid = int(common.getid(r[0].treatmentid))
        tplanid = int(common.getid(r[0].tplanid))
        providerid = int(common.getid(r[0].providerid))
        providerinfo  = getproviderinformation(providerid)
        patientinfo = getpatientinformation(int(common.getid(r[0].patientid)),int(common.getid(r[0].memberid)))
        hmopatientmember = patientinfo["hmopatientmember"]
        
        doctortitle = common.getstring(r[0].doctortitle)
        doctorname  = common.getstring(r[0].doctorname)


        treatment = common.getstring(r[0].treatment)
        description = common.getstring(r[0].description)
        chiefcomplaint = common.getstring(r[0].chiefcomplaint)
        otherinfo = chiefcomplaint
        
        Field('fp_status', 'string' ),
        Field('fp_paymentref', 'string'),
        Field('fp_paymenttype', 'string'),
        Field('fp_paymentdate', 'date'),
        Field('fp_paymentdetail', 'string'),
        Field('fp_cardtype', 'string'),
        Field('fp_merchantid', 'string'),
        Field('fp_merchantdisplay', 'string'),
        Field('fp_invoice', 'string'),
        Field('fp_invoiceamt', 'double'),
        Field('fp_amount', 'double'),
        Field('fp_fee', 'double'),
        Field('fp_error', 'string'),
        Field('fp_errormsg', 'string'),
        Field('fp_otherinfo', 'string'),
        
    
            
    db(db.payment.id == paymentid).update(\
    
        fp_paymentref = paymentref,
        fp_paymentdate = paymentdate,
        fp_paymenttype = paymenttype,
        paymentmode = 'Credit' if(status == 'S') else 'Credit/Error',
        fp_paymentdetail = paymentdetail,
        fp_cardtype = cardtype,
        fp_merchantid = merchantid,
        fp_merchantdisplay = merchantdisplay,
        fp_invoice = invoice,
        fp_invoiceamt = invoiceamt,
        fp_amount = amount,
        amount = amount,
        fp_fee = fee,
        fp_status = status,
        fp_error = error,
        fp_errormsg = errormsg,
        fp_otherinfo = otherinfo,
        paymentcommit = True
    
    )
    
    
    #Procedure Grid
    query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True))


    fields=(db.vw_treatmentprocedure.altshortdescription, \
               db.vw_treatmentprocedure.procedurefee,\
               db.vw_treatmentprocedure.treatmentdate)


    headers={
        'vw_treatmentprocedure.altshortdescription':'Description',
        'vw_treatmentprocedure.procedurefee':'Procedure Cost',
        'vw_treatmentprocedure.treatmentdate':'Treatment Date'
    }

    links = None
    maxtextlengths = {'vw_treatmentprocedure.altshortdescription':200}
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
       
    formProcedure = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        paginate=10,
                        maxtextlengths=maxtextlengths,
                        orderby=None,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )  
      
    
 
    totpaid = 0
    tottreatmentcost  = 0
    totinspays = 0    
    totaldue = 0

    
    #paytm = calculatepayments(tplanid,providerid)
    #tottreatmentcost= paytm["totaltreatmentcost"]
    #totinspays= paytm["totalinspays"]
    #totpaid=paytm["totalpaid"] 
    #totaldue = paytm["totaldue"] 

    if(status == 'S'):
        
        #db(db.treatmentplan.id == tplanid).update(totalpaid = totpaid + float(amount),totaldue  = totaldue - float(amount))        
      
        #paytm = calculatepayments(tplanid,providerid)
        #tottreatmentcost= paytm["totaltreatmentcost"]
        #totinspays= paytm["totalinspays"]
        #totpaid=paytm["totalpaid"] 
        #totaldue = paytm["totaldue"]
        
        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()                
    
        #Call Voucder success
        vcobj = mdpbenefits.Benefit(db)
        reqobj = {"paymentid" : paymentid}
        rspobj = json.loads(vcobj.voucher_success(reqobj))                 
    
        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()
        
        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()
    
        #wallet_success
        reqobj = {}
        reqobj = {"paymentid" : paymentid}
        rspobj = json.loads(vcobj.wallet_success(reqobj))                 
        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()                 
    
        trtmnt = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
        discount_amount = trtmnt[0].companypay if(len(trtmnt) > 0) else 0
    
        pmnt = db((db.payment.id == paymentid) & (db.payment.is_active == True)).select()
        policy = pmnt[0].policy if(len(pmnt) > 0) else ""
        obj={
            "paymentid":str(paymentid),
            "plan":policy,
            "discount_amount":str(discount_amount),
            "memberid":str(memberid),
            "treatmentid":str(treatmentid)
        }
        bnftobj = mdpbenefits.Benefit(db)
        rspObj = json.loads(bnftobj.benefit_success(obj))
        if(rspObj['result'] == "success"):
            #update totalcompanypays (we are saving discount_amount as companypays )
            db(db.treatment.id == treatmentid).update(companypay = discount_amount)    
            #update treatmentplan assuming there is one treatment per tplan
            db(db.treatmentplan.id==tplanid).update(totalcompanypays = discount_amount) 
            db.commit()                      
    
        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()
    
        paytm = json.loads(account._calculatepayments(db, tplanid))
        tottreatmentcost= paytm["totaltreatmentcost"]
        totinspays= paytm["totalinspays"]
        totpaid=paytm["totalpaid"] 
        totaldue = paytm["totaldue"]  
    else:
        
        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()
        
        #call Voucher Failure
        obj = {"paymentid":paymentid}
        bnftobj = mdpbenefits.Benefit(db)
        rspObj = bnftobj.voucher_failure(obj)                

        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()

        
        #Call Benefit Failure
        trtmnt = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
        discount_amount = trtmnt[0].companypay if(len(trtmnt) > 0) else 0
    
        pmnt = db((db.payment.id == paymentid) & (db.payment.is_active == True)).select()
        policy = pmnt[0].policy if(len(pmnt) > 0) else ""
        
        
        obj={
            "paymentid":str(paymentid),
            "plan":policy,
            "discount_amount":str(discount_amount),
            "memberid":str(memberid),
            "treatmentid":str(treatmentid)
            
        }
        bnftobj = mdpbenefits.Benefit(db)
        rspObj = bnftobj.benefit_failure(obj)

        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()
        paytm = json.loads(account._calculatepayments(db, tplanid))
        tottreatmentcost= paytm["totaltreatmentcost"]
        totinspays= paytm["totalinspays"]
        totpaid=paytm["totalpaid"] 
        totaldue = paytm["totaldue"]      
    
    return dict(formProcedure=formProcedure,\
                todaydate = todaydate,\
                providerid = providerid,
                practicename = providerinfo["practicename"],\
                providername  = providerinfo["providername"],\
                provideregnon = providerinfo["providerregno"],\
                practiceaddress1 = providerinfo["practiceaddress1"],\
                practiceaddress2 = providerinfo["practiceaddress2"],\
                practicephone = providerinfo["practicephone"],\
                practiceemail =providerinfo["practiceemail"],\
                patientname = patientinfo["patientname"],\
                patientmember = patientinfo["patientmember"],\
                patientemail = patientinfo["patientemail"],\
                patientcell = patientinfo["patientcell"],\
                patientgender=  patientinfo["patientgender"],\
                patientage =patientinfo["patientage"],\
                patientaddress =patientinfo["patientaddress"],\
                groupref = patientinfo["groupref"],\
                companyname = patientinfo["companyname"],\
                planname  = patientinfo["planname"],\
                paymentref =paymentref,\
                paymentdate = paymentdate,\
                paymenttype = paymenttype,\
                paymentdetail = paymentdetail,\
                cardtype = cardtype,\
                merchantid = merchantid,\
                merchantdisplay = merchantdisplay,\
                invoice = invoice,\
                invoiceamt = invoiceamt,\
                amount = amount,\
                fee = fee,\
                totaldue=totaldue,\
                status = status,\
                doctorname  = doctorname,\
                treatment = treatment,\
                description =description,\
                chiefcomplaint = chiefcomplaint,\
                otherinfo=otherinfo,\
                
                error = error,\
                errormsg=errormsg,\
                returnurl=returnurl
                )

def payment_success_hdfc():
    logger.loggerpms2.info("Enter HDFC Payment Success " + json.dumps(request.vars))
    
    
    dttodaydate = common.getISTFormatCurrentLocatTime()
    todaydate = dttodaydate.strftime("%d/%m/%Y")


    # HDFC Callback Response Params
    hdfc_paymentref =  common.getstring(request.vars.MerchantRefNo)         #"Invoice_paymentid"
    hdfc_paymentid = request.vars.PaymentID          #payment id generated by HDFC
    hdfc_paymentdate = request.vars.DateCreated      #payment happened date in HDFC YYYY-mm-dd HH:MM:SS 
    hdfc_amount = round(Decimal(request.vars.Amount),2) if((request.vars.Amount != None) & (request.vars.Amount != '')) else 0.00  #Actual Amount paid online in HDFC 
    hdfc_accountID = request.vars.RequestID         #HDFC AccountID of MYDP
    hdfc_paymenttxid = request.vars.TransactionID   #Transaction ID generated by HDFC for each payment 
    hdfc_responsecode = request.vars.ResponseCode if((request.vars.ResponseCode != '') & (request.vars.ResponseCode != None)) else '999'
    hdfc_responsemssg =  request.vars.ResponseMessage
    
    
    #extracting payment ID and Invoice
    refarr = hdfc_paymentref.split('_')   #invoice_paymentid
    paymentid = int(common.getstring(refarr[len(refarr)-1])) if(len(refarr) > 1) else 0
    invoice = common.getstring(refarr[0]) if(len(refarr) > 1) else 0   #invoice is Treatment (e.g. TRXXXXXX..)
    
    #error handling
    if(hdfc_responsecode == '0'):
        status = 'S'
        responsecode = hdfc_responsecode
        responsemssg = hdfc_responsemssg
    else:
        status = 'X'
        responsecode = hdfc_responsecode
        responsemssg = "Transaction Failure - " + responsemssg if((responsemssg != '') & (responsemssg != None)) else 'Transaction Failure'

    #extract payment information corr to paymentid returned by HDFC Callback
    paymnts = db(db.payment.id == paymentid).select()
    
    #extract payment information corr. to paymentid returned by HDFC callback
    r = db(db.vw_fonepaise.paymentid == paymentid).select()

    providerid = int(common.getid(r[0].providerid)) if(len(r) == 1) else 0
    memberid = int(common.getid(r[0].memberid)) if(len(r) == 1) else 0
    patientid = int(common.getid(r[0].patientid)) if(len(r) == 1) else 0
    
    
    pats = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select()
    companyid = int(common.getid(pats[0].company)) if(len(pats) != 0) else 0
    c = db((db.company.id == companyid) & (db.company.is_active == True)).select()
    company_code = common.getstring(c[0].company) if(len(c) >0 ) else ""
    
    rsp = json.loads(mdputils.getplandetailsformember(db, providerid,memberid, patientid))
    policy = common.getkeyvalue(rsp,"plancode","PREMWALKIN")
   
        
    #rsp = json.loads(patobj.getMemberPolicy({"providerid":str(providerid),"memberid":str(memberid)}))
    #policy = common.getkeyvalue(rsp,"plan","PREMWALKIN")

    providerinfo  = getproviderinformation(providerid)
    patientinfo = getpatientinformation(patientid, memberid)

    
    treatmentid = int(common.getid(r[0].treatmentid)) if(len(r) == 1) else 0
    tplanid = int(common.getid(r[0].tplanid)) if(len(r) == 1) else 0

    hmopatientmember = patientinfo["hmopatientmember"]
    
    doctortitle = common.getstring(r[0].doctortitle) if(len(r) == 1) else ""
    doctorname  = common.getstring(r[0].doctorname)  if(len(r) == 1) else providerinfo["providername"]


    treatment = common.getstring(r[0].treatment)  if(len(r) == 1) else ""                  #treatment 
    description = common.getstring(r[0].description) if(len(r) == 1) else ""               #treatment description
    chiefcomplaint = common.getstring(r[0].chiefcomplaint) if(len(r) == 1) else ""         #treatment chief complaint
    otherinfo = chiefcomplaint
    
    
    invoiceamt = float(common.getvalue(r[0].invoiceamt))  if(len(r) == 1) else 0.00    #This is the payment amount. This is different from amount paid online
    
    
    
    #fee, amount paid, invoice amount
    fee = 0.00
    amount = hdfc_amount
        
    
    paymentref = hdfc_paymentref
    paymentdate = datetime.datetime.strptime(hdfc_paymentdate,"%Y-%m-%d %H:%M:%S") if(len(paymnts) == 1) else "1990-01-01 00:00:00"
    paymenttype = common.getstring(paymnts[0].paymentmode) if(len(paymnts) == 1) else  "Credit"
    
    paymentdetail = hdfc_paymentid + "_" + hdfc_paymentid + "_"   + hdfc_paymenttxid           #HDFC information
    cardtype = ""
    merchantid = hdfc_accountID   
    merchantdisplay = hdfc_accountID
    
    
    
    #return url from receipt
    returnurl = URL('admin', 'providerhome')
    
  
    #update payment record with appropriate HDFC callback reference        
    db(db.payment.id == paymentid).update(\
    
        fp_paymentref   = paymentref,
        fp_paymentdate  = paymentdate,
        fp_paymenttype  = paymenttype,
        paymentmode = 'Credit' if(status == 'S') else 'Credit/Error',
        fp_paymentdetail = paymentdetail,
        fp_cardtype = cardtype,
        fp_merchantid = merchantid,
        fp_merchantdisplay = merchantdisplay,
        fp_invoice = invoice,  
        fp_invoiceamt = invoiceamt,
        fp_amount = amount,
        amount = amount,
        fp_fee = fee,
        fp_status = status,
        fp_error = responsecode,
        fp_errormsg = responsemssg,
        fp_otherinfo = otherinfo,
        paymentcommit = True
    
    )
    
    
    #Procedure Grid
    query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True))


    fields=(db.vw_treatmentprocedure.altshortdescription, \
               db.vw_treatmentprocedure.copay,\
               db.vw_treatmentprocedure.treatmentdate)


    headers={
        'vw_treatmentprocedure.altshortdescription':'Description',
        'vw_treatmentprocedure.copay':'Procedure Cost',
        'vw_treatmentprocedure.treatmentdate':'Treatment Date'
    }

    links = None
    maxtextlengths = {'vw_treatmentprocedure.altshortdescription':200}
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
       
    formProcedure = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        paginate=10,
                        maxtextlengths=maxtextlengths,
                        orderby=None,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )  
      
    totpaid = 0
    tottreatmentcost  = 0
    totinspays = 0    
    totaldue = 0
          
    if(status == 'S'):
        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()                
    
        #Call Voucder success
        vcobj = mdpbenefits.Benefit(db)
        reqobj = {"paymentid" : paymentid}
        rspobj = json.loads(vcobj.voucher_success(reqobj))                 
    
        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()
             
        #trtmnt = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
        #discount_amount = trtmnt[0].companypay if(len(trtmnt) > 0) else 0

        #pmnt = db((db.payment.id == paymentid) & (db.payment.is_active == True)).select()
        #policy = pmnt[0].policy if(len(pmnt) > 0) else ""


        #obj={
            #"paymentid":str(paymentid),
            #"plan":policy,
            #"discount_amount":str(discount_amount),
            #"memberid":str(memberid),
            #"treatmentid":str(treatmentid)
        #}
        #bnftobj = mdpbenefits.Benefit(db)
        #rspObj = json.loads(bnftobj.benefit_success(obj))

        trtmnt = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
        discount_amount = trtmnt[0].discount_amount if(len(trtmnt) > 0) else 0
        walletamount = trtmnt[0].walletamount if(len(trtmnt) > 0) else 0
        companypay = trtmnt[0].companypay if(len(trtmnt) > 0) else 0
        obj={
            "action":"benefit_success",
            "paymentid":str(paymentid),
            "plan_code":policy,
            "company_code":company_code,
            "discount_amount":str(discount_amount),
            "walletamount":str(walletamount),
            "companypay":str(companypay),
            "member_id":str(memberid),
            "treatmentid":str(treatmentid),
            "rule_event":"benefit_success"
        }
        ruleObj = mdprules.Plan_Rules(db)
        rspObj = json.loads(ruleObj.Get_Plan_Rules(obj))          
    
    
        if(rspObj['result'] == "success"):
            #update totalcompanypays (we are saving discount_amount as companypays )
            db(db.treatment.id == treatmentid).update(companypay = float(common.getkeyvalue(rspobj,"discount_benefit_amount",0)), 
                                                      walletamount= float(common.getkeyvalue(rspobj,"super_wallet_amount",0)), 
                                                      discount_amount = float(common.getkeyvalue(rspobj,"mdp_wallet_amount",0)))    
            db.commit() 
        else:
            obj={
                "action":"benefit_failure",
                "paymentid":str(paymentid),
                "plan_code":policy,
                "company_code":company_code,
                "discount_amount":str(discount_amount),
                "member_id":str(memberid),
                "treatmentid":str(treatmentid),
                "rule_event":"benefit_failure"
            }
            ruleObj = mdprules.Plan_Rules(db)
            rspObj = json.loads(ruleObj.Get_Plan_Rules(obj))                
            db(db.treatment.id == treatmentid).update(companypay = 0, 
                                                      walletamount= 0, 
                                                      discount_amount = 0)    
    

        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()
      
        paytm = json.loads(account._calculatepayments(db, tplanid))
        tottreatmentcost= paytm["totaltreatmentcost"]
        totinspays= paytm["totalinspays"]
        totpaid=paytm["totalpaid"] 
        totaldue = paytm["totaldue"]                  
    
    else:

        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()
        
        #call Voucher Failure
        obj = {"paymentid":paymentid}
        bnftobj = mdpbenefits.Benefit(db)
        rspObj = bnftobj.voucher_failure(obj)                

        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()

        
        #Call Benefit Failure
        trtmnt = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
        discount_amount = trtmnt[0].companypay if(len(trtmnt) > 0) else 0
    
        pmnt = db((db.payment.id == paymentid) & (db.payment.is_active == True)).select()
        policy = pmnt[0].policy if(len(pmnt) > 0) else ""
        
        
        obj={
            "paymentid":str(paymentid),
            "plan":policy,
            "discount_amount":str(discount_amount),
            "memberid":str(memberid),
            "treatmentid":str(treatmentid)
            
        }
        bnftobj = mdpbenefits.Benefit(db)
        rspObj = bnftobj.benefit_failure(obj)

        #here need to update treatmentplan tables
        account._updatetreatmentpayment(db, tplanid, paymentid)
        db.commit()

        paytm = json.loads(account._calculatepayments(db, tplanid))
        tottreatmentcost= paytm["totaltreatmentcost"]
        totinspays= paytm["totalinspays"]
        totpaid=paytm["totalpaid"] 
        totaldue = paytm["totaldue"]        

    
    return dict(formProcedure=formProcedure,\
                todaydate = todaydate,\
                providerid = providerid,
                practicename = providerinfo["practicename"],\
                providername  = providerinfo["providername"],\
                provideregnon = providerinfo["providerregno"],\
                practiceaddress1 = providerinfo["practiceaddress1"],\
                practiceaddress2 = providerinfo["practiceaddress2"],\
                practicephone = providerinfo["practicephone"],\
                practiceemail =providerinfo["practiceemail"],\
                patientname = patientinfo["patientname"],\
                patientmember = patientinfo["patientmember"],\
                patientemail = patientinfo["patientemail"],\
                patientcell = patientinfo["patientcell"],\
                patientgender=  patientinfo["patientgender"],\
                patientage =patientinfo["patientage"],\
                patientaddress =patientinfo["patientaddress"],\
                groupref = patientinfo["groupref"],\
                companyname = patientinfo["companyname"],\
                planname  = patientinfo["planname"],\
                paymentref =paymentref,\
                paymentdate = paymentdate,\
                paymenttype = paymenttype,\
                paymentdetail = paymentdetail,\
                cardtype = cardtype,\
                merchantid = merchantid,\
                merchantdisplay = merchantdisplay,\
                invoice = invoice,\
                invoiceamt = invoiceamt,\
                amount = amount,\
                fee = fee,\
                totaldue=totaldue,\
                status = status,\
                doctorname  = doctorname,\
                treatment = treatment,\
                description =description,\
                chiefcomplaint = chiefcomplaint,\
                otherinfo=otherinfo,\
                
                error = responsemssg,\
                errormsg=responsemssg,\
                returnurl=returnurl
                )


def payment_failure():
    
    provdict = common.getprovider(auth,db)    
    providerid = provdict["providerid"]       
    providername=provdict["providername"]
    
    returnurl = URL("admin","logout")

    #paymentref = "Ref001"
    #merchantid = "FPTEST"
    #merchantdisplay = "FPTEST MERCHANT"
    
    #invoice = "INVOICE001"
    #invoiceamt = "10.00"
    #amount = "10.00"
    #fee = "1.00"
    #status = "S"
    
    #error  = ""
    #errormsg = ""
    
    #otherinfo = "Additional Information"

    
    jsonData = json.dumps(request.post_vars)
    
    jsonConfirmPayment = json.loads(jsonData)
    

    paymentref = ""
    paymentdate = ""
    paymenttype = ""
    paymentdetail = ""
    cardtype = ""
    merchantid = ""
    merchantdisplay = ""
    
    invoice = ""
    invoiceamt = ""
    amount = ""
    fee = ""
    
    otherinfo = ""

    #status = common.getstring(jsonConfirmPayment['status'])
    status = "X"
    if(status == 'S'):
        error = ""
        errormsg = ""
    else:
        error  = "999" #common.getstring(jsonConfirmPayment['error'])
        errormsg = "User Cancelled" #common.getstring(jsonConfirmPayment['error_msg'])
 
    
    
    
    formA = SQLFORM.factory(\
        Field('paymentref', 'string',default=paymentref),
        Field('paymentdate', 'string',default=paymentdate),
        Field('paymenttype', 'string',default=paymenttype),
        Field('paymentdetail', 'string',default=paymentdetail),
        Field('cardtype', 'string',default=cardtype),
        Field('merchantid', 'string',default=merchantid),
        Field('merchantdisplay', 'string',default=merchantdisplay),
        Field('invoice', 'string',default=invoice),
        Field('invoiceamt', 'string',default=invoiceamt),
        Field('amount', 'string',default=amount),
        Field('fee', 'string',default=fee),
        Field('status', 'string',default=status),
        Field('error', 'string',default=error),
        Field('errormsg', 'string',default=errormsg),
        Field('otherinfo', 'string',default=otherinfo)
            
    )
    
    xpaymentref = formA.element('#no_table_paymentref')
    xpaymentref['_class'] = 'form-control'
    xpaymentref['_autocomplete'] = 'off'    

    xpaymentdate = formA.element('#no_table_paymentdate')
    xpaymentdate['_class'] = 'form-control'
    xpaymentdate['_autocomplete'] = 'off'    
  
    xpaymenttype = formA.element('#no_table_paymenttype')
    xpaymenttype['_class'] = 'form-control'
    xpaymenttype['_autocomplete'] = 'off'    
  
    xpaymentdetail = formA.element('#no_table_paymentdetail')
    xpaymentdetail['_class'] = 'form-control'
    xpaymentdetail['_autocomplete'] = 'off'    
  
    xcardtype = formA.element('#no_table_cardtype')
    xcardtype['_class'] = 'form-control'
    xcardtype['_autocomplete'] = 'off'    
  
  
    xmerchantid = formA.element('#no_table_merchantid')
    xmerchantid['_class'] = 'form-control'
    xmerchantid['_autocomplete'] = 'off'  
    
    xmerchantdisplay = formA.element('#no_table_merchantdisplay')
    xmerchantdisplay['_class'] = 'form-control'
    xmerchantdisplay['_autocomplete'] = 'off'  
    
    xinvoice = formA.element('#no_table_invoice')
    xinvoice['_class'] = 'form-control'
    xinvoice['_autocomplete'] = 'off'  
    
    xinvoiceamt = formA.element('#no_table_invoiceamt')
    xinvoiceamt['_class'] = 'form-control'
    xinvoiceamt['_autocomplete'] = 'off'  
    
    xamount = formA.element('#no_table_amount')
    xamount['_class'] = 'form-control'
    xamount['_autocomplete'] = 'off'  
    
    xfee = formA.element('#no_table_fee')
    xfee['_class'] = 'form-control'
    xfee['_autocomplete'] = 'off'  
    
    xstatus = formA.element('#no_table_status')
    xstatus['_class'] = 'form-control'
    xstatus['_autocomplete'] = 'off'  
    
    xerror = formA.element('#no_table_error')
    xerror['_class'] = 'form-control'
    xerror['_autocomplete'] = 'off'  
    
    xerrormsg = formA.element('#no_table_errormsg')
    xerrormsg['_class'] = 'form-control'
    xerrormsg['_autocomplete'] = 'off'  
    
    xotherinfo = formA.element('#no_table_otherinfo')
    xotherinfo['_class'] = 'form-control'
    xotherinfo['_autocomplete'] = 'off'  
    
    return dict(formA=formA,providerid=providerid,providername=providername,returnurl=returnurl,status=status)
    
def acceptcreatepayment(form):
    
    providerid = int(common.getid(form.vars.provider))
    tplanid = int(common.getid(form.vars.treatmentplan))
    amount = float(common.getvalue(form.vars.amount))
    paymenttype = common.getstring(form.vars.paymenttype)
    
    pays = db((db.payment.treatmentplan == tplanid) & (db.payment.provider == providerid)).select()
    
    totalpaid = 0
    totalinspaid = 0
    totalcopaypaid = 0
    totaldue = 0
    
    for pay in pays:
        if(pay.paymenttype == "Treatment"):
            totalpaid = totalpaid + pay.amount
        if(pay.paymenttype == "Insurance"):
            totalinspaid = totalinspaid + pay.amount
        if(pay.paymenttype == "Insurance"):
            totalcopaypaid = totalcopaypaid + pay.amount
    
    tr = db(db.treatmentplan.id == tplanid).select(db.treatmentplan.totaltreatmentcost)
    
    totaldue = float(common.getvalue(tr[0].totaltreatmentcost)) - totalpaid - totalinspaid - totalcopaypaid
    
    db(db.treatmentplan.id == tplanid).update(totalpaid = totalpaid, totalinspaid = totalinspaid, totalcopaypaid = totalcopaypaid, totaldue=totaldue)
    
    return dict()

def acceptupdatepayment(form):
    acceptcreatepayment(form)
    
    return dict()

def hextobyte(hexStr):
    
    bytes = []
   
    hexStr = ''.join( hexStr.split(" ") )

    for i in range(0, len(hexStr), 2):
        bytes.append( chr( int (hexStr[i:i+2], 16 ) ) )

    return ''.join( bytes )    


def bytetohex(byteStr):
    
    x = ''.join( [ "%02X " % ord( x ) for x in byteStr ] ).strip()
    
    return x



def generateHashForMessage(keyfile, message):
    
 
    
    privKey = ""
    privKey+="-----BEGIN RSA PRIVATE KEY-----\n";
    privKey+="MIIEowIBAAKCAQEAzcwX4G00jaets0mJknH/acMq++0AhIxkb8rrx2kUPQLD6mL8\n";
    privKey+="SMLLWq+FhEiyCjfbVL78xOMSRkbsuydLBp3oUaJvd30lrXXJOlfjAgE38VDn60SQ\n";
    privKey+="jajxBHDYtfNPXXM9arJlH2XoBt+KfwEVESd2xwGlb0t2HV/LQMHJxxRl9kC5ff3l\n";
    privKey+="9NqgGVm8aQRaI7AJc6ZBdROjZGiGiIrsprzzdRJkEJnom3klCZceo7lILRdivXku\n";
    privKey+="oW5HtJIQNlKcvtJwOjyxg56VbkJxaVxtFMYqIyzHZYf0b9KAmnXdnsWHRgdgk96v\n";
    privKey+="zRh7Q2Eipy1NcQSJr0vdpzzB1Zju4GrqMSkkHwIDAQABAoIBAQCjNQaCf1i8Nox0\n";
    privKey+="sQ8fSrTqJVODc1ODyuskFWOjQ1w/fl/tFA9LjOBEzQov/I7lt6KDtOs1IXeusDSx\n";
    privKey+="v9mqJ7TEePO5aVBmHhE16dkoD9tTz3v9guS405BAm1XiBlGcpPXCFjRIEENQoBtv\n";
    privKey+="2WXhstBpxo5ykv/bD8tbUdQ5w52RChtowDRnhOh+6LmAoRVcD/OVBDoIh79n5onU\n";
    privKey+="XX5OSqzcOKa1Xpac50zrYSsf2Yvu6vaBpBInvz5hOIXQjtbnF1LTlcVN0DDgS9EF\n";
    privKey+="iIcgZVoU3mOp7e2sl+DJyMHkbLuAkJT9C7K4oZkn7BHIKSEbXhEM4RvU7gtQlR78\n";
    privKey+="yOlx9okBAoGBAOrXldEUgklDvQAeuAPaecIAeVffkpGgRd5Qj35iWzm6ELOSZdFO\n";
    privKey+="Rdz4eyH1tTs2Q7aj04UX8vslevl1rt33Mxtxj9jhQjqz5XrJhlz071gFm36MBJIk\n";
    privKey+="ApHXa0RZsqSOkEdmQSLax14cz30fQa/Ecmwc6y7lL+8oaNARgif2Z2dfAoGBAOBW\n";
    privKey+="nV7FSZycSuuWpCPIoRiabtSoFZqyqOs2H6ZcN23c6BT2y0QJrnNPSfWkHLgEGggR\n";
    privKey+="H4Lh3lTSW9gkwL/dHcexN4Fxwg21uElHMsm20wQRuWVCM+C7b+C5yyE6hSsYk6Yj\n";
    privKey+="nPr4vPlxXzrw7asl3wVVXoCG1fsVImjmD0uFCztBAoGANHtVWdJRg3oF5N74lLPg\n";
    privKey+="fgCJHaAzKyQ8OQCb8MyeQnpYfSj8ZBgv+L/3FJHKnJ715v0Zqia+AG5R2yn3mFdE\n";
    privKey+="Lp/kW72LhX7qi9Q5mNCMJImsRE2aP+aYRGt152J8T9YkXDB34ggugdPCct3nWhZ2\n";
    privKey+="075quKIzYikPs2AWTEP+u9UCgYBF/P+vt2EVyPTetuqSd18668Mz+RR0ZNSqPQJ2\n";
    privKey+="xkJMtiR5ld0oZtTUCKKMThzfk/gDGER6crkIQXCB6EVyFivaRwGIEtN1r4HE6r9/\n";
    privKey+="itgeZuEuJA9HR3LJ62zh+v3cyhgWNvocmklqkOIi41Nil7gSU+XdtzM+2AMaMtwG\n";
    privKey+="tYUhgQKBgByYCXu3+j0+QYHg2Wwu8sNUXC8h+7hcDGk02Qh3J67L89RR21iyODeZ\n";
    privKey+="QndPEQc8soBLSKH0FxrMaROsMMgxpZzxwWV50LFFiJvnmEOG5dDuZgLpz1VPVVpe\n";
    privKey+="j/MpwqAanoW4wMst+G+fVyfdoMXHSu98m1Wx8npqHD1OBY/LKePK\n";
    privKey+="-----END RSA PRIVATE KEY-----\n";    
    
    appPath = request.folder
    prikeyfile = os.path.join(appPath, 'static/assets',keyfile)    

    
    with open(prikeyfile, mode='rb') as privatefile:
        privKey = privatefile.read()
    
    rsapvtkey = OpenSSL.crypto.load_privatekey(crypto.FILETYPE_PEM, privKey)
    
    #rsapvtkey = rsa.PrivateKey._load_pkcs1_pem(keydata)
    
    #obj = OpenSSL.crypto.X509.get_signature_algorithm

    #rsapvtkey = rsa.PrivateKey.load_pkcs1(provKey)
    #crypto = rsa.encrypt(message, rsapvtkey)
    
    
    #m = hashlib.sha512()
    #hashkey = m.update( message )
    #hashkey= m.hexdigest()
     
        

    
    signature = OpenSSL.crypto.sign(rsapvtkey, message,'sha512' )
    
   
    #signature = rsa.sign(message, rsapvtkey, 'SHA-512')
    
    signhex = bytetohex(signature)
    signhex = signhex.replace(" ","").lower()
    #signbyte = hextobyte(sign64)
    
  
    

    return signhex

def generateHashForShopSe(key, message):
    
    
    bkey = key.encode()   
    message = message.encode()    
    signature = hmac.new(bkey, message, hashlib.sha256).hexdigest()
   
  
    

    return signhex

#{"rrn": "425847096720", 
#"txn_response_msg": "SUCCESS", 
#"dia_secret": "9D8079D62F7AC619DA6FB8D747CCB2CEAAA36DABADEB4ED1EBD91EC5D0FB456B", 
#"captured_amount_in_paisa": "125035", 
#"pine_pg_txn_status": "4", 
#"salted_card_hash": "B6B6A7CE1E6E2AA0DD7C028385446A3BBADCEE026A283859C69F5D2B8CC645AD", 
#"card_holder_name": "HDFC TEST", 
#"parent_txn_status": "", 
#"amount_in_paisa": "125035", 
#"acquirer_name": "HDFC", 
#"auth_code": "999999", 

#"udf_field_4": "paymentid", 
#"udf_field_1": "memberid", 
#"udf_field_2": "providerid", 
#"udf_field_3": "treatmentid", 
#"dia_secret_type": "SHA256", 
#"masked_card_number": "401200******1112", 
#"payment_mode": "1", 
#"merchant_id": "106598", 
#"txn_response_code": "1", 
#"parent_txn_response_code": "", 
#"merchant_access_code": "4a39a6d4-46b7-474d-929d-21bf0e9ed607", 
#"pine_pg_transaction_id": "7241669", 
#"parent_txn_response_message": "", 
#"txn_completion_date_time": "27/08/2021 07:27:16 AM", 
#"refund_amount_in_paisa": "0", 
#"unique_merchant_txn_id": "ORDER_XXX"}
def test_callback():
    i = 0
    
    return dict()

def pinelabs_payment_callback():
    
    logger.loggerpms2.info("Enter Pinelabs Payment Callback " + json.dumps(request.vars))
    
    reqobj = {}
    params = request.vars
    keys = params.keys()
    pvars = ""
    
    for key in keys:
        if(key == 'signature'):
            continue
        reqobj[key] = params[key]
    
    #get paymentid
    unique_merchant_txn_id = common.getkeyvalue(request.vars,"unique_merchant_txn_id","") 
    strarr = unique_merchant_txn_id.split('_')
    paymentid = 0 if(len(strarr)<=1) else int(common.getid(strarr[1]))
    p = db((db.payment.id == paymentid)).select() 
    tplanid = int(common.getid(p[0].treatmentplan)) if(len(p) != 0) else 0
    memberid = int(common.getid(p[0].patientmember)) if(len(p) != 0) else 0
    providerid = int(common.getid(p[0].provider)) if(len(p) != 0) else 0 
    providerinfo  = getproviderinformation(providerid)
    


    plbobj = mdppinelabs.PineLabs(db)
    rsp = json.loads(plbobj.callback_transaction(reqobj))
    logger.loggerpms2.info("Pinelabs-Return Callback Transaction=>>" + json.dumps(rsp) + " " + str(paymentid))
    
    
    paymentobj = mdppayment.Payment(db, providerid)
    receiptobj = json.loads(paymentobj.paymentreceipt(paymentid))
    logger.loggerpms2.info("Pine Labs - Exit Payment Receipt " + json.dumps(receiptobj))
    returnurl = URL("admin","logout") 
    
    
    dttodaydate = common.getISTFormatCurrentLocatTime()
    todaydate = dttodaydate.strftime("%d/%m/%Y")

    
      
    doctortitle = ''
    doctorname = ''
    treatment = ''
    chiefcomplaint = ''
    description = ''
    otherinfo = ''

    providerid = 0
    treatmentid = 0
    tplanid = 0
    patientinfo = None
    hmopatientmember = False
    
    r = db(db.vw_fonepaise.paymentid == paymentid).select()
    if(len(r)>0):
        
        treatmentid = int(common.getid(r[0].treatmentid))
        tplanid = int(common.getid(r[0].tplanid))
        providerid = int(common.getid(r[0].providerid))
        patientinfo = getpatientinformation(int(common.getid(r[0].patientid)),int(common.getid(r[0].memberid)))
        hmopatientmember = patientinfo["hmopatientmember"]
        
        doctortitle = common.getstring(r[0].doctortitle)
        doctorname  = common.getstring(r[0].doctorname)


        treatment = common.getstring(r[0].treatment)
        description = common.getstring(r[0].description)
        chiefcomplaint = common.getstring(r[0].chiefcomplaint)
        otherinfo = chiefcomplaint


    paymentref = ""
    paymentdate = dttodaydate
    paymenttype = ""
    paymentdetail = ""
    paymentmode = ""
    cardtype = ""
    merchantid = ""
    merchantdisplay = ""
    invoice = ""
    invoiceamt = 0.00
    amount = 0.00
    fee = 0.00
    status = "S"
    chequeno = ""
    bankname= ""
    accountname = ""
    accountno = ""
    error = ""
    errormssg = ""
    
    p = db(db.payment.id == paymentid).select()

    
    if(len(p)>0):
        paymentref = p[0].fp_paymentref #order id
        paymentdate = (p[0].fp_paymentdate).strftime("%d/%m/%Y") if((p[0].fp_paymentdate != None)) else todaydate
        paymenttype = p[0].fp_paymenttype
        paymentdetail = p[0].fp_paymentdetail  #shopseTxId
        paymentmode = p[0].paymentmode
        cardtype = p[0].fp_cardtype
        merchantid = p[0].fp_merchantid
        merchantdisplay = p[0].fp_merchantdisplay
        invoice = p[0].fp_invoice
        invoiceamt = float(common.getvalue(p[0].fp_invoiceamt))
        amount = float(common.getvalue(p[0].fp_amount))
        fee = float(common.getvalue(p[0].fp_fee))
        status = p[0].fp_status
        chequeno = common.getstring(p[0].chequeno)
        bankname= common.getstring(p[0].bankname)
        accountname = common.getstring(p[0].accountname)
        accountno = common.getstring(p[0].accountno)
        if(status == 'S'):
            error = ""
            errormsg = ""
        else:
            error  = common.getstring(p[0].fp_error)
            errormsg = common.getstring(p[0].fp_errormsg)
        
    #Procedure Grid
    query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True))


    fields=(db.vw_treatmentprocedure.altshortdescription, \
               db.vw_treatmentprocedure.procedurefee,\
               db.vw_treatmentprocedure.treatmentdate)
 
 
    headers={
        'vw_treatmentprocedure.altshortdescription':'Description',
        'vw_treatmentprocedure.procedurefee':'Procedure Cost',
        'vw_treatmentprocedure.treatmentdate':'Treatment Date'
    }
 
    links = None
    maxtextlengths = {'vw_treatmentprocedure.altshortdescription':200}
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
       
    formProcedure = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        paginate=10,
                        maxtextlengths=maxtextlengths,
                        orderby=None,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )  
    
             
    totpaid = 0
    tottreatmentcost  = 0
    totinspays = 0    
    totaldue = 0
    
    
    if(status == 'S'):
        paytm = json.loads(account._calculatepayments(db,tplanid))
        tottreatmentcost= paytm["totaltreatmentcost"]
        totinspays= paytm["totalinspays"]
        totpaid=paytm["totalpaid"] 
        totaldue = paytm["totaldue"]
        
        otherinfo  = otherinfo + " Total Cost " + str(paytm["totalcopay"]) + " Plan Benefits = " + str(paytm["totalcompanypays"]) + " Super Wallet = " + str(paytm["totalwalletamount"]) + " Discount = " + str(paytm["discount_amount"])

    return dict(formProcedure=formProcedure,\
                todaydate = todaydate,\
                providerid = providerid,
                practicename = providerinfo["practicename"],\
                providername  = providerinfo["providername"],\
                provideregnon = providerinfo["providerregno"],\
                practiceaddress1 = providerinfo["practiceaddress1"],\
                practiceaddress2 = providerinfo["practiceaddress2"],\
                practicephone = providerinfo["practicephone"],\
                practiceemail =providerinfo["practiceemail"],\
                patientname = patientinfo["patientname"]  if(patientinfo != None) else "",\
                patientmember = patientinfo["patientmember"]   if(patientinfo != None) else "",\
                patientemail = patientinfo["patientemail"]  if(patientinfo != None) else "",\
                patientcell = patientinfo["patientcell"]  if(patientinfo != None) else "",\
                patientgender=  patientinfo["patientgender"]  if(patientinfo != None) else "",\
                patientage =patientinfo["patientage"]  if(patientinfo != None) else "",\
                patientaddress =patientinfo["patientaddress"]  if(patientinfo != None) else "",\
                groupref = patientinfo["groupref"]  if(patientinfo != None) else "",\
                companyname = patientinfo["companyname"]  if(patientinfo != None) else "",\
                planname  = patientinfo["planname"]  if(patientinfo != None) else "",\
                paymentref =paymentref,\
                paymentdate = paymentdate,\
                paymenttype = paymenttype,\
                paymentdetail = paymentdetail,\
                paymentmode = paymentmode,\
                cardtype = cardtype,\
                merchantid = merchantid,\
                merchantdisplay = merchantdisplay,\
                invoice = invoice,\
                invoiceamt = invoiceamt,\
                amount = amount,\
                fee = fee,\
                totaldue=totaldue,\
                status = status,\
                doctorname  = doctorname,\
                treatment = treatment,\
                description =description,\
                chiefcomplaint = chiefcomplaint,\
                otherinfo=otherinfo,\
                chequeno = chequeno,\
                bankname= bankname,\
                accountname = accountname,\
                accountno = accountno,\
                error = error,\
                errormsg=errormssg,\
                returnurl=returnurl
                )

    
#http://13.71.115.17/my_pms2/payment/shopse_payment_callback?
#orderId=TRBLRGSP12710003_1748&shopSeTxnId=S22062112450579710&
#status=success&statusCode=0&statusMessage=Transaction%20successful&
#currentTime=1624365999529&
#signature=JDwshy9b%2BH4y09cUJwxbycKJdbE2g5lQ8AA%2B5EdFbUo%3D
#callback_transaction
def shopse_payment_callback():
    
    logger.loggerpms2.info("Enter Shopse Payment Callback " + json.dumps(request.vars))
    reqobj = {}
    
    
    params = request.vars
    
    keys = params.keys()
    
    for key in keys:
        if(key == 'signature'):
            continue
        reqobj[key] = params[key]
        
    #sig = generateHashForShopSe('l42eh9thfp2rxbjxtlkt2ch57aqxsg', 'currentTime%3D1624365999529%26orderId%3DTRBLRGSP12710003_1748%26shopSeTxnId%3DS22062112450579710%26status%3Dsuccess%26statusCode%3D0%26statusMessage%3DTransaction+successful')
    
    
   
    
    encryptObj = mdpshopse.Shopse(db)
    encryptrsp = encryptObj.encrypt_sha256_shopse(reqobj)
    encryptrsp = json.loads(encryptrsp)
    
    encryptrsp = encryptrsp["encrypt"]
    signature = urllib.quote_plus(request.vars.signature)  if "signature" in request.vars else ""

    #for now we are not checking for ShopSeTxnId
    #p = db((db.payment.fp_paymentref == request.vars.orderId) & (db.payment.fp_paymentdetail ==request.vars.shopSeTxnId )).select(db.payment.id,db.payment.provider)
    p = db((db.payment.fp_paymentref == request.vars.orderId)).select(db.payment.id,db.payment.provider)
    
    paymentid = int(common.getid(p[0].id)) if(len(p) >= 1) else 0
    providerid = int(common.getid(p[0].provider)) if(len(p) >= 1) else 0
    providerinfo  = getproviderinformation(providerid)
    
    r = db(db.vw_fonepaise.paymentid == paymentid).select()
    patientinfo = None
    if(len(r)>0):
        patientinfo = getpatientinformation(int(common.getid(r[0].patientid)),int(common.getid(r[0].memberid)))

    
    if(encryptrsp == signature):
        logger.loggerpms2.info("ShopSe-Enter Callback Transaction Sign Match ==>" + signature + "\n" + json.dumps(reqobj) + " " + str(paymentid))
        shopseobj = mdpshopse.Shopse(db)
        rsp = json.loads(shopseobj.callback_transaction(reqobj))
        logger.loggerpms2.info("ShopSe-Return Callback Transaction=>>" + json.dumps(rsp) + " " + str(paymentid))
        
        
        paymentobj = mdppayment.Payment(db, providerid)
        receiptobj = json.loads(paymentobj.paymentreceipt(paymentid))
        logger.loggerpms2.info("Shopse - Exit Payment Receipt " + json.dumps(receiptobj))
        returnurl = URL("admin","logout") 
        
        
        dttodaydate = common.getISTFormatCurrentLocatTime()
        todaydate = dttodaydate.strftime("%d/%m/%Y")
    
        
          
        doctortitle = ''
        doctorname = ''
        treatment = ''
        chiefcomplaint = ''
        description = ''
        otherinfo = ''
    
        providerid = 0
        treatmentid = 0
        tplanid = 0
        patientinfo = None
        hmopatientmember = False
        
        r = db(db.vw_fonepaise.paymentid == paymentid).select()
        if(len(r)>0):
            
            treatmentid = int(common.getid(r[0].treatmentid))
            tplanid = int(common.getid(r[0].tplanid))
            providerid = int(common.getid(r[0].providerid))
            providerinfo  = getproviderinformation(providerid)
            patientinfo = getpatientinformation(int(common.getid(r[0].patientid)),int(common.getid(r[0].memberid)))
            hmopatientmember = patientinfo["hmopatientmember"]
            
            doctortitle = common.getstring(r[0].doctortitle)
            doctorname  = common.getstring(r[0].doctorname)
    
    
            treatment = common.getstring(r[0].treatment)
            description = common.getstring(r[0].description)
            chiefcomplaint = common.getstring(r[0].chiefcomplaint)
            otherinfo = chiefcomplaint
    
    
        paymentref = ""
        paymentdate = dttodaydate
        paymenttype = ""
        paymentdetail = ""
        paymentmode = ""
        cardtype = ""
        merchantid = ""
        merchantdisplay = ""
        invoice = ""
        invoiceamt = 0.00
        amount = 0.00
        fee = 0.00
        status = "S"
        chequeno = ""
        bankname= ""
        accountname = ""
        accountno = ""
        error = ""
        errormssg = ""
        
        p = db(db.payment.id == paymentid).select()
    
        
        if(len(p)>0):
            paymentref = p[0].fp_paymentref #order id
            paymentdate = (p[0].fp_paymentdate).strftime("%d/%m/%Y") if((p[0].fp_paymentdate != None)) else todaydate
            paymenttype = p[0].fp_paymenttype
            paymentdetail = p[0].fp_paymentdetail  #shopseTxId
            paymentmode = p[0].paymentmode
            cardtype = p[0].fp_cardtype
            merchantid = p[0].fp_merchantid
            merchantdisplay = p[0].fp_merchantdisplay
            invoice = p[0].fp_invoice
            invoiceamt = float(common.getvalue(p[0].fp_invoiceamt))
            amount = float(common.getvalue(p[0].fp_amount))
            fee = float(common.getvalue(p[0].fp_fee))
            status = p[0].fp_status
            chequeno = common.getstring(p[0].chequeno)
            bankname= common.getstring(p[0].bankname)
            accountname = common.getstring(p[0].accountname)
            accountno = common.getstring(p[0].accountno)
            if(status == 'S'):
                error = ""
                errormsg = ""
            else:
                error  = common.getstring(p[0].fp_error)
                errormsg = common.getstring(p[0].fp_errormsg)
            
        #Procedure Grid
        query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True))
    
    
        fields=(db.vw_treatmentprocedure.altshortdescription, \
                   db.vw_treatmentprocedure.procedurefee,\
                   db.vw_treatmentprocedure.treatmentdate)
     
     
        headers={
            'vw_treatmentprocedure.altshortdescription':'Description',
            'vw_treatmentprocedure.procedurefee':'Procedure Cost',
            'vw_treatmentprocedure.treatmentdate':'Treatment Date'
        }
     
        links = None
        maxtextlengths = {'vw_treatmentprocedure.altshortdescription':200}
        
        exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
           
        formProcedure = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            maxtextlengths=maxtextlengths,
                            orderby=None,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            searchable=False,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            user_signature=True
                           )  
        
                 
        totpaid = 0
        tottreatmentcost  = 0
        totinspays = 0    
        totaldue = 0
        
        
        if(status == 'S'):
            paytm = json.loads(account._calculatepayments(db, tplanid))
            tottreatmentcost= paytm["totaltreatmentcost"]
            totinspays= paytm["totalinspays"]
            totpaid=paytm["totalpaid"] 
            totaldue = paytm["totaldue"]
    else:
        dttodaydate = common.getISTFormatCurrentLocatTime()
        todaydate = dttodaydate.strftime("%d/%m/%Y")        
        
        formProcedure = None
        paymentref = ""
        paymentdate = dttodaydate
        paymenttype = ""
        paymentdetail = ""
        paymentmode = ""
        cardtype = ""
        merchantid = ""
        merchantdisplay = ""
        invoice = ""
        invoiceamt = 0.00
        amount = 0.00
        fee = 0.00
        status = "F"
        chequeno = ""
        bankname= ""
        accountname = ""
        accountno = ""
        error = ""
        errormssg = "Signature Mismatch"
        tottreatmentcost= 0
        totinspays= 0
        totpaid=0
        totaldue = 0
        doctorname  = ""
        treatment = ""
        description =""
        chiefcomplaint = ""
        otherinfo=""
      
  
      
     
   
        
        
        
   
    
    
    returnurl = request.vars.returnurl

    return dict(formProcedure=formProcedure,\
                todaydate = todaydate,\
                providerid = providerid,
                practicename = providerinfo["practicename"],\
                providername  = providerinfo["providername"],\
                provideregnon = providerinfo["providerregno"],\
                practiceaddress1 = providerinfo["practiceaddress1"],\
                practiceaddress2 = providerinfo["practiceaddress2"],\
                practicephone = providerinfo["practicephone"],\
                practiceemail =providerinfo["practiceemail"],\
                patientname = patientinfo["patientname"]  if(patientinfo != None) else "",\
                patientmember = patientinfo["patientmember"]   if(patientinfo != None) else "",\
                patientemail = patientinfo["patientemail"]  if(patientinfo != None) else "",\
                patientcell = patientinfo["patientcell"]  if(patientinfo != None) else "",\
                patientgender=  patientinfo["patientgender"]  if(patientinfo != None) else "",\
                patientage =patientinfo["patientage"]  if(patientinfo != None) else "",\
                patientaddress =patientinfo["patientaddress"]  if(patientinfo != None) else "",\
                groupref = patientinfo["groupref"]  if(patientinfo != None) else "",\
                companyname = patientinfo["companyname"]  if(patientinfo != None) else "",\
                planname  = patientinfo["planname"]  if(patientinfo != None) else "",\
                paymentref =paymentref,\
                paymentdate = paymentdate,\
                paymenttype = paymenttype,\
                paymentdetail = paymentdetail,\
                paymentmode = paymentmode,\
                cardtype = cardtype,\
                merchantid = merchantid,\
                merchantdisplay = merchantdisplay,\
                invoice = invoice,\
                invoiceamt = invoiceamt,\
                amount = amount,\
                fee = fee,\
                totaldue=totaldue,\
                status = status,\
                doctorname  = doctorname,\
                treatment = treatment,\
                description =description,\
                chiefcomplaint = chiefcomplaint,\
                otherinfo=otherinfo,\
                chequeno = chequeno,\
                bankname= bankname,\
                accountname = accountname,\
                accountno = accountno,\
                error = error,\
                errormsg=errormssg,\
                returnurl=returnurl
                )
    
  

def make_payment_pinelabs():
    
    logger.loggerpms2.info("Enter Pine Labs Payment " + json.dumps(request.vars))
    providerid = int(common.getstring(request.vars.providerid))
    returnurl = URL('payment', 'list_payment', vars=dict(page=1, providerid=providerid))
    
    paymentid = int(common.getid(request.vars.paymentid))
    paymentmode = common.getstring(request.vars.paymentmod)
    paymentamount = float(common.getvalue(request.vars.invoiceamt))    #payment amount is in paise
   

    vwfp = db(db.vw_fonepaise.paymentid == paymentid).select()
    treatmentid = int(common.getid(vwfp[0].treatmentid))
    treatment = (common.getstring(vwfp[0].treatment)) if(len(vwfp) ==1 ) else "TR_" + common.getstringfromdate(common.getISTFormatCurrentLocatTime(),"%d/%m/%Y %H:%M:%S")
    
    memberid = int(common.getid(vwfp[0].memberid)) if(len(vwfp) == 1) else 0
    pats = db(db.patientmember.id == memberid).select()

    
    
    reqobj={
       "action":"pinelabs_payment",
       "treatment":treatment,
       "amount":paymentamount,
       "cell":str(pats[0].cell),
       "email":str(pats[0].email),
       "firstname":str(pats[0].fname) if(len(pats)==1) else "",
       "lastname":str(pats[0].lname) if(len(pats)==1) else "",
       "member":pats[0].patientmember,
       "treatmentid":str(treatmentid),
       "memberid":str(memberid),
       "paymentid":str(paymentid),
       "providerid":str(providerid)
    }    
    
    #call pinelabs Payment API
    obj = mdppinelabs.PineLabs(db)
    rspobj = json.loads(obj.pinelabs_payment(reqobj))
    message = "success"
    if(rspobj["result"] == "success"):
        redirect(rspobj["redirect_url"])
    else:
        message = rspobj["error_message"]
        
         
    logger.loggerpms2.info("Exit Pine Labs Payment " + json.dumps(rspobj))
    return dict(message = message,returnurl=returnurl)


def make_payment_shopse():
    
    logger.loggerpms2.info("Enter Shopse Payment")
    
    providerid = int(common.getstring(request.vars.providerid))

    returnurl = URL('payment', 'list_payment', vars=dict(page=1, providerid=providerid))
    
    #payment, member info
    paymentid = int(common.getid(request.vars.paymentid))
    paymentmode = common.getstring(request.vars.paymentmod)
    paymentamount = float(common.getvalue(request.vars.invoiceamt))
    paymentamount = str(paymentamount if(paymentamount != 0) else 10000.0)   #this has to be defaulted to 0 in actual scenario
    
    vwfp = db(db.vw_fonepaise.paymentid == paymentid).select()
    
    treatmentid = int(common.getid(vwfp[0].treatmentid))
    treatment = (common.getstring(vwfp[0].treatment)) if(len(vwfp) ==1 ) else "TR_" + common.getstringfromdate(common.getISTFormatCurrentLocatTime(),"%d/%m/%Y %H:%M:%S")
    #treatment = (common.getstring(vwfp[0].treatment))[:(20-len(str(paymentid)))] if(len(vwfp) ==1 ) else "TR_" + common.getstringfromdate(common.getISTFormatCurrentLocatTime(),"%d/%m/%Y %H:%M:%S")
    
    #reference_no = (common.getstring(vwfp[0].invoice))[:(20-len(str(paymentid)))] +"_" + str(paymentid) if(len(vwfp) == 1) else "0000_REFNO"
    reference_no = (common.getstring(vwfp[0].invoice)) +"_" + str(paymentid) if(len(vwfp) == 1) else "0000_REFNO"
    reference_no=reference_no if(reference_no != "") else "0000_REFNO"
    
    memberid = int(common.getid(vwfp[0].memberid)) if(len(vwfp) == 1) else 0
    pats = db(db.patientmember.id == memberid).select()

    u = db(db.shopsee_properties.id > 0).select(db.shopsee_properties.shopsee_returnURL)
    
    
    #call Shopsee API
    reqobj={
        "action":"create_transaction",
        "treatment":treatment,
        "paymentid":paymentid,
        "amount":paymentamount,
        "mobile":str(pats[0].cell),
        "email":str(pats[0].email),
        "firstName":str(pats[0].fname) if(len(pats)==1) else "",
        "lastName":str(pats[0].lname) if(len(pats)==1) else "",
        "address": {
        "line1": pats[0].address1 if(len(pats)==1) else "331-332 Ganpat Plaza",
        "line2": pats[0].address2 if(len(pats)==1) else "MI Road",
        "city": pats[0].city if(len(pats)==1) else "Jaipur",
        "state": pats[0].st if(len(pats)==1) else "Rajasthan",
        "country":"India",
        "pincode":pats[0].pin if(len(pats)==1) else "302001",
        },
        
        "customParams": {
        "providerid":providerid,
        "paymentid":paymentid,
        "treatmentid":treatmentid,
        }    
        
        
    }

    #call create transaction API
    obj = mdpshopse.Shopse(db)
    rspobj = json.loads(obj.create_transaction(reqobj))
    
    message = "success"
    if(rspobj["result"] == "success"):
        redirect(rspobj["paymentRedirectUrl"])
    else:
        message = rspobj["error_message"]


    
     
    return dict(message=message,returnurl=returnurl)


#this method is called when Online Payment : create_payment->update_payment->make_payment_hdfc->HDFC site->payment_success (callback).
#redirect(URL('payment','make_payment',vars=dict(paymentid=paymentid,paymentmode=paymentmode,invoiceamt=paymentamount,returnurl=returnurl)))

def make_payment_hdfc():
    
    #secret_key='d67fa952ec2f66c394d3192f17e01550'
    #account_id='16428'
    #address='A-16 Indraprasth Apartments'
    #amount='12.34'
    #channel='10'
    #city='Bengalaru'
    #country='IND'
    #currency='INR'
    #description='Test Payment'
    #email='test@gmail.com'
    #mode='LIVE'
    #name='imtiazbengali@hotmail.com'
    #phone='9819877579'
    #postal_code='560004'
    #reference_no='IMB001'
    #return_url='http://turningcloud.com/response.jsp'
    #ship_address='test'
    #ship_city='Mumbai'
    #ship_country='IND'
    #ship_name='test'
    #ship_phone='9840123456'
    #ship_postal_code='410251'
    #ship_state='Mumbai'
    #state='test'


    #secret_key='d67fa952ec2f66c394d3192f17e01550'
    #account_id='16428'
    #address='A-16 Indraprasth Apartments'
    #amount='120.34'
    #channel='10'
    #city='Bengalaru'
    #country='IND'
    #currency='INR'
    #description='Test Payment'
    #email='imtiazbengali@hotmail.com'
    #mode='LIVE'
    #name='Imtiyaz Bengali'
    #phone='9819877579'
    #postal_code='560004'
    #reference_no='IMB001'
    #return_url='http://turningcloud.com/response.jsp'
    #ship_address='A-16 Indraprasth Apartments'
    #ship_city='Bengalaru'
    #ship_country='IND'
    #ship_name='Imtiyaz Bengali'
    #ship_phone='9819877579'
    #ship_postal_code='560004'
    #ship_state='Karnataka'
    #state='Karnataka'


    #hdfc specific
    secret_key='d67fa952ec2f66c394d3192f17e01550'
    account_id='16428'
    country='IND'
    currency='INR'
    channel = '10'
    mode = 'LIVE'
    description = 'Payment'
    
    ship_country = 'IND'
    
    
    #payment, member info
    paymentid = int(common.getid(request.vars.paymentid))
    paymentmode = common.getstring(request.vars.paymentmod)
    paymentamount = float(common.getvalue(request.vars.invoiceamt))
    memberid = 0
    reference_no = ""
    
    vwfp = db(db.vw_fonepaise.paymentid == paymentid).select()
    

    memberid = int(common.getid(vwfp[0].memberid)) if(len(vwfp) == 1) else 0
    strpaymentid = "_" + str(paymentid)
    fill = 20 - len(strpaymentid)   #HDFC max refrenece_no length -to 20 
    
    reference_no = (common.getstring(vwfp[0].invoice))[:fill] +"_" + strpaymentid if(len(vwfp) == 1) else "0000_REFNO"
    reference_no=reference_no if(reference_no != "") else "0000_REFNO"
    
    pats = db(db.patientmember.id == memberid).select()
    name = pats[0].fname + " " + pats[0].lname if(len(pats) == 1) else "PATNAME"
    name=name if(name != "") else "PATNAME"
    
    address = pats[0].address1 if(len(pats) == 1) else "ADDRESS"
    address=address if ((address != None) & (address != "")) else "ADDRESS"    
    
    phone = pats[0].cell if(len(pats) == 1) else "0000000000"
    phone=phone if ((phone != None) & (phone != "")) else "0000000000"    
      
    
    city = pats[0].city if(len(pats) == 1) else "Bengalaru"
    city=city if((city != None) & (city != "")) else "Bengalaru"    

    email = pats[0].email if(len(pats) == 1) else "x@gmail.com"
    email=email if((email != None) & (email != "")) else "x@gmail.com"    
    
    postal_code = pats[0].pin if(len(pats) == 1) else "00000000"
    postal_code=postal_code if((postal_code != None) & (postal_code != "")) else "00000000"    
    
    ship_address = pats[0].address1 if(len(pats) == 1) else "ADDRESS"
    ship_address=ship_address if(ship_address != "") else "ADDRESS"    
    
    ship_city = pats[0].city if(len(pats) == 1) else "Bengalaru"
    ship_city=ship_city if((ship_city != None) & (ship_city != "")) else "Bengalaru"    
    
    ship_state = pats[0].st if(len(pats) == 1) else "Karnataka"
    ship_state=ship_state if ((ship_state != None) & (ship_state != "")) else "Karnataka"    
    
    ship_postal_code = pats[0].pin if(len(pats) == 1) else "00000000"
    ship_postal_code=ship_postal_code if((ship_postal_code != None) & (ship_postal_code != "")) else "00000000"    
    
    ship_name = pats[0].fname + " " + pats[0].lname if(len(pats) == 1) else "PATNAME"
    ship_name=ship_name if(ship_name != "") else "PATNAME"    
    
    ship_phone = pats[0].cell if(len(pats) == 1) else "0000000000"
    ship_phone=ship_phone if((ship_phone != None) & (ship_phone != "")) else "0000000000"    
    
    state = pats[0].st if(len(pats) == 1) else "Karnataka"
    state=state if((state != None) & (state != "")) else "Karnataka"    
    
    
    p = db(db.payment.id == paymentid).select(db.payment.amount)
    amount = float(common.getvalue(p[0].amount)) if(len(p)  == 1) else 0.0
    amount = str(amount if(amount != 0) else 1.0)
    
    u = db(db.urlproperties.id > 0).select(db.urlproperties.fp_callbackurl)
    return_url = u[0].fp_callbackurl
    
    hashkey = account.generateHash(secret_key,account_id,address,amount,channel,city,country,currency,description,email,mode, \
                            name,phone,postal_code,reference_no,return_url,ship_address,ship_city,ship_country,ship_name,ship_phone,ship_postal_code,ship_state,state)

    
    logger.loggerpms2.info("HashKey = " + hashkey)
    
    return dict(\
        secret_key=secret_key,\
        account_id=account_id,\
        address=address,\
        amount=amount,\
        channel=channel,\
        city=city,\
        country=country,\
        currency=currency,\
        description=description,\
        email=email,\
        mode=mode,\
        name=name,\
        phone=phone,\
        postal_code=postal_code,\
        reference_no=reference_no,\
        return_url=return_url,\
        ship_address=ship_address,\
        ship_city=ship_city,\
        ship_country=ship_country,\
        ship_name=ship_name,\
        ship_phone=ship_phone,\
        ship_postal_code=ship_postal_code,\
        ship_state=ship_state,\
        state=state,\
        secure_hash=hashkey\
        )

def make_payment():
    
    r = db(db.urlproperties.id>0).select()
    
    #generate sign (hash of "api_key#id#merchand_id#invoice#invoice_amt#")
    #privKey = common.getstring(r[0].fp_privatekey)
    api_key = common.getstring(r[0].fp_apikey)
    xid = common.getstring(r[0].fp_id)
    merchantid = common.getstring(r[0].fp_merchantid)
    merchantdisplay = common.getstring(r[0].fp_merchantdisplay)
    callback_url = common.getstring(r[0].fp_callbackurl)
    callback_failure_url = common.getstring(r[0].fp_callbackfailureurl)
    payurl = common.getstring(r[0].fp_produrl)
    keyfile = common.getstring(r[0].fp_privatekey)
    
    paymentid = int(common.getid(request.vars.paymentid))
    
    r = db(db.vw_fonepaise.paymentid==paymentid).select()
    invoice = common.getstring(r[0].invoice)+"_" + str(paymentid)
    invoiceamt =  "{:.2f}".format(common.getstring(r[0].invoiceamt))
    mobileno = common.getstring(r[0].mobileno)
    email = common.getstring(r[0].email)
    notes = common.getstring(r[0].notes)
    providername = common.getstring(r[0].providername)
    practicename = common.getstring(r[0].practicename)
    fullname = common.getstring(r[0].fullname)  #fn + ln
    xstr = api_key + "#" + xid +"#"+ merchantid + "#" + invoice + "#" + invoiceamt + "#"
    xhash = generateHashForMessage(keyfile,xstr);    
    
    returnurl = common.getstring(request.vars.returnurl)
    
    data = {"paymentid" :  str(paymentid),  "returnurl" : returnurl, "provider":providername, "patient":fullname}
    
    jsondata = json.dumps(data)
    
    return dict(xid=xid,payurl=payurl, merchantid=merchantid,merchantdisplay=merchantdisplay,invoice=invoice,invoiceamt=invoiceamt,mobileno=mobileno,email=email,\
                callbackurl=callback_url,callbackfailureurl=callback_failure_url,xhash=xhash,addlinfo=jsondata)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def commit_payment():
    
    provdict = common.getprovider(auth,db)    
    providerid = provdict["providerid"]       
    providername=provdict["providername"]

    paymentid = int(common.getid(request.vars.paymentid))  
    
    page         = int(common.getpage(request.vars.page))
    memberid     = int(common.getid(request.vars.memberid))
    patientid     = int(common.getid(request.vars.patientid))
    tplanid      = int(common.getid(request.vars.tplanid))
    patient     = common.getstring(request.vars.patient) 
    fullname    = common.getstring(request.vars.fullname)
    
    returnurl = URL('admin','providerhome')
    
    
    
    form = FORM.confirm('Yes?',{'No':returnurl})
    
    if form.accepted:    
        
        if(paymentid > 0):
            payments = db((db.payment.id==paymentid) & (db.payment.paymentcommit==False) & (db.payment.is_active == True)).select()
        else:
            if(tplanid >0):
                payments = db((db.payment.treatmentplan==tplanid) &(db.payment.provider==providerid) & (db.payment.paymentcommit==False) & (db.payment.is_active == True)).select()
            elif(memberid > 0):
                payments = db((db.payment.provider==providerid) & (db.payment.patientmember == memberid) &(db.payment.paymentcommit==False) & (db.payment.is_active == True)).select()
            else:
                payments = db((db.payment.provider==providerid) & (db.payment.paymentcommit==False) & (db.payment.is_active == True)).select()
                
        for payment in payments:
            
            tp = db(db.treatmentplan.id == payment.treatmentplan).select()
        
            if(payment.paymenttype == 'Treatment'):
                totalpaid      = common.getvalue(tp[0].totalpaid) + common.getvalue(payment.amount)
            else:
                totalpaid      = common.getvalue(tp[0].totalpaid)
    
            if(payment.paymenttype  == 'Copay'):
                totalcopaypaid      = common.getvalue(tp[0].totalcopaypaid) + common.getvalue(payment.amount)
            else:
                totalcopaypaid      = common.getvalue(tp[0].totalcopaypaid)
    
            
            if(payment.paymenttype  == 'Insurance'):
                totalinspaid      = common.getvalue(tp[0].totalinspaid) + common.getvalue(payment.amount)
            else:
                totalinspaid      = common.getvalue(tp[0].totalinspaid)
    
        
            totaltreatmentcost = common.getvalue(tp[0].totaltreatmentcost)
        
            totaldue = totaltreatmentcost - (totalpaid + totalcopaypaid + totalinspaid)
    
            db(db.treatmentplan.id == payment.treatmentplan).update(totalpaid=totalpaid,totalcopaypaid=totalcopaypaid,totalinspaid=totalinspaid,totaldue=totaldue)
            db(db.payment.id == payment.id).update(paymentcommit = True)
            db.commit()
            
            session.flash = "All open payments committed!"
        redirect(returnurl)
        
        
    return dict(form=form,returnurl=returnurl,providerid=provdict["providerid"],providername=provdict["providername"],page=0)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def getpaymentsgrid(providerid,  xpatientname, page,returnurl):

    #Get Payments for the patient (or part patient)
    if(xpatientname != ""):
        query = ((db.vw_payments.is_active==True) & \
                 (db.vw_payments.providerid == providerid) & \
                 (db.vw_payments.patientname.like('%' + xpatientname + '%')))
    else:
        query = ((db.vw_payments.is_active==True) & \
                 (db.vw_payments.providerid == providerid))
        
    
    fields=( db.vw_payments.id,db.vw_payments.memberid, db.vw_payments.patientid, db.vw_payments.treatmentid ,\
             db.vw_payments.providerid,db.vw_payments.patientname, \
             db.vw_payments.treatmentdate, db.vw_payments.treatment, db.vw_payments.shortdescription, \
             db.vw_payments.totaltreatmentcost, db.vw_payments.totalinspays, db.vw_payments.totalcopay, \
             db.vw_payments.totalpaid,db.vw_payments.totaldue
             )
    
    
    
    db.vw_payments.id.readable = False
    db.vw_payments.id.writable = False
    
    db.vw_payments.treatmentid.readable = False
    db.vw_payments.treatmentid.writable = False
    
    db.vw_payments.memberid.readable = False
    db.vw_payments.memberid.writable = False    
    
    db.vw_payments.patientid.readable = False
    db.vw_payments.patientid.writable = False    
    
    db.vw_payments.providerid.readable = False
    db.vw_payments.providerid.writable = False    

    headers={'vw_payments.patientname':'Patient',
           'vw_payments.treatmentdate':'Tr. Date',
           'vw_payments.treatment':'Treatment',
           'vw_payments.shortdescription':'Procedures',
           'vw_payments.totaltreatmentcost':'Total Cost',
           'vw_payments.totalinspays':'Total Insurance',
           'vw_payments.totalcopay':'Total CoPay',
           'vw_payments.totalpaid':'Total Paid',
           'vw_payments.totaldue':'Total Due'
           }
      
    links = [\
           dict(header=CENTER("New/View Payment"), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),\
                _href=URL("payment","create_payment",vars=dict(page=1,patientname=row.patientname, tplanid=row.id,treatmentid=row.treatmentid, \
                                                               patientid=row.patientid, memberid=row.memberid,\
                                                               providerid=row.providerid,returnurl=returnurl))))),
    ]

    orderby = (~(db.vw_payments.treatmentdate) | ~(db.vw_payments.treatmentdate))
    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False,csv=False)
    
    
    maxtextlengths = {'vw_payments.shortdescription':64, 'vw_payments.patientname':32}

    
    args=[xpatientname]
    
  
    
    form = SQLFORM.grid(query=query,
               headers=headers,
               fields=fields,
               links=links,
               maxtextlengths=maxtextlengths,
               orderby=orderby,
               exportclasses=exportlist,
               paginate=10,
               links_in_grid=True,
               searchable=lambda f, k: db.vw_payments.patientname.like("%" + k + "%"),
               create=False,
               deletable=False,
               editable=False,
               details=False,
               user_signature=True
              )        
    search_input = form.element('#w2p_keywords')
    search_input.attributes.pop('_onfocus')
    
    return form



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def getpaymentgrid(tplanid,treatmentid, providerid,memberid,patientid,page,patient,fullname,providername,returnurl):

    #Get Payments for the Member
    query = ((db.vw_paymentlist.is_active == True) & (db.vw_paymentlist.paymentcommit == True) & (db.vw_paymentlist.providerid == providerid) &\
             (db.vw_paymentlist.treatmentid==treatmentid) & (db.vw_paymentlist.memberid==memberid) & \
             (db.vw_paymentlist.patientid==patientid))
    
    fields=(db.vw_paymentlist.paymentdate, db.vw_paymentlist.amount,db.vw_paymentlist.paymentmode,\
            db.vw_paymentlist.treatment,db.vw_paymentlist.fpinvoice,db.vw_paymentlist.patientname,db.vw_paymentlist.patientmember,\
            db.vw_paymentlist.treatmentid
            
            )
    
    headers={'vw_paymentlist.paymentdate':'Date',
             'vw_paymentlist.amount':'Amount',
             'vw_paymentlist.paymentmode':'Payment By',
             'vw_paymentlist.treatment':'Treatment',
             'vw_paymentlist.fpinvoice':'Invoice',
             'vw_paymentlist.patientname':'Patient'
            
             
             
            }   
   
    db.vw_paymentlist.treatmentid.readable = False
    db.vw_paymentlist.treatmentid.writable = False
    db.vw_paymentlist.patientmember.writable = False
    db.vw_paymentlist.patientmember.readable = False
    
    
     
    links = [\
           
           #dict(header=CENTER("New"), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("payment","create_payment",vars=dict(page=page,tplanid=row.tplanid,patientid=patientid, memberid=memberid,providerid=providerid,returnurl=returnurl))))),
           dict(header=CENTER("Open"), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("payment","update_payment",vars=dict(paymentid=row.id, page=page,tplanid=tplanid,treatmentid=treatmentid,patient=patient,fullname=fullname,patientid=patientid, memberid=memberid,providerid=providerid,providername=providername,returnurl=returnurl,mode="update"))))),
           dict(header=CENTER("View/Print"), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("payment","print_payment_receipt",vars=dict(paymentid=row.id, page=page,tplanid=tplanid,treatmentid=treatmentid,patient=patient,fullname=fullname,patientid=patientid, memberid=memberid,providerid=providerid,providername=providername,returnurl=returnurl,mode="update"))))),
           #dict(header='Delete',body=lambda row: A(IMG(_src="/my_pms2/static/img/png/001-rubbish-bin.png",_width=30, _height=30),_href=URL("payment","delete_payment",vars=dict(page=page,paymentid=row.id,providerid=providerid,tplanid=tplanid,memberid=memberid))))
    ]

    orderby = ~(db.vw_paymentlist.paymentdate) 
    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False,csv=False)
    maxtextlengths = {'vw_paymentlist.treatment':32, 'vw_paymentlist.patientname':32, 'vw_paymentlist.fpinvoice':32, }

    
    
    
    formA = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        maxtextlengths=maxtextlengths,
                        orderby=orderby,
                        exportclasses=exportlist,
                        paginate = 5,
                        links_in_grid = True,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )    

    #xsearch = formA.element('input',_value='Search')
    #xsearch['_class'] = 'form_details_button btn'
    #xclear = formA.element('input',_value='Clear')
    #xclear['_class'] = 'form_details_button btn'
    #xnew = formA.element('input',_value='New Search')
    #xnew['_class'] = 'form_details_button_black btn'
    #xand = formA.element('input',_value='+ And')
    #xand['_class'] =  'form_details_button_black btn'
    #xor = formA.element('input',_value='+ Or')
    #xor['_class'] = 'form_details_button_black btn'
    #xclose = formA.element('input',_value='Close')
    #xclose['_class'] = 'form_details_button_black btn'  

    
    return formA

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def xlist_payment():
    
    page = common.getpage(request.vars.page)
    
    totalcost = 0
    totalinspays = 0
    totalcopay = 0
    totalpaid = 0
    totaldue = 0
    
    memberid = 0
    patientid = 0
    treatmentid = 0
    tplanid = 0
    
    xpatientname = ""  #fname lname
    fullname  = ""
    patient = ""
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])    
    providername = provdict["providername"]    

    returnurl = URL('payment', 'list_payment', vars=dict(page=1, providerid=providerid))

   
    form = SQLFORM.factory(
                 Field('patientmember1', 'string',  default='', label='Patient'),
                 Field('xpatientmember1', 'string', default='', label='XPatient')
      )
         
    xpatientmember = form.element('#no_table_patientmember1')
    xpatientmember['_class'] = 'form-control'
    xpatientmember['_placeholder'] = 'Enter Patient Name - First Name Last Name'
    xpatientmember['_autocomplete'] = 'off'     
    
    formA = None
    if(len(request.args) >= 0):
        if(len(request.args) > 0):
            xpatientname = str(common.getstring(request.args[0])).strip().replace('_',' ')
            
        
       
        
        r = db((db.vw_memberpatientlist.fullname == xpatientname) & \
               (db.vw_memberpatientlist.providerid == providerid) & \
               (db.vw_memberpatientlist.is_active == True)).select()
        
        if(len(r) > 0):
            memberid = int(common.getid(r[0].primarypatientid))
            patientid = int(common.getid(r[0].patientid))
            memberref = common.getstring(r[0].patientmember)  #patientmember
            fullname = common.getstring(r[0].fullname)      #fname + lname
           
            patient = common.getstring(r[0].patient)    #fname + lname + patientmemebr
            if(patient == ""):
                patient = common.getstring(request.vars.xpatientmember1)        

    
           
        
        
        if(memberid >= 0):
            formA = gettreatmentgrid(providerid, xpatientname,page,returnurl)
        else:
            formA = None
            
      
        paytm = calculatepaymentsforpatient(providerid,memberid,patientid)    
        totalcost=paytm["totaltreatmentcost"]
        totalinspays=paytm["totalinspays"]
        totalcopay=paytm["totalcopay"]
        totalpaid=paytm["totalpaid"]
        totaldue=paytm["totaldue"]         
    
    if form.accepts(request,session,keepvalues=True):
        xpatientname = str(common.getstring(form.vars.patientmember1)).strip()
        
        r = db((db.vw_memberpatientlist.fullname == xpatientname) & \
               (db.vw_memberpatientlist.providerid == providerid) & \
               (db.vw_memberpatientlist.is_active == True)).select()
        
        if(len(r) > 0):
            memberid = int(common.getid(r[0].primarypatientid))
            patientid = int(common.getid(r[0].patientid))
            memberref = common.getstring(r[0].patientmember)  #patientmember
            fullname = common.getstring(r[0].fullname)      #fname + lname
            patient = common.getstring(r[0].patient)    #fname + lname + patientmemebr
            if(patient == ""):
                patient = common.getstring(request.args[0])
        
            if(memberid > 0):
                formA = gettreatmentgrid(providerid,xpatientname,page,returnurl)
            else:
                formA = None
          
            paytm = calculatepaymentsforpatient(providerid,memberid,patientid)    
            totalcost=paytm["totaltreatmentcost"]
            totalinspays=paytm["totalinspays"]
            totalcopay=paytm["totalcopay"]
            totalpaid=paytm["totalpaid"]
            totaldue=paytm["totaldue"]                 
                
            
    return dict(form=form, formA=formA, page=page,\
                returnurl=returnurl,providername=providername, \
                providerid=providerid,memberid=memberid,patientid=patientid,patient=patient, \
                fullname=fullname,tplanid=tplanid,\
                totalcost=totalcost,\
                totalinspays=totalinspays,\
                totalcopay=totalcopay,\
                totalpaid=totalpaid,\
                totaldue=totaldue
           
                )


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_payment():
    
    page = 0
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])    
    providername = provdict["providername"]    
    
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))  
    tplanid = int(common.getid(request.vars.tplanid))
    
    totalcost =0
    totaldue = 0
    totalpaid = 0
    
    fullname = common.getstring(request.vars.fullname)  #FirstName LastName
    patient = common.getstring(request.vars.patient)  #FirstName LastName:MemberID
    memberref = "" #MemberID
    
    returnurl = URL('payment', 'list_payment', vars=dict(page=1, providerid=providerid))

    form = getpaymentsgrid(providerid, fullname, page, returnurl)
    
    
    
    paytm = calculatepaymentsforpatient(providerid,memberid,patientid)    
    totalcost=paytm["totaltreatmentcost"]
    totalinspays=paytm["totalinspays"]
    totalcopay=paytm["totalcopay"]
    totalpaid=paytm["totalpaid"]
    totaldue=paytm["totaldue"]                 
                
            
    return dict(form=form,  page=page,\
                returnurl=returnurl,providername=providername, \
                providerid=providerid,memberid=memberid,patientid=patientid,patient=patient, \
                fullname=fullname,tplanid=tplanid,\
                totalcost=totalcost,\
                totalinspays=totalinspays,\
                totalcopay=totalcopay,\
                totalpaid=totalpaid,\
                totaldue=totaldue
           
                )

def apply_voucher():
    logger.loggerpms2.info("Enter Apply Voucher")
    
    #voucher
    voucher = common.getkeyvalue(request.vars,"voucher_code","")
    
    #wallet type
    wallet_type = common.getkeyvalue(request.vars,"wallet_type","SUPER_WALLET")
    
    #wallet amount
    walletamount = float(common.getvalue(common.getkeyvalue(request.vars,"walletamount",0)))
    
    #memberid
    memberid = int(common.getkeyvalue(request.vars,'patientmember',0))
    
    #tplanid
    tplanid = int(common.getkeyvalue(request.vars,"treatmentplan","0"))
    tr = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select(db.treatment.id, db.treatment.copay)
    treatmentid = tr[0].id if (len(tr) > 0) else 0    
    
    reqobj = {}
    reqobj["treatmentid"] = treatmentid
    reqobj["voucher_code"] = voucher
    bnft = mdpbenefits.Benefit(db)
    rspobj = json.loads(bnft.apply_voucher(reqobj))
    vlist = rspobj["voucher_list"]
    displaymssg = rspobj["voucher_message"]
    paytm=rspobj
    
    wlist = []
    wallet_type = ""
    
    #get available wallet balance
    reqobj = {}
    reqobj["action"] = "getwallet_balance"
    reqobj["member_id"] = memberid
    reqobj["amount"] = paytm["totalcopay"]
    bnftobj = mdpbenefits.Benefit(db)
    rspobj = json.loads(bnftobj.getwallet_balance(reqobj))
    if(rspobj["result"] == "success"):
        wlist = rspobj["wallet_list"]
    else:
        wlist = []

   
    
    return dict( 
                treatmentcost=paytm["treatmentcost"],
                copay=paytm["copay"],
                inspays=paytm["inspays"],
                companypays=paytm["companypays"],
                walletamount=paytm["walletamount"],
                discount_amount=paytm["discount_amount"],
                totaltreatmentcost=paytm["totaltreatmentcost"],
                totalinspays=paytm["totalinspays"],
                totalcopay=paytm["totalcopay"],
                totalpaid=paytm["totalpaid"],
                totaldue=paytm["totaldue"],
                totalcompanypays=paytm["totalcompanypays"],
                precopay=paytm["precopay"],
                totalprecopay=paytm["totalprecopay"],
                totalwalletamount=paytm["totalwalletamount"],
                totaldiscount_amount=paytm["totaldiscount_amount"],
                vlist=vlist,displaymssg=displaymssg,voucher=voucher,
                wallet_type = wallet_type,wlist=wlist
                )    
    
 
def apply_wallet():
    logger.loggerpms2.info("Enter Apply Wallet")
    
    #wallet type
    wallet_type = common.getkeyvalue(request.vars,"wallet_type","SUPER_WALLET")

    #wallet type
    walletamount = float(common.getvalue(common.getkeyvalue(request.vars,"walletamount",0)))

    #voucher
    voucher = common.getkeyvalue(request.vars,"voucher_code","")
    
    #voucher discount
    discount_amount = float(common.getvalue(common.getkeyvalue(request.vars,"discount_amount",0)))
    
    #memberid
    memberid = int(common.getkeyvalue(request.vars,'patientmember',0))
    
    #memberid
    providerid = int(common.getkeyvalue(request.vars,'provider',0))
    
    #tplanid
    tplanid = int(common.getkeyvalue(request.vars,"treatmentplan","0"))
    tr = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select(db.treatment.id, db.treatment.copay)
    treatmentid = tr[0].id if (len(tr) > 0) else 0    
 
    
   
    #plan_code = common.getkeyvalue(avars,"plan_code","PREMWALKIN")
    #company_code = common.getkeyvalue(avars,"company_code","")
    #event_code = common.getkeyvalue(avars,"event_code","create_payment")
    #region_code = common.getkeyvalue(avars,"region_code","ALL")
    #treatment_id = int(common.id(avars,"treatment_id","0"))

    #get region code
    provs = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.groupregion)
    regionid = int(common.getid(provs[0].groupregion)) if(len(provs) == 1) else 1
    regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select(db.groupregion.groupregion)
    regioncode = common.getstring(regions[0].groupregion) if(len(regions) == 1) else "ALL"    
     
    ## get patient's company
    pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == memberid)).select(db.vw_memberpatientlist.company,db.vw_memberpatientlist.hmoplan)
    companyid = int(common.getid(pats[0].company)) if(len(pats) == 1) else 0
    companys = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
    companycode = common.getstring(companys[0].company) if(len(companys) == 1) else "PREMWALKIN"
    ##for backward compatibility determine procedurepriceplancode from member's plan at the time of registration
    hmoplanid = int(common.getid(pats[0].hmoplan)) if(len(pats) == 1) else 0  #this is the patient's previously assigned plan-typically at registration
    hmoplans = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode)
    hmoplancode = common.getstring(hmoplans[0].hmoplancode) if(len(hmoplans) == 1) else "PREMWALKIN"
    r = db(
        (db.provider_region_plan.companycode == companycode) &\
        (db.provider_region_plan.plancode == hmoplancode) &\
        ((db.provider_region_plan.regioncode == regioncode)|(db.provider_region_plan.regioncode == 'ALL')) &\
        (db.provider_region_plan.is_active == True)).select()
    plancode = r[0].policy if(len(r) == 1) else "PREMWALKIN"
    
    
    avars={}
    avars["plan_code"] = plancode
    avars["company_code"] =companycode
    avars["rule_event"] ="apply_wallet"
    avars["region_code"] =regioncode
    avars["treatment_id"] =treatmentid
    avars["member_id"] =memberid
    
    ruleObj = mdprules.Plan_Rules(db)
    rspobj = json.loads(ruleObj.Get_Plan_Rules(avars))

    walletamount = float(common.getkeyvalue(rspobj,"cashback",0))
    reqobj = {}
    reqobj["treatmentid"] = treatmentid
    reqobj["wallet_type"] = wallet_type
    reqobj["walletamount"] = walletamount

    
    bnft = mdpbenefits.Benefit(db)
    rspobj = json.loads(bnft.apply_wallet(reqobj))
    
    if(rspobj["result"] == "success"):
        wlist = rspobj["wlist"]
    else:
        wlist=[]
    displaymssg = ""
   
    prov = db((db.provider.id == providerid) & (db.provider.is_active == True)).select()
    city = prov[0].city if(len(prov) != 0) else "Jaipur"

    regionid = common.getregionidfromcity(db,city)
    regioncode =  common.getregioncodefromcity(db,city)

    members = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.patientmember.company,db.patientmember.city,db.patientmember.st)
    companyid = common.getid(members[0].company) if (len(members) == 1) else "0"
    c = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
    companycode = c[0].company if (len(c) ==1) else ""

    cp = db((db.provider_region_plan.companycode == companycode) &\
            (db.provider_region_plan.regioncode == regioncode) &\
            (db.provider_region_plan.is_active == True)).select()
    policy = cp[0].policy if(len(cp) != 0) else ""
        
    #cp = db(db.companypolicy.companycode == companycode).select()
    #policy = cp[0].policy if(len(cp) != 0) else ""

    #determine member's city & state
    city = members[0].city if(len(members)>0) else "Jaipur"
    st = members[0].st if(len(members)>0) else "Rajasthan (RJ)"
    c = db(db.cities.city == city).select(db.cities.id)
    cityid = c[0].id if(len(c) > 0) else 0       
    
    reqobj  = {}
    reqobj["treatment_id"] = int(treatmentid) 
    reqobj["member_id"] = int(memberid)
    reqobj["plan_code"] = policy
    reqobj["state"] = st
    reqobj["city_id"] = int(cityid)


    vlist = []
    
    displaymssg = ""

    bnftobj = mdpbenefits.Benefit(db)    
    rspobj = json.loads(bnftobj.getVoucherList(reqobj))
    if(rspobj["result"] == "fail"):
        vlist = []
    else:
        vlist = rspobj["voucher_list"]    

   
   
    
    paytm=json.loads(account._calculatepayments(db,tplanid))
    

    
    return dict( 
                treatmentcost=paytm["treatmentcost"],
                copay=paytm["copay"],
                inspays=paytm["inspays"],
                companypays=paytm["companypays"],
                walletamount=walletamount,
                discount_amount=paytm["discount_amount"],
                totaltreatmentcost=paytm["totaltreatmentcost"],
                totalinspays=paytm["totalinspays"],
                totalcopay=paytm["totalcopay"],
                totalpaid=paytm["totalpaid"],
                totaldue=paytm["totaldue"],
                totalcompanypays=paytm["totalcompanypays"],
                precopay=paytm["precopay"],
                totalprecopay=paytm["totalprecopay"],
                totalwalletamount=paytm["totalwalletamount"],
                totaldiscount_amount=paytm["totaldiscount_amount"],
                vlist=vlist,wlist=wlist,displaymssg=displaymssg,voucher=voucher,
                wallet_type = wallet_type
                )    
    
 

#These two lines are commented because create_payment is also called from mobile browser, hence no check to require
#@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
#@auth.requires_login()
def create_payment():
    

    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    providercode = common.getstring(provdict["provider"])
    
    
    page         = 1 if(int(common.getpage(request.vars.page)) == 0) else int(common.getpage(request.vars.page))
    memberid     = int(common.getid(request.vars.memberid))
    patientid     = int(common.getid(request.vars.patientid))
    tplanid      = int(common.getid(request.vars.tplanid))
    treatmentid      = int(common.getid(request.vars.treatmentid))
    tr = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
    providerid = int(common.getid(tr[0].provider)) if(len(tr) >= 1) else 0
    
    patient = ""
    fullname = ""
    hmopatientmember = True
    
    avars={}
    avars["providerid"] = providerid
    avars["memberid"] = memberid
    avars["patientid"] = patientid

    #patobj = mdppatient.Patient(db, providerid)
    #patobj = json.loads(patobj.getMemberPolicy(avars))
    patobj = json.loads(mdputils.getMemberPolicy(db,avars))
        
    plancode = common.getkeyvalue(patobj,"plancode","PREMWALKIN")
    policy = common.getkeyvalue(patobj,"policy","PREMWALKIN")
    procedurepriceplancode = common.getkeyvalue(patobj,"procedurepriceplancode","PREM103")
    regioncode = common.getkeyvalue(patobj,"regioncode","JAI")
    companycode = common.getkeyvalue(patobj,"companycode","MYDP")
        
    #
    #provs = db((db.provider.id == providerid) & (db.provider.is_active == True)).select()
    #regionid = int(common.getid(provs[0].groupregion)) if(len(provs) == 1) else 1
    #regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select(db.groupregion.groupregion)
    #regioncode = common.getstring(regions[0].groupregion) if(len(regions) == 1) else "ALL"   

    pats = db((db.vw_memberpatientlist.patientid==patientid)&(db.vw_memberpatientlist.primarypatientid==memberid)&(db.vw_memberpatientlist.is_active==True)).select(\
        db.vw_memberpatientlist.ALL, db.company.ALL,\
        left=db.company.on(db.company.id==db.vw_memberpatientlist.company))

    st = pats[0].company.st if(len(pats)>0) else "Rajasthan (RJ)"
    cityid = pats[0].company.id if(len(pats) > 0) else 0        
   
    #companycode = pats[0].company.company if (len(pats) ==1) else ""
    #hmoplanid = int(common.getid(pats[0].vw_memberpatientlist.hmoplan)) if(len(pats) == 1) else 0  #this is the patient's previously assigned plan-typically at registration
    #hmoplans = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode)
    #hmoplancode = common.getstring(hmoplans[0].hmoplancode) if(len(hmoplans) == 1) else "PREMWALKIN"
    #r = db(
        #(db.provider_region_plan.companycode == companycode) &\
        #(db.provider_region_plan.plancode == hmoplancode) &\
        #((db.provider_region_plan.regioncode == regioncode)|(db.provider_region_plan.regioncode == 'ALL')) &\
        #(db.provider_region_plan.is_active == True)).select()
    #policy = r[0].policy if(len(r) == 1) else "PREMWALKIN"
    #plancode =  r[0].plancode if(len(r) == 1) else "PREMWALKIN"
    
    #calculate the discount for this member 
    #update the treatment, treatmentplan. 
    #There is an assumption that there will be no companypay from Plans 
    avars = {
        "action": "get_benefit",
        "member_id":str(memberid),
        "provider_id":str(providerid),
        "plan_code":plancode,
        "company_code":companycode,
        "treatmentid" : str(treatmentid),
        "tplanid" : str(tplanid),
        "rule_event":"get_plan_benefits"
    }

    ruleObj = mdprules.Plan_Rules(db)
    benefit = json.loads(ruleObj.Get_Plan_Rules(avars))

   
    if(benefit["result"]=="success"):
        #mdp_wallet_cashback
        walletobj = common.getkeyvalue(benefit,"wallet", None)
        discount_amount = 0 if (walletobj == None) else float(common.getkeyvalue(walletobj,"mdp_wallet_amount_usable",0))
        
        #Super Wallet Cashback
        walletamount = 0 if (walletobj == None) else float(common.getkeyvalue(walletobj,"super_wallet_amount_usable",0))
        wallet_type = "" if (walletamount == 0) else "SUPER_WALLET"
        #planbenefit
        planbenefitobj = common.getkeyvalue(benefit,"planBenefits", None)
        companypays = 0 if ((planbenefitobj == None)|(len(planbenefitobj)==0)) else float(common.getkeyvalue(planbenefitobj[0],"discount_benefit_amount_usable",0))
        
        
        #update totalcompanypays (we are saving discount_amount as companypays )
        db(db.treatment.id == treatmentid).update(companypay = companypays, walletamount=walletamount,wallet_type = wallet_type,
                                                  discount_amount=discount_amount,WPBA_response = json.dumps(benefit))    
        
        #update treatmentplan assuming there is one treatment per tplan
        db(db.treatmentplan.id==tplanid).update(totalcompanypays = companypays, totalwalletamount=walletamount,wallet_type =wallet_type,
                                                  totaldiscount_amount=discount_amount) 
        
        db.commit()
        

    #pats = db((db.vw_memberpatientlist.patientid==patientid)&(db.vw_memberpatientlist.primarypatientid==memberid)&(db.vw_memberpatientlist.is_active==True)).select(\
        #db.vw_memberpatientlist.ALL, db.company.ALL,\
        #left=db.company.on(db.company.id==db.vw_memberpatientlist.company))

    #Apply Voucher
    vlist = []
    #reqobj  = {}
    #reqobj["treatment_id"] = int(treatmentid) 
    #reqobj["member_id"] = int(memberid)
    #reqobj["plan_code"] = policy
    #reqobj["state"] = st
    #reqobj["city_id"] = int(cityid)
    #bnftobj = mdpbenefits.Benefit(db)    
    #rspobj = json.loads(bnftobj.getVoucherList(reqobj))
    #if(rspobj["result"] == "fail"):
        #vlist = []
    #else:
        #vlist = rspobj["voucher_list"]    
    

    #payment modes are dependant on the company
    online = True
    cashless = True
    cash = True
    cheque = True    

    if(len(pats)>0):
        patient = pats[0].vw_memberpatientlist.patient
        fullname = pats[0].vw_memberpatientlist.fullname
        hmopatientmember = pats[0].vw_memberpatientlist.hmopatientmember
        online = common.getboolean(pats[0].company.onlinepayment)
        cashless = common.getboolean(pats[0].company.cashlesspayment)
        cash = common.getboolean(pats[0].company.cashpayment)
        cheque = common.getboolean(pats[0].company.chequepayment)
        
        
    returnurl = common.getstring(request.vars.returnurl)
    if(returnurl == ""):
        returnurl = URL('payment','list_payment',vars=dict(page=page,providerid=providerid))
    
    creattreturnurl = URL('payment', 'create_payment', vars=dict(page=page,patientname=patient,tplanid=tplanid,treatmentid=treatmentid,\
                                                                 patientid=patientid,memberid=memberid,providerid=providerid,plan=policy))
    
    db.payment.treatmentplan.default=tplanid
    db.payment.patientmember.default=memberid
    db.payment.provider.default = providerid
    db.payment.is_active.default = True
    db.payment.paymentcommit.default = False
    db.payment.amount.default = 0.00
    db.payment.policy.default = policy
   
    
    formA = crud.create(db.payment, next='update_payment?page=' + str(page) + "&source=create" + "&memberid=" + str(memberid) + "&patientid=" + str(patientid) + "&paymentid=[id]"  + "&patient=" + patient + "&fullname=" + fullname+ "&treatmentid=" + str(treatmentid) + "&policy=" + policy)  ## company Details entry form
    
    xnotes = formA.element('textarea',_id='payment_notes')
    if(xnotes != None):
        xnotes['_class'] = 'form-control'
        xnotes['_style'] = 'height:50px;line-height:1.5;'
        xnotes['_rows'] = 5 
    
    xdob = formA.element('input',_id='payment_paymentdate')
    if(xdob != None):
        xdob['_class'] =  'input-group form-control form-control-inline date-picker'
        xdob['_data-date-format'] = 'dd/mm/yyyy'
        xdob['_autocomplete'] = 'off' 
        xdob['_placeholder'] = 'dd/mm/yyyy'     
     
   
    
    if(treatmentid > 0):
        formC = getproceduregrid(treatmentid, providerid)
    else:
        formC = None
    if(memberid > 0):
        
        formB = getpaymentgrid(tplanid,treatmentid,providerid, memberid,patientid,page,patient,fullname,providername,creattreturnurl)
    else:
        formB = None
                                
  
    treatment = ""     
    tps = db((db.vw_payment_treatmentplan_treatment.providerid == providerid)& (db.vw_payment_treatmentplan_treatment.primarypatient == memberid) & \
                         (db.vw_payment_treatmentplan_treatment.tplanactive == True)&(db.vw_payment_treatmentplan_treatment.tplanid == tplanid)).select()   
                         
    if(len(tps)>0):
        treatment = tps[0].treatment
    
    
    walletamount = 0     
    
    paytm = json.loads(account._calculatepayments(db, tplanid,policy))
    
    paytm["totalwalletamount"]  = paytm["totalwalletamount"] + walletamount
    paytm["walletamount"]  = paytm["walletamount"] + walletamount
    
    db.payment.amount.requires = paytm["totaldue"]
    db.payment.amount.default  = paytm["totaldue"]
    db.payment.discount_amount.default = paytm["discount_amount"]

    #get available wallet list
    wlist=[]
    #reqobj = {}
    #reqobj["action"] = "getwallet_balance"
    #reqobj["member_id"] = memberid
    #reqobj["plan_code"] = policy
    #reqobj["amount"] = paytm["totalcopay"]
    #rspobj = json.loads(bnftobj.getwallet_balance_1(reqobj))
    #if(rspobj["result"] == "success"):
        #wlist = rspobj["wallet_list"]
    #else:
        #wlist = []
     
    return dict(formA=formA,formB=formB,formC=formC, patient=patient,fullname=fullname,hmopatientmember=hmopatientmember,providername=provdict["providername"],
                providerid=provdict["providerid"],page=page,returnurl=returnurl,memberid=memberid,tplanid=tplanid,treatment=treatment,
                
                treatmentcost=paytm["treatmentcost"],
                copay=paytm["copay"],
                inspays=paytm["inspays"],
                companypays=paytm["companypays"],
                walletamount=paytm["walletamount"],
                discount_amount = paytm["discount_amount"],
                totaltreatmentcost=paytm["totaltreatmentcost"],
                totalinspays=paytm["totalinspays"],
                totalcopay=paytm["totalcopay"],
                totalpaid=paytm["totalpaid"],
                totaldue=paytm["totaldue"],
                totalcompanypays=paytm["totalcompanypays"],precopay=paytm["precopay"],totalprecopay=paytm["totalprecopay"],
                totalwalletamount=paytm["totalwalletamount"],totaldiscount_amount=paytm["totaldiscount_amount"],policy=policy,
                vlist=vlist,wlist=wlist,
                online=online,cashless=cashless,cash=cash,cheque=cheque
            )    
    

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def update_payment():
    logger.loggerpms2.info("Enter Update Payment " + json.dumps(request.vars))
    tplanid = 0
    
    source = common.getstring(request.vars.source)
    
    paymentid    = int(common.getid(request.vars.paymentid))
    payment = db(db.payment.id == paymentid).select()
    paymentamount = 0
    paymentmode = "Cash"
    paymenttype = ""
    paymentcommit = False
    treatmentid = 0
    
    if(len(payment)>0):
        paymentcommit = common.getboolean(payment[0].paymentcommit)
        paymenttype = common.getstring(payment[0].paymenttype)
        paymentmode =common.getstring(payment[0].paymentmode)
        paymentamount = common.getvalue(payment[0].amount)
        tplanid = payment[0].treatmentplan

      
    page         = int(common.getpage(request.vars.page))
    memberid     = int(common.getid(request.vars.memberid))    
    patientid     = int(common.getid(request.vars.patientid))
    patient     = common.getstring(request.vars.patient) 
    fullname    = common.getstring(request.vars.fullname)
    treatmentid     = int(common.getid(request.vars.treatmentid))
    policy     = request.vars.policy
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])

    paytm = json.loads(account._calculatepayments(db, tplanid))
    if((paytm["totaldue"] == 0) & (paytm["totalwalletamount"] > 0)):
        logger.loggerpms2.info("Call PaymentCallback_0")
        avars = {}
        avars["paymentid"] = paymentid
        avars["amount"] = paytm["copay"]
        payObj = mdppayment.Payment(db, providerid)
        rspobj = json.loads(payObj.paymentcallback_0(avars))
        logger.loggerpms2.info("Exit Update Payment - paymentcallback_0 " + json.dumps(rspobj))
        paymentobj = mdppayment.Payment(db, providerid)
        receiptobj = json.loads(paymentobj.paymentreceipt(paymentid))
        logger.loggerpms2.info("Pine  - Exit Payment Receipt " + json.dumps(receiptobj))
        returnurl = URL("admin","logout") 
    
             
        redirect(returnurl)
        return json.dumps(rspobj)
        
    
    #return url to treatment
    returnurl = URL('treatment', 'update_treatment', vars=dict(page=page,imagepage=0,tplanid=tplanid,treatmentid=treatmentid,\
                                                                 providerid=providerid))
    
    
    
    if(common.getstring(request.vars.mode) != "update"):
        if((source == "create") & ((paymentmode == 'Cash') | (paymentmode == 'Cashless') | (paymentmode == 'Cheque'))):
            redirect(URL('payment','cashpayment_success', vars=dict(paymentmode=paymentmode,paymentid=paymentid,providerid=providerid,returnurl=returnurl)))
        elif ((source=="create") & (paymentmode == "Shopse")):
            redirect(URL('payment','make_payment_shopse',vars=dict(providerid=providerid,paymentid=paymentid,paymentmode=paymentmode,invoiceamt=paymentamount,returnurl=returnurl)))
        elif ((source=="create") & (paymentmode == "PineLabs")):
            redirect(URL('payment','make_payment_pinelabs',vars=dict(providerid=providerid,paymentid=paymentid,paymentmode=paymentmode,invoiceamt=paymentamount,returnurl=returnurl)))
        else:
            redirect(URL('payment','make_payment_hdfc',vars=dict(paymentid=paymentid,paymentmode=paymentmode,invoiceamt=paymentamount,returnurl=returnurl)))
            
    
   
    treatment=""
    
    tps = db((db.vw_payment_treatmentplan_treatment.providerid == providerid)& (db.vw_payment_treatmentplan_treatment.primarypatient == memberid) & \
                            (db.vw_payment_treatmentplan_treatment.tplanactive == True)&(db.vw_payment_treatmentplan_treatment.tplanid == tplanid)).select()       
    if(len(tps)>0):
        treatment = tps[0].treatment
      
    paytm = calculatepayments(tplanid,providerid)    

    #members = db((db.vw_memberpatientlist.is_active == True) & (db.vw_memberpatientlist.providerid == providerid) & \
                #(db.vw_memberpatientlist.primarypatientid == db.vw_memberpatientlist.patientid)).select(\
                    #db.vw_memberpatientlist.ALL,\
                    #orderby=db.vw_memberpatientlist.fullname)

    
    #payment modes are dependant on the company
    #online = True
    #cashless = True
    #cash = True
    #cheque = True    

    #if(len(members)>0):
        #online = common.getboolean(members[0].company.onlinepayment)
        #cashless = common.getboolean(members[0].company.cashlesspayment)
        #cash = common.getboolean(members[0].company.cashpayment)
        #cheque = common.getboolean(members[0].company.chequepayment)
    
        
            
    crud.settings.keepvalues = True
    crud.settings.showid = True
    #crud.settings.update_onaccept = acceptupdatepayment
    crud.settings.update_next = URL('payment','list_payment',vars=dict(page=page,tplanid=tplanid,patient=patient,fullname=fullname,patientid=patientid, memberid=memberid,providerid=providerid,providername=providername))
    
    
    db.payment.amount.writable = not paymentcommit
    db.payment.paymenttype.writable = not paymentcommit
    db.payment.paymentmode.writable = not paymentcommit
    db.payment.payor.writable = not paymentcommit
    db.payment.patientmember.writable = not paymentcommit
    db.payment.treatmentplan.writable = not paymentcommit
    db.payment.paymentdate.writable = not paymentcommit
    db.payment.is_active.writable = not paymentcommit
    db.payment.paymentcommit.writable = not paymentcommit
    db.payment.fp_status.writable = not paymentcommit
    db.payment.fp_paymentref.writable = not paymentcommit
    db.payment.fp_paymenttype.writable = not paymentcommit
    db.payment.fp_paymentdetail.writable = not paymentcommit
    
    formA = crud.update(db.payment, paymentid,cast=int, message="Thankyou for your Payment!")  ## company Details entry form
    
    xnotes = formA.element('textarea',_id='payment_notes')
    xnotes['_class'] = 'form-control'    
    xnotes['_style'] = 'height:50px;line-height:1.0;'
    xnotes['_rows'] = 5   
    xnotes['_readonly'] = True
    
    
    
    
    totaltreatmentcost = 0
    totaldue = 0
    totalcost = 0
    totalpaid = 0
    
    tplan = db(db.treatmentplan.id == tplanid).select()
    totaltreatmentcost = float(common.getvalue(tplan[0].totaltreatmentcost))
    
    r = db((db.vw_paymentsummary1.provider==providerid) & (db.vw_paymentsummary1.patientmember == memberid)).select()
    if(len(r)>0):
        totalcost = float(common.getvalue(r[0].totalcost))
        totalpaid = float(common.getvalue(r[0].totalpaid))
        totaldue = totalcost-totalpaid
      

    
    
        
    
    
    return dict(formA=formA, patient=patient,fullname=fullname,returnurl=returnurl,source=source, page=page, paymentid=paymentid,\
                providerid=providerid, providername=providername, tplanid=tplanid, treatment=treatment, memberid=memberid, \
                paymentcommit=paymentcommit,paymenttype=paymenttype,paymentmode=paymentmode,\
                totalcost=totalcost,\
                treatmentcost=paytm["treatmentcost"],copay=paytm["copay"],inspays=paytm["inspays"],\
                totaltreatmentcost=paytm["totaltreatmentcost"],totalinspays=paytm["totalinspays"],totalcopay=paytm["totalcopay"],\
                totalpaid=paytm["totalpaid"],totaldue=paytm["totaldue"],
                companypays=paytm["companypays"], totalcompanypays=paytm["totalcompanypays"],precopay=paytm["precopay"],totalprecopay=paytm["totalprecopay"],policy=policy
                
                )



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def view_payment():
    
    page         = int(common.getpage(request.vars.page))
    paymentid    = int(common.getid(request.vars.paymentid))

    provdict = common.getprovider(auth, db)    
    
    providerid   =   int(provdict["providerid"])
    providername =   provdict["providername"]          
    
    payment = db(db.payment.id == paymentid).select()
    
    tps = db(((db.treatmentplan.provider == providerid)&\
                        (db.treatmentplan.is_active == True))).select()      
    tplanid = 0
    memberid = 0
    if(len(payment)>0):
        tplanid = payment[0].treatmentplan
        memberid = payment[0].patientmember
    
    crud.settings.keepvalues = True
    crud.settings.showid = True
    #crud.settings.update_onaccept = acceptupdatepayment
    crud.settings.update_next = URL('payment','list_payment',vars=dict(page=page,providerid=providerid,providername=providername,memberid=memberid,tplanid=tplanid))
  
    formA = crud.update(db.payment, paymentid,cast=int, message="Thankyou for your Payment!")  ## company Details entry form

    xnotes = formA.element('textarea',_id='payment_notes')
    
    xnotes['_style'] = 'height:50px;line-height:1.0;'
    xnotes['_rows'] = 5   
    
   


    returnurl = URL('payment','list_payment',vars=dict(page=page,tplanid=tplanid,memberid=memberid,providerid=providerid,providername=providername))
    
    return dict(formA=formA, returnurl=returnurl, page=page, providerid=providerid, providername=providername, tplanid=tplanid, memberid=memberid, tps=tps)


def calculatepaymentsforpatient(providerid, memberid, patientid):
    

    
    totaltreatmentcost = 0
    totalcopay = 0
    totalinspays = 0
    totaldue = 0
    totalpaid = 0    
    
    r = db((db.vw_treatmentplansummarybypatient.provider==providerid) & (db.vw_treatmentplansummarybypatient.memberid == memberid)&\
           (db.vw_treatmentplansummarybypatient.patientid == patientid)& (db.vw_treatmentplansummarybypatient.is_active == True)).select()
    
    if(len(r)>0):
        totaltreatmentcost = float(common.getvalue(r[0].totalcost))
        totalinspays = float(common.getvalue(r[0].totalinspays))
        totalcopay = float(common.getvalue(r[0].totalcopay))
        totalpaid = float(common.getvalue(r[0].totalpaid))
        totaldue = totaltreatmentcost- (totalpaid + totalinspays)    
     
    return dict(totaltreatmentcost=totaltreatmentcost,totalinspays=totalinspays,totalcopay=totalcopay,\
                totalpaid=totalpaid,totaldue=totaldue)

def calculatepayments(tplanid,memberid,providerid):
    
    
    
    
    treatmentcost = 0
    copay = 0
    inspays = 0
    
    totaltreatmentcost = 0
    totalcopay = 0
    totalinspays = 0
    totaldue = 0
    totalpaid = 0
    
    tplan = db(db.treatmentplan.id == tplanid).select()
    if(len(tplan) > 0):
        treatmentcost = float(common.getvalue(tplan[0].totaltreatmentcost))
        copay = float(common.getvalue(tplan[0].totalcopay))
        inspays = float(common.getvalue(tplan[0].totalinspays))
        
        r = db((db.vw_paymentsummary1.provider==providerid) & (db.vw_paymentsummary1.patientmember == memberid)).select()
        if(len(r)>0):
            totaltreatmentcost = float(common.getvalue(r[0].totalcost))
            totalinspays = float(common.getvalue(r[0].totalinspays))
            totalcopay = float(common.getvalue(r[0].totalcopay))
            totalpaid = float(common.getvalue(r[0].totalpaid))
            totaldue = totaltreatmentcost- (totalpaid + totalinspays)
        
        
    return dict(treatmentcost=treatmentcost,copay=copay,inspays=inspays,totaltreatmentcost=totaltreatmentcost,totalinspays=totalinspays,totalcopay=totalcopay,\
                totalpaid=totalpaid,totaldue=totaldue)

def calculatepayments(tplanid,providerid,policy=None):
    treatmentcost = 0
    copay = 0
    inspays = 0
    companypays = 0
    precopay = 0
    walletamount = 0
    
    totaltreatmentcost = 0
    totalcopay = 0
    totalprecopay = 0
    totalinspays = 0
    totaldue = 0
    totalpaid = 0
    totalcompanypays = 0
    totalwalletamount = 0
        
    tplan = db(db.treatmentplan.id == tplanid).select()
    if(len(tplan) > 0):
        treatmentcost = float(common.getvalue(tplan[0].totaltreatmentcost))
        companypays = float(common.getvalue(tplan[0].totalcompanypays))
        walletamount = 0 #float(common.getvalue(tplan[0].totalwalletamount))        
        precopay =float(common.getvalue(tplan[0].totalcopay))
        copay = float(common.getvalue(tplan[0].totalcopay)) - companypays
        inspays = float(common.getvalue(tplan[0].totalinspays))
        memberid = int(common.getid(tplan[0].primarypatient))
        
        
        
        
            
        
        r = db((db.vw_treatmentplansummarybytreatment.provider==providerid) & (db.vw_treatmentplansummarybytreatment.id == tplanid)).select()
        if(len(r)>0):
            totaltreatmentcost = float(common.getvalue(r[0].totalcost))
            totalinspays = float(common.getvalue(r[0].totalinspays))
            totalcompanypays = float(common.getvalue(r[0].totalcompanypays))
            totalwalletamount = 0 #float(common.getvalue(r[0].totalwalletamount))
            totalprecopay = float(common.getvalue(r[0].totalcopay))
            totalcopay = float(common.getvalue(r[0].totalcopay)) - totalcompanypays
            totalpaid = float(common.getvalue(r[0].totalpaid))
            totaldue = totalcopay - totalpaid
        
        
    return dict(treatmentcost=treatmentcost,copay=copay,precopay=precopay,inspays=inspays,companypays=companypays, walletamount=walletamount,
                totaltreatmentcost=totaltreatmentcost,totalinspays=totalinspays,\
                totalprecopay=totalprecopay,totalcopay=totalcopay,\
                totalpaid=totalpaid,totaldue=totaldue,totalcompanypays=totalcompanypays,totalwalletamount=totalwalletamount)

def paymentsummary():
    
    tplanid = int(common.getid(request.vars.treatmentplan))
    memberid = int(common.getid(request.vars.patientmember))
    providerid = int(common.getid(request.vars.provider))

    
    
    treatmentcost = 0
    copay = 0
    inspays = 0
    
    totaltreatmentcost = 0
    totalcopay = 0
    totalinspays = 0
    totaldue = 0
    totalpaid = 0
    
    tplan = db(db.treatmentplan.id == tplanid).select()
    if(len(tplan) > 0):
        treatmentcost = float(common.getvalue(tplan[0].totaltreatmentcost))
        copay = float(common.getvalue(tplan[0].totalcopay))
        inspays = float(common.getvalue(tplan[0].totalinspays))
        
        r = db((db.vw_paymentsummary1.provider==providerid) & (db.vw_paymentsummary1.patientmember == memberid)).select()
        if(len(r)>0):
            totaltreatmentcost = float(common.getvalue(r[0].totalcost))
            totalinspays = float(common.getvalue(r[0].totalinspays))
            totalcopay = float(common.getvalue(r[0].totalcopay))
            totalpaid = float(common.getvalue(r[0].totalpaid))
            
            
            totaldue = totalcopay - (totalpaid)
        
        
    return dict(treatmentcost=treatmentcost,copay=copay,inspays=inspays,totaltreatmentcost=totaltreatmentcost,totalinspays=totalinspays,totalcopay=totalcopay,\
                totalpaid=totalpaid,totaldue=totaldue)


def tplans():
    
    memberid = int(common.getid(request.vars.patientmember))
    providerid = int(common.getid(request.vars.provider))
    
    tplans = db((db.treatmentplan.provider == providerid) & (db.treatmentplan.primarypatient == memberid) & (db.treatmentplan.is_active == True)).select()
   
    
    return dict(tplans=tplans)

@auth.requires_login()
def delete_payment():
    
    provdict = common.getprovider(auth, db)
    paymentid = int(common.getid(request.vars.paymentid))
    page = common.getpage(request.vars.page)          
    
    form = FORM.confirm('Yes?',{'No':URL('payment','list_payment')})


    if form.accepted:
        db((db.payment.id == paymentid) & (db.payment.paymentcommit == False)).update(is_active=False)
        redirect(URL('payment','list_payment'))

    
    return dict(form=form,returnurl=URL('payment','list_payment'),providerid=provdict["providerid"],providername=provdict["providername"],page=page)
