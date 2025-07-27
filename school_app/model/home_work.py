from odoo import models,api, fields,_
from PIL import Image
import io
import base64
import os
from os import environ
from dotenv import load_dotenv
load_dotenv()


class HomeworkSchoolApp(models.Model):
    _name = 'homework.school.app'

    day=fields.Date('Day')
    class_id=fields.Many2one('section.school.app' , string='Class')

    homework_ids = fields.One2many('home.work.lines' , 'homework_id' , string='Home Works')


class HomeworklineSchoolApp(models.Model):
    _name = 'home.work.lines'

    subject_id=fields.Many2one('subject.school.app' , string='Subject')
    homework_id = fields.Many2one('homework.school.app')
    teacher_id = fields.Many2one('res.users' , string='Teacher' , domain=[('user_type', '=', 'Teacher')])
    homework_description = fields.Text('Home Work ')
    user_ids = fields.Many2many('res.users', string='Users')

    @api.model
    def create(self, vals):
        record = super(HomeworklineSchoolApp, self).create(vals)
        for record in self:
            for user in record.homework_id.class_id.student_ids:
                notification_data = {
                    'comment': 'New Homework',
                    'user_id': user.parent_id.id,
                    'data': {
                        'id': record.homework_id.id,
                        'date': str(record.homework_id.day)
                    },
                    'notification_type': 'HomeWork'
                }
                self.env['notification.school'].create(notification_data)
        return record