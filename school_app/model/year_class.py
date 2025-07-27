from odoo import models,api, fields,_
from PIL import Image
import io
import base64
import os
from os import environ
from dotenv import load_dotenv
load_dotenv()


class ImagesSchoolApp(models.Model):
    _name = 'class.school.app'

    _rec_name = 'name'

    
    name=fields.Text('name',default='')
    year_id = fields.Many2one('year.school.app' , string='Year')
    image = fields.Binary('Image')
    image_url = fields.Char("image url", compute='_compute_image_url')
    student_ids = fields.Many2many('res.users', string='Students', domain=[('user_type', '=', 'Student')])
    teacher_id = fields.Many2one('res.users' , string='Teacher' , domain=[('user_type', '=', 'Teacher')])
    is_valid = fields.Boolean('Is Valid')
    active = fields.Boolean('state' , default=True)

    @api.depends('image')
    def _compute_image_url(self):
        base_url = os.getenv('URL')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=class.school.app&id=' + str(obj.id) + '&field=image'
            else:
                obj.image_url = ''
