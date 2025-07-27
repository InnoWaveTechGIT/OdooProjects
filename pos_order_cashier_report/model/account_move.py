from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def get_invoice_data(self, account_move):
        print("heeeeeeeeeeeeeeeeeeeeeelelellelele")
        move = self.env['account.move'].sudo().search_read(
            [
                ('id', '=', account_move),

            ],
            ['name']
        )
        print("hwhwhhwhwhwwwww",move)

        return move
