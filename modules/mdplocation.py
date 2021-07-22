from gluon import current


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
                                                          db.provider.pa_locationurl)

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
              "location":prov.pa_locationurl
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
                                                      db.provider.pa_locationurl)

 
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
          "location":prov.pa_locationurl
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
        
      db = self.db
      auth = current.auth
      
      try:
        
        clnlist = []
        clnobj = {}
        
        clns = db((db.vw_clinic.id > 0 ) &\
                   db.vw_clinic.is_active == True).select(db.provider.id,
                                                          db.provider.provider,
                                                          db.provider.providername,
                                                          db.provider.pa_practicename,
                                                          db.provider.pa_practiceaddress,
                                                          db.provider.pa_longitude,
                                                          db.provider.pa_latitude,
                                                          db.provider.pa_locationurl,
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
          if((common.isfloat(cln.latitude) == False) | (common.isfloat(cln.longitude) == False)):
            continue
        
          logger.loggerpms2.info("Long/Lat :" + cln.name + ":" + str(cln.longitude) + ":" + str(cln.latitude))
          destlat = float(common.getid(cln.latitude))
          destlong = float(common.getid(cln.longitude))
          
          jsonobj = json.loads(self.getdistance(originlat,originlong,destlat,destlong,unit))
          
          dist = round(float(common.getstring(jsonobj.get("distance","0.0"))),2)
          
          #if provider distance is within radius, then add to the list
          if(dist <= radius):
            clnobj={
            
              "providerid":int(common.getid(cln.id)),
              "provider":common.getstring(cln.provider),
              "providername":common.getstring(cln.providername),
              "practicename":common.getstring(cln.pa_practicename),
              "practiceaddress":common.getstring(cln.pa_practiceaddress),
              "name":cln.name,
              "city":cln.city,
              "pin":cln.pin,
              "cell":cln.cell,
              "email":cln.email,
              "primary_clinic":common.getboolean(cln.primary_clinic),
              "latitude":cln.latitude,
              "longitude":cln.longitude,
              "location":cln.gps_location
            }
            
            clnlist.append(clnobj)
        
        clnobj = {
        
          "result":"success",
          "error_message":"",
          "radius":radius,
          "unit":unit,
           
           "originlat":originlat,
           "originlong":originlong,
           "clnlist":clnlist,
        } 
        
        return json.dumps(provobj)
      
      except Exception as e:
          error_message = "Get Clinics within Radius Exception Error - " + str(e)
          logger.loggerpms2.info(error_message)
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = error_message
          return json.dumps(excpobj)    
      
      return
  
        