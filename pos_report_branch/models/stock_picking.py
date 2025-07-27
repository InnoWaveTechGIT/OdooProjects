# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api

class ShStockPicking(models.Model):
    _inherit = 'stock.picking'

    sh_is_manager  = fields.Boolean(string="Is manager?", compute='_shcompute_is_manager')
    
    @api.depends('name')
    def _shcompute_is_manager(self):
        for record in self:
            if self.env.user.has_group('stock.group_stock_manager'):
                record.sh_is_manager = True
            else:
                record.sh_is_manager = False