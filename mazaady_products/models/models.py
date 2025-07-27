
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import json        

class ProductTemplate(models.Model):
    _inherit = 'product.template'    

    seller_id = fields.Many2one('res.partner')
    mazaady_product_id = fields.Integer('')
