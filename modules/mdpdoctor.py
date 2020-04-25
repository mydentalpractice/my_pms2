import datetime
from datetime import timedelta

import json
from applications.my_pms2.modules import common

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