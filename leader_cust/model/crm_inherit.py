from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    name = fields.Char(string='Custom Counter', readonly=True, default='New')



    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('crm.lead.counter') or 'New'
        return super(CrmLead, self).create(vals)
