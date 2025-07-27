from odoo import models, fields ,api,_
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    vat = fields.Char(string='VAT', size=20, index=True)



    @api.constrains('x_studio_trade_license')
    def _check_unique_trade(self):
        print(1)
        for partner in self:
            if partner.x_studio_trade_license:
                existing_partner = self.env['res.partner'].search([('x_studio_trade_license', '=', partner.x_studio_trade_license), ('id', '!=', partner.id)])
                if existing_partner:
                    existing_partner_names = '\n'.join(existing_partner.mapped('name'))
                    raise ValidationError(_('VAT must be unique per partner! Existing partner(s): %s') % existing_partner_names)


    @api.constrains('vat')
    def _check_unique_vat(self):
        for partner in self:
            if partner.vat:
                existing_partner = self.env['res.partner'].search([('vat', '=', partner.vat), ('id', '!=', partner.id)])
                if existing_partner:
                    existing_partner_names = '\n'.join(existing_partner.mapped('name'))
                    raise ValidationError(_('VAT must be unique per partner! Existing partner(s): %s') % existing_partner_names)
