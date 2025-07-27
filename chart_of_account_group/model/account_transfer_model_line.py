from odoo import api, fields, models, _, Command

class AccountAccount(models.Model):
    _inherit = "account.transfer.model.line"


    @api.depends('analytic_account_ids', 'partner_ids')
    def _compute_percent_is_readonly(self):
        for record in self:
            record.percent_is_readonly = False









