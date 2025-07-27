from odoo import models,api, fields,_
from odoo.exceptions import ValidationError

from datetime import date
class Rate(models.Model):
    _name="rate"
    _description="model for rating courses"
    _rec_name = "course_id"
    
    

    course_id=fields.Many2one('courses',string="courses" ,ondelete='cascade')
    rate_value = fields.One2many('rate.value','rate_id' , string = 'Rate Value')
    @api.constrains('course_id')
    def check_unique_course(self):
        for record in self:
            record.validate_course()
    def validate_course(self):
        rec_number=self.env['rate'].search_count([('course_id', '=',self.course_id.id)])
        if rec_number>1:
            raise ValidationError(_("rate for this course already exist "))

       


class RateValue(models.Model):
    _name="rate.value"
    _description="model for rating courses"


    rataing=fields.Float(string='Rate')
    user_id=fields.Many2one('res.users',string="Users",ondelete='cascade')
    image_path = fields.Char(related='user_id.image_path')
    comment = fields.Char('comment')
    date_of_create = fields.Date('Date')
    rate_id = fields.Many2one('rate',string = 'Rate ID',ondelete='cascade')
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        date_now = date.today()
        print('asdasdasd')
        vals['date_of_create'] = date_now
        values=super().create(vals)        
        return values
class Rate(models.Model):
    _name="rate"
    _description="model for rating courses"
    _rec_name = "course_id"
    
    

    course_id=fields.Many2one('courses',string="courses" ,ondelete='cascade')
    rate_value = fields.One2many('rate.value','rate_id' , string = 'Rate Value')
    @api.constrains('course_id')
    def check_unique_course(self):
        for record in self:
            record.validate_course()
    def validate_course(self):
        rec_number=self.env['rate'].search_count([('course_id', '=',self.course_id.id)])
        if rec_number>1:
            raise ValidationError(_("rate for this course already exist "))

       


class RateValue(models.Model):
    _name="rate.value"
    _description="model for rating courses"


    rataing=fields.Float(string='Rate')
    user_id=fields.Many2one('res.users',string="Users",ondelete='cascade')
    image_path = fields.Char(related='user_id.image_path')
    comment = fields.Char('comment')
    date_of_create = fields.Date('Date')
    rate_id = fields.Many2one('rate',string = 'Rate ID',ondelete='cascade')
    active = fields.Boolean(default=True)


    @api.model
    def create(self, vals):
        date_now = date.today()
        print('asdasdasd')
        vals['date_of_create'] = date_now
        values=super().create(vals)        
        return values
class RateVideo(models.Model):
    _name="video.rate"
    _description=' this model for rate session  created by Eng Ali alkousa'
    _rec_name = 'video'
    video = fields.Many2one('course.video' , string='Video')
    video_rate_value=fields.One2many('video_rate.value','rate_id' , string = 'Rate Value')
    
    @api.constrains('video')
    def check_unique_video(self):
        for record in self:
            record.validate_video()
    def validate_video(self):
        rec_number=self.env['video.rate'].search_count([('video', '=',self.video.id)])
        if rec_number>1:
            raise ValidationError(_("يوجد سجل تقييم سابقا لهذه الجلسة الرجاء أضافة التقييم به"))
class VideoRateValue(models.Model):
    _name="video_rate.value"
    _description="model for rating videos"


    rataing=fields.Float(string='Rate')
    user_id=fields.Many2one('res.users',string="Users",ondelete='cascade')
    image_path = fields.Char(related='user_id.image_path')
    comment = fields.Char('comment')
    rate_id = fields.Many2one('video.rate',string = 'Rate ID',ondelete='cascade')
    active = fields.Boolean(default=True)
