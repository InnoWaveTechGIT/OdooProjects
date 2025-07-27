from odoo import models, fields, api


class MyWizard(models.TransientModel):
    _name = 'supervisor.wizard'
    _description = 'My Wizard'

    user_ids = fields.Many2one('res.users', string='Student')

    @api.onchange('user_ids')
    def _get_courses(self):

        session_ids = self.env['session_status'].search([('user_id', '=', self.user_ids.id)])
        if session_ids:
            course_ids = session_ids.mapped('course_name')
            domain = [('id', 'in', course_ids.ids)]
        else:
            domain = []
        return {'domain': {'course_ids': domain}}

    course_ids = fields.Many2many('courses', string='Courses', domain=_get_courses)
    server_id = fields.Many2one('ir.actions.server', string="Supervisor Report")

    def button_show_tree_view(self):
        return self.env['dynamic.report.configure'].create_dynamic_pdf_report(self.server_id.dynamic_report_id.id, self.user_ids, self.course_ids)

