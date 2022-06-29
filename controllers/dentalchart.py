from gluon import current
db = current.globalenv['db']
#
import datetime

from shutil import copyfile

import os
from base64 import decodestring

#import sys
#sys.path.append('modules')
from applications.my_pms2.modules import common
#from gluon.contrib import common
#


#parameters for calling out dental procedures
chartid = 0
chartdate = datetime.datetime.now()
providerid = 0
doctorid = 0
dentalprocedure = ""
procedureid = 0
toothid = ""
toothnumber = 0 
toothsection = ""


def t46():
    return dict(sec1="46-1-LL", sec2="46-2-LL", sec3="46-3-LL",sec4="46-4-LL",sec5="46-5-LL",sec6="46-6-LL",sec7="46-7-LL",sec8="46-8-LL" )

def t11():
    return dict(sec1="11-1-UL", sec2="11-2-UL", sec3="11-3-UL",sec4="11-4-UL",sec5="11-5-UL",sec6="11-6-UL",sec7="11-7-UL",sec8="11-8-UL" )

def t12():
    return dict(sec1="12-1-UL", sec2="12-2-UL", sec3="12-3-UL",sec4="12-4-UL",sec5="12-5-UL",sec6="12-6-UL",sec7="12-7-UL",sec8="12-8-UL" )

def t13():
    return dict(sec1="13-1-UL", sec2="13-2-UL", sec3="13-3-UL",sec4="13-4-UL",sec5="13-5-UL",sec6="13-6-UL",sec7="13-7-UL",sec8="13-8-UL" )

def t14():
    return dict(sec1="14-1-UL", sec2="14-2-UL", sec3="14-3-UL",sec4="14-4-UL",sec5="14-5-UL",sec6="14-6-UL",sec7="14-7-UL",sec8="14-8-UL", sec9="14-9-UL" )


def t15():
    return dict(sec1="15-1-UL", sec2="15-2-UL", sec3="15-3-UL",sec4="15-4-UL",sec5="15-5-UL",sec6="15-6-UL",sec7="15-7-UL",sec8="15-8-UL" )

def t16():
    return dict(sec1="16-1-UL", sec2="16-2-UL", sec3="16-3-UL",sec4="16-4-UL",sec5="16-5-UL",sec6="16-6-UL",sec7="16-7-UL",sec8="16-8-UL", sec9="16-9-UL")

def t17():
    return dict(sec1="17-1-UL", sec2="17-2-UL", sec3="17-3-UL",sec4="17-4-UL",sec5="17-5-UL",sec6="17-6-UL",sec7="17-7-UL",sec8="17-8-UL", sec9="17-9-UL")

def t18():
    return dict(sec1="18-1-UL", sec2="18-2-UL", sec3="18-3-UL",sec4="18-4-UL",sec5="18-5-UL",sec6="18-6-UL",sec7="18-7-UL",sec8="18-8-UL")

def t21():
    return dict(sec1="21-1-UR", sec2="21-2-UR", sec3="21-3-UR",sec4="21-4-UR",sec5="21-5-UR",sec6="21-6-UR",sec7="21-7-UR",sec8="21-8-UR")

def t22():
    return dict(sec1="22-1-UR", sec2="22-2-UR", sec3="22-3-UR",sec4="22-4-UR",sec5="22-5-UR",sec6="22-6-UR",sec7="22-7-UR",sec8="22-8-UR")


def t23():
    return dict(sec1="23-1-UR", sec2="23-2-UR", sec3="23-3-UR",sec4="23-4-UR",sec5="23-5-UR",sec6="23-6-UR",sec7="23-7-UR",sec8="23-8-UR")


def t24():
    return dict(sec1="24-1-UR", sec2="24-2-UR", sec3="24-3-UR",sec4="24-4-UR",sec5="24-5-UR",sec6="24-6-UR",sec7="24-7-UR",sec8="24-8-UR",sec9="24-9-UR")


def t25():
    return dict(sec1="25-1-UR", sec2="25-2-UR", sec3="25-3-UR",sec4="25-4-UR",sec5="25-5-UR",sec6="25-6-UR",sec7="25-7-UR",sec8="25-8-UR")


def t26():
    return dict(sec1="26-1-UR", sec2="26-2-UR", sec3="26-3-UR",sec4="26-4-UR",sec5="26-5-UR",sec6="26-6-UR",sec7="26-7-UR",sec8="26-8-UR",sec9="26-9-UR")


def t27():
    return dict(sec1="27-1-UR", sec2="27-2-UR", sec3="27-3-UR",sec4="27-4-UR",sec5="27-5-UR",sec6="27-6-UR",sec7="27-7-UR",sec8="27-8-UR",sec9="27-9-UR")


def t28():
    return dict(sec1="28-1-UR", sec2="28-2-UR", sec3="28-3-UR",sec4="28-4-UR",sec5="28-5-UR",sec6="28-6-UR",sec7="28-7-UR",sec8="28-8-UR")


def t31():
    return dict(sec1="31-1-LR", sec2="31-2-LR", sec3="31-3-LR",sec4="31-4-LR",sec5="31-5-LR",sec6="31-6-LR",sec7="31-7-LR",sec8="31-8-LR")


def t32():
    return dict(sec1="32-1-LR", sec2="32-2-LR", sec3="32-3-LR",sec4="32-4-LR",sec5="32-5-LR",sec6="32-6-LR",sec7="32-7-LR",sec8="32-8-LR")


def t33():
    return dict(sec1="33-1-LR", sec2="33-2-LR", sec3="33-3-LR",sec4="33-4-LR",sec5="33-5-LR",sec6="33-6-LR",sec7="33-7-LR",sec8="33-8-LR")


def t34():
    return dict(sec1="34-1-LR", sec2="34-2-LR", sec3="34-3-LR",sec4="34-4-LR",sec5="34-5-LR",sec6="34-6-LR",sec7="34-7-LR",sec8="34-8-LR")


def t35():
    return dict(sec1="35-1-LR", sec2="35-2-LR", sec3="35-3-LR",sec4="35-4-LR",sec5="35-5-LR",sec6="35-6-LR",sec7="35-7-LR",sec8="35-8-LR")


def t36():
    return dict(sec1="36-1-LR", sec2="36-2-LR", sec3="36-3-LR",sec4="36-4-LR",sec5="36-5-LR",sec6="36-6-LR",sec7="36-7-LR",sec8="36-8-LR")


def t37():
    return dict(sec1="37-1-LR", sec2="37-2-LR", sec3="37-3-LR",sec4="37-4-LR",sec5="37-5-LR",sec6="37-6-LR",sec7="37-7-LR",sec8="37-8-LR")


def t38():
    return dict(sec1="38-1-LR", sec2="38-2-LR", sec3="38-3-LR",sec4="38-4-LR",sec5="38-5-LR",sec6="38-6-LR",sec7="38-7-LR",sec8="38-8-LR",sec9="38-9-LR")


def t41():
    return dict(sec1="41-1-LL", sec2="41-2-LL", sec3="41-3-LL",sec4="41-4-LL",sec5="41-5-LL",sec6="41-6-LL",sec7="41-7-LL",sec8="41-8-LL")

def t42():
    return dict(sec1="42-1-LL", sec2="42-2-LL", sec3="42-3-LL",sec4="42-4-LL",sec5="42-5-LL",sec6="42-6-LL",sec7="42-7-LL",sec8="42-8-LL")

def t43():
    return dict(sec1="43-1-LL", sec2="43-2-LL", sec3="43-3-LL",sec4="43-4-LL",sec5="43-5-LL",sec6="43-6-LL",sec7="43-7-LL",sec8="43-8-LL")

def t44():
    return dict(sec1="44-1-LL", sec2="44-2-LL", sec3="44-3-LL",sec4="44-4-LL",sec5="44-5-LL",sec6="44-6-LL",sec7="44-7-LL",sec8="44-8-LL")

def t45():
    return dict(sec1="45-1-LL", sec2="45-2-LL", sec3="45-3-LL",sec4="45-4-LL",sec5="45-5-LL",sec6="45-6-LL",sec7="45-7-LL",sec8="45-8-LL")

def t47():
    return dict(sec1="47-1-LL", sec2="47-2-LL", sec3="47-3-LL",sec4="47-4-LL",sec5="47-5-LL",sec6="47-6-LL",sec7="47-7-LL",sec8="47-8-LL")

def t48():
    return dict(sec1="48-1-LL", sec2="48-2-LL", sec3="48-3-LL",sec4="48-4-LL",sec5="48-5-LL",sec6="48-6-LL",sec7="48-7-LL",sec8="48-8-LL")

def t00():
    return dict(sec1="", sec2="", sec3="",sec4="",sec5="",sec6="",sec7="",sec8="")

def toothsections(toothnumber):
    switcher = {
        11: t11,
        12: t12,
        13: t13,
        14: t14,
        15: t15,
        16: t16,
        17: t17,
        18: t18,
        21: t21,
        22: t22,
        23: t23,
        24: t24,
        25: t25,
        26: t26,
        27: t27,
        28: t28,
        31: t31,
        32: t32,
        33: t33,
        34: t34,
        35: t35,
        36: t36,
        37: t37,
        38: t38,
        41: t41,
        42: t42,
        43: t43,
        44: t44,
        45: t45,
        46: t46,
        47: t47,
        48: t48,
    }
    # Get the function from switcher dictionary
    func = switcher.get(toothnumber, lambda: t00)
    # Execute the function
    return func()    



def dentalprocedures(procedurecode):
    
    switcher = {
           'X0010': toothextractionX0010,
           'X0021': filling,
           'X0022': filling,
           'X0023': filling,
           'X0024': filling,
           'X0025': filling,
           'X0026': filling,
           'X0027': filling,
           'X0028': filling,
           'X0029': filling,
           'X0030': filling,
           'X0031': filling,
           'X0032': filling,
           'X0033': filling,
           'X0034': filling,
           'X0035': filling,
           'X0036': filling,
           'X0037': filling,
           'X0038': filling,
           'X0039': filling,
           'X0040': toothcrownX0040,
           'X0050': missingtoothX0050,  
           'X0060': toothimplantX0060,
           'X0070': toothcavityX0070,
           'X0080': rootcanalX0080,
           }
    # Get the function from switcher dictionary
    func = switcher.get(procedurecode, lambda:error)
    # Execute the function
    return func()    

def error():
    
    return dict()


def toothcavityX0070():
    chartid = int(common.getid(request.vars.chartid))
    toothid = common.getstring(request.vars.toothid)
    toothsection = common.getstring(request.vars.toothsection)
    toothnumber =int(common.getid(request.vars.toothnumber))
    doctorid = int(common.getid(request.vars.doctor))
    dentalprocedure = common.getstring(request.vars.dentalprocedure)
    chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    providerid = int(common.getid(request.vars.providerid))  
    procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    notes = common.getstring(request.vars.notes)
    procedureid = 1;
    if(len(procs) > 0):
        procedureid = int(common.getid(procs[0].id))        
  
    defcolor = "#F7F2C6"
    color = defcolor
    
    p1color = defcolor
    p2color = defcolor
    p3color = defcolor
    p4color = defcolor
    p5color = defcolor
    p6color = defcolor
    p7color = defcolor
    p8color = defcolor
    p9color = defcolor
    p10color = defcolor
    l1color = defcolor
    l2color = defcolor
    l3color = defcolor
    l4color = defcolor
    e1color = defcolor
    
    # Get the color for Cavity
    rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    if(len(rows)>0):
        color = rows[0].color;
        
    tmparr = toothid.split('-');
    toothsecno = 0
    if(len(tmparr) == 3):
        toothsecno = int(tmparr[1])

    #valid sections for cavity arw 1,2,3,4,5,6 (circle sections and the 6th section)    
    if((toothsecno == 1)|(toothsecno == 2)|(toothsecno == 3)|(toothsecno == 4)|(toothsecno == 5)|(toothsecno == 6)):
        p1color = color
        l1color = color
        e1color = color
        
        toothid = db.tooth.update_or_insert(((db.tooth.chartid == chartid)&(db.tooth.toothid==toothid)&(db.tooth.is_active==True)),
                                                  chartid = chartid,
                                                  toothid = toothid,
                                                  toothsection = toothsection,
                                                  toothnumber = toothnumber,
                                                  doctorid = doctorid,
                                                  procedureid = procedureid,
                                                  chartdate = chartdate,
                                                  p1=p1color,
                                                  p2=p2color,
                                                  p3=p3color,
                                                  p4=p4color,
                                                  p5=p5color,
                                                  p6=p6color,
                                                  p7=p7color,
                                                  p8=p8color,
                                                  l1=color,
                                                  l2=color,
                                                  l3=color,
                                                  l4=color,
                                                  e1=color,
                                                  notes=notes,
                                                  created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid
                                                  
                                              )
        
        
        db.commit()
    else:
        response.flash = "Invalid tooth section for Cavity"
        
    return dict()
    
    
def rootcanalX0080():
    
    chartid = int(common.getid(request.vars.chartid))
    toothid = common.getstring(request.vars.toothid)
    toothsection = common.getstring(request.vars.toothsection)
    toothnumber =int(common.getid(request.vars.toothnumber))
    doctorid = int(common.getid(request.vars.doctor))
    dentalprocedure = common.getstring(request.vars.dentalprocedure)
    chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    providerid = int(common.getid(request.vars.providerid))  
    procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    notes = common.getstring(request.vars.notes)
    procedureid = 1;
    if(len(procs) > 0):
        procedureid = int(common.getid(procs[0].id))        
  
    defcolor = "#F7F2C6"
    color = defcolor
    
    p1color = defcolor
    p2color = defcolor
    p3color = defcolor
    p4color = defcolor
    p5color = defcolor
    p6color = defcolor
    p7color = defcolor
    p8color = defcolor
    p9color = defcolor
    p10color = defcolor
    l1color = defcolor
    l2color = defcolor
    l3color = defcolor
    l4color = defcolor
    e1color = defcolor
    
    # Get the color for Missing Tooth procedure
    rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    if(len(rows)>0):
        color = rows[0].color;
        
    x   = toothsections(toothnumber);
    
    for i in xrange(0,len(x)):
        ytoothid = x["sec" + str(i+1)]
        
    
    #for cavity color only that is  only sections 8 and above are valid 
    for i in xrange(0,len(x)):
        xtoothid = x["sec" + str(i+1)]
        
        if((xtoothid != toothid)):
            continue
        else:
            p1color = color
            l1color = color
            e1color = color
            
            toothid = db.tooth.update_or_insert(((db.tooth.chartid == chartid)&(db.tooth.toothid==xtoothid)&(db.tooth.is_active==True)),
                                                      
                                                      chartid = chartid,
                                                      toothid = xtoothid,
                                                      toothsection = xtoothid,
                                                      toothnumber = toothnumber,
                                                      doctorid = doctorid,
                                                      procedureid = procedureid,
                                                      chartdate = chartdate,
                                                      p1=p1color,
                                                      p2=p2color,
                                                      p3=p3color,
                                                      p4=p4color,
                                                      p5=p5color,
                                                      p6=p6color,
                                                      p7=p7color,
                                                      p8=p8color,
                                                      l1=color,
                                                      l2=color,
                                                      l3=color,
                                                      l4=color,
                                                      e1=color,
                                                      notes=notes,
                                                      created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid
                                                      
                                                  )
    

    db.commit()
    
    return dict()



def toothimplantX0060():
    
    chartid = int(common.getid(request.vars.chartid))
    toothid = common.getstring(request.vars.toothid)
    toothsection = common.getstring(request.vars.toothsection)
    toothnumber =int(common.getid(request.vars.toothnumber))
    doctorid = int(common.getid(request.vars.doctor))
    dentalprocedure = common.getstring(request.vars.dentalprocedure)
    chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    providerid = int(common.getid(request.vars.providerid))  
    procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    notes = common.getstring(request.vars.notes)
    procedureid = 1;
    if(len(procs) > 0):
        procedureid = int(common.getid(procs[0].id))        
  
    defcolor = "#F7F2C6"
    color = defcolor
    
    p1color = defcolor
    p2color = defcolor
    p3color = defcolor
    p4color = defcolor
    p5color = defcolor
    p6color = defcolor
    p7color = defcolor
    p8color = defcolor
    p9color = defcolor
    p10color = defcolor
    l1color = defcolor
    l2color = defcolor
    l3color = defcolor
    l4color = defcolor
    e1color = defcolor
    
    # Get the color for Missing Tooth procedure
    rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    if(len(rows)>0):
        color = rows[0].color;
        
    x   = toothsections(toothnumber);
    

    #for implants only sections 8 and above are valid 
    for i in xrange(0,len(x)):
        if((i < 7)|(i==9)):
            continue
        
        else:
            xtoothid = x["sec" + str(i+1)]
            p1color = color
            l1color = color
            e1color = color
            
            toothid = db.tooth.update_or_insert(((db.tooth.chartid == chartid)&(db.tooth.toothid==xtoothid)&(db.tooth.is_active==True)),
                                                      
                                                      chartid = chartid,
                                                      toothid = xtoothid,
                                                      toothsection = xtoothid,
                                                      toothnumber = toothnumber,
                                                      doctorid = doctorid,
                                                      procedureid = procedureid,
                                                      chartdate = chartdate,
                                                      p1=p1color,
                                                      p2=p2color,
                                                      p3=p3color,
                                                      p4=p4color,
                                                      p5=p5color,
                                                      p6=p6color,
                                                      p7=p7color,
                                                      p8=p8color,
                                                      l1=color,
                                                      l2=color,
                                                      l3=color,
                                                      l4=color,
                                                      e1=color,
                                                      notes=notes,
                                                      created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid
                                                      
                                                  )
    

    db.commit()
    
    return dict()



def toothcrownX0040():
    
    chartid = int(common.getid(request.vars.chartid))
    toothid = common.getstring(request.vars.toothid)
    toothsection = common.getstring(request.vars.toothsection)
    toothnumber =int(common.getid(request.vars.toothnumber))
    doctorid = int(common.getid(request.vars.doctor))
    dentalprocedure = common.getstring(request.vars.dentalprocedure)
    chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    providerid = int(common.getid(request.vars.providerid))  
    procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    notes = common.getstring(request.vars.notes)
    procedureid = 1;
    if(len(procs) > 0):
        procedureid = int(common.getid(procs[0].id))        
  
    defcolor = "#F7F2C6"
    color = defcolor
    
    p1color = defcolor
    p2color = defcolor
    p3color = defcolor
    p4color = defcolor
    p5color = defcolor
    p6color = defcolor
    p7color = defcolor
    p8color = defcolor
    p9color = defcolor
    p10color = defcolor
    l1color = defcolor
    l2color = defcolor
    l3color = defcolor
    l4color = defcolor
    e1color = defcolor
    
    # Get the color for Missing Tooth procedure
    rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    if(len(rows)>0):
        color = rows[0].color;
        
    x   = toothsections(toothnumber);
    
    #for crown, valid sections are 1,2,3,4,5,6,7
    #surf1 = x["sec1"]
    #surf2 = x["sec2"]
    #surf3 = x["sec3"]
    #surf4 = x["sec4"]
    #surf5 = x["sec5"]
    #surf6 = x["sec6"]
    #surf7 = x["sec7"]
    
    ##SURF1 - if it is do
    #rows = db((db.tooth.chartid == chartid)&(db.tooth.is_active==True)&(db.tooth.toothid == surf1))
    #if(len(row)>0):
        #p1color = rows[0].p1
        #l1color = rows[0].l1
        #e1color = rows[0].e1        

    #for crowns only sect1..7 are valid. 
    for i in xrange(0,len(x)):
        if(i > 6):
            continue
        else:
            xtoothid = x["sec" + str(i+1)]
            p1color = color
            l1color = color
            e1color = color
            
            toothid = db.tooth.update_or_insert(((db.tooth.chartid == chartid)&(db.tooth.toothid==xtoothid)&(db.tooth.is_active==True)),
                                                      
                                                      chartid = chartid,
                                                      toothid = xtoothid,
                                                      toothsection = xtoothid,
                                                      toothnumber = toothnumber,
                                                      doctorid = doctorid,
                                                      procedureid = procedureid,
                                                      chartdate = chartdate,
                                                      p1=p1color,
                                                      p2=p2color,
                                                      p3=p3color,
                                                      p4=p4color,
                                                      p5=p5color,
                                                      p6=p6color,
                                                      p7=p7color,
                                                      p8=p8color,
                                                      l1=color,
                                                      l2=color,
                                                      l3=color,
                                                      l4=color,
                                                      e1=color,
                                                      notes=notes,
                                                      created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid
                                                      
                                                  )
    

    db.commit()
    
    return dict()

    
def missingtoothX0050():
    
    
    chartid = int(common.getid(request.vars.chartid))
    toothid = common.getstring(request.vars.toothid)
    toothsection = common.getstring(request.vars.toothsection)
    toothnumber =int(common.getid(request.vars.toothnumber))
    doctorid = int(common.getid(request.vars.doctor))
    dentalprocedure = common.getstring(request.vars.dentalprocedure)
    chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    providerid = int(common.getid(request.vars.providerid))  
    procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    notes = common.getstring(request.vars.notes)
    procedureid = 1;
    if(len(procs) > 0):
        procedureid = int(common.getid(procs[0].id))        

    color = "#0000FF"
    # Get the color for Missing Tooth procedure
    rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    if(len(rows)>0):
        color = rows[0].color;
        
    x   = toothsections(toothnumber);

    for i in xrange(0,len(x)):
        xtoothid = x["sec" + str(i+1)]
        toothid = db.tooth.update_or_insert(((db.tooth.chartid == chartid)&(db.tooth.toothid==xtoothid)&(db.tooth.is_active==True)),
                                                  
                                                  chartid = chartid,
                                                  toothid = xtoothid,
                                                  toothsection = xtoothid,
                                                  toothnumber = toothnumber,
                                                  doctorid = doctorid,
                                                  procedureid = procedureid,
                                                  chartdate = chartdate,
                                                  p1=color,
                                                  p2=color,
                                                  p3=color,
                                                  p4=color,
                                                  p5=color,
                                                  p6=color,
                                                  p7=color,
                                                  p8=color,
                                                  l1=color,
                                                  l2=color,
                                                  l3=color,
                                                  l4=color,
                                                  e1=color,
                                                  notes=notes,
                                                  created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid
                                                  
                                              )


    db.commit()
    
    return dict()

def toothextractionX0010():
    chartid = int(common.getid(request.vars.chartid))
    toothid = common.getstring(request.vars.toothid)
    toothsection = common.getstring(request.vars.toothsection)
    toothnumber =int(common.getid(request.vars.toothnumber))
    doctorid = int(common.getid(request.vars.doctor))
    dentalprocedure = common.getstring(request.vars.dentalprocedure)
    chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    providerid = int(common.getid(request.vars.providerid))  
    procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    notes = common.getstring(request.vars.notes)
    
    procedureid = 1;
    if(len(procs) > 0):
        procedureid = int(common.getid(procs[0].id))        
          
    color = "#000000"
    # Get the color for Missing Tooth procedure
    rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    if(len(rows)>0):
        color = rows[0].color;
        
    x   = toothsections(toothnumber);

    for i in xrange(0,len(x)):
        xtoothid = x["sec" + str(i+1)]
        toothid = db.tooth.update_or_insert(((db.tooth.chartid == chartid)&(db.tooth.toothid==xtoothid)&(db.tooth.is_active==True)),
                                                  
                                                  chartid = chartid,
                                                  toothid = xtoothid,
                                                  toothsection = xtoothid,
                                                  toothnumber = toothnumber,
                                                  doctorid = doctorid,
                                                  procedureid = procedureid,
                                                  chartdate = chartdate,
                                                  p1=color,
                                                  p2=color,
                                                  p3=color,
                                                  p4=color,
                                                  p5=color,
                                                  p6=color,
                                                  p7=color,
                                                  p8=color,
                                                  l1=color,
                                                  l2=color,
                                                  l3=color,
                                                  l4=color,
                                                  e1=color,
                                                  notes=notes,
                                                  created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid
                                                  
                                              )


    db.commit()
    
    return dict()

def filling():
    
    chartid = int(common.getid(request.vars.chartid))
    toothid = common.getstring(request.vars.toothid)
    toothsection = common.getstring(request.vars.toothsection)
    toothnumber =int(common.getid(request.vars.toothnumber))
    doctorid = int(common.getid(request.vars.doctor))
    dentalprocedure = common.getstring(request.vars.dentalprocedure)
    chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    providerid = int(common.getid(request.vars.providerid))  
    procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    notes = common.getstring(request.vars.notes)  
    colors = common.getstring(request.vars.color)
    
    procedureid = 1;
    if(len(procs) > 0):
        procedureid = int(common.getid(procs[0].id))        
  
    defcolor = "#F7F2C6"
    color = defcolor
    
    p1color = defcolor
    p2color = defcolor
    p3color = defcolor
    p4color = defcolor
    p5color = defcolor
    p6color = defcolor
    p7color = defcolor
    p8color = defcolor
    p9color = defcolor
    p10color = defcolor
    l1color = defcolor
    l2color = defcolor
    l3color = defcolor
    l4color = defcolor
    e1color = defcolor
    
    # Get the color for Filling Tooth procedure
    rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    if(len(rows)>0):
        color = rows[0].color;
        
       
    surfsarr = colors.split('~')
    if((surfsarr[0] == "false")&(surfsarr[1] == "false")&(surfsarr[2] == "false")&(surfsarr[3] == "false")&(surfsarr[4] == "false")):
        response.flash = "Please select one or more of Buccal, Mesial, Lingual, Distal, Occlusal when selecting anyone of the Filling procedure for tooh "+ str(toothnumber)+"!"
        return dict
    
    tmparr = toothid.split('-');
    toothsecno = 0
    toothquad='XX'
    if(len(tmparr) == 3):
        toothsecno = int(tmparr[1])  #1,2,3,4,5,6,7,8,9,10
        toothquad  = tmparr[2]       #LL,LR,UL,UR
        
    
    #valid sections for one-surface filling arw 1,2,3,4,5 (circle sections)    
    if((toothsecno == 1)|(toothsecno == 2)|(toothsecno == 3)|(toothsecno == 4)|(toothsecno == 5)):
        
        for x in xrange(0,len(surfsarr)):
            if(surfsarr[x] == "false"):
                continue
            
            toothid = str(toothnumber) + "-" + str(x+1) + "-" + toothquad
            toothsection = str(x+1) + "-" + toothquad
            p1color = color
            l1color = color
            e1color = color
        
            xid = db.tooth.update_or_insert(((db.tooth.chartid == chartid)&(db.tooth.toothid==toothid)&(db.tooth.is_active==True)),
                                                  chartid = chartid,
                                                  toothid = toothid,
                                                  toothsection = toothsection,
                                                  toothnumber = toothnumber,
                                                  doctorid = doctorid,
                                                  procedureid = procedureid,
                                                  chartdate = chartdate,
                                                  p1=p1color,
                                                  p2=p2color,
                                                  p3=p3color,
                                                  p4=p4color,
                                                  p5=p5color,
                                                  p6=p6color,
                                                  p7=p7color,
                                                  p8=p8color,
                                                  l1=color,
                                                  l2=color,
                                                  l3=color,
                                                  l4=color,
                                                  e1=color,
                                                  notes=notes,
                                                  created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid
                                                  
                                              )
            db.commit()
    else:
        response.flash = "Invalid tooth section for Amalgam-one surface, primary!"

    
    return dict    




def colorchart():
    
    page = common.getpage(request.vars.page)
    chartid = int(common.getid(request.vars.chartid))
    toothid = common.getstring(request.vars.toothid)
    toothsection = common.getstring(request.vars.toothsection)
    toothnumber =int(common.getid(request.vars.toothnumber))
    doctorid = int(common.getid(request.vars.doctor))
    dentalprocedure = common.getstring(request.vars.dentalprocedure)
    chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    returnurl = common.getstring(request.vars.returnurl)
    material = common.getstring(request.vars.material)
    notes = common.getstring(request.vars.notes)
    procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    procedureid = 1;
    if(len(procs) > 0):
        procedureid = int(common.getid(procs[0].id))
        
    providerid = int(common.getid(request.vars.providerid))
    providername = common.getstring(request.vars.providername)
    patientname = common.getstring(request.vars.patientname)
    gender = common.getstring(request.vars.gender)
    age = int(common.getid(request.vars.age))
    
 
    
    formA = SQLFORM.factory(
        Field('chartdate', 'date', label='Date', default=chartdate, requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('toothid', 'string',label='Tooth ID',default=toothid),
        Field('toothnumber', 'integer', default=0),
        Field('doctor', 'integer', default=doctorid, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control'),  label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active == True)), 'doctor.id', '%(name)s')),
        Field('dentalprocedure', 'string',  widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control'), default="",label='Procedure',requires=IS_IN_DB(db((db.vw_dentalprocedure_chart.is_active == True)), 'vw_dentalprocedure_chart.proccode', '%(altshortdescription)s')),
        Field('chartid', 'integer',default=chartid ),
        Field('color', 'string',label='Color',default=""),
        Field('material', 'string',label='Material',default=""),
        Field('toothsection', 'string',label='Tooth Section',default=""),
        Field('p1', 'string',default=""),
        Field('p2', 'string',default=""),
        Field('p3', 'string',default=""),
        Field('p4', 'string',default=""),
        Field('p5', 'string',default=""),
        Field('p6', 'string',default=""),
        Field('p7', 'string',default=""),
        Field('p8', 'string',default=""),
        Field('p9', 'string',default=""),
        Field('l1', 'string',default=""),
        Field('l2', 'string',default=""),
        Field('l3', 'string',default=""),
        Field('l4', 'string',default=""),
        Field('e1', 'string',default=""),
        Field('notes', 'text',label='Notes',default=notes)
    )    
    
    formA.element('textarea[name=notes]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=notes]')['_rows'] = 5
    formA.element('textarea[name=notes]')['_class'] = 'form-control'

    xtoothid = formA.element('input',_id='no_table_toothid')
    xtoothid['_class'] =  'form-control '
    xtoothid['_placeholder'] = 'Enter tooth id' 
    xtoothid['_autocomplete'] = 'off'    


    xtoothnumber = formA.element('input',_id='no_table_toothnumber')
    xtoothnumber['_class'] =  'form-control '
    xtoothnumber['_placeholder'] = 'Enter tooth number' 
    xtoothnumber['_autocomplete'] = 'off'    

    xtoothsection = formA.element('input',_id='no_table_toothsection')
    xtoothsection['_class'] =  'form-control '
    xtoothsection['_placeholder'] = 'Enter tooth section' 
    xtoothsection['_autocomplete'] = 'off'    

    xcolor = formA.element('input',_id='no_table_color')
    xcolor['_class'] =  'form-control '
    xcolor['_placeholder'] = 'Enter tooth section' 
    xcolor['_autocomplete'] = 'off'    

    xmat = formA.element('input',_id='no_table_material')
    xmat['_class'] =  'form-control '
    xmat['_placeholder'] = 'Enter tooth section' 
    xmat['_autocomplete'] = 'off'    

    xchartdate = formA.element('input',_id='no_table_chartdate')
    xchartdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xchartdate['_data-date-format'] = 'dd/mm/yyyy'
    xchartdate['_autocomplete'] = 'off' 

    doc = formA.element('#no_table_doctor')
    doc['_class'] = 'form-control'
    doc['_style'] = 'width:100%'

    proc= formA.element('#no_table_dentalprocedure')
    proc['_class'] = 'form-control'
    proc['_style'] = 'width:100%'

    

    fn = dentalprocedures(dentalprocedure)
    
  
    chartds=db((db.tooth.chartid == chartid) & (db.tooth.is_active == True)).select()
    
    source = common.getstring(request.vars.source)

    return dict(formA=formA, page=page,returnurl=returnurl,providerid = providerid, providername = providername,chartid=chartid, chartds=chartds, patientname = patientname, gender=gender, age=age)

    


def chartSave():
    
    charttitle = common.getstring(request.vars.charttitle)
    chartdate = common.getstring(request.vars.chartdate)
    chartnotes = common.getstring(request.vars.chartnotes)
    patientname = common.getstring(request.vars.patientname)
    
    providerid = common.getid(request.vars.providerid)
    tplanid = common.getid(request.vars.tplanid)
    treatmentid = common.getid(request.vars.treatmentid)
    memberid = common.getid(request.vars.memberid)
    patientid = common.getid(request.vars.patientid)
    
    formA = SQLFORM.factory(
        Field('chartdate', 'date', label='Date', default=datetime.date.today(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('toothid', 'string',label='Tooth ID',default=""),
        Field('toothnumber', 'integer', default=0),
        Field('doctor', 'integer', default=doctorid, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control'),  label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active == True)), 'doctor.id', '%(name)s')),
        Field('dentalprocedure', 'string',  widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control'),  label='Procedure',requires=IS_IN_DB(db((db.vw_dentalprocedure_chart.is_active == True)), 'vw_dentalprocedure_chart.proccode', '%(altshortdescription)s')),
        Field('chartid', 'integer',default=chartid ),
        Field('color', 'string',label='Color',default=""),
        Field('material', 'string',label='Material',default=""),
        Field('toothsection', 'string',label='Tooth Section',default=""),
        Field('p1', 'string',default=""),
        Field('p2', 'string',default=""),
        Field('p3', 'string',default=""),
        Field('p4', 'string',default=""),
        Field('p5', 'string',default=""),
        Field('p6', 'string',default=""),
        Field('p7', 'string',default=""),
        Field('p8', 'string',default=""),
        Field('p9', 'string',default=""),
        Field('l1', 'string',default=""),
        Field('l2', 'string',default=""),
        Field('l3', 'string',default=""),
        Field('l4', 'string',default=""),
        Field('e1', 'string',default=""),
        Field('notes', 'text',label='Notes',default="")
    )    
    
    formA.element('textarea[name=notes]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=notes]')['_rows'] = 5
    formA.element('textarea[name=notes]')['_class'] = 'form-control'

    xtoothid = formA.element('input',_id='no_table_toothid')
    xtoothid['_class'] =  'form-control '
    xtoothid['_placeholder'] = 'Enter tooth id' 
    xtoothid['_autocomplete'] = 'off'    


    xtoothnumber = formA.element('input',_id='no_table_toothnumber')
    xtoothnumber['_class'] =  'form-control '
    xtoothnumber['_placeholder'] = 'Enter tooth number' 
    xtoothnumber['_autocomplete'] = 'off'    

    xtoothsection = formA.element('input',_id='no_table_toothsection')
    xtoothsection['_class'] =  'form-control '
    xtoothsection['_placeholder'] = 'Enter tooth section' 
    xtoothsection['_autocomplete'] = 'off'    

    xcolor = formA.element('input',_id='no_table_color')
    xcolor['_class'] =  'form-control '
    xcolor['_placeholder'] = 'Enter tooth section' 
    xcolor['_autocomplete'] = 'off'    

    xmat = formA.element('input',_id='no_table_material')
    xmat['_class'] =  'form-control '
    xmat['_placeholder'] = 'Enter tooth section' 
    xmat['_autocomplete'] = 'off'    

    xchartdate = formA.element('input',_id='no_table_chartdate')
    xchartdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xchartdate['_data-date-format'] = 'dd/mm/yyyy'
    xchartdate['_autocomplete'] = 'off' 

    doc = formA.element('#no_table_doctor')
    doc['_class'] = 'form-control'
    doc['_style'] = 'width:100%'

    proc= formA.element('#no_table_dentalprocedure')
    proc['_class'] = 'form-control'
    proc['_style'] = 'width:100%'
    
    return dict()

def chartClear():

    charturl = common.getstring(request.vars.charturl)    
    chartfile = common.getstring(request.vars.chartfile)    
    destchartfile = common.getstring(request.vars.destchartfile)    
    
    appPath = request.folder    
    srcchartfile = os.path.join(appPath, 'static/images','dentalchart.jpg') 
    
    
    if(os.path.isfile(destchartfile)):
        os.remove(destchartfile)
        
    copyfile(srcchartfile,destchartfile);

    
    return dict(charturl=charturl,chartfile=chartfile,destchartfile=destchartfile)
    
    



def saveImage():
    
    
    imagex = request.vars.image
    destchartfile = request.vars.destchartfile
 
    with open(destchartfile,"wb+") as f:
        f.write(decodestring(imagex))  
        
        
    
    return dict()

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def dentalchart():
    
    page = int(common.getid(request.vars.page))
    
    providerid = int(common.getid(request.vars.providerid))
    providerdict = common.getproviderfromid(db, providerid)
    providername = providerdict["providername"]

    patientid = int(common.getid(request.vars.patientid))
    memberid = int(common.getid(request.vars.memberid))

    doctorid = int(common.getid(request.vars.doctorid))
    treatmentid = int(common.getid(request.vars.treatmentid))   

    patientname = ""
    age = ""
    gender = ""
    
    r = db((db.vw_memberpatientlist.providerid == providerid) & (db.vw_memberpatientlist.patientid == patientid) & (db.vw_memberpatientlist.primarypatientid == memberid)).select()
    if(len(r) > 0):
        patientname = r[0].patient
        gender = r[0].gender
        age = int(common.getid(r[0].age))
    


    chartid = int(common.getid(request.vars.chartid))
    
    if(chartid == 0):
        chartid = db.dentalchart.update_or_insert(((db.dentalchart.providerid == providerid)&(db.dentalchart.patientid==patientid)&(db.dentalchart.memberid==memberid)),\
                                                  providerid = providerid,\
                                                  patientid = patientid,\
                                                  memberid = memberid,\
                                                  is_active = True,\
                                                  created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid
                                                  
                                                  )
        if(chartid == None):
            rows = db(((db.dentalchart.providerid == providerid)&(db.dentalchart.patientid==patientid)&(db.dentalchart.memberid==memberid))).select(db.dentalchart.id)
            if(len(rows)>0):
                chartid = int(common.getid(rows[0].id))
            else:
                chartid = 0
                
    
    
    #Field('dentalprocedure', 'integer',  widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control'),  label='Doctor',requires=IS_IN_DB(db((db.vw_dentalprocedure_chart.is_active == True)), 'vw_dentalprocedure_chart.id', '%(altshortdescription)s')),
    
    formA = SQLFORM.factory(
        Field('chartdate', 'date', label='Date', default=datetime.date.today(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
        Field('toothid', 'string',label='Tooth ID',default=""),
        Field('toothnumber', 'integer', default=0),
        Field('doctor', 'integer', default=doctorid, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control'),  label='Doctor',requires=IS_IN_DB(db((db.doctor.providerid==providerid)&(db.doctor.is_active == True)), 'doctor.id', '%(name)s')),
        Field('dentalprocedure', 'string',  widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='form-control'),  label='Procedure',requires=IS_IN_DB(db((db.vw_dentalprocedure_chart.is_active == True)), 'vw_dentalprocedure_chart.proccode', '%(altshortdescription)s')),
        Field('chartid', 'integer',default=chartid ),
        Field('color', 'string',label='Color',default=""),
        Field('material', 'string',label='Material',default=""),
        Field('toothsection', 'string',label='Tooth Section',default=""),
        Field('p1', 'string',default=""),
        Field('p2', 'string',default=""),
        Field('p3', 'string',default=""),
        Field('p4', 'string',default=""),
        Field('p5', 'string',default=""),
        Field('p6', 'string',default=""),
        Field('p7', 'string',default=""),
        Field('p8', 'string',default=""),
        Field('p9', 'string',default=""),
        Field('l1', 'string',default=""),
        Field('l2', 'string',default=""),
        Field('l3', 'string',default=""),
        Field('l4', 'string',default=""),
        Field('e1', 'string',default=""),
        Field('notes', 'text',label='Notes',default="")
    )    
    
    formA.element('textarea[name=notes]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=notes]')['_rows'] = 5
    formA.element('textarea[name=notes]')['_class'] = 'form-control'

    xtoothid = formA.element('input',_id='no_table_toothid')
    xtoothid['_class'] =  'form-control '
    xtoothid['_placeholder'] = 'Enter tooth id' 
    xtoothid['_autocomplete'] = 'off'    


    xtoothnumber = formA.element('input',_id='no_table_toothnumber')
    xtoothnumber['_class'] =  'form-control '
    xtoothnumber['_placeholder'] = 'Enter tooth number' 
    xtoothnumber['_autocomplete'] = 'off'    

    xtoothsection = formA.element('input',_id='no_table_toothsection')
    xtoothsection['_class'] =  'form-control '
    xtoothsection['_placeholder'] = 'Enter tooth section' 
    xtoothsection['_autocomplete'] = 'off'    

    xcolor = formA.element('input',_id='no_table_color')
    xcolor['_class'] =  'form-control '
    xcolor['_placeholder'] = 'Enter tooth section' 
    xcolor['_autocomplete'] = 'off'    

    xmat = formA.element('input',_id='no_table_material')
    xmat['_class'] =  'form-control '
    xmat['_placeholder'] = 'Enter tooth section' 
    xmat['_autocomplete'] = 'off'    

    xchartdate = formA.element('input',_id='no_table_chartdate')
    xchartdate['_class'] =  'input-group form-control form-control-inline date-picker'
    xchartdate['_data-date-format'] = 'dd/mm/yyyy'
    xchartdate['_autocomplete'] = 'off' 

    doc = formA.element('#no_table_doctor')
    doc['_class'] = 'form-control'
    doc['_style'] = 'width:100%'

    proc= formA.element('#no_table_dentalprocedure')
    proc['_class'] = 'form-control'
    proc['_style'] = 'width:100%'

    toothcolors = None
    
    if formA.accepts(request,session,keepvalues=True):
        chartid = int(common.getid(request.vars.chartid))
        treatmentid = int(common.getid(request.vars.treatmentid))
        doctorid = int(common.getid(request.vars.doctor))
        procedureid = 0
        proccode = common.getstring(request.vars.dentalprocedure)
        r = db(db.vw_dentalprocedure_chart.proccode == proccode).select()
        if(len(r)>0):
            procedureid = int(common.getid(r[0].id))
        
        
        dt = datetime.datetime.strptime(request.vars.chartdate, "%d/%m/%Y")
        chartdate = common.getdt(dt)
        toothid = common.getstring(request.vars.toothid)
        toothnumber = common.getstring(request.vars.toothnumber)
        toothsection = common.getstring(request.vars.toothsection)
        notes = common.getstring(request.vars.notes)
        color = common.getstring(request.vars.color)
        material = common.getstring(request.vars.material)
        
        #color = <pcolor1>;<pcolor2> | <lcolor1>;<lcolor2> | <ecolor1>;<ecolor2>
        colorarr = color.split("|")
        p1=""
        p2=""
        p3=""
        p4=""
        p5=""
        p6=""
        p7=""
        p8=""
        p9=""
        l1=""
        l2=""
        l3=""
        l4=""
        e1=""
         
        if(len(colorarr)>=1):
            parr = colorarr[0].split(";")
            if(len(parr)>=1):
                p1 = parr[0]

            if(len(parr)>=2):
                p2 = parr[1]

            if(len(parr)>=3):
                p3 = parr[2]
        
            if(len(parr)>=4):
                p4 = parr[3]
            
            if(len(parr)>=5):
                p5 = parr[4]

            if(len(parr)>=6):
                p6 = parr[5]

            if(len(parr)>=7):
                p7 = parr[6]

            if(len(parr)>=8):
                p8 = parr[7]
                
            if(len(parr)>=9):
                p9 = parr[8]
                
        if(procedureid >0):
        
            xid = db.tooth.update_or_insert(((db.tooth.toothid == toothid)&(db.tooth.chartid == chartid)&(db.tooth.procedureid == procedureid)),\
                                            toothid = toothid, toothnumber = toothnumber, chartid = chartid, doctorid = doctorid, procedureid=procedureid, treatmentid=treatmentid,\
                                            toothsection = toothsection, chartdate = chartdate, notes=notes, \
                                            p1=p1,p2=p2,p3=p3,p4=p4,p5=p5,p6=p6,p7=p7,p8=p8,p9=p9,l1=l1,l2=l2,l3=l3,l4=l4,e1=e1,\
                                            is_active = True,\
                                            created_on = common.getISTFormatCurrentLocatTime(), created_by = providerid, modified_on = common.getISTFormatCurrentLocatTime(), modified_by = providerid
                                            )
        else:
            response.flash = "Dental Procedure Error in saving Dental Chart!"
        

    elif formA.errors:
        response.flash = "Errors: " +  str(formA.errors)
    else:
        k = 0
        
    chartds=db((db.tooth.chartid == chartid) & (db.tooth.is_active == True)).select()
    
    #toothcolors = db((db.toothcolor.providerid == providerid) & (db.toothcolor.is_active == True)).select()
    #toothcolors = db((db.toothcolor.is_active == True)).select()
    source = common.getstring(request.vars.source)
    if(source == 'treatment'):
        returnurl = URL('treatment', 'update_treatment', vars=dict(page=page,imagepage=0,providerid=providerid,treatmentid=treatmentid))
    else:
        returnurl = URL('treatment', 'update_treatment', vars=dict(page=page,imagepage=0,providerid=providerid,treatmentid=treatmentid))
        
    return dict(formA=formA, page=page,returnurl=returnurl,providerid = providerid, providername = providername,chartid=chartid, chartds=chartds, patientname = patientname, gender=gender, age=age)

    
#def fillingX0022():

    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict    

#def fillingX0022():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    

#def fillingX0023():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #notes = common.getstring(request.vars.notes)    
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    

#def fillingX0024():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    

#def fillingX0025():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
        #tmparr = toothid.split('-');
        #toothsecno = 0
        #if(len(tmparr) == 3):
            #toothsecno = int(tmparr[1])
    
        ##valid sections for one-surface filling arw 1,2,3,4,5 (circle sections)    
        #if((toothsecno == 1)|(toothsecno == 2)|(toothsecno == 3)|(toothsecno == 4)|(toothsecno == 5)):
            #p1color = color
            #l1color = color
            #e1color = color
            
            #toothid = db.tooth.update_or_insert(((db.tooth.chartid == chartid)&(db.tooth.toothid==toothid)&(db.tooth.is_active==True)),
                                                      #chartid = chartid,
                                                      #toothid = toothid,
                                                      #toothsection = toothsection,
                                                      #toothnumber = toothnumber,
                                                      #doctorid = doctorid,
                                                      #procedureid = procedureid,
                                                      #chartdate = chartdate,
                                                      #p1=p1color,
                                                      #p2=p2color,
                                                      #p3=p3color,
                                                      #p4=p4color,
                                                      #p5=p5color,
                                                      #p6=p6color,
                                                      #p7=p7color,
                                                      #p8=p8color,
                                                      #l1=color,
                                                      #l2=color,
                                                      #l3=color,
                                                      #l4=color,
                                                      #e1=color,
                                                      #notes=notes,
                                                      #created_on = datetime.date.today(), created_by = providerid, modified_on = datetime.date.today(), modified_by = providerid
                                                      
                                                  #)
            #db.commit()
        #else:
            #response.flash = "Invalid tooth section for Amalgam-one surface, permanent!"
    
   

    #return dict()    

#def fillingX0026():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    

#def fillingX0027():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    

#def fillingX0028():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    

#def fillingX0029():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #tmparr = toothid.split('-');
    #toothsecno = 0
    #if(len(tmparr) == 3):
        #toothsecno = int(tmparr[1])

    ##valid sections for one-surface filling arw 1,2,3,4,5 (circle sections)    
    #if((toothsecno == 1)|(toothsecno == 2)|(toothsecno == 3)|(toothsecno == 4)|(toothsecno == 5)):
        #p1color = color
        #l1color = color
        #e1color = color
        
        #toothid = db.tooth.update_or_insert(((db.tooth.chartid == chartid)&(db.tooth.toothid==toothid)&(db.tooth.is_active==True)),
                                                  #chartid = chartid,
                                                  #toothid = toothid,
                                                  #toothsection = toothsection,
                                                  #toothnumber = toothnumber,
                                                  #doctorid = doctorid,
                                                  #procedureid = procedureid,
                                                  #chartdate = chartdate,
                                                  #p1=p1color,
                                                  #p2=p2color,
                                                  #p3=p3color,
                                                  #p4=p4color,
                                                  #p5=p5color,
                                                  #p6=p6color,
                                                  #p7=p7color,
                                                  #p8=p8color,
                                                  #l1=color,
                                                  #l2=color,
                                                  #l3=color,
                                                  #l4=color,
                                                  #e1=color,
                                                  #notes=notes,
                                                  #created_on = datetime.date.today(), created_by = providerid, modified_on = datetime.date.today(), modified_by = providerid
                                                  
                                              #)
        #db.commit()
    #else:
        #response.flash = "Invalid tooth section for Resin-one surface, anterior!"


    #return dict()    

#def fillingX0030():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    

#def fillingX0031():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    

#def fillingX0032():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    

#def fillingX0033():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
        #tmparr = toothid.split('-');
        #toothsecno = 0
        #if(len(tmparr) == 3):
            #toothsecno = int(tmparr[1])
    
        ##valid sections for one-surface filling arw 1,2,3,4,5 (circle sections)    
        #if((toothsecno == 1)|(toothsecno == 2)|(toothsecno == 3)|(toothsecno == 4)|(toothsecno == 5)):
            #p1color = color
            #l1color = color
            #e1color = color
            
            #toothid = db.tooth.update_or_insert(((db.tooth.chartid == chartid)&(db.tooth.toothid==toothid)&(db.tooth.is_active==True)),
                                                      #chartid = chartid,
                                                      #toothid = toothid,
                                                      #toothsection = toothsection,
                                                      #toothnumber = toothnumber,
                                                      #doctorid = doctorid,
                                                      #procedureid = procedureid,
                                                      #chartdate = chartdate,
                                                      #p1=p1color,
                                                      #p2=p2color,
                                                      #p3=p3color,
                                                      #p4=p4color,
                                                      #p5=p5color,
                                                      #p6=p6color,
                                                      #p7=p7color,
                                                      #p8=p8color,
                                                      #l1=color,
                                                      #l2=color,
                                                      #l3=color,
                                                      #l4=color,
                                                      #e1=color,
                                                      #notes=notes,
                                                      #created_on = datetime.date.today(), created_by = providerid, modified_on = datetime.date.today(), modified_by = providerid
                                                      
                                                  #)
            #db.commit()
        #else:
            #response.flash = "Invalid tooth section for Resin-one surface, posterior-primary, permanent!"
    


    #return dict()    

#def fillingX0034():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    

#def fillingX0035():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #notes = common.getstring(request.vars.notes)    
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    

#def fillingX0036():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    

#def fillingX0037():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    

#def fillingX0038():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    

#def fillingX0039():
    
    #chartid = int(common.getid(request.vars.chartid))
    #toothid = common.getstring(request.vars.toothid)
    #toothsection = common.getstring(request.vars.toothsection)
    #toothnumber =int(common.getid(request.vars.toothnumber))
    #doctorid = int(common.getid(request.vars.doctor))
    #dentalprocedure = common.getstring(request.vars.dentalprocedure)
    #chartdate = datetime.datetime.strptime(common.getstring(request.vars.chartdate),"%d/%m/%Y")
    #providerid = int(common.getid(request.vars.providerid))  
    #procs = db((db.dentalprocedure_chart.procedurecode == dentalprocedure)&(db.dentalprocedure_chart.is_active == True)).select()
    #notes = common.getstring(request.vars.notes)    
    #procedureid = 1;
    #if(len(procs) > 0):
        #procedureid = int(common.getid(procs[0].id))        
  
    #defcolor = "#F7F2C6"
    #color = defcolor
    
    #p1color = defcolor
    #p2color = defcolor
    #p3color = defcolor
    #p4color = defcolor
    #p5color = defcolor
    #p6color = defcolor
    #p7color = defcolor
    #p8color = defcolor
    #p9color = defcolor
    #p10color = defcolor
    #l1color = defcolor
    #l2color = defcolor
    #l3color = defcolor
    #l4color = defcolor
    #e1color = defcolor
    
    ## Get the color for Missing Tooth procedure
    #rows = db((db.dentalprocedure_chart.procedurecode == dentalprocedure) & (db.dentalprocedure_chart.is_active == True)).select()
    #if(len(rows)>0):
        #color = rows[0].color;
        
    #x   = toothsections(toothnumber);

    #return dict()    
    