from odoo import models,api, fields,_



class BrandAlmakaan(models.Model):
    _name = 'brand.elmakan'
    _description = "this module is for brand"
    _rec_name ='name'

    name = fields.Char('Name')
    slug = fields.Char(string='Slug',default='',compute='_compute_slug')
    image = fields.Binary('Image')
    title = fields.Text('Title')
    categ_id = fields.Many2many('category.elmakan' , string = 'Category')
    # description_ids = fields.Many2many('description.elmakan' , string='Description')
    description_ids = fields.One2many('description.elmakan' ,'brand_id', string= 'Description')
    # content_ids = fields.Many2many('content.elmakan' ,string='Content')
    content_ids = fields.One2many('content.elmakan' ,'brand_id', string= 'Content')
    # gallery_ids = fields.Many2many('gallery.elmakan' , string='Gallery')
    gallery_ids = fields.One2many('gallery.elmakan' ,'brand_id', string= 'Gallery')
    image_url = fields.Char("image url", compute='_compute_image_url')
    
    isTopBrand = fields.Boolean(string='isTopBrand',default=False)
    state = fields.Boolean(string='On WebSite',default=False)
    title_seo = fields.Char('Title SEO')
    description_seo = fields.Char('description SEO')
    keywords_seo = fields.Char('Keywords SEO')
    image_alt = fields.Char('Image alt SEO')
    @api.depends('title')
    def _compute_slug(self):
        for record in self:
            if record.title:
                record.slug = record.title.lower().replace(' ','-') +f'-{record.id}'
            else:
                record.slug='' 
            if record.title and not record.name:
                record.name = record.title
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
                obj.image_url= base_url + '/web/image?' + 'model=brand.elmakan&id=' + str(obj.id) + '&field=image'
            else:
                obj.image_url=''


class BrandSliderAlmakaan(models.Model):
    _name = 'brand.slider.elmakan'
    _description = "this module is for brand slider elmakan"
    _rec_name ='title'
    text = fields.Text(string='Text',default='')
    title = fields.Text(string='Title',default='')
    image = fields.Binary('Image')
    image_url = fields.Char("image url", compute='_compute_image_url')
    image_alt = fields.Char('Image alt SEO')
    state = fields.Boolean(string='On WebSite',default=False)

    slider_id = fields.Many2one('labelcontent.elmakan' , string='')

    @api.depends('image')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=brand.slider.elmakan&id=' + str(obj.id) + '&field=image'
            else:
                obj.image_url=''


