from odoo import api, fields, models, _
import base64
from io import BytesIO
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

    @api.model
    def _default_responsible(self):
        return self.env.user.id
    def _default_company(self):
        return self.env.user.company_id.id

    name = fields.Char(compute='_compute_tender_name', string='Tender Name')
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
    document_id = fields.Many2one('documents.folder')
    nubco_ids = fields.One2many('nubco.tender', 'tender_id', string='NUBCO Products')
    order_ids = fields.Many2many('nupco.orders',  string='Orders')

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
                    'view_mode': 'tree,form',
                    'domain': [('id', 'in', order_ids)],
                    'target': 'current',
                }
        else:
            # Handle the case where no order_ids are found
            # You can customize this part based on your requirements
            return {'type': 'ir.actions.act_window_close'}
    def action_open_document(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url+"/web?#action=326&model=documents.document&view_type=kanban&cids=1&menu_id=199&folder_id=" + str(self.document_id.id)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }

    @api.constrains('state1' , 'nubco_ids')
    def create_bmerecord(self):
        for rec in self:

                records = self.env['tender.bme.approval'].search([('tender_id' ,'=' , rec.id)])
                # records.unlink()
                if len(records) == 0 :
                    bme = self.env['tender.bme.approval'].create({
                        'tender_id' : rec.id,
                    })
                    print('bme >>>>>>> ' , bme)
                    for i in rec.nubco_ids :
                        bme_line = self.env['tender.bme.approval.line'].create({
                        'product_id' : i.product_id.id,
                        'bme_id' : bme.id,

                    })



    @api.constrains('state1' ,'order_ids','nubco_ids' )
    def create_delivery_plan(self):
        print('self >>>>>>> ', self)
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

    @api.depends('date_from', 'date_to')
    def _calculate_validity(self):
        if self.date_from and self.date_to:
            date_start = fields.Date.from_string(self.date_from)
            date_end = fields.Date.from_string(self.date_to)
            years = (date_end - date_start).days / 365.25  # Approximate number of years
            self.validity = max(1, round(years))

        else:
            self.validity =0
    # @api.depends('excel_file')
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

    # @api.constrains('excel_file')
    # def _download_excel_file(self):
    #     print(1235)
    #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     url = base_url + '/web/binary/download_generated_excel?id=%s' % (self.id)
    #     print('url >>>>>> ' , url)
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': url,
    #         'target': 'self',
    #     }


        # for record in self:
        #     if record.excel_file:
        #         with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        #             temp_file.write(base64.b64decode(record.excel_file))
        #             temp_file.close()
        #             self.open_file(temp_file.name)

    # @api.constrains('excel_file')
    # def _onchange_excel_file(self):
    #     self._download_excel_file()
    @api.depends('tender_no', 'customer_id')
    def _compute_tender_name(self):
        for record in self:
            if record.tender_no:
                record.name = record.tender_no
            else:
                record.name = 'New'


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
            headers = ['NUBCO Serial', 'NUBCO Material', 'NUBCO Material Description', 'Medical Group', 'Quantity', 'UOM',
                       'Price', 'Currency', 'VAT', 'Trade Name', 'Manufacturer', 'Country', 'Product Packaging','MDMA Code' , 'MDMA Expiry Date' , 'SFDA Code' , 'Sheif Life', 'MOQ',
                       'Volume', 'Manufacturing Process', 'Temperature Condition', '1st Lead Time', 'Lead Time', 'Max Shipments']

            for col, header in enumerate(headers):
                worksheet.write(0, col, header)

            row = 1
            for line in tender.nubco_ids:
                worksheet.write(row, 0, line.nubco_serial)
                worksheet.write(row, 1, line.nubco_material)
                worksheet.write(row, 2, line.nubco_material_des)
                worksheet.write(row, 3, line.medical_group)
                worksheet.write(row, 4, line.quantity)
                worksheet.write(row, 5, line.uom_id.name)
                worksheet.write(row, 6, line.price)
                worksheet.write(row, 7, line.currency_id.name)
                worksheet.write(row, 8, line.vat_id.name)
                worksheet.write(row, 9, line.product_id.name)
                worksheet.write(row, 10, line.manufacturer_id.name)
                worksheet.write(row, 11, line.manufacturing_country.name)
                worksheet.write(row, 12, line.product_packaging.name)

                worksheet.write(row, 13, line.mdma_code)
                worksheet.write(row, 14, str(line.MDMA_exp))
                worksheet.write(row, 15, line.SFGa_code)
                worksheet.write(row, 16, line.sheif_life)
                worksheet.write(row, 17, line.moq)
                worksheet.write(row, 18, line.volume)
                worksheet.write(row, 19, line.manufacture_process_local)
                worksheet.write(row, 20, line.temp)
                worksheet.write(row, 21, line.first_lead)
                worksheet.write(row, 22, line.lead_time)
                worksheet.write(row, 23, line.max_num_of_shipp)
                # Add other fields similarly
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
            print('url >>>>>> ' , url)
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'self',
            }


    def open_custom_wizard(self):
        self.state1 = 'open'
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
            tender_work = self.env['documents.folder'].search([('name', '=', 'Tenders')], limit=1)
            work_1 = self.env['documents.folder'].create({
                'name': rec.name,
                'parent_folder_id': tender_work.id
            })
            sub_work_space = ['Document Purchase receipt', 'Document with Terms & Conditions', 'Copy of suppliers offer',
                              'Award document', 'Customer POS and contract copies', 'NUPCO Communication /change/cancellation/Penalties',
                              'BID submission Report', 'Suppliers confirmation of terms and agreements', 'Discount letters to NUPCO']

            rec.document_id= work_1.id
            for i in sub_work_space:
                self.env['documents.folder'].create({
                    'name': i,
                    'parent_folder_id': work_1.id
                })
        print('Documents Created Successfully')

class NubcoTender(models.Model):
    _name = 'nubco.tender'

    tender_id = fields.Many2one('tenders')
    order_id= fields.Many2one('nupco.orders')
    tender_bme_id= fields.Many2one('tender.bme.approval')
    customer_id = fields.Many2one('res.partner', string='Customer')
    nubco_serial = fields.Char('NUPCO Serial')
    nubco_material = fields.Char('NUPCO Material')
    nubco_material_des = fields.Char('NUPCO Material Description')
    medical_group = fields.Char('Medical Group')
    quantity = fields.Float('Quantity')
    quantity1 = fields.Float('Quantity')
    uom_id = fields.Many2one('uom.uom', string='UOM' ,required=True)
    price = fields.Float('Price')
    currency_id = fields.Many2one('res.currency')
    vat_id = fields.Many2one('account.tax', string='VAT')
    product_id = fields.Many2one('product.product', string='Trade Name' , required=True)
    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer')
    manufacturer_ids = fields.Many2many('res.partner', string='Manufacturers' , compute='get_manufacturares')
    manufacturing_country = fields.Many2one('res.country', related='product_id.product_tmpl_id.country_of_origin')
    mdma_code = fields.Char( related='product_id.product_tmpl_id.mdma_code')
    MDMA_exp = fields.Date( related='product_id.product_tmpl_id.MDMA_exp')
    SFGa_code = fields.Char(related='product_id.product_tmpl_id.SFGa_code')
    sheif_life = fields.Integer(related='product_id.product_tmpl_id.sheif_life')
    product_packaging = fields.Many2one('product.packaging', string='Product Packaging')
    moq = fields.Char('MOQ')
    volume = fields.Char('Volume')
    manufacture_process_local = fields.Char('Manu.Process Local')
    temp = fields.Char('Temp.Condition')
    first_lead = fields.Char('1st Lead time Delivery')
    lead_time = fields.Char('Lead Time Delivery Period')
    max_num_of_shipp = fields.Char('Max NO of Shipments')
    quted_id = fields.Many2one('quted.items')
    sd = fields.Char(compute='_default_vendor')

    @api.constrains('customer_id' , 'product_id' , 'quantity' ,'quantity1')
    def create_quated_items(self):
        for rec in self:
            rec.quted_id.unlink()
            print(1997)  # Replace with your desired action
            print('rec.tender_id.tender_no >>> ' , rec.tender_id.tender_no)
            print('rec.quantity >>> ' , rec.quantity)
            if rec.order_id and rec.customer_id:
                # Pass required data (potentially from parent_path) as arguments
                print('rec.order_id.tender_id.id >>> ' , rec.order_id.tender_id.id)
                quted = self.env['quted.items'].create({
                    'tender_id' : rec.order_id.tender_id.id,
                    'barcode': rec.product_id.barcode,
                    'product_id': rec.product_id.id,
                    'supplier': rec.manufacturer_id.name,
                    'tender_no': rec.order_id.tender_no,
                    # 'qty': self.calculate_quantuty(rec , rec.product_id.id),
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
            print('from get_quantu ' , i.quantity1)
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
