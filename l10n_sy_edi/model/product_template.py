from odoo import models, api, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'


    @api.constrains('categ_id')
    def check_syrian_tax(self):
        for rec in self:
            if rec.categ_id:
                if rec.categ_id.syrian_tax_ids:
                    rec.taxes_id = rec.categ_id.syrian_tax_ids.ids
