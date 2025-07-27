from odoo import models,api, fields,_

class BoxesAlmakaan(models.Model):
    _name = 'boxes.elmakan'
    _description = "this module is for boxes.elmakan"


    text =fields.Text(string='text')
    title =fields.Char(string='title')

    category_id = fields.Many2one('category.elmakan' , string='')
    labelcontent_id = fields.Many2one('labelcontent.elmakan' , string='')
    title_seo = fields.Char('Title SEO')
    description_seo = fields.Char('description SEO')
    keywords_seo = fields.Char('Keywords SEO')
