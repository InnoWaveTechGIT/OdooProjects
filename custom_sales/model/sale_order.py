from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"


    is_contract = fields.Boolean(string='Is Contract')
    seller_id = fields.Many2one(
        comodel_name='res.partner',
        string="Seller",
        change_default=True, index=True,
        tracking=1,
        check_company=True)
    mazady_contract_id = fields.Char()
    rquested_payment_id = fields.Many2one('account.payment', string='')
    provided_payment_id = fields.Many2one('account.payment', string='')
    transaction_amount = fields.Float('')
    commission_amount = fields.Float('')
    tax_amount = fields.Float('')
    tax_percentage = fields.Float('')
    service_id = fields.Float('')
    paid_feature_type = fields.Char('')
    confirmed = fields.Boolean(string='')
    service_type = fields.Selection([('subscription', 'Subscription'), ('paid_feature', 'Paid feature'), ], string='')
    deal_total_amount = fields.Float(compute='_compute_deal_total_amount', string='', store=False)
    
    @api.depends('transaction_amount','commission_amount','tax_percentage')
    def _compute_deal_total_amount(self):
        for rec in self:
            rec.deal_total_amount = rec.transaction_amount + rec.commission_amount + (rec.commission_amount * rec.tax_percentage)

    def confirm_contract(self):
        print('Hello From contract')
        pass

    def action_confirm(self):
        # Call the original action_confirm method
        if self.is_contract == True:
            raise ValidationError('The Document type is Contract Please Press Confirm Contract')
        res = super(SaleOrder, self).action_confirm()


        return res
