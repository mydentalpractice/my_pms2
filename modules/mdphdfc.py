from gluon import current
import json
import datetime
from datetime import timedelta

import requests
import urllib
import base64
import hashlib
#


from applications.my_pms2.modules import common
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import account

from applications.my_pms2.modules import logger

class HDFC:
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    
    props = db(db.urlproperties.id > 0).select(\
      db.urlproperties.hdfc_merchantid,
      db.urlproperties.hdfc_account_name,
      db.urlproperties.hdfc_test_domain,
      db.urlproperties.hdfc_prod_domain,
      db.urlproperties.hdfc_access_code,
      db.urlproperties.hdfc_working_key,
      db.urlproperties.hdfc_return_url,
      db.urlproperties.hdfc_cancel_url,
      db.urlproperties.hdfc_getrsa_url,
      db.urlproperties.hdfc_transaction_url,
      db.urlproperties.hdfc_json_url,
      db.urlproperties.mydp_getrsa_url
                                               
      )
    
    
    self.hdfc_merchantid=""
    self.hdfc_account_name=""
    self.hdfc_test_domain=""
    self.hdfc_prod_domain=""
    self.hdfc_access_code=""
    self.hdfc_working_key=""
    self.hdfc_return_url=""
    self.hdfc_cancel_url=""
    self.hdfc_getrsa_url=""
    self.hdfc_transaction_url=""
    self.hdfc_json_url=""
    self.mydp_getrsa_url=""
    
    if(len(props)==0):
      self.hdfc_merchantid=props[0].hdfc_merchantid 
      self.hdfc_account_name=props[0].hdfc_account_name
      self.hdfc_test_domain=props[0].hdfc_test_domain
      self.hdfc_prod_domain=props[0].hdfc_prod_domain
      self.hdfc_access_code=props[0].hdfc_access_code
      self.hdfc_working_key=props[0].hdfc_working_key
      self.hdfc_return_url=props[0].hdfc_return_url
      self.hdfc_cancel_url=props[0].hdfc_cancel_url
      self.hdfc_getrsa_url=props[0].hdfc_getrsa_url
      self.hdfc_transaction_url=props[0].hdfc_transaction_url
      self.hdfc_json_url=props[0].hdfc_json_url
      self.mydp_getrsa_url=props[0].mydp_getrsa_url
    
      
    return
  
  def gethdfc_constants(self):
    
    propobj = {}
    
    propobj["hdfc_merchantid"]=self.hdfc_merchantid
    propobj["hdfc_account_name"]=self.hdfc_account_name
    propobj["hdfc_test_domain"]=self.hdfc_test_domain
    propobj["hdfc_prod_domain"]=self.hdfc_prod_domain
    propobj["hdfc_access_code"]=self.hdfc_access_code
    propobj["hdfc_working_key"]=self.hdfc_working_key
    propobj["hdfc_return_url"]=self.hdfc_return_url
    propobj["hdfc_cancel_url"]=self.hdfc_cancel_url
    propobj["hdfc_getrsa_url"]=self.hdfc_getrsa_url
    propobj["hdfc_transaction_url"]=self.hdfc_transaction_url
    propobj["hdfc_json_url"]=self.hdfc_json_url
    propobj["mydp_getrsa_url"]=self.mydp_getrsa_url
    
    return json.dumps(propobj)
  
  def gethdfc_rsakey(self,paymentid):
    
    logger.loggerpms2.info("Enter GET_HDFC_RSAKEY = " + " " + self.hdfc_access_code + " " + str(paymentid))
    
    getrsaobj = {"access_code":self.hdfc_access_code,
                 "order_id":paymentid
                 }
    
    jsonresp = {}
    try:
      logger.loggerpms2.info("POST Request==>\n")
      logger.loggerpms2.info(self.hdfc_getrsa_url + " " + json.dumps(getrsaobj))
      
      resp = requests.post(self.hdfc_getrsa_url,json=getrsaobj)
      
      
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):

        respstr =   resp.text
        
        logger.loggerpms2.info("Response success: " + repstr)
        
        jsonresp = {
          "rsa_key": respstr,
          "result":"sucess",
          "error_message":""
        }
      else:
        logger.loggerpms2.info("Response error: " + str(resp.status_code))
        jsonresp = {"result":"fail", "error_message":"Request Error - " + str(resp.status_code)}
        
    except Exception as e:
      logger.loggerpms2.info("Response Exception: " + str(e))
      
      jsonresp = {
        "result":"fail",
        "error_message":"Get_HDFC_RSAKY:\n" + str(e)
      }
    
      
    return json.dumps(jsonresp)    
    
    