from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)


from shutil import copyfile

import os
from base64 import decodestring
import json

import datetime
import time
import calendar
from datetime import timedelta
import math

#import sys
#sys.path.append('modules')
from applications.my_pms2.modules import common
from applications.my_pms2.modules import mail
from applications.my_pms2.modules import status
from applications.my_pms2.modules import account
from applications.my_pms2.modules import gender
from applications.my_pms2.modules import logger

from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import mdpreligare
from applications.my_pms2.modules import mdprules

from applications.my_pms2.modules import mdputils


#from gluon.contrib import common
#from gluon.contrib import mail
#from gluon.contrib import status
#from gluon.contrib import account
#from gluon.contrib import gender
#from gluon.contrib import logger




def changeinnotes(currnotes, newnotes):
    retVal = True
    
    
    if(common.getstring(currnotes).strip().upper() == common.getstring(newnotes).strip().upper()):
        retVal = False
    
    return retVal



#def getpresgrid(memberid, patientid,providerid):
    
    #prescriptions = db((db.vw_patientprescription.providerid == providerid) & \
                              #(db.vw_patientprescription.is_active == True) & \
                              #(db.vw_patientprescription.patientid == patientid) & \
                              #(db.vw_patientprescription.memberid == memberid)).select()
    
    
    
    #return prescriptions





#def getmedtestgrid(patientid, providerid):
    #medtestquery = ((db.medicaltest.patientid == patientid) & (db.medicaltest.providerid == providerid) & (db.medicaltest.is_active == True))
    
    #medtestfields=(db.medicaltest.testname,db.medicaltest.actval,db.medicaltest.upval, db.medicaltest.lowval, db.medicaltest.typval, db.medicaltest.modified_on)
    
    #medtestheaders={
        
        #'medicaltest.modified_on':'Date',
        #'medicaltest.testname':'Medical Test',
        #'medicaltest.actval':'Actual Value',
        #'medicaltest.lowval':'Lower Value',
        #'medicaltest.typval':'Typical Value',
        #'medicaltest.upval':'Upper Value'
                #}

    #db.medicaltest.modified_on.readable = True
    #db.medicaltest.modified_on.writable = True
 
    #medtestexport = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
     
    #medtestorderby = ~db.medicaltest.modified_on
       
    #medtestgrid = SQLFORM.grid(query=medtestquery,
                        #headers=medtestheaders,
                        #fields=medtestfields,
                        #paginate=20,
                        #orderby=medtestorderby,
                        #exportclasses=medtestexport,
                        #links_in_grid=False,
                        #searchable=False,
                        #create=False,
                        #deletable=False,
                        #editable=False,
                        #details=False,
                        #user_signature=True
                       #)
    
    #return medtestgrid

def image_selector():
    is_active = True
    page=int(common.getid(request.vars.xpage))
    memberpage = int(common.getid(request.vars.memberpage))
    patientid = int(common.getid(request.vars.patientid))
    providerid = int(common.getid(request.vars.providerid))
    memberid = int(common.getid(request.vars.memberid))
    patient = common.getstring(request.vars.patient)
    providername = common.getstring(request.vars.providername)
    fullname = common.getstring(request.vars.fullname)
    memberref = common.getstring(request.vars.memberref)
    
    items_per_page = 4
    limitby = ((page)*items_per_page,(page+1)*items_per_page) 
    
    if(patientid >0):
        r = db((db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).select()
    else:
        r = db((db.vw_memberpatientlist.patientid == patient) & (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).select()
        
        if(len(r) > 0):
            memberid = int(common.getid(r[0].primarypatientid))
            patientid = int(common.getid(r[0].patientid))
            memberref = common.getstring(r[0].patientmember)  #patientmember
            fullname = common.getstring(r[0].fullname)      #fname + lname
            patient = common.getstring(r[0].patient)    #fname + lname + patientmemebr
        

    images = getimages(db, providerid, patientid, limitby, is_active)    
    imagescount = len(images)
       
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
    
       
    if(session.nonmemberscount == True):
        returnurl =  URL('member','list_nonmembers', vars=dict(providerid=providerid,page=memberpage))    
    else:
        returnurl =  URL('member','list_members', vars=dict(providerid=providerid,page=memberpage))    
    
       
    return dict(images=images, returnurl=returnurl, page=page, items_per_page=items_per_page, limitby=limitby, rangemssg=rangemssg,memberpage=memberpage, memberid=memberid, patientid=patientid, memberref=memberref,fullname=fullname,providerid=providerid, providername=providername,patient=patient)    
    



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def getimages(db,providerid, patientid,limitby,is_active):
    
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
        
    return dsimages




def patients():
    
    ppid = common.getid(request.vars.primarypatient)
    patients = db(db.vw_primarypatientlist.id == ppid).select()
    return dict(patients = patients)

def patientsonupdate():
    
    ppid = common.getid(request.vars.primarypatient)
    pid = common.getid(request.vars.patient)
    
    patients = db((db.vw_primarypatientlist.id == ppid) & (db.vw_primarypatientlist.auxid == pid)).select()
    #patients = db((db.vw_primarypatientlist.id == ppid)).select()
    return dict(patients = patients,ppid=ppid,pid=pid)

def addtplanprocedure():

    ## Add records in POITEM tables
    treatmentid = int(request.args[6])
    
    tplanid = int(request.args[7])
    patientid = int(request.args[8])
    providerid = int(request.args[9])
    ids = request.args[1].split('_')
    redirectURL = URL(request.args[3],request.args[4],request.args[5],args=[treatmentid,tplanid,patientid,providerid])
    
    for x in ids:
        if len(x) > 0:
            if isinstance(int(x),int):
                #db.treatment.update(treatmentplan=tplanid, procedurecode=int(x))
                db(db.treatment.id==treatmentid).update(dentalprocedure=int(x))
        
    
    redirect(redirectURL)
    
@auth.requires_login()
def deltplan_patient(tplanid):

    ## Add records in POITEM tables
    db(db.treatmentplan_patient.treatmentplan == tplanid).delete()
    
    return dict()

@auth.requires_login()
def addtplan_patient(tplanid, patientid):

    ## Add records in POITEM tables
    db.treatmentplan_patient.update_or_insert(treatmentplan=tplanid, patientmember=patientid)
    return dict()

@auth.requires_login()    
def addtplanpatient():

    ## Add records in POITEM tables
    tplanid = request.args[1]
    ids = request.args[1].split('_')
    redirectURL = URL(request.args[3],request.args[4],request.args[5],args=tplanid)
    
    for x in ids:
        if len(x) > 0:
            if isinstance(int(x),int):
                db.treatmentplan_patient.insert(treatmentplan=tplanid, patientmember=int(x))
        
    
    redirect(redirectURL)



def calculatedue(tplanid):
    totaldue     = 0
    tprows = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).select(db.treatmentplan.totaltreatmentcost,\
                                                                                                db.treatmentplan.totalpaid,\
                                                                                                db.treatmentplan.totalcopaypaid,\
                                                                                                db.treatmentplan.totalinspaid)
    
    if(len(tprows) == 1):
        totaldue = float(common.getvalue(tp.totaltreatmentcost)) - float(common.getvalue(tp.totalpaid)) - float(common.getvalue(tp.totalcopaypaid)) - float(common.getvalue(tp.totalinspaid))
        
         
        
    db(db.treatmentplan.id==tplanid).update(totaldue=totaldue)

    
    
def calculatetreatmentcopay(db,treatmentid,patientid):
    copay = account.copayment_treatment(db,treatmentid,patientid)
    db(db.treatment.id == treatmentid).update(copay = copay)    
    return dict()

def calculatecopay(db,tplanid,patientid):
    #copay = account.copayment(db,tplanid,patientid)
    totalcopay = 0
    trrows = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
    for tr in trrows:
        totalcopay = totalcopay + float(common.getvalue(tr.copay))
  
    
    db(db.treatmentplan.id == tplanid).update(totalcopay = totalcopay)
    return dict()

def calculatecost(tplanid):
    
    totalcost     = 0
    
    trrows = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
    for tr in trrows:
        totalcost = totalcost + float(common.getvalue(tr.treatmentcost))
        
        
    db(db.treatmentplan.id==tplanid).update(totaltreatmentcost = totalcost)
    
    return dict()

def calculateinspays(tplanid):
    
    totalinspays     = 0
    trrows = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
    for tr in trrows:
        totalinspays = totalinspays + float(common.getvalue(tr.inspay))
    db(db.treatmentplan.id==tplanid).update(totalinspays = totalinspays)
    
    return dict()


def updatetreatmentcostandcopay(treatmentid,tplanid):
    totalactualtreatmentcost = 0   #UCR Cost
    totaltreatmentcost = 0  #Cost charged to the client which is equal to UCR fee by default
    totalcopay = 0
    totalinspays = 0
    totalcompanypays = 0
    
    #strsql = "select sum(ucrfee) as totalactualtreatmentcost, sum(procedurefee) as totaltreatmentcost, sum(copay) as copay, sum(inspays) as inspays, sum(companypays) as companypays"
    #strsql = strsql + " from  vw_treatmentprocedure where treatmentid =" +  str(treatmentid) + " and is_active = 'T'  group by treatmentid "   
    #strsql = "select * from vw_treatmentprocedure where treatmentid = " + str(treatmentid)
    #ds = db.executesql(strsql)
    
    rows = db((db.vw_treatmentprocedure.treatmentid == treatmentid) & (db.vw_treatmentprocedure.is_active == True)).select(\
    
        db.vw_treatmentprocedure.ucrfee,
        db.vw_treatmentprocedure.procedurefee,
        db.vw_treatmentprocedure.copay,
        db.vw_treatmentprocedure.inspays,\
        db.vw_treatmentprocedure.companypays
    )
    
    for row in rows:
        totalactualtreatmentcost = totalactualtreatmentcost + float(common.getvalue(row.ucrfee)) if(len(rows) == 1) else 0
        totaltreatmentcost =totaltreatmentcost+ float(common.getvalue(row.procedurefee)) if(len(rows) == 1) else 0
        totalcopay = totalcopay + float(common.getvalue(row.copay)) if(len(rows) == 1) else 0
        totalinspays =totalinspays + float(common.getvalue(row.inspays)) if(len(rows) == 1) else 0
        totalcompanypays = totalcompanypays + float(common.getvalue(row.companypays)) if(len(rows) == 1) else 0  
        
    #totalactualtreatmentcost = float(common.getvalue(rows.response[0][0])) if(len(rows) == 1) else 0
    #totaltreatmentcost = float(common.getvalue(rows.response[0][1])) if(len(rows) == 1) else 0
    #totalcopay = float(common.getvalue(rows.response[0][2])) if(len(rows) == 1) else 0
    #totalinspays = float(common.getvalue(rows.response[0][3])) if(len(rows) == 1) else 0
    #totalcompanypays = float(common.getvalue(rows.response[0][4])) if(len(rows) == 1) else 0  
    
    
    
    db(db.treatment.id == treatmentid).update(actualtreatmentcost = totalactualtreatmentcost, treatmentcost=totaltreatmentcost, copay=totalcopay, inspay=totalinspays, companypay= totalcompanypays)
    
    #update treatmentplan assuming there is one treatment per tplan
    db(db.treatmentplan.id==tplanid).update(totaltreatmentcost = totaltreatmentcost, totalcopay=totalcopay,totalinspays=totalinspays)

    totaldue     = 0
    tp = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).select(db.treatmentplan.totaltreatmentcost,\
                                                                                            db.treatmentplan.totalpaid,\
                                                                                            db.treatmentplan.totalcopaypaid,\
                                                                                            db.treatmentplan.totalcompanypays,\
                                                                                            db.treatmentplan.totalinspaid)

    if(len(tp) == 1):
        totaldue = float(common.getvalue(tp[0].totaltreatmentcost)) - float(common.getvalue(tp[0].totalpaid)) - \
            float(common.getvalue(tp[0].totalcopaypaid)) - float(common.getvalue(tp[0].totalinspaid) - float(common.getvalue(tp[0].totalcompanypays)))


    db(db.treatmentplan.id==tplanid).update(totaldue=totaldue)

    
    db.commit()
    
    return dict()


def xupdatetreatmentcostandcopay(treatmentid,tplanid):
    totalactualtreatmentcost = 0   #UCR Cost
    totaltreatmentcost = 0  #Cost charged to the client which is equal to UCR fee by default
    totalcopay = 0
    totalinspays = 0
    totalcompanypays = 0
    
    rows = db((db.vw_treatmentprocedure.treatmentid == treatmentid) & (db.vw_treatmentprocedure.is_active == True)).select()
    for r in rows:
        totalactualtreatmentcost = totalactualtreatmentcost + float(common.getvalue(r.ucrfee))
        totaltreatmentcost = totaltreatmentcost + float(common.getvalue(r.procedurefee))
        totalcopay = totalcopay + float(common.getvalue(r.copay))
        totalinspays = totalinspays + float(common.getvalue(r.inspays)) 
        totalcompanypays = totalcompanypays + float(common.getvalue(r.companypays))     
    
    
    db(db.treatment.id == treatmentid).update(actualtreatmentcost = totalactualtreatmentcost, treatmentcost=totaltreatmentcost, copay=totalcopay, inspay=totalinspays, companypay= totalcompanypays)
    
    
    return dict()


def gettplans(db,providerid, memberid, tplan,member,fromdt,todt,status,limitby):
    
    dstplans = None
    
    query = (db.treatmentplan.is_active == True)
    
    if(providerid > 0):
        query = query & (db.treatmentplan.provider == providerid)
    if(memberid >0):
        query = query & (db.treatmentplan.primarypatient == memberid)
    
    
    if(common.getstring(tplan) != ""):
        query = query & (db.treatmentplan.treatmentplan.contains(tplan))
    if(common.getstring(member) != ""):
        query = query & (db.patientmember.patientmember.contains(member))
    if(common.getnulldt(fromdt) != ""):
        query = query & (db.treatmentplan.startdate >= fromdt)
    if(common.getnulldt(todt) != ""):
        query = query & (db.treatmentplan.startdate <= todt)
    if(common.getstring(status) != ""):
        query = query & (db.treatmentplan.status == status)
        
    dstplans = db(query).select(db.treatmentplan.id, db.treatmentplan.treatmentplan, db.treatmentplan.description, db.treatmentplan.startdate, db.treatmentplan.enddate,\
                                 db.treatmentplan.status,db.treatmentplan.totaltreatmentcost,db.treatmentplan.totalcopay,db.treatmentplan.provider,db.treatmentplan.primarypatient,\
                                 db.treatmentplan.is_active,db.treatmentplan.patient,db.treatmentplan.patienttype,db.treatmentplan.patientname,db.treatmentplan.totalinspays, \
                                 db.patientmember.patientmember,db.patientmember.id,db.patientmember.fname,db.patientmember.lname,\
                                 left=[db.patientmember.on(db.treatmentplan.primarypatient == db.patientmember.id )],\
                                 limitby=limitby,orderby=~db.treatmentplan.id
                                 )
    
    return dstplans

#treatment can be "" or treatment or treatment phrase
#this function will return a grid fulfilling the query
def gettreatmentgrid(page, imagepage, providerid, providername, treatment, memberid=0,patientid=0):
    
    clinicid = 0
    
    pattern = "%" + treatment + "%"
    
    
    
    #str1  = " memberid  = " + str(memberid) + " AND " if (memberid > 0) else ""
    #str2  = " patientid = " + str(patientid) + " AND " if (patientid > 0) else ""
    #str3  = "" if((treatment == None)|(treatment == "")) else " pattern LIKE '" + pattern + "' AND " 
    
    
    #strsql = "SELECT id from vw_treatmentlist where "
    #strsql = strsql + " providerid = " + str(providerid ) + " AND "
    #strsql = strsql + str1
    #strsql = strsql + str2
    #strsql = strsql + str3
    #strsql = strsql + "is_active = 'T'"
    
    #ds = db.executesql(strsql)
    
    #ids = []
    #i = 0
    #for d in ds:
        #ids.append(d[0])
    
    #query = (db.vw_treatmentlist.id.belongs(ids))
    
 
    
    
    query = (db.vw_treatmentlist.memberid == memberid) if(memberid > 0) else (1==1)
    
    query = query & (db.vw_treatmentlist.patientid == patientid) if(patientid > 0) else query

    query = query & (db.vw_treatmentlist.providerid == providerid) if(providerid > 0) else query

    query = query & (db.vw_treatmentlist.clinicid == clinicid) if(clinicid > 0) else query
    
    query = query & (db.vw_treatmentlist.is_active == True)
    
    query =  (query )
     
    if((pattern != "") & (pattern != None)):
        query = query & (db.vw_treatmentlist.pattern.like('%' + pattern + '%'))
        
    logger.loggerpms2.info("Grid QUey ==>>" + pattern + "\n" + str(query))
    
    fields=(db.vw_treatmentlist.patientname,db.vw_treatmentlist.treatment,db.vw_treatmentlist.chiefcomplaint,db.vw_treatmentlist.startdate,db.vw_treatmentlist.dentalprocedure, db.vw_treatmentlist.shortdescription, db.vw_treatmentlist.memberid,
            db.vw_treatmentlist.treatmentplan,db.vw_treatmentlist.status,db.vw_treatmentlist.treatmentcost,db.vw_treatmentlist.memberid,db.vw_treatmentlist.patientid,db.vw_treatmentlist.tplanid,db.vw_treatmentlist.clinicname)

    #'vw_treatmentlist.clinicname':'Clinic',

    headers={
        'vw_treatmentlist.treatment':'Treatment No.',
        'vw_treatmentlist.chiefcomplaint':'Complaint',
        'vw_treatmentlist.patientname':'Patient',
        'vw_treatmentlist.startdate':'Treatment Date',
        'vw_treatmentlist.treatmentcost':'Cost',
                }

    db.vw_treatmentlist.status.readable = False
    db.vw_treatmentlist.treatmentplan.readable = False
    
    db.vw_treatmentlist.memberid.readable = False
    db.vw_treatmentlist.patientid.readable = False
    db.vw_treatmentlist.providerid.readable = False
    db.vw_treatmentlist.is_active.readable = False
    db.vw_treatmentlist.providerid.readable = False

    db.vw_treatmentlist.treatmentcost.readable = False
    db.vw_treatmentlist.tplanid.readable = False
    db.vw_treatmentlist.memberid.readable = False
    
    db.vw_treatmentlist.dentalprocedure.readable = False
    db.vw_treatmentlist.shortdescription.readable = False
    
    db.vw_treatmentlist.clinicname.readable = False
    
    links = [\
           dict(header=CENTER("Open"), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("treatment","update_treatment",vars=dict(page=page,imagepage=imagepage,treatmentid=row.id, providerid=providerid))))),
           #dict(header=CENTER('New'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/png/014-dentist.png",_width=30, _height=30),_href=URL("treatment","new_treatment",vars=dict(page=page,treatmentid=row.id, memberid=row.memberid,patientid=row.patientid, providerid=providerid))))),\
           dict(header=CENTER('Payment'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/payments.png",_width=30, _height=30),_href=URL("payment","create_payment",vars=dict(page=page,tplanid=row.tplanid,treatmentid=row.id, providerid=providerid,providername=providername,memberid=row.memberid,patientid=row.patientid))))),\
           dict(header=CENTER('Auth.Rpt.'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/reports.png",_width=30, _height=30),_href=URL("reports","treatmentreport",vars=dict(page=page,treatmentid=row.id,providerid=providerid))))),
           dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),_href=URL("treatment","delete_treatment",vars=dict(page=page,treatmentid=row.id,  memberid=row.memberid,patientid=row.patientid, providerid=providerid,providername=providername)))))
    ]

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
    returnurl =  URL('treatment', 'list_treatments', vars=dict(page=page,providerid=providerid))
     
    orderby = ~db.vw_treatmentlist.id
    
    maxtextlengths = {'vw_treatmentlist.treatment':50}
       
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
                        user_signature=True
                       )
    
    
    
    return form



def gettreatments(db,tplanid, treatment,tplan,member,fromdt,todt,status,limitby):
    
    dstplans = None
    
    query = ((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True))
    
    if(common.getstring(treatment) != ""):
        query = query & (db.treatment.treatment.contains(treatment))
    if(common.getstring(tplan) != ""):
        query = query & (db.treatmentplan.treatmentplan.contains(tplan))
    if(common.getstring(member) != ""):
        query = query & (db.patientmember.patientmember.contains(member))
    if(common.getnulldt(fromdt) != ""):
        query = query & (db.treatment.startdate >= fromdt)
    if(common.getnulldt(todt) != ""):
        query = query & (db.treatment.startdate <= todt)
    if(common.getstring(status) != ""):
        query = query & (db.treatment.status == status)
            
    dstreatments = db(query).select(db.treatment.id, db.treatment.treatment, db.treatment.description, db.treatment.startdate, db.treatment.enddate,\
                                 db.treatment.status,db.treatment.treatmentcost,db.treatment.copay,db.treatment.inspay,db.treatment.quadrant,db.treatment.tooth,db.treatment.is_active,\
                                 db.dentalprocedure.dentalprocedure, db.treatmentplan.id, db.treatmentplan.treatmentplan,db.treatmentplan.primarypatient,\
                                 db.treatmentplan.patient,db.treatmentplan.patienttype,db.treatmentplan.patientname, \
                                 db.patientmember.patientmember,db.patientmember.id,db.patientmember.fname,db.patientmember.lname,\
                                 left=[db.treatmentplan.on(db.treatmentplan.id == db.treatment.treatmentplan ),\
                                       db.patientmember.on(db.treatmentplan.primarypatient == db.patientmember.id ),\
                                       db.dentalprocedure.on(db.dentalprocedure.id == db.treatment.dentalprocedure)],\
                                 limitby=limitby,orderby=~db.treatment.id
                                 )
    
    return dstreatments

def getproceduregrid(providerid,tplanid,treatmentid,memberid,patientid,authorization,authorized,preauthorized,page,hmopatientmember,writablflag,webadmin):
    
    # procedures grid
    db.vw_treatmentprocedure.relgrtransactionid.readable = False
    if(session.religare != None):
        db.vw_treatmentprocedure.relgrprocdesc.readable = session.religare
    else:
        db.vw_treatmentprocedure.relgrprocdesc.readable = False
        
    query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True))
    
    if((hmopatientmember == True) | (session.religare == True)):
        fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription, db.vw_treatmentprocedure.relgrprocdesc, \
                   db.vw_treatmentprocedure.tooth,db.vw_treatmentprocedure.quadrant,
                   db.vw_treatmentprocedure.procedurefee,db.vw_treatmentprocedure.inspays,db.vw_treatmentprocedure.copay,db.vw_treatmentprocedure.status,\
                   db.vw_treatmentprocedure.treatmentdate, db.vw_treatmentprocedure.relgrproc,db.vw_treatmentprocedure.relgrtransactionid)

        
        headers={
            'vw_treatmentprocedure.procedurecode':'Code',
            'vw_treatmentprocedure.altshortdescription':'Description',
            'vw_treatmentprocedure.relgrprocdesc':'Religare Procedure'  if(session.religare != None) else '',
            'vw_treatmentprocedure.tooth':'Tooth',
            'vw_treatmentprocedure.quadrant':'Quadrant',
            'vw_treatmentprocedure.procedurefee':'Procedure Cost',
            'vw_treatmentprocedure.inspays':'Insurance Pays',
            'vw_treatmentprocedure.copay':'Patient Pays',
            'vw_treatmentprocedure.status':'Status',
            'vw_treatmentprocedure.treatmentdate':'Treatment Date'
        }
        
    else:
        fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription, db.vw_treatmentprocedure.relgrprocdesc,\
                   db.vw_treatmentprocedure.tooth,db.vw_treatmentprocedure.quadrant,
                   db.vw_treatmentprocedure.procedurefee,db.vw_treatmentprocedure.status,\
                   db.vw_treatmentprocedure.treatmentdate,db.vw_treatmentprocedure.relgrproc,db.vw_treatmentprocedure.relgrtransactionid)
        
        headers={
            'vw_treatmentprocedure.procedurecode':'Code',
            'vw_treatmentprocedure.altshortdescription':'Description',
            'vw_treatmentprocedure.relgrprocdesc':'',
            'vw_treatmentprocedure.tooth':'Tooth',
            'vw_treatmentprocedure.quadrant':'Quadrant',
            'vw_treatmentprocedure.procedurefee':'Procedure Cost',
            'vw_treatmentprocedure.status':'Status',
            'vw_treatmentprocedure.treatmentdate':'Treatment Date'
        }
        
      
        
    if(writablflag):
        links = [\
                dict(header=CENTER('Edit'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=30, _height=30),\
                                                                   _href=URL("treatment","update_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin,hmopatientmember=hmopatientmember))))),
                
                dict(header=CENTER('Complete'),body=lambda row: ((CENTER(A(IMG(_src="/my_pms2/static/img/complete_on.png",_width=30, _height=30),\
                                                                      _href=URL("treatment","complete_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin))))\
                                                                if(row.status == 'Started') else\
                                                                CENTER(A(IMG(_src="/my_pms2/static/img/complete_off.png",_width=30, _height=30),\
        _href=URL("treatment","complete_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,\
                                                             memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,\
                                                             webadmin=webadmin))))))\
                                                                
                             if((row.relgrproc == False) | (row.relgrtransactionid == None)) else\
                             
                             ((CENTER(A(IMG(_src="/my_pms2/static/img/religare_on.png",_width=30, _height=30),\
                _href=URL("religare","settle_transaction",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,\
                                                                    patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,\
                                                                    authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin))))\
                             if(row.status == 'Started') else\
                             CENTER(A(IMG(_src="/my_pms2/static/img/religare_off.png",_width=30, _height=30)))))\
                             
                     ),
                
                dict(header=CENTER('Delete'),body=lambda row: ((CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),\
                                                                      _href=URL("treatment","delete_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin))))))\
                                                                
                             if(row.relgrproc == False) | (row.relgrtransactionid == None) else\
                                     
                                    ((CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),\
                                               _href=URL("religare","void_transaction",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin))))))

                                    if(row.status == 'Started') else\
                                    ((CENTER(A(IMG(_src="/my_pms2/static/img/delete_off.png",_width=30, _height=30)))))
                                    
                             
                     )
        ]
    else:
        links = [\
                dict(header=CENTER('Edit'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=30, _height=30),\
                                                                   _href=URL("treatment","update_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin,hmopatientmember=hmopatientmember))))),
                
                
                dict(header=CENTER('Complete'),body=lambda row: ((CENTER(A(IMG(_src="/my_pms2/static/img/complete_on.png",_width=30, _height=30),\
                                                                                      _href=URL("treatment","complete_procedure",vars=dict(status=row.status,page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin))))\
                                                                                if(row.status == 'Started') else\
                                                                                CENTER(A(IMG(_src="/my_pms2/static/img/complete_off.png",_width=30, _height=30)\
                                                                                                                                                )))))\
                
                
                
                
        ]
    
    
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
                        links=links,
                        paginate=10,
                        maxtextlengths=maxtextlengths,
                        orderby=None,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )      

    
    return formProcedure

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def settle_procedure():
    
    return dict()

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def complete_procedure():
    treatmentprocedureid = int(common.getid(request.vars.treatmentprocedureid))
    page = int(common.getpage(request.vars.page))
    #memberid = int(common.getid(request.vars.memberid))
    #patientid = int(common.getid(request.vars.patientid))
    treatmentid = int(common.getid(request.vars.treatmentid))
    #tplanid = int(common.getid(request.vars.tplanid))
    providerid = int(common.getid(request.vars.providerid))
    #provdict = common.getproviderfromid(db,providerid)
    #providername = provdict["providername"]
    

        
    returnurl = URL('treatment', 'update_treatment', vars=dict(page=page,providerid=providerid,treatmentid=treatmentid))  

    r = db(db.vw_treatmentprocedure.id == treatmentprocedureid).select(db.vw_treatmentprocedure.relgrproc)
    religare = False if(len(r) <= 0) else common.getboolean(r[0].relgrproc)
        
    if(not religare):
        db(db.treatment_procedure.id == treatmentprocedureid).update(status = 'Completed')
    else:
        oreligare = mdpreligare.Religare(db,providerid)
        jsonrsp = oreligare.settleTransaction(treatmentprocedureid)    
        if(jsonrsp["result"] == "success"):
            db(db.treatment_procedure.id == treatmentprocedureid).update(status = 'Completed')
            
  
    redirect(returnurl)
    return True


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def void_procedure():
    
    
    return dict()


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def delete_procedure():
    treatmentprocedureid = int(common.getid(request.vars.treatmentprocedureid))
    page = int(common.getpage(request.vars.page))
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    treatmentid = int(common.getid(request.vars.treatmentid))
    tplanid = int(common.getid(request.vars.tplanid))
    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getproviderfromid(db,providerid)
    providername = provdict["providername"]
    
    treatment = ""
    r = db(db.treatment.id == treatmentid).select()
    if(len(r)>0):
        treatment = r[0].treatment
        
    returnurl = URL('treatment', 'update_treatment', vars=dict(page=page,providerid=providerid,treatmentid=treatmentid))  

    form = FORM.confirm('Yes',{'No': returnurl})
    
    if form.accepted:
        
        db(db.treatment_procedure.id == treatmentprocedureid).update(is_active = False)
        #calcualte all the costs and update tplan, treatment, treatmentnotes (prescription)
        updatetreatmentcostandcopay(treatmentid, tplanid)
     
        redirect(returnurl)
    
    return dict(form=form,returnurl=returnurl,providerid=providerid,providername=providername,page=page,patientid=patientid,memberid=memberid,treatmentid=treatmentid,tplanid=tplanid,treatment=treatment)



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def delete_treatment():
    
    page = int(common.getpage(request.vars.page))
    providerid = int(common.getid(request.vars.providerid))
    providername = common.getstring(request.vars.providername)
    treatmentid = int(common.getid(request.vars.treatmentid))
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    treatment = ""
    tplanid = 0
    
    r = db(db.treatment.id == treatmentid).select(db.treatment.treatmentplan, db.treatment.treatment)
    if(len(r)>0):
        tplanid = int(common.getid(r[0].treatmentplan))
        treatment = common.getstring(r[0].treatment)
    
    if(memberid > 0):
        returnurl = URL('treatment', 'list_treatments', vars=dict(page=page,providerid=providerid,memberid=memberid,patientid=patientid))  
    else:
        returnurl = URL('treatment', 'list_treatments', vars=dict(page=page,providerid=providerid))  
    
    form = FORM.confirm('Yes',{'No': returnurl})
    
    if form.accepted:
        db(db.treatment.id == treatmentid).update(is_active = False)
        db(db.treatment_procedure.treatmentid == treatmentid).update(is_active = False)
        db(db.treatmentplan.id == tplanid).update(is_active = False)
        deltplan_patient(tplanid)
        
        #calcualte all the costs and update tplan, treatment, treatmentnotes (prescription)
        updatetreatmentcostandcopay(treatmentid,tplanid)
        #calculatecost(tplanid)
        #calculatecopay(db, tplanid,memberid)
        #calculateinspays(tplanid) 
        #calculatedue(tplanid)    
        
        common.dashboard(db,session,providerid)
        redirect(returnurl)
      
    return dict(form=form, page=page, returnurl=returnurl, providerid=providerid, providername=providername,   treatment = treatment)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_treatments():
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])
    clinicid = 0 #session.clinicid
    
    page     = common.getgridpage(request.vars)
    page     = 1 if(page == 0) else page
    imagepage = 0
    
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    treatment = common.getstring(request.vars.treatment)
    
    returnurl = URL('admin', 'providerhome')  
    pat1 = ""   # fn ln
    xpat1 = ""  # fn ln:patientmemebr
    r = None
    r = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.primarypatientid == memberid) &\
        (db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.is_active == True)).select()
    
    if(len(r)>0):
        pat1 = common.getstring(r[0].fullname).strip()
        xpat1 = common.getstring(r[0].patient)
        treatment = pat1
        
    form = SQLFORM.factory(
                 Field('pattreatment1', 'string',  default=pat1, label='Patient',requires=IS_NOT_EMPTY()),
                 Field('xpattreatment1', 'string', default=xpat1, label='XPatient'),
                 Field('xaction','string', label='', default='X')
                 
      )
         
    xtreatment = form.element('#no_table_pattreatment1')
    xtreatment['_class'] = 'form-control'
    xtreatment['_placeholder'] = 'Enter First Name Last Name or Treatment'
    xtreatment['_autocomplete'] = 'off'     
    
    logger.loggerpms2.info("Enter gettreatmentgrid ==>>" + str(providerid) + " " + str(providername) + " " + str(pat1) + " " + str(memberid) + " " + str(patientid))
   
    formA = gettreatmentgrid(page,imagepage,providerid, providername, treatment, memberid,patientid)    
    logger.loggerpms2.info("Exte gettreatmentgrid ==>>")
    if form.accepts(request,session,keepvalues=True):
        xaction = form.vars.xaction

        if(xaction == "newTreatment"):
            redirect(URL('treatment','new_treatment',vars=dict(page=1,providerid=providerid,memberid=memberid,patientid=patientid,treatmentid=0,tplanid=0)))            
        else:
            
            if(form.vars.pattreatment1 == ""):
                form.vars.xpattreatment1 = ""
            
            if(form.vars.xpattreatment1 == ""):
                form.vars.xpattreatment1 = form.vars.pattreatment1
                
            #xpattreatments can be <fn> <ln>:<treatment>, <fn ln>:membercode
            #or patientname <fn ln>  or <trno> or <phrase> or <balnk>
            
            #matching <fn ln>:<treatment> or <fn ln>:<member code> or <fn ln>
            xphrase = common.getstring(form.vars.xpattreatment1).strip()
            
            strarr = xphrase.split(":") if(xphrase.split(":") >= 0) else ""
            xphrase = common.getstring(strarr[0]) if(len(strarr) >=1) else xphrase
            
            
            if(clinicid == 0):
                r = db((db.vw_treatmentlist.pattreatment.like("%" + xphrase.strip() + "%")) & \
                                         (db.vw_treatmentlist.providerid == providerid) & \
                                         (db.vw_treatmentlist.is_active == True)).select()     
            else:
                r = db((db.vw_treatmentlist.pattreatment.like("%" + xphrase.strip() + "%")) & \
                                                     (db.vw_treatmentlist.providerid == providerid) & \
                                                     (db.vw_treatmentlist.clinicid == clinicid) & \
                                                     (db.vw_treatmentlist.is_active == True)).select()            
                                            
            
            if(len(r)>=1):
                treatment = "" if(len(r) > 1) else common.getstring(r[0].treatment)    
                treatmentid = 0 if(len(r) > 1) else int(common.getid(r[0].id))
                tplanid = 0 if(len(r) > 1) else int(common.getid(r[0].tplanid))
                patientid = int(common.getstring(r[0].patientid))
                memberid = int(common.getstring(r[0].memberid))
                if(xaction == "listTreatments"):
                    formA = gettreatmentgrid(page,imagepage,providerid, providername, treatment,memberid,patientid)
                elif(xaction == "newTreatment"):
                    redirect(URL('treatment','new_treatment',vars=dict(page=1,providerid=providerid,memberid=memberid,patientid=patientid,treatmentid=0,tplanid=0)))            
            else:
                #match for patientname
                r = db((db.vw_memberpatientlist.fullname.like("%" + xphrase.strip() + "%"))& \
                                              (db.vw_memberpatientlist.providerid == providerid) & \
                                              (db.vw_memberpatientlist.is_active == True)).select()              
                if(len(r)>=1):
                    treatment = ""
                    treatmentid = 0
                    tplanid = 0
                    patientid = int(common.getstring(r[0].patientid))
                    memberid  = int(common.getstring(r[0].primarypatientid))
                    if(xaction == "listTreatments"):
                        formA = gettreatmentgrid(page,imagepage,providerid, providername, treatment,memberid,patientid)
                    elif(xaction == "newTreatment"):
                        redirect(URL('treatment','new_treatment',vars=dict(page=1,providerid=providerid,memberid=memberid,patientid=patientid,treatmentid=0,tplanid=0)))            
                    
                else:        
                    treatment = xphrase
                    treatmentid = 0
                    tplanid = 0
                    patientid = 0
                    memberid = 0
                    formA = gettreatmentgrid(page,imagepage,providerid, providername, treatment,memberid,patientid)               
        
                
            
    return dict(form=form, formA=formA, page=page,imagepage=imagepage,\
                   returnurl=returnurl,providername=providername, \
                   providerid=providerid,memberid=memberid,patientid=patientid \
                   )    
          
    
    


#@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
#@auth.requires_login()
#def xlist_treatments():

    
    #page     = common.getgridpage(request.vars)
    #memberid = int(common.getid(request.vars.memberid))
    #patientid = int(common.getid(request.vars.patientid))
    #providerid = int(common.getid(request.vars.providerid))
    #providerdict = common.getproviderfromid(db,providerid)
    #providername = providerdict["providername"]
    #imagepage = 0

    
    #if(patientid == 0):
        #query = ((db.vw_treatmentlist.providerid == providerid) & (db.vw_treatmentlist.is_active == True))
        #returnurl = URL('treatment', 'list_treatments', vars=dict(page=page,imagepage=imagepage,providerid=providerid))  
    #else:
        #query = ((db.vw_treatmentlist.providerid == providerid) & (db.vw_treatmentlist.patientid == patientid) & (db.vw_treatmentlist.is_active == True))
        #returnurl = URL('treatment', 'list_treatments', vars=dict(page=page,imagepage=imagepage,providerid=providerid,memberid=memberid,patientid=patientid))  
    
    #fields=(db.vw_treatmentlist.patientname,db.vw_treatmentlist.treatment,db.vw_treatmentlist.chiefcomplaint,db.vw_treatmentlist.startdate,db.vw_treatmentlist.dentalprocedure, db.vw_treatmentlist.shortdescription, db.vw_treatmentlist.memberid,
            #db.vw_treatmentlist.treatmentplan,db.vw_treatmentlist.status,db.vw_treatmentlist.treatmentcost,db.vw_treatmentlist.memberid,db.vw_treatmentlist.patientid,db.vw_treatmentlist.tplanid)

    #headers={
        #'vw_treatmentlist.treatment':'Treatment No.',
        #'vw_treatmentlist.chiefcomplaint':'Complaint',
        #'vw_treatmentlist.patientname':'Patient',
        #'vw_treatmentlist.startdate':'Treatment Date',
        #'vw_treatmentlist.treatmentcost':'Cost',
                #}

    #db.vw_treatmentlist.status.readable = False
    #db.vw_treatmentlist.treatmentplan.readable = False
    
    #db.vw_treatmentlist.memberid.readable = False
    #db.vw_treatmentlist.patientid.readable = False
    #db.vw_treatmentlist.providerid.readable = False
    #db.vw_treatmentlist.is_active.readable = False
    #db.vw_treatmentlist.providerid.readable = False

    #db.vw_treatmentlist.treatmentcost.readable = False
    #db.vw_treatmentlist.tplanid.readable = False
    #db.vw_treatmentlist.memberid.readable = False
    
    #db.vw_treatmentlist.dentalprocedure.readable = False
    #db.vw_treatmentlist.shortdescription.readable = False
    
    
    #links = [\
           #dict(header=CENTER("Open"), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),_href=URL("treatment","update_treatment",vars=dict(page=page,imagepage=imagepage,treatmentid=row.id, providerid=providerid))))),
           ##dict(header=CENTER('New'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/png/014-dentist.png",_width=30, _height=30),_href=URL("treatment","new_treatment",vars=dict(page=page,treatmentid=row.id, memberid=row.memberid,patientid=row.patientid, providerid=providerid))))),\
           #dict(header=CENTER('Payment'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/payments.png",_width=30, _height=30),_href=URL("payment","create_payment",vars=dict(page=page,tplanid=row.tplanid,providerid=providerid,providername=providername,memberid=row.memberid,patientid=row.patientid))))),\
           #dict(header=CENTER('Auth.Rpt.'), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/reports.png",_width=30, _height=30),_href=URL("reports","treatmentreport",vars=dict(page=page,treatmentid=row.id,providerid=providerid))))),
           #dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),_href=URL("treatment","delete_treatment",vars=dict(page=page,treatmentid=row.id,  memberid=row.memberid,patientid=row.patientid, providerid=providerid,providername=providername)))))
    #]

    #exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
    #returnurl =  URL('treatment', 'list_treatments', vars=dict(page=page,providerid=providerid))
     
    #orderby = ~db.vw_treatmentlist.id
    
    #maxtextlengths = {'vw_treatmentlist.treatment':50}
       
    #form = SQLFORM.grid(query=query,
                        #headers=headers,
                        #fields=fields,
                        #links=links,
                        #paginate=10,
                        #orderby=orderby,
                        #maxtextlengths=maxtextlengths,
                        #exportclasses=exportlist,
                        #links_in_grid=True,
                        #searchable=True,
                        #create=False,
                        #deletable=False,
                        #editable=False,
                        #details=False,
                        #user_signature=True
                       #)

    #xsearch = form.element('input',_value='Search')
    #xsearch['_class'] = 'form_details_button btn'
    #xclear = form.element('input',_value='Clear')
    #xclear['_class'] = 'form_details_button btn'
    #xnew = form.element('input',_value='New Search')
    #xnew['_class'] = 'form_details_button_black btn'
    #xand = form.element('input',_value='+ And')
    #xand['_class'] = 'form_details_button_black btn'
    #xor = form.element('input',_value='+ Or')
    #xor['_class'] = 'form_details_button_black btn'
    #xclose = form.element('input',_value='Close')
    #xclose['_class'] = 'form_details_button_black btn'

  
    #return dict(form = form, returnurl=returnurl,page=page,providerid=providerid,providername=providername,memberid=memberid,patientid=patientid)




@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_treatmentplans():

    provdict = common.getprovider(auth, db)
    providerid = provdict["providerid"]
    providername = provdict["providername"]
    page     = common.getgridpage(request.vars)
    memberid   = int(common.getid(request.vars.memberid))

    membername = ""
    
    
    if(memberid == 0):
        query = ((db.vw_treatmentplanlist.provider == providerid) & (db.vw_treatmentplanlist.is_active == True))
    else:
        query = ((db.vw_treatmentplanlist.provider == providerid) & (db.vw_treatmentplanlist.primarypatient == memberid) & (db.vw_treatmentplanlist.is_active == True))
        patients = db(db.patientmember.id == memberid).select()
        membername = patients[0].fname + ' ' + patients[0].lname + ' (' + patients[0].patientmember + ')'

        
    left = None
    
    
    fields=(db.vw_treatmentplanlist.fname,db.vw_treatmentplanlist.lname,db.vw_treatmentplanlist.patientmember,db.vw_treatmentplanlist.patientname, db.vw_treatmentplanlist.primarypatient,\
            db.vw_treatmentplanlist.treatmentplan,db.vw_treatmentplanlist.startdate,db.vw_treatmentplanlist.status,db.vw_treatmentplanlist.totaltreatmentcost,db.vw_treatmentplanlist.totaldue)

                   
    headers={
    
        'vw_treatmentplanlist.treatmentplan':'Treatment',
        'vw_treatmentplanlist.patientname':'Patient',
        'vw_treatmentplanlist.startdate':'Date',
        'vw_treatmentplanlist.totaltreatmentcost':'Total Cost',
        'vw_treatmentplanlist.totaldue':'Total Due',
    }
               

    #links = [dict(header='Edit', body=lambda row: A(IMG(_src="../static/assets/global/img/png/017-loupe.png",_width=25, _height=25),_href=URL("treatment","treatmentplan_update",vars=dict(page=page,tplanid=row.treatmentplan.id,memberid=row.treatmentplan.primarypatient, providerid=providerid,providername=providername)))),\
             #dict(header='Treatments', body=lambda row: A(IMG(_src="../static/assets/global/img/png/014-dentist.png",_width=30, _height=30),_href=URL("treatment","list_treatments",vars=dict(page=page,tplanid=row.treatmentplan.id,memberid=row.treatmentplan.primarypatient, providerid=providerid,providername=providername)))),\
             #dict(header='Payment', body=lambda row: A(IMG(_src="../static/assets/global/img/png/010-cash.png",_width=30, _height=30),_href=URL("payment","list_payment",vars=dict(page=page,tplanid=row.treatmentplan.id,providerid=providerid,providername=providername)))),\
             #dict(header='Reports', body=lambda row: A(IMG(_src="../static/assets/global/img/png/012-note-on-a-clipboard.png",_width=30, _height=30),_href=URL("reports","list_payment",vars=dict(page=page,tplanid=row.treatmentplan.id, providerid=providerid,providername=providername))))
             #]

    links = [dict(header='Edit', body=lambda row: A(IMG(_src="/my_pms2/static/img/png/017-loupe.png",_width=25, _height=25),_href=URL("treatment","treatmentplan_update",vars=dict(page=page,tplanid=row.id,memberid=row.primarypatient, providerid=providerid,providername=providername)))),\
             dict(header='Procedures', body=lambda row: A(IMG(_src="/my_pms2/static/img/png/014-dentist.png",_width=30, _height=30),_href=URL("treatment","list_treatments",vars=dict(page=page,tplanid=row.id,memberid=row.primarypatient, providerid=providerid,providername=providername)))),\
             dict(header='Payment', body=lambda row: A(IMG(_src="/my_pms2/static/img/png/010-cash.png",_width=30, _height=30),_href=URL("payment","list_payment",vars=dict(page=page,tplanid=row.id,providerid=providerid,providername=providername)))),\
             dict(header='Reports', body=lambda row: A(IMG(_src="/my_pms2/static/img/png/012-note-on-a-clipboard.png",_width=30, _height=30),_href=URL("reports","list_payment",vars=dict(page=page,tplanid=row.id, providerid=providerid,providername=providername))))
             ]



    

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
    db.vw_treatmentplanlist.status.readable = False
    db.vw_treatmentplanlist.is_active.readable = False
    db.vw_treatmentplanlist.provider.readable = False
    db.vw_treatmentplanlist.primarypatient.readable = False
    db.vw_treatmentplanlist.id.readable = False
    db.vw_treatmentplanlist.patientmember.readable = False    
    db.vw_treatmentplanlist.fname.readable = False    
    db.vw_treatmentplanlist.lname.readable = False    
    
 
    if(session.nonmemberscount == True):
        returnurl =  URL('member', 'list_nonmembers', vars=dict(page=page,providerid=providerid,providername=providername))
    else:
        returnurl =  URL('member', 'list_members', vars=dict(page=page,providerid=providerid,providername=providername))
    
    orderby = ~db.vw_treatmentplanlist.startdate

    form = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        left=left,
                        paginate=5,
                        orderby =orderby,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )

   
        
    return dict(form = form, returnurl=returnurl,page=page,memberid=memberid,providerid=providerid,providername=providername,membername = membername)
        



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def treatmentplan_update():
    
    page       = int(common.getpage(request.vars['page']))
    memberid   = int(common.getstring(request.vars.memberid))
    tplanid    = int(common.getstring(request.vars.tplanid))
    providerid   =   int(common.getnegid(request.vars['providerid']))
    providername =   common.getstring(request.vars['providername'])                     
    
    calculatecost(tplanid)
    calculatecopay(db, tplanid,memberid)
    calculateinspays(tplanid)
    addtplan_patient(tplanid,memberid)     
    db.commit()
    
    returnurl = URL('treatment','list_treatmentplans',vars=dict(page=page,memberid=memberid,providerid=providerid,providername=providername))
    
    sqlqry = None
    pps = None
    if(memberid == 0):
        sqlquery = db(((db.patientmember.provider == providerid)&\
                 (db.patientmember.is_active == True)))
        sqlquery1 = db(db.patientmember.id ==0)
        pps = db(((db.patientmember.provider == providerid)&\
                 (db.patientmember.is_active == True))).select()
        
    else:
        sqlquery = db((db.patientmember.provider == providerid)&\
                 (db.patientmember.id == memberid))
        pps = db((db.patientmember.provider == providerid)&\
                 (db.patientmember.id == memberid)).select()
        
    
    
    query = ((db.treatmentplan.id == tplanid)&(db.treatmentplan.is_active == True))
    dstplans = db(query).select(db.treatmentplan.id, db.treatmentplan.treatmentplan, db.treatmentplan.description, db.treatmentplan.startdate, db.treatmentplan.enddate,\
                                 db.treatmentplan.status,db.treatmentplan.totaltreatmentcost,db.treatmentplan.totalcopay,db.treatmentplan.provider,db.treatmentplan.primarypatient,\
                                 db.treatmentplan.is_active,db.treatmentplan.patient,db.treatmentplan.patienttype,db.treatmentplan.patientname,db.treatmentplan.totalinspays, \
                                 db.patientmember.patientmember,db.patientmember.id,db.patientmember.fname,db.patientmember.lname,\
                                 left=[db.patientmember.on(db.treatmentplan.primarypatient == db.patientmember.id )],orderby=~db.treatmentplan.id
                                 )
    
    
    formA = SQLFORM.factory(
                   Field('treatmentplan','string',label='Treatment Plan ID', default=dstplans[0].treatmentplan.treatmentplan),
                   Field('description','text', label='Description', default=dstplans[0].treatmentplan.description),
                   Field('startdate', 'date', label='From Date',  default=dstplans[0].treatmentplan.startdate,requires=IS_EMPTY_OR(IS_DATE(format=('%Y-%m-%d')))),
                   Field('enddate', 'date', label='To Date', default=dstplans[0].treatmentplan.enddate,requires=IS_EMPTY_OR(IS_DATE(format=('%Y-%m-%d')))),
                   Field('status', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),label='Status',default=dstplans[0].treatmentplan.status, requires = IS_IN_SET(status.TREATMENTPLANSTATUS)),  
                   Field('totaltreatmentcost', 'double', label='Total Treament Cost',default=dstplans[0].treatmentplan.totaltreatmentcost),  
                   Field('totalcopay', 'double', label='Total Copay',default=dstplans[0].treatmentplan.totalcopay),  
                   Field('totalinspays', 'double', label='Total Ins. Pays',default=dstplans[0].treatmentplan.totalinspays),  
                   Field('provider', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'), default=dstplans[0].treatmentplan.provider, label='Provider',requires=IS_IN_DB(db(db.provider.id==providerid), 'provider.id', '%(providername)s')),
                   Field('primarypatient', label='Primary Patient', default=dstplans[0].treatmentplan.primarypatient),
                   Field('patient','string', label='Patient',default=dstplans[0].treatmentplan.patient),
                   Field('patienttype','string',default=dstplans[0].treatmentplan.patienttype, label='Patient Type'),
                   Field('patientname','string',default=dstplans[0].treatmentplan.patientname, label='Patient Name')
                   )    
    #Field('primarypatient', default=dstplans[0].treatmentplan.primarypatient,label='Primary Patient', requires=IS_IN_DB(db(db.patientmember.id==memberid), 'patientmember.id', '%(fname)s %(lname)s')),
    #Field('patient','string',default=dstplans[0].treatmentplan.patient, label='Patient',requires=IS_IN_DB(db(db.vw_primarypatientlist.id==memberid), 'vw_primarypatientlist.id', '%(fname)s  %(lname)s')),
    
    formA.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=description]')['_rows'] = 5
    
    xtreatmentplan = formA.element('input',_id='no_table_treatmentplan')
    xtreatmentplan['_class'] =  'w3-input w3-border '
    
    xstartdate = formA.element('input',_id='no_table_startdate')
    xstartdate['_class'] =  'w3-input w3-border  date'

    xenddate = formA.element('input',_id='no_table_enddate')
    xenddate['_class'] =  'w3-input w3-border  date'
    
    xtotaltreatmentcost = formA.element('input',_id='no_table_totaltreatmentcost')
    xtotaltreatmentcost['_class'] =  'w3-input w3-border'

    xtotalcopay = formA.element('input',_id='no_table_totalcopay')
    xtotalcopay['_class'] =  'w3-input w3-border '

    xtotalinspays = formA.element('input',_id='no_table_totalinspays')
    xtotalinspays['_class'] =  'w3-input w3-border '
    
   
    
    
    

    if formA.accepts(request,session,keepvalues=True):
        
        rec = db(db.treatmentplan.id == tplanid).update(**db.treatmentplan._filter_fields(formA.vars))
        if(formA.vars.patientname == ""):
            rows = db(db.vw_treatmentplanlist.id == tplanid).select()
            patientname = rows[0].fname + '  ' + rows[0].lname
            tplanid = db(db.treatmentplan.id == tplanid).update(patientname = patientname)
        
        redirect(returnurl)
    else:
        response.flash = 'Treatment Plan update form has errors'    
        
    returnurl = URL('treatment','list_treatmentplans',vars=dict(page=page,memberid=memberid,providerid=providerid,providername=providername))
    return dict(formA=formA,providername=providername,providerid=providerid,page=page,returnurl=returnurl,memberid=memberid,pps=pps)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def treatmentplan_create():

    page       = int(common.getpage(request.vars['page']))
    memberid   = int(common.getstring(request.vars.memberid))
    providerid   =   int(common.getnegid(request.vars['providerid']))
    providername =   common.getstring(request.vars['providername'])                     

    returnurl = URL('treatment','list_treatmentplans',vars=dict(page=page,memberid=memberid,providerid=providerid,providername=providername))
    sqlqry = None
    
    if(memberid == 0):
        sqlquery = db(((db.patientmember.provider == providerid)&\
                 (db.patientmember.is_active == True)))
        sqlquery1 = db(db.patientmember.id ==0)
        pps = db(((db.patientmember.provider == providerid)&\
                 (db.patientmember.is_active == True))).select()
        
    else:
        sqlquery = db((db.patientmember.provider == providerid)&\
                 (db.patientmember.id == memberid))
        pps = db((db.patientmember.provider == providerid)&\
                 (db.patientmember.id == memberid)).select()
        
        
    formA = SQLFORM.factory(
                   Field('treatmentplan','string',label='Treatment Plan ID', default='', requires=[IS_NOT_EMPTY()]),
                   Field('description','text', label='Description', default=''),
                   Field('startdate', 'date', label='From Date', default=request.now, requires=IS_EMPTY_OR(IS_DATE(format=('%Y-%m-%d')))),
                   Field('enddate', 'date', label='To Date', requires=IS_EMPTY_OR(IS_DATE(format=('%Y-%m-%d')))),
                   Field('status', 'string',  widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),label='Status',default='Open', requires = IS_IN_SET(status.TREATMENTPLANSTATUS)),  
                   Field('totaltreatmentcost', 'double', label='Total Treament Cost',default=''),  
                   Field('totalcopay', 'double', label='Total Copay',default=''),  
                   Field('totalinspays', 'double', label='Total Ins. Pays',default=''),  
                   Field('provider', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),default=providerid, label='Provider',requires=IS_IN_DB(db(db.provider.id==providerid), 'provider.id', '%(providername)s')),
                   Field('primarypatient', label='Primary Patient'),
                   Field('patient','string',default='', label='Patient'),
                   Field('patienttype','string',default='', label='Patient Type'),
                   Field('patientname','string',default='', label='Patient Name')
                   
                   )    
    #requires=IS_IN_DB(db(db.vw_primarypatientlist.id==memberid), 'vw_primarypatientlist.id', '%(fname)s  %(lname)s')),
    #Field('primarypatient', default=memberid,label='Primary Patient', requires=IS_IN_DB(sqlquery, 'patientmember.id', '%(fname)s %(lname)s')),
    #Field('patient','string',default='', label='Patient',requires=IS_IN_DB(sqlquery1, 'patientmember.id','(---Select---)'))
    #)    
    
    formA.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=description]')['_rows'] = 5
    xtreatmentplan = formA.element('input',_id='no_table_treatmentplan')
    xtreatmentplan['_class'] =  'w3-input w3-border w'
    
    xstartdate = formA.element('input',_id='no_table_startdate')
    xstartdate['_class'] =  'w3-input w3-border date'

    xenddate = formA.element('input',_id='no_table_enddate')
    xenddate['_class'] =  'w3-input w3-border  date'
    
    xtotaltreatmentcost = formA.element('input',_id='no_table_totaltreatmentcost')
    xtotaltreatmentcost['_class'] =  'w3-input w3-border '

    xtotalcopay = formA.element('input',_id='no_table_totalcopay')
    xtotalcopay['_class'] =  'w3-input w3-border '

    xtotalinspays = formA.element('input',_id='no_table_totalinspays')
    xtotalinspays['_class'] =  'w3-input w3-border '
   
    
    if formA.accepts(request,session,keepvalues=True):
        tplanid = db.treatmentplan.insert(**db.treatmentplan._filter_fields(formA.vars))
        redirect(returnurl)
    else:
        response.flash = 'Errors in Create Treatment Plan'    
            
    returnurl = URL('treatment','list_treatmentplans',vars=dict(page=page,memberid=memberid,providerid=providerid,providername=providername))
    return dict(formA=formA,providername=providername,providerid=providerid,page=page,returnurl=returnurl,memberid=memberid,pps=pps)    




@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def treatment_create():

    #Get URL Variables
    page       = int(common.getpage(request.vars['page']))
    tplanid    = int(common.getid(request.vars.tplanid))
    memberid   = int(common.getid(request.vars.memberid))
    providerid = int(common.getnegid(request.vars.providerid))
    providername = common.getstring(request.vars.providername)
    membername = common.getstring(request.vars.membername)
    patientname = common.getstring(request.vars.patientname)
    
    planid       = ""
    regionid     = ""
    tplan = ""
    
    rows = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.patientmember.patientmember,db.patientmember.groupregion,db.patientmember.hmoplan)
    if(len(rows)==1):
        memberref = common.getstring(rows[0]['patientmember'])
        planid = common.getstring(rows[0]['hmoplan'])
        regionid = common.getstring(rows[0]['groupregion'])
        
    else:
        memberref = ""
        
    rows = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).select(db.treatmentplan.treatmentplan)
    if(len(rows)==1):
        tplan = common.getstring(rows[0]['treatmentplan'])
    else:
        tplan = ""

    treatmentstatus = ""
    treatment = ""

    returnurl = URL('treatment','list_treatments',vars=dict(page=page,tplanid=tplanid,memberid=memberid,providerid=providerid,providername=providername))
    #Field('xdentalprocedure', default='',widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border '), label='Dental Procedure', requires=IS_IN_DB(db, 'dentalprocedure.id', '%(dentalprocedure)s %(shortdescription)s')),
    
    formA = SQLFORM.factory(
                   Field('treatment','string',label='Treatment ID', default=''),
                   Field('description','text', label='Description', default=''),
                   Field('quadrant','string', label='Quadrant(s)', default=''),
                   Field('tooth','string', label='Tooth/Teeth', default=''),
                   Field('startdate', 'date', label='From Date',requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
                   Field('enddate', 'date', label='To Date',requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
                   Field('status', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border '),label='Status',default='Started', requires = IS_IN_SET(status.TREATMENTSTATUS)),  
                   Field('treatmentcost', 'double', label='Total Treament Cost',default=0.00),  
                   Field('copay', 'double', label='Total Copay',default=0.00, writable = False),  
                   Field('inspay', 'double', label='Total Ins. Pays',default=0.00, writable=False),  
                   Field('treatmentplan', default=tplanid, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border '), label='Treatment Plan',requires=IS_IN_DB(db(db.treatmentplan.id==tplanid), 'treatmentplan.id', '%(treatmentplan)s')),
                   Field('provider', default=providerid, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border '), label='Provider'),
                   Field('vwdentalprocedure',  widget=SQLFORM.widgets.autocomplete(request, db.vw_dentalprocedure.shortdescription, id_field=db.vw_dentalprocedure.id),   label='Dental Procedure',requires=IS_IN_DB(db, 'vw_dentalprocedure.id','%(shortdescription)s'))
                   )    

    formA.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=description]')['_rows'] = 5
   
    xvwdentalprocedure = formA.element('input',_id='no_table_vwdentalprocedure')
    xvwdentalprocedure['_class'] =  'w3-input w3-border '
    xvwdentalprocedure['_style'] =  'width:100%;height:35px'
    
    xtreatment = formA.element('input',_id='no_table_treatment')
    xtreatment['_class'] =  'w3-input w3-border '

    xquadrant = formA.element('input',_id='no_table_quadrant')
    xquadrant['_class'] =  'w3-input w3-border '

    xtooth = formA.element('input',_id='no_table_tooth')
    xtooth['_class'] =  'w3-input w3-border '
    
    xstartdate = formA.element('input',_id='no_table_startdate')
    xstartdate['_class'] =  'w3-input w3-border  date'

    xenddate = formA.element('input',_id='no_table_enddate')
    xenddate['_class'] =  'w3-input w3-border  date'
    
    xtreatmentcost = formA.element('input',_id='no_table_treatmentcost')
    xtreatmentcost['_class'] =  'w3-input w3-border '

    #xcopay = formA.element('input',_id='no_table_copay')
    #xcopay['_class'] =  'w3-input w3-border '

    #xinspay = formA.element('input',_id='no_table_inspay')
    #xinspay['_class'] =  'w3-input w3-border '
    
    
    
    
    sql = " SELECT  0 AS procid, '' AS dentalprocedure, '--Select--' as shortdescription, 0 as procedurefee, 0 as ucrfee, 0 as copay"
    sql = sql + " UNION "
    sql = sql + " SELECT dentalprocedure.id AS procid, dentalprocedure.dentalprocedure, dentalprocedure.shortdescription,"
    sql = sql + " IFNULL(copay.procedurefee,dentalprocedure.procedurefee) AS procedurefee,"
    sql = sql + " IFNULL(dentalprocedure.procedurefee,0) AS ucrfee, IFNULL(copay.copay,0) AS copay "
    sql = sql + " FROM dentalprocedure LEFT JOIN copay ON copay.dentalprocedure = dentalprocedure.id"
    sql = sql + " AND copay.region = " + str(regionid) + " AND copay.hmoplan = " + str(planid) + " AND "
    sql = sql + " copay.is_active = \'T\' AND dentalprocedure.is_active = \'T\'"
    sql = sql + " ORDER BY dentalprocedure"
    ds = db.executesql(sql)    

    if formA.accepts(request,session,keepvalues=True):
        treatmentid = db.treatment.insert(**db.treatment._filter_fields(formA.vars))
        row = db(db.vw_dentalprocedure.id == int(common.getid(formA.vars.vwdentalprocedure))).select(db.vw_dentalprocedure.procedurefee)
        if(len(row) > 0):
            ucr = float(common.getstring(row[0].procedurefee))
        else:
            ucr = 0
            
        db(db.treatment.id == treatmentid).update(dentalprocedure = formA.vars.vwdentalprocedure, treatmentcost = ucr)
        calculatecost(tplanid)
        calculatecopay(db, tplanid,memberid)
        calculateinspays(tplanid)
        calculatedue(tplanid)
        db.commit()        
        common.dashboard(db, session, providerid)
        redirect(returnurl)
    else:
        response.flash = 'Error in Treatment Create Form'  
            
    
    return dict(ds=ds,formA=formA,tplanid=tplanid,providername=providername,providerid=providerid,page=page,returnurl=returnurl,memberid=memberid,membername=membername,patientname=patientname)    



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def treatment_update():

    #Get URL Variables
    page       = int(common.getpage(request.vars.page))
    treatmentid = int(common.getid(request.vars.treatmentid))
    tplanid    = int(common.getid(request.vars.tplanid))
    memberid   = int(common.getid(request.vars.memberid))
    providerid = int(common.getnegid(request.vars.providerid))
    providername = common.getstring(request.vars.providername)
    patientname = common.getstring(request.vars.patientname)
    membername = common.getstring(request.vars.membername)
    
    planid       = ""
    regionid     = ""
    tplan = ""
    
    rows = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.patientmember.patientmember,db.patientmember.groupregion,db.patientmember.hmoplan)
    if(len(rows)==1):
        memberref = common.getstring(rows[0]['patientmember'])
        planid = common.getstring(rows[0]['hmoplan'])
        regionid = common.getstring(rows[0]['groupregion'])
        
    else:
        memberref = ""
        
    rows = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).select(db.treatmentplan.treatmentplan)
    if(len(rows)==1):
        tplan = common.getstring(rows[0]['treatmentplan'])
    else:
        tplan = ""


    treatmentstatus = ""
    treatment = ""

    #updatetreatmentcostandcopay(treatmentid)
    
    query = ((db.treatment.id == treatmentid)&(db.treatment.is_active == True))
    
    dstreatments = db(query).select(db.treatment.id, db.treatment.treatment, db.treatment.description, db.treatment.startdate, db.treatment.enddate,\
                                     db.treatment.status,db.treatment.treatmentcost,db.treatment.copay,db.treatment.inspay,db.treatment.quadrant,db.treatment.tooth,db.treatment.is_active,\
                                     db.dentalprocedure.id, db.dentalprocedure.dentalprocedure, db.dentalprocedure.procedurefee, db.dentalprocedure.shortdescription,db.treatmentplan.id, db.treatmentplan.treatmentplan,db.treatmentplan.primarypatient,\
                                     db.treatmentplan.patient,db.treatmentplan.patienttype,db.treatmentplan.patientname, \
                                     db.patientmember.patientmember,db.patientmember.id,db.patientmember.fname,db.patientmember.lname,\
                                     left=[db.treatmentplan.on(db.treatmentplan.id == db.treatment.treatmentplan ),\
                                           db.patientmember.on(db.treatmentplan.primarypatient == db.patientmember.id ),\
                                           db.dentalprocedure.on(db.dentalprocedure.id == db.treatment.dentalprocedure)]
                                          
                                     )    
    copay=0.00
    inspay = 0.00
    treatmentcost=0.00
    ucrfee=0.00
    proccode = ""
    procdesc = ""
    if(len(dstreatments)>0):
        procid  = dstreatments[0].dentalprocedure.id
        tplanid = dstreatments[0].treatmentplan.id
        treatmentcost = dstreatments[0].treatment.treatmentcost
        copay = dstreatments[0].treatment.copay
        inspay = dstreatments[0].treatment.inspay
        ucrfee = dstreatments[0].dentalprocedure.procedurefee
        proccode = dstreatments[0].dentalprocedure.dentalprocedure
        procdesc = dstreatments[0].dentalprocedure.shortdescription
    
    
    
    returnurl = URL('treatment','list_treatments',vars=dict(page=page,tplanid=tplanid,memberid=memberid,providerid=providerid,providername=providername))
    
    formA = SQLFORM.factory(
                   Field('treatment','string',label='Treatment ID', default=common.getstring(dstreatments[0].treatment.treatment)),
                   Field('description','text', label='Description', default=common.getstring(dstreatments[0].treatment.description)),
                   Field('quadrant','string', label='Quadrant(s)', default=common.getstring(dstreatments[0].treatment.quadrant)),
                   Field('tooth','string', label='Tooth/Teeth', default=common.getstring(dstreatments[0].treatment.tooth)),
                   Field('startdate', 'date', label='From Date',default=dstreatments[0].treatment.startdate, requires=IS_EMPTY_OR(IS_DATE(format=('%Y-%m-%d')))),
                   Field('enddate', 'date', label='To Date',default=dstreatments[0].treatment.enddate,requires=IS_EMPTY_OR(IS_DATE(format=('%Y-%m-%d')))),
                   Field('status', 'string', label='Status', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border '),default=common.getstring(dstreatments[0].treatment.status), requires = IS_IN_SET(status.TREATMENTSTATUS)),  
                   Field('treatmentcost', 'double', label='Total Treament Cost',default=treatmentcost),  
                   Field('copay', 'double', label='Total Copay',default=copay,writable=False),  
                   Field('inspay', 'double', label='Total Ins. Pays',default=inspay,writable=False),  
                   Field('treatmentplan', default=dstreatments[0].treatmentplan.id,   widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border '),label='Treatment Plan',requires=IS_IN_DB(db(db.treatmentplan.id==tplanid), 'treatmentplan.id', '%(treatmentplan)s')),
                   Field('provider', default=providerid),
                   Field('dentalprocedure', default=dstreatments[0].dentalprocedure.id,label='Dental Procedure', requires=IS_IN_DB(db, 'dentalprocedure.id', '%(dentalprocedure)s %(shortdescription)s'))
                   )    
    formA.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=description]')['_rows'] = 5
    
    
    xtreatment = formA.element('input',_id='no_table_treatment')
    xtreatment['_class'] =  'w3-input w3-border '

    xquadrant = formA.element('input',_id='no_table_quadrant')
    xquadrant['_class'] =  'w3-input w3-border '

    xtooth = formA.element('input',_id='no_table_tooth')
    xtooth['_class'] =  'w3-input w3-border '
    
    xstartdate = formA.element('input',_id='no_table_startdate')
    xstartdate['_class'] =  'w3-input w3-border  date'

    xenddate = formA.element('input',_id='no_table_enddate')
    xenddate['_class'] =  'w3-input w3-border  date'
    
    xtreatmentcost = formA.element('input',_id='no_table_treatmentcost')
    xtreatmentcost['_class'] =  'w3-input w3-border '

    #xcopay = formA.element('input',_id='no_table_copay')
    #xcopay['_class'] =  'w3-input w3-border '

    #xinspay = formA.element('input',_id='no_table_inspay')
    #xinspay['_class'] =  'w3-input w3-border '
    

    
    sql = " SELECT  0 AS procid, '' AS dentalprocedure, '--Select--' as shortdescription, 0 as procedurefee, 0 as ucrfee, 0 as copay"
    sql = sql + " UNION "
    sql = sql + " SELECT dentalprocedure.id AS procid, dentalprocedure.dentalprocedure, dentalprocedure.shortdescription,"
    sql = sql + " IFNULL(copay.procedurefee,dentalprocedure.procedurefee) AS procedurefee,"
    sql = sql + " IFNULL(dentalprocedure.procedurefee,0) AS ucrfee, IFNULL(copay.copay,0) AS copay "
    sql = sql + " FROM dentalprocedure LEFT JOIN copay ON copay.dentalprocedure = dentalprocedure.id"
    sql = sql + " AND copay.region = " + str(regionid) + " AND copay.hmoplan = " + str(planid) + " AND "
    sql = sql + " copay.is_active = \'T\' AND dentalprocedure.is_active = \'T\'"
    sql = sql + " ORDER BY dentalprocedure"
    ds = db.executesql(sql)    

    if formA.accepts(request,session,keepvalues=True):
        treatmentid = db(db.treatment.id == treatmentid).update(**db.treatment._filter_fields(formA.vars))
        treatmentcost = float(common.getvalue(formA.vars.treatmentcost))
        db(db.treatmentplan.id == tplanid).update(totaltreatmentcost = treatmentcost)
        calculatecost(tplanid)
        calculatecopay(db, tplanid,memberid)
        calculateinspays(tplanid)
        calculatedue(tplanid)
        db.commit()        
        
        redirect(returnurl)
    else:
        response.flash = 'Errors in Treatment update form'    
            
    
    return dict(ds=ds,formA=formA,tplanid=tplanid,providername=providername,providerid=providerid,page=page,returnurl=returnurl,memberid=memberid,membername=membername,patientname=patientname,\
                procid=procid,procdesc=procdesc,ucrfee=ucrfee,proccode=proccode)    


def image_selector():
    is_active = True
    
    ximagepage=int(common.getid(request.vars.ximagepage))
    providerid = int(common.getid(request.vars.providerid))
    patientid = int(common.getid(request.vars.patientid))
    
    items_per_page = 4
    limitby = ((ximagepage)*items_per_page,(ximagepage+1)*items_per_page) 


    images = None
    if(limitby > 0):
        images = db((db.dentalimage.patient == patientid) & (db.dentalimage.provider == providerid) & (db.dentalimage.image != "") & \
                      (db.dentalimage.image != None) & (db.dentalimage.is_active == True)).select(\
                        db.dentalimage.id,db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                        db.dentalimage.patienttype,db.dentalimage.patientname,db.dentalimage.description,db.dentalimage.is_active,db.vw_memberpatientlist.patientmember,\
                        left=[db.vw_memberpatientlist.on(db.dentalimage.patient == db.vw_memberpatientlist.patientid)],\
                              limitby=limitby, orderby = db.vw_memberpatientlist.patientmember | ~db.dentalimage.patienttype | ~db.dentalimage.id                      
                      )
    else:
        images = db((db.dentalimage.patient == patientid) & (db.dentalimage.provider == providerid) & (db.dentalimage.image != "") & \
                      (db.dentalimage.image != None) & (db.dentalimage.is_active == True)).select(
                        db.dentalimage.id,db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                        db.dentalimage.patienttype,db.dentalimage.patientname,db.dentalimage.description,db.dentalimage.is_active,db.vw_memberpatientlist.patientmember,\
                        left=[db.vw_memberpatientlist.on(db.dentalimage.patient == db.vw_memberpatientlist.patientid)],\
                              orderby = db.vw_memberpatientlist.patientmember | ~db.dentalimage.patienttype | ~db.dentalimage.id
                    )


    return dict(images=images, imagepage=ximagepage)  


def dentalprocedure_selector():
    
    pattern = request.vars.vwdentalprocedure.capitalize() + '%'
    
    
    
    selected = [row.shortdescription for row in db((db.vw_dentalprocedure.is_active == True)  & \
                (db.vw_dentalprocedure.shortdescription.like(pattern))).select()]

        
    return ''.join([DIV(k,
                 _onclick="jQuery('#no_table_vwdentalprocedure').val('%s')" % k,
                 _onmouseover="this.style.backgroundColor='yellow'",
                 _onmouseout="this.style.backgroundColor='white'"
                 ).xml() for k in selected])



def treatment_hide():
    return ''

def treatmentpatient_selector():
    provdict    = common.getprovider(auth,db)
    providerid  = common.getid(provdict["providerid"])   
    
    #if not request.vars.patientmember:
        #return ''
        
    xmemberid = int(common.getid(request.vars.xmemberid))
    
    if(request.vars.patientmember ==""):
        pattern = '%'
    else:
        pattern = request.vars.patientmember.capitalize() + '%'
        
    if(xmemberid == 0):
        selected = [row.patient for row in db(((db.vw_memberpatientlist.is_active == True)  & \
                                               ((db.vw_memberpatientlist.providerid == providerid) | ((db.vw_memberpatientlist.providerid == 1)&\
                                                                                                          (db.vw_memberpatientlist.hmopatientmember == False))))&\
                                              (db.vw_memberpatientlist.patient.like(pattern))).select()]
        
    else:
        selected = [row.patient for row in db(((db.vw_memberpatientlist.is_active == True)  & (db.vw_memberpatientlist.primarypatientid == xmemberid)  & \
                                               ((db.vw_memberpatientlist.providerid == providerid) | ((db.vw_memberpatientlist.providerid == 1)&\
                                                                                                          (db.vw_memberpatientlist.hmopatientmember == False))))&\
                                              (db.vw_memberpatientlist.patient.like(pattern))).select()]
        
    return ''.join([DIV(k,
                 _onclick="jQuery('#no_table_patientmember').val('%s')" % k,
                 _onmouseover="this.style.backgroundColor='yellow'",
                 _onmouseout="this.style.backgroundColor='white'"
                 ).xml() for k in selected])



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def image_update():
    
    if(len(request.vars) == 0):
        raise HTTP(403,"Error: No dental image to  update : dentalimage_update()")

    page         = int(common.getpage(request.vars.xpage))
    memberpage   = int(common.getpage(request.vars.xmemberpage))
    imagepage    = int(common.getpage(request.vars.ximagepage))
    
    providerid   = int(common.getnegid(request.vars.xproviderid))
    patientid   = int(common.getnegid(request.vars.xpatientid))
    memberid   = int(common.getnegid(request.vars.xmemberid))
   
    treatmentid   = int(common.getnegid(request.vars.xtreatmentid))
    
    
    
    
    title  = common.getstring(request.vars.form_title)
    tooth  = common.getstring(request.vars.form_tooth)
    quadrant  = common.getstring(request.vars.form_quadrant)
    imageid   = int(common.getid(request.vars.form_imageid))
    imagedate   = common.getnulldt( datetime.datetime.strptime(request.vars.form_imagedate, '%d/%m/%Y'))
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
    
    redirect(URL('treatment','update_treatment', vars = dict(page=page,imagepage=imagepage,providerid=providerid,treatmentid=treatmentid)))
    

def preauthorization():
    
    #check whether webadmin login
    impersonated = auth.user.impersonated
    
    
    memberid = 0
    patientid = 0
    procedureid = 0
    ucrfee = 0    
    tplanid = 0
    doctorid = 0
    companyid = 0
    
    patienttype = 'P'
    patientmember = ''
    membername = ''
    patientname = ''
    fullname = ''
    patient = ''
    doctorname = ''
    altshortdescription = ''
    title = ''
    
    #provider : logged in
    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getprovider(auth, db)
    providername  = provdict["providername"]
    
    treatment = ""
    
    #page
    page       = int(common.getpage(request.vars.page)) 
    imagepage  = int(common.getpage(request.vars.imagepage))
 
    dob = ""
    cell = ""
    email = ""
    telephone = ""
    address1 = ""
    address2 = ""
    address3 = ""
    city = ""
    st = ""
    pin = ""
    
    medicalalert = False
    
    authorization = common.getboolean(request.vars.authorization)
    preauthorized = common.getboolean(request.vars.preauthorization)
    authorized = common.getboolean(request.vars.authorized)      #post authorization
    preauthorizeerror = False
    authorizeerror = False
    webadmin = common.getboolean(request.vars.webadmin)
       
    
    rows = None
    

      
    #treatmentid,treatment, memberid,patientid,patientmember,membername, patientname, patienttype
    treatmentid = int(common.getid(request.vars.treatmentid))
    treatments = db(db.treatment.id == treatmentid).select()
    authorizationurl = URL('reports', 'treatmentreport', vars=dict(page=page, providerid=providerid,treatmentid=treatmentid))
    
    totaltreatmentcost = 0
    totalactualtreatmentcost = 0
    
    freetreatment = True
    newmember = False
    cos=None
    
    procedurepriceplancode = "PREMWALKIN"
    remarks = ""
    patienttype = 'P'
    treatment = common.getstring(treatments[0].treatment)
    tplanid = int(common.getid(treatments[0].treatmentplan))
    procedureid = int(common.getid(treatments[0].dentalprocedure))
    doctorid = int(common.getid(treatments[0].doctor))
    docs=db(db.doctor.id == doctorid).select(db.doctor.name)
    totaltreatmentcost = float(common.getvalue(treatments[0].treatmentcost)) #this is the actual treatment cost = total treatment cost unless it is changed by provider
    totalactualtreatmentcost = float(common.getvalue(treatments[0].actualtreatmentcost))   #this is total UCRR
    
   
        
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
        patientname = common.getstring(tplans[0].patientname.strip())
        
        rows = db((db.vw_memberpatientlist.primarypatientid == memberid)&(db.vw_memberpatientlist.patientid == patientid)&(db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).\
            select()
        
        if(len(rows)>0):
            title = rows[0].title
            fullname = common.getstring(rows[0].fullname).strip()
            patientmember = common.getstring(rows[0].patientmember).strip()
            patientname = common.getstring(rows[0].patient).strip()
            membername = common.getstring(rows[0].fullname).strip()
            procedurepriceplancode = mdputils.getprocedurepriceplancodeformember(db,providerid, memberid, patientid) # IB:15-Mar-2020 rows[0].procedurepriceplancode
            newmember = common.getboolean(rows[0].newmember)          
            freetreatment = common.getboolean(rows[0].freetreatment)
            patienttype = rows[0].patienttype
            #procedurepriceplancode = rows[0].procedurepriceplancode
            hmopatientmember = rows[0].hmopatientmember  
            companyid = int(common.getid(rows[0].company))
            cos = db(db.company.id == companyid).select()
            
    
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
    #preauthorized = mail.emailPreAuthorization(db, request.folder, treatmentid)
    preauthorized = True
    mail.emailPreAuthorization(db, request.folder, treatmentid)   #preauthorized is true irrespective if email is sent successfully or not
    preauthorizeerror = not preauthorized

    if(preauthorized==True):
        defsts = 'Sent for Authorization'
        db(db.treatment.id == treatmentid).update(status = defsts)
        db(db.treatment_procedure.treatmentid == treatmentid).update(status=defsts)
    else:
        defsts = common.getstring(treatments[0].status)
        defsts = defsts if((defsts != None) & (defsts != "")) else 'Started'
       
    
    enddate = common.getdt(treatments[0].enddate)

    writablflag = (not authorization) | (((not preauthorized) & (not authorized)&(not webadmin))|((webadmin)))
    formTreatment = SQLFORM.factory(
          Field('patientmember', 'string',  label='Patient', default = fullname,\
                requires=[IS_NOT_EMPTY(),IS_IN_DB(db(db.vw_memberpatientlist.providerid == providerid), 'vw_memberpatientlist.fullname','%(fullname)s')],writable=False),
          Field('xmemberid', 'string',  label='Member',default=memberid),
          Field('treatment','string',label='Treatment No.', default=treatments[0].treatment,writable=writablflag),
          Field('chiefcomplaint','string',label='Chief Complaint', default=treatments[0].chiefcomplaint,writable=writablflag),
          Field('description','text', label='Description', default=treatments[0].description, writable=writablflag),
          #Field('quadrant','string', label='Quadrant(s)', default=treatments[0].quadrant),
          #Field('tooth','string', label='Tooth/Teeth', default=treatments[0].tooth),
          Field('startdate', 'date', label='From Date',default=treatments[0].startdate, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))), writable=writablflag),
          Field('enddate', 'date', label='To Date',default=enddate, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))),writable=writablflag),
          Field('status', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border ',_onchange='onstatuschange()'),label='Status',default=defsts, requires = IS_IN_SET(status.TREATMENTSTATUS), writable=writablflag),  
          Field('ucrfee', 'double', label='Total UCR',default=totalactualtreatmentcost,writable=False),  
          Field('treatmentcost', 'double', label='Total Treament Cost',default=totaltreatmentcost,writable=False),  
          Field('copay', 'double', label='Total Copay',default=treatments[0].copay, writable = False),  
          Field('inspay', 'double', label='Total Ins. Pays',default=treatments[0].inspay, writable=False),  
          Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
          Field('remarks', 'string', default = remarks, writable=writablflag),
          Field('vwdentalprocedure', 'string',  default='', label='Procedure ID'),
          Field('vwdentalprocedurecode', 'string',  default='', label='Procedure Code'), 
          Field('xaction', 'string', default = 'UpdateTreatment')
          
          )    
       
   
   
    doc = formTreatment.element('#no_table_doctor')
    doc['_class'] = 'form-control'
    doc['_style'] = 'width:100%'
    

    xvwdentalprocedurecode = formTreatment.element('input',_id='no_table_vwdentalprocedurecode')
    xvwdentalprocedurecode['_class'] =  'form-control '
    xvwdentalprocedurecode['_placeholder'] = 'Enter Dental Procedure Code' 
    xvwdentalprocedurecode['_autocomplete'] = 'off'         
    xvwdentalprocedurecode['_style'] = 'width:100%'
    
    xvwdentalprocedure = formTreatment.element('input',_id='no_table_vwdentalprocedure')
    xvwdentalprocedure['_class'] =  'form-control '
    xvwdentalprocedure['_placeholder'] = 'Enter Dental Procedure Name' 
    xvwdentalprocedure['_autocomplete'] = 'off'         
    xvwdentalprocedure['_style'] = 'width:100%'   

    

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

        xtreatment = formTreatment.element('input',_id='no_table_treatment')
        xtreatment['_class'] =  'form-control'
        xtreatment['_type'] =  'text'
        xtreatment['_autocomplete'] = 'off' 

        cc = formTreatment.element('input', _id='no_table_chiefcomplaint')
        cc['_class'] = 'form-control'
        cc['_style'] = 'width:100%'
        cc['_type'] =  'text'
 
    # procedures grid
    query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True))
    fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription, \
               db.vw_treatmentprocedure.procedurefee,db.vw_treatmentprocedure.copay,db.vw_treatmentprocedure.inspays,db.vw_treatmentprocedure.status,\
               db.vw_treatmentprocedure.treatmentdate)
            

    headers={
        'vw_treatmentprocedure.procedurecode':'Code',
        'vw_treatmentprocedure.altshortdescription':'Description',
        'vw_treatmentprocedure.procedurefee':'Procedure Cost',
        'vw_treatmentprocedure.copay':'Co-Pay',
        'vw_treatmentprocedure.inspays':'Authorized',
        'vw_treatmentprocedure.status':'Status',
        'vw_treatmentprocedure.treatmentdate':'Treatment Date'
    }
    
    links = [\
        dict(header=CENTER('Edit'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=30, _height=30),\
                                                           _href=URL("treatment","update_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin))))),
        dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),\
                                                                  _href=URL("treatment","delete_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid)))))
    ]

    maxtextlengths = {'vw_treatmentprocedure.altshortdescription':100}
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
       
    formProcedure = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        paginate=10,
                        maxtextlengths=maxtextlengths,
                        orderby=None,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )  
  
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
        
        
        updatetreatmentcostandcopay(treatmentid,tplanid)
        #calculatecost(tplanid)
        #calculatecopay(db, tplanid,memberid)
        #calculateinspays(tplanid)
        #calculatedue(tplanid)
        
        #db.commit()                
    
        db.treatmentnotes.update_or_insert(db.treatmentnotes.treatment == treatmentid, treatment = treatmentid, notes = formTreatment.vars.prescription)   
 
        csrdate = (request.now).strftime('%d/%m/%Y %H:%M:%S')
        csr = csrdate + " : " + "CSR:"  + treatment + "\r\n" + "Doctor: " + doctorname + "\r\n" + formTreatment.vars.description
        csrid = db.casereport.insert(patientid = patientid, providerid=providerid, doctorid=doctorid, casereport = csr, is_active=True,\
                                      created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid)
        
        session.flash = "Treatment Details Updated!"
        
       
        redirect(returnurl)

    elif formTreatment.errors:
        response.flash = "Error - Updating Treatment Report! " + str(formTreatment.errors)
        #redirect(returnurl)    
    return dict(formTreatment=formTreatment,\
                    formProcedure=formProcedure,\
                    page=page, memberpage=0, imagepage=imagepage,procedureid=procedureid,\
                    providerid=providerid, providername=providername,doctorid=doctorid,doctorname=docs[0].name,\
                    hmopatientmember=hmopatientmember,patientmember=patientmember, memberid=memberid,membername=membername, patientid=patientid,patientname=patientname,
                    treatment=treatment,treatmentid=treatmentid,tplanid=tplanid,medicalalerts=medicalalerts,\
                    authorization=authorization,authorizationurl=authorizationurl,writablflag=writablflag,
                    preauthorized=preauthorized,preauthorizeerror=preauthorizeerror,authorizeerror=authorizeerror,authorized=authorized,\
                    webadmin=webadmin,returnurl=returnurl,freetreatment=freetreatment,newmember=newmember                   
                    )        

def authorizetreatment():
    
    #check whether webadmin login
    impersonated = auth.user.impersonated
    
    
    memberid = 0
    patientid = 0
    procedureid = 0
    ucrfee = 0    
    tplanid = 0
    doctorid = 0
    
    patienttype = 'P'
    patientmember = ''
    membername = ''
    patientname = ''
    fullname = ''
    patient = ''
    doctorname = ''
    altshortdescription = ''
    title = ''
    
    #provider : logged in
    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getprovider(auth, db)
    providername  = provdict["providername"]
    
    treatment = ""
    
    #page
    page       = int(common.getpage(request.vars.page)) 
    imagepage  = int(common.getpage(request.vars.imagepage))
 
    dob = ""
    cell = ""
    email = ""
    telephone = ""
    address1 = ""
    address2 = ""
    address3 = ""
    city = ""
    st = ""
    pin = ""
    
    medicalalert = False
    
    authorization = common.getboolean(request.vars.authorization)
    preauthorized = common.getboolean(request.vars.preauthorization)
    authorized = True   #post authorization
    authorizeerror = False
    preauthorizeerror = False
    webadmin = common.getboolean(request.vars.webadmin)
       
    
    rows = None
    fretreatment=True
    newmember = False
    cos=None    

      
    #treatmentid,treatment, memberid,patientid,patientmember,membername, patientname, patienttype
    treatmentid = int(common.getid(request.vars.treatmentid))
    treatments = db(db.treatment.id == treatmentid).select()
    authorizationurl = URL('reports', 'treatmentreport', vars=dict(page=page, providerid=providerid,treatmentid=treatmentid))
    
    totaltreatmentcost = 0
    totalactualtreatmentcost = 0
    
    
    
    procedurepriceplancode = "PREMWALKIN"
    remarks = ""
    patienttype = 'P'
    treatment = common.getstring(treatments[0].treatment)
    tplanid = int(common.getid(treatments[0].treatmentplan))
    procedureid = int(common.getid(treatments[0].dentalprocedure))
    doctorid = int(common.getid(treatments[0].doctor))
    docs=db(db.doctor.id == doctorid).select(db.doctor.name)
    totaltreatmentcost = float(common.getvalue(treatments[0].treatmentcost)) #this is the actual treatment cost = total treatment cost unless it is changed by provider
    totalactualtreatmentcost = float(common.getvalue(treatments[0].actualtreatmentcost))   #this is total UCRR
    
   
        
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
            newmember = common.getboolean(rows[0].newmember)          
            freetreatment = common.getboolean(rows[0].freetreatment)            
            procedurepriceplancode = mdputils.getprocedurepriceplancodeformember(db,providerid, memberid, patientid) #IB:15-Mar-2020 rows[0].procedurepriceplancode
            companyid = int(common.getid(rows[0].company))
            cos = db(db.company.id == companyid).select()
            
    
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
    #authorized = mail.emailAuthorizedTreatment(db, request.folder, treatmentid)
    mail.emailAuthorizedTreatment(db, request.folder, treatmentid)  # authorized even if email is sent successfully or not.
    authorizeerror = not authorized

    if(authorized==True):
        defsts = 'Authorized'
        db(db.treatment.id == treatmentid).update(status = defsts)
        db(db.treatment_procedure.treatmentid == treatmentid).update(status=defsts)
    else:
        defsts = common.getstring(treatments[0].status)
        defsts = defsts if((defsts != None) & (defsts != "")) else 'Started'
       
    
    enddate = common.getdt(treatments[0].enddate)

    writablflag = (not authorization) | (((not preauthorized) & (not authorized)&(not webadmin))|((webadmin)))
    
    formTreatment = SQLFORM.factory(
       Field('patientmember', 'string',  label='Patient', default = fullname,\
             requires=[IS_NOT_EMPTY(),IS_IN_DB(db(db.vw_memberpatientlist.providerid == providerid), 'vw_memberpatientlist.fullname','%(fullname)s')],writable=False),
       Field('xmemberid', 'string',  label='Member',default=memberid),
       Field('treatment','string',label='Treatment No.', default=treatments[0].treatment,writable=writablflag),
       Field('chiefcomplaint','string',label='Chief Complaint', default=treatments[0].chiefcomplaint,writable=writablflag),
       Field('description','text', label='Description', default=treatments[0].description, writable=writablflag),
       #Field('quadrant','string', label='Quadrant(s)', default=treatments[0].quadrant),
       #Field('tooth','string', label='Tooth/Teeth', default=treatments[0].tooth),
       Field('startdate', 'date', label='From Date',default=treatments[0].startdate, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))), writable=writablflag),
       Field('enddate', 'date', label='To Date',default=enddate, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))),writable=writablflag),
       Field('status', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border ',_onchange='onstatuschange()'),label='Status',default=defsts, requires = IS_IN_SET(status.TREATMENTSTATUS), writable=writablflag),  
       Field('ucrfee', 'double', label='Total UCR',default=totalactualtreatmentcost,writable=False),  
       Field('treatmentcost', 'double', label='Total Treament Cost',default=totaltreatmentcost,writable=False),  
       Field('copay', 'double', label='Total Copay',default=treatments[0].copay, writable = False),  
       Field('inspay', 'double', label='Total Ins. Pays',default=treatments[0].inspay, writable=False),  
       Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
       Field('remarks', 'string', default = remarks, writable=writablflag),
       Field('vwdentalprocedure', 'string',  default='', label='Procedure ID'),
       Field('vwdentalprocedurecode', 'string',  default='', label='Procedure Code'), 
       Field('xaction', 'string', default = 'UpdateTreatment')
       )    
    


    doc = formTreatment.element('#no_table_doctor')
    doc['_class'] = 'form-control'
    doc['_style'] = 'width:100%'
   

    

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

        xtreatment = formTreatment.element('input',_id='no_table_treatment')
        xtreatment['_class'] =  'form-control'
        xtreatment['_type'] =  'text'
        xtreatment['_autocomplete'] = 'off' 

        cc = formTreatment.element('input', _id='no_table_chiefcomplaint')
        cc['_class'] = 'form-control'
        cc['_style'] = 'width:100%'
        cc['_type'] =  'text'
  
    # procedures grid
    query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True))
    fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription, \
               db.vw_treatmentprocedure.procedurefee,db.vw_treatmentprocedure.copay,db.vw_treatmentprocedure.inspays,db.vw_treatmentprocedure.status,\
               db.vw_treatmentprocedure.treatmentdate)
            

    headers={
        'vw_treatmentprocedure.procedurecode':'Code',
        'vw_treatmentprocedure.altshortdescription':'Description',
        'vw_treatmentprocedure.procedurefee':'Procedure Cost',
        'vw_treatmentprocedure.copay':'Co-Pay',
        'vw_treatmentprocedure.inspays':'Authorized',
        'vw_treatmentprocedure.status':'Status',
        'vw_treatmentprocedure.treatmentdate':'Treatment Date'
    }
    
    links = [\
        dict(header=CENTER('Edit'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=30, _height=30),\
                                                           _href=URL("treatment","update_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin))))),
        dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),\
                                                                  _href=URL("treatment","delete_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid)))))
    ]

    maxtextlengths = {'vw_treatmentprocedure.altshortdescription':100}
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
       
    formProcedure = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        paginate=10,
                        maxtextlengths=maxtextlengths,
                        orderby=None,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )  
  
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
        
        
        updatetreatmentcostandcopay(treatmentid,tplanid)
        #calculatecost(tplanid)
        #calculatecopay(db, tplanid,memberid)
        #calculateinspays(tplanid)
        #calculatedue(tplanid)
        
        #db.commit()                
    
        db.treatmentnotes.update_or_insert(db.treatmentnotes.treatment == treatmentid, treatment = treatmentid, notes = formTreatment.vars.prescription)   
 
        csrdate = (request.now).strftime('%d/%m/%Y %H:%M:%S')
        csr = csrdate + " : " + "CSR:"  + treatment + "\r\n" + "Doctor: " + doctorname + "\r\n" + formTreatment.vars.description
        csrid = db.casereport.insert(patientid = patientid, providerid=providerid, doctorid=doctorid, casereport = csr, is_active=True,\
                                      created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid)
        
        session.flash = "Treatment Details Updated!"
        
       
        redirect(returnurl)

    elif formTreatment.errors:
        response.flash = "Error - Updating Treatment Report!" + str(formTreatment.errors)
        #redirect(returnurl)    
    return dict(formTreatment=formTreatment,\
                    formProcedure=formProcedure,\
                    page=page, memberpage=0, imagepage=imagepage,procedureid=procedureid,\
                    providerid=providerid, providername=providername,doctorid=doctorid,doctorname=docs[0].name,\
                    patientmember=patientmember, memberid=memberid,membername=membername, patientid=patientid,patientname=patientname,
                    treatment=treatment,treatmentid=treatmentid,tplanid=tplanid,medicalalerts=medicalalerts,\
                    authorization=authorization,authorizationurl=authorizationurl,writablflag=writablflag,
                    preauthorized=preauthorized,preauthorizeerror=preauthorizeerror,authorizeerror=authorizeerror,authorized=authorized,webadmin=webadmin,returnurl=returnurl,
                    freetreatment=freetreatment,newmember=newmember
                    )        


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def update_treatment():
    
    
    memberid = 0
    patientid = 0
    procedureid = 0
    ucrfee = 0    
    tplanid = 0
    doctorid = 0
    
    patienttype = 'P'
    patientmember = ''
    hmopatientmember = False
    membername = ''
    patientname = ''
    fullname = ''
    patient = ''
    doctorname = ''
    altshortdescription = ''
    title = ''
    
    #provider : logged in
    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getprovider(auth, db)
    providername  = provdict["providername"]
    
    treatment = ""
    
    #page
    page       = int(common.getpage(request.vars.page)) 
    imagepage  = int(common.getpage(request.vars.imagepage))
 
    dob = ""
    cell = ""
    email = ""
    telephone = ""
    address1 = ""
    address2 = ""
    address3 = ""
    city = ""
    st = ""
    pin = ""
    newmember = False
    freetreatment = True
    
    medicalalert = False
    
    authorization = False   #authorization required based on company/plan
    preauthorized = False
    authorized = False      #post authorization
    preauthorizeerror = False
    authorizeerror = False
    webadmin = auth.user.impersonated
       
    rows = None
   
    #treatmentid,treatment, memberid,patientid,patientmember,membername, patientname, patienttype
    treatmentid = int(common.getid(request.vars.treatmentid))
    treatments = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
    authorizationurl = URL('reports', 'treatmentreport', vars=dict(page=page, providerid=providerid,treatmentid=treatmentid))

    tplanid = treatments[0].treatmentplan if(len(treatments) > 0) else 0
    #logger.loggerpms2.info("Enter updatetreatmentpayment from update treatment")
    r = json.loads(account._updatetreatmentpayment(db,tplanid,0))
    #logger.loggerpms2.info("After updatetreatmentpayment from update treatment " + json.dumps(r))
    paytm = json.loads(account._calculatepayments(db,tplanid,None))
    
    totaltreatmentcost = 0
    totalactualtreatmentcost = 0
    
    
    
    procedurepriceplancode = "PREMWALKIN"
    remarks = ""
    patienttype = 'P'
    writablflag = True
    formTreatment = None
    formProcedure = None
    currentnotes = ""
    
    if(len(treatments) > 0):
        
        treatment = common.getstring(treatments[0].treatment)
        tplanid = int(common.getid(treatments[0].treatmentplan))
        procedureid = int(common.getid(treatments[0].dentalprocedure))
        doctorid = int(common.getid(treatments[0].doctor))
        currnotes = common.getstring(treatments[0].description)
        
        docs=db(db.doctor.id == doctorid).select(db.doctor.name)
        
        #totaltreatmentcost = float(common.getvalue(treatments[0].treatmentcost)) #this is the actual treatment cost = total treatment cost unless it is changed by provider
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
                #procedurepriceplancode = mdputils.getprocedurepriceplancodeformember(db,providerid, memberid, patientid) #IB:15-Mar-2020 rows[0].procedurepriceplancode
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
        
        precopay = paytm["precopay"]
        discount_amount = paytm["discount_amount"] + paytm["walletamount"]
        walletamount = paytm["walletamount"]
        netcopay = paytm["copay"]
        treatmentcost = paytm["treatmentcost"]
        inspay = paytm["inspays"]
        totalpaid = paytm["totalpaid"]
        totaldue = paytm["totaldue"]
        companypay = paytm["companypays"]
        
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
           Field('status', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border ',_onchange='onstatuschange()'),label='Status',default=defsts, requires = IS_IN_SET(status.TREATMENTSTATUS),writable=True,readable=True),  
           Field('ucrfee', 'double', label='Total UCR',default=totalactualtreatmentcost,writable=False),  
           Field('treatmentcost', 'double', label='Total Treament Cost',default=treatmentcost,writable=False),  
           Field('precopay', 'double', label='Total Copay',default=precopay, writable = False),  
           Field('companypay', 'double', label='Benefit Amount',default=companypay, writable = False),  
           Field('discount_amount', 'double', label='Discount Amount',default=discount_amount, writable = False),  
           Field('copay', 'double', label='Total Copay',default=netcopay, writable = False),  
           Field('inspay', 'double', label='Total Ins. Pays',default=inspay, writable=False),  
           Field('totalpaid', 'double', label='Total Paid',default=totalpaid, writable=False),  
           Field('totaldue', 'double', label='Total Due',default=totaldue, writable=False),  
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
            
            if(defsts == 'Authorized'):
                authorized = True
            else:
                authorized = False  
            
           
            db(db.treatment.id == treatmentid).update(\
                treatment = formTreatment.vars.treatment,
                chiefcomplaint = formTreatment.vars.chiefcomplaint,
                description  = formTreatment.vars.description,
                startdate = formTreatment.vars.startdate,
                enddate = formTreatment.vars.enddate,
                status = formTreatment.vars.status,       #status = defsts  before 16.9.2020
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
            
            
            updatetreatmentcostandcopay(treatmentid,tplanid)
            #calculatecost(tplanid)
            #calculatecopay(db, tplanid,memberid)
            #calculateinspays(tplanid)
            #calculatedue(tplanid)
            
            #db.commit()                
        
            db.treatmentnotes.update_or_insert(db.treatmentnotes.treatment == treatmentid, treatment = treatmentid, notes = formTreatment.vars.prescription)   
            
            if(changeinnotes(currnotes, formTreatment.vars.description)):
                common.lognotes(db,formTreatment.vars.description,treatmentid)
            
            response.flash = "Treatment Details Updated!"
            
        elif formTreatment.errors:
            session.flash = "Error - Updating Treatment Report!" + str(formTreatment.errors)
            redirect(returnurl)
            
    #====== Medical History Foem
    #===== End Medical History
    
    
    #===== Medical Test form and grid
    #====== End of Medical Test
    
    #====== Prescription Form and grid
    #===== End of Prescription
    
    
    #==== Images
    #==== End of Images
          
       
    booking_amount = account.get_booking_amount(db, treatmentid)
    showprocgrid = True
    booking = True if(booking_amount > 0) else False
    
    return dict(formTreatment=formTreatment, formProcedure=formProcedure,  \
                page=page, memberpage=0, imagepage=imagepage,procedureid=procedureid,\
                providerid=providerid, providername=providername,doctorid=doctorid,doctorname=docs[0].name,\
                patientmember=patientmember, memberid=memberid,membername=membername, patientid=patientid,patientname=patientname, hmopatientmember=hmopatientmember,\
                treatment=treatment,treatmentid=treatmentid,tplanid=tplanid,medicalalerts=medicalalerts,\
                authorization=authorization,authorizationurl=authorizationurl,writablflag=writablflag,
                preauthorized=preauthorized,preauthorizeerror=preauthorizeerror,authorizeerror=authorizeerror,authorized=authorized,webadmin=webadmin,returnurl=returnurl,\
                freetreatment=freetreatment,newmember=newmember,showprocgrid = showprocgrid,booking=booking,booking_amount = booking_amount
                )        
            

#@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
#@auth.requires_login()
#def xupdate_treatment():
    
    
    #memberid = 0
    #patientid = 0
    #procedureid = 0
    #ucrfee = 0    
    #tplanid = 0
    #doctorid = 0
    
    #patienttype = 'P'
    #patientmember = ''
    #hmopatientmember = False
    #membername = ''
    #patientname = ''
    #fullname = ''
    #patient = ''
    #doctorname = ''
    #altshortdescription = ''
    #title = ''
    
    ##provider : logged in
    #providerid = int(common.getid(request.vars.providerid))
    #provdict = common.getprovider(auth, db)
    #providername  = provdict["providername"]
    
    #treatment = ""
    
    ##page
    #page       = int(common.getpage(request.vars.page)) 
    #imagepage  = int(common.getpage(request.vars.imagepage))
 
    #dob = ""
    #cell = ""
    #email = ""
    #telephone = ""
    #address1 = ""
    #address2 = ""
    #address3 = ""
    #city = ""
    #st = ""
    #pin = ""
    #newmember = False
    #freetreatment = True
    
    #medicalalert = False
    
    #authorization = False   #authorization required based on company/plan
    #preauthorized = False
    #authorized = False      #post authorization
    #preauthorizeerror = False
    #authorizeerror = False
    #webadmin = auth.user.impersonated
       
    #rows = None
   
    ##treatmentid,treatment, memberid,patientid,patientmember,membername, patientname, patienttype
    #treatmentid = int(common.getid(request.vars.treatmentid))
    #treatments = db(db.treatment.id == treatmentid).select()
    #authorizationurl = URL('reports', 'treatmentreport', vars=dict(page=page, providerid=providerid,treatmentid=treatmentid))
    
    #totaltreatmentcost = 0
    #totalactualtreatmentcost = 0
    
    
    
    #procedurepriceplancode = "PREMWALKIN"
    #remarks = ""
    #patienttype = 'P'
    #writablflag = True
    #formTreatment = None
    #formProcedure = None
    #currentnotes = ""
    
    #if(len(treatments) > 0):
        
        #treatment = common.getstring(treatments[0].treatment)
        #tplanid = int(common.getid(treatments[0].treatmentplan))
        #procedureid = int(common.getid(treatments[0].dentalprocedure))
        #doctorid = int(common.getid(treatments[0].doctor))
        #currnotes = common.getstring(treatments[0].description)
        
        #docs=db(db.doctor.id == doctorid).select(db.doctor.name)
        #totaltreatmentcost = float(common.getvalue(treatments[0].treatmentcost)) #this is the actual treatment cost = total treatment cost unless it is changed by provider
        #totalactualtreatmentcost = float(common.getvalue(treatments[0].actualtreatmentcost))   #this is total UCRR
        #authorized = common.getboolean(treatments[0].authorized) & (webadmin == True)
    
            
        #procs = db(db.vw_procedurepriceplan.id == procedureid).select()  
        #if(len(procs) > 0):
            #ucrfee = common.getvalue(procs[0].ucrfee)
            #altshortdescription = common.getstring(procs[0].altshortdescription)
            #remarks =  common.getstring(procs[0].remarks)
       
        #tplans = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.provider==providerid) & (db.treatmentplan.is_active == True)).select()
       
      
        
        #if(len(tplans) > 0):
            #memberid = tplans[0].primarypatient
            #patientid = tplans[0].patient
            #patienttype = tplans[0].patienttype
            #patientname = tplans[0].patientname.strip()
            
            #rows = db((db.vw_memberpatientlist.primarypatientid == memberid)&(db.vw_memberpatientlist.patientid == patientid)&(db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).\
                #select()
            #companyid = ""
            #if(len(rows)>0):
                #title = rows[0].title
                #fullname = rows[0].fullname.strip()
                #patientmember = rows[0].patientmember.strip()
                #patient = rows[0].patient.strip()
                #membername = rows[0].fullname.strip()
                #hmopatientmember = rows[0].hmopatientmember
                #procedurepriceplancode = rows[0].procedurepriceplancode
                #newmember = common.getboolean(rows[0].newmember)          
                #freetreatment = common.getboolean(rows[0].freetreatment)                    
                #companyid = int(common.getstring(rows[0].company))
                #cos = db(db.company.id == companyid).select()
                ## No Authorization till procedures are added.
                #procs = db((db.treatment_procedure.treatmentid == treatmentid)&(db.treatment_procedure.is_active==True)).count()                
                #authorization = common.getboolean(cos[0].authorizationrequired) & (procs>0)
                           
                
 
        
        ##medical alerts
        #medicalalerts = False
        #alerts = db((db.medicalnotes.patientid == patientid) & (db.medicalnotes.memberid == memberid)).select()
        #if(len(alerts)>0):
            #medicalalerts = medicalalerts | common.getboolean(alerts[0].allergic)
            #medicalalerts = medicalalerts | common.getboolean(alerts[0].bp)
            #medicalalerts = medicalalerts | common.getboolean(alerts[0].heart)
            #medicalalerts = medicalalerts | common.getboolean(alerts[0].cardiac)
            #medicalalerts = medicalalerts | common.getboolean(alerts[0].diabetes)
            #medicalalerts = medicalalerts | common.getboolean(alerts[0].anyother)
       
       
      
        ##determine treatment status   
        #defsts = common.getstring(treatments[0].status)
        #defsts = defsts if((defsts != None) & (defsts != "")) else 'Started'
       
        #if(defsts == 'Sent for Authorization'):
            #preauthorized = True
    
        #if(defsts == 'Authorized'):
            #preauthorized = True
            #authorized = True
        
  
        #writablflag = (not authorization) | (((not preauthorized) & (not authorized)&(not webadmin))|((webadmin)))
         
        #enddate = common.getdt(treatments[0].enddate)
        #formTreatment = SQLFORM.factory(
           #Field('patientmember', 'string',  label='Patient', default = fullname,\
                 #requires=[IS_NOT_EMPTY(),IS_IN_DB(db(db.vw_memberpatientlist.providerid == providerid), 'vw_memberpatientlist.fullname','%(fullname)s')],writable=False),
           #Field('xmemberid', 'string',  label='Member',default=memberid),
           #Field('treatment','string',label='Treatment No.', default=treatments[0].treatment),
           #Field('chiefcomplaint','string',label='Chief Complaint', default=treatments[0].chiefcomplaint,writable=writablflag),
           #Field('description','text', label='Description', default=treatments[0].description,writable=writablflag),
           #Field('quadrant','string', label='Quadrant(s)', default=''),
           #Field('tooth','string', label='Tooth/Teeth', default=''),
           #Field('startdate', 'date', label='From Date',default=treatments[0].startdate, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))),writable=writablflag),
           #Field('enddate', 'date', label='To Date',default=enddate, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))),writable=writablflag),
           #Field('status', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border ',_onchange='onstatuschange()'),label='Status',default=defsts, requires = IS_IN_SET(status.TREATMENTSTATUS),writable=False,readable=True),  
           #Field('ucrfee', 'double', label='Total UCR',default=totalactualtreatmentcost,writable=False),  
           #Field('treatmentcost', 'double', label='Total Treament Cost',default=totaltreatmentcost,writable=False),  
           #Field('copay', 'double', label='Total Copay',default=treatments[0].copay, writable = False),  
           #Field('inspay', 'double', label='Total Ins. Pays',default=treatments[0].inspay, writable=False),  
           #Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
           #Field('vwdentalprocedure', 'string',   label='Procedure ID'),
           #Field('vwdentalprocedurecode', 'string',   label='Procedure Code'),
           #Field('xaction', 'string', default = 'UpdateTreatment')
           #)    
     
        #doc = formTreatment.element('#no_table_doctor')
        #if(doc != None):
            #doc['_class'] = 'form-control'
            #doc['_style'] = 'width:100%'
    
        
        #xtreatment = formTreatment.element('input',_id='no_table_treatment')
        #if(xtreatment != None):
            #xtreatment['_class'] =  'form-control'
            #xtreatment['_type'] =  'text'
            #xtreatment['_autocomplete'] = 'off'     
            #xtreatment['_readonly'] = 'true'
            
        #xvwdentalprocedurecode = formTreatment.element('input',_id='no_table_vwdentalprocedurecode')
        #if(xvwdentalprocedurecode != None):
            #xvwdentalprocedurecode['_class'] =  'form-control '
            #xvwdentalprocedurecode['_placeholder'] = 'Enter Dental Procedure Code' 
            #xvwdentalprocedurecode['_autocomplete'] = 'off'         
            #xvwdentalprocedurecode['_style'] = 'width:100%'
        
        #xvwdentalprocedure = formTreatment.element('input',_id='no_table_vwdentalprocedure')
        #if(xvwdentalprocedure != None):
            #xvwdentalprocedure['_class'] =  'form-control '
            #xvwdentalprocedure['_placeholder'] = 'Enter Dental Procedure Name' 
            #xvwdentalprocedure['_autocomplete'] = 'off'         
            #xvwdentalprocedure['_style'] = 'width:100%'
     
        #xtooth = formTreatment.element('input',_id='no_table_tooth')
        #if(xtooth != None):
            #xtooth['_class'] =  'form-control '
            #xtooth['_placeholder'] = 'Enter Tooth Number' 
            #xtooth['_autocomplete'] = 'off'         
            #xtooth['_style'] = 'width:100%'
        
        #xquad = formTreatment.element('input',_id='no_table_quadrant')
        #if(xquad != None):
            #xquad['_class'] =  'form-control '
            #xquad['_placeholder'] = 'Enter Quadrant' 
            #xquad['_autocomplete'] = 'off'         
            #xquad['_style'] = 'width:100%'
    
        #if(writablflag):
            #formTreatment.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
            #formTreatment.element('textarea[name=description]')['_rows'] = 5
            #formTreatment.element('textarea[name=description]')['_class'] = 'form-control'
    
            #xstartdate = formTreatment.element('input',_id='no_table_startdate')
            #xstartdate['_class'] =  'input-group form-control form-control-inline date-picker'
            #xstartdate['_data-date-format'] = 'dd/mm/yyyy'
            #xstartdate['_autocomplete'] = 'off' 
        
            #xenddate = formTreatment.element('input',_id='no_table_enddate')
            #xenddate['_class'] =  'input-group form-control form-control-inline date-picker'
            #xenddate['_data-date-format'] = 'dd/mm/yyyy'
            #xenddate['_autocomplete'] = 'off' 
    
           
    
            #cc = formTreatment.element('input', _id='no_table_chiefcomplaint')
            #cc['_class'] = 'form-control'
            #cc['_style'] = 'width:100%'
            #cc['_type'] =  'text'
      
        
        ## procedures grid
        #query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True))
        #if((hmopatientmember == True) | (session.religare != None)):
            #fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription, db.vw_treatmentprocedure.relgrprocdesc, \
                       #db.vw_treatmentprocedure.procedurefee,db.vw_treatmentprocedure.inspays,db.vw_treatmentprocedure.copay,db.vw_treatmentprocedure.status,\
                       #db.vw_treatmentprocedure.treatmentdate, db.vw_treatmentprocedure.relgrproc)
    
    
            #headers={
                #'vw_treatmentprocedure.procedurecode':'Code',
                #'vw_treatmentprocedure.altshortdescription':'Description',
                #'vw_treatmentprocedure.relgrprocdesc':'Procedure Group',
                #'vw_treatmentprocedure.procedurefee':'Procedure Cost',
                #'vw_treatmentprocedure.inspays':'Insurance Pays',
                #'vw_treatmentprocedure.copay':'Co-Pay',
                #'vw_treatmentprocedure.status':'Status',
                #'vw_treatmentprocedure.treatmentdate':'Treatment Date'
            #}
            
            #db.vw_treatmentprocedure.relgrproc.writable = False
            #db.vw_treatmentprocedure.relgrproc.readable = False
        #else:
            #fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription, db.vw_treatmentprocedure.relgrprocdesc,\
                       #db.vw_treatmentprocedure.procedurefee,db.vw_treatmentprocedure.status,\
                       #db.vw_treatmentprocedure.treatmentdate,db.vw_treatmentprocedure.relgrproc)
            
            #headers={
                #'vw_treatmentprocedure.procedurecode':'Code',
                #'vw_treatmentprocedure.altshortdescription':'Description',
                #'vw_treatmentprocedure.relgrprocdesc':'Procedure Group',
                #'vw_treatmentprocedure.procedurefee':'Procedure Cost',
                #'vw_treatmentprocedure.status':'Status',
                #'vw_treatmentprocedure.treatmentdate':'Treatment Date'
            #}
            
            #db.vw_treatmentprocedure.relgrproc.writable = False
            #db.vw_treatmentprocedure.relgrproc.readable = False
            
        #if(writablflag):
            #links = [\
                    #dict(header=CENTER('Edit'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=30, _height=30),\
                                                                       #_href=URL("treatment","update_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin,hmopatientmember=hmopatientmember))))),
                    
                    #dict(header=CENTER('Complete'),body=lambda row: ((CENTER(A(IMG(_src="/my_pms2/static/img/complete_on.png",_width=30, _height=30),\
                                                                          #_href=URL("treatment","complete_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin))))\
                                                                    #if(row.status != 'Completed') else\
                                                                    #CENTER(A(IMG(_src="/my_pms2/static/img/complete_off.png",_width=30, _height=30),\
                                                                                                                                              #_href=URL("treatment","complete_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin))))))\
                                                                    
                                 #if(row.relgrproc == False) else\
                                 
                                 #((CENTER(A(IMG(_src="/my_pms2/static/img/religare_on.png",_width=30, _height=30),\
                                                                                                           #_href=URL("treatment","complete_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin))))\
                                 #if(row.status != 'Completed') else\
                                 #CENTER(A(IMG(_src="/my_pms2/static/img/religare_off.png",_width=30, _height=30),\
                                                                                                           #_href=URL("treatment","complete_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin))))))\
                                 
                         #),
                    #dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),\
                                                                          #_href=URL("treatment","delete_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin)))))
            #]
        #else:
            #links = [\
                    #dict(header=CENTER('Edit'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=30, _height=30),\
                                                                       #_href=URL("treatment","update_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin,hmopatientmember=hmopatientmember))))),
                    #dict(header=CENTER('Complete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/complete.png",_width=30, _height=30),\
                                                                          #_href=URL("treatment","complete_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin))))),
            #]
        
    
        #maxtextlengths = {'vw_treatmentprocedure.altshortdescription':100,'vw_treatmentprocedure.relgrprocdesc':100,'vw_treatmentprocedure.status':32}
        
        #exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
           
        #formProcedure = SQLFORM.grid(query=query,
                            #headers=headers,
                            #fields=fields,
                            #links=links,
                            #paginate=10,
                            #maxtextlengths=maxtextlengths,
                            #orderby=None,
                            #exportclasses=exportlist,
                            #links_in_grid=True,
                            #searchable=False,
                            #create=False,
                            #deletable=False,
                            #editable=False,
                            #details=False,
                            #user_signature=True
                           #)  
  
        #returnurl = URL('treatment','list_treatments',vars=dict(page=page,providerid=providerid,memberid=memberid,patientid=patientid))
        #if formTreatment.accepts(request,session=session,formname='formtreatment',keepvalues=True):
            #treatmentcost = float(common.getvalue(formTreatment.vars.treatmentcost))
            #doctorid = int(common.getid(formTreatment.vars.doctor))
            #docs = db(db.doctor.id == doctorid).select()
            #doctorname = docs[0].name
            
            #if(formTreatment.vars.status == 'Authorized'):
                #authorized = True
            #else:
                #authorized = False
            
            #db(db.treatment.id == treatmentid).update(\
                #treatment = formTreatment.vars.treatment,
                #chiefcomplaint = formTreatment.vars.chiefcomplaint,
                #description  = formTreatment.vars.description,
                #startdate = formTreatment.vars.startdate,
                #enddate = formTreatment.vars.enddate,
                #status = formTreatment.vars.status,
                #authorized = authorized,
                #actualtreatmentcost = 0,
                #treatmentcost = treatmentcost,
                #quadrant = '',
                #tooth = '',
                #dentalprocedure = 0, 
                #doctor = doctorid,
                #modified_on = datetime.date.today(),
                #modified_by = providerid,
            
            #)    
            
            
            #updatetreatmentcostandcopay(treatmentid,tplanid)
            #calculatecost(tplanid)
            #calculatecopay(db, tplanid,memberid)
            #calculateinspays(tplanid)
            #calculatedue(tplanid)
            
            #db.commit()                
        
            #db.treatmentnotes.update_or_insert(db.treatmentnotes.treatment == treatmentid, treatment = treatmentid, notes = formTreatment.vars.prescription)   
            
            #if(changeinnotes(currnotes, formTreatment.vars.description)):
                #common.lognotes(db,formTreatment.vars.description,treatmentid)
            
            #response.flash = "Treatment Details Updated!"
            
        #elif formTreatment.errors:
            #session.flash = "Error - Updating Treatment Report!" + str(formTreatment.errors)
            #redirect(returnurl)
            
    ##====== Notes Foem
    
    #dob = ""
    #age = ""
    #xgender = ""
    
    #if((rows[0].dob != None) & (rows[0].dob != "")):    
        #dob = common.getstring(rows[0].dob)
        #age = common.getstring(getage(rows[0].dob))
        
    #xgender = common.getstring(rows[0].gender)    
    
    #memrows = db(db.patientmember.id == memberid).select()
    #address = ""
    #telephone  = ""
    #if(len(memrows)>0):
        #addr1 = common.getstring(memrows[0].address1)
        #addr2 = common.getstring(memrows[0].address2)
        #addr3 = common.getstring(memrows[0].address3)
        #city = common.getstring(memrows[0].city)
        #st = common.getstring(memrows[0].st)
        #pin = common.getstring(memrows[0].pin)
        #address = addr1 + " " + addr2 + " " + addr3 + ",\r\n" + city + ", " + st + " " + pin
        #telephone = common.getstring(memrows[0].telephone)
    
    #notes = db((db.medicalnotes.patientid == patientid) & (db.medicalnotes.memberid == memberid)).select()
    #if(len(notes) < 0) :
        #redirect(returnurl)
        
    #if(len(notes)>0):
        #formNotes = SQLFORM.factory(
            #Field('patientmember', 'string',  label='Patient', default = fullname,writable=False),
            #Field('notesdate', 'date', label='To Date',default=datetime.date.today(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
            #Field('dob', 'date', label='To Date',default=rows[0].dob, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
            #Field('age', 'string', default=age),
            #Field('cell', 'string', default=common.getstring(rows[0].cell)),
            #Field('email', 'string', default=common.getstring(rows[0].email)),
            #Field('telephone', 'string', default=telephone),
            #Field('occupation', 'string', default=common.getstring(notes[0].occupation)),
            #Field('xgender', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form-control '),label='Gender',default=xgender, requires = IS_IN_SET(gender.GENDER)),
            #Field('address','text', label='Address', default=address),
            #Field('referer','string', label='Doctor/Fried', default=common.getstring(notes[0].referer)),
            #Field('resoff','string', label='Residence/Office', default=common.getstring(notes[0].resoff)),
            #Field('bp','boolean', default = common.getboolean(notes[0].bp)),
            #Field('diabetes','boolean', default = common.getboolean(notes[0].diabetes)),
            #Field('anaemia','boolean', default = common.getboolean(notes[0].anaemia)),
            #Field('epilepsy','boolean', default = common.getboolean(notes[0].epilepsy)),
            #Field('asthma','boolean', default = common.getboolean(notes[0].asthma)),
            #Field('sinus','boolean', default = common.getboolean(notes[0].sinus)),
            #Field('heart','boolean', default = common.getboolean(notes[0].heart)),
            #Field('jaundice','boolean', default = common.getboolean(notes[0].jaundice)),
            #Field('tb','boolean', default = common.getboolean(notes[0].tb)),
            #Field('cardiac','boolean', default = common.getboolean(notes[0].cardiac)),
            #Field('arthritis','boolean', default = common.getboolean(notes[0].arthritis)),
            #Field('anyother','boolean', default = common.getboolean(notes[0].anyother)),
            #Field('allergic','boolean', default = common.getboolean(notes[0].allergic)),
            #Field('excessivebleeding','boolean', default = common.getboolean(notes[0].excessivebleeding)),
            #Field('seriousillness','boolean', default = common.getboolean(notes[0].seriousillness)),
            #Field('hospitalized','boolean', default = common.getboolean(notes[0].hospitalized)),
            #Field('medications','boolean', default = common.getboolean(notes[0].medications)),
            #Field('surgery','boolean', default = common.getboolean(notes[0].surgery)),
            #Field('pregnant','boolean', default = common.getboolean(notes[0].pregnant)),
            #Field('breastfeeding','boolean', default = common.getboolean(notes[0].breastfeeding)),
            #Field('anyothercomplaint','text',represent=lambda v, r: '' if v is None else v, default=common.getstring(notes[0].anyothercomplaint)),
            #Field('chiefcomplaint','text',represent=lambda v, r: '' if v is None else v, default=common.getstring(notes[0].chiefcomplaint)),
            #Field('duration','text', represent=lambda v, r: '' if v is None else v, default=common.getstring(notes[0].duration)),
            #Field('is_active','boolean', default = True)
        #)  
    #else:
        #formNotes = SQLFORM.factory(
            #Field('patientmember', 'string',  label='Patient', default = fullname,writable=False),
            #Field('notesdate', 'date', label='To Date',default=datetime.date.today(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
            #Field('dob', 'date', label='To Date',default=rows[0].dob, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
            #Field('age', 'string', default=age),
            #Field('cell', 'string', default=common.getstring(rows[0].cell)),
            #Field('email', 'string', default=common.getstring(rows[0].email)),
            #Field('telephone', 'string', default=telephone),
            #Field('occupation', 'string', default=""),
            #Field('xgender', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form-control '),label='Gender',default="Male", requires = IS_IN_SET(gender.GENDER)),
            #Field('address','text', label='Address', default=""),
            #Field('referer','string', label='Doctor/Fried', default=""),
            #Field('resoff','string', label='Residence/Office', default=""),
            #Field('bp','boolean', default = ""),
            #Field('diabetes','boolean', default = ""),
            #Field('anaemia','boolean', default = ""),
            #Field('epilepsy','boolean', default = ""),
            #Field('asthma','boolean', default = ""),
            #Field('sinus','boolean', default = ""),
            #Field('heart','boolean', default = ""),
            #Field('jaundice','boolean', default = ""),
            #Field('tb','boolean', default = ""),
            #Field('cardiac','boolean', default = ""),
            #Field('arthritis','boolean', default = ""),
            #Field('anyother','boolean', default = ""),
            #Field('allergic','boolean', default = ""),
            #Field('excessivebleeding','boolean', default = ""),
            #Field('seriousillness','boolean', default = ""),
            #Field('hospitalized','boolean', default = ""),
            #Field('medications','boolean', default = ""),
            #Field('surgery','boolean', default = ""),
            #Field('pregnant','boolean', default = ""),
            #Field('breastfeeding','boolean', default = ""),
            #Field('anyothercomplaint','text',represent=lambda v, r: '' if v is None else v, default=""),
            #Field('chiefcomplaint','text',represent=lambda v, r: '' if v is None else v, default=""),
            #Field('duration','text', represent=lambda v, r: '' if v is None else v, default=""),
            #Field('is_active','boolean', default = True)
        #)  
        
    
    #formNotes.element('textarea[name=anyothercomplaint]')['_style'] = 'height:50px;line-height:1.0;'
    #formNotes.element('textarea[name=anyothercomplaint]')['_rows'] = 2
    #formNotes.element('textarea[name=anyothercomplaint]')['_class'] = 'form-control' 
    
    #formNotes.element('textarea[name=chiefcomplaint]')['_style'] = 'height:60px;line-height:1.0;'
    #formNotes.element('textarea[name=chiefcomplaint]')['_rows'] = 3
    #formNotes.element('textarea[name=chiefcomplaint]')['_class'] = 'form-control' 

    
    #formNotes.element('textarea[name=duration]')['_style'] = 'height:60px;line-height:1.0;'
    #formNotes.element('textarea[name=duration]')['_rows'] = 3
    #formNotes.element('textarea[name=duration]')['_class'] = 'form-control' 

    

    #xnotesdate = formNotes.element('input',_id='no_table_notesdate')
    #xnotesdate['_class'] =  'input-group form-control form-control-inline date-picker'
    #xnotesdate['_data-date-format'] = 'dd/mm/yyyy'
    #xnotesdate['_autocomplete'] = 'off'  

    
    #xdob = formNotes.element('input',_id='no_table_dob')
    #xdob['_class'] =  'input-group form-control form-control-inline date-picker'
    #xdob['_data-date-format'] = 'dd/mm/yyyy'
    #xdob['_autocomplete'] = 'off'  
    
    #xage = formNotes.element('input',_id='no_table_age')
    #xage['_class'] =  'form-control'
    #xage['_type'] =  'text'
    #xage['_placeholder'] = 'Enter Dental Tooth T1 to T32' 
    #xage['_autocomplete'] = 'off'     

    #xcell = formNotes.element('input',_id='no_table_cell')
    #xcell['_class'] =  'form-control'
    #xcell['_type'] =  'text'
    
    #xemail = formNotes.element('input',_id='no_table_email')
    #xemail['_class'] =  'form-control'
    #xemail['_type'] =  'text'
    
    #xtel = formNotes.element('input',_id='no_table_telephone')
    #xtel['_class'] =  'form-control'
    #xtel['_type'] =  'text'

    #xocc = formNotes.element('input',_id='no_table_occupation')
    #xocc['_class'] =  'form-control'
    #xocc['_type'] =  'text'

    #xref = formNotes.element('input',_id='no_table_referer')
    #xref['_class'] =  'form-control'
    #xref['_type'] =  'text'
    
    #xresoff = formNotes.element('input',_id='no_table_resoff')
    #xresoff['_class'] =  'form-control'
    #xresoff['_type'] =  'text'
    
    #formNotes.element('textarea[name=address]')['_style'] = 'height:100px;line-height:1.0;'
    #formNotes.element('textarea[name=address]')['_rows'] = 3
    #formNotes.element('textarea[name=address]')['_class'] = 'form-control'

    #if formNotes.accepts(request,session=session,formname='formnotes',keepvalues=True):
        
        #patientid = int(common.getid(request.vars.notes_patientid))
        #memberid = int(common.getid(request.vars.notes_memberid))
        #providerid = int(common.getid(request.vars.notes_providerid))
        
       

        
        #db.medicalnotes.update_or_insert(((db.medicalnotes.patientid == patientid) & (db.medicalnotes.memberid == memberid) & (db.medicalnotes.is_active == True)),
                                         #patientid = patientid,
                                         #memberid = memberid,
                                         #bp = common.getboolean(formNotes.vars.bp),
                                         #diabetes = common.getboolean(formNotes.vars.diabetes),
                                         #anaemia = common.getboolean(formNotes.vars.anaemia),
                                         #epilepsy = common.getboolean(formNotes.vars.epilepsy),
                                         #asthma = common.getboolean(formNotes.vars.asthma),
                                         #sinus = common.getboolean(formNotes.vars.sinus),\
                                         #heart = common.getboolean(formNotes.vars.heart),\
                                         #jaundice = common.getboolean(formNotes.vars.jaundice),\
                                         #tb = common.getboolean(formNotes.vars.tb),\
                                         #cardiac = common.getboolean(formNotes.vars.cardiac),\
                                         #arthritis = common.getboolean(formNotes.vars.arthritis),\
                                         #anyother = common.getboolean(formNotes.vars.anyother),\
                                         #allergic = True if request.vars.allergic == "1" else False,\
                                         #excessivebleeding = True if request.vars.excessivebleeding == "1" else False,\
                                         #seriousillness = True if request.vars.seriousillness == "1" else False,\
                                         #hospitalized = True if request.vars.hospitalized == "1" else False,\
                                         #medications = True if request.vars.medications == "1" else False,\
                                         #surgery = True if request.vars.surgery == "1" else False,\
                                         #pregnant = True if request.vars.pregnant == "1" else False,\
                                         #breastfeeding = True if request.vars.breastfeeding == "1" else False,\
                                         #anyothercomplaint = common.getstring(formNotes.vars.anyothercomplaint),\
                                         #chiefcomplaint = common.getstring(formNotes.vars.chiefcomplaint),\
                                         #duration = common.getstring(formNotes.vars.duration),\
                                         #occupation = common.getstring(formNotes.vars.occupation),\
                                         #referer = common.getstring(formNotes.vars.referer),\
                                         #resoff = common.getstring(formNotes.vars.resoff),\
                                         #is_active = True,\
                                         #created_on = datetime.date.today(),\
                                         #created_by = providerid,\
                                         #modified_on = datetime.date.today(),\
                                         #modified_by = providerid
                                         #)   
        #db.commit()
        #redirect(returnurl)
    #elif formNotes.errors:
        #response.flash = "Error Treatment Update " + str(formNotes.errors)
      
    
    
        

    ##===== End Notes
    
    
    ##===== Medical Test form and grid
    #formMedtest = SQLFORM.factory(
             #Field('testname', 'string',  label='Test', default = "Test ABC")
          #)  
       
    #medtestgrid = getmedtestgrid(patientid,providerid)

    #if formMedtest.accepts(request,session=session,formname='formmedtest',keepvalues=True):
        #i  = 0
    #elif formMedtest.errors:
        #response.flash = "Error in Medical Test " + str(formMedtest.errors)
     
        
        #j = 0    
    ##====== End of Medical Test
    
    ##====== Prescription Form and grid
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
        #response.flash = "Error in Prescription " + str(formPres.errors)
   

        #j = 0    
    ##===== End of Prescription
    
    
    ##==== Images
    
    
    #items_per_page = 4
    #limitby = ((imagepage)*items_per_page,(imagepage+1)*items_per_page)       
    
    #images = None
    #if(limitby > 0):
        #images = db((db.dentalimage.patient == patientid) & (db.dentalimage.provider == providerid) & (db.dentalimage.image != "") & \
                      #(db.dentalimage.image != None) & (db.dentalimage.is_active == True)).select(\
                        #db.dentalimage.id,db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                        #db.dentalimage.patienttype,db.dentalimage.patientname,db.dentalimage.description,db.dentalimage.is_active,db.vw_memberpatientlist.patientmember,\
                        #left=[db.vw_memberpatientlist.on(db.dentalimage.patient == db.vw_memberpatientlist.patientid)],\
                              #limitby=limitby, orderby = db.vw_memberpatientlist.patientmember | ~db.dentalimage.patienttype | ~db.dentalimage.id                      
                      #)
    #else:
        #images = db((db.dentalimage.patient == patientid) & (db.dentalimage.provider == providerid) & (db.dentalimage.image != "") & \
                      #(db.dentalimage.image != None) & (db.dentalimage.is_active == True)).select(
                        #db.dentalimage.id,db.dentalimage.title,db.dentalimage.image,db.dentalimage.tooth,db.dentalimage.quadrant,db.dentalimage.imagedate,\
                        #db.dentalimage.patienttype,db.dentalimage.patientname,db.dentalimage.description,db.dentalimage.is_active,db.vw_memberpatientlist.patientmember,\
                        #left=[db.vw_memberpatientlist.on(db.dentalimage.patient == db.vw_memberpatientlist.patientid)],\
                              #orderby = db.vw_memberpatientlist.patientmember | ~db.dentalimage.patienttype | ~db.dentalimage.id
                    #)
                        
    #formImage = SQLFORM.factory(
               #Field('title', 'string',  label='Image Title', default = "Test ABC")
            #)     
    ##==== End of Images
          
       
    ##==== Dental Chart
    ##newchart = common.getboolean(request.vars.newchart)
    ##appPath = request.folder    
    ##srcchartfile = os.path.join(appPath, 'static/charts/default','dentalchart.jpg') 
    ##destfilename  = str(tplanid) + str(treatmentid) + patientname.replace(" ","").lower() + ".jpg"
    ##destchartfile = os.path.join(appPath, 'static/charts',destfilename)   
    ##if((newchart == True) | (not os.path.isfile(destchartfile))):
        ##copyfile(srcchartfile,destchartfile);
    ##chartfile = "../static/charts/" + destfilename
    ##charturl = URL('static', 'charts/' + destfilename)

    ##chartnotes=""
    ##chartdate= datetime.date.today()
    ##charttitle=str(tplanid) + "_" + str(treatmentid) + "_" + patientname
    
    ##charts = db((db.dentalchart.provider == providerid) & (db.dentalchart.treatmentplan == tplanid) & (db.dentalchart.treatment == treatmentid) & (db.dentalchart.is_active == True)).select()
    ##if(len(charts) > 0):
        ##chartnotes = common.getstring(charts[0].description)
        ##chartdate = common.getdt(charts[0].chartdate)
        ##charttitle = common.getstring(charts[0].title)
    
    ##formDentalChart = SQLFORM.factory(
                   ##Field('charttitle', 'string',  label='Title',default=chartnotes),
                   ##Field('chartdate', 'date',  label='Date',default=chartdate, requires=IS_DATE(format=('%d/%m/%Y'))),
                   ##Field('chartnotes','text', label='Description', default=chartnotes),
                   ##)            
    ##formDentalChart.element('textarea[name=chartnotes]')['_style'] = 'width:80%;line-height:1.0;'
          
    ##xcharttitle = formDentalChart.element('input',_id='no_table_charttitle')
    ##xcharttitle['_class'] =  'form-control'
    ##xcharttitle['_type'] =  'text'
    ##xcharttitle['_style'] ='width:80%'
    ##xcharttitle['_autocomplete'] = 'off' 
    
    ##xchartdate = formDentalChart.element('input',_id='no_table_chartdate')
    ##xchartdate['_class'] =  'input-group form-control form-control-inline date-picker'
    ##xchartdate['_style'] ='width:80%'
    ##xchartdate['_autocomplete'] = 'off'                     
      
    ##if formDentalChart.accepts(request,session=session,formname='formdentalchart',keepvalues=True):
        ##i = 0
    ##elif formDentalChart.errors:
        ##j= 0
    ##==== End Dental Chart
    
    ##membername = <responsible party enrolled member's fname lname> patientname = <Patient's fname, lname> patientmember = <Member/Patient Code>

    #return dict(formTreatment=formTreatment, formProcedure=formProcedure,formPres=formPres,formNotes=formNotes, formMedtest=formMedtest, medtestgrid=medtestgrid, prescriptions=prescriptions,\
                #images = images,formImage=formImage,\
                #page=page, memberpage=0, imagepage=imagepage,procedureid=procedureid,\
                #providerid=providerid, providername=providername,doctorid=doctorid,doctorname=docs[0].name,\
                #patientmember=patientmember, memberid=memberid,membername=membername, patientid=patientid,patientname=patientname, hmopatientmember=hmopatientmember,\
                #treatment=treatment,treatmentid=treatmentid,tplanid=tplanid,medicalalerts=medicalalerts,\
                #authorization=authorization,authorizationurl=authorizationurl,writablflag=writablflag,
                #preauthorized=preauthorized,preauthorizeerror=preauthorizeerror,authorizeerror=authorizeerror,authorized=authorized,webadmin=webadmin,returnurl=returnurl,\
                #freetreatment=freetreatment,newmember=newmember
                #)        
            


#=URL('treatment','patient_treatment',vars=dict(page=page,providerid=providerid))
@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def patient_treatment():
    
    page       = int(common.getpage(request.vars.page)) 

    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])    
    providername = provdict["providername"]    
    
    form = SQLFORM.factory(
                 Field('patientmember1', 'string',  default='', label='Patient'),
                 Field('xpatientmember1', 'string', default='', label='XPatient')
                 
      )
         
    xpatientmember = form.element('#no_table_patientmember1')
    xpatientmember['_class'] = 'form-control'
    xpatientmember['_placeholder'] = 'Enter Patient Name - First Name Last Name'
    xpatientmember['_autocomplete'] = 'off'     
    
    returnurl = URL('treatment','list_treatments', vars=dict(page=page,providerid=providerid))
    
    if form.accepts(request,session,keepvalues=True):
        patientmember = ""
        memberid  = 0
        patientid = 0
        memberref = ""
        fullname = ""
        patient = ""
        
        r = db((db.vw_memberpatientlist.patient == common.getstring(form.vars.xpatientmember1).strip()) & (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).select()
        if(len(r) > 0):
            memberid = int(common.getid(r[0].primarypatientid))
            patientid = int(common.getid(r[0].patientid))
            redirect(URL('treatment','new_treatment',vars=dict(page=page,providerid=providerid,patientid=patientid,memberid=memberid,treatmentid=0,tplanid=0)))
        else:
            session.flash = 'Error - searching patient for new treatment'
            redirect(returnurl)
    elif form.errors:
        session.flash = "Error - searching patient for new treatment " + str(form.errors)
        redirect(returnurl)
            
    return dict(form=form,  page=page,returnurl=returnurl,providername=providername, providerid=providerid)
    



#=URL('treatment','new_treatment',vars=dict(page=page,providerid=providerid,memberid=memberid,patientid=patientid,tplanid=0,treatmentid=0))
@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def new_treatment():

    #provider : logged in
    provdict = common.getprovider(auth, db)
    providername  = provdict["providername"]
    providerid = provdict["providerid"]
    clinicid = session.clinicid
    
    #default attending doctor to owner doctor
    doctorid = int(common.getid(request.vars.doctorid))
  
    if(doctorid == 0):
        r = db((db.doctor.providerid == providerid) & (db.doctor.practice_owner == True)  & (db.doctor.is_active == True) ).select()
        if(len(r) > 0):
            doctorid = common.getid(r[0].id)    

        
    #page
    page       = int(common.getpage(request.vars.page))
    
    #memberid, patientid, member details
    memberid   = int(common.getid(request.vars.memberid))
    patientid  = int(common.getid(request.vars.patientid))
    newmember     = False
    freetreatment = True
    patienttype = 'P'
    procedurepriceplancode = 'PREM103'
    patientname = ""
    fullname = ""
    patientmember = ""
    title = ""
    
    r = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid)  & (db.vw_memberpatientlist.primarypatientid == memberid)  & (db.vw_memberpatientlist.is_active== True)).select()
    if(len(r) > 0):
        patientmember = r[0].patientmember
        title = r[0].title
        patientname = r[0].patient   #fname lname : patientmember
        fullname = r[0].fullname     #fullname
        newmember = common.getboolean(r[0].newmember)
        freetreatment = common.getboolean(r[0].freetreatment)
        patienttype = r[0].patienttype
        

    #treatment, tplan details
    #treatmentid = int(common.getid(request.vars.treatmentid))
    #tplanid     = int(common.getid(request.vars.tplanid))

    #Create a new TreatmentPlan
    timestr = datetime.datetime.today().strftime("%d-%m-%Y_%H:%M:%S")
    tplan = "TP" + str(patientmember)  + "_" + timestr
    tplanid = db.treatmentplan.insert(
        treatmentplan = tplan,
        startdate = common.getISTFormatCurrentLocatTime(),
        enddate = common.getISTFormatCurrentLocatTime(),
        provider = providerid,
        primarypatient = memberid,
        patient = patientid,
        pattitle = title,
        patienttype = patienttype,
        patientname = fullname,
        
        status = 'Started',
        totaltreatmentcost = 0,
        totalcopay = 0,
        totalinspays = 0,
        totalpaid = 0,
        totaldue = 0,
        totalcopaypaid = 0,
        totalinspaid  = 0,             
        is_active = True,
        created_on = common.getISTFormatCurrentLocatTime(),
        created_by = 1,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by =1 

    )

    
    
    #Treatment
    count = db(db.treatment.provider == providerid).count()
    treatment = "TR" + str(patientmember) + str(count).zfill(4)      # + "_" + timestr
    treatmentid = db.treatment.insert(
        
        treatment = treatment,
        description = '',
        startdate = common.getISTFormatCurrentLocatTime(),
        enddate = common.getISTFormatCurrentLocatTime(),
        status ='Started',
        treatmentplan = tplanid,
        provider = providerid,
        clinicid = clinicid,
        dentalprocedure = 0,
        doctor = doctorid,
        quadrant = 0,
        tooth    = 0,
        treatmentcost = 0,
        actualtreatmentcost = 0,  #UCR cost
        copay = 0,
        inspay = 0,
        companypay = 0,
        is_active = True,
        created_on = common.getISTFormatCurrentLocatTime(),
        created_by = 1,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by =1 
        
    
    )
    
    db.treatmentplan_patient.insert(treatmentplan = tplanid, patientmember = memberid)
    
    
    #update treatment with increased treatment cost
    updatetreatmentcostandcopay(treatmentid,tplanid)
    common.dashboard(db,session,providerid)
    session.flash = "New Treatment Added!"
    redirect(URL('treatment','update_treatment',vars=dict(page=page,providerid=providerid,treatmentid=treatmentid)))
    
    return dict()


#URL("treatment","update_procedure",vars=dict(page=page,providerid=providerid,treatmentprocedureid=row.id,patientid=patientid,memberid=memberid,tplanid=tplanid,treatmentid=treatmentid)
@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def update_procedure():



    procedurecode = ""
    procedure = ""
    quadrant  = ""
    tooth = ""
    ucr = 0
    procedurecost = 0
    copay = 0
    inspays = 0
    companypays = 0
    remarks = ""
    procstatus = 'Started'
     
    authorization = common.getboolean(request.vars.authorization)
    preauthorized = common.getboolean(request.vars.preauthorized)
    authorized = common.getboolean(request.vars.authorized)
    webadmin =common.getboolean(request.vars.webadmin)
    hmopatientmember =common.getboolean(request.vars.hmopatientmember)   
       
    page       = int(common.getpage(request.vars.page))
 
    #provider : logged in
    provdict = common.getprovider(auth, db)
    providername  = provdict["providername"]
    providerid = int(common.getid(provdict["providerid"]))
    
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    
    treatmentid = int(common.getid(request.vars.treatmentid))
    
    tplanid = int(common.getid(request.vars.tplanid))
    
    treatmentprocedureid = int(common.getid(request.vars.treatmentprocedureid))    
    
    
    trtmnts = db(db.treatment.id == treatmentid).select(db.treatment.treatment,db.doctor.name,left=db.doctor.on(db.doctor.id==db.treatment.doctor))
    
    treatment = common.getstring(trtmnts[0].treatment.treatment) if(len(trtmnts) == 1) else 0
    doctorname = common.getstring(trtmnts[0].doctor.name)  if(len(trtmnts) == 1) else 0
    
    procs = db((db.vw_treatmentprocedure.id == treatmentprocedureid)  & (db.vw_treatmentprocedure.is_active == True)).select()
    
    if(len(procs)>0):
        procedurecode = common.getstring(procs[0].procedurecode)
        procedure = common.getstring(procs[0].altshortdescription)
        quadrant = common.getstring(procs[0].quadrant)
        tooth = common.getstring(procs[0].tooth)
        ucr = float(common.getvalue(procs[0].ucrfee))
        procedurecost = float(common.getvalue(procs[0].procedurefee))
        copay = float(common.getvalue(procs[0].copay))
        inspays = float(common.getvalue(procs[0].inspays))
        companypays = float(common.getvalue(procs[0].companypays))
        procstatus = common.getstring(procs[0].status)
        procstatus = procstatus if((procstatus != None) & (procstatus != "")) else 'Started'
        remarks = common.getstring(procs[0].remarks)
        
    
    writablflag = ( ((procstatus == 'Started')&( not hmopatientmember)) |  webadmin)
    writablflag1 = ( ((procstatus == 'Started')) | webadmin)  #for tooth and quadrant
        
        
    formProcedure = SQLFORM.factory(
       Field('procedurecode','string', label='Procedure Code', default=procedurecode, writable=False),
       Field('procedure','string', label='Procedure', default=procedure, writable=False),
       Field('quadrant','string', label='Quadrant(s)', default=quadrant,  writable = writablflag1),
       Field('tooth','string', label='Tooth/Teeth', default=tooth, writable = writablflag1),
       Field('procstatus', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border '),label='Status', default=procstatus, requires = IS_IN_SET(status.TREATMENTSTATUS)),  
       Field('remarks','text', label='Tooth/Teeth', default=remarks, writable = writablflag1),
       Field('ucr', 'double', label='UCR',default=ucr,writable=False),  
       Field('procedurecost', 'double', label='Procedure Cost',default=procedurecost, writable = writablflag),  
       Field('copay', 'double', label='Total Copay',default=copay, writable = writablflag),  
       Field('inspays', 'double', label='Total Ins. Pays',default=inspays, writable = writablflag),  
       Field('companypays', 'double', label='Total Ins. Pays',default=companypays, writable = writablflag)
       )    
    
  
    if(writablflag1):
        formProcedure.element('textarea[name=remarks]')['_style'] = 'height:100px;line-height:1.0;'
        formProcedure.element('textarea[name=remarks]')['_rows'] = 5
        formProcedure.element('textarea[name=remarks]')['_class'] = 'form-control'        
        
        xquad = formProcedure.element('#no_table_quadrant')
        xquad['_class'] = 'form-control'
        xquad['_autocomplete'] = 'off' 
    
        xtooth = formProcedure.element('#no_table_tooth')
        xtooth['_class'] = 'form-control'
        xtooth['_autocomplete'] = 'off'         
       

    if(writablflag):

        xcopay = formProcedure.element('#no_table_copay')
        xcopay['_class'] = 'form-control'
        xcopay['_autocomplete'] = 'off' 
    
        xinspays = formProcedure.element('#no_table_inspays')
        xinspays['_class'] = 'form-control'
        xinspays['_onchange'] = 'totalcalculation()'
        xinspays['_autocomplete'] = 'off' 
    
        xproc = formProcedure.element('#no_table_procedurecost')
        xproc['_class'] = 'form-control'
        xproc['_onchange'] = 'totalcalculation()'
        xproc['_autocomplete'] = 'off' 
        
        
    returnurl = URL('treatment','update_treatment',vars=dict(page=page,providerid=providerid,treatmentid=treatmentid))
    
    if formProcedure.accepts(request,session,keepvalues=True):
        
        
        if(formProcedure.vars.procstatus == 'Authorized'):
            authorized = True
        
        if(writablflag):
            db(db.treatment_procedure.id == treatmentprocedureid).update(\
                quadrant = common.getstring(formProcedure.vars.quadrant),\
                tooth = common.getstring(formProcedure.vars.tooth),\
                status = common.getstring(formProcedure.vars.procstatus),\
                authorized = authorized,
                procedurefee = float(common.getvalue(formProcedure.vars.procedurecost)),\
                inspays = float(common.getvalue(formProcedure.vars.inspays)),\
                copay = float(common.getvalue(formProcedure.vars.copay)),\
                remarks = common.getstring(formProcedure.vars.remarks)
            )
        else:
            db(db.treatment_procedure.id == treatmentprocedureid).update(\
                quadrant = common.getstring(formProcedure.vars.quadrant),\
                tooth = common.getstring(formProcedure.vars.tooth),\
                status = common.getstring(formProcedure.vars.procstatus),\
                authorized = authorized,
                remarks = common.getstring(formProcedure.vars.remarks)
            )
            
        
        updatetreatmentcostandcopay(treatmentid,tplanid)
        #calculatecost(tplanid)
        #calculatecopay(db, tplanid,memberid)
        #calculateinspays(tplanid)
        #calculatedue(tplanid)        
        #common.dashboard(db,session,providerid) 
        
        if(changeinnotes(remarks, formProcedure.vars.remarks)):
                        common.lognotes(db,formProcedure.vars.remarks,treatmentid)        

        
       
        
        session.flash = "Procedure Updated Successfully"
        redirect(returnurl)
    elif formProcedure.errors:
        session.flash = "Error Updating Procedure " + str(formProcedure.errors)
       
        redirect(returnurl)
        
    return dict(formProcedure=formProcedure, page=page,providerid=providerid, providername=providername, treatmentprocedureid=treatmentprocedureid,hmopatientmember=hmopatientmember,\
                patientid=patientid,memberid=memberid,treatmentid=treatmentid,returnurl=returnurl,writablflag=writablflag,authorization=authorization,preauthorized=preauthorized,authorized=authorized,webadmin=webadmin)





def add_proceduregrid():
    #x  = datetime.datetime.now()
    logger.loggerpms2.info("===================Enter Add_procedure=======================================")
    auth = current.auth
    #check whether webadmin login
    impersonated = auth.user.impersonated
   
    #provider : logged in
    providerid = int(common.getid(request.vars.providerid))
   
    #page
    page       = common.getpage(request.vars.page)
    imagepage  = 1
 
    tooth = common.getstring(request.vars.tooth)
    quadrant = common.getstring(request.vars.quadrant)
    
    procedurecode = common.getstring(request.vars.vwdentalprocedurecode)
    #treatmentid
    treatmentid = int(common.getid(request.vars.treatmentid))
    treatment = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select(\
        db.treatment.status,\
        db.treatmentplan.id,db.treatmentplan.primarypatient, db.treatmentplan.patient,\
        db.vw_memberpatientlist.procedurepriceplancode,\
        left = [db.treatmentplan.on(db.treatmentplan.id == db.treatment.treatmentplan),\
                db.vw_memberpatientlist.on((db.vw_memberpatientlist.primarypatientid==db.treatmentplan.primarypatient)&\
                                           (db.vw_memberpatientlist.patientid==db.treatmentplan.patient)&\
                                           (db.vw_memberpatientlist.providerid==db.treatmentplan.provider))]
        )
    
    tplanid = int(common.getid(treatment[0].treatmentplan.id)) if(len(treatment) == 1) else 0
    memberid = int(common.getid(treatment[0].treatmentplan.primarypatient)) if(len(treatment) == 1) else 0
    patientid = int(common.getid(treatment[0].treatmentplan.patient)) if(len(treatment) == 1) else 0
    #procedurepriceplancode = treatment[0].vw_memberpatientlist.procedurepriceplancode if(len(treatment) == 1) else "PREMWALKIN"
    #procedurepriceplancode = mdputils.getprocedurepriceplancodeformember(db,providerid, memberid, patientid) 
    status = common.getstring(treatment[0].treatment.status)
    status = status if(status != "") else "Started"    
    #procs = db((db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode) &\
               #(db.vw_procedurepriceplan.procedurecode == request.vars.vwdentalprocedurecode)).select(\
                #db.vw_procedurepriceplan.id,\
                #db.vw_procedurepriceplan.ucrfee,\
                #db.vw_procedurepriceplan.procedurefee,\
                #db.vw_procedurepriceplan.inspays,\
                #db.vw_procedurepriceplan.copay,\
                #db.vw_procedurepriceplan.companypays,\
                #db.vw_procedurepriceplan.relgrproc,\
                #db.vw_procedurepriceplan.remarks\
               #)
 
    #procedurepriceplanid = int(common.getid(procs[0].id))  if(len(procs) >= 1) else 0
    ##get provider from treatment
    t = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
    providerid = int(common.getid(t[0].provider if (len(t)>0) else 0 ))
    treatmentdate = t[0].startdate if (len(t)>0) else common.getISTFormatCurrentLocatDate()
    
    #get region code
    provs = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.groupregion)
    regionid = int(common.getid(provs[0].groupregion)) if(len(provs) == 1) else 1
    regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select(db.groupregion.groupregion)
    regioncode = common.getstring(regions[0].groupregion) if(len(regions) == 1) else "ALL"
        
    ## get patient's company
    pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.company,db.vw_memberpatientlist.hmoplan)
    companyid = int(common.getid(pats[0].company)) if(len(pats) == 1) else 0
    companys = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
    companycode = common.getstring(companys[0].company) if(len(companys) == 1) else "PREMWALKIN"
    
    
    ##for backward compatibility determine procedurepriceplancode from member's plan at the time of registration
    hmoplanid = int(common.getid(pats[0].hmoplan)) if(len(pats) == 1) else 0  #this is the patient's previously assigned plan-typically at registration
    hmoplans = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode)
    hmoplancode = common.getstring(hmoplans[0].hmoplancode) if(len(hmoplans) == 1) else "PREMWALKIN"
    r = db(
           (db.provider_region_plan.companycode == companycode) &\
           (db.provider_region_plan.plancode == hmoplancode) &\
           ((db.provider_region_plan.regioncode == regioncode)|(db.provider_region_plan.regioncode == 'ALL')) &\
           (db.provider_region_plan.is_active == True)).select()
    plancode = r[0].policy if(len(r) == 1) else "PREMWALKIN"
    
    #Using new pricing engine  12/10/2021
    avars = {}
    avars["region_code"] = regioncode
    avars["treatment_id"] = treatmentid
    avars["company_code"] = companycode
    avars["procedure_code"] = procedurecode
    avars["plan_code"] = plancode
    
    pricingObj = mdprules.Pricing(db)
    rspobj = json.loads(pricingObj.Get_Procedure_Fees(avars))
    
    
    ucrfee = float(common.getkeyvalue(rspobj,"ucrfee",0))
    procedurefee = float(common.getkeyvalue(rspobj,"procedurefee",0))
    copay = float(common.getkeyvalue(rspobj,"copay",0))
    inspays = float(common.getkeyvalue(rspobj,"inspays",0))
    companypays = float(common.getkeyvalue(rspobj,"companypays",0))
    walletamount = float(common.getkeyvalue(rspobj,"walletamount",0))
    discount_amount = float(common.getkeyvalue(rspobj,"discount_amount",0))
    is_free = bool(common.getkeyvalue(rspobj,"is_free",False))
    active = bool(common.getkeyvalue(rspobj,"active",True))
    authorizationrequired = bool(common.getkeyvalue(rspobj,"authorizationrequired",False))
    
    voucher_code = common.getkeyvalue(rspobj,"voucher_code","")
    remarks = common.getkeyvalue(rspobj,"remarks","")
    procedurepriceplancode = common.getkeyvalue(rspobj,"procedurepriceplancode","")
    
    procs = db((db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode) &\
               (db.vw_procedurepriceplan.procedurecode == procedurecode)).select(\
                   db.vw_procedurepriceplan.id,\
                   db.vw_procedurepriceplan.relgrproc\
               )

    procedurepriceplanid = 0
    if(len(procs)>0):
        procedurepriceplanid = int(common.getid(procs[0].id))
        balance = 0
        trxamount = 0        
        if((session.religare == True) & (common.getboolean(procs[0].relgrproc)==True)):
            balance = 0 if session.religarebalance==None else float(common.getvalue(session.religarebalance))
            trxamount = min(inspays,balance)
            copay = copay + abs(inspays - trxamount)
            inspays = trxamount
            session.religarebalance = abs(balance - trxamount)
    
    tpid = 0
    if(active == True):
        tpid = db.treatment_procedure.insert(treatmentid = treatmentid, dentalprocedure = procedurepriceplanid,status=status,\
                                        ucr = ucrfee, procedurefee=procedurefee, copay=copay,inspays=inspays,companypays=companypays,\
                                        tooth=tooth,quadrant=quadrant,remarks=remarks,voucher_code=voucher_code,\
                                        walletamount=walletamount,discount_amount=discount_amount,treatmentdate = treatmentdate)
        db.commit() 
        session.flash = "New Procedure Added!"
    
    else:
        session.flash = "Procedure not added!"
    
    booking_amount = account.get_booking_amount(db, treatmentid)
    tax = account.get_tax_amount(db, copay)
    if(booking_amount > 0):
        db(db.treatment_procedure.id == tpid).update(copay = float(common.getvalue(tax["posttaxamount"])))
        db.commit()
   
  
    account.updatetreatmentcostandcopay(db,auth.user,treatmentid)
    redirecturl = URL("treatment","update_treatment",vars=dict(providerid=providerid,treatmentid=treatmentid,page=page,imagepage=imagepage))
    
    redirect(redirecturl)

    return dict()


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def add_procedure():

    #logger.logger.info("===================Enter Add_procedure=======================================")
    #logsql = "INSERT INTO logtable (logerror, created_on) values ('Enter Add Procedure', NOW())"
    #db.executesql(logsql)
    
    
    #provider : logged in
    provdict = common.getprovider(auth, db)
    providername  = provdict["providername"]
    providerid = int(common.getid(provdict["providerid"]))
    
    doctorid = int(common.getid(request.vars.doctorid))

    if(doctorid == 0):
        r = db((db.doctor.providerid == providerid) & (db.doctor.practice_owner == True)  & (db.doctor.is_active == True) ).select()
        if(len(r) > 0):
            doctorid = common.getid(r[0].id)
   
    #page
    page       = int(common.getpage(request.vars.page))
    
    #memberid, patientid
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    membername = common.getstring(request.vars.membername)
    patientname = common.getstring(request.vars.patientname)
    fullname = common.getstring(request.vars.fullname)
    newmember = False
    freetreatment = True
    
    treatmentid = int(common.getid(request.vars.treatmentid))
    tplanid = int(common.getid(request.vars.tplanid))
    
    treatments = db(db.treatment.id == treatmentid).select()
    treatmentcost = 0
    actualtreatmentcost = 0
    treatment = ""
    if(len(treatments)>0):
        treatment = common.getstring(treatments[0].treatment)
        treatmentcost = float(common.getvalue(treatments[0].treatmentcost))
        actualtreatmentcost = float(common.getvalue(treatments[0].actualtreatmentcost))
    
    patienttype = 'P'
    procedurepriceplancode = 'PREM103'
    hmopatientmember = True
    r = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid)  & (db.vw_memberpatientlist.primarypatientid == memberid)  & (db.vw_memberpatientlist.is_active== True)).select()
    if(len(r) > 0):
        patientname = r[0].patient   #fname lname : patientmember
        fullname = r[0].fullname     #fullname
        newmember = common.getboolean(r[0].newmember)          
        freetreatment = common.getboolean(r[0].freetreatment)
        patienttype = r[0].patienttype
        procedurepriceplancode = r[0].procedurepriceplancode
        hmopatientmember = r[0].hmopatientmember
   
   
    #logger.logger.info("=procedurepriceplancode ===" + procedurepriceplancode)
    #logsql = "INSERT INTO logtable (logerror, created_on) values ('" + procedurepriceplancode + "', NOW())"
    
    #db.executesql(logsql)
    
    procquery = db((db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode) & (db.vw_procedurepriceplan.is_active == True))
    
    formTreatment = None
    if(newmember == False):
        formTreatment = SQLFORM.factory(
           Field('patientmember', 'string',   label='Patient',default=fullname,requires=[IS_NOT_EMPTY(),IS_IN_DB(db(db.vw_memberpatientlist.providerid == providerid), 'vw_memberpatientlist.fullname','%(fullname)s')]),
           Field('xpatientmember', 'string',  default=patientname),
           Field('xfullname', 'string', writable=False, default = fullname),
           Field('xmemberid', 'string',  label='Member',default=memberid),
           Field('treatment','string', label='Treatment ID', default=''),
           Field('description','text', label='Description', default=''),
           Field('quadrant','string', label='Quadrant(s)', default=''),
           Field('tooth','string', label='Tooth/Teeth', default=''),
           Field('startdate', 'date', label='From Date',default=datetime.date.today(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
           Field('enddate', 'date', label='To Date',requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
           Field('status', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border '),label='Status',default='Started', requires = IS_IN_SET(status.TREATMENTSTATUS)),  
           Field('actualtreatmentcost', 'double', label='Total Treament Cost',default=actualtreatmentcost),  
           Field('treatmentcost', 'double', label='Total Treament Cost',default=treatmentcost,writable=False),  
           Field('copay', 'double', label='Total Copay',default=0.00, writable = False),  
           Field('inspay', 'double', label='Total Ins. Pays',default=0.00, writable=False),  
           Field('doctor',  widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
           Field('vwdentalprocedure', 'string',   label='Procedure ID',requires=[IS_NOT_EMPTY(),IS_IN_DB(procquery,'vw_procedurepriceplan.altshortdescription','%(altshortdescription)s')]),
           Field('vwdentalprocedurecode', 'string',   label='Procedure Code',requires=[IS_NOT_EMPTY(),IS_IN_DB(procquery,'vw_procedurepriceplan.procedurecode','%(procedurecode)s')])
           )    
        
    else:
        if(freetreatment == False):
            x999query = db((db.vw_procedurepriceplan_x999.procedurepriceplancode == procedurepriceplancode) & (db.vw_procedurepriceplan_x999.is_active == True))
                
            formTreatment = SQLFORM.factory(
               Field('patientmember', 'string',  label='Patient',default=fullname,requires=[IS_NOT_EMPTY(),IS_IN_DB(db(db.vw_memberpatientlist.providerid == providerid), 'vw_memberpatientlist.fullname','%(fullname)s')]),
               Field('xpatientmember', 'string',  default=patientname),
               Field('xfullname', 'string', default = fullname),
               Field('xmemberid', 'string',  label='Member',default=memberid),
               Field('treatment','string',label='Treatment ID', default=''),
               Field('description','text', label='Description', default=''),
               Field('quadrant','string', label='Quadrant(s)', default=''),
               Field('tooth','string', label='Tooth/Teeth', default=''),
               Field('startdate', 'date', label='From Date',default=datetime.date.today(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
               Field('enddate', 'date', label='To Date',requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
               Field('status', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border '),label='Status',default='Started', requires = IS_IN_SET(status.TREATMENTSTATUS)),  
               Field('actualtreatmentcost', 'double', label='Total Treament Cost',default=actualtreatmentcost),  
               Field('treatmentcost', 'double', label='Total Treament Cost',default=treatmentcost, writable = False),  
               Field('copay', 'double', label='Total Copay',default=0.00, writable = False),  
               Field('inspay', 'double', label='Total Ins. Pays',default=0.00, writable=False),  
               Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
               Field('vwdentalprocedure', 'string',   label='Procedure ID',requires=[IS_NOT_EMPTY(),IS_IN_DB(x999query,'vw_procedurepriceplan_x999.altshortdescription','%(altshortdescription)s')]),
               Field('vwdentalprocedurecode', 'string',   label='Procedure Code',requires=[IS_NOT_EMPTY(),IS_IN_DB(procquery,'vw_procedurepriceplan.procedurecode','%(procedurecode)s')])
               )    
            
        else:
            formTreatment = SQLFORM.factory(
               Field('patientmember', 'string',  label='Patient',default=fullname,requires=[IS_NOT_EMPTY(),IS_IN_DB(db(db.vw_memberpatientlist.providerid == providerid), 'vw_memberpatientlist.fullname','%(fullname)s')]),
               Field('xpatientmember', 'string', default=patientname),
               Field('xfullname', 'string', default = fullname),
               Field('xmemberid', 'string',  label='Member',default=memberid),
               Field('treatment','string',label='Treatment ID', default=''),
               Field('description','text', label='Description', default=''),
               Field('quadrant','string', label='Quadrant(s)', default=''),
               Field('tooth','string', label='Tooth/Teeth', default=''),
               Field('startdate', 'date', label='From Date',default=datetime.date.today(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
               Field('enddate', 'date', label='To Date',requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
               Field('status', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form-control '),label='Status',default='Started', requires = IS_IN_SET(status.TREATMENTSTATUS)),  
               Field('actualtreatmentcost', 'double', label='Total Treament Cost',default=actualtreatmentcost),  
               Field('treatmentcost', 'double', label='Total Treament Cost',default=treatmentcost,writable = False),  
               Field('copay', 'double', label='Total Copay',default=0.00, writable = False),  
               Field('inspay', 'double', label='Total Ins. Pays',default=0.00, writable=False),  
               Field('doctor', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default=doctorid, label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.stafftype == 'Doctor')&(db.doctor.is_active==True)), 'doctor.id', '%(name)s')),
               Field('vwdentalprocedure', 'string',   label='Procedure ID',requires=[IS_NOT_EMPTY(),IS_IN_DB(procquery,'vw_procedurepriceplan.altshortdescription','%(altshortdescription)s')]),
               Field('vwdentalprocedurecode', 'string',   label='Procedure Code',requires=[IS_NOT_EMPTY(),IS_IN_DB(procquery,'vw_procedurepriceplan.procedurecode','%(procedurecode)s')])
               
               )    
            

    formTreatment.element('textarea[name=description]')['_class'] = 'form-control'
    formTreatment.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    formTreatment.element('textarea[name=description]')['_rows'] = 5


    xvwdentalprocedurecode = formTreatment.element('input',_id='no_table_vwdentalprocedurecode')
    xvwdentalprocedurecode['_class'] =  'form-control '
    xvwdentalprocedurecode['_placeholder'] = 'Enter Dental Procedure Code' 
    xvwdentalprocedurecode['_autocomplete'] = 'off'         

    xvwdentalprocedure = formTreatment.element('input',_id='no_table_vwdentalprocedure')
    xvwdentalprocedure['_class'] =  'form-control '
    xvwdentalprocedure['_placeholder'] = 'Enter Dental Procedure Name' 
    xvwdentalprocedure['_autocomplete'] = 'off'         

    xactualtreatmentcost = formTreatment.element('input',_id='no_table_actualtreatmentcost')
    xactualtreatmentcost['_class'] =  'form-control '
    xactualtreatmentcost['_placeholder'] = '' 
    xactualtreatmentcost['_autocomplete'] = 'off'         


    doc = formTreatment.element('#no_table_doctor')
    doc['_class'] = 'form-control'
    doc['_style'] = 'width:100%'



    xpatientmember = formTreatment.element('#no_table_patientmember')
    xpatientmember['_class'] = 'form-control'
    xpatientmember['_placeholder'] = 'Enter Patient Name' 
    xpatientmember['_autocomplete'] = 'off' 
    
    xquadrant = formTreatment.element('input',_id='no_table_quadrant')
    xquadrant['_class'] =  'form-control'
    xquadrant['_placeholder'] = 'Enter Dental Quadrant Q1,Q2,Q3,Q4' 
    xquadrant['_autocomplete'] = 'off' 

    xtooth = formTreatment.element('input',_id='no_table_tooth')
    xtooth['_class'] =  'form-control'
    xtooth['_placeholder'] = 'Enter Dental Tooth T1 to T32' 
    xtooth['_autocomplete'] = 'off' 
    
    
    xstartdate = formTreatment.element('input',_id='no_table_startdate')
    xstartdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xstartdate['_data-date-format'] = 'dd/mm/yyyy'
    xstartdate['_autocomplete'] = 'off' 


    # procedures grid
    query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True))
    
    if(hmopatientmember == True):
        fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription,\
                   db.vw_treatmentprocedure.procedurefee,db.vw_treatmentprocedure.copay,db.vw_treatmentprocedure.inspays,\
                   db.vw_treatmentprocedure.treatmentdate)
                
    
        headers={
            'vw_treatmentprocedure.procedurecode':'Code',
            'vw_treatmentprocedure.altshortdescription':'Description',
            'vw_treatmentprocedure.procedurefee':'Procedure Fee',
            'vw_treatmentprocedure.copay':'Co-Pay',
            'vw_treatmentprocedure.inspays':'Inusrance Pays',
            'vw_treatmentprocedure.treatmentdate':'Treatment Date'
        }
    else:
        fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription,\
                   db.vw_treatmentprocedure.procedurefee,\
                   db.vw_treatmentprocedure.treatmentdate)
                
    
        headers={
            'vw_treatmentprocedure.procedurecode':'Code',
            'vw_treatmentprocedure.altshortdescription':'Description',
            'vw_treatmentprocedure.procedurefee':'Procedure Fee',
            'vw_treatmentprocedure.treatmentdate':'Treatment Date'
        }

    

    maxtextlengths = {'vw_treatmentprocedure.altshortdescription':64}
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
       
    formProcedure = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=None,
                        paginate=10,
                        maxtextlengths=maxtextlengths,
                        orderby=None,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )

    
    
    if formTreatment.accepts(request,session,keepvalues=True):
        
        #logger.logger.info("=Accepted ===" + procedurepriceplancode) 
        #logsql = "INSERT INTO logtable (logerror, created_on) values (' Accepted " + procedurepriceplancode + "', NOW())"
        
        #db.executesql(logsql)
        
        ucrfee = 0
        procedurefee = 0
        copay = 0
        inspays = 0
        companypays = 0
        procedureid = 0
        remarks = ""
        xsts = common.getstring(formTreatment.vars.status)
        procs = db((db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode) & (db.vw_procedurepriceplan.procedurecode == request.vars.vwdentalprocedurecode)).select()
        if(len(procs)>0):
            ucrfee = float(common.getvalue(procs[0].ucrfee))
            procedurefee = float(common.getvalue(procs[0].procedurefee))
            if(procedurefee == 0):
                procedurefee = ucrfee
            copay = float(common.getvalue(procs[0].copay))
            inspays = float(common.getvalue(procs[0].inspays))
            companypays = float(common.getvalue(procs[0].companypays))
            remarks = common.getstring(procs[0].remarks)
            procedureid = int(common.getid(procs[0].id))
        
        db.treatment_procedure.insert(treatmentid = treatmentid, dentalprocedure = procedureid,status=xsts,\
                                      ucr = ucrfee, procedurefee=procedurefee, copay=copay,inspays=inspays,companypays=companypays,\
                                      tooth=formTreatment.vars.tooth,quadrant=formTreatment.vars.quadrant,remarks=remarks) 
        
              

        if(freetreatment == False):
            if(patienttype == 'P'):
                db(db.patientmember.id == patientid).update(newmember = False, freetreatment = True)
            else:
                db(db.patientmemberdependants.id == patientid).update(newmember = False, freetreatment = True)
    
        
        updatetreatmentcostandcopay(treatmentid,tplanid)
        #calculatecost(tplanid)
        #calculatecopay(db, tplanid,memberid)
        #calculateinspays(tplanid)
        #calculatedue(tplanid)        
        #common.dashboard(db,session,providerid)
        
        session.flash = "New Treatment/Procedure Added!"
        
            
        redirect(URL('treatment','update_treatment',vars=dict(page=page,providerid=providerid,treatmentid=treatmentid)))
        
    elif formTreatment.errors:
        
        #logger.loggerpms2.info("=Errors1 ===" + procedurepriceplancode) 
        #logger.loggerpms2.info("=Errors2 ===" + str(formTreatment.errors)) 

        ##logsql = "INSERT INTO logtable (logerror, created_on) values (' Error1 " + str(formTreatment.errors) + "', NOW())"
        ##db.executesql(logsql)
        #logsql = "INSERT INTO logtable (logerror, created_on) values (' Error2 " + procedurepriceplancode + "', NOW())"
        #db.executesql(logsql)
        
        response.flash = "Error: Form has errors " + str(formTreatment.errors)

        

    returnurl = URL('treatment','update_treatment',vars=dict(page=page,providerid=providerid,treatmentid=treatmentid))
    
    return dict(formTreatment=formTreatment, formProcedure=formProcedure, providername=providername,providerid=providerid,page=page,returnurl=returnurl,memberid=memberid,patientid=patientid,membername=membername,patientname=patientname,fullname=fullname,freetreatment=freetreatment,newmember=newmember,tplanid=tplanid,treatmentid=treatmentid,treatment=treatment)        


#def save_prescription():
    
    #providerid = int(common.getid(request.vars.providerid))
    #patientid = int(common.getid(request.vars.patientid))
    #memberid = int(common.getid(request.vars.memberid))
    #doctorid = int(common.getid(request.vars.doctor))
    
    #page=int(common.getid(request.vars.xpage))
    #memberpage = int(common.getid(request.vars.memberpage))

    #treatmentid = int(common.getid(request.vars.treatmentid))
    #tplanid = int(common.getid(request.vars.tplanid))
    
    
    #prescriptionid = db.prescription.insert(\
        
        #providerid = common.getid(request.vars.providerid),
        #medicineid = common.getid(request.vars.medicine),
        #doctorid = common.getid(request.vars.doctor),
        #patientid = patientid,
        #memberid = memberid,
        #frequency  = common.getstring(request.vars.frequency),
        #dosage = common.getstring(request.vars.dosage),
        #quantity  = common.getstring(request.vars.quantity),
        #prescriptiondate = datetime.datetime.strptime(request.vars.prescriptiondate,"%d/%m/%Y"),
        #remarks = common.getstring(request.vars.presremarks),
        #tplanid = tplanid,
        #treatmentid = treatmentid,
        #medicinename = None,
        #medicinecode = None,
        #is_active = True,
        #created_on = datetime.date.today(),
        #created_by = providerid,
        #modified_on = datetime.date.today(),
        #modified_by = providerid
        
    #)

    #formPres = SQLFORM.factory(\
        #Field('prescriptiondate', 'date', label='Date',  default=datetime.date.today(),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        #Field('doctor', 'integer', default=doctorid, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),  label='Drug',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active == True)), 'doctor.id', '%(name)s')),
        #Field('medicine', 'integer', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form_details'),  default="", label='Drug',requires=IS_IN_DB(db((db.medicine.providerid==providerid)&(db.medicine.is_active == True)), 'medicine.id', '%(medicine)s:%(strength)s:%(strengthuom)s')),
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
    
    
    
    #prescriptions = getpresgrid(memberid, patientid, providerid)
    
    #return dict(formPres=formPres, prescriptions=prescriptions, page=page,memberpage=memberpage,\
                   #providerid=providerid,providername=common.getstring(request.vars.providername),\
                   #patientid=patientid,patientmember=common.getstring(request.vars.patientmember),patientname=common.getstring(request.vars.patientname),\
                   #memberid=memberid,doctorid=doctorid,membername=common.getstring(request.vars.membername),\
                   #tplanid=tplanid,treatmentid=treatmentid)  



#def save_medicaltest():
    
    #page=int(common.getid(request.vars.xpage))
    #memberpage = int(common.getid(request.vars.memberpage))
    
    
    #providerid = int(common.getid(request.vars.providerid))
    #providername = common.getstring(request.vars.providername)
    
    
    #treatmentid = int(common.getid(request.vars.treatmentid))
    #tplanid = int(common.getid(request.vars.tplanid))
    
    #memberid = int(common.getid(request.vars.memberid))
    #membername = common.getstring(request.vars.membername)
    
    #patientid = int(common.getid(request.vars.patientid))
    #patientname = common.getstring(request.vars.patientname)
    #patientmember = common.getstring(request.vars.patientmember)   
    
    #testname = common.getstring(request.vars.testname)
    #upval = common.getstring(request.vars.upval)
    #lowval = common.getstring(request.vars.lowval)
    #typval =common.getstring(request.vars.typval)
    #actval = common.getstring(request.vars.actval)
    #remarks = common.getstring(request.vars.remarks)

    
    #medicaltestid = db.medicaltest.insert(
            #tplanid = tplanid,
            #treatmentid = treatmentid,
            #providerid = providerid,
            #memberid = memberid,
            #patientid = patientid,
            #testname = testname,
            #upval = upval,
            #lowval = lowval,
            #typval = typval,
            #actval = actval,
            #remarks = remarks,
            #is_active = True,
            #created_on = datetime.date.today(),
            #created_by = providerid,
            #modified_on = datetime.date.today(),
            #modified_by = providerid
            
        
        #)
    #db.commit()
    
    #medtestgrid = getmedtestgrid(patientid, providerid)
    
    
    
    #return dict(medtestgrid=medtestgrid, page=page,memberpage=memberpage,\
                #providerid=providerid,providername=providername,\
                #patientid=patientid,patientmember=patientmember,patientname=patientname,\
                #memberid=memberid,membername=membername,\
                #tplanid=tplanid,treatmentid=treatmentid)


#def save_medicalnotes():
    
    #page=int(common.getid(request.vars.xpage))
    #memberpage = int(common.getid(request.vars.memberpage))
    #patientid = int(common.getid(request.vars.patientid))
    #providerid = int(common.getid(request.vars.providerid))
    #memberid = int(common.getid(request.vars.memberid))
    #treatmentid = int(common.getid(request.vars.treatmentid))
    #tplanid = int(common.getid(request.vars.tplanid))
    #patient = common.getstring(request.vars.patient)
    #providername = common.getstring(request.vars.providername)
    #fullname = common.getstring(request.vars.fullname)
    #memberref = common.getstring(request.vars.memberref)   
    
    #mednotes = common.getstring(request.vars.mednotes)
    
    
    #db.medicalnotes.update_or_insert(((db.medicalnotes.treatmentid == treatmentid) & (db.medicalnotes.providerid == providerid) & (db.medicalnotes.patientid == patientid)), 
                                     #tplanid = tplanid,
                                     #treatmentid = treatmentid,
                                     #providerid = providerid,
                                     #memberid = memberid,
                                     #patientid = patientid,
                                     #mednotes = mednotes,
                                     #is_active = True,
                                     #modified_on = datetime.date.today(),
                                     #modified_by = providerid
                                     
                                     #)   
    #db.commit()
    
    
    
    
    #return dict(page=page,memberpage=memberpage,providerid=providerid,providername=providername,patientid=patientid,memberid=memberid,patient=patient,fullname=fullname,memberref=memberref,\
                #tplanid=tplanid,treatmentid=treatmentid,mednotes=mednotes)



#def save_chart():
    
    #charttitle = common.getstring(request.vars.charttitle)
    #chartdate = common.getstring(request.vars.chartdate)
    #chartnotes = common.getstring(request.vars.chartnotes)
    #patientname = common.getstring(request.vars.patientname)
    #destchartfile = common.getstring(request.vars.destchartfile)
    
    #providerid = common.getid(request.vars.providerid)
    #tplanid = common.getid(request.vars.tplanid)
    #treatmentid = common.getid(request.vars.treatmentid)
    #memberid = common.getid(request.vars.memberid)
    #patientid = common.getid(request.vars.patientid)
    
    #pattype = 'P'
    #if(memberid != patientid):
        #pattype = 'D'
    
    #db.dentalchart.update_or_insert(((db.dentalchart.treatmentplan==tplanid) & (db.dentalchart.treatment==treatmentid) & (db.dentalchart.provider == providerid)),\
                        #treatmentplan = tplanid,
                        #treatment = treatmentid,
                        #provider = providerid,
                        #chartfile = destchartfile,
                        #title = charttitle,
                        #chartdate = chartdate,
                        #description = chartnotes,
                        #patientmember = memberid,
                        #patient = patientid,
                        #patientname = patientname,
                        #patienttype = pattype,
                        #is_active = True,
                        #created_on = datetime.date.today(),
                        #created_by = providerid,
                        #modified_on = datetime.date.today(),
                        #modified_by = providerid
                        #)
    #db.commit()
    
    #return dict(charttitle=charttitle,chartdate=chartdate,chartnotes=chartnotes)

