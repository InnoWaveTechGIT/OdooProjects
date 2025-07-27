from odoo import models,api, fields,_


class ResCountryStateInherit(models.Model):
    _inherit = 'res.country.state'
    _description = "this module is for res.country.state"
    _order = 'order_number asc'
    
    location_ids = fields.One2many('location', 'location_id', string='location_ids')
    order_number = fields.Integer('order number')


    

class Location(models.Model):
    _name = 'location'
    _description = "this module is for location"
    _order = 'order_number asc'
    
    name = fields.Char(string='Location Name')
    location_id = fields.Many2one('res.country.state', string='location_id')
    order_number = fields.Integer('order number')