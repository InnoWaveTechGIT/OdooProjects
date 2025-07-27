from odoo import models,api, fields,_



class FeatureAlmakaan(models.Model):
    _name = 'feature.elmakan'
    _description = "this module is for feature elmakan"
    _rec_name = 'name'

    name = fields.Char('Name')
    slug = fields.Char(string='Slug',default='',compute='_compute_slug')
    title = fields.Text('Title',default='')
    text = fields.Text('Text',default='')
    # content_ids = fields.Many2many('content.elmakan' ,string= 'Content')
    content_ids = fields.One2many('content.elmakan' ,'feature_id', string= 'Content')
    form_ids = fields.One2many('form.feature.elmakan' , 'feature_id' , string= 'Forms')
    # state = fields.Boolean(string='On WebSite',default=False)
    link = fields.Char(string='link',default='')
    image = fields.Binary(string='Image')
    image_url = fields.Char("image url", compute='_compute_image_url')
    image_alt = fields.Char('Image alt SEO')
    title_seo = fields.Char('Title SEO')
    description_seo = fields.Char('description SEO')
    keywords_seo = fields.Char('Keywords SEO')
    

    @api.constrains('name')
    def _compute_title(self):
        for record in self:
            if record.name and not record.title :
                record.title = record.name
            else:
                record.title='' 
    @api.depends('image')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print('base_url' , base_url)
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=feature.elmakan&id=' + str(obj.id) + '&field=image'
            else:
                obj.image_url=''

    @api.depends('title')
    def _compute_slug(self):
        for record in self:
            if record.title:
                record.slug = record.title.lower().replace(' ','-') +f'-{record.id}'
            else:
                record.slug='' 
            if record.title and not record.name:
                record.name = record.title

# class FeatureContentAlmakaan(models.Model):
#     _name = 'feature.content.elmakan'
#     _description = "this module is for feature content elmakan"  

#     feature_id = fields.Many2one('feature.elmakan')
#     text = fields.Text(string='Text',default='')
#     title = fields.Char(string='title',default='')
#     link = fields.Char(string='link',default='')
#     image = fields.Binary(string='Image')
#     image_url = fields.Char("image url", compute='_compute_image_url')
    

#     @api.depends('image')
#     def _compute_image_url(self):
#         base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
#         for obj in self:
#             if obj.image:
#                 obj.image_url= base_url + '/web/image?' + 'model=feature.content.elmakan&id=' + str(obj.id) + '&field=image'
#             else:
#                 obj.image_url=''

class FormContentUsAlmakan(models.Model):
    _name = 'form.feature.elmakan'
    _description = "this module is for form feature elmakan"  

    feature_id = fields.Many2one('feature.elmakan')

    name = fields.Char(string='name',default='')
    email = fields.Char(string='email',default='')
    phone = fields.Char(string='phone',default='')
    company_name = fields.Char(string='companyName',default='')
    message = fields.Char(string='message',default='')                