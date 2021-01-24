from gluon import current
import datetime

import json

from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger

class Bank:
    def __init__(self,db):
        self.db = db
         

    def delete_account(self,avars):
        auth  = current.auth
        db = self.db

        try:

            bankid = int(common.getkeyvalue(avars,"bankid",0)),

            db(db.bank_details.id == bankid).update(\
                is_active = False,
                modified_on=common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id

            )

            rspobj = {
                'bankid': bankid,
                'result' : 'success',
                "error_code":"",
                "error_message":""
            }               


        except Exception as e:
            mssg = "Delete Bank Account Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)

        return json.dumps(rspobj)     

    def update_account(self,avars):
        logger.loggerpms2.info("Enter Update Account API")
        auth  = current.auth
        db = self.db
        try:
            bankid = int(common.getkeyvalue(avars,"bankid",0)),
            
            bankname = common.getkeyvalue(avars,"bankname","")
            bankbranch = common.getkeyvalue(avars,"bankbranch","")
            bankaccountname = common.getkeyvalue(avars,"bankaccountname","")
            bankaccountno = common.getkeyvalue(avars,"bankaccountno","")
            bankaccounttype = common.getkeyvalue(avars,"bankaccounttype","")
            bankmicrno = common.getkeyvalue(avars,"bankmicrno","")
            bankifsccode = common.getkeyvalue(avars,"bankifsccode","")
            address1 = common.getkeyvalue(avars,"address1","")
            address2 = common.getkeyvalue(avars,"address2","")
            address3 = common.getkeyvalue(avars,"address3","")
            city = common.getkeyvalue(avars,"city","")
            st = common.getkeyvalue(avars,"st","")
            pin = common.getkeyvalue(avars,"pin","")
            
            db(db.bank_details.id == bankid).update(\
                bankname = bankname,
                bankbranch= bankbranch,
                bankaccountname = bankaccountname,
                bankaccountno = bankaccountno,
                bankaccounttype = bankaccounttype,
                bankmicrno = bankmicrno,
                bankifsccode = bankifsccode,
                address1 = address1,
                address2 = address2,
                address3 = address3,
                city = bankaccountname,
                st = bankaccountname,
                pin = bankaccountname,
                is_active = True,
                created_on=common.getISTFormatCurrentLocatTime(),
                modified_on=common.getISTFormatCurrentLocatTime(),
                created_by = 1 if(auth.user == None) else auth.user.id,
                modified_by= 1 if(auth.user == None) else auth.user.id
                )
            
            bankobj = {
                "bankid":str(bankid),
                "result":"success",
                "error_message":"",
                "error_code":""
            }
            
            
        except Exception as e:
            mssg = "Update Bank Account Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)                 
        
        return json.dumps(bankobj)        

    def get_account(self,avars):
        logger.loggerpms2.info("Enter Get Account API")
        auth  = current.auth
        db = self.db
        
        try:
            bankid = int(common.getkeyvalue(avars,"bankid",0))
            
            ds = db(db.bank_details.id == bankid) & (db.bank_details.is_active == True)).select()
            
            bankobj = {}
            for d in ds:
                bankobj = {
                    "bankid":str(d.id),
                    "bankname":d.bankname,
                    "bankbranch":d.bankbranch,
                    "bankaccountname":d.bankaccountname,
                    "bankaccountno":d.bankaccountno,
                    "bankaccounttype":d.bankaccounttype,
                    "bankmicrno":d.bankmicrno,
                    "bankifsccode":d.bankifsccode,
                    "address1":d.address1,
                    "address2":d.address2,
                    "address3":d.address3,
                    "city":d.city,
                    "st":d.st,
                    "pin":d.pin,
                }
                
            bankobj["result"] = "success"
            bankobj["error_code"] = ""
            bankobj["error_message"] = ""
            
            
        except Exception as e:
            mssg = "Get Bank Account Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)
        
        return json.dumps(bankobj)
            
    def new_account(self,avars):
        logger.loggerpms2.info("Enter New Account API")
        auth  = current.auth
        db = self.db
        
        try:
            bankname = common.getkeyvalue(avars,"bankname","")
            bankbranch = common.getkeyvalue(avars,"bankbranch","")
            bankaccountname = common.getkeyvalue(avars,"bankaccountname","")
            bankaccountno = common.getkeyvalue(avars,"bankaccountno","")
            bankaccounttype = common.getkeyvalue(avars,"bankaccounttype","")
            bankmicrno = common.getkeyvalue(avars,"bankmicrno","")
            bankifsccode = common.getkeyvalue(avars,"bankifsccode","")
            address1 = common.getkeyvalue(avars,"address1","")
            address2 = common.getkeyvalue(avars,"address2","")
            address3 = common.getkeyvalue(avars,"address3","")
            city = common.getkeyvalue(avars,"city","")
            st = common.getkeyvalue(avars,"st","")
            pin = common.getkeyvalue(avars,"pin","")
            bankid = db.bank_details.insert(\
                bankname = bankname,
                bankbranch= bankbranch,
                bankaccountname = bankaccountname,
                bankaccountno = bankaccountno,
                bankaccounttype = bankaccounttype,
                bankmicrno = bankmicrno,
                bankifsccode = bankifsccode,
                address1 = address1,
                address2 = address2,
                address3 = address3,
                city = bankaccountname,
                st = bankaccountname,
                pin = bankaccountname,
                is_active = True,
                created_on=common.getISTFormatCurrentLocatTime(),
                modified_on=common.getISTFormatCurrentLocatTime(),
                created_by = 1 if(auth.user == None) else auth.user.id,
                modified_by= 1 if(auth.user == None) else auth.user.id
                )
            
            bankobj = {
                "bankid":str(bankid),
                "result":"success",
                "error_message":"",
                "error_code":""
            }
            
            
        except Exception as e:
            mssg = "New Bank Account Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)                 
        
        return json.dumps(bankobj)