from odoo import models, fields


class SaleOrderInherited(models.Model):
    _inherit = 'sale.order'

    # crm_id = fields.Many2one('crm.lead')
    is_interpretation = fields.Boolean(string='Is Interpretation', related='opportunity_id.is_interpretation',
                                       readonly=True)

    payment_terms = fields.Selection(
        [('1', 'Advance Payment'), ('2', 'Partial Payment'), ('3', 'Progress Payments'), ('3', 'Progress Payments'), ('4', 'Prepaid'), ('5', 'Cash on Delivery'), ('6', 'Net 30') , ('7', 'Installments')], string="Payment Terms" , default = '1')

    delivery_type = fields.Selection([('0', 'Soft Copy'), ('1', 'Printed or E-copy')],
                                     string="Delivery Type")
    used_papers = fields.Integer(string="Used Papers")

    project_ids = fields.Many2many('project.project', compute_sudo=True)
    commitment_date = fields.Datetime( readonly='1',
                                      string="Detailed Timeline")
    related_project = fields.Many2one('project.project')
    project_status = fields.Text(compute='_get_project_stage')

    def _get_project_stage(self):
        for rec in self:
            rec.project_status = ""
            if rec.sudo().related_project:
                rec.project_status = rec.sudo().related_project.stage_id.name

    def write(self, vals):
        rec = super(SaleOrderInherited, self).write(vals)
        if 'state' in vals and vals['state'] == 'sale':
            self.opportunity_id.stage_id = self.env['crm.stage'].search([('is_won', '=', True)]).id

        return rec

    def create(self, vals):
        rec = super(SaleOrderInherited, self).create(vals)
        if (rec.opportunity_id):

            nego_stage = self.env['crm.stage'].search([('is_negotiation', '=', True)])

            if nego_stage:
                rec.opportunity_id.stage_id = nego_stage.id
        return rec

    def action_quotation_download(self):
        return self.env.ref('sale.action_report_saleorder').report_action(self)
