from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
from datetime import date
class TeacherRate(models.Model):
    _name="teacher_rate"
    _description="teacher rate "
    _rec_name = 'teacher_id'


    
    teacher_id=fields.Many2one('teacher',string="teachers")
    rate_value = fields.One2many('teacher.value','rate_id' , string = ' Teacher Rate Value')

    @api.constrains('teacher_id')
    def check_unique_course(self):
        for record in self:
            print('jh')
            record.validate_course()
    def validate_course(self):
        rec_number=self.env['teacher_rate'].search_count([('teacher_id', '=',self.teacher_id.id)])

        if rec_number>1:
            raise ValidationError(_("rate for this teacher already exist "))


    class TeacherRateValue(models.Model):
        _name="teacher.value"
    
        _description="model for value of  rating teacher"


        rataing=fields.Float(string='Rate')
        user_id=fields.Many2one('res.users',string="Users")
        comment = fields.Char('comment')
        date_of_create = fields.Date('Date')
        rate_id = fields.Many2one('teacher_rate',string = 'Rate ID')
        comment=fields.Text(string="Comment")  
        active = fields.Boolean(default=True)



        @api.model
        def create(self, vals):
            date_now = date.today()
            print('asdasdasd')
            vals['date_of_create'] = date_now
            values=super().create(vals)        
            return values

