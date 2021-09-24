from gluon import current


import datetime
from datetime import timedelta
from datetime import date

import json
from applications.my_pms2.modules import common
from applications.my_pms2.modules import mdpappointment
from applications.my_pms2.modules import mdptreatment
from applications.my_pms2.modules import mdpprocedure
from applications.my_pms2.modules import mdputils

from applications.my_pms2.modules import logger

class Doctor:
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    return 
  
  #this method gets a list of doctors associated with a provider
  #returns {doctorcount,practice_owner,[{doctorid, doctorname}]
  def doctorlist(self):
    db = self.db
    providerid = self.providerid
    
    lowerlimit = (datetime.date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    sql = "select doctor.name, doctor.practice_owner, doctor.color, doctor.cell,doctor.registration, IFNULL(appts.appointments,0) AS appointments,doctor.providerid,doctor.id as docid  from doctor left join "
    sql = sql + "(select vw_appointment_count.doctorid, vw_appointment_count.name, color, count(appointments) as appointments, starttime from " 
    sql = sql + "vw_appointment_count where is_active = 'T' and providerid =" +  str(providerid)  + " and starttime >= '" + lowerlimit + "' group by name ) appts "
    sql = sql + " on doctor.id = appts.doctorid where doctor.stafftype <> 'Staff' and doctor.is_active = 'T' and doctor.providerid = " + str(providerid) + " ORDER BY appointments DESC" 
    docs = db.executesql(sql)    

    
    #drs = db((db.vw_doctor.providerid == self.providerid) & (db.vw_doctor.is_active == True)).select(db.vw_doctor.doctorid,\
                                                                                                     #db.vw_doctor.doctorname,\
                                                                                                     #db.vw_doctor.practice_owner,\
                                                                                                     #db.vw_doctor.registration,\
                                                                                                     #db.vw_doctor.cell,db.vw_doctor.color)
    
    drlist = []
    
    practice_owner = 0
    
    for dr in docs:
      
      objdr = {
        'doctorid':int(common.getid(dr[7])),
        'doctorname':common.getstring(dr[0]),
        'color':common.getstring(dr[2]) if(common.getstring(dr[2])!="") else "#ff0000",
        'count':int(common.getid(dr[5])),
        'cell':common.getstring(dr[3]),
        'registration':common.getstring(dr[4])
      }
      
      if(dr[1] == "T"):
        practice_owner = int(common.getid(dr[7]))
        
      drlist.append(objdr)
    
    json_drlist = {"doctorcount":len(docs),"practice_owner":practice_owner,"doctorlist":drlist}  
    
    return json.dumps(json_drlist)
    
  
  #this method returns doctor details
  #{doctorid,doctorname,}
  #title
  #name 
  #providerid
  #speciality
  #role 
  #practice_owner char(1) 
  #email varchar(128) 
  #cell varchar(45) 
  #registration varchar(45) 
  #color varchar(45) 
  #stafftype varchar(45) 
  #

  def doctor(self, doctorid):
    db = self.db
    providerid = self.providerid
    
    dr = db((db.vw_doctor.doctorid==doctorid) & (db.vw_doctor.providerid == providerid) & (db.vw_doctor.is_active == True)).select()
    if(len(dr)==1):
      objdr = {
        "result":True,
        "message":"",
        "doctorid":doctorid,
        "providerid":providerid,
        "title":dr[0].doctortitle,
        "doctorname":dr[0].doctorname,
        "specialityid":int(common.getid(dr[0].specialityid)),
        "speciality":dr[0].speciality,
        "roleid":int(common.getid(dr[0].roleid)),
        "role":dr[0].role,
        "practice_owner":common.getboolean(dr[0].practice_owner),
        "color":dr[0].color,
        "cell":dr[0].cell,
        "email":dr[0].email,
        "stafftype":dr[0].stafftype,
        "registration":dr[0].registration,
        "notes":dr[0].notes
      }
    else:
      objdr = {
        "result":False,
        "message":"Error in Doctor API"
        }
      
      
      
    return json.dumps(objdr)
  
  
  def newdoctor(self):
    
    return dict()
  
  def updatedoctor(self,doctorid):
    
    return dict()

  def specialitylist(self):
    db = self.db
    providerid = self.providerid    
    
    sps = db((db.speciality_default.is_active == True)).select()
    
    #if(providerid == 0):
      #sps = db((db.speciality_default.is_active == True)).select()
    #else:
      #sps = db((db.speciality.providerid == providerid) & (db.speciality.is_active == True)).select()
    
    
    splist = []
    for sp in sps:
      
      objsp = {
        'specialityid':int(common.getid(sp.id)),
        'speciality':common.getstring(sp.speciality)
      }
      splist.append(objsp)
     
    json_splist = {"specialitycount":len(sps),"specialitylist":splist}      

    return json.dumps(json_splist)
  
  
  def rolelist(self):
    db = self.db
    providerid = self.providerid    
    
    rls = db( (db.role_default.is_active == True)).select()
    #if(providerid == 0):
      #rls = db( (db.role_default.is_active == True)).select()
    #else:
      #rls = db((db.role.providerid == providerid) & (db.role.is_active == True)).select()
    
    rllist = []
    for rl in rls:
      objlr = {}
      objrl = {
        'roleid':int(common.getid(rl.id)),
        'role':common.getstring(rl.role)
      }
      rllist.append(objrl)
     
    json_rllist = {"rolecount":len(rls),"rolelist":rllist}      
    
    return json.dumps(json_rllist)

  def new_staff(self,avars):
    db = self.db
    auth  = current.auth
    rspobj = {}
    
    try:
      
      ref_code = common.getkeyvalue(avars,"ref_code","")
      ref_id   = int(common.getkeyvalue(avars,"providerid",0))
      
      role = common.getkeyvalue(avars,"role","Receptionist")
      roles = db((db.role_default.is_active == True) & (db.role_default.role == role)).select()
      roleid = 4 if(len(roles) == 0) else roles[0].id
      
      staffid = db.doctor.insert(\
        name=common.getkeyvalue(avars,"name",""),
        providerid=common.getkeyvalue(avars,"providerid","1"),
        role=str(roleid),
        
        email=common.getkeyvalue(avars,"email",""),
        cell=common.getkeyvalue(avars,"cell",""),
        stafftype=common.getkeyvalue(avars,"stafftype","Staff"),

        is_active = True,
        created_on=common.getISTFormatCurrentLocatTime(),
        modified_on=common.getISTFormatCurrentLocatTime(),
        created_by = 1 if(auth.user == None) else auth.user.id,
        modified_by= 1 if(auth.user == None) else auth.user.id        
        
      )
    
    
      #refcode = "DOC","PROV"
      db.doctor_ref.insert(doctor_id = staffid, ref_code = ref_code,ref_id = ref_id)
    
      rspobj = {
        "ref_code":ref_code,
        "ref_id":ref_id,
    
        "staffid":str(staffid),
       
        "result":"success",
        "error_message":"",
        "error_code":""
      }            
      
     
      
    except Exception as e:
      mssg = "New Staff Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = "MDP100"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)
      
    
    return json.dumps(rspobj)
  
  
  def new_doctor(self,avars):
    db = self.db
    auth  = current.auth
    rspobj = {}
    
    try:
      
      ref_code = common.getkeyvalue(avars,"ref_code","")
      ref_id   = int(common.getkeyvalue(avars,"providerid",0))
      
      doctorid = db.doctor.insert(\
        title=common.getkeyvalue(avars,"title",""),
        name=common.getkeyvalue(avars,"name",""),
        providerid=common.getkeyvalue(avars,"providerid","1"),
        speciality=common.getkeyvalue(avars,"speciality","1"),
        role=common.getkeyvalue(avars,"role","1"),
        practice_owner=common.getboolean(common.getkeyvalue(avars,"practice_owner","False")),
        email=common.getkeyvalue(avars,"email",""),
        cell=common.getkeyvalue(avars,"cell",""),
        registration=common.getkeyvalue(avars,"registration",""),
        color=common.getkeyvalue(avars,"color",""),
        stafftype=common.getkeyvalue(avars,"stafftype",""),
        state_registration=common.getkeyvalue(avars,"state_registration",""),
        pan=common.getkeyvalue(avars,"pan",""),
        adhaar=common.getkeyvalue(avars,"adhaar",""),
        status=common.getkeyvalue(avars,"status","Open"),
        approval_date=common.getkeyvalue(avars,"approval_date",datetime.datetime.today()),
        notes=common.getkeyvalue(avars,"notes",""),
        docsms=common.getboolean(common.getkeyvalue(avars,"docsms","True")),
        docemail=common.getboolean(common.getkeyvalue(avars,"docemail","True")),
        groupsms=common.getboolean(common.getkeyvalue(avars,"groupsms","True")),
        groupemail=common.getboolean(common.getkeyvalue(avars,"groupemail","True")),
        
        hv_doc=common.getboolean(common.getkeyvalue(avars,"hv_doc","False")),
        hv_doc_gender=common.getkeyvalue(avars,"hv_doc_gender","Male"),
        hv_doc_dob=common.getkeyvalue(avars,"hv_doc_dob","01/01/1900"),
        
        hv_doc_address1=common.getkeyvalue(avars,"hv_doc_address1",""),
        hv_doc_address2=common.getkeyvalue(avars,"hv_doc_address2",""),
        hv_doc_address3=common.getkeyvalue(avars,"hv_doc_address3",""),
        hv_doc_city=common.getkeyvalue(avars,"hv_doc_city",""),
        hv_doc_st=common.getkeyvalue(avars,"hv_doc_st",""),
        hv_doc_pin=common.getkeyvalue(avars,"hv_doc_pin",""),
        
        
        is_active = True,
        created_on=common.getISTFormatCurrentLocatTime(),
        modified_on=common.getISTFormatCurrentLocatTime(),
        created_by = 1 if(auth.user == None) else auth.user.id,
        modified_by= 1 if(auth.user == None) else auth.user.id        
        
      )
    
    
      #refcode = "DOC","PROV"
      db.doctor_ref.insert(doctor_id = doctorid, ref_code = ref_code,ref_id = ref_id)
    
      rspobj = {
        "ref_code":ref_code,
        "ref_id":ref_id,
    
        "doctorid":str(doctorid),
       
        "result":"success",
        "error_message":"",
        "error_code":""
      }            
      
      #add speciality in speciality tab;
      
    except Exception as e:
      mssg = "New Doctor Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = "MDP100"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)
      
    
    return json.dumps(rspobj)
  
  

  def update_hv_doctor(self,avars):
    db = self.db
    auth  = current.auth
    rspobj = {}

    logger.loggerpms2.info("Enter update HV Doctor")

    try:
      hv_doctorid = int(common.getkeyvalue(avars,'hv_doctorid',"0"))
      ds = db((db.hv_doctor.id == hv_doctorid) & (db.hv_doctor.is_active == True)).select()
      if(len(ds) != 1):
        rspobj = {
          "hv_doctorid":str(hv_doctorid),
          "result":"fail",
          "error_message":"Error Updating HV Doctor",
          "error_code":""
        }                
        return json.dumps(rspobj)

     
        
      dobstr = common.getstringfromdate(ds[0].hv_doc_dob, "%d/%m/%Y")
      db(db.hv_doctor.id == hv_doctorid).update(\

        hv_doc_ID=common.getkeyvalue(avars,"hv_doc_ID",ds[0].hv_doc_ID),
        hv_doc_fname=common.getkeyvalue(avars,"hv_doc_fname",ds[0].hv_doc_fname),
        hv_doc_lname=common.getkeyvalue(avars,"hv_doc_lname",ds[0].hv_doc_lname),
        hv_doc_gender=common.getkeyvalue(avars,"hv_doc_gender",ds[0].hv_doc_gender),
        hv_doc_dob=common.getkeyvalue(avars,"hv_doc_dob",dobstr),
        hv_doc_email=common.getkeyvalue(avars,"hv_doc_email",ds[0].hv_doc_email),
        hv_doc_cell=common.getkeyvalue(avars,"hv_doc_cell",ds[0].hv_doc_cell),
        hv_doc_speciality=int(common.getkeyvalue(avars,"hv_doc_speciality",str(ds[0].hv_doc_speciality))),
        hv_doc_role=int(common.getkeyvalue(avars,"hv_doc_role",str(ds[0].hv_doc_role))),
        hv_doc_registration=common.getkeyvalue(avars,"hv_doc_registration",ds[0].hv_doc_registration),
        hv_doc_certification=common.getkeyvalue(avars,"hv_doc_certification",ds[0].hv_doc_certification),
        hv_doc_pan=common.getkeyvalue(avars,"hv_doc_pan",ds[0].hv_doc_pan),
        hv_doc_aadhar=common.getkeyvalue(avars,"hv_doc_aadhar",ds[0].hv_doc_aadhar),
        
        hv_doc_address1=common.getkeyvalue(avars,"hv_doc_address1",ds[0].hv_doc_address1),
        hv_doc_address2=common.getkeyvalue(avars,"hv_doc_address2",ds[0].hv_doc_address2),
        hv_doc_address3=common.getkeyvalue(avars,"hv_doc_address3",ds[0].hv_doc_address3),
        hv_doc_city=common.getkeyvalue(avars,"hv_doc_city",ds[0].hv_doc_city),
        hv_doc_st=common.getkeyvalue(avars,"hv_doc_st",ds[0].hv_doc_st),
        hv_doc_pin=common.getkeyvalue(avars,"hv_doc_pin",ds[0].hv_doc_pin),

        hv_doc_profile_image=common.getkeyvalue(avars,"hv_doc_profile_image",ds[0].hv_doc_profile_image),
        hv_doc_imageid=int(common.getkeyvalue(avars,"hv_doc_imageid",ds[0].hv_doc_imageid)),
        hv_doc_stafftype=common.getkeyvalue(avars,"hv_doc_stafftype",ds[0].hv_doc_stafftype),
        
        hv_doc_notes=common.getkeyvalue(avars,"hv_doc_notes",ds[0].hv_doc_notes),
        
        

        modified_on=common.getISTFormatCurrentLocatTime(),
        modified_by= 1 if(auth.user == None) else auth.user.id
      )
      rspobj = {
        "hv_doctorid":str(hv_doctorid),
        "result":"success",
        "error_message":"",
        "error_code":""
      }              
                        
    except Exception as e:
      mssg = "Update HV Doctor Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = "MDP100"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)

    return json.dumps(rspobj)
  
  
 

  def get_hv_doctor(self,avars):
    db = self.db
    auth  = current.auth
    rspobj = {}
    

    try:
      hv_doctorid = int(common.getkeyvalue(avars,"hv_doctorid",0))
     
      if(hv_doctorid == 0):
        rspobj = {
          "hv_doctorid":str(hv_doctorid),
          "result":"success",
          "error_message":"No Doctor has been assigned for Home Visit",
          "error_code":""
        }                
        return json.dumps(rspobj)
        
      ds = db((db.hv_doctor.id == hv_doctorid) & (db.hv_doctor.is_active == True)).select()


      if(len(ds) != 1):
        rspobj = {

          "hv_doctorid":str(hv_doctorid),
          "result":"fail",
          "error_message":"Error Getting HV Doctor Details - no or duplicate record",
          "error_code":""
        }                
        return json.dumps(rspobj)


        
      hv_doc_speciality = ds[0].hv_doc_speciality
      s = db((db.speciality_default.id == hv_doc_speciality) & (db.speciality_default.is_active == True)).select()
      speciality_name = s[0].speciality if len(s) == 1 else ""
      
      hv_doc_role = ds[0].hv_doc_role
      r = db((db.role_default.id == hv_doc_role) & (db.role_default.is_active == True)).select()
      role_name = r[0].role if len(r) == 1 else ""
      
        
      rspobj = {
        
        "hv_doctorid":str(hv_doctorid),
        "doctorid":str(ds[0].doctorid),
        
        
        "speciality_name":speciality_name,
        "hv_doc_speciality":str(hv_doc_speciality),
        
        "hv_doc_role":str(ds[0].hv_doc_role),
        "role_name":role_name,
        
        "hv_doc_ID":ds[0].hv_doc_ID,
      
        "hv_doc_fname":ds[0].hv_doc_fname,
        "hv_doc_lname":ds[0].hv_doc_lname,
        "hv_doc_gender":ds[0].hv_doc_gender,
        "hv_doc_dob":common.getstringfromdate(ds[0].hv_doc_dob,"%d/%m/%Y"),
        "hv_doc_cell":ds[0].hv_doc_cell,
        "hv_doc_email":ds[0].hv_doc_email,
        
        "hv_doc_address1":ds[0].hv_doc_address1,
        "hv_doc_address1":ds[0].hv_doc_address1,
        "hv_doc_address1":ds[0].hv_doc_address1,
        "hv_doc_city":ds[0].hv_doc_city,
        "hv_doc_st":ds[0].hv_doc_st,
        "hv_doc_pin":ds[0].hv_doc_pin,
        
        "hv_doc_aadhar":ds[0].hv_doc_aadhar,
        "hv_doc_pan":ds[0].hv_doc_pan,
        "hv_doc_registration":ds[0].hv_doc_registration,
        "hv_doc_certification":ds[0].hv_doc_certification,
        
        "hv_doc_profile_image":ds[0].hv_doc_profile_image,
        "hv_doc_imageid":ds[0].hv_doc_imageid,
        
        "hv_doc_stafftype":ds[0].hv_doc_stafftype,

        "hv_doc_notes":ds[0].hv_doc_notes,

        "result":"success",
        "error_message":"",
        "error_code":""          
        
      }

    except Exception as e:
      mssg = "Get HV Doctor Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = "MDP100"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)

    return json.dumps(rspobj)

  #assign hv_doctor to an appointment
  #{
  #   hv_doctorid
  #   hv_appointmentid
  #   city
  # }
  def assign_hv_doctor(self,avars):
    logger.loggerpms2.info("Enter Assign HV Doctor " + json.dumps(avars))      
    db = self.db
    auth  = current.auth
    rspobj = {}
    
    try:
      
      hv_doctorid = common.getkeyvalue(avars,'hv_doctorid',0)
      hv_appointmentid = common.getkeyvalue(avars,'hv_appointmentid',0)
      db(db.hv_doc_appointment.id == hv_appointmentid).update(\
        hv_doctorid = hv_doctorid
      )
      
      rspobj["result"] = "success"
      rspobj["error_message"] = ""
      rspobj["error_code"] = ""
      
      
    except Exception as e:
        mssg = "Assign HV Doctor Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = "MDP100"
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
      
      
    dmp = json.dumps(rspobj)   
    logger.loggerpms2.info("Exit assign_hv_doctor " + dmp)
    return dmp

  #creates a new HV doctor and also refers to in doctor_ref table with rf_code = HVD
  def new_hv_doctor(self,avars):
      db = self.db
      auth  = current.auth
      rspobj = {}
      
      try:
       
        ref_code = "PRV"
        
        p = db(db.provider.provider == 'P0001').select(db.provider.id)
        providerid = p[0].id if(len(p)==1) else 0
        
        practice_owner = False
        
        
        hv_doctorid = db.hv_doctor.insert(\
         
          hv_doc_fname=common.getkeyvalue(avars,"hv_doc_fname",""),
          hv_doc_lname=common.getkeyvalue(avars,"hv_doc_lname",""),
          hv_doc_gender=common.getkeyvalue(avars,"hv_doc_gender","Male"),
          hv_doc_dob=common.getdatefromstring(common.getkeyvalue(avars,"hv_doc_dob","01/01/1900"),"%d/%m/%Y"),
          
          hv_doc_address1=common.getkeyvalue(avars,"hv_doc_address1","331-332 Ganpat Plaza"),
          hv_doc_address2=common.getkeyvalue(avars,"hv_doc_address2","MI Road"),
          hv_doc_address3=common.getkeyvalue(avars,"hv_doc_address3",""),
          hv_doc_city=common.getkeyvalue(avars,"hv_doc_city","Jaipur"),
          hv_doc_st=common.getkeyvalue(avars,"hv_doc_st","Rajastha (RJ)"),
          hv_doc_pin=common.getkeyvalue(avars,"hv_doc_pin","302001"),

          hv_doc_aadhar=common.getkeyvalue(avars,"hv_doc_aadhar",""),
          hv_doc_pan=common.getkeyvalue(avars,"hv_doc_pan",""),
          hv_doc_registration=common.getkeyvalue(avars,"hv_doc_registration",""),
          hv_doc_certification=common.getkeyvalue(avars,"hv_doc_certification",""),

          hv_doc_speciality=common.getkeyvalue(avars,"hv_doc_speciality","1"),
          hv_doc_role=common.getkeyvalue(avars,"hv_doc_role","1"),
          
          
          hv_doc_cell=common.getkeyvalue(avars,"hv_doc_cell",""),
          hv_doc_email=common.getkeyvalue(avars,"hv_doc_email",""),
          
          hv_doc_stafftype=common.getkeyvalue(avars,"hv_doc_stafftype",""),
          hv_doc_notes=common.getkeyvalue(avars,"hv_doc_notes",""),
          
        
          is_active = True,
          created_on=common.getISTFormatCurrentLocatTime(),
          modified_on=common.getISTFormatCurrentLocatTime(),
          created_by = 1 if(auth.user == None) else auth.user.id,
          modified_by= 1 if(auth.user == None) else auth.user.id        
          
        )
        hv_doc_ID = common.getkeyvalue(avars,"hv_doc_ID","HV_DOC_ID_" + str(hv_doctorid))
        db(db.hv_doctor.id == hv_doctorid).update(hv_doc_ID = hv_doc_ID)
      
        docobj  = {
        "action":"new_doctor",
        "ref_code":"PRV",
        "ref_id":str(providerid),
        "title":hv_doc_ID,
        "name":common.getkeyvalue(avars,"hv_doc_fname","") + " " + common.getkeyvalue(avars,"hv_doc_lname",""),
        "providerid":str(providerid),
        "speciality":common.getkeyvalue(avars,"hv_doc_speciality","1"),
        "role":common.getkeyvalue(avars,"hv_doc_role","1"),
        "practice_owner":"False",
        "email":common.getkeyvalue(avars,"hv_doc_email",""),
        "cell":common.getkeyvalue(avars,"hv_doc_cell",""),
        "registration":common.getkeyvalue(avars,"hv_doc_registration",""),
        "state_registration":common.getkeyvalue(avars,"hv_doc_certification",""),
        
        "color":"red",
        "stafftype":"Doctor",
        "pan":common.getkeyvalue(avars,"hv_doc_pan",""),
        "adhaar":common.getkeyvalue(avars,"hv_doc_aadhar",""),
        
        "notes":common.getkeyvalue(avars,"hv_doc_notes",""),
        "docsms":"False",
        "docemail":"False",
        "groupsms":"Flase",
        "groupemail":"False",
        
        "hv_doc":"True",
        "hv_doc_address1":common.getkeyvalue(avars,"hv_doc_address1","331-332 Ganpat Plaza"),
        "hv_doc_address2":common.getkeyvalue(avars,"hv_doc_address2","MI Road"),
        "hv_doc_address3":common.getkeyvalue(avars,"hv_doc_address3",""),
        "hv_doc_city":common.getkeyvalue(avars,"hv_doc_city","Jaipur"),
        "hv_doc_st":common.getkeyvalue(avars,"hv_doc_st","Rajastha (RJ)"),
        "hv_doc_pin":common.getkeyvalue(avars,"hv_doc_pin","302001"),
        "hv_doc_gender":common.getkeyvalue(avars,"hv_doc_gender","Male"),
        "hv_doc_dob":common.getdatefromstring(common.getkeyvalue(avars,"hv_doc_dob","01/01/1900"),"%d/%m/%Y"),
        }  
        
        docrsp = json.loads(self.new_doctor(docobj))
        if(docrsp["result"] == "success"):
          doctorid = int(common.getid(docrsp["doctorid"]))
          db(db.hv_doctor.id == hv_doctorid).update(doctorid = doctorid)
          rspobj = {
            "doctorid":docrsp["doctorid"],
            "hv_doctorid":str(hv_doctorid),
            "result":"success",
            "error_message":"",
            "error_code":""
          } 
        else:
          rspobj = {
            "result":"fail",
            "error_message":"Error New HV Doctor",
            "error_code":""
          }
          
        
       
        
      except Exception as e:
        mssg = "New HV Doctor Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = "MDP100"
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
      
      
      dmp = json.dumps(rspobj)   
      logger.loggerpms2.info("Exit new_hv_doctor " + dmp)
      return dmp
  
  #this api returns a list of HV Doctor
  #the HV doctors belong to MDP Default Provider P0001
  def list_hv_doctor(self,avars):
    
    db = self.db
    auth  = current.auth
    
    rspobj = {}
    
    try:
      lst = []
      obj = {}
      ds = None
      
      city = common.getkeyvalue(avars,"city","")
      qry = (db.hv_doctor.hv_doc_city == city) if(city != "") else (1==1)
      
      ds = db((qry)&(db.hv_doctor.hv_doc_stafftype == 'Doctor') & (db.hv_doctor.is_active == True)).select()
      for d in ds:
        s = db(db.speciality_default.id == d.hv_doc_speciality).select(db.speciality_default.speciality)
        r = db(db.role_default.id == d.hv_doc_role).select(db.role_default.role)
        
        obj = {
          "doctorid":d.doctorid,
          
          "hv_doctorid":d.id,
          "hv_doc_ID":d.hv_doc_ID,
          "hv_doc_fname":d.hv_doc_fname,
          "hv_doc_lname":d.hv_doc_lname,
          "hv_doc_cell":common.modify_cell(d.hv_doc_cell),
          "hv_doc_email":d.hv_doc_email,
       
          "hv_doc_address1":d.hv_doc_address1,
          "hv_doc_address2":d.hv_doc_address2,
          "hv_doc_address3":d.hv_doc_address3,
          "hv_doc_city":d.hv_doc_city,
          "hv_doc_st":d.hv_doc_st,
          "hv_doc_pin":d.hv_doc_pin,
          
          "hv_doc_aadhar":d.hv_doc_aadhar,
          "hv_doc_pan":d.hv_doc_pan,
          "hv_doc_registration":d.hv_doc_registration,
          "hv_doc_certification":d.hv_doc_certification,
          
          "hv_doc_dob":common.getstringfromdate(d.hv_doc_dob,"%d/%m/%Y"),
          "hv_doc_gender":d.hv_doc_gender,
          "hv_doc_role":d.hv_doc_role,
          
          "hv_doc_stafftype":d.hv_doc_stafftype,
          "hv_doc_notes":d.hv_doc_notes,

          "hv_doc_speciality":d.hv_doc_speciality,
          "speciality_name":s[0].speciality if(len(s) > 0) else "",
          "role_name":r[0].role if(len(r) > 0) else "",
          
          "hv_doc_profile_image":d.hv_doc_profile_image,
          "hv_doc_imageid":d.hv_doc_imageid,


          
        }
        lst.append(obj)
      
      
      rspobj["result"]="success"
      rspobj["error_code"]=""
      rspobj["error_message"]=""
      rspobj["count"] = len(lst)
      rspobj["list"]=lst
      
    except Exception as e:
      mssg = "List HV Doctor Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = "MDP100"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)
      
    
    return json.dumps(rspobj)
  
  
  def list_doctor(self,avars):
    
    
    db = self.db
    auth  = current.auth
    rspobj = {}
    
    try:
      ref_code = avars["ref_code"] if "ref_code" in avars else ""
      ref_id = int(common.getid(avars["ref_id"])) if "ref_id" in avars else 0            

      lst = []
      obj = {}
      ds = None
      
      if(ref_code == ""):
        if(ref_id == 0):
          ds = db( (db.doctor.stafftype == 'Doctor') & (db.doctor.is_active == True)).select(db.doctor.ALL,db.doctor_ref.ALL,\
                                                          left=db.doctor.on((db.doctor.id == db.doctor_ref.doctor_id)))
          
        else:
          ds = db((db.doctor.stafftype == 'Doctor') & (db.doctor.id == ref_id)&(db.doctor.is_active == True)).select(db.doctor.ALL,db.doctor_ref.ALL,\
                                                          left=db.doctor.on((db.doctor.id == db.doctor_ref.doctor_id)))
      else:
        if(ref_id == 0):
          ds = db((db.doctor.stafftype == 'Doctor') & (db.doctor_ref.ref_code == ref_code)&(db.doctor.is_active == True)).select(db.doctor.ALL,db.doctor_ref.ALL,\
                                                          left=db.doctor.on((db.doctor.id == db.doctor_ref.doctor_id)))
        else:
          ds = db((db.doctor.stafftype == 'Doctor') & (db.doctor_ref.ref_code == ref_code)&(db.doctor_ref.ref_id == ref_id)&(db.doctor.is_active == True)).select(db.doctor.ALL,db.doctor_ref.ALL,\
                                                            left=db.doctor.on((db.doctor.id == db.doctor_ref.doctor_id)))

      for d in ds:
        
        p = db((db.provider.id == d.doctor_ref.ref_id)).select(db.provider.provider)
        
        if(len(p)==1):
          provider = p[0].provider if len(p) == 1 else 0
          s = None
          if(provider > 0):
            s = db((db.speciality.specialityid == d.doctor.speciality) & (db.speciality.providerid == ref_id) & (db.speciality.is_active == True)).select()
            speciality_name = s[0].speciality if len(s) == 1 else ""
            speciality = s[0].specialityid if len(s) == 1 else 0            
            if(len(s) == 0):
              s = db((db.speciality_default.id == d.doctor.speciality) & (db.speciality_default.is_active == True)).select()
              speciality_name = s[0].speciality if len(s) == 1 else ""
              speciality = s[0].id if len(s) == 1 else 0              
          else:
            s = db((db.speciality_default.id == d.doctor.speciality) & (db.speciality_default.is_active == True)).select()
            speciality_name = s[0].speciality if len(s) == 1 else ""
            speciality = s[0].id if len(s) == 1 else 0            
          
          obj = {
            "ref_code":d.doctor_ref.ref_code,     #DOC
            "ref_id":d.doctor_ref.ref_id,         #ID to either doctor table or provider table
            "provider":provider,
           
            "doctorid":d.doctor.id,
            "name":d.doctor.name,
            "cell":d.doctor.cell,
            "email":d.doctor.email,
            "practice_owner":str(d.doctor.practice_owner),
            "status":d.doctor.status,
            "speciality":speciality,
            "speciality_name":speciality_name
            
          }
          lst.append(obj)
      
      
      rspobj["result"]="success"
      rspobj["error_code"]=""
      rspobj["error_message"]=""
      rspobj["count"] = len(lst)
      rspobj["list"]=lst
      
    except Exception as e:
      mssg = "List Doctor Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = "MDP100"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)
      
    
    return json.dumps(rspobj)

  def list_staff(self,avars):
      
      
      db = self.db
      auth  = current.auth
      rspobj = {}
      
      try:
        ref_code = avars["ref_code"] if "ref_code" in avars else ""
        providerid = int(common.getid(avars["providerid"])) if "providerid" in avars else 0            
        ref_id = providerid
         
        lst = []
        obj = {}
        ds = None
        
        if(ref_code == ""):
          if(ref_id == 0):
            ds = db((db.doctor.stafftype == 'Staff') & (db.doctor.is_active == True)).select(db.doctor.ALL,db.doctor_ref.ALL,\
                                                            left=db.doctor.on((db.doctor.id == db.doctor_ref.doctor_id)))
            
          else:
            ds = db((db.doctor.stafftype == 'Staff') & (db.doctor.id == ref_id)&(db.doctor.is_active == True)).select(db.doctor.ALL,db.doctor_ref.ALL,\
                                                            left=db.doctor.on((db.doctor.id == db.doctor_ref.doctor_id)))
        else:
          if(ref_id == 0):
            ds = db((db.doctor.stafftype == 'Staff') & (db.doctor_ref.ref_code == ref_code)&(db.doctor.is_active == True)).select(db.doctor.ALL,db.doctor_ref.ALL,\
                                                            left=db.doctor.on((db.doctor.id == db.doctor_ref.doctor_id)))
          else:
            ds = db((db.doctor.stafftype == 'Staff') & (db.doctor_ref.ref_code == ref_code)&(db.doctor_ref.ref_id == ref_id)&(db.doctor.is_active == True)).select(db.doctor.ALL,db.doctor_ref.ALL,\
                                                              left=db.doctor.on((db.doctor.id == db.doctor_ref.doctor_id)))
  
        for d in ds:
          
          p = db((db.provider.id == d.doctor_ref.ref_id)).select(db.provider.provider)
          
          if(len(p)==1):
            provider = p[0].provider if len(p) == 1 else 0
           
            roleid = int(common.getid(d.doctor.role))
            r=db(db.role_default.id == roleid).select()
            role = "Receptionist" if(len(r) == 0) else r[0].role
          
            
            obj = {
              "ref_code":d.doctor_ref.ref_code,     #DOC
              "ref_id":d.doctor_ref.ref_id,         #ID to either doctor table or provider table
              "provider":provider,
              "role":role,
              "roleid":str(roleid),
              "staffid":d.doctor.id,
              "name":d.doctor.name,
              "cell":d.doctor.cell,
              "email":d.doctor.email,
            }
            lst.append(obj)
        
        
        rspobj["result"]="success"
        rspobj["error_code"]=""
        rspobj["error_message"]=""
        rspobj["count"] = len(lst)
        rspobj["list"]=lst
        
      except Exception as e:
        mssg = "List Staff Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = "MDP100"
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
        
      
      return json.dumps(rspobj)
              
  def get_doctor(self,avars):
    db = self.db
    auth  = current.auth
    rspobj = {}
    

    try:
      doctorid = int(common.getkeyvalue(avars,"doctorid",0))
      r = db(db.doctor_ref.doctor_id ==doctorid).select()
      ref_code = r[0].ref_code if len(r) == 1 else ""
      ref_id = int(r[0].ref_id) if len(r) == 1 else 0
      
      ds = db((db.doctor.id == doctorid) & (db.doctor.is_active == True)).select()


      if(len(ds) != 1):
        rspobj = {

          "doctorid":str(doctorid),
          "result":"fail",
          "error_message":"Error Getting Doctor Details - no or duplicate record",
          "error_code":""
        }                
        return json.dumps(rspobj)

      provider = ""
      providerid = 0
      if((ref_code == "PRV")):
        r = db(db.provider.id == ref_id).select(db.provider.provider)
        provider = r[0].provider if len(r) == 1 else ""
        providerid = ref_id
        
       
      s = db((db.speciality.specialityid == ds[0].speciality) & (db.speciality.providerid == ref_id) & (db.speciality.is_active == True)).select()
      speciality_name = s[0].speciality if len(s) == 1 else ""
      speciality = ds[0].speciality
      
      dt = ds[0].approval_date
      if((dt == None)|(dt == "")):
        dtstr = ""
      else:
        dtstr = common.getstringfromdate(dt,"%d/%m/%Y")
        
      rspobj = {
        
        "ref_code":ref_code,
        "ref_id":ref_id,
        "providerid":str(ref_id),
        "provider":provider,
        
        "speciality_name":speciality_name,
        "speciality":str(speciality),
        "name":ds[0].name,
        "providerid":str(ds[0].providerid),
        "role":ds[0].role,
        "practice_owner":str(ds[0].practice_owner),
        "email":ds[0].email,
        "cell":ds[0].cell,
        "registration":ds[0].registration,
        "color":ds[0].color,
        "stafftype":ds[0].stafftype,
        "state_registration":ds[0].state_registration,
        "pan":ds[0].pan,
        "adhaar":ds[0].adhaar,
        "status":ds[0].status,
        "approval_date": dtstr,
        "notes":ds[0].notes,
        "docsms":str(ds[0].docsms),
        "docemail":str(ds[0].docemail),
        "groupsms":str(ds[0].groupsms),
        "groupemail":str(ds[0].groupemail),
        "result":"success",
        "error_message":"",
        "error_code":""          
        
      }

    except Exception as e:
      mssg = "Get Doctor Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = "MDP100"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)

    return json.dumps(rspobj)
  
  def get_staff(self,avars):
      db = self.db
      auth  = current.auth
      rspobj = {}
      
  
      try:
        staffid = int(common.getkeyvalue(avars,"staffid",0))
        r = db(db.doctor_ref.doctor_id ==staffid).select()
        ref_code = r[0].ref_code if len(r) == 1 else ""
        ref_id = int(r[0].ref_id) if len(r) == 1 else 0
        
        ds = db((db.doctor.id == staffid) & (db.doctor.is_active == True)).select()
        roleid = 0 if (len(ds) == 0) else int(common.getid(ds[0].role))
        r=db(db.role_default.id == roleid).select()
        role = "Receptionist" if(len(r) == 0) else r[0].role  

        if(len(ds) != 1):
          rspobj = {
  
            "staffid":str(staffid),
            "result":"fail",
            "error_message":"Error Getting Staff Details - no or duplicate record",
            "error_code":""
          }                
          return json.dumps(rspobj)
  
        provider = ""
        providerid = 0
        if((ref_code == "PRV")):
          r = db(db.provider.id == ref_id).select(db.provider.provider)
          provider = r[0].provider if len(r) == 1 else ""
          providerid = ref_id
          
         
       
          
        rspobj = {
          
          "ref_code":ref_code,
          "ref_id":ref_id,
       
          "provider":provider,
          
          
          "name":ds[0].name,
          "providerid":str(ds[0].providerid),
          "role":role,
          "roleid":str(roleid),
          
          "email":ds[0].email,
          "cell":ds[0].cell,
         
          "result":"success",
          "error_message":"",
          "error_code":""          
          
        }
  
      except Exception as e:
        mssg = " Get Staff Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = "MDP100"
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
  
      return json.dumps(rspobj)
  
  def update_doctor(self,avars):
    db = self.db
    auth  = current.auth
    rspobj = {}

    logger.loggerpms2.info("Enter new Clinic ")

    try:
      doctorid = int(common.getkeyvalue(avars,'doctorid',"0"))
      ds = db((db.doctor.id == doctorid) & (db.doctor.is_active == True)).select()
      if(len(ds) != 1):
        rspobj = {
          "doctorid":str(doctorid),
          "result":"fail",
          "error_message":"Error Updating Doctor - no clinic record",
          "error_code":""
        }                
        return json.dumps(rspobj)

      dt = ds[0].approval_date
      dtstr = ""
      if((dt==None)|(dt=="")):
        dtstr = ""
      else:
        dtstr = common.getstringfromdate(dt,"%d/%m/%Y")
      
      dtstr = common.getkeyvalue(avars,"approval_date",dtstr)
      if((dtstr != None)&(dtstr != "")):
        dt = common.getdatefromstring(dtstr,"%d/%m/%Y")
      else:
        dt = None
        
      db(db.doctor.id == doctorid).update(\

        title=common.getkeyvalue(avars,"title",ds[0].title),
        name=common.getkeyvalue(avars,"name",ds[0].name),
        providerid=int(common.getkeyvalue(avars,"providerid",str(ds[0].providerid))),
        speciality=int(common.getkeyvalue(avars,"speciality",str(ds[0].speciality))),
        role=int(common.getkeyvalue(avars,"role",str(ds[0].role))),
        practice_owner=common.getboolean(common.getkeyvalue(avars,"practice_owner",ds[0].practice_owner)),
        email=common.getkeyvalue(avars,"email",ds[0].email),
        cell=common.getkeyvalue(avars,"cell",ds[0].cell),
        registration=common.getkeyvalue(avars,"registration",ds[0].registration),
        color=common.getkeyvalue(avars,"color",ds[0].color),
        stafftype=common.getkeyvalue(avars,"stafftype",ds[0].stafftype),
        state_registration=common.getkeyvalue(avars,"state_registration",ds[0].state_registration),
        pan=common.getkeyvalue(avars,"pan",ds[0].pan),
        adhaar=common.getkeyvalue(avars,"adhaar",ds[0].adhaar),
        status=common.getkeyvalue(avars,"status",ds[0].status),
        approval_date=dt,
        notes=common.getkeyvalue(avars,"notes",ds[0].notes),
        docsms=common.getboolean(common.getkeyvalue(avars,"docsms",ds[0].docsms)),
        docemail=common.getboolean(common.getkeyvalue(avars,"docemail",ds[0].docemail)),
        groupsms=common.getboolean(common.getkeyvalue(avars,"groupsms",ds[0].groupsms)),
        groupemail=common.getboolean(common.getkeyvalue(avars,"groupemail",ds[0].groupemail)),

        modified_on=common.getISTFormatCurrentLocatTime(),
        modified_by= 1 if(auth.user == None) else auth.user.id
      )
      rspobj = {
        "doctorid":str(doctorid),
        "result":"success",
        "error_message":"",
        "error_code":""
      }              
                        
    except Exception as e:
      mssg = "Update Doctor Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = "MDP100"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)

    return json.dumps(rspobj)
  
  def update_staff(self,avars):
      db = self.db
      auth  = current.auth
      rspobj = {}
  
      logger.loggerpms2.info("Enter Update Stss")
  
      try:
        staffid = int(common.getkeyvalue(avars,'staffid',"0"))
        ds = db((db.doctor.id == staffid) & (db.doctor.is_active == True)).select()
        if(len(ds) != 1):
          rspobj = {
            "staffid":str(staffid),
            "result":"fail",
            "error_message":"Error Updating Staff - no clinic record",
            "error_code":""
          }                
          return json.dumps(rspobj)
  
  
        role = common.getkeyvalue(avars,"role","Receptionist")
        r=db(db.role_default.role == role).select()
        roleid = 4 if(len(r) == 0) else int(r[0].id)
               
        db(db.doctor.id == staffid).update(\
  
          
          name=common.getkeyvalue(avars,"name",ds[0].name),
          providerid=int(common.getkeyvalue(avars,"providerid",str(ds[0].providerid))),
         
          role=str(roleid),
          
          email=common.getkeyvalue(avars,"email",ds[0].email),
          cell=common.getkeyvalue(avars,"cell",ds[0].cell),
         
          stafftype=common.getkeyvalue(avars,"stafftype",ds[0].stafftype),
          modified_on=common.getISTFormatCurrentLocatTime(),
          modified_by= 1 if(auth.user == None) else auth.user.id
        )
        rspobj = {
          "staffid":str(staffid),
          "result":"success",
          "error_message":"",
          "error_code":""
        }              
                          
      except Exception as e:
        mssg = "Update Doctor Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = "MDP100"
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
  
      return json.dumps(rspobj)
      
  def delete_hv_doctor(self,avars):
    auth  = current.auth
    db = self.db
  
    try:
  
      hv_doctorid = int(common.getkeyvalue(avars,"hv_doctorid",0))
  
      db(db.hv_doctor.id == hv_doctorid).update(\
        is_active = False,
        modified_on=common.getISTFormatCurrentLocatTime(),
        modified_by= 1 if(auth.user == None) else auth.user.id
  
      )
  
      rspobj = {
        'hv_doctorid': hv_doctorid,
        'result' : 'success',
        "error_code":"",
        "error_message":""
      }               
  
  
    except Exception as e:
      mssg = "DeleteHV  Doctor Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = "MDP100"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)
  
    return json.dumps(rspobj)  
  
  
  def delete_doctor(self,avars):
    auth  = current.auth
    db = self.db
  
    try:
  
      doctorid = int(common.getkeyvalue(avars,"doctorid",0))
  
      db(db.doctor.id == doctorid).update(\
        is_active = False,
        modified_on=common.getISTFormatCurrentLocatTime(),
        modified_by= 1 if(auth.user == None) else auth.user.id
  
      )
  
      rspobj = {
        'doctorid': doctorid,
        'result' : 'success',
        "error_code":"",
        "error_message":""
      }               
  
  
    except Exception as e:
      mssg = "Delete Doctor Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = "MDP100"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)
  
    return json.dumps(rspobj)  
  
  def delete_staff(self,avars):
    auth  = current.auth
    db = self.db
  
    try:
  
      staffid = int(common.getkeyvalue(avars,"staffid",0))
  
      db(db.doctor.id == staffid).update(\
        is_active = False,
        modified_on=common.getISTFormatCurrentLocatTime(),
        modified_by= 1 if(auth.user == None) else auth.user.id
  
      )
  
      rspobj = {
        'staffid': staffid,
        'result' : 'success',
        "error_code":"",
        "error_message":""
      }               
  
  
    except Exception as e:
      mssg = "Delete Staff Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = "MDP100"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)
  
    return json.dumps(rspobj)  
  
  #{
    #"action":"new_hv_doc_appointment",
    #"user_id": Login id in auth_user table
    #"memberid":25720,
    #"patientid":25720,
    #"cell":"9137908350",
    #"complaint":"Tooth Ache",
    #"appointment_start":"01/07/2023 09:00",
    #"duration":30,
    #"notes":"This is the first visit"
  #}
  def new_hv_doc_appointment(self,avars):
    
    auth  = current.auth
    db = self.db
    
    rspobj = {}
  
    try:
      
      
      #provider id = P0001
      p = db((db.provider.provider == "P0001") & (db.provider.is_active == True)).select(db.provider.id)
      providerid = p[0].id if (len(p) > 0) else 0
      
      
      #find the clinic id corr to this provider
      c = db((db.clinic_ref.ref_code == "PRV") & (db.clinic_ref.ref_id == providerid)).select()
      clinicid = c[0].clinic_id if(len(c) > 0) else 0
  
      #default doctor id (practice owner)
      d = db((db.doctor.providerid == providerid) & (db.doctor.practice_owner == True)).select()
      def_doctorid = d[0].id if len(d) > 0 else 0
      hv_doctorid = int(common.getkeyvalue(avars,"hv_doctorid","0"))
      
      hvdoc = db((db.hv_doctor.id == hv_doctorid) & (db.hv_doctor.is_active == True)).select()
      doctorid = hvdoc[0].doctorid if(len(hvdoc) > 0) else def_doctorid
      
      appointment_start_AMPM = common.getkeyvalue(avars,"appointment_start","")
      appointment_start = common.convert12to24clock(appointment_start_AMPM)
      
      avars["providerid"] = str(providerid)
      avars["clinicid"] = str(clinicid)
      avars["doctorid"] = str(doctorid)
      del avars["appointment_start"]
      avars["appointment_start"] = appointment_start
      apptObj = mdpappointment.Appointment(db, providerid)
      rspobj = json.loads(apptObj.new_appointment(avars))
      
      if(rspobj["result"] == "success"):
        
        #add to hv_doc_appointment
        refid = db.hv_doc_appointment.insert(appointmentid=rspobj["appointmentid"],
                                             hv_doctorid = hv_doctorid,
                                             hv_appt_status="Open",
                                             hv_appt_address1 = common.getkeyvalue(avars,"hv_appt_address1","131-132 Ganpat Plaza MI Road"),
                                             hv_appt_address2 = common.getkeyvalue(avars,"hv_appt_address2",""),
                                             hv_appt_address3 = common.getkeyvalue(avars,"hv_appt_address3",""),
                                             hv_appt_city = common.getkeyvalue(avars,"hv_appt_city","Jaipur"),
                                             hv_appt_st = common.getkeyvalue(avars,"hv_appt_st","Rajasthan (RJ)"),
                                             hv_appt_pin=common.getkeyvalue(avars,"hv_appt_pin","302001"),
                                             hv_appt_city_id=common.getkeyvalue(avars,"hv_appt_city_id","0"),
                                             hv_appt_latitude=common.getkeyvalue(avars,"hv_appt_latitude",""),
                                             hv_appt_longitude=common.getkeyvalue(avars,"hv_appt_longitude",""),
                                             hv_appt_payment_txid=common.getkeyvalue(avars,"hv_appt_payment_txid","0"),
                                             hv_appt_payment_amount=common.getkeyvalue(avars,"hv_appt_payment_amount","0"),
                                             hv_appt_payment_date=common.getdatefromstring(
                                               common.getkeyvalue(avars,"hv_appt_payment_date",common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y")),"%d/%m/%Y"),
                                             hv_appt_created_on = common.getISTFormatCurrentLocatTime(),
                                             hv_appt_created_by = common.getkeyvalue(avars,"user_id", str(1) if(auth.user == None) else str(auth.user.id)),
                                             
                                             )
        apptid = int(rspobj["appointmentid"])
        db(db.t_appointment.id == apptid).update(f_status = "Open")
        
        rspobj["hv_appointmentid"] = str(refid)
        
        
        
        memberid = common.getkeyvalue(avars,"memberid","0")
        patientid = common.getkeyvalue(avars,"patientid","0")
        
        #set the provider to default provider P0001 = 95
        db(db.patientmember.id == memberid).update(provider = providerid)
        
        r = db((db.patientmember.id == memberid)).select()
        addr = ""
        if(len(r)>0):
          addr = common.getstring(r[0].address1)
          addr = addr + (" " + r[0].address2) if (common.getstring(r[0].address2) != "") else ""
          addr = addr + (" " + r[0].address3) if (common.getstring(r[0].address3) != "") else ""
          addr = addr + (" " + r[0].city) if (common.getstring(r[0].city) != "") else ""
          addr = addr + (" " + r[0].st) if (common.getstring(r[0].st) != "") else ""
          addr = addr + (" " + r[0].pin) if (common.getstring(r[0].pin) != "") else ""
        
        rspobj["hv_address"] = addr

        #create a dummy treatment against this Appointment for the Home Visit Treatment
        #"action":"new_hv_treatment",
          #"memberid":25713,
          #"patientid":25713,
          #"hv_doctorid":10,
          #"hv_doc_appointmentid":1        
        xavars = {}
        xavars["memberid"] = str(memberid)
        xavars["patientid"] = str(patientid)
        xavars["hv_doctorid"] = str(hv_doctorid)
        xavars["hv_doc_appointmentid"] = str(refid)
        trobj = json.loads(self.new_hv_treatment(xavars))
        if(trobj["result"] == "success"):
          hv_treatmentid = int(common.getid(trobj["hv_treatmentid"]))
          
          r = db(db.hv_treatment.id == hv_treatmentid).select(db.hv_treatment.treatmentid)
          
          treatmentid = r[0].treatmentid if(len(r) > 0) else 0
          db(db.hv_doc_appointment.id == refid).update(\
            hv_treatmentid = trobj["hv_treatmentid"],
            treatmentid = treatmentid
          )
          rspobj["hv_treatmentid"] =trobj["hv_treatmentid"]
          rspobj["treatmentid"] =treatmentid
          rspobj["providerid"] = str(providerid)
      
          #get cost hv_fees
          #for now, we will get hv_fees from cities table.
          m = db(db.patientmember.id == memberid).select(db.patientmember.city)
          city = m[0].city if(len(m) > 0) else ""
          c = db((db.cities.city == city) & (db.cities.HV == True)).select()
          hv_fees = c[0].hv_fees if(len(c) > 0) else 0
          rspobj["hv_fees"] = hv_fees
          
          #this is the actual way but requires corr. population of ProcedurePricePlan table
          #tp = db(db.treatment.id == treatmentid).select(db.treatment.treatmentplan)
          #tplanid = tp[0].treatmentplan if(len(tp)>0) else 0
          #tobj = mdptreatment.Treatment(db,providerid)
          #rsp = tobj.updatetreatmentcostandcopay(treatmentid, tplanid)
          #if(rsp["result"] == "success"):
            #rspobj["hv_fees"] = rsp["copay"]
          #else:
            #rspobj["hv_fees"] = 0
            
    except Exception as e:
      mssg = "New HV DOC Appointment Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = ""
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)
  
    
    return json.dumps(rspobj)
  
  
 

  
  def get_hv_doc_appointment(self,avars):

    auth  = current.auth
    db = self.db

    rspobj = {}

    try:
      hv_doc_appointmentid = int(common.getkeyvalue(avars,"hv_doc_appointmentid","0"))

      r = db(db.hv_doc_appointment.id == hv_doc_appointmentid ).select()
      
      if(len(r) <= 0):
        mssg = "No HV DOC Appointment for this id " + str(hv_doc_appointmentid)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)        

      hv_doctorid = 0 if(len(r) <= 0) else int(r[0].hv_doctorid)

      xobj = {"hv_doctorid":str(hv_doctorid)}
      hv_doctor_obj = json.loads(self.get_hv_doctor(xobj))

      apptid = 0 if(len(r) <= 0) else int(r[0].appointmentid)
      apptobj = mdpappointment.Appointment(db, self.providerid)
      xobj = {"appointmentid":str(apptid),"showcancelled":True}
      apptobj = json.loads(apptobj.get_appointment(xobj))



      rspobj["result"] = "success"
      rspobj["hv_doctor"] = hv_doctor_obj
      rspobj["appointment"] = apptobj

      
      memberid = int(common.getid(common.getkeyvalue(apptobj,"memberid","0")))
      patientid = int(common.getid(common.getkeyvalue(apptobj,"patientid","0")))
      pats = db((db.patientmember.id == memberid) &\
                (db.patientmember.is_active == True)).select()
      
      rspobj["hv_patient_profile"]= "" if(len(pats)<=0) else pats[0].image
      rspobj["hv_patient_imageid"]= "" if(len(pats)<=0) else pats[0].imageid

      rspobj["hv_appt_created_on"] = common.getstringfromtime(r[0].hv_appt_created_on, "%d/%m/%Y %H:%M")
      rspobj["hv_appt_created_by"] = r[0].hv_appt_created_by 
      rspobj["hv_appt_confirmed_on"] = common.getstringfromtime(r[0].hv_appt_confirmed_on, "%d/%m/%Y %H:%M")
      rspobj["hv_appt_confirmed_by"] = r[0].hv_appt_confirmed_by 
      rspobj["hv_appt_checkedin_on"] = common.getstringfromtime(r[0].hv_appt_checkedin_on, "%d/%m/%Y %H:%M")
      rspobj["hv_appt_checkedin_by"] = r[0].hv_appt_checkedin_by
      rspobj["hv_appt_checkedout_on"] = common.getstringfromtime(r[0].hv_appt_checkedout_on, "%d/%m/%Y %H:%M")
      rspobj["hv_appt_checkedout_by"] = r[0].hv_appt_checkedout_by
      rspobj["hv_appt_cancelled_on"] = common.getstringfromtime(r[0].hv_appt_cancelled_on, "%d/%m/%Y %H:%M")
      rspobj["hv_appt_cancelled_by"] = r[0].hv_appt_cancelled_by 
      
      rspobj["hv_appt_feedback_on"] = common.getstringfromtime(r[0].hv_appt_feedback_on, "%d/%m/%Y %H:%M")
      rspobj["hv_appt_feedback_by"] = r[0].hv_appt_feedback_by 
      
      rspobj["hv_appt_status"] = r[0].hv_appt_status 
      
      rspobj["hv_appt_distance"] = r[0].hv_appt_distance 
      rspobj["hv_appt_notes"] =r[0].hv_appt_notes 

      rspobj["hv_appt_address1"] =r[0].hv_appt_address1  
      rspobj["hv_appt_address2"] =r[0].hv_appt_address2
      rspobj["hv_appt_address3"] =r[0].hv_appt_address3 
      rspobj["hv_appt_city"] =r[0].hv_appt_city  
      rspobj["hv_appt_st"] =r[0].hv_appt_st 
      rspobj["hv_appt_pin"] =r[0].hv_appt_pin
      rspobj["hv_appt_city_id"] =r[0].hv_appt_city_id  
      rspobj["hv_appt_latitude"] =r[0].hv_appt_latitude 
      rspobj["hv_appt_longitude"] =r[0].hv_appt_longitude 
       
      rspobj["hv_appt_payment_txid"] = str(r[0].hv_appt_payment_txid)
      rspobj["hv_appt_payment_amount"] = r[0].hv_appt_payment_amount 
      rspobj["hv_appt_payment_date"] =common.getstringfromdate(r[0].hv_appt_payment_date,"%d/%m/%Y")

      rspobj["feedback_posted"] = True if int(common.getid(r[0].hv_appt_feedback_by) > 0) else False






    except Exception as e:
      mssg = "New HV DOC Appointment Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = ""
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)


    return json.dumps(rspobj)  
  
  def xget_hv_doc_appointment(self,avars):
    
    auth  = current.auth
    db = self.db
    
    rspobj = {}
    
    try:
      #hv_doc_appointmentid
      hv_doc_appointmentid = int(common.getid(common.getkeyvalue(avars,"hv_doc_appointmentid","0")))
      
      
      qry = (db.hv_doc_appointment.id == hv_doc_appointmentid)
      
      appts = db(qry).select(db.hv_doc_appointment.ALL, db.t_appointment.ALL, left=db.t_appointment.on(db.t_appointment.id == db.hv_doc_appointment.appointmentid))

      hv_apptlst = []
      hv_apptobj = {}
      
      for appt in appts:
        
        hv_apptobj = {}
        
        hv_apptobj["hv_doc_appointmentid"] = appt.hv_doc_appointment.id
        hv_apptobj["appointmentid"] = appt.hv_doc_appointment.appointmentid
        hv_apptobj["hv_doctorid"] = appt.hv_doc_appointment.hv_doctorid

        hv_apptobj["patient_name"] = appt.t_appointment.f_patientname
        hv_apptobj["appointment_date"] = common.getstringfromtime(appt.t_appointment.f_start_time,"%d/%m/%Y %I:%M %p")
        
        memberid = appt.t_appointment.patientmember
        patientid = appt.t_appointment.patient
        
        p = db((db.patientmember.id == memberid)).\
          select(db.patientmember.address1,db.patientmember.address2,db.patientmember.address3,db.patientmember.city,\
                 db.patientmember.st,db.patientmember.pin,db.patientmember.cell,db.patientmember.gender,db.patientmember.dob)
        
        address = "" if(len(p) <= 0) else p[0].address1 + " " + p[0].address2 + " " + p[0].address3 + " " + p[0].city + " " + p[0].st + " " + p[0].pin
        hv_apptobj["patient_address"] = address
        hv_apptobj["patient_cell"] = common.modify_cell("" if(len(p) <= 0) else p[0].cell )
        hv_apptobj["patient_gender"] = "" if(len(p) <= 0) else p[0].gender 
        
        today = date.today()
        year = today.year
        dob =  "" if(len(p) <= 0) else p[0].dob 
        age =0
        if(dob != ""):
          age = year - dob.year
          
        
        hv_apptobj["patient_age"] = age

        
        hv_doctorid = appt.hv_doc_appointment.hv_doctorid
        h = db(db.hv_doctor.id == hv_doctorid).select()
        hv_apptobj["hv_doctor_name"] = "" if(len(h) <= 0) else h[0].hv_doc_fname + " " + h[0].hv_doc_lname
        hv_apptobj["hv_doctor_address"] = "" if(len(h) <= 0) else h[0].hv_doc_address1 + " " + h[0].hv_doc_address2 + " " + h[0].hv_doc_address3 + " " + h[0].hv_doc_city + " " + h[0].hv_doc_st+ " " + h[0].hv_doc_pin
        hv_apptobj["hv_doctor_cell"] = "" if(len(h) <= 0) else h[0].hv_doc_cell 
        
        hv_apptlst.append(hv_apptobj)
      
      rspobj["result"]="success"
      rspobj["error_message"]=""
      rspobj["hv_appointment"]=hv_apptobj
        
        
      
    except Exception as e:
      mssg = "List HV DOC Appointment Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = ""
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)
  
    
    return json.dumps(rspobj)    
    
  #API to get a list of all home visit appointments for a HV Doctor
  #If HV_Doctor is 0, then return list of all hv appointments of all HV Doctors
  def list_hv_doc_appointment(self,avars):
    
    auth  = current.auth
    db = self.db
    
    rspobj = {}
  
    try:
      
      #user ID
      user_id = int(common.getkeyvalue(avars,"user_id","0"))
      
      #hv_doctorid
      hv_doctorid = int(common.getid(common.getkeyvalue(avars,"hv_doctorid","0")))
      
      #appointmnet status, if not specified then appointment with all status is returned
      status = common.getkeyvalue(avars,"status","")
      
      qry = (1==1)
      
      if(user_id != 0):
        qry = qry & (db.hv_doc_appointment.hv_appt_created_by == user_id)
        
      if(hv_doctorid != 0):
        qry = qry & (db.hv_doc_appointment.hv_doctorid == hv_doctorid)
      
      if(status != ""):
        qry = qry & (db.t_appointment.f_status == status)
        
      
      appts = db(qry).select(db.hv_doc_appointment.ALL, db.t_appointment.ALL, left=db.t_appointment.on(db.t_appointment.id == db.hv_doc_appointment.appointmentid))
      hv_apptlst = []
      hv_apptobj = {}
      
      for appt in appts:
        
        hv_apptobj = {}
        hv_apptobj["hv_appt_address1"] = appt.hv_doc_appointment.hv_appt_address1
        hv_apptobj["hv_appt_address2"] = appt.hv_doc_appointment.hv_appt_address2
        hv_apptobj["hv_appt_address3"] = appt.hv_doc_appointment.hv_appt_address3
        hv_apptobj["hv_appt_city"] = appt.hv_doc_appointment.hv_appt_city
        hv_apptobj["hv_appt_st"] = appt.hv_doc_appointment.hv_appt_st
        hv_apptobj["hv_appt_pin"] = appt.hv_doc_appointment.hv_appt_pin
        hv_apptobj["hv_appt_longitude"] = appt.hv_doc_appointment.hv_appt_longitude
        hv_apptobj["hv_appt_latitude"] = appt.hv_doc_appointment.hv_appt_latitude
        hv_apptobj["hv_appt_city_id"] = appt.hv_doc_appointment.hv_appt_city_id
        
        hv_apptobj["hv_appt_status"] = appt.t_appointment.f_status
        hv_apptobj["hv_doc_appointmentid"] = appt.hv_doc_appointment.id
        hv_apptobj["appointmentid"] = appt.hv_doc_appointment.appointmentid
        hv_apptobj["hv_doctorid"] = appt.hv_doc_appointment.hv_doctorid

        hv_apptobj["patient_name"] = appt.t_appointment.f_patientname
        hv_apptobj["appointment_date"] = common.getstringfromtime(appt.t_appointment.f_start_time,"%d/%m/%Y %I:%M %p")
        
        memberid = appt.t_appointment.patientmember
        patientid = appt.t_appointment.patient
        
        p = db((db.patientmember.id == memberid)).select()
        
        address = "" if(len(p) <= 0) else p[0].address1 + " " + p[0].address2 + " " + p[0].address3 + " " + p[0].city + " " + p[0].st + " " + p[0].pin
        hv_apptobj["patient_address"] = address
        hv_apptobj["patient_cell"] = common.modify_cell("" if(len(p) <= 0) else p[0].cell )
        hv_apptobj["patient_gender"] = "" if(len(p) <= 0) else p[0].gender 
        hv_apptobj["patient_profile_image"] = "" if(len(p) <= 0) else p[0].image 
        hv_apptobj["patient_imageid"] = 0 if(len(p) <= 0) else int(common.getid(p[0].imageid))
        
        hv_doc = db(db.hv_doctor.id == appt.hv_doc_appointment.hv_doctorid).select()
        hv_apptobj["hv_doc_profile_image"] = "" if(len(hv_doc) <= 0) else hv_doc[0].hv_doc_profile_image
        hv_apptobj["hv_doc_imageid"] = 0 if(len(hv_doc) <= 0) else int(common.getid(hv_doc[0].hv_doc_imageid))
        hv_apptobj["hv_doctor_name"] = "" if(len(hv_doc) <= 0) else hv_doc[0].hv_doc_fname + " " + hv_doc[0].hv_doc_lname
        hv_apptobj["hv_doctor_address"] = "" if(len(hv_doc) <= 0) else hv_doc[0].hv_doc_address1 + " " + hv_doc[0].hv_doc_address2 + " " +\
          hv_doc[0].hv_doc_address3 + " " + hv_doc[0].hv_doc_city + " " +hv_doc[0].hv_doc_st+ " " + hv_doc[0].hv_doc_pin
        hv_apptobj["hv_doctor_cell"] = "" if(len(hv_doc) <= 0) else hv_doc[0].hv_doc_cell 
        
        today = date.today()
        year = today.year
        dob =  "" if(len(p) <= 0) else p[0].dob 
        age =0
        if(dob != ""):
          age = year - dob.year
          
        
        hv_apptobj["patient_age"] = age

        
       
        
        hv_apptlst.append(hv_apptobj)
      
        
       
      
      rspobj["result"]="success"
      rspobj["error_message"]=""
      rspobj["hv_appointment_list"]=hv_apptlst
        
        
      
    except Exception as e:
      mssg = "List HV DOC Appointment Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = ""
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)
  
    
    return json.dumps(rspobj)    


  def update_hv_doc_appointment(self,avars):
      auth  = current.auth
      db = self.db
      rspobj = {}
      try:
        hv_doc_appointmentid = int(common.getkeyvalue(avars,"hv_doc_appointmentid","0"))
        
        r = db(db.hv_doc_appointment.id == hv_doc_appointmentid ).select()
        
        apptid = 0 if(len(r) <= 0) else int(r[0].appointmentid)
        
        avars["appointmentid"] = apptid
        
        apptobj = mdpappointment.Appointment(db, self.providerid)
        rspobj = json.loads(apptobj.update_appointment(avars))
        
        rspobj["result"] = "success"
        rspobj["error_code"] = ""
        rspobj["error_message"] = ""
        
      except Exception as e:
        mssg = "Update HV DOC Appointment Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
    
      
      return json.dumps(rspobj)

  def new_hv_appt_feedback(self,avars):
      auth  = current.auth
      db = self.db
      rspobj = {}
      try:
        hv_appointmentid = int(common.getkeyvalue(avars,"hv_appointmentid","0"))
        
        r = db(db.hv_doc_appointment.id == hv_appointmentid).select()
        if(len(r) <=0):
          mssg = "No Appointment for appointment = "  + str(hv_appointmentid)
          rspobj["result"] = "fail"
          rspobj["error_code"] = ""
          rspobj["error_message"] = mssg
          logger.loggerpms2.info(mssg)
          return json.dumps(rspobj)
        
        feedback_posted = True if int(common.getid(r[0].hv_appt_feedback_by) > 0) else False
          
                 
        hv_appt_feedback = (common.getkeyvalue(avars,"hv_appt_feedback",""))
        hv_appt_rating = (common.getkeyvalue(avars,"hv_appt_rating",""))
        hv_appt_user_id = common.getkeyvalue(avars,"hv_appt_user_id",1 if(auth.user == None) else auth.user.id)
        
        db((db.hv_doc_appointment.id == hv_appointmentid) & (feedback_posted == False)).update(
        hv_appt_rating = hv_appt_rating,
        hv_appt_feedback= hv_appt_feedback,
        hv_appt_feedback_on = common.getISTFormatCurrentLocatTime(),
        hv_appt_feedback_by = hv_appt_user_id
        )
                
        if(feedback_posted):
          mssg = "Feedback was already provided earlier! No new feedbacks updated!"
        else:
          mssg = "New Feedback updated !"
          
        rspobj["result"] = "success"
        rspobj["error_code"] = ""
        rspobj["error_message"] = mssg
        rspobj["feedback_posted"] = feedback_posted
        
      except Exception as e:
        mssg = "new_hv_appt_feedback  Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
    
      
      return json.dumps(rspobj)

  def get_hv_appt_feedback(self,avars):
      auth  = current.auth
      db = self.db
      rspobj = {}
      try:
        hv_appointmentid = int(common.getkeyvalue(avars,"hv_appointmentid","0"))
        
        f = db(db.hv_doc_appointment.id == hv_appointmentid).select()
        
        
                
        
        rspobj["result"] = "success"
        rspobj["error_code"] = ""
        rspobj["error_message"] = ""
        rspobj["hv_appt_feedback"] = f[0].hv_appt_feedback if(len(f) >0) else ""
        rspobj["hv_appt_rating"] = f[0].hv_appt_rating if(len(f) >0) else ""
        rspobj["hv_appt_feedback_on"] = common.getstringfromdate(f[0].hv_appt_feedback_on if(len(f) >0) else datetime.datetime.today(), "%d/%m/%Y")
        rspobj["hv_appt_feedback_by"] = f[0].hv_appt_feedback_by if(len(f) >0) else 1
        
      except Exception as e:
        mssg = "get_hv_appt_feedback  Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
    
      
      return json.dumps(rspobj)

  def get_device_info(self,avars):
    
    auth  = current.auth
    db = self.db
    rspobj = {}
    try:
      device_id = common.getkeyvalue(avars,"device_id","0")
      
      f = db(db.device_info.device_id == device_id).select()
      
      rspobj["result"] = "success"
      rspobj["error_code"] = ""
      rspobj["error_message"] = ""
      rspobj["device_id"] = f[0].device_id if(len(f) >0) else "0"
      rspobj["device_type"] = f[0].device_type if(len(f) >0) else ""
      rspobj["device_fcm_token"] = f[0].device_type if(len(f) >0) else ""
      
    except Exception as e:
      mssg = "get_device_info  Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = ""
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)
  
    
    return json.dumps(rspobj)

  def add_device_info(self,avars):
    
    auth  = current.auth
    db = self.db
    rspobj = {}
    try:
      device_id = common.getkeyvalue(avars,"device_id","")
      
      
      db.device_info.update_or_insert(db.device_info.device_id == device_id,
                                      device_id = device_id,
                                      device_type = common.getkeyvalue(avars,"device_type",""),
                                      device_fcm_token = common.getkeyvalue(avars,"device_fcm_token","")
                                      )
      rspobj["result"] = "success"
      rspobj["error_code"] = ""
      rspobj["error_message"] = ""
      
    except Exception as e:
      mssg = "add_device_info  Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = ""
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)
  
    
    return json.dumps(rspobj)

  
  def checkin_hv_doc_appointment(self,avars):
      auth  = current.auth
      db = self.db
      rspobj = {}
      try:
        hv_doc_appointmentid = int(common.getkeyvalue(avars,"hv_doc_appointmentid","0"))
        h = db(db.hv_doc_appointment.id == hv_doc_appointmentid).select(db.hv_doc_appointment.appointmentid)
        appointmentid = 0 if(len(h) <= 0) else h[0].appointmentid
        avars["appointmentid"] = appointmentid
        apptobj = mdpappointment.Appointment(db,self.providerid)
        rspobj=json.loads(apptobj.checkIn(avars))
        if(rspobj["result"] == "success"):
          hv_doc_appointmentid = int(common.getkeyvalue(avars,"hv_doc_appointmentid","0"))
          db(db.hv_doc_appointment.id == hv_doc_appointmentid).update\
             (
               hv_appt_notes = common.getkeyvalue(avars,"notes",""),
               hv_appt_status = "Checked-In",
               hv_appt_checkedin_on = common.getISTFormatCurrentLocatTime(),
               hv_appt_checkedin_by = str(1) if(auth.user == None) else str(auth.user.id)
             )
          rspobj={}
          rspobj["result"] = "success"
          rspobj["error_message"] = ""
          rspobj["error_code"] = ""
          rspobj["hv_doc_appointmentid"] = hv_doc_appointmentid
          
        else:
          rspobj={}
          rspobj["result"] = "fail"
          rspobj["error_message"] = "Error Chech-In Appointment"
          rspobj["error_code"] = ""
          rspobj["hv_doc_appointmentid"] = hv_doc_appointmentid
          
        
      except Exception as e:
        mssg = "Checkedin HV DOC Appointment Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
    
      
      return json.dumps(rspobj)

  def checkout_hv_doc_appointment(self,avars):
      auth  = current.auth
      db = self.db
      rspobj = {}
      try:
        hv_doc_appointmentid = int(common.getkeyvalue(avars,"hv_doc_appointmentid","0"))
        h = db(db.hv_doc_appointment.id == hv_doc_appointmentid).select(db.hv_doc_appointment.appointmentid)
        appointmentid = 0 if(len(h) <= 0) else h[0].appointmentid
        avars["appointmentid"] = appointmentid       
        apptobj = mdpappointment.Appointment(db,self.providerid)
        rspobj=json.loads(apptobj.checkOut(avars))
        if(rspobj["result"] == "success"):
          hv_doc_appointmentid = int(common.getkeyvalue(avars,"hv_doc_appointmentid","0"))
          db((db.hv_doc_appointment.id == hv_doc_appointmentid)).update\
             (
               hv_appt_notes = common.getkeyvalue(avars,"notes",""),
               hv_appt_status = "Checked-Out",
               hv_appt_checkedout_on = common.getISTFormatCurrentLocatTime(),
               hv_appt_checkedout_by = str(1) if(auth.user == None) else str(auth.user.id)
             )
          rspobj={}
          rspobj["result"] = "success"
          rspobj["error_message"] = ""
          rspobj["error_code"] = ""
          rspobj["hv_doc_appointmentid"] = hv_doc_appointmentid
                  
        else:
          rspobj={}
          rspobj["result"] = "fail"
          rspobj["error_message"] = "Error Chech-Out Appointment"
          rspobj["error_code"] = ""
          rspobj["hv_doc_appointmentid"] = hv_doc_appointmentid          
        
      except Exception as e:
        mssg = "Checkedout HV DOC Appointment Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
    
      
      return json.dumps(rspobj)
    
  def confirm_hv_doc_appointment(self,avars):
      auth  = current.auth
      db = self.db
      rspobj = {}
      try:
        hv_doc_appointmentid = int(common.getkeyvalue(avars,"hv_doc_appointmentid","0"))
        h = db(db.hv_doc_appointment.id == hv_doc_appointmentid).select(db.hv_doc_appointment.appointmentid)
        appointmentid = 0 if(len(h) <= 0) else h[0].appointmentid
        avars["appointmentid"] = appointmentid       
       
        apptobj = mdpappointment.Appointment(db,self.providerid)
        rspobj=json.loads(apptobj.confirm(avars))
        if(rspobj["result"] == "success"):
          hv_doc_appointmentid = int(common.getkeyvalue(avars,"hv_doc_appointmentid","0"))
          db((db.hv_doc_appointment.id == hv_doc_appointmentid)).update\
             (
               hv_appt_notes = common.getkeyvalue(avars,"notes",""),
               hv_appt_status = "Confirmed",
               hv_appt_confirmed_on = common.getISTFormatCurrentLocatTime(),
               hv_appt_confirmed_by = str(1) if(auth.user == None) else str(auth.user.id)
             )
          
          rspobj={}
          rspobj["result"] = "success"
          rspobj["error_message"] = ""
          rspobj["error_code"] = ""
          rspobj["hv_doc_appointmentid"] = hv_doc_appointmentid
                  
        else:
          rspobj={}
          rspobj["result"] = "fail"
          rspobj["error_message"] = "Error Confirm Appointment"
          rspobj["error_code"] = ""
          rspobj["hv_doc_appointmentid"] = hv_doc_appointmentid          
        
      except Exception as e:
        mssg = "Confirmed HV DOC Appointment Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
    
      
      return json.dumps(rspobj)
  
  def cancel_hv_doc_appointment(self,avars):
      auth  = current.auth
      db = self.db
      rspobj = {}
      try:
        hv_doc_appointmentid = int(common.getkeyvalue(avars,"hv_doc_appointmentid","0"))
        h = db(db.hv_doc_appointment.id == hv_doc_appointmentid).select(db.hv_doc_appointment.appointmentid)
        appointmentid = 0 if(len(h) <= 0) else h[0].appointmentid
        avars["appointmentid"] = appointmentid       
     
        apptobj = mdpappointment.Appointment(db,self.providerid)
        rspobj=json.loads(apptobj.cancel_appointment(avars))
        
        if(rspobj["result"] == "success"):
          hv_doc_appointmentid = int(common.getkeyvalue(avars,"hv_doc_appointmentid","0"))
          db((db.hv_doc_appointment.id == hv_doc_appointmentid) ).update\
             (
               hv_appt_notes = common.getkeyvalue(avars,"notes",""),
               hv_appt_status = "Cancelled",
               hv_appt_cancelled_on = common.getISTFormatCurrentLocatTime(),
               hv_appt_cancelled_by = str(1) if(auth.user == None) else str(auth.user.id)
             )
          rspobj={}
          rspobj["result"] = "success"
          rspobj["error_message"] = ""
          rspobj["error_code"] = ""
          rspobj["hv_doc_appointmentid"] = hv_doc_appointmentid
                  
        else:
          rspobj={}
          rspobj["result"] = "fail"
          rspobj["error_message"] = "Error Cancel Appointment"
          rspobj["error_code"] = ""
          rspobj["hv_doc_appointmentid"] = hv_doc_appointmentid          
          
        
      except Exception as e:
        mssg = "Cancelled HV DOC Appointment Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
    
      
      return json.dumps(rspobj)
  
 
 
  #API to update HV Treatment
  def update_hv_treatment(self,avars):
      auth  = current.auth
      db = self.db
      rspobj = {}
   
      try:
        #default provider and clinic to Provider P0001
        #provider id = P0001
        p = db((db.provider.provider == "P0001") & (db.provider.is_active == True)).select(db.provider.id)
        providerid = p[0].id if (len(p) > 0) else 0
        
        #find the clinic id corr to this provider
        c = db((db.clinic_ref.ref_code == "PRV") & (db.clinic_ref.ref_id == providerid)).select()
        clinicid = c[0].clinic_id if(len(c) > 0) else 0
  
        #dotorid  
        hv_doctorid = int(common.getkeyvalue(avars,"hv_doctorid","0"))
        d = db(db.hv_doctor.id == hv_doctorid).select()
        doctorid = 0 if(len(d) <= 0) else d[0].doctorid
  
        #create new treatment
        trobj = mdptreatment.Treatment(db, providerid)
        trobj = json.loads(trobj.newtreatment_clinic(avars))
        
        
        if(trobj["result"] == "success"):
          #{
            #"action": "addproceduretotreatment",
            #"providerid": 1011,
            #"procedurecode": "G0200",
            #"treatmentid": 3250,
            #"plan": "CC104",
            #"tooth": "12",
            #"quadrant": "Q4",
            #"remarks": "New Procedure to 3250"
          #}        
          #add procedure treatment
          obj["providerid"] = str(providerid)
          obj["procedurecode"] = "G0108"
          obj["treatmentid"] = common.getkeyvalue(trobj,"treatmentid","0")
          obj["plan"] = common.getkeyvalue(avars,"plan","PREMWALKIN")
          obj["tooth"] = common.getkeyvalue(avars,"tooth","")
          obj["quadrant"] = common.getkeyvalue(avars,"quadrant","")
          obj["remarks"] = common.getkeyvalue(avars,"remarks","")
          
          procObj = mdpprocedure.Procedure(db, providerid)
          rspobj = json.loads(procObj.addproceduretotreatment(obj["procedurecode"], 
                                                             obj["treatmentid"], 
                                                             obj["plan"], 
                                                             obj["tooth"], 
                                                             obj["quadrant"], 
                                                             obj["remarks"]))
        else:
          rspobj["result"]="failure"
          rspobj["error_message"]="Error:New HV Treatment"
        
      except Exception as e:
        mssg = "New HV DOC Treatment Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
      
      return json.dumps(rspobj)
    
  #get_hv_treatment  
  #hv_treatmentid
  #memberid
  #patientid
  #doctorid
  #clinicid
  #policy_name
  #notes
    
  def new_hv_treatment(self,avars):
      auth  = current.auth
      db = self.db
      rspobj = {}
   
      try:
        #default provider and clinic to Provider P0001
        #provider id = P0001
        p = db((db.provider.provider == "P0001") & (db.provider.is_active == True)).select(db.provider.id)
        providerid = p[0].id if (len(p) > 0) else 0
        avars["providerid"] = str(providerid)
        
        #find the clinic id corr to this provider
        c = db((db.clinic_ref.ref_code == "PRV") & (db.clinic_ref.ref_id == providerid)).select()
        clinicid = c[0].clinic_id if(len(c) > 0) else 0
        avars["clinicid"] = str(clinicid)
  
        #dotorid  
        hv_doctorid = int(common.getkeyvalue(avars,"hv_doctorid","0"))
        d = db(db.hv_doctor.id == hv_doctorid).select()
        doctorid = 0 if(len(d) <= 0) else d[0].doctorid
        avars["doctorid"] = str(doctorid)
  
        #assign a plan based on  customer's region
        
        
        
        
        #create new treatment
        avars["hv"] = True
        trobj = mdptreatment.Treatment(db, providerid)
        trobj = json.loads(trobj.newtreatment_clinic(avars))
        
        
        if(trobj["result"] == "success"):
          #{
            #"action": "addproceduretotreatment",
            #"providerid": 1011,
            #"procedurecode": "G0200",
            #"treatmentid": 3250,
            #"plan": "CC104",
            #"tooth": "12",
            #"quadrant": "Q4",
            #"remarks": "New Procedure to 3250"
          #}        
          #add procedure treatment
          obj={}
          obj["providerid"] = str(providerid)
          obj["procedurecode"] = "G0108"
          obj["treatmentid"] = common.getkeyvalue(trobj,"treatmentid","0")
          obj["plan"] = common.getkeyvalue(trobj,"plan","PREMWALKIN")
          obj["tooth"] = common.getkeyvalue(avars,"tooth","")
          obj["quadrant"] = common.getkeyvalue(avars,"quadrant","")
          obj["remarks"] = common.getkeyvalue(avars,"remarks","")
          
          procObj = mdpprocedure.Procedure(db, providerid)
          rspobj = json.loads(procObj.addproceduretotreatment(obj["procedurecode"], 
                                                             obj["treatmentid"], 
                                                             obj["plan"], 
                                                             obj["tooth"], 
                                                             obj["quadrant"], 
                                                             obj["remarks"]))
          
          
          #create new_hv_treatment
          created_on = common.getISTFormatCurrentLocatTime()
          hv_treatmentid = db.hv_treatment.insert(
            hv_doctorid = doctorid,
            treatmentid = int(common.getid(trobj["treatmentid"])),
            treatment = trobj["treatment"],
            hv_doc_appointmentid = common.getkeyvalue(avars,"hv_doc_appointmentid","0"),
            hv_treatment_status = trobj["status"],
            created_on = created_on,
            created_by = 1 if(auth.user == None) else auth.user.id,
            modified_on = created_on,
            modified_by =1 if(auth.user == None) else auth.user.id
          )
          
          if(rspobj["result"]=="success"):
            rspobj={}
            rspobj["result"]="success"
            rspobj["error_message"] = ""
            rspobj["error_code"]=""
            rspobj["hv_treatmentid"]=str(hv_treatmentid)
            rspobj["hv_treatment_status"] =  trobj["status"]
            rspobj["treatment"] =  trobj["treatment"]
            rspobj["hv_treatment_date"] = common.getstringfromtime(created_on,"%d/%m/%Y %H:%M")
          else:
            rspobj={}
            rspobj["result"]="failure"
            rspobj["error_message"]="Error:New HV Treatment (add procedure to treatment)"
            
          
        else:
          rspobj["result"]="failure"
          rspobj["error_message"]="Error:New HV Treatment"
        
      except Exception as e:
        mssg = "New HV DOC Treatment Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
      
      return json.dumps(rspobj)
    
  def get_hv_treatment(self,avars):
      auth  = current.auth
      db = self.db
      rspobj = {}
   
      try:
        
        hv_treatmentid = int(common.getid(common.getkeyvalue(avars,"hv_treatmentid","0")))
        hvt = db(db.hv_treatment.id == hv_treatmentid).select()
        rspobj={}
        if(len(hvt)>0):
          rspobj["treatment"] = hvt[0].treatment
          rspobj["treatmentid"] = hvt[0].treatmentid
          rspobj["hv_doctorid"] = hvt[0].hv_doctorid
          rspobj["hv_doc_appointmentid"] = hvt[0].hv_doc_appointmentid
          rspobj["hv_treatment_status"] = hvt[0].hv_treatment_status
          rspobj["hv_treatment_date"] = common.getstringfromtime(hvt[0].created_on,"%d/%m/%Y %H:%M")
          rspobj["result"]="success"
          rspobj["error_message"] = ""
          rspobj["error_code"]=""
          
        else:
          rspobj={}
          rspobj["result"]="failure"
          rspobj["error_message"]="Error:Get HV Treatment "
          
        
      except Exception as e:
        mssg = "Get HV Treatment Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
      
      return json.dumps(rspobj)

  #hv_appointmentid 
  #this API returns hv_treatment associated with this hv_appointment
  #avars {hv_doc_appointmentid}
  def get_hv_treatment_by_appointment(self,avars):
      auth  = current.auth
      db = self.db
      rspobj = {}
   
      try:
        #get hv_appointmentid from avars
        hv_doc_appointmentid = common.getkeyvalue(avars,"hv_doc_appointmentid","0")
        hvt = db(db.hv_treatment.hv_doc_appointmentid == hv_doc_appointmentid).select()
        hv_treatmentid = 0 if(len(hvt) <= 0) else hvt[0].id
        xavars={}
        xavars["hv_treatmentid"] = hv_treatmentid
        rspobj = json.loads(self.get_hv_treatment(xavars))
        
      except Exception as e:
        mssg = "Get HV DOC Treatment Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
      
      return json.dumps(rspobj)
    
  
  #get list of cities where home visit doctors are available
  def list_hv_cities(self,avars):
      auth  = current.auth
      db = self.db
      rspobj = {}
   
      try:
        #get list of HV Cities. This is a list of cities where HV Doctors are availdle
        
        cities = db(db.cities.HV == True).select()
        citylist = []
        for i in xrange(0,len(cities)):
          cityobj={}
          cityobj["city_id"] = str(cities[i].id)
          cityobj["city"] = cities[i].city
          cityobj["hv_fees"] = common.getvalue(cities[i].hv_fees)
          citylist.append(cityobj)
        
        rspobj={
          
          "result":"success",
          "error_message":"",
          "error_code":"",
          "citylist":citylist
        }
        
        
      except Exception as e:
        mssg = "List HV Cities Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
      
      return json.dumps(rspobj)


  #this API lists open slots
  #the slots can be for a specific appointment date
  #avars={action, appointment_date}
  #
  def list_hv_open_slots_by_day(self,avars):
      auth  = current.auth
      db = self.db
      rspobj = {}
      slotlst = []
      try:
        #provider id = P0001
        p = db((db.provider.provider == "P0001") & (db.provider.is_active == True)).select(db.provider.id)
        providerid = p[0].id if (len(p) > 0) else 0
        
        #find the clinic id corr to this provider
        c = db((db.clinic_ref.ref_code == "PRV") & (db.clinic_ref.ref_id == providerid)).select()
        clinicid = c[0].clinic_id if(len(c) > 0) else 0
        
        
        #city
        city_id = int(common.getkeyvalue(avars,"city_id","0"))
        cities = db(db.cities.id == city_id).select()
        
        city = common.getkeyvalue(avars,"city", cities[0].city if (len(cities) >0) else "Jaipur")
        drs = db(db.hv_doctor.hv_doc_city == city).select()
        slotlst = []
        
        if(len(drs) <= 0):
          rspobj["result"] = "success"
          rspobj["error_message"]="No Open Slots"
          rspobj["error_code"] = ""
          rspobj["city_id"] = city_id
          rspobj["city"] = city
          rspobj["list_open_slots"] = slotlst          
          return json.dumps(rspobj)
        
        for dr in drs:
          if((dr.doctorid == None) | (dr.doctorid == "")):
            continue
          avars["providerid"] = str(providerid)
          avars["doctorid"] = str(dr.doctorid)
          apptObj = mdpappointment.Appointment(db, providerid)
          slotobj = json.loads(apptObj.list_open_slots(avars))
          slotobj = slotobj["list_open_slots"]
          for i in xrange(0,len(slotobj)):
            if(slotobj[i] in slotlst):
              continue
            slotlst.append(slotobj[i])
          
          rspobj["result"] = "success"
          rspobj["error_message"]=""
          rspobj["error_code"] = ""
          rspobj["appointment_date"] = common.getkeyvalue(avars,"appointment_date","")
          rspobj["city_id"] = city_id
          rspobj["city"] = city
          rspobj["list_open_slots"] = slotlst
          
      except Exception as e:
        mssg = "Day Open Slots Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
      
      return json.dumps(rspobj)
      
  #this API lists open slots
  #the slots can be for a specific month
  #avars={action, month,year}
  def list_hv_open_slots_by_month(self,avars):
      auth  = current.auth
      db = self.db
      rspobj = {}
      slotobj = {}
      slotlist = []
      
      try:
        #provider id = P0001
        p = db((db.provider.provider == "P0001") & (db.provider.is_active == True)).select(db.provider.id)
        providerid = p[0].id if (len(p) > 0) else 0
        
        #find the clinic id corr to this provider
        c = db((db.clinic_ref.ref_code == "PRV") & (db.clinic_ref.ref_id == providerid)).select()
        clinicid = c[0].clinic_id if(len(c) > 0) else 0
        
        dt = datetime.date.today()
        day = dt.day
        year = dt.year
        month = dt.month
        
        month = common.getkeyvalue(avars,"month", str(month))
        monthstr = str(month).zfill(2)
        year = common.getkeyvalue(avars,"year", str(year))
        yearstr = str(year).zfill(4)
        
        
        avars["providerid"] = str(providerid)
        avars["clinicid"] = str(clinicid)
        
        for i in xrange(1,32):
          slotobj = {}
          apptdt = str(i).zfill(2) + "/" + monthstr + "/" + yearstr
          avars["appointment_date"] = apptdt
          apptObj = mdpappointment.Appointment(db, providerid)
          slotobj = json.loads(self.list_hv_open_slots_by_day(avars))
          del slotobj["result"]
          del slotobj["error_message"]
          del slotobj["error_code"]
          slotlist.append(slotobj)
        
        rspobj["result"] = "success"
        rspobj["error_message"] = ""
        rspobj["slotlist"] = slotlist
        

      except Exception as e:
        mssg = "Day Open Slots Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_code"] = ""
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
      
      return json.dumps(rspobj)
 