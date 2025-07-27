from odoo import api, fields, models, _
from collections import Counter, defaultdict


class srikLotIngerit(models.Model):
    _inherit = 'stock.lot'


    Production_warranty = fields.Date('Production Date')
    tender_id = fields.Many2one('tenders' , string='Tender NO')
    stock_tender = fields.Many2one('tender.stock')


    @api.constrains('tender_id' , 'purchase_order_ids')
    def create_tender_stock(self):
        for rec in self:
            if rec.stock_tender:
                rec.stock_tender.unlink()
            quant = self.env['stock.quant'].search(['&',('lot_id' , '=' , rec.id),("location_id.usage", "=", "internal")] , limit=1)
            if rec.tender_id:
                tender = self.env['tender.stock'].create({
                    'tender_id' : rec.tender_id.id,
                    'product_id' : rec.product_id.id,
                    'barcode' : rec.product_id.barcode,
                    'uom_id' : rec.product_id.uom_id.id,
                    'total_qty' : quant.inventory_quantity_auto_apply ,
                    'reserved' : quant.reserved_quantity,
                    'free_qty' : quant.inventory_quantity_auto_apply  - quant.reserved_quantity,
                    'lot_id' : rec.id,
                    'Production_warranty' : rec.Production_warranty,
                    'Expiration_warranty' : rec.expiration_date.date() if  rec.expiration_date else False,
                    'cost_price' : self.get_cost_price(rec),
                })
                rec.stock_tender = tender.id

    def get_cost_price(self , record):
        total = 0
        if record.purchase_order_ids:
            for rec in record.purchase_order_ids.order_line:

                if rec.product_id.id == record.product_id.id:
                    total = rec.price_unit

        else:
            total= record.product_id.standard_price
        return total


class productproductQuantInherit(models.Model):
    _inherit = 'stock.quant'

    tender_no = fields.Many2one('tenders' , related = 'lot_id.tender_id')

class productproductInherit(models.Model):
    _inherit = 'stock.move.line'

    Production_warranty1 = fields.Date('Production Date' ,compute='get_prod_date')
    Production_warranty = fields.Date('Production Date' )
    quant_id = fields.Many2one('stock.quant', "Pick From", store=False , default=False)
    tender_no = fields.Many2one('tenders' , related = 'quant_id.lot_id.tender_id')

    @api.constrains('write_date')
    def get_lot_id(self):
        for rec in self:
            if rec.lot_id:
                rec.move_id.sale_line_id.lot_id = rec.lot_id.id



    @api.depends('quant_id')
    def get_prod_date(self):
        for rec in self:

            if rec.quant_id:
                rec.Production_warranty1 = rec.quant_id.lot_id.Production_warranty
                rec.Production_warranty = rec.quant_id.lot_id.Production_warranty
            else:
                rec.Production_warranty1 = False




    def _create_and_assign_production_lot(self):
        """ Creates and assign new production lots for move lines."""
        lot_vals = []
        # It is possible to have multiple time the same lot to create & assign,
        # so we handle the case with 2 dictionaries.
        key_to_index = {}  # key to index of the lot
        key_to_mls = defaultdict(lambda: self.env['stock.move.line'])  # key to all mls
        for ml in self:
            key = (ml.company_id.id, ml.product_id.id, ml.lot_name)
            key_to_mls[key] |= ml
            if ml.tracking != 'lot' or key not in key_to_index:
                key_to_index[key] = len(lot_vals)
                lot_vals.append(ml._prepare_new_lot_vals())
        lots = self.env['stock.lot'].create(lot_vals)
        for key, mls in key_to_mls.items():
            lot = lots[key_to_index[key]].with_prefetch(lots._ids)   # With prefetch to reconstruct the ones broke by accessing by index
            mls.write({'lot_id': lot.id})

    def _prepare_new_lot_vals(self):
        self.ensure_one()
        vals = super()._prepare_new_lot_vals()
        if self.date_of_manufacturing:
            vals['Production_warranty'] = self.Production_warranty
            vals['tender_id'] = self.move_id.picking_id.tender_id.id

        return vals

