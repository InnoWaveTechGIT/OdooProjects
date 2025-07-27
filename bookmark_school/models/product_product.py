from odoo import models, fields, api


class MyModel(models.Model):
    _inherit = 'product.template'

    school_id = fields.Many2one('product.school', string="School")


class MyModelSchool(models.Model):
    _name = 'product.school'
    _rec_name = 'name'

    name = fields.Char(string="Name")


class MyModelSale(models.Model):
    _inherit = 'sale.order.line'

    school_id = fields.Many2one(related="product_template_id.school_id")

class MyModelSale(models.Model):
    _inherit = 'sale.order'

    phone = fields.Char(related="partner_id.phone")
    email = fields.Char(related="partner_id.email")
