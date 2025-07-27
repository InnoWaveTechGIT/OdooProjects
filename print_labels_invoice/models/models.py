# -*- coding: utf-8 -*-

# from odoo import model, fields, api


# class print_labels_invoice(model.Model):
#     _name = 'print_labels_invoice.print_labels_invoice'
#     _description = 'print_labels_invoice.print_labels_invoice'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

