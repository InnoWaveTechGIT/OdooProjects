from odoo import models,api, fields,_
import re
import os
import time
import base64 



class SkillsTaleb(models.Model):
    _name = 'skills'
    _description = "this module is for skills"


    name = fields.Char(string='Name')