from odoo import models,api, fields,_
from PIL import Image
import io
import base64
import os
from os import environ
from dotenv import load_dotenv
load_dotenv()


class StudentsSchoolApp(models.Model):
    _name = 'students.school.app'



    name = fields.Char('Name')
    parent_id = fields.Many2one('res.users' , domain=[('user_type', '=', 'Student')])
    image= fields.Binary('Image')
    image_url = fields.Char("image url", compute='_compute_image_url')
    code = fields.Char('Code')
    section_id = fields.Many2one('section.school.app' , domain=[('is_valid', '=', True)] , string='Section')
    class_id = fields.Many2one(related='section_id.class_id' , string='Class')
    year_id = fields.Many2one(related='section_id.year_id' , string='Year')


    @api.constrains('student_id')
    def _get_students_code(self):
        for record in self:
            record.code = str(record.id) + '_'+ str(record.name) + '_' + str(record.parent_id.id) + '_' + str(record.year_id.id) 


    @api.depends('image')
    def _compute_image_url(self):
        base_url = os.getenv('URL')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=events.school.app&id=' + str(obj.id) + '&field=image'
            else:
                obj.image_url =''