from odoo import http, models, fields, _
from odoo.exceptions import UserError
import ast
import logging
import pprint
from odoo import http
from odoo.http import request
import json
import werkzeug
import requests

class overridesds(http.Controller):
    @http.route('/shop/myfatoora/payment/', type='http', auth="public", methods=['POST'], csrf=False)
    def _payment_myfatoora(self, **kw):
        print('kw >>>>>>>>'  , kw)
        initiate_payment = request.env['payment.provider'].initiate_payment(kw.get('Environment'))
        if initiate_payment:
            if initiate_payment.get('ValidationErrors'):
                return request.render("payment_myfatoora.initiate_payment",
                                      {"error": initiate_payment.get('ValidationErrors')[0].get('Error'),
                                       })
        else:
            return request.render("payment_myfatoora.wrong_configuration",
                                  )
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        payment_methods = initiate_payment['Data']['PaymentMethods']
        CustomerReference = kw.get("CustomerReference")
        CustomerReference = CustomerReference.split('-')
        CustomerReference = CustomerReference[0]
        CustomerReference = CustomerReference[1:]
        CustomerReference = int(CustomerReference)
        return request.render("payment_myfatoora.myfatoora_card",
                              {'CustomerName': kw.get("CustomerName"),
                               'InvoiceValue': kw.get("InvoiceValue"),
                               'CustomerBlock': kw.get("CustomerBlock"),
                               'CustomerStreet': kw.get("CustomerStreet"),
                               'CustomerHouseBuildingNo': kw.get("CustomerHouseBuildingNo"),
                               'CustomerCivilId': kw.get("CustomerCivilId"),
                               'CustomerAddress': kw.get("CustomerAddress"),
                               'CustomerReference': kw.get("CustomerReference"),
                               'CountryCodeId': kw.get("CountryCodeId"),
                               'CustomerMobile': kw.get("CustomerMobile"),
                               'CustomerEmail': kw.get("CustomerEmail"),
                               'DisplayCurrencyId': kw.get("DisplayCurrencyId"),
                               'SendInvoiceOption': kw.get("SendInvoiceOption"),
                               'CallBackUrl': base_url +'/payment/callback/' +str(CustomerReference),
                               'payment_methods': payment_methods,
                               "Environment": kw.get("Environment"),
                               "ErrorUrl": 'https://www.alnasaem.com/payment/error',

                               })

    @http.route(['/myfatoora/process'], type='http', auth="public", csrf=False)
    def payment_process(self, **post):
        try:
            initiate_payment = request.env['payment.provider'].initiate_payment(post.get('Environment'))
            payment_methods = initiate_payment['Data']['PaymentMethods']
            DisplayCurrencyIso = ''
            for method in payment_methods:
                if method['PaymentMethodId'] == int(post['PaymentMethodId']):
                    DisplayCurrencyIso = method['CurrencyIso']
            currency_id = request.env['res.currency'].search([('name', '=', post.get('DisplayCurrencyId'))])
            initiate_payment_currency_id = request.env['res.currency'].search(
                [('name', '=', DisplayCurrencyIso)])
            if not initiate_payment_currency_id:
                return request.render("payment_myfatoora.error_page_currency", {"Currency": DisplayCurrencyIso,
                                                                                })
            customer = request.env['res.partner'].search([('name', '=', post.get('CustomerName'))])
            if currency_id.id != initiate_payment_currency_id.id:
                if customer.company_id:
                    company = customer.company_id
                else:
                    company = request.env.company

                amount = currency_id._convert(float(post.get('InvoiceValue')), initiate_payment_currency_id,
                                            company,
                                            date.today())
            else:
                amount = float(post.get('InvoiceValue'))

            if post.get('Environment') == 'test':
                baseURL = "https://apitest.myfatoorah.com"
            else:
                baseURL = "https://api.myfatoorah.com"
            provider = request.env['payment.provider'].sudo().search([('code', '=', 'myfatoora')])
            token = provider.sudo().token
            url = baseURL + "/v2/ExecutePayment"
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            CustomerReference = post.get("CustomerReference")
            CustomerReference = CustomerReference.split('-')
            CustomerReference = CustomerReference[0]
            CustomerReference = CustomerReference[1:]
            CustomerReference = int(CustomerReference)
            payload = {"PaymentMethodId": post['PaymentMethodId'],
                    "CustomerName": post['CustomerName'],
                    "MobileCountryCode": '',
                    "CustomerMobile": post['CustomerMobile'],
                    "CustomerEmail": post['CustomerEmail'],
                    "InvoiceValue": amount,
                    "DisplayCurrencyIso": DisplayCurrencyIso,
                    "CallBackUrl":  base_url +'/payment/callback/' +str(CustomerReference),
                    "ErrorUrl": 'https://www.alnasaem.com/payment/error' ,
                    "Language": "en",
                    "CustomerReference": post['CustomerReference'],
                    "CustomerCivilId": post['CustomerCivilId'],
                    "UserDefinedField": "Custom field",
                    "ExpireDate": "",
                    "CustomerAddress": {"Block": post['CustomerBlock'],
                                        "Street": post['CustomerStreet'],
                                        "HouseBuildingNo": post['CustomerHouseBuildingNo'],
                                        "Address": post['CustomerAddress'],
                                        "AddressInstructions": ""}}
        except UserError as e:
            raise UserError(_(e))
        try:
            headers = {'Content-Type': "application/json", 'Authorization': "bearer " + token}
            response = requests.request("POST", url, data=str(payload).encode('utf-8'), headers=headers)
            response = json.loads(response.text)
            if response.get('ValidationErrors'):
                ValidationErrors = response['ValidationErrors']
                for error in ValidationErrors:
                    return request.render("payment_myfatoora.error_page_currency_validation",
                                          {"Error": error.get('Error'),
                                           })

            return werkzeug.utils.redirect(response['Data']['PaymentURL'])
        except UserError as e:
            raise UserError(_(e))