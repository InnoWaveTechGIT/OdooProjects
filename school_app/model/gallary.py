from odoo import models,api, fields,_
from PIL import Image
import io
import base64
import os
from os import environ
from dotenv import load_dotenv
load_dotenv()


class ImagesSchoolApp(models.Model):
    _name = 'images.school.app'

    _rec_name = 'name'

    
    
    name=fields.Text('name',default='')
    image = fields.Binary('Image')
    image_url = fields.Char("image url", compute='_compute_image_url')
    medium_image = fields.Binary('Medium Image')
    medium_image_url = fields.Char("image url", compute='_compute_image_url')
    small_image = fields.Binary('Small Image')
    small_image_url = fields.Char("image url", compute='_compute_image_url')
    very_small_image = fields.Binary('Very Small Image')
    very_small_image_url = fields.Char("image url", compute='_compute_image_url')
    thumbnail_image = fields.Binary('Thumbnail Image', compute='_compute_thumbnail_image')
    class_id=fields.Many2one('section.school.app' , string='Class')
    user_id=fields.Many2one('res.users' , string='Profile')
    student_ids =  fields.Many2many('res.users', string='Students')
    student_ids2 =  fields.Many2many('students.school.app', string='Students')
    status= fields.Selection(
        [('Private', _('Private')), ('Public', _('Public'))], string="Status")
    
    image_id = fields.Many2one('album.school.app' , string='Album')
    message_id = fields.Many2one('school.message' , string='message')
    @api.depends('very_small_image')
    def _compute_thumbnail_image(self):
        for record in self:
            # You might want to resize the image to be smaller
            # or do other image processing before assigning.
            record.thumbnail_image = record.very_small_image

    @api.constrains('class_id')
    def _get_students(self):
        for record in self:
            # You might want to resize the image to be smaller
            # or do other image processing before assigning.
            record.student_ids2 = record.class_id.student_ids2


    @api.constrains('image')
    def _compute_image_url(self):
        base_url = os.getenv('URL')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=images.school.app&id=' + str(obj.id) + '&field=image'
                image_data = io.BytesIO(base64.b64decode(obj.image))

                # Open the image
                with Image.open(image_data) as img:
                    width, height = img.size
                    img = img.convert('RGB')
                    # Resize the image to medium size
                    medium_size = (int(width*0.5), int(height*0.5))
                    medium_img = img.resize(medium_size, Image.LANCZOS)

                    # Convert the resized image to bytes
                    medium_bytes = io.BytesIO()
                    medium_img.save(medium_bytes, format='JPEG')
                    medium_image_data = base64.b64encode(medium_bytes.getvalue())

                    # Resize the image to small size
                    small_size = (int(width*0.25), int(height*0.25))
                    small_img = img.resize(small_size, Image.LANCZOS)

                    # Convert the resized image to bytes
                    small_bytes = io.BytesIO()
                    small_img.save(small_bytes, format='JPEG')
                    small_image_data = base64.b64encode(small_bytes.getvalue())

                    # Resize the image to very small size
                    very_small_size = (int(width*0.15), int(height*0.15))
                    very_small_img = img.resize(very_small_size, Image.LANCZOS)

                    # Convert the resized image to bytes
                    very_small_bytes = io.BytesIO()
                    very_small_img.save(very_small_bytes, format='JPEG')
                    very_small_image_data = base64.b64encode(very_small_bytes.getvalue())

                    # Update the obj with the resized images
                    obj.write({
                        'medium_image': medium_image_data,
                        'small_image': small_image_data,
                        'very_small_image': very_small_image_data,

                    })
                    obj.medium_image_url= base_url + '/web/image?' + 'model=images.school.app&id=' + str(obj.id) + '&field=medium_image'
                    obj.small_image_url = base_url + '/web/image?' + 'model=images.school.app&id=' + str(obj.id) + '&field=small_image'
                    obj.very_small_image_url = base_url + '/web/image?' + 'model=images.school.app&id=' + str(obj.id) + '&field=very_small_image'
            else:
                obj.medium_image_url=''
                obj.small_image_url =''
                obj.very_small_image_url =''
                obj.image_url=''