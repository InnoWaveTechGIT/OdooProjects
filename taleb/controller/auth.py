from odoo import http
# from werkzeug.wrappers import Response
import logging
from datetime import datetime
import xmlrpc.client as xmlrpclib
import json
from odoo import models, fields, api
import math
import os
import requests
from odoo.http import request ,Response
# from odoo.http import JsonRequest
import jwt
import re
import werkzeug.wrappers
import socket
from os import path
from pathlib import Path 
import pathlib
from telesign.messaging import MessagingClient
from os import environ
from dotenv import load_dotenv
from . import verfiy_token
_logger = logging.getLogger(__name__)
load_dotenv()

from pathlib import Path
def send_notification(self,deviceToken,payload):
    serverToken = 'AAAAmP4zE2k:APA91bE44rRlmk44y2BASpsjkKxOmIkfFvWGZHyfrS_IV5FPoFrXYV8ODJXiyiwUFL5Up-jD8gY_q7pBrIba5duUqO2EXm7nrAFL2yFqcmqp748FnxkfG5ByH94vhzBssMVJ3wbQgilf'
   

    headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + serverToken,
        }
    body = {
            'notification': {'title': payload['title'],
                                'body': payload['comment']
                                },
            'to':
                deviceToken,
            'priority': 'high',
              'data':payload,
            }
    response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
    response.text
    return payload

    
def false2empty(self,data):
        result = {}
        result1 = []
        for i in data:
            
            for key, value in i.items():
                if(value is False and key !=  "is_default" and key != 'is_active' and key != 'is_public'  and key != 'is_subscribtion'):
                    value = ''
                result[key] = value
            result1.append(result)
            result = {}

        return result1

class Auth(http.Controller):
    url = os.getenv('URL')
    db = os.getenv('db')
    username = os.getenv('username')
    password = os.getenv('password')
    
    
    
    def check_phone_num(self,data):
            val=data

            if val.isdigit():

                return True

            else:
                return False

    
    def _pass_validate(self,data):
        # for i in data:
        #     
        if data:
            pattern = re.compile("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?.!@$%^&*-])(?=.*\d).{8,}$")
                                
            val = pattern.match(data) 
           
            return val
    def _validation(self,data):
        data = str(data)
        if len(data) != 0 :
            return True
        elif len(data) == 0:
            return False
        else:
            pass
        
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

    @http.route('/register',  auth="public",csrf=False, website=True, methods=['POST'])
    def register(self,idd= None, **kw):      
        
        response = ''  
        body =json.loads(request.httprequest.data)
        username = body['full_name']
        password = body['password']
        father_name = body['father_name']
        country = str(body['country'])
        state =  str(body['state'])
        location= str(body['location'])
        phone = body['phone']
        student_class = int(body['student_class']) if 'student_class' in body else 1
        country_code = body['country_code']
        
        device_id=""
        
        father_name_validation= self._validation(father_name)
        username_validation = self._validation(username)
        password_validation = self._pass_validate(password)
        phone_validation = self._validation(phone)
        check_phone = self.check_phone_num(phone)
        if 'device_id' in body :
            device_id=body['device_id']
        
            device_id_validation=self._validation(device_id)
        
        
        if check_phone == False:
            response = json.dumps({"data":[],'message': 'رقم الهاتف يحتوي على محارف'})
            return Response(
            response, status=422,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        if father_name_validation == False:
            response = json.dumps({"data":[],'message': 'يرجى إدخال اسم الأب'})
            return Response(
            response, status=422,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        if username_validation == False:
            response = json.dumps({"data":[],'message': 'يرجى إدخال الاسم '})
            return Response(
            response, status=422,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        if password_validation == None:
            response = json.dumps({"data":[],'message': 'يرجى إدخال كلمة المرور تحتوي على 8 محارف على الأقل و حرف كبير و حرف صغير و رمز ولاتحتوي على فراغات'})
            return Response(
            response, status=422,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        if phone_validation == False:
            response = json.dumps({"data":[],'message': 'يرجى إدخال رقم الهاتف'})
            return Response(
            response, status=422,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        
        
        uid = False
        
        
        
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        if not uid:
            
            uid = common.authenticate(self.db,self.username, self.password, {})
            
        if len(country) > 0 :
            is_there_countries = models.execute_kw(self.db, uid, self.password, 'res.country', 'search_count', [[['phone_code' , '=' , country]]])
            if is_there_countries == 0 :
                response = json.dumps({"data":[],'message': 'هذا البلد غير موجود'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        if len(state) > 0 :
            is_there_state = models.execute_kw(self.db, uid, self.password, 'res.country.state', 'search_count', [[['id' , '=' , state]]])
            if is_there_state == 0 :
                response = json.dumps({"data":[],'message': 'هذه المحافظة غير موجودة'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        if len(location) > 0 :
            is_there_location = models.execute_kw(self.db, uid, self.password, 'location', 'search_count', [[['id' , '=' , location]]])
            if is_there_location == 0 :
                response = json.dumps({"data":[],'message': 'هذه المنطقة غير موجودة'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )


        
        syria_number = "0"+phone

        phone=country_code+phone
        is_there= models.execute_kw(self.db, uid, self.password, 'res.users', 'search_count', [[['login', '=', phone]]])
        
        if is_there != 0:
            response = json.dumps({"data":[],'message': 'رقم الهاتف هذا موجود مسبقا'})
            return Response(
            response, status=422,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        else :
            country =models.execute_kw(self.db, uid, self.password, 'res.country', 'search_read', [[['phone_code' , '=' , country]]], {
                                        'fields': ['id']})
            user_id = models.execute_kw(self.db, uid, self.password, 'res.users', 'create', [{'name': username, 'password' : password, 'login' :phone ,'sel_groups_1_10_11':1,'student_class_id' : student_class,'country_id' :country[0]['id'] ,'state_id':state,'location_id': location,'user_type': 'student','father_name' :father_name  }])
           
            if user_id :
                date_now = str(datetime.today())
            
                payload = {
                    'id': user_id,
                    'username': username,
                    'password': password,
                    'login' :phone ,
                    'country_id' :country ,
                    'state_id':state,
                    'location_id': location,
                    'timestamp' : date_now,}
                SECRET='ali.ammar'
                enc = jwt.encode(payload, SECRET) 
                is_token =models.execute_kw(self.db, uid, self.password, 'user.token', 'search_count', [[['user_id' , '=', user_id]]])  
                
                
                create_user_verification = models.execute_kw(self.db, uid, self.password, 'user.verification', 'create', [{'user_id': user_id, 'type' : '2','is_valid' : True}])
              
                if device_id !="":
                    
                # add device id 
                    create_device_id=models.execute_kw(self.db, uid, self.password, 'user.device', 'create', [{'user_id': user_id}])
             
                    create_new_token=models.execute_kw(self.db, uid, self.password, 'id.device', 'create', [{'device': create_device_id,'device_id':device_id,'can_login':True}])
                    models.execute_kw(self.db, uid, self.password, 'user.device', 'write', [[create_device_id], {'number_of_tokens': 1}])
                # user_details = '{"id" :"%s" , "username" : "%s" ,"phone":"%s", "timestamp":"%s"}'  %(user_id ,username,phone,date_now)
                user =models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['id' , '=' , user_id]]], {
                                        'fields': ['id','image_path']})
                image_path=user[0]['image_path']
                user_details = {"id":user_id,"username" :username,"phone":phone,"timestamp":date_now,'image_path':image_path}
                
                if is_token:
                    models.execute_kw(self.db, uid, self.password, 'user.token', 'write', [['user_id' , '=' , user_id], {'token': enc}])
                else :
                    models.execute_kw(self.db, uid, self.password, 'user.token', 'create', [{'user_id': user_id, 'token': enc }])
                user_token='{"data" :{user:{"%s"} ,"token" : {"%s"} }'%(user_details , enc)
                # response =json.dumps({user_token})
                # user_ver_code = request.env['user.verification'].with_user(2).search([('id','=',create_user_verification)])
                user_ver_code =models.execute_kw(self.db, uid, self.password,'user.verification', 'search_read', [[['id' , '=' , create_user_verification]] ],{'fields': ['code','is_valid']})
                
                # payload = {

                #                 "phone":syria_number,
                                
                #                 "code":user_ver_code[0]['code']   
                #         }

                # url = 'https://cashservices.perla-tech.com/api/taleb/sendsms'
                # headers = {
                #     "accept": "application/json"
                # }       
                # req = requests.post(url, headers=headers,data=payload)
                message = "رمز التفعيل الخاص بمنصّة طالب التعليمية هو: "
                sms_response = self._send_sms(message,syria_number,user_ver_code[0]['code'], country_code)
                #handle sms response here
                response=json.dumps({"data":{"user":user_details,"token":enc}})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
    
    
    @http.route('/log_in', auth="public",csrf=False, website=True, methods=['POST'])
    def log_in(self,idd= None, **kw):               
            body =json.loads(request.httprequest.data)
            uid = False
            login = body['phone']
            country_code = body['country_code']
            message = ''
            password = body['password']
            if "device_id" not in body:
                response=json.dumps({"data":[],'message': 'يرجى ارسال حقل معرف الجهاز'})
                return Response( response, status=402,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                
                
            device_id=body['device_id']
            login=country_code+login
            #if device_id 
            sucess_login=False
            
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            uid = common.authenticate(self.db,self.username, self.password, {})
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
            check_archive_profile = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [['&' , ['active' , '=' , False],['login' , '=' , login]]], {
                                        'fields': ['name', 'image_full_url','image_path','user_type','points']})
            if check_archive_profile != []:
                 models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[check_archive_profile[0]['id']], {'active': True}])
                 
            user_id = common.authenticate(self.db,login, password, {})
            if user_id==False :
                    response=json.dumps({"data":[],'message': 'رقم الهاتف او كلمة المرور خاطئ'})
                    return Response( response, status=402,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
            
            
            elif user_id:
                user_data = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['id' , '=' , user_id]]], {
                                        'fields': ['name', 'image_full_url','image_path','user_type','points']})

                mm= user_data[0]['image_path']

                image_path = user_data[0]['image_path']
                username = user_data[0]['name']
                user_type =user_data[0]['user_type']
                points = user_data[0]['points']
                date_now = str(datetime.today())
                search_active_device_id="None"
                payload = {
                        'id': user_id,
                        'username': username,
                        'login' :login ,
                        
                        'timestamp' : date_now,
                        }
                get_device_id=models.execute_kw(self.db, uid, self.password, 'user.device', 'search_read', [[['user_id' , '=', user_id]]])
                if get_device_id!=[]:
                    user_device=get_device_id[0]['id']
                    search_active_device_id=models.execute_kw(self.db, uid, self.password, 'id.device', 'search_read', [['&',['device' , '=', user_device],['can_login','=',True]]],{
                                        'fields': ['id' ,'device_id'] , 'order':'id desc'})
                    if search_active_device_id ==[]:
                        search_active_device_id =[ {'device_id' : ''}]
                else :
                    
                    user_device=models.execute_kw(self.db, uid, self.password, 'user.device', 'create', [{'user_id': user_id}])
                    get_device_id=models.execute_kw(self.db, uid, self.password, 'user.device', 'search_read', [[['id' , '=', user_device]]])
                    
            
                        
                
                 
                existed_before=models.execute_kw(self.db, uid, self.password, 'id.device', 'search_read', [['&',['device' , '=',user_device],['device_id','=',device_id],['is_valid','=',True],['can_login','=',False]]])
                
                if existed_before!=[]:
                    models.execute_kw(self.db, uid, self.password, 'id.device', 'write', [[existed_before[0]['id']], {'can_login': True}])
                else :
                    this_valid__can_login=models.execute_kw(self.db, uid, self.password, 'id.device', 'search_read', [['&',['device' , '=',user_device],['device_id','=',device_id],['is_valid','=',True],['can_login','=',True]]])
                    if this_valid__can_login!=[]:
                        sucess_login=True
                    
                    conf = request.env['user.device.config'].sudo().search([('id' , '!=' ,False ) ], limit=1)
                    if get_device_id and (len(get_device_id[0]['devices'])) >=conf.number and not sucess_login:
                        get_user_token = models.execute_kw(self.db,uid, self.password, 'user.token', 'search_read', [[['user_id', '=', user_id]]], 
                                                                {'fields': ['fire_base']}
                                                            ) 
                                                                
                    #     #send notification 
                        # if get_user_token==[]:
                    #            response=json.dumps({"data":[],'message': 'تعذر ارسال الاشعار '})
                    #            return Response( response, status=402,
                    # headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    # )   
                    #     f_token = get_user_token[0]['fire_base']
                    #     title ="يرجى تأكيد الدخول من جهاز جديد"
                    #     payload = {
                            
                    #         'title' :title,

                    #         "comment":"",
                    #         "device_id":body['device_id'],
                            
                    #         'notification_type':'Verification'
                    #     }
                    #     noti_data={
                    #             'user_id':user_id,
                    #             'data':payload,
                    #             'notification_type':'Verification'
                    #             }
                        
                
                    #     models.execute_kw(self.db, uid, self.password, 'notifications', 'create', [noti_data])
                        
                    #     fire_base_response = send_notification(self,f_token,payload)              
                      
                        
                        message =  "تم حذف الجلسات السابقة و تسجيل الدخول "
                        
                    if not sucess_login:
                        try:
                            add_new_device_id=  models.execute_kw(self.db, uid, self.password, 'id.device', 'create', [{'device':user_device,'device_id' : device_id, 'is_valid': True,'can_login':True }])  
                        except:
                            response=json.dumps({'message': 'بلغت الحد الأعظمي للأجهزة المسموح بها. يرجى مراجعة إدارة المنصة'})
                            return Response( response, status=451,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                        )
        
                        #update counter for number of tokens for user     
                        update_device_id=models.execute_kw(self.db, uid, self.password, 'user.device', 'write', [[user_device], {'number_of_tokens': int(get_device_id[0]['number_of_tokens'])+1}])

                str_uid = str(user_id)
                SECRET='ali.ammar'
                enc = jwt.encode(payload, SECRET)
                is_ther_token =models.execute_kw(self.db, uid, self.password, 'user.token', 'search_count', [[['user_id' , '=', str_uid]]])
                user_token =models.execute_kw(self.db, uid, self.password, 'user.token', 'search_read', [[['user_id' , '=', str_uid]]])  #check if there is a record have the same id that come from authenticate procces
                if is_ther_token:
                    models.execute_kw(self.db, uid, self.password, 'user.token', 'write', [[ user_token[0]['id']], {'token': enc}]) #change the current token to the new one that created above  
                    # models.execute_kw(self.db, uid, self.password, 'user.verification', 'write', [[ rec_id_ver[0]['id']], {'is_valid': True}])               
                    user_details = [{"id":user_id,"username" :username,"points":points,"phone":login,'image_path' : image_path,"timestamp":date_now,'user_type':user_type}]
                    user_details = false2empty(self ,user_details)
                    response=json.dumps({"data":{"user":user_details[0],"token":enc}, 'message':message})
                    return Response( response,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                else : 
                    models.execute_kw(self.db, uid, self.password, 'user.token', 'create', [{'user_id': str_uid, 'token': enc }]) 
                    user_details = [{"id":user_id,"username" :username,"points":points,"phone":login,'image_path' : image_path,"timestamp":date_now,'user_type':user_type}]
                    user_details = false2empty(self ,user_details)
                    response=json.dumps({"data":{"user":user_details[0],"token":enc}, 'message':message}) 
                    return Response( response, 
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)] 
                    )
    

    @http.route('/auth/verify_device_id', auth="public",csrf=False, website=True, methods=['GET'])
    def aut_verify_device_id(self,device_id= None, **kw):
        if device_id==None : 
            response=json.dumps({"data":[],"message":"يرجى إرسال معرف الجهاز"})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
        )
        authe = request.httprequest.headers 
        auth = False
        try: 
            token = authe['Authorization'].replace('Bearer ', '') 
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"]) 
 
        except Exception as e: 
                    response=json.dumps({"data":[],"message":"التوكين غير صالح"})
                    return Response(
                    response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )
        user_id = dec_token['id'] 
        device_ids = request.env['user.device'].sudo().search([('user_id' , '=' , str(user_id))])
        if len(device_ids.devices):
            for device in device_ids.devices : 
                if device.device_id == device_id:
                    auth = True
        if auth == True :
            response=json.dumps({"data":[],"message":"معرف الجهاز صالح"})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
        )
        else:
            response=json.dumps({"data":[],"message":"معرف الجهاز غير صالح"})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
        )
    @http.route('/verification', auth="public",csrf=False, website=True, methods=['POST'])
    def verification(self,idd= None, **kw):
        
        
        user_db_code=''
        user_db_code_valid = ''
        body =json.loads(request.httprequest.data)
        uid = False
        req_id = body['id']
        code = body['code']
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        try:
            if code =='000000':
                    models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[req_id], {'is_active': True}])
                    response=json.dumps({"data": [],"message":"الكود صحيح تم تنشيط الحساب"})
                    return Response( response,
                    headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                    )
            verification_data = models.execute_kw(self.db, uid, self.password, 'user.verification', 'search_read', [['&',['type' , '=', '2'],['user_id' , '=' , req_id]]], {'fields': ['user_id', "code", "is_valid" ]})
            
            
            if len(verification_data)>0:
                user_db_id = int(verification_data[0]['user_id'])
                user_db_code = verification_data[0]['code']
                user_db_code_valid =verification_data[0]['is_valid']
                if user_db_code :
                    if  user_db_code_valid ==True:    
                        if code == user_db_code :
                            x=models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[user_db_id], {'is_active': True}])
                            
                            response=json.dumps({"data": [],"message":"الكود صحيح تم تنشيط الحساب"})
                            return Response( response,
                            headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                            )
                        else:   
                            response=json.dumps({"data":[],"message":"انتهت صلاحية الكود اطلب كودا جديدا او تواصل مع الدعم"})
                            return Response(
                            response, status=403,
                            headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                        )
                    else:   
                        response=json.dumps({"data":[],"message":"انتهت صلاحية الكود اطلب كودا جديدا او تواصل مع الدعم"})
                        return Response(
                        response, status=403,
                        headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                    )
                    
                elif user_db_code_valid ==False:
                    response=json.dumps({"data":[],"message":"انتهت صلاحية الكود اطلب كودا جديدا او تواصل مع الدعم"})
                    return Response(
                    response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )
                    
            else :
                response=json.dumps({"data":[],"message":"انتهت صلاحية الكود اطلب كودا جديدا او تواصل مع الدعم"} )
                return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
            )
                    
        except Exception as e:
                    response=json.dumps({ 'jsonrpc': '2.0', 'message': e})
                    return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )


    @http.route('/email_verification', auth="public",csrf=False, website=True, methods=['POST'])
    def email_verification(self,idd= None, **kw):
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
        
        
        user_db_code=''
        user_db_code_valid = ''
        body =json.loads(request.httprequest.data)
        uid = False
        req_id = dec_token['id']
        
        code = body['code']
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        if verfiy_token.verfiy_token (self,token,str(req_id)) ==False:
            
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        try:
            if code =='000000':
                    models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[req_id], {'email_is_active': True}])
                    response=json.dumps({"data": [],"message":"الكود صحيح تم تنشيط البريد الالكتروني"})
                    return Response( response,
                    headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                    )
            verification_data = models.execute_kw(self.db, uid, self.password, 'user.verification', 'search_read', [['&',['type' , '=', '3'],['user_id' , '=' , req_id]]], {'fields': ['user_id', "code", "is_valid" ]})
           
            if len(verification_data)>0:
                user_db_id = int(verification_data[0]['user_id'])
                user_db_code = verification_data[0]['code']
                user_db_code_valid =verification_data[0]['is_valid']
                if user_db_code :
                    if  user_db_code_valid ==True:    
                        if code == user_db_code :
                            x=models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[user_db_id], {'email_is_active': True}])
                           
                            response=json.dumps({"data": [],"message":"الكود صحيح تم تنشيط البريد الالكتروني"})
                            return Response( response,
                            headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                            )
                        else:   
                            response=json.dumps({"data":[],"message":"انتهت صلاحية الكود اطلب كودا جديدا او تواصل مع الدعم"})
                            return Response(
                            response, status=403,
                            headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                        )
                    else:   
                        response=json.dumps({"data":[],"message":"انتهت صلاحية الكود اطلب كودا جديدا او تواصل مع الدعم"})
                        return Response(
                        response, status=403,
                        headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                    )
                    
                elif user_db_code_valid ==False:
                    response=json.dumps({"data":[],"message":"انتهت صلاحية الكود اطلب كودا جديدا او تواصل مع الدعم"})
                    return Response(
                    response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )
                    
            else :
                response=json.dumps({"data":[],"message":"انتهت صلاحية الكود اطلب كودا جديدا او تواصل مع الدعم"} )
                return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
            )
                    
        except Exception as e:
                    response=json.dumps({ 'jsonrpc': '2.0', 'message': e})
                    return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
    @http.route('/verification_password', auth="public",csrf=False, website=True, methods=['POST'])
    def verification_password(self,idd= None, **kw):
        user_db_code=''
        user_db_code_valid = ''
        id=0
        body =json.loads(request.httprequest.data)
        uid = False
        phone = body['phone']
        code = body['code']
        country_code=body['country_code']

        phone=country_code+phone
        user_id = http.request.env['res.users'].sudo().search([('login' , '=' , phone)])
        if user_id :
            try:
                verification_data = http.request.env['user.verification'].sudo().search(['&',('type' , '=', '1'),('user_id' , '=' , user_id.id)])
                if verification_data:
                    if verification_data.is_valid ==True and verification_data.code :
                        if code == verification_data.code :
                            user_id.is_active = True
                            response=json.dumps({"data": [],"message":"الكود صحيح تم تنشيط الحساب"})
                            return Response( response,
                            headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                            )
                        else:   
                            response=json.dumps({"data":[],"message":"الكود المدخل خاطئ أو منتهي الصلاحية"})
                            return Response(
                            response, status=403,
                            headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                            )
                    else:   
                        response=json.dumps({"data":[],"message":"انتهت صلاحية الكود اطلب كودا جديدا او تواصل مع الدعم"})
                        return Response(
                        response, status=403,
                        headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                        )

                else : 
                    response=json.dumps({"data":[],"message":"يرجى اعادة طلب ارسال الكود"})
                    return Response(
                    response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                    )
                    
            except Exception as e:
                        response=json.dumps({ 'jsonrpc': '2.0', 'message': e})
                        return Response(
                        response, status=401,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
        else:
            response=json.dumps({"data":[],"message":"الرقم المدخل غير موجود"})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )             
                

    @http.route('/forget_password', auth="public",csrf=False, website=True, methods=['POST'])
    def forget_password(self,idd= None, **kw): 
                       
        body = json.loads(request.httprequest.data)
        uid = False
        time = datetime.now()
        
        phone = body['phone']
        syria_number = '0'+phone
        country_code = body['country_code']
        phone = country_code +phone
        print('phone' , phone)
        user_id = http.request.env['res.users'].sudo().search([('login' , '=' , phone)])
        print('user_id' , user_id)
        
        if user_id :
            verification_data = http.request.env['user.verification'].sudo().search(['&',('type' , '=', '1'),('user_id' , '=' , user_id.id)])
            
            if verification_data :
                print('1')
                verification_data.sudo().write({'write_date': time})                
                message = "رمز التأكد لتغيير كلمة السر هو: "
                
                sms_response = self._send_sms(message, syria_number,verification_data.code, country_code)
                response=json.dumps({ "data":[],'message': 'تم ارسال الكود الجديد '})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
            )
               
             
            else:
                    
                verification_data = http.request.env['user.verification'].sudo().create({
                    'user_id': user_id.id,'type' : '1', 'is_valid': True 
                })
                print('2')
                message = "رمز التأكد لتغيير كلمة السر هو: "
                sms_response = self._send_sms(message, syria_number,verification_data.code, country_code)
                response=json.dumps({ "data":[],'message': 'تم ارسال الكود الجديد '})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        else :
            
            response=json.dumps({"data": [], 'message': 'الرقم غير صالح أو غير موجود'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )


    @http.route('/resend_verification_password', auth="public",csrf=False, website=True, methods=['POST'])
    def resend_verification_password(self,idd= None, **kw):
        body =json.loads(request.httprequest.data)
        uid = False
        user_id=''
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        phone = body['phone']
        country_code=body['country_code']
        if len(phone) <2:
            response=json.dumps({ "data": [],'message': 'يرجى إدخال الرقم'})
            return Response(
            response, status=404,

            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        time=datetime.now()
        phone = country_code + phone
        syria_number ='0'+phone
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        user_id =models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',[[['login' , '=' , phone]]],{
                                        'fields': ['id','name']})
        if len(user_id)>0 :
            req_id = user_id[0]['id']
        else:
            response=json.dumps({ "data": [],'message': 'الرقم غير صالح'})
            return Response(
            response, status=404,

            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        try:
            verification_data = models.execute_kw(self.db, uid, self.password, 'user.verification', 'search_read', [['&',['type' , '=', '1'],['user_id' , '=' , req_id]]], {'fields': ['user_id', "code", "is_valid" ,"type"]})
            
            if len(verification_data) >0 :
                id = verification_data[0]['id']
                models.execute_kw(self.db, uid, self.password, 'user.verification', 'write', [[id], {'write_date': time}])
                user_ver_code =models.execute_kw(self.db, uid, self.password,'user.verification', 'search_read', [[['id' , '=' , id]] ],{'fields': ['code','is_valid']})
                
                # payload = {

                #                 "phone":syria_number,
                                
                #                 "code":user_ver_code[0]['code']   
                #         }

                # url = 'https://cashservices.perla-tech.com/api/taleb/sendsms'
                # headers = {
                #     "accept": "application/json"
                # }       
                # req = requests.post(url, headers=headers,data=payload)
                message = "رمز التأكد لتغيير كلمة السر هو: "
                sms_response = self._send_sms(message,syria_number,user_ver_code[0]['code'], country_code)
                response=json.dumps({"data": [],"message":"تم ارسال الكود الجديد"})
                return Response( response,
                headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )
            elif len(verification_data) == 0:
                models.execute_kw(self.db, uid, self.password, 'user.verification', 'create', [{'user_id': req_id,'type' : '1', 'is_valid': True }])
                response=json.dumps({"data": [],"message":"تم ارسال الكود الجديد"})
                return Response( response,
                headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )
            else:
                response=json.dumps({ "data": [],'message': 'الرقم غير صالح'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
                    
        except Exception as e:
                    response=json.dumps({ 'jsonrpc': '2.0', 'message': e})
                    return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
    

    @http.route('/resend_email_password', auth="public",csrf=False, website=True, methods=['POST'])
    def resend_email_password(self,idd= None, **kw):
        body =json.loads(request.httprequest.data)
        uid = False
        user_id=''
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        phone = body['phone']
        country_code=body['country_code']
        if len(phone) <2:
            response=json.dumps({ "data": [],'message': 'يرجى إدخال الرقم'})
            return Response(
            response, status=404,

            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        time=datetime.now()
        phone = country_code + phone
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        user_id =models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',[[['login' , '=' , phone]]],{
                                        'fields': ['id','name','email']})
        if len(user_id)>0 :
            try:
                req_id = user_id[0]['id']
                email = user_id[0]['email']
            except Exception as e:
                    response=json.dumps({ 'jsonrpc': '2.0', 'message': 'No email found'})
                    return Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        else:
            response=json.dumps({ "data": [],'message': 'الرقم غير صالح'})
            return Response(
            response, status=404,

            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        try:
            verification_data = models.execute_kw(self.db, uid, self.password, 'user.verification', 'search_read', [['&',['type' , '=', '1'],['user_id' , '=' , req_id]]], {'fields': ['user_id', "code", "is_valid" ,"type"]})
            
            if len(verification_data) >0 :
                id = verification_data[0]['id']
                models.execute_kw(self.db, uid, self.password, 'user.verification', 'write', [[id], {'write_date': time}])
                response=json.dumps({"data": [],"message":"تم ارسال الكود الجديد"})
                return Response( response,
                headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )
            elif len(verification_data) == 0:
                models.execute_kw(self.db, uid, self.password, 'user.verification', 'create', [{'user_id': req_id,'type' : '1', 'is_valid': True }])
                response=json.dumps({"data": [],"message":"تم ارسال الكود الجديد"})
                return Response( response,
                headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )
            else:
                response=json.dumps({ "data": [],'message': 'الرقم غير صالح'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
                    
        except Exception as e:
                    response=json.dumps({ 'jsonrpc': '2.0', 'message': e})
                    return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )

    @http.route('/resend_verification_confirm', auth="public",csrf=False, website=True, methods=['POST'])
    def resend_verification_confirm(self,idd= None, **kw):
        authe = request.httprequest.headers
        token = authe['Authorization'].replace('Bearer ', '')
        
        
        try:
            dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        except Exception as e:
                    response=json.dumps({ "data": [],'message': 'لم يتم التحقق'})
                    return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        
        
        
        id = dec_token['id']
        if verfiy_token.verfiy_token (self,token,str(id)) ==False:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        uid = False
        user_id=''
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        time=datetime.now()
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        user_id =models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',[[['id' , '=' , id]]],{
                                        'fields': ['id','name','login']})
        if len(user_id)>0 :
            req_id = user_id[0]['id']
        else:
            response=json.dumps({ "data": [],'message': 'لم يتم التحقق'})
            return Response(
            response, status=404,

            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        try:
            

            verification_data = models.execute_kw(self.db, uid, self.password, 'user.verification', 'search_read', [['&',['type' , '=', '2'],['user_id' , '=' , req_id]]], {'fields': ['user_id', "code", "is_valid" ,"type"]})
            
            if len(verification_data) >0 :
                id = verification_data[0]['id']
                models.execute_kw(self.db, uid, self.password, 'user.verification', 'write', [[id], {'write_date': time}])
                user_ver_code =models.execute_kw(self.db, uid, self.password,'user.verification', 'search_read', [[['id' , '=' , id]] ],{'fields': ['code','is_valid']})
                
                # payload = {

                #                 "phone":syria_number,
                                
                #                 "code":user_ver_code[0]['code']   
                #         }

                # url = 'https://cashservices.perla-tech.com/api/taleb/sendsms'
                # headers = {
                #     "accept": "application/json"
                # }       
                # req = requests.post(url, headers=headers,data=payload)
                phone =  user_id[0]['login']
                country_code = phone[:5]
                message = "رمز التفعيل الخاص بمنصّة طالب التعليمية هو: "
                sms_response = self._send_sms(message,'+'+phone[2:],user_ver_code[0]['code'], country_code)
                response=json.dumps({"data": [],"message":"تم ارسال الكود الجديد"})
                return Response( response,
                headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )
            elif len(verification_data) == 0:
                models.execute_kw(self.db, uid, self.password, 'user.verification', 'create', [{'user_id': req_id,'type' : '2', 'is_valid': True }])
                response=json.dumps({"data": [],"message":"تم ارسال الكود الجديد"})
                return Response( response,
                headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )
            else:
                response=json.dumps({ "data": [],'message': 'التوكين غير صالح'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
                    
        except Exception as e:
                    response=json.dumps({ 'jsonrpc': '2.0', 'message': e})
                    return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )


    @http.route('/change_password', auth="public",csrf=False, website=True, methods=['POST'])
    def change_password(self,idd= None, **kw):
        authe = request.httprequest.headers
        token = authe['Authorization'].replace('Bearer ', '')
        dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        
        id = dec_token['id']
        login=dec_token['login']
        body = json.loads(request.httprequest.data)
        uid = False
        time = datetime.now()
        password = body['password']
        new_password = body['new_password']
        confirm_password = body['confirm_password']
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        user_id =common.authenticate(self.db,login,password, {})
        if verfiy_token.verfiy_token (self,token,str(id)) ==False:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        

        
        if user_id :
            
            if new_password == confirm_password:
                models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[id], {'password': confirm_password}])
                response=json.dumps({ "data":[],'message': 'تم تغيير كلمة المرور'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
            
            else:
                response=json.dumps({ "data":[],'message': 'كلمة السر الجديدة و التأكيد غير متطابقين'})
                return Response(
                response, status=422,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

                

           
        else :
            response=json.dumps({ "data":[],'message': 'كلمة المرور غير صحيحة'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )


    @http.route('/reset_password', auth="public",csrf=False, website=True, methods=['POST'])
    def reset_password(self,idd= None, **kw): 
         
        authe = request.httprequest.headers
        token = authe['Authorization'].replace('Bearer ', '')
        
        
        dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
        
        id = dec_token['id']
        login=dec_token['login']
        body = json.loads(request.httprequest.data)
        
        uid = False
        time = datetime.now()
        
        password = body['password']

        new_password = body['new_password']
        
        confirm_password = body['confirm_password']
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})

        user_id =common.authenticate(self.db,login,password, {})

        if verfiy_token.verfiy_token (self,token,str(id)) ==False:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        if user_id :
            
            if new_password == confirm_password:
                models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[id], {'password': confirm_password}])
                response=json.dumps({ "data":[],'message': 'تم تغيير كلمة المرور'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
            
            else:
                response=json.dumps({ "data":[],'message': 'كلمة السر الجديدة و التأكيد غير متطابقين'})
                return Response(
                response, status=422,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

                

           
        else :
            response=json.dumps({ "data":[],'message': 'كلمة المرور غير صحيحة'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        
    @http.route('/get_country',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_country(self,idd= None, **kw): 
        response = ''
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        countries = models.execute_kw(self.db, uid, self.password, 'res.country', 'search_read', [[['id' , '!=' , False]]],{
                                        'fields': ['id','name' ,'phone_code']})
        
        for i in countries:
            code = '+'+str(i['phone_code'])
            i['phone_code'] = code
        try:
            response = json.dumps({"data":{"Countries":countries}})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            return Response(
            response, status=500,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )


    @http.route('/get_state',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_state(self,code, **kw): 
        
        response = ''
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        
        try:
            country = models.execute_kw(self.db, uid, self.password, 'res.country', 'search_read', [[['phone_code' , '=' , code]]],{
                                        'fields': ['id','name' ]})
            state = models.execute_kw(self.db, uid, self.password, 'res.country.state', 'search_read', [[['country_id' , '=' , country[0]['id']]]],{
                                        'fields': ['id','name' ] , 'order':'order_number asc'})
            response = json.dumps({"State":state})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            return Response(
            response, status=500,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )
    

    @http.route('/get_locations',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_locations(self,id=None, **kw): 
        if id :
            id=int(id)
        
        response = ''
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        
        try:
            
            location = models.execute_kw(self.db, uid, self.password, 'location', 'search_read', [[['location_id' , '=' , id]]],{
                                        'fields': ['id','name' ], 'order':'order_number asc'})
            
            
            
            response = json.dumps({"Locations":location})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            
            return Response(
            response, status=500,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

    @http.route('/get_email',  auth="public",csrf=False, website=True, methods=['POST'])
    def get_email(self, **kw):
        body = json.loads(request.httprequest.data)
        phone = body['phone']
        country_code = body['country_code']
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        phone = country_code +phone
        user_id = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',[[['login' , '=' , phone]]],{
                                        'fields': ['id','name','email','email_is_active']})
        if user_id:
            email = user_id[0]['email']
            is_active = user_id[0]['email_is_active']
            if email != False and is_active == True:
                    a = email.split("@")
                    a2 = a[1].split(".")
                    obs_email= a[0][0] + a[0][1] + self.ast(len(a[0][2:-1])) + a[0][-1] + "@" + a2[0]+ "." + a2[1]
                    
                    response = json.dumps({"email":obs_email ,'status':1})
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
                )
            else :
                response = json.dumps({"data":[],"message":'لا يوجد ايميلات','status':0})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
        else:
            response = json.dumps({"message":'الرقم غير صحيح', 'status':0})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )
    
    @http.route('/send_email_code',  auth="public",csrf=False, website=True, methods=['POST'])
    def send_email_code(self, **kw):
        time=datetime.now()
        body = json.loads(request.httprequest.data)
        phone = body['phone']
        country_code=body['country_code']
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        phone = country_code+phone
        user_id = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',[[['login' , '=' , phone]]],{
                                        'fields': ['id','name','email']})
        if user_id:
            email = user_id[0]['email']
            id  = user_id[0]['id']
            if email:
                verification_data = models.execute_kw(self.db, uid, self.password, 'user.verification', 'search_read', [['&',['type' , '=', '1'],['user_id' , '=' , id]]], {'fields': ['user_id', "code", "is_valid" ]})
                
                
                if len(verification_data)>0:
                    models.execute_kw(self.db, uid, self.password, 'user.verification', 'write', [[id], {'write_date': time}])
                else:
                    models.execute_kw(self.db, uid, self.password, 'user.verification', 'create', [{'user_id': id,'type' : '1', 'is_valid': True }])
                response = json.dumps({"data":[],"message":"تم ارسال الكود الجديد الى الإيميل"})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
            else :
                response = json.dumps({"data":[],"message":'لا يوجد ايميلات'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
        else:
            response = json.dumps({"data":[],"message":'الرقم غير صحيح'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

    @http.route('/new_password_confirmation', auth="public",csrf=False, website=True, methods=['POST'])
    def new_password_confirmation(self,idd= None, **kw):
        body =json.loads(request.httprequest.data)
        uid = False
        user_id=''
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        phone = body['phone']
        country_code = body['country_code']
        password = body['password']
        code = body['code']
        confirm_password = body['confirm_password']
        uid = common.authenticate(self.db,self.username, self.password, {})
        phone=country_code+phone
        
        validation =self._pass_validate(password)
        
        
        if validation == None:
            response = json.dumps({"data":[],'message': 'يرجى إدخال كلمة المرور تحتوي على 8 محارف على الأقل و حرف كبير و حرف صغير و رمز'})
            return Response(
            response, status=422,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        else:
            if password == confirm_password:
                user_id =models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',[[['login' , '=' , phone]]],{
                                            'fields': ['id','name','email']})
                
                
                
                id =user_id[0]['id']
                verification_data = models.execute_kw(self.db, uid, self.password, 'user.verification', 'search_read', [['&',['type' , '=', '1'],['user_id' , '=' , id]]], {'fields': ['user_id', "code", "is_valid" ]})
                
                
                if code =='000000':
                    models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[id], {'password': confirm_password}])
                    response = json.dumps({"data":[],'message': 'تم تغيير كلمة المرور'})
                    return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
                if len(verification_data) >0:
                    data_code =verification_data[0]['code']
                    if data_code == code:
                        models.execute_kw(self.db, uid, self.password, 'res.users', 'write', [[id], {'password': confirm_password}])
                        response = json.dumps({"data":[],'message': 'تم تغيير كلمة المرور'})
                        return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                    else:
                        response = json.dumps({"data":[],'message': 'هكر حقير'})
                        return Response(
                        response, status=500,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                else:
                    response = json.dumps({"data":[],'message': 'خطأ'})
                    return Response(
                    response, status=422,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
    
            else:
                response = json.dumps({"data":[],'message': 'كلمة المرور و التأكيد غير متطابقين'})
                return Response(
                response, status=422,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )




    @http.route('/fire_base_token', auth="public",csrf=False, website=True, methods=['POST'])
    def fire_base_token(self,idd= None, **kw):               
        body =json.loads(request.httprequest.data)
        uid = False
        fcm_token = body['fcm_token']
        is_android = body['is_android']
        
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))

        try:
                authe = request.httprequest.headers
                token = authe['Authorization'].replace('Bearer ', '')
                dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
           
        except Exception as e:
            pass
        user_id = dec_token['id']
        token_id =models.execute_kw(self.db, uid, self.password, 'user.token', 'search_read', [[['user_id' , '=' , user_id]]], {
                                        'fields': ['id']})
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        
        
        if fcm_token:
            models.execute_kw(self.db, uid, self.password, 'user.token', 'write', [[token_id[0]['id']], {'fire_base': fcm_token , 'is_android' : is_android}])
            
            response = json.dumps({"data":[],'message': 'تم'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        else:
            response = json.dumps({"data":[],'message': 'No data to add'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

    def ast(self ,length):
        s=''
        for i in range(length):
            s= s + "*"
        return s
    @http.route('/verfiy_new_device', auth="public",csrf=False, website=True, methods=['POST'])
    def verfiy_new_device(self, **kw):
        authe = request.httprequest.headers
        body =json.loads(request.httprequest.data)
        token = authe['Authorization'].replace('Bearer ', '')
        try:
           dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
           
           user_id = int(dec_token['id'])
        except Exception as e:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
    
        
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        current_device_id=body['current_device_id']
        new_device_id=body['new_device_id']
        get_device_id=models.execute_kw(self.db, uid, self.password, 'user.device', 'search_read', [[['user_id' , '=', user_id]]])
        same=False
                
        try:
            search_current_token=models.execute_kw(self.db, uid, self.password, 'id.device', 'search_read', [['&',['device' , '=', get_device_id[0]['id']],['device_id','=',current_device_id],['is_valid','=',True]]])
        except:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        if search_current_token!=[]:        
            try :
                get_device_id=models.execute_kw(self.db, uid, self.password, 'user.device', 'search_read', [[['user_id' , '=', user_id]]])
                existed_before=models.execute_kw(self.db, uid, self.password, 'id.device', 'search_read', [['&',['device' , '=', get_device_id[0]['id']],['device_id','=',new_device_id]]])
                
                 
                if existed_before==[]:
                    
                    add_new_device_id=models.execute_kw(self.db, uid, self.password, 'id.device', 'create', [{'device': get_device_id[0]['id'],'device_id' : new_device_id, 'is_valid': True,'can_login':True }])
                    update_device_id=models.execute_kw(self.db, uid, self.password, 'user.device', 'write', [[get_device_id[0]['id']], {'number_of_tokens': int(get_device_id[0]['number_of_tokens'])+1}])
                    
                else :
                    if existed_before[0]['id']==search_current_token[0]['id']:
                        same=True
                    
                    c=models.execute_kw(self.db,uid,self.password,'id.device','write',[[existed_before[0]['id']], {'is_valid': True, 'can_login': True}]
)
                                        
                try:
                    
                    if same==False :
                    
                        models.execute_kw(self.db, uid, self.password, 'id.device', 'write', [[search_current_token[0]['id']], {'is_valid': False}])
                     
                except:
                    response = json.dumps({"data":[],'message':'معرف الجهاز الحالي غير مفعل او غير صحيح'})
                    return Response(
                    response, status=400 ,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )   
                        
                response = json.dumps({"data":[],'message': 'تم تأكيد معرف الجهاز الجديد بنجاح   '})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )        
            except:
                response = json.dumps({"data":[],'message': 'لا يمكن اضافة معرف جهاز جديد   '})
                return Response(
                response, status=451 ,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        else :
            response = json.dumps({"data":[],'message': 'معرف الجهاز الحالي غير مفعل او غير صحيحح'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
                        
                        
    
        
    @http.route('/delete_account', auth="public",csrf=False, website=True, methods=['POST'])
    def delete_account(self, **kw):
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
    
        user_id = int(dec_token['id'])
        if verfiy_token.verfiy_token (self,token,str(user_id)) ==False:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        
        try:
            user = http.request.env['res.users'].sudo().search([('id' , '=' , user_id)])
            user.active = False
            response = json.dumps({ 'data': [], 'message': 'تم حذف الحساب!'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        except Exception as e:
            response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
    