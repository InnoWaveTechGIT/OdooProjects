from collections import defaultdict
from odoo import api, fields, models

class DynamicWizard(models.TransientModel):
    _inherit = "dynamic.wizard"

    def get_data(self, data=None):
        if self.report_type == '2':
            domain = []
            if self.date_from:
                domain.append(('date_order', '>=', self.date_from))
            if self.date_to:
                domain.append(('date_order', '<=', self.date_to))
            if self.pos_id:
                domain.append(('session_id.config_id', 'in', self.pos_id.ids))
            if self.partner_id:
                domain.append(('partner_id', 'in', self.partner_id.ids))
            if self.employee_id:
                domain.append(('user_id', 'in', self.employee_id.ids))
            if self.product_id:
                domain.append(('lines.product_id', 'in', self.product_id.ids))

            orders_pos = self.env['pos.order'].search(domain)

            customer_stats = defaultdict(lambda: {
                'customer_no': '',
                'customer_name': '',
                'customer_phone': '',
                'total_sales': 0.0,
                'total_returns': 0.0,
                'total_discount': 0.0,
                'net_total': 0.0,
                'sales_cost': 0.0,
                'return_cost': 0.0,
                'profit': 0.0,
                # 'delivery_fees': 0.0,
            })

            for order in orders_pos:
                customer_id = order.partner_id
                customer_stats[customer_id.id]['customer_no'] = customer_id.ref or ''
                customer_stats[customer_id.id]['customer_name'] = customer_id.name or ''
                customer_stats[customer_id.id]['customer_phone'] = customer_id.phone or ''

                order_total = sum(line.price_subtotal for line in order.lines)
                refunded_amount = abs(order_total) if 'REFUND' in order.name else 0.0
                discount = sum(line.qty * line.price_unit - line.price_subtotal for line in order.lines if line.discount)
                sales_cost = sum(line.product_id.standard_price * line.qty for line in order.lines)
                # delivery_fees = order.amount_delivery

                customer_stats[customer_id.id]['total_sales'] += order_total if refunded_amount == 0 else 0
                customer_stats[customer_id.id]['total_returns'] += refunded_amount
                customer_stats[customer_id.id]['total_discount'] += discount
                customer_stats[customer_id.id]['net_total'] += order_total - discount - refunded_amount
                customer_stats[customer_id.id]['sales_cost'] += sales_cost
                customer_stats[customer_id.id]['return_cost'] += refunded_amount
                customer_stats[customer_id.id]['profit'] += customer_stats[customer_id.id]['net_total'] - sales_cost
                # customer_stats[customer_id.id]['delivery_fees'] += delivery_fees

            order_template_filter = [
                {'From': self.date_from},
                {'To': self.date_to},
                {'Payment': ', '.join(self.payment_id.mapped('name')) if self.payment_id else ''},
                {'Partner': ', '.join(self.partner_id.mapped('name')) if self.partner_id else ''},
                {'Employee': ', '.join(self.employee_id.mapped('name')) if self.employee_id else ''},
                {'Product': ', '.join(self.product_id.mapped('name')) if self.product_id else ''},
            ]

            table_header = [
                'Customer No', 'Customer Name', 'Customer Phone', 'Total Sales', 'Total Returns',
                'Total Discount', 'Net Total', 'Sales Cost', 'Return Cost', 'Profit', 'Net'
            ]

            table_body = []
            for customer_data in customer_stats.values():
                table_body.append([
                    customer_data['customer_no'],
                    customer_data['customer_name'],
                    customer_data['customer_phone'],
                    round(customer_data['total_sales'], 2),
                    round(customer_data['total_returns'], 2),
                    round(customer_data['total_discount'], 2),
                    round(customer_data['net_total'], 2),
                    round(customer_data['sales_cost'], 2),
                    round(customer_data['return_cost'], 2),
                    round(customer_data['profit'], 2),
                    # round(customer_data['delivery_fees'], 2),
                    round(customer_data['net_total'] - customer_data['return_cost'], 2)
                ])

            title = dict(self._fields['report_type'].selection).get(self.report_type)
            data = {
                'data': {
                    'title': title,
                    'filters': order_template_filter,
                    'table_header': table_header,
                    'table_body': table_body,
                }
            }
        return super(DynamicWizard, self).get_data(data)

