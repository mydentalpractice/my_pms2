from gluon import current
import datetime
import calendar

import json
import os
import tempfile

import base64
from base64 import decodestring



from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger



    
def isLeapYear(year):
    if (year % 4) == 0:  
        if (year % 100) == 0:  
            if (year % 400) == 0:  
                return True
            else:  
                return False
        else:  
            return True
    else:  
        return False
    
    return False

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
            timingid = int(common.getid(avars["timingid"])) if "timingid" in avars else 0 
    
            ops = db((db.ops_timing.id == timingid) & (db.ops_timing.is_active == True)).select()
            ref = db(db.ops_timing_ref.ops_timing_id == timingid).select()
            
            if(len(ops) != 1):
                rspobj = {
                    "timingid":str(timingid),
                    "result":"fail",
                    "error_message":"Error Getting  Clinic Timing - no or duplicate clinic record",
                    "error_code":""
                }                
                return json.dumps(rspobj)
                
            for op in ops:
                opsobj = {
                    "ops_timing_id":str(ref[0].id),
                    "ref_code":ref[0].ref_code if len(ref) == 1 else "",
                    "ref_id":ref[0].ref_id if len(ref) == 1 else 0,
                    "calendar_date":common.getstringfromdate(op.calendar_date, "%d/%m/%Y"),
                    "open_time":common.getstringfromtime(op.open_time, "%I:%M %p"),
                    "close_time":common.getstringfromtime(op.close_time, "%I:%M %p"),
                    "day_of_week":op.day_of_week,
                    "is_lunch":"True" if op.is_lunch == True else "False",
                    "is_holiday":"True" if op.is_holiday == True else "False",
                    "is_saturday":"True" if op.is_saturday == True else "False",
                    "is_sunday":"True" if op.is_sunday == True else "False",
                }            
            
            opsobj["result"] = "success"
            opsobj["error_message"] = ""
            opsobj["error_code"] = ""
            
        except Exception as e:
            mssg = "Get OPS Timing Exception:\n" + str(e)
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
            timingid = int(common.getid(avars["timingid"])) if "timingid" in avars else 0 
            ds = db((db.ops_timing.id == timingid) & (db.ops_timing.is_active == True)).select()
            if(len(ds) != 1):
                rspobj={
                    "ops_timing_id":str(timingid),
                    "result":"fail",
                    "error_message":"Error Updating OPS Timing - no or duplicate record",
                    "error_code":""
                }
                return json.dumps(rspobj)
            
            
            calendar_date = common.getdatefromstring(common.getkeyvalue(avars, "calendar_date", common.getstringfromdate(ds[0].calendar_date, "%d/%m/%Y")), "%d/%m/%Y")
            day_of_week = common.getkeyvalue(avars,"day_of_week",ds[0].day_of_week)
            
            strtime = common.getkeyvalue(avars,"open_time",common.getstringfromtime(ds[0].open_time,"%I:%M %p"))
            #open_time = common.gettimefromstring(strtime, "%I:%M %p")
            open_time = datetime.datetime(*(common.gettimefromstring(strtime, "%I:%M %p"))[:6])
            
            strtime = common.getkeyvalue(avars,"close_time",common.getstringfromtime(ds[0].close_time,"%I:%M %p"))
            #close_time = common.gettimefromstring(strtime, "%I:%M %p")
            close_time = datetime.datetime(*(common.gettimefromstring(strtime, "%I:%M %p"))[:6])
                                                                                                                      
            is_lunch = common.getboolean(common.getkeyvalue(avars,"is_lunch",common.getstring(ds[0].is_lunch)))
            is_holiday = common.getboolean(common.getkeyvalue(avars,"is_lunch",common.getstring(ds[0].is_holiday)))
            is_saturday = common.getboolean(common.getkeyvalue(avars,"is_lunch",common.getstring(ds[0].is_saturday)))
            is_sunday = common.getboolean(common.getkeyvalue(avars,"is_lunch",common.getstring(ds[0].is_sunday)))
 
            db(db.ops_timing.id == timingid).update(\
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
                
                'timingid': timingid,
                'result' : 'success',
                "error_code":"",
                "error_message":""
                       }                  
            
        except Exception as e:
            mssg = "Update OPS Timing Exception:\n" + str(e)
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
           
            timingid = int(common.getid(avars["timingid"])) if "timingid" in avars else 0 
            
            db(db.ops_timing.id == timingid).update(
                is_active = False,
                modified_on=common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id
        
            )
        
            rspobj = {
                'timingid': timingid,
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
            
            from_date = None
            to_date = None
            
            
            
            fromdtstr = common.getkeyvalue(avars,"from_date","01/01/2000")
            fromdt = None
            if(fromdtstr != None):
                fromdt = common.getdatefromstring(fromdtstr, "%d/%m/%Y") 

            todtstr = common.getkeyvalue(avars,"to_date","31/12/2099")
            todt = None
            if(todtstr != None):
                todt = common.getdatefromstring(todtstr, "%d/%m/%Y")

          
            
            ops = None
            if(ref_code == ""):
                if(ref_id == 0):
                    ops = db((db.ops_timing.is_active == True)& (db.ops_timing.calendar_date >= fromdt)& (db.ops_timing.calendar_date <= todt)).\
                        select(db.ops_timing.ALL,db.ops_timing_ref.ALL,\
                                                                                        left=db.ops_timing.on((db.ops_timing.id == db.ops_timing_ref.ops_timing_id)))
                else:
                    ops = db((db.ops_timing_ref.ref_id == ref_id)& (db.ops_timing.calendar_date >= fromdt)& (db.ops_timing.calendar_date <= todt) &  (db.ops_timing.is_active == True)).select(db.ops_timing.ALL,db.ops_timing_ref.ALL,\
                                                                                        left=db.ops_timing.on((db.ops_timing.id == db.ops_timing_ref.ops_timing_id)))
                    
            else:
                if(ref_id == 0):
                    ops = db((db.ops_timing_ref.ref_code==ref_code)& (db.ops_timing.calendar_date >= fromdt)& (db.ops_timing.calendar_date <= todt) &  (db.ops_timing.is_active == True)).select(db.ops_timing.ALL,db.ops_timing_ref.ALL,\
                                                                                        left=db.ops_timing.on((db.ops_timing.id == db.ops_timing_ref.ops_timing_id)))
                else:
                    ops = db((db.ops_timing_ref.ref_code==ref_code) &(db.ops_timing_ref.ref_id == ref_id)& (db.ops_timing.calendar_date >= fromdt)& (db.ops_timing.calendar_date <= todt) &  (db.ops_timing.is_active == True)).select(db.ops_timing.ALL,db.ops_timing_ref.ALL,\
                                                                                        left=db.ops_timing.on((db.ops_timing.id == db.ops_timing_ref.ops_timing_id)))
                
            
           
            for op in ops:
               
                opsobj = {
                    "ops_timing_id":str(common.getid(op.ops_timing.id)),
                    "ref_code":op.ops_timing_ref.ref_code,
                    "ref_id":op.ops_timing_ref.ref_id,
                    "calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),
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

    def list_ops_timing_2(self,avars):
        auth  = current.auth
        db = self.db
        
        try:
            
            ref_code = avars["ref_code"] if "ref_code" in avars else ""
            ref_id = int(common.getid(avars["ref_id"])) if "ref_id" in avars else 0            
            
            opslist = []
            opsobj = {}
            
            rspobj = {}
            
            from_date = None
            to_date = None
            
            
            
            fromdtstr = common.getkeyvalue(avars,"from_date","01/01/2000")
            fromdt = None
            if(fromdtstr != None):
                fromdt = common.getdatefromstring(fromdtstr, "%d/%m/%Y") 

            todtstr = common.getkeyvalue(avars,"to_date","31/12/2099")
            todt = None
            if(todtstr != None):
                todt = common.getdatefromstring(todtstr, "%d/%m/%Y")

          
            
            ops = None
            if(ref_code == ""):
                if(ref_id == 0):
                    ops = db((db.ops_timing.is_active == True)& (db.ops_timing.calendar_date >= fromdt)& (db.ops_timing.calendar_date <= todt)).\
                        select(db.ops_timing.ALL,db.ops_timing_ref.ALL,\
                                                                                        left=db.ops_timing.on((db.ops_timing.id == db.ops_timing_ref.ops_timing_id)))
                else:
                    ops = db((db.ops_timing_ref.ref_id == ref_id)& (db.ops_timing.calendar_date >= fromdt)& (db.ops_timing.calendar_date <= todt) &  (db.ops_timing.is_active == True)).select(db.ops_timing.ALL,db.ops_timing_ref.ALL,\
                                                                                        left=db.ops_timing.on((db.ops_timing.id == db.ops_timing_ref.ops_timing_id)))
                    
            else:
                if(ref_id == 0):
                    ops = db((db.ops_timing_ref.ref_code==ref_code)& (db.ops_timing.calendar_date >= fromdt)& (db.ops_timing.calendar_date <= todt) &  (db.ops_timing.is_active == True)).select(db.ops_timing.ALL,db.ops_timing_ref.ALL,\
                                                                                        left=db.ops_timing.on((db.ops_timing.id == db.ops_timing_ref.ops_timing_id)))
                else:
                    ops = db((db.ops_timing_ref.ref_code==ref_code) &(db.ops_timing_ref.ref_id == ref_id)& (db.ops_timing.calendar_date >= fromdt)& (db.ops_timing.calendar_date <= todt) &  (db.ops_timing.is_active == True)).select(db.ops_timing.ALL,db.ops_timing_ref.ALL,\
                                                                                        left=db.ops_timing.on((db.ops_timing.id == db.ops_timing_ref.ops_timing_id)))
                
            
           
            monlist = []
            tuelist = []
            wedlist = []
            thulist = []
            frilist = []
            satlist = []
            sunlist = []
            
            
            
            for op in ops:
                
                if((op.ops_timing.day_of_week).lower() == "mon"):
                    if(op.ops_timing.is_lunch == True):
                        opsobj = {
                            "is_lunch":True}
                        monlist.append(opsobj)
                    
                    if(op.ops_timing.is_holiday == True):
                        opsobj = {"is_holiday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        monlist.append(opsobj)
                        continue
                    if(op.ops_timing.is_saturday == True):
                        opsobj = {"is_saturday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        monlist.append(opsobj)
                        continue
                    if(op.ops_timing.is_sunday == True):
                        opsobj = {"is_sunday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        monlist.append(opsobj)
                        continue
                    opsobj = {
                        "ops_timing_id":str(common.getid(op.ops_timing.id)),
                        "calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),                        
                        "open_time":common.getstringfromtime(op.ops_timing.open_time, "%I:%M %p"),
                        "close_time":common.getstringfromtime(op.ops_timing.close_time, "%I:%M %p")
                    }
                    monlist.append(opsobj)
                    
                if((op.ops_timing.day_of_week).lower() == "tue"):
                    if(op.ops_timing.is_lunch == True):
                        opsobj = {"is_lunch":True}
                        tuelist.append(opsobj)
                    
                    if(op.ops_timing.is_holiday == True):
                        opsobj = {"is_holiday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        tuelist.append(opsobj)
                        continue
                    if(op.ops_timing.is_saturday == True):
                        opsobj = {"is_saturday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        tuelist.append(opsobj)
                        continue
                    if(op.ops_timing.is_sunday == True):
                        opsobj = {"is_sunday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        tuelist.append(opsobj)
                        continue
                    opsobj = {
                        "ops_timing_id":str(common.getid(op.ops_timing.id)),
                        "calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),                        
                        "open_time":common.getstringfromtime(op.ops_timing.open_time, "%I:%M %p"),
                        "close_time":common.getstringfromtime(op.ops_timing.close_time, "%I:%M %p")
                    }
                    tuelist.append(opsobj)
                    
                if((op.ops_timing.day_of_week).lower() == "wed"):
                    if(op.ops_timing.is_lunch == True):
                        opsobj = {"is_lunch":True}
                        wedlist.append(opsobj)
                    
                    if(op.ops_timing.is_holiday == True):
                        opsobj = {"is_holiday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        wedlist.append(opsobj)
                        continue
                    if(op.ops_timing.is_saturday == True):
                        opsobj = {"is_saturday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        wedlist.append(opsobj)
                        continue
                    if(op.ops_timing.is_sunday == True):
                        opsobj = {"is_sunday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        wedlist.append(opsobj)
                        continue
                    opsobj = {
                        "ops_timing_id":str(common.getid(op.ops_timing.id)),
                        "calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),                        
                        "open_time":common.getstringfromtime(op.ops_timing.open_time, "%I:%M %p"),
                        "close_time":common.getstringfromtime(op.ops_timing.close_time, "%I:%M %p")
                    }
                    wedlist.append(opsobj)
                    
                if((op.ops_timing.day_of_week).lower() == "thu"):
                    if(op.ops_timing.is_lunch == True):
                        opsobj = {"is_lunch":True}
                        thulist.append(opsobj)
                    
                    if(op.ops_timing.is_holiday == True):
                        opsobj = {"is_holiday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        thulist.append(opsobj)
                        continue
                    if(op.ops_timing.is_saturday == True):
                        opsobj = {"is_saturday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        thulist.append(opsobj)
                        continue
                    if(op.ops_timing.is_sunday == True):
                        opsobj = {"is_sunday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        thulist.append(opsobj)
                        continue
                    opsobj = {
                        "ops_timing_id":str(common.getid(op.ops_timing.id)),
                        "calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),                        
                        "open_time":common.getstringfromtime(op.ops_timing.open_time, "%I:%M %p"),
                        "close_time":common.getstringfromtime(op.ops_timing.close_time, "%I:%M %p")
                    }
                    thulist.append(opsobj)
                
                if((op.ops_timing.day_of_week).lower() == "fri"):
                    if(op.ops_timing.is_lunch == True):
                        opsobj = {"is_lunch":True}
                        frilist.append(opsobj)
                    
                    if(op.ops_timing.is_holiday == True):
                        opsobj = {"is_holiday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        frilist.append(opsobj)
                        continue
                    if(op.ops_timing.is_saturday == True):
                        opsobj = {"is_saturday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        frilist.append(opsobj)
                        continue
                    if(op.ops_timing.is_sunday == True):
                        opsobj = {"is_sunday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        frilist.append(opsobj)
                        continue
                    opsobj = {
                        "ops_timing_id":str(common.getid(op.ops_timing.id)),
                        "calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),                        
                        "open_time":common.getstringfromtime(op.ops_timing.open_time, "%I:%M %p"),
                        "close_time":common.getstringfromtime(op.ops_timing.close_time, "%I:%M %p")
                    }
                    frilist.append(opsobj)
                    
                if((op.ops_timing.day_of_week).lower() == "sat"):
                    if(op.ops_timing.is_lunch == True):
                        opsobj = {"is_lunch":True}
                        satlist.append(opsobj)
                    
                    if(op.ops_timing.is_holiday == True):
                        opsobj = {"is_holiday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        
                        satlist.append(opsobj)
                        continue
                    if(op.ops_timing.is_saturday == True):
                        opsobj = {"is_saturday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        satlist.append(opsobj)
                        continue
                    if(op.ops_timing.is_sunday == True):
                        opsobj = {"is_sunday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        satlist.append(opsobj)
                        continue
                    opsobj = {
                        "ops_timing_id":str(common.getid(op.ops_timing.id)),
                        "calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),                        
                        "open_time":common.getstringfromtime(op.ops_timing.open_time, "%I:%M %p"),
                        "close_time":common.getstringfromtime(op.ops_timing.close_time, "%I:%M %p")
                    }
                    satlist.append(opsobj)
            
                if((op.ops_timing.day_of_week).lower() == "sun"):
                    if(op.ops_timing.is_lunch == True):
                        opsobj = {"is_lunch":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        sunlist.append(opsobj)
                    
                    if(op.ops_timing.is_holiday == True):
                        opsobj = {"is_holiday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        
                        sunlist.append(opsobj)
                        continue
                    if(op.ops_timing.is_saturday == True):
                        opsobj = {"is_saturday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        sunlist.append(opsobj)
                        continue
                    if(op.ops_timing.is_sunday == True):
                        opsobj = {"is_sunday":True,"calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),}
                        sunlist.append(opsobj)
                        continue
                    opsobj = {
                        "ops_timing_id":str(common.getid(op.ops_timing.id)),
                        "calendar_date":common.getstringfromdate(op.ops_timing.calendar_date, "%d/%m/%Y"),                        
                        "open_time":common.getstringfromtime(op.ops_timing.open_time, "%I:%M %p"),
                        "close_time":common.getstringfromtime(op.ops_timing.close_time, "%I:%M %p")
                    }
                    sunlist.append(opsobj)
            
                
            rspobj = {
                "result":"success",
                "error_message":"",
                "error_code":"",
                "ref_code":op.ops_timing_ref.ref_code,
                "ref_id":op.ops_timing_ref.ref_id,
                
                "mon":monlist,
                "tue":tuelist,
                "wed":wedlist,
                "thu":thulist,
                "fri":frilist,
                "sat":satlist,
                "sun":sunlist
            
            }
               
               
             
            
        except Exception as e:
            mssg = "list OPS Timing Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)
        
        return json.dumps(rspobj)            

    
    def new_ops_timing(self,avars):
        auth  = current.auth
        db = self.db
        
        logger.loggerpms2.info("Enter new_ops_timings")
        try:
            ref_code = common.getkeyvalue(avars,"ref_code","")
            ref_id = int(common.getkeyvalue(avars,"ref_id",0))
    
            calendar_date = common.getdatefromstring(common.getkeyvalue(avars, "calendar_date", common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")), "%d/%m/%Y")
            day_of_week = common.getkeyvalue(avars,"day_of_week","mon")
            
                                                                                                                      
            is_lunch = common.getboolean(common.getkeyvalue(avars,"is_lunch","True"))
            is_holiday = common.getboolean(common.getkeyvalue(avars,"is_holiday","True"))
            is_saturday = common.getboolean(common.getkeyvalue(avars,"is_saturday","True"))
            is_sunday = common.getboolean(common.getkeyvalue(avars,"is_sunday","True"))

            
            if((is_holiday == True)|(is_saturday == True)|(is_sunday==True)):     
                strtime = common.getkeyvalue(avars,"open_time","12:00 AM")
            else:
                strtime = common.getkeyvalue(avars,"open_time","09:00 AM")
            open_time = datetime.datetime(*(common.gettimefromstring(strtime, "%I:%M %p"))[:6])
            
            
            if((is_holiday == True)|(is_saturday == True)|(is_sunday==True)):     
                strtime = common.getkeyvalue(avars,"close_time","11:59 PM")
            else:
                strtime = common.getkeyvalue(avars,"close_time","06:00 PM")
            close_time = datetime.datetime(*(common.gettimefromstring(strtime, "%I:%M %p"))[:6])


            timeid = db.ops_timing.insert(\
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

    
    def new_all_ops_timing(self,avars):
        auth  = current.auth
        db = self.db
        
        logger.loggerpms2.info("Enter new_ops_timings")
        try:
            ref_code = common.getkeyvalue(avars,"ref_code","")
            ref_id = int(common.getkeyvalue(avars,"ref_id",0))
            
         
            
            from_year = int(common.getkeyvalue(avars,"from_year",str(datetime.datetime.today().year)))
            to_year = int(common.getkeyvalue(avars,"to_year",str(datetime.datetime.today().year)))
            
            from_month = 1
            to_month = 12
            
            
            currentdate = None
            
            for year in xrange(from_year,to_year+1):
                for month in xrange(1,13):
                    for day in xrange(1,32):
                        
                        #dealing for month of Feb & Leap Year
                        if(isLeapYear(year) & (month == 2) & (day <=29)):
                            i = 0
                            
                        if(isLeapYear(year)& (month == 2) & (day >= 30)):
                            continue
                        
                        if((not isLeapYear(year)) & (month == 2) & (day <= 28)):
                            i = 0
                            
                        if((not isLeapYear(year)) & (month == 2) & (day >= 29)):
                            continue
                        
                        #dealing with months with 31 days
                        if((day <=31) & ((month == 1) | (month == 3) | (month == 5) | (month == 7) |(month == 8) | (month == 10) | (month == 12))):
                            #process
                            i = 0

                        #dealing with months with 31 days
                        if((day >= 32) & ((month == 1) | (month == 3) | (month == 5) | (month == 7) | (month == 8) | (month == 10) | (month == 12))):
                            continue
                        
                        #dealing with months with 30 days
                        if((day <=30) & ((month == 2) | (month == 4) | (month == 6) | (month == 9) | (month == 11))):
                            #process
                            i = 0
                            
                        if((day >= 31) & ((month == 2) | (month == 4) | (month == 6) | (month == 9) | (month == 11))):
                            continue
                        
                            
                        datestr = str(day).zfill(2) + "/" + str(month).zfill(2) + "/" + str(year).zfill(4)
                        dt = common.getdatefromstring(datestr, "%d/%m/%Y")
                        weekday = datetime.datetime.strptime(datestr, "%d/%m/%Y").weekday()
                        day_name = calendar.day_name[weekday]
                        day_name = day_name[:3]
                        
                        timings = common.getkeyvalue(avars,day_name,None)
                        if(timings != None):
                            for timing in timings:
                                open_time = common.getkeyvalue(timing,"open_time","")
                                close_time = common.getkeyvalue(timing,"close_time","")
                                isHoliday = common.getkeyvalue(timing,"isHoliday","False")
                                isLunch = common.getkeyvalue(timing,"isLunch","False")
                                isSaturday = common.getkeyvalue(timing,"isSaturday","False")
                                isSunday = common.getkeyvalue(timing,"isSunday","False")
                                timingobj = {
                                        "action":"new_ops_timing",
                                        "ref_code":ref_code,       
                                        "ref_id":ref_id,             
                                        "calendar_date":datestr,
                                        "day_of_week":day_name,
                                        "is_lunch":isLunch,           
                                        "is_holiday":isHoliday,         
                                        "is_saturday":isSaturday,
                                        "is_sunday":isSunday
                                
                                }
                                
                                if( (open_time != "") & (open_time != None)):
                                    timingobj["open_time"] = open_time
                                if( (close_time != "") & (close_time != None)):
                                    timingobj["close_time"] = close_time
                                    
                                rsp = json.loads(self.new_ops_timing(timingobj))
                        
        
            
         
          
            
            rspobj = {
                "ref_code":ref_code,
                "ref_id":ref_id,
               
                "result":"success",
                "error_code":"",
                "error_message":""
            }            
            
        except Exception as e:
            mssg = "new All OPS Timing Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)        
          
        return json.dumps(rspobj)

    
    
        