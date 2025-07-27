from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class srikLotIngerit(models.Model):
    _inherit = 'stock.lot'

    start_warranty_in = fields.Date('Warranty Start' ,compute='get_warranty_date')
    start_warranty_end = fields.Date('Warranty Start Date' ,compute='get_warranty_date')
    warranty = fields.Boolean('Warranty' , related='product_id.product_tmpl_id.warranty')
    start_warranty = fields.Date('Warranty Start Date')
    end_warranty = fields.Date('Warranty End Date')
    warranty_status = fields.Selection(
        [('1', 'In progress'), ('2', 'Expired')], string="Warranty Status" ,compute='get_warranty_status'
    )
    recurrent = fields.Boolean('Recurrent')
    repeat_every = fields.Integer('Repeat Every')
    repeat_unit = fields.Selection([
        ('day', 'Days'),
        ('week', 'Weeks'),
        ('month', 'Months'),
        ('year', 'Years'),
    ], default='week')
    repeat_type = fields.Selection([
        ('forever', 'Forever'),
        ('until', 'Until'),
    ], default="forever", string="Until")
    repeat_until = fields.Date(string="End Date")

    @api.depends('start_warranty' , 'end_warranty')
    def get_warranty_status(self):
        for record in self:
            if record.start_warranty and record.end_warranty :
                if record.start_warranty > record.end_warranty:
                    record.warranty_status ='2'
                else:
                    record.warranty_status ='1'

            else:
                record.warranty_status = False

    @api.constrains('start_warranty', 'end_warranty')
    def _check_warranty_dates(self):
        for record in self:
            if record.end_warranty and record.start_warranty:
                if record.end_warranty < record.start_warranty:
                    raise UserError('End Warranty Date cannot be earlier than Start Warranty Date.')

    @api.depends('purchase_order_ids')
    def get_warranty_date(self):
        for rec in self:
            print('in depends >>>>>')
            if rec.purchase_order_ids:
                for i in rec.purchase_order_ids:
                    for move in i.picking_ids.move_ids_without_package:

                        if move.product_id.id == rec.product_id.id:
                            move_line = self.env['stock.move.line'].search([('move_id', '=', move.id)], limit=1)
                            print('move_line >>>> ' , move_line)
                            if move_line:
                                print('move.move_line[0].id >>> ' , move_line[0])
                                print('move.move_line[0].id >>> ' , move_line[0].start_warranty)
                                rec.start_warranty_in = move_line[0].start_warranty
                                rec.start_warranty_end = move_line[0].end_warranty
                                if not rec.start_warranty:
                                    rec.start_warranty = move_line[0].start_warranty
                                    rec.end_warranty = move_line[0].end_warranty
            else:
                rec.start_warranty_in = False
                rec.start_warranty_end = False

    @api.constrains('start_warranty_in')
    def update_warranty_dates(self):
        for rec in self:
            print("in ?>>>>>>")
            print('rec.start_warranty_in ?>>>> ' , str(rec.start_warranty_in))
            if rec.start_warranty_in:
                print('rec.start_warranty_in ?>>>> ' , str(rec.start_warranty_in))
                rec.write({
                    "start_warranty" :rec.start_warranty_in,
                    "end_warranty": rec.start_warranty_end
                })


