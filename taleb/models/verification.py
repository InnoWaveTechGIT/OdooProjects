from datetime import datetime ,date
from odoo import models, fields, api
import math, random
from dateutil.relativedelta import relativedelta

class torbet_app(models.Model):
    _name = 'user.verification'
    _description = ''
    _rec_name='user_id'

    user_id = fields.Char(string='User ID')
    user_name = fields.Char(string='User Name',compute='get_name')
    user_phone = fields.Char(string='User Phone',compute='get_name')
    code = fields.Char(string='Verification Code' , compute='_get_verification_code', store=True)
    is_valid = fields.Boolean(string='Is valid' ,compute='set_is_unvalid',default =True)
    type = fields.Selection(
        [('1', 'Password'), ('2', 'Confirm Phone'),('3','Email Verification')], string="Type" , default = '2')
    
    @api.constrains('user_id')
    def get_name(self):
        for rec in self:
            user_data = self.env['res.users'].search([('id','=',rec.user_id)])
            if len(user_data) != 0:
                rec.update({
                    'user_name' : user_data.name
                })
                rec.update({
                    'user_phone' : user_data.login
                })

            else:
                rec.update({
                    'user_name' : 'user was deleted'
                })
                rec.update({
                    'user_phone' : 'user was deleted'
                })

        return True
    def set_is_unvalid(self):
        date_now = datetime.now()
        for rec in self:
            date_4 =rec.write_date +relativedelta(hours=4)
            if date_4 > date_now :
                rec.update({
                    'is_valid' :True
                })
            else :
                rec.update({
                    'is_valid' :False
                })
              
        

    @api.depends('write_date')
    def _get_verification_code(self) :

        for rec in self:

            digits = "0123456789"
            OTP = ""

            for i in range(6) :
                OTP += digits[math.floor(random.random() * 10)]
            
            rec.update({
                'code' : OTP
            })


