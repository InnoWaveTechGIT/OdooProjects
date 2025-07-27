from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
from datetime import date
class Resaults(models.Model):
    _name="resault"
    _description="model for result courses"
    _rec_name = 'session_id'

    user_id = fields.Many2one('res.users',string='User ID')
    resault =fields.Integer('Resault')
    session_id = fields.Many2one('course.video',string='Session ID')
    course_id = fields.Many2one('courses' , string='Course')
    false_answers = fields.Char('False Answers')
    try_counter = fields.Integer('Try Counter')
    correct_stu_ans = fields.Char('Correct Answers')

class Resaults(models.Model):
    _name="quiz.conf"
    _description="model for result courses"


    number = fields.Integer(string='Number of tries')
    