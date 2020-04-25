from gluon import current
import os
import base64
import json
import tempfile
import uuid

import datetime
import time

from applications.my_pms2.modules import common
from applications.my_pms2.modules import mail

from applications.my_pms2.modules import mdpuser
from applications.my_pms2.modules import mdpdoctor
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import mdpappointment
from applications.my_pms2.modules import mdppayment
from applications.my_pms2.modules import mdptreatment
from applications.my_pms2.modules import mdpprocedure
from applications.my_pms2.modules import mdpimage
from applications.my_pms2.modules import tasks
from applications.my_pms2.modules import mdpreligare

from applications.my_pms2.modules import logger

######################################################## Religare  APIS  ##################################
def encrypt(avars):
    orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = orlgr.encrypt(avars["raw"])
    return rsp    
    
def decrypt(avars):
    orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
    #x = base64.encodestring(avars["encrypt"]) 
    rsp = orlgr.decrypts(avars["encrypt"])
    return rsp 

def decrypts128(avars):
    orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = orlgr.decrypts128(avars["encrypt"])
    return rsp 

def encrypts128(avars):
    orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = orlgr.encrypts128(avars["raw"])
    return rsp 

#API-1
def sendOTP(avars):
    rsp = {}
    orlgr = None
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
	rsp = orlgr.sendOTP(avars["policy_number"], avars["customer_id"], avars["mobile_number"])
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
    #rspencrypted = orlgr.encoderequestdata(rsp)
    #j = {"encrypt":rspencrypted}
    #jstr = json.dumps(j)
    return rsp

#API-2
def validateOTP(avars):
    rsp={}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
	rsp = orlgr.validateOTP(avars["ackid"], avars["otp"], avars["policy_number"], avars["customer_id"], avars["mobile_number"])
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + e.message})
    return rsp


def getReligarePatient(avars):
    
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
	rsp = orlgr.getreligarepatient(avars["customer_id"], avars["membername"], avars["mobile_number"], avars["dob"], avars["gender"])
	
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + e.message})
	
    
    return rsp

def updateReligarePatient(avars):
    
    
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
	rsp = orlgr.updatereligarepatient(avars["memberid"],avars["email"], avars["address1"], avars["address2"], avars["address3"], avars["city"],avars["st"],avars["pin"])
	
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + e.message})
	
    
    return rsp

#API-3
def uploadDocument(avars):
    rsp = {}
    try:
	
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
	#filename = "C:\\ib\\xray1.jpg"
	file_data = avars['document']
	#with open(filename, "rb") as imageFile:
	    #file_data = base64.b64encode(imageFile.read())	
	
	#appath = current.globalenv["request"].folder
	#dirpath = os.path.join(appath, 'temp')
	    
	#if(not os.path.exists(dirpath)):
	    #os.makedirs(dirpath,0777)
	
	#tempfile.tempdir = dirpath
	#tempimgfile = tempfile.NamedTemporaryFile(delete=False)
	#tempimgfile.name = tempimgfile.name + ".jpg"
	x = uuid.uuid1()
	filename = x.hex + ".jpg"
	
	rsp = orlgr.uploadDocument(avars["ackid"], file_data,filename,avars["policy_number"], avars["customer_id"], avars["mobile_number"])
    
	#rsp = orlgr.uploadDocument(avars["ackid"], avars["file_data"],avars["file_name"],avars["policy_number"], avars["customer_id"], avars["mobile_number"])
	#rsp = orlgr.uploadDocument(avars["ackid"], avars["document"],"",avars["policy_number"], avars["customer_id"], avars["mobile_number"])
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
    
    return rsp

def addProcedure(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
	rsp = orlgr.addProcedure(avars["ackid"], avars["sub_service_id"],avars["treatment_code"],avars["treatment_name"],avars["swipe_value"])
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + e.message})
    
    
    return rsp
#API-4
def getTransactionID(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
	rsp = orlgr.geTransactionID(avars["ackid"], avars["service_id"],\
	                            avars["procedurecode"],avars["procedurename"],\
	                            avars["procedurefee"],
	                            avars["plancode"],
	                            avars["policy_number"], avars["customer_id"], avars["mobile_number"]
	                            )
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + e.message})
    
    return rsp

#API-5
def addRlgProcedureToTreatment(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
	rsp = orlgr.addRlgProcedureToTreatment(avars["ackid"], \
	                                    avars["otp"],\
	                                    avars["treatmentid"],\
	                                    avars["plancode"],\
	                                    avars["procedurecode"],\
	                                    avars["procedurename"],\
	                                    avars["procedurefee"],\
	                                    avars["tooth"],\
	                                    avars["quadrant"],\
	                                    avars["remarks"],\
	                                    avars["policy_number"], avars["customer_id"], avars["mobile_number"]
	                            )
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + e.message})
    

    return rsp



#API-7
def voidTransaction(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
	rsp = orlgr.voidTransaction(int(common.getid(avars["treatmentid"])),int(common.getid(avars["treatmentprocedureid"])))
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + e.message})
    
    return rsp

def getreligareprocedures(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
	rsp = orlgr.getreligareprocedures(avars["ackid"], avars["procedurepriceplancode"],\
	                                  avars["phrase"] if "phrase" in avars else "",\
	                                  avars["page"] if "page" in avars else 0,\
	                                  avars["maxcount"] if "maxcount" in avars else 0)
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + e.message})
	
    return rsp

#API-6
def settleTransaction(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
	rsp = orlgr.settleTransaction(int(common.getid(avars["treatmentid"])),int(common.getid(avars["treatmentprocedureid"])))
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + e.message})
    
    
    
    return rsp

######################################################## USER  APIS  ##################################
#POST method
#Input: {"email"":<emailid>}
#error return - {"result":False,"Message":<mssg>}
#success return - {"result":True,"username":<usernam>}
def forgotusername(avars):
    ouser = mdpuser.User(current.globalenv['db'],current.auth,"","")
    mdp_user = ouser.request_username(avars["email"])
    return mdp_user

#POST method
#Input: {"email":<email>, "username":<username}
#Return:{"result":True,"resetpasswordkey":<passwordkey>}
#{"result":False, "message":<error message>}
def forgotpassword(avars):
    ouser = mdpuser.User(current.globalenv['db'],current.auth,avars["username"],"")
    mdp_user = ouser.request_resetpassword(avars["email"])
    return mdp_user

#POST method
#Input: {"username":<username>,"email":<email>,"resetpasswordkey":<resetpasswordkey,"newpassword":<newpassword>}
#error return - {"result":False,"Message":<mssg>}
#success return - {"result":True}
def resetpassword(avars):
    ouser = mdpuser.User(current.globalenv['db'],current.auth,avars["username"],"")
    mdp_user = ouser.reset_password(avars["email"],avars["resetpasswordkey"], avars["newpassword"])
    
    return mdp_user
    
#POST method
#input:{"username":<username>,"password":<password>}
#return:user_data ={"result" : False,"message":"Authentication Error"}
#user_data ={"result" : True,"usertype":"webadmin","providerid":int(provdict["providerid"]),"providername":provdict["providername"]}
#user_data ={"result" : True,"usertype":"provider","providerid":int(provdict["providerid"]),"provider":provdict["provider"],
#"providername":provdict["providername"],"registration":provdict["registration"]}
def mdplogin(avars):
    ouser = mdpuser.User(current.globalenv['db'],current.auth,avars["username"],avars["password"])
    mdp_user = ouser.login()
    
    #orlgr = mdpreligare.Religare(current.globalenv['db'],1011)
    #encmdp_user = orlgr.encoderequestdata(mdp_user)
    return mdp_user

def mdplogout(avars):
    ouser = mdpuser.User(current.globalenv['db'],current.auth,avars["username"],avars["password"])
    rsp = ouser.logout()
    return rsp

def otpvalidation(avars):
    ouser = mdpuser.User(current.globalenv['db'],None,"","")
    rsp = ouser.otpvalidation(avars["cell"], avars["email"], avars["otp"], datetime.datetime.strptime(avars["otpdatetime"],"%d/%m/%Y %H:%M:%S"))
    
    return rsp
    
def getallconstants(avars):
    ouser = mdpuser.User(current.globalenv['db'],None,"","")
    rsp = ouser.getallconstants()
    
    return rsp

######################################################## PATIENT APIS  ##################################    



#this method creates a new walk-in patient
#input:{providerid, fname,mname,lname,cell,email}
#output:{}
#"regionid ": 1,
#"groupref ": "walkin",
#"freetreatment ": true,
#"email ": "zyyyy@gmail.com",
#"company ": 104,
#"patient ": "WLK102_FN WLK102_LN :P00140288",
#"dob ": "16/11/2018 00:00",
#"gender ": "Male",
#"hmoplan ": 1,
#"primarypatientid ": 8867,
#"cell ": "102102102",
#"title ": " ",
#"newmember ": false,
#"premenddt ": "16/11/2018 00:00",
#"patientid": 8867,
#"providerid": 108,
#"hmopatientmember ": false,
#"patientmember ": "P00140288",
#"hmoplanname": "Premium Walk In",
#"premstartdt ": "16/11/2018 00:00",
#"age": 0,
#"hmoplancode ": "PREMWALKIN",
#"patienttype ": "P",
#"lname ": "WLK102_LN",
#"fname ": "WLK102_FN",
#"relation ": "Self",
#"fullname ": "WLK102_FN WLK102_LN"
def newpatient(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(avars["providerid"])))
    pat = opat.newpatient(avars['fname'],avars['mname'],avars['lname'],avars['cell'],avars['email'])
    #pat = opat.getpatient(pat[0],pat[1])
    return pat


#input - groupref,title,fname,mname,lname,cell,emailid,dob,gender,address1,address2,address3,city,st,pin,
#output - memberid,patientid 
def updatewalkinpatient(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(avars["providerid"])))
    pat = opat.updatewalkinpatient(avars)
    return pat


#input - groupref,title,fname,mname,lname,cell,emailid,dob,gender,address1,address2,address3,city,st,pin,
#output - memberid,patientid 
def newalkinpatient(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(avars["providerid"])))
    pat = opat.newalkinpatient(avars)
    return pat

#This method gets patient information
#Input Data
#{
	#"action":"getpatient",
	#"providerid":108,
	#"memberid":7942,
	#"patientid":1404

#}
#Output Data
#{
    #"regionid ": 1,
    #"groupref ": "MEDI6699",
    #"freetreatment ": true,
    #"email ": "imtiazbengali@gmail.com",
    #"company ": 4,
    #"patient ": "FN2_DEP1 LN2_DEP1 :ALLMED00410017",
    #"dob ": "03/06/2018 00:00",
    #"gender ": "Male",
    #"hmoplan ": 3,
    #"primarypatientid ": 7942,
    #"cell ": "9916314080",
    #"title ": " ",
    #"newmember ": false,
    #"premenddt ": "02/06/2019 00:00",
    #"patientid": 1404,
    #"providerid": 108,
    #"hmopatientmember ": true,
    #"patientmember ": "ALLMED00410017",
    #"hmoplanname": "Premium Plan",
    #"premstartdt ": "03/06/2018 00:00",
    #"age": 0,
    #"hmoplancode ": "BLRPRE101",
    #"patienttype ": "D",
    #"lname ": "LN2_DEP1",
    #"fname ": "FN2_DEP1",
    #"relation ": "Spouse",
    #"fullname ": "FN2_DEP1 LN2_DEP1"
#}
def getpatient(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(avars["providerid"])))
    urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.mydp_ipaddress)
    imageurl =urlprops[0].mydp_ipaddress + URL('dentalimage',"download")    
    pat = opat.getpatient(avars['memberid'],avars['patientid'],imageurl)
    
    
    return pat 

#This method returns a list of patients matching 'searchphrase' - cell or email or fname, or lname or patientmember
#input Data;
#{
   #"action":"searchpatient",
   #"providerid":108,
    #"searchphrase":"ALLMED00410017"
#}
#Output Data
#{
    #"patientlist": [
        #{
            #"member": true,
            #"patientmember": "ALLMED00410017",
            #"lname": "LN2",
            #"primary": true,
            #"fname": "FN2",
            #"relation": "Self",
            #"email": "imtiazbengali@gmail.com",
            #"cell": "9916314080",
            #"memberid": 7942,
            #"patientid": 7942
        #},
        #{
            #"member": true,
            #"patientmember": "ALLMED00410017",
            #"lname": "FN2_DEP2",
            #"primary": false,
            #"fname": "FN2_DEP2",
            #"relation": "Son",
            #"email": "imtiazbengali@gmail.com",
            #"cell": "9916314080",
            #"memberid": 7942,
            #"patientid": 1405
        #},
        #{
            #"member": true,
            #"patientmember": "ALLMED00410017",
            #"lname": "LN2_DEP1",
            #"primary": false,
            #"fname": "FN2_DEP1",
            #"relation": "Spouse",
            #"email": "imtiazbengali@gmail.com",
            #"cell": "9916314080",
            #"memberid": 7942,
            #"patientid": 1404
        #}
    #],
    #"patientcount": 3
#}

def searchpatient(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = opat.searchpatient(avars["page"] if "page" in avars else 1,avars["searchphrase"],
                            avars["maxcount"] if "maxcount" in avars else 0
                             )
    return rsp

#This returns a list of patient notes entered by a doctor(s)
def getpatientnotes(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = opat.getpatientnotes(avars['page']  if 'page' in avars else 0,avars['memberid'],avars['patientid'])
    return rsp

#this saves new note added to the patient notes log
def addpatientnotes(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = opat.addpatientnotes(avars['memberid'],avars['patientid'],avars['notes'])
    return rsp
    
def genders(avars):
    opat = mdppatient.Patient(current.globalenv['db'],0)
    rsp = opat.genders()
    
    return rsp
    
def cities(avars):
    opat = mdppatient.Patient(current.globalenv['db'],0)
    rsp = opat.cities()
    
    return rsp

def states(avars):
    opat = mdppatient.Patient(current.globalenv['db'],0)
    rsp = opat.states()
    
    return rsp

def regions(avars):
    opat = mdppatient.Patient(current.globalenv['db'],0)
    rsp = opat.regions()
    
    return rsp

def status(avars):
    opat = mdppatient.Patient(current.globalenv['db'],0)
    rsp = opat.status()
    
    return rsp

def pattitles(avars):
    opat = mdppatient.Patient(current.globalenv['db'],0)
    rsp = opat.pattitles()
    return rsp

def doctitles(avars):
    opat = mdppatient.Patient(current.globalenv['db'],0)
    rsp = opat.doctitles()
    return rsp

def getMedicalHistory(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = opat.getpatientnotes(avars['memberid'],avars['patientid'])    
    return rsp

def updateMedicalHistory(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = opat.getpatientnotes(avars['memberid'],avars['patientid'],avars["medhiststr"])    
    return rsp

############################## DOCTOR API #####################################################

def specialitylist(avars):
    odr = mdpdoctor.Doctor(current.globalenv['db'],int(common.getid(avars["providerid"])))
    splist = odr.specialitylist()
    return splist

def rolelist(avars):
    odr = mdpdoctor.Doctor(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rllist = odr.rolelist()
    return rllist

def doctorlist(avars):
    odr = mdpdoctor.Doctor(current.globalenv['db'],int(common.getid(avars["providerid"])))
    drlist = odr.doctorlist()
    return drlist
    
def getdoctor(avars):
    odr = mdpdoctor.Doctor(current.globalenv['db'],int(common.getid(avars["providerid"])))
    doctor = odr.doctor(int(common.getid(avars["doctorid"])))
    return doctor
############################ APPOINTMENT API ##################################################

#getappointments 
#providerid, month, year
#returns list of appointments : apptid, doctorid, patientname, apptdatetime, color
def getappointments(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oappts.appointments(int(common.getid(avars["month"])),int(common.getid(avars["year"])))
    return rsp


def getpatappointmentcountbymonth(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oappts.getpatappointmentcountbymonth(int(common.getid(avars["month"])),int(common.getid(avars["year"])),\
                                          int(common.getid(avars["memberid"])),int(common.getid(avars["patientid"])))
    return rsp


def getappointmentsbypatient(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oappts.getappointmentsbypatient(int(common.getid(avars["month"])),int(common.getid(avars["year"])),\
                                          int(common.getid(avars["memberid"])),int(common.getid(avars["patientid"])))
    return rsp


def getappointmentsbymonth(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oappts.getappointmentsbymonth(int(common.getid(avars["month"])),int(common.getid(avars["year"])))
    return rsp

#this method returns all appointments for a specific day (dd/mm/yyyy) for a provider/patient
def getpatappointmentsbyday(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oappts.getpatappointmentsbyday(int(common.getid(avars["day"])),int(common.getid(avars["month"])),int(common.getid(avars["year"])),\
                                         int(common.getid(avars["memberid"])),int(common.getid(avars["patientid"]))\
                                         )
    
    return rsp

    

#this method returns all appointments for a specific day (dd/mm/yyyy)
def getappointmentsbyday(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oappts.getappointmentsbyday(int(common.getid(avars["day"])),int(common.getid(avars["month"])),int(common.getid(avars["year"])))
    return rsp

#this method returns all number of appointments for each day of a month
def getappointmentcountbymonth(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oappts.getappointmentcountbymonth(int(common.getid(avars["month"])),int(common.getid(avars["year"])))
    return rsp

def getdocappointmentcountbymonth(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oappts.getdocappointmentcountbymonth(int(common.getid(avars["month"])),int(common.getid(avars["year"])))
    return rsp


#getappointment 
#providerid, apptid
#returns appointment details
def getappointment(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oappts.appointment(int(common.getid(avars["appointmentid"])))
    return rsp

def checkinappointment(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oappts.checkinappointment(int(common.getid(avars["appointmentid"])))
    return rsp

def newappointment(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oappts.newappointment(int(common.getid(avars["memberid"])),int(common.getid(avars["patientid"])),\
                                int(common.getid(avars["doctorid"])),\
                                avars["complaint"],avars["startdt"],int(common.getid(avars["duration"])),avars["providernotes"],avars["cell"],\
                                current.globalenv["request"].folder)
    return rsp

def updateappointment(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    
   # (self,appointmentid,doctorid,complaint,startdt,duration,providernotes,cell,status,treatmentid,appPath):
    rsp = oappts.updateappointment(\
        
        int(common.getid(avars["appointmentid"])) if("appointmentid" in avars) else 0,
        int(common.getid(avars["doctorid"])) if("doctorid" in avars) else 0,
        common.getstring(avars["complaint"])  if("complaint" in avars) else "",
        common.getstring(avars["startdt"])  if("startdt" in avars) else "",
        int(common.getid(avars["duration"])) if("duration" in avars) else 0,
        common.getstring(avars["providernotes"])  if("providernotes"in avars) else "",
        common.getstring(avars["cell"])  if("cell" in avars) else "",
        common.getstring(avars["status"])  if("status" in avars) else "",
        int(common.getid(avars["treatmentid"])) if("treatmentid" in avars) else 0,
        current.globalenv["request"].folder)    


    return rsp

def cancelappointment(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    
   # (self,appointmentid,doctorid,complaint,startdt,duration,providernotes,cell,status,treatmentid,appPath):
    rsp = oappts.cancelappointment(\
        
        int(common.getid(avars["appointmentid"])) if("appointmentid" in avars) else 0,
       
        common.getstring(avars["providernotes"])  if("providernotes"in avars) else "",
       
        current.globalenv["request"].folder)    


    return rsp

def appointmentstatus(avars):
    #logger.loggerpms2.info("Enter New Treatment")    
    oappts = mdpappointment.Appointment(current.globalenv['db'],0)
    rsp = oappts.appointmentstatus()
    
    return rsp

def appointmentduration(avars):
    #logger.loggerpms2.info("Enter New Treatment")    
    oappts = mdpappointment.Appointment(current.globalenv['db'],0)
    rsp = oappts.appointmentduration()
    
    return rsp


############################ Payment API ##################################################
#Input: db, providerid, memberid, patientid
#Ouput: paymentcount, {memberid,patientid,patientname,paymentdate,treatmentid,treatmentdate,treatment,procedures,
#totaltreatmentcost,totalinspays,totalcopay,totalpaid,totaldue}
def listpayments(avars):
    
    opaymnt = mdppayment.Payment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = opaymnt.listpayments(int(common.getid(avars["memberid"])),int(common.getid(avars["patientid"])))
    return rsp

#Input: db, providerid, paymentid
#Ouput: paymentcount, paymentsummary:{treatmentcost,copay,inspays,totaltreatmentcost,totalinspays,totalcopay,totaldue}, {memberid,patientid,patientname,paymentdate,treatmentid,treatmentdate,treatment,procedures,
#totaltreatmentcost,totalinspays,totalcopay,totalpaid,totaldue}
def getpayment(avars):
    
    opaymnt = mdppayment.Payment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = opaymnt.getpayment(int(common.getid(avars["paymentid"])))
    return rsp

def paymentcallback(avars):
    opaymnt = mdppayment.Payment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = opaymnt.paymentcallback(avars)
    return rsp
    
def newpayment(avars):
    opaymnt = mdppayment.Payment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = opaymnt.newpayment(int(common.getid(avars["memberid"])),int(common.getid(avars["patientid"])),int(common.getid(avars["treatmentid"])))
    return rsp

def getpaymentlist(avars):
    opaymnt = mdppayment.Payment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = opaymnt.getpaymentlist(int(common.getid(avars["memberid"])),int(common.getid(avars["patientid"])),int(common.getid(avars["treatmentid"])))
    return rsp

def paymentreceipt(avars):
    opaymnt = mdppayment.Payment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = opaymnt.paymentreceipt(int(common.getid(avars["paymentid"])))
    return rsp


def getsignedkey(avars):
    opaymnt = mdppayment.Payment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = opaymnt.getsignedkey(avars["signedip"],current.globalenv["request"].folder)
    return rsp

############################ Treatments API #######################################################
def gettreatments(avars):
    #logger.loggerpms2.info("Enter Get Treatments")
    
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = otrtmnt.gettreatments(avars["page"] if "page" in avars else 1, 
                                int(common.getid(avars["memberid"])),int(common.getid(avars["patientid"])),
                                common.getstring(avars["searchphrase"]),
                                avars["maxcount"] if "maxcount" in avars else 0
                                                                                           
                                )
    return rsp

def gettreatment(avars):
    #logger.loggerpms2.info("Enter Get Treatment")
    
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = otrtmnt.gettreatment(int(common.getid(avars["treatmentid"])))
    return rsp

def sendforauthorization(avars):
    #logger.loggerpms2.info("Enter Get Treatment")
    
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = otrtmnt.sendforauthorization(request.folder,int(common.getid(avars["treatmentid"])))
    return rsp


def newtreatment(avars):
    #logger.loggerpms2.info("Enter New Treatment")    
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = otrtmnt.newtreatment(int(common.getid(avars["memberid"])),int(common.getid(avars["patientid"])))
    
    return rsp

def updatetreatment(avars):
    #logger.loggerpms2.info("Enter Update Treatment")
    
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = otrtmnt.updatetreatment(int(common.getid(avars["treatmentid"])), avars["treatmentdate"], avars["chiefcomplaint"], \
                                  int(common.getid(avars["doctorid"])), avars["notes"],avars["status"] if 'status' in avars else 'Started')
    
    return rsp

def treatmentstatus(avars):
    #logger.loggerpms2.info("Enter New Treatment")    
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = otrtmnt.treatmentstatus()
    
    return rsp


############################ Procedures API #######################################################
def getprocedures(avars):
    #logger.loggerpms2.info("Enter Get Procedures")
    
    oproc = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oproc.getprocedures(avars['page']  if 'page' in avars else 0,int(common.getid(avars["treatmentid"])),common.getstring(avars["searchphrase"]))
    return rsp

def canceltreatmentprocedure(avars):
    oproc = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oproc.canceltreatmentprocedure(int(common.getid(avars["treatmentid"])),int(common.getid(avars["treatmentprocedureid"])))
    return rsp

def completetreatmentprocedure(avars):
    oproc = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oproc.completetreatmentprocedure(int(common.getid(avars["treatmentid"])),int(common.getid(avars["treatmentprocedureid"])))
    return rsp

def gettreatmentprocedures(avars):
    oproc = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oproc.gettreatmentprocedures(int(common.getid(avars["treatmentid"])))
    return rsp


def gettreatmentprocedure(avars):
    oproc = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oproc.gettreatmentprocedure(int(common.getid(avars["treatmentid"])),int(common.getid(avars["treatmentprocedureid"])))
    return rsp

def updatetreatmentprocedure(avars):
    oproc = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oproc.updatetreatmentprocedure(int(common.getid(avars["treatmentid"])),\
                                         int(common.getid(avars["treatmentprocedureid"])),\
                                         float(common.getvalue(avars["procedurefee"])) if 'procedurefee' in avars else 0, \
                                         float(common.getvalue(avars["copay"])) if 'copay' in avars else 0, \
                                         float(common.getvalue(avars["inspays"])) if 'inspays' in avars else 0, \
                                        avars["tooth"],avars["quadrant"],avars["remarks"])
    
    return rsp

def addproceduretotreatment(avars):
    oproc = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oproc.addproceduretotreatment(avars['procedurecode'], avars['treatmentid'], avars['plan'],avars["tooth"],avars["quadrant"],avars["remarks"])
    return rsp


############################ Procedures API #######################################################
def uploadimage(avars):
    
    #def uploadimage(self,imagedata,memberid,patientid,treatmentid,title,tooth,quadrant,imagedate,description):    
    oimage = mdpimage.Image(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oimage.uploadimage(avars["imagedata"],
                                  int(common.getid(avars["memberid"])),
                                  int(common.getid(avars["patientid"])),
                                  int(common.getid(avars["treatmentid"])),
                                  avars["title"],
                                  avars["tooth"],
                                  avars["quadrant"],
                                  avars["imagedate"],
                                  avars["description"],
                                  request.folder)
    
    return rsp


#import io
 
#with open('photo.jpg', 'rb') as inf:
    #jpgdata = inf.read()
 
#if jpgdata.startswith(b'\xff\xd8'):
    #text = u'This is a jpeg file (%d bytes long)\n'
#else:
    #text = u'This is a random file (%d bytes long)\n'
 
#with io.open('summary.txtw', encoding='utf-8') as outf:
    #outf.write(text % len(jpgdata))

def preupload():
    
    filename = request.vars.imagefile
    xstr = ""
    with open(filename, "rb") as imageFile:
	xstr = base64.b64encode(imageFile.read())
    
    oimage = mdpimage.Image(current.globalenv['db'],108)
    rsp = oimage.xuploadimage(xstr,request.folder)
       
    return

def xuploadimage(avars):
    
    #def uploadimage(self,imagedata,memberid,patientid,treatmentid,title,tooth,quadrant,imagedate,description):    
    oimage = mdpimage.Image(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oimage.xuploadimage(avars["imagedata"],request.folder)
    
    return rsp

def downloadimage(avars):
    
    urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.mydp_ipaddress)
    oimage = mdpimage.Image(current.globalenv['db'],int(common.getid(avars["providerid"])))
    imgobj = oimage.downloadimage(avars["imageid"])
    imgobj["imageurl"] = urlprops[0].mydp_ipaddress + URL('dentalimage',"download", args=imgobj["image"])
    
    return json.dumps(imgobj)


def getimages(avars):
    oimage = mdpimage.Image(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oimage.getimages(avars['page']  if 'page' in avars else 0,avars['memberid'],avars['patientid'])
    return rsp

def deleteimage(avars):
    oimage = mdpimage.Image(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oimage.deleteimage(int(common.getid(avars['imageid'])))
    return rsp
    
def updateimage(avars):
    oimage = mdpimage.Image(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oimage.updateimage(int(common.getid(avars['imageid'])), avars["title"], avars["tooth"], avars["quadrant"], avars["description"])
    return rsp


############################ GroupSMSMessage API ##################################################
def groupsmsmessage(avars):
    
    #logger.loggerpms2.info("Enter GroupSMSMessage API")
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = oappts.groupsms(request.folder)
    
    return rsp

######################################################## OTP  APIS  ##################################


def unknown(avars):
    return dict()

mdpapi_switcher = {"listappointments":getappointments,"getappointmentsbymonth":getappointmentsbymonth,"getappointmentsbyday":getappointmentsbyday,"getappointment":getappointment,\
                   "getappointmentcountbymonth":getappointmentcountbymonth,"getdocappointmentcountbymonth":getdocappointmentcountbymonth,"getappointmentsbypatient":getappointmentsbypatient,\
                   "getpatappointmentcountbymonth":getpatappointmentcountbymonth,"getpatappointmentsbyday":getpatappointmentsbyday,\
                   "createappointment":newappointment,'updateappointment':updateappointment,'cancelappointment':cancelappointment,'checkinappointment':checkinappointment,\
                   "login":mdplogin,"logout":mdplogout,"forgotusername":forgotusername,"forgotpassword":forgotpassword,\
                   "resetpassword":resetpassword,"searchpatient":searchpatient,"newpatient":newpatient,"getpatient":getpatient,"newalkinpatient":newalkinpatient,"updatewalkinpatient":updatewalkinpatient,\
                   "doctorlist":doctorlist,"doctor":getdoctor,"rolelist":rolelist,"specialitylist":specialitylist,"newpayment":newpayment,\
                   "listpayments":listpayments,"getpayment":getpayment,"paymentcallback":paymentcallback,"groupsmsmessage":groupsmsmessage,"paymentreceipt":paymentreceipt,\
                   "getpaymentlist":getpaymentlist, "getsignedkey":getsignedkey,\
                   "gettreatments":gettreatments,"gettreatment":gettreatment, "newtreatment":newtreatment, "updatetreatment":updatetreatment,
                   "treatmentstatus":treatmentstatus,"getprocedures":getprocedures,"addproceduretotreatment":addproceduretotreatment,"gettreatmentprocedure":gettreatmentprocedure,\
                   "updatetreatmentprocedure":updatetreatmentprocedure,"completetreatmentprocedure":completetreatmentprocedure,"canceltreatmentprocedure":canceltreatmentprocedure,\
                   "gettreatmentprocedures":gettreatmentprocedures,"sendforauthorization":sendforauthorization,\
                   "getpatientnotes":getpatientnotes,"addpatientnotes":addpatientnotes,\
                   "uploadimage":uploadimage,"xuploadimage":xuploadimage,"downloadimage":downloadimage,"getimages":getimages,"deleteimage":deleteimage,"updateimage":updateimage,\
                   "genders":genders,"cities":cities,"states":states,"regions":regions,"status":status,"otpvalidation":otpvalidation,"appointmentstatus":appointmentstatus,\
                   "appointmentduration":appointmentduration,"pattitles":pattitles,"doctitles":doctitles, "getallconstants":getallconstants,\
                   "encrypt":encrypt,"decrypt":decrypt,"decrypts128":decrypts128,"encrypts128":encrypts128,"uploadDocument":uploadDocument,"sendOTP":sendOTP,"validateOTP":validateOTP,\
                   "uploadDocument":uploadDocument,"addProcedure":addProcedure,"getTransactionID":getTransactionID,"getReligarePatient":getReligarePatient,\
                   "addRlgProcedureToTreatment":addRlgProcedureToTreatment,"voidTransaction":voidTransaction,"settleTransaction":settleTransaction,\
                   "getreligareprocedures":getreligareprocedures,"updateReligarePatient":updateReligarePatient,"getMedicalHistory":getMedicalHistory,\
                   "updateMedicalHistory":updateMedicalHistory
                   }


@request.restful()
def mdpapi():

    response.view = 'generic' + request.extension
    def GET(*args, **vars):
        return

    def POST(*args, **vars):
	i = 0
        try:
	    #orlgr = mdpreligare.Religare(current.globalenv['db'],0)
	    #rsp = orlgr.decoderesponsedata(vars["encrypt"])            
	    action = vars["action"]
            rsp = mdpapi_switcher.get(action,unknown)(vars)
            return rsp
        except:
	    action = vars["action"]
            raise HTTP(500)        

    def PUT(*args, **vars):
        return dict()

    def DELETE(*args, **vars):
        return dict()

    return locals()