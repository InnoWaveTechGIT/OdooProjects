from odoo import models, fields, api
from odoo.fields import Command
class AccountMove(models.Model):
    _inherit = 'account.move'

    nupco_order_id = fields.Many2one('nupco.orders' , string='NUPCO Order' ,related='sale_id.nupco_po_number')
    tender_no = fields.Char('Tender', related='nupco_order_id.tender_no')
    product_ids = fields.Many2many('product.product' , string='Products' , compute='get_products_from_tender')
    hide_add_sale = fields.Boolean()
    order_ids = fields.Many2many('nupco.orders' , compute='get_orders',store=True)
    len_order_ids = fields.Integer(compute='get_orders')
    date_from = fields.Date('Scheduled Date' , related='sale_id.date_from')
    date_to = fields.Date('To' ,related='sale_id.date_to')



    @api.ondelete(at_uninstall=False)
    def _prevent_automatic_line_deletion(self):
        if not self.env.context.get('dynamic_unlink'):
            for line in self:
                if line.display_type == 'tax' and line.move_id.line_ids.tax_ids:
                    pass
                elif line.display_type == 'payment_term':
                    pass

    @api.onchange('nupco_order_id')
    def _onchange_some_trigger_field(self):
        """
        This method is called when 'some_trigger_field' changes.
        It calculates and stores temporary lines without saving them.
        """
        new_lines = []
        for rec in self:

            rec.line_ids = [(6, 0, [])]  # Clear existing temporary lines

            # Logic to determine the lines to add
            for item in rec.nupco_order_id.nubco_ids:
                print('item.product_id >>>>>>> ' , item.product_id)
                new_lines.append((0, 0, {'product_id': item.product_id.id,
                    'price_unit' : 0.0}))  # Create new line dictionaries

            rec.invoice_line_ids = new_lines

    @api.depends('partner_id')
    def get_orders(self):
        for rec in self:
            records = []
            rec.order_ids = [(5, 0, 0)]
            if rec.partner_id:
                orders_line = self.env['nubco.tender'].search([('customer_id' , '=' , rec.partner_id.id)])
                for i in orders_line:
                    if i.order_id.id not in records:
                        records.append(i.order_id.id)

                rec.order_ids=[(6,0,records)]

            else:
                rec.order_ids = False

            rec.len_order_ids = len(rec.order_ids)

    def add_sale_id(self):
        print('self.order_ids >>>>>>>> ' , self.order_ids )
        sale_ids = self.env['sale.order'].search(['&' , ('partner_id' , '=' , self.partner_id.id) , ('nupco_po_number' , '=' , self.nupco_order_id.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Sales Order',
            'res_model': 'add.sale.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_account_id': self.id , 'default_sale_ids': sale_ids.ids},
        }


    def get_products_from_tender(self):
        for rec in self:
            products = []
            if rec.nupco_order_id:
                for line in rec.nupco_order_id.nubco_ids:
                    products.append(line.product_id.id)
            else:
                products = self.env['product.product'].search([])
                products= products.ids
            rec.product_ids = products
    @api.model
    def create(self, vals_list):
        moves = super().create(vals_list)
        for move in moves:
            if move.nupco_order_id:
                move._set_next_sequence()
        return moves


class AccountMove(models.Model):
    _inherit = 'account.move.line'

    product_ids = fields.Many2many('product.product' , string='Products' , compute='get_products_from_tender')
    delivered = fields.Float(compute='get_delivered_value' , store=True)
    delivered_test = fields.Float(compute='get_delivered_value')


    po_number = fields.Char(string='PO Number')
    manufacturer_id = fields.Many2one('res.partner' , string='Manufacturer')
    sd = fields.Char(string='Manufacturer' ,compute='get_manufac')
    # sd = fields.Char( string='Manufacturer')
    catalogue_no = fields.Char(related='product_id.barcode' , string='Catalogue Number')
    production_date = fields.Date('Production Date' ,related='lot_id.Production_warranty')
    expiry_date = fields.Datetime('Expiry Date' , related='lot_id.expiration_date')
    lot_id = fields.Many2one('stock.lot' , related='sale_id.lot_id')
    Item_code = fields.Char('Item Code')
    has_tender = fields.Boolean(' Has tender' , compute='has_tender_calc')
    sale_id = fields.Many2one('sale.order.line'  , compute='get_sale_order')


    @api.depends('sale_line_ids')
    def get_sale_order(self):
        for rec in self:
            if rec.sale_line_ids:
                if rec.sale_line_ids[0]:
                    rec.sale_id = rec.sale_line_ids[0].id
                else:
                    rec.sale_id = False
            else:
                rec.sale_id = False

    @api.depends('sale_line_ids')
    def has_tender_calc(self):
        for rec in self:
            if rec.sale_line_ids:
                if rec.sale_line_ids[0].order_id.tender_order_id:
                    rec.has_tender = False
                else:
                    rec.has_tender = True
            else:
                rec.has_tender = True

    @api.constrains('write_date')
    def get_po_number(self):
        for rec in self:
            if rec.sale_line_ids:
                if rec.sale_line_ids[0].order_id and rec.sale_line_ids[0].order_id.tender_order_id != rec.po_number:
                    rec.po_number = rec.sale_line_ids[0].order_id.tender_order_id

    @api.depends('product_id')
    def get_manufac(self):
        for rec in self:
            if rec.product_id:
                if rec.product_id.product_tmpl_id.seller_ids:
                    rec.sd = rec.product_id.product_tmpl_id.seller_ids[0].partner_id.id
                    rec.write({
                        'manufacturer_id'  : rec.product_id.product_tmpl_id.seller_ids[0].partner_id.id
                    })
                else:
                    rec.sd = False
            else:
                rec.sd =False

    @api.depends('sale_line_ids')
    def get_delivered_value(self):
        for rec in self:
            if rec.sale_line_ids:
                rec.delivered = rec.sale_line_ids[0].qty_delivered

            else:
                rec.delivered = 0

            rec.delivered_test = 0
    @api.depends('move_id')
    def get_products_from_tender(self):
        for rec in self:
            products = []
            if rec.move_id.nupco_order_id:
                for line in rec.move_id.nupco_order_id.nubco_ids:
                    products.append(line.product_id.id)

            else:
                products = self.env['product.product'].search([])
                products= products.ids
            rec.product_ids = products
