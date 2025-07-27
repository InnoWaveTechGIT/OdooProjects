

from odoo import models,api, fields,_
import os 
import base64

class AboutAlmakaan(models.Model):
    _name = 'about.elmakan'
    _description = "this module is for about elmakan"
    _rec_name ='text'
    text=fields.Text(string='Text',default='')
    video_url= fields.Char(string='video url',default='')
    content_ids = fields.One2many('content.elmakan' ,'about_id', string= 'Content')
    hero_ids = fields.Many2many('hero.section.elmakan' , string= 'Heros')
    # gallery_ids = fields.Many2many('gallery.elmakan' , string= 'Gallery')
    gallery_ids = fields.One2many('gallery.elmakan' ,'about_id', string= 'Gallery')
    
    state = fields.Boolean(string='On WebSite',default=False)
    # course_sections_ids =fields.One2many('section', 'course_id', string='Sections')
    title_seo = fields.Char('Title SEO')
    description_seo = fields.Char('description SEO')
    keywords_seo = fields.Char('Keywords SEO')
    