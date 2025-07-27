from odoo import api, fields, models, tools, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    def print_bill(self):
        return self.env.ref('arados_purchase_reports.purchase_invoice_report_temp123').report_action(self)

    def print_refund_1987(self):
        return self.env.ref('arados_purchase_reports.purchase_return_report_temp').report_action(self)
