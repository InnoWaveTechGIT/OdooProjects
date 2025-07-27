from odoo import http
from odoo.http import request ,Response
import json
from datetime import datetime


class SaleOrderController(http.Controller):

    @http.route('/api/sale_order', type='http', auth='public', methods=['POST'], csrf=False)
    def create_sale_order(self):

        # check the token
        try:
            header = request.httprequest.headers
            token = header['Authorization'].replace('Bearer ', '')

            if token == '123':
                pass
            else:
                response = json.dumps({ 'data' : [], 'message': 'Unauthorized'})
                return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
                )
        except Exception as e:
            response = json.dumps({ 'data' : [], 'message': 'Please Send Your Token'})
            return Response(
            response, status=403,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        # Step 1: Find the customer by name
        data = json.loads(request.httprequest.data)
        customer_name = data.get('customer_name')
        product_lines = data.get('product_lines')
        partner_id = request.env['res.partner'].sudo().search([('name', '=', customer_name)], limit=1)
        if not partner_id:
            response = json.dumps({ 'data' : [], 'message': 'Customer Not Found'})
            return Response(
            response, status=400,
            headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
            )
        # Step 2: Create the Sale Order
        sale_order = request.env['sale.order'].sudo().create({
            'partner_id': partner_id.id,
            'order_line': [(0, 0, {'product_id': line['product_id'], 'product_uom_qty': line['product_uom_qty']}) for line in product_lines],
        })

        # Step 3: Confirm the Sale Order
        sale_order.sudo().action_confirm()

        # Step 4: Create the Invoice

        advance_payment_obj = request.env['sale.advance.payment.inv']

        # Set the field values
        values = {
            'advance_payment_method': 'delivered',  # Set the desired value for advance_payment_method field
            'sale_order_ids': [(6, 0, [sale_order.id])],  # Set the desired sale order IDs

        }
        advance_payment = advance_payment_obj.sudo().create(values)
        invoice = advance_payment.create_invoices()
        # Step 5: Set the Invoice as Paid
        invoice = sale_order.invoice_ids[0]
        invoice.sudo().action_post() # Post the invoice
        sale_order.invoice_status = 'invoiced'

        regestr_payment = request.env['account.payment.register']
        regestr_payment_to_odoo = regestr_payment.sudo().create({
            'journal_id'  :7,
            'payment_method_line_id':4,
            'amount' : invoice.amount_residual,
            'payment_date' : datetime.now(),
            'communication' : invoice.name,
            'line_ids' : invoice.line_ids.filtered(lambda line: line.debit > 0).ids,


        })
        pay = regestr_payment_to_odoo.action_create_payments()
        payment_id = pay['res_id']
        payment = request.env['account.payment'].sudo().search([('id' , '=' , int(payment_id))])


        # Step 3: Post the payment
        payment.action_validate()
        response = json.dumps({ 'data' : {'sale_order_id': sale_order.id, 'invoice_id': invoice.id}, 'message': 'Done'})
        return Response(
        response, status=200,
        headers=[('Content-Type', 'application/json'), ('Content-Length', 100)]
        )
