from odoo import api, fields, models, _


class TenderStock(models.Model):
    _name = 'tender.stock'

    tender_id = fields.Many2one('tenders' , string='Tender NO')
    product_id = fields.Many2one('product.product')
    barcode = fields.Char('Barcode')
    uom_id = fields.Many2one('uom.uom' , string='UOM')
    total_qty = fields.Float('Total QTY')
    allocated = fields.Float('Allocated QTY')
    reserved = fields.Float('Reserved QTY')
    free_qty = fields.Float('Free QTY')
    lot_id = fields.Many2one('stock.lot' , string='Lot Id ')
    Production_warranty = fields.Date('Production Date')
    Expiration_warranty = fields.Date('Expiration Date')
    cost_price = fields.Float('Unit Cost Price')
    extended_price = fields.Float('Extended Price')
    test_f = fields.Boolean(compute= 'get_quant_values')
    test_f1 = fields.Boolean(compute= 'get_cost')

    @api.depends('lot_id')
    def get_cost(self):
        for record in self:
            allocat = 0
            total = 0
            if record.lot_id.sale_order_ids:
                for sale in record.lot_id.sale_order_ids:
                    if sale.state == 'draft':
                        for line in sale.order_line:
                            allocat += line.product_uom_qty
            if record.lot_id.purchase_order_ids:
                for rec in record.lot_id.purchase_order_ids.order_line:
                    if rec.product_id.id == record.product_id.id:
                        total = rec.price_unit

            else:
                total= record.product_id.standard_price
            record.cost_price = total
            record.test_f1=False
            record.allocated = allocat

    @api.depends('product_id')
    def get_quant_values(self):
        for rec in self:
            quant = self.env['stock.quant'].search(['&',('lot_id' , '=' , rec.lot_id.id),("location_id.usage", "=", "internal")] , limit=1)
            rec.total_qty = quant.inventory_quantity_auto_apply
            rec.reserved = quant.reserved_quantity
            rec.free_qty = quant.inventory_quantity_auto_apply  - quant.reserved_quantity
            rec.test_f = False

