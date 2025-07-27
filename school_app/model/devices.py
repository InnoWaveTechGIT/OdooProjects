from odoo import api, models, fields, _
from odoo.exceptions import UserError
import os
from odoo.exceptions import ValidationError

class StudentDevices(models.Model):
    _name = 'student.devices'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users' , string = 'User')
    device_ids = fields.One2many('student.devices.line' , 'user_id' , string='Devices')



class StudentDevices(models.Model):
    _name = 'student.devices.line'

    user_id = fields.Many2one('student.devices')
    device_name = fields.Char('Name')
    identification = fields.Char('Iden')
    is_admin = fields.Boolean('Admin')


    @api.model
    def create(self, vals):
        user_id = vals.get('user_id')
        existing_records_count = self.search_count([('user_id', '=', user_id)])
        if existing_records_count >= 3:
            raise ValidationError('Only three devices are allowed per user.')

        return super(StudentDevices, self).create(vals)