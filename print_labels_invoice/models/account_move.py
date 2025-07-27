from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def report_invoice_label_action(self):
        return self.env.ref('print_labels_invoice.report_invoice_label_action').report_action(self)
