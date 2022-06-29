from gluon import current
db = current.globalenv['db']
#
import os
import json

import datetime
import time
import calendar
from datetime import timedelta

datefmt = "%d/%m/%Y"
datetimefmt = "%d/%m/%Y %H:%M:%S"

from applications.my_pms2.modules import common


class Task:
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    return 
  
  def dummy(self):
      db = self.db
      auth = current.auth
      
      try:
        i = 0
        
      except Exception as e:
          error_message = "Add Mediclaim Procedures Exception Error - " + str(e)
          logger.loggerpms2.info(error_message)
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = error_message
          return json.dumps(excpobj)    
      
      return    
    
    
  def activitytracker(self,avars):
      db = self.db
      auth = current.auth
      
      
      
      try:
        activitydate = datetime.datetime.strptime(avars["activitydate"], "%d/%m/%Y")
        str1 = activitydate.strftime("%Y-%m-%d 00:00:00")
        str2 = activitydate.strftime("%Y-%m-%d 23:59:59")
        
        #timeinterval
        r = db(db.urlproperties.id >0).select(db.urlproperties.timeinterval)
        timeinterval = int(common.getvalue(r[0].timeinterval))
         
        #get all the appts for activitydate
        appts = db((((db.t_appointment.f_start_time >= str1) & (db.t_appointment.f_start_time <= str2)) | ((db.t_appointment.modified_on >= str1) & (db.t_appointment.modified_on <= str2)))&(db.t_appointment.is_active == True)).\
            select(db.t_appointment.ALL, db.provider.providername, db.doctor.name, left=[db.provider.on(db.provider.id == db.t_appointment.provider), db.doctor.on(db.doctor.id==db.t_appointment.doctor)]
                                                                                                                                                     )
        for appt in appts:
            db.activitytracker.update_or_insert(db.activitytracker.appointmentid == appt.t_appointment.id,\
                                                memberid = appt.t_appointment.patientmember, patientid = appt.t_appointment.patient,\
                                                appointmentid = appt.t_appointment.id,\
                                                patientname = appt.t_appointment.f_patientname,\
                                                appointmentdate = appt.t_appointment.f_start_time,\
                                                appointmentstatus = appt.t_appointment.f_status,\
                                                doctorid = appt.t_appointment.doctor,\
                                                doctorname = appt.doctor.name,\
                                                providerid = appt.t_appointment.provider,\
                                                providername = appt.provider.providername,\
                                                lastapptactivity = appt.t_appointment.modified_on,\
                                                created_on = common.getISTFormatCurrentLocatTime(),\
                                                created_by = 1 if(auth.user == None) else auth.user.id,
                                                modified_on = common.getISTFormatCurrentLocatTime(),\
                                                modified_by = 1 if(auth.user == None) else auth.user.id,
                                                 )
             
         
        #get all treatments modified activitydate
        trtmnts =db((db.vw_treatmentlist.modified_on >= str1) & (db.vw_treatmentlist.modified_on <= str2) &(db.vw_treatmentlist.is_active == True)).\
            select(db.vw_treatmentlist.ALL, db.vw_treatment_procedure_group.shortdescription, db.provider.providername,left=[db.vw_treatment_procedure_group.on(db.vw_treatment_procedure_group.treatmentid == db.vw_treatmentlist.id),
                                                                                                    db.provider.on(db.provider.id == db.vw_treatmentlist.providerid)])
        
        for trtmnt in trtmnts:
            db.activitytracker.update_or_insert(db.activitytracker.treatmentid == trtmnt.vw_treatmentlist.id,\
                                                treatmentid = trtmnt.vw_treatmentlist.id,\
                                                patientid = trtmnt.vw_treatmentlist.patientid,\
                                                memberid = trtmnt.vw_treatmentlist.memberid,\
                                                providerid = trtmnt.vw_treatmentlist.providerid,\
                                                treatment = trtmnt.vw_treatmentlist.treatment,\
                                                treatmentdate = trtmnt.vw_treatmentlist.startdate,\
                                                treatmentstatus = trtmnt.vw_treatmentlist.status,\
                                                procedures = trtmnt.vw_treatment_procedure_group.shortdescription,\
                                                treatmentcost = trtmnt.vw_treatmentlist.treatmentcost,\
                                                providername = trtmnt.provider.providername,\
                                                patientname = trtmnt.vw_treatmentlist.patientname,\
                                                lasttreatmentactivity=trtmnt.vw_treatmentlist.modified_on,\
                                                created_on = common.getISTFormatCurrentLocatTime(),\
                                                created_by = 1 if(auth.user == None) else auth.user.id,
                                                modified_on = common.getISTFormatCurrentLocatTime(),\
                                                modified_by = 1 if(auth.user == None) else auth.user.id,
                                                )
            
         
         
        #get all payments modified activitydate
        payments =db((db.vw_paymentlist.paymentdate >= str1) & (db.vw_paymentlist.paymentdate <= str2) &(db.vw_paymentlist.is_active == True)).select(db.vw_paymentlist.ALL, db.provider.providername, left=[db.provider.on(db.provider.id == db.vw_paymentlist.providerid)])
        
        for pymnt in payments:
            db.activitytracker.update_or_insert(db.activitytracker.paymentid == pymnt.vw_paymentlist.id,\
                                                        paymentid = pymnt.vw_paymentlist.id,\
                                                        paymentmode = pymnt.vw_paymentlist.paymentmode,\
                                                        paymentdate = pymnt.vw_paymentlist.paymentdate,\
                                                        paymentinvoice = pymnt.vw_paymentlist.fpinvoice,\
                                                        paymentamount = pymnt.vw_paymentlist.amount,\
                                                        patientname = pymnt.vw_paymentlist.patientname,\
                                                        providername = pymnt.provider.providername,\
                                                        treatment = pymnt.vw_paymentlist.treatment,\
                                                        memberid = pymnt.vw_paymentlist.memberid,\
                                                        patientid = pymnt.vw_paymentlist.patientid,\
                                                        providerid = pymnt.vw_paymentlist.providerid,\
                                                        treatmentid = pymnt.vw_paymentlist.treatmentid,\
                                                        totalcost = pymnt.vw_paymentlist.totaltreatmentcost,\
                                                        totalpaid = pymnt.vw_paymentlist.totalpaid,\
                                                        totaldue = pymnt.vw_paymentlist.totaldue,\
                                                        created_on = common.getISTFormatCurrentLocatTime(),\
                                                        created_by = 1 if(auth.user == None) else auth.user.id,
                                                        modified_on = common.getISTFormatCurrentLocatTime(),\
                                                        modified_by = 1 if(auth.user == None) else auth.user.id,
                                                        )
        obj = {"result":"success","error_message":""}
        return json.dumps(obj)
                            
      except Exception as e:
          error_message = "Activity Tracker Exception Error - " + str(e)
          logger.loggerpms2.info(error_message)
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = error_message
          return json.dumps(excpobj)    
      
      return      
      