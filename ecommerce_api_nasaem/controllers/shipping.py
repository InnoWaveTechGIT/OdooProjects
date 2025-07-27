from odoo import http
from odoo.http import request ,Response
import json
import jwt
class ShippingController(http.Controller):

    @http.route('/shipping/all', auth="public", csrf=False, website=True, methods=['GET'])
    def get_all_shipping_methods(self, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        try:
            shipping_methods = request.env['delivery.carrier'].sudo().with_context(lang=language).search_read(
                [['id', '!=', 0]],
                fields=['id', 'name', 'delivery_type', 'fixed_price', 'free_over', 'amount']
            )
            message = 'طرق الشحن' if language == 'ar_001' else  'All shipping methods' 
            response = json.dumps({"data": {'shipping_methods': shipping_methods}, 'message':message, 'is_success' :True})
            return Response(
                response,
                status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', str(len(response)))]
            )
        except:
            message = ' ' if language == 'ar_001' else  'No shipping methods available'
            response = json.dumps({"data": [], 'message': message , 'is_success' :False})
            return Response(
                response,
                status=404,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', str(len(response)))]
            )


    @http.route('/shipping/apply', auth='public', csrf=False, methods=['POST'])
    def apply_shipping_method(self, **post):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        website_id = 2  # Specify the desired website ID
        shipping_method_id = post.get('shipping_method_id')
        authe = request.httprequest.headers
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].sudo().search_read(
                [['token', '=', token]]
            )
        except Exception as e:
            response = json.dumps({ 'data': 'no data', 'message': str(e) , 'is_success' :False})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
        # Authenticate the user based on the provided token
        if valid_token:
            try:
                dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            except Exception as e:
                response = json.dumps({ 'jsonrpc': '2.0', 'message': str(e) , 'is_success' :False})
                return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )

        user_id = valid_token[0]['user_id']
        user_partner = request.env['res.users'].sudo().search_read(
                [['id', '=', user_id]]
            )
        user_partner = user_partner[0]['partner_id']
        sale_order = request.env['sale.order'].sudo().search([
            ('partner_id', '=', user_partner[0]),
            ('state', 'in', ['draft', 'sent']), 
            ('website_id' , '=' ,website_id)], limit=1)
            

        # Apply the shipping method to the customer's cart (quotation)
        
        if not sale_order:
            message = 'لا يوجد عربة للمستخدم' if language == 'ar_001' else  'No cart found for the customer'
            response = json.dumps({'message': message, 'code': 404 , 'is_success' :False})
            return Response(
                response,
                status=404,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

        # Update the shipping method on the quotation
        delivery_carrier = request.env['delivery.carrier'].sudo().search([('id', '=', int(shipping_method_id))], limit=1)
        delivery_wizard = request.env['choose.delivery.carrier'].sudo().create({
            'order_id': sale_order.id,
            'carrier_id': delivery_carrier.id
        })
        choose_delivery_carrier = delivery_wizard
        choose_delivery_carrier._get_shipment_rate()
        choose_delivery_carrier.sudo().button_confirm()
        sale_order.amount_delivery = choose_delivery_carrier.display_price

        # Create a sale order line for the shipping cost
        shipping_product = delivery_carrier.product_id

        

        message = 'تم تطبيق العملية بنجاح' if language == 'ar_001' else  'Shipping method applied successfully'
        response = json.dumps({'message': message, 'code': 200 , 'is_success' :True})
        return Response(
            response,
            status=200,
            headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
        )


    @http.route('/shipping/billing_addresses', auth="public", csrf=False, website=True, methods=['GET'])
    def get_billing_addresses(self, parent_id=None, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        try:
            token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
            user_token = request.env['user.token.nasaem'].sudo().search([('token', '=', token)])
            if not user_token:
                response = json.dumps({'message': 'Unauthorized!', 'code': 401 , 'is_success' :False})
                return Response(
                    response,
                    status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )

            user_id = int(user_token.user_id)
            user_records = request.env['res.users'].sudo().search(
                [['id', '=', user_id]]
            )
            partner_id = user_records.partner_id
            partner_records = request.env['res.partner'].sudo().search(
                [['id', '=', partner_id.id]]
                
            )
  
            
            partner_records = partner_records.read(fields=['id', 'name', 'email', 'phone', 'country_id', 'zip', 'street', 'street2', 'city' , 'state_id' ,'x_studio_apartment' ,'x_studio_area' ,'x_studio_block' ,'x_studio_block2' ,'x_studio_building_no' ,'x_studio_floor' ,'is_valid'])
            

            
            response = json.dumps({'data': {'billing_addresses': partner_records} , 'is_success' :True})
            return Response(
                response,
                status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        except Exception as e:
            response = json.dumps({'message': str(e), 'code': 500 , 'is_success' :False})
            return Response(
                response,
                status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    
    @http.route('/shipping/billing_address', auth="public", csrf=False, website=True, methods=['PUT'])
    def update_billing_address(self, **post):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        try:
            token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
            user_token = request.env['user.token.nasaem'].sudo().search([('token', '=', token)])
            if not user_token:
                response = json.dumps({'message': 'Unauthorized!', 'code': 401 , 'is_success' :False})
                return Response(
                    response,
                    status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )

            user_id = int(user_token.user_id)
            user_records = request.env['res.users'].sudo().search(
                [['id', '=', user_id]]
            )
            partner_id = user_records.partner_id.id
            partner = request.env['res.partner'].sudo().browse(partner_id)

            partner_data = {
                'name': post.get('name'),
                'email': post.get('email'),
                'phone': post.get('phone'),
                'street': post.get('street'),
                'city': post.get('city'),
                'country_id': int(post.get('country_id')),
                'zip': post.get('zip'),
                'state_id' : int(post.get('state_id')),
                'x_studio_apartment' : post.get('x_studio_apartment'),
                'x_studio_area' : post.get('x_studio_area'),
                'x_studio_block' : post.get('x_studio_block'),
                'x_studio_block2' : post.get('x_studio_block2'),
                'x_studio_building_no' : post.get('x_studio_building_no'),
                'x_studio_floor' : post.get('x_studio_floor'),
            }
            partner_data = {k: v for k, v in partner_data.items() if v is not None}
            partner.write(partner_data)
            partner.write({
                'is_valid' : True
            })
            message = 'تم تحديث العنوان ' if language == 'ar_001' else  'Billing address updated successfully'
            response = json.dumps({'message': message, 'code': 200 , 'is_success' :True})
            return Response(
                response,
                status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        except Exception as e:
            response = json.dumps({'message': 'Internal Server Error', 'code': 500 , 'is_success' :False})
            return Response(
                response,
                status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
    @http.route('/shipping/shipping_addresses', auth="public", csrf=False, website=True, methods=['GET'])
    def get_shipping_addresses(self, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
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
        else:
            response = json.dumps({ 'data': [], 'message': 'Unauthorized!' , 'is_success' : False})
            return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
        # Authenticate the user based on the provided token
        try:
                user_id = int(valid_token[0]['user_id'])
            
                partner = request.env['res.users'].sudo().browse(user_id)
                partner_records = request.env['res.partner'].sudo().search([ '|' ,('id' , '=' , int(partner.partner_id.id)) , ('parent_id' ,'=' , int(partner.partner_id.id))])
                response = json.dumps({'data': {'shipping_addresses': partner_records.read(fields=['id', 'name', 'email', 'phone', 'country_id', 'zip', 'street', 'street2', 'city' , 'state_id' ,'x_studio_apartment' ,'x_studio_area' ,'x_studio_block' ,'x_studio_block2' ,'x_studio_building_no' ,'x_studio_floor' ,'is_valid'])} , 'is_success' :True})
                return Response(
                    response,
                    status=200,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )
        except Exception as e:
            response = json.dumps({'message': str(e), 'code': 500, 'is_success' :False})
            return Response(
                response,
                status=500,
            headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
        )

    @http.route('/shipping/create_shipping', auth="public", csrf=False, website=True, methods=['POST'])
    def create_shipping(self, **post):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        try:
            token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
            user_token = request.env['user.token.nasaem'].sudo().search([('token', '=', token)])
            if not user_token:
                response = json.dumps({'message': 'Unauthorized!', 'code': 401, 'is_success' :False})
                return Response(
                    response,
                    status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )

            user_id = int(user_token.user_id)
            partner = request.env['res.users'].sudo().browse(user_id).partner_id
            shipping_address_data = {
                'name': post.get('name'),
                'email': post.get('email'),
                'phone': post.get('phone'),
                'street': post.get('street'),
                'city': post.get('city'),
                'country_id': int(post.get('country_id')),
                'zip': post.get('zip'),
                'state_id' : int(post.get('state_id')),
                'x_studio_apartment' : post.get('x_studio_apartment'),
                'x_studio_area' : post.get('x_studio_area'),
                'x_studio_block' : post.get('x_studio_block'),
                'x_studio_block2' : post.get('x_studio_block2'),
                'x_studio_building_no' : post.get('x_studio_building_no'),
                'x_studio_floor' : post.get('x_studio_floor'),
                'parent_id': partner.id,
            }
            shipping_address = request.env['res.partner'].sudo().create(shipping_address_data)
            shipping_address.write({
                'is_valid' : True
            })
            sale_order = request.env['sale.order'].sudo().search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['draft', 'sent']), 
                ('website_id' , '=' ,2) # Filter by cart states (e.g., draft, sent)
            ], limit=1)
            if sale_order : 
                sale_order.partner_shipping_id = shipping_address.id
            message = 'تم إضافة العنوان' if language == 'ar_001' else  'Shipping address created successfully'
            response = json.dumps({'message': message, 'code': 200, 'data': shipping_address.id , 'is_success' :True})
            return Response(
                response,
                status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        except Exception as e:
            response = json.dumps({'message': 'Internal Server Error', 'code': 500, 'is_success' :False})
            return Response(
                response,
                status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )

    @http.route('/shipping/update_shipping/<int:shipping_id>', auth="public", csrf=False, website=True, methods=['PUT'])
    def update_shipping(self, shipping_id, **post):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        try:
            token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
            user_token = request.env['user.token.nasaem'].sudo().search([('token', '=', token)])
            if not user_token:
                response = json.dumps({'message': 'Unauthorized!', 'code': 401, 'is_success': False})
                return Response(
                    response,
                    status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )

            user_id = int(user_token.user_id)
            partner = request.env['res.users'].sudo().browse(user_id).partner_id
            shipping_address = request.env['res.partner'].sudo().browse(int(shipping_id))
            if not shipping_address :
                response = json.dumps({'message': 'Shipping address not found!', 'code': 404, 'is_success': False})
                return Response(
                    response,
                    status=404,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )

            shipping_address_data = {
                'name': post.get('name'),
                'email': post.get('email'),
                'phone': post.get('phone'),
                'street': post.get('street'),
                'city': post.get('city'),
                'country_id': int(post.get('country_id')),
                'zip': post.get('zip'),
                'state_id' : int(post.get('state_id')),
                'x_studio_apartment' : post.get('x_studio_apartment'),
                'x_studio_area' : post.get('x_studio_area'),
                'x_studio_block' : post.get('x_studio_block'),
                'x_studio_block2' : post.get('x_studio_block2'),
                'x_studio_building_no' : post.get('x_studio_building_no'),
                'x_studio_floor' : post.get('x_studio_floor'),
            }
            shipping_address.write(shipping_address_data)
            shipping_address.write({
                'is_valid' : True
            })
            sale_order = request.env['sale.order'].sudo().search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['draft', 'sent']), 
                ('website_id' , '=' ,2) # Filter by cart states (e.g., draft, sent)
            ], limit=1)
            if sale_order : 
                sale_order.partner_shipping_id = shipping_address.id
            message = 'تم تحديث العنوان' if language == 'ar_001' else 'Shipping address updated successfully'
            response = json.dumps({'message': message, 'code': 200, 'is_success': True})
            return Response(
                response,
                status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        except Exception as e:
            response = json.dumps({'message': str(e), 'code': 500, 'is_success': False})
            return Response(
                response,
                status=500,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )