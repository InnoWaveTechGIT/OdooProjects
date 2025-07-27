from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
import requests
import json


class platformControl(models.Model):
    _name = 'platform.control'
    _description = "this module is for platform.control"

    platform_type =fields.Selection(
         [('ios', 'ios'), ('android', 'android')] ,string="Platform Type",required = True
    ) 
    min_version = fields.Char(string='Minimum Version')
    max_version = fields.Char(string='Maximum Version')
    android_url = fields.Char(string='Android Url')
    ios_url = fields.Char(string='IOS Url')
    what_new = fields.Html(string='What\'s new')
    message = fields.Text('Message')
    can_send = fields.Boolean('Can send')

    @api.constrains('write_date')
    def check_rec_num(self):
        x = self.env['platform.control'].search_count([('platform_type', '=', self.platform_type)])
        if x > 1:
            raise ValidationError(
                _('''هناك سجل لنفس البلاتفورم, يرجى التعديل عليه 
:)
                
                '''))
    
    def send_notification(self):
        print('asdasd')
        device_tokens=[]
        server_key = 'AAAAmP4zE2k:APA91bE44rRlmk44y2BASpsjkKxOmIkfFvWGZHyfrS_IV5FPoFrXYV8ODJXiyiwUFL5Up-jD8gY_q7pBrIba5duUqO2EXm7nrAFL2yFqcmqp748FnxkfG5ByH94vhzBssMVJ3wbQgilf'
        
        api_url = 'https://fcm.googleapis.com/fcm/send'
        if self.platform_type == 'ios':
            is_android = False
        else :
            is_android = True
        user_token=self.env['user.token'].search_read([('is_android' , '=' , is_android)],['fire_base'])
        # device_tokens=['cN6-cAK8Q7WsOO5O0gCjVu:APA91bG6zUn3Lm-v8wYb8prrS4dkTsu695GxCx5Wib0cRSOPhQCZLMGe0-GC4_cFPVW1_IvXFLsFtOeIebP3uTW50hhD7lzf3_xoryqyvy7BRA9qVZRzuxzWVTpxdJ_9nXrxSLoLG38v']
        for i in user_token:
            device_tokens.append(i['fire_base'])
        
        payload = {
            'notification': {
                'title': 'تحديث جديد',
                'body': self.message + ' ' + self.max_version
            },
            'data': { 'url' : self.ios_url if self.ios_url else self.android_url},
            'registration_ids': device_tokens
        }

        headers = {
            'Authorization': 'key=' + server_key,
            'Content-Type': 'application/json'
        }
        if self.can_send == True:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            print(' response.status_code >>> ',response.status_code)

            if response.status_code == 200:
                
                print(' response.status_code >>> ',response.status_code)
            else:
                title = _("Failed operation!")
                message = _("Something wrong happened ")
        else:
             raise ValidationError("يجب عليك تعديل نسخة الإصدار أولا")
        return True 
    def write(self, vals):
        
        if 'max_version' in vals and vals['max_version'] != False:
            vals['can_send'] = True

        return super().write(vals)