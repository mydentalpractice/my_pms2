from gluon import current
import datetime

import json

from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger


class Clinic:
    def __init__(self,db):
        self.db = db
    
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
                
                clinic_ref = common.getkeyvalue(avars,'clinic_ref',ds[0].clinicref),
                name = common.getkeyvalue(avars,'name',ds[0].name),
                address1 = common.getkeyvalue(avars,'address1',ds[0].address1),
                address2 = common.getkeyvalue(avars,'address1',ds[0].address2),
                address3 = common.getkeyvalue(avars,'address3',ds[0].address3),
                city = common.getkeyvalue(avars,'city',ds[0].city),
                st = common.getkeyvalue(avars,'st',ds[0].st),
                pin = common.getkeyvalue(avars,'pin',ds[0].pin),
                cell = common.getkeyvalue(avars,'cell',ds[0].cell),
                telephone = common.getkeyvalue(avars,'telephone',ds[0].telephone),
                email = common.getkeyvalue(avars,'email',ds[0].email),
                status = common.getkeyvalue(avars,'status',ds[0].status),
                website = common.getkeyvalue(avars,'website',ds[0].website),
                location = common.getkeyvalue(avars,'location',ds[0].location),
                whatsapp = common.getkeyvalue(avars,'whatsapp',ds[0].whatsapp),
                facebook = common.getkeyvalue(avars,'facebook',ds[0].facebook),
                twitter = common.getkeyvalue(avars,'twitter',ds[0].twitter),
                primary = common.getboolean(common.getkeyvalue(avars,'primary','True')),
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
                
                bank_id = int(common.getkeyvalue(avars,"bank_id",ds[0].bank_id)),
                
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
        
        logger.loggerpms2.info("Enter new Clinic ")
        
        try:
            ref_code = common.getkeyvalue(avars,"ref_code","")
            ref_id = int(common.getkeyvalue(avars,"ref_id",0))            
            
            clinicid = db.clinic.insert(\
                clinic_ref = common.getkeyvalue(avars,'clinic_ref',""),
                name = common.getkeyvalue(avars,'name',""),
                address1 = common.getkeyvalue(avars,'address1',""),
                address2 = common.getkeyvalue(avars,'address1',""),
                address3 = common.getkeyvalue(avars,'address3',""),
                city = common.getkeyvalue(avars,'city',""),
                st = common.getkeyvalue(avars,'st',""),
                pin = common.getkeyvalue(avars,'pin',""),
                cell = common.getkeyvalue(avars,'cell',""),
                telephone = common.getkeyvalue(avars,'telephone',""),
                email = common.getkeyvalue(avars,'email',""),
                status = common.getkeyvalue(avars,'status',""),
                website = common.getkeyvalue(avars,'website',""),
                location = common.getkeyvalue(avars,'location',""),
                whatsapp = common.getkeyvalue(avars,'whatsapp',""),
                facebook = common.getkeyvalue(avars,'facebook',""),
                twitter = common.getkeyvalue(avars,'twitter',""),
                primary = common.getboolean(common.getkeyvalue(avars,'primary','True')),
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
                
                bank_id = int(common.getkeyvalue(avars,"bank_id","0")),
                
                is_active = True,
                created_on=common.getISTFormatCurrentLocatTime(),
                modified_on=common.getISTFormatCurrentLocatTime(),
                created_by = 1 if(auth.user == None) else auth.user.id,
                modified_by= 1 if(auth.user == None) else auth.user.id
                
            )
            
            #refcode = "DOC","PROV"
            db.clinic_ref.insert(clinic_id = clinicid, ref_code = ref_code,ref_id = ref_id)
                
            rspobj = {
                "ref_code":ref_code,
                "ref_id":ref_id,
                
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
    
         
