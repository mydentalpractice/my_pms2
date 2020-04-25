from gluon import current
import json

import datetime
from datetime import timedelta

import os
import tempfile

from base64 import decodestring

from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger

class Preregister:
  def __init__(self,db,providerid,company):
    self.db = db
    self.providerid = providerid
    self.company = company
    return 

  #this method creates a new preregister patient
  def newpreregister(self, regdata):
    db = self.db

    providerid = self.providerid
    
    c = db(db.company.company == self.company).select(db.company.id)
    companyid = int(common.getid(c[0].id)) if len(c) >0 else 0
    
    jsonresp = {}
    
    regid = 0
    
    
    

    try:
      #new pre-registration
      regid = db.preregister.insert(\
        
        
        
        fname = regdata["fname"],
        lname = regdata["lname"],
        address = regdata["address"],
        city = regdata["city"],
        pin = regdata["pin"],
        st = regdata["st"],
        gender = regdata["gender"],
        dob = datetime.datetime.strptime(regdata["dob"], "%d/%m/%Y"),
        pemail = regdata["pemail"],
        cell = regdata["cell"],
        oemail = regdata["oemail"],
        description = regdata["description"],
        treatmentplandetails = regdata["treatmentplandetails"],
        priority = regdata["priority"],
        employeeid = regdata["employeeid"],
        employeephoto = "",
        image = "",
        
        provider = providerid,
        company = companyid,
        
        is_active = True,
        created_on = common.getISTFormatCurrentLocatTime(),
        created_by = 1,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1
        
      )
      
      jsonresp = {"preregisterid":str(regid), "result":"success","error_message":""}
    
    except Exception as e:
      logger.loggerpms2.info("Create Preregistration  Exception:\n" + str(e))
      jsonresp = {
        "result":"fail",
        "error_message":"Create Preregistration Exception:\n" + str(e)
      }
    
    return json.dumps(jsonresp)
  
  #this method gets a list of all case reports filtered on email and cell
  def get_preregister_list(self):
    
    db = self.db
      
    providerid = self.providerid
    
    c = db(db.company.company == self.company).select(db.company.id)
    companyid = int(common.getid(c[0].id)) if len(c) >0 else 0       

    p = db(db.provider.provider == 'P0001').select(db.provider.id)
    p0001_id = int(common.getid(p[0].id))  if(len(p)>0) else 0

    jsonresp = {}
    regobj = {}
    reglist = []
    
    try:
      if((providerid == p0001_id) | (providerid==0)):
        if(companyid > 0):
          regs = db((db.preregister.company == companyid) & (db.preregister.is_active == True)).select()
        else:
          regs = db((db.preregister.is_active == True)).select()
        
      else:
        if(companyid > 0):
          regs = db((db.preregister.provider == providerid) & (db.preregister.company == companyid) & (db.preregister.is_active == True)).select()
        else:
          regs = db((db.preregister.provider == providerid)  & (db.preregister.is_active == True)).select()
      
      for reg in regs:
        regobj = json.loads(self.getpreregister(reg.id))
        reglist.append(regobj)
        
      jsonresp = {
        "regcount":str(len(reglist)),
        "reglist":reglist,
        "result":"success",
        "error_message":"",
      
      }
        
        
    except Exception as e:
      logger.loggerpms2.info("Get Pre Register List Response Exception: \n" + str(e))
      jsonresp = {
        "result":"fail",
        "error_message":"Get Pre Register List Response Exception: \n" + str(e)
      }
    
    return json.dumps(jsonresp)  
     
  #this method returns casereport
  def getpreregister(self,regid):
    db = self.db
    
    providerid = self.providerid
        
    jsonresp = {}
    regobj = {}
    
    try:
      
      regdata = db(db.preregister.id == regid).select()
      
      
      c = db(db.company.id == int(common.getid(regdata[0].company))).select(db.company.company) if(len(regdata) > 0) else db(db.company.id == 0).select(db.company.company)
      cc = "" if (len(c) <= 0) else c[0].company
      
      regobj["preregisterid"] = regdata[0].id
      regobj["fname"] = regdata[0].fname
      regobj["lname"] = regdata[0].lname
      regobj["address"] = regdata[0].address
      regobj["city"] = regdata[0].city
      regobj["pin"] = regdata[0].pin
      regobj["st"] = regdata[0].st
      regobj["gender"] = regdata[0].gender
      regobj["dob"] = regdata[0].dob.strftime("%d/%m/%Y")  if(regdata[0].dob != None) else ""
      regobj["pemail"] = regdata[0].pemail
      regobj["cell"] = regdata[0].cell
      regobj["oemail"] = regdata[0].oemail
      regobj["description"] = regdata[0].description
      regobj["treatmentplandetails"] = regdata[0].treatmentplandetails
      regobj["priority"] = regdata[0].priority
      regobj["employeeid"] = regdata[0].employeeid
      
      regobj["providerid"] = providerid
      regobj["company"] = cc

      regobj["result"] = "success"
      regobj["error_message"] = ""
    
      jsonresp = regobj
    except Exception as e:
      logger.loggerpms2.info("Get Pre Register Response Exception: \n" + str(e))
      jsonresp = {
        "result":"fail",
        "error_message":"Get Pre Register Response Exception: \n" + str(e)
      }
    
    return json.dumps(jsonresp)
  
  
  #this method update the case report
  def updatepreregister(self,regdata):
    
    
    db = self.db
    providerid = self.providerid
    c = db(db.company.company == self.company).select(db.company.id)
    companyid = int(common.getid(c[0].id)) if len(c) >0 else 0       
    
    jsonresp = {}
    
    try:
      regid = int(common.getid(regdata["preregisterid"]))
      db(db.preregister.id == regid).update(\
        
        fname = regdata["fname"],
        lname = regdata["lname"],
        address = regdata["address"],
        city = regdata["city"],
        pin = regdata["pin"],
        st = regdata["st"],
        dob = datetime.datetime.strptime(regdata["dob"], "%d/%m/%Y"),
        gender = regdata["gender"],
        pemail = regdata["pemail"],
        cell = regdata["cell"],
        oemail = regdata["oemail"],
        description = regdata["description"],
        treatmentplandetails = regdata["treatmentplandetails"],
        priority = regdata["priority"],
        
        company = companyid,
        provider = providerid,
        
        employeeid = regdata["employeeid"],
        
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1
      )
      jsonresp = {"preregisterid":str(regid), "result":"success","error_message":""}      
    except Exception as e:
      logger.loggerpms2.info("Update Pre Register Response Exception:\n " + str(e))
      jsonresp = {
        "result":"fail",
        "error_message":"Update Pre Register Exception:\n" + str(e)
      }
    
    return json.dumps(jsonresp)
    
   
  def deletepreregister(self,regid):
    
    
    db = self.db

    jsonresp = {}
    
    try:
      
      db(db.preregister.id == regid).update(\
        is_active = False,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1
      )
      jsonresp = {"preregisterid":str(regid), "result":"success","error_message":""}      
    except Exception as e:
      logger.loggerpms2.info("Delete Pre Register Response Exception:\n " + str(e))
      jsonresp = {
        "result":"fail",
        "error_message":"Delete Pre Register Exception:\n" + str(e)
      }
    
    return json.dumps(jsonresp)
  
  
  def uploadphoto(self,regid,imagedata,appath):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    imageobj = {}

  

    dirpath = os.path.join(appath, 'temp')
    
    if(not os.path.exists(dirpath)):
      os.makedirs(dirpath,0777)
    
    tempfile.tempdir = dirpath
    tempimgfile = tempfile.NamedTemporaryFile(delete=False)
    tempimgfile.name = tempimgfile.name + ".jpg"

    with open(tempimgfile.name,"wb+") as f:
      f.write(imagedata.decode('base64'))     

    #logger.loggerpms2.info("Image Uploaded to " + tempimgfile.name)
    
    
    #upload the image to the server
    imgstream = open(tempimgfile.name,'rb')
    db(db.preregister.id == regid).update(\
      employeephoto = imgstream,
     
      modified_on = common.getISTFormatCurrentLocatTime(),
      modified_by = 1
    )

    #delete temporary file
    tempimgfile.close()
    #os.remove(tempimgfile.name)
  
    #return image object
    imageobj = {
      "result":"success",
      "error_message":""
    }
    
  
  
    return json.dumps(imageobj)  
  
  
  
  def deletephoto(self, preregid):
      
      db = self.db
      providerid = self.providerid
      
      try:
        db(db.preregister.id == preregid).update(
          employeephoto = "",
          modified_on=common.getISTFormatCurrentLocatTime(),
          modified_by= 1
          
        )
        
        imageobj = {
              'prergisterid': preregid,
              'result' : 'success',
              "error_message":""
        }   
      
      except Exception as e:
            logger.loggerpms2.info("Delete Employee Photo  Response Exception:\n " + str(e))
            imageobj = {
              "result":"fail",
              "error_message":"Delete Employee Photo Exception:\n" + str(e)
            }       

      return json.dumps(imageobj)  
  
  def downloadphoto(self,regid):
     
    db = self.db
    providerid = self.providerid
    imageobj = {}
    
    try:
      r = db(db.preregister.id == regid).select()
      
      if(len(r) == 1):
        imageobj = {
          "imageurl" : "",
          "preregisterid":regid,
          "employeephoto"  : common.getstring(r[0].employeephoto),
          "result":"success",
          "error_message":""
        
      }

    except Exception as e:
        logger.loggerpms2.info("Download Employee Photo  Response Exception:\n " + str(e))
        imageobj = {
          "result":"fail",
          "error_message":"Download Employee Photo Exception:\n" + str(e)
        }    

    
    return imageobj  
    
    
  def newpreregisterimage(self,preregimagedata):
    
    db = self.db
    
    providerid = self.providerid    
    
    
    try:
      #new pre-registration
      preregisterimageid = db.preregisterimage.insert(\
        
        preregisterid = preregimagedata["preregisterid"],
        title = preregimagedata["title"],
        tooth = preregimagedata["tooth"],
        quadrant = preregimagedata["quadrant"],
        description = preregimagedata["description"],
        is_active = True,
      )
      
      jsonresp = {"preregisterimageid":str(preregisterimageid), "result":"success","error_message":""}
    
    except Exception as e:
      logger.loggerpms2.info("New Preregistration  Image Exception:\n" + str(e))
      jsonresp = {
        "result":"fail",
        "error_message":"New Preregistration Image Exception:\n" + str(e)
      }
    
    return json.dumps(jsonresp)
  
  
  def upatepreregisterimage(self,preregimagedata):
    
    db = self.db
    jsonresp = {}
    try:
      preregisterimageid = int(common.getid(preregimagedata["preregisterimageid"]))
      db(db.preregisterimage.id == preregisterimageid).update(\
        preregisterid = preregimagedata["preregisterid"],
        title = preregimagedata["title"],
        tooth = preregimagedata["tooth"],
        quadrant = preregimagedata["quadrant"],
        description = preregimagedata["description"]
        )
      jsonresp = {"preregisterimageid":str(preregisterimageid), "result":"success","error_message":""}  
    except Exception as e:
      logger.loggerpms2.info("Update Preregistration  Image Exception:\n" + str(e))
      jsonresp = {
        "result":"fail",
        "error_message":"Update Preregistration Image Exception:\n" + str(e)
      }
    return json.dumps(jsonresp)
  
  def uploadpreregisterimage(self,preregisterimageid,imagedata,appath):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    imageobj = {}
  
    
    #save image data in a temporary file
    #logger.loggerpms2.info("Enter Upload Image")

    try:
      dirpath = os.path.join(appath, 'temp')
      
      if(not os.path.exists(dirpath)):
        os.makedirs(dirpath,0777)
      
      tempfile.tempdir = dirpath
      tempimgfile = tempfile.NamedTemporaryFile(delete=False)
      tempimgfile.name = tempimgfile.name + ".jpg"
  
      with open(tempimgfile.name,"wb+") as f:
        f.write(imagedata.decode('base64'))     
  
      #logger.loggerpms2.info("Image Uploaded to " + tempimgfile.name)
      
      
      #upload the image to the server
      imgstream = open(tempimgfile.name,'rb')
      
      
      db(db.preregisterimage.id == preregisterimageid).update(\
        image = imgstream,
        imagedate = common.getISTFormatCurrentLocatTime()
      )
  
      #delete temporary file
      tempimgfile.close()
      #os.remove(tempimgfile.name)
    
      #return image object
      imageobj = {
        "result":"success",
        "error_message":""
      }
    
    except Exception as e:
        logger.loggerpms2.info("Upload Pre Register Image API Exception:\n " + str(e))
        imageobj = {
          "result":"fail",
          "error_message":"Upload Pre Register Image API Exception:\n" + str(e)
        }    

    return json.dumps(imageobj)  

    
  def getpreregisterimages(self,page,preregid):
     
     
    db = self.db
    providerid = self.providerid
    
    page = page -1
    
    urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
    items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
    limitby = None if(page < 0) else ((page)*items_per_page,(page+1)*items_per_page)         

    
    imagelist = []
    imageobj  = {}
    
    
    query = (db.preregisterimage.is_active == True)
    query = ((query) & (db.preregisterimage.provider == providerid)) if(providerid > 0) else (query)
    
    images = db((query)&(db.preregisterimage.preregisterid == preregid)).select(db.preregisterimage.ALL,limitby=limitby)
      
    
    for image in images:
      
      imageobj = {
        "imageid":int(common.getid(image.preregisterimage.id)),
      }
      imagelist.append(imageobj)
    
    return json.dumps({"imagecount":len(images), "imagelist":imagelist})
    

  def getpreregisterimage(self,imageid):
     
    db = self.db
    providerid = self.providerid
    
    image = db(db.preregisterimage.id == imageid).select(db.preregisterimage.ALL,db.preregister.fname,db.preregister.lname,\
                                                         left=db.preregister.on(db.preregister.id==db.preregisterimage.preregisterid))
    
    imageobj = {}
    if(len(image) == 1):
      imageobj = {
        "imageurl" : "",
        "imageid":imageid,
        "title"  : common.getstring(image[0].preregisterimage.title),
        "image"  : common.getstring(image[0].preregisterimage.image),
        "tooth"  : common.getstring(image[0].preregisterimage.tooth),
        "quadrant"  : common.getstring(image[0].preregisterimage.quadrant),
        "description"  : common.getstring(image[0].preregisterimage.description),
        "imagedate":(image[0].preregisterimage.imagedate).strftime("%d/%m/%Y"),
        "fname":common.getstring(image[0].preregister.fname),
        "lname":common.getstring(image[0].preregister.lname)
    }
    
    return imageobj         
