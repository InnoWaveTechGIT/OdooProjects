from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_qty = fields.Float(string='Total Amount', compute='_compute_total_qty')
    total_delivered = fields.Float(string='Total Delivered', compute='_compute_total_delivered')
    total_return = fields.Float(string='Total Return', compute='_compute_total_return')

    total_payments = fields.Float(string='Total Payments', compute='_compute_total_payments')


    @api.depends('invoice_ids')
    def _compute_total_payments(self):
        print('self  >>>>>>>>> ' , self)
        for order in self:
            total_amount = 0.0
            invoices = order.invoice_ids
            for invoice in invoices:
                total_amount = 0.0
                payments = self.env['account.payment'].search([('ref', '=', invoice.name)])  # Search for payments related to the invoice
                for payment in payments:
                    total_amount += payment.amount
            order.total_payments = total_amount
    @api.depends('order_line.product_uom_qty', 'order_line.price_subtotal')
    def _compute_total_qty(self):
        for order in self:
            if order.order_line :
                total_amount = sum(line.price_total for line in order.order_line)
                order.total_qty = total_amount
            else:
                order.total_qty =0.0

    @api.depends('order_line.qty_delivered')
    def _compute_total_delivered(self):
        for order in self:
            if order.order_line:
                for i in order.order_line:
                    if i.product_uom_qty:
                        amount = (i.price_total / i.product_uom_qty) * i.qty_delivered
                    else:
                        amount=0

                    order.total_delivered += amount
            else:
                order.total_delivered = 0.0

    @api.depends('total_qty', 'total_delivered')
    def _compute_total_return(self):
        for order in self:
            order.total_return = order.total_qty - order.total_delivered

