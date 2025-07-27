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



class Search(http.Controller):
    url = 'https://www.alnasaem.com' 

    @http.route('/api/search', auth='public', methods=['GET'], csrf=False)
    def search_products_and_categories(self, search_query,page=None , cur=None):
        # Search for products matching the search query
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        limit = 10
        valid_token = False
        domain=[]
        authe = request.httprequest.headers
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            pass

        if valid_token:
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
                else:
                    location = ''
                    cur= ''
            except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!' , 'is_success' :False})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        try :
            if page == None:
                page = 1
            else:
                page = int(page)
            term_list = search_query.split()
            contains_only_spaces = all(search_query.isspace() or search_query == '' for search_query in term_list)
            space_count = len(term_list)
            
            if space_count == 1:
                # domain = ['|',]
                domain= [('name', 'ilike', search_query)]
                # domain.append(['description_sale', 'ilike', term])
            elif contains_only_spaces :
                response = json.dumps({ 'data': [], 'message': 'Please add keyword'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
            else :
                domain = ['|',]
                for term in term_list:
                    domain.append(('name', 'ilike', term))
            products = request.env['product.template'].sudo().with_context(lang=language).search(domain, order="id asc", limit=limit, offset=(page - 1) * limit)
            product_obj_count = request.env['product.template'].sudo().with_context(lang=language).search_count(domain)
            # Search for categories matching the search query
            categories = request.env['product.public.category'].sudo().search(domain , order="id asc", limit=limit, offset=(page - 1) * limit)
            if len(products):
                        totalpages = math.ceil(product_obj_count / 10)
            else:
                totalpages = 0
            result = {
                'products': [],
                'categories': []
            }

            # Build the response object for products

            for product in products:
                if cur :
                        pricelist = request.env['product.pricelist'].sudo().search(
                    [('currency_id.name', '=', cur)],
                    limit=1
                )
                        if pricelist:
                            pricelist.ensure_one()
                            price = pricelist.sudo()._compute_price_rule(products=product, qty=1, uom=product.uom_id)
                        else:
                            price = 0
                else:
                    pricelist = 0
                    price = 0
                result['products'].append({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'image': self.url + '/web/image?' + 'model=product.template&id=' + str(product.id) + '&field=image_1920',
                    'price' :  product.list_price,
                    'new_price': next(iter(price.values()))[0] if price else product.list_price,
                    'currency': pricelist.currency_id.name if pricelist else product.cost_currency_id.name,
                    'description_sale': product.description_sale,
                    'category': [{
                        'id': item.id,
                        'name': item.name
                    } for item in product.public_categ_ids]
                })

            # Build the response object for categories
            for category in categories:
                sub_cat = request.env['product.public.category'].with_context(lang=language).search_count([('parent_id', '=', category.id)])
                result['categories'].append({
                    'id': category.id,
                    'name': category.name,
                    'image': self.url + '/web/image?' + 'model=product.public.category&id=' + str(category.id) + '&field=image_1920',
                    'sub_categories': True if sub_cat else False
                })
        except Exception as e:
            response = json.dumps({"data": [], 'message': str(e), 'code': 400 , 'is_success' :False})
            return Response(
                response, status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        
        if result:
                message = 'نتائج البحث' if language == 'ar_001' else 'Products for this search'
                response = json.dumps({'data': result, 'message': message ,'total_pages' : totalpages , 'is_success' :True})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )
        else:
            message = 'لا يوجد نتائج' if language == 'ar_001' else 'No products found'
            response = json.dumps({'data': [], 'message': message,'total_pages' : 0 , 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )