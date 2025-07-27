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
        except Exception as e:
                message = 'بعض الحقول الإجبارية غير مدخل' if language == 'ar_001' else 'Some requierd fields is not enterd'
                response = json.dumps({'message':str(e) , 'is_success' :False})
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
                print('in')
                user_id=request.env['res.users'].sudo().create({
                    'name': username,
                    'password' : password,
                    'login' :email,
                    'phone' :phone ,
                    'company_id' :request.env.company.id,
                    'groups_id': [(6, 0, [portal_group.id])] ,
                })
                print('in12')
                user_id.partner_id.email=email
            except:
                user_id=request.env['res.users'].with_user(2).create({
                    'name': username,
                    'password' : password,
                    'login' :email,
                    'phone' :phone ,
                    'company_id' :request.env.company.id,
                    'groups_id': [(6, 0, [portal_group.id])] ,
                })

            if user_id :

                date_now = str(datetime.today())
                payload = {
                        'id': user_id.id,
                        'username': username,
                        'login' :email ,
                        'timestamp' : date_now,
                        }
                str_uid = str(user_id)
                SECRET='ali.ammar'
                enc = jwt.encode(payload, SECRET)
                user_token=request.env['user.token.haven'].sudo().create({
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

                password = kw['password']
            except Exception as e:
                message = 'بعض الحقول الإجبارية غير مدخل'if language == 'ar_001' else 'Some requierd fields is not enterd'
                response = json.dumps({'message':message , 'is_success' :False})
                return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])

            user_id = request.env['res.users'].sudo().search([('login' , '=' , login)])
            print('user_id >>>>>>>>> ' , user_id)
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
                db = http.request.env.cr.dbname
                print('db >>>>> ' , db)
                try:
                    credential = {'login': login, 'password': password, 'type': 'password'}
                    uid=request.session.authenticate(db, credential)
                    print('uid >>>>>>>>> ' , uid)
                except Exception as e:
                    user_details = []
                    message = 'البريد الإلكتروني او كلمة المرور خاطئة'if language == 'ar_001' else 'Incorrect email or password'
                    response=json.dumps({"data":{"user":str(e),"token":'Null' }, 'message':message , 'is_success' :False} )


                    # response=json.dumps({"data":{"user":user_details,"token":'Null' }, 'message':message , 'is_success' :False} )
                    return Response( response,status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                date_now = datetime.today()
                is_ther_token = request.env['user.token.haven'].search([('user_id' , '=' , user_id.id)])
                if len(is_ther_token) != 0 :
                    date_now = str(datetime.today())
                    payload = {
                            'id': user_id.id,
                            'username': user_id.name,
                            'login' :login ,
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
                            'timestamp' : date_now,
                            }
                    str_uid = str(user_id)
                    SECRET='ali.ammar'
                    enc = jwt.encode(payload, SECRET)
                    is_ther_token = request.env['user.token.haven'].sudo().create({
                        'user_id' : user_id.id,
                        'token' : enc
                    })
                    message = 'تفاصيل الحساب'if language == 'ar_001' else 'profile details'
                    user_details = [{"id":user_id.id,"username" :user_id.name,"email":user_id.login,"phone":user_id.phone,"timestamp":str(date_now)}]
                    response=json.dumps({"data":{"user":user_details[0],"token":is_ther_token.token}, 'message':message , 'is_success' :True})
                    return Response( response,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
