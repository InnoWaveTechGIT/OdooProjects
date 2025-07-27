from odoo import api, fields, models, tools, _
from num2words import num2words
from babel.numbers import get_currency_name
from itertools import groupby
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Command


class SaleOrderYokohama(models.Model):
    _inherit = 'sale.order'

    discount_amount = fields.Char()
    positive_product_prices = fields.Float(
        string='Positive Product Prices',
        compute='_compute_positive_product_prices',
        store=True,
        readonly=True,
        help='Sum of positive product prices in the invoice',
    )

    @api.depends('order_line.price_subtotal')
    def _compute_positive_product_prices(self):
        for invoice in self:
            positive_prices = sum(line.price_subtotal for line in invoice.order_line if line.price_subtotal > 0)
            invoice.positive_product_prices = positive_prices


class SaleOrderDiscountYokohama(models.TransientModel):
    _inherit = 'sale.order.discount'

    def action_apply_discount(self):

        super(SaleOrderDiscountYokohama, self).action_apply_discount()
        self.sale_order_id.discount_amount = self.discount_percentage * 100
