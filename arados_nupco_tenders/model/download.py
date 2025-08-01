from odoo import http
from odoo.http import request
import base64

class ExcelDownloadController(http.Controller):

    @http.route('/web/binary/download_generated_excel', type='http', auth="user")
    def download_generated_excel(self, **kw):
        print('kw >>>> ' , kw)
        Attachment = request.env['ir.attachment']
        record_id = kw.get('id')
        record = request.env['tenders'].browse(int(record_id))  # Replace 'your.model' with your actual model name
        print('record >>>>>>> ' , record)
        if record and record.excel_file:
            return request.make_response(
                base64.b64decode(record.excel_file),
                headers=[('Content-Type', 'application/vnd.ms-excel'), ('Content-Disposition', f'attachment; filename=generated_excel.xlsx')]
            )
        return request.not_found()
