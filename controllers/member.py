from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)
#
#import sys
#sys.path.append('modules')
from applications.my_pms2.modules import common
from applications.my_pms2.modules import status
from applications.my_pms2.modules import states
from applications.my_pms2.modules import gender

from applications.my_pms2.modules import logger

#from gluon.contrib import common
#from gluon.contrib import status
#from gluon.contrib import states
#from gluon.contrib import gender


@request.restful()
def getjsonmembers():
    response.view = 'generic.json'
    def GET(tablename, providerid):
        query = ((db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True) &  (db.patientmember.provider == 112))
        dsmembers = db(query).select(db.patientmember.id, db.patientmember.patientmember, db.patientmember.fname,db.patientmember.lname,db.patientmember.email,\
                                     db.patientmember.status,db.patientmember.address1, db.patientmember.enrollmentdate )
        return dict(dsmembers = dsmembers)    
    return locals()


def download():
    if(len(request.args)>0):
        filename = os.path.join(request.folder,'uploads/'+request.args[0])
        return response.stream(filename,1024,request)
    return response.download(request, db)

#def download():
    #return response.download(request, db)

def getdsmembers(db,providerid, member,fname,lname,cell,email,limitby,membertype):
    
    dsmembers = None
    
    if(providerid > 0):
        query = ((db.patientmember.provider == providerid) & (db.patientmember.is_active == True))
    else:
        query = ((db.patientmember.is_active == True))

    if(membertype == "members"):
        query = query & (db.patientmember.hmopatientmember == True)
    elif(membertype == "nonmembers"):
        query = query & (db.patientmember.hmopatientmember == False)
    else:
        query = query
        
    if(member != ""):
        query = query & (db.patientmember.patientmember.contains(member))
    if(fname != ""):
        query = query & (db.patientmember.fname.contains(fname))
    if(lname != ""):
        query = query & (db.patientmember.lname.contains(lname))
    if(cell != ""):
        query = query & (db.patientmember.cell.contains(cell))
    
    if(email != ""):
        query = query & (db.patientmember.email.contains(email))
    
    
        
    dsmembers = db(query).select(db.patientmember.id, db.patientmember.patientmember, db.patientmember.dob, db.patientmember.fname, db.patientmember.lname,\
                                 db.patientmember.address1,db.patientmember.address2,db.patientmember.address3,db.patientmember.city,db.patientmember.st,\
                                 db.patientmember.pin,db.patientmember.cell,db.patientmember.email,db.patientmember.enrollmentdate,db.patientmember.premstartdt, db.patientmember.premenddt, \
                                 db.vw_treatmentplancost.primarypatient, db.vw_treatmentplancost.totaltreatmentcost,db.vw_treatmentplancost.totalcopay,\
                                 db.vw_treatmentplancost.totalmemberpays,db.vw_treatmentplancost.totalinspays,db.hmoplan.hmoplancode,db.hmoplan.name,\
                                 left=[db.vw_treatmentplancost.on(db.vw_treatmentplancost.primarypatient == db.patientmember.id ),\
                                       db.hmoplan.on(db.hmoplan.id == db.patientmember.hmoplan)],limitby=limitby,orderby=~db.patientmember.id
                                 
                                 )
    
    return dsmembers


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def getmembergrid(page,providerid, providername, memberid, patientid,patientsearch, newmember=False):
    #logger.loggerpms2.info("Enter getmembergrin " + str(providerid) + " " + str(memberid) + " " + str(patientid) + " " + str(patientsearch))
    #display all those patients who have seeked appointments with this provider. Appointment guarantees that these patient/members have 
    #agreed to this provider.
    memberset = set()
  
    appts = db((db.t_appointment.is_active == True)&\
               (db.t_appointment.f_status != 'Cancelled')&\
               (db.t_appointment.provider == providerid)).select(db.t_appointment.patientmember, db.t_appointment.patient)
  
    for appt in appts:
        if(appt.patientmember in memberset):
            continue
        memberset.add(appt.patientmember)
        
    query = (db.vw_memberpatientlist.is_active == True)
    
    if(providerid > 0):
        q = (query) & ((db.vw_memberpatientlist.hmopatientmember == True) & (db.vw_memberpatientlist.providerid == providerid))
        pats = db(q).select(db.vw_memberpatientlist.primarypatientid)
        for pat in pats:
            if(pat.primarypatientid in memberset):
                continue
            memberset.add(pat.primarypatientid)

    #logger.loggerpms2.info("Membergrid-Memberset " + str(len(memberset)) +" " + str(memberset))
    #removing premenndt check
    if((patientid != 0) & (memberid != 0)):
        query = (query) & ((db.vw_memberpatientlist.hmopatientmember == True) & (db.vw_memberpatientlist.is_active == True) & \
                 (db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid))
                 #(datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )
            
    else:
        #all MDP Members who have had appointments with this Provider in the past,current & future
        query = (query) & ((db.vw_memberpatientlist.primarypatientid.belongs(memberset)) &  (db.vw_memberpatientlist.hmopatientmember == True))
                       #(datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt))

    
    #is it numeric only, then search on cell numbero
    if(patientsearch.replace("+",'').replace(' ','').isdigit()):
        query = (query) & (db.vw_memberpatientlist.cell.like("%" + patientsearch + "%"))
    #is it email only
    elif(patientsearch.find("@") >= 0):
        query = (query) & (db.vw_memberpatientlist.email.like("%" + patientsearch + "%"))
        
    #if pats is empty, then search for phrase in patient (fname lname:membercode)
    else:
        if(patientsearch != ""):
            query = ((query) & ((db.vw_memberpatientlist.patient.like("%" + patientsearch + "%")) | (db.vw_memberpatientlist.patientmember.like("%" + patientsearch + "%"))))        

    #logger.loggerpms2.info("Search Patient Query = " + str(query))
        
    fields=(db.vw_memberpatientlist.fullname,db.vw_memberpatientlist.patient,db.vw_memberpatientlist.patientmember, db.vw_memberpatientlist.cell, db.vw_memberpatientlist.email,\
            db.vw_memberpatientlist.premstartdt,db.vw_memberpatientlist.premenddt, db.vw_memberpatientlist.hmoplanname,\
            db.vw_memberpatientlist.primarypatientid,db.vw_memberpatientlist.patientid, db.vw_memberpatientlist.gender,db.vw_memberpatientlist.patienttype,db.vw_memberpatientlist.hmoplan\
            )    
    
    headers={
            'vw_memberpatientlist.patientmember':'Member ID',
            'vw_memberpatientlist.fullname':'Name',
            'vw_memberpatientlist.cell':'Mobile',
            'vw_memberpatientlist.gender':'Email',
            'vw_memberpatientlist.hmoplanname': 'Plan',
            'vw_memberpatientlist.premstartdt':'Prem. Start',
            'vw_memberpatientlist.premenddt':'Prem. End',
            }
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
    db.vw_memberpatientlist.id.readable = False
    db.vw_memberpatientlist.primarypatientid.readable = False 
    db.vw_memberpatientlist.patientid.readable = False 
    db.vw_memberpatientlist.patienttype.readable = False
    db.vw_memberpatientlist.gender.readable = False
    #db.vw_memberpatientlist.fullname.readable = False
    db.vw_memberpatientlist.patient.readable = False
    #db.vw_memberpatientlist.email.readable = False 
    db.vw_memberpatientlist.dob.readable = False 
    
    db.vw_memberpatientlist.regionid.readable = False
    
    db.vw_memberpatientlist.providerid.readable = False
    db.vw_memberpatientlist.is_active.readable = False
    db.vw_memberpatientlist.hmopatientmember.readable = False 
    
    db.vw_memberpatientlist.hmoplan.readable = False 
    db.vw_memberpatientlist.hmoplancode.readable = False 
    db.vw_memberpatientlist.company.readable = False 
    db.vw_memberpatientlist.newmember.readable = False 
    db.vw_memberpatientlist.freetreatment.readable = False 
    db.vw_memberpatientlist.age.readable = False 
    db.vw_memberpatientlist.totaltreatmentcost.readable = False 
    db.vw_memberpatientlist.totaldue.readable = False 
   
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
    links = [dict(header=CENTER('PlanPDF'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/reports.png",_width=30, _height=30),_href=URL('reports','viewplanpdf',vars=dict(planid=row.hmoplan)),_target="blank"))),
             dict(header=CENTER('Notes'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("casereport","casereport",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,source='members'))))),\
             dict(header=CENTER('Open'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("member","member_update",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, treatmentid=0, providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Treatment'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/treatments.png",_width=30, _height=30),_href=URL("treatment","list_treatments",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername,status='Open'))))),\
             dict(header=CENTER('Payment'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/payments.png",_width=30, _height=30),_href=URL("payment","list_payment",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, fullname=row.fullname, patient=row.patient,providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Image'),body=lambda row:CENTER(A(IMG(_src="/my_pms2/static/img/x-rays.png",_width=30, _height=30),_href=URL("dentalimage","list_dentalimages",vars=dict(memberpage=page,page=0,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Media'),body=lambda row:CENTER(A(IMG(_src="/my_pms2/static/img/x-rays.png",_width=30, _height=30),_href=URL("media","list_media",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername)))))
             ]

    
    orderby = (~db.vw_memberpatientlist.primarypatientid, ~db.vw_memberpatientlist.patienttype)
    
    maxtextlengths = {'vw_memberpatientlist.hmoplanname':50, 'vw_memberpatientlist.email':50,}
    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            orderby=orderby,
                            maxtextlengths=maxtextlengths,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            searchable=False,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            ui = 'jquery-ui',                           
                            user_signature=True
                           )
  
   
    
    return form
@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def xgetmembergrid(page,providerid, providername, memberid, patientid,patientmemberphrase, newmember=False):

    if(patientmemberphrase == ""):
        query = (db.vw_memberpatientlist.providerid == 0)
    else:
        #if((patientid != 0) & (memberid != 0)):
            ##if(newmember == True):
                ##query = ((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.hmopatientmember == True) & (db.vw_memberpatientlist.is_active == True) & \
                         ##(db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid) & \
                         ##(datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) & (db.vw_memberpatientlist.newmember == True))
            ##else:
            #query = ((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.hmopatientmember == True) & (db.vw_memberpatientlist.is_active == True) & \
                     #(db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid))
                     ##(datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )
                
        #else:
            ##if(newmember == True):
                ##query = ((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.hmopatientmember == True) & \
                         ##(db.vw_memberpatientlist.is_active == True) & \
                         ##((db.vw_memberpatientlist.patient == patientmemberphrase) | (db.vw_memberpatientlist.patient.like('%' + patientmemberphrase + '%'))) &\
                         ##(datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) &  (db.vw_memberpatientlist.newmember == True))
            ##else:
            #query = ((db.vw_memberpatientlist.providerid == providerid) & \
                     #(db.vw_memberpatientlist.hmopatientmember == True)&\
                     #((db.vw_memberpatientlist.patient == patientmemberphrase) | (db.vw_memberpatientlist.patient.like('%' + patientmemberphrase + '%'))) &\
                     #(db.vw_memberpatientlist.is_active == True))
                     ##(datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) & \
    
        
        if((patientid != 0) & (memberid != 0)):
            
            query = ((1==1) & (db.vw_memberpatientlist.hmopatientmember == True) & (db.vw_memberpatientlist.is_active == True) & \
                     (db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid))
                     #(datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) )
                
        else:
           
            query = ((1==1) & \
                     (db.vw_memberpatientlist.hmopatientmember == True)&\
                     ((db.vw_memberpatientlist.patient == patientmemberphrase) | (db.vw_memberpatientlist.patient.like('%' + patientmemberphrase + '%'))) &\
                     (db.vw_memberpatientlist.is_active == True))
                     #(datetime.date.today().strftime('%Y-%m-%d') <= db.vw_memberpatientlist.premenddt) & \
                
    
    #query = (((db.vw_memberpatientlist.patient == patientmemberphrase) | (db.vw_memberpatientlist.patient.like('%' + patientmemberphrase + '%'))) &\
               #(db.vw_memberpatientlist.hmopatientmember == True) & (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True))    
    
    #logger.loggerpms2.info("getmembergriid" + " " + str(query))
    
    #r = db(query).select()
    #logger.loggerpms2.info("getmembergrid size = " + str(len(r)))
    
    fields=(db.vw_memberpatientlist.fullname,db.vw_memberpatientlist.patient,db.vw_memberpatientlist.patientmember, db.vw_memberpatientlist.cell, db.vw_memberpatientlist.email,\
            db.vw_memberpatientlist.premstartdt,db.vw_memberpatientlist.premenddt, db.vw_memberpatientlist.hmoplanname,\
            db.vw_memberpatientlist.primarypatientid,db.vw_memberpatientlist.patientid, db.vw_memberpatientlist.gender,db.vw_memberpatientlist.patienttype,db.vw_memberpatientlist.hmoplan\
            )    
    
    headers={
            'vw_memberpatientlist.patientmember':'Member ID',
            'vw_memberpatientlist.fullname':'Name',
            'vw_memberpatientlist.cell':'Mobile',
            'vw_memberpatientlist.gender':'Email',
            'vw_memberpatientlist.hmoplanname': 'Plan',
            'vw_memberpatientlist.premstartdt':'Prem. Start',
            'vw_memberpatientlist.premenddt':'Prem. End',
            }
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
    db.vw_memberpatientlist.id.readable = False
    db.vw_memberpatientlist.primarypatientid.readable = False 
    db.vw_memberpatientlist.patientid.readable = False 
    db.vw_memberpatientlist.patienttype.readable = False
    db.vw_memberpatientlist.gender.readable = False
    #db.vw_memberpatientlist.fullname.readable = False
    db.vw_memberpatientlist.patient.readable = False
    #db.vw_memberpatientlist.email.readable = False 
    db.vw_memberpatientlist.dob.readable = False 
    
    db.vw_memberpatientlist.regionid.readable = False
    
    db.vw_memberpatientlist.providerid.readable = False
    db.vw_memberpatientlist.is_active.readable = False
    db.vw_memberpatientlist.hmopatientmember.readable = False 
    
    db.vw_memberpatientlist.hmoplan.readable = False 
    db.vw_memberpatientlist.hmoplancode.readable = False 
    db.vw_memberpatientlist.company.readable = False 
    db.vw_memberpatientlist.newmember.readable = False 
    db.vw_memberpatientlist.freetreatment.readable = False 
    db.vw_memberpatientlist.age.readable = False 
    db.vw_memberpatientlist.totaltreatmentcost.readable = False 
    db.vw_memberpatientlist.totaldue.readable = False 
   
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
    links = [dict(header=CENTER('PlanPDF'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/reports.png",_width=30, _height=30),_href=URL('reports','viewplanpdf',vars=dict(planid=row.hmoplan)),_target="blank"))),
             dict(header=CENTER('Notes'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("casereport","casereport",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,source='members'))))),\
             dict(header=CENTER('Open'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("member","member_update",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, treatmentid=0, providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Treatment'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/treatments.png",_width=30, _height=30),_href=URL("treatment","list_treatments",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername,status='Open'))))),\
             dict(header=CENTER('Payment'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/payments.png",_width=30, _height=30),_href=URL("payment","list_payment",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, fullname=row.fullname, patient=row.patient,providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Image'),body=lambda row:CENTER(A(IMG(_src="/my_pms2/static/img/x-rays.png",_width=30, _height=30),_href=URL("dentalimage","list_dentalimages",vars=dict(memberpage=page,page=0,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Media'),body=lambda row:CENTER(A(IMG(_src="/my_pms2/static/img/x-rays.png",_width=30, _height=30),_href=URL("media","list_media",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername)))))
             ]

    
    orderby = (~db.vw_memberpatientlist.primarypatientid, ~db.vw_memberpatientlist.patienttype)
    
    maxtextlengths = {'vw_memberpatientlist.hmoplanname':50, 'vw_memberpatientlist.email':50,}
    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            orderby=orderby,
                            maxtextlengths=maxtextlengths,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            searchable=False,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            ui = 'jquery-ui',                           
                            user_signature=True
                           )
  
   
    
    return form

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def getnonmembergrid(page,providerid, providername, memberid, patientid,patientsearch, newmember=False):
    
    if((patientid != 0) & (memberid != 0)):
        query = ((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.hmopatientmember == False) & (db.vw_memberpatientlist.is_active == True) & \
                 (db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid) )
            
    else:
        query = ((db.vw_memberpatientlist.hmopatientmember == False) & (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True))
    
    
    
    #is it numeric only, then search on cell numbero
    if(patientsearch.replace("+",'').replace(' ','').isdigit()):
        query = (query) & (db.vw_memberpatientlist.cell.like("%" + patientsearch + "%"))
    #is it email only
    elif(patientsearch.find("@") >= 0):
        query = (query) & (db.vw_memberpatientlist.email.like("%" + patientsearch + "%"))
        
    #if pats is empty, then search for phrase in patient (fname lname:membercode)
    else:
        if(patientsearch != ""):
            query = ((query) & ((db.vw_memberpatientlist.patient.like("%" + patientsearch + "%")) | (db.vw_memberpatientlist.patientmember.like("%" + patientsearch + "%"))))        

    logger.loggerpms2.info("Search Patient Query = " + str(query))    

    fields=(db.vw_memberpatientlist.fullname,db.vw_memberpatientlist.patientmember,db.vw_memberpatientlist.cell,db.vw_memberpatientlist.email,\
            db.vw_memberpatientlist.patient,db.vw_memberpatientlist.patienttype,db.vw_memberpatientlist.hmoplanname, \
            db.vw_memberpatientlist.patientid,db.vw_memberpatientlist.premstartdt,db.vw_memberpatientlist.premenddt, \
            db.vw_memberpatientlist.primarypatientid,db.vw_memberpatientlist.gender,db.vw_memberpatientlist.hmoplancode\
            )    
    
    headers={
            'vw_memberpatientlist.patientmember':'Member ID',
            'vw_memberpatientlist.fullname':'Name',
            'vw_memberpatientlist.cell':'Mobile',
            'vw_memberpatientlist.gender':'Email'
            }
 
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
    maxtextlengths = {'vw_memberpatientlist.email':50,'vw_memberpatientlist.fullname':50}
    
    db.vw_memberpatientlist.id.readable = False
    db.vw_memberpatientlist.primarypatientid.readable = False 
    db.vw_memberpatientlist.patientid.readable = False 
    db.vw_memberpatientlist.patienttype.readable = False
    db.vw_memberpatientlist.gender.readable = False
  
    db.vw_memberpatientlist.patient.readable = False
   
    db.vw_memberpatientlist.dob.readable = False 
    
    db.vw_memberpatientlist.regionid.readable = False
    
    db.vw_memberpatientlist.providerid.readable = False
    db.vw_memberpatientlist.is_active.readable = False
    db.vw_memberpatientlist.hmopatientmember.readable = False 
    
    db.vw_memberpatientlist.hmoplan.readable = False 
    db.vw_memberpatientlist.hmoplancode.readable = False 
    db.vw_memberpatientlist.hmoplanname.readable = False 
    db.vw_memberpatientlist.premstartdt.readable = False 
    db.vw_memberpatientlist.premenddt.readable = False 
    
    db.vw_memberpatientlist.company.readable = False 
    db.vw_memberpatientlist.newmember.readable = False 
    db.vw_memberpatientlist.freetreatment.readable = False 
    db.vw_memberpatientlist.age.readable = False 
    db.vw_memberpatientlist.totaltreatmentcost.readable = False 
    db.vw_memberpatientlist.totaldue.readable = False 
   
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
    links = [
             #dict(header=CENTER(''), body=lambda row: \
                  
                        #(CENTER(A(IMG(_src="/my_pms2/static/img/religare_on.png",_width=25, _height=25),_href=URL("casereport","casereport",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, treatmentid=0, providerid=providerid,source='walkin'))))\
                        #if(row.hmoplancode.startswith('RELGR')) else "")
                  #),\
        
             dict(header=CENTER('Notes'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("casereport","casereport",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, treatmentid=0, providerid=providerid,source='walkin'))))),\
             dict(header=CENTER('Open'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("member","update_nonmember",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Treatment'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/treatments.png",_width=30, _height=30),_href=URL("treatment","list_treatments",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername,status='Open'))))),\
             dict(header=CENTER('Payment'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/payments.png",_width=30, _height=30),_href=URL("payment","list_payment",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, fullname=row.fullname, patient=row.patient,providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Image'),body=lambda row:CENTER(A(IMG(_src="/my_pms2/static/img/x-rays.png",_width=30, _height=30),_href=URL("dentalimage","list_dentalimages",vars=dict(memberpage=page,page=0,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Reports'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/reports.png",_width=30, _height=30),_href=URL("reports","membertreatmentplansreport",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Delete'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=25, _height=25),_href=URL("member","delete_nonmember",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername)))))
             ]

    
    orderby = (~db.vw_memberpatientlist.primarypatientid, ~db.vw_memberpatientlist.patienttype)
        
    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            orderby=orderby,
                            maxtextlengths=maxtextlengths,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            searchable=False,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            ui = 'jquery-ui',                           
                            user_signature=True
                           )
  
   
    
    return form


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def getallmembergrid(page,providerid, providername, memberid, patientid,patientmemberphrase, newmember=False):
    
    if((patientid != 0) & (memberid != 0)):
        query = ((db.vw_memberpatientlist.providerid == providerid) &  (db.vw_memberpatientlist.is_active == True) & \
                 (db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid) )
            
    else:
        #query = ((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.hmopatientmember == False) & \
                 #(db.vw_memberpatientlist.fullname.like('%' + patientmemberphrase + '%'))  & (db.vw_memberpatientlist.is_active == True))
        query = (((db.vw_memberpatientlist.patient == patientmemberphrase) | (db.vw_memberpatientlist.patient.like('%' + patientmemberphrase + '%'))) &\
                 (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True))
    
    
    fields=(db.vw_memberpatientlist.fullname,db.vw_memberpatientlist.patientmember,db.vw_memberpatientlist.cell,db.vw_memberpatientlist.email,\
            db.vw_memberpatientlist.patient,db.vw_memberpatientlist.patienttype,db.vw_memberpatientlist.hmoplanname, \
            db.vw_memberpatientlist.patientid,db.vw_memberpatientlist.premstartdt,db.vw_memberpatientlist.premenddt, \
            db.vw_memberpatientlist.primarypatientid,db.vw_memberpatientlist.gender,db.vw_memberpatientlist.hmoplancode\
            )    
    
    headers={
            'vw_memberpatientlist.patientmember':'Member ID',
            'vw_memberpatientlist.fullname':'Name',
            'vw_memberpatientlist.cell':'Mobile',
            'vw_memberpatientlist.gender':'Email'
            }
 
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
    maxtextlengths = {'vw_memberpatientlist.email':50,'vw_memberpatientlist.fullname':50}
    
    db.vw_memberpatientlist.id.readable = False
    db.vw_memberpatientlist.primarypatientid.readable = False 
    db.vw_memberpatientlist.patientid.readable = False 
    db.vw_memberpatientlist.patienttype.readable = False
    db.vw_memberpatientlist.gender.readable = False
  
    db.vw_memberpatientlist.patient.readable = False
   
    db.vw_memberpatientlist.dob.readable = False 
    
    db.vw_memberpatientlist.regionid.readable = False
    
    db.vw_memberpatientlist.providerid.readable = False
    db.vw_memberpatientlist.is_active.readable = False
    db.vw_memberpatientlist.hmopatientmember.readable = False 
    
    db.vw_memberpatientlist.hmoplan.readable = False 
    db.vw_memberpatientlist.hmoplancode.readable = False 
    db.vw_memberpatientlist.hmoplanname.readable = False 
    db.vw_memberpatientlist.premstartdt.readable = False 
    db.vw_memberpatientlist.premenddt.readable = False 
    
    db.vw_memberpatientlist.company.readable = False 
    db.vw_memberpatientlist.newmember.readable = False 
    db.vw_memberpatientlist.freetreatment.readable = False 
    db.vw_memberpatientlist.age.readable = False 
    db.vw_memberpatientlist.totaltreatmentcost.readable = False 
    db.vw_memberpatientlist.totaldue.readable = False 
   
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
    links = [
             #dict(header=CENTER(''), body=lambda row: \
                  
                        #(CENTER(A(IMG(_src="/my_pms2/static/img/religare_on.png",_width=25, _height=25),_href=URL("casereport","casereport",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, treatmentid=0, providerid=providerid,source='walkin'))))\
                        #if(row.hmoplancode.startswith('RELGR')) else "")
                  #),\
        
             dict(header=CENTER('Notes'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("casereport","casereport",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, treatmentid=0, providerid=providerid,source='walkin'))))),\
             dict(header=CENTER('Open'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("member","update_nonmember",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Treatment'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/treatments.png",_width=30, _height=30),_href=URL("treatment","list_treatments",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername,status='Open'))))),\
             dict(header=CENTER('Payment'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/payments.png",_width=30, _height=30),_href=URL("payment","list_payment",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, fullname=row.fullname, patient=row.patient,providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Image'),body=lambda row:CENTER(A(IMG(_src="/my_pms2/static/img/x-rays.png",_width=30, _height=30),_href=URL("dentalimage","list_dentalimages",vars=dict(memberpage=page,page=0,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername))))),\
             dict(header=CENTER('Reports'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/reports.png",_width=30, _height=30),_href=URL("reports","membertreatmentplansreport",vars=dict(page=page,memberid=row.primarypatientid,patientid=row.patientid, providerid=providerid,providername=providername)))))
             ]

    
    orderby = (~db.vw_memberpatientlist.primarypatientid, ~db.vw_memberpatientlist.patienttype)
        
    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            orderby=orderby,
                            maxtextlengths=maxtextlengths,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            searchable=False,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            ui = 'jquery-ui',                           
                            user_signature=True
                           )
  
   
    
    return form


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_patients():
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])
    
    page     = common.getgridpage(request.vars)
    
    patientmember1 = common.getstring(request.vars.patientmember1)
    xpatientmember1 = common.getstring(request.vars.xpatientmember1)
    
    member = common.getstring(request.vars.member)
    newmember = common.getboolean(request.vars.newmember)    
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    newmember = common.getboolean(request.vars.newmember)    
    
    fullname = ""
    memberref = ""
    patient = ""
    
    returnurl = URL('admin', 'providerhome')    

    #r = db((db.vw_memberpatientlist_fast.providerid==providerid)&(db.vw_memberpatientlist_fast.patientid==patientid)&(db.vw_memberpatientlist_fast.primarypatientid==memberid)&(db.vw_memberpatientlist_fast.is_active==True)).select()
    r = db((db.patientmember.provider==providerid)&\
           (db.patientmember.id==patientid)&\
           (db.patientmember.hmopatientmember==True)&\
           (db.patientmember.is_active==True)).select()
    if(len(r)>0):
        memberref = common.getstring(r[0].patientmember)  #patientmember
        fullname = common.getstring(r[0].fullname)      #fname + lname
        patient = common.getstring(r[0].patient)    #fname + lname + patientmemebr
    
    form = SQLFORM.factory(
                 Field('patientmember1', 'string',  default=fullname, label='Patient'),
                 Field('xpatientmember1', 'string', default=patient, label='XPatient')
                 
      )
         
    xpatientmember = form.element('#no_table_patientmember1')
    xpatientmember['_class'] = 'form-control'
    xpatientmember['_placeholder'] = 'Enter Member ID, First Name, Last Name, Cell, Email'
    xpatientmember['_autocomplete'] = 'off'     
    
    formA = None
    
    formA = getmembergrid(page,providerid, providername, memberid, patientid,patientmember1,newmember)
    
    if form.accepts(request,session,keepvalues=True):
        logger.loggerpms2.info("Enter list_patient on submit " + form.vars.patientmember1 + " " + form.vars.xpatientmember1)
        if(form.vars.patientmember1 == ""):
            form.vars.xpatientmember1 = ""
            
        #r = db((db.vw_memberpatientlist.patient == form.vars.xpatientmember1.strip()) & (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).select()
        #if(len(r) > 0):
            #memberid = int(common.getid(r[0].primarypatientid))
            #patientid = int(common.getid(r[0].patientid))
            #memberref = common.getstring(r[0].patientmember)  #patientmember
            #fullname = common.getstring(r[0].fullname)      #fname + lname
            #patient = common.getstring(r[0].patient)    #fname + lname + patientmemebr        
         
        formA = getmembergrid(page,providerid, providername, memberid, patientid,xpatientmember1.strip(),newmember)
        
    return dict(form=form, formA=formA, page=page,\
                   returnurl=returnurl,providername=providername, \
                   providerid=providerid,memberid=memberid,patientid=patientid,patient=patient, \
                   fullname=fullname               
                   )    

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_allpatients():
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])
    
    page     = common.getgridpage(request.vars)
    
    patientmember1 = common.getstring(request.vars.phrase)
    xpatientmember1 = common.getstring(request.vars.phrase)
    
    member = common.getstring(request.vars.member)
    newmember = common.getboolean(request.vars.newmember)    
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    newmember = common.getboolean(request.vars.newmember)    
    
    fullname = ""
    memberref = ""
    patient = ""
    
    returnurl = URL('admin', 'providerhome')    

    r = db((db.vw_memberpatientlist.providerid==providerid)&(db.vw_memberpatientlist.patientid==patientid)&(db.vw_memberpatientlist.primarypatientid==memberid)&(db.vw_memberpatientlist.is_active==True)).select()
    if(len(r)>0):
        memberref = common.getstring(r[0].patientmember)  #patientmember
        fullname = common.getstring(r[0].fullname)      #fname + lname
        patient = common.getstring(r[0].patient)    #fname + lname + patientmemebr
    
    form = SQLFORM.factory(
                 Field('patientmember1', 'string',  default=fullname, label='Patient'),
                 Field('xpatientmember1', 'string', default=patient, label='XPatient')
                 
      )
         
    xpatientmember = form.element('#no_table_patientmember1')
    xpatientmember['_class'] = 'form-control'
    xpatientmember['_placeholder'] = 'Enter Member ID, First Name, Last Name, Cell, Email'
    xpatientmember['_autocomplete'] = 'off'     
    
    formA = None
    formA = getallmembergrid(page,providerid, providername, memberid, patientid,patientmember1,newmember)
    
    if form.accepts(request,session,keepvalues=True):
        if(form.vars.patientmember1 == ""):
            form.vars.xpatientmember1 = ""
            
        formA = getallmembergrid(page,providerid, providername, memberid, patientid,xpatientmember1.strip(),newmember)
        
    return dict(form=form, formA=formA, page=page,\
                   returnurl=returnurl,providername=providername, \
                   providerid=providerid,memberid=memberid,patientid=patientid,patient=patient, \
                   fullname=fullname               
                   )    
    
@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def xlist_nonmembers():
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])
    
    page     = common.getgridpage(request.vars)
    
    member = common.getstring(request.vars.member)
    newmember = common.getboolean(request.vars.newmember)    
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    newmember = common.getboolean(request.vars.newmember)    
    
    fullname = ""
    memberref = ""
    patient = ""
    
    returnurl = URL('admin', 'providerhome')    

    r = db((db.vw_memberpatientlist.providerid==providerid)&(db.vw_memberpatientlist.patientid==patientid)&(db.vw_memberpatientlist.primarypatientid==memberid)&(db.vw_memberpatientlist.is_active==True)).select()
    if(len(r)>0):
        memberref = common.getstring(r[0].patientmember)  #patientmember
        fullname = common.getstring(r[0].fullname)      #fname + lname
        patient = common.getstring(r[0].patient)    #fname + lname + patientmemebr
    
    form = SQLFORM.factory(
                 Field('patientmember1', 'string',  default=fullname, label='Patient'),
                 Field('xpatientmember1', 'string', default=patient, label='XPatient')
                 
      )
         
    xpatientmember = form.element('#no_table_patientmember1')
    xpatientmember['_class'] = 'form-control'
    xpatientmember['_placeholder'] = 'Enter Patient Name - First Name Last Name'
    xpatientmember['_autocomplete'] = 'off'     
    
    formA = None
    formA = getmembergrid(page,providerid, providername, memberid, patientid,newmember)
    
    if form.accepts(request,session,keepvalues=True):
        if(form.vars.patientmember1 == ""):
            form.vars.xpatientmember1 = ""
            
        r = db((db.vw_memberpatientlist.patient == form.vars.xpatientmember1.strip()) & (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).select()
        if(len(r) > 0):
            memberid = int(common.getid(r[0].primarypatientid))
            patientid = int(common.getid(r[0].patientid))
            memberref = common.getstring(r[0].patientmember)  #patientmember
            fullname = common.getstring(r[0].fullname)      #fname + lname
            patient = common.getstring(r[0].patient)    #fname + lname + patientmemebr        
         
        formA = getmembergrid(page,providerid, providername, memberid, patientid,newmember)
        
    return dict(form=form, formA=formA, page=page,\
                   returnurl=returnurl,providername=providername, \
                   providerid=providerid,memberid=memberid,patientid=patientid,patient=patient, \
                   fullname=fullname               
                   )    
    

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_members():
    session.nonmemberscount=False
    provdict = common.getprovider(auth, db)
    providerid = provdict["providerid"]
    providername = provdict["providername"]
    page     = common.getgridpage(request.vars)
    member = common.getstring(request.vars.member)
    newmember = common.getboolean(request.vars.newmember)

    redirect(URL('member','list_patients',vars=dict(page=page,providerid=providerid,member=member,newmember=newmember)))  
    returnurl = URL('admin', 'providerhome')    
    
    if(member != ""):
        if(newmember == True):
            query = ((db.vw_memberlist.providerid == providerid) & (db.vw_memberlist.hmopatientmember == True) & (db.vw_memberlist.is_active == True) & \
                     (db.vw_memberlist.patientmember == member) & (db.vw_memberlist.newmember == True))
        else:
            query = ((db.vw_memberlist.providerid == providerid) & (db.vw_memberlist.hmopatientmember == True) & (db.vw_memberlist.is_active == True) & \
                     (db.vw_memberlist.patientmember == member))
            
    else:
        if(newmember == True):
            query = ((db.vw_memberlist.providerid == providerid) & (db.vw_memberlist.hmopatientmember == True) & (db.vw_memberlist.is_active == True) & \
                     (db.vw_memberlist.newmember == True))
        else:
            query = ((db.vw_memberlist.providerid == providerid) & (db.vw_memberlist.hmopatientmember == True) & (db.vw_memberlist.is_active == True))
            
    
    fields=(db.vw_memberlist.fname,db.vw_memberlist.lname,db.vw_memberlist.patientmember,db.vw_memberlist.cell,db.vw_memberlist.email,db.vw_memberlist.hmoplanname, db.vw_memberlist.hmoplancode,
            db.vw_memberlist.totaltreatmentcost,db.vw_memberlist.totaldue)    
    
    headers={
            'vw_memberlist.patientmember':'Member ID',
            'vw_memberlist.fname':'First Name',
            'vw_memberlist.lname':'Last Name',
            'vw_memberlist.cell':'Cell',
            'vw_memberlist.hmoplanname': 'Plan',
            'vw_memberlist.totaltreatmentcost':'Total Cost',
            'vw_memberlist.totaldue':'Total Due',
            }
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
    db.vw_memberlist.id.readable = False
    db.vw_memberlist.providerid.readable = False
    db.vw_memberlist.is_active.readable = False
    db.vw_memberlist.hmopatientmember.readable = False 
    db.vw_memberlist.email.readable = False 
    db.vw_memberlist.hmoplancode.readable = False 
        
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
   
   
    links = [dict(header='Edit', body=lambda row: A(IMG(_src="/my_pms2/static/img/png/017-loupe.png",_width=25, _height=25),_href=URL("member","member_update",vars=dict(page=page,memberid=row.id,providerid=providerid,providername=providername)))),\
             dict(header='Treatment',body=lambda row: A(IMG(_src="/my_pms2/static/img/png/014-dentist.png",_width=30, _height=30),_href=URL("treatment","list_treatments",vars=dict(page=page,memberid=row.id,providerid=providerid,providername=providername,status='Open')))),\
             dict(header='Image',body=lambda row: A(IMG(_src="/my_pms2/static/img/png/021-xray.png",_width=30, _height=30),_href=URL("dentalimage","list_memberpatientimages",vars=dict(memberpage=page,page=1,memberid=row.id,providerid=providerid,providername=providername)))),\
             dict(header='Appointment',body=lambda row: A(IMG(_src="/my_pms2/static/img/png/011-calendar.png",_width=30, _height=30),_href=URL("appointment","list_memberpatientappointments",vars=dict(memberpage=page,page=1,memberid=row.id,providerid=providerid,providername=providername)))),\
             dict(header='Payment',body=lambda row: A(IMG(_src="/my_pms2/static/img/png/010-cash.png",_width=30, _height=30),_href=URL("payment","list_payment",vars=dict(page=page,memberid=row.id,providerid=providerid,providername=providername)))),\
             dict(header='Reports',body=lambda row: A(IMG(_src="/my_pms2/static/img/png/012-note-on-a-clipboard.png",_width=30, _height=30),_href=URL("reports","membertreatmentplansreport",vars=dict(page=page,memberid=row.id,providerid=providerid,providername=providername)))),\
             dict(header='Plan',body=lambda row: A(IMG(_src="/my_pms2/static/img/png/012-note-on-a-clipboard.png",_width=30, _height=30),_href=URL("http://www.google.com",_target="blank")))
             ]

    
    orderby = ~(db.vw_memberlist.id)

    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
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
  
    return dict(form = form, returnurl=returnurl,page=page,providerid=providerid,providername=providername)




@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_nonmembers():

    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])
    
    page     = common.getgridpage(request.vars)
    
    patientmember1 = common.getstring(request.vars.patientmember1)
    xpatientmember1 = common.getstring(request.vars.xpatientmember1)
    
    
    member = common.getstring(request.vars.member)
    newmember = common.getboolean(request.vars.newmember)    
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    returnurl = common.getstring(request.vars.returnurl) if(common.getstring(request.vars.url) != "") else URL('member','list_nonmembers', vars=dict(providerid=request.vars.providerid,page=page,member=member))

    fullname = ""
    memberref = ""
    patient = ""
    
       

    r = db((db.vw_memberpatientlist.providerid==providerid)&(db.vw_memberpatientlist.patientid==patientid)&(db.vw_memberpatientlist.primarypatientid==memberid)&(db.vw_memberpatientlist.is_active==True)).select()
    if(len(r)>0):
        memberref = common.getstring(r[0].patientmember)  #patientmember
        fullname = common.getstring(r[0].fullname)      #fname + lname
        patient = common.getstring(r[0].patient)    #fname + lname + patientmemebr
    
    form = SQLFORM.factory(
                 Field('patientmember1', 'string',  default=patientmember1, label='Patient'),
                 Field('xpatientmember1', 'string', default=xpatientmember1, label='XPatient')
                 
      )
         
    xpatientmember = form.element('#no_table_patientmember1')
    xpatientmember['_class'] = 'form-control'
    xpatientmember['_placeholder'] = 'Search on Member ID, First Name, Last Name, Cell, Email'
    xpatientmember['_autocomplete'] = 'off'     
    
    formA = None
    formA = getnonmembergrid(page,providerid, providername, memberid, patientid,patientmember1,newmember)
    
    if form.accepts(request,session,keepvalues=True):
        if(form.vars.patientmember1 == ""):
            form.vars.xpatientmember1 = ""
            
        #r = db(((db.vw_memberpatientlist.patient == form.vars.xpatientmember1.strip()) | (db.vw_memberpatientlist.patient.like('%' + form.vars.xpatientmember1.strip() + '%'))) &\
               #(db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).select()
        
        
        #if(len(r) > 0):
            #memberid = int(common.getid(r[0].primarypatientid))
            #patientid = int(common.getid(r[0].patientid))
            #memberref = common.getstring(r[0].patientmember)  #patientmember
            #fullname = common.getstring(r[0].fullname)      #fname + lname
            #patient = common.getstring(r[0].patient)    #fname + lname + patientmemebr        
         
        formA = getnonmembergrid(page,providerid, providername, memberid, patientid,form.vars.xpatientmember1.strip(),newmember)
        
    return dict(form=form, formA=formA, page=page,\
                   returnurl=returnurl,providername=providername, \
                   providerid=providerid,memberid=memberid,patientid=patientid,patient=patient, \
                   fullname=fullname               
                   )    
    




@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def delete_nonmember():
    
    page = int(common.getpage(request.vars.page))
    providerid = int(common.getid(request.vars.providerid))
    providername = common.getstring(request.vars.providername)
    memberid = int(common.getid(request.vars.memberid))
    
    returnurl = URL('member', 'list_nonmembers', vars=dict(page=page,providerid=providerid))  
    
    r = db((db.vw_memberpatientlist.patientid == memberid) & (db.vw_memberpatientlist.providerid == providerid)).select(db.vw_memberpatientlist.patient)
    
    form = FORM.confirm('Yes',{'No': returnurl})
    
    if form.accepted:
        db(db.patientmember.id == memberid).update(is_active = False)
        common.dashboard(db,session,providerid)
        redirect(returnurl)
      
    return dict(form=form, page=page, returnurl=returnurl, providerid=providerid, providername=providername,   patientname = r[0].patient)


#@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
#@auth.requires_login()
#def xlist_members():
    
    #session.nonmemberscount=False
    ##get provider information
    #provdict = common.getproviderfromid(db, request.vars.providerid)
    
    #page     = common.getgridpage(request.vars)    
    #member   = common.getstring(request.vars.member)
    #fname    = common.getstring(request.vars.fname)
    #lname    = common.getstring(request.vars.lname)
    #cell     = common.getstring(request.vars.cell)
    #email    = common.getstring(request.vars.email)
    
    ##display treatment plan filtering criteria
    #items_per_page = 5
    #limitby = (page*items_per_page,(page+1)*items_per_page+1) 
    
    ##display list of treatment plans
    #form = SQLFORM.factory(
            #Field('member','string',label='Member', default=member),
            #Field('fname', 'string',label='First Name', default=fname),
            #Field('lname', 'string',label='Last Name', default=lname),
            #Field('cell', 'string', label='Cell Phone',  default=cell ),
            #Field('email', 'string', label='Email',  default=email )
            #)
    
    #submit = form.element('input',_type='submit')
    #submit['_value'] = 'Search'   
    
    #xmember = form.element('input',_id='no_table_member')
    #xmember['_class'] =  'w3-input w3-border '
    
    
    #xfname = form.element('input',_id='no_table_fname')
    #xfname['_class'] =  'w3-input w3-border  '
    
    #xlname = form.element('input',_id='no_table_lname')
    #xlname['_class'] =  'w3-input w3-border  '
    
    #xcell = form.element('input',_id='no_table_cell')
    #xcell['_class'] =  'w3-input w3-border  '

    #xemail = form.element('input',_id='no_table_email')
    #xemail['_class'] =  'w3-input w3-border  '

    #dsmembers = getdsmembers(db,request.vars.providerid,member,fname,lname,cell,email,limitby,"members")
    
    #if(len(dsmembers) > 0):
        #rangemssg = "Displaying records from  " + str(int(common.getvalue(limitby[0]))+1) + "  to  " + str(int(common.getvalue(limitby[1]))-1)
    #else:
        #rangemssg = "No records to display"
    
    
    #if form.accepts(request,session,keepvalues=True):
        
        
        #member     = common.getstring(form.vars.member)
        #fname      = common.getstring(form.vars.fname)
        #lname      = common.getstring(form.vars.lname)
        #cell       = common.getstring(form.vars.cell)
        #email      = common.getstring(form.vars.email)
    
        #dsmembers = getdsmembers(db,request.vars.providerid,member, fname,lname,cell,email,limitby,"members")
        #if(len(dsmembers) > 0):
            #rangemssg = "Displaying records from  " + str(int(common.getvalue(limitby[0]))+1) + "  to  " + str(int(common.getvalue(limitby[1]))-1)
        #else:
            #rangemssg = "No records to display"
        
        #returnurl =  URL('admin','providerhome')
        
    #elif form.errors:
        #response.flash = 'form has errors'         
    
    #returnurl =  URL('admin','providerhome')
    
    #return dict(dsmembers=dsmembers, limitby=limitby, providername=provdict["providername"],form=form,providerid=provdict["providerid"],\
                #member=member,fname=fname,lname=lname,cell=cell,email=email,page=page,items_per_page=items_per_page,\
                #returnurl=returnurl,rangemssg = rangemssg)
    

   
@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def member_update():
    
    if(len(request.vars)<=0):
        raise HTTP(403,"Error: No Member Profile to Update : member_update()")

    #get provider information
    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getproviderfromid(db, providerid)
   
    #these are the list members filter parameters
    page     = common.getgridpage(request.vars)    
    member   = common.getstring(request.vars['member'])
    fname    = common.getstring(request.vars['fname'])
    lname    = common.getstring(request.vars['lname'])
    cell     = common.getstring(request.vars['cell'])
    email    = common.getstring(request.vars['email'])

    returnurl = URL('member','list_members', vars=dict(providerid=request.vars.providerid,page=page,member=member,fname=fname,lname=lname,cell=cell,email=email,))    
    
    memberid = int(common.getid(request.vars['memberid']))
    if(memberid == 0):
        raise HTTP(403,"Error: No Member Profile to Update : member_update()_1")
    
    query = ((db.patientmember.id == memberid) & (db.patientmember.is_active == True))
    
    members = db(query).select(db.patientmember.ALL,db.company.name, db.hmoplan.name, db.groupregion.groupregion,
                               left = [db.company.on (db.company.id == db.patientmember.company), db.hmoplan.on(db.hmoplan.id == db.patientmember.hmoplan),\
                                       db.groupregion.on(db.groupregion.id == db.patientmember.groupregion)]
                               )
                               

    if(len(members) != 1):
        raise HTTP(403,"Error: No Member Profile to Update : member_update()_2")
    
   
    formA = SQLFORM.factory(
                    Field('patientmember','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=members[0].patientmember.patientmember,requires=IS_NOT_EMPTY(), label="Member/Patient ID",writable=False, readable=True),
                    Field('groupref','string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=members[0].patientmember.groupref, label='Employee ID',writable=False, readable=True),
                    Field('dob','date', label='DOB',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border  date'), default=members[0].patientmember.dob,writable=False, readable=True),
                    Field('title','string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=members[0].patientmember.title,label='Title',requires=IS_IN_SET(gender.PATTITLE),writable=False, readable=True),
                    Field('fname', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=members[0].patientmember.fname, label='First',requires=IS_NOT_EMPTY(),writable=False, readable=True),
                    Field('mname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '),  default=members[0].patientmember.mname, label='Middle',writable=False, readable=True),
                    Field('lname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '),  default=members[0].patientmember.lname, label='Last',requires=IS_NOT_EMPTY(),writable=False, readable=True),
                    Field('gender','string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=members[0].patientmember.gender,label='Gender',requires=IS_IN_SET(gender.GENDER),writable=False, readable=True),
                    Field('address1', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=members[0].patientmember.address1,label='Address 1', requires=IS_NOT_EMPTY(),writable=False, readable=True),
                    Field('address2', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '),  default=members[0].patientmember.address2,label='Address 2',requires=IS_NOT_EMPTY(),writable=False, readable=True),
                    Field('address3', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '),  default=members[0].patientmember.address3,label='Address 3',writable=False, readable=True),
                    Field('city', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=members[0].patientmember.city,label='City',requires = IS_IN_SET(states.CITIES),writable=False, readable=True),
                    Field('st', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=members[0].patientmember.st,label='State',requires = IS_IN_SET(states.STATES),writable=False, readable=True),
                    Field('pin', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=members[0].patientmember.pin,label='Pin',requires=IS_NOT_EMPTY(),writable=False, readable=True),
                    Field('telephone', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=members[0].patientmember.telephone,label='Telephone',writable=False, readable=True),
                    Field('cell', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=members[0].patientmember.cell,label='Cell',writable=False, readable=True),
                    Field('email', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=members[0].patientmember.email,label='Email',writable=False, readable=True), 
                    Field('enrollmentdate','date',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border  date'),  label='Enrollment Date',default=members[0].patientmember.enrollmentdate,writable=False, readable=True),
                    Field('terminationdate','date', label='Termination Date',default=members[0].patientmember.terminationdate,writable=False, readable=True),
                    Field('duedate','date', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border  date'), label='Due Date',default=members[0].patientmember.duedate,writable=False, readable=True),
                    Field('premstartdt','date', label='Prem. Start Date',default=members[0].patientmember.premstartdt,writable=False, readable=True),
                    Field('premenddt','date', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border  date'), label='Prem. End Date',default=members[0].patientmember.premenddt,writable=False, readable=True),
                    Field('status', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '),  label='Status',default=members[0].patientmember.status,requires = IS_IN_SET(status.STATUS),writable=False, readable=True),
                    Field('provider',widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border '),  default=members[0].patientmember.provider, requires=IS_IN_DB(db, 'provider.id', '%(providername)s'),writable=False, readable=True),
                    Field('company', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border '), default=members[0].company.name,writable=False, readable=True ),
                    Field('hmoplan', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border '), default=members[0].hmoplan.name, writable=False, readable=True),
                    Field('groupregion', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_style="width:100%;height:35px;",_class='w3-input w3-border '), default=members[0].groupregion.groupregion, requires=IS_IN_DB(db, 'groupregion.id', '%(groupregion)s'),writable=False),
                    Field('newmember','boolean',label='Member',default=common.getboolean(members[0].patientmember.newmember),writable=False),
                    Field('freetreatment','boolean',label='Member',default=common.getboolean(members[0].patientmember.freetreatment),writable=False)
                   )
    
    
    ## Display Dependant List for this member
    fields=(db.patientmemberdependants.title,db.patientmemberdependants.fname,db.patientmemberdependants.lname,db.patientmemberdependants.depdob,db.patientmemberdependants.relation,db.patientmemberdependants.newmember,db.patientmemberdependants.freetreatment)

   

    headers={
        
             'patientmemberdependants.title':'Title',
             'patientmemberdependants.fname':'First Name',
             'patientmemberdependants.lname': 'Last Name',
             'patientmemberdependants.depdob': 'DOB',
             'patientmemberdependants.relation':'Relation',
             'patientmemberdependants.newmember': 'New Member',
             'patientmemberdependants.freetreatment':'Free Treatment'
             }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)

    left = None
    links = None ##[lambda row: A('Update',_href=URL("member","update_dependant", vars=dict(page=common.getgridpage(request.vars)),args=[row.id,memberid])), lambda row: A('Delete',_href=URL("member","delete_dependant",args=[row.id,memberid]))]

    query = (db.patientmemberdependants.patientmember == memberid) & (db.patientmemberdependants.is_active==True)


    ## called from menu
    formB = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=links,
                             left=left,
                             exportclasses=exportlist,
                             links_in_grid=True,
                             searchable=False,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )

    
    
    #if formA.process().accepted:
        #webmemberid = db(db.webmember.id == webmemberid).update(**db.webmember._filter_fields(formA.vars))
        #redirect(URL('enroll','member_update_contact', vars=dict(webmemberid=webmemberid)))
    
    #elif formA.errors:
        #response.flash = 'form has errors'    
        
    

    return dict(providername=provdict["providername"],formA=formA,formB=formB,providerid=provdict["providerid"],\
                member=member,fname=fname,lname=lname,cell=cell,email=email,page=page,\
                returnurl=returnurl)





#@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
#@auth.requires_login()
#def xlist_nonmembers():
    
    #session.nonmemberscount=True
    #provdict = common.getproviderfromid(db, request.vars.providerid)
    
    #page     = common.getgridpage(request.vars)    
    
    ##filtering fields    
    #member   = common.getstring(request.vars.member)
    #fname    = common.getstring(request.vars.fname)
    #lname    = common.getstring(request.vars.lname)
    #cell     = common.getstring(request.vars.cell)
    #email    = common.getstring(request.vars.email)
    
    ##display treatment plan filtering criteria
    #items_per_page = 5
    #limitby = (page*items_per_page,(page+1)*items_per_page+1) 
    
    ##display list of treatment plans
    #form = SQLFORM.factory(
            #Field('member','string',label='Non_Member', default=member),
            #Field('fname', 'string',label='First Name', default=fname),
            #Field('lname', 'string',label='Last Name', default=lname),
            #Field('cell', 'string', label='Cell Phone',  default=cell ),
            #Field('email', 'string', label='Email',  default=email )
            #)
    
    #submit = form.element('input',_type='submit')
    #submit['_value'] = 'Search'   
    
    #xmember = form.element('input',_id='no_table_member')
    #xmember['_class'] =  'w3-input w3-border '
    
    
    #xfname = form.element('input',_id='no_table_fname')
    #xfname['_class'] =  'w3-input w3-border  '
    
    #xlname = form.element('input',_id='no_table_lname')
    #xlname['_class'] =  'w3-input w3-border  '
    
    #xcell = form.element('input',_id='no_table_cell')
    #xcell['_class'] =  'w3-input w3-border  '

    #xemail = form.element('input',_id='no_table_email')
    #xemail['_class'] =  'w3-input w3-border  '

    #dsmembers = getdsmembers(db,request.vars.providerid,member,fname,lname,cell,email,limitby,"nonmembers")
    
    #if(len(dsmembers) > 0):
        #rangemssg = "Displaying records from  " + str(int(common.getvalue(limitby[0]))+1) + "  to  " + str(int(common.getvalue(limitby[1]))-1)
    #else:
        #rangemssg = "No records to display"
    
    
    #if form.accepts(request,session,keepvalues=True):
        
        
        #member     = common.getstring(form.vars.member)
        #fname      = common.getstring(form.vars.fname)
        #lname      = common.getstring(form.vars.lname)
        #cell       = common.getstring(form.vars.cell)
        #email      = common.getstring(form.vars.email)
    
        #dsmembers = getdsmembers(db,request.vars.providerid,member, fname,lname,cell,email,limitby,"nonmembers")
        #if(len(dsmembers) > 0):
            #rangemssg = "Displaying records from  " + str(int(common.getvalue(limitby[0]))+1) + "  to  " + str(int(common.getvalue(limitby[1]))-1)
        #else:
            #rangemssg = "No records to display"
        
        #returnurl =  URL('admin','providerhome')
        
    #elif form.errors:
        #response.flash = 'form has errors'         
    
    #returnurl =  URL('admin','providerhome')
    
    #return dict(dsmembers=dsmembers, limitby=limitby, providername=provdict["providername"],form=form,providerid=provdict["providerid"],\
                #member=member,fname=fname,lname=lname,cell=cell,email=email,page=page,items_per_page=items_per_page,\
                #returnurl=returnurl,rangemssg = rangemssg)


#def xupdate_nonmember():
    
    ##get provider information
    #provdict = common.getproviderfromid(db, request.vars.providerid)
    #providerid = int(common.getid(request.vars.providerid))
    #memberid = int(common.getid(request.vars.memberid))

    ##filtering fields    
    #member   = common.getstring(request.vars.member)
    #fname    = common.getstring(request.vars.fname)
    #lname    = common.getstring(request.vars.lname)
    #cell     = common.getstring(request.vars.cell)
    #email    = common.getstring(request.vars.email)
    
    ##these are the list members filter parameters
    #page     = common.getgridpage(request.vars)    
 
    #returnurl = URL('member','list_nonmembers', vars=dict(providerid=providerid,memberid=memberid,page=page,member=member,fname=fname,lname=lname,cell=cell,email=email))    

    #rows = db(db.patientmember.id == memberid).select()
    
 
    #formA = SQLFORM.factory(
        #Field('patientmember','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=rows[0].patientmember,requires=IS_NOT_EMPTY(), label="Member/Patient ID"),
        #Field('groupref','string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=1, label='Employee ID',writable=False, readable=False),
        #Field('dob','date', label='DOB',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border  date'),default=rows[0].dob),
        #Field('fname', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=rows[0].fname, label='First',requires=IS_NOT_EMPTY()),
        #Field('mname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '),  default=rows[0].mname, label='Middle'),
        #Field('lname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '),  default=rows[0].lname, label='Last',requires=IS_NOT_EMPTY()),
        #Field('gender','string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='w3-input w3-border '), default=rows[0].gender,label='Gender',requires=IS_IN_SET(gender.GENDER)),
        #Field('address1', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=rows[0].address1,label='Address 1', requires=IS_NOT_EMPTY()),
        #Field('address2', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '),  default=rows[0].address2,label='Address 2',requires=IS_NOT_EMPTY()),
        #Field('address3', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '),  default=rows[0].address3,label='Address 3'),
        #Field('city', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=rows[0].city,label='City',requires = IS_IN_SET(states.CITIES)),
        #Field('st', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='w3-input w3-border '), default=rows[0].st,label='State',requires = IS_IN_SET(states.STATES)),
        #Field('pin', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=rows[0].pin,label='Pin',requires=IS_NOT_EMPTY()),
        #Field('telephone', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=rows[0].telephone,label='Telephone'),
        #Field('cell', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=rows[0].cell,label='Cell'),
        #Field('email', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default=rows[0].email,label='Email'), 
        #Field('startdate','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _class='w3-input w3-border  date'), label='Start Date',default=rows[0].startdate,  \
                              #requires=IS_EMPTY_OR(IS_DATE(format=('%Y-%m-%d'))),length=20),
        #Field('status', 'string',widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='w3-input w3-border '),  label='Status',default=rows[0].status,requires = IS_IN_SET(status.STATUS)),
        #Field('provider','integer', default=0),
        #Field('company', 'integer', default=0),
        #Field('hmoplan', 'integert', default=0),
        #Field('hmopatientmember','boolean', default=False,writable=False, readable=False),
        #Field('image','upload',uploadfolder=os.path.join(request.folder,'uploads/images'), uploadseparate=True),
        
        #Field('paid', 'boolean',default=rows[0].paid,label='Paid'),
        #Field('enrollmentdate','date',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border  date'), default=request.now, label='Enrollment Date',writable=False, readable=False),
        #Field('terminationdate','date', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border  date'),label='Termination Date',default=request.now,writable=False, readable=False),
        #Field('duedate','date', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border  date'), label='Due Date',default=request.now ,writable=False, readable=False),
        #Field('premstartdt','date', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border  date'),label='Prem. Start Date',default=request.now ,writable=False, readable=False),
        #Field('premenddt','date', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border  date'), label='Prem. End Date',default=request.now,writable=False, readable=False),
        #Field('groupregion', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px;",_class='w3-input w3-border '), default=1, requires=IS_IN_DB(db, 'groupregion.id', '%(groupregion)s'),writable=False, readable=False),
        #Field('groupref', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Reference ID',length=50,writable=False, readable=False),
        #Field('pan', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Pan Card',length=20,writable=False, readable=False),
        #Field('webkey', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Web Key', default='', length=20,writable=False, readable=False),
        #Field('upgraded', 'boolean',default=False,label='Upgraded',writable=False, readable=False),
        #Field('renewed', 'boolean',default=False,label='Renewed',writable=False, readable=False),
        #Field('webmember','reference webmember',label='Member',writable=False, readable=False)
        
        
                    #)
    
    #formA = crud.update(db.patientmember, memberid,cast=int, message='Member Information Updated!')
                    
    #if formA.accepts(request,session,keepvalues=True):
        #db(db.patientmember.id == memberid).update(**db.patientmember._filter_fields(formA.vars))
        
        #redirect(URL('member','list_nonmembers', vars=dict(providerid=request.vars.providerid,memberid=memberid,page=0)))     
    #elif formA.errors:
        #errors = formA.error
    #else:
        #response.flash = 'please fill the form'                    
                    
    #return dict(providername=provdict["providername"],formA=formA,providerid=provdict["providerid"],\
                #member=member,fname=fname,lname=lname,cell=cell,email=email,page=page,image=rows[0].image,\
                #returnurl=returnurl)    



def update_nonmember():
    
    #get provider information
    provdict = common.getproviderfromid(db, request.vars.providerid)
    providerid = int(common.getid(request.vars.providerid))
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    member   = common.getstring(request.vars.member)
    
    #filtering fields    
    
    #fname    = common.getstring(request.vars.fname)
    #lname    = common.getstring(request.vars.lname)
    #cell     = common.getstring(request.vars.cell)
    #email    = common.getstring(request.vars.email)
    
    #these are the list members filter parameters
    page     = int(common.getpage(request.vars.page))
 
    returnurl = URL('member','list_nonmembers', vars=dict(providerid=providerid,page=page))    

    rows = db(db.patientmember.id == memberid).select()
    
   
    
    #db.patientmember.patientmember.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.dob.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='input-group form-control form-control-inline date-picker')
    #db.patientmember.fname.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    #db.patientmember.mname.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    #db.patientmember.lname.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    #db.patientmember.address1.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    #db.patientmember.address2.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    #db.patientmember.address3.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.city.widget = widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border ')
    db.patientmember.gender.widget = widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border ')
    db.patientmember.title.widget = widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border ')
    db.patientmember.st.widget = widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border ')
    #db.patientmember.pin.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.telephone.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    #db.patientmember.cell.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    #db.patientmember.email.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')
    db.patientmember.startdate.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border  date')
    db.patientmember.status.widget = widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border ')
    #db.patientmember.groupref.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border ')

    db.patientmember.patientmember.default=rows[0].patientmember
   
    db.patientmember.dob.default=rows[0].dob
    db.patientmember.fname.default=rows[0].fname
    db.patientmember.mname.default=rows[0].mname
    db.patientmember.lname.default=rows[0].lname
    db.patientmember.address1.default=rows[0].address1
    db.patientmember.address2.default=rows[0].address2
    db.patientmember.address3.default=rows[0].address3
    db.patientmember.city.default=rows[0].city
    db.patientmember.gender.default=rows[0].gender
    db.patientmember.title.default=rows[0].title
    db.patientmember.st.default=rows[0].st
    db.patientmember.pin.default=rows[0].pin
    db.patientmember.telephone.default=rows[0].telephone
    db.patientmember.cell.default=rows[0].cell
    db.patientmember.email.default=rows[0].email
    db.patientmember.startdate.default=rows[0].startdate
    db.patientmember.status.default=rows[0].status
    db.patientmember.image.default=rows[0].image
    db.patientmember.newmember.default = rows[0].newmember
    db.patientmember.freetreatment.default = rows[0].freetreatment
    db.patientmember.groupref.default = rows[0].groupref

    db.patientmember.pan.default = ''
    db.patientmember.webkey.default = ''
    db.patientmember.groupregion.default = 1
    
    db.patientmember.enrollmentdate.default = request.now
    db.patientmember.terminationdate.default = request.now
    db.patientmember.premstartdt.default = request.now
    db.patientmember.premenddt.default = request.now
    db.patientmember.duedate.default = request.now
    
    db.patientmember.paid.default = False
    db.patientmember.upgraded.default = False
    db.patientmember.renewed.default = False
    db.patientmember.hmopatientmember.default = False
    
    db.patientmember.provider.default = providerid
    db.patientmember.company.default = 1
    db.patientmember.hmoplan.default = 1
    
    
    db.patientmember.groupref.readable = True
    db.patientmember.groupref.writable = True
    db.patientmember.enrollmentdate.readable = False
    db.patientmember.enrollmentdate.writable = True
    db.patientmember.terminationdate.readable = False
    db.patientmember.terminationdate.writable = True
    db.patientmember.premstartdt.readable = False
    db.patientmember.premstartdt.writable = True
    db.patientmember.premenddt.readable = False
    db.patientmember.premenddt.writable = True
    db.patientmember.groupregion.readable = False
    db.patientmember.groupregion.writable = True
    db.patientmember.pan.readable = False
    db.patientmember.pan.writable = True
    db.patientmember.webkey.readable = False
    db.patientmember.webkey.writable = True
    db.patientmember.upgraded.readable = False
    db.patientmember.upgraded.writable = True
    db.patientmember.renewed.readable = False
    db.patientmember.renewed.writable = True
    db.patientmember.webmember.readable = False
    db.patientmember.webmember.writable = True
    

                
    db.patientmember.hmopatientmember.readable = False
    db.patientmember.hmopatientmember.writable = True
                        
    db.patientmember.gender.requires=IS_EMPTY_OR(IS_IN_SET(gender.GENDER))
    db.patientmember.title.requires=IS_EMPTY_OR(IS_IN_SET(gender.PATTITLE))
    db.patientmember.st.requires = IS_EMPTY_OR(IS_IN_SET(states.STATES))
    db.patientmember.city.requires = IS_EMPTY_OR(IS_IN_SET(states.CITIES))
    db.patientmember.startdate.requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))
    db.patientmember.dob.requires = IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))
    db.patientmember.address1.requires = ""
    db.patientmember.address2.requires = ""
    db.patientmember.pin.requires = ""
    db.patientmember.email.requires  = ""
    db.patientmember.groupregion.requires = ""
    db.patientmember.company.requires = ""
    db.patientmember.hmoplan.requires = ""
    db.patientmember.fname.requires = IS_NOT_EMPTY()
    db.patientmember.lname.requires = IS_NOT_EMPTY()
    
    crud.settings.update_next = URL('member','list_nonmembers', vars=dict(providerid=providerid,page=page)) 
    
    formA = crud.update(db.patientmember, memberid,cast=int, message='Member Information Updated!')

    xpatid = formA.element('input',_id='patientmember_patientmember')
    xpatid['_class'] = 'form-control'
    xpatid['_autocomplete'] = 'off' 
       
    fn = formA.element('input',_id='patientmember_fname')
    fn['_class'] = 'form-control'
    fn['_autocomplete'] = 'off' 
    
    mn = formA.element('input',_id='patientmember_mname')
    mn['_class'] = 'form-control'
    mn['_autocomplete'] = 'off' 
    
    ln = formA.element('input',_id='patientmember_lname')
    ln['_class'] = 'form-control'
    ln['_autocomplete'] = 'off' 

    grp = formA.element('input',_id='patientmember_groupref')
    grp['_class'] = 'form-control'
    grp['_autocomplete'] = 'off' 
    
    a1 = formA.element('input',_id='patientmember_address1')
    a1['_class'] = 'form-control'
    a1['_autocomplete'] = 'off' 
    
    a2 = formA.element('input',_id='patientmember_address2')
    a2['_class'] = 'form-control'
    a2['_autocomplete'] = 'off' 

    a3 = formA.element('input',_id='patientmember_address3')
    a3['_class'] = 'form-control'
    a3['_autocomplete'] = 'off' 

    pin = formA.element('input',_id='patientmember_pin')
    pin['_class'] = 'form-control'
    pin['_autocomplete'] = 'off' 

    cell = formA.element('input',_id='patientmember_cell')
    cell['_class'] = 'form-control'
    cell['_autocomplete'] = 'off' 
    
    email = formA.element('input',_id='patientmember_email')
    email['_class'] = 'form-control'
    email['_autocomplete'] = 'off' 
    
    
    xdob = formA.element('input',_id='patientmember_dob')
    xdob['_class'] =  'input-group form-control form-control-inline date-picker'
    xdob['_data-date-format'] = 'dd/mm/yyyy'
    xdob['_autocomplete'] = 'off'  
    xdob['_placeholder'] = 'dd/mm/yyyy'  
    
    xstdt = formA.element('input',_id='patientmember_startdate')
    xstdt['_class'] =  'input-group form-control form-control-inline date-picker'
    xstdt['_data-date-format'] = 'dd/mm/yyyy'
    xstdt['_autocomplete'] = 'off'     
    xstdt['_placeholder'] = 'dd/mm/yyyy'  
    
    xfn = formA.element('input',_id='patientmember_patientmember')
    xfn['_readonly'] = 'readonly'    
         
    return dict(providername=provdict["providername"],formA=formA,providerid=providerid,memberid=memberid,\
                member=member,page=page,image=rows[0].image,\
                returnurl=returnurl)    
    




def new_nonmember():
    
    if(len(request.vars)<=0):
        raise HTTP(403,"Error: No Member to create+: member_update()")

    #get provider information
    provdict = common.getprovider(auth, db)
    providerid = provdict["providerid"]
    providername = provdict["providername"]    

    provider = provdict["provider"]
    provcount = db(db.patientmember.provider == providerid).count()
    
    patientmember = provider + str(provcount).zfill(4)
    
    
    #these are the list members filter parameters
    page     = 1   
    member   = common.getstring(request.vars['member'])
    fname    = common.getstring(request.vars['fname'])
    lname    = common.getstring(request.vars['lname'])
    cell     = common.getstring(request.vars['cell'])
    email    = common.getstring(request.vars['email'])
    
    returnurl = common.getstring(request.vars.returnurl)
    
    returnurl = returnurl if(returnurl != "") else     URL('member','list_nonmembers', vars=dict(providerid=request.vars.providerid,page=page,member=member,fname=fname,lname=lname,cell=cell,email=email))     
    
    
    
    
    hmoplanid = 1
    companyid = 114 #default to Walkin
    r = db((db.company.company == "walkin") & (db.company.is_active == False)).select()
    if(len(r) > 0):
        companyid = common.getid(r[0].id)
    
    def_prem_start = request.now
    def_prem_end = common.addyears(def_prem_start, 100)
    
    formA = SQLFORM.factory(
                    Field('patientmember','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'), default=patientmember,requires=IS_NOT_EMPTY(), label="Member/Patient ID"),
                    Field('groupref','string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default=1, label='Employee ID',writable=False, readable=False),
                    Field('dob','date', label='DOB',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
                    Field('title','string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '), default=" ",label='Title',requires=IS_EMPTY_OR(IS_IN_SET(gender.PATTITLE))),
                    Field('fname', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default="", label='First',requires=IS_NOT_EMPTY()),
                    Field('mname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '),  default="", label='Middle'),
                    Field('lname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '),  default="", label='Last',requires=IS_NOT_EMPTY()),
                    Field('gender','string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '), default="Male",label='Gender',requires=IS_EMPTY_OR(IS_IN_SET(gender.GENDER))),
                    Field('address1', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default="",label='Address 1'),
                    Field('address2', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '),  default="",label='Address 2'),
                    Field('address3', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '),  default="",label='Address 3'),
                    Field('city', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '), default="--Select City--",label='City',requires = IS_EMPTY_OR(IS_IN_SET(states.CITIES))),
                    Field('st', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '), default="--Select State--",label='State',requires = IS_EMPTY_OR(IS_IN_SET(states.STATES))),
                    Field('pin', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default="",label='Pin'),
                    Field('telephone', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default="",label='Telephone'),
                    Field('cell', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default="",label='Cell',requires=IS_NOT_EMPTY()),
                    Field('email', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default="",label='Email',requires=IS_EMPTY_OR(IS_EMAIL())), 
                    Field('enrollmentdate','date',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'), default=def_prem_start, label='Enrollment Date'),
                    Field('terminationdate','date', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'),label='Termination Date',default=def_prem_end),
                    Field('duedate','date', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'), label='Due Date',default=def_prem_end ),
                    Field('premstartdt','date', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'),label='Prem. Start Date',default=def_prem_start ),
                    Field('premenddt','date', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'), label='Prem. End Date',default=def_prem_end),
                    Field('startdate','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _class='form-control  date'), label='Start Date',default=def_prem_start,  \
                                          requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))),length=20),
                    Field('status', 'string',widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '),  label='Status',default="Enrolled",requires = IS_EMPTY_OR(IS_IN_SET(status.STATUS))),
                    Field('provider','integer', default=providerid),
                    Field('company', 'integer', default=companyid),
                    Field('hmoplan', 'integert', default=hmoplanid),
                    Field('hmopatientmember','boolean', default=False),
                    Field('image','upload'),
                    Field('paid', 'boolean',default=False,label='Paid'),

                    Field('groupregion', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_style="width:100%;height:35px;",_class='form-control '), default=1),
                    Field('groupref', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Reference ID',length=50,writable=False, readable=False),
                    Field('pan', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Pan Card',length=20,writable=False, readable=False),
                    Field('webkey', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Web Key', default='', length=20,writable=False, readable=False),
                    Field('upgraded', 'boolean',default=False,label='Upgraded',writable=False, readable=False),
                    Field('renewed', 'boolean',default=False,label='Renewed',writable=False, readable=False),
                    Field('webmember','integer',label='Member',default=1),
                    Field('newmember','boolean',label='Member',default=False, writable=False, readable=True),
                    Field('freetreatment','boolean',label='Member',default=True, writable=False, readable=True)
                   )
    
    
    xdob = formA.element('input',_id='no_table_dob')
    xdob['_class'] =  'input-group form-control form-control-inline date-picker'
    xdob['_data-date-format'] = 'dd/mm/yyyy'
    xdob['_autocomplete'] = 'off' 
    xdob['_placeholder'] = 'dd/mm/yyyy' 

    startdate = formA.element('input',_id='no_table_startdate')
    startdate['_class'] =  'input-group form-control form-control-inline date-picker'
    startdate['_data-date-format'] = 'dd/mm/yyyy'
    startdate['_autocomplete'] = 'off' 
    startdate['_placeholder'] = 'dd/mm/yyyy' 
    
    xfn = formA.element('input',_id='no_table_patientmember')
    xfn['_readonly'] = 'readonly'
    
    db.patientmember.patientmember.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _readonly, _class='form-control ')
    
    if formA.accepts(request,session,keepvalues=True):
        memberid = db.patientmember.insert(**db.patientmember._filter_fields(formA.vars))
        common.dashboard(db,session,providerid)
        session.flash = 'New Patient Added!'
        redirect(returnurl)     
    elif formA.errors:
      
        response.flash = 'Error adding a New Paient' + str(formA.errors)
        
   
    
    return dict(providername=provdict["providername"],formA=formA,providerid=provdict["providerid"],\
                member=member,fname=fname,lname=lname,cell=cell,email=email,page=page,\
                returnurl=returnurl)


def history_member():
    
    
    providerid = int(common.getid(request.vars.providerid))
    provdict   = common.getproviderfromid(db, providerid)
    memberid   = int(common.getid(request.vars.memberid))
    patientid  = int(common.getid(request.vars.patientid))
    page     = int(common.getpage(request.vars.page))

    patientmember = ""
    patientname = ""
    planid = 0
    plancode = ""
    planname = ""
    pattype = ""
    
    members = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).select()
    if(len(members) > 0):
        patientname = common.getstring(members[0].fullname)
        patientmember = common.getstring(members[0].patientmember)
        pattype = common.getstring(members[0].patienttype)
        planid = int(common.getid(members[0].hmoplan))
        plancode = common.getstring(members[0].hmoplancode)
        planname = common.getstring(members[0].hmoplanname)
        
    
    
    returnurl = URL('member','list_nonmembers', vars=dict(providerid=providerid,page=page))           

    formHist = SQLFORM.factory(
        Field('chestpain', 'boolean',default=False,label=''),
        Field('shortbreath', 'boolean',default=False,label=''),
        Field('bloodpressure', 'boolean',default=False,label=''),
        Field('heartmurmur', 'boolean',default=False,label=''),
        Field('heartvalve', 'boolean',default=False,label=''),
        Field('heartmedicince', 'boolean',default=False,label=''),
        Field('rheumaticfever', 'boolean',default=False,label=''),
        Field('pacemaker', 'boolean',default=False,label=''),
        Field('artificialvalve', 'boolean',default=False,label=''),
                    
        Field('bruising', 'boolean',default=False,label=''),
        Field('nosebleeds', 'boolean',default=False,label=''),
        Field('bleeding', 'boolean',default=False,label=''),
        Field('blooddisease', 'boolean',default=False,label=''),
        Field('bloodtransfusion', 'boolean',default=False,label=''),
        
        
        Field('hayfever', 'boolean',default=False,label=''),
        Field('sinus', 'boolean',default=False,label=''),
        Field('skinrash', 'boolean',default=False,label=''),
        Field('allergymedicine', 'boolean',default=False,label=''),
        Field('asthma', 'boolean',default=False,label=''),
        
        
        Field('ulcers', 'boolean',default=False,label=''),
        Field('weight', 'boolean',default=False,label=''),
        Field('diet', 'boolean',default=False,label=''),
        Field('constipation', 'boolean',default=False,label=''),
        Field('kidneyproblem', 'boolean',default=False,label=''),
        
        
        Field('arthritis', 'boolean',default=False,label=''),
        Field('backneckpain', 'boolean',default=False,label=''),
        Field('jointrplc', 'boolean',default=False,label=''),


        Field('faintingspells', 'boolean',default=False,label=''),
        Field('strokes', 'boolean',default=False,label=''),
        Field('headaches', 'boolean',default=False,label=''),
        Field('thyroid', 'boolean',default=False,label=''),
        Field('swollenglands', 'boolean',default=False,label=''),
        Field('premedication', 'boolean',default=False,label=''),
        Field('cancer', 'boolean',default=False,label=''),
            
        Field('urination', 'boolean',default=False,label=''),
        Field('drymouth', 'boolean',default=False,label=''),
        Field('diabeteshistory', 'boolean',default=False,label=''),
        
        Field('tb', 'boolean',default=False,label=''),
        Field('alcholol', 'boolean',default=False,label=''),
        Field('smoking', 'boolean',default=False,label=''),
        Field('hepatitis', 'boolean',default=False,label=''),
        Field('std', 'boolean',default=False,label=''),

        Field('hiv', 'boolean',default=False,label=''),
        Field('glaucoma', 'boolean',default=False,label=''),
        Field('contacts', 'boolean',default=False,label=''),
        Field('headinjury', 'boolean',default=False,label=''),
        Field('eplilepsy', 'boolean',default=False,label=''),
        Field('drugabuse', 'boolean',default=False,label=''),

        Field('unlisted', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default='',label=''),
        
        
        Field('antibiotics', 'boolean',default=False,label=''),
        Field('anticoagulants', 'boolean',default=False,label=''),
        Field('bpmedicine', 'boolean',default=False,label=''),
        Field('tranqulizers', 'boolean',default=False,label=''),
        Field('insulin', 'boolean',default=False,label=''),
        Field('aspirin', 'boolean',default=False,label=''),
        Field('digitalis', 'boolean',default=False,label=''),
        Field('nitroglycerine', 'boolean',default=False,label=''),
        Field('cortisone', 'boolean',default=False,label=''),
        Field('natural', 'boolean',default=False,label=''),
        Field('supplements', 'boolean',default=False,label=''),
        Field('others', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default='',label=''),
        
        
        Field('alcoholqty', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default='',label=''),
        Field('smokeqty', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default='',label=''),
        
        
        Field('anesthetics', 'boolean',default=False,label=''),
        Field('penicillin', 'boolean',default=False,label=''),
        Field('sulfa', 'boolean',default=False,label=''),
        Field('barbiturates', 'boolean',default=False,label=''),
        Field('aspirintabs', 'boolean',default=False,label=''),
        Field('codeine', 'boolean',default=False,label=''),
        Field('metalreaction', 'boolean',default=False,label=''),
        Field('lates', 'boolean',default=False,label=''),
        Field('othersmeds', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default='',label=''),
        
        Field('contraceptives', 'boolean',default=False,label=''),
        Field('pregnant', 'boolean',default=False,label=''),
        Field('nursing', 'boolean',default=False,label=''),
        Field('menopause', 'boolean',default=False,label=''),
        Field('menopausesympts', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control '), default='',label=''),

        Field('notes','text', label='', default=''),
        
        Field('treatment', 'boolean',default=False,label=''),
        Field('treatmentproblems', 'boolean',default=False,label=''),
        Field('gag', 'boolean',default=False,label=''),
        Field('dentures', 'boolean',default=False,label=''),
        Field('foodcatch', 'boolean',default=False,label=''),
        Field('chewing', 'boolean',default=False,label=''),
        Field('oneside', 'boolean',default=False,label=''),
        Field('brushingpain', 'boolean',default=False,label=''),
        Field('gumbleed', 'boolean',default=False,label=''),
        Field('swollengums', 'boolean',default=False,label=''),
        Field('flossbleeding', 'boolean',default=False,label=''),
        Field('sores', 'boolean',default=False,label=''),
        Field('sensitive', 'boolean',default=False,label=''),
        Field('hotfood', 'boolean',default=False,label=''),
        Field('coldfood', 'boolean',default=False,label=''),
        Field('sours', 'boolean',default=False,label=''),
        Field('sweets', 'boolean',default=False,label=''),
        Field('fluoride', 'boolean',default=False,label=''),
        Field('save', 'boolean',default=False,label=''),
        Field('complete', 'boolean',default=False,label=''),
        Field('brushfreq', 'boolean',default=False,label=''),
        Field('flossfreq', 'boolean',default=False,label=''),
        Field('jawnoise', 'boolean',default=False,label=''),
        Field('jawclench', 'boolean',default=False,label=''),
        Field('jawtired', 'boolean',default=False,label=''),
        Field('jawstuck', 'boolean',default=False,label=''),
        
        Field('jawhurt', 'boolean',default=False,label=''),
        Field('earaches', 'boolean',default=False,label=''),
        Field('morningpain', 'boolean',default=False,label=''),
        Field('appetite', 'boolean',default=False,label=''),
        Field('depressing', 'boolean',default=False,label=''),
        Field('painmeds', 'boolean',default=False,label=''),
        Field('jawdisorder', 'boolean',default=False,label=''),
        Field('facepain', 'boolean',default=False,label=''),
        Field('uncomfrotablebite', 'boolean',default=False,label=''),
        Field('jawtrauma', 'boolean',default=False,label=''),
        Field('gumchewer', 'boolean',default=False,label='')
        
                   )
    
    
    if formHist.accepts(request,session,keepvalues=True):
        memberid = db.patientmember.insert(**db.patientmember._filter_fields(formHist.vars))
        common.dashboard(db,session,providerid)
        session.flash = 'Patient History Added/Update!'
        redirect(URL('member','update_nonmember', vars=dict(providerid=request.vars.providerid,memberid=memberid,page=0)))     
    elif formHist.errors:
        response.flash = 'Error updating Patient history ' + str(formHist.errors)
        
    else:
        response.flash = 'Please complete Patient history form'
    
    
    
    return dict(formHist=formHist,page=page, providerid=providerid, providername=provdict["providername"], \
                patientmember=patientmember, patientname=patientname,pattype=pattype,planid=planid,plancode=plancode, planname = planname,\
                memberid=memberid, patientid=patientid, returnurl = returnurl)

def xhistory_member():
    
    
    if(len(request.vars)<=0):
        raise HTTP(403,"Error: No Member Profile : history_nonmember")
    
    providerid = int(common.getid(request.vars.providerid))
    provdict   = common.getproviderfromid(db, providerid)
    memberid   = int(common.getid(request.vars.memberid))
    patientid  = int(common.getid(request.vars.patientid))
    member   = common.getstring(request.vars.member)
    page     = int(common.getpage(request.vars.page))
    
 
    returnurl = URL('member','list_nonmembers', vars=dict(providerid=providerid,page=page))       

    hmoplanid = 1
    companyid = 4 #default to MyDP
    r = db((db.company.company == ' ') & (db.company.is_active == False)).select()
    if(len(r) > 0):
        companyid = int(common.getid(r[0].id))
    
        
    
    formHist = SQLFORM.factory(
        Field('chestpain', 'boolean',default=False,label=''),
        Field('shortbreath', 'boolean',default=False,label=''),
        Field('bloodpressure', 'boolean',default=False,label=''),
        Field('heartmurmur', 'boolean',default=False,label=''),
        Field('heartvalve', 'boolean',default=False,label=''),
        Field('heartmedicince', 'boolean',default=False,label=''),
        Field('rheumaticfever', 'boolean',default=False,label=''),
        Field('pacemaker', 'boolean',default=False,label=''),
        Field('artificialvalve', 'boolean',default=False,label=''),
                    
        Field('bruising', 'boolean',default=False,label=''),
        Field('nosebleeds', 'boolean',default=False,label=''),
        Field('bleeding', 'boolean',default=False,label=''),
        Field('blooddisease', 'boolean',default=False,label=''),
        Field('bloodtransfusion', 'boolean',default=False,label=''),
        
        
        Field('hayfever', 'boolean',default=False,label=''),
        Field('sinus', 'boolean',default=False,label=''),
        Field('skinrash', 'boolean',default=False,label=''),
        Field('allergymedicine', 'boolean',default=False,label=''),
        Field('asthma', 'boolean',default=False,label=''),
        
        
        Field('ulcers', 'boolean',default=False,label=''),
        Field('weight', 'boolean',default=False,label=''),
        Field('diet', 'boolean',default=False,label=''),
        Field('constipation', 'boolean',default=False,label=''),
        Field('kidneyproblem', 'boolean',default=False,label=''),
        
        
        Field('arthritis', 'boolean',default=False,label=''),
        Field('backneckpain', 'boolean',default=False,label=''),
        Field('jointrplc', 'boolean',default=False,label=''),


        Field('faintingspells', 'boolean',default=False,label=''),
        Field('headaches', 'boolean',default=False,label=''),
        Field('thyroid', 'boolean',default=False,label=''),
        Field('swollenglands', 'boolean',default=False,label=''),
        Field('premedication', 'boolean',default=False,label=''),
        Field('cacer', 'boolean',default=False,label=''),
            
        Field('urination', 'boolean',default=False,label=''),
        Field('drymouth', 'boolean',default=False,label=''),
        Field('diabeteshistory', 'boolean',default=False,label=''),
        
        Field('tb', 'boolean',default=False,label=''),
        Field('alcholol', 'boolean',default=False,label=''),
        Field('smoking', 'boolean',default=False,label=''),
        Field('hepatitis', 'boolean',default=False,label=''),
        Field('std', 'boolean',default=False,label=''),

        Field('hiv', 'boolean',default=False,label=''),
        Field('glaucoma', 'boolean',default=False,label=''),
        Field('contacts', 'boolean',default=False,label=''),
        Field('headinjury', 'boolean',default=False,label=''),
        Field('eplilepsy', 'boolean',default=False,label=''),
        Field('drugabuse', 'boolean',default=False,label=''),

        Field('unlisted', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default='',label=''),
        
        
        Field('antibiotics', 'boolean',default=False,label=''),
        Field('anticoagulants', 'boolean',default=False,label=''),
        Field('bpmedicine', 'boolean',default=False,label=''),
        Field('tranqulizers', 'boolean',default=False,label=''),
        Field('insulin', 'boolean',default=False,label=''),
        Field('aspirin', 'boolean',default=False,label=''),
        Field('digitalis', 'boolean',default=False,label=''),
        Field('nitroglycerine', 'boolean',default=False,label=''),
        Field('cortisone', 'boolean',default=False,label=''),
        Field('natural', 'boolean',default=False,label=''),
        Field('supplements', 'boolean',default=False,label=''),
        Field('others', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default='',label=''),
        
        
        Field('alcoholqty', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default='',label=''),
        Field('smokeqty', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default='',label=''),
        
        
        Field('anesthetics', 'boolean',default=False,label=''),
        Field('penicillin', 'boolean',default=False,label=''),
        Field('sulfa', 'boolean',default=False,label=''),
        Field('barbiturates', 'boolean',default=False,label=''),
        Field('aspirintabs', 'boolean',default=False,label=''),
        Field('codeine', 'boolean',default=False,label=''),
        Field('metalreaction', 'boolean',default=False,label=''),
        Field('lates', 'boolean',default=False,label=''),
        Field('othersmeds', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default='',label=''),
        
        Field('contraceptives', 'boolean',default=False,label=''),
        Field('pregnant', 'boolean',default=False,label=''),
        Field('nursing', 'boolean',default=False,label=''),
        Field('menopause', 'boolean',default=False,label=''),
        Field('menopausesympts', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border '), default='',label=''),

        Field('notes','text', label='', default=''),
        
        Field('treatment', 'boolean',default=False,label=''),
        Field('treatmentproblems', 'boolean',default=False,label=''),
        Field('gag', 'boolean',default=False,label=''),
        Field('dentures', 'boolean',default=False,label=''),
        Field('foodcatch', 'boolean',default=False,label=''),
        Field('chewing', 'boolean',default=False,label=''),
        Field('oneside', 'boolean',default=False,label=''),
        Field('brushingpain', 'boolean',default=False,label=''),
        Field('gumbleed', 'boolean',default=False,label=''),
        Field('swollengums', 'boolean',default=False,label=''),
        Field('flossbleeding', 'boolean',default=False,label=''),
        Field('sores', 'boolean',default=False,label=''),
        Field('sensitive', 'boolean',default=False,label=''),
        Field('hotfood', 'boolean',default=False,label=''),
        Field('coldfood', 'boolean',default=False,label=''),
        Field('sours', 'boolean',default=False,label=''),
        Field('sweets', 'boolean',default=False,label=''),
        Field('fluoride', 'boolean',default=False,label=''),
        Field('save', 'boolean',default=False,label=''),
        Field('complete', 'boolean',default=False,label=''),
        Field('brushfreq', 'boolean',default=False,label=''),
        Field('flossfreq', 'boolean',default=False,label=''),
        Field('jawnoise', 'boolean',default=False,label=''),
        Field('jawclench', 'boolean',default=False,label=''),
        Field('jawtired', 'boolean',default=False,label=''),
        Field('jawstuck', 'boolean',default=False,label=''),
        
        Field('jawhurt', 'boolean',default=False,label=''),
        Field('earaches', 'boolean',default=False,label=''),
        Field('morningpain', 'boolean',default=False,label=''),
        Field('appetite', 'boolean',default=False,label=''),
        Field('depressing', 'boolean',default=False,label=''),
        Field('painmeds', 'boolean',default=False,label=''),
        Field('jawdisorder', 'boolean',default=False,label=''),
        Field('facepain', 'boolean',default=False,label=''),
        Field('uncomfrotablebite', 'boolean',default=False,label=''),
        Field('jawtrauma', 'boolean',default=False,label=''),
        Field('gumchewer', 'boolean',default=False,label='')
        
                   )
    
    
    if formHist.accepts(request,session,keepvalues=True):
        memberid = db.patientmember.insert(**db.patientmember._filter_fields(formA.vars))
        common.dashboard(db,session,providerid)
        session.flash = 'New Patient Added!'
        redirect(URL('member','update_nonmember', vars=dict(providerid=request.vars.providerid,memberid=memberid,page=0)))     
    elif formA.errors:
        response.flash = formA.errors
        
    else:
        response.flash = 'please fill the form'
    
    return dict(providername=provdict["providername"],formA=formA,providerid=provdict["providerid"],\
                member=member,fname=fname,lname=lname,cell=cell,email=email,page=page,\
                returnurl=returnurl)

    
