from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class productproductInherit(models.Model):
    _inherit = 'stock.move.line'

    start_warranty = fields.Date('Warranty Start' )
    end_warranty = fields.Date('Warranty End')
    not_hide_filed = fields.Boolean(related='move_id.product_id.product_tmpl_id.warranty')


    @api.constrains('end_warranty', 'start_warranty')
    def _check_warranty_dates1235(self):
        for record in self:
            if record.start_warranty and record.end_warranty:
                if record.end_warranty < record.start_warranty:
                    raise UserError('End Warranty Date cannot be earlier than Start Warranty Date.')

    @api.constrains('move_id')
    def _check_product_id_unique(self):
        for record in self:
            if record.move_id:
                if record.move_id.product_id.product_tmpl_id.warranty:
                    record.start_warranty = record.move_id.picking_id.scheduled_date
                    given_date_str = str(record.move_id.picking_id.scheduled_date)
                    print("given_date_str >>> " , given_date_str)
                    # Extracting only the date part from the datetime string
                    given_date_str = given_date_str.split()[0]
                    if given_date_str != 'False':
                        given_date = datetime.strptime(given_date_str, '%Y-%m-%d')

                        # Add years to the given date
                        years = record.move_id.product_id.product_tmpl_id.warranty_date
                        new_date = given_date + timedelta(days=365 * years)

                        # Convert the new date back to a string in the same format
                        record.end_warranty = new_date.strftime('%Y-%m-%d')
