from odoo import models,api, fields,_
from PIL import Image
import io
import base64
import os
from os import environ
from dotenv import load_dotenv
load_dotenv()


class ImagesSchoolApp(models.Model):
    _name = 'year.school.app'

    _rec_name = 'name'

    
    name=fields.Text('name',default='')
    start_time = fields.Date('Start Time')
    end_time = fields.Date('End Time')
    image = fields.Binary('Image')
    image_url = fields.Char("image url", compute='_compute_image_url')
    valid=fields.Boolean('Is Valid')
    
    @api.depends('image')
    def _compute_image_url(self):
        base_url = os.getenv('URL')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=year.school.app&id=' + str(obj.id) + '&field=image'
            else:
                obj.image_url = ''
