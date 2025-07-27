from odoo import models, fields, api

class PurchaseOrderTender(models.Model):
    _inherit = 'purchase.order'


    tender_id = fields.Many2one('tenders' , string='Tender NO')
