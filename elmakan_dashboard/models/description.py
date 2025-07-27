from odoo import models,api, fields,_

class DescriptionAlmakaan(models.Model):
    _name = 'description.elmakan'
    _description = "this module is for description"

    title = fields.Text('Title')
    description = fields.Text('Description')
    text = fields.Text('Text')
    
    brand_id = fields.Many2one('brand.elmakan' , string='')
    title_seo = fields.Char('Title SEO')
    description_seo = fields.Char('description SEO')
    keywords_seo = fields.Char('Keywords SEO')
