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



class Product(http.Controller):
    
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
    @http.route('/search',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_search(self,page=None,term=None ):
        response = ''
        valid_token = False
        authe = request.httprequest.headers
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        if authe:
                if 'Authorization' in authe:
                    token = authe['Authorization'].replace('Bearer ', '')
                    valid_token = models.execute_kw(self.db, uid, self.password, 'x_user_token', 'search_read', [[['x_studio_user_token' , '=' , token]]],{'fields':['x_studio_user_name']})
                else :
                    pass
        if term == None :
            response = json.dumps({ 'data': [], 'message': 'Please add keyword'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        limit = 10
        if page == None:
            page = 1
        else:
            page = int(page)
        if uid:

            # Search products by text
            
            term_list = term.split()
            contains_only_spaces = all(term.isspace() or term == '' for term in term_list)
            space_count = len(term_list)
            
            if space_count == 1:
                # domain = ['|',]
                domain= [['name', 'ilike', term]]
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
                    domain.append(['name', 'ilike', term])
                
            product_ids = models.execute_kw(self.db, uid, self.password, 'product.template', 'search_read', [domain],{'fields':['id','name','type','uom_name', 'cost_currency_id','categ_id','list_price','description_sale' ,'x_studio_specifications' ,'x_studio_why_and_when' ,'x_studio_product_feature_mobile','tax_string'] , 'limit':limit, 'offset':(page - 1) * limit})
            product_obj_count = models.execute_kw(self.db, uid, self.password, 'product.template', 'search_count', [domain])

            # cat_id = models.execute_kw(self.db, uid, self.password, 'product.public.category', 'search_read', [[['name', 'ilike', term]for term in term_list]],{'fields':['id','name' ] , 'limit':limit, 'offset':(page - 1) * limit})
            # for i in cat_id:
            #     category_id = i['id']
            #     image_url = self.url + '/web/image?' + 'model=product.public.category&id=' + str(category_id) + '&field=image_1920'
            #     i['image'] = image_url
            if len(product_ids):
                totalpages = math.ceil(product_obj_count / len(product_ids))
            else:
                totalpages = 0
            x = 0
            for product in product_ids:
                product_id = product['id']
                image_url = self.url + '/web/image?' + 'model=product.template&id=' + str(product_id) + '&field=image_1920'
                product['image'] = image_url
                categ_id = product['categ_id'][0]
                categ_name = product['categ_id'][1]
                product_ids[x]['categ_name'] = categ_name
                product_ids[x]['categ_id'] = categ_id
                if product_ids[x]['tax_string']:
                    product_ids[x]['list_price'] = self.extract_float_value(product_ids[x]['tax_string'])
                product_ids[x]['list_price'] = product_ids[x]['list_price'] if valid_token else None
                x+= 1 
            try:
                response = json.dumps({"data":{'product':product_ids},'total_pages' : totalpages,'message': 'All product'})
                return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

            except:
                response = json.dumps({"data":[],'message': 'No products for this Term'})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
            )
                    
    



    @http.route('/categories/all', auth="public", cors="*", csrf=False, website=True, methods=['GET'])
    def get_all_categories(self, page=int(1), limit=None):
        response = ''
        page = int(page)

        if page is None:
            page = int(1)
        else:
            pass
        if limit is None:
            limit = 10
        else:
            limit = int(limit)

        authe = request.httprequest.headers
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})

        category_ids = models.execute_kw(self.db, uid, self.password, 'product.public.category', 'search_read',[[['parent_id', '=', False]]],{'fields': ['id', 'name', 'sequence','x_studio_brand']})
        for i in category_ids:
            category_id = i['id']
            image_url = self.url + '/web/image?' + 'model=product.public.category&id=' + str(category_id) + '&field=image_1920'
            i['image'] = image_url
            sub_category_ids = models.execute_kw(
                self.db, uid, self.password, 'product.public.category', 'search',
                [[['parent_id', '=', category_id]]]
            )
            
            if sub_category_ids:
                i['sub_category'] = True
            else:
                i['sub_category'] = False

        try:
            response = json.dumps({"data": {'categories': category_ids}, 'message': 'All Categories'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
            )

        except:
            response = json.dumps({"data": [], 'message': 'No Categories now'})
            return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
            )


    @http.route('/categories/subcategories/<int:parent_id>', auth="public", csrf=False, website=True, methods=['GET'])
    def get_all_subcategories(self, parent_id):
        response = ''
        
        authe = request.httprequest.headers
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        
        category_ids = models.execute_kw(
            self.db, uid, self.password, 'product.public.category', 'search_read',
            [[['parent_id', '=', parent_id]]], {'fields': ['id', 'name', 'sequence','x_studio_brand']}
        )
        
        for category in category_ids:
            category_id = category['id']
            image_url = self.url + '/web/image?' + 'model=product.public.category&id=' + str(category_id) + '&field=image_1920'
            category['image'] = image_url
            
            sub_category_ids = models.execute_kw(
                self.db, uid, self.password, 'product.public.category', 'search',
                [[['parent_id', '=', category_id]]]
            )
            
            if sub_category_ids:
                category['sub_category'] = True
            else:
                category['sub_category'] = False
        
        try:
            response = json.dumps({"data": {'categories': category_ids}, 'message': 'All Categories'})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
            )
        except:
            response = json.dumps({"data": [], 'message': 'No Categories now'})
            return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
            )
    
    @http.route('/category/product/<int:category_id>',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_product_by_category_id(self,category_id, page= int(1), **kw):
        response = ''

        page = int(page)

        if page == None:
            page = int(1)
        else:
            pass
        valid_token = False
        authe = request.httprequest.headers
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        try:
            
            if authe:
                if 'Authorization' in authe:
                    token = authe['Authorization'].replace('Bearer ', '')
                    valid_token = models.execute_kw(self.db, uid, self.password, 'x_user_token', 'search_read', [[['x_studio_user_token' , '=' , token]]],{'fields':['x_studio_user_name']})
                else :
                    pass
        except Exception as e:
            response = json.dumps({ 'data': 'no data', 'message': str(e)})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

       
        if valid_token:
            products = models.execute_kw(self.db, uid, self.password, 'product.template', 'search_read', [[['public_categ_ids' , '=' , category_id]]],{'fields':['id','name','type','uom_name', 'cost_currency_id','categ_id','list_price','description_sale','x_studio_specifications' ,'x_studio_why_and_when','x_studio_product_feature_mobile','tax_string']})
            user_id =int(valid_token[0]['x_studio_user_name'][0])

            user_partner = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['id' , '=' , user_id]]],{'fields':['partner_id','property_product_pricelist']})
            user_product_pricelist_id =user_partner[0]['property_product_pricelist'][0] 
            user_partner = user_partner[0]['partner_id'][0]
            
            
            
            product_price_list = models.execute_kw(self.db, uid, self.password, 'product.pricelist.item', 'search_read', [[['pricelist_id' , '=' , user_product_pricelist_id]]],{'fields':['product_id','fixed_price']})
            for product in products:
                for prod in product_price_list:
                    if product['product_id'][0] == prod['product_id'][0] :
                        product['list_price'] = prod['fixed_price']
        else:
            products = models.execute_kw(self.db, uid, self.password, 'product.template', 'search_read', [[['public_categ_ids' , '=' , category_id]]],{'fields':['id','name','type','uom_name', 'cost_currency_id','list_price','categ_id','description_sale','x_studio_product_feature_mobile','tax_string']})
        x = 0
        for i in products:
            
            product_id = i['id']
            image_url = self.url + '/web/image?' + 'model=product.template&id=' + str(product_id) + '&field=image_1920'
            i['image'] = image_url
            categ_id = i['categ_id'][0]
            categ_name = i['categ_id'][1]
            products[x]['categ_name'] = categ_name
            products[x]['categ_id'] = categ_id
            # if products[x]['tax_string']:
            #     products[x]['list_price'] = self.extract_float_value(products[x]['tax_string'])
            products[x]['list_price'] = products[x]['list_price'] if valid_token else None
            
            x += 1
        try:
            response = json.dumps({"data":{'product':products},'message': 'All product'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'No products for this ID'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )



    @http.route('/featured/product',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_product_by_featured_id(self, page= int(1), **kw):
        response = ''

        page = int(page)

        if page == None:
            page = int(1)
        else:
            pass
        valid_token = False
        authe = request.httprequest.headers
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        try:
            
            if authe:
                if 'Authorization' in authe:
                    token = authe['Authorization'].replace('Bearer ', '')
                    valid_token = models.execute_kw(self.db, uid, self.password, 'x_user_token', 'search_read', [[['x_studio_user_token' , '=' , token]]],{'fields':['x_studio_user_name']})
                else :
                    pass
        except Exception as e:
            response = json.dumps({ 'data': 'no data', 'message': str(e)})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )

        crm_tag = models.execute_kw(self.db, uid, self.password, 'product.tag', 'search_read', [[['name' , '=' , 'featured']]],{'fields':['id','name']})
        if crm_tag:
            id = crm_tag[0]['id']
            if valid_token:
                
                products = models.execute_kw(self.db, uid, self.password, 'product.template', 'search_read', [[['product_tag_ids' , '=' , id]]],{'fields':['id','name','type','uom_name', 'cost_currency_id','categ_id','list_price','description_sale','x_studio_specifications' ,'x_studio_why_and_when','x_studio_product_feature_mobile','tax_string']})
                user_id =int(valid_token[0]['x_studio_user_name'][0])

                user_partner = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['id' , '=' , user_id]]],{'fields':['partner_id','property_product_pricelist']})
                user_product_pricelist_id =user_partner[0]['property_product_pricelist'][0] 
                user_partner = user_partner[0]['partner_id'][0]
                
                
                
                product_price_list = models.execute_kw(self.db, uid, self.password, 'product.pricelist.item', 'search_read', [[['pricelist_id' , '=' , user_product_pricelist_id]]],{'fields':['product_id','fixed_price']})
                for product in products:
                    for prod in product_price_list:
                        if product['product_id'][0] == prod['product_id'][0] :
                            product['list_price'] = prod['fixed_price']
            else:
                products = models.execute_kw(self.db, uid, self.password, 'product.template', 'search_read', [[['product_tag_ids' , '=' , id]]],{'fields':['id','name','type','uom_name', 'cost_currency_id','categ_id','list_price','description_sale','x_studio_specifications' ,'x_studio_why_and_when','x_studio_product_feature_mobile','tax_string']})
            x = 0
            for i in products:
                
                product_id = i['id']
                image_url = self.url + '/web/image?' + 'model=product.template&id=' + str(product_id) + '&field=image_1920'
                i['image'] = image_url
                categ_id = i['categ_id'][0]
                categ_name = i['categ_id'][1]
                products[x]['categ_name'] = categ_name
                products[x]['categ_id'] = categ_id
                # if products[x]['tax_string']:
                #     products[x]['list_price'] = self.extract_float_value(products[x]['tax_string'])
            # products[x]['list_price'] = products[x]['list_price'] if valid_token else None
                products[x]['list_price'] = products[x]['list_price'] if valid_token else None
                x += 1
        else :
            response = json.dumps({"data":[],'message': 'No featured products '})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )
        try:
            response = json.dumps({"data":{'product':products},'message': 'All product'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'No products for this ID'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )


    @http.route('/product/<int:product_id>', auth="public", csrf=False, website=True, methods=['GET'])
    def get_product_by_id(self, product_id, page=int(1), **kw):
        response = ''
        print('product_id >>> ' , product_id)
        valid_token = False
        page = int(page)

        if page is None:
            page = int(1)

        authe = request.httprequest.headers
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})

        try:
            if authe and 'Authorization' in authe:
                token = authe['Authorization'].replace('Bearer ', '')
                valid_token = models.execute_kw(
                    self.db, uid, self.password, 'x_user_token', 'search_read', 
                    [[['x_studio_user_token', '=', token]]], {'fields': ['x_studio_user_name']}
                )
            else:
                    valid_token = False
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': str(e)})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        if valid_token:
            products = models.execute_kw(
                self.db, uid, self.password, 'product.product', 'search_read',
                [[['product_tmpl_id', '=', product_id]]],
                {'fields': ['id', 'name', 'type', 'uom_name', 'cost_currency_id', 'categ_id', 'list_price','description_sale','accessory_product_ids','x_studio_specifications' ,'x_studio_video' ,'x_studio_why_and_when', 'product_template_image_ids','x_studio_product_feature_mobile','tax_string' , 'x_studio_pdf_link' , 'x_studio_breif' , 'x_studio_why_and_when' , 'x_studio_specifications','product_variant_ids'], 'limit': 1}
            )
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
                {'fields': ['product_tmpl_id', 'fixed_price']}
            )

            for product in products:
                for prod in product_price_list:
                    print('prod >>> ' , prod)
                    if product['id'] == prod['product_tmpl_id'][0]:
                        product['list_price'] = prod['fixed_price']
        else:
            products = models.execute_kw(
                self.db, uid, self.password, 'product.product', 'search_read',
                [[['product_tmpl_id', '=', product_id]]],
                {'fields': ['id', 'name', 'type', 'uom_name', 'cost_currency_id', 'categ_id','description_sale','accessory_product_ids','x_studio_specifications' ,'x_studio_why_and_when', 'x_studio_video' ,'product_template_image_ids','x_studio_product_feature_mobile','tax_string' , 'x_studio_pdf_link' , 'x_studio_breif' , 'x_studio_why_and_when' , 'x_studio_specifications' , 'product_variant_ids'],'limit': 1}
            )

        x = 0
        im = []
        values= []
        varient = []
        alternative = []
        for i in products:
            product_id = i['id']
            print('products >>> ' , products)
            print("i['accessory_product_ids']  >>> " , i['accessory_product_ids'])
            for alternative_ids in i['accessory_product_ids']:
                print('alternative_ids >>>>>> ' , alternative_ids)
                alternative_product = models.execute_kw(
                self.db, uid, self.password, 'product.product', 'search_read',
                [[['id', '=', int(alternative_ids)]]],
                {'fields': ['id','product_tmpl_id' , 'name', 'type', 'uom_name', 'cost_currency_id', 'categ_id','description_sale','x_studio_specifications' ,'x_studio_why_and_when', 'product_template_image_ids','x_studio_product_feature_mobile','tax_string' , 'x_studio_pdf_link' , 'x_studio_breif' , 'x_studio_why_and_when' , 'x_studio_specifications' , 'attribute_line_ids'], 'offset': (page - 1) * 5,
                'limit': 5}
            )
                if alternative_product:
                    for j in alternative_product:
                        id = 0
                        id = j['product_tmpl_id'][0]
                        j['id'] = id
                        del j['product_tmpl_id']
                        image_url1 = self.url + '/web/image?' + 'model=product.template&id=' + str(id) + '&field=image_1920'
                        j['image'] = image_url1
                    alternative.append(alternative_product[0])
            for variant in i['product_variant_ids']:
                values= []
                print('variant >>>> ' , variant)
                # xs = models.execute_kw(
                # self.db, uid, self.password, 'product.product', 'search_read',
                # [[['id', '=', variant]]],
                # {'fields': ['id', 'product_variant_ids', 'name']})
                # print("xs[0]['product_variant_ids'] >>> " , xs[0]['product_variant_ids'])
                x2 = models.execute_kw(
                self.db, uid, self.password, 'product.product', 'search_read',
                [[['id', '=', variant]]],
                {'fields': ['id', 'name' ,'lst_price', 'valid_product_template_attribute_line_ids' , 'attribute_line_ids' ,'product_template_variant_value_ids' ]})
                print('asd >>>>> ' ,x2)
                x3 = models.execute_kw(
                self.db, uid, self.password, 'product.template.attribute.value', 'search_read',
                [[['id', 'in', x2[0]['product_template_variant_value_ids']]]],
                {'fields': ['id', 'name' , 'attribute_id' , 'attribute_line_id' , 'display_name' , 'product_attribute_value_id' , ]})
                if x2 and x3 : 
                    varient.append({
                            'id' : x2[0]['id'],
                            'key' : x3[0]['attribute_id'][1],
                            'values' : x3[0]['name'],
                            'price' : x2[0]['lst_price'],
                        })

                print('asd >>>>> ' ,x2)
                print('asd >>>>> ' ,x3)
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
            image_url = self.url + '/web/image?' + 'model=product.product&id=' + str(product_id) + '&field=image_1920'
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
            products[x]['varient']  =varient
            products[x]['alternative']  =alternative
            products[x]['list_price'] = products[x]['list_price'] if valid_token else None
            im = []
            x += 1

        try:
            response = json.dumps({"data": {'product': products[0]}, 'message': 'Product Details '})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
            )

        except:
            response = json.dumps({"data": [], 'message': 'No products for this ID'})
            return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
            )


    @http.route('/shipping/all',  auth="public",csrf=False, website=True, methods=['GET'])
    def get_all_shipping_methods(self, **kw):
        response = ''

        
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = common.authenticate(self.db,self.username, self.password, {})
        
        shipping_id = models.execute_kw(self.db, uid, self.password, 'delivery.carrier', 'search_read', [[['id' , '!=' , 1]]],{'fields':['id','name','delivery_type','fixed_price', 'free_over','amount']})
        
    
        
        try:
            response = json.dumps({"data":{'shipping_methods':shipping_id},'message': 'All shipping methods'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'No shipping methods now'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

    
    @http.route('/shipping/<int:shipping_id>',  auth="public",csrf=False, website=True, methods=['POST'])
    def add_shipping_to_cart(self,shipping_id, **kw):
        response = ''
        body =json.loads(request.httprequest.data)
        term = body['term']
        authe = request.httprequest.headers
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url), allow_none=True)
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url), allow_none=True)
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
            shipping_id = models.execute_kw(self.db, uid, self.password, 'delivery.carrier', 'search_read', [[['id' , '=' , shipping_id]]],{'fields':['id','name','delivery_type','fixed_price', 'free_over','amount','product_id']})
            user_id =int(valid_token[0]['x_studio_user_name'][0])
            print('shipping_id >>>> ' , shipping_id)
            user_partner = models.execute_kw(self.db, uid, self.password, 'res.users', 'search_read', [[['id' , '=' , user_id]]],{'fields':['partner_id','property_product_pricelist']})
            user_product_pricelist_id =user_partner[0]['property_product_pricelist'][0] 
            user_partner = user_partner[0]['partner_id'][0]
            
            user_quot = models.execute_kw(self.db, uid, self.password, 'sale.order', 'search_read', [['&',['state' ,'=' ,'draft'],['partner_id' , '=' , user_partner]]],{'fields':['id']})
            if user_quot:
                
                
                try:
                    product_ship_id =  models.execute_kw(self.db, uid, self.password, 'product.product', 'search_read', [[['id' , '=' , shipping_id[0]['product_id'][0]]]],{'fields':['list_price']})
                    print('product_ship_id' , product_ship_id)
                    product_ship_temp_id =  models.execute_kw(self.db, uid, self.password, 'product.product', 'search_read', [[['id' , '=' , int(product_ship_id[0]['id'])]]],{'fields':['list_price']})
                    print('product_ship_id' , product_ship_id)
                    cart_line_id= models.execute_kw(self.db, uid, self.password, 'sale.order.line', 'create', [{'product_id' :shipping_id[0]['product_id'][0],'order_id': user_quot[0]['id'] ,'name':shipping_id[0]['name'],'customer_lead': 2.0,'salesman_id': '1','price_unit' :product_ship_temp_id[0]['list_price'],'product_uom_qty' : 1.0,'product_uom':'1'}])
                except Exception as e: 
                    response=json.dumps({"data":[],"message":str(e)})
                    return Response(
                    response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )
                try:
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
                except Exception as e: 
                    response=json.dumps({"data":[],"message":str(e)})
                    return Response(
                    response, status=403,
                    headers=[('Content-Type', 'application/json'), ('Accept', 'application/json')]
                )

            else:
                response = json.dumps({"data":[],'message': "You don't have cart to add shipping method"})
                return Response(
                response, status=404,
                headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )
        else:
            response = json.dumps({"data":[],'message': 'Invalid Token'})
            return Response(
            response, status=403,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )
        try:
            response = json.dumps({"data":{'shipping_methods':shipping_id},'message': 'All shipping methods'})
            return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

        except:
            response = json.dumps({"data":[],'message': 'No shipping methods now'})
            return Response(
            response, status=404,
            headers=[('Content-Type', 'application/json'),('accept','application/json'), ('Content-Length', 100)]
        )

    