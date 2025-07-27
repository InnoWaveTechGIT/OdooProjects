from odoo import models, api, fields

class Category(models.Model):
    _inherit = 'product.category'

    syrian_tax_ids = fields.Many2many('account.tax' , string='Syrian Tax Category')

class AccountTax(models.Model):
    _inherit = 'account.tax'

    syria_code = fields.Char('Tax Code(Syria)')






