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
import os
import time
import base64
from os import path
from pathlib import Path
from os import environ
from dotenv import load_dotenv
_logger = logging.getLogger(__name__)


load_dotenv()

class ContactUs(http.Controller):
    url = os.getenv('URL')
    db = os.getenv('db')
    username = os.getenv('username')
    password = os.getenv('password')
    
    def validation_email(self,email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if(re.fullmatch(regex, email)):
            
            return True
        else:
            
            return False


    def check_phone_num(self,data):
            val=data

            if val.isdigit():

                return True

            else:
                return False

    def _validation(self,data):
        data = str(data)
        if len(data) != 0 :
            return True
        elif len(data) == 0:
            return False
        else:
            pass
   



    @http.route('/contact_us',  auth="public",csrf=False, website=True, methods=['POST'])
    def contact_us(self,**kw):
        body = json.loads(request.httprequest.data)
        full_name = body['full_name']
        phone_number = body['phone_number']
        country_code = body['country_code']
        email = body['email']
        message = body['message']
        reason=body['reason']
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        phone_validation = self._validation(phone_number)
        email_validation = self.validation_email(email)


        
        if email_validation == False:
            response = json.dumps({"data":[],'message': 'يرجى إدخال  بريد الكتروني صالح'})
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

        check_phone = self.check_phone_num(phone_number)
        if check_phone == False:
            response = json.dumps({"data":[],'message': 'رقم الهاتف يحتوي على محارف'})
            return Response(
            response, status=422,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        
        
        if phone_number[0] == '0' :
            
            full_phone = country_code + phone_number[1:]
        else :
            
            full_phone = country_code + phone_number
        
        user_id = models.execute_kw(self.db, uid, self.password, 'contact.us', 'create', [{'name': full_name, 'email' : email, 'phone_number' :full_phone ,'message':message,'reason':reason }])
        
        response = json.dumps({ 'message': 'تم الارسال' })
        return Response(
        response, status=200,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    )
    @http.route('/about_us',  auth="public",csrf=False, website=True, methods=['GET'])
    def about_us(self,**kw):

        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        data =models.execute_kw(self.db, uid, self.password, 'about.us', 'search_read', [[['id' , '=', 1]]] , {'fields': ['title', "brief","face_book","linked_in","instagram","first_image_path","second_image_path","third_image_path"]})  
        response = json.dumps({"data":{'title' : data[0]['title'], 'brief' : data[0]['brief'],'facebook':data[0]['face_book'],'linkedin':data[0]['linked_in'],'intsagram':data[0]['instagram'],"first_image_path": data[0]['first_image_path'],"second_image_path": data[0]['second_image_path'],"third_image_path": data[0]['third_image_path']}})
        return Response(
        response, status=200,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
    

    @http.route('/privacy_policy',  auth="public",csrf=False, website=True, methods=['GET'])
    def privacy_policy(self,**kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        data =models.execute_kw(self.db, uid, self.password, 'privacy.policy', 'search_read',[[['id' ,'!=', False]]] , {'fields': ['content']})  
        response = json.dumps({"data":data[0]})
        return Response(
        response, status=200,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
    @http.route('/terms_of_use',  auth="public",csrf=False, website=True, methods=['GET'])
    def terms_of_use(self,**kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        data =models.execute_kw(self.db, uid, self.password, 'terms.use', 'search_read',[[['id' ,'!=', False]]] , {'fields': ['content']})  
        response = json.dumps({"data":data[0]})
        return Response(
        response, status=200,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
    @http.route('/about_us2',  auth="public",csrf=False, website=True, methods=['GET'])
    def about_us2(self,**kw):
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        data =models.execute_kw(self.db, uid, self.password, 'about.us', 'search_read', [[['id' , '=', 2]]] , {'fields': ['title', "brief" ,"first_image_path","second_image_path","third_image_path"]})    
        
        response = json.dumps({'data':{'title' : data[0]['title'], 'brief' : data[0]['brief'],"first_image_path": data[0]['first_image_path'],"second_image_path": data[0]['second_image_path']}})
        return Response(
        response, status=200,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )