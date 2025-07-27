from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_open_delivery_transfer_wizard(self):
        self.ensure_one()
        return {
            'name': 'Delivery Transfer',
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.transfer.wizard',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('kharasana_po_wizard.view_delivery_transfer_wizard_form').id,
            'context': {
                'default_purchase_order_id': self.id

            },
        }
