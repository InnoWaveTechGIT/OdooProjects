from odoo import models,api, fields,_

class GalleryAlmakaan(models.Model):
    _name = 'gallery.elmakan'
    _description = "this module is for gallery elmakan"


    text=fields.Text(string='Text')
    image = fields.Binary(string='Image')
    image_url = fields.Char("image url", compute='_compute_image_url')
    image_alt = fields.Char('Image alt SEO')
    about_id = fields.Many2one('about.elmakan' , string='')
    brand_id = fields.Many2one('brand.elmakan' , string='')
    category_id = fields.Many2one('category.elmakan' , string='')

    title_popup=fields.Char("title_popup") 
    address_popup=fields.Char("address_popup") 
    locationMapUrl_popup=fields.Char("locationMapUrl_popup") 

    phone_popup=fields.Char("phone_popup") 
    email_popup=fields.Char("email_popup") 
    title_seo = fields.Char('Title SEO')
    description_seo = fields.Char('description SEO')
    keywords_seo = fields.Char('Keywords SEO')

    @api.depends('image')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print('base_url' , base_url)
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=gallery.elmakan&id=' + str(obj.id) + '&field=image'
            else:
                obj.image_url=''