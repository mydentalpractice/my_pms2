from gluon import current
db = current.globalenv['db']
#
from gluon.tools import Crud
crud = Crud(db)
import os
import json

import datetime

from applications.my_pms2.modules  import common

from applications.my_pms2.modules  import mdpmedia
from applications.my_pms2.modules import logger


#import sys
#sys.path.insert(0, 'modules')
from applications.my_pms2.modules import common
#from gluon.contrib import common

#This method will upload a DICOM Image file to 
#POSTDICOM server using their APIs
#It returns DICOM Patient Order and Viewing URL
def uploadDICOMImage():
    
    
    returnurl = request.vars.returnurl
    source = request.vars.source
    page = int(common.getid(request.vars.page))
    memberpage = int(common.getid(request.vars.memberpage))
    imagepage = int(common.getid(request.vars.imagepage))
    
    providername = request.vars.providername
    providerid = int(common.getid(request.vars.providerid))
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    treatmentid = int(common.getid(request.vars.treatmentid))
    r = db((db.vw_memberpatientlist.primarypatientid == memberid) &\
           (db.vw_memberpatientlist.patientid == patientid) &\
           (db.vw_memberpatientlist.providerid == providerid) &\
           (db.vw_memberpatientlist.is_active  == True)).select(\
            db.vw_memberpatientlist.patientmember,\
            db.vw_memberpatientlist.fullname,\
            db.vw_memberpatientlist.dob,\
            db.vw_memberpatientlist.gender
           )
    
    patientmember = "" if(len(r) == 0) else common.getstring(r[0].patientmember)
    patientname = "" if(len(r) == 0) else common.getstring(r[0].fullname)
    dob = "00/00/0000" if(len(r) == 0) else (r[0].dob).strftime("%d/%m/%Y")
    gender = "Male" if(len(r) == 0) else common.getstring(r[0].gender)
    
    t=db((db.vw_treatmentlist.id == treatmentid) &\
       (db.vw_treatmentlist.providerid == providerid)&\
       (db.vw_treatmentlist.is_active == True)).select(\
        db.vw_treatmentlist.treatment,\
        db.vw_treatmentlist.startdate
       )
    
    treatment = "" if(len(t) == 0) else common.getstring(t[0].treatment)
    treatmentdate = "00/00/0000" if(len(t) == 0) else (t[0].startdate).strftime("%d/%m/%Y")
    
    formA = SQLFORM.factory(
               Field('dicomUserUuid', 'string', default=""),
               Field('dicomAcctUuid', 'string', default=""),
               Field('dicomInstUuid', 'string', default=""),
                 
               Field('dicomPatName', 'string', default=""),
               Field('dicomPatUuid', 'string', default=""),
               Field('dicomPatid', 'string', default=""),
               Field('dicomPatOrderUuid', 'string', default=""),
               Field('dicomProcDesc', 'string', default=""),
               Field('dicomURL', 'string', default=""),
               
     )  
    
    dicomUserUuid = formA.element('#no_table_dicomUserUuid')
    dicomUserUuid['_class'] = 'form-control'
    
    dicomAcctUuid = formA.element('#no_table_dicomAcctUuid')
    dicomAcctUuid['_class'] = 'form-control'
    
    dicomInstUuid = formA.element('#no_table_dicomInstUuid')
    dicomInstUuid['_class'] = 'form-control'
    

    dicomPatName = formA.element('#no_table_dicomPatName')
    dicomPatName['_class'] = 'form-control'

    dicomPatUuid = formA.element('#no_table_dicomPatUuid')
    dicomPatUuid['_class'] = 'form-control'

    dicomPatid = formA.element('#no_table_dicomPatid')
    dicomPatid['_class'] = 'form-control'

    dicomPatOrderUuid = formA.element('#no_table_dicomPatOrderUuid')
    dicomPatOrderUuid['_class'] = 'form-control'

    dicomProcDesc = formA.element('#no_table_dicomProcDesc')
    dicomProcDesc['_class'] = 'form-control'

    dicomProcDesc = formA.element('#no_table_dicomProcDesc')
    dicomProcDesc['_class'] = 'form-control'

    dicomURL = formA.element('#no_table_dicomURL')
    dicomURL['_class'] = 'form-control'
    

    
    return dict(formA=formA,returnurl=returnurl,memberpage=memberpage,imagepage=imagepage,page=page,source=source,providername=providername,\
                memberid=memberid,patientid=patientid,providerid=providerid,treatmentid=treatmentid,\
                patientmember=patientmember,\
                patientname=patientname,\
                treatment=treatment,\
                treatmentdate=treatmentdate)


def patient_hide():
    return ''


def image_selector():
    is_active = True
    
    xpage=int(common.getid(request.vars.xpage))
    providerid = int(common.getid(request.vars.providerid))
    patientid = int(common.getid(request.vars.patientid))
    
    items_per_page = 4
    limitby = ((xpage)*items_per_page,(xpage+1)*items_per_page) 


    
    members = None
       
    activequery = ((db.dentalimage.image != None)&(db.dentalimage.image != "") & (db.dentalimage.is_active == is_active))
    
  
    
        
    if(providerid > 0):
        activequery = ((db.dentalimage.provider == providerid) & (activequery))
   
    
    if(patientid > 0):
        activequery = ((db.dentalimage.patient == patientid) & (activequery))
                    
    dsimages = None    

    if(limitby > 0):
        dsimages = db(activequery).select(
                                    db.dentalimage.id,db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                                    db.dentalimage.patienttype,db.dentalimage.patientname,db.dentalimage.description,db.dentalimage.is_active,db.vw_memberpatientlist.patientmember,\
                                    left=[db.vw_memberpatientlist.on(db.dentalimage.patient == db.vw_memberpatientlist.patientid)],\
                                          limitby=limitby, orderby = db.vw_memberpatientlist.patientmember | ~db.dentalimage.patienttype | ~db.dentalimage.id
                                )
    else:
        dsimages = db(activequery).select(
                                    db.dentalimage.id,db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                                    db.dentalimage.patienttype,db.dentalimage.patientname,db.dentalimage.description,db.dentalimage.is_active,db.vw_memberpatientlist.patientmember,\
                                    left=[db.vw_memberpatientlist.on(db.dentalimage.patient == db.vw_memberpatientlist.patientid)],\
                                          orderby = db.vw_memberpatientlist.patientmember | ~db.dentalimage.patienttype | ~db.dentalimage.id
                                )


    return dict(images=dsimages, page=xpage)    
    

    
    
def patient_selector():
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])    

    #if not request.vars.patientmember:
        #return ''
        
    if(request.vars.patientmember == ""):
        pattern = '%'
    else:
        pattern = request.vars.patientmember.capitalize() + '%'
        
    selected = [row.patient for row in db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patient.like(pattern)) & (db.vw_memberpatientlist.is_active == True) ).select()]
    selectedid = [row.id for row in db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patient.like(pattern)) & (db.vw_memberpatientlist.is_active == True) ).select()]
    
    s = ''.join([DIV(k,
                 _id = "selected",
                 _onclick="jQuery('#no_table_patientmember').val('%s') " % k,
                 _onmouseover="this.style.backgroundColor='yellow'",
                 _onmouseout="this.style.backgroundColor='white'"
                 ).xml() for k in selected])
    
    #s1 = ''.join([DIV(K,
                 #_onclick ="selected()",
                 #_id = "selection",
                 #_class="selection",
                 #_onmouseover="this.style.backgroundColor='orange'",
                 #_onmouseout="this.style.backgroundColor='white'"
                 #).xml() for K in selected])
                 
    #return ''.join([DIV(k,
                     #_onclick="jQuery('#no_table_patientmember').val('%s')" % k,
                     #_onmouseover="this.style.backgroundColor='yellow'",
                     #_onmouseout="this.style.backgroundColor='white'"
                     #).xml() for k in selected])                 

    s2 = s
    return s2
    



def getmembers(db,providerid, member,fname,lname,cell,email,limitby,is_active):
    
    members = None
    
    if(is_active == None):
        activequery = True
    else:
        activequery = ((db.vw_imagememberlist.is_active == is_active))
        
    if(providerid > 0):
        query = ((db.vw_imagememberlist.providerid == providerid) & (activequery))
    else:
        query = ((activequery))
    
    
    if(member != ""):
        query = query & (db.vw_imagememberlist.patientmember.contains(member))
    if(fname != ""):
        query = query & (db.vw_imagememberlist.fname.contains(fname))
    if(lname != ""):
        query = query & (db.vw_imagememberlist.lname.contains(lname))
    if(cell != ""):
        query = query & (db.vw_imagememberlist.cell.contains(cell))
    if(email != ""):
        query = query & (db.vw_imagememberlist.email.contains(email))
    
  
    
    dsmembers = db(query).select(db.vw_imagememberlist.id,db.vw_imagememberlist.patientid,db.vw_imagememberlist.primarypatientid, db.vw_imagememberlist.patientmember, \
                                 db.vw_imagememberlist.fname, db.vw_imagememberlist.lname,db.vw_imagememberlist.patienttype,\
                                 db.vw_imagememberlist.cell,db.vw_imagememberlist.email,db.vw_imagememberlist.providerid,
                                 limitby=limitby, orderby = db.vw_imagememberlist.patientmember | ~db.vw_imagememberlist.patienttype
                                 
                                 )
    
        
    return dsmembers

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def getimagemembers(db,providerid, memberid, member,fname,lname,cell,email,fromdt,todt,limitby,is_active):
    
    members = None
    
    if(is_active == None):
        activequery = True
    else:
        activequery = ((db.vw_imagememberlist.is_active == is_active) & (db.dentalimage.is_active == is_active))
        
    if(providerid > 0):
        query = ((db.dentalimage.provider == providerid) & (db.vw_imagememberlist.providerid == providerid) & (activequery))
    else:
        query = ((activequery))
    
    if(memberid > 0):
        query = ((db.dentalimage.provider == providerid) & (db.vw_imagememberlist.providerid == providerid) & (db.vw_imagememberlist.primarypatientid == memberid) & (activequery))
    
    if(member != ""):
        query = query & (db.vw_imagememberlist.patientmember.contains(member))
    if(fname != ""):
        query = query & (db.vw_imagememberlist.fname.contains(fname))
    if(lname != ""):
        query = query & (db.vw_imagememberlist.lname.contains(lname))
    if(cell != ""):
        query = query & (db.vw_imagememberlist.cell.contains(cell))
    if(email != ""):
        query = query & (db.vw_imagememberlist.email.contains(email))
    if(fromdt != ""):
        query = query & (db.dentalimage.imagedate >= fromdt)
    if(todt != ""):
        query = query & (db.dentalimage.imagedate <= todt)

    query = query & ((db.dentalimage.image != None)&(db.dentalimage.image != ""))
    
    #dsmembers = db(query).select(db.vw_imagememberlist.id,db.vw_imagememberlist.primarypatientid, db.vw_imagememberlist.patientmember, \
                                 #db.vw_imagememberlist.fname, db.vw_imagememberlist.lname,db.vw_imagememberlist.patienttype,\
                                 #db.vw_imagememberlist.cell,db.vw_imagememberlist.email,db.vw_imagememberlist.providerid,
                                 #limitby=limitby, orderby = db.vw_imagememberlist.patientmember | ~db.vw_imagememberlist.patienttype
                                 
                                 #)
    
    #dsmembers = db(query).select(db.vw_imagememberlist.id,db.vw_imagememberlist.primarypatientid, db.vw_imagememberlist.patientmember, \
                                 #db.vw_imagememberlist.fname, db.vw_imagememberlist.lname,db.vw_imagememberlist.patienttype,\
                                 #db.vw_imagememberlist.cell,db.vw_imagememberlist.email,db.vw_imagememberlist.providerid,\
                                 #db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                                 #db.dentalimage.patientmember,db.dentalimage.patient,db.dentalimage.patienttype,db.dentalimage.patientname,
                                 #left=[db.dentalimage.on(db.dentalimage.patientmember == db.vw_imagememberlist.primarypatientid)],
                                       #limitby=limitby, orderby = db.vw_imagememberlist.patientmember | ~db.vw_imagememberlist.patienttype
                                 

                                 #)
    dsimages = None
                                 
    if(limitby > 0):
        dsimages = db(query).select(
                                    db.dentalimage.id,db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                                    db.dentalimage.patientmember,db.dentalimage.patient,db.dentalimage.patienttype,db.dentalimage.patientname,db.dentalimage.provider,db.dentalimage.description,db.dentalimage.is_active,\
                                    db.vw_imagememberlist.patientid,db.vw_imagememberlist.primarypatientid, db.vw_imagememberlist.patientmember, \
                                    db.vw_imagememberlist.fname, db.vw_imagememberlist.lname,db.vw_imagememberlist.patienttype,\
                                    db.vw_imagememberlist.cell,db.vw_imagememberlist.email,db.vw_imagememberlist.providerid,\
                                    left=[db.vw_imagememberlist.on((db.dentalimage.patientmember == db.vw_imagememberlist.primarypatientid)&(db.dentalimage.patient == db.vw_imagememberlist.patientid))],\
                                          limitby=limitby, orderby = db.vw_imagememberlist.patientmember | ~db.vw_imagememberlist.patienttype | ~db.dentalimage.id
                                )
    else:
        dsimages = db(query).select(
                                    db.dentalimage.id,db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                                    db.dentalimage.patientmember,db.dentalimage.patient,db.dentalimage.patienttype,db.dentalimage.patientname,db.dentalimage.provider,db.dentalimage.description,db.dentalimage.is_active,\
                                    db.vw_imagememberlist.patientid,db.vw_imagememberlist.primarypatientid, db.vw_imagememberlist.patientmember, \
                                    db.vw_imagememberlist.fname, db.vw_imagememberlist.lname,db.vw_imagememberlist.patienttype,\
                                    db.vw_imagememberlist.cell,db.vw_imagememberlist.email,db.vw_imagememberlist.providerid,\
                                    left=[db.vw_imagememberlist.on((db.dentalimage.patientmember == db.vw_imagememberlist.primarypatientid)&(db.dentalimage.patient == db.vw_imagememberlist.patientid))],\
                                          orderby = db.vw_imagememberlist.patientmember | ~db.vw_imagememberlist.patienttype | ~db.dentalimage.id
                                    )
        
    return dsimages




@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def getimages(db,providerid, patientid,limitby,is_active):
    
    if(patientid == 0):
        dsimages = db(db.dentalimage.patient == 0).select()
    else:
        activequery = ((((db.dentalimage.image != None)) | ((db.dentalimage.dicomURL != None))) & (db.dentalimage.is_active == is_active))
        #activequery = ((((db.dentalimage.image != None)&(db.dentalimage.image != "")) | ((db.dentalimage.dicomURL != None)&(db.dentalimage.dicomURL != ""))) & (db.dentalimage.is_active == is_active))        
        if(providerid > 0):
            activequery = ((db.dentalimage.provider == providerid) & (activequery))
        
        if(patientid > 0):
            activequery = ((db.dentalimage.patient == patientid) & (activequery))
                        
        dsimages = None
                                     
        if(limitby > 0):
            dsimages = db(activequery).select(
                                        db.dentalimage.id,db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                                        db.dentalimage.dicomURL,db.dentalimage.dicomUserUuid,db.dentalimage.dicomPatOrderUuid,db.dentalimage.dicomPerformedDate,db.dentalimage.dicomProcDesc,db.dentalimage.dicomPatName,\
                                        db.dentalimage.patienttype,db.dentalimage.patientname,db.dentalimage.description,db.dentalimage.is_active,db.vw_memberpatientlist.patientmember,\
                                        left=[db.vw_memberpatientlist.on(db.dentalimage.patient == db.vw_memberpatientlist.patientid)],\
                                              limitby=limitby, orderby = db.vw_memberpatientlist.patientmember | ~db.dentalimage.patienttype | ~db.dentalimage.id
                                    )
        else:
            dsimages = db(activequery).select(
                                        db.dentalimage.id,db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                                        db.dentalimage.dicomURL,db.dentalimage.dicomUserUuid,db.dentalimage.dicomPatOrderUuid,db.dentalimage.dicomPerformedDate,db.dentalimage.dicomProcDesc,db.dentalimage.dicomPatName,\
                                        db.dentalimage.patienttype,db.dentalimage.patientname,db.dentalimage.description,db.dentalimage.is_active,db.vw_memberpatientlist.patientmember,\
                                        left=[db.vw_memberpatientlist.on(db.dentalimage.patient == db.vw_memberpatientlist.patientid)],\
                                              orderby = db.vw_memberpatientlist.patientmember | ~db.dentalimage.patienttype | ~db.dentalimage.id
                                )
        
    return dsimages


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_memberpatientimages():



    provdict = common.getprovider(auth, db)
    providerid = provdict["providerid"]
    providername = provdict["providername"]
    page     = int(common.getpage(request.vars.page))
    memberpage = int(common.getpage(request.vars.memberpage))
    memberid = int(common.getid(request.vars.memberid))
        
    returnurl = URL('member', 'list_members', vars=dict(page=memberpage,providerid=providerid, providername=providername))    
    

    query = ((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.is_active == True) )
    
    fields=(db.vw_memberpatientlist.fullname,db.vw_memberpatientlist.patientmember)    
    
    headers={
            'vw_memberpatientlist.patientmember':'Member ID',
            'vw_memberpatientlist.fullname':'Fullname Name',
            }
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
    
    
        
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
    
   
    links = [
             dict(header='Image',body=lambda row: A(IMG(_src="/my_pms2/static/img/png/021-xray.png",_width=30, _height=30),\
                                                    _href=URL("dentalimage","list_dentalimages",\
                                                              vars=dict(memberpage=page,page=0,memberid=memberid,patientid=row.id,providerid=providerid,providername=providername))))
             ]

    
    orderby = None

    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            orderby=orderby,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            searchable=False,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                           
                            user_signature=True
                           )
  
    
    return dict(form = form, memberpage=memberpage, returnurl=returnurl,page=page,providerid=providerid,providername=providername)
    




@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_dentalimages():

    is_active    = True
   
    memberpage   = int(common.getpage(request.vars.memberpage))
    page         = int(common.getpage(request.vars.page))
    
    
    providerid   = int(common.getnegid(request.vars.providerid))
    provdict     = common.getproviderfromid(db, request.vars.providerid)
    providername = provdict["providername"]
    
    memberid     = int(common.getid(request.vars.memberid))
    patientid    = int(common.getid(request.vars.patientid))
    
    memberref    = common.getstring(request.vars.memberref)
    
    patient = common.getstring(request.vars.patient)
    fullname = common.getstring(request.vars.fullname)
    
    #display treatment plan filtering criteria
    items_per_page = 4
    limitby = ((page)*items_per_page,(page+1)*items_per_page)     

    rows = None
    if(memberid > 0):
        if(patientid > 0):
            sqlquery = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.is_active == True))
            rows = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.is_active == True)).select()
            if(len(rows) > 0):
                fullname = common.getstring(rows[0].fullname)
                patient = common.getstring(rows[0].patient)
                memberid = int(common.getid(rows[0].primarypatientid))
        else:
            sqlquery = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == memberid) & (db.vw_memberpatientlist.is_active == True))
            rows = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == memberid) & (db.vw_memberpatientlist.is_active == True)).select()
            if(len(rows) > 0):
                fullname = common.getstring(rows[0].fullname)
                patient = common.getstring(rows[0].patient)
                memberid = int(common.getid(rows[0].primarypatientid))
                patientid = memberid
            
    else:
        sqlquery = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True))
        rows = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).select()
    
    form = SQLFORM.factory(
               Field('patientmember', 'string',  default=fullname, label='Patient'),
               Field('xmemberid', 'string',  label='Patient ID',default=memberid),
               Field('xpatientmember', 'string', default=patient, label='XPatient'),
               Field('xfullname', 'string', default=fullname, label='XPatient')
               
    )
       
    xpatientmember = form.element('#no_table_patientmember')
    xpatientmember['_class'] = 'form-control'
    xpatientmember['_placeholder'] = 'Enter First Name Last Name, Cell, Email'
    xpatientmember['_autocomplete'] = 'off' 

    if form.accepts(request,session,keepvalues=True):
        memberid = 0
        patientid = 0

        limitby = ((page)*items_per_page,(page+1)*items_per_page) 
        r = db((db.vw_memberpatientlist.patient == form.vars.xpatientmember.strip()) & (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).select()
        if(len(r) > 0):
            memberid = int(common.getid(r[0].primarypatientid))
            patientid = int(common.getid(r[0].patientid))
            memberref = common.getstring(r[0].patientmember)  #patientmember
            fullname = common.getstring(r[0].fullname)      #fname + lname
            patient = common.getstring(r[0].patient)    #fname + lname + patientmemebr
            
    
    images = getimages(db, providerid, patientid, limitby, is_active)    
    imagescount = len(images)
    totalimages  = 0
    
    if(patientid > 0):
        totalimages = db((db.dentalimage.provider == providerid) & (db.dentalimage.patient == patientid) & (db.dentalimage.image != None) & (db.dentalimage.image != "") &\
                         (db.dentalimage.is_active == True)).count()
    else:
        totalimages = db((db.dentalimage.provider == providerid) & (db.dentalimage.image != None) & (db.dentalimage.image != "") &\
                         (db.dentalimage.is_active == True)).count()    
    session.images = totalimages
    
    
    if(len(images) > 0):
        rangemssg = "Displaying images from  " + str(int(common.getvalue(limitby[0]))+1) + "  to  " + str(int(common.getvalue(limitby[1]))) + "(" + str(totalimages) + ")"
    else:
        rangemssg = "No images to display"

    if(memberpage == 0)    :
        returnurl =  URL('admin','providerhome')    
    else:    
        if(session.nonmemberscount == True):
            returnurl =  URL('member','list_nonmembers', vars=dict(providerid=providerid,page=memberpage))    
        else:
            returnurl =  URL('member','list_members', vars=dict(providerid=providerid,page=memberpage))    
    
    
    return dict(form=form, images=images, returnurl=returnurl, page=page, items_per_page=items_per_page, limitby=limitby, rangemssg=rangemssg,memberpage=memberpage, memberid=memberid, patientid=patientid, memberref=memberref,fullname=fullname,providerid=providerid, providername=providername,patient=patient)




def dentalimage_upload():
    
    
    formA = SQLFORM(db.dentalimage,request.args(0))
      
    if formA.accepts(request.vars,session):    #formA.process().accepted
        if not formA.record:
            response.flash = 'record.created'
        else:
            redirect(r=request,f='dentalimage_upload')
    elif formA.errors:
        response.flash = 'form has errors '  + str(formA.errors)
    
    dsimages = db().select(db.dentalimage.ALL, orderby=~db.dentalimage.id)        
    return dict( formA=formA,dsimages=dsimages)    
    
    


def download():
    return response.download(request, db)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def dentalimage_update():
    
    if(len(request.vars) == 0):
        raise HTTP(403,"Error: No dental image to  update : dentalimage_update()")

    page         = int(common.getpage(request.vars.xpage))
    memberpage   = int(common.getpage(request.vars.xmemberpage))
    
    providerid   = int(common.getnegid(request.vars.xproviderid))
    patientid   = int(common.getnegid(request.vars.xpatientid))
    memberid   = int(common.getnegid(request.vars.xmemberid))
    memberref   = common.getstring(request.vars.xmemberref)
    patient    = common.getstring(request.vars.xpatient)
    
    
    
    title  = common.getstring(request.vars.form_title)
    tooth  = common.getstring(request.vars.form_tooth)
    quadrant  = common.getstring(request.vars.form_quadrant)
    imageid   = int(common.getid(request.vars.form_imageid))
    imagedate   = common.getnulldt( datetime.strptime(request.vars.form_imagedate, '%d/%m/%Y'))
    patientname     = common.getstring(request.vars.form_patientname)
    description     = common.getstring(request.vars.form_description)
    
    is_active    = True
    if(common.getstring(request.vars.form_delete) == "on"):
        is_active  = False    
    
    retid = db(db.dentalimage.id == imageid).update(title = title,tooth = tooth,
                                            quadrant = quadrant,
                                            patientname = patientname,
                                            imagedate = imagedate,
                                            description = description,
                                            is_active = is_active
                                            )
    
    redirect(URL('dentalimage','list_dentalimages', vars = dict(page=page,memberpage=memberpage,providerid=providerid,memberid=memberid,patientid=patientid,memberref=memberref,patient=patient,fullname=patientname)))



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def xdentalimage_add():
    
    
    provdict = common.getproviderfromid(db, request.vars.providerid)
    
    providerid = int(common.getid(request.vars.providerid))
    page       = common.getgridpage(request.vars)    
    memberref  = common.getstring(request.vars.memberref)
    fname      = common.getstring(request.vars.fname)
    lname      = common.getstring(request.vars.lname)
    cell       = common.getstring(request.vars.cell)
    email      = common.getstring(request.vars.email)
    memberid   = int(common.getid(request.vars.memberid))
    
    #display treatment plan filtering criteria
    items_per_page = 5
    limitby = (page*items_per_page,(page+1)*items_per_page+1) 
    
    #display list of treatment plans
    form = SQLFORM.factory(
            Field('memberref','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small'),label='Member', default=memberref),
            Field('fname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small'),label='First Name', default=fname),
            Field('lname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small'),label='Last Name', default=lname),
            Field('cell', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small'),label='Cell Phone',  default=cell ),
            Field('email', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small'), label='Email',  default=email )
            )
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Search'    
    
    dsmembers = getmembers(db,providerid,memberref,fname,lname,cell,email,limitby,True)
    
    
    
    if form.accepts(request,session,keepvalues=True):
        
        
        memberref     = common.getstring(form.vars.memberref)
        fname      = common.getstring(form.vars.fname)
        lname      = common.getstring(form.vars.lname)
        cell       = common.getstring(form.vars.cell)
        email       = common.getstring(form.vars.email)
        
        dsmembers = getmembers(db,providerid,memberref, fname,lname,cell,email,limitby,True)
        
    elif form.errors:
        response.flash = 'form has errors ' + str(form.errors)        
    
    returnurl =  URL('dentalimage','list_dentalimages', vars=dict(page=page,providerid=providerid,memberid=memberid,memberref=memberref))
    
    return dict(dsmembers=dsmembers,providername=provdict["providername"],form=form,providerid=provdict["providerid"],\
                memberref=memberref,fname=fname,lname=lname,cell=cell,email=email,page=page,items_per_page=items_per_page,\
                returnurl=returnurl)    
    


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def dentalimage_add():
    
    page = 1
    session.nonmemberscount=False
    provdict = common.getprovider(auth, db)
    providerid = provdict["providerid"]
    providername = provdict["providername"]
    imagepage=common.getpage(request.vars.imagepage)    
    memberpage=common.getpage(request.vars.memberpage)
    
    
    memberid = int(common.getid(request.vars.memberid))
    memberref  = common.getstring(request.vars.memberref)
    
    if(memberid > 0):
        r = db(db.patientmember.id == memberid).select()
        memberref= common.getstring(r[0].patientmember)


   
    returnurl = URL('dentalimage', 'list_dentalimages', vars=dict(providerid = providerid,memberid=memberid,page=imagepage,memberpage=memberpage,memberref=memberref))
    
    if(memberid>0):
        query = ((db.vw_imagememberlist.providerid == providerid) & (db.vw_imagememberlist.primarypatientid == memberid) &(db.vw_imagememberlist.is_active == True))
    else:
        query = ((db.vw_imagememberlist.providerid == providerid) & (db.vw_imagememberlist.is_active == True))



    
    fields=(db.vw_imagememberlist.patientid,db.vw_imagememberlist.primarypatientid, db.vw_imagememberlist.patientmember,db.vw_imagememberlist.fname,\
            db.vw_imagememberlist.lname,db.vw_imagememberlist.patienttype,db.vw_imagememberlist.cell,db.vw_imagememberlist.email)    
    
  
    headers={
            'vw_imagememberlist.patientmember':'Member ID',
            'vw_imagememberlist.patienttype':'P/D',
            'vw_imagememberlist.fname':'First Name',
            'vw_imagememberlist.lname':'Last Name',
            'vw_imagememberlist.cell':'Cell',
            'vw_imagememberlist.email':'Email'
            }
 
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
    db.vw_imagememberlist.patientid.readable = False
    db.vw_imagememberlist.providerid.readable = False
    db.vw_imagememberlist.is_active.readable = False
    db.vw_imagememberlist.primarypatientid.readable = False 
        
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
    
    links = [
             dict(header='New Image',body=lambda row: A(IMG(_src="/my_pms2/static/img/png/008-picture.png",_width=30, _height=30),\
                                    _href=URL('dentalimage','dentalimage_new',vars=dict(memberpage=memberpage,imagepage=imagepage,page=page,providerid=providerid,memberref=memberref,memberid=row.primarypatientid,patientid=row.patientid))))
             ]
    orderby = (db.vw_imagememberlist.patientmember|~db.vw_imagememberlist.patienttype)

    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            orderby = orderby,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            searchable=True,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            user_signature=True
                           )
    
    
 
    
    return dict(form = form, returnurl=returnurl,page=page,providerid=providerid,providername=providername)
        
@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def dentalimage_new():
    
    if(len(request.vars) == 0):
        raise HTTP(403,"Error in create_image -  request arguments " )
    
    source = common.getstring(request.vars.source)
    page     = 0 
    imagepage = common.getpage(request.vars.imagepage)
    memberpage = common.getpage(request.vars.memberpage)
    providerid  = int(common.getid(request.vars.providerid))
    patientid   = int(common.getid(request.vars.patientid))
    
   
    memberid    = int(common.getid(request.vars.memberid))    
    memberref   = common.getstring(request.vars.memberref)
    
    members = db(db.patientmember.id == memberid).select()
    memberref = common.getstring(members[0].patientmember)
    
    providerdict = common.getproviderfromid(db, providerid)
    providername = providerdict["providername"]
    treatmentid = int(common.getid(request.vars.treatmentid))
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
        returnurl = URL('dentalimage', 'list_dentalimages', vars=dict(providerid = providerid,memberid=memberid,patientid=patientid,page=page,memberref=memberref,imagepage=imagepage,memberpage=memberpage))
    
   
        #Table: media
        #Columns:
       
        # varchar(255) 
        # varchar(1024) 
        # varchar(20) 
        # varchar(20) 
        # date 
        # longtext 
        # int(11) 
        # int(11) 
        # int(11) 
        # int(11) 
        # varchar(45) 
        # varchar(45) 
        # int(11) 
        # varchar(1024) 
        # varchar(45) 
        # varchar(45) 
        # double 
        #is_active char(1) 
        #created_on datetime 
        #created_by int(11) 
        #modified_on datetime 
        #modified_by int(11) 
        #dicomUserUuid varchar(128) 
        #dicomAcctUuid varchar(128) 
        #dicomInstUuid varchar(128) 
        #dicomPatName varchar(128) 
        #dicomPatUuid varchar(128) 
        #dicomPatid varchar(128) 
        #dicomPatOrderUuid varchar(128) 
        #dicomProcDesc varchar(128) 
        #dicomPerformedDate varchar(128) 
        #dicomURL varchar(255)    

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
   
        Field('dicomUserUuid','string'),
        Field('dicomAcctUuid','string'),
        Field('dicomInstUuid','string'),
        Field('dicomPatName','string'),
        Field('dicomPatUuid','string'),
        Field('dicomPatid','string'),
        Field('dicomPatOrderUuid','string'),
        Field('dicomProcDesc','string'),
        Field('dicomPerformedDate','string'),
        Field('dicomURL','string'),




        Field('mediasize','double'),

        Field('imagedata','text', length=50e+7, label='Image Data')
        
    
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
    
    dicomUserUuid = formA.element('#no_table_dicomUserUuid')
    dicomUserUuid['_class'] = 'form-control'
    dicomUserUuid['_readonly'] = True



    dicomAcctUuid = formA.element('#no_table_dicomAcctUuid')
    dicomAcctUuid['_class'] = 'form-control'
    dicomAcctUuid['_readonly'] = True

    dicomInstUuid = formA.element('#no_table_dicomInstUuid')
    dicomInstUuid['_class'] = 'form-control'
    dicomInstUuid['_readonly'] = True


    dicomPatName = formA.element('#no_table_dicomPatName')
    dicomPatName['_class'] = 'form-control'
    dicomPatName['_readonly'] = True

    dicomPatUuid = formA.element('#no_table_dicomPatUuid')
    dicomPatUuid['_class'] = 'form-control'
    dicomPatUuid['_readonly'] = True

    dicomPatid = formA.element('#no_table_dicomPatid')
    dicomPatid['_class'] = 'form-control'
    dicomPatid['_readonly'] = True

    dicomPatOrderUuid = formA.element('#no_table_dicomPatOrderUuid')
    dicomPatOrderUuid['_class'] = 'form-control'
    dicomPatOrderUuid['_readonly'] = True

    dicomProcDesc = formA.element('#no_table_dicomProcDesc')
    dicomProcDesc['_class'] = 'form-control'
    dicomProcDesc['_readonly'] = True

    dicomPerformedDate = formA.element('#no_table_dicomPerformedDate')
    dicomPerformedDate['_class'] = 'form-control'
    dicomPerformedDate['_readonly'] = True


    dicomURL = formA.element('#no_table_dicomURL')
    dicomURL['_class'] = 'form-control'    
    dicomURL['_readonly'] = True
        
    error = ""
    count = 0
    mediaurl = ""
    mediafile = ""
    mediaid = 0

    if formA.accepts(request,session,keepvalues=True):
        
        try:
            logger.loggerpms2.info("file content \n" + str(len(request.vars.imagedata)))
            #upload image
            if(len(request.vars.imagedata)>0):
                
                file_content = None
                file_content = request.vars.imagedata
                o = mdpmedia.Media(db, providerid, 'image', 'jpg')
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
                    "appath":request.folder
                }
                 
                x= json.loads(o.upload_media(j)) 
                     
                mediaid = common.getkeyvalue(x,'mediaid',0)
                mediaurl = URL('my_dentalplan','media','media_download',\
                               args=[mediaid])  
                
            #save DICOM values
            db(db.dentalimage.id == mediaid).update(
                dicomUserUuid = formA.vars.dicomUserUuid,
                dicomAcctUuid = formA.vars.dicomAcctUuid,
                dicomInstUuid = formA.vars.dicomInstUuid,
                dicomPatName = formA.vars.dicomPatName,
                dicomPatUuid = formA.vars.dicomPatUuid,
                dicomPatid = formA.vars.dicomPatid,
                dicomPatOrderUuid = formA.vars.dicomPatOrderUuid,
                dicomProcDesc = formA.vars.dicomProcDesc,
                dicomPerformedDate = formA.vars.dicomPerformedDate,
                dicomURL = formA.vars.dicomURL
            )
        except Exception as e:
            error = "Upload Audio Exception Error - " + str(e)             
    elif formA.errors:
        error = str(formA.errors)
    else:
        i = 0
        
    return dict(formA=formA, returnurl=returnurl, providername=providername,memberid=memberid, memberref=memberref, providerid=providerid,membername=membername,patientname=patientname,dspatients=dspatients,treatmentid=treatmentid, tplanid=tplanid, tplan=tplan,page=page,patientid=patientid,memberpage=memberpage,imagepage=imagepage,source=source,error=error,count=count,mediafile=mediafile,mediaurl=mediaurl)   



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def xdentalimage_new():
    
    if(len(request.vars) == 0):
        raise HTTP(403,"Error in create_image -  request arguments " )
    
    source = common.getstring(request.vars.source)
    page     = 0 
    imagepage = common.getpage(request.vars.imagepage)
    memberpage = common.getpage(request.vars.memberpage)
    providerid  = int(common.getid(request.vars.providerid))
    patientid   = int(common.getid(request.vars.patientid))
    
   
    memberid    = int(common.getid(request.vars.memberid))    
    memberref   = common.getstring(request.vars.memberref)
    
    members = db(db.patientmember.id == memberid).select()
    memberref = common.getstring(members[0].patientmember)
    
    providerdict = common.getproviderfromid(db, providerid)
    providername = providerdict["providername"]
    treatmentid = int(common.getid(request.vars.treatmentid))
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
    
   


    ## Add PO form - 
    crud.settings.keepvalues = True
    crud.settings.showid = True
    
    strSQL = "select 0, '' AS patienttype, '-Select-' as fname, '' as lname"    
    strSQL = strSQL + " UNION "
    strSQL = strSQL + " select id , 'P' AS patienttype,fname,lname from patientmember where id = " + str(memberid)
    strSQL = strSQL + " UNION "
    strSQL = strSQL + " select id,'D' AS patienttype, patientmemberdependants.fname,patientmemberdependants.lname from patientmemberdependants where  patientmemberdependants.patientmember = " + str(memberid)
    dspatients = db.executesql(strSQL)    
   
    
    if(source == "treatment"):
        returnurl = URL('treatment', 'update_treatment', vars=dict(page=page,imagepage=0,providerid=providerid,treatmentid=treatmentid))
    else:
        returnurl = URL('dentalimage', 'list_dentalimages', vars=dict(providerid = providerid,memberid=memberid,patientid=patientid,page=page,memberref=memberref,imagepage=imagepage,memberpage=memberpage))
    
    formA = crud.create(db.dentalimage, next=returnurl, message="New Image Added!")  ## Image
    
    
    
    
    formA.element('textarea[name=description]')['_style'] = 'height:50px;line-height:1.0;'
    formA.element('textarea[name=description]')['_rows'] = 5   
    formA.element('textarea[name=description]')['_cols'] = 50
    formA.element('textarea[name=description]')['_class'] = 'form-control'
    
    
    xtitle = formA.element('#dentalimage_title')
    xtitle['_class'] = 'form-control'
    xtitle['_placeholder'] = 'Title'
    xtitle['_autocomplete'] = 'off'   
    
    xtooth = formA.element('#dentalimage_tooth')
    xtooth['_class'] = 'form-control'
    xtooth['_placeholder'] = 'Tooth'
    xtooth['_autocomplete'] = 'off'   
    
    xquad = formA.element('#dentalimage_quadrant')
    xquad['_class'] = 'form-control'
    xquad['_placeholder'] = 'Quadrant'
    xquad['_autocomplete'] = 'off'   
    
    xdate = formA.element('#dentalimage_imagedate')
    xdate['_class'] = 'input-group form-control form-control-inline date-picker'
    xdate['_placeholder'] = 'Date'
    xdate['_autocomplete'] = 'off'   
    
    
    dicomUserUuid = formA.element('#dentalimage_dicomUserUuid')
    dicomUserUuid['_class'] = 'form-control'
    dicomUserUuid['_readonly'] = True
    

    
    dicomAcctUuid = formA.element('#dentalimage_dicomAcctUuid')
    dicomAcctUuid['_class'] = 'form-control'
    dicomAcctUuid['_readonly'] = True
      
    dicomInstUuid = formA.element('#dentalimage_dicomInstUuid')
    dicomInstUuid['_class'] = 'form-control'
    dicomInstUuid['_readonly'] = True
    

    dicomPatName = formA.element('#dentalimage_dicomPatName')
    dicomPatName['_class'] = 'form-control'
    dicomPatName['_readonly'] = True

    dicomPatUuid = formA.element('#dentalimage_dicomPatUuid')
    dicomPatUuid['_class'] = 'form-control'
    dicomPatUuid['_readonly'] = True

    dicomPatid = formA.element('#dentalimage_dicomPatid')
    dicomPatid['_class'] = 'form-control'
    dicomPatid['_readonly'] = True

    dicomPatOrderUuid = formA.element('#dentalimage_dicomPatOrderUuid')
    dicomPatOrderUuid['_class'] = 'form-control'
    dicomPatOrderUuid['_readonly'] = True

    dicomProcDesc = formA.element('#dentalimage_dicomProcDesc')
    dicomProcDesc['_class'] = 'form-control'
    dicomProcDesc['_readonly'] = True

    dicomPerformedDate = formA.element('#dentalimage_dicomPerformedDate')
    dicomPerformedDate['_class'] = 'form-control'
    dicomPerformedDate['_readonly'] = True


    dicomURL = formA.element('#dentalimage_dicomURL')
    dicomURL['_class'] = 'form-control'    
    dicomURL['_readonly'] = True

    if formA.accepts(request,session,keepvalues=True):
        i = 0
       
    
    formB = SQLFORM.factory(
        #Field('csvfile','string',label='CSV File'),
        Field('imagedata','text',label='Image Data')
    )    
    submit = formB.element('input',_type='submit')
    submit['_value'] = 'Import'    
    
    error = ""
    count = 0
    mediaurl = ""
    mediafile = ""
    if formB.accepts(request,session,keepvalues=True):
        try:
            file_content = None
            file_content = request.vars.imagedata
            o = mdpmedia.Media(db, 523, 'image', 'jpg')
            j = {
                "mediadata":file_content,
                "memberid":str(1469),
                "patientid":str(1469),
                "treatmentid":str(24),
                "title":"test",
                "tooth":"1",
                "quadrant":"1",
                "mediadate":common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y"),
                "description":"XXX",
                "appath":request.folder
            }

            x= json.loads(o.upload_media(j)) 

            mediaid = common.getkeyvalue(x,'mediaid',0)
            mediaurl = URL('my_dentalplan','media','media_download',\
                           args=[mediaid])


        except Exception as e:
            error = "Upload Audio Exception Error - " + str(e)             
    elif formB.errors:
        str1 = str(formB.errors)
        response.flash = 'form has errors'
        i = 0
        
    return dict(formA=formA, formB=formB, returnurl=returnurl, providername=providername,memberid=memberid, memberref=memberref, providerid=providerid,membername=membername,patientname=patientname,dspatients=dspatients,treatmentid=treatmentid, tplanid=tplanid, tplan=tplan,page=page,patientid=patientid,memberpage=memberpage,imagepage=imagepage,source=source,error=error,count=count,mediafile=mediafile,mediaurl=mediaurl)   


@auth.requires(auth.has_membership('provider')) 
@auth.requires_login()
def dentalimage_show():
    
    page = 1
    
    imageid  = int(common.getid(request.args[0]))
    imagepage = common.getpage(request.args[1])
    memberpage = common.getpage(request.args[2])
    
    provdict = common.getprovider(auth, db)
    providerid = provdict["providerid"]
    providername = provdict["providername"]    

  
    
    memberid  = 0
    patientid = 0
    memberref = ""
    imagefile = None
    membername = ""
    images  = db((db.dentalimage.id == imageid) & (db.dentalimage.is_active == True)).select()
    if(len(images)>0):
        imagefile = images[0].image
        memberid = images[0].patientmember
        patientid = images[0].patient
        patientname = images[0].patientname
        patienttype = images[0].patienttype
        members = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select()
        memberref = members[0].patientmember
        membername = members[0].fname + ' ' + members[0].mname + ' ' + members[0].lname
   

    
    #set dentalimage default values
    db.dentalimage.treatmentplan.default = 0
    db.dentalimage.treatmentplan.writable = False
    db.dentalimage.treatment.default = 0
    db.dentalimage.treatment.writable = False    
    db.dentalimage.patientmember.default = memberid
    db.dentalimage.patientmember.writable = False    
    db.dentalimage.patient.default = patientid
    
    db.dentalimage.patienttype.default = patienttype

  
      
    rows = db((db.provider.id == providerid)& (db.provider.is_active == True)).select()
    provider = rows[0].provider
    
    strSQL = "select 0, '' AS patienttype, '-Select-' as fname, '' as lname"    
    strSQL = strSQL + " UNION "
    strSQL = strSQL + " select id , 'P' AS patienttype,fname,lname from patientmember where id = " + str(memberid)
    strSQL = strSQL + " UNION "
    strSQL = strSQL + " select id,'D' AS patienttype, patientmemberdependants.fname,patientmemberdependants.lname from patientmemberdependants where  patientmemberdependants.patientmember = " + str(memberid)
    dspatients = db.executesql(strSQL)    
  
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('dentalimage', 'list_dentalimages', vars=dict(providerid = providerid,memberid=memberid,patientid=patientid,memberref=memberref,page=page,memberpage=memberpage,imagepage=imagepage))
    
    formA = crud.update(db.dentalimage, imageid, cast=int, message = "Image Updated!")  ## Image
    
    formA.element('textarea[name=description]')['_style'] = 'height:50px;line-height:1.0;'
    formA.element('textarea[name=description]')['_rows'] = 5   
    
    

    xtitle = formA.element('#dentalimage_title')
    xtitle['_class'] = 'form-control'
    xtitle['_placeholder'] = 'Title'
    xtitle['_autocomplete'] = 'off'   
    
    xtooth = formA.element('#dentalimage_tooth')
    xtooth['_class'] = 'form-control'
    xtooth['_placeholder'] = 'Tooth'
    xtooth['_autocomplete'] = 'off'   
    
    xquad = formA.element('#dentalimage_quadrant')
    xquad['_class'] = 'form-control'
    xquad['_placeholder'] = 'Quadrant'
    xquad['_autocomplete'] = 'off'   
    
    xdate = formA.element('#dentalimage_imagedate')
    xdate['_class'] = 'input-group form-control form-control-inline date-picker'
    xdate['_placeholder'] = 'Date'
    xdate['_autocomplete'] = 'off' 
    
    
    returnurl = URL('dentalimage', 'list_dentalimages', vars=dict(providerid = providerid,memberid=memberid,patientid=patientid,memberref=memberref,page=page,memberpage=memberpage,imagepage=imagepage))

    return dict(formA=formA, returnurl=returnurl, providername=providername, membername=membername, patientname=patientname, imageid=imageid, memberid=memberid, memberref=memberref, providerid=providerid, imagefile = imagefile,dspatients=dspatients,patient=patientid,patienttype=patienttype,page=page)   
    


   