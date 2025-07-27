from odoo import http
import json
from odoo.http import request ,Response
from odoo.tools import config
import requests
from urllib.parse import urljoin, urlencode


class PromotioController(http.Controller):


    url = 'https://www.alnasaem.com' 

    @http.route('/api/promotion', auth='public', methods=['GET'], csrf=False, type='http')
    def get_promtion_data(self, **params):
        # Retrieve banner images from the "/api/banner" API
        try:
            language = request.httprequest.headers.get('Accept-Language', 'en_US').split(',')[0]
            promotion_id = request.env['promotion.nasaem'].sudo().with_context(lang=language).search([], limit=1)
            
            data = {
                    'id': promotion_id.id,
                    'title': promotion_id.title,
                    'text': promotion_id.text,
                    'image':promotion_id.image_url,
                    'is_visible' : promotion_id.is_visible ,
                }

            response = json.dumps({'data': data, 'is_success': True})
            return Response(response, status=200, content_type='application/json')
            
        except Exception as e:
                response = json.dumps({'data':[],'message':str(e) , 'is_success' :False}) 
                return Response(
                    response, status=500,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', 100)])
