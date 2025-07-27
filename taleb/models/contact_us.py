from odoo import models,api, fields,_



class ContactUsTaleb(models.Model):
    _name = 'contact.us'
    _description = "this module is for contact.us"

    name = fields.Char(string='Full Name')
    email = fields.Char(string='email ')
    phone_number = fields.Char(string='Phone')
    message =fields.Text(string='Message')
    reason=fields.Text(string='Reason')
