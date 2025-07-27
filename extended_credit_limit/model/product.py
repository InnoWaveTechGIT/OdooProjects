from odoo import models, fields, api
from odoo.exceptions import UserError
class OrderTender(models.Model):
    _inherit = 'sale.order'

    credit_limit = fields.Boolean('Credit Limit Reached' ,compute='get_credit_limit' ,store = True )
    visible_credit_limit = fields.Boolean( compute = 'get_credit_limit')


    @api.depends('partner_credit_warning')
    def get_credit_limit(self):
        for rec in self:
            print('rec >>>>>>>> ' , rec)
            print('rec >>>>>>>> ' , rec.partner_credit_warning)
            if rec.partner_credit_warning != '':
                rec.credit_limit = True
            else:
                rec.credit_limit = False

            try:
                records = self.env['res.config.settings'].search([])
                record = records[0]
                value = record.account_use_credit_limit
                partner_value = self.partner_id.use_partner_credit_limit
                print('values >>>>>> ' ,partner_value , ' >> ' , value )
                if partner_value and value:
                    self.visible_credit_limit = value
                else:
                    self.visible_credit_limit= False
            except Exception as e:
                self.visible_credit_limit= False

