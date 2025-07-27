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



class WishList(http.Controller):
    
    url = 'https://gtec-security1.odoo.com'
    db = 'gtec-security1'
    username ='marketing@gtecsecurity.co.uk'
    password = 'GTECWeb$ite'


    def extract_float_value(self,string):
        pattern = r"[-+]?\d*\.\d+|\d+"  # Regular expression pattern to match float or integer values
        match = re.search(pattern, string)
        if match:
            float_value = float(match.group())
            return float_value
        else:
            return None
    @http.route('/wishlist/mine',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_my_wishlist(self,idd= None, **kw): 
        response = '' 
        products_res=[]           
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
            user_wishlist = models.execute_kw(self.db, uid, self.password, 'product.wishlist', 'search_read', [[['partner_id' , '=' , user_partner]]],{'fields':['id' , 'partner_id','price','product_id']})
            if user_wishlist:
                
                for i in user_wishlist:
                    product_id = int(i['product_id'][0])
                    products =models.execute_kw(self.db, uid, self.password, 'product.product', 'search_read',
                                            [[['id', '=', product_id]]], {'fields': ['id', 'name', 'type', 'uom_name', 'cost_currency_id', 'categ_id', 'list_price','description_sale','x_studio_specifications' ,'x_studio_why_and_when', 'product_template_image_ids','x_studio_product_feature_mobile','tax_string','product_tmpl_id']})
                     

                    user_id = int(valid_token[0]['x_studio_user_name'][0])
                    user_partner = models.execute_kw(
                        self.db, uid, self.password, 'res.users', 'search_read',
                        [[['id', '=', user_id]]], {'fields': ['partner_id', 'property_product_pricelist']}
                    )
                    user_product_pricelist_id = user_partner[0]['property_product_pricelist'][0]
                    user_partner = user_partner[0]['partner_id'][0]

                    product_price_list = models.execute_kw(
                        self.db, uid, self.password, 'product.pricelist.item', 'search_read',
                        [[['pricelist_id', '=', user_product_pricelist_id]]],
                        {'fields': ['product_id', 'fixed_price']}
                    )

                    for product in products:
                        for prod in product_price_list:
                            if product['product_id'][0] == prod['product_id'][0]:
                                product['list_price'] = prod['fixed_price']
                    x = 0
                    im = []
                    for i in products:
                        product_id = i['id']
                        i['product_tmpl_id'] = products[0]['product_tmpl_id'][0]
                        
                        if i['product_template_image_ids']:
                            for item in i['product_template_image_ids']:
                                images = models.execute_kw(
                                self.db, uid, self.password, 'product.image', 'search_read',
                                [[['id', '=', item]]],
                                {'fields': ['id','image_1920' ]}
                            )
                                if images:
                                    im_url = self.url + '/web/image?' + 'model=product.image&id=' + str(item) + '&field=image_1920'
                                    im.append({
                                        'id' : images[0]['id'],
                                        'image' : im_url
                                    })
                                    images = False
                        image_url = self.url + '/web/image?' + 'model=product.template&id=' + str(product_id) + '&field=image_1920'
                        i['image'] = image_url
                        categ_id = i['categ_id'][0]
                        im.append({
                            'id': 0 ,
                            'image' : image_url}
                        )
                        categ_name = i['categ_id'][1]
                        products[x]['categ_name'] = categ_name
                        products[x]['categ_id'] = categ_id
                        products[x]['images_catalog']  = im
                        
                        if products[x]['tax_string']:
                            products[x]['list_price'] = self.extract_float_value(products[x]['tax_string'])
                        products[x]['list_price'] = products[x]['list_price'] if valid_token else None
                        im = []
                        x += 1
                        print('products '  , products)
                        products_res.append(products[0])
                
                response=json.dumps({"data":{'wishlist':products_res}, 'message' : 'wishlist Details'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
            else:
                response=json.dumps({"data":[], 'message' : "you don't have wishlist"})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
        else:
                
                response=json.dumps({"data":[] , 'message' : 'Invalid token'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)])

    @http.route('/wishlist/<int:product_id>', auth="public", csrf=False, website=True, methods=['POST'])
    def add_to_wishlist(self, product_id, **kw):
        response = ''
        
        authe = request.httprequest.headers
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = models.execute_kw(self.db, uid, self.password, 'x_user_token', 'search_read',
                                            [[['x_studio_user_token', '=', token]]],
                                            {'fields': ['x_studio_user_name']})
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!'})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        if valid_token:
            user_id = int(valid_token[0]['x_studio_user_name'][0])
            user_partner = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',
                                            [[['id', '=', user_id]]], {'fields': ['partner_id']})
            user_partner = user_partner[0]['partner_id'][0]
            
            # Check if the product with the given ID exists
            product_exists = models.execute_kw(self.db, uid, self.password, 'product.product', 'search_count',
                                                [[['product_tmpl_id', '=', int(product_id)]]])
            product_data = models.execute_kw(
            self.db, uid, self.password, 'product.product', 'search_read',
            [[['product_tmpl_id', '=', product_id]]],
            {'fields': ['list_price', 'description_sale','tax_string' , 'name'], 'limit': 1}
        )    
            if product_exists:
                # Create a new record in the product.wishlist model
                wishlist_data = {
                    'partner_id': user_partner,
                    'product_id': product_data[0]['id'],
                    'website_id' : 1
                }
                wishlist_id = models.execute_kw(self.db, uid, self.password, 'product.wishlist', 'create', [wishlist_data])
                
                if wishlist_id:
                    response = json.dumps({'data': {'wishlist_id': wishlist_id}, 'message': 'Product added to wishlist'})
                    return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                                ('Content-Length', 100)]
                    )
            else:
                response = json.dumps({'data': [], 'message': 'Product does not exist'})
                return Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                            ('Content-Length', 100)]
                )
        else:
            response = json.dumps({'data': [], 'message': 'Invalid token'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
            )

    @http.route('/wishlist/<int:product_id>', auth="public", csrf=False, website=True, methods=['DELETE'])
    def delete_from_wishlist(self, product_id=None, **kw):
        response = ''
        
        authe = request.httprequest.headers
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = models.execute_kw(self.db, uid, self.password, 'x_user_token', 'search_read',
                                            [[['x_studio_user_token', '=', token]]],
                                            {'fields': ['x_studio_user_name']})
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!'})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        if valid_token:
            user_id = int(valid_token[0]['x_studio_user_name'][0])
            user_partner = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read',
                                            [[['id', '=', user_id]]], {'fields': ['partner_id']})
            user_partner = user_partner[0]['partner_id'][0]
            
            # Check if the wishlist ID exists
            wishlist_exists = models.execute_kw(self.db, uid, self.password, 'product.wishlist', 'search',
                                                [['&',['product_id', '=', product_id], ['partner_id', '=', user_partner]]])
            if wishlist_exists:
                # Delete the wishlist item
                models.execute_kw(self.db, uid, self.password, 'product.wishlist', 'unlink', [[wishlist_exists[0]]])
                
                response = json.dumps({'data': {'wishlist_id': wishlist_exists[0]}, 'message': 'Product removed from wishlist'})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                            ('Content-Length', 100)]
                )
            else:
                response = json.dumps({'data': [], 'message': 'Wishlist item does not exist'})
                return Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                            ('Content-Length', 100)]
                )
        else:
            response = json.dumps({'data': [], 'message': 'Invalid token'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
            )