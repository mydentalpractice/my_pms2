from gluon import current

import datetime
import json

from applications.my_pms2.modules import common
from applications.my_pms2.modules import gender
from applications.my_pms2.modules import states
from applications.my_pms2.modules import status
from applications.my_pms2.modules import relations

from applications.my_pms2.modules import mdpmedia

from applications.my_pms2.modules import logger



class Provider:
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    return 


  def addproviderimage(self,avars):
  
    db = self.db
    providerid = self.providerid
  
    try:
  
      avars["action"] = 'upload_media'
      avars["ref_code"] = "PRV"
      avars["ref_id"] = str(providerid)
      avars["mediatype"] = "image"
      avars["mediaformat"] = "jpg"
      avars["providerid"] = str(providerid)
  
  
  
      medobj = mdpmedia.Media(db, providerid, "image", "jpg")
      rsp = json.loads(medobj.upload_media(avars))
  
      if(rsp["result"] == "success"):
        db(db.provider.id == providerid).update(imageid = common.getkeyvalue(rsp,"mediaid","0"))
  
    except Exception as e:
      logger.loggerpms2.info("Add Provider Image API  Exception:\n" + str(e))      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "Add Provider Image API Exception Error - " + str(e)
      return json.dumps(excpobj)
  
    return json.dumps(rsp)


  def getProviderCode(self):
    db = self.db
    sql = "UPDATE providercount SET providercount = providercount + 1;"
    db.executesql(sql)
    db.commit()
  
    xrows = db(db.providercount.id >0).select()
    providercount = int(xrows[0].providercount)    
  
    providercode = "P" + str(providercount).zfill(5)
    
    return ({"providercode":providercode, "result":"success","error_message":"","error_code":""})
 
  
       
  
  def new_provider(self,avars):
    db = self.db
    auth  = current.auth
    rspobj = {}
  
    logger.loggerpms2.info("Enter new Provider ")
  
    try:
      prospectid = int(common.getid(common.getkeyvalue(avars,"prospectid","0")))
      obj = self.getProviderCode()
      provider = obj["providercode"]
     
      providerid = db.provider.insert(\
  
  
        provider=common.getkeyvalue(avars,"providerCode",provider),
        title=common.getkeyvalue(avars,'title',""),
        providername=common.getkeyvalue(avars,'providername',""),
        practicename=common.getkeyvalue(avars,'practicename',""),
        address1=common.getkeyvalue(avars,'address1',""),
        address2=common.getkeyvalue(avars,'address2',""),
        address3=common.getkeyvalue(avars,'address3',""),
        city=common.getkeyvalue(avars,'city',""),
        st=common.getkeyvalue(avars,'st',""),
        pin=common.getkeyvalue(avars,'pin',""),
        
        p_address1=common.getkeyvalue(avars,'p_address1',""),
        p_address2=common.getkeyvalue(avars,'p_address2',""),
        p_address3=common.getkeyvalue(avars,'p_address3',""),
        p_city=common.getkeyvalue(avars,'p_city',""),
        p_st=common.getkeyvalue(avars,'p_st',""),
        p_pin=common.getkeyvalue(avars,'p_pin',""),
        
        telephone=common.getkeyvalue(avars,'telephone',""),
        cell=common.getkeyvalue(avars,'cell',""),
        email=common.getkeyvalue(avars,'email',""),
        
        taxid=common.getkeyvalue(avars,'taxid',""),
        speciality=int(common.getid(common.getkeyvalue(avars,'speciality',"1"))),
        specialization=common.getkeyvalue(avars,'specialization',""),
        sitekey=common.getkeyvalue(avars,'sitekey',""),
        groupregion=int(common.getid(common.getkeyvalue(avars,'groupregion',"1"))),
        
        registration=common.getkeyvalue(avars,'registration',""),
        registered=common.getboolean(common.getkeyvalue(avars,'registered',"True")),
        
        pa_providername=common.getkeyvalue(avars,'pa_providername',""),
        pa_practicename=common.getkeyvalue(avars,'pa_practicename',""),
        pa_practiceaddress=common.getkeyvalue(avars,'pa_practiceaddress',""),
        pa_dob=common.getdatefromstring(common.getkeyvalue(avars,'pa_dob',common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y")),"%d/%m/%Y"),
        pa_parent=common.getkeyvalue(avars,'pa_parent',""),
        pa_address=common.getkeyvalue(avars,'pa_address',""),
        pa_pan=common.getkeyvalue(avars,'pa_pan',""),
        pa_regno=common.getkeyvalue(avars,'pa_regno',""),
        pa_date=common.getdatefromstring(common.getkeyvalue(avars,'pa_date',common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y")),"%d/%m/%Y"),
  
        pa_accepted=common.getboolean(common.getkeyvalue(avars,'pa_accepted',"False")),
        pa_approved=common.getboolean(common.getkeyvalue(avars,'pa_approved',"False")),
        pa_approvedby=int(common.getid(common.getkeyvalue(avars,'pa_approvedby',"1"))),
        pa_approvedon=common.getdatefromstring(common.getkeyvalue(avars,'pa_approvedon',common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y")),"%d/%m/%Y"),
        pa_day=common.getkeyvalue(avars,'pa_day',""),
        pa_month=common.getkeyvalue(avars,'pa_month',""),
        pa_location=common.getkeyvalue(avars,'pa_location',""),
        pa_practicepin=common.getkeyvalue(avars,'pa_practicepin',""),
        pa_hours=common.getkeyvalue(avars,'pa_hours',""),
        pa_longitude=common.getkeyvalue(avars,'pa_longitude',""),
        pa_latitude=common.getkeyvalue(avars,'pa_latitude',""),
        pa_locationurl=common.getkeyvalue(avars,'pa_locationurl',""),
        
        groupsms=common.getboolean(common.getkeyvalue(avars,'groupsms',"True")),
        groupemail=common.getboolean(common.getkeyvalue(avars,'groupemail',"True")),
        
        status=common.getkeyvalue(avars,'status',"Enrolled"),
        bankid = int(common.getid(common.getkeyvalue(avars,'bankid','0'))),
        enrolleddate = common.getISTFormatCurrentLocatTime(),
        assignedpatientmembers = int(common.getid(common.getkeyvalue(avars,'assignedpatientmembers','0'))),
        languagesspoken = common.getkeyvalue(avars,'languagesspoken',"English,Hindi"),
        
        captguarantee = float(common.getvalue(common.getkeyvalue(avars,'captguarantee',"0.0"))),
        schedulecapitation  = float(common.getvalue(common.getkeyvalue(avars,'schedulecapitation',"0.0"))),
        capitationytd  = float(common.getvalue(common.getkeyvalue(avars,'capitationytd',"0.0"))),
        captiationmtd  = float(common.getvalue(common.getkeyvalue(avars,'captiationmtd',"0.0"))),        

  
        is_active = True,
        created_on=common.getISTFormatCurrentLocatTime(),
        modified_on=common.getISTFormatCurrentLocatTime(),
        created_by = 1 if(auth.user == None) else auth.user.id,
        modified_by= 1 if(auth.user == None) else auth.user.id
  
      )
  
     
  
   
     
      rspobj = {
  
  
        "providerid":str(providerid),
        "provider" : provider,
  
        "result":"success",
        "error_message":"",
        "error_code":""
      }            
  
  
    except Exception as e:
      mssg = "New Provider Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = "MDP100"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)

    return json.dumps(rspobj)             



  

  def get_provider(self,avars):
    db = self.db
    auth  = current.auth
    rspobj = {}
    owner = ""
  
    try:
      providerid = int(common.getkeyvalue(avars,"providerid","0"))
 
      ds = db((db.provider.id == providerid) & (db.provider.is_active == True)).select()
  
  
  
      if(len(ds) != 1):
        rspobj = {
  
          "providerid":str(providerid),
          "result":"fail",
          "error_message":"Error Getting Provider Details - no or duplicate record",
          "error_code":""
        }                
        return json.dumps(rspobj)
  
  
      rspobj = {
        "providerid":str(providerid),
        "provider":ds[0].provider,
        "title":ds[0].title,
        "providername":ds[0].providername,
        "practicename":ds[0].practicename,
        "address1":ds[0].address1,
        "address2":ds[0].address2,
        "address3":ds[0].address3,
        "city":ds[0].city,
        "st":ds[0].st,
        "pin":ds[0].pin,
        "p_address1":ds[0].p_address1,
        "p_address2":ds[0].p_address2,
        "p_address3":ds[0].p_address3,
        "p_city":ds[0].p_city,
        "p_st":ds[0].p_st,
        "p_pin":ds[0].p_pin,
        "telephone":ds[0].telephone,
        "cell":ds[0].cell,
        "fax":ds[0].fax,
        "email":ds[0].email,
        "taxid":ds[0].taxid,
        "enrolleddate":common.getstringfromdate(ds[0].enrolleddate,"%d/%m/%Y"),
        "assignedpatientmembers":str(ds[0].assignedpatientmembers),
        "languagesspoken":ds[0].languagesspoken,
        "speciality":str(ds[0].speciality),
        "specialization":ds[0].specialization,
        "sitekey":ds[0].sitekey,
        "groupregion":str(ds[0].groupregion),
        "registration":ds[0].registration,
        "registered":ds[0].registered,
        "pa_providername":ds[0].pa_providername,
        "pa_practicename":ds[0].pa_practicename,
        "pa_practiceaddress":ds[0].pa_practiceaddress,
        "pa_dob":common.getstringfromdate(ds[0].pa_dob,"%d/%m/%Y"),
        "pa_parent":ds[0].pa_parent,
        "pa_address":ds[0].pa_address,
        "pa_pan":ds[0].pa_pan,
        "pa_regno":ds[0].pa_regno,
        "pa_date":common.getstringfromdate(ds[0].pa_date,"%d/%m/%Y"),
        "pa_accepted":ds[0].pa_accepted,
        "pa_approved":ds[0].pa_approved,
        "pa_approvedby":ds[0].pa_approvedby,
        "pa_approvedon":common.getstringfromdate(ds[0].pa_approvedon, "%d/%m/%Y"),
        "pa_day":ds[0].pa_day,
        "pa_month":ds[0].pa_month,
        "pa_location":ds[0].pa_location,
        "pa_practicepin":ds[0].pa_practicepin,
        "pa_hours":ds[0].pa_hours,
        "pa_longitude":ds[0].pa_longitude,
        "pa_latitude":ds[0].pa_latitude,
        "pa_locationurl":ds[0].pa_locationurl,
        "groupsms":ds[0].groupsms,
        "groupemail":ds[0].groupemail,
        "bankid":str(ds[0].bankid),
  
        "captguarantee":str(ds[0].captguarantee),
        "schedulecapitation":str(ds[0].schedulecapitation),
        "capitationytd":str(ds[0].capitationytd),
        "captiationmtd":str(ds[0].captiationmtd),
   
        "status":ds[0].status,
        
        "is_active":ds[0].is_active,
        
        "created_by":ds[0].created_by,
        "modified_by":ds[0].modified_by,

        "created_on":common.getstringfromdate(ds[0].created_on,"%Y-%m-%d %H:%M:%S"),
        "modified_on":common.getstringfromdate(ds[0].modified_on,"%Y-%m-%d %H:%M:%S"),
        
        "result":"success",
        "error_message":"",
        "error_code":""
      }
  
    except Exception as e:
      mssg = "Get Prospect Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = "MDP100"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)
    
    return json.dumps(rspobj)

  
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