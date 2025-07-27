from odoo import models,api, fields,_
import re
import os
import time
import base64 



class FQA(models.Model):
    _name = 'fqa'
    _description = "this module is for fqa"


    # name = fields.Char(string='Name')
    question=fields.Text(string="Question")
    answer=fields.Text(string="Answer")
    
