from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'


    @api.model
    def create(self, vals):
        # Check if is_company is True and parent_id is not set
        if vals.get('company_id')== False or vals.get('company_id')== None:
            raise ValidationError("The 'Company' field is required for Individuals.")

        return super(ResPartner, self).create(vals)

    def write(self, vals):
        # Check if is_company is True and parent_id is not set
        for record in self:
            if vals.get('company_id')==False:
                raise ValidationError("The 'Company' field is required for companies.")
            if self.company_id == False :
                raise ValidationError("The 'Company' field is required for companies.")
        return super(ResPartner, self).write(vals)
