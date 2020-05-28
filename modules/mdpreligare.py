from gluon import current
db = current.globalenv['db']

import json
import datetime
import time
from datetime import timedelta

import requests
import urllib
import base64
import hashlib
import uuid

import random



from applications.my_pms2.modules import common
from applications.my_pms2.modules import mdputils
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import account

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



def validsession(ackid):
  r = db(db.sessionlog.ackid == ackid).count()
  if(r == 1):
    return True
  else:
    return False
 
class RlgEncryption:
  
  def __init__(self):
    
    return
  
  #This method 
  #stringify json obj
  #encrypt stringified json obj
  #base64 encode
  #return {"req_data":<encoded encrypted json data}
  def encoderequestdata(self,jsondata):
    jsonstr = json.dumps(jsondata)
    jsonstrencrypt = self.encrypts(jsonstr)
    #jsonstrencoded = base64.b64encode(jsonstrencrypt)
    #jsonstrdecrypt = self.decrypts(jsonstrencrypt)
    reqobj = {"req_data":jsonstrencrypt}
    
    return reqobj  
  
  def decoderesponsedata(self,jsondatastr):
    #jsonstrdecoded = base64.b64decode(jsondatastr)
     
    jsonstrdecrypt = self.decrypts(jsondatastr)
    jsondata = json.loads(jsonstrdecrypt)
    return jsondata
    
  def encrypts128(self,raw):
	
	phpurl = "http://myphp128.com/encrypt.php"
	
	rlgrobj = {"raw":raw}
	
	resp = requests.post(phpurl,json=rlgrobj)
	
	jsonresp = {}
	if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
	      respobj = resp.json()    
	      jsonresp = {
	        "encrypt": respobj["encrypt"]
	       
	      }
	else:
	  jsonresp={"encrypt": "Response Error - " + str(resp.status_code)}
	  
	return jsonresp["encrypt"]    
 
  def decrypts128(self,encrypt):    
    phpurl = "http://myphp128.com/decrypt.php"
    
    rlgrobj = {"encrypt":encrypt}
    
    resp = requests.post(phpurl,json=rlgrobj)
    
    jsonresp = {}
    if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
	  respobj = resp.json()    
	  jsonresp = {
	    "raw": respobj["raw"]
	  }
    else:
      jsonresp = {"raw":"Request Error - " + str(resp.status_code)}
      
    return jsonresp["raw"]
    

  def decrypts(self,encrypt):
    
    
    phpurl = "http://myphp.com/decrypt.php"
    
    rlgrobj = {"encrypt":encrypt}
    
    resp = requests.post(phpurl,json=rlgrobj)
    
    jsonresp = {}
    if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
	  respobj = resp.json()    
	  jsonresp = {
	    "raw": respobj["raw"]
	  }
    else:
      jsonresp = {"raw":"Request Error - " + str(resp.status_code)}
      
    return jsonresp["raw"]

  def decrypt(self,encrypt):
    
    phpurl = "http://myphp.com/decrypt.php"
    
    rlgrobj = {"encrypt":encrypt}
    
    resp = requests.post(phpurl,json=rlgrobj)
    
    jsonresp = {}
    if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
	  respobj = resp.json()    
	  jsonresp = {
	    "raw": respobj["raw"]
	  }
    return json.dumps(jsonresp)  

  def encrypt_login(self,action,providerid,username,password):
    
    request_data = {"action":action, "providerid":providerid,"username":username, "password":password}
    request_data_string = json.dumps(request_data)
    encrypt_string = self.encrypts(request_data_string)
    
    
    return encrypt_string
  
  def encrypts(self,raw):
      
      phpurl = "http://myphp.com/encrypt.php"
      
      rlgrobj = {"raw":raw}
      
      resp = requests.post(phpurl,json=rlgrobj)
      
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
	    respobj = resp.json()    
	    jsonresp = {
	      "encrypt": respobj["encrypt"]
	     
	    }
      else:
	jsonresp={"encrypt": "Response Error - " + str(reps.status_code)}
	
      return jsonresp["encrypt"]

  def encrypt(self,raw):
    
    phpurl = "http://myphp.com/encrypt.php"
    
    rlgrobj = {"raw":raw}
    
    resp = requests.post(phpurl,json=rlgrobj)
    
    jsonresp = {}
    if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
	  respobj = resp.json()    
	  jsonresp = {
	    "encrypt": respobj["encrypt"]
	   
	  }
    return json.dumps(jsonresp)
      
  

class Religare:
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    
    props = db(db.urlproperties.id > 0).select(db.urlproperties.relgrprodurl, db.urlproperties.relgrapikey)
    
    self.url = "" if(len(props)==0) else props[0].relgrprodurl
    self.apikey = "" if(len(props)==0) else props[0].relgrapikey
    self.ackid = ""
    return 
  
  
  def xerrormessage(self,errorcode,response_message=""):
    db = self.db
    
    errormssgs = db((db.rlgerrormessage.code == errorcode) & (db.rlgerrormessage.is_active == True)).select()
    
    #if error_code not in the Error table, then add it, commit, and reload
    if(len(errormssgs)==0):
      db.rlgerrormessage.insert(code=errorcode,internalmessage=response_message,externalmessage=response_message + " Please contact MDP Customer Support")
      db.commit()
      errormssgs = db((db.rlgerrormessage.code == errorcode) & (db.rlgerrormessage.is_active == True)).select()
    errormssg = errorcode + ":" + response_message  if(len(errormssgs) == 0) else errorcode + ":\n" + common.getstring(errormssgs[0].externalmessage)
    
    return errormssg
  
  
  #this will create a new religare patient if not in db else return the current religare pateint.
  #
  def getreligarepatient(self,customer_id, customer_name,cell,dob,gender,policy="Smiley"):

    logger.loggerpms2.info("Enter Get Religare Patient ")
    #logger.loggerpms2.info("Enter Get Religare Patient " + common.getstring(policy)  )

    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    
    patobj = []
    fname = ""
    lname = ""
    
    companycode = 'RLG'
    companyid = 0
    
    providercode = None
    
    regioncode = None
    regionid = 0
    
    plancode = None
    planid = 0
    
    
    try:
      customer_name = "RLG_" + str(common.getstring(customer_id))  if(common.getstring(customer_name) == "") else customer_name
      
     
      dob = "1990-01-01" if(dob == None) else (dob if(dob != "") else "1990-01-01")
      
      d=dob.split('-')  #dob is in YYYY-m-d format
      dob = datetime.datetime.strptime(d[2] + "/" + d[1] + "/" + d[0], "%d/%m/%Y")
      
      patientmember = "RLGDEL0001"   #default religare member in DEL region

      ##from provider id, get provider city and region
      #provs = db((db.rlgprovider.providerid == providerid) & (db.rlgprovider.is_active == True)).select()
      if(1==1):
	companycode = 'RLG'
	c = db(db.company.company == companycode).select()
	companyid = int(common.getid(c[0].id)) if(len(c) > 0) else 0

        
	if(policy == None):  # for smiley card take it from the provider for backward compatibility
	  provs = db((db.rlgprovider.providerid == providerid) & (db.rlgprovider.is_active == True)).select()
	  providercode = common.getstring(provs[0].providercode) if(len(provs) == 1) else None
	  #planid = int(common.getid(provs[0].planid)) if(len(provs) == 1) else 1
	  #regionid = int(common.getid(provs[0].regionid)) if(len(provs) == 1) else 1
	  #r = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select()
	  #regioncode = common.getstring(r[0].groupregion) if(len(r) == 1) else None		  

	  #h = db((db.hmoplan.id == planid) & (db.hmoplan.is_active == True)).select()
	  #plancode = common.getstring(h[0].hmoplancode) if(len(h) > 0) else "RLGMUM102" 
	  #hmoplancode = plancode
	  
	  planprovdict = mdputils.getprocedurepriceplancode(db,None, providercode, None, None)
	  planid = planprovdict["planid"] if(planprovdict["planid"] != None) else 1
	  plancode = planprovdict["plancode"] if(planprovdict["plancode"] != None) else ""
	  hmoplancode = plancode
	  procedurepriceplancode = planprovdict["procedurepriceplancode"] if(planprovdict["procedurepriceplancode"] != None) else ""
	  
	  #p = db((db.provider.id == providerid) & (db.provider.is_active == True)).select()
	  
	else: # for all other religare plans like 399, 499, 699 etc. take it from provider_region_plan
	  #logger.loggerpms2.info("Get Religare Patient A " + common.getstring(policy) )
	  logger.loggerpms2.info("Get Religare Patient A ")
	  p = db((db.provider.id == providerid) & (db.provider.is_active == True)).select()
	  providercode = p[0].provider if(len(p)==1) else None
	  
	  regionid = int(common.getid(p[0].groupregion)) if(len(p)==1) else 1
	  r = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select()
	  regioncode = common.getstring(r[0].groupregion) if(len(r) == 1) else None	
	  
	  logger.loggerpms2.info("Get Religare Patient B ")

	  #logger.loggerpms2.info("Get Religare Patient B " + common.getstring(policy) + " " +common.getstring(providercode) + " "\
	                         #+ common.getstring(regioncode) + " " + common.getstring(companycode))

	  planprovdict = mdputils.getprocedurepriceplancode(db,policy, providercode, regioncode, companycode)
	  if(planprovdict["procedurepriceplancode"] == None):
	    patobj1 = {}
	    mssg = "Get Religare Patient  API:\n" + errormessage(db,"MDP101") + ")"
	    patobj1["result"] = "fail"
	    patobj1["error_code"] = "MDP101"
	    patobj1["error_message"] = mssg
	    logger.loggerpms2.info(mssg)
	    return json.dumps(patobj1) 	    
	  
	  
	  
	  planid = planprovdict["planid"] if(planprovdict["planid"] != None) else 1
	  plancode = planprovdict["plancode"] if(planprovdict["plancode"] != None) else ""
	  hmoplancode = plancode
	  procedurepriceplancode = planprovdict["procedurepriceplancode"] if(planprovdict["procedurepriceplancode"] != None) else ""

	  
	  #planprov = db((db.provider_region_plan.providercode == providercode) & (db.provider_region_plan.policy == policy) &\
	                #(db.provider_region_plan.companycode == companycode) & (db.provider_region_plan.regioncode == regioncode) &\
	                #(db.provider_region_plan.is_active == True)).select()
	  
	  
	  
	  #plancode = common.getstring(planprov[0].plancode) if(len(planprov) == 1) else None
	  #h = db(db.hmoplan.hmoplancode == plancode).select()
	  #planid = int(common.getid(h[0].id)) if(len(h) == 1) else 1
	  #hmoplancode = plancode
	
	
	#logger.loggerpms2.info("Get Religare Patient C" + plancode + " " + str(planid))
	logger.loggerpms2.info("Get Religare Patient C")
          
        sql = "UPDATE membercount SET membercount = membercount + 1 WHERE company = " + str(companyid) + ";"
        db.executesql(sql)
        db.commit()    
     
        xrows = db(db.membercount.company == companyid).select()
        membercount = int(xrows[0].membercount)
     
        patientmember = hmoplancode + str(membercount)    
      
        todaydt = common.getISTFormatCurrentLocatTime()
        todaydtnextyear = common.addyears(todaydt,1)
      
        name = customer_name.split(" ",1)
      
        if(len(name) >= 1 ):
          fname = name[0]
          
        if(len(name) >= 2 ):
          lname = name[1]  
        
        
	pats = db((db.patientmember.groupref==customer_id)|(db.patientmember.groupref == "ci_" + common.getstring(cell))).select(db.patientmember.address1,\
	                                                                                                       db.patientmember.address2,\
	                                                                                                       db.patientmember.address3,\
	                                                                                                       db.patientmember.city,\
	                                                                                                       db.patientmember.st,\
	                                                                                                       db.patientmember.pin,\
	                                                                                                       db.patientmember.groupregion,\
	                                                                                                       db.patientmember.cell,\
	                                                                                                       db.patientmember.email\
	                                                                                                       )
	
	#logger.loggerpms2.info("Get Religare Patient D" + str(len(pats)))
	logger.loggerpms2.info("Get Religare Patient D")
	p = db((db.provider.id == providerid) & (db.provider.is_active == True)).select()
        patid = db.patientmember.update_or_insert(((db.patientmember.groupref==customer_id)|(db.patientmember.groupref == "ci_" + common.getstring(cell))),
          patientmember = patientmember,
          groupref = "ci_" + common.getstring(cell) if((customer_id == "") | (customer_id == None)) else customer_id,
          fname = fname,
          lname = lname,
          address1 = pats[0].address1 if len(pats)>0 else (p[0].address1 if(len(p)>0) else "addr1"),
	  address2 = pats[0].address2 if len(pats)>0 else (p[0].address2 if(len(p)>0) else "addr2"),
	  address3 = pats[0].address3 if len(pats)>0 else (p[0].address3 if(len(p)>0) else "addr3"),
          city = pats[0].city if len(pats)>0 else (p[0].city  if(len(p)>0) else "city"),
          st = pats[0].st if len(pats)>0 else (p[0].st if(len(p)>0) else "st"),
          pin = pats[0].pin if len(pats)>0 else (p[0].pin if(len(p)>0) else "999999"),
          cell = cell if(len(cell)>0) else (pats[0].cell if len(pats)>0 else (p[0].cell if(len(p)>0) else "999999")),
	  email = pats[0].email if len(pats)>0 else (p[0].email if(len(p)>0) else "x@gmail.com"),
          dob = dob,
          gender = 'Female' if(gender == 'F') else "Male",
          status = 'Enrolled',
          groupregion = int(common.getid(pats[0].groupregion)) if len(pats)>0 else regionid,
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
        

	
        if(patid == None):
	  logger.loggerpms2.info("Get Religare Patient E Patiid = None")
          r = db(db.patientmember.groupref == customer_id).select(db.patientmember.id)
          if(len(r)==1):
	    
            patid = int(common.getid(r[0].id))
            opat = mdppatient.Patient(db, providerid)
            patobj = opat.getpatient(patid, patid, "")          
	    #logger.loggerpms2.info("Get Religare Patient F Patiid " + str(patid))
	    logger.loggerpms2.info("Get Religare Patient F")
	    
          else:    
	    logger.loggerpms2.info("Get Religare Patient G: " + errormessage(db,"MDP102"))
	    
            patobj=json.dumps({"result":"fail","error_message":errormessage(db,"MDP102")})
        else:
	  #logger.loggerpms2.info("Get Religare Patient H Patiid " + str(patid))
	  logger.loggerpms2.info("Get Religare Patient H")
	  
          opat = mdppatient.Patient(db, providerid)
          patobj = opat.getpatient(patid, patid, "")          
      else:
	logger.loggerpms2.info("Get Religare Patient I: " + errormessage(db,"MDP101"))
        patobj=json.dumps({"result":"fail","error_code":"MDP101","error_message":errormessage(db,"MDP101") })
          
    except Exception as e:
      patobj1 = {}
      mssg = "Get Religare Patient API exception:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")"
      patobj1["result"] = "fail"
      patobj1["error_code"] = "MDP100"
      patobj1["error_message"] = mssg
      logger.loggerpms2.info(mssg)
      return json.dumps(patobj1) 
    
    return patobj
 
  
 
  def updatereligarepatient(self,memberid,email,addr1,addr2,addr3,city,st,pin,cell):
    
     
    db = self.db
    providerid = self.providerid
    auth = current.auth
    
    try:
      memberid = int(memberid)
      
      db(db.patientmember.id == memberid).update(\
        email = email,
        address1 = addr1,
        address2 = addr2,
        address3 = addr3,
        city =city,
        st = st,
        pin = pin,
        cell=cell,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1 if(auth.user == None) else auth.user.id     
        
      )
      
      retobj = {"result":"success","error_message":""}
    except Exception as e:
      retobj = {"result":"fail","error_code":"MDP100","error_message":"Update Religare Patient API:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")"}
    
    return json.dumps(retobj) 

  
  #This method 
  #stringify json obj
  #encrypt stringified json obj
  #base64 encode
  #return {"req_data":<encoded encrypted json data}
  def encoderequestdata(self,jsondata):
    jsonstr = json.dumps(jsondata)
    jsonstrencrypt = self.encrypts(jsonstr)
    #jsonstrencoded = base64.b64encode(jsonstrencrypt)
    #jsonstrdecrypt = self.decrypts(jsonstrencrypt)
    reqobj = {"req_data":jsonstrencrypt}
    
    return reqobj  
  
  def decoderesponsedata(self,jsondatastr):
    #jsonstrdecoded = base64.b64decode(jsondatastr)
     
    jsonstrdecrypt = self.decrypts(jsondatastr)
    jsondata = json.loads(jsonstrdecrypt)
    return jsondata
    
  def encrypts128(self,raw):
        
        phpurl = "http://myphp128.com/encrypt.php"
        
        rlgrobj = {"raw":raw}
        
        resp = requests.post(phpurl,json=rlgrobj)
        
        jsonresp = {}
        if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
              respobj = resp.json()    
              jsonresp = {
                "encrypt": respobj["encrypt"]
               
              }
        else:
          jsonresp={"encrypt": "Response Error - " + str(resp.status_code)}
          
        return jsonresp["encrypt"]    
 
  def decrypts128(self,encrypt):    
    phpurl = "http://myphp128.com/decrypt.php"
    
    rlgrobj = {"encrypt":encrypt}
    
    resp = requests.post(phpurl,json=rlgrobj)
    
    jsonresp = {}
    if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
          respobj = resp.json()    
          jsonresp = {
            "raw": respobj["raw"]
          }
    else:
      jsonresp = {"raw":"Request Error - " + str(resp.status_code)}
      
    return jsonresp["raw"]
    

  def decrypts(self,encrypt):
    
    
    phpurl = "http://myphp.com/decrypt.php"
    
    rlgrobj = {"encrypt":encrypt}
    
    resp = requests.post(phpurl,json=rlgrobj)
    
    jsonresp = {}
    if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
          respobj = resp.json()    
          jsonresp = {
            "raw": respobj["raw"]
          }
    else:
      jsonresp = {"raw":"Request Error - " + str(resp.status_code)}
      
    return jsonresp["raw"]

  def decrypt(self,encrypt):
    
    phpurl = "http://myphp.com/decrypt.php"
    
    rlgrobj = {"encrypt":encrypt}
    
    resp = requests.post(phpurl,json=rlgrobj)
    
    jsonresp = {}
    if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
          respobj = resp.json()    
          jsonresp = {
            "raw": respobj["raw"]
          }
    return json.dumps(jsonresp)  

  def encrypt_login(self,action,providerid,username,password):
    
    request_data = {"action":action, "providerid":providerid,"username":username, "password":password}
    request_data_string = json.dumps(request_data)
    encrypt_string = self.encrypts(request_data_string)
    
    
    return encrypt_string
  
  def encrypts(self,raw):
      
      phpurl = "http://myphp.com/encrypt.php"
      
      rlgrobj = {"raw":raw}
      
      resp = requests.post(phpurl,json=rlgrobj)
      
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respobj = resp.json()    
            jsonresp = {
              "encrypt": respobj["encrypt"]
             
            }
      else:
        jsonresp={"encrypt": "Response Error - " + str(reps.status_code)}
        
      return jsonresp["encrypt"]

  def encrypt(self,raw):
    
    phpurl = "http://myphp.com/encrypt.php"
    
    rlgrobj = {"raw":raw}
    
    resp = requests.post(phpurl,json=rlgrobj)
    
    jsonresp = {}
    if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
          respobj = resp.json()    
          jsonresp = {
            "encrypt": respobj["encrypt"]
           
          }
    return json.dumps(jsonresp)
  
  #this api will call Religare API 1 - 
  #Rlgr URL : http://... API1
  #Request: policy, cell or custid, action
  #Response: Ack Id.
  #def xsendOTP(self,policy,cell,custid,action):
    
    #db = self.db
    #providerid = self.providerid
  
    #cell = common.modify_cell(cell)
    
    #prop = db(db.urlproperties.id>0).select(db.urlproperties.relgrprodurl,db.urlproperties.religare)
    #religare = common.getboolean(prop[0]["religare"])
    
    #jsonresp = {}
    #if(religare == True):
    
      #url = prop[0]["relgrprodurl"] if(len(prop) == 1) else URL("religare","religare")
    
      #religareobj = {"action":action,"policy":policy,"mobile":cell,"customerid":custid}
    
      #resp = requests.post(url,religareobj )
      
      #if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
        #respobj = resp.json()
        ##populate jsonresp as:
        #jsonresp = {
               #"result" : "success",
               #"ackid"  : "123",  #respobj["ackid"]
               #"action" : action,
               #"policy" : policy,
               #"cell"   : cell,
               #"customerid":custid,
               #"reason" : resp.status_code
               
             #}      
        
      #else:
        #jsonresp = {
               #"result" : "fail",
               #"ackid"  : "",
               #"action":action,
               #"policy" : policy,
               #"cell": cell,
               #"customerid":custid,
               #"reason":"SendOTP request failed ==>" + resp.status_code
             #}      
    
    
    #else:
      ##dummy response
      #jsonresp = {
        #"result" : "success",
        #"ackid"  : "000", 
        #"action" : action,
        #"policy" : policy,
        #"cell"   : cell,
        #"customerid":custid,
        #"reason" : resp.status_code        
      #}
    
    #return json.dumps(jsonresp)
  
  
  #def xvalidateOTP(self, ackid, otp):
      #db = self.db
      #providerid = self.providerid
    
      
      #prop = db(db.urlproperties.id>0).select(db.urlproperties.relgrprodurl,db.urlproperties.religare)
      #religare = common.getboolean(prop[0]["religare"])
      
      #jsonresp = {}
      #if(religare == True):

        #url = prop[0]["relgrprodurl"] if(len(prop) == 1) else URL("religare","religare")

        #religareobj = {"action":"validateOTP","ackid":ackid,"otp":otp}
        
        #resp = requests.post(url,religareobj )
        
        #if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
          #respobj = resp.json()

          ## based on provider, provider city
          
          #jsonresp = {}

        #else:
          #jsonresp = {
                 #"authentication" : "fail",
                 #"ackid" : ackid,
                 #"otp":otp,
                 #"reason":"Authentication failed. " + resp.status_code
               #}      
      
      
      #else:
        ##dummy response
        #jsonresp = {
          #"authentication" : "success",
          #"ackid": ackid,
          #"otp"  : otp,
          #"membername":"RELIGARECUST", 
          #"dob":"01/01/1960",
          #"gender":"M",
          #"description" : "Religare"          
        #}
      
      #return jsonresp    

  
  
  
    
  
  #API-1
  def sendOTP(self,policy_number,customer_id,voucher_code):
    
    self.policy = policy_number
    db = self.db
    providerid = self.providerid
    url = self.url + "getCustomerInfoForOpd.php"
    apikey = self.apikey
    jsonresp = {}

    try:
      jsonreqdata = {
        "apikey":apikey,
        "policy_number":policy_number,
        "customer_id":customer_id,
        "voucher_code":voucher_code
      }
      
      logger.loggerpms2.info(">>API-1 Send OTP Request\n")
      logger.loggerpms2.info("===Req_data=\n" + json.dumps(jsonreqdata) + "\n")
      
      
      jsonencodeddata = self.encoderequestdata(jsonreqdata)
      
      #logger.loggerpms2.info("===Encoded Req_data=\n" + json.dumps(jsonencodeddata) + "\n")      
      
      #call API-1
      resp = requests.post(url,data=jsonencodeddata)
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respstr =   resp.text
	    #logger.loggerpms2.info("===Encoded Resp_data=\n" + json.dumps(respstr) + "\n")      
            jsonresp = self.decoderesponsedata(respstr)
	    #logger.loggerpms2.info("===Resp_data=\n" + json.dumps(jsonresp) + "\n")      
	    mobile_number = jsonresp.get("mobile_number","0000000000")
            if(jsonresp["response_status"]==True):
              self.ackid = jsonresp["ackid"]
              jsonresp["result"] = "success"
              jsonresp["error_message"] = ""
              jsonresp["customer_id"] = "ci_" + voucher_code if(customer_id == "") else customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["voucher_code"] = voucher_code
	      jsonresp["mobile_number"] = mobile_number
            else:
              self.ackid = ''
              jsonresp["result"] = "fail"
              jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',"")) 
              jsonresp["customer_id"] = "ci_" + voucher_code if(customer_id == "") else customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["voucher_code"] = voucher_code 
	      jsonresp["mobile_number"] = mobile_number
            
      else:
        jsonresp={
          "result" : "fail",
          "error_message":"Send OTP API-1:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":"ci_" + voucher_code if(customer_id == "") else customer_id,
          "policy_number":policy_number,
          "voucher_code": voucher_code,
	  "mobile_number":""
        }

    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Send OTP API-1:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":"ci_" + voucher_code if(customer_id == "") else customer_id,
        "policy_number":policy_number,
        "voucher_code": voucher_code,
        "mobile_number":""
      }

    logger.loggerpms2.info(">>API-1 Send OTP Response\n")
    logger.loggerpms2.info("===Resp_data=\n" + json.dumps(jsonresp) + "\n")    
    return json.dumps(jsonresp)
  
  
  #API-1 - with mobile number
  def xsendOTP(self,policy_number,customer_id,mobile_number):
    
    db = self.db
    providerid = self.providerid
    url = self.url + "getCustomerInfoForOpd.php"
    apikey = self.apikey
    jsonresp = {}
    
    
    try:
      jsonreqdata = {
        "apikey":apikey,
        "policy_number":policy_number,
        "customer_id":customer_id,
        "mobile_number":mobile_number
        #"voucher_code":voucher_code
      
      }
      
      logger.loggerpms2.info(">>API-1 Send OTP Request\n")
      logger.loggerpms2.info("===Req_data=\n" + json.dumps(jsonreqdata) + "\n")
      
      
      jsonencodeddata = self.encoderequestdata(jsonreqdata)
      
      #call API-1
      resp = requests.post(url,data=jsonencodeddata)
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
	    respstr =   resp.text
	    jsonresp = self.decoderesponsedata(respstr)
	    
	    if(jsonresp["response_status"]==True):
	      self.ackid = jsonresp["ackid"]
	      jsonresp["result"] = "success"
	      jsonresp["error_message"] = ""
	      jsonresp["customer_id"] = "ci_" + mobile_number if(customer_id == "") else customer_id
	      jsonresp["policy_number"] = policy_number
	      jsonresp["mobile_number"] = mobile_number
	    else:
	      self.ackid = ''
	      jsonresp["result"] = "fail"
	      jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',"")) 
	      jsonresp["customer_id"] = "ci_" + mobile_number if(customer_id == "") else customer_id
	      jsonresp["policy_number"] = policy_number
	      jsonresp["mobile_number"] = mobile_number            
	    
      else:
	jsonresp={
          "result" : "fail",
          "error_message":"Send OTP API-1:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":"ci_" + mobile_number if(customer_id == "") else customer_id,
          "policy_number":policy_number,
          "mobile_number": mobile_number
        }

    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Send OTP API-1:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":"ci_" + mobile_number if(customer_id == "") else customer_id,
        "policy_number":policy_number,
        "mobile_number": mobile_number
      }

    logger.loggerpms2.info(">>API-1 Send OTP Response\n")
    logger.loggerpms2.info("===Resp_data=\n" + json.dumps(jsonresp) + "\n")    
    return json.dumps(jsonresp)

  
  #def X_validateOTP(self,ackid,otp,policy_number,customer_id,mobile_number):
    
    
    #jsonresp = {
        #"description": "",
        #"policy_number": "10271334",
        #"dob": "1982-09-12",
        #"response_status": True,
        #"mobile_number": "9137908350",
        #"response_message": "",
        #"gender": "M",
        #"membername": "IMTIYAZ BENGALI",
        #"customer_id": "50753136",
        #"error_code": ""
    #}    
    

    
    #return json.dumps(jsonresp)
  
  
  
  #API-2
  def validateOTP(self,ackid,otp,policy_number,customer_id,mobile_number):
    
    db = self.db
    providerid = self.providerid
    url = self.url + "validateOtpForOpd.php"
    apikey = self.apikey
    
    try:
      
      jsonreqdata = {
        "apikey":apikey,
        "ackid":ackid,
        "otp":otp
       
      
      }

      logger.loggerpms2.info(">>API-2 Validate OTP Request\n")
      logger.loggerpms2.info("===Req_data=\n" + json.dumps(jsonreqdata) + "\n")      

      jsonencodeddata = self.encoderequestdata(jsonreqdata)
   
       
      
      #call API-2
      #resp = requests.post(url,json=jsonencodeddata)
      resp = requests.post(url,data=jsonencodeddata)
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respstr =   resp.text
            jsonresp = self.decoderesponsedata(respstr)
            
            if(jsonresp["response_status"] == True):
              jsonresp["ackid"] = ackid
              jsonresp["dob"] = jsonresp["dob"] if((common.getstring(jsonresp["dob"]) != "") & (common.getstring(jsonresp["dob"]) != "--")) else "1990-01-01"
              jsonresp["gender"] = jsonresp["gender"] if(common.getstring(jsonresp["gender"]) != "") else "M"
              jsonresp["customer_id"] = customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number
              jsonresp["result"] = "success"
              jsonresp["error_message"] = ""
            else:
              jsonresp["result"] = "fail"
	      jsonresp["ackid"] = ackid
              jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',"")) 
              jsonresp["customer_id"] = customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number
      else:
        jsonresp={
          "result" : "fail",
          "error_message":"Validate OTP API-2:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":customer_id,
          "policy_number":policy_number,
          "mobile_number": mobile_number
        }
    
    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Validate OTP API-2:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":customer_id,
        "policy_number":policy_number,
        "mobile_number": mobile_number
      }
  
    logger.loggerpms2.info(">>API-2 Validate OTP Response\n")
    logger.loggerpms2.info("===Resp_data=\n" + json.dumps(jsonresp) + "\n")      
    return json.dumps(jsonresp)
  
  #API-3
  def uploadDocument(self,ackid,file_data,filename,policy_number,customer_id,mobile_number):
    
    db = self.db
    providerid = self.providerid
    apikey = self.apikey
    url = self.url + "uploadDocumentForOpd.php"

    ackservices =[]
    jsonresp = {}
    
    try:
      
      #jsonresp["response_status"] =  True
      #jsonresp["response_message"] =  ""
      #jsonresp["error_code"] =  ""
      #jsonresp["customer_id"] = customer_id
      #jsonresp["policy_number"] = policy_number
      #jsonresp["mobile_number"] = mobile_number 
      #jsonresp["result"] = "success"       
      #jsonresp["error_message"] = ""       
      
      #jsonresp["opd_service_details"] = [
        #{
          #"service_id" : "125",
          #"service_name" : "service id 125",
          #"service_category" : "dental"       
        #},
        #{
          #"service_id" : "201",
          #"service_name" : "service id 201",
          #"service_category" : "dental"       
        #},
        #{
          #"service_id" : "221",
          #"service_name" : "service id 221",
          #"service_category" : "dental"       
        #},
        #{
          #"service_id" : "222",
          #"service_name" : "service id 222",
          #"service_category" : "dental"       
        #},
        #{
          #"service_id" : "223",
          #"service_name" : "service id 223",
          #"service_category" : "dental"       
        #},
        #{
          #"service_id" : "224",
          #"service_name" : "service id 224",
          #"service_category" : "dental"       
        #}
      #]
      
      ##populate religare acknowledged services
      #ackservices = jsonresp["opd_service_details"]
      
      
      
      #for ackservice in ackservices:
        
        #db.rlgservices.update_or_insert(((db.rlgservices.ackid==ackid) & (db.rlgservices.service_id == ackservice["service_id"])),
                                         #ackid=ackid, 
                                         #service_id = ackservice["service_id"]
                                         #)
      
     
     #this has to be uncommmented once Religare is ready with new API3 on PROD 25/4/2019
      
      jsonreqdata = {
           "apikey":apikey,
           "ackid":ackid,
           "file_data":file_data,
           "filename":filename
          
         
         }  
      xjsonreqdata = {
           "apikey":apikey,
           "ackid":ackid,
           "filename":filename
         }  
      
      logger.loggerpms2.info(">>API-3 Upload Document Reuest\n")
      logger.loggerpms2.info("===Req_data=\n" + json.dumps(xjsonreqdata) + "\n")      
      
      #this has to be removed once Religare is ready with new API3 on PROD 25/4/2019
      
      #jsonreqdata = {
                 #"apikey":apikey,
                 #"ackid":ackid,
                 #"document":file_data
                
               
               #}       
      
      jsonencodeddata = self.encoderequestdata(jsonreqdata)
      #logger.loggerpms2.info("===Encoded Req_data=\n" + json.dumps(jsonencodeddata) + "\n")      
      
      
      
      resp = requests.post(url,data=jsonencodeddata)
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respstr =   resp.text
	    #logger.loggerpms2.info("===Encoded Resp_data=\n" + json.dumps(respstr) + "\n")      
            jsonresp = self.decoderesponsedata(respstr)
            #logger.loggerpms2.info("===Resp_data=\n" + json.dumps(jsonresp) + "\n")      
            if(jsonresp["response_status"] == True):
              jsonresp["customer_id"] = customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number 
              jsonresp["result"] = "success"       
              jsonresp["error_message"] = ""       
	      #jsonresp["opd_service_details"] = []
              #populate religare acknowledged services
              if(len(jsonresp["opd_service_details"])==0):
                jsonresp["result"] = "fail"
		jsonresp["error_code"] = "MDP103"
                jsonresp["error_message"] = "Upload Document API-3:\n" + errormessage(db,"MDP103") 
                jsonresp["customer_id"] = customer_id
                jsonresp["policy_number"] = policy_number
                jsonresp["mobile_number"] = mobile_number  
		
		
		#logger.loggerpms2.info(">>>Upload Document API-3:\n" + errormessage(db,"MDP103") )
		#logger.loggerpms2.info("===Req_data=\n" + json.dumps(jsonresp))                
                #hard coding the services in case of error
                #jsonresp["opd_service_details"] = [
                       #{
                         #"service_id" : "161",
                         #"service_name" : "Dental X-Ray",
                         #"service_category" : "Radiology"       
                       #},
                       #{
                         #"service_id" : "162",
                         #"service_name" : "Periodental",
                         #"service_category" : "Surgical Procedures"       
                       #},
                       #{
                         #"service_id" : "163",
                         #"service_name" : "Endodontic",
                         #"service_category" : "Surgical Procedures"       
                       #},
                       #{
                         #"service_id" : "88",
                         #"service_name" : "Dental Consultation",
                         #"service_category" : "Dental Consultation"       
                       #},
                       #{
                         #"service_id" : "164",
                         #"service_name" : "Extractions",
                         #"service_category" : "Surgical Procedures"       
                       #},
                       #{
                         #"service_id" : "165",
                         #"service_name" : "Conservative",
                         #"service_category" : "Surgical Procedures"       
                       #}
                     #]
              else:
                ackservices = jsonresp["opd_service_details"]
                for ackservice in ackservices:
                  db.rlgservices.update_or_insert(((db.rlgservices.ackid==ackid) & (db.rlgservices.service_id == ackservice["service_id"])),
                                                   ackid=ackid, 
                                                   service_id = ackservice["service_id"]
                                                   )
	
            else:
	

              jsonresp["result"] = "fail"
              jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',"")) 
              jsonresp["customer_id"] = customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number
              
      else:
        jsonresp={
	
          "result" : "fail",
          "error_message":"Upload Document API-3:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":customer_id,
          "policy_number":policy_number,
          "mobile_number": mobile_number
        }
    
    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Send OTP API-1:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":customer_id,
        "policy_number":policy_number,
        "mobile_number": mobile_number
      }
      
    logger.loggerpms2.info(">>API-3 Upload Document Response\n")
    logger.loggerpms2.info("===Resp_data=\n" + json.dumps(jsonresp) + "\n")      
      
    
    return json.dumps(jsonresp) 
  
  
  #def xaddProcedure(self,ackid,sub_service_id,treatment_code,treatment_name,swipe_value):
     
    #db = self.db
    #providerid = self.providerid
    #apikey = self.apikey
    #url = self.url + "getTransactionIdForOpd.php"
    
    #sub_service_id = ""
    #treatment_code = ""
    #treatment_name = ""
    #procedurecode = ""
    
    #jsonreqdata = {
         #"apikey":apikey,
         #"ackid":ackid,
         #"sub_service_id":sub_service_id,
         #"treatment_code":treatment_code,
         #"treatment_name":treatment_name,
         #"swipe_value":swipe_value
        
       
       #}    
    
    #jsonencodeddata = self.encoderequestdata(jsonreqdata)
    
    ##resp = requests.post(url,json=jsonencodeddata)
    #resp = requests.post(url,data=jsonencodeddata)
    #jsonresp = {}
    #if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
          #respstr =   resp.text
          #jsonresp = self.decoderesponsedata(respstr)
    #else:
      #jsonresp={
        #"response_status":False,
        #"response_message":"API Response Error",
        #"error_code":str(resp.status_code),
        #"ackid":""
      #}   
    
      
    #return json.dumps(jsonresp)   
    
  #this procedure 
 
  #API-4
  def geTransactionID(self,ackid,service_id,procedurecode, procedurename,procedurefee,\
                      procedurepiceplancode,policy_number,customer_id,mobile_number):
    
    logger.loggerpms2.info(">>Get Transaction ID API-4\n")
    db = self.db
    providerid = self.providerid
    auth = current.auth
    apikey = self.apikey
  
    url = self.url + "getTransactionIdForOpd.php"  
    
    try:
      jsonreqdata = {
           "apikey":apikey,
           "ackid":ackid,
           "sub_service_id":service_id,
           "treatment_code":procedurecode,
           "treatment_name":procedurecode,
           "swipe_value":str(procedurefee)
         }    
      
      jsonencodeddata = self.encoderequestdata(jsonreqdata)
      
      #resp = requests.post(url,json=jsonencodeddata)
      resp = requests.post(url,data=jsonencodeddata)      
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respstr =   resp.text
            jsonresp = self.decoderesponsedata(respstr)
            if(jsonresp["response_status"] == True):   
              jsonresp["procedurecode"] = procedurecode
              jsonresp["procedurename"] = procedurename
              jsonresp["procedurefee"] = procedurefee
              jsonresp["procedurepiceplancode"] = procedurepiceplancode
              jsonresp["result"] = "success"
              jsonresp["error_message"] = ""              
              jsonresp["customer_id"] = customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number  
            else:
              jsonresp["result"] = "fail"
              jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',"")) 
              jsonresp["customer_id"] = customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number
              
      else:
        jsonresp={
          "result" : "fail",
          "error_message":"Get Transaction ID API-4:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":customer_id,
          "policy_number":policy_number,
          "mobile_number": mobile_number
        }
    
        
    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Get Transaction ID API-4:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":customer_id,
        "policy_number":policy_number,
        "mobile_number": mobile_number
      }
    
    return json.dumps(jsonresp)
  
 

    
  #this procedure adds a new procedure to the treatment
  #API-5
  def addRlgProcedureToTreatment(self,ackid,otp,treatmentid,procedurepriceplancode, procedurecode, procedurename,procedurefee,\
                              tooth, quadrant,remarks,policy_number,customer_id,mobile_number):
    
    
    logger.loggerpms2.info(">>Add Rlg Procedure API-5 " + str(otp) + "\n")
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    apikey = self.apikey
  
    url = self.url + "doTransactionForOpd.php"  
    
    try:
      procs = db((db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode) & \
                 (db.vw_procedurepriceplan_relgr.procedurecode == procedurecode)).select()
      
      procedureid = 0
      ucrfee = 0
      procedurefee = 0
      copay = 0
      companypays = 0
      relgrproc = False
      memberid = 0
      
      service_id = ""
      service_name = ""
      service_category = ""
      
      if(len(procs)>0):
              ucrfee = float(common.getvalue(procs[0].ucrfee))
              procedurefee = float(common.getvalue(procs[0].relgrprocfee))
              if(procedurefee == 0):
                  procedurefee = ucrfee
              copay = float(common.getvalue(procs[0].relgrcopay))
              inspays = float(common.getvalue(procs[0].relgrinspays))
              companypays = float(common.getvalue(procs[0].companypays))
              procedureid = int(common.getid(procs[0].id))    
              relgrproc = bool(common.getboolean(procs[0].relgrproc))
              service_id = int(common.getid(procs[0].service_id))
              service_name = procs[0].service_name
              service_category = procs[0].service_category
              
                
      sub_service_id = ""
      treatment_code = ""
      treatment_name = ""
      procedurecode = ""
      
      jsonreqdata = {
           "apikey":apikey,
           "ackid":ackid,
           "otp":otp
         }    
      
      jsonencodeddata = self.encoderequestdata(jsonreqdata)
      
      #resp = requests.post(url,json=jsonencodeddata)
      resp = requests.post(url,data=jsonencodeddata)      
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respstr =   resp.text
            jsonresp = self.decoderesponsedata(respstr)
            
            if(jsonresp["response_status"] == True):
              if(common.getstring(jsonresp["transaction_status"])=='SUCCESS' ):
                inspays = float(common.getvalue(jsonresp["transaction_amount"]))
                copay = float(common.getvalue(jsonresp["copay"]))
                transaction_id = common.getstring(jsonresp["transaction_id"])
                t = db(db.vw_treatmentlist.id == treatmentid).\
                  select(db.vw_treatmentlist.tplanid,db.vw_treatmentlist.startdate, db.vw_treatmentlist.memberid)
              
                procid = db.treatment_procedure.insert(treatmentid = treatmentid, dentalprocedure = procedureid,status="Started",\
                                                       treatmentdate=t[0].startdate if(len(t)>0) else common.getISTFormatCurrentLocatTime(),\
                                                     ucr = ucrfee, procedurefee=procedurefee, copay=copay,inspays=inspays,companypays=companypays,\
                                                     tooth=tooth,quadrant=quadrant,remarks=remarks,authorized=False,service_id = service_id,\
                                                     relgrproc=relgrproc,relgrtransactionid = transaction_id,relgrtransactionamt=inspays) 
          
                
                tplanid = int(common.getid(t[0].tplanid)) if(len(t) > 0) else 0
                memberid = int(common.getid(t[0].memberid)) if(len(t) > 0) else 0
                #update treatment with new treatment cost
                account.updatetreatmentcostandcopay(db,auth.user,treatmentid)
                #update tplan with new treatment cost
                account.calculatecost(db,tplanid)
                account.calculatecopay(db, tplanid,memberid)
                account.calculateinspays(db,tplanid)
                account.calculatedue(db,tplanid)  
                jsonresp["treatmentprocid"] = procid
                jsonresp["ackid"]=ackid
                jsonresp["result"] =  "success"
                jsonresp["error_message"] = ""
              else:
                jsonresp["ackid"]=ackid
                jsonresp["result"] = "fail"
		jsonresp["error_code"] = "MDP027"
                jsonresp["error_message"] = errormessage(db,"MDP027")
            else:
              jsonresp["result"] = "fail"
              jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',"")) 
            
            jsonresp["customer_id"] = customer_id
            jsonresp["policy_number"] = policy_number
            jsonresp["mobile_number"] = mobile_number      
            
      else:
        jsonresp={
          "result" : "fail",
          "error_message":"Do OPD Transaction API-5:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":customer_id,
          "policy_number":policy_number,
          "mobile_number": mobile_number
        }
    
      

    except Exception as e:
      mssg = "OPD Transaction API-5 Exception error:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")"
      logger.loggerpms2.info(mssg)
      jsonresp = {
        "result":"fail",
        "error_message":mssg,
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":customer_id,
        "policy_number":policy_number,
        "mobile_number": mobile_number
      }

    return json.dumps(jsonresp)
  
  
  
  def getreligareprocedures(self,ackid,procedurepriceplancode,searchphrase="",page=0,maxcount=0):
    
    #logger.loggerpms2.info("Enter Get Religare Procedures \n"  + str(ackid) + " " + procedurepriceplancode + " " + searchphrase + " " + str(page) + " " + str(maxcount))    
    
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
        query = (db.rlgservices.ackid ==ackid) & (db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode)&\
                (db.vw_procedurepriceplan_relgr.is_active == True) & (db.vw_procedurepriceplan_relgr.relgrproc ==True)        
      else:
        query = (db.rlgservices.ackid ==ackid) & (db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode)&\
                (db.vw_procedurepriceplan_relgr.shortdescription.like('%' + searchphrase + '%'))&\
                (db.vw_procedurepriceplan_relgr.is_active == True) & (db.vw_procedurepriceplan_relgr.relgrproc ==True)        
        
      #logger.loggerpms2.info("Get Religare Patient " + str(query))
      
      if(page >=0 ): 
        procs = db(query).select(\
                       db.vw_procedurepriceplan_relgr.ALL, db.rlgservices.ALL, \
                       left=[db.vw_procedurepriceplan_relgr.on(db.vw_procedurepriceplan_relgr.service_id == db.rlgservices.service_id)],\
                       orderby=db.vw_procedurepriceplan_relgr.procedurecode,\
	               limitby=limitby\
                      )
	#logger.loggerpms2.info("Get Religare Patient Procs" +str(len(procs)))
        if(maxcount == 0):
          
          procs1 = db(query).select(\
                 db.vw_procedurepriceplan_relgr.ALL, db.rlgservices.ALL, \
                 left=[db.vw_procedurepriceplan_relgr.on(db.vw_procedurepriceplan_relgr.service_id == db.rlgservices.service_id)]\
                )    
          maxcount = len(procs1)
      else:
        procs = db(query).select(\
                       db.vw_procedurepriceplan_relgr.ALL, db.rlgservices.ALL, \
	               orderby=db.vw_procedurepriceplan_relgr.procedurecode,\
                       left=[db.vw_procedurepriceplan_relgr.on(db.vw_procedurepriceplan_relgr.service_id == db.rlgservices.service_id)]\
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
      error_message = "Get Religare Procedure API:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
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

  #def xgetreligareprocedures(self,ackid,procedurepriceplancode,page=0,maxcount=0):
    
    #db = self.db
    #providerid = self.providerid
    
    
    #page = page -1
    #items_per_page = 4
    #limitby = ((page)*items_per_page,(page+1)*items_per_page)      
    #proclist = []
    #procobj = {}
    #result = "success"
    #error_message = ""
    #try:
      #if(page >=0 ):    
        #procs = db((db.rlgservices.ackid ==ackid) & (db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode)&\
                      #(db.vw_procedurepriceplan.is_active == True) & (db.vw_procedurepriceplan.relgrproc ==True)).select(\
                       #db.vw_procedurepriceplan.ALL, db.rlgservices.ALL, \
                       #left=[db.vw_procedurepriceplan.on(db.vw_procedurepriceplan.service_id == db.rlgservices.service_id)],limitby=limitby\
                      #)
        #if(maxcount == 0):
          
          #procs1 = db((db.rlgservices.ackid ==ackid) & (db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode)&\
                #(db.vw_procedurepriceplan.is_active == True) & (db.vw_procedurepriceplan.relgrproc ==True)).select(\
                 #db.vw_procedurepriceplan.ALL, db.rlgservices.ALL, \
                 #left=[db.vw_procedurepriceplan.on(db.vw_procedurepriceplan.service_id == db.rlgservices.service_id)]\
                #)    
          #maxcount = len(procs1)
      #else:
        #procs = db((db.rlgservices.ackid ==ackid) & (db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode)&\
                      #(db.vw_procedurepriceplan.is_active == True) & (db.vw_procedurepriceplan.relgrproc ==True)).select(\
                       #db.vw_procedurepriceplan.ALL, db.rlgservices.ALL, \
                       #left=[db.vw_procedurepriceplan.on(db.vw_procedurepriceplan.service_id == db.rlgservices.service_id)]\
                      #)
        #if(maxcount == 0):
          #maxcount = len(procs)
        
        
     
      
      #for proc in procs:
        #procobj = {
            #"plan":procedurepriceplancode,
            #"procedurecode":proc.vw_procedurepriceplan.procedurecode,
            #"altshortdescription":common.getstring(proc.vw_procedurepriceplan.altshortdescription),
            #"procedurefee":float(common.getvalue(proc.vw_procedurepriceplan.procedurefee)),
            #"inspays":float(common.getvalue(proc.vw_procedurepriceplan.inspays)),
            #"copay":float(common.getvalue(proc.vw_procedurepriceplan.copay)),
            #"service_id":common.getstring(proc.vw_procedurepriceplan.service_id),
            #"service_name":common.getstring(proc.vw_procedurepriceplan.service_name),
            #"service_category":common.getstring(proc.vw_procedurepriceplan.service_category)
        #}        
        #proclist.append(procobj) 
        #result = 'success'
        #error_message = ""
        
    #except Exception as e:
      #result = "fail"
      #error_message = "Exception Error getreligareprocedures API " + e.message,
      
    #xcount = ((page+1) * items_per_page) - (items_per_page - len(procs)) 
            
    #bnext = True
    #bprev = True
      
    ##first page
    #if((page+1) == 1):
        #bnext = True
        #bprev = False
      
    ##last page
    #if(len(procs) < items_per_page):
        #bnext = False
        #bprev = True  
          
    #return json.dumps({"result":result,"error_message":error_message,"count":len(procs),"page":page+1,"proclist":proclist,"runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev})
  
  
  
  #API-6 
  def settleTransaction(self, treatmentid,treatmentprocid):
    

    db = self.db
    providerid = self.providerid
    url = self.url + "settledOpdTransaction.php"
    apikey = self.apikey
    
    
    try:
      xid = db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.id == treatmentprocid)).select()
      relgrproc = False
      transaction_id = ""
      if(len(xid)==1):
        transaction_id = common.getstring(xid[0].relgrtransactionid)
        relgrproc = common.getboolean(xid[0].relgrproc)
      
      trlist = []
      trlist.append(transaction_id)
      
      jsonreqdata = {
           "apikey":apikey,
           "transaction_id":trlist
         }    
        
      logger.loggerpms2.info(">>API-6 Settle Transaction\n")
      logger.loggerpms2.info("===Req_data=\n" + json.dumps(jsonreqdata) + "\n")        
      
      jsonencodeddata = self.encoderequestdata(jsonreqdata)
      
      resp = requests.post(url,data=jsonencodeddata)
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respstr =   resp.text
            jsonresp = self.decoderesponsedata(respstr)
	    logger.loggerpms2.info(">>API-6 Settle Transaction Response\n")
	    logger.loggerpms2.info("===Resp_data=\n" + json.dumps(jsonresp) + "\n")   	    
	    
            if(jsonresp["response_status"] == True):
              j1 = jsonresp["transaction_status"][0]
              j2 = j1[transaction_id]
              
              if(j2 == "SUCCESS"):
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
                db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.id == treatmentprocid)).update(status = 'Completed')              
		db(db.treatment.id == treatmentid).update(status = 'Completed')
		
              else:
                jsonresp["result"] = "fail"
		jsonresp["error_code"] = "MDP028"
                jsonresp["error_message"] = errormessage(db,"MDP028")
		
              
            else:
              jsonresp["result"] = "fail"
              jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',""))
              
      else:
        jsonresp={
          "result" : "fail",
          "error_message":"Transaction Settlement API-6:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
        }
      
    
    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Transaction Settlement API-6:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
      }
          

    logger.loggerpms2.info(">>API-6 Settle Transaction Response Exit\n")
    logger.loggerpms2.info("===Exit Resp_data=\n" + json.dumps(jsonresp) + "\n")   	    
    
          
    return json.dumps(jsonresp)
    
  
  #API-7
  def voidTransaction(self,treatmentid,treatmentprocid):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    apikey = self.apikey
  
    url = self.url + "voidOpdTransaction.php" 
    
    try:
      xid = db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.id == treatmentprocid)).select()
      relgrproc = False
      transaction_id = ""
      if(len(xid)==1):
        transaction_id = common.getstring(xid[0].relgrtransactionid)
        relgrproc = common.getboolean(xid[0].relgrproc)
        
      if(relgrproc == True)  :
        jsonreqdata = {
               "apikey":apikey,
               "transaction_id":transaction_id
        }
	
	logger.loggerpms2.info(">>API-7 Void Transaction\n")
	logger.loggerpms2.info("===Req_data=\n" + json.dumps(jsonreqdata) + "\n")        
	
        jsonencodeddata = self.encoderequestdata(jsonreqdata)
      
      
        #resp = requests.post(url,json=jsonencodeddata)
        resp = requests.post(url,data=jsonencodeddata)      
        jsonresp = {}
        if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
              respstr =   resp.text
              jsonresp = self.decoderesponsedata(respstr) 
              if(jsonresp["response_status"] == True):
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
                db((db.treatment_procedure.relgrtransactionid == transaction_id) & \
                   (db.treatment_procedure.relgrproc == True)).update(\
                     is_active = False,
                     status = 'Cancelled',
                )
		db(db.treatment.id == treatmentid).update(status = 'Cancelled',is_active=False)
                account.updatetreatmentcostandcopay(db,None,treatmentid)
              else:
                jsonresp["result"] = "fail"
                jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',"")) 
                
        else:
          
          jsonresp={
            "result" : "fail",
            "error_message":"Void Transaction API-7:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
            "response_status":"",
            "response_message":"",
            "error_code":"MDP099",
          }
      else:
        jsonresp={
          "result" : "fail",
          "error_message":errormessage(db,"MDP029") ,
          "response_status":"",
          "response_message":"",
          "error_code":"MDP029",
        }
    
      
    except Exception as e:
      
      jsonresp = {
        "result":"fail",
        "error_message":"Void Transaction API-7:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
      }
      
    logger.loggerpms2.info(">>API-7 Void Transaction Response Exit\n")
    logger.loggerpms2.info("===Exit Resp_data=\n" + json.dumps(jsonresp) + "\n")      
          
    return json.dumps(jsonresp)
  
#====================  XXX Off-line API =======================================================================================
class Religare399:
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    self.ackid = ""
    self.policy_name = ""
    self.customer_type = ""
    self.rlgencrypt = RlgEncryption()
    return 
      
  # this API emulates sendOTP & validate OTP APIs of Religare class
  def validaterlgmember399(self,plan_code,policy,voucher_code,promocode=None):
    
    self.policy = policy
    db = self.db

    
    providerid = self.providerid

    rlgobj = Religare(db, providerid)
    
    if(promocode == None):
      promocode = "fP8dW8"

    try:
      ackid = common.generateackid("RLG", 10)
      
      db.sessionlog.insert(\
	        ackid = ackid,
	        promocode = promocode,
	        created_on = common.getISTFormatCurrentLocatTime(),
	        created_by = 1 ,
	        modified_on = common.getISTFormatCurrentLocatTime(),
	        modified_by = 1     
	      )      
      
      r = db((db.rlgvoucher.plancode==plan_code) &\
             (db.rlgvoucher.policy==policy) &\
             (db.rlgvoucher.vouchercode==voucher_code) &\
             (db.rlgvoucher.is_active==True)).select()
      
      if(len(r) == 1):
	#success
	cell = "0000000000" if(common.getstring(r[0].cell) == "") else r[0].cell
	gender = "F" if(common.getstring(r[0].gender) == "") else r[0].gender
	x = common.getnulldt(r[0].dob)
	dob = "1990-01-01" if(x == "") else datetime.datetime.strftime("%Y-%m-%d", r[0].dob)
	
	
	customer_id = "ci_" + voucher_code
	customer_name = r[0].fname + "" if(common.getstring(r[0].lname) == "") else (" " + common.getstring(r[0].lname))
	jsonresp = {}
	
	
	jsonresp["result"] = "success"
	jsonresp["error_message"] = ""
	jsonresp["ackid"] = ackid
	jsonresp["plan_code"] = plan_code
	jsonresp["voucher_code"] = voucher_code
	jsonresp["policy"] = policy
	jsonresp["customer_id"] = customer_id
	jsonresp["mobile_number"] = cell
	jsonresp["dob"] = dob
	jsonresp["gender"] = "Female" if gender == "F" else "Male"
	jsonresp["fname"] = common.getstring(r[0].fname)
	jsonresp["mname"] = common.getstring(r[0].mname)
	jsonresp["lname"] = common.getstring(r[0].lname)
	
	db.rlgservices.insert(ackid=ackid, service_id = "399")
	
      else:
	#invalid member
	jsonresp={
                  "result" : "fail",
	          "ackid":ackid,
	          "plan_code":plan_code,
	          "voucher_code":voucher_code,
	          "policy":policy,
                  "error_message":errormessage(db,"MDP102") ,
                  "response_status":"",
                  "response_message":"",
                  "error_code":"MDP102",
                }
	
      
    
    except Exception as e:
      
      jsonresp = {
             "result":"fail",
             "error_message":"Error Validating 399 member API:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
             "ackid":ackid,
             "plan_code":plan_code,
             "voucher_code":voucher_code,
             "policy":policy,
             "response_status":"",
             "response_message":"",
             "error_code":"MDP100",
           }      
    
    return json.dumps(jsonresp)  


  
  def getreligarepatient399(self, avars ):
    
    
    db = self.db
    providerid = self.providerid
    rlgobj = Religare(db, providerid)
    ackid = avars["ackid"] if "ackid" in avars else "ackid_399" 
    
    try:
      r = db(db.sessionlog.ackid == ackid).count()
      if(r != 1):
	jsonresp={
	          "result" : "fail",
	          "ackid":ackid,
	          "error_message":errormessage(db,"ERR002") ,
	          "response_status":"",
	          "response_message":"",
	          "error_code":"ERR002",
	        }
	return json.dumps(jsonresp)
      
      policy = avars["policy"] if "policy" in avars else "Policy399O"
      plancode = avars["plan_code"] if "plan_code" in avars else "Policy399O"
      voucher_code = avars["voucher_code"] if "voucher_code" in avars else "voucher_399"
      customer_id = avars["customer_id"] if "customer_id" in avars else "ci_" + voucher_code
      fname = avars["fname"] if "fname" in avars else "FN_399"
      mname = avars["mname"] if "mname" in avars else "MN_399"
      lname = avars["lname"] if "lname" in avars else "LN_399"
      
      customer_name =  fname 
      customer_name = customer_name if(lname == "") else customer_name + " " + lname
      
      mobile_number = avars["mobile_number"] if "mobile_number" in avars else "0000000000"
      gender = avars["gender"] if "gender" in avars else "F"
      dob = avars["dob"] if "dob" in avars else "1990-01-01"


       
      jsonresp = json.loads(rlgobj.getreligarepatient(customer_id, customer_name, mobile_number, dob, gender,policy))
      jsonresp["ackid"] = ackid
      
      
      
    except Exception as e:
      jsonresp = {
             "result":"fail",
             "error_message":"Error Getting  399 member API:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
             "ackid":ackid,
             "response_status":"",
             "response_message":"",
             "error_code":"MDP100",
           }      
      
      
    
    
    return json.dumps(jsonresp)
  
  def updatereligarepatient399(self, avars ):
      
      db = self.db
      providerid = self.providerid
      auth = current.auth
      rlgobj = Religare(db, providerid)
      
      ackid = avars["ackid"] if "ackid" in avars else "ackid_399"
      
      try:
	
	r = db(db.sessionlog.ackid == ackid).count()
	if(r != 1):
	  jsonresp={
	            "result" : "fail",
	            "ackid":ackid,
	            "error_message":errormessage(db,"ERR002") ,
	            "response_status":"",
	            "response_message":"",
	            "error_code":"ERR002",
	          }
	  return json.dumps(jsonresp)	
	memberid = int(common.getid(avars["memberid"])) if "memberid" in avars else 0
	email = avars["email"] if "email" in avars else "mydentalplan.in@gmail.com"
	addr1 = avars["address1"] if "address1" in avars else "addr1"
	addr2 = avars["address2"] if "address2" in avars else "addr2"
	addr3 = avars["address3"] if "address3" in avars else "addr3"
	city = avars["city"] if "city" in avars else "Bengaluru"
	st = avars["st"] if "st" in avars else "Karnatak (KA)"
	pin = avars["pin"] if "pin" in avars else "560092"
	cell = avars["cell"] if "cell" in avars else "0000000000"
	dob = avars["dob"] if "dob" in avars else "01/01/1990"
	gender = avars["gender"] if "gender" in avars else "Female"
	
	db(db.patientmember.id == memberid).update(\
	  email = email,
	  address1 = addr1,
	  address2 = addr2,
	  address3 = addr3,
	  city =city,
	  st = st,
	  pin = pin,
	  cell=cell,
	  gender = gender,
	  dob = datetime.datetime.strptime(dob, "%d/%m/%Y"),
	  modified_on = common.getISTFormatCurrentLocatTime(),
	  modified_by = 1 if(auth.user == None) else auth.user.id     
	  
	)
	
	jsonresp = {"result":"success","error_message":""}	

	jsonresp["ackid"] = ackid
	
      
	
	
      except Exception as e:
	jsonresp = {
	       "result":"fail",
	       "error_message":"Error Getting  399 member API:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
	       "ackid":ackid,
	       "response_status":"",
	       "response_message":"",
	       "error_code":"MDP100",
	     }      
	
	
      
      
      return json.dumps(jsonresp)  
    
    
    
    
  def getreligareprocedures399(self,avars):
  
      logger.loggerpms2.info("Enter Get Religare Procedures \n"  + str(avars))
    
      db = self.db
      providerid = self.providerid
      rlgobj = Religare(db, providerid)
      ackid = avars["ackid"] if "ackid" in avars else "ackid_399"      
      
      try:
	r = db(db.sessionlog.ackid == ackid).count()
	if(r != 1):
	  jsonresp={
	            "result" : "fail",
	            "ackid":ackid,
	            "error_message":errormessage(db,"ERR002") ,
	            "response_status":"",
	            "response_message":"",
	            "error_code":"ERR002",
	          }
	  return json.dumps(jsonresp)
	
	procedurepriceplancode = avars["procedurepriceplancode"] if "procedurepriceplancode" in avars else "XXX"
	
	searchphrase = avars["searchphrase"] if "searchphrase" in avars else ""
	page = int(common.getid(avars["page"])) if "page" in avars else 0
	maxcount = int(common.getid(avars["maxcount"])) if "maxcount" in avars else 0


	
	jsonresp = json.loads(rlgobj.getreligareprocedures(ackid, 
	                                                  procedurepriceplancode, 
	                                                  searchphrase, 
	                                                  page, 
	                                                  maxcount))
	
      except Exception as e:
	jsonresp = {
		       "result":"fail",
		       "error_message":"Error Get Religare   399 Procedures API:\n" + errormessage("MDP100")  + "\n(" + str(e) + ")",
	               "ackid":ackid,
		       "response_status":"",
		       "response_message":"",
		       "error_code":"MDP100",
		     }      
	

          
      return json.dumps(jsonresp)
    

    
  def addRlgProcedureToTreatment399(self,avars):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    rlgobj = Religare(db, providerid)
    ackid = avars["ackid"] if "ackid" in avars else "ackid_399"    
    jsonresp={}
    
    try:
      r = db(db.sessionlog.ackid == ackid).count()
      if(r != 1):
	jsonresp={
                  "result" : "fail",
                  "ackid":ackid,
                  "error_message":errormessage("ERR002") ,
                  "response_status":"",
                  "response_message":"",
                  "error_code":"ERR002",
                }
	return json.dumps(jsonresp)      
      
      treatmentid = int(common.getid(avars["treatmentid"])) if "treatmentid" in avars else 0
      procedurepriceplancode = avars["plancode"] if "plancode" in avars else "RLG101"
      procedurecode = avars["procedurecode"] if "procedurecode" in avars else "G0104"
      procedurename = avars["procedurename"] if "procedurename" in avars else "Dental consultations - Emergency Palliative Treatment of Dental pain and minor procedures- ONLY"
      procedurefee = float(common.getvalue(avars["procedurefee"])) if "procedurefee" in avars else "0.00"
      tooth = avars["tooth"] if "tooth" in avars else "1"
      quadrant = avars["quadrant"] if "quadrant" in avars else "Q1"
      remarks = avars["remarks"] if "remarks" in avars else "remarks"
      policy_number = avars["policy_number"] if "policy_number" in avars else "0000000000"
      customer_id = avars["customer_id"] if "customer_id" in avars else "ci_399"
      mobile_number = avars["mobile_number"] if "mobile_number" in avars else "0000000000"
	    
      
      procs = db((db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode) & \
                 (db.vw_procedurepriceplan_relgr.procedurecode == procedurecode)).select()
	
      procedureid = 0
      ucrfee = 0
      procedurefee = 0
      copay = 0
      companypays = 0
      relgrproc = False
      memberid = 0
      
      service_id = ""
      service_name = ""
      service_category = ""
      
      if(len(procs)>0):
	ucrfee = float(common.getvalue(procs[0].ucrfee))
	procedurefee = float(common.getvalue(procs[0].relgrprocfee))
	if(procedurefee == 0):
	    procedurefee = ucrfee
	copay = float(common.getvalue(procs[0].relgrcopay))
	inspays = float(common.getvalue(procs[0].relgrinspays))
	companypays = float(common.getvalue(procs[0].companypays))
	procedureid = int(common.getid(procs[0].id))    
	relgrproc = bool(common.getboolean(procs[0].relgrproc))
	service_id = int(common.getid(procs[0].service_id))
	service_name = procs[0].service_name
	service_category = procs[0].service_category
  
        transaction_id = "RLG399_"
	random.seed(int(time.time()))
	for j in range(0,7):
	    transaction_id += str(random.randint(0,9))      

      
	t = db(db.vw_treatmentlist.id == treatmentid).\
          select(db.vw_treatmentlist.tplanid,db.vw_treatmentlist.startdate, db.vw_treatmentlist.memberid)
    
	procid = db.treatment_procedure.insert(treatmentid = treatmentid, dentalprocedure = procedureid,status="Started",\
                                             treatmentdate=t[0].startdate if(len(t)>0) else common.getISTFormatCurrentLocatTime(),\
	                                     ucr = ucrfee, procedurefee=procedurefee, copay=copay,inspays=inspays,companypays=companypays,\
	                                     tooth=tooth,quadrant=quadrant,remarks=remarks,authorized=False,service_id = service_id,\
	                                     relgrproc=relgrproc,relgrtransactionid = transaction_id,relgrtransactionamt=inspays) 

		
	tplanid = int(common.getid(t[0].tplanid)) if(len(t) > 0) else 0
	memberid = int(common.getid(t[0].memberid)) if(len(t) > 0) else 0
	#update treatment with new treatment cost
	account.updatetreatmentcostandcopay(db,auth.user,treatmentid)
	#update tplan with new treatment cost
	account.calculatecost(db,tplanid)
	account.calculatecopay(db, tplanid,memberid)
	account.calculateinspays(db,tplanid)
	account.calculatedue(db,tplanid)  
	jsonresp["treatmentprocid"] = procid
	jsonresp["result"] =  "success"
	jsonresp["error_message"] = ""
	jsonresp["customer_id"] = customer_id
	jsonresp["policy_number"] = policy_number
	jsonresp["mobile_number"] = mobile_number      
	jsonresp["ackid"] = ackid      
      
      else:
	jsonresp={
          "result" : "fail",
          "error_message":"Error adding procedure to Religare Treatment 399",
	  "ackid":ackid,
          "response_status":"",
          "response_message":"",
          "customer_id":customer_id,
          "policy_number":policy_number,
          "mobile_number": mobile_number
        }
    
      
    except Exception as e:
      jsonresp = {
	             "result":"fail",
	             "error_message":"Error addRlgProcedureToTreatment399 API Exception:\n" + errormessage("MDP100")  + "\n(" + str(e) + ")",
                     "ackid":ackid,
	             "response_status":"",
	             "response_message":"",
	             "error_code":"MDP100",
	           }      
      
	
    return json.dumps(jsonresp)
  
  
  
  


#====================  XXX API =======================================================================================
class ReligareXXX:
  def __init__(self,db,providerid,policy_name="Policy399"):
    self.db = db
    self.providerid = providerid

    props = db(db.rlgproperties.policy_name == policy_name).select()
    
    self.url = "" if(len(props)==0) else props[0].url
    self.apikey = "" if(len(props)==0) else props[0].api_key
    self.ackid = ""
    self.policy_name = policy_name
    self.customer_type = ""
    self.rlgencrypt = RlgEncryption()
    
    

    return 
  
 

  #API-1
  def sendOTP(self,policy_number,customer_id,voucher_code,policy_name=""):
    
    self.policy = policy_number
    db = self.db
    providerid = self.providerid
    url = self.url + "getCustomerInfoForOpdMDP.php"
    apikey = self.apikey
    
    mobile_number = "0000000000"
    
    jsonresp = {}
    
    
    try:
      jsonreqdata = {
        "apikey":apikey,
        "policy_number":policy_number,
        "customer_id":customer_id,
        "voucher_code":voucher_code
      }
      
      logger.loggerpms2.info(">>XXX:API-1 Send OTP Request")
      logger.loggerpms2.info("===XXX:Req_data=\n" + json.dumps(jsonreqdata) + "\n")
      
      jsonencodeddata =  self.rlgencrypt.encoderequestdata(jsonreqdata)	  #self.encoderequestdata(jsonreqdata)
      
      #logger.loggerpms2.info("===XXX:Encoded Req_data=\n" + json.dumps(jsonencodeddata) + "\n")      
      
      #call API-1
      resp = requests.post(url,data=jsonencodeddata)
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
	    respstr =   resp.text
	    #logger.loggerpms2.info("XXX:===Encoded Resp_data=\n" + json.dumps(respstr) + "\n")      
	    jsonresp = self.rlgencrypt.decoderesponsedata(respstr)   #self.decoderesponsedata(respstr)
	    #logger.loggerpms2.info("XXX:===Resp_data=\n" + json.dumps(jsonresp) + "\n")      
	    mobile_number = jsonresp.get("mobile_number","0000000000")
	    if(jsonresp["response_status"]==True):
	      self.ackid = jsonresp.get("ackid","")
	      jsonresp["customer_type"] = "corporate" if(self.ackid.startswith("C_")) else\
	        ("retail" if(self.ackid.startswith("R_")) else "")
	      self.customer_type = jsonresp["customer_type"]
	      jsonresp["result"] = "success"
	      jsonresp["error_message"] = ""
	      
	      jsonresp["customer_id"] = "ci_" +  (uuid.uuid1()).hex if(customer_id == "") else customer_id
	      jsonresp["policy_number"] = policy_number
	      jsonresp["voucher_code"] = voucher_code
	      jsonresp["mobile_number"] = mobile_number
	      jsonresp["policy_name"] = jsonresp.get("policy_name",policy_name)
	      
	      
	      
	    else:
	      
	      self.ackid = ''
	      jsonresp["result"] = "fail"
	      jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',"")) 
	      jsonresp["customer_id"] = "ci_" + voucher_code if(customer_id == "") else customer_id
	      jsonresp["policy_number"] = policy_number
	      jsonresp["voucher_code"] = voucher_code 
	      jsonresp["mobile_number"] = mobile_number
	      jsonresp["policy_name"] = jsonresp.get("policy_name",policy_name)
	    
      else:
	jsonresp={
          "result" : "fail",
          "error_message":"Send OTPXXX API-1:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":"ci_" + voucher_code if(customer_id == "") else customer_id,
          "policy_number":policy_number,
          "voucher_code": voucher_code,
          "mobile_number":mobile_number,
	  "policy_name": policy_name
        }

    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Send OTPXXX API-1:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":"ci_" + voucher_code if(customer_id == "") else customer_id,
        "policy_number":policy_number,
        "voucher_code": voucher_code,
        "mobile_number":mobile_number,
        "policy_name": policy_name
        
      }

    logger.loggerpms2.info(">>XXX:API-1 Send OTP Response")
    logger.loggerpms2.info("===XXX:Resp_data=\n" + json.dumps(jsonresp) + "\n")    
    return json.dumps(jsonresp)  

  #API-2
  def validateOTP(self,ackid,otp,policy_number,customer_id,voucher_code, mobile_number,policy_name=""):
    
    db = self.db
    providerid = self.providerid
    url = self.url + "validateOtpForOpdMDP.php"
    apikey = self.apikey
    customer_type = self.customer_type
    auth = current.auth
    primary_customer_id = customer_id
    
    try:
      
      jsonreqdata = {
        "apikey":apikey,
        "ackid":ackid,
        "otp":otp
       
      
      }

      logger.loggerpms2.info(">>XXX:API-2 Validate OTP Request\n")
      logger.loggerpms2.info("===XXX:Req_data=\n" + json.dumps(jsonreqdata) + "\n")      

      jsonencodeddata = self.rlgencrypt.encoderequestdata(jsonreqdata)  #self.encoderequestdata(jsonreqdata)
   
       
      
      #call API-2
     
      resp = requests.post(url,data=jsonencodeddata)
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
	    respstr =   resp.text
	    #logger.loggerpms2.info("XXX:===Encoded Resp_data=\n" + json.dumps(respstr) + "\n")      
	    jsonresp = self.rlgencrypt.decoderesponsedata(respstr)  #self.decoderesponsedata(respstr)
	    #logger.loggerpms2.info("XXX:===Resp_data=\n" + json.dumps(jsonresp) + "\n")    
	    if(jsonresp["response_status"] == True):
	      #add relationship field in members
	      memcount = 1
	      member_details = getvalue(jsonresp,"member_detials",None)
	      if(member_details != None):
		for member in member_details:
		  if(memcount == 1):
		    memcount = memcount + 1
		    member["relationship"] = "Self"
		    customer_id = getvalue(member,"customerid",customer_id)
		    primary_customer_id = customer_id
		  else:
		    memcount = memcount + 1
		    member["relationship"] = "Dependant"	      
		
	      jsonresp["ackid"] = ackid
	      jsonresp["customer_id"] = customer_id
	      jsonresp["primary_customer_id"] = primary_customer_id
	      jsonresp["voucher_code"] = voucher_code
	      jsonresp["policy_number"] = policy_number
	      jsonresp["mobile_number"] = mobile_number
	      policy_name = getvalue(jsonresp, "Product Name", policy_name)
	      policy_name = "Policy399" if((policy_name == None) | (policy_name == "")) else policy_name
	      
	      jsonresp["policy_name"] = policy_name
	      
	      
	      jsonresp["result"] = "success"
	      jsonresp["error_message"] = ""
	      
	      
	      #insert/update records in provider_region_plan for this new policy number
	      #if(policy_name != "Policy399"):
		#rows = db(db.provider_region_plan.policy == "Policy399").select()
		#for r in rows:
		  
		  #patid = db.provider_region_plan.update_or_insert(((db.provider_region_plan.policy==policy_name) &\
		                                                    #(db.provider_region_plan.regioncode==r.regioncode)&\
		                                                    #(db.provider_region_plan.is_active==True)),
		    #providercode = r.providercode,
		    #companycode = r.companycode,
		    #regioncode = r.regioncode,
		    #policy = policy_name,
		    #plancode = r.plancode,
		    #procedurepriceplancode = r.procedurepriceplancode,
		    #is_active = True,
		    #created_on = common.getISTFormatCurrentLocatTime(),
		    #created_by = 1 if(auth.user == None) else auth.user.id,
		    #modified_on = common.getISTFormatCurrentLocatTime(),
		    #modified_by = 1 if(auth.user == None) else auth.user.id    
		  
		  #)
		  #db.commit()
	      
	      
	    else:
	      jsonresp["result"] = "fail"
	      jsonresp["ackid"] = ackid
	      jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',"")) 
	      jsonresp["customer_id"] = customer_id
	      jsonresp["primary_customer_id"] = primary_customer_id
	      jsonresp["voucher_code"] = voucher_code
	      jsonresp["policy_number"] = policy_number
	      jsonresp["mobile_number"] = mobile_number
	      jsonresp["policy_name"] = policy_name
	      
      else:
	jsonresp={
          "result" : "fail",
          "error_message":"Validate OTP API-2:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":customer_id,
	  "primary_customer_id":primary_customer_id,
	  "voucher_code":voucher_code,
          "policy_number":policy_number,
          "mobile_number": mobile_number,
	  "policy_name":policy_name
        }
    
    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Validate OTP API-2:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":customer_id,
        "primary_customer_id":primary_customer_id,
        "voucher_code":voucher_code,
        "policy_number":policy_number,
        "mobile_number": mobile_number,
        "policy_name":policy_name
        
      }
  
    logger.loggerpms2.info(">>XXX:API-2 Validate OTP Response")
    logger.loggerpms2.info("===XXX:Resp_data=\n" + json.dumps(jsonresp) + "\n")      
    return json.dumps(jsonresp)
  
  #API-3
  def uploadDocument(self,ackid,file_data,filename,policy_number,primary_customer_id,customer_id,voucher_code,mobile_number,policy_name=""):
    
    db = self.db
    providerid = self.providerid
    apikey = self.apikey
    url = self.url + "uploadDocumentForOpdMDP.php"

    ackservices =[]
    jsonresp = {}
    
    try:
      jsonreqdata = {
           "apikey":apikey,
           "ackid":ackid,
           "file_data":file_data,
           "filename":filename,
           "customer_id":primary_customer_id
          
         
         }  
      xjsonreqdata = {
           "apikey":apikey,
           "ackid":ackid,
           "filename":filename,
           "customer_id":primary_customer_id 
         }  
      
      logger.loggerpms2.info(">>API-3 Upload Document Reuest")
      logger.loggerpms2.info("===Req_data=\n" + json.dumps(xjsonreqdata) + "\n")      
      
    
      jsonencodeddata = self.rlgencrypt.encoderequestdata(jsonreqdata)  #self.encoderequestdata(jsonreqdata)
          
      
      
      
      resp = requests.post(url,data=jsonencodeddata)
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respstr =   resp.text
	    #logger.loggerpms2.info("===Encoded Resp_data=\n" + json.dumps(respstr) + "\n")      
            jsonresp = self.rlgencrypt.decoderesponsedata(respstr) #self.decoderesponsedata(respstr)
            #logger.loggerpms2.info("===Resp_data=\n" + json.dumps(jsonresp) + "\n")      
            if(jsonresp["response_status"] == True):
              jsonresp["customer_id"] = customer_id
	      jsonresp["primary_customer_id"] = primary_customer_id
	      jsonresp["voucher_code"] = voucher_code
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number 
	      jsonresp["policy_name"] = policy_name 
              jsonresp["result"] = "success"       
              jsonresp["error_message"] = ""       
	      #jsonresp["opd_service_details"] = []
              #populate religare acknowledged services
              if(len(jsonresp["opd_service_details"])==0):
                jsonresp["result"] = "fail"
		jsonresp["error_code"] = "MDP103"
                jsonresp["error_message"] = "Error:Upload Document API-3:\n" + errormessage(db,"MDP103") 
		jsonresp["voucher_code"] = voucher_code
                jsonresp["customer_id"] = customer_id
		jsonresp["primary_customer_id"] = primary_customer_id
                jsonresp["policy_number"] = policy_number
                jsonresp["mobile_number"] = mobile_number  
		jsonresp["policy_name"] = policy_name 
		
		
		#logger.loggerpms2.info(">>>Upload Document API-3:\n" + errormessage(db,"MDP103") )
		#logger.loggerpms2.info("===Resp_data=\n" + json.dumps(jsonresp))                
              else:
                ackservices = jsonresp["opd_service_details"]
                for ackservice in ackservices:
                  db.rlgservices.update_or_insert(((db.rlgservices.ackid==ackid) & (db.rlgservices.service_id == ackservice["service_id"])),
                                                   ackid=ackid, 
                                                   service_id = ackservice["service_id"]
                                                   )
	
            else:
	

              jsonresp["result"] = "fail"
              jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',"")) 
              jsonresp["customer_id"] = customer_id
	      jsonresp["primary_customer_id"] = primary_customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number
	      jsonresp["policy_name"] = policy_name 
	      jsonresp["voucher_code"] = voucher_code
	      
              
      else:
        jsonresp={
	
          "result" : "fail",
          "error_message":"Upload Document API-3:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":customer_id,
	  "primary_customer_id":primary_customer_id,
	  "voucher_code":voucher_code,
          "policy_number":policy_number,
          "mobile_number": mobile_number,
	  "policy_name": policy_name
        }
    
    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Send OTP API-1:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":customer_id,
        "primary_customer_id":primary_customer_id,
        "voucher_code":voucher_code,
        "policy_number":policy_number,
        "mobile_number": mobile_number,
        "policy_name": policy_name
        
      }
      
    logger.loggerpms2.info(">>API-3 Upload Document Response")
    logger.loggerpms2.info("===Resp_data=\n" + json.dumps(jsonresp) + "\n")      
      
    
    return json.dumps(jsonresp) 
 
  #this will create a new religare patient if not in db else return the current religare pateint.
  #member_details is a list of members. 
  def getreligarepatient(self,avars):

    logger.loggerpms2.info("XXX:Enter Get Religare Patient ")
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    
    member_details = avars["member_detials"]
    policy_name = avars["policy_name"]
    
    patobj = []
    fname = ""
    lname = ""
    
    companycode = 'RLG'
    companyid = 0
    
    providercode = None
    
    regioncode = None
    regionid = 0
    
    plancode = None
    planid = 0
    memberid = 0
    depid = 0
    try:
      
      for member in member_details:
	if(getvalue(member,"relationship","Self") == "Self"):
	  #primary member
	  customer_name = "RLG_" + getvalue(member,"customerid","")  if(getvalue(member,"membername","") == "") else getvalue(member,"membername","")
	  dob = "1990-01-01" if(getvalue(member,"dob","1990-01-01") == None) else (getvalue(member,"dob","1990-01-01") if(getvalue(member,"dob","") != "") else "1990-01-01")
	  d=dob.split('-')  #dob is in YYYY-m-d format
	  dob = datetime.datetime.strptime(d[2] + "/" + d[1] + "/" + d[0], "%d/%m/%Y")
	  
	  patientmember = "RLGDEL0001"   #default religare member in DEL region
	  
	  companycode = 'RLG'
	  c = db(db.company.company == companycode).select()
	  companyid = int(common.getid(c[0].id)) if(len(c) > 0) else 0	  

	  logger.loggerpms2.info("Get Religare Patient A " + common.getstring(policy_name) )
	  
	  #provider code
	  p = db((db.provider.id == providerid) & (db.provider.is_active == True)).select()
	  providercode = p[0].provider if(len(p)==1) else None	  
	  
          # provider region
	  regionid = int(common.getid(p[0].groupregion)) if(len(p)==1) else 1
	  r = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select()
	  regioncode = common.getstring(r[0].groupregion) if(len(r) == 1) else None		  
	  
	  logger.loggerpms2.info("Get Religare Patient B " + common.getstring(policy_name) + " " +common.getstring(providercode) + " "\
				 + common.getstring(regioncode) + " " + common.getstring(companycode))
	  
	  planprovdict = mdputils.getprocedurepriceplancode(db,policy_name, providercode, regioncode, companycode)
	  
	  if(planprovdict["procedurepriceplancode"] == None):
	    patobj1 = {}
	    mssg = "Get Religare Patient  API:\n" + errormessage(db,"MDP101") + ")"
	    patobj1["result"] = "fail"
	    patobj1["error_code"] = "MDP101"
	    patobj1["error_message"] = mssg
	    logger.loggerpms2.info(mssg)
	    return json.dumps(patobj1)
	  
	  planid = planprovdict["planid"] if(planprovdict["planid"] != None) else 1
	  plancode = planprovdict["plancode"] if(planprovdict["plancode"] != None) else ""
	  hmoplancode = plancode
	  procedurepriceplancode = planprovdict["procedurepriceplancode"] if(planprovdict["procedurepriceplancode"] != None) else ""

	  logger.loggerpms2.info("Get Religare Patient C" + plancode + " " + str(planid))
	  
	    
	  sql = "UPDATE membercount SET membercount = membercount + 1 WHERE company = " + str(companyid) + ";"
	  db.executesql(sql)
	  db.commit()    
       
	  xrows = db(db.membercount.company == companyid).select()
	  membercount = int(xrows[0].membercount)
       
	  patientmember = hmoplancode + str(membercount)    
	
	  todaydt = common.getISTFormatCurrentLocatTime()
	  todaydtnextyear = common.addyears(todaydt,1)
	
	  name = customer_name.split(" ",1)
	
	  if(len(name) >= 1 ):
	    fname = name[0]
	    
	  if(len(name) >= 2 ):
	    lname = name[1]  

	  pats = db(db.patientmember.groupref==getvalue(member,"customerid","")).select(db.patientmember.address1,\
	                                                                db.patientmember.address2,\
	                                                                db.patientmember.address3,\
	                                                                db.patientmember.city,\
	                                                                db.patientmember.st,\
	                                                                db.patientmember.pin,\
	                                                                db.patientmember.groupregion,\
	                                                                db.patientmember.cell,\
	                                                                db.patientmember.email\
	                                                                )
	  
	  #logger.loggerpms2.info("Get Religare Patient D" + str(len(pats)))
	  logger.loggerpms2.info("Get Religare Patient D")
	  p = db((db.provider.id == providerid) & (db.provider.is_active == True)).select()
	  memberid = db.patientmember.update_or_insert((db.patientmember.groupref==getvalue(member,"customerid","")),
	    patientmember = patientmember,
	    groupref = patientmember if((getvalue(member,"customerid","") == "") | (getvalue(member,"customerid","") == None)) else getvalue(member,"customerid",""),
	    fname = fname,
	    lname = lname,
	    address1 = pats[0].address1 if len(pats)>0 else (p[0].address1 if(len(p)>0) else "addr1"),
	    address2 = pats[0].address2 if len(pats)>0 else (p[0].address2 if(len(p)>0) else "addr2"),
	    address3 = pats[0].address3 if len(pats)>0 else (p[0].address3 if(len(p)>0) else "addr3"),
	    city = pats[0].city if len(pats)>0 else (p[0].city  if(len(p)>0) else "city"),
	    st = pats[0].st if len(pats)>0 else (p[0].st if(len(p)>0) else "st"),
	    pin = pats[0].pin if len(pats)>0 else (p[0].pin if(len(p)>0) else "999999"),
	    cell = pats[0].cell if len(pats)>0 else (p[0].cell if(len(p)>0) else "999999"),
	    email = pats[0].email if len(pats)>0 else (p[0].email if(len(p)>0) else "x@gmail.com"),
	    dob = dob,
	    gender = 'Female' if(getvalue(member,"gender","M") == 'F') else "Male",
	    status = 'Enrolled',
	    groupregion = int(common.getid(pats[0].groupregion)) if len(pats)>0 else regionid,
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
	  if(memberid == None):
	    logger.loggerpms2.info("Get Religare Patient E memberid = None")
	    r = db(db.patientmember.groupref == getvalue(member,"customerid","")).select(db.patientmember.id)
	    if(len(r)==1):
	      
	      memberid = int(common.getid(r[0].id))
	      opat = mdppatient.Patient(db, providerid)
	      patobj = opat.getpatient(memberid, memberid, "")          
	      #logger.loggerpms2.info("Get Religare Patient F Patiid " + str(patid))
	      #logger.loggerpms2.info("Get Religare Patient F\n")
	      #logger.loggerpms2.info(json.dumps(patobj))
	      
	    else:    
	      logger.loggerpms2.info("Get Religare Patient G: " + errormessage(db,"MDP102"))
	      patobj=json.dumps({"result":"fail","error_message":errormessage(db,"MDP102")})
	      return patobj
	    
	  
	   

		   
	elif(getvalue(member,"relationship","Dependant") == "Dependant"):
	  #dependant member
	  customer_name = "RLG_" + getvalue(member,"customerid","")  if(getvalue(member,"membername","") == "") else getvalue(member,"membername","")
	  dob = "1990-01-01" if(getvalue(member,"dob","1990-01-01") == None) else (getvalue(member,"dob","1990-01-01") if(getvalue(member,"dob","") != "") else "1990-01-01")
	  d=dob.split('-')  #dob is in YYYY-m-d format
	  dob = datetime.datetime.strptime(d[2] + "/" + d[1] + "/" + d[0], "%d/%m/%Y")
	     
	  name = customer_name.split(" ",1)
	
	  fname = name[0] if(len(name) >= 1 ) else ""
	  lname = name[1] if(len(name) >= 2 ) else ""
        
          gender = 'Female' if(getvalue(member,"gender","M") == 'F') else "Male",
	  
	  relationship = getvalue(member,"relationship","Dependant")
	  
	  customer_id = getvalue(member,"customerid","")
	  
	  depid = db.patientmemberdependants.update_or_insert((db.patientmemberdependants.title==customer_id),
	                                                      title = customer_id,
	                                                      fname = fname,
	                                                      lname = lname,
	                                                      depdob = dob,
	                                                      relation = relationship,
	                                                      gender = gender,
	                                                      patientmember = memberid,
	                                                      is_active = True,
	                                                      paid = True,
	                                                      newmember = True,
	                                                      freetreatment  = False,
	                                                      created_on = common.getISTFormatCurrentLocatTime(),
	                                                      created_by = 1 if(auth.user == None) else auth.user.id,
	                                                      modified_on = common.getISTFormatCurrentLocatTime(),
	                                                      modified_by = 1 if(auth.user == None) else auth.user.id
	                                                      )
	  db.commit()
	  
	  if(depid == None):
	    
	    #logger.loggerpms2.info("Get Religare Patient I depid = None")
	    r = db(db.patientmemberdependants.title == getvalue(member,"customerid","")).select(db.patientmemberdependants.id)
	    if(len(r)==1):
	      depid = int(common.getid(r[0].id))
	      #logger.loggerpms2.info("Get Religare Patient J DepID = " + str(depid))
	    else:    
	      logger.loggerpms2.info("Get Religare Patient K: " + errormessage(db,"MDP102"))
	      patobj=json.dumps({"result":"fail","error_message":errormessage(db,"MDP102")})
	      return patobj	  

	
      opat = mdppatient.Patient(db, providerid)
      patobj = opat.getpatient(memberid, depid, "") 	  	
      logger.loggerpms2.info("Get Religare Patient L" + str(memberid) + " " + str(depid) + "\n")
      logger.loggerpms2.info(json.dumps(patobj))
      
      
      
    except Exception as e:
      patobj1 = {}
      mssg = "Get Religare Patient API exception:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")"
      patobj1["result"] = "fail"
      patobj1["error_code"] = "MDP100"
      patobj1["error_message"] = mssg
      logger.loggerpms2.info(mssg)
      return json.dumps(patobj1) 
    
    return patobj    
  
  def updatereligarepatient(self,memberid,email,addr1,addr2,addr3,city,st,pin,cell):
    
     
    db = self.db
    providerid = self.providerid
    auth = current.auth
    
    try:
      memberid = int(memberid)
      
      db(db.patientmember.id == memberid).update(\
        email = email,
        address1 = addr1,
        address2 = addr2,
        address3 = addr3,
        city =city,
        st = st,
        pin = pin,
        cell=cell,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1 if(auth.user == None) else auth.user.id     
        
      )
      
      retobj = {"result":"success","error_message":""}
    except Exception as e:
      retobj = {"result":"fail","error_code":"MDP100","error_message":"Update Religare Patient API:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")"}
    
    return json.dumps(retobj) 
  
  def getreligareprocedures(self,ackid,procedurepriceplancode,searchphrase="",page=0,maxcount=0):
    
    logger.loggerpms2.info("XXX:Enter Get Religare Procedures \n"  + str(ackid) + " " + procedurepriceplancode + " " + searchphrase + " " + str(page) + " " + str(maxcount))    
    
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
        query = (db.rlgservices.ackid ==ackid) & (db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode)&\
                (db.vw_procedurepriceplan_relgr.is_active == True) & (db.vw_procedurepriceplan_relgr.relgrproc ==True)        
      else:
        query = (db.rlgservices.ackid ==ackid) & (db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode)&\
                (db.vw_procedurepriceplan_relgr.shortdescription.like('%' + searchphrase + '%'))&\
                (db.vw_procedurepriceplan_relgr.is_active == True) & (db.vw_procedurepriceplan_relgr.relgrproc ==True)        
        
      #logger.loggerpms2.info("Get Religare Patient " + str(query))
      
      if(page >=0 ): 
        procs = db(query).select(\
                       db.vw_procedurepriceplan_relgr.ALL, db.rlgservices.ALL, \
                       left=[db.vw_procedurepriceplan_relgr.on(db.vw_procedurepriceplan_relgr.service_id == db.rlgservices.service_id)],\
                       orderby=db.vw_procedurepriceplan_relgr.procedurecode,\
	               limitby=limitby\
                      )
	#logger.loggerpms2.info("Get Religare Patient Procs" +str(len(procs)))
        if(maxcount == 0):
          
          procs1 = db(query).select(\
                 db.vw_procedurepriceplan_relgr.ALL, db.rlgservices.ALL, \
                 left=[db.vw_procedurepriceplan_relgr.on(db.vw_procedurepriceplan_relgr.service_id == db.rlgservices.service_id)]\
                )    
          maxcount = len(procs1)
      else:
        procs = db(query).select(\
                       db.vw_procedurepriceplan_relgr.ALL, db.rlgservices.ALL, \
	               orderby=db.vw_procedurepriceplan_relgr.procedurecode,\
                       left=[db.vw_procedurepriceplan_relgr.on(db.vw_procedurepriceplan_relgr.service_id == db.rlgservices.service_id)]\
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
      error_message = "Get Religare Procedure API:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
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
  
  
  #API-4
  def geTransactionID(self,ackid,service_id,procedurecode, procedurename,procedurefee,\
                      procedurepiceplancode,policy_number,customer_id,mobile_number,voucher_code,policy_name):
    
    logger.loggerpms2.info(">>XXX:Get Transaction ID API-4\n")
    db = self.db
    providerid = self.providerid
    auth = current.auth
    apikey = self.apikey
  
    url = self.url + "getTransactionIdForOpd.php"  
    try:
      jsonreqdata = {
           "apikey":apikey,
           "ackid":ackid,
           "sub_service_id":service_id,
           "treatment_code":procedurecode,
           "treatment_name":procedurecode,
           "swipe_value":str(procedurefee)
         }    
      
      jsonencodeddata = self.rlgencrypt.encoderequestdata(jsonreqdata)
      
      #resp = requests.post(url,json=jsonencodeddata)
      resp = requests.post(url,data=jsonencodeddata)      
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
	    respstr =   resp.text
	    jsonresp = self.rlgencrypt.decoderesponsedata(respstr)
	    if(jsonresp["response_status"] == True):   
	      jsonresp["procedurecode"] = procedurecode
	      jsonresp["procedurename"] = procedurename
	      jsonresp["procedurefee"] = procedurefee
	      jsonresp["procedurepiceplancode"] = procedurepiceplancode
	      jsonresp["result"] = "success"
	      jsonresp["error_message"] = ""              
	      jsonresp["customer_id"] = customer_id
	      jsonresp["policy_number"] = policy_number
	      jsonresp["policy_name"] = policy_name  
	      jsonresp["voucher_code"] = voucher_code  
	      jsonresp["mobile_number"] = mobile_number  
	      
	    else:
	      jsonresp["result"] = "fail"
	      jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',"")) 
	      jsonresp["customer_id"] = customer_id
	      jsonresp["policy_number"] = policy_number
	      jsonresp["mobile_number"] = mobile_number
	      jsonresp["policy_name"] = policy_name  
	      jsonresp["voucher_code"] = voucher_code  
	      
	      
      else:
	jsonresp={
          "result" : "fail",
          "error_message":"Get Transaction ID API-4:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":customer_id,
          "policy_number":policy_number,
	  "policy_name":policy_name,
	  "voucher_code":voucher_code,
          "mobile_number": mobile_number
        }
    
	
    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Get Transaction ID API-4:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":customer_id,
        "policy_number":policy_number,
        "policy_name":policy_name,
        "voucher_code":voucher_code,
        "mobile_number": mobile_number
      }
    
    return json.dumps(jsonresp) 

  #this procedure adds a new procedure to the treatment
  #API-5
  def addRlgProcedureToTreatment(self,ackid,otp,treatmentid,procedurepriceplancode, procedurecode, procedurename,procedurefee,\
                              tooth, quadrant,remarks,policy_number,customer_id,mobile_number,voucher_code,policy_name):
    
    
    
    logger.loggerpms2.info(">>XXX:Add Rlg Procedure API-5 " + str(otp) + "\n")
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    apikey = self.apikey
  
    url = self.url + "doTransactionForOpd.php"  
    
    try:
      procs = db((db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode) & \
                 (db.vw_procedurepriceplan_relgr.procedurecode == procedurecode)).select()
      
      procedureid = 0
      ucrfee = 0
      procedurefee = 0
      copay = 0
      companypays = 0
      relgrproc = False
      memberid = 0
      
      service_id = ""
      service_name = ""
      service_category = ""
      
      if(len(procs)>0):
	      ucrfee = float(common.getvalue(procs[0].ucrfee))
	      procedurefee = float(common.getvalue(procs[0].relgrprocfee))
	      if(procedurefee == 0):
		  procedurefee = ucrfee
	      copay = float(common.getvalue(procs[0].relgrcopay))
	      inspays = float(common.getvalue(procs[0].relgrinspays))
	      companypays = float(common.getvalue(procs[0].companypays))
	      procedureid = int(common.getid(procs[0].id))    
	      relgrproc = bool(common.getboolean(procs[0].relgrproc))
	      service_id = int(common.getid(procs[0].service_id))
	      service_name = procs[0].service_name
	      service_category = procs[0].service_category
	      
		
      sub_service_id = ""
      treatment_code = ""
      treatment_name = ""
      procedurecode = ""
      
      jsonreqdata = {
           "apikey":apikey,
           "ackid":ackid,
           "otp":otp
         }    
      
      jsonencodeddata = self.rlgencrypt.encoderequestdata(jsonreqdata)
      
      #resp = requests.post(url,json=jsonencodeddata)
      resp = requests.post(url,data=jsonencodeddata)      
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
	    respstr =   resp.text
	    jsonresp = self.rlgencrypt.decoderesponsedata(respstr)
	    
	    if(jsonresp["response_status"] == True):
	      if(common.getstring(jsonresp["transaction_status"])=='SUCCESS' ):
		inspays = float(common.getvalue(jsonresp["transaction_amount"]))
		copay = float(common.getvalue(jsonresp["copay"]))
		transaction_id = common.getstring(jsonresp["transaction_id"])
		t = db(db.vw_treatmentlist.id == treatmentid).\
	          select(db.vw_treatmentlist.tplanid,db.vw_treatmentlist.startdate, db.vw_treatmentlist.memberid)
	      
		procid = db.treatment_procedure.insert(treatmentid = treatmentid, dentalprocedure = procedureid,status="Started",\
	                                               treatmentdate=t[0].startdate if(len(t)>0) else common.getISTFormatCurrentLocatTime(),\
	                                             ucr = ucrfee, procedurefee=procedurefee, copay=copay,inspays=inspays,companypays=companypays,\
	                                             tooth=tooth,quadrant=quadrant,remarks=remarks,authorized=False,service_id = service_id,policy_name=policy_name,\
	                                             relgrproc=relgrproc,relgrtransactionid = transaction_id,relgrtransactionamt=inspays) 
	  
		
		tplanid = int(common.getid(t[0].tplanid)) if(len(t) > 0) else 0
		memberid = int(common.getid(t[0].memberid)) if(len(t) > 0) else 0
		#update treatment with new treatment cost
		account.updatetreatmentcostandcopay(db,auth.user,treatmentid)
		#update tplan with new treatment cost
		account.calculatecost(db,tplanid)
		account.calculatecopay(db, tplanid,memberid)
		account.calculateinspays(db,tplanid)
		account.calculatedue(db,tplanid)  
		jsonresp["treatmentprocid"] = procid
		jsonresp["ackid"]=ackid
		jsonresp["result"] =  "success"
		jsonresp["error_message"] = ""
			
		
	      else:
		jsonresp["ackid"]=ackid
		jsonresp["result"] = "fail"
		jsonresp["error_code"] = "MDP027"
		jsonresp["error_message"] = errormessage(db,"MDP027")
		 		
	    else:
	      jsonresp["result"] = "fail"
	      jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',"")) 
	    
	      jsonresp["customer_id"] = customer_id
	      jsonresp["policy_number"] = policy_number
	      jsonresp["mobile_number"] = mobile_number
	      jsonresp["policy_name"] = policy_name  
	      jsonresp["voucher_code"] = voucher_code  	    
      else:
	jsonresp={
          "result" : "fail",
          "error_message":"Do OPD Transaction API-5:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":customer_id,
          "policy_number":policy_number,
	  "policy_name":policy_name,
	  "voucher_code":voucher_code,
          "mobile_number": mobile_number
        }
    
      

    except Exception as e:
      mssg = "OPD Transaction API-5 Exception error:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")"
      logger.loggerpms2.info(mssg)
      jsonresp = {
        "result":"fail",
        "error_message":mssg,
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":customer_id,
        "policy_number":policy_number,
        "policy_name":policy_name,
        "voucher_code":voucher_code,
        "mobile_number": mobile_number
      }

    return json.dumps(jsonresp)
  
  
  #API-6 
  def settleTransaction(self, treatmentid,treatmentprocid):
    

    db = self.db
    providerid = self.providerid
    url = self.url + "settledOpdTransaction.php"
    apikey = self.apikey
    
    
    try:
      xid = db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.id == treatmentprocid)).select()
      relgrproc = False
      transaction_id = ""
      if(len(xid)==1):
	transaction_id = common.getstring(xid[0].relgrtransactionid)
	relgrproc = common.getboolean(xid[0].relgrproc)
      
      trlist = []
      trlist.append(transaction_id)
      
      jsonreqdata = {
           "apikey":apikey,
           "transaction_id":trlist
         }    
	
      logger.loggerpms2.info(">>API-6 Settle Transaction\n")
      logger.loggerpms2.info("===Req_data=\n" + json.dumps(jsonreqdata) + "\n")        
      
      jsonencodeddata = self.encoderequestdata(jsonreqdata)
      
      resp = requests.post(url,data=jsonencodeddata)
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
	    respstr =   resp.text
	    jsonresp = self.decoderesponsedata(respstr)
	    logger.loggerpms2.info(">>API-6 Settle Transaction Response\n")
	    logger.loggerpms2.info("===Resp_data=\n" + json.dumps(jsonresp) + "\n")   	    
	    
	    if(jsonresp["response_status"] == True):
	      j1 = jsonresp["transaction_status"][0]
	      j2 = j1[transaction_id]
	      
	      if(j2 == "SUCCESS"):
		jsonresp["result"] = "success"
		jsonresp["error_message"] = ""
		db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.id == treatmentprocid)).update(status = 'Completed')              
		db(db.treatment.id == treatmentid).update(status = 'Completed')
		
	      else:
		jsonresp["result"] = "fail"
		jsonresp["error_code"] = "MDP028"
		jsonresp["error_message"] = errormessage(db,"MDP028")
		
	      
	    else:
	      jsonresp["result"] = "fail"
	      jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',""))
	      
      else:
	jsonresp={
          "result" : "fail",
          "error_message":"Transaction Settlement API-6:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
        }
      
    
    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Transaction Settlement API-6:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
      }
	  

    logger.loggerpms2.info(">>API-6 Settle Transaction Response Exit\n")
    logger.loggerpms2.info("===Exit Resp_data=\n" + json.dumps(jsonresp) + "\n")   	    
    
	  
    return json.dumps(jsonresp)
    
  
  #API-7
  def voidTransaction(self,treatmentid,treatmentprocid):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    apikey = self.apikey
  
    url = self.url + "voidOpdTransaction.php" 
    
    try:
      xid = db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.id == treatmentprocid)).select()
      relgrproc = False
      transaction_id = ""
      if(len(xid)==1):
	transaction_id = common.getstring(xid[0].relgrtransactionid)
	relgrproc = common.getboolean(xid[0].relgrproc)
      
      trlist = []
      trlist.append(transaction_id)      

      if(relgrproc == True)  :
	jsonreqdata = {
               "apikey":apikey,
               "transaction_id":trlist
        }
	
	logger.loggerpms2.info(">>API-7 Void Transaction\n")
	logger.loggerpms2.info("===Req_data=\n" + json.dumps(jsonreqdata) + "\n")        
	
	jsonencodeddata = self.encoderequestdata(jsonreqdata)
      
      
	#resp = requests.post(url,json=jsonencodeddata)
	resp = requests.post(url,data=jsonencodeddata)      
	jsonresp = {}
	if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
	      respstr =   resp.text
	      jsonresp = self.decoderesponsedata(respstr) 
	      if(jsonresp["response_status"] == True):
		jsonresp["result"] = "success"
		jsonresp["error_message"] = ""
		db((db.treatment_procedure.relgrtransactionid == transaction_id) & \
	           (db.treatment_procedure.relgrproc == True)).update(\
	             is_active = False,
	             status = 'Cancelled',
	        )
		db(db.treatment.id == treatmentid).update(status = 'Cancelled',is_active=False)
		account.updatetreatmentcostandcopay(db,None,treatmentid)
	      else:
		jsonresp["result"] = "fail"
		jsonresp["error_message"] = errormessage(db,jsonresp["error_code"],jsonresp.get('response_message',"")) 
		
	else:
	  
	  jsonresp={
	    "result" : "fail",
	    "error_message":"Void Transaction API-7:\n" + errormessage(db,"MDP099")  + "\n(" + str(resp.status_code) + ")",
	    "response_status":"",
	    "response_message":"",
	    "error_code":"MDP099",
	  }
      else:
	jsonresp={
          "result" : "fail",
          "error_message":errormessage(db,"MDP029") ,
          "response_status":"",
          "response_message":"",
          "error_code":"MDP029",
        }
    
      
    except Exception as e:
      
      jsonresp = {
        "result":"fail",
        "error_message":"Void Transaction API-7:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
      }
      
    logger.loggerpms2.info(">>API-7 Void Transaction Response Exit\n")
    logger.loggerpms2.info("===Exit Resp_data=\n" + json.dumps(jsonresp) + "\n")      
	  
    return json.dumps(jsonresp)
   
      
  # this API emulates sendOTP & validate OTP APIs of Religare class
  def validaterlgmember399(self,plan_code,policy,voucher_code,promocode=None):
    
    self.policy = policy
    db = self.db

    
    providerid = self.providerid

    rlgobj = Religare(db, providerid)
    
    if(promocode == None):
      promocode = "fP8dW8"

    try:
      ackid = common.generateackid("RLG", 10)
      
      db.sessionlog.insert(\
	        ackid = ackid,
	        promocode = promocode,
	        created_on = common.getISTFormatCurrentLocatTime(),
	        created_by = 1 ,
	        modified_on = common.getISTFormatCurrentLocatTime(),
	        modified_by = 1     
	      )      
      
      r = db((db.rlgvoucher.plancode==plan_code) &\
             (db.rlgvoucher.policy==policy) &\
             (db.rlgvoucher.vouchercode==voucher_code) &\
             (db.rlgvoucher.is_active==True)).select()
      
      if(len(r) == 1):
	#success
	cell = "0000000000" if(common.getstring(r[0].cell) == "") else r[0].cell
	gender = "F" if(common.getstring(r[0].gender) == "") else r[0].gender
	x = common.getnulldt(r[0].dob)
	dob = "1990-01-01" if(x == "") else datetime.datetime.strftime("%Y-%m-%d", r[0].dob)
	
	
	customer_id = "ci_" + voucher_code
	customer_name = r[0].fname + "" if(common.getstring(r[0].lname) == "") else (" " + common.getstring(r[0].lname))
	jsonresp = {}
	
	
	jsonresp["result"] = "success"
	jsonresp["error_message"] = ""
	jsonresp["ackid"] = ackid
	jsonresp["plan_code"] = plan_code
	jsonresp["voucher_code"] = voucher_code
	jsonresp["policy"] = policy
	jsonresp["customer_id"] = customer_id
	jsonresp["mobile_number"] = cell
	jsonresp["dob"] = dob
	jsonresp["gender"] = "Female" if gender == "F" else "Male"
	jsonresp["fname"] = common.getstring(r[0].fname)
	jsonresp["mname"] = common.getstring(r[0].mname)
	jsonresp["lname"] = common.getstring(r[0].lname)
	
	db.rlgservices.insert(ackid=ackid, service_id = "399")
	
      else:
	#invalid member
	jsonresp={
                  "result" : "fail",
	          "ackid":ackid,
	          "plan_code":plan_code,
	          "voucher_code":voucher_code,
	          "policy":policy,
                  "error_message":errormessage(db,"MDP102") ,
                  "response_status":"",
                  "response_message":"",
                  "error_code":"MDP102",
                }
	
      
    
    except Exception as e:
      
      jsonresp = {
             "result":"fail",
             "error_message":"Error Validating 399 member API:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
             "ackid":ackid,
             "plan_code":plan_code,
             "voucher_code":voucher_code,
             "policy":policy,
             "response_status":"",
             "response_message":"",
             "error_code":"MDP100",
           }      
    
    return json.dumps(jsonresp)  


  
  def getreligarepatient399(self, avars ):
    
    
    db = self.db
    providerid = self.providerid
    rlgobj = Religare(db, providerid)
    ackid = avars["ackid"] if "ackid" in avars else "ackid_399" 
    
    try:
      r = db(db.sessionlog.ackid == ackid).count()
      if(r != 1):
	jsonresp={
	          "result" : "fail",
	          "ackid":ackid,
	          "error_message":errormessage(db,"ERR002") ,
	          "response_status":"",
	          "response_message":"",
	          "error_code":"ERR002",
	        }
	return json.dumps(jsonresp)
      
      policy = avars["policy"] if "policy" in avars else "policy_399"
      plancode = avars["plan_code"] if "plan_code" in avars else "399"
      voucher_code = avars["voucher_code"] if "voucher_code" in avars else "voucher_399"
      customer_id = avars["customer_id"] if "customer_id" in avars else "ci_" + voucher_code
      fname = avars["fname"] if "fname" in avars else "FN_399"
      mname = avars["mname"] if "mname" in avars else "MN_399"
      lname = avars["lname"] if "lname" in avars else "LN_399"
      
      customer_name =  fname 
      customer_name = customer_name if(lname == "") else customer_name + " " + lname
      
      mobile_number = avars["mobile_number"] if "mobile_number" in avars else "0000000000"
      gender = avars["gender"] if "gender" in avars else "F"
      dob = avars["dob"] if "dob" in avars else "1990-01-01"


       
      jsonresp = json.loads(rlgobj.getreligarepatient(customer_id, customer_name, mobile_number, dob, gender,policy))
      jsonresp["ackid"] = ackid
      
      
      
    except Exception as e:
      jsonresp = {
             "result":"fail",
             "error_message":"Error Getting  399 member API:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
             "ackid":ackid,
             "response_status":"",
             "response_message":"",
             "error_code":"MDP100",
           }      
      
      
    
    
    return json.dumps(jsonresp)
  
  def updatereligarepatient399(self, avars ):
      
      db = self.db
      providerid = self.providerid
      auth = current.auth
      rlgobj = Religare(db, providerid)
      
      ackid = avars["ackid"] if "ackid" in avars else "ackid_399"
      
      try:
	
	r = db(db.sessionlog.ackid == ackid).count()
	if(r != 1):
	  jsonresp={
	            "result" : "fail",
	            "ackid":ackid,
	            "error_message":errormessage(db,"ERR002") ,
	            "response_status":"",
	            "response_message":"",
	            "error_code":"ERR002",
	          }
	  return json.dumps(jsonresp)	
	memberid = int(common.getid(avars["memberid"])) if "memberid" in avars else 0
	email = avars["email"] if "email" in avars else "mydentalplan.in@gmail.com"
	addr1 = avars["address1"] if "address1" in avars else "addr1"
	addr2 = avars["address2"] if "address2" in avars else "addr2"
	addr3 = avars["address3"] if "address3" in avars else "addr3"
	city = avars["city"] if "city" in avars else "Bengaluru"
	st = avars["st"] if "st" in avars else "Karnatak (KA)"
	pin = avars["pin"] if "pin" in avars else "560092"
	cell = avars["cell"] if "cell" in avars else "0000000000"
	dob = avars["dob"] if "dob" in avars else "01/01/1990"
	gender = avars["gender"] if "gender" in avars else "Female"
	
	db(db.patientmember.id == memberid).update(\
	  email = email,
	  address1 = addr1,
	  address2 = addr2,
	  address3 = addr3,
	  city =city,
	  st = st,
	  pin = pin,
	  cell=cell,
	  gender = gender,
	  dob = datetime.datetime.strptime(dob, "%d/%m/%Y"),
	  modified_on = common.getISTFormatCurrentLocatTime(),
	  modified_by = 1 if(auth.user == None) else auth.user.id     
	  
	)
	
	jsonresp = {"result":"success","error_message":""}	

	jsonresp["ackid"] = ackid
	
      
	
	
      except Exception as e:
	jsonresp = {
	       "result":"fail",
	       "error_message":"Error Getting  399 member API:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
	       "ackid":ackid,
	       "response_status":"",
	       "response_message":"",
	       "error_code":"MDP100",
	     }      
	
	
      
      
      return json.dumps(jsonresp)  
    
    
    
    
  def getreligareprocedures399(self,avars):
  
      logger.loggerpms2.info("Enter Get Religare Procedures \n"  + str(avars))
    
      db = self.db
      providerid = self.providerid
      rlgobj = Religare(db, providerid)
      ackid = avars["ackid"] if "ackid" in avars else "ackid_399"      
      
      try:
	r = db(db.sessionlog.ackid == ackid).count()
	if(r != 1):
	  jsonresp={
	            "result" : "fail",
	            "ackid":ackid,
	            "error_message":errormessage(db,"ERR002") ,
	            "response_status":"",
	            "response_message":"",
	            "error_code":"ERR002",
	          }
	  return json.dumps(jsonresp)
	
	procedurepriceplancode = avars["procedurepriceplancode"] if "procedurepriceplancode" in avars else "XXX"
	
	searchphrase = avars["searchphrase"] if "searchphrase" in avars else ""
	page = int(common.getid(avars["page"])) if "page" in avars else 0
	maxcount = int(common.getid(avars["maxcount"])) if "maxcount" in avars else 0


	
	jsonresp = json.loads(rlgobj.getreligareprocedures(ackid, 
	                                                  procedurepriceplancode, 
	                                                  searchphrase, 
	                                                  page, 
	                                                  maxcount))
	
      except Exception as e:
	jsonresp = {
		       "result":"fail",
		       "error_message":"Error Get Religare   399 Procedures API:\n" + errormessage("MDP100")  + "\n(" + str(e) + ")",
	               "ackid":ackid,
		       "response_status":"",
		       "response_message":"",
		       "error_code":"MDP100",
		     }      
	

          
      return json.dumps(jsonresp)
    

    
  def addRlgProcedureToTreatment399(self,avars):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    rlgobj = Religare(db, providerid)
    ackid = avars["ackid"] if "ackid" in avars else "ackid_399"    
    jsonresp={}
    
    try:
      r = db(db.sessionlog.ackid == ackid).count()
      if(r != 1):
	jsonresp={
                  "result" : "fail",
                  "ackid":ackid,
                  "error_message":errormessage("ERR002") ,
                  "response_status":"",
                  "response_message":"",
                  "error_code":"ERR002",
                }
	return json.dumps(jsonresp)      
      
      treatmentid = int(common.getid(avars["treatmentid"])) if "treatmentid" in avars else 0
      procedurepriceplancode = avars["plancode"] if "plancode" in avars else "RLG101"
      procedurecode = avars["procedurecode"] if "procedurecode" in avars else "G0104"
      procedurename = avars["procedurename"] if "procedurename" in avars else "Dental consultations - Emergency Palliative Treatment of Dental pain and minor procedures- ONLY"
      procedurefee = float(common.getvalue(avars["procedurefee"])) if "procedurefee" in avars else "0.00"
      tooth = avars["tooth"] if "tooth" in avars else "1"
      quadrant = avars["quadrant"] if "quadrant" in avars else "Q1"
      remarks = avars["remarks"] if "remarks" in avars else "remarks"
      policy_number = avars["policy_number"] if "policy_number" in avars else "0000000000"
      customer_id = avars["customer_id"] if "customer_id" in avars else "ci_399"
      mobile_number = avars["mobile_number"] if "mobile_number" in avars else "0000000000"
	    
      
      procs = db((db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode) & \
                 (db.vw_procedurepriceplan_relgr.procedurecode == procedurecode)).select()
	
      procedureid = 0
      ucrfee = 0
      procedurefee = 0
      copay = 0
      companypays = 0
      relgrproc = False
      memberid = 0
      
      service_id = ""
      service_name = ""
      service_category = ""
      
      if(len(procs)>0):
	ucrfee = float(common.getvalue(procs[0].ucrfee))
	procedurefee = float(common.getvalue(procs[0].relgrprocfee))
	if(procedurefee == 0):
	    procedurefee = ucrfee
	copay = float(common.getvalue(procs[0].relgrcopay))
	inspays = float(common.getvalue(procs[0].relgrinspays))
	companypays = float(common.getvalue(procs[0].companypays))
	procedureid = int(common.getid(procs[0].id))    
	relgrproc = bool(common.getboolean(procs[0].relgrproc))
	service_id = int(common.getid(procs[0].service_id))
	service_name = procs[0].service_name
	service_category = procs[0].service_category
  
        transaction_id = "RLG399_"
	random.seed(int(time.time()))
	for j in range(0,7):
	    transaction_id += str(random.randint(0,9))      

      
	t = db(db.vw_treatmentlist.id == treatmentid).\
          select(db.vw_treatmentlist.tplanid,db.vw_treatmentlist.startdate, db.vw_treatmentlist.memberid)
    
	procid = db.treatment_procedure.insert(treatmentid = treatmentid, dentalprocedure = procedureid,status="Started",\
                                             treatmentdate=t[0].startdate if(len(t)>0) else common.getISTFormatCurrentLocatTime(),\
	                                     ucr = ucrfee, procedurefee=procedurefee, copay=copay,inspays=inspays,companypays=companypays,\
	                                     tooth=tooth,quadrant=quadrant,remarks=remarks,authorized=False,service_id = service_id,\
	                                     relgrproc=relgrproc,relgrtransactionid = transaction_id,relgrtransactionamt=inspays) 

		
	tplanid = int(common.getid(t[0].tplanid)) if(len(t) > 0) else 0
	memberid = int(common.getid(t[0].memberid)) if(len(t) > 0) else 0
	#update treatment with new treatment cost
	account.updatetreatmentcostandcopay(db,auth.user,treatmentid)
	#update tplan with new treatment cost
	account.calculatecost(db,tplanid)
	account.calculatecopay(db, tplanid,memberid)
	account.calculateinspays(db,tplanid)
	account.calculatedue(db,tplanid)  
	jsonresp["treatmentprocid"] = procid
	jsonresp["result"] =  "success"
	jsonresp["error_message"] = ""
	jsonresp["customer_id"] = customer_id
	jsonresp["policy_number"] = policy_number
	jsonresp["mobile_number"] = mobile_number      
	jsonresp["ackid"] = ackid      
      
      else:
	jsonresp={
          "result" : "fail",
          "error_message":"Error adding procedure to Religare Treatment 399",
	  "ackid":ackid,
          "response_status":"",
          "response_message":"",
          "customer_id":customer_id,
          "policy_number":policy_number,
          "mobile_number": mobile_number
        }
    
      
    except Exception as e:
      jsonresp = {
	             "result":"fail",
	             "error_message":"Error addRlgProcedureToTreatment399 API Exception:\n" + errormessage("MDP100")  + "\n(" + str(e) + ")",
                     "ackid":ackid,
	             "response_status":"",
	             "response_message":"",
	             "error_code":"MDP100",
	           }      
      
	
    return json.dumps(jsonresp)
  
  
  
  