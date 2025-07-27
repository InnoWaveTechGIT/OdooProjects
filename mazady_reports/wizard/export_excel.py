from odoo import models, fields, api ,_
from odoo.exceptions import ValidationError
import os
import base64
from io import BytesIO
import xlsxwriter


class ExcelImportWizard(models.TransientModel):
    _name = 'excel.export.wizard'
    _description = 'Excel Export Wizard'

    date_from = fields.Date(string='From', required=True)
    date_to = fields.Date(string='To', required=True)
    loyality_id = fields.Many2one('loyalty.card')
    partner_id = fields.Many2one('res.partner')

    @api.constrains('date_from', 'date_to')
    def _check_date_order(self):
        for record in self:
            if record.date_to < record.date_from:
                raise ValidationError("The 'To' date must be after the 'From' date.")


    def export_excel_data_from_contact(self):
        for record in self:
            wallet = 0
            if record.partner_id:
                wallet = self.env['loyalty.card'].search([('partner_id' , '=' , record.partner_id.id)] , limit=1)
            else:
                raise ValidationError('There is no partner to search.')
            if wallet:
                excel_buffer = BytesIO()
                workbook = xlsxwriter.Workbook(excel_buffer, {})  # Specify the path to save the Excel file
                worksheet = workbook.add_worksheet()

                # Add headers
                header1 = ['From','To','Partner','Balance','Block Balance',
                           ]
                row = 1
                header_format = workbook.add_format({
                                                        'bold': True,
                                                        'bg_color': '#FFA07A',  # Light Salmon background color (you can change this)
                                                        'font_color': '#000000',  # Black font color
                                                        'border': 1
                                                    })

                header_format1 = workbook.add_format({
                                                        'bold': True,
                                                        'bg_color': '#87CEEB',  # Light Salmon background color (you can change this)
                                                        'font_color': '#000000',  # Black font color
                                                        'border': 1
                                                    })
                merged=0
                worksheet.set_column(0, 6, 15)
                worksheet.set_column(0, 7, 15)
                worksheet.set_column(0, 8, 15)
                worksheet.set_column(0, 9, 15)
                worksheet.set_column(0, 10, 15)
                worksheet.set_column(0, 11, 15)
                for col, header in enumerate(header1):
                    # if header == 'Partner':
                    #     # Merge the cells for "Partner" spanning two columns
                    #     worksheet.merge_range(0, col+6, 0, col+6 + 1, header, header_format)
                    #     merged=1
                    # else:
                    #     if merged:
                    #         worksheet.write(0, col+7, header, header_format)
                    #     else:
                    worksheet.write(0, col+6, header, header_format)

                    worksheet.write(row, 6, str(record.date_from), header_format1)
                    worksheet.write(row, 7, str(record.date_to), header_format1)
                    worksheet.write(row, 8, record.partner_id.name, header_format1)
                    worksheet.write(row, 9, wallet.points_display, header_format1)
                    worksheet.write(row, 10, wallet.blocked_balance, header_format1)
                header2 = ['Description','REF.','Date','Issued','Used','Withdraw Request',
                           ]
                for col, header in enumerate(header2):
                    worksheet.write(2, col+6, header ,header_format)
                row = 3
                for line in wallet.history_ids:
                    if record.date_from <= line.create_date.date() <= record.date_to:
                        worksheet.write(row, 6, line.description, header_format1)
                        worksheet.write(row, 7, line.order_id, header_format1)
                        worksheet.write(row, 8, str(line.create_date.date()), header_format1)
                        worksheet.write(row, 9, line.issued, header_format1)
                        worksheet.write(row, 10, line.used, header_format1)
                        worksheet.write(row, 11, line.withdraw_request, header_format1)

                        row += 1
                workbook.close()
                excel_buffer.seek(0)
                encoded_data = base64.b64encode(excel_buffer.read())

                attach_vals = {
                    'name': f'{self.loyality_id.code}.xlsx',
                    'datas': encoded_data,
                    'res_model': 'loyalty.card',  # Update this with your model name
                    'res_id': self.loyality_id.id,  # Update this with the ID of your record
                }

                attachment = self.env['ir.attachment'].create(attach_vals)
                excel_buffer.close()

                wallet.excel_file = attachment.datas

                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + '/web/binary/loyalty_download_generated_excel?id=%s' % (wallet.id)
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'self',
                }
            else:
                raise ValidationError('There is no Wallet for this partner')
    def export_excel_data(self):
        for record in self:
            excel_buffer = BytesIO()
            workbook = xlsxwriter.Workbook(excel_buffer, {})  # Specify the path to save the Excel file
            worksheet = workbook.add_worksheet()

            # Add headers
            header1 = ['From','To','Partner','Balance','Block Balance',
                       ]
            row = 1
            header_format = workbook.add_format({
                                                    'bold': True,
                                                    'bg_color': '#FFA07A',  # Light Salmon background color (you can change this)
                                                    'font_color': '#000000',  # Black font color
                                                    'border': 1
                                                })

            header_format1 = workbook.add_format({
                                                    'bold': True,
                                                    'bg_color': '#87CEEB',  # Light Salmon background color (you can change this)
                                                    'font_color': '#000000',  # Black font color
                                                    'border': 1
                                                })
            merged=0
            worksheet.set_column(0, 6, 15)
            worksheet.set_column(0, 7, 15)
            worksheet.set_column(0, 8, 15)
            worksheet.set_column(0, 9, 15)
            worksheet.set_column(0, 10, 15)
            worksheet.set_column(0, 11, 15)
            for col, header in enumerate(header1):
                # if header == 'Partner':
                #     # Merge the cells for "Partner" spanning two columns
                #     worksheet.merge_range(0, col+6, 0, col+6 + 1, header, header_format)
                #     merged=1
                # else:
                #     if merged:
                #         worksheet.write(0, col+7, header, header_format)
                #     else:
                worksheet.write(0, col+6, header, header_format)

                worksheet.write(row, 6, str(record.date_from), header_format1)
                worksheet.write(row, 7, str(record.date_to), header_format1)
                worksheet.write(row, 8, record.loyality_id.partner_id.name, header_format1)
                worksheet.write(row, 9, record.loyality_id.points_display, header_format1)
                worksheet.write(row, 10, record.loyality_id.blocked_balance, header_format1)
            header2 = ['Description','REF.','Date','Issued','Used','Withdraw Request',
                       ]
            for col, header in enumerate(header2):
                worksheet.write(2, col+6, header ,header_format)
            row = 3
            for line in record.loyality_id.history_ids:
                if record.date_from <= line.create_date.date() <= record.date_to:
                    worksheet.write(row, 6, line.description, header_format1)
                    worksheet.write(row, 7, line.order_id, header_format1)
                    worksheet.write(row, 8, str(line.create_date.date()), header_format1)
                    worksheet.write(row, 9, line.issued, header_format1)
                    worksheet.write(row, 10, line.used, header_format1)
                    worksheet.write(row, 11, line.withdraw_request, header_format1)

                    row += 1
            workbook.close()
            excel_buffer.seek(0)
            encoded_data = base64.b64encode(excel_buffer.read())

            attach_vals = {
                'name': f'{self.loyality_id.code}.xlsx',
                'datas': encoded_data,
                'res_model': 'loyalty.card',  # Update this with your model name
                'res_id': self.loyality_id.id,  # Update this with the ID of your record
            }

            attachment = self.env['ir.attachment'].create(attach_vals)
            excel_buffer.close()

            self.loyality_id.excel_file = attachment.datas

            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/web/binary/loyalty_download_generated_excel?id=%s' % (self.loyality_id.id)
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'self',
            }
