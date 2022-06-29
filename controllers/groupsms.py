from gluon import current
db = current.globalenv['db']
#
from applications.my_pms2.modules import tasks
from applications.my_pms2.modules import logger

def callgroupsms():
    
    logger.loggerpms2("Enter CallGroupSMS")
    tasks.sendGroupSMS(db, request.folder)
    
    return dict()