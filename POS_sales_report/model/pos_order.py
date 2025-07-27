from odoo import api, fields, models, _
from collections import defaultdict
from datetime import datetime


class DailyReportWizard(models.TransientModel):
    _inherit = 'pos.details.wizard'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

    def generate_report(self):
        
        year = self.start_date.year
        month = self.start_date.month
        day = self.start_date.day
        year1 = self.end_date.year
        month1 = self.end_date.month
        day1 = self.end_date.day

        
        domain = [
                    ('date_order', '>=',datetime(year, month, day, 0, 0, 0)),
                    ('date_order', '<=', datetime(year1, month1, day1, 23, 59, 59)),
                ]

        
        orders_pos = self.env['pos.order'].search(domain)
        print('orders_pos  >>>> ' , orders_pos)

        pos_stats = defaultdict(lambda: {'pos_id': 0, 'total_amount': 0.0, 'total_quantity': 0})
        invoice_stats = defaultdict(lambda: {'name': 0, 'total_amount': 0.0, 'total_quantity': 0 ,'cash' : 0.0 , 'bank' : 0.0 , 'customer' :0.0 ,'details' : []})
        for invoice in orders_pos:
            total_cash = 0.0
            total_bank = 0.0
            total_customer = 0.0
            total_amount = 0.0
            for payment in invoice.payment_ids:
                if payment.payment_method_id.name == 'Cash':
                    total_cash +=payment.amount
                if payment.payment_method_id.name == 'Bank':
                    total_bank +=payment.amount
                if payment.payment_method_id.name == 'Customer Account':
                    total_customer +=payment.amount
                total_amount = invoice.amount_total
            print(invoice)
            det1=[]
            for det in invoice.lines:
                det1.append({
                    'name' : det.product_id.name,
                    'qty' : det.qty,
                    'sub_total' : det.price_subtotal_incl
                })
            inv_id = invoice.account_move.id
            invoice_stats[inv_id]['name'] = invoice.account_move.name if invoice.account_move else invoice.name
            invoice_stats[inv_id]['cash'] = total_cash
            invoice_stats[inv_id]['bank'] = total_bank
            invoice_stats[inv_id]['customer'] = total_customer
            invoice_stats[inv_id]['total_amount'] = total_amount
            invoice_stats[inv_id]['details'] = det1
            
        for order in orders_pos:
            pos_id = order.session_id.config_id.id
            pos_id1 = order.session_id.config_id.name

            for line in order.lines:
                product_data = {
                    'name': line.product_id.name,
                    'quantity': line.qty,
                }

                pos_stats[pos_id]['total_quantity'] += line.qty

            pos_stats[pos_id]['pos_id'] = pos_id1
            pos_stats[pos_id]['total_amount'] += order.amount_total

            profit = pos_stats[pos_id]['total_amount']
            pos_stats[pos_id]['total_amount'] = round(profit, 2)
        orders = []
        invoices =[]
        for data in pos_stats.values() :
            # print('ddddddddddddd',data['pos_id'])
            orders.append(
                {
                    'pos_id' : data['pos_id'],
                    'total_amount' : data['total_amount'],
                    'total_quantity' : data['total_quantity'],
                }
            )
        for data in invoice_stats.values() :
            # print('ddddddddddddd',data['pos_id'])
            invoices.append(
                {
                    'name' : data['name'],
                    'total_amount' : data['total_amount'],
                    'cash' : data['cash'],
                    'bank' : data['bank'],
                    'customer' : data['customer'],
                    'details' : data['details']
                                    }
            )

            print('invoices >>>>>>>>> ' , invoices)
            
        

        data = {'date_start': self.start_date, 'date_stop': self.end_date,'pos_report' : orders , 'invoices' : invoices, 'config_ids': self.pos_config_ids.ids}
        return self.env.ref('point_of_sale.sale_details_report').report_action([], data=data)
