# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    date_of_manufacturing = fields.Datetime(related='lot_id.date_of_manufacturing', store=True)
    use_manufacturing_date = fields.Boolean(string="Date of Manufacturing", related='product_id.use_manufacturing_date', store=True)
