from odoo import models, api,fields

class SaleOrder(models.Model):
    _inherit = 'account.move.line'


    group = fields.Char(string='Group Name' , compute='get_group' , store=True)
    balance_percentage = fields.Float(compute='compute_balance_percentage' ,store=True, string='Percentage')

    @api.depends('balance', 'date')
    def compute_balance_percentage(self):
        '''

        :return: the percintage depends on the total balance we have in the expense account move line model
        '''
        for record in self:
            total_balance_for_month =0

            print('record.date >>>>>>>>>> ' , record.date)
            # Calculate the sum of balances for the month of the record
            account_move = self.env['account.move.line'].search([])
            account_saved = []
            for i in account_move:
                if i.date.year == record.date.year and i.date.month == record.date.month:
                    account_saved.append(i)
                    total_balance_for_month += i.price_total

            # Calculate the percentage for the record based on the total balance for the month
            if total_balance_for_month:
                record.balance_percentage = (record.price_total / total_balance_for_month) * 100
            else:
                record.balance_percentage = 0.0


    @api.depends('account_id')
    def get_group(self):
        '''

        :return: the group name for the invoice
        '''
        for rec in self:
            rec.group = rec.account_id.group_id.name
