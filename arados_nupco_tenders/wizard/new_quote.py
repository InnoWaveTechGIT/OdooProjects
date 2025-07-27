from odoo import models, fields, api

class CustomWizard(models.TransientModel):
    _name = 'quote.wizard'

    tender_id = fields.Many2one('nupco.orders')
    customer_id = fields.Many2one('res.partner', string='Customer' )
    date_from = fields.Date('Scheduled Date')
    date_to = fields.Date('To')
    ref = fields.Char('Release Reference')
    customer_ids = fields.Many2many('res.partner' ,related='tender_id.customer_ids')
    purchase_document_ids = fields.Many2many('nubco.tender')
    purchase_document_id = fields.Many2one('nubco.tender')
    customer2_ids = fields.Many2many('res.partner' ,'res_partner_tender_comodel' ,compute='get_delivery_adress')
    customer2_id = fields.Many2one('res.partner', string='Delivery Address')


    @api.depends('customer_id')
    def get_delivery_adress(self):
        data = []
        if self.customer_id:
            for rec in self.tender_id.nubco_ids:
                if self.customer_id.id == rec.customer_id.id and rec.delivery_address_id :
                    print('rec.delivery_address_id >>>>>>> ' , rec.delivery_address_id)
                    data.append(rec.delivery_address_id.id)
        print('data >>>>>>>> ' , data)
        self.customer2_ids = data


    def calculate_delivery(self , so):
        so_obj = self.env['sale.order'].search([('id' ,'=' ,int(so))])
        delivered = 0
        for line in so_obj.order_line:
            delivered += line.qty_delivered

        return delivered

    def calculate_un_delivery(self , so):
        so_obj = self.env['sale.order'].search([('id' ,'=' ,int(so))])
        delivered = 0
        for line in so_obj.order_line:
            delivered += line.qty_to_deliver

        return delivered




    def get_manufac(self , product):
        if product:
            if product.product_tmpl_id.seller_ids:
                return product.product_tmpl_id.seller_ids[0].partner_id.id
            else:
                return False
        else:
            return False


    def action_Create_quot(self):
        for rec in self:

            order = self.env['sale.order'].create({
                'partner_id' : rec.customer_id.id,
                'nupco_po_number' : rec.tender_id.id,
                'date_from' : rec.date_from,
                'date_to' : rec.date_to,
                'partner_shipping_id' : rec.customer2_id.id,
                'purchase_document_id' : rec.purchase_document_id.id,
                'purchase_document_ids' : rec.purchase_document_ids.ids,
                'ref' : rec.ref,
                'nubco' : True
            })
            rec.tender_id.write({
            'sale_ids': [(4, order.id)]  # 4 indicates to add a record
        })

            for line in rec.tender_id.nubco_ids:
                if line.customer_id.id == rec.customer_id.id:
                    order_line = self.env['sale.order.line'].create({
                    'product_id' : line.product_id.id,
                    'name' : line.product_id.name,
                    'po_number' : rec.tender_id.po_number,
                    'manufacturer_id' : self.get_manufac(line.product_id),
                    'order_id' : order.id,
                    'price_unit' : line.price,
                })


            so_line_del = self.env['tender.delivery.plan.so'].search([('order_id' ,'=' ,rec.tender_id.id)])
            if so_line_del:
                so_line_del.unlink()
            for i in rec.tender_id.sale_ids:
                for line in i.order_line:
                    so_details = self.env['tender.delivery.plan.so'].create({
                        'sale_id' : line.order_id.id,
                        'sale_line_id' : line.id,
                        'product_id' : line.product_id.id,
                        'lot' : line.order_id.ref,
                        'discount' : line.discount,
                        'lot_value' :round(line.price_subtotal , 2),
                        'start_date' :i.date_from,
                        'last_date' :i.date_to,
                        'so_order_date':i.date_order,
                        'delivered_value': self.calculate_delivery(i.id) ,
                        'un_delivered_value' :self.calculate_un_delivery(i.id),
                        'adjust_value' : 0 ,
                        'status' : i.nupco_po_number.tender_id.state1,
                        'tender_no1' : i.tender_order_id,
                        'total_awrd_value' : self.get_total_awd(rec.tender_id,rec.customer_id.id),
                        'order_id' : rec.tender_id.id
                    })


        return {'type': 'ir.actions.act_window_close'}


    def get_total_awd(self ,order ,customer):
        order.get_total_awarded()
        total=0
        for i in order.nubco_total_ids:
            if i.customer_id.id == int(customer):
                total = i.total_award_values

        return total
