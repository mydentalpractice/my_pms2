from gluon import current
#
import datetime
import time
import json
from decimal  import Decimal

import requests
import urllib

from applications.my_pms2.modules import common
from applications.my_pms2.modules import gender
from applications.my_pms2.modules import states
from applications.my_pms2.modules import status

from applications.my_pms2.modules import logger

class Webmember:
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


  def getrelationsbycompanyplan(self,companyid,planid):
    db = self.db
    
  def getplansbyregion(self, regionid,companyid):
    db = self.db
    
   
    
    plans = db((db.companyhmoplanrate.is_active == True) & (db.companyhmoplanrate.groupregion==regionid) & (db.companyhmoplanrate.company==companyid) & \
           (db.companyhmoplanrate.relation == 'Self') & (db.hmoplan.is_active==True)).\
    select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
           left=db.hmoplan.on((db.companyhmoplanrate.hmoplan == db.hmoplan.id)&(db.hmoplan.is_active==True)),distinct=True)
    
    planlist = []
    planobj = {}
    for plan in plans:
      pobj = {
        "planid" : plan.id,
        "plancode" : plan.hmoplancode,
        "planname" : plan.name
      }
      planlist.append(pobj)
    
    planobj["count"] = len(plans)
    planobj["planlist"] = planlist
    return json.dumps(planobj)
  
  def updatewebmember(self,patobj):
     
    db = self.db
    
    auth = current.auth
    retobj = {}
    try:
      
      providerid  = int(common.getid(patobj["providerid"])) if 'providerid' in patobj else 1
      webmemberid = int(common.getid(patobj["webmemberid"])) 
      
      #update webmember
      db(db.webmember.id == webmemberid).update(\

        webmember = patobj["webmember"],
       
        groupref = patobj["groupref"],
    
        fname = patobj["fname"],
        mname = patobj["mname"],
        lname = patobj["lname"],
        webdob = datetime.datetime.strptime(patobj['webdob'], "%d/%m/%Y"),
        cell = patobj["cell"],
        email = patobj["email"],
        telephone = patobj["telephone"],
        gender = patobj["gender"],
        address1 = patobj["address1"],
        address2 = patobj["address2"],
        address3 = patobj["address3"],
        city = patobj["city"],
        st = patobj["st"],
        pin = patobj["pin"],
        pin1 = patobj["pin1"],
        pin2 = patobj["pin2"],
        pin3 = patobj["pin3"],
        paid = common.getboolean(patobj["paid"]),
        provider = providerid  if providerid >=1 else 1,
        company = int(common.getid(patobj["companyid"])) ,
        groupregion = int(common.getid(patobj["regionid"])),
        hmoplan = int(common.getid(patobj["planid"])),
        memberorder = int(common.getid(patobj["memberorder"])),
        
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1 if(auth.user == None) else auth.user.id     
        
      )
      
      ##update dependants
      #deplist = patobj["deplist"]
      #for dep in deplist:
        #db.webmemberdependants.update_or_insert(((db.webmemberdependants.id==dep.depid)&\
                                                 #(db.webmemberdependants.webmember==dep.webmemberid)), \
                                                #webmember = dep.webmemberid,
                                                #fname = dep.fname,
                                                #mname = dep.mname,
                                                #lname = dep.lname,
                                                #memberoder = dep.memberorder,
                                                #depdob = datetime.datetime.strptime(dep.depdob, "%d/%m/%Y"),
                                                #gender = dep.gender,
                                                #relation = dep.relation,
                                                #modified_on = common.getISTFormatCurrentLocatTime(),
                                                #modified_by = 1 if(auth.user == None) else auth.user.id                                                  
                                                
                                                #)
      
     
      retobj = {"result":"success","error_message":""}
    except Exception as e:
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "Registered Member Update Exception Error - " + str(e)
      return json.dumps(excpobj)  
          
    return json.dumps(retobj)
  
  def getwebmember(self,webmemberid):
    db = self.db
    webmemobj = {}
    adddependents = True
    relations = -1

    subscribers = 1
    maxsubscribers = 1
    
    try:
      i = 0
      webmem = db((db.webmember.id == webmemberid) & (db.webmember.is_active==True)).select()
      if(len(webmem) == 1):
        webkey = common.getstring(webmem[0].webkey)
        company = ""
        companyid = 0
        providerid = int(common.getstring(webmem[0].provider))
        
        c = db(db.company.groupkey == webkey).select(db.company.id, db.company.company,db.company.maxsubscribers)
        if(len(c) == 1):
          companyid = int(common.getid(c[0].id))
          company = common.getstring(c[0].company)
          maxsubscribers = 1 if(common.getid(c[0].maxsubscribers) == None) else int(common.getid(c[0].maxsubscribers))
	  
        p = db(db.provider.id == providerid).select(db.provider.id, db.provider.provider)
        if(len(p) == 1):
          providerid = int(common.getid(p[0].id))
          provider = common.getstring(p[0].provider)
        
	
	#determine to allow adding dependants
        subscribers = subscribers + db((db.webmemberdependants.webmember == webmemberid) & (db.webmemberdependants.is_active == True)).count()
        paid = False if(common.getboolean(webmem[0].paid) == None) else common.getboolean(webmem[0].paid)
        planid = 1 if(common.getid(webmem[0].hmoplan) == None) else int(common.getid(webmem[0].hmoplan))
	relations = -1 if(common.getid(webmem[0].hmoplan) == None) else (db((db.companyhmoplanrate.company == companyid) & \
		               (db.companyhmoplanrate.hmoplan == planid) & \
		               (db.companyhmoplanrate.relation != 'Self') & \
		               (db.companyhmoplanrate.is_active == True)).count(db.companyhmoplanrate.relation)	)
	
	if((paid == True) | (relations == -1) | (planid == 1) | (subscribers == maxsubscribers)):
	  adddependents = False
	
        webmemobj["result"] = "success"
        webmemobj["error_message"] = ""
        
        
        webmemobj["webkey"] = webkey
        webmemobj["status"] = common.getstring(webmem[0].status)
        webmemobj["webmember"] = common.getstring(webmem[0].webmember)
        webmemobj["webmemberid"] = common.getstring(webmem[0].id)
        webmemobj["groupref"] = common.getstring(webmem[0].groupref)
        webmemobj["company"] = company
        webmemobj["companyid"] = str(companyid)
        webmemobj["providerid"] = str(providerid)
        webmemobj["provider"] = provider
        
        webmemobj["regionid"] = "0" if(common.getstring(webmem[0].groupregion) == None) else str(int(common.getid(webmem[0].groupregion)))
        webmemobj["planid"] = "0" if(common.getstring(webmem[0].hmoplan) == None) else str(planid)
        
        webmemobj["fname"] = common.getstring(webmem[0].fname)
        webmemobj["mname"] = common.getstring(webmem[0].mname)
        webmemobj["lname"] = common.getstring(webmem[0].lname)
        webmemobj["gender"] = common.getstring(webmem[0].gender)
        webmemobj["webdob"] = webmem[0].webdob.strftime("%d/%m/%Y")  if(webmem[0].webdob != None) else ""
        webmemobj["prempaid"] = paid
        
        webmemobj["address1"] = common.getstring(webmem[0].address1)
        webmemobj["address2"] = common.getstring(webmem[0].address2)
        webmemobj["address3"] = common.getstring(webmem[0].address3)
        webmemobj["city"] = common.getstring(webmem[0].city)
        webmemobj["st"] = common.getstring(webmem[0].st)
        webmemobj["pin"] = common.getstring(webmem[0].pin)
        webmemobj["email"] = common.getstring(webmem[0].email)
        webmemobj["cell"] = common.getstring(webmem[0].cell)
        webmemobj["telephone"] = common.getstring(webmem[0].telephone)
        
        webmemobj["pin1"] = common.getstring(webmem[0].pin1)
        webmemobj["pin2"] = common.getstring(webmem[0].pin2)
        webmemobj["pin3"] = common.getstring(webmem[0].pin3)
        webmemobj["memberorder"] = "1" if(common.getstring(webmem[0].memberorder) == None) else str(int(common.getid(webmem[0].memberorder)))
        webmemobj["relations"] = False if(relations < 1) else True

        regionlist = []
	regionobj  = {}
	
	regions = db((db.groupregion.is_active == True) & (db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.is_active == True)).\
	              select(db.groupregion.ALL,\
	                     left=db.companyhmoplanrate.on((db.companyhmoplanrate.groupregion==db.groupregion.id)  ), distinct=True, orderby=db.groupregion.id)
	
	for region in regions:
	  regionobj = {
	     "regionid": region.id,
	     "regioncode":region.groupregion,
	     "region":region.region
	  }
	  regionlist.append(regionobj)
	
	webmemobj["regions"] = regionlist
	
	planlist=[]
	planobj = {}
	
	regionid = int(common.getid(webmemobj["regionid"]))
	plans = db((db.companyhmoplanrate.is_active == True) & (db.companyhmoplanrate.groupregion== regionid) & \
		       (db.companyhmoplanrate.company==companyid) & (db.companyhmoplanrate.relation == 'Self')).\
		   select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
		          left=db.hmoplan.on((db.companyhmoplanrate.hmoplan == db.hmoplan.id)&(db.hmoplan.is_active==True))) 
	for plan in plans:
	  planobj={
	  
	    "planid":plan.id,
	    "plancode":plan.hmoplancode,
	    "planname":plan.name
	  }
	  planlist.append(planobj)
	
	webmemobj["plans"] = planlist
	
	relationlist=[]
	relationobj={}
	relations = db((db.companyhmoplanrate.company == companyid) & \
		               (db.companyhmoplanrate.hmoplan == planid) & \
	                       (db.companyhmoplanrate.groupregion == regionid) & \
		               (db.companyhmoplanrate.relation != 'Self') & \
		               (db.companyhmoplanrate.is_active == True)).select(db.companyhmoplanrate.relation)
	             
	for rel in relations:
	  relationlist.append(rel.relation)
	  
	webmemobj["relationlist"] = relationlist
	
        
       
	
	
        
        deps = db((db.webmemberdependants.webmember == webmemberid) & (db.webmemberdependants.is_active  == True)).\
          select()
        if(len(deps) >= 1):
          deplist=[]
          depobj = {}
          
          for dep in deps:
            depobj = {
              "fname":dep.fname,
              "mname":dep.mname,
              "lname":dep.lname,
              
              "depdob": dep.depdob.strftime("%d/%m/%Y"),
              "relation":dep.relation,
              "memberorder":dep.memberorder,
              "gender":dep.gender,
              "webmemberid":dep.webmember,
              "depid":dep.id
            }
            deplist.append(depobj)
            
          webmemobj["depcount"] = len(deps)
          webmemobj["deplist"] = depobj
         

          
        else:
          webmemobj["depcount"] = "0"
          webmemobj["webmemdep"] = {}

	
        
	ui={"dependents":adddependents, "payment":not paid} 
	if((common.getstring(webmem[0].status) == "Enrolled") | (common.getstring(webmem[0].status) == "Completed")):
	  ui={
	    "provider":False,
	    "webkey":False,
	    "status":False,
	    "dependents":adddependents,
	    "payment":False
	  }
	webmemobj["ui"] = ui
	
        webmemobj["result"] = "success"
        webmemobj["error_message"] = ""
        
      else:
        webmemobj["result"] = "fail"
        webmemobj["error_message"] = "Member is not Registered in MyDentalPlan"
    except Exception as e:
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = "Get Web Member Exception Error - " + str(e)
          return json.dumps(excpobj)
   
   
    return json.dumps(webmemobj)
  
  def getwebmemberdependants(self,webmemberid):
    
    db = self.db
    depobj = {}
    try:
      deps = db((db.webmemberdependants.webmember == webmemberid) & (db.webmemberdependants.is_active == True)).select()
      
      deplist = []
      
      for dep in deps:
        depobj = {
          "fname":dep.fname,
          "mname":dep.mname,
          "lname":dep.lname,
          
          "depdob": dep.depdob.strftime("%d/%m/%Y"),
          "relation":dep.relation,
          "memberorder":dep.memberorder,
          "gender":dep.gender,
          "webmemberid":dep.webmember,
          "depid":dep.id
        }
        deplist.append(depobj)      
  
      depobj = {
        "result" : "success",
        "error_message": "",
        "depcount" : len(deps),
        "deplist"  : deplist
      }
      
    except Exception as e:
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "Get Web Member Dependants Exception Error - " + str(e)
      return json.dumps(excpobj)

    return json.dumps(depobj)
  
  
  def getwebmemberdependant(self,webdepid):
    db = self.db
    depobj = {}
    
    try:
      deps = db(db.webmemberdependants.id == webdepid).select()
      for dep in deps:
        depobj = {
          "result" : "success",
          "error_message": "",
          
          "fname":dep.fname,
          "mname":dep.mname,
          "lname":dep.lname,
          
          "depdob": dep.depdob.strftime("%d/%m/%Y"),
          "relation":dep.relation,
          "memberorder":dep.memberorder,
          "gender":dep.gender,
          "webmemberid":dep.webmember,
          "depid":dep.id
        }
      
    except Exception as e:
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = "Get Web Member Dependant Exception Error - " + str(e)
        return json.dumps(excpobj)      
      
    return json.dumps(depobj)
  
  
  def updatewebmemberdependant(self,dep):
    
    db = self.db
    auth = current.auth    
    
    try:
      
 
      
      db.webmemberdependants.update_or_insert(((db.webmemberdependants.id==dep["depid"])&\
                                               (db.webmemberdependants.webmember==dep["webmemberid"])), \
                                              webmember = dep["webmemberid"],
                                              fname = dep["fname"],
                                              mname = dep["mname"],
                                              lname = dep["lname"],
                                              memberorder = dep["memberorder"],
                                              depdob = datetime.datetime.strptime(dep["depdob"], "%d/%m/%Y"),
                                              gender = dep["gender"],
                                              relation = dep["relation"],
                                              modified_on = common.getISTFormatCurrentLocatTime(),
                                              modified_by = 1 if(auth.user == None) else auth.user.id                                                  
                                              
                                              )
      
    
    except Exception as e:
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = "Update Web Member Dependant Exception Error - " + str(e)
        return json.dumps(excpobj)      
    
    
    return json.dumps({"result":"success","error_message":""})
    
  
  def deletewebmemberdependant(self,dep):
    
    
      db = self.db
      auth = current.auth    
      
      try:
        db(db.webmemberdependants.id == dep["depid"]).update(is_active = False,
                                                             modified_on = common.getISTFormatCurrentLocatTime(),
                                                             modified_by = 1 if(auth.user == None) else auth.user.id                                                  
                                                             )
      except Exception as e:
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = "Delete Web Member Dependant Exception Error - " + str(e)
          return json.dumps(excpobj)      
      
      
      return json.dumps({"result":"success","error_message":""})
   
   
  def newwebmemberpremiumpayment(self,webmemberid):
    
    
      db = self.db
      auth = current.auth    
      
      try:
	
	webkey = None
	fname = None
	dob = None
	status = None

	companyid = 0
	hmoplanid = 0	
	ds = None
	
        #no providerid for new registered member until enrollment from backoffice
        rows   = db((db.webmember.id == webmemberid) & (db.webmember.is_active == True)).select()
        if(len(rows) == 0):
          return json.dumps({"result":"fail","error_message":"Error New Webmemeber Premium Payment : Invalid Webmember"})
        
        fname  = rows[0].fname
        dob    = rows[0].webdob
        status = rows[0].status
        companyid = int(common.getid(rows[0].company))
        rows = db(db.company.id == companyid).select()
        dependantmode = common.getbool(rows[0].dependantmode)
        
        rows     = db((db.companyhmoplanrate.company == companyid) & (db.webmember.id == webmemberid)).select()
        deprows  = db(db.webmemberdependants.webmember == webmemberid).select()        

        
	if(dependantmode == True):
	    if(len(rows) > 0):
		if(len(deprows)>0):
		    ds = db.executesql('select "Self" AS relation,fname,lname,webdob, CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
			                CASE WHEN companypays IS NOT NULL THEN companypays ELSE 0.0 END AS companypays, \
			                CASE WHEN (premium IS NOT NULL) AND (companypays IS NOT NULL) THEN premium - companypays \
			                WHEN (premium IS NOT NULL) AND (companypays IS NULL) THEN premium \
			                WHEN (premium IS NULL) AND (companypays IS NOT NULL) THEN companypays \
			                ELSE 0.00 END AS youpay FROM webmember \
			                LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
			                LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
			                companyhmoplanrate.relation = "Self"  AND companyhmoplanrate.is_Active = "T"  AND \
			                companyhmoplanrate.hmoplan = webmember.hmoplan \
			                WHERE \
			                webmember.id = ' + str(webmemberid) +
			                             ' UNION ' +
			                'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob,\
			                CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium, \
			                CASE WHEN companypays IS NOT NULL THEN companypays ELSE 0.0 END AS companypays, \
			                CASE WHEN (premium IS NOT NULL) AND (companypays IS NOT NULL) THEN premium - companypays \
			                WHEN (premium IS NOT NULL) AND (companypays IS NULL) THEN premium \
			                WHEN (premium IS NULL) AND (companypays IS NOT NULL) THEN companypays \
			                ELSE 0.00 END  AS youpay FROM  webmember   \
			                LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
			                LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
			                LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND companyhmoplanrate.is_Active = "T"  AND  \
			                webmemberdependants.memberorder = companyhmoplanrate.covered AND \
			                companyhmoplanrate.hmoplan = webmember.hmoplan \
			                where webmemberdependants.is_active = "T" AND webmember.id = ' + str(webmemberid))
		else:
		    ds = db.executesql('select "Self" AS relation,fname,lname,webdob, \
			                CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
			                CASE WHEN companypays IS NOT NULL THEN companypays ELSE 0.0 END AS companypays,\
			                CASE WHEN (premium IS NOT NULL) AND (companypays IS NOT NULL) THEN premium - companypays \
			                WHEN (premium IS NOT NULL) AND (companypays IS NULL) THEN premium \
			                WHEN (premium IS NULL) AND (companypays IS NOT NULL) THEN companypays \
			                ELSE 0.00 END AS youpay FROM webmember \
			                LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
			                LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
			                companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND companyhmoplanrate.is_Active = "T"  \
			                WHERE \
			                webmember.id = ' + str(webmemberid))
	    else:
		if(len(deprows)>0):
		    ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay FROM webmember \
			                LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
			                LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
			                companyhmoplanrate.hmoplan = webmember.hmoplan AND\
			                companyhmoplanrate.relation = "Self" AND companyhmoplanrate.is_Active = "T"  \
			                WHERE webmember.id = ' + str(webmemberid) +
			                             ' UNION ' +
			                'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob, 0 AS premium, \
			                 0 AS companypays, 0 AS youpay FROM  webmember  \
			                 LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
			                 LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
			                 LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
			                 webmemberdependants.memberorder = companyhmoplanrate.covered AND companyhmoplanrate.hmoplan = webmember.hmoplan AND \
			                 companyhmoplanrate.is_Active = "T" \
			                 WHERE webmember.id = ' + str(webmemberid))
		else:
	
		    ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay \
			               FROM webmember \
			               LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
			               LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
			               companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND \
			               companyhmoplanrate.is_Active = "T" \
			               WHERE webmember.id = ' + str(webmemberid))
	    
	else:
	    if(len(rows) > 0):
		if(len(deprows)>0):
		    ds = db.executesql('select "Self" AS relation,fname,lname,webdob, \
			                CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
			                CASE WHEN companyhmoplanrate.companypays IS NOT NULL THEN companyhmoplanrate.companypays ELSE 0.0 END AS companypays, \
			                CASE WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN premium - companypays \
			                WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NULL) THEN premium \
			                WHEN (companyhmoplanrate.premium IS NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companypays \
			                ELSE 0.00 END AS youpay FROM webmember \
			                LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
			                LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND  webmember.groupregion = companyhmoplanrate.groupregion AND\
			                companyhmoplanrate.relation = "Self"  AND companyhmoplanrate.is_Active = "T"  AND \
			                companyhmoplanrate.hmoplan = webmember.hmoplan \
			                WHERE \
			                webmember.paid = "F" AND webmember.id = ' + str(webmemberid) +
			                             ' UNION ' +
			                'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob,\
			                CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium, \
			                CASE WHEN companyhmoplanrate.companypays IS NOT NULL THEN companyhmoplanrate.companypays ELSE 0.0 END AS companypays, \
			                CASE WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.premium - companyhmoplanrate.companypays \
			                WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NULL) THEN companyhmoplanrate.premium \
			                WHEN (companyhmoplanrate.premium IS NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.companypays \
			                ELSE 0.00 END  AS youpay FROM  webmember   \
			                LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
			                LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
			                LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND webmember.groupregion = companyhmoplanrate.groupregion AND companyhmoplanrate.is_Active = "T"  AND  \
			                webmemberdependants.relation = companyhmoplanrate.relation AND \
			                companyhmoplanrate.hmoplan = webmember.hmoplan \
			                where webmemberdependants.is_active = "T"  AND webmemberdependants.paid = "F" AND webmember.id = ' + str(webmemberid))
		else:
		    ds = db.executesql('select "Self" AS relation,fname,lname,webdob, \
			                CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
			                CASE WHEN companyhmoplanrate.companypays IS NOT NULL THEN companyhmoplanrate.companypays ELSE 0.0 END AS companypays,\
			                CASE WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.premium - companyhmoplanrate.companypays \
			                WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NULL) THEN companyhmoplanrate.premium \
			                WHEN (companyhmoplanrate.premium IS NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.companypays \
			                ELSE 0.00 END AS youpay FROM webmember \
			                LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
			                LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
			                companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND webmember.groupregion = companyhmoplanrate.groupregion AND  companyhmoplanrate.is_Active = "T"  \
			                WHERE \
			                webmember.paid = "F" AND webmember.id = ' + str(webmemberid))
	    else:
		if(len(deprows)>0):
		    ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay FROM webmember \
			                LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
			                LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
			                companyhmoplanrate.hmoplan = webmember.hmoplan AND\
			                companyhmoplanrate.covered = "Self" AND companyhmoplanrate.is_Active = "T"  \
			                WHERE webmember.paid = "F" AND webmember.id = ' + str(webmemberid) +
			                             ' UNION ' +
			                'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob, 0 AS premium, \
			                 0 AS companypays, 0 AS youpay FROM  webmember  \
			                 LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
			                 LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
			                 LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
			                 webmemberdependants.relation = companyhmoplanrate.relation AND companyhmoplanrate.hmoplan = webmember.hmoplan AND webmember.groupregion = companyhmoplanrate.groupregion AND \
			                 companyhmoplanrate.is_Active = "T" \
			                 WHERE webmember.paid = "F" AND webmember.id = ' + str(webmemberid))
		else:
	
		    ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay \
			               FROM webmember \
			               LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
			               LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
			               companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND \
			               companyhmoplanrate.is_Active = "T" \
			               WHERE webmember.paid = "F" AND webmember.id = ' + str(webmemberid))

        
      
	# Calculate amount to pay
	totpremium = 0
	totcompanypays = 0
	totyoupay = 0
	servicetaxes = 0
	swipecharges = 0
	total = 0
	servicetax = 0
	swipecharge = 0
    
	ppobj = {}
	mplist = []    
	
	
	if(len(ds)>0):
	  i = 0
	  for i in xrange(0,len(ds)):
	      totpremium = totpremium + round(Decimal(ds[i][4]),2)
	      totcompanypays = totcompanypays + round(Decimal(ds[i][5]),2)
	      totyoupay = totpremium - totcompanypays
	      
	      ppobj={
	        "fname":ds[i][1],
	        "lname":ds[i][2],
	        "relation":ds[i][0],
	        "dob":ds[i][3].strftime("%d/%m/%Y"),
	        "premium":str(ds[i][4]),
	        "companypays":str(ds[i][5]),
	        "memberpays":str(ds[i][6]),
	      }
	      
	      mplist.append(ppobj)
	      
	      
	  if(totyoupay > 0):
	      r = db(db.urlproperties).select()
	      if(len(r)>0):
		  servicetax = round(Decimal(r[0].servicetax),2)
		  swipecharge = round(Decimal(r[0].swipecharge),2)
	      servicetaxes = round(totyoupay * servicetax / 100,2)
	      swipecharges = round(totyoupay * swipecharge/ 100,2)
	      total = totyoupay + servicetaxes + swipecharges
	  
	  ppobj={}
	  ppobj["webmemberid"] = webmemberid
	  ppobj["memberpaymentlist"] = mplist
	  ppobj["totpremium"] = str(totpremium)
	  ppobj["totcompanypays"] = str(totcompanypays)
	  ppobj["totyoupay"] = str(totyoupay)
	  ppobj["servicetaxes"] = str(servicetaxes)
	  ppobj["swipecharges"] = str(swipecharges)
	  ppobj["total"] = str(total)
	  ppobj["result"] = "success"
	  ppobj["error_message"] = ""
	  
	else:
  
	  ppobj["webmemberid"] = webmemberid
	  ppobj["memberpaymentlist"] = mplist
	  ppobj["totpremium"] = str(totpremium)
	  ppobj["totcompanypays"] = str(totcompanypays)
	  ppobj["totyoupay"] = str(totyoupay)
	  ppobj["servicetaxes"] = str(servicetaxes)
	  ppobj["swipecharges"] = str(swipecharges)
	  ppobj["total"] = str(total)
	  ppobj["result"] = "success"
	  ppobj["error_message"] = ""
	  
       
	return json.dumps(ppobj)
      except Exception as e:
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = "Delete Web Member Dependant Exception Error - " + str(e)
          return json.dumps(excpobj)      
      
      
      return 
  

  def newwebmemberprocesspayment(self,webmemberid,payobj):
      db = self.db
      auth = current.auth
      ppobj = {} 
      
      try:
	txdatetime = datetime.datetime.now()
	txno = str(webmemberid) + "_" + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S")


	totpremium = payobj["totpremium"]
	totcompanypays = payobj["totcompanypays"]
	totyoupay = payobj["totyoupay"]
	total  = payobj["total"]
	servicetaxes = payobj["servicetaxes"]
	swipecharges = payobj["swipecharges"]
	paymentdetails = payobj["paymentdetails"]
	responsecode = "Premium Payment"
	txid = db.paymenttxlog.insert(txno=txno,txdatetime=txdatetime,webmember=webmemberid,txamount=totyoupay,total=total,servicetax=servicetaxes,swipecharge=swipecharges,responsecode=responsecode,responsemssg=paymentdetails )
	
	db(db.webmember.id == webmemberid).update(webenrollcompletedate = datetime.date.today(),status='Attempting')
	#db(db.webmemberdependants.webmember == webmemberid).update(paid=True)
	
	
	ppobj = {
	 
	 "webmemberid" : str(webmemberid),
	 "txid":str(txid),
	 "txno":str(txno),
	 "txdate":(txdatetime).strftime("%d/%m/%Y"),
	 "invoice":str(txno) + "_" + (txdatetime).strftime("%d/%m/%Y"),
	 "totpremium": str(totpremium),
	 "totcompanypays":str(totcompanypays),
	 "totyoupay":str(totyoupay),
	 "servicetaxes":str(servicetaxes),
	 "swipecharges":str(swipecharges),
	 "total":str(total),
	 "result":"success",
	 "error_message":""
	
	}
        
	return json.dumps(ppobj)
      
      except Exception as e:
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = "Delete Web Member Dependant Exception Error - " + str(e)
          return json.dumps(excpobj)      
      
      
      return 
 
  def webmember_paymentcallback(self,paymentdata):
  
      db = self.db
      providerid = self.providerid
      
      paymentcallbackobj = {}
      
      localcurrdate = common.getISTCurrentLocatTime()
      dttodaydate = datetime.datetime.strptime(localcurrdate.strftime("%d") + "/" + localcurrdate.strftime("%m") + "/" + localcurrdate.strftime("%Y"), "%d/%m/%Y")
      todaydate = dttodaydate.strftime("%d/%m/%Y")
      
      
     
      jsonConfirmPayment = paymentdata
      
      paymentref = common.getstring(jsonConfirmPayment['payment_reference']) if('payment_reference' in jsonConfirmPayment) else ""   #Payment ID
      paymenttype = common.getstring(jsonConfirmPayment['payment_type']) if('payment_type' in jsonConfirmPayment) else ""            #yes
      paymentdetail = common.getstring(jsonConfirmPayment['payment_detail']) if('payment_detail' in jsonConfirmPayment) else ""      #yes
      #cardtype = common.getstring(jsonConfirmPayment['card_type']) if('card_type' in jsonConfirmPayment) else paymenttype            #
      merchantid = common.getstring(jsonConfirmPayment['merchant_id']) if('merchant_id' in jsonConfirmPayment) else ""               #yes
      merchantdisplay = common.getstring(jsonConfirmPayment['merchant_display']) if('merchant_display' in jsonConfirmPayment) else "" #yes
      status = common.getstring(jsonConfirmPayment['status']) if('status' in jsonConfirmPayment) else ""    #yes
      invoice = common.getstring(jsonConfirmPayment['invoice']) if('invoice' in jsonConfirmPayment) else ""   #yes
      amount = 0 if(status != 'S') else (float(common.getvalue(jsonConfirmPayment['amount'])) if('amount' in jsonConfirmPayment) else 0)  #yes
      fee = 0    #if(status != 'S') else (common.getstring(jsonConfirmPayment['fee']) if('fee' in jsonConfirmPayment) else 0)   #no

      
      jsonObj = json.loads(common.getstring(jsonConfirmPayment['addln_detail']))  #yes
      paymentid = int(common.getstring(jsonConfirmPayment["txid"]))  
      paymentdate = common.getstring(jsonConfirmPayment['paymentdate']) if('paymentdate' in jsonConfirmPayment) else "01/01/1900"       
      invoiceamt = float(common.getvalue(jsonConfirmPayment['amount'])) if('amount' in jsonConfirmPayment) else 0.00
      
      error = "" if(status =="S") else common.getstring(jsonConfirmPayment['error'])
      errormsg = "" if(status =="S") else common.getstring(jsonConfirmPayment['errormsg'])

      chequeno = common.getstring(jsonConfirmPayment['chequeno']) if('chequeno' in jsonConfirmPayment) else "0000"   #yes
      acctno = common.getstring(jsonConfirmPayment['acctno']) if('acctno' in jsonConfirmPayment) else "0000"   #yes
      acctname =common.getstring(jsonConfirmPayment['acctname']) if('acctname' in jsonConfirmPayment) else "XXXX"   #yes
      bankname =common.getstring(jsonConfirmPayment['bankname']) if('bankname' in jsonConfirmPayment) else "XXXX"   #yes
      
      doctortitle = ''
      doctorname = ''
      treatment = ''
      chiefcomplaint = ''
      description = ''
      otherinfo = ''
  
      providerid = 0
      treatmentid = 0
      tplanid = 0
      patientinfo = None
      hmopatientmember = False
      
      
      r = db(db.vw_fonepaise.paymentid == paymentid).select()
      if(len(r)>0):
	  
	  treatmentid = int(common.getid(r[0].treatmentid))
	  tplanid = int(common.getid(r[0].tplanid))
	  providerid = int(common.getid(r[0].providerid))
	  providerinfo  = getproviderinformation(db,providerid)
	  patientinfo = getpatientinformation(db,int(common.getid(r[0].patientid)),int(common.getid(r[0].memberid)))
	  hmopatientmember = patientinfo["hmopatientmember"]
	  
	  doctortitle = common.getstring(r[0].doctortitle)
	  doctorname  = common.getstring(r[0].doctorname)
  
  
	  treatment = common.getstring(r[0].treatment)
	  description = common.getstring(r[0].description)
	  chiefcomplaint = common.getstring(r[0].chiefcomplaint)
	  otherinfo = chiefcomplaint
	      
      db(db.payment.id == paymentid).update(\
      
          fp_paymentref = paymentref,
          fp_paymentdate = datetime.datetime.strptime(paymentdate,"%d/%m/%Y"),
          fp_paymenttype = paymenttype,
          paymentmode = paymentdetail,
          fp_paymentdetail = paymentdetail,
          fp_cardtype = cardtype,
          fp_merchantid = merchantid,
          fp_merchantdisplay = merchantdisplay,
          fp_invoice = invoice,
          fp_invoiceamt = invoiceamt,
          fp_amount = amount,
          amount = amount,
          fp_fee = fee,
          fp_status = status,
          fp_error = error,
          fp_errormsg = errormsg,
          fp_otherinfo = otherinfo
      
      )
      
      totalpaid = 0        
      totpaid = 0
      tottreatmentcost  = 0
      totinspays = 0    
      totaldue = 0
      
      if(status == 'S'):
	  tp = db(db.treatmentplan.id == tplanid).select()
	  if(len(tp)>0):
	      totpaid = float(common.getstring(tp[0].totalpaid))
	      tottreatmentcost = float(common.getstring(tp[0].totaltreatmentcost))
	      totinspays = float(common.getstring(tp[0].totalinspays))
	      totaldue = tottreatmentcost - (totpaid + float(amount) + totinspays)
	      db(db.treatmentplan.id == tplanid).update(
	      totalpaid = totpaid + float(amount),
	      totaldue  = totaldue
	  )
		  
      
      paymentcallbackobj = {
          "todaydate":todaydate,
          "providerid":providerid,
          "practicename":providerinfo["practicename"],
          "providername ":providerinfo["providername"],
          "provideregnon":providerinfo["providerregno"],
          "practiceaddress1":providerinfo["practiceaddress1"],
          "practiceaddress2":providerinfo["practiceaddress2"],
          "practicephone":providerinfo["practicephone"],
          "practiceemail":providerinfo["practiceemail"],
          "patientname":patientinfo["patientname"],
          "patientmember":patientinfo["patientmember"],
          "patientemail":patientinfo["patientemail"],
          "patientcell":patientinfo["patientcell"],
          "patientgender":patientinfo["patientgender"],
          "patientage":patientinfo["patientage"],
          "patientaddress":patientinfo["patientaddress"],
          "groupref":patientinfo["groupref"],
          "companyname":patientinfo["companyname"],
          "planname ":patientinfo["planname"],
          "doctorname ":doctorname,
          "treatment":treatment,
          "fp_paymentref": paymentref,
          "fp_paymentdate":paymentdate,
          "fp_paymenttype":paymenttype,
          "fp_paymentmode":paymentdetail,
          "fp_paymentdetail":paymentdetail,
          "fp_cardtype":cardtype,
          "fp_merchantid":merchantid,
          "fp_merchantdisplay":merchantdisplay,
          "fp_invoice":invoice,
          "fp_invoiceamt":invoiceamt,
          "fp_amount":amount,
          "fp_fee":fee,
          "fp_status":status,
          "fp_error":error,
          "fp_errormsg":errormsg,
          "fp_otherinfo":otherinfo ,           
          "chiefcomplaint":chiefcomplaint,
          "description":description,
          "chequeno":chequeno,
          "acctno":acctno,
          "acctname":acctname,
          "bankname":bankname,
          "totalpaid":totalpaid,
          "tottreatmentcost":tottreatmentcost,
          "totinspays":totinspays,
          "totaldue":totaldue,
          
      }
      
      return json.dumps(paymentcallbackobj)

  #x = return json object newwebmemberprocesspayment
  #amount = x["total"]
  #currency = INR
  #receipt = x["invoice"]
  def createwebmember_razorpay_order(self,amount,currency,receipt,payment_capture="1"):
   
      #logger.loggerpms2.info("Enter Create Webmember Razor Pay Order")
      
  
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
	#logger.loggerpms2.info("Create Webmember Razorpay Order POST Request==>\n")
	#logger.loggerpms2.info(orderurl + " " + json.dumps(getrsaobj))
	
	resp = requests.post(orderurl,json=getrsaobj)
	
	
	if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
  
	  respobj = resp.json() 
	  #logger.loggerpms2.info("Create Webmember Razorpay Order  Response success: " + json.dumps(respobj))
	  
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
	  error_message = "Create Webmember Razorpay Order Error==>\n" + respobj.get("error").get("code","") + ":" + respobj.get("error").get("description","") + "\n" + str(resp.status_code)
	  logger.loggerpms2.info(error_message)
	  jsonresp = {"result":"fail", "error_message":error_message}
	  
      except Exception as e:
	error_message = "Create Webmember RazorPay Order Exception " + str(e)
	logger.loggerpms2.info(error_message)
	
	jsonresp = {
	  "result":"fail",
	  "error_message":error_message
	}
      
	
      return json.dumps(jsonresp)  
 
 
  #"webmemberid" : webmemberid,
  #"txno":str(txno),
  #"txdate":(txdatetime).strftime("%d/%m/%Y"),
  #"invoice":str(txno) + "_" + (txdatetime).strftime("%d/%m/%Y"),
  #"totpremium": str(totpremium),
  #"totcompanypays":str(totcompanypays),
  #"totyoupay":str(totyoupay),
  #"servicetaxes":str(servicetaxes),
  #"swipecharges":str(swipecharges),
  #"total":str(total),
  #"result":"success",
  #"error_message":""  
  #
  #razorpay_order_id is returned from razorpay when createwebmember_razorpay_order is called
  #newpayment is the object returned from newwebmemberprocesspayment

  
  def capturewebmember_razorpay_payment(self,amount,razorpay_id,razorpay_order_id,newpayment):
    #logger.loggerpms2.info("Enter Capture Webmember Razorpay Payment")
    db = self.db
    auth = current.auth     

    orderurl =   self.fp_produrl + "/payments/" + razorpay_id  +"/capture"
    paiseamount = int(amount * 100)
    getrsaobj = {
      "amount":paiseamount
    }
    
    jsonresp = {}
    resp = {}
    try:
      #logger.loggerpms2.info("Capture Webmember Razor Payment  POST Request==>\n")
      #logger.loggerpms2.info(orderurl + " " + json.dumps(getrsaobj))
      
      resp = requests.post(orderurl,json=getrsaobj)
      
      
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
  
	respobj = resp.json() 
  
	#logger.loggerpms2.info("Capture Webmember Razor Payment response success: " + json.dumps(respobj))
	
	respobj["result"] = "success"
	respobj["error_message"] = ""

	props = db(db.urlproperties.id >0 ).select(db.urlproperties.fp_id,\
	                                           db.urlproperties.fp_merchantid,\
	                                           db.urlproperties.fp_merchantdisplay)
	
	payobj = {}
	
	
	
	
	
	payobj["paymenttowards"] = props[0].fp_id if(len(props)==1) else ""
	payobj["GSTIN"] = "29AAJCM5040Q1ZU"
	payobj["payment_reference"] = razorpay_id + "_" + razorpay_order_id  # Payment ID
	payobj["transactionid"] = newpayment["txno"] #Transaction ID
	payobj["merchantid"] = props[0].fp_merchantid if(len(props)==1) else ""
	payobj["merchantdisplay"] = props[0].fp_merchantdisplay if(len(props)==1) else ""
	payobj["billingname"] = ""
	payobj["billingaddress"] = ""
	payobj["premiumamount"] = newpayment["totyoupay"] #Premium Amount 
	payobj["servicetaxes"] = newpayment["servicetaxes"]  #GST
	payobj["swipecharges"] = newpayment["swipecharges"]  #Transaction Charges	
	payobj["amount"] = amount   #Amount Paid  
	payobj["paymentdate"] = newpayment["txdate"] #Payment Date
	payobj["transactionstatus"] =  respobj.get("error_description","") #Transaction Status
	payobj["transactioncode"] = respobj.get("error_code","")  #Transaction Code	
	
	
	
	
	
	
	
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
	
	
	
	payobj["id"] = newpayment["txid"]   
	
	payobj["chequeno"] = "00000"
	payobj["acctno"] = "00000"
	payobj["acctname"] = "XXXX"
	payobj["bankname"] = "XXX"
	payobj["result"]  = "success"
	payobj["error_message"] = ""
	
	#update payment txlog
	#logger.loggerpms2.info("Capture Webmember Razor Payment  updating payment tx log")
	txid = int(common.getid(newpayment["txid"]))
	db(db.paymenttxlog.id == txid).update(\
	  
	  servicetax =  float(newpayment["servicetaxes"]),
	  swipecharge = float(newpayment["swipecharges"]),
	  total = amount,
	  totpremium = float(newpayment["totpremium"]),
	  totcompanypays = float(newpayment["totcompanypays"]),
	  paymentdate = datetime.datetime.strptime(newpayment["txdate"],"%d/%m/%Y"),
	  paymentamount = amount,
	  paymenttxid = newpayment["invoice"],
	  paymentid = razorpay_id + "_" + razorpay_order_id,
	  modified_on = common.getISTFormatCurrentLocatTime(),
	  modified_by =1 if(auth.user == None) else auth.user.id    	)
	
	#logger.loggerpms2.info("Capture Webmember Razor Payment updated payment tx log")
	#update webmember 
	webmemberid = int(common.getid(newpayment["webmemberid"]))
	db(db.webmember.id == webmemberid).update(\
	  status = "Completed",
	  paid = True,
	  modified_on = common.getISTFormatCurrentLocatTime(),
	  modified_by =1 if(auth.user == None) else auth.user.id    	
	
	)
	#logger.loggerpms2.info("Capture Webmember Razor Payment updated payment webmember")
	db(db.webmemberdependants.webmember == webmemberid).update(paid=True)	
	#logger.loggerpms2.info("Capture Webmember Razor Payment updated payment webmemberdependants")
	
	jsonresp = payobj
      else:
        respobj = resp.json() 
	error_message = "Capture Webmember Razorpay Payment Error==>\n" + respobj.get("error").get("code","") + ":" + respobj.get("error").get("description","") + "\n" + str(resp.status_code)
	logger.loggerpms2.info(error_message)
	jsonresp = {"result":"fail", "error_message":error_message}
	
    except Exception as e:
      error_message = "Capture Webmember Razorpay  Payment Exception " + str(e)
      logger.loggerpms2.info(error_message)
      jsonresp = {
        "result":"fail",
        "error_message":error_message
      }
    
      
    return json.dumps(jsonresp)   


  def printpremium_payment_receipt(self,payobj):
   
    return json.dumps(payobj)
 