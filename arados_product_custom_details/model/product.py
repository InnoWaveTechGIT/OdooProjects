from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class productTemplateInherit(models.Model):
    _inherit = 'product.template'


    mdma_code = fields.Char('MDMA Code')
    MDMA_exp = fields.Date('MDMA Expiry Date')
    SFGa_code = fields.Char('SFDA')
    sheif_life = fields.Integer('Item Validity ')



