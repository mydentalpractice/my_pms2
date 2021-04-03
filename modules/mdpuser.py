# -*- coding: utf-8 -*-
from gluon import current
CRYPT = current.globalenv["CRYPT"]

import datetime
import time

import os;
import uuid
from uuid import uuid4

import json
from applications.my_pms2.modules import common
from applications.my_pms2.modules import status
from applications.my_pms2.modules import cycle
from applications.my_pms2.modules import gender
from applications.my_pms2.modules import relations
from applications.my_pms2.modules import mail


from applications.my_pms2.modules import mdpprospect
from applications.my_pms2.modules import mdpprovider
from applications.my_pms2.modules import mdpagent
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import logger



class User:
  def __init__(self,db,auth,username,password):
    logger.loggerpms2.info("Enter User __init__")
    self.db = db
    self.auth = auth
    self.username  = username
    self.password = password
    return 
  
  
  def getmailserverdetails(self):
     
    db = self.db
    
    
    try:
      
      urlprops = db((db.urlproperties.id > 0) & (db.urlproperties.is_active == True)).\
        select(db.urlproperties.mailsender,db.urlproperties.mailserver, db.urlproperties.mailserverport,\
               db.urlproperties.mailusername, db.urlproperties.mailpassword)
      if(len(urlprops) == 1):
        return json.dumps({"result":"success","error_message":"", "mailserver":urlprops[0].mailserver,"mailserverport":urlprops[0].mailserverport,\
                           "mailurl":urlprops[0].mailsender, "mailusername":urlprops[0].mailusername, "mailpassword":urlprops[0].mailpassword})
      else:
        return json.dumps({"result":"fail","error_message":"Error: Invalide Sender Email Details"})
      
    except Exception as e:
        error_message = "Request Mail Sender Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return  

  def member_registration_validation(self,email, cell, username):
     
    db = self.db

    
    try:
      error_message = ""
  
      r = db((db.auth_user.email == email)).count()
      if((r >= 1) | (email == "")):
        error_message = error_message + "This email " + email + " is already registered or empty. Please enter valid email\n"

      r = db(db.auth_user.username == username).count()
      if((r >= 1) | (username == "")):
        error_message = error_message + "This username " + username + " is already registered or empty. Please enter valid username!\n"

      r = db(db.auth_user.cell == cell).count()
      if((r >= 1) | (cell == "")):
        error_message = error_message + "This mobile number " + cell + " is already registered. Please enter valid cell!\n"
      
      obj = {}
      if(error_message == ""):
        obj = {
          "result":"sucess",
          "error_message":error_message
        }
      else:
        obj = {
          "result":"fail",
          "error_message":error_message
        }
        
      return obj
        

        
    except Exception as e:
        error_message = "Add Mediclaim Procedures Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return

  def agent_otp_login(self,avars):
    
    auth = self.auth
    db = self.db
    
    logger.loggerpms2.info(">>AGENT LOGIN API\n")
    logger.loggerpms2.info("===Req_data=\n" + self.username + " " + self.password + "\n")
    

    user_data = {}
    
    
    try:
      cell = common.getkeyvalue(avars,"cell","")
      usr = db(db.auth_user.cell == cell).select()
      
      if(len(usr) != 1):
        error_message = "OTP Login API Error: No User/Multiple users matching registered " + cell
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    

      user = auth.login_user(db.auth_user(int(usr[0].id)))
      cell = auth.user["cell"]
      r = db(db.agent.cell == cell).select()
      if(len(r) != 1):
        error_message = "Agent Login API Error: No Agent/Multiple agent matching registered " + cell
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj) 
      
      
      user_data = {}
      user_data={
        "result":"success",
        "error_message":"",
        "usertype":"agent", 
        "agent":r[0].agent,
        "agentid":common.getid(r[0].id),
        "name":r[0].name,
        "cell":r[0].cell,
        "email":r[0].email
      }
      
    except Exception as e:
        error_message = "AGENT Login Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
  
  
    return json.dumps(user_data)

  def user_otp_login(self,avars):
      
      auth = self.auth
      db = self.db
      
      logger.loggerpms2.info(">>User LOGIN API\n")
      logger.loggerpms2.info("===Req_data=\n" + self.username + " " + self.password + "\n")
      
  
      user_data = {}
      
      
      try:
        cell = common.getkeyvalue(avars,"cell","")
        usr = db(db.auth_user.cell == cell).select()
        
        if(len(usr) != 1):
          error_message = "User OTP Login API Error: No User/Multiple users matching registered " + cell
          logger.loggerpms2.info(error_message)
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = error_message
          return json.dumps(excpobj)    
  
        auth.login_user(db.auth_user(int(usr[0].id)))
        cell = auth.user["cell"]
        user_data = {}
        #IF THE user cell is in provider then the user is a provider
        p = db((db.provider.cell == cell) & (db.provider.is_active == True)).select()
        if(len(p) >= 1):
          #if cell is in provider then otp is for provider
          obj = mdpprovider.Provider(db,int(p[0].id))
          user_data = json.loads(obj.getprovider())
          user_data["usertype"] = "provider"
          user_data["result"] = "success"
          user_data["error_message"] = ""
          user_data["error_code"] = ""
        else:
          #if the user cell is in Patient Member, then return as a patient
          pat = db((db.vw_memberpatientlist.cell == cell) & (db.vw_memberpatientlist.is_active == True)).select()
          
          if(len(pat)!=0):
            if(len(pat) == 1):
              #user is a patientmemebr
              patobj = mdppatient.Patient(db, 0)
              user_data = patobj.getpatient(int(common.getid(pat[0].primarypatientid)), int(common.getid(pat[0].patientid)), "imageurl")
              user_data["usertype"] = "member"
            else:
              #multiple users with the same cell
              error_message = "OTP Login API Error: No User/Multiple Patient/Members matching registered " + cell
              logger.loggerpms2.info(error_message)
              excpobj = {}
              excpobj["result"] = "fail"
              excpobj["error_message"] = error_message
              return json.dumps(excpobj)    
              
          else:
            #check for new Signup (prospect)
            #if the user cell is in prospect table, then returning prospect
            p = db((db.prospect.cell == cell) & (db.prospect.status != "Enrolled") & (db.prospect.is_active == True)).select()
            if(len(p)>=1):   #returning signup
              obj = mdpprospect.Prospect(db)
              
              user_data = json.loads(obj.get_prospect({"prospectid":str(p[0].id)}))
              user_data["usertype"] = "prospect"
              user_data["result"] = "success"
              user_data["error_message"] = ""
              user_data["error_code"] = ""
            else:
              user_data["usertype"] = "prospect"
              user_data["prospectid"] = "0"
              user_data["result"] = "success"
              user_data["error_message"] = ""
              user_data["error_code"] = ""
              
        
        
        #user_data = {}
        #user_data={
          #"result":"success",
          #"error_message":"",
          #"usertype":"agent", 
          #"agent":r[0].agent,
          #"agentid":common.getid(r[0].id),
          #"name":r[0].name,
          #"cell":r[0].cell,
          #"email":r[0].email
        #}
        
      except Exception as e:
          error_message = "User Login Exception Error - " + str(e)
          logger.loggerpms2.info(error_message)
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = error_message
          return json.dumps(excpobj)    
    
    
      return json.dumps(user_data)
  
  #this method is called after OTP Validation:
  #cell is xxxxxxxxxx  (without leading +<countrycode)
  #assuming Cell is unique
  def otp_login(self,avars):
    
    logger.loggerpms2.info("Enter otp_login", json.dumps(avars))
    auth = self.auth
    db = self.db
   
    
    rspobj = {}
    
    try:
      cell = common.getkeyvalue(avars,"cell","")
      usr = db(db.auth_user.cell == cell).select()
    
      if(len(usr) > 1):
        error_message = "OTP Login API Error: Multiple users matching registered " + cell
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
      
      #auth.login_user(db.auth_user(int(usr[0].id)))
      #cell = auth.user["cell"]
      user_data = {}
      #IF THE user cell is in provider then the user is a provider
      p = db((db.provider.cell == cell) & (db.provider.is_active == True)).select()
      if(len(p) >= 1):
        #if cell is in provider then otp is for provider
        obj = mdpprovider.Provider(db,int(p[0].id))
        user_data = json.loads(obj.getprovider())
        user_data["usertype"] = "provider"
        user_data["result"] = "success"
        user_data["error_message"] = ""
        user_data["error_code"] = ""
      else:
        #if the user cell is in Patient Member, then return as a patient
        pat = db((db.vw_memberpatientlist.cell == cell) & (db.vw_memberpatientlist.is_active == True)).select()
        
        if(len(pat)!=0):
          if(len(pat) == 1):
            #user is a patientmemebr
            patobj = mdppatient.Patient(db, 0)
            user_data = patobj.getpatient(int(common.getid(pat[0].primarypatientid)), int(common.getid(pat[0].patientid)), "imageurl")
            user_data["usertype"] = "member"
          else:
            #multiple users with the same cell
            error_message = "OTP Login API Error: No User/Multiple Patient/Members matching registered " + cell
            logger.loggerpms2.info(error_message)
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = error_message
            return json.dumps(excpobj)    
            
        else:
          #check for new Signup (prospect)
          #if the user cell is in prospect table, then returning prospect
          logger.loggerpms2.info("Enter Prospect Check with cell " + cell)
          p = db((db.prospect.cell == cell) & (db.prospect.status != "Enrolled") & (db.prospect.is_active == True)).select()
          if(len(p)>=1):   #returning signup
            logger.loggerpms2.info("Propsect present with " + cell)            
            obj = mdpprospect.Prospect(db)
            if(obj != None):
              logger.loggerpms2.info("Propsect after Prospect")  
            else:
              logger.loggerpms2.info("Propsect None") 
            
            user_data = json.loads(obj.get_prospect({"prospectid":str(p[0].id)}))
            logger.loggerpms2.info("After get_prospect")  
            user_data["usertype"] = "prospect"
            user_data["result"] = "success"
            user_data["error_message"] = ""
            user_data["error_code"] = ""
          else:
            
            # create new user
            users = db((db.auth_user.cell) == cell).select()
            if users:
              my_crypt = CRYPT(key=auth.settings.hmac_key)
              crypt_pass = my_crypt(cell)[0]  
              db(db.auth_user.id == users[0].id).update(username=cell,password=crypt_pass)
              db.commit()
              user_data["usertype"] = "prospect"
              user_data["prospectid"] = "0"
              user_data["result"] = "success"
              user_data["error_message"] = ""
              user_data["error_code"] = ""              
            else:
              my_crypt = CRYPT(key=auth.settings.hmac_key)
              crypt_pass = my_crypt(cell)[0]        
              id_user= db.auth_user.insert(
                                         cell = cell,
                                         username = cell,
                                         password = crypt_pass 
                                         )
              db.commit()      
                        
      
              user_data["usertype"] = "prospect"
              user_data["prospectid"] = "0"
              user_data["result"] = "success"
              user_data["error_message"] = ""
              user_data["error_code"] = ""
    
          
      
    except Exception as e:
        error_message = "OTP Login Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
  
  
    return json.dumps(user_data)

  
  #Authenticate the user returning JSON data
  #If successful, return authenticate user data, provider data(if user is provider), web admin data (if user is admin), patient data (if user is patient - member or walkin)
  def login(self,username,password):
    auth = self.auth
    db = self.db
    
    logger.loggerpms2.info(">>LOGIN API\n")
    logger.loggerpms2.info("===Req_data=\n" + username + " " + password + "\n")
    user_data = {}
    try:
      
      
      user = auth.login_bare(str(username), str(password))
 
      #logger.loggerpms2.info(">>After user")
      
     
      
      if(user==False):
        user_data ={
          "result" : "fail",
          "error_message":"Login Failure. Please re-enter correct your username and password"
        }
  
      else:
          #logger.loggerpms2.info(">>User is True")
          auth.user.impersonated = False
          auth.user.impersonatorid = 0        
          
          provdict = common.getprovider(auth, db)
          #logger.loggerpms2.info(">>After Provider Dict")
          
          if(int(provdict["providerid"]) == 0):
              
              #webadmin
              user_data ={
                "result" : 'success',
                "error_message":"",
                "usertype":"webadmin",
                "providerid":int(provdict["providerid"]),
                "providername":provdict["providername"],
              }
          
          elif(int(provdict["providerid"]) < 0):
            #webmember and/or patientmember
            webmems = db((db.webmember.webkey == auth.user.sitekey) & (db.webmember.cell == auth.user.cell) &\
                         (db.webmember.email == auth.user.email)).select()
            if(len(webmems) == 1):
              user_data = {
                "result" : "success",
                "error_message":"",
                "usertype":"webmember",
                "providerid":int(common.getid(webmems[0].provider)),
                "webmemberid":int(common.getid(webmems[0].id)),
                "memberid":0,
                "status":webmems[0].status,
                "cell":webmems[0].cell,
                "email":webmems[0].email,
                "sitekey":webmems[0].webkey,
              }
            else:
              user_data ={
                "result" : "fail",
                "error_message":"Login Failure. Invalid Web Member"
              }
            
            mems = db((db.patientmember.webkey == auth.user.sitekey) & (db.patientmember.cell == auth.user.cell) &\
                         (db.patientmember.email == auth.user.email)).select()
            #logger.loggerpms2.info(">>After mems")
            
            if(len(mems) == 1):
              #logger.loggerpms2.info(">>Mems = 1")
              user_data = {
                "result" : "success",
                "error_message":"",
                "usertype":"member",
                "providerid":int(common.getid(mems[0].provider)),
                "webmemberid":int(common.getid(mems[0].webmember)),
                "memberid":int(common.getid(mems[0].id)),
                "status":mems[0].status,
                "cell":mems[0].cell,
                "email":mems[0].email,
                "sitekey":mems[0].webkey,
              }
            elif(len(mems) > 1):
              user_data ={
                "result" : "fail",
                "error_message":"Login Failure. Invalid Patient Member"
              }         
          else:
              #logger.loggerpms2.info(">>Provider Else")
              
              #provider
              providerid = int(provdict["providerid"])
              
              rlgprov = db((db.rlgprovider.providerid == providerid) & (db.rlgprovider.is_active == True)).select()
              urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.relgrpolicynumber)
              user_data ={
                "result" : "success",
                "error_message":"",
                "usertype":"provider",
                "webmemberid":0,
                "memberid":0,
                "providerid":providerid,
                "provider":provdict["provider"],
                "providername":provdict["providername"],
                "practicename":provdict["practicename"],
                "practiceaddress":provdict["practiceaddress"],
                "cell":provdict["cell"],
                "email":provdict["email"],
                "registration":provdict["registration"],
                "rlgprovider": False if(len(rlgprov) == 0) else True,
                "rlgrpolicynumber": "" if(len(urlprops) == 0) else common.getstring(urlprops[0].relgrpolicynumber),
                "regionid": 0 if(len(rlgprov) == 0) else int(rlgprov[0].regionid),
                "planid": 0 if(len(rlgprov) == 0) else int(rlgprov[0].planid)
              
              }
      logger.loggerpms2.info(">>LOGIN API\n")
      logger.loggerpms2.info("===Rsp_data=\n" + json.dumps(user_data) + "\n")
    except Exception as e:
      error_message = "Login Exception Error - " + str(e)
      logger.loggerpms2.info(error_message)
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = error_message
      return json.dumps(excpobj)                
    
    return json.dumps(user_data)
  
  def ylogin(self,username,password):
    auth = self.auth
    db = self.db
    
    logger.loggerpms2.info(">>LOGIN API\n")
    logger.loggerpms2.info("===Req_data=\n" + username + " " + password + "\n")
    user_data = {}
    try:
     
      my_crypt = CRYPT(key=auth.settings.hmac_key)
    
      crypt_pass = my_crypt(password)[0]  
      crypt_password = crypt_pass.password
      cell = None
      if(password == crypt_password):
        r = db((db.auth_user.username == username)).select()
        if(len(r)==1):
          cell = r[0].cell
    
      if(cell == None):
        error_message = "Login API Error: No User "
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)
      
      
      usr = db((db.auth_user.username == username) & (db.auth_user.cell == cell)).select()
      
      if(len(usr) != 1):
        error_message = "Login API Error: No User/Multiple users matching registered " + cell
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    
      user = auth.login_user(db.auth_user(int(usr[0].id)))
      user = auth.user
      user = auth.login_bare(str(username), str(password))
      logger.loggerpms2.info(">>After user")
      
     
      
      if(user==False):
        user_data ={
          "result" : "fail",
          "error_message":"Login Failure. Please re-enter correct your username and password"
        }
    
      else:
          logger.loggerpms2.info(">>User is True")
          auth.user.impersonated = False
          auth.user.impersonatorid = 0        
          
          provdict = common.getprovider(auth, db)
          logger.loggerpms2.info(">>After Provider Dict")
          
          if(int(provdict["providerid"]) == 0):
              
              #webadmin
              user_data ={
                "result" : 'success',
                "error_message":"",
                "usertype":"webadmin",
                "providerid":int(provdict["providerid"]),
                "providername":provdict["providername"],
              }
          
          elif(int(provdict["providerid"]) < 0):
            #webmember and/or patientmember
            webmems = db((db.webmember.webkey == auth.user.sitekey) & (db.webmember.cell == auth.user.cell) &\
                         (db.webmember.email == auth.user.email)).select()
            if(len(webmems) == 1):
              user_data = {
                "result" : "success",
                "error_message":"",
                "usertype":"webmember",
                "providerid":int(common.getid(webmems[0].provider)),
                "webmemberid":int(common.getid(webmems[0].id)),
                "memberid":0,
                "status":webmems[0].status,
                "cell":webmems[0].cell,
                "email":webmems[0].email,
                "sitekey":webmems[0].webkey,
              }
            else:
              user_data ={
                "result" : "fail",
                "error_message":"Login Failure. Invalid Web Member"
              }
            
            mems = db((db.patientmember.webkey == auth.user.sitekey) & (db.patientmember.cell == auth.user.cell) &\
                         (db.patientmember.email == auth.user.email)).select()
            logger.loggerpms2.info(">>After mems")
            
            if(len(mems) == 1):
              logger.loggerpms2.info(">>Mems = 1")
              user_data = {
                "result" : "success",
                "error_message":"",
                "usertype":"member",
                "providerid":int(common.getid(mems[0].provider)),
                "webmemberid":int(common.getid(mems[0].webmember)),
                "memberid":int(common.getid(mems[0].id)),
                "status":mems[0].status,
                "cell":mems[0].cell,
                "email":mems[0].email,
                "sitekey":mems[0].webkey,
              }
            elif(len(mems) > 1):
              user_data ={
                "result" : "fail",
                "error_message":"Login Failure. Invalid Patient Member"
              }         
          else:
              logger.loggerpms2.info(">>Provider Else")
              
              #provider
              providerid = int(provdict["providerid"])
              
              rlgprov = db((db.rlgprovider.providerid == providerid) & (db.rlgprovider.is_active == True)).select()
              urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.relgrpolicynumber)
              user_data ={
                "result" : "success",
                "error_message":"",
                "usertype":"provider",
                "webmemberid":0,
                "memberid":0,
                "providerid":providerid,
                "provider":provdict["provider"],
                "providername":provdict["providername"],
                "practicename":provdict["practicename"],
                "practiceaddress":provdict["practiceaddress"],
                "cell":provdict["cell"],
                "email":provdict["email"],
                "registration":provdict["registration"],
                "rlgprovider": False if(len(rlgprov) == 0) else True,
                "rlgrpolicynumber": "" if(len(urlprops) == 0) else common.getstring(urlprops[0].relgrpolicynumber),
                "regionid": 0 if(len(rlgprov) == 0) else int(rlgprov[0].regionid),
                "planid": 0 if(len(rlgprov) == 0) else int(rlgprov[0].planid)
              
              }
      logger.loggerpms2.info(">>LOGIN API\n")
      logger.loggerpms2.info("===Rsp_data=\n" + json.dumps(user_data) + "\n")
    except Exception as e:
      error_message = "Login Exception Error - " + str(e)
      logger.loggerpms2.info(error_message)
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = error_message
      return json.dumps(excpobj)                
    
    return json.dumps(user_data)  
  
  def logout(self):
    auth = self.auth
    auth.settings.logout_next = None
    auth.logout()
    
    data = {"logout":"Logout Success"}
    
    return json.dumps(data)  
  

  def request_username(self,email):
    
    
    db = self.db
    
    ds = db(db.auth_user.email == email).select(db.auth_user.username,db.auth_user.cell)

    user_data = None
    
    if(len(ds) == 0):
      user_data = {"result":False, "message":"Invalid Email"}
    elif (len(ds) > 1):
      user_data = {"result":False, "message":"More than one user has this email"}
    else:
      user_data = {"result":True, "username":ds[0].username, "cell":ds[0].cell}
      
    
    return json.dumps(user_data)
  
  
 

  def request_resetpassword(self,email):

    db = self.db
    ds = db((db.auth_user.email == email) & (db.auth_user.username == self.username)).select(db.auth_user.id,db.auth_user.cell)
    user_data = None
       
    if(len(ds) == 0):
      user_data = {"result":False, "message":"Invalid Email-Username"}
    elif (len(ds) > 1):
      user_data = {"result":False, "message":"More than one user has this email"}
    else:
      reset_password_key=str(int(time.time()))+'-'+str(uuid.uuid4())
      userid = common.getid(ds[0].id)
      db(db.auth_user.id == userid).update(reset_password_key = reset_password_key)   
      user_data = {"result":True, "resetpasswordkey":reset_password_key,"cell":ds[0].cell}
    
    return json.dumps(user_data)

  
  
  def reset_password(self,email,resetpasswordkey,newpassword):
  
    db = self.db
    auth = self.auth
    
    ds = db((db.auth_user.username == self.username) & (db.auth_user.email == email) & (db.auth_user.reset_password_key == resetpasswordkey)).select(db.auth_user.id)
    
    if(len(ds) == 0):
      user_data = {"result":False, "message":"Invalid Email-Username-Passwordkey"}
    elif (len(ds) > 1):
      user_data = {"result":False, "message":"More than one user has this email"}
    else:
      userid = common.getid(ds[0].id)
      my_crypt = CRYPT(key=auth.settings.hmac_key)
      crypt_pass = my_crypt(newpassword)[0]        

      db(db.auth_user.id == userid).update(password=crypt_pass,reset_password_key='')
      
      user_data = {"result":True, "resetpasswordkey":resetpasswordkey}
    
    return json.dumps(user_data)

  #This method receives validated otp with cell number from mobile app
  #Search the patientmembers for registered cell number.  Ideally, there will be only 
  #one registered cell number, if more are found, then return with error
  #else return with member and dependant list or walk-in patient list
  def otpvalidation(self, cell, email, otp, otpdatetime):
    
    db = self.db   #there is no provider id at this stage
    
    cellno = common.modify_cell(cell)   #in standard with 91
    
    #search for the cell number in patientmember
    pats = db((db.vw_memberpatientlist.cell == cell)|(db.vw_memberpatientlist.cell == cellno)).select()   #compare with 91 or without 91
    
    patlist = []
    patobj  = {}
    message = "success"
    
    for pat in pats:
      patobj = {
        "member":common.getboolean(pat.hmopatientmember),  #False for walk in patient
        "patientmember" : pat.patientmember,
        "fname":pat.fname,
        "lname":pat.lname,
        "memberid":int(common.getid(pat.primarypatientid)),
        "patientid":int(common.getid(pat.patientid)),
        "primary":True if(pat.patienttype == "P") else False,   #True if "P" False if "D"
        "relation":pat.relation,
        "cell":pat.cell,
        "email":pat.email,
        "providerid":pat.providerid
        
        
      }
      patlist.append(patobj)   
      
      
      db.otplog.insert(\
        
        memberid = int(common.getid(pat.primarypatientid)),
        patientid = int(common.getid(pat.patientid)),
        cell = cell,
        email = email,
        otp = otp,
        otpdatetime = otpdatetime,
        is_active = True,
        created_by = 1,
        created_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1,
        modified_on = common.getISTFormatCurrentLocatTime()
      
      
      )
    message = "success" if(len(pats)>0) else "failure"
    return json.dumps({"patientcount":len(pats),"patientlist":patlist,"message":message,"result":message})
  
  #status.py
  #xSTATUS=('No_Attempt', 'Attempting','Completed','Enrolled', 'Revoked')
  #xALLSTATUS=('ALL', 'No_Attempt', 'Attempting','Completed','Enrolled', 'Revoked')
  #xTREATMENTPLANSTATUS=('Open', 'Sent for Authorization','Authorized','Completed','Cancelled')
  #xTREATMENTSTATUS=('Started', 'Sent for Authorization', 'Authorized', 'Completed','Cancelled')
  #xPRIORITY=('Emergency','High','Medium','Low')
  #xOFFICESTAFF=('Doctor','Staff')
  #xAPPTSTATUS=('Open','Confirmed','Checked-In', 'Checked-Out', 'Cancelled')
  #xCUSTACTIVITY=('Scheduled','Pending','Enrolled','Cancelled')  

  #gender.py
  #xGENDER=('Male','Female')
  #xPATTITLE = (' ', 'Mr.', 'Mrs.', 'Ms.', 'Miss')
  #xDOCTITLE = (' ','Dr.','Mr.','Mrs.', 'Ms.', 'Miss')
  
  #cycle.py
  #xDURATION=('30','45','60')
  
  
  #relations.py
  #xRELATIONS=('Self',Spouse', 'Son', 'Daughter', 'Son_in_Law', 'Daughter_in_Law', 'Father', 'Mother', 'Father_in_Law', 'Mother_in_Law','Grandmother','Grandfather','Sibling','Relative','Dependant')
  #PLANRELATIONS=('Self', 'Spouse', 'Son', 'Daughter', 'Son_in_Law', 'Daughter_in_Law', 'Father', 'Mother', 'Father_in_Law', 'Mother_in_Law','Grandmother','Grandfather','Sibling','Relative')
  #xPLANRDEPENDANTS=('Self', 'Dependant_1', 'Dependant_2', 'Dependant_3', 'Dependant_4', 'Dependant_5', 'Dependant_6', 'Dependant_7')  

  def getallconstants(self):
    
    #get appointment status
    apptsts = status.APPTSTATUS
    #patient status
    patsts = status.STATUS
    #treatment status
    treatment_status = status.TREATMENTSTATUS
    tplan_status = status.TREATMENTPLANSTATUS
    all_status = status.ALLSTATUS
    office_staff = status.OFFICESTAFF
    customer_activity = status.CUSTACTIVITY
    priority = status.PRIORITY
    
    
    #get appointment duration
    apptdur = cycle.DURATION
    
    
    #genders
    gr = gender.GENDER
    #pattitles
    pattitle = gender.PATTITLE
    #doctitle
    doctitle = gender.DOCTITLE
     
     
    #relations
    relationships = relations.RELATIONS
    dependants = relations.PLANRDEPENDANTS
    
    #regions
    
    
    obj = {
     "gender":gr,
     "relations":relationships,
     "dependants":dependants,
     "durations":apptdur,
     "patient_titles":pattitle,
     "doc_titles":doctitle,
     "appointment_status":apptsts,
     "patient_status":patsts,
     "customer_status":customer_activity,
     "treatment_status":treatment_status,
     "treatmentplan_status":tplan_status,
    
     "office_staff":office_staff,
     "priority":priority
    }
    
    
    return json.dumps(obj)
  
  
  def member_registration(self, request, sitekey, email, cell, registration_id, username, password):
    #logger.loggerpms2.info("Enter member registration")
    db = self.db
    regobj = {}
    auth = self.auth
    try:
      
      #check for valid registration data
      regobj = self.member_registration_validation(email, cell, username)
      if(regobj["result"] == "fail"):
        return json.dumps(regobj)
      
      db((db.auth_user.sitekey==sitekey) & (db.auth_user.email == email)).update(registration_key = '')
      
      # create new user
      users = db((db.auth_user.email==email) & (db.auth_user.sitekey == sitekey)).select()
      if users:
        my_crypt = CRYPT(key=auth.settings.hmac_key)
        crypt_pass = my_crypt(password)[0]  
        db(db.auth_user.id == users[0].id).update(username=username,password=crypt_pass)
        db.commit()
      else:
        my_crypt = CRYPT(key=auth.settings.hmac_key)
        crypt_pass = my_crypt(password)[0]        
        id_user= db.auth_user.insert(
                                   email = email,
                                   cell = cell,
                                   sitekey = sitekey,
                                   registration_id = registration_id,
                                   username = username,
                                   password = crypt_pass 
                                   )
        db.commit()      
      
      # create new member
      rows = db(db.company.groupkey == sitekey).select()
      companyid = rows[0].id
      companycode = rows[0].company
      webid = db.webmember.insert(email=email,webkey=sitekey,status='No_Attempt',cell=cell,\
                                  webenrolldate = common.getISTFormatCurrentLocatTime(),\
                                  company=companyid,\
                                  provider=1,hmoplan=1,imported=True,
                                  created_on = common.getISTFormatCurrentLocatTime(),
                                  created_by = 1 if(auth.user == None) else auth.user.id,
                                  modified_on = common.getISTFormatCurrentLocatTime(),
                                  modified_by = 1 if(auth.user == None) else auth.user.id    
                                  
                                  )
      
      if(webid > 0):
        db(db.webmember.id == webid).update(webmember = companycode + str(webid))

        regobj["result"] = "success"
        regobj["error_message"] = ""
        regobj["webmemberid"] = str(webid)
        regobj["webmember"] = companycode + str(webid)
        regobj["email"] = email
        regobj["cell"] = cell
        regobj["sitekey"] = sitekey
      else:
        regobj["result"] = "fail"
        regobj["error_message"] = "Member Registration Error"
        
      return json.dumps(regobj)
      
    except Exception as e:
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "Member Registration Exception Error - " + str(e)
      logger.loggerpms2.info("Member Registration Exception Error - " + str(e))
      return json.dumps(excpobj)       
   
   
   
   
  
  
    
   
  def provider_registration(self, request, providername, sitekey, email, cell, registration_id, username, password,role):
      logger.loggerpms2.info("Enter provider registration")
      db = self.db
      regobj = {}
      auth = self.auth
      try:
        db((db.auth_user.sitekey==sitekey) & (db.auth_user.email == email)).update(registration_key = '')
        
        # create new user
        users = db((db.auth_user.email==email) & (db.auth_user.sitekey == sitekey)).select()
        if users:
          #logger.loggerpms2.info("before CRYPT_1")
          my_crypt = CRYPT(key=auth.settings.hmac_key)
          #logger.loggerpms2.info("after CRYPT_1")
          crypt_pass = my_crypt(str(password))[0]  
          #logger.loggerpms2.info("after CRYPT_PASS_1")
          db(db.auth_user.id == users[0].id).update(first_name=providername,username=username,password=crypt_pass)
          db.commit()
          #logger.loggerpms2.info("after UPDATE_1")      
          
          # Setting Group Membership
          group_id = auth.id_group(role=role)
          auth.add_membership(group_id, users[0].id)  
         
         
          regobj["result"] = "success"
          regobj["error_message"] = ""
          regobj["new"] = False
          regobj["userid"] = str(users[0].id)
          regobj["email"] = email
          regobj["cell"] = cell
          regobj["sitekey"] = sitekey
             
          
        else:
          #logger.loggerpms2.info("befor CRYPT_2")
          
          my_crypt = CRYPT(key=auth.settings.hmac_key)
          #logger.loggerpms2.info("after CRYPT_2")
          
          crypt_pass = my_crypt(str(password))[0]
          
          #logger.loggerpms2.info("after CRYPT_PASS_2_" + " " + str(crypt_pass).encode("ASCII"))
          id_user= db.auth_user.insert(
                                     email = str(email),
                                     cell = str(cell),
                                     sitekey = str(sitekey),
                                     registration_id = str(registration_id),
                                     username = str(username),
                                    
                                     password = str(crypt_pass) 
                                     )
          db.commit()      
          #logger.loggerpms2.info("after INSERT_2")      
          # Setting Group Membership
          group_id = auth.id_group(role=role)
          auth.add_membership(group_id, id_user)       
  
       
         
          regobj["result"] = "success"
          regobj["error_message"] = ""
          regobj["new"] = True
          regobj["userid"] = str(id_user)
          regobj["email"] = email
          regobj["cell"] = cell
          regobj["sitekey"] = sitekey
      
      
      except Exception as e:
        excpobj = {}
        
        excpobj["result"] = "fail"
        excpobj["new"] = False
        excpobj["userid"] = ""
        excpobj["error_message"] = "Provider Registration Exception Error - " + str(e)
        logger.loggerpms2.info("Provider Registration Exception Error - " + str(e))
        return json.dumps(excpobj)       
  
      return json.dumps(regobj)
      
  def spat_registration(self, request, spat, spatname,  email, cell, username, password):
      logger.loggerpms2.info("Enter SPAT registration")
      db = self.db
      
      regobj = {}
      auth = self.auth
      sitekey = spat
      
      try:
     
        
        # create new user
        users = db((db.auth_user.email==email) & (db.auth_user.cell == cell)).select()
        if users:
          #logger.loggerpms2.info("before CRYPT_1")
          my_crypt = CRYPT(key=auth.settings.hmac_key)
          #logger.loggerpms2.info("after CRYPT_1")
          crypt_pass = my_crypt(str(password))[0]  
          #logger.loggerpms2.info("after CRYPT_PASS_1")
          db(db.auth_user.id == users[0].id).update(agent=spat,first_name=spatname,username=username,password=crypt_pass)
          db.commit()
          #logger.loggerpms2.info("after UPDATE_1")      
          
       
         
         
          regobj["result"] = "success"
          regobj["error_message"] = ""
          regobj["new"] = False
          regobj["userid"] = str(users[0].id)
          regobj["email"] = email
          regobj["cell"] = cell
          regobj["sitekey"] = sitekey
             
          
        else:
          #logger.loggerpms2.info("befor CRYPT_2")
          
          my_crypt = CRYPT(key=auth.settings.hmac_key)
          #logger.loggerpms2.info("after CRYPT_2")
          
          crypt_pass = my_crypt(str(password))[0]
          
          #logger.loggerpms2.info("after CRYPT_PASS_2_" + " " + str(crypt_pass).encode("ASCII"))
          id_user= db.auth_user.insert(
                                     email = str(email),
                                     cell = str(cell),
                                     sitekey = str(spat),
                                   
                                     username = str(username),
                                    
                                     password = str(crypt_pass) 
                                     )
          db.commit()      
          #logger.loggerpms2.info("after INSERT_2")      
              
  
       
         
          regobj["result"] = "success"
          regobj["error_message"] = ""
          regobj["new"] = True
          regobj["userid"] = str(id_user)
          regobj["email"] = email
          regobj["cell"] = cell
          regobj["sitekey"] = sitekey
      
      
      except Exception as e:
        excpobj = {}
        
        excpobj["result"] = "fail"
        excpobj["new"] = False
        excpobj["userid"] = ""
        excpobj["error_message"] = "SPAT Registration Exception Error - " + str(e)
        logger.loggerpms2.info("SPAT Registration Exception Error - " + str(e))
        return json.dumps(excpobj)       
  
      return json.dumps(regobj)
    
    
  
  
  
  
  
  