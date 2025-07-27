from odoo import api, fields, models, _, Command

class AccountAccount(models.Model):
    _inherit = "account.account"



    group_maz = fields.Char(string='test ' , compute='get_group', store=True)


    @api.depends('group_id')
    def get_group(self):
        for rec in self:
            if rec.group_id:
                rec.group_maz = rec.group_id.name
            else:
                rec.group_maz = ""
