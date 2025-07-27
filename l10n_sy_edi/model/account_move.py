from odoo import models, api, fields
from odoo.exceptions import UserError
import qrcode
from io import BytesIO
import base64
from datetime import datetime
import requests
import uuid
import math

class Invoice(models.Model):
    _inherit = 'account.move'

    def generate_guid(self):
        return str(uuid.uuid4())


    print_counter = fields.Integer()
    random_number = fields.Char('Random Number')
    register_date = fields.Char('Register Date')
    confirmation_date= fields.Date('Confirmation Date')
    confirmation_date1 = fields.Datetime('Confirmation Date')
    e_invoice_type = fields.Selection(
       [('draft', 'Draft'), ('to_send', 'To Send') , ('sent', 'Sent') , ('valid', 'Valid') , ('rejected', 'Rejected')],
       string="Electronic Invoice" ,default='draft' , tracking=True)
    qr_code_image = fields.Binary(string='QR Code Image', compute='generate_qr_code' , store=True)
    qr_code_image1 = fields.Binary(string='QR Code Image')
    qr_text = fields.Char(string='QR Code', compute='generate_qr_code')
    inv_code = fields.Char('Code' , compute ='get_inv_code')
    guid = fields.Char(string='GUID', default=generate_guid, copy=False , store=True)
    e_inv_type = fields.Char(compute='get_e_inv_type')
    discount_amount = fields.Float('Discount Amount' , compute='get_discount_amount')

    @api.depends('invoice_line_ids')
    def get_discount_amount(self):
        discount =0.0
        for rec in self:
            for line in rec.invoice_line_ids:
                discount += (line.quantity * line.price_unit) * line.discount / 100

            rec.discount_amount = discount

    @api.depends('e_invoice_type')
    def get_e_inv_type(self):
        for rec in self:
            e_type = self.env['ir.config_parameter'].search([('key' , '=' , 'l10n_sy_edi.e_invoice_type')])
            rec.e_inv_type = e_type.value
    @api.depends('confirmation_date1' , 'amount_untaxed' , 'currency_id' , 'guid')
    def get_inv_code(self):
        for rec in self:
            e_type = self.env['ir.config_parameter'].search([('key' , '=' , 'l10n_sy_edi.e_invoice_type')])
            if e_type.value == 'test' :
                facility = self.env['ir.config_parameter'].search([('key' , '=' , 'l10n_sy_edi.e_invoice_facility_test')])
            elif e_type.value == 'prod':
                facility = self.env['ir.config_parameter'].search([('key' , '=' , 'l10n_sy_edi.e_invoice_facility')])
            else :
                facility = False

            e_invoice_tax_id = self.env['ir.config_parameter'].search([('key' , '=' , 'l10n_sy_edi.e_invoice_tax_id')])
            rec.inv_code ='#'+ str(e_invoice_tax_id.value) +'_' +str(facility.value)+ '#' +str(rec.confirmation_date1)+'_' + str(rec.amount_untaxed)+'_' + str(rec.currency_id.name) +'_' + str(rec.user_id.name) +'#' + str(rec.guid) +'#'


    def process_now_fun_cron(self):
        payload = {
              "billValue": self.amount_untaxed,
              "billNumber": self.name,
              "code": self.guid,
              "currency": self.currency_id.name,
              "exProgram": "AradosERP",
              "date": str(self.confirmation_date)
            }
        e_type = self.env['ir.config_parameter'].search([('key' , '=' , 'l10n_sy_edi.e_invoice_type')])
        if e_type.value == 'test' :
            url = 'https://185.216.133.4/liveapi/api/Bill/AddFullBill'
            token = self.env['ir.config_parameter'].search([('key' , '=' , 'l10n_sy_edi.e_invoice_token_test')])
            headers = {
                'Authorization': token.value,
            }
            response = requests.post(url , headers=headers, json=payload, verify=False)
            if response.status_code == 200:
                data = response.json()
                self.e_invoice_type  = 'valid'
                self.random_number = data['data']['randomNumber']
                print("data['data'] >>> " , data['data'])
                self.register_date = data['data']['billDate']

        if e_type.value == 'prod' :
            raise UserError("We can't do the process on Live right now")
            # url = 'https://185.216.133.4/liveapi/api/Bill/AddFullBill'
            # token = self.env['ir.config_parameter'].search([('key' , '=' , 'l10n_sy_edi.e_invoice_token')])
            # headers = {
            #     'Authorization': token.value,
            # }
            # response = requests.post(url , headers=headers, json=payload, verify=False)
            # if response.status_code == 200:
            #     data = response.json()
            #     self.e_invoice_type  = 'valid'
            #     self.random_number = data['data']['randomNumber']
            # else:
            #     self.e_invoice_type  = 'rejected'

    def process_now_fun(self):
        self.e_invoice_type  = 'sent'
        payload = {
              "billValue": self.amount_untaxed,
              "billNumber": self.name,
              "code": self.guid,
              "currency": self.currency_id.name,
              "exProgram": "AradosERP",
              "date": str(self.confirmation_date)
            }
        e_type = self.env['ir.config_parameter'].search([('key' , '=' , 'l10n_sy_edi.e_invoice_type')])
        if e_type.value == 'test' :
            url = 'https://185.216.133.4/liveapi/api/Bill/AddFullBill'
            token = self.env['ir.config_parameter'].search([('key' , '=' , 'l10n_sy_edi.e_invoice_token_test')])
            headers = {
                'Authorization': token.value,
            }
            response = requests.post(url , headers=headers, json=payload, verify=False)
            if response.status_code == 200:
                data = response.json()
                self.e_invoice_type  = 'valid'
                self.random_number = data['data']['randomNumber']
                print("data['data'] >>> " , data['data'])
                self.register_date = data['data']['billDate']
            else:
                self.e_invoice_type  = 'rejected'
        if e_type.value == 'prod' :
            raise UserError("We can't do the process on Live right now")
            # url = 'https://185.216.133.4/liveapi/api/Bill/AddFullBill'
            # token = self.env['ir.config_parameter'].search([('key' , '=' , 'l10n_sy_edi.e_invoice_token')])
            # headers = {
            #     'Authorization': token.value,
            # }
            # response = requests.post(url , headers=headers, json=payload, verify=False)
            # if response.status_code == 200:
            #     data = response.json()
            #     self.e_invoice_type  = 'valid'
            #     self.random_number = data['data']['randomNumber']
            # else:
            #     self.e_invoice_type  = 'rejected'
    def action_post(self):
        # inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        for rec in self:
            if rec.partner_id.vat and rec.partner_id.street and rec.partner_id.street2 and rec.partner_id.city and rec.partner_id.state_id and rec.partner_id.zip and rec.partner_id.country_id and rec.move_type == 'out_invoice':
                pass
            else:
                if rec.move_type == 'out_invoice':
                    raise UserError("Please add the required fields in customer details")
        res = super(Invoice, self).action_post()

        self.e_invoice_type = 'to_send'
        self.confirmation_date = datetime.today().date().strftime('%Y-%m-%d')
        self.confirmation_date1 = datetime.today()
        return res

    @api.depends('name' , 'partner_id')
    def generate_qr_code(self):
        for invoice in self:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(invoice.inv_code)  # Add invoice number or any other data you want in the QR code
            qr.make(fit=True)

            qr_code_img = qr.make_image(fill_color="black", back_color="white")
            img_buffer = BytesIO()
            qr_code_img.save(img_buffer)
            qr_code_img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

            # Update the invoice record with the QR code
            invoice.write({'qr_code_image': qr_code_img_base64,
                           'qr_text' : False})



    def print_e_invoice(self):
        for rec in self:
            rec.print_counter += 1
            return self.env.ref('l10n_sy_edi.action_report_e_invoice_template').report_action(self)
    # @api.constrains('random_number')
    # def _check_tax_id_length(self):
    #     for record in self:
    #         if record.random_number and len(record.random_number) != 9:
    #             raise UserError("Random Number must be 9 digits !")


    def button_cancel(self):
        for rec in self:

            if rec.e_invoice_type  != 'draft':
                raise UserError("You can't change the status of this invoice")
            else:
                super().button_cancel()
    def button_draft(self):
        for rec in self:

            if rec.e_invoice_type  != 'draft':
                raise UserError("You can't change the status of this invoice")
            else:
                super().button_draft()








class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    price_difference = fields.Float(compute='_compute_price_difference', string='Price Difference', store=True)
    discount_amount = fields.Float(string='Discount Amount', compute='_compute_discount_amount', store=True)

    @api.depends('price_total', 'price_subtotal')
    def _compute_price_difference(self):
        for line in self:

            line.price_difference = round(line.price_total - line.price_subtotal, line.currency_id.decimal_places)


    @api.depends('price_unit', 'quantity', 'discount')
    def _compute_discount_amount(self):
        for line in self:
            line.discount_amount = (line.price_unit * line.quantity * line.discount) / 100
