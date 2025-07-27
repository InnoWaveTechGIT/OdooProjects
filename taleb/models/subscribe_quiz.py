from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
from datetime import datetime ,date,timedelta
import re
import os
import time
import base64
import requests
import json
from dateutil.relativedelta import relativedelta

class CoursesTaleb(models.Model):
    _name = 'quiz.subscribe'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "this module is for quiz subscribe"


    user_id = fields.Many2one('res.users' , string= 'User ID')
    subject_class = fields.Selection(
        [('تاسع', 'تاسع'), ('بكلوريا علمي', 'بكلوريا علمي '), ('بكلوريا أدبي', 'بكلوريا أدبي')], string="Subject Class",required = True) 
    course_id = fields.Many2many('courses' , string= 'Courses',required = True ,domain="[('subject_class', '=', subject_class)]")
