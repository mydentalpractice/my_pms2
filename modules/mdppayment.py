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
from applications.my_pms2.modules import account
from applications.my_pms2.modules import mdpbenefits
from applications.my_pms2.modules import mdprules

from applications.my_pms2.modules import mdputils
from applications.my_pms2.modules import logger

def getproviderinformation(db,providerid):
    
    provtitle = 'provtitle'
    providername = 'provname'
    providerregno = 'provregno'    
    
    pracname = ""
    pracaddress1 = ""
    pracaddress2 = ""
    
    pracphone = 'provphone'
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
    
    
    #def _calculatepayments(self,tplanid,policy=None):
        #logger.loggerpms2.info("Enter _calulate payment + " + str(tplanid))
        #db  = self.db
        #providerid = self.providerid
        #treatmentcost = 0
        #copay = 0
        #inspays = 0
        #companypays = 0
        #precopay = 0
        #walletamount = 0
        
        #totaltreatmentcost = 0
        #totalcopay = 0
        #totalprecopay = 0
        #totalinspays = 0
        #totaldue = 0
        #totalpaid = 0
        #totalcompanypays = 0
        #totalwalletamount = 0
        
        #respobj = {}
        #r = None
        #tplan = db(db.treatmentplan.id == tplanid).select()
        #try:
            #if(len(tplan) > 0):
                #treatmentcost = float(common.getvalue(tplan[0].totaltreatmentcost))
                #companypays = float(common.getvalue(tplan[0].totalcompanypays))
                #walletamount = float(common.getvalue(tplan[0].totalwalletamount))
                #precopay =float(common.getvalue(tplan[0].totalcopay))
                #copay = float(common.getvalue(tplan[0].totalcopay)) - companypays
                #inspays = float(common.getvalue(tplan[0].totalinspays))
                #memberid = int(common.getid(tplan[0].primarypatient))
                
                #r = db((db.vw_treatmentplansummarybytreatment.id == tplanid)).select()
                #if(len(r)>0):
                    #totaltreatmentcost = float(common.getvalue(r[0].totalcost))
                    #totalinspays = float(common.getvalue(r[0].totalinspays))
                    #totalcompanypays = float(common.getvalue(r[0].totalcompanypays))
                    #totalwalletamount = float(common.getvalue(r[0].totalwalletamount))
                    #totalprecopay = float(common.getvalue(r[0].totalcopay))
                    #totalcopay = float(common.getvalue(r[0].totalcopay)) - totalcompanypays - totalwalletamount
                    #totalpaid = float(common.getvalue(r[0].totalpaid))
                    #totaldue = totalcopay - totalpaid
                    
                 
                    #respobj["totaltreatmentcost"]=totaltreatmentcost
                    #respobj["totalinspays"]=totalinspays
                    #respobj["totalcompanypays"]=totalcompanypays
                    #respobj["totalwalletamount"]=totalwalletamount
                    #respobj["totalprecopay"]=totalprecopay
                    #respobj["totalcopay"]=totalcopay
                    #respobj["totalpaid"]=totalpaid
                    #respobj["totaldue"]=totaldue
                    
                    #respobj["treatmentcost"]=treatmentcost
                    #respobj["copay"]=copay
                    #respobj["precopay"]=precopay
                    #respobj["inspays"]=inspays
                    #respobj["companypays"]=companypays
                    
                    #respobj["result"] = "success"
                    #respobj["error_message"] = ""
                    
                #else:
                    #msg = "A_calculatepayments error for " + str(tplanid)
                    #respobj["result"] = "fail"
                    #respobj["error_message"] = msg
            #else:
                #msg = "B_calculatepayments error for " + str(tplanid)
                #respobj["result"] = "fail"
                #respobj["error_message"] = msg
                
                    
        #except Exception as e:
            #mssg = "_caluclatepayments Exception:\n" + str(e)
            #logger.loggerpms2.info(mssg)      
            #excpobj = {}
            #excpobj["result"] = "fail"
            #excpobj["error_message"] = mssg
            #return json.dumps(excpobj)             
                
                
        #logger.loggerpms2.info("Exit _calulatepayment " + json.dumps(respobj))
        #return json.dumps(respobj)
        

    
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
        logger.loggerpms2.info("Enter List Payments =>" + str(memberid) + " " + str(patientid))
        db = self.db
        providerid = self.providerid
        listpaymentsrspobj={}
        try:
            #this is list of treatment plans, since vw_payments.id is treatmentplan id
            #all total payments from tplan reflects all payments of the treatment since 
            #there is one treatment for one tplan
            if(providerid > 0):
                payments = db((db.vw_payments.providerid == providerid) & \
                              (db.vw_payments.memberid == memberid) & \
                              (db.vw_payments.patientid == patientid) & \
                              (db.vw_payments.is_active == True)).select()
            else:
                payments = db(\
                              (db.vw_payments.memberid == memberid) & \
                              (db.vw_payments.patientid == patientid) & \
                              (db.vw_payments.is_active == True)).select()
                
                
            payobj = {}
            
            paymentlist = []
            
            for payment in payments:
                treatmentid = int(common.getid(payment.treatmentid))
                providerid = int(common.getid(payment.providerid))
                hv = db(db.hv_treatment.treatmentid == treatmentid).count()
                
                payobj = {
            
                    "paymentid":int(common.getid(payment.id)),  #this is treatmentplan id
                    "memberid":memberid,
                    "patientid":patientid,
                    "patient":payment.patientname,
                    "paymentdate":None if(payment.lastpaymentdate == None) else (payment.lastpaymentdate).strftime("%d/%m/%Y"),
                    "treatmentid":int(common.getid(payment.treatmentid)),
                    "providerid":providerid,
                    "treatment":payment.treatment,
                    "treatmentdate":(payment.treatmentdate).strftime("%d/%m/%Y"),
                    "procedures":payment.shortdescription,
                    "totaltreatmentcost":float(common.getvalue(payment.totaltreatmentcost)),
                    "totalcopay":float(common.getvalue(payment.totalcopay)),
                    "totalinspays":float(common.getvalue(payment.totalinspays)),
                    "totalcompanypays":float(common.getvalue(payment.totalcompanypays)),
                    "totaldiscount":float(common.getvalue(payment.totalcompanypays)),
                    "totalpaid":float(common.getvalue(payment.totalpaid)),
                    "totaldue":float(common.getvalue(payment.totaldue)),
                    "hv":False if(hv == 0) else True,
                    "wallet_type":"SUPER_WALLET",
                    "totalwalletamount":float(common.getvalue(payment.totalwalletamount)),
                    "voucher_code":common.getstring(payment.voucher_code),
                    "totaldiscount_amount":float(common.getvalue(payment.totaldiscount_amount))
                    
                }
                paymentlist.append(payobj)
                
            listpaymentsrspobj = {"result":"success","error_message":"","paymentcount":len(payments), "paymentlist":paymentlist}
            
        except Exception as e:
            mssg = "List Payments Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)             
        
        dmp = json.dumps(listpaymentsrspobj)
        logger.loggerpms2.info("Exit List Payments " + dmp)
        return dmp

   

    def listpayments_fast(self, memberid, patientid):
        logger.loggerpms2.info("Enter List Payments =>" + str(memberid) + " " + str(patientid))
        db = self.db
        providerid = self.providerid
        listpaymentsrspobj={}
        voucher_code = ""
        promo_code = ""
        wallet_type = ""
        totalwalletamount = 0
        totaldiscount_amount = 0
        totalpromo_amount = 0
        
        try:
            #this is list of treatment plans, since vw_payments.id is treatmentplan id
            #all total payments from tplan reflects all payments of the treatment since 
            #there is one treatment for one tplan
            if(providerid > 0):
                payments = db((db.vw_payments_fast.providerid == providerid) & \
                              (db.vw_payments_fast.memberid == memberid) & \
                              (db.vw_payments_fast.patientid == patientid) & \
                              (db.vw_payments_fast.is_active == True)).select()
            else:
                payments = db(\
                              (db.vw_payments_fast.memberid == memberid) & \
                              (db.vw_payments_fast.patientid == patientid) & \
                              (db.vw_payments_fast.is_active == True)).select()
                
            
            payobj = {}
            
            paymentlist = []
            
            
            
            for payment in payments:

                treatmentid = payment.treatmentid
                tr = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
                tplanid = tr[0].treatmentplan if(len(tr) > 0) else 0
                paytm = json.loads(account._calculatepayments(db, tplanid))
                wallet_type = common.getstring(paytm["wallet_type"])
                voucher_code = common.getstring(paytm["voucher_code"])
                promo_code = common.getstring(paytm["promo_code"])
                totaldiscount_amount = float(common.getvalue(paytm["totaldiscount_amount"]))
                totalwalletamount = float(common.getvalue(paytm["totalwalletamount"]))
                totalpromo_amount = float(common.getvalue(paytm["totalpromo_amount"]))
                
                providerid = payment.providerid
                ts = db(db.treatment_procedure.treatmentid == treatmentid).select(db.dentalprocedure.shortdescription,\
                                                                                 left=(db.procedurepriceplan.on(db.procedurepriceplan.id == db.treatment_procedure.dentalprocedure),
                                                                                      db.dentalprocedure.on(db.dentalprocedure.dentalprocedure == db.procedurepriceplan.procedurecode)))
                
                shortdesc = ""
                for t in ts:
                    shortdesc = shortdesc + common.getstring(t.shortdescription) + ";"
                
                tp = db(db.treatmentplan.id == payment.id).select(db.treatmentplan.patientname)
                
                hv = db(db.hv_treatment.treatmentid == treatmentid).count()
                
                payobj = {
                    "paymentid":int(common.getid(payment.id)),  #this is treatmentplan id
                    "memberid":memberid,
                    "patientid":patientid,
                    "patient": "" if(len(tp) <=0 ) else tp[0].patientname,
                    "paymentdate":None if(payment.lastpaymentdate == None) else (payment.lastpaymentdate).strftime("%d/%m/%Y"),
                    "treatmentid":int(common.getid(payment.treatmentid)),
                    "providerid":int(common.getid(payment.providerid)),
                    
                    "treatment":payment.treatment,
                    "treatmentdate":(payment.treatmentdate).strftime("%d/%m/%Y"),
                    "procedures":shortdesc,
                    
                                   
                    
                    "totaltreatmentcost":float(common.getvalue(payment.totaltreatmentcost)),
                    "totalcopay":float(common.getvalue(payment.totalcopay)),
                    "totalinspays":float(common.getvalue(payment.totalinspays)),
                    "totalcompanypays":float(common.getvalue(payment.totalcompanypays)),
                    "totaldiscount":float(common.getvalue(payment.totalcompanypays)),
                    "totalpaid":float(common.getvalue(payment.totalpaid)),
                    "totaldue":float(common.getvalue(payment.totaldue)),
                    
                    "hv":False if(hv == 0) else True
                    
                    
                }
                paymentlist.append(payobj)
                
            listpaymentsrspobj = {
                                  "result":"success",
                                  "error_message":"",
                                  "paymentcount":len(payments), 
                                  "paymentlist":paymentlist,
                                  "wallet_type":wallet_type,
                                  "voucher_code":voucher_code,
                                  "promo_code":promo_code,
                                  "totalwalletamount":totalwalletamount,
                                  "totaldiscount_amount":totaldiscount_amount,
                                  "totalpromo_amount":totalpromo_amount
            }
            
        except Exception as e:
            mssg = "List Payments Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)             
        
        dmp = json.dumps(listpaymentsrspobj)
        logger.loggerpms2.info("Exit List Payments " + dmp)
        return dmp

        
    #paymentid is actually treatmentplan id
    def getpayment(self,paymentid): 
        logger.loggerpms2.info("Enter Get Payment " + str(paymentid))
        
        db = self.db
        providerid = self.providerid
        getpaymentrspobj = {}
        
        try:
            #paymentid = treatmentplan id. 
            #One tplan has one treatment which has one or more payments
            tplanid = paymentid
            
            #strsql = "SELECT * from vw_payments_fast where id = " + str(tplanid)
            #ds = db.executesql(strsql)
            
            r = db(db.vw_payments_fast.id == tplanid).select()
            providerid = int(r[0].providerid) if(len(r) >= 1) else 1
            #provs = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.groupregion)
            #regionid = int(common.getid(provs[0].groupregion)) if(len(provs) == 1) else 1
            #regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select(db.groupregion.groupregion)
            #regioncode = common.getstring(regions[0].groupregion) if(len(regions) == 1) else "ALL"
            
            memberid = int(common.getid(r[0].memberid if(len(r)>=1 ) else 0))
            patientid = int(common.getid(r[0].patientid if(len(r)>=1 ) else 0))
            treatmentid = int(common.getid(r[0].treatmentid if(len(r)>=1 ) else 0))
            #pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.company,db.vw_memberpatientlist.hmoplan)
            #companyid = int(common.getid(pats[0].company)) if(len(pats) == 1) else 0
            #companys = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
            #companycode = common.getstring(companys[0].company) if(len(companys) == 1) else "PREMWALKIN"
    
    
            ##for backward compatibility determine procedurepriceplancode from member's plan at the time of registration
            #hmoplanid = int(common.getid(pats[0].hmoplan)) if(len(pats) == 1) else 0  #this is the patient's previously assigned plan-typically at registration
            #hmoplans = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode)
            #hmoplancode = common.getstring(hmoplans[0].hmoplancode) if(len(hmoplans) == 1) else "PREMWALKIN"
            #r1 = db(
                #(db.provider_region_plan.companycode == companycode) &\
                #(db.provider_region_plan.plancode == hmoplancode) &\
                #((db.provider_region_plan.regioncode == regioncode)|(db.provider_region_plan.regioncode == 'ALL')) &\
                 #(db.provider_region_plan.is_active == True)).select()
            #plancode = r1[0].policy if(len(r1) == 1) else "PREMWALKIN"
            #policy = plancode
           
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
           
            
            benefit_amount = 0
            #calculate the discount for this member 
            #update the treatment, treatmentplan. 
            #There is an assumption that there will be no companypay from Plans 
            avars = {
                "action": "get_benefit",
                "member_id":str(memberid),
                "provider_id":str(providerid),
                "plan_code":policy,
                "rule_event":"rules_payment"
            }
        
            ruleObj = mdprules.Plan_Rules(db)
            benefit = json.loads(ruleObj.Get_Plan_Rules(avars))

            #reqobj = {
                #"action": "get_benefit",
                #"memberid":str(memberid),
                #"providerid":str(providerid)
            #}
            #bnftobj  = mdpbenefits.Benefit(db)
            #benefit = json.loads(bnftobj.get_benefits(reqobj))
            if(benefit['result'] == "success"):
                discount_amount = float(common.getkeyvalue(benefit,"discount_amount","0"))
                #update totalcompanypays (we are saving discount_amount as companypays )
                db(db.treatment.id == treatmentid).update(companypay = discount_amount)    
                #update treatmentplan assuming there is one treatment per tplan
                db(db.treatmentplan.id==tplanid).update(totalcompanypays = discount_amount) 
                db.commit()               
            
            paytm = json.loads(account._calculatepayments(db,tplanid)) 
            
            if(paytm["result"] == "fail"):
                mssg = paytm["error_message"]
                logger.loggerpms2.info(mssg)      
                excpobj = {}
                excpobj["result"] = "fail"
                excpobj["error_message"] = mssg
                return json.dumps(excpobj)            
            
            paymentsummary = {
                "totaltreatmentcost":paytm["totaltreatmentcost"],
                "totalinspays":paytm["totalinspays"],
                "totalcopay":paytm["totalcopay"],
                "totalpaid":paytm["totalpaid"],
                "totaldue":paytm["totaldue"],
                "totalprecopay":paytm["totalprecopay"],
                "totalcompanypays":paytm["totalcompanypays"],
                "totaldiscount":paytm["totalcompanypays"],
                "totalwalletamount":float(paytm["totalwalletamount"]),
                "totaldiscount_amount":float(paytm["totaldiscount_amount"]),
                "totalpromo_amount":float(paytm["totalpromo_amount"]),
                "voucher_code":common.getstring(paytm["voucher_code"]),
                "promo_code":common.getstring(paytm["promo_code"]),
                "wallet_type":common.getstring(paytm["wallet_type"]),                
            }
            
            #strsql = "SELECT * from vw_payments_fast where id = " + str(tplanid)
            #ds = db.executesql(strsql)            
            payments = db(db.vw_payments_fast.id == tplanid).select()
        

            
            payobj = {}
    
            paymentlist = []
            logger.loggerpms2.info("getpayme for payments loop " + str(len(payments)))
            for payment in payments:
                treatmentid = payment.treatmentid
                providerid = payment.providerid
                
                hv = db(db.hv_treatment.treatmentid == treatmentid).count()
                ts = db(db.treatment_procedure.treatmentid == treatmentid).select(db.dentalprocedure.shortdescription,\
                                                                                 left=(db.procedurepriceplan.on(db.procedurepriceplan.id == db.treatment_procedure.dentalprocedure),
                                                                                      db.dentalprocedure.on(db.dentalprocedure.dentalprocedure == db.procedurepriceplan.procedurecode)))
                
                shortdesc = ""
                for t in ts:
                    shortdesc = shortdesc + t.shortdescription + ";"
                
                tp = db(db.treatmentplan.id == payment.id).select(db.treatmentplan.patientname)
             
                
                payobj = {}
                payobj = {
                    "providerid":providerid,
                    "memberid":payment.memberid,
                    "patientid":payment.patientid,
                    "patient":"" if(len(tp) <=0 ) else tp[0].patientname,
                    "paymentdate":common.getstringfromdate(payment.lastpaymentdate ,"%d/%m/%Y"),
                    "treatmentid":payment.treatmentid,
                    "treatment":payment.treatment,
                    "treatmentdate":common.getstringfromdate(payment.treatmentdate,"%d/%m/%Y"),
                    "procedures":shortdesc,
                    "totaltreatmentcost":float(common.getvalue(payment.totaltreatmentcost)),
                    "totalcopay":float(common.getvalue(payment.totalcopay)),
                    "totalinspays":float(common.getvalue(payment.totalinspays)),
                    "totalpaid":float(common.getvalue(payment.totalpaid)),
                    "totaldue":float(common.getvalue(payment.totaldue)),
                    "totalcompanypays":float(common.getvalue(payment.totalcompanypays)),
                    "totaldiscount":float(common.getvalue(payment.totalcompanypays)),
                    "hv": False if(hv == 0) else True
                }
                paymentlist.append(payobj)
                
            getpaymentrspobj={"result":"success","error_message":"","paymentcount":len(payments), "paymentsummary":paymentsummary, "paymentlist":paymentlist}
                
        except Exception as e:
            mssg = "Get Payment Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)             
                
        dmp = json.dumps(getpaymentrspobj) 
        logger.loggerpms2.info("Exit Get Payment" + dmp)
        return dmp
    
    def getpaymentlist(self,memberid,patientid,treatmentid):
        logger.loggerpms2.info("Enter getpayment list " + str(memberid) + " " + str(patientid) + " " + str(treatmentid))
        db = self.db
        providerid = self.providerid
        
        #get list of payments made for this treatment
        payments = db((db.vw_paymentlist.is_active == True) & (db.vw_paymentlist.providerid == providerid) &\
                   (db.vw_paymentlist.treatmentid==treatmentid) & (db.vw_paymentlist.memberid==memberid) & \
                   (db.vw_paymentlist.patientid==patientid)).select(db.vw_paymentlist.ALL, orderby = ~(db.vw_paymentlist.paymentdate))
        
        paylist = []
        payobj = {}
        
        for payment in payments:
            #logger.loggerpms2.info("GetPyment list ")
            hv = db(db.hv_treatment.treatmentid == treatmentid).count()
            providerid = payment.providerid
            payobj = {
                "paymentdate": common.getISTFormatCurrentLocatTime().strftime("%d/%m/%Y") if(payment.paymentdate == None) else (payment.paymentdate).strftime("%d/%m/%Y"),
                "paymentid":int(common.getid(payment.id)),
                "amount":float(common.getvalue(payment.amount)),
                "mode":common.getstring(payment.paymentmode),
                "treatment":common.getstring(payment.treatment),
                "patient":common.getstring(payment.patientname),
                "providerid":providerid,
                "hv": False if(hv == 0) else True
               
            }
            
            paylist.append(payobj)
            
        #payment summary
        trtmnt = db(db.treatment.id == treatmentid).select(db.treatment.treatmentplan)
        tplanid = int(common.getid(trtmnt[0].treatmentplan))
        
        #paytm = calculatepayments(db, tplanid, providerid)
        paytm = json.loads(account._calculatepayments(db,tplanid))
        
        if(paytm["result"] == "success" )        :
            paymentsummary = {
                "totaltreatmentcost":paytm["totaltreatmentcost"],
                "totalinspays":paytm["totalinspays"],
                "totalcopay":paytm["totalcopay"],
                "totalpaid":paytm["totalpaid"],
                "totaldue":paytm["totaldue"],
                "totalprecopay":paytm["totalprecopay"],
                "totalcompanypays":paytm["totalcompanypays"],
                "totalwalletamount":float(paytm["totalwalletamount"]),
                "totaldiscount_amount":float(paytm["totaldiscount_amount"]),
                "totalpromo_amount":float(paytm["totalpromo_amount"]),
                "voucher_code":common.getstring(paytm["voucher_code"]),
                "promo_code":common.getstring(paytm["promo_code"]),
                "wallet_type":common.getstring(paytm["wallet_type"]),
                
            } 
        else:
            paymentsummary={}
  
        rspobj = {}
        rspobj["result"] = "success"
        rspobj["error_message"] = ""
        rspobj["count"] = len(paylist)
        rspobj["paymentlist"] = paylist
        rspobj["paymentsummary"] = paymentsummary
        
        
        logger.loggerpms2.info("Exit getpayment list " + json.dumps(rspobj))
        return json.dumps(rspobj)
    
    
    
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
     
        logger.loggerpms2.info("Enter New Payment ==>" + str(memberid) + " "  + str(patientid) + " "+str(treatmentid))
        
        db = self.db
        providerid = self.providerid
        paymentdata = {}
        try:
            
            rspobj = json.loads(mdputils.getplandetailsformember(db, providerid,memberid, patientid))
            policy = common.getkeyvalue(rspobj,"plancode","RPIP599")
            companycode = common.getkeyvalue(rspobj,"companycode","RPIP599")

            trtmnt = db(db.treatment.id == treatmentid).select()
            tplanid = int(common.getid(trtmnt[0].treatmentplan)) if(len(trtmnt) > 0) else 0
                                    
            voucher_code = trtmnt[0].voucher_code if(len(trtmnt) > 0) else ""
            discount_amount = float(common.getvalue(trtmnt[0].discount_amount)) if(len(trtmnt) > 0) else 0
                
            #get plan benefits - graded discount, flatdiscount(super wallet), cashback(mdp_wallet) 
            benefit_amount = 0
            avars = {
              
                "member_id":str(memberid),
                "plan_code":policy,
                "company_code":companycode,
                "treatmentid":treatmentid,
                "tplanid":tplanid,
                "rule_event":"get_plan_benefits"
            }
            ruleObj = mdprules.Plan_Rules(db)
            benefit = json.loads(ruleObj.Get_Plan_Rules(avars))
            
            if(benefit["result"]=="success"):
                logger.loggerpms2.info("New Payment - After GetPlanBenefits  - " + json.dumps(benefit))
                #mdp_wallet_cashback
                walletobj = common.getkeyvalue(benefit,"wallet", None)
                discount_amount = 0 if (walletobj == None) else float(common.getkeyvalue(walletobj,"mdp_wallet_amount_usable",0))
            
                #Super Wallet Cashback
                walletamount = 0 if (walletobj == None) else float(common.getkeyvalue(walletobj,"super_wallet_amount_usable",0))
            
                #planbenefit
                planbenefitobj = common.getkeyvalue(benefit,"planBenefits", None)
                companypays = 0 if ((planbenefitobj == None)|(len(planbenefitobj)==0)) else float(common.getkeyvalue(planbenefitobj[0],"discount_benefit_amount_usable",0))
            
            
                #update totalcompanypays (we are saving discount_amount as companypays )
                db(db.treatment.id == treatmentid).update(companypay = companypays, walletamount=walletamount,wallet_type = "SUPER_WALLET",
                                                          discount_amount=discount_amount,WPBA_response = json.dumps(benefit))    
            
                #update treatmentplan assuming there is one treatment per tplan
                db(db.treatmentplan.id==tplanid).update(totalcompanypays = companypays, totalwalletamount=walletamount,wallet_type = "SUPER_WALLET",
                                                        totaldiscount_amount=discount_amount) 
            
                db.commit()                
                
                #discount_amount = float(common.getkeyvalue(benefit, "discount_amount",0))
                ##update totalcompanypays (we are saving discount_amount as companypays )
                #db(db.treatment.id == treatmentid).update(companypay = discount_amount)    
                ##update treatmentplan assuming there is one treatment per tplan
                #db(db.treatmentplan.id==tplanid).update(totalcompanypays = discount_amount) 
                #db.commit()
                    

            dttodaydate = common.getISTFormatCurrentLocatDate()
            
            trtmnt = db(db.treatment.id == treatmentid).select()
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
            paymentmode = "Cashless"
            if(online==True):
                paymentmode = "Online"
            elif(cashless==True):
                paymentmode = "Cashless"
            elif(cash==True):
                paymentmode = "Cash"
            elif(cheque==True):
                paymentmode = "Cheque"
                
            paymentid = db.payment.insert(paymentdate=dttodaydate,paymentmode=paymentmode,patientmember=memberid,treatmentplan=tplanid,\
                                          provider=providerid,is_active=True,chequeno="0000",bankname="XXXX",accountname="XXXX",accountno="0000",policy=policy)
            
    
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
                
           
            paytm = json.loads(account._calculatepayments(db,tplanid))
            #logger.loggerpms2.info("New Payment paytm " + json.dumps(paytm))
            
            
            
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
            
            addln_info = {"paymentid":paymentid,"paymentdate":dttodaydate.strftime("%d/%m/%Y"),"invoiceamt":float(common.getvalue(common.getkeyvalue(paytm,"treatmentcost",0)))}

            #Is there a payment made against this Voucher Code
            pid = db((db.payment.treatmentplan == tplanid) & (db.payment.is_active == True)).select(db.payment.ALL, orderby=~db.payment.id)
            paymentcommit = bool(common.getboolean(pid[0].paymentcommit)) if(len(pid) > 0) else False
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
                "treatmentcost":float(common.getvalue(common.getkeyvalue(paytm,"treatmentcost",0))),
                "treatmentocost":float(common.getvalue(common.getkeyvalue(paytm,"treatmentcost",0))),
                "treatment":common.getstring(trtmnt[0].treatment) if(len(trtmnt) >0) else "",
                "treatmentdate":common.getstring(trtmnt[0].startdate).strftime("%d/%m/%Y") if(len(trtmnt) >0) else common.getISTFormatCurrentLocatTime().strftime("%d/%m/%Y %H:%M"),
                "copay":float(common.getvalue(common.getkeyvalue(paytm,"copay",0))),
                "inspays":float(common.getvalue(common.getkeyvalue(paytm,"inspays",0))),
                "totaltreatmentcost":float(common.getvalue(common.getkeyvalue(paytm,"totaltreatmentcost",0))),
                "totalinspays":float(common.getvalue(common.getkeyvalue(paytm,"totalinspays",0))),
                "totalcopay":float(common.getvalue(common.getkeyvalue(paytm,"totalcopay",0))),
                "totalpaid":float(common.getvalue(common.getkeyvalue(paytm,"totalpaid",0))),
                "totalcompanypays":float(common.getvalue(common.getkeyvalue(paytm,"totalcompanypays",0))),
                "totalwalletamount":float(common.getvalue(common.getkeyvalue(paytm,"totalwalletamount",0))),
                "totaldiscount_amount":float(common.getvalue(common.getkeyvalue(paytm,"totaldiscount_amount",0))),
                "totalprecopay":float(common.getvalue(common.getkeyvalue(paytm,"totalprecopay",0))),
                "totaldue":float(common.getvalue(common.getkeyvalue(paytm,"totaldue",0))),
                "voucher_code":voucher_code,
                "discount_amount":discount_amount,
                "precopay":float(common.getvalue(common.getkeyvalue(paytm,"precopay",0))),
                "companypays":float(common.getvalue(common.getkeyvalue(paytm,"companypays",0))),
                "walletamount":float(common.getvalue(common.getkeyvalue(paytm,"walletamount",0))),
                
                "paymentcommit":paymentcommit,
                "addln_info":addln_info
            } 
            
            paymentdata["benefit"] = benefit
            
        except Exception as e:
            mssg = "New Payment Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)             
        
        dmp = json.dumps(paymentdata)
        logger.loggerpms2.info("Exit New Payment ==>>" + dmp)
        return dmp
    
    
    
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
        logger.loggerpms2.info("Enter Paymentcallback " + json.dumps(paymentdata))
        db = self.db
        providerid = self.providerid
        
        paymentcallbackobj = {}
        discount_amount = 0
        
        try:
            dttodaydate = common.getISTFormatCurrentLocatDate()        
           
            
           
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
            
            memberid = 0
            patientid = 0
            company_code = ""
            policy = ""
            
            r = db(db.vw_fonepaise.paymentid == paymentid).select()
            if(len(r)>0):
                memberid = int(common.getid(r[0].patientid))
                patientid = int(common.getid(r[0].memberid))
                
                pats = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select()
                companyid = int(common.getid(pats[0].company)) if(len(pats) != 0) else 0
                c = db((db.company.id == companyid) & (db.company.is_active == True)).select()
                company_code = common.getstring(c[0].company) if(len(c) >0 ) else ""
                
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
                paymentcommit = True,
                precommitamount = 0,
                fp_paymentref = paymentref,
                fp_paymentdate = common.getdatefromstring(paymentdate,"%d/%m/%Y"),
                fp_paymenttype = paymenttype,
                #paymentmode = paymentdetail,
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
            db.commit()
           
            #here need to update treatmentplan tables
            account._updatetreatmentpayment(db, tplanid, paymentid)
            db.commit()             

            totalpaid = 0        
            totpaid = 0
            tottreatmentcost  = 0
            totinspays = 0    
            totaldue = 0
            totcompanypays = 0
            
            
            tp = db(db.treatmentplan.id == tplanid).select()
            memberid = int(common.getid(tp[0].primarypatient)) if(len(tp) >= 1) else 0
            if((status.lower() == "success")|(status.lower() == "s")):
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
                
                    #wallet_success
                    #reqobj = {}
                    #reqobj = {"paymentid" : paymentid}
                    #rspobj = json.loads(vcobj.wallet_success(reqobj))                 
                    ##here need to update treatmentplan tables
                    #account._updatetreatmentpayment(db, tplanid, paymentid)
                    #db.commit()                




                    #Call Benefit Success
                    trtmnt = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
                    discount_amount = trtmnt[0].companypay if(len(trtmnt) > 0) else 0
                    
                    pmnt = db((db.payment.id == paymentid) & (db.payment.is_active == True)).select()
                    policy = pmnt[0].policy if(len(pmnt) > 0) else ""
                    
                    obj={
                        "action":"benefit_success",
                        "paymentid":str(paymentid),
                        "plan_code":policy,
                        "company_code":company_code,
                        "discount_amount":str(discount_amount),
                        "member_id":str(memberid),
                        "treatmentid":str(treatmentid),
                        "rule_event":"benefit_success"
                    }
                    ruleObj = mdprules.Plan_Rules(db)
                    rspObj = json.loads(ruleObj.Get_Plan_Rules(obj))                       

                    if(rspObj['result'] == "success"):
                        #update totalcompanypays (we are saving discount_amount as companypays )
                        db(db.treatment.id == treatmentid).update(companypay = discount_amount) 
                        #update treatmentplan assuming there is one treatment per tplan
                        db(db.treatmentplan.id==tplanid).update(totalcompanypays = discount_amount) 
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
                    
                
                    #here need to update treatmentplan tables
                    account._updatetreatmentpayment(db, tplanid, paymentid)
                    db.commit()   
                   
                 
                   
                    
            else:    
                
                #call Voucher Failure
                obj = {"paymentid":paymentid}
                bnftobj = mdpbenefits.Benefit(db)
                rspObj = json.loads(bnftobj.voucher_failure(obj))
                
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
                rspObj = json.loads(bnftobj.benefit_failure(obj))
            
            paytm = json.loads(account._calculatepayments(db, tplanid))
            tottreatmentcost= paytm["totaltreatmentcost"]
            totinspays= paytm["totalinspays"]
            totpaid=paytm["totalpaid"] 
            totaldue = paytm["totaldue"]                         
            
            paymentcallbackobj = {
                "paytm":paytm,
                "paymentid":paymentid,
                "result":"success",
                "error_message":"",
                "todaydate":common.getstringfromdate(dttodaydate,"%d/%m/%Y"),
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
                "totalpaid":paytm["totalpaid"],
                "tottreatmentcost":paytm["totaltreatmentcost"],
                "totcompanypays":paytm["totalcompanypays"],
                "totinspays":paytm["totalinspays"],
                "totaldue":paytm["totaldue"],
                "discount_amount":paytm["discount_amount"],
                "walletamount":paytm["walletamount"]
                
            }
            
        except Exception as e:
            mssg = "Payment Callback Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)            
        
        dmp = json.dumps(paymentcallbackobj)
        logger.loggerpms2.info("Exit Payment Callback ==>" + dmp)
        return dmp
            
    #{paymentid, status}
    def razorpay_callback_transaction(self,avars):

        logger.loggerpms2.info("Enter Razor Pay callback_transaction API == >" + json.dumps(avars))
        db = self.db

        try:

            status = common.getkeyvalue(avars,"txn_response_msg","FAILURE")

            #get paymentid
            unique_merchant_txn_id = common.getkeyvalue(avars,"unique_merchant_txn_id","") 
            strarr = unique_merchant_txn_id.split('_')
            paymentid = 0 if(len(strarr)<=1) else int(common.getid(strarr[1]))

            




            p = db((db.payment.id == paymentid)).select() 
            tplanid = int(common.getid(p[0].treatmentplan)) if(len(p) != 0) else 0
            memberid = int(common.getid(p[0].patientmember)) if(len(p) != 0) else 0
            providerid = int(common.getid(p[0].provider)) if(len(p) != 0) else 0

            tr = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
            treatmentid = int(tr[0].id) if(len(tr) > 0) else 0

            amount = float(common.getvalue(p[0].precommitamount)) if(len(p) != 0) else 0

            rspobj = json.loads(mdputils.getplandetailsformember(db, providerid,memberid, patientid))
            policy = common.getkeyvalue(rspobj,"plancode","PREMWALKIN")
            company_code = common.getkeyvalue(rspobj,"companycode","PREMWALKIN")
                      
            #patobj = mdppatient.Patient(db, providerid)
            #rsp = json.loads(patobj.getMemberPolicy({"providerid":str(providerid),"memberid":str(memberid)}))
            #policy = common.getkeyvalue(rsp,"plan","PREMWALKIN")
            #company_code = common.getkeyvalue(rsp,"companycode","PREMWALKIN")
            

            logger.loggerpms2.info("Razor Pay Call Back Transaction API==>Amount " + str(amount) + " status " + status + " " + policy + " " + str(paymentid))

            paymentdate = common.getISTFormatCurrentLocatTime()
            if((status.lower() == "success")|(status.lower() == "s")):
                xsts = 'S'
                db((db.payment.id == paymentid)).update(fp_status = xsts,
                                                        paymentcommit = True,
                                                        fp_paymentdate =paymentdate ,
                                                        amount = amount,
                                                        fp_invoiceamt = amount,
                                                        fp_amount = amount, 
                                                        precommitamount = 0
                                                        )


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

                ##wallet_success
                #reqobj = {}
                #reqobj = {"paymentid" : paymentid}
                #rspobj = json.loads(vcobj.wallet_success(reqobj))                 
                ##here need to update treatmentplan tables
                #account._updatetreatmentpayment(db, tplanid, paymentid)
                #db.commit()                



                trtmnt = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
                discount_amount = trtmnt[0].companypay if(len(trtmnt) > 0) else 0

                pmnt = db((db.payment.id == paymentid) & (db.payment.is_active == True)).select()
                policy = pmnt[0].policy if(len(pmnt) > 0) else ""
                #obj={
                    #"paymentid":str(paymentid),
                    #"plan":policy,
                    #"discount_amount":str(discount_amount),
                    #"memberid":str(memberid),
                    #"treatmentid":str(treatmentid)
                #}
                #bnftobj = mdpbenefits.Benefit(db)
                #rspObj = json.loads(bnftobj.benefit_success(obj))
                
 
                obj={
                    "action":"benefit_success",
                    "paymentid":str(paymentid),
                    "plan_code":policy,
                    "company_code":company_code,
                    "discount_amount":str(discount_amount),
                    "member_id":str(memberid),
                    "treatmentid":str(treatmentid),
                    "rule_event":"benefit_success"
                }
                ruleObj = mdprules.Plan_Rules(db)
                rspObj = json.loads(ruleObj.Get_Plan_Rules(obj))                   
                                
                
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

                jsonresp = avars
                jsonresp["paytm"] = paytm
                jsonresp["paymentid"] = paymentid
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""



            else:
                db((db.payment.id == paymentid)).update(fp_status = status,
                                                        paymentcommit = False,
                                                        fp_paymentdate =paymentdate,
                                                        amount = 0,
                                                        #fp_invoiceamt = 0,
                                                        fp_amount = 0,  
                                                        precommitamount = 0

                                                        )

                #Call Voucher Failure
                vcobj = mdpbenefits.Benefit(db)
                reqobj = {"paymentid" : paymentid}
                rspobj = json.loads(vcobj.voucher_failure(reqobj))

                account._updatetreatmentpayment(db, tplanid,paymentid)

                jsonresp = avars
                jsonresp["result"] = "fail"
                jsonresp["error_message"] = common.getkeyvalue(avars,"message","Error in PineLabs Payment")


        except Exception as e:
            error_message = "Exit PineLabs callback_transaction API Exception " + str(e)
            logger.loggerpms2.info(error_message)      
            jsonresp = {
                "result":"fail",
                "error_message":error_message
            }
            return json.dumps(jsonresp)

        dmp = json.dumps(jsonresp)
        logger.loggerpms2.info("Exit Callback Transaction==>>" + dmp)
        return dmp      
   
        
    def paymentreceipt(self, paymentid):
        
        
        db = self.db
        providerid = self.providerid
        paymentcallbackobj = {}
        treatmentid = 0
        totalcompanypays = 0
        
        logger.loggerpms2.info("Enter Payment Receipt ==>" + str(paymentid) + " " + str(providerid))
        
        try:
            dttodaydate = common.getISTFormatCurrentLocatDate()  
            
            payment = db(db.payment.id == paymentid).select()
            
            
            paymentref = common.getstring(payment[0].fp_paymentref) if(len(payment) == 1) else "" 
            paymenttype = common.getstring(payment[0].fp_paymenttype) if(len(payment) == 1) else "" 
            paymentdetail = common.getstring(payment[0].fp_paymentdetail) if(len(payment) == 1) else "" 
            paymentmode = common.getstring(payment[0].paymentmode) if(len(payment) == 1) else "" 
            cardtype = common.getstring(payment[0].fp_cardtype) if(len(payment) == 1) else ""           #?
            merchantid = common.getstring(payment[0].fp_merchantid) if(len(payment) == 1) else "" 
            merchantdisplay = common.getstring(payment[0].fp_merchantdisplay) if(len(payment) == 1) else "" 
            status = common.getstring(payment[0].fp_status) if(len(payment) == 1) else "S" 
            
            
            invoice = common.getstring(payment[0].fp_invoice) if(len(payment) == 1) else "" 
            amount = 0 if(status.upper() != 'S') else (float(common.getvalue(payment[0].fp_amount)) if(len(payment) == 1) else 0)  #yes
            fee = 0 if(status.upper() != 'S') else (float(common.getvalue(payment[0].fp_fee)) if(len(payment) == 1) else 0)  #yes
            paymentdate = common.getstring((payment[0].paymentdate).strftime("%d/%m/%Y")) if(len(payment) == 1) else "01/01/1900"       
            invoiceamt = float(common.getvalue(payment[0].fp_invoiceamt)) if(len(payment) == 1) else 0.00
            otherinfo = common.getstring(payment[0].fp_otherinfo) if(len(payment) == 1) else "" 
            error = "" if(status.upper() =="S") else common.getstring(payment[0].fp_error)
            errormsg = "" if(status.upper() =="S") else common.getstring(payment[0].fp_errormsg)
    
            chequeno = common.getstring(payment[0].chequeno) if(len(payment) == 1) else "0000"
            acctno = common.getstring(payment[0].accountno) if(len(payment) == 1) else "0000"
            acctname =common.getstring(payment[0].accountname) if(len(payment) == 1) else "XXXX"
            bankname =common.getstring(payment[0].bankname) if(len(payment) == 1) else "XXXX"
            
            logger.loggerpms2.info("Enter Payment Receipt ==>A")
                                   
            doctortitle = ''
            doctorname = ''
            treatment = ''
            chiefcomplaint = ''
            description = ''
        
            
            treatmentid = 0
            tplanid = 0
            patientinfo = None
            hmopatientmember = False
            
            proclist = []        
            providerinfo  = getproviderinformation(db,providerid)    
            r = db(db.vw_fonepaise.paymentid == paymentid).select()
            if(len(r)>0):
                
                memberid = int(common.getid(r[0].memberid))
                patientid = int(common.getid(r[0].patientid))
                treatmentid = int(common.getid(r[0].treatmentid))
                tplanid = int(common.getid(r[0].tplanid))
                
                
              
                patientinfo = getpatientinformation(db,patientid,memberid)
                #procedurelist = self.getprocedurelist(int(common.getid(r[0].memberid)), int(common.getid(r[0].patientid)),treatmentid)
                hmopatientmember = patientinfo["hmopatientmember"]
                
                doctortitle = common.getstring(r[0].doctortitle)
                doctorname  = common.getstring(r[0].doctorname)
        
        
                treatment = common.getstring(r[0].treatment)
                description = common.getstring(r[0].description)
                chiefcomplaint = common.getstring(r[0].chiefcomplaint)
                
               
           
                #get list of procedures for this treatment
                procs = db((db.vw_treatmentprocedure.treatmentid  == treatmentid) & \
                           (db.vw_treatmentprocedure.is_active == True)) .select()        
                       
                proclist = []
                procobj = {}
                
                
                for proc in procs:
                    
                    procobj = {
                        "code": common.getstring(proc.procedurecode),
                        "description": common.getstring(proc.altshortdescription),
                        "procedurefee":float(common.getvalue(proc.copay))
                        
                    }
                    
                    proclist.append(procobj)         
    
            
            patresp  = json.loads(mdputils.getplandetailsformember(db,providerid,memberid, patientid))            
            
            #patobj = mdppatient.Patient(db, providerid)
            #patresp = json.loads(patobj.getMemberPolicy({"memberid":memberid,"providerid":providerid}))    

            tr = db(db.treatment.id == treatmentid).select()
            current_amount = (float(common.getid(tr[0].copay)) - float(common.getid(tr[0].inspay))) if(len(tr) > 0) else 0
            paytm = json.loads(account._calculatepayments(db,tplanid))

            xavars = {}
            xavars["member_id"] = memberid
            xavars["plan_code"] = common.getkeyvalue(patresp,"plancode","PREMWALKIN")
            xavars["amount"] = paytm["totalcopay"] - paytm["totalinspays"]
            xavars["current_amount"] = current_amount

            bnftObj = mdpbenefits.Benefit(db)
            
            wallet_balance= json.loads(bnftObj.getwallet_balance_1(xavars))
            
            
            
            paymentcallbackobj = {
                "todaydate":common.getstringfromdate(dttodaydate, "%d/%m/%Y"),
                "providerid":providerid,
                "practicename":providerinfo["practicename"] if(providerinfo != None) else "",
                "providername ":providerinfo["providername"] if(providerinfo != None) else "",
                "provideregnon":providerinfo["providerregno"] if(providerinfo != None) else "",
                "practiceaddress1":providerinfo["practiceaddress1"] if(providerinfo != None) else "",
                "practiceaddress2":providerinfo["practiceaddress2"] if(providerinfo != None) else "",
                "practicephone":providerinfo["practicephone"] if(providerinfo != None) else "",
                "practiceemail":providerinfo["practiceemail"] if(providerinfo != None) else "",
                "patientname":patientinfo["patientname"] if(providerinfo != None) else "",
                "patientmember":patientinfo["patientmember"] if(providerinfo != None) else "",
                "patientemail":patientinfo["patientemail"] if(patientinfo != None) else "",
                "patientcell":patientinfo["patientcell"] if(patientinfo != None) else "",
                "patientgender":patientinfo["patientgender"] if(patientinfo != None) else "",
                "patientage":patientinfo["patientage"] if(patientinfo != None) else "",
                "patientaddress":patientinfo["patientaddress"] if(patientinfo != None) else "",
                "groupref":patientinfo["groupref"] if(patientinfo != None) else "",
                "companyname":patientinfo["companyname"] if(patientinfo != None) else "",
                "planname ":patientinfo["planname"] if(patientinfo != None) else "",
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
                "totalpaid":paytm["totalpaid"],
                "tottreatmentcost":paytm["totaltreatmentcost"],
                "totinspays":paytm["totalinspays"],
                "totaldue":paytm["totaldue"],
                "totcompanypays":paytm["totalcompanypays"],
                "totdiscountamount":paytm["totaldiscount_amount"],
                "totalcopay":paytm["totalcopay"],
                
                "wallet_type":"SUPER_WALLET",
                "totalwalletamount":float(common.getvalue(paytm["totalwalletamount"])),
                "wallet_balance":wallet_balance,
                "procedurelist":{"count":len(procs),"procedurelist":proclist}
               
                
            }
        except Exception as e:
            mssg = "Payment Receipt Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)            
        
        dmp = json.dumps(paymentcallbackobj)
        logger.loggerpms2.info("Exit Payment Receipt ==>" + dmp)
        return dmp
    
    #this api is called with 
    #treatment id, wallet type and wallet to apply
    def apply_wallet(self,avars):

        logger.loggerpms2.info("Enter Apply Wallet API" + json.dumps(avars))

        db = self.db
        rspobj = {}

        try:

            #wallet type
            wallet_type = common.getkeyvalue(avars,"wallet_type","SUPER_WALLET")

            #wallet_amount
            walletamount = float(common.getkeyvalue(avars,"walletamount","0"))

            #treatment
            treatmentid = int(common.getkeyvalue(avars,"treatmentid","0"))
            tr = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select(db.treatment.id, db.treatment.copay,db.treatment.treatmentplan)

            #tplanid
            tplanid = tr[0].treatmentplan if(len(tr) > 0) else 0
            tp = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).select()    


            #get default provider 'P0001'
            p = db((db.provider.provider == 'P0001') & (db.provider.is_active == True)).select(db.provider.id)
            defproviderid = p[0].id if(len(p) > 0) else 0
            providerid = tp[0].provider if (len(tp) > 0) else defproviderid

            treatment_amount = tr[0].copay if (len(tr) > 0) else 0

            memberid = tp[0].primarypatient if (len(tp) > 0) else 0
            patientid = tp[0].patient if (len(tp) > 0) else 0
            mems = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.patientmember.city,\
                                                                                                       db.patientmember.st,db.patientmember.company)
           
            #get region code
            #provs = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.groupregion)
            #regionid = int(common.getid(provs[0].groupregion)) if(len(provs) == 1) else 1
            #regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select(db.groupregion.groupregion)
            #regioncode = common.getstring(regions[0].groupregion) if(len(regions) == 1) else "ALL"    
            
            ## get patient's company
            #pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == memberid)).select(db.vw_memberpatientlist.company,db.vw_memberpatientlist.hmoplan)
            #companyid = int(common.getid(pats[0].company)) if(len(pats) == 1) else 0
            #companys = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
            #companycode = common.getstring(companys[0].company) if(len(companys) == 1) else "PREMWALKIN"
            
            ##for backward compatibility determine procedurepriceplancode from member's plan at the time of registration
            #hmoplanid = int(common.getid(pats[0].hmoplan)) if(len(pats) == 1) else 0  #this is the patient's previously assigned plan-typically at registration
            #hmoplans = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode)
            #hmoplancode = common.getstring(hmoplans[0].hmoplancode) if(len(hmoplans) == 1) else "PREMWALKIN"
            #r = db(
               #(db.provider_region_plan.companycode == companycode) &\
               #(db.provider_region_plan.plancode == hmoplancode) &\
               #((db.provider_region_plan.regioncode == regioncode)|(db.provider_region_plan.regioncode == 'ALL')) &\
               #(db.provider_region_plan.is_active == True)).select()
            #plancode = r[0].policy if(len(r) == 1) else "PREMWALKIN"           
       
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
            walletbalance = float(common.getkeyvalue(rspobj,"super_wallet_cashback_balance",0))  
           
            
            #paytm = json.loads(account._calculatepayments(db, tplanid))
            #reqobj = {}
            #reqobj["action"] = "getwallet_balance"
            #reqobj["member_id"] = memberid
            #reqobj["plan_code"] = plancode
            #reqobj["amount"] = paytm["totalcopay"]
            
            #bnftobj = mdpbenefits.Benefit(db)
            
            #rspobj = json.loads(bnftobj.getwallet_balance(reqobj))
            #if(rspobj["result"] == "success"):
                #wlist = rspobj["wallet_list"]
            #else:
                #wlist = []


            #apply wallet
            db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).update(wallet_type = wallet_type, walletamount = walletamount)
            db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).update(wallet_type = wallet_type, totalwalletamount = walletamount)
            db.commit()
            
            
            
            paytm = json.loads(account._calculatepayments(db, tplanid))
            paytm["totalwalletamount"] = walletamount
            paytm["totalcopay"] = paytm["totalprecopay"] - paytm["walletamount"] 
            
            
            rspobj["totaltreatmentcost"] = paytm["totaltreatmentcost"]
            rspobj["totalinspays"] = paytm["totalinspays"]
            rspobj["totalcompanypays"] = paytm["totalcompanypays"]
            rspobj["totalwalletamount"] = paytm["totalwalletamount"]
            rspobj["totaldiscount_amount"] = paytm["totaldiscount_amount"]
            rspobj["totalprecopay"] = paytm["totalprecopay"]
            rspobj["totalcopay"] = paytm["totalcopay"]
            rspobj["totalpaid"] = paytm["totalpaid"]
            rspobj["totaldue"] = paytm["totaldue"]
            rspobj["result"] = "success"
            rspobj["error_message"] = ""
            
           

        except Exception as e:
            mssg = "Apply Wallet API Exception" + str(e)
            logger.loggerpms2.info(mssg)      
            rspobj = {}
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg

        mssg = json.dumps(rspobj)
        logger.loggerpms2.info("Exit Apply Wallet API " + mssg)  
        return mssg
    
 
    def paymentcallback_0(self,avars):
    
        logger.loggerpms2.info("Enter  paymentcallback_0 API == >" + json.dumps(avars))
        db = self.db
    
        try:
             
            
            paymentid = int(common.getkeyvalue(avars,"paymentid",0))
            amount = float(common.getkeyvalue(avars,"amount",0))
    
            p = db((db.payment.id == paymentid)).select() 
            tplanid = int(common.getid(p[0].treatmentplan)) if(len(p) != 0) else 0
            memberid = int(common.getid(p[0].patientmember)) if(len(p) != 0) else 0
            patientid = int(common.getid(p[0].patientmember)) if(len(p) != 0) else 0
            pats = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select()
            companyid = int(common.getid(pats[0].company)) if(len(pats) != 0) else 0
            c = db((db.company.id == companyid) & (db.company.is_active == True)).select()
            company_code = common.getstring(c[0].company) if(len(c) >0 ) else ""    

            providerid = int(common.getid(p[0].provider)) if(len(p) != 0) else 0
    
            tr = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
            treatmentid = int(tr[0].id) if(len(tr) > 0) else 0
    
            rsp = json.loads(mdputils.getplandetailsformember(db, providerid, memberid, patientid))
            #patobj = mdppatient.Patient(db, providerid)
            #rsp = json.loads(patobj.getMemberPolicy({"providerid":str(providerid),"memberid":str(memberid)}))
            policy = common.getkeyvalue(rsp,"plancode","PREMWALKIN")
            status = 'S'
            logger.loggerpms2.info("paymentcallback_0 API==>Amount " + str(amount) + " status " + status + " " + policy + " " + str(paymentid))
    
            paymentdate = common.getISTFormatCurrentLocatTime()
            xsts = 'S'
            db((db.payment.id == paymentid)).update(fp_status = xsts,
                                                    paymentcommit = True,
                                                    fp_paymentdate =paymentdate ,
                                                    amount = amount,
                                                    fp_invoiceamt = amount,
                                                    fp_amount = amount, 
                                                    precommitamount = 0
                                                    )


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

            #wallet_success
            #reqobj = {}
            #reqobj = {"paymentid" : paymentid}
            #rspobj = json.loads(vcobj.wallet_success(reqobj))                 
            ##here need to update treatmentplan tables
            #account._updatetreatmentpayment(db, tplanid, paymentid)
            #db.commit()                

            trtmnt = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
            discount_amount = trtmnt[0].companypay if(len(trtmnt) > 0) else 0

            #pmnt = db((db.payment.id == paymentid) & (db.payment.is_active == True)).select()
            #policy = pmnt[0].policy if(len(pmnt) > 0) else ""
            
            obj={
                "action":"benefit_success",
                "paymentid":str(paymentid),
                "plan_code":policy,
                "company_code":company_code,
                "discount_amount":str(discount_amount),
                "member_id":str(memberid),
                "treatmentid":str(treatmentid),
                "rule_event":"benefit_success"
            }
            ruleObj = mdprules.Plan_Rules(db)
            rspObj = json.loads(ruleObj.Get_Plan_Rules(obj))                       
            
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

            jsonresp = avars
            jsonresp["paytm"] = paytm
            jsonresp["paymentid"] = paymentid
            jsonresp["result"] = "success"
            jsonresp["error_message"] = ""
    
        except Exception as e:
            error_message = "Exit paymentcallback_0 API Exception " + str(e)
            logger.loggerpms2.info(error_message)      
            jsonresp = {
                "result":"fail",
                "error_message":error_message
            }
            return json.dumps(jsonresp)
    
        dmp = json.dumps(jsonresp)
        logger.loggerpms2.info("Exit paymentcallback_0 API==>>" + dmp)
        return dmp
        
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
    
   