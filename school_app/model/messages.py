from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
import re
import os
import time
import base64
import requests
import json
from odoo.exceptions import UserError

class Conversation(models.Model):
    
    _name='school.conversation'
    _description='this model for testing purposes display conversations to school  '
    _rec_name ='user_id'

    user_id=fields.Many2one('res.users',string='User',required = True)
    message_ids=fields.One2many('school.message','conversation_id' , string = 'Message ids')
    

class Message(models.Model):
    _name='school.message'
    _description='this model for testing purpose only for messages'
    _rec_name ='user_id'
    _order = 'date desc'

    image_ids = fields.One2many('images.school.app','message_id',string='Image')
    user_id=fields.Many2one('res.users',string='User',default=lambda self: self.env.user )
    body=fields.Text(string='body')
    date=fields.Datetime(string="Created Date", default=fields.Datetime.now)
    conversation_id=fields.Many2one('school.conversation',string = 'Conversation id',ondelete='cascade')
    user_ids = fields.Many2many('res.users', string='Users')
    
    @api.model
    def create(self, vals):
        values = super().create(vals)
        for i in values:
            for user in i.conversation_id.user_id.ids:
                notification_date={}
                notification_date = {
                    'comment' : 'New Message',
                    'user_id' : user,
                    'data' : {"id": str(i.conversation_id.id ),
                              "date" : str(i.date) ,
                              "title": 'New Message',
                              "comment" : i.body,
                              },
                    'notification_type' : 'Message'
                }
                self.env['notification.school'].create(notification_date)

        return values
    

    