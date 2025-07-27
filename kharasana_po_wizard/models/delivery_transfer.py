from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DeliveryTransferWizard(models.TransientModel):
    _name = 'delivery.transfer.wizard'
    _description = 'Delivery Transfer Wizard'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)
    partner_id = fields.Many2one('res.partner', string='Contact', required=True)
    project_id = fields.Many2one('project.project', string='Project')

    line_ids = fields.One2many(
        'delivery.transfer.wizard.line',
        'wizard_id',
        string='Products'
    )

    @api.model
    def default_get(self, fields):
        res = super(DeliveryTransferWizard, self).default_get(fields)
        if self._context.get('active_id'):
            po = self.env['purchase.order'].browse(self._context['active_id'])
            res['purchase_order_id'] = po.id
            res['partner_id'] = po.partner_id.id
            res['project_id'] = po.project_id.id if po.project_id else False

            # Prepare lines
            lines = []
            for line in po.order_line:
                if line.product_id.type == 'consu':
                    lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'product_qty': line.product_qty,
                    }))
            res['line_ids'] = lines
        return res

    def action_create_delivery(self):
        self.ensure_one()

        if not self.line_ids:
            raise UserError(_('Please select at least one product to transfer.'))

        # Get the picking type
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),
            ('warehouse_id', '!=', False),
        ], limit=1)

        if not picking_type:
            raise UserError(_('No outgoing picking type found.'))

        # Create the picking
        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': self.partner_id.property_stock_customer.id,
            'partner_id': self.partner_id.id,
            'origin': self.purchase_order_id.name,
            'project_id': self.project_id.id if self.project_id else False,
        })
        self.purchase_order_id.write({
            'picking_ids': [(4, picking.id, 0)]
        })
        # Create move lines
        for line in self.line_ids:
            if line.product_qty <= 0:
                continue

            self.env['stock.move'].create({
                'name': line.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_qty,
                'product_uom': line.product_id.uom_id.id,
                'picking_id': picking.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
            })

        # Confirm the picking
        # picking.action_confirm()

        # Return action to open the picking
        return {
            'name': _('Delivery Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': picking.id,
            'view_mode': 'form',
            'target': 'current',
        }


class DeliveryTransferWizardLine(models.TransientModel):
    _name = 'delivery.transfer.wizard.line'
    _description = 'Delivery Transfer Wizard Line'

    wizard_id = fields.Many2one('delivery.transfer.wizard', string='Wizard')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Char(string='Description')
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure')
