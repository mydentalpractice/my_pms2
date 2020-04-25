import datetime
import time
import json


import os

import base64
import hashlib
import sha
import OpenSSL

from OpenSSL import SSL
from OpenSSL import crypto


from applications.my_pms2.modules import common

def getproviderinformation(db,providerid):
    
    provtitle = 'provtitle'
    providername = 'provname'
    providerregno = 'provregno'    
    
    pracname = ""
    pracaddress1 = ""
    pracaddress2 = ""
    
    pracephone = 'provphone'
    praceemail = 'provemail'
    

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

def getpatientinformation(db,patientid, memberid):
    
    patientname = ''
    patientmember = ''
    mediassistid  = ''
    patientemail = ''
    patientcell  = ''
    patientgender = ''
    patientage = ''
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


def calculatepayments(db,tplanid,providerid):
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
        
        r = db((db.vw_treatmentplansummarybytreatment.provider==providerid) & (db.vw_treatmentplansummarybytreatment.id == tplanid)).select()
        if(len(r)>0):
            totaltreatmentcost = float(common.getvalue(r[0].totalcost))
            totalinspays = float(common.getvalue(r[0].totalinspays))
            totalcopay = float(common.getvalue(r[0].totalcopay))
            totalpaid = float(common.getvalue(r[0].totalpaid))
            totaldue = totalcopay - totalpaid
        
        
    return dict(treatmentcost=treatmentcost,copay=copay,inspays=inspays,totaltreatmentcost=totaltreatmentcost,totalinspays=totalinspays,totalcopay=totalcopay,\
                totalpaid=totalpaid,totaldue=totaldue)




  


def bytetohex(byteStr):
    
    x = ''.join( [ "%02X " % ord( x ) for x in byteStr ] ).strip()
    
    return x


class Payment:
    
    
    
    def __init__(self,db,providerid):
        self.db = db
        self.providerid = providerid
        return
    
    
   
    
    def getsignedkey(self,sign_ip,appPath):
        
        db = self.db

        r = db(db.urlproperties.id>0).select()
          
        keyfile = common.getstring(r[0].fp_privatekey)
        
        prikeyfile = os.path.join(appPath, 'static/assets',keyfile)    
        with open(prikeyfile, mode='rb') as privatefile:
            privKey = privatefile.read()
           
        rsapvtkey = OpenSSL.crypto.load_privatekey(crypto.FILETYPE_PEM, privKey)
        signature = OpenSSL.crypto.sign(rsapvtkey, sign_ip,'sha512' )    
        signhex = bytetohex(signature)
        signhex = signhex.replace(" ","").lower()

        
        return json.dumps({"signedkey":signhex})
    
    
    def listpayments(self, memberid, patientid):
        
        db = self.db
        providerid = self.providerid
        
        payments = db((db.vw_payments.providerid == providerid) & \
                      (db.vw_payments.memberid == memberid) & \
                      (db.vw_payments.patientid == patientid) & \
                      (db.vw_payments.is_active == True)).select(\
                          db.vw_payments.id,\
                          db.vw_payments.treatment,\
                          db.vw_payments.treatmentid,\
                          db.vw_payments.treatmentdate,\
                          db.vw_payments.shortdescription,\
                          db.vw_payments.memberid,\
                          db.vw_payments.patientid,\
                          db.vw_payments.providerid,\
                          db.vw_payments.patientname,\
                          db.vw_payments.lastpaymentdate,\
                          db.vw_payments.totaltreatmentcost,\
                          db.vw_payments.totalcopay,\
                          db.vw_payments.totalinspays,\
                          db.vw_payments.totalpaid,\
                          db.vw_payments.totalcopaypaid,\
                          db.vw_payments.totalinspaid,\
                          db.vw_payments.totaldue,\
                          db.vw_payments.is_active\
                      )
        
        payobj = {}
        
        paymentlist = []
        
        for payment in payments:
            
            payobj = {
                "paymentid":int(common.getid(payment.id)),
                "memberid":memberid,
                "patientid":patientid,
                "patient":payment.patientname,
                "paymentdate":None if(payment.lastpaymentdate == None) else (payment.lastpaymentdate).strftime("%d/%m/%Y"),
                "treatmentid":int(common.getid(payment.treatmentid)),
                "treatment":payment.treatment,
                "treatmentdate":(payment.treatmentdate).strftime("%d/%m/%Y"),
                "procedures":payment.shortdescription,
                "totaltreatmentcost":float(common.getvalue(payment.totaltreatmentcost)),
                "totalcopay":float(common.getvalue(payment.totalcopay)),
                "totalinspays":float(common.getvalue(payment.totalinspays)),
                "totalpaid":float(common.getvalue(payment.totalpaid)),
                "totaldue":float(common.getvalue(payment.totaldue)),
                "totaldue":float(common.getvalue(payment.totaldue))
            
            }
            paymentlist.append(payobj)
            
        return json.dumps({"paymentcount":len(payments), "paymentlist":paymentlist})
        
        
    def getpayment(self,paymentid):
        
        db = self.db
        providerid = self.providerid
        
        payments = db(db.vw_payments.id == paymentid).select(\
                  db.vw_payments.treatment,\
                  db.vw_payments.treatmentid,\
                  db.vw_payments.treatmentdate,\
                  db.vw_payments.shortdescription,\
                  db.vw_payments.memberid,\
                  db.vw_payments.patientid,\
                  db.vw_payments.providerid,\
                  db.vw_payments.patientname,\
                  db.vw_payments.lastpaymentdate,\
                  db.vw_payments.totaltreatmentcost,\
                  db.vw_payments.totalcopay,\
                  db.vw_payments.totalinspays,\
                  db.vw_payments.totalpaid,\
                  db.vw_payments.totalcopaypaid,\
                  db.vw_payments.totalinspaid,\
                  db.vw_payments.totaldue
              
              )

        trtmnt = db(db.treatment.id == int(common.getid(payments[0].treatmentid))).select(db.treatment.treatmentplan)
        tplanid = int(common.getid(trtmnt[0].treatmentplan))
        
        paytm = calculatepayments(db, tplanid, providerid)
        
        
        paymentsummary = {
            "totaltreatmentcost":paytm["totaltreatmentcost"],
            "totalinspays":paytm["totalinspays"],
            "totalcopay":paytm["totalcopay"],
            "totalpaid":paytm["totalpaid"],
            "totaldue":paytm["totaldue"]
        }
        
        payobj = {}

        paymentlist = []
        
        for payment in payments:
            
            payobj = {
                "memberid":payment.memberid,
                "patientid":payment.patientid,
                "patient":payment.patientname,
                "paymentdate":None if(payment.lastpaymentdate == None) else (payment.lastpaymentdate).strftime("%d/%m/%Y"),
                "treatmentid":int(common.getid(payment.treatmentid)),
                "treatment":payment.treatment,
                "treatmentdate":(payment.treatmentdate).strftime("%d/%m/%Y"),
                "procedures":payment.shortdescription,
                "totaltreatmentcost":float(common.getvalue(payment.totaltreatmentcost)),
                "totalcopay":float(common.getvalue(payment.totalcopay)),
                "totalinspays":float(common.getvalue(payment.totalinspays)),
                "totalpaid":float(common.getvalue(payment.totalpaid)),
                "totaldue":float(common.getvalue(payment.totaldue)),
                "totaldue":float(common.getvalue(payment.totaldue))
            
            }
            paymentlist.append(payobj)
            
        return json.dumps({"paymentcount":len(payments), "paymentsummary":paymentsummary, "paymentlist":paymentlist})
    
    def getpaymentlist(self,memberid,patientid,treatmentid):
 
        db = self.db
        providerid = self.providerid
        
        #get list of payments made for this treatment
        payments = db((db.vw_paymentlist.is_active == True) & (db.vw_paymentlist.providerid == providerid) &\
                   (db.vw_paymentlist.treatmentid==treatmentid) & (db.vw_paymentlist.memberid==memberid) & \
                   (db.vw_paymentlist.patientid==patientid)).select()        
        
        paylist = []
        payobj = {}
        
        for payment in payments:
            payobj = {
                "paymentdate": common.getISTFormatCurrentLocatTime().strftime("%d/%m/%Y") if(payment.paymentdate == None) else (payment.paymentdate).strftime("%d/%m/%Y"),
                "paymentid":int(common.getid(payment.id)),
                "amount":float(common.getvalue(payment.amount)),
                "mode":common.getstring(payment.paymentmode),
                "treatment":common.getstring(payment.treatment),
                "patient":common.getstring(payment.patientname)
            }
            
            paylist.append(payobj)
            
        #payment summary
        trtmnt = db(db.treatment.id == treatmentid).select(db.treatment.treatmentplan)
        tplanid = int(common.getid(trtmnt[0].treatmentplan))
        
        paytm = calculatepayments(db, tplanid, providerid)
        
        
        paymentsummary = {
            "totaltreatmentcost":paytm["totaltreatmentcost"],
            "totalinspays":paytm["totalinspays"],
            "totalcopay":paytm["totalcopay"],
            "totalpaid":paytm["totalpaid"],
            "totaldue":paytm["totaldue"]
        }        
  
        return json.dumps({"count":len(payments),"paymentsummary":paymentsummary,"paymentlist":paylist})
    
    
    def getprocedurelist(self,memberid,patientid,treatmentid):
        
        db = self.db
        providerid = self.providerid
        
        #get list of procedures for this treatment
        procs = db((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.providerid  == providerid) & (db.vw_treatmentprocedure.is_active == True)) .select()        
        
        proclist = []
        procobj = {}
        
        
        for proc in procs:
            
            procobj = {
                "code": common.getstring(proc.procedurecode),
                "description": common.getstring(proc.altshortdescription),
                "procedurefee":float(common.getvalue(proc.procedurefee)),
                "ucr" :float(common.getvalue(proc.ucrfee)),
                "copay" :float(common.getvalue(proc.copay)),
                "inspays" :float(common.getvalue(proc.inspays)),
                "authorized":common.getboolean(proc.authorized),
                "status":common.getstring(proc.status)
            }
            
            proclist.append(procobj)        
  
        return  json.dumps({"count":len(procs),"procedurelist":proclist})
    
    def getpaymentsummary(self,memberid,patientid,treatmentid):

        db = self.db
        providerid = self.providerid
        
        trtmnt = db(db.treatment.id == treatmentid).select(db.treatment.treatmentplan)
        tplanid = int(common.getid(trtmnt[0].treatmentplan))
        
        paytm = calculatepayments(tplanid,providerid)        
        
        paymentsummary = {
                  "totaltreatmentcost":paytm["totaltreatmentcost"],
                  "totalinspays":paytm["totalinspays"],
                  "totalcopay":paytm["totalcopay"],
                  "totalpaid":paytm["totalpaid"],
                  "totaldue":paytm["totaldue"]
              }        

        
        return  json.dumps({"paymentsummary":paymentsummary})
    
    
    #This method creates a new payment
    #
    def newpayment(self,memberid,patientid,treatmentid):
     
        
        db = self.db
        providerid = self.providerid
        
        localcurrdate = common.getISTCurrentLocatTime()
        dttodaydate = datetime.datetime.strptime(localcurrdate.strftime("%d") + "/" + localcurrdate.strftime("%m") + "/" + localcurrdate.strftime("%Y"), "%d/%m/%Y")
        
        trtmnt = db(db.treatment.id == treatmentid).select(db.treatment.treatment,db.treatment.treatmentplan,db.treatment.startdate)
        tplanid = int(common.getid(trtmnt[0].treatmentplan)) if(len(trtmnt) > 0) else 0
        
        pats = db((db.vw_memberpatientlist.patientid==patientid)&(db.vw_memberpatientlist.primarypatientid==memberid)&(db.vw_memberpatientlist.is_active==True)).select(\
        db.vw_memberpatientlist.patient, db.vw_memberpatientlist.fullname, db.vw_memberpatientlist.hmopatientmember, \
        db.vw_memberpatientlist.cell, db.vw_memberpatientlist.email,db.company.onlinepayment,db.company.cashlesspayment,db.company.cashpayment,db.company.chequepayment,\
        left=db.company.on(db.company.id==db.vw_memberpatientlist.company))
        
        patient  = ""
        fullname = ""
        hmopatientmember = False
        cellno = ""
        email = ""
        
        #payment modes are dependant on the company
        online = True
        cashless = True
        cash = True
        cheque = True
        
        if(len(pats)>0):
            patient = pats[0].vw_memberpatientlist.patient
            fullname = pats[0].vw_memberpatientlist.fullname
            hmopatientmember = pats[0].vw_memberpatientlist.hmopatientmember        
            cellno = pats[0].vw_memberpatientlist.cell
            email = pats[0].vw_memberpatientlist.email
            online = common.getboolean(pats[0].company.onlinepayment)
            cashless = common.getboolean(pats[0].company.cashlesspayment)
            cash = common.getboolean(pats[0].company.cashpayment)
            cheque = common.getboolean(pats[0].company.chequepayment)

        #create a new payment
        paymentid = db.payment.insert(paymentdate=dttodaydate,paymentmode='Cash',patientmember=memberid,treatmentplan=tplanid,\
                                      provider=providerid,is_active=True,chequeno="0000",bankname="XXXX",accountname="XXXX",accountno="0000")
        

        #get list of payments made for this treatment
        payments = db((db.vw_paymentlist.is_active == True) & (db.vw_paymentlist.providerid == providerid) &\
                   (db.vw_paymentlist.treatmentid==treatmentid) & (db.vw_paymentlist.memberid==memberid) & \
                   (db.vw_paymentlist.patientid==patientid)).select(db.vw_paymentlist.paymentdate, db.vw_paymentlist.amount,db.vw_paymentlist.paymentmode,\
                                                                     db.vw_paymentlist.treatment,db.vw_paymentlist.patientname,db.vw_paymentlist.patientmember,\
                                                                     db.vw_paymentlist.treatmentid)
        

        paymentlist = []
        paymentobj = {}
        
        for payment in payments:
            paymentobj={
                
                "paymentdate":(payment.paymentdate).strftime("%d/%m/%Y"),
                "amount":float(common.getvalue(payment.amount)),
                "mode":payment.paymentmode,
                "treatment":payment.treatment,
                "patientname":payment.patientname,
                "patientmember":payment.patientmember,
                "treatmentid":int(common.getid(payment.treatmentid))
            }
            paymentlist.append(paymentobj)
            

        paytm = calculatepayments(db,tplanid,providerid)
        
        #get list of procedures for this treatment
        procobj = {}
        proclist = []
               

        procs = db((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.providerid  == providerid) & (db.vw_treatmentprocedure.is_active == True)).\
            select(db.vw_treatmentprocedure.procedurecode, db.vw_treatmentprocedure.altshortdescription, db.vw_treatmentprocedure.procedurefee,\
                   db.vw_treatmentprocedure.copay,db.vw_treatmentprocedure.inspays,db.vw_treatmentprocedure.status,\
                       db.vw_treatmentprocedure.treatmentdate)
        
        for proc in procs:
            
            procobj = {
                "code":proc.procedurecode,
                "desc":proc.altshortdescription,
                "procfee":float(common.getvalue(proc.procedurefee)),
                "copay":float(common.getvalue(proc.copay)),
                "inspays":float(common.getvalue(proc.inspays)),
                "status":proc.status,
                "trdate":(proc.treatmentdate).strftime("%d/%m/%Y")
            }
            proclist.append(procobj)   
    
        
        r = db(db.urlproperties.id > 0).select(db.urlproperties.fp_id,db.urlproperties.fp_merchantid,\
                                               db.urlproperties.fp_merchantdisplay,db.urlproperties.fp_apikey,\
                                               db.urlproperties.fp_produrl,db.urlproperties.fp_testurl
                                               )
       
        addln_info = {"paymentid":paymentid,"paymentdate":dttodaydate.strftime("%d/%m/%Y"),"invoiceamt":float(common.getvalue(paytm["treatmentcost"]))}
        
        paymentdata={
            
            "id": common.getstring(r[0].fp_id) if(len(r) > 0) else "",
            "apikey":common.getstring(r[0].fp_apikey) if(len(r) > 0) else "",
            "merchant_id": common.getstring(r[0].fp_merchantid) if(len(r) > 0) else "",
            "merchant_display":common.getstring(r[0].fp_merchantdisplay) if(len(r) > 0) else "",
            "invoice": (trtmnt[0].treatment + "_" + str(paymentid)) if(len(trtmnt) > 0) else "",
            "mobile_no":cellno,
            "email":email,
            "online":online,
            "cashless":cashless,
            "cash":cash,
            "cheque":cheque,            
            "note":"",            
            "payment_types":"",
            "fp_produrl": common.getstring(r[0].fp_produrl) if(len(r) > 0) else "",
            "fp_testurl": common.getstring(r[0].fp_testurl) if(len(r) > 0) else "",
            "treatmentocost":float(common.getvalue(paytm["treatmentcost"])),
            "treatment":common.getstring(trtmnt[0].treatment),
            "treatmentdate":common.getstring(trtmnt[0].startdate).strftime("%d/%m/%Y"),
            "copay":float(common.getvalue(paytm["copay"])),
            "inspays":float(common.getvalue(paytm["inspays"])),
            "totaltreatmentcost":float(common.getvalue(paytm["totaltreatmentcost"])),
            "totalinspays":float(common.getvalue(paytm["totalinspays"])),
            "totalcopay":float(common.getvalue(paytm["totalcopay"])),
            "totalpaid":float(common.getvalue(paytm["totalpaid"])),
            "totaldue":float(common.getvalue(paytm["totaldue"])),
            #"paymentlist":paymentlist,
            #"proclist":proclist,
            "addln_info":addln_info
        } 
        return json.dumps(paymentdata)
    
    
    
    #This method is called on callback from Payment Gateway when payment is completed.
    #callback data
    #When payment is made on netbanking
    #{
      #"amount": "1.0",
      #"payment_detail": "SBI",
      #"error_msg": null,
      #"addnl_detail": "{\"paymentid\":303,\"paymentdate\":\"11\\/01\\/2019\"}",
      #"sign": "1912cd06923e6fe59fa0d8fa7f87a1809db3bdab17568c941b39bae37371652818791f8d70309dc7a300b809a3c703055a77621f36c27f73d72ff48db40a7a96fc1a07b161e434ad7a5b65fed89234c0cabde1b2aa89af34310a45ad8327c8029cfaaaf7344a2bece008693879595ddacc36bc499a5ed0ddca1b9a9b6b4a373df6ad884f2e297b26990262312f493c4a3e0029236a11ae8326b0811685e1836b2e68c4add41d21e1a7a841acce65db80cc38028e22136be967c7802fbc64ffa145f0de81865bf577f4cd4ade722fdbd35ac0a3b7380cf9f996fd459f8193f7b0d0a5dca127863348e44fdb6360376eb96f9a51bd117abea5b3589777fec169d5",
      #"merchant_id": "FPTEST",
      #"payment_reference": "190111171111GPO",
      #"error": null,
      #"payment_type": "Netbanking",
      #"id": "FPTEST",
      #"invoice": "TRBLRB2C066100180220_303",
      #"merchant_display": "My Dental Plan",
      #"status": "S",
      #"chequeno":"0000",
      #"acctno":"0000",
      #"acctname":"XXXX",
      #"bankname":"MDP"
    #}
    
    #When payment is made on credit card
    #{
      #"amount": "1.0",
      #"payment_detail": "411111XXXXXX1111",
      #"error_msg": null,
      #"addnl_detail": "{\"paymentid\":305,\"paymentdate\":\"11\\/01\\/2019\"}",
      #"sign": "121b88d4cfbdf2d6aca6d4a6ea2b0855a4cc3083e5474bbe174083ae9280750bcb8bb26a410d6515b45f0ca96d44704bb30b7394b95b53e9a4969d256386f01fbb38f6a68f0a40b6597dc00fbdd275aba6b55875fd75a696d5b321fb1800f00bc5b6a4670cc27eed8bc0bde55f80e5e0669257f4be6fbaecd1637bff5407ab73b5087dd7509d24a9631bb10f492dce3e99c0cc847c225cd67c7a99f807dcd78c1088a732f5e522a6879e1f9228ca8f2f1933b7d27f4aa815270a72c8716e60dac072783d992ece389963133fc79a2a7d63e4c4a88cbb22d9c6dd5b6d7f4a06bc4b5bab5761a77e14df17fb1719ee7507434c2a2dfa7d89a65c96a43bb4639c2c",
      #"merchant_id": "FPTEST",
      #"payment_reference": "190111171350GPQ",
      #"error": null,
      #"payment_type": "Credit Card",
      #"id": "FPTEST",
      #"invoice": "TRBLRB2C066100180220_305",
      #"merchant_display": "My Dental Plan",
      #"status": "S",
      #"chequeno":"0000",
      #"acctno":"0000",
      #"acctname":"XXXX",
      #"bankname":"MDP"
      
    #}
    
    #When payment is made on UPI
    #{
      #"amount": "1.0",
      #"payment_detail": "",
      #"error_msg": null,
      #"addnl_detail": "{\"paymentid\":306,\"paymentdate\":\"11\\/01\\/2019\"}",
      #"sign": "73f6024307379922ff99170e75bc7665619589ee43b0be0c1e0c98b6815d3147f4dd4e145aa5a4a42b8e10a31ac50227e07d9ea21b600ce6eb8128d871aa7d5bf3071060f051e07d9c654021159b99f3b6f0d65834d8f254c8d82fff067ad8410594ba6c542781b966ed32859d8afce94b3a06c0cafdf1b5fddb1a453d594ac7fe981f1f9af4a5ee16146da5244e5eb7b6105eef54fdf3d732188c920be3434922eee3b397bc17e6be38595c0de1931b48dc0e606a950aaee51367d7a0cc8989a201916ec36a7da5d2fa7e1c6b573698e5e32ccac4a223fbeb5edd259bcdacd00b474f14c01173eb8b0641b0d185c1e1c9bd71674bc5d57b41b37ff4a443b4d3",
      #"merchant_id": "FPTEST",
      #"payment_reference": "190111171708GPR",
      #"error": null,
      #"payment_type": "UPI",
      #"id": "FPTEST",
      #"invoice": "TRBLRB2C066100180220_306",
      #"merchant_display": "My Dental Plan",
      #"status": "S",
      #"chequeno":"0000",
      #"acctno":"0000",
      #"acctname":"XXXX",
      #"bankname":"MDP"
    #}
    
    #When payment is made on WALLETS like PayZapp
    #{
      #"amount": "1.0",
      #"payment_detail": "PAYZAP",
      #"error_msg": null,
      #"addnl_detail": "{\"paymentid\":307,\"paymentdate\":\"11\\/01\\/2019\"}",
      #"sign": "33749711e4743b0fbe1c7682a64e4c88d85cd838fe7deb87b3a21f72f27372453fadee7e7c19c0d7f88055a13bb43f31c06bd94982be46bde143bfde77b425a89c313d354f331da0388316f0b0546d29ef356d27b960aae5b188fb259e750f9dbbe148bd76f43f97656f1b3531c078012aea411886ee74c651c79a2c844181f7af2f7121c588cb121d0ea7f34e17422e7a79f20779fc4bf79ec1cf5c75caa1ba1202072eaecbe53fc1e596560fce1ba31dfc6f60b76db19ca42b1a6536973b54d6827d5ac7f806b353531089c265467caf792ef65f630b9c589080e346390af622b9a9da0c6cd2cdcef3f0ac8abbeae805c8c9bf79cb89be8e3826c92a5b65ef",
      #"merchant_id": "FPTEST",
      #"payment_reference": "190111172032GPS",
      #"error": null,
      #"payment_type": "Other Wallet",
      #"id": "FPTEST",
      #"invoice": "TRBLRB2C066100180220_307",
      #"merchant_display": "My Dental Plan",
      #"status": "S",
      #"chequeno":"0000",
      #"acctno":"0000",
      #"acctname":"XXXX",
      #"bankname":"MDP"
    #}

    def paymentcallback(self,paymentdata):
    
        db = self.db
        providerid = self.providerid
        
        paymentcallbackobj = {}
        
        localcurrdate = common.getISTCurrentLocatTime()
        dttodaydate = datetime.datetime.strptime(localcurrdate.strftime("%d") + "/" + localcurrdate.strftime("%m") + "/" + localcurrdate.strftime("%Y"), "%d/%m/%Y")
        todaydate = dttodaydate.strftime("%d/%m/%Y")
        
        
       
        jsonConfirmPayment = paymentdata
        
        paymentref = common.getstring(jsonConfirmPayment['payment_reference']) if('payment_reference' in jsonConfirmPayment) else ""   #yes 
        paymenttype = common.getstring(jsonConfirmPayment['payment_type']) if('payment_type' in jsonConfirmPayment) else ""            #yes
        paymentdetail = common.getstring(jsonConfirmPayment['payment_detail']) if('payment_detail' in jsonConfirmPayment) else ""      #yes
        cardtype = common.getstring(jsonConfirmPayment['card_type']) if('card_type' in jsonConfirmPayment) else paymenttype            #?
        merchantid = common.getstring(jsonConfirmPayment['merchant_id']) if('merchant_id' in jsonConfirmPayment) else ""               #yes
        merchantdisplay = common.getstring(jsonConfirmPayment['merchant_display']) if('merchant_display' in jsonConfirmPayment) else "" #yes
        status = common.getstring(jsonConfirmPayment['status']) if('status' in jsonConfirmPayment) else ""    #yes
        invoice = common.getstring(jsonConfirmPayment['invoice']) if('invoice' in jsonConfirmPayment) else ""   #yes
        amount = 0 if(status != 'S') else (float(common.getvalue(jsonConfirmPayment['amount'])) if('amount' in jsonConfirmPayment) else 0)  #yes
        fee = 0    #if(status != 'S') else (common.getstring(jsonConfirmPayment['fee']) if('fee' in jsonConfirmPayment) else 0)   #no

        jsonObj = json.loads(common.getstring(jsonConfirmPayment['addln_detail']))  #yes
        paymentid = int(common.getstring(jsonObj["paymentid"]))  
        paymentdate = common.getstring(jsonObj['paymentdate']) if('paymentdate' in jsonObj) else "01/01/1900"       
        invoiceamt = float(common.getvalue(jsonObj['invoiceamt'])) if('invoiceamt' in jsonObj) else 0.00
        
        error = "" if(status =="S") else common.getstring(jsonConfirmPayment['error'])
        errormsg = "" if(status =="S") else common.getstring(jsonConfirmPayment['errormsg'])

        chequeno = common.getstring(jsonConfirmPayment['chequeno']) if('chequeno' in jsonConfirmPayment) else "0000"   #yes
        acctno = common.getstring(jsonConfirmPayment['acctno']) if('acctno' in jsonConfirmPayment) else "0000"   #yes
        acctname =common.getstring(jsonConfirmPayment['acctname']) if('acctname' in jsonConfirmPayment) else "XXXX"   #yes
        bankname =common.getstring(jsonConfirmPayment['bankname']) if('bankname' in jsonConfirmPayment) else "XXXX"   #yes
        
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
            providerinfo  = getproviderinformation(db,providerid)
            patientinfo = getpatientinformation(db,int(common.getid(r[0].patientid)),int(common.getid(r[0].memberid)))
            hmopatientmember = patientinfo["hmopatientmember"]
            
            doctortitle = common.getstring(r[0].doctortitle)
            doctorname  = common.getstring(r[0].doctorname)
    
    
            treatment = common.getstring(r[0].treatment)
            description = common.getstring(r[0].description)
            chiefcomplaint = common.getstring(r[0].chiefcomplaint)
            otherinfo = chiefcomplaint
                
        db(db.payment.id == paymentid).update(\
        
            fp_paymentref = paymentref,
            fp_paymentdate = datetime.datetime.strptime(paymentdate,"%d/%m/%Y"),
            fp_paymenttype = paymenttype,
            paymentmode = paymentdetail,
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
            fp_otherinfo = otherinfo
        
        )
        
        totalpaid = 0        
        totpaid = 0
        tottreatmentcost  = 0
        totinspays = 0    
        totaldue = 0
        
        if(status == 'S'):
            tp = db(db.treatmentplan.id == tplanid).select()
            if(len(tp)>0):
                totpaid = float(common.getstring(tp[0].totalpaid))
                tottreatmentcost = float(common.getstring(tp[0].totaltreatmentcost))
                totinspays = float(common.getstring(tp[0].totalinspays))
                totaldue = tottreatmentcost - (totpaid + float(amount) + totinspays)
                db(db.treatmentplan.id == tplanid).update(
                totalpaid = totpaid + float(amount),
                totaldue  = totaldue
            )
                    
        
        paymentcallbackobj = {
            "todaydate":todaydate,
            "providerid":providerid,
            "practicename":providerinfo["practicename"],
            "providername ":providerinfo["providername"],
            "provideregnon":providerinfo["providerregno"],
            "practiceaddress1":providerinfo["practiceaddress1"],
            "practiceaddress2":providerinfo["practiceaddress2"],
            "practicephone":providerinfo["practicephone"],
            "practiceemail":providerinfo["practiceemail"],
            "patientname":patientinfo["patientname"],
            "patientmember":patientinfo["patientmember"],
            "patientemail":patientinfo["patientemail"],
            "patientcell":patientinfo["patientcell"],
            "patientgender":patientinfo["patientgender"],
            "patientage":patientinfo["patientage"],
            "patientaddress":patientinfo["patientaddress"],
            "groupref":patientinfo["groupref"],
            "companyname":patientinfo["companyname"],
            "planname ":patientinfo["planname"],
            "doctorname ":doctorname,
            "treatment":treatment,
            "fp_paymentref": paymentref,
            "fp_paymentdate":paymentdate,
            "fp_paymenttype":paymenttype,
            "fp_paymentmode":paymentdetail,
            "fp_paymentdetail":paymentdetail,
            "fp_cardtype":cardtype,
            "fp_merchantid":merchantid,
            "fp_merchantdisplay":merchantdisplay,
            "fp_invoice":invoice,
            "fp_invoiceamt":invoiceamt,
            "fp_amount":amount,
            "fp_fee":fee,
            "fp_status":status,
            "fp_error":error,
            "fp_errormsg":errormsg,
            "fp_otherinfo":otherinfo ,           
            "chiefcomplaint":chiefcomplaint,
            "description":description,
            "chequeno":chequeno,
            "acctno":acctno,
            "acctname":acctname,
            "bankname":bankname,
            "totalpaid":totalpaid,
            "tottreatmentcost":tottreatmentcost,
            "totinspays":totinspays,
            "totaldue":totaldue,
            
        }
        
        return json.dumps(paymentcallbackobj)
            
            
    #Input Paymentid
    #Output
    ##"todaydate":todaydate,
    ##"providerid":providerid,
    #"practicename":providerinfo["practicename"],
    #"providername ":providerinfo["providername"],
    #"provideregnon":providerinfo["providerregno"],
    #"practiceaddress1":providerinfo["practiceaddress1"],
    #"practiceaddress2":providerinfo["practiceaddress2"],
    #"practicephone":providerinfo["practicephone"],
    #"practiceemail":providerinfo["practiceemail"],
    #"patientname":patientinfo["patientname"],
    #"patientmember":patientinfo["patientmember"],
    #"patientemail":patientinfo["patientemail"],
    #"patientcell":patientinfo["patientcell"],
    #"patientgender":patientinfo["patientgender"],
    #"patientage":patientinfo["patientage"],
    #"patientaddress":patientinfo["patientaddress"],
    #"groupref":patientinfo["groupref"],
    #"companyname":patientinfo["companyname"],
    #"planname ":patientinfo["planname"],
    #"doctorname ":doctorname,
    #"treatment":treatment,
    ##"fp_paymentref": paymentref,
    ##"fp_paymentdate":paymentdate,
    ##"fp_paymenttype":paymenttype,
    ##"fp_paymentmode":paymentdetail,
    ##"fp_paymentdetail":paymentdetail,
    ##"fp_cardtype":cardtype,
    ##"fp_merchantid":merchantid,
    ##"fp_merchantdisplay":merchantdisplay,
    ##"fp_invoice":invoice,
    ##"fp_invoiceamt":invoiceamt,
    ##"fp_amount":amount,
    ##"fp_fee":fee,
    ##"fp_status":status,
    ##"fp_error":error,
    ##"fp_errormsg":errormsg,
    ##"fp_otherinfo":otherinfo ,           
    ##"chiefcomplaint":chiefcomplaint,
    ##"description":description,
    ##"chequeno":chequeno,
    ##"acctno":acctno,
    ##"acctname":acctname,
    ##"bankname":bankname,
    ##"totalpaid":totalpaid,
    ##"tottreatmentcost":tottreatmentcost,
    ##"totinspays":totinspays,
    ##"totaldue":totaldue,
        
    def paymentreceipt(self, paymentid):
        
        
        db = self.db
        providerid = self.providerid
        
        localcurrdate = common.getISTCurrentLocatTime()
        dttodaydate = datetime.datetime.strptime(localcurrdate.strftime("%d") + "/" + localcurrdate.strftime("%m") + "/" + localcurrdate.strftime("%Y"), "%d/%m/%Y")
        todaydate = dttodaydate.strftime("%d/%m/%Y")
        
        payment = db(db.payment.id == paymentid).select()
        
        
        paymentref = common.getstring(payment[0].fp_paymentref) if(len(payment) == 1) else "" 
        paymenttype = common.getstring(payment[0].fp_paymenttype) if(len(payment) == 1) else "" 
        paymentdetail = common.getstring(payment[0].fp_paymentdetail) if(len(payment) == 1) else "" 
        paymentmode = common.getstring(payment[0].paymentmode) if(len(payment) == 1) else "" 
        cardtype = common.getstring(payment[0].fp_cardtype) if(len(payment) == 1) else ""           #?
        merchantid = common.getstring(payment[0].fp_merchantid) if(len(payment) == 1) else "" 
        merchantdisplay = common.getstring(payment[0].fp_merchantdisplay) if(len(payment) == 1) else "" 
        status = common.getstring(payment[0].fp_status) if(len(payment) == 1) else "Success" 
        invoice = common.getstring(payment[0].fp_invoice) if(len(payment) == 1) else "" 
        amount = 0 if(status != 'S') else (float(common.getvalue(payment[0].fp_amount)) if(len(payment) == 1) else 0)  #yes
        fee = 0 if(status != 'S') else (float(common.getvalue(payment[0].fp_fee)) if(len(payment) == 1) else 0)  #yes
        paymentdate = common.getstring((payment[0].paymentdate).strftime("%d/%m/%Y")) if(len(payment) == 1) else "01/01/1900"       
        invoiceamt = float(common.getvalue(payment[0].fp_invoiceamt)) if(len(payment) == 1) else 0.00
        otherinfo = common.getstring(payment[0].fp_otherinfo) if(len(payment) == 1) else "" 
        error = "" if(status =="S") else common.getstring(payment[0].fp_error)
        errormsg = "" if(status =="S") else common.getstring(payment[0].fp_errormsg)

        chequeno = common.getstring(payment[0].chequeno) if(len(payment) == 1) else "0000"
        acctno = common.getstring(payment[0].accountno) if(len(payment) == 1) else "0000"
        acctname =common.getstring(payment[0].accountname) if(len(payment) == 1) else "XXXX"
        bankname =common.getstring(payment[0].bankname) if(len(payment) == 1) else "XXXX"
        
        doctortitle = ''
        doctorname = ''
        treatment = ''
        chiefcomplaint = ''
        description = ''
    
        providerid = 0
        treatmentid = 0
        tplanid = 0
        patientinfo = None
        hmopatientmember = False
        
        proclist = []        

        r = db(db.vw_fonepaise.paymentid == paymentid).select()
        if(len(r)>0):
            
            treatmentid = int(common.getid(r[0].treatmentid))
            tplanid = int(common.getid(r[0].tplanid))
            providerid = int(common.getid(r[0].providerid))
            providerinfo  = getproviderinformation(db,providerid)
            patientinfo = getpatientinformation(db,int(common.getid(r[0].patientid)),int(common.getid(r[0].memberid)))
            #procedurelist = self.getprocedurelist(int(common.getid(r[0].memberid)), int(common.getid(r[0].patientid)),treatmentid)
            hmopatientmember = patientinfo["hmopatientmember"]
            
            doctortitle = common.getstring(r[0].doctortitle)
            doctorname  = common.getstring(r[0].doctorname)
    
    
            treatment = common.getstring(r[0].treatment)
            description = common.getstring(r[0].description)
            chiefcomplaint = common.getstring(r[0].chiefcomplaint)
            
                
       
       
            #get list of procedures for this treatment
            procs = db((db.vw_treatmentprocedure.treatmentid  == treatmentid) & \
                       (db.vw_treatmentprocedure.providerid  == providerid) & \
                       (db.vw_treatmentprocedure.is_active == True)) .select()        
                   
            proclist = []
            procobj = {}
            
            
            for proc in procs:
                
                procobj = {
                    "code": common.getstring(proc.procedurecode),
                    "description": common.getstring(proc.altshortdescription),
                    "procedurefee":float(common.getvalue(proc.procedurefee))
                    
                }
                
                proclist.append(procobj)         

        
        totalpaid = 0        
        totpaid = 0
        tottreatmentcost  = 0
        totinspays = 0    
        totaldue = 0
        
       
        tp = db(db.treatmentplan.id == tplanid).select()
        if(len(tp)>0):
            totpaid = float(common.getstring(tp[0].totalpaid))
            tottreatmentcost = float(common.getstring(tp[0].totaltreatmentcost))
            totinspays = float(common.getstring(tp[0].totalinspays))
            totaldue = tottreatmentcost - (totpaid + float(amount) + totinspays)
               
        
       
        paymentcallbackobj = {
            "todaydate":todaydate,
            "providerid":providerid,
            "practicename":providerinfo["practicename"],
            "providername ":providerinfo["providername"],
            "provideregnon":providerinfo["providerregno"],
            "practiceaddress1":providerinfo["practiceaddress1"],
            "practiceaddress2":providerinfo["practiceaddress2"],
            "practicephone":providerinfo["practicephone"],
            "practiceemail":providerinfo["practiceemail"],
            "patientname":patientinfo["patientname"],
            "patientmember":patientinfo["patientmember"],
            "patientemail":patientinfo["patientemail"],
            "patientcell":patientinfo["patientcell"],
            "patientgender":patientinfo["patientgender"],
            "patientage":patientinfo["patientage"],
            "patientaddress":patientinfo["patientaddress"],
            "groupref":patientinfo["groupref"],
            "companyname":patientinfo["companyname"],
            "planname ":patientinfo["planname"],
            "doctorname ":doctorname,
            "treatment":treatment,
            "fp_paymentref": paymentref,
            "fp_paymentdate":paymentdate,
            "fp_paymenttype":paymenttype,
            "fp_paymentmode":paymentmode,
            "fp_paymentdetail":paymentdetail,
            "fp_cardtype":cardtype,
            "fp_merchantid":merchantid,
            "fp_merchantdisplay":merchantdisplay,
            "fp_invoice":invoice,
            "fp_invoiceamt":invoiceamt,
            "fp_amount":amount,
            "fp_fee":fee,
            "fp_status":"Success" if(status == 'S') else status,
            "fp_error":error,
            "fp_errormsg":errormsg,
            "fp_otherinfo":otherinfo ,           
            "chiefcomplaint":chiefcomplaint,
            "description":description,
            "chequeno":chequeno,
            "acctno":acctno,
            "acctname":acctname,
            "bankname":bankname,
            "totalpaid":totalpaid,
            "tottreatmentcost":tottreatmentcost,
            "totinspays":totinspays,
            "totaldue":totaldue,
            "procedurelist":{"count":len(procs),"procedurelist":proclist}
            
        }
        
        return json.dumps(paymentcallbackobj)
        
def webmember_premium_paymentcallback(self,paymentdata):

    db = self.db
    providerid = self.providerid
    
    paymentcallbackobj = {}
    
    localcurrdate = common.getISTCurrentLocatTime()
    dttodaydate = datetime.datetime.strptime(localcurrdate.strftime("%d") + "/" + localcurrdate.strftime("%m") + "/" + localcurrdate.strftime("%Y"), "%d/%m/%Y")
    todaydate = dttodaydate.strftime("%d/%m/%Y")
   
    jsonConfirmPayment = paymentdata
    
    paymentref = common.getstring(jsonConfirmPayment['payment_reference']) if('payment_reference' in jsonConfirmPayment) else ""   #yes 
    paymenttype = common.getstring(jsonConfirmPayment['payment_type']) if('payment_type' in jsonConfirmPayment) else ""            #yes
    paymentdetail = common.getstring(jsonConfirmPayment['payment_detail']) if('payment_detail' in jsonConfirmPayment) else ""      #yes
    cardtype = common.getstring(jsonConfirmPayment['card_type']) if('card_type' in jsonConfirmPayment) else paymenttype            #?
    merchantid = common.getstring(jsonConfirmPayment['merchant_id']) if('merchant_id' in jsonConfirmPayment) else ""               #yes
    merchantdisplay = common.getstring(jsonConfirmPayment['merchant_display']) if('merchant_display' in jsonConfirmPayment) else "" #yes
    status = common.getstring(jsonConfirmPayment['status']) if('status' in jsonConfirmPayment) else ""    #yes
    invoice = common.getstring(jsonConfirmPayment['invoice']) if('invoice' in jsonConfirmPayment) else ""   #yes
    amount = 0 if(status != 'S') else (float(common.getvalue(jsonConfirmPayment['amount'])) if('amount' in jsonConfirmPayment) else 0)  #yes
    fee = 0    #if(status != 'S') else (common.getstring(jsonConfirmPayment['fee']) if('fee' in jsonConfirmPayment) else 0)   #no

    jsonObj = json.loads(common.getstring(jsonConfirmPayment['addln_detail']))  #yes
    paymentid = int(common.getstring(jsonObj["paymentid"]))  
    paymentdate = common.getstring(jsonObj['paymentdate']) if('paymentdate' in jsonObj) else "01/01/1900"       
    invoiceamt = float(common.getvalue(jsonObj['invoiceamt'])) if('invoiceamt' in jsonObj) else 0.00
    
    error = "" if(status =="S") else common.getstring(jsonConfirmPayment['error'])
    errormsg = "" if(status =="S") else common.getstring(jsonConfirmPayment['errormsg'])

    chequeno = common.getstring(jsonConfirmPayment['chequeno']) if('chequeno' in jsonConfirmPayment) else "0000"   #yes
    acctno = common.getstring(jsonConfirmPayment['acctno']) if('acctno' in jsonConfirmPayment) else "0000"   #yes
    acctname =common.getstring(jsonConfirmPayment['acctname']) if('acctname' in jsonConfirmPayment) else "XXXX"   #yes
    bankname =common.getstring(jsonConfirmPayment['bankname']) if('bankname' in jsonConfirmPayment) else "XXXX"   #yes
    
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
        providerinfo  = getproviderinformation(db,providerid)
        patientinfo = getpatientinformation(db,int(common.getid(r[0].patientid)),int(common.getid(r[0].memberid)))
        hmopatientmember = patientinfo["hmopatientmember"]
        
        doctortitle = common.getstring(r[0].doctortitle)
        doctorname  = common.getstring(r[0].doctorname)


        treatment = common.getstring(r[0].treatment)
        description = common.getstring(r[0].description)
        chiefcomplaint = common.getstring(r[0].chiefcomplaint)
        otherinfo = chiefcomplaint
            
    db(db.payment.id == paymentid).update(\
    
        fp_paymentref = paymentref,
        fp_paymentdate = datetime.datetime.strptime(paymentdate,"%d/%m/%Y"),
        fp_paymenttype = paymenttype,
        paymentmode = paymentdetail,
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
        fp_otherinfo = otherinfo
    
    )
    
    totalpaid = 0        
    totpaid = 0
    tottreatmentcost  = 0
    totinspays = 0    
    totaldue = 0
    
    if(status == 'S'):
        tp = db(db.treatmentplan.id == tplanid).select()
        if(len(tp)>0):
            totpaid = float(common.getstring(tp[0].totalpaid))
            tottreatmentcost = float(common.getstring(tp[0].totaltreatmentcost))
            totinspays = float(common.getstring(tp[0].totalinspays))
            totaldue = tottreatmentcost - (totpaid + float(amount) + totinspays)
            db(db.treatmentplan.id == tplanid).update(
            totalpaid = totpaid + float(amount),
            totaldue  = totaldue
        )
                
    
    paymentcallbackobj = {
        "todaydate":todaydate,
        "providerid":providerid,
        "practicename":providerinfo["practicename"],
        "providername ":providerinfo["providername"],
        "provideregnon":providerinfo["providerregno"],
        "practiceaddress1":providerinfo["practiceaddress1"],
        "practiceaddress2":providerinfo["practiceaddress2"],
        "practicephone":providerinfo["practicephone"],
        "practiceemail":providerinfo["practiceemail"],
        "patientname":patientinfo["patientname"],
        "patientmember":patientinfo["patientmember"],
        "patientemail":patientinfo["patientemail"],
        "patientcell":patientinfo["patientcell"],
        "patientgender":patientinfo["patientgender"],
        "patientage":patientinfo["patientage"],
        "patientaddress":patientinfo["patientaddress"],
        "groupref":patientinfo["groupref"],
        "companyname":patientinfo["companyname"],
        "planname ":patientinfo["planname"],
        "doctorname ":doctorname,
        "treatment":treatment,
        "fp_paymentref": paymentref,
        "fp_paymentdate":paymentdate,
        "fp_paymenttype":paymenttype,
        "fp_paymentmode":paymentdetail,
        "fp_paymentdetail":paymentdetail,
        "fp_cardtype":cardtype,
        "fp_merchantid":merchantid,
        "fp_merchantdisplay":merchantdisplay,
        "fp_invoice":invoice,
        "fp_invoiceamt":invoiceamt,
        "fp_amount":amount,
        "fp_fee":fee,
        "fp_status":status,
        "fp_error":error,
        "fp_errormsg":errormsg,
        "fp_otherinfo":otherinfo ,           
        "chiefcomplaint":chiefcomplaint,
        "description":description,
        "chequeno":chequeno,
        "acctno":acctno,
        "acctname":acctname,
        "bankname":bankname,
        "totalpaid":totalpaid,
        "tottreatmentcost":tottreatmentcost,
        "totinspays":totinspays,
        "totaldue":totaldue,
        
    }
    
    return json.dumps(paymentcallbackobj)
    