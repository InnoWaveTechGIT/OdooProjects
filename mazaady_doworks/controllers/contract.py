from odoo import fields, http
from odoo.http import request
from odoo import Command
from dateutil.relativedelta import relativedelta
from odoo.addons.mazaady_doworks.controllers.login import validate_token
from odoo.exceptions import AccessError, ValidationError, UserError, MissingError
from . base_controller import BaseController
    
class ContractController(BaseController):
    def get_user_id(self):
        auth_header = request.httprequest.headers.get('Authorization')
        token = auth_header.split(" ")[1]
        valid_api_key = request.env["res.users.apikeys"]._check_credentials(scope='api', key=token)
        api_key_user = request.env["res.users"].sudo().browse(int(valid_api_key))
        return api_key_user         
        
    @validate_token
    @BaseController.route('/api/Contract/create', type='json', auth='none', methods=['POST'], csrf=False)
    def CreateContract(self, **kwargs):       
        rquested_user_id = kwargs.get('rquested_user_id')
        provided_user_id = kwargs.get('provided_user_id')
        contract_id = kwargs.get('contract_id')
        transaction_amount = float(kwargs.get('transaction_amount'))
        commission_amount = float(kwargs.get('commission_amount'))
        tax_percentage = float(kwargs.get('tax_percentage'))
        description = kwargs.get('description')
        company_id = int(kwargs.get('company_id'))
        service_id = int(kwargs.get('service_id'))
        # tax_amount = float(kwargs.get('tax_amount'))

        # if not rquested_user_id or not provided_user_id or not contract_id or not transaction_amount or not commission_amount or not description or not company_id or not service_id or not tax_amount:
        if not rquested_user_id or not provided_user_id or not contract_id or not transaction_amount or not tax_percentage or not description or not company_id or not service_id:
            # error_message = f"rquested_user_id, provided_user_id, contract_id, transaction_amount, commission_amount, description, company_id, service_id and tax_amount are required."
            error_message = f"rquested_user_id, provided_user_id, contract_id, transaction_amount, tax_percentage, description, company_id and service_id are required."
            raise KeyError(error_message)

        exist_contract_id = request.env['sale.order'].sudo().search([('mazady_contract_id', '=', contract_id), ], limit=1)
        if exist_contract_id:
            error_message = f"contract_id already exist."
            raise UserError(error_message)
                                
        rquested_user_id = request.env['res.partner'].sudo().search([('subID', '=', rquested_user_id), ('company_id', '!=', False),
                                                                     ('company_id', '=', company_id)], limit=1)
        if not rquested_user_id:
            error_message = f"rquested_user_id not found."
            raise MissingError(error_message)

        provided_user_id = request.env['res.partner'].sudo().search([('subID', '=', provided_user_id), ('company_id', '!=', False),
                                                                     ('company_id', '=', company_id)], limit=1)
        if not provided_user_id:
            error_message = f"provided_user_id not found."
            raise MissingError(error_message)
                        
        rquested_card_id = request.env['loyalty.card'].sudo().search([('partner_id', '=', rquested_user_id.id)], limit=1)
        # if not rquested_card_id or transaction_amount + commission_amount + tax_amount > rquested_card_id.points:
        if not rquested_card_id or transaction_amount + commission_amount + (commission_amount * tax_percentage / 100) > rquested_card_id.points:
            error_message = f"Insufficient Balance."
            raise UserError(error_message)

        provided_card_id = request.env['loyalty.card'].sudo().search([('partner_id', '=', provided_user_id.id)], limit=1)
        if not provided_card_id:
            error_message = f"No card found for provided_user_id."
            raise UserError(error_message)
                        
        contract_product_id = request.env['product.product'].sudo().search([('is_contract', '=', True)], limit=1)  
        if not contract_product_id:
            error_message = f"No service found for contract."
            raise UserError(error_message)

        sale_order = request.env['sale.order'].with_user(self.get_user_id()).sudo().create({
                                                                                        'partner_id': rquested_user_id.id,
                                                                                        'seller_id': provided_user_id.id,
                                                                                        'mazady_contract_id': contract_id,
                                                                                        'date_order': fields.Datetime.now(),
                                                                                        'is_contract': True,
                                                                                        'company_id': company_id,
                                                                                        'service_id': service_id,
                                                                                        # 'rquested_payment_id': rquested_payment.id,
                                                                                        # 'provided_payment_id': provided_payment.id,
                                                                                        'transaction_amount': transaction_amount,
                                                                                        'commission_amount': commission_amount,
                                                                                        'tax_percentage': tax_percentage / 100,
                                                                                        # 'tax_amount': 0.00,
                                                                                        'order_line': [Command.create({
                                                                                                                        'product_id': contract_product_id.id,
                                                                                                                        'name': description,
                                                                                                                        'product_uom_qty': 1,
                                                                                                                        # 'price_unit': transaction_amount + tax_amount,
                                                                                                                        'price_unit': transaction_amount,
                                                                                                                        })
                                                                                                        ],
                                                                                        'message_partner_ids': [ 
                                                                                                            Command.link(rquested_user_id.id),
                                                                                                            Command.link(provided_user_id.id),
                                                                                                        ],                                                                                                            
                                                                                                        })
        rquested_values = {
                    'partner_id': rquested_user_id.id,
                    # 'amount': transaction_amount + commission_amount + tax_amount,
                    # 'amount': transaction_amount + commission_amount + (commission_amount * tax_percentage / 100),
                    'amount': transaction_amount,
                    'payment_type': 'outbound',
                    'memo': 'contract_withdraw_transaction',
                    'ref_model': 'sale.order',
                    'ref_id':  sale_order.id,
                }        
        rquested_payment = request.env['account.payment'].with_company(company_id).with_user(self.get_user_id()).sudo().create(rquested_values)                                
        request.env['loyalty.history'].with_user(self.get_user_id()).sudo().create({
                                                'card_id': rquested_card_id.id,
                                                # 'description': "contract_withdraw_transaction" + " ( contract_id:" + contract_id + " )",
                                                'description': "contract_withdraw_transaction",
                                                # 'withdraw_request': transaction_amount + commission_amount + tax_amount,
                                                'withdraw_request': transaction_amount + commission_amount + (commission_amount * tax_percentage / 100),
                                                # 'withdraw_request': transaction_amount,
                                                'issued': 0,
                                                'used': 0,
                                                'order_model': 'sale.order',
                                                'order_id': sale_order.id,  
                                                'status': sale_order.state,                                                      
                                            })   
        sale_order.with_user(self.get_user_id()).sudo().write({'rquested_payment_id': rquested_payment.id}) 
        # provided_values = {
        #             'partner_id': provided_user_id.id,
        #             'amount': transaction_amount,
        #             'payment_type': 'inbound',
        #         }        
        # provided_payment = request.env['account.payment'].with_user(self.get_user_id()).sudo().create(provided_values)                                
        request.env['loyalty.history'].with_user(self.get_user_id()).sudo().create({
                                                'card_id': provided_card_id.id,
                                                'description': "contract_deposit_request",
                                                'deposit_request': transaction_amount,
                                                'issued': 0,
                                                'used': 0,                                                
                                                'order_model': 'sale.order',
                                                'order_id': sale_order.id, 
                                                'status': sale_order.state,                                                       
                                            })
        return {'status': 200, 
                'message': 'Contract created successfully.', 
                'rquested_user_id': kwargs.get('rquested_user_id'),
                'provided_user_id': kwargs.get('provided_user_id'),
                'odoo_contract_id': sale_order.id}

    @validate_token
    @BaseController.route('/api/Contract/action', type='json', auth='none', methods=['POST'], csrf=False)
    def ContractConfirm(self, **kwargs):       
        rquested_user_id = kwargs.get('rquested_user_id')
        provided_user_id = kwargs.get('provided_user_id')
        odoo_contract_id = kwargs.get('odoo_contract_id')
        action_type = int(kwargs.get('action_type'))
        company_id = int(kwargs.get('company_id'))
        
        if not rquested_user_id or not provided_user_id or not odoo_contract_id or not action_type or not company_id:
            error_message = f"rquested_user_id, provided_user_id and odoo_contract_id, action_type and company_id are required."
            raise KeyError(error_message)

        if action_type not in [1,2]:
            error_message = f"wrong action_type value."
            raise KeyError(error_message)
                                
        rquested_user_id = request.env['res.partner'].sudo().search([('subID', '=', rquested_user_id), ('company_id', '!=', False),
                                                                     ('company_id', '=', company_id)], limit=1)
        if not rquested_user_id:
            error_message = f"rquested_user_id not found."
            raise MissingError(error_message)

        provided_user_id = request.env['res.partner'].sudo().search([('subID', '=', provided_user_id), ('company_id', '!=', False),
                                                                     ('company_id', '=', company_id)], limit=1)
        if not provided_user_id:
            error_message = f"provided_user_id not found."
            raise MissingError(error_message)
                        
        rquested_card_id = request.env['loyalty.card'].sudo().search([('partner_id', '=', rquested_user_id.id)], limit=1)
        if not rquested_card_id:
            error_message = f"No card found for quested_user_id."
            raise UserError(error_message)
        
        provided_card_id = request.env['loyalty.card'].sudo().search([('partner_id', '=', provided_user_id.id)], limit=1)
        if not provided_card_id:
            error_message = f"No card found for provided_user_id."
            raise UserError(error_message)
                        
        contract_id = request.env['sale.order'].sudo().search([('id', '=', odoo_contract_id), 
                                                               ('partner_id', '=', rquested_user_id.id), ('seller_id', '=', provided_user_id.id),], limit=1)  
        if not contract_id:
            error_message = f"No contract found."
            raise UserError(error_message)

        rquested_payment = request.env['account.payment'].sudo().search([('id', '=', contract_id.rquested_payment_id.id), ('partner_id', '=', rquested_user_id.id)]) 
        history_payment = request.env['loyalty.history'].sudo().search([('card_id', '=', rquested_card_id.id), 
                                                                        ('order_model', '=', 'sale.order'), ('order_id', '=', contract_id.id)]) 
        history_payment_provided = request.env['loyalty.history'].sudo().search([('card_id', '=', provided_card_id.id), 
                                                                        ('order_model', '=', 'sale.order'), ('order_id', '=', contract_id.id),
                                                                        ('deposit_request', '>', 0.00)])         
        try:
            if action_type == 1:
                if not rquested_payment or not history_payment:
                    error_message = f"payment not found for this contract."
                    raise MissingError(error_message)                                     
                else:
                    # if rquested_payment.state in ['draft','in_process']:
                    if rquested_payment.state in ['draft']:
                        history_payment.with_user(self.get_user_id()).sudo().write({'used': history_payment.withdraw_request ,'withdraw_request': 0.0}) 
                        # rquested_payment.with_user(self.get_user_id()).sudo().action_post()                      
                        rquested_payment.with_user(self.get_user_id()).sudo().action_validate()                      
                    else:  
                        error_message = f"can not confirm payment. payment status is {rquested_payment.state}"
                        raise UserError(error_message)                

                provided_values = {
                            'partner_id': provided_user_id.id,
                            'amount': contract_id.transaction_amount,
                            'payment_type': 'inbound',
                            'memo': 'contract_deposit_transaction',
                            'ref_model': 'sale.order',
                            'ref_id':  contract_id.id,                            
                        }    
                provided_payment = request.env['account.payment'].with_company(company_id).with_user(self.get_user_id()).sudo().create(provided_values) 
                # provided_payment.with_user(self.get_user_id()).sudo().action_post()                               
                provided_payment.with_user(self.get_user_id()).sudo().action_validate()                               
                request.env['loyalty.history'].with_user(self.get_user_id()).sudo().create({
                                                        'card_id': provided_card_id.id,
                                                        'description': "contract_deposit_transaction",
                                                        'withdraw_request': 0,
                                                        'issued': contract_id.transaction_amount,
                                                        'used': 0,                                                
                                                        'order_model': 'sale.order',
                                                        'order_id': contract_id.id, 
                                                        'status': contract_id.state,                                                        
                                                    })
                history_payment_provided.unlink()
                contract_id.with_user(self.get_user_id()).sudo().write({'provided_payment_id': provided_payment.id, 'confirmed': True}) 

                commission_product_id = request.env['product.product'].sudo().search([('is_commission', '=', True)], limit=1) 
                tax_id = request.env['account.tax'].sudo().search([('amount', '=', contract_id.tax_percentage * 100), ('company_id', '=', company_id)], limit=1)
                if not commission_product_id or not tax_id:
                    error_message = f"No service found for commission and tax."
                    raise UserError(error_message)
                commission_sale_order = request.env['sale.order'].with_user(self.get_user_id()).sudo().create({
                                                                                                'partner_id': rquested_user_id.id,
                                                                                                'seller_id': provided_user_id.id,
                                                                                                'mazady_contract_id': contract_id,
                                                                                                'date_order': fields.Datetime.now(),
                                                                                                # 'is_contract': True,
                                                                                                'company_id': company_id,
                                                                                                'transaction_amount': contract_id.transaction_amount,
                                                                                                'commission_amount': contract_id.commission_amount,
                                                                                                'order_line': [Command.create({
                                                                                                                                'product_id': commission_product_id.id,
                                                                                                                                'tax_id': [(6, 0, [tax_id[0].id])],
                                                                                                                                'name': 'commission',
                                                                                                                                'product_uom_qty': 1,
                                                                                                                                'price_unit': contract_id.commission_amount,
                                                                                                                                })
                                                                                                                ],
                                                                                                'message_partner_ids': [ 
                                                                                                                    Command.link(rquested_user_id.id),
                                                                                                                    Command.link(provided_user_id.id),
                                                                                                                ],                                                                                                            
                                                                                                                })
                commission_sale_order.with_user(self.get_user_id()).sudo().action_confirm()
                invoicing_wizard = request.env['sale.advance.payment.inv'].with_company(company_id).with_user(self.get_user_id()).sudo().create({
                                                                                    'sale_order_ids': [Command.link(commission_sale_order.id)],
                                                                                    'advance_payment_method': 'delivered',
                                                                                })
                action = invoicing_wizard.with_company(company_id).create_invoices()
                invoice = request.env['account.move'].sudo().browse(action['res_id'])
                journal_id = request.env['account.journal'].sudo().search([('company_id', '=', company_id), ('journal_type', '=', 'deal_invoice')], limit=1)
                if journal_id:
                    invoice.with_user(self.get_user_id()).sudo().write({'journal_id': journal_id.id})                
                invoice.with_user(self.get_user_id()).sudo().action_post()
                domain = [
                    ('partner_id', '=', invoice.partner_id.id),
                    ('state', '=', 'paid'),
                    ('payment_type', '=', 'inbound'),
                    ('is_reconciled', '=', False),
                ]
                payments = request.env['account.payment'].sudo().search(domain)            
                invoice_lines = invoice.line_ids.filtered(lambda line: line.account_id.reconcile and not line.reconciled)
                payment_lines = payments.mapped('move_id.line_ids').filtered(lambda line: line.account_id.reconcile and not line.reconciled)
                lines_to_reconcile = invoice_lines + payment_lines
                if lines_to_reconcile:
                    lines_to_reconcile.with_user(self.get_user_id()).sudo().reconcile()                  
            
            elif action_type == 2:   
                # if rquested_payment.state in ['draft','in_process']:
                if rquested_payment.state in ['draft']:
                    history_payment.with_user(self.get_user_id()).sudo().write({'cancelled_amount': history_payment.withdraw_request, 'withdraw_request': 0.0}) 
                    rquested_payment.with_user(self.get_user_id()).sudo().action_cancel()                      
                    contract_id.with_user(self.get_user_id()).sudo().action_cancel()  
                    history_payment_provided.unlink()                    
                else:  
                    error_message = f"can not cancel payment. payment status is {rquested_payment.state}"
                    raise UserError(error_message) 
            return {'status': 200, 
                    'message': 'contract canceled successfully.' if action_type == 2 else 'contract confirmed successfully.', 
                    'rquested_user_id': kwargs.get('rquested_user_id'),
                    'provided_user_id': kwargs.get('provided_user_id'),
                    'odoo_contract_id': contract_id.id,
                    }
        except:
            error_message = f"Error occured."
            raise MissingError(error_message)         
        