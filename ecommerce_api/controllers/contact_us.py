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
import re
import socket
from os import path
import random
import string



class ContactUs(http.Controller):
    
    url = 'https://gtec-security1.odoo.com'
    db = 'gtec-security1'
    username ='marketing@gtecsecurity.co.uk'
    password = 'GTECWeb$ite'


    @http.route('/contact_us',  auth="public",csrf=False, website=True, methods=['POST'])
    def add_contact_us(self, **kw):
        response = ''            
        authe = request.httprequest.headers
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        body =json.loads(request.httprequest.data)
        if 'name' in body :
            name = body['name']
        if 'number' in body :
            number = body['number']
        if 'email' in body :
            email = body['email']
        if 'message' in body :
            message = body['message']
        user_id = models.execute_kw(self.db, uid, self.password, 'crm.lead', 'create', [{'name': name, 'email_from' : email, 'phone' :number ,'description':message}])
        
        response = json.dumps({ 'message': 'تم الارسال' })
        return Response(
        response, status=200,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
    )

        
        
        
        