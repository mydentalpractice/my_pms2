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


class ABHICL:
  def __init__(self,db,providerid=0):
    self.db = db
    self.providerid = providerid
    self.rlgrobj = Religare(db, providerid)
 
 
  #This API is called from ABHICL site with the following information
  #unique ABHICL Member ID
  #member firstname, lastname, cell, email, dob, gender
  #This API will create or update the member information in MDP 
  #The provider will be defaulted to P0001
  #The company will be ABHICL
  #The promocode will be ABHIC promocode
  
  def dental_service_request(self,avars):
    
    db = self.db
    
    jsonresp = {}
    
    try:

      logger.loggerpms2.info("Enter dental_service_request\n" + str(avars))
      providercode = 'P0001'
      policy = "ABHI"
      
      promocode = getvalue(avars,"promocode","ABHI") #avars["promocode"] if "promocode" in avars else "ABHI"
      companycode = getvalue(avars,"companycode","ABHI") #avars["companycode"] if "companycode" in avars else "ABHI"
      
      defval = common.generateackid("AB",10)
      abhiclid = getvalue(avars,"ABHICLID",defval)
      
      #abhiclid = avars["ABHICLID"] if "ABHICLID" in avars else common.generateackid("AB",10)
      
      #r = db(db.company.groupkey == promocode).select(db.company.company)
      #companycode = r[0].company if len(r) == 1 else 'ABHI'
      
     
      
      
      
      fname = getvalue(avars,"firstname",abhiclid + "_FN") #avars["firstname"] if "firstname" in avars else abhiclid + "_FN"
      lname = getvalue(avars,"lastname",abhiclid + "_LN") #avars["lastname"] if "lastname" in avars else abhiclid + "_LN"
      cell = getvalue(avars,"cell","0000000000") #avars["cell"] if "cell" in avars else "0000000000"
      email = getvalue(avars,"email","mydentalplan.in@gmail.com") #avars["email"] if "email" in avars else "mydentalplan.in@gmail.com"
  
      avars = {"promocode":promocode,"companycode":companycode,"ABHICLID":abhiclid}
      
      #start session
      jobj = json.loads(self.startsession(avars))

      if(jobj["result"] == "fail"):
	
	msg = self.rlgrobj.xerrormessage("ABHICL101")
	logger.loggerpms2.info(msg)
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
        "companycode":companycode,
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
	logger.loggerpms2.info(msg)
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
    promocode = getvalue(avars,"promocode","") #avars["promocode"] if "promocode" in avars else ""
    abhiclid = getvalue(avars,"abhiclid","ABHI") #avars["abhiclid"] if "abhiclid" in avars else ""
    
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
      
      ackid = getvalue(avars,"ackid",None) #avars["ackid"] if "ackid" in avars else None
      abhiclid = getvalue(avars,"ABHICLID",None) #avars["ABHICLID"] if "ABHICLID" in avars else ""
      companycode = getvalue(avars,"companycode","ABHI") #avars["companycode"] if "companycode" in avars else "ABHI"
      
      #invalid session as no ackid is specified
      if((ackid == None) | (ackid == "")):
	
	msg = "New ABHICL Patient API Error: Missing ACKID\n" + self.rlgrobj.xerrormessage("ABHICL105")
	logger.loggerpms2.info(msg)
	jsonresp = {
	  "ABHICLID":abhiclid,
	  "MDPMember":"",
          "result":"fail",
          "error_code":"ABHICL105",
          "error_message": msg
        }
	return json.dumps(jsonresp)	

      #get company
      
      r = db(db.company.company == companycode).select()
      
      #r = db(db.sessionlog.ackid == ackid).select(db.company.company,db.company.id,db.company.city,db.company.st,db.company.pin,\
                                                  #db.company.address1,db.company.address2,db.company.address3,\
                                                  #left=[db.company.on(db.company.groupkey == db.sessionlog.promocode)])
						  
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
	  "ABHICLID":abhiclid,
	  "MDPMember":"",	  
          "result":"fail",
          "error_code":"ABHICL105",
          "error_message": msg
        }
	return json.dumps(jsonresp)


      #get policy	
      policy = getvalue(avars,"policy", None) #avars["policy"] if "policy" in avars else None
      if((policy == None) | (policy == "")):
	msg = "New ABHICL Patient API Error: Missing Policy\n" + self.rlgrobj.xerrormessage("ABHICL105")	
	logger.loggerpms2.info(msg)
	jsonresp = {
	  "ABHICLID":abhiclid,
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
	  "ABHICLID":abhiclid,
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
	  "ABHICLID":abhiclid,
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
	  "ABHICLID":abhiclid,
	  "MDPMember":"",	  
          "result":"fail",
          "error_code":"ABHICL105",
          "error_message": msg
        }
	return json.dumps(jsonresp)

      #patientmember
      patientmember = None
      r = db(db.patientmember.groupref == abhiclid).select(db.patientmember.patientmember)
      if(len(r)==1):
	patientmember = r[0].patientmember
      else:
      
	sql = "UPDATE membercount SET membercount = membercount + 1 WHERE company = " + str(companyid) + ";"
	db.executesql(sql)
	db.commit()    
	xrows = db(db.membercount.company == companyid).select()
	membercount = int(common.getid(xrows[0].membercount)) if(len(xrows) == 1) else -1
	if(membercount < 0):
	  msg = "New ABHICL Patient API Error: Generating MDP MemberID\n" + self.rlgrobj.xerrormessage("ABHICL105")	
	  logger.loggerpms2.info(msg)
	  jsonresp = {
	    "ABHICLID":abhiclid,
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
          "ABHICLID":abhiclid,
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
      abhilcapptid = getvalue(avars,"ABHICLAPPTI",None) #avars["ABHICLAPPTID"] if "ABHICLAPPTID" in avars else None
      
      #get selected provider & region
      providercode = getvalue(avars,"providercode",None) #avars["providercode"] if "providercode" in avars else None
      
      if((providercode == None) | (providercode == "")):
	
	msg = "New Appointment API: No Provider: " + self.rlgrobj.xerrormessage("ERR005")
	logger.loggerpms2.info(msg)
	jsonresp = {
          "result":"fail",
          "error_code":"ERR005",
          "error_message": msg
        }        
	return json.dumps(jsonresp)
      
      #get member and patientid
      abhiclid = getvalue(avars,"ABHICLID",None) #avars["abhiclid"] if "abhiclid" in avars else None
      p = db(db.patientmember.groupref == abhiclid).select()
      
      if(len(p) != 1):
	msg = "New Appointment API: No Patient: " + self.rlgrobj.xerrormessage("ERR008")
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
	msg = "New Appointment API: No Patient: " + self.rlgrobj.xerrormessage("ERR008")
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
	msg = "New Appointment API: No Appointment " + self.rlgrobj.xerrormessage("ERR009")
	logger.loggerpms2.info(msg)
	jsonresp["result"] = "fail"
	jsonresp["error_code"] = "ERR009"
	jsonresp["error_message"] = msg
	
      
    
    except Exception as e:
	msg = "New Appointment API Exception:\n" + self.rlgrobj.xerrormessage("ERR004")  + "\n(" + str(e) + ")"
	logger.loggerpms2.info(msg)
	jsonresp["result"] = "fail"
	jsonresp["error_code"] = "ERR004"
	jsonresp["error_message"] = msg
    
    return json.dumps(jsonresp)
  


  def get_treatments(self,avars):
    
    logger.loggerpms2.info("Enter get treatments\n" + str(avars))
    db = self.db

    jsonresp = {}
    try:
    
      #get memberid
      abhiclid = getvalue(avars,"ABHICLID","")
      
     

      patientid = 0
      memberid = 0
      
      if(abhiclid != ""):
	r = db(db.patientmember.groupref == abhiclid).select(db.patientmember.id)
	if(len(r) == 1):
	  memberid = int(common.getid(r[0].id)) 
	  patientid = memberid

      #get company code 
      companycode = getvalue(avars,"company","ABHI")
      r = db(db.company.company == companycode).select(db.company.id)
      companyid = r[0].id if len(r) == 1 else 0 
      
      #get from/to dates
      today = datetime.datetime.now()
	   
      t1 = str(today.day) + "/" + str(today.month) + "/" + str(today.year) 
      t2 = str(today.day) + "/" + str(today.month) + "/" + str(today.year) 
      
      sfrom_date = getvalue(avars,"from_date","") #avars["from_date"]  if "from_date" in avars else ""
      from_date = datetime.datetime.strptime(t1 if sfrom_date == "" else sfrom_date, "%d/%m/%Y")

      sto_date = getvalue(avars,"to_date","")  #avars["to_date"]  if "to_date" in avars else ""
      to_date = datetime.datetime.strptime(t2 if sto_date == "" else sto_date, "%d/%m/%Y")      

      #get status
      status = getvalue(avars,"status","")  #avars["status"] if "status" in avars else "" 
      
      
      query = ""
      query = (db.vw_treatmentlist.companyid == companyid) if(companyid > 0) else (1==1)
      query = query & ((db.vw_treatmentlist.memberid == memberid)&(db.vw_treatmentlist.patientid == patientid)) if(abhiclid != "") else (1==1)
      query = query & ((db.vw_treatmentlist.startdate >= from_date) & (db.vw_treatmentlist.startdate <= to_date))
      
      
      if(status == ""):
	query = query & (db.vw_treatmentlist.is_active == True) & ((db.vw_treatmentlist.status == "Started") | (db.vw_treatmentlist.status == "Completed"))
      elif (status == "ALL"):
	query = query & ((db.vw_treatmentlist.status == "Started") | (db.vw_treatmentlist.status == "Completed") | (db.vw_treatmentlist.status == "Cancelled"))
      elif ((status == 'Started') | (status == "Completed")):
	query = query & ((db.vw_treatmentlist.status == status) & (db.vw_treatmentlist.is_active == True))
      else:
	query = query & (db.vw_treatmentlist.status == status)
	
      logger.loggerpms2.info("get treatments->\n" + str(query))
      
      treatments = db(query).select(db.vw_treatmentlist.id,db.vw_treatmentlist.tplanid,db.vw_treatmentlist.treatment,db.vw_treatmentlist.startdate, db.vw_treatmentlist.enddate,db.vw_treatmentlist.patientname,\
                                    db.vw_treatmentlist.status,db.vw_treatmentlist.treatmentcost,db.vw_treatment_procedure_group.shortdescription,db.vw_treatmentlist.notes,\
                                    db.vw_treatmentlist.groupref,db.vw_treatmentlist.patientmember,db.vw_treatmentlist.doctorname,db.vw_treatmentlist.chiefcomplaint,\
                                    db.vw_treatmentlist.tooth,db.vw_treatmentlist.quadrant,\
                                    left=db.vw_treatment_procedure_group.on(db.vw_treatment_procedure_group.treatmentid==db.vw_treatmentlist.id),\
                                    orderby=~db.vw_treatmentlist.id)     
    
      
      
      treatmentlist = []
  
      for treatment in treatments:

	proclist = []
	procobj = {}
        procs = db(db.vw_treatmentprocedure.treatmentid == treatment.vw_treatmentlist.id).select()
	for proc in procs:
	  procobj = {
	    "code"  : proc.procedurecode,
	    "procedure":proc.altshortdescription
	  }
	  proclist.append(procobj)
	
	prescrlist = []
	prescrobj = {}
	prescriptions = db(db.vw_patientprescription.treatmentid == treatment.vw_treatmentlist.id).select()
	for prescr in prescriptions:
	  prescrobj = {
	    "date": (prescr.prescriptiondate).strftime("%d/%m/%Y"),
	    "medicine":prescr.medicine,
	    "dosage":prescr.strength,
	    "dosageuom":prescr.strengthuom
	  }
	  prescrlist.append(prescrobj)
	
	treatmentobj = {
	  "status": "Started" if(common.getstring(treatment.vw_treatmentlist.status) == "") else common.getstring(treatment.vw_treatmentlist.status),
	  
	  "ABHICLID":treatment.vw_treatmentlist.groupref,
	  "MDPMember":treatment.vw_treatmentlist.patientmember,
	  "patientname" : common.getstring(treatment.vw_treatmentlist.patientname),
          "treatment": common.getstring(treatment.vw_treatmentlist.treatment),
          "treatment_start_date"  : (treatment.vw_treatmentlist.startdate).strftime("%d/%m/%Y"),
	  "treatment_end_date"  : (treatment.vw_treatmentlist.enddate).strftime("%d/%m/%Y"),
	  "doctorname":treatment.vw_treatmentlist.doctorname,
	  "tooth":treatment.vw_treatmentlist.tooth,
	  "quadrant":treatment.vw_treatmentlist.quadrant,
	  "notes":treatment.vw_treatmentlist.notes,
	  
          "procedures":proclist,
	  "medicines":prescrlist
        }
	
	treatmentlist.append(treatmentobj)        	
      
     
      
      jsonresp = {
        
        "result":"success",
        "error_code":"",
        "error_message":"",
        "treatmentlist":treatmentlist
      }
      
    except Exception as e:
      msg =  self.rlgrobj.xerrormessage("ABHICL100") + ":Get ABHICL Treatments"+ "\n" + str(e)
      logger.loggerpms2.info(msg)
      jsonresp = {}
      jsonresp["result"] = "fail"
      jsonresp["error_code"] = "ABHICL100"
      jsonresp["error_message"] = msg    
    
    return json.dumps(jsonresp)
  
  
  def get_appointments(self,avars):
     
    logger.loggerpms2.info("Enter get_appointments")
    db = self.db

    jsonresp = {}
    try:
    
      #get memberid
      abhiclid = getvalue(avars,"ABHICLID","")  #avars["ABHICLID"] if "ABHICLID" in avars else ""

      patientid = 0
      memberid = 0
      
      if(abhiclid != ""):
	r = db(db.patientmember.groupref == abhiclid).select(db.patientmember.id)
	if(len(r) == 1):
	  memberid = int(common.getid(r[0].id))    
	  patientid = memberid
      
      companycode = getvalue(avars,"company","ABHI") #avars["company"] if "company" in avars else "ABHI"
      r = db(db.company.company == companycode).select(db.company.id)
      companyid = r[0].id if len(r) == 1 else 0      
      
      today = datetime.datetime.now()
      
      t1 = str(today.day) + "/" + str(today.month) + "/" + str(today.year) + " 00:00"
      t2 = str(today.day) + "/" + str(today.month) + "/" + str(today.year) + " 23:59"
      
      sfrom_date = getvalue(avars,"from_date","") #avars["from_date"]  if "from_date" in avars else ""
      from_date = datetime.datetime.strptime(t1 if sfrom_date == "" else sfrom_date + " 00:00", "%d/%m/%Y %H:%M")

      sto_date = getvalue(avars,"to_date","") #avars["to_date"]  if "to_date" in avars else ""
      to_date = datetime.datetime.strptime(t2 if sto_date == "" else sto_date + " 23:59", "%d/%m/%Y %H:%M")

      
      #from_date = datetime.datetime.strptime(avars["from_date"] + " 00:00" if "from_date" in avars else t1, "%d/%m/%Y %H:%M" )
      #to_date = datetime.datetime.strptime(avars["to_date"] + " 23:59" if "to_date" in avars else t2, "%d/%m/%Y %H:%M" )

      
      status = getvalue(avars,"status","") #avars["status"] if "status" in avars else "" 
      
     
      
      query = ""
      query = (db.vw_appointments.companyid == companyid) if(companyid > 0) else (1==1)
      query = query & ((db.vw_appointments.patientmember == memberid)&(db.vw_appointments.patient == patientid)) if(abhiclid != "") else (1==1)
      query = query & ((db.vw_appointments.f_start_time >= from_date) & (db.vw_appointments.f_start_time <= to_date))
      
      
      if(status == ""):
	query = query & (db.vw_appointments.is_active == True) & ((db.vw_appointments.f_status == "Open") | (db.vw_appointments.f_status == "Checked-In"))
      elif (status == "ALL"):
	query = query & ((db.vw_appointments.f_status == "Open") | (db.vw_appointments.f_status == "Checked-In") | (db.vw_appointments.f_status == "Cancelled"))
      elif ((status == 'Open') | (status == "Checked-in") | (status == "Checked-In")):
	query = query & ((db.vw_appointments.f_status == status) & (db.vw_appointments.is_active == True))
      else:
	query = query & (db.vw_appointments.f_status == status)
	
      logger.loggerpms2.info("get_appointments->\n" + str(query))
      
      appts = db(query).select()
      
      apptlist = []
           
  
  
  
      for appt in appts:

	apptobj = {
	  
	  "ABHICLID":appt.groupref,
	  "MDPMember":appt.membercode,
          "status": "Open" if(appt.f_status == "") else appt.f_status,
          "patientname" : appt.f_patientname,
          "apptdatetime":(appt.f_start_time).strftime("%d/%m/%Y %H:%M")
        }
	apptlist.append(apptobj)        	
      
     
      
      jsonresp = {
        
        "result":"success",
        "error_code":"",
        "error_message":"",
        "appointment_list":apptlist
      }
      
    except Exception as e:
      msg =  self.rlgrobj.xerrormessage("ABHICL100") + ":Get ABHICL Appointments"+ "\n" + str(e)
      logger.loggerpms2.info(msg)
      jsonresp = {}
      jsonresp["result"] = "fail"
      jsonresp["error_code"] = "ABHICL100"
      jsonresp["error_message"] = msg    
    
    return json.dumps(jsonresp)  
  
  
  #Returns member details for abhiclic
  def getabhiclmember(self,abhiclid):

    logger.loggerpms2.info("Enter Get ABHICL Member ")

    db = self.db
    providerid = self.providerid
    auth = current.auth

    try:

      r = db((db.patientmember.groupref == abhiclid) & (db.patientmember.is_active == True)).select()
      
      if(len(r) != 1):
	mssg = "Get ABHICL Member  API:\n" + errormessage(db,"MDP101") + ")"
	patobj1["result"] = "fail"
	patobj1["error_code"] = "MDP101"
	patobj1["error_message"] = mssg
	logger.loggerpms2.info(mssg)
	return json.dumps(patobj1)      
      
      memberid = int(common.getid(r[0].id))
      
      
      opat = mdppatient.Patient(db, providerid)
      patobj = opat.getpatient(memberid, memberid, "")


    except Exception as e:
      patobj1 = {}
      mssg = "Get ABHICL Patient API exception:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")"
      patobj1["result"] = "fail"
      patobj1["error_code"] = "MDP100"
      patobj1["error_message"] = mssg
      return json.dumps(patobj1) 

    return patobj      
  
  
  
  def getABHICLprocedures(self,procedurepriceplancode,searchphrase="",page=0,maxcount=0):
  
    logger.loggerpms2.info("XXX:Enter Get ABHICL Procedures \n"   + " " + procedurepriceplancode + " " + searchphrase + " " + str(page) + " " + str(maxcount))    
  
    db = self.db
    providerid = self.providerid
  
  
    page = page -1
    urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
    items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
    limitby = ((page)*items_per_page,(page+1)*items_per_page)      
    
    proclist = []
    procobj = {}
    result = "success"
    error_message = ""
    query = ""
    
    try:
      if((searchphrase == "") | (searchphrase == None)):
	query = (db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode)&\
	  (db.vw_procedurepriceplan_relgr.is_active == True) & (db.vw_procedurepriceplan_relgr.relgrproc ==True)        
      else:
	query = (db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode)&\
	  (db.vw_procedurepriceplan_relgr.shortdescription.like('%' + searchphrase + '%'))&\
	  (db.vw_procedurepriceplan_relgr.is_active == True) & (db.vw_procedurepriceplan_relgr.relgrproc ==True)        
  
      #logger.loggerpms2.info("Get Religare Patient " + str(query))
  
      if(page >=0 ): 
	procs = db(query).select(\
	  db.vw_procedurepriceplan_relgr.ALL,  \
	  
	  orderby=db.vw_procedurepriceplan_relgr.procedurecode,\
	  limitby=limitby\
	)
	#logger.loggerpms2.info("Get Religare Patient Procs" +str(len(procs)))
	if(maxcount == 0):
  
	  procs1 = db(query).select(\
	    db.vw_procedurepriceplan_relgr.ALL,\
            orderby=db.vw_procedurepriceplan_relgr.procedurecode\
	  )    
	  maxcount = len(procs1)
      else:
	procs = db(query).select(\
	  db.vw_procedurepriceplan_relgr.ALL, \
	  orderby=db.vw_procedurepriceplan_relgr.procedurecode
	  
	)
	if(maxcount == 0):
	  maxcount = len(procs)
  
      #logger.loggerpms2.info("Get Religare Patient Procs A" + str(len(procs)))
  
      for proc in procs:
	procobj = {
	  "plan":procedurepriceplancode,
	  "procedurecode":proc.vw_procedurepriceplan_relgr.procedurecode,
	  "altshortdescription":common.getstring(proc.vw_procedurepriceplan_relgr.altshortdescription),
	  "procedurefee":float(common.getvalue(proc.vw_procedurepriceplan_relgr.relgrprocfee)),
	  "inspays":float(common.getvalue(proc.vw_procedurepriceplan_relgr.relgrinspays)),
	  "copay":float(common.getvalue(proc.vw_procedurepriceplan_relgr.relgrcopay)),
	  "service_id":common.getstring(proc.vw_procedurepriceplan_relgr.service_id),
	  "service_name":common.getstring(proc.vw_procedurepriceplan_relgr.service_name),
	  "service_category":common.getstring(proc.vw_procedurepriceplan_relgr.service_category)
	}        
	proclist.append(procobj) 
	result = 'success'
	error_message = ""
  
    except Exception as e:
      result = "fail"
      error_message = "Get ABHICL Procedure API:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
      logger.loggerpms2.info(error_message)
  
    xcount = ((page+1) * items_per_page) - (items_per_page - len(procs)) 
  
    bnext = True
    bprev = True
  
    #first page
    if((page+1) == 1):
      bnext = True
      bprev = False
  
    #last page
    if(len(procs) < items_per_page):
      bnext = False
      bprev = True  
  
    return json.dumps({"result":result,"error_message":error_message,"count":len(procs),"page":page+1,"proclist":proclist,"runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev})
  
  
  
  
  
  #this APi adds a new procedure to the treatment
  def addABHICLProcedureToTreatment(self,treatmentid,procedurepriceplancode, procedurecode,
                                 tooth, quadrant,remarks,abhiclid,abhiclpolicy):
    
    
    logger.loggerpms2.info(">>Add ABHICL Procedure\n")
    
    
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    jsonresp = {}
    
    
    
    try:
      
      
      
      procobj = mdpprocedure.Procedure(db,providerid)
      jsonresp = procobj.addcompanyProcedureToTreatment(treatmentid, 
                                                       procedurepriceplancode, 
                                                       procedurecode, 
                                                       tooth, 
                                                       quadrant, 
                                                       remarks)
      
      jsonresp = json.loads(jsonresp)
      
      jsonresp["abhiclid"] = abhiclid
      jsonresp["abhiclpolicy"] = abhiclpolicy
      
        
 
    except Exception as e:
      mssg = "addABHICLProcedureToTreatment Exception error:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")"
      logger.loggerpms2.info(mssg)
      jsonresp = {
        "result":"fail",
        "error_message":mssg,
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
      }
      

    return json.dumps(jsonresp)  