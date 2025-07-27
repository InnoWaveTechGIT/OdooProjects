# -*- coding: utf-8 -*-
# from odoo import http


# class LeadersLanguageFactory(http.Controller):
#     @http.route('/leaders_language_factory/leaders_language_factory', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/leaders_language_factory/leaders_language_factory/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('leaders_language_factory.listing', {
#             'root': '/leaders_language_factory/leaders_language_factory',
#             'objects': http.request.env['leaders_language_factory.leaders_language_factory'].search([]),
#         })

#     @http.route('/leaders_language_factory/leaders_language_factory/objects/<model("leaders_language_factory.leaders_language_factory"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('leaders_language_factory.object', {
#             'object': obj
#         })

from odoo import http
import json

class LanguageController(http.Controller):

    @http.route('/get_languages', auth='public', type='http', website=True)
    def get_languages(self):
        Lang = http.request.env['res.lang']
        languages = Lang.search(['|', ('active', '=', False), ('active', '=', True)])

        return json.dumps([(lang.id, lang.name) for lang in languages])
