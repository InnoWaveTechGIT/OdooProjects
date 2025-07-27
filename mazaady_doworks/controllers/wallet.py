from odoo import http
from odoo.http import request
from odoo.http import Response
from datetime import datetime
import json
from math import ceil
from odoo.addons.mazaady_doworks.controllers.login import validate_token
from odoo.exceptions import AccessError, ValidationError, UserError, MissingError
from . base_controller import BaseController

# class WalletController(http.Controller):
class WalletController(BaseController):
    def get_user_id(self):
        auth_header = request.httprequest.headers.get('Authorization')
        token = auth_header.split(" ")[1]
        valid_api_key = request.env["res.users.apikeys"]._check_credentials(scope='api', key=token)
        api_key_user = request.env["res.users"].sudo().browse(int(valid_api_key))
        return api_key_user

    @validate_token
    @BaseController.route('/api/wallets/register', type='json', auth='none', methods=['POST'], csrf=False)
    def RegisterWallet(self, **kwargs):
        user_id = kwargs.get('user_id')
        user_name = kwargs.get('user_name')
        user_email = kwargs.get('user_email')
        country_id = kwargs.get('country_id')
        shipping_company = int(kwargs.get('shipping_company'))
        company_id = int(kwargs.get('company_id'))

        if not user_id or not user_name or not user_email or not company_id:
            error_message = f"user_id, user_name, user_email, country_id and company_id are required."
            raise KeyError(error_message)        
        customer_exist = request.env['res.partner'].sudo().search([('subID', '=', user_id), ('name', '=', user_name), ('email', '=', user_email),
                                                                   ('company_id', '!=', False), ('company_id', '=', company_id)], limit=1)
        if not customer_exist:
            partner_id = request.env['res.partner'].with_user(self.get_user_id()).with_context(mail_create_nosubscribe=False).with_company(company_id).sudo().create({
                                                                    'name': user_name,
                                                                    'subID': user_id,
                                                                    'email': user_email,
                                                                    'company_id': self.get_user_id().company_id.id,
                                                                    'customer_rank': 1,
                                                                    'type': 'contact',
                                                                    'country_id': country_id,
                                                                    'shipping_company': shipping_company,
                                                                    'company_id': company_id,
                                                                    'user_id': self.get_user_id().id,
                                                                })
            partner_id.sudo().message_subscribe([self.get_user_id().id])
            program_id = request.env['loyalty.program'].sudo().search([('name', '=', 'e-Wallet'), ('program_type', '=', 'ewallet'),
                                                                       ('company_id', '!=', False), ('company_id', '=', company_id)], limit=1)
            if program_id:
                card_id = request.env['loyalty.card'].with_user(self.get_user_id()).sudo().with_context(action_no_send_mail=True).create({
                        'program_id': program_id.id,
                        'partner_id': partner_id.id,
                    })                    
            return {'status': 200, 
                    'message': 'New customer created successfully.', 
                    'user_id': user_id,
                    'odoo_partner_id': partner_id.id,
                    }
        else:
            program_id = request.env['loyalty.program'].sudo().search([('name', '=', 'e-Wallet'), ('program_type', '=', 'ewallet'),
                                                                       ('company_id', '!=', False), ('company_id', '=', company_id)], limit=1)
            if program_id:
                exist_card_id = request.env['loyalty.card'].sudo().search([('partner_id', '=', customer_exist.id)], limit=1)
                if not exist_card_id:
                    card_id = request.env['loyalty.card'].with_user(self.get_user_id()).sudo().with_context(action_no_send_mail=True).create({
                            'program_id': program_id.id,
                            'partner_id': customer_exist.id,
                        })                    
                    return {'status': 200, 
                            'message': 'New customer created successfully.', 
                            'user_id': user_id,
                            'odoo_partner_id': customer_exist.id,
                            }            
                error_message = f"Customer already exist."
                raise UserError(error_message)

    @validate_token
    @BaseController.route('/api/wallets/update', type='json', auth='none', methods=['POST'], csrf=False)
    def UpdateUserInfo(self, **kwargs):
        user_id = kwargs.get('user_id')
        user_name = kwargs.get('user_name')
        user_email = kwargs.get('user_email')
        company_id = int(kwargs.get('company_id'))

        if not user_id or not company_id:
            error_message = f"user_id, user_name and company_id are required."
            raise KeyError(error_message)        
        customer_exist = request.env['res.partner'].sudo().search([('subID', '=', user_id), ('company_id', '!=', False), ('company_id', '=', company_id)], limit=1)
        if not customer_exist:
            error_message = f"user_id not found."
            raise MissingError(error_message)
        else:
            customer_exist.with_user(self.get_user_id()).sudo().write({
                'name': user_name if user_name else customer_exist.name,
                'email': user_email if user_email else customer_exist.email,
                })                    
            return {'status': 200, 
                    'message': 'Customer data updated successfully.', 
                    'user_id': user_id,
                    }
            
    @validate_token
    @BaseController.route('/api/wallets/transaction', type='json', auth='none', methods=['POST'], csrf=False)
    def WalletTransaction(self, **kwargs):       
        user_id = kwargs.get('user_id')
        tranAmount = float(kwargs.get('amount')) if kwargs.get('amount') else 0.0
        transaction_type = kwargs.get('type')
        company_id = int(kwargs.get('company_id'))
        
        if transaction_type == 'deposit':
            tranType = 0  
        elif transaction_type == 'withdraw':
            tranType = 1 
        else:
            # return {'status': 'failed', 'message': 'Transaction type not valid.'}
            error_message = f"Transaction type not valid."
            raise ValueError(error_message)        
        if not user_id or not tranAmount or not transaction_type or tranAmount == 0.0 or not company_id:
            # return {'status': 'failed', 'message': 'user_id, amount and type are required for Wallet Transaction.'}
            error_message = f"user_id, amount, type and company_id are required for Wallet Transaction."
            raise KeyError(error_message)
        
        partner_id = request.env['res.partner'].sudo().search([('subID', '=', user_id), ('company_id', '!=', False), ('company_id', '=', company_id)], limit=1)
        if not partner_id:
            # return {'status': 'failed', 'message': 'user_id not found.'}
            error_message = f"user_id not found."
            raise MissingError(error_message)        
        card_id = request.env['loyalty.card'].sudo().search([('partner_id', '=', partner_id.id)], limit=1)
        if card_id:
            # try:
            if tranAmount < 0:
                # return {'status': 'failed', 'message': 'New Balance should be positive.'}
                error_message = f"New Balance should be positive."
                raise KeyError(error_message)                
            if tranAmount > card_id.points and tranType == 1:
                # return {'status': 'failed', 'message': 'Insufficient Balance.'} 
                error_message = f"Insufficient Balance."
                raise KeyError(error_message)                 
            values = {
                        'partner_id': partner_id.id,
                        'amount': tranAmount,
                        'payment_type': 'inbound' if tranType == 0 else 'outbound',
                        'memo': "wallet_deposit_transaction" if tranType == 0 else "wallet_withdraw_request",
                        'ref_model': 'account.payment',
                        # 'ref_id':  payment.id,                        
                    }
            payment = request.env['account.payment'].with_company(company_id).with_user(self.get_user_id()).sudo().create(values) 
            payment.with_user(self.get_user_id()).sudo().write({'ref_id': payment.id})                                            
            if tranType == 0:
                # payment.action_post()
                payment.action_validate()
            request.env['loyalty.history'].with_user(self.get_user_id()).sudo().create({
                                                    'card_id': card_id.id,
                                                    'description': "wallet_deposit_transaction" if tranType == 0 else "wallet_withdraw_request",
                                                    # 'used': tranAmount if tranType == 1 else 0,
                                                    'withdraw_request': tranAmount if tranType == 1 else 0,
                                                    'issued': tranAmount if tranType == 0 else 0,
                                                    'order_model': 'account.payment',
                                                    'order_id': payment.id,                                                        
                                                    'status': payment.state,                                                        
                                                })

            return {'status': 200, 
                    'message': 'Customer balance updated successfully.' if tranType == 0 else 'Withdraw request created successfully.', 
                    'user_id': user_id,
                    'odoo_payment_id': payment.id,
                    }
        
            # except Exception as e:
            #     return {'status': 'failed', 'message': str(e)} 
        else:
            # return {'status': 'failed', 'message': 'No Wallet found.', 'user_id': user_id}
            error_message = f"No Wallet found."
            raise MissingError(error_message)         

    @validate_token
    @http.route('/api/wallets/balance', type='http', auth='public', methods=['GET'], csrf=False)
    def get_wallet_balance(self, user_id=None, company_id=None, **kwargs):                
        if not user_id or not company_id:
            return Response(
                json.dumps({'status': 422, 'message': 'user_id and company_id are required.'}),
                status=422,
                content_type='application/json'
            )
                
        partner_id = request.env["res.partner"].sudo().search([('subID', '=', user_id), ('company_id', '!=', False), ('company_id', '=', int(company_id))], limit=1)
        if not partner_id.exists():
            return Response(
                json.dumps({'status': 404, 'message': 'related customer not found.'}),
                status=404,
                content_type='application/json'
            )        

        card_id = request.env['loyalty.card'].sudo().search([('partner_id', '=', partner_id.id)], limit=1)
        if card_id:
            result = {
                'status': 200,
                'result': {
                    'user_id': user_id,
                    'blocked_balance': str(card_id.blocked_balance + card_id.blocked_deposit_balance),
                    'available_balance': str(card_id.points)
                }
            }
            return Response(
                json.dumps(result),
                content_type='application/json'
            )     
        else:
            return Response(
                json.dumps({'status': 422, 'message': 'No Wallet found.', 'user_id': user_id}),
                status=422,
                content_type='application/json'
            )                 
        
    @validate_token
    @http.route('/api/wallets/account-activites', type='http', auth='public', methods=['GET'], csrf=False)
    def get_wallet_transactions(self, user_id=None, company_id=None, from_date=None, to_date=None, page_number=None, page_size=None, sort_by=None, **kwargs):        
        if not user_id or not company_id:
            return Response(
                json.dumps({'status': 422, 'message': 'user_id and company_id are required.'}),
                status=422,
                content_type='application/json'
            )        
                
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
            all_card_history_ids = request.env['loyalty.history'].sudo().search([('card_id', '=', card_id.id)])
            if from_date:
                all_card_history_ids = all_card_history_ids.filtered(lambda x: x.create_date.date() >= from_date)
            if to_date:
                all_card_history_ids = all_card_history_ids.filtered(lambda x: x.create_date.date() <= to_date)                
            total_lines = len(all_card_history_ids)
            total_pages = ceil(total_lines / page_size)
            card_history_ids = request.env['loyalty.history'].sudo().search([('id', 'in', all_card_history_ids.ids)], limit=page_size, offset=offset, order=order)
            for line in card_history_ids:
                data += [{
                    'description': str(line.description),
                    'transaction_date': str(str(line.create_date)[:16]),
                    'deposit': str(line.issued),
                    'withdrow': str(line.used) if line.used else str(line.withdraw_request),
                    'cancelled_amount': str(line.cancelled_amount) if line.cancelled_amount else '',
                    'status': str(line.status) if line.status else '',
                }]

            result = {
                'status': 200,
                'result': {
                    'user_id': user_id,
                    'wallet_transactions': data,
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