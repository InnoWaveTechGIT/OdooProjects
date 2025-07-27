from odoo import http
from odoo.http import request
from odoo.http import Response
from datetime import datetime
import json
from math import ceil
from odoo.addons.mazaady_doworks.controllers.login import validate_token
from odoo.exceptions import AccessError, ValidationError, UserError, MissingError
from . base_controller import BaseController

class AccountPaymentController(BaseController):
    def get_user_id(self):
        auth_header = request.httprequest.headers.get('Authorization')
        token = auth_header.split(" ")[1]
        valid_api_key = request.env["res.users.apikeys"]._check_credentials(scope='api', key=token)
        api_key_user = request.env["res.users"].sudo().browse(int(valid_api_key))
        return api_key_user

    @validate_token
    @BaseController.route('/api/payment/action', type='json', auth='none', methods=['POST'], csrf=False)
    def PaymentAction(self, **kwargs):       
        user_id = kwargs.get('user_id')
        payment_id = kwargs.get('odoo_payment_id')
        action_type = int(kwargs.get('action_type'))
        company_id = int(kwargs.get('company_id'))

        if not user_id or not payment_id or not action_type or not company_id:
            error_message = f"user_id, payment_id, action_type and company_id are required."
            raise KeyError(error_message)        
        
        if action_type not in [1,2]:
            error_message = f"wrong action_type value."
            raise KeyError(error_message)
                
        partner_id = request.env['res.partner'].sudo().search([('subID', '=', user_id), ('company_id', '!=', False), ('company_id', '=', company_id)], limit=1)
        if not partner_id:
            error_message = f"user_id not found."
            raise MissingError(error_message) 
                
        card_id = request.env['loyalty.card'].sudo().search([('partner_id', '=', partner_id.id)], limit=1)
        if card_id:
            payment = request.env['account.payment'].sudo().search([('id', '=', payment_id), ('partner_id', '=', partner_id.id)]) 
            history_payment = request.env['loyalty.history'].sudo().search([('card_id', '=', card_id.id), 
                                                                            ('order_model', '=', 'account.payment'), ('order_id', '=', payment.id)]) 
            if not payment or not history_payment:
                error_message = f"payment_id."
                raise MissingError(error_message)                                     
            else:
                if action_type == 1:
                    # if payment.state in ['draft','in_process']:
                    if payment.state in ['draft']:
                        history_payment.with_user(self.get_user_id()).sudo().write({'withdraw_request': 0.0, 'used': payment.amount}) 
                        # payment.with_user(self.get_user_id()).sudo().action_post()                      
                        payment.with_user(self.get_user_id()).sudo().action_validate()                      
                    else:  
                        error_message = f"can not confirm payment. payment status is {payment.state}"
                        raise UserError(error_message)                
                                     
                elif action_type == 2:
                    # if payment.state in ['draft','in_process']:
                    if payment.state in ['draft']:
                        history_payment.with_user(self.get_user_id()).sudo().write({'cancelled_amount': history_payment.withdraw_request, 'withdraw_request': 0.0}) 
                        payment.with_user(self.get_user_id()).sudo().action_cancel()                      
                    else:  
                        error_message = f"can not confirm payment. payment status is {payment.state}"
                        raise UserError(error_message)                
                                        
                return {'status': 200, 
                        'message': 'payment confirmed successfully.' if action_type == 1 else 'payment canceled successfully.', 
                        'user_id': user_id,
                        'odoo_payment_id': payment_id,
                        }                      
        else:
            error_message = f"No Wallet found."
            raise MissingError(error_message)         
        
    @validate_token
    @http.route('/api/payments/withdraw-requests', type='http', auth='public', methods=['GET'], csrf=False)
    def get_withdraw_requests(self, user_id=None, company_id=None, from_date=None, to_date=None, page_number=None, page_size=None, sort_by=None, **kwargs):        
        if not user_id or not company_id:       
            error_message = f"user_id and company_id are required."
            raise KeyError(error_message)         
                
        partner_id = request.env["res.partner"].sudo().search([('subID', '=', user_id), ('company_id', '!=', False), ('company_id', '=', int(company_id))], limit=1)
        if not partner_id.exists():
            return Response(
                json.dumps({'status': 404, 'message': 'user_id not found.'}),
                status=404,
                content_type='application/json'
            )
        
        card_id = request.env['loyalty.card'].sudo().search([('partner_id', '=', partner_id.id)], limit=1)
        if card_id:
            
            page_number = int(page_number) if page_number else 1
            page_size = int(page_size) if page_size else 30
            sort_by = 'asc' if not sort_by else sort_by
            if sort_by == 'desc':
                order = 'id DESC'   
            else:
                order = 'id ASC'
            if page_number < 1:
                page_number = 1
            if page_size < 1:
                page_size = 30
            offset = (page_number - 1) * page_size
            data = []
            try:
                from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
                to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
            except:
                return Response(
                    json.dumps({'status': 400, 'message': 'Date format not valid.'}),
                    status=400,
                    content_type='application/json'
                )                
            withdraw_request_ids = request.env['loyalty.history'].sudo().search([('card_id', '=', card_id.id), ('withdraw_request', '>', 0.0),
                                                                                 ('description', '=', 'wallet_withdraw_request')])
            if from_date:
                withdraw_request_ids = withdraw_request_ids.filtered(lambda x: x.create_date.date() >= from_date)
            if to_date:
                withdraw_request_ids = withdraw_request_ids.filtered(lambda x: x.create_date.date() <= to_date)                
            total_lines = len(withdraw_request_ids)
            total_pages = ceil(total_lines / page_size)
            card_withdraw_request_ids_ids = request.env['loyalty.history'].sudo().search([('id', 'in', withdraw_request_ids.ids)], limit=page_size, offset=offset, order=order)
            for line in card_withdraw_request_ids_ids:
                data += [{
                    'description': str(line.description),
                    'transaction_date': str(str(line.create_date)[:16]),
                    'amount': str(line.withdraw_request),
                    'odoo_payment_id': str(line.order_id),
                    'status': str(line.status) if line.status else '',
                }]

            result = {
                'status': 200,
                'result': {
                    'user_id': user_id,
                    'withdraw_requests': data,
                    'pagination': {
                        'current_page': page_number,
                        'page_size': page_size,
                        'total_activites': total_lines,
                        'total_pages': total_pages,
                        'has_next': page_number < total_pages,
                        'has_previous': page_number > 1
                    }                    
                }
            }
            return Response(
                json.dumps(result),
                content_type='application/json'
            )     
        else:
            return Response(
                json.dumps({'status': 404, 'message': 'No Wallet found.'}),
                status=404,
                content_type='application/json'
            )               