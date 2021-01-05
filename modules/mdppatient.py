from gluon import current

import datetime
import time
import calendar
from datetime import timedelta

import json





from applications.my_pms2.modules import common
from applications.my_pms2.modules import gender
from applications.my_pms2.modules import states
from applications.my_pms2.modules import status
from applications.my_pms2.modules import relations
from applications.my_pms2.modules import logger

class Patient:
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    return 
  
  def relations(self):
    return json.dumps(relations.RELATIONS)
  
  def status(self):
    sts = status.STATUS
    
    return json.dumps(sts)
  
  def genders(self):
    
    gr = gender.GENDER
    
    return json.dumps(gr)
  
  def pattitles(self):
    title = gender.PATTITLE
    return json.dumps(title)
  
  def doctitles(self):
    title = gender.DOCTITLE
    return json.dumps(title)
  
  
  def cities(self):
    cities = states.CITIES
    l = list(cities)
    l[0] = '--Select City--'
    cities = tuple(l)
    return json.dumps(cities)
  
  def states(self):
    
    xstates = states.STATES
    l = list(xstates)
    
    l[0] = '--Select State--'
    xstates = tuple(l)
    return json.dumps(xstates)
  
  
  def regionswithid(self):
    logger.loggerpms2.info("Patient->RegionsWithID==>>\n")
    db = self.db
    
    rgns = db(db.groupregion.is_active == True).select(db.groupregion.id,db.groupregion.groupregion)
    
    
    rgnlist = []
    
    for rgn in rgns:
      rgnobj = {'regionid':rgn.id,"groupregion":rgn.groupregion}
      rgnlist.append(rgnobj)
    
    logger.loggerpms2.info("Patient->RegionsWithID==>\n")
    logger.loggerpms2.info(json.dumps(rgnlist))
    return json.dumps(rgnlist)
  
    
  def regions(self):
    
    db = self.db
    
    rgns = db(db.groupregion.is_active == True).select(db.groupregion.groupregion)
    
    
    rgnlist = []
    
    for rgn in rgns:
      rgnlist.append(rgn.groupregion)
    
    
    
    
    
    return json.dumps(rgnlist)
  
  def getMedicalHistory(self,memberid,patientid):
  
    db = self.db
    providerid = self.providerid    
    medhistobj = {}
    
    try:
      medhist = db((db.medicalnotes.patientid == patientid) & (db.medicalnotes.memberid == memberid)).select()
      
      pats = db((db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid == memberid)).\
        select(db.vw_memberpatientlist.dob,db.vw_memberpatientlist.gender)
      
      
      ageyear = pats[0].dob.year if(pats[0].dob != None) else datetime.date.today().year
      curryear = datetime.date.today().year
      age = curryear - ageyear      
      
      if(len(medhist)>0):
          medhistobj["occupation"] = common.getstring(medhist[0].occupation)
          medhistobj["referer"] = common.getstring(medhist[0].referer)
          medhistobj["resoff"] = common.getstring(medhist[0].resoff)
          medhistobj["anyothercomplaint"] = common.getstring(medhist[0].anyothercomplaint)
          medhistobj["chiefcomplaint"] = common.getstring(medhist[0].chiefcomplaint)
          medhistobj["duration"] = common.getstring(medhist[0].duration)
          
          medhistobj["bp"] = common.getboolean(medhist[0].bp)
          medhistobj["diabetes"] = common.getboolean(medhist[0].diabetes)
          medhistobj["anaemia"] = common.getboolean(medhist[0].anaemia)
          medhistobj["epilepsy"] = common.getboolean(medhist[0].epilepsy)
          medhistobj["asthma"] = common.getboolean(medhist[0].asthma)
          medhistobj["sinus"] = common.getboolean(medhist[0].sinus)
          medhistobj["heart"] = common.getboolean(medhist[0].heart)
          medhistobj["jaundice"] = common.getboolean(medhist[0].jaundice)
          medhistobj["tb"] = common.getboolean(medhist[0].tb)
          medhistobj["cardiac"] = common.getboolean(medhist[0].cardiac)
          medhistobj["arthritis"] = common.getboolean(medhist[0].arthritis)
          medhistobj["anyother"] = common.getboolean(medhist[0].anyother)
          medhistobj["allergic"] = common.getboolean(medhist[0].allergic)
          medhistobj["excessivebleeding"] = common.getboolean(medhist[0].excessivebleeding)
          medhistobj["seriousillness"] = common.getboolean(medhist[0].seriousillness)
          medhistobj["hospitalized"] = common.getboolean(medhist[0].hospitalized)
          medhistobj["medications"] = common.getboolean(medhist[0].medications)
          medhistobj["surgery"] = common.getboolean(medhist[0].surgery)
          medhistobj["pregnant"] = common.getboolean(medhist[0].pregnant)
          medhistobj["breastfeeding"] = common.getboolean(medhist[0].breastfeeding)
          
          medhistobj["height"] = medhist[0].height
          medhistobj["weight"] = medhist[0].weight
          medhistobj["dob"] = pats[0].dob.strftime("%d/%m/%Y")  if(pats[0].dob != None) else ""
          medhistobj["age"] = age
          medhistobj["gender"] = pats[0].gender
          
          medhistobj["result"] = "success"
          medhistobj["error_message"] = ""
          
    except Exception as e:
      logger.loggerpms2.info("Get Medical History Exception:\n" + str(e))      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "Get Medical History Exception Error - " + str(e)
      return json.dumps(excpobj)   
    
    return json.dumps(medhistobj)
  
  def updateMedicalHistory(self,memberid,patientid,medhistory):
    db = self.db
    providerid = self.providerid      
    medhistobj = {}
    try:
      medhistobj = medhistory
      db.medicalnotes.update_or_insert(((db.medicalnotes.patientid == patientid) & (db.medicalnotes.memberid == memberid) & (db.medicalnotes.is_active == True)),
                                              patientid = patientid,
                                              memberid = memberid,
                                              bp = common.getboolean(medhistobj["bp"]),
                                              diabetes = common.getboolean(medhistobj["diabetes"]),
                                              anaemia = common.getboolean(medhistobj["anaemia"]),
                                              epilepsy = common.getboolean(medhistobj["epilepsy"]),
                                              asthma = common.getboolean(medhistobj["asthma"]),
                                              sinus = common.getboolean(medhistobj["sinus"]),
                                              heart = common.getboolean(medhistobj["heart"]),
                                              jaundice = common.getboolean(medhistobj["jaundice"]),
                                              tb = common.getboolean(medhistobj["tb"]),
                                              cardiac = common.getboolean(medhistobj["cardiac"]),
                                              arthritis = common.getboolean(medhistobj["arthritis"]),
                                              anyother = common.getboolean(medhistobj["anyother"]),
                                              pregnant = common.getboolean(medhistobj["pregnant"]),
                                              allergic = True if(common.getstring(medhistobj["allergic"])=="1") else False,
                                              excessivebleeding = True if(common.getstring(medhistobj["excessivebleeding"])=="1") else False,
                                              seriousillness = True if(common.getstring(medhistobj["seriousillness"])=="1") else False,
                                              hospitalized = True if(common.getstring(medhistobj["hospitalized"])=="1") else False,
                                              medications = True if(common.getstring(medhistobj["medications"])=="1") else False,
                                              surgery = True if(common.getstring(medhistobj["surgery"])=="1") else False,
                                              breastfeeding =True if(common.getstring(medhistobj["breastfeeding"])=="1") else False,
                                              anyothercomplaint = common.getstring(medhistobj["anyothercomplaint"]),
                                              chiefcomplaint = common.getstring(medhistobj["chiefcomplaint"]),
                                              duration = common.getstring(medhistobj["duration"]),
                                              occupation = common.getstring(medhistobj["occupation"]),
                                              referer = common.getstring(medhistobj["referer"]),
                                              resoff = common.getstring(medhistobj["resoff"]),
                                              height = common.getstring(medhistobj["height"]),
                                              weight = common.getstring(medhistobj["weight"]),
                                              is_active = True,
                                              created_on = common.getISTFormatCurrentLocatTime(),
                                              created_by = providerid,
                                              modified_on = common.getISTFormatCurrentLocatTime(),
                                              modified_by = providerid
                                              )         
      medhistobj["result"] = "success"
      medhistobj["error_message"] = ""
      
    except Exception as e:
      logger.loggerpms2.info("Update Medical History Exception:\n" + str(e))      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "Update Medical History Exception Error - " + str(e)
      return json.dumps(excpobj)      

    return  json.dumps(medhistobj)
  
  
  
  def getMediAssistPatients(self,page,maxcount):

    result = False
    patlist = []
    db = self.db
    providerid = self.providerid
    pats=None
    
    page = page -1
    urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
    items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
    limitby = ((page)*items_per_page,(page+1)*items_per_page)      
    
    c = db(db.company.company == 'MEDI').select(db.company.id)
    cid = 0 if(len(c) == 0) else int(common.getid(c[0].id))
   
    
    
    if(page >= 0):
      pats = db((db.vw_memberpatientlist.company == cid) & (db.vw_memberpatientlist.providerid == providerid) & \
                ((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                (db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.hmopatientmember,\
                                                                  db.vw_memberpatientlist.patientmember,\
                                                                  db.vw_memberpatientlist.fname,\
                                                                  db.vw_memberpatientlist.lname,\
                                                                  db.vw_memberpatientlist.primarypatientid,\
                                                                  db.vw_memberpatientlist.patientid,\
                                                                  db.vw_memberpatientlist.patienttype,\
                                                                  db.vw_memberpatientlist.relation,\
                                                                  db.vw_memberpatientlist.cell,\
                                                                  db.vw_memberpatientlist.email,\
                                                                  limitby=limitby)
      if(maxcount == 0):
        maxcount = db((db.vw_memberpatientlist.company == cid) & (db.vw_memberpatientlist.providerid == providerid) & \
                      ((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                      (db.vw_memberpatientlist.is_active == True)).count()
        
    else:
      pats = db((db.vw_memberpatientlist.company==cid) & (db.vw_memberpatientlist.providerid == providerid) & \
                ((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                (db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.hmopatientmember,\
                                                                  db.vw_memberpatientlist.patientmember,\
                                                                  db.vw_memberpatientlist.fname,\
                                                                  db.vw_memberpatientlist.lname,\
                                                                  db.vw_memberpatientlist.primarypatientid,\
                                                                  db.vw_memberpatientlist.patientid,\
                                                                  db.vw_memberpatientlist.patienttype,\
                                                                  db.vw_memberpatientlist.relation,\
                                                                  db.vw_memberpatientlist.cell,\
                                                                  db.vw_memberpatientlist.email\
                                                                  )
      if(maxcount == 0):
        maxcount = db((db.vw_memberpatientlist.company==cid) & (db.vw_memberpatientlist.providerid == providerid) & \
                      ((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                      (db.vw_memberpatientlist.is_active == True)).count()
    
      
    
    for pat in pats:
      
      patobj = {
        "member":common.getboolean(pat.hmopatientmember),  #False for walk in patient
        "patientmember" : pat.patientmember,
        "fname":pat.fname,
        "lname":pat.lname,
        "memberid":int(common.getid(pat.primarypatientid)),
        "patientid":int(common.getid(pat.patientid)),
        "primary":True if(pat.patienttype == "P") else False,   #True if "P" False if "D"
        "relation":pat.relation,
        "cell":pat.cell,
        "email":pat.email
        
      }
      patlist.append(patobj)   
    
    xcount = ((page+1) * items_per_page) - (items_per_page - len(pats)) 
    
    bnext = True
    bprev = True
    
    #first page
    if((page+1) == 1):
      bnext = True
      bprev = False
    
    #last page
    if(len(pats) < items_per_page):
      bnext = False
      bprev = True
    
    return json.dumps({"patientcount":len(pats),"page":page+1,"patientlist":patlist, "runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev} )
  
  #Searches for a patient in member, memberdependants, non-members for the patientsearch phrase
  #filters on cell, email, patientcode, patient fname/lname
  #
  #returns:
  #result as follows:
  #{
  # results: True or False
  # count
  # [
  #   {
  #      member, patientid, memberid, patientmember, fname, lname, cell,email, relation,patienttype,primary
  #   }
  # ]
  
  
  
  def searchpatient(self,page,patientsearch,maxcount,patientmembersearch,hmopatientmember, company=""):
    
    
    result = False
    patlist = []
    db = self.db
    providerid = self.providerid
    pats=None
    
    urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
    
    page = page -1
    urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
    items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
    limitby = None if page < 0 else ((page)*items_per_page,(page+1)*items_per_page)      
    
    
    
    c = db(db.company.company == company).select(db.company.id)
    companyid = 0 if(len(c) != 1) else int(common.getid(c[0].id))
    
    #if(page >= -1):
    if(hmopatientmember == True):
      qry = ((db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt))
    elif(hmopatientmember==False):
      qry = (db.vw_memberpatientlist.hmopatientmember == False)
    else:
      qry = (db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )
    
    if(companyid >0):
      qry = (qry) & (db.vw_memberpatientlist.company == companyid)
    
    #is it numeric only, then search on cell numbero
    if(patientsearch.replace("+",'').replace(' ','').isdigit()):
      pats=db((db.vw_memberpatientlist.cell.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.providerid == providerid) & \
              (qry) & \
              (db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.hmopatientmember,\
                                                                  db.vw_memberpatientlist.patientmember,\
                                                                  db.vw_memberpatientlist.fname,\
                                                                  db.vw_memberpatientlist.lname,\
                                                                  db.vw_memberpatientlist.primarypatientid,\
                                                                  db.vw_memberpatientlist.patientid,\
                                                                  db.vw_memberpatientlist.patienttype,\
                                                                  db.vw_memberpatientlist.relation,\
                                                                  db.vw_memberpatientlist.cell,\
                                                                  db.vw_memberpatientlist.email,\
                                                                  limitby=limitby)
      if(maxcount == 0):
        maxcount = db((db.vw_memberpatientlist.cell.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                      (qry) & \
                      (db.vw_memberpatientlist.is_active == True)).count()
      
    
    #is it email only
    elif(patientsearch.find("@") >= 0):
      pats=db((db.vw_memberpatientlist.email.like("%"+patientsearch+"%")) & (db.vw_memberpatientlist.providerid == providerid) & \
              (qry) & \
              (db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.hmopatientmember,\
                                                                  db.vw_memberpatientlist.patientmember,\
                                                                  db.vw_memberpatientlist.fname,\
                                                                  db.vw_memberpatientlist.lname,\
                                                                  db.vw_memberpatientlist.primarypatientid,\
                                                                  db.vw_memberpatientlist.patientid,\
                                                                  db.vw_memberpatientlist.patienttype,\
                                                                  db.vw_memberpatientlist.relation,\
                                                                  db.vw_memberpatientlist.cell,\
                                                                  db.vw_memberpatientlist.email,\
                                                                  limitby=limitby)
      
      if(maxcount == 0):
        maxcount = db((db.vw_memberpatientlist.email.like("%"+patientsearch+"%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                      (qry) & \
                      (db.vw_memberpatientlist.is_active == True)).count()
      
    #if pats is empty, then search for phrase in patient (fname lname:membercode)
    else:
      pats = db((db.vw_memberpatientlist.patient.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.patientmember.like("%" + patientmembersearch + "%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                (qry) & \
                (db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.hmopatientmember,\
                                                                  db.vw_memberpatientlist.patientmember,\
                                                                  db.vw_memberpatientlist.fname,\
                                                                  db.vw_memberpatientlist.lname,\
                                                                  db.vw_memberpatientlist.primarypatientid,\
                                                                  db.vw_memberpatientlist.patientid,\
                                                                  db.vw_memberpatientlist.patienttype,\
                                                                  db.vw_memberpatientlist.relation,\
                                                                  db.vw_memberpatientlist.cell,\
                                                                  db.vw_memberpatientlist.email,\
                                                                  limitby=limitby)
      if(maxcount == 0):
        maxcount = db((db.vw_memberpatientlist.patient.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.patientmember.like("%" + patientmembersearch + "%")) &(db.vw_memberpatientlist.providerid == providerid) & \
                      (qry) & \
                      (db.vw_memberpatientlist.is_active == True)).count()
        

  
    
    
    
    for pat in pats:
      
      patobj = {
        "member":common.getboolean(pat.hmopatientmember),  #False for walk in patient
        "patientmember" : pat.patientmember,
        "fname":pat.fname,
        "lname":pat.lname,
        "memberid":int(common.getid(pat.primarypatientid)),
        "patientid":int(common.getid(pat.patientid)),
        "primary":True if(pat.patienttype == "P") else False,   #True if "P" False if "D"
        "relation":pat.relation,
        "cell":pat.cell,
        "email":pat.email
        
      }
      patlist.append(patobj)   
    
    xcount = ((page+1) * items_per_page) - (items_per_page - len(pats)) 
    
    bnext = True
    bprev = True
    
    #first page
    if((page+1) == 1):
      bnext = True
      bprev = False
    
    #last page
    if(len(pats) < items_per_page):
      bnext = False
      bprev = True
    
    return json.dumps({"patientcount":len(pats),"page":page+1,"patientlist":patlist, "runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev,\
                       "patientsearch":patientsearch,"patientmembersearch":patientmembersearch,"member":hmopatientmember,"company":company} )
  
  
  def getcompanypatients(self,page,company,patientsearch,maxcount,patientmembersearch,hmopatientmember):
      
      
      result = False
      patlist = []
      db = self.db
      providerid = self.providerid
      pats=None
      
      urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
      
      page = page -1
      urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
      items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
      limitby = None if page < 0 else ((page)*items_per_page,(page+1)*items_per_page)      
      
      
      #get company
      
      
     
      
      
      #if(page >= -1):
      if(hmopatientmember == True):
        qry = ((db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt))
      elif(hmopatientmember==False):
        qry = (db.vw_memberpatientlist.hmopatientmember == False)
      else:
        qry = (db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )
      
      #is it numeric only, then search on cell numbero
      if(patientsearch.replace("+",'').replace(' ','').isdigit()):
        pats=db((db.vw_memberpatientlist.cell.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                (qry) & \
                (db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.hmopatientmember,\
                                                                    db.vw_memberpatientlist.patientmember,\
                                                                    db.vw_memberpatientlist.fname,\
                                                                    db.vw_memberpatientlist.lname,\
                                                                    db.vw_memberpatientlist.primarypatientid,\
                                                                    db.vw_memberpatientlist.patientid,\
                                                                    db.vw_memberpatientlist.patienttype,\
                                                                    db.vw_memberpatientlist.relation,\
                                                                    db.vw_memberpatientlist.cell,\
                                                                    db.vw_memberpatientlist.email,\
                                                                    limitby=limitby)
        if(maxcount == 0):
          maxcount = db((db.vw_memberpatientlist.cell.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                        (qry) & \
                        (db.vw_memberpatientlist.is_active == True)).count()
        
      
      #is it email only
      elif(patientsearch.find("@") >= 0):
        pats=db((db.vw_memberpatientlist.email.like("%"+patientsearch+"%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                (qry) & \
                (db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.hmopatientmember,\
                                                                    db.vw_memberpatientlist.patientmember,\
                                                                    db.vw_memberpatientlist.fname,\
                                                                    db.vw_memberpatientlist.lname,\
                                                                    db.vw_memberpatientlist.primarypatientid,\
                                                                    db.vw_memberpatientlist.patientid,\
                                                                    db.vw_memberpatientlist.patienttype,\
                                                                    db.vw_memberpatientlist.relation,\
                                                                    db.vw_memberpatientlist.cell,\
                                                                    db.vw_memberpatientlist.email,\
                                                                    limitby=limitby)
        
        if(maxcount == 0):
          maxcount = db((db.vw_memberpatientlist.email.like("%"+patientsearch+"%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                        (qry) & \
                        (db.vw_memberpatientlist.is_active == True)).count()
        
      #if pats is empty, then search for phrase in patient (fname lname:membercode)
      else:
        pats = db((db.vw_memberpatientlist.patient.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.patientmember.like("%" + patientmembersearch + "%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                  (qry) & \
                  (db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.hmopatientmember,\
                                                                    db.vw_memberpatientlist.patientmember,\
                                                                    db.vw_memberpatientlist.fname,\
                                                                    db.vw_memberpatientlist.lname,\
                                                                    db.vw_memberpatientlist.primarypatientid,\
                                                                    db.vw_memberpatientlist.patientid,\
                                                                    db.vw_memberpatientlist.patienttype,\
                                                                    db.vw_memberpatientlist.relation,\
                                                                    db.vw_memberpatientlist.cell,\
                                                                    db.vw_memberpatientlist.email,\
                                                                    limitby=limitby)
        if(maxcount == 0):
          maxcount = db((db.vw_memberpatientlist.patient.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.patientmember.like("%" + patientmembersearch + "%")) &(db.vw_memberpatientlist.providerid == providerid) & \
                        (qry) & \
                        (db.vw_memberpatientlist.is_active == True)).count()
          
  
    
      
      
      
      for pat in pats:
        
        patobj = {
          "member":common.getboolean(pat.hmopatientmember),  #False for walk in patient
          "patientmember" : pat.patientmember,
          "fname":pat.fname,
          "lname":pat.lname,
          "memberid":int(common.getid(pat.primarypatientid)),
          "patientid":int(common.getid(pat.patientid)),
          "primary":True if(pat.patienttype == "P") else False,   #True if "P" False if "D"
          "relation":pat.relation,
          "cell":pat.cell,
          "email":pat.email
          
        }
        patlist.append(patobj)   
      
      xcount = ((page+1) * items_per_page) - (items_per_page - len(pats)) 
      
      bnext = True
      bprev = True
      
      #first page
      if((page+1) == 1):
        bnext = True
        bprev = False
      
      #last page
      if(len(pats) < items_per_page):
        bnext = False
        bprev = True
      
      return json.dumps({"patientcount":len(pats),"page":page+1,"patientlist":patlist, "runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev,\
                         "patientsearch":patientsearch,"patientmembersearch":patientmembersearch,"member":hmopatientmember} )

  
  #this method retrieves member/patient information
  #{
  # "profile":{}
  # "contact":{}
  # "plan":{}
  # "dependants":{[]}
  #}
  def getpatient(self,memberid,patientid,imageurl):
    
    db = self.db
    providerid = self.providerid
    memobj = {}
    
    try:
      mem = db(db.patientmember.id == memberid).select(db.patientmember.ALL, db.groupregion.groupregion,db.groupregion.id,db.company.name,
                                                       db.hmoplan.name,db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode,
                                                       left=[db.groupregion.on(db.groupregion.id == db.patientmember.groupregion),
                                                             db.company.on(db.company.id == db.patientmember.company),
                                                             db.hmoplan.on(db.hmoplan.id == db.patientmember.hmoplan)])
      
      deps = db((db.patientmemberdependants.patientmember == memberid) & (db.patientmemberdependants.is_active == True)).select()
      deplist=[]
      depobj = {}
      
      for dep in deps:
        depobj = {
          "name":dep.fname + " " + dep.mname + " " + dep.lname,
          "dob": dep.depdob.strftime("%d/%m/%Y"),
          "relation":dep.relation,
          "groupref":common.getstring(dep.title),   # for Religare patient (policy 399)  for others it may be title
          "patientid":int(common.getid(dep.id))
        }
        deplist.append(depobj)
      
      memobj = {}
      memobj["memberid"] = int(common.getid(mem[0].patientmember.id))
      memobj["patientid"] = int(common.getid(mem[0].patientmember.id))
      
      memprofile = {}
      memprofile = {
          "patientid":int(common.getid(mem[0].patientmember.id)), 
          "memberid ":int(common.getid(mem[0].patientmember.id)), 
          "patientmember ":common.getstring(mem[0].patientmember.patientmember), 
          "groupref ":common.getstring(mem[0].patientmember.groupref), 
          "title ":common.getstring(mem[0].patientmember.title), 
          "fname ":common.getstring(mem[0].patientmember.fname), 
          "mname ":common.getstring(mem[0].patientmember.mname), 
          "lname ":common.getstring(mem[0].patientmember.lname), 
          "dob ":mem[0].patientmember.dob.strftime("%d/%m/%Y")  if(mem[0].patientmember.dob != None) else "",
          "gender ":common.getstring(mem[0].patientmember.gender), 
          "newmember ":common.getboolean(mem[0].patientmember.newmember), 
          "freetreatment ":common.getboolean(mem[0].patientmember.freetreatment),   
          "status":common.getstring(mem[0].patientmember.status),
          "hmopatientmember":common.getboolean(mem[0].patientmember.hmopatientmember),
          "image":common.getstring(mem[0].patientmember.image),
          "imageurl":imageurl + "/" + common.getstring(mem[0].patientmember.image),
          "dcsid":int(common.getid(mem[0].patientmember.dcsid))
          }
      memobj["profile"] = memprofile
      
      memcontact = {}
      memcontact = {
          "address1":common.getstring(mem[0].patientmember.address1),
          "address2":common.getstring(mem[0].patientmember.address2),
          "address3":common.getstring(mem[0].patientmember.address3),
          "city":common.getstring(mem[0].patientmember.city),
          "st":common.getstring(mem[0].patientmember.st),
          "pin":common.getstring(mem[0].patientmember.pin),
          "cell ":common.getstring(mem[0].patientmember.cell), 
          "email ":common.getstring(mem[0].patientmember.email),         
          "region":common.getstring(mem[0].groupregion.groupregion),
          "regionid":int(common.getid(mem[0].groupregion.id))
        }
      memobj["contact"] = memcontact
      
      if(common.getboolean(mem[0].patientmember.hmopatientmember) == True):
        memplan = {
            "company":common.getstring(mem[0].company.name),
            "plan":common.getstring(mem[0].hmoplan.name),
            "plancode":common.getstring(mem[0].hmoplan.hmoplancode),
            "planid": int(common.getid(mem[0].hmoplan.id)),
            'procedurepriceplancode':common.getstring(mem[0].hmoplan.procedurepriceplancode),
            "enrollment":mem[0].patientmember.enrollmentdate.strftime("%d/%m/%Y"),
            "premenddate":mem[0].patientmember.premenddt.strftime("%d/%m/%Y")
        }
      else:
        #walkin member
        memplan = {
            "company":"WALKIN",
            "plan":"Premium Walkin",
            "plancode":"PREMWALKIN",
            "planid": int(common.getid(mem[0].hmoplan.id)),
            'procedurepriceplancode':"PREMWALKIN",
            "enrollment":"",
            "premenddate":"",
        }
        
      
      memobj["plan"] = memplan
      
    
      memdep = {
        "count": len(deplist),
        "deplist":deplist
      }
      memobj["dependants"] = memdep
      memobj["result"] = "success"
      memobj["error_message"] = ""
      
      
    except Exception as e:
      logger.loggerpms2.info("Get Patient Exception:\n" + str(e))
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "Get Patient API Exception Error - " + str(e)
      return json.dumps(excpobj)  
                   
    
    return json.dumps(memobj)
  
  #def xsearchpatient(self,page,patientsearch,maxcount):
      
      
      #result = False
      #patlist = []
      #db = self.db
      #providerid = self.providerid
      #pats=None
      
      #page = page -1
      #items_per_page = 4
      #limitby = ((page)*items_per_page,(page+1)*items_per_page)      
      
      
     
      
      
      #if(page >= 0):
        ##is it numeric only, then search on cell numbero
        #if(patientsearch.replace("+",'').replace(' ','').isdigit()):
          #pats=db((db.vw_memberpatientlist.cell.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                  #((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                  #(db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.hmopatientmember,\
                                                                      #db.vw_memberpatientlist.patientmember,\
                                                                      #db.vw_memberpatientlist.fname,\
                                                                      #db.vw_memberpatientlist.lname,\
                                                                      #db.vw_memberpatientlist.primarypatientid,\
                                                                      #db.vw_memberpatientlist.patientid,\
                                                                      #db.vw_memberpatientlist.patienttype,\
                                                                      #db.vw_memberpatientlist.relation,\
                                                                      #db.vw_memberpatientlist.cell,\
                                                                      #db.vw_memberpatientlist.email,\
                                                                      #limitby=limitby)
          #if(maxcount == 0):
            #maxcount = db((db.vw_memberpatientlist.cell.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                          #((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                          #(db.vw_memberpatientlist.is_active == True)).count()
          
        
        ##is it email only
        #elif(patientsearch.find("@") >= 0):
          #pats=db((db.vw_memberpatientlist.email.like("%"+patientsearch+"%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                  #((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                  #(db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.hmopatientmember,\
                                                                      #db.vw_memberpatientlist.patientmember,\
                                                                      #db.vw_memberpatientlist.fname,\
                                                                      #db.vw_memberpatientlist.lname,\
                                                                      #db.vw_memberpatientlist.primarypatientid,\
                                                                      #db.vw_memberpatientlist.patientid,\
                                                                      #db.vw_memberpatientlist.patienttype,\
                                                                      #db.vw_memberpatientlist.relation,\
                                                                      #db.vw_memberpatientlist.cell,\
                                                                      #db.vw_memberpatientlist.email,\
                                                                      #limitby=limitby)
          
          #if(maxcount == 0):
            #maxcount = db((db.vw_memberpatientlist.email.like("%"+patientsearch+"%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                          #((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                          #(db.vw_memberpatientlist.is_active == True)).count()
          
        ##if pats is empty, then search for phrase in patient (fname lname:membercode)
        #if(pats == None):
          #pats = db((db.vw_memberpatientlist.patient.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                    #((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                    #(db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.hmopatientmember,\
                                                                      #db.vw_memberpatientlist.patientmember,\
                                                                      #db.vw_memberpatientlist.fname,\
                                                                      #db.vw_memberpatientlist.lname,\
                                                                      #db.vw_memberpatientlist.primarypatientid,\
                                                                      #db.vw_memberpatientlist.patientid,\
                                                                      #db.vw_memberpatientlist.patienttype,\
                                                                      #db.vw_memberpatientlist.relation,\
                                                                      #db.vw_memberpatientlist.cell,\
                                                                      #db.vw_memberpatientlist.email,\
                                                                      #limitby=limitby)
          #if(maxcount == 0):
            #maxcount = db((db.vw_memberpatientlist.patient.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                          #((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                          #(db.vw_memberpatientlist.is_active == True)).count()
            
      #else:
        ##is it numeric only, then search on cell numbero
        #if(patientsearch.replace("+",'').replace(' ','').isdigit()):
          #pats=db((db.vw_memberpatientlist.cell.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                  #((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                  #(db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.hmopatientmember,\
                                                                      #db.vw_memberpatientlist.patientmember,\
                                                                      #db.vw_memberpatientlist.fname,\
                                                                      #db.vw_memberpatientlist.lname,\
                                                                      #db.vw_memberpatientlist.primarypatientid,\
                                                                      #db.vw_memberpatientlist.patientid,\
                                                                      #db.vw_memberpatientlist.patienttype,\
                                                                      #db.vw_memberpatientlist.relation,\
                                                                      #db.vw_memberpatientlist.cell,\
                                                                      #db.vw_memberpatientlist.email\
                                                                      #)
          #if(maxcount == 0):
            #maxcount = db((db.vw_memberpatientlist.cell.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                          #((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                          #(db.vw_memberpatientlist.is_active == True)).count()
        
        ##is it email only
        #elif(patientsearch.find("@") >= 0):
          #pats=db((db.vw_memberpatientlist.email.like("%"+patientsearch+"%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                  #((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                  #(db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.hmopatientmember,\
                                                                      #db.vw_memberpatientlist.patientmember,\
                                                                      #db.vw_memberpatientlist.fname,\
                                                                      #db.vw_memberpatientlist.lname,\
                                                                      #db.vw_memberpatientlist.primarypatientid,\
                                                                      #db.vw_memberpatientlist.patientid,\
                                                                      #db.vw_memberpatientlist.patienttype,\
                                                                      #db.vw_memberpatientlist.relation,\
                                                                      #db.vw_memberpatientlist.cell,\
                                                                      #db.vw_memberpatientlist.email\
                                                                     #)
          #if(maxcount == 0):
            #maxcount = db((db.vw_memberpatientlist.email.like("%"+patientsearch+"%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                          #((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                          #(db.vw_memberpatientlist.is_active == True)).count()
          
          
        ##if pats is empty, then search for phrase in patient (fname lname:membercode)
        #if(pats == None):
          #pats = db((db.vw_memberpatientlist.patient.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                    #((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                    #(db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.hmopatientmember,\
                                                                      #db.vw_memberpatientlist.patientmember,\
                                                                      #db.vw_memberpatientlist.fname,\
                                                                      #db.vw_memberpatientlist.lname,\
                                                                      #db.vw_memberpatientlist.primarypatientid,\
                                                                      #db.vw_memberpatientlist.patientid,\
                                                                      #db.vw_memberpatientlist.patienttype,\
                                                                      #db.vw_memberpatientlist.relation,\
                                                                      #db.vw_memberpatientlist.cell,\
                                                                      #db.vw_memberpatientlist.email\
                                                                      #)
          #if(maxcount == 0):
            #maxcount = db((db.vw_memberpatientlist.patient.like("%" + patientsearch + "%")) & (db.vw_memberpatientlist.providerid == providerid) & \
                          #((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )) & \
                          #(db.vw_memberpatientlist.is_active == True)).count()
        
          
      
      #for pat in pats:
        
        #patobj = {
          #"member":common.getboolean(pat.hmopatientmember),  #False for walk in patient
          #"patientmember" : pat.patientmember,
          #"fname":pat.fname,
          #"lname":pat.lname,
          #"memberid":int(common.getid(pat.primarypatientid)),
          #"patientid":int(common.getid(pat.patientid)),
          #"primary":True if(pat.patienttype == "P") else False,   #True if "P" False if "D"
          #"relation":pat.relation,
          #"cell":pat.cell,
          #"email":pat.email
          
        #}
        #patlist.append(patobj)   
      
      #xcount = ((page+1) * items_per_page) - (items_per_page - len(pats)) 
      
      #bnext = True
      #bprev = True
      
      ##first page
      #if((page+1) == 1):
        #bnext = True
        #bprev = False
      
      ##last page
      #if(len(pats) < items_per_page):
        #bnext = False
        #bprev = True
      
      #return json.dumps({"patientcount":len(pats),"page":page+1,"patientlist":patlist, "runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev} )
    
    
    #this method retrieves member/patient information
    #{
    # "profile":{}
    # "contact":{}
    # "plan":{}
    # "dependants":{[]}
    #}
    def getpatient(self,memberid,patientid,imageurl):
      
      db = self.db
      providerid = self.providerid
      memobj = {}
      
      try:
        mem = db(db.patientmember.id == memberid).select(db.patientmember.ALL, db.groupregion.groupregion,db.groupregion.id,db.company.name,
                                                         db.hmoplan.name,db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode,
                                                         left=[db.groupregion.on(db.groupregion.id == db.patientmember.groupregion),
                                                               db.company.on(db.company.id == db.patientmember.company),
                                                               db.hmoplan.on(db.hmoplan.id == db.patientmember.hmoplan)])
        
        deps = db((db.patientmemberdependants.patientmember == memberid) & (db.patientmemberdependants.is_active == True)).select()
        deplist=[]
        depobj = {}
        
        for dep in deps:
          depobj = {
            "name":dep.fname + " " + dep.mname + " " + dep.lname,
            "dob": dep.depdob.strftime("%d/%m/%Y"),
            "relation":dep.relation
          }
          deplist.append(depobj)
        
        memobj = {}
        memobj["memberid"] = int(common.getid(mem[0].patientmember.id))
        memobj["patientid"] = int(common.getid(mem[0].patientmember.id))
        
        memprofile = {}
        memprofile = {
            "patientid":int(common.getid(mem[0].patientmember.id)), 
            "memberid ":int(common.getid(mem[0].patientmember.id)), 
            "patientmember ":common.getstring(mem[0].patientmember.patientmember), 
            "groupref ":common.getstring(mem[0].patientmember.groupref), 
            "title ":common.getstring(mem[0].patientmember.title), 
            "fname ":common.getstring(mem[0].patientmember.fname), 
            "mname ":common.getstring(mem[0].patientmember.mname), 
            "lname ":common.getstring(mem[0].patientmember.lname), 
            "dob ":mem[0].patientmember.dob.strftime("%d/%m/%Y")  if(mem[0].patientmember.dob != None) else "",
            "gender ":common.getstring(mem[0].patientmember.gender), 
            "newmember ":common.getboolean(mem[0].patientmember.newmember), 
            "freetreatment ":common.getboolean(mem[0].patientmember.freetreatment),   
            "status":common.getstring(mem[0].patientmember.status),
            "hmopatientmember":common.getboolean(mem[0].patientmember.hmopatientmember),
            "image":common.getstring(mem[0].patientmember.image),
            "imageurl":imageurl + "/" + common.getstring(mem[0].patientmember.image),
            "dcsid":int(common.getid(mem[0].patientmember.dcsid))
            }
        memobj["profile"] = memprofile
        
        memcontact = {}
        memcontact = {
            "address1":common.getstring(mem[0].patientmember.address1),
            "address2":common.getstring(mem[0].patientmember.address2),
            "address3":common.getstring(mem[0].patientmember.address3),
            "city":common.getstring(mem[0].patientmember.city),
            "st":common.getstring(mem[0].patientmember.st),
            "pin":common.getstring(mem[0].patientmember.pin),
            "cell ":common.getstring(mem[0].patientmember.cell), 
            "email ":common.getstring(mem[0].patientmember.email),         
            "region":common.getstring(mem[0].groupregion.groupregion),
            "regionid":int(common.getid(mem[0].groupregion.id))
          }
        memobj["contact"] = memcontact
        
        if(common.getboolean(mem[0].patientmember.hmopatientmember) == True):
          memplan = {
              "company":common.getstring(mem[0].company.name),
              "plan":common.getstring(mem[0].hmoplan.name),
              "plancode":common.getstring(mem[0].hmoplan.hmoplancode),
              "planid": int(common.getid(mem[0].hmoplan.id)),
              'procedurepriceplancode':common.getstring(mem[0].hmoplan.procedurepriceplancode),
              "enrollment":mem[0].patientmember.enrollmentdate.strftime("%d/%m/%Y"),
              "premenddate":mem[0].patientmember.premenddt.strftime("%d/%m/%Y")
          }
        else:
          memplan = {}
        
        memobj["plan"] = memplan
        
      
        memdep = {
          "count": len(deplist),
          "deplist":deplist
        }
        memobj["dependants"] = memdep
        memobj["result"] = "success"
        memobj["error_message"] = ""
        
        
      except Exception as e:
        logger.loggerpms2.info("Get Patient Exception:\n" + str(e))
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = "Get Patient API Exception Error - " + str(e)
        return json.dumps(excpobj)  
                     
      
      return json.dumps(memobj)
  


  def xnewreligarepatient(self,customerid, customername,cell,dob):
    db = self.db
    providerid = self.providerid
    
    provider = ""
    r = db(db.provider.id == providerid).select(db.provider.provider)
    if(len(r)>0):
      provider = r[0].provider
    
    hmoplanid = 1
    companyid = 4 #default to MyDP
    
    r = db((db.company.company == 'RELGR') & (db.company.is_active == True)).select()
    if(len(r) > 0):
        companyid = common.getid(r[0].id)    
    
    r = db((db.hmoplan.hmoplancode.lower() == 'relgr101') & (db.hmoplan.is_active == True)).select()
    if(len(r) > 0):
        hmoplanid = common.getid(r[0].id)    
    
    regionid = 1    
    r = db((db.groupregion.groupregion.lower() == 'all') & (db.groupregion.is_active == True)).select()
    if(len(r) > 0):
        regionid = common.getid(r[0].id)   
        
    provcount = db(db.patientmember.provider == providerid).count()
    patientmember = "RELGR" + str(provcount).zfill(4)    



    
    todaydt = datetime.date.today()
    patid = db.patientmember.update_or_insert(db.patientmember.groupref==customerid,
      patientmember = patientmember,
      groupref = customerid,
      fname = customername,
      lname = customername,
      cell = cell,
      dob = dob,
      gender = 'Male',
      status = 'Enrolled',
      groupregion = regionid,
      provider = providerid,
      company = companyid,
      hmoplan = hmoplanid,
      enrollmentdate = todaydt,
      premstartdt = todaydt,
      premenddt = todaydt,
      startdate = todaydt,
      hmopatientmember = False,
      paid = False,
      newmember = False,
      freetreatment  = True,
      created_on = common.getISTFormatCurrentLocatTime(),
      created_by = 1,
      modified_on = common.getISTFormatCurrentLocatTime(),
      modified_by = 1     
    
    )
    
    if(patid == None):
      r = db(db.patientmember.groupref == customerid).select(db.patientmember.id)
      if(len(r)==1):
        patid = int(common.getid(r[0].id))
      else:
        patid = 0
 
    
    pat = db((db.vw_memberpatientlist.primarypatientid == patid) & \
                   (db.vw_memberpatientlist.patientid == patid) & \
                   (db.vw_memberpatientlist.providerid == providerid)).select(db.vw_memberpatientlist.ALL)
        
        
       
       
    patobj = {}
    if(len(pat) == 1):
      patobj = {
        
        "patientid":int(common.getid(pat[0].patientid)), 
        "primarypatientid":int(common.getid(pat[0].primarypatientid)), 
        "patientmember":common.getstring(pat[0].patientmember), 
        "groupref":common.getstring(pat[0].groupref), 
        "patienttype":common.getstring(pat[0].patienttype), 
        "title":common.getstring(pat[0].title), 
        "fname":common.getstring(pat[0].fname), 
       
        "fullname":common.getstring(pat[0].fullname), 
        "patient":common.getstring(pat[0].patient), 
        "cell":common.getstring(pat[0].cell), 
     
        "dob":pat[0].dob.strftime("%d/%m/%Y"),
        "gender":common.getstring(pat[0].gender), 
        "relation":common.getstring(pat[0].relation), 
        
        "regionid":int(common.getid(pat[0].regionid)), 
        "providerid" :int(common.getid(pat[0].providerid)), 
  
        "hmopatientmember":common.getstring(pat[0].hmopatientmember), 
        "hmoplan":int(common.getid(pat[0].hmoplan)), 
        "company":int(common.getid(pat[0].company)), 
        "newmember":common.getboolean(pat[0].newmember), 
        "freetreatment":common.getboolean(pat[0].freetreatment), 
        "age" :int(common.getid(pat[0].age)) ,
        "premstartdt":pat[0].premstartdt.strftime("%d/%m/%Y %H:%M"), 
        "premenddt":pat[0].premenddt.strftime("%d/%m/%Y %H:%M"), 
        "hmoplanname":pat[0].hmoplanname,
        "hmoplancode":pat[0].hmoplancode
      
      }    
    
    return json.dumps(patobj)

  def deletewalkinpatient(self,memberid):
    
    db = self.db
    auth = current.auth
    retobj = {}
    
    try:
      db((db.patientmember.id == memberid) & (db.patientmember.hmopatientmember == False)).update(\
    
        is_active = False,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1 if(auth.user == None) else auth.user.id     
        
      )
      
      retobj = {"result":"success","error_message":""}
    except Exception as e:
      logger.loggerpms2.info("Delete Walk-in Patient Exception:\n" + str(e))
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "Delete Walk-in Patient API Exception Error - " + str(e)
      return json.dumps(excpobj)  
         
    return json.dumps(retobj)
    
    
  #memberid, patientid, title, fname, mname, lname, gender, dob(dd/mm/yyyy), addr1, addr2, addr3, city, st, pin, cell, email  
  def updatewalkinpatient(self,patobj):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    retobj = {}
    try:
      memberid = int(common.getid(patobj["memberid"]))
      
      db(db.patientmember.id == memberid).update(\
    
        title = patobj['title'],
        fname = patobj["fname"],
        mname = patobj["mname"],
        lname = patobj["lname"],
        dob = datetime.datetime.strptime(patobj['dob'], "%d/%m/%Y"),
        cell = patobj["cell"],
        email = patobj["email"],
        gender = patobj["gender"],
        address1 = patobj["address1"],
        address2 = patobj["address2"],
        address3 = patobj["address3"],
        city = patobj["city"],
        st = patobj["st"],
        pin = patobj["pin"],
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1 if(auth.user == None) else auth.user.id     
        
      )
      
      retobj = {"result":"success","error_message":""}
    except Exception as e:
      logger.loggerpms2.info("Update Walk-in Patient API  Exception:\n" + str(e))
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "Update Walk-in Patient API Exception Error - " + str(e)
      return json.dumps(excpobj)  
         
    return json.dumps(retobj)
  
  
  def newalkinpatient(self,patobj):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    newpatobj = {}
    
    try:
      #generating patient member
      r = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.provider)
      provider = r[0].provider if(len(r) == 1)  else "MYDP"
      provcount = db(db.patientmember.provider == providerid).count()
      patientmember = provider + str(provcount).zfill(4)    
     
      #WALKIN company
      r = db((db.company.company.lower() == 'walkin') & (db.company.is_active == False)).select()  #this is a dummy company created for WALKIN
      companyid = int(common.getid(r[0].id))  if(len(r) == 1) else 0
      
      #WALKIN PLAN
      r = db((db.hmoplan.hmoplancode.lower() == 'premwalkin') & (db.hmoplan.is_active == False)).select()
      hmoplanid = int(common.getid(r[0].id))  if(len(r) == 1) else 1
      
      #ALL Region
      r = db((db.groupregion.groupregion.lower() == 'all') & (db.groupregion.is_active == True)).select()
      regionid = int(common.getid(r[0].id))  if(len(r) == 1) else 1
  
      #Create new WALK in patient
      todaydt = datetime.date.today()
      patid = db.patientmember.insert(\
           patientmember = patientmember,
           groupref = 'walkin',
           title = patobj['title'],
           fname = patobj["fname"],
           mname = patobj["mname"],
           lname = patobj["lname"],
           dob = datetime.datetime.strptime(patobj["dob"], "%d/%m/%Y"),
           cell = patobj["cell"],
           email = patobj["email"],
           gender = patobj["gender"],
           address1 = patobj["address1"],
           address2 = patobj["address2"],
           address3 = patobj["address3"],
           city = patobj["city"],
           st = patobj["st"],
           pin = patobj["pin"],
           status = 'Enrolled',
           groupregion = regionid,
           provider = providerid,
           company = companyid,
           hmoplan = hmoplanid,
           enrollmentdate = todaydt,
           premstartdt = todaydt,
           premenddt = todaydt,
           startdate = todaydt,
           hmopatientmember = False,
           paid = False,
           newmember = False,
           freetreatment  = True,
           created_on = common.getISTFormatCurrentLocatTime(),
           created_by = 1 if(auth.user == None) else auth.user.id,
           modified_on = common.getISTFormatCurrentLocatTime(),
           modified_by = 1 if(auth.user == None) else auth.user.id     
         
         )
      
      newpatobj={
           "result":"success",
           "error_message":"",
           "patientmember":patientmember,
           "memberid":patid,
           "patientid":patid
         }    
      
    except Exception as e:
      logger.loggerpms2.info("New Walkin Patient Exception:\n" + str(e))
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "New Walk-in Patient API Exception Error - " + str(e)
      return json.dumps(excpobj)       
      
    
    return json.dumps(newpatobj)
  
  
  def newpatient(self,fname, mname,lname,cell,email,groupref=""):
    
    db = self.db
    providerid = self.providerid
    provider = ""
    hmoplanid = 1
    companyid = 4 #default to MyDP
    patobj = {}
    
    try:
      r = db(db.provider.id == providerid).select(db.provider.provider)
      if(len(r)>0):
        provider = r[0].provider
      
      r = db((db.company.company == ' ') & (db.company.is_active == False)).select()
      if(len(r) > 0):
          companyid = common.getid(r[0].id)    
      
      r = db((db.hmoplan.hmoplancode.lower() == 'premwalkin') & (db.hmoplan.is_active == False)).select()
      if(len(r) > 0):
          hmoplanid = common.getid(r[0].id)    
      
      regionid = 1    
      r = db((db.groupregion.groupregion.lower() == 'all') & (db.groupregion.is_active == True)).select()
      if(len(r) > 0):
          regionid = common.getid(r[0].id)   
          
      provcount = db(db.patientmember.provider == providerid).count()
      patientmember = provider + str(provcount).zfill(4)    
  
  
  
      todaydt = datetime.date.today()
      patid = db.patientmember.insert(\
        patientmember = patientmember,
        groupref = groupref,
        fname = fname,
        mname = mname,
        lname = lname,
        cell = cell,
        email = email,
        status = 'Enrolled',
        groupregion = regionid,
        provider = providerid,
        company = companyid,
        hmoplan = hmoplanid,
        enrollmentdate = todaydt,
        premstartdt = todaydt,
        premenddt = todaydt,
        startdate = todaydt,
        hmopatientmember = False,
        paid = False,
        newmember = False,
        freetreatment  = True,
        created_on = common.getISTFormatCurrentLocatTime(),
        created_by = 1,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1     
      
      )
      
     
      #patobj={
       
        
        #"memberid":patid,
        #"patientid":patid,
       
      #}
      
      pat = db((db.vw_memberpatientlist.primarypatientid == patid) & \
                     (db.vw_memberpatientlist.patientid == patid) & \
                     (db.vw_memberpatientlist.providerid == providerid)).select(db.vw_memberpatientlist.ALL)
          
          
         
         
      
      patobj = {
        
        "patientid":int(common.getid(pat[0].patientid)), 
        "primarypatientid ":int(common.getid(pat[0].primarypatientid)), 
        "patientmember ":common.getstring(pat[0].patientmember), 
        "groupref ":common.getstring(pat[0].groupref), 
        "patienttype ":common.getstring(pat[0].patienttype), 
        "title ":common.getstring(pat[0].title), 
        "fname ":common.getstring(pat[0].fname), 
        "lname ":common.getstring(pat[0].lname), 
        "fullname ":common.getstring(pat[0].fullname), 
        "patient ":common.getstring(pat[0].patient), 
        "cell ":common.getstring(pat[0].cell), 
        "email ":common.getstring(pat[0].email), 
        "dob ":pat[0].dob.strftime("%d/%m/%Y"),
        "gender ":common.getstring(pat[0].gender), 
        "relation ":common.getstring(pat[0].relation), 
        
        "regionid ":int(common.getid(pat[0].regionid)), 
        "providerid" :int(common.getid(pat[0].providerid)), 
  
        "hmopatientmember ":common.getstring(pat[0].hmopatientmember), 
        "hmoplan ":int(common.getid(pat[0].hmoplan)), 
        "company ":int(common.getid(pat[0].company)), 
        "newmember ":common.getboolean(pat[0].newmember), 
        "freetreatment ":common.getboolean(pat[0].freetreatment), 
        "age" :int(common.getid(pat[0].age)) ,
        "premstartdt ":pat[0].premstartdt.strftime("%d/%m/%Y %H:%M"), 
        "premenddt ":pat[0].premenddt.strftime("%d/%m/%Y %H:%M"), 
        "hmoplanname":pat[0].hmoplanname,
        "hmoplancode ":pat[0].hmoplancode,
      
        "result":"success",
        "error_message":""
      }    
      
    except Exception as e:
      logger.loggerpms2.info("New Patient API  Exception:\n" + str(e))      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "New Patient API Exception Error - " + str(e)
      return json.dumps(excpobj)       
      
    return json.dumps(patobj)
  
  
  def getpatientnotes(self,page,memberid,patientid):
    
    db = self.db
    providerid = self.providerid
    
    page = page -1
    
    urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
    items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
    limitby = ((page)*items_per_page,(page+1)*items_per_page)     
    
    
    notelistobj = {}    
    notelist = []
    
    try:
      if(page >=0 ):
        notes = db((db.vw_casereport.patientid == patientid) &\
                  (db.vw_casereport.memberid == memberid) &\
                  (db.vw_casereport.is_active == True)).select(db.vw_casereport.providername, db.vw_casereport.doctorname, db.vw_casereport.casereport, limitby=limitby,\
                                                               orderby=~db.vw_casereport.id)  
      else:
        notes = db((db.vw_casereport.patientid == patientid) &\
                  (db.vw_casereport.memberid == memberid) &\
                  (db.vw_casereport.is_active == True)).select(db.vw_casereport.providername, db.vw_casereport.doctorname, db.vw_casereport.casereport,\
                                                               orderby=~db.vw_casereport.id)  
        
      
      
      
      for note in notes:
        
        noteobj = {
          "providername": note.providername,
          "docname": note.doctorname  if(note.doctorname != None) else "",
          "casereport": note.casereport,
        }
       
        notelist.append(noteobj)
        notelistobj = {"result":"success","error_message":"","notecount":len(notes),"page":page+1,"notelist":notelist}
    except Exception as e:
      logger.loggerpms2.info("Get Patient Notes Exception:\n" + str(e))
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "Get Patient Notes API Exception Error - " + str(e)
      return json.dumps(excpobj)       
      
    
    
    return   json.dumps(notelistobj)
  
  #Save new notes
  def addpatientnotes(self,memberid,patientid,notes):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    noteobj = {}
    
    try:
      notedate = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
      newnote = notedate + "\n" + common.getstring(notes)    
  
      
      noteid = db.casereport.insert(memberid=memberid,patientid=patientid,providerid=providerid,casereport=newnote,doctorid=0,\
                           is_active = True,
                           created_on = common.getISTFormatCurrentLocatTime(),
                           created_by = 1 if(auth.user == None) else auth.user.id,
                           modified_on = common.getISTFormatCurrentLocatTime(),
                           modified_by =1 if(auth.user == None) else auth.usr.id
                           )
      noteobj = {
         "result":"success",
         "error_message":"",
         "noteid":noteid
      }
    except Exception as e:
      logger.loggerpms2.info("Add Patient Notes Exception:\n" + str(e))
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "Add Patient Notes API Exception Error - " + str(e)
      return json.dumps(excpobj)       
    
    return json.dumps(noteobj)
  
  
  def newpatientfromcustomer(self,avars):
    
    db = self.db
    providerid = self.providerid
    
    patobj = {}
    
    try:
      providerid = common.getkeyvalue(avars,"providerid",0)
      companyid = common.getkeyvalue(avars,"companyid",0)
      planid = common.getkeyvalue(avars,"planid",0)
      regionid = common.getkeyvalue(avars,"regionid",0)
      
      
      sql = "UPDATE membercount SET membercount = membercount + 1 WHERE company = " + str(companyid) + ";"
      db.executesql(sql)
      db.commit()      
        
      r = db(db.groupregion.id == regionid).select(db.groupregion.groupregion)
      region = r[0].groupregion if(len(r)==1) else "ALL"
      
      c = db(db.company.id == companyid).select(db.company.company)
      companycode = c[0].company if(len(c)==1) else "MYDP"
      
      
      
      xrows = db(db.membercount.company == companyid).select()
      membercount = int(xrows[0].membercount)
     
      
      patientmember = region + companycode[:3] + str(companyid).zfill(3) + str(membercount)                                     
      
      todaydt = datetime.date.today()
      enrolldate = common.getkeyvalue(avars,"enrolldate","")
      
      
      premstartdt = todaydt if(enrolldate == "") else (datetime.datetime.strptime(enrolldate,"%d/%m/%Y")).date()
      
      day  = timedelta(days = 1)
      
      if(calendar.isleap(premstartdt.year + 1)):
        if(premstartdt > datetime.date(premstartdt.year,02,28)):
          year            = timedelta(days=366)
        else:
          year = timedelta(days=365)
      elif(calendar.isleap(premstartdt.year)):
        if(premstartdt <= datetime.date(premstartdt.year,02,29)):
          year            = timedelta(days=366)
        else:
          year            = timedelta(days=365)
      else:
        year            = timedelta(days=365)
    
      premenddt = (premstartdt + year) - day  
      
      patid = db.patientmember.insert(\
        patientmember = patientmember,
        groupref = common.getkeyvalue(avars,"customer_ref",""),
        fname = common.getkeyvalue(avars,"fname",""),
        mname = common.getkeyvalue(avars,"mname",""),
        lname = common.getkeyvalue(avars,"lname",""),
        cell = common.getkeyvalue(avars,"cell","0000000000"),
        email = common.getkeyvalue(avars,"email","x@x.com"),
        telephone = common.getkeyvalue(avars,"telephone","0000000000"),
        gender = common.getkeyvalue(avars,"gender",""),
        dob = datetime.datetime.strptime(common.getkeyvalue(avars,"dob","01/01/1990"), "%d/%m/%Y"),
        address1 = common.getkeyvalue(avars,"address1","addr1"),
        address2 = common.getkeyvalue(avars,"address2","addr2"),
        address3 = common.getkeyvalue(avars,"address3","addr3"),
        city = common.getkeyvalue(avars,"city","city"),
        st = common.getkeyvalue(avars,"st","st"),
        pin = common.getkeyvalue(avars,"pin","000000"),
        
        status = 'Enrolled',
        groupregion = regionid,
        provider = providerid,
        company = companyid,
        hmoplan = planid,
        enrollmentdate = premstartdt,
        premstartdt = premstartdt,
        premenddt = premenddt,
        startdate = premstartdt,
        hmopatientmember = True,
        paid = False,
        newmember = True,
        freetreatment  = True,
        
        created_on = common.getISTFormatCurrentLocatTime(),
        created_by = 1,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1     
      
      )
     
      deps = common.getkeyvalue(avars,"dependants",None)
      if(deps != None):
        for dep in deps:
          db.patientmemberdependants.insert(
            
            title = "",
            fname = dep["fname"],
            mname = dep["mname"],
            lname = dep["lname"],
            depdob = common.getdatefromstring(dep["depdob"],"%d/%m/%Y"),
            gender = dep["gender"],
            relation = dep["relation"],
            patientmember = patid,
            newmember = True,
            
            created_on = common.getISTFormatCurrentLocatTime(),
            created_by = 1,
            modified_on = common.getISTFormatCurrentLocatTime(),
            modified_by = 1                 
          
          )
     
      
      pat = db((db.vw_memberpatientlist.primarypatientid == patid) & \
                     (db.vw_memberpatientlist.patientid == patid) & \
                     (db.vw_memberpatientlist.providerid == providerid)).select(db.vw_memberpatientlist.ALL)
          
          
         
         
      
      patobj = {
        
        "patientid":int(common.getid(pat[0].patientid)), 
        "primarypatientid":int(common.getid(pat[0].primarypatientid)), 
        "patientmember":common.getstring(pat[0].patientmember), 
        "groupref":common.getstring(pat[0].groupref), 
        "patienttype":common.getstring(pat[0].patienttype), 
        "title":common.getstring(pat[0].title), 
        "fname":common.getstring(pat[0].fname), 
        "lname":common.getstring(pat[0].lname), 
        "fullname":common.getstring(pat[0].fullname), 
        "patient":common.getstring(pat[0].patient), 
        "cell":common.getstring(pat[0].cell), 
        "email":common.getstring(pat[0].email), 
        "dob":pat[0].dob.strftime("%d/%m/%Y"),
        "gender":common.getstring(pat[0].gender), 
        "relation":common.getstring(pat[0].relation), 
        
        "regionid":int(common.getid(pat[0].regionid)), 
        "providerid" :int(common.getid(pat[0].providerid)), 
  
        "hmopatientmember":common.getstring(pat[0].hmopatientmember), 
        "hmoplan":int(common.getid(pat[0].hmoplan)), 
        "company":int(common.getid(pat[0].company)), 
        "newmember":common.getboolean(pat[0].newmember), 
        "freetreatment":common.getboolean(pat[0].freetreatment), 
        "age" :int(common.getid(pat[0].age)) ,
        "premstartdt":pat[0].premstartdt.strftime("%d/%m/%Y %H:%M"), 
        "premenddt":pat[0].premenddt.strftime("%d/%m/%Y %H:%M"), 
        "hmoplanname":pat[0].hmoplanname,
        "hmoplancode":pat[0].hmoplancode,
      
        "result":"success",
        "error_message":""
      }    
           
      
      deplist = []
      depobj = {}
      deps = db((db.patientmemberdependants.patientmember == patid) & (db.patientmemberdependants.is_active == True)).select()
      for dep in deps:
        depobj = {
         "fname":dep["fname"],
         "mname":dep["mname"],
         "lname":dep["lname"],
         "depdob":common.getstringfromdate(dep["depdob"],"%d/%m/%Y"),
         "gender":dep["gender"],
         "relation":dep["relation"],
         "patientmember":dep["patientmember"] 
        }
        deplist.append(depobj)
      
      patobj["dependants"] = deplist
        
        
    except Exception as e:
      logger.loggerpms2.info("New Patient API  Exception:\n" + str(e))      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "New Patient API Exception Error - " + str(e)
      return json.dumps(excpobj)       
      
    return json.dumps(patobj)
   
  