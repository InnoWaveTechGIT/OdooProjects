from odoo import http
from odoo.http import request
from odoo.http import Response
from datetime import datetime
import json
from math import ceil
from odoo.addons.mazaady_doworks.controllers.login import validate_token
from odoo.exceptions import AccessError, ValidationError, UserError, MissingError
from . base_controller import BaseController

class WalletController(BaseController):
    def get_user_id(self):
        auth_header = request.httprequest.headers.get('Authorization')
        token = auth_header.split(" ")[1]
        valid_api_key = request.env["res.users.apikeys"]._check_credentials(scope='api', key=token)
        api_key_user = request.env["res.users"].sudo().browse(int(valid_api_key))
        return api_key_user       

    @validate_token
    @BaseController.route('/api/products/post-product', type='json', auth='none', methods=['POST'], csrf=False)
    def post_productmazady(self, **kwargs):
        mazaady_product_id = kwargs.get('mazaady_product_id')
        mazaady_item_desc = kwargs.get('mazaady_item_desc')
        mazaady_sub_cat = int(kwargs.get('mazaady_sub_cat'))
        mazaady_item_price = kwargs.get('mazaady_item_price')
        company_id = int(kwargs.get('company_id'))
        seller_id = int(kwargs.get('seller_id'))

        if not seller_id or not mazaady_product_id or not mazaady_item_desc or not mazaady_sub_cat or not mazaady_item_price or not company_id:
            error_message = f"seller_id, mazaady_product_id, mazaady_item_desc, mazaady_sub_cat, mazaady_item_price, and company_id are required."
            raise KeyError(error_message)        

        seller = request.env['res.partner'].sudo().search([('subID', '=', seller_id), ('company_id', '!=', False), ('company_id', '=', company_id)], limit=1)
        if not seller:
            error_message = f"seller_id not found."
            raise MissingError(error_message)             

        product = request.env['product.template'].with_user(self.get_user_id()).with_context(mail_create_nosubscribe=False).with_company(company_id).sudo().create({
                                    'name': mazaady_item_desc,
                                    'list_price': float(mazaady_item_price),
                                    'categ_id': int(mazaady_sub_cat),
                                    'seller_id': seller.id,
                                    'mazaady_product_id': mazaady_product_id,
                                    'company_id': company_id
                                })
        return  {
                'status': 200, 
                'message': 'New Product created successfully.', 
                'mazaady_product_id': mazaady_product_id,
                'odoo_product_id': product.id,
            }

    @validate_token
    @BaseController.route('/api/products/update-product', type='json', auth='none', methods=['POST'], csrf=False)
    def UpdateProduct_mazady(self, **kwargs):
        mazaady_product_id = kwargs.get('mazaady_product_id')
        mazaady_item_desc = kwargs.get('mazaady_item_desc')
        mazaady_sub_cat = int(kwargs.get('mazaady_sub_cat'))
        mazaady_item_price = kwargs.get('mazaady_item_price')
        company_id = int(kwargs.get('company_id'))
        seller_id = int(kwargs.get('seller_id'))
        
        if not mazaady_product_id or not company_id:
            error_message = f"mazaady_product_id and company_id are required ."
            raise KeyError(error_message)

        if seller_id:
            seller = request.env['res.partner'].sudo().search([('subID', '=', seller_id), ('company_id', '!=', False), ('company_id', '=', company_id)], limit=1)
            if not seller:
                error_message = f"seller_id not found."
                raise MissingError(error_message)
        
        product = request.env['product.template'].sudo().search([('mazaady_product_id', '=', mazaady_product_id), ('company_id', '!=', False), ('company_id', '=', company_id)], limit=1)
        if not product:
            error_message = f"Product not found."
            raise MissingError(error_message)
        else:
            product.with_user(self.get_user_id()).sudo().write({
                                                                'name': mazaady_item_desc if mazaady_item_desc else product.name,
                                                                'list_price': mazaady_item_price if mazaady_item_price else product.list_price,
                                                                'categ_id' : mazaady_sub_cat if mazaady_sub_cat else product.categ_id.id,
                                                                'seller_id' : seller.id if seller_id else product.seller_id.id
                                                                })
            return {'status': 200,
                    'message': 'Product data updated successfully.',
                    'mazaady_product_id': mazaady_product_id,
                    'odoo_product_id': product.id,
                    }

    @validate_token
    @http.route('/api/products/delete-product' ,csrf=False, type='http', auth='public' , methods=['Delete'])
    def delete_product(self, **kwargs):
        mazaady_product_id = kwargs.get('mazaady_product_id')
        company_id = kwargs.get('company_id')
        if company_id:
            company_id = int(company_id)
        if not mazaady_product_id or not company_id:
            return Response(
                json.dumps({'status': 422, 'message': 'product_id and company_id are required.'}),
                status=422,
                content_type='application/json'
            )     
            
        product = request.env['product.template'].sudo().search([('mazaady_product_id', '=', int(mazaady_product_id)), ('company_id', '!=', False), ('company_id', '=', int(company_id))], limit=1)
        if product:
            product.sudo().write({'active': False})
            
            response= json.dumps({'message': 'mazaady_product_id archived successfully'})
            return Response(
                            response, status=200,
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                            )
        else:
            response= json.dumps({'error': 'mazaady_product_id not found'})
            return Response(
                            response, status=404,
                            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                            )
