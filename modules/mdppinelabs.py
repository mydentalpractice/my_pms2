from gluon import current
import json
import datetime
from datetime import timedelta
import hmac
import requests
import urllib
import base64
import hashlib
import binascii
import os;
import uuid
from uuid import uuid4


from applications.my_pms2.modules import common
from applications.my_pms2.modules import account
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import account
from applications.my_pms2.modules import mdppayment
from applications.my_pms2.modules import mdpbenefits
from applications.my_pms2.modules import mdputils
from applications.my_pms2.modules import mdprules

from applications.my_pms2.modules import datasecurity

from applications.my_pms2.modules import logger

class PineLabs:

    def __init__(self,db):
        self.db = db
        
        r = db(db.pinelab_properties.id>0).select()
    
        self.pl_url = r[0].pl_url
        self.pl_prod = r[0].pl_prod
        self.pl_uat = r[0].pl_uat
        self.pl_mid = r[0].pl_mid
        self.pl_ac = r[0].pl_ac
        self.pl_key = r[0].pl_key
        self.pl_callback = r[0].pl_callback
        self.pl_card = r[0].pl_card
        self.pl_name = r[0].pl_name        
        self.pl_expiry = r[0].pl_expiry
        self.pl_cvv = r[0].pl_cvv        
        


    def pinelabs_encrypt(self, avars):

        logger.loggerpms2.info("Enter Pinelabs Encrypt " + json.dumps(avars)) 
        rspobj = {}

        try:

            key = self.pl_key
            message = common.getkeyvalue(avars,"payment_request","")
            
            #base64 encoding
            message = message.encode()
            message = base64.encodestring(message)
            message = message.decode()            

            byte_key = binascii.unhexlify(key)
            message = message.encode()
            encryptmessage = hmac.new(byte_key, message, hashlib.sha256).hexdigest().upper()        

            rspobj["encrypt"] = encryptmessage
            rspobj["encoded_message"] = message
            rspobj["result"] = "success"
            rspobj["error_code"] = ""
            rspobj["error_message"] = ""

        except Exception as e:
            mssg = "Pine Labs Encryption Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)     

        logger.loggerpms2.info("Exit Pine Labs Encryption " + json.dumps(rspobj))      

        return(json.dumps(rspobj))
    
  
    
    
    def pinelabs_payment(self,avars):
        logger.loggerpms2.info("Enter Pine Labs Payment API == >" + json.dumps(avars))
        db = self.db
   
        try:
            paymentid = int(common.getkeyvalue(avars,"paymentid",0))
           
            
            #create URL
            pl_url = self.pl_url

            plObj = {
                
                "customer_data": {
                    "first_name":common.getkeyvalue(avars,"firstname",""),
                    "last_name":common.getkeyvalue(avars,"lastname",""),
                    "mobile_no":common.getkeyvalue(avars,"cell",""),
                    "email_id":common.getkeyvalue(avars,"email",""),
                    "customer_id":common.getkeyvalue(avars,"memberid","")
                    },

                
                "merchant_data": {
                    "merchant_access_code": self.pl_ac,
                    "merchant_id": self.pl_mid,
                    "merchant_return_url": self.pl_callback,
                    "unique_merchant_txn_id": common.getkeyvalue(avars,"treatment","") + "_" + str(paymentid),   #<treatment>_<paymentid> e.g. TRTMUM001XXXX_1234
                    },
                
                "payment_data": {
                    "amount_in_paisa": 100 * long(common.getkeyvalue(avars,"amount","0"))   # amount to be send to Pine Labs is in paise
                    },
                
                "txn_data": {
                    "navigation_mode": "2",
                    "payment_mode": "1,3,4,7,10,11",
                    "transaction_type": "1",
                },                
              
               
                "udf_data": {
                    "udf_field_1": int(common.getkeyvalue(avars,"memberid",0)),
                    "udf_field_2": int(common.getkeyvalue(avars,"providerid",0)),
                    "udf_field_3": int(common.getkeyvalue(avars,"treatmentid",0)),
                    "udf_field_4": paymentid
                    
                },
                
                "product_details": [
            
                    {
            
                        "schemes": [
                            ],
            
                        "product_code": common.getkeyvalue(avars,"treatment",""),
                        "product_amount": 100 * long(common.getkeyvalue(avars,"amount","0"))
                    }
            
                    ],                

            } 
            
           
            payment_request = json.dumps(plObj)
            
            logger.loggerpms2.info("Pine Labs Raw Data==>" + payment_request)
            
            obj={"payment_request":payment_request}
            rspobj = json.loads(self.pinelabs_encrypt(obj))
            
            #x-verify header
            x_verify = ""
            encoded_message = ""
            
            if (rspobj["result"]=="success"):
                x_verify = rspobj["encrypt"]  
                encoded_message = rspobj["encoded_message"]
                
            body ={
                "request": encoded_message 
            }
            headers = {'content-type': 'application/json', 'X-VERIFY': x_verify}
            
            logger.loggerpms2.info("PineLabs " +  pl_url + " " +  json.dumps(headers) + " " + json.dumps(body))
            
            
            #call API
            resp = requests.post(pl_url, json = body, headers = headers)
                
            jsonresp = {}
            if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
                respstr =   resp.text
                jsonresp = json.loads(respstr)
                if(jsonresp["response_code"] == 1):
                    jsonresp["result"] = "success"
                    jsonresp["error_message"] = ""
                else:
                    jsonresp["result"] = "fail"
                    jsonresp["error_message"] = "PineLabs Payment API Error :\n" + "(" + jsonresp["response_message"] + ")" 
                
                #update payment table 
                db(db.payment.id == paymentid).update(
            
                    fp_paymentref = plObj["merchant_data"]["unique_merchant_txn_id"],
                    fp_invoice = common.getkeyvalue(avars,"treatment",""),
                    fp_merchantid = plObj["merchant_data"]["merchant_id"],
                    fp_paymenttype = "Pine Labs",
                    fp_paymentdetail = plObj["merchant_data"]["unique_merchant_txn_id"],
                    fp_merchantdisplay=plObj["merchant_data"]["merchant_id"],
                    precommitamount = long(plObj["payment_data"]["amount_in_paisa"]) / 100,        #temporary storing the amount  to commit on callback 
                    paymentcommit = False,
                    paymentmode = "Online",
                    fp_status = 'S' if (jsonresp["response_code"] == 1) else 'F'
                )                

          
            else:
                jsonresp={
                    "result" : "fail",
                    "error_message":"PineLabs Payment API Error Response:\n" + "(" + str(resp.status_code) + ")" + " " + resp._content
                    
                } 
                dmp = json.dumps(jsonresp)
                logger.loggerpms2.info(json.dumps(dmp))
                return json.dumps(dmp)
                
        except Exception as e:
            error_message = "PineLabs Payment API Exception " + str(e)
            logger.loggerpms2.info(error_message)      
            jsonresp = {
              "result":"fail",
              "error_message":error_message
            }
            return json.dumps(jsonresp)
        
        logger.loggerpms2.info("PineLabs Payment Exit createTransaction API \n" + json.dumps(jsonresp)) 
        return json.dumps(jsonresp)
    
    def pinelabs_payment_prem(self,avars):
        logger.loggerpms2.info("Enter Pine Labs Payment API == >" + json.dumps(avars))
        db = self.db
   
        try:
            dttodaydate = common.getISTCurrentLocatTime()
            
            paymentid = db.payment.insert(paymentdate=dttodaydate,paymentmode="OnLinr",patientmember=0,treatmentplan=0,\
                                          provider=0,is_active=True,chequeno="0000",bankname="XXXX",accountname="XXXX",accountno="0000",policy="")

            #create URL
            pl_url = self.pl_url

            plObj = {
                
                "customer_data": {
                    "first_name":common.getkeyvalue(avars,"firstname",""),
                    "last_name":common.getkeyvalue(avars,"lastname",""),
                    "mobile_no":common.getkeyvalue(avars,"cell",""),
                    "email_id":common.getkeyvalue(avars,"email",""),
                    "customer_id":common.getkeyvalue(avars,"memberid","")
                    },

                
                "merchant_data": {
                    "merchant_access_code": self.pl_ac,
                    "merchant_id": self.pl_mid,
                    "merchant_return_url": common.getkeyvalue(avars,"callback",""),
                    "unique_merchant_txn_id": common.getstringfromtime(dttodaydate,"%d%m%Y%H%M") + "_" + str(paymentid),   
                    
                    },
                
                "payment_data": {
                    "amount_in_paisa": 100 * long(common.getkeyvalue(avars,"amount","0"))   # amount to be send to Pine Labs is in paise
                    },
                
                "txn_data": {
                    "navigation_mode": "2",
                    "payment_mode": "1,3,4,7,10,11",
                    "transaction_type": "1",
                },                
              
               
                "udf_data": {
                    "udf_field_1": common.getkeyvalue(avars,"firstname",""),
                    "udf_field_2": common.getkeyvalue(avars,"lastname",""),
                    "udf_field_3": common.getkeyvalue(avars,"cell",""),
                    "udf_field_4": common.getkeyvalue(avars,"email","")
                    
                },
                
                "product_details": [
            
                    {
            
                        "schemes": [
                            ],
            
                        "product_code": common.getkeyvalue(avars,"treatment",""),
                        "product_amount": 100 * long(common.getkeyvalue(avars,"amount","0"))
                    }
            
                    ],                

            } 
            
           
            payment_request = json.dumps(plObj)
            
            logger.loggerpms2.info("Pine Labs Raw Data==>" + payment_request)
            
            obj={"payment_request":payment_request}
            rspobj = json.loads(self.pinelabs_encrypt(obj))
            
            #x-verify header
            x_verify = ""
            encoded_message = ""
            
            if (rspobj["result"]=="success"):
                x_verify = rspobj["encrypt"]  
                encoded_message = rspobj["encoded_message"]
                
            body ={
                "request": encoded_message 
            }
            headers = {'content-type': 'application/json', 'X-VERIFY': x_verify}
            
            logger.loggerpms2.info("PineLabs " +  pl_url + " " +  json.dumps(headers) + " " + json.dumps(body))
            
            
            #call API
            resp = requests.post(pl_url, json = body, headers = headers)
                
            jsonresp = {}
            if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
                respstr =   resp.text
                jsonresp = json.loads(respstr)
                if(jsonresp["response_code"] == 1):
                    jsonresp["result"] = "success"
                    jsonresp["error_message"] = ""
                else:
                    jsonresp["result"] = "fail"
                    jsonresp["error_message"] = "PineLabs Payment API Error :\n" + "(" + jsonresp["response_message"] + ")" 
                
                #update payment table 
                db(db.payment.id == paymentid).update(
            
                    fp_paymentref = plObj["merchant_data"]["unique_merchant_txn_id"],
                    fp_invoice = common.getkeyvalue(avars,"treatment",""),
                    fp_merchantid = plObj["merchant_data"]["merchant_id"],
                    fp_paymenttype = "Pine Labs",
                    fp_paymentdetail = plObj["merchant_data"]["unique_merchant_txn_id"],
                    fp_merchantdisplay=plObj["merchant_data"]["merchant_id"],
                    precommitamount = long(plObj["payment_data"]["amount_in_paisa"]) / 100,        #temporary storing the amount  to commit on callback 
                    paymentcommit = False,
                    paymentmode = "Online",
                    fp_status = 'S' if (jsonresp["response_code"] == 1) else 'F'
                )                

          
            else:
                jsonresp={
                    "result" : "fail",
                    "error_message":"PineLabs Payment API Error Response:\n" + "(" + str(resp.status_code) + ")" + " " + resp._content
                    
                } 
                dmp = json.dumps(jsonresp)
                logger.loggerpms2.info(json.dumps(dmp))
                return json.dumps(dmp)
                
        except Exception as e:
            error_message = "PineLabs Payment API Exception " + str(e)
            logger.loggerpms2.info(error_message)      
            jsonresp = {
              "result":"fail",
              "error_message":error_message
            }
            return json.dumps(jsonresp)
        
        logger.loggerpms2.info("PineLabs Payment Exit createTransaction API \n" + json.dumps(jsonresp)) 
        return json.dumps(jsonresp)    
 
    def callback_transaction(self,avars):
        
        logger.loggerpms2.info("Enter Pine Labs callback_transaction API == >" + json.dumps(avars))
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
            patientid = memberid
            
            pats = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select()
            companyid = int(common.getid(pats[0].company)) if(len(pats) != 0) else 0
            c = db((db.company.id == companyid) & (db.company.is_active == True)).select()
            company_code = common.getstring(c[0].company) if(len(c) >0 ) else ""
            
            tr = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
            treatmentid = int(tr[0].id) if(len(tr) > 0) else 0
            
            amount = float(common.getvalue(p[0].precommitamount)) if(len(p) != 0) else 0
            
            
            rsp = json.loads(mdputils.getplandetailsformember(db, providerid, memberid, patientid))
            #patobj = mdppatient.Patient(db, providerid)
            #rsp = json.loads(patobj.getMemberPolicy({"providerid":str(providerid),"memberid":str(memberid)}))
            policy = common.getkeyvalue(rsp,"plancode","PREMWALKIN")
            
            logger.loggerpms2.info("Pine Labs Call Back Transaction API==>Amount " + str(amount) + " status " + status + " " + policy + " " + str(paymentid))
            
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
            
                #wallet_success
                #reqobj = {}
                #reqobj = {"paymentid" : paymentid}
                #rspobj = json.loads(vcobj.wallet_success(reqobj))                 
                ##here need to update treatmentplan tables
                #account._updatetreatmentpayment(db, tplanid, paymentid)
                #db.commit()                
                
                
                
                trtmnt = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
                discount_amount = trtmnt[0].companypay if(len(trtmnt) > 0) else 0
            
          

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

                #db(db.treatment.id == treatmentid).update(companypay = 0, walletamount=0,wallet_type = "",
                                                          #discount_amount=0,WPBA_response = "")  
                #db(db.payment.id == paymentid).update(amount=0,fp_invoiceamt=0,fp_amount=0,fp_fee=0,walletamount=0,discount_amount=0)
                
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
    
    def callback_transaction_prem(self,avars):
            logger.loggerpms2.info("Enter Pine Labs  callback_transaction_prem API == >" + json.dumps(avars))
            db = self.db
           
            try:
                
                
                status = common.getkeyvalue(avars,"txn_response_msg","FAILURE")
                status_code =  common.getkeyvalue(avars,"txn_response_code","-1")
                
                #get unique merchant txn id <datetime>_paymentid
                unique_merchant_txn_id = common.getkeyvalue(avars,"unique_merchant_txn_id","") 
                strarr = unique_merchant_txn_id.split('_')
                paymentid = 0 if(len(strarr)<=1) else int(common.getid(strarr[1]))
                
                merchant_id = common.getkeyvalue(avars,"merchant_id","") 
                
                amount = float(common.getvalue(common.getkeyvalue(avars,"amount_in_paisa",0)))/100
                
                txn_completion_date_time = common.getkeyvalue(avars,"txn_completion_date_time",common.getISTFormatCurrentLocatTime())
                
                paymentdate = common.getISTFormatCurrentLocatTime()
                
                #first,last,cell,email
                firstname = common.getkeyvalue(avars,"firstname","") 
                lastname = common.getkeyvalue(avars,"lastname","") 
                cell = common.getkeyvalue(avars,"cell","") 
                email = common.getkeyvalue(avars,"email","") 
                
                if((status.lower() == "success")|(status.lower() == "s")):
                    xsts = 'S'
                    db((db.payment.id == paymentid)).update(fp_status = xsts,
                                                            paymentcommit = True,
                                                            
                                                            paymentdate = paymentdate,
                                                            fp_paymentdate =paymentdate ,
                                                            
                                                            amount = amount,
                                                            fp_invoiceamt = amount,
                                                            fp_amount = amount, 
                                                            fp_invoice = common.getkeyvalue(avars,"rrn",""),
                                                            paymenttype = "Premium",
                                                            paymentmode = "PineLabs",

                                                            fp_paymentref = unique_merchant_txn_id,
                                                            fp_paymenttype = "Premium",
                                                            fp_paymentdetail = "Pine Labs Payment",
                                                            fp_cardtype = common.getkeyvalue(avars,"acquirer_name",""),
                                                            fp_merchantid =  merchant_id,
                                                            fp_otherinfo =common.getkeyvalue(avars,"udf_field_1","") + " " + common.getkeyvalue(avars,"udf_field_2",""),
                                                            precommitamount = 0
                                                            )
                    
                    
                   
                    
                    
                    
       
                    jsonresp = {}
                    jsonresp["result"] = "success"
                    jsonresp["error_message"] = ""
                    
                    jsonresp["payment_ref"] = unique_merchant_txn_id
                    jsonresp["payment_date"] = common.getstringfromtime(paymentdate,"%d/%m/%Y %H:%M:%S")
                    jsonresp["payment_amount"] = str(amount)
                    jsonresp["payment_status"] = status
                    jsonresp["payment_status_code"] = status_code
                    jsonresp["payment_type"] = "Premium"
                    jsonresp["payment_details"] = "Pine Labs"
                    jsonresp["payment_merchant_id"] = merchant_id
                    jsonresp["payment_card"] = common.getkeyvalue(avars,"acquirer_name","")
                    jsonresp["payment_firstname"] = common.getkeyvalue(avars,"udf_field_1","")
                    jsonresp["payment_lastname"] = common.getkeyvalue(avars,"udf_field_2","")
                    jsonresp["payment_mobile"] = common.getkeyvalue(avars,"mobile_no","")
                    jsonresp["payment_email"] = common.getkeyvalue(avars,"email","")
                else:
                    db((db.payment.id == paymentid)).update(fp_status = status,
                                                                    paymentcommit = False,
                                                                    fp_paymentdate =paymentdate,
                                                                    amount = 0,
                                                                    
                                                                    fp_amount = 0,  
                                                                    precommitamount = 0
                                                                    
                                                                    )
    
                    jsonresp = avars
                    jsonresp["result"] = "fail"
                    jsonresp["error_message"] = common.getkeyvalue(avars,"txn_response_msg","Error in PineLabs Payment")
                    jsonresp["payment_status"] = status
                    jsonresp["payment_status_code"] = status_code
                    jsonresp["payment_ref"] = unique_merchant_txn_id
                    jsonresp["payment_date"] = common.getstringfromtime(paymentdate,"%d/%m/%Y %H:%M:%S")
                    
                    
            except Exception as e:
                error_message = "Exit PineLabs callback_transaction_prem API Exception " + str(e)
                logger.loggerpms2.info(error_message)      
                jsonresp = {
                  "result":"fail",
                  "error_message":error_message
                }
                return json.dumps(jsonresp)
            
            dmp = json.dumps(jsonresp)
            logger.loggerpms2.info("Exit Callback Transaction Prem ==>>" + dmp)
            return dmp
    
    
    
    
    