
from odoo import models, fields, api
from odoo.exceptions import UserError

class ScrapWizard(models.TransientModel):
    _name = 'add.month.wizard'

    quantity = fields.Integer('Month')

    @api.constrains('quantity')
    def _check_positive_quantity(self):
        for record in self:
            if record.quantity < 0:
                raise UserError("Quantity must be positive.")
            if record.quantity > 1000:
                raise UserError("Quantity must be smaller than 1000.")
    def add_months(self):
        records = self.env['mrd.forcasting'].search([])


        for i in records:
            i.update({
                'months_to_cal' : int(self.quantity)
            })

        return {
        'type': 'ir.actions.client',
        'tag': 'reload',
    }

class VendorWizard(models.TransientModel):
    _name = 'add.vendor.wizard'

    vendor_id = fields.Many2one('res.partner' , string='Vendor')
    # def _prepare_product_context(self):
    #     return {
    #         'search_default_vendor': self.vendor_id.id,
    #         'search_default_domain': [('vendor', '=', self.vendor_id.id)],
    #     }

    def add_vendor(self):
        if not self.vendor_id:
            raise UserError("Please select a vendor.")
        records = self.env['product.product'].search([])
        prod=[]
        for rec in records:
            product_id = rec.id
            if product_id:
                product = self.env['product.product'].search([('id' , '=' , product_id)])
                if product.product_tmpl_id.seller_ids:
                    if product.product_tmpl_id.seller_ids[0].partner_id.id == self.vendor_id.id:
                        prod.append(product_id)

        records = self.env['mrd.forcasting'].search([])
        ids = list(set(records.mapped('product_id').ids))
        for i in prod:
            if i not in ids:
                if records:
                    self.env['mrd.forcasting'].create({
                        'product_id' : i,
                        'months_to_cal' : records[0].months_to_cal,
                        'goal_mrd_fu' : records[0].goal_mrd_fu,
                        'vendor' : self.vendor_id.id
                    })
                else:
                    self.env['mrd.forcasting'].create({
                        'product_id' : i,
                        'months_to_cal' : 1,
                        'goal_mrd_fu' :1,
                        'vendor' : self.vendor_id.id
                    })

        return {
        'type': 'ir.actions.client',
        'tag': 'reload',
    }


        # res_ids = self.env['mrd.forcasting'].search([('vendor', '=', self.vendor_id.id)])
        #
        # products_map = records.mapped('product_id').ids
        # products = self.env['product.product'].search([('id' , 'in' , products_map)])
        # print('products >>>> ' , products)
        # prod_map =[]
        # for product in products:
        #     # print('products.product_tmpl_id.seller_ids[0].partner_id.id >> ' , product.product_tmpl_id.seller_ids[0].partner_id.id)
        #     print("self.vendor_id.id >>>>>> " ,self.vendor_id.id )
        #     if product.product_tmpl_id.seller_ids:
        #         if product.product_tmpl_id.seller_ids[0].partner_id.id == self.vendor_id.id:
        #             if product.id not in prod_map:
        #                 prod_map.append(product.id)
        #
        #
        # print('prod_map >>>>> ' , prod_map)
        # if not res_ids:
        #     res_ids = self.env['mrd.forcasting'].search([('product_id', 'in', prod_map)])
        #     print('res_ids >>> ' , res_ids)
        #     if not res_ids:
        #         raise UserError("No records for this vendor.")
        # if len(res_ids) == 1:
        #     view_mode = 'list'
        #     view_id = self.env.ref('arados_mrd_forcasting.view_mrd_forcasting_tree').id
        # else:
        #     view_mode = 'tree'
        #     view_id = self.env.ref('arados_mrd_forcasting.view_mrd_forcasting_tree').id
        #
        # return {
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'mrd.forcasting',
        #     'view_mode': view_mode,
        #     'view_id': view_id,
        #     'res_id': res_ids.ids,
        #     'domain': [('id', 'in', res_ids.ids)],
        #     'target': 'current',
        # }


class GoalWizard(models.TransientModel):
    _name = 'add.goal.wizard'

    quantity = fields.Integer('Goal')

    @api.constrains('quantity')
    def _check_positive_quantity(self):
        for record in self:
            if record.quantity < 0:
                raise UserError("Quantity must be positive.")
            if record.quantity > 1000:
                raise UserError("Quantity must be smaller than 1000.")
    def add_goals(self):
        records = self.env['mrd.forcasting'].search([])


        for i in records:
            i.update({
                'goal_mrd_fu' : int(self.quantity)
            })

        return {
        'type': 'ir.actions.client',
        'tag': 'reload',
    }
