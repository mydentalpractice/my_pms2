from gluon import current


import datetime

import json
from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger

class Plan:
    def __init__(self,db):
        self.db = db
        return 

    #this api returns premium for a company/policy/region
    #if region is not specifieed, it defaults to 'ALL'
    def get_plan_premium(self,avars):
        db = self.db
        premium = 0
        rspobj = {}
        
        try:
            companycode = common.getkeyvalue(avars,"companycode","WALKIN")
            plancode = common.getkeyvalue(avars,"plancode","PREMWALKIN")
            regioncode = common.getkeyvalue(avars,"regioncode","ALL")
    
            r = db((db.provider_region_plan.companycode == companycode) & 
                   (db.provider_region_plan.plancode == plancode) &
                   (db.provider_region_plan.regioncode == regioncode)
                   ).select()
    
            premium = float(common.getvalue(r[0].premium)) if(len(r)>0) else 0
    
            rspobj["result"] = "success"
            rspobj["error_code"] = ""
            rspobj["error_message"] = ""    
            rspobj["premium"] = str(premium)
    
    
        except Exception as e:
            mssg = "get_plan_premium  Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = ""
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)    
        
        
        return json.dumps(rspobj)

   

