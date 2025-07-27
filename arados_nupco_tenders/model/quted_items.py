
from odoo import models, fields, api
from datetime import datetime, timedelta
class OrderTenderItems(models.Model):
    _name = 'quted.items'

    barcode= fields.Char('Barcode')
    product_id = fields.Many2one('product.product','Product')
    supplier = fields.Char('Supplier')
    tender_no = fields.Char('Tender NO')
    tender_id = fields.Many2one('tenders' , ondelete='cascade')
    qty = fields.Float('QTY')
    uom = fields.Char('UOM')
    unit_price = fields.Float('Unit Price')
    total_value = fields.Float('Total Value')
    won_value = fields.Float('Won Value')
    customer = fields.Many2one('res.partner' , string='Customer')

    order = fields.Many2one('nupco.orders', ondelete='cascade')
    dds = fields.Boolean(compute='get_quantity')


    @api.depends('tender_id')
    def get_quantity(self):
        for rec in self:
            if rec.tender_id:
                print('rec.tender_id.quantity1' , rec.tender_id.quantity1)
                rec.quantity = self.get_quantu(rec.tender_id.id, rec.product_id.id)
                rec.product_id= rec.tender_id.product_id.id
                rec.supplier= rec.tender_id.manufacturer_id.name
                rec.tender_no= rec.tender_id.order_id.tender_no
                rec.qty = rec.tender_id.quantity
                rec.uom= rec.tender_id.uom_id.name
                rec.unit_price= rec.tender_id.price
                rec.total_value= rec.tender_id.quantity * rec.tender_id.price
                rec.won_value= rec.order.quantity


            rec.dds = False


    def get_quantu(self , tender,product):
        qua = 0
        record = self.env['tenders'].search([('id' , '=' ,int(tender))])
        for i in record.nubco_ids:
            print('from get_quantu ' , i.quantity1)
            if i.product_id.id == int(product):
                qua= i.quantity1


        return qua
