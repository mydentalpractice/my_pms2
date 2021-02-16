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
from applications.my_pms2.modules import datasecurity

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
from applications.my_pms2.modules import mdpprescription
from applications.my_pms2.modules import mdpwebmember
from applications.my_pms2.modules import mdphdfc
from applications.my_pms2.modules import mdprazorpay
from applications.my_pms2.modules import mdpdentalcasesheet
from applications.my_pms2.modules import mdpdentalchart
from applications.my_pms2.modules import mdppreregister
from applications.my_pms2.modules import mdpmediclaim
from applications.my_pms2.modules import mdplocation
from applications.my_pms2.modules import mdptask
from applications.my_pms2.modules import mdpprovider
from applications.my_pms2.modules import mdpabhicl
from applications.my_pms2.modules import mdpmedia
from applications.my_pms2.modules import mdpcustomer
from applications.my_pms2.modules import mdptimings
from applications.my_pms2.modules import mdpbank
from applications.my_pms2.modules import mdpclinic
from applications.my_pms2.modules import mdpprospect
from applications.my_pms2.modules import mdpagent

from applications.my_pms2.modules import logger



######################################################## Religare Cashless APIS  ##################################
#API-1
def sendOTPCashless(avars):
    rsp = {}
    orlgr = None
    
    
    policy_name = avars.get("policy_name", "RLGCashless")
    props = db(db.rlgproperties.policy_name == policy_name).select()
    url = "" if(len(props)==0) else props[0].url
    apikey = "" if(len(props)==0) else props[0].api_key
    
    try:
	orlgr = mdpreligare.ReligareCashless(current.globalenv['db'],int(common.getid(str(avars["providerid"]))),apikey,url)
	rsp = orlgr.sendOTP(str(avars["mobile_number"]),str(avars["policy_number"]), str(avars["customer_id"]))

    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
  
    return rsp

#API-2
def validateOTPCashless(avars):

    policy_name = avars.get("policy_name", "RLGCashless")
    props = db(db.rlgproperties.policy_name == policy_name).select()
    url = "" if(len(props)==0) else props[0].url
    apikey = "" if(len(props)==0) else props[0].api_key

    
    rsp={}
    try:
	orlgr = mdpreligare.ReligareCashless(current.globalenv['db'],int(common.getid(str(avars["providerid"]))),apikey,url)
	rsp = orlgr.validateOTP(str(avars["ackid"]), str(avars["otp"]), str(avars["policy_number"]),\
	                        str(avars["customer_id"]), str(avars["mobile_number"]),str(avars["policy_name"]))
	
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    return rsp

#API-3
def getOPDServicesCashless(avars):
    
    policy_name = avars.get("policy_name", "RLGCashless")
    props = db(db.rlgproperties.policy_name == policy_name).select()
    url = "" if(len(props)==0) else props[0].url
    apikey = "" if(len(props)==0) else props[0].api_key    

    rsp = {}
    try:
	file_data = avars['document']
	x = uuid.uuid1()
	filename = x.hex + ".jpg"
	orlgr = mdpreligare.ReligareCashless(current.globalenv['db'],int(common.getid(str(avars["providerid"]))),apikey,url)
	rsp = orlgr.getOPDServices(str(avars["ackid"]), str(avars["policy_number"]), 
	                           str(avars["primary_customer_id"]),str(avars["customer_id"]),\
	                           str(avars["mobile_number"]),str(avars["policy_name"]))
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
    
    return rsp

#API-4
def getTransactionIDCashless(avars):
    
    policy_name = avars.get("policy_name", "RLGCashless")
    props = db(db.rlgproperties.policy_name == policy_name).select()
    url = "" if(len(props)==0) else props[0].url
    apikey = "" if(len(props)==0) else props[0].api_key    

    rsp = {}
    try:
	orlgr = mdpreligare.ReligareCashless(current.globalenv['db'],int(common.getid(str(avars["providerid"]))),apikey,url)
	rsp = orlgr.geTransactionID(str(avars["ackid"]), str(avars["service_id"]),\
	                            str(avars["procedurecode"]),str(avars["procedurename"]),\
	                            str(avars["procedurefee"]),
	                            str(avars["procedurepiceplancode"]),
	                            str(avars["policy_number"]), str(avars["customer_id"]), str(avars["mobile_number"]),\
	                            str(avars["policy_name"])
	                            )
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
    return rsp



######################################################## Religare XXX APIS  ##################################
#API-1
def sendOTPXXX(avars):
    rsp = {}
    orlgr = None
    try:
	orlgr = mdpreligare.ReligareXXX(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.sendOTP(str(avars["policy_number"]), str(avars["customer_id"]), str(avars["voucher_code"]),str(avars["policy_name"]))

    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
    #rspencrypted = orlgr.encoderequestdata(rsp)
    #j = {"encrypt":rspencrypted}
    #jstr = json.dumps(j)
    return rsp

#API-2
def validateOTPXXX(avars):
    rsp={}
    try:
	orlgr = mdpreligare.ReligareXXX(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.validateOTP(str(avars["ackid"]), str(avars["otp"]), str(avars["policy_number"]),\
	                        str(avars["customer_id"]), str(avars["voucher_code"]),str(avars["mobile_number"]),str(avars["policy_name"]))
	
	#insert/update records in provider_region_plan for this new policy number
	
	
	    
	
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    return rsp

#API-3
def uploadDocumentXXX(avars):
    rsp = {}
    try:
	file_data = avars['document']
	x = uuid.uuid1()
	filename = x.hex + ".jpg"
	orlgr = mdpreligare.ReligareXXX(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.uploadDocument(str(avars["ackid"]), file_data,filename,str(avars["policy_number"]), 
	                           str(avars["primary_customer_id"]),str(avars["customer_id"]),\
	                           str(avars["voucher_code"]),str(avars["mobile_number"]),str(avars["policy_name"]))
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
    
    return rsp



def getreligarepatientXXX(avars):
    rsp={}
    try:
	orlgr = mdpreligare.ReligareXXX(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.getreligarepatient(avars)
	
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    return rsp

def updatereligarepatientXXX(avars):
    rsp={}
    try:
	orlgr = mdpreligare.ReligareXXX(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.updatereligarepatient(str(avars["memberid"]),str(avars["email"]), str(avars["address1"]), str(avars["address2"]), \
	    str(avars["address3"]), str(avars["city"]),str(avars["st"]),str(avars["pin"]),str(avars["mobile_number"]))
	
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    return rsp

def getreligareproceduresXXX(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.ReligareXXX(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.getreligareprocedures(str(avars["ackid"]), str(avars["procedurepriceplancode"]),\
	                                  str(avars["phrase"]) if "phrase" in avars else "",\
	                                  int(common.getid(str(avars["page"]))) if "page" in avars else 0,\
	                                  int(common.getid(str(avars["maxcount"]))) if "maxcount" in avars else 0)
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
	
    return rsp

def getcompanyprocedures(avars):
    rsp = {}
    try:
	orlgr = mdpprocedure.Procedure(current.globalenv['db'],0)
	rsp = orlgr.getcompanyprocedures(str(avars["procedurepriceplancode"]),\
	                                  str(avars["phrase"]) if "phrase" in avars else "",\
	                                  int(common.getid(str(avars["page"]))) if "page" in avars else 0,\
	                                  int(common.getid(str(avars["maxcount"]))) if "maxcount" in avars else 0)
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
	
    return rsp

def getnoncompanyprocedures(avars):
    rsp = {}
    try:
	orlgr = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.getnoncompanyprocedures(str(avars["procedurepriceplancode"]),\
	                                  str(avars["phrase"]) if "phrase" in avars else "",\
	                                  int(common.getid(str(avars["page"]))) if "page" in avars else 0,\
	                                  int(common.getid(str(avars["maxcount"]))) if "maxcount" in avars else 0)
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
	
    return rsp

#API-4
def getTransactionIDXXX(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.ReligareXXX(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.geTransactionID(str(avars["ackid"]), str(avars["service_id"]),\
	                            str(avars["procedurecode"]),str(avars["procedurename"]),\
	                            str(avars["procedurefee"]),
	                            str(avars["procedurepiceplancode"]),
	                            str(avars["policy_number"]), str(avars["customer_id"]), str(avars["mobile_number"]),\
	                            str(avars["voucher_code"]), str(avars["policy_name"])
	                            )
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
    return rsp

#API-5
def addRlgProcedureToTreatmentXXX(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.ReligareXXX(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.addRlgProcedureToTreatment(str(avars["ackid"]), \
	                                    str(avars["otp"]),\
	                                    str(avars["treatmentid"]),\
	                                    str(avars["plancode"]),\
	                                    str(avars["procedurecode"]),\
	                                    str(avars["procedurename"]),\
	                                    str(avars["procedurefee"]),\
	                                    str(avars["tooth"]),\
	                                    str(avars["quadrant"]),\
	                                    str(avars["remarks"]),\
	                                    str(avars["policy_number"]), 
	                                    str(avars["customer_id"]), 
	                                    str(avars["mobile_number"]),
	                                    str(avars["voucher_code"]), 
	                                    str(avars["policy_name"])
	                            )
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    

    return rsp

#API-6
def settleTransactionXXX(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.ReligareXXX(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.settleTransaction(int(common.getid(str(avars["treatmentid"]))),int(common.getid(str(avars["treatmentprocedureid"]))))
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
    
    
    return rsp


#API-7
def voidTransactionXXX(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.ReligareXXX(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.voidTransaction(int(common.getid(str(avars["treatmentid"]))),int(common.getid(str(avars["treatmentprocedureid"]))))
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
    return rsp

######################################################## Religare 399 APIS  ##################################
def validaterlgmember399(avars):

    try:
	orlgr = mdpreligare.Religare399(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.validaterlgmember399(str(avars["plan_code"]), str(avars["policy"]), str(avars["voucher_code"]))

    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})

    
    return rsp
    
def getreligarepatient399(avars):
    try:
	orlgr = mdpreligare.Religare399(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.getreligarepatient399(avars)

    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})

    
    return rsp
    
    
def updatereligarepatient399(avars):
    try:
	orlgr = mdpreligare.Religare399(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.updatereligarepatient399(avars)

    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})

    
    return rsp
        
def getreligareprocedures399(avars):
    try:
	orlgr = mdpreligare.Religare399(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.getreligareprocedures399(avars)

    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})

    
    return rsp

def addRlgProcedureToTreatment399(avars):
    try:
	orlgr = mdpreligare.Religare399(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.addRlgProcedureToTreatment399(avars)

    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})

    
    return rsp

    
    
######################################################## End Religare 399 APIS  ##################################

######################################################## Religare  APIS  ##################################
def encrypt(avars):
    orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = orlgr.encrypt(avars["raw"])
    return rsp    

def decrypts(avars):
    orlgr = mdpreligare.Religare(current.globalenv['db'],0)
    rsp = orlgr.decrypts(avars["encrypt"])
    return rsp 

    
def decrypt(avars):
    orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = orlgr.decrypt(avars["encrypt"])
    return rsp 

def decrypts128(avars):
    orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = orlgr.decrypts128(avars["encrypt"])
    return rsp 

def encrypts128(avars):
    orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(avars["providerid"])))
    rsp = orlgr.encrypts128(avars["raw"])
    return rsp 

def encrypt_json(avars):
    orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    jsonobj = avars["jsonobj"]
    jsonobjstr = json.dumps(jsonobj)
   
    rsp = orlgr.encrypts(jsonobjstr)
    
    return rsp
    
#API-1
def sendOTP(avars):
    rsp = {}
    orlgr = None
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.sendOTP(str(avars["policy_number"]), str(avars["customer_id"]), str(avars["voucher_code"]))

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
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.validateOTP(str(avars["ackid"]), str(avars["otp"]), str(avars["policy_number"]), str(avars["customer_id"]), str(avars["mobile_number"]))
	
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    return rsp


def getReligarePatient(avars):
    
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.getreligarepatient(str(avars["customer_id"]),\
	                               str(avars["membername"]),\
	                               str(avars["mobile_number"]),\
	                               str(avars["dob"]),\
	                               str(avars["gender"]))
	
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
	
    
    return rsp

def updateReligarePatient(avars):
    
    
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.updatereligarepatient(str(avars["memberid"]),str(avars["email"]), str(avars["address1"]), str(avars["address2"]), \
	    str(avars["address3"]), str(avars["city"]),str(avars["st"]),str(avars["pin"]),str(avars["cell"]))
	
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
	
    
    return rsp

#API-3
def uploadDocument(avars):
    rsp = {}
    try:
	
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
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
	
	rsp = orlgr.uploadDocument(str(avars["ackid"]), file_data,filename,str(avars["policy_number"]), str(avars["customer_id"]), str(avars["mobile_number"]))
    
	#rsp = orlgr.uploadDocument(avars["ackid"], avars["file_data"],avars["file_name"],avars["policy_number"], avars["customer_id"], avars["mobile_number"])
	#rsp = orlgr.uploadDocument(avars["ackid"], avars["document"],"",avars["policy_number"], avars["customer_id"], avars["mobile_number"])
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
    
    return rsp

def addProcedure(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.addProcedure(str(avars["ackid"]), str(avars["sub_service_id"]),str(avars["treatment_code"]),str(avars["treatment_name"]),str(avars["swipe_value"]))
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
    
    return rsp
#API-4
def getTransactionID(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.geTransactionID(str(avars["ackid"]), str(avars["service_id"]),\
	                            str(avars["procedurecode"]),str(avars["procedurename"]),\
	                            str(avars["procedurefee"]),
	                            str(avars["plancode"]),
	                            str(avars["policy_number"]), str(avars["customer_id"]), str(avars["mobile_number"])
	                            )
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
    return rsp

#API-5
def addRlgProcedureToTreatment(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.addRlgProcedureToTreatment(str(avars["ackid"]), \
	                                    str(avars["otp"]),\
	                                    str(avars["treatmentid"]),\
	                                    str(avars["plancode"]),\
	                                    str(avars["procedurecode"]),\
	                                    str(avars["procedurename"]),\
	                                    str(avars["procedurefee"]),\
	                                    str(avars["tooth"]),\
	                                    str(avars["quadrant"]),\
	                                    str(avars["remarks"]),\
	                                    str(avars["policy_number"]), str(avars["customer_id"]), str(avars["mobile_number"])
	                            )
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    

    return rsp



#API-7
def voidTransaction(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.voidTransaction(int(common.getid(str(avars["treatmentid"]))),int(common.getid(str(avars["treatmentprocedureid"]))))
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
    return rsp

def getreligareprocedures(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.getreligareprocedures(str(avars["ackid"]), str(avars["procedurepriceplancode"]),\
	                                  str(avars["phrase"]) if "phrase" in avars else "",\
	                                  int(common.getid(str(avars["page"]))) if "page" in avars else 0,\
	                                  int(common.getid(str(avars["maxcount"]))) if "maxcount" in avars else 0)
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
	
    return rsp

#API-6
def settleTransaction(avars):
    rsp = {}
    try:
	orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
	rsp = orlgr.settleTransaction(int(common.getid(str(avars["treatmentid"]))),int(common.getid(str(avars["treatmentprocedureid"]))))
    except Exception as e:
	rsp = json.dumps({"result":"fail", "error_message":"Exception Error - " + str(e)})
    
    
    
    return rsp




######################################################## USER  APIS  ##################################
#POST method
#Input: {"email"":<emailid>}
#error return - {"result":False,"Message":<mssg>}
#success return - {"result":True,"username":<usernam>}
def forgotusername(avars):
    ouser = mdpuser.User(current.globalenv['db'],current.auth,"","")
    mdp_user = ouser.request_username(str(avars["email"]))
    return mdp_user

#POST method
#Input: {"email":<email>, "username":<username}
#Return:{"result":True,"resetpasswordkey":<passwordkey>}
#{"result":False, "message":<error message>}
def forgotpassword(avars):
    ouser = mdpuser.User(current.globalenv['db'],current.auth,avars["username"],"")
    mdp_user = ouser.request_resetpassword(str(avars["email"]))
    return mdp_user

#POST method
#Input: {"username":<username>,"email":<email>,"resetpasswordkey":<resetpasswordkey,"newpassword":<newpassword>}
#error return - {"result":False,"Message":<mssg>}
#success return - {"result":True}
def resetpassword(avars):
    ouser = mdpuser.User(current.globalenv['db'],current.auth,str(avars["username"]),"")
    mdp_user = ouser.reset_password(str(avars["email"]),str(avars["resetpasswordkey"]), str(avars["newpassword"]))
    
    return mdp_user

def encrypt_login(avars):
    orlgr = mdpreligare.Religare(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = orlgr.encrypt_login("login",0,str(avars["username"]),str(avars["password"])) 
    return json.dumps({"req_data":rsp})
    

def encrypted_mdplogin(avars):
    orlgr = mdpreligare.Religare(current.globalenv['db'],0)    
    #avars = json.loads(orlgr.decrypts(avars["req_data"]))
    ouser = mdpuser.User(current.globalenv['db'],current.auth,avars["username"],avars["password"])
    mdp_user = ouser.login()
    return mdp_user



    
#POST method
#input:{"username":<username>,"password":<password>}
#return:user_data ={"result" : False,"message":"Authentication Error"}
#user_data ={"result" : True,"usertype":"webadmin","providerid":int(provdict["providerid"]),"providername":provdict["providername"]}
#user_data ={"result" : True,"usertype":"provider","providerid":int(provdict["providerid"]),"provider":provdict["provider"],
#"providername":provdict["providername"],"registration":provdict["registration"]}
def mdplogin(avars):
    ouser = mdpuser.User(current.globalenv['db'],current.auth,str(avars["username"]),str(avars["password"]))
    mdp_user = ouser.login()
    return mdp_user

def mdplogout(avars):
    ouser = mdpuser.User(current.globalenv['db'],current.auth,str(avars["username"]),str(avars["password"]))
    rsp = ouser.logout()
    return rsp

def otpvalidation(avars):
    ouser = mdpuser.User(current.globalenv['db'],None,"","")
    rsp = ouser.otpvalidation(str(avars["cell"]), str(avars["email"]), str(avars["otp"]), datetime.datetime.strptime(str(avars["otpdatetime"]),"%d/%m/%Y %H:%M:%S"))
    
    return rsp
    
def getallconstants(avars):
    ouser = mdpuser.User(current.globalenv['db'],None,"","")
    rsp = ouser.getallconstants()
    
    return rsp

def member_registration(avars):
    ouser = mdpuser.User(current.globalenv['db'],current.auth,"","")
    rsp = ouser.member_registration(current.globalenv["request"], str(avars["sitekey"]), \
                             str(avars["email"]), str(avars["cell"]), \
                             str(avars["registration_id"]) if "registration_id" in avars else str(avars["cell"]),\
                             str(avars["username"]), str(avars["password"])
                            )
    
    return rsp

def provider_registration(avars):
    ouser = mdpuser.User(current.globalenv['db'],current.auth,"","")
    rsp = ouser.provider_registration(current.globalenv["request"],\
                                      str(avars["providername"]), \
                                      str(avars["sitekey"]), \
                                      str(avars["email"]),\
                                      str(avars["cell"]), \
                                      str(avars["registration_id"]) if "registration_id" in avars else str(avars["cell"]),\
                                      str(avars["username"]),\
                                      str(avars["password"]),\
                                      str(avars["role"])
                            )
    
    return rsp

def agent_otp_login(avars):
    
    ouser = mdpuser.User(current.globalenv['db'],current.auth,"","")
    mdp_user = ouser.agent_otp_login(avars)
    return mdp_user 

def otp_login(avars):
    
    ouser = mdpuser.User(current.globalenv['db'],current.auth,"","")
    mdp_user = ouser.otp_login(avars)
    return mdp_user 


def getmailserverdetails(avars):
    ouser = mdpuser.User(current.globalenv['db'],None,"","")
    rsp = ouser.getmailserverdetails()
    
    return rsp


######################################################## PROVIDER APIS  ##################################    
def updatememberprovider(avars):
    oprov = mdpprovider.Provider(db, 0)
    prov = oprov.updatememberprovider(int(common.getid(str(avars["memberid"]))),int(common.getid(str(avars["newproviderid"]))))
    return prov

def getprovider(avars):
    oprov = mdpprovider.Provider(db, int(common.getid(str(avars["providerid"]))))
    prov = oprov.getprovider()
    return prov


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
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    pat = opat.newpatient(str(avars['fname']),str(avars['mname']),str(avars['lname']),str(avars['cell']),str(avars['email']))
    #pat = opat.getpatient(pat[0],pat[1])
    return pat



#input - groupref,title,fname,mname,lname,cell,emailid,dob,gender,address1,address2,address3,city,st,pin,
#output - memberid,patientid 
def updatewalkinpatient(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    pat = opat.updatewalkinpatient(avars)
    return pat


#input - groupref,title,fname,mname,lname,cell,emailid,dob,gender,address1,address2,address3,city,st,pin,
#output - memberid,patientid 
def newalkinpatient(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    pat = opat.newalkinpatient(avars)
    return pat

def deletewalkinpatient(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    pat = opat.deletewalkinpatient(int(common.getid(str(avars["memberid"]))))
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
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.mydp_ipaddress)
    imageurl =urlprops[0].mydp_ipaddress + URL('dentalimage',"download")    
    pat = opat.getpatient(str(avars['memberid']),str(avars['patientid']),imageurl)
    
    
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
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    
    company = avars["company"] if "company" in avars else ""
    company = "" if (company == None) | (company == "") else company
    
    member = avars.get('member',None)
    rsp = opat.searchpatient(int(common.getid(str(avars["page"]))) if "page" in avars else 1,str(avars["searchphrase"]),
                            int(common.getid(str(avars["maxcount"]))) if "maxcount" in avars else 0,
                            str(avars["patientmembersearch"]) if "patientmembersearch" in avars else "",
                            None if ((member == "") | (member == None)) else common.getboolean(avars["member"]),
                            company
                             )
    return rsp

def getMediAssistPatients(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opat.getMediAssistPatients(int(common.getid(str(avars["page"]))) if "page" in avars else 1,
                            int(common.getid(str(avars["maxcount"]))) if "maxcount" in avars else 0
                             )
    return rsp


#This returns a list of patient notes entered by a doctor(s)
def getpatientnotes(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opat.getpatientnotes(int(common.getid(str(avars['page'])))  if 'page' in avars else 0,str(avars['memberid']),str(avars['patientid']))
    return rsp

#this saves new note added to the patient notes log
def addpatientnotes(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opat.addpatientnotes(str(avars['memberid']),str(avars['patientid']),str(avars['notes']))
    return rsp

def relations(avars):
    opat = mdppatient.Patient(current.globalenv['db'],0)
    rsp = opat.relations()
    
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

def regionswithid(avars):
    #logger.loggerpms2.info("RegionsWithID==>>\n")
    opat = mdppatient.Patient(current.globalenv['db'],0)
    rsp = opat.regionswithid()
    #logger.loggerpms2.info("RegionsWithID==>>\n")
    #logger.loggerpms2.info(rsp)
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
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opat.getMedicalHistory(str(avars['memberid']),str(avars['patientid']))    
    return rsp

def updateMedicalHistory(avars):
    opat = mdppatient.Patient(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opat.updateMedicalHistory(str(avars['memberid']),str(avars['patientid']),avars["medhistory"])    
    return rsp

############################## DOCTOR API #####################################################

def specialitylist(avars):
    odr = mdpdoctor.Doctor(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    splist = odr.specialitylist()
    return splist

def rolelist(avars):
    odr = mdpdoctor.Doctor(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rllist = odr.rolelist()
    return rllist

def doctorlist(avars):
    odr = mdpdoctor.Doctor(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    drlist = odr.doctorlist()
    return drlist
    
def getdoctor(avars):
    odr = mdpdoctor.Doctor(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    doctor = odr.doctor(int(common.getid(str(avars["doctorid"]))))
    return doctor
############################ APPOINTMENT API ##################################################

    

def new_appointment(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oappts.new_appointment(avars)
    return rsp    
    
def get_appointment(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],common.getkeyvalue(avars,"poviderid",0))
    rsp = oappts.get_appointment(avars)
    return rsp    

def list_appointment(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],common.getkeyvalue(avars,"poviderid",0))
    rsp = oappts.list_appointment(avars)
    return rsp    

def update_appointment(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],common.getkeyvalue(avars,"poviderid",0))
    rsp = oappts.update_appointment(avars)
    return rsp    
    
def cancel_appointment(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],common.getkeyvalue(avars,"poviderid",0))
    rsp = oappts.cancel_appointment(avars)
    return rsp    

def add_block_datetime(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],common.getkeyvalue(avars,"poviderid",0))
    rsp = oappts.add_block_datetime(avars)
    return rsp

def remove_block_datetime(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],common.getkeyvalue(avars,"poviderid",0))
    rsp = oappts.remove_block_datetime(avars)
    return rsp

def list_block_datetime(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],common.getkeyvalue(avars,"poviderid",0))
    rsp = oappts.list_block_datetime(avars)
    return rsp

def get_block_datetime(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],common.getkeyvalue(avars,"poviderid",0))
    rsp = oappts.get_block_datetime(avars)
    return rsp
    
def list_day_appointment_count(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],common.getkeyvalue(avars,"poviderid",0))
    rsp = oappts.list_day_appointment_count(avars)
    return rsp

def list_appointments_byday(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],common.getkeyvalue(avars,"poviderid",0))
    rsp = oappts.list_appointments_byday(avars)
    return rsp

def checkIn(avars):
  
    oappts = mdpappointment.Appointment(current.globalenv['db'],common.getkeyvalue(avars,"poviderid",0))
    rsp = oappts.checkIn(avars)
    return rsp

def checkOut(avars):
  
    oappts = mdpappointment.Appointment(current.globalenv['db'],common.getkeyvalue(avars,"poviderid",0))
    rsp = oappts.checkOut(avars)
    return rsp




def confirm(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],common.getkeyvalue(avars,"poviderid",0))
    rsp = oappts.confirm(avars)
    return rsp

def reSchedule(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],common.getkeyvalue(avars,"poviderid",0))
    rsp = oappts.reSchedule(avars)
    return rsp
    


#getappointments 
#providerid, month, year
#returns list of appointments : apptid, doctorid, patientname, apptdatetime, color
#X
def getappointments(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oappts.appointments(int(common.getid(str(avars["month"]))),int(common.getid(str(avars["year"]))))
    return rsp

#X
def getpatappointmentcountbymonth(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oappts.getpatappointmentcountbymonth(int(common.getid(str(avars["month"]))),int(common.getid(str(avars["year"]))),\
                                          int(common.getid(str(avars["memberid"]))),int(common.getid(str(avars["patientid"]))))
    return rsp

#X
def getappointmentsbypatient(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oappts.getappointmentsbypatient(int(common.getid(str(avars["month"]))),\
                                          int(common.getid(str(avars["year"]))),\
                                          int(common.getid(str(avars["memberid"]))),
                                          int(common.getid(str(avars["patientid"]))))
    return rsp

#X
def getappointmentsbymonth(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oappts.getappointmentsbymonth(int(common.getid(str(avars["month"]))),int(common.getid(str(avars["year"]))))
    return rsp

#this method returns all appointments for a specific day (dd/mm/yyyy) for a provider/patient
#X
def getpatappointmentsbyday(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oappts.getpatappointmentsbyday(int(common.getid(str(avars["day"]))),int(common.getid(str(avars["month"]))),int(common.getid(str(avars["year"]))),\
                                         int(common.getid(str(avars["memberid"]))),int(common.getid(str(avars["patientid"])))\
                                         )
    
    return rsp

    

#X this method returns all appointments for a specific day (dd/mm/yyyy)
def getappointmentsbyday(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oappts.getappointmentsbyday(int(common.getid(str(avars["day"]))),\
                                      int(common.getid(str(avars["month"]))),\
                                      int(common.getid(str(avars["year"]))))
    return rsp

#this method returns all number of appointments for each day of a month
#X
def getappointmentcountbymonth(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oappts.getappointmentcountbymonth(int(common.getid(str(avars["month"]))),int(common.getid(str(avars["year"]))))
    return rsp
#X
def getdocappointmentcountbymonth(avars):
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oappts.getdocappointmentcountbymonth(int(common.getid(str(avars["month"]))),int(common.getid(str(avars["year"]))))
    return rsp


#getappointment 
#providerid, apptid
#returns appointment details
#X
def getappointment(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oappts.appointment(int(common.getid(str(avars["appointmentid"]))))
    return rsp
#X
def checkinappointment(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oappts.checkinappointment(int(common.getid(str(avars["appointmentid"]))))
    return rsp
#X
def newappointment(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oappts.newappointment(int(common.getid(str(avars["memberid"]))),int(common.getid(str(avars["patientid"]))),\
                                int(common.getid(str(avars["doctorid"]))),\
                                str(avars["complaint"]),str(avars["startdt"]),int(common.getid(str(avars["duration"]))),\
                                str(avars["providernotes"]),str(avars["cell"]),\
                                current.globalenv["request"].folder)
    return rsp
#X
def updateappointment(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    
   # (self,appointmentid,doctorid,complaint,startdt,duration,providernotes,cell,status,treatmentid,appPath):
    rsp = oappts.updateappointment(\
        
        int(common.getid(str(avars["appointmentid"]))) if("appointmentid" in avars) else 0,
        int(common.getid(str(avars["doctorid"]))) if("doctorid" in avars) else 0,
        common.getstring(str(avars["complaint"]))  if("complaint" in avars) else "",
        common.getstring(str(avars["startdt"]))  if("startdt" in avars) else "",
        int(common.getid(str(avars["duration"]))) if("duration" in avars) else 0,
        common.getstring(str(avars["providernotes"]))  if("providernotes"in avars) else "",
        common.getstring(str(avars["cell"]))  if("cell" in avars) else "",
        common.getstring(str(avars["status"]))  if("status" in avars) else "",
        int(common.getid(str(avars["treatmentid"]))) if("treatmentid" in avars) else 0,
        current.globalenv["request"].folder)    


    return rsp
#X
def cancelappointment(avars):
    
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    
   # (self,appointmentid,doctorid,complaint,startdt,duration,providernotes,cell,status,treatmentid,appPath):
    rsp = oappts.cancelappointment(\
        
        int(common.getid(str(avars["appointmentid"]))) if("appointmentid" in avars) else 0,
       
        common.getstring(str(avars["providernotes"]))  if("providernotes"in avars) else "",
       
        current.globalenv["request"].folder)    


    return rsp
#X
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
    
    opaymnt = mdppayment.Payment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opaymnt.listpayments(int(common.getid(str(avars["memberid"]))),int(common.getid(str(avars["patientid"]))))
    return rsp

#Input: db, providerid, paymentid
#Ouput: paymentcount, paymentsummary:{treatmentcost,copay,inspays,totaltreatmentcost,totalinspays,totalcopay,totaldue}, {memberid,patientid,patientname,paymentdate,treatmentid,treatmentdate,treatment,procedures,
#totaltreatmentcost,totalinspays,totalcopay,totalpaid,totaldue}
def getpayment(avars):
    
    opaymnt = mdppayment.Payment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opaymnt.getpayment(int(common.getid(str(avars["paymentid"]))))
    return rsp

def paymentcallback(avars):
    opaymnt = mdppayment.Payment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opaymnt.paymentcallback(avars)
    return rsp
    
def newpayment(avars):
    opaymnt = mdppayment.Payment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opaymnt.newpayment(int(common.getid(str(avars["memberid"]))),int(common.getid(str(avars["patientid"]))),int(common.getid(str(avars["treatmentid"]))))
    return rsp

def getpaymentlist(avars):
    opaymnt = mdppayment.Payment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opaymnt.getpaymentlist(int(common.getid(str(avars["memberid"]))),int(common.getid(str(avars["patientid"]))),int(common.getid(str(avars["treatmentid"]))))
    return rsp

def paymentreceipt(avars):
    opaymnt = mdppayment.Payment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opaymnt.paymentreceipt(int(common.getid(str(avars["paymentid"]))))
    return rsp


def getsignedkey(avars):
    opaymnt = mdppayment.Payment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opaymnt.getsignedkey(str(avars["signedip"]),current.globalenv["request"].folder)
    return rsp

############################ Treatments API #######################################################
def gettreatments(avars):
    #logger.loggerpms2.info("Enter Get Treatments")
    
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = otrtmnt.gettreatments(int(common.getid(str(avars["page"]))) if "page" in avars else 1, 
                                int(common.getid(str(avars["memberid"]))),int(common.getid(str(avars["patientid"]))),
                                common.getstring(str(avars["searchphrase"])) if "searchphrase" in avars else "",
                                int(common.getid(str(avars["maxcount"]))) if "maxcount" in avars else 0,
                                (None if(avars["treatmentyear"] == "") else avars["treatmentyear"])  if "treatmentyear" in avars else None,
                                                                                           
                                )
    return rsp

#def gettreatmentsbypatient(avars):
    ##logger.loggerpms2.info("Enter Get Treatments")
    
    #otrtmnt = mdptreatment.Treatment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    #rsp = otrtmnt.gettreatments(int(common.getid(str(avars["page"]))) if "page" in avars else 1, 
                                #int(common.getid(str(avars["memberid"]))),int(common.getid(str(avars["patientid"]))),
                                #common.getstring(str(avars["searchphrase"])) if "searchphrase" in avars else "",
                                #int(common.getid(str(avars["maxcount"]))) if "maxcount" in avars else 0,
                                #common.getstring(str(avars["treatmentyear"])) if "treatmentyear" in avars else None,
                                                                                           
                                #)
    #return rsp


def getopentreatments(avars):
    #logger.loggerpms2.info("Enter Get Treatments")
    
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = otrtmnt.getopentreatments(int(common.getid(str(avars["page"]))) if "page" in avars else 1, 
                                    int(common.getid(str(avars["memberid"]))) if "memberid" in avars else 0,\
                                    int(common.getid(str(avars["patientid"]))) if "patientid" in avars else 0,\
                                    common.getstring(str(avars["searchphrase"])) if "searchphrase" in avars else "",\
                                    int(common.getid(str(avars["maxcount"]))) if "maxcount" in avars else 0
                                                                                           
                                )
    return rsp


def gettreatment(avars):
    #logger.loggerpms2.info("Enter Get Treatment")
    
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = otrtmnt.gettreatment(int(common.getid(str(avars["treatmentid"]))))
    return rsp

def sendforauthorization(avars):
    #logger.loggerpms2.info("Enter Get Treatment")
    
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = otrtmnt.sendforauthorization(request.folder,int(common.getid(str(avars["treatmentid"]))))
    return rsp


def newtreatment(avars):
    #logger.loggerpms2.info("Enter New Treatment")    
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = otrtmnt.newtreatment(int(common.getid(str(avars["memberid"]))),int(common.getid(str(avars["patientid"]))))
    
    return rsp

def updatetreatment(avars):
    #logger.loggerpms2.info("Enter Update Treatment")
    
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = otrtmnt.updatetreatment(int(common.getid(str(avars["treatmentid"]))), str(avars["treatmentdate"]), str(avars["chiefcomplaint"]), \
                                  int(common.getid(str(avars["doctorid"]))), str(avars["notes"]),str(avars["status"]) if 'status' in avars else 'Started')
    
    return rsp

def treatmentstatus(avars):
    #logger.loggerpms2.info("Enter New Treatment")    
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = otrtmnt.treatmentstatus()
    
    return rsp


############################ Procedures API #######################################################
def getprocedures(avars):
    #logger.loggerpms2.info("Enter Get Procedures")
    
    oproc = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oproc.getprocedures(int(common.getid(str(avars["treatmentid"]))),\
                              common.getstring(str(avars["searchphrase"])),\
                              int(common.getid(str(avars['page'])))  if 'page' in avars else 0,\
                              int(common.getid(str(avars['maxcount'])))  if 'maxcount' in avars else 0
                              )
    return rsp

def canceltreatmentprocedure(avars):
    oproc = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oproc.canceltreatmentprocedure(int(common.getid(str(avars["treatmentid"]))),int(common.getid(str(avars["treatmentprocedureid"]))))
    return rsp

def completetreatmentprocedure(avars):
    oproc = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oproc.completetreatmentprocedure(int(common.getid(str(avars["treatmentid"]))),int(common.getid(str(avars["treatmentprocedureid"]))))
    return rsp

def gettreatmentprocedures(avars):
    oproc = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oproc.gettreatmentprocedures(int(common.getid(str(avars["treatmentid"]))))
    return rsp


def gettreatmentprocedure(avars):
    oproc = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oproc.gettreatmentprocedure(int(common.getid(str(avars["treatmentid"]))),int(common.getid(str(avars["treatmentprocedureid"]))))
    return rsp

def updatetreatmentprocedure(avars):
    oproc = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oproc.updatetreatmentprocedure(int(common.getid(str(avars["treatmentid"]))),\
                                         int(common.getid(str(avars["treatmentprocedureid"]))),\
                                         float(common.getvalue(str(avars["procedurefee"]))) if 'procedurefee' in avars else 0, \
                                         float(common.getvalue(str(avars["copay"]))) if 'copay' in avars else 0, \
                                         float(common.getvalue(str(avars["inspays"]))) if 'inspays' in avars else 0, \
                                        str(avars["tooth"]),str(avars["quadrant"]),str(avars["remarks"]))
    
    return rsp

def addproceduretotreatment(avars):
    oproc = mdpprocedure.Procedure(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oproc.addproceduretotreatment(str(avars['procedurecode']), str(avars['treatmentid']), str(avars['plan']),str(avars["tooth"]),str(avars["quadrant"]),str(avars["remarks"]))
    return rsp


############################ Procedures API #######################################################
def uploadimage(avars):
    
    #def uploadimage(self,imagedata,memberid,patientid,treatmentid,title,tooth,quadrant,imagedate,description):    
    oimage = mdpimage.Image(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oimage.uploadimage(str(avars["imagedata"]),
                                  int(common.getid(str(avars["memberid"]))),
                                  int(common.getid(str(avars["patientid"]))),
                                  int(common.getid(str(avars["treatmentid"]))),
                                  str(avars["title"]),
                                  str(avars["tooth"]),
                                  str(avars["quadrant"]),
                                  str(avars["imagedate"]),
                                  str(avars["description"]),
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
    oimage = mdpimage.Image(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oimage.xuploadimage(str(avars["imagedata"]),request.folder)
    
    return rsp

def downloadimage(avars):
    
    urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.mydp_ipaddress)
    oimage = mdpimage.Image(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    imgobj = oimage.downloadimage(str(avars["imageid"]))
    imgobj["imageurl"] = urlprops[0].mydp_ipaddress + URL('dentalimage',"download", args=imgobj["image"])
    
    return json.dumps(imgobj)


def getimages(avars):
    oimage = mdpimage.Image(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oimage.getimages(int(common.getid(str(avars['page'])))  if 'page' in avars else 0,str(avars['memberid']),str(avars['patientid']))
    return rsp

def deleteimage(avars):
    oimage = mdpimage.Image(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oimage.deleteimage(int(common.getid(str(avars['imageid']))))
    return rsp
    
def updateimage(avars):
    oimage = mdpimage.Image(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oimage.updateimage(int(common.getid(str(avars['imageid']))), str(avars["title"]), str(avars["tooth"]), str(avars["quadrant"]), str(avars["description"]))
    return rsp


############################ Prescription API ##################################################
def getmedicines(avars):
    opres = mdpprescription.Prescription(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opres.getmedicines(common.getstring(str(avars["searchphrase"])),\
                              int(common.getid(str(avars['page'])))  if 'page' in avars else 0,\
                              int(common.getid(str(avars['maxcount'])))  if 'maxcount' in avars else 0
                              )
    
    
    return rsp


def getmedicine(avars):
    opres = mdpprescription.Prescription(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opres.getmedicine(int(common.getid(str(avars['medicineid']))))
    
    
    return rsp

def updatemedicine(avars):
    opres = mdpprescription.Prescription(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opres.updatemedicine(avars['medicine'])
    
    
    return rsp

def getprescriptions(avars):
    opres = mdpprescription.Prescription(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opres.getprescriptions(\
                               int(common.getid(str(avars['memberid'])))  if 'memberid' in avars else 0,\
                               int(common.getid(str(avars['patientid'])))  if 'patientid' in avars else 0,\
                               common.getstring(str(avars["searchphrase"])),\
                               int(common.getid(str(avars['page'])))  if 'page' in avars else 0,\
                               int(common.getid(str(avars['maxcount'])))  if 'maxcount' in avars else 0
                              )
    return rsp

def getprescription(avars):
    opres = mdpprescription.Prescription(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opres.getprescription(\
                               int(common.getid(str(avars['presid'])))  if 'presid' in avars else 0
                              )
    return rsp

def newprescription(avars):
    opres = mdpprescription.Prescription(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opres.newprescription(avars)
    return rsp

def updateprescription(avars):
    opres = mdpprescription.Prescription(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opres.updateprescription(int(common.getid(str(avars['presid'])))  if 'presid' in avars else 0,avars)
    return rsp

def deleteprescription(avars):
    opres = mdpprescription.Prescription(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = opres.deleteprescription(int(common.getid(str(avars['presid'])))  if 'presid' in avars else 0)
    return rsp


############################ Web Member API ##################################################
def getwebmember(avars):
    omember = mdpwebmember.Webmember(current.globalenv['db'],0)
    rsp = omember.getwebmember(int(common.getid(str(avars['webmemberid']))))
    return rsp

def updatewebmember(avars):
    omember = mdpwebmember.Webmember(current.globalenv['db'],0)
    rsp = omember.updatewebmember(avars)
    return rsp

def getplansbyregion(avars):
    omember = mdpwebmember.Webmember(current.globalenv['db'],0)
    rsp = omember.getplansbyregion(int(common.getid(str(avars['regionid']))) if 'regionid' in avars else 0 ,\
                                   int(common.getid(str(avars['companyid'])))  if 'companyid' in avars else 0
                                   )
    return rsp

def getwebmemberdependants(avars):
    omember = mdpwebmember.Webmember(current.globalenv['db'],0)
    rsp = omember.getwebmemberdependants(int(common.getid(str(avars['webmemberid']))))
    return rsp

def getwebmemberdependant(avars):
    omember = mdpwebmember.Webmember(current.globalenv['db'],0)
    rsp = omember.getwebmemberdependant(int(common.getid(str(avars['webmemberdependantid']))))
    return rsp

def updatewebmemberdependant(avars):
    
    omember = mdpwebmember.Webmember(current.globalenv['db'],0)
    rsp = omember.updatewebmemberdependant(avars)
    
    return rsp

def deletewebmemberdependant(avars):
    omember = mdpwebmember.Webmember(current.globalenv['db'],0)
    rsp = omember.deletewebmemberdependant(avars)
    return rsp

def newwebmemberpremiumpayment(avars):
    omember = mdpwebmember.Webmember(current.globalenv['db'],0)
    rsp = omember.newwebmemberpremiumpayment(int(common.getid(str(avars['webmemberid']))))
    return rsp

def newwebmemberprocesspayment(avars):
    omember = mdpwebmember.Webmember(current.globalenv['db'],0)
    rsp = omember.newwebmemberprocesspayment(int(common.getid(str(avars['webmemberid']))),avars)
    return rsp

def createwebmember_razorpay_order(avars):
    #logger.loggerpms2.info("Enter createwebmember_razorpay_order")
    omember = mdpwebmember.Webmember(current.globalenv['db'],0)
    rsp = omember.createwebmember_razorpay_order(float(common.getvalue(avars['amount'])),\
                                          common.getstring(avars["currency"]),\
                                          common.getstring(avars["receipt"]),\
                                          common.getstring(avars["payment_capture"]))
    return rsp

def capturewebmember_razorpay_payment(avars):
    omember = mdpwebmember.Webmember(current.globalenv['db'],0)
    rsp = omember.capturewebmember_razorpay_payment(float(common.getvalue(avars['amount'])),\
                                             common.getstring(avars["razorpay_id"]),\
                                             common.getstring(avars["razorpay_order_id"]),\
                                             avars["newpayment"]
                                             )
    
   
    return rsp
    
def printpremium_payment_receipt(avars):
    omember = mdpwebmember.Webmember(current.globalenv['db'],0)
    rsp = omember.printpremium_payment_receipt(avars["payobj"])
    
   
    return rsp
    
########################### HDFC API ##################################################
def gethdfc_constants(avars):
    ohdfc = mdphdfc.HDFC(current.globalenv['db'],0)
    rsp = ohdfc.gethdfc_constants()
    return rsp

def gethdfc_rsakey(avars):
    ohdfc = mdphdfc.HDFC(current.globalenv['db'],0)
    rsp = ohdfc.gethdfc_rsakey(int(common.getstring(avars['paymentid'])))
    return rsp
    
########################### Razorpay API ##################################################
def getrazorpay_constants(avars):
    orazorpay = mdprazorpay.Razorpay(current.globalenv['db'],0)
    rsp = orazorpay.getrazorpay_constants()
    return rsp

def create_razorpay_order(avars):
    orazorpay = mdprazorpay.Razorpay(current.globalenv['db'],int(common.getid(avars['providerid'])))
    rsp = orazorpay.create_razorpay_order(float(common.getvalue(avars['amount'])),\
                                          common.getstring(avars["currency"]),\
                                          common.getstring(avars["receipt"]),\
                                          common.getstring(avars["payment_capture"]))
    return rsp

def capture_razorpay_payment(avars):
    orazorpay = mdprazorpay.Razorpay(current.globalenv['db'],int(common.getid(avars['providerid'])))
    rsp = orazorpay.capture_razorpay_payment(float(common.getid(avars['amount'])),\
                                             common.getstring(avars["razorpay_id"]),\
                                             common.getstring(avars["razorpay_order_id"]),\
                                             avars["newpayment"]
                                             )
    return rsp

########################### Case Report API ##################################################
def createcasereport(avars):
    ocsr = mdpdentalcasesheet.Dentalcasesheet(current.globalenv['db'],int(common.getid(avars['providerid'])))
    rsp	= ocsr.createcasereport(avars)
    return rsp
def get_casereport_list(avars):
    ocsr = mdpdentalcasesheet.Dentalcasesheet(current.globalenv['db'],int(common.getid(avars['providerid'])))
    rsp	= ocsr.get_casereport_list(common.getstring(avars["email"]),common.getstring(avars["cell"]))
    return rsp
def getcasereport(avars):
    ocsr = mdpdentalcasesheet.Dentalcasesheet(current.globalenv['db'],int(common.getid(avars['providerid'])))
    rsp	= ocsr.getcasereport(int(common.getstring(avars["id"])))
    return rsp
def updatecasereport(avars):
    ocsr = mdpdentalcasesheet.Dentalcasesheet(current.globalenv['db'],int(common.getid(avars['providerid'])))
    rsp	= ocsr.updatecasereport(avars)
    return rsp

############################ Dental Chart API ##################################################
def getdentalchart(avars):
    odch = mdpdentalchart.Dentalchart(current.globalenv['db'],int(common.getid(avars['providerid'])))
    rsp = odch.getdentalchart(int(common.getid(str(avars['memberid']))) if 'memberid' in avars else 0 ,\
	                                   int(common.getid(str(avars['patientid'])))  if 'patientid' in avars else 0
	                                   )
    return rsp

def gettoothcolours(avars):
    odch = mdpdentalchart.Dentalchart(current.globalenv['db'],int(common.getid(avars['providerid'])))
    rsp = odch.gettoothcolours(int(common.getid(str(avars['chartid']))) if 'chartid' in avars else 0 ,\
	                                   int(common.getid(str(avars['toothnumber'])))  if 'toothnumber' in avars else 0
	                                   )
    return rsp

def getalltoothcolours(avars):
    odch = mdpdentalchart.Dentalchart(current.globalenv['db'],int(common.getid(avars['providerid'])))
    rsp = odch.getalltoothcolours(int(common.getid(str(avars['chartid']))) if 'chartid' in avars else 0\
	                                   )
    return rsp


def getchartprocedures(avars):
    odch = mdpdentalchart.Dentalchart(current.globalenv['db'],int(common.getid(avars['providerid'])))
    rsp = odch.getchartprocedures()
    
    return rsp


############################ Pre Register API ##################################################
def newpreregister(avars):
    oprereg = mdppreregister.Preregister(current.globalenv['db'],int(common.getid(avars['providerid'])),common.getstring(avars['company']) if "company" in avars else "")
    rsp = oprereg.newpreregister(avars)
    
    return rsp

def getpreregister(avars):
    oprereg = mdppreregister.Preregister(current.globalenv['db'],int(common.getid(avars['providerid'])),common.getstring(avars['company']) if "company" in avars else "")
    rsp = oprereg.getpreregister(int(common.getid(avars['preregisterid'])))
    
    return rsp

def get_preregister_list(avars):
    oprereg = mdppreregister.Preregister(current.globalenv['db'],int(common.getid(avars['providerid'])),common.getstring(avars['company']) if "company" in avars else "")
    rsp = oprereg.get_preregister_list()
    
    return rsp


def updatepreregister(avars):
    oprereg = mdppreregister.Preregister(current.globalenv['db'],int(common.getid(avars['providerid'])),common.getstring(avars['company']) if "company" in avars else "")
    rsp = oprereg.updatepreregister(avars)
    
    return rsp



def deletepreregister(avars):
    oprereg = mdppreregister.Preregister(current.globalenv['db'],int(common.getid(avars['providerid'])),common.getstring(avars['company']) if "company" in avars else "")
    rsp = oprereg.deletepreregister(int(common.getid(avars['preregisterid'])))
    
    return rsp


def uploadphoto(avars):
    oprereg = mdppreregister.Preregister(current.globalenv['db'],int(common.getid(avars['providerid'])),common.getstring(avars['company']) if "company" in avars else "")
    rsp = oprereg.uploadphoto(int(common.getid(avars['preregisterid'])),str(avars["imagedata"]),request.folder)
    
    return rsp

def deletephoto(avars):
    oprereg = mdppreregister.Preregister(current.globalenv['db'],int(common.getid(avars['providerid'])),common.getstring(avars['company']) if "company" in avars else "")
    rsp = oprereg.deletephoto(int(common.getid(avars['preregisterid'])))
    
    return rsp


def newpreregisterimage(avars):
    oprereg = mdppreregister.Preregister(current.globalenv['db'],int(common.getid(avars['providerid'])),common.getstring(avars['company']) if "company" in avars else "")
    rsp = oprereg.newpreregisterimage(avars)
    
    return rsp

def updatepreregisterimage(avars):
    oprereg = mdppreregister.Preregister(current.globalenv['db'],int(common.getid(avars['providerid'])),common.getstring(avars['company']) if "company" in avars else "")
    rsp = oprereg.updatepreregisterimage(avars)
    
    return rsp


def uploadpreregisterimage(avars):
    oprereg = mdppreregister.Preregister(current.globalenv['db'],int(common.getid(avars['providerid'])),common.getstring(avars['company']) if "company" in avars else "")
    rsp = oprereg.uploadpreregisterimage(int(common.getid(avars['preregisterimageid'])),str(avars["imagedata"]),request.folder)
    
    return rsp


def getpreregisterimage(preregisterimageid):
    urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.mydp_ipaddress)
    oprereg = mdppreregister.Preregister(current.globalenv['db'],int(common.getid(avars['providerid'])),common.getstring(avars['company']) if "company" in avars else "")
    imgobj = oprereg.getpreregisterimage(preregisterimageid)
    imgobj["imageurl"] = urlprops[0].mydp_ipaddress + URL('dentalimage',"download", args=imgobj["image"])
    
    return json.dumps(imgobj)


def getpreregisterimages(avars):
    oprereg = mdppreregister.Preregister(current.globalenv['db'],int(common.getid(avars['providerid'])),common.getstring(avars['company']) if "company" in avars else "")
    rsp = oprereg.getpreregisterimages(int(common.getid(avars['page']))  if "page" in avars else 0,int(common.getid(avars['preregid'])))
    
    return rsp


def downloadphoto(avars):
    urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.mydp_ipaddress)
    oprereg = mdppreregister.Preregister(current.globalenv['db'],int(common.getid(avars['providerid'])),common.getstring(avars['company']) if "company" in avars else "")
    imgobj = oprereg.downloadphoto(int(common.getid(avars['preregisterid'])))
    imgobj["imageurl"] = urlprops[0].mydp_ipaddress + URL('dentalimage',"download", args=imgobj["employeephoto"])
    
    return json.dumps(imgobj)


   

############################ GroupSMSMessage API ##################################################
def groupsmsmessage(avars):
    
    #logger.loggerpms2.info("Enter GroupSMSMessage API")
    oappts = mdpappointment.Appointment(current.globalenv['db'],int(common.getid(str(avars["providerid"]))))
    rsp = oappts.groupsms(request.folder)
    
    return rsp

def task(avars):
    logger.loggerpms2.info("Enter Activity Tracker Task at " + (common.getISTFormatCurrentLocatTime()).strftime("%d/%m/%Y %H:%M:%S"))
    otask = mdptask.Task(current.globalenv['db'], 0)
    avars["activitydate"] = (common.getISTFormatCurrentLocatTime()).strftime("%d/%m/%Y")
    rsp = otask.activitytracker(avars)
    logger.loggerpms2.info("TASK API Response " + rsp)
    return rsp
    

######################################################## OTP  APIS  ##################################


############################ Medi Claim API ##################################################
def addmediclaim(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.addmediclaim(int(common.getid(avars["treatmentid"]))  if "treatmentid" in avars else 0, avars)
    
    return rsp

def getmediclaims(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.getmediclaims(int(common.getid(avars["treatmentid"])) if "treatmentid" in avars else 0 )
    
    return rsp


def getmediclaim(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.getmediclaim(int(common.getid(avars["mediclaimid"])) if "mediclaimid" in avars else 0 )
    
    return rsp

def updatemediclaim(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.updatemediclaim(int(common.getid(avars["mediclaimid"])) if "mediclaimid" in avars else 0 , avars)
    
    return rsp

def deletemediclaim(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.deletemediclaim(int(common.getid(avars["mediclaimid"])) if "mediclaimid" in avars else 0 )
    
    return rsp



def addmediclaimcharts(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.addmediclaimcharts(int(common.getid(avars["mediclaimid"])) if "mediclaimid" in avars else 0,avars )
    
    return rsp

def updatemediclaimcharts(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.updatemediclaimcharts(int(common.getid(avars["mediclaimid"])) if "mediclaimid" in avars else 0,avars )
    
    return rsp

def getmediclaimcharts(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.getmediclaimcharts(int(common.getid(avars["mediclaimid"])) if "mediclaimid" in avars else 0 )
    
    return rsp

def deletemediclaimcharts(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.deletemediclaimcharts(int(common.getid(avars["mediclaimid"])) if "mediclaimid" in avars else 0 )
    
    return rsp


def addmediclaimprocedure(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.addmediclaimprocedure(int(common.getid(avars["mediclaimid"])) if "mediclaimid" in avars else 0,
                                       int(common.getid(avars["procedureid"])) if "procedureid" in avars else 0,
                                       int(common.getid(avars["treatmentprocedureid"])) if "treatmentprocedureid" in avars else 0,
                                       avars["procdate"] if "procdate" in avars else "01/01/1990",
                                       avars["tooth"],
				       avars["description"],
                                       avars["quantity"],
                                       avars["cashless"],
                                       avars["status"]
                                       )
    
    return rsp

def updatemediclaimprocedure(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.updatemediclaimprocedure(int(common.getid(avars["mediclaimid"])) if "mediclaimid" in avars else 0,
                                       int(common.getid(avars["procedureid"])) if "procedureid" in avars else 0,
                                       int(common.getid(avars["treatmentprocedureid"])) if "treatmentprocedureid" in avars else 0,
                                       int(common.getid(avars["mediclaimprocedureid"])) if "mediclaimprocedureid" in avars else 0,
                                       avars["procdate"] if "procdate" in avars else "01/01/1990",
                                       avars["tooth"],
				       avars["description"],
                                       avars["quantity"],
                                       avars["cashless"],
                                       avars["status"]
                                       )
    
    return rsp

def deletemediclaimprocedure(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.deletemediclaimprocedure(
                                       int(common.getid(avars["mediclaimprocedureid"])) if "mediclaimprocedureid" in avars else 0
                                       )
    
    return rsp

def getmediclaimprocedure(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.getmediclaimprocedure(int(common.getid(avars["mediclaimprocedureid"])) if "mediclaimprocedureid" in avars else 0)
    
    return rsp

def getmediclaimprocedures(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.getmediclaimprocedures(int(common.getid(avars["treatmentid"])) if "treatmentid" in avars else 0,
                                       int(common.getid(avars["mediclaimid"])) if "mediclaimid" in avars else 0
                                       )
    
    return rsp

def uploadmediclaimsignature(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.uploadmediclaimsignature(int(common.getid(avars["mediclaimid"])) if "mediclaimid" in avars else 0,
                                        str(avars["signature"]) if "signature" in avars else "",
                                        str(avars["signdata"]) if "signdata" in avars else "",
                                        str(avars["signdate"])if "signdate" in avars else "01/01/1990",
                                        request.folder
                                       )
    
    return rsp

def downloadmediclaimsignature(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.downloadmediclaimsignature(str(avars["mediclaimid"]),avars["signature"])
    
    
    obj = json.loads(rsp)
    if(obj["result"] == "success"):
	urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.mydp_ipaddress)
	obj["signatureurl"] = urlprops[0].mydp_ipaddress + URL('admin',"download", args=obj["signdata"])

    rsp = json.dumps(obj)    

    
    return rsp


def deletemediclaimsignature(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.deletemediclaimsignature(int(common.getid(avars["mediclaimid"])) if "mediclaimid" in avars else 0,
                                        str(avars["signature"])  if "signature" in avars else ""
                                       )
    
    return rsp



def addmediclaimattachment(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.addmediclaimattachment(int(common.getid(avars["mediclaimid"])) if "mediclaimid" in avars else 0,
                                        str(avars["attachment"]) if "attachment" in avars else "",
                                        str(avars["title"]) if "title" in avars else "",
                                        str(avars["description"])if "description" in avars else "",
                                        request.folder,
                                        )
    
    return rsp


def getmediclaimattachments(avars):
    
    urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.mydp_ipaddress)
    
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.getmediclaimattachments(int(common.getid(avars["mediclaimid"])) if "mediclaimid" in avars else 0)
    
    
    obj = json.loads(rsp)
    if(obj["result"] == "success"):
	attachments = obj["attachments"]
	for attachment in attachments:
	    attachment["attachurl"] = urlprops[0].mydp_ipaddress + URL('admin',"download", args=attachment["attachment"])
	rsp = json.dumps(obj)
    else:
	rsp = json.dumps(obj)
    
    return rsp


def deletemediclaimattachment(avars):
    
    oclaim = mdpmediclaim.Mediclaim(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    rsp = oclaim.deletemediclaimattachment(int(common.getid(avars["attachmentid"])) if "attachmentid" in avars else 0 )
    
    return rsp


############################# Location API ##################################################


#Calculate the distance (in various units) between two points on Earth using their latitude(lat) and longitude(long).
def getdistance(avars):
    
    oloc = mdplocation.Location(current.globalenv['db'])
    rsp = oloc.getdistance(float(common.getstring(avars["originlat"])) if "originlat" in avars else 0,
                                           float(common.getstring(avars["originlong"])) if "originlong" in avars else 0,                                           
                                           float(common.getstring(avars["destlat"])) if "destlat" in avars else 0,                                           
                                           float(common.getstring(avars["destlong"])) if "destlong" in avars else 0,                                           
                                           avars["unit"] if "unit" in avars else "km",                                           
                                           )
    
    return rsp

#Returns list of providers within a radius of the origin provider
def getproviderswithinradius(avars):
    
    oloc = mdplocation.Location(current.globalenv['db'])
    rsp = oloc.getproviderswithinradius(float(common.getstring(avars["originlat"])) if "originlat" in avars else 0,
                                           float(common.getstring(avars["originlong"])) if "originlong" in avars else 0,                                           
                                           float(common.getstring(avars["radius"])) if "radius" in avars else 0,                                           
                                           avars["unit"] if "unit" in avars else "km"                                          
                                           )
    #rsp = oloc.getproviderswithinradius(int(common.getstring(avars["providerid"])) if "providerid" in avars else 0,
                                           #float(common.getstring(avars["radius"])) if "radius" in avars else 0,                                           
                                           #avars["unit"] if "unit" in avars else "km",                                           
                                           #)
    
    return rsp

#Returns list of providers in a specific pin
def getproviderswithpincode(avars):
    oloc = mdplocation.Location(current.globalenv['db'])
    rsp = oloc.getproviderswithpincode(avars["pin"] if "pin" in avars else "00000000")    
    return rsp

############################# End Location API ##################################################

############################# ABHICL API ##################################################
def dental_service_request(avars):
    logger.loggerpms2.info("Enter Dental Service Request(MDP)-Request\n" + str(avars) )
    appPath = current.globalenv["request"].folder
    oabhicl = mdpabhicl.ABHICL(current.globalenv['db'],appPath)
    rsp = oabhicl.dental_service_request(avars)   
    logger.loggerpms2.info("Enter Dental Service Request(MDP)-Response\n" + rsp)
    return rsp

def get_appointments(avars):
    oabhicl = mdpabhicl.ABHICL(current.globalenv['db'])
    rsp = oabhicl.get_appointments(avars)   
    return rsp

def get_treatments(avars):
    logger.loggerpms2.info("Enter Get Treatments(MDP)-Request\n" + str(avars) )
    oabhicl = mdpabhicl.ABHICL(current.globalenv['db'])
    rsp = oabhicl.get_treatments(avars)   
    logger.loggerpms2.info("Enter Get Treatments(MDP)-Response\n" + rsp )
   
    return rsp

def addABHICLProcedureToTreatment(avars):
    oabhicl = mdpabhicl.ABHICL(current.globalenv['db'],int(common.getid(str(avars["providerid"]))) if "providerid" in avars else 0)
    
    treatmentid = int(common.getid(str(avars["treatmentid"]))) if "treatmentid" in avars else 0    
    procedurepriceplancode = avars["procedurepriceplancode"] if "procedurepriceplancode" in avars else "ABHICSX"    
    procedurecode = avars["procedurecode"] if "procedurecode" in avars else ""    
   
       
  
    tooth = avars["tooth"] if "tooth" in avars else ""    
    quadrant = avars["quadrant"] if "quadrant" in avars else ""    
    remarks = avars["remarks"] if "remarks" in avars else ""    
    abhiclid = avars["abhiclid"] if "abhiclid" in avars else "" 
    abhiclpolicy = avars["abhiclpolicy"] if "abhiclpolicy" in avars else ""
    
    rsp = oabhicl.addABHICLProcedureToTreatment(treatmentid, 
                                               procedurepriceplancode, 
                                               procedurecode, 
                                               tooth, 
                                               quadrant, 
                                               remarks, 
                                               abhiclid, 
                                               abhiclpolicy)
    return rsp


############################# End ABHICL API ##################################################

############################# Media API ######################################################
def upload_media(avars):
    logger.loggerpms2.info("Enter Upload Media-Request\n" + str(avars) )

    
    omedia = mdpmedia.Media(current.globalenv['db'],\
                            int(avars["providerid"]) if "providerid" in avars else 0,\
                            avars["mediatype"] if "mediatype" in avars else "image",\
                            avars["mediaformat"] if "mediaformat" in avars else "jpg"
                            )
    avars["appath"] = current.globalenv["request"].folder
    rsp = omedia.upload_media(avars)
    
   
    logger.loggerpms2.info("Exit Upload Media-Response\n" + rsp )

    return rsp

def upload_mediafile(avars):
    logger.loggerpms2.info("Enter Upload Media File Request\n" + str(avars) )

    
    omedia = mdpmedia.Media(current.globalenv['db'],\
                            int(avars["providerid"]) if "providerid" in avars else 0,\
                            avars["mediatype"] if "mediatype" in avars else "image",\
                            avars["mediaformat"] if "mediaformat" in avars else "jpg"
                            )
    
    rsp = omedia.upload_mediafile(avars)
    
   
    logger.loggerpms2.info("Exit Upload Media File Response\n" + rsp )

    return rsp

def downloadmedia(avars):
    
    logger.loggerpms2.info("Enter Upload Media File Request\n" + str(avars) )
   
       
    omedia = mdpmedia.Media(current.globalenv['db'],\
                            int(avars["providerid"]) if "providerid" in avars else 0,\
                            avars["mediatype"] if "mediatype" in avars else "image",\
                            avars["mediaformat"] if "mediaformat" in avars else "jpg"
                            )
    
    rsp = omedia.downloadmedia(int(avars["mediaid"]) if "mediaid" in avars else 0)
    
   
    
   
    logger.loggerpms2.info("Exit Upload Media File Response\n" + rsp )

    return rsp

def updatemedia(avars):
     
    logger.loggerpms2.info("Enter Upload Media File Request\n" + str(avars) )
   
       
    omedia = mdpmedia.Media(current.globalenv['db'],\
                            int(avars["providerid"]) if "providerid" in avars else 0,\
                            avars["mediatype"] if "mediatype" in avars else "image",\
                            avars["mediaformat"] if "mediaformat" in avars else "jpg"
                            )
    
    rsp = omedia.updatemedia(avars)
    
   
    logger.loggerpms2.info("Exit Upload Media File Response\n" + rsp )
    
    return rsp

def deletemedia(avars):
    
    logger.loggerpms2.info("Enter Upload Media File Request\n" + str(avars) )
   
       
    omedia = mdpmedia.Media(current.globalenv['db'],\
                            int(avars["providerid"]) if "providerid" in avars else 0,\
                            avars["mediatype"] if "mediatype" in avars else "image",\
                            avars["mediaformat"] if "mediaformat" in avars else "jpg"
                            )
    
    rsp = omedia.deletemedia(int(avars["mediaid"]) if "mediaid" in avars else 0)
    
   
    logger.loggerpms2.info("Exit Upload Media File Response\n" + rsp )

    return rsp


def getmedia_list(avars):
    
    
    logger.loggerpms2.info("Get Media List Request\n" + str(avars) )
   
       
    omedia = mdpmedia.Media(current.globalenv['db'],\
                            int(avars["providerid"]) if "providerid" in avars else 0,\
                            avars["mediatype"] if "mediatype" in avars else "image",\
                            avars["mediaformat"] if "mediaformat" in avars else "jpg"
                            )
    
    rsp = omedia.getmedia_list(0, int(avars["memberid"]) if "memberid" in avars else 0, \
                                  int(avars["patientid"]) if "patientid" in avars else 0,\
	                          avars["mediatype"] if "mediatype" in avars else "",\
                                  avars["ref_code"] if "ref_code" in avars else "",\
                                  avars["ref_id"] if "ref_id" in avars else 0
                                  )
	

    
    #rsp = omedia.getmedia_list(0, int(avars["memberid"]) if "memberid" in avars else 0, \
                               #int(avars["patientid"]) if "patientid" in avars else 0,\
                               #int(avars["doctorid"]) if "doctorid" in avars else 0,\
                               #int(avars["clinicid"]) if "clinicid" in avars else 0,\
                               #int(avars["treatmentid"]) if "treatmentid" in avars else 0,\
                               #int(avars["userid"]) if "userid" in avars else 0,\
                               #int(avars["customerid"]) if "customerid" in avars else 0,\
                                #avars["mediatype"] if "mediatype" in avars else "image")
    
    
  
    
   
    logger.loggerpms2.info("Exit Get Nedia List Response\n" + rsp )

    
    return rsp


############################# End Media API ##################################################

############################# VITAL API #######################################################
def register_vital_member(avars):
    logger.loggerpms2.info("Enter Subscribe Vital Member-Request\n" + str(avars) )
    
    policy = common.getkeyvalue(avars,"policy","ViTAL_Z")
    
    #providerid, regioinid = provider's region 
    provcode = common.getkeyvalue(avars,"providercode","P001")
    p = db(db.provider.provider == provcode).select(db.provider.id,db.provider.groupregion)
    providerid = p[0].id if(len(p)==1) else 1
    
    #region (from provider's region)
    regionid = p[0].groupregion if(len(p)==1) else 1
    r = db(db.groupregion.id == regionid).select(db.groupregion.groupregion)
    regioncode = r[0].groupregion if(len(r)==1) else "ALL"
    
    #company
    companycode = common.getkeyvalue(avars,"companycode","VITAL")
    c = db((db.company.company == companycode) & (db.company.is_active == True)).select()
    companyid = c[0].id if(len(c)==1) else 1
    
    #prp
    prp = db((db.provider_region_plan.regioncode == regioncode) & (db.provider_region_plan.policy == policy) & (db.provider_region_plan.is_active == True)).select()
    plancode = prp[0].plancode if(len(prp)==1) else "VITALZ"

    #planid
    h = db((db.hmoplan.hmoplancode == plancode) & (db.hmoplan.groupregion == regionid)).select(db.hmoplan.id)
    planid = h[0].id if(len(h)==1) else 1
    
    avars["providerid"] = providerid
    avars["companyid"] = companyid
    avars["regionid"] = regionid
    avars["planid"] = planid
    

    #address
    avars["address1"] =  avars["address1"] if "address1" in avars else common.getkeyvalue(avars,"address1",c[0].address1)
    avars["address2"] = avars["address2"] if "address2" in avars else common.getkeyvalue(avars,"address2",c[0].address2)
    avars["address3"] = avars["address3"] if "address3" in avars else common.getkeyvalue(avars,"address3",c[0].address3)
    avars["city"] = avars["city"] if "city" in avars else common.getkeyvalue(avars,"city",c[0].city)
    avars["st"] = avars["st"] if "st" in avars else common.getkeyvalue(avars,"st",c[0].st)
    avars["pin"] = avars["pin"] if "pin" in avars else common.getkeyvalue(avars,"pin",c[0].pin)
    avars["pin1"] = avars["pin1"] if "pin1" in avars else common.getkeyvalue(avars,"pin1",c[0].pin)
    avars["pin2"] = avars["pin2"] if "pin2" in avars else common.getkeyvalue(avars,"pin2",c[0].pin)
    avars["pin3"] = avars["pin3"] if "pin3" in avars else common.getkeyvalue(avars,"pin3",c[0].pin)
    
    avars["telephone"] = avars["telephone"] if "telephone" in avars else common.getkeyvalue(avars,"telephone",c[0].telephone)
    avars["cell"] = avars["cell"] if "cell" in avars else common.getkeyvalue(avars,"cell",c[0].cell)
    avars["email"] = avars["email"] if "email" in avars else common.getkeyvalue(avars,"email",c[0].email)
    
    
    #create VITAL Customer
    ovapi  = mdpcustomer.Customer(current.globalenv['db'],providerid)
    rsp = ovapi.customer(avars)
    
    logger.loggerpms2.info("Exit Subcribe Vital Member -Response\n" + rsp)
    return rsp

def set_appointment_vital_member(avars):
    logger.loggerpms2.info("Enter set_appointment_vital_member VITAL Member-Request\n" + str(avars) )
    
    #providerid, regioinid = provider's region 
    provcode = common.getkeyvalue(avars,"providercode","P001")
    p = db(db.provider.provider == provcode).select(db.provider.id,db.provider.groupregion)
    providerid = p[0].id if(len(p)==1) else 1
    
    
    ovapi  = mdpcustomer.Customer(current.globalenv['db'],providerid)
    rsp = ovapi.set_appointment(avars)
    
    
    logger.loggerpms2.info("Exit set_appointment_vital_member VIATL Member -Response\n" + rsp)
    
    return rsp

def enroll_vital_member(avars):
    logger.loggerpms2.info("Enter Enroll VITAL Member-Request\n" + str(avars) )
    
    #providerid, regioinid = provider's region 
    provcode = common.getkeyvalue(avars,"providercode","P001")
    p = db(db.provider.provider == provcode).select(db.provider.id,db.provider.groupregion)
    providerid = p[0].id if(len(p)==1) else 1
    
    
    ovapi  = mdpcustomer.Customer(current.globalenv['db'],providerid)
    rsp = ovapi.enroll_customer(avars)
    
    
    logger.loggerpms2.info("Exit Enroll VIATL Member -Response\n" + rsp)
    
    return rsp

def cancel_vital_member(avars):
    logger.loggerpms2.info("Enter Cancel VITAL Member-Request\n" + str(avars) )
    
    providerid = int(common.getkeyvalue(avars,"providerid","0"))
    
    ovapi  = mdpcustomer.Customer(current.globalenv['db'],providerid)
    rsp = ovapi.delete_customer(avars)
    
    
    logger.loggerpms2.info("Exit Cancel VIATL Member -Response\n" + rsp)
    return rsp



############################# END VITAL API ###################################################


############################# START CLINIC API #################################################
def get_clinic(avars):
    logger.loggerpms2.info("Enter Get Clinic Request\n" + str(avars) )
    ops = mdpclinic.Clinic(current.globalenv['db'])
    rsp = ops.get_clinic(avars)
    
    return rsp

def update_clinic(avars):
    logger.loggerpms2.info("Enter Update Clinic Request\n" + str(avars) )
    ops = mdpclinic.Clinic(current.globalenv['db'])
    rsp = ops.update_clinic(avars)
    return rsp

def delete_clinic(avars):
    logger.loggerpms2.info("Enter Delee Clinic Request\n" + str(avars) )
    ops = mdpclinic.Clinic(current.globalenv['db'])
    rsp = ops.delete_clinic(avars)
    return rsp

def list_clinic(avars):
    logger.loggerpms2.info("Enter List Clinic Request\n" + str(avars) )
    ops = mdpclinic.Clinic(current.globalenv['db'])
    rsp = ops.list_clinic(avars)
    return rsp

def new_clinic(avars):
    logger.loggerpms2.info("Enter New Clinic Request\n" + str(avars) )
    ops = mdpclinic.Clinic(current.globalenv['db'])
    rsp = ops.new_clinic(avars)
    return rsp

def add_doc_clinic(avars):
    logger.loggerpms2.info("Enter Add DOC Clinic Request\n" + str(avars) )
    ops = mdpclinic.Clinic(current.globalenv['db'])
    rsp = ops.add_doc_clinic(avars)
    return rsp

def list_doc_clinic(avars):
    logger.loggerpms2.info("Enter List Doc Clinic Request\n" + str(avars) )
    ops = mdpclinic.Clinic(current.globalenv['db'])
    rsp = ops.list_doc_clinic(avars)
    return rsp

def remove_doc_clinic(avars):
    logger.loggerpms2.info("Enter Remove DOC Clinic Request\n" + str(avars) )
    ops = mdpclinic.Clinic(current.globalenv['db'])
    rsp = ops.remove_doc_clinic(avars)
    return rsp

    
############################# END CLINIC API ###################################################

############################# START OPS TIMING API #################################################
def get_ops_timing(avars):
    logger.loggerpms2.info("Enter Get OPS Timing Request\n" + str(avars) )
    ops = mdptimings.OPS_Timing(current.globalenv['db'])
    rsp = ops.get_ops_timing(avars)
    
    return rsp

def update_ops_timing(avars):
    logger.loggerpms2.info("Enter Update OPS Timing Request\n" + str(avars) )
    ops = mdptimings.OPS_Timing(current.globalenv['db'])
    rsp = ops.update_ops_timing(avars)
    return rsp

def delete_ops_timng(avars):
    logger.loggerpms2.info("Enter Delee OPS Timing Request\n" + str(avars) )
    ops = mdptimings.OPS_Timing(current.globalenv['db'])
    rsp = ops.delete_ops_timng(avars)
    return rsp

def list_ops_timing(avars):
    logger.loggerpms2.info("Enter List OPS Timing Request\n" + str(avars) )
    ops = mdptimings.OPS_Timing(current.globalenv['db'])
    rsp = ops.list_ops_timing(avars)
    return rsp

def new_ops_timing(avars):
    logger.loggerpms2.info("Enter New OPS Timing Request\n" + str(avars) )
    ops = mdptimings.OPS_Timing(current.globalenv['db'])
    rsp = ops.new_ops_timing(avars)
    return rsp
    
############################# END OPS TIMING API ###################################################

############################# START Bank Detail Account API #################################################
def get_account(avars):
    logger.loggerpms2.info("Enter Get Account Request\n" + str(avars) )
    acct = mdpbank.Bank(current.globalenv['db'])
    rsp = acct.get_account(avars)
    
    return rsp

def update_account(avars):
    logger.loggerpms2.info("Enter Update Account Request\n" + str(avars) )
    acct = mdpbank.Bank(current.globalenv['db'])
    rsp = acct.update_account(avars)
    return rsp

def delete_account(avars):
    logger.loggerpms2.info("Enter Delete Account Request\n" + str(avars) )
    acct = mdpbank.Bank(current.globalenv['db'])
    rsp = acct.delete_account(avars)
    return rsp

def new_account(avars):
    logger.loggerpms2.info("Enter New Account Request\n" + str(avars) )
    acct = mdpbank.Bank(current.globalenv['db'])
    rsp = acct.new_account(avars)
    return rsp

    
############################# ENDBank Detail Account API ###################################################

############################# START  DOCTOR API #################################################
def new_doctor(avars):
    logger.loggerpms2.info("Enter New Doctor Request\n" + str(avars) )
    doc = mdpdoctor.Doctor(current.globalenv['db'], common.getkeyvalue(avars,"providerid","0"))
    rsp = doc.new_doctor(avars)
    return rsp

def list_doctor(avars):
    logger.loggerpms2.info("Enter List Doctor Request\n" + str(avars) )
    doc = mdpdoctor.Doctor(current.globalenv['db'], common.getkeyvalue(avars,"providerid","0"))
    rsp = doc.list_doctor(avars)
    return rsp

def get_doctor(avars):
    logger.loggerpms2.info("Enter Get Doctor Request\n" + str(avars) )
    doc = mdpdoctor.Doctor(current.globalenv['db'], common.getkeyvalue(avars,"providerid","0"))
    rsp = doc.get_doctor(avars)
    return rsp

def update_doctor(avars):
    logger.loggerpms2.info("Enter Get Doctor Request\n" + str(avars) )
    doc = mdpdoctor.Doctor(current.globalenv['db'], common.getkeyvalue(avars,"providerid","0"))
    rsp = doc.update_doctor(avars)
    return rsp

def delete_doctor(avars):
    logger.loggerpms2.info("Enter Delete Doctor Request\n" + str(avars) )
    doc = mdpdoctor.Doctor(current.globalenv['db'], common.getkeyvalue(avars,"providerid","0"))
    rsp = doc.delete_doctor(avars)
    return rsp

############################# END DOCTOR API  ###################################################


############################# START  PROSPECT API #################################################
def new_prospect(avars):
    logger.loggerpms2.info("Enter New Prospect Request\n" + str(avars) )
    prs = mdpprospect.Prospect(current.globalenv['db'])
    rsp = prs.new_prospect(avars)
    return rsp

def list_prospect(avars):
    logger.loggerpms2.info("Enter List Prospect Request\n" + str(avars) )
    prs = mdpprospect.Prospect(current.globalenv['db'])
    rsp = prs.list_prospect(avars)
    return rsp

def get_prospect(avars):
    logger.loggerpms2.info("Enter Get Prospect Request\n" + str(avars) )
    prs = mdpprospect.Prospect(current.globalenv['db'])
    rsp = prs.get_prospect(avars)
    return rsp

def update_prospect(avars):
    logger.loggerpms2.info("Enter Get Prospect Request\n" + str(avars) )
    prs = mdpprospect.Prospect(current.globalenv['db'])
    rsp = prs.update_prospect(avars)
    return rsp

def delete_propsect(avars):
    logger.loggerpms2.info("Enter Delete Prospect Request\n" + str(avars) )
    prs = mdpprospect.Prospect(current.globalenv['db'])
    rsp = prs.delete_prospect(avars)
    return rsp

def approve_prospect(avars):
    logger.loggerpms2.info("Enter Approve Prospect Request\n" + str(avars) )
    prs = mdpprospect.Prospect(current.globalenv['db'])
    rsp = prs.approve_prospect(avars)
    return rsp

def enroll_prospect(avars):
    logger.loggerpms2.info("Enter Approve Prospect Request\n" + str(avars) )
    prs = mdpprospect.Prospect(current.globalenv['db'])
    rsp = prs.enroll_prospect(avars)
    return rsp

############################# END DPROSPECT API  ###################################################



############################# START AGENT API #################################################
def new_agent(avars):
    logger.loggerpms2.info("Enter New Agent Prospect Request\n" + str(avars) )
    obj = mdpagent.Agent(current.globalenv['db'])  
    rsp = obj.new_agent(avars)
    return rsp

def new_agent_prospect(avars):
    logger.loggerpms2.info("Enter New Agent Prospect Request\n" + str(avars) )
    obj = mdpagent.Agent(current.globalenv['db'])  
    rsp = obj.new_agent_prospect(avars)
    return rsp
############################# END AGENT API  ###################################################

def unknown(avars):
    return dict()



mediaAPI_switcher = {
    
    "upload_mediafile":upload_mediafile,"upload_media":upload_media,"downloadmedia":downloadmedia,\
    "getmedia_list":getmedia_list,"updatemedia":updatemedia,"deletemedia":deletemedia
}

opsTimingAPI_switcher = {
    
    "get_ops_timing":get_ops_timing,"update_ops_timing":update_ops_timing,"delete_ops_timng":delete_ops_timng,\
    "list_ops_timing":list_ops_timing,"new_ops_timing":new_ops_timing
}

accountAPI_switcher = {
    
    "get_account":get_account,"update_account":update_account,"delete_account":delete_account,"new_account":new_account
}

clinicAPI_switcher = {
    
    "get_clinic":get_clinic,"update_clinic":update_clinic,"delete_clinic":delete_clinic,\
    "new_clinic":new_clinic,"list_clinic":list_clinic,"add_doc_clinic":add_doc_clinic,"list_doc_clinic":list_doc_clinic,"remove_doc_clinic":remove_doc_clinic
}

doctorAPI_switcher = {
    "new_doctor":new_doctor,"list_doctor":list_doctor,"get_doctor":get_doctor,"update_doctor":update_doctor,"delete_doctor":delete_doctor
}

prospectAPI_switcher = {
    "new_prospect":new_prospect,"list_prospect":list_prospect,"get_prospect":get_prospect,"update_prospect":update_prospect,"delete_propsect":delete_propsect,\
    "approve_prospect":approve_prospect, "enroll_prospect":enroll_prospect
}

appointmentAPI_switcher = {
    "new_appointment":new_appointment,"get_appointment":get_appointment,"list_appointment":list_appointment,"update_appointment":update_appointment,
    "cancel_appointment":cancel_appointment,"add_block":add_block_datetime,"remove_block":remove_block_datetime,"list_block":list_block_datetime,
    "get_block":get_block_datetime,"list_day_appointment_count":list_day_appointment_count,"checkIn_appointment":checkIn,"checkOut_appointment":checkOut,"confirm_appointment":confirm,
    "reSchedule_appointment":reSchedule,"list_appointments_byday":list_appointments_byday,"list_appointmentstatus":appointmentstatus,"list_appointmentduration":appointmentduration
}

agentAPI_switcher = {

    "new_agent":new_agent,"new_agent_prospect":new_agent_prospect
}

userAPI_switcher = {
    
    "otp_login":otp_login, "agent_otp_login":agent_otp_login

}

mdpapi_switcher = {"listappointments":getappointments,"getappointmentsbymonth":getappointmentsbymonth,"getappointmentsbyday":getappointmentsbyday,"getappointment":getappointment,\
                   "getappointmentcountbymonth":getappointmentcountbymonth,"getdocappointmentcountbymonth":getdocappointmentcountbymonth,"getappointmentsbypatient":getappointmentsbypatient,\
                   "getpatappointmentcountbymonth":getpatappointmentcountbymonth,"getpatappointmentsbyday":getpatappointmentsbyday,\
                   "createappointment":newappointment,'updateappointment':updateappointment,'cancelappointment':cancelappointment,'checkinappointment':checkinappointment,\
                   "login":mdplogin,"logout":mdplogout,"forgotusername":forgotusername,"forgotpassword":forgotpassword,"getmailserverdetails":getmailserverdetails,\
                   "resetpassword":resetpassword,"searchpatient":searchpatient,"newpatient":newpatient,"getpatient":getpatient,"newalkinpatient":newalkinpatient,"updatewalkinpatient":updatewalkinpatient,\
                   "doctorlist":doctorlist,"doctor":getdoctor,"rolelist":rolelist,"specialitylist":specialitylist,"newpayment":newpayment,\
                   "listpayments":listpayments,"getpayment":getpayment,"paymentcallback":paymentcallback,"groupsmsmessage":groupsmsmessage,"paymentreceipt":paymentreceipt,\
                   "getpaymentlist":getpaymentlist, "getsignedkey":getsignedkey,"getopentreatments":getopentreatments,\
                   "gettreatments":gettreatments,"gettreatment":gettreatment, "newtreatment":newtreatment, "updatetreatment":updatetreatment,
                   "treatmentstatus":treatmentstatus,"getprocedures":getprocedures,"addproceduretotreatment":addproceduretotreatment,"gettreatmentprocedure":gettreatmentprocedure,\
                   "updatetreatmentprocedure":updatetreatmentprocedure,"completetreatmentprocedure":completetreatmentprocedure,"canceltreatmentprocedure":canceltreatmentprocedure,\
                   "gettreatmentprocedures":gettreatmentprocedures,"sendforauthorization":sendforauthorization,\
                   "getpatientnotes":getpatientnotes,"addpatientnotes":addpatientnotes,\
                   "uploadimage":uploadimage,"xuploadimage":xuploadimage,"downloadimage":downloadimage,"getimages":getimages,"deleteimage":deleteimage,"updateimage":updateimage,\
                   "genders":genders,"cities":cities,"states":states,"regions":regions,"regionswithid":regionswithid,"status":status,"otpvalidation":otpvalidation,"appointmentstatus":appointmentstatus,\
                   "appointmentduration":appointmentduration,"pattitles":pattitles,"doctitles":doctitles, "getallconstants":getallconstants,\
                   "encrypt":encrypt,"decrypt":decrypt,"decrypts128":decrypts128,"encrypts128":encrypts128,"uploadDocument":uploadDocument,"sendOTP":sendOTP,"validateOTP":validateOTP,\
                   "uploadDocument":uploadDocument,"addProcedure":addProcedure,"getTransactionID":getTransactionID,"getReligarePatient":getReligarePatient,\
                   "addRlgProcedureToTreatment":addRlgProcedureToTreatment,"voidTransaction":voidTransaction,"settleTransaction":settleTransaction,\
                   "getreligareprocedures":getreligareprocedures,"updateReligarePatient":updateReligarePatient,"getMedicalHistory":getMedicalHistory,\
                   "updateMedicalHistory":updateMedicalHistory,"encrypt_login":encrypt_login,"encrypted_mdplogin":encrypted_mdplogin,"getMediAssistPatients":getMediAssistPatients,\
                   "decrypts":decrypts,"encrypt_json":encrypt_json,"getmedicines":getmedicines,"getmedicine":getmedicine,"updatemedicine":updatemedicine,\
                   "getprescriptions":getprescriptions,"getprescription":getprescription,"newprescription":newprescription,\
                   "updateprescription":updateprescription,"deleteprescription":deleteprescription,\
                   "member_registration":member_registration,"getwebmember":getwebmember,"updatewebmember":updatewebmember, "getplansbyregion":getplansbyregion,\
                   "getwebmemberdependants":getwebmemberdependants,"getwebmemberdependant":getwebmemberdependant,"provider_registration":provider_registration,\
                   "updatewebmemberdependant":updatewebmemberdependant,"relations":relations,"newwebmemberpremiumpayment":newwebmemberpremiumpayment,"newwebmemberprocesspayment":newwebmemberprocesspayment,\
                   "deletewebmemberdependant":deletewebmemberdependant,"deletewalkinpatient":deletewalkinpatient,\
                   "gethdfc_constants":gethdfc_constants,"gethdfc_rsakey":gethdfc_rsakey,\
                   "getrazorpay_constants":getrazorpay_constants,"create_razorpay_order":create_razorpay_order,"capture_razorpay_payment":capture_razorpay_payment,\
                   "createcasereport":createcasereport,"get_casereport_list":get_casereport_list,"getcasereport":getcasereport,"updatecasereport":updatecasereport,\
                   "getdentalchart":getdentalchart,"gettoothcolours":gettoothcolours,"getchartprocedures":getchartprocedures,"getalltoothcolours":getalltoothcolours,\
                   "newpreregister":newpreregister,"getpreregister":getpreregister,"get_preregister_list":get_preregister_list,"updatepreregister":updatepreregister,"deletepreregister":deletepreregister,\
                   "uploadphoto":uploadphoto,"downloadphoto":downloadphoto,"getpreregisterimages":getpreregisterimages,"getpreregisterimage":getpreregisterimage,\
                   "uploadpreregisterimage":uploadpreregisterimage,"newpreregisterimage":newpreregisterimage,"updatepreregisterimage":updatepreregisterimage,"deletephoto":deletephoto,\
                   "addmediclaim":addmediclaim,"getmediclaim":getmediclaim,"updatemediclaim":updatemediclaim,"deletemediclaim":deletemediclaim,\
                   "addmediclaimcharts":addmediclaimcharts,"updatemediclaimcharts":updatemediclaimcharts,"deletemediclaimcharts":deletemediclaimcharts,"getmediclaimcharts":getmediclaimcharts,\
                   "addmediclaimprocedure":addmediclaimprocedure,"updatemediclaimprocedure":updatemediclaimprocedure,"getmediclaimprocedure":getmediclaimprocedure,\
                   "getmediclaimprocedures":getmediclaimprocedures,"deletemediclaimprocedure":deletemediclaimprocedure,"getmediclaims":getmediclaims,
                   "uploadmediclaimsignature":uploadmediclaimsignature,"downloadmediclaimsignature":downloadmediclaimsignature,"deletemediclaimsignature":deletemediclaimsignature,\
                   "addmediclaimattachment":addmediclaimattachment,"getmediclaimattachments":getmediclaimattachments,"deletemediclaimattachment":deletemediclaimattachment,\
                   "getdistance":getdistance,"getproviderswithinradius":getproviderswithinradius,"getproviderswithpincode":getproviderswithpincode,\
                   "task":task,"createwebmember_razorpay_order":createwebmember_razorpay_order,"capturewebmember_razorpay_payment":capturewebmember_razorpay_payment,\
                   "printpremium_payment_receipt":printpremium_payment_receipt,"updatememberprovider":updatememberprovider,"getprovider":getprovider,\
                   "validaterlgmember399":validaterlgmember399,"getreligarepatient399":getreligarepatient399,"updatereligarepatient399":updatereligarepatient399,\
                   "getreligareprocedures399":getreligareprocedures399,"addRlgProcedureToTreatment399":addRlgProcedureToTreatment399,\
                   "sendOTPXXX":sendOTPXXX,"validateOTPXXX":validateOTPXXX,"uploadDocumentXXX":uploadDocumentXXX,"getreligarepatientXXX":getreligarepatientXXX,\
                   "updatereligarepatientXXX":updatereligarepatientXXX,"getreligareproceduresXXX":getreligareproceduresXXX,"getTransactionIDXXX":getTransactionIDXXX,\
                   "addRlgProcedureToTreatmentXXX":addRlgProcedureToTreatmentXXX,"settleTransactionXXX":settleTransactionXXX,"voidTransactionXXX":voidTransactionXXX,\
                   "dental_service_request":dental_service_request,"get_appointments":get_appointments,"get_treatments":get_treatments,\
                   "getcompanyprocedures":getcompanyprocedures,"getnoncompanyprocedures":getnoncompanyprocedures,\
                   "addABHICLProcedureToTreatment":addABHICLProcedureToTreatment,\
                  
                   "register_vital_member":register_vital_member,"cancel_vital_member":cancel_vital_member,"enroll_vital_member":enroll_vital_member,\
                   "set_appointment_vital_member":set_appointment_vital_member,\
                   "sendOTPCashless":sendOTPCashless,"validateOTPCashless":validateOTPCashless,\
                   "getOPDServicesCashless":getOPDServicesCashless,"getTransactionIDCashless":getTransactionIDCashless,\
                   "agent_otp_login":agent_otp_login,"otp_login":otp_login
                   
                   }


@request.restful()
def mdpapi():

   
    response.view = 'generic' + request.extension
    def GET(*args, **vars):
	
        return

    def POST(*args, **vars):
	i = 0
        try:
	    #logger.loggerpms2.info(">>Enter API==>>")
	    db = current.globalenv['db']
	    props = db(db.urlproperties.id > 0).select(db.urlproperties.encryption)
	    #encryption = False if(len(props) == 0) else common.getboolean(props[0].encryption)
	    orlgr = mdpreligare.Religare(current.globalenv['db'],0)
	    #logger.loggerpms2.info(">>API==>>1")
            
            
            encryption = vars.has_key("req_data")
	   
	    
	    if(encryption):
		#logger.loggerpms2.info(">>API==>>2")
		
		encrypt_req = vars["req_data"]
		#logger.loggerpms2.info(">>API==>>3")
		
		vars = json.loads(orlgr.decrypts(vars["req_data"]))
		#logger.loggerpms2.info(">>API==>>4")
		
	    #logger.loggerpms2.info(">>API==>>5")
		
	    action = str(vars["action"])
	    #logger.loggerpms2.info(">>API ACTION==>>" + action)
	    #logger.loggerpms2.info(">>API ACTION==>>" + action)
	    if(action == 'getreligareprocedures'):
		logger.loggerpms2.info(">>Get Religare Procedures\n")
		logger.loggerpms2.info("===Req_data=\n" + encrypt_req)
		logger.loggerpms2.info("===Req_data=\n" + json.dumps(vars))
	    
	    #return json.dumps({"action":action})
            rsp = mdpapi_switcher.get(action,unknown)(vars)
	    common.setcookies(response)
	    if(encryption):
		return json.dumps({"resp_data":orlgr.encrypts(rsp)})
	    else:
		return rsp
	    
        except Exception as e:
	    #logger.loggerpms2.info("API Exception Error =>>\n")
	    #logger.loggerpms2.info(str(e))
            raise HTTP(500)   

    def PUT(*args, **vars):
        return dict()

    def DELETE(*args, **vars):
        return dict()

    return locals()



@request.restful()
def mediaAPI():
    response.view = 'generic' + request.extension
    def GET(*args, **vars):
	
	return

    def POST(*args, **vars):
	i = 0
	try:
	    #logger.loggerpms2.info(">>Enter MEDIA API==>>")
	    dsobj = datasecurity.DataSecurity()
	    
	    
	    encryption = vars.has_key("req_data")
	    if(encryption):
		#logger.loggerpms2.info(">>MEIDA API with Encryption")
		encrypt_req = vars["req_data"]
		vars = json.loads(dsobj.decrypts(encrypt_req))
	    
	    #decrypted request date
	    action = str(vars["action"])
	    #logger.loggerpms2.info(">>MEDIA API ACTION==>>" + action)
	    
	    
	    #return json.dumps({"action":action})
	    rsp = mediaAPI_switcher.get(action,unknown)(vars)
	    common.setcookies(response)
	    if(encryption):
		return json.dumps({"resp_data":dsobj.encrypts(rsp)})
	    else:
		return rsp
	    
	except Exception as e:
	    mssg = "MEDIA API Exception Error =>>\n" + str(e)
	    #logger.loggerpms2.info(mssg)
	    raise HTTP(500)   

    def PUT(*args, **vars):
	return dict()

    def DELETE(*args, **vars):
	return dict()

    return locals()


@request.restful()
def opsTimingAPI():
    response.view = 'generic' + request.extension
    def GET(*args, **vars):
	
	return

    def POST(*args, **vars):
	i = 0
	try:
	    #logger.loggerpms2.info(">>Enter OPS Timing API==>>")
	    dsobj = datasecurity.DataSecurity()
	    
	    
	    encryption = vars.has_key("req_data")
	    if(encryption):
		#logger.loggerpms2.info(">>OPS Timing with Encryption")
		encrypt_req = vars["req_data"]
		vars = json.loads(dsobj.decrypts(encrypt_req))
	    
	    #decrypted request date
	    action = str(vars["action"])
	    #logger.loggerpms2.info(">>OPS Timing ACTION==>>" + action)
	    
	    
	    #return json.dumps({"action":action})
	    rsp = opsTimingAPI_switcher.get(action,unknown)(vars)
	    common.setcookies(response)
	    if(encryption):
		return json.dumps({"resp_data":dsobj.encrypts(rsp)})
	    else:
		return rsp
	    
	except Exception as e:
	    mssg = "OPS Timing Exception Error =>>\n" + str(e)
	    #logger.loggerpms2.info(mssg)
	    raise HTTP(500)   

    def PUT(*args, **vars):
	return dict()

    def DELETE(*args, **vars):
	return dict()

    return locals()


@request.restful()
def accountAPI():
    response.view = 'generic' + request.extension
    def GET(*args, **vars):
	
	return

    def POST(*args, **vars):
	i = 0
	try:
	    #logger.loggerpms2.info(">>Enter Account API==>>")
	    dsobj = datasecurity.DataSecurity()
	    
	    
	    encryption = vars.has_key("req_data")
	    if(encryption):
		#logger.loggerpms2.info(">>Account with Encryption")
		encrypt_req = vars["req_data"]
		vars = json.loads(dsobj.decrypts(encrypt_req))
	    
	    #decrypted request date
	    action = str(vars["action"])
	    #logger.loggerpms2.info(">>Account ACTION==>>" + action)
	    
	    
	    #return json.dumps({"action":action})
	    rsp = accountAPI_switcher.get(action,unknown)(vars)
	    common.setcookies(response)
	    if(encryption):
		return json.dumps({"resp_data":dsobj.encrypts(rsp)})
	    else:
		return rsp
	    
	except Exception as e:
	    mssg = "OPS Timing Exception Error =>>\n" + str(e)
	    #logger.loggerpms2.info(mssg)
	    raise HTTP(500)   

    def PUT(*args, **vars):
	return dict()

    def DELETE(*args, **vars):
	return dict()

    return locals()

@request.restful()
def clinicAPI():
    response.view = 'generic' + request.extension
    def GET(*args, **vars):
	return

    def POST(*args, **vars):
	i = 0
	try:
	    #logger.loggerpms2.info(">>Enter Account API==>>")
	    dsobj = datasecurity.DataSecurity()
	    encryption = vars.has_key("req_data")
	    if(encryption):
		#logger.loggerpms2.info(">>Account with Encryption")
		encrypt_req = vars["req_data"]
		vars = json.loads(dsobj.decrypts(encrypt_req))
	    
	    #decrypted request date
	    action = str(vars["action"])
	    #logger.loggerpms2.info(">>Account ACTION==>>" + action)
	    
	    #return json.dumps({"action":action})
	    rsp = clinicAPI_switcher.get(action,unknown)(vars)
	    common.setcookies(response)
	    if(encryption):
		return json.dumps({"resp_data":dsobj.encrypts(rsp)})
	    else:
		return rsp
	    
	except Exception as e:
	    mssg = "Clinic API Exception Error =>>\n" + str(e)
	    #logger.loggerpms2.info(mssg)
	    raise HTTP(500)   

    def PUT(*args, **vars):
	return dict()

    def DELETE(*args, **vars):
	return dict()

    return locals()

@request.restful()
def doctorAPI():
    response.view = 'generic' + request.extension
    def GET(*args, **vars):
	return

    def POST(*args, **vars):
	i = 0
	try:
	    #logger.loggerpms2.info(">>Enter Doctor API==>>")
	    dsobj = datasecurity.DataSecurity()
	    encryption = vars.has_key("req_data")
	    if(encryption):
		#logger.loggerpms2.info(">>Doctor with Encryption")
		encrypt_req = vars["req_data"]
		vars = json.loads(dsobj.decrypts(encrypt_req))
	    
	    #decrypted request date
	    action = str(vars["action"])
	    #logger.loggerpms2.info(">>Doctor ACTION==>>" + action)
	    
	    #return json.dumps({"action":action})
	    rsp = doctorAPI_switcher.get(action,unknown)(vars)
	    common.setcookies(response)
	    if(encryption):
		return json.dumps({"resp_data":dsobj.encrypts(rsp)})
	    else:
		return rsp
	    
	except Exception as e:
	    mssg = "Clinic API Exception Error =>>\n" + str(e)
	    #logger.loggerpms2.info(mssg)
	    raise HTTP(500)   

    def PUT(*args, **vars):
	return dict()

    def DELETE(*args, **vars):
	return dict()

    return locals()

@request.restful()
def prospectAPI():
    response.view = 'generic' + request.extension
    def GET(*args, **vars):
	return

    def POST(*args, **vars):
	i = 0
	try:
	    #logger.loggerpms2.info(">>Enter Prospect API==>>")
	    dsobj = datasecurity.DataSecurity()
	    encryption = vars.has_key("req_data")
	    if(encryption):
		#logger.loggerpms2.info(">>Prospedct with Encryption")
		encrypt_req = vars["req_data"]
		vars = json.loads(dsobj.decrypts(encrypt_req))
	    
	    #decrypted request date
	    action = str(vars["action"])
	    #logger.loggerpms2.info(">>Prospect ACTION==>>" + action)
	    
	    #return json.dumps({"action":action})
	    rsp = prospectAPI_switcher.get(action,unknown)(vars)
	    common.setcookies(response)
	    if(encryption):
		return json.dumps({"resp_data":dsobj.encrypts(rsp)})
	    else:
		return rsp
	    
	except Exception as e:
	    mssg = "Prospect API Exception Error =>>\n" + str(e)
	    #logger.loggerpms2.info(mssg)
	    raise HTTP(500)   

    def PUT(*args, **vars):
	return dict()

    def DELETE(*args, **vars):
	return dict()

    return locals()


@request.restful()
def agentAPI():
    response.view = 'generic' + request.extension
    def GET(*args, **vars):
	return

    def POST(*args, **vars):
	i = 0
	try:
	    #logger.loggerpms2.info(">>Enter Agent API==>>")
	    dsobj = datasecurity.DataSecurity()
	    encryption = vars.has_key("req_data")
	    if(encryption):
		#logger.loggerpms2.info(">>Agent with Encryption")
		encrypt_req = vars["req_data"]
		vars = json.loads(dsobj.decrypts(encrypt_req))
	    
	    #decrypted request date
	    action = str(vars["action"])
	    #logger.loggerpms2.info(">>Agent ACTION==>>" + action)
	    
	    #return json.dumps({"action":action})
	    rsp = agentAPI_switcher.get(action,unknown)(vars)
	    common.setcookies(response)
	    if(encryption):
		return json.dumps({"resp_data":dsobj.encrypts(rsp)})
	    else:
		return rsp
	    
	except Exception as e:
	    mssg = "AGENT API Exception Error =>>\n" + str(e)
	    #logger.loggerpms2.info(mssg)
	    raise HTTP(500)   

    def PUT(*args, **vars):
	return dict()

    def DELETE(*args, **vars):
	return dict()

    return locals()


@request.restful()
def appointmentAPI():
    response.view = 'generic' + request.extension
    def GET(*args, **vars):
	return

    def POST(*args, **vars):
	i = 0
	try:
	    #logger.loggerpms2.info(">>Enter Appointment API==>>")
	    dsobj = datasecurity.DataSecurity()
	    encryption = vars.has_key("req_data")
	    if(encryption):
		#logger.loggerpms2.info(">>Appointment with Encryption")
		encrypt_req = vars["req_data"]
		vars = json.loads(dsobj.decrypts(encrypt_req))
	    
	    #decrypted request date
	    action = str(vars["action"])
	    #logger.loggerpms2.info(">>Appointment ACTION==>>" + action)
	    
	    #return json.dumps({"action":action})
	    rsp = appointmentAPI_switcher.get(action,unknown)(vars)
	    common.setcookies(response)
	    if(encryption):
		return json.dumps({"resp_data":dsobj.encrypts(rsp)})
	    else:
		return rsp
	    
	except Exception as e:
	    mssg = "AGENT API Exception Error =>>\n" + str(e)
	    #logger.loggerpms2.info(mssg)
	    raise HTTP(500)   

    def PUT(*args, **vars):
	return dict()

    def DELETE(*args, **vars):
	return dict()

    return locals()

@request.restful()
def userAPI():
    response.view = 'generic' + request.extension
    def GET(*args, **vars):
	return

    def POST(*args, **vars):
	i = 0
	try:
	    #logger.loggerpms2.info(">>Enter Agent API==>>")
	    dsobj = datasecurity.DataSecurity()
	    encryption = vars.has_key("req_data")
	    if(encryption):
		#logger.loggerpms2.info(">>Agent with Encryption")
		encrypt_req = vars["req_data"]
		vars = json.loads(dsobj.decrypts(encrypt_req))
	    
	    #decrypted request date
	    action = str(vars["action"])
	    #logger.loggerpms2.info(">>Agent ACTION==>>" + action)
	    
	    #return json.dumps({"action":action})
	    rsp = userAPI_switcher.get(action,unknown)(vars)
	    common.setcookies(response)
	    if(encryption):
		return json.dumps({"resp_data":dsobj.encrypts(rsp)})
	    else:
		return rsp
	    
	except Exception as e:
	    mssg = "AGENT API Exception Error =>>\n" + str(e)
	    #logger.loggerpms2.info(mssg)
	    raise HTTP(500)   

    def PUT(*args, **vars):
	return dict()

    def DELETE(*args, **vars):
	return dict()

    return locals()


