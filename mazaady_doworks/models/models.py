
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import json        

class loyaltyCard(models.Model):
    _inherit = 'loyalty.card'

    blocked_balance = fields.Float('', compute='_compute_points_balance', store=True)
    blocked_deposit_balance = fields.Float('', compute='_compute_points_balance', store=True)
    points = fields.Float(compute='_compute_points_balance', store=True)

    @api.depends('history_ids', 'history_ids.issued', 'history_ids.used', 'history_ids.withdraw_request')
    def _compute_points_balance(self):
        status = ''
        for card in self:
            card.blocked_deposit_balance = sum(card.history_ids.mapped("deposit_request"))    
            card.blocked_balance = sum(card.history_ids.mapped("withdraw_request"))    
            card.points = sum(card.history_ids.mapped("issued")) - sum(card.history_ids.mapped("used")) - sum(card.history_ids.mapped("withdraw_request"))           
        for line in self.history_ids:
            if line.order_model == 'sale.order':
                sale_order_id = self.env['sale.order'].sudo().search([('id', '=', line.order_id)], limit=1)
                if sale_order_id.confirmed:
                    status = 'Confirmed'
                else:
                    status = sale_order_id.state
            elif line.order_model == 'account.payment':
                status = self.env['account.payment'].sudo().search([('id', '=', line.order_id)], limit=1).state  
            line.write({'status': status if status else ''})

    def action_loyalty_update_balance(self):
        pass
        # return {
        #     'name': _("Update Balance"),
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'res_model': 'loyalty.card.update.balance',
        #     'target': 'new',
        #     'context': {
        #         'default_card_id': self.id,
        #     },
        # }

class LoyaltyHistory(models.Model):
    _inherit = 'loyalty.history'

    order_id = fields.Many2oneReference(string='Ref.', model_field='order_model', readonly=True)
    transaction_date = fields.Date('')
    withdraw_request = fields.Float('')
    deposit_request = fields.Float('')
    blocked_deposit_balance = fields.Float('')
    cancelled_amount = fields.Float('')
    status = fields.Char('')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # @api.constrains('subID')
    # def check_subID(self):
    #     for rec in self:
    #         if rec.subID:
    #             if len(self.search([("subID", "=", rec.subID), ('company_id', '!=', False), ('company_id', '=', rec.company_id.id)])) > 1:
    #                 raise ValidationError("Sub ID already exists.") 

    subID = fields.Char('Sub ID')
    shipping_company = fields.Boolean('')

class SaleSubscriptionPlan(models.Model):
    _inherit = 'sale.subscription.plan'

    billing_period_unit = fields.Selection(selection_add=[('day', 'Days')], ondelete={'day': 'cascade'},)

class ProductTemplate(models.Model):
    _inherit = 'product.template'    

    subscription_unit = fields.Selection([('day', 'Days'), ("week", "Weeks"), ("month", "Months"), ('year', 'Years')], string="Subscription Unit", default='')
    is_contract = fields.Boolean('')
    is_commission = fields.Boolean('')
    seller_id = fields.Many2one('res.partner')
    mazaady_product_id = fields.Char('')    

class AccountJournal(models.Model):
    _inherit = 'account.journal'    

    journal_type = fields.Selection([('subscription_invoice', 'Subscription Invoice'), ("deal_invoice", "Deal Invoice")], string="Journal Type", default='')

class AccountPayment(models.Model):
    _inherit = 'account.payment'     
    
    ref_model = fields.Char('')
    ref_id = fields.Char('')

    def action_validate(self):
        card_id = self.env['loyalty.card'].sudo().search([('partner_id', '=', self.partner_id.id)], limit=1)
        if card_id and self.ref_model and self.ref_id:
            history_payment = self.env['loyalty.history'].sudo().search([('card_id', '=', card_id.id), ('description', '=', self.memo),
                                                                    ('order_model', '=', self.ref_model), ('order_id', '=', self.ref_id)]) 
            if history_payment:
                history_payment.sudo().write({'withdraw_request': 0.0, 'used': self.amount})

        history_payment_provided = self.env['loyalty.history'].sudo().search([ #('card_id', '=', provided_card_id.id), 
                                                                        ('order_model', '=', 'sale.order'), ('order_id', '=', self.ref_id),
                                                                        ('deposit_request', '=', self.amount)]) 
        if history_payment_provided:
            history_payment_provided.sudo().write({'issued': history_payment_provided.deposit_request, 'deposit_request': 0.0})                
        res = super(AccountPayment, self).action_validate()
        return res 

    def action_cancel(self):
        card_id = self.env['loyalty.card'].sudo().search([('partner_id', '=', self.partner_id.id)], limit=1)
        if card_id and self.ref_model and self.ref_id:
            history_payment = self.env['loyalty.history'].sudo().search([('card_id', '=', card_id.id), ('description', '=', self.memo),
                                                                    ('order_model', '=', self.ref_model), ('order_id', '=', self.ref_id)]) 
            if history_payment:
                # history_payment.sudo().write({'cancelled_amount': history_payment.withdraw_request, 'withdraw_request': 0.0}) 
                history_payment.sudo().unlink()
        
        history_payment_provided = self.env['loyalty.history'].sudo().search([ #('card_id', '=', provided_card_id.id), 
                                                                        ('order_model', '=', 'sale.order'), ('order_id', '=', self.ref_id),
                                                                        ('deposit_request', '=', self.amount)]) 
        if history_payment_provided:
            history_payment_provided.sudo().unlink()                
        res = super(AccountPayment, self).action_cancel()
        return res           