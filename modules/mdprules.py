from gluon import current

import os
import json

import datetime
import time
from datetime import timedelta

from string import Template

from applications.my_pms2.modules import account
from applications.my_pms2.modules import common
from applications.my_pms2.modules import mdpbenefits

from applications.my_pms2.modules import logger


class Plan_Rules:
    def __init__(self,db):
        self.db = db
        return 
    
    #This API is called
    #a customer when a procedure is added to the treatment
    #{plancode, companycode, treatmentid,}
    def Get_Plan_Rules(self,avars):
        logger.loggerpms2.info("Enter Get_Plan_Rule " + json.dumps(avars))
        
        db = self.db
        rspobj = {}
        
        try:
            rspobj = json.loads(getattr(self, common.getkeyvalue(avars,"plan_code","premwalkin").lower())(avars))
        except Exception as e:
            mssg = "Get_Plan_Rule API Exception " + str(e)
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg
            
        mssg = json.dumps(rspobj)
        logger.loggerpms2.info("Exit Get Plan Rul " + mssg)
        return mssg    
   
    def vit_ap002(self,avars):
        logger.loggerpms2.info("Enter  AP002 " + json.dumps(avars))
        
        db = self.db
        rspobj = {}
        
        try:
            procedure_code = common.getkeyvalue(avars,"procedure_code","")
            plan_code = common.getkeyvalue(avars,"plan_code","")
            company_code = common.getkeyvalue(avars,"company_code","")
            member_id = int(common.getkeyvalue(avars,"member_id","0"))
            event = common.getkeyvalue(avars,"rule_event","")

            #apply pricing rules
            rules = None
            event_ALL = "all"
            event_OTHERS = "others"
            rules = db((db.rules.plan_code == plan_code) &\
                       (db.rules.company_code == company_code) &\
                       ((db.rules.rule_event == event)|(db.rules.rule_event == event_ALL)|(db.rules.rule_event == event_OTHERS)) &\
                       (db.rules.is_active == True)).select(db.rules.ALL, orderby=db.rules.rule_order)
            
            
            rspobj = {}
            rspobj["result"] = "fail"
            rspobj["error_message"] = "AP002 No Rule"
            rspobj["error_code"] = ""
            for rule in rules:
                if(rule.is_active == True):
                    rspobj = json.loads(getattr(self, (rule.rule_code).lower())(avars))
                    if(rspobj["result"] == "fail"):
                        break;
                   
                       
        except Exception as e:
            rspobj = {}
            mssg = " Exception AP002 API" + str(e)
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg
            
        mssg = json.dumps(rspobj)
        logger.loggerpms2.info("Exit AP002 " + mssg)
        return mssg
    
    #this rule is to be called when cashback has to be credited to a wallet for
    #a customer when a procedure is added to the treatment
    #{plancode, companycode, event=enroll, makepayment, completetreatment}
    def rule_voucher(self,avars):
        logger.loggerpms2.info("Enter Plan Rules - rule_voucher " + json.dumps(avars))
        db = self.db
        rspobj = {}
        
        try:    
            #get plan details from HMO Plan table
            plan_code = common.getkeyvalue(avars,"plan_code","PREMWALKIN")
            company_code = common.getkeyvalue(avars,"company_code","")
            event_code = common.getkeyvalue(avars,"event_code","enroll")
            region_code = common.getkeyvalue(avars,"region_code","ALL")
            
            plans = db((db.hmoplan.hmoplancode == plan_code) & (db.hmoplan.is_active == True)).select()
            
            for plan in plans:
                discount_amount = float(common.getvalue(plan.discount_amount))
                #call wallet API to credit MDP Wallet with discount_amount

            rspobj["result"] = "success"
            rspobj["error_message"] = ""
            rspobj["error_code"] = ""
        except Exception as e:
            mssg = " Exception Plan Rules rule_voucher" + str(e)
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg
            
        mssg = json.dumps(rspobj)
        logger.loggerpms2.info("Exit Plan_Rules rule_voucher" + mssg)
        return mssg
    
    #this rule is to be called when cashback has to be debited from MDP_Wallet
    #towards payment of a treatment cost. This is called at the time of payment
    #{plancode, companycode, event=enroll, makepayment, completetreatment}
    def rule_cashback(self,avars):
        logger.loggerpms2.info("Enter Plan Rules - rule_cashback " + json.dumps(avars))
        db = self.db
        rspobj = {}
        
        try:    
            #get plan details from HMO Plan table
            plan_code = common.getkeyvalue(avars,"plan_code","PREMWALKIN")
            company_code = common.getkeyvalue(avars,"company_code","")
            event_code = common.getkeyvalue(avars,"event_code","payment")
            region_code = common.getkeyvalue(avars,"region_code","ALL")
            treatment_id = int(common.id(avars,"treatment_id","0"))
            
            plans = db((db.hmoplan.hmoplancode == plan_code) & (db.hmoplan.is_active == True)).select()
            
            cashback = 0
            for plan in plans:
                walletamount = float(common.getvalue(plan.walletamount))  #this is the % value of the treatmentcost to be given as cashback
                tr = db((db.treatment.id == treatment_id) & (db.treatment.is_active == True)).select()
                tplanid = int(common.getid(tr[0].treatmentplan)) if(len(tr)==1) else 0
                paytm = account._calculatepayments(db, tplanid)
                #call wallet API to debit MDP Wallet with the cashback amount
                cashback = (walletamount/100 ) * paytm["totaltreatmentcost"]
                rspobj["casback"] = cashback
                rspobj["totaltreatmentcost"] = paytm["totaltreatmentcost"]

            rspobj["result"] = "success"
            rspobj["error_message"] = ""
            rspobj["error_code"] = ""
        except Exception as e:
            mssg = " Exception Plan Rules rule_cashback " + str(e)
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg
            
        mssg = json.dumps(rspobj)
        logger.loggerpms2.info("Exit Plan_Rules rule_voucher" + mssg)
        return mssg

    #this rule is to be called when MDP_Wallet & SUPER_Wallet & Wallet0 have to be 
    #created for a member with 0 amount
    #towards payment of a treatment cost. This is called at the time of payment
    #{plancode, companycode, event=createwallet, memberid}
    def rule_createwallet(self,avars):
        logger.loggerpms2.info("Enter Plan Rules - rule_createwallet " + json.dumps(avars))
        db = self.db
        rspobj = {}
        
        try:    
            member_id = int(common.getkeyvalue(avars,"member_id","0"))
            avars={}
            avars["member_id"] = member_id
            bnftobj = mdpbenefits.Benefit(db)
            rspobj = json.loads(bnftobj.create_wallet(avars))

        except Exception as e:
            mssg = " Exception Plan Rules rule_createwallet " + str(e)
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg
            
        mssg = json.dumps(rspobj)
        logger.loggerpms2.info("Exit Plan_Rules rule_createwaller" + mssg)
        return mssg

    #this rule is called to credir a member's wallet with the cashback amount
    #this rule is called at tjhe 
    def rule_creditwallet(self,avars):
        logger.loggerpms2.info("Enter Plan Rules - rule_creditwallet " + json.dumps(avars))
        db = self.db
        rspobj = {}
        
        try:    
            #get plan details from HMO Plan table
            plan_code = common.getkeyvalue(avars,"plan_code","PREMWALKIN")
            company_code = common.getkeyvalue(avars,"company_code","")
            member_id = int(common.getkeyvalue(avars,"member_id","0"))
            
            plans = db((db.hmoplan.hmoplancode == plan_code) & (db.hmoplan.company_code == company_code) & (db.hmoplan.is_active == True)).select()
            
            discount_amount = float(common.getvalue(plans[0].discount_amount)) if(len(plans) == 1) else 0
            
            avars={}
            avars["member_id"] = member_id
            avars["wallet_type"] = "MDP_Wallet"
            avars["walletamount"] = discount_amount # this is the discount voucher to be credited to the wallet
            bnftobj = mdpbenefits.Benefit(db)
            rspobj = json.loads(bnftobj.credit_wallet(avars))
            
        except Exception as e:
            mssg = " Exception Plan Rules rule_cashback " + str(e)
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg
            
        mssg = json.dumps(rspobj)
        logger.loggerpms2.info("Exit Plan_Rules rule_voucher" + mssg)
        return mssg
        

class Pricing:
    def __init__(self,db):
        self.db = db
        return 
    
    
    # This API will return Pricing of a Procedure based on the following
    # Procedure Code, Region, Plan, Member Treatment, Plan Pricing Rules
    def Get_Procedure_Fees(self,avars):
        logger.loggerpms2.info("Enter Get_Procedure_Fees " + json.dumps(avars))
        
        db = self.db
        rspobj = {}
        
        try:
            rspobj = json.loads(getattr(self, common.getkeyvalue(avars,"plan_code","premwalkin").lower())(avars))
        except Exception as e:
            mssg = "Get_Procedure_Fees API Exception " + str(e)
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg
            
        mssg = json.dumps(rspobj)
        logger.loggerpms2.info("Exit Get Procedure Fees " + mssg)
        return mssg
    
    def rpip99(self,avars):
        logger.loggerpms2.info("Enter  RPIP99 " + json.dumps(avars))
        
        db = self.db
        rspobj = {}
        
        try:
            procedure_code = common.getkeyvalue(avars,"procedure_code","")
            plan_code = common.getkeyvalue(avars,"plan_code","")
            company_code = common.getkeyvalue(avars,"company_code","")

            #apply pricing rules
            rules = None
            procedure_ALL = "all"
            procedure_OTHERS = "others"
            rules = db((db.rules.plan_code == plan_code) &\
                       (db.rules.company_code == company_code) &\
                       ((db.rules.procedure_code == procedure_code)|(db.rules.procedure_code == procedure_ALL)|(db.rules.procedure_code == procedure_OTHERS)) &\
                       (db.rules.is_active == True)).select(db.rules.ALL, orderby=db.rules.rule_order)
            
            
            rspobj = {}
            rspobj["result"] = "fail"
            rspobj["error_message"] = "RPIP99 No Rule"
            rspobj["error_code"] = ""
            for rule in rules:
                if(rule.is_active == True):
                    rspobj = json.loads(getattr(self, (rule.rule_code).lower())(avars))
                    if(rspobj["result"] == "fail"):
                        break;
                    if(rspobj["active"] == False):
                        break;
                       
        except Exception as e:
            rspobj = {}
            mssg = " Exception RPIP99 API" + str(e)
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg
            
        mssg = json.dumps(rspobj)
        logger.loggerpms2.info("Exit rpip99 " + mssg)
        return mssg


    def rpip599(self,avars):
        logger.loggerpms2.info("Enter  RPIP599 " + json.dumps(avars))
        
        db = self.db
        rspobj = {}
        
        try:
            procedure_code = common.getkeyvalue(avars,"procedure_code","")
            plan_code = common.getkeyvalue(avars,"plan_code","")
            company_code = common.getkeyvalue(avars,"company_code","")

            #apply pricing rules
            rules = None
            procedure_ALL = "all"
            procedure_OTHERS = "others"
            rules = db((db.rules.plan_code == plan_code) &\
                       (db.rules.company_code == company_code) &\
                       ((db.rules.procedure_code == procedure_code)|(db.rules.procedure_code == procedure_ALL)|(db.rules.procedure_code == procedure_OTHERS)) &\
                       (db.rules.is_active == True)).select(db.rules.ALL, orderby=db.rules.rule_order)
            
            
            rspobj = {}
            rspobj["result"] = "fail"
            rspobj["error_message"] = "RPIP599 No Rule"
            rspobj["error_code"] = ""
            for rule in rules:
                if(rule.is_active == True):
                    rspobj = json.loads(getattr(self, (rule.rule_code).lower())(avars))
                    if(rspobj["result"] == "fail"):
                        break;
                    if(rspobj["active"] == False):
                        break;
                       
        except Exception as e:
            rspobj = {}
            mssg = " Exception RPIP599 API" + str(e)
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg
            
        mssg = json.dumps(rspobj)
        logger.loggerpms2.info("Exit rpip599 " + mssg)
        return mssg
    
    
    #This is a generic rule for all procedures for all plans for all procedurepriceplancodes
    #Bring all the fields
    def rule0(self,avars):
        logger.loggerpms2.info("Enter RPIP599 Rule 0 API " + json.dumps(avars))
        
        db = self.db
        rspobj = {}
        
        try:
            procedure_code = common.getkeyvalue(avars,"procedure_code","")
            region_code = common.getkeyvalue(avars,"region_code","")
            plan_code = common.getkeyvalue(avars,"plan_code","")
            company_code = common.getkeyvalue(avars,"company_code","")
            treatment_id = int(common.getid(common.getkeyvalue(avars,"treatment_id",0)))
        
            #check whether the plan is valid for this member or not
            tr = db((db.vw_treatmentlist_fast.id == treatment_id) & (db.vw_treatmentlist_fast.is_active == True)).select(db.vw_treatmentlist_fast.memberid,db.vw_treatmentlist_fast.startdate)
            
          
            memberid = int(common.getid(tr[0].memberid)) if(len(tr) == 1)  else 0
            members = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.patientmember.premstartdt,db.patientmember.premenddt)
            premenddt = members[0].premenddt if(len(members) == 1) else common.getdatefromstring("01/01/1900","%d/%m/%Y")
            premstartdt = members[0].premstartdt if(len(members) == 1) else common.getdatefromstring("01/01/1900","%d/%m/%Y")
            tr_startdate = tr[0].startdate if(len(tr) == 1) else common.getdatefromstring("01/01/2200","%d/%m/%Y")
            
            is_valid = True
            if((tr_startdate >= premstartdt) & (tr_startdate <= premenddt)):
                is_valid = True
            else:
                is_valid = False
            
            
            
            
            prp = db((db.provider_region_plan.companycode == company_code) & \
                     (db.provider_region_plan.regioncode == region_code) & \
                     ((db.provider_region_plan.policy == plan_code)|(db.provider_region_plan.plancode == plan_code))).select()
        
            ppc = prp[0].procedurepriceplancode if(len(prp) == 1) else "PREMWALKIN"
        
            ppp = db((db.procedurepriceplan.procedurecode == procedure_code) &\
                     (db.procedurepriceplan.procedurepriceplancode == ppc)  &\
                     (db.procedurepriceplan.is_active == True)).select()
        
            #ppp JSON Object
            rspobj["active"] = True 
            rspobj["result"] = "success"
            rspobj["error_message"] = ""
            rspobj["error_code"] = ""
            if(len(ppp) == 1):
                rspobj["ucrfee"] = float(common.getvalue(ppp[0].ucrfee))
                rspobj["procedurefee"] = float(common.getvalue(ppp[0].procedurefee))
                rspobj["copay"] = float(common.getvalue(ppp[0].copay))
                rspobj["inspays"] = float(common.getvalue(ppp[0].inspays))
                rspobj["companypays"] = float(common.getvalue(ppp[0].companypays))
                rspobj["walletamount"] = float(common.getvalue(ppp[0].walletamount))
                rspobj["discount_amount"] = float(common.getvalue(ppp[0].discount_amount))
                rspobj["is_free"] = common.getboolean(ppp[0].is_free)
                rspobj["voucher_code"] = common.getstring(ppp[0].voucher_code)
                rspobj["active"] = is_valid 
                rspobj["remarks"] = common.getstring(ppp[0].remarks)
                c = db(db.company.company == company_code).select()
                rspobj["authorizationrequired"] = False if (len(c) <= 0) else common.getboolean(c[0].authorizationrequired)
                
        except Exception as e:
            rspobj = {}
            mssg = "RPIP599 Rule 0 API Exception " + str(e)
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg
            
        mssg = json.dumps(rspobj)
        logger.loggerpms2.info("Exit Pricing rule0 " + mssg)
        return mssg
    
    #This rule - Consultation can only be used once in every four months - three in total.
    def rpip599_consultancy_validity(self,avars):
        logger.loggerpms2.info("Enter RPIP599 Rule 0 API " + json.dumps(avars))
        
        db = self.db
        rspobj = {}
        
        try:
            procedure_code = common.getkeyvalue(avars,"procedure_code","")
            region_code = common.getkeyvalue(avars,"region_code","")
            plan_code = common.getkeyvalue(avars,"plan_code","")
            company_code = common.getkeyvalue(avars,"company_code","")
            treatment_id = int(common.getid(common.getkeyvalue(avars,"treatment_id",0)))
            
            is_valid = True
            #number of times this procedure is used
            trp = db((db.vw_treatmentprocedure.treatmentid == treatment_id) &\
                     (db.vw_treatmentprocedure.procedurecode == procedure_code) &\
                     (db.vw_treatmentprocedure.is_active == True)).select(db.vw_treatmentprocedure.ALL, orderby=~db.vw_treatmentprocedure.id)
            
            is_valid3 = True if(len(trp) >=3) else False #already used three times
            is_valid0 = True if(len(trp) ==0) else False #Not used once
            
            
            #last treatment date when this G0101 was added.
            treatmentdate = trp[0].treatmentdate if((len(trp) > 0) & (is_valid == True)) else common.getISTCurrentLocatTime().date()
            currentdate = common.getISTFormatCurrentLocatTime().date()
            #if current date > last treatmentdate + 4 months, then G0101 can be added, else not.
            #this is appx because we are not differentiating about 28,29,30,31 days month
            months4 = timedelta(days=4*30)
            day  = timedelta(days = 1)
            nextdateallowed = (treatmentdate + months4) - day  
            is_validn = True if(currentdate >= nextdateallowed) else False
            
            if(is_valid3 == True):  #3 times limit reached
                is_valid = False
            elif (is_valid0 == True): #0 times used
                is_valid = True
            elif (is_validn == True): # 4 months period passed
                is_valid = True
            else:
                is_valid = False
            
            
            prp = db((db.provider_region_plan.companycode == company_code) & \
                     (db.provider_region_plan.regioncode == region_code) & \
                     ((db.provider_region_plan.policy == plan_code)|(db.provider_region_plan.plancode == plan_code))).select()
        
            ppc = prp[0].procedurepriceplancode if(len(prp) == 1) else "PREMWALKIN"
        
            ppp = db((db.procedurepriceplan.procedurecode == procedure_code) &\
                     (db.procedurepriceplan.procedurepriceplancode == ppc)  &\
                     (db.procedurepriceplan.is_active == True)).select()
        
            #ppp JSON Object
            rspobj["active"] = True 
            rspobj["result"] = "success"
            rspobj["error_message"] = ""
            rspobj["error_code"] = ""
            if(len(ppp) == 1):
                rspobj["ucrfee"] = float(common.getvalue(ppp[0].ucrfee))
                rspobj["procedurefee"] = float(common.getvalue(ppp[0].procedurefee))
                rspobj["copay"] = float(common.getvalue(ppp[0].copay))
                rspobj["inspays"] = float(common.getvalue(ppp[0].inspays))
                rspobj["companypays"] = float(common.getvalue(ppp[0].companypays))
                rspobj["walletamount"] = float(common.getvalue(ppp[0].walletamount))
                rspobj["discount_amount"] = float(common.getvalue(ppp[0].discount_amount))
                rspobj["is_free"] = common.getboolean(ppp[0].is_free)
                rspobj["voucher_code"] = common.getstring(ppp[0].voucher_code)
                rspobj["active"] = is_valid 
                rspobj["remarks"] = common.getstring(ppp[0].remarks)
                c = db(db.company.company == company_code).select()
                rspobj["authorizationrequired"] = False if (len(c) <= 0) else common.getboolean(c[0].authorizationrequired)
                
        except Exception as e:
            rspobj = {}
            mssg = "RPIP599 Rule 0 API Exception " + str(e)
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg
            
        mssg = json.dumps(rspobj)
        logger.loggerpms2.info("Exit Pricing rpip599_consultancy_validity "  + mssg)
        return mssg
    
    #This rule - Consultation can only be used once in every four months - three in total.
    def rpip99_consultancy_validity(self,avars):
        logger.loggerpms2.info("Enter RPIP599 Rule 0 API " + json.dumps(avars))
        
        db = self.db
        rspobj = {}
        
        try:
            procedure_code = common.getkeyvalue(avars,"procedure_code","")
            region_code = common.getkeyvalue(avars,"region_code","")
            plan_code = common.getkeyvalue(avars,"plan_code","")
            company_code = common.getkeyvalue(avars,"company_code","")
            treatment_id = int(common.getid(common.getkeyvalue(avars,"treatment_id",0)))
            
            is_valid = True
            #number of times this procedure is used
            trp = db((db.vw_treatmentprocedure.treatmentid == treatment_id) &\
                     (db.vw_treatmentprocedure.procedurecode == procedure_code) &\
                     (db.vw_treatmentprocedure.is_active == True)).select(db.vw_treatmentprocedure.ALL, orderby=~db.vw_treatmentprocedure.id)
            
            is_valid3 = True if(len(trp) >=3) else False #already used three times
            is_valid0 = True if(len(trp) ==0) else False #Not used once
            
            
            #last treatment date when this G0101 was added.
            treatmentdate = trp[0].treatmentdate if((len(trp) > 0) & (is_valid == True)) else common.getISTCurrentLocatTime().date()
            currentdate = common.getISTFormatCurrentLocatTime().date()
            #if current date > last treatmentdate + 4 months, then G0101 can be added, else not.
            #this is appx because we are not differentiating about 28,29,30,31 days month
            months4 = timedelta(days=4*30)
            day  = timedelta(days = 1)
            nextdateallowed = (treatmentdate + months4) - day  
            is_validn = True if(currentdate >= nextdateallowed) else False
            
            if(is_valid3 == True):  #3 times limit reached
                is_valid = False
            elif (is_valid0 == True): #0 times used
                is_valid = True
            elif (is_validn == True): # 4 months period passed
                is_valid = True
            else:
                is_valid = False
            
            
            prp = db((db.provider_region_plan.companycode == company_code) & \
                     (db.provider_region_plan.regioncode == region_code) & \
                     ((db.provider_region_plan.policy == plan_code)|(db.provider_region_plan.plancode == plan_code))).select()
        
            ppc = prp[0].procedurepriceplancode if(len(prp) == 1) else "PREMWALKIN"
        
            ppp = db((db.procedurepriceplan.procedurecode == procedure_code) &\
                     (db.procedurepriceplan.procedurepriceplancode == ppc)  &\
                     (db.procedurepriceplan.is_active == True)).select()
        
            #ppp JSON Object
            rspobj["active"] = True 
            rspobj["result"] = "success"
            rspobj["error_message"] = ""
            rspobj["error_code"] = ""
            if(len(ppp) == 1):
                rspobj["ucrfee"] = float(common.getvalue(ppp[0].ucrfee))
                rspobj["procedurefee"] = float(common.getvalue(ppp[0].procedurefee))
                rspobj["copay"] = float(common.getvalue(ppp[0].copay))
                rspobj["inspays"] = float(common.getvalue(ppp[0].inspays))
                rspobj["companypays"] = float(common.getvalue(ppp[0].companypays))
                rspobj["walletamount"] = float(common.getvalue(ppp[0].walletamount))
                rspobj["discount_amount"] = float(common.getvalue(ppp[0].discount_amount))
                rspobj["is_free"] = common.getboolean(ppp[0].is_free)
                rspobj["voucher_code"] = common.getstring(ppp[0].voucher_code)
                rspobj["active"] = is_valid 
                rspobj["remarks"] = common.getstring(ppp[0].remarks)
                c = db(db.company.company == company_code).select()
                rspobj["authorizationrequired"] = False if (len(c) <= 0) else common.getboolean(c[0].authorizationrequired)
                
        except Exception as e:
            rspobj = {}
            mssg = "RPIP599 Rule 0 API Exception " + str(e)
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg
            
        mssg = json.dumps(rspobj)
        logger.loggerpms2.info("Exit Pricing rpip99_consultancy_validity " + mssg)
        return mssg
    
    def rpip599_rule1(self,avars):
        logger.loggerpms2.info("Enter RPIP599 Rule 1 API " + json.dumps(avars))
        
        db = self.db
        rspobj = {}
        
        try:
            procedure_code = common.getkeyvalue(avars,"procedure_code","")
            region_code = common.getkeyvalue(avars,"region_code","")
            plan_code = common.getkeyvalue(avars,"plan_code","")
            company_code = common.getkeyvalue(avars,"company_code","")
            treatment_id = int(common.getid(common.getkeyvalue(avars,"treatment_id",0)))
        
            prp = db((db.provider_region_plan.companycode == company_code) & \
                     (db.provider_region_plan.regioncode == region_code) & \
                     (db.provider_region_plan.policy == plan_code)).select()
        
            ppc = prp[0].procedurepriceplancode if(len(prp) == 1) else "PREMWALKIN"
        
            ppp = db((db.procedurepriceplan.procedurecode == procedure_code) &\
                     (db.procedurepriceplan.procedurepriceplancode == ppc)  &\
                     (db.procedurepriceplan.is_active == True)).select()
        
            #ppp JSON Object
            rspobj["active"] = True 
            rspobj["result"] = "success"
            rspobj["error_message"] = ""
            rspobj["error_code"] = ""
            if(len(ppp) == 1):
                rspobj["ucrfee"] = float(common.getvalue(ppp[0].ucrfee))
                rspobj["procedurefee"] = float(common.getvalue(ppp[0].procedurefee))
                rspobj["copay"] = float(common.getvalue(ppp[0].copay))
                rspobj["inspays"] = float(common.getvalue(ppp[0].inspays))
                rspobj["companypays"] = float(common.getvalue(ppp[0].companypays))
                rspobj["walletamount"] = float(common.getvalue(ppp[0].walletamount))
                rspobj["discount_amount"] = float(common.getvalue(ppp[0].discount_amount))
                rspobj["is_free"] = common.getboolean(ppp[0].is_free)
                rspobj["voucher_code"] = ppp[0].voucher_code
                rspobj["active"] = True 
                rspobj["remarks"] = common.getstring(ppp[0].remarks)
                
        except Exception as e:
            rspobj = {}
            mssg = "RPIP599 Rule 1 API Exception " + str(e)
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg
            
        mssg = json.dumps(rspobj)
        logger.loggerpms2.info("Exit Pricing rpip599_rule1 " + mssg)
        return mssg
    


    def Template(self,avars):
        logger.loggerpms2.info("Enter  " + json.dumps(avars))
        
        db = self.db
        rspobj = {}
        
        try:
            
    
            rspobj["result"] = "success"
            rspobj["error_message"] = ""
            rspobj["error_code"] = ""
        except Exception as e:
            mssg = " Exception " + str(e)
            rspobj["result"] = "fail"
            rspobj["error_message"] = mssg
            
        mssg = json.dumps(rspobj)
        logger.loggerpms2.info(mssg)
        return mssg
    

    