# discount_wizard.py

from odoo import models, fields, api

class DiscountWizard(models.TransientModel):
    _name = 'discount.wizard'


    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    discount_percentage = fields.Float(string='Discount (%)')

    def apply_discount(self):
        order = self.sale_order_id
        discount_product = self.env['product.product'].search([('name', '=', 'Discount')], limit=1)
        
        order_line = {
            'product_id': discount_product.id,
            'name': discount_product.name,
            'product_uom_qty': 1,
            'price_unit': -1 * (order.amount_untaxed * (self.discount_percentage / 100)),
            'order_id': order.id,
        }
        
        order.write({'order_line': [(0, 0, order_line)],
            'discount_percentage' :self.discount_percentage })
        return {'type': 'ir.actions.act_window_close'}

# sale_order_inherit.py

from odoo import models, fields, api

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    discount_percentage = fields.Float(string='Discount (%)') 
    is_discount = fields.Boolean(string='Has Discount', compute='_compute_has_discount')

    @api.depends('order_line')
    def _compute_has_discount(self):
        for order in self:
            has_discount = any(line.product_id.name == 'Discount' for line in order.order_line)
            order.is_discount = has_discount

    def open_discount_wizard(self):
        discount_wizard = self.env['discount.wizard'].create({})
        return {
            'name': 'Add Discount',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'discount.wizard',
            'target': 'new',
            'context': {'default_sale_order_id': self.id},
        }