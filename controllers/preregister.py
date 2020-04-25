# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)

import datetime
import time
import json

import requests
import urllib2
import base64
import os

import Tkinter, tkFileDialog


from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import mdppreregister
from applications.my_pms2.modules  import states
from applications.my_pms2.modules  import gender

from applications.my_pms2.modules  import logger



@auth.requires_login()
def list_preregister():

   
    

    page = int(common.getid(request.vars.page))

    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getproviderfromid(db, providerid)
    providername = provdict["providername"]
    companycode = request.vars.companycode
    
    c = db(db.company.company == companycode).select(db.company.id)
    companyid = int(common.getid(c[0].id)) if len(c) >0 else 0           

    p = db(db.provider.provider == 'P0001').select(db.provider.id)
    p0001_id = int(common.getid(p[0].id))  if(len(p)>0) else 0
    
    # grid
    
    if((providerid == p0001_id) | (providerid==0)):  #if no provider or provider is 'P0001' (MDP Provider), all active pre-registers to be seen
        query = ((db.preregister.company==companyid) & (db.preregister.is_active==True))
    else:
        query = ((db.preregister.company==companyid) & (db.preregister.provider == providerid) & (db.preregister.is_active==True))  #else only active pre-register for the provider
        
        
    left = [db.provider.on(db.provider.id==db.preregister.provider),db.company.on(db.company.id == db.preregister.company)]
   
    
    fields=(db.preregister.employeeid, db.preregister.fname,db.preregister.lname,db.preregister.cell,db.preregister.oemail,db.provider.id,\
            db.company.company, db.provider.providername)
    
    db.provider.id.readable = False
    
    headers={
          'preregister.employeeid':'Employee ID',
          'preregister.fname':'First Name',          
          'preregister.lname':'Last Name',
          'preregister.cell':'Cell',
          'preregister.oemail':'Email',
          'company.company':'Company',
          'provider.providername':'Provider',
         
      }    

    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
	
    links = [\
             dict(header=CENTER('Open'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),\
                                                                   _href=URL("preregister","update_preregister",\
                                                                             vars=dict(page=page,preregid=row.preregister.id,providerid=p0001_id,\
                                                                                       companycode=companycode))))),
             dict(header=CENTER('Delete'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=25, _height=25),\
                                                                   _href=URL("preregister","delete_preregister",\
                                                                             vars=dict(page=page,preregid=row.preregister.id,providerid=p0001_id,\
                                                                                       companycode=companycode)))))
             
            ]

    orderby = (db.preregister.fname)

    
    formA = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        left=left,
                        paginate=10,
                        orderby=orderby,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )

    
    returnurl = URL('admin','providerhome')
    formheader = "PreRegister List"

    return dict(formA=formA,companycode=companycode, returnurl=returnurl,page=page,providerid=providerid, providername=providername)

@auth.requires_login()
def new_preregister():
    
    page = request.vars.page


    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getproviderfromid(db, providerid)
    providername = provdict["providername"]
    companycode = request.vars.companycode
    
    c = db(db.company.company == companycode).select(db.company.id,db.company.hmoplan)
    companyid = int(common.getid(c[0].id)) if len(c) >0 else 0           
    planid =  int(common.getid(c[0].hmoplan)) if len(c) >0 else 0           
    p = db(db.provider.provider == 'P0001').select(db.provider.id)
    p0001_id = int(common.getid(p[0].id))  if(len(p)>0) else 0
      
    
    formA = SQLFORM.factory(
        Field('employeeid', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),label='Employee ID', default=''),
        Field('fname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),label='First Name', default=''),
        Field('lname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),label='Last Name', default=''),
        Field('gender','string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '), default="Male",label='Gender',requires=IS_EMPTY_OR(IS_IN_SET(gender.GENDER))),
        Field('dob','date', label='DOB',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('address', 'text',label='Address', default=''),
        Field('city', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '), default="--Select City--",label='City',requires = IS_EMPTY_OR(IS_IN_SET(states.CITIES))),
        Field('st', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '), default="--Select State--",label='State',requires = IS_EMPTY_OR(IS_IN_SET(states.STATES))),
        Field('pin', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default="",label='Pin'),
        Field('cell', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),label='Cell Phone', default=''),
        Field('email', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),label='Email', default='emailid@mydentalplan.in'),
        Field('company', default=companyid, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '),requires=IS_IN_DB(db((db.company.is_active==True) & (db.company.company==companycode)), 'company.id', '%(name)s (%(company)s)')),
        Field('treatmentplandetails', 'text',label='Treatments'),
        Field('description', 'text',label='Description')
    )
    
    formA.element('textarea[name=address]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=address]')['_rows'] = 5 
    formA.element('textarea[name=address]')['_class'] = 'form-control'
    
    formA.element('textarea[name=treatmentplandetails]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=treatmentplandetails]')['_rows'] = 5 
    formA.element('textarea[name=treatmentplandetails]')['_class'] = 'form-control'    
    
    
    formA.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=description]')['_rows'] = 5 
    formA.element('textarea[name=description]')['_class'] = 'form-control'
    
    xdob = formA.element('input',_id='no_table_dob')
    xdob['_class'] =  'input-group form-control form-control-inline date-picker'
    xdob['_data-date-format'] = 'dd/mm/yyyy'
    xdob['_autocomplete'] = 'off' 
    xdob['_placeholder'] = 'dd/mm/yyyy'
    
    returnurl = URL('preregister', 'list_preregister',vars=dict(page=page,providerid=providerid,companycode=companycode))
     
    if formA.process().accepted:
        regobj = mdppreregister.Preregister(db, providerid, companycode)
        
        regdata={
            "fname": formA.vars.fname,
            "lname": formA.vars.lname,
            "address": formA.vars.address,
            "city": formA.vars.city,
            "pin": formA.vars.pin,
            "st": formA.vars.st,
            "gender": formA.vars.gender,
            "dob": formA.vars.dob.strftime("%d/%m/%Y")  if(formA.vars.dob != None) else "01/01/1990",
            "pemail": formA.vars.email,
            "cell": formA.vars.cell,
            "oemail": formA.vars.email,
            "description": formA.vars.description,
            "treatmentplandetails": formA.vars.treatmentplandetails,
            "priority": "High",
            "employeeid": formA.vars.employeeid,
            "providerid": providerid,
            "company" :companycode        
        }
       
        regobj.newpreregister(regdata)
        redirect(returnurl)
        
    elif formA.errors:
        response.flash = str(formA.errors)
    
   
    
    return dict(formA=formA,providerid=providerid,providername=providername,returnurl=returnurl)

@auth.requires_login()
def update_preregister():
    
    page = request.vars.page
   

    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getproviderfromid(db, providerid)
    providername = provdict["providername"]
    companycode = request.vars.companycode
    
    c = db(db.company.company == companycode).select(db.company.id,db.company.hmoplan)
    companyid = int(common.getid(c[0].id)) if len(c) >0 else 0           
    planid =  int(common.getid(c[0].hmoplan)) if len(c) >0 else 0           

    p = db(db.provider.provider == 'P0001').select(db.provider.id)
    p0001_id = int(common.getid(p[0].id))  if(len(p)>0) else 0    

    preregid = int(common.getid(request.vars.preregid))
    regobj = mdppreregister.Preregister(db, providerid, companycode)
    regdata = json.loads(regobj.getpreregister(preregid))
    
    
    formA = SQLFORM.factory(
            Field('employeeid', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),label='Employee ID', default=regdata["employeeid"]),
            Field('employeephoto','upload',uploadfolder=os.path.join(request.folder,'uploads')),
            Field('fname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),label='First Name', default=regdata["fname"]),
            Field('lname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),label='Last Name', default=regdata["lname"]),
            Field('gender','string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '), default=regdata["gender"],label='Gender',requires=IS_EMPTY_OR(IS_IN_SET(gender.GENDER))),
            Field('dob','date', label='DOB',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'),\
                  default=datetime.datetime.strptime(regdata["dob"],"%d/%m/%Y"),\
                  requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
            Field('address', 'text',label='Address', default=regdata["address"]),
            Field('city', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '), default=regdata["city"],label='City',requires = IS_EMPTY_OR(IS_IN_SET(states.CITIES))),
            Field('st', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '),default=regdata["st"],label='State',requires = IS_EMPTY_OR(IS_IN_SET(states.STATES))),
            Field('pin', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default=regdata["pin"],label='Pin'),
            Field('cell', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),label='Cell Phone', default=regdata["cell"]),
            Field('email', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),label='Email',default=regdata["oemail"]),
            Field('company', default=companyid, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '),requires=IS_IN_DB(db((db.company.is_active==True) & (db.company.company==companycode)), 'company.id', '%(name)s (%(company)s)')),
            Field('treatmentplandetails', 'text',label='Treatments',default=regdata["treatmentplandetails"]),
            Field('description', 'text',label='Description',default=regdata["description"])
        )
    
    formA.element('textarea[name=address]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=address]')['_rows'] = 5 
    formA.element('textarea[name=address]')['_class'] = 'form-control'
    
    formA.element('textarea[name=treatmentplandetails]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=treatmentplandetails]')['_rows'] = 5 
    formA.element('textarea[name=treatmentplandetails]')['_class'] = 'form-control'    


    formA.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=description]')['_rows'] = 5 
    formA.element('textarea[name=description]')['_class'] = 'form-control'

    xdob = formA.element('input',_id='no_table_dob')
    xdob['_class'] =  'input-group form-control form-control-inline date-picker'
    xdob['_data-date-format'] = 'dd/mm/yyyy'
    xdob['_autocomplete'] = 'off' 
    xdob['_placeholder'] = 'dd/mm/yyyy'    

    returnurl = URL('preregister', 'list_preregister',vars=dict(page=page,providerid=providerid,companycode=companycode))
 
    if formA.process().accepted:
        regobj = mdppreregister.Preregister(db, providerid, companycode)
               
        regdata={
            "preregisterid":str(preregid),
            "fname": formA.vars.fname,
            "lname": formA.vars.lname,
            "address": formA.vars.address,
            "city": formA.vars.city,
            "pin": formA.vars.pin,
            "st": formA.vars.st,
            "gender": formA.vars.gender,
            "dob": formA.vars.dob.strftime("%d/%m/%Y")  if(formA.vars.dob != None) else "01/01/1990",
            "pemail": formA.vars.email,
            "cell": formA.vars.cell,
            "oemail": formA.vars.email,
            "description": formA.vars.description,
            "treatmentplandetails": formA.vars.treatmentplandetails,
            "priority": "High",
            "employeeid": formA.vars.employeeid,
            "providerid": providerid,
            "company" :companycode        
        }
       
        regobj.updatepreregister(regdata)
        
        redirect(returnurl)
        
    elif formA.errors:
        response.flash = str(formA.errors) 

    
    
    return dict(formA=formA,page=page,providerid=providerid,providername=providername,returnurl=returnurl,preregid=preregid,companycode=companycode,imagefile=None)



@auth.requires_login()
def delete_preregister():
    page = request.vars.page
      
   
    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getproviderfromid(db, providerid)
    providername = provdict["providername"]
    companycode = request.vars.companycode
    
    c = db(db.company.company == companycode).select(db.company.id,db.company.hmoplan)
    companyid = int(common.getid(c[0].id)) if len(c) >0 else 0           
    planid =  int(common.getid(c[0].hmoplan)) if len(c) >0 else 0           

    p = db(db.provider.provider == 'P0001').select(db.provider.id)
    p0001_id = int(common.getid(p[0].id))  if(len(p)>0) else 0    

    preregid = int(common.getid(request.vars.preregid))
    regobj = mdppreregister.Preregister(db, providerid, companycode)
    regdata = json.loads(regobj.getpreregister(preregid))

    returnurl = URL('preregister', 'list_preregister',vars=dict(page=page,providerid=providerid,companycode=companycode))
    
    formA = FORM.confirm('Yes?',{'No':returnurl})


    if formA.accepted:
        db(db.preregister.id == preregid).update(is_active=False)
        redirect(returnurl)

    
    return dict(formA=formA,providerid=providerid,providername=providername,returnurl=returnurl)


def upload_employeephoto():
    
    page=request.vars.page
    providerid = int(common.getid(request.vars.providerid))
    preregid = int(common.getid(request.vars.preregid))
    companycode = request.vars.companycode
    
    
   
    
    
    returnurl = URL('preregister','update_preregister',vars=dict(page=page,providerid=providerid,preregid=preregid,companycode=companycode))
    image_form = FORM(
           
            INPUT(_name='image_file',_type='file')
            )
    
    
    if image_form.accepts(request.vars,formname='image_form'):
	i=0
	
	

	filename = os.path.join(request.folder,'uploads') + "\\" + image_form.vars.image_file.filename
	#filename = image_form.vars.image_file.file.name
	#imagefile = db.preregister.image.store(image_form.vars.image_file.file)
	#imagedata = ""
	#with open(filename, "rb") as imageFile:
	    #imagedata = base64.b64encode(imageFile.read())
      
	#oimage = mdpimage.Image(current.globalenv['db'],providerid)
	#rsp = oimage.xuploadimage(imagedata,request.folder)

	
	
	
    
    #images = db(db.preregister.id == preregid).select(db.preregister.image)
    
    return dict(form=image_form,page=page,providerid=providerid,preregid=preregid,companycode=companycode)

