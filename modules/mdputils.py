from gluon import current
db = current.globalenv['db']



import json
import datetime
import time
from datetime import timedelta


from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger


def getprocedurepriceplancodeformember(db,providerid,memberid,patientid,policy_name=""):
    
    procedurepriceplancode = "PREMWALKIN"
    
    try:   
        
        # get providers region
        provs = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.groupregion)
        regionid = int(common.getid(provs[0].groupregion)) if(len(provs) == 1) else 1
        
        regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select(db.groupregion.groupregion)
        regioncode = common.getstring(regions[0].groupregion) if(len(regions) == 1) else "ALL"
        
        # get patient's company
        pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.company,db.vw_memberpatientlist.hmoplan)
        companyid = int(common.getid(pats[0].company)) if(len(pats) == 1) else 0
	planid = int(common.getid(pats[0].hmoplan)) if(len(pats) == 1) else 0
        
        companys = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
        companycode = common.getstring(companys[0].company) if(len(companys) == 1) else "PREMWALKIN"
        
	plans = db((db.hmoplan.id == planid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode)
	plancode = common.getstring(plans[0].hmoplancode) if(len(plans) == 1) else "PREMWALKIN"
        
        #by default companycode is policyproduct
        policyname = plancode  if(policy_name == "") else policy_name
        
        d = getprocedurepriceplancode(db,policyname,None,regioncode,companycode)
        
        
        procedurepriceplancode = d.get("procedurepriceplancode","PREMWALKIN")
    
    except Exception as e:
        raise Exception(str(e))
    
    
    
    
    return procedurepriceplancode

#policyproduct refers to insurance company's insurance product like Colgate2000, 399Plan, 499Plan, ABHICL399  etc.
def getprocedurepriceplancode(db,policyproduct, providercode, regioncode, companycode):

    plancode = None
    planid = 0
    procedurepriceplancode = None
    
    try:
	if(policyproduct == None):
	    #for backward compatibility with Religare COlgate 2000
	    provs = db((db.rlgprovider.providercode == providercode) & (db.rlgprovider.is_active == True)).select()
	    planid = int(common.getid(provs[0].planid)) if(len(provs) == 1) else 1
	    h = db((db.hmoplan.id == planid) & (db.hmoplan.is_active == True)).select()
	    plancode = common.getstring(h[0].hmoplancode) if(len(h) == 1) else None       
	    procedurepriceplancode = common.getstring(h[0].procedurepriceplancode) if(len(h) == 1) else None
	    procedurepriceplancode = None if(procedurepriceplancode == "") else procedurepriceplancode
	    
	
	else:
	    
	    planprov = db((db.provider_region_plan.policy == policyproduct) &\
			                       (db.provider_region_plan.companycode == companycode) &\
	                                       (db.provider_region_plan.regioncode == regioncode) &\
			                       (db.provider_region_plan.is_active == True)).select()    

	    
	 
	    #if no plans exists for the current region, then check for "ALL" other regions
	    if(len(planprov) == 0):
		planprov = db((db.provider_region_plan.policy == policyproduct) &\
		                                   (db.provider_region_plan.companycode == companycode) &\
		                                   (db.provider_region_plan.regioncode == "ALL") &\
		                                   (db.provider_region_plan.is_active == True)).select()    
		
	    plancode = common.getstring(planprov[0].plancode) if(len(planprov) == 1) else None
	    plancode = None if(plancode == "") else plancode
	    
	    h = db(db.hmoplan.hmoplancode == plancode).select()
	    planid = int(common.getid(h[0].id)) if(len(h) == 1) else 1
	    
	    
	    procedurepriceplancode = common.getstring(planprov[0].procedurepriceplancode) if(len(planprov) == 1) else None
	    procedurepriceplancode = None if(procedurepriceplancode == "") else procedurepriceplancode
	    
	    
    
    except Exception as e:
	raise Exception(str(e))
	
	
    return dict(planid = planid, plancode = plancode, procedurepriceplancode=procedurepriceplancode)

