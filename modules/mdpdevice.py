from gluon import current
#

import datetime

import json
from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger

class Device:
    def __init__(self,db):
        self.db = db
        return 

    def get_device_info(self,avars):

        auth  = current.auth
        db = self.db
        rspobj = {}
        try:
            device_id = common.getkeyvalue(avars,"device_id","0")

            f = db(db.device_info.device_id == device_id).select()

            rspobj["result"] = "success"
            rspobj["error_code"] = ""
            rspobj["error_message"] = ""
            rspobj["device_info_id"] = f[0].id if(len(f) >0) else 0
            rspobj["user_id"] = f[0].user_id if(len(f) >0) else 0
            rspobj["device_id"] = f[0].device_id if(len(f) >0) else 0
            rspobj["device_type"] = f[0].device_type if(len(f) >0) else 0
            rspobj["device_fcm_token"] = f[0].device_type if(len(f) >0) else 0

        except Exception as e:
            mssg = "get_device_info  Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = ""
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)


        return json.dumps(rspobj)

    def add_device_info(self,avars):

        auth  = current.auth
        db = self.db
        rspobj = {}
        try:
            user_id = common.getkeyvalue(avars,"user_id",0)
            
            device_id = common.getkeyvalue(avars,"device_id","")


            db.device_info.update_or_insert(db.device_info.device_id == device_id,
                                            device_id = device_id,
                                            user_id = user_id,
                                            device_type = common.getkeyvalue(avars,"device_type",""),
                                            device_fcm_token = common.getkeyvalue(avars,"device_fcm_token","")
                                            )
            dv = db(db.device_info.device_id == device_id).select()
            
            rspobj["result"] = "success"
            rspobj["error_code"] = ""
            rspobj["error_message"] = ""
            rspobj["device_id"] = dv[0].device_id if(len(dv) != 0) else ""
            rspobj["device_info_id"] = dv[0].id if(len(dv) != 0) else 0
            
        except Exception as e:
            mssg = "add_device_info  Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = ""
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)


        return json.dumps(rspobj)


