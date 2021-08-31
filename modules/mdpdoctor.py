from gluon import current


import datetime
from datetime import timedelta

import json
from applications.my_pms2.modules import common
from applications.my_pms2.modules import mdpappointment
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
      
      ds = db((db.hv_doctor.hv_doc_stafftype == 'Doctor') & (db.hv_doctor.is_active == True)).select()
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
          "role_name":r[0].role if(len(r) > 0) else ""
          
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
  
      hv_doctorid = int(common.getkeyvalue(avars,"hv_doctorid","0"))
      
      hvdoc = db((db.hv_doctor.id == hv_doctorid) & (db.hv_doctor.is_active == True)).select()
      doctorid = hvdoc[0].doctorid if(len(hvdoc) > 0) else 0
      
      avars["providerid"] = str(providerid)
      avars["clinicid"] = str(clinicid)
      avars["doctorid"] = str(doctorid)
      
      apptObj = mdpappointment.Appointment(db, providerid)
      apptrsp = apptObj.new_appointment(avars)
      
      if(apptrsp["result"] == "success"):
        rspobj["result"] = "success"
        rspobj["error_code"] = ""
        rspobj["error_message"] = ""
        
        
      
    except Exception as e:
      mssg = "New HV DOC Appointment Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_code"] = ""
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)
  
    
    return json.dumps(rspobj)    