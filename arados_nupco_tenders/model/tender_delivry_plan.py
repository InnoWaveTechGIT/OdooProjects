from odoo import api, fields, models, _


class Tender(models.Model):
    _name = 'tender.delivery.plan'

    name = fields.Char(related='tender_number.name')
    tender_number = fields.Many2one('tenders' ,string='Tender Number', ondelete='cascade')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    total_awarded = fields.Float('Total Awarded Value', compute='get_total_awarded')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('lost', 'Lost'),
        ('open', 'Open'),
        ('close', 'Close'),
    ], default='draft')
    customer_id = fields.Many2one('res.partner' , string='Customer')
    company_id = fields.Many2one('res.company')
    delivery_ids= fields.One2many('tender.delivery.plan.line' , 'delivery_id' , string='NUPCO Products')


    @api.depends('delivery_ids')
    def get_total_awarded(self):
        for rec in self:
            total=0.0
            for line in rec.delivery_ids:
                total += (line.total_awarded)

            rec.total_awarded = total
class Tenderlines(models.Model):
    _name = 'tender.delivery.plan.line'

    customer_id = fields.Many2one('res.partner' , string='Customer')
    delivery_id = fields.Many2one('tender.delivery.plan' )
    nubco_order_id = fields.Many2one('nupco.orders' , string='NUPCO Order' , ondelete='cascade')
    total_awarded = fields.Float('Total Awarded Value')
    release_plan = fields.Integer('Release Plan')

    def action_open_order(self):
        for rec in self:
            records = self.env['tender.delivery.plan.so'].search([('order_id' , '=' , rec.nubco_order_id.id)])
            return {
                'type': 'ir.actions.act_window',
                'name': 'Sale Order',
                'res_model': 'tender.delivery.plan.so',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', records.ids)],
                'target': 'current',
            }






class TenderlinesDetails(models.Model):
    _name = 'tender.delivery.plan.so'

    lot = fields.Char()
    lot_value = fields.Char( digits=(12, 2))
    start_date = fields.Date()
    last_date = fields.Date()
    so_order_date = fields.Date()
    delivered_value = fields.Char()
    un_delivered_value = fields.Char()
    adjust_value = fields.Float()
    late_delivery_sub = fields.Char()
    late_delivery_amg = fields.Char('Late Delivery (company)')
    status = fields.Char()
    discount = fields.Float()
    tender_no = fields.Many2one('tenders')
    tender_no1 = fields.Char('Tender NO')
    total_awrd_value=fields.Float()
    order_id = fields.Many2one('nupco.orders', ondelete='cascade')
    sale_id = fields.Many2one('sale.order', ondelete='cascade')
    dd = fields.Boolean(compute='get_deliverd_value')

    @api.depends('sale_id')
    def get_deliverd_value(self):
        for rec in self:
            delivered = 0
            un_delivered = 0
            for order in rec.sale_id.order_line:
                delivered += order.qty_delivered
                un_delivered += order.qty_to_deliver
            rec.delivered_value = delivered
            rec.un_delivered_value = un_delivered
            rec.dd = False
            rec.order_id.get_total_awarded()
            for order in rec.order_id.nubco_total_ids:
                if order.customer_id.id == rec.sale_id.partner_id.id:
                    rec.total_awrd_value = order.total_award_values

