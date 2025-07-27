from odoo import api, fields, models


class DynamicWizard(models.TransientModel):
    _name = "dynamic.wizard"

    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')

    def print_dynamic_report(self):
        print("hhhhhhhhhh")

        data = {
            'data': {
                'title': 'New Title',
                'filters': [
                    {'Date From': self.date_from},
                    {'Date To': self.date_to},
                    {'category': 'Sales'},
                    {'Name': 'self'},
                    {'Status': 'new'},
                    {'customer': 'Omar'},

                ],
                'table_header': ['Product', 'Unit Price', 'Quantity', 'Total'],
                'table_body': [
                    ['Chair', '19.2', '3', '190 US']
                ],
            }
        }
        template = 'dynamic_reports.action_dynamic_report'
        action = self.env.ref(template).report_action(self, data=data)
        return action

