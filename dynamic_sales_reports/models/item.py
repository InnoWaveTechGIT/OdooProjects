from collections import defaultdict
from odoo import api, fields, models

class DynamicWizard(models.TransientModel):
    _inherit = "dynamic.wizard"


    def get_data(self, data=None):
        if self.report_type == '1':
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

            # Initialize dictionary to store stats by product
            product_stats = defaultdict(lambda: {
                'item_code': '',
                'item_description': '',
                'unit': '',
                'total_sales': 0.0,
                'total_returns': 0.0,
                'total_discount': 0.0,
                'net_total': 0.0,
                'sales_cost': 0.0,
                'return_cost': 0.0,
                'profit': 0.0,
                'net': 0.0,
                'quantity': 0,
                'return_quantity': 0,
                'net_quantity': 0,
            })

            for order in orders_pos:
                for line in order.lines:
                    product_id = line.product_id
                    product_name = product_id.name
                    unit = product_id.uom_id.name  # Assuming the product has a unit of measure
                    item_code = product_id.default_code or ''

                    # Initialize key by product ID and populate product-specific fields
                    key = product_id.id

                    if not product_stats[key]['item_code']:
                        product_stats[key]['item_code'] = item_code
                        product_stats[key]['item_description'] = product_name
                        product_stats[key]['unit'] = unit

                    # Accumulate sales and return data
                    product_stats[key]['total_sales'] += line.price_subtotal
                    product_stats[key]['quantity'] += line.qty
                    product_stats[key]['sales_cost'] += line.product_id.standard_price * line.qty

                    if line.discount:
                        product_stats[key]['total_discount'] += line.qty * line.price_unit - line.price_subtotal

                    if 'REFUND' in order.name:
                        product_stats[key]['total_returns'] += abs(line.price_subtotal)
                        product_stats[key]['return_quantity'] += abs(line.qty)
                        product_stats[key]['return_cost'] += abs(line.product_id.standard_price * line.qty)

                    # Compute net quantity as the difference between quantity sold and return quantity
                    product_stats[key]['net_quantity'] = product_stats[key]['quantity'] - product_stats[key]['return_quantity']

            # Calculate net total, profit, and net for each product
            for product_data in product_stats.values():
                net_total = product_data['total_sales'] - product_data['total_discount'] - product_data['total_returns']
                product_data['net_total'] = round(net_total, 2)
                product_data['profit'] = round(net_total - product_data['sales_cost'], 2)
                product_data['net'] = round(product_data['profit'], 2)

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

            # Define updated table header with new fields
            table_header = [
                'Item Code', 'Item Description', 'Unit', 'Qty', 'Return Qty', 'Net Qty',
                'Total Sales', 'Total Returns', 'Total Discount', 'Net Total',
                'Sales Cost', 'Return Cost', 'Profit', 'Net'
            ]

            # Populate table body with the product data
            table_body = []
            for product_data in product_stats.values():
                table_body.append([
                    product_data['item_code'],
                    product_data['item_description'],
                    product_data['unit'],
                    product_data['quantity'],
                    product_data['return_quantity'],
                    product_data['net_quantity'],
                    round(product_data['total_sales'], 2),
                    round(product_data['total_returns'], 2),
                    round(product_data['total_discount'], 2),
                    product_data['net_total'],
                    round(product_data['sales_cost'], 2),
                    round(product_data['return_cost'], 2),
                    product_data['profit'],
                    product_data['net']
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

