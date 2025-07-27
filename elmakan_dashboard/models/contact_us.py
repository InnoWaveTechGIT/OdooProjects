from odoo import models,api, fields,_



class ContactUsAlmakaan(models.Model):
    _name = 'contact.us.elmakan'
    _description = "this module is for contact us elmakan"

    location_ids = fields.One2many('location.content.us.elmakan' , 'contactus_id' , string= 'Locations')
    ourAgents_ids = fields.One2many('ouragents.content.us.elmakan' , 'contactus_id' , string= 'OurAgents')
    form_ids = fields.One2many('form.content.us.elmakan' , 'contactus_id' , string= 'Forms')
    state = fields.Boolean(string='On WebSite',default=False)
    email = fields.Char('Email')
    Phone = fields.Char('Phone')
    title_seo = fields.Char('Title SEO')
    description_seo = fields.Char('description SEO')
    keywords_seo = fields.Char('Keywords SEO')
class LocationContentUsAlmakan(models.Model):
    _name = 'location.content.us.elmakan'
    _description = "this module is for location content us elmakan"  

    contactus_id = fields.Many2one('contact.us.elmakan')  

    region = fields.Char(string='region',default='')
    city = fields.Char(string='city',default='')
    address = fields.Char(string='address',default='')
    phone = fields.Char(string='phone',default='')
    fax = fields.Char(string='fax',default='')
    poBoxNumber = fields.Char(string='poBoxNumber',default='')
    poBoxLocation = fields.Char(string='poBoxLocation',default='')
    email = fields.Char(string='email',default='')

class OurAgentsContentUsAlmakan(models.Model):
    _name = 'ouragents.content.us.elmakan'
    _description = "this module is for ouragents content us elmakan"  

    contactus_id = fields.Many2one('contact.us.elmakan') 

    region = fields.Char(string='region',default='')
    name = fields.Char(string='name',default='') 
    address = fields.Char(string='address',default='')
    phone = fields.Char(string='phone',default='')
    fax = fields.Char(string='fax',default='')
    mobile = fields.Char(string='mobile',default='')
    email = fields.Char(string='email',default='')


class FormContentUsAlmakan(models.Model):
    _name = 'form.content.us.elmakan'
    _description = "this module is for form content us elmakan"  

    contactus_id = fields.Many2one('contact.us.elmakan')  

    name = fields.Char(string='name',default='')
    email = fields.Char(string='email',default='')
    phone = fields.Char(string='phone',default='')
    company_name = fields.Char(string='companyName',default='')
    message = fields.Char(string='message',default='')