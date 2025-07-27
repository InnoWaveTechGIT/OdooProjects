# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api

class ShStock(models.Model):
    _inherit = 'stock.warehouse'

    sh_allowed_branch_ids = fields.Many2many('pos.report.branch', string="allowed Branches", default=lambda self: self.env.user.sh_allowed_branch_ids.ids)
    

    # @api.model
    # def write(self, vals):
    #     self.env.user.sh_allowed_branch_ids.sh_warehouse_id = self.id
    #     return super().write(vals)
    