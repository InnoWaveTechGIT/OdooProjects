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
import requests
from dotenv import load_dotenv
# import google.auth
# from google.auth.transport import requests as req
# from google.auth import credentials
# from google.oauth2 import service_account
load_dotenv()

def _abs_rout(self,data):
    path1=''
    

    abs = os.path.dirname(os.path.abspath(__file__))
    abs_sp =abs.split("/")
    
    for i in abs_sp:
        if i !='models':
            path1 += i +'/'
    return path1
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

    # @api.model
    # def create(self, vals):
    #     values =super().create(vals)
    #     print("data ?>>>>> " , values.data)
    #     print("data ?>>>>> " , type(values.data))
    #     data = json.dumps(values.data)
    #     # print("data ?>>>>> " , data)
    #     payload = vals['data']
    #     noti_data={
    #         'user_id':values.user_id,
    #         'data':payload,
    #         'notification_type':values.notification_type
    #     }
    #     f_token = self.env['user.token.school'].search([('user_id' , '=' , values.user_id.id)])
    #     f_token = f_token.fire_base_token
    #     print('asdasadasdasd')
    #     self.send_notification(f_token,payload)
    #     print(123123123)

    #     return values


    # def _get_access_token(self):
    #     """Retrieve a valid access token that can be used to authorize requests.

    #     :return: Access token.
    #     """
    #     data=os.path.dirname(os.path.abspath(__file__))
    #     module_path = _abs_rout(self ,data) + "schoolapp-910f6-96da3b509eb8.json"
    #     credentials = service_account.Credentials.from_service_account_file(
    #         module_path, scopes=['https://www.googleapis.com/auth/firebase.messaging'])
    #     request = google.auth.transport.requests.Request()
    #     credentials.refresh(request)
    #     return credentials.token



    # def send_notification(self, deviceToken, payload):
    #     serverToken = os.getenv('SERVER_TOKEN')
    #     # payload = json.loads(payload)
    #     headers = {
    #         'Authorization': 'Bearer ' + self._get_access_token(),
    #         'Content-Type': 'application/json; UTF-8',
    #         }
    #     print("Payload >>>>>>>>>> " , payload)
    #     body = {
    #         "message": {
    #             'notification': {
    #                 'title': payload['title'],
    #                 'body': payload['comment']
    #             },
    #             'token': 'cbHB69ibT4qpJgQ4pYyvKr:APA91bHs8jO7iknAfoY81JpDWb6qU4ydx6BXNw-t18N0e8f_NfbQhuCYPETG8l85dMAl49cO5QjfQNNIoAnbryKhl_6s4dNL9apK5eAG3VENYyk4rVFfb-Tx2DYnV-z6wzmJmbaOLhku',
    #             "data":payload,
    #         }
            
    #     }

    #     response = requests.post("https://fcm.googleapis.com/v1/projects/schoolapp-910f6/messages:send", headers=headers, data=json.dumps(body))

    #     print(response.text)