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
        [('Teacher', _('Teacher')), ('Student', _('Student')) , ('Supervisor', _('Supervisor')) , ('Secretary', _('Secretary'))], string="Status")
    bin_fields = fields.Char('BIN', default=lambda self: self._generate_bin())
    student_ids =fields.One2many('students.school.app' , 'parent_id', string='Students')
    def _generate_bin(self):
        # Generate a random 4-digit integer
        return randint(1000, 9999)

    @api.constrains('image_1920')
    def _compute_image_url(self):
        base_url = os.getenv('URL')
        for rec in self:
            if rec.image_1920:
                image = self.env['images.school.app'].create({
                    'image' : rec.image_1920,
                    'user_id' : rec.id
                })
                rec.image_url = base_url + '/web/image?' + 'model=images.school.app&id=' + str(image.id) + '&field=image'
            else:
                rec.image_url = ""

    