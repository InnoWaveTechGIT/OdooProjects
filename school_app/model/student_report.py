from odoo import api, models, fields, _
from odoo.exceptions import UserError
import os

class StudentReport(models.Model):
    _name = 'student.report'
    

    user_id =fields.Many2one('res.users',string='Student')
    student_id =  fields.Many2one('students.school.app', string='Students')
    date= fields.Date('Date')

    fields_1 = fields.Boolean('BreakFast')
    fields_2 = fields.Boolean('Lunch')
    fields_3 = fields.Boolean('Snack')


    mood_ids = fields.One2many('student.mood.report' , 'student_id' , string='Student Mood')
    drink_ids = fields.One2many('student.drink.report' , 'student_id' , string='Student drink')
    health_ids = fields.One2many('student.health.report' , 'student_id' , string='Student health')
    behavior_ids = fields.One2many('student.behavior.report' , 'student_id' , string='Student behavior')
    description = fields.Text('Student Behavior Description')