from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class productproductInherit(models.Model):
    _inherit = 'maintenance.request'


    product_id = fields.Many2one('product.product' , string='Product')
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial', domain="[('product_id', '=', product_id)]")
    warranty_start = fields.Date('Warranty Start Date')
    warranty_end = fields.Date('Warranty End Date')
    warranty_status = fields.Selection(
        [('1', 'In progress'), ('2', 'Expired')], string="Warranty Status" , default = '1' , compute='_compute_warranty_status'
    )
    recurrent = fields.Boolean('Recurrent Re')
    repeat_every = fields.Integer('Repeat Every Intereval')
    repeat_unit = fields.Selection([
        ('day', 'Days'),
        ('week', 'Weeks'),
        ('month', 'Months'),
        ('year', 'Years'),
    ], default='week' )
    repeat_type = fields.Selection([
        ('forever', 'Forever'),
        ('until', 'Until'),
    ], default="forever", string="Until" )
    # repeat_until = fields.Date(string="End Date" )
    reference = fields.Many2one('sale.order' , 'Reference')
    partner_id = fields.Many2one('res.partner' , 'Customer')

    under_warranty = fields.Boolean()
    expected_mtbf = fields.Integer('Expected Mean Time')
    mtbf = fields.Integer('Mean Time Between')
    estimated_next_failure = fields.Integer('Estimated Next Failure')
    latest_failure_date = fields.Integer('Latest Failure')
    mttr = fields.Integer('Mean Time Repair')
    maintenance_for1 = fields.Selection([
        ('equipment', 'Equipment'),
        ('workcenter', 'Work Center'),
        ('warranty', 'Warranty')
    ], string='For', default='equipment', required=True)

    repair_order_id = fields.Many2one('repair.order')
    assigned_date = fields.Date('Assigned Date')
    effective_date = fields.Date('Effective Date')

    @api.constrains('lot_id' , 'product_id')
    def _onchange_lot_id(self):
        if self.lot_id and self.lot_id.product_id != self.product_id:
            raise ValidationError('The selected lot does not belong to the selected product.')

    @api.depends('warranty_start', 'warranty_end')
    def _check_warranty_status(self):
        for record in self:
            if record.warranty_start and record.warranty_end :
                if record.warranty_start >= record.warranty_end:
                    record.warranty_status ='1'
                else:
                    record.warranty_status ='2'

            else:
                record.warranty_status =False
    @api.constrains('warranty_status')
    def _check_warranty_status(self):
        for record in self:
            if record.warranty_status:
                if record.warranty_status =='2':
                    record.recurring_maintenance = False

    @api.constrains('warranty_start', 'warranty_end')
    def _check_warranty_dates1235(self):
        print(self)
        for record in self:
            if record.warranty_end and record.warranty_start:
                if record.warranty_end < record.warranty_start:
                    raise UserError('End Warranty Date cannot be earlier than Start Warranty Date.')

    def action_open_repair_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Repair Order',
            'view_mode': 'form',
            'res_model': 'repair.order',
            'res_id': self.repair_order_id.id,
            'target': 'current',
        }
    # @api.constrains('repeat_every', 'repeat_unit', 'repeat_type', 'repeat_until')
    # def calculate_schedule_dates125(self):
    #     print(123456)
    #     for rec in self:
    #         current = fields.Datetime.now()
    #         schedule_date = fields.Datetime.now()
    #         delta = {f"{rec.repeat_unit}s": rec.repeat_every}
    #         new_schedule_date = schedule_date + relativedelta(**delta)
    #         print(new_schedule_date)
    #         print(rec.repeat_until)
    #         date_object = rec.repeat_until
    #         if date_object:
    #             datetime_object = datetime.combine(date_object, datetime.min.time())
    #             if rec.repeat_type == 'forever' or (rec.repeat_type == 'until' and new_schedule_date <= datetime_object):
    #                 if rec.schedule_date and schedule_date >= current :
    #                     rec.update({
    #                         'schedule_date' : new_schedule_date
    #                     })
    #                 else:
    #                     rec.update({
    #                         'schedule_date' : new_schedule_date.date()
    #                     })
    #
    #         else:
    #             if rec.repeat_type == 'forever':
    #                 if rec.schedule_date and schedule_date >= current :
    #                     rec.update({
    #                         'schedule_date' : new_schedule_date
    #                     })
    #                 else:
    #                     rec.update({
    #                         'schedule_date' : new_schedule_date.date()
    #                     })
    @api.onchange('lot_id')
    def get_warranty_date123(self):
        for rec in self:
            if rec.lot_id:
                rec.warranty_start = rec.lot_id.start_warranty
                rec.warranty_end = rec.lot_id.end_warranty
    @api.model
    def calculate_schedule_dates(self):
        print(123)
        print(self)
        record = self.env['maintenance.request'].search([('maintenance_for1' ,'=','warranty')])
        for rec in record:
            print(123)
            schedule_date = rec.schedule_date or fields.Datetime.now()
            schedule_date += relativedelta(**{f"{rec.repeat_unit}s": rec.repeat_every})
            print(schedule_date)
            if rec.schedule_date:
                if rec.repeat_type == 'forever' and rec.schedule_date <= datetime.now():
                    rec.write({'schedule_date': schedule_date})
                if rec.repeat_type == 'until' and  schedule_date <= rec.repeat_until:
                    rec.write({'schedule_date': schedule_date})
            else:
                if rec.repeat_type == 'forever' :
                    rec.write({'schedule_date': schedule_date})
                if rec.repeat_type == 'until' :
                    rec.write({'schedule_date': schedule_date})

    @api.onchange('recurrent')
    def _onchange_recurrent(self):
        if self.recurrent:
            self.maintenance_type = 'preventive'
            return {'readonly': {'maintenance_type': True}}
        else:
            return {'readonly': {'maintenance_type': False}}


    @api.depends('warranty_end' , 'warranty_start')
    def _compute_warranty_status(self):
        for record in self:
            if record.warranty_start and record.warranty_end :
                if record.warranty_start >= record.warranty_end:
                    record.warranty_status ='2'
                else:
                    record.warranty_status ='1'

            else:
                record.warranty_status = False

    @api.constrains('recurrent')
    def compute_maintenance_for(self):
        for rec in self:
            if rec.recurrent:
                rec.maintenance_type = 'preventive'

    @api.depends('maintenance_for1')
    def compute_maintenance_for(self):
        for record in self:
            if record.maintenance_for1 in ['equipment', 'workcenter']:
                record.maintenance_for = record.maintenance_for1
            else:
                record.maintenance_for = 'equipment'

    def create_repair(self):
        for rec in self:
            pick = self.env['stock.picking.type'].search([('code' , '=' ,'repair_operation')] ,limit=1)
            repair = self.env['repair.order'].create({
                'partner_id' : rec.partner_id.id,
                # 'name' : rec.product_id.name + '-' +rec.lot_id.name,
                # 'parts_location_id' : int(16),
                'product_id' : rec.product_id.id,
                'user_id'  : rec.user_id.id,
                'under_warranty' : True,
                'maintenance_id' : rec.id,
                'picking_type_id' : pick.id,
                'lot_id' : rec.lot_id.id,
                'under_warranty' : True if rec.warranty_status =='1' else False

            })
            rec.repair_order_id = repair.id

class testttddtInherit(models.Model):
    _inherit = 'maintenance.equipment'

    product_id = fields.Many2one('product.product' , string='Product')
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial', domain="[('product_id', '=', product_id)]")
    warranty_start = fields.Date('Warranty Start Date')
    warranty_end = fields.Date('Warranty End Date')
    warranty_status = fields.Selection(
        [('1', 'In progress'), ('2', 'Expired')], string="Warranty Status" , default = '1' , compute='_compute_warranty_status'
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
    ], default="forever", string="Until" )
    repeat_until = fields.Date(string="End Date" )
    reference = fields.Many2one('sale.order' , 'Reference')
    partner_id = fields.Many2one('res.partner' , 'Customer')

    under_warranty = fields.Boolean()
    expected_mtbf = fields.Integer('Expected Mean Time')
    mtbf = fields.Integer('Mean Time Between')
    estimated_next_failure = fields.Integer('Estimated Next Failure')
    latest_failure_date = fields.Integer('Latest Failure')
    mttr = fields.Integer('Mean Time Repair')
    maintenance_for1 = fields.Selection([
        ('equipment', 'Equipment'),
        ('workcenter', 'Work Center'),
        ('warranty', 'Warranty')
    ], string='For', default='equipment', required=True)
    maintenance_for = fields.Selection([
        ('equipment', 'Equipment'),
        ('workcenter', 'Work Center'),
    ], string='For', default='equipment', required=True)
    repair_order_id = fields.Many2one('repair.order')
    request_id = fields.Many2one('maintenance.request')
    assigned_date = fields.Date('Assigned Date')
    effective_date = fields.Date('Effective Date')

    # equipment_id = fields.Many2one('maintenance.equipment')
    request_date = fields.Date('request Date')
    close_date = fields.Date('Close Date')
    maintenance_type = fields.Selection([('corrective', 'Corrective'), ('preventive', 'Preventive')], string='Maintenance Type', default="corrective")
    is_warranty = fields.Boolean()

    @api.constrains('lot_id' , 'product_id')
    def _onchange_lot_id(self):
        if self.lot_id and self.lot_id.product_id != self.product_id:
            raise ValidationError('The selected lot does not belong to the selected product.')
    @api.constrains('warranty_start', 'warranty_end')
    def _check_warranty_dates(self):
        for record in self:
            if record.warranty_end and record.warranty_start:
                if record.warranty_end < record.warranty_start:
                    raise UserError('End Warranty Date cannot be earlier than Start Warranty Date.')

    def archive_equipment_request(self):
        self.write({'archive': True, 'recurring_maintenance': False})

    def reset_equipment_request(self):
        first_stage_obj = self.env['maintenance.stage'].search([], order="sequence asc", limit=1)
        # self.write({'active': True, 'stage_id': first_stage_obj.id})
        pass
    @api.depends('warranty_end')
    def _compute_warranty_status(self):
        for record in self:
            if record.warranty_end and fields.Date.today() <= record.warranty_end:
                record.warranty_status = '1'  # In progress
            else:
                record.warranty_status = '2'  # Expired
    @api.model
    def calculate_schedule_dates(self):
        print(123)
        print(self)
        record = self.env['maintenance.equipment'].search([('maintenance_for1' ,'=','warranty')])
        for rec in record:
            print(123)
            schedule_date = rec.schedule_date or fields.Datetime.now()
            schedule_date += relativedelta(**{f"{rec.repeat_unit}s": rec.repeat_every})
            print(schedule_date)
            if rec.repeat_type == 'forever' and rec.schedule_date.date() <= datetime.now():
                rec.write({'schedule_date': schedule_date})
            if rec.repeat_type == 'until' and  schedule_date.date() <= rec.repeat_until:
                rec.write({'schedule_date': schedule_date})
            # if rec.recurrent:
            #
            #     schedule_date = rec.schedule_date or datetime.today()
            #
            #     # Calculate the increment based on repeat_every and repeat_unit
            #     increment = {
            #     'day': timedelta(days=rec.repeat_every),
            #     'week': timedelta(weeks=rec.repeat_every),
            #     'month': timedelta(days=30 * rec.repeat_every),  # Approximate for months
            #     'year': timedelta(days=365 * rec.repeat_every),  # Corrected line
            # }[rec.repeat_unit]
            #
            #     # Handle repeat type
            #     if rec.repeat_type == 'forever':
            #         # Forever, simply add the increment
            #         schedule_date += increment
            #
            #     elif rec.repeat_type == 'until' and rec.repeat_until:
            #         # Until a specific date, check if we've reached the end
            #         if schedule_date > rec.repeat_until:
            #             return None  # Reached the end date, no more schedule
            #         else:
            #             # Not reached the end yet, add the increment until reaching it
            #             schedule_date += increment
            #     print('schedule_date   >>>> ' , schedule_date)
            #     rec.write({
            #         'schedule_date' : schedule_date
            #     })
            # else:
            #     pass


    @api.constrains('recurrent')
    def _onchange_recurrent(self):
        # partner = self.env['res.users'].create([
        #     'name' :
        # ])
        if self.recurrent:
            self.maintenance_type = 'preventive'
        if self.recurrent and len(self.request_id) == 0:
            request= self.env['maintenance.request'].create({
                'name' : self.name,
                'product_id' : self.product_id.id,
                'lot_id' : self.lot_id.id,
                'warranty_start' : self.warranty_start,
                'warranty_end' : self.warranty_end,
                'recurring_maintenance' : self.recurrent,
                'repeat_interval' : self.repeat_every,
                'repeat_unit' : self.repeat_unit,
                'repeat_type' : self.repeat_type,
                'repeat_until' : self.repeat_until,
                'reference' : self.reference.id,
                # 'employee_id' : False,
                'maintenance_type' : 'preventive',
                'assigned_date' : self.warranty_start,
                'effective_date' : self.effective_date,
                'user_id' : self.technician_user_id.id,
                'partner_id' : self.partner_id.id,
                'schedule_date' : self.effective_date,
                'maintenance_for1' : 'warranty',

            })
            self.request_id = request.id

            return {'readonly': {'maintenance_type': True}}
        else:
            return {'readonly': {'maintenance_type': False}}

