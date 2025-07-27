import datetime
import string
import re
import stdnum
from stdnum.eu.vat import check_vies
from stdnum.exceptions import InvalidComponent, InvalidChecksum, InvalidFormat
from stdnum.util import clean
from stdnum import luhn

import logging

from odoo import api, models, fields, tools, _
from odoo.tools import zeep
from odoo.tools.misc import ustr
from odoo.exceptions import ValidationError



_ref_vat = {
    'al': 'ALJ91402501L',
    'ar': _('AR200-5536168-2 or 20055361682'),
    'at': 'ATU12345675',
    'au': '83 914 571 673',
    'be': 'BE0477472701',
    'bg': 'BG1234567892',
    'br': _('either 11 digits for CPF or 14 digits for CNPJ'),
    'ch': _('CHE-123.456.788 TVA or CHE-123.456.788 MWST or CHE-123.456.788 IVA'),  # Swiss by Yannick Vaucher @ Camptocamp
    'cl': 'CL76086428-5',
    'co': _('CO213123432-1 or CO213.123.432-1'),
    'cy': 'CY10259033P',
    'cz': 'CZ12345679',
    'de': _('DE123456788 or 12/345/67890'),
    'dk': 'DK12345674',
    'do': _('DO1-01-85004-3 or 101850043'),
    'ec': _('1792060346001 or 1792060346'),
    'ee': 'EE123456780',
    'es': 'ESA12345674',
    'fi': 'FI12345671',
    'fr': 'FR23334175221',
    'gb': _('GB123456782 or XI123456782'),
    'gr': 'EL123456783',
    'hu': _('HU12345676 or 12345678-1-11 or 8071592153'),
    'hr': 'HR01234567896',  # Croatia, contributed by Milan Tribuson
    'ie': 'IE1234567FA',
    'in': "12AAAAA1234AAZA",
    'is': 'IS062199',
    'it': 'IT12345670017',
    'lt': 'LT123456715',
    'lu': 'LU12345613',
    'lv': 'LV41234567891',
    'mc': 'FR53000004605',
    'mt': 'MT12345634',
    'mx': _('MXGODE561231GR8 or GODE561231GR8'),
    'nl': 'NL123456782B90',
    'no': 'NO123456785',
    'nz': _('49-098-576 or 49098576'),
    'pe': _('10XXXXXXXXY or 20XXXXXXXXY or 15XXXXXXXXY or 16XXXXXXXXY or 17XXXXXXXXY'),
    'ph': '123-456-789-123',
    'pl': 'PL1234567883',
    'pt': 'PT123456789',
    'ro': 'RO1234567897 or 8001011234567 or 9000123456789',
    'rs': 'RS101134702',
    'ru': 'RU123456789047',
    'se': 'SE123456789701',
    'si': 'SI12345679',
    'sk': 'SK2022749619',
    'sm': 'SM24165',
    'tr': _('TR1234567890 (VERGINO) or TR17291716060 (TCKIMLIKNO)'),  # Levent Karakas @ Eska Yazilim A.S.
    've': 'V-12345678-1, V123456781, V-12.345.678-1',
    'xi': 'XI123456782',
    'sa': _('310175397400003 [Fifteen digits, first and last digits should be "3"]')
}




class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('vat', 'country_id')
    def check_vat(self):
        pass
        # The context key 'no_vat_validation' allows you to store/set a VAT number without doing validations.
        # This is for API pushes from external platforms where you have no control over VAT numbers.
        # if self.env.context.get('no_vat_validation'):
        #     return
        #
        # for partner in self:
        #     # Skip checks when only one character is used. Some users like to put '/' or other as VAT to differentiate between
        #     # A partner for which they didn't input VAT, and the one not subject to VAT
        #     if not partner.vat or len(partner.vat) == 1:
        #         continue
        #     country = partner.commercial_partner_id.country_id
        #     if self._run_vat_test(partner.vat, country, partner.is_company) is False:
        #         partner_label = _("partner [%s]", partner.name)
        #         msg = partner._build_vat_error_message(country and country.code.lower() or None, partner.vat, partner_label)
        #         raise ValidationError(msg)


    @api.model
    def _build_vat_error_message(self, country_code, wrong_vat, record_label):
        # OVERRIDE account
        print('record_label  >>>>>>> ' , record_label)
        # if self.env.context.get('company_id'):
        #     company = self.env['res.company'].browse(self.env.context['company_id'])
        # else:
        #     company = self.env.company
        #
        # vat_label = _("VAT")
        # if country_code and company.country_id and country_code == company.country_id.code.lower() and company.country_id.vat_label:
        #     vat_label = company.country_id.vat_label

    #     expected_format = _ref_vat.get(country_code, "'CC##' (CC=Country Code, ##=VAT Number)")
    #
    #     # Catch use case where the record label is about the public user (name: False)
    #     if 'False' not in record_label:
    #         return '\n' + _(
    #             'The %(vat_label)s number [%(wrong_vat)s] for %(record_label)s does not seem to be valid. \nNote: the expected format is %(expected_format)s',
    #             vat_label=vat_label,
    #             wrong_vat=wrong_vat,
    #             record_label=record_label,
    #             expected_format=expected_format,
    #         )
    #     else:
    #         return '\n' + _(
    #             'The %(vat_label)s number [%(wrong_vat)s] does not seem to be valid. \nNote: the expected format is %(expected_format)s',
    #             vat_label=vat_label,
    #             wrong_vat=wrong_vat,
    #             expected_format=expected_format,
    #         )
    #
    #
    # __check_vat_al_re = re.compile(r'^[JKLM][0-9]{8}[A-Z]$')
