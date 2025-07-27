# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockLot(models.Model):
    _inherit = 'stock.lot'

    date_of_manufacturing = fields.Datetime(string='Manufacturing Date', required=True)
    use_manufacturing_date = fields.Boolean(string="Date of Manufacturing", related='product_id.use_manufacturing_date', store=True)

    @api.onchange('date_of_manufacturing')
    def _check_date_of_manufacturing(self):
        for record in self:
            if record.date_of_manufacturing and record.date_of_manufacturing > datetime.now():
                raise ValidationError(_("Invalid Date."))
