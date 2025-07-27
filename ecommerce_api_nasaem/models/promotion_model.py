from odoo import models,api, fields,_
import jwt
from datetime import datetime ,timedelta
import base64 
from odoo.exceptions import ValidationError
import time

class PromotoinNasaem(models.Model):
    _name = 'promotion.nasaem'
    _description = "this module is for promotion nasaem"

    title = fields.Char('Title', translate=True)
    text = fields.Char('Text', translate=True)
    image = fields.Binary('Image')
    image_url = fields.Char("image url", compute='_compute_image_url')
    is_visible = fields.Boolean('Visible')

    @api.depends('image')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=promotion.nasaem&id=' + str(obj.id) + '&field=image'
            else :
                obj.image_url= ''

