from odoo import models,api, fields,_



class DailyArticle(models.Model):
    _name = 'daily.article'
    _description = "this module is for articles"

    name = fields.Char(default='Daily Article')
    title = fields.Text(string='Title')

