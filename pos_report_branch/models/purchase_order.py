# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api

# ============================================================
# ================ for puchase order reporting ===============
# ============================================================

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    report_branch_id = fields.Many2one(
        string='Branch',
        comodel_name='pos.report.branch',
        ondelete='restrict')
    
    sh_branch_bool=fields.Boolean('Branch ex', compute='compute_branch_id')
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse" , related='picking_type_id.warehouse_id')

    # @api.onchange('picking_type_id')
    # def _onchange_partner_id(self):
    #     if self.picking_type_id:
    #         self.warehouse_id = self.picking_type_id.warehouse_id.id

    def compute_branch_id(self):
        for rec in self:
            if rec.sh_branch_bool==True:
                rec.sh_branch_bool=False
            else: 
                rec.sh_branch_bool=True
            if rec.picking_type_id.sudo().warehouse_id:

                warehouse_id=rec.picking_type_id.sudo().warehouse_id.id
                branch_id=self.env['pos.report.branch'].search([('sh_warehouse_id','in',warehouse_id)])
                if branch_id:
                    rec.report_branch_id=branch_id

                else:
                    rec.report_branch_id=False
            else:
                rec.report_branch_id=False


class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    report_branch_id = fields.Many2one(
        string='Branch',
        comodel_name='pos.report.branch',
        ondelete='restrict')

    def _select(self):
        return super(PurchaseReport, self)._select() + ", po.report_branch_id as report_branch_id"

    def _from(self):
        return super(PurchaseReport, self)._from() + "left join pos_report_branch prb on (prb.id=report_branch_id)"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ",report_branch_id"
