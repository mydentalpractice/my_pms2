from gluon import current
import datetime

import json
import os
import tempfile

import base64
from base64 import decodestring


from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger

#Image (.PNG, .GIF, .JPG, .JPEG)
#Audio (.WAV, .OGG, .MP3)
#Video (.MOV, .MPE, .MP4, .MPG, .MPG2, .MPEG, .MPEG4, .MOVIE)

class Media:
    def __init__(self,db,providerid,mediatype,mediaformat):
        self.db = db
        self.providerid = providerid
        self.mtype = mediatype
        self.mformat = mediaformat 
        
        
        return 


    def deletemedia(self, mediaid):

        db = self.db
        providerid = self.providerid
        auth  = current.auth
        try:
            db(db.dentalimage.id == mediaid).update(
                is_active = False,
                modified_on=common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id
    
            )
    
            mediaobj = {
                'mediaid': mediaid,
                'result' : 'success',
                "error_code":"",
                "error_message":""
            }   
         
        except Exception as e:
            logger.loggerpms2.info("Delete Media Exception:\n" + str(e))      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"            
            excpobj["error_message"] = "Delete Media Exception Exception Error - " + str(e)
            return json.dumps(excpobj)  
        
        return json.dumps(mediaobj) 

    def updatemedia(self,avars):


        db = self.db
        providerid = self.providerid
        auth  = current.auth
        
        mediaid = int(common.getid(avars["mediaid"])) if "mediaid" in avars else 0
        title = avars["title"] if "title" in avars else ""      
        tooth = avars["tooth"] if "tooth" in avars else ""        
        quadrant = avars["quadrant"] if "quadrant" in avars else ""        
        description = avars["description"] if "description" in avars else ""        
        
        try:
            db(db.dentalimage.id == mediaid).update(
                title = title,
                tooth = tooth,
                quadrant = quadrant,
                description = description,
                modified_on=common.getISTFormatCurrentLocatTime(),
                modified_by= 1 if(auth.user == None) else auth.user.id
    
            )
    
            mediaobj = {
                'mediaid': mediaid,
                'result' : 'success',
                "error_code":"",
                "error_message":""
            } 
            
        except Exception as e:
            logger.loggerpms2.info("Update Media Exception:\n" + str(e))      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"            
            excpobj["error_message"] = "Update Media Exception Exception Error - " + str(e)
            return json.dumps(excpobj)        
              

        return json.dumps(mediaobj)


    #this method uploads audio/video files to Application Server
    def upload_mediafile(self,avars):

        db = self.db
        providerid = self.providerid
        auth = current.auth

        filename = avars["filename"] if "filename" in avars else ""
        memberid = int(common.getid(avars["memberid"])) if "memberid" in avars else 0
        patientid = int(common.getid(avars["patientid"])) if "patientid" in avars else 0
        treatmentid = int(common.getid(avars["treatmentid"])) if "treatmentid" in avars else 0
        title = avars["title"] if "title" in avars else ""
        tooth = avars["tooth"] if "tooth" in avars else ""
        quadrant = avars["quadrant"] if "quadrant" in avars else ""
        mediadate = avars["mediadate"] if "mediadate" in avars else common.getstringfromdate(datetime.date.today(),"%d/%m/%Y")
                                                                                           
        description = avars["description"] if "description" in avars else ""
        appath = avars["appath"] if "appath" in avars else ""


        try:
            p = db(db.provider.id == providerid).select(db.provider.provider)
            provcode = p[0].provider if(len(p) == 1) else "MDP_PROV"
    
            pat = db(db.patientmember.id == memberid).select(db.patientmember.patientmember)
            patmember = pat[0].patientmember if(len(pat) == 1) else "MDP_MEMBER"
    
            r = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid) & \
                   (db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.fullname,db.vw_memberpatientlist.patientmember)
    
            patientname = r[0].fullname if(len(r) == 1) else ""
            patientmember = r[0].patientmember if(len(r) == 1) else ""
    
    
    
            ##logger.loggerpms2.info("Image Uploaded to " + tempimgfile.name)
    
    
            ##upload the media  to the server
            x = appath.split('\\') 
            appath = os.path.join(x[0],"\\")
            appath = os.path.join(appath,x[1])
            appath = os.path.join(appath,x[2])            
            appath = os.path.join(appath,x[3]) if len(x) == 4 else appath
            
            dirpath = os.path.join(appath , "media")
            if(not os.path.exists(dirpath)):
                os.makedirs(dirpath,0777)    
    
            dirpath = os.path.join(dirpath , self.mtype)
            media_subfolder = os.path.join("media" , self.mtype)
            if(not os.path.exists(dirpath)):
                os.makedirs(dirpath,0777)    
    
    
            dirpath = os.path.join(dirpath, provcode)
            if(not os.path.exists(dirpath)):
                os.makedirs(dirpath,0777)    
    
            dirpath = os.path.join(dirpath, patmember)  
            if(not os.path.exists(dirpath)):
                os.makedirs(dirpath,0777)    
    
            uploadfolder=dirpath
    
            mediasize = os.path.getsize(filename)
    
            medstream = open(filename,'rb')
            
            db.dentalimage.image.uploadfolder = uploadfolder
    
           
                
    
            mediaid = db.dentalimage.insert(\
                title = title,
                image = medstream,
                uploadfolder = uploadfolder,
    
                tooth = tooth,
                quadrant = quadrant,
                imagedate = common.getdatefromstring(mediadate,"%d/%m/%Y"),
                description = description,
                
                provider = providerid,
                patientmember = memberid,
                patient = patientid,
                patientname = patientname,
                treatmentplan = 0,
                treatment = treatmentid,
                
                mediatype = self.mtype,
                mediaformat = self.mformat,
                mediafile = filename,
                mediasize = mediasize,
                
                is_active = True,
                created_on=common.getISTFormatCurrentLocatTime(),
                modified_on=common.getISTFormatCurrentLocatTime(),
                created_by = 1 if(auth.user == None) else auth.user.id,
                modified_by= 1 if(auth.user == None) else auth.user.id
            )
    
    
            
            #return image object
            media = db(db.dentalimage.id == mediaid).select(db.dentalimage.image)
            mediaobj = {
                'mediaid': mediaid,
                'media':media[0].image,
                'uploadfolder':uploadfolder,
                
               
                'mediafilename':filename,
                "result":"success",
                "error_code":"",
                "error_message":""
    
    
            }
        except Exception as e:
            logger.loggerpms2.info("Upload Media File Exception:\n" + str(e))      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"            
            excpobj["error_message"] = "Upload Media File Exception Exception Error - " + str(e)
            return json.dumps(excpobj)        
    
            
            
        return json.dumps(mediaobj)



    def upload_media(self,avars):

        logger.loggerpms2.info("Enter upload_media")
        db = self.db
        providerid = self.providerid
        auth = current.auth
 
        mediadata = avars["mediadata"] if "mediadata" in avars else ""
        memberid = int(common.getid(avars["memberid"])) if "memberid" in avars else 0
        patientid = int(common.getid(avars["patientid"])) if "patientid" in avars else 0
        treatmentid = int(common.getid(avars["treatmentid"])) if "treatmentid" in avars else 0
        title = avars["title"] if "title" in avars else ""
        tooth = avars["tooth"] if "tooth" in avars else ""
        quadrant = avars["quadrant"] if "quadrant" in avars else ""
        mediadate = avars["mediadate"] if "mediadate" in avars else common.getstringfromdate(datetime.date.today(),"%d/%m/%Y")
        
        ref_code = avars["ref_code"] if "ref_code" in avars else "RST"
        ref_id = int(common.getid(avars["ref_id"])) if "ref_id" in avars else 0
                                                                                           
        description = avars["description"] if "description" in avars else ""
        appath = avars["appath"] if "appath" in avars else ""
        
        try:

    
    
            r = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid) & \
                   (db.vw_memberpatientlist.is_active == True)).select(db.vw_memberpatientlist.fullname)
    
            patientname = r[0].fullname if(len(r) == 1) else ""
            
           
    
            
            ##upload the image to the server
            #appath = "d:\\web2py\\applications"
            x = appath.split('\\') 
           
            appath = os.path.join(x[0],"\\")
            appath = os.path.join(appath,x[1])
            appath = os.path.join(appath,x[2])
            appath = os.path.join(appath,x[3])  if len(x) == 4 else appath
            
            dirpath = os.path.join(appath , "media")
            if(not os.path.exists(dirpath)):
                os.makedirs(dirpath,0777)    
    
            strdate = common.getstringfromdate(datetime.date.today(),"%m-%Y")    
            dirpath = os.path.join(dirpath , strdate)
            media_subfolder = dirpath
            if(not os.path.exists(dirpath)):
                os.makedirs(dirpath,0777)    
    
            dirpath = os.path.join(dirpath , self.mtype)
            media_subfolder = dirpath
            if(not os.path.exists(dirpath)):
                os.makedirs(dirpath,0777)    
    
    
            #dirpath = os.path.join(dirpath, provcode)
            #if(not os.path.exists(dirpath)):
                #os.makedirs(dirpath,0777)    
    
            #dirpath = os.path.join(dirpath, patmember)  
            #if(not os.path.exists(dirpath)):
                #os.makedirs(dirpath,0777)    
    
    
            uploadfolder=dirpath    #appications\media\<mm-Y>\<media-type>
    
    
            #save image data in a temporary file
            logger.loggerpms2.info("Enter Upload Image " + uploadfolder)
    
    
    
            dirpath = os.path.join(appath, 'temp')
            if(not os.path.exists(dirpath)):
                os.makedirs(dirpath,0777)
    
            tempfile.tempdir = dirpath
            tempmediafile = tempfile.NamedTemporaryFile(delete=False)
            tempmediafile.name = tempmediafile.name + "." + self.mformat
    
            with open(tempmediafile.name,"wb+") as f:
                f.write(mediadata.decode('base64'))     
    
            
            logger.loggerpms2.info("Image Uploaded to " + tempmediafile.name)
    
    
            #upload the image to the server
            medstream = open(tempmediafile.name,'rb')
            db.dentalimage.image.uploadfolder = uploadfolder

            mediaid = db.dentalimage.insert(\
                title = title,
                image = medstream,
                uploadfolder = uploadfolder,
    
                tooth = tooth,
                quadrant = quadrant,
                imagedate = common.getdt(datetime.datetime.strptime(mediadate,"%d/%m/%Y")),
                description = description,
                
                provider = providerid,
                patientmember = memberid,
                patient = patientid,
                patientname = patientname,
                treatmentplan = 0,
                treatment = treatmentid,
                
                mediatype = self.mtype,
                mediaformat = self.mformat,
                mediafile = "",
                mediasize = 0.0,
                
                is_active = True,
                created_on=common.getISTFormatCurrentLocatTime(),
                modified_on=common.getISTFormatCurrentLocatTime(),
                created_by = 1 if(auth.user == None) else auth.user.id,
                modified_by= 1 if(auth.user == None) else auth.user.id
            )
    
            #CLN if the media is for CLINIC, DOC if the media is for DOCTOR,PRV if the media is for Provider
            #MEM for Memeber, TRT for Treatment, USR for User, CUS for Customer, EMP for MDP Employee,
            #GUS for Guest, CSP for Customer Support, MKT for Marketing, SLS for Sales, GEN for General, RST for all others  
            #BNK for Bank, CSF for Customer Support
            #update cross-reference tables
            db.dentalimage_ref.insert(media_id = mediaid, ref_code = ref_code,ref_id = ref_id)
    
            #delete temporary file
            tempmediafile.close()
            #os.remove(tempimgfile.name)
    
            #return image object
            media = db(db.dentalimage.id == mediaid).select(db.dentalimage.image)
            mediaobj = {
                'mediaid': mediaid,
                'media':media[0].image,
                'uploadfolder':uploadfolder,
                'mediafilename':"",
                
                
                "result":"success",
                "error_code":"",
                "error_message":""
    
    
            }
    
        except Exception as e:
            logger.loggerpms2.info("Upload Media Exception:\n" + str(e))      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = "Upload Media Exception Error - " + str(e)
            return json.dumps(excpobj)        
          
        return json.dumps(mediaobj)


   

  


    def downloadmedia(self,mediaid):

        db = self.db
        providerid = self.providerid
        
        try:
            props = db(db.urlproperties.id > 0).select(db.urlproperties.mydp_ipaddress,db.urlproperties.mydp_port)
            
            media = db(db.dentalimage.id == mediaid).select()
            
            mediaobj = {}
            if(len(media) == 1):
                mediaobj = {
                    "mediaid":int(common.getid(media[0].id)),

                    "mediaurl" : props[0].mydp_ipaddress + ":" + props[0].mydp_port +"/my_dentalplan/media/media_download/" + str(mediaid),
                    "media"  : common.getstring(media[0].image),
                    "uploadfolder":media[0].uploadfolder,
                    "title"  : common.getstring(media[0].title),
                    
                    "tooth"  : common.getstring(media[0].tooth),
                    "quadrant"  : common.getstring(media[0].quadrant),
                    "description"  : common.getstring(media[0].description),
                    "mediadate":(media[0].imagedate).strftime("%d/%m/%Y"),
                    "mediatype":common.getstring(media[0].mediatype),
                    "mediaformat":common.getstring(media[0].mediaformat),
                    "mediasize":common.getvalue(media[0].mediasize),
                    "mediafile":common.getstring(media[0].mediafile),
                    "treatmentplan":media[0].treatmentplan,
                    "treatment":media[0].treatment,

                    "patientmember":media[0].patientmember,
                    "patient":media[0].patient,
                    "patienttype":media[0].patienttype,
                    "patientname":media[0].patientname,
                    "provider":media[0].provider,

                    
                    "result":"success",
                    "error_code":"",
                    "error_message":""
    
                }
            else:
                excpobj = {}
                excpobj["result"] = "fail"
                excpobj["error_message"] = "Download Media Error"
                excpobj["error_code"] = "MDP100"
                
                return json.dumps(excpobj                     )
                
        except Exception as e:
                logger.loggerpms2.info("Download Media Exception:\n" + str(e))      
                excpobj = {}
                excpobj["result"] = "fail"
                excpobj["error_code"] = "MDP100"
                excpobj["error_message"] = "Download Media  Exception Error - " + str(e)
                return json.dumps(excpobj)

        return json.dumps(mediaobj)


    def getmedia_list(self,page,memberid,patientid,mediatype,ref_code,ref_id):


        db = self.db
        providerid = self.providerid

        page = page -1

        try:
            
            urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
            items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
            limitby = ((page)*items_per_page,(page+1)*items_per_page)         
    
            
    
            medialist = []
            mediaobj  = {}
    
    
            query = (db.dentalimage.is_active == True)
            query = ((query) & (db.dentalimage.provider == providerid)) if(providerid > 0) else (query)
            query = ((query) & (db.dentalimage.mediatype == mediatype)) if(mediatype != "") else (query)
            limitby = None if(page<0) else limitby
            
            medias = None
            if(memberid != 0):  
                medias = db((query)&(db.dentalimage.patientmember == memberid)&\
                            (db.dentalimage.patient == patientid)).select(db.dentalimage.ALL, limitby=limitby)
                
            else:
                if(ref_id == 0):
                    if(mediatype == ""):
                        if(ref_code == ""):
                            medias = db((db.dentalimage.is_active == True)).select(db.dentalimage.ALL,db.dentalimage_ref.ALL,\
                                                                                left=db.dentalimage.on((db.dentalimage.id == db.dentalimage_ref.media_id)),limitby=limitby)
                        else:
                            medias = db((db.dentalimage_ref.ref_code==ref_code) & (db.dentalimage.is_active == True)).select(db.dentalimage.ALL,db.dentalimage_ref.ALL,\
                                                                                left=db.dentalimage.on((db.dentalimage.id == db.dentalimage_ref.media_id)),limitby=limitby)
                            
                    else:
                        if(ref_code==""):
                            medias = db((db.dentalimage.mediatype == mediatype) & (db.dentalimage.is_active == True)).select(db.dentalimage.ALL,db.dentalimage_ref.ALL,\
                                                                                left=db.dentalimage.on((db.dentalimage.id == db.dentalimage_ref.media_id)),limitby=limitby)
                        else:
                            medias = db((db.dentalimage_ref.ref_code==ref_code) & (db.dentalimage.mediatype == mediatype) & (db.dentalimage.is_active == True)).select(db.dentalimage.ALL,\
                                                                                left=db.dentalimage.on((db.dentalimage.id == db.dentalimage_ref.media_id)),limitby=limitby)
                                                                                                               
                else:
                    if(mediatype == ""):
                        if(ref_code == ""):
                            medias = db((db.dentalimage_ref.ref_id == ref_id)  & (db.dentalimage.is_active == True)).select(db.dentalimage.ALL,db.dentalimage_ref.ALL,\
                                                                                    left=db.dentalimage.on((db.dentalimage.id == db.dentalimage_ref.media_id)),limitby=limitby)
                        else:
                            medias = db((db.dentalimage_ref.ref_code==ref_code)&(db.dentalimage_ref.ref_id == ref_id)  & (db.dentalimage.is_active == True)).select(db.dentalimage.ALL,db.dentalimage_ref.ALL,\
                                                                                    left=db.dentalimage.on((db.dentalimage.id == db.dentalimage_ref.media_id)),limitby=limitby)
                            
                    else:
                        if(ref_code == ""):
                            medias = db((db.dentalimage_ref.ref_id == ref_id) & (db.dentalimage.mediatype == mediatype) & (db.dentalimage.is_active == True)).select(db.dentalimage.ALL,db.dentalimage_ref.ALL,\
                                                                                    left=db.dentalimage.on((db.dentalimage.id == db.dentalimage_ref.media_id)),limitby=limitby)
                        else:
                            medias = db((db.dentalimage_ref.ref_code==ref_code)&(db.dentalimage_ref.ref_id == ref_id) & (db.dentalimage.mediatype == mediatype) & (db.dentalimage.is_active == True)).select(db.dentalimage.ALL,db.dentalimage_ref.ALL,\
                                                                                    left=db.dentalimage.on((db.dentalimage.id == db.dentalimage_ref.media_id)),limitby=limitby)
                        
                    

            
            #if(providerid != 0):  
                #medias = db(db.provider_media.provider_id == providerid).select(db.dentalimage.ALL,\
                                                                         #left=db.dentalimage.on((db.dentalimage.id == db.provider_media.media_id)&\
                                                                                               #(db.dentalimage.mediatype == mediatype)&\
                                                                                               #(db.dentalimage.is_active == True)),limitby=limitby)
 
 
            #if(doctorid != 0):  
                #medias = db(db.doctor_media.doctor_id == doctorid).select(db.dentalimage.ALL,\
                                                                         #left=db.dentalimage.on((db.dentalimage.id == db.doctor_media.media_id)&\
                                                                                               #(db.dentalimage.mediatype == mediatype)&\
                                                                                               #(db.dentalimage.is_active == True)),limitby=limitby)
            #if(clinicid != 0):  
                #medias = db(db.clinic_media.clinic_id == clinicid).select(db.dentalimage.ALL,\
                                                                         #left=db.dentalimage.on((db.dentalimage.id == db.clinic_media.media_id)&\
                                                                                               #(db.dentalimage.mediatype == mediatype)&\
                                                                                               #(db.dentalimage.is_active == True)),limitby=limitby)

            #if(treatmentid != 0):  
                #medias = db(db.treatment_media.treatment_id == treatmentid).select(db.dentalimage.ALL,\
                                                                         #left=db.dentalimage.on((db.dentalimage.id == db.treatment_media.media_id)&\
                                                                                               #(db.dentalimage.mediatype == mediatype)&\
                                                                                               #(db.dentalimage.is_active == True)),limitby=limitby)
              
            #if(customer != 0):  
                #medias = db(db.customer_media.customer_id == customerid).select(db.dentalimage.ALL,\
                                                                         #left=db.dentalimage.on((db.dentalimage.id == db.customer_media.media_id)&\
                                                                                               #(db.dentalimage.mediatype == mediatype)&\
                                                                                               #(db.dentalimage.is_active == True)),limitby=limitby)
                
            #if(userid != 0):  
                #medias = db(db.auth_user_media.user_id == userid).select(db.dentalimage.ALL,\
                                                                         #left=db.dentalimage.on((db.dentalimage.id == db.auth_user_media.media_id)&\
                                                                                               #(db.dentalimage.mediatype == mediatype)&\
                                                                                               #(db.dentalimage.is_active == True)),limitby=limitby)
    
            for media in medias:
    
                mediaobj = {
                    "ref_code":media.dentalimage_ref.ref_code,
                    "ref_id":media.dentalimage_ref.ref_id,
                    "mediaid":int(common.getid(media.dentalimage.id)),
                    "title"  : common.getstring(media.dentalimage.title),
                    "mediadate":(media.dentalimage.imagedate).strftime("%d/%m/%Y"),
                    "mediatype":common.getstring(media.dentalimage.mediatype)
                }
                medialist.append(mediaobj)
                
        except Exception as e:
            logger.loggerpms2.info("Get Media List Exception:\n" + str(e))      
            excpobj = {}
            excpobj["result"] = "fail"
            excpobj["error_code"] = "MDP100"
            excpobj["error_message"] = "Get Media List Exception Exception Error - " + str(e)
            return json.dumps(excpobj)        
    
        return json.dumps({"result":"success","error_code":"","error_message":"","mediacount":len(medias), "medialist":medialist})



