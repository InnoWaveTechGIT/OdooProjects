from odoo import api, models, fields, _
from odoo.exceptions import UserError
import os

class StudentbehaviorReport(models.Model):
    _name = 'student.behavior.report'
    
    student_id = fields.Many2one('student.report')
    behavior_id = fields.Many2one('student.behavior' , string='Behavior')
    status =fields.Selection(
        [('Weak', _('Weak')), ('Good', _('Good')) , ('VeryGood', _('VeryGood')) , ('Excellent', _('Excellent'))], string="Unit")


class Studentbehavior(models.Model):
    _name = 'student.behavior'
    
    name = fields.Char('behavior Name')
    image = fields.Binary('Image')

    image_url = fields.Char("image url", compute='_compute_image_url')

    @api.depends('image')
    def _compute_image_url(self):
        base_url = os.getenv('URL')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=student.behavior&id=' + str(obj.id) + '&field=image'
            else:
                obj.image_url = ''