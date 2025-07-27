from datetime import datetime ,date,timedelta
from odoo import models, fields, api
import math, random
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class UserCourseProgress(models.Model):
    _name = 'user.course.progress'
    _description = 'User Course Progress'

    user_id = fields.Many2one('res.users', string="User")
    course_id = fields.Many2one('my.course', string="Course")
    section_id = fields.Many2one('my.section', string="Section")
    session_id = fields.Many2one('my.session', string="Session")
    progress = fields.Float(string="Progress")

    _sql_constraints = [
        ('session_user_uniq', 'unique(session_id, user_id)', 'A user cannot watch a session more than once.'),
    ]

# class Course(models.Model):
#     _inherit = 'my.course'

#     @api.depends('section_ids.session_ids.usercourseprogress_ids.progress')
#     def _compute_total_progress(self):
#         for record in self:
#             record.total_progress = sum(section.session_ids.mapped('usercourseprogress_ids.progress') for section in record.section_ids)

    total_progress = fields.Float(compute='_compute_total_progress', string="Total Progress")
class EducationalSupervisor(models.Model):
    _name = 'educational.supervisor'
    _description = ''
    user_id = fields.Many2one('res.users',string='User Name')
    course_id = fields.Many2one('courses' , string='Course')
    user_progress = fields.Float('Progress')
    section = fields.Char('Sections') 
    section_progress_ids = fields.One2many('educational.supervisor.section' , 'edu_super_id' )
    session_progress_ids = fields.One2many('educational.supervisor.session' , 'edu_super_id' )
    

    def get_student_progress(self):
        action = self.env['session_status'].get_student_progress()

        return True

class EducationalSupervisorSection(models.Model):
    _name = 'educational.supervisor.section'

    edu_super_id = fields.Many2one('educational.supervisor')
    section_id = fields.Many2one('section' , string='Section')
    user_progress = fields.Float('Progress')

class EducationalSupervisorSession(models.Model):
    _name = 'educational.supervisor.session'


    edu_super_id = fields.Many2one('educational.supervisor')
    session_id = fields.Many2one('course.video' , string='Section')
