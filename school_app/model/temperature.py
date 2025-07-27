from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import datetime


class Temperature(models.Model):
    _name = 'school.temperature'
    

    temperature = fields.Char()
    time = fields.Datetime('Time')
    unit = fields.Selection(
        [('°C', _('Celsius')), ('°F', _('Fahrenheit'))], string="Unit")
    date = fields.Date('Date', compute='_compute_date', store=True)

    @api.depends('time')
    def _compute_date(self):
        for record in self:
            if record.time:
                record.date = record.time.date()
            else:
                record.date = False