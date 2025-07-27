from odoo import models, api, fields

class SaleOrder(models.Model):
    _name = 'work.invite.nova'

    name = fields.Char('Name')
    owner_id = fields.Many2one('res.partner' , string='Owner')
    state = fields.Selection( [('late', 'Late'), ('plan', 'Planned') , ('progress', 'In Progress') , ('review', 'Under Review') , ('complete', 'Completed')],
       string="State")

    progress = fields.Integer('Progress')
    description =fields.Text('Description')
    date = fields.Date('Deliver Date')
    kpis = fields.Char('KPIS')
    files = fields.Many2many('ir.attachment' , string='Files')
    actions = fields.Many2one('work.action' , string='Actions')
    result = fields.Selection( [('field', 'Failed'), ('poor', 'Poor') , ('avg', 'AVG')],
       string="Result")

    Customer_satisfaction_level = fields.Integer('Customer satisfaction level')
    Increase_engagement_with_content = fields.Char('Increase engagement with content')
    compared_to = fields.Char('Compared to')
    valid = fields.Boolean()



class SaleOrder(models.Model):
    _name = 'work.action'

    name= fields.Char('Name')

