from odoo import models, api, fields
from odoo.exceptions import UserError
import requests


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    e_invoice_type = fields.Selection(
       [('test', 'Testing Mode'), ('prod', 'Production Mode')],
       string="Connection Mode")

    e_invoice_api_url = fields.Char('API URL')
    e_invoice_user_name = fields.Char('Client UserName')
    e_invoice_secret = fields.Char('User Secret')
    e_invoice_tax_id = fields.Char('Tax ID')
    e_invoice_token = fields.Char('Token')
    e_invoice_token_test = fields.Char('Token')
    e_invoice_facility = fields.Char('Facility')
    e_invoice_facility_test = fields.Char('Facility')
    e_invoice_sale_tax = fields.Many2one('account.tax',
        string="Sale Tax" ,related='company_id.account_sale_tax_id',
        readonly=False,
        check_company=True,)
    e_invoice_purchase_tax = fields.Many2one('account.tax',
        string="Purchase Tax",
                                             related='company_id.account_purchase_tax_id',
        readonly=False,
        check_company=True,)



    def connection_to_server_e_invoice(self):

        if self.e_invoice_type == 'test':
            if self.company_id.vat != self.e_invoice_tax_id:
                raise UserError("Tax ID in Settings should be similar with tax id in active company")
            payload = {
                "userName": self.e_invoice_user_name,
                "passWord": self.e_invoice_secret,
                "taxNumber": self.e_invoice_tax_id
            }
            try:
                response = requests.post(self.e_invoice_api_url, json=payload, verify=False)  # Set verify=False to ignore SSL certificate verification
                if response.status_code == 200:
                    data = response.json()
                    self.e_invoice_token_test = data['data']['token']
                    data_saved = self.env['ir.config_parameter'].search([('key' , '=' ,'l10n_sy_edi.e_invoice_token_test')])
                    data_saved.sudo().unlink()
                    self.env['ir.config_parameter'].create({
                        'key' : 'l10n_sy_edi.e_invoice_token_test',
                        'value' : data['data']['token']
                    })
                    data_saved = self.env['ir.config_parameter'].search([('key' , '=' ,'l10n_sy_edi.e_invoice_facility_test')])
                    data_saved.sudo().unlink()
                    self.env['ir.config_parameter'].create({
                        'key' : 'l10n_sy_edi.e_invoice_facility_test',
                        'value' : data['data']['facilityName']
                    })
                    return {
                        'type' :'ir.actions.client',
                        'tag' : 'display_notification',
                        'params' : {
                            'title' : 'Test Connection' ,
                            'message' : 'Successfully Connected'
                        }
                    }
                else:
                    raise UserError(f"Request failed with status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                raise UserError(f"An error occurred: {e}")

        elif self.e_invoice_type == 'prod':
            raise UserError("We can't do the process on Live right now")

        else:
            raise UserError("Please enter the type in Production or Test ")


    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('l10n_sy_edi.e_invoice_type' , self.e_invoice_type)
        self.env['ir.config_parameter'].set_param('l10n_sy_edi.e_invoice_api_url' , self.e_invoice_api_url)
        self.env['ir.config_parameter'].set_param('l10n_sy_edi.e_invoice_user_name' , self.e_invoice_user_name)
        self.env['ir.config_parameter'].set_param('l10n_sy_edi.e_invoice_secret' , self.e_invoice_secret)
        self.env['ir.config_parameter'].set_param('l10n_sy_edi.e_invoice_tax_id' , self.e_invoice_tax_id)
        self.env['ir.config_parameter'].set_param('l10n_sy_edi.e_invoice_token' , self.e_invoice_token)
        self.env['ir.config_parameter'].set_param('l10n_sy_edi.e_invoice_token_test' , self.e_invoice_token_test)
        self.env['ir.config_parameter'].set_param('l10n_sy_edi.e_invoice_facility' , self.e_invoice_facility)
        # e_invoice_sale_tax_val = self.env['ir.config_parameter'].set_param('l10n_sy_edi.e_invoice_sale_tax' , self.e_invoice_sale_tax.id)
        # self.env['ir.config_parameter'].set_param('l10n_sy_edi.e_invoice_purchase_tax' , self.e_invoice_purchase_tax.id)
        # print('e_invoice_sale_tax_val >>>>> ' , e_invoice_sale_tax_val )
        # print('self.e_invoice_purchase_tax >>>>>> ' , self.e_invoice_purchase_tax)

        return  res


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        records = self.env['ir.config_parameter'].sudo()
        e_invoice_type = records.get_param('l10n_sy_edi.e_invoice_type')
        e_invoice_api_url = records.get_param('l10n_sy_edi.e_invoice_api_url')
        e_invoice_user_name = records.get_param('l10n_sy_edi.e_invoice_user_name')
        e_invoice_secret = records.get_param('l10n_sy_edi.e_invoice_secret')
        e_invoice_tax_id = records.get_param('l10n_sy_edi.e_invoice_tax_id')
        e_invoice_token = records.get_param('l10n_sy_edi.e_invoice_token')
        e_invoice_token_test = records.get_param('l10n_sy_edi.e_invoice_token_test')
        e_invoice_facility = records.get_param('l10n_sy_edi.e_invoice_facility')
        # e_invoice_sale_tax = records.get_param('l10n_sy_edi.e_invoice_sale_tax')
        # print('e_invoice_sale_tax >>>> ', e_invoice_sale_tax)
        # e_invoice_purchase_tax = records.get_param('l10n_sy_edi.e_invoice_purchase_tax')
        res.update(
            e_invoice_type = e_invoice_type
        )
        res.update(
            e_invoice_api_url = e_invoice_api_url
        )
        res.update(
            e_invoice_user_name = e_invoice_user_name
        )
        res.update(
            e_invoice_secret = e_invoice_secret
        )
        res.update(
            e_invoice_tax_id = e_invoice_tax_id
        )
        res.update(
            e_invoice_token = e_invoice_token
        )
        res.update(
            e_invoice_token_test = e_invoice_token_test
        )

        res.update(
            e_invoice_facility = e_invoice_facility
        )
        # res.update(
        #     e_invoice_sale_tax = e_invoice_sale_tax
        # )
        # res.update(
        #     e_invoice_purchase_tax = e_invoice_purchase_tax
        # )

        return res

    @api.constrains('e_invoice_tax_id')
    def _check_tax_id_length(self):
        for record in self:
            if record.e_invoice_tax_id and len(record.e_invoice_tax_id) != 12:
                raise UserError("Tax ID must be 12 digits !")

