from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)




#import sys
#sys.path.append('modules')
from applications.my_pms2.modules import common
from applications.my_pms2.modules import status
from applications.my_pms2.modules import states
from applications.my_pms2.modules import gender
from applications.my_pms2.modules import cycle

from cycle import WEEKDAYS
from cycle import AMS
from cycle import PMS

#from gluon.contrib import common
#from gluon.contrib import status
#from gluon.contrib import states
#from gluon.contrib import gender
#from gluon.contrib import cycle

#from gluon.contrib.cycle import WEEKDAYS
#from gluon.contrib.cycle import AMS
#from gluon.contrib.cycle import PMS


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def delete_role():
    
    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]
    
    roleid = int(common.getid(request.vars.roleid))

    returnurl = URL('doctor', 'list_roles')
    
    form = FORM.confirm('Yes',{'No': returnurl})
    
    if form.accepted:
        db(db.role.id == roleid).update(is_active = False)  
	session.flash = "Role deleted!"
        redirect(returnurl)
        
    return dict(form=form,returnurl=returnurl,providerid=providerid,providername=providername,page=0)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_roles():

    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]

     
    query = ((db.role_default.id > 0) )
    fields = (db.role_default.role, db.role_default.id)
    db.role_default.id.readable = False

    
    headers = {\
        'role_default.role' : 'Role'
    }
    
    links = [\
        dict(header=CENTER('Edit'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=30, _height=30),_href=URL("doctor","update_role",vars=dict(roleid=row.id))))),
        dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),_href=URL("doctor","delete_role",vars=dict(roleid=row.id)))))
        ]
    
    orderby = None #(db.role_d.role)
        
    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)    

    returnurl = URL('admin', 'providerhome')
    
   
    
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

    return dict(form=form,page=0,returnurl=returnurl,providerid=providerid,providername=providername)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def xlist_roles():

    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]

     
    query = ((db.role.providerid == providerid) & (db.role.is_active == True))
    fields = (db.role.role,db.role.is_active)
    db.role.is_active.readable = False

    
    headers = {\
        'role.role' : 'Role'
        
    }
    
    links = [\
        dict(header=CENTER('Edit'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=30, _height=30),_href=URL("doctor","update_role",vars=dict(roleid=row.id))))),
        dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),_href=URL("doctor","delete_role",vars=dict(roleid=row.id)))))
        ]
    
    orderby = (db.role.role)
        
    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)    

    returnurl = URL('admin', 'providerhome')
    
   
    
    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            orderby=orderby,
                            exportclasses=exportlist,
                            maxtextlengths={'role.role':128},
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
def new_role():
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    returnurl = URL('doctor', 'list_roles')
    page = 0
    
    db.role.is_active.default = True
    db.role.providerid.default = providerid
    
    crud.settings.create_next = URL('doctor','list_roles')
    
    formA = crud.create(db.role,message="New Role added!")  
    
    xrole =  formA.element('input',_id='role_role')
    xrole['_class'] = 'form-control'
    
    return dict(formA=formA, returnurl=returnurl,page=page,providerid=providerid,providername=providername)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def delete_speciality():
    
    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]
    
    specialityid = int(common.getid(request.vars.specialityid))

    returnurl = URL('doctor', 'list_specialities')
    
    form = FORM.confirm('Yes',{'No': returnurl})
    
    if form.accepted:
        db(db.speciality.id == specialityid).update(is_active = False)
	session.flash = "Speciality deleted!"
        redirect(returnurl)
        
    return dict(form=form,returnurl=returnurl,providerid=providerid,providername=providername,page=0)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_specialities():

    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]

     
    query = ((db.speciality.providerid == providerid) & (db.speciality.is_active == True))
    fields = (db.speciality.speciality,db.speciality.is_active)
    
    db.speciality.is_active.readable = False
    
    headers = {\
        'speciality.speciality' : 'Speciality'
        
    }
    
    links = [\
        dict(header=CENTER('Edit'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=30, _height=30),_href=URL("doctor","update_speciality",vars=dict(specialityid=row.id))))),
        dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),_href=URL("doctor","delete_speciality",vars=dict(specialityid=row.id)))))
        ]
    
    orderby = (db.speciality.speciality)
        
    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)    

    returnurl = URL('admin', 'providerhome')
    
   
    
    
    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            orderby=orderby,
                            exportclasses=exportlist,
                            maxtextlengths={'speciality.speciality':128},
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
def new_speciality():
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    returnurl = URL('doctor', 'list_specialities')
    page = 0
    
    db.speciality.is_active.default = True
    db.speciality.providerid.default = providerid
    
    crud.settings.create_next = URL('doctor','list_specialities')
    
    formA = crud.create(db.speciality,message="New Speciality added!")  
    
    xspeciality =  formA.element('input',_id='speciality_speciality')
    xspeciality['_class'] = 'form-control'
    
    return dict(formA=formA, returnurl=returnurl,page=page,providerid=providerid,providername=providername)



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def xlist_doctors():

    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]

     
    query = ((db.doctor.providerid == providerid) & (db.doctor.is_active == True))
    fields = (db.doctor.name,db.doctor.role,db.doctor.speciality,db.doctor.email, db.doctor.cell,db.doctor.registration,db.doctor.color)
    

    
    headers = {\
        'doctor.name' : 'Name',
        'doctor.role' : 'Role',
        'doctor.speciality' : 'Speciality',
        'doctor.email' : 'Email',
        'doctor.cell' : 'Cell',
        'doctor.registration' : 'Registration',
        'doctor.color' : 'Color'
    }
    
    links = [\
        dict(header=CENTER('Edit'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=30, _height=30),_href=URL("doctor","update_doctor",vars=dict(doctorid=row.id))))),
        dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),_href=URL("doctor","delete_doctor",vars=dict(doctorid=row.id)))))
        ]
    
    orderby = (db.doctor.name)
        
    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)    

    returnurl = URL('admin', 'providerhome')
    
   
    
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

    return dict(form=form,page=0,returnurl=returnurl,providerid=providerid,providername=providername)



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def new_doctor():
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    returnurl = URL('doctor', 'list_doctors')
    page = 0
    
    db.doctor.is_active.default = True
    db.doctor.providerid.default = providerid
    db.doctor.practice_owner.default = False
    
    crud.settings.create_next = URL('doctor','list_doctors')
    
    if(request.vars.personnel == 'doctor'):
	db.doctor.name.requires = IS_NOT_EMPTY()
	db.doctor.registration.requires = IS_NOT_EMPTY()
	db.doctor.cell.requires = IS_NOT_EMPTY()
	db.doctor.email.requires = IS_NOT_EMPTY()
	db.doctor.color.requires = IS_NOT_EMPTY()
	db.doctor.stafftype.default = 'Doctor'
	db.doctor.role.requires  = IS_IN_DB(db((db.role_default.is_active == True)),db.role_default.id, '%(role)s')
	db.doctor.speciality.requires = IS_IN_DB(db((db.speciality_default.is_active == True)),db.speciality_default.id, '%(speciality)s')
	
    else:
	db.doctor.name.requires = IS_NOT_EMPTY()
	db.doctor.registration.requires = ""
	db.doctor.cell.requires = ""
	db.doctor.email.requires = ""
	db.doctor.color.requires = ""
	db.doctor.role.requires  = IS_IN_DB(db((db.role_default.is_active == True)),db.role_default.id, '%(role)s')
	db.doctor.speciality.requires = ""
	db.doctor.speciality.widget = ""
	db.doctor.registration.writable = False
	db.doctor.speciality.writable = False
	db.doctor.color.writable = False
	db.doctor.stafftype.default = 'Staff'


   
    formA = crud.create(db.doctor,message="New Docto/Staff added!")  
    xname = formA.element('input',_id='doctor_name')
    xname['_class'] = 'form-control'

    xcell = formA.element('input',_id='doctor_cell')
    if(xcell != None):
	xcell['_class'] = 'form-control'

    
    xemail = formA.element('input',_id='doctor_email')
    
    if(xemail != None):
	xemail['_class'] = 'form-control'

        
    xreg = formA.element('input',_id='doctor_registration')
    if(xreg != None):
	xreg['_class'] = 'form-control'

    xcolor = formA.element('input',_id='doctor_color')
    if(xcolor != None):
	xcolor['_class'] = 'form-control'
	
    
    return dict(formA=formA, returnurl=returnurl,page=page,providerid=providerid,providername=providername)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def update_role():
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    roleid = int(common.getid(request.vars.roleid))
    
    returnurl = URL('doctor', 'list_roles')
    page = 0
    
    db.role.is_active.default = True
    db.role.providerid.default = providerid
    
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = returnurl
    
    
    
    formA = crud.update(db.role, roleid,cast=int, message="Role information updated!")  ## company Details entry form
    
    xrole =  formA.element('input',_id='role_role')
    xrole['_class'] = 'form-control'
    
    
    return dict(formA=formA, returnurl=returnurl,page=page,providerid=providerid,providername=providername)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def update_speciality():
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    specialityid = int(common.getid(request.vars.specialityid))
    
    returnurl = URL('doctor', 'list_specialities')
    page = 0
    
    db.speciality.is_active.default = True
    db.speciality.providerid.default = providerid
    
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = returnurl
    
    
    
    formA = crud.update(db.speciality, specialityid,cast=int, message="Speciality information updated!")  ## company Details entry form
    
    xspeciality =  formA.element('input',_id='speciality_speciality')
    xspeciality['_class'] = 'form-control'
    
    
    return dict(formA=formA, returnurl=returnurl,page=page,providerid=providerid,providername=providername)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def update_doctor():
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    doctorid = int(common.getid(request.vars.doctorid))
    
    returnurl = URL('doctor', 'list_doctors')
    page = 0
    
    db.doctor.is_active.default = True
    db.doctor.providerid.default = providerid
    
    
    if(request.vars.personnel == 'doctor'):
	    db.doctor.name.requires = IS_NOT_EMPTY()
	    db.doctor.registration.requires = IS_NOT_EMPTY()
	    db.doctor.cell.requires = IS_NOT_EMPTY()
	    db.doctor.email.requires = IS_NOT_EMPTY()
	    db.doctor.color.requires = IS_NOT_EMPTY()
	    db.doctor.stafftype.default = 'Doctor'
	    db.doctor.role.requires  = IS_IN_DB(db((db.role_default.is_active == True)),db.role_default.id, '%(role)s')
	    db.doctor.speciality.requires = IS_IN_DB(db((db.speciality_default.is_active == True)),db.speciality_default.id, '%(speciality)s')
	    
	    
	    
    else:
	db.doctor.name.requires = IS_NOT_EMPTY()
	db.doctor.registration.requires = ""
	db.doctor.cell.requires = ""
	db.doctor.email.requires = ""
	db.doctor.color.requires = ""
	db.doctor.speciality.requires = ""
	
	db.doctor.speciality.widget = ""
	db.doctor.registration.writable = False
	db.doctor.speciality.writable = False
	db.doctor.color.writable = False
	db.doctor.stafftype.default = 'Staff'    
	db.doctor.role.requires  = IS_IN_DB(db((db.role_default.is_active == True)),db.role_default.id, '%(role)s')
	
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = returnurl
    
    
    
    formA = crud.update(db.doctor, doctorid,cast=int, message="Doctor/Staff information updated!")  ## company Details entry form
    
    
    xname = formA.element('input',_id='doctor_name')
    xname['_class'] = 'form-control'

    xcell = formA.element('input',_id='doctor_cell')
    if(xcell != None):
	xcell['_class'] = 'form-control'

    
    xemail = formA.element('input',_id='doctor_email')
    
    if(xemail != None):
	xemail['_class'] = 'form-control'

        
    xreg = formA.element('input',_id='doctor_registration')
    if(xreg != None):
	xreg['_class'] = 'form-control'

    xcolor = formA.element('input',_id='doctor_color')
    if(xcolor != None):
	xcolor['_class'] = 'form-control'
	
    
    return dict(formA=formA, returnurl=returnurl,page=page,providerid=providerid,providername=providername)



def refer_doctor_provider():
    
    docs = db((db.doctor.is_active == True) & (db.doctor.stafftype == 'Doctor')).select()
    
    for doc in docs:
	providerid = doc.providerid
	r = db((db.doctor_ref.ref_code == "PRV") & (db.doctor_ref.ref_id == providerid) & (db.doctor_ref.doctor_id == doc.id)).select()
	if(len(r)==0):
	    db.doctor_ref.insert(ref_code = 'PRV',ref_id = providerid, doctor_id = doc.id)
    
    return dict()

    
@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_doctors():
    
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    page = 0

    
    returnurl = URL('admin', 'providerhome')
     

    staff = db((db.doctor.providerid == providerid) & (db.doctor.is_active == True)).select(db.doctor.ALL, db.role_default.ALL, db.speciality_default.ALL,\
                                                                                            left=[db.role_default.on(db.role_default.id == db.doctor.role),\
                                                                                                  db.speciality_default.on(db.speciality_default.id == db.doctor.speciality)])
                                                                                            
    
    
    timings = db((db.doctor.providerid == providerid) & (db.doctor.is_active == True) & (db.doctor.stafftype == 'Doctor')).\
        select(db.doctor.ALL, db.role.ALL, db.speciality.ALL, db.doctortiming.ALL,\
            left=[db.role.on(db.role.id == db.doctor.role),\
                  db.speciality.on(db.speciality.id == db.doctor.speciality),\
                  db.doctortiming.on((db.doctortiming.doctor == db.doctor.id)&(db.doctortiming.is_active == True))])
    
    
    return dict(page=page, staff=staff, timings=timings, returnurl=returnurl, providerid=providerid, providername=providername)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def delete_doctortiming():
    
    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]
    
    doctorid = int(common.getid(request.vars.doctorid))

    returnurl = URL('doctor', 'list_doctors')
    
    form = FORM.confirm('Yes',{'No': returnurl})
    
    if form.accepted:
        db(db.doctortiming.doctor == doctorid).update(is_active = False)
	session.flash = "Doctor Timing deleted!"
        redirect(returnurl)
        
    return dict(form=form,returnurl=returnurl,providerid=providerid,providername=providername,page=0)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def delete_doctor():
    
    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]
    
    doctorid = int(common.getid(request.vars.doctorid))

    returnurl = URL('doctor', 'list_doctors')
    
    form = FORM.confirm('Yes',{'No': returnurl})
    
    if form.accepted:
        db(db.doctor.id == doctorid).update(is_active = False)
	session.flash = "Doctor deleted!"
        redirect(returnurl)
        
    return dict(form=form,returnurl=returnurl,providerid=providerid,providername=providername,page=0)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_doctor_timings():
    
    return dict()

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def doctor_timings():

    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]
    page = 0
    
    doctorid = int(common.getid(request.vars.doctorid))  
    doctorname =""
    dr = db(db.doctor.id == doctorid).select()
    if(len(dr)>0):
        doctorname = dr[0].name
    
    
    doctortimingid = int(common.getid(request.vars.doctortimingid))    

    returnurl = URL('doctor', 'list_doctors')
    
    
    mon_day_chk = False
    mon_lunch_chk = False
    mon_del_chk = False
    mon_starttime_1 = ""
    mon_endtime_1 = ""
    mon_starttime_2 = ""
    mon_endtime_2 = ""
    mon_visitinghours = ""
    
    tue_day_chk = False
    tue_lunch_chk = False
    tue_del_chk = False
    tue_starttime_1 = ""
    tue_endtime_1 = ""
    tue_starttime_2 = ""
    tue_endtime_2 = ""
    tue_visitinghours = ""

    wed_day_chk = False
    wed_lunch_chk = False
    wed_del_chk = False
    wed_starttime_1 = ""
    wed_endtime_1 = ""
    wed_starttime_2 = ""
    wed_endtime_2 = ""
    wed_visitinghours = ""

    thu_day_chk = False
    thu_lunch_chk = False
    thu_del_chk = False
    thu_starttime_1 = ""
    thu_endtime_1 = ""
    thu_starttime_2 = ""
    thu_endtime_2 = ""
    thu_visitinghours = ""

    fri_day_chk = False
    fri_lunch_chk = False
    fri_del_chk = False
    fri_starttime_1 = ""
    fri_endtime_1 = ""
    fri_starttime_2 = ""
    fri_endtime_2 = ""
    fri_visitinghours = ""
    
    sat_day_chk = False
    sat_lunch_chk = False
    sat_del_chk = False
    sat_starttime_1 = ""
    sat_endtime_1 = ""
    sat_starttime_2 = ""
    sat_endtime_2 = ""
    sat_visitinghours = ""
    
    sun_day_chk = False
    sun_lunch_chk = False
    sun_del_chk = False
    sun_starttime_1 = ""
    sun_endtime_1 = ""
    sun_starttime_2 = ""
    sun_endtime_2 = ""
    sun_visitinghours = ""
    
    visitinghours = 'Not Set'
    lunchbreak = 'Not Set'
    
    if(doctortimingid > 0):
        # need to get information from database and set the defauls
        dts = db(db.doctortiming.id == doctortimingid).select()
        mon_day_chk = common.getboolean(dts[0].mon_day_chk)
        mon_lunch_chk = common.getboolean(dts[0].mon_lunch_chk)
        mon_del_chk = common.getboolean(dts[0].mon_del_chk)
        mon_starttime_1 = common.getstring(dts[0].mon_starttime_1)
        mon_endtime_1 = common.getstring(dts[0].mon_endtime_1)
        mon_starttime_2 = common.getstring(dts[0].mon_starttime_2)
        mon_endtime_2 = common.getstring(dts[0].mon_endtime_2)
        mon_visitinghours = common.getstring(dts[0].mon_visitinghours)
        
	tue_day_chk = common.getboolean(dts[0].tue_day_chk)
	tue_lunch_chk = common.getboolean(dts[0].tue_lunch_chk)
	tue_del_chk = common.getboolean(dts[0].tue_del_chk)
	tue_starttime_1 = common.getstring(dts[0].tue_starttime_1)
	tue_endtime_1 = common.getstring(dts[0].tue_endtime_1)
	tue_starttime_2 = common.getstring(dts[0].tue_starttime_2)
	tue_endtime_2 = common.getstring(dts[0].tue_endtime_2)
	tue_visitinghours = common.getstring(dts[0].tue_visitinghours)

	wed_day_chk = common.getboolean(dts[0].wed_day_chk)
	wed_lunch_chk = common.getboolean(dts[0].wed_lunch_chk)
	wed_del_chk = common.getboolean(dts[0].wed_del_chk)
	wed_starttime_1 = common.getstring(dts[0].wed_starttime_1)
	wed_endtime_1 = common.getstring(dts[0].wed_endtime_1)
	wed_starttime_2 = common.getstring(dts[0].wed_starttime_2)
	wed_endtime_2 = common.getstring(dts[0].wed_endtime_2)
	wed_visitinghours = common.getstring(dts[0].wed_visitinghours)

	thu_day_chk = common.getboolean(dts[0].thu_day_chk)
	thu_lunch_chk = common.getboolean(dts[0].thu_lunch_chk)
	thu_del_chk = common.getboolean(dts[0].thu_del_chk)
	thu_starttime_1 = common.getstring(dts[0].thu_starttime_1)
	thu_endtime_1 = common.getstring(dts[0].thu_endtime_1)
	thu_starttime_2 = common.getstring(dts[0].thu_starttime_2)
	thu_endtime_2 = common.getstring(dts[0].thu_endtime_2)
	thu_visitinghours = common.getstring(dts[0].thu_visitinghours)

	fri_day_chk = common.getboolean(dts[0].fri_day_chk)
	fri_lunch_chk = common.getboolean(dts[0].fri_lunch_chk)
	fri_del_chk = common.getboolean(dts[0].fri_del_chk)
	fri_starttime_1 = common.getstring(dts[0].fri_starttime_1)
	fri_endtime_1 = common.getstring(dts[0].fri_endtime_1)
	fri_starttime_2 = common.getstring(dts[0].fri_starttime_2)
	fri_endtime_2 = common.getstring(dts[0].fri_endtime_2)
	fri_visitinghours = common.getstring(dts[0].fri_visitinghours)

	sat_day_chk = common.getboolean(dts[0].sat_day_chk)
	sat_lunch_chk = common.getboolean(dts[0].sat_lunch_chk)
	sat_del_chk = common.getboolean(dts[0].sat_del_chk)
	sat_starttime_1 = common.getstring(dts[0].sat_starttime_1)
	sat_endtime_1 = common.getstring(dts[0].sat_endtime_1)
	sat_starttime_2 = common.getstring(dts[0].sat_starttime_2)
	sat_endtime_2 = common.getstring(dts[0].sat_endtime_2)
	sat_visitinghours = common.getstring(dts[0].sat_visitinghours)

	sun_day_chk = common.getboolean(dts[0].sun_day_chk)
	sun_lunch_chk = common.getboolean(dts[0].sun_lunch_chk)
	sun_del_chk = common.getboolean(dts[0].sun_del_chk)
	sun_starttime_1 = common.getstring(dts[0].sun_starttime_1)
	sun_endtime_1 = common.getstring(dts[0].sun_endtime_1)
	sun_starttime_2 = common.getstring(dts[0].sun_starttime_2)
	sun_endtime_2 = common.getstring(dts[0].sun_endtime_2)
	sun_visitinghours = common.getstring(dts[0].sun_visitinghours)
        
        visitinghours = common.getstring(dts[0].visitinghours)
        lunchbreak = common.getstring(dts[0].lunchbreak)
    
    formA = SQLFORM.factory(
        Field('mon_day_chk', 'boolean', default=mon_day_chk),        
        Field('mon_lunch_chk', 'boolean', default=mon_lunch_chk),        
        Field('mon_del_chk', 'boolean', default=mon_del_chk),        
        Field('mon_starttime_1', 'string', default=mon_starttime_1,requires=IS_IN_SET(AMS)),
        Field('mon_endtime_1', 'string', default=mon_endtime_1,requires=IS_IN_SET(AMS)),
        Field('mon_starttime_2', 'string', default=mon_starttime_2,requires=IS_IN_SET(AMS)),
        Field('mon_endtime_2', 'string', default=mon_endtime_2,requires=IS_IN_SET(AMS)),
        Field('mon_visitinghours', 'string', default=mon_visitinghours),
        
        Field('tue_day_chk', 'boolean', default=tue_day_chk),        
        Field('tue_lunch_chk', 'boolean', default=tue_lunch_chk),        
        Field('tue_del_chk', 'boolean', default=tue_del_chk),        
        Field('tue_starttime_1', 'string', default=tue_starttime_1,requires=IS_IN_SET(AMS)),
        Field('tue_endtime_1', 'string', default=tue_endtime_1,requires=IS_IN_SET(AMS)),
        Field('tue_starttime_2', 'string', default=tue_starttime_2,requires=IS_IN_SET(AMS)),
        Field('tue_endtime_2', 'string', default=tue_endtime_2,requires=IS_IN_SET(AMS)),
        Field('tue_visitinghours', 'string', default=tue_visitinghours),
        
        Field('wed_day_chk', 'boolean', default=wed_day_chk),        
        Field('wed_lunch_chk', 'boolean', default=wed_lunch_chk),        
        Field('wed_del_chk', 'boolean', default=wed_del_chk),        
        Field('wed_starttime_1', 'string', default=wed_starttime_1,requires=IS_IN_SET(AMS)),
        Field('wed_endtime_1', 'string', default=wed_endtime_1,requires=IS_IN_SET(AMS)),
        Field('wed_starttime_2', 'string', default=wed_starttime_2,requires=IS_IN_SET(AMS)),
        Field('wed_endtime_2', 'string', default=wed_endtime_2,requires=IS_IN_SET(AMS)),
        Field('wed_visitinghours', 'string', default=wed_visitinghours),
        
        Field('thu_day_chk', 'boolean', default=thu_day_chk),        
        Field('thu_lunch_chk', 'boolean', default=thu_lunch_chk),        
        Field('thu_del_chk', 'boolean', default=thu_del_chk),        
        Field('thu_starttime_1', 'string', default=thu_starttime_1,requires=IS_IN_SET(AMS)),
        Field('thu_endtime_1', 'string', default=thu_endtime_1,requires=IS_IN_SET(AMS)),
        Field('thu_starttime_2', 'string', default=thu_starttime_2,requires=IS_IN_SET(AMS)),
        Field('thu_endtime_2', 'string', default=thu_endtime_2,requires=IS_IN_SET(AMS)),
        Field('thu_visitinghours', 'string', default=thu_visitinghours),
        
        Field('fri_day_chk', 'boolean', default=fri_day_chk),        
        Field('fri_lunch_chk', 'boolean', default=fri_lunch_chk),        
        Field('fri_del_chk', 'boolean', default=fri_del_chk),        
        Field('fri_starttime_1', 'string', default=fri_starttime_1,requires=IS_IN_SET(AMS)),
        Field('fri_endtime_1', 'string', default=fri_endtime_1,requires=IS_IN_SET(AMS)),
        Field('fri_starttime_2', 'string', default=fri_starttime_2,requires=IS_IN_SET(AMS)),
        Field('fri_endtime_2', 'string', default=fri_endtime_2,requires=IS_IN_SET(AMS)),
        Field('fri_visitinghours', 'string', default=fri_visitinghours),
        
        Field('sat_day_chk', 'boolean', default=sat_day_chk),        
        Field('sat_lunch_chk', 'boolean', default=sat_lunch_chk),        
        Field('sat_del_chk', 'boolean', default=sat_del_chk),        
        Field('sat_starttime_1', 'string', default=sat_starttime_1,requires=IS_IN_SET(AMS)),
        Field('sat_endtime_1', 'string', default=sat_endtime_1,requires=IS_IN_SET(AMS)),
        Field('sat_starttime_2', 'string', default=sat_starttime_2,requires=IS_IN_SET(AMS)),
        Field('sat_endtime_2', 'string', default=sat_endtime_2,requires=IS_IN_SET(AMS)),
        Field('sat_visitinghours', 'string', default=sat_visitinghours),

        Field('sun_day_chk', 'boolean', default=sun_day_chk),        
        Field('sun_lunch_chk', 'boolean', default=sun_lunch_chk),        
        Field('sun_del_chk', 'boolean', default=sun_del_chk),        
        Field('sun_starttime_1', 'string', default=sun_starttime_1,requires=IS_IN_SET(AMS)),
        Field('sun_endtime_1', 'string', default=sun_endtime_1,requires=IS_IN_SET(AMS)),
        Field('sun_starttime_2', 'string', default=sun_starttime_2,requires=IS_IN_SET(AMS)),
        Field('sun_endtime_2', 'string', default=sun_endtime_2,requires=IS_IN_SET(AMS)),
        Field('sun_visitinghours', 'string', default=sun_visitinghours),
    
        Field('visitinghours', 'string', default=visitinghours),
        Field('lunchbreak', 'string', default=lunchbreak)
        

        )
    
    if formA.accepts(request,session,keepvalues=True):
    
        visitinghours = ""
        lunchbreaks = ""
        
        #Monday
        if((formA.vars.mon_day_chk == True) & (formA.vars.mon_del_chk == False)):
            visitinghours = visitinghours + "Mon "
            if(formA.vars.mon_starttime_1 != ""):
                visitinghours = visitinghours + formA.vars.mon_starttime_1
                if(formA.vars.mon_endtime_1 != ""):
                    visitinghours = visitinghours + "-" + formA.vars.mon_endtime_1 + "; "
                else:
                    visitinghours = visitinghours  +"; "
            if(formA.vars.mon_starttime_2 != ""):
                visitinghours = visitinghours + formA.vars.mon_starttime_2
                if(formA.vars.mon_endtime_2 != ""):
                    visitinghours = visitinghours + "-" + formA.vars.mon_endtime_2 + "; "
                else:
                    visitinghours = visitinghours  +"; "
            if(formA.vars.mon_lunch_chk == True):
                lunchbreaks = lunchbreaks + "Mon; "
                
        
        #Tue
        if((formA.vars.tue_day_chk == True) & (formA.vars.tue_del_chk == False)):
            visitinghours = visitinghours + "Tue "
            if(formA.vars.tue_starttime_1 != ""):
                visitinghours = visitinghours + formA.vars.tue_starttime_1
                if(formA.vars.tue_endtime_1 != ""):
                    visitinghours = visitinghours + "-" + formA.vars.tue_endtime_1 + "; "
                else:
                    visitinghours = visitinghours  +"; "
            if(formA.vars.tue_starttime_2 != ""):
                visitinghours = visitinghours + formA.vars.tue_starttime_2
                if(formA.vars.tue_endtime_2 != ""):
                    visitinghours = visitinghours + "-" + formA.vars.mon_endtime_2 + "; "
                else:
                    visitinghours = visitinghours  +"; "

            if(formA.vars.tue_lunch_chk == True):
                lunchbreaks = lunchbreaks + "Tue; "

        #Wed
        if((formA.vars.wed_day_chk == True) & (formA.vars.wed_del_chk == False)):
            visitinghours = visitinghours + "Wed "
            if(formA.vars.wed_starttime_1 != ""):
                visitinghours = visitinghours + formA.vars.wed_starttime_1
                if(formA.vars.wed_endtime_1 != ""):
                    visitinghours = visitinghours + "-" + formA.vars.wed_endtime_1 + "; "
                else:
                    visitinghours = visitinghours  +"; "
                    
            if(formA.vars.wed_starttime_2 != ""):
                visitinghours = visitinghours + formA.vars.wed_starttime_2
                if(formA.vars.wed_endtime_2 != ""):
                    visitinghours = visitinghours + "-" + formA.vars.wed_endtime_2 + "; "
                else:
                    visitinghours = visitinghours  +"; "
            if(formA.vars.wed_lunch_chk == True):
                lunchbreaks = lunchbreaks + "Wed; "
                    

        #Thu
        if((formA.vars.thu_day_chk == True)& (formA.vars.thu_del_chk == False)):
            visitinghours = visitinghours + "Thu "
            if(formA.vars.thu_starttime_1 != ""):
                visitinghours = visitinghours + formA.vars.thu_starttime_1
                if(formA.vars.thu_endtime_1 != ""):
                    visitinghours = visitinghours + "-" + formA.vars.thu_endtime_1 + "; "
                else:
                    visitinghours = visitinghours  +"; "
                    
            if(formA.vars.thu_starttime_2 != ""):
                visitinghours = visitinghours + formA.vars.thu_starttime_2
                if(formA.vars.thu_endtime_2 != ""):
                    visitinghours = visitinghours + "-" + formA.vars.thu_endtime_2 + "; "
                else:
                    visitinghours = visitinghours  +"; "
    
            if(formA.vars.thu_lunch_chk == True):
                lunchbreaks = lunchbreaks + "Thu; "


        #Fri
        if((formA.vars.fri_day_chk == True) & (formA.vars.fri_del_chk == False)):
            visitinghours = visitinghours + "Fri "
            if(formA.vars.fri_starttime_1 != ""):
                visitinghours = visitinghours + formA.vars.fri_starttime_1
                if(formA.vars.fri_endtime_1 != ""):
                    visitinghours = visitinghours + "-" + formA.vars.fri_endtime_1 + "; "
                else:
                    visitinghours = visitinghours  +"; "

            if(formA.vars.fri_starttime_2 != ""):
                visitinghours = visitinghours + formA.vars.fri_starttime_2
                if(formA.vars.fri_endtime_2 != ""):
                    visitinghours = visitinghours + "-" + formA.vars.fri_endtime_2 + "; "
                else:
                    visitinghours = visitinghours  +"; "
    
            if(formA.vars.fri_lunch_chk == True):
                lunchbreaks = lunchbreaks + "Fri; "
    

        #Sat
        if((formA.vars.sat_day_chk == True) & (formA.vars.sat_del_chk == False)):
            visitinghours = visitinghours + "Sat "
            if(formA.vars.sat_starttime_1 != ""):
                visitinghours = visitinghours + formA.vars.sat_starttime_1
                if(formA.vars.sat_endtime_1 != ""):
                    visitinghours = visitinghours + "-" + formA.vars.sat_endtime_1 + "; "
                else:
                    visitinghours = visitinghours  +"; "
                    
            if(formA.vars.sat_starttime_2 != ""):
                visitinghours = visitinghours + formA.vars.sat_starttime_2
                if(formA.vars.sat_endtime_2 != ""):
                    visitinghours = visitinghours + "-" + formA.vars.sat_endtime_2 + "; "
                else:
                    visitinghours = visitinghours  +"; "

            if(formA.vars.sat_lunch_chk == True):
                lunchbreaks = lunchbreaks + "Sat; "
            

        #Sun
        if((formA.vars.sun_day_chk == True) & (formA.vars.sun_del_chk == False)):
            visitinghours = visitinghours + "Sun "
            if(formA.vars.sun_starttime_1 != ""):
                visitinghours = visitinghours + formA.vars.sun_starttime_1
                if(formA.vars.sun_endtime_1 != ""):
                    visitinghours = visitinghours + "-" + formA.vars.sun_endtime_1 + "; "
                else:
                    visitinghours = visitinghours  +"; "
            if(formA.vars.sun_starttime_2 != ""):
                visitinghours = visitinghours + formA.vars.sun_starttime_2
                if(formA.vars.sun_endtime_2 != ""):
                    visitinghours = visitinghours + "-" + formA.vars.sun_endtime_2 + "; "
                else:
                    visitinghours = visitinghours  +"; "

            if(formA.vars.sun_lunch_chk == True):
                lunchbreaks = lunchbreaks + "Sun; "
                
        #add/update 
        retval = db.doctortiming.update_or_insert(((db.doctortiming.doctor==doctorid) & (db.doctortiming.is_active==True)),\
                                          doctor = doctorid,\
                                          mon_day_chk = common.getboolean(formA.vars.mon_day_chk),\
                                          mon_lunch_chk = common.getboolean(formA.vars.mon_lunch_chk),\
                                          mon_del_chk = common.getboolean(formA.vars.mon_del_chk),\
                                          mon_starttime_1 = common.getstring(formA.vars.mon_starttime_1),\
                                          mon_endtime_1 = common.getstring(formA.vars.mon_endtime_1),\
                                          mon_starttime_2 = common.getstring(formA.vars.mon_starttime_2),\
                                          mon_endtime_2 = common.getstring(formA.vars.mon_endtime_2),\
                                          mon_visitinghours = "",\
                                          
                                          tue_day_chk = common.getboolean(formA.vars.tue_day_chk),\
                                          tue_lunch_chk = common.getboolean(formA.vars.tue_lunch_chk),\
                                          tue_del_chk = common.getboolean(formA.vars.tue_del_chk),\
                                          tue_starttime_1 = common.getstring(formA.vars.tue_starttime_1),\
                                          tue_endtime_1 = common.getstring(formA.vars.tue_endtime_1),\
                                          tue_starttime_2 = common.getstring(formA.vars.tue_starttime_2),\
                                          tue_endtime_2 = common.getstring(formA.vars.tue_endtime_2),\
                                          tue_visitinghours = "",\
  
                                          wed_day_chk = common.getboolean(formA.vars.wed_day_chk),\
                                          wed_lunch_chk = common.getboolean(formA.vars.wed_lunch_chk),\
                                          wed_del_chk = common.getboolean(formA.vars.wed_del_chk),\
                                          wed_starttime_1 = common.getstring(formA.vars.wed_starttime_1),\
                                          wed_endtime_1 = common.getstring(formA.vars.wed_endtime_1),\
                                          wed_starttime_2 = common.getstring(formA.vars.wed_starttime_2),\
                                          wed_endtime_2 = common.getstring(formA.vars.wed_endtime_2),\
                                          wed_visitinghours = "",\
                                                                                  
                                          thu_day_chk = common.getboolean(formA.vars.thu_day_chk),\
                                          thu_lunch_chk = common.getboolean(formA.vars.thu_lunch_chk),\
                                          thu_del_chk = common.getboolean(formA.vars.thu_del_chk),\
                                          thu_starttime_1 = common.getstring(formA.vars.thu_starttime_1),\
                                          thu_endtime_1 = common.getstring(formA.vars.thu_endtime_1),\
                                          thu_starttime_2 = common.getstring(formA.vars.thu_starttime_2),\
                                          thu_endtime_2 = common.getstring(formA.vars.thu_endtime_2),\
                                          thu_visitinghours = "",\
                                                                                  
                                          fri_day_chk = common.getboolean(formA.vars.fri_day_chk),\
                                          fri_lunch_chk = common.getboolean(formA.vars.fri_lunch_chk),\
                                          fri_del_chk = common.getboolean(formA.vars.fri_del_chk),\
                                          fri_starttime_1 = common.getstring(formA.vars.fri_starttime_1),\
                                          fri_endtime_1 = common.getstring(formA.vars.fri_endtime_1),\
                                          fri_starttime_2 = common.getstring(formA.vars.fri_starttime_2),\
                                          fri_endtime_2 = common.getstring(formA.vars.fri_endtime_2),\
                                          fri_visitinghours = "",\
                                                                                  
                                          sat_day_chk = common.getboolean(formA.vars.sat_day_chk),\
                                          sat_lunch_chk = common.getboolean(formA.vars.sat_lunch_chk),\
                                          sat_del_chk = common.getboolean(formA.vars.sat_del_chk),\
                                          sat_starttime_1 = common.getstring(formA.vars.sat_starttime_1),\
                                          sat_endtime_1 = common.getstring(formA.vars.sat_endtime_1),\
                                          sat_starttime_2 = common.getstring(formA.vars.sat_starttime_2),\
                                          sat_endtime_2 = common.getstring(formA.vars.sat_endtime_2),\
                                          sat_visitinghours = "",\
                                        
                                          sun_day_chk = common.getboolean(formA.vars.sun_day_chk),\
                                          sun_lunch_chk = common.getboolean(formA.vars.sun_lunch_chk),\
                                          sun_del_chk = common.getboolean(formA.vars.sun_del_chk),\
                                          sun_starttime_1 = common.getstring(formA.vars.sun_starttime_1),\
                                          sun_endtime_1 = common.getstring(formA.vars.sun_endtime_1),\
                                          sun_starttime_2 = common.getstring(formA.vars.sun_starttime_2),\
                                          sun_endtime_2 = common.getstring(formA.vars.sun_endtime_2),\
                                          sun_visitinghours = "",\

                                          visitinghours = visitinghours, lunchbreak = lunchbreaks,is_active = True,\
                                          created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid\
                                          
                                    )
	
	session.flash = 'Doctor timings added!'
        redirect(returnurl)                                  

    elif formA.errors:
        
        session.flash = 'Error in updating Doctor timings! ' + str(formA.errors)
   
        
    return dict(formA=formA, returnurl=returnurl, page=page, providerid=providerid, providername=providername,doctorname=doctorname)