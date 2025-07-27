from odoo import models, fields, api

class CustomWizard(models.TransientModel):
    _name = 'quote.wizard'

    tender_id = fields.Many2one('nupco.orders')
    customer_id = fields.Many2one('res.partner', string='Customer' )
    date_from = fields.Date('Scheduled Date')
    date_to = fields.Date('To')
    ref = fields.Char('Release Reference')
    customer_ids = fields.Many2many('res.partner' ,related='tender_id.customer_ids')


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
        print(123)
        if product:
            if product.product_tmpl_id.seller_ids:
                print(1997)
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
                    'price_unit' : line.price
                })


            so_line_del = self.env['tender.delivery.plan.so'].search([('order_id' ,'=' ,rec.tender_id.id)])
            if so_line_del:
                so_line_del.unlink()
            for i in rec.tender_id.sale_ids:
                so_details = self.env['tender.delivery.plan.so'].create({
                    'sale_id' : i.id,
                    'lot' : i.ref,
                    'lot_value' :round(i.amount_total , 2),
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
