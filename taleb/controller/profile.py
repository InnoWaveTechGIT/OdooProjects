from odoo import http
# from werkzeug.wrappers import Response
import logging
from datetime import datetime
import xmlrpc.client as xmlrpclib
import json
from odoo import models, fields, api
from datetime import datetime ,date
import math
import os
import requests
from odoo.http import request ,Response
# from odoo.http import JsonRequest
import jwt
import re
import werkzeug.wrappers
import os
import time
import base64
from os import path
from pathlib import Path
import re
import math
from telesign.messaging import MessagingClient
from . import verfiy_token
from os import environ
from dotenv import load_dotenv
load_dotenv()
_logger = logging.getLogger(__name__)
def check_phone_num(self,data):
            val=data

            if val.isdigit():

                return True

            else:
                return False

def false2empty(self,data):
        result = {}
        result1 = []
        for i in data:
            
            for key, value in i.items():
                if(value is False and key !=  "is_default" and key != 'is_active'):
                    value = ''
                result[key] = value
            result1.append(result)
        return result1


def validation_email(self,email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if(re.fullmatch(regex, email)):
            
            return True
        else:
            
            return False

def _abs_rout(self,data):
    path1=''
    

    abs = os.path.dirname(os.path.abspath(__file__))
    abs_sp =abs.split("/")
    
    for i in abs_sp:
        if i != 'controller':
            path1 += i +'/'
        
    return path1

class Profile(http.Controller):
    url = os.getenv('URL')
    db = os.getenv('db')
    username = os.getenv('username')
    password = os.getenv('password')

        
    def _send_sms (self,message,phone_number,code, country_code):
        if country_code and '249' in country_code:
            return False
        elif country_code and not '963' in country_code:
            # customer_id = os.getenv('CUSTOMER_ID', '23E479A9-FC5B-4FEC-A17F-D7182D09148B')
            # api_key = os.getenv('API_KEY', 'AKpnGihB7+DGPNosTd0+F5rgSuKpsFWOD52ha9vw/SvF2lwK7uzP/6q3ZYHSTuEaBc2ZlTzXIzwpHQsUNj61uA==')
            # phone = os.getenv('PHONE_NUMBER', phone_number)
            # message = message + code
            # messaging = MessagingClient(customer_id,api_key)
            # response =  messaging.message(phone,message,"ARN")
            # return response
            return False

         
        else:
            url = f'https://syservices.talebeduction.com/api/sms/send_sms/{code}/{phone_number}/Taleb Edu/Taleb1/P@123456/Taleb1_T1'
            response = requests.get(url = url)
            return response
    
    @http.route('/add_photo',  auth="public",csrf=False, website=True, methods=['POST'])
    def add_photo(self,personal_image= None, **kw):
        # jpeg  png  jpg
        
        blob = personal_image.read() 
        size = len(blob) 
        
        
        if size > 10292205:
            response = json.dumps({ 'data': [], 'message':'حجم الصورة كبير'})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        data = os.path.dirname(os.path.abspath(__file__))
        authe = request.httprequest.headers
        token = authe['Authorization'].replace('Bearer ', '')
        image_file_name=personal_image.filename
        
        image_type = personal_image.filename.split(".") 
        types =['jpeg','JPEG','png','PNG','jpg','JPG']
        if image_type[1] in types :
            
            
            try:
                dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!','errrror':e})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

            
            id = dec_token['id']
            login=dec_token['login']
            fields={}
            if verfiy_token.verfiy_token (self,token,str(id)) ==False:
                response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            uid = common.authenticate(self.db, self.username, self.password, {})
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
            user = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',[[['id', '=', id]]], {'fields':  ['name','image_path',]})
            if(personal_image != None ):
                
                fields['image_file_name']=image_file_name.replace(" ", "")

                time_stamp = str(time.time())
                # module_path = "/home/vps112/odoo_16/torbetodoo/torbet_app/static/" #servar

                module_path = _abs_rout(self ,data)+"static/personal_images"#loc
                isExist = os.path.exists(module_path)
                
                
                
                
                if isExist == False:
                    os.mkdir(module_path)
                personal_image= base64.encodebytes(blob)
                fields["personal_image"] = personal_image

                
                
                fields["image_full_url"] = module_path + '/' + \
                time_stamp+image_file_name.replace(" ", "")
                fields["image_path"] = "/taleb/static/" + \
                    time_stamp+fields["image_file_name"].replace(" ", "")
                
            

                # 
                
                
            elif personal_image == None:
                
                return True
            else:
                
                fields['image_file_name']=""
                fields["personal_image"]=""
                return True
            
            
            write = models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[id],fields])
            user = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',[[['id', '=', id]]], {'fields':  ['name','image_full_url','image_path']})
            
            
            img_url1 = user[0]['image_path']
            
            img_url = self.url+user[0]['image_full_url']
            response = json.dumps({ 'message': 'تم تغيير الصورة' , 'image_url' : img_url1})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        else:
            response = json.dumps({ 'data': [], 'message':'يرجى رفع صورة من نمط jpeg  png  jpg  '})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

    @http.route('/edit_profile',  auth="public",csrf=False, website=True, methods=['POST'])
    def edit_profile(self, **kw):
        

        authe = request.httprequest.headers
    
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        
        except Exception as e:
            response = json.dumps({ 'data': 'no data', 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        id = dec_token['id']
        login=dec_token['login']
        
        fields={}
        if verfiy_token.verfiy_token (self,token,str(id)) ==False:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        
        change_phone =False
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))        
        body =json.loads(request.httprequest.data)
        counter_=0
        
        check_blocked_student=models.execute_kw(self.db,uid,self.password,'block.student','search_read', [['&',['user_id' , '=' , id],['block','=',True]]], {
                                        'fields': [ 'id']})
        if check_blocked_student!=[]:
            response=json.dumps({"messsage":" الطالب محظور من التقييم يرجى مراسلة الدعم "})
            return Response(
                    
                    response, status=460,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
        
        
            
        if 'full_name' in body:
            
            
            fields['name']=body['full_name']
        if 'father_name' in body:
            
            fields['father_name']=body['father_name']
        if 'password'in body:
            
            password=body['password']
        else :
            
            response = json.dumps({'data':[], 'message': 'يرجى ادخال كلمة المرور '})
            return Response(response,
        status=200,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    )
            
        if 'phone' in body :
            if 'country_code' not in body :
            
                response = json.dumps({'data':[], 'message': 'يرجى ادخال حقل رمز البلد   '})
                return Response(response,
            status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
            
            else :
                check_phone=check_phone_num(self,body['phone'])
                if check_phone == False:
                    response = json.dumps({"data":[],'message': 'رقم الهاتف يحتوي على محارف'})
                    return Response(
                    response, status=422,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
                
                fields['login']=str(body['country_code'])+body['phone']
                fields['country_code']=body['country_code']
                if fields['country_code']!='00963':
                    fields['state_id']=""
                    fields['location_id']=""
        
                        
        if 'email' in body :
            if body['email']!="":
                if validation_email(self,body['email']) == True:
                
                    fields['email']=body['email']
                else :
                    response=json.dumps({"data": [],"message":"example@gmail.com تم ادخال بريد الكتروني خاطئ يرجى ادخال حساب اخر على الشكل التالي "})
                    return Response( response,
                    headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                    )
        
        
        
        if 'state' in body:
            if 'country_code' not in body:
                response = json.dumps({'data':[], 'message': 'يرجى ادخال حقل رمز البلد   '})
                return Response(response,
            status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
            else :    
                if body['country_code']!='00963':
                    fields['state_id']=""
                    
                else :
                    
                    fields['country_code'] = body['country_code']
                    if body['state']!="":
                        state =  int(body['state'])
                    else :
                        state=""
                    fields['state_id'] = state
                    check_modified_location=True
        
        if 'location' in body:
            if 'country_code' not in body:
                response = json.dumps({'data':[], 'message': 'يرجى ادخال حقل رمز البلد   '})
                return Response(response,
            status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
            else :
                if body['country_code']!='00963':
                    fields['location_id']=""
                    
                else :
                    
                    fields['country_code'] = body['country_code']
                    
                    if body['location']!="":
                        location_id=int(body['location'])
                    else :
                        location_id=""
                        
                    fields['location_id']=location_id
                    check_modified_location=True
            
            

    #check empty fields
        for key in body:
            if key=='father_name':
                    
                if len(body[key]) >0:
                    pass
                else :
                    response = json.dumps({'data':[], 'message': ' يرجى ادخال حقل اسم الأب '})
                    return Response(response,
                status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

            
            if key=='full_name':    
                if len(body[key]) >0:
                    pass
                else :
                    response = json.dumps({'data':[], 'message': 'يرجى ادخالل حقل الأسم   '})
                    return Response(response,
                    status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
            
                
                
    
            
    
            
        
        
        
        try:
            
            user_id = common.authenticate(self.db,login, password, {})
        except:
            
            response = json.dumps({'data':[], 'message': 'كلمة المرور غير صحيحة  '})
            return Response(response,
        status=403,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    )
        
        
        if not user_id :
            response = json.dumps({'data':[], 'message': 'كلمة المرور غير صحيحة  '})
            return Response(response,
        status=403,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    )
        user_data = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['id' , '=' ,id]]], {'fields': ['login','name','father_name', 'email',"phone","country_code","country_id"]})

        # update user country
        if 'country_code' in fields:
            
            if 'phone' not in body:
                                
                del fields['country_code']
            else :
                
                country =models.execute_kw(self.db, uid, self.password, 'res.country', 'search_read', [[['phone_code' , '=' , fields['country_code']]]], {
                                        'fields': ['id']})
                
                fields['country_id']=country[0]['id']
                
        if 'login' in fields:
            # check_user_change_phone=models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['id' , '=' ,id]]], {'fields': ['name','father_name', 'email',"login"]})
            if user_data[0]['login']==fields['login']:
               
                del fields['login']
            else :
                fields['is_active']=False
            

        if 'email' in fields:
            if user_data[0]['email']==fields['email']:
                del fields['email']
            
            
        c=models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[id], fields])
        
        
        if 'login' in fields:
            write_date=datetime.now()
            # models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[id], {'is_active': False }])
            user_verfication=models.execute_kw(self.db, uid, self.password, 'user.verification', 'search_read',[['&',['type' , '=', '2'],['user_id' , '=' , id]]], {'fields': ['user_id', "code", "is_valid" ]})
            if user_verfication==[]:
                
                
                
                user_verfication=models.execute_kw(self.db, uid, self.password, 'user.verification', 'create',[{'user_id':id,'type':'2'}])
            else :    
                models.execute_kw(self.db, uid, self.password, 'user.verification', 'write', [[user_verfication[0]['id']], {'user_id':id,'write_date':write_date}])
        
    
        if 'email' in fields:
            write_Date=datetime.now()
            email_verfecation=user_verfication=models.execute_kw(self.db, uid, self.password, 'user.verification', 'search_read',[['&',['type' , '=', '3'],['user_id' , '=' , id]]], {'fields': ['user_id', "code", "is_valid" ]})
            if email_verfecation==[]:
                models.execute_kw(self.db, uid, self.password, 'user.verification', 'create',[{'user_id':id,'type':'3'}])
            else :
                models.execute_kw(self.db, uid, self.password, 'user.verification', 'write', [[email_verfecation[0]['id']], {'user_id':id,'write_date':write_Date}])
        user_data = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['id' , '=' ,id]]], {'fields': ['name','father_name', 'email',"login"]})
        user_data = false2empty(self ,user_data)
        response = json.dumps({'data': user_data,'message':'تم تغيير معلوماتك'})
        return Response(
        response, status=200,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    )   
    @http.route('/get_my_profile',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_my_profile(self, **kw):

        
        authe = request.httprequest.headers
        token = authe['Authorization'].replace('Bearer ', '')
        try:
           dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
           
        except Exception as e:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        
        id = dec_token['id']
        login=dec_token['login']
        
        fields={}
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        
        
        
        if verfiy_token.verfiy_token(self,token,str(id)) ==False:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
            
        else :
            
            user = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',[[['id', '=', id]]], {'fields':  ['user_type','student_id','name','login','calling_code','email','image_path','father_name',"is_active",'state_id','location_id','points','image_path','country_id']})
            user_country = ""
            if user[0]["country_id"]:
                user_country = request.env['res.country'].search([('id','=',user[0]["country_id"][0])])
            if user[0]['user_type']=="student":
                del user[0]['user_type']
            else :
                del user[0]['user_type']
                del user[0]['student_id']
            if len(user_country) != 0:
                user[0]['country_short_code'] = user_country.code
            else:
                user[0]['country_short_code'] = ''
            for i in user:
                if i['state_id']!=False:
                    if i['state_id'][0]:
                        state_id = i['state_id'][0]
                        state_name = i['state_id'][1]
                        user[0]['state_id'] = state_id
                        user[0]['state_name'] = state_name
                        sd = user[0]['state_name'].split("(")
                        user[0]['state_name'] = sd[0]
                if i['location_id']!=False:   
                    if i['location_id'][0]:
                        location_id = i['location_id'][0]
                        location_name = i['location_id'][1]
                        user[0]['location_id'] = location_id
                        user[0]['location_name'] = location_name
            user = false2empty(self ,user)
            response = json.dumps({'data': user[0],'message':'معلومات الحساب'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

    @http.route('/change_phone_number',  auth="public",csrf=False, website=True, methods=['POST'])
    def change_phone_number(self, **kw):

        authe = request.httprequest.headers
        token = authe['Authorization'].replace('Bearer ', '')
        try:
           dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
           
        except Exception as e:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!','errrror':e})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
    
        id = int(dec_token['id'])
        login=dec_token['login']
        username =dec_token['username']
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))        
        body =json.loads(request.httprequest.data)
        phone = body['phone']
        country_code = body['country_code']
        password = body['password']
        if verfiy_token.verfiy_token (self,token,str(id)) ==False:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        syria_number = '0'+phone
        phone = country_code + phone
        user = common.authenticate(self.db,login, password, {})
        country_code=country_code.replace("0","")
        country_rec = http.request.env['res.country'].search([('phone_code' , '=' ,country_code )] , limit = 1)
        if country_rec :
            country_id = country_rec.id
        else :
            country_id  = False
        if user != False: 
            try :
                models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[id], {'is_active': False , 'login' : phone , 'country_id' :country_id }])

            except:
            
                response = json.dumps({'data':[], 'message': 'الرقم موجود سابقا'})
                return Response(response,
            status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    )
        
            date_now = str(datetime.today())
            payload = {
                    'id': id,
                    'username': username,
                    'login' :login ,
                    
                    'timestamp' : date_now,
                    }
            SECRET='ali.ammar'
            enc = jwt.encode(payload, SECRET)
            is_ther_token =models.execute_kw(self.db, uid, self.password, 'user.token', 'search_count', [[['user_id' , '=', user]]])
            user_token =models.execute_kw(self.db, uid, self.password, 'user.token', 'search_read', [[['user_id' , '=', user]]])
            
            if is_ther_token:
                    models.execute_kw(self.db, uid, self.password, 'user.token', 'write', [[ user_token[0]['id']], {'token': enc}])
                    verification_data = models.execute_kw(self.db, uid, self.password, 'user.verification', 'search_read', [['&',['type' , '=', '2'],['user_id' , '=' , id]]], {'fields': ['user_id', "code", "is_valid" ,"type"]})
                    
                    if len(verification_data) >0 :
                        verification_data_id = verification_data[0]['id']
                        models.execute_kw(self.db, uid, self.password, 'user.verification', 'write', [[verification_data_id], {'write_date': date_now}])
                        # if country_code == '00963':
                        #     payload = {

                        #             "phone":syria_number,
                                    
                        #             "code":verification_data[0]['code']   
                        #     }

                        #     url = 'https://cashservices.perla-tech.com/api/taleb/sendsms'
                        #     headers = {
                        #         "accept": "application/json"
                        #     }       
                        #     req = requests.post(url, headers=headers,data=payload)
                        message = "رمز التفعيل الخاص بمنصّة طالب التعليمية هو: "
                        sms_response = self._send_sms(message, phone[2:],verification_data[0]['code'], country_code )
                        print("======================== sms response", sms_response)
                        response=json.dumps({"data": [],"message":"تم تغيير الرقم و ارسال كود تحقق"})
                        return Response( response,
                        headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                        )
                    else:
                        models.execute_kw(self.db, uid, self.password, 'user.verification', 'create', [{'user_id': id,'type' : '2', 'is_valid': True }])
                        response=json.dumps({"data": [],"message":"تم تغيير الرقم و ارسال كود تحقق"})
                        return Response( response,
                        headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                        )
            else:
                response=json.dumps({"data": [],"message":"لم يتم التحقق من الحساب"})
                return Response( response,status=403,
                headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )
        
        else:
                response=json.dumps({"data": [],"message":"كلمة السر او رقم الهاتف خاطئ"})
                return Response( response,status=403,
                headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )
    
    
 
        
    @http.route('/change_email',  auth="public",csrf=False, website=True, methods=['POST'])
    def change_email(self, **kw):

        authe = request.httprequest.headers
        token = authe['Authorization'].replace('Bearer ', '')
        try:
           dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
           
           
        except Exception as e:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!','errrror':e})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        id = dec_token['id']
        login=dec_token['login']
        # username =dec_token['username']
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))        
        body =json.loads(request.httprequest.data)
        email = body['email']
        
        password = body['password']
        user= common.authenticate(self.db,login, password, {})
        if verfiy_token.verfiy_token (self,token,str(id)) ==False:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        
        
        if user != False: 
            if validation_email(self,email) == True:
                models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[id], {'is_active':True , 'email' : email ,"email_is_active" : False}])
                verification_data = models.execute_kw(self.db, uid, self.password, 'user.verification', 'search_read', [['&',['type' , '=', '3'],['user_id' , '=' , id]]], {'fields': ['user_id', "code", "is_valid" ]})
                
                
                
                if verification_data != [] :
                    create_user_verification = models.execute_kw(self.db, uid, self.password, 'user.verification', 'write', [[verification_data[0]['id']],{'user_id': id, 'type' : '3','is_valid' : True}])
                else:
                    create_user_verification = models.execute_kw(self.db, uid, self.password, 'user.verification', 'create', [{'user_id': id, 'type' : '3','is_valid' : True}])
                response=json.dumps({"data": [],"message":"تم تغير البريد الاكتروني "})
                return Response( response,
                headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )
            else:
                response=json.dumps({"data": [],"message":"example@gmail.com تم ادخال بريد الكتروني خاطئ يرجى ادخال حساب اخر على الشكل التالي "})
                return Response( response,
                headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )

        else:
                response=json.dumps({"data": [],"message":"لم يتم التحقق من الحساب"})
                return Response( response,status=401,
                headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )

    @http.route('/post_quiz',  auth="public",csrf=False, website=True, methods=['POST'])
    def post_quiz(self, **kw):
        
        resault=0.0
        x=0.0
        correct_stu_ans=[]
        false_answers = []
        authe = request.httprequest.headers
        
        token = authe['Authorization'].replace('Bearer ', '')
        try:
           dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
           
           
        except Exception as e:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        id = dec_token['id']
        login=dec_token['login']
        body =json.loads(request.httprequest.data)
        session_id = int(body['session_id'])
        answers = body['answers']
        if verfiy_token.verfiy_token (self,token,str(id)) ==False:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))       
        session_data = models.execute_kw(self.db, uid, self.password, 'course.video', 'search_read', [[['id' , '=' , session_id]]], {'fields': ['quiz_ids',"course_id"]})
        count = len(session_data[0]['quiz_ids'])
        course_id = session_data[0]['course_id'][0]
        
        
        question_point = 10/count 

        
        for i in answers:
            
            answers_id = i['id']
            correct_answers = str(i['correct_answer'])
            quiz_data = models.execute_kw(self.db, uid, self.password, 'video.quiz', 'search_read', [[['id' , '=' , answers_id]]], {'fields': ['correct_answers']})
            if correct_answers == quiz_data[0]['correct_answers']:
                resault+= question_point
                correct_stu_ans.append({'question_id':quiz_data[0]['id'], 'student_answer':correct_answers })
            else : 
                false_answers.append({'question_id':quiz_data[0]['id'],'correct_answer': quiz_data[0]['correct_answers'] , 'student_answer':correct_answers })
        resault=math.ceil(resault)
        quiz_result_search = models.execute_kw(self.db, uid, self.password, 'resault', 'search_read', [['&',['course_id' , '=' ,course_id],['user_id' , '=', id],['session_id' , '=' ,session_id]]] ,  {'fields': ['resault','try_counter']})

        
        if quiz_result_search != []:
            maxresult = max(quiz_result_search, key=lambda x:x['resault'])

            try_counter = quiz_result_search[0]['try_counter']
            
            
            if try_counter ==0 :
                models.execute_kw(self.db, uid, self.password, 'resault', 'write', [[maxresult['id']], {'false_answers':false_answers , 'correct_stu_ans' : correct_stu_ans}])
                response = json.dumps({ 'data':{'result':resault},'message': 'تم رفع الاختبار'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            
            
            else :
                try_counter = try_counter-1
   
            if resault > maxresult['resault']:
                max_resault  = resault
                models.execute_kw(self.db, uid, self.password, 'resault', 'write', [[maxresult['id']], {'user_id': id,'resault':resault,'session_id' :session_id ,'try_counter':try_counter,"course_id" :course_id, 'false_answers':false_answers,'correct_stu_ans':correct_stu_ans}])
            else :
                max_resault = maxresult['resault']
                models.execute_kw(self.db, uid, self.password, 'resault', 'write', [[maxresult['id']], {'try_counter':try_counter,'false_answers':false_answers,'correct_stu_ans':correct_stu_ans}])
        
        else :
            try_counter_conf = request.env['quiz.conf'].sudo().search([('id' , '!=' , False)] , limit=1)
            resault_create = models.execute_kw(self.db, uid, self.password, 'resault', 'create', [{'user_id': id,'resault':resault,'session_id' :session_id ,"course_id" :course_id, 'try_counter':try_counter_conf.number,'false_answers':false_answers ,'correct_stu_ans':correct_stu_ans}])
            max_resault = resault
        resault_count = models.execute_kw(self.db, uid, self.password, 'resault', 'search_count', [['&',['course_id' , '=' ,course_id],['user_id' , '=', id]]])  
        resault_data = models.execute_kw(self.db, uid, self.password, 'resault', 'search_read', [['&',['course_id' , '=' ,course_id],['user_id' , '=', id]]] ,  {'fields': ['resault']})
        for i in  resault_data :
            x += i['resault']
        final_resault = x /resault_count
        
        final_resault =math.ceil(final_resault)
        user_grade_data = models.execute_kw(self.db, uid, self.password, 'course.result', 'search_read', [['&',['course_id' , '=' ,course_id],['course_result_id' , '=', id]]])
        if user_grade_data == []:
            models.execute_kw(self.db, uid, self.password, 'course.result', 'create', [{'course_result_id': id,'result':final_resault,"course_id" :course_id}])
        
        else :
             models.execute_kw(self.db, uid, self.password, 'course.result', 'write', [[user_grade_data[0]['id']], {'course_result_id': id,'result':final_resault,"course_id" :course_id}])
        response = json.dumps({ 'data':{'result':resault,'max_result' : max_resault},'message': 'تم رفع الاختبار'})
        return Response(
        response, status=200,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    )





    @http.route('/send_notification_vector',  auth="public",csrf=False, website=True, methods=['POST'])
    def send_notification_vector(self, **kw):
        body =json.loads(request.httprequest.data)

        token =body['token']
        notification_type =body['notification_type']
        serverToken = 'AAAA_L5lIgQ:APA91bFTVdRtgkLdumXwdHHf8P4EHUxvx4Ju4uGHnWaSO4EffJgAX0ni9muO_kjtbnGagJXzWhcdTkKGhzY8TP4jqhAAezK8D25-D1Rz67XY8gQfSfbpLz5x0sjVMKwOreBin22Q1Hcs'
   
        payload = {
        "comment_id":'sdasd',
        "session_id":'session_id' ,
        "course_id":'course_id',
        "reply_id":'reply_id',
        'title' :'title',

        "comment":'comment',
        "notification_type":"Comment"
    }
        headers = {
                'Content-Type': 'application/json',
                'Authorization': 'key=' + serverToken,
            }
        body = {
                'notification': {'title': 'asdqwe123',
                                    'body': 'asdqwe123'
                                    },
                'to':
                    token,
                'priority': 'high',
                'data':payload,
                }
        response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
        
        
        