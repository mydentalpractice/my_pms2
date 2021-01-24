from gluon import current
db = current.globalenv['db']

import json

import requests
import urllib
import base64
import hashlib
import uuid

import random



from applications.my_pms2.modules import common
from applications.my_pms2.modules import mdputils
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import account

from applications.my_pms2.modules import logger





class DataSecurity:
    def __init__(self):
        return 

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

   

  




   
