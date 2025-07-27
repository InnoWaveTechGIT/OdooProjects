from odoo import models, api, fields

class Tax(models.Model):
    _inherit = 'account.tax'

    syria_code = fields.Char('Tax Code(Syria)')






