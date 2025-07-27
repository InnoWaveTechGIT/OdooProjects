from odoo import api, models, fields, _
from odoo.exceptions import UserError
import os

class StudentReport(models.Model):
    _name = 'student.mood.report'
    
    student_id = fields.Many2one('student.report')
    Period = fields.Selection(
        [('Morning', _('Morning')), ('Noon', _('Noon')),('Afternoon',_('Afternoon'))], string="Period")
    mood_id = fields.Many2one('student.mood' , string="Mood")
    _sql_constraints = [
        ('unique_period_student', 'unique(student_id, Period)', 'Period must be unique for the same student!'),
    ]

class StudentMood(models.Model):
    _name = 'student.mood'
    
    name = fields.Char('Mood')
    image= fields.Binary('Image')
    image_url = fields.Char("image url", compute='_compute_image_url')

    @api.depends('image')
    def _compute_image_url(self):
        base_url = os.getenv('URL')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=student.mood&id=' + str(obj.id) + '&field=image'
