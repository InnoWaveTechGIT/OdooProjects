from odoo import api, fields, models, _
from collections import defaultdict
from datetime import datetime


class DailyReportWizard(models.TransientModel):
    _name = 'daily.report.wizard'

    date = fields.Date('Date', required=True)


    def generate_pdf(self):
        domain = []
        company = {}
        # Your existing code to build the domain
        year = self.date.year
        month = self.date.month
        day = self.date.day
        domain = [
                    ('date_order', '>=', datetime(year, month, day, 0, 0, 0)),
                    ('date_order', '<=', datetime(year, month, day, 23, 59, 59)),
                ]

        
        orders_pos = self.env['pos.order'].search(domain)
        # if self.company_id:
        #     company = {
        #         'id': self.company_id.id,
        #         'name': self.company_id.name,
        #         'mobile': self.company_id.mobile
        #     }

        # Group orders by session_id.config_id and calculate total amount, quantity, number of orders, and total product cost for each POS
        pos_stats = defaultdict(lambda: {'pos_id': 0, 'total_amount': 0.0, 'total_quantity': 0, 'order_count': 0, 'total_product_cost': 0.0, 'profit': 0.0, 'orders': []})

        for order in orders_pos:
            pos_id = order.session_id.config_id.id
            pos_id1 = order.session_id.config_id.name

            order_data = {
                'order_id': order.name,
                'customer': order.partner_id.name,
                'products': [],
                'customer_note': order.note,
                'discount': order.amount_total - sum(line.price_subtotal for line in order.lines),
            }

            for line in order.lines:
                product_data = {
                    'name': line.product_id.name,
                    'quantity': line.qty,
                }
                order_data['products'].append(product_data)

                pos_stats[pos_id]['total_quantity'] += line.qty
                pos_stats[pos_id]['total_product_cost'] += line.product_id.standard_price * line.qty

            pos_stats[pos_id]['pos_id'] = pos_id1
            pos_stats[pos_id]['total_amount'] += order.amount_total
            pos_stats[pos_id]['order_count'] += 1

            profit = pos_stats[pos_id]['total_amount'] - pos_stats[pos_id]['total_product_cost']
            pos_stats[pos_id]['profit'] = round(profit, 2)

            pos_stats[pos_id]['orders'].append(order_data)

        total_orders = sum(pos_stats[pos_id]['order_count'] for pos_id in pos_stats)

        data = {
            'form_data': self.read()[0],
            'data': dict(pos_stats),
            'total': total_orders,
        }

        print('data dddddddddddd >>>>>>>>>>> ', data['form_data'])
        print('data dddddddddddd >>>>>>>>>>> ', data['data'])

        # return self.env.ref('all_reports.report_order_filter').report_action(self, data=data)
        return True
