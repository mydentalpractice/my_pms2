from gluon import current

import json
import datetime
import time
from datetime import timedelta

import requests
import urllib
import base64
import hashlib

import random



from applications.my_pms2.modules import common
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import mdpappointment
from applications.my_pms2.modules import account
from applications.my_pms2.modules import mdpreligare
from mdpreligare import Religare


from applications.my_pms2.modules import logger


class ABHICL:
  def __init__(self,db,providerid=0):
    self.db = db
    self.providerid = providerid
    self.rlgrobj = Religare(db, providerid)
    
  def startsession(self,avars):
    
    db = self.db
    promocode = avars["promocode"] if "promocode" in avars else ""
    jsonresp = {}
    
    try:

      if(promocode != ""):
        # generate ackid 
        ackid = common.generateackid("AB",10)
        self.ackid = ackid
	
	db.sessionlog.insert(\
	  ackid = ackid,
	  promocode = promocde,
	  created_on = common.getISTFormatCurrentLocatTime(),
	  created_by = 1 ,
	  modified_on = common.getISTFormatCurrentLocatTime(),
	  modified_by = 1     
	)
        jsonresp["result"] = "success"
        jsonresp["error_code"] = ""
        jsonresp["error_message"] = ""
        jsonresp["ackid"] = ackid    
	
        
      else:
        msg = "Start Sessoion API: " + self.rlgrobj.errormessage("ABHICL001")
        logger.loggerpms2.info(msg)
        jsonresp = {
          "result":"fail",
          "error_code":"ABHICL001",
          "error_message": msg
        }        
      
     
    except Exception as e:
      msg = "Start Session API Excption:\n" + self.rlgrobj.errormessage("ERR004")  + "\n(" + str(e) + ")"
      logger.loggerpms2(msg)
      jsonresp["result"] = "fail"
      jsonresp["error_code"] = "ERR004"
      jsonresp["error_message"] = msg
      
    
    
    return json.dumps(jsonresp)
    
  
 def newabhiclpatient(self,avars):
    
    db = self.db
    
    auth = current.auth
    
    jsonresp = {}

    providerid = 0
    providercode = None

    companyid = 0
    companycode = None
    companycity = None
    companyst = None
    companypin = None
    companyaddr1 = None
    companyaddr2 = None
    companyaddr3 = None
    

    regionid = 0
    regioncode = None
    
    planid = 0
    plancode = None
    
    policy = None
    
    patientmember = None
    
    try:
      
      ackid = avars["ackid"] if "ackid" in avars else None
      
      #invalid session as no ackid is specified
      if((ackid == None) | (ackid != "")):
	msg = "New ABHICL Patient API No ACKID: " + self.rlgrobj.errormessage("ERR002")
	logger.loggerpms2.info(msg)
	jsonresp = {
          "result":"fail",
          "error_code":"ERR002",
          "error_message": msg
        }
	return json.dumps(jsonresp)	

      #get company
      r = db(db.sessionlog.ackid == ackid).select(db.company.company,db.company.id,left=[db.company.on(db.company.groupkey == db.sessionlog.promocode)])
      companycode = r[0].company.company if(len(r) == 1) else None
      companycity = r[0].company.city if(len(r) == 1) else ""
      companyst = r[0].company.st if(len(r) == 1) else ""
      companypin = r[0].company.pin if(len(r) == 1) else ""
      
      companyid = int(common.getid(r[0].company.id)) if(len(r) == 1) else 0
      
      if((companycode == "") | (companycode==None) | (companyid == 0)):
	msg = "New ABHICL Patient API : No Promocode: " + self.rlgrobj.errormessage("ERR002")
	logger.loggerpms2.info(msg)
	jsonresp = {
          "result":"fail",
          "error_code":"ERR002",
          "error_message": msg
        }
	return json.dumps(jsonresp)


      #get policy	
      policy = avars["policy"] if "policy" in avars else None
      if((policy == None) | (policy == "")):
	msg = "New ABHICL Patient API: No Policy: " + self.rlgrobj.errormessage("ERR003")
	logger.loggerpms2.info(msg)
	jsonresp = {
          "result":"fail",
          "error_code":"ERR003",
          "error_message": msg
        }        
	return json.dumps(jsonresp)
      
      
      #get selected provider & region
      providercode = common.getstring(avars["providercode"]) if "providercode" in avars else None
      
      if((providercode == None) | (providercode == "")):
	msg = "New ABHICL Patient API: No Provider: " + self.rlgrobj.errormessage("ERR005")
	logger.loggerpms2.info(msg)
	jsonresp = {
          "result":"fail",
          "error_code":"ERR005",
          "error_message": msg
        }        
	return json.dumps(jsonresp)

      provs = db((db.provider.provider == providercode) & (db.provider.is_active == True)).select()
      
      if(len(provs) != 1):
	msg = "New ABHICL Patient API: No Provider: " + self.rlgrobj.errormessage("ERR005")
	logger.loggerpms2.info(msg)
	jsonresp = {
          "result":"fail",
          "error_code":"ERR005",
          "error_message": msg
        }        
	return json.dumps(jsonresp)

      providerid = int(common.getid(provs[0].id))
      regionid = int(common.getid(provs[0].groupregion))
      r = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select()
      regioncode = common.getstring(r[0].groupregion) if(len(r) == 1) else None
	
      
      #get planid for the patient
      x = db(\
             (db.provider_region_plan.providercode == providercode) & (db.provider_region_plan.companycode == companycode) &\
             (db.provider_region_plan.regioncode == regioncode) & (db.provider_region_plan.policy == policy) &\
             (db.provider_region_plan.is_active == True).select()
             )
      plancode = common.getstring(x[0].plancode) if(len(x) == 1) else None
      p = db(db.hmoplan.hmoplancode == plancode).select()
      planid = int(common.getid(p[0].id)) if(len(p) == 1) else 0
      
      if(planid == 0):
	msg = "New ABHICL Patient API: No Plan: " + self.rlgrobj.errormessage("ERR006")
	logger.loggerpms2.info(msg)
	jsonresp = {
          "result":"fail",
          "error_code":"ERR006",
          "error_message": msg
        }        
	return json.dumps(jsonresp)

      #patientmember
      sql = "UPDATE membercount SET membercount = membercount + 1 WHERE company = " + str(companyid) + ";"
      db.executesql(sql)
      db.commit()    
      xrows = db(db.membercount.company == companyid).select()
      membercount = int(common.getid(xrows[0].membercount)) if(len(xrows) == 1) else -1
      if(membercount < 0):
	msg = "New ABHICL Patient API: Patient Member Count: " + self.rlgrobj.errormessage("ERR007")
	logger.loggerpms2.info(msg)
	jsonresp = {
          "result":"fail",
          "error_code":"ERR007",
          "error_message": msg
        }        
	return json.dumps(jsonresp)
      patientmember = plancode + str(membercount)    

      #create or update new patient
      groupref = avars["ABHICLID"] if "ABHICLID" in avars else None
      
      todaydt = common.getISTFormatCurrentLocatTime()
      todaydtnextyear = common.addyears(todaydt,1)      

      patid = db.patientmember.update_or_insert((db.patientmember.groupref==groupref),
                                                patientmember = patientmember,
                                                groupref = groupref,

                                                fname = common.getstring(avars["firstname"]) if "firstname" in avars else groupref + "_FN",
                                                mname = common.getstring(avars["middlename"]) if "middlename" in avars else "",
                                                lname = common.getstring(avars["lastname"]) if "lastname" in avars else groupref + "_LN",
                                                
                                                address1 = common.getstring(avars["address1"]) if "address1" in avars else companyaddr1,
                                                address2 = common.getstring(avars["address2"]) if "address2" in avars else companyaddr2,
                                                address3 = common.getstring(avars["address3"]) if "address3" in avars else companyaddr3,
                                                city = common.getstring(avars["city"]) if "city" in avars else companycity,
                                                st = common.getstring(avars["st"]) if "st" in avars else companyst,
                                                pin = common.getstring(avars["pin"]) if "pin" in avars else companypin,
                                                
                                                
                                                cell = common.getstring(avars["cell"]) if "cell" in avars else "0000000000",
                                                email = common.getstring(avars["email"]) if "email" in avars else "mydentalplan.in@gmail.com",
                                                
                                                dob = datetime.datetime.strptime(common.getstring(avars["dob"]) if "dob" in avars else "01/01/1990", "%d/%m/%YYYY" ),
                                                gender = common.getstring(avars["gender"]) if "gender" in avars else "Male",
                                                status = 'Enrolled',
                                                
                                                groupregion = regionid,
                                                provider = providerid,
                                                company = companyid,
                                                hmoplan = planid,
                                                
                                                enrollmentdate = todaydt,
                                                premstartdt = todaydt,
                                                premenddt = todaydtnextyear,
                                                startdate = todaydt,
                                                hmopatientmember = True,
                                                paid = True,
                                                newmember = False,
                                                freetreatment  = True,
                                                
                                                created_on = common.getISTFormatCurrentLocatTime(),
                                                created_by = 1 if(auth.user == None) else auth.user.id,
                                                modified_on = common.getISTFormatCurrentLocatTime(),
                                                modified_by = 1 if(auth.user == None) else auth.user.id    
                                              
                                              )
      
      db.commit()
      
      #update_or_insert does not return patid, hence we need to retrieve from the new record created
      if(patid == None):
	r = db(db.patientmember.groupref == groupref).select(db.patientmember.id)
	patid = int(common.getid(r[0].id)) if(len(r) == 1) else None
	
	if(patid == None):
	  jsonresp={"result":"fail","error_message":"New ABHICL Patient API:Patient ID None", self.errormessage("ERR007"), "error_code":"ERR007"}
	  return json.dumps(jsonresp)

	opat = mdppatient.Patient(db, providerid)
	patobj = opat.getpatient(patid, patid, "")          
	if(patobj["result"] == "success"):
	  jsonresp = {
	    "result":"success",
	    "error_message":"",
	    "error_code":"",
	    "ackid":ackid,
	    "ABHICLID":groupref
	  }
	else:
	  jsonresp={"result":"fail","error_message":"New ABHICL Patient API:Patient Object Error", self.errormessage("ERR007"), "error_code":"ERR007"}
	  
          
    except Exception as e:
      msg = "New ABHICL Patient API Exception:\n" + self.rlgrobj.errormessage("ERR004")  + "\n(" + str(e) + ")"
      logger.loggerpms2(msg)
      jsonresp["result"] = "fail"
      jsonresp["error_code"] = "ERR004"
      jsonresp["error_message"] = msg
    
    return json.dumps(jsonresp)
  
  
  
  def newappointment(self,avars,appPath):
    
    db = self.db

    providerid = 0
    
    memberid = 0
    patientd = 0
    

    try:
      #get ABHICL appointment ID
      abhilcapptid = common.getstring(avars["ABHICLAPPTID"]) if "ABHICLAPPTID" in avars else None
      
      #get selected provider & region
      providercode = common.getstring(avars["providercode"]) if "providercode" in avars else None
      
      if((providercode == None) | (providercode == "")):
	
	msg = "New Appointment API: No Provider: " + self.rlgrobj.errormessage("ERR005")
	logger.loggerpms2.info(msg)
	jsonresp = {
          "result":"fail",
          "error_code":"ERR005",
          "error_message": msg
        }        
	return json.dumps(jsonresp)
      
      #get member and patientid
      abhiclid = common.getstring(avars["abhiclid"]) if "abhiclid" in avars else None
      p = db(db.patientmember.groupref == abhiclid).select()
      
      if(len(p) != 1):
	msg = "New Appointment API: No Patient: " + self.rlgrobj.errormessage("ERR008")
	logger.loggerpms2.info(msg)
	jsonresp = {
          "result":"fail",
          "error_code":"ERR008",
          "error_message": msg
        }        
	return json.dumps(jsonresp)
      
      cell = common.getstring(p[0].cell)
      doctorid = providerid
      complaint = "Appointment created from ABHILC Portal"
      providernotes = "Appointment created from ABHILC Portal"
      
      duration = 30
      dt = common.getstring(avars["appointmentdate"]) if "appointmentdate" in avars else (d1).strftime("%d/%m/%Y %I:%M %p")  #
      dt1 = datetime.datetime.strptime(dt, "%d/%m/%Y %I:%M %p")
      startdt = (dt1).strftime("%d/%m/%Y %H:%M")
      
      
      
      memberid = int(common.getid(p[0].id))
      v = db(db.vw_memberpatientlist.primarypatientid == memberid).select(db.vw_memberpatientlist.patientid)
      patientid = int(common.getid(v[0].patientid)) if(len(v) == 1) else 0
      if(patientid == 0):
	msg = "New Appointment API: No Patient: " + self.rlgrobj.errormessage("ERR008")
	logger.loggerpms2.info(msg)
	jsonresp = {
          "result":"fail",
          "error_code":"ERR008",
          "error_message": msg
        }        
	return json.dumps(jsonresp)
      
      
      oappt = mdpappointment.Appointment(db,provideid)
      aptt = oappt.newappointment(memberid, patientid, doctorid, complaint,startdt,duration,providernotes,cell,appPath)
      apptobj = json.loads(appt)
      
      if(apptobj["result"] == "success"):
	apptid = int(common.getid(apptobj["appointmentid"]))
	if((abhilcapptid != "") & (abhilcapptid != None)):
	  db(db.t_appointment.id == apptid).update(f_uniqueid = apptid)
	a = db(db.t_appointment.id == apptid).select(db.t_appointment.f_uniqueid)
	jsonresp = {
	  
	  "result":"success",
	  "error_message":"",
	  "error_code":"",
	  "ackid":ackid,
	  "apptref":a[0].f_uniqueid,
	}
      else:
	msg = "New Appointment API: No Appointment " + self.rlgrobj.errormessage("ERR009")
	logger.loggerpms2(msg)
	jsonresp["result"] = "fail"
	jsonresp["error_code"] = "ERR009"
	jsonresp["error_message"] = msg
	
      
    
    except Exception as e:
	msg = "New Appointment API Exception:\n" + self.rlgrobj.errormessage("ERR004")  + "\n(" + str(e) + ")"
	logger.loggerpms2(msg)
	jsonresp["result"] = "fail"
	jsonresp["error_code"] = "ERR004"
	jsonresp["error_message"] = msg
    
    return json.dumps(jsonresp)