from odoo import api, fields, models, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    # @api.depends('sequence_number', 'session_id')
    # def _compute_tracking_number(self):
    #     for record in self:
    #         print("i am heeeeeeeeeeeeeeeeeeeeere")
    #         base_tracking_number = (record.session_id.id % 10) * 100 + record.sequence_number % 100
    #         record.tracking_number = str(base_tracking_number + 1000).zfill(4)

    @api.model
    def get_order_data(self, order_id):
        print("heeeeeeeeeeeeeeeeeeeeeelelellelele")
        order = self.env['pos.order'].sudo().search_read(
            [
                ('id', '=', order_id),

            ],
            ['name']
        )
        print("hwhwhhwhwhwwwww", order)

        return order
    @api.model
    def get_order_data_by_number(self, trackingnumber):
        print("heeeeeeeeeeeeeeeeeeeeeelelellelele")
        order = self.env['pos.order'].sudo().search_read(
            [
                ('pos_reference', '=', trackingnumber),

            ],
            ['name']
        )
        print("hwhwhhwhwhwwwww", order)

        return order

