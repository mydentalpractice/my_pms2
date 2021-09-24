from gluon import current
import json
import datetime
from datetime import timedelta

import requests
import urllib
import base64
import hashlib



from applications.my_pms2.modules import common
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import account
from applications.my_pms2.modules import mdppayment

from applications.my_pms2.modules import logger

class Razorpay:
  
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    
    props = db(db.urlproperties.id > 0).select(\
      db.urlproperties.fp_produrl,
      db.urlproperties.fp_apikey,
      db.urlproperties.fp_privatekey,
      db.urlproperties.fp_merchantid,
      db.urlproperties.fp_merchantdisplay
      )
    
    
    self.fp_produrl=""
    self.fp_apikey=""
    self.fp_privatekey=""
    self.fp_merchantid = ""
    self.fp_merchantdisplay  = ""
    
    
    if(len(props)>0):
      self.fp_produrl=props[0].fp_produrl 
      self.fp_apikey=props[0].fp_apikey
      self.fp_privatekey=props[0].fp_privatekey
      self.fp_merchantid = props[0].fp_merchantid
      self.fp_merchantdisplay = props[0].fp_merchantdisplay
      
    return
  
  def getrazorpay_constants(self):
    
    propobj = {}
    
    propobj["produrl"]=self.fp_produrl
    propobj["apikey"]=self.fp_apikey
    propobj["merchantid"]=self.fp_merchantid
    propobj["merchantdisplay"]=self.merchantdisplay
    
    return json.dumps(propobj)
  
  
  def create_razorpay_order(self,amount,currency,receipt,payment_capture="1"):

    logger.loggerpms2.info("Enter New_razorpay_order")
    

    paiseamount = int(amount * 100)
    orderurl =   self.fp_produrl + "/orders"
    
    getrsaobj = {
      "amount":paiseamount,
      "currency":currency,
      "receipt":receipt,
      "payment_capture":payment_capture
    }
    
    jsonresp = {}
    try:
      logger.loggerpms2.info("POST Request==>\n")
      logger.loggerpms2.info(orderurl + " " + json.dumps(getrsaobj))
      
      resp = requests.post(orderurl,json=getrsaobj)
      
      
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):

        respobj = resp.json() 
	
	logger.loggerpms2.info("new_razorpay_order  Response success: " + json.dumps(respobj))
        
        jsonresp = {
          "order_id": respobj["id"],
          "entity": respobj["entity"],
          "amount": float(respobj["amount"])/100,
          "amount_paid": float(respobj["amount_paid"])/100,
          "amount_due": float(respobj["amount_due"])/100,
          "currency": respobj["currency"],
          "receipt": respobj["receipt"],
          "offer_id": respobj["offer_id"],
          "status": respobj["status"],
          "attempts": respobj["attempts"],
          "notes": respobj["notes"],
          "created_at": respobj["created_at"],

          "result":"sucess",
          "error_message":""
          
        }        

        
      else:
	
	respobj = resp.json() 
	error_message = "Create Razorpay Order Error==>\n" + respobj.get("error","").get("code","") + ":" + respobj.get("error","").get("description","") + "\n" + str(resp.status_code)
	logger.loggerpms2.info(error_message)
	jsonresp = {"result":"fail", "error_message":error_message}
			

        
    except Exception as e:
      error_message = "Create Razorpay Order Exception " + str(e)
      logger.loggerpms2.info(error_message)      

     
      
      jsonresp = {
        "result":"fail",
        "error_message":error_message
      }
    
      
    return json.dumps(jsonresp)    
  
    
  def capture_razorpay_payment(self,amount,razorpay_id,razorpay_order_id,newpayment):
    logger.loggerpms2.info("Enter capture_razorpay_payment " + str(amount) + " " + str(razorpay_id) + " " + str(razorpay_order_id) + " " + json.dumps(newpayment["addln_info"]))
    
    orderurl =   self.fp_produrl + "/payments/" + razorpay_id  +"/capture"
    paiseamount = int(amount * 100)
    getrsaobj = {
      "amount":paiseamount
    }
    
    jsonresp = {}
    resp = {}
    try:
      #logger.loggerpms2.info("POST Request==>\n")
      #logger.loggerpms2.info(orderurl + " " + json.dumps(getrsaobj))
      
      resp = requests.post(orderurl,json=getrsaobj)
      
      
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
  
        respobj = resp.json() 
  
        #logger.loggerpms2.info("capture_razorpay_payment  Response success: " + json.dumps(respobj))
        
        respobj["result"] = "success"
        respobj["error_message"] = ""
        
        
        
        #"action":"paymentcallback",
         #"providerid":108,
          #X"amount": "100.0",        # this value is capture_razor_payment amount
    
          #X"payment_detail": "411111XXXXXX1111",   #
    
          #X"error_msg": null,         #capture Razor Payment error_description
          #X"addln_detail": "{\       #additional info returned by on new Payment API
                 #"paymentid\": \"236\",\      #MDP Payment ID created on new Payment
                 #"paymentdate\": \"11\\/01\\/2019\",   #MDP Payment Date created on new Payment
                 #"invoiceamt\": \"25600\"     
           #}",
          
          #X"sign":   "121b88d4cfbdf2d6aca6d4a6ea2b0855a4cc3083e5474bbe174083ae9280750bcb8bb26a410d6515b45f0ca96d44704bb30b7394b95b53e9a4969d256386f01fbb38f6a68f0a40b6597dc00fbdd275aba6b55875fd75a696d5b321fb1800f00bc5b6a4670cc27eed8bc0bde55f80e5e0669257f4be6fbaecd1637bff5407ab73b5087dd7509d24a9631bb10f492dce3e99c0cc847c225cd67c7a99f807dcd78c1088a732f5e522a6879e1f9228ca8f2f1933b7d27f4aa815270a72c8716e60dac072783d992ece389963133fc79a2a7d63e4c4a88cbb22d9c6dd5b6d7f4a06bc4b5bab5761a77e14df17fb1719ee7507434c2a2dfa7d89a65c96a43bb4639c2c",   #capture razor payment id
    
          #X"merchant_id": "FPTEST",     # New Payment Obj 
      
          #X"payment_reference": "190111171350GPQ",   #capture razor payment id
    
          #X"error": null,   ,         #capture Razor Payment error_code
          #X"payment_type": "Credit Card",
          #X"id": "FPTEST",            
          #X"invoice": "TRRELGR01280127_236",
          #X"merchant_display": "My Dental Plan",   #New Payment obj field
          #X"status": "S",
          #X"chequeno":"0000",   #hard coded
          #X"acctno":"0000",
          #X"acctname":"XXXX",
          #X"bankname":"MDP"
          
          
         
            #"bankname":"MDP"
        
        
        #call payment callback with paymentdata object
        
        strdetailobj = json.dumps(newpayment["addln_info"])
        payobj = {}
        
       
	                                          
        payobj["payment_reference"] = razorpay_id + "_" + razorpay_order_id
        payobj["amount"] = amount
        payobj["addln_detail"] = strdetailobj
        payobj["merchant_id"] = newpayment["merchant_id"]
        payobj["merchant_display"] = newpayment["merchant_display"]
        payobj["invoice"] = newpayment["invoice"]
        payobj["payment_detail"] =  respobj.get("card_id","") 
       
        if(respobj.get("card",None) == None):
          payobj["payment_type"] = "Non Card"
        else:
          payobj["payment_type"] = respobj["card"]["entity"]
        
        payobj["sign"] = ""
        payobj["status"] = "S" if(respobj.get("status","") == 'captured') else 'X'
        
        payobj["error_msg"] = respobj.get("error_description","")
        payobj["error"] = respobj.get("error_code","")
        payobj["id"] = newpayment["id"]
        
        payobj["chequeno"] = "00000"
        payobj["acctno"] = "00000"
        payobj["acctname"] = "XXXX"
        payobj["bankname"] = "XXX"
        payobj["result"]  = "success"
        payobj["error_message"] = ""
        
        obj = mdppayment.Payment(self.db, self.providerid)
        jsondump = obj.paymentcallback(payobj)
        jsonresp = json.loads(jsondump)
      else:
	respobj = resp.json() 
	error_message = "Capture Razorpay  Payment Error==>\n" + respobj.get("error").get("code","") + ":" + respobj.get("error").get("description","") + "\n" + str(resp.status_code)
        logger.loggerpms2.info(error_message)
        
        jsonresp = {"result":"fail", "error_message":error_message}
        
    except Exception as e:
      error_message = "Capture Razorpay Payment Exception " + str(e)
      logger.loggerpms2.info(error_message)      

     
      
      
      jsonresp = {
        "result":"fail",
        "error_message": errstr
      }
    
    dmp = json.dumps(jsonresp)  
    logger.loggerpms2.info("Exit Captur Razorpay Payment " + dmp)
    return dmp

  
  
  

   
 