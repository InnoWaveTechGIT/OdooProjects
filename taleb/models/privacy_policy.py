from odoo import models,api, fields,_
import re
import os
import time
import base64 

class PrivacyPolicy(models.Model):
    _name = 'privacy.policy'
    _description = "this module is for privacy.policy"

    content=fields.Html(string="Content")
class Termsofuse(models.Model):
    _name='terms.use'
    _description = "this module is for terms.use"
    content=fields.Html(string="Content")
