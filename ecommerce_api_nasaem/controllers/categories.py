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

class Categories(http.Controller):
    url = 'https://www.alnasaem.com' 
    print('as')
    @http.route('/ctegories/brands',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_brands(self, idd=None, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        category_model = request.env['product.public.category']
        brands = category_model.with_context(lang=language).search([('x_studio_is_brand', '=', True)])
        result = []
        try:
            # Process the brands as needed
            for brand in brands:
                sub_cat =  category_model.search_count([('parent_id', '=', brand.id)])
                result.append(
                            {
                                'id':brand.id,
                                'name':brand.name,
                                'image':self.url + '/web/image?' + 'model=product.public.category&id=' + str(brand.id) + '&field=image_1920',
                                'sub_categories' : True if sub_cat else False
                                })
            if result:
                message = 'جميع الماركات' if language == 'ar_001' else 'All Brands'
                response = json.dumps({'data':result,'message': message , 'is_success' :True})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
            else :
                response = json.dumps({'data':[],'message': 'No Brands Now' , 'is_success' :False})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        except Exception as e:
                response = json.dumps({'data':[],'message':str(e) , 'is_success' :False}) 
                return Response(
                    response, status=500,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])


    @http.route('/ctegories/brands/sub_categories',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_brands_sub_categories(self, id=None, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        category_model = request.env['product.public.category']
        brands = category_model.with_context(lang=language).search([('parent_id', '=', int(id))])
        result = []
        # Process the brands as needed
        for brand in brands:
            sub_cat =  category_model.search_count([('parent_id', '=', brand.id)])
            result.append(
                        {
                            'id':brand.id,
                            'name':brand.name,
                            'image':self.url + '/web/image?' + 'model=product.public.category&id=' + str(brand.id) + '&field=image_1920',
                            'sub_categories' : True if sub_cat else False
                            })
        if result:
            message = 'جميع الماركات' if language == 'ar_001' else 'All Brands'
            response = json.dumps({'data':result,'message': message , 'is_success' :True})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        else :
            response = json.dumps({'data':[],'message': 'No Brands Now' , 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])

    
    @http.route('/ctegories/shop/all',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_shop_by_categories(self, idd=None, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        category_model = request.env['product.public.category']
        brands = category_model.with_context(lang=language).search([('x_studio_is_brand', '=', False), ('visible_website', '=', True)])
        result = []
        # Process the brands as needed
        for brand in brands:
            sub_cat =  category_model.search_count([('parent_id', '=', brand.id)])
            result.append(
                        {
                            'id':brand.id,
                            'name':brand.name,
                            'image':self.url + '/web/image?' + 'model=product.public.category&id=' + str(brand.id) + '&field=image_1920',
                            'sub_categories' : True if sub_cat else False
                            })
        if result:
            message = 'جميع الماركات' if language == 'ar_001' else 'All Brands'
            response = json.dumps({'data':result,'message': message, 'is_success' :True})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        else :
            response = json.dumps({'data':[],'message': 'No Brands Now' , 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
    
    @http.route('/ctegories/all',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_all_categories(self, idd=None, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        category_model = request.env['product.public.category']
        brands = category_model.with_context(lang=language).search([('x_studio_is_brand', '=', False)])
        result = []
        # Process the brands as needed
        for brand in brands:
            sub_cat =  category_model.search_count([('parent_id', '=', brand.id)])
            result.append(
                        {
                            'id':brand.id,
                            'name':brand.name,
                            'image':self.url + '/web/image?' + 'model=product.public.category&id=' + str(brand.id) + '&field=image_1920',
                            'sub_categories' : True if sub_cat else False
                            })
        if result:
            message = 'كل الفئات ' if language == 'ar_001' else 'All Categories'
            response = json.dumps({'data':result,'message': message , 'is_success' :True})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        else :
            response = json.dumps({'data':[],'message': 'No Categories Now' , 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])

    @http.route('/ctegories/all/sub_categories',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_all_sub_categories(self, id=None, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        category_model = request.env['product.public.category']
        brands = category_model.with_context(lang=language).search([('parent_id', '=', int(id))])
        result = []
        # Process the brands as needed
        for brand in brands:
            sub_cat =  category_model.search_count([('parent_id', '=', brand.id)])
            result.append(
                        {
                            'id':brand.id,
                            'name':brand.name,
                            'image':self.url + '/web/image?' + 'model=product.public.category&id=' + str(brand.id) + '&field=image_1920',
                            'sub_categories' : True if sub_cat else False
                            })
        if result:
            message = 'كل الماركات' if language == 'ar_001' else 'All Brands'
            response = json.dumps({'data':result,'message': 'All Brands', 'is_success' :True})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
        else :
            response = json.dumps({'data':[],'message': 'No Categories Now' , 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])


