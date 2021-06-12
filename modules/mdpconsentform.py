from gluon import current
import datetime

import json

from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger


class ConsentForm:
    def __init__(self,db):
        self.db = db

    def consentforms(self,avars):
        logger.loggerpms2.info("Enter - Consent Form")
        db = self.db
        auth  = current.auth        
        rsp = {}
        rsp["result"] = "success"
        rsp["error_message"] = ""
        rsp["error_code"] = ""
        
        lst = [
            "Apicoectomies Apicalsurgery Consent Form",
            "Composite Filing Consent Form",
            "Cosmetic Treatment Consent Form",
            "Cosmetic Dentistry Consent Form",
            "Crown Bridge Consent Form",
            "Endodontics Consent Form",
            "Extraction Consent Form",
            "General Consent Form",
            "Orthodontics Treatment Consent Form",
            "Pediatric Dentistry Consent Form",
            "Peridontal Consent Form",
            "Wisdom Teeth Removal Consent Form",
            "Implant Surgery Consent Form"
        ]
        
        rsp["consentforms"] = lst
        
        return json.dumps(rsp)
    
    
    def new_consentform(self,avars):
        logger.loggerpms2.info("Enter New Consent Form")
        
        db = self.db
        auth  = current.auth        
        try:
            providerid = int(common.getid(common.getkeyvalue(avars,"providerid",str(0))))
            memberid = int(common.getid(common.getkeyvalue(avars,"memberid",str(0))))        
            patientid = int(common.getid(common.getkeyvalue(avars,"patientid",str(0))))
            clinicid = int(common.getid(common.getkeyvalue(avars,"clinicid",str(0))))
            doctorid = int(common.getid(common.getkeyvalue(avars,"doctorid",str(0))))
            consentformid = int(common.getid(common.getkeyvalue(avars,"consentformid",str(0))))
            
            consentform_date = common.getdatefromstring(common.getkeyvalue(avars,"consentform_date", common.getstringfromdate(datetime.date.today(),"%d/%m/%Y")),"%d/%m/%Y")
            consentform_code =  common.getkeyvalue(avars,"consentform_code","")
            consentform_name = common.getkeyvalue(avars,"consentform_name","")
            procedurecode = common.getkeyvalue(avars,"procedurecode","")
            procedurename = common.getkeyvalue(avars,"procedurename","")
            patientname = common.getkeyvalue(avars,"patientname","")
            membername = common.getkeyvalue(avars,"membername",patientname)
            status = common.getkeyvalue(avars,"status","Confirmed")
            
            cfsid = db.consentform.insert(
                providerid = int(common.getid(common.getkeyvalue(avars,"providerid",str(0)))),
                memberid = int(common.getid(common.getkeyvalue(avars,"memberid",str(0)))),        
                patientid = int(common.getid(common.getkeyvalue(avars,"patientid",str(0)))),
                clinicid = int(common.getid(common.getkeyvalue(avars,"clinicid",str(0)))),
                doctorid = int(common.getid(common.getkeyvalue(avars,"doctorid",str(0)))),
                consentformid = int(common.getid(common.getkeyvalue(avars,"consentformid",str(0)))),
                
                consentform_date = common.getdatefromstring(common.getkeyvalue(avars,"consentform_date", common.getstringfromdate(datetime.date.today(),"%d/%m/%Y")),"%d/%m/%Y"),
                consentform_code =  common.getkeyvalue(avars,"consentform_code",""),
                consentform_name = common.getkeyvalue(avars,"consentform_name",""),
                procedurecode = common.getkeyvalue(avars,"procedurecode",""),
                procedurename = common.getkeyvalue(avars,"procedurename",""),
                patientname = common.getkeyvalue(avars,"patientname",""),
                membername = common.getkeyvalue(avars,"membername",""),
                status = common.getkeyvalue(avars,"status","")
            )
            
            db(db.consentform.id == cfsid).update(consentformid = cfsid)
            cfsobj = {}
            cfsobj["result"] = "success"
            cfsobj["error_message"] = ""
            cfsobj["error_code"] = ""
            
            cfsobj["cfid"] = str(cfsid)
            return json.dumps(cfsobj)            
        
        
        except Exception as e:
            cfsobj = {}
            cfsobj["result"] = "fail"
            cfsobj["error_message"] = "New Consent Form API Exception Error " + str(e)
            cfsobj["error_code"] = ""
            return json.dumps(cfsobj)            
        
        
    def get_consentform(self,avars):
        logger.loggerpms2.info("Enter Get Consent Form")
        db = self.db
        auth  = current.auth
        
        try:
            cfid = int(common.getid(common.getkeyvalue(avars,"consentformid","0")))
            
            cfs = db((db.consentform.id == cfid) & (db.consentform.is_active == True)).select()
            cfsobj={}
            providerid = 0
            for cf in cfs:
                
                cfsobj = {}
                cfsobj["providerid"] = common.getstring(cf.providerid)
                cfsobj["memberid"] = common.getstring(cf.memberid)
                cfsobj["patientid"] = common.getstring(cf.patientid)
                cfsobj["clinicid"] = common.getstring(cf.clinicid)
                cfsobj["doctorid"] = common.getstring(cf.doctorid)
                cfsobj["consentformid"] = common.getstring(cf.consentformid)
                
                cfsobj["consentform_date"] = common.getstringfromdate(cf.consentform_date,"%d/%m/%Y")
                cfsobj["consentform_code"] =  common.getstring(cf.consentform_code)
                cfsobj["consentform_name"] = common.getstring(cf.consentform_name)
                cfsobj["procedurecode"] = common.getstring(cf.procedurecode)
                cfsobj["procedurename"] = common.getstring(cf.procedurename)
                cfsobj["patientname"] = common.getstring(cf.patientname)
                cfsobj["membername"] = common.getstring(cf.membername)
                cfsobj["status"] = common.getstring(cf.status)          
                break;
            
            providerid = int(cfsobj["providerid"])
            prv = db(db.provider.id == providerid).select()
            cfsobj["providername"] = "" if(len(prv) == 0) else prv[0].pa_providername
            cfsobj["practicename"] = "" if(len(prv) == 0) else prv[0].pa_practicename
            cfsobj["practiceaddress"] = "" if(len(prv) == 0) else prv[0].pa_practiceaddress
            cfsobj["telephone"] = "" if(len(prv) == 0) else prv[0].telephone
            cfsobj["cell"] = "" if(len(prv) == 0) else prv[0].cell
            cfsobj["email"] = "" if(len(prv) == 0) else prv[0].email
            cfsobj["registration"] = "" if(len(prv) == 0) else prv[0].registration            

            cfsobj["result"] = "success"
            cfsobj["error_message"] = ""
            cfsobj["error_code"] = ""
            
        except Exception as e:
            cfsobj = {}
            cfsobj["result"] = "fail"
            cfsobj["error_message"] = "Get Consent Form API Exception Error " + str(e)
            cfsobj["error_code"] = ""
            return json.dumps(cfsobj)            
            
        return json.dumps(cfsobj)
    
    def list_consentform(self,avars):
        
        
        db = self.db
        
        try:
            providerid = int(common.getid(common.getkeyvalue(avars,"providerid",str(0))))
            memberid = int(common.getid(common.getkeyvalue(avars,"memberid",str(0))))        
            patientid = int(common.getid(common.getkeyvalue(avars,"patientid",str(0))))
            clinicid = int(common.getid(common.getkeyvalue(avars,"clinicid",str(0))))
            doctorid = int(common.getid(common.getkeyvalue(avars,"doctorid",str(0))))
            consentformid = int(common.getid(common.getkeyvalue(avars,"consentformid",str(0))))
            
            prv = db(db.provider.id == providerid).select()
            providername = "" if(len(prv) == 0) else prv[0].pa_providername
            practicename = "" if(len(prv) == 0) else prv[0].pa_practicename
            practiceaddress = "" if(len(prv) == 0) else prv[0].pa_practiceaddress
            telephone = "" if(len(prv) == 0) else prv[0].telephone
            cell = "" if(len(prv) == 0) else prv[0].cell
            email = "" if(len(prv) == 0) else prv[0].email
            registration = "" if(len(prv) == 0) else prv[0].registration
            
            #consentform_date = common.getdatefromstring(common.getkeyvalue(avars,"consentform_date",common.getstringfromdate(datetime.date.today(),"%d/%m/%Y")),"%d/%m/%Y")
            
            #consentform_code = common.getkeyvalue(avars,"consentform_code","")
            
            #consentform_code = common.getkeyvalue(avars,"consentform_code","")
            #consentform_code = common.getkeyvalue(avars,"consentform_code","")
            #consentform_code = common.getkeyvalue(avars,"consentform_code","")
            #consentform_code = common.getkeyvalue(avars,"consentform_code","")
            #consentform_code = common.getkeyvalue(avars,"consentform_code","")
            #consentform_code = common.getkeyvalue(avars,"consentform_code","")
    
            query = ((db.consentform.is_active==True) & (db.consentform.providerid == providerid))
            
            query = query if(memberid == 0) else query & (db.consentform.memberid == memberid)
            query = query if(patientid == 0) else query & (db.consentform.patientid == patientid)
            query = query if(clinicid == 0) else query & (db.consentform.clinicid == clinicid)
            query = query if(doctorid == 0) else query & (db.consentform.doctorid == doctorid)
            
            cfs = db(query).select()
            
            cfsobj = {}
            cfslist = []
            
            for cf in cfs:
                cfsobj = {}
                cfsobj["providerid"] = common.getstring(cf.providerid)
                cfsobj["memberid"] = common.getstring(cf.memberid)
                cfsobj["patientid"] = common.getstring(cf.patientid)
                cfsobj["clinicid"] = common.getstring(cf.clinicid)
                cfsobj["doctorid"] = common.getstring(cf.doctorid)
                cfsobj["consentformid"] = common.getstring(cf.consentformid)
                
                cfsobj["consentform_date"] = common.getstringfromdate(cf.consentform_date,"%d/%m/%Y")
                cfsobj["consentform_code"] =  common.getstring(cf.consentform_code)
                cfsobj["consentform_name"] = common.getstring(cf.consentform_name)
                cfsobj["procedurecode"] = common.getstring(cf.procedurecode)
                cfsobj["procedurename"] = common.getstring(cf.procedurename)
                cfsobj["patientname"] = common.getstring(cf.patientname)
                cfsobj["membername"] = common.getstring(cf.membername)
                cfsobj["status"] = common.getstring(cf.status)
                cfslist.append(cfsobj)
                
            rspobj = {}
            
            rspobj["result"] = "success"
            rspobj["error_message"] = ""
            rspobj["error_code"] = ""
            rspobj["providername"] = providername
            rspobj["practicename"] = practicename
            rspobj["practiceaddress"] = practiceaddress
            rspobj["telephone"] = telephone
            rspobj["cell"] = cell
            rspobj["email"] = email
            rspobj["registration"] = registration
            rspobj["cfslist"] = cfslist
            rspobj["count"] = str(len(cfslist))
        except Exception as e:
            cfsobj = {}
            cfsobj["result"] = "fail"
            cfsobj["error_message"] = "Consent Form List API Exception Error " + str(e)
            cfsobj["error_code"] = ""
            return json.dumps(cfsobj)            
        
        
        return json.dumps(rspobj)
        
        
            
            