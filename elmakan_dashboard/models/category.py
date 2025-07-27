from odoo import models,api, fields,_



class CategoryAlmakaan(models.Model):
    _name = 'category.elmakan'
    _description = "this module is for hero.section"
    _rec_name = 'slug'
    text=fields.Text(string='Text')
    image = fields.Binary(string='Image')
    title =fields.Char(string='title')
    # content_ids = fields.Many2many('content.elmakan' ,string= 'Content')
    content_ids = fields.One2many('content.elmakan' ,'category_id', string= 'Content')
    # boxes_ids = fields.Many2many('boxes.elmakan' ,string= 'Boxes')
    boxes_ids = fields.One2many('boxes.elmakan' ,'category_id', string= 'Boxes')
    # gallery_ids = fields.Many2many('gallery.elmakan' ,string= 'Gallery')
    gallery_ids = fields.One2many('gallery.elmakan' ,'category_id', string= 'Gallery')
    image_url = fields.Char("image url", compute='_compute_image_url')
    slug = fields.Char(string='Slug',default='',compute='_compute_slug')
    # video= fields.Text(string='video')
    state = fields.Boolean(string='On WebSite',default=False)
    title_in_section_boxes=fields.Char(string="title in section boxes")
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

    @api.depends('image')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print('base_url' , base_url)
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=category.elmakan&id=' + str(obj.id) + '&field=image'
            else:
                obj.image_url=''



   