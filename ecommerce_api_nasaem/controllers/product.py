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
import collections

class Categories(http.Controller):
    url = 'https://www.alnasaem.com' 
    @http.route('/products/<int:product_id>',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_product_by_id(self, product_id,cur=None,loc=None ,**kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]

        product_model = http.request.env['product.template']
        products = product_model.sudo().with_context(lang=language).search([('id', '=', product_id),('qty_available' ,'!=' , 0)])
        result = []
        price = {}
        check_str=lambda x:x if x else ''
        pricelist = []
        # Process the products as needed
        authe = request.httprequest.headers
        valid_token =''
        price_cu=0.0
        pricecurrency={}
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            pass

        if valid_token:
            try:
                dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!' , 'is_success' :False})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        
            location = dec_token['location']
            if location:
                    if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                            location = location
                    else :
                        location = 'KW'
            else :
                location = 'KW'
            country = request.env['res.country'].search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
        else :
            location = loc
            if location:
                    if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                            location = location
                    else :
                        location = 'KW'
            else :
                location = 'KW'
            country = request.env['res.country'].search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
        
        for product in products:
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
            images = [{
                'url': self.url + '/web/image?' + 'model=product.image&id=' + str(item.id) + '&field=image_1920'
            } for item in product.product_template_image_ids]
            images.append({'url' :self.url + '/web/image?' + 'model=product.template&id=' + str(product.id) + '&field=image_1920' })
            result.append({
                'id': product.id,
                'name': product.name,
                'website_ribbon_id' : [{'id':template.id,'name':check_str(template.html) ,'text_color' : template.text_color , 'class' : template.html_class , 'bg_color' : template.bg_color} for template in product.website_ribbon_id] ,
                'description': product.description,
                'price' :  price_cu,
                'new_price': next(iter(price.values()))[0] if price else price_cu,
                'currency' : cur  if pricecurrency else product.cost_currency_id.name ,
                'description_sale' : product.description_sale,
                'images' : images,
                'category' : [{
                                    'id' : item.id,
                                    'name' : item.name
                                }for item in product.public_categ_ids ]
            })
        
        if result:
            message = 'Product with specified ID' if language == 'ar_001' else "المنتج صاحب المعرف المطلوب"
            response = json.dumps({'data': result, 'message': message , 'is_success' :True})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            message = 'لا يوجد منتج بالمعرف المطلوب' if language == 'ar_001' else 'No products found with specified ID'
            response = json.dumps({'data': [], 'message': message , 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )


    @http.route('/products/categories/<int:categ_id>',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_product_by_categ_id_id(self, categ_id,cur=None,loc=None , **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        product_model = request.env['product.template']
        products = product_model.sudo().with_context(lang=language).search([('public_categ_ids', 'in', categ_id),('is_published' ,'=' , True),('qty_available' ,'!=' , 0)])
        result = []
        price = {}
        pricelist = []
        # Process the products as needed
        check_str=lambda x:x if x else ''
        authe = request.httprequest.headers
        valid_token =''
        price_cu=0.0
        pricecurrency={}
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            pass

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
            if location:
                    if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                            location = location
                    else :
                        location = 'KW'
            else :
                location = 'KW'
            country = request.env['res.country'].with_context(lang=language).search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
        else :
            location = loc
            if location:
                    if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                            location = location
                    else :
                        location = 'KW'
            else :
                location = 'KW'
            country = request.env['res.country'].search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
        
        for product in products:
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
                
            result.append({
                'id': product.id,
                'name': product.name,
                'website_ribbon_id' : [{'id':template.id,'name':check_str(template.html) ,'text_color' : template.text_color , 'class' : template.html_class , 'bg_color' : template.bg_color} for template in product.website_ribbon_id] ,
                'description': product.description,
                'image':self.url + '/web/image?' + 'model=product.template&id=' + str(product.id) + '&field=image_1920',
                'price' :  price_cu,
                'new_price': next(iter(price.values()))[0] if price else price_cu,
                'currency' : cur  if pricecurrency else product.cost_currency_id.name ,
                'description_sale' : product.description_sale,
                'category' : [{
                                    'id' : item.id,
                                    'name' : item.name
                                }for item in product.public_categ_ids ]
            })
        
        if result:
            message =  "المنتج صاحب المعرف المطلوب"  if language == 'ar_001' else 'Product with specified ID'
            response = json.dumps({'data': result, 'message': message , 'is_success' :True})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            message = 'لا يوجد منتج بالمعرف المطلوب' if language == 'ar_001' else 'No products found with specified ID'
            response = json.dumps({'data': [], 'message': message , 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

    @http.route('/ctegories/hairwigs/products',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_hair_products_wigs(self,cur=None,loc=None, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        product_model = request.env['product.template'].sudo()
        products = product_model.with_context(lang=language).search([('public_categ_ids', 'in', [3615]) ,('is_published' ,'=' , True),('qty_available' ,'!=' , 0)], order='id desc', limit=16)
        result = []
        price=0
        pricelist={}
        authe = request.httprequest.headers
        valid_token =''
        check_str=lambda x:x if x else ''
        price_cu=0.0
        pricecurrency={}
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            pass

        if valid_token:
            try:
                dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!' , 'is_success' :False})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        
            location = dec_token['location']
            if location:
                if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                        location = location
                else :
                    location = 'KW'
            else :
                location = 'KW'
            country = request.env['res.country'].search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
        else :
            location = loc
            if location:
                if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                        location = location
                else :
                    location = 'KW'
            else :
                location = 'KW'
            country = request.env['res.country'].search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
        
        for product in products:
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
                
            result.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'website_ribbon_id' : [{'id':template.id,'name':check_str(template.html) ,'text_color' : template.text_color , 'class' : template.html_class , 'bg_color' : template.bg_color} for template in product.website_ribbon_id] ,
                'image':self.url + '/web/image?' + 'model=product.template&id=' + str(product.id) + '&field=image_1920',
                'price' :  price_cu,
                'new_price': next(iter(price.values()))[0] if price else price_cu,
                'currency' : cur  if pricecurrency else product.cost_currency_id.name ,
                'description_sale' : product.description_sale,
                'category' : [{
                                    'id' : item.id,
                                    'name' : item.name
                                }for item in product.public_categ_ids ]
            })
            

        if result:
            message = 'تمديدات الشعر و الوصلات' if language == 'ar_001' else 'HAIR WIGS & EXTENSIONS '
            response = json.dumps({'data': result, 'message': message , 'is_success' :True})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [], 'message': 'No products found with specified categories' , 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )


    @http.route('/ctegories/haircolor/products',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_haircolor_products(self,cur=None, idd=None,loc=None, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        product_model = request.env['product.template']
        products = product_model.sudo().with_context(lang=language).search([('id', 'in', [14809,14810,14803,14799,16575,16574,14798,14800,14801,14802,14804,14811]),('is_published' ,'=' , True),('qty_available' ,'!=' , 0)], order='id desc', limit=16)
        result = []
        
        price=0
        check_str=lambda x:x if x else ''
        pricelist={}
        authe = request.httprequest.headers
        valid_token =''
        price_cu=0.0
        pricecurrency={}
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            pass

        if valid_token:
            try:
                dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!' , 'is_success' :False})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        
            location = dec_token['location']
            if location:
                if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                        location = location
                else :
                    location = 'KW'
            else :
                location = 'KW'
            country = request.env['res.country'].search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
        else :
            location = loc
            if location:
                if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                        location = location
                else :
                    location = 'KW'
            else :
                location = 'KW'
            country = request.env['res.country'].search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
        
        for product in products:
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
                
            result.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'image':self.url + '/web/image?' + 'model=product.template&id=' + str(product.id) + '&field=image_1920',
                'price' :  price_cu,
                'new_price': next(iter(price.values()))[0] if price else price_cu,
                'currency' : cur  if pricecurrency else product.cost_currency_id.name ,
                'website_ribbon_id' : [{'id':template.id,'name':check_str(template.html) ,'text_color' : template.text_color , 'class' : template.html_class , 'bg_color' : template.bg_color} for template in product.website_ribbon_id] ,
                'description_sale' : product.description_sale,
                'category' : [{
                                    'id' : item.id,
                                    'name' : item.name
                                }for item in product.public_categ_ids ]
            })
            

        if result:
            message = 'ملونات الشعر' if language == 'ar_001' else 'HAIR COLOR'
            response = json.dumps({'data': result, 'message': message , 'is_success' :True})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [], 'message': 'No products found with specified categories' , 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

    @http.route('/ctegories/bodyskin/products',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_bodyskin_products(self,cur=None, idd=None,loc=None, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        product_model = request.env['product.template']
        products = product_model.sudo().with_context(lang=language).search([('id', 'in', [14862,14885,14793,14792,23702,16338,16337,16336,16335,16334,16333,14776]),('qty_available' ,'!=' , 0),('is_published' ,'=' , True)], order='id desc', limit=16)
        result = []
        price=0
        pricelist={}
        authe = request.httprequest.headers
        check_str=lambda x:x if x else ''
        valid_token =''
        price_cu=0.0
        pricecurrency={}
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            pass

        if valid_token:
            try:
                dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!' , 'is_success' :False})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        
            location = dec_token['location']
            if location:
                if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                        location = location
                else :
                    location = 'KW'
            else :
                location = 'KW'
            country = request.env['res.country'].search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
        else :
            location = loc
            if location:
                if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                        location = location
                else :
                    location = 'KW'
            else :
                location = 'KW'
            country = request.env['res.country'].search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
        for product in products:
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
                
            result.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'website_ribbon_id' : [{'id':template.id,'name':check_str(template.html) ,'text_color' : template.text_color , 'class' : template.html_class , 'bg_color' : template.bg_color} for template in product.website_ribbon_id] ,
                'image':self.url + '/web/image?' + 'model=product.template&id=' + str(product.id) + '&field=image_1920',
                'price' :  price_cu,
                'new_price': next(iter(price.values()))[0] if price else price_cu,
                'currency' : cur  if pricecurrency else product.cost_currency_id.name ,
                'description_sale' : product.description_sale,
                'category' : [{
                                    'id' : item.id,
                                    'name' : item.name
                                }for item in product.public_categ_ids ]
            })

        if result:
            message = 'منتجات الجسم والعناية بالبشرة' if language == 'ar_001' else 'BODY & SKINCARE'
            response = json.dumps({'data': result, 'message': message , 'is_success' :True})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [], 'message': 'No products found with specified categories' , 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    
    @http.route('/ctegories/hairstyle/products',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_hairstyle_products(self,cur=None, idd=None,loc=None, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        product_model = request.env['product.template']
        products = product_model.sudo().with_context(lang=language).search([('id', 'in', [23692,23691,23693,23690,16655,16649,16648,16647,16643,16642,16617,16545,16336,16335,16298,16111]),('qty_available' ,'!=' , 0),('is_published' ,'=' , True)], order='id desc', limit=16)
        result = []
        price=0
        pricelist={}
        authe = request.httprequest.headers
        check_str=lambda x:x if x else ''
        valid_token =''
        price_cu=0.0
        pricecurrency={}
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            pass

        if valid_token:
            try:
                dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!' , 'is_success' :False})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        
            location = dec_token['location']
            if location:
                if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                        location = location
                else :
                    location = 'KW'
            else :
                location = 'KW'
            country = request.env['res.country'].search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
        else :
            location = loc
            if location:
                if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                        location = location
                else :
                    location = 'KW'
            else :
                location = 'KW'
            country = request.env['res.country'].search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
        for product in products:
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
                
            result.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'website_ribbon_id' : [{'id':template.id,'name':check_str(template.html) ,'text_color' : template.text_color , 'class' : template.html_class , 'bg_color' : template.bg_color} for template in product.website_ribbon_id] ,
                'image':self.url + '/web/image?' + 'model=product.template&id=' + str(product.id) + '&field=image_1920',
                'price' :  price_cu,
                'new_price': next(iter(price.values()))[0] if price else price_cu,
                'currency' : cur  if pricecurrency else product.cost_currency_id.name ,
                'description_sale' : product.description_sale,
                'category' : [{
                                    'id' : item.id,
                                    'name' : item.name
                                }for item in product.public_categ_ids ]
            })

        if result:
            message = 'منتجات العناية بالشعر' if language == 'ar_001' else 'HAIR STYLING'
            response = json.dumps({'data': result, 'message': message , 'is_success' :True})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [], 'message': 'No products found with specified categories' , 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

    
    @http.route('/api/pricelist/products', auth='public', methods=['GET'])
    def get_pricelist_products(self, pricelist_id=None):
        # Retrieve the pricelist ID from the request
        # pricelist_id = 1
        response = []
        authe = request.httprequest.headers
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            pass

        if valid_token:
            try:
                dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!' , 'is_success' :False})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            location = dec_token['location']
            if location:
                if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                        location = location
                else :
                    location = 'KW'
            else :
                location = 'KW'
            country = request.env['res.country'].search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
        else :
            location = loc
            if location:
                if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                        location = location
                else :
                    location = 'KW'
            else :
                location = 'KW'
            country = request.env['res.country'].search([('code', '=', location)])
            if country:
                cur = country.currency_id.name
            else:
                location = ''
                cur= ''
        # Retrieve the pricelist and its applied products
        products = pricelist.item_ids
        merged_products = set()
        for i in products:

            if i.applied_on == '2_product_category':
                products_1 = request.env['product.template'].search([('categ_id' , '=' , i.categ_id.id)])
                merged_products.update(products_1)
            if i.applied_on == '1_product':
                products_2 = request.env['product.template'].search([('id' , '=' , i.product_tmpl_id.id)])
                merged_products.update(products_2)
            # if i.applied_on == '1_product':
            #     products_3 = request.env['product.template'].search([('id' , '=' , i.product_templ_id)])
                # merged_products.update(products_3)
            if i.applied_on == '4_product_brand':
                products_4 = request.env['product.template'].search([('brand_id' , '=' , i.brand_ids.id)])
                merged_products.update(products_4)
        # Construct the response

        print('merged_products >> ' , merged_products)
        # price = pricelist.sudo()._compute_price_rule( products = product, qty =1, uom = product.uom_id)
        for product in merged_products:
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

            # price = pricelist.sudo()._compute_price_rule( products = product, qty =1, uom = product.uom_id)
            response.append({'id': product.id, 'name': product.name ,
            'price' :  next(iter(price.values()))[0]})
        # response = {
        #     'pricelist_id': pricelist_id,
        #     'products': [{'id': product.id, 'name': product.name ,'price' :pricelist.sudo()._compute_price_rule( products = product, qty =1, uom = product.uom_id) } for product in merged_products]
        # }
        response = json.dumps({'data': response, 'message': 'Hair color Product' , 'is_success' :True})
        return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
        )


    @http.route('/product/most_frequent', cors="*", auth="public", csrf=False, website=True, methods=['GET'])
    def get_most_frequent_product_template(self):
        SaleOrder = http.request.env['sale.order']
        ProductTemplate = http.request.env['product.template']
        
        # Query the sale order lines and count the occurrences of each product template
        product_template_counts = SaleOrderLine.search_read(
            domain=[],
            fields=['product_template_id', 'product_uom_qty'],
            groupby=['product_template_id'],
            orderby='product_uom_qty desc',
            limit=1
        )
        
        if product_template_counts:
            # Retrieve the product template ID with the highest count
            product_template_id = product_template_counts[0]['product_template_id'][0]
            
            # Retrieve the product template record
            product_template = ProductTemplate.browse(product_template_id)
            
            return {
                'product_template_id': product_template.id,
                'product_template_name': product_template.name,
                'product_template_count': product_template_counts[0]['product_uom_qty']
            }


    # @http.route('/product/most_frequent_website', cors="*", auth="public", csrf=False, website=True, methods=['GET'])
    # def most_frequent_products(self, limit=10):
    #     SaleOrderLine = request.env['sale.order.line']

    #     try:
    #         # Search for sale order lines and group by product
    #         sale_order_lines = SaleOrderLine.sudo().search([]).read(['product_template_id'])

    #         # Count the occurrence of each product ID
    #         print('sale_order_lines >> ' , sale_order_lines)
    #         product_counter = collections.Counter(line['product_template_id'][0] for line in sale_order_lines)
    #         print('product_counter >>> ' , product_counter)
    #         # Get the most frequent product IDs
    #         most_frequent_product_ids = [product_id for product_id, count in product_counter.most_common(limit)]

    #         # Read the details of the most frequent products
    #         most_frequent_products = request.env['product.template'].sudo().search(
    #             [('id', 'in', most_frequent_product_ids)] , limit=10
    #             )
    #         res=[]
    #         response = json.dumps({"data": most_frequent_products, 'message': 'Most frequent products'})
    #         return Response(
    #             response, status=200,
    #             headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
    #         )
    #     except Exception as e:
    #         response = json.dumps({"data": [], 'message': str(e)})
    #         return Response(
    #             response, status=500,
    #             headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
    #         )

