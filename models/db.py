# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()
#

if not request.env.web2py_runtime_gae:
    
    ## if NOT running on Google App Engine use SQLite or other DB
    #PROD__db =  DAL('mysql://mydentalplan:mydentalplan@mydentalplan.mysql.pythonanywhere-services.com:3306/mydentalplan$my_dentalplan_prod',pool_size=10,check_reserved=['all'],migrate_enabled=False,lazy_tables=True)
    #STG__db =  DAL('mysql://StagingServer:mydentalplan@StagingServer.mysql.pythonanywhere-services.com:3306/StagingServer$prod_stg',pool_size=10,check_reserved=['all'],migrate_enabled=False,lazy_tables=True)
    #db = DAL('mysql://root:root@localhost:3306/prod_dup',pool_size=10,check_reserved=['all'],migrate_enabled=False,lazy_tables=True)
    #db = DAL('mysql://root:root@localhost:3306/mydp_stg',pool_size=10,check_reserved=['all'],migrate_enabled=False,lazy_tables=True)
    db = DAL('mysql://root:root@localhost:3306/mydp_prod',pool_size=10,check_reserved=['all'],migrate_enabled=False,lazy_tables=True)
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################
import datetime

import sys
sys.path.append('applications/my_dentalplan/modules')

from applications.my_pms2.modules import account
from applications.my_pms2.modules import states
from applications.my_pms2.modules import relations
from applications.my_pms2.modules import gender
from applications.my_pms2.modules import treatmentstatus
from applications.my_pms2.modules import dental
from applications.my_pms2.modules import cycle
from applications.my_pms2.modules import status

from account import *
from states import *
from relations import *
from gender import *
from treatmentstatus import *
from dental import *
from cycle import *
from status import *

#from status import ALLSTATUS
#from status import PRIORITY
#from status import OFFICESTAFF

#from states import STATES
#from states import CITIES


#from applications.my_dentalplan.modules.states import *
#from applications.my_dentalplan.modules.relations import *
#from applications.my_dentalplan.modules.gender import *
#from applications.my_dentalplan.modules.treatmentstatus import *
#from applications.my_dentalplan.modules.dental import *
#from applications.my_dentalplan.modules.cycle import *
#from applications.my_dentalplan.modules.status import *
#from applications.my_dentalplan.modules.treatmentstatus import *


#from gluon.contrib.account import *
#from gluon.contrib.states import *
#from gluon.contrib.relations import *
#from gluon.contrib.gender import *
#from gluon.contrib.treatmentstatus import *
#from gluon.contrib.dental import *
#from gluon.contrib.cycle import *
#from gluon.contrib.status import *

from gluon.contrib.populate import populate
from gluon.tools import Auth, Service, PluginManager


auth = Auth(db)
from gluon import current

current.auth = auth
current.db = db 

service = Service()
plugins = PluginManager()

#additonal fields

## create all tables needed by auth if not custom tables
#auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.janrain_account import use_janrain
use_janrain(auth, filename='private/janrain.key')


#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','xstring'))
##
## Fields can be 'xstring','text','xpassword','xinteger','xdouble','xboolean'
##       'xdate','xtime','xdatetime','xblob','xupload', 'xreference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

db.define_table('hv_treatment',
                Field('treatmentid','integer'),
                Field('treatment','string'),
                Field('hv_doctorid','integer'),
                Field('hv_doc_appointmentid','integer'),
                Field('hv_treatment_status','string'),
                auth.signature
                )
db.hv_treatment._singular = "hv_treatment"
db.hv_treatment._plural   = "hv_treatment"       


db.define_table('device_info',
                Field('user_id','integer'),
                Field('device_id','string'),
                Field('device_type','string'),
                Field('device_fcm_token','string')
                )
db.device_info._singular = "device_info"
db.device_info._plural   = "device_info" 

db.define_table('hv_doc_appointment',
                Field('appointmentid','integer'),
                Field('hv_doctorid','integer'),
                Field('hv_appt_created_on','datetime'),
                Field('hv_appt_created_by','string'),
                Field('hv_appt_confirmed_on','datetime'),
                Field('hv_appt_confirmed_by','string'),
                Field('hv_appt_checkedin_on','datetime'),
                Field('hv_appt_checkedin_by','string'),
                Field('hv_appt_checkedout_on','datetime'),
                Field('hv_appt_checkedout_by','string'),
                Field('hv_appt_cancelled_on','datetime'),
                Field('hv_appt_cancelled_by','string'),
                Field('hv_appt_distance','double'),
                Field('hv_appt_notes','text'),
                Field('hv_appt_address1','string'),
                Field('hv_appt_address2','string'),
                Field('hv_appt_address3','string'),
                Field('hv_appt_city','string'),
                Field('hv_appt_st','string'),
                Field('hv_appt_pin','string'),
                Field('hv_appt_city_id','integer'),
                Field('hv_appt_latitude','string'),
                Field('hv_appt_longitude','string'),
                Field('hv_appt_status','string'),
                Field('hv_appt_payment_txid','integer'),
          
                Field('hv_appt_payment_amount','float'),
                Field('hv_appt_payment_date','date'),

                Field('hv_appt_feedback','string'),
                Field('hv_appt_rating','string'),
                Field('hv_appt_feedback_on','date'),
                Field('hv_appt_feedback_by','integer'),

                Field('hv_treatmentid','integer'),
                Field('treatmentid','integer'),
                Field('paymentid','integer')
                
                )




db.hv_doc_appointment._singular = "hv_doc_appointment"
db.hv_doc_appointment._plural   = "hv_doc_appointment"                
                
db.define_table('hv_doctor',
                Field('hv_doc_ID','string'),
                Field('hv_doc_fname','string'),
                Field('hv_doc_lname','string'),
                Field('hv_doc_address1','string'),
                Field('hv_doc_address2','string'),
                Field('hv_doc_address3','string'),
                Field('hv_doc_city','string'),
                Field('hv_doc_st','string'),
                Field('hv_doc_pin','string'),
                Field('hv_doc_aadhar','string'),
                Field('hv_doc_pan','string'),
                Field('hv_doc_registration','string'),
                Field('hv_doc_certification','string'),
                Field('hv_doc_profile_image','string'),
                Field('hv_doc_imageid','integer'),
                Field('hv_doc_dob','date'),
                Field('hv_doc_gender','string'),
                Field('hv_doc_cell','string'),
                Field('hv_doc_email','string'),
                Field('hv_doc_stafftype','string'),
                Field('hv_doc_notes','text'),
                Field('hv_doc_speciality','integer'),
                Field('hv_doc_role','integer'),
                Field('doctorid','integer'),
                
                Field('is_active','boolean',default=True),
                auth.signature
              )
db.hv_doctor._singular = "hv_doctor"
db.hv_doctor._plural   = "hv_doctor"


db.define_table('benefit_member',
                Field('member_id','integer'),
                Field('member_code','string'),
                Field('plan_id','integer'),
                Field('treatment_id','integer'),
                Field('treatment_proc_id','integer'),
                Field('plan_code', 'string'),
                Field('redeem_date','date',default=datetime.date.today(),requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y')))),
                Field('redeem_amount','double'),
                Field('last_redeemed_date','date',default=datetime.date.today(),requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y')))),
                Field('last_redeemed_amount','double'),
                Field('balance_benefit_amount','double'),
                
                Field('is_active','boolean',default=True),
                auth.signature
                )

db.benefit_member._singular = "benefit_member"
db.benefit_member._plural   = "benefit_member"


db.define_table('benefit_member_x_member',
                Field('member_id','integer'),
                Field('benefit_member_id','integer')
                )
db.benefit_member_x_member._singular = "benefit_member_x_member"
db.benefit_member_x_member._plural   = "benefit_member_x_member"




db.define_table('benefit_master',
                Field('benefit_code','string'),
                Field('benefit_name','string'),
                Field('benefit_start_date','date',default=datetime.date.today(),requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y')))),
                Field('benefit_end_date','date',default=datetime.date.today(),requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y')))),
                Field('benefit_value','double'),
                Field('benefit_premium','double'),
                Field('is_valid','boolean',default=True),
                Field('is_active','boolean',default=True),
                auth.signature
                )

db.benefit_master._singular = "benefit_master"
db.benefit_master._plural   = "benefit_master"


db.define_table('benefit_master_x_plan',
                Field('benefit_master_id','integer'),
                Field('plan_id','integer'),
                Field('benefit_master_code','string'),
                Field('plan_code','string')
                )


db.benefit_master_x_plan._singular = "benefit_master_x_plan"
db.benefit_master_x_plan._plural   = "benefit_master_x_plan"

db.define_table('benefit_master_x_member',
                Field('member_id','integer'),
                Field('patient_id','integer'),
                Field('benefit_master_id','integer'),
                Field('plan_id','integer'),
                Field('plan_code','string')
                )


db.benefit_master_x_member._singular = "benefit_master_x_member"
db.benefit_master_x_member._plural   = "benefit_master_x_member"


db.define_table('benefit_master_slabs',
                Field('redeem_mode','string',default="S"),
                Field('redeem_percent','float',default=0.0),
                Field('redeem_lower_limit','float',default=0.0),
                Field('redeem_upper_limit','float',default=0.0),
                Field('redeem_value','float',default=0.0),
                )
db.benefit_master_slabs._singular = "benefit_master_slabs"
db.benefit_master_slabs._plural   = "benefit_master_slabs"

db.define_table('benefit_master_x_slabs',
                Field('benefit_master_id','integer'),
                Field('benefit_master_slabs_id','integer'),
                Field('benefit_master_code','string')
                )

db.benefit_master_x_slabs._singular = "benefit_master_x_slabs"
db.benefit_master_x_slabs._plural   = "benefit_master_x_slabs"

db.define_table('mdpmessages',
               Field('message_code','string'),
               Field('mdpmessage','string')
               
               )
db.mdpmessages._singular = "mdpmessages"
db.mdpmessages._plural   = "mdpmessages"





db.define_table('cities',
                Field('city','string'),
                Field('regioncode','string'),
                Field('HV','boolean'),
                Field('VC','boolean'),
                Field('hv_fees','double'),
                )
db.cities._singular = "cities"
db.cities._plural   = "cities"



db.define_table('states',
                Field('st','string')
                )

db.define_table('travel_log',
                
                Field('travel_code','string'),
                Field('description','string'),
                Field('notes','string'),
                Field('origin','string'),
                Field('destination','string'),
                Field('origin_time','datetime'),
                Field('destination_time','datetime'),
                Field('expenses','double'),
                Field('expenses_notes','text'),
                Field('is_active','boolean',default=True),
                auth.signature
)
db.travel_log._singular = "travel_log"
db.travel_log._plural   = "travel_log"


db.define_table('travel_log_ref',
                Field('ref_code', 'string',default='AGN'),
                Field('ref_id', 'integer'),
                Field('travel_id', 'integer')
                )
db.travel_log_ref._singular = "travel_log_ref"
db.travel_log_ref._plural = "travel_log_ref"


db.define_table('activity_log',
                
                Field('activity_code','string'),
           
                Field('notes','text'),
         
              
                Field('start_time','datetime'),
                Field('end_time','datetime'),
              
                
                Field('is_active','boolean',default=True),
                auth.signature
)
db.activity_log._singular = "activity_log"
db.activity_log._plural   = "activity_log"

db.define_table('activity_log_ref',
                Field('ref_code', 'string',default='AGN'),
                Field('ref_id', 'integer'),
                Field('activity_id', 'integer')
                )
db.activity_log_ref._singular = "activity_log_ref"
db.activity_log_ref._plural = "activity_log_ref"

db.define_table('clinic',
                
                Field('clinic_ref','string'),
                    
                Field('name','string'),
                Field('address1','string'),
                Field('address2','string'),
                Field('address3','string'),
                Field('city', 'string',default='--Select City--',label='City',length=50,requires = IS_IN_SET(CITIES)),
                Field('st', 'string',default='--Select State--',label='State',length=50,requires = IS_IN_SET(STATES)),
                Field('pin','string'),
                
                Field('cell','string'),
                Field('telephone','string'),
                Field('email','string'),

                Field('website','string'),
                Field('gps_location','string'),
                Field('longitude','string'),
                Field('latitude','string'),
                Field('whatsapp','string'),
                Field('facebook','string'),
                Field('twitter','string'),

                Field('status','string'),
                Field('primary_clinic','boolean'),
                
                Field('mdp_registration','string'),
                Field('dentalchairs','string'),
                Field('auto_clave','string',default='yes',requires=IS_IN_SET(YESNO)),
                Field('implantology','string'),
                Field('instrument_sterilization','string'),
                Field('waste_displosal','string'),
                Field('suction_machine','string'),
                Field('laser','string'),
                Field('RVG_OPG','string'),
                
                Field('radiation_protection','string'),                
                Field('computers','string'),                
                Field('network','string'),                
                Field('internet','string'),                
                Field('air_conditioned','string'),                
                Field('waiting_area','string'),                
                Field('backup_power','string'),                
                Field('toilet','string'),                
                Field('water_filter','string'),                
                Field('parking_facility','string'),                
                Field('receptionist','string'),                
                Field('credit_card','string'),                
                Field('certifcates','string'),                
                Field('emergency_drugs','string'),                
                Field('infection_control','string'),                
                Field('daily_autoclaved','string'),                
                Field('patient_records','string'),                
                Field('patient_consent','string'),                
                Field('patient_traffic','string'),                
                Field('nabh_iso_certifcation','string'),     
                Field('intra_oral_camera','string'),     
                Field('rotary_endodontics','string'),     
                Field('bank_id','integer'), 
                
                Field('state_dental_registration','string'),
                Field('registration_certificate','string'),
                Field('isMDP', 'boolean',default=True),
                Field('logo_id', 'integer'),
                Field('logo_file', 'string'),
                
                
                Field('notes','text'),
                auth.signature                
                )

db.clinic._singular = "clinic"
db.clinic._plural   = "clinic"

db.define_table('clinic_ref',
                Field('ref_code', 'string',default='PRV'),
                Field('ref_id', 'integer'),
                Field('clinic_id', 'integer')
                )
db.clinic_ref._singular = "clinic_ref"
db.clinic_ref._plural = "clinic_ref"

db.define_table('bank_details',
                Field('bankname','string'),
                Field('bankbranch','string'),
                Field('bankaccountname','string'),
                Field('bankaccountno','string'),
                Field('bankaccounttype','string'),
                Field('bankmicrno','string'),
                Field('bankifsccode','string'),
                Field('address1','string'),
                Field('address2','string'),
                Field('address3','string'),
                Field('city', 'string',default='None',label='City',length=50,requires = IS_IN_SET(CITIES)),
                Field('st', 'string',default='',label='State',length=50,requires = IS_IN_SET(STATES)),
                Field('pin','string'),
                auth.signature
                )
db.bank_details._singular = "bank_details"
db.bank_details._plural   = "bank_details"

db.define_table('ops_timing',
                Field('calendar_date','date'),
                Field('day_of_week','string'),
                Field('open_time','time'),
                Field('close_time','time'),
                Field('is_lunch','boolean',default=False),
                Field('is_holiday','boolean',default=False),
                Field('is_saturday','boolean',default=False),
                Field('is_sunday','boolean',default=False),
                auth.signature
                )

db.ops_timing._singular = "ops_timing"
db.ops_timing._plural   = "ops_timing"

db.define_table('ops_timing_ref',
                Field('ref_code', 'string',default='RST'),
                Field('ref_id', 'integer'),
                Field('ops_timing_id', 'integer')
                )
db.ops_timing_ref._singular = "ops_timing_ref"
db.ops_timing_ref._plural = "ops_timing_ref"


db.define_table('loginblock',
                Field('ip_address','string'),
                Field('username','string'),
                Field('attempts','integer',default=0),
                Field('lastlogin','datetime', default=request.now, requires=IS_DATETIME(format=T('%d/%m/%Y %H:%M:%S'))),
                auth.signature)

db.define_table('sessionlog',
                Field('ackid','string'),
                Field('promocode','string'),
                Field('is_active','boolean',default=True),
                Field('username','string'),
                auth.signature
                
                )
db.sessionlog._singular = "sessionlog"
db.sessionlog._plural   = "sessionlog"

## after defining tables, uncomment below to enable auditing
db.define_table('otplog',
                Field('memberid', 'integer'),
                Field('patientid', 'integer'),
                Field('cell','string'),
                Field('email','string'),
                Field('otp','string'),
                Field('otpdatetime','datetime', default=request.now, requires=IS_DATETIME(format=T('%d/%m/%Y %H:%M:%S'))),
                Field('is_active','boolean',default=True),
                auth.signature
                )
db.otplog._singular = "OtpHistory"
db.otplog._plural   = "OtpHistory"

db.define_table('loghistory',
                Field('username','string'),
                Field('logerror','string'),
                Field('logstatus','boolean', default=True),
                Field('created_on','datetime', default=request.now, requires=IS_DATETIME(format=T('%d/%m/%Y %H:%M:%S'))),
                Field('created_by','integer'),
                Field('modified_on','datetime', default=request.now, requires=IS_DATETIME(format=T('%d/%m/%Y %H:%M:%S'))),
                Field('modified_by','integer')
                
             
                )
db.loghistory._singular = "loghistory"
db.loghistory._plural   = "loghistory"


db.define_table('auth_user',
    Field('id','id',
          represent=lambda id:SPAN(id,' ',A('view',_href=URL('auth_user_read',args=id)))),
    Field('first_name', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),
          label=T('Provider Name')),
    Field('last_name', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),
          label=T('Last Name'),writable=False,readable=False),
    Field('email', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),
          label=T('Email')),
    Field('cell', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),
          label=T('Cell')),
    
    Field('sitekey', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),
             label=T('Site Key')),
    Field('registration_id', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),
             label=T('Tel/Mobile Number')),
    Field('username', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),
             label=T('Username')),
    Field('password', 'password',
          readable=False,
          label=T('Password')),

    Field('created_on','datetime',default=request.now,
          label=T('Created On'),writable=False,readable=False),
    Field('modified_on','datetime',default=request.now,
          label=T('Modified On'),writable=False,readable=False,
          update=request.now),
    Field('registration_key',default='',
          writable=False,readable=False),
    Field('reset_password_key',default='',
          writable=False,readable=False),
    Field('impersonated','boolean',default=False,
          writable=False,readable=False),
    Field('impersonatorid','integer',default=1,
          writable=False,readable=False),

    Field('IND_IS_SYNC','boolean'),
    
    format='%(username)s')

db.auth_user.first_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
#db.auth_user.last_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
db.auth_user.password.requires = CRYPT(key=auth.settings.hmac_key)
#db.auth_user.sitekey.requires = IS_NOT_IN_DB(db,db.auth_user.sitekey)
db.auth_user.username.requires = IS_NOT_IN_DB(db, db.auth_user.username)
db.auth_user.registration_id.requires = IS_NOT_IN_DB(db, db.auth_user.registration_id)
db.auth_user.email.requires = (IS_EMAIL(error_message=auth.messages.invalid_email),
                               IS_NOT_IN_DB(db, db.auth_user.email))
auth.define_tables(username=True)            # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
#auth.settings.actions_disabled.append('register')
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['reset_password'])+'/%(key)s to reset your password'

auth.settings.remember_me_form = False

db.define_table('monthly',
                Field('premmonth','integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                auth.signature,
                format='%(premmonth)s'
                )

db.define_table('enrollstatus',
                Field('enrollstatus', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                auth.signature,
                format='%(enrollstatus).s'
                )
db.enrollstatus._singular = "EnrollStatus"
db.enrollstatus._plural = "EnrollStatus"


db.define_table('groupregion',
                Field('groupregion','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('region','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                auth.signature,
                format='%(region)s (%(groupregion)s)'
                )
db.groupregion._singular = "GroupRegion"
db.groupregion._plural   = "GroupRegion"

db.define_table('hmoplan',
                Field('hmoplancode','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='HMOPlan  Code',requires=IS_NOT_EMPTY(error_message='cannot be empty!'),length=20),
                Field('name','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Name',length=32),
                Field('procedurepriceplancode','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Name',length=32),
                Field('planfile','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Plan File'),
                Field('welcomeletter','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Welcome Letter'),
                Field('groupregion','reference groupregion'),  
                Field('voucher_code','string'),
                Field('discount_amount','double',default=0),
                Field('walletamount','double',default=0),
                Field('authorizationrequired','boolean',default=False),
                Field('company_code','string',default=None),
                
                auth.signature,
                format = '%(name)s (%(hmoplancode)s)'
               )

db.hmoplan._singular = "HMOPlan"
db.hmoplan._plural   = "HMOPlan"

## Agent  Table
db.define_table('agent',
                Field('agent', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Agent Code',requires=IS_NOT_EMPTY(error_message='cannot be empty!'), unique=True,length=20),
                Field('name', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Agent Name',length=128),
                Field('address1', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Address 1',length=50),
                Field('address2', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=50),
                Field('address3', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=50),
                Field('city', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='City',length=50,requires = IS_IN_SET(CITIES)),
                Field('st', 'string',represent=lambda v, r: '' if v is None else v, default=None,label='State',length=50,requires = IS_IN_SET(STATES)),
                Field('pin', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',length=20),
                Field('telephone', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Telephone',length=20),
                Field('cell', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Cell',length=20),
                Field('fax', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Fax',length=20),
                Field('email', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Email',length=50),
                Field('taxid', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='TaxID',length=20),
                Field('enrolleddate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),label='Enrolled Date',default=request.now, requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
                Field('holdcommissionchecks', 'boolean', default=False,label='Hold Commission Checks'),
                Field('commissionYTD','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Commission YTD'),
                Field('commissionMTD','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Commission MTD'),
                Field('TotalCompanies','integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=0, label='Companies Assigned'),
                auth.signature,
                format='%(agent)s'
               )
db.agent._singular = "Agent"
db.agent._plural = "Agent"

db.define_table('companypolicy',
                Field('companycode','string'),
                Field('policy','string'),
                Field('region','string'),
                Field('premium','double'),
                )
db.companypolicy._singular = "companypolicy"
db.companypolicy._plural = "companypolicy"

db.define_table('company',
                Field('company','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Company Code',required=True,unique=True,length=24),
                Field('name', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Company',default='',length=128),
                Field('contact', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='HR Contact',default='',length=128),
                Field('address1', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Address 1', required=True,length=50),
                Field('address2', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=50),
                Field('address3', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=50),
                Field('city', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='City',length=50,requires = IS_IN_SET(CITIES)),
                Field('st', 'string',represent=lambda v, r: '' if v is None else v, default='',label='State',length=50,requires = IS_IN_SET(STATES)),
                Field('pin', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',required=True,length=20),
                Field('telephone', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Telephone',length=20),
                Field('cell', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Cell',length=20),
                Field('fax', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Fax',length=20),
                Field('email', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Email',length=50),
                Field('enrolleddate','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Enrolled Date',default=request.now, requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
                Field('terminationdate','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),label='Termination Date',default=request.now, requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
                Field('renewaldate','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),label='Renewal Date',default=request.now, requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
                Field('capcycle', 'string',represent=lambda v, r: '' if v is None else v,default='Annual',label='Capitation Cycle',length=24,requires = IS_IN_SET(CYCLE)),
                Field('premcycle', 'string',represent=lambda v, r: '' if v is None else v, default='Annual',label='Premium Cycle',length=24,requires = IS_IN_SET(CYCLE)),
                Field('adminfee', 'double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Admin Fee'),
                Field('minsubscribers', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=1,label='Minimum Subscribers'),
                Field('maxsubscribers', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=20,label='Maximum Subscribers'),
                Field('minsubsage', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=1,label='Subscriber Age(Min.)'),
                Field('maxsubsage', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=99,label='Subscriber Age(Max'),
                Field('mindependantage', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=1,label='Dependant Age(Min.)'),
                Field('maxdependantage', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=99,label='Dependant Age(Max'),
                Field('maxdependantage', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=99,label='Dependant Age(Max'),
                Field('notes', 'text', default='', label='Notes'),
                Field('commission', 'double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Commission'),
                Field('dependantmode','boolean', default=False),
                Field('authorizationrequired','boolean', default=False),
                Field('onlinepayment','boolean', default=True),
                Field('cashlesspayment','boolean', default=True),
                Field('cashpayment','boolean', default=True),
                Field('chequepayment','boolean', default=True),
                Field('IND_IS_SYNC','boolean'),
                Field('hmoplan', 'reference hmoplan'),
                Field('agent', 'reference agent'),
                Field('groupkey', 'string', label='Group Key', length=20),
                auth.signature,
                format='%(name)s (%(company)s)')

db.company._singular = "Company"
db.company._plural   = "Company"

db.define_table('membercount',
                Field('membercount', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=10000),
                Field('dummy1', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('company',  'reference company'),
                auth.signature
            )

db.define_table('providercount',
                Field('providercount', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=10000)
              
            )

db.define_table('groupsmscount',
                Field('smsdate', 'date'),
                Field('smscount', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=0)
              
            )

db.define_table('dentalprocedure',
                Field('dentalprocedure','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Procedure',requires=IS_NOT_EMPTY(error_message='cannot be empty!'),unique=False,length=20),
                Field('category','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Category',length=32),
                Field('shortdescription','text',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Short Name'),
                Field('description','text', default='',label='Description'),
                Field('keywords','string'),
                Field('procedurefee','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Standard Fees'),
                Field('chartcolor','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Color',length=16),
                Field('for_chart','boolean',default=False),
                Field('is_free','boolean',default=False),
                auth.signature,
                format = '%(shortdescription)s (%(dentalprocedure)s)'
                )

db.dentalprocedure._singular = "Procedure"
db.dentalprocedure._plural   = "Procedure"


db.define_table('vw_procedurepriceplan',
                Field('id', 'integer'),
                Field('providerid', 'integer'),
                Field('procedureid', 'integer'),
                Field('procedurepriceplancode',  'string'),
                Field('procedurecode',  'string'),
                Field('longprocedurecode',  'string'),
                Field('shortdescription',  'string'),
                Field('altshortdescription',  'string'),
                Field('description',  'string'),
                Field('category',  'string'),
                Field('ucrfee', 'double'),
                Field('procedurefee', 'double'),
                Field('copay', 'double'),
                Field('inspays', 'double'),
                Field('companypays', 'double'),
                Field('walletamount', 'double'),
                Field('discount_amount', 'double'),
                Field('voucher_code', 'string'),
                Field('remarks', 'string'),
                Field('is_free','boolean',default=False),
                Field('relgrproc','boolean',default=False),
                Field('relgrprocdesc','string'),
                Field('service_id','string'),
                Field('service_name','string'),
                Field('service_category','string'),
               
                Field('is_active','boolean',default=True)
                )
db.vw_procedurepriceplan._singular = "vw_procedurepriceplan"
db.vw_procedurepriceplan._plural   = "vw_procedurepriceplan"

db.define_table('vw_procedurepriceplan_relgr',
                Field('id', 'integer'),
                Field('providerid', 'integer'),
                Field('procedureid', 'integer'),
                Field('procedurepriceplancode',  'string'),
                Field('procedurecode',  'string'),
                Field('longprocedurecode',  'string'),
                Field('shortdescription',  'string'),
                Field('altshortdescription',  'string'),
                Field('description',  'string'),
                Field('category',  'string'),
                Field('ucrfee', 'double'),
                Field('procedurefee', 'double'),
                Field('copay', 'double'),
                Field('inspays', 'double'),
                Field('relgrprocfee', 'double'),
                Field('relgrcopay', 'double'),
                Field('relgrinspays', 'double'),
                Field('companypays', 'double'),
                Field('walletamount', 'double'),
                Field('discount_amount', 'double'),
                Field('voucher_code', 'string'),
                Field('remarks', 'string'),
                Field('is_free','boolean',default=False),
                Field('relgrproc','boolean',default=False),
                Field('relgrprocdesc','string'),
                Field('service_id','string'),
                Field('service_name','string'),
                Field('service_category','string'),
               
                Field('is_active','boolean',default=True)
                )
db.vw_procedurepriceplan_relgr._singular = "vw_procedurepriceplan_relgr"
db.vw_procedurepriceplan_relgr._plural   = "vw_procedurepriceplan_relgr"


db.define_table('vw_procedurepriceplan_x999',
                Field('id', 'integer'),
                Field('providerid', 'integer'),
                Field('procedurepriceplancode',  'string'),
                Field('procedurecode',  'string'),
                Field('longprocedurecode',  'string'),
                Field('shortdescription',  'string'),
                Field('altshortdescription',  'string'),
                Field('description',  'string'),
                Field('category',  'string'),
                Field('ucrfee', 'double'),
                Field('procedurefee', 'double'),
                Field('copay', 'double'),
                Field('inspays', 'double'),
                Field('companypays', 'double'),
                Field('walletamount', 'double'),
                Field('discount_amount', 'double'),
                Field('voucher_code', 'string'),
                Field('remarks', 'string'),
                Field('is_free','boolean',default=False),
                Field('relgrproc','boolean',default=False),
                Field('relgrprocdesc','string'),
                Field('service_id','string'),
                Field('service_name','string'),
                Field('service_category','string'),
                Field('is_active','boolean',default=True)
                )
db.vw_procedurepriceplan_x999._singular = "vw_procedurepriceplan_x999"
db.vw_procedurepriceplan_x999._plural   = "vw_procedurepriceplan_x999"




db.define_table('vw_dentalprocedure',
                Field('id', 'integer'),
                Field('category',  'string'),
                Field('shortdescription',  'string'),
                Field('altshortdescription',  'string'),
                Field('procedurefee', 'double'),
                Field('is_active','boolean',default=True)
                )
db.vw_dentalprocedure._singular = "vw_dentalprocedure"
db.vw_dentalprocedure._plural   = "vw_dentalprocedure"

#this view is to display only Free Initial Consulting & Cleaning (X999 is the procedure code)
db.define_table('vw_dentalprocedure_x999',
                Field('id', 'integer'),
                Field('category',  'string'),
                Field('proccode',  'string'),
                Field('shortdescription',  'string'),
                Field('altshortdescription',  'string'),
                Field('procedurefee', 'double'),
                Field('is_active','boolean',default=True)
                )
db.vw_dentalprocedure_x999._singular = "vw_dentalprocedure_x999"
db.vw_dentalprocedure_x999._plural   = "vw_dentalprocedure_x999"


db.define_table('dentalprocedure_chart',
                Field('id', 'integer'),
                Field('providerid', 'integer'),
                Field('procedurecode',  'string'),
                Field('description',  'string'),
                Field('color',  'string'),
                Field('is_active','boolean',default=True)
                )
db.dentalprocedure_chart._singular = "dentalprocedure_chart"
db.dentalprocedure_chart._plural   = "dentalprocedure_chart"




#this view is to display only Free Initial Consulting & Cleaning (X999 is the procedure code)
db.define_table('vw_dentalprocedure_chart',
                Field('id', 'integer'),
                Field('providerid', 'integer'),
                Field('proccode',  'string'),
                Field('shortdescription',  'string'),
                Field('altshortdescription',  'string'),
                Field('procedurefee', 'double'),
                Field('chartcolor', 'string'),
                Field('for_chart', 'boolean'),
                Field('is_active','boolean',default=True)
                )
db.vw_dentalprocedure_chart._singular = "vw_dentalprocedure_chart"
db.vw_dentalprocedure_chart._plural   = "vw_dentalprocedure_chart"




db.define_table('testdentalproc',
                Field('dummy1', 'string'),
                Field('dproc',  'reference dentalprocedure')
                )
db.testdentalproc._singular = "testdentalrpoc"
db.testdentalproc._plural   = "testdentalrpoc"

db.define_table('copay',
                Field('copay','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Co-Pay'),
                Field('dentalprocedure', 'reference dentalprocedure'),
                Field('shortdescription','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Short Name',length=32),
                Field('procedureucrfee','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Standard Fees'),
                Field('procedurefee','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Procedure Fees'),
                Field('region', 'reference groupregion'),
                Field('hmoplan', 'reference hmoplan'),
                auth.signature
               )

db.copay._singular = "Copay"
db.copay._plural   = "Copay"




db.define_table('agentcommission',
                Field('commission','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Commission'),
                Field('effectiveddate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Effective Date',default=request.now, requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
                Field('hmoplan', 'reference hmoplan', label='HMOPlan'),
                Field('agent', 'reference agent', label='Agent'),
                Field('company', 'reference company', label='Company'),
                auth.signature
               )
db.agentcommission._singular = "Agent_Commission"
db.agentcommission._plural = "Agent_Commission"

db.define_table('companyagent',
                Field('company', 'reference company', label='Company'),
                Field('hmoplan', 'reference hmoplan', label='HMOPlan'),
                Field('agent', 'reference agent', label='Agent'),
                auth.signature
               )
db.companyagent._singular = "Company_Agent"
db.companyagent._plural   = "Company_Agent"

db.define_table('companyhmoplan',
                Field('company', 'reference company', label='Company'),
                Field('hmoplan', 'reference hmoplan', label='HMOPlan'),
                Field('agent', 'reference agent', label='Agent'),
                auth.signature
               )
db.companyhmoplan._singular = "Company_HMOPlan"
db.companyhmoplan._plural   = "Company_HMOPlan"

db.define_table('companyhmoplanrate',
                Field('covered','integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=1, label='Covered'),
                Field('premium','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Premium'),
                Field('capitation','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Capitation'),
                Field('companypays','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Company Pays'),
                Field('relation', 'string',represent=lambda v, r: '' if v is None else v,default='Self',label='Relationship',length=50,requires = IS_IN_SET(PLANRELATIONS)),
                Field('company', 'reference company', label='Company'),
                Field('hmoplan', 'reference hmoplan', label='HMOPlan'),
                Field('groupregion', 'reference groupregion', label='Region'),
                auth.signature
               )
db.companyhmoplanrate._singular = "Company_HMOPlan_Rate"
db.companyhmoplanrate._plural   = "Company_HMOPlan_Rate"


db.define_table('providerbank',
                Field('providerid', 'integer'),
                Field('bankname', 'string', default='', label=''),
                Field('bankbranch', 'string', default='', label=''),
                Field('bankaccountno', 'string', default='', label=''),
                Field('bankaccounttype', 'string', default='', label=''),
                Field('bankmicrno', 'string', default='', label=''),
                Field('bankifsccode', 'string', default='', label=''),
                Field('cancelledcheque', 'string', default='', label=''),
                Field('is_active', 'boolean',default=True),
                auth.signature
                )
db.providerbank._singular = "providerbank"
db.providerbank._plural   = "providerbank"

db.define_table('provider',
                Field('provider', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Provider Code',default='',length=20),
                Field('title','string',represent=lambda v, r: '' if v is None else v,default=' ',label='Title',length=10,requires = IS_EMPTY_OR(IS_IN_SET(DOCTITLE))),
                Field('providername', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Provider Name ',length=512),
                Field('practicename', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Pratice Name',length=512),
                Field('address1', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Address 1',default='',length=512),
                Field('address2', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=512),
                Field('address3', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=512),
                Field('city', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='City',length=50,requires=IS_IN_SET(CITIES)),
                Field('st', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='State',length=50,requires = IS_IN_SET(STATES)),
                Field('pin', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',default='',length=20),
                Field('p_address1', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Address 1',default='',length=512),
                Field('p_address2', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=512),
                Field('p_address3', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=512),
                Field('p_city', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='City',length=50,requires=IS_EMPTY_OR(IS_IN_SET(CITIES))),
                Field('p_st', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='State',length=50,requires = IS_EMPTY_OR(IS_IN_SET(STATES))),
                Field('p_pin', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',default='',length=20),

                Field('telephone', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Telephone',length=20),
                Field('cell', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Cell',length=20),
                Field('fax', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Fax',length=20),
                Field('email', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Email',length=50),
                Field('taxid', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='PAN',readable=False, writable=False,length=20),
                Field('enrolleddate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),label='Enrolled Date',default=request.now,length=20),
                Field('assignedpatientmembers', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'),default=0,label='Assigned Members'),
                Field('captguarantee', 'double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Capitation Guarantee'),
                Field('schedulecapitation', 'double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Schedule Guarantee'),
                Field('capitationytd', 'double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Capitation YTD'),
                Field('captiationmtd', 'double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Capitation MTD'),
                Field('languagesspoken', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Languages Spoken',length=32),
                Field('speciality',  'reference speciality', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control')),
                Field('specialization', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Specialization',length=64),
                Field('sitekey','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Web Enrollment Key', default='1234', length=20),
                Field('registration','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Registration', default='', length=128),
                Field('registered','boolean', default='False'),
                Field('pa_providername', 'string', default='', label=''),
                Field('pa_practicename', 'string', default='', label=''),
                Field('pa_parent', 'string', default='', label=''),
                Field('pa_address', 'string', default='', label=''),
                Field('pa_practiceaddress', 'string', default='', label=''),
                Field('pa_pan', 'string', default='', label=''),
                Field('pa_regno', 'string', default='', label=''),
                Field('pa_dob', 'date', label=''),
                Field('pa_date', 'datetime', default=request.now, label=''),
                Field('pa_accepted', 'boolean', default=False),
                Field('pa_approved', 'boolean', default=False),
                Field('pa_approvedon', 'datetime', default=request.now, label=''),
                Field('pa_approvedby', 'integer'),
                Field('pa_day', 'string', default='', label=''),
                Field('pa_month', 'string', default='', label=''),
                Field('pa_location', 'string', default='', label=''),
                Field('pa_practicepin', 'string', default='', label=''),
                
                Field('pa_hours', 'string', default='', label=''),
                Field('pa_longitude', 'string', default='', label=''),
                Field('pa_latitude', 'string', default='', label=''),
                Field('pa_locationurl', 'string', default='', label=''),

                Field('groupregion','reference groupregion'),
                Field('groupsms', 'boolean', default=True),
                Field('groupemail', 'boolean', default=True),
                
                Field('status', 'string', default='New'),
                
                Field('bankid','reference providerbank'),                
                Field('imageid','integer'),                
                Field('IND_VC','boolean',default=False),
                Field('available','boolean',default=True),
                Field('isMDP', 'boolean',default=True),
                Field('logo_id', 'integer'),
                Field('logo_file', 'string'),
                
                
                auth.signature,
                format='%(providername)s (%(provider)s')
               
db.provider._singular = "Provider"
db.provider._plural = "Provider"



db.define_table('provider_region_plan',
                Field('providercode', 'string'),
                Field('companycode', 'string'),
                Field('regioncode', 'string'),
                Field('plancode', 'string'),
                Field('procedurepriceplancode', 'string'),
                Field('policy', 'string'),
                Field('premium', 'double'),
                auth.signature
                )

db.provider_region_plan._singular = "Provider"
db.provider_region_plan._plural = "Provider"


db.define_table('prospect',
                Field('speciality',  'integer', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control')),
                Field('provider', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Provider Code',default='',length=20),
                Field('title','string',represent=lambda v, r: '' if v is None else v,default=' ',label='Title',length=10,requires = IS_EMPTY_OR(IS_IN_SET(DOCTITLE))),
                Field('providername', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Provider Name ',length=512),
                Field('practicename', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Pratice Name',length=512),
                Field('address1', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Address 1',default='',length=512),
                Field('address2', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=512),
                Field('address3', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=512),
                Field('city', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='City',length=50,requires=IS_IN_SET(CITIES)),
                Field('st', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='State',length=50,requires = IS_IN_SET(STATES)),
                Field('pin', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',default='',length=20),
                Field('p_address1', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Address 1',default='',length=512),
                Field('p_address2', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=512),
                Field('p_address3', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=512),
                Field('p_city', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='City',length=50,requires=IS_EMPTY_OR(IS_IN_SET(CITIES))),
                Field('p_st', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='State',length=50,requires = IS_EMPTY_OR(IS_IN_SET(STATES))),
                Field('p_pin', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',default='',length=20),

                Field('telephone', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Telephone',length=20),
                Field('cell', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Cell',length=20),
                Field('fax', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Fax',length=20),
                Field('email', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Email',length=50),
                Field('taxid', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='PAN',readable=False, writable=False,length=20),
                Field('gender','string',represent=lambda v, r: '' if v is None else v,default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
                Field('dob',
                'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Birth Date',default=request.now,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),                
                Field('enrolleddate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),label='Enrolled Date',default=request.now,length=20),
                Field('assignedpatientmembers', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'),default=0,label='Assigned Members'),
                Field('captguarantee', 'double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Capitation Guarantee'),
                Field('schedulecapitation', 'double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Schedule Guarantee'),
                Field('capitationytd', 'double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Capitation YTD'),
                Field('captiationmtd', 'double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Capitation MTD'),
                Field('languagesspoken', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Languages Spoken',length=32),
                
                Field('specialization', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Specialization',length=64),
                Field('sitekey','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Web Enrollment Key', default='1234', length=20),
                Field('registration','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Registration', default='', length=128),
                Field('registered','boolean', default='False'),
                Field('pa_providername', 'string', default='', label=''),
                Field('pa_practicename', 'string', default='', label=''),
                Field('pa_parent', 'string', default='', label=''),
                Field('pa_address', 'string', default='', label=''),
                Field('pa_practiceaddress', 'string', default='', label=''),
                Field('pa_pan', 'string', default='', label=''),
                Field('pa_regno', 'string', default='', label=''),
                Field('pa_dob', 'date', label=''),
                Field('pa_date', 'date', default=request.now, label=''),
                Field('pa_accepted', 'boolean', default=False),
                Field('pa_approved', 'boolean', default=False),
                Field('pa_approvedon', 'date', default=request.now, label=''),
                Field('pa_approvedby', 'integer'),
                Field('pa_day', 'string', default='', label=''),
                Field('pa_month', 'string', default='', label=''),
                Field('pa_location', 'string', default='', label=''),
                Field('pa_practicepin', 'string', default='', label=''),
                
                Field('pa_hours', 'string', default='', label=''),
                Field('pa_longitude', 'string', default='', label=''),
                Field('pa_latitude', 'string', default='', label=''),
                Field('pa_locationurl', 'string', default='', label=''),

                Field('groupregion','reference groupregion'),
                Field('groupsms', 'boolean', default=True),
                Field('groupemail', 'boolean', default=True),
                
                Field('status', 'string', default='New'),
                
                Field('bankid','reference providerbank'),                
                Field('newcity', 'string'),
                Field('isMDP', 'boolean',default=True),
                Field('logo_id', 'integer'),
                Field('logo_file', 'string'),
                
                auth.signature,
                format='%(providername)s (%(provider)s')
               
db.prospect._singular = "prospect"
db.prospect._plural = "prospect"

db.define_table('prospect_ref',
                Field('ref_code', 'string',default='AGN'),
                Field('ref_id', 'integer'),
                Field('prospect_id', 'integer'),
                Field('provider_id', 'integer')
                )
db.prospect_ref._singular = "prospect_ref"
db.prospect_ref._plural = "prospect_ref"

## Member Table
db.define_table('patientmember',
                Field('patientmember', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), required=True, label="Member/Patient ID",length=50),
                Field('groupref', 'string'),
                Field('pan', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Pan Card',length=20),
                Field('dob',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Birth Date',default=request.now,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),
                Field('title','string',represent=lambda v, r: '' if v is None else v,default=' ',label='Title',length=10,requires = IS_EMPTY_OR(IS_IN_SET(PATTITLE))),
                Field('fname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='First',length=50),
                Field('mname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Middle',length=50),
                Field('lname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Last',length=50),
                Field('gender','string',represent=lambda v, r: '' if v is None else v,default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
                Field('address1', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Address 1', requires=IS_NOT_EMPTY,length=50),
                Field('address2', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=50),
                Field('address3', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=50),
                Field('city', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='City',length=50,requires = IS_IN_SET(CITIES)),
                Field('st', 'string',represent=lambda v, r: '' if v is None else v, default='',label='State',length=50,requires = IS_IN_SET(STATES)),
                Field('pin', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',requires=IS_NOT_EMPTY, length=20),
                Field('telephone', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Telephone',length=20),
                Field('cell', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Cell',length=20),
                Field('email', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Email',length=50),
                Field('enrollmentdate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Enrollment Date',default=request.now,length=20,requires = IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
                Field('terminationdate', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now,length=20,requires = IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
                Field('duedate', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now,length=20,requires = IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
                Field('premstartdt', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now, length=20,requires = IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
                Field('premenddt', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now, length=20,requires = IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
                Field('premium', 'double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00),
                Field('status', 'string',represent=lambda v, r: '' if v is None else v, label='Status',default='No_Attempt',requires = IS_IN_SET(STATUS)),
                Field('webkey', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Web Key', default='', length=20),
                Field('hmopatientmember','boolean', default=True),
                Field('image','upload'),
                Field('imageid','integer'),
                Field('paid', 'boolean',default=False,label='Paid'),
                Field('upgraded', 'boolean',default=False,label='Upgraded'),
                Field('renewed', 'boolean',default=False,label='Renewed'),
                Field('newmember', 'boolean',default=True,label='New Member'),
                Field('freetreatment', 'boolean',default=True,label='Free Treatment'),
                Field('webmember','reference webmember',label='Member'),
                Field('company','reference company',label='Company(Company)'),
                Field('provider','reference provider', label='Provider'),
                Field('memberorder', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'),default=1),
                Field('groupregion','reference groupregion'),
                Field('hmoplan', 'reference hmoplan'),
                Field('startdate','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Start Date',default=request.now,  \
                      requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),length=20),
                
                Field('dcsid','integer',default=0),
                auth.signature,
                format='%(patientmember)s '
               )
db.patientmember._singular = "PatientMember"
db.patientmember._plural   = "PatientMember"

## Member Table
db.define_table('patientmemberdependants',
                Field('title','string',represent=lambda v, r: '' if v is None else v,default=' ',label='Title',length=10,requires = IS_EMPTY_OR(IS_IN_SET(PATTITLE))),
                Field('fname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='First',length=50),
                Field('mname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Middle',length=50),
                Field('lname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Last',length=50),
                Field('depdob', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='DOB', default=request.now, requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),length=20),
                Field('gender','string',represent=lambda v, r: '' if v is None else v, default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
                Field('relation', 'string',represent=lambda v, r: '' if v is None else v,default='Spouse',label='Relationship',length=50,requires = IS_IN_SET(RELATIONS)),
                Field('paid', 'boolean',default=False,label='Paid'),
                Field('newmember', 'boolean',default=True,label='New Member'),
                Field('freetreatment', 'boolean',default=True,label='Free Treatment'),
                Field('patientmember','reference patientmember'),
                Field('webdepid','integer',represent=lambda v, r: 0 if v is None else v),
                Field('memberorder', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'),default=2),
                auth.signature
               )
db.patientmemberdependants._singular = "Dependant"
db.patientmemberdependants._plural   = "Dependant"


db.define_table('companypatientmember',
                Field('company', 'reference company', label='Company'),
                Field('patientmember', 'reference patientmember', label='Member'),
                auth.signature
               )
db.companypatientmember._singular = "Company_Member"
db.companypatientmember._plural   = "Company_Member"


db.define_table('webmember',
               Field('webmember', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Member ID',length=50),
               Field('groupref', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Employee ID',length=50),
               Field('title','string',represent=lambda v, r: '' if v is None else v,default=' ',label='Title',length=10,requires = IS_EMPTY_OR(IS_IN_SET(PATTITLE))),
               Field('fname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='First',length=50),
               Field('mname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Middle',length=50),
               Field('lname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Last',length=50),
               Field('address1', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Address 1', length=50),
               Field('address2', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=50),
               Field('address3', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=50),
               Field('city', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='City',length=50,requires = IS_IN_SET(CITIES)),
               Field('st', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='State',length=50,requires = IS_IN_SET(STATES)),
               Field('pin', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',length=20),
               Field('gender','string',represent=lambda v, r: '' if v is None else v, default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
               Field('telephone', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Telephone',length=20),
               Field('cell', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Cell',length=20),
               Field('email', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Email',length=50),
               Field('webpan', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Pan Card',length=50),
               Field('webdob',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Birth Date',default=request.now,  requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),length=20),
               Field('status', 'string',represent=lambda v, r: '' if v is None else v, label='Status',default='No_Attempt',requires = IS_IN_SET(STATUS)),
               Field('enrollstatus', 'string',represent=lambda v, r: '' if v is None else v, label='Status',default='No_Attempt'),
               Field('image','upload'),
               Field('webkey','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Web Key'),
               Field('pin1','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Option 1'),
               Field('pin2','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Option 2'),
               Field('pin3','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Option 3'),
               Field('webenrolldate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Web Enroll Date',default=request.now,requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),length=20),
               Field('webenrollcompletedate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Web Enrollment Complete Date',default=request.now,requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),length=20),
               Field('imported', 'boolean', default=False, label='Imported'),
               Field('paid', 'boolean',default=False,label='Paid'),
               Field('upgraded', 'boolean',default=False,label='Upgraded'),
               Field('renewed', 'boolean',default=False,label='Renewed'),
               Field('company','reference company'),
               Field('provider','reference provider'),
               Field('groupregion','reference groupregion'),
               Field('hmoplan','reference hmoplan'),
               Field('memberorder', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'),default=1),
               Field('startdate',
                     'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Start Date',default=request.now,  \
                     requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),length=20),
               auth.signature,
                 format='%(webmember)s'
               )
db.webmember._singular = "Web_Member"
db.webmember._plural   = "Web_Member"

## Member Table
db.define_table('webmemberdependants',
                Field('title','string',represent=lambda v, r: '' if v is None else v,default=' ',label='Title',length=10,requires = IS_EMPTY_OR(IS_IN_SET(PATTITLE))),
                Field('fname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='First',length=50),
                Field('mname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Middle',length=50),
                Field('lname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Last',length=50),
                Field('depdob', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='DOB', default=request.now, requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),length=20),
                Field('gender','string',represent=lambda v, r: '' if v is None else v, default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
                Field('relation', 'string',represent=lambda v, r: '' if v is None else v,default='Spouse',label='Relationship',length=50,requires = IS_IN_SET(RELATIONS)),
                Field('paid', 'boolean',default=False,label='Paid'),
                Field('webmember','reference webmember'),
                Field('patdepid','integer',represent=lambda v, r: 0 if v is None else v),
                Field('memberorder', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'),default=2),
                auth.signature
               )
db.webmemberdependants._singular = "Web_Dependant"
db.webmemberdependants._plural   = "Web_Dependant"

db.define_table('agentcommissionreportparam',
                Field('agent', 'reference agent', label='Agent'),
                Field('startdate', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,length=20, label='Commission Start Date'),
                Field('enddate', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,length=20 ,  label = 'Commission End Date'),
                auth.signature
                )
db.agentcommissionreportparam._singular = "Agent_Commission_Report_Params"
db.agentcommissionreportparam._plural   = "Agent_Commission_Report_Params"


db.define_table('providercapitationreportparam',
                Field('provider', 'reference provider', label='Provider'),
                Field('startdate', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,length=20, label='Commission Start Date'),
                Field('enddate', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,length=20 ,  label = 'Commission End Date'),
                Field('memberstatus', 'string',represent=lambda v, r: '' if v is None else v, default='all',length=20 ,  label = 'Commission End Date'),
                Field('is_active', 'boolean',default=True),
                auth.signature
                )
db.providercapitationreportparam._singular = "Provider_Capitation_Report_Params"
db.providercapitationreportparam._plural   = "Provider_Capitation_Report_Params"

db.define_table('treatmentplan',
                Field('treatmentplan','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Treatment_Plan', requires=IS_NOT_EMPTY(error_message='cannot be empty!'), unique=False,length=64),
                Field('description','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Description',length=128),
                Field('startdate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now, requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),label="Start Date",length=20),
                Field('enddate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),label="End Date",length=20),
                Field('status', 'string',represent=lambda v, r: '' if v is None else v,default='Open',label='Status',length=20,requires = IS_IN_SET(TREATMENTSTATUS)),
                Field('totaltreatmentcost','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Cost'),
                Field('totalcopay','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Copay'),
                Field('totalinspays','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Insurance Pays'),
                Field('patient', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('pattitle','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='P'),
                Field('patienttype','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='P'),
                Field('patientname','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('provider','reference provider',label='Provider'),
                Field('primarypatient','reference patientmember',label='Member/Patient'),
                Field('totalpaid','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Paid'),
                Field('totaldue','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Due'),
                Field('totalcopaypaid','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Copay Paid'),
                Field('totalinspaid','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Insurance Paid'),
                Field('totalcompanypays','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Company Pays'),
                Field('totalwalletamount','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Wallet Amount'),
                Field('totaldiscount_amount','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Discount Amount'),
                Field('voucher_code','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('wallet_type','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('totalpromo_amount','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Insurance Pays'),
                Field('promo_amount','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Insurance Pays'),
                Field('promo_code','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='P'),
                
                auth.signature
                )
db.treatmentplan._singular = "Treatment_Plan"
db.treatmentplan._plural   = "Treatment_Plan"

## Provider Notes Table
db.define_table('treatmentplannotes',
                Field('notes', 'text',label='Notes'),
                Field('treatmentplan', 'reference treatmentplan'),
                auth.signature
               )

db.treatmentplannotes._singular = "Treatment_Notes"
db.treatmentplannotes._plural = "Treatment_Notes"



db.define_table('treatment_procedure',
                 Field('treatmentid', 'integer'),
                 Field('dentalprocedure', 'integer'),
                 Field('ucr', 'double',default=0.00),
                 Field('procedurefee', 'double',default=0.00),
                 Field('copay', 'double',default=0.00),
                 Field('inspays', 'double',default=0.00),
                 Field('companypays', 'double',default=0.00),
                 Field('walletamount', 'double',default=0.00),
                 Field('discount_amount', 'double',default=0.00),
                 Field('voucher_code', 'string'),
                 
                 Field('quadrant', 'string'),
                 Field('tooth', 'string'),
                 Field('status', 'string'),
                 Field('authorized', 'boolean'),                 
                 Field('relgrproc', 'boolean',default=False),                 
                 Field('relgrtransactionid', 'string'),
                 Field('relgrtransactionamt', 'double'),
                 Field('service_id', 'string'),
                 Field('policy_name', 'string'),
                 Field('remarks', 'string'),
                 Field('treatmentdate','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now, requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),label="Start Date",length=20),
                 Field('is_active', 'boolean', default = True)
                 
                )

db.treatment_procedure._singular = "treatment_procedure"
db.treatment_procedure._plural = "treatment_procedure"


db.define_table('treatmentplan_patient',
                 Field('treatmentplan', 'reference treatmentplan'),
                 Field('patientmember', 'reference patientmember')
                )




db.define_table('tplan',
                Field('tplan','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Treatment_Plan', requires=IS_NOT_EMPTY(error_message='cannot be empty!'), unique=False,length=20),
                Field('description','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Description',length=128),
                Field('startdate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now, requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),label="Start Date",length=20),
                Field('enddate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default='',requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),label="End Date",length=20),
                Field('status', 'string',represent=lambda v, r: '' if v is None else v, default='Open',label='Status',length=20,requires = IS_IN_SET(TREATMENTSTATUS)),
                Field('totaltreatmentcost','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Cost'),
                Field('totalcopay','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Copay'),
                Field('totalinspays','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Insurance Pays'),
                Field('patient', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('patienttype','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='P'),
                Field('patientname','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('provider','reference provider',label='Provider'),
                Field('primarypatient','reference patientmember',label='Member/Patient'),
                auth.signature,
                format = '%(tplan)s'
                )
db.tplan._singular = "TPlan"
db.tplan._plural   = "TPlan"

db.define_table('treatment',
                Field('treatment','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Case No', requires=IS_NOT_EMPTY(error_message='cannot be empty!'), unique=False,length=64),
                Field('chiefcomplaint','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Chief Complaint', requires="", unique=False,length=128),
                Field('description','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Description',length=128),
                Field('quadrant','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Quadrant(s)'),
                Field('tooth','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Tooth/Teeth'),
                Field('startdate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now, requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),label="Start Date",length=20),
                Field('enddate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),label="End Date",length=20),
                Field('status', 'string',represent=lambda v, r: '' if v is None else v, default='Open',label='Status',length=20,requires = IS_IN_SET(TREATMENTSTATUS)),
                Field('actualtreatmentcost','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Actual Treatment Cost'),
                Field('treatmentcost','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Treatment Cost'),
                Field('copay','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Copay'),
                Field('inspay','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Ins. Pays'),
                Field('companypay','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Co. Pays'),
                Field('walletamount','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Wallet Amount'),
                Field('discount_amount','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Discount Amount'),
                Field('promo_amount','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Discount Amount'),
                Field('voucher_code','string'),
                Field('promo_code','string'),
                Field('wallet_type', 'string' ),                
                Field('WPBA_response', 'text' ),                
                Field('authorized', 'boolean'),
                Field('treatmentplan','reference treatmentplan',label='Member/Patient'),
                Field('provider','reference provider',label='Member/Patient'),
                Field('doctor', 'integer',represent=lambda v, r: 0 if v is None else v, label=T('Dentist'), default=''),
                Field('clinicid', 'integer',represent=lambda v, r: 0 if v is None else v, label=T('Clinic'), default=''),
                Field('dentalprocedure','reference procedurepriceplan',label='Member/Patient'),
                Field('benefit_applied', 'boolean'),
                
                auth.signature,
                format = '%(treatment)s'
                )
db.treatment._singular = "Treatment"
db.treatment._plural   = "Treatment"

## Provider Notes Table
db.define_table('treatmentnotes',
                Field('notes', 'text',label='Notes'),
                Field('treatment', 'reference treatment'),
                auth.signature
               )

db.treatmentnotes._singular = "TreatmentNotes"
db.treatmentnotes._plural = "TreatmentNotes"



db.define_table('dentalimage',
                Field('title', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Title'),
                Field('image','upload',length=255),
                Field('uploadfolder','string'),
                Field('tooth', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Tooth',length=20),
                Field('quadrant', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Quadrant',length=20),
                Field('imagedate', 'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),length=20),
                Field('description', 'text', default='',label='Description',length=128),
                Field('treatmentplan', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('treatment', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('patientmember', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('patient', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('provider', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('patientname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('patienttype', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('provider', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),

                Field('mediafile', 'string',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),                
                Field('mediatype', 'string',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),                
                Field('mediaformat', 'string',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),                
                Field('mediasize', 'double',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details')),                
                
                
                Field('dicomUserUuid', 'string',default=''),
                Field('dicomAcctUuid', 'string',default=''),
                Field('dicomInstUuid', 'string',default=''),
                Field('dicomPatName', 'string',default=''),
                Field('dicomPatUuid', 'string',default=''),
                Field('dicomPatid', 'string',default=''),
                Field('dicomPatOrderUuid', 'string',default=''),
                Field('dicomProcDesc', 'string',default=''),
                Field('dicomPerformedDate', 'string',default=''),
                Field('dicomURL', 'string',default=''),
                
                auth.signature,
                format = '%(title)s')
db.dentalimage._singular = "DentalImage"
db.dentalimage._plural = "DentalImage"

db.define_table('dentalimage_ref',
                Field('ref_code', 'string',default='RST'),
                Field('ref_id', 'integer'),
                Field('media_id', 'integer')
                )
db.dentalimage_ref._singular = "DentalImageRef"
db.dentalimage_ref._plural = "DentalImageRef"

                
                

db.define_table('t_appointment',
    Field('id','id',
          represent=lambda id:SPAN(id,' ',A('view',_href=URL('appointment_read',args=id)))),
    Field('f_title', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), notnull=True,
          label=T('Title')),
    Field('f_patientname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), notnull=True,
          label=T('Name')),
    Field('cell', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), notnull=True,
          label=T('Cell')),
    Field('f_start_time', 'datetime', requires=IS_DATETIME(format=T('%d/%m/%Y %H:%M:%S'),error_message='must be d/m/Y h:m:s!'),
          label=T('Start Time')),
    Field('f_end_time', 'datetime',requires=IS_DATETIME(format=T('%d/%m/%Y %H:%M:%S'),error_message='must be d/m/Y h:m:s!'),
          label=T('End Time')),
    Field('f_duration', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), notnull=True,
          label=T('Duration')),
    Field('f_location','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),
          label=T('Location')),
    Field('f_uniqueid', 'integer',represent=lambda v, r: 0 if v is None else v, label=T('Uniqueid'), default=''),
    Field('f_treatmentid', 'integer',represent=lambda v, r: 0 if v is None else v, label=T('Case'), default=''),
    Field('f_status', 'string',represent=lambda v, r: 0 if v is None else v, label=T('Case'), default='Open'),
    Field('newpatient', 'boolean',default=False),
    Field('blockappt', 'boolean',default=False),
    Field('description','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Description',length=128),
    Field('provider', 'reference provider',label=T('Dentist'), default=''),
    Field('doctor', 'integer',represent=lambda v, r: 0 if v is None else v, label=T('Dentist'), default=''),
    Field('clinicid', 'integer',represent=lambda v, r: 0 if v is None else v, label=T('Clinic'), default=''),
    Field('patient', 'integer',represent=lambda v, r: 0 if v is None else v, label=T('Patient'), default = ''),
    Field('patientmember', 'reference patientmember', label=T('Member'), default = ''),
    Field('sendsms', 'boolean',default=False),
    Field('sendrem', 'boolean',default=False),
    Field('smsaction', 'string',default='create'),

    auth.signature,
    format='%(f_title)s'
    )

db.define_table('t_appointment_archive',db.t_appointment,Field('current_record','reference t_appointment'))

db.define_table('paymenttxlog',
                Field('txno','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Transaction Reference'),
                Field('txdatetime','datetime',default=request.now,length=20, label='Transaction Date_Time' ),
                Field('txamount','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Transaction Amount'),
                Field('totpremium','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Premium Amount'),
                Field('totcompanypays','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Company Pays Amount'),
                Field('servicetax','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Service Tax Amount'),
                Field('swipecharge','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Swipe Charge Amount'),
                Field('total','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Total Amount'),
                Field('responsecode','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('responsemssg', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('paymentid', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('paymentdate', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('paymentamount','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00),
                Field('paymenttxid','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('accountid','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('premstartdt','date',length=20, label='Premium Start Date' ,requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
                Field('premenddt','date',length=20, label='Premium End Date',requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
                Field('webmember','reference webmember'),
                Field('patientmember','reference patientmember'),
                Field('memberpolicyrenewal','reference memberpolicyrenewal'),
                auth.signature
                )

db.paymenttxlog._singular = "PaymentTxLog"
db.paymenttxlog._plural = "PaymentTxLog"


db.define_table('rlgproperties',
                Field('policy_name', 'string',default=''),
                Field('api_key', 'string',default=''),
                Field('url', 'string',default=''),
)
db.rlgproperties._singular = "rlgproperties"
db.rlgproperties._plural = "rlgproperties"


db.define_table('shopsee_properties',
                Field('shopsee_url', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_returnURL', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_stg_url', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_prod_url', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('webhookUrl', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_api_token', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_response_key', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_axis_db_card', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_axis_cr_card', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_hdfc_db_card', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_axis_db_card_exp', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_axis_db_card_cvv', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_axis_db_card_otp', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_axis_cr_card_exp', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_axis_cr_card_cvv', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_axis_cr_card_otp', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_hdfc_db_card_exp', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_hdfc_db_card_cvv', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('shopsee_hdfc_db_card_otp', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('product_name', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('product_id', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
)
db.shopsee_properties._singular = "shopsee_properties"
db.shopsee_properties._plural = "shopsee_properties"

db.define_table('urlproperties',
                Field('callbackurl', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('externalurl', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('mydp_ipaddress', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('mydp_port', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='8001'),
                Field('mydp_application', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='my_dentalplan'),
                Field('pms_ipaddress', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('pms_port', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='8001'),
                Field('pms_application', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='jaiminipms'),
                Field('mailserver','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('mailserverport','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='25'),
                Field('mailsender','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('mailcc','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('mailusername','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('mailpassword','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('servicetax','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00),
                Field('swipecharge','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00),
                Field('jasperreporturl','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('jdomain','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('jport','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('j_username','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('j_password','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('renewalnoticeperiod','integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'),default=0, label='Renewal Notice Period'),
                Field('renewalcallback','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('emailreceipt','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('upgradepolicycallback','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('smsusername','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('smsemail','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),

                Field('fp_apikey', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('fp_privatekey', 'text',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('fp_id', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('fp_merchantid', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('fp_merchantdisplay', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('fp_testurl', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('fp_produrl', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('fp_callbackurl', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('fp_callbackfailureurl', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),

                Field('medi_percent','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00),
                Field('medi_mydp_percent','double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00),
                Field('medi_email', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('medi_mydp_email', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('medi_mydp_cell', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),

                Field('autoemailreceipt', 'boolean'),
                Field('providersms', 'boolean', default=False),
                Field('docsms', 'boolean', default=False),
                Field('groupsms', 'boolean', default=True),

                Field('provideremail', 'boolean', default=False),
                Field('docemail', 'boolean', default=False),
                Field('groupemail', 'boolean', default=True),
                Field('timeinterval', 'double', default=0),

                Field('relgrprodurl', 'string', default=''),
                Field('relgrstgurl', 'string', default=''),
                Field('religare', 'boolean', default=False),
                Field('relgrapikey', 'string', default=''),
                Field('relgrpolicynumber', 'string', default=''),
                Field('encryption', 'boolean', default=True),
                Field('welcomekit', 'boolean', default=True),

                Field('hdfc_merchantid','string',default=''),
                Field('hdfc_account_name','string',default=''),
                Field('hdfc_test_domain','string',default=''),
                Field('hdfc_prod_domain','string',default=''),
                Field('hdfc_access_code','string',default=''),
                Field('hdfc_working_key','string',default=''),
                Field('hdfc_return_url','string',default=''),
                Field('hdfc_cancel_url','string',default=''),
                Field('hdfc_getrsa_url','string',default=''),
                Field('hdfc_transaction_url','string',default=''),
                Field('hdfc_json_url','string',default=''),
                Field('mydp_getrsa_url','string',default=''),

                Field('pagination','integer',default=10),
                Field('php_url','text'),
                Field('vw_url','text'),
                Field('vw_stg_url','text'),
                Field('vw_prod_url','text'),
                
                Field('mdp_contact_cell','string',default='18001027526'),
                Field('mdp_contact_email','string',default='appointments@mydentalplan.in'),

                auth.signature
                )
db.urlproperties._singular = "URL_Properties"
db.urlproperties._plural = "URL_Properties"


db.define_table('pinelab_properties',
                Field('pl_url', 'string',default='https://uat.pinepg.in/api/v2/accept/payment') ,
                Field('pl_uat', 'string',default='https://uat.pinepg.in/api/v2/accept/payment') ,
                Field('pl_prod', 'string',default='https://pinepg.in/api/v2/accept/payment') ,
                Field('pl_mid', 'string',default='106598') ,                
                Field('pl_ac', 'string',default='4a39a6d4-46b7-474d-929d-21bf0e9ed607') ,                
                Field('pl_key', 'string',default='55E0F73224EC458A8EC0B68F7B47ACAE') ,                
                Field('pl_card', 'string',default='4012001037141112') ,                
                Field('pl_name', 'string',default='HDFC TEST') ,                
                Field('pl_expiry', 'string',default='11/23') ,                
                Field('pl_cvv', 'string',default='123'),                 
                Field('pl_callback', 'string',default='')                 
                
                
                )
db.pinelab_properties._singular = "pinelab_properties"
db.pinelab_properties._plural = "pinelab_properties"


db.define_table('enrollmentstatus',
                Field('companyid', 'reference company'),
                Field('userid', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('fname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('mname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('lname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('gender','string',represent=lambda v, r: '' if v is None else v,default='Male',label='Gender',length=10),
                Field('webdob',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=''),
                Field('address1', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='', length=50),
                Field('address2', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=50),
                Field('address3', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=50),
                Field('city', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='City',length=50,requires = IS_IN_SET(CITIES)),
                Field('st', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='State',length=50,requires = IS_IN_SET(STATES)),
                Field('pin', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',length=20),
                Field('telephone', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Telephone',length=20),
                Field('cell', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Cell',length=20),
                Field('email', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Email',length=50),
                Field('webpan', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Pan Card',length=50),
                Field('status', 'string',represent=lambda v, r: '' if v is None else v, label='Status',default='No_Attempt'),
                Field('pin1','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Option 1'),
                Field('pin2','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Option 2'),
                Field('pin3','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Option 3'),
                Field('provider','reference provider'),
                Field('groupregion','reference groupregion'),
                Field('dependants', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=0),
                Field('companyname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                auth.signature

                )
db.enrollmentstatus._singular = "enrollmentstatus"
db.enrollmentstatus._plural = "enrollmentstatus"

db.define_table('vw_assignedmembers',
                Field('pattype', 'string',represent=lambda v, r: '' if v is None else v),
                Field('patientmember', 'string',represent=lambda v, r: '' if v is None else v),
                Field('groupref', 'string',represent=lambda v, r: '' if v is None else v),
                Field('fname', 'string',represent=lambda v, r: '' if v is None else v),
                Field('lname', 'string',represent=lambda v, r: '' if v is None else v),
                Field('cell', 'string',represent=lambda v, r: '' if v is None else v),
                Field('dob', 'date'),
                Field('email', 'string',represent=lambda v, r: '' if v is None else v),
                Field('enrollmentdate', 'date'),
                Field('premenddt', 'date'),
                Field('hmopatientmember', 'boolean'),
                Field('is_active', 'boolean'),
                Field('provider', 'reference provider'),
                Field('company', 'string',represent=lambda v, r: '' if v is None else v),
                Field('providername', 'string',represent=lambda v, r: '' if v is None else v),
                Field('hmoplan', 'string',represent=lambda v, r: '' if v is None else v),
                migrate = False
                )

db.define_table('vw_enrollmentstatus',
                Field('webmember', 'string',represent=lambda v, r: '' if v is None else v),
                Field('groupref', 'string',represent=lambda v, r: '' if v is None else v),
                Field('fname', 'string',represent=lambda v, r: '' if v is None else v),
                Field('lname', 'string',represent=lambda v, r: '' if v is None else v),
                Field('status', 'string',represent=lambda v, r: '' if v is None else v),
                Field('provider', 'string',represent=lambda v, r: '' if v is None else v),
                Field('providername', 'string',represent=lambda v, r: '' if v is None else v),
                Field('companyid', 'reference company'),
                Field('company', 'string',represent=lambda v, r: '' if v is None else v),
                Field('hmoplancode', 'string',represent=lambda v, r: '' if v is None else v),
                Field('cell', 'string',represent=lambda v, r: '' if v is None else v),
                Field('webenrollcompletedate', 'date'),
                Field('is_active', 'boolean'),
                Field('dependants', 'integer',represent=lambda v, r: 0 if v is None else v),
                migrate = False
                )

db.define_table('vw_enrollmentstatus1',
                Field('id', 'integer',represent=lambda v, r: 0 if v is None else v),
                Field('webmember', 'string',represent=lambda v, r: '' if v is None else v),
                Field('groupref', 'string',represent=lambda v, r: '' if v is None else v),
                Field('fname', 'string',represent=lambda v, r: '' if v is None else v),
                Field('lname', 'string',represent=lambda v, r: '' if v is None else v),
                Field('status', 'string',represent=lambda v, r: '' if v is None else v),
                Field('provider', 'string',represent=lambda v, r: '' if v is None else v),
                Field('providername', 'string',represent=lambda v, r: '' if v is None else v),
                Field('companyid', 'reference company'),
                Field('company', 'string',represent=lambda v, r: '' if v is None else v),
                Field('hmoplancode', 'string',represent=lambda v, r: '' if v is None else v),
                Field('cell', 'string',represent=lambda v, r: '' if v is None else v),
                Field('webenrollcompletedate', 'date'),
                Field('is_active', 'boolean'),
                Field('dependants', 'integer',represent=lambda v, r: 0 if v is None else v),
                migrate = False
                )

db.define_table('vw_member',
                Field('pattype', 'string',represent=lambda v, r: '' if v is None else v),
                Field('patientmember',  'string',represent=lambda v, r: '' if v is None else v),
                Field('groupref',  'string',represent=lambda v, r: '' if v is None else v),
                Field('fname',  'string',represent=lambda v, r: '' if v is None else v),
                Field('mname',  'string',represent=lambda v, r: '' if v is None else v),
                Field('lname',  'string',represent=lambda v, r: '' if v is None else v),
                Field('dob',  'date'),
                Field('cell',  'string',represent=lambda v, r: '' if v is None else v),
                Field('telephone',  'string',represent=lambda v, r: '' if v is None else v),
                Field('email',  'string',represent=lambda v, r: '' if v is None else v),
                Field('status',  'string',represent=lambda v, r: '' if v is None else v),
                Field('address1',  'string',represent=lambda v, r: '' if v is None else v),
                Field('address2','string',represent=lambda v, r: '' if v is None else v),
                Field('address3','string',represent=lambda v, r: '' if v is None else v),
                Field('city','string',represent=lambda v, r: '' if v is None else v),
                Field('pin','string',represent=lambda v, r: '' if v is None else v),
                Field('enrollmentdate','date'),
                Field('terminationdate','date'),
                Field('premstartdt','date'),
                Field('premenddt','date'),
                Field('is_active','boolean'),
                Field('relation','string',represent=lambda v, r: '' if v is None else v),
                Field('dependants','integer',represent=lambda v, r: 0 if v is None else v),
                Field('amount','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('membercap','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('dependantcap','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('provider','string',represent=lambda v, r: '' if v is None else v),
                Field('providername','string',represent=lambda v, r: '' if v is None else v),
                Field('provaddress1','string',represent=lambda v, r: '' if v is None else v),
                Field('provaddress2','string',represent=lambda v, r: '' if v is None else v),
                Field('provaddress3','string',represent=lambda v, r: '' if v is None else v),
                Field('provcity','string',represent=lambda v, r: '' if v is None else v),
                Field('provpin','string',represent=lambda v, r: '' if v is None else v),
                Field('provemail','string',represent=lambda v, r: '' if v is None else v),
                Field('provtelephone','string',represent=lambda v, r: '' if v is None else v),
                Field('companyid','reference company'),
                Field('company','string',represent=lambda v, r: '' if v is None else v),
                Field('hmoplancode','string',represent=lambda v, r: '' if v is None else v),
                Field('planname','string',represent=lambda v, r: '' if v is None else v),
                Field('agent','string',represent=lambda v, r: '' if v is None else v),
                Field('agentname','string',represent=lambda v, r: '' if v is None else v),
                Field('agentcommission','string',represent=lambda v, r: '' if v is None else v),
                Field('webmemberid','reference webmember'),
                Field('paymentdate','string',represent=lambda v, r: '' if v is None else v),
                Field('chractive','boolean'),
                migrate = False
                )

db.define_table('vw_memberpayment',
                Field('webmemberid','reference webmember'),
                Field('paymentdate','string',represent=lambda v, r: '' if v is None else v),
                migrate = False
                )
db.define_table('vw_patientmemberdependants',
                Field('dependants','integer',represent=lambda v, r: 0 if v is None else v),
                Field('patientmember','reference patientmember'),
                migrate = False
                )

db.define_table('vw_birthday',
                Field('dependants','integer',represent=lambda v, r: 0 if v is None else v),
                Field('patientmember','reference patientmember'),
                migrate = False
                )

db.define_table('enrollmentstatusreportparams',
                Field('company', 'reference company', label='Company'),
                Field('companyname','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Company Name'),
                Field('status', 'reference company', label='Status',requires = IS_IN_SET(ALLSTATUS)),
                Field('startdt', 'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,length=20, label='Start Date',requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),
                Field('enddt', 'date', widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now,length=20, label='End Date',requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),
                Field('is_active', 'boolean',default=True),
                Field('memberonly', 'boolean',default=True),
                auth.signature
                )
db.enrollmentstatusreportparams._singular = "enrollmentstatusreportparams"
db.enrollmentstatusreportparams._plural   = "enrollmentstatusreportparams"

db.define_table('memberpolicyrenewal',
                Field('patientmember', 'reference patientmember', label='Member'),
                Field('paymenttxlog','reference paymenttxlog'),
                Field('renewaldate', 'date',length=20, label='Renewal Date'),
                Field('renewaldays', 'integer',represent=lambda v, r: 0 if v is None else v, default=0, label='Renewal Days'),
                Field('reminders', 'integer',represent=lambda v, r: 0 if v is None else v, default=0, label='Reminders'),
                Field('reminderdate', 'date',length=20, label='Reminder Date'),
                Field('premium', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Premium Amount"),
                Field('companyamt', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Company Amount"),
                Field('memberamt', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Member Amount"),
                Field('swipecharge', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Swipe Charge"),
                Field('servicetax', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Service Tax"),
                Field('total', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Total"),
                Field('newrenewaldate', 'date',length=20, label='New Renewal Date',requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),
                Field('newduedate', 'date',length=20, label='New Due Date',requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),
                Field('paymentmode','string',represent=lambda v, r: '' if v is None else v, default='None',label='Payment Mode',length=20,requires = IS_IN_SET(PAYMENTMODE)),
                Field('renewed', 'boolean',default=False),
                Field('is_active', 'boolean',default=True),
                auth.signature
                )
db.memberpolicyrenewal._singular = "memberpolicyrenewal"
db.memberpolicyrenewal._plural   = "memberpolicyrenewal"



db.define_table('dependantpolicyrenewal',
                Field('patientmemberdependant', 'reference patientmemberdependant', label='Dependant Member'),
                Field('memberpolicyrenewal', 'reference memberpolicyrenewal'),
                Field('paymenttxlog','reference paymenttxlog'),
                Field('premium', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Premium Amount"),
                Field('companyamt', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Company Amount"),
                Field('memberamt', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Member Amount"),
                Field('is_active', 'boolean',default=True),
                auth.signature
                )
db.dependantpolicyrenewal._singular = "dependantpolicyrenewal"
db.dependantpolicyrenewal._plural   = "dependantpolicyrenewal"




db.define_table('memberpayment',
                Field('patientmember','integer',represent=lambda v, r: 0 if v is None else v),
                Field('premium', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Premium Amount"),
                Field('companyamt', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Company Amount"),
                Field('memberamt', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Member Amount"),
                Field('is_active', 'boolean',default=True),
                auth.signature
                )
db.memberpayment._singular = "memberpayment"
db.memberpayment._plural   = "memberpayment"

db.define_table('dependantpayment',
                Field('patientmember','integer',represent=lambda v, r: 0 if v is None else v),
                Field('premium', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Premium Amount"),
                Field('companyamt', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Company Amount"),
                Field('memberamt', 'double',represent=lambda v, r: 0.00 if v is None else v, default=0.00, label="Member Amount"),
                Field('is_active', 'boolean',default=True),
                auth.signature
                )
db.dependantpayment._singular = "dependantpayment"
db.dependantpayment._plural   = "dependantpayment"

db.define_table('appointmentreminders',
                Field('appointmentid','reference t_appointment'),
                Field('lastreminder', 'date'),
                auth.signature
                )
db.appointmentreminders._singular = "appointmentreminders"
db.appointmentreminders._plural   = "appointmentreminders"

db.define_table('birthdayreminders',
                Field('patient','reference patientmember'),
                Field('lastreminder', 'date'),
                auth.signature
                )
db.appointmentreminders._singular = "birthdayreminders"
db.appointmentreminders._plural   = "birthdayreminders"


db.define_table('vw_providercapitation',
                Field('company','string',represent=lambda v, r: '' if v is None else v),
                Field('hmoplancode','string',represent=lambda v, r: '' if v is None else v),
                Field('premstartdt', 'date'),
                Field('premenddt', 'date'),
                Field('premmonth', 'string',represent=lambda v, r: '' if v is None else v),
                Field('capitation', 'double',represent=lambda v, r: 0.00 if v is None else v),
                Field('provider','reference provider')
                )
db.vw_providercapitation._singular = "vw_providercapitation"
db.vw_providercapitation._plural   = "vw_providercapitation"


db.define_table('importdata',
                Field('memberid', 'string',represent=lambda v, r: '' if v is None else v),
                Field('employeeid', 'string',represent=lambda v, r: '' if v is None else v, default='', label='Member ID',length=50),
                Field('firstname', 'string',represent=lambda v, r: '' if v is None else v, default='', label='Reference ID',length=50),
               Field('lastname', 'string',represent=lambda v, r: '' if v is None else v, default='', label='First',length=50),
               Field('startdate','date', label='Start Date',default=request.now,length=20),
               Field('webdob','date', label='Birth Date',default=request.now,  requires=IS_DATE(format=('%d/%m/%Y')),length=20),
               Field('email', 'string',represent=lambda v, r: '' if v is None else v, default='',label='Email',length=50),
               Field('gender','string',represent=lambda v, r: '' if v is None else v, default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
               Field('webkey','string',represent=lambda v, r: '' if v is None else v,default='',label='Web Key'),
               Field('address1', 'string',represent=lambda v, r: '' if v is None else v,label='Address 1', length=50),
               Field('address2', 'string',represent=lambda v, r: '' if v is None else v, default='',label='Address 2',length=50),
               Field('address3', 'string',represent=lambda v, r: '' if v is None else v, default='',label='Address 2',length=50),
               Field('city', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='City',length=50,requires = IS_IN_SET(CITIES)),
               Field('st', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='State',length=50,requires = IS_IN_SET(STATES)),
               Field('pin', 'string',represent=lambda v, r: '' if v is None else v,label='Pin',length=20),
               Field('status', 'string',represent=lambda v, r: '' if v is None else v, label='Status',default='No_Attempt',requires = IS_IN_SET(STATUS)),
               Field('enrolldate','date', label='Web Enroll Date',default=request.now,length=20),
               Field('imported', 'boolean', default=False, label='Imported'),
               Field('company','reference company'),
               Field('provider','reference provider'),
               Field('groupregion','reference groupregion'),
               Field('hmoplan','reference hmoplan'),
               Field('is_active', 'boolean',default=True),
               auth.signature
               )
db.importdata._singular = "importdata"
db.importdata._plural   = "importdata"


db.define_table('dentalchart',
                Field('patientid', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('memberid', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('providerid', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('is_active', 'boolean',default=True),
                auth.signature
            )
db.dentalchart._singular = "DentalChart"
db.dentalchart._plural = "DentalChart"




db.define_table('tooth',
                Field('toothid', 'string',represent=lambda v, r: '' if v is None else v,label='Tooth ID', length=32),
                Field('toothnumber', 'integer', default=0, represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('chartdate', 'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,length=20, label='Chart Date',requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),
                Field('chartid', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('doctorid', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('procedureid', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('treatmentid', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('toothsection', 'string',represent=lambda v, r: '' if v is None else v,label='Section', length=16),
                Field('notes', 'string',represent=lambda v, r: '' if v is None else v,label='Notes'),
                Field('p1', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p2', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p3', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p4', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p5', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p6', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p7', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p8', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p9', 'string',represent=lambda v, r: '' if v is None else v),
                Field('l1', 'string',represent=lambda v, r: '' if v is None else v),
                Field('l2', 'string',represent=lambda v, r: '' if v is None else v),
                Field('l3', 'string',represent=lambda v, r: '' if v is None else v),
                Field('l4', 'string',represent=lambda v, r: '' if v is None else v),
                Field('e1', 'string',represent=lambda v, r: '' if v is None else v),
                Field('is_active', 'boolean',default=True),
                auth.signature
            )
db.tooth._singular = "tooth"
db.tooth._plural = "tooth"

db.define_table('toothcolor',
                Field('toothid', 'string',represent=lambda v, r: '' if v is None else v,label='Tooth ID', length=32),
                Field('providerid', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form-control')),
                Field('procedureid', 'string',represent=lambda v, r: 0 if v is None else v),
                Field('p1', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p2', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p3', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p4', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p5', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p6', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p7', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p8', 'string',represent=lambda v, r: '' if v is None else v),
                Field('p9', 'string',represent=lambda v, r: '' if v is None else v),
                Field('l1', 'string',represent=lambda v, r: '' if v is None else v),
                Field('l2', 'string',represent=lambda v, r: '' if v is None else v),
                Field('l3', 'string',represent=lambda v, r: '' if v is None else v),
                Field('l4', 'string',represent=lambda v, r: '' if v is None else v),
                Field('e1', 'string',represent=lambda v, r: '' if v is None else v),
                Field('is_active', 'boolean',default=True),
                auth.signature
            )
db.tooth._singular = "toothcolor"
db.tooth._plural = "toothcolor"


db.define_table('vw_tooth',
                 Field('toothid', 'string'),
                 Field('toothnumber', 'integer', default=0, represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form-control')),
                 Field('providerid', 'integer'),
                 Field('dentalchartid', 'integer'),
                 Field('patientid', 'integer'),
                 Field('memberid', 'integer'),
                 Field('treatmentid', 'integer'),
                 Field('procedureid', 'integer'),
                 Field('toothsection', 'string'),
                 Field('p1', 'string',represent=lambda v, r: '' if v is None else v),
                 Field('p2', 'string',represent=lambda v, r: '' if v is None else v),
                 Field('p3', 'string',represent=lambda v, r: '' if v is None else v),
                 Field('p4', 'string',represent=lambda v, r: '' if v is None else v),
                 Field('p5', 'string',represent=lambda v, r: '' if v is None else v),
                 Field('p6', 'string',represent=lambda v, r: '' if v is None else v),
                 Field('p7', 'string',represent=lambda v, r: '' if v is None else v),
                 Field('p8', 'string',represent=lambda v, r: '' if v is None else v),
                 Field('p9', 'string',represent=lambda v, r: '' if v is None else v),
                 Field('l1', 'string',represent=lambda v, r: '' if v is None else v),
                 Field('l2', 'string',represent=lambda v, r: '' if v is None else v),
                 Field('l3', 'string',represent=lambda v, r: '' if v is None else v),
                 Field('l4', 'string',represent=lambda v, r: '' if v is None else v),
                 Field('e1', 'string',represent=lambda v, r: '' if v is None else v),
                 Field('chartdate', 'date'),
                 Field('notes', 'text'),
                 Field('doctorname', 'string'),
                 Field('shortdescription', 'string'),
                 Field('altshortdescription', 'string'),
                 Field('chartcolor', 'string'),
                 Field('activetooth', 'boolean')
                 )

db.vw_tooth._singular = "tooth"
db.vw_tooth._plural = "tooth"


db.define_table('vw_treatmentplancost',
                Field('primarypatient','reference patientmember'), 
                Field('totaltreatmentcost','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('totalcopay','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('totalinspays','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('totalmemberpays','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('totalcompanypays','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('totalwalletamount','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('totaldiscount_amount','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('voucher_code','atring'),  
                migrate = False
                )
db.vw_treatmentplancost._singular = "vw_treatmentplancost"
db.vw_treatmentplancost._plural   = "vw_treatmentplancost"

db.define_table('vw_primarypatientlist',
                Field('id','reference patientmember'), 
                Field('auxid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('patienttype','string',represent=lambda v, r: '' if v is None else v),  
                Field('title','string',represent=lambda v, r: '' if v is None else v),  
                Field('fname','string',represent=lambda v, r: '' if v is None else v),  
                Field('lname','string',represent=lambda v, r: '' if v is None else v),  
                Field('fullname','string',represent=lambda v, r: '' if v is None else v),  
                
                migrate = False
                )
db.vw_primarypatientlist._singular = "vw_primarypatientlist"
db.vw_primarypatientlist._plural   = "vw_primarypatientlist"

db.define_table('vw_imagememberlist',
                Field('patientid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('primarypatientid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('providerid','reference provider'), 
                Field('patientmember','string',represent=lambda v, r: '' if v is None else v),  
                Field('patienttype','string',represent=lambda v, r: '' if v is None else v),  
                Field('fname','string',represent=lambda v, r: '' if v is None else v),  
                Field('lname','string',represent=lambda v, r: '' if v is None else v),  
                Field('cell','string',represent=lambda v, r: '' if v is None else v),  
                Field('email','string',represent=lambda v, r: '' if v is None else v),  
                Field('is_active','boolean'),  
                migrate = False
                )
db.vw_imagememberlist._singular = "vw_imagememberlist"
db.vw_imagememberlist._plural   = "vw_imagememberlist"

db.define_table('vw_patientmemberbirthday',
                Field('patientid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('memberid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('patientmember','string',label="Member ID",represent=lambda v, r: '' if v is None else v),  
                Field('title','string',represent=lambda v, r: '' if v is None else v),  
                Field('fname','string',label="Frist Name",represent=lambda v, r: '' if v is None else v),  
                Field('lname','string',label='Last Name',represent=lambda v, r: '' if v is None else v),  
                Field('cell','string',label="Mobile", represent=lambda v, r: '' if v is None else v),  
                Field('email','string',represent=lambda v, r: '' if v is None else v),  
                Field('dob','date', label="DOB"),
                Field('birthday','date', label="Birthday"),
                Field('gender','string',represent=lambda v, r: '' if v is None else v),
                Field('hmopatientmember','boolean'),  
                Field('is_active','boolean'),  
                Field('lastreminder','date',represent=lambda v, r: '' if v is None else v),
                Field('providername','string',represent=lambda v, r: '' if v is None else v),  
                Field('providerid','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('company','integer',represent=lambda v, r: 0 if v is None else v),  
                migrate = False
                )
db.vw_patientmemberbirthday._singular = "vw_patientmemberbirthday"
db.vw_patientmemberbirthday._plural   = "vw_patientmemberbirthday"


db.define_table('vw_appointmentreminders',
                Field('title','string',represent=lambda v, r: '' if v is None else v),  
                Field('starttime','datetime',label="Start Time"),  
                Field('endtime','datetime',label="End Time"),  
                Field('startdate','date',label="Start Date"),  
                Field('enddate','date',label="End Date"),  
                Field('place','string',represent=lambda v, r: '' if v is None else v),  
                Field('patientmember','string',represent=lambda v, r: '' if v is None else v,label="Member ID"),  
                Field('gender','string',represent=lambda v, r: '' if v is None else v),  
                Field('ptitle','string',represent=lambda v, r: '' if v is None else v),  
                Field('fname','string',represent=lambda v, r: '' if v is None else v,label="First Name"),  
                Field('lname','string',represent=lambda v, r: '' if v is None else v,label="Last Name"),  
                Field('cell','string',represent=lambda v, r: '' if v is None else v,label="Mobile"),  
                Field('email','string',represent=lambda v, r: '' if v is None else v,label="Email"),  
                Field('hmopatientmember','boolean'),  
                Field('activeappt','boolean'),  
                Field('provider','integer',represent=lambda v, r: 0 if v is None else v),
                Field('clinicid','integer',represent=lambda v, r: 0 if v is None else v),
                Field('patient','integer',represent=lambda v, r: 0 if v is None else v),
                Field('lastreminder','date',represent=lambda v, r: '' if v is None else v),
                migrate = False
                )
db.vw_appointmentreminders._singular = "vw_appointmentreminders"
db.vw_appointmentreminders._plural   = "vw_appointmentreminders"



#db.define_table('vw_appointmentreminders',
                #Field('title','string',represent=lambda v, r: '' if v is None else v),  
                #Field('starttime','date'),  
                #Field('endtime','date'),  
                #Field('startdate','date'),  
                #Field('enddate','date'),  
                #Field('place','string',represent=lambda v, r: '' if v is None else v),  
                #Field('providername','string',represent=lambda v, r: '' if v is None else v),  
                #Field('patientmember','string',represent=lambda v, r: '' if v is None else v),  
                #Field('gender','string',represent=lambda v, r: '' if v is None else v),  
                #Field('fname','string',represent=lambda v, r: '' if v is None else v),  
                #Field('lname','string',represent=lambda v, r: '' if v is None else v),  
                #Field('cell','string',represent=lambda v, r: '' if v is None else v),  
                #Field('email','string',represent=lambda v, r: '' if v is None else v),  
                #Field('hmopatientmember','boolean'),  
                #Field('activeappt','boolean'),  
                #Field('provider','integer',represent=lambda v, r: 0 if v is None else v),
                #Field('patient','integer',represent=lambda v, r: 0 if v is None else v),
                #Field('lastreminder','date',represent=lambda v, r: '' if v is None else v),
                #migrate = False
                #)
#db.vw_appointmentreminders._singular = "vw_appointmentreminders"
#db.vw_appointmentreminders._plural   = "vw_appointmentreminders"


## Member Table

db.define_table('vw_patienttreatment_header_rpt',
                Field('treatmentplan','string',represent=lambda v, r: '' if v is None else v),  
                Field('startdate','date'),  
                Field('enddate','date'),  
                Field('status','string',represent=lambda v, r: '' if v is None else v),  
                Field('title','string',represent=lambda v, r: '' if v is None else v),  
                Field('membername','string',represent=lambda v, r: '' if v is None else v),  
                Field('patientname','string',represent=lambda v, r: '' if v is None else v),  
                Field('memberaddress','string',represent=lambda v, r: '' if v is None else v),  
                Field('membercontact','string',represent=lambda v, r: '' if v is None else v),  
                Field('patientmember','string',represent=lambda v, r: '' if v is None else v),  
                Field('pattype','string',represent=lambda v, r: '' if v is None else v),  
                Field('providername','string',represent=lambda v, r: '' if v is None else v),  
                Field('provaddress','string',represent=lambda v, r: '' if v is None else v),  
                Field('provcontact','string',represent=lambda v, r: '' if v is None else v),  
                Field('hmoplan','string',represent=lambda v, r: '' if v is None else v),
                Field('premenddt','date'),
                Field('company','string',represent=lambda v, r: '' if v is None else v),
                Field('totaltreatmentcost','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalcopay','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalinspays','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalpaid','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totaldue','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalcopaypaid','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalinspaid','double',represent=lambda v, r: 0.00 if v is None else v),
                
                migrate = False
                )
db.vw_patienttreatment_header_rpt._singular = "vw_patienttreatment_header_rpt"
db.vw_patienttreatment_header_rpt._plural   = "vw_patienttreatment_header_rpt"

db.define_table('vw_patienttreatment_detail_rpt',
                Field('treatment','string',represent=lambda v, r: '' if v is None else v),  
                Field('status','string',represent=lambda v, r: '' if v is None else v),  
                Field('startdate','date'),  
                Field('enddate','date'),  
                Field('dentalprocedure','string',represent=lambda v, r: '' if v is None else v),  
                Field('shortdescription','string',represent=lambda v, r: '' if v is None else v),  
                Field('UCR','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('quadrant','string',represent=lambda v, r: '' if v is None else v),  
                Field('tooth','string',represent=lambda v, r: '' if v is None else v),  
                Field('description','string',represent=lambda v, r: '' if v is None else v),  
                Field('treatmentcost','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('copay','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('inspay','double',represent=lambda v, r: 0.00 if v is None else v),  
                migrate = False
                )
db.vw_patienttreatment_detail_rpt._singular = "vw_patienttreatment_detail_rpt"
db.vw_patienttreatment_detail_rpt._plural   = "vw_patienttreatment_detail_rpt"



db.define_table('vw_treatmentpaymentreport',
                Field('id','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('treatmentid','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('treatmentplan','string',represent=lambda v, r: '' if v is None else v),  
                Field('treatment','string',represent=lambda v, r: '' if v is None else v),  
                Field('primarypatient','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('patient','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('providerid','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('membername','string',represent=lambda v, r: '' if v is None else v),  
                Field('memberaddress','string',represent=lambda v, r: '' if v is None else v),  
                Field('membercontact','string',represent=lambda v, r: '' if v is None else v),  
                Field('membercell','string',represent=lambda v, r: '' if v is None else v),  
                Field('memberemail','string',represent=lambda v, r: '' if v is None else v),  
                Field('providername','string',represent=lambda v, r: '' if v is None else v),  
                Field('provaddress','string',represent=lambda v, r: '' if v is None else v),  
                Field('provcontact','string',represent=lambda v, r: '' if v is None else v),  
                Field('hmoplan','string',represent=lambda v, r: '' if v is None else v),
                Field('premenddt','date'),
                Field('company','string',represent=lambda v, r: '' if v is None else v),
                Field('totaltreatmentcost','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalcopay','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalinspays','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalmemberpays','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalpaid','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totaldue','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalcopaypaid','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalinspaid','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('is_active','boolean'),  
                
                migrate = False
                )
db.vw_treatmentpaymentreport._singular = "vw_treatmentpaymentreport"
db.vw_treatmentpaymentreport._plural   = "vw_treatmentpaymentreport"



db.define_table('vw_membertreatmentplans_header_rpt',
                Field('id','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('primarypatient','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('patient','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('providerid','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('membername','string',represent=lambda v, r: '' if v is None else v),  
                Field('memberaddress','string',represent=lambda v, r: '' if v is None else v),  
                Field('membercontact','string',represent=lambda v, r: '' if v is None else v),  
                Field('membercell','string',represent=lambda v, r: '' if v is None else v),  
                Field('memberemail','string',represent=lambda v, r: '' if v is None else v),  
                Field('providername','string',represent=lambda v, r: '' if v is None else v),  
                Field('provaddress','string',represent=lambda v, r: '' if v is None else v),  
                Field('provcontact','string',represent=lambda v, r: '' if v is None else v),  
                Field('hmoplan','string',represent=lambda v, r: '' if v is None else v),
                Field('premenddt','date'),
                Field('company','string',represent=lambda v, r: '' if v is None else v),
                Field('totaltreatmentcost','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalcopay','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalinspays','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalmemberpays','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalpaid','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totaldue','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalcopaypaid','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalinspaid','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('is_active','boolean'),  
                
                migrate = False
                )
db.vw_membertreatmentplans_header_rpt._singular = "vw_membertreatmentplans_header_rpt"
db.vw_membertreatmentplans_header_rpt._plural   = "vw_membertreatmentplans_header_rpt"


db.define_table('vw_membertreatmentplans_detail_rpt',
                Field('id','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('primarypatient','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('patient','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('providerid','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('treatmentid','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('treatmentplan','string',represent=lambda v, r: '' if v is None else v),  
                Field('treatment','string',represent=lambda v, r: '' if v is None else v),  
                Field('status','string',represent=lambda v, r: '' if v is None else v),  
                Field('startdate','date'),  
                Field('enddate','date'),  
                Field('dentalprocedure','string',represent=lambda v, r: '' if v is None else v),  
                Field('shortdescription','string',represent=lambda v, r: '' if v is None else v),  
                Field('UCR','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('quadrant','string',represent=lambda v, r: '' if v is None else v),  
                Field('tooth','string',represent=lambda v, r: '' if v is None else v),  
                Field('description','string',represent=lambda v, r: '' if v is None else v),  
                Field('treatmentcost','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('actualtreatmentcost','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('copay','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('inspay','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('is_active','boolean'),  
                migrate = False
                )
db.vw_membertreatmentplans_detail_rpt._singular = "vw_membertreatmentplans_detail_rpt"
db.vw_membertreatmentplans_detail_rpt._plural   = "vw_membertreatmentplans_detail_rpt"

#Field('paymenttype', 'string',represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border w3-small'), default='Treatment',label='Payment Type',requires=IS_IN_SET('Treatment','Treatment'),length=10),

db.define_table('payment',
                Field('paymentdate', 'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px', _class='w3-input w3-border w3-small date '), default=request.now, label='Payment Date',length=50,requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),
                Field('amount', 'double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='w3-input w3-border w3-small'), default=0, label='Payment Amount',length=50),
                Field('companypays', 'double',represent=lambda v, r: 0.00 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='w3-input w3-border w3-small'), default=0, label='Company Pays Amount',length=50),
                Field('paymenttype', 'string',represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border w3-small'), default='Treatment',label='Payment Type',length=10),
                Field('paymentmode', 'string',represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border w3-small'), default='Cash',label='Payment Mode',requires=IS_IN_SET(('Cash','Credit','Cheque','Cashless','Shopse','PineLabs')),length=10),
                Field('payor', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='w3-input w3-border w3-small'), default='',label='Paid By'),
                Field('notes', 'text', default='',label='Notesl'),
                Field('patientmember',  widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border w3-small'), requires=IS_IN_DB(db, 'patientmember.id', '%(fname)s (%(patientmember)s)')),
                Field('treatmentplan', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border w3-small'), requires=IS_IN_DB(db, 'treatmentplan.id', '%(treatmentplan)s')),
                Field('provider', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border w3-small'), requires=IS_IN_DB(db, 'provider.id', '%(provider)s')),
                Field('is_active','boolean'),
                Field('paymentcommit','boolean',default=False),
                Field('precommitamount', 'double',default=0.00),
                Field('walletamount', 'double',default=0.00),
                Field('discount_amount', 'double',default=0.00),
                Field('voucher_code', 'string' ),
                Field('wallet_type', 'string' ),
                
                Field('fp_status', 'string' ),
                Field('fp_paymentref', 'string'),
                Field('fp_paymenttype', 'string'),
                Field('fp_paymentdate', 'date'),
                Field('fp_paymentdetail', 'string'),
                Field('fp_cardtype', 'string'),
                Field('fp_merchantid', 'string'),
                Field('fp_merchantdisplay', 'string'),
                Field('fp_invoice', 'string'),
                Field('fp_invoiceamt', 'double',default=0.00),
                Field('fp_amount', 'double',default=0.00),
                Field('fp_fee', 'double',default=0.00),
                Field('fp_error', 'string'),
                Field('fp_errormsg', 'string'),
                Field('fp_otherinfo', 'string'),
                Field('policy', 'string'),
                
                
                Field('chequeno', 'string',default="000"),
                Field('bankname', 'string',default="XXX"),
                Field('accountname', 'string',default="XXX"),
                Field('accountno', 'string',default="000"),
                auth.signature
               )
db.payment._singular = "payment"
db.payment._plural   = "payment"


db.define_table('vw_paymentlist',
                Field('id', 'id'),
                Field('providerid','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('tplanid','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('treatmentid','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('memberid','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('patientid','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('paymentdate','date',requires=IS_DATE(format=T('%d/%m/%Y'))),  
                Field('amount','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('discount_amount','double',represent=lambda v, r: 0.00 if v is None else v),  
                Field('paymenttype','string',represent=lambda v, r: '' if v is None else v),  
                Field('paymentmode','string',represent=lambda v, r: '' if v is None else v),  
                Field('payor','string',represent=lambda v, r: '' if v is None else v),  
                Field('voucher_code','string',represent=lambda v, r: '' if v is None else v),  
                Field('treatmentplan','string',represent=lambda v, r: '' if v is None else v),  
                Field('treatment','string',represent=lambda v, r: '' if v is None else v),  
                Field('title','string',represent=lambda v, r: '' if v is None else v),  
                Field('patientmember','string',represent=lambda v, r: '' if v is None else v),  
                Field('patientname','string',represent=lambda v, r: '' if v is None else v),  
                Field('totaltreatmentcost','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalcopay','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalinspays','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalpaid','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalcopaypaid','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalinspaid','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totaldue','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalcompanypays','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totalwalletamount','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('totaldiscount_amount','double',represent=lambda v, r: 0.00 if v is None else v),
                Field('fppaymentstatus','string',represent=lambda v, r: '' if v is None else v),  
                Field('fppaymentref','string',represent=lambda v, r: '' if v is None else v),  
                Field('fppaymenttype','string',represent=lambda v, r: '' if v is None else v),  
                Field('fppaymentdetail','string',represent=lambda v, r: '' if v is None else v),  
                Field('fppaymentcard','string',represent=lambda v, r: '' if v is None else v),  
                Field('fpinvoice','string',represent=lambda v, r: '' if v is None else v),  
                Field('is_active','boolean'),
                Field('paymentcommit','boolean'),
                migrate = False
                )
db.vw_paymentlist._singular = "vw_paymentlist"
db.vw_paymentlist._plural   = "vw_paymentlist"
                
db.define_table('vw_treatmentplanlist',
                Field('primarypatient','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('provider','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('startdate','date', label='Start Date',represent=lambda v, r: 0 if v is None else v, requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),  
                Field('status','string',represent=lambda v, r: '' if v is None else v,label='Status'),  
                Field('treatmentplan','string',represent=lambda v, r: '' if v is None else v, label='Treatment Plan'),  
                Field('patientname','string',represent=lambda v, r: '' if v is None else v, label='Patient'),  
                Field('patientmember','string',represent=lambda v, r: '' if v is None else v, label='Member'),  
                Field('fname','string',represent=lambda v, r: '' if v is None else v, label='First Name'),  
                Field('lname','string',represent=lambda v, r: '' if v is None else v, label='Last Name'),  
                Field('cell','string',represent=lambda v, r: '' if v is None else v, label='Cell'),  
                Field('email','string',represent=lambda v, r: '' if v is None else v, label='Email'),  
                Field('totaltreatmentcost','double',represent=lambda v, r: 0.00 if v is None else v, label=' ', default=0.0),
                Field('totaldue','double',represent=lambda v, r: 0.00 if v is None else v,label=' ', default=0.0),
                Field('is_active','boolean', default=True),
                migrate = False
                )
db.vw_treatmentplanlist._singular = "vw_treatmentplanlist"
db.vw_treatmentplanlist._plural   = "vw_treatmentplanlist"

db.define_table('vw_memberlist',
                Field('patientmember','string',represent=lambda v, r: '' if v is None else v, label='Member'),  
                Field('providerid','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('title','string',label='Title', represent=lambda v, r: '' if v is None else v),  
                Field('fname','string',represent=lambda v, r: '' if v is None else v, label='First Name'),  
                Field('lname','string',represent=lambda v, r: '' if v is None else v, label='Last Name'),  
                Field('patient','string',represent=lambda v, r: '' if v is None else v, label='Patient'),  
                Field('cell','string',represent=lambda v, r: '' if v is None else v, label='Cell'),  
                Field('email','string',represent=lambda v, r: '' if v is None else v, label='Email'),  
                Field('premenddt','date',represent=lambda v, r: '' if v is None else v),  
                Field('newmember', 'boolean',default=True,label='New Member'),
                Field('freetreatment', 'boolean',default=True,label='Free Treatment'),
                Field('hmoplanname','string',represent=lambda v, r: '' if v is None else v, label='Plan'),  
                Field('hmoplancode','string',represent=lambda v, r: '' if v is None else v, label='Plan Code'),  
                Field('totaltreatmentcost','double',represent=lambda v, r: 0.00 if v is None else v, label=' ', default=0),
                Field('totaldue','double',represent=lambda v, r: 0.00 if v is None else v,label=' ', default=0),
                Field('hmopatientmember','boolean', default=True),
                Field('is_active','boolean', default=True),
                migrate = False
                )
db.vw_memberlist._singular = "vw_memberlist"
db.vw_memberlist._plural   = "vw_memberlist"


db.define_table('vw_patientmember',
                Field('patientmember','string',represent=lambda v, r: '' if v is None else v, label='Member'),  
                Field('providerid','integer',represent=lambda v, r: 0 if v is None else v),  
                Field('title','string',label='Title', represent=lambda v, r: '' if v is None else v),  
                Field('patient','string',represent=lambda v, r: 0 if v is None else v),  
                migrate = False
                )
db.vw_patientmember._singular = "vw_patientmember"
db.vw_patientmember._plural   = "vw_patientmember"


db.define_table('vw_treatmentlist',
                Field('tplanid','integer',represent=lambda v, r: 0 if v is None else v, label='Treatment Plan ID'),  
                Field('providerid','integer',represent=lambda v, r: 0 if v is None else v, label='Provider ID'),     
                Field('companyid','integer',represent=lambda v, r: 0 if v is None else v, label='Company ID'),                  
                Field('treatmentplan','string',represent=lambda v, r: '' if v is None else v, label='Treatment Plan'),  
                Field('treatment','string',represent=lambda v, r: '' if v is None else v, label='Treatment'),  
                Field('chiefcomplaint','string',represent=lambda v, r: '' if v is None else v, label='Chief Complaint'),  
                Field('startdate','date', label='Start Date',requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),  
                Field('enddate','date', label='End Date',requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),  
                Field('status','string',represent=lambda v, r: '' if v is None else v,label='Status'),  
                Field('title','string',represent=lambda v, r: '' if v is None else v,label='Title'),  
                Field('patientname','string',represent=lambda v, r: '' if v is None else v, label='Patient'),  
                Field('dentalprocedure','string',represent=lambda v, r: '' if v is None else v, label='Procedure'),  
                Field('shortdescription','string',represent=lambda v, r: '' if v is None else v, label='Description'),  
                Field('treatmentcost','double',represent=lambda v, r: 0.00 if v is None else v, label='Treatment Cost', default=0),
                Field('memberid','integer',represent=lambda v, r: 0 if v is None else v, label='Member ID'),                  
                Field('patientid','integer',represent=lambda v, r: 0 if v is None else v, label='Patient ID'),  
                Field('doctorid','integer',represent=lambda v, r: 0 if v is None else v, label='Patient ID'),  
                Field('doctorname','string'),  
                Field('clinicid','integer',represent=lambda v, r: 0 if v is None else v, label='Clinic ID'),  
                Field('clinicname','string'),  
                Field('pattern','string'),  
                Field('pattreatment','string'),  
                Field('groupref','string'),  
                Field('patientmember','string'),  
                Field('tooth','string'),  
                Field('quadrant','string'),  
                Field('notes','string'),  
                Field('is_active','boolean', default=True),
                Field('modified_on','datetime'),
                migrate = False
                )
db.vw_treatmentlist._singular = "vw_treatmentlist"
db.vw_treatmentlist._plural   = "vw_treatmentlist"

        
db.define_table('vw_treatmentlist_fast',
                Field('tplanid','integer'),     
                Field('providerid','integer',represent=lambda v, r: 0 if v is None else v, label='Provider ID'),     
                Field('treatment','string',represent=lambda v, r: '' if v is None else v, label='Treatment'),  
                Field('startdate','date', label='Start Date',requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),  
                Field('enddate','date', label='End Date',requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),  
                Field('status','string',represent=lambda v, r: '' if v is None else v,label='Status'),  
                Field('patientname','string',represent=lambda v, r: '' if v is None else v, label='Patient'),  
                Field('memberid','integer',represent=lambda v, r: 0 if v is None else v, label='Member ID'),                  
                Field('patientid','integer',represent=lambda v, r: 0 if v is None else v, label='Patient ID'),  
                Field('doctorname','string'),  
                Field('clinicid','integer',represent=lambda v, r: 0 if v is None else v, label='Clinic ID'),  
                Field('clinicname','string'),  
                Field('pattern','string'),  
                Field('is_active','boolean', default=True)
                )
db.vw_treatmentlist_fast._singular = "vw_treatmentlist_fast"
db.vw_treatmentlist_fast._plural   = "vw_treatmentlist_fast"


db.define_table('vw_appointmentmemberlist',
                Field('patientid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('primarypatientid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('providerid','reference provider'), 
                Field('patientmember','string',represent=lambda v, r: '' if v is None else v),  
                Field('patienttype','string',represent=lambda v, r: '' if v is None else v),  
                Field('fname','string',represent=lambda v, r: '' if v is None else v),  
                Field('lname','string',represent=lambda v, r: '' if v is None else v),  
                Field('patient','string',represent=lambda v, r: '' if v is None else v),  
                Field('cell','string',represent=lambda v, r: '' if v is None else v),  
                Field('email','string',represent=lambda v, r: '' if v is None else v),  
                Field('is_active','boolean'),  
                Field('hmopatientmember','boolean'),  
                migrate = False
                )
db.vw_appointmentmemberlist._singular = "vw_appointmentmemberlist"
db.vw_appointmentmemberlist._plural   = "vw_appointmentmemberlist"

db.define_table('vw_memberpatientlist',
                Field('patientid','integer',label='Patient ID',represent=lambda v, r: 0 if v is None else v), 
                Field('primarypatientid','integer',label='Primary Patient ID',represent=lambda v, r: 0 if v is None else v), 
                Field('regionid','integer',label='Region', represent=lambda v, r: 0 if v is None else v), 
                Field('providerid','reference provider'), 
                Field('company','reference company'), 
                Field('hmoplan','reference hmoplan'), 
                Field('patientmember','string',label='Member ID',represent=lambda v, r: '' if v is None else v),  
                Field('groupref','string',label='Group Ref',represent=lambda v, r: '' if v is None else v),  
                Field('patienttype','string',label='Patient Type',represent=lambda v, r: '' if v is None else v),  
                Field('title','string',label='Title', represent=lambda v, r: '' if v is None else v),  
                Field('fname','string',label='First Name',represent=lambda v, r: '' if v is None else v),  
                Field('lname','string',label = 'Last Name', represent=lambda v, r: '' if v is None else v),  
                Field('fullname','string',represent=lambda v, r: '' if v is None else v),                  
                Field('patient','string',label='Patient',represent=lambda v, r: '' if v is None else v),  
                Field('cell','string',label='Mobile',represent=lambda v, r: '' if v is None else v),  
                Field('email','string',label='Email', represent=lambda v, r: '' if v is None else v),  
                Field('gender','string',label='Gender', represent=lambda v, r: '' if v is None else v),  
                Field('relation','string',label='Gender', represent=lambda v, r: '' if v is None else v),  
                Field('dob','date',label='DOB',represent=lambda v, r: '' if v is None else v),  
                Field('image','string',label='Gender', represent=lambda v, r: '' if v is None else v),  
                Field('premstartdt','string',label='Prem. Start', represent=lambda v, r: '' if v is None else v),  
                Field('premenddt','string',label='Prem. End',represent=lambda v, r: '' if v is None else v),  
                Field('newmember', 'boolean',default=True,label='New Member'),
                Field('freetreatment', 'boolean',default=True,label='Free Treatment'),
                Field('age', 'integer',label='Age'),
                Field('is_active','boolean'),  
                Field('hmopatientmember','boolean'),  
                Field('hmoplanname','string',represent=lambda v, r: '' if v is None else v, label='Plan'),  
                Field('hmoplancode','string',represent=lambda v, r: '' if v is None else v, label='Plan Code'),  
                Field('procedurepriceplancode','string',represent=lambda v, r: '' if v is None else v, label='Plan Code'),  
                Field('totaltreatmentcost','double',represent=lambda v, r: 0.00 if v is None else v, label=' ', default=0),
                Field('totaldue','double',represent=lambda v, r: 0.00 if v is None else v,label=' ', default=0),
                Field('modified_on','datetime'),
                Field('pattern','string'),
                migrate = False
                )
db.vw_memberpatientlist._singular = "vw_memberpatientlist"
db.vw_memberpatientlist._plural   = "vw_memberpatientlist"



db.define_table('vw_memberpatientlist_fast',
                Field('patientid','integer'), 
                Field('primarypatientid','integer'), 
                Field('providerid','integer'), 
                Field('patientmember','string'),  
                Field('cell','string'), 
                Field('email','string'), 
                Field('hmopatientmember','boolean'),
                Field('fname','string'),
                Field('mname','string'),
                Field('lname','string'),
                Field('premstartdt','date'),
                Field('premenddt','date'),
                Field('patienttype','string'),
                Field('relation','string'),
                Field('memberorder','integer'),
                Field('pattern','text'),
                Field('plan_details','text'),
                Field('plan_id','integer'),
                Field('plan_code','string'),
                Field('plan_name','string'),
                Field('company_code','string')
                
                
                )
db.vw_memberpatientlist_fast._singular = "vw_memberpatientlist_fast"
db.vw_memberpatientlist_fast_plural   = "vw_memberpatientlist+fast"





db.define_table('medicalnotes',
                Field('patientid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('memberid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('notesdate', 'date', label='To Date',default=datetime.date.today(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
                Field('referer','string', label='Doctor/Fried', default=""),
                Field('resoff','string', label='Residence/Office', default=""),
                Field('occupation','string', label='Occupation', default=""),
                Field('bp','boolean', default = False),
                Field('diabetes','boolean', default = False),
                Field('anaemia','boolean', default = False),
                Field('epilepsy','boolean', default = False),
                Field('asthma','boolean', default = False),
                Field('sinus','boolean', default = False),
                Field('heart','boolean', default = False),
                Field('jaundice','boolean', default = False),
                Field('tb','boolean', default = False),
                Field('cardiac','boolean', default = False),
                Field('arthritis','boolean', default = False),
                Field('anyother','boolean', default = False),
                Field('allergic','boolean', default = False),
                Field('excessivebleeding','boolean', default = False),
                Field('seriousillness','boolean', default = False),
                Field('hospitalized','boolean', default = False),
                Field('medications','boolean', default = False),
                Field('surgery','boolean', default = False),
                Field('pregnant','boolean', default = False),
                Field('breastfeeding','boolean', default = False),
                Field('anyothercomplaint','text',represent=lambda v, r: '' if v is None else v),
                Field('chiefcomplaint','text',represent=lambda v, r: '' if v is None else v),
                Field('duration','string', represent=lambda v, r: '' if v is None else v),
                Field('height','string', represent=lambda v, r: '' if v is None else v),
                Field('weight','string', represent=lambda v, r: '' if v is None else v),
                
                Field('is_active','boolean', default = True),
                auth.signature
                )
db.medicalnotes._singular = "medicalnotes"
db.medicalnotes._plural   = "medicalnotes"


db.define_table('medicaltest',
                Field('testname','string',represent=lambda v, r: '' if v is None else v),  
                Field('testdate', 'date', label='Test Date',default=datetime.date.today(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
                Field('actval','string',represent=lambda v, r: '' if v is None else v),  
                Field('lowval','string',represent=lambda v, r: 0 if v is None else v), 
                Field('typval','string',represent=lambda v, r: 0 if v is None else v), 
                Field('upval','string',represent=lambda v, r: 0 if v is None else v), 
                Field('treatmentid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('tplanid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('providerid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('patientid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('memberid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('remarks','string',represent=lambda v, r: '' if v is None else v),  
                Field('is_active','boolean', default = True),
                auth.signature
                )
db.medicaltest._singular = "medicaltest"
db.medicaltest._plural   = "medicaltest"


db.define_table('medication',
                Field('treatmentid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('medicinename','string',represent=lambda v, r: '' if v is None else v),  
                Field('medicinecode','string',represent=lambda v, r: '' if v is None else v),  
                Field('frequency','string',represent=lambda v, r: '' if v is None else v),  
                Field('dosage','string',represent=lambda v, r: '' if v is None else v),  
                Field('quantity','string',represent=lambda v, r: '' if v is None else v),  
                Field('is_active','boolean', default = True),
                auth.signature
                )
db.medication._singular = "medication"
db.medication._plural   = "medication"

db.define_table('prescription',
                Field('medicinename','string',represent=lambda v, r: '' if v is None else v),  
                Field('medicinecode','string',represent=lambda v, r: '' if v is None else v),  
                Field('medicineid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('treatmentid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('tplanid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('providerid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('doctorid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('patientid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('memberid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('frequency','string',represent=lambda v, r: '' if v is None else v),  
                Field('dosage','string',represent=lambda v, r: '' if v is None else v),  
                Field('quantity','string',represent=lambda v, r: '' if v is None else v),  
                Field('remarks','string',represent=lambda v, r: '' if v is None else v), 
                Field('prescriptiondate','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),label='Enrolled Date',default=request.now, requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y')))),
                Field('is_active','boolean', default = True),
                auth.signature
                )
db.prescription._singular = "prescription"
db.prescription._plural   = "prescription"

db.define_table('vw_prescriptionmeds',
                Field('medicinename','string',represent=lambda v, r: '' if v is None else v),  
                Field('frequency','string',represent=lambda v, r: '' if v is None else v),  
                Field('dosage','string',represent=lambda v, r: '' if v is None else v),  
                Field('quantity','string',represent=lambda v, r: '' if v is None else v)  
                )
db.vw_prescriptionmeds._singular = "vw_prescriptionmeds"
db.vw_prescriptionmeds._plural   = "vw_prescriptionmeds"



db.define_table('vw_paymentsummary1',
                Field('patientmember','integer'),  
                Field('provider','integer'),  
                Field('totalcost','double'),  
                Field('totalinspays','double'),  
                Field('totalcopay','double'),  
                Field('totalpaid','double'),
                Field('totaldue','double')
                )
db.vw_paymentsummary1._singular = "vw_paymentsummary1"
db.vw_paymentsummary1._plural   = "vw_paymentsummary1"

db.define_table('vw_paymenttotalpaid',
                Field('patientmember','integer'),  
                Field('provider','integer'),  
                Field('treatmentplan','integer'),  
                Field('totalpaid','double'),
                Field('lastpaymentdate','date')
                )
db.vw_paymenttotalpaid._singular = "vw_paymenttotalpaid"
db.vw_paymenttotalpaid._plural   = "vw_paymenttotalpaid"


db.define_table('vw_treatmentplansummarybytreatment',
                Field('provider','integer'),  
                Field('is_active', 'boolean'),
                Field('totalcost','double'),  
                Field('totalinspays','double'),  
                Field('totalcompanypays','double'),  
                Field('totalwalletamount','double'),  
                Field('totaldiscount_amount','double'),  
                Field('totalcopay','double'),  
                Field('totalpaid','double'),
                Field('totaldue','double'),
                Field('totalcopaypaid','double'),
                Field('totalinspaid','double'),
                Field('totalpromo_amount','double')
                
                
                )
db.vw_treatmentplansummarybytreatment._singular = "vw_treatmentplansummarybytreatment"
db.vw_treatmentplansummarybytreatment._plural   = "vw_treatmentplansummarybytreatment"


db.define_table('vw_treatmentplansummarybypatient',
                Field('provider','integer'),  
                Field('memberid','integer'),  
                Field('patientid','integer'),  
                Field('is_active', 'boolean'),
                Field('totalcost','double'),  
                Field('totalinspays','double'),  
                Field('totalcompanypays','double'),  
                Field('totalwalletamount','double'),  
                Field('totaldiscount_amount','double'),  
                Field('totalcopay','double'),  
                Field('totalpaid','double'),
                Field('totaldue','double'),
                Field('totalcopaypaid','double'),
                Field('totalinspaid','double'),
                Field('totalpromo_amount','double')
                
                )
db.vw_treatmentplansummarybypatient._singular = "vw_treatmentplansummarybypatient"
db.vw_treatmentplansummarybypatient._plural   = "vw_treatmentplansummarybypatient"


db.define_table('role',
                Field('roleid','integer'),  
                Field('role','string',length=128, represent=lambda v, r: '' if v is None else v, requires=IS_NOT_EMPTY()),  
                Field('providerid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('is_active','boolean', default = True),
                auth.signature,
                format = '%(role)s'
                )
db.role._singular = "role"
db.role._plural   = "role"




db.define_table('role_default',
                Field('role','string',length=128, represent=lambda v, r: '' if v is None else v, requires=IS_NOT_EMPTY()),  
                auth.signature,
                
                format = '%(role)s'
                )
db.role_default._singular = "role_default"
db.role_default._plural   = "role_default"


db.define_table('speciality',
                Field('specialityid','integer'),  
                Field('speciality','string',length=128, represent=lambda v, r: '' if v is None else v,requires=IS_NOT_EMPTY()),  
                Field('providerid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('is_active','boolean', default = True),
                auth.signature,
                format = '%(speciality)s'
                )
db.speciality._singular = "speciality"
db.speciality._plural   = "speciality"

db.define_table('speciality_default',
                Field('speciality','string',length=128, represent=lambda v, r: '' if v is None else v,requires=IS_NOT_EMPTY()),  
                auth.signature,
                format = '%(speciality)s'
                )
db.speciality_default._singular = "speciality_default"
db.speciality_default._plural   = "speciality_default"





db.define_table('doctor',
                Field('title','string',represent=lambda v, r: '' if v is None else v,default=' ',label='Title',length=10,requires = IS_EMPTY_OR(IS_IN_SET(DOCTITLE))),
                Field('name','string',represent=lambda v, r: '' if v is None else v,requires=IS_NOT_EMPTY(),length=64),  
                Field('practice_owner','boolean', default = False),
                Field('providerid','integer',represent=lambda v, r: 0 if v is None else v), 
                Field('role',  'reference role',  widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control')),
                Field('speciality',  'reference speciality', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control')),
                Field('email','string',represent=lambda v, r: '' if v is None else v,requires=IS_NOT_EMPTY(),length=128),  
                Field('cell','string',represent=lambda v, r: '' if v is None else v,requires=IS_NOT_EMPTY(),length=40),  
                Field('registration','string',represent=lambda v, r: '' if v is None else v,requires=IS_NOT_EMPTY(),length=64),  
                Field('color','string',represent=lambda v, r: '' if v is None else v,requires=IS_NOT_EMPTY(),length=32),  
                Field('stafftype','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control'),default='Doctor',label='Type',length=10,requires = IS_IN_SET(OFFICESTAFF)),

                Field('state_registration','string'),
                Field('pan','string'),
                Field('adhaar','string'),
                Field('status','string'),
                


                Field('notes','text',represent=lambda v, r: '' if v is None else v),  
                Field('docsms','boolean', default = True),
                Field('docemail','boolean', default = True),
                Field('groupsms','boolean', default = False),
                Field('groupemail','boolean', default = False),
                Field('practice_owner','boolean', default = False),
                
                Field('approval_date','datetime'),
                Field('IND_IS_SYNC','boolean'),
                
                Field('hv_doc','boolean', default=False),
                Field('hv_doc_address1','string'),
                Field('hv_doc_address2','string'),
                Field('hv_doc_address3','string'),
                Field('hv_doc_city','string'),
                Field('hv_doc_st','string'),
                Field('hv_doc_pin','string'),
                Field('hv_doc_gender','string'),
                Field('hv_doc_dob','date'),
                Field('hv_doc_profile_image','string'),
                
                Field('is_active','boolean', default = True),
                
                auth.signature
                )
db.doctor._singular = "doctor"
db.doctor._plural   = "doctor"

db.define_table('doctor_ref',
                Field('ref_code', 'string',default='PRV'),
                Field('ref_id', 'integer'),
                Field('doctor_id', 'integer')
                )
db.doctor_ref._singular = "doctor_ref"
db.doctor_ref._plural = "doctor_ref"

db.define_table('doctortiming',
                Field('mon_day_chk','boolean', default = False),
                Field('mon_lunch_chk','boolean', default = True),
                Field('mon_del_chk','boolean', default = False),
                Field('mon_starttime_1','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('mon_endtime_1','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('mon_starttime_2','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('mon_endtime_2','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('mon_visitinghours','string',represent=lambda v, r: '' if v is None else v),  
                
                Field('tue_day_chk','boolean', default = False),
                Field('tue_lunch_chk','boolean', default = True),
                Field('tue_del_chk','boolean', default = False),
                Field('tue_starttime_1','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('tue_endtime_1','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('tue_starttime_2','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('tue_endtime_2','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('tue_visitinghours','string',represent=lambda v, r: '' if v is None else v),  
                
                Field('wed_day_chk','boolean', default = False),
                Field('wed_lunch_chk','boolean', default = True),
                Field('wed_del_chk','boolean', default = False),
                Field('wed_starttime_1','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('wed_endtime_1','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('wed_starttime_2','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('wed_endtime_2','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('wed_visitinghours','string',represent=lambda v, r: '' if v is None else v),  

                Field('thu_day_chk','boolean', default = False),
                Field('thu_lunch_chk','boolean', default = True),
                Field('thu_del_chk','boolean', default = False),
                Field('thu_starttime_1','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('thu_endtime_1','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('thu_starttime_2','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('thu_endtime_2','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('thu_visitinghours','string',represent=lambda v, r: '' if v is None else v),  

                Field('fri_day_chk','boolean', default = False),
                Field('fri_lunch_chk','boolean', default = True),
                Field('fri_del_chk','boolean', default = False),
                Field('fri_starttime_1','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('fri_endtime_1','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('fri_starttime_2','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('fri_endtime_2','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('fri_visitinghours','string',represent=lambda v, r: '' if v is None else v),  

                Field('sat_day_chk','boolean', default = False),
                Field('sat_lunch_chk','boolean', default = True),
                Field('sat_del_chk','boolean', default = False),
                Field('sat_starttime_1','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('sat_endtime_1','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('sat_starttime_2','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('sat_endtime_2','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('sat_visitinghours','string',represent=lambda v, r: '' if v is None else v),  
 
                Field('sun_day_chk','boolean', default = False),
                Field('sun_lunch_chk','boolean', default = True),
                Field('sun_del_chk','boolean', default = False),
                Field('sun_starttime_1','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('sun_endtime_1','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('sun_starttime_2','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('sun_endtime_2','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(AMS)),  
                Field('sun_visitinghours','string',represent=lambda v, r: '' if v is None else v),  
 
                Field('visitinghours','string',length=512, represent=lambda v, r: '' if v is None else v),  
                Field('lunchbreak','string',length=512,represent=lambda v, r: '' if v is None else v),  
 
                Field('doctor', 'integer'),

                Field('is_active','boolean', default = True),
                auth.signature
                )
db.doctortiming._singular = "doctortiming"
db.doctortiming._plural   = "doctortiming"

db.define_table('vw_appointment_count_sub',
                Field('doctor', 'integer'),
                Field('appointments', 'integer'),
                Field('provider', 'integer'),
                Field('clinicid', 'integer'),
                Field('starttime', 'datetime')
                )
db.vw_appointment_count_sub._singular = "vw_appointment_count_sub"
db.vw_appointment_count_sub._plural   = "vw_appointment_count_sub"

db.define_table('vw_appointment_count',
                Field('doctorid', 'integer'),
                Field('name', 'string'),
                Field('color', 'string'),
                Field('providerid', 'integer'),
                Field('appointments', 'integer'),
                Field('clinicid', 'integer'),
                Field('color', 'string'),
                Field('starttime', 'datetiem'),
                Field('is_active', 'boolean')
                )
db.vw_appointment_count._singular = "vw_appointment_count"
db.vw_appointment_count._plural   = "vw_appointment_count"


db.define_table('medicine',
                Field('providerid', 'integer'),
                Field('medicine', 'string',represent=lambda v, r: '' if v is None else v,default=""),
                Field('medicinetype','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(MEDICINETYPE)),
                Field('strength', 'string',represent=lambda v, r: '' if v is None else v,default=""),
                Field('strengthuom', 'string',represent=lambda v, r: '' if v is None else v,default="",requires=IS_IN_SET(STRENGTHUOM)),
                Field('instructions', 'string',represent=lambda v, r: '' if v is None else v,default=""),
                Field('notes', 'text',represent=lambda v, r: '' if v is None else v, default=""),
                Field('is_active','boolean', default = True),
                auth.signature                
                )
db.medicine._singular = "medicine"
db.medicine._plural   = "medicine"

db.define_table('medicine_default',
                Field('medicine', 'string',represent=lambda v, r: '' if v is None else v,default=""),
                Field('meditype','string',represent=lambda v, r: '' if v is None else v,requires=IS_IN_SET(MEDICINETYPE)),
                Field('strength', 'string',represent=lambda v, r: '' if v is None else v,default=""),
                Field('strengthuom', 'string',represent=lambda v, r: '' if v is None else v,default="",requires=IS_IN_SET(STRENGTHUOM)),
                Field('instructions', 'string',represent=lambda v, r: '' if v is None else v,default=""),
                Field('is_active','boolean', default = True)
            
                )
db.medicine_default._singular = "medicine_default"
db.medicine_default._plural   = "medicine_default"

db.define_table('vw_patientprescription',
                Field('providerid', 'integer'),
                Field('memberid', 'integer'),
                Field('patientid', 'integer'),
                Field('medicineid', 'integer'),
                Field('doctorid', 'integer'),
                Field('tplanid', 'integer'),
                Field('treatmentid', 'integer'),
                Field('doctitle', 'string'),
                Field('doctorname', 'string'),
                Field('title', 'string'),
                Field('fullname', 'string'),
                Field('patientmember', 'string'),
                Field('dob', 'date'),
                Field('age', 'integer'),
                Field('gender', 'string'),
                Field('medicine', 'string'),
                Field('medicinetype', 'string'),
                Field('strength', 'string'),
                Field('strengthuom', 'string'),
                Field('dosage', 'string'),
                Field('frequency', 'string'),
                Field('quantity', 'string'),
                Field('instructions', 'string'),
                Field('remarks', 'text'),
                Field('prescriptiondate','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),label='Enrolled Date',default=request.now, requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y')))),
                Field('is_active', 'boolean')
                )
db.vw_patientprescription._singular = "vw_patientprescription"
db.vw_patientprescription._plural   = "vw_patientprescription"

db.define_table('vw_payment_treatmentplan_treatment',
                Field('tplanid', 'integer'),
                Field('providerid', 'integer'),
                Field('primarypatient', 'integer'),
                Field('patientid', 'integer'),
                Field('tplan', 'string'),
                Field('treatment', 'string'),
                Field('tplanactive', 'boolean')
                )
db.vw_patientprescription._singular = "vw_payment_treatmentplan_treatment"
db.vw_patientprescription._plural   = "vw_payment_treatmentplan_treatment"


db.define_table('procedurepriceplan',
                Field('providerid', 'integer', label='Provider'),
                Field('procedurepriceplancode', 'string',represent=lambda v, r: '' if v is None else v,default="",label='Price Plan Code'),
                Field('procedurecode', 'string',represent=lambda v, r: '' if v is None else v,default="",label='Procedure'),
                Field('ucrfee','double',default=0,label='UCR'),
                Field('procedurefee','double',default=0,label='Procedure Fee'),
                Field('copay','double',default=0, label='CoPay'),
                Field('companypays','double',default=0,label='Co. Pays'),
                Field('walletamount','double',default=0,label='Wallet Amount'),
                Field('discount_amount','double',default=0,label='Discount Amount'),
                
                Field('relgrprocfee','double',default=0,label='RLG Proc Fee'),
                Field('relgrcopay','double',default=0,label='RLG Copay'),
                Field('relgrinspays','double',default=0,label='RLG. Inspays'),
                Field('inspays','double',default=0,label='Ins. Pays'),
                Field('is_free','boolean',default=False),
                Field('relgrproc','boolean',default=False),
                Field('relgrprocdesc','string'),
                Field('voucher_code','string'),
                Field('remarks','string'),
                Field('service_id','string'),
                Field('service_name','string'),
                Field('service_category','string'),
                Field('authorizationrequired','boolean', default = False),
                Field('is_active','boolean', default = True),
                auth.signature                
                )
db.procedurepriceplan._singular = "procedurepriceplan"
db.procedurepriceplan._plural   = "procedurepriceplan"






db.define_table('vw_hmoprocedurepriceplan',
                Field('providerid', 'integer', label='Provider'),
                Field('procedurepriceplancode', 'string', label='Price Plan Code'),
                Field('procedurecode', 'string', label='Procedure'),
                Field('hmoplancode', 'string', label='HMO Plan'),
                Field('shortdescription', 'string', label='Description'),
                Field('ucrfee','double',default=0, label='UCR'),
                Field('procedurefee','double',default=0, label='Procedure Fee'),
                Field('copay','double',default=0,label='CoPay'),
                Field('companypays','double',default=0,label='Co. Pays'),
                Field('inspays','double',default=0, label='Ins. Payes'),
                Field('is_active','boolean', default = True),
                )
db.vw_hmoprocedurepriceplan._singular = "vw_hmoprocedurepriceplan"
db.vw_hmoprocedurepriceplan._plural   = "vw_hmoprocedurepriceplan"


db.define_table('vw_treatmentprocedure',
                Field('treatmentid', 'integer'),
                Field('primarypatient', 'integer'),
                Field('patient', 'integer'),
                Field('providerid', 'integer'),
                Field('treatmentplan', 'string'),
                Field('treatment', 'string'),
                Field('procedurecode', 'string'),
                Field('altshortdescription', 'string'),
                Field('relgrproc','boolean',default=False),
                Field('relgrprocdesc','string'),
                Field('relgrtransactionid','string'),
                Field('relgrtransactionamt', 'double'),
                Field('service_id','string'),                
                Field('ucrfee','double',default=0),
                Field('procedurefee','double',default=0),
                Field('copay','double',default=0),
                Field('inspays','double',default=0),
                Field('companypays','double',default=0),
                Field('quadrant','string'),
                Field('tooth','string'),
                Field('status', 'string'),
                Field('authorized', 'boolean'),
                Field('remarks','string'),
            
                Field('treatmentdate','date',requires=IS_DATE(format=T('%d/%m/%Y'))),
                Field('is_active','boolean', default = True)
                )
db.vw_treatmentprocedure._singular = "vw_treatmentprocedure"
db.vw_treatmentprocedure._plural   = "vw_treatmentprocedure"



       

db.define_table('casereport',
                Field('patientid', 'integer',),
                Field('memberid', 'integer',),
                Field('providerid', 'integer',),
                Field('doctorid', 'integer',),
                Field('treatmentid', 'integer',),
                Field('appointmentid', 'integer',),
                Field('casereport','text',represent=lambda v, r: '' if v is None else v),
                
                Field('child_name','string'),
                Field('child_class','string'),
                
                Field('parent_name','string'),
                Field('school_name','string'),
                Field('admission_number','string'),
                Field('cell','string'),
                Field('email','string'),
                Field('dob','date',requires = IS_DATE(format=T('%d/%m/%Y'))),
                Field('gender','string'),
                Field('cavity_milk_teeth','boolean',default=False),
                Field('cavity_perm_teeth','boolean',default=False),
                Field('crooked_teeth','boolean',default=False),
                Field('gum_problems','boolean',default=False),
                Field('emergency_consult','boolean',default=False),
                Field('priority_checkup','boolean',default=False),
                Field('routine_checkup','boolean',default=False),
                Field('fluoride_check','boolean',default=False),
                Field('image_file','string'),
                
                Field('is_active','boolean', default = True),
                auth.signature    
                )
db.casereport._singular = "casereport"
db.casereport._plural   = "casereport"

db.define_table('dentalcasesheet',
                Field('providerid', 'integer'),
                Field('doctorid', 'integer'),
                Field('casereport','text',represent=lambda v, r: '' if v is None else v),
                Field('child_name','string'),
                Field('child_class','string'),
                Field('parent_name','string'),
                Field('school_name','string'),
                Field('admission_number','string'),
                Field('cell','string'),
                Field('email','string'),
                Field('dob','date',requires = IS_DATE(format=T('%d/%m/%Y'))),
                Field('gender','string'),
                Field('cavity_milk_teeth','boolean',default=False),
                Field('cavity_perm_teeth','boolean',default=False),
                Field('crooked_teeth','boolean',default=False),
                Field('gum_problems','boolean',default=False),
                Field('emergency_consult','boolean',default=False),
                Field('priority_checkup','boolean',default=False),
                Field('routine_checkup','boolean',default=False),
                Field('fluoride_check','boolean',default=False),
                Field('image_file','string'),
                
                Field('is_active','boolean', default = True),
                auth.signature    
                )
db.dentalcasesheet._singular = "dentalcasesheet"
db.dentalcasesheet._plural   = "dentalcasesheet"


#db.define_table('providerregister',
                #Field('','string',length=0),
                #Field('name','string',length=256),
                #Field('gender','string',length=128),
                #Field('dob',
#'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Birth Date',default=request.now,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),
                #Field('parentage','string',length=255),
                #Field('residentaddress','string',length=512),
                #Field('pancardname','string',length=128),
                #Field('pancardno','string',length=128),
                #Field('clinicspeciality','string',length=128),
                #Field('clinicregistration','string',length=128),
                #Field('clinicname','string',length=128),
                #Field('clinicnaddr1','string',length=128),
                #Field('clinicnaddr2','string',length=128),
                #Field('clinicnaddr3','string',length=128),
                #Field('cliniccity','string',length=128),
                #Field('clinicst','string',length=128),
                #Field('clinicpin','string',length=128),
                #Field('clinictelephone','string',length=128),
                #Field('cliniccell','string',length=128),
                #Field('clinicemail','string',length=128),
                #Field('clinichairs','integers'),
                
                
                #)



db.define_table('preregister',
                Field('provider', 'integer'),
                Field('company','integer'),
                Field('description','text',represent=lambda v, r: '' if v is None else v),
                Field('fname','string'),
                Field('lname','string'),
                Field('dob',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Birth Date',default=request.now,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),
                Field('gender','string',represent=lambda v, r: '' if v is None else v,default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
                Field('address','string'),
                Field('city','string'),
                Field('pin','string'),
                Field('st','string'),
                Field('pemail','string'),
                Field('cell','string'),
                Field('oemail','string'),
                Field('treatmentplandetails','string'),
                Field('priority','string'),
                Field('image','upload',length=255),
                Field('employeeid','string'),
                Field('employeephoto','upload',length=255),
                
                Field('is_active','boolean', default = True),
                auth.signature    
                )
db.preregister._singular = "preregister"
db.preregister._plural   = "preregister"

db.define_table('preregisterimage',
                Field('preregisterid', 'integer'),
                Field('title','string'),
                Field('image','string'),
                Field('imagedate', 'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),length=20),
                Field('tooth','string'),
                Field('quadrant','string'),
                Field('description','string'),
                Field('is_active','boolean', default = True)
                )
db.preregisterimage._singular = "preregisterimage"
db.preregisterimage._plural   = "preregisterimage"

db.define_table('vw_casereport',
                Field('patientid', 'integer'),
                Field('memberid', 'integer'),
                Field('providerid', 'integer'),
                Field('treatmentid', 'integer'),
                Field('appointmentid', 'integer'),
                Field('casereport', 'text'),
                Field('doctorname', 'string'),
                Field('providername', 'string'),
                Field('fullname','string'),
                Field('patientmember','string'),
                
                Field('child_name','string'),
                Field('child_class','string'),
                
                Field('parent_name','string'),
                Field('school_name','string'),
                Field('admission_number','string'),
                Field('cell','string'),
                Field('email','string'),
                Field('dob','date'),
                Field('gender','string'),
                
                
                Field('cavity_milk_teeth','boolean',default=False),
                Field('cavity_perm_teeth','boolean',default=False),
                Field('crooked_teeth','boolean',default=False),
                Field('gum_problems','boolean',default=False),
                Field('emergency_consult','boolean',default=False),
                Field('priority_checkup','boolean',default=False),
                Field('routine_checkup','boolean',default=False),
                Field('fluoride_check','boolean',default=False),
                Field('image_file','string'),
                
                Field('is_active', 'boolean'),
                Field('modified_on', 'datetime',requires=IS_DATE(format=('%d/%m/%Y %H:%M:%S'))),
                Field('modified_by', 'integer')
                )
db.vw_casereport._singular = "vw_casereport"
db.vw_casereport._plural   = "vw_casereport"

db.define_table('vw_dentalcasesheet',
                Field('providerid', 'integer'),
                Field('doctorid', 'integer'),
                Field('doctorname', 'string'),
                Field('providername', 'string'),
                
                Field('casereport', 'text'),
                Field('child_name','string'),
                Field('child_class','string'),
                
                Field('parent_name','string'),
                Field('school_name','string'),
                Field('admission_number','string'),
                Field('cell','string'),
                Field('email','string'),
                Field('dob','date'),
                Field('gender','string'),
                
                
                Field('cavity_milk_teeth','boolean',default=False),
                Field('cavity_perm_teeth','boolean',default=False),
                Field('crooked_teeth','boolean',default=False),
                Field('gum_problems','boolean',default=False),
                Field('emergency_consult','boolean',default=False),
                Field('priority_checkup','boolean',default=False),
                Field('routine_checkup','boolean',default=False),
                Field('fluoride_check','boolean',default=False),
                Field('casereport', 'text'),
                
                Field('image_file','string'),
                
                Field('is_active', 'boolean')
               
                )
db.vw_dentalcasesheet._singular = "vw_dentalcasesheet"
db.vw_dentalcasesheet._plural   = "vw_dentalcasesheet"

        

db.define_table('vw_fonepaise',
                Field('paymentid', 'integer'),
                Field('providerid', 'integer'),
                Field('patientid', 'integer'),
                Field('memberid', 'integer'),
                Field('treatmentid', 'integer'),
                Field('tplanid', 'integer'),
                Field('invoice', 'string'),
                Field('invoiceamt', 'double'),
                Field('email', 'string'),
                Field('mobileno', 'string'),
                Field('providername', 'string'),
                Field('provtitle', 'string'),
                Field('practicename', 'string'),
                Field('treatment', 'string'),
                Field('chiefcomplaint', 'string'),
                Field('description', 'string'),
                Field('treatmentplan', 'string'),
                Field('title', 'string'),
                Field('patientmember', 'string'),
                Field('fullname', 'string'),
                Field('doctortitle', 'string'),
                Field('doctorname', 'string'),
                Field('notes', 'string')
                
                
                )
db.vw_fonepaise._singular = "vw_fonepaise"
db.vw_fonepaise._plural   = "vw_fonepaise"

db.define_table('vw_appointment_today',
                Field('f_title', 'string'),
                Field('f_patientname', 'string'),
                Field('f_start_time', 'datetime'),
                Field('f_duration', 'integer'),
                Field('f_status', 'string'),
                Field('description', 'string'),
                Field('providerid', 'integer'),
                Field('clinicid', 'integer'),
                Field('doctorname','string'),
                Field('doctorid','integer'),
                Field('treatmentid','integer'),
                Field('treatment','string'),
                Field('patientid', 'integer'),
                Field('memberid','integer'),
                Field('patientcell','string'),
                Field('newpatient','boolean'),
                Field('patienttype','string'),
                Field('appointmentblock','string'),
                Field('doccolor','string'),
                Field('apptcolor','string'),
                Field('is_active','boolean')
                )
db.vw_appointment_today._singular = "vw_appointment_today"
db.vw_appointment_today._plural   = "vw_appointment_today"               
                
                
db.define_table('vw_appointment_monthly',
                Field('f_title', 'string'),
                Field('f_patientname', 'string'),
                Field('f_start_time', 'datetime'),
                Field('f_duration', 'integer'),
                Field('f_status', 'string'),
                
                Field('description', 'string'),
                Field('providerid', 'integer'),
                Field('doctorname','string'),
                Field('doctorid','integer'),   
                Field('treatmentid','integer'),
                Field('treatment','string'),
                Field('patientid', 'integer'),
                Field('memberid','integer'),
                Field('clinicid', 'integer'),
                
                Field('patientcell','string'),
                Field('newpatient','boolean'),
                Field('patienttype','string'),
                Field('appointmentblock','string'),
                Field('doccolor','string'),
                Field('doccell','string'),
                Field('apptcolor','string'),
                Field('is_active','boolean')
                )
db.vw_appointment_monthly._singular = "vw_appointment_monthly"
db.vw_appointment_monthly._plural   = "vw_appointment_monthly"               
                
db.define_table('vw_appointment_weekly',
                Field('f_title', 'string'),
                Field('f_patientname', 'string'),
                Field('f_start_time', 'datetime'),
                Field('f_duration', 'integer'),
                Field('f_status', 'string'),
                
                Field('description', 'string'),
                Field('providerid', 'integer'),
                Field('doctorname','string'),
                Field('doctorid','integer'),    
                Field('treatmentid','integer'),
                Field('treatment','string'),
                Field('patientid', 'integer'),
                Field('memberid','integer'),
                Field('clinicid', 'integer'),
                
                Field('patientcell','string'),
                Field('newpatient','boolean'),
                Field('patienttype','string'),
                Field('appointmentblock','string'),
                Field('doccolor','string'),
                Field('apptcolor','string'),
                Field('is_active','boolean')
                )
db.vw_appointment_weekly._singular = "vw_appointment_weekly"
db.vw_appointment_weekly._plural   = "vw_appointment_weekly"        
                
db.define_table('vw_provider',
                Field('providerid', 'integer'),
                Field('provider', 'string'),
                Field('is_active','boolean'),
                Field('IND_VC','boolean')
                
                )
db.vw_provider._singular = "vw_provider"
db.vw_provider._plural   = "vw_provider"
          
db.define_table('vw_procedurepriceplancode',
                Field('id', 'integer'),
                Field('procedurepriceplancode', 'string')
                )
db.vw_procedurepriceplancode._singular = "vw_procedurepriceplancode"
db.vw_procedurepriceplancode._plural   = "vw_procedurepriceplancode"                

#db.define_table('consentform',
                #Field('id', 'integer'),
                #Field('consentform', 'string'),
                #Field('formcontent', 'text'),
                #auth.signature
                #)
#db.consentform._singular = "consentform"
#db.consentform._plural   = "consentform"                

db.define_table('vw_appointments',
                Field('id','integer'),
                Field('f_title', 'string'),
                Field('f_patientname', 'string'),
                Field('cell', 'string'),
                Field('f_start_time', 'datetime'), 
                Field('f_end_time', 'datetime'),
                Field('f_duration', 'string'),
                Field('f_location','string'),
                Field('f_uniqueid', 'integer'),
                Field('f_treatmentid', 'integer'),
                Field('f_status', 'string'),
                Field('newpatient', 'boolean'),
                Field('blockappt', 'boolean'),
                Field('description','string'),
                Field('provider', 'reference provider'),
                Field('doctor', 'integer'),
                Field('patient', 'integer'),
                Field('patientmember', 'string'),
                Field('sendsms', 'boolean'),
                Field('sendrem', 'boolean'),
                Field('smsaction', 'string'),
                Field('docname', 'string'),
                Field('doccell', 'string'),
                Field('docemail', 'string'),
                Field('provcell', 'string'),
                Field('clinic', 'string'),
                Field('provname', 'string'),
                Field('provemail','string'),
                Field('color','string'),
                Field('docsms', 'boolean'),
                Field('docemailflag', 'boolean'),
                Field('groupsms', 'boolean'),
                Field('groupemail', 'boolean'),
                Field('provtel', 'string'),
                Field('companyid', 'integer'),
                Field('groupref', 'string'),
                Field('membercode', 'string'),
                Field('dob', 'datetime',requires=IS_DATE(format=T('%d/%m/%Y'))),
                Field('gender', 'string'),
                Field('hmopatientmember', 'boolean',default="False"),
                Field('clinicid', 'integer'),
                Field('clinic_ref', 'string'),
                Field('clinic_name', 'string'),
                
                auth.signature
    )


db.define_table('vw_paymentgroup',
                Field('id', 'integer'),
                Field('lastpaymentdate', 'date'),
                Field('paymentcount', 'integer'),
                Field('amount', 'double'),
                auth.signature
                )
db.vw_paymentgroup._singular = "vw_paymentgroup"
db.vw_paymentgroup._plural   = "vw_paymentgroup"



db.define_table('vw_treatment_procedure_group',
                Field('id', 'integer'),
                Field('treatmentid', 'integer'),
                Field('shortdescription', 'text'),
                
                auth.signature
                )
db.vw_treatment_procedure_group._singular = "vw_treatment_procedure_group"
db.vw_treatment_procedure_group._plural   = "vw_treatment_procedure_group"


db.define_table('vw_payments',
    Field('id','integer'),
          
    Field('treatment', 'string',represent=lambda v, r: '' if v is None else v),
    Field('treatmentid', 'integer',represent=lambda v, r: 0 if v is None else v),
    Field('treatmentdate', 'date',represent=lambda v, r: '' if v is None else v,requires=IS_DATE(format=T('%d/%m/%Y'))),
    Field('shortdescription', 'text',represent=lambda v, r: '' if v is None else v), 
    Field('memberid', 'integer',represent=lambda v, r: 0 if v is None else v),
    Field('patientid', 'integer',represent=lambda v, r: 0 if v is None else v),
    Field('providerid','integer',represent=lambda v, r: 0 if v is None else v),
    Field('patientname', 'string',represent=lambda v, r: '' if v is None else v),
    Field('voucher_code', 'string',represent=lambda v, r: '' if v is None else v),
    Field('lastpayment', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('lastpaymentdate', 'date',represent=lambda v, r: '' if v is None else v,requires=IS_DATE(format=T('%d/%m/%Y'))),
    Field('totaltreatmentcost', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalcopay','double',represent=lambda v, r: 0 if v is None else v),
    Field('totalinspays', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalmemberpays', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalpaid', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalcopaypaid', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalinspaid', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totaldue', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalcompanypays', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalwalletamount', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totaldiscount_amount', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('is_active', 'boolean',represent=lambda v, r: 0 if v is None else v),
   


    auth.signature
    )

db.vw_payments._singular = "vw_payments"
db.vw_payments._plural   = "vw_payments"



    
db.define_table('vw_payments_fast',
    Field('id','integer'),
          
    Field('treatment', 'string',represent=lambda v, r: '' if v is None else v),
    Field('treatmentid', 'integer',represent=lambda v, r: 0 if v is None else v),
    Field('treatmentdate', 'date',represent=lambda v, r: '' if v is None else v,requires=IS_DATE(format=T('%d/%m/%Y'))),
    #Field('shortdescription', 'text',represent=lambda v, r: '' if v is None else v), 
    Field('memberid', 'integer',represent=lambda v, r: 0 if v is None else v),
    Field('patientid', 'integer',represent=lambda v, r: 0 if v is None else v),
    Field('providerid','integer',represent=lambda v, r: 0 if v is None else v),
   
    Field('voucher_code', 'string',represent=lambda v, r: '' if v is None else v),
    #Field('lastpayment', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('lastpaymentdate', 'date',represent=lambda v, r: '' if v is None else v,requires=IS_DATE(format=T('%d/%m/%Y'))),
    Field('totaltreatmentcost', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalcopay','double',represent=lambda v, r: 0 if v is None else v),
    Field('totalinspays', 'double',represent=lambda v, r: 0 if v is None else v),
    #Field('totalmemberpays', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalpaid', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalcopaypaid', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalinspaid', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totaldue', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalcompanypays', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalwalletamount', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totaldiscount_amount', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('is_active', 'boolean',represent=lambda v, r: 0 if v is None else v)
   



    )

db.vw_payments_fast._singular = "vw_payments_fast"
db.vw_payments_fast._plural   = "vw_payments_fast"




db.define_table('activitytracker',
    Field('id','integer'),
    Field('memberid', 'integer',represent=lambda v, r: 0 if v is None else v),
    Field('patientid', 'integer',represent=lambda v, r: 0 if v is None else v),
    Field('appointmentid', 'integer',represent=lambda v, r: 0 if v is None else v),
    Field('treatmentid', 'integer',represent=lambda v, r: 0 if v is None else v),
    Field('paymentid', 'integer',represent=lambda v, r: 0 if v is None else v),
    Field('providerid', 'integer',represent=lambda v, r: 0 if v is None else v),
    Field('doctorid', 'integer',represent=lambda v, r: 0 if v is None else v),
    Field('providername', 'string',represent=lambda v, r: '' if v is None else v),
    Field('doctorname', 'string',represent=lambda v, r: '' if v is None else v),
    Field('patientmember', 'string',represent=lambda v, r: '' if v is None else v),
    Field('patientname', 'string',represent=lambda v, r: '' if v is None else v),
    Field('appointmentdate', 'datetime',represent=lambda v, r: '' if v is None else v,requires=IS_DATETIME(format=T('%d/%m/%Y %I:%M %p'))),
    Field('appointmentstatus', 'string',represent=lambda v, r: '' if v is None else v),
    Field('lastapptactivity', 'datetime',represent=lambda v, r: '' if v is None else v,requires=IS_DATETIME(format=T('%d/%m/%Y %I:%M %p'))),

          
    Field('treatment', 'string',represent=lambda v, r: '' if v is None else v),
    Field('treatmentdate', 'date',represent=lambda v, r: '' if v is None else v,requires=IS_DATE(format=T('%d/%m/%Y'))),
    Field('treatmentstatus', 'string',represent=lambda v, r: '' if v is None else v),
    Field('procedures', 'string',represent=lambda v, r: '' if v is None else v),
    Field('treatmentcost', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('lasttreatmentactivity', 'datetime',represent=lambda v, r: '' if v is None else v,requires=IS_DATETIME(format=T('%d/%m/%Y %I:%M %p'))),

    Field('paymentdate', 'datetime',represent=lambda v, r: '' if v is None else v,requires=IS_DATE(format=T('%d/%m/%Y'))),
    Field('paymentmode', 'string',represent=lambda v, r: '' if v is None else v),
    Field('paymentamount', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('paymentinvoice', 'string',represent=lambda v, r: '' if v is None else v),
    
    Field('totalcost', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalpaid', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totaldue', 'double',represent=lambda v, r: 0 if v is None else v),
    
    Field('is_active', 'boolean',represent=lambda v, r: 0 if v is None else v),
    
    Field('customerid', 'integer',represent=lambda v, r: 0 if v is None else v),
    Field('customer_ref', 'string',represent=lambda v, r: '' if v is None else v),
    Field('customer_name', 'string',represent=lambda v, r: '' if v is None else v),
    Field('company', 'string',represent=lambda v, r: '' if v is None else v),
    Field('hmoplan', 'string',represent=lambda v, r: '' if v is None else v),
    Field('region', 'string',represent=lambda v, r: '' if v is None else v),
    Field('provider', 'string',represent=lambda v, r: '' if v is None else v),
    Field('enrolledon', 'date',represent=lambda v, r: '' if v is None else v,requires=IS_DATE(format=T('%d/%m/%Y' ))),
    Field('appointmenton', 'datetime',represent=lambda v, r: '' if v is None else v,requires=IS_DATETIME(format=T('%d/%m/%Y %I:%M %p'))),    
  

    auth.signature
    )

db.activitytracker._singular = "activitytracker"
db.activitytracker._plural   = "activitytracker"

db.define_table('vw_doctor',
    Field('id','integer'),
    Field('doctorid','integer'),
    Field('providerid','integer'),
    Field('roleid','integer'),
    Field('specialityid','integer'),
    Field('doctortitle', 'string'),                
    Field('doctorname', 'string'),
    Field('speciality','string'),
    Field('role','string'),
    Field('cell','string'),
    Field('email','string'),
    Field('registration','string'),
    Field('color','string'),
    Field('stafftype','string'),
    Field('notes','text'),
    Field('practice_owner','boolean'),
    Field('is_active','boolean'),
    Field('IND_IS_SYNC','boolean')
    
    )
    
    
db.define_table('vw_providertotalrevenue',
                Field('providerid', 'integer',represent=lambda v, r: 0 if v is None else v),
                Field('earnedrevenue', 'double',represent=lambda v, r: 0 if v is None else v),
                Field('paymentyear', 'integer',represent=lambda v, r: 0 if v is None else v)
                )




 


db.define_table('vw_memberdata',
    Field('id','integer'),
    Field('patientid','integer'),
    Field('primarypatientid','integer'),
    
    Field('patientmember','string'),
    Field('groupref','string'),
    Field('fname','string'),
    Field('mname','string'),
    Field('lname','string'),
    Field('address1','string'),
    Field('address2','string'),
    Field('address3','string'),
    Field('city','string'),
    Field('st','string'),
    Field('pin','string'),
    Field('cell','string'),
    Field('email','string'),
    Field('gender','string'),
    Field('relation','string'),
    Field('status','string'),
    Field('hmoplanname','string'),
    Field('hmoplancode','string'),
    Field('companycode','string'),
    Field('provider','string'),
    Field('provaddress1','string'),
    Field('provaddress2','string'),
    Field('provaddress3','string'),
    Field('provcity','string'),
    Field('provst','string'),
    Field('provpin','string'),
    Field('provcell','string'),
    Field('provemail','string'),
    
    Field('patienttype', 'boolean'),
    Field('renewed', 'boolean'),
    Field('upgraded', 'boolean'),

    Field('premium', 'double',represent=lambda v, r: 0 if v is None else v),

    Field('premstartdt', 'datetime',represent=lambda v, r: '' if v is None else v,requires=IS_DATE(format=T('%d/%m/%Y'))),
    Field('premenddt', 'datetime',represent=lambda v, r: '' if v is None else v,requires=IS_DATE(format=T('%d/%m/%Y'))),
    Field('dob', 'datetime',represent=lambda v, r: '' if v is None else v,requires=IS_DATE(format=T('%d/%m/%Y'))),

    Field('provactive', 'boolean'),
    Field('compactive', 'boolean'),
    Field('hmoactive', 'boolean'),
    Field('is_active', 'boolean')
    
    
)





 
 

db.define_table('vw_memberpaymentreport',
    Field('id','integer'),
    Field('treatmentid','integer'),
    
    Field('fppaymentref','string'),
    Field('fppaymenttype','string'),
    Field('fpinvoice','string'),
    
    Field('patienttype','string'),
    Field('patientmember','string'),
    Field('fname','string'),
    Field('mname','string'),
    Field('lname','string'),
    Field('city','string'),
    Field('st','string'),
    Field('pin','string'),
    Field('cell','string'),
    Field('email','string'),
   
    Field('provider','string'),
    Field('practicename','string'),
   
    Field('provcity','string'),
    Field('provst','string'),
    Field('provpin','string'),
    Field('provcell','string'),
    Field('provemail','string'),
    
    Field('treatment','string'),
    Field('shortdescription','string'),
     
     
    

    Field('invoiceamount', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('paymentamount', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totaltreatmentcost', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalcopay', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalinspays', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalpaid', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalcopaypaid', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totalinspaid', 'double',represent=lambda v, r: 0 if v is None else v),
    Field('totaldue', 'double',represent=lambda v, r: 0 if v is None else v),

    Field('paymentdate', 'datetime',represent=lambda v, r: '' if v is None else v,requires=IS_DATE(format=T('%d/%m/%Y'))),
    Field('is_active', 'boolean')
    
    
)

db.define_table('importrlgprovider',
    Field('id','integer'),
    Field('providercode','string'),
    Field('region','string'),
    Field('plan','string')
)


db.define_table('rlgservices',
    Field('id','integer'),
    Field('ackid','string'),
    Field('service_id','string')
)

db.define_table('rlgprovider',
    Field('id','integer'),
    Field('providerid','integer'),
    Field('providercode','string'),
    Field('regionid','integer'),
    Field('planid','integer'),
    Field('is_active', 'boolean')
    
)


#db.define_table('rlgplanprovider',
    #Field('id','integer'),
    #Field('providerid','integer'),
    #Field('policy','string'),
    #Field('planid','integer'),
    #Field('is_active', 'boolean')
    
#)


db.define_table('rlgdocument',
    Field('id','integer'),
    Field('rlgdocument','upload'),
    Field('rlgdocument_filename','string'),
    Field('membername','string'),
    Field('ackid','string'),
    Field('policy_number','string'),
    Field('policy_name','string'),
    Field('voucher_code','string'),
    Field('customer_id','string'),
    Field('mobile_number','string'),
    Field('docdate', 'date',default=request.now,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),length=20),
    Field('is_active', 'boolean'),
    Field('created_on', 'date',default=request.now,requires = IS_DATETIME(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),length=20),
    Field('modified_on', 'date',default=request.now,requires = IS_DATETIME(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),length=20),
    Field('created_by','integer'),
    Field('modified_by','integer')
    
)

#Religare 399 Voucher Coder
db.define_table('rlgvoucher',
                Field('plancode','string',length=10),
                Field('policy','string'),
                Field('vouchercode','string',length=10),
                Field('fname','string',length=128),
                Field('mname','string',length=128),
                Field('lname','string',length=128),
                Field('cell','string',length=20),
                Field('dob','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), \
                      label='Birth Date',length=20),
                Field('gender','string',length=10),
                Field('is_active','boolean',default=True),
                Field('created_on', 'datetime'),
                Field('modified_on', 'datetime'),
                Field('created_by','integer'),
                Field('modified_by','integer')
                
                )
db.rlgvoucher._singular = "rlgvoucher"
db.rlgvoucher._plural   = "rlgvoucher"


db.define_table('vw_rlgprovider',
        Field('id','integer'),
        Field('providerid','integer'),
        Field('providercode','string'),
        Field('providername','string'),
        Field('regionid','integer'),
        Field('planid','integer'),
        Field('is_active', 'boolean')
    
)




db.define_table('vw_relgrtreatmentprocedure',
        Field('providerid','integer'),


        
        Field('providercode','string'),
        Field('providername','string'),
        Field('practicename','string'),
        Field('practiceaddress','string'),

        Field('practiceaddress','string'),
        Field('practiceaddress','string'),
        Field('practiceaddress','string'),
        Field('practiceaddress','string'),
        
        Field('fullname','string'),
        Field('cell','string'),
        Field('groupref','string'),
        Field('patientmember','string'),
        
        Field('company','string'),
        
        Field('treatment','string'),
        Field('treatmentdate','datetime',requires=IS_DATE(format=T('%d/%m/%Y'))),
        Field('service_id','string'),
        Field('procedurecode','string'),
        Field('procdesc','string'),
        
        Field('procedurefee','double'),
        Field('inspays','double'),
        Field('inspays_GST','double'),
        Field('copay','double'),
        Field('tooth','string'),
        Field('quadrant','string'),
        
        Field('regno','string'),
       
        
        Field('relgrproc', 'boolean'),
        Field('relgrprocdesc','string'),
        Field('relgrtransactionid','string'),
        Field('status','string'),
        
        Field('is_active', 'boolean')
    
)

db.define_table('rlgerrormessage',
        Field('id','integer'),
        Field('code','string'),
        Field('internalmessage','string'),
        Field('externalmessage','string'),
        Field('is_active', 'boolean')
    
)
db.rlgerrormessage._singular = "rlgerrormessage"
db.rlgerrormessage._plural = "rlgerrormessage"
               


#MEDIASSIST CLAIM FORM Tables
db.define_table('mediclaim',
                
                Field('id','integer'),
                Field('providerid','integer'),
                Field('treatmentid','reference treatment'), 
                Field('companyid','reference company'), 
                Field('memberid','reference patientmember'), 
                Field('patientid','reference patientmember'), 
                Field('final_statement','boolean',default=False), 
                Field('request_for_authorization','boolean',default=False), 
                Field('oralprophylate','boolean',default=False), 
                Field('orthodontics','boolean',default=False), 
                Field('preauth_number','string'), 
                Field('history','string'), 
                Field('allergy','string'), 
                Field('chiefcomplaint','string'), 
                Field('attendingdoctor','string'), 
                Field('remarks','text'), 
                Field('is_active','boolean'), 
                auth.signature
                
)
db.mediclaim._singular = "mediclaim"
db.mediclaim._plural = "mediclaim"




db.define_table('mediclaim_procedures',
                Field('id','integer'),
                Field('mediclaimid','reference mediclaim'),                 
                Field('procedureid','reference dentalprocedure'),   
                Field('treatmentprocedureid','reference treatment_procedure'),   
                Field('procdate','date',default=request.now, requires=IS_DATE(format=T('%d/%m/%Y')),length=20),
                Field('tooth','string',default=""),
                Field('description','string',default=""),
                Field('quantity','string',default=""),
                Field('cashless','string',default=""), 
                Field('status','string',default=""),
                Field('is_active','boolean',default=True), 
                auth.signature
                )
db.mediclaim_procedures._singular = "mediclaim_procedures"
db.mediclaim_procedures._plural = "mediclaim_procedures"



db.define_table('mediclaim_attachments',
                Field('id','integer'),
                Field('mediclaimid','reference mediclaim'),  
                Field('attachment','upload'), 
                Field('title','string'), 
                Field('description','text'), 
                Field('is_active','boolean'), 
                auth.signature
                )
db.mediclaim_attachments._singular = "mediclaim_attachments"
db.mediclaim_attachments._plural = "mediclaim_attachments"



db.define_table('mediclaim_signatures',
                Field('id','integer'),
                Field('mediclaimid','reference mediclaim'),  
                Field('employee_signature','upload'), 
                Field('employee_signature_date','date'), 
                Field('dentist_signature','upload'), 
                Field('dentist_signature_date','date'), 
                Field('is_active','boolean'), 
                auth.signature
                )
db.mediclaim_signatures._singular = "mediclaim_signatures"
db.mediclaim_signatures._plural = "mediclaim_signatures"



db.define_table('mediclaim_charts',
                Field('id','integer'),
                Field('mediclaimid','reference mediclaim'),  
                Field('restoration_ul_1','boolean',default=False), 
                Field('restoration_ul_2','boolean',default=False), 
                Field('restoration_ul_3','boolean',default=False), 
                Field('restoration_ul_4','boolean',default=False), 
                Field('restoration_ul_5','boolean',default=False), 
                Field('restoration_ul_6','boolean',default=False), 
                Field('restoration_ul_7','boolean',default=False), 
                Field('restoration_ul_8','boolean',default=False), 
                Field('restoration_ur_1','boolean',default=False), 
                Field('restoration_ur_2','boolean',default=False), 
                Field('restoration_ur_3','boolean',default=False), 
                Field('restoration_ur_4','boolean',default=False), 
                Field('restoration_ur_5','boolean',default=False), 
                Field('restoration_ur_6','boolean',default=False), 
                Field('restoration_ur_7','boolean',default=False), 
                Field('restoration_ur_8','boolean',default=False), 
                Field('restoration_ll_1','boolean',default=False), 
                Field('restoration_ll_2','boolean',default=False), 
                Field('restoration_ll_3','boolean',default=False), 
                Field('restoration_ll_4','boolean',default=False), 
                Field('restoration_ll_5','boolean',default=False), 
                Field('restoration_ll_6','boolean',default=False), 
                Field('restoration_ll_7','boolean',default=False), 
                Field('restoration_ll_8','boolean',default=False), 
                Field('restoration_lr_1','boolean',default=False), 
                Field('restoration_lr_2','boolean',default=False), 
                Field('restoration_lr_3','boolean',default=False), 
                Field('restoration_lr_4','boolean',default=False), 
                Field('restoration_lr_5','boolean',default=False), 
                Field('restoration_lr_6','boolean',default=False), 
                Field('restoration_lr_7','boolean',default=False), 
                Field('restoration_lr_8','boolean',default=False), 
                
                Field('rootcanal_ul_1','boolean',default=False), 
                Field('rootcanal_ul_2','boolean',default=False), 
                Field('rootcanal_ul_3','boolean',default=False), 
                Field('rootcanal_ul_4','boolean',default=False), 
                Field('rootcanal_ul_5','boolean',default=False), 
                Field('rootcanal_ul_6','boolean',default=False), 
                Field('rootcanal_ul_7','boolean',default=False), 
                Field('rootcanal_ul_8','boolean',default=False), 
                Field('rootcanal_ur_1','boolean',default=False), 
                Field('rootcanal_ur_2','boolean',default=False), 
                Field('rootcanal_ur_3','boolean',default=False), 
                Field('rootcanal_ur_4','boolean',default=False), 
                Field('rootcanal_ur_5','boolean',default=False), 
                Field('rootcanal_ur_6','boolean',default=False), 
                Field('rootcanal_ur_7','boolean',default=False), 
                Field('rootcanal_ur_8','boolean',default=False), 
                Field('rootcanal_ll_1','boolean',default=False), 
                Field('rootcanal_ll_2','boolean',default=False), 
                Field('rootcanal_ll_3','boolean',default=False), 
                Field('rootcanal_ll_4','boolean',default=False), 
                Field('rootcanal_ll_5','boolean',default=False), 
                Field('rootcanal_ll_6','boolean',default=False), 
                Field('rootcanal_ll_7','boolean',default=False), 
                Field('rootcanal_ll_8','boolean',default=False), 
                Field('rootcanal_lr_1','boolean',default=False), 
                Field('rootcanal_lr_2','boolean',default=False), 
                Field('rootcanal_lr_3','boolean',default=False), 
                Field('rootcanal_lr_4','boolean',default=False), 
                Field('rootcanal_lr_5','boolean',default=False), 
                Field('rootcanal_lr_6','boolean',default=False), 
                Field('rootcanal_lr_7','boolean',default=False), 
                Field('rootcanal_lr_8','boolean',default=False), 

                Field('extract_ul_1','boolean',default=False), 
                Field('extract_ul_2','boolean',default=False), 
                Field('extract_ul_3','boolean',default=False), 
                Field('extract_ul_4','boolean',default=False), 
                Field('extract_ul_5','boolean',default=False), 
                Field('extract_ul_6','boolean',default=False), 
                Field('extract_ul_7','boolean',default=False), 
                Field('extract_ul_8','boolean',default=False), 
                Field('extract_ur_1','boolean',default=False), 
                Field('extract_ur_2','boolean',default=False), 
                Field('extract_ur_3','boolean',default=False), 
                Field('extract_ur_4','boolean',default=False), 
                Field('extract_ur_5','boolean',default=False), 
                Field('extract_ur_6','boolean',default=False), 
                Field('extract_ur_7','boolean',default=False), 
                Field('extract_ur_8','boolean',default=False), 
                Field('extract_ll_1','boolean',default=False), 
                Field('extract_ll_2','boolean',default=False), 
                Field('extract_ll_3','boolean',default=False), 
                Field('extract_ll_4','boolean',default=False), 
                Field('extract_ll_5','boolean',default=False), 
                Field('extract_ll_6','boolean',default=False), 
                Field('extract_ll_7','boolean',default=False), 
                Field('extract_ll_8','boolean',default=False), 
                Field('extract_lr_1','boolean',default=False), 
                Field('extract_lr_2','boolean',default=False), 
                Field('extract_lr_3','boolean',default=False), 
                Field('extract_lr_4','boolean',default=False), 
                Field('extract_lr_5','boolean',default=False), 
                Field('extract_lr_6','boolean',default=False), 
                Field('extract_lr_7','boolean',default=False), 
                Field('extract_lr_8','boolean',default=False), 

                Field('missing_ul_1','boolean',default=False), 
                Field('missing_ul_2','boolean',default=False), 
                Field('missing_ul_3','boolean',default=False), 
                Field('missing_ul_4','boolean',default=False), 
                Field('missing_ul_5','boolean',default=False), 
                Field('missing_ul_6','boolean',default=False), 
                Field('missing_ul_7','boolean',default=False), 
                Field('missing_ul_8','boolean',default=False), 
                Field('missing_ur_1','boolean',default=False), 
                Field('missing_ur_2','boolean',default=False), 
                Field('missing_ur_3','boolean',default=False), 
                Field('missing_ur_4','boolean',default=False), 
                Field('missing_ur_5','boolean',default=False), 
                Field('missing_ur_6','boolean',default=False), 
                Field('missing_ur_7','boolean',default=False), 
                Field('missing_ur_8','boolean',default=False), 
                Field('missing_ll_1','boolean',default=False), 
                Field('missing_ll_2','boolean',default=False), 
                Field('missing_ll_3','boolean',default=False), 
                Field('missing_ll_4','boolean',default=False), 
                Field('missing_ll_5','boolean',default=False), 
                Field('missing_ll_6','boolean',default=False), 
                Field('missing_ll_7','boolean',default=False), 
                Field('missing_ll_8','boolean',default=False), 
                Field('missing_lr_1','boolean',default=False), 
                Field('missing_lr_2','boolean',default=False), 
                Field('missing_lr_3','boolean',default=False), 
                Field('missing_lr_4','boolean',default=False), 
                Field('missing_lr_5','boolean',default=False), 
                Field('missing_lr_6','boolean',default=False), 
                Field('missing_lr_7','boolean',default=False), 
                Field('missing_lr_8','boolean',default=False), 

                Field('xray_ul_1','boolean',default=False), 
                Field('xray_ul_2','boolean',default=False), 
                Field('xray_ul_3','boolean',default=False), 
                Field('xray_ul_4','boolean',default=False), 
                Field('xray_ul_5','boolean',default=False), 
                Field('xray_ul_6','boolean',default=False), 
                Field('xray_ul_7','boolean',default=False), 
                Field('xray_ul_8','boolean',default=False), 
                Field('xray_ur_1','boolean',default=False), 
                Field('xray_ur_2','boolean',default=False), 
                Field('xray_ur_3','boolean',default=False), 
                Field('xray_ur_4','boolean',default=False), 
                Field('xray_ur_5','boolean',default=False), 
                Field('xray_ur_6','boolean',default=False), 
                Field('xray_ur_7','boolean',default=False), 
                Field('xray_ur_8','boolean',default=False), 
                Field('xray_ll_1','boolean',default=False), 
                Field('xray_ll_2','boolean',default=False), 
                Field('xray_ll_3','boolean',default=False), 
                Field('xray_ll_4','boolean',default=False), 
                Field('xray_ll_5','boolean',default=False), 
                Field('xray_ll_6','boolean',default=False), 
                Field('xray_ll_7','boolean',default=False), 
                Field('xray_ll_8','boolean',default=False), 
                Field('xray_lr_1','boolean',default=False), 
                Field('xray_lr_2','boolean',default=False), 
                Field('xray_lr_3','boolean',default=False), 
                Field('xray_lr_4','boolean',default=False), 
                Field('xray_lr_5','boolean',default=False), 
                Field('xray_lr_6','boolean',default=False), 
                Field('xray_lr_7','boolean',default=False), 
                Field('xray_lr_8','boolean',default=False), 


                Field('is_active','boolean'), 
                auth.signature
                )
db.mediclaim_charts._singular = "mediclaim_charts"
db.mediclaim_charts._plural = "mediclaim_charts"

db.define_table('customer',
               Field('customer', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Member ID',length=50),
               Field('customer_ref', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Employee ID',length=50),
               Field('fname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='First',length=50),
               Field('mname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Middle',length=50),
               Field('lname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Last',length=50),
               Field('address1', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Address 1', length=50),
               Field('address2', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=50),
               Field('address3', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=50),
               Field('city', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='City',length=50,requires = IS_IN_SET(CITIES)),
               Field('st', 'string',represent=lambda v, r: '' if v is None else v, default='None',label='State',length=50,requires = IS_IN_SET(STATES)),
               Field('pin', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',length=20),
               Field('gender','string',represent=lambda v, r: '' if v is None else v, default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
               Field('telephone', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Telephone',length=20),
               Field('cell', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Cell',length=20),
               Field('email', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Email',length=50),
               Field('dob',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Birth Date',default=request.now,  requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),length=20),
               Field('status', 'string',represent=lambda v, r: '' if v is None else v, label='Status',default='No_Attempt',requires = IS_IN_SET(STATUS)),
               Field('enrolldate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Web Enroll Date',default=request.now,requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),length=20),
               Field('companyid','reference company'),
               Field('providerid','reference provider'),
               Field('clinicid','integer'),
               Field('regionid','reference groupregion'),
               Field('planid','reference hmoplan'),
               Field('pin1', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',length=20),
               Field('pin2', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',length=20),
               Field('pin3', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',length=20),
               Field('appointment_id','string'),
               Field('appointment_datetime','datetime', default=request.now, requires=IS_DATETIME(format=T('%d/%m/%Y %H:%M:%S'))),
               Field('tx_id','string'),
               Field('payment_id','string'),
               Field('payment_status','string'),
               Field('payment_amount','double'),
               Field('amount_paid','double'),
               Field('payment_date','datetime', default=request.now, requires=IS_DATETIME(format=T('%d/%m/%Y'))),
               
               
               Field('notes','text'),
               
               auth.signature,
                 format='%(customer)s'
               )
db.customer._singular = "Customer"
db.customer._plural   = "Customer"


db.define_table('customerdependants',
               Field('dependant', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Dependant',length=50),
               Field('dependant_ref', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Employee ID',length=50),
               Field('customer_id','reference customer'),
               Field('fname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='First',length=50),
               Field('mname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Middle',length=50),
               Field('lname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Last',length=50),
               Field('depdob',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Birth Date',default=request.now,  requires=IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),length=20),
               Field('gender','string',represent=lambda v, r: '' if v is None else v, default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
               Field('relation','string',represent=lambda v, r: '' if v is None else v, default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
               auth.signature,
                format='%(dependant)s'
               )
db.customerdependants._singular = "customerdependants"
db.customerdependants._plural   = "customerdependants"




db.define_table('customeractivity',
               Field('customerid',  widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border w3-small'), requires=IS_IN_DB(db, 'customer.id', '%(fname)s (%(lname)s)')),
               Field('customer','string'), 
               Field('customer_ref','string'), 
               Field('activitydate','datetime', default=request.now, requires=IS_DATETIME(format=T('%d/%m/%Y %H:%M'))),
               Field('status','string',represent=lambda v, r: '' if v is None else v, default='Scheduled',label='Status',requires = IS_IN_SET(CUSTACTIVITY)),
               Field('activity', 'text',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Middle',length=50),
               auth.signature
               )
db.customeractivity._singular = "customeractivity"
db.customeractivity._plural   = "customeractivity"




db.define_table('booking',
      
                
                Field('booking_id','string'),
                Field('package_name','string'),
                Field('name','string'),
                Field('email','string'),
                Field('contact','string'),
                Field('cell','string'),
                Field('city','string'),
                Field('pincode','string'),
                Field('tx_id','string'),
                Field('payment_id','string'),
                Field('payment_status','string'),
                Field('notes','text'),
                
                Field('package_cost','double'),
                Field('package_offer_price','double'),
                Field('package_booking_amount','double'),
                Field('payment_amount','double'),
                Field('amount_paid','double'),
                
                Field('package_start_date','datetime',requires = IS_DATE(format=T('%d/%m/%Y'))),
                Field('package_end_date','datetime',requires = IS_DATE(format=T('%d/%m/%Y'))),
                Field('payment_date','datetime',requires = IS_DATE(format=T('%d/%m/%Y'))),
                
                Field('status','string'),
                auth.signature
                
                )

db.booking._singular = "booking"
db.booking._plural   = "booking"


db.define_table('package_region_plan',
                Field('package_code','string'),
                Field('package_name','string'),
                Field('city','string'),
                Field('region','string'),
                Field('plancode','string')
                )
db.package_region_plan._singular = "package_region_plan"
db.package_region_plan._plural   = "package_region_plan"


db.define_table('vw_customer',
               Field('id','integer'),
               Field('customerid', 'integer'),
               Field('customer', 'string'),
               Field('customer_ref', 'string'),
               Field('customername', 'string'),
               Field('address', 'string'),
               Field('cell', 'string'),
               Field('email', 'string'),
               Field('gender', 'string'),
               Field('dob', 'date'),
               
               Field('company', 'string'),
               Field('groupregion', 'string'),
               Field('provider', 'string'),
               Field('hmoplancode', 'string'),
               
               Field('appointment_id', 'string'),
               Field('appointment_datetime', 'datetime'),
               Field('notes', 'text'),
               Field('status', 'string'),
               Field('is_active', 'boolean')
                     
              
               
               )
db.vw_customer._singular = "vw_customer"
db.vw_customer._plural   = "vw_customer"


db.define_table('vw_customer_dependants',
               Field('id','integer'),
               Field('dependant_id', 'integer'),
               Field('dependant', 'string'),
               Field('dependant_ref', 'string'),
               Field('dependant_name', 'string'),
              
               Field('dependant_gender', 'string'),
               Field('dependant_dob', 'date'),
               
               Field('dependant_relation', 'string'),
               Field('dependant_is_active', 'boolean'),
               
               Field('customer', 'string'),
               Field('customer_ref', 'string'),
               Field('customer_id', 'integer')
               
              
               
               )
db.vw_customer_dependants._singular = "vw_customer_dependants"
db.vw_customer_dependants._plural   = "vw_customer_dependants"

db.define_table('vw_customertopcount',
               Field('id','integer'),
               Field('companyid', 'integer'),
               Field('company', 'string'),
               Field('customer_count','integer')
               )
db.vw_customertopcount._singular = "vw_customertopcount"
db.vw_customertopcount._plural   = "vw_customertopcount"

db.define_table('vw_customerdetailcount',
               Field('id','integer'),
            
               Field('company', 'string'),
               Field('enrolldate', 'date'),
               Field('customer_count','integer')
               )
db.vw_customertopcount._singular = "vw_customertopcount"
db.vw_customertopcount._plural   = "vw_customertopcount"

db.define_table('media',
                Field('title', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Title'),
                Field('media','upload',length=255),
                Field('uploadfolder','string'),
                Field('tooth', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Tooth',length=20),
                Field('quadrant', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Quadrant',length=20),
                Field('mediadate', 'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'),length=20),
                Field('description', 'text', default='',label='Description',length=128),
                Field('treatmentplan', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('treatment', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('patientmember', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('patient', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('provider', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('patientname', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('patienttype', 'string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('provider', 'integer',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                
                Field('mediafile', 'string',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),                
                Field('mediatype', 'string',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),                
                Field('mediaformat', 'string',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),                
                Field('mediasize', 'double',represent=lambda v, r: 0 if v is None else v,widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details')),                
                
                Field('dicomUserUuid', 'string',default=''),
                Field('dicomAcctUuid', 'string',default=''),
                Field('dicomInstUuid', 'string',default=''),
                Field('dicomPatName', 'string',default=''),
                Field('dicomPatUuid', 'string',default=''),
                Field('dicomPatid', 'string',default=''),
                Field('dicomPatOrderUuid', 'string',default=''),
                Field('dicomProcDesc', 'string',default=''),
                Field('dicomPerformedDate', 'string',default=''),
                Field('dicomURL', 'string',default=''),
                
                auth.signature,
                format = '%(title)s')
db.media._singular = "Media"
db.media._plural = "Media"
  


db.define_table('vw_abhicl_report',
                Field('id','integer'),
                Field('treatmentid','integer'),
                Field('treatment','string'),
                Field('startdate','date'),
                Field('enddate','date'),
                Field('status','string'),
                Field('chiefcomplaint','string'),
                Field('Attending_Doctor','string'),
                Field('tooth','string'),
                Field('quadrant','string'),
                #Field('dentalprocedure','string'),
                #Field('procedure_name','string'),
                Field('doctor_notes','text'),
                #Field('prescription','string'),
                Field('providerid','integer'),
                #Field('providercode','string'),
                #Field('memberid','integer'),
                #Field('companyid','integer'),
                #Field('company','string')
                Field('is_active','boolean')
            
                
                )


db.define_table('vw_abhicl_report_group',
                Field('id','integer'),
                Field('treatmentid','integer'),
                Field('treatment','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('startdate','date'),
                Field('enddate','date'),
                Field('status','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('chiefcomplaint','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('Attending_Doctor','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('procedure_code','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('procedure_name','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),               
                Field('tooth','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('quadrant','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('doctor_notes','text',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('prescription','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('providerid','integer'),
                Field('providercode','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('is_active','boolean'),
                Field('memberid','integer'),
                Field('companyid','integer'),
                Field('company','string',represent=lambda v, r: '' if v is None else v,widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                
                
                )




 

db.define_table('consentform',
                
                Field('providerid','integer'),
                Field('memberid','integer'),
                Field('patientid','integer'),
                Field('clinicid','integer'),
                Field('doctorid','integer'),
                Field('consentformid','integer'),
                Field('consentform_date','date'),
                Field('consentform_code','string'),
                Field('consentform_name','string'),
                Field('procedurecode','string'),
                Field('procedurename','string'),
                Field('patientname','string'),
                Field('membername','string'),
                
                Field('status','string'),
                Field('is_active','boolean'),
                
                auth.signature
                            
                
                )

db.consentform._singular = "consentform"
db.consentform._plural   = "consentform"   

db.define_table('vw_procedure_groupby_treatment',
                Field('treatmentid','integer'),
                Field('treatment','string'),
                
                Field('procedure_code','string'),
                Field('tooth','string'),
                Field('quadrant','string'),
                Field('procedure_name','string')
               
                )

db.define_table('vw_prescription_groupby_treatment',
                Field('prescriptiondate','date'),
                Field('Prescription','string'),
                
                Field('treatmentid','integer')
               
                )


db.define_table('vw_clinic',
                
                Field('id','integer'),
                Field('clinicid','integer'),
                
                
                Field('clinic_ref','string'),
                    
                Field('name','string'),
                Field('address1','string'),
                Field('address2','string'),
                Field('address3','string'),
                Field('city', 'string',default='--Select City--',label='City',length=50,requires = IS_IN_SET(CITIES)),
                Field('st', 'string',default='--Select State--',label='State',length=50,requires = IS_IN_SET(STATES)),
                Field('pin','string'),
                
                Field('cell','string'),
                Field('telephone','string'),
                Field('email','string'),

                Field('website','string'),
                Field('gps_location','string'),
                Field('whatsapp','string'),
                Field('facebook','string'),
                Field('twitter','string'),

                Field('status','string'),
                Field('primary_clinic','boolean'),
                
                Field('mdp_registration','string'),
                Field('dentalchairs','string'),
                Field('auto_clave','string',default='Yes',requires=IS_IN_SET(YESNO)),
                Field('implantology','string'),
                Field('instrument_sterilization','string'),
                Field('waste_displosal','string'),
                Field('suction_machine','string'),
                Field('laser','string'),
                Field('RVG_OPG','string'),
                
                Field('radiation_protection','string'),                
                Field('computers','string'),                
                Field('network','string'),                
                Field('internet','string'),                
                Field('air_conditioned','string'),                
                Field('waiting_area','string'),                
                Field('backup_power','string'),                
                Field('toilet','string'),                
                Field('water_filter','string'),                
                Field('parking_facility','string'),                
                Field('receptionist','string'),                
                Field('credit_card','string'),                
                Field('certifcates','string'),                
                Field('emergency_drugs','string'),                
                Field('infection_control','string'),                
                Field('daily_autoclaved','string'),                
                Field('patient_records','string'),                
                Field('patient_consent','string'),                
                Field('patient_traffic','string'),                
                Field('nabh_iso_certifcation','string'),     
                Field('intra_oral_camera','string'),     
                Field('rotary_endodontics','string'),     
                Field('bank_id','integer'), 
                
                Field('state_dental_registration','string'),
                Field('registration_certificate','string'),
                
                Field('notes','text'),
                Field('latitude','string'),
                Field('longitude','string'),
                
                Field('ref_code','string'),                
                Field('ref_id','integer'), 
                Field('clinic_id','integer'), 
                
                
                auth.signature                
                )

db.clinic._singular = "clinic"
db.clinic._plural   = "clinic"

db.define_table('redeem_voucher_wallet',
                
                Field('paymentid','integer'),
                Field('treatmentid','integer'),
                Field('treatment','string'),
                Field('paymentdate','date'),
                Field('treatmentdate','date'),
                Field('discount_amount','double',default=0.00),
                Field('wallet_amount','double',default=0.00),
                Field('voucher_code','string')
                
                )

db.consentform._singular = "consentform"
db.consentform._plural   = "consentform"   

db.define_table('kytc_category',
                
                Field('name','string'),
                Field('parent_id','integer'),
                Field('child_id','integer',default=0),
                Field('status','integer',default=1)
                )
db.kytc_category._singular = "kytc_category"
db.kytc_category._plural   = "kytc_category"  

db.define_table('kytc_procedure',
                
                Field('code','string'),
                Field('name','string'),
                Field('tcat_id','integer'),
                
                Field('rg101_ucr','integer'),
                Field('rg101_copay','integer'),
                Field('rg102_copay','integer'),
                Field('rg102_ucr','integer'),
                Field('rg103_ucr','integer'),
                Field('rg103_copay','integer'),
                Field('rg104_ucr','integer'),
                Field('rg104_copay','integer'),
                Field('rg104_copay','integer'),
                Field('status','string', default=1)
                
                )
db.kytc_procedure._singular = "kytc_procedure"
db.kytc_procedure._plural   = "kytc_procedure"  


db.define_table('kytc_track_log',
                Field('user_id','integer'),
                
                Field('city','string'),
                Field('mobile','string'),
                Field('log_data','text')
                
                )
db.kytc_track_log._singular = "kytc_track_log"
db.kytc_track_log._plural   = "kytc_track_log"  

db.define_table('rules',
                Field('treatment_id','integer'),
                
                Field('procedure_code','string'),
                Field('company_code','string'),
                Field('plan_code','string'),
                Field('rule_code','string'),
                Field('description','string'),
                Field('rule_event','string'),
                Field('rule_order','integer',default=0),
                Field('is_active','boolean', default = True),
                auth.signature  
                )
db.rules._singular = "rules"
db.rules._plural   = "rules"


db.define_table('mdp_nonmdp',
                Field('prospect_id','integer'),
                Field('provider_id','integer'),
                Field('clinic_id','integer'),
                Field('image_id','integer')
                
                
                )
db.mdp_nonmdp._singular = "mdp_nonmdp"
db.mdp_nonmdp._plural   = "mdp_nonmdp"  




db.define_table('vw_agent_prospect_clinic',
                Field('id','integer'),
                Field('agent_id','integer'),
                Field('prospect_id','string'),
                Field('clinic_id','integer'),
                Field('agent_add_date','date'),
                Field('prospect_add_date','date'),
                Field('clinic_add_date','date'),
                Field('agent','string'),
                Field('agent_name','string'),
                Field('providername','string'),
                Field('clinic_ref','string'),
                Field('clinic_name','string'),
                Field('clinic_city','string'),
                Field('clinic_pin','string')



                )


db.vw_agent_prospect_clinic._singular = "vw_agent_prospect_clinic"
db.vw_agent_prospect_clinic._plural   = "vw_agent_prospect_clinic"  

def geocode2(form):
    from gluon.tools import geocode
    lo,la= geocode(form.vars.f_location+' USA')
    form.vars.f_latitude=la
    form.vars.f_longitude=lo






#db.provider.update_or_insert(provider=' ', providername=' ', is_active=False)
#db.groupregion.update_or_insert(groupregion=' ', region=' ', is_active=False)
#db.agent.update_or_insert(agent=' ', name=' ', is_active=False)
#db.hmoplan.update_or_insert(hmoplancode=' ', name=' ', is_active=False)


#db.monthly.update_or_insert(premmonth=1)
#db.monthly.update_or_insert(premmonth=2)
#db.monthly.update_or_insert(premmonth=3)
#db.monthly.update_or_insert(premmonth=4)
#db.monthly.update_or_insert(premmonth=5)
#db.monthly.update_or_insert(premmonth=6)
#db.monthly.update_or_insert(premmonth=7)
#db.monthly.update_or_insert(premmonth=8)
#db.monthly.update_or_insert(premmonth=9)
#db.monthly.update_or_insert(premmonth=10)
#db.monthly.update_or_insert(premmonth=11)
#db.monthly.update_or_insert(premmonth=12)

db.webmember.fname.requires = IS_NOT_EMPTY()
db.webmember.lname.requires = IS_NOT_EMPTY()
db.webmember.address1.requires = IS_NOT_EMPTY()
db.webmember.address2.requires = IS_NOT_EMPTY()
#db.webmember.city.requires = IS_NOT_EMPTY()
db.webmember.pin.requires = IS_NOT_EMPTY()
db.webmember.cell.requires = IS_NOT_EMPTY()
db.webmember.email.requires = IS_NOT_EMPTY()
db.webmember.email.requires = IS_EMAIL(error_message = 'Invalid Email')



db.webmemberdependants.fname.requires = IS_NOT_EMPTY()
db.webmemberdependants.lname.requires = IS_NOT_EMPTY()

db.provider.providername.requires = IS_NOT_EMPTY()
db.provider.address1.requires = IS_NOT_EMPTY()
db.provider.address2.requires = IS_NOT_EMPTY()

db.provider.pin.requires = IS_NOT_EMPTY()
db.provider.cell.requires = IS_NOT_EMPTY()
db.provider.email.requires = IS_NOT_EMPTY()

db.patientmember.fname.requires = IS_NOT_EMPTY()
db.patientmember.lname.requires = IS_NOT_EMPTY()
db.patientmember.address1.requires = IS_NOT_EMPTY()
db.patientmember.address2.requires = IS_NOT_EMPTY()
db.patientmember.pin.requires = IS_NOT_EMPTY()
db.patientmember.cell.requires = IS_NOT_EMPTY()
db.patientmember.email.requires = IS_NOT_EMPTY()
db.patientmember.email.requires = IS_EMAIL(error_message = 'Invalid Email')


