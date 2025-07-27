from odoo import models,api, fields,_



class MailAlmakaan(models.Model):
    _name = 'mail.elmakan'
    _description = "this module is for mail elmakan"

    app_key = fields.Char(string='App Key',default='',required=True)
    company_email = fields.Char(string='Company Email',default='',required=True,help='Specifies the e-mail address through which the e-mails will be sent')

    feature_ids = fields.One2many('feature.mail.elmakan' , 'mail_id' , string= 'Forms')
    contact_us_email = fields.Char(string='Email',default='',required=True)
class FeatureMailAlmakan(models.Model):
    _name = 'feature.mail.elmakan'
    _description = "this module is for feature mail elmakan"  

    mail_id = fields.Many2one('mail.elmakan')
    feature_id = fields.Many2one('feature.elmakan',required=True)
    email = fields.Char(string='Email',default='',required=True)
      