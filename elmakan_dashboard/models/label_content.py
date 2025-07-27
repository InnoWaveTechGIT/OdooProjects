from odoo import models,api, fields,_



class LabelContentAlmakaan(models.Model):
    _name = 'labelcontent.elmakan'
    _description = "this module is for label content elmakan"
    _rec_name ='title'
    title = fields.Text(string='Title',default='')
    text = fields.Char(string='Text',default='')
    slug = fields.Char(string='Slug',default='',compute='_compute_slug')
    link = fields.Char(string='Link',default='')
    image = fields.Binary(string='Image')
    image_url = fields.Char("image url", compute='_compute_image_url')
    image_alt = fields.Char('Image alt SEO')
    title_seo = fields.Char('Title SEO')
    description_seo = fields.Char('description SEO')
    keywords_seo = fields.Char('Keywords SEO')
    
    @api.depends('image')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print('base_url' , base_url)
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=labelcontent.elmakan&id=' + str(obj.id) + '&field=image'
            else:
                obj.image_url=''
    # content_ids = fields.Many2many('content.elmakan' , string= 'Content')
    content_ids = fields.One2many('content.elmakan' ,'labelcontent_id', string= 'Content')
    # slider_ids = fields.Many2many('brand.slider.elmakan' , string= 'Sliders')
    slider_ids = fields.One2many('brand.slider.elmakan' ,'slider_id', string= 'Sliders')
    # box_ids = fields.Many2many('boxes.elmakan' , string= 'Boxs')
    
    box_ids = fields.One2many('boxes.elmakan' ,'labelcontent_id', string= 'Boxs')
    # state = fields.Boolean(string='On WebSite',default=False)
    @api.depends('title')
    def _compute_slug(self):
        for record in self:
            if record.title:
                record.slug = record.title.lower().replace(' ','-') +f'-{record.id}'
            else:
                record.slug='' 
# class LContentAlmakaan(models.Model): 
#     _name ='label.content.elmakan'

#     label_id = fields.Many2one('labelcontent.elmakan')
#     image = fields.Binary(string='Image')
#     image_url = fields.Char("image url", compute='_compute_image_url')
#     text = fields.Text(string='Text',default='')
#     title = fields.Text(string='Title',default='')

#     @api.depends('image')
#     def _compute_image_url(self):
#         base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
#         for obj in self:
#             if obj.image:
#                 obj.image_url= base_url + '/web/image?' + 'model=label.content.elmakan&id=' + str(obj.id) + '&field=image'
#             else:
#                 obj.image_url=''


# class LSliderAlmakaan(models.Model): 
#     _name ='label.slider.elmakan'

#     label_id = fields.Many2one('labelcontent.elmakan')
#     image = fields.Binary(string='Image')
#     image_url = fields.Char("image url", compute='_compute_image_url')
#     text = fields.Text(string='Text',default='')
#     title = fields.Text(string='Title',default='')

#     @api.depends('image')
#     def _compute_image_url(self):
#         base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
#         for obj in self:
#             if obj.image:
#                 obj.image_url= base_url + '/web/image?' + 'model=label.slider.elmakan&id=' + str(obj.id) + '&field=image'
#             else:
#                 obj.image_url=''


# class LBoxAlmakaan(models.Model): 
#     _name ='label.box.elmakan'

#     label_id = fields.Many2one('labelcontent.elmakan')
#     text = fields.Text(string='Text',default='')
#     title = fields.Text(string='Title',default='')
