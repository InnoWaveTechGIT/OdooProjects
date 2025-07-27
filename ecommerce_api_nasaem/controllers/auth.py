from odoo import http
# from werkzeug.wrappers import Response
import logging
from datetime import datetime
import xmlrpc.client as xmlrpclib
import json
from odoo import models, fields, api
import math
import os
import pip
import requests
from odoo.http import request ,Response
# from odoo.http import JsonRequest
import importlib
import pip

try:
    importlib.import_module('jwt')
except ImportError:
    # Library not found, download and install it
    pip.main(['install', 'jwt'])

try:
    importlib.import_module('pyjwt')
except ImportError:
    # Library not found, download and install it
    pip.main(['install', 'pyjwt'])
# pip.main(['install', 'jwt'])
import jwt
import re
import werkzeug.wrappers
import socket
from os import path
from pathlib import Path 
import pathlib
# from telesign.messaging import MessagingClient
# from os import environ
from .validation_marshmallow import RegisterSchema , LoginSchema,PasswordSchema
_logger = logging.getLogger(__name__)



    
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
    def _email_validation(self,data):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, data)):
            return True
        else:
            return False
        
    def _send_sms (self,message,phone_number,code):
         customer_id = os.getenv('CUSTOMER_ID', '23E479A9-FC5B-4FEC-A17F-D7182D09148B')
         api_key = os.getenv('API_KEY', 'AKpnGihB7+DGPNosTd0+F5rgSuKpsFWOD52ha9vw/SvF2lwK7uzP/6q3ZYHSTuEaBc2ZlTzXIzwpHQsUNj61uA==')
         phone = os.getenv('PHONE_NUMBER', phone_number)
         message = message + code
         messaging = MessagingClient(customer_id,api_key)
         response =  messaging.message(phone,message,"ARN")
         return response


    @http.route('/auth/register',  auth="public",csrf=False, website=True, methods=['POST'])
    def register(self,idd= None, **kw):      
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        response = ''  
        try:
            username = kw['full_name']
            password = kw['password']
            confirm_password = kw['confirm_password']
            email = kw['email']
            email = email.lower()
            phone = kw['phone']
            location = kw.get('location', '')
        except Exception as e:
                message = 'بعض الحقول الإجبارية غير مدخل' if language == 'ar_001' else 'Some requierd fields is not enterd'
                response = json.dumps({'message':message , 'is_success' :False})
                return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        try:
            data = RegisterSchema().load(kw)
        except Exception as e:

            response = json.dumps({'message':RegisterSchema().validate(kw)})
            return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])    

        username_validation = self._validation(username)
        # password_validation = self._pass_validate(password)     
        check_email=self._email_validation(email)
        if confirm_password != password:
            message = 'كلمة المرور و التأكيد غير متطابقين'if language == 'ar_001' else 'Make sure your passwor and confirm password are the same'
            response = json.dumps({"data":[],'message': message})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        if check_email == False:
            response = json.dumps({"data":[],'message': 'Incorrect email'})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        
        if username_validation == False:
            response = json.dumps({"data":[],'message': 'يرجى إدخال اسم المستخدم'})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        is_there = request.env['res.users'].sudo().search_count([('login' , '=' , email)])
        
        if is_there != 0:
            response = json.dumps({"data":[],'message': 'This email is already exist' , 'is_success' :False})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        else :
            portal_group = request.env.ref('base.group_portal')
            try:
                user_id=request.env['res.users'].with_user(2).with_company(5).create({
                    'name': username, 
                    'password' : password, 
                    'login' :email,
                    'phone' :phone ,
                    # 'company_id' :5,
                    'groups_id': [(6, 0, [portal_group.id])] ,
                })
                user_id.partner_id.email=email
            except:
                user_id=request.env['res.users'].with_user(2).create({
                    'name': username, 
                    'password' : password, 
                    'login' :email,
                    'phone' :phone ,
                    # 'company_id' :5,
                    'groups_id': [(6, 0, [portal_group.id])] ,
                })
           
            if user_id :
                # if location:
                #     if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                #             location = location
                #     else :
                #         location = 'US'
                # else :
                #     location = 'KW'
                # country = request.env['res.country'].with_user(2).with_company(5).search([('code', '=', location)])
                # if country:
                #     cur = country.currency_id.name
                # else:
                #     location = ''
                #     cur= ''
                # if cur:
                #     pricelist = request.env['product.pricelist'].with_user(2).search(
                #         [('currency_id.name', '=', cur),('company_id' , '=' , 5)],
                #         limit=1
                #     )
                # if location == 'KW':
                #     user_id.partner_id.property_product_pricelist = 270
                # else:
                #     user_id.partner_id.property_product_pricelist = pricelist.id
                date_now = str(datetime.today())
                payload = {
                        'id': user_id.id,
                        'username': username,
                        'login' :email ,
                        'location' : location,
                        'timestamp' : date_now,
                        }
                str_uid = str(user_id)
                SECRET='ali.ammar'
                enc = jwt.encode(payload, SECRET)
                user_token=request.env['user.token.nasaem'].sudo().create({
                'user_id': user_id.id, 
                'token' : enc
                }) 

                user_details = {"id":user_id.id,"username" :username,"email":email , 'phone' : phone }
                response=json.dumps({"data":{"user":user_details,"token":user_token.token} , 'is_success' :True})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
    
    
    @http.route('/auth/login', auth="public",csrf=False, website=True, methods=['POST'])
    def log_in(self,idd= None, **kw):  
            language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
            try:             
                uid = False
                login = kw['email']
                login = login.lower()
                message = ''
                location =kw.get('location', '')
                password = kw['password']
            except Exception as e:
                message = 'بعض الحقول الإجبارية غير مدخل'if language == 'ar_001' else 'Some requierd fields is not enterd'
                response = json.dumps({'message':message , 'is_success' :False})
                return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]) 
            try:
                data =LoginSchema().load(kw)
            except Exception as e:

                response = json.dumps({'message':LoginSchema().validate(kw) , 'is_success' :False})
                return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])   
            user_id = request.env['res.users'].sudo().search([('login' , '=' , login)])
            if len(user_id)==0 :
                    message = 'البريد الإلكتروني او كلمة المرور خاطئة'if language == 'ar_001' else 'Incorrect email or password'
                    response=json.dumps({"data":[],'message': message , 'is_success' : False})
                    return Response( response, status=402,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                    if checkPassword(password) == False:
                        response=json.dumps({"data":[],'message': 'Incorrect email or password'})
                        return Response( response, status=402,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                        )

            
            
            elif len(user_id) != 0:  
                if location:
                    if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                            location = location
                    else :
                        location = 'US'
                else :
                    location = 'KW'
                country = request.env['res.country'].sudo().search([('code', '=', location)])
                if country:
                    cur = country.currency_id.name
                else:
                    location = ''
                    cur= ''
                if cur:
                    pricelist = request.env['product.pricelist'].with_user(2).with_company(5).search(
                        [('currency_id.name', '=', cur)],
                        limit=1
                    )

                    user_id.partner_id.property_product_pricelist = pricelist.id
                db = http.request.env.cr.dbname
                try:
                    uid = request.session.authenticate(db, login, password)
                except Exception as e:
                    user_details = []
                    message = 'البريد الإلكتروني او كلمة المرور خاطئة'if language == 'ar_001' else 'Incorrect email or password'
                    response=json.dumps({"data":{"user":user_details,"token":'Null' }, 'message':message , 'is_success' :False} )
                    return Response( response,status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                date_now = datetime.today()
                is_ther_token = request.env['user.token.nasaem'].search([('user_id' , '=' , user_id.id)])
                if len(is_ther_token) != 0 :
                    date_now = str(datetime.today())
                    payload = {
                            'id': user_id.id,
                            'username': user_id.name,
                            'login' :login ,
                            'location' : location,
                            'timestamp' : date_now,
                            }
                    str_uid = str(user_id)
                    SECRET='ali.ammar'
                    enc = jwt.encode(payload, SECRET)
                    is_ther_token.write({
                        'token' : enc
                    })
                    message = 'تفاصيل الحساب'if language == 'ar_001' else 'profile details'
                    user_details = [{"id":user_id.id,"username" :user_id.name,"email":user_id.login, 'phone' : user_id.phone ,"timestamp":str(date_now)}]
                    response=json.dumps({"data":{"user":user_details[0],"token":is_ther_token.token}, 'message':message , 'is_success' :True})
                    return Response( response,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                else : 
                    date_now = str(datetime.today())
                    payload = {
                            'id': user_id.id,
                            'username': user_id.name,
                            'login' :login ,
                            'location' : location,
                            'timestamp' : date_now,
                            }
                    str_uid = str(user_id)
                    SECRET='ali.ammar'
                    enc = jwt.encode(payload, SECRET)
                    is_ther_token = request.env['user.token.nasaem'].sudo().create({
                        'user_id' : user_id.id,
                        'token' : enc
                    })
                    message = 'تفاصيل الحساب'if language == 'ar_001' else 'profile details'
                    user_details = [{"id":user_id.id,"username" :user_id.name,"email":user_id.login,"phone":user_id.phone,"timestamp":str(date_now)}]
                    response=json.dumps({"data":{"user":user_details[0],"token":is_ther_token.token}, 'message':message , 'is_success' :True}) 
                    return Response( response, 
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)] 
                    )
    

    @http.route('/auth/forget_password', auth="public",csrf=False, website=True, methods=['POST'])
    def forget_password(self,idd= None, **kw): 
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        email = kw['email']
        users = request.env['res.users'].sudo().search([
                                        '|',
                                        ('login', '=', email),
                                        ('email', '=', email)
                                    ])
        try:
            if users.email or users.login :
                users.partner_id.email = email
                users.action_reset_password()
                message = 'تم ارسال ايميل لتغيير كلمة المرور'if language == 'ar_001' else 'email had been sent to reset password'
                response=json.dumps({"data":'Done', 'message':message , 'is_success' :True})
                return Response( response,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            else:
                message = 'لم يتم ايجاد البريد الإلكتروني'if language == 'ar_001' else 'email not found'
                response = json.dumps({"data": [], 'message': message, 'code': 400 , 'is_success' :False})
                return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        except Exception as e:
            response = json.dumps({"data": [], 'message': str(e), 'code': 400 , 'is_success' :False})
            return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])

    

    @http.route('/auth/new_password', auth="public", csrf=False, website=True, methods=['POST'])
    def new_password(self, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        headers = request.httprequest.headers
        authe = request.httprequest.headers
        password = kw['password']
        new_password = kw['new_password']
        confirm_password = kw['confirm_password']
        if new_password !=  confirm_password :
            message = 'كلمة المرور و التأكيد غير متطابقين'if language == 'ar_001' else 'Password and confirm password not matched !'
            response = json.dumps({ 'data': [], 'message': message , 'is_success' :False})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            message = 'التوكين غير صالح'if language == 'ar_001' else 'Un valid token !'
            response = json.dumps({ 'data': [], 'message': message , 'is_success' :False})
            return Response(
            response, status=403,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])

        if valid_token:
            try:
                dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
                login = dec_token['login']
            except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!' , 'is_success' :False})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        try:
            db = http.request.env.cr.dbname
            try:
                uid = request.session.authenticate(db, login, password)
            except Exception as e:
                message = 'كلمة المرور غير صحيحة'if language == 'ar_001' else 'Password is incorrect!'
                response = json.dumps({ 'data': [], 'message': message , 'is_success' :False})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            user_obj = request.env['res.users'].sudo().search([('login', '=', login)])
            if uid:
                if user_obj:
                    try:
                        user_obj.sudo().write({'password': new_password})
                    except Exception as e:
                        response = json.dumps({"data": [], 'message': str(e), 'code': 400})
                        return Response(
                            response, status=400,
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
                    # user_obj.write({'new_password': password})
                    
                    
                    message = 'تمت العملية بنجاح 'if language == 'ar_001' else 'The operation was successful'
                    response = json.dumps({"data": [], 'message': message, 'code': 200 , 'is_success' :True})
                    return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                                ('Content-Length', 100)])

                else:
                    message = 'البيانات غير صحيحة 'if language == 'ar_001' else 'Unvalid data , password is not correct'
                    response = json.dumps({"data": [], 'message': message, 'code': 404, 'is_success' :False})
                    return Response(
                        response, status=404,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                                ('Content-Length', 100)])
            else:
                
                message = ''
                message = 'لم يتم ايجاد الحساب'if language == 'ar_001' else 'Account not found'
                response = json.dumps({"data": [], 'message': message, 'code': 404, 'is_success' :False})
                return Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                            ('Content-Length', 100)])
        except Exception as e:
            response = json.dumps({"data": [], 'message': str(e), 'code': 400 , 'is_success' :False})
            return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])


    @http.route('/auth/logout', auth="public", csrf=False, website=True, methods=['POST'])
    def log_out(self, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        try:
            headers = request.httprequest.headers
            try:
                token = headers['Authorization'].replace('Bearer ', '')
                valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
            except Exception as e:
                response = json.dumps({'data': 'no data', 'message': 'Unauthorized!' , 'is_success' :False})
                return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
            access_token = kw.get('access_token')
            user_token = request.env['user.token.nasaem'].sudo().search([('token', '=', token)])
            if user_token:
                user_token.unlink()
                message = 'تم تسجيل الخروج بنجاح'if language == 'ar_001' else 'User logged out successfully'
                response = json.dumps({'message': message, 'is_success': True})
                return Response(response,
                                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
            else:
                message = 'التوكين غير صالح'if language == 'ar_001' else 'Invalid Access Token'
                response = json.dumps({'message': message, 'is_success': False})
                return Response(response, status=401,
                                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        except Exception as e:
            message = 'حدث خطأ ما'if language == 'ar_001' else 'An error occurred while logging out'
            response = json.dumps({'message': message, 'is_success': False})
            return Response(response, status=500,
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])

    @http.route('/delete_account', auth="public", csrf=False, website=True, methods=['DELETE'])
    def delete_account(self, **kw):
        headers = request.httprequest.headers
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        try:
            token = headers['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!' , 'is_success' :False})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        email = kw.get('email')
        password = kw.get('password')
        db = http.request.env.cr.dbname
        try:
            uid = request.session.authenticate(db, email, password)
        except Exception as e:
            user_details = []
            message = 'كلمة المرور او البريد الإلكتروني خاطئ'if language == 'ar_001' else 'Incorrect email or password'
            response=json.dumps({'message':mesaage, 'is_success' :False} )
            return Response( response,status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        # Perform any necessary checks or validations before deleting the account
        user_id = int(valid_token[0]['user_id'])
        if uid == user_id:
        # Delete the account
            user = request.env['res.users'].sudo().search([('id', '=', uid)])
            user.sudo().write({
                'active' : False
            })
        else:
            message = 'البريد الالكتروني او كلمة المرور خاطئين'if language == 'ar_001' else 'email and password is not correct'
            response=json.dumps({'message':message , 'is_success' :False} )
            return Response( response,status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        # Perform any additional tasks or cleanup operations

        # Return a response
        message = 'تم حذف الحساب بنجاح 'if language == 'ar_001' else 'Account deleted successfully'
        response=json.dumps({'message':message, 'is_success' :True} )
        return Response( response,status=200,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

    @http.route('/edit_profile', auth="public", csrf=False, website=True, methods=['POST'])
    def edit_profile(self, **kw):
        try:
            token = None
            language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
            try:
                headers = request.httprequest.headers
                token = headers['Authorization'].replace('Bearer ', '')
                valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
            except Exception as e:
                response = json.dumps({'data': 'no data', 'message': str(e)})
                return http.Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )
            if valid_token:
                    try:
                        dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
                    except Exception as e:
                        response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!' , 'is_success' :False})
                        return Response(
                        response, status=401,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                        )
            user_id = int(dec_token['id'])
            user_id = request.env['res.users'].sudo().search([('id', '=', user_id)])
            user_partner_id = user_id.partner_id.id
            fields = {}
            body = json.loads(request.httprequest.data)
            if 'email' in body:
                    count = request.env['res.users'].sudo().search([('login', '=', body['email'])])
                    if len(count) == 1 and count.id == user_id.id  or len(count) == 0:
                        user_id.login= body['email']
                        request.env['res.partner'].sudo().search([('id', '=', user_partner_id)]).write({'email': body['email']})
                    if len(count) == 1 and count.id != user_id.id or len(count) >= 1 :

                        message = ' البريد الالكتروني موجود سابقا'if language == 'ar_001' else "The email is already exist"
                        response = json.dumps({'data': [], 'message': message , 'is_success' : False})
                        return http.Response(
                        response, status=401,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                    )
            if 'name' in body:
                fields['name'] = body['name']
            if 'phone' in body:
                fields['phone'] = body['phone']
            
            # Update user information
            request.env['res.users'].sudo().search([('id', '=', user_id.id)]).write(fields)

            

            if 'company' in body:
                request.env['res.partner'].sudo().search([('id', '=', user_partner_id)]).write({'company_name': body['company']})

            if 'country_id' in body:
                request.env['res.partner'].sudo().search([('id', '=', user_partner_id)]).write({'country_id': body['country_id']})

            if 'address' in body:
                request.env['res.partner'].sudo().search([('id', '=', user_partner_id)]).write({'street': body['address']})
            if 'vat' in body:
                request.env['res.partner'].sudo().search([('id', '=', user_partner_id)]).write({'vat': body['vat']})
            if 'city' in body:
                request.env['res.partner'].sudo().search([('id', '=', user_partner_id)]).write({'city': body['city']})
            if 'zip' in body:
                request.env['res.partner'].sudo().search([('id', '=', user_partner_id)]).write({'zip': body['zip']})
            if 'state_id' in body:
                request.env['res.partner'].sudo().search([('id', '=', user_partner_id)]).write({'state_id': body['state_id']})
            
            message = 'تم تحديث معلومات الملف الشخصي'if language == 'ar_001' else 'Profile updated successfully'
            response = json.dumps({'data': [], 'message': message , 'is_success' : True})
            return http.Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        
        except Exception as e:
                response = json.dumps({'data': 'no data', 'message': str(e)})
                return http.Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )



    @http.route('/profile', auth="public", csrf=False, website=True, methods=['GET'])
    def profile(self, **kw):
        token = None
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        try:
            headers = request.httprequest.headers
            token = headers['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': str(e)})
            return http.Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        try:
            if valid_token:
                try:
                    dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
                except Exception as e:
                    response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!' , 'is_success' :False})
                    return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
            user_id = int(dec_token['id'])
            user_id = request.env['res.users'].sudo().search([('id', '=', user_id)])
            user_partner_id = user_id.partner_id.id
            user_data = {
                'name': user_id.name,
                'email': user_id.login,
                'phone': user_id.phone,
                'company': user_id.partner_id.company_name,
                'country_id': user_id.partner_id.country_id.id,
                'address': user_id.partner_id.street,
                'vat' : user_id.partner_id.vat,
                'city' :user_id.partner_id.city,
                'zip' : user_id.partner_id.zip,
                'state_id' : user_id.partner_id.state_id.id,
            }

            message = 'مغلومات الحساب'if language == 'ar_001' else 'User data retrieved successfully'
            response = json.dumps({'data': user_data, 'message': message , 'is_success' : True})
            return http.Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': str(e) , 'is_success' : False})
            return http.Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    @http.route('/user/countries',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_country(self,idd= None, **kw): 
        result = []
        
        countries = request.env['res.country'].search([])
        
        for i in countries:
            
            result.append({
                        'id':i.id,
                        'country_name':i.name,                  
                        'phone_code':'+'+str(i.phone_code)
                    
                })
        
        try:
            response = json.dumps({"data":{"Countries":result} , 'message' :' All Countries', 'is_success' :True})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            return Response(
            status=500,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

    @http.route('/user/state',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_country_state(self,country_id= None, **kw): 
        result = []
        country_id = int(country_id)
        countries = request.env['res.country.state'].search([('country_id' , '=' , country_id)])
        
        for i in countries:
            
            result.append({
                        'id':i.id,
                        'state_name':i.name,                                      
                })
        
        try:
            response = json.dumps({"data":{"States":result} , 'message' :' All States', 'is_success' :True})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            return Response(
            status=500,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )