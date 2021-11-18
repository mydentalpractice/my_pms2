from gluon import current
db = current.globalenv['db']



import json
import datetime
import time
from datetime import timedelta


from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger



#THIS API is called to determine the member's procedure price plan code based on 
#the provider's region, plan and policy
def getprocedurepriceplancodeformember(db,providerid,memberid,patientid,policy_name=""):
    logger.loggerpms2.info("Enter getprocedurepriceplancodeformember = " + str(providerid) + " " + str(memberid) + " " + str(patientid) + " " + policy_name)
    procedurepriceplancode = "PREMWALKIN"  #default it to PREMWALKIN
    
    try:   
        
        # get providers region via city
        provs = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.groupregion)
        regionid = int(common.getid(provs[0].groupregion)) if(len(provs) == 1) else 1
        regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select(db.groupregion.groupregion)
        regioncode = common.getstring(regions[0].groupregion) if(len(regions) == 1) else "ALL"
	
        
        # get patient's company
        pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.company,db.vw_memberpatientlist.hmoplan)
        companyid = int(common.getid(pats[0].company)) if(len(pats) == 1) else 0
        companys = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
        companycode = common.getstring(companys[0].company) if(len(companys) == 1) else "PREMWALKIN"

        #for backward compatibility determine procedurepriceplancode from member's plan at the time of registration
	def_planid = int(common.getid(pats[0].hmoplan)) if(len(pats) == 1) else 0  #this is the patient's previously assigned plan-typically at registration
	def_plans = db((db.hmoplan.id == def_planid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode)
	def_plancode = common.getstring(def_plans[0].hmoplancode) if(len(def_plans) == 1) else "PREMWALKIN"
	def_procedurepriceplancode = common.getstring(def_plans[0].procedurepriceplancode) if(len(def_plans) == 1) else "PREMWALKIN"

    
	#by default policy = companycode
	policy = companycode if policy_name == "" else policy_name 
	ppc = getprocedurepriceplancode(db, policy, None, regioncode, companycode)
	procedurepriceplancode = ppc["procedurepriceplancode"]
	procedurepriceplancode = def_procedurepriceplancode if(common.getstring(procedurepriceplancode) == "") else procedurepriceplancode

	
	logger.loggerpms2.info("getprocedurepriceplancodeformember 2 = " + common.getstring(regioncode) + " " + common.getstring(companycode) + " " + str(ppc["planid"]) + " " + common.getstring(ppc["plancode"]) + " " + common.getstring(procedurepriceplancode))
	
	#if policy_name == None, means you are adding procedure from web app
	#policy_name = None if(policy_name == "") else policy_name
        #if(policy_name == None):
	    #procedurepriceplancode = common.getstring(plans[0].procedurepriceplancode) if(len(plans) == 1) else "PREMWALKIN"
 	    #logger.loggerpms2.info("Enter getprocedurepriceplancodeformember 3 " + procedurepriceplancode)
        #else:
	    #policyname = plancode if(policy_name == "") else policy_name
            #d = getprocedurepriceplancode(db,policyname,None,regioncode,companycode,plancode)
            #procedurepriceplancode = d.get("procedurepriceplancode","PREMWALKIN")
	    #logger.loggerpms2.info("Enter getprocedurepriceplancodeformember 4 " + procedurepriceplancode)
    
    except Exception as e:
        raise Exception(str(e))
    
    return procedurepriceplancode

    
#THIS API is called to determine the member's procedure price plan code based on 
#the HV Regions
def getprocedurepriceplancodeforHVmember(db,providerid,memberid,patientid,policy_name=""):
    logger.loggerpms2.info("Enter getprocedurepriceplancodeformember = " + str(providerid) + " " + str(memberid) + " " + str(patientid) + " " + policy_name)
    procedurepriceplancode = "PREMWALKIN"  #default it to PREMWALKIN
    
    try:   
        
        # get HV region via Member's Region
        mems = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.patientmember.groupregion)
        regionid = int(common.getid(mems[0].groupregion)) if(len(mems) == 1) else 1
        regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select(db.groupregion.groupregion)
        regioncode = common.getstring(regions[0].groupregion) if(len(regions) == 1) else "ALL"
	
        
        # get patient's company
        pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.company,db.vw_memberpatientlist.hmoplan)
        companyid = int(common.getid(pats[0].company)) if(len(pats) == 1) else 0
        companys = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
        companycode = common.getstring(companys[0].company) if(len(companys) == 1) else "PREMWALKIN"

        #for backward compatibility determine procedurepriceplancode from member's plan at the time of registration
	def_planid = int(common.getid(pats[0].hmoplan)) if(len(pats) == 1) else 0  #this is the patient's previously assigned plan-typically at registration
	def_plans = db((db.hmoplan.id == def_planid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode)
	def_plancode = common.getstring(def_plans[0].hmoplancode) if(len(def_plans) == 1) else "PREMWALKIN"
	def_procedurepriceplancode = common.getstring(def_plans[0].procedurepriceplancode) if(len(def_plans) == 1) else "PREMWALKIN"

    
	#by default policy = companycode
	policy = companycode if policy_name == "" else policy_name 
	ppc = getprocedurepriceplancode(db, policy, None, regioncode, companycode)
	procedurepriceplancode = ppc["procedurepriceplancode"]
	procedurepriceplancode = def_procedurepriceplancode if(common.getstring(procedurepriceplancode) == "") else procedurepriceplancode

	
	logger.loggerpms2.info("getprocedurepriceplancodeformember 2 = " + common.getstring(regioncode) + " " + common.getstring(companycode) + " " + str(ppc["planid"]) + " " + common.getstring(ppc["plancode"]) + " " + common.getstring(procedurepriceplancode))
	
	#if policy_name == None, means you are adding procedure from web app
	#policy_name = None if(policy_name == "") else policy_name
        #if(policy_name == None):
	    #procedurepriceplancode = common.getstring(plans[0].procedurepriceplancode) if(len(plans) == 1) else "PREMWALKIN"
 	    #logger.loggerpms2.info("Enter getprocedurepriceplancodeformember 3 " + procedurepriceplancode)
        #else:
	    #policyname = plancode if(policy_name == "") else policy_name
            #d = getprocedurepriceplancode(db,policyname,None,regioncode,companycode,plancode)
            #procedurepriceplancode = d.get("procedurepriceplancode","PREMWALKIN")
	    #logger.loggerpms2.info("Enter getprocedurepriceplancodeformember 4 " + procedurepriceplancode)
    
    except Exception as e:
        raise Exception(str(e))
    
    
    
    return procedurepriceplancode



#policyproduct refers to insurance company's insurance product like Colgate2000, 399Plan, 499Plan, ABHICL399  etc.
def getprocedurepriceplancode(db,policy, providercode, regioncode, companycode,plancode=None):
    logger.loggerpms2.info("Enter getprocedurepriceplancode " + common.getstring(policy) + " "  + common.getstring(regioncode) + " " + common.getstring(companycode) + " ")
    
    planid = 0
    procedurepriceplancode = None
    
    try:
	if(policy == None):
	    #for backward compatibility
	    planprov = db((db.provider_region_plan.plancode == plancode)&\
			                       (db.provider_region_plan.companycode == companycode) &\
	                                       (db.provider_region_plan.regioncode == regioncode) &\
			                       (db.provider_region_plan.is_active == True)).select()    
	 
		
		
	    if(len(planprov) == 0):
		planprov = db((db.provider_region_plan.policy == policy) &\
		                                   (db.provider_region_plan.companycode == companycode) &\
		                                   (db.provider_region_plan.regioncode == "ALL") &\
		                                   (db.provider_region_plan.is_active == True)).select()    
	    
	    plancode = common.getstring(planprov[0].plancode) if(len(planprov) == 1) else None
	    plancode = None if(plancode == "") else plancode
	    
	    
	    h = db(db.hmoplan.hmoplancode == plancode).select()
	    planid = int(common.getid(h[0].id)) if(len(h) == 1) else 1
	    procedurepriceplancode = common.getstring(h[0].procedurepriceplancode) if(len(h) == 1) else None
	    procedurepriceplancode = None if(procedurepriceplancode == "") else procedurepriceplancode
	    
	    
	    
	
	else:
	    planprov = db((db.provider_region_plan.policy == policy) &\
			                       (db.provider_region_plan.companycode == companycode) &\
	                                       (db.provider_region_plan.regioncode == regioncode) &\
			                       (db.provider_region_plan.is_active == True)).select()    

	    
	 
	    #if no plans exists for the current region, then check for "ALL" other regions
	    if(len(planprov) == 0):
		planprov = db((db.provider_region_plan.policy == policy) &\
		                                   (db.provider_region_plan.companycode == companycode) &\
		                                   (db.provider_region_plan.regioncode == "ALL") &\
		                                   (db.provider_region_plan.is_active == True)).select()    
		
	    plancode = common.getstring(planprov[0].plancode) if(len(planprov) == 1) else None
	    plancode = None if(plancode == "") else plancode
	    
	    h = db(db.hmoplan.hmoplancode == plancode).select()
	    planid = int(common.getid(h[0].id)) if(len(h) == 1) else 1
	    procedurepriceplancode = common.getstring(h[0].procedurepriceplancode) if(len(h) == 1) else None
	    procedurepriceplancode = None if(procedurepriceplancode == "") else procedurepriceplancode
	    
	    
	    
	    logger.loggerpms2.info("Enter getprocedurepriceplancode 2 " + policy + " " + str(planid) + " " + common.getstring(plancode) + " " + common.getstring(procedurepriceplancode))
    except Exception as e:
	raise Exception(str(e))
	
    
    return dict(policy=policy,planid = planid, plancode = plancode, procedurepriceplancode=procedurepriceplancode)

	    