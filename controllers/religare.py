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
        fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription, db.vw_treatmentprocedure.relgrprocdesc, \
                   db.vw_treatmentprocedure.tooth,db.vw_treatmentprocedure.quadrant,
                   db.vw_treatmentprocedure.procedurefee,db.vw_treatmentprocedure.inspays,db.vw_treatmentprocedure.copay,db.vw_treatmentprocedure.status,\
                   db.vw_treatmentprocedure.treatmentdate, db.vw_treatmentprocedure.relgrproc)

        
        headers={
            'vw_treatmentprocedure.procedurecode':'Code',
            'vw_treatmentprocedure.altshortdescription':'Description',
            'vw_treatmentprocedure.relgrprocdesc':'Religare Procedure'  if(session.religare ==  True) else '',
            'vw_treatmentprocedure.tooth':'Tooth',
            'vw_treatmentprocedure.quadrant':'Quadrant',
            'vw_treatmentprocedure.procedurefee':'Procedure Cost',
            'vw_treatmentprocedure.inspays':'Insurance Pays',
            'vw_treatmentprocedure.copay':'Co-Pay',
            'vw_treatmentprocedure.status':'Status',
            'vw_treatmentprocedure.treatmentdate':'Treatment Date'
        }
        
    else:
        fields=(db.vw_treatmentprocedure.procedurecode,db.vw_treatmentprocedure.altshortdescription, db.vw_treatmentprocedure.relgrprocdesc,\
                   db.vw_treatmentprocedure.tooth,db.vw_treatmentprocedure.quadrant,
                   db.vw_treatmentprocedure.procedurefee,db.vw_treatmentprocedure.status,\
                   db.vw_treatmentprocedure.treatmentdate,db.vw_treatmentprocedure.relgrproc)
        
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


#API-1 & API-2
def religare():
    
    
 

    message = ""
    providerdict = common.getprovider(auth, db)
    providerid = int(common.getid(providerdict["providerid"]))
    providername = providerdict["providername"]
    returnurl = URL('admin','providerhome')  
    
    
    sendotp = True
    validateotp = False
    mobile_number = request.vars.mobile_number
    ackid = request.vars.ackid
    customer_id = request.vars.customer_id
    policy_number = providerdict["rlgrpolicynumber"]
    voucher_code = request.vars.voucher_code
    
    form = SQLFORM.factory(
                Field('voucher_code', 'string',  label='Voucher Code',requires=IS_NOT_EMPTY(),default=voucher_code),
                Field('mobile_number', 'string',  label='Mobile Number',default=mobile_number),
                Field('policy_number', 'string',  label='Policy Number',default=policy_number),
                Field('customer_id', 'string',  label='Customer ID',default=customer_id),
                Field('ackid', 'string',  label='Ackid ID',default=ackid),
                Field('otp', 'string',  label='OTP'),
                Field('xaction','string',default='sendotp')
        )
    
    xcell = form.element('input',_id='no_table_voucher_code')
    xcell['_class'] =  'form-control placeholder-no-fix'
    xcell['_placeholder'] =  "Enter Smiling Card Code"
    xcell['_autocomplete'] =  'off'
    
    xotp = form.element('input',_id='no_table_otp')
    xotp['_class'] =  'form-control placeholder-no-fix'
    xotp['_placeholder'] =  'Enter OTP'
    xotp['_autocomplete'] =  'off'

    db.vw_memberpatientlist.id.readable = False
    
    if form.process().accepted:
	if(form.vars.xaction == "sendOTP"):
	    sendotp = False
	    validateotp = True

	    #POST API-I Send OTP
	    oreligare = mdpreligare.Religare(db,providerid)
	    jsonrsp = oreligare.sendOTP(form.vars.policy_number, form.vars.customer_id, form.vars.voucher_code)
	    jsonrsp = json.loads(jsonrsp)
	    if(jsonrsp["result"] == "success"):
		sendotp = False
		validateotp = True 
		ackid = jsonrsp["ackid"]
		customer_id = jsonrsp["customer_id"]
		
		xackid = form.element('input',_id='no_table_ackid')
		xackid['_default']  = ackid
		xackid['_value']  = ackid
		
		xcustid = form.element('input',_id='no_table_customer_id')
		xcustid['_default']  = customer_id
		xcustid['_value']  = customer_id
		
		message = "Enter OTP sent to customer's / patient's registered mobile phone"
	    else:
		sendotp = True
		validateotp = False 
		message = jsonrsp["error_message"]
	    
	if(form.vars.xaction == "validateOTP"):
	    #POST API-I Validate OTP
	    oreligare = mdpreligare.Religare(db,providerid)
	    jsonrsp = json.loads(oreligare.validateOTP(form.vars.ackid, form.vars.otp, form.vars.policy_number, form.vars.customer_id,form.vars.mobile_number))
	 
	    session.religarevalidmember = json.dumps(jsonrsp)
	    
	    if(jsonrsp["result"] == "success"):
		sendotp = False
		validateotp = False 
		message = "Authentication successful!"
		
		#call Select Document
		redirect(URL('religare','selectdocument'))
	    else:
		sendotp = True
		validateotp = False 
		message = jsonrsp["error_message"]
	    
	
	response.flash = ""
    elif form.errors:
	message = "OTP Form Error " + str(form.errors)
        
	    
    return dict(form=form,providername=providername,providerid=providerid,returnurl=returnurl,sendotp=sendotp, validateotp=validateotp,mobile_number=form.vars.mobile_number,voucher_code=form.vars.voucher_code,\
                ackid=form.vars.ackid,customer_id=form.vars.customer_id,message=message )    



#XXXAPI-1 & API-2
def religareXXX():
    
    
 

    message = ""
    providerdict = common.getprovider(auth, db)
    providerid = int(common.getid(providerdict["providerid"]))
    providername = providerdict["providername"]
    returnurl = URL('admin','providerhome')  
    
    
    sendotp = True
    validateotp = False
    mobile_number = request.vars.mobile_number
    ackid = request.vars.ackid
    customer_id = request.vars.customer_id
    policy_number = request.vars.policy_number
    voucher_code = request.vars.voucher_code
    policy_name = request.vars.policy_name
    
    #for development.
    #policy_number = "10406362"
    #voucher_code = "0002456781"
    
    form = SQLFORM.factory(
        
               
               
                Field('voucher_code', 'string',  label='Voucher Code',default=voucher_code),
                Field('mobile_number', 'string',  label='Mobile Number',default=mobile_number),
                Field('policy_number', 'string',  label='Policy Number',default=policy_number),
                Field('customer_id', 'string',  label='Customer ID',default=customer_id),
                Field('ackid', 'string',  label='Ackid ID',default=ackid),
                Field('otp', 'string',  label='OTP'),
                Field('xaction','string',default='sendotp')
        )

  

    
    xpn = form.element('input',_id='no_table_policy_number')
    xpn['_class'] =  'form-control placeholder-no-fix'
    xpn['_placeholder'] =  "Enter Policy Number"
    xpn['_autocomplete'] =  'off'

    xci = form.element('input',_id='no_table_customer_id')
    xci['_class'] =  'form-control placeholder-no-fix'
    xci['_placeholder'] =  "Enter Customer ID"
    xci['_autocomplete'] =  'off'
    
    xcell = form.element('input',_id='no_table_voucher_code')
    xcell['_class'] =  'form-control placeholder-no-fix'
    xcell['_placeholder'] =  "Enter Voucher Code (if customer id not entered)"
    xcell['_autocomplete'] =  'off'
    
    xotp = form.element('input',_id='no_table_otp')
    xotp['_class'] =  'form-control placeholder-no-fix'
    xotp['_placeholder'] =  'Enter OTP'
    xotp['_autocomplete'] =  'off'

    db.vw_memberpatientlist.id.readable = False
    
    if form.process().accepted:
	if(form.vars.xaction == "sendOTP"):
	
            
            #if((form.vars.customer_id == "") & (form.vars.voucher_code == "")):
		#message= "Please enter either Customer_ID or Voucher Code. Both cannot be empty"
	    #else:
	    sendotp = False
	    validateotp = True	    
	    #POST API-I Send OTP
	    oreligare = mdpreligare.ReligareXXX(db,providerid)
	    jsonrsp = oreligare.sendOTP(form.vars.policy_number, form.vars.customer_id, form.vars.voucher_code,policy_name)
	    jsonrsp = json.loads(jsonrsp)
	    if(jsonrsp["result"] == "success"):
		sendotp = False
		validateotp = True 
		ackid = jsonrsp["ackid"]
		jsonrsp["customer_type"] = "corporate" if(ackid.startswith("C_")) else\
	                        ("retail" if(ackid.startswith("R_")) else "")
		
		customer_id = jsonrsp["customer_id"]
		
		xackid = form.element('input',_id='no_table_ackid')
		xackid['_default']  = ackid
		xackid['_value']  = ackid
		
		xcustid = form.element('input',_id='no_table_customer_id')
		xcustid['_default']  = customer_id
		xcustid['_value']  = customer_id
		
		message_otp = "Enter OTP sent to customer's / patient's registered mobile phone"
	    else:
		sendotp = True
		validateotp = False 
		message = jsonrsp["error_message"]
       
	    
		
	if(form.vars.xaction == "validateOTP"):
	    #POST XXXAPI-I Validate OTP
	    oreligare = mdpreligare.ReligareXXX(db,providerid)
	    jsonrsp = json.loads(oreligare.validateOTP(form.vars.ackid, form.vars.otp, form.vars.policy_number, form.vars.customer_id,form.vars.voucher_code,form.vars.mobile_number,policy_name))
	    policy_name = getvalue(jsonrsp,"policy_name",policy_name)
	    
	      
	    
	    session.religarevalidmember = json.dumps(jsonrsp)
	    
	    if(jsonrsp["result"] == "success"):
		sendotp = False
		validateotp = False 
		message = "Authentication successful!"
		
		#call Select Document
		redirect(URL('religare','selectdocumentXXX'))
	    else:
		sendotp = True
		validateotp = False 
		message = jsonrsp["error_message"]
	    
	
	response.flash = ""
    elif form.errors:
	message = "OTP Form Error " + str(form.errors)
        
	    
    return dict(form=form,providername=providername,providerid=providerid,returnurl=returnurl,sendotp=sendotp, validateotp=validateotp,mobile_number=form.vars.mobile_number,voucher_code=form.vars.voucher_code,\
                ackid=form.vars.ackid,customer_id=form.vars.customer_id,policy_name = policy_name, message=message )    


def deletedocument():
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])
    
    returnurl = URL('admin','providerhome')
    
    docid = int(common.getid(request.vars.docid))
    docname = common.getstring(request.vars.docname)
    docfilename = common.getstring(request.vars.docfilename)
    
    
    if(docfilename == ""):
	redirect(returnurl)
    else:
	form = FORM.confirm('Yes?',{'No':URL('religare','uploaddocument',vars=dict(docid=docid,docname=docname,docfilename=docfilename))})
    
    if form.accepted:
	#delete the file form web2py uploads folder
	if os.path.exists(docname):
	    os.remove(docname)
	db(db.rlgdocument.id == docid).delete()
	#return to selectdocument with empty file
	redirect(URL('religare','selectdocument'))    
	    
    return dict(form=form,docfilename=docfilename,providerid=providerid,providername=providername,returnurl=returnurl)


#API-3
def uploaddocument():
    
    errormssg = ""
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])

    

    religaremember = None if session.religarevalidmember == None else json.loads(session.religarevalidmember)
    ackid = "" if religaremember == None else religaremember["ackid"]
    membername = "" if religaremember == None else religaremember["membername"]
    customer_id  = "" if religaremember == None else religaremember["customer_id"]
   
    policy_number = "" if religaremember == None else religaremember["policy_number"]
    mobile_number = "" if religaremember == None else religaremember["mobile_number"]
    
    
    #ackid = "72dd2b2a4a"
    #customer_id = "ci_9916314080"
    #policy_number = "13713771"
    #membername = "DIVYANSHI"    
    #mobile_number = "9916314080"    

    docname = common.getstring(request.vars.docname)
    docfilename = common.getstring(request.vars.docfilename)
    docid = int(common.getid(request.vars.docid))

    form = SQLFORM.factory(
                   Field('membername', 'string',  label='Customer ID',default=membername),
                   Field('customer_id', 'string',  label='Customer ID',default=customer_id),
                   Field('policy_number', 'string',  label='Policy Number',default=policy_number),
                   Field('mobile_number', 'string',  label='Mobile Number',default=mobile_number),
                   Field('rlgdocument', 'string',  label='Document', default=docname),
                   Field('rlgdocument_filename', 'string',  label='Document', default=docfilename),
           )    

    
    
    xmembername = form.element('input',_id='no_table_membername')
    if(xmembername != None):
	xmembername['_class'] =  'form-control '
	xmembername['_autocomplete'] = 'off'         
	xmembername['_style'] = 'width:100%'    

    xcustomer_id = form.element('input',_id='no_table_customer_id')
    if(xcustomer_id != None):
	xcustomer_id['_class'] =  'form-control '
	xcustomer_id['_autocomplete'] = 'off'         
	xcustomer_id['_style'] = 'width:100%'    

    xpolicy_number = form.element('input',_id='no_table_policy_number')
    if(xpolicy_number != None):
	xpolicy_number['_class'] =  'form-control '
	xpolicy_number['_autocomplete'] = 'off'         
	xpolicy_number['_style'] = 'width:100%'    

    xmobile_number = form.element('input',_id='no_table_mobile_number')
    if(xmobile_number != None):
	xmobile_number['_class'] =  'form-control '
	xmobile_number['_autocomplete'] = 'off'         
	xmobile_number['_style'] = 'width:100%'    
	
    xrlgdocument_filename = form.element('input',_id='no_table_rlgdocument_filename')
    if(xrlgdocument_filename != None):
	xrlgdocument_filename['_class'] =  'form-control '
	xrlgdocument_filename['_autocomplete'] = 'off'         
	xrlgdocument_filename['_style'] = 'width:100%'    


    if form.process().accepted:
	filename = os.path.join(request.folder,'uploads') + "\\" + docname
	file_data = ""
	
	with open(filename, "rb") as binary_file:
	    #Read the whole file at once
	    file_data =  base64.b64encode(binary_file.read())
	
	#POST API-3 Upload Document
	oreligare = mdpreligare.Religare(db,providerid)
	jsonrsp = oreligare.uploadDocument(ackid, file_data, filename, policy_number, 
                                          customer_id, 
                                          mobile_number)
	jsonrsp = json.loads(jsonrsp)
	
	if(jsonrsp["result"] == "success"):
	    redirect(URL('religare','religarepatient'))
	else:
	    redirect(URL('religare','religareerror',vars=dict(errorcode=jsonrsp["error_code"])))
    elif form.errors:
	errormssg = "Form Errors: " + str(form.errors)
    
    returnurl = URL('religare','deletedocument',vars=dict(docid=docid,docname=docname,docfilename=docfilename))
    return dict(form =form, docname=docname, docid=docid, docfilename=docfilename, providerid = providerid, providername = providername, returnurl=returnurl, errormssg = errormssg)
    
#API-3
def uploaddocumentXXX():
    
    errormssg = ""
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])

    

    religaremember = None if session.religarevalidmember == None else json.loads(session.religarevalidmember)
    member = None if session.religarevalidmember == None else religaremember.get("member_detials",None)
    member = None if member == None else (member[0] if(len(member) > 0) else None)  #first is alway primary member
    
    ackid = "" if religaremember == None else getvalue(religaremember,"ackid","")
    membername = "" if member == None else getvalue(member,"membername","")
    customer_id  = "" if member == None else getvalue(member,"customerid","")
    primary_customer_id  = "" if member == None else getvalue(member,"primary_customerid",customer_id)
    mobile_number = "" if member == None else getvalue(member,"mobile_number","")
    
    policy_number = "" if religaremember == None else getvalue(religaremember,"policy_number","")
    policy_name = "" if religaremember == None else getvalue(religaremember,"policy_name","")
    voucher_code = "" if religaremember == None else getvalue(religaremember,"voucher_code","")
  

    docname = common.getstring(request.vars.docname)
    docfilename = common.getstring(request.vars.docfilename)
    docid = int(common.getid(request.vars.docid))

    form = SQLFORM.factory(
                   Field('membername', 'string',  label='Customer ID',default=membername),
                   Field('customer_id', 'string',  label='Customer ID',default=customer_id),
                   Field('voucher_code', 'string',  label='Customer ID',default=voucher_code),
                   Field('policy_number', 'string',  label='Policy Number',default=policy_number),
                   Field('policy_name', 'string',  label='Policy Number',default=policy_name),
                   Field('mobile_number', 'string',  label='Mobile Number',default=mobile_number),
                   Field('rlgdocument', 'string',  label='Document', default=docname),
                   Field('rlgdocument_filename', 'string',  label='Document', default=docfilename),
           )    

    
    
    xmembername = form.element('input',_id='no_table_membername')
    if(xmembername != None):
	xmembername['_class'] =  'form-control '
	xmembername['_autocomplete'] = 'off'         
	xmembername['_style'] = 'width:100%'    

    xcustomer_id = form.element('input',_id='no_table_customer_id')
    if(xcustomer_id != None):
	xcustomer_id['_class'] =  'form-control '
	xcustomer_id['_autocomplete'] = 'off'         
	xcustomer_id['_style'] = 'width:100%'    
	
    xvc = form.element('input',_id='no_table_voucher_code')
    if(xvc != None):
	xvc['_class'] =  'form-control '
	xvc['_autocomplete'] = 'off'         
	xvc['_style'] = 'width:100%'    

    xpolicy_number = form.element('input',_id='no_table_policy_number')
    if(xpolicy_number != None):
	xpolicy_number['_class'] =  'form-control '
	xpolicy_number['_autocomplete'] = 'off'         
	xpolicy_number['_style'] = 'width:100%'    
    xpn = form.element('input',_id='no_table_policy_name')
    if(xpn != None):
	xpn['_class'] =  'form-control '
	xpn['_autocomplete'] = 'off'         
	xpn['_style'] = 'width:100%'    

    xmobile_number = form.element('input',_id='no_table_mobile_number')
    if(xmobile_number != None):
	xmobile_number['_class'] =  'form-control '
	xmobile_number['_autocomplete'] = 'off'         
	xmobile_number['_style'] = 'width:100%'    
	
    xrlgdocument_filename = form.element('input',_id='no_table_rlgdocument_filename')
    if(xrlgdocument_filename != None):
	xrlgdocument_filename['_class'] =  'form-control '
	xrlgdocument_filename['_autocomplete'] = 'off'         
	xrlgdocument_filename['_style'] = 'width:100%'    


    if form.process().accepted:
	filename = os.path.join(request.folder,'uploads') + "\\" + docname
	file_data = ""
	
	with open(filename, "rb") as binary_file:
	    #Read the whole file at once
	    file_data =  base64.b64encode(binary_file.read())
	
	#POST API-3 Upload Document
	oreligare = mdpreligare.ReligareXXX(db,providerid)
	jsonrsp = oreligare.uploadDocument(ackid, file_data, filename, policy_number, 
                                          primary_customer_id, customer_id, 
	                                  voucher_code,
                                          mobile_number,
	                                  policy_name)
	jsonrsp = json.loads(jsonrsp)
	
	if(jsonrsp["result"] == "success"):
	    redirect(URL('religare','religarepatientXXX'))
	else:
	    redirect(URL('religare','religareerror',vars=dict(errorcode=jsonrsp["error_code"])))
    elif form.errors:
	errormssg = "Form Errors: " + str(form.errors)
    
    returnurl = URL('religare','deletedocument',vars=dict(docid=docid,docname=docname,docfilename=docfilename))
    return dict(form =form, docname=docname, docid=docid, docfilename=docfilename, providerid = providerid, providername = providername, returnurl=returnurl, errormssg = errormssg)

def selectdocument():
    

    errormssg = ""
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])

    returnurl = URL('admin','providerhome')  
    

    religaremember = None if session.religarevalidmember == None else json.loads(session.religarevalidmember)
    ackid = "" if religaremember == None else religaremember["ackid"]
    membername = "" if religaremember == None else religaremember["membername"]
    customer_id  = "" if religaremember == None else religaremember["customer_id"]
    policy_number = "" if religaremember == None else religaremember["policy_number"]
    mobile_number = "" if religaremember == None else religaremember["mobile_number"]
    
    
    #ackid = "72dd2b2a4a"
    #customer_id = "ci_9916314080"
    #policy_number = "13713771"
    #membername = "DIVYANSHI"    
    #mobile_number = "9916314080"    
    

    
    db.rlgdocument.membername.default = membername
    db.rlgdocument.ackid.default = ackid
    db.rlgdocument.customer_id.default = customer_id
    db.rlgdocument.policy_number.default = policy_number
    db.rlgdocument.mobile_number.default = mobile_number
    db.rlgdocument.is_active.default = True,
    db.rlgdocument.created_by.default = 1 if(auth.user == None) else auth.user.id,
    db.rlgdocument.modified_by.default = 1 if(auth.user == None) else auth.user.id,

    form = SQLFORM(db.rlgdocument)
    
    xmembername = form.element('input',_id='rlgdocument_membername')
    if(xmembername != None):
	xmembername['_class'] =  'form-control '
	xmembername['_autocomplete'] = 'off'         
	xmembername['_style'] = 'width:100%'    

    xcustomer_id = form.element('input',_id='rlgdocument_customer_id')
    if(xcustomer_id != None):
	xcustomer_id['_class'] =  'form-control '
	xcustomer_id['_autocomplete'] = 'off'         
	xcustomer_id['_style'] = 'width:100%'    

    xpolicy_number = form.element('input',_id='rlgdocument_policy_number')
    if(xpolicy_number != None):
	xpolicy_number['_class'] =  'form-control '
	xpolicy_number['_autocomplete'] = 'off'         
	xpolicy_number['_style'] = 'width:100%'    

    xmobile_number = form.element('input',_id='rlgdocument_mobile_number')
    if(xmobile_number != None):
	xmobile_number['_class'] =  'form-control '
	xmobile_number['_autocomplete'] = 'off'         
	xmobile_number['_style'] = 'width:100%'    
	
    xrlgdocument_filename = form.element('input',_id='rlgdocument_rlgdocument_filename')
    if(xrlgdocument_filename != None):
	xrlgdocument_filename['_class'] =  'form-control '
	xrlgdocument_filename['_autocomplete'] = 'off'         
	xrlgdocument_filename['_style'] = 'width:100%'    
   
    xrlgdocument_docdate= form.element('input',_id='rlgdocument_docdate')
    if(xrlgdocument_docdate != None):
	xrlgdocument_docdate['_class'] =  'form-control '
	xrlgdocument_docdate['_autocomplete'] = 'off'         
	xrlgdocument_docdate['_style'] = 'width:100%'    
       
   
    if form.process().accepted:
	docid = form.vars.id
	docname = form.vars.rlgdocument
	docfilename = request.vars.rlgdocument.filename
	db(db.rlgdocument.id == docid).update(rlgdocument_filename = docfilename)
	redirect(URL('religare','uploaddocument',vars=dict(docid=docid,docname=docname,docfilename=docfilename)))
	
    elif form.errors:
	session.flash = "Form Errors " + str(form.errors)
	
    return dict(form =form,  providerid = providerid, providername = providername, returnurl=returnurl, errormssg = errormssg)

def selectdocumentXXX():
    

    errormssg = ""
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])

    returnurl = URL('admin','providerhome')  
    

    religaremember = None if session.religarevalidmember == None else json.loads(session.religarevalidmember)
    member = None if session.religarevalidmember == None else religaremember.get("member_detials",None)
    member = None if member == None else (member[0] if(len(member) >  0) else None)   #first is alway primary member
    
    ackid = "" if religaremember == None else getvalue(religaremember,"ackid","")
    membername = "" if member == None else getvalue(member,"membername","")
    customer_id  = "" if member == None else getvalue(member,"customerid","")
    mobile_number = "" if member == None else getvalue(member,"mobile_number","")
    
    policy_number = "" if religaremember == None else getvalue(religaremember,"policy_number","")
    policy_name = "" if religaremember == None else getvalue(religaremember,"policy_name","")
    voucher_code = "" if religaremember == None else getvalue(religaremember,"voucher_code","")
      
    

    
    db.rlgdocument.membername.default = membername
    db.rlgdocument.ackid.default = ackid
    db.rlgdocument.customer_id.default = customer_id
    db.rlgdocument.policy_number.default = policy_number
    db.rlgdocument.policy_name.default = policy_name
    db.rlgdocument.voucher_code.default = voucher_code
    db.rlgdocument.mobile_number.default = mobile_number
    db.rlgdocument.is_active.default = True,
    db.rlgdocument.created_by.default = 1 if(auth.user == None) else auth.user.id,
    db.rlgdocument.modified_by.default = 1 if(auth.user == None) else auth.user.id,

    form = SQLFORM(db.rlgdocument)
    
    xmembername = form.element('input',_id='rlgdocument_membername')
    if(xmembername != None):
	xmembername['_class'] =  'form-control '
	xmembername['_autocomplete'] = 'off'         
	xmembername['_style'] = 'width:100%'    

    xcustomer_id = form.element('input',_id='rlgdocument_customer_id')
    if(xcustomer_id != None):
	xcustomer_id['_class'] =  'form-control '
	xcustomer_id['_autocomplete'] = 'off'         
	xcustomer_id['_style'] = 'width:100%'    

    xvc = form.element('input',_id='rlgdocument_voucher_code')
    if(xvc != None):
	xvc['_class'] =  'form-control '
	xvc['_autocomplete'] = 'off'         
	xvc['_style'] = 'width:100%'    


    xpolicy_number = form.element('input',_id='rlgdocument_policy_number')
    if(xpolicy_number != None):
	xpolicy_number['_class'] =  'form-control '
	xpolicy_number['_autocomplete'] = 'off'         
	xpolicy_number['_style'] = 'width:100%'    

    xpn = form.element('input',_id='rlgdocument_policy_name')
    if(xpn != None):
	xpn['_class'] =  'form-control '
	xpn['_autocomplete'] = 'off'         
	xpn['_style'] = 'width:100%'    


    xmobile_number = form.element('input',_id='rlgdocument_mobile_number')
    if(xmobile_number != None):
	xmobile_number['_class'] =  'form-control '
	xmobile_number['_autocomplete'] = 'off'         
	xmobile_number['_style'] = 'width:100%'    
	
    xrlgdocument_filename = form.element('input',_id='rlgdocument_rlgdocument_filename')
    if(xrlgdocument_filename != None):
	xrlgdocument_filename['_class'] =  'form-control '
	xrlgdocument_filename['_autocomplete'] = 'off'         
	xrlgdocument_filename['_style'] = 'width:100%'    
   
    xrlgdocument_docdate= form.element('input',_id='rlgdocument_docdate')
    if(xrlgdocument_docdate != None):
	xrlgdocument_docdate['_class'] =  'form-control '
	xrlgdocument_docdate['_autocomplete'] = 'off'         
	xrlgdocument_docdate['_style'] = 'width:100%'    
       
   
    if form.process().accepted:
	docid = form.vars.id
	docname = form.vars.rlgdocument
	docfilename = request.vars.rlgdocument.filename
	db(db.rlgdocument.id == docid).update(rlgdocument_filename = docfilename)
	redirect(URL('religare','uploaddocumentXXX',vars=dict(docid=docid,docname=docname,docfilename=docfilename)))
	
    elif form.errors:
	session.flash = "Form Errors " + str(form.errors)
	
    return dict(form =form,  providerid = providerid, providername = providername, returnurl=returnurl, errormssg = errormssg)



def religarepatient():
    
    page = 1
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])    
    returnurl = URL('admin','providerhome') 
    
    religaremember = None if session.religarevalidmember == None else json.loads(session.religarevalidmember)
    ackid = "" if religaremember == None else religaremember["ackid"]
    membername = "" if religaremember == None else religaremember["membername"]
    customer_id  = "" if religaremember == None else religaremember["customer_id"]
    policy_number = "" if religaremember == None else religaremember["policy_number"]
    mobile_number = "" if religaremember == None else religaremember["mobile_number"]
    dob = "1990-01-01" if religaremember == None else religaremember["dob"]
    xgender = "M" if religaremember == None else religaremember["gender"]
    
    #ackid = "72dd2b2a4a"
    #customer_id = "ci_9916314080"
    #policy_number = "13713771"
    #membername = "DIVYANSHI"    
    #mobile_number = "9916314080"
    #memberid = 13073
    #patientid = 13073
    #dob = "1990-01-01"
    #xgender = "M"
    
    
    oreligare = mdpreligare.Religare(db,providerid)
    rsp = oreligare.getreligarepatient(customer_id,membername,mobile_number,dob,xgender)
    patobj = json.loads(rsp)
    memberid = common.getid(patobj["memberid"])
    session.religarepatient = json.dumps(patobj)
    
    if(memberid == 0):
        raise HTTP(403,"Error: No Religare Member")
    
    query = ((db.patientmember.id == memberid) & (db.patientmember.is_active == True))
    
    members = db(query).select(db.patientmember.ALL,db.company.name, db.hmoplan.name, db.groupregion.groupregion,db.groupregion.id,
                               left = [db.company.on (db.company.id == db.patientmember.company), db.hmoplan.on(db.hmoplan.id == db.patientmember.hmoplan),\
                                       db.groupregion.on(db.groupregion.id == db.patientmember.groupregion)]
                               )
                               

    if(memberid == 0):
        raise HTTP(403,"Error: No Religare Member")

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
	
	redirect(URL('religare','religarepatient'))
	
    return dict(providername=providername, providerid = providerid, formA=formA,\
                member=member,fname=fname,lname=lname,cell=cell,email=email,page=page,\
                returnurl=returnurl)
    
    
def religarepatientXXX():
    
    page = 1
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])    
    returnurl = URL('admin','providerhome') 
    
    religaremember = None if session.religarevalidmember == None else json.loads(session.religarevalidmember)
    member = None if session.religarevalidmember == None else religaremember.get("member_detials",None)
    member = None if member == None else (member[0] if(len(member) > 0) else None)   #first is alway primary member
    
    ackid = "" if religaremember == None else getvalue(religaremember,"ackid","")
    membername = "" if member == None else getvalue(member,"membername","")
    customer_id  = "" if member == None else getvalue(member,"customerid","")
    mobile_number = "" if member == None else getvalue(member,"mobile_number","")
    
    policy_number = "" if religaremember == None else getvalue(religaremember,"policy_number","")
    policy_name = "" if religaremember == None else getvalue(religaremember,"policy_name","")
    voucher_code = "" if religaremember == None else getvalue(religaremember,"voucher_code","")
   
    
    
    oreligare = mdpreligare.ReligareXXX(db,providerid)
    rsp = oreligare.getreligarepatient(religaremember)
    patobj = json.loads(rsp)
    
    memberid = common.getid(patobj["memberid"])
    session.religarepatient = json.dumps(patobj)
    
    if(memberid == 0):
        raise HTTP(403,"Error: No Religare Member")
    
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
    
    
    #dependant grid
    fields=(db.patientmemberdependants.title,
            db.patientmemberdependants.fname,
            db.patientmemberdependants.lname,
            db.patientmemberdependants.depdob,
            db.patientmemberdependants.relation)
    
       
    
    headers={
        
             'patientmemberdependants.title':'CustomerID',
             'patientmemberdependants.fname':'First Name',
             'patientmemberdependants.lname': 'Last Name',
             'patientmemberdependants.depdob': 'DOB',
             'patientmemberdependants.relation':'Relation'
	         }
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)
    
    left = None
    links = [lambda row: A('Add Treatment',_href=URL("religare","religaretreatmentXXX", vars=dict(mode='dependant',customerid = row.title)))] 
             
             #lambda row: A('Delete',_href=URL("member","delete_dependant",args=[row.id,memberid]))]
    
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
    
    if(formA.process().accepted):
	
	#save addr1,2,3,city,st,pin,cell,email,groupregion
	db(db.patientmember.id == memberid).update(address1=formA.vars.address1,address2=formA.vars.address2,address3=formA.vars.address3,\
	                                           city=formA.vars.city,st=formA.vars.st,groupregion=formA.vars.groupregion,email=formA.vars.email,cell=formA.vars.cell)
	
	redirect(URL('religare','religarepatientXXX'))
	
    return dict(providername=providername, providerid = providerid, formA=formA, formB=formB,\
                member=member,fname=fname,lname=lname,cell=cell,email=email,page=page,\
                returnurl=returnurl)
    

#New Treatment
def religaretreatment():
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])

    #constants that are used for development.  In actual, these have to come from session.religarepatient
    religaremember = None if session.religarevalidemember == None else json.loads(session.religarevalidmember)
    ackid = "" if religaremember == None else religaremember["ackid"]
    membername = "" if religaremember == None else religaremember["membername"]
    customer_id  = "" if religaremember == None else religaremember["customer_id"]
    policy_number = "" if religaremember == None else religaremember["policy_number"]
    mobile_number = "" if religaremember == None else religaremember["mobile_number"]       
    phone_number = mobile_number

    #ackid = "72dd2b2a4a"
    #customer_id = "ci_9916314080"
    #policy_number = "13713771"
    #membername = "DIVYANSHI"
    
    patobj = json.loads(session.religarepatient)
    memberid = int(common.getid(patobj["memberid"]))
    patientid = int(common.getid(patobj["patientid"]))
    p = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.patientmember,\
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
    rsp = otrtmnt.newtreatment(memberid,patientid)
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
           Field('chiefcomplaint','string',label='Chief Complaint', default=treatments[0].chiefcomplaint,writable=False),
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
                freetreatment=freetreatment,newmember=newmember,showprocgrid = showprocgrid
                )        

#New Treatment
def religaretreatmentXXX():
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])

    #constants that are used for development.  In actual, these have to come from session.religarepatient
    religaremember = None if session.religarevalidmember == None else json.loads(session.religarevalidmember)
    member_detials = None if session.religarevalidmember == None else religaremember.get("member_detials",None)
    member = None if member_detials == None else (member_detials[0] if(len(member_detials) > 0) else None) #first is alway primary member
    
    ackid = "" if religaremember == None else getvalue(religaremember,"ackid","")
    membername = "" if member == None else getvalue(member,"membername","")
    customer_id  = "" if member == None else getvalue(member,"customerid","")
    mobile_number = "" if member == None else getvalue(member,"mobile_number","")
    
    policy_number = "" if religaremember == None else getvalue(religaremember,"policy_number","")
    policy_name = "" if religaremember == None else getvalue(religaremember,"policy_name","")
    voucher_code = "" if religaremember == None else getvalue(religaremember,"voucher_code","")

    
    patobj = json.loads(session.religarepatient)
    memberid = int(common.getid(patobj["memberid"]))
    patientid = int(common.getid(patobj["memberid"]))
    if(request.vars.mode == "dependant"):
      deps = patobj["dependants"]
      count = int(common.getid(deps["count"]))
      deplist = deps["deplist"]
      for i in xrange(count):
	if(deplist[i]["groupref"] == request.vars.customerid):
	  patientid = int(common.getid(deplist[i]["patientid"]))
	  break;
      
    else:
      patientid = int(common.getid(patobj["patientid"]))
      
    p = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.patientmember,\
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
    rsp = otrtmnt.newtreatment(memberid,patientid,policy_name)
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
           Field('chiefcomplaint','string',label='Chief Complaint', default=treatments[0].chiefcomplaint,writable=False),
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
                freetreatment=freetreatment,newmember=newmember,showprocgrid = showprocgrid
                )        


def updatereligaretreatment():
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])


    patientmember =""
    groupref = ""
    patienttype = "P"
    hmopatientmember = True
    freetreatment = True
    newmember = False
       

    treatmentid = int(common.getid(request.vars.treatmentid))
    otrtmnt = mdptreatment.Treatment(current.globalenv['db'],providerid)
    rsp = otrtmnt.gettreatment(treatmentid)
    treatmentobj = json.loads(rsp)    
    
    
    #constants that are used for development.  In actual, these have to come from session.religarepatient
    #religaremember = None if session.religarevalidemember == None else json.loads(session.religarevalidmember)
    #ackid = "" if religaremember == None else religaremember["ackid"]
    #membername = "" if religaremember == None else religaremember["membername"]
    #customer_id  = "" if religaremember == None else religaremember["customer_id"]
    #policy_number = "" if religaremember == None else religaremember["policy_number"]
    #mobile_number = "" if religaremember == None else religaremember["mobile_number"]       
    #phone_number = mobile_number

    #ackid = "72dd2b2a4a"
    #customer_id = "ci_9916314080"
    #policy_number = "13713771"
    #membername = "DIVYANSHI"
    #mobile_number = "9916314080"
    #phone_number = mobile_number
    
    
    #patobj = json.loads(session.religarepatient)
    #memberid = int(common.getid(patobj["memberid"]))
    #patientid = int(common.getid(patobj["patientid"]))
    #patientid = 13061
    #memberid = 13061    
    #p = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.patientmember,\
                                                                                                                             #db.vw_memberpatientlist.groupref,\
                                                                                                                             #db.vw_memberpatientlist.patienttype,\
                                                                                                                             #db.vw_memberpatientlist.hmopatientmember,\
                                                                                                                             #db.vw_memberpatientlist.freetreatment,\
                                                                                                                             #db.vw_memberpatientlist.newmember)
                                                                                                                             
   
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
            #calculatecost(tplanid)
            #calculatecopay(db, tplanid,memberid)
            #calculateinspays(tplanid)
            #calculatedue(tplanid)
            
            #db.commit()                
        
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
                freetreatment=freetreatment,newmember=newmember,showprocgrid = showprocgrid
                )        

def updatereligaretreatmentXXX():
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])


    patientmember =""
    groupref = ""
    patienttype = "P"
    hmopatientmember = True
    freetreatment = True
    newmember = False
       

    treatmentid = int(common.getid(request.vars.treatmentid))
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
                freetreatment=freetreatment,newmember=newmember,showprocgrid = showprocgrid
                )        


#call API-4            
def gettransactionid():
    
    
    religaremember = None if(session.religarevalidmember == None) else json.loads(session.religarevalidmember)
    ackid = "" if religaremember == None else religaremember["ackid"]
    membername = "" if religaremember == None else religaremember["membername"]
    customer_id  = "" if religaremember == None else religaremember["customer_id"]
    policy_number = "" if religaremember == None else religaremember["policy_number"]
    mobile_number = "" if religaremember == None else religaremember["mobile_number"]    

    treatmentid = int(common.getid(request.vars.treatmentid))
    providerid = int(common.getid(request.vars.providerid))
    
    patobj = json.loads(session.religarepatient)
    memberid = int(common.getid(patobj["memberid"]))
    patientid = int(common.getid(patobj["patientid"]))
    
    r = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.procedurepriceplancode)
    procedurepriceplancode = r[0].procedurepriceplancode if(len(r) == 1) else "RLG102"
    
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
    
    #def geTransactionID(self,ackid,service_id,procedurecode, procedurename,procedurefee,\
                         #procedurepiceplancode,policy_number,customer_id,mobile_number):    
    
    #call API-4 (get transaction ID)
    oreligare = mdpreligare.Religare(db,providerid)
    rsp = oreligare.geTransactionID(ackid, service_id, procedurecode, 
                                   procedurename, 
                                   procedurefee, 
                                   procedurepriceplancode, 
                                   policy_number, 
                                   customer_id, 
                                   mobile_number)
    
    jsonobj = json.loads(rsp)
    session.transactionID = rsp
    
    #jsonresp["procedurecode"] = procedurecode
		 #jsonresp["procedurename"] = procedurename
		 #jsonresp["procedurefee"] = procedurefee
		 #jsonresp["procedurepiceplancode"] = procedurepiceplancode
		 #jsonresp["result"] = "success"
		 #jsonresp["error_message"] = ""              
		 #jsonresp["customer_id"] = customer_id
		 #jsonresp["policy_number"] = policy_number
		 #jsonresp["mobile_number"] = mobile_number  
		 #"response_status" : true, //if policy information is correct.
		 #"response_message" : "",
		 #“error_code” : “”,
		 #“ackid” : “”,
		 #“transaction_id” : “”,
		 #“transaction_amount” : “”,
		 #“copay” : “”		 
    if(jsonobj["result"] == "success"):
	#go to Transaction OTP Validation Screen
	redirect(URL('religare','validatetransaction',vars=dict(treatmentid=treatmentid,tooth=request.vars.tooth,quadrant=request.vars.quadrant)))
    else:
	#go to error screen
	redirect(URL('religare','religareerror',vars=dict(errorcode=jsonobj["error_code"])))
    
    
    return dict()

#call API-4            
def gettransactionidXXX():
    
    
    #constants that are used for development.  In actual, these have to come from session.religarepatient
    religaremember = None if session.religarevalidmember == None else json.loads(session.religarevalidmember)
    member = None if session.religarevalidmember == None else religaremember.get("member_detials",None)
    member = None if member == None else (member[0] if(len(member) > 0) else None)   #first is alway primary member
    
    ackid = "" if religaremember == None else getvalue(religaremember,"ackid","")
    membername = "" if member == None else getvalue(member,"membername","")
    customer_id  = "" if member == None else getvalue(member,"customerid","")
    mobile_number = "" if member == None else getvalue(member,"mobile_number","")
    
    policy_number = "" if religaremember == None else getvalue(religaremember,"policy_number","")
    policy_name = "" if religaremember == None else getvalue(religaremember,"policy_name","")
    voucher_code = "" if religaremember == None else getvalue(religaremember,"voucher_code","")


    treatmentid = int(common.getid(request.vars.treatmentid))
    providerid = int(common.getid(request.vars.providerid))
    
    patobj = json.loads(session.religarepatient)
    memberid = int(common.getid(patobj["memberid"]))
    patientid = int(common.getid(patobj["patientid"]))
    
    #r = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.procedurepriceplancode)
    
    procedurepriceplancode = mdputils.getprocedurepriceplancodeformember(db,providerid,memberid,patientid,policy_name)  #r[0].procedurepriceplancode if(len(r) == 1) else "RLG102"
    
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
    
    
    #call API-4 (get transaction ID)
    oreligare = mdpreligare.ReligareXXX(db,providerid)
    rsp = oreligare.geTransactionID(ackid, service_id, procedurecode, 
                                   procedurename, 
                                   procedurefee, 
                                   procedurepriceplancode, 
                                   policy_number, 
                                   customer_id, 
                                   mobile_number,
                                   voucher_code,
                                   policy_name)
    
    jsonobj = json.loads(rsp)
    session.transactionID = rsp
    
     
    if(jsonobj["result"] == "success"):
	#go to Transaction OTP Validation Screen
	redirect(URL('religare','validatetransactionXXX',vars=dict(treatmentid=treatmentid,tooth=request.vars.tooth,quadrant=request.vars.quadrant)))
    else:
	#go to error screen
	redirect(URL('religare','religareerror',vars=dict(errorcode=jsonobj["error_code"])))
    
    
    return dict()


#API-5
def validatetransaction():
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])    

    
   
    form = SQLFORM.factory(
        Field('otp', 'string',  label='OTP')
    )
    xotp = form.element('input',_id='no_table_otp')
    xotp['_class'] =  'form-control placeholder-no-fix'
    xotp['_placeholder'] =  'Enter OTP'
    xotp['_autocomplete'] =  'off'    

    treatmentid = int(common.getid(request.vars.treatmentid))
    tooth = request.vars.tooth
    quadrant = request.vars.quadrant
    remarks = request.vars.remarks

    message = ""
    
    if form.process().accepted:
	
	
	transactionID = json.loads(session.transactionID)
	procedurepriceplancode = transactionID["procedurepiceplancode"]
	procedurecode = transactionID["procedurecode"]
	procedurename = transactionID["procedurename"]
	procedurefee = transactionID["procedurefee"]
	
	
	religaremember = json.loads(session.religarevalidmember)
	ackid = "" if religaremember == None else religaremember["ackid"]
	customer_id  = "" if religaremember == None else religaremember["customer_id"]
	policy_number = "" if religaremember == None else religaremember["policy_number"]
	mobile_number = "" if religaremember == None else religaremember["mobile_number"] 	
	
	#POST API-5 Validate Transaction OTP
	oreligare = mdpreligare.Religare(db,providerid)
	rsp = oreligare.addRlgProcedureToTreatment(ackid, form.vars.otp, treatmentid, 
	                                    procedurepriceplancode, 
	                                    procedurecode, 
	                                    procedurename, 
	                                    procedurefee, 
	                                    tooth, 
	                                    quadrant, 
	                                    remarks, 
	                                    policy_number, 
	                                    customer_id, 
	                                    mobile_number)
     
	jsonrsp  = json.loads(rsp)
	if(jsonrsp["result"] == "success"):
	    redirect(URL('religare','updatereligaretreatment',vars=dict(treatmentid=treatmentid)))
	else:
	    #go to error screen
	    redirect(URL('religare','religareerror',vars=dict(errorcode=jsonrsp["error_code"])))
    elif form.errors:
	session.flash = "Form Error - Validate Transaction " + str(form.errors)
	message = "Form Error - Validate Transaction " + str(form.errors)
	
    returnurl = URL('admin','providerhome')	
    return dict(form=form,providerid=providerid, providername=providername,returnurl=returnurl,message=message)


#API-5
def validatetransactionXXX():
    
    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])    

     

    form = SQLFORM.factory(
        Field('otp', 'string',  label='OTP')
    )
    xotp = form.element('input',_id='no_table_otp')
    xotp['_class'] =  'form-control placeholder-no-fix'
    xotp['_placeholder'] =  'Enter OTP'
    xotp['_autocomplete'] =  'off'    

    treatmentid = int(common.getid(request.vars.treatmentid))
    tooth = request.vars.tooth
    quadrant = request.vars.quadrant
    remarks = request.vars.remarks

    message = ""
    
    if form.process().accepted:
	
	
	transactionID = json.loads(session.transactionID)
	procedurepriceplancode = transactionID["procedurepiceplancode"]
	procedurecode = transactionID["procedurecode"]
	procedurename = transactionID["procedurename"]
	procedurefee = transactionID["procedurefee"]
	
	
	
	#constants that are used for development.  In actual, these have to come from session.religarepatient
	religaremember = None if session.religarevalidmember == None else json.loads(session.religarevalidmember)
	member = None if session.religarevalidmember == None else religaremember.get("member_detials",None)
	member = None if member == None else (member[0] if(len(member) > 0) else None)   #first is alway primary member
	
	ackid = "" if religaremember == None else getvalue(religaremember,"ackid","")
	membername = "" if member == None else getvalue(member,"membername","")
	customer_id  = "" if member == None else getvalue(member,"customerid","")
	mobile_number = "" if member == None else getvalue(member,"mobile_number","")
	
	policy_number = "" if religaremember == None else getvalue(religaremember,"policy_number","")
	policy_name = "" if religaremember == None else getvalue(religaremember,"policy_name","")
	voucher_code = "" if religaremember == None else getvalue(religaremember,"voucher_code","")  	
	
	#POST API-5 Validate Transaction OTP
	oreligare = mdpreligare.ReligareXXX(db,providerid)
	rsp = oreligare.addRlgProcedureToTreatment(ackid, form.vars.otp, treatmentid, 
	                                    procedurepriceplancode, 
	                                    procedurecode, 
	                                    procedurename, 
	                                    procedurefee, 
	                                    tooth, 
	                                    quadrant, 
	                                    remarks, 
	                                    policy_number, 
	                                    customer_id, 
	                                    mobile_number,
	                                    voucher_code,
	                                    policy_name)
     
	jsonrsp  = json.loads(rsp)
	if(jsonrsp["result"] == "success"):
	    redirect(URL('religare','updatereligaretreatmentXXX',vars=dict(treatmentid=treatmentid)))
	else:
	    #go to error screen
	    redirect(URL('religare','religareerror',vars=dict(errorcode=jsonrsp["error_code"])))
    elif form.errors:
	session.flash = "Form Error - Validate Transaction " + str(form.errors)
	message = "Form Error - Validate Transaction " + str(form.errors)
	
    returnurl = URL('admin','providerhome')	
    return dict(form=form,providerid=providerid, providername=providername,returnurl=returnurl,message=message)
  
def religareerror():

    provdict = common.getprovider(auth, db)
    providerid = int(common.getid(provdict["providerid"]))
    providername = common.getstring(provdict["providername"])
    
    returnurl = URL('admin','providerhome') if common.getstring(request.vars.returnurl) == "" else common.getstring(request.vars.returnurl)
    
    errorheader = "Religare Error"
    errorcode = 0 if common.getstring(request.vars.errorcode) == "" else request.vars.errorcode
    
    mssg = db((db.rlgerrormessage.code == errorcode) & (db.rlgerrormessage.is_active == True)).select()
    errormssg = "No Error Message" if errorcode == 0 else (errorcode + ": Blank error message"  if(len(mssg) == 0) else errorcode + ":\n" + common.getstring(mssg[0].externalmessage))


    
    return dict(errorheader=errorheader,providerid=providerid, providername=providername,errormssg=errormssg,returnurl=returnurl)
    
#Cashless API-1 & API-2
def religareCashless():
    message = ""
    providerdict = common.getprovider(auth, db)
    providerid = int(common.getid(providerdict["providerid"]))
    providername = providerdict["providername"]
    returnurl = URL('admin','providerhome')  
    
    
    sendotp = True
    validateotp = False
    mobile_number = request.vars.mobile_number
    ackid = request.vars.ackid
    customer_id = request.vars.customer_id
    policy_number = request.vars.policy_number
    policy_name = request.vars.policy_name
    
    #for development.
    #policy_number = "10406362"
    #voucher_code = "0002456781"
    
    form = SQLFORM.factory(
               
                Field('mobile_number', 'string',  label='Mobile Number',default=mobile_number),
                Field('policy_number', 'string',  label='Policy Number',default=policy_number),
                Field('customer_id', 'string',  label='Customer ID',default=customer_id),
                Field('ackid', 'string',  label='Ackid ID',default=ackid),
                Field('otp', 'string',  label='OTP'),
                Field('xaction','string',default='sendotp')
        )

  

    
    xpn = form.element('input',_id='no_table_policy_number')
    xpn['_class'] =  'form-control placeholder-no-fix'
    xpn['_placeholder'] =  "Enter Policy Number"
    xpn['_autocomplete'] =  'off'

    xci = form.element('input',_id='no_table_customer_id')
    xci['_class'] =  'form-control placeholder-no-fix'
    xci['_placeholder'] =  "Enter Customer ID"
    xci['_autocomplete'] =  'off'
    
    xcell = form.element('input',_id='no_table_mobile_number')
    xcell['_class'] =  'form-control placeholder-no-fix'
    xcell['_placeholder'] =  "Enter Mobile Number"
    xcell['_autocomplete'] =  'off'
    
    xotp = form.element('input',_id='no_table_otp')
    xotp['_class'] =  'form-control placeholder-no-fix'
    xotp['_placeholder'] =  'Enter OTP'
    xotp['_autocomplete'] =  'off'

    db.vw_memberpatientlist.id.readable = False
    
    if form.process().accepted:
	if(form.vars.xaction == "sendOTP"):
	

	    props = db(db.rlgproperties.policy_name == policy_name).select()
	    url = "" if(len(props)==0) else props[0].url
	    apikey = "" if(len(props)==0) else props[0].api_key          
	    
	    sendotp = False
	    validateotp = True	
	    
	    #POST API-I Send OTP
	    oreligare = mdpreligare.ReligareCashless(db, providerid, policy_name, apikey, url)
	    jsonrsp = oreligare.sendOTP(form.vars.mobile_number,form.vars.policy_number, form.vars.customer_id)
	    jsonrsp = json.loads(jsonrsp)
	    if(jsonrsp["result"] == "success"):
		sendotp = False
		validateotp = True 
		ackid = jsonrsp["ackid"]
	      
		
		customer_id = jsonrsp["customer_id"]
		
		xackid = form.element('input',_id='no_table_ackid')
		xackid['_default']  = ackid
		xackid['_value']  = ackid
		
		xcustid = form.element('input',_id='no_table_customer_id')
		xcustid['_default']  = customer_id
		xcustid['_value']  = customer_id
		
		message_otp = "Enter OTP sent to customer's / patient's registered mobile phone"
	    else:
		sendotp = True
		validateotp = False 
		message = jsonrsp["error_message"]
       
	    
		
	if(form.vars.xaction == "validateOTP"):
	    #POST XXXAPI-2 Validate OTP
	  
	    props = db(db.rlgproperties.policy_name == policy_name).select()
	    url = "" if(len(props)==0) else props[0].url
	    apikey = "" if(len(props)==0) else props[0].api_key          
	    
	    sendotp = False
	    validateotp = True	
	    
	    #POST API-2 Validate OTP
	    oreligare = mdpreligare.ReligareCashless(db, providerid, policy_name, apikey, url)
	      
	    jsonrsp = json.loads(oreligare.validateOTP(form.vars.ackid, form.vars.otp, form.vars.policy_number, form.vars.customer_id,form.vars.mobile_number))
	   
	    
	      
	    
	    session.religarevalidmember = json.dumps(jsonrsp)
	    
	    if(jsonrsp["result"] == "success"):
		sendotp = False
		validateotp = False 
		message = "Authentication successful!"
		
		#call API-3 getOPDServices
		redirect(URL('religare','getOPDServicesCashless'))
	    else:
		sendotp = True
		validateotp = False 
		message = jsonrsp["error_message"]
	    
	
	response.flash = ""
    elif form.errors:
	message = "OTP Form Error " + str(form.errors)
        
	    
    return dict(form=form,providername=providername,providerid=providerid,returnurl=returnurl,sendotp=sendotp, validateotp=validateotp,mobile_number=form.vars.mobile_number,voucher_code=form.vars.voucher_code,\
                ackid=form.vars.ackid,customer_id=form.vars.customer_id,policy_name = policy_name, message=message )    



