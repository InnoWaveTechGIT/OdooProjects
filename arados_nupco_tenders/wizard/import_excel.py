from odoo import models, fields, api
import base64
import xlrd
from odoo.exceptions import UserError

class ExcelImportWizard(models.TransientModel):
    _name = 'excel.import.wizard'
    _description = 'Excel Import Wizard'

    excel_file = fields.Binary(string='Excel File', required=True)
    tender_id = fields.Many2one('tenders')
    def import_excel_data(self):
        tender_obj = self.env['nubco.tender']
        uom_obj = self.env['uom.uom']
        currency_obj = self.env['res.currency']
        vat_obj = self.env['account.tax']
        product_obj = self.env['product.product']
        manufacturer_obj = self.env['res.partner']
        country_obj = self.env['res.country']
        try:
            for wizard in self:
                data = base64.b64decode(wizard.excel_file)
                workbook = xlrd.open_workbook(file_contents=data)
                sheet = workbook.sheet_by_index(0)  # Assuming data is in the first sheet

                for row in range(1, sheet.nrows):  # Start from row 1 to skip headers
                    row_values = sheet.row_values(row)
                    print(row_values[11])
                    # Create or update records based on the Excel data
                    tender_obj.create({
                    'tender_id': self.tender_id.id,
                    'nubco_serial': row_values[0],
                    'nubco_material': row_values[1],
                    'nubco_material_des': row_values[2],
                    'medical_group': row_values[3],
                    'quantity1': row_values[4],
                    'uom_id': uom_obj.search([('name', '=', row_values[5])], limit=1).id,
                    'price': row_values[6],
                    'currency_id': currency_obj.search([('name', '=', row_values[7])], limit=1).id,
                    'vat_id': vat_obj.search([('name', '=', row_values[8])], limit=1).id,
                    'product_id': product_obj.search([('name', '=', row_values[9])], limit=1).id,
                    'manufacturer_id': manufacturer_obj.search([('name', '=', row_values[10])], limit=1).id,
                    'manufacturing_country': country_obj.search([('name', '=', row_values[11])], limit=1).id,
                    'product_packaging': row_values[12],
                    'mdma_code' : row_values[13],
                    'MDMA_exp' : row_values[14],
                    'SFGa_code' : row_values[15],
                    'sheif_life' : row_values[16],
                    'moq': row_values[17],
                    'volume': row_values[18],
                    'manufacture_process_local': row_values[19],
                    'temp': row_values[20],
                    'first_lead': row_values[21],
                    'lead_time': row_values[22],
                    'max_num_of_shipp': row_values[23],
                })

        except Exception as e:
            raise UserError("The file is invalid. Please check the file format and contents.")

        return {'type': 'ir.actions.act_window_close'}
