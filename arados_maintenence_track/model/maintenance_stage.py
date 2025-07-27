from odoo import api, fields, models
from odoo.exceptions import ValidationError

class MaintenanceStage(models.Model):
    _inherit = 'maintenance.stage'

    is_repaired = fields.Boolean(string='Is Repaired')

    @api.constrains('is_repaired')
    def _check_unique_is_repaired(self):
        for record in self:
            if record.is_repaired:
                existing_record = self.env['maintenance.stage'].search([('is_repaired', '=', True), ('id', '!=', record.id)], limit=1)
                if existing_record:
                    raise ValidationError("There is already a record with 'Is Repaired' set to True. Only one record can have this flag set at a time.")
