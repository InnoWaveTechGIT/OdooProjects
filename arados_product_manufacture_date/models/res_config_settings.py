from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_manufacturing_date = fields.Boolean(string='Manufacturing Date',config_parameter="arados_product_manufacture_date.allow_manufacturing_date", default=False)

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #
    #     params = self.env['ir.config_parameter'].sudo()
    #
    #     res.update(
    #         allow_manufacturing_date=params.get_param('arados_product_manufacture_date.allow_manufacturing_date', default=False),
    #     )
    #     return res
    #
    # def set_values(self):
    #     super(ResConfigSettings, self).set_values()
    #     IrConfigParameter = self.env['ir.config_parameter'].sudo()
    #     IrConfigParameter.set_param("arados_product_manufacture_date.allow_manufacturing_date", self.allow_manufacturing_date)



