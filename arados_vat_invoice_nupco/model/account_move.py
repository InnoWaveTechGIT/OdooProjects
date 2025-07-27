from odoo import models, fields, api
from odoo.fields import Command
class AccountMove(models.Model):
    _inherit = 'account.move'



    discount_amount = fields.Float('Discount Amount' , compute='get_discount_amount')

    def print_vat_invoice(self):
        for rec in self:
            report_template = self.env.ref('arados_vat_invoice_nupco.action_report_vat_invoice_template')
            return report_template.report_action(rec)


    @api.depends('invoice_line_ids')
    def get_discount_amount(self):
        discount =0.0
        for rec in self:
            for line in rec.invoice_line_ids:
                discount += (line.quantity * line.price_unit) * line.discount / 100

            rec.discount_amount = discount
