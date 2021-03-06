from gluon import current
db = current.globalenv['db']

import json

import requests
import urllib
import base64
import hashlib
import uuid
import hmac
import random



from applications.my_pms2.modules import common
from applications.my_pms2.modules import mdputils
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import account

from applications.my_pms2.modules import logger


#key = '080f73a76d6e049bed04da6f79e711'
#key_byte = bytes(key, 'utf-8')
#signature = ''
#params = urllib.parse.parse_qsl(qs='orderId=TXN95&shopSeTxnId=S0309202014423579899&status=failed&statusCode=4&statusMessage=Cancelled%20by%20user&currentTime=1599144302548&signature=eMJj%2FsI%2BEmgPmyCkrn83ZXd5WTDEJOQ9TxwRadpwjL8%3D', keep_blank_values=False, strict_parsing=False, encoding='utf-8', errors='replace', max_num_fields=None) 
## params = 'orderId=TXN95&shopSeTxnId=S0309202014423579899&status=failed&statusCode=4&statusMessage=Cancelled%20by%20user&currentTime=1599144302548&signature=eMJj%2FsI%2BEmgPmyCkrn83ZXd5WTDEJOQ9TxwRadpwjL8%3D'
#qs = 'orderId=TXN95&shopSeTxnId=S0309202014423579899&status=failed&statusCode=4&statusMessage=Cancelled%20by%20user&currentTime=1599144302548&signature=eMJj%2FsI%2BEmgPmyCkrn83ZXd5WTDEJOQ9TxwRadpwjL8%3D'
#params = {}
#encoded_sorted = []
#signature = ''
#for key in qs.split('&'):
    #p = key.split('=')
    #params[p[0]] = p[1]

#resp = json.loads(json.dumps(params))

#print(resp)

#qstr = 'currentTime=' + resp.get('currentTime') + \
       #'&orderId=' + resp.get('orderId') + \
       #'&shopSeTxnId=' + resp.get('shopSeTxnId') + \
       #'&status=' + resp.get('status') + \
       #'&statusCode=' + resp.get('statusCode') + \
       #'&statusMessage=' 
       
#print(urllib.parse.quote(resp.get('statusMessage')))
#print(urllib.parse.unquote(resp.get('statusMessage')))
#en_q_str = urllib.parse.quote(qstr) + urllib.parse.quote_plus(urllib.parse.unquote(resp.get('statusMessage')))
#print(en_q_str)
#print(en_q_str.encode('utf-8'))

#shopse_generated_signature = resp.get('signature')
#print(shopse_generated_signature)
#h = hmac.new(key_byte, en_q_str.encode('utf-8'), hashlib.sha256)
#my_generated_signature = urllib.parse.quote_plus(base64.b64encode(h.digest()).decode())
#print(my_generated_signature)
#print(my_generated_signature == shopse_generated_signature)


class DataSecurity:
    def __init__(self):
        return 

    def encrypt_sha256_shopse(self,message,key):
        
        bkey = bytes(key)
        #bkey = key.encode()   
        
        message = message.encode('utf-8')    
        #params = urllib.parse.parse_qsl(qs=self.params, keep_blank_values=False, strict_parsing=False, encoding='utf-8', errors='replace', max_num_fields=None) 
        
        #signature = hmac.new(bkey, message, hashlib.sha256).hexdigest()
        
        h = hmac.new(bkey, message, hashlib.sha256)
        signature = urllib.quote_plus(base64.b64encode(h.digest()).decode())        
        signature1 = urllib.quote_plus(base64.b64encode(h.digest()))
                                       
        jsonresp = {
                        "encrypt": signature
        
                    }        

        return json.dumps(jsonresp)

        
    #encrypt sha256 + base64 encode
    def xencrypt_sha256_shopse(self,raw):

        #phpurl = "http://myphp.com/myphp.php"
        phpurl = "http://myphp.com/encrypt_sha256_shopse.php"
        dsobj = {"raw":raw}

        resp = requests.post(phpurl,json=dsobj)
        
        jsonresp = {}
        if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respobj = resp.json()  
            e = respobj["encrypt"]
            e = urllib.quote(e.encode('utf-8'))
            
            jsonresp = {
                "encrypt": e

            }
        else:
            jsonresp={"encrypt": "Response Error - " + str(resp.status_code)}

        return json.dumps(jsonresp)

    #encrypt sha256 + base64 encode
    def xencrypts_sha256_shopse(self,raw):

        phpurl = "http://myphp.com/encrypt_sha256_shopse.php"

        dsobj = {"raw":raw}

        resp = requests.post(phpurl,json=dsobj)

        jsonresp = {}
        if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respobj = resp.json() 
            e = respobj["encrypt"]
            e = urllib.quote(e.encode('utf-8'))            
            jsonresp = {
                "encrypt": e

            }
        else:
            jsonresp={"encrypt": "Response Error - " + str(reps.status_code)}

        return jsonresp["encrypt"]




    #this method - encrypts  AES-256-CBC + base64 encode
    def encrypts(self,raw):

        phpurl = "http://myphp.com/encrypt.php"
        #phpurl = "http://localhost/encrypt.php"

        dsobj = {"raw":raw}

        resp = requests.post(phpurl,json=dsobj)

        jsonresp = {}
        if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respobj = resp.json()    
            jsonresp = {
                "encrypt": respobj["encrypt"]

            }
        else:
            jsonresp={"encrypt": "Response Error - " + str(reps.status_code)}

        return jsonresp["encrypt"]

    #this method - encrypts  AES-256-CBC + base64 encode
    def encrypt(self,raw):

        phpurl = "http://myphp.com/encrypt.php"
        #phpurl = "http://localhost/encrypt.php"

        dsobj = {"raw":raw}

        resp = requests.post(phpurl,json=dsobj)

        jsonresp = {}
        if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respobj = resp.json()    
            jsonresp = {
                "encrypt": respobj["encrypt"]

            }
        return json.dumps(jsonresp)

    #base64 Decode + Decrypt AES-256-CBC
    def decrypts(self,encrypt):


        phpurl = "http://myphp.com/decrypt.php"
        #phpurl = "http://localhost/decrypt.php"

        dsobj = {"encrypt":encrypt}

        resp = requests.post(phpurl,json=dsobj)

        jsonresp = {}
        if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respobj = resp.json()    
            jsonresp = {
                "raw": respobj["raw"]
            }
        else:
            jsonresp = {"raw":"Request Error - " + str(resp.status_code)}

        return jsonresp["raw"]

    #base64 Decode + Decrypt AES-256-CBC
    def decrypt(self,encrypt):

        phpurl = "http://myphp.com/decrypt.php"
        #phpurl = "http://localhost/decrypt.php"

        dsobj = {"encrypt":encrypt}

        resp = requests.post(phpurl,json=dsobj)

        jsonresp = {}
        if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respobj = resp.json()    
            jsonresp = {
                "raw": respobj["raw"]
            }
        return json.dumps(jsonresp)  


    #This method 
    #stringify json obj
    #encrypt stringified json obj
    #base64 encode
    #return {"req_data":<encoded encrypted json data}
    def encoderequestdata(self,jsondata):
        jsonstr = json.dumps(jsondata)
        jsonstrencrypt = self.encrypts(jsonstr)
        #jsonstrencoded = base64.b64encode(jsonstrencrypt)
        #jsonstrdecrypt = self.decrypts(jsonstrencrypt)
        reqobj = {"req_data":jsonstrencrypt}

        return reqobj  

    def decoderesponsedata(self,jsondatastr):
        #jsonstrdecoded = base64.b64decode(jsondatastr)

        jsonstrdecrypt = self.decrypts(jsondatastr)
        jsondata = json.loads(jsonstrdecrypt)
        return jsondata



    def encrypts128(self,raw):

        phpurl = "http://myphp128.com/encrypt.php"
        #phpurl = "http://localhost/encrypt128.php"

        dsobj = {"raw":raw}

        resp = requests.post(phpurl,json=dsobj)

        jsonresp = {}
        if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respobj = resp.json()    
            jsonresp = {
                "encrypt": respobj["encrypt"]

            }
        else:
            jsonresp={"encrypt": "Response Error - " + str(resp.status_code)}

        return jsonresp["encrypt"]    

    def decrypts128(self,encrypt):    
        phpurl = "http://myphp128.com/decrypt.php"
        #phpurl = "http://localhost/decrypt128.php"

        dsobj = {"encrypt":encrypt}

        resp = requests.post(phpurl,json=dsobj)

        jsonresp = {}
        if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respobj = resp.json()    
            jsonresp = {
                "raw": respobj["raw"]
            }
        else:
            jsonresp = {"raw":"Request Error - " + str(resp.status_code)}

        return jsonresp["raw"]



    def encrypt_login(self,action,providerid,username,password):

        request_data = {"action":action, "providerid":providerid,"username":username, "password":password}
        request_data_string = json.dumps(request_data)
        encrypt_string = self.encrypts(request_data_string)


        return encrypt_string

   

  




   
