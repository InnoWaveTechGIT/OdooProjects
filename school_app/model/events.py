from odoo import models,api, fields,_
from PIL import Image
import io
import base64
import os
from os import environ
from dotenv import load_dotenv
load_dotenv()


class EventsSchoolApp(models.Model):
    _name = 'events.school.app'

    _rec_name = 'name'

    
    event_type = fields.Selection(
        [('Private', _('Private')), ('Public', _('Public'))], string="The Type")

    name = fields.Char('Name')
    description = fields.Text('Description')
    start_time = fields.Date('Start Time')
    end_time = fields.Date('End Time')
    
    class_id=fields.Many2one('section.school.app' , string='Class')
    student_ids =  fields.Many2many('res.users', string='Students')
    student_ids2 =  fields.Many2many('students.school.app', string='Students')
    image= fields.Binary('Image')
    image_url = fields.Char("image url", compute='_compute_image_url')
    user_ids = fields.Many2many('res.users', 'users_seen', string='Users')
    
    @api.model
    def create(self, vals):
        values = super().create(vals)
        for i in values:
            for user in i.student_ids2:
                notification_date={}
                notification_date = {
                    'comment' : 'New Event',
                    'user_id' : user.parent_id.id,
                    'data' : {'id': i.id ,
                              'date' : str(i.create_date) 
                              },
                    'notification_type' : 'Events'
                }
                self.env['notification.school'].create(notification_date)
        return values

    @api.depends('image')
    def _compute_image_url(self):
        base_url = os.getenv('URL')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=events.school.app&id=' + str(obj.id) + '&field=image'
            else:
                obj.image_url =''

    @api.constrains('class_id')
    def _get_students(self):
        for record in self:
            # You might want to resize the image to be smaller
            # or do other image processing before assigning.
            record.student_ids2 = record.class_id.student_ids2