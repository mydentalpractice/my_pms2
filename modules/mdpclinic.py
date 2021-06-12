from gluon import current
import datetime

import json

from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger


class Clinic:
    def __init__(self,db):
        self.db = db
        
    
    def remove_doc_clinic(self,avars)    :
        auth  = current.auth
        db = self.db        
        
        try:
            clinicid = int(common.getkeyvalue(avars,"clinicid",0))
            ref_id = int(common.getkeyvalue(avars,"docid",0))
            ref_code = common.getkeyvalue(avars,"ref_code","")
            
            db((db.clinic_ref.ref_id == ref_id) & (db.clinic_ref.ref_code == ref_code)& (db.clinic_ref.clinic_id == clinicid)).delete()
            
            rspobj = {
                "clinicid":str(clinicid),
                "ref_code":ref_code,
                "ref_id":str(ref_id),
                "result":"success",
                "error_message":"",
                "error_code":""
            }      
            
        except Exception as e:
            mssg = "Remove Clinic Doctor Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)  
        
        return json.dumps(rspobj)  
        
   
   
    
   
   
    def list_clinic(self,avars):
        auth  = current.auth
        db = self.db        
      
        
        cliniclist = []
        rspobj = {}
        urlprops = db(db.urlproperties.id >0 ).select()
        
        try:
            
            ref_code = common.getkeyvalue(avars,"ref_code","PRV")
            ref_id = common.getkeyvalue(avars,"ref_id",0)
            
            ds = db((db.clinic_ref.ref_id == ref_id) & (db.clinic_ref.ref_code == ref_code)).select()
            
            logger.loggerpms2.info("Number of clinics  = " + str(len(ds)) + " " + ref_code + " " + str(ref_id))
            
            for d in ds:
                r = db((db.clinic.id == d.clinic_id) & (db.clinic.is_active == True)).select()
                if(len(r)!=1):
                    continue
                
                p = db((db.dentalimage_ref.ref_code == "CLN") & (db.dentalimage_ref.ref_id == d.clinic_id)).select()
                mediaid = 0 if(len(p) == 0) else int(common.getid(p[0].media_id))
                md = db((db.dentalimage.id == mediaid) & (db.dentalimage.is_active == True)).select()
                dobj = {
                    
                    "ref_code":ref_code,
                    "name":r[0].name if len(r) == 1 else "",
                    "city":r[0].city if len(r) == 1 else "",
                    "pin":r[0].pin if len(r) == 1 else "",
                    "status":r[0].status if len(r) == 1 else "",
                    "clinic":r[0].clinic_ref if len(r) == 1 else "",
                    "clinicid":r[0].id if len(r) == 1 else 0,
                    "cell":r[0].cell if len(r) == 1 else "",
                    "email":r[0].email if len(r) == 1 else "",
                    "primary_clinic":r[0].primary_clinic if len(r) == 1 else False,
                    "mediaurl" : urlprops[0].mydp_ipaddress + "/my_dentalplan/media/media_download/" + str(mediaid),
                    "media"  : "" if(len(md) == 0) else  common.getstring(md[0].image),
                    "uploadfolder":"" if(len(md) == 0) else common.getstring(md[0].uploadfolder),
                    "title":"" if(len(md) == 0) else common.getstring(md[0].title),
                    "imagedate":"00/00/00" if(len(md) == 0) else common.getstringfromdate(md[0].imagedate,"%d/%m/%Y"),
                    "longitude":r[0].longitude if len(r) == 1 else "",
                    "latitude":r[0].latitude if len(r) == 1 else "",
                    
                }
                cliniclist.append(dobj)
            
          
            
            rspobj = {
                
                "count":str(len(cliniclist)),
                "clinic_list":cliniclist,
                "result":"success",
                "error_message":"",
                "error_code":""
            }
                    
        
        except Exception as e:
            mssg = "List Clinic Doctor Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)  
        
        return json.dumps(rspobj)    

    def list_doc_clinic(self,avars):
        auth  = current.auth
        db = self.db        
      
        
        doclist = []
        rspobj = {}
        
        try:
            clinicid = int(common.getkeyvalue(avars,"clinicid",0))
            ref_code = common.getkeyvalue(avars,"ref_code","DOC")
            
            ds = db((db.clinic_ref.clinic_id == clinicid) & (db.clinic_ref.ref_code == ref_code)).select()
            

            for d in ds:
                r = db((db.clinic.id == d.clinic_id) & (db.clinic.is_active == True)).select()
                if(len(r) != 1):
                    continue
                
                x = db((db.doctor.id == d.ref_id) & (db.doctor.is_active == True)).select(db.doctor.id,db.doctor.name)
                if(len(x) != 1):
                    continue
                
                dobj = {
                    
                    "clinic":r[0].clinic_ref if len(r) == 1 else "",
                    "doctor":x[0].name if len(x) == 1 else "",
                    "clinicid":r[0].id if len(r) == 1 else 0,
                    "doctorid":x[0].id if len(x) == 1 else 0
                }
                doclist.append(dobj)
            
          
            
            rspobj = {
                
                "count":str(len(ds)),
                "doclist":doclist,
                "result":"success",
                "error_message":"",
                "error_code":""
            }
                    
        
        except Exception as e:
            mssg = "List Clinic Doctor Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)  
        
        return json.dumps(rspobj)
        
    def add_doc_clinic(self,avars):
        auth  = current.auth
        db = self.db        
        rspobj = None
        
        try:
            clinicid = int(common.getkeyvalue(avars,"clinicid",0))
            ref_id = int(common.getkeyvalue(avars,"docid",0))
            ref_code = "DOC"
            
            clinic_ref_id = db.clinic_ref.insert(\
                ref_code = ref_code,
                ref_id = ref_id,
                clinic_id = clinicid
            )
            
            rspobj = {
                
                "clinicid":str(clinicid),
                "ref_code":ref_code,
                "docid":str(ref_id),
                "result":"success",
                "error_message":"",
                "error_code":""
            }
                    
        
        except Exception as e:
            mssg = "Add Doctor Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)  
        
        return json.dumps(rspobj)
    
    
    def xlist_clinic(self,avars):
        auth  = current.auth
        db = self.db
        
        try:
            
            ref_code = avars["ref_code"] if "ref_code" in avars else ""
            ref_id = int(common.getid(avars["ref_id"])) if "ref_id" in avars else 0            
            
            clnlist = []
            clnobj = {}
            
            rspobj = {}
            
            clns = None
            if(ref_code == ""):
                if(ref_id == 0):
                    clns = db((db.clinic.is_active == True)).select(db.clinic.ALL,db.clinic_ref.ALL,\
                                                                                        left=db.clinic.on((db.clinic.id == db.clinic_ref.clinic_id)),)
                else:
                    clns = db((db.clinic_ref.ref_id == ref_id) &  (db.clinic.is_active == True)).select(db.clinic.ALL,db.clinic_ref.ALL,\
                                                                                        left=db.clinic.on((db.clinic.id == db.clinic_ref.clinic_id)))
                    
            else:
                if(ref_id == 0):
                    clns = db((db.clinic_ref.ref_code==ref_code)&  (db.clinic.is_active == True)).select(db.clinic.ALL,db.clinic_ref.ALL,\
                                                                                        left=db.clinic.on((db.clinic.id == db.clinic_ref.clinic_id)))
                else:
                    clns = db((db.clinic_ref.ref_code==ref_code)&(db.clinic_ref.ref_id == ref_id) &  (db.clinic.is_active == True)).select(db.clinic.ALL,db.clinic_ref.ALL,\
                                                                                        left=db.clinic.on((db.clinic.id == db.clinic_ref.clinic_id)))
                
            
            owner = ""
            for cln in clns:
               
                if(ref_code == "PRV"):
                    r = db(db.provider.id == ref_id).select(db.provider.provider)
                    if(common.getboolean(cln.clinic.primary_clinic) == True):
                        owner = r[0].provider if len(r) == 1 else ""
                    
                clnobj = {
                    "ref_code":cln.clinic_ref.ref_code,   #DOC or PRV
                    "ref_id":cln.clinic_ref.ref_id,       #ID to either doctor table or provider table
                    
                    "clinic_ref":cln.clinic.clinic_ref,
                    "name":cln.clinic.name,
                    "cell":cln.clinic.cell,
                    "email":cln.clinic.email,
                    "primary_clinic":str(cln.clinic.primary_clinic),
                    "status":cln.clinic.status,
                    "owner": owner
                }
                clnlist.append(clnobj)   
             
            
        except Exception as e:
            mssg = "list Clinic Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)
        
        return json.dumps({"result":"success","error_code":"","error_message":"","clinic_count":len(clns), "owner":owner, "clinic_list":clnlist})            
    
    
    def get_clinic(self,avars):
        db = self.db
        auth  = current.auth
        rspobj = {}
        owner = ""
        urlprops = db(db.urlproperties.id >0 ).select()
        try:
            clinicid = int(common.getkeyvalue(avars,"clinicid",0))
            r = db(db.clinic_ref.clinic_id ==clinicid).select()
            ref_code = r[0].ref_code if len(r) == 1 else ""
            ref_id = int(r[0].ref_id) if len(r) == 1 else 0
            ds = db((db.clinic.id == clinicid) & (db.clinic.is_active == True)).select()
            
            p = db((db.dentalimage_ref.ref_code == "CLN") & (db.dentalimage_ref.ref_id == clinicid)).select()
            mediaid = 0 if(len(p) == 0) else int(common.getid(p[0].media_id))
            md = db((db.dentalimage.id == mediaid) & (db.dentalimage.is_active == True)).select()            
            
                   

            if(len(ds) != 1):
                rspobj = {
                    
                    "clinicid":str(clinicid),
                    "result":"fail",
                    "error_message":"Error Getting Clinic Details - no or duplicate record",
                    "error_code":""
                }                
                return json.dumps(rspobj)
            
            if((ref_code == "PRV")):
                r = db(db.provider.id == ref_id).select(db.provider.provider)
                if(common.getboolean(ds[0].primary_clinic) == True):
                    owner = r[0].provider if len(r) == 1 else "" 
                
            rspobj = {
                "clinincid":str(clinicid),
                "bank_id":str(ds[0].bank_id),
                "clinic_ref":ds[0].clinic_ref,            

                "mediaurl" : urlprops[0].mydp_ipaddress + "/my_dentalplan/media/media_download/" + str(mediaid),
                "media"  : "" if(len(md) == 0) else  common.getstring(md[0].image),
                "uploadfolder":"" if(len(md) == 0) else common.getstring(md[0].uploadfolder),
                "title":"" if(len(md) == 0) else common.getstring(md[0].title),
                "imagedate":"00/00/00" if(len(md) == 0) else common.getstringfromdate(md[0].imagedate,"%d/%m/%Y"),
                
                
                "name":ds[0].name,            
                "address1":ds[0].address1,            
                "address2":ds[0].address2,            
                "address3":ds[0].address3,
                "city":ds[0].city,
                "st":ds[0].st,
                "pin":ds[0].pin,
                
                "cell":ds[0].cell,            
                "telephone":ds[0].telephone,            
                "email":ds[0].email,            
                "website":ds[0].website,            
                "gps_location":ds[0].gps_location, 
                "longitude":ds[0].longitude,
                "latitude":ds[0].latitude,
                
                "whatsapp":ds[0].whatsapp,            
                "facebook":ds[0].facebook,            
                "twitter":ds[0].twitter,            
                "primary_clinic": str(ds[0].primary_clinic),            
                "dentalchairs":ds[0].dentalchairs,            
                "auto_clave":ds[0].auto_clave,            
                "implantology":ds[0].implantology,            
                "instrument_sterilization":ds[0].instrument_sterilization,            
                "waste_displosal":ds[0].waste_displosal,            
                "suction_machine":ds[0].suction_machine,            
                "laser":ds[0].laser,            
                "RVG_OPG":ds[0].RVG_OPG,            
                "radiation_protection":ds[0].radiation_protection,            
                "computers":ds[0].computers,            
                "network":ds[0].network,            
                "internet":ds[0].internet,            
                "air_conditioned":ds[0].air_conditioned,            
                "waiting_area":ds[0].waiting_area,            
                "backup_power":ds[0].backup_power,            
                "toilet":ds[0].toilet,            
                "water_filter":ds[0].water_filter,            
                "parking_facility":ds[0].parking_facility,            
                "receptionist":ds[0].receptionist,            
                "credit_card":ds[0].credit_card,            
                "certifcates":ds[0].certifcates,            
                "emergency_drugs":ds[0].emergency_drugs,            
                "infection_control":ds[0].infection_control,            
                "daily_autoclaved":ds[0].daily_autoclaved,            
                "patient_records":ds[0].patient_records,            
                "patient_consent":ds[0].patient_consent,            
                "patient_traffic":ds[0].patient_traffic,            
                "nabh_iso_certifcation":ds[0].nabh_iso_certifcation,            
                "mdp_registration":ds[0].mdp_registration,            
                "intra_oral_camera":ds[0].intra_oral_camera,            
                "rotary_endodontics":ds[0].rotary_endodontics,            
                "status":ds[0].status,   
                "owner":owner,
                "notes":ds[0].notes,
                "registration_certificate":ds[0].registration_certificate,
                "state_dental_registration":ds[0].state_dental_registration,
                "result":"success",
                "error_message":"",
                "error_code":""
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
        
        
    def delete_clinic(self,avars):
        auth  = current.auth
        db = self.db
    
        try:
    
            clinicid = int(common.getkeyvalue(avars,"clinicid",0))
    
            db(db.clinic.id == clinicid).update(\
                is_active = False,
                modified_on=common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id
    
            )
    
            rspobj = {
                'clinicid': clinicid,
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

    def update_clinic(self,avars):
        db = self.db
        auth  = current.auth
        rspobj = {}
        
        logger.loggerpms2.info("Enter new Clinic ")
        
        try:
            clinicid = int(common.getkeyvalue(avars,'clinicid',"0"))
            ds = db((db.clinic.id == clinicid) & (db.clinic.is_active == True)).select()
            if(len(ds) != 1):
                rspobj = {
                            "clinicid":str(clinicid),
                            "result":"fail",
                            "error_message":"Error Updating Clinic - no clinic record",
                            "error_code":""
                          }                
                return json.dumps(rspobj)
                
            
            db(db.clinic.id == clinicid).update(\
                
                clinic_ref = common.getkeyvalue(avars,'clinic_ref',ds[0].clinic_ref),
                name = common.getkeyvalue(avars,'name',ds[0].name),
                address1 = common.getkeyvalue(avars,'address1',ds[0].address1),
                address2 = common.getkeyvalue(avars,'address2',ds[0].address2),
                address3 = common.getkeyvalue(avars,'address3',ds[0].address3),
                city = common.getkeyvalue(avars,'city',ds[0].city),
                st = common.getkeyvalue(avars,'st',ds[0].st),
                pin = common.getkeyvalue(avars,'pin',ds[0].pin),
                cell = common.getkeyvalue(avars,'cell',ds[0].cell),
                telephone = common.getkeyvalue(avars,'telephone',ds[0].telephone),
                email = common.getkeyvalue(avars,'email',ds[0].email),
                status = common.getkeyvalue(avars,'status',ds[0].status),
                website = common.getkeyvalue(avars,'website',ds[0].website),
                gps_location = common.getkeyvalue(avars,'gps_location',ds[0].gps_location),
                longitude = common.getkeyvalue(avars,'longitude',ds[0].longitude),
                latitude = common.getkeyvalue(avars,'latitude',ds[0].latitude),
                whatsapp = common.getkeyvalue(avars,'whatsapp',ds[0].whatsapp),
                facebook = common.getkeyvalue(avars,'facebook',ds[0].facebook),
                twitter = common.getkeyvalue(avars,'twitter',ds[0].twitter),
                primary_clinic = common.getboolean(common.getkeyvalue(avars,'primary',ds[0].primary_clinic)),
                dentalchairs = common.getkeyvalue(avars,'dentalchairs',ds[0].dentalchairs),
                auto_clave = common.getkeyvalue(avars,'auto_clave',ds[0].auto_clave),
                implantology = common.getkeyvalue(avars,'implantology',ds[0].implantology),
                instrument_sterilization = common.getkeyvalue(avars,'instrument_sterilization',ds[0].instrument_sterilization),
                waste_displosal = common.getkeyvalue(avars,'waste_displosal',ds[0].waste_displosal),
                suction_machine = common.getkeyvalue(avars,'suction_machine',ds[0].suction_machine),
                laser = common.getkeyvalue(avars,'laser',ds[0].laser),
                RVG_OPG = common.getkeyvalue(avars,'RVG_OPG',ds[0].RVG_OPG),
                radiation_protection = common.getkeyvalue(avars,'radiation_protection',ds[0].radiation_protection),
                computers = common.getkeyvalue(avars,'computers',ds[0].computers),
                network = common.getkeyvalue(avars,'network',ds[0].network),
                internet = common.getkeyvalue(avars,'internet',ds[0].internet),
                air_conditioned = common.getkeyvalue(avars,'air_conditioned',ds[0].air_conditioned),
                waiting_area = common.getkeyvalue(avars,'waiting_area',ds[0].waiting_area),
                backup_power = common.getkeyvalue(avars,'backup_power',ds[0].backup_power),
                toilet = common.getkeyvalue(avars,'toilet',ds[0].toilet),
                water_filter = common.getkeyvalue(avars,'water_filter',ds[0].water_filter),
                parking_facility = common.getkeyvalue(avars,'parking_facility',ds[0].parking_facility),
                receptionist = common.getkeyvalue(avars,'receptionist',ds[0].receptionist),
                credit_card = common.getkeyvalue(avars,'credit_card',ds[0].credit_card),
                
                certifcates = common.getkeyvalue(avars,'certifcates',ds[0].certifcates),
                emergency_drugs = common.getkeyvalue(avars,'emergency_drugs',ds[0].emergency_drugs),
                infection_control = common.getkeyvalue(avars,'infection_control',ds[0].infection_control),
                daily_autoclaved = common.getkeyvalue(avars,'daily_autoclaved',ds[0].daily_autoclaved),
                patient_records = common.getkeyvalue(avars,'patient_records',ds[0].patient_records),
               
                patient_consent = common.getkeyvalue(avars,'patient_consent',ds[0].patient_consent),
                patient_traffic = common.getkeyvalue(avars,'patient_traffic',ds[0].patient_traffic),
                nabh_iso_certifcation = common.getkeyvalue(avars,'nabh_iso_certifcation',ds[0].nabh_iso_certifcation),
                mdp_registration = common.getkeyvalue(avars,'mdp_registration',ds[0].mdp_registration),

                intra_oral_camera = common.getkeyvalue(avars,'intra_oral_camera',ds[0].intra_oral_camera),
                rotary_endodontics = common.getkeyvalue(avars,'rotary_endodontics',ds[0].rotary_endodontics),
                
                
                bank_id = common.getkeyvalue(avars,"bankid",ds[0].bank_id),
                
                notes = common.getkeyvalue(avars,'notes',ds[0].notes),
                
                state_dental_registration = common.getkeyvalue(avars,"state_dental_registration",ds[0].state_dental_registration),
                registration_certificate =  common.getkeyvalue(avars,"registration_certificate",ds[0].registration_certificate),                

                
                modified_on=common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id
                )
            
            rspobj = {
                          "clinicid":str(clinicid),
                          "result":"success",
                          "error_message":"",
                          "error_code":""
                      }                        
        except Exception as e:
            mssg = "New Clinic Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)
    
        return json.dumps(rspobj)            

    def new_clinic(self,avars):
        db = self.db
        auth  = current.auth
        rspobj = {}
        
        logger.loggerpms2.info("Enter new Clinic " + json.dumps(avars))
        
        try:
            ref_code = common.getkeyvalue(avars,"ref_code","")
            ref_id = int(common.getkeyvalue(avars,"ref_id",0))            
            
            #check if there is a primary clinic for this ref_code, if so, then default others to non-primary clinic
            r = db((db.clinic_ref.ref_code == ref_code) & (db.clinic_ref.ref_id == ref_id) & (db.clinic.primary_clinic == True)& (db.clinic.primary_clinic == True)).select(db.clinic.ALL,left=db.clinic.on(db.clinic.id == db.clinic_ref.clinic_id))
            primary_clinic = False if(len(r)>=1) else True

            clinicid = db.clinic.insert(\
                
                name = common.getkeyvalue(avars,'name',""),
                address1 = common.getkeyvalue(avars,'address1',""),
                address2 = common.getkeyvalue(avars,'address2',""),
                address3 = common.getkeyvalue(avars,'address3',""),
                city = common.getkeyvalue(avars,'city',""),
                st = common.getkeyvalue(avars,'st',""),
                pin = common.getkeyvalue(avars,'pin',""),
                cell = common.getkeyvalue(avars,'cell',""),
                telephone = common.getkeyvalue(avars,'telephone',""),
                email = common.getkeyvalue(avars,'email',""),
                status = common.getkeyvalue(avars,'status',""),
                website = common.getkeyvalue(avars,'website',""),
                gps_location = common.getkeyvalue(avars,'gps_location',""),
                longitude = common.getkeyvalue(avars,'longitude',""),
                latitude = common.getkeyvalue(avars,'latitude',""),
                
                whatsapp = common.getkeyvalue(avars,'whatsapp',""),
                facebook = common.getkeyvalue(avars,'facebook',""),
                twitter = common.getkeyvalue(avars,'twitter',""),
                primary_clinic = common.getboolean(common.getkeyvalue(avars,'primary',primary_clinic)),
                dentalchairs = common.getkeyvalue(avars,'dentalchairs',""),
                auto_clave = common.getkeyvalue(avars,'auto_clave',""),
                implantology = common.getkeyvalue(avars,'implantology',""),
                instrument_sterilization = common.getkeyvalue(avars,'instrument_sterilization',""),
                waste_displosal = common.getkeyvalue(avars,'waste_displosal',""),
                suction_machine = common.getkeyvalue(avars,'suction_machine',""),
                laser = common.getkeyvalue(avars,'laser',""),
                RVG_OPG = common.getkeyvalue(avars,'RVG_OPG',""),
                radiation_protection = common.getkeyvalue(avars,'radiation_protection',""),
                computers = common.getkeyvalue(avars,'computers',""),
                network = common.getkeyvalue(avars,'network',""),
                internet = common.getkeyvalue(avars,'internet',""),
                air_conditioned = common.getkeyvalue(avars,'air_conditioned',""),
                waiting_area = common.getkeyvalue(avars,'waiting_area',""),
                backup_power = common.getkeyvalue(avars,'backup_power',""),
                toilet = common.getkeyvalue(avars,'toilet',""),
                water_filter = common.getkeyvalue(avars,'water_filter',""),
                parking_facility = common.getkeyvalue(avars,'parking_facility',""),
                receptionist = common.getkeyvalue(avars,'receptionist',""),
                credit_card = common.getkeyvalue(avars,'credit_card',""),
                
                certifcates = common.getkeyvalue(avars,'certifcates',""),
                emergency_drugs = common.getkeyvalue(avars,'emergency_drugs',""),
                infection_control = common.getkeyvalue(avars,'infection_control',""),
                daily_autoclaved = common.getkeyvalue(avars,'daily_autoclaved',""),
                patient_records = common.getkeyvalue(avars,'patient_records',""),
               
                patient_consent = common.getkeyvalue(avars,'patient_consent',""),
                patient_traffic = common.getkeyvalue(avars,'patient_traffic',""),
                nabh_iso_certifcation = common.getkeyvalue(avars,'nabh_iso_certifcation',""),
                mdp_registration = common.getkeyvalue(avars,'mdp_registration',""),

                intra_oral_camera = common.getkeyvalue(avars,'intra_oral_camera',""),
                rotary_endodontics = common.getkeyvalue(avars,'rotary_endodontics',""),
                
                bank_id = common.getkeyvalue(avars,"bank_id",None),
                
                notes = common.getkeyvalue(avars,"notes",None),
                
                state_dental_registration = common.getkeyvalue(avars,"state_dental_registration",None),
                registration_certificate =  common.getkeyvalue(avars,"registration_certificate",None),
                
                is_active = True,
                created_on=common.getISTFormatCurrentLocatTime(),
                modified_on=common.getISTFormatCurrentLocatTime(),
                created_by = 1 if(auth.user == None) else auth.user.id,
                modified_by= 1 if(auth.user == None) else auth.user.id
                
            )
            
            clinic_ref = common.getkeyvalue(avars,'clinic_ref',"CLN" + str(clinicid).zfill(4))
            db(db.clinic.id == clinicid).update(clinic_ref = clinic_ref)
            
            #refcode = "DOC","PROV"
            
            db.clinic_ref.insert(clinic_id = clinicid, ref_code = ref_code,ref_id = ref_id)
                
            rspobj = {
                "ref_code":ref_code,
                "ref_id":ref_id,
                
                "clinicid":str(clinicid),
                "clinic_ref":clinic_ref,
                "result":"success",
                "error_message":"",
                "error_code":""
            }            
        
        except Exception as e:
            mssg = "New Clinic Exception:\n" + str(e)
            logger.loggerpms2.info(mssg)      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = mssg
            return json.dumps(excpobj)

        logger.loggerpms2.info("Exit new_clinic " + json.dumps(rspobj))
        return json.dumps(rspobj)             
    
         
