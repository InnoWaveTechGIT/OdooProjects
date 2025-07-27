from odoo import api, models, fields, _
from odoo.exceptions import UserError
import os

class StudentbehaviorReport(models.Model):
    _name = 'student.evaluation.report'

    student_id =  fields.Many2one('students.school.app', string='Students')
    subject_id =  fields.Many2one('subject.school.app', string='Subject')
    teacher_id = fields.Many2one(related='subject_id.teacher_id' , string='Teacher')
    rate = fields.Float('Rate')
    note = fields.Text('Note')
    date = fields.Date('Date')


