from gluon import current
import datetime
#
import json

import requests
import urllib
import base64
import hashlib
import uuid



from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger


class CRM:
    def __init__(self,db):
        
        self.db = db
        self.apiURL = "https://api.mydentalpractice.in/vtigercrmapi/"
    
    #{
    #"patient_id":<3308>
    #}    
    def mdp_crm_createpatient(self,avars):
        logger.loggerpms2.info("Enter MDP CRM CreatePatient API " + json.dumps(avars))
        auth  = current.auth
        db = self.db
        rspobj = {}
        
        try:
            #create URL
            apiURL =self.apiURL
            apiURL = apiURL+"crmCreatePatient"
            #crm_header = {"Content-Type":"application/json"}
            crm_header = {"Content-Type":"application/json","x-api-key":"MYDP~mc3b1q2o"}
            
            jsonreqdata = {
                "patient_id":common.getkeyvalue(avars,"patient_id","0")
            }            
            
            logger.loggerpms2.info("CRM Create Patient REQUEST\n" + json.dumps(jsonreqdata) + "URL " + apiURL + " Header " + json.dumps(crm_header))
            
            #call API
            resp = requests.post(apiURL,headers=crm_header,json=jsonreqdata)
            jsonresp = {}
            if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
                respstr =   resp.text
                #jsonresp = json.loads(respstr)
                jsonresp["response"] = respstr
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
            
            
        except Exception as e:
            mssg = " MDP CRM CreatePatient API Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = ""
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)           
        
        logger.loggerpms2.info("Exit MD CRM CreatePatientAPI API " + json.dumps(jsonresp))
        return json.dumps(jsonresp)

        #{
        #"provider_id":<3308>
        #}    
    def mdp_crm_createprovider(self,avars):
        logger.loggerpms2.info("Enter MDP CRM CreateProvider API " + json.dumps(avars))
        auth  = current.auth
        db = self.db
        rspobj = {}
        
        try:
            #create URL
            apiURL =self.apiURL
            apiURL = apiURL+"crmCreateProvider"
            #crm_header = {"Content-Type":"application/json"}
            crm_header = {"Content-Type":"application/json","x-api-key":"MYDP~mc3b1q2o"}
            
            jsonreqdata = {
                "provider_id":common.getkeyvalue(avars,"provider_id","0")
            }            
            
            logger.loggerpms2.info("CRM Create Provider REQUEST\n" + json.dumps(jsonreqdata) + "URL " + apiURL + " Header " + json.dumps(crm_header))
            
            #call API
            resp = requests.post(apiURL,headers=crm_header,json=jsonreqdata)
            jsonresp = {}
            if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
                respstr =   resp.text
                #jsonresp = json.loads(respstr)
                jsonresp["response"] = respstr
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
            
            
        except Exception as e:
            mssg = " MDP CRM CreateProvider API Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = ""
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)           
        
        logger.loggerpms2.info("Exit MD CRM CreateProvider API " + json.dumps(jsonresp))
        return json.dumps(jsonresp)

    #{
    #"provider_id":<3308>
    #}    
    def mdp_crm_updateprovider(self,avars):
        logger.loggerpms2.info("Enter MDP CRM mdp_crm_updateprovider API " + json.dumps(avars))
        auth  = current.auth
        db = self.db
        rspobj = {}
        
        try:
            #create URL
            apiURL =self.apiURL
            apiURL = apiURL+"crmUpdateProvider"
            #crm_header = {"Content-Type":"application/json"}
            crm_header = {"Content-Type":"application/json","x-api-key":"MYDP~mc3b1q2o"}
            
            jsonreqdata = {
                "provider_id":common.getkeyvalue(avars,"provider_id","0")
            }            
            
            logger.loggerpms2.info("CRM mdp_crm_updateprovider REQUEST\n" + json.dumps(jsonreqdata) + "URL " + apiURL + " Header " + json.dumps(crm_header))
            
            #call API
            resp = requests.post(apiURL,headers=crm_header,json=jsonreqdata)
            jsonresp = {}
            if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
                respstr =   resp.text
                #jsonresp = json.loads(respstr)
                jsonresp["response"] = respstr
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
            
            
        except Exception as e:
            mssg = " MDP CRM mdp_crm_updateprovider API Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = ""
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)           
        
        logger.loggerpms2.info("Exit MD CRM mdp_crm_updateprovider API " + json.dumps(jsonresp))
        return json.dumps(jsonresp)
    #{
    #"clinic_id":<3308>
    #}    
    def mdp_crm_createclinic(self,avars):
        logger.loggerpms2.info("Enter MDP CRM mdp_crm_createclinic API " + json.dumps(avars))
        auth  = current.auth
        db = self.db
        rspobj = {}
        
        try:
            #create URL
            apiURL =self.apiURL
            apiURL = apiURL+"crmCreateClinic"
            #crm_header = {"Content-Type":"application/json"}
            crm_header = {"Content-Type":"application/json","x-api-key":"MYDP~mc3b1q2o"}
            
            jsonreqdata = {
                "clinic_id":common.getkeyvalue(avars,"clinic_id","0")
            }            
            
            logger.loggerpms2.info("CRM mdp_crm_createclinic REQUEST\n" + json.dumps(jsonreqdata) + "URL " + apiURL + " Header " + json.dumps(crm_header))
            
            #call API
            resp = requests.post(apiURL,headers=crm_header,json=jsonreqdata)
            jsonresp = {}
            if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
                respstr =   resp.text
                #jsonresp = json.loads(respstr)
                jsonresp["response"] = respstr
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
            
            
        except Exception as e:
            mssg = " MDP CRM mdp_crm_createclinic API Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = ""
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)           
        
        logger.loggerpms2.info("Exit MD CRM mdp_crm_updateprovider API " + json.dumps(jsonresp))
        return json.dumps(jsonresp)

    #{
    #"clinic_id":<3308>
    #}    
    def mdp_crm_updateclinic(self,avars):
        logger.loggerpms2.info("Enter MDP CRM mdp_crm_updateclinic API " + json.dumps(avars))
        auth  = current.auth
        db = self.db
        rspobj = {}
        
        try:
            #create URL
            apiURL =self.apiURL
            apiURL = apiURL+"crmUpdateClinic"
            #crm_header = {"Content-Type":"application/json"}
            crm_header = {"Content-Type":"application/json","x-api-key":"MYDP~mc3b1q2o"}
            
            jsonreqdata = {
                "clinic_id":common.getkeyvalue(avars,"clinic_id","0")
            }            
            
            logger.loggerpms2.info("CRM mdp_crm_updateclinic REQUEST\n" + json.dumps(jsonreqdata) + "URL " + apiURL + " Header " + json.dumps(crm_header))
            
            #call API
            resp = requests.post(apiURL,headers=crm_header,json=jsonreqdata)
            jsonresp = {}
            if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
                respstr =   resp.text
                #jsonresp = json.loads(respstr)
                jsonresp["response"] = respstr
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
            
            
        except Exception as e:
            mssg = " MDP CRM mdp_crm_updateclinic API Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = ""
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)           
        
        logger.loggerpms2.info("Exit MD CRM mdp_crm_updateclinic API " + json.dumps(jsonresp))
        return json.dumps(jsonresp)
            

   #{
    #"cf_events_mdpaptid":31931
    #"subject":"Appointment Created using vTiger CRM"
#}
    def mdp_crm_bookappointment(self,avars):
        logger.loggerpms2.info("Enter MDP CRM Book Appointment API " + json.dumps(avars))
        auth  = current.auth
        db = self.db
        rspobj = {}
        
        try:
            #create URL
            apiURL =self.apiURL
            apiURL = apiURL+"crmBookAppointment"
            #crm_header = {"Content-Type":"application/json"}
            crm_header = {"Content-Type":"application/json","x-api-key":"MYDP~mc3b1q2o"}
            
            jsonreqdata = {
                "appointment_id":common.getkeyvalue(avars,"appointment_id",0)
                
            }            
            
            logger.loggerpms2.info("MDP CRM Book Appointment REQUEST\n" + json.dumps(jsonreqdata) + "URL " + apiURL + " Header " + json.dumps(crm_header))
            
            #call API
            resp = requests.post(apiURL,headers=crm_header,json=jsonreqdata)
            jsonresp = {}
            if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
                respstr =   resp.text
                jsonresp["response"] = respstr
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
                
            
            
        except Exception as e:
            mssg = " MDP CRM   Book Appointmentt API Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = ""
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)           
        
        logger.loggerpms2.info("Exit MD CRM Book Appointment " + json.dumps(jsonresp))
        return json.dumps(jsonresp)             
    
    
    #formdata": [
    #{
        #"key": "cf_events_mdpaptid",
        #"value": "33095",
       
    #{
        #"key": "cf_events_appointmentstatus",
        #"value": "Re-Scheduled",
       
    #{
        #"key": "cf_events_comment",
        #"value": "test1 Re-Scheduled",
        #"description": "optional",
       
        #},
    #{
        #"key": "date_start",
        #"value": "2023-01-28",
        #"description": "optional",
      
        #},
    #{
        #"key": "time_start",
        #"value": "07:30 AM",
        #"description": "optional",
        #"type": "text"
        #},
    #{
        #"key": "due_date",
        #"value": "2023-01-28",
        #"description": "optional",
        #"type": "text"
        #},
    #{
        #"key": "time_end",
        #"value": "08:00 AM",
        #"description": "optional",
        #"type": "text"
    #}
    #],
    def mdp_crm_updateappointment(self,avars):
        logger.loggerpms2.info("Enter MDP CRM Update Appointment API " + json.dumps(avars))
        auth  = current.auth
        db = self.db
        rspobj = {}
        
        try:
            #create URL
            apiURL =self.apiURL
            apiURL = apiURL+"crmUpdateAppointment"
            #crm_header = {"Content-Type":"application/json"}
            crm_header = {"Content-Type":"application/json","x-api-key":"MYDP~mc3b1q2o"}
            
            jsonreqdata = {
                "appointment_id":common.getkeyvalue(avars,"appointment_id",0),
            }            
            
            logger.loggerpms2.info("MDP CRM Update Appointment REQUEST\n" + json.dumps(jsonreqdata) + "URL " + apiURL + " Header " + json.dumps(crm_header))
            
            #call API
            resp = requests.post(apiURL,headers=crm_header,json=jsonreqdata)
            jsonresp = {}
            if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
                respstr =   resp.text
                jsonresp["response"] = respstr
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
            
            
        except Exception as e:
            mssg = " MDP CRM   Book Appointmentt API Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = ""
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)           
        
        logger.loggerpms2.info("Exit MD CRM UpdateAppointment API API " + json.dumps(jsonresp))
        return json.dumps(jsonresp)                 