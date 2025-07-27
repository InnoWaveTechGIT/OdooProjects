from odoo import models,api, fields,_
import re
import os
import time
import base64 

class StudentClass(models.Model):
    _name = 'student.class'
    _description = "this module is for Student Class"

    name=fields.Char(string="Class Name")