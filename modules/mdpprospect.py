from gluon import current
import datetime

import json

from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger


class Prospect:
    def __init__(self,db):
        self.db = db
    
    
     
        
        
    
    def list_prospect(self,avars):
        auth  = current.auth
        db = self.db
        
        try:
            
            ref_code = avars["ref_code"] if "ref_code" in avars else ""
            ref_id = int(common.getid(avars["ref_id"])) if "ref_id" in avars else 0            
            
            lst = []
            obj = {}
            
            rspobj = {}
            
            ds = None
            if(ref_code == ""):
                if(ref_id == 0):
                    ds = db((db.prospect.is_active == True)).select(db.prospect.ALL,db.prospect_ref.ALL,\
                                                                                        left=db.prospect.on((db.prospect.id == db.prospect_ref.prospect_id)))
                else:
                    ds = db((db.prospect_ref.ref_id == ref_id) &  (db.prospect.is_active == True)).select(db.prospect.ALL,db.prospect_ref.ALL,\
                                                                                        left=db.prospect.on((db.prospect.id == db.prospect_ref.prospect_id)))
                    
            else:
                
                if(ref_id == 0):
                    ds = db((db.prospect_ref.ref_code == ref_code) &  (db.prospect.is_active == True)).select(db.prospect.ALL,db.prospect_ref.ALL,\
                                                                                        left=db.prospect.on((db.prospect.id == db.prospect_ref.prospect_id)))
      
                else:
                    ds = db((db.prospect_ref.ref_code == ref_code)&(db.prospect_ref.ref_id == ref_id) &  (db.prospect.is_active == True)).select(db.prospect.ALL,db.prospect_ref.ALL,\
                                                                                        left=db.prospect.on((db.prospect.id == db.prospect_ref.prospect_id)))
      
            
            for d in ds:
               
             
                obj = {
                    "ref_code":d.prospect_ref.ref_code,   #AGN
                    "ref_id":d.prospect_ref.ref_id,       #ID to either AGent Table
                    
                    
                    "providername":d.prospect.providername,
                    "cell":d.prospect.cell,
                    "email":d.prospect.email,
                    "status":d.prospect.status
                }
                lst.append(obj)   
             
            
        except Exception as e:
            mssg = "list Prospect Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)
        
        return json.dumps({"result":"success","error_code":"","error_message":"","count":len(ds),  "list":lst})            
    
    
    def get_prospect(self,avars):
        db = self.db
        auth  = current.auth
        rspobj = {}
        owner = ""
        
        try:
            prospectid = int(common.getkeyvalue(avars,"prospectid",0))
            r = db(db.prospect_ref.prospect_id ==prospectid).select()
            ref_code = r[0].ref_code if len(r) == 1 else ""
            ref_id = int(r[0].ref_id) if len(r) == 1 else 0
            ds = db((db.prospect.id == prospectid) & (db.prospect.is_active == True)).select()
            
                   

            if(len(ds) != 1):
                rspobj = {
                    
                    "prospectid":str(prospectid),
                    "result":"fail",
                    "error_message":"Error Getting Prospect Details - no or duplicate record",
                    "error_code":""
                }                
                return json.dumps(rspobj)
            
            
            rspobj = {
                "prospectid":str(prospectid),
                "provider'":ds[0].provider,
                "title'":ds[0].title,
                "providername'":ds[0].providername,
                "practicename'":ds[0].practicename,
                "address1'":ds[0].address1,
                "address2'":ds[0].address2,
                "address3'":ds[0].address3,
                "city'":ds[0].city,
                "st'":ds[0].st,
                "pin'":ds[0].pin,
                "p_address1'":ds[0].p_address1,
                "p_address2'":ds[0].p_address2,
                "p_address3'":ds[0].p_address3,
                "p_city'":ds[0].p_city,
                "p_st'":ds[0].p_st,
                "p_pin'":ds[0].p_pin,
                "telephone'":ds[0].telephone,
                "cell'":ds[0].cell,
                "fax'":ds[0].fax,
                "email'":ds[0].email,
                "taxid'":ds[0].taxid,
                "enrolleddate'":common.getstringfromdate(ds[0].enrolleddate,"%Y-%m-%d"),
                "assignedpatientmembers'":str(ds[0].assignedpatientmembers),
                "languagesspoken'":ds[0].languagesspoken,
                "speciality'":str(ds[0].speciality),
                "specialization'":ds[0].specialization,
                "sitekey'":ds[0].sitekey,
                "groupregion'":str(ds[0].groupregion),
                "registration'":ds[0].registration,
                "registered'":ds[0].registered,
                "pa_providername'":ds[0].pa_providername,
                "pa_practicename'":ds[0].pa_practicename,
                "pa_practiceaddress'":ds[0].pa_practiceaddress,
                "pa_dob'":common.getstringfromdate(ds[0].pa_dob,"%Y-%m-%d"),
                "pa_parent'":ds[0].pa_parent,
                "pa_address'":ds[0].pa_address,
                "pa_pan'":ds[0].pa_pan,
                "pa_regno'":ds[0].pa_regno,
                "pa_date'":common.getstringfromdate(ds[0].pa_date,"%Y-%m-%d"),
                "pa_accepted'":ds[0].pa_accepted,
                "pa_approved'":ds[0].pa_approved,
                "pa_approvedby'":ds[0].pa_approvedby,
                "pa_approvedon'":common.getstringfromdate(ds[0].pa_approvedon, "%Y-%m-%d"),
                "pa_day'":ds[0].pa_day,
                "pa_month'":ds[0].pa_month,
                "pa_location'":ds[0].pa_location,
                "pa_practicepin'":ds[0].pa_practicepin,
                "pa_hours'":ds[0].pa_hours,
                "pa_longitude'":ds[0].pa_longitude,
                "pa_latitude'":ds[0].pa_latitude,
                "pa_locationurl'":ds[0].pa_locationurl,
                "groupsms'":ds[0].groupsms,
                "groupemail'":ds[0].groupemail,
                "bankid'":ds[0].bankid,
                
                "result":"success",
                "error_message":"",
                "error_code":""
            }

        except Exception as e:
            mssg = "Get Prospect Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)
    
        return json.dumps(rspobj)         
        
        
    def delete_prospect(self,avars):
        auth  = current.auth
        db = self.db
    
        try:
    
            prospectid = int(common.getkeyvalue(avars,"prospectid",0))
    
            db(db.prospect.id == prospectid).update(\
                is_active = False,
                modified_on=common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id
    
            )
    
            rspobj = {
                'prospectid': prospectid,
                'result' : 'success',
                "error_code":"",
                "error_message":""
            }               
    
    
        except Exception as e:
            mssg = "Delete Clinict Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)
    
        return json.dumps(rspobj)         

    def update_prospect(self,avars):
        db = self.db
        auth  = current.auth
        rspobj = {}
        
        logger.loggerpms2.info("Enter Update Prospect ")
        
        try:
            prospectid = int(common.getkeyvalue(avars,'prospectid',"0"))
            ds = db((db.prospect.id == prospectid) & (db.prospect.is_active == True)).select()
            if(len(ds) != 1):
                rspobj = {
                            "prospectid":str(prospectid),
                            "result":"fail",
                            "error_message":"Error Updating Prospect - no clinic record",
                            "error_code":""
                          }                
                return json.dumps(rspobj)
                
            dts = common.getstringfromdate(ds[0].enrolleddate,"%d/%m/%Y")
            db(db.prospect.id == prospectid).update(\
                
                provider=common.getkeyvalue(avars,'provider',ds[0].provider),
                title=common.getkeyvalue(avars,'title',ds[0].title),
                providername=common.getkeyvalue(avars,'providername',ds[0].providername),
                practicename=common.getkeyvalue(avars,'practicename',ds[0].practicename),
                address1=common.getkeyvalue(avars,'address1',ds[0].address1),
                address2=common.getkeyvalue(avars,'address2',ds[0].address2),
                address3=common.getkeyvalue(avars,'address3',ds[0].address3),
                city=common.getkeyvalue(avars,'city',ds[0].city),
                st=common.getkeyvalue(avars,'st',ds[0].st),
                pin=common.getkeyvalue(avars,'pin',ds[0].pin),
                p_address1=common.getkeyvalue(avars,'p_address1',ds[0].p_address1),
                p_address2=common.getkeyvalue(avars,'p_address2',ds[0].p_address2),
                p_address3=common.getkeyvalue(avars,'p_address3',ds[0].p_address3),
                p_city=common.getkeyvalue(avars,'p_city',ds[0].p_city),
                p_st=common.getkeyvalue(avars,'p_st',ds[0].p_st),
                p_pin=common.getkeyvalue(avars,'p_pin',ds[0].p_pin),
                telephone=common.getkeyvalue(avars,'telephone',ds[0].telephone),
                cell=common.getkeyvalue(avars,'cell',ds[0].cell),
                fax=common.getkeyvalue(avars,'fax',ds[0].fax),
                email=common.getkeyvalue(avars,'email',ds[0].email),
                taxid=common.getkeyvalue(avars,'taxid',ds[0].taxid),
                enrolleddate=  common.getdatefromstring(common.getkeyvalue(avars,'enrolleddate',common.getstringfromdate(ds[0].enrolleddate,"%d/%m/%Y")),"%d/%m/%Y"),
                assignedpatientmembers=common.getkeyvalue(avars,'assignedpatientmembers',ds[0].assignedpatientmembers),
                captguarantee=common.getkeyvalue(avars,'captguarantee',ds[0].captguarantee),
                schedulecapitation=common.getkeyvalue(avars,'schedulecapitation',ds[0].schedulecapitation),
                capitationytd=common.getkeyvalue(avars,'capitationytd',ds[0].capitationytd),
                captiationmtd=common.getkeyvalue(avars,'captiationmtd',ds[0].captiationmtd),
                languagesspoken=common.getkeyvalue(avars,'languagesspoken',ds[0].languagesspoken),
                speciality=int(common.getkeyvalue(avars,'speciality',ds[0].speciality)),
                specialization=common.getkeyvalue(avars,'specialization',ds[0].specialization),
                sitekey=common.getkeyvalue(avars,'sitekey',ds[0].sitekey),
                groupregion=int(common.getkeyvalue(avars,'groupregion',ds[0].groupregion)),
                registration=common.getkeyvalue(avars,'registration',ds[0].registration),
                registered=common.getkeyvalue(avars,'registered',ds[0].registered),
                pa_providername=common.getkeyvalue(avars,'pa_providername',ds[0].pa_providername),
                pa_practicename=common.getkeyvalue(avars,'pa_practicename',ds[0].pa_practicename),
                pa_practiceaddress=common.getkeyvalue(avars,'pa_practiceaddress',ds[0].pa_practiceaddress),
                pa_dob=  common.getdatefromstring(common.getkeyvalue(avars,'pa_dob',common.getstringfromdate(ds[0].pa_dob,"%d/%m/%Y")),"%d/%m/%Y"),
                pa_parent=common.getkeyvalue(avars,'pa_parent',ds[0].pa_parent),
                pa_address=common.getkeyvalue(avars,'pa_address',ds[0].pa_address),
                pa_pan=common.getkeyvalue(avars,'pa_pan',ds[0].pa_pan),
                pa_regno=common.getkeyvalue(avars,'pa_regno',ds[0].pa_regno),
                pa_date=common.getkeyvalue(avars,'pa_date',ds[0].pa_date),
                pa_accepted=common.getkeyvalue(avars,'pa_accepted',ds[0].pa_accepted),
                pa_approved=common.getkeyvalue(avars,'pa_approved',ds[0].pa_approved),
                pa_approvedby=common.getkeyvalue(avars,'pa_approvedby',ds[0].pa_approvedby),
                pa_approvedon=  common.getdatefromstring(common.getkeyvalue(avars,'pa_approvedon',common.getstringfromdate(ds[0].pa_approvedon,"%d/%m/%Y")),"%d/%m/%Y"),
                pa_day=common.getkeyvalue(avars,'pa_day',ds[0].pa_day),
                pa_month=common.getkeyvalue(avars,'pa_month',ds[0].pa_month),
                pa_location=common.getkeyvalue(avars,'pa_location',ds[0].pa_location),
                pa_practicepin=common.getkeyvalue(avars,'pa_practicepin',ds[0].pa_practicepin),
                pa_hours=common.getkeyvalue(avars,'pa_hours',ds[0].pa_hours),
                pa_longitude=common.getkeyvalue(avars,'pa_longitude',ds[0].pa_longitude),
                pa_latitude=common.getkeyvalue(avars,'pa_latitude',ds[0].pa_latitude),
                pa_locationurl=common.getkeyvalue(avars,'pa_locationurl',ds[0].pa_locationurl),
                status = common.getkeyvalue(avars,'status',ds[0].status),
                groupsms=common.getkeyvalue(avars,'groupsms',ds[0].groupsms),
                groupemail=common.getkeyvalue(avars,'groupemail',ds[0].groupemail),
                bankid=common.getkeyvalue(avars,'groupemail',ds[0].bankid),
                
                modified_on=common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id
                
                )
            
            rspobj = {
                          "prospectid":str(prospectid),
                          "result":"success",
                          "error_message":"",
                          "error_code":""
                      }                        
        except Exception as e:
            mssg = "Update Prospect Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)
    
        return json.dumps(rspobj)            

    def new_prospect(self,avars):
        db = self.db
        auth  = current.auth
        rspobj = {}
        
        logger.loggerpms2.info("Enter new Propsect ")
        
        try:
            ref_code = common.getkeyvalue(avars,"ref_code","")     #Prospect is added by Agent
            ref_id = int(common.getkeyvalue(avars,"ref_id",0))            

            propsectid = db.prospect.insert(\
                
                
                provider=common.getkeyvalue(avars,'provider',""),
                title=common.getkeyvalue(avars,'title',""),
                providername=common.getkeyvalue(avars,'providername',""),
                practicename=common.getkeyvalue(avars,'practicename',""),
                address1=common.getkeyvalue(avars,'address1',""),
                address2=common.getkeyvalue(avars,'address2',""),
                address3=common.getkeyvalue(avars,'address3',""),
                city=common.getkeyvalue(avars,'city',""),
                st=common.getkeyvalue(avars,'st',""),
                pin=common.getkeyvalue(avars,'pin',""),
                p_address1=common.getkeyvalue(avars,'p_address1',""),
                p_address2=common.getkeyvalue(avars,'p_address2',""),
                p_address3=common.getkeyvalue(avars,'p_address3',""),
                p_city=common.getkeyvalue(avars,'p_city',""),
                p_st=common.getkeyvalue(avars,'p_st',""),
                p_pin=common.getkeyvalue(avars,'p_pin',""),
                telephone=common.getkeyvalue(avars,'telephone',""),
                cell=common.getkeyvalue(avars,'cell',""),
                email=common.getkeyvalue(avars,'email',""),
                
                
                
                taxid=common.getkeyvalue(avars,'taxid',""),

               
                speciality=int(common.getkeyvalue(avars,'speciality',"1")),
                specialization=common.getkeyvalue(avars,'specialization',""),
                sitekey=common.getkeyvalue(avars,'sitekey',""),
                groupregion=int(common.getkeyvalue(avars,'groupregion',"1")),
                registration=common.getkeyvalue(avars,'registration',""),
                registered=common.getboolean(common.getkeyvalue(avars,'registered',"True")),
                pa_providername=common.getkeyvalue(avars,'pa_providername',""),
                pa_practicename=common.getkeyvalue(avars,'pa_practicename',""),
                pa_practiceaddress=common.getkeyvalue(avars,'pa_practiceaddress',""),
                pa_dob=common.getdatefromstring(common.getkeyvalue(avars,'pa_dob',common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y")),"%d/%m/%Y"),
                pa_parent=common.getkeyvalue(avars,'pa_parent',""),
                pa_address=common.getkeyvalue(avars,'pa_address',""),
                pa_pan=common.getkeyvalue(avars,'pa_pan',""),
                pa_regno=common.getkeyvalue(avars,'pa_regno',""),
                pa_date=common.getdatefromstring(common.getkeyvalue(avars,'pa_date',common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y")),"%d/%m/%Y"),
                
                pa_accepted=common.getboolean(common.getkeyvalue(avars,'pa_accepted',"False")),
                pa_approved=common.getboolean(common.getkeyvalue(avars,'pa_approved',"False")),
                pa_approvedby=int(common.getkeyvalue(avars,'pa_approvedby',"1")),
                pa_approvedon=common.getdatefromstring(common.getkeyvalue(avars,'pa_approvedon',common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y")),"%d/%m/%Y"),
                pa_day=common.getkeyvalue(avars,'pa_day',""),
                pa_month=common.getkeyvalue(avars,'pa_month',""),
                pa_location=common.getkeyvalue(avars,'pa_location',""),
                pa_practicepin=common.getkeyvalue(avars,'pa_practicepin',""),
                pa_hours=common.getkeyvalue(avars,'pa_hours',""),
                pa_longitude=common.getkeyvalue(avars,'pa_longitude',""),
                pa_latitude=common.getkeyvalue(avars,'pa_latitude',""),
                pa_locationurl=common.getkeyvalue(avars,'pa_locationurl',""),
                groupsms=common.getboolean(common.getkeyvalue(avars,'groupsms',"True")),
                groupemail=common.getboolean(common.getkeyvalue(avars,'groupemail',"True")),
                status=common.getkeyvalue(avars,'status',"New"),

                is_active = True,
                created_on=common.getISTFormatCurrentLocatTime(),
                modified_on=common.getISTFormatCurrentLocatTime(),
                created_by = 1 if(auth.user == None) else auth.user.id,
                modified_by= 1 if(auth.user == None) else auth.user.id
                
            )
            #refcode = "AGN""
            db.prospect_ref.insert(prospect_id = propsectid, ref_code = ref_code,ref_id = ref_id)
                
            rspobj = {
                "ref_code":ref_code,
                "ref_id":ref_id,
                
                "prospectid":str(propsectid),
                
                "result":"success",
                "error_message":"",
                "error_code":""
            }            
        
        
        except Exception as e:
            mssg = "New Prospect Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)
    
        return json.dumps(rspobj)             
    
         
