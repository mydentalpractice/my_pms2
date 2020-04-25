# -*- coding: utf-8 -*-
import sys
import datetime
import requests




# defining the api-endpoint 
API_ENDPOINT = "http://127.0.0.1:8001/my_pms2/mdpapi/mdpapi"
#API_ENDPOINT = "http://stagingserver.pythonanywhere.com/my_pms2/mdpapi/mdpapi"
 
# data to be sent to api
data = {'action':'groupsmsmessage'}

# sending post request and saving response as response object
r = requests.post(url = API_ENDPOINT, data = data)
 
# extracting response text 
y = r.text

x = datetime.datetime.today().strftime("%d\%m\%Y %H:%M")
sys.stdout = open('c:\\web2pysrc\\web2py\\Applications\\my_pms2\\pms2log.txt', 'a')

print("Post Response " + str(r) + " on" + x)
