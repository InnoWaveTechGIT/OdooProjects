from odoo import api, models, fields, _
from odoo.exceptions import UserError
import os

class StudentHealthReport(models.Model):
    _name = 'student.health.report'
    
    student_id = fields.Many2one('student.report')
    health_id = fields.Many2one('student.health' , string='Action')
    number_of = fields.Integer('Number Of Times')


class Studenthealth(models.Model):
    _name = 'student.health'
    
    name = fields.Char('health Name')
    image = fields.Binary('Image')
    image_url = fields.Char("image url", compute='_compute_image_url')

    @api.depends('image')
    def _compute_image_url(self):
        base_url = os.getenv('URL')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=student.health&id=' + str(obj.id) + '&field=image'
            else:
                obj.image_url=''