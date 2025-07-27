from odoo import models,api, fields,_



class TeacherTaleb(models.Model):
    _name = 'teacher'
    _description = "this module is for teacher"

    name = fields.Many2one('res.users',string='Teacher Name' ,domain="[('user_type', '=', 'teacher')]" ,ondelete='cascade')
    teacher_image = fields.Char(related='name.image_path')
    teacher_name = fields.Char(related='name.name')
    specialization = fields.Char(string='Specialization ')
    description = fields.Html(string='Description ')
    rate = fields.Float(string='Rate' , readonly=True)
    number_of_rater = fields.Integer(string='Number Of Raters', readonly = True)
    number_of_courses =fields.Integer(string='Number Of Courses' , readonly=True)
    number_of_student =fields.Integer(string='Numbere Of Student', readonly=True)
    courses_ids = fields.One2many('courses', 'teacher_id')
    active = fields.Boolean(default=True)
    


    @api.constrains('name')
    def check_id_len(self):
        for rec in self:
            print("name>>>> "+str(rec.name))