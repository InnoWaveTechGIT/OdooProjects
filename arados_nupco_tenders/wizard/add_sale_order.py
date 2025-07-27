from odoo import models, fields, api
from odoo.exceptions import UserError

class ExcelImportWizard(models.TransientModel):
    _name = 'add.sale.wizard'
    _description = 'Excel Import Wizard'

    account_id = fields.Many2one('account.move', string='Account')
    action = fields.Selection([('1', 'New'), ('2', 'Link to exist')], string='Action' , default='1')
    date_from = fields.Date('Scheduled Date')
    date_to = fields.Date('To')
    ref = fields.Char('Release Reference')
    sale_id = fields.Many2one('sale.order' , string='Sale Order')

    sale_ids = fields.Many2many('sale.order')


    def link_with_saleorder(self):
        for rec in self:
            rec.account_id.hide_add_sale = True
            if rec.action == '1':
                sale_order = self.env['sale.order'].create({
                    'partner_id' : rec.account_id.partner_id.id ,
                    'date_from' : rec.date_from,
                    'date_to' : rec.date_to,
                    'ref' : rec.ref,

                })
                sale_order.write({
                    'invoice_status' : 'invoiced'
                })
                for line in rec.account_id.line_ids:
                    if line.product_id.name:
                        sale_line = self.env['sale.order.line'].create({
                            'product_id' : line.product_id.id ,
                            'name' : line.product_id.name ,
                            'product_uom_qty' : line.quantity,
                            'price_unit' : line.price_unit,
                            'tax_id' : line.tax_ids,
                            'discount' : line.discount,
                            'order_id' : sale_order.id
                    })

                        line.write({
                                        'sale_line_ids': [(4, sale_line.id)]
                                    })
            else:
                rec.sale_id.order_line.unlink()
                for line in rec.account_id.line_ids:

                    if line.product_id:
                        sale_line = self.env['sale.order.line'].create({
                            'order_id' : rec.sale_id.id,
                            'product_id' : line.product_id.id,
                            'name' : line.product_id.name
                        })
                        line.write({
                                        'sale_line_ids': [(4, sale_line.id)]
                                    })
