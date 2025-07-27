from odoo import models, fields, api


class torbet_app(models.Model):
    _name = 'user.token'
    _description = ''
    _rec_name='user_id'

    user_id = fields.Char(string='User ID')
    token = fields.Text(string='Token')
    fire_base = fields.Text(string='Fire Base Token')
    is_android = fields.Boolean('Is Android')
    