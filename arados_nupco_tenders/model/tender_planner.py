from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class TenderPlanner(models.Model):
    _name = 'tender.planner'


    product_id = fields.Many2one('product.product', string='Product Name' , required=True)
    part_no = fields.Char(related='product_id.barcode' , string='Barcode')
    nubco_order_id = fields.Many2one('nupco.orders' , string='NUPCO Order' , compute='get_nupco_order')
    nubco_order_line_id = fields.Many2one('nubco.tender' , string='NUPCO Order Line' , compute='get_nupco_order')
    selling_factor  = fields.Float('Selling Factor')
    last_winnig_price = fields.Many2one('tender.planner.last.price' )
    unit_price = fields.Float('Unit Price' ,compute='get_unit_price')
    total_price = fields.Float('Total Price' , compute='get_total_price')
    GP = fields.Float('GP' , compute='get_GP')
    comparison_id = fields.Many2one('price.comparison')
    negotiation_id = fields.Many2one('price.negotiation')
    target_disc = fields.Float('Target discount(%)')
    target_amount = fields.Float('Target Amount' , compute='get_target')
    target_per = fields.Float('Target %' , compute='get_target')
    product_ids = fields.Many2many('product.product' , string='Products' , compute='get_products')


    @api.depends('product_id')
    def get_products(self):
        records = self.env['nubco.tender'].search([])
        for rec in self:
            products = records.mapped('product_id')
            rec.product_ids = products

    @api.constrains('target_disc')
    def _check_target_discount(self):
        for record in self:
            if record.target_disc < 0 or record.target_disc > 100:
                raise ValidationError("Target discount must be between 0 and 100%.")

    @api.depends('target_disc' , 'last_winnig_price' , 'GP' ,'negotiation_id' )
    def get_target(self):

        for rec in self:
            rec.target_amount = rec.last_winnig_price.supplier_price * (1 + (rec.target_disc -rec.GP))
            if rec.negotiation_id.curr_price:
                rec.target_per = (rec.target_amount - rec.negotiation_id.curr_price) / rec.negotiation_id.curr_price
            else:
                rec.target_per = 0.0
    def negotiation_price(self):
        self.ensure_one()  # Ensure that we are working with a single record
        if self.negotiation_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Price Negotiation',
                'res_model': 'price.negotiation',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.negotiation_id.id,
                'target': 'new',  # Opens in the current window
            }
        else:
            raise ValidationError('There is no NUPCO Order for this product')

    @api.constrains('product_id')
    def create_negotiation(self):
        for rec in self:
            nego = self.env['price.negotiation'].create({
                'prev_price' : 0.0
            })

            rec.negotiation_id = nego.id
    def last_compartion(self):
        self.ensure_one()  # Ensure that we are working with a single record
        if self.last_winnig_price:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Price Comparison',
                'res_model': 'price.comparison',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.comparison_id.id,
                'target': 'new',  # Opens in the current window
            }
        else:
            raise ValidationError('There is no NUPCO Order for this product')


    @api.constrains('last_winnig_price')
    def create_comparison(self):
        for rec in self:

            comp = self.env['price.comparison'].create({
                'planner_id' : rec.id,

            })

            rec.comparison_id = comp.id
    @api.depends('total_price' , 'last_winnig_price')
    def get_GP(self):
        for rec in self:
            if rec.total_price:
                rec.GP = (rec.total_price -float(rec.last_winnig_price.total_cost)) /rec.total_price
            else:
                rec.GP = 0.0

    @api.depends('unit_price' , 'last_winnig_price')
    def get_total_price(self):
        for rec in self:
            rec.total_price = rec.unit_price * float(rec.last_winnig_price.init_qty)
    @api.depends('selling_factor' , 'last_winnig_price')
    def get_unit_price(self):
        for rec in self:
            rec.unit_price = rec.selling_factor * rec.last_winnig_price.unit_cost_in_SAR
    @api.constrains('product_id')
    def _check_product_id_unique(self):
        for record in self:
            if record.product_id:
                count = self.search_count([('product_id', '=', record.product_id.id), ('id', '!=', record.id)])
                if count > 0:
                    raise ValidationError("Product already exist.")

    @api.constrains('product_id' , 'nubco_order_line_id')
    def create_last_winning(self):
        for rec in self:
            if rec.last_winnig_price:
                if rec.last_winnig_price.product_id == rec.product_id.id:
                    pass
                else:
                    if rec.nubco_order_line_id :
                        lasr_win = self.env['tender.planner.last.price'].create({
                            'product_id' : rec.product_id.id,
                            'nubco_order_line_id' : rec.nubco_order_line_id.id,
                        })
                        rec.last_winnig_price = lasr_win.id

            else:
                if rec.nubco_order_line_id :
                    lasr_win = self.env['tender.planner.last.price'].create({
                        'product_id' : rec.product_id.id,
                        'nubco_order_line_id' : rec.nubco_order_line_id.id,
                    })
                    rec.last_winnig_price = lasr_win.id
    @api.depends('product_id')
    def get_nupco_order(self):
        for rec in self:
            product_ids=[]
            if rec.product_id:
                records = self.env['nubco.tender'].search(['&' ,('product_id' , '=' ,rec.product_id.id),('order_id', '!=', False)])
                x = records.mapped('order_id')
                x = x.ids
                x_sorted = sorted(x, reverse=True)

                if x_sorted:
                    rec.nubco_order_id = x_sorted[0]
                    record = self.env['nubco.tender'].search([('order_id' , '=' ,x_sorted[0])] , limit=1)
                    rec.nubco_order_line_id =record.id
                else:
                    rec.nubco_order_id = False
                    rec.nubco_order_line_id= False

            else:
                rec.nubco_order_id = False
                rec.nubco_order_line_id= False




    def last_wining_price(self):
        self.ensure_one()  # Ensure that we are working with a single record
        if self.last_winnig_price:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Last Winning Price',
                'res_model': 'tender.planner.last.price',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.last_winnig_price.id,
                'target': 'new',  # Opens in the current window
            }
        else:
            raise ValidationError('There is no NUPCO Order for this product')



class TenderPlannerLast(models.Model):
    _name = 'tender.planner.last.price'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string='Product Name' , required=True)
    part_no = fields.Char(related='product_id.barcode' , string='Barcode')
    uom_id = fields.Char(related='product_id.uom_id.name' , string='UOM')
    price = fields.Float(related='product_id.lst_price' , string='Price')
    discount = fields.Integer()
    NET = fields.Float()
    supplier_id = fields.Many2one('res.partner' , string='Supplier' , compute='_default_vendor')

    nubco_order_line_id = fields.Many2one('nubco.tender' , string='NUPCO Order Line')

    Nupco_Code = fields.Char('Nupco Code' ,compute='get_data_from_order' )
    description = fields.Char('Description' ,compute='get_data_from_order' )
    group = fields.Char('Group' ,compute='get_data_from_order' )
    init_qty = fields.Char('Initial QTY' ,compute='get_data_from_order' )
    nupco_uom = fields.Char('NUPCO UOM' ,compute='get_data_from_order' )

    tender_ids = fields.One2many('tender.last.winning.price' , 'tender_planner_last_id' )

    supplier_price = fields.Float('Supplier Price For EACH')
    currency_id = fields.Many2one('res.currency')
    landed_cost = fields.Float('Landed Cost Factor')
    Finance_fator = fields.Float('Finance Factor')
    bm_factor = fields.Float('BM Factor')
    unit_cost_in_SAR = fields.Float('Unit Cost In SAR')
    total_cost = fields.Float('Total Cost In SAR')

    @api.constrains('supplier_price', 'landed_cost', 'Finance_fator' , 'bm_factor' , 'unit_cost_in_SAR' , 'total_cost')
    def _check_positive_prices(self):
        for record in self:
            if record.supplier_price < 0:
                raise ValidationError("supplier_price must be a positive integer.")
            if record.landed_cost < 0:
                raise ValidationError("landed_cost must be a positive integer.")
            if record.Finance_fator < 0:
                raise ValidationError("Finance_fator must be a positive integer.")
            if record.bm_factor < 0:
                raise ValidationError("bm_factor must be a positive integer.")
            if record.unit_cost_in_SAR < 0:
                raise ValidationError("unit_cost_in_SAR must be a positive integer.")
            if record.total_cost < 0:
                raise ValidationError("total_cost must be a positive integer.")
    @api.depends('product_id')
    def _default_vendor(self):
        for rec in self:
            product_id = rec.product_id.id
            if product_id:
                product = self.env['product.product'].browse(product_id)
                if product:
                    if product.product_tmpl_id.seller_ids:
                        rec.supplier_id = product.product_tmpl_id.seller_ids[0].partner_id.id
                    else:
                        rec.supplier_id = False  # No seller found
                else:
                    rec.supplier_id = False  # Invalid product
            else:
                rec.supplier_id = False  # Reset if no product is selected
    @api.depends('nubco_order_line_id')
    def get_data_from_order(self):
        for rec in self:
            if rec.nubco_order_line_id:
                for line in rec.nubco_order_line_id.order_id.tender_id.nubco_ids:
                    if line.product_id.id == rec.product_id.id:
                        rec.Nupco_Code = line.nubco_serial
                        rec.description = line.nubco_material_des
                        rec.group = line.medical_group
                        rec.init_qty = line.quantity1
                        rec.nupco_uom = line.uom_id.name
                        rec.supplier_id = line.manufacturer_id.id

                        break
            else:
                rec.Nupco_Code = False
                rec.description = False
                rec.group = False
                rec.init_qty = False
                rec.nupco_uom = False




class TenderPlannerLastLines(models.Model):
    _name='tender.last.winning.price'

    tender_planner_last_id = fields.Many2one('tender.planner.last.price')
    tender_id = fields.Many2one('tenders' , string='Tender')
    price_1 = fields.Float('Price #1')
    price_2 = fields.Float('Price #2')
    company_price = fields.Float('Company Price')

    @api.constrains('price_1', 'price_2', 'company_price')
    def _check_positive_prices(self):
        for record in self:
            if record.price_1 < 0:
                raise ValidationError("Price #1 must be a positive integer.")
            if record.price_2 < 0:
                raise ValidationError("Price #2 must be a positive integer.")
            if record.company_price < 0:
                raise ValidationError("Company Price must be a positive integer.")
    @api.constrains('tender_planner_last_id')
    def _check_tender_planner_last_id_limit(self):
        for record in self:
            count = self.search_count([
                ('tender_planner_last_id', '=', record.tender_planner_last_id.id)
            ])
            if count > 3:
                raise ValidationError("You cannot create more than three records with the same Tender Planner ID.")


class TenderPlannerPriceComparison(models.Model):
    _name='price.comparison'

    trend_price = fields.Float('Tender Price')
    private_prices = fields.Float('Private Prices' ,compute='calculate_values')
    planner_id = fields.Many2one('tender.planner')
    tender_1 = fields.Float('Tender #1' ,compute='calculate_values')
    tender_2 = fields.Float('Tender #2' ,compute='calculate_values')
    tender_Company = fields.Float('Tender #Company' ,compute='calculate_values')

    @api.depends('trend_price' , 'planner_id')
    def calculate_values(self):
        for rec in self:
            if rec.planner_id.last_winnig_price.NET:
                rec.private_prices = (rec.planner_id.selling_factor - rec.planner_id.last_winnig_price.NET) / rec.planner_id.last_winnig_price.NET
            else:
                rec.private_prices = 0.0
            if rec.planner_id.last_winnig_price.tender_ids :
                if rec.planner_id.last_winnig_price.tender_ids[0].price_1:
                    rec.tender_1 = (rec.planner_id.unit_price - rec.planner_id.last_winnig_price.tender_ids[0].price_1) / rec.planner_id.last_winnig_price.tender_ids[0].price_1
                else:
                    rec.tender_1 = False
                if rec.planner_id.last_winnig_price.tender_ids[0].price_2:
                    rec.tender_2 = (rec.planner_id.unit_price - rec.planner_id.last_winnig_price.tender_ids[0].price_2) / rec.planner_id.last_winnig_price.tender_ids[0].price_2
                else:
                    rec.tender_2= False

                if rec.planner_id.last_winnig_price.tender_ids[0].company_price:
                    rec.tender_Company = (rec.planner_id.unit_price - rec.planner_id.last_winnig_price.tender_ids[0].company_price) / rec.planner_id.last_winnig_price.tender_ids[0].company_price
                else:
                    rec.tender_Company= False

            else:
                rec.tender_1 = False
                rec.tender_2= False
                rec.tender_Company= False

class TenderPlannerPriceNego(models.Model):
    _name='price.negotiation'

    prev_price = fields.Float('Previous Price')
    curr_price = fields.Float('Current Price')
