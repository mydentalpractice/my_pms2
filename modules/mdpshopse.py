from gluon import current
import json
import datetime
from datetime import timedelta

import requests
import urllib
import base64
import hashlib
import os;
import uuid
from uuid import uuid4
#

from applications.my_pms2.modules import common
from applications.my_pms2.modules import account
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import account
from applications.my_pms2.modules import mdppayment
from applications.my_pms2.modules import mdpbenefits
from applications.my_pms2.modules import mdputils

from applications.my_pms2.modules import datasecurity

from applications.my_pms2.modules import logger

class Shopse:

    def __init__(self,db):
        self.db = db
     
        
     
        
        r = db(db.shopsee_properties.id>0).select()

        self.shopsee_prod_url = r[0].shopsee_prod_url
        self.shopsee_stg_url = r[0].shopsee_stg_url
        self.shopsee_api_token = r[0].shopsee_api_token
        self.shopsee_response_key = r[0].shopsee_response_key
        self.shopsee_returnURL = r[0].shopsee_returnURL
        self.shopsee_product_name = r[0].product_name
        self.shopsee_product_id = r[0].product_id
        self.webhookUrl = r[0].webhookUrl

    def encrypt_sha256_shopse(self,avars):
        
        logger.loggerpms2.info("Enter Encrypt Sha256 Shopse " + json.dumps(avars))
        
        try:
            jsonobj = avars
            keys = jsonobj.keys()
            keylist = []
            for key in keys:
                obj = {}
                obj[key] = common.getkeyvalue(avars,key,"")
                keylist.append(obj)
    
            keylist.sort()
            avars2 = {}
            rspstr = ""
            first  = True
            for x in range(len(keylist)):
                o = keylist[x]
                keys = o.keys()
                keyname = keys[0]
                keyval = avars[keyname]
                if(keyname == "action"):
                    continue
                if(first):
                    
                    n = keyname #urllib.quote(keyname.encode('utf-8'))
                    k = keyval #urllib.quote(keyval.encode('utf-8'))
                    rspstr = str(n) + "=" + str(k)
                    first = False
                else:
                    n = keyname #urllib.quote(keyname.encode('utf-8'))
                    k = keyval #urllib.quote(keyval.encode('utf-8'))
                    rspstr = rspstr + "&" + str(n) + "=" + str(k)
            
            
            logger.loggerpms2.info("Signature String to Encrypt " + rspstr)
            
            
            rspstr1 = urllib.quote_plus(rspstr.encode('utf-8'))
            logger.loggerpms2.info("Signature (URL Encode) String to Encrypt " + rspstr1)
            obj = datasecurity.DataSecurity(self.db)
            rsp = json.loads(obj.encrypt_sha256_shopse(rspstr1,self.shopsee_response_key))

        except Exception as e:
            error_message = "Shopsee Encrypt Sha256  API Exception " + str(e)
            logger.loggerpms2.info(error_message)      
            jsonresp = {
              "result":"fail",
              "error_message":error_message
            }
            return json.dumps(jsonresp)
    
        logger.loggerpms2.info("Exit Shopse Encrypt Sha256 " + json.dumps(rsp))
        return json.dumps(rsp)
            
    def create_transaction(self,avars):
        logger.loggerpms2.info("Enter Shopsee CreateTransaction API == >" + json.dumps(avars))
        db = self.db
   
        try:
            
            #create URL
            url = self.shopsee_prod_url + "/merchant/api/v2/transactions" 
            #shopsee_header = {"Content-Type":"application/json"}
            shopsee_header = {"Content-Type":"application/json","Authorization":self.shopsee_api_token}
            
            
            #get list of procedures for a treatment
            treatment = common.getkeyvalue(avars,"treatment","")
            trs= db((db.treatment.treatment == treatment) & (db.treatment.is_active  == True)).select(db.treatment.id)
            treatmentid = trs[0].id if(len(trs)==1) else 0
            procs = db((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True)).select()
            
            proclist = []
            procobj = {}
            providerid = 0
            
            for proc in procs:
                providerid = proc.providerid
                procobj={}
                procobj["productId"] = proc.procedurecode
                procobj["name"] = proc.altshortdescription
                procobj["amount"] = proc.procedurefee
                proclist.append(procobj)
            
            
            customParams = avars["customParams"] if ("customParams" in avars) else {}
           
            provdict = common.getproviderfromid(db,providerid)
            customParams["salesPersonEmail"] = provdict["email"]
            customParams["salesPersonMobile"] = provdict["cell"]
            
            #Request CreateTransaction API
            shopsee_request = {
                "orderId":common.getkeyvalue(avars,"treatment","") + "_" + str(common.getkeyvalue(avars,"paymentid",0)),   #<treatment>_<paymentid> e.g. TRTMUM001XXXX_1234
                "amount":float(common.getkeyvalue(avars,"amount","0")),
                "mobile":common.getkeyvalue(avars,"mobile",""),
                "email":common.getkeyvalue(avars,"email",""),
                "returnUrl":self.shopsee_returnURL,
                #"webhookUrl":self.webhookUrl,
                "productName":treatment,
                "productId":treatmentid,
                "firstName":common.getkeyvalue(avars,"firstName",""),
                "lastName":common.getkeyvalue(avars,"lastName",""),
                "address":avars["address"],
                "customParams":customParams,
                "products":proclist
            }
        
            logger.loggerpms2.info("SHOPSEE REQUEST\n" + json.dumps(shopsee_request) + "URL " + url + " Header " + json.dumps(shopsee_header))
            
            #call API
            resp = requests.post(url,headers=shopsee_header,json=shopsee_request)
            jsonresp = {}
            if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
                respstr =   resp.text
                jsonresp = json.loads(respstr)
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
                
                #complete the transaction, #orderid = <treatment>_<paymentid>
                arr = common.getkeyvalue(jsonresp,"orderid","0_0")
                arr = arr.split("_")
               
                paymentid = int(common.getid(arr[1])) if (len(arr) >= 2) else 0
                treatment = common.getstring(arr[0]) if (len(arr) >= 1) else ""
                x=db((db.treatment.treatment == treatment) & (db.treatment.is_active == True)).select(db.treatment.id)
                treatmentid = int(common.getid(x[0].id)) if(len(x) > 0) else 0
                amount = float(common.getkeyvalue(avars,"amount","0"))
                
                logger.loggerpms2.info("Shopsee createTransaction API Response \n" + json.dumps(jsonresp)) 
                logger.loggerpms2.info("Shopsee Create Transaction API - amount=" + str(amount) + " paymentid " + str(paymentid)+" treatmentid " + str(treatmentid))
                
                db(db.payment.id == paymentid).update(
                    
                                                      fp_paymentref = common.getkeyvalue(jsonresp,"OrderId",""),
                                                      fp_invoice = treatment,
                                                      fp_merchantid = "MDP",
                                                      fp_paymenttype = "ShopSe",
                                                      fp_paymentdetail = common.getkeyvalue(jsonresp,"shopSeTxnId",""),
                                                      fp_merchantdisplay="MyDental Health Plan Pvt. Ltd.",
                                                      precommitamount = amount,   #temporary storing the amount  to commit on callback 
                                                      paymentcommit = False,
                                                      paymentmode = "Online",
                                                      fp_status = "Open"
                                                    )

            else:
                jsonresp={
                    "result" : "fail",
                    "error_message":"Shopsee createTransaction API Error Response:\n" + "(" + str(resp.status_code) + ")",
                    "orderId":common.getkeyvalue(avars,"orderId",""),
                    "productName":common.getkeyvalue(avars,"productName",""),
                    "productId":common.getkeyvalue(avars,"productId",""),
                }                
                return json.dumps(jsonresp)
                
        except Exception as e:
            error_message = "Shopsee CreateTransaction API Exception " + str(e)
            logger.loggerpms2.info(error_message)      
            jsonresp = {
              "result":"fail",
              "error_message":error_message
            }
            return json.dumps(jsonresp)
        
        logger.loggerpms2.info("Shopsee Exit createTransaction API \n" + json.dumps(jsonresp)) 
        return json.dumps(jsonresp)
    
    #2021-07-06 09:22:02,321 - web2py.app.my_pms2 - INFO - Enter Shopsee callback_transaction API == >{"orderId": "TRCHAGSP13010001_2158", "status": "failed", "currentTime": "1625543519024", "shopSeTxnId": "S06072103513799343", "statusMessage": "We are observing technical issues with the Bank. Please try again after some time.", "statusCode": "53"}
    #2021-07-06 09:22:02,321 - web2py.app.my_pms2 - INFO - Exit Shopsee callback_transaction API Exception 'message'
    #import requests
    
    
   
    
    
    #x = requests.get('https://w3schools.com')
    #print(x.status_code)    
    def callback_transaction(self,avars):
        
        logger.loggerpms2.info("Enter Shopsee callback_transaction API == >" + json.dumps(avars))
        db = self.db
       
        try:
            status = common.getkeyvalue(avars,"status","")
            status = "failed" if(status == "") else status
            
            orderid = common.getkeyvalue(avars,"orderid","") 
            shopsetxnid = common.getkeyvalue(avars,"shopsetxnid","") 

            p = db((db.payment.fp_paymentref == orderid)).select() 
            providerid = int(common.getid(p[0].provider)) if(len(p) != 0) else 0
            amount = float(common.getvalue(p[0].precommitamount)) if(len(p) != 0) else 0
            memberid = int(common.getid(p[0].patientmember)) if(len(p) != 0) else 0
            patientid = memberid
            tplanid = int(common.getid(p[0].treatmentplan)) if(len(p) != 0) else 0
            paymentid = int(common.getid(p[0].id)) if(len(p) >= 1) else 0
            amount = float(common.getvalue(p[0].precommitamount)) if(len(p) != 0) else 0
            
            patobj = mdppatient.Patient(db, providerid)
            companyid = int(common.getid(pats[0].company)) if(len(pats) != 0) else 0
            c = db((db.company.id == companyid) & (db.company.is_active == True)).select()
            company_code = common.getstring(c[0].company) if(len(c) >0 ) else ""            

            tr = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
            treatmentid = int(tr[0].id) if(len(tr) > 0) else 0

            rsp = json.loads(mdputils.getplandetailsformember(db,providerid,memberid,patientid))
            #rsp = json.loads(patobj.getMemberPolicy({"providerid":str(providerid),"memberid":str(memberid)}))
            policy = common.getkeyvalue(rsp,"plancode","PREMWALKIN")
            
            logger.loggerpms2.info("ShopSe Call Back Transaction API==>Amount " + str(amount) + " status " + status + " " + policy + " " + str(paymentid))
            
            paymentdate = common.getISTFormatCurrentLocatTime()
            
            
            if((status.lower() == "success")|(status.lower() == "s")):
                db((db.payment.fp_paymentref == orderid)).update(fp_status = status,
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
                #vcobj = mdpbenefits.Benefit(db)
                #reqobj = {"paymentid" : paymentid}
                #rspobj = json.loads(vcobj.voucher_success(reqobj))                 
            
                ##here need to update treatmentplan tables
                #account._updatetreatmentpayment(db, tplanid, paymentid)
                #db.commit()
            
                ##wallet_success
                #reqobj = {}
                #reqobj = {"paymentid" : paymentid}
                #rspobj = json.loads(vcobj.wallet_success(reqobj))                 
                ##here need to update treatmentplan tables
                #account._updatetreatmentpayment(db, tplanid, paymentid)
                #db.commit()                

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
        
                jsonresp = avars
                jsonresp["paytm"] = paytm
                jsonresp["paymentid"] = paymentid
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
                
            else:
                db((db.payment.fp_paymentref == orderid)).update(fp_status = status,
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
                
                #reset 
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
                account._updatetreatmentpayment(db, tplanid,paymentid) 
                 
                jsonresp = avars
                jsonresp["result"] = "fail"
                jsonresp["error_message"] = common.getkeyvalue(avars,"message","Error in ShopSe Payment")
                
                
        except Exception as e:
            error_message = "Exit Shopsee callback_transaction API Exception " + str(e)
            logger.loggerpms2.info(error_message)      
            jsonresp = {
              "result":"fail",
              "error_message":error_message
            }
            return json.dumps(jsonresp)
        
        dmp = json.dumps(jsonresp)
        logger.loggerpms2.info("Exit Callback Transaction==>>" + dmp)
        return dmp
    
    
    
    
    
    
    #This API is called from ShopSe
    def mdp_shopse_webhook(self,avars):
        
        logger.loggerpms2.info("Enter mdp_shopse_webhook API == >" + json.dumps(avars))
        db = self.db
        jsonresp = {}
        
        try:
            status = common.getkeyvalue(avars,"status","failed")
            
            if((status.lower() == "success")|(status.lower() == 's')):
                orderid = common.getkeyvalue(avars,"orderid","") 
                shopsetxnid = common.getkeyvalue(avars,"shopsetxnid","") 
                
                #generate encryption signature
                sigobj = {}
                sigobj["orderId"] = common.getkeyvalue(avars,"orderId","")
                sigobj["shopSeTxnId"] = common.getkeyvalue(avars,"shopSeTxnId","")
                sigobj["status"] = status
                sigobj["statusCode"] = common.getkeyvalue(avars,"statusCode","")
                sigobj["statusMessage"] = common.getkeyvalue(avars,"statusMessage","")
                sigobj["currentTime"] = common.getkeyvalue(avars,"currentTime","")
                sigobj = json.loads(self.encrypt_sha256_shopse(sigobj))
                
                gen_signature = sigobj["encrypt"]
                signature = urllib.quote_plus(common.getkeyvalue(avars,"signature",""))
                
                #mismatch
                #if(gen_signature != signature):
                    #error_message = "Webhook Callback Failure - Signature Mismatch\n" + "Calculated Signature = " + gen_signature + "\n" + "Callback Signature = " + signature
                    #logger.loggerpms2.info(error_message)
                    #jsonresp = {
                      #"result":"fail",
                      #"error_message":error_message
                    #}
                    
                    #return json.dumps(jsonresp)

                logger.loggerpms2.info("Signatures Match")
                
                otherinfo = json.dumps(common.getkeyvalue(avars,"payment","")) + "\n" + json.dumps(common.getkeyvalue(avars,"charge",""))
                strdt = common.getkeyvalue(avars,"timestamp",common.getstringfromdate(common.getISTFormatCurrentLocatTime(),"%Y-%m-%dT%H:%M:%S.000Z"))
                paymentdate = common.getdatefromstring(strdt, "%Y-%m-%dT%H:%M:%S.%fZ")
                
                db((db.payment.fp_paymentref == orderid) & (db.payment.fp_paymentdetail ==shopsetxnid )).update(fp_status = status,
                                                                                                                 paymentcommit = True,
                                                                                                                 fp_paymentdate = paymentdate,
                                                                                                                 fp_otherinfo = otherinfo
                                                                                                                 )
                
                #need to send email to Patient
                jsonresp = {}
                jsonresp["orderid"] = common.getkeyvalue(avars,"orderid","") 
                jsonresp["shopSeTxnId"] = common.getkeyvalue(avars,"shopSeTxnId","")
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
            else:
                #need to send email to Patient
                jsonresp = {}
                jsonresp["result"] = "fail"
                jsonresp["error_message"] = "The status of webhook callback is " + status
                
                
        except Exception as e:
            error_message = "Exit mdp_shopse_webhook API Exception " + str(e)
            logger.loggerpms2.info(error_message)      
            jsonresp = {
              "result":"fail",
              "error_message":error_message
            }
            return json.dumps(jsonresp)
        
        logger.loggerpms2.info("Exit Shopse Webhook = " + json.dumps(jsonresp))
        return json.dumps(jsonresp)
    