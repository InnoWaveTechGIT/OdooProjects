from odoo import models,api, fields,_
import jwt
from datetime import datetime ,timedelta
import base64 
from odoo.exceptions import ValidationError
import time

class UserrTokennasaem(models.Model):
    _name = 'banner.nasaem'
    _description = "this module is for user_token nasaem"

    STATES = [
        ('en_US', 'English'),
        ('ar_001', 'Arabic'),
    ]

    image = fields.Binary('Image')
    image_url = fields.Char("image url", compute='_compute_image_url')
    category_id = fields.Many2one('product.public.category' , string='Category')
    for_register = fields.Boolean('For Register')
    banner_language = fields.Selection(STATES, string="language")

    @api.depends('image')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=banner.nasaem&id=' + str(obj.id) + '&field=image'
            else :
                obj.image_url= ''


# class SaleOrderInherit(models.Model):
#     _inherit = 'sale.order'

#     # delivery_status = fields.Selection(selection_add=[ ('shipped', "Shipped"), ],ondelete={'shipped': 'cascade'},
#     #                              )
#     @api.constrains('partner_id')
#     def chang_prop(self):
#         for rec in self :
#             data = self.env['ir.model.fields.selection'].search([('field_id.id' ,'=', 13312)])
#             for i in data:
#                 if i.value == 'partial':
#                     i.name = 'Shipped'