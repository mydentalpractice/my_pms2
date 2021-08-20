from gluon import current
import os
import json
import datetime
import time
from datetime import timedelta

from applications.my_pms2.modules import common
from applications.my_pms2.modules import logger

class Benefit:
  def __init__(self,db):
    self.db = db
    return 
  
  
  
  #this method maps member to benefit
  def map_member_benefit(self,avars):
    logger.loggerpms2.info("Enter map_member_benefits " + json.dumps(avars))
    db = self.db
   
   
    try:
      
      
      policy = common.getkeyvalue(avars,"plan","")
      r = db((db.company.company == policy) & (db.company.is_active == True)).select()
      planid = int(common.getid(r[0].id)) if(len(r)>0) else 0
      
      memberid = int(common.getkeyvalue(avars,"memberid","0"))
      p = db((db.benefit_master.benefit_code == policy) & (db.benefit_master.is_active == True)).select()
      benefit_master_id = int(common.getid(p[0].id)) if(len(p)>0) else 0
      db.benefit_master_x_member.insert(\
        member_id = memberid,
        benefit_master_id = benefit_master_id,
        plan_code = policy,
        plan_id = planid
      
      )

      rspobj = {}
      rspobj["result"] = "success"
      rspobj["error_message"] = ""

    except Exception as e:
      mssg = "Map Member Benefits  Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)     
    
    logger.loggerpms2.info("Exit map_member_benefits " + json.dumps(avars))
    
    return json.dumps(rspobj)
  
    
  def get_benefits(self,avars):
    logger.loggerpms2.info("Enter get_benefits " + json.dumps(avars))
    db = self.db
    rspobj = {}
    
    try:

      policy = common.getkeyvalue(avars,"plan","")
      providerid = int(common.getid(common.getkeyvalue(avars,"providerid","0")))
      prov = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.city)
      logger.loggerpms2.info("Enter get_benefits 1" + str(providerid))
      
      #region regiond code      
      city = prov[0].city if(len(prov) != 0) else "Jaipur"
      regionid = common.getregionidfromcity(db,city)
      regioncode =  common.getregioncodefromcity(db,city)         
      logger.loggerpms2.info("Enter get_benefits 2" + str(regionid) + " " +regioncode)
     
      #get company code
      memberid = int(common.getkeyvalue(avars,"memberid","0"))
      members = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.patientmember.company,db.patientmember.hmoplan)

      companyid = int(common.getid(members[0].company) if (len(members) == 1) else "0")
      c = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
      companycode = c[0].company if (len(c) ==1) else ""
      logger.loggerpms2.info("Enter get_benefits 3" + str(companyid) + " " + companycode + " " + str(len(c)))
      
      #get hmoplan code
      hmoplanid = int(common.getid(members[0].hmoplan) if (len(members) == 1) else "0")  #members hmoplan assigned
      h = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.is_active == True)).select()    
      hmoplancode = h[0].hmoplancode if(len(h) == 1) else "PREMWALKIN"
      logger.loggerpms2.info("Enter get_benefits 4" + str(hmoplanid) + " " +hmoplancode)
      
      #get policy from provider-region-plan corr to companycode, regioncode and hmoplancode
      prp = db((db.provider_region_plan.companycode == companycode) &\
                     (db.provider_region_plan.regioncode == regioncode) &\
                     (db.provider_region_plan.plancode == hmoplancode) &\
                     (db.provider_region_plan.is_active == True)).select() 
      
      
      policy = prp[0].policy if(len(prp) == 1) else "PREMWALKIN"  #get policy corr.
      
 
      
      if(policy == "RPIP599"):
        avars["plan"] = policy
        rspobj = json.loads(self.RPIP599(avars))
      else:
        mssg = "Get Benefits:Invalid benefit Policy"
        rspobj = {}
        rspobj["result"] = "success"
        rspobj["error_message"] = mssg
        rspobj["redeem_code"] = "BNFT_INVALID"
        rspobj["redeem_value"] = 0
        rspobj["redeem_date"] = common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")
        rspobj["redeem_message"] = common.getmessage(db,"BNFT_INVALID")
        rspobj["memberid"] = str(memberid)
        rspobj["plan"] = policy
     
        rspobj["total_redeemed_benefits"] = 0
        rspobj["benefit_code"] = ""
        rspobj["benefit_name"] = ""
        rspobj["benefit_value"] = str(0)
        rspobj["discount_amount"] = str(0)
   
        
      
    except Exception as e:
      mssg = "Get Bnefits  Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)     
    
    logger.loggerpms2.info("Exit get_benefits " + json.dumps(rspobj))
    
    return json.dumps(rspobj)
  

  def RPIP599Success(self,avars):
    
    logger.loggerpms2.info("Enter RPIP599 Success ==>>" + str(avars))
    
    db = self.db
    benefit_obj = {}
    auth = current.auth
    
    
    try:
      memberid = int(common.getkeyvalue(avars,"memberid","0"))
      treatmentid = int(common.getkeyvalue(avars,"treatmentid","0"))
      policy = common.getkeyvalue(avars,"plan","")
      c = db((db.company.company == policy) & (db.company.is_active == True)).select(db.company.id)
      companyid = c[0].id if (len(c) ==1) else ""
      
      discount_amount = float(common.getkeyvalue(avars,"discount_amount","0"))      
      balance_benefit_amount = float(common.getkeyvalue(avars,"balance_benefit_amount","0"))      
      last_redeemed_amount = float(common.getkeyvalue(avars,"last_redeemed_amount","0"))      
      benefit_member_id = 0
      
    
      #update benefit_member table on successful payment 
      if(discount_amount > 0):
        benefit_member_id = db.benefit_member.insert(\
          
          member_id = memberid,
          plan_id = companyid,
          plan_code = policy,
          redeem_date = common.getISTFormatCurrentLocatTime(),
          redeem_amount = discount_amount,
          last_redeemed_date=common.getISTFormatCurrentLocatTime(),
          last_redeemed_amount=last_redeemed_amount,
          balance_benefit_amount=balance_benefit_amount,
          is_active = True,
          created_on = common.getISTFormatCurrentLocatTime(),
          created_by = 1 if(auth.user == None) else auth.user.id,
          modified_on = common.getISTFormatCurrentLocatTime(),
          modified_by =  1 if(auth.user == None) else auth.user.id    
      )      
      #update benefit_x_members table
           
      if(benefit_member_id > 0):
        db.benefit_member_x_member.update_or_insert(db.benefit_member_x_member.member_id == memberid,
                                                    member_id = memberid,
                                                    benefit_member_id = benefit_member_id
                                                    )
         
       
        
      rspobj = {}
      rspobj["result"] = "success"
      rspobj["error_message"] = ""
      rspobj["plan"] = policy
      rspobj["memberid"]=memberid
      rspobj["treatmentid"]=treatmentid
      rspobj["benefit_member_id"]  = str(benefit_member_id)
      rspobj["discount_amount"] = str(discount_amount)
      
    except Exception as e:
      mssg = "RPIP599 Success Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)     
  
    logger.loggerpms2.info("Exit from RPIP599 Success " + json.dumps(rspobj))
    return json.dumps(rspobj)

  def RPIP599Failure(self,avars):
    
    logger.loggerpms2.info("Enter RPIP599 Failure ==>>" + str(avars))
    
    db = self.db
    benefit_obj = {}
    auth = current.auth
    
    
    try:
      memberid = int(common.getkeyvalue(avars,"memberid","0"))
      treatmentid = int(common.getkeyvalue(avars,"treatmentid","0"))
      policy = common.getkeyvalue(avars,"plan","")
      c = db((db.company.company == policy) & (db.company.is_active == True)).select(db.company.id)
      companyid = c[0].id if (len(c) ==1) else ""
      
      discount_amount = float(common.getkeyvalue(avars,"discount_amount","0"))      
      balance_benefit_amount = float(common.getkeyvalue(avars,"balance_benefit_amount","0"))      
      last_redeemed_amount = float(common.getkeyvalue(avars,"last_redeemed_amount","0"))      
      benefit_member_id = 0
       
      #Reset companypays = 0 in treatment & treatment plans
      t = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
      tplanid = int(common.getid(t[0].treatmentplan)) if(len(t) > 0) else 0
      db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).update(companypay=0)
      db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).update(totalcompanypays=0)
    
     
      
      rsppobj = {}
      rsppobj["result"] = "success"
      rsppobj["error_message"] = ""
      rspobj["plan"] = policy
      rspobj["memberid"]=memberid
      treatmentid["memberid"]=treatmentid
      rspobj["benefit_member_id"]  = str(benefit_member_id)
      rspobj["discount_amount"] = str(discount_amount)
      
    except Exception as e:
      mssg = "RPIP599 Success Failure:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)     
  
    logger.loggerpms2.info("Exit from RPIP599 Failure " + json.dumps(rspobj))
    return json.dumps(rspobj)

  
  def benefit_success(self, avars):
    logger.loggerpms2.info("Enter Benefit Success " + json.dumps(avars))
    
    db = self.db
    benefit_obj = {}
    auth = current.auth    
    try:
      policy = common.getkeyvalue(avars,"plan","")    
      if(policy == "RPIP599"):
        rspobj = json.loads(self.RPIP599Success(avars))
      else:
        rspobj = {}
        rspobj["result"] = "success"
        rspobj["error_message"] = ""
        rspobj["redeen_code"] = "BNFT_INVALID"
        rspobj["redeem_value"] = 0
        rspobj["redeem_date"] = common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")
        rspobj["redeem_message"] = common.getmessage(db,"BNFT_INVALID")          
        
    except Exception as e:
        mssg = "Bnefits Success Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)     
      
    logger.loggerpms2.info("Enter Benefit Success " + json.dumps(avars))
    return json.dumps(rspobj)    
    
  def benefit_failure(self, avars):
      logger.loggerpms2.info("Enter Benefit Failure " + json.dumps(avars))
      
      db = self.db
      benefit_obj = {}
      auth = current.auth    
      try:
        policy = common.getkeyvalue(avars,"plan","")    
        if(policy == "RPIP599"):
          rspobj = json.loads(self.RPIP599Failure(avars))
        else:
          rspobj = {}
          rspobj["result"] = "success"
          rspobj["error_message"] = ""
          rspobj["redeen_code"] = "BNFT_INVALID"
          rspobj["redeem_value"] = 0
          rspobj["redeem_date"] = common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")
          rspobj["redeem_message"] = common.getmessage(db,"BNFT_INVALID")          
          
      except Exception as e:
          mssg = "Bnefits Success Exception:\n" + str(e)
          logger.loggerpms2.info(mssg)      
          excpobj = {}
          excpobj["result"] = "fail"
          excpobj["error_message"] = mssg
          return json.dumps(excpobj)     
        
      logger.loggerpms2.info("Enter Benefit Success " + json.dumps(avars))
      return json.dumps(rspobj)     
    
  def RPIP599(self, avars):
    
    logger.loggerpms2.info("Enter RPIP599 ==>>" + str(avars))
    
    db = self.db
    benefit_obj = {}
    auth = current.auth
    
    policy = common.getkeyvalue(avars,"plan","")   #this is the plan passed from get_benefits
    logger.loggerpms2.info("Enter RPIP599 1==>>" + policy)
      
    ##return rspobj
    #benefit_obj = {}
    #benefit_obj["result"] = "success"
    #benefit_obj["error_message"] = ""
    #benefit_obj["memberid"] = str(19449)
    #benefit_obj["policy"] = policy
    #benefit_obj["total_redeemed_benefits"] = "0"
    #benefit_obj["benefit_code"] = "RPIP599"
    #benefit_obj["benefit_name"] = "pLAN 599"
    #benefit_obj["benefit_value"] = "5000"
    #benefit_obj["benefit_start_date"] = "01/07/2021"
    #benefit_obj["benefit_end_date"] = "30/06/2022"
    #benefit_obj["redeen_code"] = "BNFT_OK"
    #benefit_obj["discount_amount"] = "500"
    #benefit_obj["discount_date"] = common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")
    #benefit_obj["discount_message"] = common.getmessage(db,"BNFT_OK")
    #return json.dumps(benefit_obj)          
    

    
    try:
    
      
      #get company from member (if member has purchased this RIP599)
      memberid = int(common.getkeyvalue(avars,"memberid","0"))
      members = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.patientmember.company)
      companyid = common.getid(members[0].company) if (len(members) == 1) else "0"
      c = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
      companycode = c[0].company if (len(c) ==1) else ""
      logger.loggerpms2.info("Enter RPIP599 2==>>" + str(len(members)) + " " + str(companyid) + " " + companycode)
      
      
      #get benefit_master
      #Table: benefit_master_x_member
      #Columns:
      #id int(11) AI PK 
      #member_id int(11) 
      #plan_id int(11) 
      #benefit_master_id int(11) 
      #plan_code varch      
      bms = db((db.benefit_master_x_member.member_id == memberid) & (db.benefit_master_x_member.plan_code == policy) &\
             (db.benefit_master.is_valid == True) & (db.benefit_master.is_active == True)).select(db.benefit_master.ALL,\
                                                                                                  left=db.benefit_master.on(db.benefit_master.id == db.benefit_master_x_member.benefit_master_id))
      bmid = bms[0].id if(len(bms)==1) else 0
      logger.loggerpms2.info("Enter RPIP599 3==>>" + str(len(bms)))
      
    

      #select benefit_master_slabs.* from benefit_master_x_slabs
      #left join benefit_master_slabs  on benefit_master_slabs.id = benefit_master_x_slabs.benefit_master_slabs_id
      #where benefit_master_x_slabs.benefit_master_id = 1 and benefit_master_x_slabs.benefit_master_code = 'RPIP599'
      slbs = db((db.benefit_master_x_slabs.benefit_master_id == bmid)&(db.benefit_master_x_slabs.benefit_master_code==policy)).\
        select(db.benefit_master_slabs.ALL,left=db.benefit_master_slabs.on(db.benefit_master_slabs.id == db.benefit_master_x_slabs.benefit_master_slabs_id))
      
      
      #benefit start date & benefit end date
      benefit_start_date = bms[0].benefit_start_date if(len(bms)==1) else common.getISTCurrentLocatTime()
      benefit_end_date = bms[0].benefit_end_date if(len(bms)==1) else common.getISTCurrentLocatTime()
      
      #benefit value of the Plan 
      benefit_value = common.getvalue(bms[0].benefit_value if (len(bms) == 1) else 0)

      #determine total benefit redeemed for this plan & period
      total_redeemed_benefits = 0
      rbs = db((db.benefit_member.member_id == memberid) & (db.benefit_member.plan_code==policy)&\
               ((db.benefit_member.redeem_date >= benefit_start_date) & (db.benefit_member.redeem_date <= benefit_end_date)) &\
               (db.benefit_member.is_active == True)).select()
      
      for rb in rbs:
        total_redeemed_benefits += rb.redeem_amount
        
      #if total redeemed value = max benefit amount, then return
      if(total_redeemed_benefits >= benefit_value):
        
        rspobj = {}
        rspobj["result"] = "success"
        rspobj["error_message"] = ""
        rspobj["memberid"] = memberid
        rspobj["plan"] = policy
        rspobj["total_redeemed_benefits"] = str(total_redeemed_benefits)
        rspobj["benefit_code"] = (bms[0].benefit_code if (len(bms) == 1) else "")
        rspobj["benefit_name"] = (bms[0].benefit_name if (len(bms) == 1) else "")
        rspobj["benefit_value"] = str(benefit_value)
        rspobj["benefit_start_date"] = common.getstringfromdate(benefit_start_date,"%d/%m/%Y")
        rspobj["benefit_end_date"] = common.getstringfromdate(benefit_end_date,"%d/%m/%Y")
        rspobj["discount_code"] = "BNFT_VAL_MAX"
        rspobj["discount_value"] = "0"
        rspobj["discount_date"] = common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")
        rspobj["discount_message"] = common.getmessage(db,"BNFT_VAL_MAX")
        
        logger.loggerpms2.info("Maximum Benefit Reached " + json.dumps(rspobj))
        return json.dumps(rspobj)
      
      
      #for each of the treatment,determing total treatment cost, total UCR, total inspays, total company pays
      #determine for this member -- total treatment cost, total inspays, total patient pays, total company pasy
      totalactualtreatmentcost = 0   #UCR Cost
      totaltreatmentcost = 0  #Cost charged to the client which is equal to UCR fee by default
      totalcopay = 0
      totalinspays = 0
      totalcompanypays = 0
      
      rows = db((db.vw_treatmentprocedure.primarypatient == memberid) &\
                (db.vw_treatmentprocedure.treatmentdate >= benefit_start_date) &\
                (db.vw_treatmentprocedure.treatmentdate <= benefit_end_date) &\
                (db.vw_treatmentprocedure.is_active == True)).select()
      
      
      for r in rows:
        totalactualtreatmentcost = totalactualtreatmentcost + float(common.getvalue(r.ucrfee))
        totaltreatmentcost = totaltreatmentcost + float(common.getvalue(r.procedurefee))
        totalcopay = totalcopay + float(common.getvalue(r.copay))
        totalinspays = totalinspays + float(common.getvalue(r.inspays)) 
        totalcompanypays = totalcompanypays + float(common.getvalue(r.companypays))         
      
      totalamountforbenefit = totaltreatmentcost - totalinspays
      
      #determine the total benefit amount
      redeem_value = 0
      for slb in slbs:
        if(slb.redeem_mode == 'S'):
          #slab mode and not percentage mod
          if((totalamountforbenefit >= slb.redeem_lower_limit) & (totalamountforbenefit <= slb.redeem_upper_limit)):
            redeem_value = slb.redeem_value
            break
        
      benefit_amount = abs(redeem_value - total_redeemed_benefits)
      
      if((benefit_amount + total_redeemed_benefits) >= benefit_value):
        benefit_amount = abs(benefit_value-total_redeemed_benefits)
    
      balance_benefit_amount = benefit_value - (benefit_amount + total_redeemed_benefits)
     
        
      #update benefit_member table on successful payment 
      #if(benefit_amount > 0):
        #benefit_member_id = db.benefit_member.insert(\
          #member_id = memberid,
          #plan_id = planid,
          #plan_code = policy,
          #redeem_date = common.getISTFormatCurrentLocatTime(),
          #redeem_amount = benefit_amount,
          #last_redeemed_date=common.getISTFormatCurrentLocatTime(),
          #last_redeemed_amount=0,
          #balance_benefit_amount=balance_benefit_amount,
          #is_active = True,
          #created_on = common.getISTFormatCurrentLocatTime(),
          #created_by = 1 if(auth.user == None) else auth.user.id,
          #modified_on = common.getISTFormatCurrentLocatTime(),
          #modified_by =  1 if(auth.user == None) else auth.user.id    
      #)
      
      
      
      #return rspobj
      benefit_obj = {}
      benefit_obj["result"] = "success"
      benefit_obj["error_message"] = ""
      benefit_obj["memberid"] = memberid
      benefit_obj["plan"] = policy
   
      benefit_obj["total_redeemed_benefits"] = str(benefit_amount + total_redeemed_benefits)   #this should only be updated by the benefit amount on payment success
      benefit_obj["benefit_code"] = (bms[0].benefit_code if (len(bms) == 1) else "")
      benefit_obj["benefit_name"] = (bms[0].benefit_name if (len(bms) == 1) else "")
      benefit_obj["benefit_value"] = str(benefit_value)
      benefit_obj["benefit_start_date"] = common.getstringfromdate(benefit_start_date,"%d/%m/%Y")
      benefit_obj["benefit_end_date"] = common.getstringfromdate(benefit_end_date,"%d/%m/%Y")
      benefit_obj["redeen_code"] = "BNFT_OK"
      benefit_obj["discount_amount"] = str(benefit_amount)
      benefit_obj["discount_date"] = common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")
      benefit_obj["discount_message"] = common.getmessage(db,"BNFT_OK")
                
       
      
      
      
      
    except Exception as e:
      mssg = "RPIP599 Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)     
  
    logger.loggerpms2.info("Exit from RPIP599 Benefit " + json.dumps(benefit_obj))
    return json.dumps(benefit_obj)