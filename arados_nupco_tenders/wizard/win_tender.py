from odoo import models, fields, api

class CustomWizard(models.TransientModel):
    _name = 'win.tender.wizard'

    po_number = fields.Char(string='Contract NO')
    tender_id = fields.Many2one('tenders')
    tender_name = fields.Char(string='Tender Number' ,related='tender_id.tender_no' , readonly=True)

    def action_add_details(self):
        for rec in self:
            rec.tender_id.state1 = 'open'
            order = self.env['nupco.orders'].create({
                'customer_id' : rec.tender_id.customer_id.id,
                'tender_id' : rec.tender_id.id,
                'tender_no' : rec.tender_id.tender_no,
                'name' : rec.tender_id.name,
                'responsible' : rec.tender_id.responsible.id,
                'date_from' : rec.tender_id.date_from,
                'date_to' : rec.tender_id.date_to,
                'validity' : rec.tender_id.validity,
                'tags_ids' : rec.tender_id.tags_ids.ids,
                'company_id' : rec.tender_id.company_id.id,
                'po_number' : rec.po_number,
            })
            rec.tender_id.write({
                'order_ids': [(4, order.id)]  # Use (4, id) to add a record to a Many2many field
            })
            for i in rec.tender_id.nubco_ids:
                order1 = self.env['nubco.tender'].create({
                    'tender_id':False,
                    'customer_ref' : i.customer_ref,
                    'etimad' : i.etimad,
                    'contract_item_no' : i.contract_item_no,
                    'item_type' : i.item_type,
                    'po_item' : i.po_item,
                    'cust_gen_code' : i.cust_gen_code,
                    'net_price_per' : i.net_price_per,
                    'per_unit' : i.per_unit,
                    'net_order_value' : i.net_order_value,
                    'tax_value' : i.tax_value,
                    'official_agent' :i.official_agent,
                    'delivery_address_id' : i.delivery_address_id.id,
                    'nupco_delivery_date' : i.nupco_delivery_date,
                    'delivery_no' : i.delivery_no,
                    'plant' : i.plant,
                    'order_id' : order.id,
                    'customer_id' : i.customer_id.id,
                    'nubco_serial' : i.nubco_serial,
                    'nubco_material' : i.nubco_material,
                    'nubco_material_des' : i.nubco_material_des,
                    'medical_group' : i.medical_group,
                    'quantity':i.quantity1,
                    'uom_id' : i.uom_id.id,
                    'price' : i.price,
                    'currency_id' : i.currency_id.id,
                    'vat_id' : i.vat_id.id,
                    'product_id' :i.product_id.id,
                    'manufacturer_id' : i.manufacturer_id.id,
                    'manufacturing_country' : i.manufacturing_country.id,
                    'product_packaging' : i.product_packaging.id,
                    'moq' : i.moq,
                    'volume' : i.volume,
                    'manufacture_process_local' : i.manufacture_process_local,
                    'temp' : i.temp,
                    'first_lead' : i.first_lead,
                    'lead_time' : i.lead_time,
                    'max_num_of_shipp' : i.max_num_of_shipp,

                })
                # i.write({
                #     'order_id' : order.id,
                #     # 'customer_id' : rec.tender_id.customer_id.id
                # })


        return {'type': 'ir.actions.act_window_close'}

    def calculate_won(self , customer , order):
        order_id = self.env['nupco.orders'].search([('id' , '=' , int(order))])
        total = 0
        for i in order_id.nubco_ids:
            if i.customer_id.id == int(customer):
                total += i.quantity * i.price

            return total
