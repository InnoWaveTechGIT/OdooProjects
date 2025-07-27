from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
import re
import os
import time
import base64
from os import environ
from dotenv import load_dotenv
from random import randint
load_dotenv()


class UserInherit(models.Model):
    _inherit = 'res.users'

    
    image_url= fields.Char(string='image url',compute='_compute_image_url')
    user_type= fields.Selection(
        [('Teacher', _('Teacher')), ('Student', _('Student'))], string="Status")
    bin_fields = fields.Char('BIN', default=lambda self: self._generate_bin())
    def _generate_bin(self):
        # Generate a random 4-digit integer
        return randint(1000, 9999)

    @api.depends('image_1920')
    def _compute_image_url(self):
        base_url = os.getenv('URL')
        for rec in self:
            if rec.image_1920:
                rec.image_url = base_url + '/web/image?' + 'model=res.users&id=' + str(rec.id) + '&field=image_1920'
            else:
                rec.image_url = ""

