from odoo import api, fields, models, _
import base64
import math
from io import BytesIO
from datetime import datetime, timedelta
import xlrd
import xlsxwriter
import tempfile
import os
import tempfile
import base64
import platform
from datetime import timedelta
from odoo.http import request

class Tender(models.Model):
    _name = 'tenders'
    _rec_name='tender_no'
    @api.model
    def _default_responsible(self):
        return self.env.user.id
    def _default_company(self):
        return self.env.user.company_id.id


    customer_id = fields.Many2one('res.partner', string='Customer' ,required=True)
    tender_no = fields.Char('Tender Number',required=True)
    responsible = fields.Many2one('res.users', default=_default_responsible ,required=True)
    date_from = fields.Date('Date' ,required=True)
    date_to = fields.Date('To')
    validity = fields.Integer('Validity' , compute='_calculate_validity')
    tags_ids = fields.Many2many('tenders.tags', string='Tags')
    company_id = fields.Many2one('res.company' ,default=_default_company ,required=True)
    state1 = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('lost', 'Lost'),
        ('open', 'Open'),
        ('close', 'Close'),
    ], default='draft')
    excel_file = fields.Binary('Generated Excel File', readonly=True)
    document_id = fields.Many2one('documents.document')
    nubco_ids = fields.One2many('nubco.tender', 'tender_id', string='NUBCO Products')
    order_ids = fields.Many2many('nupco.orders',  string='Orders')


    document_no = fields.Char('Document Number' ,required=True)
    name = fields.Char( string='Tender Name' ,required=True)

    @api.depends('date_from', 'date_to')
    def _calculate_validity(self):
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

    def copy(self, default=None):
        if default is None:
            default = {}
        # Set the state to 'draft' when duplicating
        default['state1'] = 'draft'
        default['order_ids'] = False
        return super(Tender, self).copy(default=default)


    def action_open_orders(self):
        if self.order_ids:
            order_ids = self.order_ids.ids
            if len(order_ids) == 1:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'NUPCO Order',
                    'res_model': 'nupco.orders',
                    'view_mode': 'form',
                    'res_id': order_ids[0],
                    'target': 'current',
                }
            else:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'NUPCO Orders',
                    'res_model': 'nupco.orders',
                    'view_mode': 'list,form',
                    'domain': [('id', 'in', order_ids)],
                    'target': 'current',
                }
        else:
            # Handle the case where no order_ids are found
            # You can customize this part based on your requirements
            return {'type': 'ir.actions.act_window_close'}
    def action_open_document(self):
        self.ensure_one()
        url = str(self.document_id.access_url)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }

    @api.constrains('state1' , 'nubco_ids')
    def create_bmerecord(self):
        for rec in self:

                records = self.env['tender.bme.approval'].search([('tender_id' ,'=' , rec.id)])
                if len(records) == 0 :
                    bme = self.env['tender.bme.approval'].create({
                        'tender_id' : rec.id,
                    })
                    for i in rec.nubco_ids :
                        bme_line = self.env['tender.bme.approval.line'].create({
                        'product_id' : i.product_id.id,
                        'bme_id' : bme.id,

                    })



    @api.constrains('state1' ,'order_ids','nubco_ids' )
    def create_delivery_plan(self):
        for rec in self:
            if rec.state1 in ['open' , 'close']:
                orders = self.env['nupco.orders'].search([('tender_id' ,'=',rec.id)])
                tenders = self.env['tender.delivery.plan'].search([('tender_number' ,'=',rec.id)],limit=1)
                if tenders:
                    tenders.delivery_ids.unlink()
                    for order in rec.order_ids:
                        for line in order.sale_ids:
                            delivery_line = self.env['tender.delivery.plan.line'].create({
                                'customer_id' : line.partner_id.id,
                                'delivery_id' : tenders.id,
                                'nubco_order_id' : order.id,
                                'total_awarded' : self.get_awarded_from_order(order.id , line.partner_id.id),


                            })

                else:
                    delivery = self.env['tender.delivery.plan'].create({
                        'tender_number' : rec.id,
                        'start_date' : rec.date_from,
                        'end_date' : rec.date_to,
                        'status' : rec.state1,
                        'company_id' : rec.company_id.id


                    })
                    for order in orders:
                        for line in order.sale_ids:
                            delivery_line = self.env['tender.delivery.plan.line'].create({
                                'customer_id' : line.partner_id.id,
                                'delivery_id' : delivery.id,
                                'nubco_order_id' : order.id,
                                'total_awarded' : self.get_awarded_from_order(order.id , line.partner_id.id),


                            })

            else:
                tenders = self.env['tender.delivery.plan'].search([('tender_number' ,'=',rec.id)])
                tenders.unlink()

    def get_awarded_from_order(self , order_id , partner_id):
        orders = self.env['nupco.orders'].search([('id' , '=' , int(order_id))])
        if orders:
            orders.get_total_page_awarded()
            for line in orders.nubco_total_ids:
                if line.customer_id.id == int(partner_id):
                    return line.total_award_values
                else:
                    return 0
        else:
            return 0


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


    def confirm_tender(self):
        self.state1 = 'in_progress'

    def open_excel_import_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Excel Data',
            'res_model': 'excel.import.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_tender_id': self.id},
        }

    def generate_excel_file(self):
        for tender in self:
            excel_buffer = BytesIO()
            workbook = xlsxwriter.Workbook(excel_buffer, {})  # Specify the path to save the Excel file
            worksheet = workbook.add_worksheet()

            # Add headers
            headers = ['Tender Number','Document Number','Change Option','Item Type','Material Number', 'Material Description', 'NUBCO Material Description', 'Medical Group', 'Quantity', 'UOM',
                       'Price', 'Currency', 'VAT', 'Trade Name', 'Manufacturer', 'Country', 'Package Size','MDMA Code' ,'foc', 'MDMA Expiry Date' , 'SFDA Code' ,'Concentration', 'Sheif Life', 'MOQ',
                       'Volume', 'Manufacturing Process', 'Official Agent','Company Comment','Company Comment Term','Temperature Condition', '1st Lead Time', 'Lead Time', 'Max Shipments']

            for col, header in enumerate(headers):
                worksheet.write(0, col, header)

            row = 1
            for line in tender.nubco_ids:
                worksheet.write(row, 0, tender.tender_no)
                worksheet.write(row, 1, tender.document_no)
                worksheet.write(row, 2, line.change_option)
                worksheet.write(row, 3, line.item_type)
                worksheet.write(row, 4, line.nubco_serial)
                worksheet.write(row, 5, line.nubco_material)
                worksheet.write(row, 6, line.nubco_material_des)
                worksheet.write(row, 7, line.medical_group)
                worksheet.write(row, 8, line.quantity)
                worksheet.write(row, 9, line.uom_id.name)
                worksheet.write(row, 10, line.price)
                worksheet.write(row, 11, line.currency_id.name)
                worksheet.write(row, 12, line.vat_id.name)
                worksheet.write(row, 13, line.product_id.name)
                worksheet.write(row, 14, line.manufacturer_id.name)
                worksheet.write(row, 15, line.manufacturing_country.name)
                worksheet.write(row, 16, line.product_packaging.name)
                worksheet.write(row, 17, line.mdma_code)
                worksheet.write(row, 18, line.foc)
                worksheet.write(row, 19, str(line.MDMA_exp))
                worksheet.write(row, 20, line.SFGa_code)
                worksheet.write(row, 21, line.concentration)
                worksheet.write(row, 22, line.sheif_life)
                worksheet.write(row, 23, line.moq)
                worksheet.write(row, 24, line.volume)
                worksheet.write(row, 25, line.manufacture_process_local)
                worksheet.write(row, 26, line.official_agent)
                worksheet.write(row, 27, line.company_comment)
                worksheet.write(row, 28, line.company_comment_term)
                worksheet.write(row, 29, line.temp)
                worksheet.write(row, 30, line.first_lead)
                worksheet.write(row, 31, line.lead_time)
                worksheet.write(row, 32, line.max_num_of_shipp)
                row += 1
            workbook.close()
            excel_buffer.seek(0)
            encoded_data = base64.b64encode(excel_buffer.read())

            attach_vals = {
                'name': f'{tender.name}.xlsx',
                'datas': encoded_data,
                'res_model': 'tenders',  # Update this with your model name
                'res_id': tender.id,  # Update this with the ID of your record
            }

            attachment = self.env['ir.attachment'].create(attach_vals)
            excel_buffer.close()

            tender.excel_file = attachment.datas

            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/web/binary/download_generated_excel?id=%s' % (self.id)
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'self',
            }


    def open_custom_wizard(self):

        return {
            'name': 'Add Details',
            'type': 'ir.actions.act_window',
            'res_model': 'win.tender.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('arados_nupco_tenders.view_wizard_form').id,
            'target': 'new',
            'context': {'default_tender_id': self.id},
        }

    def lost_tender(self):
        self.state1 = 'lost'

    @api.constrains('create_date')
    def create_tender_document(self):
        for rec in self:
            tender_work = self.env['documents.document'].search([('name', '=', 'Tenders')], limit=1)
            work_1 = self.env['documents.document'].create({
                'name': rec.name,
                'folder_id': tender_work.id,
                'type' : 'folder',
                'company_id': rec.company_id.id
            })
            sub_work_space = ['Document Purchase receipt', 'Document with Terms & Conditions', 'Copy of suppliers offer',
                              'Award document', 'Customer POS and contract copies', 'NUPCO Communication /change/cancellation/Penalties',
                              'BID submission Report', 'Suppliers confirmation of terms and agreements', 'Discount letters to NUPCO']

            rec.document_id= work_1.id
            for i in sub_work_space:
                self.env['documents.document'].create({
                    'name': i,
                    'folder_id': work_1.id,
                    'type' : 'folder',
                    'company_id': rec.company_id.id
                })

class NubcoTender(models.Model):
    _name = 'nubco.tender'
    _rec_name = 'purchasing_document'


    tender_id = fields.Many2one('tenders')
    order_id= fields.Many2one('nupco.orders')
    tender_bme_id= fields.Many2one('tender.bme.approval')
    customer_id = fields.Many2one('res.partner', string='Customer')
    nubco_serial = fields.Char('Material Number')
    nubco_material = fields.Char('Material Description')
    nubco_material_des = fields.Char('NUPCO Material Description')
    medical_group = fields.Char('Pharma Group')
    quantity = fields.Float('Quantity')
    quantity1 = fields.Float('Quantity')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measurement' ,required=True)
    price = fields.Float('Price')
    currency_id = fields.Many2one('res.currency')
    vat_id = fields.Many2one('account.tax', string='VAT', domain="[('type_tax_use', '=', 'sale')]")
    product_id = fields.Many2one('product.product', string='Trade Name' , required=True)
    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer')
    manufacturer_ids = fields.Many2many('res.partner', string='Manufacturers' , compute='get_manufacturares')
    manufacturing_country = fields.Many2one('res.country', string='Manufacturer Country',related='product_id.product_tmpl_id.country_of_origin')
    mdma_code = fields.Char( related='product_id.product_tmpl_id.mdma_code')
    MDMA_exp = fields.Date( related='product_id.product_tmpl_id.MDMA_exp')
    SFGa_code = fields.Char(related='product_id.product_tmpl_id.SFGa_code')
    sheif_life = fields.Integer(related='product_id.product_tmpl_id.sheif_life')
    product_packaging = fields.Many2one('product.packaging', string='Package Size')
    moq = fields.Char('MOQ')
    volume = fields.Char('Volume')
    manufacture_process_local = fields.Char('Manu.Process Local')
    temp = fields.Char('Temp.Condition')
    first_lead = fields.Char('1st Lead time Delivery')
    lead_time = fields.Char('Lead Time Delivery Period')
    max_num_of_shipp = fields.Char('Max NO of Shipments')
    quted_id = fields.Many2one('quted.items')
    sd = fields.Char(compute='_default_vendor')

    change_option = fields.Char('Change Option')
    item_type = fields.Selection([('Orig' , 'Orig') , ('Alt' , 'Alt')] , required=True , default='Orig')
    foc = fields.Float('FOC%')
    concentration = fields.Char()
    official_agent = fields.Selection([('yes' , 'Yes') , ('no' , 'No')] , required=True , default='yes')
    company_comment = fields.Char('Company Comments')
    company_comment_term = fields.Char('Company Comments Term')
    # order New Fields
    customer_ref = fields.Char('Customer Ref/PO No')
    etimad = fields.Char('Eitimad Number')
    contract_item_no = fields.Char('Contract Item No')
    purchasing_document = fields.Char('Purchasing Document')
    po_item = fields.Char('PO Item')
    cust_gen_code = fields.Char('Cust Gen Code')
    per_unit = fields.Float('Per Unit')
    net_price_per = fields.Float('Net Price/Per unit 1')
    net_order_value = fields.Float('Net Order Value' , compute='get_net_order_value')
    tax_value = fields.Float('Tax Value' , compute='get_tax_value')
    delivery_address_id = fields.Many2one('res.partner', string='Delivery Address')
    nupco_delivery_date = fields.Date('Nupco Delivery Date')
    delivery_no = fields.Integer('Delivery NO')
    plant = fields.Char('Plant')


    @api.depends('vat_id' , 'net_order_value')
    def get_tax_value(self):
        for rec in self:
            rec.tax_value = (rec.vat_id.amount / 100) * rec.net_order_value

    @api.depends('quantity' , 'price')
    def get_net_order_value(self):
        for rec in self:
            # rec.net_order_value = 0
            rec.net_order_value = rec.quantity* rec.price


    @api.constrains('customer_id' , 'product_id' , 'quantity' ,'quantity1')
    def create_quated_items(self):
        for rec in self:
            rec.quted_id.unlink()
            if rec.order_id and rec.customer_id:
                quted = self.env['quted.items'].create({
                    'tender_id' : rec.order_id.tender_id.id,
                    'barcode': rec.product_id.barcode,
                    'product_id': rec.product_id.id,
                    'supplier': rec.manufacturer_id.name,
                    'tender_no': rec.order_id.tender_no,
                    'qty' : self.get_quantu(rec.order_id.tender_id.id , rec.product_id.id),
                    'uom': rec.uom_id.name,
                    'unit_price': rec.price,
                    'total_value': rec.quantity * rec.price,
                    'won_value': rec.quantity,
                    'customer': rec.customer_id.id,
                    'order': rec.order_id.id
                })
                rec.quted_id = quted.id

        return True



    def get_quantu(self , tender,product):
        qua = 0
        record = self.env['tenders'].search([('id' , '=' ,int(tender))])
        for i in record.nubco_ids:
            if i.product_id.id == int(product):
                qua= i.quantity1


        return qua




    def calculate_quantuty(self , record , product):
        lines = self.env['nubco.tender'].search([('order_id' ,'=' , record.order_id.id)])
        quantity = 0
        for line in lines:
            if line.product_id.id == product:
                quantity += line.quantity

        return quantity
    def calculate_won(self, customer, order):
        order_id = self.env['nupco.orders'].search([('id', '=', int(order))])
        total = 0
        for i in order_id.nubco_ids:
            if i.customer_id == customer:  # Avoid including the current record
                total += i.quantity * i.price
        return total

    @api.depends('product_id')
    def get_manufacturares(self):
        for rec in self:
            ids = []
            product_id = rec.product_id.id
            if product_id:
                product = self.env['product.product'].browse(product_id)
                if product:
                    if product.product_tmpl_id.seller_ids:
                        for man in product.product_tmpl_id.seller_ids:
                            ids.append(man.partner_id.id)

                        rec.manufacturer_ids = [(6, 0, ids)]
                    else:
                        rec.manufacturer_ids = False  # No seller found
                else:
                    rec.manufacturer_ids = False  # Invalid product
            else:
                rec.manufacturer_ids = False  # Reset if no product is selected

    @api.depends('product_id')
    def _default_vendor(self):
        for rec in self:
            product_id = rec.product_id.id
            if product_id:
                product = self.env['product.product'].browse(product_id)
                if product:
                    if product.product_tmpl_id.seller_ids:
                        rec.manufacturer_id = product.product_tmpl_id.seller_ids[0].partner_id.id
                    else:
                        rec.manufacturer_id = False  # No seller found
                else:
                    rec.manufacturer_id = False  # Invalid product
            else:
                rec.manufacturer_id = False  # Reset if no product is selected

            rec.sd = False
class NubcoTenderTags(models.Model):
    _name = 'tenders.tags'

    name = fields.Char('Name')
