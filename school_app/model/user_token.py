from odoo import models,api, fields,_
import jwt
import os
from datetime import datetime ,timedelta
import base64 
from os import environ
from odoo.exceptions import ValidationError
import time
from dotenv import load_dotenv
load_dotenv()
class UserrTokenschool(models.Model):
    _name = 'user.token.school'
    _description = "this module is for user_token school"
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users' , 'User Id'  ,state={
        'done': [('readonly', True)],
    })
    access_token = fields.Char('Access Token')
    access_token_time = fields.Datetime('Access Token Time')
    # refresh_token = fields.Char('Refresh Token')
    refresh_token_time = fields.Datetime('Refresh Token Time')
    state = fields.Selection(selection=[
       ('draft', 'Draft'),
       ('done', 'Done'),
       
   ], string='Status', required=True, readonly=True, copy=False,
   tracking=True, default='draft')
    
    fire_base_token = fields.Char('Fire base Token')


    @api.model
    def create(self, vals):
        try : 
            date_now = datetime.today()
            if 'user_id' in vals and vals['user_id'] != []:
                vals['access_token_time'] = date_now
                vals['refresh_token_time'] = date_now
                payload = {
                        'id': vals['user_id'],
                        'timestamp' : str(date_now)
                        }
                SECRET = os.getenv('JWT_SECRET')
                enc = jwt.encode(payload, SECRET) 
                vals['state'] = 'done'
                #search if user have token :
                user_id=vals.get('user_id')
                token_obj=self.env['auth.api.key'].sudo().search([('user_id','=',int(user_id))])
                if token_obj:
                    pass
                else:
                    time_s=str(time.time())
                    token_obj=self.env['auth.api.key'].sudo().create({'name':str(user_id)+time_s,'user_id':user_id,'key':enc})
                #vals['access_token'] = token_obj
                vals['access_token'] = enc
                # vals['refresh_token'] = enc
                values =super().create(vals)
                return values
            else:
                raise ValidationError("يرجى تحديد المستخدم")
        except Exception as e: 
            raise ValidationError(e)
        
    def write(self, vals):
        date_now = datetime.today()
        if 'refresh_token_time' in vals or 'access_token_time' in vals :
            
            time_difference = date_now - self.access_token_time

            # Check if the time difference is greater than one day
            if time_difference > timedelta(days=1):
                payload = {
                        'id': self.user_id.id,
                        'timestamp' : str(date_now),}
                SECRET = os.getenv('JWT_SECRET')
                enc = jwt.encode(payload, SECRET) 
                vals['state'] = 'done'
                token_obj=self.env['auth.api.key'].sudo().search([('user_id','=',self.user_id.id)])
                if token_obj:
                    token_obj.sudo().write({'key':enc})
                vals['access_token'] = enc
                # vals['refresh_token'] = enc
                vals['access_token_time'] = date_now
                vals['refresh_token_time'] = date_now
            elif  date_now - self.refresh_token_time > timedelta(minutes=15):
                payload = {
                        'id': self.user_id.id,
                        'timestamp' : str(date_now)}
                SECRET = os.getenv('JWT_SECRET')
                enc = jwt.encode(payload, SECRET) 
                vals['state'] = 'done'
                token_obj=self.env['auth.api.key'].sudo().search([('user_id','=',self.user_id.id)])
                if token_obj:
                    token_obj.sudo().write({'key':enc})
                vals['access_token'] = enc
                vals['refresh_token_time'] = date_now
            
       
        values =super().write(vals)
        return values




