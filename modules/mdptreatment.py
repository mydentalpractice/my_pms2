from gluon import current
import os
import json
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

from applications.my_pms2.modules import mdputils

datefmt = "%d/%m/%Y"
datetimefmt = "%d/%m/%Y %H:%M:%S"

def serializedatetime(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()    
   
   

def updatetreatmentcostandcopay(db,treatmentid,tplanid):
    totalactualtreatmentcost = 0   #UCR Cost
    totaltreatmentcost = 0  #Cost charged to the client which is equal to UCR fee by default
    totalcopay = 0
    totalinspays = 0
    totalcompanypays = 0
    
    #strsql = "select sum(ucrfee) as totalactualtreatmentcost, sum(procedurefee) as totaltreatmentcost, sum(copay) as copay, sum(inspays) as inspays, sum(companypays) as companypays"
    #strsql = strsql + " from  vw_treatmentprocedure where treatmentid =" +  str(treatmentid) + " and is_active = 'T'  group by treatmentid "   
    #ds = db.executesql(strsql)
    
    rows = db((db.vw_treatmentprocedure.treatmentid == treatmentid) & (db.vw_treatmentprocedure.is_active == True)).select(\
    
        db.vw_treatmentprocedure.ucrfee.sum(),\
        db.vw_treatmentprocedure.procedurefee.sum(),\
        db.vw_treatmentprocedure.copay.sum(),\
        db.vw_treatmentprocedure.inspays.sum(),\
        db.vw_treatmentprocedure.companypays.sum(),\
        orderby=db.vw_treatmentprocedure.treatmentid,\
        groupby=db.vw_treatmentprocedure.treatmentid\
        
    )
    
    totalactualtreatmentcost = float(common.getvalue(rows.response[0][0])) if(len(rows) == 1) else 0
    totaltreatmentcost = float(common.getvalue(rows.response[0][1])) if(len(rows) == 1) else 0
    totalcopay = float(common.getvalue(rows.response[0][2])) if(len(rows) == 1) else 0
    totalinspays = float(common.getvalue(rows.response[0][3])) if(len(rows) == 1) else 0
    totalcompanypays = float(common.getvalue(rows.response[0][4])) if(len(rows) == 1) else 0  
    
    totaldue     = 0
    tp = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).select(db.treatmentplan.totaltreatmentcost,\
                                                                                                db.treatmentplan.totalpaid,\
                                                                                                db.treatmentplan.totalcopaypaid,\
                                                                                                db.treatmentplan.totalinspaid)
    
    if(len(tp) == 1):
        totaldue = float(common.getvalue(tp[0].totaltreatmentcost)) - float(common.getvalue(tp[0].totalpaid)) - \
            float(common.getvalue(tp[0].totalcopaypaid)) - float(common.getvalue(tp[0].totalinspaid))
    
    
    db(db.treatment.id == treatmentid).update(actualtreatmentcost = totalactualtreatmentcost, treatmentcost=totaltreatmentcost, copay=totalcopay, inspay=totalinspays, companypay= totalcompanypays)
    
    #update treatmentplan assuming there is one treatment per tplan
    db(db.treatmentplan.id==tplanid).update(totaltreatmentcost = totaltreatmentcost, totalcopay=totalcopay,totalinspays=totalinspays,totaldue=totaldue)
    
    db.commit()
    
    return dict(totaltreatmentcost=totaltreatmentcost, totalcopay=totalcopay,totalinspays=totalinspays,totaldue=totaldue)

class Treatment:
    
    
    
    def __init__(self,db,providerid):
        self.db = db
        self.providerid = providerid
        return   
    
    def updatetreatmentcostandcopay(self,treatmentid,tplanid):
        db = self.db
        providerid = self.providerid
        
        totalactualtreatmentcost = 0   #UCR Cost
        totaltreatmentcost = 0  #Cost charged to the client which is equal to UCR fee by default
        totalcopay = 0
        totalinspays = 0
        totalcompanypays = 0
        
        #strsql = "select sum(ucrfee) as totalactualtreatmentcost, sum(procedurefee) as totaltreatmentcost, sum(copay) as copay, sum(inspays) as inspays, sum(companypays) as companypays"
        #strsql = strsql + " from  vw_treatmentprocedure where treatmentid =" +  str(treatmentid) + " and is_active = 'T'  group by treatmentid "   
        #ds = db.executesql(strsql)
        
        rows = db((db.vw_treatmentprocedure.treatmentid == treatmentid) & (db.vw_treatmentprocedure.is_active == True)).select(\
        
            db.vw_treatmentprocedure.ucrfee.sum(),\
            db.vw_treatmentprocedure.procedurefee.sum(),\
            db.vw_treatmentprocedure.copay.sum(),\
            db.vw_treatmentprocedure.inspays.sum(),\
            db.vw_treatmentprocedure.companypays.sum(),\
            orderby=db.vw_treatmentprocedure.treatmentid,\
            groupby=db.vw_treatmentprocedure.treatmentid\
            
        )
        
        totalactualtreatmentcost = float(common.getvalue(rows.response[0][0])) if(len(rows) == 1) else 0
        totaltreatmentcost = float(common.getvalue(rows.response[0][1])) if(len(rows) == 1) else 0
        totalcopay = float(common.getvalue(rows.response[0][2])) if(len(rows) == 1) else 0
        totalinspays = float(common.getvalue(rows.response[0][3])) if(len(rows) == 1) else 0
        totalcompanypays = float(common.getvalue(rows.response[0][4])) if(len(rows) == 1) else 0  
        
        totaldue     = 0
        tp = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).select(db.treatmentplan.totaltreatmentcost,\
                                                                                                    db.treatmentplan.totalpaid,\
                                                                                                    db.treatmentplan.totalcopaypaid,\
                                                                                                    db.treatmentplan.totalinspaid)
        
        if(len(tp) == 1):
            totaldue = float(common.getvalue(tp[0].totaltreatmentcost)) - float(common.getvalue(tp[0].totalpaid)) - \
                float(common.getvalue(tp[0].totalcopaypaid)) - float(common.getvalue(tp[0].totalinspaid))
        
        
        db(db.treatment.id == treatmentid).update(actualtreatmentcost = totalactualtreatmentcost, treatmentcost=totaltreatmentcost, copay=totalcopay, inspay=totalinspays, companypay= totalcompanypays)
        
        #update treatmentplan assuming there is one treatment per tplan
        db(db.treatmentplan.id==tplanid).update(totaltreatmentcost = totaltreatmentcost, totalcopay=totalcopay,totalinspays=totalinspays,totaldue=totaldue)
        
        db.commit()
        
        return dict(totaltreatmentcost=totaltreatmentcost, totalcopay=totalcopay,totalinspays=totalinspays,totaldue=totaldue)
    
    
    
    
    
    #def getopentreatments(self,page,memberid,patientid,searchphrase,maxcount,clinicid=0):
    def getopentreatments(self,avars):
        
        #logger.loggerpms2.info("Enter GetOpen Treatments API " + json.dumps(avars))
        
        db = self.db
        providerid = self.providerid
        
    
        memberid = int(common.getid(common.getkeyvalue(avars,"memberid","0")))
        patientid = int(common.getid(common.getkeyvalue(avars,"patientid","0")))
        page = int(common.getid(common.getkeyvalue(avars,"page","0")))
        clinicid = int(common.getid(common.getkeyvalue(avars,"clinicid","0")))        
        maxcount = int(common.getid(common.getkeyvalue(avars,"maxcount","0")))        
        searchphrase = common.getkeyvalue(avars,"searchphrase","")
        
        page = page -1
        urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
        items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
        limitby = ((page)*items_per_page,(page+1)*items_per_page) 
        trtmntobj  = {}
        
        try:
            query = (db.vw_treatmentlist.memberid == memberid) if(memberid > 0) else (1==1)
            query = query & (db.vw_treatmentlist.patientid == patientid) if(patientid > 0) else (1==1)
            query = query & (db.vw_treatmentlist.clinicid == clinicid) if(clinicid > 0) else (1==1)
            query = query & (db.vw_treatmentlist.status == "Started")  
            
            #IB 31/01/2020 Sending all treatments
            #query = query & ((db.vw_treatmentlist.is_active == True) | ((db.vw_treatmentlist.is_active == False) & (db.vw_treatmentlist.status == "Cancelled" )))
            
            query =  (query )
            
            if((searchphrase == "") | (searchphrase == None)):
                query = query & ((db.vw_treatmentlist.providerid == providerid))
            else:
                query=  query & ((db.vw_treatmentlist.providerid == providerid) & (db.vw_treatmentlist.pattern.like('%' + searchphrase + '%')) )
    
             
            
            if(page >= 0):
                treatments = db(query).select(db.vw_treatmentlist.id,db.vw_treatmentlist.tplanid,db.vw_treatmentlist.treatment,db.vw_treatmentlist.startdate,db.vw_treatmentlist.clinicid,db.vw_treatmentlist.clinicname,db.patientmember.cell,\
                                              db.vw_treatmentlist.memberid,db.vw_treatmentlist.patientid,db.vw_treatmentlist.status,db.vw_treatmentlist.treatmentcost,db.vw_treatmentlist.patientname,db.vw_treatmentlist.memberid,db.vw_treatmentlist.patientid,\
                                              db.vw_treatment_procedure_group.shortdescription,\
                                              left=[db.vw_treatment_procedure_group.on(db.vw_treatment_procedure_group.treatmentid==db.vw_treatmentlist.id),\
                                                    db.patientmember.on(db.patientmember.id == db.vw_treatmentlist.memberid)],\
                                              limitby=limitby, orderby=~db.vw_treatmentlist.id)
                if(maxcount == 0):
                    maxcount = db(query).count()
            else:
                treatments = db(query).select(db.vw_treatmentlist.id,db.vw_treatmentlist.tplanid,db.vw_treatmentlist.treatment,db.vw_treatmentlist.startdate,db.vw_treatmentlist.clinicid,db.vw_treatmentlist.clinicname,db.patientmember.cell,  \
                                              db.vw_treatmentlist.memberid,db.vw_treatmentlist.patientid,db.vw_treatmentlist.status,db.vw_treatmentlist.treatmentcost,db.vw_treatmentlist.patientname,db.vw_treatmentlist.memberid,db.vw_treatmentlist.patientid,\
                                              db.vw_treatment_procedure_group.shortdescription,\
                                              left=[db.vw_treatment_procedure_group.on(db.vw_treatment_procedure_group.treatmentid==db.vw_treatmentlist.id),\
                                                    db.patientmember.on(db.patientmember.id == db.vw_treatmentlist.memberid)],\
                                              orderby=~db.vw_treatmentlist.id)
                if(maxcount == 0):
                    maxcount = db(query).count()
                    
            #logger.loggerpms2.info("Query = " + str(query))
            #logger.loggerpms2.info("Number of Treatments = " + str(len(treatments)))
            
            treatmentlist = []
            treatmentobj = {}
            
            for treatment in treatments:
                treatmentid = int(common.getid(treatment.vw_treatmentlist.id))
                tplanid = int(common.getid(treatment.vw_treatmentlist.tplanid))
                r= self.updatetreatmentcostandcopay(treatmentid, tplanid)
                treatmentobj = {
                    "treatmentid" : treatmentid,
                    "treatment": common.getstring(treatment.vw_treatmentlist.treatment),
                    "treatmentdate"  : (treatment.vw_treatmentlist.startdate).strftime("%d/%m/%Y"),
                    "patientname" : common.getstring(treatment.vw_treatmentlist.patientname),
                    "memberid":int(common.getid(treatment.vw_treatmentlist.memberid)),
                    "patientid":int(common.getid(treatment.vw_treatmentlist.patientid)),
                    "patcell":str(treatment.patientmember.cell),
                    "clinicid":str(treatment.vw_treatmentlist.clinicid),
                    "clinicname":treatment.vw_treatmentlist.clinicname,
                    "procedures":common.getstring(treatment.vw_treatment_procedure_group.shortdescription),
                    "status": "Started" if(common.getstring(treatment.vw_treatmentlist.status) == "") else common.getstring(treatment.vw_treatmentlist.status),
                    "totaltreatmentcost":float(common.getstring(r["totaltreatmentcost"])),
                    "totalcopay":float(common.getstring(r["totalcopay"])),
                    "totalinspays":float(common.getstring(r["totalinspays"])),
                    "totaldue":float(common.getstring(r["totaldue"])),
                    "totalpaid":float(common.getstring(r["totaltreatmentcost"]))-float(common.getstring(r["totaldue"])),
                    
                    
                }
                treatmentlist.append(treatmentobj)        
            
            xcount = ((page+1) * items_per_page) - (items_per_page - len(treatments)) 
            
            bnext = True
            bprev = True
            
            #first page
            if((page+1) == 1):
                bnext = True
                bprev = False
            
            #last page
            if(len(treatments) < items_per_page):
                bnext = False
                bprev = True  
                
            trtmntobj = {"treatmentcount":len(treatments),"page":page+1, "treatmentlist":treatmentlist,"runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev}
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "New Patient API Exception Error - " + str(e)
            return json.dumps(excpobj)       
            
    
        return json.dumps(trtmntobj)

    
    #def gettreatments(self,page,memberid,patientid,searchphrase,maxcount,treatmentyear,clinicid):
    def gettreatments(self,avars):
        
        db = self.db
        providerid = self.providerid
        
        memberid = int(common.getid(common.getkeyvalue(avars,"memberid","0")))
        patientid = int(common.getid(common.getkeyvalue(avars,"patientid","0")))
        page = int(common.getid(common.getkeyvalue(avars,"page","0")))
        clinicid = int(common.getid(common.getkeyvalue(avars,"clinicid","0")))        
        maxcount = int(common.getid(common.getkeyvalue(avars,"maxcount","0")))        
        searchphrase = common.getkeyvalue(avars,"searchphrase","")
        treatmentyear = (None if(avars["treatmentyear"] == "") else str(avars["treatmentyear"])   )  if "treatmentyear" in avars else None
        
            
        page = page -1
        urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
        items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
        limitby = ((page)*items_per_page,(page+1)*items_per_page) 
        
        limitby = None if(items_per_page <= 0) else limitby
        
        #logger.loggerpms2.info("page = " + str(page) + " limitby=" + str(limitby))
        trtmntobj  = {}
        
        try:
            startdate = datetime.datetime.strptime("01/01/" + treatmentyear, "%d/%m/%Y")  if(treatmentyear != None) else None
            enddate = datetime.datetime.strptime("31/12/" + treatmentyear, "%d/%m/%Y") if(treatmentyear != None) else None
            
            query = (1==1)
            query = (db.vw_treatmentlist.memberid == memberid) if(memberid > 0) else query

            query = (query & (db.vw_treatmentlist.patientid == patientid)) if(patientid > 0) else query
            
            query = (query & (db.vw_treatmentlist.providerid == providerid)) if(providerid > 0) else query

            query = (query & (db.vw_treatmentlist.clinicid == clinicid)) if(clinicid > 0) else query

            
            query = (query & ((db.vw_treatmentlist.startdate >= startdate) & (db.vw_treatmentlist.startdate <= enddate))) if(treatmentyear != None) else query
            
            #query = query & (db.vw_treatmentlist.is_active == True)
            #IB 31/01/2020 Sending all treatments - Cancelled, Started and Completed
            query = query & ((db.vw_treatmentlist.is_active == True) | ((db.vw_treatmentlist.is_active == False) & (db.vw_treatmentlist.status == "Cancelled" ))) 
            
            query =  (query)
            
            query = query if((searchphrase == "") | (searchphrase == None)) else query & (db.vw_treatmentlist.pattern.like('%' + searchphrase + '%'))
            
            if(page >= 0):
                treatments = db(query).select(db.vw_treatmentlist.id,db.vw_treatmentlist.tplanid,db.vw_treatmentlist.treatment,db.vw_treatmentlist.startdate, db.vw_treatmentlist.patientname,db.patientmember.cell,\
                                              db.vw_treatmentlist.memberid,db.vw_treatmentlist.patientid,db.vw_treatmentlist.status,db.vw_treatmentlist.treatmentcost,db.vw_treatment_procedure_group.shortdescription,\
                                              db.vw_treatmentlist.doctorid,db.vw_treatmentlist.doctorname, db.vw_treatmentlist.clinicid, db.vw_treatmentlist.clinicname,\
                                              left=[db.vw_treatment_procedure_group.on(db.vw_treatment_procedure_group.treatmentid==db.vw_treatmentlist.id),\
                                                    db.patientmember.on(db.patientmember.id == db.vw_treatmentlist.memberid)],\
                                              limitby=limitby, orderby=~db.vw_treatmentlist.id)
                if(maxcount == 0):
                    maxcount = db(query).count()
            else:
                treatments = db(query).select(db.vw_treatmentlist.id,db.vw_treatmentlist.tplanid,db.vw_treatmentlist.treatment,db.vw_treatmentlist.startdate, db.vw_treatmentlist.patientname,db.patientmember.cell,\
                                              db.vw_treatmentlist.memberid,db.vw_treatmentlist.patientid,db.vw_treatmentlist.status,db.vw_treatmentlist.treatmentcost,db.vw_treatment_procedure_group.shortdescription,\
                                              db.vw_treatmentlist.doctorid,db.vw_treatmentlist.doctorname, db.vw_treatmentlist.clinicid, db.vw_treatmentlist.clinicname,\
                                              left=[db.vw_treatment_procedure_group.on(db.vw_treatment_procedure_group.treatmentid==db.vw_treatmentlist.id),\
                                                    db.patientmember.on(db.patientmember.id == db.vw_treatmentlist.memberid)],\
                                              orderby=~db.vw_treatmentlist.id)
                if(maxcount == 0):
                    maxcount = db(query).count()
                    
            #logger.loggerpms2.info("Query = " + str(query))
            #logger.loggerpms2.info("Number of Treatments = " + str(len(treatments)))
            
            treatmentlist = []
            treatmentobj = {}
            
            
            for treatment in treatments:
                treatmentid = int(common.getid(treatment.vw_treatmentlist.id))
                tplanid = int(common.getid(treatment.vw_treatmentlist.tplanid))
                r= self.updatetreatmentcostandcopay(treatmentid, tplanid)
                treatmentobj = {
                    "treatmentid" : treatmentid,
                    "treatment": common.getstring(treatment.vw_treatmentlist.treatment),
                    "treatmentdate"  : (treatment.vw_treatmentlist.startdate).strftime("%d/%m/%Y"),
                    "patientname" : common.getstring(treatment.vw_treatmentlist.patientname),
                    "memberid":int(common.getid(treatment.vw_treatmentlist.memberid)),
                    "patientid":int(common.getid(treatment.vw_treatmentlist.patientid)),
                    "patcell":str(treatment.patientmember.cell),
                    "doctorid":str(treatment.vw_treatmentlist.doctorid),
                    "doctorname":treatment.vw_treatmentlist.doctorname,
                    "clinicid":str(treatment.vw_treatmentlist.clinicid),
                    "clinicname":treatment.vw_treatmentlist.clinicname,
                    "procedures":common.getstring(treatment.vw_treatment_procedure_group.shortdescription),
                    "status": "Started" if(common.getstring(treatment.vw_treatmentlist.status) == "") else common.getstring(treatment.vw_treatmentlist.status),
                    "totaltreatmentcost":float(common.getstring(r["totaltreatmentcost"])),
                    "totalcopay":float(common.getstring(r["totalcopay"])),
                    "totalinspays":float(common.getstring(r["totalinspays"])),
                    "totaldue":float(common.getstring(r["totaldue"])),
                    "totalpaid":float(common.getstring(r["totaltreatmentcost"]))-float(common.getstring(r["totaldue"])),
                   
                    
                }
                treatmentlist.append(treatmentobj)        
            
            xcount = ((page+1) * items_per_page) - (items_per_page - len(treatments)) 
            
            bnext = True
            bprev = True
            
            #first page
            if((page+1) == 1):
                bnext = True
                bprev = False
            
            #last page
            if(len(treatments) < items_per_page):
                bnext = False
                bprev = True  
                
            trtmntobj = {"result":"success","error_message":"","error_code":"",\
                         "treatmentcount":len(treatments),"page":page+1, "treatmentyear":treatmentyear,"treatmentlist":treatmentlist,"runningcount":xcount,\
                         "maxcount":maxcount, "next":bnext, "prev":bprev}
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "New Patient API Exception Error - " + str(e)
            return json.dumps(excpobj)       
            
        
        return json.dumps(trtmntobj)        
    

    
        
    def xgettreatments(self,page,memberid,patientid,searchphrase,maxcount):
        
        #logger.loggerpms2.info("Enter Get Treatments API")
        
        db = self.db
        providerid = self.providerid
        
        
        page = page -1
        urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
        items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
        limitby = ((page)*items_per_page,(page+1)*items_per_page) 
        trtmntobj  = {}
        
        try:
            query = (db.vw_treatmentlist.memberid == memberid) if(memberid > 0) else (1==1)
    
               
            query = query & (db.vw_treatmentlist.patientid == patientid) if(patientid > 0) else (1==1)
            
            
           
            query =  (query )
                
            if((searchphrase == "") | (searchphrase == None)):
                query = query & ((db.vw_treatmentlist.providerid == providerid) & (db.vw_treatmentlist.is_active == True))
            else:
                query=  query & ((db.vw_treatmentlist.providerid == providerid) & (db.vw_treatmentlist.pattern.like('%' + searchphrase + '%')) & (db.vw_treatmentlist.is_active == True))
    
             
            
            if(page >= 0):
                treatments = db(query).select(db.vw_treatmentlist.id,db.vw_treatmentlist.tplanid,db.vw_treatmentlist.treatment,db.vw_treatmentlist.startdate, \
                                              db.vw_treatmentlist.status,db.vw_treatmentlist.treatmentcost,db.vw_treatment_procedure_group.shortdescription,\
                                              left=db.vw_treatment_procedure_group.on(db.vw_treatment_procedure_group.treatmentid==db.vw_treatmentlist.id),\
                                              limitby=limitby, orderby=~db.vw_treatmentlist.id)
                if(maxcount == 0):
                    maxcount = db(query).count()
            else:
                treatments = db(query).select(db.vw_treatmentlist.id,db.vw_treatmentlist.tplanid,db.vw_treatmentlist.treatment,db.vw_treatmentlist.startdate, \
                                              db.vw_treatmentlist.status,db.vw_treatmentlist.treatmentcost,db.vw_treatment_procedure_group.shortdescription,\
                                              left=db.vw_treatment_procedure_group.on(db.vw_treatment_procedure_group.treatmentid==db.vw_treatmentlist.id), \
                                              orderby=~db.vw_treatmentlist.id)
                if(maxcount == 0):
                    maxcount = db(query).count()
                    
            #logger.loggerpms2.info("Query = " + str(query))
            #logger.loggerpms2.info("Number of Treatments = " + str(len(treatments)))
            
            treatmentlist = []
            treatmentobj = {}
            
            for treatment in treatments:
                treatmentid = int(common.getid(treatment.vw_treatmentlist.id))
                tplanid = int(common.getid(treatment.vw_treatmentlist.tplanid))
                r= self.updatetreatmentcostandcopay(treatmentid, tplanid)
                treatmentobj = {
                    "treatmentid" : treatmentid,
                    "treatment": common.getstring(treatment.vw_treatmentlist.treatment),
                    "treatmentdate"  : (treatment.vw_treatmentlist.startdate).strftime("%d/%m/%Y"),
                    "procedures":common.getstring(treatment.vw_treatment_procedure_group.shortdescription),
                    "status": "Started" if(common.getstring(treatment.vw_treatmentlist.status) == "") else common.getstring(treatment.vw_treatmentlist.status),
                    "totaltreatmentcost":float(common.getstring(r["totaltreatmentcost"])),
                    "totalcopay":float(common.getstring(r["totalcopay"])),
                    "totalinspays":float(common.getstring(r["totalinspays"])),
                    "totaldue":float(common.getstring(r["totaldue"]))
                    
                }
                treatmentlist.append(treatmentobj)        
            
            xcount = ((page+1) * items_per_page) - (items_per_page - len(treatments)) 
            
            bnext = True
            bprev = True
            
            #first page
            if((page+1) == 1):
                bnext = True
                bprev = False
            
            #last page
            if(len(treatments) < items_per_page):
                bnext = False
                bprev = True  
                
            trtmntobj = {"treatmentcount":len(treatments),"page":page+1, "treatmentlist":treatmentlist,"runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev}
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Get Treatments API Exception Error - " + str(e)
            return json.dumps(excpobj)       
            
    
        return json.dumps(trtmntobj)
        
        

    def gettreatment(self,treatmentid):
        
        #logger.loggerpms2.info("Enter Get Treatment API")
        
        db = self.db
        providerid = self.providerid        
        treatmentobj = {}
        
        query = (1==1)
        query1 = (1==1)
        query = (query & (db.vw_treatmentprocedure.providerid == providerid)) if(providerid > 0) else query
        query1 = (query1 & (db.vw_treatmentlist.providerid == providerid)) if(providerid > 0) else query1
        
        try:
        
            procs = db((db.vw_treatmentprocedure.treatmentid == treatmentid) & (query) &\
                       (db.vw_treatmentprocedure.is_active == True)).select()
    
            
            treatment = db((db.vw_treatmentlist.id == treatmentid) & (query1) & \
                           (db.vw_treatmentlist.is_active == True)).select(db.vw_treatmentlist.treatment,\
                                                                           db.vw_treatmentlist.startdate,\
                                                                           db.vw_treatmentlist.patientname,\
                                                                           db.vw_treatmentlist.chiefcomplaint,\
                                                                           db.vw_treatmentlist.status,\
                                                                           db.vw_treatmentlist.doctorid,\
                                                                           db.vw_treatmentlist.doctorname,\
                                                                           db.vw_treatmentlist.clinicid,\
                                                                           db.vw_treatmentlist.clinicname,\
                                                                           db.vw_treatmentlist.treatmentcost,
                                                                           db.vw_treatmentlist.memberid,
                                                                           db.vw_treatmentlist.patientid,
                                                                           db.vw_treatmentlist.tplanid,
                                                                           db.treatment.description,\
                                                                           db.vw_memberpatientlist.procedurepriceplancode,\
                                                                           db.vw_memberpatientlist.company,\
                                                                           db.vw_memberpatientlist.cell,\
                                                                          
                                                                           left = [db.treatment.on(db.treatment.id == db.vw_treatmentlist.id),\
                                                                                   db.vw_memberpatientlist.on((db.vw_memberpatientlist.primarypatientid==db.vw_treatmentlist.memberid)&\
                                                                                                              (db.vw_memberpatientlist.patientid==db.vw_treatmentlist.patientid))
                                                                                  
                                                                                   
                                                                                   
                                                                                   ])
                                                                           
            
            
            
            
            
            if(len(treatment) == 1):
                #logger.loggerpms2.info("Enter Get Treatment API - A")
                c = db(db.company.id == int(common.getid(treatment[0].vw_memberpatientlist.company))).select(db.company.authorizationrequired)
                #logger.loggerpms2.info("Enter Get Treatment API - A1 " + str(len(c)))
                
                tplanid = int(common.getid(treatment[0].vw_treatmentlist.tplanid))
                r = self.updatetreatmentcostandcopay(treatmentid, tplanid)
                #logger.loggerpms2.info("Enter Get Treatment API - A2 ")
                
                memberid = int(common.getid(treatment[0].vw_treatmentlist.memberid))
                patientid = int(common.getid(treatment[0].vw_treatmentlist.patientid))
                procedurepriceplancode = mdputils.getprocedurepriceplancodeformember(db,providerid,memberid,patientid)
                #logger.loggerpms2.info("Enter Get Treatment API - B")
                
                treatmentobj = {
                    
                    "treatmentid":treatmentid,
                    "tplanid":tplanid,
                    "treatment": common.getstring(treatment[0].vw_treatmentlist.treatment),
                    "memberid":memberid,
                    "patientid":patientid,
                    "treatmentdate"  : (treatment[0].vw_treatmentlist.startdate).strftime("%d/%m/%Y"),
                    "patientname": common.getstring(treatment[0].vw_treatmentlist.patientname),
                    "patcell": common.getstring(treatment[0].vw_memberpatientlist.cell),
                    "chiefcomplaint" : common.getstring(treatment[0].vw_treatmentlist.chiefcomplaint),
                    "status":"Started" if(common.getstring(treatment[0].vw_treatmentlist.status) == "") else common.getstring(treatment[0].vw_treatmentlist.status),
                    "doctorid":int(common.getid(treatment[0].vw_treatmentlist.doctorid)),
                    "doctorname":treatment[0].vw_treatmentlist.doctorname,
                    "clinicid":int(common.getid(treatment[0].vw_treatmentlist.clinicid)),
                    "clinicname":treatment[0].vw_treatmentlist.clinicname,
                    "treatmentcost":float(common.getvalue(treatment[0].vw_treatmentlist.treatmentcost)),
                    "description":common.getstring(treatment[0].treatment.description),
                    "plan":  procedurepriceplancode,   #IB:15-Mar-2020 common.getstring(treatment[0].vw_memberpatientlist.procedurepriceplancode),
                    "authorization": False if(len(c) <= 0) else (len(procs)>0 & common.getboolean(c[0].authorizationrequired)),
                    "authorized": True if(common.getstring(treatment[0].vw_treatmentlist.status) == "Authorized") else False,
                    "totaltreatmentcost":float(common.getstring(r["totaltreatmentcost"])),
                    "totalcopay":float(common.getstring(r["totalcopay"])),
                    "totalinspays":float(common.getstring(r["totalinspays"])),
                    "totaldue":float(common.getstring(r["totaldue"])),
                    "totalpaid":float(common.getstring(r["totaltreatmentcost"])) - float(common.getstring(r["totaldue"])),
                    
                    
                }        
                
                #logger.loggerpms2.info("Enter Get Treatment API - C")
            
                proclist = []
                procobj = {}
                uiobj  = {}
               
                for proc in procs:
                    
                    procobj = {
                    
                        "procedurecode":proc.procedurecode,
                        "altshortdescription":common.getstring(proc.altshortdescription),
                        "relgrproc":common.getboolean(proc.relgrproc),
                        "relgrprocdesc":common.getstring(proc.relgrprocdesc),
                        "relgrtransaction":True if(common.getstring(proc.relgrtransactionid) != "") else False,
                        "procedurefee":float(common.getvalue(proc.procedurefee)),
                        "inspays":float(common.getvalue(proc.inspays)),
                        "copay":float(common.getvalue(proc.copay)),
                        "status":common.getstring(proc.status),
                        "tooth":common.getstring(proc.tooth),
                        "quadrant":common.getstring(proc.quadrant),
                        "remarks":common.getstring(proc.remarks)
                    }
                    proclist.append(procobj)   
                
                #logger.loggerpms2.info("Enter Get Treatment API - D")
                treatmentobj["proccount"] = len(procs)
                treatmentobj["proclist"] = proclist
                
                memberid = 0 if (len(treatment) <= 0) else treatment[0].vw_treatmentlist.memberid
                patientid =  0 if (len(treatment) <= 0) else treatment[0].vw_treatmentlist.patientid
                
                pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.hmopatientmember)
                hmopatientmember = False if(len(pats) <= 0) else common.getboolean(pats[0].hmopatientmember)
                #logger.loggerpms2.info("Enter Get Treatment API - E")
                #W, R, H, S
                trtmtnui = {}
                procui = {}
                
                trstatus = common.getstring(treatment[0].vw_treatmentlist.status)
                #logger.loggerpms2.info("Enter Get Treatment API - F")
                if(hmopatientmember):
                    if( trstatus == "Started"):
                        trtmntui = {
                        "chiefcomplaint":"w",
                        "treatmentno":"r",
                        "doctor":"w",
                        "date":"r",
                        "status":"r",
                        "notes":"w",
                        "cost":"r",
                        "copay":"r",
                        "inspays":"r",
                        "addproc":"s"
                        
                        }
                        
                        procui={
                            
                            "proccode":"r",
                            "procdesc":"r",
                            "procfee":"r",
                            "copay":"r",
                            "inspays":"r",
                            "tooth":"w",
                            "quad":"w",
                            "remarks":"w",
                            "more":"s"
                        
                        }
                        
                    else:
                        trtmntui = {
                        "chiefcomplaint":"r",
                        "treatmentno":"r",
                        "doctor":"r",
                        "date":"r",
                        "status":"r",
                        "notes":"w",
                        "cost":"r",
                        "copay":"r",
                        "inspays":"r",
                        "addproc":"h"
                        
                        }
                        
                        procui={
                            
                            "proccode":"r",
                            "procdesc":"r",
                            "procfee":"r",
                            "copay":"r",
                            "inspays":"r",
                            "tooth":"r",
                            "quad":"r",
                            "remarks":"r",
                            "more":"h"
                        
                        }
                        
                        
                        
                    
                    
                else:
                    if( trstatus == "Started"):
                        trtmntui = {
                        "chiefcomplaint":"w",
                        "treatmentno":"r",
                        "doctor":"w",
                        "date":"r",
                        "status":"r",
                        "notes":"w",
                        "cost":"r",
                        "copay":"h",
                        "inspays":"h",
                        "addproc":"s"
                        
                        }
                        
                        procui={
                            
                            "proccode":"r",
                            "procdesc":"r",
                            "procfee":"w",
                            "copay":"h",
                            "inspays":"h",
                            "tooth":"w",
                            "quad":"w",
                            "remarks":"w",
                            "more":"s"
                        
                        }
                        
             
                    else:
                        trtmntui = {
                                      "chiefcomplaint":"w",
                                      "treatmentno":"r",
                                      "doctor":"w",
                                      "date":"r",
                                      "status":"r",
                                      "notes":"w",
                                      "cost":"r",
                                      "copay":"h",
                                      "inspays":"h",
                                      "addproc":"s"
                                      
                                      }
                                      
                        procui={
                            
                            "proccode":"r",
                            "procdesc":"r",
                            "procfee":"w",
                            "copay":"h",
                            "inspays":"h",
                            "tooth":"w",
                            "quad":"w",
                            "remarks":"w",
                            "more":"h"
                        
                        }                
                
                #logger.loggerpms2.info("Enter Get Treatment API - G")
                treatmentobj["treatmentui"] = trtmntui
                treatmentobj["procedureui"] = procui
                treatmentobj["result"] = "success"
                treatmentobj["error_message"] = ""
                treatmentobj["error_code"] = ""
                
            else:
                treatmentobj["result"] = "fail"
                treatmentobj["error_message"] = "Invalid Treatment"
                treatmentobj["error_code"] = ""
            
        except Exception as e:
            treatmentobj1 = {}
            treatmentobj1["result"] = "fail"
            treatmentobj1["error_message"] = "GetTreatment API Exception Error " + str(e)
            treatmentobj["error_code"] = ""
            return json.dumps(treatmentobj1)
            
        
        return json.dumps(treatmentobj)
    
    

    #def newtreatment(self,memberid,patientid,policy_name=""):
    def newtreatment(self,avars):
        
        logger.loggerpms2.info("Enter New Treatment API " + json.dumps(avars))
        
        db = self.db
        providerid = self.providerid        
        auth = current.auth
        treatmentobj = None
        
        #primary clinic id
        clns = db((db.clinic_ref.ref_code == 'PRV') & (db.clinic_ref.ref_id == providerid) & (db.clinic.primary_clinic == True) &(db.clinic.is_active == True)).\
            select(db.clinic_ref.clinic_id, left=db.clinic.on(db.clinic.id==db.clinic_ref.clinic_id))

        prim_clinicid  = 0 if(len(clns) == 0) else clns[0].clinic_id            
        memberid = common.getkeyvalue(avars,"memberid","0")
        patientid = common.getkeyvalue(avars,"patientid","0")
        policy_name = common.getkeyvalue(avars,"policy_name","")
        clinicid = common.getkeyvalue(avars,"clinicid",str(prim_clinicid))
        notes = common.getkeyvalue(avars,"notes","")
        
        try:
            
            #defatul doctor = provider (clinic owner)
            r = db((db.doctor.providerid == providerid) & (db.doctor.practice_owner == True)  & (db.doctor.is_active == True) ).select()
            doctorid = 0 if(len(r) == 0) else int(common.getid(r[0].id))
            
            
         
            
            r = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid)  & \
                   (db.vw_memberpatientlist.primarypatientid == memberid)  & (db.vw_memberpatientlist.is_active== True)).select()
            
            newmember     = False
            freetreatment = True
            patienttype = 'P'
            procedurepriceplancode = 'PREMWALKIN'
            patientname = ""
            fullname = ""
            patientmember = ""
            title = ""
            if(len(r) > 0):
                patientmember = r[0].patientmember
                title = r[0].title
                patientname = r[0].patient   #fname lname : patientmember
                fullname = r[0].fullname     #fullname
                newmember = common.getboolean(r[0].newmember)
                freetreatment = common.getboolean(r[0].freetreatment)
                patienttype = r[0].patienttype
                procedurepriceplancode =  mdputils.getprocedurepriceplancodeformember(db,providerid,memberid,patientid,policy_name) #IB:15-Mar-2020 r[0].procedurepriceplancode        
            
            
            #Create a new TreatmentPlan
            timestr = datetime.datetime.today().strftime("%d-%m-%Y_%H:%M:%S")
            tplan = "TP" + str(patientmember)  + "_" + timestr
            tplanid = db.treatmentplan.insert(
                        treatmentplan = tplan,
                        startdate = datetime.date.today(),
                        provider = providerid,
                        primarypatient = memberid,
                        patient = patientid,
                        pattitle = title,
                        patienttype = patienttype,
                        patientname = fullname,
                        status = 'Started',
                        totaltreatmentcost = 0,
                        totalcopay = 0,
                        totalinspays = 0,
                        totalpaid = 0,
                        totaldue = 0,
                        totalcopaypaid = 0,
                        totalinspaid  = 0,             
                        is_active = True,
                        created_on = common.getISTFormatCurrentLocatTime(),
                        created_by = 1 if(auth.user == None) else auth.user.id,
                        modified_on = common.getISTFormatCurrentLocatTime(),
                        modified_by =1 if(auth.user == None) else auth.user.id
                
                    )
            
            
            #Treatment
            count = db(db.treatment.provider == providerid).count()
            treatment = "TR" + str(patientmember) + str(count).zfill(4)      
            treatmentid = db.treatment.insert(
                treatment = treatment,
                description = notes,
                startdate = datetime.date.today(),
                status ='Started',
                treatmentplan = tplanid,
                provider = providerid,
                dentalprocedure = 0,
                doctor = doctorid,
                clinicid =clinicid,
                quadrant = 0,
                tooth    = 0,
                treatmentcost = 0,
                actualtreatmentcost = 0,  #UCR cost
                copay = 0,
                inspay = 0,
                companypay = 0,
                is_active = True,
                created_on =common.getISTFormatCurrentLocatTime(),
                created_by = 1 if(auth.user == None) else auth.user.id,
                modified_on = common.getISTFormatCurrentLocatTime(),
                modified_by =1 if(auth.user == None) else auth.user.id
            )        
            db.treatmentplan_patient.insert(treatmentplan = tplanid, patientmember = memberid)
            
            #update treatment with new treatment cost
            account.updatetreatmentcostandcopay(db,auth.user,treatmentid)
            #update tplan with new treatment cost
            account.calculatecost(db,tplanid)
            account.calculatecopay(db, tplanid,memberid)
            account.calculateinspays(db,tplanid)
            account.calculatedue(db,tplanid)                
            
            treatmentobj = self.gettreatment(treatmentid)
            
            
        except Exception as e:
            treatmentobj1 = {}
            treatmentobj1["result"] = "fail"
            treatmentobj1["error_message"] = "NewTreatment API Error " + str(e)
            return json.dumps(treatmentobj1)
        
        return treatmentobj
    
    
    #int(common.getid(str(avars["memberid"]))),
    #int(common.getid(str(avars["patientid"]))),

    #int(common.getid(str(avars["clinicid"]))) if "clinicid" in avars else 0)

    
    #def newtreatment_clinic(self,memberid,patientid,clinicid,policy_name=""):
    def newtreatment_clinic(self,avars):            
            #logger.loggerpms2.info("Enter New Treatment Clinic API")
            
            db = self.db
            providerid = self.providerid        
            auth = current.auth
            treatmentobj = None
            try:
                
                memberid = int(common.getid(common.getkeyvalue(avars,"memberid","0")))
                patientid = int(common.getid(common.getkeyvalue(avars,"patientid","0")))                
                clinicid = int(common.getid(common.getkeyvalue(avars,"clinicid","0")))                
                doctorid = int(common.getid(common.getkeyvalue(avars,"doctorid","0")))                
                policy_name = common.getkeyvalue(avars,"policy_name","")
                notes = common.getkeyvalue(avars,"notes","")
                
                #defatul doctor = provider (clinic owner)
                if(doctorid == 0):
                    r = db((db.doctor.providerid == providerid) & (db.doctor.practice_owner == True)  & (db.doctor.is_active == True) ).select()
                    doctorid = 0 if(len(r) == 0) else int(common.getid(r[0].id))
                
                
                if(clinicid == 0):
                    #default clinicid = provider's primary clinic
                    clinic_ref_ids = db((db.clinic_ref.ref_code == 'PRV') & (db.clinic_ref.ref_id == providerid)).select()
                    for clinic_ref_id in clinic_ref_ids:
                        
                        clinic = db(db.clinic.id == clinic_ref_id.clinic_id).select()
                        if clinic[0].primary_clinic == True:
                            clinicid = clinic[0].id
                            break

                    
                             

                r = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid) & \
                       (db.vw_memberpatientlist.primarypatientid == memberid)  & (db.vw_memberpatientlist.is_active== True)).select()
                
                newmember     = False
                freetreatment = True
                patienttype = 'P'
                procedurepriceplancode = 'PREMWALKIN'
                patientname = ""
                fullname = ""
                patientmember = ""
                title = ""
                if(len(r) > 0):
                    patientmember = r[0].patientmember
                    title = r[0].title
                    patientname = r[0].patient   #fname lname : patientmember
                    fullname = r[0].fullname     #fullname
                    newmember = common.getboolean(r[0].newmember)
                    freetreatment = common.getboolean(r[0].freetreatment)
                    patienttype = r[0].patienttype
                    procedurepriceplancode =  mdputils.getprocedurepriceplancodeformember(db,providerid,memberid,patientid,policy_name) #IB:15-Mar-2020 r[0].procedurepriceplancode        
                
                
                #Create a new TreatmentPlan
                timestr = datetime.datetime.today().strftime("%d-%m-%Y_%H:%M:%S")
                tplan = "TP" + str(patientmember)  + "_" + timestr
                tplanid = db.treatmentplan.insert(
                            treatmentplan = tplan,
                            startdate = datetime.date.today(),
                            provider = providerid,
                            primarypatient = memberid,
                            patient = patientid,
                            pattitle = title,
                            patienttype = patienttype,
                            patientname = fullname,
                            status = 'Started',
                            totaltreatmentcost = 0,
                            totalcopay = 0,
                            totalinspays = 0,
                            totalpaid = 0,
                            totaldue = 0,
                            totalcopaypaid = 0,
                            totalinspaid  = 0,             
                            is_active = True,
                            created_on = common.getISTFormatCurrentLocatTime(),
                            created_by = 1 if(auth.user == None) else auth.user.id,
                            modified_on = common.getISTFormatCurrentLocatTime(),
                            modified_by =1 if(auth.user == None) else auth.user.id
                    
                        )
                
                
                #Treatment
                count = db(db.treatment.provider == providerid).count()
                treatment = "TR" + str(patientmember) + str(count).zfill(4)      
                treatmentid = db.treatment.insert(
                    treatment = treatment,
                    description = notes,
                    startdate = datetime.date.today(),
                    status ='Started',
                    treatmentplan = tplanid,
                    provider = providerid,
                    dentalprocedure = 0,
                    doctor = doctorid,
                    clinicid =clinicid,
                    quadrant = 0,
                    tooth    = 0,
                    treatmentcost = 0,
                    actualtreatmentcost = 0,  #UCR cost
                    copay = 0,
                    inspay = 0,
                    companypay = 0,
                    is_active = True,
                    created_on =common.getISTFormatCurrentLocatTime(),
                    created_by = 1 if(auth.user == None) else auth.user.id,
                    modified_on = common.getISTFormatCurrentLocatTime(),
                    modified_by =1 if(auth.user == None) else auth.user.id
                )        
                db.treatmentplan_patient.insert(treatmentplan = tplanid, patientmember = memberid)
                
                #update treatment with new treatment cost
                account.updatetreatmentcostandcopay(db,auth.user,treatmentid)
                #update tplan with new treatment cost
                account.calculatecost(db,tplanid)
                account.calculatecopay(db, tplanid,memberid)
                account.calculateinspays(db,tplanid)
                account.calculatedue(db,tplanid)                
                
                treatmentobj = self.gettreatment(treatmentid)
                
                
            except Exception as e:
                treatmentobj1 = {}
                treatmentobj1["result"] = "fail"
                treatmentobj1["error_message"] = "NewTreatment API Error " + str(e)
                return json.dumps(treatmentobj1)
            
            return treatmentobj    

    def updatetreatment(self,treatmentid,  treatmentdate, chiefcomplaint, doctorid, notes, status,clinicid=0):

        #logger.loggerpms2.info("Enter Update Treatment API")
               
        db = self.db
        providerid = self.providerid        
        auth = current.auth        
        
        
        treatmentobj = None
        try:
            
            
            today = datetime.date.today()
            today_str = common.getstringfromdate(today,"%d/%m/%Y")
            
            dt = None          
            if(treatmentdate != None):
                dt = common.getdt(datetime.datetime.strptime(treatmentdate,"%d/%m/%Y"))
            
            
            t = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
            
            if(len(t) == 1):
                db((db.treatment.id == treatmentid) & (db.treatment.provider == providerid)).update(\
                    chiefcomplaint = chiefcomplaint if (chiefcomplaint != None) else t[0].chiefcomplaint,
                    status=status if (status != None) else t[0].status,\
                    doctor = doctorid if (doctorid != None) else t[0].doctorid,\
                    clinicid=clinicid if (clinicid != 0) else t[0].clinicid,\
                    startdate = dt if (treatmentdate != None) else t[0].startdate,\
                    description = notes if (notes != None) else t[0].description,\
                    modified_on = common.getISTFormatCurrentLocatTime(),
                    modified_by =1 if(auth.user == None) else auth.user.id
                    )
                
                
                
                treatmentobj = self.gettreatment(treatmentid)
            else:
                treatmentobj = {}
                treatmentobj["result"] = "fail"
                treatmentobj["error_message"] = "No Treatment to update " + str(e)
                return json.dumps(treatmentobj1)
            
        except Exception as e:
            treatmentobj1 = {}
            treatmentobj1["result"] = "fail"
            treatmentobj1["error_message"] = "Update Treatment API Error " + str(e)
            return json.dumps(treatmentobj1)
        
        
        return treatmentobj
    
    def treatmentstatus(self):
        
        st = status.TREATMENTSTATUS
        
        
        return  json.dumps(st)
    
    def sendforauthorization(self,appPath,treatmentid):
        
        
        db = self.db
        providerid = self.providerid
        auth = current.auth
         
        sts = status.TREATMENTSTATUS
        jobj = {}
        try:
            #send pre-authorization email
            preauthorized = True
            mail.emailPreAuthorization(db, appPath, treatmentid)   #preauthorized is true irrespective if email is sent successfully or not
            preauthorizeerror = not preauthorized         
            
            #update treatment status
            db(db.treatment.id == treatmentid).update(status = sts[1],
                                                      modified_on = common.getISTFormatCurrentLocatTime(),
                                                      modified_by =1 if(auth.user == None) else auth.user.id
                                                      )
            
            
            #update treatment_procedure status
            db(db.treatment_procedure.treatmentid == treatmentid).update(status = sts[1])
            
            #update treatmentplan status
            tr = db(db.treatment.id == treatmentid).select(db.treatment.treatmentplan)
            db(db.treatmentplan.id == (tr[0].treatmentplan if(len(tr)>0) else 0)).update(status = sts[1],
                                                      modified_on = common.getISTFormatCurrentLocatTime(),
                                                      modified_by =1 if(auth.user == None) else auth.user.id
                                                      )
            
            jobj = {"result":"success","error_message":""}
            
        except Exception as e:
            
            jobj = {"result":"fail","result": "Send for Authorization API exception error - " + str(e)}
        
       
        
        
        
        return json.dumps(jobj)
    