

import os


import urllib

#import sys
#sys.path.append('modules')
from applications.my_pms2.modules import common
#from gluon.contrib import common

#

def generalconsentform():
    
    page = 0
    returnurl = request.vars.returnurl
    
    #if request.args(0) == 'a':
        #response.view = 'default/a.html'
    #if request.args(0) == 'b':
        #response.view = 'default/b.html'   
          
    providerid = int(common.getid(request.vars.providerid))
    prov = db((db.provider.id == providerid)&(db.provider.is_active == True)).select()
    
    registration = ""
    if(len(prov)>0):
        registration = prov[0]["registration"]
    
    docreg = ""    
    doctorid = int(common.getid(request.vars.doctorid))
    doc = db(db.doctor.id == doctorid).select(db.doctor.name,db.doctor.registration)
    if(len(doc)>0):
        docreg = doc[0]["registration"]
    
    patientmember = common.getstring(request.vars.patientmember)
    patarr = patientmember.split(":")
    if(len(patarr)<1):
        patientmember = "No Patient"
    else:
        patientmember = patarr[0]
        
    dentalprocedure = common.getstring(request.vars.dentalprocedure)
    
    response.view = "consentform/" + request.vars.consentform  + ".html"
    
  
    
 
    
    return dict(page=0,  returnurl=returnurl, consentdate=request.vars.consentdate, prov=prov, doctorname=doc[0].name, patientmember=patientmember,dentalprocedure = dentalprocedure,registration=registration,docreg=docreg)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def consentform():
    
    page = 0
    provdict = common.getprovider(auth,db)
    providerid = provdict["providerid"]    
    providername = provdict["providername"]    
    
    
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    pats = db((db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid == memberid) & \
        (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).select()
    
    fullname = ""  #fname lname
    patient = ""   #fname lname : memberid
    
    if(len(pats)>0):
        fullname = pats[0].fullname
        patient = pats[0].patient
    
    doctorid = int(common.getid(request.vars.doctorid))
    treatmentid = int(common.getid(request.vars.treatmentid))
    treats = db(db.treatment.id == treatmentid).select()
    
    source = common.getstring(request.vars.source)
    shortdesc = ""
    
    if(len(treats)>0):
        procid = int(common.getid(treats[0].dentalprocedure))
        procs = db(db.dentalprocedure.id == procid).select()
        if(len(procs)>0):
            shortdesc = common.getstring(procs[0].shortdescription)
    
    if(source == "treatment"):
        returnurl = URL('treatment', 'update_treatment', vars=dict(page=page,imagepage=0,providerid=providerid,treatmentid=treatmentid))
    else:
        returnurl = URL('admin', 'providerhome')
    
    consentforms = os.listdir(os.path.join(request.folder, 'views/consentform'))
    listofconsentforms=[str(consentform).replace(".html","") for consentform in consentforms] 
    listofconsentforms.remove("consentform")
    sqlquery = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True))
    #procquery = db(db.vw_dentalprocedure.is_active == True)
    procquery = db(db.dentalprocedure.is_active == True)
    if(doctorid == 0):
        doctorid = int(common.getdefaultdoctor(db, providerid))
    form = SQLFORM.factory(
        Field('consentdate', 'date', label='Date',  default=datetime.date.today(),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('doctor', 'integer', default=doctorid,  widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),   label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active == True)), 'doctor.id', '%(name)s')),
        #Field('xdentalprocedure',  widget=SQLFORM.widgets.autocomplete(request, db.dentalprocedure.shortdescription, id_field=db.dentalprocedure.id,limitby=(0,10), min_length=1),   label='Dental Procedure',requires=IS_IN_DB(db, 'dentalprocedure.id','%(shortdescription)s')),
        Field('dentalprocedure', 'string',   default=shortdesc, label='Procedure ID',requires=[IS_NOT_EMPTY(),IS_IN_DB(db(db.dentalprocedure.is_active == True),'dentalprocedure.shortdescription', '%(shortdescription)s')]),
        Field('patientmember1', 'string',   default = fullname, label='Patient ID',requires=[IS_NOT_EMPTY(),IS_IN_DB(sqlquery,'vw_memberpatientlist.fullname')]),
        Field('xpatientmember1', 'string',  default = patient, label='Member ID',requires=[IS_NOT_EMPTY(),IS_IN_DB(sqlquery,'vw_memberpatientlist.patient')]),
        Field('consentform',  'list:string', default="GeneralConsentForm", requires=IS_IN_SET(listofconsentforms))
           )
    
    
    xpatientmember = form.element('#no_table_patientmember1')
    xpatientmember['_class'] = 'form-control'
    xpatientmember['_placeholder'] = 'Enter Patient Name (first, Last)' 
    xpatientmember['_autocomplete'] = 'off' 
    

    xdate =  form.element('#no_table_consentdate')
    xdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xdate['_data-date-format'] = 'dd/mm/yyyy'
    xdate['_autocomplete'] = 'off'  
    
    xdoctor = form.element('#no_table_doctor')
    xdoctor['_class'] = 'form-control'
    xdoctor['_autocomplete'] = 'off'    

    
    xdoctor = form.element('#no_table_consentform')
    xdoctor['_class'] = 'form-control'
    xdoctor['_autocomplete'] = 'off'    

    xdentalprocedure = form.element('input',_id='no_table_dentalprocedure')
    xdentalprocedure['_class'] =  'form-control '
    xdentalprocedure['_placeholder'] = 'Enter Dental Procedure Name/Code' 
    xdentalprocedure['_autocomplete'] = 'off'         


    if form.accepts(request,session,keepvalues=True):
        
        if(request.vars.consentform != ""):
            redirect(URL('consentform','generalconsentform', vars=dict(consentform=request.vars.consentform, consentdate=request.vars.consentdate, \
                                                                       providerid=request.vars.providerid, doctorid=request.vars.doctor, dentalprocedure = request.vars.dentalprocedure,\
                                                                       patientmember=request.vars.xpatientmember1,returnurl=returnurl)))
        else:
            redirect(returnurl)
        
    elif form.errors:
        
        session.flash = "Errors in Consent Form " + str(form.errors)
    
    return dict(form=form, providerid=providerid, providername=providername, returnurl=returnurl, page=page)