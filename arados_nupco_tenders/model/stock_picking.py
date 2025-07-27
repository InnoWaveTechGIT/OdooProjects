from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class srikLotIngerit(models.Model):
    _inherit = 'stock.picking'

    tender_id = fields.Many2one('tenders' , string='Tender NO' ,compute='get_tender_po')
    is_delivery = fields.Boolean(string='Is Delivery', default=False, compute='_compute_is_delivery')

    @api.depends('origin')
    def _compute_is_delivery(self):
        for record in self:
            if record.origin and record.origin.lower().startswith('p'):
                record.is_delivery = True
            else:
                record.is_delivery = False



    @api.depends('purchase_id')
    def get_tender_po(self):
        for rec in self:
            if rec.origin and rec.origin.startswith('P'):
                purchase = self.env['purchase.order'].search([('name', '=', rec.origin)])
                rec.tender_id = purchase.tender_id.id

            else:
                rec.tender_id = False





