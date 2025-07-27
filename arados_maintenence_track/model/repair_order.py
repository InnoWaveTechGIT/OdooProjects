from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools.float_utils import float_compare

class productproductInherit(models.Model):
    _inherit = 'repair.order'



    maintenance_id = fields.Many2one('maintenance.request')
    region = fields.Selection(
        [('East' , 'EAST') , ('West' , 'WEST') , ('CENTRAL' , 'CENTRAL') , ('SOUTH' , 'SOUTH')]
    )
    under_wwosr = fields.Boolean(string='UNDER W.W.O.S.P')
    under_wwsp = fields.Boolean(string='UNDER W.W.S.P')
    ppm = fields.Boolean(string='P.P.M')
    INSTALLATION = fields.Boolean(string='INSTALLATION')
    CONTRACT = fields.Boolean(string='CONTRACT')
    INVOICE = fields.Boolean(string='S.INVOICE')
    work_details_ids = fields.One2many('work.details.repair' , 'repair_id' , string="Work Details")
    action_taken_ids = fields.One2many('action.details.repair' , 'repair_id' , string="Action Taken")
    parts_ids = fields.One2many('action.parts.repair' , 'repair_id' , string="parts")
    def action_validate(self):
        self.ensure_one()
        if self.filtered(lambda repair: any(m.product_uom_qty < 0 for m in repair.move_ids)):
            raise UserError(_("You can not enter negative quantities."))
        if not self.product_id or self.product_id.type == 'consu':
            return self._action_repair_confirm()
        if self.product_id.product_tmpl_id.warranty == True:
            return self._action_repair_confirm()
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        available_qty_owner = sum(self.env['stock.quant'].search([
            ('product_id', '=', self.product_id.id),
            ('location_id', '=', self.location_id.id),
            ('lot_id', '=', self.lot_id.id),
            ('owner_id', '=', self.partner_id.id),
        ]).mapped('quantity'))
        available_qty_noown = sum(self.env['stock.quant'].search([
            ('product_id', '=', self.product_id.id),
            ('location_id', '=', self.location_id.id),
            ('lot_id', '=', self.lot_id.id),
            ('owner_id', '=', False),
        ]).mapped('quantity'))
        repair_qty = self.product_uom._compute_quantity(self.product_qty, self.product_id.uom_id)
        for available_qty in [available_qty_owner, available_qty_noown]:
            if float_compare(available_qty, repair_qty, precision_digits=precision) >= 0:
                return self._action_repair_confirm()

        return {
            'name': self.product_id.display_name + _(': Insufficient Quantity To Repair'),
            'view_mode': 'form',
            'res_model': 'stock.warn.insufficient.qty.repair',
            'view_id': self.env.ref('repair.stock_warn_insufficient_qty_repair_form_view').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_product_id': self.product_id.id,
                'default_location_id': self.location_id.id,
                'default_repair_id': self.id,
                'default_quantity': repair_qty,
                'default_product_uom_name': self.product_id.uom_name
            },
            'target': 'new'
        }

    def action_open_MR(self):

        self.ensure_one()
        if len(self.maintenance_id) == 1:
            view_mode = 'form'
            view_id = self.env.ref('arados_maintenence_track.hr_equipment_request_view_form123').id
        else:
            view_mode = 'tree,form'
            view_id = self.env.ref('arados_maintenence_track.view_maintenance_request_tree_custom1').id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': view_mode,
            'view_id': view_id,
            'res_id': self.maintenance_id.ids[0] if len(self.maintenance_id) == 1 else False,
            'domain': [('id', 'in', self.maintenance_id.ids)],
            'target': 'current',
        }


    @api.constrains('state')
    def _change_request_state(self):
        for rec in self:
            print(rec)
            print(rec.state)
            if rec.state =='done':

                if rec.maintenance_id:
                    print(rec.maintenance_id)
                    stage = self.env['maintenance.stage'].search([('is_repaired' , '=' , True)])
                    if stage:
                        print(stage)
                        rec.maintenance_id.stage_id = stage.id


class WorkDetailstInherit(models.Model):
    _name = 'work.details.repair'

    name = fields.Char('Description')
    repair_id = fields.Many2one('repair.order')

class WorkDetailstInherit(models.Model):
    _name = 'action.details.repair'

    name = fields.Char('Description')
    repair_id = fields.Many2one('repair.order')


class PartsRepair(models.Model):
    _name = 'action.parts.repair'

    product_id = fields.Many2one('product.product' , string='Products')
    quantity = fields.Float('Quantity')
    repair_id = fields.Many2one('repair.order')
