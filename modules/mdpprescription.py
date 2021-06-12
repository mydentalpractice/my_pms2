from gluon import current


import json

import datetime
from datetime import timedelta

from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger

class Prescription:
    
    
    
    def __init__(self,db,providerid):
        self.db = db
        self.providerid = providerid
        return 
    
    
    def getprescriptions(self, memberid, patientid,searchphrase,page,maxcount):
    
        db = self.db
        providerid = self.providerid
        
        page = page -1
        urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
        items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
        limitby = ((page)*items_per_page,(page+1)*items_per_page) if page >= 0 else None        
        presobj = {}
        preslist = []   
        
        
        
        
        query = (db.vw_patientprescription.is_active == True)
        query = ((query) & (db.vw_patientprescription.providerid == providerid)) if(providerid > 0) else (query)


        try:
            if((searchphrase == "") | (searchphrase == None)):
                query =((query) & (db.vw_patientprescription.patientid == patientid) & (db.vw_patientprescription.memberid == memberid))
            else:
                query =((query) & (db.vw_patientprescription.patientid == patientid) & \
                        (db.vw_patientprescription.memberid == memberid) & (db.vw_patientprescription.medicine.like('%' + searchphrase + '%')))
    
            
            prescriptions = db(query).select(db.vw_patientprescription.ALL, limitby = limitby)
            maxcount = db(query).count() if maxcount == 0 else maxcount    
            
            for pres in prescriptions:
                           
                presobj = {
                    "presid":pres.id,
                    "patient": pres.fullname,
                    "doctor":pres.doctorname,
                    "medicine":pres.medicine + " " + pres.strength + " " + pres.strengthuom if((pres.medicine != "") & (pres.medicine != None)) else "",
                    "presdate":(pres.prescriptiondate).strftime("%d/%m/%Y"),
                    "frequency":pres.frequency,
                    "duration":pres.dosage,
                    
                    "dosage":pres.dosage,
                    "strength":pres.strength,
                    "strengthuom":pres.strengthuom,
                    "presdate":(pres.prescriptiondate).strftime("%d/%m/%Y"),
                    "quantity":pres.quantity,                    
                    
                    "remarks":pres.remarks,
                    "instructions":pres.remarks
                    
                }
                preslist.append(presobj)      
                
            xcount = ((page+1) * items_per_page) - (items_per_page - len(prescriptions)) 
                                      
            bnext = True
            bprev = True
            
            #first page
            if((page+1) == 1):
                bnext = True
                bprev = False
            
            #last page
            if(len(prescriptions) < items_per_page):
                bnext = False
                bprev = True          
            
            presobj = {"result":"success","error_message":"","prescount":len(prescriptions),"page":page+1, "preslist":preslist,"runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev}                

        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Get Prescriprions Error - " + str(e)
            return json.dumps(excpobj) 
        
        
        
        return json.dumps(presobj)

    
    def getprescription(self,presid):
        
        db = self.db
        providerid = self.providerid
        presobj = {}
        
       

        try:
            prescriptions = db( (db.vw_patientprescription.id == presid) & (db.vw_patientprescription.is_active == True)).select()
            
           
            
            
            for pres in prescriptions:
                pat = db((db.patientmember.id == pres.memberid) & (db.patientmember.is_active == True)).select(db.patientmember.cell,  db.patientmember.email)
                prov = db((db.provider.id == pres.providerid)& (db.provider.is_active == True)).select(db.provider.cell, db.provider.email)
                
                clinics = db((db.clinic_ref.ref_code == "PRV") & (db.clinic_ref.ref_id == pres.providerid) & (db.clinic.primary_clinic == True) & (db.clinic.is_active == True)).\
                    select(db.clinic.ALL, left=db.clinic.on(db.clinic.id == db.clinic_ref.clinic_id))
                           
                presobj = {
                    
                    "presid":pres.id,
                    "tplanid":pres.tplanid,
                    "treatmentid":pres.treatmentid,
                    "providerid":pres.providerid,
                    "doctorid":pres.doctorid,
                    "patientid":pres.patientid,
                    "mememberid":pres.memberid,
                    
                    "patient": pres.fullname,
                    "doctor":pres.doctorname,
                    "gender":pres.gender,
                    "dob":(pres.dob).strftime("%d/%m/%Y") if(pres.dob != None) else common.getstringfromdate(common.getISTFormatCurrentLocatTime(),"%d/%m/%Y"),
                    "medicineid":pres.medicineid,
                    "medicinename":pres.medicine,
                    "medicinetype":pres.medicinetype,
                    
                    "dosage":pres.dosage,
                    "strength":pres.strength,
                    "strengthuom":pres.strengthuom,
                    "presdate":(pres.prescriptiondate).strftime("%d/%m/%Y") if(pres.prescriptiondate != None) else common.getstringfromdate(common.getISTFormatCurrentLocatTime(),"%d/%m/%Y"),
                    "frequency":pres.frequency,
                    "duration":pres.dosage,
                    "quantity":pres.quantity,
                    "remarks":pres.remarks,
                    "instructions":pres.remarks,
                    
                    "patcell":pat[0].cell if(len(pat) >0 ) else "",
                    "patemail":pat[0].email if(len(pat) >0 ) else "",
                    "provcell":prov[0].cell if(len(prov) >0 ) else "",
                    "provemail":prov[0].email if(len(prov) >0 ) else "",
                  
                    "clinic_name":clinics[0].name if(len(clinics) >0 ) else "",
                    "clinic_address1":clinics[0].address1 if(len(clinics) >0 ) else "",
                    "clinic_address2":clinics[0].address2 if(len(clinics) >0 ) else "",
                    "clinic_address3":clinics[0].address3 if(len(clinics) >0 ) else "",
                    "clinic_city":clinics[0].city if(len(clinics) >0 ) else "",
                    "clinic_st":clinics[0].st if(len(clinics) >0 ) else "",
                    "clinic_pin":clinics[0].pin if(len(clinics) >0 ) else ""
                
                }
            
            presobj["result"] = "success"    
            presobj["error_message"] = ""
    
            
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Get Prescription Error - " + str(e)
            return json.dumps(excpobj) 
        
        logger.loggerpms2.info("Exit Get Prescription = " + json.dumps(presobj))
        return json.dumps(presobj)
    
    def newprescription(self,presdata):
        
        logger.loggerpms2.info("Enter new pescriptions " + json.dumps(presdata))
        db = self.db
        providerid = self.providerid
        


        try:
            #create new prescription
            presid = db.prescription.insert(\
                prescriptiondate=datetime.datetime.strptime(presdata["presdate"],"%d/%m/%Y"),
              
                medicineid=presdata["medicineid"],
                treatmentid=presdata["treatmentid"],
                dosage=presdata["dosage"],
                quantity=presdata["quantity"],
                frequency=presdata["frequency"],
                remarks=presdata["remarks"],
                tplanid = presdata["tplanid"],
                providerid=presdata["providerid"],
                doctorid=presdata["doctorid"],
                patientid=presdata["patientid"],
                memberid=presdata["memberid"],
                is_active = True,
                created_on = common.getISTFormatCurrentLocatTime(),
                created_by = 1,
                modified_on = common.getISTFormatCurrentLocatTime(),
                modified_by = 1
            )
          
            jsonresp = {"presid":str(presid), "result":"success","error_message":""}
        
        except Exception as e:
            logger.loggerpms2.info("Create Prescription Exception:\n" + str(e))
            jsonresp = {
              "result":"fail",
              "error_message":"Create Prescription Exception:\n" + str(e)
            }
        
        return json.dumps(jsonresp)
        
    def updateprescription(self,presid,presdata):
        logger.loggerpms2.info("Enter Update Prescription " + str(presid) + " " + json.dumps(presdata))
        db = self.db
        providerid = self.providerid
        


        try:
            #update prescription
            db(db.prescription.id == presid).update(\
                prescriptiondate=common.getdatefromstring(presdata["presdate"], "%d/%m/%Y") if((presdata["presdate"] != None) & (presdata["presdate"] != "") ) else common.getISTFormatCurrentLocatTime() ,
                medicineid=presdata["medicineid"],
                treatmentid=presdata["treatmentid"],
                dosage=presdata["dosage"],
                quantity=presdata["quantity"],
                frequency=presdata["frequency"],
                remarks=presdata["remarks"],
                tplanid = presdata["tplanid"],
                providerid=presdata["providerid"],
                doctorid=presdata["doctorid"],
                patientid=presdata["patientid"],
                memberid=presdata["memberid"],
                is_active = True,
                modified_on = common.getISTFormatCurrentLocatTime(),
                modified_by = 1
            )
          
            jsonresp = {"presid":str(presid), "result":"success","error_message":""}
        
        except Exception as e:
            logger.loggerpms2.info("Update Prescription Exception:\n" + str(e))
            jsonresp = {
              "result":"fail",
              "error_message":"Update Prescription Exception:\n" + str(e)
            }
        
        logger.loggerpms2.info("Exit Update Prescription " + " " + json.dumps(jsonresp))
        return json.dumps(jsonresp)
    
    def deleteprescription(self,presid):
        
        db = self.db
        providerid = self.providerid
        


        try:
            #update prescription
            db(db.prescription.id == presid).update(\
                is_active = False,
                modified_on = common.getISTFormatCurrentLocatTime(),
                modified_by = 1
            )
          
            jsonresp = {"presid":str(presid), "result":"success","error_message":""}
        
        except Exception as e:
            logger.loggerpms2.info("Delete Prescription Exception:\n" + str(e))
            jsonresp = {
              "result":"fail",
              "error_message":"Delete Prescription Exception:\n" + str(e)
            }
        
        return json.dumps(jsonresp)
    
    
    def getmedicines(self,searchphrase,page,maxcount):
        
        db = self.db
        providerid = self.providerid          
        
        
        page = page -1
        urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
        items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
        limitby = ((page)*items_per_page,(page+1)*items_per_page) if page >= 0 else None     
        if(page < 0):
            limitby = None
        
        
        medobj = {}
        medlist = []
        try:
            #query =((db.medicine_default.id > 0) & (db.medicine_default.is_active == True))
            if((searchphrase == "") | (searchphrase == None)):
                query =((db.medicine_default.id > 0) & (db.medicine_default.is_active == True))
            else:
                query= ((db.medicine_default.id > 0) & (db.medicine_default.medicine.like('%' + searchphrase + '%')) & (db.medicine_default.is_active == True))
    
        
            medicines = db(query).select(db.medicine_default.ALL, limitby=limitby)
            maxcount = db(query).count() if maxcount == 0 else maxcount    
    
            for medicine in medicines:
                
                medobj = {
                
                    "medicineid":int(common.getid(medicine.id)),
                    "medicine":common.getstring(medicine.medicine),
                    "medicinetype":common.getstring(medicine.meditype),
                    "strength":common.getstring(medicine.strength),
                    "strengthuom":common.getstring(medicine.strengthuom)
                }
                medlist.append(medobj)
            
            xcount = ((page+1) * items_per_page) - (items_per_page - len(medicines)) 
                           
            bnext = True
            bprev = True
            
            #first page
            if((page+1) == 1):
                bnext = True
                bprev = False
            
            #last page
            if(len(medicines) < items_per_page):
                bnext = False
                bprev = True          
            
            medobj = {"result":"success","error_message":"","medcount":len(medicines),"page":page+1, "medlist":medlist,"runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev}
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Get Medicines Error - " + str(e)
            return json.dumps(excpobj)       
        
        return json.dumps(medobj)
        
    def getmedicine(self,medicineid):
        
        db = self.db
        providerid = self.providerid
        medobj = {}
        
        try:
            medicines = db((db.medicine_default.id == medicineid) & (db.medicine_default.is_active == True)).select()
           
            for medicine in medicines:
                           
                medobj = {
                
                    "medicineid":int(common.getid(medicine.id)),
                    "medicine":common.getstring(medicine.medicine),
                    "medicinetype":common.getstring(medicine.meditype),
                    "strength":common.getstring(medicine.strength),
                    "strengthuom":common.getstring(medicine.strengthuom),
                    "instructions":common.getstring(medicine.instructions)
                }
            
                medobj["result"] = "success"    
                medobj["error_message"] = ""
            
            
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Get Medicine Error - " + str(e)
            return json.dumps(excpobj) 
        
        return json.dumps(medobj)

    def updatemedicine(self,medobj):
        
        db = self.db
        providerid = self.providerid
        
        
        try:
            auth = current.auth
            medicineid = int(common.getid(medobj["medicineid"]))
            medid = db.medicine_default.update_or_insert(((db.medicine_default.id == medicineid) & (db.medicine_default.is_active == True)),
                                        
                                         medicine = common.getstring(medobj["medicine"]),
                                         meditype = common.getstring(medobj["medicinetype"]),
                                         strength = common.getstring(medobj["strength"]),
                                         strengthuom = common.getstring(medobj["strengthuom"]),
                                         instructions = common.getstring(medobj["instructions"]),
                                         is_active = True
                                         )
                                         
                                         
            
            return json.dumps({"result":"success", "error_message":"","medicineid":medicineid if medid == None else medid})
        except Exception as e:
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = "Update Medicine Error - " + str(e)
            return json.dumps(excpobj) 
        
   