from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
import re
import os
import time
import base64
import requests
import json


class DenouncementTaleb(models.Model):
    _name = 'notifications'
    _description = "this module is for notifications"
    _rec_name='comment'

    comment = fields.Char('Comment')
    user_id = fields.Many2one('res.users')
    data = fields.Char('Data')
    is_seen = fields.Boolean('Is Seen')
   
    notification_type = fields.Selection(selection=[
        ('Comment', 'Comment'),
        ('Payment', 'Payment'),
        ('Verification','Verification')
    ]
, string='Type')



    @api.model
    def create(self, vals):

        values =super().create(vals)

        return values