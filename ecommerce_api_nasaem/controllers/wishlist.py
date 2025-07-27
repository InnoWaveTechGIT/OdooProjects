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
import jwt

_logger = logging.getLogger(__name__)


from pathlib import Path



class WishList(http.Controller):
    
    

    url = 'https://www.alnasaem.com' 
    def extract_float_value(self,string):
        pattern = r"[-+]?\d*\.\d+|\d+"  # Regular expression pattern to match float or integer values
        match = re.search(pattern, string)
        if match:
            float_value = float(match.group())
            return float_value
        else:
            return None
    @http.route('/wishlist/mine',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_my_wishlist(self,currency= None, **kw): 
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        response = '' 
        result = []
        price = {}
        pricelist = []
        # Process the products as needed
        authe = request.httprequest.headers
        valid_token =''
        price_cu=0.0
        pricecurrency={}
        products_res=[]           
        authe = request.httprequest.headers
        try:
            token = authe['Authorization'].replace('Bearer ', '')
             
            valid_token = request.env['user.token.nasaem'].search([('token' , '=' , token)])
        except Exception as e:
            response = json.dumps({ 'data': 'no data', 'message': 'Unauthorized!', 'is_success' :False})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        currency_id = request.env['res.currency'].search([('name' , '=' , currency)]) if currency else ''
        if valid_token:
            try:
                dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!', 'is_success' :False})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            location = dec_token['location']
            if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                location = location
            else :
                location = 'KW'
            country = request.env['res.country'].search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
            user_id =valid_token[0]['user_id']
            user_partner = request.env['res.users'].sudo().search_read(
                [['id', '=', user_id]]
            )
            user_partner = user_partner[0]['partner_id']            
            user_wishlist = request.env['product.wishlist'].sudo().search([('partner_id' , '=' , int(user_partner[0]))])
            if user_wishlist:
                
                for i in user_wishlist:
                    product_id = i.product_id.id
                    product = request.env['product.product'].with_context(lang=language).search([('id' , '=' , product_id)])
                    if cur:
                        pricelist = request.env['product.pricelist'].sudo().search(
                            [('currency_id.name', '=', cur)],
                            limit=1
                        )
                        if pricelist:
                            price = pricelist.sudo()._compute_price_rule( products = product, qty =1, uom = product.uom_id)
                        pricecurrency = request.env['res.currency'].sudo().search(
                            [('name', '=', cur)],
                            limit=1
                        )
                    if pricecurrency:
                        price_cu = product.list_price * pricecurrency.rate
                    else :
                        price_cu = product.list_price
                    
                    for i in product:
                        product_id = i.product_tmpl_id.id
                        products_res.append({
                                'id': i.product_tmpl_id.id,
                                'name': i.name,
                                'description': i.description,
                                'image':self.url + '/web/image?' + 'model=product.product&id=' + str(i.id) + '&field=image_1920',
                                'price' : next(iter(price.values()))[0] if price else price_cu ,
                                'currency' : i.cost_currency_id.name ,
                                'description_sale' : i.description_sale,
                                'category' : [{
                                    'id' : item.id,
                                    'name' : item.name
                                }for item in i.public_categ_ids ]
                                # Add other fields as required
                    })
                if currency_id:
                    price_list = request.env['product.pricelist'].search([('currency_id' , '=' , currency_id.id)]) 
                    for product in products_res:
                        currency = price_list.currency_id
                        price = price_list._compute_price_rule(product['id'], 1.0)[0]
                        formatted_price = currency.format(price)
                        product['price'] = formatted_price
                        product['currency'] = currency.name


                message = 'تفاصيل المفضلات' if language == 'ar_001' else 'wishlist Details'
                response=json.dumps({"data":{'wishlist':products_res}, 'message' : message , 'is_success' :True})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
            else:
                message = 'لا تملك اي عنصر في قائمة المفضلة' if language == 'ar_001' else "you don't have wishlist"
                response=json.dumps({"data":[], 'message' : message , 'is_success' :False})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
        else:
                
                response=json.dumps({"data":[] , 'message' : 'Invalid token', 'is_success' :False})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)])

    @http.route('/wishlist/<int:product_id>', auth="public", csrf=False, website=True, methods=['POST'])
    def add_to_wishlist(self, product_id, **kw):
        response = ''
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]

        try:
            token = request.httprequest.headers['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].sudo().search_read(
                [['token', '=', token]]
            )
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!', 'is_success' :False})
            return http.Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', '100')]
            )

        if valid_token:
            user_id = int(valid_token[0]['user_id'])
            user_partner = request.env['res.users'].sudo().search_read(
                [['id', '=', user_id]]
            )
            try:
                dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
                location = dec_token['location']
                if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                    location = location
                else :
                    location = 'KW'
                country = request.env['res.country'].search([('code', '=', location)])
                if country:
                    cur = country.currency_id.name
            except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!' , 'is_success' :False})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            user_partner = user_partner[0]['partner_id'] 
            # Check if the product with the given ID exists
            product_exists = request.env['product.product'].sudo().search_count(
                [['product_tmpl_id', '=', product_id]]
            )

            if product_exists:
                product = request.env['product.product'].sudo().with_context(lang=language).search(
                [('product_tmpl_id', '=', product_id)],limit=1
            )
                # Create a new record in the product.wishlist model
                wishlist_data = {
                    'partner_id': user_partner[0],
                    'product_id': product.id,
                    'website_id': 2
                }
                wishlist_id = request.env['product.wishlist'].sudo().create(wishlist_data)

                if wishlist_id:
                    message = 'تم إضافة المنتج بنجاح' if language == 'ar_001' else 'Product added to wishlist'
                    response = json.dumps({'data': {'wishlist_id': wishlist_id.id}, 'message': message , 'is_success' :True})
                    return http.Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', '100')]
                    )
            else:
                message = 'المنتج غير موجود' if language == 'ar_001' else 'Product does not exist'
                response = json.dumps({'data': [], 'message': message, 'is_success' :False})
                return http.Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', '100')]
                )
        else:
            response = json.dumps({'data': [], 'message': 'Invalid token' , 'is_success' :False})
            return http.Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', '100')]
            )

    @http.route('/wishlist/<int:product_id>', auth="public", csrf=False, website=True, methods=['DELETE'])
    def delete_from_wishlist(self, product_id=None, **kw):
        response = ''
        product_id= int(product_id)
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        try:
            token = request.httprequest.headers['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].sudo().search_read(
                [['token', '=', token]])
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!' , 'is_success' :False})
            return http.Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', '100')]
            )

        if valid_token:
            user_id = int(valid_token[0]['user_id'])
            user_partner = request.env['res.users'].sudo().search(
                [('id', '=', user_id)]
            )
            user_partner = user_partner.partner_id.id 

            # Check if the wishlist ID exists
            w = request.env['product.wishlist'].sudo().search(
                [('partner_id', '=', user_partner)]
            )
            wishlist_exists = request.env['product.wishlist'].sudo().search(
                [('product_id.product_tmpl_id', '=', product_id), ('partner_id', '=', user_partner)]
            )
            if wishlist_exists:
                # Delete the wishlist item
                wishlist_exists.sudo().unlink()
                message = 'تم حذف المنتج من قائمة المفضلة بنجاح' if language == 'ar_001' else 'Product removed from wishlist'
                response = json.dumps({'data': {'wishlist_id': wishlist_exists.id}, 'message': message , 'is_success' :True})
                return http.Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', '100')]
                )
            else:
                message = 'العنصر غير موجود في قائمة المفضلة' if language == 'ar_001' else 'Wishlist item does not exist'
                response = json.dumps({'data': [], 'message': message, 'is_success' :False})
                return http.Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', '100')]
                )
        else:
            response = json.dumps({'data': [], 'message': 'Invalid token', 'is_success' :False})
            return http.Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', '100')]
            )

    @http.route('/wishlist/mine', auth="public", csrf=False, website=True, methods=['DELETE'])
    def delete_my_wishlist(self, **kw):
        response = ''
        authe = request.httprequest.headers
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!', 'is_success' :False})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        if valid_token:
            user_id = int(valid_token[0]['user_id'])
            user_partner = request.env['res.users'].sudo().search(
                [('id', '=', user_id)]
            )
            user_partner = user_partner.partner_id.id 

            
            user_wishlist = request.env['product.wishlist'].search([('partner_id', '=', user_partner)])
            
            if user_wishlist:
                user_wishlist.unlink()  # Delete all wishlist items for the user
                message = 'تم حذف قائمة المفضلة بنجاح' if language == 'ar_001' else "Wishlist items deleted successfully"
                response = json.dumps({"data": [], 'message': message , 'is_success' :True} )
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
                )
            else:
                message = 'أنت لا تملك هذا المنتج في قائمة المفضلة' if language == 'ar_001' else "You don't have a wishlist"
                response = json.dumps({"data": [], 'message': message , 'is_success' :False})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
                )
        else:
            response = json.dumps({"data": [], 'message': 'Invalid token' , 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
            )