from odoo import models, fields, api



import importlib
import pip
from odoo.exceptions import AccessError, ValidationError, UserError

try:
    import validators
    importlib.import_module('validators')
except ImportError:
    # Library not found, download and install it
    pip.main(['install', 'validators'])


class FacebookPost(models.Model):
    _name = 'facebook.post'
    _description = 'Facebook Post'

    name = fields.Char(string='Post Name', required=True)
    link = fields.Char(string='Post Link')
    create_date = fields.Datetime(string='Create Date', default=fields.Datetime.now)
    image = fields.Binary(string='Image')

    @api.constrains('link')
    def is_valid_url(self):
        """Checks if the given URL is valid.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL is valid, False otherwise.
        """
        if self.link:
            val = validators.url(self.link)
            if not val:
                raise ValidationError("Please enter valid URL")


    def go_to_url(self):
        if self.link:
            return {
            'type': 'ir.actions.act_url',
            'url': self.link,
            'target': 'self',
        }
