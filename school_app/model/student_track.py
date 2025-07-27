from odoo import api, models, fields, _
from odoo.exceptions import UserError
import os

class StudentbehaviorReport(models.Model):
    _name = 'student.track.report'

    
    student_id =  fields.Many2one('students.school.app', string='Student')
    track_ids = fields.One2many('student.track.report.line' , 'track_id' , string='Tracking')


class StudentbehaviorReport(models.Model):
    _name = 'student.track.report.line'


    responseble_id = fields.Many2one('res.users' , string='Responsble ')
    date = fields.Date('Date')
    track_id =  fields.Many2one('student.track.report', string='Students')
    state = fields.Selection(
        [('Home', _('Home')), ('Bus', _('Bus')) , ('School', _('School')) ], string="Status")

