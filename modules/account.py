import json
import datetime
import hashlib
import md5
import common
from applications.my_pms2.modules import logger
#
def assignedPatients(db,providerid):

    sql = " SELECT  patientmember.patientmember, patientmember.fname, patientmember.lname, patientmember.cell, patientmember.dob,company.company FROM patientmember "
    sql = sql + " LEFT JOIN company on patientmember.company = company.id "
    sql = sql + " WHERE patientmember.hmopatientmember = 'T' AND patientmember.is_active = 'T' AND patientmember.provider = " + str(providerid)
    sql = sql + " UNION "
    sql = sql + " SELECT patientmember.patientmember, patientmemberdependants.fname, patientmemberdependants.lname, patientmember.cell, patientmemberdependants.depdob as dob,company.company from patientmemberdependants"
    sql = sql + " left join patientmember on patientmemberdependants.patientmember  = patientmember.id "
    sql = sql + " left join company on company.id = patientmember.company  "
    sql = sql + " WHERE patientmember.hmopatientmember = 'T' AND  patientmember.is_active = 'T' AND patientmember.provider = " + str(providerid)
    sql = sql + " ORDER BY lname"

    ds = db.executesql(sql)


    patients  = len(ds)
    return patients


def assignedGroups(db,agentid):

    rows = db(db.company.agent == agentid).select()

    groups = len(rows)

    return groups

def agentYTD(db, agentid):

    today = datetime.date.today()

    year  = today.year
    month = today.month
    onedaydelta = datetime.timedelta(days=1)

    premiumstartdate      = datetime.date(year,1,1)  ## start of plan period
    premiumenddate        = datetime.date(year,12,31) ## end of plan period
    premiumlastmonthdate  = datetime.date(today.year,today.month,1) - onedaydelta

    ### get a list of all the companies represented by this agetn
    groups = db((db.company.agent == agentid) & (db.company.is_active==True)).select()

    YTD = 0
    premiumamount = 0

    ### get a list of all the employees of this Group
    for group in groups:
        commission = group.commission
        premiumamount = 0
        ## Get the plan rate
        planid    = group.hmoplan
        rates     = db((db.companyhmoplanrate.company == group.id) & (db.companyhmoplanrate.hmoplan == planid) & (db.companyhmoplanrate.is_active == True)).select()
        employees = db((db.patientmember.company == group.id) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True) &\
                        (db.patientmember.terminationdate > premiumenddate)).select()

        for emp in employees:
            rate = db((db.companyhmoplanrate.company == group.id) & (db.companyhmoplanrate.hmoplan == planid) & (db.companyhmoplanrate.is_active == True) & \
                      (db.companyhmoplanrate.covered == emp.memberorder)).select()

            monthlypremium = 0
            if(len(rate)>0):
                monthlypremium = rate[0].premium


            premiummonths = 1
            if(emp.enrollmentdate.month <= premiumstartdate.month):
                if(premiumlastmonthdate.year <  premiumstartdate.year ):
                    premiummonths = 1
                else:
                    premiummonths = premiumlastmonthdate.month - premiumstartdate.month + 1
            else:
                if(premiumlastmonthdate.year <  premiumstartdate.year ):
                    premiummonths = 1
                else:
                    premiummonths = premiumlastmonthdate.month - emp.enrollmentdate.month + 1

            premiumamount = premiumamount + (monthlypremium * premiummonths)

            dependants = db((db.patientmemberdependants.patientmember == emp.id) & (db.patientmemberdependants.is_active == True)).select()

            for dep in dependants:
                rate = db((db.companyhmoplanrate.company == group.id) & (db.companyhmoplanrate.hmoplan == planid) & (db.companyhmoplanrate.is_active == True) & \
                                     (db.companyhmoplanrate.covered == dep.memberorder)).select()


                monthlypremium = 0
                if(len(rate)>0):
                    monthlypremium = rate[0].premium



                premiummonths = 1
                if(emp.enrollmentdate.month <= premiumstartdate.month):
                    if(premiumlastmonthdate.year <  premiumstartdate.year ):
                        premiummonths = 1
                    else:
                        premiummonths = premiumlastmonthdate.month - premiumstartdate.month + 1
                else:
                    if(premiumlastmonthdate.year <  premiumstartdate.year ):
                        premiummonths = 1
                    else:
                        premiummonths = premiumlastmonthdate.month - emp.enrollmentdate.month + 1

                premiumamount = premiumamount + (monthlypremium * premiummonths)

        YTD = YTD + (premiumamount * commission) / 100

    return YTD


def agentMTD(db, agentid):

    today = datetime.date.today()

    year  = today.year
    month = today.month
    onedaydelta = datetime.timedelta(days=1)

    premiumstartdate      = datetime.date(year,1,1)  ## start of plan period
    premiumenddate        = datetime.date(year,12,31) ## end of plan period
    premiumlastmonthdate  = datetime.date(today.year,today.month,1) - onedaydelta

    ### get a list of all the companies represented by this agetn
    groups = db((db.company.agent == agentid) & (db.company.is_active==True)).select()

    MTD = 0
    premiumamount = 0

    ### get a list of all the employees of this Group
    for group in groups:
        commission = group.commission
        premiumamount = 0

        ## Get the plan rate
        planid    = group.hmoplan
        rates     = db((db.companyhmoplanrate.company == group.id) & (db.companyhmoplanrate.hmoplan == planid) & (db.companyhmoplanrate.is_active == True)).select()
        employees = db((db.patientmember.company == group.id) & (db.patientmember.is_active == True)  & (db.patientmember.hmopatientmember == True) & \
                        (db.patientmember.terminationdate > premiumlastmonthdate)).select()



        for emp in employees:
            rate = db((db.companyhmoplanrate.company == group.id) & (db.companyhmoplanrate.hmoplan == planid) & (db.companyhmoplanrate.is_active == True) & \
                      (db.companyhmoplanrate.covered == emp.memberorder)).select()

            monthlypremium = 0
            if(len(rate)>0):
                monthlypremium = rate[0].premium


            premiummonths = 1
            premiumamount = premiumamount + (monthlypremium * premiummonths)

            dependants = db((db.patientmemberdependants.patientmember == emp.id) & (db.patientmemberdependants.is_active == True)).select()

            for dep in dependants:
                rate = db((db.companyhmoplanrate.company == group.id) & (db.companyhmoplanrate.hmoplan == planid) & (db.companyhmoplanrate.is_active == True) & \
                                     (db.companyhmoplanrate.covered == dep.memberorder)).select()

                monthlypremium = 0
                if(len(rate)>0):
                    monthlypremium = rate[0].premium
                premiummonths = 1
                premiumamount = premiumamount + (monthlypremium * premiummonths)

        MTD= MTD + (premiumamount * commission) / 100

    return MTD

def capitationYTD(db,providerid):

    today = datetime.date.today()

    year  = today.year
    month = today.month
    onedaydelta = datetime.timedelta(days=1)

    capstartdate      = datetime.date(year,1,1)  ## start of plan period
    capenddate        = datetime.date(year,12,31) ## end of plan period
    caplastmonthdate  = datetime.date(today.year,today.month,1) - onedaydelta

    YTD = 0
    capamount = 0

    employees = db((db.patientmember.provider == providerid) & (db.patientmember.is_active == True) & \
                    (db.patientmember.hmopatientmember == True) & (db.patientmember.terminationdate > capenddate)).select()

    for emp in employees:
        capamount = 0

        planid = emp.hmoplan

        rate   = db((db.companyhmoplanrate.company == emp.company) & (db.companyhmoplanrate.hmoplan == planid) & (db.companyhmoplanrate.is_active == True) & \
                  (db.companyhmoplanrate.relation == 'Self')).select()

        monthlycap  = 0
        if(len(rate) > 0):
            monthlycap = rate[0].capitation
        capmmonths = 1
        if(emp.enrollmentdate.month <= capstartdate.month):
            if(caplastmonthdate.year <  capstartdate.year ):
                capmmonths = 1
            else:
                capmmonths = caplastmonthdate.month - capstartdate.month + 1
        else:
            if(caplastmonthdate.year <  capstartdate.year ):
                capmmonths = 1
            else:
                capmmonths = caplastmonthdate.month - emp.enrollmentdate.month +1

        capamount = capamount + (monthlycap * capmmonths)

        dependants = db((db.patientmemberdependants.patientmember == emp.id) & (db.patientmemberdependants.is_active == True)).select()

        for dep in dependants:
            rate = db((db.companyhmoplanrate.company == emp.company) & (db.companyhmoplanrate.hmoplan == planid) & (db.companyhmoplanrate.is_active == True) & \
                                 (db.companyhmoplanrate.relation == dep.relation)).select()
            monthlycap = 0
            if(len(rate) > 0):
                monthlycap = rate[0].capitation

            capmonths = 1
            if(emp.enrollmentdate.month <= capstartdate.month):
                if(caplastmonthdate.year <  capstartdate.year ):
                    capmonths = 1
                else:
                    capmonths = caplastmonthdate.month - capstartdate.month + 1
            else:
                if(caplastmonthdate.year <  capstartdate.year ):
                    capmonths = 0
                else:
                    capmonths = caplastmonthdate.month - emp.enrollmentdate.month +1

            capamount = capamount + (monthlycap * capmonths)

        YTD = YTD + capamount

    return YTD

def capitationMTD(db,providerid):

    today = datetime.date.today()

    year  = today.year
    month = today.month
    onedaydelta = datetime.timedelta(days=1)

    capstartdate      = datetime.date(year,1,1)  ## start of plan period
    capenddate        = datetime.date(year,12,31) ## end of plan period
    caplastmonthdate  = datetime.date(today.year,today.month,1) - onedaydelta

    MTD = 0
    capamount = 0

    employees = db((db.patientmember.provider == providerid) & (db.patientmember.is_active == True) & \
                    (db.patientmember.hmopatientmember == True)&(db.patientmember.terminationdate > caplastmonthdate)).select()
    for emp in employees:
        capamount = 0
        planid = emp.hmoplan
        rate   = db((db.companyhmoplanrate.company == emp.company) & (db.companyhmoplanrate.hmoplan == planid) & (db.companyhmoplanrate.is_active == True) & \
                  (db.companyhmoplanrate.covered == emp.memberorder)).select()

        monthlycap = 0
        if(len(rate)>0):
            monthlycap = rate[0].capitation
        capmmonths = 1
        capamount = capamount + (monthlycap * capmmonths)

        dependants = db((db.patientmemberdependants.patientmember == emp.id) & (db.patientmemberdependants.is_active == True)).select()

        for dep in dependants:
            rate = db((db.companyhmoplanrate.company == emp.company) & (db.companyhmoplanrate.hmoplan == planid) & (db.companyhmoplanrate.is_active == True) & \
                                 (db.companyhmoplanrate.relation == dep.relation)).select()
            monthlycap = 0
            if(len(rate)>0):
                monthlycap = rate[0].capitation
            capmonths = 1
            capamount = capamount + (monthlycap * capmonths)

        MTD = MTD + capamount

    return MTD


def setmemberpremiumdatesbyagent(db,agentid, startdate,enddate):

    ds = db((db.patientmember.is_active == True)   & (db.patientmember.hmopatientmember == True)& (db.agent.id == agentid)).select(
          left = [db.company.on(db.company.id==db.patientmember.company),db.agent.on(db.agent.id == db.company.agent)])

    return dict()




def agentcommissionYTD(db, agentid, startdate, enddate):

    today = datetime.date.today()

    if(today <= enddate):
        enddate = today

    startyear = startdate.year
    startmonth = startdate.month
    startday = startdate.day
    sstartdate = str(startdate.year) + '-' + str(startdate.month) + '-' + str(startdate.day)

    endyear = enddate.year
    endmonth = enddate.month
    endday = enddate.day
    senddate = str(enddate.year) + '-' + str(enddate.month) + '-' + str(enddate.day)

    sql = 'SELECT company, hmoplancode, '
    sql = sql + ' CASE '
    sql = sql + ' WHEN premmonth = 1 THEN \'Jan\' '
    sql = sql + ' WHEN premmonth = 2 THEN \'Feb\' '
    sql = sql + ' WHEN premmonth = 3 THEN \'Mar\' '
    sql = sql + ' WHEN premmonth = 4 THEN \'Apr\' '
    sql = sql + ' WHEN premmonth = 5 THEN \'May\' '
    sql = sql + ' WHEN premmonth = 6 THEN \'Jun\' '
    sql = sql + ' WHEN premmonth = 7 THEN \'Jul\' '
    sql = sql + ' WHEN premmonth = 8 THEN \'Aug\' '
    sql = sql + ' WHEN premmonth = 9 THEN \'Sep\' '
    sql = sql + ' WHEN premmonth = 10 THEN \'Oct\' '
    sql = sql + ' WHEN premmonth = 11 THEN \'Nov\' '
    sql = sql + ' WHEN premmonth = 12 THEN \'Dec\' '
    sql = sql + ' END AS premmonth, '
    sql = sql + ' COUNT(memberorder) AS members,  SUM(premium), SUM(premium * commission/100) AS commission  FROM '
    sql = sql + '( SELECT company.company, hmoplan.hmoplancode,  patientmember.fname, patientmember.memberorder, patientmember.enrollmentdate, patientmember.terminationdate,  patientmember.duedate,'
    sql = sql + ' CASE '
    sql = sql + ' WHEN patientmember.enrollmentdate > date(' +  sstartdate + ') THEN  patientmember.enrollmentdate'
    sql = sql + ' WHEN patientmember.enrollmentdate <= date(' + sstartdate +  ') THEN  date(' + sstartdate + ')'
    sql = sql + ' END AS premstartdt,'
    sql = sql + ' CASE '
    sql = sql + ' WHEN patientmember.terminationdate > date(' + senddate + ') THEN date(' +   senddate + ')'
    sql = sql + ' WHEN patientmember.terminationdate <= date(' + senddate + ') THEN patientmember.terminationdate'
    sql = sql + ' END AS premenddt,'
    sql = sql + ' companyhmoplanrate.premium, '
    sql = sql + ' company.commission '
    sql = sql + ' FROM patientmember LEFT JOIN '
    sql = sql + ' company ON company.id = patientmember.company LEFT JOIN '
    sql = sql + ' hmoplan ON hmoplan.id = company.hmoplan LEFT JOIN '
    sql = sql + ' companyhmoplanrate ON companyhmoplanrate.company = company.id AND companyhmoplanrate.hmoplan = hmoplan.id  LEFT JOIN '
    sql = sql + ' agent ON agent.id = company.agent '
    sql = sql + ' WHERE agent.id = ' + str(agentid) + ' AND patientmember.is_active = \'T\' AND '
    sql = sql + ' patientmember.memberorder = companyhmoplanrate.covered '

    sql = sql + ' UNION '

    sql = sql + 'select company.company, hmoplan.hmoplancode, patientmemberdependants.fname, patientmemberdependants.memberorder, patientmember.enrollmentdate, patientmember.terminationdate,  patientmember.duedate, '
    sql = sql + ' CASE '
    sql = sql + ' WHEN patientmember.enrollmentdate > date('+ sstartdate + ') THEN  patientmember.enrollmentdate'
    sql = sql + ' WHEN patientmember.enrollmentdate <=  date(' +  sstartdate + ') THEN date(' + sstartdate + ')'
    sql = sql + ' END AS premstartdt,'
    sql = sql + ' CASE '
    sql = sql + ' WHEN patientmember.terminationdate > date(' + senddate + ') THEN date(' + senddate + ')'
    sql = sql + ' WHEN patientmember.terminationdate <= date(' + senddate + ') THEN patientmember.terminationdate'
    sql = sql + ' END AS premenddt,'
    sql = sql + ' companyhmoplanrate.premium, company.commission '
    sql = sql + ' FROM  patientmemberdependants LEFT JOIN '
    sql = sql + ' patientmember ON patientmember.id = patientmemberdependants.patientmember LEFT JOIN '
    sql = sql + ' company ON company.id = patientmember.company LEFT JOIN '
    sql = sql + ' hmoplan ON hmoplan.id = company.hmoplan LEFT JOIN '
    sql = sql + ' companyhmoplanrate on companyhmoplanrate.company = company.id AND companyhmoplanrate.hmoplan = hmoplan.id  LEFT JOIN '
    sql = sql + ' agent ON agent.id = company.agent '
    sql = sql + ' WHERE agent.id = ' + str(agentid) + ' and patientmemberdependants.is_active = \'T\' AND '
    sql = sql + ' patientmemberdependants.memberorder = companyhmoplanrate.covered) '
    sql = sql + ' LEFT JOIN '
    sql = sql  + ' monthly ON ( (monthly.premmonth >=  strftime(\'%m\', premstartdt))  AND (monthly.premmonth <  strftime(\'%m\', date(\'now\'))))'
    sql = sql  + ' WHERE  premmonth > 0 AND  (strftime(\'%m\', premstartdt) < strftime(\'%m\', premenddt))'
    sql = sql  + ' GROUP BY  company, premmonth'

    ds = db.executesql(sql)

    ##########
    #sql = 'SELECT company, monthly.premmonth, SUM(premium),    SUM(premium * commission) AS commission  from '
    #sql = sql + '(select company.company, hmoplan.hmoplancode,  patientmember.fname, patientmember.memberorder, patientmember.enrollmentdate, patientmember.terminationdate,  patientmember.duedate,'
    #sql = sql + 'CASE'
    #sql = sql + 'WHEN patientmember.enrollmentdate > ' + startdate + 'THEN  patientmember.enrollmentdate'
    #sql = sql + 'WHEN patientmember.enrollmentdate <= ' + startdate +  'THEN' + startdate
    #sql = sql + 'END AS premstartdt,'
    #sql = sql + 'CASE'
    #sql = sql + 'WHEN patientmember.terminationdate > ' + enddate + 'THEN' +   enddate
    #sql = sql + 'WHEN patientmember.terminationdate <=' + enddate + 'THEN patientmember.terminationdate'
    #sql = sql + 'END AS premenddt,'
    #sql = sql + 'companyhmoplanrate.premium,'
    #sql = sql + 'company.commission'
    #sql = sql + 'from patientmember left join '
    #sql = sql + 'company on company.id = patientmember.company left join'
    #sql = sql + 'hmoplan on hmoplan.id = company.hmoplan left join'
    #sql = sql + 'companyhmoplanrate on companyhmoplanrate.company = company.id AND companyhmoplanrate.hmoplan = hmoplan.id  left join'
    #sql = sql + 'agent on agent.id = company.agent'
    #sql = sql + 'where agent.id = ' + str(agentid) + ' and patientmember.is_active = \'T\' and'
    #sql = sql + 'patientmember.memberorder = companyhmoplanrate.covered'

    #sql = sql + 'UNION'

    #sql = sql + 'select company.company, hmoplan.hmoplancode, patientmemberdependants.fname, patientmemberdependants.memberorder, patientmember.enrollmentdate, patientmember.terminationdate,  patientmember.duedate, '
    #sql = sql + 'CASE '
    #sql = sql + 'WHEN patientmember.enrollmentdate > '+ startdate + ' THEN  patientmember.enrollmentdate'
    #sql = sql + 'WHEN patientmember.enrollmentdate <= ' +  startdate + 'THEN' + startdate
    #sql = sql + 'END AS premstartdt,'
    #sql = sql + 'CASE '
    #sql = sql + 'WHEN patientmember.terminationdate > ' + enddate + 'THEN' + enddate
    #sql = sql + 'WHEN patientmember.terminationdate <= ' + enddate + ' THEN patientmember.terminationdate'
    #sql = sql + 'END AS premenddt,'
    #sql = sql + 'companyhmoplanrate.premium,'
    #sql = sql + 'company.commission'
    #sql = sql + 'from patientmemberdependants left join '
    #sql = sql + 'patientmember on patientmember.id = patientmemberdependants.patientmember left join'
    #sql = sql + 'company on company.id = patientmember.company left join'
    #sql = sql + 'hmoplan on hmoplan.id = company.hmoplan left join'
    #sql = sql + 'companyhmoplanrate on companyhmoplanrate.company = company.id AND companyhmoplanrate.hmoplan = hmoplan.id  left join'
    #sql = sql + 'agent on agent.id = company.agent'
    #sql = sql + 'where agent.id = ' + str(agentid) + ' and patientmemberdependants.is_active = \'T\' and '
    #sql = sql + 'patientmemberdependants.memberorder = companyhmoplanrate.covered) left join'
    #sql = sql + 'monthly on ( (monthly.premmonth >=  strftime(\'%m\', premstartdt))  AND (monthly.premmonth <  strftime(\'%m\', date(\'now\'))))'
    #sql = sql + 'where   (strftime(\'%m\', premstartdt) < strftime(\'%m\', premenddt))'
    #sql = sql + 'group by company, premmonth'

    #SELECT company, monthly.premmonth, SUM(premium),    SUM(premium * commission) AS commission  from\
    #(select company.company, hmoplan.hmoplancode,  patientmember.fname, patientmember.memberorder, patientmember.enrollmentdate, patientmember.terminationdate,  patientmember.duedate, \
    #CASE \
        #WHEN patientmember.enrollmentdate > date(\'2015-01-01\') THEN  patientmember.enrollmentdate\
        #WHEN patientmember.enrollmentdate <= date(\'2015-01-01\') THEN  date(\'2015-01-01\') \
    #END AS premstartdt,\
    #CASE \
        #WHEN patientmember.terminationdate > date(\'now\') THEN  date(\'now\')\
        #WHEN patientmember.terminationdate <= date(\'now\') THEN patientmember.terminationdate\
    #END AS premenddt,\
    #companyhmoplanrate.premium,\
    #company.commission\
    #from patientmember left join \
    #company on company.id = patientmember.company left join\
    #hmoplan on hmoplan.id = company.hmoplan left join\
    #companyhmoplanrate on companyhmoplanrate.company = company.id AND companyhmoplanrate.hmoplan = hmoplan.id  left join\
    #agent on agent.id = company.agent\
    #where agent.id = 1 and patientmember.is_active = \'T\' and\
    #patientmember.memberorder = companyhmoplanrate.covered\

    #UNION\

    #select company.company, hmoplan.hmoplancode, patientmemberdependants.fname, patientmemberdependants.memberorder, patientmember.enrollmentdate, patientmember.terminationdate,  patientmember.duedate, \
    #CASE \
        #WHEN patientmember.enrollmentdate > date('2015-01-01') THEN  patientmember.enrollmentdate\
        #WHEN patientmember.enrollmentdate <= date('2015-01-01') THEN  date('2015-01-01') \
    #END AS premstartdt,\
    #CASE \
        #WHEN patientmember.terminationdate > date('now') THEN  date('now')\
        #WHEN patientmember.terminationdate <= date('now') THEN patientmember.terminationdate\
    #END AS premenddt,\
    #companyhmoplanrate.premium,\
    #company.commission\
    #from patientmemberdependants left join \
    #patientmember on patientmember.id = patientmemberdependants.patientmember left join\
    #company on company.id = patientmember.company left join\
    #hmoplan on hmoplan.id = company.hmoplan left join\
    #companyhmoplanrate on companyhmoplanrate.company = company.id AND companyhmoplanrate.hmoplan = hmoplan.id  left join\
    #agent on agent.id = company.agent\
    #where agent.id = 1 and patientmemberdependants.is_active = \'T\' and\
    #patientmemberdependants.memberorder = companyhmoplanrate.covered) left join\
    #monthly on ( (monthly.premmonth >=  strftime(\'%m\', premstartdt))  AND (monthly.premmonth <  strftime(\'%m\', date(\'now\'))))\
    #where   (strftime(\'%m\', premstartdt) < strftime(\'%m\', premenddt))\
    #group by company, premmonth\'

    return ds


def providercapitationYTD(db, providerid, startdate, enddate):

    today = datetime.date.today()

    if(today <= enddate):
        enddate = today

    startyear = startdate.year
    startmonth = startdate.month
    startday = startdate.day
    sstartdate = str(startdate.year) + '-' + str(startdate.month) + '-' + str(startdate.day)

    endyear = enddate.year
    endmonth = enddate.month
    endday = enddate.day
    senddate = str(enddate.year) + '-' + str(enddate.month) + '-' + str(enddate.day)

    sql = 'SELECT captble.company  as company,captble.hmoplancode AS hmoplancode, '
    sql = sql + ' CASE '
    sql = sql + ' WHEN premmonth = 1 THEN \'Jan\' '
    sql = sql + ' WHEN premmonth = 2 THEN \'Feb\' '
    sql = sql + ' WHEN premmonth = 3 THEN \'Mar\' '
    sql = sql + ' WHEN premmonth = 4 THEN \'Apr\' '
    sql = sql + ' WHEN premmonth = 5 THEN \'May\' '
    sql = sql + ' WHEN premmonth = 6 THEN \'Jun\' '
    sql = sql + ' WHEN premmonth = 7 THEN \'Jul\' '
    sql = sql + ' WHEN premmonth = 8 THEN \'Aug\' '
    sql = sql + ' WHEN premmonth = 9 THEN \'Sep\' '
    sql = sql + ' WHEN premmonth = 10 THEN \'Oct\' '
    sql = sql + ' WHEN premmonth = 11 THEN \'Nov\' '
    sql = sql + ' WHEN premmonth = 12 THEN \'Dec\' '
    sql = sql + ' END AS premmonth, '
    sql = sql + ' COUNT(captble.memberorder) AS members,  SUM(captble.capitation) AS capitation  FROM '
    sql = sql + '( SELECT company.company, hmoplan.hmoplancode,  patientmember.fname, patientmember.memberorder, patientmember.enrollmentdate, patientmember.terminationdate,  patientmember.duedate,'
    sql = sql + ' CASE '
    sql = sql + ' WHEN patientmember.premstartdt > date(\' ' +  sstartdate + ' \') THEN  patientmember.premstartdt'
    sql = sql + ' WHEN patientmember.premstartdt <= date(\' ' + sstartdate +  ' \') THEN  date(\'' + sstartdate + '\')'
    sql = sql + ' END AS premstartdt,'
    sql = sql + ' CASE '
    sql = sql + ' WHEN patientmember.premenddt > date(\' ' + senddate + ' \') THEN date(\'' +   senddate + '\')'
    sql = sql + ' WHEN patientmember.premenddt <= date(\' ' + senddate + ' \') THEN patientmember.premenddt'
    sql = sql + ' END AS premenddt,'
    sql = sql + ' companyhmoplanrate.capitation '
    sql = sql + ' FROM patientmember LEFT JOIN '
    sql = sql + ' company ON company.id = patientmember.company LEFT JOIN '
    sql = sql + ' hmoplan ON hmoplan.id = company.hmoplan LEFT JOIN '
    sql = sql + ' companyhmoplanrate ON companyhmoplanrate.company = company.id AND companyhmoplanrate.hmoplan = hmoplan.id   '
    sql = sql + ' WHERE patientmember.provider = ' + str(providerid) + ' AND patientmember.is_active = \'T\' AND '
    sql = sql + ' patientmember.memberorder = companyhmoplanrate.covered '

    sql = sql + ' UNION '

    sql = sql + ' select company.company, hmoplan.hmoplancode, patientmemberdependants.fname, patientmemberdependants.memberorder, patientmember.enrollmentdate, patientmember.terminationdate,  patientmember.duedate, '
    sql = sql + ' CASE '
    sql = sql + ' WHEN patientmember.premstartdt > date(\' ' + sstartdate + ' \') THEN  patientmember.premstartdt'
    sql = sql + ' WHEN patientmember.premstartdt <=  date(\''  +  sstartdate + ' \') THEN date(\' '  + sstartdate + ' \')'
    sql = sql + ' END AS premstartdt,'
    sql = sql + ' CASE '
    sql = sql + ' WHEN patientmember.premenddt > date(\'' + senddate + '\') THEN date(\'' + senddate + ' \')'
    sql = sql + ' WHEN patientmember.premenddt <= date(\'' + senddate + '\') THEN patientmember.premenddt'
    sql = sql + ' END AS premenddt,'
    sql = sql + ' companyhmoplanrate.capitation '
    sql = sql + ' FROM  patientmemberdependants LEFT JOIN '
    sql = sql + ' patientmember ON patientmember.id = patientmemberdependants.patientmember LEFT JOIN '
    sql = sql + ' company ON company.id = patientmember.company LEFT JOIN '
    sql = sql + ' hmoplan ON hmoplan.id = company.hmoplan LEFT JOIN '
    sql = sql + ' companyhmoplanrate on companyhmoplanrate.company = company.id AND companyhmoplanrate.hmoplan = hmoplan.id '
    sql = sql + ' WHERE patientmember.provider = ' + str(providerid) + ' and patientmemberdependants.is_active = \'T\' AND '
    sql = sql + ' patientmemberdependants.memberorder = companyhmoplanrate.covered) AS captble '
    sql = sql + ' LEFT JOIN '
    sql = sql  + ' monthly ON ( (monthly.premmonth >=  date_format(premstartdt,\'%m\'))  AND (monthly.premmonth <  date_format(now(),\'%m\')))'
    #sql = sql  + ' WHERE  premmonth > 0 AND  (date_format(premstartdt,\'%m\') < date_format(premenddt,\'%m\'))'
    sql = sql  + ' GROUP BY  company, premmonth'


    # The following commented query is used in Jasper Reports Query
    #sql = sql + "SELECT 'P' AS pattype, company.company, hmoplan.hmoplancode,  patientmember.fname, patientmember.lname, "
    #sql = sql + "patientmember.patientmember, patientmember.enrollmentdate, patientmember.created_on,  "
    #sql = sql + "CASE  WHEN patientmember.enrollmentdate > date($P{startDt_ds}) THEN  patientmember.enrollmentdate WHEN patientmember.enrollmentdate <= date($P{startDt_ds})"
    #sql = sql + "THEN  date($P{startDt_ds}) END AS premstartdt, "
    #sql = sql + "CASE  WHEN patientmember.terminationdate > date($P{endDt_ds}) THEN date($P{endDt_ds})"
    #sql = sql + "WHEN patientmember.terminationdate <= date($P{endDt_ds}) THEN patientmember.terminationdate END AS premenddt,"
    #sql = sql + "'Self' AS relation, companyhmoplanrate.premium, companyhmoplanrate.capitation "
    #sql = sql + "FROM patientmember LEFT JOIN  company ON company.id = patientmember.company"
    #sql = sql + "LEFT JOIN  hmoplan ON hmoplan.id = company.hmoplan "
    #sql = sql + "LEFT JOIN  companyhmoplanrate ON companyhmoplanrate.company = company.id AND companyhmoplanrate.hmoplan = hmoplan.id   "
    #sql = sql + "WHERE patientmember.provider = $P{providerid_ds} AND patientmember.is_active = 'T' AND  companyhmoplanrate.relation = 'Self'"
    #sql = sql + "UNION  "
    #sql = sql + "select 'D' As pattype, company.company, hmoplan.hmoplancode, patientmemberdependants.fname,patientmemberdependants.lname, "
    #sql = sql + "patientmember.patientmember,patientmember.enrollmentdate, patientmember.created_on,  "
    #sql = sql + "CASE  WHEN patientmember.enrollmentdate > date($P{startDt_ds}) THEN  patientmember.enrollmentdate WHEN patientmember.enrollmentdate <=  date($P{startDt_ds}) "
    #sql = sql + "THEN date($P{startDt_ds}) END AS premstartdt, CASE  WHEN patientmember.terminationdate > date($P{endDt_ds}) THEN date($P{endDt_ds}) "
    #sql = sql + "WHEN patientmember.terminationdate <= date($P{endDt_ds}) THEN patientmember.terminationdate END AS premenddt, "
    #sql = sql + "patientmemberdependants.relation, companyhmoplanrate.premium, companyhmoplanrate.capitation  "
    #sql = sql + "FROM  patientmemberdependants "
    #sql = sql + "LEFT JOIN  patientmember ON patientmember.id = patientmemberdependants.patientmember "
    #sql = sql + "LEFT JOIN  company ON company.id = patientmember.company "
    #sql = sql + "LEFT JOIN  hmoplan ON hmoplan.id = company.hmoplan "
    #sql = sql + "LEFT JOIN  companyhmoplanrate on companyhmoplanrate.company = company.id AND companyhmoplanrate.hmoplan = hmoplan.id  "
    #sql = sql + "WHERE patientmember.provider = $P{providerid_ds} and patientmemberdependants.is_active = 'T' AND  patientmemberdependants.relation = companyhmoplanrate.relation"

    #This is modified report to be used in Jasper Report for Patient-hmoplan
    #SELECT 'P' AS pattype, company.company, hmoplan.hmoplancode,  patientmember.fname, patientmember.lname,
    #patientmember.patientmember, patientmember.enrollmentdate, patientmember.created_on,
    #CASE  WHEN patientmember.enrollmentdate > date('2015-01-01') THEN  patientmember.enrollmentdate
    #WHEN patientmember.enrollmentdate <= date('2015-01-01')
     #THEN  date('2015-01-01') END AS premstartdt,
     #CASE  WHEN patientmember.terminationdate > date('2015-12-31') THEN date('2015-12-31')
      #WHEN patientmember.terminationdate <= date('2015-12-31') THEN patientmember.terminationdate END AS premenddt,
      #'Self' AS relation, companyhmoplanrate.premium, companyhmoplanrate.capitation
       #FROM patientmember LEFT JOIN  company ON company.id = patientmember.company
        #LEFT JOIN  hmoplan ON hmoplan.id = patientmember.hmoplan
        #LEFT JOIN  companyhmoplanrate ON companyhmoplanrate.company = patientmember.company AND companyhmoplanrate.hmoplan = patientmember.hmoplan
         #WHERE patientmember.provider = 112 AND patientmember.is_active = 'T' AND  companyhmoplanrate.relation = 'Self'
     #UNION
     #select 'D' As pattype, company.company, hmoplan.hmoplancode, patientmemberdependants.fname,patientmemberdependants.lname,
     #patientmember.patientmember,patientmember.enrollmentdate, patientmember.created_on,
     #CASE  WHEN patientmember.enrollmentdate > date('2015-01-01') THEN  patientmember.enrollmentdate
     #WHEN patientmember.enrollmentdate <=  date('2015-01-01')
     #THEN date('2015-01-01') END AS premstartdt, CASE  WHEN patientmember.terminationdate > date('2015-12-31') THEN date('2015-12-31')
     #WHEN patientmember.terminationdate <= date('2015-12-31') THEN patientmember.terminationdate END AS premenddt,
      #patientmemberdependants.relation, companyhmoplanrate.premium, companyhmoplanrate.capitation
      #FROM  patientmemberdependants
      #LEFT JOIN  patientmember ON patientmember.id = patientmemberdependants.patientmember
      #LEFT JOIN  company ON company.id = patientmember.company
      #LEFT JOIN  hmoplan ON hmoplan.id = patientmember.hmoplan
      #LEFT JOIN  companyhmoplanrate on companyhmoplanrate.company = patientmember.company AND companyhmoplanrate.hmoplan = patientmember.hmoplan
      #WHERE patientmember.provider =112 and patientmemberdependants.is_active = 'T'
      #AND  patientmemberdependants.relation = companyhmoplanrate.relation

    ds = db.executesql(sql)


    return ds


def generateHash(secret_key,account_id,address,amount,channel,city,country,currency,description,email,mode, \
                name,phone,postal_code,reference_no,return_url,ship_address,ship_city,ship_country,ship_name,ship_phone,ship_postal_code,ship_state,state):
    


    hashdata = secret_key
    hashdata = hashdata + '|' + account_id + '|' + address  + '|' + amount + '|' + channel + '|' + city + '|' + country + '|' + currency + '|' + description + '|' + email
    hashdata = hashdata + '|' + mode + '|' + name + '|' + phone + '|' + postal_code + '|' + reference_no + '|' + return_url + '|' + ship_address + '|' + ship_city + '|' + ship_country
    hashdata = hashdata + '|' + ship_name + '|' + ship_phone + '|' + ship_postal_code + '|' + ship_state + '|' + state




    
    m = hashlib.md5()
    hashkey =  m.update(hashdata)
    hashkey = m.hexdigest()

    return hashkey.upper()

def copayment(db,tplanid,patientid):

    copay     = 0
    sql = "SELECT SUM(copay) as copay FROM treatment WHERE treatmentplan = " + str(tplanid) + " AND is_active = \'T \' "
    ds = db.executesql(sql)
    if(len(ds)>0):
        if(ds[0][0] != None):
            copay = float(ds[0][0])

    #trrows = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
    #for tr in trrows:
        #copay = copay + float(tr.copay)
    return copay


def treatment_cost_copay(db,treatmentid):

    totalcost = 0
    copay = 0

    sql = "select "
    sql = sql + " copay.procedureucrfee, copay.procedurefee, copay.copay "
    sql = sql + " from treatment "
    sql = sql + " left join treatmentplan on treatmentplan.id = treatment.treatmentplan  "
    sql = sql + " left join patientmember on patientmember.id = treatmentplan.primarypatient "
    sql = sql + " left join groupregion on groupregion.id = patientmember.groupregion "
    sql = sql + " left join hmoplan on hmoplan.id = patientmember.hmoplan "
    sql = sql + " left join copay on copay.hmoplan = hmoplan.id AND copay.region = groupregion.id AND copay.dentalprocedure = treatment.dentalprocedure "
    sql = sql + " where treatment.is_active = \'T\' AND treatmentplan.is_active = \'T\' AND patientmember.is_active = \'T\' AND groupregion.is_active = \'T\' AND hmoplan.is_active = \'T\' "
    sql = sql + " AND treatment.id = " + str(treatmentid)

    ds = db.executesql(sql)

    if(len(ds) > 0):
        if(ds[0][1] != None):
            totalcost = float(ds[0][1])
        if(ds[0][2] != None):
            copay = float(ds[0][2])

    return dict(totalcost=totalcost,copay=copay)

def copayment_treatment(db,treatmentid,patientid):
    copay     = 0
    hmoplanid = 0
    regionid = 0

    #get company id, hmoplan
    prows = db((db.patientmember.id == patientid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember==True)).select()
    if(len(prows) > 0):
        if(prows[0].hmoplan != None):
            hmoplanid = prows[0].hmoplan
        if(prows[0].groupregion != None):
            regionid =  rows[0].groupregion

    treatments  = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
    if(len(treatments)>0):
        procedureid = treatments[0].dentalprocedure

    if((hmoplanid > 0)):
        copayrow = db((db.copay.dentalprocedure == procedureid) & (db.copay.hmoplan == hmoplanid) & (db.copay.region == regionid)&(db.copay.is_active == True)).select()
        if(len(copayrow)>0):
            copay = copay + float(copayrow[0].copay)
        else:
            procrow = db((db.dentalprocedure.id == procedureid) & (db.dentalprocedure.is_active == True)).select()
            if(len(procrow)>0):
                copay = copay + float(procrow[0].procedurefee)
            else:
                copay = 0
    else:
        #non-hmo patient
        procrow = db((db.dentalprocedure.id == procedureid) & (db.dentalprocedure.is_active == True)).select()
        if(len(procrow)>0):
            copay = copay + float(procrow[0].procedurefee)
        else:
            copay = 0

    return copay


def calculatedue(db,tplanid):
    totaldue     = 0
    tprows = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).select()
    for tp in tprows:
        totaltreatmentcost = float(common.getvalue(tp.totaltreatmentcost))
        totalpaid = float(common.getvalue(tp.totalpaid))
        copaypaid = float(common.getvalue(tp.totalcopaypaid))
        inspaid = float(common.getvalue(tp.totalinspaid))
        
        totaldue = totaltreatmentcost - totalpaid - copaypaid - inspaid
        
    db(db.treatmentplan.id==tplanid).update(totaldue=totaldue)

    
    
def calculatetreatmentcopay(db,treatmentid,patientid):
    copay = account.copayment_treatment(db,treatmentid,patientid)
    db(db.treatment.id == treatmentid).update(copay = copay)    
    return dict()

def calculatecopay(db,tplanid,patientid):
    #copay = account.copayment(db,tplanid,patientid)
    totalcopay = 0
    trrows = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
    for tr in trrows:
        totalcopay = totalcopay + float(common.getvalue(tr.copay))
  
    
    db(db.treatmentplan.id == tplanid).update(totalcopay = totalcopay)
    return dict()

def calculatecost(db,tplanid):
    
    totalcost     = 0
    
    trrows = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
    for tr in trrows:
        totalcost = totalcost + float(common.getvalue(tr.treatmentcost))
        
        
    db(db.treatmentplan.id==tplanid).update(totaltreatmentcost = totalcost)
    
    return dict()

def calculateinspays(db,tplanid):
    
    totalinspays     = 0
    trrows = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
    for tr in trrows:
        totalinspays = totalinspays + float(common.getvalue(tr.inspay))
    db(db.treatmentplan.id==tplanid).update(totalinspays = totalinspays)
    
    return dict()

def get_tax_amount(db,amount):
    r = db((db.urlproperties.id > 0 ) & (db.urlproperties.is_active == True)).select()
    servicetax = float(common.getvalue(r[0].servicetax)) if (len(r) ==1) else 0
    tax = amount * servicetax/100
    posttaxamount = amount + tax
    
    return dict(tax=tax,posttaxamount = posttaxamount)

def get_booking_amount(db,treatmentid):
    #logger.loggerpms2.info("Enter get_booking_amount " + str(treatmentid))
    rows = db((db.vw_treatmentprocedure.treatmentid == treatmentid) & (db.vw_treatmentprocedure.is_active == True)).select()
    logger.loggerpms2.info("rows " + str(len(rows)))
    if(len(rows) != 1):
        return 0
    
    memberid = rows[0].primarypatient
    p = db((db.patientmember.id == memberid)& (db.patientmember.is_active == True)).select(db.patientmember.groupref)
    #logger.loggerpms2.info("patients " + str(len(p)) + " " + str(memberid))
    if(len(p) != 1):
        return 0
    
    b = db((db.booking.booking_id == common.getstring(p[0].groupref)) & (db.booking.is_active == True)).select()
    
    booking_amount = 0
    
    
    if(len(b)==1):
        booking_amount = float(common.getvalue(b[0].package_booking_amount))

    #logger.loggerpms2.info("Exit get_booking_amount " + common.getstring(p[0].groupref) + " " + str(len(b)) + " " + str(booking_amount))                                                   
    return booking_amount

def updatetreatmentcostandcopay(db,user,treatmentid):
    
    logger.loggerpms2.info("Enter Update Treatment Cost Copay " + str(treatmentid))
    
    totalactualtreatmentcost = 0   #UCR Cost
    totaltreatmentcost = 0  #Cost charged to the client which is equal to UCR fee by default
    totalcopay = 0
    totalinspays = 0
    totalcompanypays = 0
    
    rows = db((db.vw_treatmentprocedure.treatmentid == treatmentid) & (db.vw_treatmentprocedure.is_active == True)).select()
    for r in rows:
        totalactualtreatmentcost = totalactualtreatmentcost + float(common.getvalue(r.ucrfee))
        totaltreatmentcost = totaltreatmentcost + float(common.getvalue(r.procedurefee))
        totalcopay = totalcopay + float(common.getvalue(r.copay))
        totalinspays = totalinspays + float(common.getvalue(r.inspays)) 
        totalcompanypays = totalcompanypays + float(common.getvalue(r.companypays))     
       
    
    db(db.treatment.id == treatmentid).update(actualtreatmentcost = totalactualtreatmentcost, treatmentcost=totaltreatmentcost, \
                                              copay=totalcopay, inspay=totalinspays, companypay= totalcompanypays,
                                              modified_on = datetime.datetime.today(),modified_by = 1 if(user == None) else user.id)
    
    
    d = dict(totalactualtreatmentcost=totalactualtreatmentcost,totaltreatmentcost=totaltreatmentcost,totalcopay=totalcopay,totalinspays=totalinspays,totalcompanypays=totalcompanypays)
    logger.loggerpms2.info("Exit Update Treatment Cost Copay API " + json.dumps(d))
    return dict(totalactualtreatmentcost=totalactualtreatmentcost,totaltreatmentcost=totaltreatmentcost,totalcopay=totalcopay,totalinspays=totalinspays,totalcompanypays=totalcompanypays)


def calculatepayments(tplanid,providerid,policy=None):
    treatmentcost = 0
    copay = 0
    inspays = 0
    companypays = 0
    precopay = 0
    walletamount = 0
    discountamount = 0
    
    totaltreatmentcost = 0
    totalcopay = 0
    totalprecopay = 0
    totalinspays = 0
    totaldue = 0
    totalpaid = 0
    totalcompanypays = 0   
    totalwalletamount = 0
    totaldiscountamount = 0
    
        
    tplan = db(db.treatmentplan.id == tplanid).select()
    if(len(tplan) > 0):
        treatmentcost = float(common.getvalue(tplan[0].totaltreatmentcost))
        companypays = float(common.getvalue(tplan[0].totalcompanypays))
        walletamount = float(common.getvalue(tplan[0].totalwalletamount))        
        
        precopay =float(common.getvalue(tplan[0].totalcopay))
        copay = float(common.getvalue(tplan[0].totalcopay)) - companypays
        inspays = float(common.getvalue(tplan[0].totalinspays))
        
        memberid = int(common.getid(tplan[0].primarypatient))
        
        
        
        
            
        
        r = db((db.vw_treatmentplansummarybytreatment.provider==providerid) & (db.vw_treatmentplansummarybytreatment.id == tplanid)).select()
        if(len(r)>0):
            totaltreatmentcost = float(common.getvalue(r[0].totalcost))
            totalinspays = float(common.getvalue(r[0].totalinspays))
            totalcompanypays = float(common.getvalue(r[0].totalcompanypays))
            totalwalletamount = 0 #float(common.getvalue(r[0].totalwalletamount))
            totalprecopay = float(common.getvalue(r[0].totalcopay))
            totalcopay = float(common.getvalue(r[0].totalcopay)) - totalcompanypays
            totalpaid = float(common.getvalue(r[0].totalpaid))
            totaldue = totalcopay - totalpaid
        
        
    return dict(treatmentcost=treatmentcost,copay=copay,precopay=precopay,inspays=inspays,companypays=companypays, walletamount=walletamount,
                totaltreatmentcost=totaltreatmentcost,totalinspays=totalinspays,\
                totalprecopay=totalprecopay,totalcopay=totalcopay,\
                totalpaid=totalpaid,totaldue=totaldue,totalcompanypays=totalcompanypays,totalwalletamount=totalwalletamount)


def x_calculatepayments(db,tplanid,policy=None):
    respobj = {}

    treatmentcost = 0
    copay = 0
    inspays = 0
    companypays = 0
    precopay = 0
    walletamount = 0 
    discount_amount = 0
    promo_amount = 0
    
    totaltreatmentcost = 0
    totalcopay = 0
    totalprecopay = 0
    totalinspays = 0
    totaldue = 0
    totalpaid = 0
    totalcompanypays = 0
    totalwalletamount = 0
    totaldiscount_amount = 0
    totalpromo_amount = 0
    wallet_type = ""
    voucher_code = ""
    promo_code = ""
    
    r = None
    tplan = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).select()
    if(len(tplan) > 0):
        treatmentcost = float(common.getvalue(tplan[0].totaltreatmentcost))
        companypays = float(common.getvalue(tplan[0].totalcompanypays))
        walletamount = float(common.getvalue(tplan[0].totalwalletamount))  
        discount_amount = float(common.getvalue(tplan[0].totaldiscount_amount))  
        precopay =float(common.getvalue(tplan[0].totalcopay))
        copay = float(common.getvalue(tplan[0].totalcopay)) - (discount_amount + companypays + walletamount)
        inspays = float(common.getvalue(tplan[0].totalinspays))
        memberid = int(common.getid(tplan[0].primarypatient))
        promo_amount = float(common.getvalue(tplan[0].totalpromo_amount))  
        promo_code = common.getstring(tplan[0].promo_code)
        wallet_type = common.getstring(tplan[0].wallet_type)
        voucher_code = common.getstring(tplan[0].voucher_code)
        
        r = db((db.vw_treatmentplansummarybytreatment.id == tplanid) & (db.vw_treatmentplansummarybytreatment.is_active  == True)).select()
        if(len(r)>0):
            totaltreatmentcost = float(common.getvalue(r[0].totalcost))
            totalinspays = float(common.getvalue(r[0].totalinspays))
            totalcompanypays = float(common.getvalue(r[0].totalcompanypays))
            totalwalletamount = float(common.getvalue(r[0].totalwalletamount))           
            totaldiscount_amount = float(common.getvalue(r[0].totaldiscount_amount))           
            totalpromo_amount = float(common.getvalue(r[0].totalpromo_amount))           
            totalprecopay = float(common.getvalue(r[0].totalcopay))
            totalcopay = float(common.getvalue(r[0].totalcopay)) - (totaldiscount_amount + totalcompanypays + totalwalletamount)
            totalpaid = float(common.getvalue(r[0].totalpaid))
            totaldue = totalcopay - totalpaid

            respobj = {}
            respobj["totaltreatmentcost"]=totaltreatmentcost
            respobj["totalinspays"]=totalinspays
            respobj["totalcompanypays"]=totalcompanypays
            respobj["totalwalletamount"]=totalwalletamount
            respobj["totaldiscount_amount"]=totaldiscount_amount
            respobj["totalpromo_amount"]=totalpromo_amount
            respobj["totalprecopay"]=totalprecopay
            respobj["totalcopay"]=totalcopay
            respobj["totalpaid"]=totalpaid
            respobj["totaldue"]=totaldue

            respobj["treatmentcost"]=treatmentcost
            respobj["copay"]=copay
            respobj["precopay"]=precopay
            respobj["inspays"]=inspays
            respobj["companypays"]=companypays
            respobj["walletamount"]=walletamount
            respobj["discount_amount"]=discount_amount
            respobj["promo_amount"]=promo_amount
            respobj["wallet_type"] = wallet_type
            respobj["voucher_code"] = voucher_code
            respobj["promo_code"] = promo_code
            
            
            respobj["result"] = "success"
            respobj["error_message"] = ""

        else:
            msg = "_calculatepayments error for " + str(tplanid)
            respobj["result"] = "fail"
            respobj["error_message"] = msg


    return json.dumps(respobj)

def _updatetreatmentpayment(db,tplanid,paymentid,policy="PREMWALKIN"):
    logger.loggerpms2.info("Enter Update Treatment Payment " + str(tplanid) + " " + str(paymentid))
    user = None

    #calculate
    totalactualtreatmentcost = 0   #UCR Cost
    totaltreatmentcost = 0         #treatment cost as per the plan
    totalprecopay = 0              #total pre-copay by the patient prior to discount and wallet amounts
    totalcopay = 0                 #total copay by the patient after discount and wallet amounts
    totalinspays = 0               #total amount paid by the insurance
    totalcompanypays = 0           #total amount paid by the company - benefit amount as per the plan
    totalpaid = 0                  #total amount paid
    totaldue = 0                   #total due
    totaldiscount_amount = 0
    totalwalletamount = 0
    totalpromo_amount = 0

    #Table: treatment
    #Columns:
    #id int(11) AI PK 
    #treatment varchar(64) 
    #description varchar(128) 
    #startdate date 
    #enddate date 
    #status varchar(45) 
    #---actualtreatmentcost double 
    #---treatmentcost double 
    #---copay double 
    #---inspay double 
    #companypay double 
    #walletamount double 
    #discount_amount double 
    #wallet_type varchar(45) 
    #voucher_code varchar(45) 
    #promo_code varchar(45) 
    #promo_amount double 
    #WPBA_response longtext 
    #treatmentplan int(11) 
    #provider int(11) 
    #doctor int(11) 
    #clinicid int(11) 
    #dentalprocedure int(11) 
    #quadrant varchar(45) 
    #tooth varchar(45) 
    #chiefcomplaint varchar(128) 
    #authorized char(1) 
    #is_active char(1) 
    #created_on datetime 
    #created_by int(11) 
    #modified_on datetime 
    #modified_by int(11)
    
    
    
    trs = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
    for tr in trs:
        procs = db((db.treatment_procedure.treatmentid == tr.id) & (db.treatment_procedure.is_active == True)).select()
        actualtreatmentcost = 0
        treatmentcost = 0
        precopay = 0
        copay = 0
        inspay = 0
        for proc in procs:
            actualtreatmentcost = actualtreatmentcost +  float(common.getvalue(proc.ucr))
            treatmentcost = treatmentcost + float(common.getvalue(proc.procedurefee))
            precopay = precopay + float(common.getvalue(proc.copay))
            copay = copay + float(common.getvalue(proc.copay))
            inspay = inspay + float(common.getvalue(proc.inspays))
         
        #update proc costs into treatment costs
        db((db.treatment.id == tr.id) & (tr.is_active == True)).update(actualtreatmentcost=actualtreatmentcost,treatmentcost=treatmentcost,copay=copay,inspay=inspay)
        
        #calculate total costs for treatment plan
        totalactualtreatmentcost = totalactualtreatmentcost + actualtreatmentcost
        totaltreatmentcost = totaltreatmentcost + treatmentcost
        totalprecopay = totalprecopay + precopay
        totalcopay = totalcopay + copay
        totalinspays = totalinspays + inspay
        
        totalcompanypays = totalcompanypays + float(common.getvalue(tr.companypay))
        totaldiscount_amount = totaldiscount_amount + float(common.getvalue(tr.discount_amount))
        totalwalletamount = totalwalletamount + float(common.getvalue(tr.walletamount))
        totalpromo_amount = totalpromo_amount + float(common.getvalue(tr.promo_amount))
        
    #calculate all the payments made and due for each treatment plan
    pymnts = db((db.payment.treatmentplan == tplanid) & (db.payment.is_active == True)).select()
    for pymnt in pymnts:
        totalpaid = totalpaid + float(common.getvalue(pymnt.amount))
        
    totaldue = totalcopay - totalinspays - totalcompanypays - totaldiscount_amount - totalwalletamount - totalpromo_amount - totalpaid
    
    db(db.treatmentplan.id == tplanid).update(
        totaltreatmentcost = totaltreatmentcost,
        totalcopay = totalcopay,
        totalinspays = totalinspays,
        totalcompanypays = totalcompanypays,
        totalwalletamount = totalwalletamount,
        totaldiscount_amount  = totaldiscount_amount,
        totalpromo_amount  = totalpromo_amount,
        totalpaid = totalpaid,
        totaldue = totaldue
    )    
    db.commit()
    #paytm = json.loads(_calculatepayments(db, tplanid,policy))
    
    ##logger.loggerpms2.info("_updatetreatmentpayment -1A " + str(common.getvalue(totalpaid)))
    #procs = db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.is_active == True)).select()
    ##logger.loggerpms2.info("_updatetreatmentpayment -2 " + str(tplanid) + " " + str(treatmentid))
    
    #for proc in procs:
        ##logger.loggerpms2.info("_updatetreatmentpayment -proc ")
        
        #totalactualtreatmentcost = totalactualtreatmentcost + float(common.getvalue(proc.ucr))
        #totaltreatmentcost = totaltreatmentcost + float(common.getvalue(proc.procedurefee))
        #totalprecopay = totalprecopay + float(common.getvalue(proc.copay))
        #totalcopay = totalcopay + float(common.getvalue(proc.copay))
        #totalinspays = totalinspays + float(common.getvalue(proc.inspays))
        #totalcompanypays = totalcompanypays + float(common.getvalue(proc.companypays))
    
    ##logger.loggerpms2.info("_updatetreatmentpayment -proc Exit loop ")
    #db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).update(actualtreatmentcost = totalactualtreatmentcost, treatmentcost=totaltreatmentcost, \
                                              #copay=totalcopay, inspay=totalinspays, companypay= totalcompanypays,
                                              #modified_on = datetime.datetime.today(),modified_by = 1 if(user == None) else user.id)    

    
    
    
    #tr = db((db.treatment.id == treatmentid) & (db.treatment.is_active == True)).select()
    
    #totaldiscount_amount = float(common.getvalue(tr[0].discount_amount)) if(len(tr) > 0) else 0
    #totalwalletamount = float(common.getvalue(tr[0].walletamount)) if(len(tr) > 0) else 0
    #totalpromo_amount = float(common.getvalue(tr[0].promo_amount)) if(len(tr) > 0) else 0
    #voucher_code  = common.getstring(tr[0].voucher_code) if(len(tr) > 0) else 0
    
  
    #ps = db((db.payment.treatmentplan == tplanid) & (db.payment.is_active == True)).select()
    ##logger.loggerpms2.info("_updatetreatmentpayment -3 " + str(tplanid) + " " + str(len(ps)))
    #for p in ps:
        ##logger.loggerpms2.info("_updatetreatmentpayment -3A ")
        #totalpaid = totalpaid + float(common.getvalue(p.amount))
        
    ##logger.loggerpms2.info("_updatetreatmentpayment -4 " )
  
    ##totaldue = totalcopay
    ###logger.loggerpms2.info("_updatetreatmentpayment -41 " )
    ##totaldue = totalcopay - totalcompanypays
    ###logger.loggerpms2.info("_updatetreatmentpayment -42 " )
    ##totaldue = totalcopay - totalcompanypays - totaldiscount_amount
    ###logger.loggerpms2.info("_updatetreatmentpayment -43 " )
    ##totaldue = totalcopay - totalcompanypays - totaldiscount_amount - totalwalletamount
    ###logger.loggerpms2.info("_updatetreatmentpayment -44 " )
    ##totaldue = totalcopay - totalcompanypays - totaldiscount_amount - totalwalletamount - totalpaid
    
    #logger.loggerpms2.info("_updatetreatmentpayment -4A ")
    
    #db(db.treatmentplan.id == tplanid).update(
        #totaltreatmentcost = totaltreatmentcost,
        #totalcopay = totalcopay,
        #totalinspays = totalinspays,
        #totalcompanypays = totalcompanypays,
        #totalwalletamount = totalwalletamount,
        #totaldiscount_amount  = totaldiscount_amount,
        #totalpromo_amount  = totalpromo_amount,
        #totalpaid = totalpaid,
        #totaldue = totalcopay - totalcompanypays - totaldiscount_amount - totalwalletamount - totalpromo_amount - totalpaid

    #)    

    #logger.loggerpms2.info("_updatetreatmentpayment -5 " )
    
    #logger.loggerpms2.info("Paytm Update Treatment Payment " + json.dumps(paytm))
   
    logger.loggerpms2.info("Exit Update Treamtnet Payment ")
    return json.dumps({"result":"success"})

def _calculatepayments(db,tplanid,policy="PREMWALKIN"):
    logger.loggerpms2.info("Enter Calulate Payment " + str(tplanid) )
    user = None

    treatmentcost = 0
    copay = 0
    inspays = 0
    companypays = 0
    precopay = 0
    walletamount = 0 
    discount_amount = 0
    promo_amount = 0
        
    wallet_type = ""
    voucher_code = ""
    promo_code = ""

    
    #calculate
    totalactualtreatmentcost = 0   #UCR Cost
    totaltreatmentcost = 0         #treatment cost as per the plan
    totalprecopay = 0              #total pre-copay by the patient prior to discount and wallet amounts
    totalcopay = 0                 #total copay by the patient after discount and wallet amounts
    totalinspays = 0               #total amount paid by the insurance
    totalcompanypays = 0           #total amount paid by the company - benefit amount as per the plan
    totalpaid = 0                  #total amount paid
    totaldue = 0                   #total due
    totaldiscount_amount = 0
    totalwalletamount = 0
    totalpromo_amount = 0


    tplan = db((db.treatmentplan.id == tplanid) & (db.treatmentplan.is_active == True)).select()
    if(len(tplan) > 0):
        treatmentcost = float(common.getvalue(tplan[0].totaltreatmentcost))
        companypays = float(common.getvalue(tplan[0].totalcompanypays))
        walletamount = float(common.getvalue(tplan[0].totalwalletamount))  
        discount_amount = float(common.getvalue(tplan[0].totaldiscount_amount))  
        precopay =float(common.getvalue(tplan[0].totalcopay))
        copay = float(common.getvalue(tplan[0].totalcopay)) - (discount_amount + companypays + walletamount)
        inspays = float(common.getvalue(tplan[0].totalinspays))
        memberid = int(common.getid(tplan[0].primarypatient))
        promo_amount = float(common.getvalue(tplan[0].totalpromo_amount))  
        promo_code = common.getstring(tplan[0].promo_code)
        wallet_type = common.getstring(tplan[0].wallet_type)
        voucher_code = common.getstring(tplan[0].voucher_code)
        
        
    #Table: treatment
    #Columns:
    #id int(11) AI PK 
    #treatment varchar(64) 
    #description varchar(128) 
    #startdate date 
    #enddate date 
    #status varchar(45) 
    #---actualtreatmentcost double 
    #---treatmentcost double 
    #---copay double 
    #---inspay double 
    #companypay double 
    #walletamount double 
    #discount_amount double 
    #wallet_type varchar(45) 
    #voucher_code varchar(45) 
    #promo_code varchar(45) 
    #promo_amount double 
    #WPBA_response longtext 
    #treatmentplan int(11) 
    #provider int(11) 
    #doctor int(11) 
    #clinicid int(11) 
    #dentalprocedure int(11) 
    #quadrant varchar(45) 
    #tooth varchar(45) 
    #chiefcomplaint varchar(128) 
    #authorized char(1) 
    #is_active char(1) 
    #created_on datetime 
    #created_by int(11) 
    #modified_on datetime 
    #modified_by int(11)
    
    
    
    trs = db((db.treatment.treatmentplan == tplanid) & (db.treatment.is_active == True)).select()
    for tr in trs:
        procs = db((db.treatment_procedure.treatmentid == tr.id) & (db.treatment_procedure.is_active == True)).select()
        actualtreatmentcost = 0
        treatmentcost = 0
        precopay = 0
        copay = 0
        inspay = 0
        for proc in procs:
            actualtreatmentcost = actualtreatmentcost +  float(common.getvalue(proc.ucr))
            treatmentcost = treatmentcost + float(common.getvalue(proc.procedurefee))
            precopay = precopay + float(common.getvalue(proc.copay))
            copay = copay + float(common.getvalue(proc.copay))
            inspay = inspay + float(common.getvalue(proc.inspays))
         
        #update proc costs into treatment costs
        db((db.treatment.id == tr.id) & (tr.is_active == True)).update(actualtreatmentcost=actualtreatmentcost,treatmentcost=treatmentcost,copay=copay,inspay=inspay)
        
        #calculate total costs for treatment plan
        totalactualtreatmentcost = totalactualtreatmentcost + actualtreatmentcost
        totaltreatmentcost = totaltreatmentcost + treatmentcost
        totalprecopay = totalprecopay + precopay
        totalinspays = totalinspays + inspay
        
        totalcompanypays = totalcompanypays + float(common.getvalue(tr.companypay))
        totaldiscount_amount = totaldiscount_amount + float(common.getvalue(tr.discount_amount))
        totalwalletamount = totalwalletamount + float(common.getvalue(tr.walletamount))
        totalpromo_amount = totalpromo_amount + float(common.getvalue(tr.promo_amount))

        totalcopay = totalprecopay - totalinspays - totalcompanypays - totaldiscount_amount -totalwalletamount-totalpromo_amount
 
        
    #calculate all the payments made and due for each treatment plan
    pymnts = db((db.payment.treatmentplan == tplanid) & (db.payment.is_active == True)).select()
    for pymnt in pymnts:
        totalpaid = totalpaid + float(common.getvalue(pymnt.amount))
    
    totaldue = totalcopay - totalpaid
    
   
    respobj = {}
    respobj["totaltreatmentcost"]=totaltreatmentcost
    respobj["totalinspays"]=totalinspays
    respobj["totalcompanypays"]=totalcompanypays
    respobj["totalwalletamount"]=totalwalletamount
    respobj["totaldiscount_amount"]=totaldiscount_amount
    respobj["totalpromo_amount"]=totalpromo_amount
    respobj["totalprecopay"]=totalprecopay
    respobj["totalcopay"]=totalcopay
    respobj["totalpaid"]=totalpaid
    respobj["totaldue"]=totaldue

    respobj["treatmentcost"]=treatmentcost
    respobj["precopay"]=precopay
    respobj["inspays"]=inspays
    respobj["companypays"]=companypays
    respobj["walletamount"]=walletamount
    respobj["discount_amount"]=discount_amount
    respobj["promo_amount"]=promo_amount
    respobj["wallet_type"] = wallet_type
    respobj["voucher_code"] = voucher_code
    respobj["promo_code"] = promo_code
    respobj["copay"]=precopay-inspays-companypays-discount_amount-walletamount-promo_amount


    respobj["result"] = "success"
    respobj["error_message"] = ""
    
    mssg = json.dumps(respobj)
    logger.loggerpms2.info("Exit _CalculatePayments " + mssg)
    return mssg

