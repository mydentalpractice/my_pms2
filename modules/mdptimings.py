from gluon import current
import datetime

import json
import os
import tempfile

import base64
from base64 import decodestring



from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger



#Field('','date'),
#ref codes
#DOC = Timing for Doctor,CLN = Timing for Clinic,PRV = Timing for Provider,NON=Timing for Non-Medial Staff
#OFF= Timing for MDP Office,
#SLS = Sales Person, MKT = Marketing Person, EMP = Non-Medial Clinic Employee
   
class OPS_Timing:
    def __init__(self,db):
        self.db = db
        
    def get_ops_timing(self,avars):
        auth  = current.auth
        db = self.db
        
        try:
            opsobj = {}
            ops_timing_id = int(common.getid(avars["ops_timing_id"])) if "ops_timing_id" in avars else 0 
    
            ops = db((db.ops_timing.id == ops_timing_id) & (db.ops_timing.is_active == True)).select()
            
            for op in ops:
                opsobj = {
                    "ref_code":op.ops_timing_ref.ref_code,
                    "ref_id":op.ops_timing_ref.ref_id,
                    "calendar_date":common.getstringfromdate(op.ps_timing.calendar_date, "%d/%m/%Y"),
                    "open_time":common.getstringfromtime(op.ops_timing.open_time, "%I:%M %p"),
                    "close_time":common.getstringfromtime(op.ops_timing.close_time, "%I:%M %p"),
                    "day_of_week":op.ops_timing.day_of_week,
                    "is_lunch":"True" if op.ops_timing.is_lunch == True else "False",
                    "is_holiday":"True" if op.ops_timing.is_holiday == True else "False",
                    "is_saturday":"True" if op.ops_timing.is_saturday == True else "False",
                    "is_sunday":"True" if op.ops_timing.is_sunday == True else "False",
                }            
            
            opsobj["result"] = "success"
            opsobj["error_message"] = ""
            opsobj["error_code"] = ""
            
        except Exception as e:
            mssg = "Delete OPS Timing Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)            
        
        return json.dumps(opsobj) 


    def update_ops_timing(self,avars):
        auth  = current.auth
        db = self.db
        
        try:
            rspobj = {}
            ops_timing_id = int(common.getid(avars["ops_timing_id"])) if "ops_timing_id" in avars else 0 
            
            calendar_date = common.getdatefromstring(common.getkeyvalue(avars, "calendar_date", common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")), "%d/%m/%Y")
            day_of_week = common.getkeyvalue(avars,"day_of_week","mon")
            
            strtime = common.getkeyvalue(avars,"open_time","09:00 AM")
            open_time = common.gettimefromstring(strtime, "%I:%M %p")
            
            strtime = common.getkeyvalue(avars,"close_time","06:00 PM")
            close_time = common.gettimefromstring(strtime, "%I:%M %p")
                                                                                                                      
            is_lunch = common.getboolean(common.getkeyvalue(avars,"is_lunch","True"))
            is_holiday = common.getboolean(common.getkeyvalue(avars,"is_holiday","True"))
            is_saturday = common.getboolean(common.getkeyvalue(avars,"is_saturday","True"))
            is_sunday = common.getboolean(common.getkeyvalue(avars,"is_sunday","True"))            
 
            db(db.ops_timing.id == ops_timing_id).update(\
                calendar_date = calendar_date,
                day_of_week =day_of_week,
                open_time = open_time,
                close_time = close_time,
                is_lunch = is_lunch,
                is_holiday = is_holiday,
                is_saturday = is_saturday,
                is_sunday = is_sunday,
                modified_on=common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id
                )
            
            rspobj = {
                
                'ops_timing_id': ops_timing_id,
                'result' : 'success',
                "error_code":"",
                "error_message":""
                       }                  
            
        except Exception as e:
            mssg = "Delete OPS Timing Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)            
        
        return json.dumps(rspobj) 
    
    def delete_ops_timng(self,avars):
        auth  = current.auth
        db = self.db
        
        try:
           
            ops_timing_id = int(common.getid(avars["ops_timing_id"])) if "ops_timing_id" in avars else 0 
            
            db(db.ops_timing.id == ops_timing_id).update(
                is_active = False,
                modified_on=common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id
        
            )
        
            rspobj = {
                'ops_timing_id': ops_timing_id,
                'result' : 'success',
                "error_code":"",
                "error_message":""
            }               

            
        except Exception as e:
                mssg = "Delete OPS Timing Exception:\n" + str(e)
                logger.loggerpms2.info(mssg)      
                excpobj = {}
                excpobj["result"] = "fail"
                excpobj["error_code"] = "MDP100"
                excpobj["error_message"] = mssg
                return json.dumps(excpobj)
    
        return json.dumps(rspobj) 
    
    def list_ops_timing(self,avars):
        auth  = current.auth
        db = self.db
        
        try:
            
            ref_code = avars["ref_code"] if "ref_code" in avars else ""
            ref_id = int(common.getid(avars["ref_id"])) if "ref_id" in avars else 0            
            
            opslist = []
            opsobj = {}
            
            rspobj = {}
            
            ops = None
            if(ref_code == ""):
                if(ref_id == 0):
                    ops = db((db.ops_timing.is_active == True)).select(db.ops_timing.ALL,db.ops_timing_ref.ALL,\
                                                                                        left=db.ops_timing.on((db.ops_timing.id == db.ops_timing_ref.ref_id)),limitby=limitby)
                else:
                    ops = db((db.ops_timing_ref.ref_id == ref_id) &  (db.ops_timing.is_active == True)).select(db.ops_timing.ALL,db.ops_timing_ref.ALL,\
                                                                                        left=db.ops_timing.on((db.ops_timing.id == db.ops_timing_ref.ref_id)),limitby=limitby)
                    
            else:
                if(ref_id == 0):
                    ops = db((db.ops_timing_ref.ref_code==ref_code)&  (db.ops_timing.is_active == True)).select(db.ops_timing.ALL,db.ops_timing_ref.ALL,\
                                                                                        left=db.ops_timing.on((db.ops_timing.id == db.ops_timing_ref.ref_id)),limitby=limitby)
                else:
                    ops = db((db.ops_timing_ref.ref_code==ref_code)&(db.ops_timing_ref.ref_id == ref_id) &  (db.ops_timing.is_active == True)).select(db.ops_timing.ALL,db.ops_timing_ref.ALL,\
                                                                                        left=db.ops_timing.on((db.ops_timing.id == db.ops_timing_ref.ref_id)),limitby=limitby)
                
            
           
            for op in ops:
                opsobj = {
                    "ref_code":op.ops_timing_ref.ref_code,
                    "ref_id":op.ops_timing_ref.ref_id,
                    "calendar_date":common.getstringfromdate(op.ps_timing.calendar_date, "%d/%m/%Y"),
                    "open_time":common.getstringfromtime(op.ops_timing.open_time, "%I:%M %p"),
                    "close_time":common.getstringfromtime(op.ops_timing.close_time, "%I:%M %p"),
                    "day_of_week":op.ops_timing.day_of_week,
                    "is_lunch":"True" if op.ops_timing.is_lunch == True else "False",
                    "is_holiday":"True" if op.ops_timing.is_holiday == True else "False",
                    "is_saturday":"True" if op.ops_timing.is_saturday == True else "False",
                    "is_sunday":"True" if op.ops_timing.is_sunday == True else "False",
                    
                }
                opslist.append(opsobj)   
             
            
        except Exception as e:
            mssg = "list OPS Timing Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)
        
        return json.dumps({"result":"success","error_code":"","error_message":"","ops_timing_count":len(ops), "ops_timing_list":opslist})            
    
    def new_ops_timing(self,avars):
        auth  = current.auth
        db = self.db
        
        logger.loggerpms2.info("Enter new_ops_timings")
        try:
            ref_code = common.getkeyvalue(avars,"ref_code","")
            ref_id = int(common.getkeyvalue(avars,"ref_id",0))
    
            calendar_date = common.getdatefromstring(common.getkeyvalue(avars, "calendar_date", common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")), "%d/%m/%Y")
            day_of_week = common.getkeyvalue(avars,"day_of_week","mon")
            
            strtime = common.getkeyvalue(avars,"open_time","09:00 AM")
            open_time = common.gettimefromstring(strtime, "%I:%M %p")
            
            strtime = common.getkeyvalue(avars,"close_time","06:00 PM")
            close_time = common.gettimefromstring(strtime, "%I:%M %p")
                                                                                                                      
            is_lunch = common.getboolean(common.getkeyvalue(avars,"is_lunch","True"))
            is_holiday = common.getboolean(common.getkeyvalue(avars,"is_holiday","True"))
            is_saturday = common.getboolean(common.getkeyvalue(avars,"is_saturday","True"))
            is_sunday = common.getboolean(common.getkeyvalue(avars,"is_sunday","True"))

            timeid = db.ops_timings.insert(\
                calendar_date = calendar_date,
                day_of_week =day_of_week,
                open_time = open_time,
                close_time = close_time,
                is_lunch = is_lunch,
                is_holiday = is_holiday,
                is_saturday = is_saturday,
                is_sunday = is_sunday,
                is_active = True,
                created_on=common.getISTFormatCurrentLocatTime(),
                modified_on=common.getISTFormatCurrentLocatTime(),
                created_by = 1 if(auth.user == None) else auth.user.id,
                modified_by= 1 if(auth.user == None) else auth.user.id
                )
                
            db.ops_timing_ref.insert(ops_timing_id = timeid, ref_code = ref_code,ref_id = ref_id)
            
            rspobj = {
                "ref_code":ref_code,
                "ref_id":ref_id,
                "ops_timing_id":str(timeid),
                "result":"success",
                "error_code":"",
                "error_message":""
            }            
            
        except Exception as e:
            mssg = "new OPS Timing Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)        
          
        return json.dumps(rspobj)

    
    
    
        