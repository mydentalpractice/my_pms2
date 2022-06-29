# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from gluon import current
db = current.globalenv['db']
from gluon.tools import Mail
#
from gluon.tools import Crud
crud = Crud(db)

from shutil import copyfile

import os
import json
from base64 import decodestring
#from datetime import datetime

import datetime
import time
import calendar
from datetime import timedelta


#import sys
#sys.path.append('my_pms2/modules')
from applications.my_pms2.modules import common
from applications.my_pms2.modules import status
from applications.my_pms2.modules import account
from applications.my_pms2.modules import gender
from applications.my_pms2.modules import states
from applications.my_pms2.modules import tasks
from applications.my_pms2.modules import mdpappointment
from applications.my_pms2.modules import logger

#from gluon.contrib import common
#from gluon.contrib import status
#from gluon.contrib import account
#from gluon.contrib import gender
#from gluon.contrib import states
#from gluon.contrib import tasks

datefmt = "%d/%m/%Y"
datetimefmt = "%d/%m/%Y %H:%M:%S"

_mail = None


def testgroupsms():
     r = tasks.sendNewAptGrpSMS(db,request.folder)
     return dict()


def smsservice():
     
     message = "Enter Loop" + " " + (common.getISTFormatCurrentLocatTime()).strftime(datetimefmt)
     logger.loggerpms2.info(message)
     strdt  = request.vars.activitydate
     groupapptsms = request.vars.groupapptsms
     activitydate = datetime.datetime.strptime(strdt, datefmt)
     stractdt = activitydate.strftime(datefmt)
     
     try:
          formC =  SQLFORM.factory( 
              
              Field('activitydate', 'date',label='Activity Date',default=activitydate, requires=[IS_NOT_EMPTY(), IS_DATE(format=T('%d/%m/%Y'))])
          )
          
          #timeinterval
          r = db(db.urlproperties.id >0).select(db.urlproperties.timeinterval)
          timeinterval = float(common.getvalue(r[0].timeinterval)) if(len(r) ==1 ) else 3600000
        
          if(groupapptsms == "1"):
               message = "Re-Enter Loop"  + " " + (common.getISTFormatCurrentLocatTime()).strftime(datetimefmt)
               logger.loggerpms2.info(message)
               obj = {"appPath":request.folder}
               
               o = mdpappointment.Appointment(db, 1)
               r = o.sendAllAppointmentsSMSEmail(obj)
               #r = o.groupsms(request.folder)
               jsonr = json.loads(r)
               if(jsonr["result"] == "fail"):
                    message = message + " " + jsonr["error_message"]
          
          
               
     except Exception as e:
          message = "SMSService : Exception error - " + str(e)
          logger.loggerpms2.info(message)
          activitydate = common.getISTFormatCurrentLocatTime()
          formC =  SQLFORM.factory( 
              Field('activitydate', 'date',label='Activity Date',default=activitydate, requires=[IS_NOT_EMPTY(), IS_DATE(format=T('%d/%m/%Y'))])
          )
               
               
     return dict(formC=formC,timeinterval=timeinterval,stractdt=stractdt,message=message)


def activitytracker():


   
    
    strdt  = request.vars.activitydate if((request.vars.activitydate != None)&(request.vars.activitydate != "")) else (datetime.date.today()).strftime("%d/%m/%Y")
    groupapptsms = request.vars.groupapptsms if((request.vars.groupapptsms != None)&(request.vars.groupapptsms != ""))  else True
    
    activitydate = datetime.datetime.strptime(strdt, datefmt)
    
    stractdt = activitydate.strftime(datefmt)

    str1 = activitydate.strftime("%Y-%m-%d 00:00:00")
    str2 = activitydate.strftime("%Y-%m-%d 23:59:59")
    
    #Deactivate all activities previous to activitydate's date
    
    
    
    formAppts = None
    formTrtmnts = None
    formPayments = None
    formCustomers = None
    
    #timeinterval
    r = db(db.urlproperties.id >0).select(db.urlproperties.timeinterval)
    timeinterval = int(common.getvalue(r[0].timeinterval))
    
    
    #get all customers for the activity date
    customers = db((db.customer.enrolldate >= str1) & (db.customer.enrolldate <= str2) &(db.customer.is_active == True)).\
        select(db.customer.ALL, db.provider.providername, db.company.company,db.hmoplan.hmoplancode,db.groupregion.groupregion,
               left=[db.provider.on(db.provider.id == db.customer.providerid), db.hmoplan.on(db.hmoplan.id==db.customer.planid),\
                     db.company.on(db.company.id == db.customer.companyid), db.groupregion.on(db.groupregion.id == db.customer.regionid)])
    
    for customer in customers:
         db.activitytracker.update_or_insert(db.activitytracker.customerid == customer.customer.id,\
                                             customerid = customer.customer.id,
                                             customer_ref = customer.customer.customer_ref,
                                             customer_name = customer.customer.fname +  " " + customer.customer.lname,
                                             company = customer.company.company,
                                             hmoplan = customer.hmoplan.hmoplancode,
                                             region = customer.groupregion.groupregion,
                                             provider = customer.provider.providername,
                                             enrolledon = customer.customer.enrolldate,
                                             appointmenton = customer.customer.appointment_datetime,
                                             created_on = common.getISTFormatCurrentLocatTime(),\
                                             created_by = 1,\
                                             modified_on = common.getISTFormatCurrentLocatTime(),\
                                             modified_by = 1                                             
                                             )
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
                                            created_by = 1,\
                                            modified_on = common.getISTFormatCurrentLocatTime(),\
                                            modified_by = 1
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
                                            created_by = 1,\
                                            modified_on = common.getISTFormatCurrentLocatTime(),\
                                            modified_by = 1
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
                                                    created_by = 1,\
                                                    modified_on = common.getISTFormatCurrentLocatTime(),\
                                                    modified_by = 1
                                                    )
                
            
    query = ((db.activitytracker.appointmentid >0)&\
             (((db.activitytracker.lastapptactivity >= str1)&(db.activitytracker.lastapptactivity <= str2)) | ((db.activitytracker.appointmentdate >= str1)&(db.activitytracker.appointmentdate <= str2)))&\
             (db.activitytracker.is_active == True))
 
    fields = (db.activitytracker.patientname,db.activitytracker.appointmentdate,\
              db.activitytracker.appointmentstatus,db.activitytracker.providername,db.activitytracker.doctorname,\
              db.activitytracker.lastapptactivity)
    headers = {
    
         'activitytracker.patientname':'Patient',
         'activitytracker.appointmentdate':'Appointment Date',
         'activitytracker.appointmentstatus':'Status',
         'activitytracker.providername':'Provider',
         'activitytracker.doctorname':'Doctor',
         'activitytracker.lastapptactivity':'Last Activity'
    }
    
    
    left =    [db.t_appointment.on(db.t_appointment.id==db.patientmember.company)]    
    orderby = db.activitytracker.providername | db.activitytracker.patientname 
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    formAppts = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            paginate=10,
                            orderby=orderby,
                            exportclasses=exportlist,
                            links_in_grid=False,
                            searchable=False,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            user_signature=True
                           )           
    
    
    query = ((db.activitytracker.paymentid >0)&(db.activitytracker.paymentdate >= str1)&(db.activitytracker.paymentdate <= str2)&(db.activitytracker.is_active == True))
    fields = (db.activitytracker.paymentid,db.activitytracker.patientname,db.activitytracker.providername,db.activitytracker.treatment,db.activitytracker.paymentdate,\
              db.activitytracker.paymentmode,db.activitytracker.paymentinvoice,\
              db.activitytracker.paymentamount,db.activitytracker.totalcost, db.activitytracker.totalpaid,db.activitytracker.totaldue)
  
    returnurl = URL("superadmin","activitytracker",vars=dict(groupapptsms=0,activitydate=stractdt))
    headers = {
         
         'activitytracker.patientname':'Patient',
         'activitytracker.providername':'Provider',
         'activitytracker.treatment':'Treatment',
         'activitytracker.paymentdate':'Payment Date',
         'activitytracker.paymentmode':'Mode',
         'activitytracker.paymentinvoice':'Invoice',
         'activitytracker.paymentamount':'Paid Amount',
         'activitytracker.totalcost':'Total Cost',
         'activitytracker.totalpaid':'Total Paid',
         'activitytracker.totaldue':'Total Due',
         
    }
    db.activitytracker.paymentid.readable = False
    db.activitytracker.paymentid.writable = False
    links = [\
           
           dict(header=CENTER("View/Print"), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),\
                                                                       _href=URL("payment","print_payment_receipt",\
                                                                                 vars=dict(paymentid=row.paymentid, page=1,tplanid=0,\
                                                                                           treatmentid=0,patient="",\
                                                                                           fullname="",patientid=0, \
                                                                                           memberid=0,providerid=0,\
                                                                                           providername="",\
                                                                                           returnurl=returnurl,mode="update"))))),
    ]
    
    
    
    orderby = ~db.activitytracker.appointmentdate | db.activitytracker.providername | db.activitytracker.patientname
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, csv=False,json=False, xml=False)
    formPayments = SQLFORM.grid(query=query,
                                headers=headers,
                                fields=fields,
                                paginate=10,
                                links=links,
                                orderby=orderby,
                                exportclasses=exportlist,
                                links_in_grid=True,
                                searchable=False,
                                create=False,
                                deletable=False,
                                editable=False,
                                details=False,
                                user_signature=True
                           )           
    
    
    query = ((db.activitytracker.treatmentid >0)&(db.activitytracker.lasttreatmentactivity >= str1)&(db.activitytracker.lasttreatmentactivity <= str2)&(db.activitytracker.is_active == True))
    fields = (db.activitytracker.patientname,db.activitytracker.providername,db.activitytracker.treatment,db.activitytracker.treatmentdate,db.activitytracker.treatmentstatus,\
              db.activitytracker.procedures,db.activitytracker.treatmentcost,db.activitytracker.lasttreatmentactivity\
              )
    headers = {
    
         'activitytracker.patientname':'Patient',
         'activitytracker.providername':'Provider',
         'activitytracker.treatment':'Treatment',
         'activitytracker.treatmentdate':'Treatment Date',
         'activitytracker.treatmentstatus':'Status',
         'activitytracker.procedures':'Procedures',
         'activitytracker.treatmentcost':'Cost',
         'activitytracker.lasttreatmentactivity':'Last Activity'
         
    }
    
    maxtextlengths = {'activitytracker.procedures':100}
    orderby = db.activitytracker.providername | db.activitytracker.patientname
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    formTrtmnts = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            paginate=10,
                            orderby=orderby,
                            maxtextlengths=maxtextlengths,
                            exportclasses=exportlist,
                            links_in_grid=False,
                            searchable=False,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            user_signature=True
                           )          
                           
    
    
    #display customers
    query = ((db.activitytracker.customerid >0)&(db.activitytracker.enrolledon >= str1)&(db.activitytracker.enrolledon <= str2)&(db.activitytracker.is_active == True))    
    fields = (db.activitytracker.customer_ref, db.activitytracker.customer_name, db.activitytracker.appointmenton, \
              db.activitytracker.provider,db.activitytracker.company, db.activitytracker.hmoplan,db.activitytracker.region)
              
    headers = {
       
            'activitytracker.customer_ref':'Customer Ref',
            'activitytracker.customer_name':'Customer',
            'activitytracker.appointmenton':'Appointment',
            'activitytracker.provider':'Provider',
            'activitytracker.company':'Company',
            'activitytracker.hmoplan':'Plan',
            'activitytracker.region':'Region'
            
       }    
    maxtextlengths = {'activitytracker.customer_name':100}
    orderby = db.activitytracker.company | db.activitytracker.customer_name
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    formCustomers = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            paginate=10,
                            orderby=orderby,
                            maxtextlengths=maxtextlengths,
                            exportclasses=exportlist,
                            links_in_grid=False,
                            searchable=False,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            user_signature=True
                           )          
    
    formC =  SQLFORM.factory( 
        
        Field('activitydate', 'date',label='Activity Date',default=activitydate, requires=[IS_NOT_EMPTY(), IS_DATE(format=T('%d/%m/%Y'))])
    )

    query = ((db.groupsmscount.id >0) & (db.groupsmscount.smscount > 0))
    fields = (db.groupsmscount.smsdate,db.groupsmscount.smscount)
    headers = {
            'groupsmscount.smsdate':'SMS Date',
            'groupsmscount.smscount':'SMS Coumt',    
    }
    orderby = ~db.groupsmscount.smsdate 
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    formSMS = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            exportclasses = exportlist,
                            paginate=10,
                            orderby=orderby,
                            links_in_grid=False,
                            searchable=False,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            user_signature=True
                           )           

    
    return dict(formC=formC,formCustomers=formCustomers,\
                formAppts=formAppts,formPayments=formPayments,formTrtmnts=formTrtmnts,formSMS=formSMS,\
                timeinterval=timeinterval,stractdt=stractdt)

def getpresgrid(memberid, patientid,providerid):
    
    prescriptions = db((db.vw_patientprescription.providerid == providerid) & \
                              (db.vw_patientprescription.is_active == True) & \
                              (db.vw_patientprescription.patientid == patientid) & \
                              (db.vw_patientprescription.memberid == memberid)).select()
    
    
    
    return prescriptions



def xgetpresgrid(patientid,providerid):
    
    query = ((db.prescription.patientid == patientid) & (db.prescription.providerid == providerid) &  (db.prescription.is_active == True))
    fields=(db.prescription.medicinename,db.prescription.dosage,db.prescription.frequency, db.prescription.quantity,db.prescription.modified_on)
    headers={
        'prescription.modified_on':'Date',
        'prescription.medicinename':'Medicine',
        'prescription.dosage':'Dosage',
        'prescription.frequency':'Period',
        'prescription.quantity':'Quantity'
    }
    
    db.prescription.modified_on.readable = True
    db.prescription.modified_on.writable = True
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    orderby = ~db.prescription.modified_on
    
    presgrid = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        paginate=20,
                        orderby=orderby,
                        exportclasses=exportlist,
                        links_in_grid=False,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )       
   
    
    
    return presgrid

def getmedtestgrid(patientid, providerid):
    medtestquery = ((db.medicaltest.patientid == patientid) & (db.medicaltest.providerid == providerid) & (db.medicaltest.is_active == True))
    
    medtestfields=(db.medicaltest.testname,db.medicaltest.actval,db.medicaltest.upval, db.medicaltest.lowval, db.medicaltest.typval, db.medicaltest.modified_on)
    
    medtestheaders={
        
        'medicaltest.modified_on':'Date',
        'medicaltest.testname':'Medical Test',
        'medicaltest.actval':'Actual Value',
        'medicaltest.lowval':'Lower Value',
        'medicaltest.typval':'Typical Value',
        'medicaltest.upval':'Upper Value'
                }

    db.medicaltest.modified_on.readable = True
    db.medicaltest.modified_on.writable = True
 
    medtestexport = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
     
    medtestorderby = ~db.medicaltest.modified_on
       
    medtestgrid = SQLFORM.grid(query=medtestquery,
                        headers=medtestheaders,
                        fields=medtestfields,
                        paginate=20,
                        orderby=medtestorderby,
                        exportclasses=medtestexport,
                        links_in_grid=False,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )
    
    return medtestgrid


def getage(dob):
    ageyear = dob.year
    curryear = datetime.date.today().year
    return curryear - ageyear

def getproviders(providerid):

    if(providerid == 0):
        providers = db((db.provider.id >= 0) & (db.provider.is_active == True)).count()
        regproviders = db((db.provider.id >= 0) & (db.provider.registered == True) & (db.provider.is_active == True)).count()
        nonregproviders = db((db.provider.id >= 0) & (db.provider.registered == False) & (db.provider.is_active == True)).count()
    else:
        providers = db((db.provider.id == providerid) & (db.provider.is_active == True)).count()
        regproviders = db((db.provider.id == providerid) & (db.provider.registered == True) & (db.provider.is_active == True)).count()
        nonregproviders = db((db.provider.id == providerid) & (db.provider.registered == False) & (db.provider.is_active == True)).count()
    
    
    return dict(providers=providers, regproviders=regproviders, nonregproviders=nonregproviders)

def getmembers(providerid):

    if(providerid == 0)    :
        members = db((db.vw_memberpatientlist.id > 0) & (db.vw_memberpatientlist.hmopatientmember == True) & (db.vw_memberpatientlist.is_active == True)).count()
        walkins = db((db.vw_memberpatientlist.id > 0) & (db.vw_memberpatientlist.hmopatientmember == False) & (db.vw_memberpatientlist.is_active == True)).count()
    else:
        members = db((db.vw_memberpatientlist.id > 0) & (db.vw_memberpatientlist.providerid == providerid)  & (db.vw_memberpatientlist.hmopatientmember == True) & (db.vw_memberpatientlist.is_active == True)).count()
        walkins = db((db.vw_memberpatientlist.id > 0) & (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.hmopatientmember == False) & (db.vw_memberpatientlist.is_active == True)).count()
        
    
    return dict(members=members,walkins=walkins)

def gettreatments(providerid):
    
    if(providerid == 0):
        treatments = db((db.vw_treatmentlist.id > 0)  & (db.vw_treatmentlist.is_active == True )).count()
    else:
        treatments = db((db.vw_treatmentlist.id > 0)  & (db.vw_treatmentlist.providerid == providerid)  & (db.vw_treatmentlist.is_active == True )).count()
        
    return dict(treatments=treatments)

def getpayments(providerid):
    
    totalcost = 0
    totalpaid = 0
    totaldue = 0
    
    if(providerid == 0):
        payments = db((db.vw_paymentsummary1.id > 0)).select()
    else:
        payments = db((db.vw_paymentsummary1.id > 0)  & (db.vw_paymentsummary1.provider == providerid)).select()
    
    for payment in payments:
        totalcost = totalcost + float(common.getvalue(payment.totalcost))
        totalpaid = totalpaid + float(common.getvalue(payment.totalpaid))
    
    totaldue = totalcost - totalpaid
        
    return dict(totalcost=totalcost, totalpaid=totalpaid,totaldue=totaldue)

def dashboard(providerid):
    
    providers = getproviders(providerid)
    session.assignedprovs = int(providers["providers"])
    session.regprovs =  int(providers["regproviders"])
    session.nonregprovs =  int(providers["nonregproviders"])

    members = getmembers(providerid)
    session.totmembers = int(members["members"])
    session.totwalkins = int(members["walkins"])
    
    treatments = gettreatments(providerid)
    session.tottreatments = int(treatments["treatments"])
    
    payments = getpayments(providerid)
    session.totcost = payments["totalcost"]
    session.totpaid = payments["totalpaid"]
    session.totdue = payments["totaldue"]
    
    return dict()

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def getpaymentgrid(tplanid, patientid,patient,fullname,memberid,providerid,providername,page):

    #Get Payments for the Member
    if(memberid == 0):
        query = ((db.vw_paymentlist.is_active==True) & (db.vw_paymentlist.providerid == providerid))
    else:    
        query = ((db.vw_paymentlist.is_active==True) & (db.vw_paymentlist.providerid == providerid) & (db.vw_paymentlist.memberid==memberid))
    
    fields=(db.vw_paymentlist.paymentdate, db.vw_paymentlist.amount,\
            db.vw_paymentlist.treatment,db.vw_paymentlist.patientmember, db.vw_paymentlist.memberid,\
            db.vw_paymentlist.paymentcommit
            )
    
    headers={'vw_paymentlist.paymentdate':'Date',
             'vw_paymentlist.amount':'Amount',
             'vw_paymentlist.treatment':'Treatment',
             'vw_paymentlist.patientmember':'Member',
             'vw_paymentlist.paymentcommit':'Committed?',
             
            }   

    links = [\
           dict(header=CENTER("Edit"), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("superadmin","update_payment",vars=dict(paymentid=row.id, page=page,tplanid=tplanid,patient=patient,fullname=fullname,patientid=patientid, memberid=row.memberid,providerid=providerid,providername=providername))))),
           #dict(header='Delete',body=lambda row: A(IMG(_src="/my_pms2/static/img/png/001-rubbish-bin.png",_width=30, _height=30),_href=URL("payment","delete_payment",vars=dict(page=page,paymentid=row.id,providerid=providerid,tplanid=tplanid,memberid=memberid))))
    ]

    
    db.vw_paymentlist.memberid.writable = False;
    db.vw_paymentlist.memberid.readable = False;

    orderby = ~(db.vw_paymentlist.paymentdate) | ~(db.vw_paymentlist.id) | (db.vw_paymentlist.patientmember)
    
    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
    
    
    
    maxtextlengths = {'vw_paymentlist.treatment':64, 'vw_paymentlist.patientmember':32}

    totalcost =0
    totaldue = 0
    totalpaid = 0
    
    if(memberid > 0):
        
        r = db((db.vw_paymentsummary1.provider == providerid) & (db.vw_paymentsummary1.patientmember == memberid)).select()
        if(len(r) > 0):
            totalcost = float(common.getvalue(r[0].totalcost))
            totalpaid = float(common.getvalue(r[0].totalpaid))
            totaldue = totalcost - totalpaid
    
    
    formA = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        maxtextlengths=maxtextlengths,
                        orderby=orderby,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )    

    xsearch = formA.element('input',_value='Search')
    xsearch['_class'] = 'form_details_button btn'
    xclear = formA.element('input',_value='Clear')
    xclear['_class'] = 'form_details_button btn'
    xnew = formA.element('input',_value='New Search')
    xnew['_class'] = 'form_details_button_black btn'
    xand = formA.element('input',_value='+ And')
    xand['_class'] = 'form_details_button_black btn'
    xor = formA.element('input',_value='+ Or')
    xor['_class'] = 'form_details_button_black btn'
    xclose = formA.element('input',_value='Close')
    xclose['_class'] = 'form_details_button_black btn'  

    
    return formA


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def getimages(db,providerid, patientid,limitby,is_active):
    
    activequery = ((db.dentalimage.image != None)&(db.dentalimage.image != "") & (db.dentalimage.is_active == is_active))

    if(providerid > 0):
        activequery = ((db.dentalimage.provider == providerid) & (activequery))

    if(patientid > 0):
        activequery = ((db.dentalimage.patient == patientid) & (activequery))
                    
    dsimages = None
                                 
    if(limitby > 0):
        dsimages = db(activequery).select(
                                    db.dentalimage.id,db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                                    db.dentalimage.patienttype,db.dentalimage.patientname,db.dentalimage.description,db.dentalimage.is_active,db.vw_memberpatientlist.patientmember,\
                                    left=[db.vw_memberpatientlist.on(db.dentalimage.patient == db.vw_memberpatientlist.patientid)],\
                                          limitby=limitby, orderby = db.vw_memberpatientlist.patientmember | ~db.dentalimage.patienttype | ~db.dentalimage.id
                                )
    else:
        dsimages = db(activequery).select(
                                    db.dentalimage.id,db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                                    db.dentalimage.patienttype,db.dentalimage.patientname,db.dentalimage.description,db.dentalimage.is_active,db.vw_memberpatientlist.patientmember,\
                                    left=[db.vw_memberpatientlist.on(db.dentalimage.patient == db.vw_memberpatientlist.patientid)],\
                                          orderby = db.vw_memberpatientlist.patientmember | ~db.dentalimage.patienttype | ~db.dentalimage.id
                            )
        
    return dsimages


def impersonate():
    user_id = 1
    impersonatorid = auth.user.id
    
    provdict=common.getproviderfromid(db, int(common.getid(request.vars.providerid)))
    session.religare = False
    impersonateid  = int(common.getid(request.vars.providerid))
    
    r = db((db.provider.id == impersonateid) & (db.provider.registered==True)).select()
    sitekey = r[0].sitekey
    
    r = db(db.auth_user.sitekey == sitekey).select()
    if(len(r) > 0):
        user_id = int(common.getstring(r[0].id))
        
    auth.user.id = user_id
    auth.user.sitekey = sitekey
    auth.user.impersonated = True
    auth.user.impersonatorid = impersonatorid
    
    providerdict = common.getprovider(auth, db);
    
    redirect(URL('admin','providerhome'))
    return dict()    

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()    
def superadmin():
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getstring(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])
    
    returnurl = URL('superadmin','superadmin')
    common.dashboard(db,session,providerid)
    
    #get list of all providers in PMS2
    query = ((db.provider.id >0) & (db.provider.is_active == True))
      
    fields=(db.provider.provider, db.provider.providername, db.provider.practicename,db.provider.cell,\
            db.provider.pa_practiceaddress,db.provider.registered)
    
    headers={ 'provider.provider':'Provider',
              'provider.providername':'Name',
              'provider.practicename':'Practice Name',
              'provider.cell':'Cell',
              'provider.pa_practiceaddress' : 'Address'
              }    
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)

    maxtextlengths = {'provider.provider':10, 'provider.providername':50, 'provider.practicename':100, 'provider.cell':10,'provider.pa_practiceaddress':250}
    
    links = [
               
               dict(header=CENTER('Login As'), body=lambda row:
                    
                    (CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("superadmin","impersonate",vars=dict(page=1,providerid=row.id))))\
                    if(row.registered == True) else "")
                    ),
               
               dict(header=CENTER('Treatment Payment Report'), body=lambda row: 
                    (CENTER(A(IMG(_src="/my_pms2/static/img/reports.png",_width=30, _height=30),_href=URL("reports","treatmentpaymentreport",vars=dict(page=1,providerid=row.id))))
               if(row.registered == True) else "")
               ),
               
               
               #dict(header=CENTER('Walk-in'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("superadmin","list_nonmembers",vars=dict(page=1,providerid=row.id))))),\
               #dict(header=CENTER('Case Papers'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/treatments.png",_width=25, _height=25),_href=URL('superadmin',"list_treatments",vars=dict(page=1,providerid=row.id))))),\
               #dict(header=CENTER('Images'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/x-rays.png",_width=25, _height=25),_href=URL("superadmin","list_dentalimages",vars=dict(page=0,providerid=row.id))))),\
               #dict(header=CENTER('Payments'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/payments.png",_width=25, _height=25),_href=URL("superadmin","list_payment",vars=dict(page=1, providerid=row.id))))),\
            ]    

    orderby = (db.provider.provider)
    
    db.provider.address1.readable = False
    db.provider.address1.writeable = False
    db.provider.address2.readable = False
    db.provider.address2.writeable = False
    db.provider.address3.readable = False
    db.provider.address3.writeable = False
    db.provider.st.readable = False
    db.provider.st.writeable = False
    db.provider.city.readable = False
    db.provider.city.writeable = False
    db.provider.telephone.readable = False
    db.provider.telephone.writeable = False
   
    db.provider.fax.readable = False
    db.provider.fax.writeable = False

    db.provider.taxid.readable = False
    db.provider.taxid.writeable = False
    db.provider.enrolleddate.readable = False
    db.provider.enrolleddate.writeable = False
    db.provider.assignedpatientmembers.readable = False
    db.provider.assignedpatientmembers.writeable = False
    db.provider.captguarantee.readable = False
    db.provider.captguarantee.writeable = False
    db.provider.schedulecapitation.readable = False
    db.provider.schedulecapitation.writeable = False
    db.provider.capitationytd.readable = False
    db.provider.capitationytd.writeable = False
    db.provider.captiationmtd.readable = False
    db.provider.captiationmtd.writeable = False
    db.provider.languagesspoken.readable = False
    db.provider.languagesspoken.writeable = False
    db.provider.specialization.readable = False
    db.provider.specialization.writeable = False
    db.provider.sitekey.readable = False
    db.provider.sitekey.writeable = False
    db.provider.groupregion.readable = False
    db.provider.pin.readable = False
    db.provider.pin.writeable = False
    db.provider.title.readable = False
    db.provider.title.writeable = False
    db.provider.pa_practiceaddress.represent=lambda v, r: '' if v is None else v
   
    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            maxtextlengths=maxtextlengths,
                            orderby=orderby,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            searchable=True,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            user_signature=True
                           )
    
    xsearch = form.element('input',_value='Search')
    xsearch['_class'] = 'form_details_button btn'
    xclear = form.element('input',_value='Clear')
    xclear['_class'] = 'form_details_button btn'
    xnew = form.element('input',_value='New Search')
    xnew['_class'] = 'form_details_button_black btn'
    xand = form.element('input',_value='+ And')
    xand['_class'] = 'form_details_button_black btn'
    xor = form.element('input',_value='+ Or')
    xor['_class'] = 'form_details_button_black btn'
    xclose = form.element('input',_value='Close')
    xclose['_class'] = 'form_details_button_black btn'    
    
       

    dashboard(providerid)
    
    today = datetime.date.today()
    formC =  SQLFORM.factory( 
            Field('activitydate', 'date',label='Activity Date',default=today, requires=[IS_NOT_EMPTY(), IS_DATE(format=T('%d/%m/%Y'))])
        )    
    
    return dict(form = form, formC=formC, returnurl=returnurl,page=1,providerid=providerid,providername=providername)

                #assignedprovs=assignedprovs,regprovs=regprovs,nonregprovs=nonregprovs,\
                #totmembers=totmembers,totwalkins=totwalkins,tottreatments=tottreatments,totcost=totcost,totpaid=totpaid,totdue=totdue)



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_patients():
    
    session.nonmemberscount=False
    
    providerid = int(common.getid(request.vars.providerid))
    providerdict = common.getproviderfromid(db,providerid)
    providername = providerdict["providername"]    
    
    page     = common.getgridpage(request.vars)
    member = common.getstring(request.vars.member)
    newmember = common.getboolean(request.vars.newmember)    
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    
    returnurl = URL('superadmin', 'superadmin')    
  
    
    members = db(((db.vw_memberpatientlist.providerid == providerid)&\
                        (db.vw_memberpatientlist.hmopatientmember == True)&\
                        (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt)&\
                        (db.vw_memberpatientlist.is_active == True))).count()    
    
    
    if((patientid != 0) & (memberid != 0)):
        if(newmember == True):
            query = ((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.hmopatientmember == True) & (db.vw_memberpatientlist.is_active == True) & \
                     (db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid) & \
                     (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) & (db.vw_memberpatientlist.newmember == True))
        else:
            query = ((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.hmopatientmember == True) & (db.vw_memberpatientlist.is_active == True) & \
                     (db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)&(datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )
            
    else:
        if(newmember == True):
            query = ((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.hmopatientmember == True) & (db.vw_memberpatientlist.is_active == True) & \
                     (datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) &  (db.vw_memberpatientlist.newmember == True))
        else:
            query = ((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.hmopatientmember == True)&(datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) & (db.vw_memberpatientlist.is_active == True))
            
    
    
    
    fields=(db.vw_memberpatientlist.fname,db.vw_memberpatientlist.lname,db.vw_memberpatientlist.patientmember,db.vw_memberpatientlist.hmoplanname, \
            db.vw_memberpatientlist.patientid,db.vw_memberpatientlist.premstartdt,db.vw_memberpatientlist.premenddt, \
            db.vw_memberpatientlist.primarypatientid,db.vw_memberpatientlist.gender,db.vw_memberpatientlist.cell\
            )    
    
    headers={
            'vw_memberpatientlist.patientmember':'Member ID',
   
            'vw_memberpatientlist.fname':'First Name',
            'vw_memberpatientlist.lname':'Last Name',
            'vw_memberpatientlist.cell':'Mobile',
            'vw_memberpatientlist.gender':'M/F',
            'vw_memberpatientlist.hmoplanname': 'Plan',
            'vw_memberpatientlist.premstartdt':'Prem. Start',
            'vw_memberpatientlist.premenddt':'Prem. End',
            }
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
    db.vw_memberpatientlist.id.readable = False
    db.vw_memberpatientlist.primarypatientid.readable = False 
    db.vw_memberpatientlist.patientid.readable = False 
    db.vw_memberpatientlist.patienttype.readable = False
    db.vw_memberpatientlist.fullname.readable = False
    db.vw_memberpatientlist.patient.readable = False
    db.vw_memberpatientlist.email.readable = False 
    db.vw_memberpatientlist.dob.readable = False 
    
    db.vw_memberpatientlist.regionid.readable = False
    
    db.vw_memberpatientlist.providerid.readable = False
    db.vw_memberpatientlist.is_active.readable = False
    db.vw_memberpatientlist.hmopatientmember.readable = False 
    
    db.vw_memberpatientlist.hmoplan.readable = False 
    db.vw_memberpatientlist.hmoplancode.readable = False 
    db.vw_memberpatientlist.company.readable = False 
    db.vw_memberpatientlist.newmember.readable = False 
    db.vw_memberpatientlist.freetreatment.readable = False 
    db.vw_memberpatientlist.age.readable = False 
    db.vw_memberpatientlist.totaltreatmentcost.readable = False 
    db.vw_memberpatientlist.totaldue.readable = False 
   
   
        
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)

    
   
   
    links = [
             #dict(header=CENTER('Edit'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("my_mydentalplan","member","member_update",args=[row.primarypatientid],vars=dict(page=page))))),\
             dict(header=CENTER('Case'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/treatments.png",_width=30, _height=30),_href=URL("superadmin","list_treatments",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername,status='Open'))))),\
             dict(header=CENTER('Image'),body=lambda row:CENTER(A(IMG(_src="/my_pms2/static/img/x-rays.png",_width=30, _height=30),_href=URL("superadmin","list_dentalimages",vars=dict(memberpage=page,page=0,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername))))),\
             #dict(header=CENTER('Reports'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/reports.png",_width=30, _height=30),_href=URL("reports","membertreatmentplansreport",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername)))))
             ]

    
    orderby = (db.vw_memberpatientlist.lname)

    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            orderby=orderby,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            searchable=True,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            ui = 'jquery-ui',                           
                            user_signature=True
                           )
  
    xsearch = form.element('input',_value='Search')
    xsearch['_class'] = 'form_details_button btn'
    xclear = form.element('input',_value='Clear')
    xclear['_class'] = 'form_details_button btn'
    xnew = form.element('input',_value='New Search')
    xnew['_class'] = 'form_details_button_black btn'
    xand = form.element('input',_value='+ And')
    xand['_class'] = 'form_details_button_black btn'
    xor = form.element('input',_value='+ Or')
    xor['_class'] = 'form_details_button_black btn'
    xclose = form.element('input',_value='Close')
    xclose['_class'] = 'form_details_button_black btn'
    
    
   
    
    return dict(form = form, returnurl=returnurl,page=page,providerid=providerid,providername=providername)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_nonmembers():

    session.nonmemberscount=True

  
    providerid = int(common.getid(request.vars.providerid))
    providerdict = common.getproviderfromid(db,providerid)
    providername = providerdict["providername"]    
    
    page     = common.getgridpage(request.vars)
    
    member = common.getstring(request.vars.member)
    patientid = common.getid(request.vars.patientid)
    memberid = common.getid(request.vars.memberid)
    
    returnurl = URL('superadmin', 'superadmin')    
    
    if((patientid != 0) & (memberid != 0)):
        query = ((db.vw_memberpatientlist.providerid == providerid) &  (db.vw_memberpatientlist.primarypatientid == memberid)  &  (db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.hmopatientmember == False) &  (db.vw_memberpatientlist.is_active == True))
    else:
        query = ((db.vw_memberpatientlist.providerid == providerid)  & (db.vw_memberpatientlist.hmopatientmember == False) &  (db.vw_memberpatientlist.is_active == True))
        
    #fields=(db.vw_memberpatientlist.fname,db.vw_memberpatientlist.lname,db.vw_memberpatientlist.patientmember,db.vw_memberpatientlist.cell,db.vw_memberpatientlist.email, \
            #db.vw_memberpatientlist.hmoplancode, db.vw_memberpatientlist.totaltreatmentcost,db.vw_memberpatientlist.totaldue,db.vw_memberpatientlist.primarypatientid,db.vw_memberpatientlist.patientid)    
    fields=(db.vw_memberpatientlist.fname,db.vw_memberpatientlist.lname,db.vw_memberpatientlist.patientmember,db.vw_memberpatientlist.cell, db.vw_memberpatientlist.gender,\
            db.vw_memberpatientlist.primarypatientid,db.vw_memberpatientlist.patientid)    
    
    headers={
            'vw_memberpatientlist.patientmember':'Member ID',
          
            'vw_memberpatientlist.fname':'First Name',
            'vw_memberpatientlist.lname':'Last Name',
            'vw_memberpatientlist.cell':'Mobile',
            'vw_memberpatientlist.gender':'M/F'
            }
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
   
    db.vw_memberpatientlist.id.readable = False
    db.vw_memberpatientlist.primarypatientid.readable = False 
    db.vw_memberpatientlist.patientid.readable = False 
    db.vw_memberpatientlist.patienttype.readable = False
    db.vw_memberpatientlist.fullname.readable = False
    db.vw_memberpatientlist.patient.readable = False

    db.vw_memberpatientlist.email.readable = False 
    db.vw_memberpatientlist.dob.readable = False 
    
    db.vw_memberpatientlist.regionid.readable = False
    
    db.vw_memberpatientlist.providerid.readable = False
    db.vw_memberpatientlist.is_active.readable = False
    db.vw_memberpatientlist.hmopatientmember.readable = False 
    
    db.vw_memberpatientlist.hmoplan.readable = False 
    db.vw_memberpatientlist.hmoplanname.readable = False 
    db.vw_memberpatientlist.hmoplancode.readable = False 
    db.vw_memberpatientlist.company.readable = False 
    db.vw_memberpatientlist.newmember.readable = False 
    db.vw_memberpatientlist.freetreatment.readable = False 
    db.vw_memberpatientlist.age.readable = False 
    db.vw_memberpatientlist.premstartdt.readable = False 
    db.vw_memberpatientlist.premenddt.readable = False 
    db.vw_memberpatientlist.totaltreatmentcost.readable = False 
    db.vw_memberpatientlist.totaldue.readable = False 
   
        
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
   
    links = [
             dict(header=CENTER('Open'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("superadmin","update_nonmember",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Case Paper'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/treatments.png",_width=30, _height=30),_href=URL("superadmin","list_treatments",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername,status='Open'))))),\
             dict(header=CENTER('Image'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/x-rays.png",_width=30, _height=30),_href=URL("superadmin","list_dentalimages",vars=dict(memberpage=page,page=0,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Reports'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/reports.png",_width=30, _height=30),_href=URL("reports","membertreatmentplansreport",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername,nonmember=True))))),
             ]

    
    orderby = (db.vw_memberpatientlist.lname)

    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            orderby=orderby,
                            exportclasses=exportlist,

                            links_in_grid=True,
                            searchable=True,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                           
                            user_signature=True
                           )
    
    xsearch = form.element('input',_value='Search')
    xsearch['_class'] = 'form_details_button btn'
    xclear = form.element('input',_value='Clear')
    xclear['_class'] = 'form_details_button btn'
    xnew = form.element('input',_value='New Search')
    xnew['_class'] = 'form_details_button_black btn'
    xand = form.element('input',_value='+ And')
    xand['_class'] = 'form_details_button_black btn'
    xor = form.element('input',_value='+ Or')
    xor['_class'] = 'form_details_button_black btn'
    xclose = form.element('input',_value='Close')
    xclose['_class'] = 'form_details_button_black btn'    
    return dict(form = form, returnurl=returnurl,page=page,providerid=providerid,providername=providername)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_treatments():

    
    page     = common.getgridpage(request.vars)
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    providerid = int(common.getid(request.vars.providerid))
    providerdict = common.getproviderfromid(db,providerid)
    providername = providerdict["providername"]
    imagepage = 0

    
    if(patientid == 0):
        query = ((db.vw_treatmentlist.providerid == providerid) & (db.vw_treatmentlist.is_active == True))
        returnurl = URL('superadmin', 'list_treatments', vars=dict(page=page,imagepage=imagepage,providerid=providerid))  
    else:
        query = ((db.vw_treatmentlist.providerid == providerid) & (db.vw_treatmentlist.patientid == patientid) & (db.vw_treatmentlist.is_active == True))
        returnurl = URL('superadmin', 'list_treatments', vars=dict(page=page,imagepage=imagepage,providerid=providerid,memberid=memberid,patientid=patientid))  
    
    fields=(db.vw_treatmentlist.patientname,db.vw_treatmentlist.treatment,db.vw_treatmentlist.chiefcomplaint,db.vw_treatmentlist.startdate,db.vw_treatmentlist.dentalprocedure, db.vw_treatmentlist.shortdescription, db.vw_treatmentlist.memberid,
            db.vw_treatmentlist.treatmentplan,db.vw_treatmentlist.status,db.vw_treatmentlist.treatmentcost,db.vw_treatmentlist.memberid,db.vw_treatmentlist.patientid,db.vw_treatmentlist.tplanid)

    headers={
        'vw_treatmentlist.treatment':'Case No.',
        'vw_treatmentlist.chiefcomplaint':'Complaint',
        'vw_treatmentlist.patientname':'Patient',
        'vw_treatmentlist.startdate':'Case Date',
        'vw_treatmentlist.treatmentcost':'Cost',
                }

    db.vw_treatmentlist.status.readable = False
    db.vw_treatmentlist.treatmentplan.readable = False
    
    db.vw_treatmentlist.memberid.readable = False
    db.vw_treatmentlist.patientid.readable = False
    db.vw_treatmentlist.providerid.readable = False
    db.vw_treatmentlist.is_active.readable = False
    db.vw_treatmentlist.providerid.readable = False

    db.vw_treatmentlist.treatmentcost.readable = False
    db.vw_treatmentlist.tplanid.readable = False
    db.vw_treatmentlist.memberid.readable = False
    
    db.vw_treatmentlist.dentalprocedure.readable = False
    db.vw_treatmentlist.shortdescription.readable = False
    
    
    links = [\
           dict(header=CENTER("Open"), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("superadmin","update_treatment",vars=dict(page=page,imagepage=imagepage,treatmentid=row.id, providerid=providerid))))),
           dict(header=CENTER('Payment'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/payments.png",_width=30, _height=30),_href=URL("superadmin","list_payment",vars=dict(page=page,tplanid=row.tplanid,providerid=providerid,providername=providername,memberid=row.memberid,patientid=row.patientid))))),\
    ]

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
    returnurl =  URL('superadmin', 'superadmin')
     
    orderby = ~db.vw_treatmentlist.startdate
    
    maxtextlengths = {'vw_treatmentlist.treatment':50}
       
    form = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        paginate=10,
                        maxtextlengths=maxtextlengths,
                        orderby=orderby,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )

    xsearch = form.element('input',_value='Search')
    xsearch['_class'] = 'form_details_button btn'
    xclear = form.element('input',_value='Clear')
    xclear['_class'] = 'form_details_button btn'
    xnew = form.element('input',_value='New Search')
    xnew['_class'] = 'form_details_button_black btn'
    xand = form.element('input',_value='+ And')
    xand['_class'] = 'form_details_button_black btn'
    xor = form.element('input',_value='+ Or')
    xor['_class'] = 'form_details_button_black btn'
    xclose = form.element('input',_value='Close')
    xclose['_class'] = 'form_details_button_black btn'

    dashboard(providerid)
  
    return dict(form = form, returnurl=returnurl,page=page,providerid=providerid,providername=providername,memberid=memberid,patientid=patientid)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_dentalimages():

    is_active    = True
   
    memberpage   = int(common.getpage(request.vars.memberpage))
    page         = int(common.getpage(request.vars.page))
    
    
    providerid   = int(common.getnegid(request.vars.providerid))
    provdict     = common.getproviderfromid(db, request.vars.providerid)
    providername = provdict["providername"]
    
    memberid     = int(common.getid(request.vars.memberid))
    patientid    = int(common.getid(request.vars.patientid))
    
    memberref    = common.getstring(request.vars.memberref)
    
    patient = common.getstring(request.vars.patient)
    fullname = common.getstring(request.vars.fullname)
    
    #display treatment plan filtering criteria
    items_per_page = 4
    limitby = ((page)*items_per_page,(page+1)*items_per_page)     

    rows = None
    if(memberid > 0):
        if(patientid > 0):
            sqlquery = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.is_active == True))
            rows = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.is_active == True)).select()
            if(len(rows) > 0):
                fullname = common.getstring(rows[0].fullname)
                patient = common.getstring(rows[0].patient)
                memberid = int(common.getid(rows[0].primarypatientid))
        else:
            sqlquery = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == memberid) & (db.vw_memberpatientlist.is_active == True))
            rows = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == memberid) & (db.vw_memberpatientlist.is_active == True)).select()
            if(len(rows) > 0):
                fullname = common.getstring(rows[0].fullname)
                patient = common.getstring(rows[0].patient)
                memberid = int(common.getid(rows[0].primarypatientid))
                patientid = memberid
            
    else:
        sqlquery = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True))
        rows = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).select()
    
    form = SQLFORM.factory(
               Field('patientmember', 'string',  default=fullname, label='Patient'),#requires=[IS_NOT_EMPTY(),IS_IN_DB(sqlquery,'vw_memberpatientlist.fullname')]),
               Field('xmemberid', 'string',  label='Patient ID',default=memberid),
               Field('xpatientmember', 'string', default=patient, label='XPatient'),
               Field('xfullname', 'string', default=fullname, label='XPatient'),
               
    )
       
    xpatientmember = form.element('#no_table_patientmember')
    xpatientmember['_class'] = 'w3-input w3-border'
    xpatientmember['_placeholder'] = 'Enter Patient Name - First Name Last Name'
    xpatientmember['_autocomplete'] = 'off' 

    if form.accepts(request,session,keepvalues=True):
        memberid = 0
        patientid = 0

        limitby = ((page)*items_per_page,(page+1)*items_per_page) 
        r = db((db.vw_memberpatientlist.patient == form.vars.xpatientmember.strip()) & (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).select()
        if(len(r) > 0):
            memberid = int(common.getid(r[0].primarypatientid))
            patientid = int(common.getid(r[0].patientid))
            memberref = common.getstring(r[0].patientmember)  #patientmember
            fullname = common.getstring(r[0].fullname)      #fname + lname
            patient = common.getstring(r[0].patient)    #fname + lname + patientmemebr
            
    
    images = getimages(db, providerid, patientid, limitby, is_active)    
    imagescount = len(images)
    totalimages  = 0
    
    if(patientid > 0):
        totalimages = db((db.dentalimage.provider == providerid) & (db.dentalimage.patient == patientid) & (db.dentalimage.image != None) & (db.dentalimage.image != "") &\
                         (db.dentalimage.is_active == True)).count()
    else:
        totalimages = db((db.dentalimage.provider == providerid) & (db.dentalimage.image != None) & (db.dentalimage.image != "") &\
                         (db.dentalimage.is_active == True)).count()    
    session.images = totalimages
    
    
    if(len(images) > 0):
        rangemssg = "Displaying images from  " + str(int(common.getvalue(limitby[0]))+1) + "  to  " + str(int(common.getvalue(limitby[1]))) + "(" + str(totalimages) + ")"
    else:
        rangemssg = "No images to display"

    if(memberpage == 0)    :
        returnurl =  URL('superadmin','superadmin')    
    else:    
        if(session.nonmemberscount == True):
            returnurl =  URL('superadmin','list_nonmembers', vars=dict(providerid=providerid,page=memberpage))    
        else:
            returnurl =  URL('superadmin','list_members', vars=dict(providerid=providerid,page=memberpage))    
    
    
    return dict(form=form, images=images, returnurl=returnurl, page=page, items_per_page=items_per_page, limitby=limitby, rangemssg=rangemssg,memberpage=memberpage, memberid=memberid, patientid=patientid, memberref=memberref,fullname=fullname,providerid=providerid, providername=providername,patient=patient)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_payment():
    
    page = int(request.vars.page)
    returnurl = URL('superadmin', 'superadmin')
    
    providerid   = int(common.getnegid(request.vars.providerid))
    provdict     = common.getproviderfromid(db, request.vars.providerid)
    providername = provdict["providername"]
    
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))  
    tplanid = int(common.getid(request.vars.tplanid))
    
    totalcost =0
    totaldue = 0
    totalpaid = 0
    
    fullname = common.getstring(request.vars.fullname)  #FirstName LastName
    patient = common.getstring(request.vars.patient)  #FirstName LastName:MemberID
    memberref = "" #MemberID
    

    r = db((db.vw_memberpatientlist.providerid==providerid)&(db.vw_memberpatientlist.patientid==patientid)&(db.vw_memberpatientlist.primarypatientid==memberid)&(db.vw_memberpatientlist.is_active==True)).select()
    if(len(r)>0):
        memberref = common.getstring(r[0].patientmember)  #patientmember
        fullname = common.getstring(r[0].fullname)      #fname + lname
        patient = common.getstring(r[0].patient)    #fname + lname + patientmemebr
    
    form = SQLFORM.factory(
                 Field('patientmember', 'string',  default=fullname, label='Patient'),
                 Field('xpatientmember', 'string', default=patient, label='XPatient')
                 
      )
         
    xpatientmember = form.element('#no_table_patientmember')
    xpatientmember['_class'] = 'form-control'
    xpatientmember['_placeholder'] = 'Enter Patient Name - First Name Last Name'
    xpatientmember['_autocomplete'] = 'off'     

    if(memberid >= 0):
        formA = getpaymentgrid(tplanid, patientid,patient,fullname,memberid,providerid,providername,page)
    else:
        formA = None
    
    if form.accepts(request,session,keepvalues=True):
        patientmember = ""
        r = db((db.vw_memberpatientlist.patient == form.vars.xpatientmember.strip()) & (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).select()
        if(len(r) > 0):
            memberid = int(common.getid(r[0].primarypatientid))
            patientid = int(common.getid(r[0].patientid))
            memberref = common.getstring(r[0].patientmember)  #patientmember
            fullname = common.getstring(r[0].fullname)      #fname + lname
            patient = common.getstring(r[0].patient)    #fname + lname + patientmemebr
        

            #Get Payments for the Member
            formA = getpaymentgrid(tplanid, patientid,patient,fullname,memberid,providerid,providername,page)
    
    
    totalcost =0
    totaldue = 0
    totalpaid = 0
    
    if(memberid > 0):
        r = db((db.vw_paymentsummary1.provider == providerid) & (db.vw_paymentsummary1.patientmember == memberid)).select()
        if(len(r) > 0):
            totalcost = float(common.getvalue(r[0].totalcost))
            totalpaid = float(common.getvalue(r[0].totalpaid))
            totaldue = totalcost - totalpaid

            
    return dict(form=form, formA=formA, page=page,returnurl=returnurl,providername=providername, providerid=providerid,memberid=memberid,patientid=patientid,patient=patient, fullname=fullname,tplanid=tplanid,\
                totalcost=totalcost,totaldue=totaldue,totalpaid=totalpaid)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def update_treatment():
    
    
    memberid = 0
    patientid = 0
    procedureid = 0
    ucrfee = 0    
    tplanid = 0
    doctorid = 0
    
    patienttype = 'P'
    patientmember = ''
    membername = ''
    patientname = ''
    fullname = ''
    patient = ''
    doctorname = ''
    altshortdescription = ''
    title = ''
    
    #provider : logged in
    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getprovider(auth, db)
    providername  = provdict["providername"]
    
    treatment = ""
    
    #page
    page       = int(common.getpage(request.vars.page)) 
    imagepage  = int(common.getpage(request.vars.imagepage))
 
    dob = ""
    cell = ""
    email = ""
    telephone = ""
    address1 = ""
    address2 = ""
    address3 = ""
    city = ""
    st = ""
    pin = ""
    
    medicalalert = False
    
    rows = None
    
    returnurl = URL('superadmin','list_treatments',vars=dict(page=page,providerid=providerid,memberid=memberid,patientid=patientid))
    
      
    #treatmentid,treatment, memberid,patientid,patientmember,membername, patientname, patienttype
    treatmentid = int(common.getid(request.vars.treatmentid))
    treatments = db(db.treatment.id == treatmentid).select()
    
    totaltreatmentcost = 0
    totalactualtreatmentcost = 0
    
    
    procedurepriceplancode = "PREMWALKIN"
    remarks = ""
    patienttype = 'P'
    if(len(treatments) > 0):
        treatment = common.getstring(treatments[0].treatment)
        tplanid = int(common.getid(treatments[0].treatmentplan))
        procedureid = int(common.getid(treatments[0].dentalprocedure))
        doctorid = int(common.getid(treatments[0].doctor))
        docs=db(db.doctor.id == doctorid).select(db.doctor.name)
        totaltreatmentcost = float(common.getvalue(treatments[0].treatmentcost)) #this is the actual treatment cost = total treatment cost unless it is changed by provider
        totalactualtreatmentcost = float(common.getvalue(treatments[0].actualtreatmentcost))   #this is total UCRR
        
        #if(totaltreatmentcost == 0):
            #totaltreatmentcost = totalactualtreatmentcost
            
        procs = db(db.vw_procedurepriceplan.id == procedureid).select()  
        if(len(procs) > 0):
            ucrfee = common.getvalue(procs[0].ucrfee)
            altshortdescription = common.getstring(procs[0].altshortdescription)
            remarks =  common.getstring(procs[0].remarks)
       
        tplans = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.provider==providerid) & (db.treatmentplan.is_active == True)).select()
        
        if(len(tplans) > 0):
            memberid = tplans[0].primarypatient
            patientid = tplans[0].patient
            patienttype = tplans[0].patienttype
            patientname = tplans[0].patientname.strip()
            
            rows = db((db.vw_memberpatientlist.primarypatientid == memberid)&(db.vw_memberpatientlist.patientid == patientid)&(db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).\
                select()
            
            if(len(rows)>0):
                title = rows[0].title
                fullname = rows[0].fullname.strip()
                patientmember = rows[0].patientmember.strip()
                patient = rows[0].patient.strip()
                membername = rows[0].fullname.strip()
                procedurepriceplancode = rows[0].procedurepriceplancode
                
        
        #medical alerts
        medicalalerts = False
        alerts = db((db.medicalnotes.patientid == patientid) & (db.medicalnotes.memberid == memberid)).select()
        if(len(alerts)>0):
            medicalalerts = medicalalerts | common.getboolean(alerts[0].allergic)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].bp)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].heart)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].cardiac)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].diabetes)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].anyother)
       
            
        formTreatment = SQLFORM.factory(
           Field('patientmember', 'string',  label='Patient', default = fullname,\
                 requires=[IS_NOT_EMPTY(),IS_IN_DB(db(db.vw_memberpatientlist.providerid == providerid), 'vw_memberpatientlist.fullname','%(fullname)s')],writable=False),
           Field('xmemberid', 'string',  label='Member',default=memberid),
           Field('treatment','string',label='Case No.', default=treatments[0].treatment),
           Field('chiefcomplaint','string',label='Chief Complaint', default=treatments[0].chiefcomplaint),
           Field('description','text', label='Description', default=treatments[0].description),
           #Field('quadrant','string', label='Quadrant(s)', default=treatments[0].quadrant),
           #Field('tooth','string', label='Tooth/Teeth', default=treatments[0].tooth),
           Field('startdate', 'date', label='From Date',default=treatments[0].startdate, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
           #Field('enddate', 'date', label='To Date',default=treatments[0].enddate, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
           #Field('status', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border '),label='Status',default=treatments[0].status, requires = IS_IN_SET(status.TREATMENTSTATUS)),  
           Field('ucrfee', 'double', label='Total UCR',default=totalactualtreatmentcost,writable=False),  
           Field('treatmentcost', 'double', label='Total Treament Cost',default=totaltreatmentcost),  
           Field('copay', 'double', label='Total Copay',default=treatments[0].copay, writable = False),  
           Field('inspay', 'double', label='Total Ins. Pays',default=treatments[0].inspay, writable=False),  
           Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
           Field('remarks', 'string', default = remarks, writable=False)
           #Field('vwdentalprocedure', 'string',   default=altshortdescription, label='Procedure ID',requires=[IS_NOT_EMPTY(),IS_IN_DB(db((db.vw_procedurepriceplan.procedurepriceplancode==procedurepriceplancode)&(db.vw_procedurepriceplan.is_active == True)),'vw_procedurepriceplan.altshortdescription','%(altshortdescription)s')])
           )    
    else:
        formTreatment = SQLFORM.factory(
           Field('patientmember', 'string',  label='Patient', default = fullname,\
                 requires=[IS_NOT_EMPTY(),IS_IN_DB(db(db.vw_memberpatientlist.providerid == providerid), 'vw_memberpatientlist.fullname','%(fullname)s')],writable=False),
           Field('xmemberid', 'string',  label='Member',default=memberid),
           Field('treatment','string',label='Case No.'),
           Field('chiefcomplaint','string',label='Chief Complaint'),
           Field('description','text', label='Description'),
           #Field('quadrant','string', label='Quadrant(s)'),
           #Field('tooth','string', label='Tooth/Teeth'),
           Field('startdate', 'date', label='From Date', requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
           #Field('enddate', 'date', label='To Date',requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
           #Field('status', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border '),label='Status'),  
           Field('ucrfee', 'double', label='UCR',default=0),  
           Field('treatmentcost', 'double', label='Total Treament Cost'),  
           Field('copay', 'double', label='Total Copay', writable = False),  
           Field('inspay', 'double', label='Total Ins. Pays'),  
           Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
           Field('remarks', 'string', default = remarks)
           #Field('vwdentalprocedure', 'string',  default=altdescription,  label='Procedure ID',requires=[IS_NOT_EMPTY(),IS_IN_DB(db(db.vw_dentalprocedure.is_active == True),'vw_dentalprocedure.altshortdescription','%(altshortdescription)s')])
           )    
        
    formTreatment.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    formTreatment.element('textarea[name=description]')['_rows'] = 5
    formTreatment.element('textarea[name=description]')['_class'] = 'form-control'

    #xvwdentalprocedure = formTreatment.element('input',_id='no_table_vwdentalprocedure')
    #xvwdentalprocedure['_class'] =  'form-control '
    #xvwdentalprocedure['_placeholder'] = 'Enter Dental Procedure Name/Code' 
    #xvwdentalprocedure['_autocomplete'] = 'off'

    doc = formTreatment.element('#no_table_doctor')
    doc['_class'] = 'form-control'
    doc['_style'] = 'width:100%'
    

    #ucr = formTreatment.element('#no_table_ucrfee')
    #ucr['_class'] = 'form-control'
    #ucr['_style'] = 'width:100%'

    #xquadrant = formTreatment.element('input',_id='no_table_quadrant')
    #xquadrant['_class'] =  'form-control'
    #xquadrant['_type'] =  'text'
    #xquadrant['_placeholder'] = 'Enter Dental Quadrant Q1,Q2,Q3,Q4' 
    #xquadrant['_autocomplete'] = 'off' 

    #xtooth = formTreatment.element('input',_id='no_table_tooth')
    #xtooth['_class'] =  'form-control'
    #xtooth['_type'] =  'text'
    #xtooth['_placeholder'] = 'Enter Dental Tooth T1 to T32' 
    #xtooth['_autocomplete'] = 'off' 
    
    xstartdate = formTreatment.element('input',_id='no_table_startdate')
    xstartdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xstartdate['_data-date-format'] = 'dd/mm/yyyy'
    xstartdate['_autocomplete'] = 'off' 


    #xenddate = formTreatment.element('input',_id='no_table_enddate')
    #xenddate['_class'] =  'input-group form-control form-control-inline date-picker'
    #xenddate['_data-date-format'] = 'dd/mm/yyyy'
    #xenddate['_autocomplete'] = 'off' 
    
    xtreatmentcost = formTreatment.element('input',_id='no_table_treatmentcost')
    xtreatmentcost['_class'] =  'form-control'
    xtreatmentcost['_type'] =  'text'
    xtreatmentcost['_autocomplete'] = 'off' 
    
    xtreatment = formTreatment.element('input',_id='no_table_treatment')
    xtreatment['_class'] =  'form-control'
    xtreatment['_type'] =  'text'
    xtreatment['_autocomplete'] = 'off' 

    cc = formTreatment.element('input', _id='no_table_chiefcomplaint')
    cc['_class'] = 'form-control'
    cc['_style'] = 'width:100%'
    cc['_type'] =  'text'
  
    # procedures grid
    query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True))
    fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription,db.vw_treatmentprocedure.ucrfee, \
               db.vw_treatmentprocedure.procedurefee,db.vw_treatmentprocedure.copay,db.vw_treatmentprocedure.inspays,\
               db.vw_treatmentprocedure.remarks,db.vw_treatmentprocedure.treatmentdate)
            

    headers={
        'vw_treatmentprocedure.procedurecode':'Code',
        'vw_treatmentprocedure.altshortdescription':'Description',
        'vw_treatmentprocedure.ucrfee':'UCR',
        'vw_treatmentprocedure.procedurefee':'Procedure Cost',
        'vw_treatmentprocedure.copay':'Co-Pay',
        'vw_treatmentprocedure.inspays':'Inusrance Pays',
        'vw_treatmentprocedure.remarks':'Remarks',
        'vw_treatmentprocedure.treatmentdate':'Treatment Date'
    }
    
    links = [\
            dict(header=CENTER('Edit'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=30, _height=30),\
                                                               _href=URL("treatment","update_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid))))),
            dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),\
                                                                  _href=URL("treatment","delete_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid)))))
    ]

    links = None
    maxtextlengths = {'vw_treatmentprocedure.altshortdescription':50}
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
       
    formProcedure = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        paginate=10,
                        maxtextlengths=maxtextlengths,
                        orderby=None,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )  
  
    if formTreatment.accepts(request,session=session,formname='formtreatment',keepvalues=True):
        treatmentcost = float(common.getvalue(formTreatment.vars.treatmentcost))
        doctorid = int(common.getid(formTreatment.vars.doctor))
        docs = db(db.doctor.id == doctorid).select()
        doctorname = docs[0].name
        
        db(db.treatment.id == treatmentid).update(\
            treatment = formTreatment.vars.treatment,
            chiefcomplaint = formTreatment.vars.chiefcomplaint,
            description  = formTreatment.vars.description,
            startdate = formTreatment.vars.startdate,
            enddate = formTreatment.vars.enddate,
            status = formTreatment.vars.status,
            actualtreatmentcost = 0,
            treatmentcost = treatmentcost,
            quadrant = '',
            tooth = '',
            dentalprocedure = 0, 
            doctor = doctorid,
            modified_on = common.getISTFormatCurrentLocatTime(),
            modified_by = providerid,
        
        )    
        updatetreatmentcostandcopay(treatmentid)
        calculatecost(tplanid)
        calculatecopay(db, tplanid,memberid)
        calculateinspays(tplanid)
        calculatedue(tplanid)
        
        db.commit()                
    
        db.treatmentnotes.update_or_insert(db.treatmentnotes.treatment == treatmentid, treatment = treatmentid, notes = formTreatment.vars.prescription)   
 
        csrdate = (request.now).strftime('%d/%m/%Y %H:%M:%S')
        csr = csrdate + " : " + "CSR:"  + treatment + "\r\n" + "Doctor: " + doctorname + "\r\n" + formTreatment.vars.description
        csrid = db.casereport.insert(patientid = patientid, providerid=providerid, doctorid=doctorid, casereport = csr, is_active=True,\
                                      created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid)
        
        session.flash = "Case Paper Details Updated!"
        
        redirect(returnurl)

    elif formTreatment.errors:
        session.flash = "Error - Case Paper Update! " + str(formTreatment.errors)
        redirect(returnurl)
        
    #====== Notes Foem
    
    dob = ""
    age = ""
    xgender = ""
    
    if((rows[0].dob != None) & (rows[0].dob != "")):    
        dob = common.getstring(rows[0].dob)
        age = common.getstring(getage(rows[0].dob))
        
    xgender = common.getstring(rows[0].gender)    
    
    memrows = db(db.patientmember.id == memberid).select()
    address = ""
    telephone  = ""
    if(len(memrows)>0):
        addr1 = common.getstring(memrows[0].address1)
        addr2 = common.getstring(memrows[0].address2)
        addr3 = common.getstring(memrows[0].address3)
        city = common.getstring(memrows[0].city)
        st = common.getstring(memrows[0].st)
        pin = common.getstring(memrows[0].pin)
        address = addr1 + " " + addr2 + " " + addr3 + ",\r\n" + city + ", " + st + " " + pin
        telephone = common.getstring(memrows[0].telephone)
    
    notes = db((db.medicalnotes.patientid == patientid) & (db.medicalnotes.memberid == memberid)).select()
    if(len(notes) < 0) :
        redirect(returnurl)
        
    if(len(notes)>0):
        formNotes = SQLFORM.factory(
            Field('patientmember', 'string',  label='Patient', default = fullname,writable=False),
            Field('notesdate', 'date', label='To Date',default=datetime.date.today(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
            Field('dob', 'date', label='To Date',default=rows[0].dob, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
            Field('age', 'string', default=age),
            Field('cell', 'string', default=common.getstring(rows[0].cell)),
            Field('email', 'string', default=common.getstring(rows[0].email)),
            Field('telephone', 'string', default=telephone),
            Field('occupation', 'string', default=common.getstring(notes[0].occupation)),
            Field('xgender', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form-control '),label='Gender',default=xgender, requires = IS_IN_SET(gender.GENDER)),
            Field('address','text', label='Address', default=address),
            Field('referer','string', label='Doctor/Fried', default=common.getstring(notes[0].referer)),
            Field('resoff','string', label='Residence/Office', default=common.getstring(notes[0].resoff)),
            Field('bp','boolean', default = common.getboolean(notes[0].bp)),
            Field('diabetes','boolean', default = common.getboolean(notes[0].diabetes)),
            Field('anaemia','boolean', default = common.getboolean(notes[0].anaemia)),
            Field('epilepsy','boolean', default = common.getboolean(notes[0].epilepsy)),
            Field('asthma','boolean', default = common.getboolean(notes[0].asthma)),
            Field('sinus','boolean', default = common.getboolean(notes[0].sinus)),
            Field('heart','boolean', default = common.getboolean(notes[0].heart)),
            Field('jaundice','boolean', default = common.getboolean(notes[0].jaundice)),
            Field('tb','boolean', default = common.getboolean(notes[0].tb)),
            Field('cardiac','boolean', default = common.getboolean(notes[0].cardiac)),
            Field('arthritis','boolean', default = common.getboolean(notes[0].arthritis)),
            Field('anyother','boolean', default = common.getboolean(notes[0].anyother)),
            Field('allergic','boolean', default = common.getboolean(notes[0].allergic)),
            Field('excessivebleeding','boolean', default = common.getboolean(notes[0].excessivebleeding)),
            Field('seriousillness','boolean', default = common.getboolean(notes[0].seriousillness)),
            Field('hospitalized','boolean', default = common.getboolean(notes[0].hospitalized)),
            Field('medications','boolean', default = common.getboolean(notes[0].medications)),
            Field('surgery','boolean', default = common.getboolean(notes[0].surgery)),
            Field('pregnant','boolean', default = common.getboolean(notes[0].pregnant)),
            Field('breastfeeding','boolean', default = common.getboolean(notes[0].breastfeeding)),
            Field('anyothercomplaint','text',represent=lambda v, r: '' if v is None else v, default=common.getstring(notes[0].anyothercomplaint)),
            Field('chiefcomplaint','text',represent=lambda v, r: '' if v is None else v, default=common.getstring(notes[0].chiefcomplaint)),
            Field('duration','text', represent=lambda v, r: '' if v is None else v, default=common.getstring(notes[0].duration)),
            Field('is_active','boolean', default = True)
        )  
    else:
        formNotes = SQLFORM.factory(
            Field('patientmember', 'string',  label='Patient', default = fullname,writable=False),
            Field('notesdate', 'date', label='To Date',default=datetime.date.today(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
            Field('dob', 'date', label='To Date',default=rows[0].dob, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
            Field('age', 'string', default=age),
            Field('cell', 'string', default=common.getstring(rows[0].cell)),
            Field('email', 'string', default=common.getstring(rows[0].email)),
            Field('telephone', 'string', default=telephone),
            Field('occupation', 'string', default=""),
            Field('xgender', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form-control '),label='Gender',default="Male", requires = IS_IN_SET(gender.GENDER)),
            Field('address','text', label='Address', default=""),
            Field('referer','string', label='Doctor/Fried', default=""),
            Field('resoff','string', label='Residence/Office', default=""),
            Field('bp','boolean', default = ""),
            Field('diabetes','boolean', default = ""),
            Field('anaemia','boolean', default = ""),
            Field('epilepsy','boolean', default = ""),
            Field('asthma','boolean', default = ""),
            Field('sinus','boolean', default = ""),
            Field('heart','boolean', default = ""),
            Field('jaundice','boolean', default = ""),
            Field('tb','boolean', default = ""),
            Field('cardiac','boolean', default = ""),
            Field('arthritis','boolean', default = ""),
            Field('anyother','boolean', default = ""),
            Field('allergic','boolean', default = ""),
            Field('excessivebleeding','boolean', default = ""),
            Field('seriousillness','boolean', default = ""),
            Field('hospitalized','boolean', default = ""),
            Field('medications','boolean', default = ""),
            Field('surgery','boolean', default = ""),
            Field('pregnant','boolean', default = ""),
            Field('breastfeeding','boolean', default = ""),
            Field('anyothercomplaint','text',represent=lambda v, r: '' if v is None else v, default=""),
            Field('chiefcomplaint','text',represent=lambda v, r: '' if v is None else v, default=""),
            Field('duration','text', represent=lambda v, r: '' if v is None else v, default=""),
            Field('is_active','boolean', default = True)
        )  
        
    
    formNotes.element('textarea[name=anyothercomplaint]')['_style'] = 'height:50px;line-height:1.0;'
    formNotes.element('textarea[name=anyothercomplaint]')['_rows'] = 2
    formNotes.element('textarea[name=anyothercomplaint]')['_class'] = 'form-control' 
    
    formNotes.element('textarea[name=chiefcomplaint]')['_style'] = 'height:60px;line-height:1.0;'
    formNotes.element('textarea[name=chiefcomplaint]')['_rows'] = 3
    formNotes.element('textarea[name=chiefcomplaint]')['_class'] = 'form-control' 

    
    formNotes.element('textarea[name=duration]')['_style'] = 'height:60px;line-height:1.0;'
    formNotes.element('textarea[name=duration]')['_rows'] = 3
    formNotes.element('textarea[name=duration]')['_class'] = 'form-control' 

    

    xnotesdate = formNotes.element('input',_id='no_table_notesdate')
    xnotesdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xnotesdate['_data-date-format'] = 'dd/mm/yyyy'
    xnotesdate['_autocomplete'] = 'off'  

    
    xdob = formNotes.element('input',_id='no_table_dob')
    xdob['_class'] =  'input-group form-control form-control-inline date-picker'
    xdob['_data-date-format'] = 'dd/mm/yyyy'
    xdob['_autocomplete'] = 'off'  
    
    xage = formNotes.element('input',_id='no_table_age')
    xage['_class'] =  'form-control'
    xage['_type'] =  'text'
    xage['_placeholder'] = 'Enter Dental Tooth T1 to T32' 
    xage['_autocomplete'] = 'off'     

    xcell = formNotes.element('input',_id='no_table_cell')
    xcell['_class'] =  'form-control'
    xcell['_type'] =  'text'
    
    xemail = formNotes.element('input',_id='no_table_email')
    xemail['_class'] =  'form-control'
    xemail['_type'] =  'text'
    
    xtel = formNotes.element('input',_id='no_table_telephone')
    xtel['_class'] =  'form-control'
    xtel['_type'] =  'text'

    xocc = formNotes.element('input',_id='no_table_occupation')
    xocc['_class'] =  'form-control'
    xocc['_type'] =  'text'

    xref = formNotes.element('input',_id='no_table_referer')
    xref['_class'] =  'form-control'
    xref['_type'] =  'text'
    
    xresoff = formNotes.element('input',_id='no_table_resoff')
    xresoff['_class'] =  'form-control'
    xresoff['_type'] =  'text'
    
    formNotes.element('textarea[name=address]')['_style'] = 'height:100px;line-height:1.0;'
    formNotes.element('textarea[name=address]')['_rows'] = 3
    formNotes.element('textarea[name=address]')['_class'] = 'form-control'

    if formNotes.accepts(request,session=session,formname='formnotes',keepvalues=True):
        
        patientid = int(common.getid(request.vars.notes_patientid))
        memberid = int(common.getid(request.vars.notes_memberid))
        providerid = int(common.getid(request.vars.notes_providerid))
        
       

        
        db.medicalnotes.update_or_insert(((db.medicalnotes.patientid == patientid) & (db.medicalnotes.memberid == memberid) & (db.medicalnotes.is_active == True)),
                                         patientid = patientid,
                                         memberid = memberid,
                                         bp = common.getboolean(formNotes.vars.bp),
                                         diabetes = common.getboolean(formNotes.vars.diabetes),
                                         anaemia = common.getboolean(formNotes.vars.anaemia),
                                         epilepsy = common.getboolean(formNotes.vars.epilepsy),
                                         asthma = common.getboolean(formNotes.vars.asthma),
                                         sinus = common.getboolean(formNotes.vars.sinus),\
                                         heart = common.getboolean(formNotes.vars.heart),\
                                         jaundice = common.getboolean(formNotes.vars.jaundice),\
                                         tb = common.getboolean(formNotes.vars.tb),\
                                         cardiac = common.getboolean(formNotes.vars.cardiac),\
                                         arthritis = common.getboolean(formNotes.vars.arthritis),\
                                         anyother = common.getboolean(formNotes.vars.anyother),\
                                         allergic = True if request.vars.allergic == "1" else False,\
                                         excessivebleeding = True if request.vars.excessivebleeding == "1" else False,\
                                         seriousillness = True if request.vars.seriousillness == "1" else False,\
                                         hospitalized = True if request.vars.hospitalized == "1" else False,\
                                         medications = True if request.vars.medications == "1" else False,\
                                         surgery = True if request.vars.surgery == "1" else False,\
                                         pregnant = True if request.vars.pregnant == "1" else False,\
                                         breastfeeding = True if request.vars.breastfeeding == "1" else False,\
                                         anyothercomplaint = common.getstring(formNotes.vars.anyothercomplaint),\
                                         chiefcomplaint = common.getstring(formNotes.vars.chiefcomplaint),\
                                         duration = common.getstring(formNotes.vars.duration),\
                                         occupation = common.getstring(formNotes.vars.occupation),\
                                         referer = common.getstring(formNotes.vars.referer),\
                                         resoff = common.getstring(formNotes.vars.resoff),\
                                         is_active = True,\
                                         created_on = common.getISTFormatCurrentLocatTime(),\
                                         created_by = providerid,\
                                         modified_on = common.getISTFormatCurrentLocatTime(),\
                                         modified_by = providerid
                                         )   
        db.commit()
        redirect(returnurl)
    elif formNotes.errors:
        
        response.flash = str(formNotes.errors)
      
        i = 0
    
    
        

    #===== End Notes
    
    
    #===== Medical Test form and grid
    formMedtest = SQLFORM.factory(
             Field('testname', 'string',  label='Test', default = "Test ABC")
          )  
       
    medtestgrid = getmedtestgrid(patientid,providerid)

    if formMedtest.accepts(request,session=session,formname='formmedtest',keepvalues=True):
        i  = 0
    elif formMedtest.errors:
        response.flash = str(formMedtest.errors)  
    #====== End of Medical Test
    
    #====== Prescription Form and grid
    formPres = SQLFORM.factory(\
        Field('prescriptiondate', 'date', label='Date',  default=datetime.date.today(),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('doctor', 'integer', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),  label='Drug',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active == True)), 'doctor.id', '%(name)s')),
        Field('medicine', 'integer', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),  label='Drug',requires=IS_IN_DB(db((db.medicine.providerid==providerid)&(db.medicine.is_active == True)), 'medicine.id', '%(medicine)s:%(strength)s:%(strengthuom)s')),
        Field('strength', 'string',represent=lambda v, r: '' if v is None else v),
        Field('strengthuom', 'string',represent=lambda v, r: '' if v is None else v,default="",requires=IS_IN_SET(STRENGTHUOM)),
        Field('frequency', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('dosage', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('quantity', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('presremarks', 'text',represent=lambda v, r: '' if v is None else v,default=""),
        
    )
    
    xdate =  formPres.element('#no_table_prescriptiondate')
    xdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xdate['_data-date-format'] = 'dd/mm/yyyy'
    xdate['_autocomplete'] = 'off'  
    
    xdoctor = formPres.element('#no_table_doctor')
    xdoctor['_class'] = 'form-control'
    xdoctor['_autocomplete'] = 'off'    
    
    xmedicine = formPres.element('#no_table_medicine')
    xmedicine['_class'] = 'form-control'
    xmedicine['_autocomplete'] = 'off'    
    
    xstrength = formPres.element('#no_table_strength')
    xstrength['_class'] = 'form-control'
    xstrength['_autocomplete'] = 'off'    
    
    xstrengthuom = formPres.element('#no_table_strengthuom')
    xstrengthuom['_class'] = 'form-control'
    xstrengthuom['_autocomplete'] = 'off'    
    
    xfreq = formPres.element('#no_table_frequency')
    xfreq['_class'] = 'form-control'
    xfreq['_autocomplete'] = 'off'    
    
    xdosage = formPres.element('#no_table_dosage')
    xdosage['_class'] = 'form-control'
    xdosage['_autocomplete'] = 'off'   
    
    xqty = formPres.element('#no_table_quantity')
    xqty['_class'] = 'form-control'
    xqty['_autocomplete'] = 'off'   
    
    formPres.element('textarea[name=presremarks]')['_class'] = 'form-control'
    formPres.element('textarea[name=presremarks]')['_style'] = 'height:100px;line-height:1.0;'
    formPres.element('textarea[name=presremarks]')['_rows'] = 5
    
    
    #fromPres = SQLFORM.factory(
             #Field('medicinename', 'string',  label='', default = "")
          #)  
       
    prescriptions = getpresgrid(memberid, patientid, providerid)

    if formPres.accepts(request,session=session,formname='formpres',keepvalues=True):
        i  = 0
    elif formPres.errors:
        response.flash = "Errors: " + str(formPres.errors)
       
    #===== End of Prescription
    
    
    #==== Images
    
    
    items_per_page = 4
    limitby = ((imagepage)*items_per_page,(imagepage+1)*items_per_page)       
    
    images = None
    if(limitby > 0):
        images = db((db.dentalimage.patient == patientid) & (db.dentalimage.provider == providerid) & (db.dentalimage.image != "") & \
                      (db.dentalimage.image != None) & (db.dentalimage.is_active == True)).select(\
                        db.dentalimage.id,db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                        db.dentalimage.patienttype,db.dentalimage.patientname,db.dentalimage.description,db.dentalimage.is_active,db.vw_memberpatientlist.patientmember,\
                        left=[db.vw_memberpatientlist.on(db.dentalimage.patient == db.vw_memberpatientlist.patientid)],\
                              limitby=limitby, orderby = db.vw_memberpatientlist.patientmember | ~db.dentalimage.patienttype | ~db.dentalimage.id                      
                      )
    else:
        images = db((db.dentalimage.patient == patientid) & (db.dentalimage.provider == providerid) & (db.dentalimage.image != "") & \
                      (db.dentalimage.image != None) & (db.dentalimage.is_active == True)).select(
                        db.dentalimage.id,db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                        db.dentalimage.patienttype,db.dentalimage.patientname,db.dentalimage.description,db.dentalimage.is_active,db.vw_memberpatientlist.patientmember,\
                        left=[db.vw_memberpatientlist.on(db.dentalimage.patient == db.vw_memberpatientlist.patientid)],\
                              orderby = db.vw_memberpatientlist.patientmember | ~db.dentalimage.patienttype | ~db.dentalimage.id
                    )
                        
    formImage = SQLFORM.factory(
               Field('title', 'string',  label='Image Title', default = "Test ABC")
            )     
    #==== End of Images
          
       
    #==== Dental Chart
    #newchart = common.getboolean(request.vars.newchart)
    #appPath = request.folder    
    #srcchartfile = os.path.join(appPath, 'static/charts/default','dentalchart.jpg') 
    #destfilename  = str(tplanid) + str(treatmentid) + patientname.replace(" ","").lower() + ".jpg"
    #destchartfile = os.path.join(appPath, 'static/charts',destfilename)   
    #if((newchart == True) | (not os.path.isfile(destchartfile))):
        #copyfile(srcchartfile,destchartfile);
    #chartfile = "../static/charts/" + destfilename
    #charturl = URL('static', 'charts/' + destfilename)

    #chartnotes=""
    #chartdate= datetime.date.today()
    #charttitle=str(tplanid) + "_" + str(treatmentid) + "_" + patientname
    
    #charts = db((db.dentalchart.provider == providerid) & (db.dentalchart.treatmentplan == tplanid) & (db.dentalchart.treatment == treatmentid) & (db.dentalchart.is_active == True)).select()
    #if(len(charts) > 0):
        #chartnotes = common.getstring(charts[0].description)
        #chartdate = common.getdt(charts[0].chartdate)
        #charttitle = common.getstring(charts[0].title)
    
    #formDentalChart = SQLFORM.factory(
                   #Field('charttitle', 'string',  label='Title',default=chartnotes),
                   #Field('chartdate', 'date',  label='Date',default=chartdate, requires=IS_DATE(format=('%d/%m/%Y'))),
                   #Field('chartnotes','text', label='Description', default=chartnotes),
                   #)            
    #formDentalChart.element('textarea[name=chartnotes]')['_style'] = 'width:80%;line-height:1.0;'
          
    #xcharttitle = formDentalChart.element('input',_id='no_table_charttitle')
    #xcharttitle['_class'] =  'form-control'
    #xcharttitle['_type'] =  'text'
    #xcharttitle['_style'] ='width:80%'
    #xcharttitle['_autocomplete'] = 'off' 
    
    #xchartdate = formDentalChart.element('input',_id='no_table_chartdate')
    #xchartdate['_class'] =  'input-group form-control form-control-inline date-picker'
    #xchartdate['_style'] ='width:80%'
    #xchartdate['_autocomplete'] = 'off'                     
      
    #if formDentalChart.accepts(request,session=session,formname='formdentalchart',keepvalues=True):
        #i = 0
    #elif formDentalChart.errors:
        #j= 0
    #==== End Dental Chart
    
    #membername = <responsible party enrolled member's fname lname> patientname = <Patient's fname, lname> patientmember = <Member/Patient Code>

    return dict(formTreatment=formTreatment, formProcedure=formProcedure,formPres=formPres,formNotes=formNotes, formMedtest=formMedtest, medtestgrid=medtestgrid, prescriptions=prescriptions,\
                images = images,formImage=formImage,\
                page=page, memberpage=0, imagepage=imagepage,procedureid=procedureid,\
                providerid=providerid, providername=providername,doctorid=doctorid,doctorname=docs[0].name,\
                patientmember=patientmember, memberid=memberid,membername=membername, patientid=patientid,patientname=patientname,
                treatment=treatment,treatmentid=treatmentid,tplanid=tplanid,medicalalerts=medicalalerts,
                returnurl=returnurl
                )        


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def casereport():
    
    page = int(common.getpage(request.vars.page))
    providerid = int(common.getstring(request.vars.providerid))
    provdict = common.getproviderfromid(db, providerid)
    providername  = provdict["providername"]
 
    
    treatmentid = int(common.getid(request.vars.treatmentid))
    source = common.getstring(request.vars.source)    
    
    patientname = ""
    patientid = int(common.getid(request.vars.patientid))
    pats = db(db.vw_memberpatientlist.patientid == patientid).select()
    if(len(pats)>0):
        patientname = pats[0].patient
    
    #list of CSRS
    csrs = db((db.vw_casereport.patientid == patientid) & (db.vw_casereport.providerid == providerid)  & (db.vw_casereport.is_active == True)).select(db.vw_casereport.ALL, orderby=~db.vw_casereport.id)    
    
    formCSR= SQLFORM.factory(
        Field('patientmember', 'string', default=''),
        Field('fullname', 'string', default=patientname),
        Field('doctor', 'string', default=''),
        Field('csrs', 'text', default=''),
        Field('newcsr', 'text', default='')
    )
    
    formCSR.element('textarea[name=csrs]')['_class'] = 'form-control'
    formCSR.element('textarea[name=csrs]')['_style'] = 'height:500px;line-height:1.0;'
    formCSR.element('textarea[name=csrs]')['_rows'] = 1000
    
    formCSR.element('textarea[name=newcsr]')['_class'] = 'form-control'
    formCSR.element('textarea[name=newcsr]')['_style'] = 'height:100px;line-height:1.0;'
    formCSR.element('textarea[name=newcsr]')['_rows'] = 10
    
    xpm = formCSR.element('#no_table_patientmember')
    xpm['_class'] = 'form-control'
    xpm['_autocomplete'] = 'off'     

    xfnm = formCSR.element('#no_table_fullname')
    xfnm['_class'] = 'form-control'
    xfnm['_autocomplete'] = 'off'  
    
    xdoc = formCSR.element('#no_table_doctor')
    xdoc['_class'] = 'form-control'
    xdoc['_autocomplete'] = 'off'  
    
    if(source == 'members'):
        returnurl = URL('superadmin', 'list_patients', vars=dict(page=page, providerid=providerid))
    elif(source == 'walkin'):
        returnurl = URL('superadmin', 'list_nonmembers', vars=dict(page=page, providerid=providerid))
    else:
        returnurl = URL('superadmin', 'update_treatment', vars=dict(page=page, providerid=providerid,patientid=patientid,treatmentid=treatmentid))
        
    
    return dict(formCSR=formCSR,csrs=csrs,page=page,returnurl=returnurl,providerid=providerid,providername=providername,patientid=patientid,patientname=patientname,treatmentid=treatmentid,source=source)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def dentalchart():
    
    page = int(common.getid(request.vars.page))
    
    providerid = int(common.getid(request.vars.providerid))
    providerdict = common.getproviderfromid(db, providerid)
    providername = providerdict["providername"]

    patientid = int(common.getid(request.vars.patientid))
    memberid = int(common.getid(request.vars.memberid))

    doctorid = int(common.getid(request.vars.doctorid))
    treatmentid = int(common.getid(request.vars.treatmentid))   

    patientname = ""
    age = ""
    gender = ""
    
    r = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid == memberid)).select()
    if(len(r) > 0):
        patientname = r[0].patient
        gender = r[0].gender
        age = r[0].age
    


    chartid = int(common.getid(request.vars.chartid))
    
    if(chartid == 0):
        chartid = db.dentalchart.update_or_insert(((db.dentalchart.providerid == providerid)&(db.dentalchart.patientid==patientid)&(db.dentalchart.memberid==memberid)),\
                                                  providerid = providerid,\
                                                  patientid = patientid,\
                                                  memberid = memberid,\
                                                  is_active = True,\
                                                  created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid
                                                  
                                                  )
        if(chartid == None):
            rows = db(((db.dentalchart.providerid == providerid)&(db.dentalchart.patientid==patientid)&(db.dentalchart.memberid==memberid))).select(db.dentalchart.id)
            if(len(rows)>0):
                chartid = int(common.getid(rows[0].id))
            else:
                chartid = 0
                
    
    
    #Field('dentalprocedure', 'integer',  widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control'),  label='Doctor',requires=IS_IN_DB(db((db.vw_dentalprocedure_chart.is_active == True)), 'vw_dentalprocedure_chart.id', '%(altshortdescription)s')),
    
    formA = SQLFORM.factory(
        Field('chartdate', 'date', label='Date', default=datetime.date.today(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('toothid', 'string',label='Tooth ID',default=""),
        Field('toothnumber', 'integer', default=0),
        Field('doctor', 'integer', default=doctorid, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control'),  label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active == True)), 'doctor.id', '%(name)s')),
        Field('dentalprocedure', 'string',  widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control'),  label='Procedure',requires=IS_IN_DB(db((db.vw_dentalprocedure_chart.is_active == True)), 'vw_dentalprocedure_chart.proccode', '%(altshortdescription)s')),
        Field('chartid', 'integer',default=chartid ),
        Field('color', 'string',label='Color',default=""),
        Field('material', 'string',label='Material',default=""),
        Field('toothsection', 'string',label='Tooth Section',default=""),
        Field('p1', 'string',default=""),
        Field('p2', 'string',default=""),
        Field('p3', 'string',default=""),
        Field('p4', 'string',default=""),
        Field('p5', 'string',default=""),
        Field('p6', 'string',default=""),
        Field('p7', 'string',default=""),
        Field('p8', 'string',default=""),
        Field('p9', 'string',default=""),
        Field('l1', 'string',default=""),
        Field('l2', 'string',default=""),
        Field('l3', 'string',default=""),
        Field('l4', 'string',default=""),
        Field('e1', 'string',default=""),
        Field('notes', 'text',label='Notes',default="")
    )    
    
    formA.element('textarea[name=notes]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=notes]')['_rows'] = 5
    formA.element('textarea[name=notes]')['_class'] = 'form-control'

    xtoothid = formA.element('input',_id='no_table_toothid')
    xtoothid['_class'] =  'form-control '
    xtoothid['_placeholder'] = 'Enter tooth id' 
    xtoothid['_autocomplete'] = 'off'    


    xtoothnumber = formA.element('input',_id='no_table_toothnumber')
    xtoothnumber['_class'] =  'form-control '
    xtoothnumber['_placeholder'] = 'Enter tooth number' 
    xtoothnumber['_autocomplete'] = 'off'    

    xtoothsection = formA.element('input',_id='no_table_toothsection')
    xtoothsection['_class'] =  'form-control '
    xtoothsection['_placeholder'] = 'Enter tooth section' 
    xtoothsection['_autocomplete'] = 'off'    

    xcolor = formA.element('input',_id='no_table_color')
    xcolor['_class'] =  'form-control '
    xcolor['_placeholder'] = 'Enter tooth section' 
    xcolor['_autocomplete'] = 'off'    

    xmat = formA.element('input',_id='no_table_material')
    xmat['_class'] =  'form-control '
    xmat['_placeholder'] = 'Enter tooth section' 
    xmat['_autocomplete'] = 'off'    

    xchartdate = formA.element('input',_id='no_table_chartdate')
    xchartdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xchartdate['_data-date-format'] = 'dd/mm/yyyy'
    xchartdate['_autocomplete'] = 'off' 

    doc = formA.element('#no_table_doctor')
    doc['_class'] = 'form-control'
    doc['_style'] = 'width:100%'

    proc= formA.element('#no_table_dentalprocedure')
    proc['_class'] = 'form-control'
    proc['_style'] = 'width:100%'

    toothcolors = None
    
    if formA.accepts(request,session,keepvalues=True):
        chartid = int(common.getid(request.vars.chartid))
        treatmentid = int(common.getid(request.vars.treatmentid))
        doctorid = int(common.getid(request.vars.doctor))
        procedureid = 0
        proccode = common.getstring(request.vars.dentalprocedure)
        r = db(db.vw_dentalprocedure_chart.proccode == proccode).select()
        if(len(r)>0):
            procedureid = int(common.getid(r[0].id))
        
        
        dt = datetime.datetime.strptime(request.vars.chartdate, "%d/%m/%Y")
        chartdate = common.getdt(dt)
        toothid = common.getstring(request.vars.toothid)
        toothnumber = common.getstring(request.vars.toothnumber)
        toothsection = common.getstring(request.vars.toothsection)
        notes = common.getstring(request.vars.notes)
        color = common.getstring(request.vars.color)
        material = common.getstring(request.vars.material)
        
        #color = <pcolor1>;<pcolor2> | <lcolor1>;<lcolor2> | <ecolor1>;<ecolor2>
        colorarr = color.split("|")
        p1=""
        p2=""
        p3=""
        p4=""
        p5=""
        p6=""
        p7=""
        p8=""
        p9=""
        l1=""
        l2=""
        l3=""
        l4=""
        e1=""
         
        if(len(colorarr)>=1):
            parr = colorarr[0].split(";")
            if(len(parr)>=1):
                p1 = parr[0]

            if(len(parr)>=2):
                p2 = parr[1]

            if(len(parr)>=3):
                p3 = parr[2]
        
            if(len(parr)>=4):
                p4 = parr[3]
            
            if(len(parr)>=5):
                p5 = parr[4]

            if(len(parr)>=6):
                p6 = parr[5]

            if(len(parr)>=7):
                p7 = parr[6]

            if(len(parr)>=8):
                p8 = parr[7]
                
            if(len(parr)>=9):
                p9 = parr[8]
                
        if(procedureid >0):
        
            xid = db.tooth.update_or_insert(((db.tooth.toothid == toothid)&(db.tooth.chartid == chartid)&(db.tooth.procedureid == procedureid)),\
                                            toothid = toothid, toothnumber = toothnumber, chartid = chartid, doctorid = doctorid, procedureid=procedureid, treatmentid=treatmentid,\
                                            toothsection = toothsection, chartdate = chartdate, notes=notes, \
                                            p1=p1,p2=p2,p3=p3,p4=p4,p5=p5,p6=p6,p7=p7,p8=p8,p9=p9,l1=l1,l2=l2,l3=l3,l4=l4,e1=e1,\
                                            is_active = True,\
                                            created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid
                                            )
        else:
            session.flash = "Dental Procedure Error in saving Dental Chart!"
        

    elif formA.errors:
        response.flash = "Errors " + str(formA.errors)
    else:
        k = 0
        
    chartds=db((db.tooth.chartid == chartid) & (db.tooth.is_active == True)).select()
    
    #toothcolors = db((db.toothcolor.providerid == providerid) & (db.toothcolor.is_active == True)).select()
    #toothcolors = db((db.toothcolor.is_active == True)).select()
    source = common.getstring(request.vars.source)
    if(source == 'treatment'):
        returnurl = URL('superadmin', 'update_treatment', vars=dict(page=page,imagepage=0,providerid=providerid,treatmentid=treatmentid))
    else:
        returnurl = URL('superadmin', 'update_treatment', vars=dict(page=page,imagepage=0,providerid=providerid,treatmentid=treatmentid))
        
    return dict(formA=formA, page=page,returnurl=returnurl,providerid = providerid, providername = providername,chartid=chartid, chartds=chartds, patientname = patientname, gender=gender, age=age)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def update_payment():
    tplanid = 0
    
    paymentid    = int(common.getid(request.vars.paymentid))
    payment = db(db.payment.id == paymentid).select()
    paymentcommit = common.getboolean(payment[0].paymentcommit)
    
    if(len(payment)>0):
        tplanid = payment[0].treatmentplan
      
    page         = int(common.getpage(request.vars.page))
    memberid     = int(common.getid(request.vars.memberid))    
    patientid     = int(common.getid(request.vars.patientid))
    patient     = common.getstring(request.vars.patient) 
    fullname    = common.getstring(request.vars.fullname)

    providerid = int(common.getstring(request.vars.providerid))
    provdict = common.getproviderfromid(db, providerid)
    providername = common.getstring(provdict["providername"])

    
        
    
    tps = db((db.vw_payment_treatmentplan_treatment.providerid == providerid)& (db.vw_payment_treatmentplan_treatment.primarypatient == memberid) & \
                         (db.vw_payment_treatmentplan_treatment.tplanactive == True)).select()  
    
    members = db((db.vw_memberpatientlist.is_active == True) & (db.vw_memberpatientlist.providerid == providerid) & \
                (db.vw_memberpatientlist.primarypatientid == db.vw_memberpatientlist.patientid)).select(db.vw_memberpatientlist.ALL, orderby=db.vw_memberpatientlist.fullname)

    
        
            
    crud.settings.keepvalues = True
    crud.settings.showid = True
    #crud.settings.update_onaccept = acceptupdatepayment
    crud.settings.update_next = URL('superadmin','list_payment',vars=dict(page=page,tplanid=tplanid,patient=patient,fullname=fullname,patientid=patientid, memberid=memberid,providerid=providerid,providername=providername))
    db.payment.amount.writable = not paymentcommit
    db.payment.paymenttype.writable = not paymentcommit
    db.payment.paymentmode.writable = not paymentcommit
    db.payment.payor.writable = not paymentcommit
    db.payment.patientmember.writable = not paymentcommit
    db.payment.treatmentplan.writable = not paymentcommit
    db.payment.paymentdate.writable = not paymentcommit
    db.payment.is_active.writable = not paymentcommit
    db.payment.paymentcommit.writable = not paymentcommit
    
    formA = crud.update(db.payment, paymentid,cast=int, message="Thankyou for your Payment!")  ## company Details entry form
    
    xnotes = formA.element('textarea',_id='payment_notes')
    xnotes['_class'] = 'form-control'    
    xnotes['_style'] = 'height:50px;line-height:1.0;'
    xnotes['_rows'] = 5   
    xnotes['_readonly'] = paymentcommit

    
    
    
    totaltreatmentcost = 0
    totaldue = 0
    totalcost = 0
    totalpaid = 0
    
    tplan = db(db.treatmentplan.id == tplanid).select()
    totaltreatmentcost = float(common.getvalue(tplan[0].totaltreatmentcost))
    
    r = db((db.vw_paymentsummary1.provider==providerid) & (db.vw_paymentsummary1.patientmember == memberid)).select()
    if(len(r)>0):
        totalcost = float(common.getvalue(r[0].totalcost))
        totalpaid = float(common.getvalue(r[0].totalpaid))
        totaldue = totalcost-totalpaid
      

    returnurl = URL('superadmin','list_payment',vars=dict(page=page,tplanid=tplanid,patient=patient,fullname=fullname,patientid=patientid, memberid=memberid,providerid=providerid,providername=providername))
    
    return dict(formA=formA, returnurl=returnurl, page=page, paymentid=paymentid,providerid=providerid, providername=providername, tplanid=tplanid, memberid=memberid, \
                tps=tps,paymentcommit=paymentcommit,members=members,\
                totalcost=totalcost,totalpaid=totalpaid,totaldue=totaldue,totaltreatmentcost=totaltreatmentcost)

def update_nonmember():
    
    #get provider information
    provdict = common.getproviderfromid(db, request.vars.providerid)
    providerid = int(common.getid(request.vars.providerid))
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    member   = common.getstring(request.vars.member)
    
    #filtering fields    
    
    #fname    = common.getstring(request.vars.fname)
    #lname    = common.getstring(request.vars.lname)
    #cell     = common.getstring(request.vars.cell)
    #email    = common.getstring(request.vars.email)
    
    #these are the list members filter parameters
    page     = int(common.getpage(request.vars.page))
 
    returnurl = URL('superadmin','list_nonmembers', vars=dict(providerid=providerid,page=page))    

    rows = db(db.patientmember.id == memberid).select()
    
   
    
    db.patientmember.patientmember.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.dob.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='input-group form-control form-control-inline date-picker')
    db.patientmember.fname.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.mname.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.lname.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.address1.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.address2.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.address3.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.city.widget = widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.gender.widget = widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.title.widget = widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.st.widget = widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.pin.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.telephone.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.cell.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.email.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.startdate.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border  date')
    db.patientmember.status.widget = widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='w3-input w3-border ')

    db.patientmember.patientmember.default=rows[0].patientmember
    db.patientmember.dob.default=rows[0].dob
    db.patientmember.fname.default=rows[0].fname
    db.patientmember.mname.default=rows[0].mname
    db.patientmember.lname.default=rows[0].lname
    db.patientmember.address1.default=rows[0].address1
    db.patientmember.address2.default=rows[0].address2
    db.patientmember.address3.default=rows[0].address3
    db.patientmember.city.default=rows[0].city
    db.patientmember.gender.default=rows[0].gender
    db.patientmember.title.default=rows[0].title
    db.patientmember.st.default=rows[0].st
    db.patientmember.pin.default=rows[0].pin
    db.patientmember.telephone.default=rows[0].telephone
    db.patientmember.cell.default=rows[0].cell
    db.patientmember.email.default=rows[0].email
    db.patientmember.startdate.default=rows[0].startdate
    db.patientmember.status.default=rows[0].status
    db.patientmember.image.default=rows[0].image
    db.patientmember.newmember.default = rows[0].newmember
    db.patientmember.freetreatment.default = rows[0].freetreatment

    db.patientmember.groupref.default = ''
    db.patientmember.pan.default = ''
    db.patientmember.webkey.default = ''
    db.patientmember.groupregion.default = 1
    
    db.patientmember.enrollmentdate.default = request.now
    db.patientmember.terminationdate.default = request.now
    db.patientmember.premstartdt.default = request.now
    db.patientmember.premenddt.default = request.now
    db.patientmember.duedate.default = request.now
    
    db.patientmember.paid.default = False
    db.patientmember.upgraded.default = False
    db.patientmember.renewed.default = False
    db.patientmember.hmopatientmember.default = False
    
    db.patientmember.provider.default = providerid
    db.patientmember.company.default = 1
    db.patientmember.hmoplan.default = 1
    
    
    db.patientmember.groupref.readable = True
    db.patientmember.groupref.writable = True
    db.patientmember.enrollmentdate.readable = False
    db.patientmember.enrollmentdate.writable = True
    db.patientmember.terminationdate.readable = False
    db.patientmember.terminationdate.writable = True
    db.patientmember.premstartdt.readable = False
    db.patientmember.premstartdt.writable = True
    db.patientmember.premenddt.readable = False
    db.patientmember.premenddt.writable = True
    db.patientmember.groupregion.readable = False
    db.patientmember.groupregion.writable = True
    db.patientmember.pan.readable = False
    db.patientmember.pan.writable = True
    db.patientmember.webkey.readable = False
    db.patientmember.webkey.writable = True
    db.patientmember.upgraded.readable = False
    db.patientmember.upgraded.writable = True
    db.patientmember.renewed.readable = False
    db.patientmember.renewed.writable = True
    db.patientmember.webmember.readable = False
    db.patientmember.webmember.writable = True
    

                
    db.patientmember.hmopatientmember.readable = False
    db.patientmember.hmopatientmember.writable = True
                        
    db.patientmember.gender.requires=IS_EMPTY_OR(IS_IN_SET(gender.GENDER))
    db.patientmember.title.requires=IS_EMPTY_OR(IS_IN_SET(gender.PATTITLE))
    db.patientmember.st.requires = IS_EMPTY_OR(IS_IN_SET(states.STATES))
    db.patientmember.city.requires = IS_EMPTY_OR(IS_IN_SET(states.CITIES))
    db.patientmember.startdate.requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))
    db.patientmember.dob.requires = IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))
    db.patientmember.address1.requires = ""
    db.patientmember.address2.requires = ""
    db.patientmember.pin.requires = ""
    db.patientmember.email.requires  = ""
    db.patientmember.groupregion.requires = ""
    db.patientmember.company.requires = ""
    db.patientmember.hmoplan.requires = ""
    
    crud.settings.update_next = URL('member','list_nonmembers', vars=dict(providerid=providerid,page=page)) 
    
    formA = crud.update(db.patientmember, memberid,cast=int, message='Member Information Updated!')
    
    xdob = formA.element('input',_id='patientmember_dob')
    xdob['_class'] =  'input-group form-control form-control-inline date-picker'
    xdob['_data-date-format'] = 'dd/mm/yyyy'
    xdob['_autocomplete'] = 'off'                     
    
    
         
    return dict(providername=provdict["providername"],formA=formA,providerid=providerid,memberid=memberid,\
                member=member,page=page,image=rows[0].image,\
                returnurl=returnurl)    
    
