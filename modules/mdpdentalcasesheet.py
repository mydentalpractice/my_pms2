from gluon import current
import json

import datetime
from datetime import timedelta
#


from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger

class Dentalcasesheet:
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    return 

  #this method creates a new case report
  def createcasereport(self, csrdata):
    db = self.db
    
    jsonresp = {}
    
    csrid = 0
    
    try:
      #create new case report
      csrid = db.dentalcasesheet.insert(\
        child_name = csrdata["child_name"],
        child_class = csrdata["child_class"],
        parent_name = csrdata["parent_name"],
        school_name = csrdata["school_name"],
        admission_number = csrdata["admission_number"],
        cell = csrdata["cell"],
        email = csrdata["email"],
        dob = datetime.datetime.strptime(csrdata["dob"],"%d/%m/%Y"),
        gender = csrdata["gender"],
        cavity_milk_teeth = True if(csrdata["cavity_milk_teeth"]=="1") else False,
        cavity_perm_teeth = True if(csrdata["cavity_perm_teeth"]=="1") else False,
        crooked_teeth = True if(csrdata["crooked_teeth"]=="1") else False,
        gum_problems = True if(csrdata["gum_problems"]=="1") else False,
        emergency_consult = True if(csrdata["emergency_consult"]=="1") else False,
        priority_checkup = True if(csrdata["priority_checkup"]=="1") else False,
        routine_checkup = True if(csrdata["routine_checkup"]=="1") else False,
        fluoride_check = True if(csrdata["fluoride_check"]=="1") else False,
        casereport = csrdata["doctor_notes"],
        
        is_active = True,
        created_on = common.getISTFormatCurrentLocatTime(),
        created_by = 1,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1
        
      )
      
      jsonresp = {"casereport_id":str(csrid), "result":"success","error_message":""}
    
    except Exception as e:
      logger.loggerpms2.info("Create Case Report Exception:\n" + str(e))
      jsonresp = {
        "result":"fail",
        "error_message":"Create Case Report Exception:\n" + str(e)
      }
    
    return json.dumps(jsonresp)
  
  #this method gets a list of all case reports filtered on email and cell
  def get_casereport_list(self, email, cell):
    
    db = self.db
       
    jsonresp = {}
    csrobj = {}
    csrlist = []
    
    try:
      csrs = db((db.dentalcasesheet.email == email) & (db.dentalcasesheet.cell == cell) & (db.dentalcasesheet.is_active == True)).select()
      
      
      for csr in csrs:
        csrobj = {}
        csrobj["id"] = csr.id
        csrobj["child_name"] = csr.child_name
        csrobj["child_class"] = csr.child_class
        csrobj["parent_name"] = csr.parent_name
        csrobj["school_name"] = csr.school_name
        csrobj["admission_number"] = csr.admission_number
        csrobj["cell"] = csr.cell
        csrobj["email"] = csr.email
        csrobj["dob"] = (csr.dob).strftime("%d/%m/%Y")
        csrobj["gender"] = csr.gender
        csrobj["created_on"] = (csr.created_on).strftime("%d/%m/%Y")
        csrobj["modified_on"] = (csr.modified_on).strftime("%d/%m/%Y")
        
        csrlist.append(csrobj)
        
      jsonresp = {
        "csrcount":str(len(csrlist)),
        "csrlist":csrlist,
        "result":"success",
        "error_message":"",
      
      }
        
        
    except Exception as e:
      logger.loggerpms2.info("Get Case Report List Response Exception: \n" + str(e))
      jsonresp = {
        "result":"fail",
        "error_message":"Get Case Report List Response Exception: \n" + str(e)
      }
    
    return json.dumps(jsonresp)  
     
  #this method returns casereport
  def getcasereport(self,csrid):
    db = self.db
        
    jsonresp = {}
    csrobj = {}
    try:
      
      csr = db(db.dentalcasesheet.id == csrid).select()
      csrobj["id"] = csr[0].id
      csrobj["child_name"] = csr[0].child_name
      csrobj["child_class"] = csr[0].child_class
      csrobj["parent_name"] = csr[0].parent_name
      csrobj["school_name"] = csr[0].school_name
      csrobj["admission_number"] = csr[0].admission_number
      csrobj["cell"] = csr[0].cell
      csrobj["email"] = csr[0].email
      csrobj["dob"] = (csr[0].dob).strftime("%d/%m/%Y")
      csrobj["gender"] = csr[0].gender
      
      csrobj["cavity_milk_teeth"] = "1" if(csr[0].cavity_milk_teeth == True) else "0"
      csrobj["cavity_perm_teeth"] = "1" if(csr[0].cavity_perm_teeth == True) else "0"
      csrobj["crooked_teeth"] = "1" if(csr[0].crooked_teeth == True) else "0"
      csrobj["gum_problems"] = "1" if(csr[0].gum_problems == True) else "0"
      csrobj["emergency_consult"] = "1" if(csr[0].emergency_consult == True) else "0"
      csrobj["priority_checkup"] = "1" if(csr[0].priority_checkup == True) else "0"
      csrobj["routine_checkup"] = "1" if(csr[0].routine_checkup == True) else "0"
      csrobj["fluoride_check"] = "1" if(csr[0].fluoride_check == True) else "0"
      
      csrobj["doctor_notes"] = csr[0].casereport
      
      csrobj["created_on"] = (csr[0].created_on).strftime("%d/%m/%Y")
      csrobj["modified_on"] = (csr[0].modified_on).strftime("%d/%m/%Y")      
    
      csrobj["result"] = "success"
      csrobj["error_message"] = ""
      
      jsonresp = csrobj
    except Exception as e:
      logger.loggerpms2.info("Get Case Report Response Exception: \n" + str(e))
      jsonresp = {
        "result":"fail",
        "error_message":"Get Case Report Response Exception: \n" + str(e)
      }
    
    return json.dumps(jsonresp)
  
  
  #this method update the case report
  def updatecasereport(self,csrdata):
    
    db = self.db
    
    jsonresp = {}
    
    try:
      csrid = int(common.getid(csrdata["id"]))
      db(db.dentalcasesheet.id == csrid).update(\
        child_name = csrdata["child_name"],
        child_class = csrdata["child_class"],
        parent_name = csrdata["parent_name"],
        school_name = csrdata["school_name"],
        admission_number = csrdata["admission_number"],
        cell = csrdata["cell"],
        email = csrdata["email"],
        dob = datetime.datetime.strptime(csrdata["dob"],"%d/%m/%Y"),
        gender = csrdata["gender"],
        cavity_milk_teeth = True if(csrdata["cavity_milk_teeth"]=="1") else False,
        cavity_perm_teeth = True if(csrdata["cavity_perm_teeth"]=="1") else False,
        crooked_teeth = True if(csrdata["crooked_teeth"]=="1") else False,
        gum_problems = True if(csrdata["gum_problems"]=="1") else False,
        emergency_consult = True if(csrdata["emergency_consult"]=="1") else False,
        priority_checkup = True if(csrdata["priority_checkup"]=="1") else False,
        routine_checkup = True if(csrdata["routine_checkup"]=="1") else False,
        fluoride_check = True if(csrdata["fluoride_check"]=="1") else False,
        casereport = csrdata["doctor_notes"],
        is_active = True,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1
      )
      jsonresp = {"casereport_id":str(csrid), "result":"success","error_message":""}      
    except Exception as e:
      logger.loggerpms2.info("Update Case Report Response Exception: " + str(e))
      jsonresp = {
        "result":"fail",
        "error_message":"updatecasereport:\n" + str(e)
      }
    
    return json.dumps(jsonresp)
    
    
    
