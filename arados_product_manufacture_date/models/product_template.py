from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _default_manufacturing_date(self):
        return self.env['ir.config_parameter'].sudo().get_param('arados_product_manufacture_date.allow_manufacturing_date')

    use_manufacturing_date = fields.Boolean(string='Manufacturing Date', store=True)
    allow_manufacturing_date = fields.Boolean(default='_default_manufacturing_date', store=True)

