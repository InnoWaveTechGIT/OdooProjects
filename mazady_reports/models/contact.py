from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"


    def open_excel_export_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Export Excel Data',
            'res_model': 'excel.export.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_partner_id': self.id},

        }
