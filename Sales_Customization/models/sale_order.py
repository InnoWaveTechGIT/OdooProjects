from odoo import models, api, fields
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_amount = fields.Float('Discount Amount' , compute='get_discount_amount')
    total_amount_after_discount = fields.Float('Total Amount after discount' , compute='get_total_amount_after_discount' )


    @api.depends('discount_amount')
    def get_total_amount_after_discount(self):
        for rec in self:
            if rec.discount_amount:
                rec.total_amount_after_discount = rec.amount_total - rec.discount_amount
            else:
                rec.total_amount_after_discount = 0

    @api.depends('order_line' , 'state')
    def get_discount_amount(self):
        discount =0.0
        for rec in self:
            if rec.state not in ['draft' , 'sent' , 'cancel']:
                for line in rec.order_line:
                    discount += (line.product_uom_qty * line.price_unit) * line.discount / 100

            rec.discount_amount = discount
