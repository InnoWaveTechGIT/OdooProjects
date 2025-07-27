from odoo import http
import json
from odoo.http import request ,Response
import jwt
class BannerController(http.Controller):
    url = 'https://www.alnasaem.com' 
    @http.route('/cart/mine', auth='public', methods=['GET'], csrf=False)
    def get_my_cart(self, **params):
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
        cur = False
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!' , 'is_success' :False})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        
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
            user_id = valid_token[0]['user_id']
            user_partner = request.env['res.users'].sudo().search_read(
                [['id', '=', user_id]]
            )
            user_partner = user_partner[0]['partner_id']
            sale_order = request.env['sale.order'].sudo().with_context(lang=language).search([
                ('partner_id', '=', user_partner[0]), 
                ('website_id' , '=' ,2) 
            ], order='id desc', limit=1)
            
            if sale_order:
                # Retrieve cart details and format the response
                cart_items = []
                invoice_ids = sale_order.invoice_ids
                if invoice_ids:
                    for i in invoice_ids:
                        if i.payment_state == 'not_paid' :
                            inv_available = True
                        else :
                            inv_available = False
                else :
                    inv_available = True
                if inv_available:
                    for line in sale_order.order_line:
                        product = line.product_template_id
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
                        cart_items.append({
                            'id': line.id,
                            'product_id': line.product_template_id.id,
                            'name': product.name,
                            'quantity': line.product_uom_qty,
                            'price': line.price_unit,
                            'currency' : cur  if pricecurrency else line.product_template_id.cost_currency_id.name,
                            'description_sale' : product.description_sale,
                            'image':self.url + '/web/image?' + 'model=product.template&id=' + str(product.id) + '&field=image_1920',
                            'subtotal': line.price_subtotal,
                            'category' : [{
                                        'id' : item.id,
                                        'name' : item.name
                                    }for item in product.public_categ_ids ]
                            # Add other fields as required
                        })  
                    invoice_details = []
                    invoice_details.append({
                        'amount_total' :sale_order.amount_total,
                        'amount_tax' : sale_order.amount_tax,
                        'currency' : sale_order.currency_id.name
                    })      

                    message = 'تفاصيل العربة' if language == 'ar_001' else 'Cart Details'
                    response = json.dumps({"data": {'cart_id' : sale_order.id ,'cart_items': cart_items , 'invoice_details' :invoice_details }, 'message': message , 'is_success' :True})
                    return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
                    )
                else:
                    message = 'لا تملك عربة' if language == 'ar_001' else 'You don"t have an active cart'
                    response = json.dumps({"data": [], 'message': message , 'is_success' :False})
                    return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
                    )
            else:
                message = 'لا تملك عربة' if language == 'ar_001' else 'You don"t have an active cart'
                response = json.dumps({"data": [], 'message': message , 'is_success' :False})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
                )
        else:
            message = 'لا تملك عربة' if language == 'ar_001' else "You don't have an active cart"
            response = json.dumps({"data": [], 'message': 'Invalid token' , 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
            )


    @http.route('/cart/mine', auth='public', methods=['DELETE'], csrf=False)
    def clear_my_cart(self, **params):
        response = ''
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        authe = request.httprequest.headers
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!' , 'is_success' :False})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

        if valid_token:
            user_id = valid_token[0]['user_id']
            user_partner = request.env['res.users'].sudo().search_read(
                [['id', '=', user_id]]
            )
            user_partner = user_partner[0]['partner_id']
            sale_order = request.env['sale.order'].sudo().search([
                ('partner_id', '=', user_partner[0]),
                ('state', 'in', ['draft', 'sent']),
                ('website_id', '=', 2)  # Filter by cart states (e.g., draft, sent)
            ], limit=1)

            if sale_order:
                sale_order.order_line.unlink()  # Delete all order lines in the cart
                message = 'تم حذف العربة' if language == 'ar_001' else 'Cart cleared successfully'
                response = json.dumps({"data": [], 'message': message, 'is_success' :True})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
                )
            else:
                message = 'لا تملك عربة' if language == 'ar_001' else "You don't have an active cart"
                response = json.dumps({"data": [], 'message':message , 'is_success' :False})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
                )
        else:
            message = 'التوكين غير صالح' if language == 'ar_001' else 'Invalid token'
            response = json.dumps({"data": [], 'message': message, 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
            )
    @http.route('/cart/<int:product_id>', auth='public', methods=['DELETE'], csrf=False)
    def delete_item_from_cart(self,product_id, **params):
        response = ''
        cart_items = []
        invoice_details =[]
        authe = request.httprequest.headers
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!' , 'is_success' :False})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

        if valid_token:
            user_id = valid_token[0]['user_id']
            user_partner = request.env['res.users'].sudo().search_read(
                [['id', '=', user_id]]
            )
            user_partner = user_partner[0]['partner_id']
            sale_order = request.env['sale.order'].sudo().search([
                ('partner_id', '=', user_partner[0]),
                ('state', 'in', ['draft', 'sent']),
                ('website_id', '=', 2)  # Filter by cart states (e.g., draft, sent)
            ], limit=1)

            if sale_order:
                product_id = int(product_id)
                order_line = sale_order.order_line.filtered(lambda line: line.product_template_id.id == product_id)
                
                if order_line:
                    order_line.unlink()  # Delete the specific order line from the cart
                    for line in sale_order.order_line:
                        cart_items.append({
                                'id': line.id,
                                'product_id': line.product_template_id.id,
                                'name': line.product_template_id.name,
                                'quantity': line.product_uom_qty,
                                'price': line.price_unit,
                                'currency' : line.product_template_id.cost_currency_id.name,
                                'description_sale' : line.product_template_id.description_sale,
                                'image':self.url + '/web/image?' + 'model=product.template&id=' + str(line.product_template_id.id) + '&field=image_1920',
                                'subtotal': line.price_subtotal,
                                'category' : [{
                                            'id' : item.id,
                                            'name' : item.name
                                        }for item in line.product_template_id.public_categ_ids ]
                                # Add other fields as required
                            })  
                        invoice_details = []
                        invoice_details.append({
                            'amount_total' :sale_order.amount_total,
                            'amount_tax' : sale_order.amount_tax,
                            'currency' : sale_order.currency_id.name
                        })      
                    message = 'تم حذف العنصر' if language == 'ar_001' else 'Item deleted successfully'
                    response = json.dumps({"data": {  'cart_items': cart_items , 'invoice_details' :invoice_details }, 'message': message , 'is_success' :True})
                    return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
                    )
                else:
                    message = 'لم يتم ايجاد العنصر في العربة' if language == 'ar_001' else 'Item not found in the cart'
                    response = json.dumps({"data": [], 'message': message , 'is_success' :False})
                    return Response(
                        response, status=404,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
                    )
            else:
                message = 'لا تملك عربة' if language == 'ar_001' else "You don't have an active cart"
                response = json.dumps({"data": [], 'message': message , 'is_success' :False})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
                )
        else:
            response = json.dumps({"data": [], 'message': 'Invalid token', 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
            )

    @http.route('/cart/<int:product_id>', auth='public', methods=['POST'], csrf=False)
    def add_item_to_cart(self,product_id , **params):
        try:
            response = ''
            pricecurrency = False
            country = False
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
                user_id = valid_token[0]['user_id']
                user_partner = request.env['res.users'].sudo().search_read(
                    [['id', '=', user_id]]
                )
                try:
                    dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
                    # location = dec_token['location']
                    # if location in ['KW' , 'SA' ,'BH' ,'OM' , 'AE']:
                    #     location = location
                    # else :
                    #     location = 'KW'
                    # country = request.env['res.country'].search([('code', '=', location)])
                    # if country:
                    #     cur = country.currency_id.name

                    # else:
                    #     location = ''
                    #     cur= ''
                except Exception as e:
                    response = json.dumps({ 'jsonrpc': '2.0', 'message': 'Unauthorized!' , 'is_success' :False})
                    return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
            
                
        
                user_partner = request.env['res.partner'].sudo().browse(user_partner[0]['partner_id'][0])
                sale_order = request.env['sale.order'].sudo().search([
                    ('partner_id', '=', user_partner.id),
                    ('state', 'in', ['draft', 'sent']),
                    ('website_id', '=', 2)  # Filter by cart states (e.g., draft, sent)
                ], limit=1)

                

                product_id = int(product_id)
                product = request.env['product.product'].sudo().search([('product_tmpl_id', '=', product_id)], limit=1)

                if product and product.qty_available != 0:
                    
                    # if cur:
                    #     pricelist = request.env['product.pricelist'].sudo().search(
                    #         [('currency_id.name', '=', cur)],
                    #         limit=1
                    #     )
                    #     if pricelist:
                    #         price = pricelist.sudo()._compute_price_rule( products = product, qty =1, uom = product.uom_id)
                    #         # sale_order.pricelist_id = pricelist.id
                    #     pricecurrency = request.env['res.currency'].sudo().search(
                    #         [('name', '=', cur),('active' , '=' , True)],
                    #         limit=1
                    #     )
                    # if pricecurrency:
                    #     price_cu = product.list_price * pricecurrency.rate
                    # else :
                    #     price_cu = product.list_price
                    if not sale_order:
                    # Create a new cart if none exists
                        sale_order = request.env['sale.order'].sudo().create({
                            'partner_id': user_partner.id,
                            'website_id': 2,  # Set the website ID for the cart
                            'pricelist_id': user_partner.property_product_pricelist.id,  # Set the pricelist ID for the cart
                            'user_id': 2,
                        })
                    order_line = sale_order.order_line.filtered(lambda line: line.product_template_id.id == product_id)
                    if order_line:
                        # If the item already exists in the cart, increase the quantity
                        order_line.write({'product_uom_qty': order_line.product_uom_qty + 1})
                    else:
                        # If the item doesn't exist, create a new order line
                        order_line = request.env['sale.order.line'].sudo().create({
                            'order_id': sale_order.id,
                            'product_id': product.id,
                            'name': product.name,
                            'product_uom_qty': 1,
                            'price_unit': price_cu if pricecurrency else product.list_price,
                            'currency_id': country.currency_id.id if country else 93
                        })
                    sale_order.currency_id = country.currency_id.id if country else 93
                    sale_order.invoice_status = 'to invoice'
                    message = 'تم إضافة العنصر الى العربة' if language == 'ar_001' else 'Item added to cart successfully'
                    response = json.dumps({"data": [], 'message': message, 'is_success' :True})
                    return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
                    )
                else:
                    message = 'المنتج غير موجود' if language == 'ar_001' else 'Product not found'
                    response = json.dumps({"data": [], 'message': message , 'is_success' :False})
                    return Response(
                        response, status=404,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
                    )
            else:
                message = 'التوكين غير صالح' if language == 'ar_001' else 'Invalid token'
                response = json.dumps({"data": [], 'message': message , 'is_success' :False})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
                )
        except Exception as e:
            response = json.dumps({'data': [], 'message': str(e), 'is_success' :False})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )


    @http.route('/cart/<int:product_id>', auth='public', methods=['PUT'], csrf=False)
    def update_cart_item_quantity(self, product_id, **params):
        response = ''
        cart_items = []
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
            user_id = valid_token[0]['user_id']
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
                response = json.dumps({'jsonrpc': '2.0', 'message': 'Unauthorized!', 'is_success' :False})
                return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )

            user_partner = request.env['res.partner'].sudo().browse(user_partner[0]['partner_id'][0])
            sale_order = request.env['sale.order'].sudo().search([
                ('partner_id', '=', user_partner.id),
                ('state', 'in', ['draft', 'sent']),
                ('website_id', '=', 2)  # Filter by cart states (e.g., draft, sent)
            ], limit=1)

            if not sale_order:
                # Create a new cart if none exists
                sale_order = request.env['sale.order'].sudo().create({
                    'partner_id': user_partner.id,
                    'website_id': 2,  # Set the website ID for the cart
                    'pricelist_id': user_partner.property_product_pricelist.id,  # Set the pricelist ID for the cart
                    'user_id': 2,
                })

            product_id = int(product_id)
            product = request.env['product.template'].sudo().browse(product_id)

            if product:
                order_line = sale_order.order_line.filtered(lambda line: line.product_template_id.id == product_id)
              
                if order_line:
                    # Update the quantity of the existing order line
                    quantity = params.get('quantity', 0)
                    try:
                        quantity = int(quantity)
                    except ValueError:
                        message = 'الكمية غير صالحة' if language == 'ar_001' else 'Invalid quantity' 
                        response = json.dumps({"data": [], 'message': message, 'is_success' :False})
                        return Response(
                            response, status=400,
                            headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                                    ('Content-Length', 100)]
                        )

                    if quantity > 0:
                        order_line.write({'product_uom_qty': quantity})
                        for line in sale_order.order_line:
                            cart_items.append({
                                    'id': line.id,
                                    'product_id': line.product_template_id.id,
                                    'name': product.name,
                                    'quantity': line.product_uom_qty,
                                    'price': line.price_unit,
                                    'currency' :line.product_template_id.cost_currency_id.name,
                                    'description_sale' : product.description_sale,
                                    'image':self.url + '/web/image?' + 'model=product.template&id=' + str(product.id) + '&field=image_1920',
                                    'subtotal': line.price_subtotal,
                                    'category' : [{
                                                'id' : item.id,
                                                'name' : item.name
                                            }for item in product.public_categ_ids ]
                                    # Add other fields as required
                                })  
                            invoice_details = []
                            invoice_details.append({
                                'amount_total' :sale_order.amount_total,
                                'amount_tax' : sale_order.amount_tax,
                                'currency' : sale_order.currency_id.name
                            })      

                        message = 'تم تعديل كمية المنتج في العربة' if language == 'ar_001' else 'Cart item quantity updated successfully'
                        response = json.dumps({"data": {'cart_items': cart_items , 'invoice_details' :invoice_details }, 'mm': message , 'is_success' :True})
                        return Response(
                            response, status=200,
                            headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                                    ('Content-Length', 100)]
                        )
                    else:
                        message = 'الكمية يجب ان تكون أكير من الصفر' if language == 'ar_001' else 'Quantity must be greater than 0' 
                        response = json.dumps({"data": [], 'message': message, 'is_success' :False})
                        return Response(
                            response, status=400,
                            headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                                    ('Content-Length', 100)]
                        )
                else:
                    message = 'المنتج غير موجود في العربة' if language == 'ar_001' else 'Product not found in the cart'
                    response = json.dumps({"data": [], 'message': message , 'is_success' :False})
                    return Response(
                        response, status=404,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                                ('Content-Length', 100)]
                    )
            else:
                message = 'المنتج غير موجود' if language == 'ar_001' else 'Product not found'
                response = json.dumps({"data": [], 'message': message , 'is_success' :False})
                return Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                            ('Content-Length', 100)]
                )
        else:
            message = 'التوكين غير صالح' if language == 'ar_001' else 'Invalid token'
            response = json.dumps({"data": [], 'message': message , 'is_success' :False})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
            )