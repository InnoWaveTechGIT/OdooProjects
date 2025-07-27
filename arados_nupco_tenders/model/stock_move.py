from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    tender_id = fields.Many2one('tenders' , string='Tender NO' ,compute='get_tender_po')
    is_delivery = fields.Boolean(string='Tender NO' ,compute='get_tender_po')

    @api.depends('picking_id')
    def get_tender_po(self):
        for rec in self:
            if rec.picking_id:
                if rec.picking_id.tender_id:
                    rec.tender_id = rec.picking_id.tender_id.id

                else:
                    rec.tender_id =False
            else:
                rec.tender_id =False
            if rec.picking_id.is_delivery:
                rec.is_delivery = True
            else:
                rec.is_delivery = False
