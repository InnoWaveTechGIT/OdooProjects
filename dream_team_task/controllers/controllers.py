from odoo import http
import json
from odoo.http import request ,Response
import jwt
from datetime import datetime
from ast import literal_eval


class Controllers(http.Controller):


    @http.route('/auth/login', auth="public",csrf=False, website=True, methods=['POST'])
    def log_in(self,idd= None, **kw):
            language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
            try:
                uid = False
                login = kw['email']
                login = login.lower()
                message = ''

                password = kw['password']
            except Exception as e:
                message = 'بعض الحقول الإجبارية غير مدخل'if language == 'ar_001' else 'Some requierd fields is not enterd'
                response = json.dumps({'message':message , 'is_success' :False})
                return Response(
                    response, status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])

            user_id = request.env['res.users'].sudo().search([('login' , '=' , login)])
            print('user_id >>>>>>>>> ' , user_id)
            if len(user_id)==0 :
                    message = 'البريد الإلكتروني او كلمة المرور خاطئة'if language == 'ar_001' else 'Incorrect email or password'
                    response=json.dumps({"data":[],'message': message , 'is_success' : False})
                    return Response( response, status=402,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                    if checkPassword(password) == False:
                        response=json.dumps({"data":[],'message': 'Incorrect email or password'})
                        return Response( response, status=402,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                        )



            elif len(user_id) != 0:
                db = http.request.env.cr.dbname
                print('db >>>>> ' , db)
                try:
                    credential = {'login': login, 'password': password, 'type': 'password'}
                    uid=request.session.authenticate(db, credential)
                    print('uid >>>>>>>>> ' , uid)
                except Exception as e:
                    user_details = []
                    message = 'البريد الإلكتروني او كلمة المرور خاطئة'if language == 'ar_001' else 'Incorrect email or password'
                    response=json.dumps({"data":{"user":str(e),"token":'Null' }, 'message':message , 'is_success' :False} )


                    # response=json.dumps({"data":{"user":user_details,"token":'Null' }, 'message':message , 'is_success' :False} )
                    return Response( response,status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                date_now = datetime.today()
                is_ther_token = request.env['user.token.haven'].search([('user_id' , '=' , user_id.id)])
                if len(is_ther_token) != 0 :
                    date_now = str(datetime.today())
                    payload = {
                            'id': user_id.id,
                            'username': user_id.name,
                            'login' :login ,
                            'timestamp' : date_now,
                            }
                    str_uid = str(user_id)
                    SECRET='ali.ammar'
                    enc = jwt.encode(payload, SECRET)
                    is_ther_token.write({
                        'token' : enc
                    })
                    message = 'تفاصيل الحساب'if language == 'ar_001' else 'profile details'
                    user_details = [{"id":user_id.id,"username" :user_id.name,"email":user_id.login, 'phone' : user_id.phone ,"timestamp":str(date_now)}]
                    response=json.dumps({"data":{"user":user_details[0],"token":is_ther_token.token}, 'message':message , 'is_success' :True})
                    return Response( response,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
                else :
                    date_now = str(datetime.today())
                    payload = {
                            'id': user_id.id,
                            'username': user_id.name,
                            'login' :login ,
                            'timestamp' : date_now,
                            }
                    str_uid = str(user_id)
                    SECRET='ali.ammar'
                    enc = jwt.encode(payload, SECRET)
                    is_ther_token = request.env['user.token.haven'].sudo().create({
                        'user_id' : user_id.id,
                        'token' : enc
                    })
                    message = 'تفاصيل الحساب'if language == 'ar_001' else 'profile details'
                    user_details = [{"id":user_id.id,"username" :user_id.name,"email":user_id.login,"phone":user_id.phone,"timestamp":str(date_now)}]
                    response=json.dumps({"data":{"user":user_details[0],"token":is_ther_token.token}, 'message':message , 'is_success' :True})
                    return Response( response,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )


    @http.route('/api/v1/order-summary', auth='public', methods=['GET'], csrf=False)
    def get_my_cart(self,products=None,delivery_ids=None, **params):
        # Helper function for consistent responses
        def make_response(data, message, is_success, status=200):
            return Response(
                json.dumps({"data": data, "message": message, "is_success": is_success}),
                status=status,
                headers=[
                    ('Content-Type', 'application/json'),
                    ('accept', 'application/json'),
                    ('Content-Length', len(json.dumps(data)))
                ]
            )

        # Authentication
        try:
            token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return make_response('no data', 'Authorization header missing', False, 401)

            valid_token = request.env['user.token.haven'].search([('token', '=', token)])
            if not valid_token:
                return make_response([], 'Invalid token', False, 401)

            try:
                jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            except Exception:
                return make_response([], 'Token verification failed', False, 401)

        except Exception as e:
            return make_response('no data', 'Authentication error', False, 401)

        # Get user info
        try:
            user_id = valid_token[0]['user_id']
            user_partner = request.env['res.users'].sudo().search_read(
                [['id', '=', user_id]],
                fields=['partner_id']
            )
            if not user_partner:
                return make_response([], 'User partner not found', False, 400)

            partner_id = user_partner[0]['partner_id'][0]
        except Exception as e:
            return make_response([], 'Error fetching user data', False, 400)

        # Process parameters
        try:
            accepted_products = products
            delivery_ids = delivery_ids

            # Convert string parameters to lists
            accepted_product_ids = literal_eval(accepted_products) if accepted_products and accepted_products != '[]' else []
            delivery_id_list = literal_eval(delivery_ids) if delivery_ids and delivery_ids != '[]' else []

            if not isinstance(accepted_product_ids, list) or not isinstance(delivery_id_list, list):
                return make_response([], 'Invalid parameter format', False, 400)
        except Exception as e:
            return make_response([], 'Invalid parameter format', False, 400)

        # Build domain for sale order search
        domain = [('partner_id', '=', partner_id)]
        if delivery_id_list:
            domain.append(('partner_shipping_id', 'in', delivery_id_list))

        # Get sale orders
        sale_orders = request.env['sale.order'].sudo().search(domain, order='id desc')
        if not sale_orders:
            return make_response([], 'No active cart found', False, 200)

        # Filter orders that contain ALL accepted products
        valid_orders = []
        for order in sale_orders:
            order_product_ids = set(order.all_order_products.ids)

            # If no product filter or all requested products are in this order
            if not accepted_product_ids or all(pid in order_product_ids for pid in accepted_product_ids):
                valid_orders.append({
                    'id': order.id,
                    'name': order.name,
                    'partner_shipping_name': order.partner_shipping_id.name,
                    'partner_shipping_id': order.partner_shipping_id.id,
                    'products_ids': list(order_product_ids),
                    'date': order.date_order.strftime('%Y-%m-%d %H:%M:%S') if order.date_order else None,
                    'amount_total': order.amount_total
                })

        if not valid_orders:
            missing_products = set(accepted_product_ids) - set(order_product_ids) if accepted_product_ids else set()
            message = 'No orders contain all requested products'
            if missing_products:
                message += f" (Missing products: {list(missing_products)})"
            return make_response([], message, False, 200)

        return make_response({'cart_items': valid_orders}, 'Cart details retrieved successfully', True, 200)


    @http.route('/cart/details', auth='public', methods=['GET'], csrf=False)
    def get_my_cart_details(self,id, **params):
        authe = request.httprequest.headers
        accepted_products = params.get('products', False)
        delivery_ids = params.get('delivery_ids', False)
        url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.haven'].search([('token', '=', token)])
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

            domain = [ ('id', '=', int(id))]
            if accepted_products and accepted_products != '[]':
                accepted_products = literal_eval(accepted_products)

            if delivery_ids and delivery_ids != '[]':
                delivery_ids = literal_eval(delivery_ids)
                domain.append(('partner_shipping_id', 'in', delivery_ids))
            sale_order = request.env['sale.order'].sudo().search(domain, order='id desc')
            if sale_order:
                cart_items = []
                for line in sale_order.order_line:
                        product = line.product_template_id
                        if accepted_products and accepted_products != '[]' :
                            if product.id in accepted_products :
                                cart_items.append({
                                    'id': line.id,
                                    'product_id': line.product_template_id.id,
                                    'name': product.name,
                                    'quantity': line.product_uom_qty,
                                    'price': line.price_unit,
                                    'currency' : line.product_template_id.cost_currency_id.name,
                                    'description_sale' : product.description_sale,
                                    'image':url + '/web/image?' + 'model=product.template&id=' + str(product.id) + '&field=image_1920',
                                    'subtotal': line.price_subtotal,
                                    'category' : [{
                                                'id' : item.id,
                                                'name' : item.name
                                            }for item in product.public_categ_ids ]
                                    # Add other fields as required
                                })

                        else :
                            cart_items.append({
                                'id': line.id,
                                'product_id': line.product_template_id.id,
                                'name': product.name,
                                'quantity': line.product_uom_qty,
                                'price': line.price_unit,
                                'currency' : line.product_template_id.cost_currency_id.name,
                                'description_sale' : product.description_sale,
                                'image':url + '/web/image?' + 'model=product.template&id=' + str(product.id) + '&field=image_1920',
                                'subtotal': line.price_subtotal,
                                'category' : [{
                                            'id' : item.id,
                                            'name' : item.name
                                        }for item in product.public_categ_ids ]
                            })

                message = 'Cart Details'
                response = json.dumps({"data": {'cart_items': cart_items}, 'message': message , 'is_success' :True})
                return Response(
                    response, status=200,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'), ('Content-Length', 100)]
                )
            else:
                message = 'You don"t have an active cart'
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






