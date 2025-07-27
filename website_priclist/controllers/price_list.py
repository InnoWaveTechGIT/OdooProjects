from odoo import http

class WebsitePriceListController(http.Controller):

    @http.route('/get_products_by_price_list', type='json', auth='public')
    def get_products_by_price_list(self, price_list_id):
        # Code to fetch products by price list ID
        products = self.env['product.product'].search([('pricelist_ids', 'in', price_list_id)])
        product_data = [{'name': product.name, 'price': product.list_price} for product in products]
        return product_data