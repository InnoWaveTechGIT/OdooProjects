from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class productproductInherit(models.Model):
    _inherit = 'product.template'

    warranty = fields.Boolean('Warranty')
    warranty_date = fields.Integer('Warranty Date')
    recurrent = fields.Boolean('Recurrent')


    @api.constrains('warranty_date')
    def _check_positive_warranty_date(self):
        for record in self:
            if record.warranty_date < 0:
                raise UserError('Warranty Date must be a positive integer.')
    # repeat_every = fields.Integer('Repeat Every')
    # repeat_unit = fields.Selection([
    #     ('day', 'Days'),
    #     ('week', 'Weeks'),
    #     ('month', 'Months'),
    #     ('year', 'Years'),
    # ], default='week')
    # repeat_type = fields.Selection([
    #     ('forever', 'Forever'),
    #     ('until', 'Until'),
    # ], default="forever", string="Until")
    # repeat_until = fields.Date(string="End Date")

