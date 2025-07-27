from odoo import api, models, fields, _
from odoo.exceptions import UserError
import os

class StudentDrinkReport(models.Model):
    _name = 'student.drink.report'
    
    student_id = fields.Many2one('student.report')
    drink_id = fields.Many2one('student.drink')


class StudentDrink(models.Model):
    _name = 'student.drink'
    
    name = fields.Char('Drink Name')
    image = fields.Binary('Image')
    image_url = fields.Char("image url", compute='_compute_image_url')

    @api.depends('image')
    def _compute_image_url(self):
        base_url = os.getenv('URL')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=student.drink&id=' + str(obj.id) + '&field=image'
