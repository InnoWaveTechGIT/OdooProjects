import re
import importlib
try:
    importlib.import_module('marshmallow')
except ImportError:
    # Library not found, download and install it
    import pip
    pip.main(['install', 'marshmallow'])
from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class RegisterSchema(Schema):
    full_name=fields.String(required=True)
    password=fields.String(required=True)
    confirm_password =fields.String(required=True)
    email=fields.String(required=True )
    location = fields.String( )
    phone = fields.String( )

class LoginSchema(Schema):
    password=fields.String(required=True)
    email = fields.String(required=True )
    location = fields.String( )
    

class PasswordSchema(Schema):
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={
            'required': 'Password is required.',
            'length': 'Password must be at least 8 characters long.'
        }
    )
    #
    confirm_password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={
            'required': 'Password is required.',
            'length': 'Password must be at least 8 characters long.'
        }
    )

    @validates_schema
    def validate_password(self, data, **kwargs):
        password = data['password']
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase character.')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase character.')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one digit.')
        if not re.search(r'[^A-Za-z0-9]', password):
            raise ValidationError('Password must contain at least one special character.')