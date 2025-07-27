from odoo import models, api, fields
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class ContactInherit(models.Model):
    _inherit = 'res.partner'

    birth_date = fields.Date(string="Birth Date")


    @api.model
    def send_birthday_emails(self):
        today = datetime.now().date()
        three_days_later = today + timedelta(days=3)
        contacts = self.search([('birth_date', '=', three_days_later)])
        for contact in contacts:
            # Prepare email
            template = self.env.ref('Contacts_Customization.birthday_email_template')
            template.send_mail(contact.id, force_send=True)

