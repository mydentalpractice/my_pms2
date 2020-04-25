from gluon import current

import datetime
import json

from applications.my_pms2.modules import common
from applications.my_pms2.modules import gender
from applications.my_pms2.modules import states
from applications.my_pms2.modules import status
from applications.my_pms2.modules import relations
from applications.my_pms2.modules import logger

class Provider:
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    return 

  def getprovider(self):
    logger.loggerpms2.info(">>Get Provider API\n")
        
    db = self.db
    providerid = self.providerid    
    auth = current.auth
    resp={}
      
    try:
      provdict = common.getproviderfromid(db, providerid)
      providerid = int(provdict["providerid"])
  
      resp ={
        "result" : "success",
        "error_message":"",
        "providerid":providerid,
        "provider":provdict["provider"],
        "providername":provdict["providername"],
        "practicename":provdict["practicename"],
        "practiceaddress":provdict["practiceaddress"],
        "city":provdict["city"],
        "st":provdict["st"],
        "pin":provdict["pin"],
        "cell":provdict["cell"],
        "email":provdict["email"],
        "registration":provdict["registration"],
        "longitude":provdict["longitude"],
        "latitude":provdict["latitude"],
        "locationurl":provdict["locationurl"],
      
      }
      
      logger.loggerpms2.info("GetProvider Rsp_data=\n" + json.dumps(resp) + "\n")
      
  
    except Exception as e:
      mssg = "Get Provider API Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)
      resp = {}
      resp["providerid"] = str(providerid)
      resp["result"] = "fail"
      resp["error_message"] = mssg 
      
    
    return json.dumps(resp)


  def updatememberprovider(self, memberid,newproviderid):
  
    logger.loggerpms2.info(">>Update Member Provider API\n")
     
    db = self.db
    
    auth = current.auth
    retobj = {}
    
    try:
      
      p = db(db.provider.id == newproviderid).select(db.provider.pin)
      pin = common.getstring(p[0].pin) if(len(p) == 1) else ""
      db(db.patientmember.id == memberid).update(\
        provider = newproviderid,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1 if(auth.user == None) else auth.user.id     
        )
      
      r = db(db.patientmember.id == memberid).select(db.patientmember.webmember)
      
      webmemberid = int(common.getid(r[0].webmember)) if(len(r) > 0) else 0
      
      db(db.webmember.id == webmemberid).update(\
        provider = newproviderid,
        pin3 = pin,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1 if(auth.user == None) else auth.user.id     
        )
      
            
      retobj = {"result":"success","error_message":""}      
      
    
    except Exception as e:
      mssg = "Update Member Provider API Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)
      retobj = {}
      retobj["result"] = "fail"
      retobj["error_message"] = mssg
                
  
    
    return json.dumps(retobj)

  
  #this API generates a list of providers based on the following logic
  #if pin != None, all providers with this pincode
  #if pin == None & city != None, then all providers in this city
  #if pin == None, city == None, st 1= None, then all  providers in this state
  #if pin == None, city == None, st == None, then all providers in the country
  def getproviders(self, avars):
    
    
    db = self.db
    
       
    try:
      ackid = avars["ackid"] if "ackid" in avars else None
      
      if((ackid != None) & (ackid != "")):
        pin = avars["pin"] if "pin" in avars else None
        city = avars["city"] if "city" in avars else None
        st = avars["state"] if "state" in avars else None
        
        
        provs = db( \
                   ((1==1) if(pin == None) else (db.provider.pin == pin )) &\
                   ((1==1) if(city == None) else (db.provider.city == city )) &\
                   ((1==1) if(st == None) else (db.provider.st == st )) &\
                   (db.provider.registered == True) &\
                   (db.provider.pa_accepted == True) &\
                   db.provider.is_active == True).select(db.provider.id,\
                                                        db.provider.provider,\
                                                        db.provider.providername,
                                                        db.provider.practicename,
                                                        db.provider.address1,
                                                        db.provider.address2,
                                                        db.provider.address3,
                                                        db.provider.city,
                                                        db.provider.st,
                                                        db.provider.pin,
                                                        db.provider.cell,
                                                        db.provider.telephone,
                                                        db.provider.registration,
                                                        db.provider.pa_locationurl)
  
   
        for prov in provs:
          
          provobj={
          
            "providerid":int(common.getid(prov.id)),
            "providercode":common.getstring(prov.provider),
            "providername":common.getstring(prov.providername),
            "practicename":common.getstring(prov.practicename),
            "practiceaddress":common.getstring(prov.pa_practiceaddress),
            "address1":common.getstring(prov.address1),
            "address2":common.getstring(prov.address2),
            "address3":common.getstring(prov.address3),
            "city":prov.city,
            "state":prov.st,
            "pin":prov.pin,
            "cell":prov.cell,
            "telephone":prov.telephone,
            "registration":prov.registration,
            "location":prov.pa_locationurl
          }
          
          provlist.append(provobj)
      
        jsonresp = {
          
          "result":"success",
          "error_message":"",
          "error_code":"",
          "providerlist":provlist,
          "ackid":ackid
           
        
        } 
        
      else:
        msg = "Get Providers API: " + self.rlgrobj.errormessage("ERR000")
        logger.loggerpms2.info(msg)
        jsonresp = {
          "result":"fail",
          "error_code":"ERR000",
          "error_message": msg
        }        
      
      
 
    except Exception as e:
      msg = "Get Providers API Exception:\n" + self.rlgrobj.errormessage("ERR004")  + "\n(" + str(e) + ")"
      logger.loggerpms2(msg)
      jsonresp["result"] = "fail"
      jsonresp["error_code"] = "ERR004"
      jsonresp["error_message"] = msg
        
    
    return json.dumps(jsonresp)