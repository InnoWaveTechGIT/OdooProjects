from odoo import api, models, fields, _
from odoo.exceptions import UserError




class StudentSubjectMood(models.Model):
    _name = 'subject.school.app'
    
    name = fields.Char('Subject')
    teacher_id = fields.Many2one('res.users' , string='Teacher' , domain=[('user_type', '=', 'Teacher')])

    # image= fields.Binary('Image')
    # image_url = fields.Char("image url", compute='_compute_image_url')

   