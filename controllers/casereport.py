from gluon import current
db = current.globalenv['db']
#
import datetime
import time

#import sys
#sys.path.append('/my_pms2/modules')
from applications.my_pms2.modules import common
from applications.my_pms2.modules import gender

def getage(dob):
    ageyear = dob.year
    curryear = datetime.date.today().year
    return curryear - ageyear

def getmedtestgrid(patientid, providerid):
    medtestquery = ((db.medicaltest.patientid == patientid) & (db.medicaltest.providerid == providerid) & (db.medicaltest.is_active == True))
    
    medtestfields=(db.medicaltest.testdate,db.medicaltest.testname,db.medicaltest.actval,db.medicaltest.upval, db.medicaltest.lowval, db.medicaltest.typval)
    
    medtestheaders={
        
        'medicaltest.testdate':'Date',
        'medicaltest.testname':'Medical Test',
        'medicaltest.actval':'Actual Value',
        'medicaltest.lowval':'Lower Value',
        'medicaltest.typval':'Typical Value',
        'medicaltest.upval':'Upper Value'
                }

    db.medicaltest.modified_on.readable = True
    db.medicaltest.modified_on.writable = True
 
    medtestexport = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
     
    medtestorderby = ~db.medicaltest.modified_on
       
    medtestgrid = SQLFORM.grid(query=medtestquery,
                        headers=medtestheaders,
                        fields=medtestfields,
                        paginate=20,
                        orderby=medtestorderby,
                        exportclasses=medtestexport,
                        links_in_grid=False,
                        searchable=False,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )
    
    return medtestgrid

#URL('casereport', 'casereport', vars=dict(page=page, patientid = patientid, source=member))
@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def casereport():
    
    page = int(common.getpage(request.vars.page))
    provdict = common.getprovider(auth, db)
    providername  = provdict["providername"]
    providerid = int(provdict["providerid"])
    treatmentid = int(common.getid(request.vars.treatmentid))  #display all notes of a patient for all treatments.
    source = common.getstring(request.vars.source)    
    
    memberid = int(common.getid(request.vars.memberid))
    patientname = ""
    patientid = int(common.getid(request.vars.patientid))
    pats = db((db.vw_memberpatientlist.primarypatientid == memberid) &(db.vw_memberpatientlist.patientid == patientid)&(db.vw_memberpatientlist.providerid == providerid)).select()
    if(len(pats)>0):
        patientname = pats[0].patient
    
    csrs = db((db.vw_casereport.patientid == patientid) &(db.vw_casereport.memberid == memberid) &(db.vw_casereport.providerid == providerid)  & (db.vw_casereport.is_active == True)).select(db.vw_casereport.ALL, orderby=~db.vw_casereport.id)    
        
    
    formCSR= SQLFORM.factory(
        Field('patientmember', 'string', default=''),
        Field('fullname', 'string', default=patientname),
        Field('doctor', 'string', default=''),
        Field('csrs', 'text', default=''),
        Field('newcsr', 'text', default='')
    )
    
    formCSR.element('textarea[name=csrs]')['_class'] = 'form-control'
    formCSR.element('textarea[name=csrs]')['_style'] = 'height:500px;line-height:1.0;'
    formCSR.element('textarea[name=csrs]')['_rows'] = 1000
    
    formCSR.element('textarea[name=newcsr]')['_class'] = 'form-control'
    formCSR.element('textarea[name=newcsr]')['_style'] = 'height:100px;line-height:1.0;'
    formCSR.element('textarea[name=newcsr]')['_rows'] = 10
    
    xpm = formCSR.element('#no_table_patientmember')
    xpm['_class'] = 'form-control'
    xpm['_autocomplete'] = 'off'     

    xfnm = formCSR.element('#no_table_fullname')
    xfnm['_class'] = 'form-control'
    xfnm['_autocomplete'] = 'off'  
    
    xdoc = formCSR.element('#no_table_doctor')
    xdoc['_class'] = 'form-control'
    xdoc['_autocomplete'] = 'off'  
    
    if(source == 'members'):
        returnurl = URL('member', 'list_patients', vars=dict(page=page, providerid=providerid))
    elif(source == 'walkin'):
        returnurl = URL('member', 'list_nonmembers', vars=dict(page=page, providerid=providerid))
    else:
        returnurl = URL('treatment', 'update_treatment', vars=dict(page=page, providerid=providerid,patientid=patientid,treatmentid=treatmentid))
        
    
    return dict(formCSR=formCSR,csrs=csrs,page=page,returnurl=returnurl,providerid=providerid,providername=providername,memberid=memberid,patientid=patientid,patientname=patientname,treatmentid=treatmentid,source=source)


def addcsr():
    
    
    patientid = int(common.getid(request.vars.patientid))
    memberid = int(common.getid(request.vars.memberid))
    providerid = int(common.getid(request.vars.providerid))
    page = int(common.getpage(request.vars.page))
    source = common.getstring(request.vars.source)
    treatmentid = int(common.getid(request.vars.treatmentid))


    
    common.lognotes(db, common.getstring(request.vars.newcsr), 0,providerid,patientid,memberid,0)
    
    newcsr=""
    
 
    #list of CSRS
    csrs = db((db.vw_casereport.patientid == patientid) &(db.vw_casereport.memberid == memberid) &(db.vw_casereport.providerid == providerid)  & (db.vw_casereport.is_active == True)).select(db.vw_casereport.ALL, orderby=~db.vw_casereport.id)    
    
    formCSR= SQLFORM.factory(
           Field('patientmember', 'string', default=''),
           Field('fullname', 'string', default=''),
           Field('doctor', 'string', default=''),
           Field('csrs', 'text',  default=csrs),
           Field('newcsr', 'text', default='')
       )
       
    formCSR.element('textarea[name=csrs]')['_class'] = 'form-control'
    formCSR.element('textarea[name=csrs]')['_style'] = 'height:500px;line-height:1.0;'
    formCSR.element('textarea[name=csrs]')['_rows'] = 1000
    
    formCSR.element('textarea[name=newcsr]')['_class'] = 'form-control'
    formCSR.element('textarea[name=newcsr]')['_style'] = 'height:100px;line-height:1.0;'
    formCSR.element('textarea[name=newcsr]')['_rows'] = 10
    
    xpm = formCSR.element('#no_table_patientmember')
    xpm['_class'] = 'form-control'
    xpm['_autocomplete'] = 'off'     

    xfnm = formCSR.element('#no_table_fullname')
    xfnm['_class'] = 'form-control'
    xfnm['_autocomplete'] = 'off'  
    
    xdoc = formCSR.element('#no_table_doctor')
    xdoc['_class'] = 'form-control'
    xdoc['_autocomplete'] = 'off'      

    if(source == 'members'):
        returnurl = URL('member', 'list_patients', vars=dict(page=page, providerid=providerid))
    elif(source == 'walkin'):
        returnurl = URL('member', 'list_nonmembers', vars=dict(page=page, providerid=providerid))
    else:
        returnurl = URL('treatment', 'update_treatment', vars=dict(page=page, providerid=providerid,patientid=patientid,memberid=memberid,treatmentid=treatmentid))
    
    
    
    return dict(formCSR=formCSR,returnurl=returnurl,csrs=csrs,newcsr=newcsr,page=page,providerid=providerid,memberid=memberid,patientid=patientid,treatmentid=treatmentid,source=source)



@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def medicaltest():
    
    page=common.getpage(request.vars.page)
    provdict = common.getprovider(auth, db)
    providername  = provdict["providername"]    
    providerid = int(common.getid(request.vars.providerid))
    memberid = int(common.getid(request.vars.memberid1))
    patientid = int(common.getid(request.vars.patientid1))
    tplanid = int(common.getid(request.vars.tplanid1))
    treatmentid = int(common.getid(request.vars.treatmentid1))
    returnurl = URL('treatment','update_treatment', vars=dict(imagepage=0,page=page,providerid=providerid,treatmentid=treatmentid))
    
    patient = ""
    patientmember = ""
    
    r = db((db.vw_memberpatientlist.primarypatientid == memberid)&(db.vw_memberpatientlist.patientid == patientid)).select(
        db.vw_memberpatientlist.patient
    )
    if(len(r)>0):
        patient = common.getstring(r[0].patient)
        
        
    formMedTest = SQLFORM.factory(
        Field('testname', 'string', default=""),
        Field('testdate', 'date', label='Test Date',default=datetime.date.today(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('actualvalue', 'string', default=""),
        Field('lowervalue', 'string', default=""),
        Field('uppervalue', 'string', default=""),
        Field('typicalvalue', 'string', default=""),
        Field('remarks','text',default=""),
        Field('is_active','boolean', default = True)        
    
    )
    formMedTest.element('textarea[name=remarks]')['_style'] = 'height:50px;line-height:1.0;'
    formMedTest.element('textarea[name=remarks]')['_rows'] = 2
    formMedTest.element('textarea[name=remarks]')['_class'] = 'form-control'     

    xtestname = formMedTest.element('input',_id='no_table_testname')
    xtestname['_class'] =  'form-control'
    xtestname['_type'] =  'text'    


    xactval = formMedTest.element('input',_id='no_table_actualvalue')
    xactval['_class'] =  'form-control'
    xactval['_type'] =  'text'    
    
    xloval = formMedTest.element('input',_id='no_table_lowervalue')
    xloval['_class'] =  'form-control'
    xloval['_type'] =  'text'    
    
    xupval = formMedTest.element('input',_id='no_table_uppervalue')
    xupval['_class'] =  'form-control'
    xupval['_type'] =  'text'    
    
    xtypval = formMedTest.element('input',_id='no_table_typicalvalue')
    xtypval['_class'] =  'form-control'
    xtypval['_type'] =  'text'    
    
    xtestdate = formMedTest.element('input',_id='no_table_testdate')
    xtestdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xtestdate['_data-date-format'] = 'dd/mm/yyyy'
    xtestdate['_autocomplete'] = 'off'  

    if formMedTest.accepts(request,session=session,keepvalues=True):
        i = 0
        medicaltestid = db.medicaltest.insert(
                testdate = common.getdt(formMedTest.vars.testdate),
                tplanid = tplanid,
                treatmentid = treatmentid,
                providerid = providerid,
                memberid = memberid,
                patientid = patientid,
                testname = common.getstring(formMedTest.vars.testname),
                upval = common.getstring(formMedTest.vars.uppervalue),
                lowval = common.getstring(formMedTest.vars.lowervalue),
                typval = common.getstring(formMedTest.vars.typicalvalue),
                actval = common.getstring(formMedTest.vars.actualvalue),
                remarks = common.getstring(formMedTest.vars.remarks),
                is_active = True,
                created_on = common.getISTFormatCurrentLocatTime(),
                created_by =  1 if(auth.user == None) else auth.user.id,
                modified_on = common.getISTFormatCurrentLocatTime(),
                modified_by =  1 if(auth.user == None) else auth.user.id
            )
    
    elif formMedTest.errors:
        response.flash = "Error Medical Test " + str(formMedTest.errors)   
        
    
    
    medtestgrid = getmedtestgrid(patientid, providerid)
    
       
       
    return dict(formMedTest=formMedTest,medtestgrid=medtestgrid,page=page,\
                providerid=providerid,providername=providername,memberid=memberid,\
                patientid=patientid,patientmember=patientmember,patientname=patient,\
                treatmentid=treatmentid,returnurl=returnurl)    
    
    
    
    
    
    


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def medicalhistory():
    
    page=common.getpage(request.vars.page)
    provdict = common.getprovider(auth, db)
    providername  = provdict["providername"]    
    providerid = int(common.getid(request.vars.providerid))
    memberid = int(common.getid(request.vars.memberid1))
    patientid = int(common.getid(request.vars.patientid1))
    tplanid = int(common.getid(request.vars.tplanid1))
    treatmentid = int(common.getid(request.vars.treatmentid1))
    doctorid = int(common.getid(request.vars.doctorid1))
    returnurl = URL('treatment','update_treatment', vars=dict(imagepage=0,page=page,providerid=providerid,treatmentid=treatmentid))

    dob = datetime.datetime.strptime("01/01/2001", "%d/%m/%Y")
    age = common.getstring(getage(dob))
    xgender = "Male"
    address = ""
    telephone  = ""
    cell = ""
    email = ""
    fullname = ""
    
    rows = db((db.vw_memberpatientlist.primarypatientid == memberid)&\
              (db.vw_memberpatientlist.patientid == patientid)&\
              (db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.is_active == True)).select(\
                  db.vw_memberpatientlist.fullname,\
                  db.vw_memberpatientlist.cell,\
                  db.vw_memberpatientlist.email,\
                  db.vw_memberpatientlist.dob,\
                  db.vw_memberpatientlist.gender,\
                  db.patientmember.address1,\
                  db.patientmember.address2,\
                  db.patientmember.address3,\
                  db.patientmember.city,\
                  db.patientmember.st,\
                  db.patientmember.pin,\
                  db.patientmember.telephone,\
                  left = db.patientmember.on(db.patientmember.id == memberid)
              
              )    
    
   
    if(len(rows)>0) :
        fullname = common.getstring(rows[0].vw_memberpatientlist.fullname)
        cell = common.getstring(rows[0].vw_memberpatientlist.cell)
        email = common.getstring(rows[0].vw_memberpatientlist.email)
        xgender = common.getstring(rows[0].vw_memberpatientlist.gender)    
        address = common.getstring(rows[0].patientmember.address1) + " " + \
            common.getstring(rows[0].patientmember.address2) + " " + common.getstring(rows[0].patientmember.address3) + ",\r\n" + \
            common.getstring(rows[0].patientmember.city) + ", " + common.getstring(rows[0].patientmember.st) + " " + common.getstring(rows[0].patientmember.pin)
        telephone = common.getstring(rows[0].patientmember.telephone)        
        
        if((rows[0].vw_memberpatientlist.dob != None) & (rows[0].vw_memberpatientlist.dob != "")):    
            dob = rows[0].vw_memberpatientlist.dob
            age = common.getstring(getage(dob))
        
    medhist = db((db.medicalnotes.patientid == patientid) & (db.medicalnotes.memberid == memberid)).select()
    
    occupation = ""
    referer = ""
    resoff = ""
    bp = False
    diabetes = False
    anaemia = False
    epilepsy = False
    asthma = False
    sinus = False
    heart = False
    jaundice = False
    tb = False
    cardiac = False
    arthritis = False
    anyother = False
    allergic = False
    excessivebleeding = False
    seriousillness = False
    hospitalized = False
    medications = False
    surgery = False
    pregnant = False
    breastfeeding = False
    anyothercomplaint = ""
    chiefcomplaint = ""
    duration = ""
    height = "0.00"
    weight = "0.00"
    
    if(len(medhist)>0):
        occupation = common.getstring(medhist[0].occupation)
        referer = common.getstring(medhist[0].referer)
        resoff = common.getstring(medhist[0].resoff)
        anyothercomplaint = common.getstring(medhist[0].anyothercomplaint)
        chiefcomplaint = common.getstring(medhist[0].chiefcomplaint)
        duration = common.getstring(medhist[0].duration)
        height = common.getstring(medhist[0].height)
        weight = common.getstring(medhist[0].weight)
        
        bp = common.getboolean(medhist[0].bp)
        diabetes = common.getboolean(medhist[0].diabetes)
        anaemia = common.getboolean(medhist[0].anaemia)
        epilepsy = common.getboolean(medhist[0].epilepsy)
        asthma = common.getboolean(medhist[0].asthma)
        sinus = common.getboolean(medhist[0].sinus)
        heart = common.getboolean(medhist[0].heart)
        jaundice = common.getboolean(medhist[0].jaundice)
        tb = common.getboolean(medhist[0].tb)
        cardiac = common.getboolean(medhist[0].cardiac)
        arthritis = common.getboolean(medhist[0].arthritis)
        anyother = common.getboolean(medhist[0].anyother)
        allergic = common.getboolean(medhist[0].allergic)
        excessivebleeding = common.getboolean(medhist[0].excessivebleeding)
        seriousillness = common.getboolean(medhist[0].seriousillness)
        hospitalized = common.getboolean(medhist[0].hospitalized)
        medications = common.getboolean(medhist[0].medications)
        surgery = common.getboolean(medhist[0].surgery)
        pregnant = common.getboolean(medhist[0].pregnant)
        breastfeeding = common.getboolean(medhist[0].breastfeeding)
   
    
    formMedHist = SQLFORM.factory(
        Field('patientmember', 'string',  label='Patient', default = fullname,writable=False),
        Field('notesdate', 'date', label='To Date',default=datetime.date.today(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('dob', 'date', label='DOB',default=dob, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('age', 'string', default=age),
        Field('cell', 'string', default=cell),
        Field('email', 'string', default=email),
        Field('telephone', 'string', default=telephone),
        Field('xgender', 'string', label='Gender',widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form-control '),default=xgender, requires = IS_IN_SET(gender.GENDER)),
        Field('address','text', label='Address', default=address),
        Field('occupation', 'string', default=occupation),
        Field('referer','string', label='Doctor/Fried', default=referer),
        Field('resoff','string', label='Residence/Office', default=resoff),
        Field('bp','boolean', default = bp),
        Field('diabetes','boolean', default = diabetes),
        Field('anaemia','boolean', default = anaemia),
        Field('epilepsy','boolean', default = epilepsy),
        Field('asthma','boolean', default = asthma),
        Field('sinus','boolean', default = sinus),
        Field('heart','boolean', default = heart),
        Field('jaundice','boolean', default = jaundice),
        Field('tb','boolean', default = tb),
        Field('cardiac','boolean', default = cardiac),
        Field('arthritis','boolean', default = arthritis),
        Field('anyother','boolean', default = anyother),
        Field('allergic','boolean', default = allergic),
        Field('excessivebleeding','boolean', default = excessivebleeding),
        Field('seriousillness','boolean', default = seriousillness),
        Field('hospitalized','boolean', default = hospitalized),
        Field('medications','boolean', default = medications),
        Field('surgery','boolean', default = surgery),
        Field('pregnant','boolean', default = pregnant),
        Field('breastfeeding','boolean', default = breastfeeding),
        Field('anyothercomplaint','text',default=anyothercomplaint),
        Field('chiefcomplaint','text',default=chiefcomplaint),
        Field('duration','text',  default=duration),
        Field('height','string',  default=height),
        Field('weight','string',  default=weight),
        
        Field('is_active','boolean', default = True)
    )  


    formMedHist.element('textarea[name=anyothercomplaint]')['_style'] = 'height:50px;line-height:1.0;'
    formMedHist.element('textarea[name=anyothercomplaint]')['_rows'] = 2
    formMedHist.element('textarea[name=anyothercomplaint]')['_class'] = 'form-control' 
    
    formMedHist.element('textarea[name=chiefcomplaint]')['_style'] = 'height:60px;line-height:1.0;'
    formMedHist.element('textarea[name=chiefcomplaint]')['_rows'] = 3
    formMedHist.element('textarea[name=chiefcomplaint]')['_class'] = 'form-control' 
  
    
    formMedHist.element('textarea[name=duration]')['_style'] = 'height:60px;line-height:1.0;'
    formMedHist.element('textarea[name=duration]')['_rows'] = 3
    formMedHist.element('textarea[name=duration]')['_class'] = 'form-control' 
  
    
  
    xnotesdate = formMedHist.element('input',_id='no_table_notesdate')
    xnotesdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xnotesdate['_data-date-format'] = 'dd/mm/yyyy'
    xnotesdate['_autocomplete'] = 'off'  
  
    
    xdob = formMedHist.element('input',_id='no_table_dob')
    xdob['_class'] =  'input-group form-control form-control-inline date-picker'
    xdob['_data-date-format'] = 'dd/mm/yyyy'
    xdob['_autocomplete'] = 'off'  
    
    xage = formMedHist.element('input',_id='no_table_age')
    xage['_class'] =  'form-control'
    xage['_type'] =  'text'
    xage['_placeholder'] = 'Enter Dental Tooth T1 to T32' 
    xage['_autocomplete'] = 'off'     
  
    xcell = formMedHist.element('input',_id='no_table_cell')
    xcell['_class'] =  'form-control'
    xcell['_type'] =  'text'
    
    xemail = formMedHist.element('input',_id='no_table_email')
    xemail['_class'] =  'form-control'
    xemail['_type'] =  'text'
    
    xtel = formMedHist.element('input',_id='no_table_telephone')
    xtel['_class'] =  'form-control'
    xtel['_type'] =  'text'
  
    xocc = formMedHist.element('input',_id='no_table_occupation')
    xocc['_class'] =  'form-control'
    xocc['_type'] =  'text'
  
    xref = formMedHist.element('input',_id='no_table_referer')
    xref['_class'] =  'form-control'
    xref['_type'] =  'text'
    
    xresoff = formMedHist.element('input',_id='no_table_resoff')
    xresoff['_class'] =  'form-control'
    xresoff['_type'] =  'text'

    xheight = formMedHist.element('input',_id='no_table_height')
    xheight['_class'] =  'form-control'
    xheight['_type'] =  'text'

    xweight = formMedHist.element('input',_id='no_table_weight')
    xweight['_class'] =  'form-control'
    xweight['_type'] =  'text'
    
    formMedHist.element('textarea[name=address]')['_style'] = 'height:50px;line-height:1.0;'
    formMedHist.element('textarea[name=address]')['_rows'] = 3
    formMedHist.element('textarea[name=address]')['_class'] = 'form-control'
  
    if formMedHist.accepts(request,session=session,formname='formnotes',keepvalues=True):
        db.medicalnotes.update_or_insert(((db.medicalnotes.patientid == patientid) & (db.medicalnotes.memberid == memberid) & (db.medicalnotes.is_active == True)),
                                         patientid = patientid,
                                         memberid = memberid,
                                         bp = common.getboolean(formMedHist.vars.bp),
                                         diabetes = common.getboolean(formMedHist.vars.diabetes),
                                         anaemia = common.getboolean(formMedHist.vars.anaemia),
                                         epilepsy = common.getboolean(formMedHist.vars.epilepsy),
                                         asthma = common.getboolean(formMedHist.vars.asthma),
                                         sinus = common.getboolean(formMedHist.vars.sinus),\
                                         heart = common.getboolean(formMedHist.vars.heart),\
                                         jaundice = common.getboolean(formMedHist.vars.jaundice),\
                                         tb = common.getboolean(formMedHist.vars.tb),\
                                         cardiac = common.getboolean(formMedHist.vars.cardiac),\
                                         arthritis = common.getboolean(formMedHist.vars.arthritis),\
                                         anyother = common.getboolean(formMedHist.vars.anyother),\
                                         allergic = True if request.vars.allergic == "1" else False,\
                                         excessivebleeding = True if request.vars.excessivebleeding == "1" else False,\
                                         seriousillness = True if request.vars.seriousillness == "1" else False,\
                                         hospitalized = True if request.vars.hospitalized == "1" else False,\
                                         medications = True if request.vars.medications == "1" else False,\
                                         surgery = True if request.vars.surgery == "1" else False,\
                                         pregnant = True if request.vars.pregnant == "1" else False,\
                                         breastfeeding = True if request.vars.breastfeeding == "1" else False,\
                                         anyothercomplaint = common.getstring(formMedHist.vars.anyothercomplaint),\
                                         chiefcomplaint = common.getstring(formMedHist.vars.chiefcomplaint),\
                                         duration = common.getstring(formMedHist.vars.duration),\
                                         occupation = common.getstring(formMedHist.vars.occupation),\
                                         referer = common.getstring(formMedHist.vars.referer),\
                                         resoff = common.getstring(formMedHist.vars.resoff),\
                                         height = common.getstring(formMedHist.vars.height),\
                                         weight = common.getstring(formMedHist.vars.weight),\
                                         
                                         is_active = True,\
                                         created_on = common.getISTFormatCurrentLocatTime(),\
                                         created_by = providerid,\
                                         modified_on = common.getISTFormatCurrentLocatTime(),\
                                         modified_by = providerid
                                         )   
        redirect(returnurl)
        
    elif formMedHist.errors:
        response.flash = "Error Treatment Update " + str(formMedHist.errors)    
  
      
    return dict(page=1,formMedHist=formMedHist,providerid=providerid,providername=providername,memberid=memberid,patientid=patientid,returnurl=returnurl)