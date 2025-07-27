from odoo import http
from odoo.http import request
from odoo.http import Response
import json

from . base_controller import BaseController
import functools
from odoo.exceptions import AccessError, ValidationError, UserError, MissingError


def validate_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        auth_header = request.httprequest.headers.get('Authorization')
        content_type = request.httprequest.headers.get('Content-Type', '')
        if content_type == 'application/json':
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'status': 404, 'message': 'Missing or invalid authorization header.'}

            token = auth_header.split(" ")[1]
            valid_api_key = request.env["res.users.apikeys"]._check_credentials(scope='api', key=token)
            # api_key_user = request.env["res.users"].sudo().browse(int(valid_api_key))
            if not valid_api_key:
                return {'status': 404, 'message': 'Invalid or expired token.'}

            return func(self, *args, **kwargs)
        else:
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response(
                    json.dumps({'status': 404, 'message': 'Missing or invalid authorization header.'}),
                    status=404,
                    content_type='application/json'
                )
            token = auth_header.split(" ")[1]
            valid_api_key = request.env["res.users.apikeys"]._check_credentials(scope='api', key=token)
            # api_key_user = request.env["res.users"].sudo().browse(int(valid_api_key))
            if not valid_api_key:
                return Response(
                    json.dumps({'status': 404, 'message': 'Invalid or expired token.'}),
                    status=404,
                    content_type='application/json'
                )
            return func(self, *args, **kwargs)
    return wrap

class ProductController(http.Controller):

    def get_user_id(self):
        auth_header = request.httprequest.headers.get('Authorization')
        token = auth_header.split(" ")[1]
        valid_api_key = request.env["res.users.apikeys"]._check_credentials(scope='api', key=token)
        api_key_user = request.env["res.users"].sudo().browse(int(valid_api_key))
        return api_key_user


