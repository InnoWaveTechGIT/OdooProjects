# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _inherit = "stock.move"

    use_manufacturing_date = fields.Boolean(
        related='product_id.use_manufacturing_date', store=True)

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    date_of_manufacturing = fields.Datetime(string='DOM', required=True, store=True,compute='_compute_expiration_date', readonly=False)
    use_manufacturing_date = fields.Boolean(related='product_id.use_manufacturing_date')

    @api.onchange('date_of_manufacturing')
    def _check_date_of_manufacturing(self):
        for record in self:
            if record.date_of_manufacturing and record.date_of_manufacturing > datetime.now():
                raise ValidationError(_("Invalid Date."))

    @api.depends('lot_id.date_of_manufacturing')
    def _compute_production_date(self):
        for move_line in self:
            if not move_line.date_of_manufacturing and move_line.lot_id.date_of_manufacturing:
                move_line.date_of_manufacturing = move_line.lot_id.date_of_manufacturing

    def _prepare_new_lot_vals(self):
        vals = super()._prepare_new_lot_vals()
        if self.date_of_manufacturing:
            vals['date_of_manufacturing'] = self.date_of_manufacturing
        return vals

    @api.onchange('quant_id', 'lot_id')
    def _onchange_lot_id(self):
        if self.quant_id:
            self.date_of_manufacturing = self.quant_id.date_of_manufacturing
        elif self.lot_id:
            self.date_of_manufacturing = self.lot_id.date_of_manufacturing
        else:
            self.date_of_manufacturing = False

