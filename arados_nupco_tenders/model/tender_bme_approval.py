from odoo import api, fields, models, _


class TenderStock(models.Model):
    _name = 'tender.bme.approval'
    _rec_name='tender_id'

    tender_id = fields.Many2one('tenders' , string='Tender NO')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'Confirmed'),

    ], default='draft')

    nubco_ids = fields.One2many('tender.bme.approval.line', 'bme_id', string='NUPCO Products')


    def confirm(self):
        self.state='in_progress'


    def get_products(self):
        for rec in self:
            rec.nubco_ids.unlink()
            if rec.tender_id:
                for i in rec.tender_id.nubco_ids:
                    bme_line = self.env['tender.bme.approval.line'].create({
                        'product_id' : i.product_id.id,
                        'bme_id' : rec.id,

                    })


class TenderBME(models.Model):
    _name = 'tender.bme.approval.line'



    bme_id = fields.Many2one('tender.bme.approval' )
    product_id = fields.Many2one('product.product' , string='Product')
    pre_inst = fields.Float('Pre-Installation Cost')
    inst = fields.Float('Installation Cost')
    comm = fields.Float('commission Cost')
    warr_2_cust = fields.Integer('Warranty 2 Customer')
    warr_from_supp = fields.Integer('Warranty From Supplier')
    anticipated_warranty_cost = fields.Float('Anticipated Warranty Cost')
    ppm_main = fields.Integer('PPM/Maintenance Schedule')
