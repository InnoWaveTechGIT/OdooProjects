from odoo import models,api, fields,_
from PIL import Image
import io
import base64
import os
from os import environ
from dotenv import load_dotenv
load_dotenv()


class ImagesSchoolApp(models.Model):
    _name = 'album.school.app'

    _rec_name = 'name'

    
    image_ids = fields.One2many('images.school.app' ,'image_id', string='Image')
    name=fields.Text('name',default='')
    status= fields.Selection(
        [('Private', _('Private')), ('Public', _('Public'))], string="Status")
    class_id=fields.Many2one('section.school.app' , string='Class')
    student_ids =  fields.Many2many('res.users', string='Students')
    student_ids2 =  fields.Many2many('students.school.app', string='Students')
    user_ids = fields.Many2many('res.users', 'users_seen1', string='Users')

    @api.constrains('class_id')
    def _get_students(self):
        for record in self:
            # You might want to resize the image to be smaller
            # or do other image processing before assigning.
            record.student_ids2 = record.class_id.student_ids2
