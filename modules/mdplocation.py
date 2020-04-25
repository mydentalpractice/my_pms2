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
