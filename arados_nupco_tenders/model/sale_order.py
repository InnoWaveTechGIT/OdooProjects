from odoo import models, fields, api
from odoo.exceptions import UserError
class OrderTender(models.Model):
    _inherit = 'sale.order'

    nupco_po_number = fields.Many2one('nupco.orders' , string ='NUPCO PO Number' , ondelete='cascade')
    tender_order_id = fields.Char( string='Tender NO' , related='nupco_po_number.tender_no')
    date_from = fields.Date('Scheduled Date')
    date_to = fields.Date('To')
    ref = fields.Char('Release Reference')
    nubco = fields.Boolean()
    has_tender = fields.Boolean(' Has tender' , compute='has_tender_calc')
    order_ids = fields.Many2many('nupco.orders' , compute='get_orders',store=True)

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
                # orders_line = self.env['nubco.tender'].search([])
                rec.order_ids = False


    @api.constrains('partner_id' , 'nupco_po_number')
    def partner_constraint(self):
        for rec in self:
            if rec.nupco_po_number:
                if rec.partner_id.id in rec.nupco_po_number.customer_ids.ids:
                    pass
                else:
                    raise UserError("The partner you select should be in NUPCO order Customers ")
    @api.depends('nupco_po_number')
    def has_tender_calc(self):
        for rec in self:
            if rec.tender_order_id:
                rec.has_tender = False
            else:
                rec.has_tender = True


    def action_open_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'res_model': 'nupco.orders',
            'view_mode': 'tree,form',
            'domain': [('id', '=', self.nupco_po_number.id)],
            'res_id': self.nupco_po_number.id,
            'target': 'current',
        }



class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_id = fields.Many2one('sale.order' ,compute='get_sale_id')
    tender_number = fields.Char('Tender Number' , related='sale_id.nupco_po_number.tender_no' )
    release_number = fields.Char('Release Number', related='sale_id.ref')
    total_award_values=fields.Float('Total Awarded Value' ,compute='get_total_award_values')
    del_award_values=fields.Float('Delivered Awarded Value' ,compute='get_delivered')
    curr_release_values=fields.Monetary('Current Release Value' ,compute='get_amount_total')
    remaining_awarded_value =fields.Float('Remaining Awarded Value',compute='get_remaining_awarded_value')



    @api.depends('total_award_values' , 'curr_release_values')
    def get_remaining_awarded_value(self):
        for rec in self:
            print('rec.tender_number >>> ' , rec.tender_number)
            invoices = self.env['account.move'].search([('sale_id' ,'=' ,rec.sale_id.id)])
            print('invoices >>> ' , invoices)
            total = 0
            for record in invoices:
                if record.sale_id.nupco_po_number.tender_no == rec.tender_number:

                    print('record.sale_id.nupco_po_number.tender_no >>>> ' , record.sale_id.nupco_po_number.tender_no)
                    print('rec.tender_number >>>> ' , rec.tender_number)
                    print('record.total_award_values >>>> ' , record.total_award_values)
                    print('record.curr_release_values >>>> ' , record.curr_release_values)
                    print('record.id >>>> ' , record.id)
                    total += record.total_award_values - record.curr_release_values

            rec.remaining_awarded_value = total

    @api.depends('tender_number')
    def get_amount_total(self):
        total = 0
        for rec in self:
            if rec.sale_id:
                if rec.sale_id:
                    total += rec.sale_id.amount_total
            rec.curr_release_values = total
    @api.depends('tender_number')
    def get_delivered(self):
        for rec in self:
            total = 0
            if rec.sale_id:
                if rec.sale_id.order_line:
                    orders =self.env['sale.order'].search([('nupco_po_number.tender_id' , '=' , rec.sale_id.nupco_po_number.tender_id.id)])
                    for order in orders:
                        for line in order.order_line:
                            total += line.qty_delivered



            rec.del_award_values = total


    @api.depends('tender_number')
    def get_total_award_values(self):
        for rec in self:
            total = 0
            if rec.sale_id.nupco_po_number:
                if rec.sale_id.nupco_po_number.nubco_total_ids:
                    for line in rec.sale_id.nupco_po_number.nubco_total_ids:
                        if line.customer_id.id == rec.sale_id.partner_id.id :
                            total += line.total_award_values
                else:
                    rec.sale_id.nupco_po_number.get_total_page_awarded()
                    for line in rec.sale_id.nupco_po_number.nubco_total_ids:
                        if line.customer_id.id == rec.sale_id.partner_id.id :
                            total += line.total_award_values

            rec.total_award_values = total



    @api.depends('invoice_line_ids')
    def get_sale_id(self):
        if self.invoice_line_ids:
            if self.invoice_line_ids[0].sale_line_ids:
                self.sale_id = self.invoice_line_ids[0].sale_line_ids[0].order_id.id
            else:
                self.sale_id = False
        else:
            self.sale_id = False

class SaleOrderLineTender(models.Model):
    _inherit = 'sale.order.line'



    po_number = fields.Char(string='PO Number')
    manufacturer_id = fields.Many2one('res.partner' , string='Manufacturer')
    sd = fields.Char(string='Manufacturer' ,compute='get_manufac')
    # sd = fields.Char( string='Manufacturer')
    catalogue_no = fields.Char(related='product_id.barcode' , string='Catalogue Number')
    production_date = fields.Date('Production Date' ,related='lot_id.Production_warranty')
    expiry_date = fields.Datetime('Expiry Date' , related='lot_id.expiration_date')
    lot_id = fields.Many2one('stock.lot' )
    Item_code = fields.Char('Item Code')
    has_tender = fields.Boolean(' Has tender' , compute='has_tender_calc')

    @api.depends('order_id')
    def has_tender_calc(self):
        for rec in self:
            if rec.order_id.tender_order_id:
                rec.has_tender = False
            else:
                rec.has_tender = True

    @api.constrains('write_date')
    def get_po_number(self):
        for rec in self:
            if rec.order_id and rec.order_id.tender_order_id != rec.po_number:
                rec.po_number = rec.order_id.tender_order_id
                print('rec.po_number >>> ' , rec.po_number)

    @api.depends('product_id')
    def get_manufac(self):
        print(123)
        for rec in self:
            if rec.product_id:
                if rec.product_id.product_tmpl_id.seller_ids:
                    print(1997)
                    rec.sd = rec.product_id.product_tmpl_id.seller_ids[0].partner_id.id
                    print('rec.sd >>>> ' , rec.sd)
                    rec.write({
                        'manufacturer_id'  : rec.product_id.product_tmpl_id.seller_ids[0].partner_id.id
                    })
                else:
                    rec.sd = False
            else:
                rec.sd =False
