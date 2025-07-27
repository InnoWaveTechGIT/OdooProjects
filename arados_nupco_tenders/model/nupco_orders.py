import math

from odoo import models, fields, api
from datetime import datetime, timedelta
from io import BytesIO
import xlrd
import xlsxwriter
import tempfile
import os
import tempfile
import base64
import platform

class OrderTender(models.Model):
    _name = 'nupco.orders'
    _rec_name = 'po_number'

    name = fields.Char(string='Tender Name')
    customer_id = fields.Many2one('res.partner' , string='Customer')
    responsible =fields.Many2one('res.users')
    date_from = fields.Date('From')
    date_to = fields.Date('To')
    validity = fields.Integer('Validity' , compute='_compute_validity')
    tags_ids = fields.Many2many('tenders.tags' ,'order_tender_tag', string='Tags')
    company_id = fields.Many2one('res.company')
    state = fields.Selection([
        ('Draft' , 'Draft'),
        ('In Progress' , 'In Progress'),
        ('Lost' ,'Lost'),
        ('Open' ,'Open'),
        ('Close' ,'Close'),
    ])
    po_number = fields.Char(string='Contract No')
    nubco_ids= fields.One2many('nubco.tender' , 'order_id' , string='NUPCO Products')
    nubco_total_ids= fields.One2many('nubco.total.tender' , 'order_id' , string='NUPCO Products')
    total_award_values=fields.Float('Total Awarded Value' , compute='get_total_awarded')
    customer_ids = fields.Many2many('res.partner' , compute='get_customers')
    sale_ids = fields.Many2many('sale.order' , compute = 'get_sales_records')
    len_order_id = fields.Integer( compute="_1235888")
    tender_id = fields.Many2one('tenders' , ondelete='cascade')

    document_no = fields.Char('Document Number' , related='tender_id.document_no')
    tender_no = fields.Char('Tender No' , related='tender_id.tender_no')
    excel_file = fields.Binary('Generated Excel File', readonly=True)


    def open_file(self ,file_path):
        system = platform.system()
        if system == 'Windows':
            os.startfile(file_path)
        elif system == 'Darwin':  # macOS
            os.system('open ' + file_path)
        elif system == 'Linux':
            os.system('xdg-open ' + file_path)
        else:
            raise OSError("Unsupported operating system")

    def open_excel_import_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Excel Data',
            'res_model': 'order.excel.import.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},

        }

    def generate_excel_file(self):
        for tender in self:
            excel_buffer = BytesIO()
            workbook = xlsxwriter.Workbook(excel_buffer, {})  # Specify the path to save the Excel file
            worksheet = workbook.add_worksheet()

            # Add headers
            headers = ['Tender Number','Document Number','Customer','Customer Ref','Etimad','Contract Item No',
                       'Purchasing Document', 'PO Item', 'NUPCO Trade Code', 'Cust Gen Code', 'Material Description',
                       'NUPCO Material Description', 'Quantity', 'Unit of Measurement', 'Net Price', 'Per Unit',
                       'Net Price/Per unit 1', 'Net Order Value','Tax Value' ,'Tax Percentage', 'Delivery Address' , 'Nupco Delivery Date'
                ,'Delivery NO','Plant','Trade Name','Manufacturer', 'Manufacturer Country', 'Package Size','MOQ',
                       'Volume','Manu.Process Local', 'Temp.Condition', '1st Lead time Delivery','Lead Time Delivery Period',
                       'Max NO of Shipments']

            for col, header in enumerate(headers):
                worksheet.write(0, col, header)

            row = 1
            for line in tender.nubco_ids:
                worksheet.write(row, 0, tender.tender_no)
                worksheet.write(row, 1, tender.document_no)
                worksheet.write(row, 2, line.customer_id.name)
                worksheet.write(row, 3, line.customer_ref)
                worksheet.write(row, 4, line.etimad)
                worksheet.write(row, 5, line.contract_item_no)
                worksheet.write(row, 6, line.purchasing_document)
                worksheet.write(row, 7, line.po_item)
                worksheet.write(row, 8, line.nubco_serial)
                worksheet.write(row, 9, line.cust_gen_code)
                worksheet.write(row, 10, line.nubco_material)
                worksheet.write(row, 11, line.nubco_material_des)
                worksheet.write(row, 12, line.quantity)
                worksheet.write(row, 13, line.uom_id.name)
                worksheet.write(row, 14, line.price)
                worksheet.write(row, 15, line.per_unit)
                worksheet.write(row, 16, line.net_price_per)
                worksheet.write(row, 17, line.net_order_value)
                worksheet.write(row, 18, line.tax_value)
                worksheet.write(row, 19, str(line.vat_id.name))
                worksheet.write(row, 20, line.delivery_address_id.name)
                worksheet.write(row, 21, str(line.nupco_delivery_date))
                worksheet.write(row, 22, line.delivery_no)
                worksheet.write(row, 23, line.plant)
                worksheet.write(row, 24, line.product_id.name)
                worksheet.write(row, 25, line.manufacturer_id.name)
                worksheet.write(row, 26, line.manufacturing_country.name)
                worksheet.write(row, 27, line.product_packaging.name)
                worksheet.write(row, 28, line.moq)
                worksheet.write(row, 29, line.volume)
                worksheet.write(row, 30, line.manufacture_process_local)
                worksheet.write(row, 31, line.temp)
                worksheet.write(row, 32, line.first_lead)
                worksheet.write(row, 33, line.lead_time)
                worksheet.write(row, 34, line.max_num_of_shipp)
                row += 1
            workbook.close()
            excel_buffer.seek(0)
            encoded_data = base64.b64encode(excel_buffer.read())

            attach_vals = {
                'name': f'{tender.name}.xlsx',
                'datas': encoded_data,
                'res_model': 'nupco.orders',  # Update this with your model name
                'res_id': tender.id,  # Update this with the ID of your record
            }

            attachment = self.env['ir.attachment'].create(attach_vals)
            excel_buffer.close()

            tender.excel_file = attachment.datas

            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/web/binary/order_download_generated_excel?id=%s' % (self.id)
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'self',
            }
    @api.depends('tender_id')
    def get_sales_records(self):
        for record in self:
            # Search sale orders related to the current tender
            sale_orders = self.env['sale.order'].search([('nupco_po_number', '=', record.id)])
            # Assign the found sale orders to the sale_ids field
            record.sale_ids = sale_orders

    def copy(self, default=None):
        if default is None:
            default = {}
        # Set the state to 'draft' when duplicating
        default['state'] = 'Draft'
        default['sale_ids'] = False
        return super(OrderTender, self).copy(default=default)

    def action_open_tender(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tenders',
            'res_model': 'tenders',
            'view_mode': 'list,form',
            'domain': [('id', '=', self.tender_id.id)],
            'target': 'current',
        }

    def action_open_sale_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.sale_ids.ids)],
            'target': 'current',
        }
    @api.depends('write_date')
    def _1235888(self):
        parent_id = 0
        for lead in self:
            lead.get_total_page_awarded()
            del_plane = self.env['tender.delivery.plan'].search([('tender_number' ,'=' ,lead.tender_id.id)])
            delivery_plan = self.env['tender.delivery.plan.line'].search([('nubco_order_id' , '=' ,lead.id)])
            if delivery_plan:

                delivery_plan.unlink()

            if lead.tender_id.state1 in ['open' , 'close'] and len(del_plane) == 0:
                    x=self.env['tender.delivery.plan'].create({
                        'tender_number' : lead.tender_id.id,
                        'total_awarded' : lead.total_award_values,
                        'start_date' : lead.tender_id.date_from,
                        'end_date' : lead.tender_id.date_to,
                        'status' : lead.tender_id.state1,
                        'company_id' : lead.tender_id.company_id.id
                    })
                    parent_id = x.id
                    for line in lead.nubco_total_ids:

                        self.env['tender.delivery.plan.line'].create({
                            'delivery_id' : int(parent_id),
                            'customer_id' : line.customer_id.id,
                            'nubco_order_id' : lead.id,
                            'total_awarded' : line.total_award_values
                        })

            elif lead.tender_id.state1 in ['open' , 'close']:
                for line in lead.nubco_total_ids:
                        self.env['tender.delivery.plan.line'].create({
                            'delivery_id' : int(del_plane[0].id),
                            'customer_id' : line.customer_id.id,
                            'nubco_order_id' : lead.id,
                            'total_awarded' : line.total_award_values
                        })

            lead.len_order_id =len(self.sale_ids)



    @api.depends('date_from', 'date_to')
    def _compute_validity(self):
        for record in self:
            if record.date_from and record.date_to:
                # Convert date objects to strings
                date_from_str = record.date_from.strftime('%Y-%m-%d')
                date_to_str = record.date_to.strftime('%Y-%m-%d')

                # Calculate the number of days between date_from and date_to
                delta = (datetime.strptime(date_to_str, "%Y-%m-%d") - datetime.strptime(date_from_str, "%Y-%m-%d")).days

                # Calculate the number of years
                years = delta / 365
                # Adjust validity based on the number of years
                if years < 1:  # If less than 1 year, set as 1
                    record.validity = 1
                else:
                    record.validity = math.ceil(years)  # Use the integer part of years
            else:
                record.validity = 1
    def new_quotaion(self):

        lines = self.nubco_ids.ids
        return {
            'name': 'New Quotation',
            'type': 'ir.actions.act_window',
            'res_model': 'quote.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('arados_nupco_tenders.view_wizard_quote_wizard_form').id,
            'target': 'new',
            'context': {'default_tender_id': self.id , 'default_purchase_document_ids' : lines},
        }
    @api.depends('nubco_ids')
    def get_total_awarded(self):
        for rec in self:
            total=0.0
            for line in rec.nubco_ids:
                total += (line.quantity * line.price)

            rec.total_award_values = total


    @api.depends('nubco_ids')
    def get_customers(self):
        for rec in self:
            rec.customer_ids = rec.nubco_ids.mapped('customer_id').ids

    def get_total_page_awarded(self):
        for rec in self:
            rec.nubco_total_ids.unlink()

            customer_ids = rec.nubco_ids.mapped('customer_id')
            for customer in customer_ids:
                total=0.0
                for line in rec.nubco_ids:
                    if line.customer_id.id == customer.id:
                        total +=(line.quantity * line.price)

                self.env['nubco.total.tender'].create({
                    'order_id' : rec.id ,
                    'customer_id' : customer.id,
                    'total_award_values' : total
                })









class NubcoTotalTender(models.Model):
    _name = 'nubco.total.tender'


    order_id= fields.Many2one('nupco.orders')
    customer_id = fields.Many2one('res.partner' , string='Customer')
    total_award_values=fields.Float('Total Awarded Value' ,readonly='1')
