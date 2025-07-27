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

_logger = logging.getLogger(__name__)


from pathlib import Path



class Banners(http.Controller):
    
    url = 'https://gtec-security1.odoo.com'
    db = 'gtec-security1'
    username ='marketing@gtecsecurity.co.uk'
    password = 'GTECWeb$ite'


    @http.route('/banners',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_mybanners(self, **kw):
        response = ''            
        authe = request.httprequest.headers
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})

        banners = models.execute_kw(self.db, uid, self.password, 'x_slider_gtec', 'search_read', [[['id' , '!=' , 0]]],{'fields':['id']})
        x = 0
        if banners:
            for i in banners:
                
                banners_id = i['id']
                image_url = self.url + '/web/image?' + 'model=x_slider_gtec&id=' + str(banners_id) + '&field=x_studio_binary_field_64g_1hi0esu21'
                i['image'] = image_url            
                x += 1
        
        else:
            response = json.dumps({"data":{'banners':[]},'message': 'No Images'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        
        try:
            response = json.dumps({"data":{'banners':banners},'message': 'All Images'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'No Images found'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

    @http.route('/cart/extra_info',  auth="public",csrf=False, website=True, methods=['GET'])
    def add_extra_info(self, **kw):
        response = ''            
        body =json.loads(request.httprequest.data)
        po_ref = body.get('reference', False)
        comment = body.get('comment', False)
        authe = request.httprequest.headers
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
                    'body': 'Comment : %s' % comment,
                    'model': 'sale.order',
                    'res_id': user_quot[0]['id'],
                    'message_type': 'comment',
                }

                # Append the log note to the existing messages
                existing_messages = user_quot[0]['message_ids'].append((0, 0, log_note))
                
                id = int(user_quot[0]['id'])
                # Update the chatter field of the sale order with the updated messages
                x = models.execute_kw(self.db,uid,self.password,'mail.message','create', [{'body': 'Comment : %s' % comment,
                    'model': 'sale.order',
                    'res_id': user_quot[0]['id'],
                    'message_type': 'comment',}])
                 
                response=json.dumps({"data":[] , 'message' : 'address had been added to your cart'})
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

    @http.route('/cart/billing_address', auth="public", csrf=False, website=True, methods=['POST'])
    def add_billing_address(self, **kw):
        response = ''
        body = json.loads(request.httprequest.data)
        name = body.get('name' , False)
        email = body.get('email',False)
        street1 = body.get('street1' , False)
        phone = body.get('phone' ,False)
        street2 = body.get('street2' , False)
        city = body.get('city' , False)
        state_id =  body.get('state_id' , False)
        zip = body.get('zip' , False)
        country_id = body.get('country_id' ,False)

        if not (phone):
            response = json.dumps({'data': [], 'message': 'Missing required fields'})
            return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url), allow_none=True)
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url), allow_none=True)
        uid = common.authenticate(self.db, self.username, self.password, {})

        try:
            token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
            valid_token = models.execute_kw(
                self.db, uid, self.password, 'x_user_token', 'search_read',
                [[['x_studio_user_token', '=', token]]],
                {'fields': ['x_studio_user_name']}
            )
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!'})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

        if valid_token:
            try:
                user_id = int(valid_token[0]['x_studio_user_name'][0])
                user_partner = models.execute_kw(
                    self.db, uid, self.password, 'res.users', 'search_read',
                    [[['id', '=', user_id]]],
                    {'fields': ['partner_id']}
                )
                user_partner = user_partner[0]['partner_id'][0]

            
                delivery_address_data = {
                    'name': name,
                    'street': street1,
                    'street2': street2,
                    'city': city,
                    'zip': zip,
                    'country_id': 1,
                    'state_id' : state_id,  # Country ID, e.g., 1 for United States
                    'phone': phone,
                    'email': email
                }

                # Create the delivery address
                print(121212)
              
                address_id =models.execute_kw(self.db, uid, self.password, 'res.partner', 'write', [[user_partner],delivery_address_data])
                user_quot = models.execute_kw(self.db, uid, self.password, 'sale.order', 'search_read', [['&',['state' ,'=' ,'draft'],['partner_id' , '=' , user_partner]]],{'fields':['id' , 'amount_total','amount_tax','amount_paid']})
                # if user_quot:
                    # models.execute_kw(self.db, uid, self.password, 'sale.order', 'write', [[user_quot[0]['id']], {'partner_invoice_id': address_id}]) 
                response = json.dumps({'data': {'partner_id': user_partner}, 'message': 'Address saved successfully'})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            except Exception as e:
                response = json.dumps({'data': [], 'message': str(e)})
                return Response(
                    response, status=500,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        else:
            response = json.dumps({'data': [], 'message': 'Invalid Token'})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

    @http.route('/cart/billing_address/<int:address_id>', auth="public", csrf=False, website=True, methods=['PUT'])
    def update_billing_address(self, address_id, **kw):
        response = ''
        body = json.loads(request.httprequest.data)
        name = body.get('name', False)
        email = body.get('email', False)
        street1 = body.get('street1', False)
        phone = body.get('phone', False)
        street2 = body.get('street2', False)
        city = body.get('city', False)
        state_id = body.get('state_id', False)
        zip = body.get('zip', False)
        country_id = body.get('country_id', False)

        if not phone:
            response = json.dumps({'data': [], 'message': 'Missing required fields'})
            return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url), allow_none=True)
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url), allow_none=True)
        uid = common.authenticate(self.db, self.username, self.password, {})

        try:
            token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
            valid_token = models.execute_kw(
                self.db, uid, self.password, 'x_user_token', 'search_read',
                [[['x_studio_user_token', '=', token]]],
                {'fields': ['x_studio_user_name']}
            )
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!'})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

        if valid_token:
            try:
                user_id = int(valid_token[0]['x_studio_user_name'][0])
                user_partner = models.execute_kw(
                    self.db, uid, self.password, 'res.users', 'search_read',
                    [[['id', '=', user_id]]],
                    {'fields': ['partner_id']}
                )
                user_partner = user_partner[0]['partner_id'][0]

                billing_address_data = {
                    'name': name,
                    'street': street1,
                    'street2': street2,
                    'city': city,
                    'zip': zip,
                    'country_id': country_id,
                    'state_id': state_id,
                    'phone': phone,
                    'email': email
                }

                # Update the billing address
                models.execute_kw(self.db, uid, self.password, 'res.partner', 'write', [[address_id], billing_address_data])
                user_quot = models.execute_kw(
                    self.db, uid, self.password, 'sale.order', 'search_read',
                    [['&', ['state', '=', 'draft'], ['partner_id', '=', user_partner]]],
                    {'fields': ['id', 'amount_total', 'amount_tax', 'amount_paid']}
                )

                response = json.dumps({'data': {'partner_id': user_partner}, 'message': 'Address updated successfully'})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            except Exception as e:
                response = json.dumps({'data': [], 'message': str(e)})
                return Response(
                    response, status=500,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        else:
            response = json.dumps({'data': [], 'message': 'Invalid Token'})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

    @http.route('/cart/set_addresses', auth="public", csrf=False, website=True, methods=['PUT'])
    def set_addresses(self, **kw):
        response = ''
        body = json.loads(request.httprequest.data)
        billing_id = body.get('billing_id', False)
        shipping_id = body.get('shipping_id', False)

        if not (billing_id and shipping_id):
            response = json.dumps({'data': [], 'message': 'Missing required fields'})
            return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url), allow_none=True)
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url), allow_none=True)
        uid = common.authenticate(self.db, self.username, self.password, {})

        try:
            token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
            valid_token = models.execute_kw(
                self.db, uid, self.password, 'x_user_token', 'search_read',
                [[['x_studio_user_token', '=', token]]],
                {'fields': ['x_studio_user_name']}
            )
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!'})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

        if valid_token:
            try:
                user_id = int(valid_token[0]['x_studio_user_name'][0])
                user_partner = models.execute_kw(
                    self.db, uid, self.password, 'res.users', 'search_read',
                    [[['id', '=', user_id]]],
                    {'fields': ['partner_id']}
                )
                user_partner = user_partner[0]['partner_id'][0]

                user_quot = models.execute_kw(
                    self.db, uid, self.password, 'sale.order', 'search_read',
                    [['&', ['state', '=', 'draft'], ['partner_id', '=', user_partner]]],
                    {'fields': ['id', 'amount_total', 'amount_tax', 'amount_paid']}
                )
                if user_quot:
                    models.execute_kw(
                        self.db, uid, self.password, 'sale.order', 'write',
                        [[user_quot[0]['id']], {'partner_id': user_partner, 'partner_invoice_id': billing_id, 'partner_shipping_id': shipping_id}]
                    )

                response = json.dumps({'data': {'partner_id': user_partner}, 'message': 'Addresses updated successfully'})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            except Exception as e:
                response = json.dumps({'data': [], 'message': str(e)})
                return Response(
                    response, status=500,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        else:
            response = json.dumps({'data': [], 'message': 'Invalid Token'})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )



    @http.route('/cart/add_address', auth="public", csrf=False, website=True, methods=['POST'])
    def add_address(self, **kw):
        response = ''
        body = json.loads(request.httprequest.data)
        name = body.get('name' , False)
        email = body.get('email',False)
        street1 = body.get('street1' , False)
        phone = body.get('phone' ,False)
        street2 = body.get('street2' , False)
        city = body.get('city' , False)
        zip = body.get('zip' , False)
        country_id = body.get('country_id' ,False)

        if not (phone):
            response = json.dumps({'data': [], 'message': 'Missing required fields'})
            return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url), allow_none=True)
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url), allow_none=True)
        uid = common.authenticate(self.db, self.username, self.password, {})

        try:
            token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
            valid_token = models.execute_kw(
                self.db, uid, self.password, 'x_user_token', 'search_read',
                [[['x_studio_user_token', '=', token]]],
                {'fields': ['x_studio_user_name']}
            )
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!'})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

        if valid_token:
            try:
                user_id = int(valid_token[0]['x_studio_user_name'][0])
                user_partner = models.execute_kw(
                    self.db, uid, self.password, 'res.users', 'search_read',
                    [[['id', '=', user_id]]],
                    {'fields': ['partner_id']}
                )
                user_partner = user_partner[0]['partner_id'][0]

            
                delivery_address_data = {
                    'parent_id': user_partner,
                    'name': name,
                    'street': street1,
                    'street2': street2,
                    'city': city,
                    'zip': zip,
                    'type' : "delivery",    
                    'country_id': 1,  # Country ID, e.g., 1 for United States
                    'phone': phone,
                    'email': email
                }

                # Create the delivery address
                address_id = models.execute_kw(
                    self.db, uid, self.password,
                    'res.partner', 'create',
                    [delivery_address_data]
                )

                user_quot = models.execute_kw(self.db, uid, self.password, 'sale.order', 'search_read', [['&',['state' ,'=' ,'draft'],['partner_id' , '=' , user_partner]]],{'fields':['id' , 'amount_total','amount_tax','amount_paid']})
                if user_quot:
                    models.execute_kw(self.db, uid, self.password, 'sale.order', 'write', [[user_quot[0]['id']], {'partner_shipping_id': address_id}]) 
                response = json.dumps({'data': {'partner_id': user_partner}, 'message': 'Address saved successfully'})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            except Exception as e:
                response = json.dumps({'data': [], 'message': str(e)})
                return Response(
                    response, status=500,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        else:
            response = json.dumps({'data': [], 'message': 'Invalid Token'})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )


    @http.route('/cart/shipping_addresses',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_shipping_adresses(self, **kw): 
        response = ''
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        try:
            token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
            valid_token = models.execute_kw(
                self.db, uid, self.password, 'x_user_token', 'search_read',
                [[['x_studio_user_token', '=', token]]],
                {'fields': ['x_studio_user_name']}
            )
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!'})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        if valid_token:
            valid_token = models.execute_kw(
                self.db, uid, self.password, 'x_user_token', 'search_read',
                [[['x_studio_user_token', '=', token]]],
                {'fields': ['x_studio_user_name']}
            )
            user_id = int(valid_token[0]['x_studio_user_name'][0])
            print('user_id >> ' , user_id)
            user_records = models.execute_kw(
                self.db, uid, self.password, 'res.users', 'search_read',
                [[['id', '=', user_id]]],
                {'fields': ['id', 'name', 'partner_id']}
            )
            print('user_records >> ' , user_records)
            partner_id=user_records[0]['partner_id'][0]
            partner_records = models.execute_kw(self.db, uid, self.password, 'res.partner', 'search_read', [['|' , ['parent_id', '=', partner_id] , ['id' , '=' , partner_id]]],{
                                            'fields': ['id','name' ,'email','phone','country_id','zip' ,'street', 'street2','city']})
            for partner in partner_records:
                is_valid = all(partner.get(field) for field in partner)  # Check if all fields have a truthy value
                partner['is_valid'] = is_valid and True or False
            print('user_records >> ' , partner_records)
            
            try:
                response = json.dumps({"data":{"shipping_adresses":partner_records}})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )

            except:
                return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
        else:
            response = json.dumps({'data': [], 'message': 'Invalid Token'})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

    

    @http.route('/cart/billing_addresse',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_billing_addresse(self,parent_id= None, **kw): 
        response = ''
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        try:
            token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
            valid_token = models.execute_kw(
                self.db, uid, self.password, 'x_user_token', 'search_read',
                [[['x_studio_user_token', '=', token]]],
                {'fields': ['x_studio_user_name']}
            )
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!'})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        if valid_token:
            user_id = int(valid_token[0]['x_studio_user_name'][0])
            print('user_id >> ' , user_id)
            user_records = models.execute_kw(
                self.db, uid, self.password, 'res.users', 'search_read',
                [[['id', '=', user_id]]],
                {'fields': ['id', 'name', 'partner_id']}
            )
            print('user_records >> ' , user_records)
            partner_id=user_records[0]['partner_id'][0]
            partner_records = models.execute_kw(
                self.db, uid, self.password, 'res.partner', 'search_read',
                [[['id', '=', partner_id]]],
                {'fields': ['id', 'name', 'email', 'phone', 'country_id', 'zip', 'street', 'street2', 'city']}
            )
            for partner in partner_records:
                is_valid = all(partner.get(field) for field in partner)  # Check if all fields have a truthy value
                partner['is_valid'] = is_valid and True or False
            try:
                response = json.dumps({"data":{"billing_adresses":partner_records}})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )

            except:
                return Response(
                response, status=500,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
        else:
            response = json.dumps({'data': [], 'message': 'Invalid Token'})
            return Response(
                response, status=403,
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
            response = json.dumps({"data":{"countries":countries}})
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
    def get_state(self,id, **kw): 
        
        response = ''
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        
        try:
            
            state = models.execute_kw(self.db, uid, self.password, 'res.country.state', 'search_read', [[['country_id' , '=' , int(id)]]],{
                                        'fields': ['id','name' ] })
            response = json.dumps({"state":state})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': str(e)})
            return Response(
            response, status=500,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )