from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)


import datetime
import time

#import sys
#sys.path.append('modules')
from applications.my_pms2.modules import common
from applications.my_pms2.modules import treatmentstatus
#from gluon.contrib import common
#from gluon.contrib import treatmentstatus



def getpresgrid(memberid, patientid,providerid):
    
    prescriptions = db((db.vw_patientprescription.providerid == providerid) & \
                              (db.vw_patientprescription.is_active == True) & \
                              (db.vw_patientprescription.patientid == patientid) & \
                              (db.vw_patientprescription.memberid == memberid)).select()
    
    
    
    return prescriptions


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_medicine():

    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]

     
    #query = ((db.medicine.providerid == providerid) & (db.medicine.is_active == True))
    #fields = (db.medicine.medicine,db.medicine.medicinetype,db.medicine.strength, db.medicine.strengthuom, db.medicine.instructions)
    
    query = ((db.medicine_default.is_active == True))
    fields = (db.medicine_default.medicine,db.medicine_default.meditype,db.medicine_default.strength, db.medicine_default.strengthuom, db.medicine_default.instructions)
   
    
    headers = {\
        'medicine_default.medicine' : 'Medicine Name',
        'medicine_default.meditype' : 'Medicine Type',
        'medicine_default.strength' : 'Dosage',
        'medicine_default.strengthuom' : 'Measure'
    }
    
    links = [\
        dict(header=CENTER('Edit'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=30, _height=30),_href=URL("prescription","update_medicine",vars=dict(medicineid=row.id))))),
        dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),_href=URL("prescription","delete_medicine",vars=dict(medicineid=row.id)))))
        ]
    
    orderby = (db.medicine_default.medicine)
        
    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)    

    returnurl = URL('admin', 'providerhome')

    maxtextlengths = {'medicine_default.medicine':128, 'medicine_default.meditype':32,'medicine_default.strength':16, 'medicine_default.strengthuom':16}
    
    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            maxtextlengths=maxtextlengths,
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

    return dict(form=form,page=0,returnurl=returnurl,providerid=providerid,providername=providername)



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def new_medicine():
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    returnurl = ""
    doctorid = 0
    patientid = 0
    memberid = 0
    tplanid = 0
    treatmentid = 0
    page = 0
    
    source = common.getstring(request.vars.source)
    if(source == "prescriptions"):
        doctorid = int(common.getid(request.vars.doctorid))
        patientid = int(common.getid(request.vars.patientid))
        memberid = int(common.getid(request.vars.memberid))
        page = common.getpage(request.vars.page)
        tplanid = int(common.getid(request.vars.tplanid))
        treatmentid = int(common.getid(request.vars.treatmentid))
        xreturnurl = common.getstring(request.vars.returnurl)
        returnurl = URL('prescription', 'prescriptions', vars=dict(page=page,providerid=providerid,patientid=patientid,memberid=memberid,doctorid=doctorid,tplanid=tplanid,treatmentid=treatmentid,returnurl=xreturnurl))
    else:
        returnurl = URL('prescription', 'list_medicine')
        
    page = 0
    
    #db.medicine.is_active.default = True
    #db.medicine.providerid.default = providerid
    
    if(source == "prescriptions"):
        crud.settings.create_next = returnurl
    else:
        crud.settings.create_next = URL('prescription','list_medicine')
    
    formA = crud.create(db.medicine_default,message='New medicine added!')  
    
    xname = formA.element('input',_id='medicine_default_medicine')
    if(xname != None):
        xname['_class'] = 'form-control' 

    xtype = formA.element('select',_id='medicine_default_meditype')
    if(xtype != None):
        xtype['_class'] = 'form-control'
    
    xstr = formA.element('input',_id='medicine_default_strength')
    if(xstr != None):
        xstr['_class'] = 'form-control'
    

    xuom = formA.element('select',_id='medicine_default_strengthuom')
    if(xuom != None):
        xuom['_class'] = 'form-control'
    

    xinstr = formA.element('input',_id='medicine_default_instructions')
    if(xinstr != None):
        xinstr['_class'] = 'form-control'

    #formA.element('textarea[name=notes]')['_class'] = 'form-control'
    #formA.element('textarea[name=notes]')['_style'] = 'height:100px;line-height:1.0;'
    #formA.element('textarea[name=notes]')['_rows'] = 5

    
    return dict(formA=formA, returnurl=returnurl,page=page,providerid=providerid,providername=providername)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def update_medicine():
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    medicineid = int(common.getid(request.vars.medicineid))
    
    returnurl = URL('prescription', 'list_medicine')
    page = 0
    
    db.doctor.is_active.default = True
    db.doctor.providerid.default = providerid
    
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = returnurl
    
    formA = crud.update(db.medicine, medicineid,cast=int,message='Medicine information updated!')  ## company Details entry form
    
   
    
    xname = formA.element('input',_id='medicine_medicine')
    xname['_class'] = 'form-control'

    xtype = formA.element('select',_id='medicine_medicinetype')
    xtype['_class'] = 'form-control'
    
    xstr = formA.element('input',_id='medicine_strength')
    xstr['_class'] = 'form-control'
    

    xuom = formA.element('select',_id='medicine_strengthuom')
    xuom['_class'] = 'form-control'
    

    xinstr = formA.element('input',_id='medicine_instructions')
    xinstr['_class'] = 'form-control'

    formA.element('textarea[name=notes]')['_class'] = 'form-control'
    formA.element('textarea[name=notes]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=notes]')['_rows'] = 5
    
    return dict(formA=formA, returnurl=returnurl,page=page,providerid=providerid,providername=providername)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def delete_medicine():
    
    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]
    
    medicineid = int(common.getid(request.vars.medicineid))

    returnurl = URL('prescription', 'list_medicine')
    
    form = FORM.confirm('Yes',{'No': returnurl})
    
    if form.accepted:
        db(db.medicine.id == medicineid).update(is_active = False) 
        session.flash = 'Medicine deleted!'
        redirect(returnurl)
        
    return dict(form=form,returnurl=returnurl,providerid=providerid,providername=providername,page=0)


def get_prescriptions():
    
    page=common.getpage(request.vars.page)
    
    returnurl = common.getstring(request.vars.returnurl)
    
    providerid = int(common.getid(request.get_vars.providerid))
    
    doctorid = int(common.getid(request.get_vars.doctor))
    doctorid = int(common.getid(request.post_vars.doctor)) if(doctorid == 0) else doctorid
    
    patient = common.getstring(request.vars.xpatientmember1)
    
    patientid = 0
    memberid = 0
    medicineid = 0
    
    pats = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patient == patient)).select()
    if(len(pats)>0):
        patientid = int(common.getid(pats[0].patientid))
        memberid = int(common.getid(pats[0].primarypatientid))

    tplanid = int(common.getid(request.get_vars.tplanid))
    tplanid = int(common.getid(request.post_vars.tplanid)) if(tplanid == 0) else tplanid
    treatmentid = int(common.getid(request.get_vars.treatmentid))
    treatmentid = int(common.getid(request.post_vars.treatmentid)) if(treatmentid == 0) else treatmentid
    
    formPres = SQLFORM.factory(\
        Field('prescriptiondate', 'date', label='Date',  default=datetime.date.today(),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('medicine', 'integer', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _default="0",_style="width:100%;height:35px",_class='form_details'),\
              label='Drug',requires=IS_IN_DB(db((db.medicine_default.id > 0)&(db.medicine_default.is_active == True)), 'medicine_default.id', '%(medicine)s:%(strength)s:%(strengthuom)s')),
        Field('strength', 'string',represent=lambda v, r: '' if v is None else v),
        Field('strengthuom', 'string',represent=lambda v, r: '' if v is None else v,default="",requires=IS_IN_SET(STRENGTHUOM)),
        Field('frequency', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('dosage', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('quantity', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('presremarks', 'text',represent=lambda v, r: '' if v is None else v,default=""),
        Field('doctorid', 'integer', default=doctorid),
        Field('doctorid1', 'integer', default=doctorid),
        Field('patientid', 'integer', default=patientid),
        Field('memberid', 'integer', default=memberid),
        Field('patientid1', 'integer', default=patientid),
        Field('memberid1', 'integer', default=memberid),
    )
    
    xdate =  formPres.element('#no_table_prescriptiondate')
    xdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xdate['_data-date-format'] = 'dd/mm/yyyy'
    xdate['_autocomplete'] = 'off'  
    
    xmedicine = formPres.element('#no_table_medicine')
    xmedicine['_class'] = 'form-control'
    xmedicine['_autocomplete'] = 'off'    
    
    xstrength = formPres.element('#no_table_strength')
    xstrength['_class'] = 'form-control'
    xstrength['_autocomplete'] = 'off'    
    
    xstrengthuom = formPres.element('#no_table_strengthuom')
    xstrengthuom['_class'] = 'form-control'
    xstrengthuom['_autocomplete'] = 'off'    
    
    xfreq = formPres.element('#no_table_frequency')
    xfreq['_class'] = 'form-control'
    xfreq['_autocomplete'] = 'off'    
    
    xdosage = formPres.element('#no_table_dosage')
    xdosage['_class'] = 'form-control'
    xdosage['_autocomplete'] = 'off'   
    
    xqty = formPres.element('#no_table_quantity')
    xqty['_class'] = 'form-control'
    xqty['_autocomplete'] = 'off'   
    
    formPres.element('textarea[name=presremarks]')['_class'] = 'form-control'
    formPres.element('textarea[name=presremarks]')['_style'] = 'height:100px;line-height:1.0;'
    formPres.element('textarea[name=presremarks]')['_rows'] = 5
    
    
   
    query  =((db.vw_patientprescription.providerid == providerid) & \
            (db.vw_patientprescription.is_active == True) & \
            (db.vw_patientprescription.patientid == patientid) & \
            (db.vw_patientprescription.memberid == memberid))

    fields= (db.vw_patientprescription.medicine, db.vw_patientprescription.frequency,db.vw_patientprescription.dosage,db.vw_patientprescription.prescriptiondate)
    
    headers={
            'vw_patientprescription.medicine':'Drug',
            'vw_patientprescription.frequency':'Frequency',
            'vw_patientprescription.dosage':'Duration',
            'vw_patientprescription.prescriptiondate':'Date'
                }    

    links = [
             dict(header=CENTER('Edit'), 
                  body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL('prescription','update_prescription',vars=dict(providerid=providerid,prescriptionid=row.id))))),\
             dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),_href=URL('prescription','delete_prescription',vars=dict(providerid=providerid,prescriptionid=row.id)))))
             ]
    
    

    selectable = lambda ids : redirect(URL('pescription', 'prescripion_report', vars=dict(ids=ids,providerid=providerid,memberid=memberid,patientid=patientid,doctorid=doctorid,treatmentid=treatmentid,tplanid=tplanid,returnurl=returnurl)))  

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
 
    left = None
    orderby = ~db.vw_patientprescription.prescriptiondate

 
    
    prescriptions = SQLFORM.grid(query=query,
                         headers=headers,
                         fields=fields,
                         orderby=orderby,
                         links=links,
                         selectable=selectable,
                         paginate=20,
                         exportclasses=exportlist,
                         links_in_grid=True,
                         searchable=False ,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=True
                         )    

    submit = prescriptions.element('.web2py_table input[type=submit]')
    if(submit != None):
        submit['_value'] = T('Print Prescription')
        submit['_class'] = 'btn green'
        #submit['_class'] = 'form_details_button'
    
    #prescriptions = getpresgrid(memberid, patientid, providerid)

    if formPres.accepts(request,session=session,formname='formpres',keepvalues=True):
        i  = 0
    elif formPres.errors:
       response.flash = 'Error in Prescription form ' + str(formPres.errors)
        
        
        
    return dict(formPres=formPres,prescriptions=prescriptions,page=page,providerid=providerid,patientid1=patientid,memberid1=memberid,doctorid1=doctorid,tplanid1=tplanid,treatmentid1=treatmentid,returnurl=returnurl)

def save_prescription():
    
    page=common.getpage(request.vars.page)
    
    returnurl = common.getstring(request.vars.returnurl)
    
    memberid = int(common.getid(request.get_vars.memberid))
    memberid = int(common.getid(request.post_vars.memberid)) if(memberid == 0) else memberid

    patientid = int(common.getid(request.get_vars.patientid))
    patientid = int(common.getid(request.post_vars.patientid)) if(patientid == 0) else patientid

    providerid = int(common.getid(request.get_vars.providerid))
    doctorid = int(common.getid(request.get_vars.doctor))
    doctorid = int(common.getid(request.post_vars.doctorid)) if(doctorid == 0) else doctorid
    tplanid = int(common.getid(request.get_vars.tplanid))
    tplanid = int(common.getid(request.post_vars.tplanid)) if(tplanid == 0) else tplanid
    treatmentid = int(common.getid(request.get_vars.treatmentid))
    treatmentid = int(common.getid(request.post_vars.treatmentid)) if(treatmentid == 0) else treatmentid
    
    medicineid = int(common.getid(request.vars.medicine))

    prescriptionid = db.prescription.insert(\
           
           providerid = providerid,
           medicineid = medicineid,
           doctorid = doctorid,
           patientid = patientid,
           memberid = memberid,
           frequency  = common.getstring(request.vars.frequency),
           dosage = common.getstring(request.vars.dosage),
           quantity  = common.getstring(request.vars.quantity),
           prescriptiondate = datetime.datetime.strptime(request.vars.prescriptiondate,"%d/%m/%Y"),
           remarks = common.getstring(request.vars.presremarks),
           tplanid = tplanid,
           treatmentid = treatmentid,
           medicinename = None,
           medicinecode = None,
           is_active = True,
           created_on = common.getISTFormatCurrentLocatTime(),
           created_by = providerid,
           modified_on = common.getISTFormatCurrentLocatTime(),
           modified_by = providerid
           
       )    
    
    formPres = SQLFORM.factory(\
        Field('prescriptiondate', 'date', label='Date',  default=common.getISTFormatCurrentLocatTime(),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('medicine', 'integer',  widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),  label='Drug',requires=IS_IN_DB(db((db.medicine.providerid==providerid)&(db.medicine.is_active == True)), 'medicine.id', '%(medicine)s:%(strength)s:%(strengthuom)s')),
        Field('strength', 'string',represent=lambda v, r: '' if v is None else v),
        Field('strengthuom', 'string',represent=lambda v, r: '' if v is None else v,default="",requires=IS_IN_SET(STRENGTHUOM)),
        Field('frequency', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('dosage', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('quantity', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('presremarks', 'text',represent=lambda v, r: '' if v is None else v,default=""),
        Field('doctorid', 'integer', default=doctorid),
        Field('patientid', 'integer', default=patientid),
        Field('memberid', 'integer', default=memberid),
        Field('patientid1', 'integer', default=patientid),
        Field('memberid1', 'integer', default=memberid),
    )
    
    xdate =  formPres.element('#no_table_prescriptiondate')
    xdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xdate['_data-date-format'] = 'dd/mm/yyyy'
    xdate['_autocomplete'] = 'off'  
    
    xmedicine = formPres.element('#no_table_medicine')
    xmedicine['_class'] = 'form-control'
    xmedicine['_autocomplete'] = 'off'    
    
    xstrength = formPres.element('#no_table_strength')
    xstrength['_class'] = 'form-control'
    xstrength['_autocomplete'] = 'off'    
    
    xstrengthuom = formPres.element('#no_table_strengthuom')
    xstrengthuom['_class'] = 'form-control'
    xstrengthuom['_autocomplete'] = 'off'    
    
    xfreq = formPres.element('#no_table_frequency')
    xfreq['_class'] = 'form-control'
    xfreq['_autocomplete'] = 'off'    
    
    xdosage = formPres.element('#no_table_dosage')
    xdosage['_class'] = 'form-control'
    xdosage['_autocomplete'] = 'off'   
    
    xqty = formPres.element('#no_table_quantity')
    xqty['_class'] = 'form-control'
    xqty['_autocomplete'] = 'off'   
    
    formPres.element('textarea[name=presremarks]')['_class'] = 'form-control'
    formPres.element('textarea[name=presremarks]')['_style'] = 'height:100px;line-height:1.0;'
    formPres.element('textarea[name=presremarks]')['_rows'] = 5
    
    
   
    query  =((db.vw_patientprescription.providerid == providerid) & \
            (db.vw_patientprescription.is_active == True) & \
            (db.vw_patientprescription.patientid == patientid) & \
            (db.vw_patientprescription.memberid == memberid))

    fields= (db.vw_patientprescription.medicine, db.vw_patientprescription.frequency,db.vw_patientprescription.dosage,db.vw_patientprescription.prescriptiondate)
    
    headers={
            'vw_patientprescription.medicine':'Drug',
            'vw_patientprescription.frequency':'Frequency',
            'vw_patientprescription.dosage':'Duration',
            'vw_patientprescription.prescriptiondate':'Date'
                }    

    links = [
             dict(header=CENTER('Edit'), 
                  body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL('prescription','update_prescription',vars=dict(providerid=providerid,prescriptionid=row.id))))),\
             dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),_href=URL('prescription','delete_prescription',vars=dict(providerid=providerid,prescriptionid=row.id)))))
             ]
    
    

    selectable = lambda ids : redirect(URL('pescription', 'prescripion_report', vars=dict(ids=ids,providerid=providerid,memberid=memberid,patientid=patientid,doctorid=doctorid,treatmentid=treatmentid,tplanid=tplanid,returnurl=returnurl)))  

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
 
    left = None
    orderby = ~db.vw_patientprescription.prescriptiondate

 
    
    prescriptions = SQLFORM.grid(query=query,
                         headers=headers,
                         fields=fields,
                         orderby=orderby,
                         links=links,
                         selectable=selectable,
                         paginate=20,
                         exportclasses=exportlist,
                         links_in_grid=True,
                         searchable=False ,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=True
                         )    

    submit = prescriptions.element('.web2py_table input[type=submit]')
    if(submit != None):
        submit['_value'] = T('Print Prescription')
        submit['_class'] = 'btn green'
        #submit['_class'] = 'form_details_button'
    
    #prescriptions = getpresgrid(memberid, patientid, providerid)

    if formPres.accepts(request,session=session,formname='formpres',keepvalues=True):
        i  = 0
    elif formPres.errors:
       
        response.flash = 'Error in Prescription form ' + str(formPres.errors)
        
        
        
    return dict(formPres=formPres,prescriptions=prescriptions,page=page,providerid=providerid,patientid1=patientid,memberid1=memberid,doctorid1=doctorid,tplanid1=tplanid,treatmentid1=treatmentid,returnurl=returnurl)


def xsave_prescription():
    
    returnurl = common.getstring(request.vars.returnurl)
    page=common.getpage(request.vars.page)
    providerid = int(common.getid(request.vars.providerid))
    patientid = int(common.getid(request.vars.patientid))
    memberid = int(common.getid(request.vars.memberid))
    doctorid = int(common.getid(request.vars.doctor))
    
   
    treatmentid = int(common.getid(request.vars.treatmentid))
    tplanid = int(common.getid(request.vars.tplanid))
    
    
    prescriptionid = db.prescription.insert(\
        
        providerid = common.getid(request.vars.providerid),
        medicineid = common.getid(request.vars.medicine),
        doctorid = common.getid(request.vars.doctor),
        patientid = patientid,
        memberid = memberid,
        frequency  = common.getstring(request.vars.frequency),
        dosage = common.getstring(request.vars.dosage),
        quantity  = common.getstring(request.vars.quantity),
        prescriptiondate = datetime.datetime.strptime(request.vars.prescriptiondate,"%d/%m/%Y"),
        remarks = common.getstring(request.vars.presremarks),
        tplanid = tplanid,
        treatmentid = treatmentid,
        medicinename = None,
        medicinecode = None,
        is_active = True,
        created_on = common.getISTFormatCurrentLocatTime(),
        created_by = providerid,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = providerid
        
    )
    
    

    formPres = SQLFORM.factory(\
        Field('prescriptiondate', 'date', label='Date',  default=datetime.date.today(),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('doctor', 'integer', default=doctorid, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),  label='Drug',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active == True)), 'doctor.id', '%(name)s')),
        Field('medicine', 'integer', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),  default="", label='Drug',requires=IS_IN_DB(db((db.medicine.providerid==providerid)&(db.medicine.is_active == True)), 'medicine.id', '%(medicine)s:%(strength)s:%(strengthuom)s')),
        Field('strength', 'string',represent=lambda v, r: '' if v is None else v),
        Field('strengthuom', 'string',represent=lambda v, r: '' if v is None else v,default="",requires=IS_IN_SET(STRENGTHUOM)),
        Field('frequency', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('dosage', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('quantity', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('presremarks', 'text',represent=lambda v, r: '' if v is None else v,default=""),
        Field('doctorid', 'integer', default=doctorid),
        Field('patientid', 'integer', default=patientid),
        Field('memberid', 'integer', default=memberid),
        Field('patientid1', 'integer', default=patientid),
        Field('memberid1', 'integer', default=memberid),
        
    )
    
    xdate =  formPres.element('#no_table_prescriptiondate')
    xdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xdate['_data-date-format'] = 'dd/mm/yyyy'
    xdate['_autocomplete'] = 'off'  
    
    xdoctor = formPres.element('#no_table_doctor')
    xdoctor['_class'] = 'form-control'
    xdoctor['_autocomplete'] = 'off'    
    
    xmedicine = formPres.element('#no_table_medicine')
    xmedicine['_class'] = 'form-control'
    xmedicine['_autocomplete'] = 'off'    
    
    xstrength = formPres.element('#no_table_strength')
    xstrength['_class'] = 'form-control'
    xstrength['_autocomplete'] = 'off'    
    
    xstrengthuom = formPres.element('#no_table_strengthuom')
    xstrengthuom['_class'] = 'form-control'
    xstrengthuom['_autocomplete'] = 'off'    
    
    xfreq = formPres.element('#no_table_frequency')
    xfreq['_class'] = 'form-control'
    xfreq['_autocomplete'] = 'off'    
    
    xdosage = formPres.element('#no_table_dosage')
    xdosage['_class'] = 'form-control'
    xdosage['_autocomplete'] = 'off'   
    
    xqty = formPres.element('#no_table_quantity')
    xqty['_class'] = 'form-control'
    xqty['_autocomplete'] = 'off'   
    
    formPres.element('textarea[name=presremarks]')['_class'] = 'form-control'
    formPres.element('textarea[name=presremarks]')['_style'] = 'height:100px;line-height:1.0;'
    formPres.element('textarea[name=presremarks]')['_rows'] = 5
    
    query  =((db.vw_patientprescription.providerid == providerid) & \
            (db.vw_patientprescription.is_active == True) & \
            (db.vw_patientprescription.patientid == patientid) & \
            (db.vw_patientprescription.memberid == memberid))

    fields= (db.vw_patientprescription.medicine, db.vw_patientprescription.frequency,db.vw_patientprescription.dosage,db.vw_patientprescription.prescriptiondate)
    
    headers={
            'vw_patientprescription.medicine':'Drug',
            'vw_patientprescription.frequency':'Frequency',
            'vw_patientprescription.dosage':'Duration',
            'vw_patientprescription.prescriptiondate':'Date'
                }    

    links = [
             dict(header=CENTER('Edit'), 
                  body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL('prescription','update_prescription',vars=dict(providerid=providerid,prescriptionid=row.id))))),\
             dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),_href=URL('prescription','delete_prescription',vars=dict(providerid=providerid,prescriptionid=row.id)))))
             ]
    
    

    selectable = lambda ids : redirect(URL('pescription', 'prescripion_report', vars=dict(ids=ids,providerid=providerid,memberid=memberid,patientid=patientid,doctorid=doctorid,memberid1=memberid,patientid1=patientid,doctorid1=doctori,treatmentid=treatmentid,tplanid=tplanid,returnurl=returnurl)))  

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
 
    left = None
    orderby = ~db.vw_patientprescription.prescriptiondate

 
    
    prescriptions = SQLFORM.grid(query=query,
                         headers=headers,
                         fields=fields,
                         orderby=orderby,
                         links=links,
                         selectable=selectable,
                         paginate=20,
                         exportclasses=exportlist,
                         links_in_grid=True,
                         searchable=False ,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=True
                         )    

    submit = prescriptions.element('.web2py_table input[type=submit]')
    if(submit != None):
        submit['_value'] = T('Print Prescription')
        submit['_class'] = 'btn green'
    
    
    #prescriptions = getpresgrid(memberid, patientid, providerid)
    
    return dict(formPres=formPres,prescriptions=prescriptions,page=page,providerid=providerid,patientid=patientid,memberid=memberid,doctorid=doctorid,patientid1=patientid,memberid1=memberid,doctorid1=doctorid,tplanid=tplanid,treatmentid=treatmentid,returnurl=returnurl)
    


def xget_prescriptions():
    
    provdict = common.getprovider(auth,db)
    providerid = provdict["providerid"]    
    providername = provdict["providername"]
    doctorname = ""
    doctorid = int(common.getid(request.vars.doctor))
    rows = db(db.doctor.id == doctorid).select(db.doctor.name)
    if(len(rows)>0):
        doctorname = rows[0].name
        
    memberid = 0
    patientid = 0
    
    prescriptions = None
    
    page = request.vars.page
    
    
    r = db((db.vw_memberpatientlist.patient == request.vars.xpatientmember)).select()
    if(len(r)>0):
        memberid = int(common.getid(r[0].primarypatientid))
        patientid = int(common.getid(r[0].patientid))

        prescriptions = db((db.vw_patientprescription.providerid == providerid) & \
                           (db.vw_patientprescription.is_active == True) & \
                           (db.vw_patientprescription.patientid == patientid) & \
                           (db.vw_patientprescription.memberid == memberid)).select()
        
        
    return dict(prescriptions = prescriptions,page=page,providerid=providerid,providername=providername,patientid=patientid,memberid=memberid,doctorid=doctorid,doctorname=doctorname)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def new_prescription():
    
    paget = request.vars.page
    providerid = common.getid(request.vars.providerid)
    providername = common.getstring(request.vars.providername)
    patientid = common.getid(request.vars.patientid)
    memberid = common.getid(request.vars.memberid)
    doctorid = common.getid(request.vars.doctorid)
    doc = db((db.doctor.id == doctorid) & (db.doctor.is_active == True)).select(db.doctor.name)
    
    
    patientname = ""
    age = ""
    gender = ""
    
    r = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid == memberid)).select()
    if(len(r) > 0):
        patientname = r[0].patient
        gender = r[0].gender
        age = r[0].age
    
    page = 0
    
    returnurl = URL('prescription', 'prescriptions', vars=dict(page=page,providerid=providerid,patientid=patientid,memberid=memberid))
    
    formA = SQLFORM.factory(\
        Field('prescriptiondate', 'date', label='Date',  default=datetime.date.today(),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('doctor', 'integer', default=doctorid, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),  label='Drug',writable=False,requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active == True)), 'doctor.id', '%(name)s')),
        Field('medicine', 'integer', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _default="0",_style="width:100%;height:35px",_class='form_details'),\
              label='Drug',requires=IS_IN_DB(db((db.medicine_default.id > 0)&(db.medicine_default.is_active == True)), 'medicine_default.id', '%(medicine)s:%(strength)s:%(strengthuom)s')),
        
        Field('strength', 'string',represent=lambda v, r: '' if v is None else v),
        Field('strengthuom', 'string',represent=lambda v, r: '' if v is None else v,default="",requires=IS_IN_SET(STRENGTHUOM)),
        Field('frequency', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('dosage', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('quantity', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        Field('remarks', 'text',represent=lambda v, r: '' if v is None else v,default=""),
        
    )
    
    xdate =  formA.element('#no_table_prescriptiondate')
    xdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xdate['_data-date-format'] = 'dd/mm/yyyy'
    xdate['_autocomplete'] = 'off'  
    
    #xdoctor = formA.element('#no_table_doctor')
    #xdoctor['_class'] = 'form-control'
    #xdoctor['_autocomplete'] = 'off'    
    
    xmedicine = formA.element('#no_table_medicine')
    xmedicine['_class'] = 'form-control'
    xmedicine['_autocomplete'] = 'off'    
    
    xstrength = formA.element('#no_table_strength')
    xstrength['_class'] = 'form-control'
    xstrength['_autocomplete'] = 'off'    
    
    xstrengthuom = formA.element('#no_table_strengthuom')
    xstrengthuom['_class'] = 'form-control'
    xstrengthuom['_autocomplete'] = 'off'    
    
    xfreq = formA.element('#no_table_frequency')
    xfreq['_class'] = 'form-control'
    xfreq['_autocomplete'] = 'off'    
    
    xdosage = formA.element('#no_table_dosage')
    xdosage['_class'] = 'form-control'
    xdosage['_autocomplete'] = 'off'   
    
    xqty = formA.element('#no_table_quantity')
    xqty['_class'] = 'form-control'
    xqty['_autocomplete'] = 'off'   
    
    formA.element('textarea[name=remarks]')['_class'] = 'form-control'
    formA.element('textarea[name=remarks]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=remarks]')['_rows'] = 5
    
    
    if formA.accepts(request,session,keepvalues=True):
        
        prescriptionid = db.prescription.insert(\
            
            providerid = common.getid(request.vars.providerid),
            medicineid = common.getid(request.vars.medicine),
            doctorid = doctorid,
            patientid = common.getid(request.vars.patientid),
            memberid = common.getid(request.vars.memberid),
            frequency  = common.getstring(request.vars.frequency),
            dosage = common.getstring(request.vars.dosage),
            quantity  = common.getstring(request.vars.quantity),
            prescriptiondate = datetime.datetime.strptime(request.vars.prescriptiondate,"%d/%m/%Y"),
            remarks = common.getstring(request.vars.remarks),
            tplanid = None,
            treatmentid = None,
            medicinename = None,
            medicinecode = None,
            is_active = True,
            created_on = common.getISTFormatCurrentLocatTime(),
            created_by = providerid,
            modified_on = common.getISTFormatCurrentLocatTime(),
            modified_by = providerid
            
        )
        
        session.flash = "New prescription added successfully!"
        redirect(URL('prescription', 'prescriptions', vars=dict(prescriptionid=prescriptionid)))
        
    elif formA.errors:
        response.flash = 'Error adding new prescription! '  + str(formA.errors)
    
    return dict(formA=formA, returnurl=returnurl,page=page,providerid=providerid,providername=providername,patientname = patientname, gender=gender, age=age,doctorid=doctorid,doctorname=doc[0].name)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def update_prescription():
    
   
    page = request.vars.page
    prescriptionid = common.getid(request.vars.prescriptionid)
    returnurl = URL("admin","providerhome")
    
    providerid = common.getid(request.vars.providerid)
    providername = common.getstring(request.vars.providername)
    
    patientname = ""
    gender = ""
    age = ""
    
    patientid = 0
    memberid = 0
    tplanid = 0
    treatmentid  = 0
    doctorid = 0    
    medicineid = int(common.getid(request.vars.medicine))
    
    pres = db((db.vw_patientprescription.id == prescriptionid) & (db.vw_patientprescription.is_active == True)).select()
    if(len(pres)>0):
        patientid = common.getid(pres[0].patientid)
        memberid = common.getid(pres[0].memberid)
        tplanid = common.getid(pres[0].tplanid)
        treatmentid = common.getid(pres[0].treatmentid)
        doctorid = common.getid(pres[0].doctorid)
        returnurl = URL('prescription','prescriptions', vars=dict(page=page,providerid=providerid,memberid1=memberid,patientid1=patientid,doctorid1=doctorid,treatmentid1=treatmentid,tplanid1=tplanid,returnurl=returnurl))        
        
        r = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid == memberid)).select()
        if(len(r) > 0):
            patientname = r[0].patient
            gender = r[0].gender
            age = r[0].age
        
    
    formA = SQLFORM.factory(\
        Field('prescriptiondate', 'date', label='Date',  default=pres[0].prescriptiondate,requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('doctor', 'integer', default=doctorid, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),  label='Drug',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active == True)), 'doctor.id', '%(name)s')),
        Field('medicine', 'integer', default=common.getid(pres[0].medicineid),widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _default="0",_style="width:100%;height:35px",_class='form_details'),\
              label='Drug',requires=IS_IN_DB(db((db.medicine_default.id > 0)&(db.medicine_default.is_active == True)), 'medicine_default.id', '%(medicine)s:%(strength)s:%(strengthuom)s')),
        
        Field('strength', 'string',default=common.getstring(pres[0].strength),represent=lambda v, r: '' if v is None else v),
        Field('strengthuom', 'string', represent=lambda v, r: '' if v is None else v,default=common.getstring(pres[0].strengthuom),requires=IS_IN_SET(STRENGTHUOM)),
        Field('frequency', 'string',represent=lambda v, r: '' if v is None else v,default=common.getstring(pres[0].frequency)),
        Field('dosage', 'string',represent=lambda v, r: '' if v is None else v,default=common.getstring(pres[0].dosage)),
        Field('quantity', 'string',represent=lambda v, r: '' if v is None else v,default=common.getstring(pres[0].quantity)),
        Field('remarks', 'text',represent=lambda v, r: '' if v is None else v,default=common.getstring(pres[0].remarks)),
        
    )
    
    xdate =  formA.element('#no_table_prescriptiondate')
    xdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xdate['_data-date-format'] = 'dd/mm/yyyy'
    xdate['_autocomplete'] = 'off'  
    
    xdoctor = formA.element('#no_table_doctor')
    xdoctor['_class'] = 'form-control'
    xdoctor['_autocomplete'] = 'off'    
    
    xmedicine = formA.element('#no_table_medicine')
    xmedicine['_class'] = 'form-control'
    xmedicine['_autocomplete'] = 'off'    
    
    xstrength = formA.element('#no_table_strength')
    xstrength['_class'] = 'form-control'
    xstrength['_autocomplete'] = 'off'    
    
    xstrengthuom = formA.element('#no_table_strengthuom')
    xstrengthuom['_class'] = 'form-control'
    xstrengthuom['_autocomplete'] = 'off'    
    
    xfreq = formA.element('#no_table_frequency')
    xfreq['_class'] = 'form-control'
    xfreq['_autocomplete'] = 'off'    
    
    xdosage = formA.element('#no_table_dosage')
    xdosage['_class'] = 'form-control'
    xdosage['_autocomplete'] = 'off'   
    
    xqty = formA.element('#no_table_quantity')
    xqty['_class'] = 'form-control'
    xqty['_autocomplete'] = 'off'   
    
    formA.element('textarea[name=remarks]')['_class'] = 'form-control'
    formA.element('textarea[name=remarks]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=remarks]')['_rows'] = 5
    
    
    if formA.accepts(request,session,keepvalues=True):
        
        db(db.prescription.id == prescriptionid).update(\
            
            providerid = providerid,
            medicineid = common.getid(request.vars.medicine),
            doctorid = common.getid(request.vars.doctor),
            patientid = patientid,
            memberid = memberid,
            frequency  = common.getstring(request.vars.frequency),
            dosage = common.getstring(request.vars.dosage),
            quantity  = common.getstring(request.vars.quantity),
            prescriptiondate = datetime.datetime.strptime(request.vars.prescriptiondate,"%d/%m/%Y"),
            remarks = common.getstring(request.vars.remarks),
            tplanid = None,
            treatmentid = None,
            medicinename = None,
            medicinecode = None,
            is_active = True,
            modified_on = common.getISTFormatCurrentLocatTime(),
            modified_by = providerid
            
        )
        session.flash = 'Prescription updated successfully!'
        redirect(returnurl)
     
    elif formA.errors:
        response.flash = 'Errors - Prescription Update '  + str(formA.errors)
    
    return dict(formA=formA, returnurl=returnurl,page=page,providerid=providerid,providername=providername,patientname = patientname, gender=gender, age=age)



def prescription_report():
    
    page = common.getpage(request.vars.page)
    
    ids = request.vars.ids
    
    if(type(ids)==list):
            
        idss = "( "
        
        for xid in ids:
            idss = idss + common.getstring(xid) + ", "
        
            
        idss= idss.strip().rstrip(',')
        idss = idss + ")"
    else:
        idss = "(" + ids + ")"
    
    
    xreturnurl = common.getstring(request.vars.returnurl)
    
    providerid = int(common.getid(request.get_vars.providerid))
    providername = ""
    if(providerid == 0):
        provdict = common.getprovider(auth, db)
        providerid = provdict["providerid"]
        
    patientid = int(common.getid(request.get_vars.patientid))
    patientid = int(common.getid(request.post_vars.patientid)) if(patientid == 0) else patientid
    memberid = int(common.getid(request.get_vars.memberid))
    memberid = int(common.getid(request.post_vars.memberid)) if(memberid == 0) else memberid
    treatmentid = int(common.getid(request.get_vars.treatmentid))
    treatmentid = int(common.getid(request.post_vars.treatmentid)) if(treatmentid == 0) else treatmentid
    tplanid = int(common.getid(request.get_vars.tplanid))        
    tplanid = int(common.getid(request.post_vars.tplanid)) if(tplanid == 0) else tplanid
    
    

    doctorid = int(common.getid(request.get_vars.doctorid))
    d1 = doctorid
    doctorid = int(common.getid(request.post_vars.doctorid)) if(doctorid == 0) else doctorid
    d2 = doctorid
    doctorid = int(common.getdefaultdoctor(db,providerid)) if(doctorid==0) else doctorid    
    d3 = doctorid
    
    

    
    doc = db((db.doctor.id == doctorid) & (db.doctor.is_active == True)).select()
    

    
    prov = db((db.provider.id == providerid)&(db.provider.is_active == True)).select()
    mem = db((db.patientmember.id == memberid)&(db.patientmember.is_active == True)).select()
    pat = db((db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid==memberid)).select()
    
    registration = ""
    if(len(prov)>0):
        registration = prov[0]["registration"]    
    
    sql = "SELECT id, medicine,frequency,quantity, remarks from vw_patientprescription where id IN " + idss
    
    
    prescriptions = db.executesql(sql)
    
    
    returnurl = URL('prescription','prescriptions', vars=dict(page=page,providerid=providerid,memberid1=memberid,patientid1=patientid,doctorid1=doctorid,treatmentid1=treatmentid,tplanid1=tplanid,returnurl=xreturnurl))
    prescdate = datetime.date.today().strftime("%d/%m/%Y")
    return dict(prescdate=prescdate, prescriptions=prescriptions,prov=prov,mem=mem,pat=pat,doc=doc,returnurl=returnurl,registration=registration,doctorid=doctorid)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def prescriptions():

    ids = request.vars.records
        
    returnurl = common.getstring(request.vars.returnurl)
    if(returnurl == ""):
        returnurl = URL('admin', 'providerhome')
    
    page = common.getpage(request.vars.page)
    
    patientid1 = 0
    memberid1 = 0
    doctorid1 = 0
    treatmentid1 = 0
    tplanid1 = 0
    prescriptionid = 0
    
    provdict = common.getprovider(auth, db)
    providerid = provdict["providerid"]
    providername = provdict["providername"]     

    patientid1 = int(common.getid(request.get_vars.patientid1))
    patientid1 = int(common.getid(request.post_vars.patientid1)) if(patientid1 == 0) else patientid1
    memberid1 = int(common.getid(request.get_vars.memberid1))    
    memberid1 = int(common.getid(request.post_vars.memberid1)) if(memberid1 == 0) else memberid1
    
    doctorid1 = int(common.getid(request.get_vars.doctorid1))   
    doctorid1 = int(common.getid(request.post_vars.doctorid1)) if(doctorid1 == 0) else doctorid1
    doctorid1 = int(common.getdefaultdoctor(db,providerid)) if(doctorid1==0) else doctorid1    
    
    treatmentid1 = int(common.getid(request.get_vars.treatmentid1))
    treatmentid1 = int(common.getid(request.post_vars.treatmentid1)) if(treatmentid1 == 0) else treatmentid1
    
    tplanid1= int(common.getid(request.get_vars.tplanid1))
    tplanid1 = int(common.getid(request.post_vars.tplanid1)) if(tplanid1 == 0) else tplanid1    

        



    fullname = ""
    patient = ""
    pats = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid1) & (db.vw_memberpatientlist.primarypatientid == memberid1)).select()
    if(len(pats)>0):
        fullname = common.getstring(pats[0].fullname)
        patient = common.getstring(pats[0].patient)

  
    
    sqlquery = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True))

    form = SQLFORM.factory(
           Field('patientmember1', 'string',  default=fullname, label='Patient ID',requires=[IS_NOT_EMPTY(),IS_IN_DB(sqlquery,'vw_memberpatientlist.patient')]),
           Field('doctor', 'integer', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),  default=doctorid1, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active == True)), 'doctor.id', '%(name)s')),
           Field('xpatientmember1', 'string',  default=patient, label='Member ID')
    )


    xpatientmember = form.element('#no_table_patientmember1')
    xpatientmember['_class'] = 'form-control'
    xpatientmember['_placeholder'] = 'Enter Patient Name (first, Last)' 
    xpatientmember['_autocomplete'] = 'off' 

    xdoctor = form.element('#no_table_doctor')
    xdoctor['_class'] = 'form-control'
    xdoctor['_autocomplete'] = 'off'    


    if(ids != None):
        treatmentid1 = int(common.getid(request.get_vars.treatmentid1))
        treatmentid1 = int(common.getid(request.post_vars.treatmentid1)) if(treatmentid1 == 0) else treatmentid1
        
        tplanid1= int(common.getid(request.get_vars.tplanid1))
        tplanid1 = int(common.getid(request.post_vars.tplanid1)) if(tplanid1 == 0) else tplanid1
        
        doctorid1 = int(common.getid(request.get_vars.doctorid1)) 
        doctorid1 = int(common.getid(request.post_vars.doctorid1)) if(doctorid1 == 0) else doctorid1
        doctorid1 = int(common.getdefaultdoctor(db,providerid)) if(doctorid1==0) else doctorid1
        
        if((ids != None)):
            redirect(URL('prescription', 'prescription_report', vars=dict(ids=ids,providerid=providerid,memberid=memberid1,patientid=patientid1,doctorid=doctorid1,treatmentid=treatmentid1,tplanid=tplanid1,returnurl=returnurl)))        
        
    return dict(form=form,page=page,providerid=providerid,providername=providername,tplanid=tplanid1,treatmentid=treatmentid1,returnurl=returnurl)    

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def xprescriptions():

    ids = request.vars.records
        
    returnurl = common.getstring(request.vars.returnurl)
    if(returnurl == ""):
        returnurl = URL('admin', 'providerhome')
    
    patientid = 0
    memberid = 0
    doctorid = 0
    treatmentid = 0
    tplanid = 0
    
    page = common.getpage(request.vars.page)

    prescriptionid = int(common.getid(request.vars.prescriptionid))
   
    if(prescriptionid > 0):    
        prescrp = db(db.prescription.id == prescriptionid).select()
        patientid = int(common.getid(prescrp[0].patientid))
        memberid = int(common.getid(prescrp[0].memberid))
        doctorid = int(common.getid(prescrp[0].doctorid))
        providerid = int(common.getid(prescrp[0].providerid))
        treatmentid = int(common.getid(prescrp[0].treatmentid))
        tplanid= int(common.getid(prescrp[0].tplanid))
    else:
        patientid = int(common.getid(request.vars.patientid))
        memberid = int(common.getid(request.vars.memberid))
        doctorid = int(common.getid(request.vars.doctorid))
        providerid = int(common.getid(request.vars.providerid))
        treatmentid = int(common.getid(request.vars.treatmentid))
        tplanid = int(common.getid(request.vars.tplanid))
        

    providername = ""
    if(providerid == 0):
        provdict = common.getprovider(auth, db)
        providerid = provdict["providerid"]
        providername = provdict["providername"]        
    else:
        provdict = common.getproviderfromid(db, providerid)
        providername = provdict["providername"]        

    if(doctorid == 0):
        doctorid = int(common.getdefaultdoctor(db,providerid))  

    if(type(ids) == list):  
        i = 0
    else:
        j = 0
    if((ids != None)):
        redirect(URL('prescription', 'prescription_report', vars=dict(ids=ids,providerid=providerid,memberid=memberid,patientid=patientid,doctorid=doctorid,treatmentid=treatmentid,tplanid=tplanid,returnurl=returnurl)))

    fullname = ""
    patient = ""
    pats = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid == memberid)).select()
    if(len(pats)>0):
        fullname = common.getstring(pats[0].fullname)
        patient = common.getstring(pats[0].patient)

  
    
    sqlquery = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True))

    form = SQLFORM.factory(
           Field('patientmember1', 'string',  default=fullname, label='Patient ID',requires=[IS_NOT_EMPTY(),IS_IN_DB(sqlquery,'vw_memberpatientlist.patient')]),
           Field('doctor', 'integer', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),  default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active == True)), 'doctor.id', '%(name)s')),
           Field('xpatientmember1', 'string',  default=patient, label='Member ID')
    )


    xpatientmember = form.element('#no_table_patientmember1')
    xpatientmember['_class'] = 'form-control'
    xpatientmember['_placeholder'] = 'Enter Patient Name (first, Last)' 
    xpatientmember['_autocomplete'] = 'off' 

    xdoctor = form.element('#no_table_doctor')
    xdoctor['_class'] = 'form-control'
    xdoctor['_autocomplete'] = 'off'    

    

    #formPres = SQLFORM.factory(\
        #Field('prescriptiondate', 'date', label='Date',  default=datetime.date.today(),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        #Field('doctor', 'integer', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),  label='Drug',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active == True)), 'doctor.id', '%(name)s')),
        #Field('medicine', 'integer', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),  label='Drug',requires=IS_IN_DB(db((db.medicine.providerid==providerid)&(db.medicine.is_active == True)), 'medicine.id', '%(medicine)s:%(strength)s:%(strengthuom)s')),
        #Field('strength', 'string',represent=lambda v, r: '' if v is None else v),
        #Field('strengthuom', 'string',represent=lambda v, r: '' if v is None else v,default="",requires=IS_IN_SET(STRENGTHUOM)),
        #Field('frequency', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        #Field('dosage', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        #Field('quantity', 'string',represent=lambda v, r: '' if v is None else v,default=""),
        #Field('presremarks', 'text',represent=lambda v, r: '' if v is None else v,default=""),
        
    #)
    
    #xdate =  formPres.element('#no_table_prescriptiondate')
    #xdate['_class'] =  'input-group form-control form-control-inline date-picker'
    #xdate['_data-date-format'] = 'dd/mm/yyyy'
    #xdate['_autocomplete'] = 'off'  
    
    #xdoctor = formPres.element('#no_table_doctor')
    #xdoctor['_class'] = 'form-control'
    #xdoctor['_autocomplete'] = 'off'    
    
    #xmedicine = formPres.element('#no_table_medicine')
    #xmedicine['_class'] = 'form-control'
    #xmedicine['_autocomplete'] = 'off'    
    
    #xstrength = formPres.element('#no_table_strength')
    #xstrength['_class'] = 'form-control'
    #xstrength['_autocomplete'] = 'off'    
    
    #xstrengthuom = formPres.element('#no_table_strengthuom')
    #xstrengthuom['_class'] = 'form-control'
    #xstrengthuom['_autocomplete'] = 'off'    
    
    #xfreq = formPres.element('#no_table_frequency')
    #xfreq['_class'] = 'form-control'
    #xfreq['_autocomplete'] = 'off'    
    
    #xdosage = formPres.element('#no_table_dosage')
    #xdosage['_class'] = 'form-control'
    #xdosage['_autocomplete'] = 'off'   
    
    #xqty = formPres.element('#no_table_quantity')
    #xqty['_class'] = 'form-control'
    #xqty['_autocomplete'] = 'off'   
    
    #formPres.element('textarea[name=presremarks]')['_class'] = 'form-control'
    #formPres.element('textarea[name=presremarks]')['_style'] = 'height:100px;line-height:1.0;'
    #formPres.element('textarea[name=presremarks]')['_rows'] = 5
    
    
    ##fromPres = SQLFORM.factory(
             ##Field('medicinename', 'string',  label='', default = "")
          ##)  
       
    #prescriptions = getpresgrid(memberid, patientid, providerid)

    #if formPres.accepts(request,session=session,formname='formpres',keepvalues=True):
        #i  = 0
    #elif formPres.errors:
        #j = 0    
        
    return dict(form=form,page=page,providerid=providerid,providername=providername,tplanid=tplanid,treatmentid=treatmentid,returnurl=returnurl)    


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def yprescriptions():
    
    
    prescriptionid = int(common.getid(request.vars.prescriptionid))

    if(prescriptionid > 0):    
        prescrp = db(db.prescription.id == prescriptionid).select()
        patientid = int(common.getid(prescrp[0].patientid))
        memberid = int(common.getid(prescrp[0].memberid))
        doctorid = int(common.getid(prescrp[0].doctorid))
        providerid = int(common.getid(prescrp[0].providerid))
    else:
        patientid = int(common.getid(request.vars.patientid))
        memberid = int(common.getid(request.vars.memberid))
        doctorid = int(common.getid(request.vars.doctorid))
        providerid = int(common.getid(request.vars.providerid))
    
    
    if(providerid == 0):
        providerdict = common.getprovider(auth, db)
        providerid = providerdict["providerid"]
        providername = providerdict["providername"]        
    else:
        provdict = common.getproviderfromid(db, providerid)
        providername = provdict["providername"]        

    if(doctorid == 0):
        doctorid = int(common.getdefaultdoctor(db,providerid))  

    prescriptions = db((db.vw_patientprescription.providerid == providerid) & \
                              (db.vw_patientprescription.is_active == True) & \
                              (db.vw_patientprescription.patientid == patientid) & \
                              (db.vw_patientprescription.memberid == memberid)).select() 

    returnurl = URL('admin', 'providerhome')

    sqlquery = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True))
    
    fullname = ""
    patient = ""
    pats = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid == memberid)).select()
    if(len(pats)>0):
        fullname = common.getstring(pats[0].fullname)
        patient = common.getstring(pats[0].patient)
    form = SQLFORM.factory(
           Field('patientmember', 'string',  default=fullname, label='Patient ID',requires=[IS_NOT_EMPTY(),IS_IN_DB(sqlquery,'vw_memberpatientlist.patient')]),
           Field('doctor', 'integer', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),  default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active == True)), 'doctor.id', '%(name)s')),
           Field('xpatientmember', 'string',  default=patient, label='Member ID')
                       
    )
       
    xpatientmember = form.element('#no_table_patientmember')
    xpatientmember['_class'] = 'form-control'
    xpatientmember['_placeholder'] = 'Enter Patient Name (first, Last)' 
    xpatientmember['_autocomplete'] = 'off' 

    xdoctor = form.element('#no_table_doctor')
    xdoctor['_class'] = 'form-control'
    xdoctor['_autocomplete'] = 'off'    

        
    return dict(form=form,prescriptions = prescriptions, providerid=providerid, providername=providername,page=1,returnurl=returnurl,patientid=patientid,memberid=memberid)    
    
@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def delete_prescription():
    
    page = request.vars.page
    prescriptionid = common.getid(request.vars.prescriptionid)
    returnurl = URL("admin","providerhome")
    
    providerid = common.getid(request.vars.providerid)
    providername = common.getstring(request.vars.providername)
    patientid = 0
    memberid = 0
    tplanid = 0
    treatmentid  = 0
    doctorid = 0
    
    pres = db((db.prescription.id == prescriptionid) & (db.prescription.is_active == True)).select()
    if(len(pres)>0):
        patientid = common.getid(pres[0].patientid)
        memberid = common.getid(pres[0].memberid)
        tplanid = common.getid(pres[0].tplanid)
        treatmentid = common.getid(pres[0].treatmentid)
        doctorid = common.getid(pres[0].doctorid)
        returnurl = URL('prescription','prescriptions', vars=dict(page=page,providerid=providerid,memberid1=memberid,patientid1=patientid,doctorid1=doctorid,treatmentid1=treatmentid,tplanid1=tplanid,returnurl=returnurl))        
  
    
    form = FORM.confirm('Yes',{'No': returnurl})
    
    if form.accepted:
        db(db.prescription.id == prescriptionid).update(is_active = False)
        redirect(returnurl)  
        
    return dict(form=form,returnurl=returnurl,providerid=providerid,providername=providername,page=0)
