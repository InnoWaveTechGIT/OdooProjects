from odoo import models, api, fields
from odoo.exceptions import ValidationError
from datetime import datetime ,date,timedelta
import os
from datetime import datetime ,timedelta
import base64 
from os import environ
from odoo.exceptions import ValidationError
import time
import json
from dotenv import load_dotenv
load_dotenv()

class Notificationscool(models.Model):
    _name = 'notification.school'


    comment = fields.Char('Comment')
    user_id = fields.Many2one('res.users')
    data = fields.Char('Data')
    is_seen = fields.Boolean('Is Seen')
   
    notification_type = fields.Selection(selection=[
        ('Events', 'Events'),
        ('Message', 'Message'),
        ('HomeWork','HomeWork')
    ]
    , string='Type')

    @api.model
    def create(self, vals):
        values =super().create(vals)
        data = json.dumps(values.data)
        payload = data
        noti_data={
            'user_id':values.user_id,
            'data':payload,
            'notification_type':values.notification_type
        }
        f_token = self.env['user.token.school'].search([('user_id' , '=' , values.user_id.id)])
        f_token = f_token.fire_base_token
        # self.send_notification(f_token,payload)

        return values

    def send_notification(self,deviceToken,payload):
        serverToken = os.getenv('SERVER_TOKEN')
    

        headers = {
                'Content-Type': 'application/json',
                'Authorization': 'key=' + serverToken,
            }
        body = {
                'notification': {'title': payload['title'],
                                    'body': payload['comment']
                                    },
                'to':
                    deviceToken,
                'priority': 'high',
                'data':payload,
                }
        response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))