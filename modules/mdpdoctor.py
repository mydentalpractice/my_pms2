from gluon import current


import datetime
from datetime import timedelta

import json
from applications.my_pms2.modules import common
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
    
    sps = db((db.speciality.providerid == providerid) & (db.speciality.is_active == True)).select()
    
    
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
    
    rls = db((db.role.providerid == providerid) & (db.role.is_active == True)).select()
    
    rllist = []
    for rl in rls:
      
      objrl = {
        'roleid':int(common.getid(rl.id)),
        'role':common.getstring(rl.role)
      }
      rllist.append(objrl)
     
    json_rllist = {"rolecount":len(rls),"rolelist":rllist}      
    
    return json.dumps(json_rllist)
  
  
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
      
      
    except Exception as e:
      mssg = "New Doctor Exception:\n" + str(e)
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
          ds = db((db.doctor.is_active == True)).select(db.doctor.ALL,db.doctor_ref.ALL,\
                                                          left=db.doctor.on((db.doctor.id == db.doctor_ref.doctor_id)))
          
        else:
          ds = db((db.doctor.id == ref_id)&(db.doctor.is_active == True)).select(db.doctor.ALL,db.doctor_ref.ALL,\
                                                          left=db.doctor.on((db.doctor.id == db.doctor_ref.doctor_id)))
      else:
        if(ref_id == 0):
          ds = db((db.doctor_ref.ref_code == ref_code)&(db.doctor.is_active == True)).select(db.doctor.ALL,db.doctor_ref.ALL,\
                                                          left=db.doctor.on((db.doctor.id == db.doctor_ref.doctor_id)))
        else:
          ds = db((db.doctor_ref.ref_code == ref_code)&(db.doctor_ref.ref_id == ref_id)&(db.doctor.is_active == True)).select(db.doctor.ALL,db.doctor_ref.ALL,\
                                                            left=db.doctor.on((db.doctor.id == db.doctor_ref.doctor_id)))

      for d in ds:
        
        p = db(db.provider.id == d.doctor_ref.ref_id).select(db.provider.provider)
        provider = p[0].provider if len(p) == 1 else 0
        s = db((db.speciality.specialityid == d.doctor.speciality) & (db.speciality.providerid == ref_id) & (db.speciality.is_active == True)).select()
        speciality_name = s[0].speciality if len(s) == 1 else ""
        speciality = s[0].specialityid if len(s) == 1 else 0
        obj = {
          "ref_code":d.doctor_ref.ref_code,     #DOC
          "ref_id":d.doctor_ref.ref_id,       #ID to either doctor table or provider table
          "provider":provider,
         
          "name":d.doctor.name,
          "cell":d.doctor.cell,
          "email":d.doctor.email,
          "practice_owner":str(d.doctor.practice_owner),
          "status":d.doctor.status,
          "speciality":str(speciality),
          "speciality_name":speciality_name
          
        }
        lst.append(obj)
      
      
      rspobj["result"]="success"
      rspobj["error_code"]=""
      rspobj["error_message"]=""
      rspobj["count"] = len(lst)
      rspobj["list"]=lst
      
    except Exception as e:
      mssg = "New Doctor Exception:\n" + str(e)
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
      mssg = "Delete Get Docto Exception:\n" + str(e)
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
      mssg = "New Clinic Exception:\n" + str(e)
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