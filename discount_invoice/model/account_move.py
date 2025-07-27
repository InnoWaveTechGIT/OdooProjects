from odoo import api, fields, models, tools, _
from num2words import num2words
from babel.numbers import get_currency_name
from itertools import groupby
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Command


class LoyaltyUsersGiftYokohama(models.Model):
    _inherit = 'account.move'
    invisible_discount = fields.Boolean()
    discount_amount = fields.Char()
    positive_product_prices = fields.Float(
        string='Positive Product Prices',
        compute='_compute_positive_product_prices',
        store=True,
        readonly=True,
        help='Sum of positive product prices in the invoice',
    )

    grand_total_words = fields.Char('Grand Total ', compute='_get_Grand_total')

    @api.depends('partner_id')
    def _get_Grand_total(self):
        for order in self:
            total_price = float(order.partner_id.total_due)
            formatted_total_due = "{:.4f}".format(total_price)
            integer_part, fractional_part = str(formatted_total_due).split('.')

            # Convert the integer part to words
            integer_words = num2words(int(integer_part)).title()
            if " And " in integer_words:
                integer_words = integer_words.replace(" And ", " ")

            # Convert the fractional part to words
            if fractional_part:
                intfractional_part =  int(fractional_part)
                last_two_digits = intfractional_part % 100
                if last_two_digits >= 50:
                    intfractional_part -= last_two_digits
                    intfractional_part += 50
                else:
                    intfractional_part -= last_two_digits
                fractional_words = num2words(intfractional_part, ordinal=False).title()
            else:
                fractional_words = ""

            # Define the currency name and format
            currency_name = "dirhams"
            fractional_name = "fils"

            # Create the final formatted string
            if integer_part != '0' and fractional_part != '0':
                result = f"{integer_words} {currency_name} and {fractional_words} {fractional_name}"
            elif integer_part != '0':
                result = f"{integer_words} {currency_name}"
            elif fractional_part != '0':
                result = f"{fractional_words} {fractional_name}"
            else:
                result = "Zero dirhams"
            order.grand_total_words = result


    @api.depends('invoice_line_ids.price_unit')
    def _compute_positive_product_prices(self):
        for invoice in self:
            positive_prices = sum(line.price_subtotal for line in invoice.invoice_line_ids if line.price_subtotal > 0)
            invoice.positive_product_prices = positive_prices

    def open_add_discount_wizard(self):
        self.ensure_one()
        print('Asd asdas ds>>> ' , self.id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Discount',
            'res_model': 'discount.invoice.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_invoice_id': self.id,
            },
        }

class AddDiscountWizard(models.TransientModel):
    _name = 'discount.invoice.wizard'
    _description = 'Add discount Wizard'

    invoice_id = fields.Many2one('account.move', string='Invoice')
    discount = fields.Integer(string='Discount')


    def confirm(self):

        # Close the wizard
        self.invoice_id.invisible_discount = True
        self.invoice_id.discount_amount = str(self.discount) + '%'
        discount = int(self.invoice_id.amount_residual )* self.discount / 100
        discount = (-1) * discount
        invoice_line_id = self.env['account.move.line'].create({
            'move_id' : self.invoice_id.id ,
            'product_id' : 9,
            'name' : 'Discount' ,
            'quantity' :  1,
            'price_unit' : discount
        })
        return {'type': 'ir.actions.act_window_close'}

    def cancel(self):
        # Close the wizard without performing any operations
        return {'type': 'ir.actions.act_window_close'}

    @api.constrains('discount')
    def _check_discount_range(self):
        for record in self:
            if record.discount < 0 or record.discount > 100:
                raise ValidationError("Discount must be between 0 and 100.")
