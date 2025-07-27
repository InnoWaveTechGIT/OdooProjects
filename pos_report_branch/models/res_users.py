# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields

# ============================================================
# ================ for user allocation =======================
# ============================================================

class ResUsers(models.Model):
    _inherit = 'res.users'

    sh_allowed_branch_ids = fields.Many2many('pos.report.branch', string="allowed Branches")
    