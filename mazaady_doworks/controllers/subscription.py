from odoo import fields, http
from odoo.http import request
from odoo import Command
from dateutil.relativedelta import relativedelta
from odoo.addons.mazaady_doworks.controllers.login import validate_token
from odoo.exceptions import AccessError, ValidationError, UserError, MissingError
from . base_controller import BaseController
    
class SubscriptionController(BaseController):
    def get_user_id(self):
        auth_header = request.httprequest.headers.get('Authorization')
        token = auth_header.split(" ")[1]
        valid_api_key = request.env["res.users.apikeys"]._check_credentials(scope='api', key=token)
        api_key_user = request.env["res.users"].sudo().browse(int(valid_api_key))
        return api_key_user         
        
    @validate_token
    @BaseController.route('/api/subscriptions/create', type='json', auth='none', methods=['POST'], csrf=False)
    def CreateSubscription(self, **kwargs):       
        user_id = kwargs.get('user_id')
        tranaction_amount = float(kwargs.get('price')) # * int(kwargs.get('duration'))
        # tax_percentage = kwargs.get('tax_percentage')
        service_type = kwargs.get('duration_unit')
        quantity = int(kwargs.get('duration'))
        company_id = int(kwargs.get('company_id'))

        if not user_id or not tranaction_amount or not service_type or not quantity or not company_id:
            # return {'status': 'failed', 'message': 'user_id, price, tax_percentage, duration_unit and duration are required.'}
            error_message = f"user_id, price, tax_percentage, duration_unit, duration and company_id are required."
            raise KeyError(error_message)
        
        if service_type not in['day','week','month','year']:
            # return {'status': 'failed', 'message': 'service_type not found.'}
            error_message = f"service_type not found."
            raise MissingError(error_message)
                        
        partner_id = request.env['res.partner'].sudo().search([('subID', '=', user_id), ('company_id', '!=', False), ('company_id', '=', company_id)], limit=1)
        if not partner_id:
            # return {'status': 'failed', 'message': 'user_id not found.'}
            error_message = f"user_id not found."
            raise MissingError(error_message)
                
        card_id = request.env['loyalty.card'].sudo().search([('partner_id', '=', partner_id.id)], limit=1)
        if not card_id or tranaction_amount * quantity > card_id.points:
            # return {'status': 'failed', 'message': 'Insufficient Balance.', 'user_id': user_id}
            error_message = f"Insufficient Balance."
            raise UserError(error_message)
                
        plan_id = request.env['sale.subscription.plan'].sudo().search([('billing_period_unit', '=', service_type)], limit=1)        
        product_id = request.env['product.product'].sudo().search([('subscription_unit', '=', service_type), ('recurring_invoice', '=', True), 
                                                                   ('type', '=', 'service')], limit=1)            
        if service_type == 'day': 
            end_date = (fields.Datetime.now() + relativedelta(days = quantity))  
        elif service_type == 'week': 
            end_date = (fields.Datetime.now() + relativedelta(days = quantity * 7))
        elif service_type == 'month': 
            end_date = (fields.Datetime.now() + relativedelta(months = quantity)) 
        elif service_type == 'year': 
            end_date = (fields.Datetime.now() + relativedelta(months = quantity * 12))  
            
        sale_order = request.env['sale.order'].with_user(self.get_user_id()).sudo().create({
                                                                                        'partner_id': partner_id.id,
                                                                                        'end_date': end_date,
                                                                                        'date_order': fields.Datetime.now(),
                                                                                        'plan_id': plan_id.id,
                                                                                        'is_subscription': True,
                                                                                        'service_type': 'subscription',
                                                                                        'company_id': company_id,
                                                                                        'order_line': [Command.create({
                                                                                                                        'product_id': product_id.id,
                                                                                                                        'name': product_id.name,
                                                                                                                        'product_uom_qty': quantity,
                                                                                                                        'price_unit': tranaction_amount,
                                                                                                                        })
                                                                                                        ],
                                                                                        'message_partner_ids': [ 
                                                                                                            Command.link(partner_id.id),
                                                                                                        ],                                                                                                            
                                                                                                        })      
        sale_order.with_user(self.get_user_id()).sudo().action_confirm()

        invoicing_wizard = request.env['sale.advance.payment.inv'].with_company(company_id).with_user(self.get_user_id()).sudo().create({
                                                                            'sale_order_ids': [Command.link(sale_order.id)],
                                                                            'advance_payment_method': 'delivered',
                                                                        })
        action = invoicing_wizard.with_company(company_id).create_invoices()
        invoice = request.env['account.move'].sudo().browse(action['res_id'])
        journal_id = request.env['account.journal'].sudo().search([('company_id', '=', company_id), ('journal_type', '=', 'subscription_invoice')], limit=1)
        if journal_id:
            invoice.with_user(self.get_user_id()).sudo().write({'journal_id': journal_id.id})
        invoice.with_user(self.get_user_id()).sudo().action_post()
        # action_register_payment = invoice.with_user(self.get_user_id()).sudo().action_force_register_payment()
        # wizard = request.env[action_register_payment['res_model']].with_user(self.get_user_id()).sudo().with_context(action_register_payment['context']).create({})
        # action_create_payment = wizard.with_user(self.get_user_id()).sudo().action_create_payments()
        # payment = request.env['account.payment'].sudo().browse(action_create_payment['res_id'])
        # payment.with_user(self.get_user_id()).sudo().action_validate()
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

        request.env['loyalty.history'].with_user(self.get_user_id()).sudo().create({
                                                'card_id': card_id.id,
                                                # 'description': "wallet_withdraw_transaction_for_subscription" + " ( " + product_id.name + " )",
                                                'description': "wallet_withdraw_transaction_for_subscription",
                                                'used': sale_order.amount_total,
                                                'order_model': 'sale.order',
                                                'order_id': sale_order.id,
                                                'status': sale_order.state, 
                                            })           
        return {'status': 200, 
                'message': 'Subscription created successfully.', 
                'user_id': user_id,
                'odoo_subscription_id': sale_order.id}

    @validate_token
    @BaseController.route('/api/paid-feature/create', type='json', auth='none', methods=['POST'], csrf=False)
    def CreatePaidFeature(self, **kwargs):       
        user_id = kwargs.get('user_id')
        tranaction_amount = float(kwargs.get('price'))
        paid_feature_type = kwargs.get('paid_feature_type')
        company_id = int(kwargs.get('company_id'))
        if not user_id or not tranaction_amount or not paid_feature_type or not company_id:
            error_message = f"user_id, price, paid_feature_type and company_id are required."
            raise KeyError(error_message)
                        
        partner_id = request.env['res.partner'].sudo().search([('subID', '=', user_id), ('company_id', '!=', False), ('company_id', '=', company_id)], limit=1)
        if not partner_id:
            error_message = f"user_id not found."
            raise MissingError(error_message)
                
        card_id = request.env['loyalty.card'].sudo().search([('partner_id', '=', partner_id.id)], limit=1)
        if not card_id or tranaction_amount > card_id.points:
            error_message = f"Insufficient Balance."
            raise UserError(error_message)
                
        plan_id = request.env['sale.subscription.plan'].sudo().search([('billing_period_unit', '=', 'day')], limit=1)        
        product_id = request.env['product.product'].sudo().search([('subscription_unit', '=', 'day'), ('recurring_invoice', '=', True),
                                                                   ('type', '=', 'service')], limit=1)            
        # end_date = (fields.Datetime.now() + relativedelta(days = quantity))
        sale_order = request.env['sale.order'].with_user(self.get_user_id()).sudo().create({
                                                                                        'partner_id': partner_id.id,
                                                                                        # 'end_date': end_date,
                                                                                        'date_order': fields.Datetime.now(),
                                                                                        'plan_id': plan_id.id,
                                                                                        'is_subscription': True,
                                                                                        'service_type': 'paid_feature',
                                                                                        'paid_feature_type': paid_feature_type,
                                                                                        'company_id': company_id,
                                                                                        'order_line': [Command.create({
                                                                                                                        'product_id': product_id.id,
                                                                                                                        'name': product_id.name,
                                                                                                                        'product_uom_qty': 1,
                                                                                                                        'price_unit': tranaction_amount,
                                                                                                                        })
                                                                                                        ],
                                                                                        'message_partner_ids': [ 
                                                                                                            Command.link(partner_id.id),
                                                                                                        ],                                                                                                            
                                                                                                        })      
        sale_order.with_user(self.get_user_id()).sudo().action_confirm()

        invoicing_wizard = request.env['sale.advance.payment.inv'].with_company(company_id).with_user(self.get_user_id()).sudo().create({
                                                                            'sale_order_ids': [Command.link(sale_order.id)],
                                                                            'advance_payment_method': 'delivered',
                                                                        })
        action = invoicing_wizard.with_company(company_id).create_invoices()
        invoice = request.env['account.move'].sudo().browse(action['res_id'])
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

        request.env['loyalty.history'].with_user(self.get_user_id()).sudo().create({
                                                'card_id': card_id.id,
                                                # 'description': "wallet_withdraw_transaction_for_paid_feature" + " ( " + product_id.name + " )",
                                                'description': "wallet_withdraw_transaction_for_paid_feature",
                                                'used': sale_order.amount_total,
                                                'order_model': 'sale.order',
                                                'order_id': sale_order.id,
                                                'status': sale_order.state,
                                            })           
        return {'status': 200, 
                'message': 'Mark Service created successfully.', 
                'user_id': user_id,
                # 'odoo_subscription_id': sale_order.id
                }
    