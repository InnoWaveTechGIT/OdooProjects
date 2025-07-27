from odoo.http import request
from odoo.http import Response
import json
import functools
import logging
from odoo.exceptions import AccessError, ValidationError, UserError, MissingError
_logger = logging.getLogger(__name__)

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

from odoo import http, _
import uuid
from datetime import datetime, timedelta

class PortalAPIKey(http.Controller):
    @http.route(['/api/portal/generate_api_key'], type='json', auth='user')
    def portal_generate_api_key(self, **kw):
        user = request.env.user
        # if not user.has_group('base.group_portal'):
        #     return {'error': 'Only portal users can access this endpoint'}
        portal_user = request.env['res.users'].sudo().search([('login', '=', 'doworks')])
        # key = str(uuid.uuid4())
        api_key_id = request.env['res.users.apikeys'].with_user(portal_user)._generate(None, 'doworks key', datetime.now() + timedelta(days=365)
        )
        return {
            'success': True,
            'api_key': api_key_id
        }