from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    all_order_products = fields.Many2many(
        'product.product',
        string="All Products in Order",
        compute='_compute_all_order_products',
        store=True,
        help="All products included in this sale order"
    )

    @api.depends('order_line')
    def _compute_all_order_products(self):
        for order in self:
            # Get all distinct product_ids from order lines
            products = order.order_line.mapped('product_id')
            order.all_order_products = [(6, 0, products.ids)]

    def create_products(self):
        # for i in range(1, 1000):
        #     self.env['product.template'].sudo().create({
        #         'name': f'Test Product {i}{i}',
        #         'list_price': 10.0,
        #     })
        #
        #
        # print("✅ Created 50,000 products")

        products = self.env['product.product'].sudo().search([('company_id' ,'=' ,False)], limit=50000)

        if not products:
            print("❌ No products found")
            return

        product_list = products.ids
        sale_orders = []
        partner_id = 92   # Or use any valid partner

        for i in range(2):  # Create 5,000 sale orders
            lines = []
            for j in range(1000):  # 10 lines per order
                index = (i * 10 + j) % len(product_list)
                lines.append((0, 0, {
                    'product_id': product_list[index],
                    'product_uom_qty': 1,
                    'company_id' : 1
                }))

            sale_orders.append({
                'partner_id': partner_id,
                'order_line': lines,
            })
        self.env['sale.order'].sudo().create(sale_orders)
        print("✅ Created 5,000 sale orders (50k lines)")
