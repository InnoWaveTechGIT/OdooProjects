from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class productTemplateInherit(models.Model):
    _inherit = 'product.supplierinfo'


    administrativ_and_logistic = fields.Integer('Administrative & Logistic LT')
    container_booking_lt = fields.Integer('Container Booking LT')
    tranit_lt = fields.Integer('Transit LT')
    Mimar_reception_redispatch = fields.Integer('Mimar Reception & Redispatch LT')
    manufacturing = fields.Integer('Manufacturing LT')
    delay = fields.Integer('Delivery LeadTime' , compute = '_get_delay')

    @api.depends('administrativ_and_logistic', 'container_booking_lt', 'tranit_lt', 'Mimar_reception_redispatch', 'manufacturing')
    def _get_delay(self):
        for record in self:
            record.delay = sum([
                record.administrativ_and_logistic,
                record.container_booking_lt,
                record.tranit_lt,
                record.Mimar_reception_redispatch,
                record.manufacturing
            ])
    @api.constrains('administrativ_and_logistic', 'container_booking_lt', 'tranit_lt', 'Mimar_reception_redispatch', 'manufacturing')
    def _check_positive_values(self):
        for record in self:
            if any(field < 0 for field in [record.administrativ_and_logistic, record.container_booking_lt, record.tranit_lt, record.Mimar_reception_redispatch, record.manufacturing]):
                raise UserError('Fields must have positive values.')



class productproductInherit(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None , order=None):
       args = list(args or [])
       if name:
           args += ['|', ('name', operator, name), ('barcode', operator, name)]

           return self._search(args, limit=limit, access_rights_uid=name_get_uid)

       else :
           args += ['|', ('name', operator, name), ('barcode', operator, name)]
           return self._search(args, limit=limit, access_rights_uid=name_get_uid)
