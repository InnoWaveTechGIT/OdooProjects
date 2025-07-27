
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PosReportBranch(models.Model):
    _name = 'pos.report.branch'
    _description = 'Pos Report Branch'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string='Name',
        required=True,
        default=lambda self: _('New'),
        copy=False
    )

    pos_ids = fields.One2many(
        string='POS Configs',
        comodel_name='pos.config',
        inverse_name='report_branch_id',
    )


    # ============ For purchase order report ===================
    
    sh_warehouse_id=fields.Many2many('stock.warehouse', required=True)

    sh_user_ids=fields.Many2many('res.users',string='Allowed Users')

    # @api.model
    # def create(self, vals):
    #     res = super().create(vals)
    #     res.sh_warehouse_id.sh_allowed_branch_ids = [(4, res.id)]
    #     return res

    # @api.onchange('sh_warehouse_id')
    # def onchange_field(self):
    #     self.sh_warehouse_id.sh_allowed_branch_ids = [(4, self.id)]
    

    def write(self, vals):
        if 'sh_user_ids' in vals or "sh_warehouse_id" in vals:
            self.env['ir.model.access'].call_cache_clearing_methods()
            self.env['ir.rule'].clear_caches()
            # self.env['res.users'].has_group.clear_cache(self.env['res.users'])
        # if 'sh_warehouse_id' in vals:
            # self.sh_warehouse_id.sh_allowed_branch_ids = [(4, self.id)]
        user = super(PosReportBranch, self).write(vals)
        return user

class PosConfig(models.Model):
    _inherit = 'pos.config'

    report_branch_id = fields.Many2one(
        string='Branch',
        comodel_name='pos.report.branch',
        ondelete='restrict',
    )

class ReportPosOrder(models.Model):
    _inherit = 'report.pos.order'

    report_branch_id = fields.Many2one(
        string='Branch',
        comodel_name='pos.report.branch',
        readonly=True                
    )
    
    def _select(self):
        return super(ReportPosOrder, self)._select() + ''',
pc.report_branch_id as report_branch_id'''

    def _group_by(self):
        return super(ReportPosOrder, self)._group_by() + ',pc.report_branch_id'
        
    def _from(self):
        return super(ReportPosOrder, self)._from() + '''
LEFT JOIN pos_config pc ON (ps.config_id=pc.id)'''
