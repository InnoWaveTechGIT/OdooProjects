from odoo import models, api, fields
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class EmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    overtime_ability = fields.Boolean(string="Overtime ability")



