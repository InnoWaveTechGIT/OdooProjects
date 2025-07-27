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



class Auth(http.Controller): 

    @http.route('/school/auth/login', cors="*", auth="public",csrf=False, methods=['POST'])
    def log_in_school(self,idd= None, **kw):               
            uid = False
            login = kw['phone']
            language = 'en'
            country_code = kw['country_code']
            message = ''
            password = kw['password']
            login=country_code+login
            headers = request.httprequest.headers
            if 'Accept-Language' in headers and headers["Accept-Language"] == "ar":
                language = "ar_SY"
            else:
                language = 'en'
             
            user_id = request.env['res.users'].sudo().search([('login' , '=' , login)])
            if len(user_id)==0 :
               
                message = 'رقم الهاتف خاطئ'if language == 'ar_SY' else 'Wrong Phone Number'
                response=json.dumps({"data":[],'message': message})
                return Response( response, status=402,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
           
                    
            
            elif len(user_id) != 0:    
                db = http.request.env.cr.dbname
                try:
                    uid = request.session.authenticate(db, login, password)
                except Exception as e:
                    user_details = []
                    message = 'رقم الهاتف او كلمة المرور خاطئة'if language == 'ar_SY' else 'Incorrect Phone or password'
                    response=json.dumps({"data":{"user":user_details,"token":'Null' }, 'message':message , 'is_success' :False} )
                    return Response( response,status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                date_now = datetime.today()
                is_ther_token = request.env['user.token.school'].search([('user_id' , '=' , user_id.id)])
                if len(is_ther_token) != 0 :
                    try:
                        is_ther_token.write({
                            'refresh_token_time' : date_now
                        })
                    except Exception as e:

                        response = json.dumps({'message':str(e)})
                        return Response(
                            response, status=400,
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]) 
                    
                    user_details = [{"id":user_id.id,"name":user_id.name,"phone":user_id.login,'image_path':user_id.image_url, 'type' : user_id.user_type}]
                    message = 'تفاصيل الحساب'if language == 'ar_SY' else 'Profile Details'
                    response=json.dumps({"data":{"user":user_details[0],"token":is_ther_token.access_token}, 'message':message})
                    return Response( response,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                else : 
                    is_ther_token = request.env['user.token.school'].create({
                        'user_id' : user_id.id
                    })
                    user_details = [{"id":user_id.id,"name":user_id.name,"phone":user_id.login,'image_path':user_id.image_url , 'type' : user_id.user_type}]
                    message = 'تفاصيل الحساب'if language == 'ar_SY' else 'Profile Details'
                    response=json.dumps({"data":{"user":user_details[0],"token":is_ther_token.access_token}, 'message':message}) 
                    return Response( response, 
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)] 
                    )



    @http.route('/school/auth/login_bin', cors="*", auth="api_key",csrf=False, website=True, methods=['PATCH'])
    def update_log_in_bin(self,idd= None, **kw):               
            uid = request.env.uid

            bin = kw['bin']
            password = kw['password']
            language = 'en'
            message = ''
            headers = request.httprequest.headers
            if 'Accept-Language' in headers and headers["Accept-Language"] == "ar":
                language = "ar_SY"
            else:
                language = 'en'
            db = http.request.env.cr.dbname
            
            user_id = request.env['res.users'].sudo().search([('id' , '=' ,uid )])
            try:
             
                uid = request.session.authenticate(db, user_id.login, password)
            except Exception as e:
                message = 'كلمة المرور او الرقم خاطئ' if language == 'ar_SY' else 'Incorrect Phone or password'
                response = json.dumps({"data":[] ,'message': message, 'is_success': False})
                return Response(response, status=401, headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
            user_id.sudo().write({
                'bin_fields' : bin
            })

            message = 'تم تغيير الرقم السري'if language == 'ar_SY' else 'BIN have been changed'
            response=json.dumps({"data":[],'message': message})
            return Response( response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
             

    @http.route('/school/auth/login_bin', cors="*", auth="api_key",csrf=False, website=True, methods=['POST'])
    def Update_bin(self,idd= None, **kw):               
            uid = request.env.uid

            bin =kw['bin']
            
            language = 'en'
            message = ''
            headers = request.httprequest.headers
            if 'Accept-Language' in headers and headers["Accept-Language"] == "ar":
                language = "ar_SY"
            else:
                language = 'en'
             
            user_id = request.env['res.users'].sudo().search([('bin_fields' , '=' , bin) , ('id' , '=' ,uid )])
            if len(user_id)==0 :
               
                message = 'رقم  خاطئ'if language == 'ar_SY' else 'Wrong Number'
                response=json.dumps({"data":[],'message': message})
                return Response( response, status=402,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
           
                    
            
            elif len(user_id) != 0:    
                
                date_now = datetime.today()
                
                is_ther_token = request.env['user.token.school'].search([('user_id' , '=' , user_id.id)])
                if len(is_ther_token) != 0 :                    
                    user_details = [{"id":user_id.id,"name":user_id.name,"phone":user_id.login,'image_path':user_id.image_url , 'type' : user_id.user_type}]
                    message = 'تفاصيل الحساب'if language == 'ar_SY' else 'Profile Details'
                    response=json.dumps({"data":{"user":user_details[0]}, 'message':message})
                    return Response( response,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                else : 
                    
                    user_details = [{"id":user_id.id,"name":user_id.name,"phone":user_id.login,'image_path':user_id.image_url}]
                    message = 'تفاصيل الحساب'if language == 'ar_SY' else 'Profile Details'
                    response=json.dumps({"data":{"user":user_details[0]}, 'message':message}) 
                    return Response( response, 
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)] 
                    )