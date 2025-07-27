from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create_invoice(self):
        for order in self:
            if order.state == 'sale':  # Ensures the order is confirmed
                invoice = order.action_invoice_create()
                # Optionally, you can do more with the invoice here
                # e.g., invoice.action_post() to post it immediately

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        x = self._create_invoices()  # Create the invoice after confirming the sale order
        print('x >>>>>>>>>> ' , x)
        x.action_post()

        self.write({
            'invoice_status' : 'invoiced'
        })

        return res
