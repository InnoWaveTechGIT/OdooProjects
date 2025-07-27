from odoo import models, api, fields
from odoo.exceptions import ValidationError


class Journals(models.Model):
    _inherit = 'account.journal'

    partner_id = fields.Many2one('res.partner' , string='Branch' ,domain="[('is_company', '=', True)]" , required = True)
    branch = fields.Char('Branch ID' , required = True)


    @api.constrains('partner_id')
    def check_partner_fields(self):
        for record in self:
            empty_fields = []
            partner = record.partner_id
            if partner:
                if not partner.street:
                    empty_fields.append('Street')
                if not partner.street2:
                    empty_fields.append('Street2')
                if not partner.city:
                    empty_fields.append('City')
                if not partner.state_id:
                    empty_fields.append('State')
                if not partner.zip:
                    empty_fields.append('ZIP')
                if not partner.country_id:
                    empty_fields.append('Country')
                if not partner.vat:
                    empty_fields.append('VAT')

                if empty_fields:
                    error_message = "The following fields are required for the selected partner:\n%s" % ', '.join(empty_fields)
                    raise ValidationError(error_message)







