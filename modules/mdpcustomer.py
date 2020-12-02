from gluon import current

import os;


import json
import datetime
import time
from datetime import timedelta

import requests
import urllib
import base64
import hashlib

import random

from string import Template


from applications.my_pms2.modules import common
from applications.my_pms2.modules import mail
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import mdpappointment
from applications.my_pms2.modules import account
from applications.my_pms2.modules import mdpreligare
from applications.my_pms2.modules import mdpprocedure

from mdpreligare import Religare


from applications.my_pms2.modules import logger

def getvalue(jobj, key1, defval):

    keys = jobj.keys()

    for key in keys:
        if(key.lower() == key1.lower()):
            return jobj.get(key,"defval")


    return defval


def errormessage(db,errorcode,response_message=""):


    errormssgs = db((db.rlgerrormessage.code == errorcode) & (db.rlgerrormessage.is_active == True)).select()

    #if error_code not in the Error table, then add it, commit, and reload
    if(len(errormssgs)==0):
        db.rlgerrormessage.insert(code=errorcode,internalmessage=response_message,externalmessage=response_message + " Please contact MDP Customer Support")
        db.commit()
        errormssgs = db((db.rlgerrormessage.code == errorcode) & (db.rlgerrormessage.is_active == True)).select()

    errormssg = errorcode + ":" + response_message  if(len(errormssgs) == 0) else errorcode + ":\n" + response_message + "\n" + common.getstring(errormssgs[0].externalmessage)

    return errormssg


class Customer:
    def __init__(self,db,providerid=0):
        self.db = db
        self.providerid = providerid
    
    def enroll_customer(self,avars):
        db = self.db
        customerid = getvalue(avars,"customerid",0)
        customer_ref = getvalue(avars,"customer_ref","")
        
        jsonresp = {}

        
        logger.loggerpms2.info("Enter enroll_customer " + str(customerid) )    
        
        try:
            
            #determine if customer is already enrolled in MDP
            
            if((customer_ref != "") & (customer_ref != None)):
                count = db( (db.patientmember.groupref == customer_ref) & 
                            (db.patientmember.is_active == True)).count()
            else:
                count = 0
                
            if(count == 0):
                #new enrollment
                            
                c = db(db.customer.id == customerid).select()
                cobj = {}
                cobj["customerid"] = customerid
                cobj["customer_ref"] = customer_ref
                cobj["fname"] = c[0].fname
                cobj["mname"] = c[0].mname
                cobj["lname"] = c[0].lname
                cobj["address1"] = c[0].address1
                cobj["address2"] = c[0].address2
                cobj["address3"] = c[0].address3
                cobj["city"] = c[0].city
                cobj["st"] = c[0].st
                cobj["pin"] = c[0].pin
                
                cobj["gender"] = c[0].gender
                cobj["telephone"] = c[0].telephone
                cobj["cell"] = c[0].cell
                cobj["email"] = c[0].email
                
                cobj["dob"] = c[0].dob.strftime("%d/%m/%Y")
                cobj["status"] = c[0].status
                cobj["pin1"] = c[0].pin1
                cobj["pin2"] = c[0].pin2
                cobj["pin3"] = c[0].pin3
                
                cobj["providerid"] = c[0].providerid
                cobj["companyid"] = c[0].companyid
                cobj["regionid"] = c[0].regionid
                cobj["planid"] = c[0].planid
                
                cobj["appointment_id"] = c[0].appointment_id
                cobj["appointment_datetime"] = c[0].appointment_datetime.strftime("%d/%m/%Y %H:%M")
                
                cobj["enrolldate"] = c[0].enrolldate.strftime("%d/%m/%Y")
                
                cobj["notes"] = c[0].notes
                
                pat = mdppatient.Patient(db, c[0].providerid)
                
                jsonresp = json.loads(pat.newpatientfromcustomer(cobj))
                
                pat.addpatientnotes(jsonresp["primarypatientid"], jsonresp["patientid"], c[0].notes)
                
                
            
            elif(count == 1):
                #patient member is already enrolled
                i =0
            else:
                #error
                error_code = "ENROLL_CUST_002"
                mssg = error_code + ":" + "Error Enroll Member"
                logger.loggerpms2.info(mssg)
                jsonresp = {
                    "result":"fail",
                    "error_message":mssg,
                    "error_code":error_code
                }            
                
        except Exception as e:
            error_code = "ENROLL_CUST_001"
            mssg = error_code + ":" + "Exception Enroll Member:\n" + "(" + str(e) + ")"
            logger.loggerpms2.info(mssg)
            jsonresp = {
                "result":"fail",
                "error_message":mssg,
                "error_code":error_code
            }            
    
        return json.dumps(jsonresp)