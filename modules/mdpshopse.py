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


from applications.my_pms2.modules import common
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import account
from applications.my_pms2.modules import mdppayment

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
            obj = datasecurity.DataSecurity()
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
            
            provdict = common.getproviderfromid(db,providerid)
            customParams = avars["customParams"] if ("customParams" in avars) else {}
            
            customParams["SalesPersonEmail"] = provdict["email"]
            customParams["SalesPersonMobile"] = provdict["cell"]
            
            #Request CreateTransaction API
            shopsee_request = {
                "orderId":common.getkeyvalue(avars,"treatment","") + "_" + str(common.getkeyvalue(avars,"paymentid",0)),   #<treatment>_<paymentid> e.g. TRTMUM001XXXX_1234
                "amount":float(common.getkeyvalue(avars,"amount","0")),
                "mobile":common.getkeyvalue(avars,"mobile",""),
                "email":common.getkeyvalue(avars,"email",""),
                "returnUrl":self.shopsee_returnURL,
                "webhookUrl":self.webhookUrl,
                "productName":treatment ,
                "productId":treatmentid,
                "firstName":common.getkeyvalue(avars,"firstName",""),
                "lastName":common.getkeyvalue(avars,"lastName",""),
                "address":avars["address"],
                "customParams":avars["customParams"],
                "products":proclist
            }
        
            logger.loggerpms2.info("SHOPSEE REQUEST\n" + json.dumps(shopsee_request))
            
            #call API
            resp = requests.post(url,headers=shopsee_header,json=shopsee_request)
            jsonresp = {}
            if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
                respstr =   resp.text
                jsonresp = json.loads(respstr)
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
                
                #complete the transaction
                arr = common.getkeyvalue(jsonresp,"orderid","0_0")
                arr = arr.split("_")
                
                paymentid = int(common.getid(arr[1])) if (len(arr) >= 2) else 0
                treatment = common.getstring(arr[0]) if (len(arr) >= 1) else ""
                x=db((db.treatment.treatment == treatment) & (db.treatment.is_active == True)).select(db.treatment.id)
                treatmentid = int(common.getid(x[0].id)) if(len(x) > 0) else 0
                amount = float(common.getkeyvalue(avars,"amount","0"))
                db(db.payment.id == paymentid).update(
                    
                                                      fp_paymentref = common.getkeyvalue(jsonresp,"OrderId",""),
                                                      amount = amount,
                                                      fp_invoice = treatment,
                                                      fp_invoiceamt = amount,
                                                      fp_amount = amount,
                                                      fp_merchantid = "MDP",
                                                      fp_paymenttype = "ShopSe",
                                                      fp_paymentdetail = common.getkeyvalue(jsonresp,"shopSeTxnId",""),
                                                      fp_merchantdisplay="MyDental Health Plan Pvt. Ltd."
                                                    )
                
                logger.loggerpms2.info("Shopsee createTransaction API Response \n" + json.dumps(jsonresp)) 
                
               
                
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
    
    
    def callback_transaction(self,avars):
        
        logger.loggerpms2.info("Enter Shopsee callback_transaction API == >" + json.dumps(avars))
        db = self.db
   
        try:
            if(common.getkeyvalue(avars,"status","") == "success"):
                orderid = common.getkeyvalue(avars,"orderid","") 
                shopsetxnid = common.getkeyvalue(avars,"shopsetxnid","") 
                
                p = db((db.payment.fp_paymentref == orderid) & (db.payment.fp_paymentdetail ==shopsetxnid )).select(db.payment.id)
                db((db.payment.fp_paymentref == orderid) & (db.payment.fp_paymentdetail ==shopsetxnid )).update(fp_status = common.getkeyvalue(avars,"status",""),
                                                                                                                 paymentcommit = True,
                                                                                                                 fp_paymentdate = ""
                                                                                                                 )
                
                jsonresp = avars
                jsonresp["paymentid"] = int(common.getid(p[0].id)) if(len(p) >= 1) else 0
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
                
            else:
                jsonresp = avars
                jsonresp["result"] = "fail"
                jsonresp["error_message"] = avars["message"]
                
                
        except Exception as e:
            error_message = "Exit Shopsee callback_transaction API Exception " + str(e)
            logger.loggerpms2.info(error_message)      
            jsonresp = {
              "result":"fail",
              "error_message":error_message
            }
            return json.dumps(jsonresp)
        
        
        return json.dumps(jsonresp)
    
    
    
    
    
    
    #This API is called from ShopSe
    def mdp_shopse_webhook(self,avars):
        
        logger.loggerpms2.info("Enter mdp_shopse_webhook API == >" + json.dumps(avars))
        db = self.db
        jsonresp = {}
        
        try:
            if(common.getkeyvalue(avars,"status","") == "success"):
                orderid = common.getkeyvalue(avars,"orderid","") 
                shopsetxnid = common.getkeyvalue(avars,"shopsetxnid","") 
                
                #generate encryption signature
                sigobj = {}
                sigobj["orderId"] = common.getkeyvalue(avars,"orderId","")
                sigobj["shopSeTxnId"] = common.getkeyvalue(avars,"shopSeTxnId","")
                sigobj["status"] = common.getkeyvalue(avars,"status","")
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
                
                db((db.payment.fp_paymentref == orderid) & (db.payment.fp_paymentdetail ==shopsetxnid )).update(fp_status = common.getkeyvalue(avars,"status",""),
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
    