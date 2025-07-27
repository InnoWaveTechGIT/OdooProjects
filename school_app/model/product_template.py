from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class Product_template(models.Model):
    _inherit = 'product.template'

    warehouse_ids = fields.Many2many('stock.quant', string="Warehouses" , compute="get_product_warehouses")



    def get_product_warehouses(self):
        for rec in self:
            locations = self.env['stock.quant'].search([('product_id.product_tmpl_id' , '=' , rec.id)])

            rec.warehouse_ids = locations.ids
        