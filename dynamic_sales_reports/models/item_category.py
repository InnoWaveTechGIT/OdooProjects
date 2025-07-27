from collections import defaultdict

from odoo import api, fields, models


class DynamicWizard(models.TransientModel):
    _inherit = "dynamic.wizard"

    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')
    pos_id = fields.Many2many('pos.config', string='Point of Sale')
    payment_id = fields.Many2many('pos.payment.method', string='Payment Method')
    category_id = fields.Many2many('product.category', string='Category')
    partner_id = fields.Many2many('res.partner', string='Customer')
    employee_id = fields.Many2many('res.users', string='User')
    product_id = fields.Many2many('product.product', string='Product')
    company_id = fields.Many2many('res.company', string='Company', default=lambda self: self.env.user.company_id)

    def get_data(self, data=None):
        if self.report_type == '0':
            print("hellllllllllllllll", self.report_type)

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

            if self.payment_id:
                domain.append(('payment_ids.payment_method_id', 'in', self.payment_id.ids))

            orders_pos = self.env['pos.order'].search(domain)

            # Initialize dictionary to store stats by category
            category_stats = defaultdict(lambda: {
                'category_name': '',
                'total_amount': 0.0,
                'refunded_amount': 0.0,
                'total_quantity': 0,
                'total_product_cost': 0.0,
                'total_discount': 0.0,
                'order_count': 0,
                'net_total': 0.0,
                'profit': 0.0,
            })
            print("order", orders_pos)

            for order in orders_pos:
                for line in order.lines:
                    category_id = line.product_id.categ_id
                    category_name = category_id.name
                    for payment in order.payment_ids:
                        payment_id = payment.payment_method_id
                        payment_name = payment_id.name

                    if line.product_id in self.product_id:

                        key = (category_id.id, payment_id.id)

                        # Initialize category data if not already set
                        if not category_stats[key]['category_name']:
                            category_stats[key]['category_name'] = category_name
                            category_stats[key]['payment_method'] = payment_name

                        category_stats[key]['total_amount'] += line.price_subtotal
                        category_stats[key]['total_quantity'] += line.qty
                        category_stats[key]['total_product_cost'] += line.product_id.standard_price * line.qty

                        if line.discount:
                            category_stats[key]['total_discount'] += line.qty * line.price_unit - line.price_subtotal

                        if 'REFUND' in order.name:
                            category_stats[key]['refunded_amount'] += abs(line.price_subtotal)

                        category_stats[key]['order_count'] += 1

            # Calculate net total and profit for each category
            for category_data in category_stats.values():
                net_total = category_data['total_amount'] - category_data['total_discount'] - category_data[
                    'refunded_amount']
                category_data['net_total'] = round(net_total, 2)
                category_data['profit'] = round(category_data['net_total'] - category_data['total_product_cost'], 2)

            # Prepare data for the report
            order_template_filter = [
                {'From': self.date_from},
                {'To': self.date_to},
                {'Payment': ', '.join(self.payment_id.mapped('name')) if self.payment_id else ''},
                {'Category': ', '.join(self.category_id.mapped('name')) if self.category_id else ''},
                {'Partner': ', '.join(self.partner_id.mapped('name')) if self.partner_id else ''},
                {'Employee': ', '.join(self.employee_id.mapped('name')) if self.employee_id else ''},
                {'Product': ', '.join(self.product_id.mapped('name')) if self.product_id else ''},
            ]

            table_header = [
                'Category Name', 'Total Sales', 'Total Returns', 'Discount', 'Net Total',
                'Sales Cost', 'Total Quantity', 'Order Count', 'Profit', 'Net'
            ]

            # Populate the table_body with aggregated data by category
            table_body = []
            for category_data in category_stats.values():
                net_total = category_data['total_amount'] - category_data['total_discount'] - category_data[
                    'refunded_amount']
                table_body.append([
                    category_data['category_name'],
                    round(category_data['total_amount'], 2),
                    round(category_data['refunded_amount'], 2),
                    round(category_data['total_discount'], 2),
                    round(net_total, 2),
                    round(category_data['total_product_cost'], 2),
                    category_data['total_quantity'],
                    category_data['order_count'],
                    category_data['profit'],
                    category_data['net_total']
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
            print("data", data)
        return super(DynamicWizard, self).get_data(data)
