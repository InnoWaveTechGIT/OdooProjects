from odoo import api, fields, models, tools, _



class AccountMoveLine(models.Model):
    _inherit = "sale.order.line"

    lot_id = fields.Many2one('stock.lot', string="Lots", domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]")


class StockPicking(models.Model):
    _inherit = "stock.picking"


    sale_id = fields.Many2one('sale.order', string="Sale Order")

    @api.constrains('origin')
    def _check_origin_startswith_s(self):
        for picking in self:
            if picking.origin and picking.origin.startswith('S'):
                sale_order = self.env['sale.order'].search([('name', '=', picking.origin)], limit=1)
                if sale_order:
                    picking.sale_id = sale_order.id
class StockPlinrg(models.Model):
    _inherit = "stock.move.line"


    @api.constrains('origin')
    def _update_lot_ids(self):
        for picking in self:
            if picking.reference :
                pick = self.env['stock.picking'].search([('name', '=', picking.reference)], limit=1)
                sale_order = self.env['sale.order'].search([('name', '=', pick.origin)], limit=1)
            if sale_order:
                for line in sale_order.order_line:
                        if line.product_id.id == picking.product_id.id and line.lot_ids:
                            print('In >>>>')
                            try:
                                picking.lot_id = line.lot_id.id
                            except Exception as e:
                                print(str(e))
