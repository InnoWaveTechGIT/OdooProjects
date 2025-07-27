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
import werkzeug.wrappers
import socket
from os import path
from pathlib import Path 
import pathlib
import collections
import base64

class Subjects(http.Controller):
    @http.route('/school/subjects',  auth="api_key",csrf=False, website=True, methods=['GET'])
    def get_student_subjectss(self,**kw):
        user_id=request.env.uid
        result = []
        user_id = request.env['res.users'].sudo().search([('id' , '=' , user_id)])
        if user_id.user_type == 'Student':
            
            response = json.dumps({'data': [] , 'message' : 'you don\'t have access' , 'code' : 403})
            return Response(
                response, status=403,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        if user_id.user_type == 'Teacher':
            class_id = request.env['subject.school.app'].sudo().search([('teacher_id' , '=' , user_id.id)])
            for line in class_id:
                result.append({
                    'id' : line.id,
                    'name' : line.name
                })
           
            response = json.dumps({'data': result , 'message' : 'All Data' , 'code' : 200})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        else:
            response = json.dumps({'data': [] , 'message' : 'No Data' , 'code' : 404})
            return Response(
                response, status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )