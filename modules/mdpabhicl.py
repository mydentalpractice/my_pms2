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
from applications.my_pms2.modules import mail
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
 
 
  #This API is called from ABHICL site with the following information
  #unique ABHICL Member ID
  #member firstname, lastname, cell, email, dob, gender
  #This API will create or update the member information in MDP and sent an email/SMS to the member informing for 
  #appointment creation with MDP
  #The provider will be defaulted to P0001
  #The company will be ABHICL
  #The promocode will be ABHICL promocode
  
  def abhicl_member_registration(self,avars):
    
    db = self.db
    
    jsonresp = {}
    
    try:

      providercode = 'P0001'
      policy = "ABHICL40"
      
      promocode = avars["promocode"] if "promocode" in avars else "ABHICL40"
      
      r = db(db.company.groupkey == promocode).select(db.company.company)
      companycode = r[0].company if len(r) == 1 else 'ABHICL'
    
      abhiclid = avars["ABHICLID"] if "ABHICLID" in avars else common.generateackid("AB",10)
      
      
      fname = avars["firstname"] if "firstname" in avars else abhiclid + "_FN"
      lname = avars["lastname"] if "lastname" in avars else abhiclid + "_LN"
      cell = avars["cell"] if "cell" in avars else "0000000000"
      email = avars["email"] if "email" in avars else "mydentalplan.in@gmail.com"
  
      avars = {"promocode":promocode,"ABHICLID":abhiclid}
      
      #start session
      jobj = json.loads(self.startsession(avars))

      if(jobj["result"] == "fail"):
	
	msg = self.rlgrobj.xerrormessage("ABHICL101")
	logger.loggerpms2(msg)
	jsonresp = {}
	jsonresp["ABHICLID"] = abhiclid
	jsonresp["MDPMember"] = ""
	jsonresp["result"] = "fail"
	jsonresp["error_code"] = "ABHICL101"
	jsonresp["error_message"] = msg    
	return json.dumps(jsonresp)
	
      #create new abhicl patient
      avars = {
        
        "ackid":jobj["ackid"],
        "promocode":promocode,
        "ABHICLID":abhiclid,
        "firstname":fname,
        "lastname":lname,
        "cell":cell,
        "email":email,
        "policy":policy,
        "providercode":providercode
      }
      jobj = json.loads(self.newabhiclpatient(avars))
      if(jobj["result"] == "fail"):
	msg = self.rlgrobj.xerrormessage("ABHICL102")
	logger.loggerpms2(msg)
	jsonresp = {}
	jsonresp["ABHICLID"] = abhiclid
	jsonresp["MDPMember"] = ""
	jsonresp["result"] = "fail"
	jsonresp["error_code"] = "ABHICL102"
	jsonresp["error_message"] = msg    
	return json.dumps(jsonresp)
      
      #send sms/email notification
      #cellno = common.modify_cell(cell)
      #message = "You have been successfully registered with MyDental Health Plan.  They will call you to fix an appointment with a Dentist."
      #retval = mail.sendSMS2Email(db,cellno,message)
      
      #ccs = email
      #subject = "Member Registration"
      #message = "You have been successfully registered with MyDental Health Plan.  They will call you to fix an appointment with a Dentist."
      #retval = mail.groupEmail(db, email, email, subject, message)
      
      jsonresp = {}
      jsonresp["ABHICLID"] = abhiclid
      jsonresp["MDPMember"] = jobj["MDPMember"]
      jsonresp["result"] = "success"
      jsonresp["error_code"] = ""
      jsonresp["error_message"] = ""         

    except Exception as e:
	  msg =  self.rlgrobj.xerrormessage("ABHICL100") + ":New Member Registration"+ "\n" + str(e)
	  logger.loggerpms2.info(msg)
	  jsonresp = {}
	  jsonresp["ABHICLID"] = abhiclid
	  jsonresp["MDPMember"] = ""	  
	  jsonresp["result"] = "fail"
	  jsonresp["error_code"] = "ABHICL100"
	  jsonresp["error_message"] = msg    

    return json.dumps(jsonresp)
    
  def startsession(self,avars):
    
    db = self.db
    promocode = avars["promocode"] if "promocode" in avars else ""
    abhiclid = avars["abhiclid"] if "abhiclid" in avars else ""
    
    jsonresp = {}
    
    try:

      if(promocode != ""):
        # generate ackid 
        ackid = common.generateackid("AB",10)
        self.ackid = ackid
	
	db.sessionlog.insert(\
	  ackid = ackid,
	  promocode = promocode,
	  created_on = common.getISTFormatCurrentLocatTime(),
	  created_by = 1 ,
	  modified_on = common.getISTFormatCurrentLocatTime(),
	  modified_by = 1     
	)
	db.commit()
	
	jsonresp["ABHICLID"] = abhiclid
	jsonresp["MDPMember"] = ""
        jsonresp["result"] = "success"
        jsonresp["error_code"] = ""
        jsonresp["error_message"] = ""
        jsonresp["ackid"] = ackid    
	
        
      else:
        msg = self.rlgrobj.xerrormessage("ABHICL104")
        logger.loggerpms2.info(msg)
        jsonresp = {
          "result":"fail",
          "error_code":"ABHICL104",
          "error_message": msg
        }        
	jsonresp["ABHICLID"] = abhiclid
	jsonresp["MDPMember"] = ""      
     
    except Exception as e:
      msg = self.rlgrobj.xerrormessage("ABHICL100")  + ":Start Session" + "\n(" + str(e) + ")"
      logger.loggerpms2.info(msg)
      jsonresp = {}
      jsonresp["ABHICLID"] = abhiclid
      jsonresp["MDPMember"] = ""      
      jsonresp["result"] = "fail"
      jsonresp["error_code"] = "ABHICL100"
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
      abhiclid = avars["abhiclid"] if "abhiclid" in avars else ""
      
      #invalid session as no ackid is specified
      if((ackid == None) | (ackid == "")):
	
	msg = "New ABHICL Patient API Error: Missing ACKID\n" + self.rlgrobj.xerrormessage("ABHICL105")
	logger.loggerpms2.info(msg)
	jsonresp = {
	  "ABHICLID":abhcilcid,
	  "MDPMember":"",
          "result":"fail",
          "error_code":"ABHICL105",
          "error_message": msg
        }
	return json.dumps(jsonresp)	

      #get company
      r = db(db.sessionlog.ackid == ackid).select(db.company.company,db.company.id,db.company.city,db.company.st,db.company.pin,\
                                                  db.company.address1,db.company.address2,db.company.address3,\
                                                  left=[db.company.on(db.company.groupkey == db.sessionlog.promocode)])
      companycode = r[0].company if(len(r) == 1) else None
      companycity = r[0].city if(len(r) == 1) else ""
      companyst = r[0].st if(len(r) == 1) else ""
      companypin = r[0].pin if(len(r) == 1) else ""
      companyaddr1 = r[0].address1 if(len(r) == 1) else ""
      companyaddr2 = r[0].address2 if(len(r) == 1) else ""
      companyaddr3 = r[0].address3 if(len(r) == 1) else ""
      
      companyid = int(common.getid(r[0].id)) if(len(r) == 1) else 0
      
      if((companycode == "") | (companycode==None) | (companyid == 0)):
	msg = "New ABHICL Patient API Error: Missing Company\n" + self.rlgrobj.xerrormessage("ABHICL105")	
	logger.loggerpms2.info(msg)
	jsonresp = {
	  "ABHICLID":abhcilcid,
	  "MDPMember":"",	  
          "result":"fail",
          "error_code":"ABHICL105",
          "error_message": msg
        }
	return json.dumps(jsonresp)


      #get policy	
      policy = avars["policy"] if "policy" in avars else None
      if((policy == None) | (policy == "")):
	msg = "New ABHICL Patient API Error: Missing Policy\n" + self.rlgrobj.xerrormessage("ABHICL105")	
	logger.loggerpms2.info(msg)
	jsonresp = {
	  "ABHICLID":abhcilcid,
	  "MDPMember":"",	  
          "result":"fail",
          "error_code":"ABHICL105",
          "error_message": msg
        }
	return json.dumps(jsonresp)
      
      
      #get selected provider & region
      providercode = common.getstring(avars["providercode"]) if "providercode" in avars else None
      
      if((providercode == None) | (providercode == "")):
	msg = "New ABHICL Patient API Error: Missing Provider\n" + self.rlgrobj.xerrormessage("ABHICL105")	
	logger.loggerpms2.info(msg)
	jsonresp = {
	  "ABHICLID":abhcilcid,
	  "MDPMember":"",	  
          "result":"fail",
          "error_code":"ABHICL105",
          "error_message": msg
        }
	return json.dumps(jsonresp)

      provs = db((db.provider.provider == providercode) & (db.provider.is_active == True)).select()
      
      if(len(provs) != 1):
	msg = "New ABHICL Patient API Error: Mulltiple Providers\n" + self.rlgrobj.xerrormessage("ABHICL105")	
	logger.loggerpms2.info(msg)
	jsonresp = {
	  "ABHICLID":abhcilcid,
	  "MDPMember":"",	  
          "result":"fail",
          "error_code":"ABHICL105",
          "error_message": msg
        }
	return json.dumps(jsonresp)

      providerid = int(common.getid(provs[0].id))
      regionid = int(common.getid(provs[0].groupregion))
      r = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select()
      regioncode = common.getstring(r[0].groupregion) if(len(r) == 1) else None
	
      
      #get planid for the patient
      x = None
      x = db(\
             (db.provider_region_plan.companycode == companycode) &\
             (db.provider_region_plan.regioncode == regioncode) & (db.provider_region_plan.policy == policy) &\
             (db.provider_region_plan.is_active == True)).select()
             
      if(len(x) == 0):
	regioncode = "ALL"
	x = db(\
	       (db.provider_region_plan.companycode == companycode) &\
	       (db.provider_region_plan.regioncode == regioncode) & (db.provider_region_plan.policy == policy) &\
	       (db.provider_region_plan.is_active == True)).select()
	       
	
      plancode = common.getstring(x[0].plancode) if(len(x) == 1) else None
      p = db(db.hmoplan.hmoplancode == plancode).select()
      planid = int(common.getid(p[0].id)) if(len(p) == 1) else 0
      
      if(planid == 0):
	msg = "New ABHICL Patient API Error: No Plan\n" + self.rlgrobj.xerrormessage("ABHICL105")	
	logger.loggerpms2.info(msg)
	jsonresp = {
	  "ABHICLID":abhcilcid,
	  "MDPMember":"",	  
          "result":"fail",
          "error_code":"ABHICL105",
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
	msg = "New ABHICL Patient API Error: Generating MDP MemberID\n" + self.rlgrobj.xerrormessage("ABHICL105")	
	logger.loggerpms2.info(msg)
	jsonresp = {
	  "ABHICLID":abhcilcid,
	  "MDPMember":"",	  
          "result":"fail",
          "error_code":"ABHICL105",
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
                                                
                                                dob = datetime.datetime.strptime(avars["dob"] if "dob" in avars else "01/01/1990", "%d/%m/%Y" ),
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
	  jsonresp={"result":"fail","error_message":"New ABHICL Patient API:Patient ID None\n"+self.rlgrobj.xerrormessage("ERR007"), "error_code":"ERR007"}
	  return json.dumps(jsonresp)

      opat = mdppatient.Patient(db, providerid)
      patobj = json.loads(opat.getpatient(patid, patid, ""))
      if(patobj["result"] == "success"):
	jsonresp = {
          "result":"success",
          "error_message":"",
          "error_code":"",
          "ackid":ackid,
          "ABHICLID":groupref,
	  "MDPMember":patientmember
        }
      else:
	msg = "New ABHICL Patient API Error: Patient Object\n" + self.rlgrobj.xerrormessage("ABHICL105")	
	logger.loggerpms2.info(msg)
	jsonresp = {
          "ABHICLID":abhcilcid,
          "MDPMember":"",	  
          "result":"fail",
          "error_code":"ABHICL105",
          "error_message": msg
	  }
    except Exception as e:
      msg = self.rlgrobj.xerrormessage("ABHICL100")  + ":New ABHICL Patient" + "\n(" + str(e) + ")"
      logger.loggerpms2.info(msg)
      jsonresp = {}
      jsonresp["ABHICLID"] = abhiclid
      jsonresp["MDPMember"] = ""      
      jsonresp["result"] = "fail"
      jsonresp["error_code"] = "ABHICL100"
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