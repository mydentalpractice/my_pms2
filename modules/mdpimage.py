from gluon import current
import datetime
import json
import os
import tempfile

import base64
from base64 import decodestring


from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger


class Image:
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    return 
  
  
  def deleteimage(self, imageid):
    
    db = self.db
    providerid = self.providerid
    auth  = current.auth
    
    db(db.dentalimage.id == imageid).update(
      is_active = False,
      modified_on=common.getISTFormatCurrentLocatTime(),
      modified_by= 1 if(auth.user == None) else auth.user.id
      
    )
    
    imageobj = {
          'imageid': imageid,
          'result' : 'success'
    }   
    
    return json.dumps(imageobj) 
  
  def updateimage(self,imageid,title,tooth,quadrant,description):
    
    
    db = self.db
    providerid = self.providerid
    auth  = current.auth
    
    db(db.dentalimage.id == imageid).update(
      title = title,
      tooth = tooth,
      quadrant = quadrant,
      description = description,
      modified_on=common.getISTFormatCurrentLocatTime(),
      modified_by= 1 if(auth.user == None) else auth.user.id
      
    )
    
    imageobj = {
          'imageid': imageid,
          'result' : 'success'
       }       
    
    return json.dumps(imageobj)

  
  def upload_imagefile(self,filename,memberid,patientid,treatmentid,title,tooth,quadrant,imagedate,description,appath):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    
    p = db(db.provider.id == providerid).select(db.provider.provider)
    provcode = p[0].provider if(len(p) == 1) else "MDP_PROV"
    
    pat = db(db.patientmember.id == memberid).select(db.patientmember.patientmember)
    patmember = pat[0].patientmember if(len(pat) == 1) else "MDP_MEMBER"
    
    r = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid) & \
           (db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.fullname,db.vw_memberpatientlist.patientmember)
    
    patientname = r[0].fullname if(len(r) == 1) else ""
    patientmember = r[0].patientmember if(len(r) == 1) else ""
    
  

    ##logger.loggerpms2.info("Image Uploaded to " + tempimgfile.name)
    
    
    ##upload the image to the server
    dirpath = os.path.join(appath , "images")
    if(not os.path.exists(dirpath)):
      os.makedirs(dirpath,0777)    

    
    dirpath = os.path.join(dirpath, provcode)
    if(not os.path.exists(dirpath)):
      os.makedirs(dirpath,0777)    
    
    dirpath = os.path.join(dirpath, patmember)  
    if(not os.path.exists(dirpath)):
      os.makedirs(dirpath,0777)    
    
    
    uploadfolder=dirpath

    imgstream = open(filename,'rb')
   
    db.dentalimage.image.uploadfolder = uploadfolder
    
    
    imageid = db.dentalimage.insert(\
      title = title,
      image = imgstream,
      
      tooth = tooth,
      quadrant = quadrant,
      imagedate = common.getdt(datetime.datetime.strptime(imagedate,"%d/%m/%Y")),
      description = description,
      is_active = True,
      provider = providerid,
      patientmember = memberid,
      patient = patientid,
      patientname = patientname,
      treatmentplan = 0,
      treatment = treatmentid,
      created_on=common.getISTFormatCurrentLocatTime(),
      modified_on=common.getISTFormatCurrentLocatTime(),
      created_by = 1 if(auth.user == None) else auth.user.id,
      modified_by= 1 if(auth.user == None) else auth.user.id
    )

    
    i = db
    #delete temporary file
    #tempimgfile.close()
    #os.remove(tempimgfile.name)
  
    #return image object
    img = db(db.dentalimage.id == imageid).select(db.dentalimage.image)
    imageobj = {
      'imageid': imageid,
      'uploadfolder':uploadfolder,
      'images_subfolder':'images',
      'provcode_subfolder':provcode,
      'patmember_subfolder':patmember,
      'filename':img[0].image
      
      
    }
    
    return json.dumps(imageobj)

  
  
  def uploadimage(self,imagedata,memberid,patientid,treatmentid,title,tooth,quadrant,imagedate,description,appath):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    
    p = db(db.provider.id == providerid).select(db.provider.provider)
    provcode = p[0].provider if(len(p) == 1) else "MDP_PROV"

    
    r = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid) & \
           (db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.fullname,db.vw_memberpatientlist.patientmember)
    
    patientname = r[0].fullname if(len(r) == 1) else ""
    patientmember = r[0].patientmember if(len(r) == 1) else ""
    patmember = r[0].patientmember if(len(r) == 1) else "MDP_MEMBER"
    
    ##upload the image to the server
    dirpath = os.path.join(appath , "images")
    if(not os.path.exists(dirpath)):
      os.makedirs(dirpath,0777)    

    
    dirpath = os.path.join(dirpath, provcode)
    if(not os.path.exists(dirpath)):
      os.makedirs(dirpath,0777)    
    
    dirpath = os.path.join(dirpath, patmember)  
    if(not os.path.exists(dirpath)):
      os.makedirs(dirpath,0777)    
    
    
    uploadfolder=dirpath    
    
    
    #save image data in a temporary file
    #logger.loggerpms2.info("Enter Upload Image")



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
    db.dentalimage.image.uploadfolder = uploadfolder
   
    imageid = db.dentalimage.insert(\
      title = title,
      image = imgstream,
      uploadfolder = uploadfolder,
      tooth = tooth,
      quadrant = quadrant,
      imagedate = common.getdt(datetime.datetime.strptime(imagedate,"%d/%m/%Y")),
      description = description,
      is_active = True,
      provider = providerid,
      patientmember = memberid,
      patient = patientid,
      patientname = patientname,
      treatmentplan = 0,
      treatment = treatmentid,
      created_on=common.getISTFormatCurrentLocatTime(),
      modified_on=common.getISTFormatCurrentLocatTime(),
      created_by = 1 if(auth.user == None) else auth.user.id,
      modified_by= 1 if(auth.user == None) else auth.user.id
    )
    
    #delete temporary file
    tempimgfile.close()
    #os.remove(tempimgfile.name)
  
    #return image object
    img = db(db.dentalimage.id == imageid).select(db.dentalimage.image)
    imageobj = {
      'imageid': imageid,
      'uploadfolder':uploadfolder,
       'images_subfolder':'images',
       'provcode_subfolder':provcode,
       'patmember_subfolder':patmember,
       'filename':img[0].image      
    }
    
    return json.dumps(imageobj)
  

  
  
  def xuploadimage(self,imagedata,appath):

    #logger.loggerpms2.info("Enter XUpload Image")
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    
    #save image data in a temporary file
    dirpath = os.path.join(appath, 'temp')
    #logger.loggerpms2.info("DirPath = " + dirpath)
    
    if(not os.path.exists(dirpath)):
      os.makedirs(dirpath,0777)
    
    tempfile.tempdir = dirpath
    tempimgfile = tempfile.NamedTemporaryFile(delete=False)
    tempimgfile.name = tempimgfile.name + ".jpg"
   
    
    #logger.loggerpms2.info("TmpImageFile = " + tempimgfile.name)
    
    with open(tempimgfile.name,"wb+") as f:
      f.write(imagedata.decode('base64'))     

    #logger.loggerpms2.info("Image Uploaded to " + tempimgfile.name)
    
    #upload the image to the server
    imgstream = open(tempimgfile.name,'rb')
    imageid = db.dentalimage.insert(\
      image = imgstream,
      tooth = 0,
      quadrant = 0,
      imagedate = datetime.datetime.today(),
      description = "",
      is_active = True,
      provider = 108,
      patientmember = 8202,
      patient = 8202,
      patientname = "XXXX",
      treatmentplan = 0,
      treatment = 0,
      created_on=common.getISTFormatCurrentLocatTime(),
      modified_on=common.getISTFormatCurrentLocatTime(),
      created_by = 1,
      modified_by= 1
    )
    
    #delete temporary file
    tempimgfile.close()
    
    
    #return image object
    imageobj = {
      'imageid': imageid
    }
    
    return json.dumps(imageobj)
  
  
  def downloadimage(self,imageid):
    
    db = self.db
    providerid = self.providerid
    
    image = db(db.dentalimage.id == imageid).select()
    
    imageobj = {}
    if(len(image) == 1):
      imageobj = {
        "imageurl" : "",
        "imageid":imageid,
        "title"  : common.getstring(image[0].title),
        "image"  : common.getstring(image[0].image),
        "tooth"  : common.getstring(image[0].tooth),
        "quadrant"  : common.getstring(image[0].quadrant),
        "description"  : common.getstring(image[0].description),
        "imagedate":(image[0].imagedate).strftime("%d/%m/%Y"),
      
    }
    
    return imageobj
  
  
  def getimages(self,page,memberid,patientid):
    
    
    db = self.db
    providerid = self.providerid
    
    page = page -1
    
    urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
    items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
    limitby = ((page)*items_per_page,(page+1)*items_per_page)         

    
    imagelist = []
    imageobj  = {}
    
    
    query = (db.dentalimage.is_active == True)
    query = ((query) & (db.dentalimage.provider == providerid)) if(providerid > 0) else (query)
    limitby = None if(page<0) else limitby
    
    
    images = db((query)&(db.dentalimage.patientmember == memberid)&\
                (db.dentalimage.patient == patientid)).select(db.dentalimage.ALL, limitby=limitby)
      
    
    for image in images:
      
      imageobj = {
        "imageid":int(common.getid(image.id)),
        "imageurl" : "",
        "title"  : common.getstring(image.title),
        "image"  : common.getstring(image.image),
        "tooth"  : common.getstring(image.tooth),
        "quadrant"  : common.getstring(image.quadrant),
        "description"  : common.getstring(image.description),
        "imagedate":(image.imagedate).strftime("%d/%m/%Y"),
      }
      imagelist.append(imageobj)
    
    return json.dumps({"imagecount":len(images), "imagelist":imagelist})
    
    
    
  