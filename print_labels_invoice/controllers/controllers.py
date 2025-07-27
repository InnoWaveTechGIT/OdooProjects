# -*- coding: utf-8 -*-
# from odoo import http


# class PrintLabelsInvoice(http.Controller):
#     @http.route('/print_labels_invoice/print_labels_invoice', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/print_labels_invoice/print_labels_invoice/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('print_labels_invoice.listing', {
#             'root': '/print_labels_invoice/print_labels_invoice',
#             'objects': http.request.env['print_labels_invoice.print_labels_invoice'].search([]),
#         })

#     @http.route('/print_labels_invoice/print_labels_invoice/objects/<model("print_labels_invoice.print_labels_invoice"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('print_labels_invoice.object', {
#             'object': obj
#         })

