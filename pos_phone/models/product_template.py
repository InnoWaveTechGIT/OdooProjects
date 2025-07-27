from odoo import models, fields , api, _
from odoo.exceptions import ValidationError


class Offer(models.Model):
    _inherit = 'pos.config'



    phone = fields.Char('Phone')
