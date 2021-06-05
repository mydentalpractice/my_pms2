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

from applications.my_pms2.modules import logger

class Shopsee:

    def __init__(self,db):
        self.db = db
     
        
        r = db(db.shopsee_properties.id>0).select()

        self.shopsee_prod_url = r[0].shopsee_prod_url
        self.shopsee_stg_url = r[0].shopsee_stg_url
        self.shopsee_api_token = r[0].shopsee_api_token
        self.shopsee_response_key = r[0].shopsee_response_key

    def create_transaction(self,avars):
        logger.loggerpms2.info("Enter Shopsee CreateTransaction API == >" + json.dumps(avars))
        db = self.db
   
        try:
            
            #create URL
            url = self.shopsee_prod_url + "/merchant/api/v2/transactions" 
            #shopsee_header = {"Content-Type":"application/json"}
            shopsee_header = {"Content-Type":"application/json","Authorization":self.shopsee_api_token}
            
            #Request CreateTransaction API
            shopsee_request = {
                "orderId":common.getkeyvalue(avars,"orderId",""),
                "amount":float(common.getkeyvalue(avars,"amount","0")),
                "mobile":common.getkeyvalue(avars,"mobile",""),
                "email":common.getkeyvalue(avars,"email",""),
                "returnUrl":common.getkeyvalue(avars,"returnUrl",""),
                "productName":common.getkeyvalue(avars,"productName",""),
                
                "productId":common.getkeyvalue(avars,"productId",""),
                "firstName":common.getkeyvalue(avars,"firstName",""),
                "lastName":common.getkeyvalue(avars,"lastName",""),
                "address":avars["address"],
                "customParams":avars["customParams"]
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