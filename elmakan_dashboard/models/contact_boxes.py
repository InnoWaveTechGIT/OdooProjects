from odoo import models,api, fields,_



# class ContactAlmakaan(models.Model):
#     _name = 'contact.elmakan'
#     _description = "this module is for contact"
#     _rec_name = 'title'
#     title = fields.Char('Title')
#     text = fields.Text('Text')
#     link = fields.Char('Link')
#     icon = fields.Binary('Icon')
#     image_url = fields.Char("image url", compute='_compute_image_url')
#     @api.depends('icon')
#     def _compute_image_url(self):
#         base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
#         print('base_url' , base_url)
#         for obj in self:
#             if obj.icon:
#                 obj.image_url= base_url + '/web/image?' + 'model=contact.elmakan&id=' + str(obj.id) + '&field=icon'
#             else:
#                 obj.image_url=''