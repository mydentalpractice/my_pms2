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

datefmt = "%d/%m/%Y"
datetimefmt = "%d/%m/%Y %H:%M:%S"

def serializedatetime(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()    
   

class Procedure:
    
    
    
    def __init__(self,db,providerid):
        self.db = db
        self.providerid = providerid
        return 
    
    # procedure id points to treatment_procedure id
    def gettreatmentprocedure(self,treatmentid,treatmentprocid):
        db = self.db
        providerid = self.providerid
        procobj = {}
        
        try:
            r = db((db.vw_treatmentprocedure.id == treatmentprocid) & (db.vw_treatmentprocedure.treatmentid == treatmentid) & (db.vw_treatmentprocedure.providerid == providerid)).select()
            
            procobj = {
                "procedurecode":r[0].procedurecode,
                "procedurefee":r[0].procedurefee,
                "ucrfee":r[0].ucrfee,
                "copay":r[0].copay,
                "inspays":r[0].inspays,
                "tooth":r[0].tooth,
                "quadrant":r[0].quadrant,
                "remarks":r[0].remarks,
                "status":r[0].status,
                "treatmentid":treatmentid,
                "treatmentprocid":treatmentprocid
            }
            
            #procedure ui
            procui = {}
            treatment = db((db.vw_treatmentlist.id == treatmentid) & (db.vw_treatmentlist.providerid == providerid) & \
                           (db.vw_treatmentlist.is_active == True)).select(db.vw_treatmentlist.memberid,db.vw_treatmentlist.patientid)
            
            if(len(treatment) > 0)                                                               :
                memberid = int(common.getid(treatment[0].memberid))        
                patientid = int(common.getid(treatment[0].patientid))
                pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.hmopatientmember)
                hmopatientmember = False if(len(pats) <= 0) else common.getboolean(pats[0].hmopatientmember)    
            else:
                hmopatientmember = False
            
            if(hmopatientmember == True):
                if(procobj["status"] == "Started"):
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
            
            procobj["procui"] = procui
            procobj["result"] = "success"
            procobj["error_message"] = ""
        except Exception as e:
            procobj["result"] = "fail"
            procobj["error_message"] = "GetTreatmentProcedure API Error - " + str(e)
            
        
        return json.dumps(procobj)
    

    def getnoncompanyprocedures(self,procedurepriceplancode,searchphrase="",page=0,maxcount=0):

        logger.loggerpms2.info("XXX:Enter Get NonCompany Procedures \n"  + procedurepriceplancode + " " + searchphrase + " " + str(page) + " " + str(maxcount))    

        db = self.db
        providerid = self.providerid


        page = page -1
        urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
        items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
        limitby = ((page)*items_per_page,(page+1)*items_per_page)      
        proclist = []
        procobj = {}
        result = "success"
        error_message = ""
        query = ""
        try:
            if((searchphrase == "") | (searchphrase == None)):
                query = (db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode)&\
                    (db.vw_procedurepriceplan_relgr.is_active == True) & (db.vw_procedurepriceplan_relgr.relgrproc ==False)        
            else:
                query = (db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode)&\
                    (db.vw_procedurepriceplan_relgr.shortdescription.like('%' + searchphrase + '%'))&\
                    (db.vw_procedurepriceplan_relgr.is_active == True) & (db.vw_procedurepriceplan_relgr.relgrproc ==False)        

            #logger.loggerpms2.info("Get Non Company Procedures " + str(query))

            if(page >=0 ): 
                procs = db(query).select(\
                    db.vw_procedurepriceplan_relgr.ALL, \
                    orderby=db.vw_procedurepriceplan_relgr.procedurecode,\
                    limitby=limitby\
                )
                #logger.loggerpms2.info("Get Non Compamy Procs" +str(len(procs)))
                if(maxcount == 0):

                    procs1 = db(query).select(\
                        db.vw_procedurepriceplan_relgr.ALL
                    )    
                    maxcount = len(procs1)
            else:
                procs = db(query).select(\
                    db.vw_procedurepriceplan_relgr.ALL,\
                    orderby=db.vw_procedurepriceplan_relgr.procedurecode
                )
                if(maxcount == 0):
                    maxcount = len(procs)

            #logger.loggerpms2.info("Get Non Company Procs A" + str(len(procs)))

            for proc in procs:
                procobj = {
                    "plan":procedurepriceplancode,
                    "procedurecode":proc.vw_procedurepriceplan_relgr.procedurecode,
                    "altshortdescription":common.getstring(proc.vw_procedurepriceplan_relgr.altshortdescription),
                    "procedurefee":float(common.getvalue(proc.vw_procedurepriceplan_relgr.procedurefee)),
                    "inspays":float(common.getvalue(proc.vw_procedurepriceplan_relgr.inspays)),
                    "copay":float(common.getvalue(proc.vw_procedurepriceplan_relgr.copay))
                }        
                proclist.append(procobj) 
                result = 'success'
                error_message = ""

        except Exception as e:
            result = "fail"
            error_message = "Get Non Company Procedure API:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
            logger.loggerpms2.info(error_message)

        xcount = ((page+1) * items_per_page) - (items_per_page - len(procs)) 

        bnext = True
        bprev = True

        #first page
        if((page+1) == 1):
            bnext = True
            bprev = False

        #last page
        if(len(procs) < items_per_page):
            bnext = False
            bprev = True  

        return json.dumps({"result":result,"error_message":error_message,"count":len(procs),"page":page+1,"proclist":proclist,"runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev})
    
    def getcompanyprocedures(self,procedurepriceplancode,searchphrase="",page=0,maxcount=0):

        logger.loggerpms2.info("XXX:Enter Get Company Procedures \n"  + procedurepriceplancode + " " + searchphrase + " " + str(page) + " " + str(maxcount))    

        db = self.db
        providerid = self.providerid


        page = page -1
        urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
        items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
        limitby = ((page)*items_per_page,(page+1)*items_per_page)      
        proclist = []
        procobj = {}
        result = "success"
        error_message = ""
        query = ""
        try:
            if((searchphrase == "") | (searchphrase == None)):
                query = (db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode)&\
                    (db.vw_procedurepriceplan_relgr.is_active == True) & (db.vw_procedurepriceplan_relgr.relgrproc ==True)        
            else:
                query = (db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode)&\
                    (db.vw_procedurepriceplan_relgr.shortdescription.like('%' + searchphrase + '%'))&\
                    (db.vw_procedurepriceplan_relgr.is_active == True) & (db.vw_procedurepriceplan_relgr.relgrproc ==True)        

            #logger.loggerpms2.info("Get Company Procedures " + str(query))

            if(page >=0 ): 
                procs = db(query).select(\
                    db.vw_procedurepriceplan_relgr.ALL, \
                    orderby=db.vw_procedurepriceplan_relgr.procedurecode,\
                    limitby=limitby\
                )
                #logger.loggerpms2.info("Get Compamy Procs" +str(len(procs)))
                if(maxcount == 0):

                    procs1 = db(query).select(\
                        db.vw_procedurepriceplan_relgr.ALL
                    )    
                    maxcount = len(procs1)
            else:
                procs = db(query).select(\
                    db.vw_procedurepriceplan_relgr.ALL,\
                    orderby=db.vw_procedurepriceplan_relgr.procedurecode
                )
                if(maxcount == 0):
                    maxcount = len(procs)

            #logger.loggerpms2.info("Get Company Procs A" + str(len(procs)))

            for proc in procs:
                procobj = {
                    "plan":procedurepriceplancode,
                    "procedurecode":proc.procedurecode,
                    "altshortdescription":common.getstring(proc.altshortdescription),
                    "procedurefee":float(common.getvalue(proc.relgrprocfee)),
                    "inspays":float(common.getvalue(proc.relgrinspays)),
                    "copay":float(common.getvalue(proc.relgrcopay))
                }        
                proclist.append(procobj) 
                result = 'success'
                error_message = ""

        except Exception as e:
            result = "fail"
            error_message = "Get Company Procedure API:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")",
            logger.loggerpms2.info(error_message)

        xcount = ((page+1) * items_per_page) - (items_per_page - len(procs)) 

        bnext = True
        bprev = True

        #first page
        if((page+1) == 1):
            bnext = True
            bprev = False

        #last page
        if(len(procs) < items_per_page):
            bnext = False
            bprev = True  

        return json.dumps({"result":result,"error_message":error_message,"count":len(procs),"page":page+1,"proclist":proclist,"runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev})
    
    
        
    #this APi adds a new procedure to the treatment
    def addcompanyProcedureToTreatment(self,treatmentid,procedurepriceplancode, procedurecode,
                                      tooth, quadrant,remarks):


        logger.loggerpms2.info(">>Add Company Procedure to Treatment\n " + str(treatmentid) + " " + procedurepriceplancode + " " + procedurecode)

        db = self.db
        providerid = self.providerid
        auth = current.auth
        jsonresp = {}

        try:
            procs = db((db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode) & \
                       (db.vw_procedurepriceplan_relgr.procedurecode == procedurecode)).select()

            procedureid = 0
            ucrfee = 0
            procedurefee = 0
            inspays = 0
            copay = 0
            companypays = 0
            relgrproc = False
            memberid = 0

            service_id = ""
            service_name = ""
            service_category = ""

            if(len(procs)>0):
                ucrfee = float(common.getvalue(procs[0].ucrfee))
                procedurefee = float(common.getvalue(procs[0].relgrprocfee))
                if(procedurefee == 0):
                    procedurefee = ucrfee
                copay = float(common.getvalue(procs[0].relgrcopay))
                inspays = float(common.getvalue(procs[0].relgrinspays))
                companypays = float(common.getvalue(procs[0].companypays))
                procedureid = int(common.getid(procs[0].id))    
                relgrproc = bool(common.getboolean(procs[0].relgrproc))
                service_id = int(common.getid(procs[0].service_id))
                service_name = procs[0].service_name
                service_category = procs[0].service_category


            sub_service_id = ""
            treatment_code = ""
            treatment_name = ""
            procedurecode = ""

            t = db(db.vw_treatmentlist.id == treatmentid).\
                select(db.vw_treatmentlist.tplanid,db.vw_treatmentlist.startdate, db.vw_treatmentlist.memberid)

            procid = db.treatment_procedure.insert(treatmentid = treatmentid, dentalprocedure = procedureid,status="Started",\
                                                   treatmentdate=t[0].startdate if(len(t)>0) else common.getISTFormatCurrentLocatTime(),\
                                                   ucr = ucrfee, procedurefee=procedurefee, copay=copay,inspays=inspays,companypays=companypays,\
                                                   tooth=tooth,quadrant=quadrant,remarks=remarks,authorized=False,service_id = service_id,\
                                                   relgrproc=relgrproc,relgrtransactionid = 0,relgrtransactionamt=inspays) 


            tplanid = int(common.getid(t[0].tplanid)) if(len(t) > 0) else 0
            memberid = int(common.getid(t[0].memberid)) if(len(t) > 0) else 0
            #update treatment with new treatment cost
            account.updatetreatmentcostandcopay(db,auth.user,treatmentid)
            #update tplan with new treatment cost
            account.calculatecost(db,tplanid)
            account.calculatecopay(db, tplanid,memberid)
            account.calculateinspays(db,tplanid)
            account.calculatedue(db,tplanid)  
            jsonresp["treatmentprocid"] = procid
            jsonresp["result"] =  "success"
            jsonresp["error_message"] = ""
            

        except Exception as e:
            mssg = "addcompanyProcedureToTreatment Exception error:\n" + errormessage(db,"MDP100")  + "\n(" + str(e) + ")"
            logger.loggerpms2.info(mssg)
            jsonresp = {
                "result":"fail",
                "error_message":mssg,
                "response_status":"",
                "response_message":"",
                "error_code":"MDP100",
            }

        rsp = json.dumps(jsonresp)
        logger.loggerpms2.info("Exit Add Company Procedure To Treatment " + rsp)
        return rsp      
    
    
    
    #returns a list of dental procedures matching the searchphrase for a specific plan
    #search phrase can be 'procedure code', 'keywords', 'short description'
    def getnonreligareprocedures(self,page,treatmentid, searchphrase):
        
        db = self.db
        providerid = self.providerid
        
        page = page -1
            
        urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
        items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
        limitby = ((page)*items_per_page,(page+1)*items_per_page)             
        retobj = {}
        try:
            rows = db((db.vw_treatmentlist.id == treatmentid) & (db.vw_treatmentlist.is_active == True)).\
                select(db.vw_treatmentlist.memberid,db.vw_treatmentlist.patientid)
            patientid = int(common.getid(rows[0].patientid)) if(len(rows) == 1) else 0
            memberid = int(common.getid(rows[0].memberid)) if(len(rows) == 1) else 0
            
            
            rows = db((db.vw_memberpatientlist.patientid ==patientid)&(db.vw_memberpatientlist.primarypatientid == memberid)).\
                select(db.vw_memberpatientlist.hmoplan)
        
            
            procedurepriceplancode = rows[0].hmoplan.procedurepriceplancode if(len(rows) > 0) else 'PREMWALKIN' 
               
            
            if((searchphrase == "") | (searchphrase == None)):
                query = ( \
                         (db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode) &\
                         (db.vw_procedurepriceplan.relgrproc == False) & (db.vw_procedurepriceplan.is_active == True))
            else:
                query=  ( \
                         (db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode) &\
                         (db.vw_procedurepriceplan.shortdescription.like('%' + searchphrase + '%'))\
                         & (db.vw_procedurepriceplan.relgrproc == False) & (db.vw_procedurepriceplan.is_active == True))
        
            if(page >= 0):
                procs = db(query).select(db.vw_procedurepriceplan.procedurecode,db.vw_procedurepriceplan.altshortdescription,\
                                              db.vw_procedurepriceplan.procedurefee,db.vw_procedurepriceplan.inspays,\
                                              db.vw_procedurepriceplan.copay,limitby=limitby,orderby=db.vw_procedurepriceplan.procedurecode
                                              )
            else:
                procs = db(query).select(db.vw_procedurepriceplan.procedurecode,db.vw_procedurepriceplan.altshortdescription,\
                                              db.vw_procedurepriceplan.procedurefee,db.vw_procedurepriceplan.inspays,\
                                              db.vw_procedurepriceplan.copay,db.vw_procedurepriceplan.procedurecode
                                              )        
            proclist = []
            procobj = {}        
            
            for proc in procs:
                procobj = {
                    "plan":procedurepriceplancode,
                    "procedurecode":proc.procedurecode,
                    "altshortdescription":common.getstring(proc.altshortdescription),
                    "procedurefee":float(common.getvalue(proc.procedurefee)),
                    "inspays":float(common.getvalue(proc.inspays)),
                    "copay":float(common.getvalue(proc.copay)),
                }
                proclist.append(procobj)          
            retobj = {"count":len(procs), "proclist":proclist}
        except Exception as e:
            retobj1 = {}
            retobj1["result"] = "fail"
            retobj1["error_message"] = "Get Non Religare Procedure API Exception Error " + str(e)
            json.dumps(retobj1)
            
    
        
        return json.dumps(retobj)    
    
    def getprocedure(self, avars):
        
        logger.loggerpms2.info("Enter getprocedure " + json.dumps(avars))
        db = self.db
        providerid = self.providerid
        
        procedurecode = common.getkeyvalue(avars,"procedurecode","")

        procs = db((db.dentalprocedure.dentalprocedure==procedurecode)& (db.dentalprocedure.is_active == True)).select()
        
        rspobj = {}
        
        rspobj["result"] = "success"
        rspobj["error_message"] = ""
        rspobj["error_code"] = ""   
        rspobj["procedureid"] = str(0) if (len(procs) == 0) else procs[0].id
        rspobj["procedurecode"] = "" if  (len(procs) == 0) else procs[0].dentalprocedure
        rspobj["procedurename"] = "" if (len(procs) == 0) else procs[0].shortdescription
        
        rsp = json.dumps(rspobj)
        logger.loggerpms2.info("Exit Get Procedure " + rsp)
        return rsp
    
    #returns a list of dental procedures matching the searchphrase for a specific plan
    #search phrase can be 'procedure code', 'keywords', 'short description'
    def getprocedures(self,treatmentid, searchphrase, page=0, maxcount=0):
        
        logger.loggerpms2.info("Enter getprocedures API " + str(treatmentid) + " " + searchphrase)
        db = self.db
        providerid = self.providerid
        
        page = page -1
            
        urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
        items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
        limitby = ((page)*items_per_page,(page+1)*items_per_page)             

        
        rows = db((db.vw_treatmentlist.id == treatmentid) & (db.vw_treatmentlist.is_active == True)).\
            select(db.vw_treatmentlist.memberid,db.vw_treatmentlist.patientid)
        patientid = int(common.getid(rows[0].patientid)) if(len(rows) == 1) else 0
        memberid = int(common.getid(rows[0].memberid)) if(len(rows) == 1) else 0
        
        
        rows = db((db.vw_memberpatientlist.patientid ==patientid)&(db.vw_memberpatientlist.primarypatientid == memberid)).\
            select(db.vw_memberpatientlist.hmoplan)

        
        procedurepriceplancode = rows[0].hmoplan.procedurepriceplancode if(len(rows) > 0) else 'PREMWALKIN' 
           
        
        if((searchphrase == "") | (searchphrase == None)):
            query = ( \
                     (db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode) &\
                     (db.vw_procedurepriceplan.is_active == True))
        else:
            query=  ( \
                     (db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode) &\
                     (db.vw_procedurepriceplan.shortdescription.like('%' + searchphrase + '%'))\
                     & (db.vw_procedurepriceplan.is_active == True))

        if(page >= 0):
            procs = db(query).select(db.vw_procedurepriceplan.procedurecode,db.vw_procedurepriceplan.altshortdescription,\
                                          db.vw_procedurepriceplan.procedurefee,db.vw_procedurepriceplan.inspays,\
                                          db.vw_procedurepriceplan.copay,limitby=limitby,orderby=db.vw_procedurepriceplan.procedurecode
                                          )
            if(maxcount == 0):
                maxcount = db(query).count()            
        else:
            procs = db(query).select(db.vw_procedurepriceplan.procedurecode,db.vw_procedurepriceplan.altshortdescription,\
                                          db.vw_procedurepriceplan.procedurefee,db.vw_procedurepriceplan.inspays,\
                                          db.vw_procedurepriceplan.copay,db.vw_procedurepriceplan.procedurecode,\
                                          orderby=db.vw_procedurepriceplan.procedurecode
                                          )        
            if(maxcount == 0):
                maxcount = db(query).count()            

        
        
        proclist = []
        procobj = {}        
        
        for proc in procs:
            procobj = {
                "plan":procedurepriceplancode,
                "procedurecode":proc.procedurecode,
                "altshortdescription":common.getstring(proc.altshortdescription),
                "procedurefee":float(common.getvalue(proc.procedurefee)),
                "inspays":float(common.getvalue(proc.inspays)),
                "copay":float(common.getvalue(proc.copay)),
            }
            proclist.append(procobj)          

 
        xcount = ((page+1) * items_per_page) - (items_per_page - len(procs)) 
 
        bnext = True
        bprev = True
 
        #first page
        if((page+1) == 1):
            bnext = True
            bprev = False
        
        #last page
        if(len(procs) < items_per_page):
            bnext = False
            bprev = True  
        
        obj1= {"count":len(procs), "proclist":proclist,"page":page+1,"runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev}
        rsp = json.dumps(obj1)
        logger.loggerpms2.info("Exit 'getprocedures " + rsp)
        return rsp
    
    #returns a list of procedures in the selected treatment
    def gettreatmentprocedures(self,treatmentid):
        
        db = self.db
        providerid = self.providerid
        
        procs = db((db.vw_treatmentprocedure.treatmentid == treatmentid) & (db.vw_treatmentprocedure.is_active == True)).select()
        
        proclist = []
        procobj = {}
        
        for proc in procs:
            procobj = {
                "treatmentid":treatmentid,
                "trtmntprocid":int(common.getid(proc.id)),
                "procedurecode":proc.procedurecode,
                "altshortdescription":common.getstring(proc.altshortdescription),
                "ucr":float(common.getvalue(proc.ucrfee)),
                "procedurefee":float(common.getvalue(proc.procedurefee)),
                "inspays":float(common.getvalue(proc.inspays)),
                "copay":float(common.getvalue(proc.copay)),
                "relgrproc": common.getboolean(proc.relgrproc),
                "relgrprocdesc":common.getstring(proc.relgrprocdesc),
                "status":common.getboolean(proc.status),
                "treatment":common.getstring(proc.treatment),
                "remarks":common.getstring(proc.remarks),
                "authorized":common.getboolean(proc.authorized),
                "treatmentdate"  : (proc.treatmentdate).strftime("%d/%m/%Y")
            }
            proclist.append(procobj)          

        return json.dumps({"count":len(procs), "proclist":proclist})
    
    #this procedure adds a new procedure to the treatment
    def addproceduretotreatment(self, procedurecode, treatmentid, plan, tooth, quadrant,remarks):
        logger.loggerpms2.info("Enter Add Procedure To Treatment - " + str(procedurecode) + " " + str(treatmentid) + " " + plan)
        db = self.db
        providerid = self.providerid
        auth = current.auth
        jsonObj = {}
        try:
            procs = db((db.vw_procedurepriceplan.procedurepriceplancode == plan) & \
                       (db.vw_procedurepriceplan.procedurecode == procedurecode)).select()
            
            procedureid = 0
            ucrfee = 0
            procedurefee = 0
            copay = 0
            companypays = 0
            relgrproc = False
            memberid = 0
            
            if(len(procs)>0):
                    ucrfee = float(common.getvalue(procs[0].ucrfee))
                    procedurefee = float(common.getvalue(procs[0].procedurefee))
                    if(procedurefee == 0):
                        procedurefee = ucrfee
                    copay = float(common.getvalue(procs[0].copay))
                    inspays = float(common.getvalue(procs[0].inspays))
                    companypays = float(common.getvalue(procs[0].companypays))
                    procedureid = int(common.getid(procs[0].id))    
                    relgrproc = bool(common.getboolean(procs[0].relgrproc))
    
            #t = db(db.treatment.id == treatmentid).select(db.treatment.startdate,db.treatment.treatmentplan)
            t = db(db.vw_treatmentlist.id == treatmentid).select(db.vw_treatmentlist.tplanid,db.vw_treatmentlist.startdate, db.vw_treatmentlist.memberid)
            
            procid = db.treatment_procedure.insert(treatmentid = treatmentid, dentalprocedure = procedureid,status="Started",\
                                                   treatmentdate=t[0].startdate if(len(t)>0) else common.getISTFormatCurrentLocatTime(),\
                                                 ucr = ucrfee, procedurefee=procedurefee, copay=copay,inspays=inspays,companypays=companypays,\
                                                 tooth=tooth,quadrant=quadrant,remarks=remarks,authorized=False,relgrproc=relgrproc) 
    
            
            tplanid = int(common.getid(t[0].tplanid)) if(len(t) > 0) else 0
            memberid = int(common.getid(t[0].memberid)) if(len(t) > 0) else 0
            #update treatment with new treatment cost
            account.updatetreatmentcostandcopay(db,auth.user,treatmentid)
            #update tplan with new treatment cost
            account.calculatecost(db,tplanid)
            account.calculatecopay(db, tplanid,memberid)
            account.calculateinspays(db,tplanid)
            account.calculatedue(db,tplanid)            
    
            jsonObj = {\
                "result" : "success" if(procid > 0) else "fail",
                "error_message" : "" if(procid > 0) else "Invalid Procedure",
                "treatmentprocid":procid
            }
        
        except Exception as e:
            retobj1 = {}
            retobj1["result"] = "fail"
            retobj1["error_message"] = "Add Procedure to Treatment API Exception Error " + str(e)
            json.dumps(retobj1)
    
        rsp = json.dumps(jsonObj)
        logger.loggerpms2.info("Exit Add Procedure To Treatment " + rsp)
        return rsp
    
    #this procedure adds a new procedure to the treatment
    def addSPLproceduretotreatment(self, procedurecode, treatmentid, plan, tooth, quadrant,remarks):
        logger.loggerpms2.info("Enter addSPLproceduretotreatment " + procedurecode)
        db = self.db
        providerid = self.providerid
        auth = current.auth
        jsonObj = {}
        try:
            procs = db((db.vw_procedurepriceplan.procedurepriceplancode == plan) & \
                       (db.vw_procedurepriceplan.procedurecode == procedurecode)).select()
            
            procedureid = 0
            ucrfee = 0
            procedurefee = 0
            copay = 0
            companypays = 0
            relgrproc = False
            memberid = 0
            
            if(len(procs)>0):
                    ucrfee = float(common.getvalue(procs[0].ucrfee))
                    procedurefee = float(common.getvalue(procs[0].procedurefee))
                    if(procedurefee == 0):
                        procedurefee = ucrfee
                    copay = float(common.getvalue(procs[0].copay))
                    inspays = float(common.getvalue(procs[0].inspays))
                    companypays = float(common.getvalue(procs[0].companypays))
                    procedureid = int(common.getid(procs[0].id))    
                    relgrproc = bool(common.getboolean(procs[0].relgrproc))
    
            #t = db(db.treatment.id == treatmentid).select(db.treatment.startdate,db.treatment.treatmentplan)
            t = db(db.vw_treatmentlist.id == treatmentid).select(db.vw_treatmentlist.tplanid,db.vw_treatmentlist.startdate, db.vw_treatmentlist.memberid)
            
            procid = db.treatment_procedure.insert(treatmentid = treatmentid, dentalprocedure = procedureid,status="Started",\
                                                   treatmentdate=t[0].startdate if(len(t)>0) else common.getISTFormatCurrentLocatTime(),\
                                                 ucr = ucrfee, procedurefee=procedurefee, copay=copay,inspays=inspays,companypays=companypays,\
                                                 tooth=tooth,quadrant=quadrant,remarks=remarks,authorized=False,relgrproc=relgrproc) 
    
            db.commit()
            
            tplanid = int(common.getid(t[0].tplanid)) if(len(t) > 0) else 0
            memberid = int(common.getid(t[0].memberid)) if(len(t) > 0) else 0
            
            booking_amount = account.get_booking_amount(db, treatmentid)
            tax = account.get_tax_amount(db, copay)
            #logger.loggerpms2.info("Booking & Tax amount = " + str(booking_amount) + " " + json.dumps(tax))
            if(booking_amount > 0):
                #db(db.treatmentplan.id == tplanid).update(totalpaid = booking_amount)
               
                db(db.treatment_procedure.id == procid).update(copay = float(common.getvalue(tax["posttaxamount"])))
                db.commit()                
                
            #update treatment with new treatment cost
            account.updatetreatmentcostandcopay(db,auth.user,treatmentid)
            
            #update tplan with new treatment cost
            #account.calculatecost(db,tplanid)
            #account.calculatecopay(db, tplanid,memberid)
            #account.calculateinspays(db,tplanid)
            #account.calculatedue(db,tplanid)            
    
            jsonObj = {\
                "result" : "success" if(procid > 0) else "fail",
                "error_message" : "" if(procid > 0) else "Invalid Procedure",
                "treatmentprocid":procid,
                "originalcopay":copay+booking_amount,
                "copay":common.getvalue(tax["posttaxamount"]),
                "booking_amount":booking_amount,
                "tax":common.getvalue(tax["tax"])
                
            }
        
        except Exception as e:
            retobj1 = {}
            retobj1["result"] = "fail"
            retobj1["error_message"] = "Add Procedure to Treatment API Exception Error " + str(e)
            logger.loggerpms2.info("addSPLproceduretotreatment Exceptionerror " + json.dumps(retobj1))
            json.dumps(retobj1)
            
        rsp = json.dumps(jsonObj)
        logger.loggerpms2.info("Exit addSPLprocedureToTreatment " + rsp)
        return rsp
    

    #this procedure updates a treatment procedure record
    def updatetreatmentprocedure(self,treatmentid,treatmentprocid,procedurefee,copay,inspays,tooth,quadrant,remarks):
        
        db = self.db
        
        jsonObj = {}
        
        try:
            xid = db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.id == treatmentprocid)).update(\
                quadrant = quadrant,
                tooth = tooth,        
                procedurefee = procedurefee,
                copay=copay,
                inspays=inspays,
                remarks = remarks
            )
    
            jsonObj = {
            
                "result" : "success" if(xid > 0) else "fail",
                "error_message":"" if(xid > 0) else "Error in updating treatment procedure",
                "treatmentid":treatmentid,
                "treatmentprocid":treatmentprocid
                
                
            }
        except Exception as e:
            retobj1 = {}
            retobj1["result"] = "fail"
            retobj1["error_message"] = "Update Treatment Procedure API Exception Error " + str(e)
            json.dumps(retobj1)
        
        return json.dumps(jsonObj)
    
   
    #this method 'cancels' the procedure for this treatment
    def completetreatmentprocedure(self,treatmentid,treatmentprocid ):
        
        db = self.db 
        jsonObj = {}
        
        try:
            xid = db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.id == treatmentprocid)).update(\
                status = 'Completed'
            )
    
            jsonObj = {
            
                "result" : "success" if(xid >= 0) else "fail",
                "error_message":"" if(xid >= 0) else "Error in completing a treatment procedure",
                "treatmentid":treatmentid,
                "treatmentprocid":treatmentprocid
                
            }
        except Exception as e:
            retobj1 = {}
            retobj1["result"] = "fail"
            retobj1["error_message"] = "Complete Treatment Procedure API Exception Error " + str(e)
            json.dumps(retobj1)
       
        return json.dumps(jsonObj)
        
        
    #this method 'cancels' the procedure for this treatment
    def canceltreatmentprocedure(self,treatmentid,treatmentprocid ):
        db = self.db
        
        jsonObj = {}
        
        try:
            xid = db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.id == treatmentprocid)).update(\
                is_active = False,
                status = 'Cancelled'
            )
    
            jsonObj = {
            
                "result" : "success" if(xid >= 0) else "fail",
                "error_message":"" if(xid >= 0) else "Error cancelling a treatment procedure",
                "treatmentid":treatmentid,
                "treatmentprocid":treatmentprocid
                
            }
            r = db(db.treatment.id == treatmentid).select(db.treatment.treatmentplan)
            account.updatetreatmentcostandcopay(db,None,treatmentid)
        except Exception as e:
            retobj1 = {}
            retobj1["result"] = "fail"
            retobj1["error_message"] = "Cancelling Treatment Procedure API Exception Error " + str(e)
            json.dumps(retobj1)
        
        return json.dumps(jsonObj)
        
    #this method sets status = 'sent for authorization' the procedure for this treatment
    def sentforauthorization(self,treatmentid,treatmentprocid ):
        
        db = self.db
        providerid = self.providerid
        
        
        jsonObj = {}
        
        try:
            xid = db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.dentalprocedure == procedurecode)).update(\
               
                status = 'Sent for Authorization'
            )
    
            jsonObj = {
            
                "result" : "success" if(xid > 0) else "fail",
                "error_message":"" if(xid >= 0) else "Error in send for authorization treatment procedure",                
                "treatmentprocid":xid
                
            }
        except Exception as e:
            retobj1 = {}
            retobj1["result"] = "fail"
            retobj1["error_message"] = "Send for Authorization Treatment Procedure API Exception Error " + str(e)
            json.dumps(retobj1)
        
        return json.dumps(jsonObj)
        