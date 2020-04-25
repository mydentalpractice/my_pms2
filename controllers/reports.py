from gluon import current
db = current.globalenv['db']



#import sys
#sys.path.append('modules')
from applications.my_pms2.modules import common
from applications.my_pms2.modules import mail
from applications.my_pms2.modules import status

#from gluon.contrib import common
#from gluon.contrib import mail
#from gluon.contrib import status


import datetime
def email():
    
    
    return dict()


def viewplanpdf():
    
    
    planid = int(common.getid(request.vars.planid))
    
    r=db(db.hmoplan.id == planid).select(db.hmoplan.planfile)
    
    planfile = common.getstring(r[0].planfile)
    
    planfile = planfile if(planfile != "") else "blankplan.pdf"
    
    r = db(db.urlproperties.id > 0).select(db.urlproperties.externalurl)
    externalurl = common.getstring(r[0].externalurl)
    
  
    redirect(externalurl.rstrip("/") + "/files/"  + planfile)
    
    
    
    return dict()

    
def treatmentreport():
    
    page = common.getpage(request.vars.page)
    
    treatmentid = int(common.getid(request.vars.treatmentid))
    tr = db(db.treatment.id == treatmentid).select()
    
    tplanid = int(common.getstring(tr[0].treatmentplan))
    providerid = int(common.getstring(tr[0].provider))
    prov = db((db.provider.id == providerid)).select()
    registration = common.getstring(prov[0].registration)
      
    rptheader = db((db.vw_patienttreatment_header_rpt.id == tplanid )).select()

    provname = common.getstring(rptheader[0].providername)
    provaddr = common.getstring(rptheader[0].provaddress)
    provcontact = common.getstring(rptheader[0].provcontact)
    
    membername = common.getstring(rptheader[0].membername)
    memberaddress = common.getstring(rptheader[0].memberaddress)
    membercontact =  common.getstring(rptheader[0].membercontact)
    
    patientname = common.getstring(rptheader[0].patientname)
    
    hmoplan = common.getstring(rptheader[0].hmoplan)
    premenddt = common.getnulldt(rptheader[0].premenddt)
    
    company = common.getstring(rptheader[0].company)
  
    tplan = common.getstring(rptheader[0].treatmentplan)
    status = common.getstring(rptheader[0].status)
    startdate = common.getnulldt(rptheader[0].startdate)
    enddate = common.getnulldt(rptheader[0].enddate)
    
    totalcost = common.getvalue(rptheader[0].totaltreatmentcost)
    totalcopay = common.getvalue(rptheader[0].totalcopay)
    totalinspays = common.getvalue(rptheader[0].totalinspays)
    
    totalpaid = common.getvalue(rptheader[0].totalpaid)
    totaldue = common.getvalue(rptheader[0].totaldue)
    totalinspaid = common.getvalue(rptheader[0].totalinspaid)
    totalcopaypaid = common.getvalue(rptheader[0].totalcopaypaid)
    
    tp = db(db.treatmentplan.id == tplanid).select()
    patientid = int(common.getstring(tp[0].patient))
    memberid = int(common.getstring(tp[0].primarypatient))
    

    #treatment
    left   = None 
    links  = None
    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
     
   
    query = (db.vw_patienttreatment_detail_rpt.id == tplanid)
            
    fields=(\
             db.vw_patienttreatment_detail_rpt.treatment,
             db.vw_patienttreatment_detail_rpt.status,
             db.vw_patienttreatment_detail_rpt.startdate,
             db.vw_patienttreatment_detail_rpt.treatmentcost,
             db.vw_patienttreatment_detail_rpt.copay,
             db.vw_patienttreatment_detail_rpt.inspay,
             db.vw_patienttreatment_detail_rpt.description
            )
   
       
    headers={
        'vw_patienttreatment_detail_rpt.treatment':'Treatment',
        'vw_patienttreatment_detail_rpt.startdate':'Date',
        'vw_patienttreatment_detail_rpt.status':'Status',
        'vw_patienttreatment_detail_rpt.description':'Description',
        'vw_patienttreatment_detail_rpt.treatmentcost':'Cost',
        'vw_patienttreatment_detail_rpt.inspay':'Authorized Pay',
        'vw_patienttreatment_detail_rpt.copay':'Co-Pay',
        'vw_patienttreatment_detail_rpt.description':'Description'
        
        }
   
    formB = SQLFORM.grid(query=query,
                         headers=headers,
                         fields=fields,
                         exportclasses=exportlist,
                         links_in_grid=False,
                         searchable=False,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=False
                        )    
    
    
    #procedures
    left   = None 
    links  = None
    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
    
    query = ((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True))
    fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription,db.vw_treatmentprocedure.ucrfee, \
               db.vw_treatmentprocedure.procedurefee,db.vw_treatmentprocedure.copay,db.vw_treatmentprocedure.inspays,db.vw_treatmentprocedure.status,\
               db.vw_treatmentprocedure.treatmentdate)
            

    headers={
        'vw_treatmentprocedure.procedurecode':'Code',
        'vw_treatmentprocedure.altshortdescription':'Description',
        'vw_treatmentprocedure.ucrfee':'UCR',
        'vw_treatmentprocedure.procedurefee':'Procedure Cost',
        'vw_treatmentprocedure.copay':'Co-Pay',
        'vw_treatmentprocedure.inspays':'Authorized',
        'vw_treatmentprocedure.status':'Status',
        'vw_treatmentprocedure.treatmentdate':'Treatment Date'
    }
    

    maxtextlengths = {'vw_treatmentprocedure.altshortdescription':100}
    
       
    formC = SQLFORM.grid(query=query,
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
    
    
    returnurl = URL('treatment','list_treatments', vars=dict(page=page,providerid=providerid,patientid=patientid,memberid=memberid))
    return dict(prov=prov,formB=formB,formC=formC,
               membername=membername,memberaddress=memberaddress,membercontact=membercontact,\
               hmoplan = hmoplan, premenddt = premenddt,patientname=patientname,company=company,
               tplan=tplan,status=status,startdate=startdate,enddate=enddate,
               totalcost=totalcost,totalcopay=totalcopay,totalinspays=totalinspays,
               totalpaid=totalpaid,totaldue=totaldue,totalinspaid=totalinspaid,totalcopaypaid= totalcopaypaid,
               returnurl=returnurl

        )

def preauthorization():
    
    treatmentid = int(common.getid(request.vars.treatmentid))
    retval = mail.emailPreAuthorization(db, request.folder, treatmentid)
    
    #tr = db(db.treatment.id == treatmentid).select()
    #tplanid = int(common.getid(tr[0].treatmentplan))    
    #tp = db(db.treatmentplan.id == tplanid).select()
    #providerid = int(common.getid(tp[0].provider))
    #patientid = int(common.getid(tp[0].patient))
    #memberid = int(common.getid(tp[0].primarypatient))
    #pats = db((db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid == memberid )).select()
    #patient = ""  #first &lastname:patientmember
    #if(len(pats)>0):
        #patient = common.getstring(pats[0].patient)
    
    #provs= db((db.provider.id == providerid)&(db.provider.is_active == True)).select()
    #providername = ""
    #if(len(provs)>0):
        #providername = common.getstring(provs[0].provider) + ":" + common.getstring(provs[0].providername)
   
    
    
   
  
    #str1 = "<p>" + "Patient:" + "\t" + patient + "</p>\r\n"
    #str1 = str1 + "<p>" + "Provider:" + "\t" + providername + "</p>\r\n"
    

    ##treatment
    #trmnts = db(db.vw_patienttreatment_detail_rpt.id == tplanid).select()
    #str1 = "<p>Treatment Plan</p>"
    #str1 = str1 + "\r\n"
    #str1 = str1 + "<p>"
    
    #for trtmnt in trmnts:
        #str1 = str1 + trtmnt.treatment + "\t" + common.getdt(trtmnt.startdate).strftime("%d/%m/%Y")
        
    #str1 = str1 + "</p>\r\n<p>Procedures</p>\r\n"
    
    ##procedures
    #procs = db((db.vw_treatmentprocedure.treatmentid  == treatmentid) & (db.vw_treatmentprocedure.is_active == True)).select()
    #for proc in procs:
        #str1 = str1 + "<p>" + "\t" + common.getdt(proc.treatmentdate).strftime("%d/%m/%Y") + "\t" + common.getstring(proc.procedurecode) + "\t" + common.getstring(proc.altshortdescription) + "\t" + str(common.getvalue(proc.procedurefee)) + "</p>\r\n"
        
    
    return retval

                                                   
                                              
                                            
                                              
    
    
    
    
def membertreatmentplansreport():
    
    page = int(common.getpage(request.vars.page))
    
    provdict = common.getprovider(auth,db)
    providerid = provdict["providerid"]
    prov = db((db.provider.id == providerid)&(db.provider.is_active == True)).select()
    registration = ""
    if(len(prov)>0):
        registration = prov[0]["registration"]    
    
    
    tplanid = int(common.getid(request.vars.tplanid))
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))
    
    nonmember = common.getboolean(request.vars.nonmember)

    if(nonmember == True):
        returnurl = URL('member', 'list_nonmembers', vars=dict(page=page,providerid = providerid,memberid=memberid,patientid=patientid))
    else:
        returnurl = URL('member', 'list_members', vars=dict(page=page,providerid = providerid,memberid=memberid,patientid=patientid))


   
    patientname = ""
    r = db((db.vw_memberpatientlist.patientid==patientid) & (db.vw_memberpatientlist.primarypatientid == memberid)).select()
    if(len(r)>0):
        patientname = common.getstring(r[0].fullname)
    
   
    rptheader = db((db.vw_membertreatmentplans_header_rpt.patient == patientid)&(db.vw_membertreatmentplans_header_rpt.primarypatient == memberid )&(db.vw_membertreatmentplans_header_rpt.providerid == providerid )).select()
    
    if(len(rptheader) == 0):
        response.flash = "No Treatments and Payments to report!"
        session.flash = "No Treatments and Payments to report!"
        redirect(returnurl)
    
    provname = common.getstring(rptheader[0].providername)
    provaddr = common.getstring(rptheader[0].provaddress)
    provcontact = common.getstring(rptheader[0].provcontact)
    
    membername = common.getstring(rptheader[0].membername)
    memberaddress = common.getstring(rptheader[0].memberaddress)
    membercontact =  common.getstring(rptheader[0].membercontact)
    memberemail = common.getstring(rptheader[0].memberemail)
    membercell = common.getstring(rptheader[0].membercell)
    
    hmoplan = common.getstring(rptheader[0].hmoplan)
    premenddt = common.getnulldt(rptheader[0].premenddt)
    
    company = common.getstring(rptheader[0].company)

    docreg = ""    
       

    totalcost = 0
    totalcopay = 0
    totalinspays = 0
    
    totalpaid = 0
    totaldue = 0
    totalinspaid = 0
    totalcopaypaid = 0
    
  
    rptheader = db((db.vw_membertreatmentplans_header_rpt.patient == patientid)&(db.vw_membertreatmentplans_header_rpt.primarypatient == memberid )&(db.vw_membertreatmentplans_header_rpt.providerid == providerid )).select()
   
    if(len(rptheader)>0):
        totalcost = common.getvalue(rptheader[0].totaltreatmentcost)
        totalcopay = common.getvalue(rptheader[0].totalcopay)
        totalinspays = common.getvalue(rptheader[0].totalinspays)
        
        totalpaid = common.getvalue(rptheader[0].totalpaid)
        totaldue = totalcopay-totalpaid
        totalinspaid = common.getvalue(rptheader[0].totalinspaid)
        totalcopaypaid = common.getvalue(rptheader[0].totalcopaypaid)
    
    
    
    
    left   = None 
    links  = None
    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False,csv=False)
    orderby = ~(db.vw_membertreatmentplans_detail_rpt.id)
   
    query = ((db.vw_membertreatmentplans_detail_rpt.primarypatient == memberid) & (db.vw_membertreatmentplans_detail_rpt.patient == patientid) \
             & (db.vw_membertreatmentplans_detail_rpt.providerid == providerid) & (db.vw_membertreatmentplans_detail_rpt.is_active == True))
            
    fields=(\
             db.vw_membertreatmentplans_detail_rpt.treatment,
             db.vw_membertreatmentplans_detail_rpt.startdate,
             db.vw_membertreatmentplans_detail_rpt.treatmentcost,
             db.vw_membertreatmentplans_detail_rpt.inspay,
             db.vw_membertreatmentplans_detail_rpt.copay,
            
            )
   
       
    headers={
        'vw_membertreatmentplans_detail_rpt.treatment':'Treatment',
        'vw_membertreatmentplans_detail_rpt.startdate':'Date',
        'vw_membertreatmentplans_detail_rpt.treatmentcost':'Treatment Cost',
        'vw_membertreatmentplans_detail_rpt.inspay':'Authorized Pay',
        'vw_membertreatmentplans_detail_rpt.copay':'Co-Pay',
        
        }
   
    maxtextlengths = {'vw_membertreatmentplans_detail_rpt.Treatment':50}
    
    formB = SQLFORM.grid(query=query,
                         headers=headers,
                         fields=fields,
                         orderby = orderby,
                         exportclasses=exportlist,
                         links_in_grid=False,
                         maxtextlengths=maxtextlengths,
                         paginate=5,
                         searchable=False,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=False
                        )    

    
    #procedures
    query = ((db.vw_treatmentprocedure.primarypatient == memberid) & \
                                                     (db.vw_treatmentprocedure.patient == patientid) \
                                                     & (db.vw_treatmentprocedure.providerid == providerid) & \
                                                     (db.vw_treatmentprocedure.is_active == True)) 

    left = None
    
    fields = (\
        db.vw_treatmentprocedure.treatmentdate,
        db.vw_treatmentprocedure.treatment,
        db.vw_treatmentprocedure.procedurecode,
        db.vw_treatmentprocedure.altshortdescription,
        db.vw_treatmentprocedure.tooth,
        db.vw_treatmentprocedure.quadrant,
        db.vw_treatmentprocedure.status,
        db.vw_treatmentprocedure.procedurefee,
        db.vw_treatmentprocedure.inspays,
        db.vw_treatmentprocedure.copay
    )
    
    headers={
           'vw_treatmentprocedure.treatmentdate':'Date',
           'vw_treatmentprocedure.treatment':'Treatment',
           'vw_treatmentprocedure.procedurecode':'Code',
           'vw_treatmentprocedure.altshortdescription':'Procedure',
           'vw_treatmentprocedure.tooth':'Tooth',
           'vw_treatmentprocedure.quadrant':'Quadrant',
           'vw_treatmentprocedure.status':'Status',
           
           'vw_treatmentprocedure.procedurefee':'Procedure Fee',
           'vw_treatmentprocedure.inspays':'Authorized Pay',
           'vw_treatmentprocedure.copay':'Co-Pay'
           
           }    
    
    maxtextlengths = {'vw_treatmentprocedure.altshortdescription':128}
    orderby = ~(db.vw_treatmentprocedure.treatmentdate)
    formC= SQLFORM.grid(query=query,
                         headers=headers,
                         fields=fields,
                         orderby = orderby,
                         exportclasses=exportlist,
                         links_in_grid=False,
                         maxtextlengths=maxtextlengths,
                         paginate=None,
                         searchable=False,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=False
                        )    
    
    return dict(prov=prov,registration=registration,docreg=docreg,\
                membername=membername,memberaddress=memberaddress,membercell=membercell, memberemail=memberemail,\
                hmoplan = hmoplan, premenddt = premenddt,company=company,
                totalcost=totalcost,totalcopay=totalcopay,totalinspays=totalinspays,
                totalpaid=totalpaid,totaldue=totaldue,totalinspaid=totalinspaid,totalcopaypaid= totalcopaypaid,
                formB=formB,formC=formC,nonmember = nonmember,patientname=patientname,returnurl=returnurl
                )
    
    
    
    

    
    
def treatmentpaymentreport():

    
    
    providerid = int(common.getstring(request.vars.providerid))
    provideridct = common.getproviderfromid(db, providerid)
    
    returnurl = URL('superadmin','superadmin', vars=dict(page=1))
    
    strsql = "SELECT SUM(totaltreatmentcost) AS totaltreatmentcost, SUM(totalcopay) AS totalcopay, SUM(totalinspays) as totalinspays, "    
    strsql = strsql + " SUM(totalpaid) AS totalpaid, SUM(totaldue) AS totaldue FROM vw_treatmentpaymentreport WHERE providerid =  " + str(providerid)
    ds = db.executesql(strsql)
    
    if(len(ds) > 0):
        totaltreatmentcost = float(common.getstring(ds[0][0]))
        totalcopay = float(common.getstring(ds[0][1]))
        totalinspays = float(common.getstring(ds[0][2]))
        totalpaid = float(common.getstring(ds[0][3]))
        totaldue = float(common.getstring(ds[0][4]))
                                   
        
    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
    
    
    orderby = ~(db.vw_treatmentpaymentreport.membername)
   
    query = ((db.vw_treatmentpaymentreport.providerid == providerid))

            
    fields=(\
   
             db.vw_treatmentpaymentreport.membername,
             db.vw_treatmentpaymentreport.treatment,
             db.vw_treatmentpaymentreport.totaltreatmentcost,
             db.vw_treatmentpaymentreport.totalinspays,
             db.vw_treatmentpaymentreport.totalcopay,
             db.vw_treatmentpaymentreport.totalpaid,
             db.vw_treatmentpaymentreport.totaldue
            
            
            )
   
       
    headers={
     
        'vw_treatmentpaymentreport.membername':'Patient Name',
        'vw_treatmentpaymentreport.treatment':'Treatment',
        'vw_treatmentpaymentreport.totaltreatmentcost':'Treatment Cost',
        'vw_treatmentpaymentreport.totalinspays':'Authorized Pay',
        'vw_treatmentpaymentreport.totalcopay':'Co-Pay',
        'vw_treatmentpaymentreport.totalpaid':'Total Paid',
        'vw_treatmentpaymentreport.totaldue':'Total Due'
        
        }
   
    maxtextlengths = {'vw_treatmentpaymentreport.treatment':50, 'vw_treatmentpaymentreport.membername':50}
    
    formB = SQLFORM.grid(query=query,
                         headers=headers,
                         fields=fields,
                         orderby = orderby,
                         exportclasses=exportlist,
                         links_in_grid=False,
                         maxtextlengths=maxtextlengths,
                         paginate=20,
                         searchable=False,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=False
                        )    


    
    db.vw_treatmentpaymentreport.is_active.writeable = False
    
    return dict(formB=formB,page=0, providerid=providerid, providername=provideridct["providername"],returnurl=returnurl,\
                totaltreatmentcost=totaltreatmentcost,totalcopay=totalcopay,totalinspays=totalinspays,totalpaid=totalpaid,totaldue=totaldue)
