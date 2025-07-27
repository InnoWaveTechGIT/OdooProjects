from odoo import models,api, fields,_
import requests
import json
from odoo.exceptions import ValidationError
import os
import time
import base64


class CourseResult(models.Model):
    _name = 'course.result'
    _description = "this module is for course.result"


    course_result_id = fields.Many2one('res.users' , string= 'User ID')
    course_id = fields.Many2one('courses' , string='Course ID')
    result = fields.Integer('Resault')



   