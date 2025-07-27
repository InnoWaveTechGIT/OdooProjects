from odoo import models, api,fields

class SaleOrder(models.Model):
    _inherit = 'account.move.line'


    group = fields.Char(string='Group Name' , compute='get_group' , store=True)
    balance_percentage1 = fields.Float(compute='compute_balance_percentage' , string='Percentage')
    balance_percentage = fields.Float(compute='compute_balance_percentage' ,store=True, string='Percentage')

    @api.depends('balance', 'date')
    def compute_balance_percentage(self):
        '''

        :return: the percintage depends on the total balance we have in the expense account move line model
        '''

        for record in self:
            total_balance_for_month =0
            # Calculate the sum of balances for the month of the record
            account_move = self.env['account.move.line'].search([])
            account_saved = []
            for i in account_move:
                if i.date.year == record.date.year and i.date.month == record.date.month and i.account_id.account_type in ['expense', 'expense_depreciation']  :
                    account_saved.append(i)
                    total_balance_for_month += i.balance

            # Calculate the percentage for the record based on the total balance for the month
            if total_balance_for_month:

                record.balance_percentage = (record.balance / total_balance_for_month) * 100
            else:
                record.balance_percentage = 0.0

            record.balance_percentage1 = 0.0


    @api.depends('account_id')
    def get_group(self):
        '''

        :return: the group name for the invoice
        '''
        for rec in self:
            rec.group = rec.account_id.group_id.name
