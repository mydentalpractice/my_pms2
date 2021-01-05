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
        auth = current.auth
    
       
    def customer(self,avars):
        db = self.db
        customer_ref = common.getkeyvalue(avars, "customer_ref", "")
        jsonresp={}
        if(customer_ref != ""):
            c = db((db.customer.customer_ref == customer_ref) & (db.customer.is_active == True)).select(db.customer.id, db.customer.customer_ref)
            if(len(c) == 0):
                #new custoemr
                jsonresp = json.loads(self.new_customer(avars))
            else:
                #update customer
                jsonresp = json.loads(self.update_customer(avars))
            
        else:
            error_code = "CUST_001"
            mssg = error_code + ":" + "Customer not created! No Customer_Ref:\n"
            logger.loggerpms2.info(mssg)
            jsonresp = {
                "result":"fail",
                "error_message":mssg,
                "error_code":error_code
            } 
            
        return json.dumps(jsonresp)
    
    #customer with dependants
    def new_customer(self,avars):
        db = self.db        
        auth = current.auth
        jsonresp = {}
        customer_id = 0
        
        try:
            i=0
            
            customer_ref = common.getkeyvalue(avars, "customer_ref", common.generateackid("VIT",8))
            
            if(customer_ref != "" ):
                customer_id = db.customer.insert(
                    customer_ref = customer_ref,
                    fname = common.getkeyvalue(avars,"fname", customer_ref + "_First"),
                    mname = common.getkeyvalue(avars,"mname", ""),
                    lname = common.getkeyvalue(avars,"lname", customer_ref + "_Last"),

                    address1 = common.getkeyvalue(avars,"address1", "331-332 Ganpati Plaza"),
                    address2 = common.getkeyvalue(avars,"address2", "MI Road"),
                    address3 = common.getkeyvalue(avars,"address3", ""),
                    city = common.getkeyvalue(avars,"city", "Jaipur"),
                    st = common.getkeyvalue(avars,"st", "Rajasthan (RJ)"),
                    pin = common.getkeyvalue(avars,"pin", "302001"),
                    pin1 = common.getkeyvalue(avars,"pin1", "302001"),
                    pin2 = common.getkeyvalue(avars,"pin2", "302001"),
                    pin3 = common.getkeyvalue(avars,"pin3", "302001"),

                    gender = common.getkeyvalue(avars,"gender", "Male"),
                    dob = common.getdatefromstring(common.getkeyvalue(avars,"dob", common.getstringfromdate(datetime.date.today(),"%d/%m/%Y")),"%d/%m/%Y"),
                    
                    telephone = common.getkeyvalue(avars,"telephone", ""),
                    cell = common.getkeyvalue(avars,"cell", "8001027526 "),
                    email = common.getkeyvalue(avars,"email", "info@mydentalplan.in"),
                    
                    status = common.getkeyvalue(avars,"status", "No_Attempt"),
                    
                    providerid = int(common.getkeyvalue(avars,"providerid", "1")),
                    companyid = int(common.getkeyvalue(avars,"companyid", "1")),
                    planid = int(common.getkeyvalue(avars,"planid", "1")),
                    regionid = int(common.getkeyvalue(avars,"regionid", "1")),
                   
                    enrolldate = common.getdatefromstring(
                        common.getkeyvalue(avars, "enrolldate",common.getstringfromdate(common.getISTFormatCurrentLocatTime(),"%d/%m/%Y")),"%d/%m/%Y"),
                    
                    appointment_id = common.getkeyvalue(avars,"appointment_id",common.getstringfromdate(common.getISTFormatCurrentLocatTime(),"%d/%m/%Y %H:%M")),
                    appointment_datetime = common.getdatefromstring(
                        common.getkeyvalue(avars, "appointment_datetime",common.getstringfromdate(common.getISTFormatCurrentLocatTime(),"%d/%m/%Y %H:%M")),"%d/%m/%Y %H:%M"),
                    
                    notes = common.getkeyvalue(avars,"notes",""),
                    
                    is_active = True,
                    
                    created_on = common.getISTFormatCurrentLocatTime(),
                    created_by = 1 if(auth.user == None) else auth.user.id,
                    modified_on = common.getISTFormatCurrentLocatTime(),
                    modified_by =1 if(auth.user == None) else auth.usr.id                
                )
                db(db.customer.id == customer_id).update(customer = customer_id)
                
                
                #register customer dependants
         
                deps = common.getkeyvalue(avars,"dependants",None)
                                
                dependantscount = 0 if deps == None else len(deps)
                
                for dep in deps:
                    
                    depid=db.customerdependants.insert(
                        
                        fname=dep["fname"],
                        mname=dep["mname"] if "mname" in dep else "",
                        lname=dep["lname"],
                        depdob=common.getdatefromstring(dep["depdob"], "%d/%m/%Y"),
                        gender=dep["gender"],
                        relation=dep["relation"],
                        customer_id=customer_id,
                        
                        dependant_ref = customer_ref + "_" + dep["relation"],
                        is_active = True,
                        created_on = common.getISTFormatCurrentLocatTime(),
                        created_by = 1 if(auth.user == None) else auth.user.id,
                        modified_on = common.getISTFormatCurrentLocatTime(),
                        modified_by =1 if(auth.user == None) else auth.usr.id                
                    )
                    
                    db(db.customerdependants.id == depid).update(dependant = str(depid))
                    
                    
                jsonresp = {
                    "result":"success",
                    "error_message":"",
                    "error_code":"",
                    "mdp_customer_id":customer_id,
                    "customer_ref":customer_ref,
                    "dependantscount":str(dependantscount)
                }
            else:
                error_code = "NEW_CUST_002"
                mssg = error_code + ":" + "New Customer not created! No unique Customer_Ref:\n"
                logger.loggerpms2.info(mssg)
                jsonresp = {
                    "result":"fail",
                    "error_message":mssg,
                    "error_code":error_code
                }            
            
        except Exception as e:
            error_code = "NEW_CUST_001"
            mssg = error_code + ":" + "Exception New Customer:\n" + "(" + str(e) + ")"
            logger.loggerpms2.info(mssg)
            jsonresp = {
                "result":"fail",
                "error_message":mssg,
                "error_code":error_code
            }            
      
        return json.dumps(jsonresp)
    
    def update_customer(self,avars):
        db = self.db        
        auth = current.auth        
        jsonresp = {}
        try:
            i=0
            customer_ref = common.getkeyvalue(avars, "customer_ref", "")
            
            if(customer_ref != "" ):
                c = db((db.customer.customer_ref == customer_ref)& (db.customer.is_active == True)).select()
                
                db((db.customer.customer_ref == customer_ref) & (db.customer.is_active == True)).update(
                    customer_ref = common.getkeyvalue(avars,"customer_ref", c[0].customer_ref),
                    fname = common.getkeyvalue(avars,"fname", c[0].fname),
                    mname = common.getkeyvalue(avars,"mname", c[0].mname),
                    lname = common.getkeyvalue(avars,"lname", c[0].lname),

                    address1 = common.getkeyvalue(avars,"address1", c[0].address1),
                    address2 = common.getkeyvalue(avars,"address2", c[0].address2),
                    address3 = common.getkeyvalue(avars,"address3", c[0].address3),
                    city = common.getkeyvalue(avars,"city", c[0].city),
                    st = common.getkeyvalue(avars,"st", c[0].st),
                    pin = common.getkeyvalue(avars,"pin", c[0].pin),
                    pin1 = common.getkeyvalue(avars,"pin1", c[0].pin1),
                    pin2 = common.getkeyvalue(avars,"pin2", c[0].pin2),
                    pin3 = common.getkeyvalue(avars,"pin3", c[0].pin3),

                    gender = common.getkeyvalue(avars,"gender", c[0].gender),
                    dob = common.getkeyvalue(avars,"dob",  c[0].do),
                    
                    telephone = common.getkeyvalue(avars,"telephone",  c[0].telephone),
                    cell = common.getkeyvalue(avars,"cell",  c[0].cell),
                    email = common.getkeyvalue(avars,"email",  c[0].email),
                    
                    status = common.getkeyvalue(avars,"status", "No_Attempt"),
                    
                    providerid = int(common.getkeyvalue(avars,"providerid", c[0].providerid)),
                    companyid = int(common.getkeyvalue(avars,"companyid",  c[0].companyid)),
                    planid = int(common.getkeyvalue(avars,"planid",  c[0].planid)),
                    regionid = int(common.getkeyvalue(avars,"regionid",  c[0].regionid)),

                    enrolldate = common.getdatefromstring(
                        common.getvalue(avars, "enrolldate",common.getstringfromdate(c[0].enrolldate,"%d/%m/%Y")),"%d/%m/%Y"),

                    appointment_datetime = common.getdatefromstring(
                        common.getvalue(avars, "appointment_datetime",common.getstringfromdate(c[0].appointment_datetime,"%d/%m/%Y %H:%M")),"%d/%m/%Y %H:%M"),

                    notes = common.getkeyvalue(avars,"notes",c[0].notes),
                    
                    is_active =  c[0].is_active,
                    
                    modified_on = common.getISTFormatCurrentLocatTime(),
                    modified_by =1 if(auth.user == None) else auth.usr.id                       
                )
                
                         
                deps = common.getkeyvalue(avars,"dependants",None)
                for dep in deps:
                    depid = int(dep["dependant"])
                    db(db.customerdependants.id == depid).update(
                        dependant = dep["dependant"],
                        dependant_ref = dep["dependant_ref"],
                        fname = dep["fname"],
                        mname = dep["mname"],
                        lname = dep["lname"],
                        gender = dep["gender"],
                        relation = dep["relation"],
                        depdob = common.getdatefromstring(dep["depdob"], "%d/%m/%Y"),
                        
                        modified_on = common.getISTFormatCurrentLocatTime(),
                        modified_by =1 if(auth.user == None) else auth.usr.id                            
                        
                    
                    )
                    
                    
               
                
            else:
                error_code = "UPDATE_CUST_002"
                mssg = error_code + ":" + "Update Customer not created! No unique Customer_Ref:\n"
                logger.loggerpms2.info(mssg)
                jsonresp = {
                    "result":"fail",
                    "error_message":mssg,
                    "error_code":error_code
                }            
            
        except Exception as e:
            error_code = "UPDATECUST_001"
            mssg = error_code + ":" + "Exception Updatee Customer:\n" + "(" + str(e) + ")"
            logger.loggerpms2.info(mssg)
            jsonresp = {
                "result":"fail",
                "error_message":mssg,
                "error_code":error_code
            }            
      
        return json.dumps(jsonresp)


   

    def get_customer(self,customerid):
        db = self.db        
        auth = current.auth
        
        deplist = []
        depobj = {}
        depcount = 0
        
        jsonresp = {}
        try:
            
            c = db((db.customer.id == customerid) & (db.customer.is_active == True)).select()
            jsonresp={
                "result":"success",
                "error_message":"",
                "error_code":"",
            
                "customer_id":c[0].id,
              
                "customer":c[0].customer,
                
                "customer_ref":c[0].customer_ref,

                "fname":c[0].fname,                
                "mname":c[0].mname,
                "lname":c[0].lname,
                
                "address1":c[0].address1,
                "address2":c[0].address2,
                "address3":c[0].address3,
                "city":c[0].city,
                "st":c[0].st,
                "pin":c[0].pin,
                "pin1":c[0].pin1,
                "pin2":c[0].pin2,
                "pin3":c[0].pin3,
                
                "gender":c[0].gender,
                "dob":common.getstringfromdate(c[0].dob, "%d/%m/%Y"),
                "status":c[0].status,
                
                "telephone":c[0].telephone,
                "cell":c[0].cell,
                "email":c[0].email,
                
                "providerid":self.providerid,
                "companyid":c[0].companyid,
                "planid":c[0].planid,
                "regionid":c[0].regionid,
                
                "enrolldate":common.getstringfromdate(c[0].enrolldate,"%d/%m/%Y"),
                
                "appointment_id":c[0].appointment_id,
                "appointment_datetime":common.getstringfromdate(c[0].appointment_datetime,"%d/%m/%Y %H:%M"),
                
                "notes":c[0].notes,
                
                "is_active":str(c[0].is_active),
                
                "created_on":c[0].common.getstringfromdate(c[0].created_on,"%d/%m/%Y %H:%M"),
                "created_by":c[0].created_by,
                "modified_on":c[0].common.getstringfromdate(c[0].modified_on,"%d/%m/%Y %H:%M"),
                "modified_by":c[0].modified_by,
            
            }
            
            #get customers
            deps = db((db.customerdependants.customer_id == customerid) & (db.customerdependants.is_active == True)).select()
            depcount = 0 if deps == None else len(deps)
            
            for dep in deps:
                depobj= {
                    
                    "dependant_id" : dep["id"],
                    "dependant":dep["dependant"],
                    "dependant_ref" :dep["dependant_ref"],
                    "fname":dep["fname"],
                    "mname":dep["mname"] if "mname" in dep else "",
                    "lname":dep["lname"],
                    "gender":dep["gender"],
                    "relation":dep["relation"],
                    "depdob":common.getstringfromdate(dep["depdob"],"%d/%m/%Y"),
                
                
                }
                deplist.append(depobj)
            
            jsonresp["dependants"] = deplist
            jsonresp["dependantscount"] = depcount
                
        except Exception as e:
            error_code = "GET_CUST_001"
            mssg = error_code + ":" + "Exception GET Customer:\n" + "(" + str(e) + ")"
            logger.loggerpms2.info(mssg)
            jsonresp = {
                "result":"fail",
                "error_message":mssg,
                "error_code":error_code
            }            
      
        return json.dumps(jsonresp)
    
    def delete_customer(self,avars):
        
        db = self.db        
        auth = current.auth
        jsonresp = {}        
        
        customer_ref = common.getkeyvalue(avars,"customer_ref","")
        customer_id = common.getkeyvalue(avars,"customer_id",0)
        
        try:
            c = db((db.customer.customer_ref == customer_ref) & (db.customer.is_active == True)).select(db.customer.id)
            customer_id = c[0].id if(len(c) == 1) else customer_id 
            
            if(customer_id == 0):
                jsonresp = {
                    "result":"fail",
                    "error_message":"No Customer to Cancel",
                    "error_code":"",
                    
                    "customer_id":customer_id,
                    "customer_ref":customer_ref
                    
                }                     
                
                return jason.dumps(jsonresp)
            
            
            db(db.customer.id == customer_id).update(
                is_active = False,
                modified_on = common.getISTFormatCurrentLocatTime(),
                modified_by =1 if(auth.user == None) else auth.usr.id                               
            )
            
            d = db(db.customerdependants.customer_id == customer_id).update(
                is_active = False,
                modified_on = common.getISTFormatCurrentLocatTime(),
                modified_by =1 if(auth.user == None) else auth.usr.id                               
            )
            
            c = db(db.customer.id == customer_id).select(db.customer.customer_ref)
            patid = 0
            if(len(c)==1):
                db((db.patientmember.groupref == c[0].customer_ref) & (db.patientmember.is_active == True)).update(
                    is_active = False,
                    modified_on = common.getISTFormatCurrentLocatTime(),
                    modified_by =1 if(auth.user == None) else auth.usr.id                               
                )
            p = db((db.patientmember.groupref == customer_ref)).select(db.patientmember.id)
            patid = p[0].id if len(p) == 1 else 0
            
           
            d = db((db.patientmemberdependants.patientmember == patid) & (db.patientmemberdependants.is_active == True)).update(
                is_active = False,
                modified_on = common.getISTFormatCurrentLocatTime(),
                modified_by =1 if(auth.user == None) else auth.usr.id              
            )

            
            jsonresp = {
                            "result":"success",
                            "error_message":"",
                            "error_code":"",
                            
                            "customer_id":customer_id,
                            "customer_ref":customer_ref
                            
                        }                            

        except Exception as e:
            error_code = "DELETE_CUST_001"
            mssg = error_code + ":" + "Exception DELETE Customer:\n" + "(" + str(e) + ")"
            logger.loggerpms2.info(mssg)
            jsonresp = {
                "result":"fail",
                "error_message":mssg,
                "error_code":error_code
            }            
        
        return json.dumps(jsonresp)
    
    def set_appointment(self,avars):
        db = self.db        
        auth = current.auth
        jsonresp = {}        
        providerid = self.providerid
        
        customer_ref = common.getkeyvalue(avars,"customer_ref","")
        customer_id = common.getkeyvalue(avars,"customer_id",0)
        
        mdappt = None
        apptobj = {}

                
        logger.loggerpms2.info("Enter set_appointment " + str(customer_id))    
         
        try:
            
            c = db((db.customer.customer_ref == customer_ref) & (db.customer.is_active == True)).select()
            customer_id = c[0].id if(len(c)==1) else customer_id
         
                
            todaystr = common.getstringfromdate(datetime.date.today(),"%d/%m/%Y")
           
            appointment_id  = common.getkeyvalue(avars,"appointment_id",c[0].appointment_id)
            appointment_datetime = common.getdatefromstring(common.getkeyvalue(avars,"appointment_datetime",todaystr + " 09:00"),"%d/%m/%Y %H:%M")
            
            p = db((db.vw_memberpatientlist.groupref == customer_ref) & (db.vw_memberpatientlist.patienttype == 'P') & (db.vw_memberpatientlist.is_active == True)).select()
            patientid = p[0].patientid if(len(p)==1) else 0
            memberid = p[0].primarypatientid if(len(p)==1) else 0
            member = p[0].fullname if(len(p)==1) else ""
            
            appPath = current.globalenv["request"].folder
           
            docs = db((db.doctor.providerid == providerid) & 
                      (db.doctor.practice_owner == True) & 
                      (db.doctor.is_active == True)).select()
    
            if(len(docs)>0):
                doctorid = docs[0].id
    
            else:  
                doctorid = 0
            
            mdpappt = mdpappointment.Appointment(db, providerid)
            apptobj = json.loads(mdpappt.newappointment(memberid, patientid, doctorid, 
                                                        "", 
                                                        appointment_datetime.strftime("%d/%m/%Y %H:%M"),
                                                        30, 
                                                        "Auto-Appointment created\nAppointment_ID: " + appointment_id + "\n" + c[0].notes, 
                                                        c[0].cell, 
                                                        appPath,
                                                        appointment_id
                                                        )
                                     )   
            
            #update appointment unique id with customer appointment id
            db(db.t_appointment.id == int(apptobj["appointmentid"])).update(f_uniqueid == appointment_id)
            
            
            #email Welcome Kit
            ret = mail.emailWelcomeKit(db,current.globalenv["request"],memberid,providerid)
            message = "Customer " + member + " has been successfully enrolled in MDP\n Welcome Kit has been sent to the registered email address"            

            jsonresp = {
                            "result":"success",
                            "error_message":"",
                            "error_code":"",
                            "message":message,
                            "appointment_id":appointment_id,
                            "customer_id":customer_id,
                            "customer_ref":customer_ref
                            
                        }                            
    
        except Exception as e:
            error_code = "DELETE_CUST_001"
            mssg = error_code + ":" + "Exception SET APPOINTMENT :\n" + "(" + str(e) + ")"
            logger.loggerpms2.info(mssg)
            jsonresp = {
                "result":"fail",
                "error_message":mssg,
                "error_code":error_code
            }            
        
        return json.dumps(jsonresp) 
    
    def enroll_customer(self,avars):
        db = self.db
        auth = current.auth
        
        customerid = common.getkeyvalue(avars,"customerid",0)
        customer_ref = common.getkeyvalue(avars,"customer_ref","")
        
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
                c = db((db.customer.customer_ref == customer_ref) & (db.customer.is_active == True)).select()
                customerid = c[0].id if(len(c) == 1) else customerid
                
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
                
                
                deps = db((db.customerdependants.customer_id == customerid) & (db.customerdependants.is_active == True)).select()
                deplist = []
                depobj = {}
                
                
                     

                for dep in deps:
                    depobj = {
                        "dependant":dep["dependant"],
                        "dependant_ref":dep["dependant_ref"],
                        "customer_id":dep["customer_id"],
                        "fname":dep["fname"],
                        "mname":dep["mname"]  if "mname" in dep else "",
                        "lname":dep["lname"],
                        "depdob":common.getstringfromdate(dep["depdob"],"%d/%m/%Y"),
                        "gender":dep["gender"],
                        "relation":dep["relation"],
                    }
                    deplist.append(depobj)
                
                cobj["dependants"] = deplist
                pat = mdppatient.Patient(db, c[0].providerid)
                
                jsonresp = json.loads(pat.newpatientfromcustomer(cobj))
                
                pat.addpatientnotes(jsonresp["primarypatientid"], jsonresp["patientid"], c[0].notes)
                
                db(db.customer.id == customerid).update(
                    
                    status = 'Enrolled',
                    modified_on = common.getISTFormatCurrentLocatTime(),
                    modified_by =1 if(auth.user == None) else auth.user.id                               
                         
                
                )
                
            
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