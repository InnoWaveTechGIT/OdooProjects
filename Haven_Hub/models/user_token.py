from odoo import models,api, fields,_
import jwt
from datetime import datetime ,timedelta
import base64
from odoo.exceptions import ValidationError
import time

class UserrTokenHaven(models.Model):
    _name = 'user.token.haven'
    _description = "this module is for user token Haven Hub"
    _rec_name = 'user_id'

    user_id = fields.Char(string='User ID')
    token = fields.Text(string='Token')
