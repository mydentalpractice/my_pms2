from gluon import current
import datetime

import json

from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger

from applications.my_pms2.modules import mdpprospect

class Agent:
    def __init__(self,db):
        self.db = db
    
      
    def new_agent_prospect(self,avars):
        logger.loggerpms2.info("Enter New Agent Prospect API")
        auth  = current.auth
        db = self.db

        try:
            cell =  common.getkeyvalue(avars,"cell","XXXXXXXXXX")
            aobj = json.loads(self.new_agent({"cell":cell}))
            
            if(aobj["result"] == "fail"):
                mssg = "New Agent Prospect Exception:\n" + str(e)
                logger.loggerpms2.info(mssg)      
                excpobj = {}
                excpobj["result"] = "fail"
                excpobj["error_message"] = mssg
                return json.dumps(excpobj)                 
                
            avars["ref_code"] ="AGN"
            avars["ref_id"] = aboj["agentid"]
            pobj = mdpprospect.Prospect(db)
            rspobj = json.loads(pobj.new_prospect(avars))

            rspobj["agentid"] = aobj["agentid"]


        except Exception as e:
            mssg = "New Prospect Agent Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)                 

        return json.dumps(rspobj)        
        
    def new_agent(self,avars):
        logger.loggerpms2.info("Enter New Agent API")
        auth  = current.auth
        db = self.db

        try:
            cell =  common.getkeyvalue(avars,"cell","XXXXXXXXXX")
            agentref = "AGN_" + cell
            r = db((db.agent.agent == agentref) & (db.agent.is_active == True)).select()
            if(len(r) >= 1):
                
                rspobj = {
                    "result":"success",
                    "agentid":str(r[0].id),
                    "error_message":"",
                    "error_code":""
                }
                return json.dumps(rspobj)
            
            
            agentid = db.agent.insert(\
                agent =common.getkeyvalue(avars,"agent ",agentref),
                name=common.getkeyvalue(avars,"name",agentref+"_name"),
                address1=common.getkeyvalue(avars,"address1",""),
                address2=common.getkeyvalue(avars,"address2",""),
                address3=common.getkeyvalue(avars,"address3",""),
                city=common.getkeyvalue(avars,"city",""),
                st=common.getkeyvalue(avars,"st",""),
                pin=common.getkeyvalue(avars,"pin",""),
                telephone=common.getkeyvalue(avars,"telephone",""),
                cell=common.getkeyvalue(avars,"cell",cell),
                fax=common.getkeyvalue(avars,"fax",""),
                email=common.getkeyvalue(avars,"email",""),
                taxid=common.getkeyvalue(avars,"taxid",""),
                enrolleddate=common.getdatefromstring(common.getkeyvalue(avars,"enrolleddate",common.getstringfromdate(datetime.date.today(),"%d/%m/%Y")),"%d/%m/%Y"),
                holdcommissionchecks=common.getboolean(common.getkeyvalue(avars,"holdcommissionchecks","True")),
                commissionYTD=float(common.getkeyvalue(avars,"commissionYTD","0")),
                commissionMTD=float(common.getkeyvalue(avars,"commissionMTD","0")),
                TotalCompanies=int(common.getkeyvalue(avars,"TotalCompanies","0")),
                is_active = True,
                created_on=common.getISTFormatCurrentLocatTime(),
                modified_on=common.getISTFormatCurrentLocatTime(),
                created_by = 1 if(auth.user == None) else auth.user.id,
                modified_by= 1 if(auth.user == None) else auth.user.id
            )


            rspobj = {
                "agentid":str(agentid),
                "result":"success",
                "error_message":"",
                "error_code":""
            }


        except Exception as e:
            mssg = "New Agent Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)                 

        return json.dumps(rspobj)