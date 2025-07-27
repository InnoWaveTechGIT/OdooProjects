from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError


class LoyaltyHistory(models.Model):
    _inherit = "sale.order"


    partner_sub_id = fields.Char(related='partner_id.subID')
    partner_email= fields.Char(related='partner_id.email')
    seller_sub_id = fields.Integer(related='seller_id.id')
    product_id = fields.Many2one('product.template' , compute='get_data_from_lines')
    product_Description = fields.Text(string='Description' , compute='get_data_from_lines' , store=True)
    Price_unit = fields.Char(compute='get_data_from_lines')
    tax_id = fields.Char(compute='get_data_from_lines' , store=True)
    Product_uom_qty = fields.Char(compute='get_data_from_lines')
    price_total = fields.Char(compute='get_data_from_lines')
    price_tax = fields.Char(compute='get_data_from_lines')


    status = fields.Char(string='Status', compute='_compute_status', store=True)

    @api.depends('confirmed' , 'state')
    def _compute_status(self):
        for order in self:
            if not order.confirmed and order.state == 'draft':
                order.status = 'Pending'
            elif order.confirmed:
                order.status = 'Confirmed'
            elif order.state == 'cancel':
                order.status = 'Cancelled'
            else:
                order.status = 'Unknown'

    @api.depends('order_line')
    def get_data_from_lines(self):
        for rec in self:
            if rec.order_line:
                rec.product_id = rec.order_line[-1].product_template_id.id
                rec.product_Description = rec.order_line[-1].name
                rec.Price_unit = rec.order_line[-1].price_unit
                rec.tax_id = rec.order_line[-1].tax_id[-1].name if rec.order_line[-1].tax_id else ''
                rec.Product_uom_qty = rec.order_line[-1].product_uom.name
                rec.price_total = rec.order_line[-1].price_total
                rec.price_tax = rec.order_line[-1].price_tax
            else:
                rec.product_id = False
                rec.product_Description = False
                rec.Price_unit = False
                rec.tax_id = False
                rec.Product_uom_qty = False
                rec.price_total =False
                rec.price_total = False
