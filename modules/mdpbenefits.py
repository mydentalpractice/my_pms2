from gluon import current
import os
import json
import datetime
import time
from datetime import timedelta

from applications.my_pms2.modules import common
from applications.my_pms2.modules import account
from applications.my_pms2.modules import status
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import mdptreatment
from applications.my_pms2.modules import mdpprocedure
from applications.my_pms2.modules import logger

class Benefit:
  def __init__(self,db):
    self.db = db
    return 
  
  
  def get_benefits(self,avars):
    
    memberid = int(common.getkeyvalue(avars,"memberid","0"))
    members = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.member.company)
    companyid = common.getid(members[0].company) if (len(members) == 1) else "0"
    c = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
    companycode = c[0].company if (len(c) ==1) else ""
    plancode = companycode
    planid = companyid
    
    if(plancode == "RPIP599"):
      rspobj = json.loads(self.RPIP599(avars))
    else:
      rspobj = {}
      rspobj["result"] = "success"
      rspobj["error_message"] = ""
      rspobj["redeen_code"] = "BNFT_INVALID"
      rspobj["redeem_value"] = 0
      rspobj["redeem_date"] = common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")
      rspobj["redeem_message"] = common.getmessage(db,"BNFT_INVALID")
                           
    
    return json.dumps(rspobj)
  
  #avars={
  #Company Code = RPIP599
  #Promocode = RPIP599
  
  
  #Provider Region Plan table
  #-----------------------------
  #compaycode = RPIP599
  #Policy = RPIP599
  #Region = <Region Code>
  #Plan Code = RPIP599BLR (this will be same as HMOPLANCODE field in HMOPLAN table)
  #Procedure Price Plan Code = RPIP599_PPP

  #}
  def RPIP599(self, avars):
    
    logger.loggerpms2.info("Enter RPIP599 ==>>" + str(avars))
    
    db = self.db
    benefit_obj = {}
    auth = current.auth
    
    try:
      #get company from member (if member has purchased this RIP599)
      memberid = int(common.getkeyvalue(avars,"memberid","0"))
      members = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.member.company)
      companyid = common.getid(members[0].company) if (len(members) == 1) else "0"
      c = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
      companycode = c[0].company if (len(c) ==1) else ""
      plancode = companycode
      planid = companyid
      
      #get benefit_master
      #Table: benefit_master_x_member
      #Columns:
      #id int(11) AI PK 
      #member_id int(11) 
      #plan_id int(11) 
      #benefit_master_id int(11) 
      #plan_code varch      
      bms = db((db.benefit_master_x_member.member_id == memberid) & (db.benefit_master_x_member.plan_code == plancode) &\
             (db.benefit_master.is_valid == True) & (db.benefit_master.is_active == True)).select(db.benefit_master.All,\
                                                                                                  left=db.benefit_master.on(db.benefit_master.id == benefit_master_x_member.member_id))
      bmid = bms[0].id if(len(bms)==1) else 0
      
      #Table: benefit_master_x_slabs
      #Columns:
        #id int(11) AI PK 
        #benefit_master_id int(11) 
        #benefit_master_slabs_id int(11)

      xslbs = db((db.benefit_master_x_slabs.benefit_master_id == bmid)).select()
      slbid = xslbs[0].benefit_master_slabs_id if (len(xslbs)==0) else 0
      slbs = db(db.benefit_master_slab.id == slbid).select()
      
      #benefit start date & benefit end date
      benefit_start_date = bms[0].benefit_start_date
      benefit_end_date = bms[0].benefit_end_date
      
      #benefit value of the Plan 
      benefit_value = common.getvalue(bms[0].value if (len(bms) == 1) else 0)

      #determine total benefit redeemed for this plan & period
      total_redeemed_benefits = 0
      rbs = db((db.benefit_member.member_id == memberid) & (db.benefit_member.plan_code==plancode)&\
               ((db.benefit_member.redeem_date >= benefit_start_date) & (db.benefit_member.treatmentdate <= redeem_date)) &\
               (db.benefit_member.is_active == True)).select()
      
      for rb in rbs:
        total_redeemed_benefits += r.redeem_amount
        
      #if total redeemed value = max benefit amount, then return
      if(total_redeemed_benefits >= benefit_value):
        
        rspobj = {}
        rspobj["result"] = "success"
        rspobj["error_message"] = ""
        rspobj["memberid"] = memberid
        rspobj["plancode"] = plancode
        rspobj["total_redeemed_benefits"] = str(total_redeemed_benefits)
        rspobj["benefit_code"] = (bms[0].benefit_code if (len(bms) == 1) else "")
        rspobj["benefit_name"] = (bms[0].benefit_name if (len(bms) == 1) else "")
        rspobj["benefit_value"] = str(benefit_value)
        rspobj["benefit_start_date"] = common.getstringfromdate(benefit_start_date,"%d/%m/%Y")
        rspobj["benefit_end_date"] = common.getstringfromdate(benefit_end_date,"%d/%m/%Y")
        rspobj["redeen_code"] = "BNFT_VAL_MAX"
        rspobj["redeem_value"] = "0"
        rspobj["redeem_date"] = common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")
        rspobj["redeem_message"] = common.getmessage(db,"BNFT_VAL_MAX")
        
        logger.loggerpms2.info("Maximum Benefit Reached " + json.dumps(rspobj))
        return json.dumps(rspobj)
      
      
      #for each of the treatment,determing total treatment cost, total UCR, total inspays, total company pays
      #determine for this member -- total treatment cost, total inspays, total patient pays, total company pasy
      totalactualtreatmentcost = 0   #UCR Cost
      totaltreatmentcost = 0  #Cost charged to the client which is equal to UCR fee by default
      totalcopay = 0
      totalinspays = 0
      totalcompanypays = 0
      
      rows = db((db.vw_treatmentprocedure.primarypatientid == memberid) &\
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
        if(slb.mode == 'S'):
          #slab mode and not percentage mod
          if((totalamountforbenefit >= slb.redeem_lower_limit) & (totalamountforbenefit <= slb.redeem_upper_limit)):
            redeem_value = slb.redeem_value
            break
        
      benefit_amount = abs(redeem_value - total_redeemed_benefits)
      
      if((benefit_amount + total_redeemed_benefits) >= benefit_value):
        benefit_amount = abs(benefit_value-total_redeemed_benefits)
    
      balance_benefit_amount = benefit_value - (benefit_amount + total_redeemed_benefits)
     
        
      #update benefit_member table
      benefit_member_id = db.benefit.member.insert(\
        
        member_id = memberid,
        plan_id = planid,
        plan_code = plancode,
        redeem_date = common.getISTFormatCurrentLocatTime(),
        redeem_amount = benefit_amount,
        last_redeemed_date=common.getISTFormatCurrentLocatTime(),
        last_redeemed_amount=0,
        balance_benefit_amount=balance_benefit_amount,
        is_active = True,
        created_on = common.getISTFormatCurrentLocatTime(),
        created_by = 1 if(auth.user == None) else auth.user.id,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by =  1 if(auth.user == None) else auth.user.id    
        
      
      
      )
      
      
      
      #return rspobj
      benefit_obj = {}
      benefit_obj["result"] = "success"
      benefit_obj["error_message"] = ""
      benefit_obj["memberid"] = memberid
      benefit_obj["plancode"] = plancode
      benefit_obj["total_redeemed_benefits"] = str(benefit_amount + total_redeemed_benefits)
      benefit_obj["benefit_code"] = (bms[0].benefit_code if (len(bms) == 1) else "")
      benefit_obj["benefit_name"] = (bms[0].benefit_name if (len(bms) == 1) else "")
      benefit_obj["benefit_value"] = str(benefit_value)
      benefit_obj["benefit_start_date"] = common.getstringfromdate(benefit_start_date,"%d/%m/%Y")
      benefit_obj["benefit_end_date"] = common.getstringfromdate(benefit_end_date,"%d/%m/%Y")
      benefit_obj["redeen_code"] = "BNFT_OK"
      benefit_obj["redeem_value"] = str(benefit_amount)
      benefit_obj["redeem_date"] = common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")
      benefit_obj["redeem_message"] = common.getmessage(db,"BNFT_OK")
                
      
      
      
      
      
    except Exception as e:
      mssg = "RPIP599 Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)     
  
    logger.loggerpms2.info("Exit from RPIP599 Benefit " + json.dumps(benefit_obj))
    return json.dumps(benefit_obj)