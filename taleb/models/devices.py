from datetime import datetime ,date,timedelta
from odoo import models, fields, api
import math, random
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class Device(models.Model):
    _name = 'user.device'
    _description = ''
    user_id = fields.Char(string='User ID')
    user_name = fields.Char(string='User Name',compute='get_name' ,store=True)
    user_number = fields.Char(string='User Number',compute='get_name',store=True)
    user_relation_id = fields.Many2one('res.users',string='User Account',compute='get_name' ,store=True)
    devices = fields.One2many('id.device', 'device', string='ids')
    number_of_tokens=fields.Integer(string="Tokens",default=5)

    @api.constrains('user_id')
    def get_name(self):
        for rec in self:
            user_data = self.env['res.users'].sudo().search([('id','=',int(rec.user_id))])
            if len(user_data) != 0:
                rec.sudo().update({
                    'user_name' : user_data.name,
                    'user_number' : user_data.login,
                    'user_relation_id' : user_data.id
                })
               

            else:
                rec.update({
                    'user_name' : 'user was deleted'
                })
                

        return True
class Device(models.Model):
    _name = 'user.device.config'
    _description = ''
    number = fields.Integer(string='User Device count')
    

class DeviceID(models.Model):
    _name = 'id.device'

    device_id = fields.Char(string='Device Id')
    device = fields.Many2one('user.device', string='Device')
    is_valid = fields.Boolean(string='Is valid',default =True)
    can_login=fields.Boolean(string='Can Login',default=False)
    
   
        
    @api.constrains('can_login')
    def _check_can_login(self):
        for record in self:
            if record.can_login:
                # Set all other records with the same device to can_login = False
                self.search([
                    ('id', '!=', record.id),
                    ('device', '=', record.device.id),
                    ('can_login', '=', True)
                ]).write({'can_login': False})
    @api.model
    def create(self, vals):
        if 'device' in vals:
            device = self.env['user.device'].browse(vals['device'])

            # Check if the device has more than 5 records
            device_number = self.env['user.device.config'].search([('id' ,'!=' , False)],limit = 1)
            if device.devices and len(device.devices) >= device_number.number:
                
                # for d in device.devices:
                #     oldest_record = device.devices.sorted(key=lambda r: r.create_date)[0]
                    # today = datetime.today()
                    # one_year_ago = today - timedelta(days=365)

                    # # Check if the oldest record is more than one year old
                    # if oldest_record.create_date < one_year_ago:
                    #     # Delete the oldest record
                    # oldest_record.unlink()
                    # else:
                    #     # Raise an error if the oldest record is less than one year old
                        raise ValidationError("Cannot create a new record for this device. Maximum number of records reached.")

        return super(DeviceID, self).create(vals)
   