from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)
import os
import json

import datetime

from applications.my_pms2.modules  import common

from applications.my_pms2.modules  import mdpmedia




from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger


def update_media():
    
    mediaid = int(request.vars.mediaid)
    m = db(db.dentalimage.id == mediaid).select()
    providerid  = int(m[0].provider)
    mediatype = m[0].mediatype
    mediaformat = m[0].mediaformat
    
    o = mdpmedia.Media(db, providerid, mediatype, mediaformat)
    mediaobj = json.loads(o.downloadmedia(mediaid))
    
    
    source = common.getstring(request.vars.source)
    page     = common.getpage1(request.vars.page)

    patientid   = int(mediaobj["patient"])
    memberid    = int(mediaobj["patientmember"])    

    members = db(db.patientmember.id == memberid).select()
    memberref = common.getstring(members[0].patientmember)

    providerdict = common.getproviderfromid(db, providerid)
    providername = providerdict["providername"]

    treatmentid = int(mediaobj["treatment"])

    tplanid = 0
    tplan = "Treatment Plan"



    rows = db((db.patientmember.id == memberid)&(db.patientmember.is_active == True)).select()
    membername = rows[0].fname + ' ' + rows[0].mname + ' ' + rows[0].lname    

    if(memberid == patientid):
        patienttype = 'P'
        patientname = membername
    else:
        patienttype = 'D'
        rows = db((db.patientmemberdependants.id == patientid)&(db.patientmemberdependants.is_active == True)).select()    
        if(len(rows) > 0):
            patientname = rows[0].fname + ' ' + rows[0].mname + ' ' + rows[0].lname    


    db.dentalimage.treatmentplan.default = tplanid
    db.dentalimage.treatmentplan.writable = False
    db.dentalimage.treatment.default = treatmentid
    db.dentalimage.treatment.writable = False    
    db.dentalimage.patientmember.default = memberid
    db.dentalimage.patientmember.writable = False
    db.dentalimage.patient.default = patientid
    db.dentalimage.patient.writable = False
    db.dentalimage.patienttype.default = patienttype
    db.dentalimage.patienttype.writable = False
    db.dentalimage.patientname.default = patientname
    db.dentalimage.patientname.writable = False

    db.dentalimage.provider.default = providerid
    db.dentalimage.provider.writable = False



    db.dentalimage.title.widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small')
    db.dentalimage.tooth.widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small')
    db.dentalimage.quadrant.widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small')
    db.dentalimage.imagedate.widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small date')
    db.dentalimage.patient.widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border w3-small')


    rows = db((db.provider.id == providerid)).select()
    provider = rows[0].provider

    strSQL = "select 0, '' AS patienttype, '-Select-' as fname, '' as lname"    
    strSQL = strSQL + " UNION "
    strSQL = strSQL + " select id , 'P' AS patienttype,fname,lname from patientmember where id = " + str(memberid)
    strSQL = strSQL + " UNION "
    strSQL = strSQL + " select id,'D' AS patienttype, patientmemberdependants.fname,patientmemberdependants.lname from patientmemberdependants where  patientmemberdependants.patientmember = " + str(memberid)
    dspatients = db.executesql(strSQL)    


    if(source == "treatment"):
        returnurl = URL('treatment', 'update_treatment', vars=dict(page=page,imagepage=0,providerid=providerid,treatmentid=treatmentid))
    else:
        returnurl = URL('media', 'list_media', vars=dict(providerid = providerid,memberid=memberid,patientid=patientid,page=page,memberref=memberref,mediatype=mediatype))


    formA = SQLFORM.factory(
        Field('title','string', default=common.getkeyvalue(mediaobj, "title","")),
        Field('media','string',default=common.getkeyvalue(mediaobj, "media","")),
        Field('uploadfolder','string',default=common.getkeyvalue(mediaobj, "uploadfolder","")),
        Field('tooth','string',default=common.getkeyvalue(mediaobj, "tooth","")),
        Field('quadrant','string',default=common.getkeyvalue(mediaobj, "quadrant","")),
        Field('description','text',default=common.getkeyvalue(mediaobj, "description","")),
        Field('patienttype','string',default=common.getkeyvalue(mediaobj, "patienttype","P")),
        Field('patientname','string',default=common.getkeyvalue(mediaobj, "patientname","")),
        Field('mediafile','string',default=common.getkeyvalue(mediaobj, "mediafile","")),
        Field('mediatype','string',default=common.getkeyvalue(mediaobj, "mediatype","")),
        Field('mediaformat','string',default=common.getkeyvalue(mediaobj, "mediaformat","")),
        Field('mediadate','date', default=common.getdatefromstring(common.getkeyvalue(mediaobj, "mediadate","01/01/2020"),"%d/%m/%Y"),requires = IS_DATE(format=T('%d/%m/%Y'))),
        Field('treatmentplan','integer',default=common.getkeyvalue(mediaobj, "treatmentplan","1")),
        Field('treatment','integer',default=common.getkeyvalue(mediaobj, "treatment","1")),
        Field('patientmember','integer',default=common.getkeyvalue(mediaobj, "patientmember","1")),
        Field('patient','integer',default=common.getkeyvalue(mediaobj, "patient","1")),  
        Field('provider','integer',default=common.getkeyvalue(mediaobj, "provider","1"))

    )




    formA.element('textarea[name=description]')['_style'] = 'height:50px;line-height:1.0;'
    formA.element('textarea[name=description]')['_rows'] = 5   
    formA.element('textarea[name=description]')['_cols'] = 50
    formA.element('textarea[name=description]')['_class'] = 'form-control'


    xtitle = formA.element('#no_table_title')
    xtitle['_class'] = 'form-control'
    xtitle['_placeholder'] = 'Title'
    xtitle['_autocomplete'] = 'off'   

    xtooth = formA.element('#no_table_tooth')
    xtooth['_class'] = 'form-control'
    xtooth['_placeholder'] = 'Tooth'
    xtooth['_autocomplete'] = 'off'   

    xquad = formA.element('#no_table_quadrant')
    xquad['_class'] = 'form-control'
    xquad['_placeholder'] = 'Quadrant'
    xquad['_autocomplete'] = 'off'   

    xdate = formA.element('#no_table_mediadate')
    xdate['_class'] = 'input-group form-control form-control-inline date-picker'
    xdate['_placeholder'] = 'Date'
    xdate['_autocomplete'] = 'off'   

    submit = formA.element('input',_type='submit')
    submit['_value'] = 'Save Changes'    
    submit["_class"] = "btn green"


    error = ""
    count = 0
    mediaurl = ""
    mediafile = ""
    
    
    mediaurl = URL('my_dentalplan','media','media_download',args=[mediaid]) 
    
    if formA.accepts(request,session,keepvalues=True):
        try:
            #update 
            o = mdpmedia.Media(db, providerid, mediatype, mediaformat)
            j = {
                "mediaid":mediaid,
                "memberid":str(memberid),
                "patientid":str(patientid),
                "treatmentid":str(treatmentid),
                "title":request.vars.title,
                "tooth":request.vars.tooth,
                "quadrant":request.vars.quadrant,
               
                "description":request.vars.description,
                "appath":request.folder,
                "mediatype":mediatype,
                "mediaformat":mediaformat
            }

            x= json.loads(o.updatemedia(j)) 

            mediaid = common.getkeyvalue(x,'mediaid',0)
            mediaurl = URL('my_dentalplan','media','media_download',\
                           args=[mediaid])              
            
        except Exception as e:
            error = "Update Media Exception Error - " + str(e)             
    elif formA.errors:
        x = str(formA.errors)
    else:
        i = 0

    return dict(formA=formA, returnurl=returnurl, providername=providername,memberid=memberid, memberref=memberref,\
                providerid=providerid,membername=membername,patientname=patientname,dspatients=dspatients,\
                treatmentid=treatmentid, tplanid=tplanid, tplan=tplan,page=page,patientid=patientid,\
                source=source,error=error,count=count,\
                mediatype=mediatype, mediaformat=mediaformat, mediafile=mediafile,mediaurl=mediaurl)   


def new_media():
    
    #logger.loggerpms2.info("Enter New Media")
    if(len(request.vars) == 0):
        raise HTTP(403,"Error in create_media -  request arguments " )

    mediatype = request.vars.mediatype
    mediaformat = request.vars.mediaformat
    
    source = common.getstring(request.vars.source)
    page     = common.getpage1(request.vars.page)

    providerid  = int(common.getid(request.vars.providerid))
    patientid   = int(common.getid(request.vars.patientid))
    memberid    = int(common.getid(request.vars.memberid))    

    logger.loggerpms2.info("Get all Members " + str(memberid))

    members = db(db.patientmember.id == memberid).select()
    memberref = common.getstring(members[0].patientmember)

    providerdict = common.getproviderfromid(db, providerid)
    providername = providerdict["providername"]

    treatmentid = int(common.getid(request.vars.treatmentid))

    tplanid = 0
    tplan = "Treatment Plan"


    #logger.loggerpms2.info("Get all Members1 " + str(memberid))

    rows = db((db.patientmember.id == memberid)&(db.patientmember.is_active == True)).select()
    membername = rows[0].fname + ' ' + rows[0].mname + ' ' + rows[0].lname    

    if(memberid == patientid):
        patienttype = 'P'
        patientname = membername
    else:
        patienttype = 'D'
        rows = db((db.patientmemberdependants.id == patientid)&(db.patientmemberdependants.is_active == True)).select()    
        if(len(rows) > 0):
            patientname = rows[0].fname + ' ' + rows[0].mname + ' ' + rows[0].lname    
    #logger.loggerpms2.info("Log a") 

    db.dentalimage.treatmentplan.default = tplanid
    db.dentalimage.treatmentplan.writable = False
    db.dentalimage.treatment.default = treatmentid
    db.dentalimage.treatment.writable = False    
    db.dentalimage.patientmember.default = memberid
    db.dentalimage.patientmember.writable = False
    db.dentalimage.patient.default = patientid
    db.dentalimage.patient.writable = False
    db.dentalimage.patienttype.default = patienttype
    db.dentalimage.patienttype.writable = False
    db.dentalimage.patientname.default = patientname
    db.dentalimage.patientname.writable = False

    db.dentalimage.provider.default = providerid
    db.dentalimage.provider.writable = False



    db.dentalimage.title.widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small')
    db.dentalimage.tooth.widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small')
    db.dentalimage.quadrant.widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small')
    db.dentalimage.imagedate.widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small date')
    db.dentalimage.patient.widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border w3-small')

    #logger.loggerpms2.info("Provider id " + str(providerid)) 

    rows = db((db.provider.id == providerid)).select()
    provider = rows[0].provider

    strSQL = "select 0, '' AS patienttype, '-Select-' as fname, '' as lname"    
    strSQL = strSQL + " UNION "
    strSQL = strSQL + " select id , 'P' AS patienttype,fname,lname from patientmember where id = " + str(memberid)
    strSQL = strSQL + " UNION "
    strSQL = strSQL + " select id,'D' AS patienttype, patientmemberdependants.fname,patientmemberdependants.lname from patientmemberdependants where  patientmemberdependants.patientmember = " + str(memberid)
    dspatients = db.executesql(strSQL)    

    #logger.loggerpms2.info("dspatients " + len(dspatients)) 

    if(source == "treatment"):
        returnurl = URL('treatment', 'update_treatment', vars=dict(page=page,imagepage=0,providerid=providerid,treatmentid=treatmentid))
    else:
        returnurl = URL('media', 'list_media', vars=dict(providerid = providerid,memberid=memberid,patientid=patientid,page=page,memberref=memberref,mediatype=mediatype))


    formA = SQLFORM.factory(
        Field('title','string'),
        Field('media','string'),
        Field('uploadfolder','string'),
        Field('tooth','string'),
        Field('quadrant','string'),
        Field('description','text'),
        Field('patienttype','string'),
        Field('patientname','string'),
        Field('mediafile','string'),
        Field('mediatype','string'),
        Field('mediaformat','string'),


        Field('mediadate','date', default=request.now,requires = IS_DATE(format=T('%d/%m/%Y'))),

        Field('treatmentplan','integer'),
        Field('treatment','integer'),
        Field('patientmember','integer'),
        Field('patient','integer'),  
        Field('provider','integer'),

        Field('mediasize','double'),

        Field('imagedata','text', length=50e+6, label='Image Data')


    )




    formA.element('textarea[name=description]')['_style'] = 'height:50px;line-height:1.0;'
    formA.element('textarea[name=description]')['_rows'] = 5   
    formA.element('textarea[name=description]')['_cols'] = 50
    formA.element('textarea[name=description]')['_class'] = 'form-control'


    xtitle = formA.element('#no_table_title')
    xtitle['_class'] = 'form-control'
    xtitle['_placeholder'] = 'Title'
    xtitle['_autocomplete'] = 'off'   

    xtooth = formA.element('#no_table_tooth')
    xtooth['_class'] = 'form-control'
    xtooth['_placeholder'] = 'Tooth'
    xtooth['_autocomplete'] = 'off'   

    xquad = formA.element('#no_table_quadrant')
    xquad['_class'] = 'form-control'
    xquad['_placeholder'] = 'Quadrant'
    xquad['_autocomplete'] = 'off'   

    xdate = formA.element('#no_table_mediadate')
    xdate['_class'] = 'input-group form-control form-control-inline date-picker'
    xdate['_placeholder'] = 'Date'
    xdate['_autocomplete'] = 'off'   

    submit = formA.element('input',_type='submit')
    submit['_value'] = 'Save' 
    submit["_class"] = "btn green"
    
    error = ""
    count = 0
    mediaurl = ""
    mediafile = ""
    mediaid = 0

    if formA.accepts(request,session,keepvalues=True):

        try:

            #upload image
            if(len(request.vars.imagedata)>0):
                file_content = None
                file_content = request.vars.imagedata
                
                o = mdpmedia.Media(db, providerid, mediatype, mediaformat)
                j = {
                    "mediadata":file_content,
                    "memberid":str(memberid),
                    "patientid":str(patientid),
                    "treatmentid":str(treatmentid),
                    "title":request.vars.title,
                    "tooth":request.vars.tooth,
                    "quadrant":request.vars.quadrant,
                    "mediadate":common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y"),
                    "description":request.vars.description,
                    "appath":request.folder,
                    "mediatype":mediatype,
                    "mediaformat":mediaformat
                }

                x= json.loads(o.upload_media(j)) 

                mediaid = common.getkeyvalue(x,'mediaid',0)
                mediaurl = URL('my_dentalplan','media','media_download',\
                               args=[mediaid])  

           
        except Exception as e:
            error = "Upload Audio Exception Error - " + str(e)             
    elif formA.errors:
        x = str(formA.errors)
    else:
        i = 0

    return dict(formA=formA, returnurl=returnurl, providername=providername,memberid=memberid, memberref=memberref,\
                providerid=providerid,membername=membername,patientname=patientname,dspatients=dspatients,\
                treatmentid=treatmentid, tplanid=tplanid, tplan=tplan,page=page,patientid=patientid,\
                source=source,error=error,count=count,\
                mediatype=mediatype, mediaformat=mediaformat, mediafile=mediafile,mediaurl=mediaurl)   


def list_media():
    
    db = current.globalenv['db']

    formheader = "Media  List"
    username = "Admin" 

    page = common.getpage1(request.vars.page)
    
    source = request.vars.source
    treatmentid = int(common.getid(request.vars.treatmentid))
   
    
    providerid   = int(common.getnegid(request.vars.providerid))
    provdict     = common.getproviderfromid(db, request.vars.providerid)
    providername = provdict["providername"]

    memberid     = int(common.getid(request.vars.memberid))
    patientid    = int(common.getid(request.vars.patientid))
        
    patient = common.getstring(request.vars.patient)
    fullname = common.getstring(request.vars.fullname)    
    
    mediatype = common.getstring(request.vars.mediatype)
   
    if(source == "treatment"):
        returnurl = URL('treatment', 'update_treatment', vars=dict(page=page,imagepage=0,providerid=providerid,treatmentid=treatmentid,mediatype=mediatype))
    else:
        returnurl = URL('admin', 'providerhome', vars=dict(providerid=providerid))


      
       
    db.dentalimage.image.readable = False
    db.dentalimage.uploadfolder.readable = False
    db.dentalimage.tooth.readable = False
    db.dentalimage.quadrant.readable = False
    db.dentalimage.description.readable = False
    db.dentalimage.treatmentplan.readable = False
    db.dentalimage.treatment.readable = False
    db.dentalimage.patientmember.readable = False
    db.dentalimage.patient.readable = False
    db.dentalimage.patienttype.readable = False
    db.dentalimage.patientname.readable = False
    db.dentalimage.provider.readable = False
    db.dentalimage.mediafile.readable = False
    db.dentalimage.mediaformat.readable = False
    db.dentalimage.mediasize.readable = False
    db.dentalimage.is_active.readable = False
    db.dentalimage.created_on.readable = False
    db.dentalimage.created_by.readable = False
    db.dentalimage.modified_on.readable = False
    db.dentalimage.modified_by.readable = False
    db.dentalimage.dicomUserUuid.readable = False
    db.dentalimage.dicomAcctUuid.readable = False
    db.dentalimage.dicomInstUuid.readable = False
    db.dentalimage.dicomPatName.readable = False
    db.dentalimage.dicomPatUuid.readable = False
    db.dentalimage.dicomPatid.readable = False
    db.dentalimage.dicomPatOrderUuid.readable = False
    db.dentalimage.dicomProcDesc.readable = False
    db.dentalimage.dicomPerformedDate.readable = False
    db.dentalimage.dicomURL.readable = False
  
    
    fields=(

        db.dentalimage.id,
        db.dentalimage.mediatype,
        db.dentalimage.title,
        db.dentalimage.imagedate,
        db.dentalimage.tooth,
        db.dentalimage.quadrant,
        db.dentalimage.description
      
    )

    headers={
        'dentalimage.id':'ID',
        'dentalimage.mediatype':'Media',

        'dentalimage.title':'Title',
        'dentalimage.imagedate':'Date',
        'dentalimage.tooth':'Tooth',
        'dentalimage.quadrant':'Quadrant',
        'dentalimage.description':'Description',
       
    }


    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, xml=False)




    links = [lambda row: A('View/Play/Update',_href=URL("media","update_media",vars=dict(page=page,mediaid=row.id))),
             lambda row: A('Delete',_href=URL("media","delete_media",vars=dict(page=page,mediaid=row.id)))
             ]
    
    if(mediatype == ''):
        query = ((db.dentalimage.id > 0) & ((db.dentalimage.mediatype == 'image') |(db.dentalimage.mediatype == 'audio') | (db.dentalimage.mediatype == 'video')) & (db.dentalimage.is_active == True))
    else:
        query = ((db.dentalimage.id > 0) & (db.dentalimage.mediatype == mediatype) & (db.dentalimage.is_active == True))
    maxtextlength = 40
    maxtextlengths = {'dentalimage.description':100}

    orderby = ~(db.dentalimage.id)    

    formB = SQLFORM.grid(query=query,
                         headers=headers,
                         fields=fields,
                         links=links,
                         maxtextlengths =maxtextlengths,
                         orderby=orderby,
                         exportclasses=exportlist,
                         links_in_grid=True,
                         searchable=True,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=False
                         )

    #return dict(formB = formB, username = username, formheader=formheader, page=page, returnurl = returnurl)    
    return dict(formB=formB,  page=page,\
            returnurl=returnurl,providername=providername, \
            providerid=providerid,memberid=memberid,patientid=patientid,patient=patient, \
            fullname=fullname               
            )    

def delete_media():
    
    
    mediaid = int(request.vars.mediaid)
    m = db((db.dentalimage.id == mediaid) & (db.dentalimage.is_active == True)).select()
    
    providerid = m[0].provider
    patientid = m[0].patient
    memberid = m[0].patientmember
    page=common.getpage1(request.vars.page)
    
    redirect(URL('media','list_media', vars=dict(page=page,providerid=providerid,patientid=patientid,memberid=memberid)))
    
    return dict()