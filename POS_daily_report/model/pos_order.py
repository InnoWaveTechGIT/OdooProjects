from odoo import api, fields, models, _
from collections import defaultdict
from datetime import datetime
from odoo.exceptions import UserError


class DailyReportWizard(models.TransientModel):
    _name = 'daily.report.wizard'

    date = fields.Date('Date', required=True)
    pos_id = fields.Many2one('pos.config' ,required=True )


    def generate_pdf(self):
        domain = []
        company = {}
        sessions = []
        cash = []
        prod = []

        invoice_detais = []
        # Your existing code to build the domain
        year = self.date.year
        month = self.date.month
        day = self.date.day
        domain = [
                    ('date_order', '>=', datetime(year, month, day, 0, 0, 0)),
                    ('date_order', '<=', datetime(year, month, day, 23, 59, 59)),
                    ('config_id' , '=' , self.pos_id.id)
                ]
        total_or = 0
        orders_pos = self.env['pos.order'].search(domain)
        for i in orders_pos:
            if i.session_id.id not in sessions:
                sessions.append(i.session_id.read()[0])  # Include only needed fields
                for zstate in i.session_id.statement_line_ids:
                    cash_data = zstate.read()[0]  # Extract specific fields
                    if cash_data['id'] not in [c['id'] for c in cash]:  # Check for existing ID
                        cash.append(cash_data)

        # if self.company_id:
        #     company = {
        #         'id': self.company_id.id,
        #         'name': self.company_id.name,
        #         'mobile': self.company_id.mobile
        #     }

        # Group orders by session_id.config_id and calculate total amount, quantity, number of orders, and total product cost for each POS
        pos_stats = defaultdict(lambda: {'pos_id': 0, 'total_amount': 0.0, 'total_quantity': 0, 'order_count': 0, 'total_product_cost': 0.0, 'profit': 0.0, 'orders': []})

        for order in orders_pos:
            total_cash = 0.0
            total_bank = 0.0
            total_customer = 0.0
            total_or +=1
            pos_id = order.session_id.config_id.id
            pos_id1 = order.session_id.config_id.name
            for oays in order.payment_ids:
                if oays.payment_method_id.name == 'Cash':
                    total_cash +=oays.amount
                if oays.payment_method_id.name == 'Bank':
                    total_bank +=oays.amount
                if oays.payment_method_id.name == 'Customer Account':
                    total_customer +=oays.amount

            invoice_detais.append({
                'name' : order.account_move.name if order.account_move else order.name ,
                'cash' : total_cash ,
                'bank' : total_bank ,
                'customer' : total_customer,
                'total' : total_cash + total_bank
            })
            order_data = {
                'order_id': order.name,
                'customer': order.partner_id.name,
                'products': [],
                'amount_total': order.amount_total,
                'amount_tax': order.amount_tax,
                'user_id': order.user_id.name,

            }

            for line in order.lines:
                product_data = {
                    'name': line.product_id.name,
                    'quantity': line.qty,
                    'discount' : line.discount,
                    'customer_note' : line.customer_note,
                    'subtotal' : line.price_subtotal_incl
                }
                order_data['products'].append(product_data)
                prod.append(product_data)

                pos_stats[pos_id]['total_quantity'] += line.qty
                pos_stats[pos_id]['total_product_cost'] += line.product_id.standard_price * line.qty

            pos_stats[pos_id]['pos_id'] = pos_id1
            pos_stats[pos_id]['total_amount'] += order.amount_total
            pos_stats[pos_id]['order_count'] += 1

            profit = pos_stats[pos_id]['total_amount'] - pos_stats[pos_id]['total_product_cost']
            pos_stats[pos_id]['profit'] = round(profit, 2)

            pos_stats[pos_id]['orders'].append(order_data)

        # total_orders = sum(pos_stats[pos_id]['order_count'] for pos_id in pos_stats)
        total_orders = 0
        # for d in pos_stats:
        #     total_orders +=int(d[pos_id]['order_count'])
        total_invoic = sum(pos_stats[pos_id]['total_amount'] for pos_id in pos_stats)
        total_quantity = sum(pos_id['quantity'] for pos_id in prod)
        inv_det_cash = {
            'sum_cash': sum(detail.get('cash', 0) for detail in invoice_detais),
            'sum_bank': sum(detail.get('bank', 0) for detail in invoice_detais),
            'sum_customer': sum(detail.get('customer', 0) for detail in invoice_detais)
        }
        data = {
            'form_data': self.read()[0],
            'data': dict(pos_stats),
            'total': total_or,
            'total_invoic': total_invoic,
            'inv_det_cash' : inv_det_cash,
            'invoice' : invoice_detais,
            'total_quantity' : total_quantity ,
            'sessions' : sessions,
            'cash' : cash,
            'prod' : prod
        }

        if 'sessions' in data and data['sessions']:
            return self.env.ref('POS_daily_report.report_order_daily_filter12').report_action(docids=self.ids, data=data)
        else:
            raise UserError("There is no data available for sessions.")
