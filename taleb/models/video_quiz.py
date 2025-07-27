from odoo import models,api, fields,_
import requests
import json
from odoo.exceptions import ValidationError
import os
import time
import base64


class CourseVideoQuiz(models.Model):
    _name = 'video.quiz'
    _description = "this module is for video.quiz"



    quiz_id = fields.Many2one('course.video' , string = 'Video ID')
    question = fields.Html('Question' , required = True)
    hint=fields.Html(string='Hint')
    number_of_answers = fields.Selection(
        [('2', '2'), ('3', '3'), ('4', '4')], string="Number of answers" , default ='2')
    correct_answers = fields.Selection(
        [('1', '1'),('2', '2'), ('3', '3'), ('4', '4')], string="Correct answer" , required = True)
    answer1 = fields.Html('Answer 1' , required = True)
    answer2 = fields.Html('Answer 2' , required = True)
    answer3 = fields.Html('Answer 3')
    answer4 = fields.Html('Answer 4')