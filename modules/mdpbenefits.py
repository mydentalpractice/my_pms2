from gluon import current
import os
import json
import datetime
import time
from datetime import timedelta

import requests

from applications.my_pms2.modules import common
from applications.my_pms2.modules import account

from applications.my_pms2.modules import logger


class Benefit:
  def __init__(self,db):
    self.db = db
    return 

  def tempWallet(self,avars):
    db = self.db
    rspobj = {}
    
    try:
      i = 0
    
    except Exception as e:
      mssg = "" + str(e)
      logger.loggerpms2.info(mssg)      
      rspobj = {}
      rspobj["result"] = "fail"
      rspobj["error_message"] = mssg
      return json.dumps(rspobj)     
    

    return json.dumps(rspobj)


  def credit_wallet(self,avars):
    logger.loggerpms2.info("Enter Credit Wallet " + json.dumps(avars))
    
    db = self.db
    rspobj = {}
    reqobj = {}
    
    try:
      member_id = int(common.getkeyvalue(avars,"member_id", "0"))
      wallet_type = common.getkeyvalue(avars,"wallet_type", "SUPER_WALLET")
      walletamount = float(common.getkeyvalue(avars,"walletamount", "0"))
      discount_amount = float(common.getkeyvalue(avars,"discount_amount", "0"))
     
      reqobj["member_id"] = member_id
      reqobj["wallet_type"] = wallet_type
      reqobj["transaction_type"] = "CR"
      reqobj["amount"] = walletamount
      reqobj["head_name"] = "CASHBACK"
      reqobj["head_id"] = str(member_id)
      
      urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.vw_url)
      vw_url = urlprops[0].vw_url if(len(urlprops) > 0) else ""
      vw_url = vw_url + "WalletCrDr"
      logger.loggerpms2.info("Credit Wallet Request " + vw_url + " " + json.dumps(reqobj))
      resp = requests.post(vw_url,json=reqobj)
      logger.loggerpms2.info("Credit Wallet Respones " + vw_url + " " + json.dumps(resp.json()))
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            rspobj = resp.json()

            if(rspobj["RETURN_CODE"] != 1):
              mssg = "Credit Wallet API - Wallet Response Error: " + common.getkeyvalue(rspobj,"RETURN_MESSAGE", "")
              rspobj = {}
              rspobj["result"] = "fail"
              rspobj["error_message"] = mssg
            
            #success API
            rspobj["result"] = "success"
            rspobj["error_message"] = ""
      else:
        #response error
        mssg = "Credit Wallet API -  HTTP Response Error: " + str(resp.status_code)
        logger.loggerpms2.info(mssg)      
        rspobj = {}
        rspobj["result"] = "fail"
        rspobj["error_message"] = mssg
        return json.dumps(rspobj)          
    
    except Exception as e:
      
      mssg = "Credit Wallet API Exception " + str(e)
      logger.loggerpms2.info(mssg)      
      rspobj = {}
      rspobj["result"] = "fail"
      rspobj["error_message"] = mssg
      return json.dumps(rspobj)     
    
    logger.loggerpms2.info("Exit Credit Wallet (Benefits) " + json.dumps(rspobj))
    return json.dumps(rspobj)  
  
  def debit_wallet(self,avars):
      logger.loggerpms2.info("Enter Debit Wallet " + json.dumps(avars))
      
      db = self.db
      rspobj = {}
      reqobj = {}
      
      try:
        member_id = int(common.getkeyvalue(avars,"member_id", "0"))
        wallet_type = common.getkeyvalue(avars,"wallet_type", "SUPER_WALLET")
        walletamount = float(common.getkeyvalue(avars,"walletamount", "0"))
       
        reqobj["member_id"] = member_id
        reqobj["wallet_type"] = wallet_type
        reqobj["transaction_type"] = "DR"
        reqobj["amount"] = walletamount
        reqobj["head_name"] = "CASHBACK"
        reqobj["head_id"] = str(member_id)
        
        urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.vw_url)
        vw_url = urlprops[0].vw_url if(len(urlprops) > 0) else ""
        vw_url = vw_url + "WalletCrDr"
        logger.loggerpms2.info("Debit Wallet Request " + vw_url + " " + json.dumps(reqobj))
        resp = requests.post(vw_url,json=reqobj)
        logger.loggerpms2.info("Debit Wallet Respones " + vw_url + " " + json.dumps(resp.json()))
      
        if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
              rspobj = resp.json()
  
              if(rspobj["RETURN_CODE"] != 1):
                mssg = "Debit Wallet API - Wallet Response Error: " + common.getkeyvalue(rspobj,"RETURN_MESSAGE", "")
                rspobj = {}
                rspobj["result"] = "fail"
                rspobj["error_message"] = mssg
              
              #success API
              rspobj["result"] = "success"
              rspobj["error_message"] = ""
        else:
          #response error
          mssg = "Debit Wallet API -  HTTP Response Error: " + str(resp.status_code)
          logger.loggerpms2.info(mssg)      
          rspobj = {}
          rspobj["result"] = "fail"
          rspobj["error_message"] = mssg
          return json.dumps(rspobj)          
      
      except Exception as e:
        
        mssg = "Debit Wallet API Exception " + str(e)
        logger.loggerpms2.info(mssg)      
        rspobj = {}
        rspobj["result"] = "fail"
        rspobj["error_message"] = mssg
        return json.dumps(rspobj)     
      
      logger.loggerpms2.info("Exit Debit Wallet (Benefits) " + json.dumps(rspobj))
      return json.dumps(rspobj)  
      
  
  #This API will debit wallet of the amount used from the wallet in the 
  #payment
  def ywallet_success(self,avars):
    logger.loggerpms2.info("Enter Wallet Success API - " + json.dumps(avars))

    db = self.db
    rspobj = {}
    reqobj = {}  
    try:
      paymentid = int(common.getkeyvalue(avars,"paymentid","0"))
      p = db((db.payment.id == paymentid) & (db.payment.is_active == True)).select()
      precommitamount = float(p[0].amount) if(len(p)>0) else 0
      amount = float(p[0].amount) if(len(p)>0) else 0
      amount = precommitamount if (precommitamoun > 0) else amount
      
      memberid = int(p[0].patientmember) if(len(p)>0) else 0
      providerid = int(p[0].provider) if(len(p)>0) else 0
      tplanid = int(p[0].treatmentplan) if(len(p)>0) else 0
      tr = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
      treatmentid = int(tr[0].id) if(len(tr)>0) else 0      
      wallet_type  = tr[0].wallet_type if(len(tr) > 0) else ""
      walletamount = amount
      super_wallet_amount = walletamount if wallet_type == "SUPER_WALLET" else 0
      mdp_wallet_amount = walletamount if wallet_type == "MDP_WALLET" else 0
      
      #get provider's region
      #get region code
      provs = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.groupregion)
      regionid = int(common.getid(provs[0].groupregion)) if(len(provs) == 1) else 1
      regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select(db.groupregion.groupregion)
      regioncode = common.getstring(regions[0].groupregion) if(len(regions) == 1) else "ALL"
    
      #get companycode
      pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == memberid)).select(db.vw_memberpatientlist.company,db.vw_memberpatientlist.hmoplan)
      companyid = int(common.getid(pats[0].company)) if(len(pats) == 1) else 0
      companys = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
      companycode = common.getstring(companys[0].company) if(len(companys) == 1) else "PREMWALKIN"
    
      ##for backward compatibility determine procedurepriceplancode from member's plan at the time of registration
      hmoplanid = int(common.getid(pats[0].hmoplan)) if(len(pats) == 1) else 0  #this is the patient's previously assigned plan-typically at registration
      hmoplans = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode)
      hmoplancode = common.getstring(hmoplans[0].hmoplancode) if(len(hmoplans) == 1) else "PREMWALKIN"
      r = db(
        (db.provider_region_plan.companycode == companycode) &\
        (db.provider_region_plan.plancode == hmoplancode) &\
        ((db.provider_region_plan.regioncode == regioncode)|(db.provider_region_plan.regioncode == 'ALL'))).select()
      plancode = r[0].policy if(len(r) == 1) else "PREMWALKIN"    
      
      avars={}
      avars["plan_code"] =plancode
      avars["company_code"] = companycode                          
      avars["member_id"] = memberid
      avars["rule_event"] = "rules_payment"
      avars["mdp_wallet_usase"] = 0
      avars["super_wallet_amount"] = super_wallet_amount 
      avars["mdp_wallet_amount"] = mdp_wallet_amount
  
      rulesobj = None #mdprules.Plan_Rules(db)
      rspobj = None #json.loads(rulesobj.Get_Plan_Rules(avars))
      
      if(rspobj["result"] == "fail"):
        mssg = "Wallet Success API - Wallet Response Error: " + common.getkeyvalue(rspobj,"RETURN_MESSAGE", "")
        rspobj["error_message"] = mssg
      else:
        db(db.payment.id == paymentid).update(wallet_type = wallet_type,walletamount=walletamount,
                                              modified_on=common.getISTCurrentLocatTime())
    
    except Exception as e:
      mssg = "Wallet Success API Exception " + str(e)
      rspobj = {}
      rspobj["result"] = "fail"
      rspobj["error_message"] = mssg
        
    
    mssg = json.dumps(rspobj)
    logger.loggerpms2.info(mssg)
    return mssg

  #This API will debit wallet of the amount used from the wallet in the 
  #payment
  def wallet_success(self,avars):
    logger.loggerpms2.info("Enter Wallet Success API - " + json.dumps(avars))

    db = self.db
    rspobj = {}
    reqobj = {}  
    try:
      paymentid = int(common.getkeyvalue(avars,"paymentid","0"))
      p = db((db.payment.id == paymentid) & (db.payment.is_active == True)).select()
      memberid = int(p[0].patientmember) if(len(p)>0) else 0
      tplanid = int(p[0].treatmentplan) if(len(p)>0) else 0
      tr = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
      treatmentid = int(tr[0].id) if(len(tr)>0) else 0
      wallet_type  = tr[0].wallet_type if(len(tr) > 0) else "SUPER_WALLET"
      walletamount = float(common.getvalue(tr[0].walletamount if(len(tr)>0) else 0))
      
      reqobj["member_id"] = memberid
      reqobj["wallet_type"] = wallet_type
      reqobj["transaction_type"] = "Dr"
      reqobj["amount"] = walletamount
      
      urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.vw_url)
      vw_url = urlprops[0].vw_url if(len(urlprops) > 0) else ""
      vw_url = vw_url + "WalletCrDr"
      resp = requests.post(vw_url,json=reqobj)
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            rspobj = resp.json()

            if(rspobj["RETURN_CODE"] != 1):
              mssg = "Wallet Success API - Wallet Response Error: " + common.getkeyvalue(rspobj,"RETURN_MESSAGE", "")
              rspobj = {}
              rspobj["result"] = "fail"
              rspobj["error_message"] = mssg
            else:
              #success API
              rspobj["result"] = "success"
              rspobj["error_message"] = ""
              
              db(db.payment.id == paymentid).update(wallet_type = wallet_type,walletamount=walletamount,
                                                    modified_on=common.getISTCurrentLocatTime())
      else:
        #response error
        mssg = "Wallet Success API -  HTTP Response Error: " + str(resp.status_code)
        rspobj = {}
        rspobj["result"] = "fail"
        rspobj["error_message"] = mssg
    
    except Exception as e:
      mssg = "Wallet Success API Exception " + str(e)
      rspobj = {}
      rspobj["result"] = "fail"
      rspobj["error_message"] = mssg
        
    
    mssg = json.dumps(rspobj)
    logger.loggerpms2.info(mssg)
    return mssg

  
  #this api is called with 
  #treatment id, wallet type and wallet to apply
  def apply_wallet(self,avars):
    
    logger.loggerpms2.info("Enter Apply Wallet API" + json.dumps(avars))
      
    db = self.db
    rspobj = {}
    
    try:

      #wallet type
      wallet_type = common.getkeyvalue(avars,"wallet_type","supper_wallet")
      
      #wallet_amount
      walletamount = float(common.getkeyvalue(avars,"walletamount","0"))
      
      #treatment
      treatmentid = int(common.getkeyvalue(avars,"treatmentid","0"))
      tr = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select(db.treatment.id, db.treatment.copay,db.treatment.treatmentplan)
      
      #tplanid
      tplanid = tr[0].treatmentplan if(len(tr) > 0) else 0
      tp = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).select()    
  
    
      #get default provider 'P0001'
      p = db((db.provider.provider == 'P0001') & (db.provider.is_active == True)).select(db.provider.id)
      defproviderid = p[0].id if(len(p) > 0) else 0
      providerid = tp[0].provider if (len(tp) > 0) else defproviderid
    
      #treatment_amount = tr[0].copay if (len(tr) > 0) else 0
    
      memberid = tp[0].primarypatient if (len(tp) > 0) else 0
      patientid = tp[0].patient if (len(tp) > 0) else 0
      #mems = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.patientmember.city,\
                                                                                                 #db.patientmember.st,db.patientmember.company)
      #city = mems[0].city if(len(mems)>0) else "Jaipur"
      #state = mems[0].st if(len(mems)>0) else "Rajastan (RJ)"
      #c = db(db.cities.city == city).select(db.cities.id)
      #cityid = c[0].id if(len(c) > 0) else 0

      #get plan
      #companyid = mems[0].company if(len(mems) > 0) else 0
      #c = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
      #companycode = c[0].company if (len(c) ==1) else "RPIP599"
      #cp = db(db.companypolicy.companycode == companycode).select()
      #plan = cp[0].policy if(len(cp) != 0) else "RPIP599"  

      #get region code
      provs = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.groupregion)
      regionid = int(common.getid(provs[0].groupregion)) if(len(provs) == 1) else 1
      regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select(db.groupregion.groupregion)
      regioncode = common.getstring(regions[0].groupregion) if(len(regions) == 1) else "ALL"
          
      ## get patient's company
      pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select(db.vw_memberpatientlist.company,db.vw_memberpatientlist.hmoplan)
      companyid = int(common.getid(pats[0].company)) if(len(pats) == 1) else 0
      companys = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
      companycode = common.getstring(companys[0].company) if(len(companys) == 1) else "PREMWALKIN"
      
      
      ##for backward compatibility determine procedurepriceplancode from member's plan at the time of registration
      hmoplanid = int(common.getid(pats[0].hmoplan)) if(len(pats) == 1) else 0  #this is the patient's previously assigned plan-typically at registration
      hmoplans = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode)
      hmoplancode = common.getstring(hmoplans[0].hmoplancode) if(len(hmoplans) == 1) else "PREMWALKIN"
      r = db(
             (db.provider_region_plan.companycode == companycode) &\
             (db.provider_region_plan.plancode == hmoplancode) &\
             ((db.provider_region_plan.regioncode == regioncode)|(db.provider_region_plan.regioncode == 'ALL'))).select()
      plancode = r[0].policy if(len(r) == 1) else "PREMWALKIN"

      
      #get wallet list
      #get available wallet balance
      paytm = json.loads(account._calculatepayments(db, tplanid))
      reqobj = {}
      reqobj["action"] = "getwallet_balance"
      reqobj["member_id"] = memberid
      reqobj["plan_code"] = plancode
      reqobj["amount"] = paytm["totalcopay"]
  
      rspobj = json.loads(self.getwallet_balance(reqobj))
      if(rspobj["result"] == "success"):
        wlist = rspobj["wallet_list"]
      else:
        wlist = []

      
      #apply wallet
      db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).update(wallet_type = wallet_type, walletamount = walletamount)
      db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).update(wallet_type = wallet_type, totalwalletamount = walletamount)
      db.commit()
      
          
      rspobj = {}
      rspobj["wlist"] = wlist
      rspobj["result"] = "success"
      rspobj["error_message"] = ""
    
    except Exception as e:
      mssg = "Apply Wallet API Exception" + str(e)
      logger.loggerpms2.info(mssg)      
      rspobj = {}
      rspobj["result"] = "fail"
      rspobj["error_message"] = mssg
  
    mssg = json.dumps(rspobj)
    logger.loggerpms2.info("Exit Apply Wallet API " + mssg)  
    return mssg


  def create_wallet(self,avars):
    logger.loggerpms2.info("Enter Create_Wallet (Benefits) " + json.dumps(avars))
    db = self.db
    rspobj = {}
    reqobj = {}
    
    try:
      #make a POST Call
      reqobj = avars
      #reqobj["member_id"] = int(common.getid(common.getkeyvalue(avars,"member_id","0")))
      
      urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.vw_url)
      vw_url = urlprops[0].vw_url if(len(urlprops) > 0) else ""
      
      vw_url = vw_url + "createWallet"
      logger.loggerpms2.info("Create Wallet Request " + vw_url + " " + json.dumps(reqobj))
      resp = requests.post(vw_url,json=reqobj)
      logger.loggerpms2.info("Create Wallet Respones " + vw_url + " " + json.dumps(resp.json()))
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            rspobj = resp.json()
            
            if(rspobj["RETURN_CODE"] != 1):
              mssg = "Create Wall API - Wallet Response Error: " + common.getkeyvalue(rspobj,"RETURN_MESSAGE", "")
              rspobj = {}
              rspobj["result"] = "fail"
              rspobj["error_message"] = mssg
            
            #success API
            rspobj["result"] = "success"
            rspobj["error_message"] = ""
      else:
        #response error
        mssg = "Create Wallet API -  HTTP Response Error: " + str(resp.status_code)
        logger.loggerpms2.info(mssg)      
        rspobj = {}
        rspobj["result"] = "fail"
        rspobj["error_message"] = mssg
        return json.dumps(rspobj)             
    except Exception as e:
      mssg = "Create Wallet API Exception" + str(e)
      logger.loggerpms2.info(mssg)      
      rspobj = {}
      rspobj["result"] = "fail"
      rspobj["error_message"] = mssg
      return json.dumps(rspobj)     
    
    mssg = json.dumps(rspobj)
    logger.loggerpms2.info(mssg)
    return mssg    

  def getwallet_balance(self,avars):
    
    logger.loggerpms2.info("Enter Get Wallet Balance " + json.dumps(avars))
    
    db = self.db
    rspobj = {}
    reqobj = {}
    
    try:
      
      member_id = int(common.getid(common.getkeyvalue(avars,"member_id","0")))
      plan_code = common.getkeyvalue(avars,"plan_code","PREMWALKIN")
      amount = float(common.getvalue(common.getkeyvalue(avars,"amount","0")))
      
      #make a POST Call
      reqobj = {}
      reqobj["member_id"] = member_id
      reqobj["plan_code"] = plan_code
      
      urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.vw_url)
      vw_url = urlprops[0].vw_url if(len(urlprops) > 0) else ""
      
      vw_url = vw_url + "getWalletBalance"
      resp = requests.post(vw_url,json=reqobj)
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            rspobj = resp.json()
            
            if(rspobj["RETURN_CODE"] != 1):
              mssg = "Get Wallet Balance API - Wallet Response Error: " + common.getkeyvalue(rspobj,"RETURN_MESSAGE", "")
              rspobj = {}
              rspobj["result"] = "fail"
              rspobj["error_message"] = mssg
              return json.dumps(rspobj)
            
            mdp_wallet_usage = float((common.getkeyvalue(rspobj,"MDP_WALLET_USASE","0")))
            mdp_wallet_usage_for_plan = float((common.getkeyvalue(rspobj,"MDP_WALLET_USASE_FOR_PLAN","0")))
                        
            
            balobj = rspobj["WALLET_BALANCE"]
            super_wallet_amount = float(common.getkeyvalue(balobj,"super_wallet_amount","0"))
            mdp_wallet_amount = float(common.getkeyvalue(balobj,"mdp_wallet_amount","0"))
            
            #min of mdp wallet amount and % of total treatment amount to Pay
            percentamount = float((amount * mdp_wallet_usage_for_plan)/100)
            mdp_wallet_usage_amount = min(mdp_wallet_amount,percentamount)  
            
            #rspobj["super_wallet_amount"] = super_wallet_amount
            #rspobj["mdp_wallet_amount"] = mdp_wallet_usage_amount
            
            rspobj["super_wallet_message"] = "Available Balance Rs." + str(super_wallet_amount)
            rspobj["mdp_wallet_message"] = "Available Balance Rs." + str(mdp_wallet_usage_amount) + ". " + \
              "This is minimum of " + str(mdp_wallet_amount) + " and " + str(mdp_wallet_usage) + " percentage of Rs." + str(amount) + "(" + str(percentamount) + ")"
            
            rspobj["result"] = "success"
            rspobj["error_message"] = ""
            
            wallet_list = []
            lstobj = {}
            lstobj["wallet_amount"] = super_wallet_amount
            lstobj["wallet_type"]  = "SUPER_WALLET"
            lstobj["wallet_message"] = rspobj["super_wallet_message"]
            wallet_list.append(lstobj)
            lstobj = {}
            lstobj["wallet_amount"] = mdp_wallet_usage_amount
            lstobj["wallet_type"]  = "MDP_WALLET"
            lstobj["wallet_message"] = rspobj["mdp_wallet_message"]
            wallet_list.append(lstobj)
            rspobj["wallet_list"] = wallet_list
            
      else:
        #response error
        mssg = "Get Wallet Balance API -  HTTP Response Error: " + str(resp.status_code)
        logger.loggerpms2.info(mssg)      
        rspobj = {}
        rspobj["result"] = "fail"
        rspobj["error_message"] = mssg
        return json.dumps(rspobj)
      
    except Exception as e:
      mssg = "Get Wallet Balance API Exception" + str(e)
      logger.loggerpms2.info(mssg)      
      rspobj = {}
      rspobj["result"] = "fail"
      rspobj["error_message"] = mssg
      return json.dumps(rspobj)     
    
    mssg = json.dumps(rspobj)
    logger.loggerpms2.info(mssg)
    return mssg    

  def xgetwallet_balance(self,avars):
    
    logger.loggerpms2.info("Enter Get Wallet Balance " + json.dumps(avars))
    
    db = self.db
    rspobj = {}
    reqobj = {}
    
    try:
      
      member_id = int(common.getid(common.getkeyvalue(avars,"member_id","0")))
      amount = float(common.getvalue(common.getkeyvalue(avars,"amount","0")))
      
      #make a POST Call
      reqobj = {}
      reqobj["member_id"] = member_id
      
      urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.vw_url)
      vw_url = urlprops[0].vw_url if(len(urlprops) > 0) else ""
      
      vw_url = vw_url + "getWalletBalance"
      resp = requests.post(vw_url,json=reqobj)
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            rspobj = resp.json()
            
            if(rspobj["RETURN_CODE"] != 1):
              mssg = "Get Wallet Balance API - Wallet Response Error: " + common.getkeyvalue(rspobj,"RETURN_MESSAGE", "")
              rspobj = {}
              rspobj["result"] = "fail"
              rspobj["error_message"] = mssg
              return json.dumps(rspobj)
            
            mdp_wallet_usage = int((common.getkeyvalue(rspobj,"MDP_WALLET_USASE","0")))
                        
            
            balobj = rspobj["WALLET_BALANCE"]
            super_wallet_amount = float(common.getkeyvalue(balobj,"super_wallet_amount","0"))
            mdp_wallet_amount = float(common.getkeyvalue(balobj,"mdp_wallet_amount","0"))
            
            #min of mdp wallet amount and % of total treatment amount to Pay
            percentamount = float((amount * mdp_wallet_usage)/100)
            mdp_wallet_usage_amount = min(mdp_wallet_amount,float((amount * mdp_wallet_usage)/100))  
            
            #rspobj["super_wallet_amount"] = super_wallet_amount
            #rspobj["mdp_wallet_amount"] = mdp_wallet_usage_amount
            
            rspobj["super_wallet_message"] = "Available Balance Rs." + str(super_wallet_amount)
            rspobj["mdp_wallet_message"] = "Available Balance Rs." + str(mdp_wallet_usage_amount) + ". " + \
              "This is minimum of " + str(mdp_wallet_amount) + " and " + str(mdp_wallet_usage) + " percentage of Rs." + str(amount) + "(" + str(percentamount) + ")"
            
            rspobj["result"] = "success"
            rspobj["error_message"] = ""
            
            wallet_list = []
            lstobj = {}
            lstobj["wallet_amount"] = super_wallet_amount
            lstobj["wallet_type"]  = "SUPER_WALLET"
            lstobj["wallet_message"] = rspobj["super_wallet_message"]
            wallet_list.append(lstobj)
            lstobj = {}
            lstobj["wallet_amount"] = mdp_wallet_usage_amount
            lstobj["wallet_type"]  = "MDP_WALLET"
            lstobj["wallet_message"] = rspobj["mdp_wallet_message"]
            wallet_list.append(lstobj)
            rspobj["wallet_list"] = wallet_list
            
      else:
        #response error
        mssg = "Get Wallet Balance API -  HTTP Response Error: " + str(resp.status_code)
        logger.loggerpms2.info(mssg)      
        rspobj = {}
        rspobj["result"] = "fail"
        rspobj["error_message"] = mssg
        return json.dumps(rspobj)
      
    except Exception as e:
      mssg = "Get Wallet Balance API Exception" + str(e)
      logger.loggerpms2.info(mssg)      
      rspobj = {}
      rspobj["result"] = "fail"
      rspobj["error_message"] = mssg
      return json.dumps(rspobj)     
    
    mssg = json.dumps(rspobj)
    logger.loggerpms2.info(mssg)
    return mssg    


  # This API is called to reverse voucher application
  def reverse_voucher(self,avars):
    logger.loggerpms2.info("Enter Reverse Voucher API" + json.dumps(avars))
    
    db=self.db
    try:
      voucher_code = common.getkeyvalue(avars,"voucher_code","")

      #treatment
      treatmentid = int(common.getkeyvalue(avars,"treatmentid","0"))

      tr = db(db.treatment.id == treatmentid).select()
      #tplanid
      tplanid = tr[0].treatmentplan if(len(tr) > 0) else 0
      
      
      #reset voucher_discount
      db((db.treatment.id == treatmentid) & (db.treatment.voucher_code == voucher_code) & (db.treatment.is_active == True)).\
        update(discount_amount = 0,voucher_code="" )
      db.commit()
      
      db((db.treatmentplan.id == tplanid) & (db.treatmentplan.voucher_code == voucher_code) & (db.treatmentplan.is_active == True)).\
        update(totaldiscount_amount = 0, voucher_code="")
      db.commit()

      db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.voucher_code == voucher_code) & (db.treatment_procedure.is_active == True)).\
        update(discount_amount = 0, voucher_code="")
      db.commit()

      account._updatetreatmentpayment(db,tplanid,0)
      
      rspobj = {}
      rspobj["result"] = "success"
      rspobj["error_message"] = ""
      
    except Exception as e:
      mssg = "Reverse Voucher API  Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      rspobj = {}
      rspobj["result"] = "fail"
      rspobj["error_message"] = mssg
      return json.dumps(rspobj)        
    
    return json.dumps(rspobj) 
    
    
  
  def apply_voucher(self,avars):
    logger.loggerpms2.info("Enter Apply Voucher API" + json.dumps(avars))
    
    db=self.db
    try:
      voucher_code = common.getkeyvalue(avars,"voucher_code","")
      
      #treatment
      treatmentid = int(common.getkeyvalue(avars,"treatmentid","0"))
      tr = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select(db.treatment.id, db.treatment.copay,db.treatment.treatmentplan)
      
      #tplanid
      tplanid = tr[0].treatmentplan if(len(tr) > 0) else 0
      tp = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).select()    
  
    
      #get default provider 'P0001'
      p = db((db.provider.provider == 'P0001') & (db.provider.is_active == True)).select(db.provider.id)
      defproviderid = p[0].id if(len(p) > 0) else 0
      providerid = tp[0].provider if (len(tp) > 0) else defproviderid
    
      treatment_amount = tr[0].copay if (len(tr) > 0) else 0
    
      memberid = tp[0].primarypatient if (len(tp) > 0) else 0
      mems = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.patientmember.city,\
                                                                                                 db.patientmember.st,db.patientmember.company)
      city = mems[0].city if(len(mems)>0) else "Jaipur"
      state = mems[0].st if(len(mems)>0) else "Rajastan (RJ)"
      c = db(db.cities.city == city).select(db.cities.id)
      cityid = c[0].id if(len(c) > 0) else 0
    
    
      #get plan
      companyid = mems[0].company if(len(mems) > 0) else 0
      c = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
      companycode = c[0].company if (len(c) ==1) else "RPIP599"
      cp = db(db.companypolicy.companycode == companycode).select()
      plan = cp[0].policy if(len(cp) != 0) else "RPIP599"  
      
      
      #Apply Voucher
      reqobj  = {}
      reqobj["treatment_id"] = int(treatmentid)
      reqobj["member_id"] = int(memberid)
      reqobj["plan_code"] = plan
      reqobj["state"] = state
      reqobj["city_id"] = int(cityid)
    
      #the following reqobj is test data. It has to be commented 
      #reqobj["treatment_id"] = 2
      #reqobj["member_id"] = 44
      #reqobj["plan_code"] = ""
      #reqobj["state"] = "Andaman and Nicobar Islands(AN)"
      #reqobj["city_id"] = 2
    
      vlist = []
      rspobj = json.loads(self.getVoucherList(reqobj))
      vlist = rspobj["voucher_list"] if(rspobj["result"] == "success") else []
      #calculate voucher
      reqobj  = {}
      for v in vlist:
        if(v["voucher_code"] == voucher_code):
          reqobj["voucher_code"] = voucher_code
          reqobj["member_id"] = int(memberid)
          reqobj["plan_code"] = plan
          reqobj["state"] = state
          reqobj["city_id"] = int(cityid)
          reqobj["treatment_id"] = treatmentid
          reqobj["order_amount"] = treatment_amount
          break;

      rspobj = json.loads(self.calculateVoucher(reqobj))
      rspobj["voucher_list"] = vlist
      
      displaymssg = ""
      if(rspobj["result"] == "fail"):
        mssg = "Error Apply Voucher - Calculate Voucher API " +  " " + json.dumps(rspobj)
        logger.loggerpms2.info(mssg)
        displaymssg = rspobj["voucher_message"]
        discount_amount = 0   
      else:
        mssg = "Success Apply Voucher - Calculate Voucher API " + json.dumps(rspobj)
        logger.loggerpms2.info(mssg)
        displaymssg = rspobj["voucher_message"]
        discount_amount = float(rspobj["discount_amount"])
        
    except Exception as e:
      mssg = "Apply Voucher API  Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      rspobj = {}
      rspobj["result"] = "fail"
      rspobj["error_message"] = mssg
      return json.dumps(rspobj)        

    return json.dumps(rspobj) 
  
  #treament_id, member_id, plan_code, state, city_id
  def getVoucherList(self,avars):
    logger.loggerpms2.info("Enter Get Voucher List " + json.dumps(avars))
    db = self.db
    rspobj = {}
    reqobj = {}

    try:
     
      reqobj["treatment_ids"] = int(common.getkeyvalue(avars,"treatment_id","0"))   #<id> field of the treatment table
      reqobj["customer_id"] = int(common.getkeyvalue(avars,"member_id",""))         #<id> field of the patientmember table
      reqobj["plan_code"] = common.getkeyvalue(avars,"plan_code","")                #<plancode> offered to a patient
      reqobj["region"] = common.getkeyvalue(avars,"state","")                       #<memberis state
      reqobj["city"] = int(common.getkeyvalue(avars,"city_id","0"))                 #<members> city ID <id> of the cities table
    
      
      #make a POST Call
      urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.vw_url)
      vw_url = urlprops[0].vw_url if(len(urlprops) > 0) else ""
      
      vw_url = vw_url + "getVoucher"
      resp = requests.post(vw_url,json=reqobj)
      
      voucher_code = ""
      voucher_message = ""  
      vclist = []
      
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
        rspobj = resp.json()    

        vcobj = common.getkeyvalue(rspobj,"VOUCHER_DATA", [])
        
        #error voucher list
        if(rspobj["RETURN_CODE"] != 1):
          mssg = "Get Voucher List Error: " + json.dumps(rspobj)
          logger.loggerpms2.info(mssg)  
          voucher_message = common.getkeyvalue(rspobj,"RETURN_MESSAGE","Get Voucher List Error")
          rspobj = {}
          
          rspobj["voucher_code"] = ""
          rspobj["voucher_message"] = voucher_message
          rspobj["voucher_list"] = []
          rspobj["result"] = "fail"
          rspobj["error_message"] = mssg
          return json.dumps(rspobj)     
        
        #success get voucher list
        for vc in vcobj:
          voucher_code = common.getkeyvalue(vc,"voucher_code","")
          if(common.getkeyvalue(vc,"discount_type","Percentage")):
            voucher_message = "You will get cashback of " +str(common.getstring(common.getkeyvalue(vc,"discount",0))) + "% on treatment. Applicable to treatment above certain value"
          else:
            voucher_message = "You will get cashback of " + str(common.getstring(common.getkeyvalue(vc,"discount",0)))+ " on treatment cost. Applicable to treatment above certain value"
          vco = {}
          vco["voucher_code"] = voucher_code
          vco["voucher_message"] = voucher_message
          vclist.append(vco)
        
        rspobj={}  
        rspobj["result"] = "success"
        rspobj["error_message"]  = ""
        rspobj["voucher_list"] = vclist
        
      else:
        mssg = "Get Voucher List Response Error:\n" + str(resp.status_code)
        logger.loggerpms2.info(mssg)      
        rspobj = {}
        rspobj["voucher_code"] = ""
        rspobj["voucher_message"] = mssg
        rspobj["voucher_list"] = []
        rspobj["result"] = "fail"
        rspobj["error_message"] = mssg
        return json.dumps(rspobj)
      
    except Exception as e:
      mssg = "Get Voucher List  Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      rspobj = {}
      rspobj["voucher_code"] = ""
      rspobj["voucher_message"] = mssg
      rspobj["voucher_list"] = []
      rspobj["result"] = "fail"
      rspobj["error_message"] = mssg
      return json.dumps(rspobj)     
  
    return json.dumps(rspobj)


  #avars
  #treatment_id, order_amount, voucher_code, member_id, state, city_code, city_id,plan_code
  def calculateVoucher(self,avars):
    logger.loggerpms2.info("Enter Calculate Voucher " + json.dumps(avars))
    db = self.db
    rspobj = {}
    reqobj = {}

    try:
      reqobj["action"] = "getdiscount"
      reqobj["voucherCode"] = common.getkeyvalue(avars,"voucher_code","")
      reqobj["customerId"] = common.getkeyvalue(avars,"member_id","")
      reqobj["planCode"] = common.getkeyvalue(avars,"plan_code","")
      reqobj["region"] = common.getkeyvalue(avars,"state","")
      reqobj["city"] = int(common.getkeyvalue(avars,"city_id","0"))
    
      lst = []
    
      trobj = {}
      trobj["id"] = int(common.getkeyvalue(avars,"treatment_id","0"))
      trobj["orderAmount"] = float(common.getkeyvalue(avars,"order_amount","0"))
      lst.append(trobj)
      reqobj["treatment_ids"] = lst
      
      treatmentid = int(common.getkeyvalue(avars,"treatment_id","0"))
      t = db(db.treatment.id == treatmentid).select(db.treatment.treatmentplan)
      tplanid = int(t[0].treatmentplan) if(len(t) > 0) else 0
      
      
      
      #make a POST Call
      urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.vw_url)
      vw_url = urlprops[0].vw_url if(len(urlprops) > 0) else ""
      
      vw_url = vw_url + "calculateVoucher"
      resp = requests.post(vw_url,json=reqobj)
      voucher_message = ""
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
        rspobj1 = resp.json()    
        if(int(common.getkeyvalue(rspobj1,"RETURN_CODE","1")) == 1):
          rspobj["result"] = "success"
          rspobj["error_message"]  = ""
          rspobj["discount_amount"] = rspobj1["discountAmount"]
          rspobj["voucher_code"] = common.getkeyvalue(avars,"voucher_code","")
          if(rspobj1["discountAmount"] > 0):
            rspobj["voucher_message"] = "Voucher Discount = " + str(rspobj["discount_amount"])
          else:
            rspobj["voucher_message"] = "Voucher Discount is cashback into SUPER and MDP wallets"
            
          

          #update discount_amount, voucher_code in treatment, treatmentplan, treatment_procedure 
          discount_amount = float(common.getkeyvalue(rspobj,"discount_amount","0"))
          voucher_code = common.getkeyvalue(rspobj,"voucher_code","")
          totaldiscount_amount = discount_amount
          
          db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).update(discount_amount = discount_amount,voucher_code=voucher_code )
          db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).update(totaldiscount_amount = totaldiscount_amount, voucher_code=voucher_code)
          db.commit()          
          
        else:
          mssg = "Error Calculate Voucher - Invalid Voucher " + json.dumps(rspobj)
          voucher_message =  "Error Calculate Voucher - Invalid Voucher "
          rspobj["voucher_code"] = common.getkeyvalue(avars,"voucher_code","")
          rspobj["voucher_message"] = voucher_message
          rspobj["discount_amount"] = 0
          rspobj["result"] = "fail"
          rspobj["error_message"] = mssg
          
      else:
        mssg = "Calculate Voucher Response Error:\n" + str(resp.status_code)
        logger.loggerpms2.info(mssg)      
        rspobj = {}
        rspobj["voucher_code"] = common.getkeyvalue(avars,"voucher_code","")
        rspobj["voucher_message"] = mssg
        rspobj["discount_amount"] = 0
        rspobj["result"] = "fail"
        rspobj["error_message"] = mssg
            
    except Exception as e:
      mssg = "Calculate Voucher  Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      rspobj = {}
      rspobj["voucher_code"] = common.getkeyvalue(avars,"voucher_code","")
      rspobj["voucher_message"] = mssg
      rspobj["discount_amount"] = 0
      rspobj["result"] = "fail"
      rspobj["error_message"] = mssg
    
    paymentid = 0 #payment id is not required in _updatetreatmentpayment
    account._updatetreatmentpayment(db, tplanid, 0)  
    paytm = json.loads(account._calculatepayments(db, tplanid,common.getkeyvalue(avars,"plan_code","") ) )
    
    
    rspobj["treatmentcost"]=common.getkeyvalue(paytm,"treatmentcost",0)
    rspobj["copay"]=common.getkeyvalue(paytm,"copay",0)
    rspobj["inspays"]=common.getkeyvalue(paytm,"inspays",0)
    rspobj["companypays"]=common.getkeyvalue(paytm,"companypays",0)
    rspobj["walletamount"]=common.getkeyvalue(paytm,"walletamount",0)
    rspobj["discount_amount"]=common.getkeyvalue(paytm,"discount_amount",0)
    rspobj["totaltreatmentcost"]=common.getkeyvalue(paytm,"totaltreatmentcost",0)
    rspobj["totalinspays"]=common.getkeyvalue(paytm,"totalinspays",0)
    rspobj["totalcopay"]=common.getkeyvalue(paytm,"totalcopay",0)
    rspobj["totalpaid"]=common.getkeyvalue(paytm,"totalpaid",0)
    rspobj["totaldue"]=common.getkeyvalue(paytm,"totaldue",0)
    rspobj["totalcompanypays"]=common.getkeyvalue(paytm,"totalcompanypays",0)
    rspobj["precopay"]=common.getkeyvalue(paytm,"precopay",0)
    rspobj["totalprecopay"]=common.getkeyvalue(paytm,"totalprecopay",0)
    rspobj["totalwalletamount"]=common.getkeyvalue(paytm,"totalwalletamount",0)
    rspobj["totaldiscount_amount"]=common.getkeyvalue(paytm,"totaldiscount_amount",0)
    
    mssg = json.dumps(rspobj)
    logger.loggerpms2.info("Exit Calculate Voucher " + mssg)
    return mssg
  
  
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
      if(benefit_master_id == 0):
        rspobj = {}
        rspobj["result"] = "success"
        rspobj["error_message"] = ""
        return json.dumps(rspobj)
      
      db.benefit_master_x_member.update_or_insert((db.benefit_master_x_member.member_id == memberid) & \
                                                  (db.benefit_master_x_member.benefit_master_id == benefit_master_id) &\
                                                  (db.benefit_master_x_member.plan_code == policy),
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

    logger.loggerpms2.info("Enter get_benefits API " + json.dumps(avars))
    db = self.db
    rspobj = {}
    
    try:

      plancode = common.getkeyvalue(avars,"plan_code","")
      
      #region regiond code      
      providerid = int(common.getid(common.getkeyvalue(avars,"provider_id","0")))
      prov = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.city)
      regionid = int(common.getid(provs[0].groupregion)) if(len(provs) == 1) else 1
      regions = db((db.groupregion.id == regionid) & (db.groupregion.is_active == True)).select(db.groupregion.groupregion)
      regioncode = common.getstring(regions[0].groupregion) if(len(regions) == 1) else "ALL"     

      #get company code
      memberid = int(common.getid(common.getkeyvalue(avars,"member_id","0")))
      pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == memberid)).\
        select(db.vw_memberpatientlist.company,db.vw_memberpatientlist.hmoplan,db.vw_memberpatientlist.premstartdt,\
               db.vw_memberpatientlist.premenddt)
      
      #companyid = int(common.getid(pats[0].company)) if(len(pats) == 1) else 0
      #companys = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
      #companycode = common.getstring(companys[0].company) if(len(companys) == 1) else "PREMWALKIN"
      
      #get hmoplan code
      #hmoplanid = int(common.getid(pats[0].hmoplan)) if(len(pats) == 1) else 0  #this is the patient's previously assigned plan-typically at registration
      #hmoplans = db((db.hmoplan.id == hmoplanid) & (db.hmoplan.is_active == True)).select(db.hmoplan.hmoplancode,db.hmoplan.procedurepriceplancode)
      #hmoplancode = common.getstring(hmoplans[0].hmoplancode) if(len(hmoplans) == 1) else "PREMWALKIN"
      #r = db(
             #(db.provider_region_plan.companycode == companycode) &\
             #(db.provider_region_plan.plancode == plancode) &\
             #((db.provider_region_plan.regioncode == regioncode)|(db.provider_region_plan.regioncode == 'ALL'))).select()
      #policy = r[0].policy if(len(r) == 1) else "PREMWALKIN"
  
      bms = db((db.benefit_master_x_member.member_id == memberid) & (db.benefit_master_x_member.plan_code == plancode) &\
             (db.benefit_master.is_valid == True) & (db.benefit_master.is_active == True)).select(db.benefit_master.ALL,\
                                                                                                  left=db.benefit_master.on(db.benefit_master.id == db.benefit_master_x_member.benefit_master_id))
      bmid = bms[0].id if(len(bms)==1) else 0
      logger.loggerpms2.info("Enter Get Benefits 1==>>" + str(len(bms)))

      #select benefit_master_slabs.* from benefit_master_x_slabs
      #left join benefit_master_slabs  on benefit_master_slabs.id = benefit_master_x_slabs.benefit_master_slabs_id
      #where benefit_master_x_slabs.benefit_master_id = 1 and benefit_master_x_slabs.benefit_master_code = 'RPIP599'
      slbs = db((db.benefit_master_x_slabs.benefit_master_id == bmid)&(db.benefit_master_x_slabs.benefit_master_code==policy)).\
        select(db.benefit_master_slabs.ALL,left=db.benefit_master_slabs.on(db.benefit_master_slabs.id == db.benefit_master_x_slabs.benefit_master_slabs_id))
      
      
      #benefit start date & benefit end date
      benefit_start_date = pats[0].premstartdt if(len(pats)==1) else common.getISTCurrentLocatTime()
      benefit_end_date = pats[0].benefit_end_date if(len(pats)==1) else common.getISTCurrentLocatTime()
      
      #benefit value of the Plan 
      benefit_value = common.getvalue(bms[0].benefit_value if (len(bms) == 1) else 0)

      #determine total benefit redeemed for this plan & period
      total_redeemed_benefits = 0
      rbs = db((db.benefit_member.member_id == memberid) & (db.benefit_member.plan_code==policy)&\
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
        rspobj["discount_amount"] = "0"
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
      mssg = "Get Bnefits  Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)     
    
    logger.loggerpms2.info("Exit get_benefits " + json.dumps(rspobj))
    
    return json.dumps(rspobj)

  def xget_benefits(self,avars):
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
                     (db.provider_region_plan.is_active == True)).select() 
      
      #prp = db((db.provider_region_plan.companycode == companycode) &\
                     #(db.provider_region_plan.regioncode == regioncode) &\
                     #(db.provider_region_plan.plancode == hmoplancode) &\
                     #(db.provider_region_plan.is_active == True)).select() 
      
      
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

  
  def get_benefits_kytc(self,avars):
      logger.loggerpms2.info("Enter get_benefits for KYTC " + json.dumps(avars))
      db = self.db
      rspobj = {}
      
      try:
        m = db((db.patientmember.groupref == "KYTC")&(db.patientmember.is_active == True)).select(db.patientmember.id)
        avars["memberid"] = m[0].id if(len(m) > 0) else 0
        plan = common.getkeyvalue(avars,"plan","RPIP599")
        if(plan == "RPIP599"):
          rspobj = json.loads(self.RPIP599_kytc(avars))
        else:
          mssg = "Get Benefits:Invalid benefit KYTC Policy"
          rspobj = {}
          rspobj["result"] = "success"
          rspobj["error_message"] = mssg
          rspobj["redeem_code"] = "BNFT_INVALID"
          rspobj["redeem_value"] = 0
          rspobj["redeem_date"] = common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")
          rspobj["redeem_message"] = common.getmessage(db,"BNFT_INVALID")
          rspobj["memberid"] = common.getkeyvalue(avars,"memberid","")
          rspobj["plan"] = plan
       
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
      
      logger.loggerpms2.info("Exit get_benefits KYTC " + json.dumps(rspobj))
      
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
      if(discount_amount >= 0):
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

  #call with paymentid
  def voucher_success(self, avars):
    logger.loggerpms2.info("Enter Voucher Success " + json.dumps(avars))
    
    db = self.db
    reqobj = {}
    
    rspobj = {}
    
    try:
      paymentid = int(common.getkeyvalue(avars,"paymentid","0"))
      p = db((db.payment.id == paymentid) & (db.payment.is_active == True)).select()
      voucher = common.getstring(p[0].voucher_code) if(len(p) > 0) else ""
      memberid = int(p[0].patientmember) if(len(p)>0) else 0
      tplanid = int(p[0].treatmentplan) if(len(p)>0) else 0
      tp = db(db.treatmentplan.id == tplanid).select()
      totalcopay = (tp[0].totalcopay-tp[0].totaldiscount_amount - tp[0].totalwalletamount) if (len(tp) > 0 ) else 0
      
      tr = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
      treatmentid = int(tr[0].id) if(len(tr)>0) else 0
      amount = (tr[0].copay - tr[0].discount_amount - tr[0].companypay-tr[0].walletamount) if (len(tr) > 0) else 0
      
      members = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.patientmember.company,db.patientmember.city,db.patientmember.st)
      companyid = common.getid(members[0].company) if (len(members) == 1) else "0"
      c = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
      companycode = c[0].company if (len(c) ==1) else ""
  
      cp = db(db.companypolicy.companycode == companycode).select()
      plan = cp[0].policy if(len(cp) != 0) else ""      
      
      #determine member's city & state
      city = members[0].city if(len(members)>0) else "Jaipur"
      st = members[0].st if(len(members)>0) else "Rajasthan (RJ)"
      c = db(db.cities.city == city).select(db.cities.id)
      cityid = c[0].id if(len(c) > 0) else 0 
      
      
      ##reset discount_amount in treatment, treatmentplan, treatment_procedure, payment
      db.redeem_voucher_wallet.insert(
        treatmentid = treatmentid,
        treatmentdate = tr[0].startdate if (len(tr) > 0) else datetime.datetime.now(),
        paymentid = paymentid,
        paymentdate = p[0].paymentdate if (len(p) > 0) else datetime.datetime.now(),
        discount_amount = tr[0].discount_amount if (len(tr) > 0) else 0,
        voucher_code = tr[0].voucher_code if (len(tr) > 0) else "",
        wallet_amount = tr[0].walletamount if (len(tr) > 0) else 0
      )
      
      #db((db.treatment.id == treatmentid)&(db.treatment.is_active == True)).update(copay=amount,discount_amount = 0,voucher_code="")
      #db((db.treatmentplan.id == tplanid)&(db.treatmentplan.is_active == True)).update(totalcopay=totalcopay,totaldiscount_amount = 0,voucher_code = "")
      #db((db.payment.id == paymentid)&(db.payment.is_active == True)).update(discount_amount = 0, voucher_code = "")
      #db.commit()
      
      lst = []
    
      trobj = {}
      trobj["id"] = int(treatmentid)
      trobj["orderAmount"] = amount
      lst = lst.append(trobj)
      

      reqobj["action"] = "calculatediscount"
      reqobj["treatment_ids"] = lst
      reqobj["voucherCode"] = voucher
      reqobj["customerId"] = int(memberid)
      reqobj["region"] = st
      reqobj["city"] = int(cityid)
      reqobj["plan_code"] = plan
      reqobj["wallet_usase"] ={}

      #make a POST Call
      logger.loggerpms2.info("Voucher_Success - Verifying valid voucher " + voucher)
      if((voucher == "") | (voucher == None)):
        rspobj={}
        rspobj["result"] = "success"
        rspobj["error_message"]  = ""
        rspobj["voucher_code"] = voucher
        rspobj["voucher_message"] = ""
        logger.loggerpms2.info("Exit Voucher Success - No Voucher " + json.dumps(rspobj))
        return json.dumps(rspobj)
                
      urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.vw_url)
      vw_url = urlprops[0].vw_url if(len(urlprops) > 0) else ""
      
      vw_url = vw_url + "calculateVoucher"
      resp = requests.post(vw_url,json=reqobj)

      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
        rspobj = resp.json()    
        
        if(rspobj["RETURN_CODE"] != 1):
          mssg = "Redeem Voucher Error: " + json.dumps(rspobj)
          logger.loggerpms2.info(mssg)      
          rspobj = {}
          rspobj["voucher_code"] = voucher
          rspobj["voucher_message"] = rspobj["RETURN_MESSAGE"]
          rspobj["result"] = "fail"
          rspobj["error_message"] = mssg
          return json.dumps(rspobj)     
        
        rspobj["result"] = "success"
        rspobj["error_message"]  = ""
        
        rspobj["voucher_code"] = voucher
        rspobj["voucher_message"] = rspobj["RETURN_MESSAGE"]
      else:
        mssg = "Redeem Voucher Response Error:\n" + str(resp.status_code)
        logger.loggerpms2.info(mssg)      
        rspobj = {}
        
        rspobj["voucher_code"] = voucher
        rspobj["voucher_message"] = mssg
        rspobj["result"] = "fail"
        rspobj["error_message"] = mssg
        return json.dumps(rspobj)

    except Exception as e:
        mssg = "Voucher Success Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)     
      
    logger.loggerpms2.info("Exit Voucher Success " + json.dumps(avars))
    return json.dumps(rspobj)    
  
  #call with paymentid
  def voucher_failure(self, avars):
    logger.loggerpms2.info("Enter Voucher Failure " + json.dumps(avars))
    db = self.db
    reqobj = {}
    rspobj = {}
    
    try:
      paymentid = int(common.getkeyvalue(avars,"paymentid","0"))
      p = db((db.payment.id == paymentid) & (db.payment.is_active == True)).select()
      voucher = p[0].payor if(len(p) > 0) else ""
      memberid = int(p[0].patientmember) if(len(p)>0) else 0
      tplanid = int(p[0].treatmentplan) if(len(p)>0) else 0
      tr = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select(db.treatment.id, db.treatment.copay)
      treatmentid = int(tr[0].id) if(len(tr)>0) else 0
      amount = tr[0].copay if (len(tr) > 0) else 0
        
      members = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.patientmember.company,db.patientmember.city,db.patientmember.st)
      companyid = common.getid(members[0].company) if (len(members) == 1) else "0"
      c = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
      companycode = c[0].company if (len(c) ==1) else ""
  
      cp = db(db.companypolicy.companycode == companycode).select()
      plan = cp[0].policy if(len(cp) != 0) else ""      
      
      #determine member's city & state
      city = members[0].city if(len(members)>0) else "Jaipur"
      st = members[0].st if(len(members)>0) else "Rajasthan (RJ)"
      c = db(db.cities.city == city).select(db.cities.id)
      cityid = c[0].id if(len(c) > 0) else 0 
      
      #Reset companypays = 0 in treatment & treatment plans
      t = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
      tplanid = int(common.getid(t[0].treatmentplan)) if(len(t) > 0) else 0
      db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).update(discount_amount = 0,voucher_code = "")
      db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).update(totalcompanypays=0, voucher_code = 0)
      db((db.payment.id == paymentid) & (db.payment.is_active == True)).update(discount_amount = 0,voucher_code = "")

      rspobj["result"] = "success"
      rspobj["error_message"]  = ""

    except Exception as e:
        mssg = "Voucher Failure Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)     
      
    logger.loggerpms2.info("Exit Voucher Failure " + json.dumps(avars))
    return json.dumps(rspobj)   
  
  
  #call with paymentid
  def wallet_failure(self, avars):
    logger.loggerpms2.info("Enter Wallet Failure " + json.dumps(avars))
    db = self.db
    reqobj = {}
    rspobj = {}
    
    try:
      paymentid = int(common.getkeyvalue(avars,"paymentid","0"))
      p = db((db.payment.id == paymentid) & (db.payment.is_active == True)).select()
      voucher = p[0].payor if(len(p) > 0) else ""
      memberid = int(p[0].patientmember) if(len(p)>0) else 0
      tplanid = int(p[0].treatmentplan) if(len(p)>0) else 0
      tr = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select(db.treatment.id, db.treatment.copay)
      treatmentid = int(tr[0].id) if(len(tr)>0) else 0
      amount = tr[0].copay if (len(tr) > 0) else 0
        
      members = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select(db.patientmember.company,db.patientmember.city,db.patientmember.st)
      companyid = common.getid(members[0].company) if (len(members) == 1) else "0"
      c = db((db.company.id == companyid) & (db.company.is_active == True)).select(db.company.company)
      companycode = c[0].company if (len(c) ==1) else ""
  
      cp = db(db.companypolicy.companycode == companycode).select()
      plan = cp[0].policy if(len(cp) != 0) else ""      
      
      #determine member's city & state
      city = members[0].city if(len(members)>0) else "Jaipur"
      st = members[0].st if(len(members)>0) else "Rajasthan (RJ)"
      c = db(db.cities.city == city).select(db.cities.id)
      cityid = c[0].id if(len(c) > 0) else 0 
      
      #Reset companypays = 0 in treatment & treatment plans
      t = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
      tplanid = int(common.getid(t[0].treatmentplan)) if(len(t) > 0) else 0
      db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).update(discount_amount = 0,voucher_code = "")
      db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).update(totalcompanypays=0, voucher_code = 0)
      db((db.payment.id == paymentid) & (db.payment.is_active == True)).update(discount_amount = 0,voucher_code = "")

      rspobj["result"] = "success"
      rspobj["error_message"]  = ""

    except Exception as e:
        mssg = "Voucher Failure Exception:\n" + str(e)
        logger.loggerpms2.info(mssg)      
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = mssg
        return json.dumps(excpobj)     
      
    logger.loggerpms2.info("Exit Voucher Failure " + json.dumps(avars))
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
      #rbs = db((db.benefit_member.member_id == memberid) & (db.benefit_member.plan_code==policy)&\
               #((db.benefit_member.redeem_date >= benefit_start_date) & (db.benefit_member.redeem_date <= benefit_end_date)) &\
               #(db.benefit_member.is_active == True)).select()
      rbs = db((db.benefit_member.member_id == memberid) & (db.benefit_member.plan_code==policy)&\
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
        rspobj["discount_amount"] = "0"
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
  
  def RPIP599_kytc(self, avars):
    
    logger.loggerpms2.info("Enter RPIP599_KYTC ==>>" + str(avars))
    
    db = self.db
    benefit_obj = {}
    auth = current.auth
    
    
    try:
      plan = common.getkeyvalue(avars,"plan","")   #this is the plan passed from get_benefits
      memberid = int(common.getkeyvalue(avars,"memberid","0"))
      amount = float(common.getkeyvalue(avars,"amount","0"))
    
 
    
      bms = db((db.benefit_master_x_member.member_id == memberid) & (db.benefit_master_x_member.plan_code == plan) &\
             (db.benefit_master.is_valid == True) & (db.benefit_master.is_active == True)).select(db.benefit_master.ALL,\
                                                                                                  left=db.benefit_master.on(db.benefit_master.id == db.benefit_master_x_member.benefit_master_id))
      bmid = bms[0].id if(len(bms)==1) else 0
      logger.loggerpms2.info("Enter RPIP599 KYTC  3==>>" + str(len(bms)))
      
    

      #select benefit_master_slabs.* from benefit_master_x_slabs
      #left join benefit_master_slabs  on benefit_master_slabs.id = benefit_master_x_slabs.benefit_master_slabs_id
      #where benefit_master_x_slabs.benefit_master_id = 1 and benefit_master_x_slabs.benefit_master_code = 'RPIP599'
      slbs = db((db.benefit_master_x_slabs.benefit_master_id == bmid)&(db.benefit_master_x_slabs.benefit_master_code==plan)).\
        select(db.benefit_master_slabs.ALL,left=db.benefit_master_slabs.on(db.benefit_master_slabs.id == db.benefit_master_x_slabs.benefit_master_slabs_id))
      
      
      #benefit start date & benefit end date
      benefit_start_date = bms[0].benefit_start_date if(len(bms)==1) else common.getISTCurrentLocatTime()
      benefit_end_date = bms[0].benefit_end_date if(len(bms)==1) else common.getISTCurrentLocatTime()
      
      #benefit value of the Plan 
      benefit_value = common.getvalue(bms[0].benefit_value if (len(bms) == 1) else 0)

      #determine total benefit redeemed for this plan & period
      total_redeemed_benefits = 0
      
      rbs = db((db.benefit_member.member_id == memberid) & (db.benefit_member.plan_code==plan)&\
               (db.benefit_member.is_active == True)).select()
      
      for rb in rbs:
        total_redeemed_benefits += rb.redeem_amount
        
      #if total redeemed value = max benefit amount, then return
      if(total_redeemed_benefits >= benefit_value):
        
        rspobj = {}
        rspobj["result"] = "success"
        rspobj["error_message"] = ""
        rspobj["total_redeemed_benefits"] = str(total_redeemed_benefits)
        rspobj["benefit_code"] = (bms[0].benefit_code if (len(bms) == 1) else "")
        rspobj["benefit_name"] = (bms[0].benefit_name if (len(bms) == 1) else "")
        rspobj["benefit_value"] = str(benefit_value)
        rspobj["benefit_start_date"] = common.getstringfromdate(benefit_start_date,"%d/%m/%Y")
        rspobj["benefit_end_date"] = common.getstringfromdate(benefit_end_date,"%d/%m/%Y")
        rspobj["benefit_error_code"] = "BNFT_VAL_MAX"
        rspobj["benefit_amount"] = "0"
        rspobj["benefit_date"] = common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")
        rspobj["benefit_message"] = common.getmessage(db,"BNFT_VAL_MAX")
        
        logger.loggerpms2.info("Maximum Benefit Reached (KYTC) " + json.dumps(rspobj))
        return json.dumps(rspobj)
      
      
   
      totalamountforbenefit = amount
      
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
     
      
      
      #return rspobj
      benefit_obj = {}
      benefit_obj["result"] = "success"
      benefit_obj["error_message"] = ""
     
      
      benefit_obj["benefit_value"] = str(benefit_value)
 
      benefit_obj["benefit_code"] = "BNFT_OK"
      benefit_obj["benefit_amount"] = str(benefit_amount)
      benefit_obj["benefit_date"] = common.getstringfromdate(datetime.date.today(), "%d/%m/%Y")
      benefit_obj["benefit_message"] = common.getmessage(db,"BNFT_OK")

    except Exception as e:
      mssg = "RPIP599 KYTC  Exception:\n" + str(e)
      logger.loggerpms2.info(mssg)      
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = mssg
      return json.dumps(excpobj)     
  
    logger.loggerpms2.info("Exit from RPIP599 KYTC Benefit " + json.dumps(benefit_obj))
    return json.dumps(benefit_obj)  