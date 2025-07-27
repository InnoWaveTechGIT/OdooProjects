from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError
class LoyaltyHistory(models.Model):
    _inherit = "loyalty.history"


    partner_id = fields.Many2one('res.partner' , related='card_id.partner_id')
    partner_id_subid = fields.Char(related='card_id.partner_id.subID')
class LoyaltyCards(models.Model):
    _inherit = "loyalty.card"

    excel_file = fields.Binary('Generated Excel File', readonly=True)
    partner_sub_id = fields.Char(related='partner_id.subID')
    partner_email = fields.Char(related='partner_id.email')
    total_balance = fields.Float(string='Total Balance' , compute='get_total_balance' , store=True)
    available_balance = fields.Float(compute='get_total_balance' , store=True)



    @api.depends('blocked_balance' , 'points_display')
    def get_total_balance(self):
        for rec in self:
            rec.total_balance = float(rec.points) + float(rec.blocked_balance)
    def open_excel_export_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Export Excel Data',
            'res_model': 'excel.export.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_loyality_id': self.id},

        }
