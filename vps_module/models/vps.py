# model/vps.py
from odoo import models, fields

class VpsServer(models.Model):
    _name = 'vps.server'
    _description = 'VPS Server Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('User Admin' , required=True)
    ip_address = fields.Char(string='IP Address', required=True)
    password = fields.Char(string='Password', required=True)
    domain = fields.Char(string='Domain', required=True)
    admin_password = fields.Char(string='Admin Password', required=True)
    master_password = fields.Char(string='Master Password', required=True)
    creation_date = fields.Date(string='Date of Creation', required=True)
    renew_date = fields.Date(string='Renew Date', required=True)
    odoo_charter = fields.Text(string='Charter of Odoo')


class VpsServer(models.Model):
    _name = 'cpanel.server'
    _description = 'VPS Server Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('User Admin' , required=True)
    cpanel= fields.Char('C Panel link' , required=True)
    password = fields.Char('password' , required=True)
    creation_date = fields.Date(string='Date of Creation', required=True)
