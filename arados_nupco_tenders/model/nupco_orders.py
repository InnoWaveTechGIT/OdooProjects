import math

from odoo import models, fields, api
from datetime import datetime, timedelta
class OrderTender(models.Model):
    _name = 'nupco.orders'
    _rec_name = 'po_number'

    name = fields.Char(string='Tender Name')
    customer_id = fields.Many2one('res.partner' , string='Customer')
    tender_no = fields.Char('Tender Number')
    responsible =fields.Many2one('res.users')
    date_from = fields.Date('From')
    date_to = fields.Date('To')
    validity = fields.Integer('Validity' , compute='_compute_validity')
    tags_ids = fields.Many2many('tenders.tags' ,'order_tender_tag', string='Tags')
    company_id = fields.Many2one('res.company')
    state = fields.Selection([
        ('Draft' , 'Draft'),
        ('In Progress' , 'In Progress'),
        ('Lost' ,'Lost'),
        ('Open' ,'Open'),
        ('Close' ,'Close'),
    ])
    po_number = fields.Char(string='PO Number')
    nubco_ids= fields.One2many('nubco.tender' , 'order_id' , string='NUPCO Products')
    nubco_total_ids= fields.One2many('nubco.total.tender' , 'order_id' , string='NUPCO Products')
    total_award_values=fields.Float('Total Awarded Value' , compute='get_total_awarded')
    customer_ids = fields.Many2many('res.partner' , compute='get_customers')
    sale_ids = fields.Many2many('sale.order' , compute = 'get_sales_records')
    len_order_id = fields.Integer( compute="_1235888")
    tender_id = fields.Many2one('tenders' , ondelete='cascade')

    @api.depends('tender_id')
    def get_sales_records(self):
        for record in self:
            # Search sale orders related to the current tender
            sale_orders = self.env['sale.order'].search([('nupco_po_number', '=', record.id)])
            # Assign the found sale orders to the sale_ids field
            record.sale_ids = sale_orders

    def copy(self, default=None):
        if default is None:
            default = {}
        # Set the state to 'draft' when duplicating
        default['state'] = 'Draft'
        default['sale_ids'] = False
        return super(OrderTender, self).copy(default=default)

    def action_open_tender(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tenders',
            'res_model': 'tenders',
            'view_mode': 'tree,form',
            'domain': [('id', '=', self.tender_id.id)],
            'target': 'current',
        }

    def action_open_sale_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.sale_ids.ids)],
            'target': 'current',
        }
    @api.depends('write_date')
    def _1235888(self):
        parent_id = 0
        for lead in self:
            print('self >>>>>>>>  ' , self)
            print('self.lead >>>>>>>>  ' , lead)
            lead.get_total_page_awarded()
            del_plane = self.env['tender.delivery.plan'].search([('tender_number' ,'=' ,lead.tender_id.id)])
            delivery_plan = self.env['tender.delivery.plan.line'].search([('nubco_order_id' , '=' ,lead.id)])
            if delivery_plan:
                # parent_id = delivery_plan[0].delivery_id
                # parent_id.unlink()
                delivery_plan.unlink()

            print(del_plane)
            if lead.tender_id.state1 in ['open' , 'close'] and len(del_plane) == 0:
                    x=self.env['tender.delivery.plan'].create({
                        'tender_number' : lead.tender_id.id,
                        'total_awarded' : lead.total_award_values,
                        'start_date' : lead.tender_id.date_from,
                        'end_date' : lead.tender_id.date_to,
                        'status' : lead.tender_id.state1,
                        'company_id' : lead.tender_id.company_id.id
                    })
                    print('tender_delivery_plan >> ')
                    parent_id = x.id
                    print('Parent_ sdf >>> ' , parent_id)
                    for line in lead.nubco_total_ids:

                        # parent = self.env['tender.delivery.plan'].search([('id' , '=' , parent_id)])
                        # parent.unlink()
                        print('line.customer_id   , ' , line.customer_id.name)
                        print('line.customer_id   , ' , line)
                        print('lead.total_award_values   , ' , line.total_award_values)
                        self.env['tender.delivery.plan.line'].create({
                            'delivery_id' : int(parent_id),
                            'customer_id' : line.customer_id.id,
                            'nubco_order_id' : lead.id,
                            'total_awarded' : line.total_award_values
                        })

            elif lead.tender_id.state1 in ['open' , 'close']:
                for line in lead.nubco_total_ids:
                        self.env['tender.delivery.plan.line'].create({
                            'delivery_id' : int(del_plane[0].id),
                            'customer_id' : line.customer_id.id,
                            'nubco_order_id' : lead.id,
                            'total_awarded' : line.total_award_values
                        })

            lead.len_order_id =len(self.sale_ids)



    @api.depends('date_from', 'date_to')
    def _compute_validity(self):
        for record in self:
            if record.date_from and record.date_to:
                # Convert date objects to strings
                date_from_str = record.date_from.strftime('%Y-%m-%d')
                date_to_str = record.date_to.strftime('%Y-%m-%d')

                # Calculate the number of days between date_from and date_to
                delta = (datetime.strptime(date_to_str, "%Y-%m-%d") - datetime.strptime(date_from_str, "%Y-%m-%d")).days

                # Calculate the number of years
                years = delta / 365

                # Adjust validity based on the number of years
                if years < 1:  # If less than 1 year, set as 1
                    record.validity = 1
                else:
                    record.validity = math.ceil(years)  # Use the integer part of years
            else:
                record.validity = 1
    def new_quotaion(self):
        return {
            'name': 'New Quotation',
            'type': 'ir.actions.act_window',
            'res_model': 'quote.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('arados_nupco_tenders.view_wizard_quote_wizard_form').id,
            'target': 'new',
            'context': {'default_tender_id': self.id},
        }
    @api.depends('nubco_ids')
    def get_total_awarded(self):
        for rec in self:
            total=0.0
            for line in rec.nubco_ids:
                total += (line.quantity * line.price)

            rec.total_award_values = total


    @api.depends('nubco_ids')
    def get_customers(self):
        for rec in self:
            rec.customer_ids = rec.nubco_ids.mapped('customer_id').ids

    def get_total_page_awarded(self):
        for rec in self:
            rec.nubco_total_ids.unlink()

            customer_ids = rec.nubco_ids.mapped('customer_id')
            # print(customer_ids)
            for customer in customer_ids:
                total=0.0
                for line in rec.nubco_ids:
                    if line.customer_id.id == customer.id:
                        total +=(line.quantity * line.price)

                self.env['nubco.total.tender'].create({
                    'order_id' : rec.id ,
                    'customer_id' : customer.id,
                    'total_award_values' : total
                })









class NubcoTotalTender(models.Model):
    _name = 'nubco.total.tender'


    order_id= fields.Many2one('nupco.orders')
    customer_id = fields.Many2one('res.partner' , string='Customer')
    total_award_values=fields.Float('Total Awarded Value' ,readonly='1')
