from odoo import models, fields ,api , _
from datetime import datetime, timedelta
import math
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class MRDForcasting(models.Model):
    _name = 'mrd.forcasting'


    product_id = fields.Many2one('product.product'  , string='Product' ,domain=[('detailed_type', '=', 'product')])
    part_no = fields.Char(related='product_id.barcode' , string='Part NO')

    avg_sales = fields.Integer('AVG Sales' , compute = '_get_avg_sales')
    qty_on_hand = fields.Float(related='product_id.qty_available' , string='Quantity On Hand')
    months_to_cal = fields.Integer('Months')
    goal_mrd_fu = fields.Integer('MRD Goal Future' )
    goal_mrd = fields.Integer('MRD Goal', compute = '_get_goal_mrd')
    manager_opinion = fields.Integer('Manager Opinion')
    reserved_out = fields.Integer('Reserved Out' , compute = '_get_reserved_out')
    in_transit = fields.Integer('In Transit' , compute = '_get_in_transit')
    pending= fields.Integer('Pending' , compute = '_get_pending')
    balance = fields.Integer('Balance' , compute = '_get_balance')
    min_quan = fields.Integer('Min Quantity' , compute = '_get_min_quant')
    to_order = fields.Integer('To Order' , compute = '_get_to_order')
    lead_time = fields.Integer('lead time' , compute = '_get_lead_time')
    is_officer = fields.Boolean(compute='_compute_is_officer')
    vendor = fields.Many2one('res.partner', string='Vendor')
    Notes =fields.Char('Notes')
    def action_create_purchase_order(self):
        vendors = self.mapped('vendor').ids
        if len(vendors) > 1:
            raise UserError("Please select records for same vendor")
        else:
            if len(vendors) ==0:
                raise UserError("Please select records with vendor")
            else:

                po = self.env['purchase.order'].create({
                    'partner_id': vendors[0]
                })
                for rec in self:
                    # Create order lines
                    order_line = self.env['purchase.order.line'].create({
                        'order_id': po.id,
                        'product_id': rec.product_id.id,
                        'product_qty': rec.to_order,
                        'name': rec.product_id.name,
                        'price_unit': rec.product_id.list_price  # You may adjust the price as needed
                    })
    @api.model
    def default_get(self, fields_list):
        res = super(MRDForcasting, self).default_get(fields_list)
        vendor_id = self._context.get('search_default_vendor_id')
        if vendor_id:
            domain = [('vendor', '=', vendor_id)]
            res['domain'] = domain
        return res

    def _get_filter_domain(self,vendor):
        return [('vendor', '=', vendor)]  # Example filter domain

    @api.model
    def get_action(self , vendor):
        action = self.env.ref('base.action_res_partner_form')  # Example action reference
        action_domain = self._get_filter_domain(vendor)
        action['domain'] = action_domain
        return action
    
    @api.model
    def create(self, vals):
        # Call the original create method to create the record
        # Find the last record created before the current one
        last_record = self.search([], order='id desc', limit=1)

        # Set the values of months_to_cal and goal_mrd_fu from the last record
        if last_record:
            vals_to_update = {}
            if last_record.months_to_cal:
                vals['months_to_cal'] = last_record.months_to_cal
            if last_record.goal_mrd_fu:
                vals['goal_mrd_fu'] = last_record.goal_mrd_fu

        record = super(MRDForcasting, self).create(vals)



        return record
    @api.depends_context('uid')
    def _compute_is_officer(self):
        self.is_officer = self.env.user.has_group("sales_team.group_sale_manager")
    @api.depends('product_id')
    def _get_lead_time(self):
        for rec in self:
            if rec.product_id:
                order = self.env['product.template'].search([('id' , '=' , rec.product_id.product_tmpl_id.id)] , limit=1)
                if order.seller_ids:
                    rec.lead_time = order.seller_ids[0].delay

                else:
                    rec.lead_time =0
            else:
                rec.lead_time =0


    @api.constrains('product_id')
    def _default_vendor(self):
        for rec in self:
            product_id = rec.product_id.id
            if product_id:
                product = self.env['product.product'].search([('id' , '=' , product_id)])
                if product.product_tmpl_id.seller_ids:
                    rec.update({
                        'vendor' : product.product_tmpl_id.seller_ids[0].partner_id.id
                    })
    @api.constrains('months_to_cal', 'goal_mrd_fu')
    def _check_positive_values(self):
        for record in self:
            if record.months_to_cal < 0:
                raise UserError("Months to Calculate must be positive.")
            if record.goal_mrd_fu < 0:
                raise UserError("MRD Goal Future must be positive.")


    # @api.constrains('manager_opinion')
    # def _check_manager_opinion_range(self):
    #     for record in self:
    #         if record.manager_opinion < 1 or record.manager_opinion > 10000:
    #             raise UserError("Only positive values are allowed.")

    @api.constrains('product_id')
    def _check_product_id_unique(self):
        for record in self:
            if record.product_id:
                count = self.search_count([('product_id', '=', record.product_id.id), ('id', '!=', record.id)])
                if count > 0:
                    raise UserError("Product already exist.")

    @api.depends('product_id')
    def _get_min_quant(self):
        for rec in self:
            total = 0
            if rec.product_id:
                order = self.env['stock.warehouse.orderpoint'].search([('product_id' , '=' , rec.product_id.id)] )
                if order:
                    for i in order:
                        total += i.product_min_qty
                    rec.min_quan =total
                else:
                    rec.min_quan =0
            else:
                rec.min_quan =0


    def create_po(self):
        for rec in self:
            if rec.vendor:
                # Create a purchase order
                po = self.env['purchase.order'].create({
                    'partner_id': rec.vendor.id
                })

                # Create order lines
                order_line = self.env['purchase.order.line'].create({
                    'order_id': po.id,
                    'product_id': rec.product_id.id,
                    'product_qty': rec.to_order,
                    'name': rec.product_id.name,
                    'price_unit': rec.product_id.list_price  # You may adjust the price as needed
                })
            elif rec.product_id.product_tmpl_id.seller_ids:
                partner = rec.product_id.product_tmpl_id.seller_ids[0].partner_id
                po = self.env['purchase.order'].create({
                    'partner_id': partner.id
                })

                # Create order lines
                order_line = self.env['purchase.order.line'].create({
                    'order_id': po.id,
                    'product_id': rec.product_id.id,
                    'product_qty': rec.to_order,
                    'name': rec.product_id.name,
                    'price_unit': rec.product_id.list_price  # You may adjust the price as needed
                })

            else:
                raise ValidationError(_('Add Vendor to be able to create Purchase order !'))


    @api.model
    def update_months_to_cal(self, record_id, months):
        record = self.browse(record_id)
        record.months_to_cal = months
        return True


    @api.depends('balance' ,'min_quan'  )
    def _get_to_order(self):
        for rec in self:
            if rec.min_quan:
                rec.to_order = math.ceil(rec.balance / rec.min_quan) * rec.min_quan
                if rec.to_order <0:
                    rec.to_order = 0
            else:
                rec.to_order = 0

    @api.depends('goal_mrd' ,'qty_on_hand' , 'reserved_out' , 'in_transit' , 'pending','manager_opinion')
    def _get_balance(self):
        for rec in self :
            total = rec.goal_mrd - (rec.qty_on_hand -rec.reserved_out + rec.in_transit + rec.pending)
            if total < 0 :
                rec.balance = 0
            else:
                rec.balance = total

    @api.depends('goal_mrd_fu' ,'avg_sales' , 'lead_time','manager_opinion')
    def _get_goal_mrd(self):

        for rec in self:
            if rec.manager_opinion or rec.lead_time:
                rec.goal_mrd = math.ceil(rec.avg_sales * rec.goal_mrd_fu+(rec.avg_sales/30*(rec.lead_time + rec.manager_opinion)))
            else:
                rec.goal_mrd =0

    @api.depends('months_to_cal' , 'goal_mrd_fu' ,'manager_opinion')
    def _get_avg_sales(self):
        for record in self:
            total_amount=0
            if record.months_to_cal:
                # Calculate the start date based on the number of months
                start_date = datetime.now() - timedelta(days=30 * record.months_to_cal)
                domain = [
                    ('create_date', '>=', start_date)
                ]
                sales_orders = self.env['sale.order'].search(domain)
                # Calculate the total amount
                for i in sales_orders.order_line:
                    if i.product_id.id == record.product_id.id:
                        total_amount += i.qty_invoiced

                # Calculate the average sales
                if sales_orders:
                    record.avg_sales = math.ceil(total_amount / record.months_to_cal)
                else:
                    record.avg_sales = 0
            else:
                record.avg_sales = 0


    @api.depends('months_to_cal' , 'goal_mrd_fu' , 'product_id','manager_opinion')
    def _get_pending(self):
        for record in self:
            total_amount=0
            if record.months_to_cal:
                # Calculate the start date based on the number of months
                start_date = datetime.now() - timedelta(days=30 * record.months_to_cal)
                domain = [
                    ('create_date', '>=', start_date),
                    ('state' , '=' , 'draft')
                ]
                pu_orders = self.env['purchase.order'].search(domain)
                for i in pu_orders.order_line:
                    if i.product_id.id == record.product_id.id:

                        total_amount += i.product_qty


                if total_amount:
                    record.pending = math.ceil(total_amount)
                else:
                    record.pending = 0
            else:
                record.pending = 0

    @api.depends('months_to_cal' , 'goal_mrd_fu','manager_opinion')
    def _get_reserved_out(self):
        for record in self:
            total_amount=0
            if record.months_to_cal:
                # Calculate the start date based on the number of months
                start_date = datetime.now() - timedelta(days=30 * record.months_to_cal)
                print('start_date >>> ' , start_date)
                domain = [
                    ('create_date', '>=', start_date),
                    ("picking_id.picking_type_id.code", "=", "outgoing"),
                    ("picking_id.sale_id.state", "=", "sale"),
                    ('state' , 'in' , ['assigned' , 'partially_available'])
                ]
                move_line = self.env['stock.move.line'].search(domain)
                for i in move_line:
                    if i.product_id.id == record.product_id.id:
                        total_amount += i.quantity

                record.reserved_out = total_amount

            else:
                record.reserved_out = 0


    @api.depends('months_to_cal' , 'goal_mrd_fu','manager_opinion')
    def _get_in_transit(self):
        for record in self:
            total_amount=0
            if record.months_to_cal:
                # Calculate the start date based on the number of months
                start_date = datetime.now() - timedelta(days=30 * record.months_to_cal)
                domain = [
                    ('create_date', '>=', start_date),
                    ("picking_id.picking_type_id.code", "=", "incoming"),
                    ("picking_id.purchase_id.state", "=", "purchase"),
                    ('state' , 'in' , ['assigned' ])
                ]
                move_line = self.env['stock.move.line'].search(domain)
                for i in move_line:
                    if i.product_id.id == record.product_id.id:
                        total_amount += i.quantity

                record.in_transit = total_amount

            else:
                record.in_transit = 0
