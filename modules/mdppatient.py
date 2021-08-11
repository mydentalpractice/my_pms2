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
from applications.my_pms2.modules import mdpmedia
from applications.my_pms2.modules import mdpbenefits
from applications.my_pms2.modules import logger

class Patient:
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    return 

  #returns the policy which the patient has subscribed to  
  def getMemberPolicy(self,avars):
    logger.loggerpms2.info("Enter getMemberPolicy==> " + str(avars))
    db = self.db
    rspobj={}
    
    try:
      
      
      p = db((db.provider.provider == "P0001") & (db.provider.is_active == True)).select(db.provider.id)
      defproviderid = int(common.getid(p[0].id if(len(p) >=1) else 0))
      
      providerid = int(common.getid(common.getkeyvalue(avars,"providerid",str(defproviderid))))
      prov = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.city)
      
      #region regiond code      
      city = prov[0].city if(len(prov) != 0) else "Jaipur"
      regionid = common.getregionidfromcity(db,city)
      regioncode =  common.getregioncodefromcity(db,city)         
    
      #get company code
      memberid = int(common.getid(common.getkeyvalue(avars,"memberid","0")))
      members = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.patientmember.company,db.patientmember.hmoplan)
    
      companyid = int(common.getid(members[0].company) if (len(members) == 1) else "0")
      c = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
      companycode = c[0].company if (len(c) ==1) else ""
    
    
      #get hmoplan code
      hmoplanid = int(common.getid(members[0].hmoplan) if (len(members) == 1) else "0")  #members hmoplan assigned
      h = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.is_active == True)).select()    
      hmoplancode = h[0].hmoplancode if(len(h) == 1) else "PREMWALKIN"
    
      #get policy from provider-region-plan corr to companycode, regioncode and hmoplancode
      prp = db((db.provider_region_plan.companycode == companycode) &\
               (db.provider_region_plan.regioncode == regioncode) &\
               (db.provider_region_plan.plancode == hmoplancode) &\
               (db.provider_region_plan.is_active == True)).select() 
    
      policy = prp[0].policy if(len(prp) == 1) else "PREMWALKIN"  #get policy corr.
      
      rspobj = {}
      rspobj["memberid"] = str(memberid)
      rspobj["providerid"] = str(providerid)
      rspobj["plan"] = policy
      

    except Exception as e:
      mssg = "Get Member Policy Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)     
    
    logger.loggerpms2.info("Exit getMemberPolicy==> " + json.dumps(rspobj))
    return json.dumps(rspobj)
  
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
    
    rgns = db(db.groupregion.is_active == True).select(db.groupregion.groupregion,orderby=db.groupregion.groupregion)
    
    
    rgnlist = []
    
    for rgn in rgns:
      rgnlist.append(rgn.groupregion)
    
    rgnlist[0] = "--Select Region--"
    
    
    
    
    return json.dumps(rgnlist)
  
  def getMedicalHistory(self,memberid,patientid):
  
    db = self.db
    providerid = self.providerid    
    medhistobj = {}
    
    try:
      medhist = db((db.medicalnotes.patientid == patientid) & (db.medicalnotes.memberid == memberid)).select()
      
      pats = db((db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid == memberid)).\
        select(db.vw_memberpatientlist.dob,db.vw_memberpatientlist.gender,db.vw_memberpatientlist.fullname)
      
      
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
          medhistobj["memberid"] = memberid
          medhistobj["patientid"] = patientid
          medhistobj["membername"] = pat[0].fullame
          
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
  
  
  
  # Display all Walk-in Patients assigned to the Provider matching the 'Search'
  # For Members, Display all those Patients who have seeked appointments in the past or in future. This means that
  # since taking an appointment, they have agreed to the Provider. List these members based on the search phrase filter
  
  #def searchpatient(self,page,patientsearch,maxcount,patientmembersearch,hmopatientmember, company=""):
  def searchpatient(self,avars):    
    logger.loggerpms2.info("Enter Search Patient " + json.dumps(avars))

    
    try:
      db = self.db

      page = common.getkeyvalue(avars,"page","0")
      page = 0 if((page==None)|(page == "")) else int(common.getid(page))

      maxcount = common.getkeyvalue(avars,"maxcount","0")
      maxcount = 0 if((maxcount==None)|(maxcount == "")) else int(common.getid(maxcount))

      
      patientsearch = common.getkeyvalue(avars,"searchphrase","")
      patientsearch = "" if((patientsearch==None)) else patientsearch
      
      patientmembersearch = common.getkeyvalue(avars,"patientmembersearch",patientsearch)
      patientmembersearch = patientsearch if((patientmembersearch==None)|(patientmembersearch=="")) else patientmembersearch
      
      hmopatientmember = common.getkeyvalue(avars,"member","")
      hmopatientmember = "" if((hmopatientmember==None)|(hmopatientmember=="")) else common.getboolean(hmopatientmember)  #default to walk-in members
      

      company = common.getkeyvalue(avars,"company","")
      company = "" if((company==None)) else company

      c = db(db.company.company == company).select(db.company.id)
      companyid = 0 if(len(c) != 1) else int(common.getid(c[0].id))      

      providerid = common.getkeyvalue(avars,"providerid","0")
      providerid = 0 if((providerid==None)|(providerid == "")) else int(common.getid(providerid))
      
      
      result = False
      patlist = []
      
      
     
        
        
      pats=None
      
      urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
      
      page = page -1
      urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
      items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
      limitby = None if page < 0 else ((page)*items_per_page,(page+1)*items_per_page)      
      memberset = set()
      
      #display all those patients who have seeked appointments with this provider. Appointment guarantees that these patient/members have 
      #agreed to this provider.
      memberset = set()
    
      appts = db((db.t_appointment.is_active == True)&\
                 (db.t_appointment.f_status != 'Cancelled')&\
                 (db.t_appointment.provider == providerid)).select(db.t_appointment.patientmember, db.t_appointment.patient)
    
      for appt in appts:
        if(appt.patientmember in memberset):
          continue
        memberset.add(appt.patientmember)      

      #also add those patients & members who is assigned to this Provider outside the Appt. but from Customer Support
      
      qry = (db.vw_memberpatientlist.is_active == True)

      if(providerid > 0):
        q = (qry) & ((db.vw_memberpatientlist.hmopatientmember == True) & (db.vw_memberpatientlist.providerid == providerid))
        pats = db(q).select(db.vw_memberpatientlist.primarypatientid)
        for pat in pats:
          if(pat.primarypatientid in memberset):
            continue
          memberset.add(pat.primarypatientid)
      
      if(hmopatientmember == True):
        qry = (qry) & ((db.vw_memberpatientlist.primarypatientid.belongs(memberset)) & (db.vw_memberpatientlist.hmopatientmember == True))
        #qry = (qry) & ((db.vw_memberpatientlist.primarypatientid.belongs(memberset)) & (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt))
        #qry = (qry) & ((patientsearch != "") & (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt))
      
      elif(hmopatientmember==False):
        #display all Walk-in Patients for this Provider
        if(providerid > 0):
          qry = (qry) & (db.vw_memberpatientlist.hmopatientmember == False) & (db.vw_memberpatientlist.providerid == providerid)
        else:
          qry = qry & ( 1 !=1 ) #display no walk in patients
         
      else:
        if(providerid > 0):  #list of walk-in patients for this Provider + list of MDP Members matching the search phrase  (removed premenddt check)
          qry = (qry) & (((db.vw_memberpatientlist.hmopatientmember == False) & (db.vw_memberpatientlist.providerid == providerid)) |\
                         ((db.vw_memberpatientlist.primarypatientid.belongs(memberset)) &  (db.vw_memberpatientlist.hmopatientmember == True)))
        else: # list of MDP Members matching the search phrase
          qry = (qry) & ((db.vw_memberpatientlist.primarypatientid.belongs(memberset)) &  (db.vw_memberpatientlist.hmopatientmember == True))



        #if(providerid > 0):  #list of walk-in patients for this Provider + list of MDP Members matching the search phrase
          #qry = (qry) & (((db.vw_memberpatientlist.hmopatientmember == False) & (db.vw_memberpatientlist.providerid == providerid)) |\
                         #((patientsearch != "") &  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) ))
        #else: # list of MDP Members matching the search phrase
          #qry = (qry) & ((patientsearch != "") &  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt))
          ##qry = (qry) & ((db.vw_memberpatientlist.hmopatientmember == False) | (  (db.vw_memberpatientlist.hmopatientmember == True) &  (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) ))
    
      if(companyid >0):
        qry = (qry) & (db.vw_memberpatientlist.company == companyid)
  
    
      #if(patientsearch != ""):
        #qry = ((qry) & ((db.vw_memberpatientlist.patient.like("%" + patientsearch + "%")) | (db.vw_memberpatientlist.patientmember.like("%" + patientmembersearch + "%"))))
        
      logger.loggerpms2.info("Search Query = " + str(qry))
      
      
      #is it numeric only, then search on cell numbero
      if(patientsearch.replace("+",'').replace(' ','').isdigit()):
          pats=db((qry) & (db.vw_memberpatientlist.cell.like("%" + patientsearch + "%")))\
                  .select(db.vw_memberpatientlist.hmopatientmember,\
                                db.vw_memberpatientlist.patientmember,\
                                db.vw_memberpatientlist.fname,\
                                db.vw_memberpatientlist.lname,\
                                db.vw_memberpatientlist.primarypatientid,\
                                db.vw_memberpatientlist.patientid,\
                                db.vw_memberpatientlist.patienttype,\
                                db.vw_memberpatientlist.relation,\
                                db.vw_memberpatientlist.cell,\
                                db.vw_memberpatientlist.email,\
                                db.vw_memberpatientlist.dob,\
                                db.vw_memberpatientlist.gender,\
                                db.vw_memberpatientlist.age,\
                                limitby=limitby,orderby=db.vw_memberpatientlist.fname)
          maxcount = maxcount if (maxcount > 0 ) else db((qry) & (db.vw_memberpatientlist.cell.like("%" + patientsearch + "%"))).count()
      
      #is it email only
      elif(patientsearch.find("@") >= 0):
        pats=db((qry) & (db.vw_memberpatientlist.email.like("%" + patientsearch + "%")))\
                .select(db.vw_memberpatientlist.hmopatientmember,\
                              db.vw_memberpatientlist.patientmember,\
                              db.vw_memberpatientlist.fname,\
                              db.vw_memberpatientlist.lname,\
                              db.vw_memberpatientlist.primarypatientid,\
                              db.vw_memberpatientlist.patientid,\
                              db.vw_memberpatientlist.patienttype,\
                              db.vw_memberpatientlist.relation,\
                              db.vw_memberpatientlist.cell,\
                              db.vw_memberpatientlist.email,\
                              db.vw_memberpatientlist.dob,\
                              db.vw_memberpatientlist.gender,\
                              db.vw_memberpatientlist.age,\
                              limitby=limitby,orderby=db.vw_memberpatientlist.fname)
        maxcount = maxcount if (maxcount > 0 ) else db((qry) & (db.vw_memberpatientlist.email.like("%" + patientsearch + "%"))),count()
        
      #if pats is empty, then search for phrase in patient (fname lname:membercode)
      else:
        if(patientsearch != ""):
          qry = ((qry) & ((db.vw_memberpatientlist.patient.like("%" + patientsearch + "%")) | (db.vw_memberpatientlist.patientmember.like("%" + patientmembersearch + "%"))))        
          logger.loggerpms2.info("Search Patient Query = " + str(qry))
        
        pats = db((qry))\
          .select(db.vw_memberpatientlist.hmopatientmember,\
                  db.vw_memberpatientlist.patientmember,\
                  db.vw_memberpatientlist.fname,\
                  db.vw_memberpatientlist.lname,\
                  db.vw_memberpatientlist.primarypatientid,\
                  db.vw_memberpatientlist.patientid,\
                  db.vw_memberpatientlist.patienttype,\
                  db.vw_memberpatientlist.relation,\
                  db.vw_memberpatientlist.cell,\
                  db.vw_memberpatientlist.email,\
                  db.vw_memberpatientlist.dob,\
                  db.vw_memberpatientlist.gender,\
                  db.vw_memberpatientlist.age,\
                  limitby=limitby,orderby=db.vw_memberpatientlist.fname)
        
        maxcount = maxcount if (maxcount > 0) else db((qry)).count()
      
      
      
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
          "email":pat.email,
          "age":pat.age,
          "dob":common.getstringfromdate(pat.dob,"%d/%m/%Y"),
          "gender":pat.gender
          
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
      
      rsp = {"patientcount":len(pats),"page":page+1,"patientlist":patlist, "runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev,\
                         "patientsearch":patientsearch,"patientmembersearch":patientmembersearch,"member":hmopatientmember,"company":company,"result":"success","error_message":"","error_code":""} 
      
      #logger.loggerpms2.info("Exit Search Patient " + json.dumps(rsp))
    except Exception as e:
      mssg = "Search Patient Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)  
        
    return json.dumps(rsp )
  
  
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
    logger.loggerpms2.info("Enter GetPatient API =>> " + str(memberid) + " " + str(patientid))
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
                   
    logger.loggerpms2.info(json.dumps(memobj))
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
    logger.loggerpms2.info("Enter Update Walk In Patient ==> "+ json.dumps(patobj))
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    retobj = {}
    try:
      memberid = int(common.getid(patobj["memberid"]))
      patientid = int(common.getid(patobj["patientid"]))
      
      pats = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select()              
      
      
      dobstr = common.getkeyvalue(patobj,"dob","")
      dob = common.getdatefromstring(dobstr,"%d/%m/%Y") if(dobstr != "") else (None if(len(pat) == 0) else pat[0].dob)
      
      db(db.patientmember.id == memberid).update(\
    
        title = common.getkeyvalue(patobj,'title', pats[0].title if(len(pats) > 0) else ""),
        fname = common.getkeyvalue(patobj,'fname', pats[0].fname if(len(pats) > 0) else ""),
        mname = common.getkeyvalue(patobj,'mname', pats[0].mname if(len(pats) > 0) else ""),
        lname = common.getkeyvalue(patobj,'lname', pats[0].lname if(len(pats) > 0) else ""),
        dob = dob,
        cell = common.getkeyvalue(patobj,'cell', pats[0].cell if(len(pats) > 0) else ""),
        email = common.getkeyvalue(patobj,'email', pats[0].email if(len(pats) > 0) else ""),
        gender = common.getkeyvalue(patobj,'gender', pats[0].gender if(len(pats) > 0) else ""),
        address1 = common.getkeyvalue(patobj,'address1', pats[0].address1 if(len(pats) > 0) else ""),
        address2 = common.getkeyvalue(patobj,'address2', pats[0].address2 if(len(pats) > 0) else ""),
        address3 =common.getkeyvalue(patobj,'address3', pats[0].address3 if(len(pats) > 0) else ""),
        city = common.getkeyvalue(patobj,'city', pats[0].city if(len(pats) > 0) else ""),
        st = common.getkeyvalue(patobj,'st', pats[0].st if(len(pats) > 0) else ""),
        pin = common.getkeyvalue(patobj,'pin', pats[0].pin if(len(pats) > 0) else ""),
        status = common.getkeyvalue(patobj,'status', pats[0].status if(len(pats) > 0) else ""),
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1 if(auth.user == None) else auth.user.id     
        
      )
      
      retobj = {"result":"success","error_message":"","memberid":str(memberid),"patientid":str(patientid)}
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
      todaystr = common.getstringfromdate(todaydt,"%d/%m/%Y")
      patid = db.patientmember.insert(
           patientmember = patientmember,
           groupref = 'walkin',
           title = common.getkeyvalue(patobj,"title",""),
           fname = common.getkeyvalue(patobj,"fname",patientmember + "_FN"),
           mname = common.getkeyvalue(patobj,"mname",""),
           lname = common.getkeyvalue(patobj,"lname",patientmember + "_LN"),
           dob =   common.getdatefromstring(common.getkeyvalue(patobj,"dob",todaystr),"%d/%m/%Y"),
           cell = common.getkeyvalue(patobj,"cell","18001027526"),
           email = common.getkeyvalue(patobj,"email","customersupport@mydentalplan.in"),
           gender = common.getkeyvalue(patobj,"gender","Male"),
           address1 = common.getkeyvalue(patobj,"address1","331-332 Ganpat Plaza"), 
           address2 = common.getkeyvalue(patobj,"address2","M.I. Road"),
           address3 = common.getkeyvalue(patobj,"address3",""),
           city = common.getkeyvalue(patobj,"city","Jaipur"),
           st = common.getkeyvalue(patobj,"st","Rajasthan (RA)"),
           pin = common.getkeyvalue(patobj,"pin","302001"),
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
    company = ""
    patobj = {}
    
    try:
      r = db(db.provider.id == providerid).select(db.provider.provider)
      if(len(r)>0):
        provider = r[0].provider
      
      r = db((db.company.company == ' ') & (db.company.is_active == False)).select()
      if(len(r) > 0):
          companyid = common.getid(r[0].id)
          company = r[0].company
      
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
      
      obj={
        "plan":company,
        "memberid":patid
      }
      
      bnft = mdpbenefits.Benefit(db)
      bnft.map_member_benefit(obj)

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
                           modified_by =1 if(auth.user == None) else auth.user.id
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
    
    logger.loggerpms2.info("Enter newpatientifromcustomer " + json.dumps(avars))
    patobj = {}
    
    try:
      providerid = common.getkeyvalue(avars,"providerid",0)
      companyid = common.getkeyvalue(avars,"companyid",0)
      planid = common.getkeyvalue(avars,"planid",0)
      regionid = common.getkeyvalue(avars,"regionid",0)
      
      premstartdt_str = common.getkeyvalue(avars,"premstartdt","")
      premenddt_str = common.getkeyvalue(avars,"premenddt","")
      
      sql = "UPDATE membercount SET membercount = membercount + 1 WHERE company = " + str(companyid) + ";"
      db.executesql(sql)
      db.commit()      
        
      r = db(db.groupregion.id == regionid).select(db.groupregion.groupregion)
      region = r[0].groupregion if(len(r)==1) else "ALL"
      
      c = db(db.company.id == companyid).select(db.company.company)
      companycode = c[0].company if(len(c)==1) else "MYDP"
      
      
      
      xrows = db(db.membercount.company == companyid).select()
      if(len(xrows) == 0):
        db.membercount.insert(company=companyid,dummy1= 'X')
        db.commit()
        xrows = db(db.membercount.company == companyid).select()
        
      membercount = int(xrows[0].membercount)
     
      
      patientmember = region + companycode[:3] + str(companyid).zfill(3) + str(membercount)                                     
      
      todaydt = datetime.date.today()
      enrolldate = common.getkeyvalue(avars,"enrolldate","")
      
      if(premstartdt_str != ""):
        premstartdt = common.getdatefromstring(premstartdt_str, "%d/%m/%Y")
        premenddt = common.getdatefromstring(premenddt_str, "%d/%m/%Y")
      else:
        premstartdt = todaydt if((enrolldate == None)|(enrolldate == "")) else (datetime.datetime.strptime(enrolldate,"%d/%m/%Y")).date()
        
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
     
      obj={
        "plan":companycode,
        "memberid":patid
      }
      
      bnft = mdpbenefits.Benefit(db)
      bnft.map_member_benefit(obj)
  
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
        "dob":common.getstringfromdate(pat[0].dob,"%d/%m/%Y"),  #pat[0].dob.strftime("%d/%m/%Y"),
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
        "premstartdt":common.getstringfromdate(pat[0].premstartdt,"%d/%m/%Y"),   #pat[0].premstartdt.strftime("%d/%m/%Y"), 
        "premenddt":common.getstringfromdate(pat[0].premenddt,"%d/%m/%Y"),       #pat[0].premenddt.strftime("%d/%m/%Y"), 
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
   
 
  
  
  
  def registerVCPatient(self,avars):
    logger.loggerpms2.info("Enter Register VC Patient " + json.dumps(avars))
    db = self.db
    providerid = self.providerid
    
    try:
      
      if(providerid == 0):
        prov = db(db.provider.provider == 'P0001').select(db.provider.id)
        providerid = prov[0].id if(len(prov) > 0) else 0
        
        if(providerid == 0):
          mssg = "Register VC Patient API - Invalid Providerid"
          logger.loggerpms2.info(mssg)    
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = mssg
          return json.dumps(excpobj)
      
      
    
      
      
      cell = common.getkeyvalue(avars,"cell","")
      email = common.getkeyvalue(avars,"email","")
      name = common.getkeyvalue(avars,"name","")
      
      x = name.split(' ')
      fname = name if(len(x) == 0) else x[0]
      lname = "" if(len(x)<=1) else x[1]      

      dobstr = common.getkeyvalue(avars,"dob",common.getstringfromdate(common.getISTFormatCurrentLocatTime(),"%d/%m/%Y"))
      
      reqObj={
        "action":"searchpatient",
        "providerid":str(providerid),
        "searchphrase":cell
      }
      respObj = json.loads(self.searchpatient(reqObj))
      
      #error search patient
      if(respObj["result"] != "success"):
        mssg = "Register VC Patient API - Invalid Search Patient"
        logger.loggerpms2.info(mssg)    
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
      
      #patient already registered
      if(respObj["patientcount"] > 0):
        xrespObj = {}
        xrespObj["result"] = "success"
        xrespObj["error_message"] = ""
        patientlist = respObj["patientlist"]
        xrespObj["patientmember"] = patientlist[0]["patientmember"]
        xrespObj["memberid"] = patientlist[0]["memberid"]
        xrespObj["patientid"] = patientlist[0]["patientid"]
        
        return json.dumps(xrespObj)
      
      
      #register walk-in patient
      reqObj = {
        "action":"newalkinpatient",
        "providerid":providerid,
        "fname":fname,
        "lname":lname,
        "cell":cell,
        "email":email,
        "dob": dobstr
      }
      
      self.providerid = providerid
      self.db = db
      respObj = json.loads(self.newalkinpatient(reqObj))
      
      if(respObj["result"] != "success"):
        mssg = "Register VC Patient API - Error Registering Walk-in Patient " + name
        logger.loggerpms2.info(mssg)    
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)
          
    except Exception as e:
      mssg = "Register VC Patient API  Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] =mssg
      return json.dumps(excpobj)
    
    logger.loggerpms2.info("Exit Register VC Patient " + json.dumps(respObj))
    return json.dumps(respObj)
    
    
  def addpatientimage(self,avars):
    
    db = self.db
    providerid = self.providerid
    
    try:
      
      
      patientid = int(common.getid(common.getkeyvalue(avars,"patientid","0")))
      memberid = int(common.getid(common.getkeyvalue(avars,"memberid","0")))
      
      avars["action"] = 'upload_media'
      avars["providerid"] = str(providerid)
      
      avars["ref_code"] = "MEM"
      avars["ref_id"] = str(memberid)
      avars["mediatype"] = "image"
      avars["mediaformat"] = "jpg"
      
      
      
      medobj = mdpmedia.Media(db, providerid, "image", "jpg")
      rsp = json.loads(medobj.upload_media(avars))
      
      if(rsp["result"] == "success"):
        
        db(db.patientmember.id == memberid).update(imageid = common.getkeyvalue(rsp,"mediaid","0"))
      
    except Exception as e:
        logger.loggerpms2.info("Add Patient Image API  Exception:\n" + str(e))      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = "Add Patient Image API Exception Error - " + str(e)
        return json.dumps(excpobj)
      
    return json.dumps(rsp)
    

    
      
    