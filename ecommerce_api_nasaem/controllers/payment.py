
from odoo import http
import json
from odoo.http import request ,Response
import sys
import jwt
import requests
import time
import ast

class PaymentController(http.Controller):
    def call_api(self ,api_url, api_key, request_data, request_type="POST"):
        request_data = json.dumps(request_data)
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}
        response = requests.request(request_type, api_url, data=request_data, headers=headers)
        # handle_response(response)
        return response

    base_url = "https://api.myfatoorah.com"
    # base_url = "https://apitest.myfatoorah.com"
    # api_key ='rLtt6JWvbUHDDhsZnfpAhpYk4dxYDQkbcPTyGaKp2TYqQgG7FGZ5Th_WD53Oq8Ebz6A53njUoo1w3pjU1D4vs_ZMqFiz_j0urb_BH9Oq9VZoKFoJEDAbRZepGcQanImyYrry7Kt6MnMdgfG5jn4HngWoRdKduNNyP4kzcp3mRv7x00ahkm9LAK7ZRieg7k1PDAnBIOG3EyVSJ5kK4WLMvYr7sCwHbHcu4A5WwelxYK0GMJy37bNAarSJDFQsJ2ZvJjvMDmfWwDVFEVe_5tOomfVNt6bOg9mexbGjMrnHBnKnZR1vQbBtQieDlQepzTZMuQrSuKn-t5XZM7V6fCW7oP-uXGX-sMOajeX65JOf6XVpk29DP6ro8WTAflCDANC193yof8-f5_EYY-3hXhJj7RBXmizDpneEQDSaSz5sFk0sV5qPcARJ9zGG73vuGFyenjPPmtDtXtpx35A-BVcOSBYVIWe9kndG3nclfefjKEuZ3m4jL9Gg1h2JBvmXSMYiZtp9MR5I6pvbvylU_PP5xJFSjVTIz7IQSjcVGO41npnwIxRXNRxFOdIUHn0tjQ-7LwvEcTXyPsHXcMD8WtgBh-wxR8aKX7WPSsT1O8d8reb2aR7K3rkV3K82K_0OgawImEpwSvp9MNKynEAJQS6ZHe_J_l77652xwPNxMRTMASk1ZsJL'
    api_key = "55X-_ZDbefDtPYZXbTgFNYHZRFJXADudwf-4FSyJPb1_OJvJ5unaqes55-P816yCZwlk9N2_z8dCDn2njJfOszuzrEGR64MRXZHyoEGtKcDV3Dt1X2Lm_l3934qCNbMug1nl8y8IWlFPCPGHCt09JXh1FuMHdx-KENs2BolnXD2HjzIsLxOSwCQqD7YfguCRaV6HVkgswGfWJtFscxNxtpomMLyLHAg4jmEWHKs41VM5q2lH48QaDHpOYKpfS7ljJVhNtqiuL2rywffTZpXNqSH3Qj4ev6kUsStBiNmZX2hcwJBJl2uMxqpDA_FEyWTbW7IQ2e0gvWLAv8-5vixKLpvSYzxwWaPyA-_JXipoZPjxSMtK2Ir8rkk8Oh_bMcxJZLCOffczisY1jMMrL4s-vLvndSsxDdrx3HObVM_2En0bImkr2h4h84oWxBykOdoB1nLI5y6XqiXgja3b-zmiNcKBe0RvvREZNcnt-EmPrU7WuPpbTeu23XxosbfYWMupph5yXmpL8TR6sW1-5Ebqj5V_e8Zh5TEAsJKr4lJ_gOFdS8FQ9bBDsbBfXb2k-xfio6KfpZOn5DfxcS8Q6XLOs2p-szF1N0gaz-sp1_qxs2BfzZk3vQDGLraErDPQR2423ptyImhhRYgD5MdAX1yW6sSLjJsEJBsAKlf2ZZ8LwnNFViCU" 
    @http.route('/payment/invoice', auth="public", csrf=False, website=True, methods=['GET'])
    def get_my_invoice(self,so,sh, **kw):
        try:
            language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
            authe = request.httprequest.headers
            valid_token = ''
            cur = False
            sh=int(sh)
            ship_meth = 2
            try:
                token = authe['Authorization'].replace('Bearer ', '')
                valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
            except Exception as e:
                response = json.dumps({'data': 'no data', 'message': 'Unauthorized!', 'is_success': False})
                return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )

            if valid_token:
                try:
                    dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
                except Exception as e:
                    response = json.dumps({'jsonrpc': '2.0', 'message': 'Unauthorized!', 'is_success': False})
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
                                  ('id', '=', int(so)),
                ], limit=1)

                sale_order.partner_shipping_id = sh
       
                if sale_order:
                  
                    
                    ship_meth = 1        
                    # sale_order.partner_shipping_id = sh
                    if sale_order.partner_shipping_id.country_id.name == 'Kuwait':
                        ship_meth = 1
                    elif sale_order.partner_shipping_id.country_id.name =='Saudi Arabia' : 
                        ship_meth = 3
                    else:
                        ship_meth == 2
                    
                    delivery_wizard = request.env['choose.delivery.carrier'].sudo().create({
                        'order_id': sale_order.id,
                        'carrier_id': ship_meth
                    })
                    choose_delivery_carrier = delivery_wizard
                    choose_delivery_carrier._get_shipment_rate()
                    choose_delivery_carrier.sudo().button_confirm()
                    sale_order.amount_delivery = choose_delivery_carrier.display_price
                    
                    billing = sale_order.partner_id.read(fields=['id', 'name', 'email', 'phone', 'country_id', 'zip', 'street', 'street2', 'city' , 'state_id' ,'x_studio_apartment' ,'x_studio_area' ,'x_studio_block' ,'x_studio_block2' ,'x_studio_building_no' ,'x_studio_floor' ])
                    shipping = sale_order.partner_shipping_id.read(fields=['id', 'name', 'email', 'phone', 'country_id', 'zip', 'street', 'street2', 'city' , 'state_id' ,'x_studio_apartment' ,'x_studio_area' ,'x_studio_block' ,'x_studio_block2' ,'x_studio_building_no' ,'x_studio_floor' ])
                    invoice_details = {
                        'id': sale_order.id,
                        'name' : sale_order.partner_id.name ,
                        'currency_id' : sale_order.currency_id.name , 
                        'amount' : sale_order.amount_total,
                        'billing' : billing,
                        'shipping' : shipping ,
                        'delivery' : 'Delivery Charges applied on your invoice'
                    }
                    
                    message = 'تفاصيل الفاتورة' if language == 'ar_001' else 'Invoice Details'
                    response = json.dumps({"data": invoice_details, 'message': message, 'is_success': True})
                    return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                                ('Content-Length', 100)]
                    )
                else:
                    # invoice = sale_order.invoice_ids[0]
                    # sale_order.invoice_status = 'to invoice'
                    # invoice_details = billing = sale_order.partner_id.read(fields=['id', 'name', 'email', 'phone', 'country_id', 'zip', 'street', 'street2', 'city' , 'state_id' ,'x_studio_apartment' ,'x_studio_area' ,'x_studio_block' ,'x_studio_block2' ,'x_studio_building_no' ,'x_studio_floor' ])
                    # shipping = sale_order.partner_shipping_id.read(fields=['id', 'name', 'email', 'phone', 'country_id', 'zip', 'street', 'street2', 'city' , 'state_id' ,'x_studio_apartment' ,'x_studio_area' ,'x_studio_block' ,'x_studio_block2' ,'x_studio_building_no' ,'x_studio_floor' ])
                    # invoice_details = {
                    #     'id': sale_order.invoice_ids.id,
                    #     'name' : sale_order.invoice_ids.partner_id.name ,
                    #     'currency_id' : sale_order.invoice_ids.currency_id.name , 
                    #     'amount' : sale_order.invoice_ids.amount_residual,
                    #     'billing' : billing,
                    #     'shipping' : shipping ,
                    #     'delivery' : 'Delivery Charges applied on your invoice'
                    # }
                    message = 'لا تملك عربة' if language == 'ar_001' else 'You don\'t have a Cart'
                    response = json.dumps({"data": [], 'message': message, 'is_success': False})
                    return Response(
                        response, status=404,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                                ('Content-Length', 100)]
                    )
            else :
                message = 'التوكين غير صالح' if language == 'ar_001' else 'Inalid token'
                response = json.dumps({"data": [], 'message': message, 'is_success': False})
                return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                            ('Content-Length', 100)]
              )   
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': str(e), 'is_success': False})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
    @http.route('/payment/pay', auth="public", csrf=False, website=True, methods=['POST'])
    def pay_on_myfatoorah(self, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        authe = request.httprequest.headers
        valid_token = ''
        cur = False
        invoice_id = int(kw.get('inv_id'))
        paymentMethodId = int(kw.get('paymentMethodId' , 1))
        back_url = kw.get('back_url' , "https://example.com/callback.php")
        error_url = kw.get('error_url' , "https://example.com/callback.php")
        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!', 'is_success': False})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

        if valid_token:
            try:
                dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            except Exception as e:
                response = json.dumps({'jsonrpc': '2.0', 'message': 'Unauthorized!', 'is_success': False})
                return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            try :
                
                invoice = request.env['sale.order'].sudo().search([
                    ('id', '=', int(invoice_id)),
                ], limit=1)
                if invoice : 
                    api_url = self.base_url + "/v2/InitiatePayment"
                    initiatepay_request = {
                        "InvoiceAmount": invoice.amount_total,
                        "CurrencyIso": invoice.currency_id.name
                        }

                    initiatedpay_response = self.call_api(api_url, self.api_key, initiatepay_request).json()
                    payment_methods = initiatedpay_response["Data"]["PaymentMethods"]
                    api_url = self.base_url + "/v2/ExecutePayment"
                    # sale_order = request.env['sale.order'].sudo().search([('invoice_ids' , 'in' , [invoice.id])])
                    executepay_request = {
                            "paymentMethodId" : paymentMethodId,
                            "InvoiceValue"    : invoice.amount_total,
                            "CallBackUrl"     : 'https://www.alnasaem.com/payment/callback' + '/'+str(invoice.id),
                            "ErrorUrl"        : 'https://www.alnasaem.com/payment/error',
                            "CustomerName"       : invoice.partner_id.name,
                            "DisplayCurrencyIso" : invoice.currency_id.name,
                            #"MobileCountryCode"  : "+965",
                            #"CustomerMobile"     : "1234567890",
                            #"CustomerEmail"      : "email@example.com",
                            "Language"           : "en", #or "ar"
                            "CustomerReference"  : invoice.name,
                            #"CustomerCivilId"    : "CivilId",
                            #"UserDefinedField"   : "This could be string, number, or array",
                            #"ExpiryDate"         : "", #The Invoice expires after 3 days by default. Use "Y-m-d\TH:i:s" format in the "Asia/Kuwait" time zone.
                            #"SourceInfo"         : "Pure PHP", #For example: (Laravel/Yii API Ver2.0 integration)
                            #"CustomerAddress"    : "customerAddress",
                            #"InvoiceItems"       : "invoiceItems",
                        }
                    executepay_response = self.call_api(api_url, self.api_key, executepay_request).json()
                    
                    invoice_id = executepay_response["Data"]["InvoiceId"]
                    invoice_url = executepay_response["Data"]["PaymentURL"]

                    response = json.dumps({"data": executepay_response, 'message': 'Done', 'is_success': True})
                    return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                                ('Content-Length', 100)]
                    )
                else : 
                    response = json.dumps({'data': 'no data', 'message' :'server error please try again later and make sure you have a good internet connection', 'is_success': False})
                    return Response(
                        response, status=401,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
            except Exception as e:
                response = json.dumps({'data': 'no data', 'message' :'server error please try again later and make sure you have a good internet connection', 'is_success': False})
                return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        response = json.dumps({'data': [], 'message': 'Invalid token', 'is_success': False})
        return Response(
            response, status=401,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
    @http.route('/payment/payed', auth="public", csrf=False, website=True, methods=['POST'])
    def payed_on_odoo(self, **kw):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        authe = request.httprequest.headers
        valid_token = ''
        cur = False
        invoice_id = int(kw.get('inv_id'))
        paymentId = int(kw.get('paymentId' , 0))

        try:
            token = authe['Authorization'].replace('Bearer ', '')
            valid_token = request.env['user.token.nasaem'].search([('token', '=', token)])
        except Exception as e:
            response = json.dumps({'data': 'no data', 'message': 'Unauthorized!', 'is_success': False})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )

        if valid_token:
            try:
                dec_token = jwt.decode(token, "ali.ammar", algorithms=["HS256"])
            except Exception as e:
                response = json.dumps({'jsonrpc': '2.0', 'message': 'Unauthorized!', 'is_success': False})
                return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            try:
                user_id = valid_token[0]['user_id']
                user_partner = request.env['res.users'].sudo().search_read(
                    [['id', '=', user_id]]
                )
                
                invoice = request.env['account.move'].sudo().search([
                    ('id', '=', int(invoice_id)),
                ], limit=1)
               
            except Exception as e:
                response = json.dumps({'jsonrpc': '2.0', 'message': str(e), 'is_success': False})
                return Response(
                    response, status=401,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
            if invoice :          
                try :
                    invoice.sudo().action_post()
                    
                    payment = request.env['account.payment.method.line'].sudo().search([])            
                    sale_order = request.env['sale.order'].sudo().search([('invoice_ids' , 'in' , [invoice_id])])
                    
                    journal_id = http.request.env['account.journal'].sudo().search([('code', 'ilike', '678')], limit=1)
                    
                    payment_id = request.env['account.payment'].sudo().create({
                    'ref' : invoice.name ,
                    'amount' : invoice.amount_residual,
                    'payment_method_line_id' : 18 , 
                    'company_id' : 5,
                    'payment_type' : 'inbound' ,
                    'partner_id' : invoice.partner_id.id , 
                    'currency_id' : invoice.currency_id.id
                    })
                    payment_id.action_post()
                    tx_sudo = request.env['payment.transaction'].sudo().create({
                    'reference' : sale_order.name,
                    'amount' : invoice.amount_residual,
                    'provider_id' :19, 
                    'company_id' : 5,
                    'partner_id' : invoice.partner_id.id , 
                    'partner_email' : invoice.partner_id.email,
                    'partner_phone' : invoice.partner_id.phone,
                    'partner_lang' : 'ar_001',
                    'currency_id' : invoice.currency_id.id
                    })

                    invoice.write({
                        'transaction_ids': [(4, tx_sudo.id)],
                        'payment_state' : "in_payment"
                    })
                    

                    response = json.dumps({"data": [], 'message': 'Done', 'is_success': True})
                    return Response(
                        response, status=200,
                        headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                                ('Content-Length', 100)]
                    )
                except Exception as e:
                    response = json.dumps({'jsonrpc': '2.0', 'message': 'server error please try again later and make sure you have a good internet connection', 'is_success': False})
                    return Response(
                        response, status=401,
                        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                    )
            else:
                response = json.dumps({"data": [], 'message': "you don't have active invoice", 'is_success': False})
                return Response(
                    response, status=404,
                    headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                            ('Content-Length', 100)]
                )
                    # print('payment_wizard >>> ' , x)
        
        else:
            response = json.dumps({"data": [], 'message': 'Invalid Token', 'is_success': False})
            return Response(
                response, status=401,
                headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                        ('Content-Length', 100)]
            )   
    @http.route('/payment/callback/<int:inv_id>', type='http', auth='public', website=True)
    def payment_callback(self,inv_id,**data):
        int(inv_id)
        sale_order = request.env['sale.order'].sudo().search([
                                  ('id', '=', int(inv_id)),
                ], limit=1)
        
        try:
            for order_line in sale_order.order_line:
                order_line.product_id.invoice_policy = 'order'
                # Create the invoice
                advance_payment_obj = request.env['sale.advance.payment.inv']

                # Set the field values
                values = {
                    'advance_payment_method': 'delivered',  # Set the desired value for advance_payment_method field
                    'sale_order_ids': [(6, 0, [sale_order.id])],  # Set the desired sale order IDs
                    # Set other desired field values
                    # ...
                }
            advance_payment = advance_payment_obj.sudo().create(values)
        except Exception as e:
                pass
        sale_order.sudo().action_confirm()
        # sale_order.invoice_status = 'to invoice'
        invoice = advance_payment.create_invoices()
        email = sale_order.sudo().action_quotation_send()
                    
        template = request.env.ref('sale.mail_template_sale_confirmation').sudo()
        template.send_mail(sale_order.id, force_send=True)
        invoice = sale_order.invoice_ids[0]
        invoice.sudo().action_post()
        sale_order.invoice_status = 'invoiced'
        payment_meth_id=0
        journal_id = http.request.env['account.journal'].sudo().search([('id', '=', 10)], limit=1)
        for payment in journal_id.inbound_payment_method_line_ids:
            if payment.name == 'MyFatoorah' :
                payment_meth_id = payment.id
        payment_id = request.env['account.payment'].sudo().create({
        'ref' : invoice.name ,
        'amount' : invoice.amount_residual,
        'journal_id' : 10,
        'payment_method_line_id' : payment_meth_id if payment_meth_id else 18 , 
        'company_id' : 5,
        'payment_type' : 'inbound' ,
        'partner_id' : invoice.partner_id.id , 
        'currency_id' : invoice.currency_id.id
        })
        payment_id.action_post()
        tx_sudo = request.env['payment.transaction'].sudo().create({
        'reference' : sale_order.name+'123',
        'amount' : invoice.amount_residual,
        'provider_id' :19, 
        'company_id' : 5,
        'partner_id' : invoice.partner_id.id , 
        'partner_email' : invoice.partner_id.email,
        'partner_phone' : invoice.partner_id.phone,
        'partner_lang' : 'ar_001',
        'currency_id' : invoice.currency_id.id
        })

        invoice.write({
            'transaction_ids': [(4, tx_sudo.id)],
            'payment_state' : "in_payment"
        })
                


        return request.render('ecommerce_api_nasaem.payment_callback_page')
    
    @http.route('/payment/error', type='http', auth='public', website=True)
    def payment_error(self):


        return request.render('ecommerce_api_nasaem.payment_error_page')

    @http.route('/set_fully/status/<int:inv_id>', type='http', csrf=False, auth='public', website=True, methods=['GET'])
    def asdasdqweqqwe(self,inv_id,**data):
        sale_order = request.env['sale.order'].sudo().search([('id' , '=' , inv_id)])
        sale_order.invoice_status = 'invoiced'
        response = json.dumps({"data": [], 'message': 'Done', 'is_success': False})
        return Response(
            response, status=200,
            headers=[('Content-Type', 'application/json'), ('accept', 'application/json'),
                    ('Content-Length', 100)]
            ) 
               


# def check_data(key, response_data):
#     if key in response_data.keys() and response_data[key] is not None:
#         return True
#     else:
#         return False


# # Error Handle Function
# def handle_response(response):
#     if response.text == "":  # In case of empty response
#         raise Exception("API key is not correct")

#     response_data = response.json()
#     response_keys = response_data.keys()

#     if "IsSuccess" in response_keys and response_data["IsSuccess"] is True:
#         return  # Successful
#     elif check_data("ValidationErrors", response_data):
#         error = []
#         for i in range(len(response.json()["ValidationErrors"])):
#             v_error = [response_data["ValidationErrors"][i].get(key) for key in ["Name", "Error"]]
#             error.append(v_error)
#     elif check_data("ErrorMessage", response_data):
#         error = response_data["ErrorMessage"]
#     elif check_data("Message", response_data):
#         error = response_data["Message"]
#     elif check_data("Data", response_data):
#         error = response_data["Data"]["ErrorMessage"]
#     elif check_data("ErrorMessage", response_data["Data"]):
#         error = response_data["Data"]["ErrorMessage"]
#     else:
#         error = "An Error has occurred. API response: " + response.text
#     raise Exception(error)


# # Call API Function



# # Initiate Payment endpoint Function
# def initiate_payment(initiatepay_request):
#     api_url = base_url + "/v2/InitiatePayment"
#     initiatedpay_response = call_api(api_url, api_key, initiatepay_request).json()
#     payment_methods = initiatedpay_response["Data"]["PaymentMethods"]
#     # Initiate Payment output if successful
#     #print("Payment Methods: ", payment_methods)
#     return payment_methods


# Execute Payment endpoint Function
# def execute_payment(executepay_request):
#     api_url = base_url + "/v2/ExecutePayment"
#     executepay_response = call_api(api_url, api_key, executepay_request).json()
#     invoice_id = executepay_response["Data"]["InvoiceId"]
#     invoice_url = executepay_response["Data"]["PaymentURL"]
#     # Execute Payment output if successful
#     print("InvoiceId: ", invoice_id,
#           "\nInvoiceURL: ", invoice_url)
#     return invoice_id, invoice_url



# Test Environment
# base_url = "https://apitest.myfatoorah.com"
# api_key = "MyTokenKey"  # Test token value to be placed here: https:#myfatoorah.readme.io/docs/test-token

# Live Environment
# base_url = "https:#api.myfatoorah.com"
# api_key = "mytokenvalue" #Live token value to be placed here: https:#myfatoorah.readme.io/docs/live-token


# Initaite Payment request data
# initiatepay_request = {
#                     "InvoiceAmount": 100,
#                     "CurrencyIso": "KWD"
#                     }


# try:
    # Getting the value of payment Method Id
    # payment_method = initiate_payment(initiatepay_request)

    # # Creating a simplified list for payment methods
    # payment_method_list = []
    # for item in range(len(payment_method)):
    #     if payment_method[item]["IsDirectPayment"] == False:
    #         y = [payment_method[item].get(key) for key in ["PaymentMethodEn", "PaymentMethodId"]]
    #         payment_method_list.append(y)
    # print(payment_method_list)


    # Get the payment method key.
    # while True:
    #     payment_method_id = input("Kindly enter the number equivalent to the required payment method: ")
    #     try:
    #         if int(payment_method_id) in [el[1] for el in payment_method_list]:
    #             break
    #         else:
    #             print("Kindly enter a correct payment method id")
    #     except:
    #         print("The input must be a number")

    # Based on the initiate payment response, we select the value of reference number to choose payment method

    # Execute Payment Request
    # executepay_request = {
    #                      "paymentMethodId" : payment_method_id,
    #                      "InvoiceValue"    : 50,
    #                      "CallBackUrl"     : "https://example.com/callback.php",
    #                      "ErrorUrl"        : "https://example.com/callback.php",
                    # Fill optional data
                         #"CustomerName"       : "fname lname",
                         #"DisplayCurrencyIso" : "KWD",
                         #"MobileCountryCode"  : "+965",
                         #"CustomerMobile"     : "1234567890",
                         #"CustomerEmail"      : "email@example.com",
                         #"Language"           : "en", #or "ar"
                         #"CustomerReference"  : "orderId",
                         #"CustomerCivilId"    : "CivilId",
                         #"UserDefinedField"   : "This could be string, number, or array",
                         #"ExpiryDate"         : "", #The Invoice expires after 3 days by default. Use "Y-m-d\TH:i:s" format in the "Asia/Kuwait" time zone.
                         #"SourceInfo"         : "Pure PHP", #For example: (Laravel/Yii API Ver2.0 integration)
                         #"CustomerAddress"    : "customerAddress",
                         #"InvoiceItems"       : "invoiceItems",
                    # }

#     execute_payment(executepay_request)
# except:
#     ex_type, ex_value, ex_traceback = sys.exc_info()
#     print("Exception type : %s " % ex_type.__name__)
#     print("Exception message : %s" % ex_value)