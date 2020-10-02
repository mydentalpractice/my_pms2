from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)

import requests
import urllib2
import base64
import json
import datetime
import os


from applications.my_pms2.modules import common
from applications.my_pms2.modules import status
from applications.my_pms2.modules import states
from applications.my_pms2.modules import gender

from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import mdpreligare
from applications.my_pms2.modules import mdputils
from applications.my_pms2.modules import mdptreatment
from applications.my_pms2.modules import mdpprocedure
from applications.my_pms2.modules import mdpabhicl

def getvalue(jobj, key1, defval):

    keys = jobj.keys()

    for key in keys:
        if(key.lower() == key1.lower()):
            return jobj.get(key,"defval")


    return defval


def vwdentalprocedure_selector():
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])    

    freetreatment = common.getboolean(request.vars.freetreatment)
    newmember = common.getboolean(request.vars.newmember)

    patientid = int(common.getid(request.vars.patientid))
    memberid  = int(common.getid(request.vars.memberid))

    rows = db((db.vw_memberpatientlist.patientid == patientid)&(db.vw_memberpatientlist.primarypatientid == memberid)).select()
    procedurepriceplancode = 'RLG102'
    if(len(rows)>0):
        procedurepriceplancode = rows[0].hmoplan.procedurepriceplancode
    if(request.vars.vwdentalprocedure == ""):
        pattern = '%'
    else:
        pattern = '%' + request.vars.vwdentalprocedure.capitalize() + '%'


    selected = [row.shortdescription for row in db((db.vw_procedurepriceplan_relgr.is_active == True)  &  \
                                                   (db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode) & \
                                                   (db.vw_procedurepriceplan_relgr.relgrproc == True) & \
                                                   (db.vw_procedurepriceplan_relgr.shortdescription.like(pattern))).select(db.vw_procedurepriceplan_relgr.shortdescription)]



    return ''.join([DIV(k,
                        _onclick="jQuery('#no_table_vwdentalprocedure').val('%s')" % k,
                        _onmouseover="this.style.backgroundColor='cyan'",
                        _onmouseout="this.style.backgroundColor='white'",
                        _style="z-index:500000;width:100%;font-family:verdana;font-size:12px;color:black;font-weight:normal"
                        ).xml() for k in selected])




@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def settle_transaction():

    page = int(common.getid(request.vars.page))
    page = page if(page >0) else 1
    imagepage = 1

    providerdict = common.getprovider(auth, db)
    providerid = int(common.getid(providerdict["providerid"]))
    providername = providerdict["providername"]    

    treatmentid = int(common.getid(request.vars.treatmentid))
    treatmentprocedureid = int(common.getid(request.vars.treatmentprocedureid))
    r = db(db.treatment_procedure.id == treatmentprocedureid).select(db.treatment_procedure.policy_name)
    policy_name = common.getstring(r[0].policy_name) if len(r) == 1 else None

    returnurl = URL('treatment','update_treatment', vars=dict(page=page,imagepage=imagepage,treatmentid=treatmentid,providerid=providerid))


    r = db((db.vw_treatmentprocedure.id == treatmentprocedureid) & (db.vw_treatmentprocedure.treatmentid == treatmentid)).select(\
        db.vw_treatmentprocedure.procedurecode, db.vw_treatmentprocedure.altshortdescription)

    procedurename = "" if(len(r) == 0) else  r[0].procedurecode + ": " + r[0].altshortdescription

    form = FORM.confirm('Yes?',{'No':URL('treatment','update_treatment', vars=dict(page=page,imagepage=imagepage,treatmentid=treatmentid,providerid=providerid))})

    if form.accepted:

        orlgr = mdpreligare.ReligareXXX(db,providerid) if(policy_name == "Policy399") else mdpreligare.Religare(db,providerid) 

        rsp = orlgr.settleTransaction(treatmentid,treatmentprocedureid)    

        jsonrsp = json.loads(rsp)
        if(jsonrsp["result"] == "fail"):
            redirect(URL('religare','religareerror',vars=dict(errorcode=jsonrsp["error_code"],returnurl=returnurl)))
        redirect(returnurl)

    return dict(form=form,procedurename=procedurename,providerid=providerid,providername=providername,treatmentid=treatmentid,treatmentprocedureid=treatmentprocedureid,returnurl=returnurl)



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def void_transaction():

    page = int(common.getid(request.vars.page))
    page = page if(page > 0) else page
    imagepage = 1

    providerdict = common.getprovider(auth, db)
    providerid = int(common.getid(providerdict["providerid"]))
    providername = providerdict["providername"]    

    treatmentid = int(common.getid(request.vars.treatmentid))
    treatmentprocedureid = int(common.getid(request.vars.treatmentprocedureid))
    r = db(db.treatment_procedure.id == treatmentprocedureid).select(db.treatment_procedure.policy_name)
    policy_name = common.getstring(r[0].policy_name) if len(r) == 1 else None

    returnurl = URL('treatment','update_treatment', vars=dict(page=page,imagepage=imagepage,treatmentid=treatmentid,providerid=providerid))


    r = db((db.vw_treatmentprocedure.id == treatmentprocedureid) & (db.vw_treatmentprocedure.treatmentid == treatmentid)).select(\
        db.vw_treatmentprocedure.procedurecode, db.vw_treatmentprocedure.altshortdescription)

    procedurename = "" if(len(r) == 0) else r[0].procedurecode + ": " + r[0].altshortdescription

    form = FORM.confirm('Yes?',{'No':URL('treatment','update_treatment', vars=dict(page=page,imagepage=imagepage,treatmentid=treatmentid,providerid=providerid))})

    if form.accepted:
        orlgr = mdpreligare.ReligareXXX(db,providerid) if(policy_name == "Policy399") else mdpreligare.Religare(db,providerid) 
        rsp = orlgr.voidTransaction(treatmentid,treatmentprocedureid)    

        jsonrsp = json.loads(rsp)
        if(jsonrsp["result"] == "fail"):
            redirect(URL('religare','religareerror',vars=dict(errorcode=jsonrsp["error_code"],returnurl=returnurl)))
        redirect(returnurl)

    return dict(form=form,procedurename=procedurename,providerid=providerid,providername=providername,treatmentid=treatmentid,treatmentprocedureid=treatmentprocedureid,returnurl=returnurl)


def getproceduregrid(providerid,tplanid,treatmentid,memberid,patientid,authorization,authorized,preauthorized,page,hmopatientmember,writablflag,webadmin):

    # procedures grid
    query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True))
    if((hmopatientmember == True) | (session.religare == True)):
        fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription,\
                db.vw_treatmentprocedure.tooth,db.vw_treatmentprocedure.quadrant,
                db.vw_treatmentprocedure.procedurefee,db.vw_treatmentprocedure.inspays,db.vw_treatmentprocedure.copay,db.vw_treatmentprocedure.status,\
                db.vw_treatmentprocedure.treatmentdate, db.vw_treatmentprocedure.relgrproc)


        headers={
            'vw_treatmentprocedure.procedurecode':'Code',
            'vw_treatmentprocedure.altshortdescription':'Description',
            'vw_treatmentprocedure.tooth':'Tooth',
            'vw_treatmentprocedure.quadrant':'Quadrant',
            'vw_treatmentprocedure.procedurefee':'Procedure Cost',
            'vw_treatmentprocedure.inspays':'Insurance Pays',
            'vw_treatmentprocedure.copay':'Co-Pay',
            'vw_treatmentprocedure.status':'Status',
            'vw_treatmentprocedure.treatmentdate':'Treatment Date'
        }

    else:
        fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription, \
                db.vw_treatmentprocedure.tooth,db.vw_treatmentprocedure.quadrant,
                db.vw_treatmentprocedure.procedurefee,db.vw_treatmentprocedure.status,\
                db.vw_treatmentprocedure.treatmentdate,db.vw_treatmentprocedure.relgrproc)

        headers={
            'vw_treatmentprocedure.procedurecode':'Code',
            'vw_treatmentprocedure.altshortdescription':'Description',
            'vw_treatmentprocedure.tooth':'Tooth',
            'vw_treatmentprocedure.quadrant':'Quadrant',
            'vw_treatmentprocedure.procedurefee':'Procedure Cost',
            'vw_treatmentprocedure.status':'Status',
            'vw_treatmentprocedure.treatmentdate':'Treatment Date'
        }





    maxtextlengths = {'vw_treatmentprocedure.altshortdescription':100,'vw_treatmentprocedure.relgrprocdesc':100,'vw_treatmentprocedure.status':32}


    db.vw_treatmentprocedure.procedurecode.represent=lambda v, r: '' if v is None else v
    db.vw_treatmentprocedure.altshortdescription.represent=lambda v, r: '' if v is None else v
    db.vw_treatmentprocedure.procedurefee.represent=lambda v, r: 0 if v is None else v
    db.vw_treatmentprocedure.inspays.represent=lambda v, r: 0 if v is None else v
    db.vw_treatmentprocedure.copay.represent=lambda v, r: 0 if v is None else v
    db.vw_treatmentprocedure.status.represent=lambda v, r: 'Open' if v is None else v
    db.vw_treatmentprocedure.relgrprocdesc.represent=lambda v, r: '' if v is None else v
    db.vw_treatmentprocedure.relgrproc.writable = False
    db.vw_treatmentprocedure.relgrproc.readable = False



    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)


    formProcedure = SQLFORM.grid(query=query,
                                 headers=headers,
                                 fields=fields,
                                 paginate=10,
                                 maxtextlengths=maxtextlengths,
                                 orderby=None,
                                 exportclasses=exportlist,
                                 links_in_grid=False,
                                 searchable=False,
                                 create=False,
                                 deletable=False,
                                 editable=False,
                                 details=False,
                                 user_signature=True
                                 )      


    return formProcedure



def download():
    return response.download(request, db)




#Get ABHICL Patient. Enter member's ABHICL ID, get the patient details and 
#display on patient screen
def abhicl():

    message = ""
    providerdict = common.getprovider(auth, db)
    providerid = int(common.getid(providerdict["providerid"]))
    providername = providerdict["providername"]
    returnurl = URL('admin','providerhome')  

    
    abhiclid = request.vars.abhiclid
    abhiclpolicy = request.vars.abhiclpolicy 
    abhiclpolicy = "ABHI" if ((abhiclpolicy == "") | (abhiclpolicy == None)) else abhiclpolicy
    
    form = SQLFORM.factory(
        Field('abhiclid', 'string',  label='ABHICL ID',requires=IS_NOT_EMPTY(),default=abhiclid),
        Field('abhiclpolicy', 'string',  label='ABHICL ID',requires=IS_NOT_EMPTY(),default=abhiclpolicy)
    )

    x1 = form.element('input',_id='no_table_abhiclid')
    x1['_class'] =  'form-control placeholder-no-fix'
    x1['_placeholder'] =  "Enter Member's ABHICL ID"
    x1['_autocomplete'] =  'off'
    
    x2 = form.element('input',_id='no_table_abhiclpolicy')
    x2['_class'] =  'form-control placeholder-no-fix'
    x2['_placeholder'] =  "Enter ABHICL Policy"
    x2['_autocomplete'] =  'off'

    if form.process().accepted:
        #call Select Document
        abhiclid = form.vars.abhiclid
        abhiclpolicy= request.vars.abhiclpolicy
        redirect(URL('abhicl','abhiclpatient',vars=dict(providerid=providerid,abhiclid = abhiclid,abhiclpolicy=abhiclpolicy)))
        
        response.flash = ""
    elif form.errors:
        message = "ABHICLID Form Error " + str(form.errors)


    return dict(form=form,providername=providername,providerid=providerid,returnurl=returnurl,\
                abhiclid = abhiclid,abhiclpolicy=abhiclpolicy,message=message )    




def abhiclpatient():
    
    
    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getproviderfromid(db, providerid)
    providername = common.getstring(provdict["providername"])    

    returnurl = URL('admin','providerhome') 


    abhiclid  = request.vars.abhiclid
    abhiclpolicy  = request.vars.abhiclpolicy

    oabhicl = mdpabhicl.ABHICL(db, providerid)
    rsp = oabhicl.getabhiclmember(abhiclid)
    patobj = json.loads(rsp)
    
    if(patobj["result"] == "fail"):
        return redirect(returnurl)
    
    profile={}
    profile = patobj["profile"]
    memberid = int(profile["memberid "])
    patientid = int(profile["patientid"])
    
    
    query = ((db.patientmember.id == memberid) & (db.patientmember.is_active == True))

    members = db(query).select(db.patientmember.ALL,db.company.name, db.hmoplan.name, db.groupregion.groupregion,db.groupregion.id,
                               left = [db.company.on (db.company.id == db.patientmember.company), db.hmoplan.on(db.hmoplan.id == db.patientmember.hmoplan),\
                                       db.groupregion.on(db.groupregion.id == db.patientmember.groupregion)]
                               )



    member = members[0].patientmember.patientmember
    fname = members[0].patientmember.fname
    lname = members[0].patientmember.lname
    cell = members[0].patientmember.cell
    email = members[0].patientmember.email
    city = members[0].patientmember.city
    st = members[0].patientmember.st
    regid = int(common.getid(members[0].groupregion.id))
    
    formA = SQLFORM.factory(
                    Field('patientmember','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default=members[0].patientmember.patientmember,requires=IS_NOT_EMPTY(), label="Member/Patient ID",writable=False, readable=True),
                    Field('groupref','string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default=members[0].patientmember.groupref, label='Employee ID',writable=False, readable=True),
                    Field('dob','date', label='DOB',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'), default=members[0].patientmember.dob,writable=False, readable=True),
                    Field('title','string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default=members[0].patientmember.title,label='Title',requires=IS_IN_SET(gender.PATTITLE),writable=False, readable=True),
                    Field('fname', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default=members[0].patientmember.fname, label='First',requires=IS_NOT_EMPTY(),writable=False, readable=True),
                    Field('mname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '),  default=members[0].patientmember.mname, label='Middle',writable=False, readable=True),
                    Field('lname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '),  default=members[0].patientmember.lname, label='Last',requires=IS_NOT_EMPTY(),writable=False, readable=True),
                    Field('gender','string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default=members[0].patientmember.gender,label='Gender',requires=IS_IN_SET(gender.GENDER),writable=False, readable=True),
                    Field('address1', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default=members[0].patientmember.address1,label='Address 1', requires=IS_NOT_EMPTY(),writable=True, readable=True),
                    Field('address2', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),  default=members[0].patientmember.address2,label='Address 2',requires=IS_NOT_EMPTY(),writable=True, readable=True),
                    Field('address3', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '),  default=members[0].patientmember.address3,label='Address 3',writable=True, readable=True),

                    Field('city', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '), default=city,label='City',requires = IS_EMPTY_OR(IS_IN_SET(states.CITIES))),
                    Field('st', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '), default=st,label='State',requires = IS_EMPTY_OR(IS_IN_SET(states.STATES))),

                    Field('pin', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default=members[0].patientmember.pin,label='Pin',requires=IS_NOT_EMPTY(),writable=True, readable=True),
                    Field('telephone', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default=members[0].patientmember.telephone,label='Telephone',writable=False, readable=True),
                    
                    Field('cell', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default=members[0].patientmember.cell,label='Cell',writable=True, readable=True),
                    Field('email', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'), default=members[0].patientmember.email,label='Email',writable=True, readable=True), 
                    Field('enrollmentdate','date',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'),  label='Enrollment Date',default=members[0].patientmember.enrollmentdate,writable=False, readable=True),
                    Field('terminationdate','date', label='Termination Date',default=members[0].patientmember.terminationdate,writable=False, readable=True),
                    Field('duedate','date', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'), label='Due Date',default=members[0].patientmember.duedate,writable=False, readable=True),
                    Field('premstartdt','date', label='Prem. Start Date',default=members[0].patientmember.premstartdt,writable=False, readable=True),
                    Field('premenddt','date', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'), label='Prem. End Date',default=members[0].patientmember.premenddt,writable=False, readable=True),
                    Field('status', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '),  label='Status',default=members[0].patientmember.status,requires = IS_IN_SET(status.STATUS),writable=False, readable=True),
                    Field('provider',widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='form-control '),  default=members[0].patientmember.provider, requires=IS_IN_DB(db, 'provider.id', '%(providername)s'),writable=False, readable=True),
                    Field('company', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_style="width:100%;height:35px",_class='form-control '), default=members[0].company.name,writable=False, readable=True ),
                    Field('hmoplan', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_style="width:100%;height:35px",_class='form-control '), default=members[0].hmoplan.name, writable=False, readable=True),
                    Field('groupregion', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px;",_class='form-control '), default=regid, requires=IS_IN_DB(db, 'groupregion.id', '%(groupregion)s'),writable=True),
                    Field('newmember','boolean',label='Member',default=common.getboolean(members[0].patientmember.newmember),writable=False),
                    Field('freetreatment','boolean',label='Member',default=common.getboolean(members[0].patientmember.freetreatment),writable=False)
                   )

    if(formA.process().accepted):

        #save addr1,2,3,city,st,pin,cell,email,groupregion
        db(db.patientmember.id == memberid).update(address1=formA.vars.address1,address2=formA.vars.address2,address3=formA.vars.address3,\
                                                   city=formA.vars.city,st=formA.vars.st,groupregion=formA.vars.groupregion,email=formA.vars.email,cell=formA.vars.cell)

        redirect(URL('religare','religarepatient',vars=dict(providerid=providerid,abhiclid=abhiclid,abhiclpolicy=abhiclpolicy)))

    return dict(providername=providername, providerid = providerid, formA=formA,\
                memberid=memberid, patientid=patientid,abhiclid=abhiclid,abhiclpolicy=abhiclpolicy,\
                member=member,fname=fname,lname=lname,cell=cell,email=email,page=1,\
                returnurl=returnurl)






#New Treatment
def abhicltreatment():

    providerid = request.vars.providerid
    memberid = request.vars.memberid
    patientid = request.vars.patientid
    abhiclpolicy = request.vars.abhiclpolicy
    abhiclid=request.vars.abhiclid
    
    provdict = common.getproviderfromid(db, providerid)
    providername = common.getstring(provdict["providername"])


    p = db((db.vw_memberpatientlist.primarypatientid == memberid) & \
           (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.patientmember,\
                                                                    db.vw_memberpatientlist.groupref,\
                                                                    db.vw_memberpatientlist.patienttype,\
                                                                    db.vw_memberpatientlist.hmopatientmember,\
                                                                    db.vw_memberpatientlist.freetreatment,\
                                                                    db.vw_memberpatientlist.newmember)

    patientmember = p[0].patientmember if len(p) == 1 else ""
    groupref = p[0].groupref if len(p) == 1 else ""
    patienttype = p[0].patienttype if len(p) == 1 else ""
    hmopatientmember = bool(common.getboolean(p[0].hmopatientmember)) if len(p) == 1 else True
    freetreatment = bool(common.getboolean(p[0].freetreatment)) if len(p) == 1 else True
    newmember = bool(common.getboolean(p[0].newmember)) if len(p) == 1 else False

    #new Treatment API
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],providerid)
    rsp = otrtmnt.newtreatment(memberid,patientid,abhiclpolicy)
    treatmentobj = json.loads(rsp)

    treatmentid = int(common.getid(treatmentobj["treatmentid"]))
    tplanid = int(common.getid(treatmentobj["tplanid"]))
    doctorid = int(common.getid(treatmentobj["doctorid"]))
    patientname = common.getstring(treatmentobj["patientname"])
    fullname = ""
    treatment = common.getstring(treatmentobj["treatment"])
    procedurepriceplancode = common.getstring(treatmentobj["plan"])

    chiefcomplaint = common.getstring(treatmentobj["chiefcomplaint"])
    description = common.getstring(treatmentobj["description"])

    d = db(db.doctor.id == doctorid).select(db.doctor.name)
    doctorname = common.getstring(d[0].name)


    #default for religare treatments
    authorization = common.getboolean(treatmentobj["authorization"])
    preauthorized = common.getboolean(treatmentobj["authorized"])
    authorized = common.getboolean(treatmentobj["authorized"])
    preauthorizeerror = False
    authorizeerror = False

    #determine treatment status   
    defsts = common.getstring(treatmentobj["status"])
    defsts = defsts if((defsts != None) & (defsts != "")) else 'Started'



    procedureid = 0
    ucrfee = 0    
    patient = ''
    altshortdescription = ''
    title = ''


    #page
    page       = 1
    imagepage  = 1
    memberpage = 1





    medicalalert = False



    rows = None

    treatments = db(db.treatment.id == treatmentid).select()
    authorizationurl = URL('reports', 'treatmentreport', vars=dict(page=page, providerid=providerid,treatmentid=treatmentid))

    totaltreatmentcost = 0
    totalactualtreatmentcost = 0
    remarks = ""

    writablflag = True
    formTreatment = None
    formProcedure = None
    currentnotes = ""

    webadmin = False

    if(len(treatments) > 0):

        treatment = common.getstring(treatments[0].treatment)
        tplanid = int(common.getid(treatments[0].treatmentplan))
        procedureid = int(common.getid(treatments[0].dentalprocedure))
        doctorid = int(common.getid(treatments[0].doctor))
        currnotes = common.getstring(treatments[0].description)

        docs=db(db.doctor.id == doctorid).select(db.doctor.name)
        totaltreatmentcost = float(common.getvalue(treatments[0].treatmentcost)) #this is the actual treatment cost = total treatment cost unless it is changed by provider
        totalactualtreatmentcost = float(common.getvalue(treatments[0].actualtreatmentcost))   #this is total UCRR
        authorized = common.getboolean(treatments[0].authorized) & (webadmin == True)


        procs = db(db.vw_procedurepriceplan.id == procedureid).select()  
        if(len(procs) > 0):
            ucrfee = common.getvalue(procs[0].ucrfee)
            altshortdescription = common.getstring(procs[0].altshortdescription)
            remarks =  common.getstring(procs[0].remarks)

        tplans = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.provider==providerid) & (db.treatmentplan.is_active == True)).select()



        if(len(tplans) > 0):
            memberid = tplans[0].primarypatient
            patientid = tplans[0].patient
            patienttype = tplans[0].patienttype
            patientname = common.getstring(tplans[0].patientname).strip()

            rows = db((db.vw_memberpatientlist.primarypatientid == memberid)&(db.vw_memberpatientlist.patientid == patientid)&(db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).\
                select()
            companyid = ""
            if(len(rows)>0):
                title = rows[0].title
                fullname = common.getstring(rows[0].fullname).strip()
                patientmember = common.getstring(rows[0].patientmember).strip()
                patient = common.getstring(rows[0].patient).strip()
                membername = common.getstring(rows[0].fullname).strip()
                hmopatientmember = rows[0].hmopatientmember
                procedurepriceplancode = rows[0].procedurepriceplancode
                newmember = common.getboolean(rows[0].newmember)          
                freetreatment = common.getboolean(rows[0].freetreatment)                    
                companyid = int(common.getstring(rows[0].company))
                cos = db(db.company.id == companyid).select()
                # No Authorization till procedures are added.
                procs = db((db.treatment_procedure.treatmentid == treatmentid)&(db.treatment_procedure.is_active==True)).count()                
                authorization = common.getboolean(cos[0].authorizationrequired) & (procs>0)




        #medical alerts
        medicalalerts = False
        alerts = db((db.medicalnotes.patientid == patientid) & (db.medicalnotes.memberid == memberid)).select()
        if(len(alerts)>0):
            medicalalerts = medicalalerts | common.getboolean(alerts[0].allergic)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].bp)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].heart)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].cardiac)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].diabetes)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].anyother)



        #determine treatment status   
        defsts = common.getstring(treatments[0].status)
        defsts = defsts if((defsts != None) & (defsts != "")) else 'Started'

        if(defsts == 'Sent for Authorization'):
            preauthorized = True

        if(defsts == 'Authorized'):
            preauthorized = True
            authorized = True


        writablflag = (not authorization) | (((not preauthorized) & (not authorized)&(not webadmin))|((webadmin)))

        enddate = common.getdt(treatments[0].enddate)
        #Chief Complant and Notes(Description) is readonly when new religare treatment is created with no procedures.
        formTreatment = SQLFORM.factory(
            Field('patientmember', 'string',  label='Patient', default = fullname,\
                  requires=[IS_NOT_EMPTY(),IS_IN_DB(db(db.vw_memberpatientlist.providerid == providerid), 'vw_memberpatientlist.fullname','%(fullname)s')],writable=False),
            Field('xmemberid', 'string',  label='Member',default=memberid),
            Field('treatment','string',label='Treatment No.', default=treatments[0].treatment),
            Field('chiefcomplaint','string',label='Chief Complaint', default=treatments[0].chiefcomplaint),
            Field('description','text', label='Description', default=treatments[0].description,writable=False),
            Field('quadrant','string', label='Quadrant(s)', default='',writable=writablflag),
            Field('tooth','string', label='Tooth/Teeth', default='',writable=writablflag),
            Field('startdate', 'date', label='From Date',default=treatments[0].startdate, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))),writable=writablflag),
            Field('enddate', 'date', label='To Date',default=enddate, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))),writable=writablflag),
            Field('status', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border ',_onchange='onstatuschange()'),label='Status',default=defsts, requires = IS_IN_SET(status.TREATMENTSTATUS),writable=False,readable=True),  
            Field('ucrfee', 'double', label='Total UCR',default=totalactualtreatmentcost,writable=False),  
            Field('treatmentcost', 'double', label='Total Treament Cost',default=totaltreatmentcost,writable=False),  
            Field('copay', 'double', label='Total Copay',default=treatments[0].copay, writable = False),  
            Field('inspay', 'double', label='Total Ins. Pays',default=treatments[0].inspay, writable=False),  
            Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
            Field('vwdentalprocedure', 'string',   label='Procedure ID'),
            Field('vwdentalprocedurecode', 'string',   label='Procedure Code'),
            Field('xaction', 'string', default = 'UpdateTreatment')
        )    

        doc = formTreatment.element('#no_table_doctor')
        if(doc != None):
            doc['_class'] = 'form-control'
            doc['_style'] = 'width:100%'


        xtreatment = formTreatment.element('input',_id='no_table_treatment')
        if(xtreatment != None):
            xtreatment['_class'] =  'form-control'
            xtreatment['_type'] =  'text'
            xtreatment['_autocomplete'] = 'off'     
            xtreatment['_readonly'] = 'true'

        xvwdentalprocedurecode = formTreatment.element('input',_id='no_table_vwdentalprocedurecode')
        if(xvwdentalprocedurecode != None):
            xvwdentalprocedurecode['_class'] =  'form-control '
            xvwdentalprocedurecode['_placeholder'] = 'Enter Dental Procedure Code' 
            xvwdentalprocedurecode['_autocomplete'] = 'off'         
            xvwdentalprocedurecode['_style'] = 'width:100%'

        xcc = formTreatment.element('input',_id='no_table_chiefcomplaint')
        if(xcc != None):
            xcc['_class'] =  'form-control '
            xcc['_placeholder'] = 'Enter Chief Complaint' 
            xcc['_autocomplete'] = 'off'         
            xcc['_style'] = 'width:100%'
            
        xvwdentalprocedure = formTreatment.element('input',_id='no_table_vwdentalprocedure')
        if(xvwdentalprocedure != None):
            xvwdentalprocedure['_class'] =  'form-control '
            xvwdentalprocedure['_placeholder'] = 'Enter Dental Procedure Name' 
            xvwdentalprocedure['_autocomplete'] = 'off'         
            xvwdentalprocedure['_style'] = 'width:100%'

        xtooth = formTreatment.element('input',_id='no_table_tooth')
        if(xtooth != None):
            xtooth['_class'] =  'form-control '
            xtooth['_placeholder'] = 'Enter Tooth Number' 
            xtooth['_autocomplete'] = 'off'         
            xtooth['_style'] = 'width:100%'

        xquad = formTreatment.element('input',_id='no_table_quadrant')
        if(xquad != None):
            xquad['_class'] =  'form-control '
            xquad['_placeholder'] = 'Enter Quadrant' 
            xquad['_autocomplete'] = 'off'         
            xquad['_style'] = 'width:100%'

        if(writablflag):


            xstartdate = formTreatment.element('input',_id='no_table_startdate')
            xstartdate['_class'] =  'input-group form-control form-control-inline date-picker'
            xstartdate['_data-date-format'] = 'dd/mm/yyyy'
            xstartdate['_autocomplete'] = 'off' 

            xenddate = formTreatment.element('input',_id='no_table_enddate')
            xenddate['_class'] =  'input-group form-control form-control-inline date-picker'
            xenddate['_data-date-format'] = 'dd/mm/yyyy'
            xenddate['_autocomplete'] = 'off' 





        # procedures grid
        formProcedure = None


        returnurl = URL('admin','providerhome')
        if formTreatment.accepts(request,session=session,formname='formtreatment',keepvalues=True):
            treatmentcost = float(common.getvalue(formTreatment.vars.treatmentcost))
            doctorid = int(common.getid(formTreatment.vars.doctor))
            docs = db(db.doctor.id == doctorid).select()
            doctorname = docs[0].name

            if(formTreatment.vars.status == 'Authorized'):
                authorized = True
            else:
                authorized = False

            db(db.treatment.id == treatmentid).update(\
                treatment = formTreatment.vars.treatment,
                chiefcomplaint = formTreatment.vars.chiefcomplaint,
                description  = formTreatment.vars.description,
                startdate = formTreatment.vars.startdate,
                enddate = formTreatment.vars.enddate,
                status = formTreatment.vars.status,
                authorized = authorized,
                actualtreatmentcost = 0,
                treatmentcost = treatmentcost,
                quadrant = '',
                tooth = '',
                dentalprocedure = 0, 
                doctor = doctorid,
                modified_on = common.getISTFormatCurrentLocatTime(),
                modified_by = providerid,

            )    


            otrtmnt.updatetreatmentcostandcopay(treatmentid,tplanid)
            #calculatecost(tplanid)
            #calculatecopay(db, tplanid,memberid)
            #calculateinspays(tplanid)
            #calculatedue(tplanid)

            #db.commit()                

            db.treatmentnotes.update_or_insert(db.treatmentnotes.treatment == treatmentid, treatment = treatmentid, notes = formTreatment.vars.prescription)   

            if(changeinnotes(currnotes, formTreatment.vars.description)):
                common.lognotes(db,formTreatment.vars.description,treatmentid)

            response.flash = "Treatment Details Updated!"
            redirect(returnurl)
        elif formTreatment.errors:
            session.flash = "Error - Updating Treatment Report!" + str(formTreatment.errors)
            redirect(returnurl)

    showprocgrid = False

    return dict(formTreatment=formTreatment, formProcedure=formProcedure,  \
                page=page, memberpage=memberpage, imagepage=imagepage,procedureid=procedureid,\
                providerid=providerid, providername=providername,doctorid=doctorid,doctorname=docs[0].name,\
                patientmember=patientmember, memberid=memberid,membername=membername, patientid=patientid,patientname=patientname, hmopatientmember=hmopatientmember,\
                treatment=treatment,treatmentid=treatmentid,tplanid=tplanid,medicalalerts=medicalalerts,\
                authorization=authorization,authorizationurl=authorizationurl,writablflag=writablflag,
                preauthorized=preauthorized,preauthorizeerror=preauthorizeerror,authorizeerror=authorizeerror,authorized=authorized,webadmin=webadmin,returnurl=returnurl,\
                freetreatment=freetreatment,newmember=newmember,showprocgrid = showprocgrid,abhiclid=abhiclid,abhiclpolicy=abhiclpolicy
                )        


   

def updateabhicltreatment():

    providerid = int(request.vars.providerid)
    treatmentid = int(request.vars.treatmentid)
    memberid = int(request.vars.memberid)
    patientid = int(request.vars.patientid)
    abhiclpolicy = request.vars.abhiclpolicy
    abhiclid=request.vars.abhiclid
    
    provdict = common.getproviderfromid(db, providerid)
    providername = common.getstring(provdict["providername"])

    patientmember =""
    groupref = ""
    patienttype = "P"
    hmopatientmember = True
    freetreatment = True
    newmember = False


  
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],providerid)
    rsp = otrtmnt.gettreatment(treatmentid)
    treatmentobj = json.loads(rsp)    

    #get treatment Treatment API
    treatmentid = int(common.getid(treatmentobj["treatmentid"]))
    tplanid = int(common.getid(treatmentobj["tplanid"]))
    doctorid = int(common.getid(treatmentobj["doctorid"]))
    patientname = common.getstring(treatmentobj["patientname"])
    fullname = ""
    treatment = common.getstring(treatmentobj["treatment"])
    procedurepriceplancode = common.getstring(treatmentobj["plan"])

    chiefcomplaint = common.getstring(treatmentobj["chiefcomplaint"])
    description = common.getstring(treatmentobj["description"])

    d = db(db.doctor.id == doctorid).select(db.doctor.name)
    doctorname = common.getstring(d[0].name)


    #default for religare treatments
    authorization = common.getboolean(treatmentobj["authorization"])
    preauthorized = common.getboolean(treatmentobj["authorized"])
    authorized = common.getboolean(treatmentobj["authorized"])
    preauthorizeerror = False
    authorizeerror = False

    #determine treatment status   
    defsts = common.getstring(treatmentobj["status"])
    defsts = defsts if((defsts != None) & (defsts != "")) else 'Started'


    #page
    page       = 1  
    imagepage  = 1
    memberpage = 1

    medicalalert = False



    rows = None

    treatments = db(db.treatment.id == treatmentid).select()
    authorizationurl = URL('reports', 'treatmentreport', vars=dict(page=page, providerid=providerid,treatmentid=treatmentid))

    totaltreatmentcost = 0
    totalactualtreatmentcost = 0
    remarks = ""

    writablflag = True
    formTreatment = None
    formProcedure = None
    currentnotes = ""

    webadmin = False

    if(len(treatments) > 0):

        treatment = common.getstring(treatments[0].treatment)
        tplanid = int(common.getid(treatments[0].treatmentplan))
        procedureid = int(common.getid(treatments[0].dentalprocedure))
        doctorid = int(common.getid(treatments[0].doctor))
        currnotes = common.getstring(treatments[0].description)

        docs=db(db.doctor.id == doctorid).select(db.doctor.name)
        totaltreatmentcost = float(common.getvalue(treatments[0].treatmentcost)) #this is the actual treatment cost = total treatment cost unless it is changed by provider
        totalactualtreatmentcost = float(common.getvalue(treatments[0].actualtreatmentcost))   #this is total UCRR
        authorized = common.getboolean(treatments[0].authorized) & (webadmin == True)


        procs = db(db.vw_procedurepriceplan.id == procedureid).select()  
        if(len(procs) > 0):
            ucrfee = common.getvalue(procs[0].ucrfee)
            altshortdescription = common.getstring(procs[0].altshortdescription)
            remarks =  common.getstring(procs[0].remarks)

        tplans = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.provider==providerid) & (db.treatmentplan.is_active == True)).select()



        if(len(tplans) > 0):
            memberid = tplans[0].primarypatient
            patientid = tplans[0].patient
            patienttype = tplans[0].patienttype
            patientname = common.getstring(tplans[0].patientname).strip()

            rows = db((db.vw_memberpatientlist.primarypatientid == memberid)&(db.vw_memberpatientlist.patientid == patientid)&(db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).\
                select()
            companyid = ""
            if(len(rows)>0):
                title = rows[0].title
                fullname = common.getstring(rows[0].fullname).strip()
                patientmember = common.getstring(rows[0].patientmember).strip()
                patient = common.getstring(rows[0].patient).strip()
                membername = common.getstring(rows[0].fullname).strip()
                hmopatientmember = rows[0].hmopatientmember
                procedurepriceplancode = rows[0].procedurepriceplancode
                newmember = common.getboolean(rows[0].newmember)          
                freetreatment = common.getboolean(rows[0].freetreatment)                    
                companyid = int(common.getstring(rows[0].company))
                cos = db(db.company.id == companyid).select()
                # No Authorization till procedures are added.
                procs = db((db.treatment_procedure.treatmentid == treatmentid)&(db.treatment_procedure.is_active==True)).count()                
                authorization = common.getboolean(cos[0].authorizationrequired) & (procs>0)




        #medical alerts
        medicalalerts = False
        alerts = db((db.medicalnotes.patientid == patientid) & (db.medicalnotes.memberid == memberid)).select()
        if(len(alerts)>0):
            medicalalerts = medicalalerts | common.getboolean(alerts[0].allergic)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].bp)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].heart)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].cardiac)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].diabetes)
            medicalalerts = medicalalerts | common.getboolean(alerts[0].anyother)



        #determine treatment status   
        defsts = common.getstring(treatments[0].status)
        defsts = defsts if((defsts != None) & (defsts != "")) else 'Started'

        if(defsts == 'Sent for Authorization'):
            preauthorized = True

        if(defsts == 'Authorized'):
            preauthorized = True
            authorized = True


        writablflag = (not authorization) | (((not preauthorized) & (not authorized)&(not webadmin))|((webadmin)))

        enddate = common.getdt(treatments[0].enddate)
        formTreatment = SQLFORM.factory(
            Field('patientmember', 'string',  label='Patient', default = fullname,\
                  requires=[IS_NOT_EMPTY(),IS_IN_DB(db(db.vw_memberpatientlist.providerid == providerid), 'vw_memberpatientlist.fullname','%(fullname)s')],writable=False),
            Field('xmemberid', 'string',  label='Member',default=memberid),
            Field('treatment','string',label='Treatment No.', default=treatments[0].treatment),
            Field('chiefcomplaint','string',label='Chief Complaint', default=treatments[0].chiefcomplaint,writable=writablflag),
            Field('description','text', label='Description', default=treatments[0].description,writable=writablflag),
            Field('quadrant','string', label='Quadrant(s)', default='',writable=writablflag),
            Field('tooth','string', label='Tooth/Teeth', default='',writable=writablflag),
            Field('startdate', 'date', label='From Date',default=treatments[0].startdate, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))),writable=writablflag),
            Field('enddate', 'date', label='To Date',default=enddate, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))),writable=writablflag),
            Field('status', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border ',_onchange='onstatuschange()'),label='Status',default=defsts, requires = IS_IN_SET(status.TREATMENTSTATUS),writable=False,readable=True),  
            Field('ucrfee', 'double', label='Total UCR',default=totalactualtreatmentcost,writable=False),  
            Field('treatmentcost', 'double', label='Total Treament Cost',default=totaltreatmentcost,writable=False),  
            Field('copay', 'double', label='Total Copay',default=treatments[0].copay, writable = False),  
            Field('inspay', 'double', label='Total Ins. Pays',default=treatments[0].inspay, writable=False),  
            Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
            Field('vwdentalprocedure', 'string',   label='Procedure ID'),
            Field('vwdentalprocedurecode', 'string',   label='Procedure Code'),
            Field('xaction', 'string', default = 'UpdateTreatment')
        )    

        doc = formTreatment.element('#no_table_doctor')
        if(doc != None):
            doc['_class'] = 'form-control'
            doc['_style'] = 'width:100%'


        xtreatment = formTreatment.element('input',_id='no_table_treatment')
        if(xtreatment != None):
            xtreatment['_class'] =  'form-control'
            xtreatment['_type'] =  'text'
            xtreatment['_autocomplete'] = 'off'     
            xtreatment['_readonly'] = 'true'

        xvwdentalprocedurecode = formTreatment.element('input',_id='no_table_vwdentalprocedurecode')
        if(xvwdentalprocedurecode != None):
            xvwdentalprocedurecode['_class'] =  'form-control '
            xvwdentalprocedurecode['_placeholder'] = 'Enter Dental Procedure Code' 
            xvwdentalprocedurecode['_autocomplete'] = 'off'         
            xvwdentalprocedurecode['_style'] = 'width:100%'

        xvwdentalprocedure = formTreatment.element('input',_id='no_table_vwdentalprocedure')
        if(xvwdentalprocedure != None):
            xvwdentalprocedure['_class'] =  'form-control '
            xvwdentalprocedure['_placeholder'] = 'Enter Dental Procedure Name' 
            xvwdentalprocedure['_autocomplete'] = 'off'         
            xvwdentalprocedure['_style'] = 'width:100%'

        xtooth = formTreatment.element('input',_id='no_table_tooth')
        if(xtooth != None):
            xtooth['_class'] =  'form-control '
            xtooth['_placeholder'] = 'Enter Tooth Number' 
            xtooth['_autocomplete'] = 'off'         
            xtooth['_style'] = 'width:100%'

        xquad = formTreatment.element('input',_id='no_table_quadrant')
        if(xquad != None):
            xquad['_class'] =  'form-control '
            xquad['_placeholder'] = 'Enter Quadrant' 
            xquad['_autocomplete'] = 'off'         
            xquad['_style'] = 'width:100%'

        if(writablflag):
            formTreatment.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
            formTreatment.element('textarea[name=description]')['_rows'] = 5
            formTreatment.element('textarea[name=description]')['_class'] = 'form-control'

            xstartdate = formTreatment.element('input',_id='no_table_startdate')
            xstartdate['_class'] =  'input-group form-control form-control-inline date-picker'
            xstartdate['_data-date-format'] = 'dd/mm/yyyy'
            xstartdate['_autocomplete'] = 'off' 

            xenddate = formTreatment.element('input',_id='no_table_enddate')
            xenddate['_class'] =  'input-group form-control form-control-inline date-picker'
            xenddate['_data-date-format'] = 'dd/mm/yyyy'
            xenddate['_autocomplete'] = 'off' 



            cc = formTreatment.element('input', _id='no_table_chiefcomplaint')
            cc['_class'] = 'form-control'
            cc['_style'] = 'width:100%'
            cc['_type'] =  'text'


        # procedures grid
        formProcedure = getproceduregrid(providerid,tplanid,treatmentid,memberid,patientid,authorization,authorized,preauthorized,page,hmopatientmember,writablflag,webadmin)

        returnurl = URL('treatment','list_treatments',vars=dict(page=page,providerid=providerid,memberid=memberid,patientid=patientid))
        if formTreatment.accepts(request,session=session,formname='formtreatment',keepvalues=True):
            treatmentcost = float(common.getvalue(formTreatment.vars.treatmentcost))
            doctorid = int(common.getid(formTreatment.vars.doctor))
            docs = db(db.doctor.id == doctorid).select()
            doctorname = docs[0].name

            if(formTreatment.vars.status == 'Authorized'):
                authorized = True
            else:
                authorized = False

            db(db.treatment.id == treatmentid).update(\
                treatment = formTreatment.vars.treatment,
                chiefcomplaint = formTreatment.vars.chiefcomplaint,
                description  = formTreatment.vars.description,
                startdate = formTreatment.vars.startdate,
                enddate = formTreatment.vars.enddate,
                status = defsts, #formTreatment.vars.status,
                authorized = authorized,
                actualtreatmentcost = 0,
                treatmentcost = treatmentcost,
                quadrant = '',
                tooth = '',
                dentalprocedure = 0, 
                doctor = doctorid,
                modified_on = common.getISTFormatCurrentLocatTime(),
                modified_by = providerid,

            )    



            otrtmnt.updatetreatmentcostandcopay(treatmentid,tplanid)


            db.treatmentnotes.update_or_insert(db.treatmentnotes.treatment == treatmentid, treatment = treatmentid, notes = formTreatment.vars.prescription)   

            if(common.changeinnotes(currnotes, formTreatment.vars.description)):
                common.lognotes(db,formTreatment.vars.description,treatmentid)

            response.flash = "Treatment Details Updated!"
            redirect(returnurl)
        elif formTreatment.errors:
            session.flash = "Error - Updating Treatment Report!" + str(formTreatment.errors)
            redirect(returnurl)

    showprocgrid = False

    return dict(formTreatment=formTreatment, formProcedure=formProcedure,  \
                page=page, memberpage=memberpage, imagepage=imagepage,procedureid=procedureid,\
                providerid=providerid, providername=providername,doctorid=doctorid,doctorname=docs[0].name,\
                patientmember=patientmember, memberid=memberid,membername=membername, patientid=patientid,patientname=patientname, hmopatientmember=hmopatientmember,\
                treatment=treatment,treatmentid=treatmentid,tplanid=tplanid,medicalalerts=medicalalerts,\
                authorization=authorization,authorizationurl=authorizationurl,writablflag=writablflag,
                preauthorized=preauthorized,preauthorizeerror=preauthorizeerror,authorizeerror=authorizeerror,authorized=authorized,webadmin=webadmin,returnurl=returnurl,\
                freetreatment=freetreatment,newmember=newmember,showprocgrid = showprocgrid,\
                abhiclid=abhiclid,abhiclpolicy=abhiclpolicy
                )        



      
def addabhiclprocedure():


    treatmentid = int(common.getid(request.vars.treatmentid))
    providerid = int(common.getid(request.vars.providerid))
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    abhiclid = request.vars.abhiclid
    abhiclpolicy = request.vars.abhiclpolicy
    tooth = request.vars.tooth
    quadrant = request.vars.quadrant
    chiefcomplaint = request.vars.chiefcomplaint
    
    remarks = ""
    
    
    procedurepriceplancode = mdputils.getprocedurepriceplancodeformember(db,providerid,memberid,patientid,abhiclpolicy)

    procs = db((db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode) &\
               (db.vw_procedurepriceplan_relgr.procedurecode == request.vars.vwdentalprocedurecode)).select(\
                   db.vw_procedurepriceplan_relgr.relgrprocfee,\
                   db.vw_procedurepriceplan_relgr.service_id,\
                   db.vw_procedurepriceplan_relgr.procedurecode
               )


    service_id = procs[0].service_id if len(procs) == 1 else "9999"
    procedurename = procs[0].procedurecode if len(procs) == 1 else "9999"
    procedurefee = procs[0].relgrprocfee if len(procs) == 1 else "0"
    procedurecode = procs[0].procedurecode if len(procs) == 1 else "G0104"

    db(db.treatment.id == treatmentid).update(chiefcomplaint=chiefcomplaint)
    oabhicl = mdpabhicl.ABHICL(db,providerid)
    rsp = oabhicl.addABHICLProcedureToTreatment(treatmentid, 
                                               procedurepriceplancode, 
                                               procedurecode, 
                                               
                                               tooth, 
                                               quadrant, 
                                               remarks, 
                                               abhiclid, 
                                               abhiclpolicy)
    
    jsonobj = json.loads(rsp)

    if(jsonobj["result"] == "success"):
        redirect(URL('abhicl','updateabhicltreatment',vars=dict(providerid=providerid,treatmentid=treatmentid,memberid=memberid,\
                                                                patientid=patientid,abhicl=abhicl,abhiclpolicy=abhiclpolicy)))    
    else:
        redirect(URL('abhicl','abhiclerror',vars=dict(errorcode=jsonobj["error_code"])))


    return dict()



def abhiclerror():

    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])

    returnurl = URL('admin','providerhome') if common.getstring(request.vars.returnurl) == "" else common.getstring(request.vars.returnurl)

    errorheader = "Error"
    errorcode = 0 if common.getstring(request.vars.errorcode) == "" else request.vars.errorcode

    mssg = db((db.rlgerrormessage.code == errorcode) & (db.rlgerrormessage.is_active == True)).select()
    errormssg = "No Error Message" if errorcode == 0 else (errorcode + ": Blank error message"  if(len(mssg) == 0) else errorcode + ":\n" + common.getstring(mssg[0].externalmessage))



    return dict(errorheader=errorheader,providerid=providerid, providername=providername,errormssg=errormssg,returnurl=returnurl)



