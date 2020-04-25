from gluon import current
CRYPT = current.globalenv["CRYPT"]

import datetime
import time

import os;
import uuid
from uuid import uuid4

import json
import common

class User:
  def __init__(self,db,auth,username,password):
    self.db = db
    self.auth = auth
    self.username  = username.strip()
    self.password = password.strip()
    return 
  
  #Authenticate the user returning JSON data
  #If successful, return authenticate user data, provider data(if user is provider), web admin data (if user is admin), patient data (if user is patient - member or walkin)
  def login(self):
    auth = self.auth
    db = self.db
    user = auth.login_bare(self.username, self.password)
    user_data = None
    
    if(user==False):
      user_data ={
        "result" : False,
        "message":"Authentication Error",
      }

    else:
        auth.user.impersonated = False
        auth.user.impersonatorid = 0        
        
        provdict = common.getprovider(auth, db)
        
        if(int(provdict["providerid"]) == 0):
          #webadmin
          user_data ={
            "result" : True,
            "usertype":"webadmin",
            "providerid":int(provdict["providerid"]),
            "providername":provdict["providername"],
          }
          
        else:
          #provider
          user_data ={
            "result" : True,
            "usertype":"provider",
            "providerid":int(provdict["providerid"]),
            "provider":provdict["provider"],
            "providername":provdict["providername"],
            "registration":provdict["registration"]
          }
    return json.dumps(user_data)
  
  def logout(self):
    auth = self.auth
    auth.logout()
    
    data = {"logout":"Logout Success"}
    
    return json.dumps(data)  
  

  def request_username(self,email):
    
    
    db = self.db
    
    ds = db(db.auth_user.email == email).select(db.auth_user.username)

    user_data = None
    
    if(len(ds) == 0):
      user_data = {"result":False, "message":"Invalid Email"}
    elif (len(ds) > 1):
      user_data = {"result":False, "message":"More than one user has this email"}
    else:
      user_data = {"result":True, "username":ds[0].username}
      
    
    return json.dumps(user_data)
  
  
 

  def request_resetpassword(self,email):

    db = self.db
    ds = db((db.auth_user.email == email) & (db.auth_user.username == self.username)).select(db.auth_user.id)
    user_data = None
       
    if(len(ds) == 0):
      user_data = {"result":False, "message":"Invalid Email-Username"}
    elif (len(ds) > 1):
      user_data = {"result":False, "message":"More than one user has this email"}
    else:
      reset_password_key=str(int(time.time()))+'-'+str(uuid.uuid4())
      userid = common.getid(ds[0].id)
      db(db.auth_user.id == userid).update(reset_password_key = reset_password_key)   
      user_data = {"result":True, "resetpasswordkey":reset_password_key}
    
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
    
    
  
  
  
  
  
  