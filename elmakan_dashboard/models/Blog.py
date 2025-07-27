from odoo import models,api, fields,_
from odoo.exceptions import ValidationError
from datetime import datetime ,date,timedelta


class BlogElmakan(models.Model):
    _name = 'blog.almakan'
    _description = "this module is for blog "
    _rec_name ='slug'
    image = fields.Image(string='Image')
    image_url= fields.Char(string='Image url',compute='_compute_image_url')
    image_alt = fields.Char('Image alt SEO')
    title = fields.Char(string='Title', default='')
    content =  fields.Html(string='Content',default='')
    slug = fields.Char(string='Slug',default='',compute='_compute_slug')
    tag = fields.Char(string='tag')
    state = fields.Boolean(string='On WebSite',default=False)
    title_seo = fields.Char('Title SEO')
    description_seo = fields.Char('description SEO')
    keywords_seo = fields.Char('Keywords SEO')
    @api.depends('title')
    def _compute_slug(self):
        for record in self:
            if record.title:
                record.slug = record.title.lower().replace(' ','-')
            else:
                record.slug='' 
    @api.depends('image')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=blog.almakan&id=' + str(obj.id) + '&field=image'
            else :
                obj.image_url= ''


