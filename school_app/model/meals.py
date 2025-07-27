from odoo import models,api, fields,_
from PIL import Image
import io
import base64
import os
from os import environ
from dotenv import load_dotenv
load_dotenv()


class EventsSchoolApp(models.Model):
    _name = 'meals.school.app'

    _rec_name = 'name'

    name = fields.Char('Name')
    description = fields.Text('Description')
    date_time = fields.Date('Date Time')
    breakfast = fields.Char('BreakFast')
    duration_1 = fields.Char('From')
    duration_12 = fields.Char('To')
    image_1= fields.Binary('Image')
    color_picker1 = fields.Char(string='BreakFast Color')
    image_1_url  = fields.Char("image url", compute='_compute_image_url1')
    lunch = fields.Char('Lunch')
    duration_2 = fields.Char('From')
    duration_22 = fields.Char('To')
    image_2= fields.Binary('Image')
    color_picker2 = fields.Char(string='Lunch Color')
    image_2_url = fields.Char("image url", compute='_compute_image_url2')
    snack = fields.Char('Snack')
    duration_3 = fields.Char('From')
    duration_32 = fields.Char('To')
    image_3 = fields.Binary('Image')
    color_picker3 = fields.Char(string='Snack Color')
    image_3_url = fields.Char("image url", compute='_compute_image_url3')
    # <field name='color_picker' widget="color" />


    @api.depends('image_1')
    def _compute_image_url1(self):
        base_url = os.getenv('URL')
        for obj in self:
            if obj.image_1:
                obj.image_1_url= base_url + '/web/image?' + 'model=student.drink&id=' + str(obj.id) + '&field=image_1'

    @api.depends('image_2')
    def _compute_image_url2(self):
        base_url = os.getenv('URL')
        for obj in self:
            if obj.image_2:
                obj.image_2_url= base_url + '/web/image?' + 'model=student.drink&id=' + str(obj.id) + '&field=image_2'
    @api.depends('image_3')
    def _compute_image_url3(self):
        base_url = os.getenv('URL')
        for obj in self:
            if obj.image_3:
                obj.image_3_url= base_url + '/web/image?' + 'model=student.drink&id=' + str(obj.id) + '&field=image_3'
