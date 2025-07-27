
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


class Payments(http.Controller):
    url = 'https://gtec-security1.odoo.com'
    db = 'gtec-security1'
    username ='marketing@gtecsecurity.co.uk'
    password = 'GTECWeb$ite'

    @http.route('/payments/all',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_all_payments_methods(self, **kw):
        response = ''

        
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        
        payments_id = models.execute_kw(self.db, uid, self.password, 'payment.provider', 'search_read', [['&' ,['id' , '!=' , 0] ,['active' , '=' ,True]]],{'fields':['id','name']})
        
      
        
        try:
            response = json.dumps({"data":{'payments_methods':payments_id},'message': 'All payments methods'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'No payments methods now'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)])




    @http.route('/payment/my_cart',  auth="public",csrf=False, website=True, methods=['POST'])
    def add_payment_for_sale(self):
        response = ''            
        authe = request.httprequest.headers
        body =json.loads(request.httprequest.data)
        term = body['term']
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = models.execute_kw(self.db, uid, self.password, 'x_user_token', 'search_read', [[['x_studio_user_token' , '=' , token]]],{'fields':['x_studio_user_name']})
        except Exception as e:
            response = json.dumps({ 'data': 'no data', 'message': 'Unauthorized!'})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        if valid_token:
            user_id =int(valid_token[0]['x_studio_user_name'][0])

            user_partner = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['id' , '=' , user_id]]],{'fields':['partner_id']})

            user_partner = user_partner[0]['partner_id'][0]
            user_quot = models.execute_kw(self.db, uid, self.password, 'sale.order', 'search_read', [['&',['state' ,'=' ,'draft'],['partner_id' , '=' , user_partner]]],{'fields':['id','message_ids']})
            if user_quot:
                
                log_note = {
                    'body': 'The customer has selected %s to make the payment.' % term,
                    'model': 'sale.order',
                    'res_id': user_quot[0]['id'],
                    'message_type': 'comment',
                }

                # Append the log note to the existing messages
                existing_messages = user_quot[0]['message_ids'].append((0, 0, log_note))
                
                id = int(user_quot[0]['id'])
                # Update the chatter field of the sale order with the updated messages
                x = models.execute_kw(self.db,uid,self.password,'mail.message','create', [{'body': 'The customer has selected %s to make the payment.' % term,
                    'model': 'sale.order',
                    'res_id': user_quot[0]['id'],
                    'message_type': 'comment',}])
                 
                response=json.dumps({"data":[] , 'message' : 'Product had been added to your cart'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
            else:
                response=json.dumps({"data":[] , 'message' : 'this cart not belong to you '})
                return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
        else:
                response=json.dumps({"data":[] , 'message' : 'Invlid Token'})
                return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
        