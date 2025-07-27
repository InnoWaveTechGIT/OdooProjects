from odoo import models,api, fields,_
class ContentAlmakaan(models.Model):
    _name = 'content.elmakan'
    _description = "this module is for content elmakan"  

    text = fields.Text(string='Text',default='')
    title = fields.Char(string='title',default='')
    link = fields.Char(string='link',default='')
    image = fields.Binary(string='Image')
    image_url = fields.Char("image url", compute='_compute_image_url')
    image_alt = fields.Char('Image alt SEO')
    about_id = fields.Many2one('about.elmakan' , string='')
    brand_id = fields.Many2one('brand.elmakan' , string='')
    category_id = fields.Many2one('category.elmakan' , string='')
    feature_id = fields.Many2one('feature.elmakan' , string='')
    home_id = fields.Many2one('home.elmakan' , string='')
    labelcontent_id = fields.Many2one('labelcontent.elmakan' , string='')

    logo = fields.Binary(string='Logo')
    logo_url = fields.Char("Logo url", compute='_compute_logo_url')
    title_seo = fields.Char('Title SEO')
    description_seo = fields.Char('description SEO')
    keywords_seo = fields.Char('Keywords SEO')

    @api.depends('image')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=content.elmakan&id=' + str(obj.id) + '&field=image'
            else:
                obj.image_url=''
    @api.depends('logo')
    def _compute_logo_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for obj in self:
            if obj.logo:
                obj.logo_url= base_url + '/web/image?' + 'model=content.elmakan&id=' + str(obj.id) + '&field=logo'
            else:
                obj.logo_url=''            