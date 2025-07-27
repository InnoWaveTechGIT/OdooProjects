from odoo import api, fields, models, tools, _



class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    tags = fields.Many2many('res.partner.category', string='Tags')

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    total_payments = fields.Float(string='Total Payments', compute='_compute_total_payments')
    total_unpayed = fields.Float(string='Total not payed', compute='_compute_unpayed')


    @api.depends('payment_state')
    def _compute_unpayed(self):
        for rec in self:
            total_amount = 0.0
            payments = self.env['account.move'].search([('partner_id' , '<' , rec.partner_id.id)]) # Search for payments related to the invoice
            print('payments >>>> ' , payments)
            for payment in payments:
                if payment.id < rec.id:
                    total_amount += payment.amount_residual
            rec.total_unpayed = total_amount

    @api.depends('payment_state')
    def _compute_total_payments(self):
        for move in self:
            total_amount = 0.0
            total_amount = move.amount_total - move.amount_residual
            move.total_payments = total_amount


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    expiration_date = fields.Char('Expiration Date' )


    # @api.depends('lot_ids')
    # def _get_exp_dates(self):
    #     for rec in self:
    #         exp_dates = [str(lot.lot_id.expiration_date) for lot in rec.sale_line_ids]
    #         rec.expiration_date = ", ".join(exp_dates)
#
