from gluon import current

import requests

import haversine
from haversine import haversine, Unit


import os
import json

from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger



class Location:
  def __init__(self,db):
    self.db = db
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

  def get_city_state_frompin(self,pin):
    
    db = self.db
    auth = current.auth
    rspobj = {}
    
    pin_url = "https://api.postalpincode.in/pincode/" + str(pin)
    try:
      
      resp = requests.get(pin_url)
      
      obj = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
        obj = resp.json()
        if(len(obj)>=1):
          if(obj[0]["Status"] == "Success"):
            po=obj[0]["PostOffice"]
            if(len(po) >= 1):
              st = po[0]["State"]
              city = po[0]["District"]
              rspobj["result"]="success"
              rspobj["error_message"] = ""
              rspobj["state"]=st
              rspobj["city"]=city
              
              
            else:
              error_message = "Get City State from Pin API Error   - No valid Post Office object"
              logger.loggerpms2.info(error_message)
              excpobj = {}
              excpobj["result"] = "fail"
              excpobj["error_message"] = error_message
              return json.dumps(excpobj)    
              
          else:
            error_message = "Get City State from Pin API Error   - No valid response object"
            logger.loggerpms2.info(error_message)
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_message"] = error_message
            return json.dumps(excpobj)    
            
        else:
          error_message = "Get City State from Pin API Error   - " + obj["Status"]
          logger.loggerpms2.info(error_message)
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = error_message
          return json.dumps(excpobj)    
          
        
      else:
        error_message = "Get City State from Pin API Error - " + str(resp.status_code)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
        
      
      
    except Exception as e:
        error_message = "Get City State from Pin API Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return json.dumps(rspobj)


  #Calculate the distance (in various units) between two points on Earth using their latitude(lat) and longitude(long).
  def getdistance(self,originlat, originlong, destlat,destlong, unit="km"):
     
    db = self.db
    auth = current.auth
    
    try:
      origin = (originlat, originlong)
      dest = (destlat,destlong)
      distance = round(haversine(origin,dest,unit),2)
      
      
      
      distobj={
          
          "distance":str(distance),
          "unit":unit,
          "result":"success",
          "error_message":""
      } 
      
      return json.dumps(distobj)
    
    except Exception as e:
        error_message = "Get Distance Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return
   
  
 
  
  #Returns list of providers within a radius of the origin location
  def getproviderswithinradius(self,originlat,originlong,radius,unit):
        
      db = self.db
      auth = current.auth
      
      try:
        
        provlist = []
        provobj = {}
        
        provs = db((db.provider.id > 0 ) &\
                   (db.provider.registered == True) & \
                   (db.provider.pa_accepted == True) & \
                   db.provider.is_active == True).select(db.provider.id,
                                                          db.provider.provider,
                                                          db.provider.providername,
                                                          db.provider.pa_practicename,
                                                          db.provider.pa_practiceaddress,
                                                          db.provider.city,
                                                          db.provider.pin,
                                                          db.provider.cell,
                                                          db.provider.telephone,
                                                          db.provider.pa_longitude,
                                                          db.provider.pa_latitude,
                                                          db.provider.pa_locationurl,
                                                          db.provider.available)

        for prov in provs:
          
          
          if((common.isfloat(prov.pa_latitude) == False) | (common.isfloat(prov.pa_longitude) == False)):
            continue
          
          
        
          #logger.loggerpms2.info("Long/Lat :" + prov.provider + ":" + str(prov.pa_longitude) + ":" + str(prov.pa_latitude))
          destlat = float(common.getid(prov.pa_latitude))
          destlong = float(common.getid(prov.pa_longitude))
          
          jsonobj = json.loads(self.getdistance(originlat,originlong,destlat,destlong,unit))
          
          dist = round(float(common.getstring(jsonobj.get("distance","0.0"))),2)
          
          #if provider distance is within radius, then add to the list
          if(dist <= radius):
            provobj={
            
              "providerid":int(common.getid(prov.id)),
              "provider":common.getstring(prov.provider),
              "providername":common.getstring(prov.providername),
              "practicename":common.getstring(prov.pa_practicename),
              "practiceaddress":common.getstring(prov.pa_practiceaddress),
              "city":prov.city,
              "pin":prov.pin,
              "cell":prov.cell,
              "telephone":prov.telephone,
              "latitude":prov.pa_latitude,
              "longitude":prov.pa_longitude,
              "location":prov.pa_locationurl,
              "available":common.getboolean(prov.available)
              
            }
            
            provlist.append(provobj)
        
        provobj = {
        
          "result":"success",
          "error_message":"",
          "radius":radius,
          "unit":unit,
           
           "originlat":originlat,
           "originlong":originlong,
           "providerlist":provlist,
        } 
        
        return json.dumps(provobj)
      
      except Exception as e:
          error_message = "Get Providers within Radius Exception Error - " + str(e)
          logger.loggerpms2.info(error_message)
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = error_message
          return json.dumps(excpobj)    
      
      return
      
  
  
  #Returns list of providers within a radius of the origin provider
  def getproviderswithpincode(self,pin=None):
     
    db = self.db
    auth = current.auth
    
    try:
      
      provs = db( ((1==1) if(pin == None) else (db.provider.pin == pin )) &\
                 (db.provider.registered == True) &\
                 (db.provider.pa_accepted == True) &\
                 db.provider.is_active == True).select(db.provider.id,\
                                                      db.provider.provider,\
                                                      db.provider.providername,
                                                      db.provider.pa_practicename,
                                                      db.provider.pa_practiceaddress,
                                                      db.provider.city,
                                                      db.provider.pin,
                                                      db.provider.cell,
                                                      db.provider.telephone,
                                                      db.provider.pa_longitude,
                                                      db.provider.pa_latitude,
                                                      db.provider.pa_locationurl,
                                                      db.provider.available)

 
      for prov in provs:
        
        provobj={
        
          "providerid":int(common.getid(prov.id)),
          "provider":common.getstring(prov.provider),
          "providername":common.getstring(prov.providername),
          "practicename":common.getstring(prov.pa_practicename),
          "practiceaddress":common.getstring(prov.pa_practiceaddress),
          "city":prov.city,
          "pin":prov.pin,
          "cell":prov.cell,
          "telephone":prov.telephone,
          "latitude":prov.pa_latitude,
          "longitude":prov.pa_longitude,
          "location":prov.pa_locationurl,
          "available":common.getboolean(prov.available)          
        }
        
        provlist.append(provobj)
    
      provobj = {
      
         "providerid":providerid,
         "radius":radius,
         "unit":unit,
         
         "originlat":originlat,
         "originlong":originlong,
         "providerlist":provlist,
         
         "result":"success",
         "error_message":""
      
      } 
      
      return json.dumps(provobj)      
      
    except Exception as e:
        error_message = "Get Providers with Pincode Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return
  

  
    
  #Returns list of clinics within a radius of the origin location
  def getclinicswithinradius(self,originlat,originlong,radius,unit):
      
      logger.loggerpms2.info("Enter getclinicwithinradius" + str(originlat) + " " + str(originlong) + " " + str(radius))
      db = self.db
      auth = current.auth
      
      try:
        
        clnlist = []
        clnobj = {}
        dlist = []
        
        clns = db((db.vw_clinic.id > 0 ) & (db.provider.available == True) &\
                   db.vw_clinic.is_active == True).select(db.provider.id,
                                                          db.provider.provider,
                                                          db.provider.providername,
                                                          db.provider.pa_practicename,
                                                          db.provider.pa_practiceaddress,
                                                          db.provider.pa_longitude,
                                                          db.provider.pa_latitude,
                                                          db.provider.pa_locationurl,
                                                          db.provider.available,
                                                          db.vw_clinic.clinicid,
                                                          db.vw_clinic.name,
                                                          db.vw_clinic.city,
                                                          db.vw_clinic.pin,
                                                          db.vw_clinic.cell,
                                                          db.vw_clinic.email,
                                                          db.vw_clinic.longitude,
                                                          db.vw_clinic.latitude,
                                                          db.vw_clinic.gps_location,
                                                          db.vw_clinic.primary_clinic,
                                                          left = db.provider.on((db.provider.id == db.vw_clinic.ref_id) & (db.vw_clinic.ref_code == "PRV")))

        for cln in clns:
          if((common.isfloat(common.getvalue(cln.vw_clinic.latitude)) == False) | (common.isfloat(common.getvalue(cln.vw_clinic.longitude)) == False)):
            
            #logger.loggerpms2.info("GetClinics within radius Clinics Loop - Null Lat Long\n")
            #logger.loggerpms2.info(str(cln.vw_clinic.clinicid) + " " + common.getstring(cln.vw_clinic.name) + " " + \
            #common.getstring(cln.vw_clinic.city) + " " + common.getstring(cln.vw_clinic.pin))
            continue
        
          
          destlat = float(common.getid(cln.vw_clinic.latitude))
          destlong = float(common.getid(cln.vw_clinic.longitude))
          
          jsonobj = json.loads(self.getdistance(originlat,originlong,destlat,destlong,unit))
          
          dist = round(float(common.getstring(jsonobj.get("distance","0.0"))),2)
          
          #if provider distance is within radius, then add to the list
          if((dist <= radius) & (common.getboolean(cln.provider.available == True))):
            #logger.loggerpms2.info("Distance="+ str(dist) + "-Long/Lat:" + cln.vw_clinic.name + ":" + str(cln.vw_clinic.longitude) + ":" + str(cln.vw_clinic.latitude))
            dlist.append(dist)
            clnobj={
              "distance":str(dist),
              "providerid":int(common.getid(cln.provider.id)),
              "provider":common.getstring(cln.provider.provider),
              "providername":common.getstring(cln.provider.providername),
              "practicename":common.getstring(cln.provider.pa_practicename),
              "practiceaddress":common.getstring(cln.provider.pa_practiceaddress),
              "clinicid":int(common.getid(cln.vw_clinic.clinicid)),
              "name":cln.vw_clinic.name,
              "city":cln.vw_clinic.city,
              "pin":cln.vw_clinic.pin,
              "cell":cln.vw_clinic.cell,
              "email":cln.vw_clinic.email,
              "primary_clinic":common.getboolean(cln.vw_clinic.primary_clinic),
              "latitude":cln.vw_clinic.latitude,
              "longitude":cln.vw_clinic.longitude,
              "location":cln.vw_clinic.gps_location,
              "available":common.getboolean(cln.provider.available)
            }
            
            clnlist.append(clnobj)
        
        
        dlist.sort()
        clnlist1 = []
        
        for d in dlist:
          for c in clnlist:
            if(float(c["distance"]) == float(d)):
              clnlist1.append(c)
              continue
          
        clnobj = {
        
          "result":"success",
          "error_message":"",
          "radius":radius,
          "unit":unit,
           
           "originlat":originlat,
           "originlong":originlong,
           "clnlist":clnlist1,
        } 
        
        return json.dumps(clnobj)
      
      except Exception as e:
          error_message = "Get Clinics within Radius Exception Error - " + str(e)
          logger.loggerpms2.info(error_message)
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = error_message
          return json.dumps(excpobj)    
      
      return
  
        