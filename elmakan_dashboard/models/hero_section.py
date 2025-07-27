from odoo import models,api, fields,_



class HeroSection(models.Model):
    _name = 'hero.section.elmakan'
    _description = "this module is for hero.section"
    _rec_name ='title'

    image = fields.Binary(string='Image')
    image_url = fields.Char("image url", compute='_compute_image_url')
    image_alt = fields.Char('Image alt SEO')
    text = fields.Html(string='Text',default='')
    title = fields.Char(string='title',default='')
    state = fields.Boolean(string='state',default=False)
    title_seo = fields.Char('Title SEO')
    description_seo = fields.Char('description SEO')
    keywords_seo = fields.Char('Keywords SEO')
    
    @api.depends('image')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=hero.section.elmakan&id=' + str(obj.id) + '&field=image'
            else:
                obj.image_url=''