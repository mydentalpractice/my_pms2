from gluon import current
db = current.globalenv['db']
#


import json
import datetime
import time
from datetime import timedelta


from applications.my_pms2.modules import common

from applications.my_pms2.modules import logger


#returns the policy which the patient has subscribed to 
#{ providerid,memberid,patientid}
def getMemberPolicy(db,avars):

    logger.loggerpms2.info("Enter getMemberPolicy (Utils) ==> " + str(avars))

  
    rspobj={}

    try:

	#determine provider's region. If Provider is empty, then set provider to P0001 and its region
	p = db((db.provider.provider == "P0001") & (db.provider.is_active == True)).select(db.provider.id)
	defproviderid = int(common.getid(p[0].id)) if(len(p) >=1) else 0
	providerid = int(common.getid(common.getkeyvalue(avars,"providerid",str(defproviderid))))      

	#get region code
	provs = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.groupregion)
	regionid = int(common.getid(provs[0].groupregion)) if(len(provs) >= 1) else 1   
	regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select(db.groupregion.groupregion)
	regioncode = common.getstring(regions[0].groupregion) if(len(regions) >= 1) else "ALL"

	## get patient's company
	memberid = int(common.getid(common.getkeyvalue(avars,"memberid","0")))
	patientid = int(common.getid(common.getkeyvalue(avars,"memberid",memberid)))
	pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.company,db.vw_memberpatientlist.hmoplan)
	companyid = int(common.getid(pats[0].company)) if(len(pats) >= 1) else 0
	companys = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
	companycode = common.getstring(companys[0].company) if(len(companys) >= 1) else "WALKIN"

	##for backward compatibility determine procedurepriceplancode from member's plan at the time of registration
	hmoplanid = int(common.getid(pats[0].hmoplan)) if(len(pats) >= 1) else 0  #this is the patient's previously assigned plan-typically at registration
	hmoplans = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode)
	hmoplancode = common.getstring(hmoplans[0].hmoplancode) if(len(hmoplans) >= 1) else "PREMWALKIN"


       
	
	#get policy from provider-region-plan corr to companycode, regioncode and hmoplancode
	prp = db((db.provider_region_plan.companycode == companycode) &\
                 (db.provider_region_plan.regioncode == regioncode) &\
                 (db.provider_region_plan.plancode == hmoplancode) &\
                 (db.provider_region_plan.is_active == True)).select() 

	if(len(prp) == 0):
	    #region code = "ALL"
	    prp = db((db.provider_region_plan.companycode == companycode) &\
	             (db.provider_region_plan.regioncode == "ALL") &\
	             (db.provider_region_plan.plancode == hmoplancode) &\
	             (db.provider_region_plan.is_active == True)).select() 


	policy = prp[0].policy if(len(prp) >= 1) else "PREMWALKIN"
	policy = "PREMWALKIN" if((policy == None) | (policy == "")) else policy
	plancode = policy      
	ppc = prp[0].procedurepriceplancode if(len(prp) >= 1) else "PREM103"
	

	rspobj = {}
	rspobj["memberid"] = str(memberid)
	rspobj["providerid"] = str(providerid)

	rspobj["plancode"] = plancode
	rspobj["policy"] = policy
	rspobj["companycode"] = companycode
	rspobj["regioncode"] = regioncode
	rspobj["procedurepriceplancode"] = ppc      
	
	

    except Exception as e:
	mssg = "Get Member Policy (Utils) Exception:\n" + str(e)
	logger.loggerpms2.info(mssg)      
	excpobj = {}
	excpobj["result"] = "fail"
	excpobj["error_message"] = mssg
	return json.dumps(excpobj)     

    logger.loggerpms2.info("Exit getMemberPolicy (Utils)==> " + json.dumps(rspobj))
    return json.dumps(rspobj)


#THIS API is called to get plan details for the member
#based 
def getplandetailsformember(db,providerid,memberid,patientid):
    logger.loggerpms2.info("Enter getplandetailsformember = " + str(providerid) + " " + str(memberid) + " " + str(patientid))
    procedurepriceplancode = "PREMWALKIN"  #default it to PREMWALKIN
    rspobj = {}
    
    try:   
	
	#region - ALL for Patient
	regioncode = 'ALL'
        #provs = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.groupregion)
        #regionid = int(common.getid(provs[0].groupregion)) if(len(provs) == 1) else 1
        #regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select(db.groupregion.groupregion)
        #regioncode = common.getstring(regions[0].groupregion) if(len(regions) == 1) else "ALL"
	
        
        # get patient's company
        pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.company,db.vw_memberpatientlist.hmoplan)
        companyid = int(common.getid(pats[0].company)) if(len(pats) > 0) else 0
        companys = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company,db.company.name)
        companycode = common.getstring(companys[0].company) if(len(companys) > 0) else "PREMWALKIN"
	companyname = common.getstring(companys[0].name) if(len(companys) > 0) else "PREMWALKIN"
	
	#get PPC based on HMOPLAN assigned to the patient
	hmoplanid = int(common.getid(pats[0].hmoplan)) if(len(pats) > 0) else 0  #this is the patient's previously assigned plan-typically at registration
	hmoplans = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode,db.hmoplan.name)
	hmoplancode = common.getstring(hmoplans[0].hmoplancode) if(len(hmoplans) > 0) else "PREMWALKIN"
	planname = common.getstring(hmoplans[0].name) if(len(hmoplans) > 0) else "PREMWALKIN"
	
	r = db(
	    (db.provider_region_plan.companycode == companycode) &\
	    (db.provider_region_plan.plancode == hmoplancode) &\
	    ((db.provider_region_plan.regioncode == 'ALL')) &\
	    (db.provider_region_plan.is_active == True)).select()
	plancode = r[0].plancode if(len(r) > 0) else "PREMWALKIN"    
	procedurepriceplancode = r[0].procedurepriceplancode if(len(r) > 0) else "PREMWALKIN"

	rspobj = {}
	rspobj["result"] = "success"
	rspobj["error_message"] = ""
	rspobj["companyname"] = companyname
	rspobj["companycode"] = companycode
	rspobj["planid"] = str(hmoplanid)
	rspobj["plancode"] = hmoplancode
	rspobj["planname"] = planname
	rspobj["procedurepriceplancode"] = procedurepriceplancode

    except Exception as e:
	raise Exception(str(e))
    
    return json.dumps(rspobj)




#THIS API is called to determine the member's procedure price plan code based on 
#the provider's region, plan and policy
def getprocedurepriceplancodeformember(db,providerid,memberid,patientid,policy_name=""):
    logger.loggerpms2.info("Enter getprocedurepriceplancodeformember = " + str(providerid) + " " + str(memberid) + " " + str(patientid) + " " + policy_name)
    procedurepriceplancode = "PREMWALKIN"  #default it to PREMWALKIN
    
    try:   
	
	avars={}
	avars["providerid"] = providerid
	avars["memberid"] = memberid
	avars["patientid"] = patientid
	patobj = json.loads(getMemberPolicy(db,avars))
	
	plancode = common.getkeyvalue(patobj,"plancode","PREMWALKIN")
	policy = common.getkeyvalue(patobj,"policy","PREMWALKIN")
	procedurepriceplancode = common.getkeyvalue(patobj,"procedurepriceplancode","PREM103")
	regioncode = common.getkeyvalue(patobj,"regioncode","JAI")
	companycode = common.getkeyvalue(patobj,"companycode","MYDP")	
        
        # get providers region via city
        #provs = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.groupregion)
        #regionid = int(common.getid(provs[0].groupregion)) if(len(provs) == 1) else 1
        #regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select(db.groupregion.groupregion)
        #regioncode = common.getstring(regions[0].groupregion) if(len(regions) == 1) else "ALL"
	
        
        # get patient's company
        #pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.company,db.vw_memberpatientlist.hmoplan)
        #companyid = int(common.getid(pats[0].company)) if(len(pats) == 1) else 0
        #companys = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
        #companycode = common.getstring(companys[0].company) if(len(companys) == 1) else "PREMWALKIN"

	##for backward compatibility determine procedurepriceplancode from member's plan at the time of registration
	#hmoplanid = int(common.getid(pats[0].hmoplan)) if(len(pats) == 1) else 0  #this is the patient's previously assigned plan-typically at registration
	#hmoplans = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode)
	#hmoplancode = common.getstring(hmoplans[0].hmoplancode) if(len(hmoplans) == 1) else "PREMWALKIN"
	#r = db(
	    #(db.provider_region_plan.companycode == companycode) &\
	    #(db.provider_region_plan.plancode == hmoplancode) &\
	    #((db.provider_region_plan.regioncode == regioncode)|(db.provider_region_plan.regioncode == 'ALL'))&\
	    #(db.provider_region_plan.is_active == True)).select()
	#plancode = r[0].plancode if(len(r) == 1) else "PREMWALKIN"    
	#procedurepriceplancode = r[0].procedurepriceplancode if(len(r) == 1) else "PREMWALKIN"

        #for backward compatibility determine procedurepriceplancode from member's plan at the time of registration
	#def_planid = int(common.getid(pats[0].hmoplan)) if(len(pats) == 1) else 0  #this is the patient's previously assigned plan-typically at registration
	#def_plans = db((db.hmoplan.id == def_planid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode)
	#def_plancode = common.getstring(def_plans[0].hmoplancode) if(len(def_plans) == 1) else "PREMWALKIN"
	#def_procedurepriceplancode = common.getstring(def_plans[0].procedurepriceplancode) if(len(def_plans) == 1) else "PREMWALKIN"

    
	#by default policy = companycode
	#policy = companycode if policy_name == "" else policy_name 
	#ppc = getprocedurepriceplancode(db, policy, None, regioncode, companycode)
	#procedurepriceplancode = ppc["procedurepriceplancode"]
	#procedurepriceplancode = def_procedurepriceplancode if(common.getstring(procedurepriceplancode) == "") else procedurepriceplancode

	
	logger.loggerpms2.info("getprocedurepriceplancodeformember 2 = " + common.getstring(regioncode) + " " + common.getstring(companycode) + "  " + common.getstring(plancode) + " " + common.getstring(procedurepriceplancode))
	
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

	    