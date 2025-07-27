from odoo import http
# from werkzeug.wrappers import Response
import logging
from datetime import datetime
import xmlrpc.client as xmlrpclib
import json
from odoo import models, fields, api
import math
import os
import requests
from odoo.http import request ,Response
# from odoo.http import JsonRequest
import jwt
import re
import time
import base64
import werkzeug.wrappers
from requests_toolbelt.multipart import decoder

from os import path
from pathlib import Path 
import pathlib


#version 1.0.0
def verfiy_token (self,token,user_id):
    
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
    uid = common.authenticate(self.db, self.username, self.password, {})
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
    tokens=models.execute_kw(self.db,uid, self.password, 'user.token', 'search_count', [['&',['user_id', '=', user_id],['token','=',str(token)]]] )
    if tokens != 1:
        return False
    else :
        return True


def verify_active(self,user_id):
    user = request.env['res.users'].sudo().search([('id' , '=' ,user_id )])
    if user.is_active:
        return True
    else:
        return False