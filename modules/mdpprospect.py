from gluon import current
import datetime

import json
import random
import string

from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger

from applications.my_pms2.modules import mdpprovider
from applications.my_pms2.modules import mdpclinic


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
               
                clinic_count = db((db.clinic_ref.ref_code == 'PST') & (db.clinic_ref.ref_id == d.prospect.id)).count()
                obj = {
                    "ref_code":d.prospect_ref.ref_code,   #AGN
                    "ref_id":d.prospect_ref.ref_id,       #ID to either AGent Table
                    
                    "prospectid":d.prospect.id,
                    "providername":d.prospect.providername,
                    "cell":d.prospect.cell,
                    "email":d.prospect.email,
                    "status":d.prospect.status,
                    "clinic_count":str(clinic_count)
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
        logger.loggerpms2.info("Enter get_prospect " + json.dumps(avars))
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
            
            
            
            clinic_count = db((db.clinic_ref.ref_code == 'PST') & (db.clinic_ref.ref_id == prospectid)).count()
            
            rspobj = {
                "prospectid":str(prospectid),
                "provider":ds[0].provider,
                "title":ds[0].title,
                "providername":ds[0].providername,
                "practicename":ds[0].practicename,
                "address1":ds[0].address1,
                "address2":ds[0].address2,
                "address3":ds[0].address3,
                "city":ds[0].city,
                "st":ds[0].st,
                "pin":ds[0].pin,
                "p_address1":ds[0].p_address1,
                "p_address2":ds[0].p_address2,
                "p_address3":ds[0].p_address3,
                "p_city":ds[0].p_city,
                "p_st":ds[0].p_st,
                "p_pin":ds[0].p_pin,
                "telephone":ds[0].telephone,
                "cell":ds[0].cell,
                "fax":ds[0].fax,
                "email":ds[0].email,
                "gender":ds[0].gender,
                "dob": common.getstringfromdate(ds[0].dob,"%d/%m/%Y"),
                "taxid":ds[0].taxid,
                "enrolleddate":common.getstringfromdate(ds[0].enrolleddate,"%d/%m/%Y"),
                "assignedpatientmembers":str(ds[0].assignedpatientmembers),
                "languagesspoken":ds[0].languagesspoken,
                "speciality":str(ds[0].speciality),
                "specialization":ds[0].specialization,
                "sitekey":ds[0].sitekey,
                "groupregion":str(ds[0].groupregion),
                "registration":ds[0].registration,
                "registered":ds[0].registered,
                "pa_providername":ds[0].pa_providername,
                "pa_practicename":ds[0].pa_practicename,
                "pa_practiceaddress":ds[0].pa_practiceaddress,
                "pa_dob":common.getstringfromdate(ds[0].pa_dob,"%d/%m/%Y"),
                "pa_parent":ds[0].pa_parent,
                "pa_address":ds[0].pa_address,
                "pa_pan":ds[0].pa_pan,
                "pa_regno":ds[0].pa_regno,
                "pa_date":common.getstringfromdate(ds[0].pa_date,"%d/%m/%Y"),
                "pa_accepted":ds[0].pa_accepted,
                "pa_approved":ds[0].pa_approved,
                "pa_approvedby":str(ds[0].pa_approvedby),
                "pa_approvedon":common.getstringfromdate(ds[0].pa_approvedon, "%d/%m/%Y"),
                "pa_day":ds[0].pa_day,
                "pa_month":ds[0].pa_month,
                "pa_location":ds[0].pa_location,
                "pa_practicepin":ds[0].pa_practicepin,
                "pa_hours":ds[0].pa_hours,
                "pa_longitude":ds[0].pa_longitude,
                "pa_latitude":ds[0].pa_latitude,
                "pa_locationurl":ds[0].pa_locationurl,
                "groupsms":ds[0].groupsms,
                "groupemail":ds[0].groupemail,
                "bankid":str(ds[0].bankid),
                
                "clinic_count":str(clinic_count),    
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
                gender = common.getkeyvalue(avars,"gender",ds[0].gender),
                dob = common.getdatefromstring(common.getkeyvalue(avars,"dob",common.getstringfromdate(ds[0].dob,"%d/%m/%Y")), "%d/%m/%Y"),
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
                bankid=common.getkeyvalue(avars,'bankid',ds[0].bankid),
                
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
     
        logger.loggerpms2.info("Enter new Propsect "  + json.dumps(avars))
        
        try:
            ref_code = common.getkeyvalue(avars,"ref_code","")     #Prospect is added by Agent
            ref_id = int(common.getkeyvalue(avars,"ref_id",0))            
            prospect = common.getkeyvalue(avars,'provider',"")

            address1=common.getkeyvalue(avars,'address1',"")
            address2=common.getkeyvalue(avars,'address2',"")
            address3=common.getkeyvalue(avars,'address3',"")
            city=common.getkeyvalue(avars,'city',"")
            st=common.getkeyvalue(avars,'st',"")
            pin=common.getkeyvalue(avars,'pin',"")
            cell = common.getkeyvalue(avars,"cell","")
            
            practiceaddress = ""
            practiceaddress = practiceaddress + "" if(address1 == "") else address1
            practiceaddress = practiceaddress + "" if(address2 == "") else practiceaddress + " " + address2
            practiceaddress = practiceaddress + "" if(address3 == "") else practiceaddress+ " " + address3
            practiceaddress = practiceaddress + "" if(city == "") else practiceaddress + "," + city
            practiceaddress = practiceaddress + "" if(st == "") else practiceaddress + "," + st
            practiceaddress = practiceaddress + "" if(pin == "") else practiceaddress + "," + pin
            
            sitekey = common.getkeyvalue(avars,'sitekey',"")
            if(common.getstring(sitekey) == ""):
                
                sitekey = ''
             
                for i in range(0,2):
                    sitekey += random.choice(string.lowercase)
                    sitekey += random.choice(string.uppercase)
                    sitekey += random.choice(string.digits)
                   
        
                               
            #check if prospect is already in the system
            #if it is there, then return the prospect
            #else create a new prospect
            r = db((db.prospect.cell == cell) & (db.prospect.is_active == True)).select()
            if(len(r)>1):
                i = 0
                #return error
                mssg = "More than 1 Prospect with the same cell number: " + cell
                logger.loggerpms2.info(mssg)      
                excpobj = {}
                excpobj["result"] = "fail"
                excpobj["error_code"] = "MDP100"
                excpobj["error_message"] = mssg
                return json.dumps(excpobj)                
            
            if(len(r)==1):
                prospectid = int(common.getid(r[0].id))
               
               
                p = db(db.prospect_ref.prospect_id ==prospectid).select()
                ref_code = p[0].ref_code if len(p) == 1 else ""
                ref_id = int(p[0].ref_id) if len(p) == 1 else 0
                
                reqobj = {
                    "ref_code":"PST",
                    "ref_id":str(prospectid)
                }
                            
                clinicobj = mdpclinic.Clinic(db)
                obj = json.loads(clinicobj.list_clinic(json.dumps(reqobj)))
                
                count = 0
                if(obj["result"] == "success"):
                    count = int(common.getid(obj["count"]))
                
                rspobj = {
                        "ref_code":ref_code,
                        "ref_id":ref_id,
                        
                        "prospectid":str(prospectid),
                        "clinic_count":str(count),
                        "result":"success",
                        "error_message":"",
                        "error_code":""
                    }
                
                return json.dumps(rspobj)
                
                
            
            #create a new prospect
            prospectid = db.prospect.insert(\
                
                
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
                p_address1=common.getkeyvalue(avars,'p_address1',address1),
                p_address2=common.getkeyvalue(avars,'p_address2',address2),
                p_address3=common.getkeyvalue(avars,'p_address3',address3),
                p_city=common.getkeyvalue(avars,'p_city',city),
                p_st=common.getkeyvalue(avars,'p_st',st),
                p_pin=common.getkeyvalue(avars,'p_pin',pin),
                telephone=common.getkeyvalue(avars,'telephone',""),
                cell=common.getkeyvalue(avars,'cell',""),
                email=common.getkeyvalue(avars,'email',""),
                fax=common.getkeyvalue(avars,'fax',""),
                gender = common.getkeyvalue(avars,'gender',"Male"),
                dob = common.getdatefromstring(common.getkeyvalue(avars,"dob","01/01/1990"), "%d/%m/%Y"),
                
                taxid=common.getkeyvalue(avars,'taxid',""),

                
                assignedpatientmembers=int(common.getkeyvalue(avars,'assignedpatientmembers',"0")),
                speciality=int(common.getkeyvalue(avars,'speciality',"1")),
                specialization=common.getkeyvalue(avars,'specialization',""),
                sitekey=sitekey,
                groupregion=int(common.getkeyvalue(avars,'groupregion',"1")),
                registration=common.getkeyvalue(avars,'registration',""),
                registered=common.getboolean(common.getkeyvalue(avars,'registered',"True")),
                languagesspoken=common.getkeyvalue(avars,'languagesspoken',"English"),
                pa_providername=common.getkeyvalue(avars,'pa_providername',common.getkeyvalue(avars,'providername',"")),
                pa_practicename=common.getkeyvalue(avars,'pa_practicename',common.getkeyvalue(avars,'practicename',"")),
                pa_practiceaddress=common.getkeyvalue(avars,'pa_practiceaddress',practiceaddress),
                pa_dob=common.getdatefromstring(common.getkeyvalue(avars,'pa_dob',common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y")),"%d/%m/%Y"),
                pa_parent=common.getkeyvalue(avars,'pa_parent',""),
                pa_address=common.getkeyvalue(avars,'pa_address',practiceaddress),
                pa_pan=common.getkeyvalue(avars,'pa_pan',""),
                pa_regno=common.getkeyvalue(avars,'pa_regno',""),
                pa_date=common.getdatefromstring(common.getkeyvalue(avars,'pa_date',common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y")),"%d/%m/%Y"),
                
                pa_accepted=common.getboolean(common.getkeyvalue(avars,'pa_accepted',"False")),
                pa_approved=common.getboolean(common.getkeyvalue(avars,'pa_approved',"False")),
                pa_approvedby=int(common.getkeyvalue(avars,'pa_approvedby',"1")),
                pa_approvedon=common.getdatefromstring(common.getkeyvalue(avars,'pa_approvedon',common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y")),"%d/%m/%Y"),
                pa_day=common.getkeyvalue(avars,'pa_day',""),
                pa_month=common.getkeyvalue(avars,'pa_month',""),
                pa_location=common.getkeyvalue(avars,'pa_location',common.getkeyvalue(avars,'city',"")),
                pa_practicepin=common.getkeyvalue(avars,'pa_practicepin',""),
                pa_hours=common.getkeyvalue(avars,'pa_hours',""),
                pa_longitude=common.getkeyvalue(avars,'pa_longitude',""),
                pa_latitude=common.getkeyvalue(avars,'pa_latitude',""),
                pa_locationurl=common.getkeyvalue(avars,'pa_locationurl',""),
                groupsms=common.getboolean(common.getkeyvalue(avars,'groupsms',"True")),
                groupemail=common.getboolean(common.getkeyvalue(avars,'groupemail',"True")),
                status=common.getkeyvalue(avars,'status',"New"),
                bankid = 0,
                captguarantee = 0 ,
                schedulecapitation = 0,
                capitationytd  = 0,
                captiationmtd  = 0,
                
               

                is_active = True,
                created_on=common.getISTFormatCurrentLocatTime(),
                modified_on=common.getISTFormatCurrentLocatTime(),
                created_by = 1 if(auth.user == None) else auth.user.id,
                modified_by= 1 if(auth.user == None) else auth.user.id
                
            )
            
            if(prospect == ""):
                prospect = "PR" + str(prospectid).zfill(4)
                db(db.prospect.id == prospectid).update(provider = prospect)
            
            
                
            #refcode = "AGN""
            db.prospect_ref.insert(prospect_id = prospectid, ref_code = ref_code,ref_id = ref_id)
                
            rspobj = {
                "ref_code":ref_code,
                "ref_id":ref_id,
                
                "prospectid":str(prospectid),
                "clinic_count":"0",
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
    
        logger.loggerpms2.info("Exit New_Prospect " + json.dumps(rspobj))
        return json.dumps(rspobj)             
    

    def approve_prospect(self,avars):
        auth  = current.auth
        db = self.db
    
        try:
            prospectid = common.getkeyvalue(avars,"prospectid","0")
            #change prospect status to 'Enrolled'
            db((db.prospect.id == prospectid) & (db.prospect.is_active == True)).update(\
                pa_approved = True,
                pa_approvedon = common.getISTFormatCurrentLocatTime(),
                pa_approvedby = 1 if(auth.user == None) else auth.user.id,
                pa_accepted = True,
                status = "Approved",
                
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
            mssg = "Prospect Approval Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)
    
        return json.dumps(rspobj)    
    
    def enroll_prospect(self,avars):
        logger.loggerpms2.info("Enter Enroll Prospect - Module")
        auth  = current.auth
        db = self.db
    
        try:
    
            #create provider for this prospect
            prospectid = common.getkeyvalue(avars,"prospectid","0")
            
            
            #create a new provider
            prv = mdpprovider.Provider(db, 0)
            prvobj = json.loads(prv.new_provider(avars))
            providerid = common.getkeyvalue(prvobj,"providerid","0")
            db(db.prospect_ref.prospect_id == prospectid).update(provider_id = providerid)
            
            #create prospect to provider image_ref records for this provider corresponding to the 'Prospect' images
            ds = db((db.dentalimage_ref.ref_code == "PST") & (db.dentalimage_ref.ref_id == prospectid)).select()
            for d in ds:
                xid = db.dentalimage_ref.insert(\
                    ref_code = "PRV",
                    ref_id = providerid,
                    media_id = d.media_id
                )
            
            
            #copy prospect to provider clinic_ref records
            ds = db((db.clinic_ref.ref_code == "PST") & (db.clinic_ref.ref_id == prospectid)).select()
            for d in ds:
                
                db.clinic_ref.update_or_insert((ref_code == "PRV") & (clinic_id == d.clinic_id),
                                               ref_code = "PRV",
                                               ref_id = providerid,
                                               clinic_id = d.clinic_id
                                            )
                        
                #xid = db.clinic_ref.insert(\
                    #ref_code = "PRV",
                    #ref_id = providerid,
                    #clinic_id = d.clinic_id
                #)
            
            
            #copy propsect doctors to provider
            ds = db((db.doctor_ref.ref_code == "PST") & (db.doctor_ref.ref_id == prospectid)).select()
            for d in ds:
                xid = db.doctor_ref.insert(\
                    ref_code = "PRV",
                    ref_id = providerid,
                    doctor_id = d.doctor_id
                )
            
            #change prospect status to 'Enrolled'
            db((db.prospect.id == prospectid) & (db.prospect.is_active == True)).update(
                status = "Enrolled",
                modified_on=common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id
            )
                
                
            db((db.provider.id == providerid) & (db.provider.is_active == True)).update(
                pa_approved = True,
                pa_approvedon = common.getISTFormatCurrentLocatTime(),
                pa_approvedby = 1 if(auth.user == None) else auth.user.id,
                pa_accepted = True,
                status = "Enrolled"                
            )
                
                                                    
            
    
            rspobj = {
                'prospectid': prospectid,
                'providerid':providerid,
                'result' : 'success',
                "error_code":"",
                "error_message":""
            }               
    
    
        except Exception as e:
            mssg = "Enroll Prospect Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)
    
        return json.dumps(rspobj)    