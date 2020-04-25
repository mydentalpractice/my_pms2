from gluon import current
import json

import datetime
from datetime import timedelta



from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger

class Dentalchart:
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    return
  
  def getchartprocedures(self):
    db = self.db
    providerid = self.providerid
    jsonresp = {}
    proclist = []
    
    try:
      procs = db(db.vw_dentalprocedure_chart.is_active == True).select()
      
      for proc in procs:
        
        procobj = {
          "procid":proc.id,
          "proccode":proc.proccode,
          "description":proc.altshortdescription
        }
        proclist.append(procobj)
        
      jsonresp = {
      
        "proccount":len(proclist),
        "proclist":proclist,
        "result":"success",
        "error_message":""
      }
    except Exception as e:
        logger.loggerpms2.info("Get Tooth Procedures Exception:\n" + str(e))
        jsonresp = {
          "result":"fail",
          "error_message":"Get Tooth Procedures Exception:\n" + str(e)
        }    
            
    return json.dumps(jsonresp)
    
      
  def getalltoothcolours(self,chartid):
    db = self.db
    providerid = self.providerid
    jsonresp = {}

    colorlist = []
    
    try:
      
      tooths = db((db.tooth.chartid == chartid) & (db.tooth.is_active == True)).select()
      
      for tooth in tooths:
        strarr = (tooth.toothid).split('-')
        section = int(strarr[1]) if(len(strarr) > 2) else 0
        colour = tooth.p1 if(section != 5) else tooth.e1
        
        colorobj = {
          #"chatdate":(tooth.chartdate).strftime("%d/%m/%Y"),
          #"doctorid":tooth.doctorid,
          #"procedureid":tooth.procedureid,
          #"treatmentid":tooth.treatmentid,
          "toothid":tooth.toothid,
          "toothnumber":tooth.toothnumber,
          #"toothsection":tooth.toothsection,
          #"notes":tooth.notes,
          
          "section":str(section),
          "colour": colour
        
        }
        
        colorlist.append(colorobj)
        
      jsonresp={"colourcount":len(colorlist),"colourlist":colorlist,"result":"success","error_message":""}
      
      
    except Exception as e:
      logger.loggerpms2.info("Get Tooth Colors Exception:\n" + str(e))
      jsonresp = {
        "result":"fail",
        "error_message":"Get Tooth Colors Exception:\n" + str(e)
      }    
    
    return json.dumps(jsonresp)
  
  
  def gettoothcolours(self,chartid,toothnumber):
    db = self.db
    providerid = self.providerid
    jsonresp = {}

    colorlist = []
    
    try:
      
      tooths = db((db.tooth.chartid == chartid) & (db.tooth.toothnumber == toothnumber)).select()
      
      for tooth in tooths:
        strarr = (tooth.toothid).split('-')
        section = int(strarr[1]) if(len(strarr) > 2) else 0
        colour = tooth.p1 if(section != 5) else tooth.e1
        
        colorobj = {
          "chatdate":(tooth.chartdate).strftime("%d/%m/%Y"),
          "doctorid":tooth.doctorid,
          "procedureid":tooth.procedureid,
          "treatmentid":tooth.treatmentid,
          "toothid":tooth.toothid,
          "toothnumber":tooth.toothnumber,
          "toothsection":tooth.toothsection,
          "notes":tooth.notes,
          
          "section":str(section),
          "colour": colour
        
        }
        
        colorlist.append(colorobj)
        
      jsonresp={"colourcount":len(colorlist),"colourlist":colorlist,"result":"success","error_message":""}
      
      
    except Exception as e:
      logger.loggerpms2.info("Get Tooth Colors Exception:\n" + str(e))
      jsonresp = {
        "result":"fail",
        "error_message":"Get Tooth Colors Exception:\n" + str(e)
      }    
    
    return json.dumps(jsonresp)
  
  
  def getdentalchart(self, memberid, patientid):
    
    db = self.db
    providerid = self.providerid
    chartid = 0
    
    toothlist = []
    
    jsonresp = {}
    
    patientname = ""
    gender = ""
    age = ""
    r = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid == memberid)).select()
    if(len(r) > 0):
        patientname = r[0].patient
        gender = r[0].gender
        age = int(common.getid(r[0].age))
    
    
    try:
      
      dch = db((db.dentalchart.providerid == providerid)&\
               (db.dentalchart.patientid == patientid)&\
               (db.dentalchart.memberid == memberid)&\
               (db.dentalchart.is_active == True)).select()
      
      chartid = dch[0].id if(len(dch)>=1) else 0

      
      tooths=db((db.tooth.chartid == chartid) & (db.tooth.is_active == True)).select(db.tooth.toothnumber,distinct=True)
      
      for tooth in tooths:
        toothobj = {
          #"chatdate":(tooth.chartdate).strftime("%d/%m/%Y"),
          #"doctorid":tooth.doctorid,
          #"procedureid":tooth.procedureid,
          #"treatmentid":tooth.treatmentid,
          #"toothid":tooth.toothid,
          "toothnumber":tooth.toothnumber,
          #"toothsection":tooth.toothsection,
          #"notes":tooth.notes
        }
        toothlist.append(toothobj)
      
      jsonresp = {
        "chartid":chartid,
        "toothcount":str(len(toothlist)),
        "patientname":patientname,
        "gender":gender,
        "age":age,
        "toothlist":toothlist,
        "result":"success",
        "error_message":""
      
      }
    
    
    except Exception as e:
      logger.loggerpms2.info("Get Dental Chart Exception:\n" + str(e))
      jsonresp = {
        "result":"fail",
        "error_message":"Get Dental Chart Exception:\n" + str(e)
      }
    
    return json.dumps(jsonresp)
    
    