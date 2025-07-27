

from odoo import models, fields, api
from odoo.exceptions import UserError


class CustomSupplierWizard(models.TransientModel):
    _name = 'filter.supplier.wizard'

    customer_id = fields.Many2one('res.partner' , string='Supplier')


    def get_supplier_record(self):
        records = self.env['tender.stock'].search([])
        ids=[]
        for rec in records:
            product_id = rec.product_id.id
            if product_id:
                product = self.env['product.product'].search([('id' , '=' , product_id)])
                if product.product_tmpl_id.seller_ids:
                    if product.product_tmpl_id.seller_ids[0].partner_id.id == self.customer_id.id:
                        ids.append(rec.id)
        if ids:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Stock',
                'res_model': 'tender.stock',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', ids)],
                'target': 'current',
            }
        else:
            raise UserError("No records for this Supplier.")


class CustombarcodeWizard(models.TransientModel):
    _name = 'filter.barcode.wizard'

    barcode = fields.Char(string='Barcode')


    def get_barcode_record(self):
        records = self.env['tender.stock'].search([])
        ids=[]
        for rec in records:
            if rec.barcode == self.barcode:
                ids.append(rec.id)
        if ids:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Stock',
                'res_model': 'tender.stock',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', ids)],
                'target': 'current',
            }
        else:
            raise UserError("No records for this Barcode.")


class CustombarcodeWizard(models.TransientModel):
    _name = 'filter.tender.wizard'

    tender_id = fields.Many2one('tenders' , string='Tender NO')


    def get_tender_record(self):
        records = self.env['tender.stock'].search([])
        ids=[]
        for rec in records:
            if rec.tender_id.id == self.tender_id.id:
                ids.append(rec.id)
        if ids:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Stock',
                'res_model': 'tender.stock',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', ids)],
                'target': 'current',
            }
        else:
            raise UserError("No records for this Tender.")
