from odoo import models,api, fields,_



class ClientAlmakaan(models.Model):
    _name = 'client.elmakan'
    _description = "this module is for client elmakan"
    _rec_name = 'title'
    title = fields.Char('Title',default='')
    text = fields.Text('Text',default='')
    company_ids = fields.One2many('client.company.elmakan' , 'client_id' , string= 'Companies')
    state = fields.Boolean(string='On WebSite',default=False)
    title_seo = fields.Char('Title SEO')
    description_seo = fields.Char('description SEO')
    keywords_seo = fields.Char('Keywords SEO')
    
class ClientCompanyAlmakan(models.Model):
    _name = 'client.company.elmakan'
    _description = "this module is for client company elmakan"  

    client_id = fields.Many2one('client.elmakan')
    key = fields.Char('Company Name',default='')
    value =  fields.Char('Category',default='')
    title_seo = fields.Char('Title SEO')
    description_seo = fields.Char('descreption SEO')