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
def _abs_rout(self,data):
    path1=''
    abs = os.path.dirname(os.path.abspath(__file__))
    abs_sp =abs.split("/")
    for i in abs_sp:
        if i !='models':
            path1 += i +'/'
    return path1
class Conversation(models.Model):
    
    _name='support.conversation'
    _description='this model for testing purposes display conversations to support  '
    _rec_name ='user_id'
    user_id=fields.Many2one('res.users',string='User',required = True)
    
    Support_id=fields.Many2one('res.users',string='Support')
    message_ids=fields.One2many('support.message','conversation_id' , string = 'Message ids')
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        args += ['|', ('Support_id', '=', False), ('Support_id', '=', self.env.uid)]
        return super(Conversation, self).search(args, offset, limit, order, count)
class Message(models.Model):
    _name='support.message'
    _description='this model for testing purpose only for messages'
    _rec_name ='user_id'
    image_ids = fields.One2many('support.message.images','image_id',string='Image')
    user_id=fields.Many2one('res.users',string='User',default=lambda self: self.env.user )
    body=fields.Text(string='body')
    date=fields.Datetime(string="Created Date", default=fields.Datetime.now)
    conversation_id=fields.Many2one('support.conversation',string = 'Conversation id',ondelete='cascade')
    @api.model
    def create(self, vals):
        module_path= ''
        time_stamp = str(time.time())
        data = os.path.dirname(os.path.abspath(__file__))
        mod =_abs_rout(self ,data)
        if 'conversation_id' not in vals or vals['conversation_id'] =="":
            
            conversation_data={
            'user_id':vals['user_id']
            
        }
            create_conversation=self.env['support.conversation'].create(conversation_data)
            vals['conversation_id'] = create_conversation.id
        return super().create(vals)
    class Message(models.Model):
        _name='support.message.images'
        _description='this model for testing purpose only for messages'
        
        image_id = fields.Many2one('support.message',readonly= True)
        image = fields.Binary(string='Image')
        image_file_name = fields.Char("File Name")
        image_path = fields.Char(string="Image Url",readonly= True)
        image_full_url = fields.Char(string="Image Full Url",readonly= True)
        @api.model
        def create(self, vals):
            module_path= ''
            
            time_stamp = str(time.time())
            data = os.path.dirname(os.path.abspath(__file__))
            mod =_abs_rout(self ,data)
            
            # Set the conversation_id and support_id fields based on the current conversation record
            

            if "image_file_name" in vals and vals['image_file_name']!= False:
                
                if "image_file_name" in vals and "image" in vals and vals["image_file_name"] != False and vals["image"] != False:
                    try:

                        time_stamp = str(time.time())
                        module_path = _abs_rout(self ,data)+"static/messages_images"#loc
            
                        isExist = os.path.exists(module_path)
                        if isExist == False:
                            os.mkdir(module_path)

                        with open(os.path.join(module_path, time_stamp + vals["image_file_name"].replace(" ", "")), "wb+") as f:
                            f.write(base64.b64decode(vals["image"]))
                    except Exception as e:
                            print('asdasdasd')

                    vals["image_full_url"] = module_path + '/' + \
                    time_stamp + vals["image_file_name"].replace(" ", "")
                    vals["image_path"] = "/taleb/static/messages_images/" + \
                    time_stamp + vals["image_file_name"].replace(" ", "")
                
            return super().create(vals)
        
        
