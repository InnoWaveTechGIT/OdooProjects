from odoo import models, fields, api


class AccountMoveInherited(models.Model):
    _inherit = 'account.move'

    due_date = fields.Date(string='Due Date')
    delivery_date = fields.Datetime()
    customer_notes = fields.Html(string='Customer Notes')
    order_id = fields.Many2one('sale.order' ,compute="_compute_origin_so")
    payment_terms = fields.Selection(related='order_id.payment_terms',string="Payment Terms" )
    invisible_project = fields.Boolean('invisible' , compute="_compute_invisible_project")


    def action_create_project(self):
        for rec in self:
            print(1212)
            print(rec.order_id)
            print(rec.order_id.opportunity_id)
            if rec.order_id.opportunity_id:
                print(1254)
                crm = rec.order_id.opportunity_id
                project = self.env['project.project'].create({
                    'name' : crm.name,
                    'service_industry' : crm.service_industry,
                    'service_type' : crm.service_type,
                    'delivery_type' : crm.delivery_type,
                    'priority_work' : crm.priority_work,
                    'detailed_timeline' : crm.detailed_timeline,
                    # 'planned_timeline' : crm.planned_timeline

                })

                for i in rec.order_id.order_line:
                    product_id = self.env['product.product'].search([('product_tmpl_id' , '=' , i.product_id.id)] , limit=1)
                    print('product_id >>>>>>>> ' ,product_id)
                    task = self.env['project.task'].create({
                        'name' : project.name,
                        'project_id' : project.id,
                        'date_deadline' : i.order_id.opportunity_id.deadline,
                        'source_attachment_ids' : i.source_attachment_ids,
                        'product_id':product_id.id,
                        'source_language' : i.source_language.id,
                        'target_language' :i.target_language.id ,

                    })


    def _compute_invisible_project(self):
        for rec in self:
            if rec.payment_terms in ['1' , '2']:
                if rec.payment_state =='paid':
                    rec.invisible_project = False
                else:
                    rec.invisible_project = True
            else:
                rec.invisible_project = False
    def _compute_origin_so(self):
        for move in self:
            if move.line_ids.sale_line_ids.order_id:
                move.order_id = move.line_ids.sale_line_ids.order_id[0]
            else:
                move.order_id = False

class AccountMoveLineInherited(models.Model):
    _inherit = 'account.move.line'

    language_pair = fields.Char(readonly=True)

    timeline = fields.Date()

    source = fields.Many2many('ir.attachment',related='sale_line_ids.source_attachment_ids', string='Source')
    source_lang =fields.Many2one('res.lang' ,related='sale_line_ids.source_language', string='Source' ,domain="['|',('active', '=', False),('active', '=', True)  ]")
    target_lang =fields.Many2one('res.lang' ,related='sale_line_ids.target_language', string='Target' , domain="['|',('active', '=', False),('active', '=', True)  ]")
    words = fields.Integer('Words',related='sale_line_ids.estimated_number_of_words')
    pages = fields.Integer('Pages',related='sale_line_ids.estimated_number_of_pages')
