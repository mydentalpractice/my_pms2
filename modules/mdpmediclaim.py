from gluon import current

import os
import json

import tempfile

import datetime
import time
from datetime import timedelta

from string import Template

from applications.my_pms2.modules import account
from applications.my_pms2.modules import status
from applications.my_pms2.modules import common
from applications.my_pms2.modules import mail
from applications.my_pms2.modules import tasks
from applications.my_pms2.modules import logger

datefmt = "%d/%m/%Y"
datetimefmt = "%d/%m/%Y %H:%M:%S"


def findnode(procedureid,treatmentprocedureid,procedurelist):
  
  for p in procedurelist:
    
    if((p["procedureid"] == procedureid) & (p["treatmentprocedureid"]==treatmentprocedureid)):
      return True
    
  
  return False

class Mediclaim:
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    return
  
  def dummy(self):
    
    db = self.db
    auth = current.auth
    
    try:
      i = 0
      
    except Exception as e:
        error_message = "Add Mediclaim Procedures Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return
  

 


  
  def updatemediclaimprocedure(self,mediclaimid,procedureid,treatmentprocedureid,mediclaim_procedure_id,procdate,tooth,description,quantity,cashless,status):
     
    db = self.db
    auth = current.auth
    
    try:
      
      db((db.mediclaim_procedures.id == mediclaim_procedure_id) & \
         (db.mediclaim_procedures.mediclaimid == mediclaimid) & \
         (db.mediclaim_procedures.procedureid == procedureid) & \
         (db.mediclaim_procedures.treatmentprocedureid == treatmentprocedureid) & \
         (db.mediclaim_procedures.is_active == True)).update(\
        procdate = datetime.datetime.strptime(procdate,"%d/%m/%Y"),
        tooth=tooth,
        description=description,
        quantity=quantity,
        cashless=cashless,
        status=status,        
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by =1 if(auth.user == None) else auth.user.id              
      )
      
      return json.dumps({"result":"success","error_message":""})
    
    except Exception as e:
        error_message = "Update Mediclaim Procedures Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return  

  
  
  #this method adds procedure to mediclaim
  #procedureid points to id of dentalprocedure table
  def addmediclaimprocedure(self,mediclaimid,procedureid,treatmentprocedureid,procdate,tooth,description,quantity,cashless,status):
    
    db = self.db
    auth = current.auth
    
    try:
      
      claimprocedureid = db.mediclaim_procedures.insert(
      
        mediclaimid = mediclaimid,
        procedureid = procedureid,
        treatmentprocedureid = treatmentprocedureid,
        procdate = datetime.datetime.strptime(procdate,"%d/%m/%Y"),
        tooth=tooth,
        description=description,
        quantity=quantity,
        cashless=cashless,
        status=status,
        is_active = True,
        created_on = common.getISTFormatCurrentLocatTime(),
        created_by = 1 if(auth.user == None) else auth.user.id,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by =1 if(auth.user == None) else auth.user.id        

      )
      
      return json.dumps({"result":"success","error_message":"","claimprocedureid":str(claimprocedureid)})
      
    except Exception as e:
        error_message = "Add Mediclaim Procedures API Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return
  
  def deletemediclaimprocedure(self,mediclaimprocedureid):
    
    db = self.db
    auth = current.auth
    
    try:
      db((db.mediclaim_procedures.id == mediclaimprocedureid)).update(\
        is_active = False,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by =1 if(auth.user == None) else auth.user.id              
      
      )
      
    except Exception as e:
        error_message = "Delete Mediclaim Procedure API Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return  
 
 
  def getmediclaimprocedure(self,mediclaimprocedureid):
    
    db = self.db
    auth = current.auth
    
    try:
      procs = db((db.mediclaim_procedures.id == mediclaimprocedureid)&\
                 (db.mediclaim_procedures.is_active == True)).select()
      procobj = {}
      
      if(len(procs)==1):
        proc=procs[0]
        procobj["procedureid"]=proc.procedureid
        procobj["treatmentprocedureid"]=proc.treatmentprocedureid
        procobj["description"]=proc.description
        procobj["procdate"]=(proc.procdate).strftime("%d/%m/%Y")
        procobj["tooth"]=proc.tooth
        procobj["status"]=proc.status
        procobj["cashless"]=proc.cashless
        procobj["quantity"]=proc.quantity
        procobj["result"]="success"
        procobj["error_message"]=""
        
      else:
        procobj = {"result":"fail","error_message":"No Procedures for this Claim"}
          
  
      return json.dumps(procobj)
      
    except Exception as e:
        error_message = "Get Mediclaim Procedure Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return
  
   
 
  #get two list of procedures for the treatment associated with this claim
  #first lists all procedures associated with this treatment referred by the claim
  #second lists all procedures assigned to the claim
  def getmediclaimprocedures(self,treatmentid,mediclaimid):
    
    db = self.db
   
    
    trtmntproclist  = []
    claimproclist = []
    procobj = {}
    
    
    try:
      procs = db((db.mediclaim_procedures.mediclaimid == mediclaimid)&(db.mediclaim_procedures.is_active == True)).select()
      for proc in procs:
        procobj = {
          "mediclaimprocedureid":int(common.getid(proc.id)),
          "procedureid":int(common.getid(proc.procedureid)),
          "treatmentprocedureid":int(common.getid(proc.treatmentprocedureid)),
          "description":proc.description,
          "procdate":(proc.procdate).strftime("%d/%m/%Y"),
          "tooth":proc.tooth,
          "status":proc.status,
          "cashless":proc.cashless,
          "quantity":proc.quantity
          
        }
        
        claimproclist.append(procobj)
        
      treatmentprocs = db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.is_active == True)).select(db.treatment_procedure.id,db.treatment_procedure.tooth,\
                                                                                                                                 db.treatment_procedure.status,\
                                                                                                                                 db.treatment_procedure.treatmentdate,\
                                                                                                                                 db.vw_procedurepriceplan.procedureid,\
                                                                                                                                 db.vw_procedurepriceplan.description,\
                                                                                                                                 left=db.vw_procedurepriceplan.on(db.vw_procedurepriceplan.id == db.treatment_procedure.dentalprocedure))
             
      for proc in treatmentprocs:
        if(not findnode(proc.vw_procedurepriceplan.procedureid, proc.treatment_procedure.id, claimproclist)):
          procobj = {
            "mediclaimprocedureid":0,
            "treatmentprocedureid":proc.treatment_procedure.id,
            "procedureid":proc.vw_procedurepriceplan.procedureid,
            "description":proc.vw_procedurepriceplan.description,
            "procdate":(proc.treatment_procedure.treatmentdate).strftime("%d/%m/%Y"),
            "tooth":proc.treatment_procedure.tooth,
            "status":proc.treatment_procedure.status,
            "cashless":"",
            "quantity":""
            
          }
          trtmntproclist.append(procobj)        

    
    except Exception as e:
      error_message = "Get Mediclaim Procedures Exception Error - " + str(e)
      logger.loggerpms2.info(error_message)
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = error_message
      return json.dumps(excpobj)
             
    return json.dumps({"result":"success","error_message":"", "treatmentid":str(treatmentid),"mediclaimid":str(mediclaimid),"treatmentprocedures":trtmntproclist,"mediclaimprocedures":claimproclist})
    
    
    
    
  def addmediclaimcharts(self,mediclaimid,charts):
      
      db = self.db
      auth = current.auth
      
      ochart = charts["charts"]
      
      try:
        
        db.mediclaim_charts.update_or_insert((db.mediclaim_charts.mediclaimid == mediclaimid),
          mediclaimid = mediclaimid, 
          restoration_ul_1=ochart["restoration_ul_1"] if "restoration_ul_1" in ochart else False, 
          restoration_ul_2=ochart["restoration_ul_2"] if "restoration_ul_2" in ochart else False, 
          restoration_ul_3=ochart["restoration_ul_3"] if "restoration_ul_3" in ochart else False, 
          restoration_ul_4=ochart["restoration_ul_4"] if "restoration_ul_4" in ochart else False, 
          restoration_ul_5=ochart["restoration_ul_5"] if "restoration_ul_5" in ochart else False, 
          restoration_ul_6=ochart["restoration_ul_6"] if "restoration_ul_6" in ochart else False, 
          restoration_ul_7=ochart["restoration_ul_7"] if "restoration_ul_7" in ochart else False, 
          restoration_ul_8=ochart["restoration_ul_8"] if "restoration_ul_8" in ochart else False, 
          restoration_ur_1=ochart["restoration_ur_1"] if "restoration_ur_1" in ochart else False, 
          restoration_ur_2=ochart["restoration_ur_2"] if "restoration_ur_2" in ochart else False, 
          restoration_ur_3=ochart["restoration_ur_3"] if "restoration_ur_3" in ochart else False, 
          restoration_ur_4=ochart["restoration_ur_4"] if "restoration_ur_4" in ochart else False, 
          restoration_ur_5=ochart["restoration_ur_5"] if "restoration_ur_5" in ochart else False, 
          restoration_ur_6=ochart["restoration_ur_6"] if "restoration_ur_6" in ochart else False, 
          restoration_ur_7=ochart["restoration_ur_7"] if "restoration_ur_7" in ochart else False, 
          restoration_ur_8=ochart["restoration_ur_8"] if "restoration_ur_8" in ochart else False, 
          restoration_ll_1=ochart["restoration_ll_1"] if "restoration_ll_1" in ochart else False, 
          restoration_ll_2=ochart["restoration_ll_2"] if "restoration_ll_2" in ochart else False, 
          restoration_ll_3=ochart["restoration_ll_3"] if "restoration_ll_3" in ochart else False, 
          restoration_ll_4=ochart["restoration_ll_4"] if "restoration_ll_4" in ochart else False, 
          restoration_ll_5=ochart["restoration_ll_5"] if "restoration_ll_5" in ochart else False, 
          restoration_ll_6=ochart["restoration_ll_6"] if "restoration_ll_6" in ochart else False, 
          restoration_ll_7=ochart["restoration_ll_7"] if "restoration_ll_7" in ochart else False, 
          restoration_ll_8=ochart["restoration_ll_8"] if "restoration_ll_8" in ochart else False, 
          restoration_lr_1=ochart["restoration_lr_1"] if "restoration_lr_1" in ochart else False, 
          restoration_lr_2=ochart["restoration_lr_2"] if "restoration_lr_2" in ochart else False, 
          restoration_lr_3=ochart["restoration_lr_3"] if "restoration_lr_3" in ochart else False, 
          restoration_lr_4=ochart["restoration_lr_4"] if "restoration_lr_4" in ochart else False, 
          restoration_lr_5=ochart["restoration_lr_5"] if "restoration_lr_5" in ochart else False, 
          restoration_lr_6=ochart["restoration_lr_6"] if "restoration_lr_6" in ochart else False, 
          restoration_lr_7=ochart["restoration_lr_7"] if "restoration_lr_7" in ochart else False, 
          restoration_lr_8=ochart["restoration_lr_8"] if "restoration_lr_8" in ochart else False, 
          rootcanal_ul_1=ochart["rootcanal_ul_1"] if "rootcanal_ul_1" in ochart else False, 
          rootcanal_ul_2=ochart["rootcanal_ul_2"] if "rootcanal_ul_2" in ochart else False, 
          rootcanal_ul_3=ochart["rootcanal_ul_3"] if "rootcanal_ul_3" in ochart else False, 
          rootcanal_ul_4=ochart["rootcanal_ul_4"] if "rootcanal_ul_4" in ochart else False, 
          rootcanal_ul_5=ochart["rootcanal_ul_5"] if "rootcanal_ul_5" in ochart else False, 
          rootcanal_ul_6=ochart["rootcanal_ul_6"] if "rootcanal_ul_6" in ochart else False, 
          rootcanal_ul_7=ochart["rootcanal_ul_7"] if "rootcanal_ul_7" in ochart else False, 
          rootcanal_ul_8=ochart["rootcanal_ul_8"] if "rootcanal_ul_8" in ochart else False, 
          rootcanal_ur_1=ochart["rootcanal_ur_1"] if "rootcanal_ur_1" in ochart else False, 
          rootcanal_ur_2=ochart["rootcanal_ur_2"] if "rootcanal_ur_2" in ochart else False, 
          rootcanal_ur_3=ochart["rootcanal_ur_3"] if "rootcanal_ur_3" in ochart else False, 
          rootcanal_ur_4=ochart["rootcanal_ur_4"] if "rootcanal_ur_4" in ochart else False, 
          rootcanal_ur_5=ochart["rootcanal_ur_5"] if "rootcanal_ur_5" in ochart else False, 
          rootcanal_ur_6=ochart["rootcanal_ur_6"] if "rootcanal_ur_6" in ochart else False, 
          rootcanal_ur_7=ochart["rootcanal_ur_7"] if "rootcanal_ur_7" in ochart else False, 
          rootcanal_ur_8=ochart["rootcanal_ur_8"] if "rootcanal_ur_8" in ochart else False, 
          rootcanal_ll_1=ochart["rootcanal_ll_1"] if "rootcanal_ll_1" in ochart else False, 
          rootcanal_ll_2=ochart["rootcanal_ll_2"] if "rootcanal_ll_2" in ochart else False, 
          rootcanal_ll_3=ochart["rootcanal_ll_3"] if "rootcanal_ll_3" in ochart else False, 
          rootcanal_ll_4=ochart["rootcanal_ll_4"] if "rootcanal_ll_4" in ochart else False, 
          rootcanal_ll_5=ochart["rootcanal_ll_5"] if "rootcanal_ll_5" in ochart else False, 
          rootcanal_ll_6=ochart["rootcanal_ll_6"] if "rootcanal_ll_6" in ochart else False, 
          rootcanal_ll_7=ochart["rootcanal_ll_7"] if "rootcanal_ll_7" in ochart else False, 
          rootcanal_ll_8=ochart["rootcanal_ll_8"] if "rootcanal_ll_8" in ochart else False, 
          rootcanal_lr_1=ochart["rootcanal_lr_1"] if "rootcanal_lr_1" in ochart else False, 
          rootcanal_lr_2=ochart["rootcanal_lr_2"] if "rootcanal_lr_2" in ochart else False, 
          rootcanal_lr_3=ochart["rootcanal_lr_3"] if "rootcanal_lr_3" in ochart else False, 
          rootcanal_lr_4=ochart["rootcanal_lr_4"] if "rootcanal_lr_4" in ochart else False, 
          rootcanal_lr_5=ochart["rootcanal_lr_5"] if "rootcanal_lr_5" in ochart else False, 
          rootcanal_lr_6=ochart["rootcanal_lr_6"] if "rootcanal_lr_6" in ochart else False, 
          rootcanal_lr_7=ochart["rootcanal_lr_7"] if "rootcanal_lr_7" in ochart else False, 
          rootcanal_lr_8=ochart["rootcanal_lr_8"] if "rootcanal_lr_8" in ochart else False, 
          extract_ul_1=ochart["extract_ul_1"] if "extract_ul_1" in ochart else False, 
          extract_ul_2=ochart["extract_ul_2"] if "extract_ul_2" in ochart else False, 
          extract_ul_3=ochart["extract_ul_3"] if "extract_ul_3" in ochart else False, 
          extract_ul_4=ochart["extract_ul_4"] if "extract_ul_4" in ochart else False, 
          extract_ul_5=ochart["extract_ul_5"] if "extract_ul_5" in ochart else False, 
          extract_ul_6=ochart["extract_ul_6"] if "extract_ul_6" in ochart else False, 
          extract_ul_7=ochart["extract_ul_7"] if "extract_ul_7" in ochart else False, 
          extract_ul_8=ochart["extract_ul_8"] if "extract_ul_8" in ochart else False, 
          extract_ur_1=ochart["extract_ur_1"] if "extract_ur_1" in ochart else False, 
          extract_ur_2=ochart["extract_ur_2"] if "extract_ur_2" in ochart else False, 
          extract_ur_3=ochart["extract_ur_3"] if "extract_ur_3" in ochart else False, 
          extract_ur_4=ochart["extract_ur_4"] if "extract_ur_4" in ochart else False, 
          extract_ur_5=ochart["extract_ur_5"] if "extract_ur_5" in ochart else False, 
          extract_ur_6=ochart["extract_ur_6"] if "extract_ur_6" in ochart else False, 
          extract_ur_7=ochart["extract_ur_7"] if "extract_ur_7" in ochart else False, 
          extract_ur_8=ochart["extract_ur_8"] if "extract_ur_8" in ochart else False, 
          extract_ll_1=ochart["extract_ll_1"] if "extract_ll_1" in ochart else False, 
          extract_ll_2=ochart["extract_ll_2"] if "extract_ll_2" in ochart else False, 
          extract_ll_3=ochart["extract_ll_3"] if "extract_ll_3" in ochart else False, 
          extract_ll_4=ochart["extract_ll_4"] if "extract_ll_4" in ochart else False, 
          extract_ll_5=ochart["extract_ll_5"] if "extract_ll_5" in ochart else False, 
          extract_ll_6=ochart["extract_ll_6"] if "extract_ll_6" in ochart else False, 
          extract_ll_7=ochart["extract_ll_7"] if "extract_ll_7" in ochart else False, 
          extract_ll_8=ochart["extract_ll_8"] if "extract_ll_8" in ochart else False, 
          extract_lr_1=ochart["extract_lr_1"] if "extract_lr_1" in ochart else False, 
          extract_lr_2=ochart["extract_lr_2"] if "extract_lr_2" in ochart else False, 
          extract_lr_3=ochart["extract_lr_3"] if "extract_lr_3" in ochart else False, 
          extract_lr_4=ochart["extract_lr_4"] if "extract_lr_4" in ochart else False, 
          extract_lr_5=ochart["extract_lr_5"] if "extract_lr_5" in ochart else False, 
          extract_lr_6=ochart["extract_lr_6"] if "extract_lr_6" in ochart else False, 
          extract_lr_7=ochart["extract_lr_7"] if "extract_lr_7" in ochart else False, 
          extract_lr_8=ochart["extract_lr_8"] if "extract_lr_8" in ochart else False, 
          missing_ul_1=ochart["missing_ul_1"] if "missing_ul_1" in ochart else False, 
          missing_ul_2=ochart["missing_ul_2"] if "missing_ul_2" in ochart else False, 
          missing_ul_3=ochart["missing_ul_3"] if "missing_ul_3" in ochart else False, 
          missing_ul_4=ochart["missing_ul_4"] if "missing_ul_4" in ochart else False, 
          missing_ul_5=ochart["missing_ul_5"] if "missing_ul_5" in ochart else False, 
          missing_ul_6=ochart["missing_ul_6"] if "missing_ul_6" in ochart else False, 
          missing_ul_7=ochart["missing_ul_7"] if "missing_ul_7" in ochart else False, 
          missing_ul_8=ochart["missing_ul_8"] if "missing_ul_8" in ochart else False, 
          missing_ur_1=ochart["missing_ur_1"] if "missing_ur_1" in ochart else False, 
          missing_ur_2=ochart["missing_ur_2"] if "missing_ur_2" in ochart else False, 
          missing_ur_3=ochart["missing_ur_3"] if "missing_ur_3" in ochart else False, 
          missing_ur_4=ochart["missing_ur_4"] if "missing_ur_4" in ochart else False, 
          missing_ur_5=ochart["missing_ur_5"] if "missing_ur_5" in ochart else False, 
          missing_ur_6=ochart["missing_ur_6"] if "missing_ur_6" in ochart else False, 
          missing_ur_7=ochart["missing_ur_7"] if "missing_ur_7" in ochart else False, 
          missing_ur_8=ochart["missing_ur_8"] if "missing_ur_8" in ochart else False, 
          missing_ll_1=ochart["missing_ll_1"] if "missing_ll_1" in ochart else False, 
          missing_ll_2=ochart["missing_ll_2"] if "missing_ll_2" in ochart else False, 
          missing_ll_3=ochart["missing_ll_3"] if "missing_ll_3" in ochart else False, 
          missing_ll_4=ochart["missing_ll_4"] if "missing_ll_4" in ochart else False, 
          missing_ll_5=ochart["missing_ll_5"] if "missing_ll_5" in ochart else False, 
          missing_ll_6=ochart["missing_ll_6"] if "missing_ll_6" in ochart else False, 
          missing_ll_7=ochart["missing_ll_7"] if "missing_ll_7" in ochart else False, 
          missing_ll_8=ochart["missing_ll_8"] if "missing_ll_8" in ochart else False, 
          missing_lr_1=ochart["missing_lr_1"] if "missing_lr_1" in ochart else False, 
          missing_lr_2=ochart["missing_lr_2"] if "missing_lr_2" in ochart else False, 
          missing_lr_3=ochart["missing_lr_3"] if "missing_lr_3" in ochart else False, 
          missing_lr_4=ochart["missing_lr_4"] if "missing_lr_4" in ochart else False, 
          missing_lr_5=ochart["missing_lr_5"] if "missing_lr_5" in ochart else False, 
          missing_lr_6=ochart["missing_lr_6"] if "missing_lr_6" in ochart else False, 
          missing_lr_7=ochart["missing_lr_7"] if "missing_lr_7" in ochart else False, 
          missing_lr_8=ochart["missing_lr_8"] if "missing_lr_8" in ochart else False, 
          xray_ul_1=ochart["xray_ul_1"] if "xray_ul_1" in ochart else False, 
          xray_ul_2=ochart["xray_ul_2"] if "xray_ul_2" in ochart else False, 
          xray_ul_3=ochart["xray_ul_3"] if "xray_ul_3" in ochart else False, 
          xray_ul_4=ochart["xray_ul_4"] if "xray_ul_4" in ochart else False, 
          xray_ul_5=ochart["xray_ul_5"] if "xray_ul_5" in ochart else False, 
          xray_ul_6=ochart["xray_ul_6"] if "xray_ul_6" in ochart else False, 
          xray_ul_7=ochart["xray_ul_7"] if "xray_ul_7" in ochart else False, 
          xray_ul_8=ochart["xray_ul_8"] if "xray_ul_8" in ochart else False, 
          xray_ur_1=ochart["xray_ur_1"] if "xray_ur_1" in ochart else False, 
          xray_ur_2=ochart["xray_ur_2"] if "xray_ur_2" in ochart else False, 
          xray_ur_3=ochart["xray_ur_3"] if "xray_ur_3" in ochart else False, 
          xray_ur_4=ochart["xray_ur_4"] if "xray_ur_4" in ochart else False, 
          xray_ur_5=ochart["xray_ur_5"] if "xray_ur_5" in ochart else False, 
          xray_ur_6=ochart["xray_ur_6"] if "xray_ur_6" in ochart else False, 
          xray_ur_7=ochart["xray_ur_7"] if "xray_ur_7" in ochart else False, 
          xray_ur_8=ochart["xray_ur_8"] if "xray_ur_8" in ochart else False, 
          xray_ll_1=ochart["xray_ll_1"] if "xray_ll_1" in ochart else False, 
          xray_ll_2=ochart["xray_ll_2"] if "xray_ll_2" in ochart else False, 
          xray_ll_3=ochart["xray_ll_3"] if "xray_ll_3" in ochart else False, 
          xray_ll_4=ochart["xray_ll_4"] if "xray_ll_4" in ochart else False, 
          xray_ll_5=ochart["xray_ll_5"] if "xray_ll_5" in ochart else False, 
          xray_ll_6=ochart["xray_ll_6"] if "xray_ll_6" in ochart else False, 
          xray_ll_7=ochart["xray_ll_7"] if "xray_ll_7" in ochart else False, 
          xray_ll_8=ochart["xray_ll_8"] if "xray_ll_8" in ochart else False, 
          xray_lr_1=ochart["xray_lr_1"] if "xray_lr_1" in ochart else False, 
          xray_lr_2=ochart["xray_lr_2"] if "xray_lr_2" in ochart else False, 
          xray_lr_3=ochart["xray_lr_3"] if "xray_lr_3" in ochart else False, 
          xray_lr_4=ochart["xray_lr_4"] if "xray_lr_4" in ochart else False, 
          xray_lr_5=ochart["xray_lr_5"] if "xray_lr_5" in ochart else False, 
          xray_lr_6=ochart["xray_lr_6"] if "xray_lr_6" in ochart else False, 
          xray_lr_7=ochart["xray_lr_7"] if "xray_lr_7" in ochart else False, 
          xray_lr_8=ochart["xray_lr_8"] if "xray_lr_8" in ochart else False, 
          is_active = True,
          created_on = common.getISTFormatCurrentLocatTime(),
          created_by = 1 if(auth.user == None) else auth.user.id,
          modified_on = common.getISTFormatCurrentLocatTime(),
          modified_by =1 if(auth.user == None) else auth.user.id        
        
        
        )
        
        return json.dumps({"result":"success","error_message":""})
        
      except Exception as e:
          error_message = "Add Mediclaim Charts Exception Error - " + str(e)
          logger.loggerpms2.info(error_message)
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = error_message
          return json.dumps(excpobj)    
      
      return
    
  
 
   
  def updatemediclaimcharts(self,mediclaimid,charts):
      
      db = self.db
      auth = current.auth
      
      try:
        
        ochart = charts["charts"]
        
        
        
        
        chartsid = db(db.mediclaim_charts.mediclaimid == mediclaimid).update(\
          
        
          restoration_ul_1=ochart["restoration_ul_1"] if "restoration_ul_1" in ochart else False, 
          restoration_ul_2=ochart["restoration_ul_2"] if "restoration_ul_2" in ochart else False, 
          restoration_ul_3=ochart["restoration_ul_3"] if "restoration_ul_3" in ochart else False, 
          restoration_ul_4=ochart["restoration_ul_4"] if "restoration_ul_4" in ochart else False, 
          restoration_ul_5=ochart["restoration_ul_5"] if "restoration_ul_5" in ochart else False, 
          restoration_ul_6=ochart["restoration_ul_6"] if "restoration_ul_6" in ochart else False, 
          restoration_ul_7=ochart["restoration_ul_7"] if "restoration_ul_7" in ochart else False, 
          restoration_ul_8=ochart["restoration_ul_8"] if "restoration_ul_8" in ochart else False, 
          restoration_ur_1=ochart["restoration_ur_1"] if "restoration_ur_1" in ochart else False, 
          restoration_ur_2=ochart["restoration_ur_2"] if "restoration_ur_2" in ochart else False, 
          restoration_ur_3=ochart["restoration_ur_3"] if "restoration_ur_3" in ochart else False, 
          restoration_ur_4=ochart["restoration_ur_4"] if "restoration_ur_4" in ochart else False, 
          restoration_ur_5=ochart["restoration_ur_5"] if "restoration_ur_5" in ochart else False, 
          restoration_ur_6=ochart["restoration_ur_6"] if "restoration_ur_6" in ochart else False, 
          restoration_ur_7=ochart["restoration_ur_7"] if "restoration_ur_7" in ochart else False, 
          restoration_ur_8=ochart["restoration_ur_8"] if "restoration_ur_8" in ochart else False, 
          restoration_ll_1=ochart["restoration_ll_1"] if "restoration_ll_1" in ochart else False, 
          restoration_ll_2=ochart["restoration_ll_2"] if "restoration_ll_2" in ochart else False, 
          restoration_ll_3=ochart["restoration_ll_3"] if "restoration_ll_3" in ochart else False, 
          restoration_ll_4=ochart["restoration_ll_4"] if "restoration_ll_4" in ochart else False, 
          restoration_ll_5=ochart["restoration_ll_5"] if "restoration_ll_5" in ochart else False, 
          restoration_ll_6=ochart["restoration_ll_6"] if "restoration_ll_6" in ochart else False, 
          restoration_ll_7=ochart["restoration_ll_7"] if "restoration_ll_7" in ochart else False, 
          restoration_ll_8=ochart["restoration_ll_8"] if "restoration_ll_8" in ochart else False, 
          restoration_lr_1=ochart["restoration_lr_1"] if "restoration_lr_1" in ochart else False, 
          restoration_lr_2=ochart["restoration_lr_2"] if "restoration_lr_2" in ochart else False, 
          restoration_lr_3=ochart["restoration_lr_3"] if "restoration_lr_3" in ochart else False, 
          restoration_lr_4=ochart["restoration_lr_4"] if "restoration_lr_4" in ochart else False, 
          restoration_lr_5=ochart["restoration_lr_5"] if "restoration_lr_5" in ochart else False, 
          restoration_lr_6=ochart["restoration_lr_6"] if "restoration_lr_6" in ochart else False, 
          restoration_lr_7=ochart["restoration_lr_7"] if "restoration_lr_7" in ochart else False, 
          restoration_lr_8=ochart["restoration_lr_8"] if "restoration_lr_8" in ochart else False, 
          rootcanal_ul_1=ochart["rootcanal_ul_1"] if "rootcanal_ul_1" in ochart else False, 
          rootcanal_ul_2=ochart["rootcanal_ul_2"] if "rootcanal_ul_2" in ochart else False, 
          rootcanal_ul_3=ochart["rootcanal_ul_3"] if "rootcanal_ul_3" in ochart else False, 
          rootcanal_ul_4=ochart["rootcanal_ul_4"] if "rootcanal_ul_4" in ochart else False, 
          rootcanal_ul_5=ochart["rootcanal_ul_5"] if "rootcanal_ul_5" in ochart else False, 
          rootcanal_ul_6=ochart["rootcanal_ul_6"] if "rootcanal_ul_6" in ochart else False, 
          rootcanal_ul_7=ochart["rootcanal_ul_7"] if "rootcanal_ul_7" in ochart else False, 
          rootcanal_ul_8=ochart["rootcanal_ul_8"] if "rootcanal_ul_8" in ochart else False, 
          rootcanal_ur_1=ochart["rootcanal_ur_1"] if "rootcanal_ur_1" in ochart else False, 
          rootcanal_ur_2=ochart["rootcanal_ur_2"] if "rootcanal_ur_2" in ochart else False, 
          rootcanal_ur_3=ochart["rootcanal_ur_3"] if "rootcanal_ur_3" in ochart else False, 
          rootcanal_ur_4=ochart["rootcanal_ur_4"] if "rootcanal_ur_4" in ochart else False, 
          rootcanal_ur_5=ochart["rootcanal_ur_5"] if "rootcanal_ur_5" in ochart else False, 
          rootcanal_ur_6=ochart["rootcanal_ur_6"] if "rootcanal_ur_6" in ochart else False, 
          rootcanal_ur_7=ochart["rootcanal_ur_7"] if "rootcanal_ur_7" in ochart else False, 
          rootcanal_ur_8=ochart["rootcanal_ur_8"] if "rootcanal_ur_8" in ochart else False, 
          rootcanal_ll_1=ochart["rootcanal_ll_1"] if "rootcanal_ll_1" in ochart else False, 
          rootcanal_ll_2=ochart["rootcanal_ll_2"] if "rootcanal_ll_2" in ochart else False, 
          rootcanal_ll_3=ochart["rootcanal_ll_3"] if "rootcanal_ll_3" in ochart else False, 
          rootcanal_ll_4=ochart["rootcanal_ll_4"] if "rootcanal_ll_4" in ochart else False, 
          rootcanal_ll_5=ochart["rootcanal_ll_5"] if "rootcanal_ll_5" in ochart else False, 
          rootcanal_ll_6=ochart["rootcanal_ll_6"] if "rootcanal_ll_6" in ochart else False, 
          rootcanal_ll_7=ochart["rootcanal_ll_7"] if "rootcanal_ll_7" in ochart else False, 
          rootcanal_ll_8=ochart["rootcanal_ll_8"] if "rootcanal_ll_8" in ochart else False, 
          rootcanal_lr_1=ochart["rootcanal_lr_1"] if "rootcanal_lr_1" in ochart else False, 
          rootcanal_lr_2=ochart["rootcanal_lr_2"] if "rootcanal_lr_2" in ochart else False, 
          rootcanal_lr_3=ochart["rootcanal_lr_3"] if "rootcanal_lr_3" in ochart else False, 
          rootcanal_lr_4=ochart["rootcanal_lr_4"] if "rootcanal_lr_4" in ochart else False, 
          rootcanal_lr_5=ochart["rootcanal_lr_5"] if "rootcanal_lr_5" in ochart else False, 
          rootcanal_lr_6=ochart["rootcanal_lr_6"] if "rootcanal_lr_6" in ochart else False, 
          rootcanal_lr_7=ochart["rootcanal_lr_7"] if "rootcanal_lr_7" in ochart else False, 
          rootcanal_lr_8=ochart["rootcanal_lr_8"] if "rootcanal_lr_8" in ochart else False, 
          extract_ul_1=ochart["extract_ul_1"] if "extract_ul_1" in ochart else False, 
          extract_ul_2=ochart["extract_ul_2"] if "extract_ul_2" in ochart else False, 
          extract_ul_3=ochart["extract_ul_3"] if "extract_ul_3" in ochart else False, 
          extract_ul_4=ochart["extract_ul_4"] if "extract_ul_4" in ochart else False, 
          extract_ul_5=ochart["extract_ul_5"] if "extract_ul_5" in ochart else False, 
          extract_ul_6=ochart["extract_ul_6"] if "extract_ul_6" in ochart else False, 
          extract_ul_7=ochart["extract_ul_7"] if "extract_ul_7" in ochart else False, 
          extract_ul_8=ochart["extract_ul_8"] if "extract_ul_8" in ochart else False, 
          extract_ur_1=ochart["extract_ur_1"] if "extract_ur_1" in ochart else False, 
          extract_ur_2=ochart["extract_ur_2"] if "extract_ur_2" in ochart else False, 
          extract_ur_3=ochart["extract_ur_3"] if "extract_ur_3" in ochart else False, 
          extract_ur_4=ochart["extract_ur_4"] if "extract_ur_4" in ochart else False, 
          extract_ur_5=ochart["extract_ur_5"] if "extract_ur_5" in ochart else False, 
          extract_ur_6=ochart["extract_ur_6"] if "extract_ur_6" in ochart else False, 
          extract_ur_7=ochart["extract_ur_7"] if "extract_ur_7" in ochart else False, 
          extract_ur_8=ochart["extract_ur_8"] if "extract_ur_8" in ochart else False, 
          extract_ll_1=ochart["extract_ll_1"] if "extract_ll_1" in ochart else False, 
          extract_ll_2=ochart["extract_ll_2"] if "extract_ll_2" in ochart else False, 
          extract_ll_3=ochart["extract_ll_3"] if "extract_ll_3" in ochart else False, 
          extract_ll_4=ochart["extract_ll_4"] if "extract_ll_4" in ochart else False, 
          extract_ll_5=ochart["extract_ll_5"] if "extract_ll_5" in ochart else False, 
          extract_ll_6=ochart["extract_ll_6"] if "extract_ll_6" in ochart else False, 
          extract_ll_7=ochart["extract_ll_7"] if "extract_ll_7" in ochart else False, 
          extract_ll_8=ochart["extract_ll_8"] if "extract_ll_8" in ochart else False, 
          extract_lr_1=ochart["extract_lr_1"] if "extract_lr_1" in ochart else False, 
          extract_lr_2=ochart["extract_lr_2"] if "extract_lr_2" in ochart else False, 
          extract_lr_3=ochart["extract_lr_3"] if "extract_lr_3" in ochart else False, 
          extract_lr_4=ochart["extract_lr_4"] if "extract_lr_4" in ochart else False, 
          extract_lr_5=ochart["extract_lr_5"] if "extract_lr_5" in ochart else False, 
          extract_lr_6=ochart["extract_lr_6"] if "extract_lr_6" in ochart else False, 
          extract_lr_7=ochart["extract_lr_7"] if "extract_lr_7" in ochart else False, 
          extract_lr_8=ochart["extract_lr_8"] if "extract_lr_8" in ochart else False, 
          missing_ul_1=ochart["missing_ul_1"] if "missing_ul_1" in ochart else False, 
          missing_ul_2=ochart["missing_ul_2"] if "missing_ul_2" in ochart else False, 
          missing_ul_3=ochart["missing_ul_3"] if "missing_ul_3" in ochart else False, 
          missing_ul_4=ochart["missing_ul_4"] if "missing_ul_4" in ochart else False, 
          missing_ul_5=ochart["missing_ul_5"] if "missing_ul_5" in ochart else False, 
          missing_ul_6=ochart["missing_ul_6"] if "missing_ul_6" in ochart else False, 
          missing_ul_7=ochart["missing_ul_7"] if "missing_ul_7" in ochart else False, 
          missing_ul_8=ochart["missing_ul_8"] if "missing_ul_8" in ochart else False, 
          missing_ur_1=ochart["missing_ur_1"] if "missing_ur_1" in ochart else False, 
          missing_ur_2=ochart["missing_ur_2"] if "missing_ur_2" in ochart else False, 
          missing_ur_3=ochart["missing_ur_3"] if "missing_ur_3" in ochart else False, 
          missing_ur_4=ochart["missing_ur_4"] if "missing_ur_4" in ochart else False, 
          missing_ur_5=ochart["missing_ur_5"] if "missing_ur_5" in ochart else False, 
          missing_ur_6=ochart["missing_ur_6"] if "missing_ur_6" in ochart else False, 
          missing_ur_7=ochart["missing_ur_7"] if "missing_ur_7" in ochart else False, 
          missing_ur_8=ochart["missing_ur_8"] if "missing_ur_8" in ochart else False, 
          missing_ll_1=ochart["missing_ll_1"] if "missing_ll_1" in ochart else False, 
          missing_ll_2=ochart["missing_ll_2"] if "missing_ll_2" in ochart else False, 
          missing_ll_3=ochart["missing_ll_3"] if "missing_ll_3" in ochart else False, 
          missing_ll_4=ochart["missing_ll_4"] if "missing_ll_4" in ochart else False, 
          missing_ll_5=ochart["missing_ll_5"] if "missing_ll_5" in ochart else False, 
          missing_ll_6=ochart["missing_ll_6"] if "missing_ll_6" in ochart else False, 
          missing_ll_7=ochart["missing_ll_7"] if "missing_ll_7" in ochart else False, 
          missing_ll_8=ochart["missing_ll_8"] if "missing_ll_8" in ochart else False, 
          missing_lr_1=ochart["missing_lr_1"] if "missing_lr_1" in ochart else False, 
          missing_lr_2=ochart["missing_lr_2"] if "missing_lr_2" in ochart else False, 
          missing_lr_3=ochart["missing_lr_3"] if "missing_lr_3" in ochart else False, 
          missing_lr_4=ochart["missing_lr_4"] if "missing_lr_4" in ochart else False, 
          missing_lr_5=ochart["missing_lr_5"] if "missing_lr_5" in ochart else False, 
          missing_lr_6=ochart["missing_lr_6"] if "missing_lr_6" in ochart else False, 
          missing_lr_7=ochart["missing_lr_7"] if "missing_lr_7" in ochart else False, 
          missing_lr_8=ochart["missing_lr_8"] if "missing_lr_8" in ochart else False, 
          xray_ul_1=ochart["xray_ul_1"] if "xray_ul_1" in ochart else False, 
          xray_ul_2=ochart["xray_ul_2"] if "xray_ul_2" in ochart else False, 
          xray_ul_3=ochart["xray_ul_3"] if "xray_ul_3" in ochart else False, 
          xray_ul_4=ochart["xray_ul_4"] if "xray_ul_4" in ochart else False, 
          xray_ul_5=ochart["xray_ul_5"] if "xray_ul_5" in ochart else False, 
          xray_ul_6=ochart["xray_ul_6"] if "xray_ul_6" in ochart else False, 
          xray_ul_7=ochart["xray_ul_7"] if "xray_ul_7" in ochart else False, 
          xray_ul_8=ochart["xray_ul_8"] if "xray_ul_8" in ochart else False, 
          xray_ur_1=ochart["xray_ur_1"] if "xray_ur_1" in ochart else False, 
          xray_ur_2=ochart["xray_ur_2"] if "xray_ur_2" in ochart else False, 
          xray_ur_3=ochart["xray_ur_3"] if "xray_ur_3" in ochart else False, 
          xray_ur_4=ochart["xray_ur_4"] if "xray_ur_4" in ochart else False, 
          xray_ur_5=ochart["xray_ur_5"] if "xray_ur_5" in ochart else False, 
          xray_ur_6=ochart["xray_ur_6"] if "xray_ur_6" in ochart else False, 
          xray_ur_7=ochart["xray_ur_7"] if "xray_ur_7" in ochart else False, 
          xray_ur_8=ochart["xray_ur_8"] if "xray_ur_8" in ochart else False, 
          xray_ll_1=ochart["xray_ll_1"] if "xray_ll_1" in ochart else False, 
          xray_ll_2=ochart["xray_ll_2"] if "xray_ll_2" in ochart else False, 
          xray_ll_3=ochart["xray_ll_3"] if "xray_ll_3" in ochart else False, 
          xray_ll_4=ochart["xray_ll_4"] if "xray_ll_4" in ochart else False, 
          xray_ll_5=ochart["xray_ll_5"] if "xray_ll_5" in ochart else False, 
          xray_ll_6=ochart["xray_ll_6"] if "xray_ll_6" in ochart else False, 
          xray_ll_7=ochart["xray_ll_7"] if "xray_ll_7" in ochart else False, 
          xray_ll_8=ochart["xray_ll_8"] if "xray_ll_8" in ochart else False, 
          xray_lr_1=ochart["xray_lr_1"] if "xray_lr_1" in ochart else False, 
          xray_lr_2=ochart["xray_lr_2"] if "xray_lr_2" in ochart else False, 
          xray_lr_3=ochart["xray_lr_3"] if "xray_lr_3" in ochart else False, 
          xray_lr_4=ochart["xray_lr_4"] if "xray_lr_4" in ochart else False, 
          xray_lr_5=ochart["xray_lr_5"] if "xray_lr_5" in ochart else False, 
          xray_lr_6=ochart["xray_lr_6"] if "xray_lr_6" in ochart else False, 
          xray_lr_7=ochart["xray_lr_7"] if "xray_lr_7" in ochart else False, 
          xray_lr_8=ochart["xray_lr_8"] if "xray_lr_8" in ochart else False, 

          modified_on = common.getISTFormatCurrentLocatTime(),
          modified_by =1 if(auth.user == None) else auth.user.id        
        
        
        )
        
        return json.dumps({"result":"success","error_message":"","mediclaimid":str(mediclaimid)})
        
      except Exception as e:
          error_message = "Update Mediclaim Charts Exception Error - " + str(e)
          logger.loggerpms2.info(error_message)
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = error_message
          return json.dumps(excpobj)    
      
      return
    
     
  def deletemediclaimcharts(self,mediclaimid):
      
      db = self.db
      auth = current.auth
      
      try:
        
        
        chartsid = db(db.mediclaim_charts.mediclaimid == mediclaimid).update(\
          
          is_active = False,
          modified_on = common.getISTFormatCurrentLocatTime(),
          modified_by =1 if(auth.user == None) else auth.user.id        
        
        
        )
        
        return json.dumps({"result":"success","error_message":""})
        
      except Exception as e:
          error_message = "Delete Mediclaim Charts Exception Error - " + str(e)
          logger.loggerpms2.info(error_message)
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = error_message
          return json.dumps(excpobj)    
      
      return
    
    
  def getmediclaimcharts(self,mediclaimid):
    
    db = self.db
    auth = current.auth
    
    try:
      chartobj = {}
      
      charts = db(db.mediclaim_charts.mediclaimid == mediclaimid).select()
      
      
      if(len(charts) == 1):
        
        chartobj["mediclaimid"] = str(mediclaimid)
        chartobj["result"] = "success"
        chartobj["error_message"] = ""
        ochart = charts[0]
        if(common.getboolean(ochart["restoration_ul_1"]) == True):
                  chartobj["restoration_ul_1"] = charts[0].restoration_ul_1
        if(common.getboolean(ochart["restoration_ul_2"]) == True):
                  chartobj["restoration_ul_2"] = charts[0].restoration_ul_2
        if(common.getboolean(ochart["restoration_ul_3"]) == True):
                  chartobj["restoration_ul_3"] = charts[0].restoration_ul_3
        if(common.getboolean(ochart["restoration_ul_4"]) == True):
                  chartobj["restoration_ul_4"] = charts[0].restoration_ul_4
        if(common.getboolean(ochart["restoration_ul_5"]) == True):
                  chartobj["restoration_ul_5"] = charts[0].restoration_ul_5
        if(common.getboolean(ochart["restoration_ul_6"]) == True):
                  chartobj["restoration_ul_6"] = charts[0].restoration_ul_6
        if(common.getboolean(ochart["restoration_ul_7"]) == True):
                  chartobj["restoration_ul_7"] = charts[0].restoration_ul_7
        if(common.getboolean(ochart["restoration_ul_8"]) == True):
                  chartobj["restoration_ul_8"] = charts[0].restoration_ul_8
                          
        if(common.getboolean(ochart["restoration_ur_1"]) == True):
                  chartobj["restoration_ur_1"] = charts[0].restoration_ur_1
        if(common.getboolean(ochart["restoration_ur_2"]) == True):
                  chartobj["restoration_ur_2"] = charts[0].restoration_ur_2
        if(common.getboolean(ochart["restoration_ur_3"]) == True):
                  chartobj["restoration_ur_3"] = charts[0].restoration_ur_3
        if(common.getboolean(ochart["restoration_ur_4"]) == True):
                  chartobj["restoration_ur_4"] = charts[0].restoration_ur_4
        if(common.getboolean(ochart["restoration_ur_5"]) == True):
                  chartobj["restoration_ur_5"] = charts[0].restoration_ur_5
        if(common.getboolean(ochart["restoration_ur_6"]) == True):
                  chartobj["restoration_ur_6"] = charts[0].restoration_ur_6
        if(common.getboolean(ochart["restoration_ur_7"]) == True):
                  chartobj["restoration_ur_7"] = charts[0].restoration_ur_7
        if(common.getboolean(ochart["restoration_ur_8"]) == True):
                  chartobj["restoration_ur_8"] = charts[0].restoration_ur_8
                          
        if(common.getboolean(ochart["restoration_ll_1"]) == True):
                  chartobj["restoration_ll_1"] = charts[0].restoration_ll_1
        if(common.getboolean(ochart["restoration_ll_2"]) == True):
                  chartobj["restoration_ll_2"] = charts[0].restoration_ll_2
        if(common.getboolean(ochart["restoration_ll_3"]) == True):
                  chartobj["restoration_ll_3"] = charts[0].restoration_ll_3
        if(common.getboolean(ochart["restoration_ll_4"]) == True):
                  chartobj["restoration_ll_4"] = charts[0].restoration_ll_4
        if(common.getboolean(ochart["restoration_ll_5"]) == True):
                  chartobj["restoration_ll_5"] = charts[0].restoration_ll_5
        if(common.getboolean(ochart["restoration_ll_6"]) == True):
                  chartobj["restoration_ll_6"] = charts[0].restoration_ll_6
        if(common.getboolean(ochart["restoration_ll_7"]) == True):
                  chartobj["restoration_ll_7"] = charts[0].restoration_ll_7
        if(common.getboolean(ochart["restoration_ll_8"]) == True):
                  chartobj["restoration_ll_8"] = charts[0].restoration_ll_8
        
        if(common.getboolean(ochart["restoration_lr_1"]) == True):
                  chartobj["restoration_lr_1"] = charts[0].restoration_lr_1
        if(common.getboolean(ochart["restoration_lr_2"]) == True):
                  chartobj["restoration_lr_2"] = charts[0].restoration_lr_2
        if(common.getboolean(ochart["restoration_lr_3"]) == True):
                  chartobj["restoration_lr_3"] = charts[0].restoration_lr_3
        if(common.getboolean(ochart["restoration_lr_4"]) == True):
                  chartobj["restoration_lr_4"] = charts[0].restoration_lr_4
        if(common.getboolean(ochart["restoration_lr_5"]) == True):
                  chartobj["restoration_lr_5"] = charts[0].restoration_lr_5
        if(common.getboolean(ochart["restoration_lr_6"]) == True):
                  chartobj["restoration_lr_6"] = charts[0].restoration_lr_6
        if(common.getboolean(ochart["restoration_lr_7"]) == True):
                  chartobj["restoration_lr_7"] = charts[0].restoration_lr_7
        if(common.getboolean(ochart["restoration_lr_8"]) == True):
                  chartobj["restoration_lr_8"] = charts[0].restoration_lr_8

        if(common.getboolean(ochart["rootcanal_ul_1"]) == True):
                  chartobj["rootcanal_ul_1"] = charts[0].rootcanal_ul_1
        if(common.getboolean(ochart["rootcanal_ul_2"]) == True):
                  chartobj["rootcanal_ul_2"] = charts[0].rootcanal_ul_2
        if(common.getboolean(ochart["rootcanal_ul_3"]) == True):
                  chartobj["rootcanal_ul_3"] = charts[0].rootcanal_ul_3
        if(common.getboolean(ochart["rootcanal_ul_4"]) == True):
                  chartobj["rootcanal_ul_4"] = charts[0].rootcanal_ul_4
        if(common.getboolean(ochart["rootcanal_ul_5"]) == True):
                  chartobj["rootcanal_ul_5"] = charts[0].rootcanal_ul_5
        if(common.getboolean(ochart["rootcanal_ul_6"]) == True):
                  chartobj["rootcanal_ul_6"] = charts[0].rootcanal_ul_6
        if(common.getboolean(ochart["rootcanal_ul_7"]) == True):
                  chartobj["rootcanal_ul_7"] = charts[0].rootcanal_ul_7
        if(common.getboolean(ochart["rootcanal_ul_8"]) == True):
                  chartobj["rootcanal_ul_8"] = charts[0].rootcanal_ul_8
                          
        if(common.getboolean(ochart["rootcanal_ur_1"]) == True):
                  chartobj["rootcanal_ur_1"] = charts[0].rootcanal_ur_1
        if(common.getboolean(ochart["rootcanal_ur_2"]) == True):
                  chartobj["rootcanal_ur_2"] = charts[0].rootcanal_ur_2
        if(common.getboolean(ochart["rootcanal_ur_3"]) == True):
                  chartobj["rootcanal_ur_3"] = charts[0].rootcanal_ur_3
        if(common.getboolean(ochart["rootcanal_ur_4"]) == True):
                  chartobj["rootcanal_ur_4"] = charts[0].rootcanal_ur_4
        if(common.getboolean(ochart["rootcanal_ur_5"]) == True):
                  chartobj["rootcanal_ur_5"] = charts[0].rootcanal_ur_5
        if(common.getboolean(ochart["rootcanal_ur_6"]) == True):
                  chartobj["rootcanal_ur_6"] = charts[0].rootcanal_ur_6
        if(common.getboolean(ochart["rootcanal_ur_7"]) == True):
                  chartobj["rootcanal_ur_7"] = charts[0].rootcanal_ur_7
        if(common.getboolean(ochart["rootcanal_ur_8"]) == True):
                  chartobj["rootcanal_ur_8"] = charts[0].rootcanal_ur_8
                          
        if(common.getboolean(ochart["rootcanal_ll_1"]) == True):
                  chartobj["rootcanal_ll_1"] = charts[0].rootcanal_ll_1
        if(common.getboolean(ochart["rootcanal_ll_2"]) == True):
                  chartobj["rootcanal_ll_2"] = charts[0].rootcanal_ll_2
        if(common.getboolean(ochart["rootcanal_ll_3"]) == True):
                  chartobj["rootcanal_ll_3"] = charts[0].rootcanal_ll_3
        if(common.getboolean(ochart["rootcanal_ll_4"]) == True):
                  chartobj["rootcanal_ll_4"] = charts[0].rootcanal_ll_4
        if(common.getboolean(ochart["rootcanal_ll_5"]) == True):
                  chartobj["rootcanal_ll_5"] = charts[0].rootcanal_ll_5
        if(common.getboolean(ochart["rootcanal_ll_6"]) == True):
                  chartobj["rootcanal_ll_6"] = charts[0].rootcanal_ll_6
        if(common.getboolean(ochart["rootcanal_ll_7"]) == True):
                  chartobj["rootcanal_ll_7"] = charts[0].rootcanal_ll_7
        if(common.getboolean(ochart["rootcanal_ll_8"]) == True):
                  chartobj["rootcanal_ll_8"] = charts[0].rootcanal_ll_8
        
        if(common.getboolean(ochart["rootcanal_lr_1"]) == True):
                  chartobj["rootcanal_lr_1"] = charts[0].rootcanal_lr_1
        if(common.getboolean(ochart["rootcanal_lr_2"]) == True):
                  chartobj["rootcanal_lr_2"] = charts[0].rootcanal_lr_2
        if(common.getboolean(ochart["rootcanal_lr_3"]) == True):
                  chartobj["rootcanal_lr_3"] = charts[0].rootcanal_lr_3
        if(common.getboolean(ochart["rootcanal_lr_4"]) == True):
                  chartobj["rootcanal_lr_4"] = charts[0].rootcanal_lr_4
        if(common.getboolean(ochart["rootcanal_lr_5"]) == True):
                  chartobj["rootcanal_lr_5"] = charts[0].rootcanal_lr_5
        if(common.getboolean(ochart["rootcanal_lr_6"]) == True):
                  chartobj["rootcanal_lr_6"] = charts[0].rootcanal_lr_6
        if(common.getboolean(ochart["rootcanal_lr_7"]) == True):
                  chartobj["rootcanal_lr_7"] = charts[0].rootcanal_lr_7
        if(common.getboolean(ochart["rootcanal_lr_8"]) == True):
                  chartobj["rootcanal_lr_8"] = charts[0].rootcanal_lr_8

        if(common.getboolean(ochart["extract_ul_1"]) == True):
                  chartobj["extract_ul_1"] = charts[0].extract_ul_1
        if(common.getboolean(ochart["extract_ul_2"]) == True):
                  chartobj["extract_ul_2"] = charts[0].extract_ul_2
        if(common.getboolean(ochart["extract_ul_3"]) == True):
                  chartobj["extract_ul_3"] = charts[0].extract_ul_3
        if(common.getboolean(ochart["extract_ul_4"]) == True):
                  chartobj["extract_ul_4"] = charts[0].extract_ul_4
        if(common.getboolean(ochart["extract_ul_5"]) == True):
                  chartobj["extract_ul_5"] = charts[0].extract_ul_5
        if(common.getboolean(ochart["extract_ul_6"]) == True):
                  chartobj["extract_ul_6"] = charts[0].extract_ul_6
        if(common.getboolean(ochart["extract_ul_7"]) == True):
                  chartobj["extract_ul_7"] = charts[0].extract_ul_7
        if(common.getboolean(ochart["extract_ul_8"]) == True):
                  chartobj["extract_ul_8"] = charts[0].extract_ul_8
                          
        if(common.getboolean(ochart["extract_ur_1"]) == True):
                  chartobj["extract_ur_1"] = charts[0].extract_ur_1
        if(common.getboolean(ochart["extract_ur_2"]) == True):
                  chartobj["extract_ur_2"] = charts[0].extract_ur_2
        if(common.getboolean(ochart["extract_ur_3"]) == True):
                  chartobj["extract_ur_3"] = charts[0].extract_ur_3
        if(common.getboolean(ochart["extract_ur_4"]) == True):
                  chartobj["extract_ur_4"] = charts[0].extract_ur_4
        if(common.getboolean(ochart["extract_ur_5"]) == True):
                  chartobj["extract_ur_5"] = charts[0].extract_ur_5
        if(common.getboolean(ochart["extract_ur_6"]) == True):
                  chartobj["extract_ur_6"] = charts[0].extract_ur_6
        if(common.getboolean(ochart["extract_ur_7"]) == True):
                  chartobj["extract_ur_7"] = charts[0].extract_ur_7
        if(common.getboolean(ochart["extract_ur_8"]) == True):
                  chartobj["extract_ur_8"] = charts[0].extract_ur_8
                          
        if(common.getboolean(ochart["extract_ll_1"]) == True):
                  chartobj["extract_ll_1"] = charts[0].extract_ll_1
        if(common.getboolean(ochart["extract_ll_2"]) == True):
                  chartobj["extract_ll_2"] = charts[0].extract_ll_2
        if(common.getboolean(ochart["extract_ll_3"]) == True):
                  chartobj["extract_ll_3"] = charts[0].extract_ll_3
        if(common.getboolean(ochart["extract_ll_4"]) == True):
                  chartobj["extract_ll_4"] = charts[0].extract_ll_4
        if(common.getboolean(ochart["extract_ll_5"]) == True):
                  chartobj["extract_ll_5"] = charts[0].extract_ll_5
        if(common.getboolean(ochart["extract_ll_6"]) == True):
                  chartobj["extract_ll_6"] = charts[0].extract_ll_6
        if(common.getboolean(ochart["extract_ll_7"]) == True):
                  chartobj["extract_ll_7"] = charts[0].extract_ll_7
        if(common.getboolean(ochart["extract_ll_8"]) == True):
                  chartobj["extract_ll_8"] = charts[0].extract_ll_8
        
        if(common.getboolean(ochart["extract_lr_1"]) == True):
                  chartobj["extract_lr_1"] = charts[0].extract_lr_1
        if(common.getboolean(ochart["extract_lr_2"]) == True):
                  chartobj["extract_lr_2"] = charts[0].extract_lr_2
        if(common.getboolean(ochart["extract_lr_3"]) == True):
                  chartobj["extract_lr_3"] = charts[0].extract_lr_3
        if(common.getboolean(ochart["extract_lr_4"]) == True):
                  chartobj["extract_lr_4"] = charts[0].extract_lr_4
        if(common.getboolean(ochart["extract_lr_5"]) == True):
                  chartobj["extract_lr_5"] = charts[0].extract_lr_5
        if(common.getboolean(ochart["extract_lr_6"]) == True):
                  chartobj["extract_lr_6"] = charts[0].extract_lr_6
        if(common.getboolean(ochart["extract_lr_7"]) == True):
                  chartobj["extract_lr_7"] = charts[0].extract_lr_7
        if(common.getboolean(ochart["extract_lr_8"]) == True):
                  chartobj["extract_lr_8"] = charts[0].extract_lr_8

        if(common.getboolean(ochart["missing_ul_1"]) == True):
                  chartobj["missing_ul_1"] = charts[0].missing_ul_1
        if(common.getboolean(ochart["missing_ul_2"]) == True):
                  chartobj["missing_ul_2"] = charts[0].missing_ul_2
        if(common.getboolean(ochart["missing_ul_3"]) == True):
                  chartobj["missing_ul_3"] = charts[0].missing_ul_3
        if(common.getboolean(ochart["missing_ul_4"]) == True):
                  chartobj["missing_ul_4"] = charts[0].missing_ul_4
        if(common.getboolean(ochart["missing_ul_5"]) == True):
                  chartobj["missing_ul_5"] = charts[0].missing_ul_5
        if(common.getboolean(ochart["missing_ul_6"]) == True):
                  chartobj["missing_ul_6"] = charts[0].missing_ul_6
        if(common.getboolean(ochart["missing_ul_7"]) == True):
                  chartobj["missing_ul_7"] = charts[0].missing_ul_7
        if(common.getboolean(ochart["missing_ul_8"]) == True):
                  chartobj["missing_ul_8"] = charts[0].missing_ul_8
                          
        if(common.getboolean(ochart["missing_ur_1"]) == True):
                  chartobj["missing_ur_1"] = charts[0].missing_ur_1
        if(common.getboolean(ochart["missing_ur_2"]) == True):
                  chartobj["missing_ur_2"] = charts[0].missing_ur_2
        if(common.getboolean(ochart["missing_ur_3"]) == True):
                  chartobj["missing_ur_3"] = charts[0].missing_ur_3
        if(common.getboolean(ochart["missing_ur_4"]) == True):
                  chartobj["missing_ur_4"] = charts[0].missing_ur_4
        if(common.getboolean(ochart["missing_ur_5"]) == True):
                  chartobj["missing_ur_5"] = charts[0].missing_ur_5
        if(common.getboolean(ochart["missing_ur_6"]) == True):
                  chartobj["missing_ur_6"] = charts[0].missing_ur_6
        if(common.getboolean(ochart["missing_ur_7"]) == True):
                  chartobj["missing_ur_7"] = charts[0].missing_ur_7
        if(common.getboolean(ochart["missing_ur_8"]) == True):
                  chartobj["missing_ur_8"] = charts[0].missing_ur_8
                          
        if(common.getboolean(ochart["missing_ll_1"]) == True):
                  chartobj["missing_ll_1"] = charts[0].missing_ll_1
        if(common.getboolean(ochart["missing_ll_2"]) == True):
                  chartobj["missing_ll_2"] = charts[0].missing_ll_2
        if(common.getboolean(ochart["missing_ll_3"]) == True):
                  chartobj["missing_ll_3"] = charts[0].missing_ll_3
        if(common.getboolean(ochart["missing_ll_4"]) == True):
                  chartobj["missing_ll_4"] = charts[0].missing_ll_4
        if(common.getboolean(ochart["missing_ll_5"]) == True):
                  chartobj["missing_ll_5"] = charts[0].missing_ll_5
        if(common.getboolean(ochart["missing_ll_6"]) == True):
                  chartobj["missing_ll_6"] = charts[0].missing_ll_6
        if(common.getboolean(ochart["missing_ll_7"]) == True):
                  chartobj["missing_ll_7"] = charts[0].missing_ll_7
        if(common.getboolean(ochart["missing_ll_8"]) == True):
                  chartobj["missing_ll_8"] = charts[0].missing_ll_8
        
        if(common.getboolean(ochart["missing_lr_1"]) == True):
                  chartobj["missing_lr_1"] = charts[0].missing_lr_1
        if(common.getboolean(ochart["missing_lr_2"]) == True):
                  chartobj["missing_lr_2"] = charts[0].missing_lr_2
        if(common.getboolean(ochart["missing_lr_3"]) == True):
                  chartobj["missing_lr_3"] = charts[0].missing_lr_3
        if(common.getboolean(ochart["missing_lr_4"]) == True):
                  chartobj["missing_lr_4"] = charts[0].missing_lr_4
        if(common.getboolean(ochart["missing_lr_5"]) == True):
                  chartobj["missing_lr_5"] = charts[0].missing_lr_5
        if(common.getboolean(ochart["missing_lr_6"]) == True):
                  chartobj["missing_lr_6"] = charts[0].missing_lr_6
        if(common.getboolean(ochart["missing_lr_7"]) == True):
                  chartobj["missing_lr_7"] = charts[0].missing_lr_7
        if(common.getboolean(ochart["missing_lr_8"]) == True):
                  chartobj["missing_lr_8"] = charts[0].missing_lr_8

        if(common.getboolean(ochart["xray_ul_1"]) == True):
                  chartobj["xray_ul_1"] = charts[0].xray_ul_1
        if(common.getboolean(ochart["xray_ul_2"]) == True):
                  chartobj["xray_ul_2"] = charts[0].xray_ul_2
        if(common.getboolean(ochart["xray_ul_3"]) == True):
                  chartobj["xray_ul_3"] = charts[0].xray_ul_3
        if(common.getboolean(ochart["xray_ul_4"]) == True):
                  chartobj["xray_ul_4"] = charts[0].xray_ul_4
        if(common.getboolean(ochart["xray_ul_5"]) == True):
                  chartobj["xray_ul_5"] = charts[0].xray_ul_5
        if(common.getboolean(ochart["xray_ul_6"]) == True):
                  chartobj["xray_ul_6"] = charts[0].xray_ul_6
        if(common.getboolean(ochart["xray_ul_7"]) == True):
                  chartobj["xray_ul_7"] = charts[0].xray_ul_7
        if(common.getboolean(ochart["xray_ul_8"]) == True):
                  chartobj["xray_ul_8"] = charts[0].xray_ul_8
                          
        if(common.getboolean(ochart["xray_ur_1"]) == True):
                  chartobj["xray_ur_1"] = charts[0].xray_ur_1
        if(common.getboolean(ochart["xray_ur_2"]) == True):
                  chartobj["xray_ur_2"] = charts[0].xray_ur_2
        if(common.getboolean(ochart["xray_ur_3"]) == True):
                  chartobj["xray_ur_3"] = charts[0].xray_ur_3
        if(common.getboolean(ochart["xray_ur_4"]) == True):
                  chartobj["xray_ur_4"] = charts[0].xray_ur_4
        if(common.getboolean(ochart["xray_ur_5"]) == True):
                  chartobj["xray_ur_5"] = charts[0].xray_ur_5
        if(common.getboolean(ochart["xray_ur_6"]) == True):
                  chartobj["xray_ur_6"] = charts[0].xray_ur_6
        if(common.getboolean(ochart["xray_ur_7"]) == True):
                  chartobj["xray_ur_7"] = charts[0].xray_ur_7
        if(common.getboolean(ochart["xray_ur_8"]) == True):
                  chartobj["xray_ur_8"] = charts[0].xray_ur_8
                          
        if(common.getboolean(ochart["xray_ll_1"]) == True):
                  chartobj["xray_ll_1"] = charts[0].xray_ll_1
        if(common.getboolean(ochart["xray_ll_2"]) == True):
                  chartobj["xray_ll_2"] = charts[0].xray_ll_2
        if(common.getboolean(ochart["xray_ll_3"]) == True):
                  chartobj["xray_ll_3"] = charts[0].xray_ll_3
        if(common.getboolean(ochart["xray_ll_4"]) == True):
                  chartobj["xray_ll_4"] = charts[0].xray_ll_4
        if(common.getboolean(ochart["xray_ll_5"]) == True):
                  chartobj["xray_ll_5"] = charts[0].xray_ll_5
        if(common.getboolean(ochart["xray_ll_6"]) == True):
                  chartobj["xray_ll_6"] = charts[0].xray_ll_6
        if(common.getboolean(ochart["xray_ll_7"]) == True):
                  chartobj["xray_ll_7"] = charts[0].xray_ll_7
        if(common.getboolean(ochart["xray_ll_8"]) == True):
                  chartobj["xray_ll_8"] = charts[0].xray_ll_8
        
        if(common.getboolean(ochart["xray_lr_1"]) == True):
                  chartobj["xray_lr_1"] = charts[0].xray_lr_1
        if(common.getboolean(ochart["xray_lr_2"]) == True):
                  chartobj["xray_lr_2"] = charts[0].xray_lr_2
        if(common.getboolean(ochart["xray_lr_3"]) == True):
                  chartobj["xray_lr_3"] = charts[0].xray_lr_3
        if(common.getboolean(ochart["xray_lr_4"]) == True):
                  chartobj["xray_lr_4"] = charts[0].xray_lr_4
        if(common.getboolean(ochart["xray_lr_5"]) == True):
                  chartobj["xray_lr_5"] = charts[0].xray_lr_5
        if(common.getboolean(ochart["xray_lr_6"]) == True):
                  chartobj["xray_lr_6"] = charts[0].xray_lr_6
        if(common.getboolean(ochart["xray_lr_7"]) == True):
                  chartobj["xray_lr_7"] = charts[0].xray_lr_7
        if(common.getboolean(ochart["xray_lr_8"]) == True):
                  chartobj["xray_lr_8"] = charts[0].xray_lr_8
        
                                                      
      else:
        error_message = "Get MedicCharts Error : Invalid chart for this claim " + str(mediclaimid)
        chartobj["result"] = "fail"
        chartobj["error_message"] = error_message
        logger.loggerpms2.info(error_message)
        
      return json.dumps(chartobj)
      
    except Exception as e:
        error_message = "Add Mediclaim Procedures Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return
  

  
  def addmediclaim(self,treatmentid,oclaim):
    
    db = self.db
    auth = current.auth
    providerid = self.providerid
    claimid = 0
    
    try:
      
      tr = db(db.vw_treatmentlist.id == treatmentid).select(db.vw_treatmentlist.memberid,db.vw_treatmentlist.patientid)
      co = db(db.company.company == 'MEDI').select(db.company.id)
      
      claimid = db.mediclaim.insert(\
        providerid = providerid,
        treatmentid = treatmentid,
        companyid = int(co[0].id) if(len(co) == 1) else 0,
        memberid = int(tr[0].memberid) if(len(tr) == 1) else 0,
        patientid = int(tr[0].patientid) if(len(tr) == 1) else 0,
        final_statement = oclaim["final_statement"],
        request_for_authorization = oclaim["request_for_authorization"],
        preauth_number = oclaim["preauth_number"],
        history = oclaim["history"],
        allergy = oclaim["allergy"],
        chiefcomplaint = oclaim["chiefcomplaint"],
        oralprophylate = oclaim["oralprophylate"],
        orthodontics = oclaim["orthodontics"],
        remarks = oclaim["remarks"],
        attendingdoctor = oclaim["attendingdoctor"],
        is_active = True,
        created_on = common.getISTFormatCurrentLocatTime(),
        created_by = 1 if(auth.user == None) else auth.user.id,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by =1 if(auth.user == None) else auth.user.id        
      
      )
      db.commit()

      if("attachments" in oclaim):
        i = 0
      
      if("signatures" in oclaim):
        i = 0

      
      if("charts" in oclaim):
        self.addmediclaimcharts(claimid, oclaim["charts"])
      
      if("procedures" in oclaim):
        mediclaimprocedures = oclaim["procedures"]
      
        for p in mediclaimprocedures:
          self.addmediclaimprocedure(claimid,p["procedureid"],p["procdate"],p["tooth"],p["description"],p["quantity"],p["cashless"],p["status"])
      
    except Exception as e:
        error_message = "Add Mediclaim  Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return json.dumps({"result":"success","error_message":"","mediclaimid":str(claimid)})
    
 
  def getmediclaims(self,treatmentid):
    
    db = self.db
    providerid = self.providerid

    claimobj = {}
    claimlist = []
    try:
      claims = db((db.mediclaim.treatmentid == treatmentid) & (db.mediclaim.providerid == providerid) & (db.mediclaim.is_active == True)).select()
      
      for claim in claims:
        claimobj = {}
        claimobj["mediclaimid"] = claim.id
        claimobj["providerid"]=claim.providerid
        claimobj["treatmentid"]=claim.treatmentid 
        claimobj["companyid"]=claim.companyid
        claimobj["memberid"]=claim.memberid
        claimobj["patientid"]=claim.patientid
        claimobj["final_statement"]=claim.final_statement
        claimobj["request_for_authorization"]=claim.request_for_authorization
        claimobj["preauth_number"]=claim.preauth_number
        claimobj["history"]=claim.history
        claimobj["allergy"]=claim.allergy
        claimobj["chiefcomplaint"]=claim.chiefcomplaint
        claimobj["oralprophylate"]=claim.oralprophylate
        claimobj["orthodontics"]=claim.orthodontics
        claimobj["remarks"]=claim.remarks
        claimobj["attendingdoctor"]=claim.attendingdoctor
        claimlist.append(claimobj)
      
      return json.dumps({"result":"success","error_message":"","claimlist":claimlist})
      
    except Exception as e:
        error_message = "Add Mediclaim Procedures Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return
  
   
  
  def getmediclaim(self,mediclaimid):
    
    db = self.db
   
    providerid = self.providerid
    
    try:
      claimobj = {}
      
      claim = db((db.mediclaim.id == mediclaimid) & (db.mediclaim.providerid == providerid) & (db.mediclaim.is_active == True)).select()
      
      if(len(claim) == 1):
        claimobj["providerid"]=claim[0].providerid
        claimobj["treatmentid"]=claim[0].treatmentid
        
        claimobj["companyid"]=claim[0].companyid
        claimobj["memberid"]=claim[0].memberid
        claimobj["patientid"]=claim[0].patientid
        claimobj["final_statement"]=claim[0].final_statement
        claimobj["request_for_authorization"]=claim[0].request_for_authorization
        claimobj["preauth_number"]=claim[0].preauth_number
        claimobj["history"]=claim[0].history
        claimobj["allergy"]=claim[0].allergy
        claimobj["chiefcomplaint"]=claim[0].chiefcomplaint
        claimobj["oralprophylate"]=claim[0].oralprophylate
        claimobj["orthodontics"]=claim[0].orthodontics
        claimobj["remarks"]=claim[0].remarks
        claimobj["attendingdoctor"]=claim[0].attendingdoctor
        claimobj["result"] = "success"
        claimobj["error_message"] = ""
        
        chartobj = json.loads(self.getmediclaimcharts(mediclaimid))
        claimobj["charts"] = chartobj
        
      else:
        error_message = "Get Mediclaim Error : No claim in the systme for this ID " + str(mediclaimid)
        claimobj["result"] = "fail"
        claimobj["error_message"] = error_message
        logger.loggerpms2.info(error_message)
      
      return json.dumps(claimobj)
    except Exception as e:
        error_message = "Get Mediclaim Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return

  def updatemediclaim(self,mediclaimid,oclaim):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    
    try:
      i = 0
      
      db((db.mediclaim.id == mediclaimid) & (db.mediclaim.providerid == providerid) & (db.mediclaim.is_active == True)).update(\
      
        final_statement = oclaim["final_statement"],
        request_for_authorization = oclaim["request_for_authorization"],
        preauth_number = oclaim["preauth_number"],
        history = oclaim["history"],
        allergy = oclaim["allergy"],
        chiefcomplaint = oclaim["chiefcomplaint"],
        oralprophylate = oclaim["oralprophylate"],
        orthodontics = oclaim["orthodontics"],
        remarks = oclaim["remarks"],
        attendingdoctor = oclaim["attendingdoctor"],
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by =1 if(auth.user == None) else auth.user.id        
      
      )
      
      return json.dumps({"result":"success","error_message":"","mediclaimid":str(mediclaimid)})
    
    except Exception as e:
        error_message = "Update Mediclaim Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return
  
  
  
  
  def deletemediclaim(self,mediclaimid):
     
    db = self.db
    providerid = self.providerid
    auth = current.auth
    
    try:
      db((db.mediclaim.id == mediclaimid) & (db.mediclaim.providerid == providerid) & (db.mediclaim.is_active == True)).update(\
        is_active = False,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by =1 if(auth.user == None) else auth.user.id        
      
      )
      
      return json.dumps({"result":"success","error_message":"","mediclaimid":str(mediclaimid)})
      
      
    except Exception as e:
        error_message = "Delete Mediclaim  Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return  
  
  
  def uploadmediclaimsignature(self,mediclaimid,signature,signdata,signdate, appath):
     
    db = self.db
    auth = current.auth
    try:
      
    #save image data in a temporary file
    #logger.loggerpms2.info("Enter Mediclaim Upload  Signature")

      dirpath = os.path.join(appath, 'temp')
      
      if(not os.path.exists(dirpath)):
        os.makedirs(dirpath,0777)
      
      tempfile.tempdir = dirpath
      tempimgfile = tempfile.NamedTemporaryFile(delete=False)
      tempimgfile.name = tempimgfile.name + ".jpg"
  
      with open(tempimgfile.name,"wb+") as f:
        f.write(signdata.decode('base64'))     
  
      #logger.loggerpms2.info("Mediclaim Signature Uploaded to " + tempimgfile.name)
      
      
      #upload the image to the server
      signstream = open(tempimgfile.name,'rb') 
      
      if(signature == 'dentist'):
        db.mediclaim_signatures.update_or_insert(((db.mediclaim_signatures.mediclaimid == mediclaimid) & (db.mediclaim_signatures.is_active == True)),
                                                 mediclaimid = mediclaimid,
                                                 dentist_signature = signstream,
                                                 dentist_signature_date = common.getdt(datetime.datetime.strptime(signdate,"%d/%m/%Y")),
                                                 is_active = True,
                                                 created_on=common.getISTFormatCurrentLocatTime(),
                                                 modified_on=common.getISTFormatCurrentLocatTime(),
                                                 created_by = 1 if(auth.user == None) else auth.user.id,
                                                 modified_by= 1 if(auth.user == None) else auth.user.id
                                                 )
      
      if(signature == 'employee'):
        db.mediclaim_signatures.update_or_insert(((db.mediclaim_signatures.mediclaimid == mediclaimid) & (db.mediclaim_signatures.is_active == True)),
                                                 mediclaimid=mediclaimid,
                                                 employee_signature = signstream,
                                                 employee_signature_date = common.getdt(datetime.datetime.strptime(signdate,"%d/%m/%Y")),
                                                 is_active = True,
                                                 created_on=common.getISTFormatCurrentLocatTime(),
                                                 modified_on=common.getISTFormatCurrentLocatTime(),
                                                 created_by = 1 if(auth.user == None) else auth.user.id,
                                                 modified_by= 1 if(auth.user == None) else auth.user.id
                                                 )
      #delete temporary file
      tempimgfile.close()
      #os.remove(tempimgfile.name)
      
      #return image object
      imageobj = {
        "result": "success",
        "error_message":""
        
      }
        
      return json.dumps(imageobj)        
    
      
    except Exception as e:
        error_message = "Mediclaim Upload Signature Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return
  
  
  def downloadmediclaimsignature(self,mediclaimid,signature):
    
    db = self.db
    auth = current.auth
    
  
    try:
      
      sign = db((db.mediclaim_signatures.mediclaimid == mediclaimid) & (db.mediclaim_signatures.is_active==True)).select()
      
      
      signobj = {}
      signobj["result"] = "fail"
      signobj["error_message"] = "No Signature"
      if(signature == 'dentist'):
        signobj={
          
          "signatureurl":"",
          "mediclaimid":str(mediclaimid),
          "signdate":(sign[0].dentist_signature_date).strftime("%d/%m/%Y"),
          "signdata":(sign[0].dentist_signature),
          "result":"success",
          "error_message":""
        }
             
      if(signature == 'employee'):
        signobj={
          
          "signatureurl":"",
          "mediclaimid":str(mediclaimid),
          "signdate":(sign[0].employee_signature_date).strftime("%d/%m/%Y"),
          "signdata":(sign[0].employee_signature),
          "result":"success",
          "error_message":""
          
        }
      
             
      return  json.dumps(signobj)
    
    except Exception as e:
        error_message = "Download Mediclaim SIgnature Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)
    

  def deletemediclaimsignature(self,mediclaimid,signature=""):
    
    db = self.db
    auth = current.auth
    
    try:
      signobj = {}
      
      if(signature == ""):
        db(db.mediclaim_signatures.mediclaimid == mediclaimid).update(\
          is_active = False,
          modified_on=common.getISTFormatCurrentLocatTime(),
          modified_by= 1 if(auth.user == None) else auth.user.id        
        )
      
      if(signature == "dentist"):
        
          db(db.mediclaim_signatures.mediclaimid == mediclaimid).update(\
          dentist_signature = None,
          dentist_signature_date = None,
          modified_on=common.getISTFormatCurrentLocatTime(),
          modified_by= 1 if(auth.user == None) else auth.user.id        
        )
        
      if(signature == "employee"):
        db(db.mediclaim_signatures.mediclaimid == mediclaimid).update(\
          employee_signature = None,
          employee_signature_date = None,
          modified_on=common.getISTFormatCurrentLocatTime(),
          modified_by= 1 if(auth.user == None) else auth.user.id        
        )
      
      return json.dumps({"result":"success","error_message":""})
    
    except Exception as e:
        error_message = "Add Mediclaim Procedures Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return
  


  def addmediclaimattachment(self,mediclaimid,attachment,title,description,appath):
   
       
    db = self.db
    auth = current.auth
    
    try:
      #======created_on is also the date on which the attachment was added.
      
      
      #save image data in a temporary file
      #logger.loggerpms2.info("Enter Mediclaim Add Attachment")

      dirpath = os.path.join(appath, 'temp')
      
      if(not os.path.exists(dirpath)):
        os.makedirs(dirpath,0777)
      
      tempfile.tempdir = dirpath
      tempimgfile = tempfile.NamedTemporaryFile(delete=False)
      tempimgfile.name = tempimgfile.name + ".jpg"
  
      with open(tempimgfile.name,"wb+") as f:
        f.write(attachment.decode('base64'))     
  
      #logger.loggerpms2.info("Add Mediclaim Attachment to " + tempimgfile.name)
      #upload the image to the server
      attachstream = open(tempimgfile.name,'rb') 
      attachid = db.mediclaim_attachments.insert(\
        mediclaimid = mediclaimid,
        attachment = attachstream,
        title = title,
        description = description,
        is_active = True,
        created_on=common.getISTFormatCurrentLocatTime(),
        modified_on=common.getISTFormatCurrentLocatTime(),
        created_by = 1 if(auth.user == None) else auth.user.id,
        modified_by= 1 if(auth.user == None) else auth.user.id
      )
        
      #delete temporary file
      tempimgfile.close()
      #os.remove(tempimgfile.name)
    
      #return attchment object
      attachobj = {
        "attachmentid":str(attachid),
        "result": "success",
        "error_message":""
      }
      
      return json.dumps(attachobj)        
    
      
    except Exception as e:
        error_message = "Add Mediclaim Attachment Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return


  def getmediclaimattachments(self,mediclaimid):
      
      db = self.db
    
      try:
        
        attachments = db((db.mediclaim_attachments.mediclaimid == mediclaimid) & (db.mediclaim_attachments.is_active==True)).select()
        
        attachlist = []
        attachobj = {}
        
        
        for attach in attachments:
          attachobj = {
            "attachmentid":str(attach.id),
            "mediclaimid":str(mediclaimid),
            "attachurl":"",
            "attachment":attach.attachment,
            "title":attach.title,
            "description":attach.description,
            "attachdate":(attach.created_on).strftime("%d/%m/%Y"),
          
          }
          attachlist.append(attachobj)
          
               
        return  json.dumps({"result":"success","error_message":"","attachments":attachlist})
      
      except Exception as e:
          error_message = "Get Mediclaim Attachments Exception Error - " + str(e)
          logger.loggerpms2.info(error_message)
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = error_message
          return json.dumps(excpobj)
      
  def deletemediclaimattachment(self,attachmentid):
    
    db = self.db
    auth = current.auth
    
    try:
  
      db(db.mediclaim_attachments.id == attachmentid).update(\
        is_active = False,
        modified_on=common.getISTFormatCurrentLocatTime(),
        modified_by= 1 if(auth.user == None) else auth.user.id        
      )
      
      return json.dumps({"result":"success","error_message":""})
    except Exception as e:
        error_message = "Delete Mediclaim Procedures Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return
  
      