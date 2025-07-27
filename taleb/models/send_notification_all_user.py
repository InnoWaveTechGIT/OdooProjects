from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
import re
import os
import time
import base64
import requests
import json
from odoo.exceptions import UserError
from . import send_notification



class NotificationAllUsers(models.Model):
    _name = 'users.notificationall'
    _description = 'App Notification'
    
    title = fields.Char(required=True)
    body = fields.Text(required=True)
    
    @api.model
    def create(self, vals):
        res = super(NotificationAllUsers, self).create(vals)
        server_key = 'AAAAmP4zE2k:APA91bE44rRlmk44y2BASpsjkKxOmIkfFvWGZHyfrS_IV5FPoFrXYV8ODJXiyiwUFL5Up-jD8gY_q7pBrIba5duUqO2EXm7nrAFL2yFqcmqp748FnxkfG5ByH94vhzBssMVJ3wbQgilf'
        
        api_url = 'https://fcm.googleapis.com/fcm/send'
        user_token=self.env['user.token'].search_read([],['fire_base'])
        device_tokens=[]
        for i in user_token:
            device_tokens.append(i['fire_base'])
        
        payload = {
            'notification': {
                'title': vals['title'],
                'body': vals['body']
            },
            'data': {
                'foo': 'bar'
            },
            'registration_ids': device_tokens
        }

        headers = {
            'Authorization': 'key=' + server_key,
            'Content-Type': 'application/json'
        }

        response = requests.post(api_url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            print("Success")
            
            
        else:
            title = _("Failed operation!")
            message = _("Something wrong happened ")
            print(message)
        return res 
           
        

    def create(self, vals):
        res = super(NotificationAllUsers, self).create(vals)
        server_key = 'AAAAmP4zE2k:APA91bE44rRlmk44y2BASpsjkKxOmIkfFvWGZHyfrS_IV5FPoFrXYV8ODJXiyiwUFL5Up-jD8gY_q7pBrIba5duUqO2EXm7nrAFL2yFqcmqp748FnxkfG5ByH94vhzBssMVJ3wbQgilf'  # Replace with your server key
        api_url = 'https://fcm.googleapis.com/fcm/send'

        payload = {
            'notification': {
                'title': vals['title'],
                'body': vals['body']
            },
            'data': {
                'foo': 'bar'
            },
            'to': server_key  # Use server token instead of registration_ids
        }

        headers = {
            'Authorization': 'key=' + server_key,
            'Content-Type': 'application/json'
        }

        response = requests.post(api_url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            print("Success" )
        else:
            title = _("Failed operation!")
            message = _("Something wrong happened ")
            print(message)
        return res